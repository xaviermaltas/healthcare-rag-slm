"""
BioPortal connector for Healthcare RAG system
Fetches medical ontologies and concepts from BioPortal API
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Iterator
import logging
from .base_connector import BaseConnector, Document

logger = logging.getLogger(__name__)


class BioPortalConnector(BaseConnector):
    """Connector for BioPortal ontology data"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.base_url = self.config.get('base_url', 'https://data.bioontology.org')
        self.api_key = self.config.get('api_key', '')
        self.session = None
        
    async def connect(self) -> bool:
        """Establish connection to BioPortal API"""
        if not self.api_key:
            logger.error("BioPortal API key not provided")
            return False
            
        try:
            headers = {'Authorization': f'apikey token={self.api_key}'}
            self.session = aiohttp.ClientSession(headers=headers)
            
            # Test connection
            async with self.session.get(f"{self.base_url}/ontologies") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to BioPortal: {e}")
            return False
    
    async def fetch_documents(self, query: Optional[str] = None, limit: Optional[int] = 10) -> Iterator[Document]:
        """Fetch ontology concepts from BioPortal"""
        if not self.session:
            await self.connect()
        
        if not query:
            query = "disease"
        
        try:
            # Search for concepts
            params = {
                'q': query,
                'pagesize': limit or 10,
                'ontologies': 'SNOMEDCT,ICD10CM,MESH'
            }
            
            async with self.session.get(f"{self.base_url}/search", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for item in data.get('collection', []):
                        doc = await self._parse_bioportal_concept(item)
                        if doc:
                            yield doc
                else:
                    logger.error(f"BioPortal API error: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error fetching from BioPortal: {e}")
    
    async def _parse_bioportal_concept(self, concept: Dict[str, Any]) -> Optional[Document]:
        """Parse BioPortal concept into Document format"""
        try:
            # Get detailed concept information
            concept_id = concept.get('@id', '')
            if not concept_id:
                return None
            
            async with self.session.get(concept_id) as response:
                if response.status == 200:
                    detailed_concept = await response.json()
                else:
                    detailed_concept = concept
            
            pref_label = detailed_concept.get('prefLabel', '')
            definition = detailed_concept.get('definition', [])
            if isinstance(definition, list) and definition:
                definition = definition[0]
            
            content = f"{pref_label}\n\n{definition}" if definition else pref_label
            
            metadata = {
                'concept_id': concept_id,
                'pref_label': pref_label,
                'definition': definition,
                'ontology': detailed_concept.get('links', {}).get('ontology', ''),
                'synonyms': detailed_concept.get('synonym', []),
                'semantic_types': detailed_concept.get('semanticType', []),
                'source_type': 'bioportal'
            }
            
            return Document(
                id=concept_id.split('/')[-1],
                source='bioportal',
                language='en',
                content=content,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error parsing BioPortal concept: {e}")
            return None
    
    async def get_concept_by_id(self, concept_id: str, ontology: str = 'SNOMEDCT') -> Optional[Document]:
        """Get specific concept by ID"""
        try:
            url = f"{self.base_url}/ontologies/{ontology}/classes/{concept_id}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    concept = await response.json()
                    return await self._parse_bioportal_concept(concept)
        except Exception as e:
            logger.error(f"Error fetching concept {concept_id}: {e}")
        return None
    
    async def disconnect(self) -> None:
        """Close connection to BioPortal API"""
        if self.session:
            await self.session.close()
            self.session = None
