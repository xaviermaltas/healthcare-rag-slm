#!/usr/bin/env python3
"""
Test Semantic Endpoints
Valida que els endpoints usin la nova arquitectura semàntica
"""

import asyncio
import aiohttp
import logging
import json
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test data
DISCHARGE_SUMMARY_REQUEST = {
    "patient_context": "Pacient home de 65 anys amb antecedents de hipertensió arterial i diabetis tipus 2",
    "admission_reason": "Dolor toràcic opressiu amb elevació de troponines",
    "procedures": [
        "Cateterisme cardíac amb angioplàstia primària",
        "Implantació d'stent farmacoactiu a artèria descendant anterior"
    ],
    "medications": [
        "Atorvastatina 40mg",
        "Metformina 850mg",
        "Enalapril 10mg",
        "Adiro 100mg"
    ],
    "evolution": "Evolució favorable amb resolució del dolor toràcic",
    "discharge_plan": "Controls ambulatoris en cardiologia i endocrinologia",
    "language": "ca"
}

REFERRAL_REQUEST = {
    "patient_context": "Pacient dona de 45 anys amb antecedents familiars de càncer de mama",
    "referral_reason": "Nòdul mamari palpable de nova aparició",
    "clinical_findings": [
        "Nòdul de 2cm a quadrant superoextern mama dreta",
        "Consistència dura, adherit a plans profunds"
    ],
    "previous_tests": [
        "Ecografia mamària: massa sòlida hipoecogènica",
        "Mamografia: densitat asimètrica"
    ],
    "urgency": "preferent",
    "target_specialty": "oncologia",
    "language": "ca"
}


async def test_endpoint(
    session: aiohttp.ClientSession,
    endpoint: str,
    request_data: Dict[str, Any],
    endpoint_name: str
) -> Dict[str, Any]:
    """Test individual endpoint"""
    logger.info(f"🧪 Testing {endpoint_name} endpoint...")
    
    try:
        async with session.post(
            f"http://localhost:8000{endpoint}",
            json=request_data,
            timeout=aiohttp.ClientTimeout(total=60)
        ) as response:
            
            if response.status == 200:
                result = await response.json()
                logger.info(f"✅ {endpoint_name} endpoint: SUCCESS")
                
                # Analyze semantic coding results
                if 'diagnoses' in result:
                    diagnoses = result['diagnoses']
                    logger.info(f"   📋 Diagnoses found: {len(diagnoses)}")
                    for diag in diagnoses[:3]:  # Show first 3
                        snomed = diag.get('snomed_code', 'None')
                        icd10 = diag.get('icd10_code', 'None')
                        logger.info(f"      - {diag.get('description', 'N/A')[:50]}...")
                        logger.info(f"        SNOMED: {snomed} | ICD-10: {icd10}")
                
                if 'medications' in result:
                    medications = result['medications']
                    logger.info(f"   💊 Medications found: {len(medications)}")
                    for med in medications[:3]:  # Show first 3
                        atc = med.get('atc_code', 'None')
                        logger.info(f"      - {med.get('name', 'N/A')}: ATC {atc}")
                
                if 'referral_reason_codes' in result:
                    codes = result['referral_reason_codes']
                    logger.info(f"   🎯 Referral codes found: {len(codes)}")
                    for code in codes:
                        snomed = code.get('snomed_code', 'None')
                        conf = code.get('confidence', 0)
                        logger.info(f"      - SNOMED: {snomed} (confidence: {conf:.2f})")
                
                return {
                    'status': 'success',
                    'endpoint': endpoint_name,
                    'response': result
                }
                
            else:
                error_text = await response.text()
                logger.error(f"❌ {endpoint_name} endpoint: HTTP {response.status}")
                logger.error(f"   Error: {error_text}")
                return {
                    'status': 'error',
                    'endpoint': endpoint_name,
                    'error': f"HTTP {response.status}: {error_text}"
                }
                
    except asyncio.TimeoutError:
        logger.error(f"❌ {endpoint_name} endpoint: TIMEOUT")
        return {
            'status': 'timeout',
            'endpoint': endpoint_name,
            'error': 'Request timeout'
        }
    except Exception as e:
        logger.error(f"❌ {endpoint_name} endpoint: EXCEPTION - {e}")
        return {
            'status': 'exception',
            'endpoint': endpoint_name,
            'error': str(e)
        }


async def check_api_health() -> bool:
    """Check if API is running"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/health") as response:
                if response.status == 200:
                    logger.info("✅ API is running")
                    return True
                else:
                    logger.error(f"❌ API health check failed: HTTP {response.status}")
                    return False
    except Exception as e:
        logger.error(f"❌ Cannot connect to API: {e}")
        return False


async def main():
    """Test principal"""
    logger.info("🚀 Testing Semantic Medical Coding Endpoints...")
    
    # Check API health
    if not await check_api_health():
        logger.error("❌ API is not available. Please start the system first:")
        logger.error("   ./scripts/lifecycle/start.sh")
        return
    
    results = []
    
    async with aiohttp.ClientSession() as session:
        # Test discharge summary endpoint
        discharge_result = await test_endpoint(
            session,
            "/generate/discharge-summary",
            DISCHARGE_SUMMARY_REQUEST,
            "Discharge Summary"
        )
        results.append(discharge_result)
        
        print()  # Separator
        
        # Test referral endpoint
        referral_result = await test_endpoint(
            session,
            "/generate/referral",
            REFERRAL_REQUEST,
            "Referral"
        )
        results.append(referral_result)
    
    # Summary
    print()
    logger.info("📊 TEST SUMMARY:")
    success_count = sum(1 for r in results if r['status'] == 'success')
    total_count = len(results)
    
    for result in results:
        status_icon = "✅" if result['status'] == 'success' else "❌"
        logger.info(f"   {status_icon} {result['endpoint']}: {result['status'].upper()}")
        if result['status'] != 'success':
            logger.info(f"      Error: {result.get('error', 'Unknown')}")
    
    logger.info(f"🎯 Overall: {success_count}/{total_count} endpoints successful")
    
    if success_count == total_count:
        logger.info("🎉 All endpoints are working with SEMANTIC architecture!")
    else:
        logger.warning("⚠️ Some endpoints failed. Check logs above.")
    
    # Save detailed results
    with open('test_results_semantic_endpoints.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    logger.info("📁 Detailed results saved to: test_results_semantic_endpoints.json")


if __name__ == "__main__":
    asyncio.run(main())
