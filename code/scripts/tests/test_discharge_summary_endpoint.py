#!/usr/bin/env python3
"""
Test script for /generate/discharge-summary endpoint
Tests with 3 clinical cases: Myocardial Infarction, Diabetes, Stroke
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any


API_URL = "http://localhost:8000"
ENDPOINT = f"{API_URL}/generate/discharge-summary"


def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def test_discharge_summary(case_name: str, request_data: Dict[str, Any]):
    """Test discharge summary generation"""
    
    print_section(f"TEST CASE: {case_name}")
    
    print("📤 REQUEST:")
    print(json.dumps(request_data, indent=2, ensure_ascii=False))
    
    print("\n🔄 Sending request...")
    start_time = datetime.now()
    
    try:
        response = requests.post(
            ENDPOINT,
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"✅ Response received in {duration:.2f}s")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n📄 SUMMARY (first 500 chars):")
            print("-" * 80)
            print(result['summary'][:500] + "...")
            print("-" * 80)
            
            print("\n🏥 DIAGNOSES:")
            for i, diag in enumerate(result.get('diagnoses', []), 1):
                print(f"  {i}. {diag.get('description', 'N/A')}")
                if diag.get('snomed_code'):
                    print(f"     SNOMED CT: {diag['snomed_code']}")
                if diag.get('icd10_code'):
                    print(f"     ICD-10: {diag['icd10_code']}")
            
            print("\n💊 MEDICATIONS:")
            for i, med in enumerate(result.get('medications', []), 1):
                print(f"  {i}. {med.get('name', 'N/A')} - {med.get('dosage', 'N/A')}")
                if med.get('atc_code'):
                    print(f"     ATC: {med['atc_code']}")
            
            print("\n📚 SOURCES (Protocols Retrieved):")
            for i, source in enumerate(result.get('sources', []), 1):
                print(f"  {i}. {source['title']}")
                print(f"     Specialty: {source['specialty']}")
                print(f"     Score: {source['score']:.4f}")
                print(f"     Official: {source['official']}")
            
            print("\n✔️ VALIDATION STATUS:")
            validation = result.get('validation_status', {})
            print(f"  All sections present: {validation.get('all_sections_present', False)}")
            print(f"  Has diagnoses: {validation.get('has_diagnoses', False)}")
            print(f"  Has medications: {validation.get('has_medications', False)}")
            print(f"  Has follow-up: {validation.get('has_follow_up', False)}")
            if validation.get('missing_sections'):
                print(f"  Missing sections: {', '.join(validation['missing_sections'])}")
            
            print("\n📊 METADATA:")
            metadata = result.get('generation_metadata', {})
            print(f"  Generation time: {metadata.get('generation_time_seconds', 0):.2f}s")
            print(f"  Protocols retrieved: {metadata.get('protocols_retrieved', 0)}")
            print(f"  Language: {metadata.get('language', 'N/A')}")
            print(f"  Model: {metadata.get('model', 'N/A')}")
            
            return True
        
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(response.text)
            return False
    
    except requests.exceptions.Timeout:
        print("❌ ERROR: Request timeout (>60s)")
        return False
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all test cases"""
    
    print_section("DISCHARGE SUMMARY ENDPOINT TEST")
    print(f"API URL: {API_URL}")
    print(f"Endpoint: {ENDPOINT}")
    
    # Check API is running
    try:
        health_response = requests.get(f"{API_URL}/", timeout=5)
        if health_response.status_code != 200:
            print("❌ API is not running!")
            return
        print("✅ API is running")
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return
    
    # ========================================================================
    # TEST CASE 1: MYOCARDIAL INFARCTION
    # ========================================================================
    
    case1_request = {
        "patient_context": "Pacient home de 65 anys amb antecedents de hipertensió arterial i dislipèmia en tractament. No fumador des de fa 10 anys. Vida activa.",
        "admission_reason": "Dolor toràcic opressiu d'inici sobtat amb irradiació a braç esquerre, acompanyat de diaforesi i dispnea. Elevació de troponines (cTnI: 15 ng/mL).",
        "procedures": [
            "ECG de 12 derivacions amb elevació del segment ST en derivacions inferiors",
            "Analítica completa amb troponines seriades",
            "Ecocardiograma transtorácic (FEVI 45%, hipocinèsia inferior)",
            "Coronariografia urgent",
            "Angioplastia primària amb implantació de stent farmacoactiu en artèria coronària dreta"
        ],
        "current_medications": [
            "AAS 100mg/24h",
            "Clopidogrel 75mg/24h durant 12 mesos",
            "Atorvastatina 80mg/24h",
            "Ramipril 5mg/24h",
            "Bisoprolol 5mg/24h"
        ],
        "language": "es",
        "specialty": "Cardiologia"
    }
    
    result1 = test_discharge_summary("Infart Agut de Miocardi", case1_request)
    
    # ========================================================================
    # TEST CASE 2: DECOMPENSATED DIABETES
    # ========================================================================
    
    case2_request = {
        "patient_context": "Pacient dona de 58 anys amb diabetis mellitus tipus 2 de 12 anys d'evolució, obesitat (IMC 34), hipertensió arterial.",
        "admission_reason": "Hiperglucèmia severa (glucèmia 450 mg/dL) amb cetosi, poliúria, polidipsia i pèrdua de pes de 5 kg en 2 setmanes.",
        "procedures": [
            "Analítica completa amb hemoglobina glicada (HbA1c: 11.2%)",
            "Gasometria venosa",
            "Perfil lipídic",
            "Funció renal i hepàtica",
            "Fons d'ull per descartar retinopatia"
        ],
        "current_medications": [
            "Insulina glargina 24 UI/24h subcutània",
            "Insulina ràpida segons pauta correctora",
            "Metformina 850mg/12h",
            "Enalapril 10mg/24h",
            "Atorvastatina 20mg/24h"
        ],
        "language": "ca",
        "specialty": "Endocrinologia"
    }
    
    result2 = test_discharge_summary("Diabetis Mellitus Descompensada", case2_request)
    
    # ========================================================================
    # TEST CASE 3: ISCHEMIC STROKE
    # ========================================================================
    
    case3_request = {
        "patient_context": "Pacient home de 72 anys amb antecedents de fibril·lació auricular, hipertensió arterial, dislipèmia. En tractament anticoagulant.",
        "admission_reason": "Debilitat sobtada de hemicòs dret i disàrtria d'inici fa 3 hores. Escala NIHSS: 8 punts.",
        "procedures": [
            "TC cranial urgent (descarta hemorràgia)",
            "Analítica completa amb coagulació",
            "ECG (confirma fibril·lació auricular)",
            "Ecocardiograma transtorácic",
            "Dúplex de troncs supraaòrtics",
            "RM cerebral (infart isquèmic en territori ACM esquerra)"
        ],
        "current_medications": [
            "Acenocumarol segons pauta INR",
            "Enalapril 10mg/12h",
            "Atorvastatina 40mg/24h",
            "Bisoprolol 2.5mg/24h"
        ],
        "language": "es",
        "specialty": "Neurologia"
    }
    
    result3 = test_discharge_summary("Accident Cerebrovascular Isquèmic", case3_request)
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    
    print_section("TEST SUMMARY")
    
    results = [
        ("Infart Agut de Miocardi", result1),
        ("Diabetis Mellitus Descompensada", result2),
        ("Accident Cerebrovascular Isquèmic", result3)
    ]
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    print()
    
    for case_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {case_name}")
    
    print()
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
    else:
        print(f"⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    main()
