"""
Medical Coding Service
Maps diagnoses and medications to SNOMED CT, ICD-10, and ATC codes
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from functools import lru_cache

from src.main.infrastructure.ontologies.snomed_client import SNOMEDClient, SNOMEDConcept
from src.main.infrastructure.ontologies.ontology_manager import OntologyManager
from src.main.core.coding.medical_translator import MedicalTranslator

logger = logging.getLogger(__name__)


@dataclass
class MedicalCode:
    """Represents a medical code with metadata"""
    code: str
    system: str  # SNOMED_CT, ICD10, ATC
    display: str
    confidence: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'code': self.code,
            'system': self.system,
            'display': self.display,
            'confidence': self.confidence
        }


@dataclass
class DiagnosisCoding:
    """Coding result for a diagnosis"""
    diagnosis_text: str
    snomed_code: Optional[MedicalCode] = None
    icd10_code: Optional[MedicalCode] = None
    
    def to_dict(self) -> Dict:
        return {
            'diagnosis': self.diagnosis_text,
            'snomed': self.snomed_code.to_dict() if self.snomed_code else None,
            'icd10': self.icd10_code.to_dict() if self.icd10_code else None
        }


@dataclass
class MedicationCoding:
    """Coding result for a medication"""
    medication_text: str
    atc_code: Optional[MedicalCode] = None
    snomed_code: Optional[MedicalCode] = None
    
    def to_dict(self) -> Dict:
        return {
            'medication': self.medication_text,
            'atc': self.atc_code.to_dict() if self.atc_code else None,
            'snomed': self.snomed_code.to_dict() if self.snomed_code else None
        }


class MedicalCodingService:
    """
    Service for automatic medical coding
    Maps clinical text to standardized medical codes
    """
    
    def __init__(self, 
                 snomed_client: Optional[SNOMEDClient] = None,
                 ontology_manager: Optional[OntologyManager] = None):
        """
        Initialize medical coding service
        
        Args:
            snomed_client: SNOMED CT client
            ontology_manager: Ontology manager for multiple ontologies
        """
        self.snomed_client = snomed_client
        self.ontology_manager = ontology_manager
        self._cache = {}
        
    async def code_diagnosis(self, 
                            diagnosis_text: str,
                            min_confidence: float = 0.6) -> DiagnosisCoding:
        """
        Code a diagnosis with SNOMED CT and ICD-10
        
        Args:
            diagnosis_text: Diagnosis description
            min_confidence: Minimum confidence threshold
            
        Returns:
            DiagnosisCoding with SNOMED and ICD-10 codes
        """
        # Check cache
        cache_key = f"diag_{diagnosis_text.lower()}"
        if cache_key in self._cache:
            logger.debug(f"Cache hit for diagnosis: {diagnosis_text}")
            return self._cache[cache_key]
        
        result = DiagnosisCoding(diagnosis_text=diagnosis_text)
        
        # Get SNOMED CT code
        if self.snomed_client:
            try:
                snomed_code = await self._get_snomed_for_diagnosis(
                    diagnosis_text, 
                    min_confidence
                )
                result.snomed_code = snomed_code
            except Exception as e:
                logger.warning(f"SNOMED coding failed for '{diagnosis_text}': {e}")
        
        # Get ICD-10 code
        if self.ontology_manager:
            try:
                icd10_code = await self._get_icd10_for_diagnosis(
                    diagnosis_text,
                    min_confidence
                )
                result.icd10_code = icd10_code
            except Exception as e:
                logger.warning(f"ICD-10 coding failed for '{diagnosis_text}': {e}")
        
        # Cache result
        self._cache[cache_key] = result
        return result
    
    async def code_medication(self,
                             medication_text: str,
                             min_confidence: float = 0.6) -> MedicationCoding:
        """
        Code a medication with ATC and SNOMED CT
        
        Args:
            medication_text: Medication name/description
            min_confidence: Minimum confidence threshold
            
        Returns:
            MedicationCoding with ATC and SNOMED codes
        """
        # Check cache
        cache_key = f"med_{medication_text.lower()}"
        if cache_key in self._cache:
            logger.debug(f"Cache hit for medication: {medication_text}")
            return self._cache[cache_key]
        
        result = MedicationCoding(medication_text=medication_text)
        
        # Get ATC code
        if self.ontology_manager:
            try:
                atc_code = await self._get_atc_for_medication(
                    medication_text,
                    min_confidence
                )
                result.atc_code = atc_code
            except Exception as e:
                logger.warning(f"ATC coding failed for '{medication_text}': {e}")
        
        # Get SNOMED CT code for medication
        if self.snomed_client:
            try:
                snomed_code = await self._get_snomed_for_medication(
                    medication_text,
                    min_confidence
                )
                result.snomed_code = snomed_code
            except Exception as e:
                logger.warning(f"SNOMED coding failed for '{medication_text}': {e}")
        
        # Cache result
        self._cache[cache_key] = result
        return result
    
    async def code_diagnoses_batch(self,
                                  diagnoses: List[str],
                                  min_confidence: float = 0.6) -> List[DiagnosisCoding]:
        """
        Code multiple diagnoses in batch
        
        Args:
            diagnoses: List of diagnosis descriptions
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of DiagnosisCoding results
        """
        tasks = [
            self.code_diagnosis(diag, min_confidence) 
            for diag in diagnoses
        ]
        return await asyncio.gather(*tasks)
    
    async def code_medications_batch(self,
                                    medications: List[str],
                                    min_confidence: float = 0.6) -> List[MedicationCoding]:
        """
        Code multiple medications in batch
        
        Args:
            medications: List of medication names
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of MedicationCoding results
        """
        tasks = [
            self.code_medication(med, min_confidence)
            for med in medications
        ]
        return await asyncio.gather(*tasks)
    
    # ========================================================================
    # Private helper methods
    # ========================================================================
    
    async def _get_snomed_for_diagnosis(self,
                                       diagnosis_text: str,
                                       min_confidence: float) -> Optional[MedicalCode]:
        """Get SNOMED CT code for diagnosis"""
        if not self.snomed_client:
            return None
        
        # Get search variants (original + translated + simplified)
        search_variants = MedicalTranslator.get_search_variants(diagnosis_text)
        logger.debug(f"Search variants for '{diagnosis_text}': {search_variants}")
        
        # Try each variant until we find a good match
        for variant in search_variants:
            # Search SNOMED CT for diagnosis
            # Note: semantic_types filter removed because SNOMED returns UMLS codes (T047, etc.)
            # instead of text labels. BioPortal search already prioritizes relevant concepts.
            concepts = await self.snomed_client.search_concepts(
                query=variant,
                limit=5
            )
            
            if not concepts:
                logger.debug(f"No SNOMED concepts found for variant: {variant}")
                continue
            
            # Get best match
            best_concept = concepts[0]
            
            # Calculate confidence based on text similarity with ORIGINAL term
            confidence = self._calculate_text_similarity(
                diagnosis_text.lower(),
                best_concept.pref_label.lower()
            )
            
            # Also check similarity with translated term
            if variant != diagnosis_text:
                translated_confidence = self._calculate_text_similarity(
                    variant.lower(),
                    best_concept.pref_label.lower()
                )
                # Use the higher confidence
                confidence = max(confidence, translated_confidence)
            
            if confidence >= min_confidence:
                logger.info(f"SNOMED match for '{diagnosis_text}' via '{variant}': {best_concept.concept_id}")
                return MedicalCode(
                    code=best_concept.concept_id,
                    system='SNOMED_CT',
                    display=best_concept.pref_label,
                    confidence=confidence
                )
            else:
                logger.debug(f"Low confidence ({confidence:.2f}) for variant: {variant}")
        
        logger.debug(f"No SNOMED code found for: {diagnosis_text}")
        return None
    
    async def _get_icd10_for_diagnosis(self,
                                      diagnosis_text: str,
                                      min_confidence: float) -> Optional[MedicalCode]:
        """Get ICD-10 code for diagnosis"""
        if not self.ontology_manager:
            return None
        
        # Get search variants (original + translated + simplified)
        search_variants = MedicalTranslator.get_search_variants(diagnosis_text)
        
        # Try each variant until we find a good match
        from src.main.infrastructure.ontologies.ontology_manager import OntologyType
        for variant in search_variants:
            # Search ICD-10
            concepts = await self.ontology_manager.search_concepts(
                query=variant,
                ontologies=[OntologyType.ICD10],
                limit=5
            )
            
            if not concepts:
                logger.debug(f"No ICD-10 concepts found for variant: {variant}")
                continue
            
            # Get best match
            best_concept = concepts[0]
            
            # Calculate confidence with ORIGINAL term
            confidence = self._calculate_text_similarity(
                diagnosis_text.lower(),
                best_concept.pref_label.lower()
            )
            
            # Also check similarity with translated term
            if variant != diagnosis_text:
                translated_confidence = self._calculate_text_similarity(
                    variant.lower(),
                    best_concept.pref_label.lower()
                )
                confidence = max(confidence, translated_confidence)
            
            if confidence >= min_confidence:
                # Extract ICD-10 code from concept ID
                # concept_id format: "http://purl.bioontology.org/ontology/ICD10CM/I21.0"
                icd10_code = best_concept.concept_id.split('/')[-1]
                
                logger.info(f"ICD-10 match for '{diagnosis_text}' via '{variant}': {icd10_code}")
                return MedicalCode(
                    code=icd10_code,
                    system='ICD10',
                    display=best_concept.pref_label,
                    confidence=confidence
                )
            else:
                logger.debug(f"Low confidence ({confidence:.2f}) for variant: {variant}")
        
        logger.debug(f"No ICD-10 code found for: {diagnosis_text}")
        return None
    
    async def _get_atc_for_medication(self,
                                     medication_text: str,
                                     min_confidence: float) -> Optional[MedicalCode]:
        """Get ATC code for medication"""
        if not self.ontology_manager:
            return None
        
        # Search ATC (Anatomical Therapeutic Chemical Classification)
        # Note: BioPortal might not have ATC, this is a placeholder
        # In production, you'd use a dedicated ATC database
        
        # For now, return None - ATC requires specific database
        logger.debug(f"ATC coding not yet implemented for: {medication_text}")
        return None
    
    async def _get_snomed_for_medication(self,
                                        medication_text: str,
                                        min_confidence: float) -> Optional[MedicalCode]:
        """Get SNOMED CT code for medication"""
        if not self.snomed_client:
            return None
        
        # Get search variants (original + translated + simplified)
        search_variants = MedicalTranslator.get_search_variants(medication_text)
        
        # Try each variant until we find a good match
        for variant in search_variants:
            # Search SNOMED CT for medication
            # Note: semantic_types filter removed (see _get_snomed_for_diagnosis)
            concepts = await self.snomed_client.search_concepts(
                query=variant,
                limit=5
            )
            
            if not concepts:
                logger.debug(f"No SNOMED concepts found for variant: {variant}")
                continue
            
            # Get best match
            best_concept = concepts[0]
            
            # Calculate confidence with ORIGINAL term
            confidence = self._calculate_text_similarity(
                medication_text.lower(),
                best_concept.pref_label.lower()
            )
            
            # Also check similarity with translated term
            if variant != medication_text:
                translated_confidence = self._calculate_text_similarity(
                    variant.lower(),
                    best_concept.pref_label.lower()
                )
                confidence = max(confidence, translated_confidence)
            
            if confidence >= min_confidence:
                logger.info(f"SNOMED match for '{medication_text}' via '{variant}': {best_concept.concept_id}")
                return MedicalCode(
                    code=best_concept.concept_id,
                    system='SNOMED_CT',
                    display=best_concept.pref_label,
                    confidence=confidence
                )
            else:
                logger.debug(f"Low confidence ({confidence:.2f}) for variant: {variant}")
        
        logger.debug(f"No SNOMED code found for: {medication_text}")
        return None
    
    @staticmethod
    def _calculate_text_similarity(text1: str, text2: str) -> float:
        """
        Calculate text similarity with special handling for medical terms
        Uses Jaccard similarity on word sets with boost for exact substring matches
        """
        # Normalize: lowercase and remove punctuation
        import re
        text1_norm = re.sub(r'[^\w\s]', ' ', text1.lower())
        text2_norm = re.sub(r'[^\w\s]', ' ', text2.lower())
        
        words1 = set(text1_norm.split())
        words2 = set(text2_norm.split())
        
        if not words1 or not words2:
            return 0.0
        
        # Standard Jaccard similarity
        intersection = words1 & words2
        union = words1 | words2
        jaccard = len(intersection) / len(union)
        
        # Boost for exact substring match (e.g., "metformin" in "Metformin-containing product")
        # This helps with medication names that appear in compound terms
        # Check if the main term appears as a word in the longer text
        for word1 in words1:
            if len(word1) > 3:  # Only check meaningful words
                for word2 in words2:
                    if word1 in word2 or word2 in word1:
                        if len(word1) >= 5 or len(word2) >= 5:  # Significant overlap
                            substring_boost = 0.4
                            return min(1.0, jaccard + substring_boost)
        
        return jaccard
    
    def clear_cache(self):
        """Clear the coding cache"""
        self._cache.clear()
        logger.info("Medical coding cache cleared")
