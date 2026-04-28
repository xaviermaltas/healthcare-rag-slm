"""
Discharge Summary Parser
Extreu informació estructurada d'informes d'alta hospitalària generats per LLM
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ExtractedDiagnosis:
    """Diagnòstic extret amb codis i descripció"""
    description: str
    snomed_code: Optional[str] = None
    icd10_code: Optional[str] = None
    is_primary: bool = False


@dataclass
class ExtractedMedication:
    """Medicació extreta amb codis i posologia"""
    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    route: Optional[str] = None
    atc_code: Optional[str] = None


@dataclass
class ExtractedFollowUp:
    """Recomanació de seguiment"""
    description: str
    specialty: Optional[str] = None
    timeframe: Optional[str] = None


class DischargeSummaryParser:
    """
    Parser per extreure informació estructurada d'informes d'alta
    
    Funcionalitats:
    - Extracció de seccions de l'informe
    - Extracció de diagnòstics amb codis SNOMED CT i ICD-10
    - Extracció de medicacions amb codis ATC
    - Extracció de recomanacions de seguiment
    - Validació de format de codis
    """
    
    # Patterns per codis mèdics
    SNOMED_PATTERN = r'(?:SNOMED|Codi SNOMED|SNOMED CT)[:\s]*(\d{6,18})'
    ICD10_PATTERN = r'(?:ICD-10|ICD10|Codi ICD)[:\s]*([A-Z]\d{2}(?:\.\d{1,2})?)'
    ATC_PATTERN = r'(?:ATC|Codi ATC)[:\s]*([A-Z]\d{2}[A-Z]{2}\d{2})'
    
    # Patterns alternatius (codis solts en el text)
    SNOMED_LOOSE_PATTERN = r'\b(\d{6,18})\b'
    ICD10_LOOSE_PATTERN = r'\b([A-Z]\d{2}(?:\.\d{1,2})?)\b'
    ATC_LOOSE_PATTERN = r'\b([A-Z]\d{2}[A-Z]{2}\d{2})\b'
    
    # Patterns per medicacions
    MEDICATION_PATTERN = r'[-•*]\s*([A-Z][a-zà-ú]+(?:\s+[A-Z][a-zà-ú]+)*)\s+(\d+(?:\.\d+)?)\s*(?:mg|g|ml|mcg|UI)(?:/(\d+h|24h|dia|día))?'
    
    # Patterns per seccions (multiidioma)
    SECTION_PATTERNS = {
        'patient_data': r'(?:1\.|DADES DEL PACIENT|DATOS DEL PACIENTE)',
        'admission_reason': r'(?:2\.|MOTIU D\'INGRÉS|MOTIVO DE INGRESO)',
        'main_diagnosis': r'(?:3\.|DIAGNÒSTIC PRINCIPAL|DIAGNÓSTICO PRINCIPAL)',
        'secondary_diagnoses': r'(?:4\.|DIAGNÒSTICS SECUNDARIS|DIAGNÓSTICOS SECUNDARIOS)',
        'procedures': r'(?:5\.|PROCEDIMENTS REALITZATS|PROCEDIMIENTOS REALIZADOS)',
        'treatment': r'(?:6\.|TRACTAMENT I MEDICACIÓ|TRATAMIENTO Y MEDICACIÓN)',
        'clinical_evolution': r'(?:7\.|EVOLUCIÓ CLÍNICA|EVOLUCIÓN CLÍNICA)',
        'follow_up': r'(?:8\.|RECOMANACIONS DE SEGUIMENT|RECOMENDACIONES DE SEGUIMIENTO)',
        'contraindications': r'(?:9\.|CONTRAINDICACIONS|CONTRAINDICACIONES)',
    }
    
    @classmethod
    def extract_sections(cls, text: str) -> Dict[str, str]:
        """
        Extreu les seccions de l'informe
        
        Args:
            text: Text complet de l'informe
            
        Returns:
            Dict amb les seccions extretes
        """
        sections = {}
        
        # Ordenar patterns per posició en el text
        section_positions = []
        for section_name, pattern in cls.SECTION_PATTERNS.items():
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                section_positions.append((match.start(), section_name, pattern))
        
        section_positions.sort()
        
        # Extreure text entre seccions
        for i, (start_pos, section_name, pattern) in enumerate(section_positions):
            # Trobar on acaba aquesta secció (inici de la següent o final del text)
            if i < len(section_positions) - 1:
                end_pos = section_positions[i + 1][0]
            else:
                end_pos = len(text)
            
            # Extreure text de la secció
            section_text = text[start_pos:end_pos].strip()
            
            # Eliminar el header de la secció
            section_text = re.sub(pattern, '', section_text, count=1, flags=re.IGNORECASE | re.MULTILINE).strip()
            
            sections[section_name] = section_text
        
        return sections
    
    @classmethod
    def extract_diagnoses(cls, text: str, section_text: Optional[str] = None) -> List[ExtractedDiagnosis]:
        """
        Extreu diagnòstics amb codis del text
        
        Args:
            text: Text complet de l'informe
            section_text: Text específic de la secció de diagnòstics (opcional)
            
        Returns:
            Llista de diagnòstics extrets
        """
        diagnoses = []
        search_text = section_text if section_text else text
        
        # Buscar diagnòstic principal amb codi
        main_diag_pattern = r'(?:DIAGNÒSTIC PRINCIPAL|DIAGNÓSTICO PRINCIPAL)[:\s]*\n([^\n]+)'
        main_match = re.search(main_diag_pattern, search_text, re.IGNORECASE | re.MULTILINE)
        
        if main_match:
            diag_text = main_match.group(1).strip()
            
            # Extreure codis
            snomed_match = re.search(cls.SNOMED_PATTERN, diag_text, re.IGNORECASE)
            icd10_match = re.search(cls.ICD10_PATTERN, diag_text, re.IGNORECASE)
            
            # Netejar descripció (eliminar línies de codi)
            description = re.sub(r'Codi.*', '', diag_text, flags=re.IGNORECASE).strip()
            description = re.sub(r'(?:SNOMED|ICD).*', '', description, flags=re.IGNORECASE).strip()
            
            if description:
                diagnoses.append(ExtractedDiagnosis(
                    description=description,
                    snomed_code=snomed_match.group(1) if snomed_match else None,
                    icd10_code=icd10_match.group(1) if icd10_match else None,
                    is_primary=True
                ))
        
        # Buscar diagnòstics secundaris
        secondary_pattern = r'(?:DIAGNÒSTICS SECUNDARIS|DIAGNÓSTICOS SECUNDARIOS)[:\s]*\n((?:[-•*].*\n?)+)'
        secondary_match = re.search(secondary_pattern, search_text, re.IGNORECASE | re.MULTILINE)
        
        if secondary_match:
            secondary_text = secondary_match.group(1)
            # Extreure cada línia que comença amb -, •, o *
            for line in re.findall(r'[-•*]\s*([^\n]+)', secondary_text):
                # Extreure codis
                snomed_match = re.search(cls.SNOMED_PATTERN, line, re.IGNORECASE)
                icd10_match = re.search(cls.ICD10_PATTERN, line, re.IGNORECASE)
                
                # Netejar descripció
                description = re.sub(r'Codi.*', '', line, flags=re.IGNORECASE).strip()
                description = re.sub(r'(?:SNOMED|ICD).*', '', description, flags=re.IGNORECASE).strip()
                
                if description:
                    diagnoses.append(ExtractedDiagnosis(
                        description=description,
                        snomed_code=snomed_match.group(1) if snomed_match else None,
                        icd10_code=icd10_match.group(1) if icd10_match else None,
                        is_primary=False
                    ))
        
        # Si no hem trobat res amb els patterns estrictes, buscar codis solts
        if not diagnoses:
            # Buscar codis SNOMED solts
            snomed_codes = re.findall(cls.SNOMED_LOOSE_PATTERN, search_text)
            for code in snomed_codes[:3]:  # Màxim 3 codis
                diagnoses.append(ExtractedDiagnosis(
                    description="Extracted from summary",
                    snomed_code=code,
                    is_primary=len(diagnoses) == 0
                ))
            
            # Buscar codis ICD-10 solts
            icd10_codes = re.findall(cls.ICD10_LOOSE_PATTERN, search_text)
            for code in icd10_codes[:3]:  # Màxim 3 codis
                # Intentar afegir a diagnòstic existent o crear nou
                if diagnoses and not diagnoses[-1].icd10_code:
                    diagnoses[-1].icd10_code = code
                else:
                    diagnoses.append(ExtractedDiagnosis(
                        description="Extracted from summary",
                        icd10_code=code,
                        is_primary=len(diagnoses) == 0
                    ))
        
        return diagnoses
    
    @classmethod
    def extract_medications(cls, text: str, section_text: Optional[str] = None) -> List[ExtractedMedication]:
        """
        Extreu medicacions amb posologia del text
        
        Args:
            text: Text complet de l'informe
            section_text: Text específic de la secció de medicació (opcional)
            
        Returns:
            Llista de medicacions extretes
        """
        medications = []
        search_text = section_text if section_text else text
        
        # Pattern per medicacions amb format: - Nom Dosi/Freqüència
        med_pattern = r'[-•*]\s*([A-Z][a-zà-úñ]+(?:\s+[A-Z][a-zà-úñ]+)*)\s+(\d+(?:\.\d+)?)\s*(mg|g|ml|mcg|UI)(?:/(\d+h|24h|dia|día|d))?'
        
        for match in re.finditer(med_pattern, search_text):
            name = match.group(1).strip()
            dosage = f"{match.group(2)}{match.group(3)}"
            frequency = match.group(4) if match.group(4) else None
            
            # Buscar codi ATC en la mateixa línia o propera
            line_start = max(0, match.start() - 50)
            line_end = min(len(search_text), match.end() + 100)
            context = search_text[line_start:line_end]
            
            atc_match = re.search(cls.ATC_PATTERN, context, re.IGNORECASE)
            atc_code = atc_match.group(1) if atc_match else None
            
            medications.append(ExtractedMedication(
                name=name,
                dosage=dosage,
                frequency=frequency,
                atc_code=atc_code
            ))
        
        # Si no hem trobat res amb el pattern estricte, buscar codis ATC solts
        if not medications:
            atc_codes = re.findall(cls.ATC_LOOSE_PATTERN, search_text)
            for code in atc_codes[:5]:  # Màxim 5 medicacions
                medications.append(ExtractedMedication(
                    name="Extracted from summary",
                    dosage="See summary",
                    atc_code=code
                ))
        
        return medications
    
    @classmethod
    def extract_follow_up(cls, text: str, section_text: Optional[str] = None) -> List[ExtractedFollowUp]:
        """
        Extreu recomanacions de seguiment
        
        Args:
            text: Text complet de l'informe
            section_text: Text específic de la secció de seguiment (opcional)
            
        Returns:
            Llista de recomanacions de seguiment
        """
        follow_ups = []
        search_text = section_text if section_text else text
        
        # Buscar línies que comencen amb -, •, o *
        for line in re.findall(r'[-•*]\s*([^\n]+)', search_text):
            # Buscar especialitat
            specialty_match = re.search(r'(cardiologia|endocrinologia|neurologia|medicina interna|cirurgia)', 
                                       line, re.IGNORECASE)
            specialty = specialty_match.group(1) if specialty_match else None
            
            # Buscar timeframe
            timeframe_match = re.search(r'(\d+\s*(?:dies|días|setmanes|semanas|mesos|meses))', 
                                       line, re.IGNORECASE)
            timeframe = timeframe_match.group(1) if timeframe_match else None
            
            follow_ups.append(ExtractedFollowUp(
                description=line.strip(),
                specialty=specialty,
                timeframe=timeframe
            ))
        
        return follow_ups
    
    @classmethod
    def validate_codes(cls, snomed_code: Optional[str] = None, 
                      icd10_code: Optional[str] = None,
                      atc_code: Optional[str] = None) -> Dict[str, bool]:
        """
        Valida format de codis mèdics
        
        Args:
            snomed_code: Codi SNOMED CT
            icd10_code: Codi ICD-10
            atc_code: Codi ATC
            
        Returns:
            Dict amb validació de cada codi
        """
        validation = {}
        
        if snomed_code:
            validation['snomed'] = bool(re.match(r'^\d{6,18}$', snomed_code))
        
        if icd10_code:
            validation['icd10'] = bool(re.match(r'^[A-Z]\d{2}(?:\.\d{1,2})?$', icd10_code))
        
        if atc_code:
            validation['atc'] = bool(re.match(r'^[A-Z]\d{2}[A-Z]{2}\d{2}$', atc_code))
        
        return validation
