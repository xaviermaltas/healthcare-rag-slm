"""
Specialty Detector
Detecta l'especialitat mèdica a partir del context clínic
"""

import re
from typing import Optional, List, Dict
from dataclasses import dataclass


@dataclass
class SpecialtyMatch:
    """Resultat de detecció d'especialitat"""
    specialty: str
    confidence: float
    matched_terms: List[str]


class SpecialtyDetector:
    """
    Detecta l'especialitat mèdica més probable a partir del context clínic
    
    Utilitza:
    - Keywords específiques de cada especialitat
    - Diagnòstics típics
    - Procediments característics
    - Medicacions específiques
    """
    
    # Diccionari d'especialitats amb keywords associades
    SPECIALTY_KEYWORDS = {
        "Cardiologia": {
            "diagnoses": [
                "infart", "iamcest", "iamsest", "angina", "insuficiència cardíaca",
                "insuficiencia cardíaca", "fibril·lació auricular", "fibrilación auricular",
                "miocardi", "coronària", "coronaria", "síndrome coronari", "síndrome coronario",
                "arítmia", "arritmia", "taquicàrdia", "taquicardia", "bradicàrdia", "bradicardia",
                "hipertensió arterial", "hipertensión arterial", "cardiopatia", "valvulopatia",
                "estenosi aòrtica", "estenosis aórtica", "insuficiència mitral"
            ],
            "procedures": [
                "cateterisme", "cateterismo", "angioplastia", "stent", "coronariografia",
                "ecocardiograma", "holter", "ergometria", "marcapassos", "desfibril·lador"
            ],
            "medications": [
                "betabloqueant", "betabloqueante", "ieca", "ara ii", "estatina",
                "antiagregant", "anticoagulant", "diürètic", "diurético", "nitroglicerina",
                "bisoprolol", "enalapril", "ramipril", "atorvastatina", "simvastatina",
                "clopidogrel", "acenocumarol", "warfarina", "furosemida"
            ],
            "anatomy": [
                "cor", "corazón", "cardíac", "cardíaco", "miocardi", "ventricle",
                "ventrículo", "aurícula", "vàlvula", "válvula", "aorta", "coronària"
            ]
        },
        "Endocrinologia": {
            "diagnoses": [
                "diabetis", "diabetes", "hiperglucèmia", "hiperglucemia", "hipoglucèmia",
                "cetoacidosi", "cetoacidosis", "hiperosmolar", "tiroide", "tiroides",
                "hipertiroidisme", "hipertiroidismo", "hipotiroidisme", "hipotiroidismo",
                "obesitat", "obesidad", "síndrome metabòlic", "síndrome metabólico",
                "dislipèmia", "dislipemia", "hipercolesterolèmia"
            ],
            "procedures": [
                "glucèmia", "glucemia", "hemoglobina glicada", "hba1c", "insulina",
                "bomba d'insulina", "monitorització contínua glucosa", "tirotropina", "tsh"
            ],
            "medications": [
                "metformina", "insulina", "glibenclamida", "gliclazida", "sitagliptina",
                "empagliflozina", "liraglutida", "levotiroxina", "metimazol", "propiltiouracil"
            ],
            "anatomy": [
                "pàncrees", "páncreas", "tiroide", "tiroides", "suprarrenal", "hipòfisi"
            ]
        },
        "Neurologia": {
            "diagnoses": [
                "ictus", "accident cerebrovascular", "acv", "acvi", "hemorràgia cerebral",
                "hemorragia cerebral", "isquèmia cerebral", "isquemia cerebral", "epilèpsia", "epilepsia",
                "parkinson", "alzheimer", "demència", "demencia", "esclerosi múltiple",
                "esclerosis múltiple", "migranya", "cefalea", "meningitis", "encefalitis",
                "neuropatia", "miastènia", "miastenia", "nihss"
            ],
            "procedures": [
                "tac cranial", "tac cerebral", "ressonància magnètica cerebral",
                "resonancia magnética cerebral", "punció lumbar", "punción lumbar", 
                "electroencefalograma", "eeg", "doppler transcranial", "doppler de troncs",
                "trombòlisi", "trombólisis", "trombolisi"
            ],
            "medications": [
                "levetiracetam", "valproat", "carbamazepina", "fenitoïna", "levodopa",
                "carbidopa", "donepezil", "rivastigmina", "gabapentina", "pregabalina"
            ],
            "anatomy": [
                "cervell", "cerebro", "cerebral", "neurològic", "neurológico",
                "hemicòs", "hemicuerpo", "disàrtria", "disartria", "afàsia", "afasia",
                "debilitat", "debilidad", "paràlisi", "parálisis", "hemiparàlisi", "hemiparálisis"
            ]
        },
        "Medicina Interna": {
            "diagnoses": [
                "pneumònia", "neumonía", "bronquitis", "epoc", "asma", "insuficiència renal",
                "insuficiencia renal", "infecció urinària", "infección urinaria", "pielonefritis",
                "sèpsia", "sepsis", "anèmia", "anemia", "trombosi", "trombosis",
                "embòlia pulmonar", "embolia pulmonar", "cirrosi", "hepatitis"
            ],
            "procedures": [
                "radiografia toràcica", "radiografía torácica", "gasometria",
                "toracocentesi", "paracentesi", "broncoscòpia", "broncoscopia"
            ],
            "medications": [
                "amoxicil·lina", "amoxicilina", "levofloxacino", "azitromicina",
                "omeprazol", "pantoprazol", "paracetamol", "ibuprofè", "ibuprofeno"
            ],
            "anatomy": [
                "pulmonar", "respiratori", "respiratorio", "renal", "hepàtic", "hepático"
            ]
        },
        "Cirurgia": {
            "diagnoses": [
                "apendicitis", "colecistitis", "pancreatitis aguda", "oclusió intestinal",
                "oclusión intestinal", "peritonitis", "hèrnia", "hernia", "isquèmia mesentèrica",
                "abdomen agut", "abdomen agudo", "traumatisme", "traumatismo", "fractura"
            ],
            "procedures": [
                "laparotomia", "laparoscòpia", "laparoscopia", "apendicectomia",
                "colecistectomia", "herniorràfia", "drenatge", "sutura", "amputació"
            ],
            "medications": [
                "morfina", "fentanil", "tramadol", "antibiòtic", "antibiótico"
            ],
            "anatomy": [
                "abdominal", "quirúrgic", "quirúrgico", "postoperatori", "postoperatorio"
            ]
        }
    }
    
    @classmethod
    def detect_specialty(
        cls,
        patient_context: str = "",
        admission_reason: str = "",
        procedures: List[str] = None,
        medications: List[str] = None,
        explicit_specialty: Optional[str] = None
    ) -> SpecialtyMatch:
        """
        Detecta l'especialitat més probable
        
        Args:
            patient_context: Context del pacient
            admission_reason: Motiu d'ingrés
            procedures: Llista de procediments
            medications: Llista de medicacions
            explicit_specialty: Especialitat explícita (prioritària)
            
        Returns:
            SpecialtyMatch amb l'especialitat detectada
        """
        # Si hi ha especialitat explícita, retornar-la directament
        if explicit_specialty:
            # Normalitzar nom d'especialitat
            normalized = cls._normalize_specialty(explicit_specialty)
            if normalized in cls.SPECIALTY_KEYWORDS:
                return SpecialtyMatch(
                    specialty=normalized,
                    confidence=1.0,
                    matched_terms=[explicit_specialty]
                )
        
        # Combinar tot el text per analitzar
        # Donar més pes al motiu d'ingrés (símptomes aguts)
        admission_text = (admission_reason or "") * 2  # Duplicar per donar més pes
        full_text = " ".join([
            patient_context or "",
            admission_text,
            " ".join(procedures or []),
            " ".join(medications or [])
        ]).lower()
        
        # Comptar matches per cada especialitat
        specialty_scores = {}
        specialty_matches = {}
        
        for specialty, keywords in cls.SPECIALTY_KEYWORDS.items():
            score = 0
            matched_terms = []
            
            # Buscar keywords de diagnòstics (pes: 3)
            for keyword in keywords["diagnoses"]:
                if keyword.lower() in full_text:
                    score += 3
                    matched_terms.append(keyword)
            
            # Buscar keywords de procediments (pes: 2)
            for keyword in keywords["procedures"]:
                if keyword.lower() in full_text:
                    score += 2
                    matched_terms.append(keyword)
            
            # Buscar keywords de medicacions (pes: 1.5)
            for keyword in keywords["medications"]:
                if keyword.lower() in full_text:
                    score += 1.5
                    matched_terms.append(keyword)
            
            # Buscar keywords anatòmiques (pes: 1)
            for keyword in keywords["anatomy"]:
                if keyword.lower() in full_text:
                    score += 1
                    matched_terms.append(keyword)
            
            if score > 0:
                specialty_scores[specialty] = score
                specialty_matches[specialty] = matched_terms
        
        # Si no hi ha matches, retornar Medicina Interna per defecte
        if not specialty_scores:
            return SpecialtyMatch(
                specialty="Medicina Interna",
                confidence=0.3,
                matched_terms=[]
            )
        
        # Trobar l'especialitat amb més score
        best_specialty = max(specialty_scores, key=specialty_scores.get)
        max_score = specialty_scores[best_specialty]
        
        # Calcular confidence (normalitzat entre 0 i 1)
        # Score típic: 3-15 punts
        confidence = min(max_score / 15.0, 1.0)
        
        return SpecialtyMatch(
            specialty=best_specialty,
            confidence=confidence,
            matched_terms=specialty_matches[best_specialty][:5]  # Top 5 matches
        )
    
    @staticmethod
    def _normalize_specialty(specialty: str) -> str:
        """Normalitza el nom de l'especialitat"""
        specialty_map = {
            "cardiologia": "Cardiologia",
            "cardiology": "Cardiologia",
            "endocrinologia": "Endocrinologia",
            "endocrinology": "Endocrinologia",
            "neurologia": "Neurologia",
            "neurology": "Neurologia",
            "medicina interna": "Medicina Interna",
            "internal medicine": "Medicina Interna",
            "cirurgia": "Cirurgia",
            "surgery": "Cirurgia",
        }
        return specialty_map.get(specialty.lower(), specialty.title())
    
    @classmethod
    def get_related_specialties(cls, specialty: str) -> List[str]:
        """
        Retorna especialitats relacionades per fallback
        
        Args:
            specialty: Especialitat principal
            
        Returns:
            Llista d'especialitats relacionades
        """
        related = {
            "Cardiologia": ["Medicina Interna", "Cirurgia"],
            "Endocrinologia": ["Medicina Interna"],
            "Neurologia": ["Medicina Interna"],
            "Medicina Interna": ["Cardiologia", "Endocrinologia", "Neurologia"],
            "Cirurgia": ["Medicina Interna"]
        }
        return related.get(specialty, ["Medicina Interna"])
