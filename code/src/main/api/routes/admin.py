"""
Admin endpoints for Healthcare RAG system
Provides system administration and maintenance operations
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging
import asyncio

from src.main.api.dependencies import get_ollama_client, get_qdrant_client, get_embeddings_model
from src.main.infrastructure.llm.ollama_client import OllamaClient
from src.main.infrastructure.vector_db.qdrant_client import HealthcareQdrantClient
# from src.main.infrastructure.embeddings.bge_m3 import BGEM3Embeddings  # Temporarily disabled

logger = logging.getLogger(__name__)
router = APIRouter()


class SystemStatus(BaseModel):
    """System status response model"""
    overall_status: str
    components: Dict[str, Any]
    uptime: float
    memory_usage: Dict[str, Any]


@router.get("/status")
async def get_system_status(
    ollama_client: OllamaClient = Depends(get_ollama_client),
    qdrant_client: HealthcareQdrantClient = Depends(get_qdrant_client),
    embeddings_model = Depends(get_embeddings_model)
):
    """Get comprehensive system status"""
    try:
        # Check all components
        ollama_healthy = await ollama_client.health_check()
        qdrant_healthy = await qdrant_client.health_check()
        
        # Get detailed info
        ollama_models = await ollama_client.get_available_models()
        collection_info = await qdrant_client.get_collection_info()
        
        # Determine overall status
        all_healthy = ollama_healthy and qdrant_healthy
        overall_status = "healthy" if all_healthy else "degraded"
        
        return {
            "overall_status": overall_status,
            "components": {
                "ollama": {
                    "status": "healthy" if ollama_healthy else "unhealthy",
                    "models_available": len(ollama_models),
                    "default_model": ollama_client.model
                },
                "qdrant": {
                    "status": "healthy" if qdrant_healthy else "unhealthy",
                    "collection_info": collection_info
                },
                "embeddings": {
                    "status": "healthy" if await embeddings_model.health_check() else "unhealthy",
                    "model": embeddings_model.model_name
                }
            },
            "timestamp": asyncio.get_event_loop().time()
        }
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")


@router.post("/initialize")
async def initialize_system(
    background_tasks: BackgroundTasks,
    ollama_client: OllamaClient = Depends(get_ollama_client),
    qdrant_client: HealthcareQdrantClient = Depends(get_qdrant_client),
    embeddings_model = Depends(get_embeddings_model)
):
    """Initialize or reinitialize system components"""
    try:
        # Initialize components in background
        background_tasks.add_task(
            initialize_components,
            ollama_client,
            qdrant_client
        )
        
        return {"message": "System initialization started in background"}
        
    except Exception as e:
        logger.error(f"Error starting system initialization: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start initialization: {str(e)}")


@router.post("/maintenance/rebuild-index")
async def rebuild_index(
    background_tasks: BackgroundTasks,
    qdrant_client: HealthcareQdrantClient = Depends(get_qdrant_client)
):
    """Rebuild the vector index (maintenance operation)"""
    try:
        background_tasks.add_task(rebuild_vector_index, qdrant_client)
        return {"message": "Index rebuild started in background"}
        
    except Exception as e:
        logger.error(f"Error starting index rebuild: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start index rebuild: {str(e)}")


@router.get("/logs")
async def get_recent_logs(limit: int = 100):
    """Get recent system logs"""
    try:
        # This is a simplified implementation
        # In production, you'd read from actual log files
        return {
            "message": "Log retrieval not implemented",
            "note": "Check application logs directly for detailed information"
        }
        
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get logs: {str(e)}")


async def initialize_components(
    ollama_client: OllamaClient,
    qdrant_client: HealthcareQdrantClient
):
    """Initialize all system components (background task)"""
    try:
        logger.info("Starting system component initialization...")
        
        # Initialize Ollama
        if not await ollama_client.initialize():
            logger.error("Failed to initialize Ollama client")
        else:
            logger.info("Ollama client initialized successfully")
        
        # Initialize Qdrant
        if not await qdrant_client.initialize():
            logger.error("Failed to initialize Qdrant client")
        else:
            logger.info("Qdrant client initialized successfully")
        
        # Initialize embeddings
        if await embeddings_model.health_check():
            logger.info("Embeddings model initialized successfully")
        else:
            logger.warning("Embeddings model initialization failed")
        
        logger.info("System component initialization completed")
        
    except Exception as e:
        logger.error(f"Error during component initialization: {e}", exc_info=True)


async def rebuild_vector_index(qdrant_client: HealthcareQdrantClient):
    """Rebuild vector index (background task)"""
    try:
        logger.info("Starting vector index rebuild...")
        
        # Get collection info
        collection_info = await qdrant_client.get_collection_info()
        logger.info(f"Current collection has {collection_info.get('points_count', 0)} points")
        
        # In a real implementation, you would:
        # 1. Create a new temporary collection
        # 2. Re-process all documents
        # 3. Generate new embeddings
        # 4. Swap collections
        # 5. Delete old collection
        
        logger.info("Vector index rebuild completed (placeholder implementation)")
        
    except Exception as e:
        logger.error(f"Error during index rebuild: {e}", exc_info=True)
