#!/usr/bin/env python3
"""
Test Ontology Semantic Retrieval
Valida que el retrieval semàntic d'ontologies funciona correctament
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.main.infrastructure.vector_db.qdrant_client import HealthcareQdrantClient
from src.main.infrastructure.embeddings.bge_m3 import BGEM3Embeddings
from src.main.core.ontology.ontology_indexer import OntologyRetriever

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_snomed_retrieval():
    """Test SNOMED CT semantic retrieval"""
    logger.info("\n" + "="*80)
    logger.info("🔍 TEST 1: SNOMED CT Retrieval")
    logger.info("="*80)
    
    # Initialize
    qdrant_client = HealthcareQdrantClient(collection_name="medical_ontologies")
    await qdrant_client.initialize()
    
    embeddings_model = BGEM3Embeddings()
    await embeddings_model.initialize()
    
    retriever = OntologyRetriever(qdrant_client, embeddings_model)
    
    # Test cases
    test_cases = [
        ("diabetis", "73211009"),  # Diabetes mellitus
        ("hipertensió", "38341003"),  # Hypertensive disorder
        ("infart de miocardi", "57054005"),  # Acute myocardial infarction
        ("pneumònia", "233604007"),  # Pneumonia
        ("asma", "195967001"),  # Asthma
        ("COVID-19", "840539006"),  # COVID-19
    ]
    
    results = []
    for term, expected_code in test_cases:
        logger.info(f"\n🔎 Cercant: '{term}'")
        matches = await retriever.search_snomed(term, limit=3)
        
        if matches:
            top_match = matches[0]
            logger.info(f"  ✅ Top match: {top_match['code']} - {top_match['term']} (score: {top_match['score']:.3f})")
            
            # Check if expected code is in top 3
            found = any(m['code'] == expected_code for m in matches)
            results.append({
                'term': term,
                'expected': expected_code,
                'found': found,
                'top_code': top_match['code'],
                'top_score': top_match['score']
            })
            
            if found:
                logger.info(f"  ✅ Expected code {expected_code} found in top 3")
            else:
                logger.warning(f"  ⚠️ Expected code {expected_code} NOT in top 3")
        else:
            logger.error(f"  ❌ No matches found for '{term}'")
            results.append({
                'term': term,
                'expected': expected_code,
                'found': False,
                'top_code': None,
                'top_score': 0.0
            })
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("📊 SNOMED CT RESULTS")
    logger.info("="*80)
    success_rate = sum(1 for r in results if r['found']) / len(results) * 100
    logger.info(f"Success rate: {success_rate:.1f}% ({sum(1 for r in results if r['found'])}/{len(results)})")
    
    return results


async def test_icd10_retrieval():
    """Test ICD-10 semantic retrieval"""
    logger.info("\n" + "="*80)
    logger.info("🔍 TEST 2: ICD-10 Retrieval")
    logger.info("="*80)
    
    # Initialize
    qdrant_client = HealthcareQdrantClient(collection_name="medical_ontologies")
    await qdrant_client.initialize()
    
    embeddings_model = BGEM3Embeddings()
    await embeddings_model.initialize()
    
    retriever = OntologyRetriever(qdrant_client, embeddings_model)
    
    # Test cases
    test_cases = [
        ("diabetis tipus 2", "E11.9"),
        ("hipertensió essencial", "I10"),
        ("infart agut de miocardi", "I21.9"),
        ("pneumònia", "J18.9"),
        ("asma", "J45.909"),
    ]
    
    results = []
    for term, expected_code in test_cases:
        logger.info(f"\n🔎 Cercant: '{term}'")
        matches = await retriever.search_icd10(term, limit=3)
        
        if matches:
            top_match = matches[0]
            logger.info(f"  ✅ Top match: {top_match['code']} - {top_match['term']} (score: {top_match['score']:.3f})")
            
            found = any(m['code'] == expected_code for m in matches)
            results.append({
                'term': term,
                'expected': expected_code,
                'found': found,
                'top_code': top_match['code'],
                'top_score': top_match['score']
            })
            
            if found:
                logger.info(f"  ✅ Expected code {expected_code} found in top 3")
            else:
                logger.warning(f"  ⚠️ Expected code {expected_code} NOT in top 3")
        else:
            logger.error(f"  ❌ No matches found for '{term}'")
            results.append({
                'term': term,
                'expected': expected_code,
                'found': False,
                'top_code': None,
                'top_score': 0.0
            })
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("📊 ICD-10 RESULTS")
    logger.info("="*80)
    success_rate = sum(1 for r in results if r['found']) / len(results) * 100
    logger.info(f"Success rate: {success_rate:.1f}% ({sum(1 for r in results if r['found'])}/{len(results)})")
    
    return results


async def test_atc_retrieval():
    """Test ATC semantic retrieval"""
    logger.info("\n" + "="*80)
    logger.info("🔍 TEST 3: ATC Retrieval")
    logger.info("="*80)
    
    # Initialize
    qdrant_client = HealthcareQdrantClient(collection_name="medical_ontologies")
    await qdrant_client.initialize()
    
    embeddings_model = BGEM3Embeddings()
    await embeddings_model.initialize()
    
    retriever = OntologyRetriever(qdrant_client, embeddings_model)
    
    # Test cases
    test_cases = [
        ("metformina", "A10BA02"),
        ("enalapril", "C09AA02"),
        ("atorvastatina", "C10AA05"),
        ("omeprazol", "A02BC01"),
        ("paracetamol", "N02BE01"),
        ("ibuprofè", "M01AE01"),
    ]
    
    results = []
    for term, expected_code in test_cases:
        logger.info(f"\n🔎 Cercant: '{term}'")
        matches = await retriever.search_atc(term, limit=3)
        
        if matches:
            top_match = matches[0]
            logger.info(f"  ✅ Top match: {top_match['code']} - {top_match['term']} (score: {top_match['score']:.3f})")
            
            found = any(m['code'] == expected_code for m in matches)
            results.append({
                'term': term,
                'expected': expected_code,
                'found': found,
                'top_code': top_match['code'],
                'top_score': top_match['score']
            })
            
            if found:
                logger.info(f"  ✅ Expected code {expected_code} found in top 3")
            else:
                logger.warning(f"  ⚠️ Expected code {expected_code} NOT in top 3")
        else:
            logger.error(f"  ❌ No matches found for '{term}'")
            results.append({
                'term': term,
                'expected': expected_code,
                'found': False,
                'top_code': None,
                'top_score': 0.0
            })
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("📊 ATC RESULTS")
    logger.info("="*80)
    success_rate = sum(1 for r in results if r['found']) / len(results) * 100
    logger.info(f"Success rate: {success_rate:.1f}% ({sum(1 for r in results if r['found'])}/{len(results)})")
    
    return results


async def main():
    """Run all ontology retrieval tests"""
    logger.info("🚀 Starting Ontology Retrieval Tests")
    
    try:
        # Run tests
        snomed_results = await test_snomed_retrieval()
        icd10_results = await test_icd10_retrieval()
        atc_results = await test_atc_retrieval()
        
        # Overall summary
        logger.info("\n" + "="*80)
        logger.info("📊 OVERALL SUMMARY")
        logger.info("="*80)
        
        total_tests = len(snomed_results) + len(icd10_results) + len(atc_results)
        total_success = (
            sum(1 for r in snomed_results if r['found']) +
            sum(1 for r in icd10_results if r['found']) +
            sum(1 for r in atc_results if r['found'])
        )
        
        overall_rate = total_success / total_tests * 100
        
        logger.info(f"SNOMED CT: {sum(1 for r in snomed_results if r['found'])}/{len(snomed_results)} ✅")
        logger.info(f"ICD-10:    {sum(1 for r in icd10_results if r['found'])}/{len(icd10_results)} ✅")
        logger.info(f"ATC:       {sum(1 for r in atc_results if r['found'])}/{len(atc_results)} ✅")
        logger.info(f"\n🎯 Overall Success Rate: {overall_rate:.1f}% ({total_success}/{total_tests})")
        
        if overall_rate >= 80:
            logger.info("✅ TESTS PASSED - Semantic retrieval working well!")
        elif overall_rate >= 60:
            logger.warning("⚠️ TESTS PARTIAL - Semantic retrieval needs improvement")
        else:
            logger.error("❌ TESTS FAILED - Semantic retrieval not working properly")
        
    except Exception as e:
        logger.error(f"❌ Error running tests: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
