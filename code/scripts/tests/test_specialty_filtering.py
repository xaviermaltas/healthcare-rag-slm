"""
Test Specialty Filtering
Verifica que el filtratge semàntic per especialitat funciona correctament
"""

import requests
import json
from typing import Dict, Any


API_URL = "http://localhost:8000"


def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def test_specialty_detection(case: Dict[str, Any], expected_specialty: str):
    """
    Test specialty detection and filtering
    
    Args:
        case: Clinical case data
        expected_specialty: Expected detected specialty
    """
    print(f"📋 Testing: {case['name']}")
    print(f"   Expected specialty: {expected_specialty}")
    
    # Send request
    response = requests.post(
        f"{API_URL}/generate/discharge-summary",
        json=case['request'],
        timeout=120
    )
    
    if response.status_code != 200:
        print(f"   ❌ ERROR: {response.status_code}")
        print(f"   {response.text}")
        return False
    
    data = response.json()
    metadata = data.get('generation_metadata', {})
    
    detected = metadata.get('specialty_detected')
    confidence = metadata.get('specialty_confidence', 0)
    matched_terms = metadata.get('specialty_matched_terms', [])
    protocols_count = metadata.get('protocols_retrieved', 0)
    
    print(f"   ✅ Detected: {detected} (confidence: {confidence:.2f})")
    print(f"   📝 Matched terms: {', '.join(matched_terms)}")
    print(f"   📚 Protocols retrieved: {protocols_count}")
    
    # Verify specialty
    if detected == expected_specialty:
        print(f"   ✅ PASS - Specialty correctly detected")
    else:
        print(f"   ⚠️  WARNING - Expected {expected_specialty}, got {detected}")
    
    # Verify protocols are from correct specialty
    sources = data.get('sources', [])
    if sources:
        print(f"\n   📖 Retrieved protocols:")
        for i, source in enumerate(sources[:3], 1):
            specialty_match = "✅" if source['specialty'] == detected else "⚠️"
            print(f"      {i}. {source['title']}")
            print(f"         Specialty: {source['specialty']} {specialty_match}")
            print(f"         Score: {source['score']:.4f}")
    
    return detected == expected_specialty


def main():
    """Run specialty filtering tests"""
    
    print_section("🧪 SPECIALTY FILTERING TESTS")
    
    # Test cases for different specialties
    test_cases = [
        {
            'name': 'Cardiology - Acute Myocardial Infarction',
            'expected_specialty': 'Cardiologia',
            'request': {
                'patient_context': 'Home de 65 anys amb antecedents de hipertensió arterial i dislipèmia',
                'admission_reason': 'Dolor toràcic opressiu d\'inici sobtat amb elevació de troponines i elevació del segment ST en ECG',
                'procedures': [
                    'ECG de 12 derivacions',
                    'Coronariografia urgent',
                    'Angioplastia primària amb stent'
                ],
                'current_medications': [
                    'Enalapril 10mg/24h',
                    'Atorvastatina 40mg/24h',
                    'AAS 100mg/24h'
                ],
                'language': 'ca'
            }
        },
        {
            'name': 'Endocrinology - Diabetes Mellitus',
            'expected_specialty': 'Endocrinologia',
            'request': {
                'patient_context': 'Dona de 58 anys amb obesitat i antecedents familiars de diabetis',
                'admission_reason': 'Hiperglucèmia descompensada amb glucèmia de 450 mg/dL i cetoacidosi diabètica',
                'procedures': [
                    'Analítica completa amb glucèmia i HbA1c',
                    'Gasometria arterial',
                    'Monitorització contínua de glucosa'
                ],
                'current_medications': [
                    'Metformina 850mg/12h',
                    'Insulina glargina 20 UI/24h'
                ],
                'language': 'ca'
            }
        },
        {
            'name': 'Neurology - Ischemic Stroke',
            'expected_specialty': 'Neurologia',
            'request': {
                'patient_context': 'Home de 72 anys amb fibril·lació auricular i hipertensió arterial',
                'admission_reason': 'Debilitat sobtada de hemicòs dret i disàrtria d\'inici fa 3 hores. Escala NIHSS: 8 punts',
                'procedures': [
                    'TAC cranial urgent',
                    'Ressonància magnètica cerebral',
                    'Doppler de troncs supraaòrtics',
                    'Trombòlisi intravenosa'
                ],
                'current_medications': [
                    'Acenocumarol segons pauta INR',
                    'Enalapril 10mg/12h',
                    'Atorvastatina 40mg/24h'
                ],
                'language': 'ca'
            }
        },
        {
            'name': 'Internal Medicine - Pneumonia',
            'expected_specialty': 'Medicina Interna',
            'request': {
                'patient_context': 'Dona de 68 anys amb EPOC i tabaquisme actiu',
                'admission_reason': 'Febre de 39°C, tos productiva i dispnea. Radiografia toràcica amb infiltrat a lòbul inferior dret',
                'procedures': [
                    'Radiografia toràcica',
                    'Analítica amb hemograma i PCR',
                    'Gasometria arterial',
                    'Hemocultius'
                ],
                'current_medications': [
                    'Amoxicil·lina-clavulànic 1g/8h IV',
                    'Salbutamol inhalat'
                ],
                'language': 'ca'
            }
        }
    ]
    
    # Run tests
    results = []
    for case in test_cases:
        try:
            result = test_specialty_detection(case, case['expected_specialty'])
            results.append(result)
            print()
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results.append(False)
            print()
    
    # Summary
    print_section("📊 TEST SUMMARY")
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}\n")
    
    for i, (case, result) in enumerate(zip(test_cases, results), 1):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {case['name']}")
    
    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    return passed == total


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
