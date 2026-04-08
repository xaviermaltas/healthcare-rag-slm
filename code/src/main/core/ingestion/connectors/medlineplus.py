"""
MedlinePlus connector for Healthcare RAG system
Fetches medical information from MedlinePlus API
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Iterator
import logging
from .base_connector import BaseConnector, Document

logger = logging.getLogger(__name__)


class MedlinePlusConnector(BaseConnector):
    """Connector for MedlinePlus medical information"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.base_url = self.config.get('base_url', 'https://wsearch.nlm.nih.gov/ws/query')
        self.session = None
        
    async def connect(self) -> bool:
        """Establish connection to MedlinePlus API"""
        try:
            self.session = aiohttp.ClientSession()
            # Test connection with a simple query
            async with self.session.get(f"{self.base_url}?db=healthTopics&term=diabetes") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to MedlinePlus: {e}")
            return False
    
    async def fetch_documents(self, query: Optional[str] = None, limit: Optional[int] = 10) -> Iterator[Document]:
        """Fetch medical documents from MedlinePlus"""
        if not self.session:
            await self.connect()
        
        if not query:
            query = "health topics"
        
        try:
            params = {
                'db': 'healthTopics',
                'term': query,
                'retmax': limit or 10,
                'rettype': 'json'
            }
            
            async with self.session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for item in data.get('nlmSearchResult', {}).get('list', []):
                        doc = self._parse_medlineplus_item(item)
                        if doc:
                            yield doc
                else:
                    logger.error(f"MedlinePlus API error: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error fetching from MedlinePlus: {e}")
    
    def _parse_medlineplus_item(self, item: Dict[str, Any]) -> Optional[Document]:
        """Parse MedlinePlus item into Document format"""
        try:
            content = item.get('content', '')
            title = item.get('title', '')
            
            # Combine title and content
            full_content = f"{title}\n\n{content}" if title else content
            
            metadata = {
                'title': title,
                'url': item.get('FullSummary', {}).get('Url', ''),
                'source_type': 'medlineplus',
                'language': item.get('language', 'en'),
                'last_updated': item.get('DateCreated', ''),
                'categories': item.get('MeshHeadings', [])
            }
            
            return Document(
                id=item.get('DocumentId', ''),
                source='medlineplus',
                language='en',
                content=full_content,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error parsing MedlinePlus item: {e}")
            return None
    
    async def disconnect(self) -> None:
        """Close connection to MedlinePlus API"""
        if self.session:
            await self.session.close()
            self.session = None
