#!/usr/bin/env python3
"""
Test Complete Semantic Flow
Valida el flux complet: RAG retrieval + Semantic coding + LLM generation
"""

import asyncio
import aiohttp
import logging
import json
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test cases amb termes que sabem que estan al fallback mínim
TEST_CASES = [
    {
        "name": "Diabetis + Metformina (Fallback)",
        "request": {
            "patient_context": "Pacient home de 65 anys amb antecedents de diabetis tipus 2",
            "admission_reason": "Descompensació diabètica amb hiperglucèmia",
            "procedures": ["Control glucèmic", "Ajust tractament antidiabètic"],
            "medications": ["Metformina 850mg", "Insulina NPH"],
            "evolution": "Milloria del control glucèmic",
            "discharge_plan": "Controls en endocrinologia",
            "language": "ca"
        },
        "expected_codes": {
            "snomed_diabetis": "73211009",
            "icd10_diabetis": "E11.9", 
            "atc_metformina": "A10BA02"
        }
    },
    {
        "name": "Hipertensió + Enalapril (Fallback)",
        "request": {
            "patient_context": "Pacient dona de 55 anys amb hipertensió arterial",
            "admission_reason": "Crisis hipertensiva amb cefalea intensa",
            "procedures": ["Monitorització tensional", "ECG"],
            "medications": ["Enalapril 10mg", "Hidroclorotiazida 25mg"],
            "evolution": "Normalització de la tensió arterial",
            "discharge_plan": "Controls en medicina interna",
            "language": "ca"
        },
        "expected_codes": {
            "snomed_hta": "38341003",
            "icd10_hta": "I10",
            "atc_enalapril": "C09AA02"
        }
    },
    {
        "name": "Infart + Adiro (Protocol SAS)",
        "request": {
            "patient_context": "Pacient home de 62 anys sense antecedents cardíacs",
            "admission_reason": "Dolor toràcic opressiu amb elevació de troponines",
            "procedures": ["Cateterisme cardíac", "Angioplàstia primària"],
            "medications": ["Adiro 100mg", "Atorvastatina 40mg"],
            "evolution": "Evolució favorable post-angioplàstia",
            "discharge_plan": "Controls en cardiologia",
            "language": "ca"
        },
        "expected_codes": {
            "snomed_infart": "57054005",
            "icd10_infart": "I21.9",
            "atc_adiro": "B01AC06"
        }
    }
]


async def test_complete_flow(session: aiohttp.ClientSession, test_case: Dict[str, Any]) -> Dict[str, Any]:
    """Test del flux complet per un cas específic"""
    logger.info(f"🧪 Testing: {test_case['name']}")
    
    try:
        # Call discharge summary endpoint
        async with session.post(
            "http://localhost:8000/generate/discharge-summary",
            json=test_case['request'],
            timeout=aiohttp.ClientTimeout(total=90)
        ) as response:
            
            if response.status != 200:
                error_text = await response.text()
                return {
                    'test_case': test_case['name'],
                    'status': 'error',
                    'error': f"HTTP {response.status}: {error_text}"
                }
            
            result = await response.json()
            
            # Analyze results
            analysis = {
                'test_case': test_case['name'],
                'status': 'success',
                'rag_retrieval': {
                    'sources_found': len(result.get('sources', [])),
                    'sources': [s.get('title', 'Unknown')[:50] + '...' for s in result.get('sources', [])[:3]]
                },
                'semantic_coding': {
                    'diagnoses_found': len(result.get('diagnoses', [])),
                    'medications_found': len(result.get('medications', [])),
                    'codes_found': {}
                },
                'llm_generation': {
                    'summary_generated': bool(result.get('generated_summary')),
                    'summary_length': len(result.get('generated_summary', ''))
                }
            }
            
            # Check specific codes
            expected = test_case['expected_codes']
            
            # Check diagnoses codes
            for diag in result.get('diagnoses', []):
                if diag.get('snomed_code'):
                    analysis['semantic_coding']['codes_found']['snomed'] = diag['snomed_code']
                if diag.get('icd10_code'):
                    analysis['semantic_coding']['codes_found']['icd10'] = diag['icd10_code']
            
            # Check medication codes
            for med in result.get('medications', []):
                if med.get('atc_code'):
                    med_name = med.get('name', '').lower()
                    if 'metformina' in med_name:
                        analysis['semantic_coding']['codes_found']['atc_metformina'] = med['atc_code']
                    elif 'enalapril' in med_name:
                        analysis['semantic_coding']['codes_found']['atc_enalapril'] = med['atc_code']
                    elif 'adiro' in med_name:
                        analysis['semantic_coding']['codes_found']['atc_adiro'] = med['atc_code']
            
            # Validate expected codes
            validation = {}
            for key, expected_code in expected.items():
                found_code = analysis['semantic_coding']['codes_found'].get(key.replace('_', '_').split('_')[1])
                validation[key] = {
                    'expected': expected_code,
                    'found': found_code,
                    'match': found_code == expected_code
                }
            
            analysis['validation'] = validation
            
            # Log results
            logger.info(f"   📊 RAG: {analysis['rag_retrieval']['sources_found']} sources")
            logger.info(f"   🔍 Coding: {analysis['semantic_coding']['diagnoses_found']} diagnoses, {analysis['semantic_coding']['medications_found']} medications")
            logger.info(f"   📝 LLM: {analysis['llm_generation']['summary_length']} chars generated")
            
            # Log code validation
            for key, val in validation.items():
                status = "✅" if val['match'] else "❌"
                logger.info(f"   {status} {key}: expected {val['expected']}, found {val['found']}")
            
            return analysis
            
    except Exception as e:
        logger.error(f"❌ Error testing {test_case['name']}: {e}")
        return {
            'test_case': test_case['name'],
            'status': 'exception',
            'error': str(e)
        }


async def check_qdrant_status():
    """Check Qdrant collection status"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:6333/collections/healthcare_rag") as response:
                if response.status == 200:
                    data = await response.json()
                    count = data['result']['points_count']
                    logger.info(f"✅ Qdrant collection 'healthcare_rag': {count} documents")
                    return True
                else:
                    logger.error(f"❌ Qdrant collection error: HTTP {response.status}")
                    return False
    except Exception as e:
        logger.error(f"❌ Cannot connect to Qdrant: {e}")
        return False


async def main():
    """Test principal del flux complet"""
    logger.info("🚀 Testing Complete Semantic Flow...")
    
    # Check Qdrant status
    if not await check_qdrant_status():
        logger.error("❌ Qdrant is not available")
        return
    
    # Check API health
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/health") as response:
                if response.status != 200:
                    logger.error("❌ API is not available")
                    return
                logger.info("✅ API is running")
    except Exception as e:
        logger.error(f"❌ Cannot connect to API: {e}")
        return
    
    # Run tests
    results = []
    
    async with aiohttp.ClientSession() as session:
        for test_case in TEST_CASES:
            result = await test_complete_flow(session, test_case)
            results.append(result)
            print()  # Separator
    
    # Summary
    logger.info("📊 COMPLETE FLOW TEST SUMMARY:")
    
    success_count = sum(1 for r in results if r['status'] == 'success')
    total_count = len(results)
    
    for result in results:
        status_icon = "✅" if result['status'] == 'success' else "❌"
        logger.info(f"   {status_icon} {result['test_case']}")
        
        if result['status'] == 'success':
            # Count successful validations
            validations = result.get('validation', {})
            matches = sum(1 for v in validations.values() if v.get('match', False))
            total_validations = len(validations)
            logger.info(f"      Code validation: {matches}/{total_validations} correct")
    
    logger.info(f"🎯 Overall: {success_count}/{total_count} test cases successful")
    
    # Save detailed results
    with open('test_results_complete_flow.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    logger.info("📁 Detailed results saved to: test_results_complete_flow.json")
    
    # Final assessment
    if success_count == total_count:
        logger.info("🎉 Complete semantic flow is working!")
    else:
        logger.warning("⚠️ Some test cases failed. Check logs above.")


if __name__ == "__main__":
    asyncio.run(main())
