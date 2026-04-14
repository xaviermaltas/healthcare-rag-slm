"""
Document management endpoints for Healthcare RAG system
Handles document ingestion, processing, and management
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import asyncio
import logging
from datetime import datetime
import tempfile
import os
import uuid

from src.main.api.dependencies import get_qdrant_client, get_embeddings_model
from src.main.infrastructure.vector_db.qdrant_client import HealthcareQdrantClient
from src.main.infrastructure.embeddings.bge_m3 import BGEM3Embeddings
from src.main.core.ingestion.connectors.sas_pdf import SASPDFConnector
from src.main.core.ingestion.processors.text_cleaner import TextCleaner
from src.main.core.ingestion.chunking.medical_chunker import MedicalChunker

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize processors
text_cleaner = TextCleaner()
medical_chunker = MedicalChunker()


class DocumentUploadResponse(BaseModel):
    """Response model for document upload"""
    document_id: str
    filename: str
    status: str
    chunks_created: int
    processing_time: float
    message: str


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    source: str = "upload",
    language: str = "es",
    qdrant_client: HealthcareQdrantClient = Depends(get_qdrant_client),
    embeddings_model: BGEM3Embeddings = Depends(get_embeddings_model)
):
    """Upload and process a document"""
    
    start_time = asyncio.get_event_loop().time()
    
    # Validate file type
    allowed_types = ["application/pdf", "text/plain", "application/msword"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type: {file.content_type}"
        )
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Process document based on type
        if file.content_type == "application/pdf":
            # Use SAS PDF connector for processing
            pdf_connector = SASPDFConnector()
            await pdf_connector.connect()
            
            # Process the PDF file
            from pathlib import Path
            pdf_path = Path(temp_file_path)
            document = await pdf_connector._process_pdf_file(pdf_path)
            
        elif file.content_type == "text/plain":
            # Process plain text
            with open(temp_file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            
            # Clean text
            cleaned_content = text_cleaner.clean_text(text_content)
            
            document = {
                'id': file.filename.replace('.', '_'),
                'source': source,
                'language': language,
                'content': cleaned_content,
                'metadata': {
                    'filename': file.filename,
                    'source_type': 'text_upload',
                    'file_size': len(content)
                }
            }
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported file processing")
        
        if not document:
            raise HTTPException(status_code=400, detail="Failed to process document")
        
        # Chunk the document
        chunks = medical_chunker.chunk_document(
            document['content'], 
            document.get('metadata', {})
        )
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No chunks created from document")
        
        # Process in background
        background_tasks.add_task(
            process_document_chunks,
            chunks,
            document,
            qdrant_client,
            embeddings_model
        )
        
        # Cleanup temp file
        os.unlink(temp_file_path)
        
        processing_time = asyncio.get_event_loop().time() - start_time
        
        return DocumentUploadResponse(
            document_id=document['id'],
            filename=file.filename,
            status="processing",
            chunks_created=len(chunks),
            processing_time=processing_time,
            message=f"Document uploaded successfully. {len(chunks)} chunks will be processed in background."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}", exc_info=True)
        # Cleanup temp file if it exists
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Document upload failed: {str(e)}")


@router.get("/")
async def list_documents(
    limit: int = 50,
    source: Optional[str] = None,
    language: Optional[str] = None,
    qdrant_client: HealthcareQdrantClient = Depends(get_qdrant_client)
):
    """List documents in the system"""
    try:
        # Build filter conditions
        filter_conditions = {}
        if source:
            filter_conditions['source'] = source
        if language:
            filter_conditions['language'] = language
        
        # Get documents from Qdrant
        if filter_conditions:
            documents = await qdrant_client.search_by_text_filter(
                text_query="",
                limit=limit,
                source_filter=source,
                language_filter=language
            )
        else:
            # Get all documents (using scroll)
            from qdrant_client.http import models
            search_result = qdrant_client.client.scroll(
                collection_name=qdrant_client.collection_name,
                limit=limit,
                with_payload=True,
                with_vectors=False
            )
            
            documents = []
            for point in search_result[0]:
                documents.append({
                    'id': point.id,
                    'content': point.payload.get('content', '')[:200] + "...",
                    'source': point.payload.get('source', ''),
                    'language': point.payload.get('language', ''),
                    'metadata': point.payload.get('metadata', {})
                })
        
        return {
            "documents": documents,
            "count": len(documents),
            "filters": filter_conditions
        }
        
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    qdrant_client: HealthcareQdrantClient = Depends(get_qdrant_client)
):
    """Delete a document and all its chunks"""
    try:
        success = await qdrant_client.delete_documents([document_id])
        
        if success:
            return {"message": f"Document {document_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Document not found or deletion failed")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    qdrant_client: HealthcareQdrantClient = Depends(get_qdrant_client)
):
    """Get a specific document by ID"""
    try:
        # Search for document by ID
        documents = await qdrant_client.search_by_text_filter(
            text_query="",
            limit=1
        )
        
        # Filter by document ID (this is a simplified approach)
        document = None
        for doc in documents:
            if doc.get('id') == document_id:
                document = doc
                break
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")


async def process_document_chunks(
    chunks,
    document,
    qdrant_client: HealthcareQdrantClient,
    embeddings_model: BGEM3Embeddings
):
    """Process document chunks in background: embed + index to Qdrant"""
    try:
        logger.info(f"Processing {len(chunks)} chunks for document {document['id']}")
        
        # Build document list and extract texts for embedding
        qdrant_documents = []
        texts = []
        
        for i, chunk in enumerate(chunks):
            doc_data = {
                'id': str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{document['id']}_chunk_{i}")),
                'content': chunk.content,
                'source': document['source'],
                'language': document['language'],
                'chunk_type': chunk.chunk_type,
                'metadata': {
                    **document.get('metadata', {}),
                    'chunk_index': i,
                    'chunk_start': chunk.start_index,
                    'chunk_end': chunk.end_index,
                    'parent_document': document['id']
                }
            }
            qdrant_documents.append(doc_data)
            texts.append(chunk.content)
        
        # Generate embeddings (BGE-M3 dense vectors)
        logger.info(f"Generating embeddings for {len(texts)} chunks...")
        embeddings_result = await embeddings_model.encode_documents(texts)
        vectors = embeddings_result['dense_vecs']
        
        # Index to Qdrant
        success = await qdrant_client.add_documents(
            documents=qdrant_documents,
            vectors=vectors
        )
        
        if success:
            logger.info(f"Successfully indexed {len(chunks)} chunks for document {document['id']}")
        else:
            logger.error(f"Failed to index chunks to Qdrant for document {document['id']}")
            
    except Exception as e:
        logger.error(f"Error processing document chunks: {e}", exc_info=True)
