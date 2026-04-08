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
# from src.main.infrastructure.embeddings.bge_m3 import BGEM3Embeddings  # Temporalment desactivat

logger = logging.getLogger(__name__)
settings = get_settings()

# Global instances
_ollama_client: Optional[OllamaClient] = None
_qdrant_client: Optional[HealthcareQdrantClient] = None
# _embeddings_model: Optional[BGEM3Embeddings] = None  # Temporalment desactivat


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


# Temporalment desactivat per evitar dependències de torch
# @lru_cache()
# async def get_embeddings_model() -> BGEM3Embeddings:
#     """Get or create embeddings model instance"""
#     global _embeddings_model
#     
#     if _embeddings_model is None:
#         _embeddings_model = BGEM3Embeddings(
#             model_name=settings.EMBEDDING_MODEL,
#             device=settings.EMBEDDING_DEVICE,
#             batch_size=settings.EMBEDDING_BATCH_SIZE,
#             cache_dir=settings.EMBEDDINGS_CACHE_DIR
#         )
#         
#         # Initialize model
#         if not await _embeddings_model.initialize():
#             logger.warning("Failed to initialize embeddings model")
#     
#     return _embeddings_model

async def get_embeddings_model():
    """Placeholder - embeddings temporalment desactivats"""
    raise NotImplementedError("Embeddings temporalment desactivats per compatibilitat")


async def cleanup_dependencies():
    """Cleanup all dependency instances"""
    global _ollama_client, _qdrant_client
    
    if _ollama_client:
        await _ollama_client.close()
        _ollama_client = None
    
    # Qdrant and embeddings don't need explicit cleanup
    _qdrant_client = None
    # _embeddings_model = None  # Temporalment desactivat
