#!/usr/bin/env python3
"""
Test script to verify BioPortal ontologies are working correctly
Tests SNOMED CT, MeSH, and ICD-10 with real API calls
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.main.infrastructure.ontologies.ontology_manager import OntologyManager, OntologyType
from config.settings import get_settings
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_ontology_connection():
    """Test basic connection to BioPortal"""
    print("=" * 80)
    print("TEST 1: CONNECTION TO BIOPORTAL")
    print("=" * 80)
    
    settings = get_settings()
    
    if not settings.BIOPORTAL_API_KEY:
        print("❌ ERROR: BIOPORTAL_API_KEY not set")
        print("Please add it to your .env file")
        return False
    
    print(f"✓ API Key found: {settings.BIOPORTAL_API_KEY[:8]}...")
    print(f"✓ Base URL: {settings.BIOPORTAL_BASE_URL}")
    
    manager = OntologyManager(
        api_key=settings.BIOPORTAL_API_KEY,
        base_url=settings.BIOPORTAL_BASE_URL
    )
    
    success = await manager.initialize()
    
    if success:
        print("✅ Connection successful!")
        await manager.close()
        return True
    else:
        print("❌ Connection failed")
        return False


async def test_ontology_statistics():
    """Test getting statistics from each ontology"""
    print("\n" + "=" * 80)
    print("TEST 2: ONTOLOGY STATISTICS")
    print("=" * 80)
    
    settings = get_settings()
    manager = OntologyManager(
        api_key=settings.BIOPORTAL_API_KEY,
        base_url=settings.BIOPORTAL_BASE_URL
    )
    
    await manager.initialize()
    
    try:
        stats = await manager.get_ontology_stats()
        
        print("\n📊 STATISTICS:")
        for ontology, data in stats.items():
            print(f"\n{ontology}:")
            if 'error' in data:
                print(f"  ❌ Error: {data['error']}")
            else:
                print(f"  ✓ Name: {data.get('name', 'N/A')}")
                print(f"  ✓ Version: {data.get('version', 'N/A')}")
                print(f"  ✓ Classes: {data.get('num_classes', 0):,}")
        
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    finally:
        await manager.close()


async def test_search_snomed():
    """Test searching SNOMED CT concepts"""
    print("\n" + "=" * 80)
    print("TEST 3: SEARCH SNOMED CT - 'diabetes mellitus type 2'")
    print("=" * 80)
    
    settings = get_settings()
    manager = OntologyManager(
        api_key=settings.BIOPORTAL_API_KEY,
        base_url=settings.BIOPORTAL_BASE_URL
    )
    
    await manager.initialize()
    
    try:
        concepts = await manager.search_concepts(
            query="diabetes mellitus type 2",
            ontologies=[OntologyType.SNOMED_CT],
            limit=5
        )
        
        print(f"\n✓ Found {len(concepts)} concepts")
        
        for i, concept in enumerate(concepts[:3], 1):
            print(f"\n📋 Concept {i}:")
            print(f"  ID: {concept.concept_id}")
            print(f"  Label: {concept.pref_label}")
            print(f"  Ontology: {concept.ontology.value}")
            
            if concept.definition:
                print(f"  Definition: {concept.definition[:100]}...")
            
            if concept.synonyms:
                print(f"  Synonyms: {', '.join(concept.synonyms[:3])}")
        
        return len(concepts) > 0
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        await manager.close()


async def test_search_mesh():
    """Test searching MeSH concepts"""
    print("\n" + "=" * 80)
    print("TEST 4: SEARCH MESH - 'diabetes mellitus type 2'")
    print("=" * 80)
    
    settings = get_settings()
    manager = OntologyManager(
        api_key=settings.BIOPORTAL_API_KEY,
        base_url=settings.BIOPORTAL_BASE_URL
    )
    
    await manager.initialize()
    
    try:
        concepts = await manager.search_concepts(
            query="diabetes mellitus type 2",
            ontologies=[OntologyType.MESH],
            limit=5
        )
        
        print(f"\n✓ Found {len(concepts)} concepts")
        
        for i, concept in enumerate(concepts[:3], 1):
            print(f"\n📋 Concept {i}:")
            print(f"  ID: {concept.concept_id}")
            print(f"  Label: {concept.pref_label}")
            print(f"  Ontology: {concept.ontology.value}")
            
            if concept.definition:
                print(f"  Definition: {concept.definition[:100]}...")
            
            if concept.synonyms:
                print(f"  Synonyms: {', '.join(concept.synonyms[:3])}")
        
        return len(concepts) > 0
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        await manager.close()


async def test_search_icd10():
    """Test searching ICD-10 concepts"""
    print("\n" + "=" * 80)
    print("TEST 5: SEARCH ICD-10 - 'diabetes mellitus type 2'")
    print("=" * 80)
    
    settings = get_settings()
    manager = OntologyManager(
        api_key=settings.BIOPORTAL_API_KEY,
        base_url=settings.BIOPORTAL_BASE_URL
    )
    
    await manager.initialize()
    
    try:
        concepts = await manager.search_concepts(
            query="type 2 diabetes mellitus",
            ontologies=[OntologyType.ICD10],
            limit=5
        )
        
        print(f"\n✓ Found {len(concepts)} concepts")
        
        for i, concept in enumerate(concepts[:3], 1):
            print(f"\n📋 Concept {i}:")
            print(f"  ID: {concept.concept_id}")
            print(f"  Label: {concept.pref_label}")
            print(f"  Ontology: {concept.ontology.value}")
            
            if concept.definition:
                print(f"  Definition: {concept.definition[:100]}...")
            
            if concept.synonyms:
                print(f"  Synonyms: {', '.join(concept.synonyms[:3])}")
        
        return len(concepts) > 0
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        await manager.close()


async def test_multi_ontology_search():
    """Test searching across multiple ontologies"""
    print("\n" + "=" * 80)
    print("TEST 6: MULTI-ONTOLOGY SEARCH - 'hypertension'")
    print("=" * 80)
    
    settings = get_settings()
    manager = OntologyManager(
        api_key=settings.BIOPORTAL_API_KEY,
        base_url=settings.BIOPORTAL_BASE_URL
    )
    
    await manager.initialize()
    
    try:
        concepts = await manager.search_concepts(
            query="hypertension",
            ontologies=[
                OntologyType.SNOMED_CT,
                OntologyType.MESH,
                OntologyType.ICD10
            ],
            limit=15
        )
        
        print(f"\n✓ Found {len(concepts)} concepts across all ontologies")
        
        # Group by ontology
        by_ontology = {}
        for concept in concepts:
            ont = concept.ontology.value
            if ont not in by_ontology:
                by_ontology[ont] = []
            by_ontology[ont].append(concept)
        
        print("\n📊 Distribution:")
        for ont, ont_concepts in by_ontology.items():
            print(f"  {ont}: {len(ont_concepts)} concepts")
        
        # Show samples
        print("\n📋 Sample concepts:")
        for ont, ont_concepts in by_ontology.items():
            if ont_concepts:
                concept = ont_concepts[0]
                print(f"\n  {ont}:")
                print(f"    ID: {concept.concept_id}")
                print(f"    Label: {concept.pref_label}")
        
        return len(concepts) > 0
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        await manager.close()


async def test_text_mapping():
    """Test mapping clinical text to ontology concepts"""
    print("\n" + "=" * 80)
    print("TEST 7: TEXT MAPPING - Clinical text to concepts")
    print("=" * 80)
    
    clinical_text = "paciente con diabetes tipo 2 e hipertensión arterial"
    print(f"\nText: '{clinical_text}'")
    
    settings = get_settings()
    manager = OntologyManager(
        api_key=settings.BIOPORTAL_API_KEY,
        base_url=settings.BIOPORTAL_BASE_URL
    )
    
    await manager.initialize()
    
    try:
        mappings = await manager.map_text_to_concepts(
            text=clinical_text,
            ontologies=[OntologyType.SNOMED_CT, OntologyType.ICD10],
            top_k=5,
            min_score=0.5
        )
        
        print(f"\n✓ Found {len(mappings)} mappings")
        
        for i, mapping in enumerate(mappings[:5], 1):
            concept = mapping['concept']
            score = mapping['score']
            print(f"\n📋 Mapping {i} (score: {score:.2f}):")
            print(f"  Label: {concept['pref_label']}")
            print(f"  Ontology: {concept['ontology']}")
            print(f"  ID: {concept['concept_id']}")
        
        return len(mappings) > 0
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        await manager.close()


async def main():
    """Run all tests"""
    print("\n" + "🧪" * 40)
    print("BIOPORTAL ONTOLOGIES TEST SUITE")
    print("🧪" * 40 + "\n")
    
    results = {}
    
    # Test 1: Connection
    results['connection'] = await test_ontology_connection()
    
    if not results['connection']:
        print("\n❌ Connection failed. Cannot continue with other tests.")
        return
    
    # Test 2: Statistics
    results['statistics'] = await test_ontology_statistics()
    
    # Test 3-5: Individual ontology searches
    results['snomed'] = await test_search_snomed()
    results['mesh'] = await test_search_mesh()
    results['icd10'] = await test_search_icd10()
    
    # Test 6: Multi-ontology search
    results['multi_ontology'] = await test_multi_ontology_search()
    
    # Test 7: Text mapping
    results['text_mapping'] = await test_text_mapping()
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\nTests passed: {passed}/{total}")
    print("\nDetailed results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    if passed == total:
        print("\n🎉 All tests passed! Ontologies are working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the errors above.")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
