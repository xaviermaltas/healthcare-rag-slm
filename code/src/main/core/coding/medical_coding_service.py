"""
Medical Coding Service
NOVA ARQUITECTURA: Semantic retrieval + minimal fallback
Substitueix diccionaris estàtics per retrieval intel·ligent a Qdrant
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from functools import lru_cache

# Legacy imports (mantenir compatibilitat)
from src.main.infrastructure.ontologies.snomed_client import SNOMEDClient, SNOMEDConcept
from src.main.infrastructure.ontologies.ontology_manager import OntologyManager
# MedicalTranslator ELIMINAT - anti-pattern refactoritzat

# Nova arquitectura semàntica
from src.main.core.coding.semantic_coding_service import SemanticCodingService, CodingPipeline
from src.main.core.coding.semantic_coding_service import MedicalCode as SemanticMedicalCode

logger = logging.getLogger(__name__)


@dataclass
class MedicalCode:
    """Legacy MedicalCode class - mantenir compatibilitat"""
    code: str
    system: str  # SNOMED_CT, ICD10, ATC
    display: str
    confidence: float = 0.0
    source: str = "legacy"  # Nou camp per tracking
    
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
    NOVA ARQUITECTURA: Semantic Medical Coding Service
    Usa retrieval semàntic + fallback mínim en lloc de diccionaris estàtics
    """
    
    def __init__(self, 
                 qdrant_client=None,
                 embeddings_model=None,
                 ner_service=None,
                 # Legacy compatibility
                 snomed_client: Optional[SNOMEDClient] = None,
                 ontology_manager: Optional[OntologyManager] = None):
        """
        Initialize medical coding service amb nova arquitectura
        
        Args:
            qdrant_client: Client Qdrant per retrieval semàntic
            embeddings_model: Model d'embeddings (BGE-M3)
            ner_service: Servei NER per extracció d'entitats
            snomed_client: Legacy SNOMED CT client (compatibility)
            ontology_manager: Legacy ontology manager (compatibility)
        """
        # Nova arquitectura semàntica
        if qdrant_client:
            self.semantic_coding = SemanticCodingService(qdrant_client, embeddings_model, snomed_client)
            if ner_service:
                self.coding_pipeline = CodingPipeline(ner_service, self.semantic_coding)
            else:
                self.coding_pipeline = None
        else:
            self.semantic_coding = None
            self.coding_pipeline = None
        
        # Legacy compatibility
        self.snomed_client = snomed_client
        self.ontology_manager = ontology_manager
        self._cache = {}
        
        # Log arquitectura utilitzada
        if self.semantic_coding:
            logger.info("✅ Using NEW semantic coding architecture")
        else:
            logger.warning("⚠️ Using LEGACY dictionary-based architecture")
    
    # ========== NOVA ARQUITECTURA SEMÀNTICA ==========
    
    async def code_clinical_text_semantic(self, clinical_text: str) -> Dict:
        """
        NOVA ARQUITECTURA: Codifica text clínic complet amb pipeline semàntic
        
        Args:
            clinical_text: Text clínic generat pel LLM
            
        Returns:
            Dict amb entitats i codis mèdics
        """
        if not self.coding_pipeline:
            logger.error("Semantic coding pipeline not available")
            return await self._fallback_to_legacy(clinical_text)
        
        try:
            result = await self.coding_pipeline.process_clinical_text(clinical_text)
            logger.info(f"Semantic coding completed: {result['summary']}")
            return result
            
        except Exception as e:
            logger.error(f"Semantic coding failed: {e}")
            return await self._fallback_to_legacy(clinical_text)
    
    async def get_snomed_code_semantic(self, term: str) -> Optional[MedicalCode]:
        """
        NOVA ARQUITECTURA: Obté codi SNOMED via retrieval semàntic
        
        Args:
            term: Terme mèdic
            
        Returns:
            MedicalCode o None
        """
        if not self.semantic_coding:
            return await self._get_snomed_for_diagnosis_legacy(term, 0.6)
        
        try:
            semantic_code = await self.semantic_coding.get_snomed_code(term)
            if semantic_code:
                # Convertir SemanticMedicalCode a MedicalCode legacy
                return MedicalCode(
                    code=semantic_code.code,
                    system=semantic_code.system,
                    display=semantic_code.display,
                    confidence=semantic_code.confidence,
                    source=semantic_code.source
                )
            return None
            
        except Exception as e:
            logger.error(f"Semantic SNOMED search failed: {e}")
            return await self._get_snomed_for_diagnosis_legacy(term, 0.6)
    
    async def get_icd10_code_semantic(self, term: str) -> Optional[MedicalCode]:
        """
        NOVA ARQUITECTURA: Obté codi ICD-10 via retrieval semàntic
        """
        if not self.semantic_coding:
            return self._get_icd10_code_legacy(term)
        
        try:
            semantic_code = await self.semantic_coding.get_icd10_code(term)
            if semantic_code:
                return MedicalCode(
                    code=semantic_code.code,
                    system=semantic_code.system,
                    display=semantic_code.display,
                    confidence=semantic_code.confidence,
                    source=semantic_code.source
                )
            return None
            
        except Exception as e:
            logger.error(f"Semantic ICD-10 search failed: {e}")
            return self._get_icd10_code_legacy(term)
    
    async def get_atc_code_semantic(self, medication: str) -> Optional[MedicalCode]:
        """
        NOVA ARQUITECTURA: Obté codi ATC via retrieval semàntic
        """
        if not self.semantic_coding:
            return self._get_atc_code_legacy(medication)
        
        try:
            semantic_code = await self.semantic_coding.get_atc_code(medication)
            if semantic_code:
                return MedicalCode(
                    code=semantic_code.code,
                    system=semantic_code.system,
                    display=semantic_code.display,
                    confidence=semantic_code.confidence,
                    source=semantic_code.source
                )
            return None
            
        except Exception as e:
            logger.error(f"Semantic ATC search failed: {e}")
            return self._get_atc_code_legacy(medication)
    
    async def _fallback_to_legacy(self, clinical_text: str) -> Dict:
        """Fallback a arquitectura legacy quan semàntica falla"""
        logger.warning("Falling back to legacy coding architecture")
        
        # Simulació de resultat legacy
        return {
            'entities': {'DISEASE': [], 'MEDICATION': [], 'PROCEDURE': []},
            'codes': {'diagnoses': [], 'medications': [], 'procedures': []},
            'summary': {
                'total_entities': 0,
                'total_codes': 0,
                'coding_rate': 0.0,
                'source': 'legacy_fallback'
            }
        }
    
    # ========== MÈTODES LEGACY (compatibilitat) ==========
        
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
                snomed_code = await self._get_snomed_for_diagnosis_legacy(
                    diagnosis_text, 
                    min_confidence
                )
                result.snomed_code = snomed_code
            except Exception as e:
                logger.warning(f"SNOMED coding failed for '{diagnosis_text}': {e}")
        
        # Get ICD-10 code
        if self.ontology_manager:
            try:
                icd10_code = await self._get_icd10_for_diagnosis_legacy(
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
                atc_code = await self._get_atc_for_medication_legacy(
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
    
    async def _get_snomed_for_diagnosis_legacy(self,
                                      diagnosis_text: str,
                                      min_confidence: float) -> Optional[MedicalCode]:
        """
        🔄 REFACTORED: Legacy method now uses SEMANTIC architecture
        Eliminat anti-pattern MedicalTranslator
        """
        # 1. Try SEMANTIC retrieval first (NEW ARCHITECTURE)
        if self.semantic_coding:
            semantic_result = await self.semantic_coding.get_snomed_code(diagnosis_text)
            if semantic_result and semantic_result.confidence >= min_confidence:
                logger.info(f"✅ SNOMED semantic hit for '{diagnosis_text}': {semantic_result.code}")
                return MedicalCode(
                    code=semantic_result.code,
                    system=semantic_result.system,
                    display=semantic_result.display,
                    confidence=semantic_result.confidence,
                    source=semantic_result.source
                )

        # 2. Fallback to BioPortal API if available
        if not self.snomed_client:
            logger.warning(f"No SNOMED client available for: {diagnosis_text}")
            return None

        # 3. Generate search variants (without MedicalTranslator)
        search_variants = self._generate_search_variants(diagnosis_text)
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
    
    async def _get_icd10_for_diagnosis_legacy(self,
                                     diagnosis_text: str,
                                     min_confidence: float) -> Optional[MedicalCode]:
        """
        🔄 REFACTORED: Legacy method now uses SEMANTIC architecture
        Eliminat anti-pattern MedicalTranslator
        """
        
        # 1. Try SEMANTIC retrieval first (NEW ARCHITECTURE)
        if self.semantic_coding:
            semantic_result = await self.semantic_coding.get_icd10_code(diagnosis_text)
            if semantic_result and semantic_result.confidence >= min_confidence:
                logger.info(f"✅ ICD-10 semantic hit for '{diagnosis_text}': {semantic_result.code}")
                return MedicalCode(
                    code=semantic_result.code,
                    system=semantic_result.system,
                    display=semantic_result.display,
                    confidence=semantic_result.confidence,
                    source=semantic_result.source
                )

        # 2. Fallback to BioPortal API if available
        if not self.ontology_manager:
            logger.warning(f"No ontology manager available for ICD-10: {diagnosis_text}")
            return None
        
        # 3. Generate search variants (without MedicalTranslator)
        search_variants = self._generate_search_variants(diagnosis_text)
        
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
    
    async def _get_atc_for_medication_legacy(self,
                                    medication_text: str,
                                    min_confidence: float) -> Optional[MedicalCode]:
        """
        🔄 REFACTORED: Legacy method now uses SEMANTIC architecture
        Eliminat anti-pattern MedicalTranslator
        """

        # 1. Try SEMANTIC retrieval first (NEW ARCHITECTURE)
        if self.semantic_coding:
            semantic_result = await self.semantic_coding.get_atc_code(medication_text)
            if semantic_result and semantic_result.confidence >= min_confidence:
                logger.info(f"✅ ATC semantic hit for '{medication_text}': {semantic_result.code}")
                return MedicalCode(
                    code=semantic_result.code,
                    system=semantic_result.system,
                    display=semantic_result.display,
                    confidence=semantic_result.confidence,
                    source=semantic_result.source
                )
        
        logger.debug(f"No semantic ATC match for: {medication_text}")
        
        # 2. Fallback to BioPortal API if available
        if not self.ontology_manager:
            logger.warning(f"No ontology manager available for ATC: {medication_text}")
            return None
        
        # 3. Generate search variants (without MedicalTranslator)
        search_variants = self._generate_search_variants(medication_text)
        
        from src.main.infrastructure.ontologies.ontology_manager import OntologyType
        for variant in search_variants:
            # Search ATC
            concepts = await self.ontology_manager.search_concepts(
                query=variant,
                ontologies=[OntologyType.ATC],
                limit=5
            )
            
            if not concepts:
                logger.debug(f"No ATC concepts found for variant: {variant}")
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
                # Extract ATC code from concept ID
                # concept_id format: "http://purl.bioontology.org/ontology/ATC/A10BA02"
                atc_code = best_concept.concept_id.split('/')[-1]
                
                logger.info(f"ATC match for '{medication_text}' via '{variant}': {atc_code}")
                return MedicalCode(
                    code=atc_code,
                    system='ATC',
                    display=best_concept.pref_label,
                    confidence=confidence
                )
            else:
                logger.debug(f"Low confidence ({confidence:.2f}) for variant: {variant}")
        
        logger.debug(f"No ATC code found for: {medication_text}")
        return None
    
    def _generate_search_variants(self, term: str) -> list[str]:
        """
        🆕 NEW: Generate search variants using semantic approach
        Implements search variant generation without anti-pattern dependencies
        """
        variants = []
        
        # Original term
        variants.append(term)
        
        # Basic translation (simplified)
        translated = self._basic_translate_to_english(term)
        if translated.lower() != term.lower():
            variants.append(translated)
        
        # Simplified versions (remove common words)
        simplified = self._simplify_term(term)
        if simplified not in variants:
            variants.append(simplified)
        
        return variants
    
    def _basic_translate_to_english(self, term: str) -> str:
        """Basic medical translation without MedicalTranslator dependency"""
        # Minimal translation dictionary for common terms
        basic_translations = {
            'diabetis': 'diabetes',
            'hipertensió': 'hypertension',
            'infart': 'infarction',
            'pneumònia': 'pneumonia',
            'asma': 'asthma',
            'metformina': 'metformin',
            'enalapril': 'enalapril',
            'atorvastatina': 'atorvastatin',
            'omeprazol': 'omeprazole',
            'paracetamol': 'paracetamol'
        }
        
        normalized = term.lower().strip()
        return basic_translations.get(normalized, term)
    
    def _simplify_term(self, term: str) -> str:
        """Simplify medical term by removing common words"""
        # Remove common medical words that don't add semantic value
        stop_words = [
            'agut', 'aguda', 'acute', 'crònic', 'cronica', 'chronic',
            'tipus', 'tipo', 'type', 'de', 'del', 'de la', 'amb', 'con', 'with'
        ]
        
        words = term.lower().split()
        filtered_words = [w for w in words if w not in stop_words]
        
        return ' '.join(filtered_words) if filtered_words else term
    
    async def _get_snomed_for_medication(self,
                                        medication_text: str,
                                        min_confidence: float) -> Optional[MedicalCode]:
        """Get SNOMED CT code for medication"""
        if not self.snomed_client:
            return None
        
        # Get search variants (original + translated + simplified)
        search_variants = self._generate_search_variants(medication_text)
        
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
