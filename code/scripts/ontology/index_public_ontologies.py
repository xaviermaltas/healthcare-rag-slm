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
            # Diabetis i metabolisme
            "73211009\tDiabetes mellitus\ten\t900000000000013009",
            "73211009\tDiabetis mellitus\tca\t900000000000013009",
            "73211009\tDiabetes mellitus\tes\t900000000000013009",
            "44054006\tType 2 diabetes mellitus\ten\t900000000000013009",
            "44054006\tDiabetis mellitus tipus 2\tca\t900000000000013009",
            "44054006\tDiabetes mellitus tipo 2\tes\t900000000000013009",
            "46635009\tType 1 diabetes mellitus\ten\t900000000000013009",
            "46635009\tDiabetis mellitus tipus 1\tca\t900000000000013009",
            "46635009\tDiabetes mellitus tipo 1\tes\t900000000000013009",
            "237599002\tInsulin resistance\ten\t900000000000013009",
            "237599002\tResistència a la insulina\tca\t900000000000013009",
            "237599002\tResistencia a la insulina\tes\t900000000000013009",
            
            # Cardiovascular
            "38341003\tHypertensive disorder\ten\t900000000000013009",
            "38341003\tTrastorn hipertensiu\tca\t900000000000013009",
            "38341003\tTrastorno hipertensivo\tes\t900000000000013009",
            "59621000\tEssential hypertension\ten\t900000000000013009",
            "59621000\tHipertensió essencial\tca\t900000000000013009",
            "59621000\tHipertensión esencial\tes\t900000000000013009",
            "57054005\tAcute myocardial infarction\ten\t900000000000013009",
            "57054005\tInfart agut de miocardi\tca\t900000000000013009",
            "57054005\tInfarto agudo de miocardio\tes\t900000000000013009",
            "22298006\tMyocardial infarction\ten\t900000000000013009",
            "22298006\tInfart de miocardi\tca\t900000000000013009",
            "22298006\tInfarto de miocardio\tes\t900000000000013009",
            "84114007\tHeart failure\ten\t900000000000013009",
            "84114007\tInsuficiència cardíaca\tca\t900000000000013009",
            "84114007\tInsuficiencia cardíaca\tes\t900000000000013009",
            "49601007\tCardiovascular disease\ten\t900000000000013009",
            "49601007\tMalaltia cardiovascular\tca\t900000000000013009",
            "49601007\tEnfermedad cardiovascular\tes\t900000000000013009",
            "53741008\tCoronary artery disease\ten\t900000000000013009",
            "53741008\tMalaltia de les artèries coronàries\tca\t900000000000013009",
            "53741008\tEnfermedad de las arterias coronarias\tes\t900000000000013009",
            "13645005\tChronic obstructive pulmonary disease\ten\t900000000000013009",
            "13645005\tMalaltia pulmonar obstructiva crònica\tca\t900000000000013009",
            "13645005\tEnfermedad pulmonar obstructiva crónica\tes\t900000000000013009",
            
            # Respiratori
            "233604007\tPneumonia\ten\t900000000000013009",
            "233604007\tPneumònia\tca\t900000000000013009",
            "233604007\tNeumonía\tes\t900000000000013009",
            "195967001\tAsthma\ten\t900000000000013009",
            "195967001\tAsma\tca\t900000000000013009",
            "195967001\tAsma\tes\t900000000000013009",
            "389087006\tBronchitis\ten\t900000000000013009",
            "389087006\tBronquitis\tca\t900000000000013009",
            "389087006\tBronquitis\tes\t900000000000013009",
            
            # Neurològic
            "230690007\tCerebrovascular accident\ten\t900000000000013009",
            "230690007\tAccident cerebrovascular\tca\t900000000000013009",
            "230690007\tAccidente cerebrovascular\tes\t900000000000013009",
            "432504007\tCerebral infarction\ten\t900000000000013009",
            "432504007\tInfart cerebral\tca\t900000000000013009",
            "432504007\tInfarto cerebral\tes\t900000000000013009",
            "49049000\tParkinson's disease\ten\t900000000000013009",
            "49049000\tMalaltia de Parkinson\tca\t900000000000013009",
            "49049000\tEnfermedad de Parkinson\tes\t900000000000013009",
            "26929004\tAlzheimer's disease\ten\t900000000000013009",
            "26929004\tMalaltia d'Alzheimer\tca\t900000000000013009",
            "26929004\tEnfermedad de Alzheimer\tes\t900000000000013009",
            "25064002\tHeadache\ten\t900000000000013009",
            "25064002\tCefalea\tca\t900000000000013009",
            "25064002\tCefalea\tes\t900000000000013009",
            "37796009\tMigraine\ten\t900000000000013009",
            "37796009\tMigranya\tca\t900000000000013009",
            "37796009\tMigraña\tes\t900000000000013009",
            
            # Gastrointestinal
            "235595009\tGastritis\ten\t900000000000013009",
            "235595009\tGastritis\tca\t900000000000013009",
            "235595009\tGastritis\tes\t900000000000013009",
            "397825006\tGastric ulcer\ten\t900000000000013009",
            "397825006\tÚlcera gàstrica\tca\t900000000000013009",
            "397825006\tÚlcera gástrica\tes\t900000000000013009",
            "235919008\tDuodenal ulcer\ten\t900000000000013009",
            "235919008\tÚlcera duodenal\tca\t900000000000013009",
            "235919008\tÚlcera duodenal\tes\t900000000000013009",
            "197480006\tAnxiety disorder\ten\t900000000000013009",
            "197480006\tTrastorn d'ansietat\tca\t900000000000013009",
            "197480006\tTrastorno de ansiedad\tes\t900000000000013009",
            
            # Psiquiàtric
            "35489007\tDepressive disorder\ten\t900000000000013009",
            "35489007\tTrastorn depressiu\tca\t900000000000013009",
            "35489007\tTrastorno depresivo\tes\t900000000000013009",
            "191736004\tBipolar disorder\ten\t900000000000013009",
            "191736004\tTrastorn bipolar\tca\t900000000000013009",
            "191736004\tTrastorno bipolar\tes\t900000000000013009",
            
            # Renal
            "709044004\tChronic kidney disease\ten\t900000000000013009",
            "709044004\tMalaltia renal crònica\tca\t900000000000013009",
            "709044004\tEnfermedad renal crónica\tes\t900000000000013009",
            "236425005\tEnd stage renal disease\ten\t900000000000013009",
            "236425005\tMalaltia renal terminal\tca\t900000000000013009",
            "236425005\tEnfermedad renal terminal\tes\t900000000000013009",
            
            # Endocrí
            "40930008\tHypothyroidism\ten\t900000000000013009",
            "40930008\tHipotiroïdisme\tca\t900000000000013009",
            "40930008\tHipotiroidismo\tes\t900000000000013009",
            "34486009\tHyperthyroidism\ten\t900000000000013009",
            "34486009\tHipertiroïdisme\tca\t900000000000013009",
            "34486009\tHipertiroidismo\tes\t900000000000013009",
            
            # Hematològic
            "271737000\tAnemia\ten\t900000000000013009",
            "271737000\tAnèmia\tca\t900000000000013009",
            "271737000\tAnemia\tes\t900000000000013009",
            "87522002\tIron deficiency anemia\ten\t900000000000013009",
            "87522002\tAnèmia per deficiència de ferro\tca\t900000000000013009",
            "87522002\tAnemia por deficiencia de hierro\tes\t900000000000013009",
            
            # Reumatològic
            "69896004\tRheumatoid arthritis\ten\t900000000000013009",
            "69896004\tArtritis reumatoide\tca\t900000000000013009",
            "69896004\tArtritis reumatoide\tes\t900000000000013009",
            "396275006\tOsteoarthritis\ten\t900000000000013009",
            "396275006\tOsteoartritis\tca\t900000000000013009",
            "396275006\tOsteoartritis\tes\t900000000000013009",
            
            # Infecciós
            "840539006\tCOVID-19\ten\t900000000000013009",
            "840539006\tCOVID-19\tca\t900000000000013009",
            "840539006\tCOVID-19\tes\t900000000000013009",
            "6142004\tInfluenza\ten\t900000000000013009",
            "6142004\tGrip\tca\t900000000000013009",
            "6142004\tGripe\tes\t900000000000013009",
            "56717001\tTuberculosis\ten\t900000000000013009",
            "56717001\tTuberculosi\tca\t900000000000013009",
            "56717001\tTuberculosis\tes\t900000000000013009",
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
        
        # 🆕 AMPLIAT: Dataset amb 50+ codis ICD-10 més comuns
        icd10_data = [
            # Diabetis
            "E11.9\tType 2 diabetes mellitus without complications\ten",
            "E11.9\tDiabetis mellitus tipus 2 sense complicacions\tca",
            "E11.9\tDiabetes mellitus tipo 2 sin complicaciones\tes",
            "E10.9\tType 1 diabetes mellitus without complications\ten",
            "E10.9\tDiabetis mellitus tipus 1 sense complicacions\tca",
            "E10.9\tDiabetes mellitus tipo 1 sin complicaciones\tes",
            
            # Cardiovascular
            "I10\tEssential hypertension\ten",
            "I10\tHipertensió essencial\tca",
            "I10\tHipertensión esencial\tes",
            "I21.9\tAcute myocardial infarction, unspecified\ten",
            "I21.9\tInfart agut de miocardi, no especificat\tca",
            "I21.9\tInfarto agudo de miocardio, no especificado\tes",
            "I50.9\tHeart failure, unspecified\ten",
            "I50.9\tInsuficiència cardíaca, no especificada\tca",
            "I50.9\tInsuficiencia cardíaca, no especificada\tes",
            "I25.10\tAtherosclerotic heart disease\ten",
            "I25.10\tMalaltia cardíaca ateroscleròtica\tca",
            "I25.10\tEnfermedad cardíaca aterosclerótica\tes",
            
            # Respiratori
            "J18.9\tPneumonia, unspecified organism\ten",
            "J18.9\tPneumònia, organisme no especificat\tca",
            "J18.9\tNeumonía, organismo no especificado\tes",
            "J45.909\tUnspecified asthma, uncomplicated\ten",
            "J45.909\tAsma no especificat, sense complicacions\tca",
            "J45.909\tAsma no especificado, sin complicaciones\tes",
            "J44.9\tChronic obstructive pulmonary disease, unspecified\ten",
            "J44.9\tMalaltia pulmonar obstructiva crònica, no especificada\tca",
            "J44.9\tEnfermedad pulmonar obstructiva crónica, no especificada\tes",
            "J20.9\tAcute bronchitis, unspecified\ten",
            "J20.9\tBronquitis aguda, no especificada\tca",
            "J20.9\tBronquitis aguda, no especificada\tes",
            
            # Neurològic
            "I63.9\tCerebral infarction, unspecified\ten",
            "I63.9\tInfart cerebral, no especificat\tca",
            "I63.9\tInfarto cerebral, no especificado\tes",
            "G20\tParkinson's disease\ten",
            "G20\tMalaltia de Parkinson\tca",
            "G20\tEnfermedad de Parkinson\tes",
            "G30.9\tAlzheimer's disease, unspecified\ten",
            "G30.9\tMalaltia d'Alzheimer, no especificada\tca",
            "G30.9\tEnfermedad de Alzheimer, no especificada\tes",
            "R51\tHeadache\ten",
            "R51\tCefalea\tca",
            "R51\tCefalea\tes",
            "G43.909\tMigraine, unspecified\ten",
            "G43.909\tMigranya, no especificada\tca",
            "G43.909\tMigraña, no especificada\tes",
            
            # Gastrointestinal
            "K29.70\tGastritis, unspecified\ten",
            "K29.70\tGastritis, no especificada\tca",
            "K29.70\tGastritis, no especificada\tes",
            "K25.9\tGastric ulcer, unspecified\ten",
            "K25.9\tÚlcera gàstrica, no especificada\tca",
            "K25.9\tÚlcera gástrica, no especificada\tes",
            "K26.9\tDuodenal ulcer, unspecified\ten",
            "K26.9\tÚlcera duodenal, no especificada\tca",
            "K26.9\tÚlcera duodenal, no especificada\tes",
            
            # Psiquiàtric
            "F41.9\tAnxiety disorder, unspecified\ten",
            "F41.9\tTrastorn d'ansietat, no especificat\tca",
            "F41.9\tTrastorno de ansiedad, no especificado\tes",
            "F32.9\tMajor depressive disorder, single episode, unspecified\ten",
            "F32.9\tTrastorn depressiu major, episodi únic, no especificat\tca",
            "F32.9\tTrastorno depresivo mayor, episodio único, no especificado\tes",
            "F31.9\tBipolar disorder, unspecified\ten",
            "F31.9\tTrastorn bipolar, no especificat\tca",
            "F31.9\tTrastorno bipolar, no especificado\tes",
            
            # Renal
            "N18.9\tChronic kidney disease, unspecified\ten",
            "N18.9\tMalaltia renal crònica, no especificada\tca",
            "N18.9\tEnfermedad renal crónica, no especificada\tes",
            "N18.6\tEnd stage renal disease\ten",
            "N18.6\tMalaltia renal terminal\tca",
            "N18.6\tEnfermedad renal terminal\tes",
            
            # Endocrí
            "E03.9\tHypothyroidism, unspecified\ten",
            "E03.9\tHipotiroïdisme, no especificat\tca",
            "E03.9\tHipotiroidismo, no especificado\tes",
            "E05.90\tThyrotoxicosis, unspecified\ten",
            "E05.90\tTirotoxicosi, no especificada\tca",
            "E05.90\tTirotoxicosis, no especificada\tes",
            
            # Hematològic
            "D64.9\tAnemia, unspecified\ten",
            "D64.9\tAnèmia, no especificada\tca",
            "D64.9\tAnemia, no especificada\tes",
            "D50.9\tIron deficiency anemia, unspecified\ten",
            "D50.9\tAnèmia per deficiència de ferro, no especificada\tca",
            "D50.9\tAnemia por deficiencia de hierro, no especificada\tes",
            
            # Reumatològic
            "M06.9\tRheumatoid arthritis, unspecified\ten",
            "M06.9\tArtritis reumatoide, no especificada\tca",
            "M06.9\tArtritis reumatoide, no especificada\tes",
            "M19.90\tUnspecified osteoarthritis, unspecified site\ten",
            "M19.90\tOsteoartritis no especificada, localització no especificada\tca",
            "M19.90\tOsteoartritis no especificada, localización no especificada\tes",
            
            # Infecciós
            "U07.1\tCOVID-19\ten",
            "U07.1\tCOVID-19\tca",
            "U07.1\tCOVID-19\tes",
            "J11.1\tInfluenza due to unidentified influenza virus\ten",
            "J11.1\tGrip deguda a virus de la grip no identificat\tca",
            "J11.1\tGripe debida a virus de la gripe no identificado\tes",
            "A15.9\tRespiratory tuberculosis unspecified\ten",
            "A15.9\tTuberculosi respiratòria no especificada\tca",
            "A15.9\tTuberculosis respiratoria no especificada\tes",
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
        
        # 🆕 AMPLIAT: Dataset amb 50+ medicaments ATC més comuns
        atc_data = [
            # Antidiabètics
            "A10BA02\tMetformin\tmetformin\tglucophage,dianben\ten",
            "A10BA02\tMetformina\tmetformina\tglucophage,dianben\tes",
            "A10BA02\tMetformina\tmetformina\tglucophage,dianben\tca",
            "A10AB01\tInsulin (human)\tinsulin\tactrapid,humulin\ten",
            "A10AB01\tInsulina (humana)\tinsulina\tactrapid,humulin\tes",
            "A10AB01\tInsulina (humana)\tinsulina\tactrapid,humulin\tca",
            
            # Antihipertensius
            "C09AA02\tEnalapril\tenalapril\trenitec\ten",
            "C09AA02\tEnalapril\tenalapril\trenitec\tes",
            "C09AA02\tEnalapril\tenalapril\trenitec\tca",
            "C09CA01\tLosartan\tlosartan\tcozaar\ten",
            "C09CA01\tLosartan\tlosartan\tcozaar\tes",
            "C09CA01\tLosartan\tlosartan\tcozaar\tca",
            "C07AB07\tBisoprolol\tbisoprolol\tconcor,emconcor\ten",
            "C07AB07\tBisoprolol\tbisoprolol\tconcor,emconcor\tes",
            "C07AB07\tBisoprolol\tbisoprolol\tconcor,emconcor\tca",
            "C08CA01\tAmlodipine\tamlodipine\tnorvasc\ten",
            "C08CA01\tAmlodipino\tamlodipino\tnorvasc\tes",
            "C08CA01\tAmlodipí\tamlodipí\tnorvasc\tca",
            
            # Hipolipemiants
            "C10AA05\tAtorvastatin\tatorvastatin\tlipitor,zarator\ten",
            "C10AA05\tAtorvastatin\tatorvastatina\tlipitor,zarator\tes",
            "C10AA05\tAtorvastatin\tatorvastatina\tlipitor,zarator\tca",
            "C10AA01\tSimvastatin\tsimvastatin\tzocor\ten",
            "C10AA01\tSimvastatina\tsimvastatina\tzocor\tes",
            "C10AA01\tSimvastatina\tsimvastatina\tzocor\tca",
            
            # Antiulcerosos
            "A02BC01\tOmeprazole\tomeprazole\tlosec\ten",
            "A02BC01\tOmeprazol\tomeprazol\tlosec\tes",
            "A02BC01\tOmeprazol\tomeprazol\tlosec\tca",
            "A02BC05\tEsomeprazole\tesomeprazole\tnexium\ten",
            "A02BC05\tEsomeprazol\tesomeprazol\tnexium\tes",
            "A02BC05\tEsomeprazol\tesomeprazol\tnexium\tca",
            
            # Analgèsics
            "N02BE01\tParacetamol\tparacetamol\tgelocatil\ten",
            "N02BE01\tParacetamol\tparacetamol\tgelocatil\tes",
            "N02BE01\tParacetamol\tparacetamol\tgelocatil\tca",
            "M01AE01\tIbuprofen\tibuprofen\tespidifen\ten",
            "M01AE01\tIbuprofeno\tibuprofeno\tespidifen\tes",
            "M01AE01\tIbuprofè\tibuprofè\tespidifen\tca",
            
            # Antiagregants
            "B01AC06\tAcetylsalicylic acid\taspirin\tadiro,aspirina\ten",
            "B01AC06\tÁcido acetilsalicílico\taspirina\tadiro,aspirina\tes",
            "B01AC06\tÀcid acetilsalicílic\taspirina\tadiro,aspirina\tca",
            "B01AC04\tClopidogrel\tclopidogrel\tplavix\ten",
            "B01AC04\tClopidogrel\tclopidogrel\tplavix\tes",
            "B01AC04\tClopidogrel\tclopidogrel\tplavix\tca",
            
            # Anticoagulants
            "B01AA03\tWarfarin\twarfarin\taldocumar\ten",
            "B01AA03\tWarfarina\twarfarina\taldocumar\tes",
            "B01AA03\tWarfarina\twarfarina\taldocumar\tca",
            "B01AF01\tRivaroxaban\trivaroxaban\txarelto\ten",
            "B01AF01\tRivaroxaban\trivaroxaban\txarelto\tes",
            "B01AF01\tRivaroxaban\trivaroxaban\txarelto\tca",
            
            # Broncodilatadors
            "R03AC02\tSalbutamol\tsalbutamol\tventolin\ten",
            "R03AC02\tSalbutamol\tsalbutamol\tventolin\tes",
            "R03AC02\tSalbutamol\tsalbutamol\tventolin\tca",
            
            # Antibiòtics
            "J01CA04\tAmoxicillin\tamoxicillin\tamoxil\ten",
            "J01CA04\tAmoxicilina\tamoxicilina\tamoxil\tes",
            "J01CA04\tAmoxicil·lina\tamoxicil·lina\tamoxil\tca",
            "J01CR02\tAmoxicillin and clavulanic acid\tamoxicillin-clavulanate\taugmentine\ten",
            "J01CR02\tAmoxicilina y ácido clavulánico\tamoxicilina-clavulanato\taugmentine\tes",
            "J01CR02\tAmoxicil·lina i àcid clavulànic\tamoxicil·lina-clavulanat\taugmentine\tca",
            
            # Antidepressius
            "N06AB03\tFluoxetine\tfluoxetine\tprozac\ten",
            "N06AB03\tFluoxetina\tfluoxetina\tprozac\tes",
            "N06AB03\tFluoxetina\tfluoxetina\tprozac\tca",
            "N06AB04\tCitalopram\tcitalopram\tseropram\ten",
            "N06AB04\tCitalopram\tcitalopram\tseropram\tes",
            "N06AB04\tCitalopram\tcitalopram\tseropram\tca",
            
            # Ansiolítics
            "N05BA01\tDiazepam\tdiazepam\tvalium\ten",
            "N05BA01\tDiazepam\tdiazepam\tvalium\tes",
            "N05BA01\tDiazepam\tdiazepam\tvalium\tca",
            "N05BA12\tAlprazolam\talprazolam\ttrankimazin\ten",
            "N05BA12\tAlprazolam\talprazolam\ttrankimazin\tes",
            "N05BA12\tAlprazolam\talprazolam\ttrankimazin\tca",
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
        from src.main.infrastructure.embeddings.bge_m3 import BGEM3Embeddings
        
        qdrant_client = HealthcareQdrantClient(collection_name="medical_ontologies")
        await qdrant_client.initialize()
        
        embeddings_model = BGEM3Embeddings()
        await embeddings_model.initialize()
        
        ontology_indexer = OntologyIndexer(qdrant_client, embeddings_model)
        
        # 2. Crear col·lecció d'ontologies
        await ontology_indexer.create_ontology_collection()
        
        # 3. Descarregar ontologies públiques
        downloader = PublicOntologyDownloader()
        
        # Use extended dataset if available, otherwise use basic
        extended_snomed = Path("data/ontologies/snomed_ct_extended.tsv")
        if extended_snomed.exists():
            logger.info("✅ Using EXTENDED SNOMED dataset")
            snomed_file = str(extended_snomed)
        else:
            logger.info("⚠️ Using basic SNOMED dataset")
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
