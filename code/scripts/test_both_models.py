#!/usr/bin/env python3
"""
Script per testejar i comparar models LLM
Compara Mistral 7B vs Llama 3.2 amb mateixos inputs
"""

import requests
import json
import time
from typing import Dict, Any, Tuple
from datetime import datetime
import os

# Colors per terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text:^60}{Colors.ENDC}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_status(text: str):
    print(f"{Colors.BLUE}[INFO]{Colors.ENDC} {text}")

def print_success(text: str):
    print(f"{Colors.GREEN}[✓]{Colors.ENDC} {text}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}[!]{Colors.ENDC} {text}")

def print_error(text: str):
    print(f"{Colors.RED}[✗]{Colors.ENDC} {text}")

def check_backend() -> bool:
    """Verificar que el backend està corrent"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_available_models() -> list:
    """Obtenir models disponibles a Ollama"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
    except:
        pass
    return []

def test_discharge_summary(model_name: str) -> Tuple[Dict[str, Any], float]:
    """Testejar Discharge Summary"""
    payload = {
        "patient_context": "Home de 68 anys, masculí, antecedents de hipertensió",
        "admission_reason": "Dolor toràcic agut",
        "hospital_course": "Pacient ingressat per dolor toràcic. Realitzades proves cardíaques: ECG, troponina, ecocardiograma. Diagnòstic: Infart agut de miocardi de paret anterior.",
        "discharge_condition": "Estable, milloria clínica significativa",
        "medications": ["Aspirina 100mg", "Atorvastatina 40mg", "Ramipril 5mg"],
        "follow_up_instructions": "Control per cardiologia en 1 setmana, evitar esforços físics",
        "language": "ca"
    }
    
    start_time = time.time()
    response = requests.post(
        "http://localhost:8000/generate/discharge-summary",
        json=payload,
        timeout=120
    )
    elapsed_time = time.time() - start_time
    
    if response.status_code == 200:
        return response.json(), elapsed_time
    else:
        return {"error": response.text}, elapsed_time

def test_referral(model_name: str) -> Tuple[Dict[str, Any], float]:
    """Testejar Referral"""
    payload = {
        "patient_context": "Home de 68 anys, antecedents de hipertensió",
        "specialty": "Cardiologia",
        "reason": "Dolor toràcic persistent, sospita d'infart",
        "clinical_history": "Hipertensió arterial controlada, dislipidèmia, fumador",
        "current_medications": ["Ramipril 5mg", "Atorvastatina 40mg"],
        "language": "ca"
    }
    
    start_time = time.time()
    response = requests.post(
        "http://localhost:8000/generate/referral",
        json=payload,
        timeout=120
    )
    elapsed_time = time.time() - start_time
    
    if response.status_code == 200:
        return response.json(), elapsed_time
    else:
        return {"error": response.text}, elapsed_time

def test_clinical_summary(model_name: str) -> Tuple[Dict[str, Any], float]:
    """Testejar Clinical Summary"""
    payload = {
        "patient_context": "Home de 68 anys",
        "current_symptoms": ["Dolor toràcic", "Dispnea", "Sudoració"],
        "medications": ["Aspirina", "Atorvastatina", "Ramipril"],
        "specialty": "Cardiologia",
        "language": "ca"
    }
    
    start_time = time.time()
    response = requests.post(
        "http://localhost:8000/generate/clinical-summary",
        json=payload,
        timeout=120
    )
    elapsed_time = time.time() - start_time
    
    if response.status_code == 200:
        return response.json(), elapsed_time
    else:
        return {"error": response.text}, elapsed_time

def extract_summary(data: Dict[str, Any]) -> str:
    """Extreure el resum del resultat"""
    if "error" in data:
        return f"ERROR: {data['error']}"
    return data.get("summary", "No summary found")

def count_words(text: str) -> int:
    """Comptar paraules en un text"""
    return len(text.split())

def has_medical_codes(data: Dict[str, Any]) -> bool:
    """Verificar si el resultat té codis mèdics"""
    if "diagnoses" in data:
        for diag in data.get("diagnoses", []):
            if diag.get("snomed_code") or diag.get("icd10_code"):
                return True
    if "medications" in data:
        for med in data.get("medications", []):
            if med.get("atc_code"):
                return True
    return False

def main():
    print_header("Healthcare RAG System - Model Comparison")
    
    # Verificar backend
    print_status("Verificant backend API...")
    if not check_backend():
        print_error("Backend API no està corrent a http://localhost:8000")
        return
    print_success("Backend API està corrent")
    
    # Obtenir models disponibles
    print_status("Verificant models disponibles...")
    available_models = get_available_models()
    print(f"Models disponibles: {', '.join(available_models)}")
    
    if "mistral:latest" not in available_models or "llama3.2:latest" not in available_models:
        print_warning("No tots els models estan disponibles")
        print_warning("Assegureu-vos que teniu Mistral 7B i Llama 3.2 descarregats")
    
    print_success("Verificació completada\n")
    
    # Crear directori per resultats
    os.makedirs("/tmp/model_comparison", exist_ok=True)
    
    # Resultats
    results = {
        "mistral": {},
        "llama": {}
    }
    
    # ============================================
    # TEST 1: DISCHARGE SUMMARY
    # ============================================
    print_header("TEST 1: DISCHARGE SUMMARY")
    
    print_status("Testeig Mistral 7B...")
    mistral_data, mistral_time = test_discharge_summary("mistral:latest")
    results["mistral"]["discharge"] = {
        "data": mistral_data,
        "time": mistral_time,
        "words": count_words(extract_summary(mistral_data)),
        "has_codes": has_medical_codes(mistral_data)
    }
    print_success(f"Mistral 7B - {mistral_time:.2f}s ({results['mistral']['discharge']['words']} paraules)")
    
    print_status("Testeig Llama 3.2...")
    llama_data, llama_time = test_clinical_summary("llama3.2:latest")
    results["llama"]["discharge"] = {
        "data": llama_data,
        "time": llama_time,
        "words": count_words(extract_summary(llama_data)),
        "has_codes": has_medical_codes(llama_data)
    }
    print_success(f"Llama 3.2 - {llama_time:.2f}s ({results['llama']['discharge']['words']} paraules)")
    
    # ============================================
    # TEST 2: REFERRAL
    # ============================================
    print_header("TEST 2: REFERRAL")
    
    print_status("Testeig Mistral 7B...")
    mistral_data, mistral_time = test_referral("mistral:latest")
    results["mistral"]["referral"] = {
        "data": mistral_data,
        "time": mistral_time,
        "words": count_words(extract_summary(mistral_data)),
        "has_codes": has_medical_codes(mistral_data)
    }
    print_success(f"Mistral 7B - {mistral_time:.2f}s ({results['mistral']['referral']['words']} paraules)")
    
    print_status("Testeig Llama 3.2...")
    llama_data, llama_time = test_referral("llama3.2:latest")
    results["llama"]["referral"] = {
        "data": llama_data,
        "time": llama_time,
        "words": count_words(extract_summary(llama_data)),
        "has_codes": has_medical_codes(llama_data)
    }
    print_success(f"Llama 3.2 - {llama_time:.2f}s ({results['llama']['referral']['words']} paraules)")
    
    # ============================================
    # TEST 3: CLINICAL SUMMARY
    # ============================================
    print_header("TEST 3: CLINICAL SUMMARY")
    
    print_status("Testeig Mistral 7B...")
    mistral_data, mistral_time = test_clinical_summary("mistral:latest")
    results["mistral"]["clinical"] = {
        "data": mistral_data,
        "time": mistral_time,
        "words": count_words(extract_summary(mistral_data)),
        "has_codes": has_medical_codes(mistral_data)
    }
    print_success(f"Mistral 7B - {mistral_time:.2f}s ({results['mistral']['clinical']['words']} paraules)")
    
    print_status("Testeig Llama 3.2...")
    llama_data, llama_time = test_clinical_summary("llama3.2:latest")
    results["llama"]["clinical"] = {
        "data": llama_data,
        "time": llama_time,
        "words": count_words(extract_summary(llama_data)),
        "has_codes": has_medical_codes(llama_data)
    }
    print_success(f"Llama 3.2 - {llama_time:.2f}s ({results['llama']['clinical']['words']} paraules)")
    
    # ============================================
    # COMPARATIVA
    # ============================================
    print_header("COMPARATIVA RESULTATS")
    
    print(f"{Colors.BOLD}{'Test':<20} {'Mistral 7B':<20} {'Llama 3.2':<20} {'Guanyador':<15}{Colors.ENDC}")
    print("-" * 75)
    
    for test_name in ["discharge", "referral", "clinical"]:
        mistral_time = results["mistral"][test_name]["time"]
        llama_time = results["llama"][test_name]["time"]
        winner = "Mistral" if mistral_time < llama_time else "Llama"
        
        print(f"{test_name:<20} {mistral_time:>6.2f}s ({results['mistral'][test_name]['words']:>3}w) {llama_time:>6.2f}s ({results['llama'][test_name]['words']:>3}w) {winner:<15}")
    
    print("\n")
    
    # Guardar resultats
    with open("/tmp/model_comparison/results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print_success("Resultats guardats a /tmp/model_comparison/results.json")
    
    # Resum
    print_header("RESUM")
    
    mistral_avg_time = sum(results["mistral"][t]["time"] for t in ["discharge", "referral", "clinical"]) / 3
    llama_avg_time = sum(results["llama"][t]["time"] for t in ["discharge", "referral", "clinical"]) / 3
    
    print(f"Temps promig Mistral 7B: {mistral_avg_time:.2f}s")
    print(f"Temps promig Llama 3.2: {llama_avg_time:.2f}s")
    print(f"Diferència: {abs(mistral_avg_time - llama_avg_time):.2f}s ({abs(mistral_avg_time - llama_avg_time)/max(mistral_avg_time, llama_avg_time)*100:.1f}%)")
    
    print("\n")
    
    if mistral_avg_time < llama_avg_time:
        print_success(f"Mistral 7B és {llama_avg_time/mistral_avg_time:.1f}x més ràpid")
    else:
        print_success(f"Llama 3.2 és {mistral_avg_time/llama_avg_time:.1f}x més ràpid")

if __name__ == "__main__":
    main()
