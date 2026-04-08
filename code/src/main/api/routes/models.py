"""
Model management endpoints for Healthcare RAG system
Handles Ollama model operations and embeddings model info
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging

from src.main.api.dependencies import get_ollama_client
from src.main.infrastructure.llm.ollama_client import OllamaClient
# from src.main.infrastructure.embeddings.bge_m3 import BGEM3Embeddings  # Temporarily disabled

logger = logging.getLogger(__name__)
router = APIRouter()


class ModelPullRequest(BaseModel):
    """Request model for pulling a new model"""
    model_name: str


@router.get("/ollama")
async def get_ollama_models(
    ollama_client: OllamaClient = Depends(get_ollama_client)
):
    """Get available Ollama models"""
    try:
        models = await ollama_client.get_available_models()
        return {
            "models": models,
            "count": len(models),
            "default_model": ollama_client.model
        }
    except Exception as e:
        logger.error(f"Error getting Ollama models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get models: {str(e)}")


@router.post("/ollama/pull")
async def pull_ollama_model(
    request: ModelPullRequest,
    ollama_client: OllamaClient = Depends(get_ollama_client)
):
    """Pull a new Ollama model"""
    try:
        success = await ollama_client.pull_model(request.model_name)
        if success:
            return {"message": f"Model {request.model_name} pulled successfully"}
        else:
            raise HTTPException(status_code=500, detail=f"Failed to pull model {request.model_name}")
    except Exception as e:
        logger.error(f"Error pulling model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to pull model: {str(e)}")


@router.delete("/ollama/{model_name}")
async def delete_ollama_model(
    model_name: str,
    ollama_client: OllamaClient = Depends(get_ollama_client)
):
    """Delete an Ollama model"""
    try:
        success = await ollama_client.delete_model(model_name)
        if success:
            return {"message": f"Model {model_name} deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail=f"Failed to delete model {model_name}")
    except Exception as e:
        logger.error(f"Error deleting model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete model: {str(e)}")


@router.get("/embeddings")
async def get_embeddings_info():
    """Get embeddings model information"""
    return {
        "status": "disabled",
        "message": "Embeddings temporarily disabled for compatibility"
    }


@router.delete("/embeddings/cache")
async def clear_embeddings_cache():
    """Clear embeddings cache"""
    return {
        "status": "disabled",
        "message": "Embeddings temporarily disabled for compatibility"
    }
