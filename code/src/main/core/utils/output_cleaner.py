"""
Output Cleaner for Medical Reports
Neteja la sortida del LLM eliminant instruccions internes i text innecessari
"""

import re
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class OutputCleaner:
    """Neteja la sortida del LLM per a informes mèdics"""
    
    # Patrons a eliminar
    PATTERNS_TO_REMOVE = [
        # Instruccions internes
        r"RECORDATORI CRÍTIC.*?(?=\n\n|\Z)",
        r"RECORDATORIO CRÍTICO.*?(?=\n\n|\Z)",
        r"ZERO TOLERANCIA.*?(?=\n\n|\Z)",
        r"CERO TOLERANCIA.*?(?=\n\n|\Z)",
        r"✓.*?(?=\n|$)",
        r"❌.*?(?=\n|$)",
        
        # Context de protocols
        r"CONTEXT CLÍNIC.*?(?=\n\n[0-9]\.|\Z)",
        r"CONTEXTO CLÍNICO.*?(?=\n\n[0-9]\.|\Z)",
        r"FONTS CONSULTADES:.*?(?=\n\n[0-9]\.|\Z)",
        r"FUENTES CONSULTADAS:.*?(?=\n\n[0-9]\.|\Z)",
        
        # Instruccions de format
        r"\[.*?específic.*?\]",
        r"\[.*?especific.*?\]",
        r"\[.*?escau.*?\]",
        r"\[.*?proceda.*?\]",
        
        # Línies buides múltiples
        r"\n\n\n+",
    ]
    
    @staticmethod
    def clean_discharge_summary(text: str, language: str = "ca") -> str:
        """
        Neteja un informe d'alta hospitalària
        
        Args:
            text: Text generat pel LLM
            language: Idioma (ca/es)
            
        Returns:
            Text netejat
        """
        # Check if text contains codes before cleaning
        has_codes = bool(re.search(r'\((?:SNOMED|ICD-10|ATC)', text, re.IGNORECASE))
        if has_codes:
            logger.warning(f"⚠️ Text contains medical codes before cleaning (length: {len(text)})")
        
        cleaned = text
        
        # 1. Eliminar instruccions internes
        for pattern in OutputCleaner.PATTERNS_TO_REMOVE:
            cleaned = re.sub(pattern, "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        
        # 2. Eliminar línies que comencin amb "Genera un informe"
        cleaned = re.sub(r"^Genera un informe.*?(?=\n[0-9]\.|\Z)", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r"^Genera un informe.*?(?=\n[0-9]\.|\Z)", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        
        # 3. Netejar seccions buides
        if language == "ca":
            cleaned = re.sub(r"\[.*?específic.*?\]", "", cleaned)
            cleaned = re.sub(r"\[.*?escau.*?\]", "", cleaned)
        else:
            cleaned = re.sub(r"\[.*?específic.*?\]", "", cleaned)
            cleaned = re.sub(r"\[.*?proceda.*?\]", "", cleaned)
        
        # 4. CRÍTICA: Eliminar codis generats pel LLM (NO hauria de fer-ho)
        # Pattern: (SNOMED: XXX, ICD-10: XXX) o (SNOMED: XXX) o (ICD-10: XXX) o (ATC: XXX)
        # Capturar qualsevol combinació de codis dins de parèntesis
        before_codes = len(cleaned)
        # Find all code patterns before removing
        code_matches = re.findall(r'\s*\([^)]*(?:SNOMED|ICD-10|ATC)[^)]*\)', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s*\([^)]*(?:SNOMED|ICD-10|ATC)[^)]*\)', '', cleaned, flags=re.IGNORECASE)
        after_codes = len(cleaned)
        if before_codes != after_codes:
            logger.warning(f"🔧 REMOVED {len(code_matches)} LLM-generated code patterns ({before_codes - after_codes} chars)")
            for match in code_matches[:3]:  # Log first 3 matches
                logger.warning(f"   - {match}")
        # Eliminar línies que comencen amb "Codi"
        cleaned = re.sub(r'^-?\s*Codi\s+.*?$', '', cleaned, flags=re.MULTILINE)
        
        # 5. Eliminar línies buides múltiples
        cleaned = re.sub(r"\n\n\n+", "\n\n", cleaned)
        
        # 6. Trim
        cleaned = cleaned.strip()
        
        return cleaned
    
    @staticmethod
    def clean_referral_report(text: str, language: str = "ca") -> str:
        """
        Neteja un informe de derivació
        
        Args:
            text: Text generat pel LLM
            language: Idioma (ca/es)
            
        Returns:
            Text netejat
        """
        cleaned = text
        
        # Eliminar instruccions internes
        for pattern in OutputCleaner.PATTERNS_TO_REMOVE:
            cleaned = re.sub(pattern, "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        
        # Eliminar línies de generació
        cleaned = re.sub(r"^Genera un informe.*?(?=\n[0-9]\.|\Z)", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        
        # CRÍTICA: Eliminar codis generats pel LLM
        cleaned = re.sub(r'\s*\([^)]*(?:SNOMED|ICD-10|ATC)[^)]*\)', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'^-?\s*Codi\s+.*?$', '', cleaned, flags=re.MULTILINE)
        
        # Netejar línies buides
        cleaned = re.sub(r"\n\n\n+", "\n\n", cleaned)
        cleaned = cleaned.strip()
        
        return cleaned
    
    @staticmethod
    def clean_clinical_summary(text: str, language: str = "ca") -> str:
        """
        Neteja un resum clínic
        
        Args:
            text: Text generat pel LLM
            language: Idioma (ca/es)
            
        Returns:
            Text netejat
        """
        cleaned = text
        
        # Eliminar instruccions internes
        for pattern in OutputCleaner.PATTERNS_TO_REMOVE:
            cleaned = re.sub(pattern, "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        
        # Eliminar línies de generació
        cleaned = re.sub(r"^Genera.*?(?=\n\*\*|\Z)", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        
        # CRÍTICA: Eliminar codis generats pel LLM
        cleaned = re.sub(r'\s*\([^)]*(?:SNOMED|ICD-10|ATC)[^)]*\)', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'^-?\s*Codi\s+.*?$', '', cleaned, flags=re.MULTILINE)
        
        # Netejar línies buides
        cleaned = re.sub(r"\n\n\n+", "\n\n", cleaned)
        cleaned = cleaned.strip()
        
        return cleaned
    
    @staticmethod
    def extract_main_content(text: str, language: str = "ca") -> str:
        """
        Extreu el contingut principal eliminant tot el que no sigui clínic
        
        Args:
            text: Text complet
            language: Idioma (ca/es)
            
        Returns:
            Contingut principal
        """
        # Eliminar tot el que estigui després de "---" o "FONTS"
        if "---" in text:
            text = text.split("---")[0]
        
        if language == "ca":
            if "FONTS CONSULTADES" in text:
                text = text.split("FONTS CONSULTADES")[0]
        else:
            if "FUENTES CONSULTADAS" in text:
                text = text.split("FUENTES CONSULTADAS")[0]
        
        return text.strip()
