"""
Tests for Discharge Summary Prompt Template
"""

import pytest
from src.main.core.prompts.discharge_summary_template import DischargeSummaryPrompt


class TestDischargeSummaryPrompt:
    """Tests per DischargeSummaryPrompt"""
    
    def test_system_prompt_spanish(self):
        """Test system prompt en espanyol"""
        prompt = DischargeSummaryPrompt.get_system_prompt("es")
        
        assert "asistente médico" in prompt.lower()
        assert "informe" in prompt.lower()
        assert "alta hospitalaria" in prompt.lower()
        assert "SNOMED CT" in prompt
        assert "ICD-10" in prompt
    
    def test_system_prompt_catalan(self):
        """Test system prompt en català"""
        prompt = DischargeSummaryPrompt.get_system_prompt("ca")
        
        assert "assistent mèdic" in prompt.lower()
        assert "informe" in prompt.lower()
        assert "alta hospitalària" in prompt.lower()
        assert "SNOMED CT" in prompt
        assert "ICD-10" in prompt
    
    def test_template_spanish(self):
        """Test template en espanyol"""
        template = DischargeSummaryPrompt.get_template("es")
        
        # Check all required sections
        assert "DATOS DEL PACIENTE" in template
        assert "MOTIVO DE INGRESO" in template
        assert "DIAGNÓSTICO PRINCIPAL" in template
        assert "DIAGNÓSTICOS SECUNDARIOS" in template
        assert "PROCEDIMIENTOS REALIZADOS" in template
        assert "TRATAMIENTO Y MEDICACIÓN" in template
        assert "EVOLUCIÓN CLÍNICA" in template
        assert "RECOMENDACIONES DE SEGUIMIENTO" in template
        assert "CONTRAINDICACIONES" in template
        assert "FIRMA Y FECHA" in template
        
        # Check placeholders
        assert "{patient_context}" in template
        assert "{admission_reason}" in template
        assert "{procedures}" in template
        assert "{medications}" in template
        assert "{sources}" in template
    
    def test_template_catalan(self):
        """Test template en català"""
        template = DischargeSummaryPrompt.get_template("ca")
        
        # Check all required sections
        assert "DADES DEL PACIENT" in template
        assert "MOTIU D'INGRÉS" in template
        assert "DIAGNÒSTIC PRINCIPAL" in template
        assert "DIAGNÒSTICS SECUNDARIS" in template
        assert "PROCEDIMENTS REALITZATS" in template
        assert "TRACTAMENT I MEDICACIÓ" in template
        assert "EVOLUCIÓ CLÍNICA" in template
        assert "RECOMANACIONS DE SEGUIMENT" in template
        assert "CONTRAINDICACIONS" in template
        assert "FIRMA I DATA" in template
    
    def test_build_prompt_basic(self):
        """Test construcció de prompt bàsic"""
        prompt = DischargeSummaryPrompt.build_prompt(
            patient_context="Paciente de 65 años, diabético tipo 2",
            admission_reason="Dolor torácico agudo",
            procedures=["ECG", "Analítica completa"],
            medications=["Metformina 850mg", "AAS 100mg"],
            retrieved_protocols=[],
            language="es"
        )
        
        assert "Paciente de 65 años" in prompt
        assert "Dolor torácico agudo" in prompt
        assert "ECG" in prompt
        assert "Metformina" in prompt
        assert "INFORME DE ALTA" in prompt
    
    def test_build_prompt_with_protocols(self):
        """Test construcció de prompt amb protocols"""
        protocols = [
            {
                "source": "Protocolo SAS - Dolor Torácico",
                "content": "En caso de dolor torácico agudo, realizar ECG inmediato..."
            },
            {
                "source": "Guía Clínica - Diabetes",
                "content": "Control glucémico estricto en pacientes hospitalizados..."
            }
        ]
        
        prompt = DischargeSummaryPrompt.build_prompt(
            patient_context="Paciente de 65 años",
            admission_reason="Dolor torácico",
            procedures=["ECG"],
            medications=["Metformina"],
            retrieved_protocols=protocols,
            language="es"
        )
        
        assert "Protocolo SAS" in prompt
        assert "Guía Clínica" in prompt
        assert "CONTEXTO CLÍNICO" in prompt
    
    def test_build_prompt_catalan(self):
        """Test construcció de prompt en català"""
        prompt = DischargeSummaryPrompt.build_prompt(
            patient_context="Pacient de 65 anys, diabètic tipus 2",
            admission_reason="Dolor toràcic agut",
            procedures=["ECG", "Analítica completa"],
            medications=["Metformina 850mg"],
            retrieved_protocols=[],
            language="ca"
        )
        
        assert "Pacient de 65 anys" in prompt
        assert "Dolor toràcic agut" in prompt
        assert "INFORME D'ALTA" in prompt
        assert "CONTEXT CLÍNIC" in prompt or "protocols" in prompt.lower()
    
    def test_validate_response_complete(self):
        """Test validació de resposta completa"""
        response = """INFORME DE ALTA HOSPITALARIA

1. DATOS DEL PACIENTE
Paciente de 65 años

2. MOTIVO DE INGRESO
Dolor torácico agudo

3. DIAGNÓSTICO PRINCIPAL
Infarto agudo de miocardio
Código: I21.9

4. DIAGNÓSTICOS SECUNDARIOS
Diabetes mellitus tipo 2

5. PROCEDIMIENTOS REALIZADOS
- ECG
- Analítica

6. TRATAMIENTO Y MEDICACIÓN
- Metformina 850mg

7. EVOLUCIÓN CLÍNICA
Evolución favorable

8. RECOMENDACIONES DE SEGUIMIENTO
- Control en 1 semana

9. CONTRAINDICACIONES
Ninguna conocida

10. FIRMA Y FECHA
Fecha de alta: 21/04/2026"""
        
        validation = DischargeSummaryPrompt.validate_response(response, "es")
        
        # All sections should be present
        assert validation["datos_paciente"] is True
        assert validation["motivo_ingreso"] is True
        assert validation["diagnostico_principal"] is True
        assert validation["procedimientos"] is True
        assert validation["tratamiento"] is True
        assert validation["recomendaciones"] is True
    
    def test_validate_response_incomplete(self):
        """Test validació de resposta incompleta"""
        response = """INFORME DE ALTA HOSPITALARIA

1. DATOS DEL PACIENTE
Paciente de 65 años

2. MOTIVO DE INGRESO
Dolor torácico"""
        
        validation = DischargeSummaryPrompt.validate_response(response, "es")
        
        # Only first sections should be present
        assert validation["datos_paciente"] is True
        assert validation["motivo_ingreso"] is True
        assert validation["diagnostico_principal"] is False
        assert validation["tratamiento"] is False
    
    def test_extract_codes_snomed(self):
        """Test extracció de codis SNOMED CT"""
        response = """Diagnóstico principal: Infarto agudo de miocardio
Código SNOMED CT: 22298006"""
        
        codes = DischargeSummaryPrompt.extract_codes(response)
        
        assert "22298006" in codes["snomed"]
    
    def test_extract_codes_icd10(self):
        """Test extracció de codis ICD-10"""
        response = """Diagnóstico principal: Infarto agudo de miocardio
Código ICD-10: I21.9
Diagnóstico secundario: Diabetes mellitus tipo 2 (E11.9)"""
        
        codes = DischargeSummaryPrompt.extract_codes(response)
        
        assert "I21" in codes["icd10"] or "I21.9" in codes["icd10"]
        assert "E11" in codes["icd10"] or "E11.9" in codes["icd10"]
    
    def test_extract_codes_atc(self):
        """Test extracció de codis ATC"""
        response = """Medicación:
- Metformina (A10BA02)
- Ácido acetilsalicílico (B01AC06)"""
        
        codes = DischargeSummaryPrompt.extract_codes(response)
        
        assert "A10BA02" in codes["atc"]
        assert "B01AC06" in codes["atc"]
    
    def test_extract_codes_multiple(self):
        """Test extracció de múltiples codis"""
        response = """Diagnóstico principal: Infarto agudo de miocardio
Código SNOMED CT: 22298006
Código ICD-10: I21.9

Medicación:
- Metformina (A10BA02)
- AAS (B01AC06)"""
        
        codes = DischargeSummaryPrompt.extract_codes(response)
        
        assert len(codes["snomed"]) > 0
        assert len(codes["icd10"]) > 0
        assert len(codes["atc"]) > 0
    
    def test_required_sections_list(self):
        """Test que les seccions obligatòries estiguin definides"""
        required = DischargeSummaryPrompt.REQUIRED_SECTIONS
        
        assert "datos_paciente" in required
        assert "motivo_ingreso" in required
        assert "diagnostico_principal" in required
        assert "tratamiento_medicacion" in required
        assert "recomendaciones_seguimiento" in required
