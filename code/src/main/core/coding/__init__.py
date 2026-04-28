"""
Medical Coding Module
Automatic coding of diagnoses and medications to standardized terminologies
"""

from src.main.core.coding.medical_coding_service import (
    MedicalCodingService,
    MedicalCode,
    DiagnosisCoding,
    MedicationCoding
)
from src.main.core.coding.medical_translator import MedicalTranslator

__all__ = [
    'MedicalCodingService',
    'MedicalCode',
    'DiagnosisCoding',
    'MedicationCoding',
    'MedicalTranslator'
]
