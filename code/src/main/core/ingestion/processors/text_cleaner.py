"""
Text cleaning utilities for Healthcare RAG system
Handles text normalization, cleaning, and preprocessing
"""

import re
import unicodedata
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class TextCleaner:
    """Text cleaning and normalization utilities"""
    
    def __init__(self):
        # Medical abbreviations that should be preserved
        self.medical_abbreviations = {
            'Dr.', 'Dra.', 'Prof.', 'Sr.', 'Sra.',
            'mg.', 'ml.', 'kg.', 'cm.', 'mm.',
            'ICD-10', 'ICD-11', 'SNOMED-CT',
            'COVID-19', 'SARS-CoV-2', 'HIV', 'AIDS',
            'ECG', 'EKG', 'MRI', 'CT', 'PET'
        }
        
        # Patterns for medical codes
        self.medical_code_patterns = [
            r'[A-Z]\d{2}\.?\d*',  # ICD codes
            r'\d{6,8}',           # SNOMED codes
            r'[A-Z]{1,3}\d{1,4}', # Other medical codes
        ]
    
    def clean_text(self, text: str, preserve_medical_formatting: bool = True) -> str:
        """Main text cleaning function"""
        if not text:
            return ""
        
        # Normalize unicode characters
        text = unicodedata.normalize('NFKC', text)
        
        # Remove or replace problematic characters
        text = self._fix_encoding_issues(text)
        
        # Clean whitespace
        text = self._clean_whitespace(text)
        
        # Fix punctuation
        text = self._fix_punctuation(text)
        
        # Preserve medical formatting if requested
        if preserve_medical_formatting:
            text = self._preserve_medical_formatting(text)
        
        # Remove excessive newlines but preserve paragraph structure
        text = self._normalize_paragraphs(text)
        
        return text.strip()
    
    def _fix_encoding_issues(self, text: str) -> str:
        """Fix common encoding issues in medical documents"""
        replacements = {
            'â€™': "'",
            'â€œ': '"',
            'â€': '"',
            'â€¢': '•',
            'Ã¡': 'á',
            'Ã©': 'é',
            'Ã­': 'í',
            'Ã³': 'ó',
            'Ãº': 'ú',
            'Ã±': 'ñ',
            'Ã§': 'ç'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def _clean_whitespace(self, text: str) -> str:
        """Clean and normalize whitespace"""
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Replace tabs with spaces
        text = text.replace('\t', ' ')
        
        # Fix spaces around punctuation
        text = re.sub(r' +([,.;:!?])', r'\1', text)
        text = re.sub(r'([,.;:!?]) +', r'\1 ', text)
        
        return text
    
    def _fix_punctuation(self, text: str) -> str:
        """Fix common punctuation issues"""
        # Fix missing spaces after punctuation
        text = re.sub(r'([.!?])([A-ZÁÉÍÓÚÑ])', r'\1 \2', text)
        
        # Fix comma spacing
        text = re.sub(r',([^\s])', r', \1', text)
        
        # Fix colon spacing
        text = re.sub(r':([^\s])', r': \1', text)
        
        return text
    
    def _preserve_medical_formatting(self, text: str) -> str:
        """Preserve important medical formatting"""
        # Preserve medical abbreviations
        for abbrev in self.medical_abbreviations:
            # Ensure proper spacing around abbreviations
            pattern = rf'\b{re.escape(abbrev)}\b'
            text = re.sub(pattern, abbrev, text, flags=re.IGNORECASE)
        
        # Preserve medical codes formatting
        for pattern in self.medical_code_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # Ensure codes are properly formatted
                text = text.replace(match, match.upper())
        
        return text
    
    def _normalize_paragraphs(self, text: str) -> str:
        """Normalize paragraph structure"""
        # Replace multiple newlines with double newline
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Ensure single newline within paragraphs
        text = re.sub(r'([^\n])\n([^\n])', r'\1 \2', text)
        
        return text
    
    def extract_medical_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract medical entities from text"""
        entities = {
            'codes': [],
            'abbreviations': [],
            'medications': [],
            'procedures': []
        }
        
        # Extract medical codes
        for pattern in self.medical_code_patterns:
            codes = re.findall(pattern, text)
            entities['codes'].extend(codes)
        
        # Extract abbreviations
        for abbrev in self.medical_abbreviations:
            if abbrev.lower() in text.lower():
                entities['abbreviations'].append(abbrev)
        
        # Extract potential medication names (capitalized words ending in common suffixes)
        medication_pattern = r'\b[A-Z][a-z]+(?:ina|ine|ol|al|an|ate|ide)\b'
        medications = re.findall(medication_pattern, text)
        entities['medications'].extend(medications)
        
        return entities
    
    def split_sentences(self, text: str) -> List[str]:
        """Split text into sentences, handling medical abbreviations"""
        # Protect abbreviations from sentence splitting
        protected_text = text
        protection_map = {}
        
        for i, abbrev in enumerate(self.medical_abbreviations):
            placeholder = f"__ABBREV_{i}__"
            protected_text = protected_text.replace(abbrev, placeholder)
            protection_map[placeholder] = abbrev
        
        # Split sentences
        sentences = re.split(r'[.!?]+\s+', protected_text)
        
        # Restore abbreviations
        for i, sentence in enumerate(sentences):
            for placeholder, abbrev in protection_map.items():
                sentence = sentence.replace(placeholder, abbrev)
            sentences[i] = sentence.strip()
        
        return [s for s in sentences if s]
    
    def remove_headers_footers(self, text: str) -> str:
        """Remove common headers and footers from documents"""
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip common header/footer patterns
            if any(pattern in line.lower() for pattern in [
                'página', 'page', 'servicio andaluz de salud',
                'junta de andalucía', 'consejería de salud',
                'copyright', '©', 'todos los derechos'
            ]):
                continue
            
            # Skip lines that are just numbers (page numbers)
            if line.isdigit():
                continue
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
