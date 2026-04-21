"""
Ontology endpoints for Healthcare RAG system
Provides access to SNOMED CT and semantic annotation
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from src.main.api.dependencies import get_snomed_client, get_semantic_annotation_service
from src.main.infrastructure.ontologies.snomed_client import SNOMEDClient
from src.main.core.retrieval.semantic_annotation import SemanticAnnotationService

logger = logging.getLogger(__name__)
router = APIRouter()


class ConceptSearchRequest(BaseModel):
    """Request model for concept search"""
    query: str = Field(..., description="Search term", min_length=1, max_length=200)
    limit: int = Field(default=10, ge=1, le=50, description="Maximum results")
    semantic_types: Optional[List[str]] = Field(default=None, description="Filter by semantic types")


class ConceptResponse(BaseModel):
    """Response model for SNOMED concept"""
    concept_id: str
    pref_label: str
    definition: str = ""
    synonyms: List[str] = []
    semantic_type: str = ""


class AnnotationRequest(BaseModel):
    """Request model for semantic annotation"""
    text: str = Field(..., description="Medical text to annotate", min_length=1, max_length=5000)
    min_confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum confidence threshold")


class AnnotationResponse(BaseModel):
    """Response model for semantic annotations"""
    text: str
    annotations: List[Dict[str, Any]]
    summary: Dict[str, Any]


class QueryExpansionRequest(BaseModel):
    """Request model for query expansion"""
    query: str = Field(..., description="Original query", min_length=1, max_length=500)
    include_synonyms: bool = Field(default=True, description="Include SNOMED synonyms")
    include_parents: bool = Field(default=False, description="Include parent concepts")


@router.post("/search", response_model=List[ConceptResponse])
async def search_concepts(
    request: ConceptSearchRequest,
    snomed_client: SNOMEDClient = Depends(get_snomed_client)
):
    """
    Search SNOMED CT concepts by text query
    
    Example:
    ```json
    {
        "query": "diabetes tipo 2",
        "limit": 5,
        "semantic_types": ["Disease or Syndrome"]
    }
    ```
    """
    try:
        concepts = await snomed_client.search_concepts(
            query=request.query,
            limit=request.limit,
            semantic_types=request.semantic_types
        )
        
        return [
            ConceptResponse(
                concept_id=c.concept_id,
                pref_label=c.pref_label,
                definition=c.definition,
                synonyms=c.synonyms,
                semantic_type=c.semantic_type
            )
            for c in concepts
        ]
        
    except Exception as e:
        logger.error(f"Error searching SNOMED concepts: {e}")
        raise HTTPException(status_code=500, detail=f"Concept search failed: {str(e)}")


@router.get("/concept/{concept_id}", response_model=ConceptResponse)
async def get_concept(
    concept_id: str,
    snomed_client: SNOMEDClient = Depends(get_snomed_client)
):
    """
    Get SNOMED CT concept by ID
    
    Example: GET /ontology/concept/44054006
    """
    try:
        concept = await snomed_client.get_concept_by_id(concept_id)
        
        if not concept:
            raise HTTPException(status_code=404, detail=f"Concept {concept_id} not found")
        
        return ConceptResponse(
            concept_id=concept.concept_id,
            pref_label=concept.pref_label,
            definition=concept.definition,
            synonyms=concept.synonyms,
            semantic_type=concept.semantic_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching concept {concept_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Concept retrieval failed: {str(e)}")


@router.post("/annotate", response_model=AnnotationResponse)
async def annotate_text(
    request: AnnotationRequest,
    annotation_service: SemanticAnnotationService = Depends(get_semantic_annotation_service)
):
    """
    Annotate medical text with SNOMED CT codes
    
    Example:
    ```json
    {
        "text": "Paciente con diabetes mellitus tipo 2 e hipertensión arterial",
        "min_confidence": 0.6
    }
    ```
    
    Returns medical entities with their SNOMED CT codes
    """
    try:
        annotations = await annotation_service.annotate_text(
            text=request.text,
            min_confidence=request.min_confidence
        )
        
        summary = annotation_service.get_annotation_summary(annotations)
        
        return AnnotationResponse(
            text=request.text,
            annotations=[ann.to_dict() for ann in annotations],
            summary=summary
        )
        
    except Exception as e:
        logger.error(f"Error annotating text: {e}")
        raise HTTPException(status_code=500, detail=f"Annotation failed: {str(e)}")


@router.post("/expand-query", response_model=Dict[str, Any])
async def expand_query(
    request: QueryExpansionRequest,
    annotation_service: SemanticAnnotationService = Depends(get_semantic_annotation_service)
):
    """
    Expand query with SNOMED CT synonyms and related terms
    
    Example:
    ```json
    {
        "query": "diabetes",
        "include_synonyms": true,
        "include_parents": false
    }
    ```
    
    Returns expanded query terms for better retrieval
    """
    try:
        expanded_terms = await annotation_service.get_expanded_query_terms(
            text=request.query,
            include_synonyms=request.include_synonyms,
            include_parents=request.include_parents
        )
        
        return {
            "original_query": request.query,
            "expanded_terms": expanded_terms,
            "expansion_count": len(expanded_terms) - 1  # Exclude original
        }
        
    except Exception as e:
        logger.error(f"Error expanding query: {e}")
        raise HTTPException(status_code=500, detail=f"Query expansion failed: {str(e)}")


@router.get("/concept/{concept_id}/hierarchy")
async def get_concept_hierarchy(
    concept_id: str,
    snomed_client: SNOMEDClient = Depends(get_snomed_client)
):
    """
    Get concept hierarchy (parents and children)
    
    Example: GET /ontology/concept/44054006/hierarchy
    """
    try:
        hierarchy = await snomed_client.get_hierarchy(concept_id)
        
        return {
            "concept_id": concept_id,
            "parents": hierarchy.get('parents', []),
            "children": hierarchy.get('children', [])
        }
        
    except Exception as e:
        logger.error(f"Error fetching hierarchy for {concept_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Hierarchy retrieval failed: {str(e)}")
