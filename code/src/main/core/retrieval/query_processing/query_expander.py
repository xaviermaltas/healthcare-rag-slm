"""
Query Expander for Healthcare RAG
Expands user queries with medical ontology terms (SNOMED CT, MeSH, ICD-10)
"""

import logging
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass

from src.main.infrastructure.ontologies.ontology_manager import OntologyManager, OntologyType
from src.main.core.retrieval.query_processing.medical_ner import MedicalNER

logger = logging.getLogger(__name__)


@dataclass
class ExpandedTerm:
    """Represents an expanded term with metadata"""
    term: str
    source: str  # 'original', 'synonym', 'code', 'related'
    weight: float  # Importance weight for retrieval
    ontology: Optional[str] = None
    concept_id: Optional[str] = None


@dataclass
class ExpandedQuery:
    """Query with expanded terms"""
    original_query: str
    expanded_terms: List[ExpandedTerm]
    entities_detected: List[Any]  # List of MedicalEntity objects
    
    def get_search_text(self, include_codes: bool = True) -> str:
        """
        Get combined search text for retrieval
        
        Args:
            include_codes: Whether to include ontology codes
        
        Returns:
            Combined search text with weights
        """
        # Group terms by weight
        weighted_terms = []
        
        for term in self.expanded_terms:
            # Skip codes if not requested
            if not include_codes and term.source == 'code':
                continue
            
            # Add term with repetition based on weight
            repetitions = int(term.weight * 3)  # Max 3 repetitions
            weighted_terms.extend([term.term] * max(1, repetitions))
        
        return ' '.join(weighted_terms)
    
    def get_terms_by_source(self) -> Dict[str, List[str]]:
        """Group terms by source"""
        by_source = {}
        for term in self.expanded_terms:
            if term.source not in by_source:
                by_source[term.source] = []
            by_source[term.source].append(term.term)
        return by_source


class QueryExpander:
    """
    Expands queries with medical ontology terms
    
    Workflow:
    1. Extract medical entities from query (MedicalNER)
    2. For each entity, search in ontologies (SNOMED, MeSH, ICD)
    3. Add synonyms and related terms
    4. Weight terms by relevance
    5. Return expanded query
    """
    
    def __init__(
        self,
        ontology_manager: OntologyManager,
        medical_ner: Optional[MedicalNER] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize QueryExpander
        
        Args:
            ontology_manager: OntologyManager instance
            medical_ner: MedicalNER instance (optional, will create if None)
            config: Configuration dict
        """
        self.ontology_manager = ontology_manager
        self.medical_ner = medical_ner or MedicalNER()
        
        # Default configuration
        self.config = {
            'max_synonyms_per_entity': 5,
            'max_concepts_per_entity': 3,
            'include_codes': True,
            'include_synonyms': True,
            'include_related': False,
            'ontologies': [OntologyType.SNOMED_CT, OntologyType.MESH, OntologyType.ICD10],
            'weights': {
                'original': 1.0,
                'synonym': 0.8,
                'code': 0.5,
                'related': 0.3
            },
            'min_concept_score': 0.5
        }
        
        # Update with user config
        if config:
            self.config.update(config)
        
        logger.info(f"QueryExpander initialized with config: {self.config}")
    
    async def expand_query(self, query: str) -> ExpandedQuery:
        """
        Expand query with ontology terms
        
        Args:
            query: Original user query
        
        Returns:
            ExpandedQuery with all expanded terms
        """
        logger.info(f"Expanding query: '{query}'")
        
        expanded_terms = []
        
        # Step 1: Add original query terms
        original_terms = self._extract_original_terms(query)
        expanded_terms.extend(original_terms)
        
        # Step 2: Extract medical entities
        entities = self.medical_ner.extract_entities(query)
        logger.info(f"Detected {len(entities)} medical entities")
        
        # Step 3: Expand each entity with ontology terms
        for entity in entities:
            entity_terms = await self._expand_entity(entity)
            expanded_terms.extend(entity_terms)
        
        # Step 4: Remove duplicates (keep highest weight)
        expanded_terms = self._deduplicate_terms(expanded_terms)
        
        logger.info(
            f"Query expanded: {len(expanded_terms)} total terms "
            f"({len(original_terms)} original + {len(expanded_terms) - len(original_terms)} ontology)"
        )
        
        return ExpandedQuery(
            original_query=query,
            expanded_terms=expanded_terms,
            entities_detected=entities
        )
    
    def _extract_original_terms(self, query: str) -> List[ExpandedTerm]:
        """Extract terms from original query"""
        terms = []
        
        # Split query into words (simple tokenization)
        words = query.lower().split()
        
        # Filter stop words (simple list)
        stop_words = {'el', 'la', 'de', 'en', 'a', 'para', 'con', 'por', 'un', 'una', 
                     'es', 'que', 'del', 'los', 'las', 'y', 'o', 'si', 'no'}
        
        for word in words:
            if word not in stop_words and len(word) > 2:
                terms.append(ExpandedTerm(
                    term=word,
                    source='original',
                    weight=self.config['weights']['original']
                ))
        
        # Also add full query
        terms.append(ExpandedTerm(
            term=query.lower(),
            source='original',
            weight=self.config['weights']['original']
        ))
        
        return terms
    
    async def _expand_entity(self, entity: Any) -> List[ExpandedTerm]:
        """
        Expand a single entity with ontology terms
        
        Args:
            entity: MedicalEntity from MedicalNER
        
        Returns:
            List of expanded terms
        """
        entity_text = entity.text
        entity_type = entity.entity_type
        
        logger.debug(f"Expanding entity: '{entity_text}' ({entity_type})")
        
        expanded_terms = []
        
        try:
            # Search in ontologies
            concepts = await self.ontology_manager.search_concepts(
                query=entity_text,
                ontologies=self.config['ontologies'],
                limit=self.config['max_concepts_per_entity']
            )
            
            logger.debug(f"Found {len(concepts)} concepts for '{entity_text}'")
            
            # Process each concept
            for concept in concepts:
                # Add preferred label
                expanded_terms.append(ExpandedTerm(
                    term=concept.pref_label.lower(),
                    source='synonym',
                    weight=self.config['weights']['synonym'],
                    ontology=concept.ontology.value,
                    concept_id=concept.concept_id
                ))
                
                # Add synonyms
                if self.config['include_synonyms'] and concept.synonyms:
                    for synonym in concept.synonyms[:self.config['max_synonyms_per_entity']]:
                        expanded_terms.append(ExpandedTerm(
                            term=synonym.lower(),
                            source='synonym',
                            weight=self.config['weights']['synonym'],
                            ontology=concept.ontology.value,
                            concept_id=concept.concept_id
                        ))
                
                # Add codes
                if self.config['include_codes']:
                    expanded_terms.append(ExpandedTerm(
                        term=concept.concept_id,
                        source='code',
                        weight=self.config['weights']['code'],
                        ontology=concept.ontology.value,
                        concept_id=concept.concept_id
                    ))
        
        except Exception as e:
            logger.error(f"Error expanding entity '{entity_text}': {e}")
        
        return expanded_terms
    
    def _deduplicate_terms(self, terms: List[ExpandedTerm]) -> List[ExpandedTerm]:
        """
        Remove duplicate terms, keeping the one with highest weight
        
        Args:
            terms: List of expanded terms
        
        Returns:
            Deduplicated list
        """
        # Group by term (case-insensitive)
        term_map = {}
        
        for term in terms:
            key = term.term.lower()
            
            if key not in term_map or term.weight > term_map[key].weight:
                term_map[key] = term
        
        return list(term_map.values())
    
    def get_expansion_summary(self, expanded_query: ExpandedQuery) -> Dict[str, Any]:
        """
        Get summary of query expansion
        
        Args:
            expanded_query: Expanded query
        
        Returns:
            Summary dict
        """
        by_source = expanded_query.get_terms_by_source()
        
        return {
            'original_query': expanded_query.original_query,
            'total_terms': len(expanded_query.expanded_terms),
            'entities_detected': len(expanded_query.entities_detected),
            'terms_by_source': {
                source: len(terms) for source, terms in by_source.items()
            },
            'ontologies_used': list(set(
                term.ontology for term in expanded_query.expanded_terms 
                if term.ontology
            )),
            'sample_expansions': {
                source: terms[:3] for source, terms in by_source.items()
            }
        }
