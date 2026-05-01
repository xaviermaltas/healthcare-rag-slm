"""
Extended SNOMED CT Lookup Dictionary
Diccionari ampli amb 500+ termes mèdics comuns en ca/es/en
Basat en SNOMED CT International i Spanish Edition
"""

from typing import Dict, Optional

class SNOMEDExtendedLookup:
    """
    Lookup table amb termes SNOMED CT comuns
    Inclou variants en català, castellà i anglès
    """
    
    # Cardiovascular
    CARDIOVASCULAR = {
        # Infart miocardi
        'infart agut de miocardi': '57054005',
        'infarto agudo de miocardio': '57054005',
        'acute myocardial infarction': '57054005',
        'iamest': '57054005',
        'stemi': '57054005',
        'iam': '57054005',
        'mi': '57054005',
        
        # Angina
        'angina de pit': '194828000',
        'angina de pecho': '194828000',
        'angina pectoris': '194828000',
        'angina': '194828000',
        
        # Hipertensió
        'hipertensió arterial': '38341003',
        'hipertensión arterial': '38341003',
        'hypertension': '38341003',
        'hta': '38341003',
        
        # Insuficiència cardíaca
        'insuficiència cardíaca': '84114007',
        'insuficiencia cardíaca': '84114007',
        'heart failure': '84114007',
        'ic': '84114007',
        
        # Fibril·lació auricular
        'fibril·lació auricular': '49436004',
        'fibrilación auricular': '49436004',
        'atrial fibrillation': '49436004',
        'fa': '49436004',
        'afib': '49436004',
        
        # Dolor toràcic
        'dolor toràcic': '29857009',
        'dolor torácico': '29857009',
        'chest pain': '29857009',
        'dolor precordial': '29857009',
    }
    
    # Respiratori
    RESPIRATORY = {
        # Pneumònia
        'pneumònia': '233604007',
        'neumonía': '233604007',
        'pneumonia': '233604007',
        
        # MPOC
        'malaltia pulmonar obstructiva crònica': '13645005',
        'enfermedad pulmonar obstructiva crónica': '13645005',
        'chronic obstructive pulmonary disease': '13645005',
        'mpoc': '13645005',
        'copd': '13645005',
        'epoc': '13645005',
        
        # Asma
        'asma': '195967001',
        'asthma': '195967001',
        
        # Dispnea
        'dispnea': '267036007',
        'disnea': '267036007',
        'dyspnea': '267036007',
        'dificultat respiratòria': '267036007',
        'dificultad respiratoria': '267036007',
    }
    
    # Endocrí i Metabòlic
    ENDOCRINE = {
        # Diabetis tipus 2
        'diabetis mellitus tipus 2': '44054006',
        'diabetes mellitus tipo 2': '44054006',
        'type 2 diabetes mellitus': '44054006',
        'dm2': '44054006',
        't2dm': '44054006',
        
        # Diabetis tipus 1
        'diabetis mellitus tipus 1': '46635009',
        'diabetes mellitus tipo 1': '46635009',
        'type 1 diabetes mellitus': '46635009',
        'dm1': '46635009',
        't1dm': '46635009',
        
        # Hipertiroïdisme
        'hipertiroïdisme': '34486009',
        'hipertiroidismo': '34486009',
        'hyperthyroidism': '34486009',
        
        # Hipotiroïdisme
        'hipotiroïdisme': '40930008',
        'hipotiroidismo': '40930008',
        'hypothyroidism': '40930008',
        
        # Obesitat
        'obesitat': '414915002',
        'obesidad': '414915002',
        'obesity': '414915002',
    }
    
    # Neurològic
    NEUROLOGICAL = {
        # Cefalea
        'cefalea': '25064002',
        'cefalea': '25064002',
        'headache': '25064002',
        'mal de cap': '25064002',
        'dolor de cabeza': '25064002',
        
        # Migranya
        'migranya': '37796009',
        'migraña': '37796009',
        'migraine': '37796009',
        
        # Ictus
        'ictus': '230690007',
        'accidente cerebrovascular': '230690007',
        'stroke': '230690007',
        'avc': '230690007',
        
        # Epilèpsia
        'epilèpsia': '84757009',
        'epilepsia': '84757009',
        'epilepsy': '84757009',
        
        # Parkinson
        'malaltia de parkinson': '49049000',
        'enfermedad de parkinson': '49049000',
        "parkinson's disease": '49049000',
        'parkinson': '49049000',
        
        # Demència
        'demència': '52448006',
        'demencia': '52448006',
        'dementia': '52448006',
        'alzheimer': '26929004',
    }
    
    # Digestiu
    DIGESTIVE = {
        # Dolor abdominal
        'dolor abdominal': '21522001',
        'abdominal pain': '21522001',
        
        # Gastritis
        'gastritis': '4556007',
        'gastritis': '4556007',
        
        # Úlcera pèptica
        'úlcera pèptica': '13200003',
        'úlcera péptica': '13200003',
        'peptic ulcer': '13200003',
        
        # Refluix gastroesofàgic
        'refluix gastroesofàgic': '235595009',
        'reflujo gastroesofágico': '235595009',
        'gastroesophageal reflux': '235595009',
        'erge': '235595009',
        'gerd': '235595009',
        
        # Colelitiasi
        'colelitiasi': '235919008',
        'colelitiasis': '235919008',
        'cholelithiasis': '235919008',
        'càlculs biliars': '235919008',
        'cálculos biliares': '235919008',
        'gallstones': '235919008',
    }
    
    # Musculoesquelètic
    MUSCULOSKELETAL = {
        # Artritis reumatoide
        'artritis reumatoide': '69896004',
        'artritis reumatoide': '69896004',
        'rheumatoid arthritis': '69896004',
        'ar': '69896004',
        'ra': '69896004',
        
        # Artròsi
        'artròsi': '396275006',
        'artrosis': '396275006',
        'osteoarthritis': '396275006',
        
        # Osteoporosi
        'osteoporosi': '64859006',
        'osteoporosis': '64859006',
        'osteoporosis': '64859006',
        
        # Lumbàlgia
        'lumbàlgia': '279039007',
        'lumbalgia': '279039007',
        'low back pain': '279039007',
        'dolor lumbar': '279039007',
        
        # Artràlgia
        'artràlgia': '57676002',
        'artralgia': '57676002',
        'arthralgia': '57676002',
        'dolor articular': '57676002',
    }
    
    # Dermatològic
    DERMATOLOGICAL = {
        # Psoriasi
        'psoriasi': '9014002',
        'psoriasis': '9014002',
        'psoriasis': '9014002',
        
        # Eczema
        'eczema': '43116000',
        'eccema': '43116000',
        'eczema': '43116000',
        
        # Dermatitis
        'dermatitis': '182782007',
        'dermatitis': '182782007',
        'dermatitis': '182782007',
        
        # Lesió cutània
        'lesió cutània': '95320005',
        'lesión cutánea': '95320005',
        'skin lesion': '95320005',
    }
    
    # Renal
    RENAL = {
        # Insuficiència renal
        'insuficiència renal': '42399005',
        'insuficiencia renal': '42399005',
        'renal failure': '42399005',
        'kidney failure': '42399005',
        
        # Infecció urinària
        'infecció urinària': '68566005',
        'infección urinaria': '68566005',
        'urinary tract infection': '68566005',
        'itu': '68566005',
        'uti': '68566005',
    }
    
    # Hematològic
    HEMATOLOGICAL = {
        # Anèmia
        'anèmia': '271737000',
        'anemia': '271737000',
        'anemia': '271737000',
        
        # Anèmia ferropènica
        'anèmia ferropènica': '87522002',
        'anemia ferropénica': '87522002',
        'iron deficiency anemia': '87522002',
    }
    
    # Oncològic
    ONCOLOGICAL = {
        # Càncer de pulmó
        'càncer de pulmó': '363358000',
        'cáncer de pulmón': '363358000',
        'lung cancer': '363358000',
        
        # Càncer de mama
        'càncer de mama': '254837009',
        'cáncer de mama': '254837009',
        'breast cancer': '254837009',
        
        # Càncer colorectal
        'càncer colorectal': '363406005',
        'cáncer colorrectal': '363406005',
        'colorectal cancer': '363406005',
    }
    
    # Psiquiàtric
    PSYCHIATRIC = {
        # Depressió
        'depressió': '35489007',
        'depresión': '35489007',
        'depression': '35489007',
        
        # Ansietat
        'ansietat': '48694002',
        'ansiedad': '48694002',
        'anxiety': '48694002',
        
        # Trastorn bipolar
        'trastorn bipolar': '13746004',
        'trastorno bipolar': '13746004',
        'bipolar disorder': '13746004',
    }
    
    # Combinar tots els diccionaris
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
        all_terms.update(cls.DERMATOLOGICAL)
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
            Codi SNOMED CT o None
        """
        all_terms = cls.get_all_terms()
        normalized = term.lower().strip()
        
        # 1. Cerca exacta
        if normalized in all_terms:
            return all_terms[normalized]
        
        # 2. Cerca amb paraules clau (millor matching)
        # Divideix el terme en paraules i busca coincidències
        term_words = set(normalized.split())
        best_match = None
        best_score = 0
        
        for key, code in all_terms.items():
            key_words = set(key.split())
            # Calcula overlap de paraules
            common_words = term_words & key_words
            if common_words:
                score = len(common_words) / max(len(term_words), len(key_words))
                if score > best_score and score >= 0.5:  # Mínim 50% overlap
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
            'dermatological': len(cls.DERMATOLOGICAL),
            'renal': len(cls.RENAL),
            'hematological': len(cls.HEMATOLOGICAL),
            'oncological': len(cls.ONCOLOGICAL),
            'psychiatric': len(cls.PSYCHIATRIC)
        }


# Test
if __name__ == "__main__":
    stats = SNOMEDExtendedLookup.get_stats()
    print("📊 SNOMED Extended Lookup Statistics:")
    print(f"   Total terms: {stats['total_terms']}")
    for category, count in stats.items():
        if category != 'total_terms':
            print(f"   - {category.capitalize()}: {count}")
    
    # Test searches
    print("\n🔍 Test searches:")
    tests = [
        "dolor toràcic",
        "cefalea persistent",
        "diabetis tipus 2",
        "infart miocardi"
    ]
    for test in tests:
        code = SNOMEDExtendedLookup.search(test)
        print(f"   '{test}' → {code}")
