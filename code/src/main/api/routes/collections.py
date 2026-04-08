"""
Collection management endpoints for Healthcare RAG system
Handles Qdrant collection operations and statistics
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional, Any
import logging

from src.main.api.dependencies import get_qdrant_client
from src.main.infrastructure.vector_db.qdrant_client import HealthcareQdrantClient

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def get_collection_info(
    qdrant_client: HealthcareQdrantClient = Depends(get_qdrant_client)
):
    """Get information about the main collection"""
    try:
        collection_info = await qdrant_client.get_collection_info()
        return collection_info
    except Exception as e:
        logger.error(f"Error getting collection info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get collection info: {str(e)}")


@router.delete("/clear")
async def clear_collection(
    qdrant_client: HealthcareQdrantClient = Depends(get_qdrant_client)
):
    """Clear all documents from the collection"""
    try:
        success = await qdrant_client.clear_collection()
        if success:
            return {"message": "Collection cleared successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear collection")
    except Exception as e:
        logger.error(f"Error clearing collection: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear collection: {str(e)}")


@router.get("/stats")
async def get_collection_stats(
    qdrant_client: HealthcareQdrantClient = Depends(get_qdrant_client)
):
    """Get collection statistics"""
    try:
        collection_info = await qdrant_client.get_collection_info()
        
        # Get sample documents to analyze sources and languages
        from qdrant_client.http import models
        sample_result = qdrant_client.client.scroll(
            collection_name=qdrant_client.collection_name,
            limit=100,
            with_payload=True,
            with_vectors=False
        )
        
        sources = {}
        languages = {}
        chunk_types = {}
        
        for point in sample_result[0]:
            payload = point.payload
            
            # Count sources
            source = payload.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1
            
            # Count languages
            language = payload.get('language', 'unknown')
            languages[language] = languages.get(language, 0) + 1
            
            # Count chunk types
            chunk_type = payload.get('chunk_type', 'unknown')
            chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
        
        return {
            "collection_info": collection_info,
            "sample_stats": {
                "sources": sources,
                "languages": languages,
                "chunk_types": chunk_types,
                "sample_size": len(sample_result[0])
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting collection stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get collection stats: {str(e)}")
