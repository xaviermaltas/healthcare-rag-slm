"""
Base connector class for Healthcare RAG data sources
Provides common interface and functionality for all data connectors
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Iterator
from dataclasses import dataclass
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Standard document format for Healthcare RAG system"""
    id: str
    source: str
    language: str
    content: str
    metadata: Dict[str, Any]
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if not self.id:
            self.id = str(uuid.uuid4())


class BaseConnector(ABC):
    """Base class for all data source connectors"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.source_name = self.__class__.__name__.lower().replace('connector', '')
        
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to data source"""
        pass
    
    @abstractmethod
    async def fetch_documents(self, query: Optional[str] = None, limit: Optional[int] = None) -> Iterator[Document]:
        """Fetch documents from data source"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to data source"""
        pass
    
    def normalize_document(self, raw_data: Dict[str, Any]) -> Document:
        """Convert raw data to standardized Document format"""
        return Document(
            id=raw_data.get('id', str(uuid.uuid4())),
            source=self.source_name,
            language=raw_data.get('language', 'es'),
            content=raw_data.get('content', ''),
            metadata=raw_data.get('metadata', {})
        )
    
    async def health_check(self) -> bool:
        """Check if connector is healthy and can connect"""
        try:
            return await self.connect()
        except Exception as e:
            logger.error(f"Health check failed for {self.source_name}: {e}")
            return False
