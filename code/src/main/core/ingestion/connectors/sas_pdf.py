"""
SAS PDF connector for Healthcare RAG system
Processes PDF documents from Servicio Andaluz de Salud (SAS)
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Iterator
import logging
import PyPDF2
from io import BytesIO
import aiohttp
from .base_connector import BaseConnector, Document

logger = logging.getLogger(__name__)


class SASPDFConnector(BaseConnector):
    """Connector for SAS PDF documents"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.pdf_directory = Path(self.config.get('pdf_directory', 'data/raw/sas_pdfs'))
        self.session = None
        
    async def connect(self) -> bool:
        """Establish connection (check if PDF directory exists)"""
        try:
            self.pdf_directory.mkdir(parents=True, exist_ok=True)
            self.session = aiohttp.ClientSession()
            return True
        except Exception as e:
            logger.error(f"Failed to initialize SAS PDF connector: {e}")
            return False
    
    async def fetch_documents(self, query: Optional[str] = None, limit: Optional[int] = None) -> Iterator[Document]:
        """Fetch and process PDF documents from SAS directory"""
        if not self.session:
            await self.connect()
        
        pdf_files = list(self.pdf_directory.glob("*.pdf"))
        
        if limit:
            pdf_files = pdf_files[:limit]
        
        for pdf_file in pdf_files:
            try:
                doc = await self._process_pdf_file(pdf_file)
                if doc and (not query or query.lower() in doc.content.lower()):
                    yield doc
            except Exception as e:
                logger.error(f"Error processing PDF {pdf_file}: {e}")
    
    async def _process_pdf_file(self, pdf_path: Path) -> Optional[Document]:
        """Process a single PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract text from all pages
                text_content = ""
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        text_content += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                    except Exception as e:
                        logger.warning(f"Error extracting text from page {page_num + 1} of {pdf_path}: {e}")
                
                if not text_content.strip():
                    logger.warning(f"No text extracted from {pdf_path}")
                    return None
                
                # Extract metadata
                metadata = {
                    'filename': pdf_path.name,
                    'file_path': str(pdf_path),
                    'file_size': pdf_path.stat().st_size,
                    'num_pages': len(pdf_reader.pages),
                    'source_type': 'sas_pdf',
                    'document_type': self._classify_document_type(pdf_path.name, text_content)
                }
                
                # Try to extract PDF metadata
                if pdf_reader.metadata:
                    metadata.update({
                        'title': pdf_reader.metadata.get('/Title', ''),
                        'author': pdf_reader.metadata.get('/Author', ''),
                        'subject': pdf_reader.metadata.get('/Subject', ''),
                        'creator': pdf_reader.metadata.get('/Creator', ''),
                        'creation_date': pdf_reader.metadata.get('/CreationDate', '')
                    })
                
                return Document(
                    id=pdf_path.stem,
                    source='sas_pdf',
                    language='es',
                    content=text_content.strip(),
                    metadata=metadata
                )
                
        except Exception as e:
            logger.error(f"Error processing PDF file {pdf_path}: {e}")
            return None
    
    def _classify_document_type(self, filename: str, content: str) -> str:
        """Classify document type based on filename and content"""
        filename_lower = filename.lower()
        content_lower = content.lower()
        
        # Classification based on common SAS document types
        if any(term in filename_lower for term in ['protocolo', 'protocol']):
            return 'protocol'
        elif any(term in filename_lower for term in ['guia', 'guide', 'guideline']):
            return 'guideline'
        elif any(term in filename_lower for term in ['procedimiento', 'procedure']):
            return 'procedure'
        elif any(term in filename_lower for term in ['informe', 'report']):
            return 'report'
        elif any(term in content_lower for term in ['diagnóstico', 'diagnosis']):
            return 'diagnostic_guide'
        elif any(term in content_lower for term in ['tratamiento', 'treatment']):
            return 'treatment_guide'
        else:
            return 'general_document'
    
    async def add_pdf_from_url(self, url: str, filename: str) -> bool:
        """Download and add PDF from URL"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    pdf_content = await response.read()
                    pdf_path = self.pdf_directory / filename
                    
                    with open(pdf_path, 'wb') as f:
                        f.write(pdf_content)
                    
                    logger.info(f"Downloaded PDF: {filename}")
                    return True
                else:
                    logger.error(f"Failed to download PDF from {url}: HTTP {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Error downloading PDF from {url}: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Close connection"""
        if self.session:
            await self.session.close()
            self.session = None
