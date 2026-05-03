"""
Test script per verificar el fallback de BioPortal per ATC, SNOMED i ICD-10
"""

import asyncio
import sys
import os
from pathlib import Path

# Afegir el directori arrel al path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from src.main.core.coding.semantic_coding_service import SemanticCodingService
from src.main.infrastructure.vector_db.qdrant_client import HealthcareQdrantClient
from src.main.infrastructure.embeddings.bge_m3 import BGEM3Embeddings


async def test_bioportal_fallback():
    """Test del fallback a BioPortal per medicacions poc comunes"""
    
    print("🧪 TEST: BioPortal Fallback per ATC, SNOMED i ICD-10\n")
    print("=" * 70)
    
    # Inicialitzar components
    print("\n1️⃣ Inicialitzant components...")
    qdrant_client = HealthcareQdrantClient()
    embeddings_model = BGEM3Embeddings()
    await embeddings_model.initialize()
    
    coding_service = SemanticCodingService(
        qdrant_client=qdrant_client,
        embeddings_model=embeddings_model,
        bioportal_client=True  # Habilitar BioPortal
    )
    
    # Forçar threshold alt per testejar fallback
    coding_service.min_confidence = 0.95
    
    print("✅ Components inicialitzats\n")
    
    # Test 1: Medicació poc comuna (hauria de fer fallback a BioPortal)
    print("=" * 70)
    print("\n2️⃣ TEST ATC: Medicació poc comuna")
    print("-" * 70)
    
    medication = "Adalimumab"  # Medicació biològica poc indexada
    print(f"🔍 Cercant codi ATC per: {medication}")
    
    atc_code = await coding_service.get_atc_code(medication)
    
    if atc_code:
        print(f"\n✅ Codi ATC trobat:")
        print(f"   - Code: {atc_code.code}")
        print(f"   - Display: {atc_code.display}")
        print(f"   - Confidence: {atc_code.confidence:.2f}")
        print(f"   - Source: {atc_code.source}")
    else:
        print(f"\n❌ No s'ha trobat codi ATC per: {medication}")
    
    # Test 2: Condició poc comuna (SNOMED)
    print("\n" + "=" * 70)
    print("\n3️⃣ TEST SNOMED: Condició poc comuna")
    print("-" * 70)
    
    condition = "Síndrome de Guillain-Barré"
    print(f"🔍 Cercant codi SNOMED per: {condition}")
    
    snomed_code = await coding_service.get_snomed_code(condition)
    
    if snomed_code:
        print(f"\n✅ Codi SNOMED trobat:")
        print(f"   - Code: {snomed_code.code}")
        print(f"   - Display: {snomed_code.display}")
        print(f"   - Confidence: {snomed_code.confidence:.2f}")
        print(f"   - Source: {snomed_code.source}")
    else:
        print(f"\n❌ No s'ha trobat codi SNOMED per: {condition}")
    
    # Test 3: Diagnòstic poc comú (ICD-10)
    print("\n" + "=" * 70)
    print("\n4️⃣ TEST ICD-10: Diagnòstic poc comú")
    print("-" * 70)
    
    diagnosis = "Malaltia de Crohn"
    print(f"🔍 Cercant codi ICD-10 per: {diagnosis}")
    
    icd10_code = await coding_service.get_icd10_code(diagnosis)
    
    if icd10_code:
        print(f"\n✅ Codi ICD-10 trobat:")
        print(f"   - Code: {icd10_code.code}")
        print(f"   - Display: {icd10_code.display}")
        print(f"   - Confidence: {icd10_code.confidence:.2f}")
        print(f"   - Source: {icd10_code.source}")
    else:
        print(f"\n❌ No s'ha trobat codi ICD-10 per: {diagnosis}")
    
    print("\n" + "=" * 70)
    print("\n✅ Test completat!")
    print("\nNota: Si els codis tenen source='bioportal_api', el fallback funciona correctament.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(test_bioportal_fallback())
