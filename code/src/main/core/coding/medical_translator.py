"""
Medical Term Translator
Translates medical terms from Catalan/Spanish to English for ontology search
"""

from typing import Optional, Dict
import logging

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
