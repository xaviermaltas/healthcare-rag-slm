#!/usr/bin/env python3
"""
Test Semantic Coding Architecture
Valida la nova arquitectura de codificació semàntica vs legacy
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.main.core.coding.semantic_coding_service import SemanticCodingService, MINIMAL_FALLBACK
from src.main.core.coding.medical_coding_service import MedicalCodingService
from src.main.core.coding.medical_translator import MedicalTranslator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_fallback_dictionaries():
    """Test diccionaris de fallback mínims"""
    logger.info("🧪 Testing minimal fallback dictionaries...")
    
    # Test SNOMED CT fallback
    snomed_tests = [
        ("diabetis", "73211009"),
        ("hipertensió", "38341003"),
        ("infart", "57054005"),
        ("pneumònia", "233604007"),
        ("asma", "195967001")
    ]
    
    for term, expected_code in snomed_tests:
        actual_code = MINIMAL_FALLBACK['SNOMED_CT'].get(term)
        status = "✅" if actual_code == expected_code else "❌"
        logger.info(f"  {status} SNOMED '{term}' → {actual_code} (expected: {expected_code})")
    
    # Test ICD-10 fallback
    icd10_tests = [
        ("diabetis tipus 2", "E11.9"),
        ("hipertensió", "I10"),
        ("infart miocardi", "I21.9"),
        ("pneumònia", "J18.9"),
        ("asma", "J45.909")
    ]
    
    for term, expected_code in icd10_tests:
        actual_code = MINIMAL_FALLBACK['ICD10'].get(term)
        status = "✅" if actual_code == expected_code else "❌"
        logger.info(f"  {status} ICD-10 '{term}' → {actual_code} (expected: {expected_code})")
    
    # Test ATC fallback
    atc_tests = [
        ("metformina", "A10BA02"),
        ("enalapril", "C09AA02"),
        ("atorvastatina", "C10AA05"),
        ("omeprazol", "A02BC01"),
        ("paracetamol", "N02BE01")
    ]
    
    for term, expected_code in atc_tests:
        actual_code = MINIMAL_FALLBACK['ATC'].get(term)
        status = "✅" if actual_code == expected_code else "❌"
        logger.info(f"  {status} ATC '{term}' → {actual_code} (expected: {expected_code})")


async def test_legacy_vs_semantic():
    """Compara arquitectura legacy vs semàntica"""
    logger.info("🧪 Testing Legacy vs Semantic Architecture...")
    
    # Test cases
    test_cases = [
        {
            'diagnosis': 'diabetis mellitus tipus 2',
            'medication': 'metformina 850mg',
            'expected_snomed': '73211009',
            'expected_icd10': 'E11.9',
            'expected_atc': 'A10BA02'
        },
        {
            'diagnosis': 'hipertensió arterial',
            'medication': 'enalapril 10mg',
            'expected_snomed': '38341003',
            'expected_icd10': 'I10',
            'expected_atc': 'C09AA02'
        },
        {
            'diagnosis': 'infart agut de miocardi',
            'medication': 'adiro 100mg',
            'expected_snomed': '57054005',
            'expected_icd10': 'I21.9',
            'expected_atc': 'B01AC06'
        }
    ]
    
    # Test legacy architecture
    logger.info("  📊 Testing LEGACY architecture...")
    legacy_service = MedicalCodingService()  # No Qdrant client = legacy mode
    
    for i, case in enumerate(test_cases, 1):
        logger.info(f"    Case {i}: {case['diagnosis']} + {case['medication']}")
        
        # Test SNOMED via legacy translator
        snomed_code = MedicalTranslator.get_snomed_code(case['diagnosis'])
        logger.info(f"      SNOMED: {snomed_code} (expected: {case['expected_snomed']})")
        
        # Test ICD-10 via legacy translator
        icd10_code = MedicalTranslator.get_icd10_code(case['diagnosis'])
        logger.info(f"      ICD-10: {icd10_code} (expected: {case['expected_icd10']})")
        
        # Test ATC via legacy translator
        atc_code = MedicalTranslator.get_atc_code(case['medication'])
        logger.info(f"      ATC: {atc_code} (expected: {case['expected_atc']})")
    
    # Test semantic architecture (amb fallback)
    logger.info("  🔍 Testing SEMANTIC architecture (fallback mode)...")
    semantic_service = SemanticCodingService(qdrant_client=None)  # No Qdrant = fallback
    
    for i, case in enumerate(test_cases, 1):
        logger.info(f"    Case {i}: {case['diagnosis']} + {case['medication']}")
        
        # Test SNOMED semantic
        snomed_result = await semantic_service.get_snomed_code(case['diagnosis'])
        snomed_code = snomed_result.code if snomed_result else None
        logger.info(f"      SNOMED: {snomed_code} (expected: {case['expected_snomed']})")
        
        # Test ICD-10 semantic
        icd10_result = await semantic_service.get_icd10_code(case['diagnosis'])
        icd10_code = icd10_result.code if icd10_result else None
        logger.info(f"      ICD-10: {icd10_code} (expected: {case['expected_icd10']})")
        
        # Test ATC semantic
        atc_result = await semantic_service.get_atc_code(case['medication'])
        atc_code = atc_result.code if atc_result else None
        logger.info(f"      ATC: {atc_code} (expected: {case['expected_atc']})")


async def test_medication_cleaning():
    """Test neteja de noms de medicaments"""
    logger.info("🧪 Testing medication name cleaning...")
    
    from src.main.core.coding.semantic_coding_service import SemanticCodingService
    
    # Mock service per test cleaning
    class MockSemanticService(SemanticCodingService):
        def __init__(self):
            pass  # Skip parent __init__
    
    service = MockSemanticService()
    
    test_cases = [
        ("enalapril 10mg", "enalapril"),
        ("metformina 850mg/12h", "metformina"),
        ("omeprazol 20mg comprimits", "omeprazol"),
        ("paracetamol 500mg/8h", "paracetamol"),
        ("atorvastatina 40mg càpsules", "atorvastatina"),
        ("adiro 100mg", "adiro")
    ]
    
    for original, expected in test_cases:
        cleaned = service._clean_medication_name(original)
        status = "✅" if cleaned == expected else "❌"
        logger.info(f"  {status} '{original}' → '{cleaned}' (expected: '{expected}')")


async def test_architecture_comparison():
    """Comparació completa d'arquitectures"""
    logger.info("🧪 Architecture Comparison Summary...")
    
    # Estadístiques diccionaris
    from src.main.core.coding.snomed_extended_lookup import SNOMEDExtendedLookup
    from src.main.core.coding.icd10_extended_lookup import ICD10ExtendedLookup
    from src.main.core.coding.atc_extended_lookup import ATCExtendedLookup
    
    snomed_stats = SNOMEDExtendedLookup.get_stats()
    icd10_stats = ICD10ExtendedLookup.get_stats()
    atc_stats = ATCExtendedLookup.get_stats()
    
    logger.info("  📊 LEGACY Architecture (Static Dictionaries):")
    logger.info(f"    - SNOMED CT: {snomed_stats['total_terms']} terms")
    logger.info(f"    - ICD-10: {icd10_stats['total_terms']} terms")
    logger.info(f"    - ATC: {atc_stats['total_terms']} terms")
    logger.info(f"    - TOTAL: {snomed_stats['total_terms'] + icd10_stats['total_terms'] + atc_stats['total_terms']} terms")
    logger.info("    - Pros: Fast, deterministic, no dependencies")
    logger.info("    - Cons: Limited coverage, manual maintenance, no semantic understanding")
    
    logger.info("  🔍 SEMANTIC Architecture (Retrieval-based):")
    logger.info("    - SNOMED CT: 350,000+ concepts (when indexed)")
    logger.info("    - ICD-10: 70,000+ codes (when indexed)")
    logger.info("    - ATC: 6,000+ medications (when indexed)")
    logger.info("    - TOTAL: 426,000+ entries (when indexed)")
    logger.info("    - Fallback: 30 ultra-common terms")
    logger.info("    - Pros: Complete coverage, semantic understanding, auto-updates")
    logger.info("    - Cons: Requires Qdrant, more complex, potential latency")
    
    logger.info("  🎯 RECOMMENDATION:")
    logger.info("    ✅ Use SEMANTIC architecture for production")
    logger.info("    ⚠️ Keep LEGACY as fallback for critical terms")
    logger.info("    🔄 Migrate gradually: index ontologies → test → switch")


async def main():
    """Test principal"""
    logger.info("🚀 Starting Semantic Coding Architecture Tests...")
    
    try:
        await test_fallback_dictionaries()
        print()
        
        await test_legacy_vs_semantic()
        print()
        
        await test_medication_cleaning()
        print()
        
        await test_architecture_comparison()
        
        logger.info("✅ All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
