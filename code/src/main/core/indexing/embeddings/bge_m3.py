"""
BGE-M3 embeddings implementation for Healthcare RAG system
Handles multilingual medical embeddings using BAAI/bge-m3 model
"""

import asyncio
from typing import Dict, List, Optional, Union, Any
import numpy as np
import torch
from FlagEmbedding import BGEM3FlagModel
import logging
from pathlib import Path
import pickle
import hashlib

logger = logging.getLogger(__name__)


class BGEM3Embeddings:
    """BGE-M3 embeddings handler for medical documents"""
    
    def __init__(self, 
                 model_name: str = "BAAI/bge-m3",
                 device: str = "cpu",
                 use_fp16: bool = True,
                 max_length: int = 8192,
                 batch_size: int = 32,
                 cache_dir: Optional[Path] = None):
        
        self.model_name = model_name
        self.device = device
        self.use_fp16 = use_fp16
        self.max_length = max_length
        self.batch_size = batch_size
        self.cache_dir = cache_dir
        
        self.model = None
        self._embedding_cache = {}
        
        if cache_dir:
            self.cache_dir = Path(cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self._load_cache()
    
    async def initialize(self) -> bool:
        """Initialize the BGE-M3 model"""
        try:
            logger.info(f"Loading BGE-M3 model: {self.model_name}")
            
            # Load model in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(
                None, 
                self._load_model
            )
            
            logger.info("BGE-M3 model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize BGE-M3 model: {e}")
            return False
    
    def _load_model(self) -> BGEM3FlagModel:
        """Load the BGE-M3 model (runs in thread)"""
        return BGEM3FlagModel(
            self.model_name,
            use_fp16=self.use_fp16,
            device=self.device
        )
    
    async def encode_texts(self, 
                          texts: List[str], 
                          return_dense: bool = True,
                          return_sparse: bool = False,
                          return_colbert: bool = False) -> Dict[str, np.ndarray]:
        """Encode texts using BGE-M3 model"""
        if not self.model:
            await self.initialize()
        
        if not texts:
            return {}
        
        # Check cache first
        cached_results = {}
        texts_to_encode = []
        text_indices = []
        
        for i, text in enumerate(texts):
            cache_key = self._get_cache_key(text)
            if cache_key in self._embedding_cache:
                cached_results[i] = self._embedding_cache[cache_key]
            else:
                texts_to_encode.append(text)
                text_indices.append(i)
        
        # Encode uncached texts
        if texts_to_encode:
            try:
                loop = asyncio.get_event_loop()
                new_embeddings = await loop.run_in_executor(
                    None,
                    self._encode_batch,
                    texts_to_encode,
                    return_dense,
                    return_sparse,
                    return_colbert
                )
                
                # Cache new embeddings
                for i, text in enumerate(texts_to_encode):
                    cache_key = self._get_cache_key(text)
                    embedding_data = {}
                    
                    if return_dense and 'dense_vecs' in new_embeddings:
                        embedding_data['dense'] = new_embeddings['dense_vecs'][i]
                    if return_sparse and 'lexical_weights' in new_embeddings:
                        embedding_data['sparse'] = new_embeddings['lexical_weights'][i]
                    if return_colbert and 'colbert_vecs' in new_embeddings:
                        embedding_data['colbert'] = new_embeddings['colbert_vecs'][i]
                    
                    self._embedding_cache[cache_key] = embedding_data
                    cached_results[text_indices[i]] = embedding_data
                
                # Save cache periodically
                if len(self._embedding_cache) % 100 == 0:
                    self._save_cache()
                    
            except Exception as e:
                logger.error(f"Error encoding texts: {e}")
                return {}
        
        # Combine results
        result = {}
        if return_dense:
            result['dense_vecs'] = np.array([
                cached_results[i]['dense'] for i in range(len(texts))
                if i in cached_results and 'dense' in cached_results[i]
            ])
        
        if return_sparse:
            result['lexical_weights'] = [
                cached_results[i]['sparse'] for i in range(len(texts))
                if i in cached_results and 'sparse' in cached_results[i]
            ]
        
        if return_colbert:
            result['colbert_vecs'] = [
                cached_results[i]['colbert'] for i in range(len(texts))
                if i in cached_results and 'colbert' in cached_results[i]
            ]
        
        return result
    
    def _encode_batch(self, 
                     texts: List[str],
                     return_dense: bool,
                     return_sparse: bool,
                     return_colbert: bool) -> Dict[str, Any]:
        """Encode a batch of texts (runs in thread)"""
        return self.model.encode(
            texts,
            batch_size=self.batch_size,
            max_length=self.max_length,
            return_dense=return_dense,
            return_sparse=return_sparse,
            return_colbert_vecs=return_colbert
        )
    
    async def encode_query(self, query: str) -> Dict[str, np.ndarray]:
        """Encode a single query for retrieval"""
        results = await self.encode_texts(
            [query],
            return_dense=True,
            return_sparse=True,
            return_colbert=False
        )
        
        # Return single vectors instead of arrays
        encoded_query = {}
        if 'dense_vecs' in results and len(results['dense_vecs']) > 0:
            encoded_query['dense'] = results['dense_vecs'][0]
        if 'lexical_weights' in results and len(results['lexical_weights']) > 0:
            encoded_query['sparse'] = results['lexical_weights'][0]
        
        return encoded_query
    
    async def encode_documents(self, documents: List[str]) -> Dict[str, np.ndarray]:
        """Encode documents for indexing"""
        return await self.encode_texts(
            documents,
            return_dense=True,
            return_sparse=True,
            return_colbert=False
        )
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of dense embeddings"""
        if not self.model:
            return 1024  # BGE-M3 default dimension
        
        # Get dimension from model
        test_embedding = self.model.encode(["test"], return_dense=True)
        return test_embedding['dense_vecs'].shape[1]
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _load_cache(self):
        """Load embeddings cache from disk"""
        if not self.cache_dir:
            return
        
        cache_file = self.cache_dir / "bge_m3_cache.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    self._embedding_cache = pickle.load(f)
                logger.info(f"Loaded {len(self._embedding_cache)} cached embeddings")
            except Exception as e:
                logger.warning(f"Failed to load embedding cache: {e}")
                self._embedding_cache = {}
    
    def _save_cache(self):
        """Save embeddings cache to disk"""
        if not self.cache_dir:
            return
        
        cache_file = self.cache_dir / "bge_m3_cache.pkl"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(self._embedding_cache, f)
            logger.debug(f"Saved {len(self._embedding_cache)} embeddings to cache")
        except Exception as e:
            logger.warning(f"Failed to save embedding cache: {e}")
    
    def clear_cache(self):
        """Clear embeddings cache"""
        self._embedding_cache = {}
        if self.cache_dir:
            cache_file = self.cache_dir / "bge_m3_cache.pkl"
            if cache_file.exists():
                cache_file.unlink()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'cached_embeddings': len(self._embedding_cache),
            'cache_dir': str(self.cache_dir) if self.cache_dir else None,
            'model_name': self.model_name,
            'device': self.device
        }
