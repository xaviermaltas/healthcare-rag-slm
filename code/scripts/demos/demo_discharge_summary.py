#!/usr/bin/env python3
"""
Demo del cas d'ús: Generació d'Informe d'Alta Hospitalària
Simula un cas clínic real amb interacció visual
"""

import requests
import json
from datetime import datetime
import time

API_URL = "http://localhost:8000"
ENDPOINT = f"{API_URL}/generate/discharge-summary"

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80 + "\n")

def print_section(title, content):
    """Print formatted section"""
    print(f"\n{'─'*80}")
    print(f"📋 {title}")
    print(f"{'─'*80}")
    print(content)

# Cas clínic real: Infart Agut de Miocardi
caso_clinico = {
    "patient_context": """Pacient home de 65 anys amb antecedents de:
    - Hipertensió arterial en tractament amb Enalapril
    - Dislipèmia en tractament amb Atorvastatina
    - Ex-fumador (va deixar de fumar fa 10 anys)
    - Vida activa, camina diàriament
    - Sense al·lèrgies medicamentoses conegudes""",
    
    "admission_reason": """Ingrés urgent per dolor toràcic opressiu d'inici sobtat mentre feia exercici.
    Característiques del dolor:
    - Intensitat 8/10
    - Irradiació a braç esquerre i mandíbula
    - Acompanyat de diaforesi profusa i dispnea
    - Durada: 45 minuts abans d'arribar a urgències
    
    Troponines elevades (cTnI: 15 ng/mL - valor normal <0.04)
    ECG: Elevació del segment ST en derivacions inferiors (II, III, aVF)""",
    
    "procedures": [
        "ECG de 12 derivacions (elevació ST en derivacions inferiors)",
        "Analítica completa amb troponines seriades cada 6h",
        "Ecocardiograma transtorácic (FEVI 45%, hipocinèsia de paret inferior)",
        "Coronariografia urgent: oclusió total de artèria coronària dreta",
        "Angioplastia primària amb implantació de stent farmacoactiu en CD",
        "Monitorització contínua en UCI durant 48h"
    ],
    
    "current_medications": [
        "AAS 100mg/24h (antiagregant)",
        "Clopidogrel 75mg/24h durant 12 mesos (antiagregant)",
        "Atorvastatina 80mg/24h (estatina d'alta intensitat)",
        "Ramipril 5mg/24h (IECA per cardioprotecció)",
        "Bisoprolol 5mg/24h (betabloqueant)"
    ],
    
    "language": "ca",
    "specialty": "Cardiologia"
}

print_header("🏥 DEMO: GENERACIÓ AUTOMÀTICA D'INFORME D'ALTA HOSPITALÀRIA")

print("📝 CAS CLÍNIC:")
print(f"   Pacient: Home, 65 anys")
print(f"   Diagnòstic: Infart Agut de Miocardi (IAMCEST)")
print(f"   Especialitat: Cardiologia")
print(f"   Idioma: Català")

print_section("CONTEXT DEL PACIENT", caso_clinico["patient_context"])
print_section("MOTIU D'INGRÉS", caso_clinico["admission_reason"])

print(f"\n📊 PROCEDIMENTS REALITZATS ({len(caso_clinico['procedures'])}):")
for i, proc in enumerate(caso_clinico["procedures"], 1):
    print(f"   {i}. {proc}")

print(f"\n💊 MEDICACIÓ ACTUAL ({len(caso_clinico['current_medications'])}):")
for i, med in enumerate(caso_clinico["current_medications"], 1):
    print(f"   {i}. {med}")

print("\n" + "─"*80)
input("\n⏸️  Prem ENTER per generar l'informe d'alta automàticament...")

print("\n🔄 Enviant petició a l'API...")
print(f"   Endpoint: {ENDPOINT}")

start_time = time.time()

try:
    response = requests.post(
        ENDPOINT,
        json=caso_clinico,
        headers={"Content-Type": "application/json"},
        timeout=120
    )
    
    end_time = time.time()
    duration = end_time - start_time
    
    if response.status_code == 200:
        result = response.json()
        
        print_header("✅ INFORME D'ALTA GENERAT AUTOMÀTICAMENT")
        
        print(f"⏱️  Temps de generació: {duration:.2f} segons")
        print(f"🤖 Model utilitzat: {result['generation_metadata']['model']}")
        print(f"📚 Protocols consultats: {result['generation_metadata']['protocols_retrieved']}")
        
        print_section("INFORME COMPLET", result['summary'])
        
        if result.get('sources'):
            print(f"\n📖 PROTOCOLS SAS UTILITZATS:")
            for i, source in enumerate(result['sources'], 1):
                print(f"\n   {i}. {source['title']}")
                print(f"      Especialitat: {source['specialty']}")
                print(f"      Rellevància: {source['score']:.2%}")
                print(f"      Protocol oficial: {'Sí' if source['official'] else 'No'}")
        
        print(f"\n✔️  VALIDACIÓ:")
        validation = result['validation_status']
        print(f"   - Totes les seccions presents: {'✅' if validation['all_sections_present'] else '❌'}")
        print(f"   - Conté diagnòstics: {'✅' if validation['has_diagnoses'] else '❌'}")
        print(f"   - Conté medicacions: {'✅' if validation['has_medications'] else '❌'}")
        print(f"   - Conté seguiment: {'✅' if validation['has_follow_up'] else '❌'}")
        
        print_header("🎯 BENEFICIS DEL SISTEMA")
        print("✅ Generació automàtica en ~50 segons (vs 10-15 minuts manual)")
        print("✅ Consulta de protocols oficials del SAS")
        print("✅ Estructura estandarditzada i completa")
        print("✅ Suport multiidioma (català/castellà)")
        print("✅ Codificació amb SNOMED CT i ICD-10")
        print("✅ Traçabilitat de fonts utilitzades")
        
        print("\n💡 IMPACTE ESTIMAT:")
        print(f"   - Estalvi de temps: ~10 minuts per informe")
        print(f"   - Reducció d'errors: Estructura validada automàticament")
        print(f"   - Millora qualitat: Basada en protocols oficials")
        
    else:
        print(f"\n❌ ERROR {response.status_code}:")
        print(response.text)

except requests.exceptions.Timeout:
    print("\n❌ Timeout: La generació ha trigat més de 120 segons")
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "="*80)
