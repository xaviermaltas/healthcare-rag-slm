"""
Code Injector for Medical Reports
Injecta codis SNOMED/ICD-10/ATC dins del text generat pel LLM
"""

import re
from typing import Dict, List, Optional, Tuple


class CodeInjector:
    """Injecta codis mèdics dins dels informes de forma legible"""
    
    @staticmethod
    def inject_diagnosis_codes(
        text: str,
        diagnoses: List[Dict],
        language: str = "ca"
    ) -> str:
        """
        Injecta codis SNOMED/ICD-10 dins de diagnòstics mencionats
        
        Args:
            text: Text de l'informe
            diagnoses: Llista de diagnòstics amb codis
            language: Idioma (ca/es)
            
        Returns:
            Text amb codis injectats
        """
        if not diagnoses:
            return text
        
        result = text
        
        for diagnosis in diagnoses:
            diagnosis_text = diagnosis.get('description', '')
            snomed_code = diagnosis.get('snomed_code')
            icd10_code = diagnosis.get('icd10_code')
            
            if not diagnosis_text:
                continue
            
            # Buscar el diagnòstic al text (case-insensitive)
            # Prioritzar matches més llargs per evitar replacements parcials
            pattern = re.compile(re.escape(diagnosis_text), re.IGNORECASE)
            
            # Construir el codi a injectar
            codes_str = CodeInjector._build_code_string(
                snomed_code, icd10_code, language
            )
            
            if codes_str:
                # Reemplaçar la primera ocurrència del diagnòstic amb codi
                replacement = f"{diagnosis_text}{codes_str}"
                result = pattern.sub(replacement, result, count=1)
        
        return result
    
    @staticmethod
    def inject_medication_codes(
        text: str,
        medications: List[Dict],
        language: str = "ca"
    ) -> str:
        """
        Injecta codis ATC dins de medicaments mencionats
        
        Args:
            text: Text de l'informe
            medications: Llista de medicaments amb codis
            language: Idioma (ca/es)
            
        Returns:
            Text amb codis injectats
        """
        if not medications:
            return text
        
        result = text
        
        for medication in medications:
            med_name = medication.get('name', '')
            atc_code = medication.get('atc_code')
            
            if not med_name or not atc_code:
                continue
            
            # Buscar el medicament al text
            pattern = re.compile(re.escape(med_name), re.IGNORECASE)
            
            # Construir el codi a injectar
            if language == "ca":
                codes_str = f" (ATC: {atc_code})"
            else:
                codes_str = f" (ATC: {atc_code})"
            
            # Reemplaçar la primera ocurrència
            replacement = f"{med_name}{codes_str}"
            result = pattern.sub(replacement, result, count=1)
        
        return result
    
    @staticmethod
    def _build_code_string(
        snomed_code: Optional[str],
        icd10_code: Optional[str],
        language: str = "ca"
    ) -> str:
        """
        Construeix string de codis per injectar
        
        Args:
            snomed_code: Codi SNOMED CT
            icd10_code: Codi ICD-10
            language: Idioma
            
        Returns:
            String formatat amb codis
        """
        codes = []
        
        if snomed_code:
            codes.append(f"SNOMED: {snomed_code}")
        if icd10_code:
            codes.append(f"ICD-10: {icd10_code}")
        
        if not codes:
            return ""
        
        codes_str = ", ".join(codes)
        return f" ({codes_str})"
    
    @staticmethod
    def inject_all_codes(
        text: str,
        diagnoses: List[Dict] = None,
        medications: List[Dict] = None,
        language: str = "ca"
    ) -> str:
        """
        Injecta tots els codis (diagnòstics + medicaments)
        
        Args:
            text: Text de l'informe
            diagnoses: Llista de diagnòstics
            medications: Llista de medicaments
            language: Idioma
            
        Returns:
            Text amb tots els codis injectats
        """
        # CRÍTICA: Eliminar codis generats pel LLM PRIMER
        # Pattern: (SNOMED: XXX, ICD-10: XXX) o (SNOMED: XXX) o (ICD-10: XXX) o (ATC: XXX)
        result = re.sub(r'\s*\([^)]*(?:SNOMED|ICD-10|ATC)[^)]*\)', '', text, flags=re.IGNORECASE)
        
        if diagnoses:
            result = CodeInjector.inject_diagnosis_codes(result, diagnoses, language)
        
        if medications:
            result = CodeInjector.inject_medication_codes(result, medications, language)
        
        return result
    
    @staticmethod
    def extract_codes_from_text(text: str) -> Dict[str, List[str]]:
        """
        Extreu codis ja presents al text
        
        Args:
            text: Text de l'informe
            
        Returns:
            Dict amb codis SNOMED, ICD-10, ATC
        """
        codes = {
            'snomed': [],
            'icd10': [],
            'atc': []
        }
        
        # SNOMED CT: 6-18 dígits
        snomed_pattern = r'SNOMED[:\s]+(\d{6,18})'
        codes['snomed'] = list(set(re.findall(snomed_pattern, text, re.IGNORECASE)))
        
        # ICD-10: Lletra + 2 dígits + punt opcional + dígits
        icd10_pattern = r'ICD-10[:\s]+([A-Z]\d{2}(?:\.\d{1,2})?)'
        codes['icd10'] = list(set(re.findall(icd10_pattern, text, re.IGNORECASE)))
        
        # ATC: Lletra + 2 dígits + 2 lletres + 2 dígits
        atc_pattern = r'ATC[:\s]+([A-Z]\d{2}[A-Z]{2}\d{2})'
        codes['atc'] = list(set(re.findall(atc_pattern, text, re.IGNORECASE)))
        
        return codes
