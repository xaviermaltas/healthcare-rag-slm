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
    
    def __init__(self, qdrant_client, embeddings_model=None):
        """
        Args:
            qdrant_client: Client de Qdrant per indexar
            embeddings_model: Model d'embeddings (BGE-M3)
        """
        self.qdrant_client = qdrant_client
        self.embeddings_model = embeddings_model
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
        ✅ IMPLEMENTAT: Indexa una entrada d'ontologia a Qdrant
        
        Args:
            entry: Entrada d'ontologia a indexar
        """
        # Crear text complet per embedding
        full_text = f"{entry.term} {' '.join(entry.synonyms)}"
        if entry.description:
            full_text += f" {entry.description}"
        
        # Generate embedding using embeddings model
        try:
            # Use BGE-M3 embeddings model
            if self.embeddings_model is None:
                logger.error("No embeddings model provided to OntologyIndexer")
                return
            
            # encode returns array, we need first element
            embeddings = await self.embeddings_model.encode([full_text])
            embedding = embeddings[0].tolist()  # Convert numpy to list for Qdrant
            
            # Metadata per filtratge
            metadata = {
                "code": entry.code,
                "term": entry.term,
                "category": entry.category,
                "ontology_type": entry.ontology_type,
                "language": entry.language,
                "synonyms": entry.synonyms,
                "description": entry.description or "",
                "full_text": full_text
            }
            
            # Indexar a Qdrant
            from qdrant_client.models import PointStruct
            
            point = PointStruct(
                id=hash(f"{entry.ontology_type}_{entry.code}_{entry.language}"),
                vector=embedding,
                payload=metadata
            )
            
            self.qdrant_client.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            logger.debug(f"✅ Indexed: {entry.ontology_type} {entry.code} - {entry.term}")
            
        except Exception as e:
            logger.error(f"❌ Error indexing {entry.ontology_type} {entry.code}: {e}")
    
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
    
    def __init__(self, qdrant_client, embeddings_model=None):
        """
        Args:
            qdrant_client: Client de Qdrant
            embeddings_model: Model d'embeddings (BGE-M3)
        """
        self.qdrant_client = qdrant_client
        self.embeddings_model = embeddings_model
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
        ✅ IMPLEMENTAT: Cerca genèrica d'ontologia amb filtre per tipus
        
        Args:
            term: Terme a cercar
            ontology_type: Tipus d'ontologia (SNOMED_CT, ICD10, ATC)
            limit: Nombre de resultats
            
        Returns:
            Llista de {code, term, score, synonyms}
        """
        try:
            if self.embeddings_model is None:
                logger.error("No embeddings model provided to OntologyRetriever")
                return []
            
            # Generate embedding for search term
            embeddings = await self.embeddings_model.encode([term])
            query_vector = embeddings[0].tolist()
            
            # Search in Qdrant with filter
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="ontology_type",
                        match=MatchValue(value=ontology_type)
                    )
                ]
            )
            
            search_results = self.qdrant_client.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                query_filter=search_filter,
                limit=limit
            ).points
            
            # Format results
            results = []
            for hit in search_results:
                results.append({
                    'code': hit.payload.get('code'),
                    'term': hit.payload.get('term'),
                    'score': hit.score,
                    'synonyms': hit.payload.get('synonyms', []),
                    'language': hit.payload.get('language'),
                    'category': hit.payload.get('category')
                })
            
            logger.debug(f"Search {ontology_type} for '{term}': {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error searching ontology: {e}")
            return []
