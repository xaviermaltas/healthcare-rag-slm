"""
Clinical Summary Generation Endpoint
Genera resums clínics previs a consulta amb arquitectura RAG semàntica
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

from src.main.core.prompts.clinical_summary_template import ClinicalSummaryPrompt
from src.main.infrastructure.embeddings.bge_m3 import BGEM3Embeddings
from src.main.infrastructure.llm.ollama_client import OllamaClient
from src.main.api.dependencies import get_ollama_client, get_embeddings_model, get_medical_coding_service
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/generate", tags=["generation"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ClinicalSummaryRequest(BaseModel):
    """Request model for clinical summary generation"""
    
    patient_context: str = Field(
        ...,
        description="Patient context and medical history",
        min_length=10,
        max_length=2000,
        example="Pacient home de 70 anys amb antecedents de diabetis tipus 2, hipertensió arterial i dislipèmia"
    )
    
    current_symptoms: List[str] = Field(
        ...,
        description="Current symptoms or complaints",
        min_items=1,
        max_items=10,
        example=["Dolor toràcic intermitent", "Dispnea d'esforç", "Fatiga"]
    )
    
    medications: List[str] = Field(
        default=[],
        description="Current medications",
        max_items=20,
        example=["Metformina 850mg", "Enalapril 10mg", "Atorvastatina 20mg"]
    )
    
    specialty: Optional[str] = Field(
        default=None,
        description="Target specialty for consultation",
        example="cardiologia"
    )
    
    language: str = Field(
        default="ca",
        description="Response language",
        regex="^(ca|es|en)$"
    )


class ClinicalSummaryResponse(BaseModel):
    """Response model for clinical summary"""
    
    summary: str = Field(description="Generated clinical summary")
    
    relevant_conditions: List[Dict[str, Any]] = Field(
        description="Relevant medical conditions identified",
        example=[{
            "condition": "Diabetis mellitus tipus 2",
            "snomed_code": "44054006",
            "icd10_code": "E11.9",
            "relevance": "high"
        }]
    )
    
    coded_medications: List[Dict[str, Any]] = Field(
        description="Medications with ATC codes",
        example=[{
            "medication": "Metformina 850mg",
            "atc_code": "A10BA02",
            "therapeutic_class": "Antidiabètics"
        }]
    )
    
    sources: List[Dict[str, Any]] = Field(
        description="Sources used for summary generation"
    )
    
    metadata: Dict[str, Any] = Field(
        description="Generation metadata"
    )


# ============================================================================
# ENDPOINT
# ============================================================================

@router.post("/clinical-summary", response_model=ClinicalSummaryResponse)
async def generate_clinical_summary(
    request: ClinicalSummaryRequest,
    ollama_client: OllamaClient = Depends(get_ollama_client),
    embeddings_client: BGEM3Embeddings = Depends(get_embeddings_model),
    coding_service = Depends(get_medical_coding_service)
) -> ClinicalSummaryResponse:
    """
    🆕 NOVA ARQUITECTURA: Genera resum clínic amb retrieval semàntic
    
    Aquest endpoint implementa l'arquitectura RAG correcta:
    1. Semantic retrieval de protocols clínics
    2. Semantic coding d'antecedents i medicacions
    3. Generació LLM amb context enriquit
    """
    
    try:
        logger.info(f"🏥 Generating clinical summary for specialty: {request.specialty}")
        
        # ====================================================================
        # STEP 1: Prepare search query for RAG retrieval
        # ====================================================================
        
        # Combine patient context and symptoms for search
        search_query = f"{request.patient_context}. Símptomes actuals: {', '.join(request.current_symptoms)}"
        if request.specialty:
            search_query += f". Especialitat: {request.specialty}"
        
        logger.info(f"Search query: {search_query[:100]}...")
        
        # ====================================================================
        # STEP 2: RAG Retrieval - Get relevant clinical protocols
        # ====================================================================
        
        # Generate embeddings for search
        query_embedding = await embeddings_client.embed_query(search_query)
        
        # Search Qdrant for relevant documents
        qdrant_client = QdrantClient(host="localhost", port=6333)
        
        # Build specialty filter if specified
        search_filter = None
        if request.specialty:
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="specialty",
                        match=MatchValue(value=request.specialty.lower())
                    )
                ]
            )
        
        search_results = qdrant_client.search(
            collection_name="healthcare_rag",
            query_vector=query_embedding,
            query_filter=search_filter,
            limit=5,
            with_payload=True
        )
        
        logger.info(f"Found {len(search_results)} relevant sources")
        
        # Extract sources for response
        sources = []
        context_chunks = []
        
        for result in search_results:
            payload = result.payload
            sources.append({
                "title": payload.get("title", "Unknown"),
                "specialty": payload.get("specialty", "General"),
                "score": float(result.score),
                "chunk": payload.get("content", "")[:200] + "..."
            })
            context_chunks.append(payload.get("content", ""))
        
        # ====================================================================
        # STEP 3: SEMANTIC CODING - Process medical conditions and medications
        # ====================================================================
        
        relevant_conditions = []
        coded_medications = []
        
        if coding_service:
            logger.info("🔍 SEMANTIC CODING: Processing medical conditions...")
            
            # Extract and code medical conditions from patient context
            # Simple extraction - in production would use NER
            conditions_to_code = [
                "diabetis tipus 2", "hipertensió arterial", "dislipèmia"
            ]
            
            for condition in conditions_to_code:
                if condition.lower() in request.patient_context.lower():
                    # Try SEMANTIC SNOMED coding
                    snomed_result = await coding_service.get_snomed_code_semantic(condition)
                    icd10_result = await coding_service.get_icd10_code_semantic(condition)
                    
                    relevant_conditions.append({
                        "condition": condition.title(),
                        "snomed_code": snomed_result.code if snomed_result else None,
                        "icd10_code": icd10_result.code if icd10_result else None,
                        "relevance": "high",
                        "source": snomed_result.source if snomed_result else "not_found"
                    })
            
            # Code medications
            logger.info("💊 SEMANTIC CODING: Processing medications...")
            for medication in request.medications:
                atc_result = await coding_service.get_atc_code_semantic(medication)
                
                coded_medications.append({
                    "medication": medication,
                    "atc_code": atc_result.code if atc_result else None,
                    "therapeutic_class": _get_therapeutic_class(atc_result.code) if atc_result else "Unknown",
                    "source": atc_result.source if atc_result else "not_found"
                })
        
        # ====================================================================
        # STEP 4: LLM Generation with enriched context
        # ====================================================================
        
        # Build enriched context
        context = "\n\n".join(context_chunks[:3])  # Top 3 most relevant chunks
        
        # Generate clinical summary prompt
        prompt = ClinicalSummaryPrompt.build_prompt(
            patient_context=request.patient_context,
            current_symptoms=request.current_symptoms,
            medications=request.medications,
            relevant_conditions=relevant_conditions,
            context=context,
            specialty=request.specialty,
            language=request.language
        )
        
        logger.info("🤖 Generating clinical summary with LLM...")
        
        # Generate with Ollama
        generated_summary = await ollama_client.generate(
            prompt=prompt,
            max_tokens=1000,
            temperature=0.3
        )
        
        # ====================================================================
        # STEP 5: Build response
        # ====================================================================
        
        response = ClinicalSummaryResponse(
            summary=generated_summary,
            relevant_conditions=relevant_conditions,
            coded_medications=coded_medications,
            sources=sources,
            metadata={
                "generation_timestamp": datetime.now().isoformat(),
                "specialty": request.specialty,
                "language": request.language,
                "sources_count": len(sources),
                "conditions_coded": len(relevant_conditions),
                "medications_coded": len(coded_medications),
                "architecture": "semantic_rag"
            }
        )
        
        logger.info(f"✅ Clinical summary generated successfully")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error generating clinical summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate clinical summary: {str(e)}"
        )


def _get_therapeutic_class(atc_code: Optional[str]) -> str:
    """Get therapeutic class from ATC code"""
    if not atc_code:
        return "Unknown"
    
    # ATC first letter indicates therapeutic class
    atc_classes = {
        'A': 'Aparell digestiu i metabolisme',
        'B': 'Sang i òrgans hematopoètics',
        'C': 'Sistema cardiovascular',
        'D': 'Dermatològics',
        'G': 'Sistema genitourinari i hormones sexuals',
        'H': 'Preparats hormonals sistèmics',
        'J': 'Antiinfecciosos per a ús sistèmic',
        'L': 'Agents antineoplàstics i immunomoduladors',
        'M': 'Sistema musculoesquelètic',
        'N': 'Sistema nerviós',
        'P': 'Productes antiparasitaris',
        'R': 'Sistema respiratori',
        'S': 'Òrgans dels sentits',
        'V': 'Varis'
    }
    
    return atc_classes.get(atc_code[0], "Unknown") if atc_code else "Unknown"
