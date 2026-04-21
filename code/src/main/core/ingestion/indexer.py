"""
Document Indexer for Healthcare RAG
Indexes documents from connectors into Qdrant with BGE-M3 embeddings
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import hashlib
import uuid

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Document representation for indexing"""
    content: str
    metadata: Dict[str, Any]
    doc_id: Optional[str] = None
    
    def __post_init__(self):
        if self.doc_id is None:
            # Generate unique ID from content hash
            content_hash = hashlib.md5(self.content.encode()).hexdigest()
            self.doc_id = f"doc_{content_hash[:16]}"


@dataclass
class Chunk:
    """Chunk representation for indexing"""
    content: str
    metadata: Dict[str, Any]
    chunk_id: Optional[str] = None
    embedding: Optional[List[float]] = None
    
    def __post_init__(self):
        if self.chunk_id is None:
            # Generate UUID from content hash for deterministic IDs
            content_hash = hashlib.md5(self.content.encode()).hexdigest()
            # Convert hash to UUID format
            self.chunk_id = str(uuid.UUID(content_hash))


class DocumentIndexer:
    """
    Indexes documents into Qdrant vector database
    
    Workflow:
    1. Receive documents from connectors
    2. Chunk documents (if needed)
    3. Generate embeddings with BGE-M3
    4. Index to Qdrant with metadata
    """
    
    def __init__(
        self,
        qdrant_client,
        embedding_model,
        collection_name: str = "healthcare_rag",
        chunk_size: int = 512,
        chunk_overlap: int = 50
    ):
        """
        Initialize indexer
        
        Args:
            qdrant_client: Qdrant client instance
            embedding_model: BGE-M3 embedding model
            collection_name: Qdrant collection name
            chunk_size: Maximum chunk size in tokens
            chunk_overlap: Overlap between chunks
        """
        self.qdrant_client = qdrant_client
        self.embedding_model = embedding_model
        self.collection_name = collection_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        logger.info(
            f"DocumentIndexer initialized: collection={collection_name}, "
            f"chunk_size={chunk_size}, overlap={chunk_overlap}"
        )
    
    async def index_documents(
        self,
        documents: List[Document],
        batch_size: int = 32,
        show_progress: bool = True
    ) -> Dict[str, Any]:
        """
        Index documents to Qdrant
        
        Args:
            documents: List of documents to index
            batch_size: Batch size for embedding generation
            show_progress: Show progress logs
        
        Returns:
            Dict with indexing statistics
        """
        logger.info(f"Starting indexing of {len(documents)} documents")
        
        stats = {
            'total_documents': len(documents),
            'total_chunks': 0,
            'indexed_chunks': 0,
            'failed_chunks': 0,
            'start_time': datetime.now().isoformat()
        }
        
        # Step 1: Chunk documents
        all_chunks = []
        for doc in documents:
            chunks = self._chunk_document(doc)
            all_chunks.extend(chunks)
            
            if show_progress and len(all_chunks) % 100 == 0:
                logger.info(f"Chunked {len(all_chunks)} chunks so far...")
        
        stats['total_chunks'] = len(all_chunks)
        logger.info(f"Created {len(all_chunks)} chunks from {len(documents)} documents")
        
        # Step 2: Generate embeddings in batches
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i:i + batch_size]
            
            try:
                # Extract texts
                texts = [chunk.content for chunk in batch]
                
                # Generate embeddings
                embeddings = await self._generate_embeddings(texts)
                
                # Assign embeddings to chunks
                for chunk, embedding in zip(batch, embeddings):
                    chunk.embedding = embedding
                
                if show_progress:
                    logger.info(
                        f"Generated embeddings for batch {i//batch_size + 1}/"
                        f"{(len(all_chunks) + batch_size - 1)//batch_size}"
                    )
            
            except Exception as e:
                logger.error(f"Error generating embeddings for batch {i//batch_size + 1}: {e}")
                stats['failed_chunks'] += len(batch)
                continue
        
        # Step 3: Index to Qdrant
        indexed_count = await self._index_chunks_to_qdrant(all_chunks, batch_size)
        stats['indexed_chunks'] = indexed_count
        
        stats['end_time'] = datetime.now().isoformat()
        
        logger.info(
            f"Indexing complete: {stats['indexed_chunks']}/{stats['total_chunks']} chunks indexed, "
            f"{stats['failed_chunks']} failed"
        )
        
        return stats
    
    def _chunk_document(self, document: Document) -> List[Chunk]:
        """
        Chunk a document into smaller pieces
        
        For ontology concepts: 1 chunk per concept
        For PubMed articles: chunk by sections (title, abstract, body)
        
        Args:
            document: Document to chunk
        
        Returns:
            List of chunks
        """
        chunks = []
        
        # Check document type from metadata
        doc_type = document.metadata.get('type', 'unknown')
        
        if doc_type == 'ontology_concept':
            # Ontology concepts: 1 chunk per concept
            chunk = Chunk(
                content=document.content,
                metadata={
                    **document.metadata,
                    'doc_id': document.doc_id,
                    'chunk_index': 0,
                    'total_chunks': 1
                }
            )
            chunks.append(chunk)
        
        elif doc_type == 'pubmed_article':
            # PubMed articles: chunk by sections
            chunks = self._chunk_pubmed_article(document)
        
        else:
            # Generic chunking by size
            chunks = self._chunk_by_size(document)
        
        return chunks
    
    def _chunk_pubmed_article(self, document: Document) -> List[Chunk]:
        """
        Chunk PubMed article by sections
        
        Sections: title, abstract, body (if available)
        """
        chunks = []
        metadata = document.metadata
        
        # Chunk 1: Title + Abstract (always together)
        title = metadata.get('title', '')
        abstract = metadata.get('abstract', '')
        
        if title or abstract:
            content = f"{title}\n\n{abstract}".strip()
            chunk = Chunk(
                content=content,
                metadata={
                    **metadata,
                    'doc_id': document.doc_id,
                    'chunk_index': 0,
                    'section': 'title_abstract',
                    'total_chunks': 1  # Will update later
                }
            )
            chunks.append(chunk)
        
        # Update total_chunks
        for chunk in chunks:
            chunk.metadata['total_chunks'] = len(chunks)
        
        return chunks
    
    def _chunk_by_size(self, document: Document) -> List[Chunk]:
        """
        Generic chunking by size with overlap
        
        Simple implementation: split by sentences and group
        """
        chunks = []
        
        # Split by sentences (simple approach)
        sentences = document.content.split('. ')
        
        current_chunk = []
        current_size = 0
        chunk_index = 0
        
        for sentence in sentences:
            sentence_size = len(sentence.split())
            
            if current_size + sentence_size > self.chunk_size and current_chunk:
                # Create chunk
                chunk_content = '. '.join(current_chunk) + '.'
                chunk = Chunk(
                    content=chunk_content,
                    metadata={
                        **document.metadata,
                        'doc_id': document.doc_id,
                        'chunk_index': chunk_index,
                        'total_chunks': 0  # Will update later
                    }
                )
                chunks.append(chunk)
                
                # Overlap: keep last sentence
                if self.chunk_overlap > 0 and current_chunk:
                    current_chunk = [current_chunk[-1]]
                    current_size = len(current_chunk[-1].split())
                else:
                    current_chunk = []
                    current_size = 0
                
                chunk_index += 1
            
            current_chunk.append(sentence)
            current_size += sentence_size
        
        # Last chunk
        if current_chunk:
            chunk_content = '. '.join(current_chunk) + '.'
            chunk = Chunk(
                content=chunk_content,
                metadata={
                    **document.metadata,
                    'doc_id': document.doc_id,
                    'chunk_index': chunk_index,
                    'total_chunks': 0
                }
            )
            chunks.append(chunk)
        
        # Update total_chunks
        for chunk in chunks:
            chunk.metadata['total_chunks'] = len(chunks)
        
        return chunks
    
    async def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for texts using BGE-M3
        
        Args:
            texts: List of texts to embed
        
        Returns:
            List of embeddings (dense vectors)
        """
        try:
            embeddings = []
            
            # BGE-M3 encode_query returns dict with 'dense', 'sparse', 'colbert'
            # We need to call it for each text and extract dense embeddings
            for text in texts:
                result = await self.embedding_model.encode_query(text)
                # Extract dense embedding
                dense_embedding = result.get('dense', result.get('embedding', []))
                embeddings.append(dense_embedding)
            
            return embeddings
        
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    async def _index_chunks_to_qdrant(
        self,
        chunks: List[Chunk],
        batch_size: int = 100
    ) -> int:
        """
        Index chunks to Qdrant
        
        Args:
            chunks: List of chunks with embeddings
            batch_size: Batch size for Qdrant upload
        
        Returns:
            Number of successfully indexed chunks
        """
        indexed_count = 0
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            
            # Filter chunks with embeddings
            valid_chunks = [c for c in batch if c.embedding is not None]
            
            if not valid_chunks:
                continue
            
            try:
                # Prepare points for Qdrant
                points = []
                for chunk in valid_chunks:
                    point = {
                        'id': chunk.chunk_id,
                        'vector': chunk.embedding,
                        'payload': {
                            'content': chunk.content,
                            **chunk.metadata
                        }
                    }
                    points.append(point)
                
                # Upload to Qdrant
                await self._upload_points_to_qdrant(points)
                
                indexed_count += len(valid_chunks)
                
                logger.info(
                    f"Indexed batch {i//batch_size + 1}: "
                    f"{len(valid_chunks)} chunks ({indexed_count} total)"
                )
            
            except Exception as e:
                logger.error(f"Error indexing batch {i//batch_size + 1}: {e}")
                continue
        
        return indexed_count
    
    async def _upload_points_to_qdrant(self, points: List[Dict[str, Any]]):
        """
        Upload points to Qdrant
        
        Args:
            points: List of points to upload
        """
        # Assuming qdrant_client has an async upsert method
        try:
            if hasattr(self.qdrant_client, 'upsert_async'):
                await self.qdrant_client.upsert_async(
                    collection_name=self.collection_name,
                    points=points
                )
            else:
                # Sync fallback
                await asyncio.to_thread(
                    self.qdrant_client.upsert,
                    collection_name=self.collection_name,
                    points=points
                )
        
        except Exception as e:
            logger.error(f"Error uploading to Qdrant: {e}")
            raise
