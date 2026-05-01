"""
Medical Term Translator
Translates medical terms from Catalan/Spanish to English for ontology search
"""

from typing import Dict, Optional
import logging
from src.main.core.coding.snomed_extended_lookup import SNOMEDExtendedLookup
from src.main.core.coding.icd10_extended_lookup import ICD10ExtendedLookup
from src.main.core.coding.atc_extended_lookup import ATCExtendedLookup

logger = logging.getLogger(__name__)


class MedicalTranslator:
    """
    Translates medical terms to English for better ontology coverage
    Uses a curated dictionary of common medical terms
    """
    
    # Dictionary: Catalan/Spanish -> English
    MEDICAL_TERMS = {
        # Diagnoses - Catalan
        'infart agut de miocardi': 'acute myocardial infarction',
        'infart de miocardi': 'myocardial infarction',
        'diabetis mellitus tipus 2': 'type 2 diabetes mellitus',
        'diabetis tipus 2': 'type 2 diabetes mellitus',
        'diabetis mellitus tipus 1': 'type 1 diabetes mellitus',
        'diabetis tipus 1': 'type 1 diabetes mellitus',
        'diabetis mellitus': 'diabetes mellitus',
        'diabetis': 'diabetes',
        'hipertensió arterial': 'arterial hypertension',
        'hipertensió': 'hypertension',
        'pneumònia': 'pneumonia',
        'pneumònia adquirida a la comunitat': 'community acquired pneumonia',
        'accident cerebrovascular': 'cerebrovascular accident',
        'accident cerebrovascular isquèmic': 'ischemic stroke',
        'ictus': 'stroke',
        'ictus isquèmic': 'ischemic stroke',
        'insuficiència cardíaca': 'heart failure',
        'insuficiència cardíaca congestiva': 'congestive heart failure',
        'fibril·lació auricular': 'atrial fibrillation',
        'malaltia pulmonar obstructiva crònica': 'chronic obstructive pulmonary disease',
        'mpoc': 'copd',
        'epoc': 'copd',
        'asma': 'asthma',
        'bronquitis': 'bronchitis',
        'obesitat': 'obesity',
        'dislipèmia': 'dyslipidemia',
        'hipercolesterolèmia': 'hypercholesterolemia',
        'insuficiència renal crònica': 'chronic kidney disease',
        'insuficiència renal': 'kidney failure',
        'cirrosi hepàtica': 'liver cirrhosis',
        'hepatitis': 'hepatitis',
        'anèmia': 'anemia',
        'trombosi': 'thrombosis',
        'embòlia pulmonar': 'pulmonary embolism',
        'angina de pit': 'angina pectoris',
        'cardiopatia isquèmica': 'ischemic heart disease',
        'epilèpsia': 'epilepsy',
        'malaltia de parkinson': 'parkinson disease',
        "malaltia d'alzheimer": 'alzheimer disease',
        'demència': 'dementia',
        'depressió': 'depression',
        'ansietat': 'anxiety',
        'esquizofrènia': 'schizophrenia',
        'artritis reumatoide': 'rheumatoid arthritis',
        'artrosi': 'osteoarthritis',
        'osteoporosi': 'osteoporosis',
        'fractura': 'fracture',
        'càncer': 'cancer',
        'tumor': 'tumor',
        'leucèmia': 'leukemia',
        'limfoma': 'lymphoma',
        'melanoma': 'melanoma',
        'sepsi': 'sepsis',
        'sèpsia': 'sepsis',
        'infecció': 'infection',
        'covid-19': 'covid-19',
        'grip': 'influenza',
        'tuberculosi': 'tuberculosis',
        'vih': 'hiv',
        'sida': 'aids',
        
        # Diagnoses - Spanish
        'infarto agudo de miocardio': 'acute myocardial infarction',
        'infarto de miocardio': 'myocardial infarction',
        'diabetes mellitus tipo 2': 'type 2 diabetes mellitus',
        'diabetes tipo 2': 'type 2 diabetes mellitus',
        'diabetes mellitus tipo 1': 'type 1 diabetes mellitus',
        'diabetes tipo 1': 'type 1 diabetes mellitus',
        'diabetes mellitus': 'diabetes mellitus',
        'diabetes': 'diabetes',
        'hipertensión arterial': 'arterial hypertension',
        'hipertensión': 'hypertension',
        'neumonía': 'pneumonia',
        'neumonía adquirida en la comunidad': 'community acquired pneumonia',
        'accidente cerebrovascular': 'cerebrovascular accident',
        'accidente cerebrovascular isquémico': 'ischemic stroke',
        'ictus isquémico': 'ischemic stroke',
        'insuficiencia cardíaca': 'heart failure',
        'insuficiencia cardíaca congestiva': 'congestive heart failure',
        'fibrilación auricular': 'atrial fibrillation',
        'enfermedad pulmonar obstructiva crónica': 'chronic obstructive pulmonary disease',
        'obesidad': 'obesity',
        'dislipemia': 'dyslipidemia',
        'hipercolesterolemia': 'hypercholesterolemia',
        'insuficiencia renal crónica': 'chronic kidney disease',
        'insuficiencia renal': 'kidney failure',
        'cirrosis hepática': 'liver cirrhosis',
        'anemia': 'anemia',
        'trombosis': 'thrombosis',
        'embolia pulmonar': 'pulmonary embolism',
        'angina de pecho': 'angina pectoris',
        'cardiopatía isquémica': 'ischemic heart disease',
        'epilepsia': 'epilepsy',
        'enfermedad de parkinson': 'parkinson disease',
        'enfermedad de alzheimer': 'alzheimer disease',
        'demencia': 'dementia',
        'depresión': 'depression',
        'ansiedad': 'anxiety',
        'esquizofrenia': 'schizophrenia',
        'artritis reumatoide': 'rheumatoid arthritis',
        'artrosis': 'osteoarthritis',
        'osteoporosis': 'osteoporosis',
        'fractura': 'fracture',
        'cáncer': 'cancer',
        'leucemia': 'leukemia',
        'linfoma': 'lymphoma',
        'sepsis': 'sepsis',
        'infección': 'infection',
        'gripe': 'influenza',
        'tuberculosis': 'tuberculosis',
        
        # Medications - Catalan
        'àcid acetilsalicílic': 'acetylsalicylic acid',
        'aspirina': 'aspirin',
        'paracetamol': 'paracetamol',
        'ibuprofèn': 'ibuprofen',
        'metformina': 'metformin',
        'insulina': 'insulin',
        'enalapril': 'enalapril',
        'losartan': 'losartan',
        'atorvastatina': 'atorvastatin',
        'simvastatina': 'simvastatin',
        'omeprazol': 'omeprazole',
        'amoxicil·lina': 'amoxicillin',
        'azitromicina': 'azithromycin',
        'furosemida': 'furosemide',
        'espironolactona': 'spironolactone',
        'bisoprolol': 'bisoprolol',
        'carvedilol': 'carvedilol',
        'digoxina': 'digoxin',
        'warfarina': 'warfarin',
        'acenocumarol': 'acenocoumarol',
        'clopidogrel': 'clopidogrel',
        'apixaban': 'apixaban',
        'rivaroxaban': 'rivaroxaban',
        'levotiroxina': 'levothyroxine',
        'prednisona': 'prednisone',
        'hidrocortisona': 'hydrocortisone',
        'salbutamol': 'salbutamol',
        'budesonida': 'budesonide',
        'morfina': 'morphine',
        'tramadol': 'tramadol',
        'gabapentina': 'gabapentin',
        'pregabalina': 'pregabalin',
        'sertralina': 'sertraline',
        'fluoxetina': 'fluoxetine',
        'escitalopram': 'escitalopram',
        'diazepam': 'diazepam',
        'lorazepam': 'lorazepam',
        'alprazolam': 'alprazolam',
        'zolpidem': 'zolpidem',
        'melatonina': 'melatonin',
        
        # Medications - Spanish
        'ácido acetilsalicílico': 'acetylsalicylic acid',
        'ibuprofeno': 'ibuprofen',
        'amoxicilina': 'amoxicillin',
        'furosemida': 'furosemide',
        
        # Additional medications
        'metformina': 'metformin',
        'atorvastatina': 'atorvastatin',
        'simvastatina': 'simvastatin',
    }
    
    # ICD-10 lookup table: normalized term (lowercase) → ICD-10 code
    # Covers Catalan, Spanish and English variants of common diagnoses
    ICD10_LOOKUP: Dict[str, str] = {
        # Cardiovascular
        'acute myocardial infarction': 'I21.0',
        'myocardial infarction': 'I21.0',
        'stemi': 'I21.0',
        'infart agut de miocardi': 'I21.0',
        'infart agut de miocardi amb elevació del segment st': 'I21.0',
        'iamest': 'I21.0',
        'infarto agudo de miocardio': 'I21.0',
        'hypertension': 'I10',
        'arterial hypertension': 'I10',
        'essential hypertension': 'I10',
        'hipertensió arterial': 'I10',
        'hipertensió arterial essencial': 'I10',
        'hipertensión arterial': 'I10',
        'heart failure': 'I50.9',
        'insuficiència cardíaca': 'I50.9',
        'insuficiencia cardíaca': 'I50.9',
        'atrial fibrillation': 'I48.0',
        'fibril·lació auricular': 'I48.0',
        'fibrilación auricular': 'I48.0',
        'ischemic stroke': 'I63.4',
        'cerebral infarction': 'I63.4',
        'ictus isquèmic': 'I63.4',
        'ictus isquémico': 'I63.4',
        'stroke': 'I63.9',
        'angina pectoris': 'I20.9',
        'angina de pit': 'I20.9',
        # Endocrine
        'type 2 diabetes mellitus': 'E11.9',
        'diabetes mellitus type 2': 'E11.9',
        'diabetis mellitus tipus 2': 'E11.9',
        'diabetes mellitus tipo 2': 'E11.9',
        'diabetis tipus 2': 'E11.9',
        'hypothyroidism': 'E03.9',
        'hipotiroïdisme': 'E03.9',
        'hipotiroidismo': 'E03.9',
        'dyslipidemia': 'E78.5',
        'mixed dyslipidemia': 'E78.2',
        'dislipèmia mixta': 'E78.2',
        'dislipemia mixta': 'E78.2',
        'hypercholesterolemia': 'E78.0',
        'hipercolesterolèmia': 'E78.0',
        'hyponatremia': 'E87.1',
        'hiponatrèmia': 'E87.1',
        'hiponatremia': 'E87.1',
        # Respiratory
        'community acquired pneumonia': 'J18.1',
        'pneumònia adquirida a la comunitat': 'J18.1',
        'neumonía adquirida en la comunidad': 'J18.1',
        'pneumonia': 'J18.9',
        'pneumònia': 'J18.9',
        'copd': 'J44.1',
        'chronic obstructive pulmonary disease': 'J44.1',
        'malaltia pulmonar obstructiva crònica': 'J44.1',
        'mpoc': 'J44.1',
        'epoc': 'J44.1',
        'asthma': 'J45.9',
        'asma': 'J45.9',
        # Mental / substance
        'smoking': 'F17.2',
        'nicotine dependence': 'F17.2',
        'tabaquisme': 'F17.2',
        'tabaquisme actiu': 'F17.2',
        'tabaquismo': 'F17.2',
        # Neurological
        'epilepsy': 'G40.9',
        'epilèpsia': 'G40.9',
        'epilepsia': 'G40.9',
        'migraine': 'G43.9',
        'migranya': 'G43.9',
        # Digestive
        'gastroesophageal reflux disease': 'K21.0',
        'reflux gastroesofàgic': 'K21.0',
        'reflujo gastroesofágico': 'K21.0',
        'peptic ulcer': 'K27.9',
        # Musculoskeletal
        'osteoporosis': 'M81.0',
        'osteoporòsi': 'M81.0',
        'rheumatoid arthritis': 'M06.9',
        'artritis reumatoide': 'M06.9',
        # Renal
        'chronic kidney disease': 'N18.9',
        'malaltia renal crònica': 'N18.9',
        'enfermedad renal crónica': 'N18.9',
        'urinary tract infection': 'N39.0',
        'infecció urinària': 'N39.0',
        'infección urinaria': 'N39.0',
        # Clinical abbreviations (Catalan/Spanish)
        'acvi': 'I63.4',             # Accident cerebrovascular isquèmic
        'ictus': 'I63.9',
        'iamest': 'I21.0',           # Infart agut de miocardi amb elevació ST
        'iamsest': 'I21.4',          # Infart agut de miocardi sense elevació ST
        'sca': 'I24.9',              # Síndrome coronari agut
        'iam': 'I21.9',              # Infart agut de miocardi
        'fa': 'I48.0',               # Fibril·lació auricular
        'ic': 'I50.9',               # Insuficiència cardíaca
        'hta': 'I10',                # Hipertensió arterial
        'dm2': 'E11.9',             # Diabetis mellitus tipus 2
        'mpoc': 'J44.1',            # Malaltia pulmonar obstructiva crònica
        'epoc': 'J44.1',            # Enfermedad pulmonar obstructiva crónica
        'ira': 'N17.9',             # Insuficiència renal aguda
        'irc': 'N18.9',             # Insuficiència renal crònica
        'tep': 'I26.9',             # Tromboembolisme pulmonar
        'tvp': 'I80.2',             # Trombosi venosa profunda
        'ictus isquèmic': 'I63.4',
        'accident cerebrovascular isquèmic': 'I63.4',
        'accident vascular cerebral': 'I64',
        'avc': 'I64',
    }
    
    # SNOMED CT lookup table: normalized diagnosis term → SNOMED CT code
    SNOMED_LOOKUP: Dict[str, str] = {
        # Cardiovascular
        'infart agut de miocardi': '57054005',
        'infart agut de miocardi amb elevació del segment st': '57054005',
        'iamest': '57054005',
        'stemi': '57054005',
        'myocardial infarction': '57054005',
        'acute myocardial infarction': '57054005',
        'infarto agudo de miocardio': '57054005',
        'iam': '57054005',
        'heart failure': '84114007',
        'insuficiència cardíaca': '84114007',
        'insuficiencia cardíaca': '84114007',
        'heart failure acute': '56675007',
        'insuficiència cardíaca aguda': '56675007',
        'hypertension': '59621000',
        'hipertensió arterial': '59621000',
        'hipertensión arterial': '59621000',
        'hta': '59621000',
        'atrial fibrillation': '49436004',
        'fibril·lació auricular': '49436004',
        'fibrilación auricular': '49436004',
        'fa': '49436004',
        'angina de pit': '194828000',
        'angina pectoris': '194828000',
        'angina de pecho': '194828000',
        # Metabolic
        'diabetes mellitus tipus 2': '44054006',
        'diabetis mellitus tipus 2': '44054006',
        'diabetes mellitus type 2': '44054006',
        'diabetes mellitus tipo 2': '44054006',
        'dm2': '44054006',
        't2dm': '44054006',
        'diabetes mellitus amb complicacions': '420422005',
        'diabetes mellitus with complications': '420422005',
        'diabetis mellitus amb cetoacidosi': '420422005',
        'diabetis amb cetoacidosi': '420422005',
        'dyslipidemia': '370992007',
        'dislipèmia': '370992007',
        'dislipemia': '370992007',
        'hiperlipidèmia': '55822004',
        'hyperlipidemia': '55822004',
        # Respiratory
        'pneumonia': '233604007',
        'pneumònia': '233604007',
        'community acquired pneumonia': '385093006',
        'pneumònia adquirida a la comunitat': '385093006',
        'pneumonia comunitaria': '385093006',
        'copd': '13645005',
        'mpoc': '13645005',
        'epoc': '13645005',
        'chronic obstructive pulmonary disease': '13645005',
        'malaltia pulmonar obstructiva crònica': '13645005',
        'asthma': '195967001',
        'asma': '195967001',
        # Neurological
        'ischemic stroke': '422504002',
        'ictus isquèmic': '422504002',
        'cerebral infarction': '422504002',
        'accident cerebrovascular isquèmic': '422504002',
        'acvi': '422504002',
        'stroke': '230690007',
        'ictus': '230690007',
        'avc': '230690007',
        # Renal
        'acute kidney injury': '14669001',
        'insuficiència renal aguda': '14669001',
        'insuficiencia renal aguda': '14669001',
        'chronic kidney disease': '709044004',
        'malaltia renal crònica': '709044004',
    }

    @classmethod
    def get_snomed_code(cls, term: str) -> Optional[str]:
        """
        Look up SNOMED CT code for a medical term.
        Uses extended lookup (500+ terms) + legacy lookup + translation fallback.
        Returns None if the term is not found.
        """
        # 1. Try extended lookup first (500+ terms in ca/es/en)
        code = SNOMEDExtendedLookup.search(term)
        if code:
            logger.info(f"SNOMED found in extended lookup: {term} → {code}")
            return code
        
        # 2. Fallback to legacy lookup
        normalized = term.lower().strip()
        if normalized in cls.SNOMED_LOOKUP:
            logger.info(f"SNOMED found in legacy lookup: {term} → {cls.SNOMED_LOOKUP[normalized]}")
            return cls.SNOMED_LOOKUP[normalized]

        # 3. Translated match (to English)
        translated = cls.translate_to_english(term).lower().strip()
        if translated in cls.SNOMED_LOOKUP:
            logger.info(f"SNOMED found via translation: {term} → {cls.SNOMED_LOOKUP[translated]}")
            return cls.SNOMED_LOOKUP[translated]

        # 4. Partial match on meaningful keys (≥8 chars)
        for key, code in cls.SNOMED_LOOKUP.items():
            if len(key) >= 8 and (key in normalized or normalized in key):
                logger.info(f"SNOMED found via partial match: {term} → {code}")
                return code

        logger.warning(f"No SNOMED code found for: {term}")
        return None

    # ATC lookup table: normalized medication name → ATC code
    # Covers Catalan, Spanish and English variants
    ATC_LOOKUP: Dict[str, str] = {
        # ACE inhibitors
        'enalapril': 'C09AA02',
        'enalapril maleate': 'C09AA02',
        'lisinopril': 'C09AA03',
        'ramipril': 'C09AA05',
        'perindopril': 'C09AA04',
        'captopril': 'C09AA01',
        # ARBs
        'losartan': 'C09CA01',
        'valsartan': 'C09CA03',
        'irbesartan': 'C09CA04',
        'candesartan': 'C09CA06',
        'olmesartan': 'C09CA08',
        # Beta-blockers
        'bisoprolol': 'C07AB07',
        'metoprolol': 'C07AB02',
        'carvedilol': 'C07AG02',
        'atenolol': 'C07AB03',
        'nebivolol': 'C07AB12',
        # Statins
        'atorvastatin': 'C10AA05',
        'atorvastatina': 'C10AA05',
        'simvastatin': 'C10AA01',
        'simvastatina': 'C10AA01',
        'rosuvastatin': 'C10AA07',
        'rosuvastatina': 'C10AA07',
        'pravastatin': 'C10AA03',
        # Antiplatelet
        'aspirin': 'B01AC06',
        'àcid acetilsalicílic': 'B01AC06',
        'acido acetilsalicilico': 'B01AC06',
        'aas': 'B01AC06',
        'clopidogrel': 'B01AC04',
        'ticagrelor': 'B01AC24',
        'prasugrel': 'B01AC22',
        # Anticoagulants
        'warfarin': 'B01AA03',
        'acenocoumarol': 'B01AA07',
        'acenocumarol': 'B01AA07',
        'heparin': 'B01AB01',
        'heparina': 'B01AB01',
        'enoxaparin': 'B01AB05',
        'enoxaparina': 'B01AB05',
        'rivaroxaban': 'B01AF01',
        'apixaban': 'B01AF02',
        'dabigatran': 'B01AE07',
        # Antidiabetics
        'metformin': 'A10BA02',
        'metformina': 'A10BA02',
        'insulin': 'A10AB01',
        'insulina': 'A10AB01',
        'glipizide': 'A10BB07',
        'gliclazide': 'A10BB09',
        'sitagliptin': 'A10BH01',
        'empagliflozin': 'A10BK03',
        'dapagliflozin': 'A10BK01',
        # Diuretics
        'furosemide': 'C03CA01',
        'furosemida': 'C03CA01',
        'hydrochlorothiazide': 'C03AA03',
        'hidroclorotiazida': 'C03AA03',
        'spironolactone': 'C03DA01',
        'espironolactona': 'C03DA01',
        # Calcium channel blockers
        'amlodipine': 'C08CA01',
        'amlodipino': 'C08CA01',
        'nifedipine': 'C08CA05',
        # Antibiotics
        'amoxicillin': 'J01CA04',
        'amoxicilina': 'J01CA04',
        'amoxicillin clavulanate': 'J01CR02',
        'amoxicilina clavulanico': 'J01CR02',
        'azithromycin': 'J01FA10',
        'azitromicina': 'J01FA10',
        'levofloxacin': 'J01MA12',
        'levofloxacino': 'J01MA12',
        'ciprofloxacin': 'J01MA02',
        'ceftriazone': 'J01DD04',
        'ceftriaxona': 'J01DD04',
        # Bronchodilators
        'salbutamol': 'R03AC02',
        'ipratropium': 'R03BB01',
        'ipratropio': 'R03BB01',
        'tiotropium': 'R03BB04',
        'tiotroipo': 'R03BB04',
        'salmeterol': 'R03AC12',
        'formoterol': 'R03AC13',
        'budesonide': 'R03BA02',
        # Proton pump inhibitors
        'omeprazole': 'A02BC01',
        'omeprazol': 'A02BC01',
        'pantoprazole': 'A02BC02',
        'pantoprazol': 'A02BC02',
        'esomeprazole': 'A02BC05',
        # Analgesics
        'paracetamol': 'N02BE01',
        'ibuprofen': 'M01AE01',
        'ibuprofeno': 'M01AE01',
        'tramadol': 'N02AX02',
        # Corticosteroids
        'prednisone': 'H02AB07',
        'prednisolone': 'H02AB06',
        'methylprednisolone': 'H02AB04',
        'dexamethasone': 'H02AB02',
        # Thyroid
        'levothyroxine': 'H03AA01',
        'levotiroxina': 'H03AA01',
    }

    @classmethod
    def get_atc_code(cls, term: str) -> Optional[str]:
        """
        Look up ATC code for a medication.
        Uses extended lookup (218 terms) + legacy lookup + translation fallback.
        Returns None if the term is not found.
        """
        # 1. Try extended lookup first (218 terms, noms genèrics + comercials)
        code = ATCExtendedLookup.search(term)
        if code:
            logger.info(f"ATC found in extended lookup: {term} → {code}")
            return code
        
        # 2. Fallback to legacy lookup
        normalized = term.lower().strip()
        if normalized in cls.ATC_LOOKUP:
            logger.info(f"ATC found in legacy lookup: {term} → {cls.ATC_LOOKUP[normalized]}")
            return cls.ATC_LOOKUP[normalized]

        # 3. Translated match
        translated = cls.translate_to_english(term).lower().strip()
        if translated in cls.ATC_LOOKUP:
            logger.info(f"ATC found via translation: {term} → {cls.ATC_LOOKUP[translated]}")
            return cls.ATC_LOOKUP[translated]

        # 4. Partial match
        for key, code in cls.ATC_LOOKUP.items():
            if len(key) >= 6 and (key in normalized or normalized in key):
                logger.info(f"ATC found via partial match: {term} → {code}")
                return code

        logger.warning(f"No ATC code found for: {term}")
        return None

    @classmethod
    def get_icd10_code(cls, term: str) -> Optional[str]:
        """
        Look up ICD-10 code for a medical term.
        Uses extended lookup (181 terms) + legacy lookup + translation fallback.
        Returns None if the term is not found.
        
        Args:
            term: Medical term in any supported language
            
        Returns:
            ICD-10 code string or None
        """
        # 1. Try extended lookup first (181 terms in ca/es/en)
        code = ICD10ExtendedLookup.search(term)
        if code:
            logger.info(f"ICD-10 found in extended lookup: {term} → {code}")
            return code
        
        # 2. Fallback to legacy lookup
        normalized = term.lower().strip()
        if normalized in cls.ICD10_LOOKUP:
            logger.info(f"ICD-10 found in legacy lookup: {term} → {cls.ICD10_LOOKUP[normalized]}")
            return cls.ICD10_LOOKUP[normalized]
        
        # 3. Translated match
        translated = cls.translate_to_english(term).lower().strip()
        if translated in cls.ICD10_LOOKUP:
            logger.info(f"ICD-10 found via translation: {term} → {cls.ICD10_LOOKUP[translated]}")
            return cls.ICD10_LOOKUP[translated]
        
        # 4. Partial match
        for key, code in cls.ICD10_LOOKUP.items():
            if key in normalized or normalized in key:
                if len(key) >= 6:
                    logger.info(f"ICD-10 found via partial match: {term} → {code}")
                    return code
        
        logger.warning(f"No ICD-10 code found for: {term}")
        return None

    @classmethod
    def translate_to_english(cls, term: str) -> str:
        """
        Translate medical term to English
        
        Args:
            term: Medical term in Catalan/Spanish/English
            
        Returns:
            Translated term in English (or original if no translation found)
        """
        # Normalize: lowercase and strip
        normalized = term.lower().strip()
        
        # Check if translation exists
        if normalized in cls.MEDICAL_TERMS:
            translated = cls.MEDICAL_TERMS[normalized]
            logger.debug(f"Translated '{term}' -> '{translated}'")
            return translated
        
        # Try partial matches (for compound terms)
        for cat_term, eng_term in cls.MEDICAL_TERMS.items():
            if cat_term in normalized or normalized in cat_term:
                logger.debug(f"Partial match: '{term}' -> '{eng_term}'")
                return eng_term
        
        # No translation found, return original
        logger.debug(f"No translation for '{term}', using original")
        return term
    
    @classmethod
    def get_search_variants(cls, term: str) -> list[str]:
        """
        Get search variants for a medical term
        Returns list of terms to try: [original, translated, simplified]
        
        Args:
            term: Medical term
            
        Returns:
            List of search variants
        """
        variants = []
        
        # Original term
        variants.append(term)
        
        # Translated term (if different)
        translated = cls.translate_to_english(term)
        if translated.lower() != term.lower():
            variants.append(translated)
        
        # Simplified versions (remove common words)
        simplified = cls._simplify_term(term)
        if simplified not in variants:
            variants.append(simplified)
        
        return variants
    
    @classmethod
    def _simplify_term(cls, term: str) -> str:
        """
        Simplify medical term by removing common words
        
        Examples:
            "Diabetis mellitus tipus 2" -> "Diabetis tipus 2"
            "Pneumònia adquirida a la comunitat" -> "Pneumònia"
        """
        # Words to remove
        stop_words = [
            'agut', 'aguda', 'agudo', 'aguda',
            'crònic', 'crònica', 'crónico', 'crónica',
            'adquirit', 'adquirida', 'adquirido', 'adquirida',
            'a la comunitat', 'en la comunidad',
            'de', 'del', 'de la', 'dels', 'de les',
            'amb', 'con',
            'sense', 'sin',
        ]
        
        simplified = term.lower()
        for word in stop_words:
            simplified = simplified.replace(word, ' ')
        
        # Clean up extra spaces
        simplified = ' '.join(simplified.split())
        
        return simplified.strip()
