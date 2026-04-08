"""
Health check endpoints for Healthcare RAG system
Provides system status and component health monitoring
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import asyncio
import logging

from src.main.api.dependencies import get_ollama_client, get_qdrant_client
from src.main.infrastructure.llm.ollama_client import OllamaClient
from src.main.infrastructure.vector_db.qdrant_client import HealthcareQdrantClient
# from src.main.infrastructure.embeddings.bge_m3 import BGEM3Embeddings  # Temporarily disabled

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
async def health_check(
    ollama_client: OllamaClient = Depends(get_ollama_client),
    qdrant_client: HealthcareQdrantClient = Depends(get_qdrant_client)
):
    """Main health check endpoint"""
    
    health_status = {
        "status": "healthy",
        "components": {},
        "timestamp": asyncio.get_event_loop().time()
    }
    
    # Check Ollama
    try:
        ollama_healthy = await ollama_client.health_check()
        available_models = await ollama_client.get_available_models()
        
        health_status["components"]["ollama"] = {
            "status": "healthy" if ollama_healthy else "unhealthy",
            "available_models": [model.get("name", "") for model in available_models],
            "model_count": len(available_models)
        }
    except Exception as e:
        health_status["components"]["ollama"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Check Qdrant
    try:
        qdrant_healthy = await qdrant_client.health_check()
        collection_info = await qdrant_client.get_collection_info()
        
        health_status["components"]["qdrant"] = {
            "status": "healthy" if qdrant_healthy else "unhealthy",
            "collection_info": collection_info
        }
    except Exception as e:
        health_status["components"]["qdrant"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Embeddings temporarily disabled
    health_status["components"]["embeddings"] = {
        "status": "disabled",
        "message": "Embeddings temporarily disabled for compatibility"
    }
    
    # Determine overall status
    component_statuses = [comp.get("status") for comp in health_status["components"].values()]
    if "error" in component_statuses:
        health_status["status"] = "unhealthy"
    elif "unhealthy" in component_statuses:
        health_status["status"] = "degraded"
    
    return health_status


@router.get("/ollama")
async def ollama_health(ollama_client: OllamaClient = Depends(get_ollama_client)):
    """Detailed Ollama health check"""
    try:
        is_healthy = await ollama_client.health_check()
        models = await ollama_client.get_available_models()
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "base_url": ollama_client.base_url,
            "default_model": ollama_client.model,
            "available_models": models,
            "model_count": len(models)
        }
    except Exception as e:
        logger.error(f"Ollama health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Ollama health check failed: {str(e)}")


@router.get("/qdrant")
async def qdrant_health(qdrant_client: HealthcareQdrantClient = Depends(get_qdrant_client)):
    """Detailed Qdrant health check"""
    try:
        is_healthy = await qdrant_client.health_check()
        collection_info = await qdrant_client.get_collection_info()
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "host": qdrant_client.host,
            "port": qdrant_client.port,
            "collection_name": qdrant_client.collection_name,
            "collection_info": collection_info
        }
    except Exception as e:
        logger.error(f"Qdrant health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Qdrant health check failed: {str(e)}")


@router.get("/embeddings")
async def embeddings_health():
    """Detailed embeddings model health check"""
    return {
        "status": "disabled",
        "message": "Embeddings temporarily disabled for compatibility"
    }


@router.get("/ready")
async def readiness_check(
    ollama_client: OllamaClient = Depends(get_ollama_client),
    qdrant_client: HealthcareQdrantClient = Depends(get_qdrant_client)
):
    """Kubernetes-style readiness check"""
    try:
        # Check all critical components
        ollama_ready = await ollama_client.health_check()
        qdrant_ready = await qdrant_client.health_check()
        
        if ollama_ready and qdrant_ready:
            return {"status": "ready"}
        else:
            raise HTTPException(
                status_code=503, 
                detail="System not ready - one or more components are unhealthy"
            )
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="System not ready")


@router.get("/live")
async def liveness_check():
    """Kubernetes-style liveness check"""
    return {"status": "alive", "timestamp": asyncio.get_event_loop().time()}
