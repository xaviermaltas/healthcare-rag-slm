"""
Medical Named Entity Recognition for Healthcare RAG system
Extracts medical entities from queries to enhance retrieval
"""

import re
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class MedicalEntity:
    """Represents a medical entity found in text"""
    text: str
    entity_type: str
    start_pos: int
    end_pos: int
    confidence: float = 1.0
    normalized_form: str = None
    codes: List[str] = None
    
    def __post_init__(self):
        if self.normalized_form is None:
            self.normalized_form = self.text.lower()
        if self.codes is None:
            self.codes = []


class MedicalNER:
    """Medical Named Entity Recognition for Spanish/Catalan medical texts"""
    
    def __init__(self):
        self._load_medical_dictionaries()
        self._compile_patterns()
    
    def _load_medical_dictionaries(self):
        """Load medical dictionaries and terminology"""
        
        # Common diseases in Spanish/Catalan
        self.diseases = {
            'diabetes', 'diabetis', 'hipertensión', 'hipertensió',
            'cáncer', 'càncer', 'tumor', 'infarto', 'ictus',
            'neumonía', 'pneumònia', 'asma', 'bronquitis',
            'artritis', 'artrosis', 'osteoporosis', 'fractura',
            'anemia', 'leucemia', 'hepatitis', 'cirrosis',
            'insuficiencia cardíaca', 'insuficiència cardíaca',
            'enfermedad renal', 'malaltia renal', 'nefropatía',
            'retinopatía', 'neuropatía', 'angina', 'arritmia'
        }
        
        # Symptoms in Spanish/Catalan
        self.symptoms = {
            'dolor', 'fiebre', 'febra', 'tos', 'fatiga',
            'mareo', 'mareig', 'náuseas', 'nàusees', 'vómito',
            'diarrea', 'estreñimiento', 'restrenyiment',
            'cefalea', 'cefalgia', 'disnea', 'taquicardia',
            'bradicardia', 'hipotensión', 'hipertensión',
            'edema', 'inflamación', 'inflamació', 'prurito',
            'erupción', 'erupció', 'sangrado', 'sagnat'
        }
        
        # Medications in Spanish/Catalan
        self.medications = {
            'paracetamol', 'ibuprofeno', 'aspirina', 'omeprazol',
            'metformina', 'insulina', 'enalapril', 'losartán',
            'atorvastatina', 'simvastatina', 'furosemida',
            'digoxina', 'warfarina', 'heparina', 'morfina',
            'tramadol', 'diazepam', 'lorazepam', 'fluoxetina',
            'sertralina', 'amoxicilina', 'ciprofloxacino'
        }
        
        # Body parts and anatomy
        self.anatomy = {
            'corazón', 'cor', 'pulmón', 'pulmó', 'hígado', 'fetge',
            'riñón', 'ronyó', 'cerebro', 'cervell', 'estómago', 'estómac',
            'intestino', 'páncreas', 'bazo', 'vesícula', 'vejiga',
            'próstata', 'útero', 'ovario', 'testículo', 'mama',
            'tiroides', 'suprarrenal', 'hueso', 'os', 'músculo',
            'piel', 'ojo', 'ull', 'oído', 'orella', 'nariz', 'nas'
        }
        
        # Medical procedures
        self.procedures = {
            'cirugía', 'cirurgia', 'operación', 'operació',
            'biopsia', 'endoscopia', 'colonoscopia', 'gastroscopia',
            'radiografía', 'radiografia', 'tomografía', 'resonancia',
            'ecografía', 'ecografia', 'electrocardiograma', 'análisis',
            'anàlisi', 'transfusión', 'transfusió', 'diálisis',
            'quimioterapia', 'quimioteràpia', 'radioterapia'
        }
        
        # Medical specialties
        self.specialties = {
            'cardiología', 'cardiologia', 'neurología', 'neurologia',
            'oncología', 'oncologia', 'pediatría', 'pediatria',
            'ginecología', 'ginecologia', 'urología', 'urologia',
            'dermatología', 'dermatologia', 'psiquiatría', 'psiquiatria',
            'endocrinología', 'endocrinologia', 'gastroenterología',
            'neumología', 'pneumologia', 'reumatología', 'reumatologia'
        }
    
    def _compile_patterns(self):
        """Compile regex patterns for entity recognition"""
        
        # Medical codes patterns
        self.code_patterns = [
            (r'\b[A-Z]\d{2}\.?\d*\b', 'ICD_CODE'),  # ICD codes
            (r'\b\d{6,8}\b', 'SNOMED_CODE'),        # SNOMED codes
            (r'\b[A-Z]{2,4}\d{1,4}\b', 'MEDICAL_CODE')  # Other codes
        ]
        
        # Dosage patterns
        self.dosage_patterns = [
            (r'\b\d+\s*mg\b', 'DOSAGE'),
            (r'\b\d+\s*ml\b', 'DOSAGE'),
            (r'\b\d+\s*g\b', 'DOSAGE'),
            (r'\b\d+\s*mcg\b', 'DOSAGE'),
            (r'\b\d+\s*UI\b', 'DOSAGE'),
            (r'\b\d+\s*comprimidos?\b', 'DOSAGE'),
            (r'\b\d+\s*pastillas?\b', 'DOSAGE')
        ]
        
        # Vital signs patterns
        self.vitals_patterns = [
            (r'\b\d{2,3}/\d{2,3}\s*mmHg\b', 'BLOOD_PRESSURE'),
            (r'\b\d{1,3}\s*bpm\b', 'HEART_RATE'),
            (r'\b\d{2,3}\.\d\s*°C\b', 'TEMPERATURE'),
            (r'\b\d{2,3}\s*kg\b', 'WEIGHT'),
            (r'\b\d{1,3}\s*cm\b', 'HEIGHT')
        ]
    
    def extract_entities(self, text: str) -> List[MedicalEntity]:
        """Extract medical entities from text"""
        entities = []
        text_lower = text.lower()
        
        # Extract diseases
        entities.extend(self._extract_from_dictionary(
            text, text_lower, self.diseases, 'DISEASE'
        ))
        
        # Extract symptoms
        entities.extend(self._extract_from_dictionary(
            text, text_lower, self.symptoms, 'SYMPTOM'
        ))
        
        # Extract medications
        entities.extend(self._extract_from_dictionary(
            text, text_lower, self.medications, 'MEDICATION'
        ))
        
        # Extract anatomy
        entities.extend(self._extract_from_dictionary(
            text, text_lower, self.anatomy, 'ANATOMY'
        ))
        
        # Extract procedures
        entities.extend(self._extract_from_dictionary(
            text, text_lower, self.procedures, 'PROCEDURE'
        ))
        
        # Extract specialties
        entities.extend(self._extract_from_dictionary(
            text, text_lower, self.specialties, 'SPECIALTY'
        ))
        
        # Extract codes using patterns
        entities.extend(self._extract_with_patterns(
            text, self.code_patterns
        ))
        
        # Extract dosages
        entities.extend(self._extract_with_patterns(
            text, self.dosage_patterns
        ))
        
        # Extract vital signs
        entities.extend(self._extract_with_patterns(
            text, self.vitals_patterns
        ))
        
        # Remove overlapping entities (keep longer ones)
        entities = self._remove_overlaps(entities)
        
        return sorted(entities, key=lambda x: x.start_pos)
    
    def _extract_from_dictionary(self, 
                                text: str, 
                                text_lower: str, 
                                dictionary: Set[str], 
                                entity_type: str) -> List[MedicalEntity]:
        """Extract entities using dictionary lookup"""
        entities = []
        
        for term in dictionary:
            term_lower = term.lower()
            start = 0
            
            while True:
                pos = text_lower.find(term_lower, start)
                if pos == -1:
                    break
                
                # Check word boundaries
                if (pos == 0 or not text_lower[pos-1].isalnum()) and \
                   (pos + len(term_lower) == len(text_lower) or 
                    not text_lower[pos + len(term_lower)].isalnum()):
                    
                    original_text = text[pos:pos + len(term_lower)]
                    entities.append(MedicalEntity(
                        text=original_text,
                        entity_type=entity_type,
                        start_pos=pos,
                        end_pos=pos + len(term_lower),
                        normalized_form=term_lower
                    ))
                
                start = pos + 1
        
        return entities
    
    def _extract_with_patterns(self, 
                              text: str, 
                              patterns: List[Tuple[str, str]]) -> List[MedicalEntity]:
        """Extract entities using regex patterns"""
        entities = []
        
        for pattern, entity_type in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                entities.append(MedicalEntity(
                    text=match.group(),
                    entity_type=entity_type,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    normalized_form=match.group().lower()
                ))
        
        return entities
    
    def _remove_overlaps(self, entities: List[MedicalEntity]) -> List[MedicalEntity]:
        """Remove overlapping entities, keeping longer ones"""
        if not entities:
            return entities
        
        # Sort by start position
        sorted_entities = sorted(entities, key=lambda x: x.start_pos)
        
        filtered = []
        for entity in sorted_entities:
            # Check if this entity overlaps with any in filtered list
            overlaps = False
            for existing in filtered:
                if (entity.start_pos < existing.end_pos and 
                    entity.end_pos > existing.start_pos):
                    # There's an overlap
                    if len(entity.text) > len(existing.text):
                        # Remove existing, add current
                        filtered.remove(existing)
                        break
                    else:
                        # Skip current entity
                        overlaps = True
                        break
            
            if not overlaps:
                filtered.append(entity)
        
        return filtered
    
    def get_entity_summary(self, entities: List[MedicalEntity]) -> Dict[str, List[str]]:
        """Get summary of extracted entities by type"""
        summary = {}
        
        for entity in entities:
            if entity.entity_type not in summary:
                summary[entity.entity_type] = []
            
            if entity.normalized_form not in summary[entity.entity_type]:
                summary[entity.entity_type].append(entity.normalized_form)
        
        return summary
    
    def expand_medical_terms(self, entities: List[MedicalEntity]) -> List[str]:
        """Expand medical terms with synonyms and related terms"""
        expanded_terms = []
        
        # Synonym mappings
        synonyms = {
            'diabetes': ['diabetes mellitus', 'diabetis', 'hiperglucemia'],
            'hipertensión': ['hipertensió', 'presión alta', 'tensión alta'],
            'infarto': ['infarto de miocardio', 'ataque cardíaco', 'IM'],
            'ictus': ['accidente cerebrovascular', 'ACV', 'derrame cerebral'],
            'cáncer': ['càncer', 'tumor maligno', 'neoplasia'],
            'dolor': ['algesia', 'molestia', 'malestar']
        }
        
        for entity in entities:
            expanded_terms.append(entity.normalized_form)
            
            # Add synonyms if available
            if entity.normalized_form in synonyms:
                expanded_terms.extend(synonyms[entity.normalized_form])
        
        return list(set(expanded_terms))  # Remove duplicates
