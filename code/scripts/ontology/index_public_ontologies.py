#!/usr/bin/env python3
"""
Index Public Medical Ontologies
Script per indexar ontologies mèdiques públiques a Qdrant
Fonts: SNOMED CT, ICD-10, ATC des de repositoris oficials
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.main.core.ontology.ontology_indexer import OntologyIndexer, OntologyEntry
from src.main.infrastructure.vector_db.qdrant_client import HealthcareQdrantClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PublicOntologyDownloader:
    """
    Descarrega ontologies mèdiques des de fonts públiques oficials
    """
    
    def __init__(self, data_dir: str = "data/ontologies"):
        """
        Args:
            data_dir: Directori on guardar les ontologies descarregades
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    async def download_snomed_ct_subset(self) -> str:
        """
        Descarrega subset públic de SNOMED CT
        
        Font oficial: https://www.nlm.nih.gov/healthit/snomedct/international.html
        Subset gratuït: SNOMED CT International Edition (Core subset)
        
        Returns:
            Path al fitxer descarregat
        """
        logger.info("Downloading SNOMED CT public subset...")
        
        # Per ara, creem un subset simulat amb termes comuns
        # En producció, descarregar des de NLM/SNOMED International
        
        snomed_file = self.data_dir / "snomed_ct_subset.tsv"
        
        # Crear subset simulat amb estructura RF2
        snomed_data = [
            # Format: conceptId\tterm\tlanguageCode\ttypeId
            "73211009\tDiabetes mellitus\ten\t900000000000013009",
            "73211009\tDiabetis mellitus\tca\t900000000000013009",
            "73211009\tDiabetes mellitus\tes\t900000000000013009",
            "38341003\tHypertensive disorder\ten\t900000000000013009",
            "38341003\tTrastorn hipertensiu\tca\t900000000000013009",
            "38341003\tTrastorno hipertensivo\tes\t900000000000013009",
            "57054005\tAcute myocardial infarction\ten\t900000000000013009",
            "57054005\tInfart agut de miocardi\tca\t900000000000013009",
            "57054005\tInfarto agudo de miocardio\tes\t900000000000013009",
            "233604007\tPneumonia\ten\t900000000000013009",
            "233604007\tPneumònia\tca\t900000000000013009",
            "233604007\tNeumonía\tes\t900000000000013009",
            "195967001\tAsthma\ten\t900000000000013009",
            "195967001\tAsma\tca\t900000000000013009",
            "195967001\tAsma\tes\t900000000000013009",
            # Afegir més termes...
        ]
        
        with open(snomed_file, 'w', encoding='utf-8') as f:
            f.write("conceptId\tterm\tlanguageCode\ttypeId\n")
            for line in snomed_data:
                f.write(line + "\n")
        
        logger.info(f"SNOMED CT subset created: {snomed_file}")
        return str(snomed_file)
    
    async def download_icd10_cm(self) -> str:
        """
        Descarrega ICD-10-CM des de CDC
        
        Font oficial: https://www.cdc.gov/nchs/icd/icd-10-cm.htm
        Fitxers públics disponibles en format XML/TXT
        
        Returns:
            Path al fitxer descarregat
        """
        logger.info("Downloading ICD-10-CM...")
        
        icd10_file = self.data_dir / "icd10_cm.tsv"
        
        # Crear subset simulat
        icd10_data = [
            # Format: code\tterm\tlanguage
            "E11.9\tType 2 diabetes mellitus without complications\ten",
            "E11.9\tDiabetis mellitus tipus 2 sense complicacions\tca",
            "E11.9\tDiabetes mellitus tipo 2 sin complicaciones\tes",
            "I10\tEssential hypertension\ten",
            "I10\tHipertensió essencial\tca",
            "I10\tHipertensión esencial\tes",
            "I21.9\tAcute myocardial infarction, unspecified\ten",
            "I21.9\tInfart agut de miocardi, no especificat\tca",
            "I21.9\tInfarto agudo de miocardio, no especificado\tes",
            "J18.9\tPneumonia, unspecified organism\ten",
            "J18.9\tPneumònia, organisme no especificat\tca",
            "J18.9\tNeumonía, organismo no especificado\tes",
            "J45.909\tUnspecified asthma, uncomplicated\ten",
            "J45.909\tAsma no especificat, sense complicacions\tca",
            "J45.909\tAsma no especificado, sin complicaciones\tes",
            # Afegir més codis...
        ]
        
        with open(icd10_file, 'w', encoding='utf-8') as f:
            f.write("code\tterm\tlanguage\n")
            for line in icd10_data:
                f.write(line + "\n")
        
        logger.info(f"ICD-10-CM created: {icd10_file}")
        return str(icd10_file)
    
    async def download_atc_ddd(self) -> str:
        """
        Descarrega ATC/DDD Index des de WHO
        
        Font oficial: https://www.whocc.no/atc_ddd_index/
        Fitxers públics disponibles
        
        Returns:
            Path al fitxer descarregat
        """
        logger.info("Downloading ATC/DDD Index...")
        
        atc_file = self.data_dir / "atc_ddd.tsv"
        
        # Crear subset simulat
        atc_data = [
            # Format: code\tterm\tgeneric_name\tcommercial_names\tlanguage
            "A10BA02\tMetformin\tmetformin\tglucophage,dianben\ten",
            "A10BA02\tMetformina\tmetformina\tglucophage,dianben\tes",
            "A10BA02\tMetformina\tmetformina\tglucophage,dianben\tca",
            "C09AA02\tEnalapril\tenalapril\trenitec\ten",
            "C09AA02\tEnalapril\tenalapril\trenitec\tes",
            "C09AA02\tEnalapril\tenalapril\trenitec\tca",
            "C10AA05\tAtorvastatin\tatorvastatin\tlipitor,zarator\ten",
            "C10AA05\tAtorvastatin\tatorvastatina\tlipitor,zarator\tes",
            "C10AA05\tAtorvastatin\tatorvastatina\tlipitor,zarator\tca",
            "A02BC01\tOmeprazole\tomeprazole\tlosec\ten",
            "A02BC01\tOmeprazol\tomeprazol\tlosec\tes",
            "A02BC01\tOmeprazol\tomeprazol\tlosec\tca",
            "N02BE01\tParacetamol\tparacetamol\tgelocatil\ten",
            "N02BE01\tParacetamol\tparacetamol\tgelocatil\tes",
            "N02BE01\tParacetamol\tparacetamol\tgelocatil\tca",
            # Afegir més medicaments...
        ]
        
        with open(atc_file, 'w', encoding='utf-8') as f:
            f.write("code\tterm\tgeneric_name\tcommercial_names\tlanguage\n")
            for line in atc_data:
                f.write(line + "\n")
        
        logger.info(f"ATC/DDD created: {atc_file}")
        return str(atc_file)


class OntologyParser:
    """
    Parser per convertir fitxers d'ontologies a OntologyEntry
    """
    
    @staticmethod
    def parse_snomed_rf2(file_path: str) -> List[OntologyEntry]:
        """
        Parseja fitxer SNOMED CT en format RF2
        
        Args:
            file_path: Path al fitxer RF2
            
        Returns:
            Llista d'OntologyEntry
        """
        entries = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            # Skip header
            next(f)
            
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 4:
                    concept_id = parts[0]
                    term = parts[1]
                    language = parts[2]
                    
                    entry = OntologyEntry(
                        code=concept_id,
                        term=term,
                        synonyms=[],  # TODO: Extreure sinònims
                        category="clinical_finding",  # TODO: Determinar categoria
                        ontology_type="SNOMED_CT",
                        language=language
                    )
                    entries.append(entry)
        
        logger.info(f"Parsed {len(entries)} SNOMED CT entries")
        return entries
    
    @staticmethod
    def parse_icd10_cm(file_path: str) -> List[OntologyEntry]:
        """
        Parseja fitxer ICD-10-CM
        
        Args:
            file_path: Path al fitxer ICD-10
            
        Returns:
            Llista d'OntologyEntry
        """
        entries = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            # Skip header
            next(f)
            
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 3:
                    code = parts[0]
                    term = parts[1]
                    language = parts[2]
                    
                    # Determinar categoria per codi ICD-10
                    category = "disease"
                    if code.startswith('E'):
                        category = "endocrine"
                    elif code.startswith('I'):
                        category = "cardiovascular"
                    elif code.startswith('J'):
                        category = "respiratory"
                    
                    entry = OntologyEntry(
                        code=code,
                        term=term,
                        synonyms=[],
                        category=category,
                        ontology_type="ICD10",
                        language=language
                    )
                    entries.append(entry)
        
        logger.info(f"Parsed {len(entries)} ICD-10 entries")
        return entries
    
    @staticmethod
    def parse_atc_ddd(file_path: str) -> List[OntologyEntry]:
        """
        Parseja fitxer ATC/DDD
        
        Args:
            file_path: Path al fitxer ATC
            
        Returns:
            Llista d'OntologyEntry
        """
        entries = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            # Skip header
            next(f)
            
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 5:
                    code = parts[0]
                    term = parts[1]
                    generic_name = parts[2]
                    commercial_names = parts[3].split(',') if parts[3] else []
                    language = parts[4]
                    
                    # Crear sinònims amb noms genèrics i comercials
                    synonyms = [generic_name] + commercial_names
                    synonyms = [s.strip() for s in synonyms if s.strip()]
                    
                    # Determinar categoria per codi ATC
                    category = "medication"
                    if code.startswith('C'):
                        category = "cardiovascular_drug"
                    elif code.startswith('A'):
                        category = "alimentary_drug"
                    elif code.startswith('N'):
                        category = "nervous_system_drug"
                    
                    entry = OntologyEntry(
                        code=code,
                        term=term,
                        synonyms=synonyms,
                        category=category,
                        ontology_type="ATC",
                        language=language
                    )
                    entries.append(entry)
        
        logger.info(f"Parsed {len(entries)} ATC entries")
        return entries


async def main():
    """
    Script principal per indexar ontologies públiques
    """
    logger.info("Starting public ontology indexing...")
    
    try:
        # 1. Inicialitzar clients
        qdrant_client = HealthcareQdrantClient(collection_name="medical_ontologies")
        await qdrant_client.initialize()
        
        ontology_indexer = OntologyIndexer(qdrant_client)
        
        # 2. Crear col·lecció d'ontologies
        await ontology_indexer.create_ontology_collection()
        
        # 3. Descarregar ontologies públiques
        downloader = PublicOntologyDownloader()
        
        snomed_file = await downloader.download_snomed_ct_subset()
        icd10_file = await downloader.download_icd10_cm()
        atc_file = await downloader.download_atc_ddd()
        
        # 4. Parsejar i indexar SNOMED CT
        logger.info("Indexing SNOMED CT...")
        snomed_entries = OntologyParser.parse_snomed_rf2(snomed_file)
        await ontology_indexer.index_batch(snomed_entries)
        
        # 5. Parsejar i indexar ICD-10
        logger.info("Indexing ICD-10...")
        icd10_entries = OntologyParser.parse_icd10_cm(icd10_file)
        await ontology_indexer.index_batch(icd10_entries)
        
        # 6. Parsejar i indexar ATC
        logger.info("Indexing ATC...")
        atc_entries = OntologyParser.parse_atc_ddd(atc_file)
        await ontology_indexer.index_batch(atc_entries)
        
        # 7. Estadístiques finals
        total_entries = len(snomed_entries) + len(icd10_entries) + len(atc_entries)
        logger.info(f"✅ Ontology indexing completed!")
        logger.info(f"   Total entries indexed: {total_entries}")
        logger.info(f"   - SNOMED CT: {len(snomed_entries)}")
        logger.info(f"   - ICD-10: {len(icd10_entries)}")
        logger.info(f"   - ATC: {len(atc_entries)}")
        
    except Exception as e:
        logger.error(f"Error indexing ontologies: {e}")
        raise
    
    finally:
        if 'qdrant_client' in locals() and qdrant_client.client:
            logger.info("Qdrant client cleanup completed")


if __name__ == "__main__":
    asyncio.run(main())
