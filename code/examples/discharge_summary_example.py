"""
Example: Discharge Summary Prompt Template Usage
Exemple d'ús del template per informes d'alta
"""

from src.main.core.prompts.discharge_summary_template import DischargeSummaryPrompt


def example_basic_spanish():
    """Exemple bàsic en espanyol"""
    print("=" * 80)
    print("EXEMPLE 1: Informe d'Alta Bàsic (Espanyol)")
    print("=" * 80)
    
    # Build prompt
    prompt = DischargeSummaryPrompt.build_prompt(
        patient_context="Paciente de 65 años, sexo masculino, diabético tipo 2 en tratamiento con metformina",
        admission_reason="Dolor torácico agudo de 2 horas de evolución",
        procedures=[
            "ECG de 12 derivaciones",
            "Analítica completa con troponinas",
            "Ecocardiograma transtorácico"
        ],
        medications=[
            "Metformina 850mg cada 12 horas",
            "Ácido acetilsalicílico 100mg cada 24 horas",
            "Atorvastatina 40mg cada 24 horas"
        ],
        retrieved_protocols=[],
        language="es"
    )
    
    print("\n📝 PROMPT GENERAT:\n")
    print(prompt[:1000] + "...\n")
    
    # Simulate response
    simulated_response = """INFORME DE ALTA HOSPITALARIA

1. DATOS DEL PACIENTE
Paciente de 65 años, sexo masculino, diabético tipo 2 en tratamiento con metformina

2. MOTIVO DE INGRESO
Dolor torácico agudo de 2 horas de evolución

3. DIAGNÓSTICO PRINCIPAL
Infarto agudo de miocardio con elevación del segmento ST (IAMCEST)
Código SNOMED CT: 401303003
Código ICD-10: I21.9

4. DIAGNÓSTICOS SECUNDARIOS
- Diabetes mellitus tipo 2 (E11.9)
- Dislipidemia (E78.5)

5. PROCEDIMIENTOS REALIZADOS
- ECG de 12 derivaciones
- Analítica completa con troponinas
- Ecocardiograma transtorácico

6. TRATAMIENTO Y MEDICACIÓN
- Metformina 850mg cada 12 horas (A10BA02)
- Ácido acetilsalicílico 100mg cada 24 horas (B01AC06)
- Atorvastatina 40mg cada 24 horas (C10AA05)
- Clopidogrel 75mg cada 24 horas (B01AC04)

7. EVOLUCIÓN CLÍNICA
Paciente ingresado por dolor torácico agudo compatible con síndrome coronario agudo. 
ECG mostró elevación del segmento ST en derivaciones anteriores. Troponinas elevadas.
Evolución favorable tras tratamiento médico inicial.

8. RECOMENDACIONES DE SEGUIMIENTO
- Control en consulta de cardiología en 1 semana
- Ecocardiograma de control en 1 mes
- Control analítico con perfil lipídico en 2 semanas
- Signos de alarma: dolor torácico, disnea, palpitaciones

9. CONTRAINDICACIONES
- Alergia conocida a penicilina
- Evitar AINE por riesgo de sangrado con doble antiagregación

10. FIRMA Y FECHA
Fecha de alta: 21/04/2026
Médico responsable: Dr. García López
Especialidad: Cardiología"""
    
    print("\n📋 RESPOSTA SIMULADA:\n")
    print(simulated_response)
    
    # Validate response
    validation = DischargeSummaryPrompt.validate_response(simulated_response, "es")
    print("\n✅ VALIDACIÓ DE SECCIONS:")
    for section, is_present in validation.items():
        status = "✓" if is_present else "✗"
        print(f"  {status} {section}: {'Present' if is_present else 'Absent'}")
    
    # Extract codes
    codes = DischargeSummaryPrompt.extract_codes(simulated_response)
    print("\n🏷️  CODIS EXTRETS:")
    print(f"  SNOMED CT: {codes['snomed']}")
    print(f"  ICD-10: {codes['icd10']}")
    print(f"  ATC: {codes['atc']}")


def example_with_protocols_catalan():
    """Exemple amb protocols en català"""
    print("\n\n" + "=" * 80)
    print("EXEMPLE 2: Informe d'Alta amb Protocols (Català)")
    print("=" * 80)
    
    # Simulated retrieved protocols
    protocols = [
        {
            "source": "Protocol SAS - Síndrome Coronària Aguda",
            "content": """En cas de síndrome coronària aguda amb elevació del segment ST, 
            es recomana antiagregació doble amb AAS i clopidogrel durant almenys 12 mesos. 
            Control estricte de factors de risc cardiovascular."""
        },
        {
            "source": "Guia Clínica - Diabetis i Malaltia Cardiovascular",
            "content": """Els pacients diabètics amb infart agut de miocardi requereixen 
            control glucèmic estricte. Objectiu HbA1c <7%. Considerar intensificació del 
            tractament hipoglucemiant si cal."""
        }
    ]
    
    # Build prompt
    prompt = DischargeSummaryPrompt.build_prompt(
        patient_context="Pacient de 65 anys, sexe masculí, diabètic tipus 2",
        admission_reason="Dolor toràcic agut",
        procedures=["ECG", "Analítica amb troponines"],
        medications=["Metformina 850mg", "AAS 100mg"],
        retrieved_protocols=protocols,
        language="ca"
    )
    
    print("\n📝 PROMPT GENERAT (amb protocols):\n")
    print(prompt[:1200] + "...\n")
    
    print("\n📚 PROTOCOLS RECUPERATS:")
    for i, protocol in enumerate(protocols, 1):
        print(f"\n  {i}. {protocol['source']}")
        print(f"     {protocol['content'][:150]}...")


def example_validation():
    """Exemple de validació de resposta"""
    print("\n\n" + "=" * 80)
    print("EXEMPLE 3: Validació de Respostes")
    print("=" * 80)
    
    # Complete response
    complete_response = """INFORME DE ALTA HOSPITALARIA
1. DATOS DEL PACIENTE
2. MOTIVO DE INGRESO
3. DIAGNÓSTICO PRINCIPAL
Código: I21.9
4. DIAGNÓSTICOS SECUNDARIOS
5. PROCEDIMIENTOS REALIZADOS
6. TRATAMIENTO Y MEDICACIÓN
7. EVOLUCIÓN CLÍNICA
8. RECOMENDACIONES DE SEGUIMIENTO
9. CONTRAINDICACIONES
10. FIRMA Y FECHA"""
    
    # Incomplete response
    incomplete_response = """INFORME DE ALTA HOSPITALARIA
1. DATOS DEL PACIENTE
2. MOTIVO DE INGRESO"""
    
    print("\n✅ Resposta COMPLETA:")
    validation_complete = DischargeSummaryPrompt.validate_response(complete_response, "es")
    complete_count = sum(validation_complete.values())
    print(f"   Seccions presents: {complete_count}/{len(validation_complete)}")
    
    print("\n❌ Resposta INCOMPLETA:")
    validation_incomplete = DischargeSummaryPrompt.validate_response(incomplete_response, "es")
    incomplete_count = sum(validation_incomplete.values())
    print(f"   Seccions presents: {incomplete_count}/{len(validation_incomplete)}")


if __name__ == "__main__":
    # Run examples
    example_basic_spanish()
    example_with_protocols_catalan()
    example_validation()
    
    print("\n\n" + "=" * 80)
    print("✅ EXEMPLES COMPLETATS")
    print("=" * 80)
