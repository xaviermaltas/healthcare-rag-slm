"""
Semantic Medical Coding Service
Servei de codificació mèdica basat en retrieval semàntic
Substitueix diccionaris estàtics per cerca intel·ligent a Qdrant
"""

import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from src.main.core.ontology.ontology_indexer import OntologyRetriever

logger = logging.getLogger(__name__)


@dataclass
class MedicalCode:
    """Codi mèdic amb metadata"""
    code: str
    system: str  # SNOMED_CT, ICD10, ATC
    display: str
    confidence: float
    source: str  # semantic_retrieval, fallback_dict, api


class SemanticCodingService:
    """
    Servei de codificació mèdica amb retrieval semàntic
    Arquitectura: NER → Semantic Retrieval → Fallback → API
    """
    
    def __init__(self, qdrant_client, embeddings_model=None, bioportal_client=None):
        """
        Args:
            qdrant_client: Client Qdrant per retrieval semàntic
            embeddings_model: Model d'embeddings (BGE-M3) per generar query vectors
            bioportal_client: Client BioPortal com a fallback final
        """
        self.ontology_retriever = OntologyRetriever(qdrant_client, embeddings_model)
        self.bioportal_client = bioportal_client
        self.min_confidence = 0.7  # Threshold mínim per acceptar resultats
    
    async def get_snomed_code(self, term: str) -> Optional[MedicalCode]:
        """
        Obté codi SNOMED CT per un terme mèdic
        
        Args:
            term: Terme mèdic (diagnòstic, símptoma, procediment)
            
        Returns:
            MedicalCode amb SNOMED CT o None
        """
        # 1. Retrieval semàntic (prioritat màxima)
        semantic_results = await self.ontology_retriever.search_snomed(term, limit=3)
        if semantic_results:
            best_result = semantic_results[0]
            if best_result.get('score', 0) >= self.min_confidence:
                logger.info(f"SNOMED found via semantic retrieval: {term} → {best_result['code']}")
                return MedicalCode(
                    code=best_result['code'],
                    system='SNOMED_CT',
                    display=best_result['term'],
                    confidence=best_result['score'],
                    source='semantic_retrieval'
                )
        
        # 2. Fallback a BioPortal API (si disponible)
        if self.bioportal_client:
            api_result = await self._search_bioportal_snomed(term)
            if api_result:
                logger.info(f"SNOMED found via BioPortal API: {term} → {api_result.code}")
                return api_result
        
        logger.warning(f"No SNOMED code found for: {term}")
        return None
    
    async def get_icd10_code(self, term: str) -> Optional[MedicalCode]:
        """
        Obté codi ICD-10 per un terme mèdic
        
        Args:
            term: Terme mèdic (diagnòstic, condició)
            
        Returns:
            MedicalCode amb ICD-10 o None
        """
        # 1. Retrieval semàntic
        semantic_results = await self.ontology_retriever.search_icd10(term, limit=3)
        if semantic_results:
            best_result = semantic_results[0]
            if best_result.get('score', 0) >= self.min_confidence:
                logger.info(f"ICD-10 found via semantic retrieval: {term} → {best_result['code']}")
                return MedicalCode(
                    code=best_result['code'],
                    system='ICD10',
                    display=best_result['term'],
                    confidence=best_result['score'],
                    source='semantic_retrieval'
                )
        
        # 2. Fallback a BioPortal API
        if self.bioportal_client:
            api_result = await self._search_bioportal_icd10(term)
            if api_result:
                logger.info(f"ICD-10 found via BioPortal API: {term} → {api_result.code}")
                return api_result
        
        logger.warning(f"No ICD-10 code found for: {term}")
        return None
    
    async def get_atc_code(self, medication: str) -> Optional[MedicalCode]:
        """
        Obté codi ATC per un medicament
        
        Args:
            medication: Nom del medicament (genèric o comercial)
            
        Returns:
            MedicalCode amb ATC o None
        """
        # Preprocessar medicament (eliminar dosis)
        clean_medication = self._clean_medication_name(medication)
        
        # 1. Retrieval semàntic
        semantic_results = await self.ontology_retriever.search_atc(clean_medication, limit=3)
        if semantic_results:
            best_result = semantic_results[0]
            if best_result.get('score', 0) >= self.min_confidence:
                logger.info(f"ATC found via semantic retrieval: {medication} → {best_result['code']}")
                return MedicalCode(
                    code=best_result['code'],
                    system='ATC',
                    display=best_result['term'],
                    confidence=best_result['score'],
                    source='semantic_retrieval'
                )
        
        # 2. Fallback a BioPortal API
        if self.bioportal_client:
            api_result = await self._search_bioportal_atc(clean_medication)
            if api_result:
                logger.info(f"ATC found via BioPortal API: {medication} → {api_result.code}")
                return api_result
        
        logger.warning(f"No ATC code found for: {medication}")
        return None
    
    async def code_medical_entities(self, entities: Dict[str, List[str]]) -> Dict[str, List[MedicalCode]]:
        """
        Codifica múltiples entitats mèdiques extretes per NER
        
        Args:
            entities: Dict amb llistes d'entitats per tipus
                     {'DISEASE': [...], 'MEDICATION': [...], 'PROCEDURE': [...]}
            
        Returns:
            Dict amb codis per cada tipus d'entitat
        """
        results = {
            'diagnoses': [],
            'medications': [],
            'procedures': []
        }
        
        # Codificar diagnòstics (DISEASE) amb SNOMED + ICD-10
        if 'DISEASE' in entities:
            for disease in entities['DISEASE']:
                # SNOMED CT per diagnòstics
                snomed_code = await self.get_snomed_code(disease)
                if snomed_code:
                    results['diagnoses'].append(snomed_code)
                
                # ICD-10 per diagnòstics
                icd10_code = await self.get_icd10_code(disease)
                if icd10_code:
                    results['diagnoses'].append(icd10_code)
        
        # Codificar medicaments (MEDICATION) amb ATC
        if 'MEDICATION' in entities:
            for medication in entities['MEDICATION']:
                atc_code = await self.get_atc_code(medication)
                if atc_code:
                    results['medications'].append(atc_code)
        
        # Codificar procediments (PROCEDURE) amb SNOMED
        if 'PROCEDURE' in entities:
            for procedure in entities['PROCEDURE']:
                snomed_code = await self.get_snomed_code(procedure)
                if snomed_code:
                    results['procedures'].append(snomed_code)
        
        # Log estadístiques
        total_codes = sum(len(codes) for codes in results.values())
        logger.info(f"Coded {total_codes} medical entities: "
                   f"diagnoses={len(results['diagnoses'])}, "
                   f"medications={len(results['medications'])}, "
                   f"procedures={len(results['procedures'])}")
        
        return results
    
    def _clean_medication_name(self, medication: str) -> str:
        """
        Neteja nom de medicament eliminant dosis i formats
        
        Args:
            medication: Nom original del medicament
            
        Returns:
            Nom net del medicament
        """
        clean = medication.lower().strip()
        
        # Eliminar dosis comunes
        dose_patterns = [
            ' mg', ' g', ' ml', ' mcg', ' ui', ' iu',
            '/12h', '/24h', '/8h', '/6h',
            ' comprimits', ' comprimidos', ' tablets',
            ' càpsules', ' cápsulas', ' capsules'
        ]
        
        for pattern in dose_patterns:
            clean = clean.replace(pattern, '')
        
        # Eliminar números i símbols
        import re
        clean = re.sub(r'\d+', '', clean)
        clean = re.sub(r'[^\w\s]', '', clean)
        
        return clean.strip()
    
    async def _search_bioportal_snomed(self, term: str) -> Optional[MedicalCode]:
        """Cerca SNOMED CT a BioPortal API com a fallback"""
        if not self.bioportal_client:
            return None
            
        try:
            import aiohttp
            import os
            
            api_key = os.getenv('BIOPORTAL_API_KEY')
            if not api_key:
                logger.warning("BIOPORTAL_API_KEY not configured")
                return None
            
            base_url = "https://data.bioontology.org"
            headers = {'Authorization': f'apikey token={api_key}'}
            
            async with aiohttp.ClientSession(headers=headers) as session:
                params = {
                    'q': term,
                    'ontologies': 'SNOMEDCT',
                    'pagesize': 5,
                    'suggest': 'true'
                }
                
                async with session.get(f"{base_url}/search", params=params) as response:
                    if response.status != 200:
                        logger.error(f"BioPortal API error: {response.status}")
                        return None
                    
                    data = await response.json()
                    collection = data.get('collection', [])
                    
                    if not collection:
                        return None
                    
                    # Agafar el primer resultat (millor match)
                    best_match = collection[0]
                    
                    # Extreure codi SNOMED del notation o prefLabel
                    code = best_match.get('notation', '')
                    if not code:
                        # Intentar extreure del @id
                        concept_id = best_match.get('@id', '')
                        code = concept_id.split('/')[-1] if concept_id else ''
                    
                    display = best_match.get('prefLabel', term)
                    
                    if code:
                        logger.info(f"BioPortal SNOMED fallback: {term} → {code}")
                        return MedicalCode(
                            code=code,
                            system='SNOMED_CT',
                            display=display,
                            confidence=0.6,  # Confiança baixa per fallback
                            source='bioportal_api'
                        )
                    
                    return None
                    
        except Exception as e:
            logger.error(f"BioPortal SNOMED search error: {e}")
            return None
    
    async def _search_bioportal_icd10(self, term: str) -> Optional[MedicalCode]:
        """Cerca ICD-10 a BioPortal API com a fallback"""
        if not self.bioportal_client:
            return None
            
        try:
            import aiohttp
            import os
            
            api_key = os.getenv('BIOPORTAL_API_KEY')
            if not api_key:
                logger.warning("BIOPORTAL_API_KEY not configured")
                return None
            
            base_url = "https://data.bioontology.org"
            headers = {'Authorization': f'apikey token={api_key}'}
            
            async with aiohttp.ClientSession(headers=headers) as session:
                params = {
                    'q': term,
                    'ontologies': 'ICD10CM',
                    'pagesize': 5,
                    'suggest': 'true'
                }
                
                async with session.get(f"{base_url}/search", params=params) as response:
                    if response.status != 200:
                        logger.error(f"BioPortal API error: {response.status}")
                        return None
                    
                    data = await response.json()
                    collection = data.get('collection', [])
                    
                    if not collection:
                        return None
                    
                    # Agafar el primer resultat (millor match)
                    best_match = collection[0]
                    
                    # Extreure codi ICD-10
                    code = best_match.get('notation', '')
                    if not code:
                        concept_id = best_match.get('@id', '')
                        code = concept_id.split('/')[-1] if concept_id else ''
                    
                    display = best_match.get('prefLabel', term)
                    
                    if code:
                        logger.info(f"BioPortal ICD-10 fallback: {term} → {code}")
                        return MedicalCode(
                            code=code,
                            system='ICD-10',
                            display=display,
                            confidence=0.6,
                            source='bioportal_api'
                        )
                    
                    return None
                    
        except Exception as e:
            logger.error(f"BioPortal ICD-10 search error: {e}")
            return None
    
    async def _search_bioportal_atc(self, medication_name: str) -> Optional[MedicalCode]:
        """Cerca codi ATC a BioPortal API com a fallback"""
        if not self.bioportal_client:
            return None
            
        try:
            import aiohttp
            import os
            
            api_key = os.getenv('BIOPORTAL_API_KEY')
            if not api_key:
                logger.warning("BIOPORTAL_API_KEY not configured")
                return None
            
            base_url = "https://data.bioontology.org"
            headers = {'Authorization': f'apikey token={api_key}'}
            
            async with aiohttp.ClientSession(headers=headers) as session:
                params = {
                    'q': medication_name,
                    'ontologies': 'ATC',
                    'pagesize': 5,
                    'suggest': 'true'
                }
                
                async with session.get(f"{base_url}/search", params=params) as response:
                    if response.status != 200:
                        logger.error(f"BioPortal API error: {response.status}")
                        return None
                    
                    data = await response.json()
                    collection = data.get('collection', [])
                    
                    if not collection:
                        logger.warning(f"No ATC code found in BioPortal for: {medication_name}")
                        return None
                    
                    # Agafar el primer resultat (millor match)
                    best_match = collection[0]
                    
                    # Extreure codi ATC del notation o @id
                    code = best_match.get('notation', '')
                    if not code:
                        # Intentar extreure del @id
                        concept_id = best_match.get('@id', '')
                        code = concept_id.split('/')[-1] if concept_id else ''
                    
                    display = best_match.get('prefLabel', medication_name)
                    
                    if code:
                        logger.info(f"BioPortal ATC fallback: {medication_name} → {code}")
                        return MedicalCode(
                            code=code,
                            system='ATC',
                            display=display,
                            confidence=0.6,  # Confiança baixa per fallback API
                            source='bioportal_api'
                        )
                    
                    logger.warning(f"No valid ATC code extracted from BioPortal for: {medication_name}")
                    return None
                    
        except Exception as e:
            logger.error(f"BioPortal ATC search error: {e}")
            return None


class CodingPipeline:
    """
    Pipeline complet de codificació mèdica
    NER → Semantic Coding → Validation
    """
    
    def __init__(self, ner_service, semantic_coding_service):
        """
        Args:
            ner_service: Servei de NER per extreure entitats
            semantic_coding_service: Servei de codificació semàntica
        """
        self.ner_service = ner_service
        self.coding_service = semantic_coding_service
    
    async def process_clinical_text(self, text: str) -> Dict[str, Any]:
        """
        Processa text clínic complet: NER + Codificació
        
        Args:
            text: Text clínic generat pel LLM
            
        Returns:
            Dict amb entitats i codis mèdics
        """
        # 1. Extracció d'entitats amb NER
        entities = await self.ner_service.extract_entities(text)
        
        # 2. Codificació semàntica d'entitats
        codes = await self.coding_service.code_medical_entities(entities)
        
        # 3. Validació i neteja
        validated_codes = self._validate_codes(codes)
        
        return {
            'entities': entities,
            'codes': validated_codes,
            'summary': {
                'total_entities': sum(len(ents) for ents in entities.values()),
                'total_codes': sum(len(codes) for codes in validated_codes.values()),
                'coding_rate': self._calculate_coding_rate(entities, validated_codes)
            }
        }
    
    def _validate_codes(self, codes: Dict[str, List[MedicalCode]]) -> Dict[str, List[MedicalCode]]:
        """Valida i filtra codis per qualitat"""
        validated = {}
        
        for category, code_list in codes.items():
            # Filtrar per confidence mínim
            high_confidence = [
                code for code in code_list 
                if code.confidence >= 0.7
            ]
            
            # Eliminar duplicats per codi
            unique_codes = {}
            for code in high_confidence:
                key = f"{code.system}_{code.code}"
                if key not in unique_codes or code.confidence > unique_codes[key].confidence:
                    unique_codes[key] = code
            
            validated[category] = list(unique_codes.values())
        
        return validated
    
    def _calculate_coding_rate(self, entities: Dict, codes: Dict) -> float:
        """Calcula percentatge d'entitats codificades amb èxit"""
        total_entities = sum(len(ents) for ents in entities.values())
        total_codes = sum(len(code_list) for code_list in codes.values())
        
        if total_entities == 0:
            return 0.0
        
        return min(total_codes / total_entities, 1.0)
