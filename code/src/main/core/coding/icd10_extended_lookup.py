"""
Extended ICD-10 Lookup Dictionary
Diccionari ampli amb 50+ condicions ICD-10 en ca/es/en
Basat en ICD-10-CM (Clinical Modification)
"""

from typing import Dict, Optional


class ICD10ExtendedLookup:
    """
    Lookup table amb codis ICD-10 per condicions mèdiques comunes
    Inclou variants en català, castellà i anglès
    """
    
    # Cardiovascular
    CARDIOVASCULAR = {
        # Infart miocardi
        'infart agut de miocardi': 'I21.9',
        'infarto agudo de miocardio': 'I21.9',
        'acute myocardial infarction': 'I21.9',
        'iamest': 'I21.3',
        'stemi': 'I21.3',
        'iam': 'I21.9',
        'infart amb elevació st': 'I21.3',
        'infarto con elevación st': 'I21.3',
        'st elevation mi': 'I21.3',
        
        # Angina
        'angina de pit': 'I20.9',
        'angina de pecho': 'I20.9',
        'angina pectoris': 'I20.9',
        'angina inestable': 'I20.0',
        'unstable angina': 'I20.0',
        
        # Hipertensió
        'hipertensió arterial': 'I10',
        'hipertensión arterial': 'I10',
        'hypertension': 'I10',
        'hta': 'I10',
        'hipertensió essencial': 'I10',
        
        # Insuficiència cardíaca
        'insuficiència cardíaca': 'I50.9',
        'insuficiencia cardíaca': 'I50.9',
        'heart failure': 'I50.9',
        'ic': 'I50.9',
        'insuficiència cardíaca congestiva': 'I50.0',
        'congestive heart failure': 'I50.0',
        
        # Fibril·lació auricular
        'fibril·lació auricular': 'I48.91',
        'fibrilación auricular': 'I48.91',
        'atrial fibrillation': 'I48.91',
        'fa': 'I48.91',
        
        # Ictus
        'ictus': 'I63.9',
        'accidente cerebrovascular': 'I63.9',
        'stroke': 'I63.9',
        'avc': 'I63.9',
        'infart cerebral': 'I63.9',
        
        # Altres cardiovasculars
        'dolor toràcic': 'R07.9',
        'dolor torácico': 'R07.9',
        'chest pain': 'R07.9',
    }
    
    # Respiratori
    RESPIRATORY = {
        # Pneumònia
        'pneumònia': 'J18.9',
        'neumonía': 'J18.9',
        'pneumonia': 'J18.9',
        'pneumònia bacteriana': 'J15.9',
        'bacterial pneumonia': 'J15.9',
        
        # MPOC
        'malaltia pulmonar obstructiva crònica': 'J44.9',
        'enfermedad pulmonar obstructiva crónica': 'J44.9',
        'chronic obstructive pulmonary disease': 'J44.9',
        'mpoc': 'J44.9',
        'copd': 'J44.9',
        'epoc': 'J44.9',
        
        # Asma
        'asma': 'J45.909',
        'asthma': 'J45.909',
        'asma persistent': 'J45.50',
        
        # Bronquitis
        'bronquitis': 'J40',
        'bronquitis aguda': 'J20.9',
        'acute bronchitis': 'J20.9',
        
        # Altres respiratoris
        'dispnea': 'R06.00',
        'disnea': 'R06.00',
        'dyspnea': 'R06.00',
        'dificultat respiratòria': 'R06.00',
    }
    
    # Endocrí i Metabòlic
    ENDOCRINE = {
        # Diabetis tipus 2
        'diabetis mellitus tipus 2': 'E11.9',
        'diabetes mellitus tipo 2': 'E11.9',
        'type 2 diabetes mellitus': 'E11.9',
        'dm2': 'E11.9',
        't2dm': 'E11.9',
        'diabetis tipus 2 amb complicacions': 'E11.8',
        
        # Diabetis tipus 1
        'diabetis mellitus tipus 1': 'E10.9',
        'diabetes mellitus tipo 1': 'E10.9',
        'type 1 diabetes mellitus': 'E10.9',
        'dm1': 'E10.9',
        't1dm': 'E10.9',
        
        # Tiroide
        'hipertiroïdisme': 'E05.90',
        'hipertiroidismo': 'E05.90',
        'hyperthyroidism': 'E05.90',
        'hipotiroïdisme': 'E03.9',
        'hipotiroidismo': 'E03.9',
        'hypothyroidism': 'E03.9',
        
        # Obesitat
        'obesitat': 'E66.9',
        'obesidad': 'E66.9',
        'obesity': 'E66.9',
        'obesitat mòrbida': 'E66.01',
        
        # Dislipèmia
        'dislipèmia': 'E78.5',
        'dislipemia': 'E78.5',
        'dyslipidemia': 'E78.5',
        'hiperlipidèmia': 'E78.5',
        'hipercolesterolèmia': 'E78.0',
    }
    
    # Neurològic
    NEUROLOGICAL = {
        # Cefalea
        'cefalea': 'R51',
        'cefalea': 'R51',
        'headache': 'R51',
        'mal de cap': 'R51',
        'dolor de cabeza': 'R51',
        
        # Migranya
        'migranya': 'G43.909',
        'migraña': 'G43.909',
        'migraine': 'G43.909',
        
        # Epilèpsia
        'epilèpsia': 'G40.909',
        'epilepsia': 'G40.909',
        'epilepsy': 'G40.909',
        
        # Parkinson
        'malaltia de parkinson': 'G20',
        'enfermedad de parkinson': 'G20',
        "parkinson's disease": 'G20',
        'parkinson': 'G20',
        
        # Demència
        'demència': 'F03.90',
        'demencia': 'F03.90',
        'dementia': 'F03.90',
        'alzheimer': 'G30.9',
        'malaltia d\'alzheimer': 'G30.9',
        
        # Esclerosi múltiple
        'esclerosi múltiple': 'G35',
        'esclerosis múltiple': 'G35',
        'multiple sclerosis': 'G35',
    }
    
    # Digestiu
    DIGESTIVE = {
        # Dolor abdominal
        'dolor abdominal': 'R10.9',
        'abdominal pain': 'R10.9',
        
        # Gastritis
        'gastritis': 'K29.70',
        'gastritis aguda': 'K29.00',
        
        # Úlcera
        'úlcera pèptica': 'K27.9',
        'úlcera péptica': 'K27.9',
        'peptic ulcer': 'K27.9',
        'úlcera gàstrica': 'K25.9',
        'úlcera duodenal': 'K26.9',
        
        # Refluix
        'refluix gastroesofàgic': 'K21.9',
        'reflujo gastroesofágico': 'K21.9',
        'gastroesophageal reflux': 'K21.9',
        'erge': 'K21.9',
        'gerd': 'K21.9',
        
        # Colelitiasi
        'colelitiasi': 'K80.20',
        'colelitiasis': 'K80.20',
        'cholelithiasis': 'K80.20',
        'càlculs biliars': 'K80.20',
        'cálculos biliares': 'K80.20',
        'gallstones': 'K80.20',
        
        # Altres
        'cirrosi hepàtica': 'K74.60',
        'cirrosis hepática': 'K74.60',
        'hepatic cirrhosis': 'K74.60',
    }
    
    # Musculoesquelètic
    MUSCULOSKELETAL = {
        # Artritis
        'artritis reumatoide': 'M06.9',
        'rheumatoid arthritis': 'M06.9',
        'ar': 'M06.9',
        
        # Artròsi
        'artròsi': 'M19.90',
        'artrosis': 'M19.90',
        'osteoarthritis': 'M19.90',
        
        # Osteoporosi
        'osteoporosi': 'M81.0',
        'osteoporosis': 'M81.0',
        
        # Dolor
        'lumbàlgia': 'M54.5',
        'lumbalgia': 'M54.5',
        'low back pain': 'M54.5',
        'dolor lumbar': 'M54.5',
        'artràlgia': 'M25.50',
        'artralgia': 'M25.50',
        'arthralgia': 'M25.50',
        'dolor articular': 'M25.50',
    }
    
    # Renal
    RENAL = {
        # Insuficiència renal
        'insuficiència renal': 'N19',
        'insuficiencia renal': 'N19',
        'renal failure': 'N19',
        'kidney failure': 'N19',
        'insuficiència renal crònica': 'N18.9',
        'chronic kidney disease': 'N18.9',
        
        # Infecció urinària
        'infecció urinària': 'N39.0',
        'infección urinaria': 'N39.0',
        'urinary tract infection': 'N39.0',
        'itu': 'N39.0',
        'uti': 'N39.0',
    }
    
    # Hematològic
    HEMATOLOGICAL = {
        # Anèmia
        'anèmia': 'D64.9',
        'anemia': 'D64.9',
        'anemia': 'D64.9',
        'anèmia ferropènica': 'D50.9',
        'anemia ferropénica': 'D50.9',
        'iron deficiency anemia': 'D50.9',
    }
    
    # Oncològic
    ONCOLOGICAL = {
        # Càncer
        'càncer de pulmó': 'C34.90',
        'cáncer de pulmón': 'C34.90',
        'lung cancer': 'C34.90',
        'càncer de mama': 'C50.919',
        'cáncer de mama': 'C50.919',
        'breast cancer': 'C50.919',
        'càncer colorectal': 'C18.9',
        'cáncer colorrectal': 'C18.9',
        'colorectal cancer': 'C18.9',
    }
    
    # Psiquiàtric
    PSYCHIATRIC = {
        # Depressió
        'depressió': 'F32.9',
        'depresión': 'F32.9',
        'depression': 'F32.9',
        'trastorn depressiu': 'F32.9',
        
        # Ansietat
        'ansietat': 'F41.9',
        'ansiedad': 'F41.9',
        'anxiety': 'F41.9',
        'trastorn d\'ansietat': 'F41.9',
        
        # Trastorn bipolar
        'trastorn bipolar': 'F31.9',
        'trastorno bipolar': 'F31.9',
        'bipolar disorder': 'F31.9',
    }
    
    @classmethod
    def get_all_terms(cls) -> Dict[str, str]:
        """Retorna tots els termes combinats"""
        all_terms = {}
        all_terms.update(cls.CARDIOVASCULAR)
        all_terms.update(cls.RESPIRATORY)
        all_terms.update(cls.ENDOCRINE)
        all_terms.update(cls.NEUROLOGICAL)
        all_terms.update(cls.DIGESTIVE)
        all_terms.update(cls.MUSCULOSKELETAL)
        all_terms.update(cls.RENAL)
        all_terms.update(cls.HEMATOLOGICAL)
        all_terms.update(cls.ONCOLOGICAL)
        all_terms.update(cls.PSYCHIATRIC)
        return all_terms
    
    @classmethod
    def search(cls, term: str) -> Optional[str]:
        """
        Cerca un terme al diccionari amb múltiples estratègies
        
        Args:
            term: Terme a cercar (ca/es/en)
            
        Returns:
            Codi ICD-10 o None
        """
        all_terms = cls.get_all_terms()
        normalized = term.lower().strip()
        
        # 1. Cerca exacta
        if normalized in all_terms:
            return all_terms[normalized]
        
        # 2. Cerca amb paraules clau (millor matching)
        term_words = set(normalized.split())
        best_match = None
        best_score = 0
        
        for key, code in all_terms.items():
            key_words = set(key.split())
            common_words = term_words & key_words
            if common_words:
                score = len(common_words) / max(len(term_words), len(key_words))
                if score > best_score and score >= 0.5:
                    best_score = score
                    best_match = code
        
        if best_match:
            return best_match
        
        # 3. Cerca parcial (substring matching)
        for key, code in all_terms.items():
            if len(key) >= 8 and (key in normalized or normalized in key):
                return code
        
        return None
    
    @classmethod
    def get_stats(cls) -> Dict[str, int]:
        """Estadístiques del diccionari"""
        all_terms = cls.get_all_terms()
        return {
            'total_terms': len(all_terms),
            'cardiovascular': len(cls.CARDIOVASCULAR),
            'respiratory': len(cls.RESPIRATORY),
            'endocrine': len(cls.ENDOCRINE),
            'neurological': len(cls.NEUROLOGICAL),
            'digestive': len(cls.DIGESTIVE),
            'musculoskeletal': len(cls.MUSCULOSKELETAL),
            'renal': len(cls.RENAL),
            'hematological': len(cls.HEMATOLOGICAL),
            'oncological': len(cls.ONCOLOGICAL),
            'psychiatric': len(cls.PSYCHIATRIC)
        }


# Test
if __name__ == "__main__":
    stats = ICD10ExtendedLookup.get_stats()
    print("📊 ICD-10 Extended Lookup Statistics:")
    print(f"   Total terms: {stats['total_terms']}")
    for category, count in stats.items():
        if category != 'total_terms':
            print(f"   - {category.capitalize()}: {count}")
    
    # Test searches
    print("\n🔍 Test searches:")
    tests = [
        "infart miocardi",
        "diabetis tipus 2",
        "pneumònia bacteriana",
        "dolor toràcic"
    ]
    for test in tests:
        code = ICD10ExtendedLookup.search(test)
        print(f"   '{test}' → {code}")
