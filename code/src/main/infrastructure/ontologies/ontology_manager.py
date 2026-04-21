"""
Unified Ontology Manager for Healthcare RAG
Manages SNOMED CT, MeSH, and ICD-10 ontologies via BioPortal API
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class OntologyType(Enum):
    """Supported ontology types"""
    SNOMED_CT = "SNOMEDCT"
    MESH = "MESH"
    ICD10 = "ICD10CM"


@dataclass
class OntologyConcept:
    """Unified concept representation across ontologies"""
    concept_id: str
    ontology: OntologyType
    pref_label: str
    definition: str = ""
    synonyms: List[str] = None
    semantic_types: List[str] = None
    parents: List[str] = None
    children: List[str] = None
    cui: Optional[str] = None  # UMLS Concept Unique Identifier
    
    def __post_init__(self):
        if self.synonyms is None:
            self.synonyms = []
        if self.semantic_types is None:
            self.semantic_types = []
        if self.parents is None:
            self.parents = []
        if self.children is None:
            self.children = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'concept_id': self.concept_id,
            'ontology': self.ontology.value,
            'pref_label': self.pref_label,
            'definition': self.definition,
            'synonyms': self.synonyms,
            'semantic_types': self.semantic_types,
            'parents': self.parents,
            'children': self.children,
            'cui': self.cui
        }


class OntologyManager:
    """
    Unified manager for medical ontologies
    
    Supports:
    - SNOMED CT: Clinical terminology (350k+ concepts)
    - MeSH: Medical Subject Headings (30k+ descriptors)
    - ICD-10: Disease classification (70k+ codes)
    """
    
    def __init__(self, api_key: str, base_url: str = "https://data.bioontology.org"):
        """
        Initialize ontology manager
        
        Args:
            api_key: BioPortal API key
            base_url: BioPortal API base URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self._cache: Dict[str, OntologyConcept] = {}
        
    async def initialize(self) -> bool:
        """Initialize connection to BioPortal"""
        try:
            headers = {
                'Authorization': f'apikey token={self.api_key}',
                'Accept': 'application/json'
            }
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(headers=headers, timeout=timeout)
            
            # Test connection
            async with self.session.get(f"{self.base_url}/ontologies") as response:
                if response.status == 200:
                    logger.info("OntologyManager initialized successfully")
                    return True
                else:
                    logger.error(f"BioPortal API returned status {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to initialize OntologyManager: {e}")
            return False
    
    async def close(self) -> None:
        """Close connection"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def search_concepts(
        self,
        query: str,
        ontologies: List[OntologyType] = None,
        limit: int = 10,
        semantic_types: Optional[List[str]] = None
    ) -> List[OntologyConcept]:
        """
        Search concepts across multiple ontologies
        
        Args:
            query: Search term
            ontologies: List of ontologies to search (default: all)
            limit: Maximum results per ontology
            semantic_types: Filter by semantic types
            
        Returns:
            List of matching concepts
        """
        if not self.session:
            await self.initialize()
        
        if ontologies is None:
            ontologies = [OntologyType.SNOMED_CT, OntologyType.MESH, OntologyType.ICD10]
        
        try:
            ontology_str = ','.join([ont.value for ont in ontologies])
            params = {
                'q': query,
                'pagesize': limit,
                'ontologies': ontology_str,
                'require_exact_match': 'false',
                'also_search_properties': 'true'
            }
            
            if semantic_types:
                params['semantic_types'] = ','.join(semantic_types)
            
            async with self.session.get(f"{self.base_url}/search", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    concepts = []
                    
                    for item in data.get('collection', []):
                        concept = await self._parse_concept(item)
                        if concept:
                            concepts.append(concept)
                    
                    logger.info(f"Found {len(concepts)} concepts for query: {query}")
                    return concepts
                else:
                    logger.error(f"Search failed with status {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error searching concepts: {e}")
            return []
    
    async def get_concept_by_id(
        self,
        concept_id: str,
        ontology: OntologyType
    ) -> Optional[OntologyConcept]:
        """
        Get concept by ID from specific ontology
        
        Args:
            concept_id: Concept identifier
            ontology: Ontology type
            
        Returns:
            Concept or None if not found
        """
        cache_key = f"{ontology.value}:{concept_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            url = f"{self.base_url}/ontologies/{ontology.value}/classes/{concept_id}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    concept = await self._parse_concept(data, ontology)
                    if concept:
                        self._cache[cache_key] = concept
                    return concept
                else:
                    logger.warning(f"Concept {concept_id} not found in {ontology.value}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching concept {concept_id}: {e}")
            return None
    
    async def get_hierarchy(
        self,
        concept_id: str,
        ontology: OntologyType,
        depth: int = 1
    ) -> Dict[str, List[str]]:
        """
        Get concept hierarchy (parents and children)
        
        Args:
            concept_id: Concept identifier
            ontology: Ontology type
            depth: Hierarchy depth (1=immediate, 2=grandparents/grandchildren)
            
        Returns:
            Dict with 'parents' and 'children' lists
        """
        try:
            # Get parents
            parents_url = f"{self.base_url}/ontologies/{ontology.value}/classes/{concept_id}/parents"
            parents = []
            async with self.session.get(parents_url) as response:
                if response.status == 200:
                    data = await response.json()
                    for item in data.get('collection', []):
                        parents.append(item.get('prefLabel', ''))
            
            # Get children
            children_url = f"{self.base_url}/ontologies/{ontology.value}/classes/{concept_id}/children"
            children = []
            async with self.session.get(children_url) as response:
                if response.status == 200:
                    data = await response.json()
                    for item in data.get('collection', []):
                        children.append(item.get('prefLabel', ''))
            
            return {
                'parents': parents[:10],  # Limit to avoid overwhelming
                'children': children[:10]
            }
            
        except Exception as e:
            logger.error(f"Error fetching hierarchy: {e}")
            return {'parents': [], 'children': []}
    
    async def map_text_to_concepts(
        self,
        text: str,
        ontologies: List[OntologyType] = None,
        top_k: int = 5,
        min_score: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Map free text to ontology concepts with relevance scoring
        
        Args:
            text: Input text
            ontologies: Target ontologies
            top_k: Maximum concepts to return
            min_score: Minimum relevance score
            
        Returns:
            List of concepts with scores
        """
        concepts = await self.search_concepts(text, ontologies, limit=top_k * 2)
        
        # Score concepts based on text similarity
        scored_concepts = []
        text_lower = text.lower()
        
        for concept in concepts:
            score = self._calculate_relevance_score(text_lower, concept)
            
            if score >= min_score:
                scored_concepts.append({
                    'concept': concept.to_dict(),
                    'score': score,
                    'matched_term': concept.pref_label
                })
        
        # Sort by score and return top-k
        scored_concepts.sort(key=lambda x: x['score'], reverse=True)
        return scored_concepts[:top_k]
    
    def _calculate_relevance_score(self, query: str, concept: OntologyConcept) -> float:
        """Calculate relevance score between query and concept"""
        score = 0.0
        
        # Exact match with preferred label
        if query == concept.pref_label.lower():
            score = 1.0
        # Partial match with preferred label
        elif query in concept.pref_label.lower() or concept.pref_label.lower() in query:
            score = 0.8
        # Match with synonyms
        elif any(query in syn.lower() or syn.lower() in query for syn in concept.synonyms):
            score = 0.7
        # Match with definition
        elif concept.definition and query in concept.definition.lower():
            score = 0.6
        else:
            # Token overlap score
            query_tokens = set(query.split())
            label_tokens = set(concept.pref_label.lower().split())
            overlap = len(query_tokens & label_tokens)
            if overlap > 0:
                score = 0.5 + (overlap / max(len(query_tokens), len(label_tokens))) * 0.3
        
        return min(score, 1.0)
    
    async def _parse_concept(
        self,
        data: Dict[str, Any],
        ontology: Optional[OntologyType] = None
    ) -> Optional[OntologyConcept]:
        """Parse BioPortal API response into OntologyConcept"""
        try:
            # Determine ontology from data if not provided
            if not ontology:
                ontology_link = data.get('links', {}).get('ontology', '')
                if 'SNOMEDCT' in ontology_link:
                    ontology = OntologyType.SNOMED_CT
                elif 'MESH' in ontology_link:
                    ontology = OntologyType.MESH
                elif 'ICD10CM' in ontology_link:
                    ontology = OntologyType.ICD10
                else:
                    logger.warning(f"Unknown ontology in: {ontology_link}")
                    return None
            
            concept_id = data.get('@id', '').split('/')[-1]
            pref_label = data.get('prefLabel', '')
            
            if not concept_id or not pref_label:
                return None
            
            # Extract definition
            definition = data.get('definition', [])
            if isinstance(definition, list) and definition:
                definition = definition[0]
            elif not isinstance(definition, str):
                definition = ""
            
            # Extract synonyms
            synonyms = data.get('synonym', [])
            if not isinstance(synonyms, list):
                synonyms = [synonyms] if synonyms else []
            
            # Extract semantic types
            semantic_types = data.get('semanticType', [])
            if not isinstance(semantic_types, list):
                semantic_types = [semantic_types] if semantic_types else []
            
            # Extract CUI (UMLS identifier)
            cui = data.get('cui', None)
            
            return OntologyConcept(
                concept_id=concept_id,
                ontology=ontology,
                pref_label=pref_label,
                definition=definition,
                synonyms=synonyms,
                semantic_types=semantic_types,
                cui=cui
            )
            
        except Exception as e:
            logger.error(f"Error parsing concept: {e}")
            return None
    
    async def get_ontology_stats(self) -> Dict[str, Any]:
        """Get statistics about available ontologies"""
        stats = {}
        
        for ontology in [OntologyType.SNOMED_CT, OntologyType.MESH, OntologyType.ICD10]:
            try:
                url = f"{self.base_url}/ontologies/{ontology.value}"
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        stats[ontology.value] = {
                            'name': data.get('name', ''),
                            'acronym': data.get('acronym', ''),
                            'num_classes': data.get('numberOfClasses', 0),
                            'version': data.get('version', ''),
                            'description': data.get('description', '')[:200]
                        }
            except Exception as e:
                logger.error(f"Error fetching stats for {ontology.value}: {e}")
                stats[ontology.value] = {'error': str(e)}
        
        return stats
