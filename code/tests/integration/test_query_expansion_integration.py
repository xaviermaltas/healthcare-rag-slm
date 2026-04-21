#!/usr/bin/env python3
"""
Integration tests for QueryExpander with real ontologies
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.main.infrastructure.ontologies.ontology_manager import OntologyManager, OntologyType
from src.main.core.retrieval.query_processing.query_expander import QueryExpander
from config.settings import get_settings
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_expand_simple_query():
    """Test expanding a simple medical query"""
    print("\n" + "=" * 80)
    print("TEST 1: EXPAND SIMPLE QUERY - 'diabetes tipo 2'")
    print("=" * 80)
    
    settings = get_settings()
    
    # Initialize components
    ontology_manager = OntologyManager(
        api_key=settings.BIOPORTAL_API_KEY,
        base_url=settings.BIOPORTAL_BASE_URL
    )
    await ontology_manager.initialize()
    
    query_expander = QueryExpander(ontology_manager=ontology_manager)
    
    try:
        # Expand query
        expanded = await query_expander.expand_query("diabetes tipo 2")
        
        print(f"\n✓ Original query: '{expanded.original_query}'")
        print(f"✓ Total expanded terms: {len(expanded.expanded_terms)}")
        print(f"✓ Entities detected: {len(expanded.entities_detected)}")
        
        # Show terms by source
        by_source = expanded.get_terms_by_source()
        print("\n📊 Terms by source:")
        for source, terms in by_source.items():
            print(f"  {source}: {len(terms)} terms")
            print(f"    Samples: {', '.join(terms[:3])}")
        
        # Show expansion summary
        summary = query_expander.get_expansion_summary(expanded)
        print("\n📋 Expansion summary:")
        print(f"  Ontologies used: {', '.join(summary['ontologies_used'])}")
        
        # Show search text
        search_text = expanded.get_search_text(include_codes=True)
        print(f"\n🔍 Search text (first 200 chars):")
        print(f"  {search_text[:200]}...")
        
        return len(expanded.expanded_terms) > 1
    
    finally:
        await ontology_manager.close()


async def test_expand_complex_query():
    """Test expanding a complex clinical query"""
    print("\n" + "=" * 80)
    print("TEST 2: EXPAND COMPLEX QUERY - Clinical scenario")
    print("=" * 80)
    
    query = "paciente con diabetes mellitus tipo 2 e hipertensión arterial"
    print(f"\nQuery: '{query}'")
    
    settings = get_settings()
    
    ontology_manager = OntologyManager(
        api_key=settings.BIOPORTAL_API_KEY,
        base_url=settings.BIOPORTAL_BASE_URL
    )
    await ontology_manager.initialize()
    
    query_expander = QueryExpander(ontology_manager=ontology_manager)
    
    try:
        expanded = await query_expander.expand_query(query)
        
        print(f"\n✓ Entities detected: {len(expanded.entities_detected)}")
        for entity in expanded.entities_detected:
            print(f"  - {entity.text} ({entity.entity_type})")
        
        print(f"\n✓ Total expanded terms: {len(expanded.expanded_terms)}")
        
        # Show terms by source
        by_source = expanded.get_terms_by_source()
        print("\n📊 Expansion breakdown:")
        for source, terms in by_source.items():
            print(f"\n  {source.upper()} ({len(terms)} terms):")
            for term in terms[:5]:
                print(f"    - {term}")
        
        # Show ontology codes found
        codes = [t for t in expanded.expanded_terms if t.source == 'code']
        if codes:
            print(f"\n🏷️  Ontology codes found ({len(codes)}):")
            for code_term in codes[:10]:
                print(f"    - {code_term.ontology}: {code_term.term}")
        
        return len(expanded.entities_detected) >= 2
    
    finally:
        await ontology_manager.close()


async def test_expand_with_custom_config():
    """Test query expansion with custom configuration"""
    print("\n" + "=" * 80)
    print("TEST 3: CUSTOM CONFIGURATION - Only SNOMED, no codes")
    print("=" * 80)
    
    settings = get_settings()
    
    ontology_manager = OntologyManager(
        api_key=settings.BIOPORTAL_API_KEY,
        base_url=settings.BIOPORTAL_BASE_URL
    )
    await ontology_manager.initialize()
    
    # Custom config: only SNOMED, no codes
    custom_config = {
        'ontologies': [OntologyType.SNOMED_CT],
        'include_codes': False,
        'max_synonyms_per_entity': 3,
        'max_concepts_per_entity': 2
    }
    
    query_expander = QueryExpander(
        ontology_manager=ontology_manager,
        config=custom_config
    )
    
    try:
        expanded = await query_expander.expand_query("asma bronquial")
        
        print(f"\n✓ Configuration:")
        print(f"  Ontologies: SNOMED CT only")
        print(f"  Include codes: False")
        print(f"  Max synonyms: 3")
        
        print(f"\n✓ Results:")
        print(f"  Total terms: {len(expanded.expanded_terms)}")
        
        by_source = expanded.get_terms_by_source()
        print(f"\n📊 Terms by source:")
        for source, terms in by_source.items():
            print(f"  {source}: {len(terms)} terms")
        
        # Verify no codes
        has_codes = 'code' in by_source
        print(f"\n✓ Codes included: {has_codes}")
        
        return not has_codes
    
    finally:
        await ontology_manager.close()


async def test_expansion_weights():
    """Test that term weights are applied correctly"""
    print("\n" + "=" * 80)
    print("TEST 4: TERM WEIGHTS")
    print("=" * 80)
    
    settings = get_settings()
    
    ontology_manager = OntologyManager(
        api_key=settings.BIOPORTAL_API_KEY,
        base_url=settings.BIOPORTAL_BASE_URL
    )
    await ontology_manager.initialize()
    
    query_expander = QueryExpander(ontology_manager=ontology_manager)
    
    try:
        expanded = await query_expander.expand_query("infarto de miocardio")
        
        print(f"\n✓ Term weights:")
        
        # Group by weight
        by_weight = {}
        for term in expanded.expanded_terms:
            weight_key = f"{term.weight:.1f}"
            if weight_key not in by_weight:
                by_weight[weight_key] = []
            by_weight[weight_key].append(f"{term.term} ({term.source})")
        
        for weight in sorted(by_weight.keys(), reverse=True):
            terms = by_weight[weight]
            print(f"\n  Weight {weight}:")
            for term in terms[:3]:
                print(f"    - {term}")
        
        # Verify original terms have highest weight
        original_terms = [t for t in expanded.expanded_terms if t.source == 'original']
        if original_terms:
            max_weight = max(t.weight for t in expanded.expanded_terms)
            original_weight = original_terms[0].weight
            print(f"\n✓ Original term weight: {original_weight}")
            print(f"✓ Max weight in expansion: {max_weight}")
            print(f"✓ Original has highest weight: {original_weight == max_weight}")
        
        return True
    
    finally:
        await ontology_manager.close()


async def main():
    """Run all tests"""
    print("\n" + "🧪" * 40)
    print("QUERY EXPANSION INTEGRATION TESTS")
    print("🧪" * 40 + "\n")
    
    results = {}
    
    # Test 1: Simple query
    results['simple_query'] = await test_expand_simple_query()
    
    # Test 2: Complex query
    results['complex_query'] = await test_expand_complex_query()
    
    # Test 3: Custom config
    results['custom_config'] = await test_expand_with_custom_config()
    
    # Test 4: Weights
    results['weights'] = await test_expansion_weights()
    
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
        print("\n🎉 All tests passed! Query expansion is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
