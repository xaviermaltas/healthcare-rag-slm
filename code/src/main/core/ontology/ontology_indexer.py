"""
Ontology Indexer
Indexa ontologies mèdiques completes (SNOMED CT, ICD-10, ATC) a Qdrant
per retrieval semàntic en lloc de diccionaris estàtics
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class OntologyEntry:
    """Entrada d'ontologia per indexar"""
    code: str
    term: str
    synonyms: List[str]
    category: str
    ontology_type: str  # SNOMED_CT, ICD10, ATC
    language: str  # ca, es, en
    description: Optional[str] = None


class OntologyIndexer:
    """
    Indexa ontologies mèdiques completes a Qdrant
    Permet retrieval semàntic en lloc de diccionaris hardcoded
    """
    
    def __init__(self, qdrant_client):
        """
        Args:
            qdrant_client: Client de Qdrant per indexar
        """
        self.qdrant_client = qdrant_client
        self.collection_name = "medical_ontologies"
    
    async def create_ontology_collection(self):
        """Crea col·lecció Qdrant per ontologies si no existeix"""
        try:
            # TODO: Implementar creació de col·lecció amb schema adequat
            logger.info(f"Creating ontology collection: {self.collection_name}")
            # await self.qdrant_client.create_collection(...)
            pass
        except Exception as e:
            logger.error(f"Error creating ontology collection: {e}")
            raise
    
    async def index_snomed_ct(self, snomed_file_path: str):
        """
        Indexa SNOMED CT complet des d'un fitxer
        
        Args:
            snomed_file_path: Path al fitxer SNOMED CT (format RF2)
        
        Fonts públiques:
        - SNOMED CT International: https://www.nlm.nih.gov/healthit/snomedct/international.html
        - SNOMED CT Spanish Edition: https://www.snomed.org/snomed-ct/get-snomed
        """
        logger.info(f"Indexing SNOMED CT from: {snomed_file_path}")
        
        # TODO: Implementar parsing i indexació
        # 1. Llegir fitxer RF2 (TSV format)
        # 2. Extreure: conceptId, term, synonyms
        # 3. Crear OntologyEntry per cada concepte
        # 4. Indexar a Qdrant en batches
        
        entries_indexed = 0
        logger.info(f"SNOMED CT indexed: {entries_indexed} entries")
        return entries_indexed
    
    async def index_icd10(self, icd10_file_path: str):
        """
        Indexa ICD-10 complet des d'un fitxer
        
        Args:
            icd10_file_path: Path al fitxer ICD-10
        
        Fonts públiques:
        - ICD-10-CM: https://www.cdc.gov/nchs/icd/icd-10-cm.htm
        - ICD-10 WHO: https://icd.who.int/browse10/2019/en
        """
        logger.info(f"Indexing ICD-10 from: {icd10_file_path}")
        
        # TODO: Implementar parsing i indexació
        entries_indexed = 0
        logger.info(f"ICD-10 indexed: {entries_indexed} entries")
        return entries_indexed
    
    async def index_atc(self, atc_file_path: str):
        """
        Indexa ATC complet des d'un fitxer
        
        Args:
            atc_file_path: Path al fitxer ATC
        
        Fonts públiques:
        - ATC/DDD Index: https://www.whocc.no/atc_ddd_index/
        """
        logger.info(f"Indexing ATC from: {atc_file_path}")
        
        # TODO: Implementar parsing i indexació
        entries_indexed = 0
        logger.info(f"ATC indexed: {entries_indexed} entries")
        return entries_indexed
    
    async def index_entry(self, entry: OntologyEntry):
        """
        Indexa una entrada d'ontologia a Qdrant
        
        Args:
            entry: Entrada d'ontologia a indexar
        """
        # Crear text complet per embedding
        full_text = f"{entry.term} {' '.join(entry.synonyms)}"
        if entry.description:
            full_text += f" {entry.description}"
        
        # Metadata per filtratge
        metadata = {
            "code": entry.code,
            "term": entry.term,
            "category": entry.category,
            "ontology_type": entry.ontology_type,
            "language": entry.language,
            "synonyms": entry.synonyms
        }
        
        # TODO: Indexar a Qdrant
        # await self.qdrant_client.upsert(
        #     collection_name=self.collection_name,
        #     points=[{
        #         "id": f"{entry.ontology_type}_{entry.code}",
        #         "vector": embedding,
        #         "payload": metadata
        #     }]
        # )
        
        logger.debug(f"Indexed: {entry.ontology_type} {entry.code} - {entry.term}")
    
    async def index_batch(self, entries: List[OntologyEntry], batch_size: int = 100):
        """
        Indexa múltiples entrades en batches
        
        Args:
            entries: Llista d'entrades a indexar
            batch_size: Mida del batch
        """
        total = len(entries)
        for i in range(0, total, batch_size):
            batch = entries[i:i + batch_size]
            for entry in batch:
                await self.index_entry(entry)
            
            logger.info(f"Indexed batch {i//batch_size + 1}: {min(i+batch_size, total)}/{total}")


class OntologyRetriever:
    """
    Retrieval semàntic d'ontologies des de Qdrant
    Substitueix diccionaris estàtics
    """
    
    def __init__(self, qdrant_client):
        """
        Args:
            qdrant_client: Client de Qdrant
        """
        self.qdrant_client = qdrant_client
        self.collection_name = "medical_ontologies"
    
    async def search_snomed(self, term: str, limit: int = 5) -> List[Dict]:
        """
        Cerca codis SNOMED CT per un terme
        
        Args:
            term: Terme mèdic a cercar
            limit: Nombre màxim de resultats
            
        Returns:
            Llista de resultats amb code, term, score
        """
        results = await self._search_ontology(
            term=term,
            ontology_type="SNOMED_CT",
            limit=limit
        )
        return results
    
    async def search_icd10(self, term: str, limit: int = 5) -> List[Dict]:
        """Cerca codis ICD-10 per un terme"""
        results = await self._search_ontology(
            term=term,
            ontology_type="ICD10",
            limit=limit
        )
        return results
    
    async def search_atc(self, term: str, limit: int = 5) -> List[Dict]:
        """Cerca codis ATC per un medicament"""
        results = await self._search_ontology(
            term=term,
            ontology_type="ATC",
            limit=limit
        )
        return results
    
    async def _search_ontology(
        self,
        term: str,
        ontology_type: str,
        limit: int = 5
    ) -> List[Dict]:
        """
        Cerca genèrica d'ontologia amb filtre per tipus
        
        Args:
            term: Terme a cercar
            ontology_type: Tipus d'ontologia (SNOMED_CT, ICD10, ATC)
            limit: Nombre de resultats
            
        Returns:
            Llista de {code, term, score, synonyms}
        """
        try:
            # TODO: Implementar cerca a Qdrant
            # results = await self.qdrant_client.search(
            #     collection_name=self.collection_name,
            #     query_text=term,
            #     query_filter={"ontology_type": ontology_type},
            #     limit=limit
            # )
            
            # Placeholder
            results = []
            
            logger.info(f"Search {ontology_type} for '{term}': {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error searching ontology: {e}")
            return []


# Diccionari mínim de fallback (30 termes ultra-comuns)
MINIMAL_FALLBACK = {
    # SNOMED CT - 10 termes més comuns
    'SNOMED_CT': {
        'diabetis': '73211009',
        'diabetes': '73211009',
        'hipertensió': '38341003',
        'hipertensión': '38341003',
        'infart': '57054005',
        'pneumònia': '233604007',
        'neumonía': '233604007',
        'asma': '195967001',
        'depressió': '35489007',
        'depresión': '35489007',
    },
    
    # ICD-10 - 10 termes més comuns
    'ICD10': {
        'diabetis tipus 2': 'E11.9',
        'diabetes tipo 2': 'E11.9',
        'hipertensió': 'I10',
        'hipertensión': 'I10',
        'infart miocardi': 'I21.9',
        'infarto miocardio': 'I21.9',
        'pneumònia': 'J18.9',
        'neumonía': 'J18.9',
        'asma': 'J45.909',
        'depressió': 'F32.9',
    },
    
    # ATC - 10 medicaments més prescrits
    'ATC': {
        'metformina': 'A10BA02',
        'enalapril': 'C09AA02',
        'atorvastatina': 'C10AA05',
        'omeprazol': 'A02BC01',
        'paracetamol': 'N02BE01',
        'ibuprofè': 'M01AE01',
        'ibuprofeno': 'M01AE01',
        'adiro': 'B01AC06',
        'aspirina': 'B01AC06',
        'losartan': 'C09CA01',
    }
}
