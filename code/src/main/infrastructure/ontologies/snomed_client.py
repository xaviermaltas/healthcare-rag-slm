"""
SNOMED CT Client via BioPortal API
Provides semantic search, concept mapping, and hierarchy navigation
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class SNOMEDConcept:
    """Represents a SNOMED CT concept"""
    concept_id: str
    pref_label: str
    definition: str = ""
    synonyms: List[str] = None
    semantic_type: str = ""
    parents: List[str] = None
    children: List[str] = None
    
    def __post_init__(self):
        if self.synonyms is None:
            self.synonyms = []
        if self.parents is None:
            self.parents = []
        if self.children is None:
            self.children = []


class SNOMEDClient:
    """Client for SNOMED CT via BioPortal API"""
    
    def __init__(self, api_key: str, base_url: str = "https://data.bioontology.org"):
        """
        Initialize SNOMED CT client
        
        Args:
            api_key: BioPortal API key (get free at https://bioportal.bioontology.org/account)
            base_url: BioPortal API base URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.ontology = "SNOMEDCT"
        self.session = None
        
    async def initialize(self) -> bool:
        """Initialize HTTP session and test connection"""
        try:
            headers = {
                'Authorization': f'apikey token={self.api_key}',
                'Accept': 'application/json'
            }
            self.session = aiohttp.ClientSession(headers=headers)
            
            # Test connection
            async with self.session.get(f"{self.base_url}/ontologies/{self.ontology}") as response:
                if response.status == 200:
                    logger.info("SNOMED CT client initialized successfully")
                    return True
                else:
                    logger.error(f"Failed to connect to SNOMED CT: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to initialize SNOMED CT client: {e}")
            return False
    
    async def search_concepts(self, 
                            query: str, 
                            limit: int = 10,
                            semantic_types: Optional[List[str]] = None) -> List[SNOMEDConcept]:
        """
        Search SNOMED CT concepts by text query
        
        Args:
            query: Search term (e.g., "diabetes", "insuficiencia cardíaca")
            limit: Maximum number of results
            semantic_types: Filter by semantic types (e.g., ["Disease or Syndrome"])
            
        Returns:
            List of SNOMED concepts matching the query
        """
        if not self.session:
            await self.initialize()
        
        try:
            params = {
                'q': query,
                'ontologies': self.ontology,
                'pagesize': limit,
                'suggest': 'true',  # Enable fuzzy matching
                'require_exact_match': 'false'
            }
            
            async with self.session.get(f"{self.base_url}/search", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    concepts = []
                    
                    for item in data.get('collection', []):
                        concept = await self._parse_concept(item)
                        if concept:
                            # Filter by semantic type if specified
                            if semantic_types and concept.semantic_type not in semantic_types:
                                continue
                            concepts.append(concept)
                    
                    logger.info(f"Found {len(concepts)} SNOMED concepts for query: {query}")
                    return concepts
                else:
                    logger.error(f"SNOMED search failed: HTTP {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error searching SNOMED concepts: {e}")
            return []
    
    async def get_concept_by_id(self, concept_id: str) -> Optional[SNOMEDConcept]:
        """
        Get SNOMED concept by ID
        
        Args:
            concept_id: SNOMED CT concept ID (e.g., "44054006" for Diabetes mellitus type 2)
            
        Returns:
            SNOMED concept or None if not found
        """
        if not self.session:
            await self.initialize()
        
        try:
            # Encode concept ID for URL
            encoded_id = f"http://purl.bioontology.org/ontology/SNOMEDCT/{concept_id}"
            url = f"{self.base_url}/ontologies/{self.ontology}/classes/{encoded_id}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return await self._parse_concept(data)
                else:
                    logger.warning(f"Concept {concept_id} not found: HTTP {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching concept {concept_id}: {e}")
            return None
    
    async def map_text_to_concepts(self, 
                                  text: str, 
                                  top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Map medical text to SNOMED CT concepts
        
        Args:
            text: Medical text (e.g., "paciente con diabetes tipo 2")
            top_k: Number of top concepts to return
            
        Returns:
            List of mappings with concept and confidence score
        """
        concepts = await self.search_concepts(text, limit=top_k)
        
        mappings = []
        for concept in concepts:
            # Calculate simple relevance score based on text similarity
            score = self._calculate_relevance(text.lower(), concept)
            
            mappings.append({
                'concept_id': concept.concept_id,
                'pref_label': concept.pref_label,
                'definition': concept.definition,
                'score': score,
                'semantic_type': concept.semantic_type
            })
        
        # Sort by score descending
        mappings.sort(key=lambda x: x['score'], reverse=True)
        return mappings[:top_k]
    
    def _calculate_relevance(self, query: str, concept: SNOMEDConcept) -> float:
        """Calculate relevance score between query and concept"""
        query_lower = query.lower()
        pref_label_lower = concept.pref_label.lower()
        
        # Exact match
        if query_lower == pref_label_lower:
            return 1.0
        
        # Substring match in preferred label
        if query_lower in pref_label_lower or pref_label_lower in query_lower:
            return 0.8
        
        # Synonym match
        for synonym in concept.synonyms:
            synonym_lower = synonym.lower()
            if query_lower == synonym_lower:
                return 0.9
            if query_lower in synonym_lower or synonym_lower in query_lower:
                return 0.7
        
        # Word overlap
        query_words = set(query_lower.split())
        label_words = set(pref_label_lower.split())
        overlap = len(query_words & label_words)
        
        if overlap > 0:
            return 0.5 + (overlap / max(len(query_words), len(label_words))) * 0.3
        
        return 0.3  # Default low score
    
    async def get_hierarchy(self, concept_id: str) -> Dict[str, List[str]]:
        """
        Get concept hierarchy (parents and children)
        
        Args:
            concept_id: SNOMED CT concept ID
            
        Returns:
            Dict with 'parents' and 'children' lists
        """
        if not self.session:
            await self.initialize()
        
        try:
            encoded_id = f"http://purl.bioontology.org/ontology/SNOMEDCT/{concept_id}"
            
            # Get parents
            parents_url = f"{self.base_url}/ontologies/{self.ontology}/classes/{encoded_id}/parents"
            async with self.session.get(parents_url) as response:
                parents = []
                if response.status == 200:
                    data = await response.json()
                    parents = [item.get('prefLabel', '') for item in data.get('collection', [])]
            
            # Get children
            children_url = f"{self.base_url}/ontologies/{self.ontology}/classes/{encoded_id}/children"
            async with self.session.get(children_url) as response:
                children = []
                if response.status == 200:
                    data = await response.json()
                    children = [item.get('prefLabel', '') for item in data.get('collection', [])]
            
            return {
                'parents': parents,
                'children': children
            }
            
        except Exception as e:
            logger.error(f"Error fetching hierarchy for {concept_id}: {e}")
            return {'parents': [], 'children': []}
    
    async def _parse_concept(self, data: Dict[str, Any]) -> Optional[SNOMEDConcept]:
        """Parse BioPortal API response into SNOMEDConcept"""
        try:
            # Extract concept ID from URL
            concept_url = data.get('@id', '')
            concept_id = concept_url.split('/')[-1] if concept_url else ''
            
            if not concept_id:
                return None
            
            pref_label = data.get('prefLabel', '')
            
            # Handle definition (can be list or string)
            definition = data.get('definition', [])
            if isinstance(definition, list):
                definition = definition[0] if definition else ''
            
            # Extract synonyms
            synonyms = data.get('synonym', [])
            if not isinstance(synonyms, list):
                synonyms = [synonyms] if synonyms else []
            
            # Extract semantic type
            semantic_types = data.get('semanticType', [])
            semantic_type = semantic_types[0] if isinstance(semantic_types, list) and semantic_types else str(semantic_types) if semantic_types else ''
            
            return SNOMEDConcept(
                concept_id=concept_id,
                pref_label=pref_label,
                definition=definition,
                synonyms=synonyms,
                semantic_type=semantic_type
            )
            
        except Exception as e:
            logger.error(f"Error parsing SNOMED concept: {e}")
            return None
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("SNOMED CT client closed")
