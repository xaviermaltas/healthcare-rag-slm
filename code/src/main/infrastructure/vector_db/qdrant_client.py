"""
Qdrant client for Healthcare RAG system
Handles vector storage and retrieval using Qdrant database
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import logging
import uuid

logger = logging.getLogger(__name__)


class HealthcareQdrantClient:
    """Qdrant client specialized for healthcare RAG system"""
    
    def __init__(self, 
                 host: str = "localhost",
                 port: int = 6333,
                 collection_name: str = "healthcare_rag",
                 vector_size: int = 1024):
        
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.client = None
        
    async def initialize(self) -> bool:
        """Initialize Qdrant client and create collection if needed"""
        try:
            self.client = QdrantClient(host=self.host, port=self.port)
            
            # Check if collection exists, create if not
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                await self._create_collection()
                logger.info(f"Created Qdrant collection: {self.collection_name}")
            else:
                logger.info(f"Using existing Qdrant collection: {self.collection_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant client: {e}")
            return False
    
    async def _create_collection(self):
        """Create Qdrant collection with appropriate configuration"""
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.vector_size,
                distance=Distance.COSINE
            ),
            optimizers_config=models.OptimizersConfig(
                default_segment_number=2,
                max_segment_size=20000,
                memmap_threshold=20000,
                indexing_threshold=20000
            ),
            hnsw_config=models.HnswConfig(
                m=16,
                ef_construct=100,
                full_scan_threshold=10000,
                max_indexing_threads=0
            )
        )
    
    async def add_documents(self, 
                          documents: List[Dict[str, Any]], 
                          vectors: np.ndarray,
                          batch_size: int = 100) -> bool:
        """Add documents with their vectors to Qdrant"""
        if not self.client:
            await self.initialize()
        
        try:
            points = []
            for i, (doc, vector) in enumerate(zip(documents, vectors)):
                point_id = doc.get('id', str(uuid.uuid4()))
                
                # Prepare payload with document metadata
                payload = {
                    'content': doc.get('content', ''),
                    'source': doc.get('source', ''),
                    'language': doc.get('language', 'es'),
                    'chunk_type': doc.get('chunk_type', 'content'),
                    'metadata': doc.get('metadata', {})
                }
                
                # Add any additional fields from document
                for key, value in doc.items():
                    if key not in ['id', 'content', 'source', 'language', 'chunk_type', 'metadata']:
                        payload[key] = value
                
                points.append(PointStruct(
                    id=point_id,
                    vector=vector.tolist() if isinstance(vector, np.ndarray) else vector,
                    payload=payload
                ))
            
            # Upload in batches
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )
                logger.debug(f"Uploaded batch {i//batch_size + 1}/{(len(points)-1)//batch_size + 1}")
            
            logger.info(f"Successfully added {len(documents)} documents to Qdrant")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents to Qdrant: {e}")
            return False
    
    async def search_similar(self, 
                           query_vector: np.ndarray,
                           limit: int = 10,
                           score_threshold: float = 0.0,
                           filter_conditions: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search for similar documents using vector similarity"""
        if not self.client:
            await self.initialize()
        
        try:
            # Prepare search filter
            search_filter = None
            if filter_conditions:
                search_filter = models.Filter(
                    must=[
                        models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value)
                        ) for key, value in filter_conditions.items()
                    ]
                )
            
            # Perform search
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector.tolist() if isinstance(query_vector, np.ndarray) else query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=search_filter,
                with_payload=True,
                with_vectors=False
            )
            
            # Format results
            results = []
            for hit in search_result:
                result = {
                    'id': hit.id,
                    'score': hit.score,
                    'content': hit.payload.get('content', ''),
                    'source': hit.payload.get('source', ''),
                    'language': hit.payload.get('language', ''),
                    'chunk_type': hit.payload.get('chunk_type', ''),
                    'metadata': hit.payload.get('metadata', {})
                }
                
                # Add any additional payload fields
                for key, value in hit.payload.items():
                    if key not in ['content', 'source', 'language', 'chunk_type', 'metadata']:
                        result[key] = value
                
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search in Qdrant: {e}")
            return []
    
    async def search_by_text_filter(self, 
                                  text_query: str,
                                  limit: int = 10,
                                  source_filter: Optional[str] = None,
                                  language_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search documents by text content filtering"""
        if not self.client:
            await self.initialize()
        
        try:
            # Build filter conditions
            filter_conditions = []
            
            if source_filter:
                filter_conditions.append(
                    models.FieldCondition(
                        key="source",
                        match=models.MatchValue(value=source_filter)
                    )
                )
            
            if language_filter:
                filter_conditions.append(
                    models.FieldCondition(
                        key="language",
                        match=models.MatchValue(value=language_filter)
                    )
                )
            
            # Add text search condition
            filter_conditions.append(
                models.FieldCondition(
                    key="content",
                    match=models.MatchText(text=text_query)
                )
            )
            
            search_filter = models.Filter(must=filter_conditions)
            
            # Perform filtered search
            search_result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=search_filter,
                limit=limit,
                with_payload=True,
                with_vectors=False
            )
            
            # Format results
            results = []
            for point in search_result[0]:  # scroll returns (points, next_page_offset)
                result = {
                    'id': point.id,
                    'content': point.payload.get('content', ''),
                    'source': point.payload.get('source', ''),
                    'language': point.payload.get('language', ''),
                    'chunk_type': point.payload.get('chunk_type', ''),
                    'metadata': point.payload.get('metadata', {})
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search by text filter in Qdrant: {e}")
            return []
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection"""
        if not self.client:
            await self.initialize()
        
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                'name': collection_info.config.params.vectors.size,
                'vector_size': collection_info.config.params.vectors.size,
                'distance': collection_info.config.params.vectors.distance,
                'points_count': collection_info.points_count,
                'segments_count': collection_info.segments_count,
                'status': collection_info.status
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {}
    
    async def delete_documents(self, document_ids: List[str]) -> bool:
        """Delete documents by their IDs"""
        if not self.client:
            await self.initialize()
        
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=document_ids
                )
            )
            logger.info(f"Deleted {len(document_ids)} documents from Qdrant")
            return True
        except Exception as e:
            logger.error(f"Failed to delete documents from Qdrant: {e}")
            return False
    
    async def clear_collection(self) -> bool:
        """Clear all documents from the collection"""
        if not self.client:
            await self.initialize()
        
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.HasIdCondition(has_id=[])
                        ]
                    )
                )
            )
            logger.info("Cleared all documents from Qdrant collection")
            return True
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Check if Qdrant is healthy and accessible"""
        try:
            if not self.client:
                await self.initialize()
            
            # Try to get collection info
            collections = self.client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return False
