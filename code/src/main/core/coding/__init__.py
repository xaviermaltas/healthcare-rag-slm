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
# MedicalTranslator ELIMINAT - anti-pattern refactoritzat

# Nova arquitectura semàntica
from src.main.core.coding.semantic_coding_service import (
    SemanticCodingService,
    CodingPipeline
)

__all__ = [
    'MedicalCodingService',
    'MedicalCode',
    'DiagnosisCoding',
    'MedicationCoding',
    'SemanticCodingService',
    'CodingPipeline'
]
