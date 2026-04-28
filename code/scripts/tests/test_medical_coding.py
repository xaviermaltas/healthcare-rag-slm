"""
Test Medical Coding Service
Validates automatic coding of diagnoses and medications
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.main.core.coding.medical_coding_service import MedicalCodingService
from src.main.infrastructure.ontologies.snomed_client import SNOMEDClient
from src.main.infrastructure.ontologies.ontology_manager import OntologyManager
from config.settings import get_settings

settings = get_settings()


async def test_diagnosis_coding():
    """Test diagnosis coding with SNOMED CT and ICD-10"""
    
    print("\n" + "="*80)
    print("TEST: Diagnosis Coding")
    print("="*80)
    
    # Check if API key is available
    if not settings.BIOPORTAL_API_KEY:
        print("⚠️  BIOPORTAL_API_KEY not set - skipping test")
        print("   Get a free API key at: https://bioportal.bioontology.org/account")
        return
    
    # Initialize clients
    snomed_client = SNOMEDClient(
        api_key=settings.BIOPORTAL_API_KEY,
        base_url=settings.BIOPORTAL_BASE_URL
    )
    
    ontology_manager = OntologyManager(
        api_key=settings.BIOPORTAL_API_KEY,
        base_url=settings.BIOPORTAL_BASE_URL
    )
    
    # Initialize coding service
    coding_service = MedicalCodingService(
        snomed_client=snomed_client,
        ontology_manager=ontology_manager
    )
    
    # Test cases
    test_diagnoses = [
        "Infart agut de miocardi",
        "Diabetis mellitus tipus 2",
        "Hipertensió arterial",
        "Pneumònia adquirida a la comunitat"
    ]
    
    print("\nTesting diagnosis coding...")
    for diagnosis in test_diagnoses:
        print(f"\n📋 Diagnosis: {diagnosis}")
        
        try:
            result = await coding_service.code_diagnosis(diagnosis, min_confidence=0.5)
            
            if result.snomed_code:
                print(f"   ✅ SNOMED CT: {result.snomed_code.code} - {result.snomed_code.display}")
                print(f"      Confidence: {result.snomed_code.confidence:.2f}")
            else:
                print(f"   ❌ SNOMED CT: Not found")
            
            if result.icd10_code:
                print(f"   ✅ ICD-10: {result.icd10_code.code} - {result.icd10_code.display}")
                print(f"      Confidence: {result.icd10_code.confidence:.2f}")
            else:
                print(f"   ❌ ICD-10: Not found")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Close clients
    await snomed_client.close()
    await ontology_manager.close()


async def test_medication_coding():
    """Test medication coding with ATC and SNOMED CT"""
    
    print("\n" + "="*80)
    print("TEST: Medication Coding")
    print("="*80)
    
    # Check if API key is available
    if not settings.BIOPORTAL_API_KEY:
        print("⚠️  BIOPORTAL_API_KEY not set - skipping test")
        return
    
    # Initialize clients
    snomed_client = SNOMEDClient(
        api_key=settings.BIOPORTAL_API_KEY,
        base_url=settings.BIOPORTAL_BASE_URL
    )
    
    ontology_manager = OntologyManager(
        api_key=settings.BIOPORTAL_API_KEY,
        base_url=settings.BIOPORTAL_BASE_URL
    )
    
    # Initialize coding service
    coding_service = MedicalCodingService(
        snomed_client=snomed_client,
        ontology_manager=ontology_manager
    )
    
    # Test cases
    test_medications = [
        "Enalapril",
        "Metformina",
        "Atorvastatina",
        "Àcid acetilsalicílic"
    ]
    
    print("\nTesting medication coding...")
    for medication in test_medications:
        print(f"\n💊 Medication: {medication}")
        
        try:
            result = await coding_service.code_medication(medication, min_confidence=0.5)
            
            if result.atc_code:
                print(f"   ✅ ATC: {result.atc_code.code} - {result.atc_code.display}")
                print(f"      Confidence: {result.atc_code.confidence:.2f}")
            else:
                print(f"   ⚠️  ATC: Not implemented yet")
            
            if result.snomed_code:
                print(f"   ✅ SNOMED CT: {result.snomed_code.code} - {result.snomed_code.display}")
                print(f"      Confidence: {result.snomed_code.confidence:.2f}")
            else:
                print(f"   ❌ SNOMED CT: Not found")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Close clients
    await snomed_client.close()
    await ontology_manager.close()


async def test_batch_coding():
    """Test batch coding performance"""
    
    print("\n" + "="*80)
    print("TEST: Batch Coding Performance")
    print("="*80)
    
    # Check if API key is available
    if not settings.BIOPORTAL_API_KEY:
        print("⚠️  BIOPORTAL_API_KEY not set - skipping test")
        return
    
    # Initialize clients
    snomed_client = SNOMEDClient(
        api_key=settings.BIOPORTAL_API_KEY,
        base_url=settings.BIOPORTAL_BASE_URL
    )
    
    ontology_manager = OntologyManager(
        api_key=settings.BIOPORTAL_API_KEY,
        base_url=settings.BIOPORTAL_BASE_URL
    )
    
    # Initialize coding service
    coding_service = MedicalCodingService(
        snomed_client=snomed_client,
        ontology_manager=ontology_manager
    )
    
    # Test batch
    diagnoses = [
        "Infart agut de miocardi",
        "Diabetis mellitus tipus 2",
        "Hipertensió arterial"
    ]
    
    print(f"\nCoding {len(diagnoses)} diagnoses in batch...")
    
    import time
    start = time.time()
    
    try:
        results = await coding_service.code_diagnoses_batch(diagnoses, min_confidence=0.5)
        
        elapsed = time.time() - start
        
        print(f"\n✅ Batch coding completed in {elapsed:.2f}s")
        print(f"   Average: {elapsed/len(diagnoses):.2f}s per diagnosis")
        
        for result in results:
            codes = []
            if result.snomed_code:
                codes.append(f"SNOMED: {result.snomed_code.code}")
            if result.icd10_code:
                codes.append(f"ICD-10: {result.icd10_code.code}")
            
            print(f"\n   {result.diagnosis_text}")
            print(f"   → {', '.join(codes) if codes else 'No codes found'}")
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Close clients
    await snomed_client.close()
    await ontology_manager.close()


async def main():
    """Run all tests"""
    
    print("\n" + "="*80)
    print("🧪 MEDICAL CODING SERVICE TESTS")
    print("="*80)
    
    await test_diagnosis_coding()
    await test_medication_coding()
    await test_batch_coding()
    
    print("\n" + "="*80)
    print("✅ All tests completed")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
