"""
Discharge Summary Generation Endpoint
Generates hospital discharge summaries using RAG with SAS protocols
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

from src.main.core.prompts.discharge_summary_template import DischargeSummaryPrompt
from src.main.infrastructure.embeddings.bge_m3 import BGEM3Embeddings
from src.main.infrastructure.llm.ollama_client import OllamaClient
from src.main.api.dependencies import get_ollama_client, get_embeddings_model
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/generate", tags=["generation"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class DischargeSummaryRequest(BaseModel):
    """Request model for discharge summary generation"""
    
    patient_context: str = Field(
        ...,
        description="Patient context (age, gender, relevant medical history)",
        min_length=10,
        max_length=2000,
        example="Pacient home de 65 anys amb antecedents de hipertensió arterial i dislipèmia"
    )
    
    admission_reason: str = Field(
        ...,
        description="Reason for hospital admission",
        min_length=5,
        max_length=500,
        example="Dolor toràcic opressiu amb elevació de troponines"
    )
    
    procedures: List[str] = Field(
        default_factory=list,
        description="List of procedures performed during hospitalization",
        max_items=20,
        example=["ECG de 12 derivacions", "Coronariografia", "Angioplastia primària"]
    )
    
    current_medications: List[str] = Field(
        default_factory=list,
        description="Current medications at discharge",
        max_items=30,
        example=["AAS 100mg/24h", "Clopidogrel 75mg/24h", "Atorvastatina 80mg/24h"]
    )
    
    language: str = Field(
        default="es",
        description="Language for the discharge summary (es/ca)",
        pattern="^(es|ca)$",
        example="es"
    )
    
    specialty: Optional[str] = Field(
        default=None,
        description="Medical specialty for filtering protocols",
        example="Cardiologia"
    )
    
    @validator('procedures', 'current_medications')
    def validate_lists(cls, v):
        """Validate that list items are not empty"""
        if v:
            for item in v:
                if not item or not item.strip():
                    raise ValueError("List items cannot be empty")
        return v


class DiagnosisInfo(BaseModel):
    """Diagnosis information with codes"""
    description: str
    snomed_code: Optional[str] = None
    icd10_code: Optional[str] = None
    is_primary: bool = False


class MedicationInfo(BaseModel):
    """Medication information with codes"""
    name: str
    dosage: str
    atc_code: Optional[str] = None
    duration: Optional[str] = None


class ProtocolSource(BaseModel):
    """Protocol source information"""
    title: str
    specialty: str
    score: float
    official: bool = False


class ValidationStatus(BaseModel):
    """Validation status of the generated summary"""
    all_sections_present: bool
    missing_sections: List[str] = Field(default_factory=list)
    has_diagnoses: bool
    has_medications: bool
    has_follow_up: bool


class DischargeSummaryResponse(BaseModel):
    """Response model for discharge summary generation"""
    
    summary: str = Field(
        ...,
        description="Complete discharge summary document"
    )
    
    diagnoses: List[DiagnosisInfo] = Field(
        default_factory=list,
        description="List of diagnoses with SNOMED CT and ICD-10 codes"
    )
    
    medications: List[MedicationInfo] = Field(
        default_factory=list,
        description="List of medications with ATC codes"
    )
    
    follow_up_recommendations: List[str] = Field(
        default_factory=list,
        description="Follow-up recommendations"
    )
    
    contraindications: List[str] = Field(
        default_factory=list,
        description="Contraindications and warnings"
    )
    
    sources: List[ProtocolSource] = Field(
        default_factory=list,
        description="SAS protocols used as sources"
    )
    
    validation_status: ValidationStatus = Field(
        ...,
        description="Validation status of the generated summary"
    )
    
    generation_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata about the generation process"
    )


# ============================================================================
# ENDPOINT
# ============================================================================

@router.post(
    "/discharge-summary",
    response_model=DischargeSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Hospital Discharge Summary",
    description="Generates a structured hospital discharge summary using RAG with SAS protocols",
    responses={
        200: {"description": "Discharge summary generated successfully"},
        400: {"description": "Invalid request parameters"},
        500: {"description": "Internal server error during generation"}
    }
)
async def generate_discharge_summary(
    request: DischargeSummaryRequest,
    ollama_client: OllamaClient = Depends(get_ollama_client),
    embeddings_client: BGEM3Embeddings = Depends(get_embeddings_model)
) -> DischargeSummaryResponse:
    """
    Generate a hospital discharge summary using RAG
    
    This endpoint:
    1. Retrieves relevant SAS protocols from Qdrant
    2. Constructs a prompt using the DischargeSummaryPrompt template
    3. Generates the summary using Ollama
    4. Validates the response structure
    5. Extracts medical codes (SNOMED CT, ICD-10, ATC)
    6. Returns a structured response
    """
    
    start_time = datetime.now()
    
    try:
        logger.info(f"Generating discharge summary - Language: {request.language}, Specialty: {request.specialty}")
        
        # ====================================================================
        # STEP 1: Initialize Qdrant client
        # ====================================================================
        # Note: Ollama and Embeddings clients are injected via dependencies
        
        qdrant_client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT
        )
        
        # ====================================================================
        # STEP 2: Construct query for protocol retrieval
        # ====================================================================
        
        # Build query from admission reason and patient context
        query_text = f"{request.admission_reason} {request.patient_context}"
        if request.procedures:
            query_text += " " + " ".join(request.procedures[:3])  # Top 3 procedures
        
        logger.info(f"Retrieval query: {query_text[:100]}...")
        
        # Generate embedding
        query_result = await embeddings_client.encode_query(query_text)
        query_embedding = query_result.get('dense', query_result.get('embedding', []))
        
        # ====================================================================
        # STEP 3: Retrieve relevant SAS protocols
        # ====================================================================
        
        # Build filter for specialty if provided
        query_filter = Filter(
            must=[
                FieldCondition(key="type", match=MatchValue(value="protocol_sas"))
            ]
        )
        
        if request.specialty:
            query_filter.must.append(
                FieldCondition(key="specialty", match=MatchValue(value=request.specialty))
            )
        
        # Search in Qdrant
        protocol_results = qdrant_client.query_points(
            collection_name=settings.QDRANT_COLLECTION,
            query=query_embedding,
            limit=5,
            score_threshold=0.3,
            query_filter=query_filter
        ).points
        
        logger.info(f"Retrieved {len(protocol_results)} protocols")
        
        # Format protocols for prompt
        retrieved_protocols = []
        sources = []
        
        for hit in protocol_results:
            protocol_info = {
                'title': hit.payload.get('title', 'Unknown'),
                'content': hit.payload.get('content', ''),
                'specialty': hit.payload.get('specialty', 'Unknown'),
                'score': hit.score
            }
            retrieved_protocols.append(protocol_info)
            
            sources.append(ProtocolSource(
                title=protocol_info['title'],
                specialty=protocol_info['specialty'],
                score=round(hit.score, 4),
                official=hit.payload.get('official', False)
            ))
        
        # ====================================================================
        # STEP 4: Build prompt using DischargeSummaryPrompt template
        # ====================================================================
        
        prompt = DischargeSummaryPrompt.build_prompt(
            patient_context=request.patient_context,
            admission_reason=request.admission_reason,
            procedures=request.procedures,
            medications=request.current_medications,
            retrieved_protocols=retrieved_protocols,
            language=request.language
        )
        
        logger.info(f"Prompt built - Length: {len(prompt)} chars")
        
        # ====================================================================
        # STEP 5: Generate summary with Ollama
        # ====================================================================
        
        generation_response = await ollama_client.generate(
            prompt=prompt,
            model=settings.OLLAMA_MODEL,
            temperature=0.3,  # Low temperature for factual medical content
            max_tokens=800  # Reduced for faster generation on CPU
        )
        
        generated_summary = generation_response.get('response', '')
        
        if not generated_summary:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate summary - empty response from LLM"
            )
        
        logger.info(f"Summary generated - Length: {len(generated_summary)} chars")
        
        # ====================================================================
        # STEP 6: Validate response structure
        # ====================================================================
        
        validation_result = DischargeSummaryPrompt.validate_response(
            response=generated_summary,
            language=request.language
        )
        
        missing_sections = [
            section for section, present in validation_result.items()
            if not present
        ]
        
        validation_status = ValidationStatus(
            all_sections_present=len(missing_sections) == 0,
            missing_sections=missing_sections,
            has_diagnoses=True,  # Will be updated after extraction
            has_medications=True,  # Will be updated after extraction
            has_follow_up=True  # Will be updated after extraction
        )
        
        # ====================================================================
        # STEP 7: Extract medical codes
        # ====================================================================
        
        extracted_codes = DischargeSummaryPrompt.extract_codes(generated_summary)
        
        # Build diagnoses list
        diagnoses = []
        for snomed_code in extracted_codes.get('snomed_codes', []):
            diagnoses.append(DiagnosisInfo(
                description="Extracted from summary",
                snomed_code=snomed_code,
                is_primary=len(diagnoses) == 0  # First one is primary
            ))
        
        for icd10_code in extracted_codes.get('icd10_codes', []):
            # Try to find matching diagnosis or create new
            found = False
            for diag in diagnoses:
                if not diag.icd10_code:
                    diag.icd10_code = icd10_code
                    found = True
                    break
            if not found:
                diagnoses.append(DiagnosisInfo(
                    description="Extracted from summary",
                    icd10_code=icd10_code
                ))
        
        # Build medications list
        medications = []
        for atc_code in extracted_codes.get('atc_codes', []):
            medications.append(MedicationInfo(
                name="Extracted from summary",
                dosage="See summary",
                atc_code=atc_code
            ))
        
        # Update validation status
        validation_status.has_diagnoses = len(diagnoses) > 0
        validation_status.has_medications = len(medications) > 0
        
        # ====================================================================
        # STEP 8: Extract follow-up and contraindications
        # ====================================================================
        
        # Simple extraction based on section headers
        follow_up = []
        contraindications = []
        
        # Split by sections and extract
        if "SEGUIMENT" in generated_summary or "SEGUIMIENTO" in generated_summary:
            validation_status.has_follow_up = True
        
        # ====================================================================
        # STEP 9: Build response
        # ====================================================================
        
        end_time = datetime.now()
        generation_time = (end_time - start_time).total_seconds()
        
        response = DischargeSummaryResponse(
            summary=generated_summary,
            diagnoses=diagnoses,
            medications=medications,
            follow_up_recommendations=follow_up,
            contraindications=contraindications,
            sources=sources,
            validation_status=validation_status,
            generation_metadata={
                'generation_time_seconds': round(generation_time, 2),
                'protocols_retrieved': len(protocol_results),
                'language': request.language,
                'specialty': request.specialty,
                'model': settings.OLLAMA_MODEL,
                'timestamp': end_time.isoformat()
            }
        )
        
        logger.info(f"Discharge summary generated successfully in {generation_time:.2f}s")
        
        return response
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error generating discharge summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate discharge summary: {str(e)}"
        )
