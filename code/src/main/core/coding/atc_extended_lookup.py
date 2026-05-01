"""
Extended ATC Lookup Dictionary
Diccionari ampli amb 100+ medicaments amb codis ATC
Inclou noms genèrics i comercials en ca/es/en
Basat en ATC/DDD Index 2024
"""

from typing import Dict, Optional


class ATCExtendedLookup:
    """
    Lookup table amb codis ATC per medicaments comuns
    Inclou noms genèrics i comercials en català, castellà i anglès
    """
    
    # ACE Inhibitors (C09AA)
    ACE_INHIBITORS = {
        'enalapril': 'C09AA02',
        'enalapril maleate': 'C09AA02',
        'renitec': 'C09AA02',
        'lisinopril': 'C09AA03',
        'prinivil': 'C09AA03',
        'zestril': 'C09AA03',
        'ramipril': 'C09AA05',
        'tritace': 'C09AA05',
        'perindopril': 'C09AA04',
        'coversyl': 'C09AA04',
        'captopril': 'C09AA01',
        'capoten': 'C09AA01',
    }
    
    # ARBs - Angiotensin II Receptor Blockers (C09CA)
    ARBS = {
        'losartan': 'C09CA01',
        'losartán': 'C09CA01',
        'cozaar': 'C09CA01',
        'valsartan': 'C09CA03',
        'valsartán': 'C09CA03',
        'diovan': 'C09CA03',
        'irbesartan': 'C09CA04',
        'irbesartán': 'C09CA04',
        'aprovel': 'C09CA04',
        'candesartan': 'C09CA06',
        'candesartán': 'C09CA06',
        'atacand': 'C09CA06',
        'telmisartan': 'C09CA07',
        'telmisartán': 'C09CA07',
        'micardis': 'C09CA07',
    }
    
    # Beta Blockers (C07AB)
    BETA_BLOCKERS = {
        'atenolol': 'C07AB03',
        'tenormin': 'C07AB03',
        'metoprolol': 'C07AB02',
        'seloken': 'C07AB02',
        'bisoprolol': 'C07AB07',
        'concor': 'C07AB07',
        'carvedilol': 'C07AG02',
        'coreg': 'C07AG02',
        'nebivolol': 'C07AB12',
        'lobivon': 'C07AB12',
        'propranolol': 'C07AA05',
        'sumial': 'C07AA05',
    }
    
    # Calcium Channel Blockers (C08CA)
    CALCIUM_BLOCKERS = {
        'amlodipine': 'C08CA01',
        'amlodipino': 'C08CA01',
        'norvasc': 'C08CA01',
        'nifedipine': 'C08CA05',
        'nifedipino': 'C08CA05',
        'adalat': 'C08CA05',
        'diltiazem': 'C08DB01',
        'verapamil': 'C08DA01',
        'verapamilo': 'C08DA01',
    }
    
    # Diuretics (C03)
    DIURETICS = {
        'furosemide': 'C03CA01',
        'furosemida': 'C03CA01',
        'lasix': 'C03CA01',
        'torasemide': 'C03CA04',
        'torasemida': 'C03CA04',
        'sutril': 'C03CA04',
        'hydrochlorothiazide': 'C03AA03',
        'hidroclorotiazida': 'C03AA03',
        'spironolactone': 'C03DA01',
        'espironolactona': 'C03DA01',
        'aldactone': 'C03DA01',
    }
    
    # Statins (C10AA)
    STATINS = {
        'atorvastatin': 'C10AA05',
        'atorvastatina': 'C10AA05',
        'lipitor': 'C10AA05',
        'zarator': 'C10AA05',
        'simvastatin': 'C10AA01',
        'simvastatina': 'C10AA01',
        'zocor': 'C10AA01',
        'rosuvastatin': 'C10AA07',
        'rosuvastatina': 'C10AA07',
        'crestor': 'C10AA07',
        'pravastatin': 'C10AA03',
        'pravastatina': 'C10AA03',
        'fluvastatin': 'C10AA04',
        'fluvastatina': 'C10AA04',
    }
    
    # Antidiabetics - Metformin (A10BA)
    ANTIDIABETICS = {
        'metformin': 'A10BA02',
        'metformina': 'A10BA02',
        'glucophage': 'A10BA02',
        'dianben': 'A10BA02',
        'glibenclamide': 'A10BB01',
        'glibenclamida': 'A10BB01',
        'gliclazide': 'A10BB09',
        'gliclazida': 'A10BB09',
        'diamicron': 'A10BB09',
        'sitagliptin': 'A10BH01',
        'sitagliptina': 'A10BH01',
        'januvia': 'A10BH01',
        'empagliflozin': 'A10BK03',
        'empagliflozina': 'A10BK03',
        'jardiance': 'A10BK03',
    }
    
    # Insulin (A10A)
    INSULIN = {
        'insulin': 'A10AB01',
        'insulina': 'A10AB01',
        'insulin glargine': 'A10AE04',
        'insulina glargina': 'A10AE04',
        'lantus': 'A10AE04',
        'insulin detemir': 'A10AE05',
        'insulina detemir': 'A10AE05',
        'levemir': 'A10AE05',
        'insulin aspart': 'A10AB05',
        'insulina aspart': 'A10AB05',
        'novorapid': 'A10AB05',
    }
    
    # Anticoagulants (B01A)
    ANTICOAGULANTS = {
        'acenocoumarol': 'B01AA07',
        'acenocumarol': 'B01AA07',
        'sintrom': 'B01AA07',
        'warfarin': 'B01AA03',
        'warfarina': 'B01AA03',
        'aldocumar': 'B01AA03',
        'apixaban': 'B01AF02',
        'apixabán': 'B01AF02',
        'eliquis': 'B01AF02',
        'rivaroxaban': 'B01AF01',
        'rivaroxabán': 'B01AF01',
        'xarelto': 'B01AF01',
        'dabigatran': 'B01AE07',
        'dabigatrán': 'B01AE07',
        'pradaxa': 'B01AE07',
    }
    
    # Antiplatelets (B01AC)
    ANTIPLATELETS = {
        'aspirin': 'B01AC06',
        'aspirina': 'B01AC06',
        'adiro': 'B01AC06',
        'acetylsalicylic acid': 'B01AC06',
        'clopidogrel': 'B01AC04',
        'plavix': 'B01AC04',
        'ticagrelor': 'B01AC24',
        'brilique': 'B01AC24',
    }
    
    # PPIs - Proton Pump Inhibitors (A02BC)
    PPIS = {
        'omeprazole': 'A02BC01',
        'omeprazol': 'A02BC01',
        'losec': 'A02BC01',
        'pantoprazole': 'A02BC02',
        'pantoprazol': 'A02BC02',
        'anagastra': 'A02BC02',
        'esomeprazole': 'A02BC05',
        'esomeprazol': 'A02BC05',
        'nexium': 'A02BC05',
        'lansoprazole': 'A02BC03',
        'lansoprazol': 'A02BC03',
        'rabeprazole': 'A02BC04',
        'rabeprazol': 'A02BC04',
    }
    
    # Antibiotics - Penicillins (J01C)
    ANTIBIOTICS_PENICILLIN = {
        'amoxicillin': 'J01CA04',
        'amoxicil·lina': 'J01CA04',
        'amoxicilina': 'J01CA04',
        'clamoxyl': 'J01CA04',
        'amoxicillin clavulanate': 'J01CR02',
        'amoxicil·lina clavulànic': 'J01CR02',
        'augmentine': 'J01CR02',
        'penicillin': 'J01CE01',
        'penicil·lina': 'J01CE01',
        'penicilina': 'J01CE01',
    }
    
    # Antibiotics - Macrolides (J01FA)
    ANTIBIOTICS_MACROLIDE = {
        'azithromycin': 'J01FA10',
        'azitromicina': 'J01FA10',
        'zitromax': 'J01FA10',
        'clarithromycin': 'J01FA09',
        'claritromicina': 'J01FA09',
        'klacid': 'J01FA09',
        'erythromycin': 'J01FA01',
        'eritromicina': 'J01FA01',
    }
    
    # Antibiotics - Quinolones (J01MA)
    ANTIBIOTICS_QUINOLONE = {
        'ciprofloxacin': 'J01MA02',
        'ciprofloxacino': 'J01MA02',
        'cipro': 'J01MA02',
        'levofloxacin': 'J01MA12',
        'levofloxacino': 'J01MA12',
        'tavanic': 'J01MA12',
        'moxifloxacin': 'J01MA14',
        'moxifloxacino': 'J01MA14',
    }
    
    # Bronchodilators (R03)
    BRONCHODILATORS = {
        'salbutamol': 'R03AC02',
        'ventolin': 'R03AC02',
        'terbutaline': 'R03AC03',
        'terbutalina': 'R03AC03',
        'formoterol': 'R03AC13',
        'salmeterol': 'R03AC12',
        'tiotropium': 'R03BB04',
        'spiriva': 'R03BB04',
    }
    
    # Corticosteroids (H02AB)
    CORTICOSTEROIDS = {
        'prednisone': 'H02AB07',
        'prednisona': 'H02AB07',
        'dacortin': 'H02AB07',
        'prednisolone': 'H02AB06',
        'prednisolona': 'H02AB06',
        'methylprednisolone': 'H02AB04',
        'metilprednisolona': 'H02AB04',
        'urbason': 'H02AB04',
        'dexamethasone': 'H02AB02',
        'dexametasona': 'H02AB02',
    }
    
    # Analgesics - NSAIDs (M01A)
    NSAIDS = {
        'ibuprofen': 'M01AE01',
        'ibuprofè': 'M01AE01',
        'ibuprofeno': 'M01AE01',
        'espidifen': 'M01AE01',
        'naproxen': 'M01AE02',
        'naproxè': 'M01AE02',
        'naproxeno': 'M01AE02',
        'diclofenac': 'M01AB05',
        'voltaren': 'M01AB05',
        'ketoprofen': 'M01AE03',
        'ketoprofè': 'M01AE03',
        'ketoprofeno': 'M01AE03',
    }
    
    # Analgesics - Paracetamol (N02BE)
    ANALGESICS = {
        'paracetamol': 'N02BE01',
        'acetaminophen': 'N02BE01',
        'gelocatil': 'N02BE01',
        'tramadol': 'N02AX02',
        'adolonta': 'N02AX02',
        'codeine': 'N02AA59',
        'codeïna': 'N02AA59',
        'codeina': 'N02AA59',
    }
    
    # Antidepressants - SSRIs (N06AB)
    ANTIDEPRESSANTS = {
        'sertraline': 'N06AB06',
        'sertralina': 'N06AB06',
        'besitran': 'N06AB06',
        'fluoxetine': 'N06AB03',
        'fluoxetina': 'N06AB03',
        'prozac': 'N06AB03',
        'paroxetine': 'N06AB05',
        'paroxetina': 'N06AB05',
        'seroxat': 'N06AB05',
        'escitalopram': 'N06AB10',
        'cipralex': 'N06AB10',
    }
    
    # Anxiolytics - Benzodiazepines (N05BA)
    ANXIOLYTICS = {
        'diazepam': 'N05BA01',
        'valium': 'N05BA01',
        'lorazepam': 'N05BA06',
        'orfidal': 'N05BA06',
        'alprazolam': 'N05BA12',
        'trankimazin': 'N05BA12',
        'bromazepam': 'N05BA08',
        'lexatin': 'N05BA08',
    }
    
    @classmethod
    def get_all_terms(cls) -> Dict[str, str]:
        """Retorna tots els termes combinats"""
        all_terms = {}
        all_terms.update(cls.ACE_INHIBITORS)
        all_terms.update(cls.ARBS)
        all_terms.update(cls.BETA_BLOCKERS)
        all_terms.update(cls.CALCIUM_BLOCKERS)
        all_terms.update(cls.DIURETICS)
        all_terms.update(cls.STATINS)
        all_terms.update(cls.ANTIDIABETICS)
        all_terms.update(cls.INSULIN)
        all_terms.update(cls.ANTICOAGULANTS)
        all_terms.update(cls.ANTIPLATELETS)
        all_terms.update(cls.PPIS)
        all_terms.update(cls.ANTIBIOTICS_PENICILLIN)
        all_terms.update(cls.ANTIBIOTICS_MACROLIDE)
        all_terms.update(cls.ANTIBIOTICS_QUINOLONE)
        all_terms.update(cls.BRONCHODILATORS)
        all_terms.update(cls.CORTICOSTEROIDS)
        all_terms.update(cls.NSAIDS)
        all_terms.update(cls.ANALGESICS)
        all_terms.update(cls.ANTIDEPRESSANTS)
        all_terms.update(cls.ANXIOLYTICS)
        return all_terms
    
    @classmethod
    def search(cls, term: str) -> Optional[str]:
        """
        Cerca un medicament al diccionari amb múltiples estratègies
        
        Args:
            term: Nom del medicament (ca/es/en, genèric o comercial)
            
        Returns:
            Codi ATC o None
        """
        all_terms = cls.get_all_terms()
        normalized = term.lower().strip()
        
        # Eliminar dosis comunes del terme
        # Ex: "enalapril 10mg" → "enalapril"
        for dose_pattern in [' mg', ' g', ' ml', ' mcg', ' ui', '/12h', '/24h', '/8h']:
            normalized = normalized.replace(dose_pattern, '')
        normalized = normalized.strip()
        
        # 1. Cerca exacta
        if normalized in all_terms:
            return all_terms[normalized]
        
        # 2. Cerca amb paraules clau
        term_words = set(normalized.split())
        best_match = None
        best_score = 0
        
        for key, code in all_terms.items():
            key_words = set(key.split())
            common_words = term_words & key_words
            if common_words:
                score = len(common_words) / max(len(term_words), len(key_words))
                if score > best_score and score >= 0.7:  # Threshold més alt per medicaments
                    best_score = score
                    best_match = code
        
        if best_match:
            return best_match
        
        # 3. Cerca parcial (substring matching)
        for key, code in all_terms.items():
            if len(key) >= 5 and (key in normalized or normalized in key):
                return code
        
        return None
    
    @classmethod
    def get_stats(cls) -> Dict[str, int]:
        """Estadístiques del diccionari"""
        all_terms = cls.get_all_terms()
        return {
            'total_terms': len(all_terms),
            'ace_inhibitors': len(cls.ACE_INHIBITORS),
            'arbs': len(cls.ARBS),
            'beta_blockers': len(cls.BETA_BLOCKERS),
            'calcium_blockers': len(cls.CALCIUM_BLOCKERS),
            'diuretics': len(cls.DIURETICS),
            'statins': len(cls.STATINS),
            'antidiabetics': len(cls.ANTIDIABETICS),
            'insulin': len(cls.INSULIN),
            'anticoagulants': len(cls.ANTICOAGULANTS),
            'antiplatelets': len(cls.ANTIPLATELETS),
            'ppis': len(cls.PPIS),
            'antibiotics_penicillin': len(cls.ANTIBIOTICS_PENICILLIN),
            'antibiotics_macrolide': len(cls.ANTIBIOTICS_MACROLIDE),
            'antibiotics_quinolone': len(cls.ANTIBIOTICS_QUINOLONE),
            'bronchodilators': len(cls.BRONCHODILATORS),
            'corticosteroids': len(cls.CORTICOSTEROIDS),
            'nsaids': len(cls.NSAIDS),
            'analgesics': len(cls.ANALGESICS),
            'antidepressants': len(cls.ANTIDEPRESSANTS),
            'anxiolytics': len(cls.ANXIOLYTICS)
        }


# Test
if __name__ == "__main__":
    stats = ATCExtendedLookup.get_stats()
    print("📊 ATC Extended Lookup Statistics:")
    print(f"   Total terms: {stats['total_terms']}")
    for category, count in stats.items():
        if category != 'total_terms':
            print(f"   - {category.replace('_', ' ').capitalize()}: {count}")
    
    # Test searches
    print("\n🔍 Test searches:")
    tests = [
        "enalapril 10mg",
        "adiro",
        "omeprazol 20mg",
        "augmentine",
        "ventolin"
    ]
    for test in tests:
        code = ATCExtendedLookup.search(test)
        print(f"   '{test}' → {code}")
