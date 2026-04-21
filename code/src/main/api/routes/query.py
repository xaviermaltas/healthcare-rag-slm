"""
Query endpoints for Healthcare RAG system
Handles medical queries using retrieval-augmented generation
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import asyncio
import logging
from datetime import datetime

from src.main.api.dependencies import get_ollama_client, get_qdrant_client, get_embeddings_model, get_ontology_manager
from src.main.infrastructure.llm.ollama_client import OllamaClient
from src.main.infrastructure.vector_db.qdrant_client import HealthcareQdrantClient
from src.main.infrastructure.embeddings.bge_m3 import BGEM3Embeddings
from src.main.infrastructure.ontologies.ontology_manager import OntologyManager
from src.main.core.retrieval.query_processing.medical_ner import MedicalNER
from src.main.core.retrieval.query_processing.query_expander import QueryExpander

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize medical NER
medical_ner = MedicalNER()


class QueryRequest(BaseModel):
    """Request model for RAG queries"""
    query: str = Field(..., description="Medical query text", min_length=1, max_length=2000)
    model: Optional[str] = Field(default="mistral", description="Ollama model to use")
    max_tokens: Optional[int] = Field(default=1000, ge=1, le=4000, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0, description="Generation temperature")
    top_k: Optional[int] = Field(default=10, ge=1, le=50, description="Number of documents to retrieve")
    score_threshold: Optional[float] = Field(default=0.0, ge=0.0, le=1.0, description="Minimum similarity score")
    language: Optional[str] = Field(default="es", description="Response language (es/ca/en)")
    include_sources: Optional[bool] = Field(default=True, description="Include source documents in response")
    use_query_expansion: Optional[bool] = Field(default=True, description="Use ontology-based query expansion")
    include_ontology_codes: Optional[bool] = Field(default=True, description="Include ontology codes in expansion")


class QueryResponse(BaseModel):
    """Response model for RAG queries"""
    response: str = Field(..., description="Generated response")
    query: str = Field(..., description="Original query")
    expanded_query: Optional[str] = Field(default=None, description="Query expanded with ontology terms")
    model_used: str = Field(..., description="Model used for generation")
    sources: List[Dict[str, Any]] = Field(default=[], description="Retrieved source documents")
    medical_entities: Dict[str, List[str]] = Field(default={}, description="Extracted medical entities")
    query_expansion_stats: Optional[Dict[str, Any]] = Field(default=None, description="Query expansion statistics")
    retrieval_stats: Dict[str, Any] = Field(default={}, description="Retrieval statistics")
    generation_stats: Dict[str, Any] = Field(default={}, description="Generation statistics")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


@router.post("/", response_model=QueryResponse)
async def query_rag(
    request: QueryRequest,
    background_tasks: BackgroundTasks,
    ollama_client: OllamaClient = Depends(get_ollama_client),
    qdrant_client: HealthcareQdrantClient = Depends(get_qdrant_client),
    embeddings_model: BGEM3Embeddings = Depends(get_embeddings_model),
    ontology_manager: Optional[OntologyManager] = Depends(get_ontology_manager)
):
    """Main RAG query endpoint"""
    
    start_time = asyncio.get_event_loop().time()
    
    try:
        # Step 1: Extract medical entities from query
        logger.info(f"Processing query: {request.query[:100]}...")
        entities = medical_ner.extract_entities(request.query)
        entity_summary = medical_ner.get_entity_summary(entities)
        
        # Step 2: Query Expansion (if enabled and ontology manager available)
        expanded_query_text = request.query
        expansion_stats = None
        
        if request.use_query_expansion and ontology_manager:
            try:
                logger.info("Expanding query with ontologies...")
                query_expander = QueryExpander(
                    ontology_manager=ontology_manager,
                    medical_ner=medical_ner,
                    config={
                        'include_codes': request.include_ontology_codes,
                        'max_synonyms_per_entity': 5,
                        'max_concepts_per_entity': 3
                    }
                )
                
                expanded_query = await query_expander.expand_query(request.query)
                expanded_query_text = expanded_query.get_search_text(include_codes=request.include_ontology_codes)
                
                # Get expansion summary
                expansion_summary = query_expander.get_expansion_summary(expanded_query)
                expansion_stats = {
                    'total_terms': expansion_summary['total_terms'],
                    'entities_detected': expansion_summary['entities_detected'],
                    'terms_by_source': expansion_summary['terms_by_source'],
                    'ontologies_used': expansion_summary['ontologies_used']
                }
                
                logger.info(f"Query expanded: {expansion_summary['total_terms']} terms from {expansion_summary['entities_detected']} entities")
                
            except Exception as e:
                logger.warning(f"Query expansion failed, using original query: {e}")
                expanded_query_text = request.query
        
        # Step 3: Generate query embeddings and retrieve documents
        query_embedding = await embeddings_model.encode_query(expanded_query_text)
        retrieved_docs = await qdrant_client.search_similar(
            query_vector=query_embedding['dense'],
            limit=request.top_k,
            score_threshold=request.score_threshold
        )
        
        if not retrieved_docs:
            logger.warning("No relevant documents found")
            retrieved_docs = []
        
        retrieval_time = asyncio.get_event_loop().time() - start_time
        
        # Step 4: Generate response using retrieved context
        logger.debug("Generating response...")
        generation_start = asyncio.get_event_loop().time()
        
        # Build system prompt based on language
        system_prompts = {
            "es": """Eres un asistente médico especializado que ayuda a profesionales sanitarios de la Junta de Andalucía.

Instrucciones:
- Responde basándote únicamente en la información médica proporcionada en el contexto
- Si no tienes información suficiente, indícalo claramente
- Usa terminología médica precisa pero comprensible
- Incluye referencias a las fuentes cuando sea relevante
- Responde en español
- No proporciones diagnósticos definitivos, solo información orientativa
- Mantén un tono profesional y objetivo""",
            
            "ca": """Ets un assistent mèdic especialitzat que ajuda a professionals sanitaris de la Junta d'Andalusia.

Instruccions:
- Respon basant-te únicament en la informació mèdica proporcionada en el context
- Si no tens informació suficient, indica-ho clarament
- Usa terminologia mèdica precisa però comprensible
- Inclou referències a les fonts quan sigui rellevant
- Respon en català
- No proporcionis diagnòstics definitius, només informació orientativa
- Mantén un to professional i objectiu""",
            
            "en": """You are a specialized medical assistant helping healthcare professionals from Junta de Andalucía.

Instructions:
- Respond based only on the medical information provided in the context
- If you don't have sufficient information, clearly indicate this
- Use precise but understandable medical terminology
- Include references to sources when relevant
- Respond in English
- Do not provide definitive diagnoses, only guidance information
- Maintain a professional and objective tone"""
        }
        
        system_prompt = system_prompts.get(request.language, system_prompts["es"])
        
        generation_result = await ollama_client.generate_medical_response(
            query=request.query,
            context_documents=retrieved_docs,
            system_prompt=system_prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        generation_time = asyncio.get_event_loop().time() - generation_start
        
        if "error" in generation_result:
            raise HTTPException(status_code=500, detail=f"Generation failed: {generation_result['error']}")
        
        # Step 5: Prepare response
        total_time = asyncio.get_event_loop().time() - start_time
        
        # Format sources for response
        sources = []
        if request.include_sources:
            for doc in retrieved_docs:
                source_info = {
                    "content": doc.get("content", "")[:500] + "..." if len(doc.get("content", "")) > 500 else doc.get("content", ""),
                    "source": doc.get("source", ""),
                    "score": doc.get("score", 0.0),
                    "metadata": doc.get("metadata", {})
                }
                sources.append(source_info)
        
        response = QueryResponse(
            response=generation_result.get("response", ""),
            query=request.query,
            expanded_query=expanded_query_text if request.use_query_expansion else None,
            model_used=request.model,
            sources=sources,
            medical_entities=entity_summary,
            query_expansion_stats=expansion_stats,
            retrieval_stats={
                "documents_found": len(retrieved_docs),
                "retrieval_time": retrieval_time,
                "top_score": max([doc.get("score", 0.0) for doc in retrieved_docs]) if retrieved_docs else 0.0,
                "avg_score": sum([doc.get("score", 0.0) for doc in retrieved_docs]) / len(retrieved_docs) if retrieved_docs else 0.0
            },
            generation_stats={
                "generation_time": generation_time,
                "total_time": total_time,
                "total_duration": generation_result.get("total_duration", 0),
                "eval_count": generation_result.get("eval_count", 0),
                "context_length": generation_result.get("context_length", 0)
            }
        )
        
        # Log query for analytics (in background)
        background_tasks.add_task(
            log_query_analytics,
            request.query,
            len(retrieved_docs),
            entity_summary,
            total_time
        )
        
        logger.info(f"Query processed successfully in {total_time:.2f}s")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error processing query: {str(e)}")


@router.post("/entities")
async def extract_medical_entities(query: str):
    """Extract medical entities from query text"""
    try:
        entities = medical_ner.extract_entities(query)
        entity_summary = medical_ner.get_entity_summary(entities)
        expanded_terms = medical_ner.expand_medical_terms(entities)
        
        return {
            "query": query,
            "entities": [
                {
                    "text": entity.text,
                    "type": entity.entity_type,
                    "start": entity.start_pos,
                    "end": entity.end_pos,
                    "normalized": entity.normalized_form
                }
                for entity in entities
            ],
            "entity_summary": entity_summary,
            "expanded_terms": expanded_terms
        }
    except Exception as e:
        logger.error(f"Error extracting entities: {e}")
        raise HTTPException(status_code=500, detail=f"Entity extraction failed: {str(e)}")


@router.post("/retrieve")
async def retrieve_documents(
    query: str,
    top_k: int = 10,
    score_threshold: float = 0.0,
    qdrant_client: HealthcareQdrantClient = Depends(get_qdrant_client),
    embeddings_model = Depends(get_embeddings_model)
):
    """Retrieve relevant documents without generation"""
    try:
        # Generate query embeddings and retrieve documents
        query_embedding = await embeddings_model.encode_query(query)
        documents = await qdrant_client.search_similar(
            query_vector=query_embedding['dense'],
            limit=top_k,
            score_threshold=score_threshold
        )
        
        return {
            "query": query,
            "documents": documents,
            "count": len(documents),
            "top_score": max([doc.get("score", 0.0) for doc in documents]) if documents else 0.0
        }
        
    except Exception as e:
        logger.error(f"Error retrieving documents: {e}")
        raise HTTPException(status_code=500, detail=f"Document retrieval failed: {str(e)}")


async def log_query_analytics(query: str, doc_count: int, entities: Dict, processing_time: float):
    """Log query analytics for monitoring (background task)"""
    try:
        analytics_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "query_length": len(query),
            "documents_retrieved": doc_count,
            "entity_types": list(entities.keys()),
            "entity_count": sum(len(ents) for ents in entities.values()),
            "processing_time": processing_time
        }
        
        # Here you could log to a database, file, or monitoring system
        logger.info(f"Query analytics: {analytics_data}")
        
    except Exception as e:
        logger.error(f"Error logging analytics: {e}")
