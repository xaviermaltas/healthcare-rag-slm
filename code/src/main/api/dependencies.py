"""
Dependencies for Healthcare RAG API
Provides shared instances of core components
"""

import asyncio
from typing import Optional
from functools import lru_cache
import logging

from config.settings import get_settings
from src.main.infrastructure.llm.ollama_client import OllamaClient
from src.main.infrastructure.vector_db.qdrant_client import HealthcareQdrantClient
from src.main.infrastructure.embeddings.bge_m3 import BGEM3Embeddings
from src.main.infrastructure.ontologies.snomed_client import SNOMEDClient
from src.main.infrastructure.ontologies.ontology_manager import OntologyManager
from src.main.core.retrieval.semantic_annotation import SemanticAnnotationService
from src.main.core.coding.medical_coding_service import MedicalCodingService

logger = logging.getLogger(__name__)
settings = get_settings()

# Global instances
_ollama_client: Optional[OllamaClient] = None
_qdrant_client: Optional[HealthcareQdrantClient] = None
_embeddings_model: Optional[BGEM3Embeddings] = None
_snomed_client: Optional[SNOMEDClient] = None
_ontology_manager: Optional[OntologyManager] = None
_semantic_annotation_service: Optional[SemanticAnnotationService] = None
_medical_coding_service: Optional[MedicalCodingService] = None


async def get_ollama_client() -> OllamaClient:
    """Get or create Ollama client instance"""
    global _ollama_client
    
    if _ollama_client is None:
        _ollama_client = OllamaClient(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            timeout=settings.OLLAMA_TIMEOUT
        )
        
        # Initialize client
        if not await _ollama_client.initialize():
            logger.warning("Failed to initialize Ollama client")
    
    return _ollama_client


async def get_qdrant_client() -> HealthcareQdrantClient:
    """Get or create Qdrant client instance"""
    global _qdrant_client
    
    if _qdrant_client is None:
        _qdrant_client = HealthcareQdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
            collection_name=settings.QDRANT_COLLECTION,
            vector_size=settings.QDRANT_VECTOR_SIZE
        )
        
        # Initialize client
        if not await _qdrant_client.initialize():
            logger.warning("Failed to initialize Qdrant client")
    
    return _qdrant_client


async def get_embeddings_model() -> BGEM3Embeddings:
    """Get or create embeddings model instance"""
    global _embeddings_model
    
    if _embeddings_model is None:
        _embeddings_model = BGEM3Embeddings(
            model_name=settings.EMBEDDING_MODEL,
            device=settings.EMBEDDING_DEVICE,
            batch_size=settings.EMBEDDING_BATCH_SIZE,
            cache_dir=settings.EMBEDDINGS_CACHE_DIR
        )
        
        # Initialize model
        if not await _embeddings_model.initialize():
            logger.warning("Failed to initialize embeddings model")
    
    return _embeddings_model


async def get_snomed_client() -> SNOMEDClient:
    """Get or create SNOMED CT client instance"""
    global _snomed_client
    
    if _snomed_client is None:
        if not settings.BIOPORTAL_API_KEY:
            logger.warning("BIOPORTAL_API_KEY not set - SNOMED CT features will be disabled")
            # Return a dummy client that will fail gracefully
            _snomed_client = SNOMEDClient(
                api_key="",
                base_url=settings.BIOPORTAL_BASE_URL
            )
        else:
            _snomed_client = SNOMEDClient(
                api_key=settings.BIOPORTAL_API_KEY,
                base_url=settings.BIOPORTAL_BASE_URL
            )
            
            # Initialize client
            if not await _snomed_client.initialize():
                logger.warning("Failed to initialize SNOMED CT client")
    
    return _snomed_client


async def get_ontology_manager() -> Optional[OntologyManager]:
    """Get or create OntologyManager instance"""
    global _ontology_manager
    
    if _ontology_manager is None:
        if not settings.BIOPORTAL_API_KEY:
            logger.warning("BIOPORTAL_API_KEY not set - Query expansion will be disabled")
            return None
        
        _ontology_manager = OntologyManager(
            api_key=settings.BIOPORTAL_API_KEY,
            base_url=settings.BIOPORTAL_BASE_URL
        )
        
        # Initialize manager
        if not await _ontology_manager.initialize():
            logger.warning("Failed to initialize OntologyManager")
            return None
        
        logger.info("OntologyManager initialized successfully")
    
    return _ontology_manager


async def get_semantic_annotation_service() -> SemanticAnnotationService:
    """Get or create Semantic Annotation Service instance"""
    global _semantic_annotation_service
    
    if _semantic_annotation_service is None:
        snomed_client = await get_snomed_client()
        _semantic_annotation_service = SemanticAnnotationService(snomed_client)
        logger.info("Semantic Annotation Service initialized")
    
    return _semantic_annotation_service


async def get_medical_coding_service() -> Optional[MedicalCodingService]:
    """Get or create Medical Coding Service instance"""
    global _medical_coding_service
    
    if _medical_coding_service is None:
        if not settings.BIOPORTAL_API_KEY:
            logger.warning("BIOPORTAL_API_KEY not set - Medical coding will be disabled")
            return None
        
        snomed_client = await get_snomed_client()
        ontology_manager = await get_ontology_manager()
        
        _medical_coding_service = MedicalCodingService(
            snomed_client=snomed_client,
            ontology_manager=ontology_manager
        )
        logger.info("Medical Coding Service initialized")
    
    return _medical_coding_service


async def cleanup_dependencies():
    """Cleanup all dependency instances"""
    global _ollama_client, _qdrant_client, _snomed_client, _ontology_manager
    
    if _ollama_client:
        await _ollama_client.close()
        _ollama_client = None
    
    if _snomed_client:
        await _snomed_client.close()
        _snomed_client = None
    
    if _ontology_manager:
        await _ontology_manager.close()
        _ontology_manager = None
    
    # Qdrant and embeddings don't need explicit cleanup
    _qdrant_client = None
    # _embeddings_model = None  # Temporalment desactivat
