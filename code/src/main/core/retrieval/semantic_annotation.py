"""
Semantic Annotation Service
Maps medical text to SNOMED CT codes using MedicalNER + SNOMED Client
"""

from typing import List, Dict, Any, Optional
import logging
from dataclasses import dataclass

from src.main.core.retrieval.query_processing.medical_ner import MedicalNER, MedicalEntity
from src.main.infrastructure.ontologies.snomed_client import SNOMEDClient, SNOMEDConcept

logger = logging.getLogger(__name__)


@dataclass
class SemanticAnnotation:
    """Represents a semantic annotation (text + SNOMED code)"""
    text: str
    entity_type: str
    start_pos: int
    end_pos: int
    snomed_concept_id: str
    snomed_label: str
    snomed_definition: str = ""
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'text': self.text,
            'entity_type': self.entity_type,
            'position': {'start': self.start_pos, 'end': self.end_pos},
            'snomed': {
                'concept_id': self.snomed_concept_id,
                'label': self.snomed_label,
                'definition': self.snomed_definition
            },
            'confidence': self.confidence
        }


class SemanticAnnotationService:
    """Service for annotating medical text with SNOMED CT codes"""
    
    def __init__(self, snomed_client: SNOMEDClient):
        """
        Initialize semantic annotation service
        
        Args:
            snomed_client: Initialized SNOMED CT client
        """
        self.snomed_client = snomed_client
        self.medical_ner = MedicalNER()
        
        # Map entity types to SNOMED semantic types
        self.entity_to_semantic_type = {
            'DISEASE': ['Disease or Syndrome', 'Finding'],
            'SYMPTOM': ['Sign or Symptom', 'Finding'],
            'MEDICATION': ['Pharmacologic Substance', 'Clinical Drug'],
            'PROCEDURE': ['Therapeutic or Preventive Procedure', 'Diagnostic Procedure'],
            'ANATOMY': ['Body Part, Organ, or Organ Component', 'Body Location or Region'],
            'SPECIALTY': ['Biomedical Occupation or Discipline']
        }
    
    async def annotate_text(self, 
                           text: str, 
                           min_confidence: float = 0.5) -> List[SemanticAnnotation]:
        """
        Annotate medical text with SNOMED CT codes
        
        Args:
            text: Medical text to annotate
            min_confidence: Minimum confidence threshold for annotations
            
        Returns:
            List of semantic annotations
        """
        # Step 1: Extract medical entities using NER
        entities = self.medical_ner.extract_entities(text)
        logger.info(f"Extracted {len(entities)} medical entities from text")
        
        # Step 2: Map each entity to SNOMED CT concepts
        annotations = []
        for entity in entities:
            annotation = await self._map_entity_to_snomed(entity)
            
            if annotation and annotation.confidence >= min_confidence:
                annotations.append(annotation)
        
        logger.info(f"Created {len(annotations)} semantic annotations (min_confidence={min_confidence})")
        return annotations
    
    async def _map_entity_to_snomed(self, entity: MedicalEntity) -> Optional[SemanticAnnotation]:
        """Map a single medical entity to SNOMED CT concept"""
        try:
            # Get semantic types for this entity type
            semantic_types = self.entity_to_semantic_type.get(entity.entity_type)
            
            # Search SNOMED CT for this entity
            concepts = await self.snomed_client.search_concepts(
                query=entity.text,
                limit=3,
                semantic_types=semantic_types
            )
            
            if not concepts:
                logger.debug(f"No SNOMED concept found for entity: {entity.text}")
                return None
            
            # Take the best match
            best_concept = concepts[0]
            
            # Calculate confidence based on text similarity
            confidence = self._calculate_confidence(entity.text, best_concept)
            
            return SemanticAnnotation(
                text=entity.text,
                entity_type=entity.entity_type,
                start_pos=entity.start_pos,
                end_pos=entity.end_pos,
                snomed_concept_id=best_concept.concept_id,
                snomed_label=best_concept.pref_label,
                snomed_definition=best_concept.definition,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Error mapping entity to SNOMED: {e}")
            return None
    
    def _calculate_confidence(self, entity_text: str, concept: SNOMEDConcept) -> float:
        """Calculate confidence score for entity-concept mapping"""
        entity_lower = entity_text.lower()
        label_lower = concept.pref_label.lower()
        
        # Exact match
        if entity_lower == label_lower:
            return 1.0
        
        # Substring match
        if entity_lower in label_lower or label_lower in entity_lower:
            return 0.9
        
        # Synonym match
        for synonym in concept.synonyms:
            synonym_lower = synonym.lower()
            if entity_lower == synonym_lower:
                return 0.95
            if entity_lower in synonym_lower or synonym_lower in entity_lower:
                return 0.85
        
        # Word overlap
        entity_words = set(entity_lower.split())
        label_words = set(label_lower.split())
        overlap = len(entity_words & label_words)
        
        if overlap > 0:
            jaccard = overlap / len(entity_words | label_words)
            return 0.6 + (jaccard * 0.3)
        
        return 0.5  # Default medium confidence
    
    async def get_expanded_query_terms(self, 
                                      text: str, 
                                      include_synonyms: bool = True,
                                      include_parents: bool = False) -> List[str]:
        """
        Expand query with SNOMED CT synonyms and related terms
        
        Args:
            text: Original query text
            include_synonyms: Include SNOMED synonyms
            include_parents: Include parent concepts (broader terms)
            
        Returns:
            List of expanded query terms
        """
        expanded_terms = [text]
        
        # Annotate text to get SNOMED concepts
        annotations = await self.annotate_text(text, min_confidence=0.6)
        
        for annotation in annotations:
            # Add SNOMED preferred label
            if annotation.snomed_label.lower() not in [t.lower() for t in expanded_terms]:
                expanded_terms.append(annotation.snomed_label)
            
            # Get full concept details
            concept = await self.snomed_client.get_concept_by_id(annotation.snomed_concept_id)
            
            if concept:
                # Add synonyms
                if include_synonyms:
                    for synonym in concept.synonyms:
                        if synonym.lower() not in [t.lower() for t in expanded_terms]:
                            expanded_terms.append(synonym)
                
                # Add parent concepts (broader terms)
                if include_parents:
                    hierarchy = await self.snomed_client.get_hierarchy(concept.concept_id)
                    for parent in hierarchy.get('parents', []):
                        if parent.lower() not in [t.lower() for t in expanded_terms]:
                            expanded_terms.append(parent)
        
        logger.info(f"Expanded query from 1 term to {len(expanded_terms)} terms")
        return expanded_terms
    
    def get_annotation_summary(self, annotations: List[SemanticAnnotation]) -> Dict[str, Any]:
        """Get summary statistics of annotations"""
        if not annotations:
            return {
                'total_annotations': 0,
                'by_entity_type': {},
                'avg_confidence': 0.0,
                'snomed_concepts': []
            }
        
        by_type = {}
        for ann in annotations:
            if ann.entity_type not in by_type:
                by_type[ann.entity_type] = 0
            by_type[ann.entity_type] += 1
        
        return {
            'total_annotations': len(annotations),
            'by_entity_type': by_type,
            'avg_confidence': sum(a.confidence for a in annotations) / len(annotations),
            'snomed_concepts': [
                {
                    'id': ann.snomed_concept_id,
                    'label': ann.snomed_label,
                    'type': ann.entity_type
                }
                for ann in annotations
            ]
        }
