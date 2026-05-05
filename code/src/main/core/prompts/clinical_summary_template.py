"""
Clinical Summary Prompt Template
Template per generar resums clínics previs a consulta
"""

from typing import List, Dict, Any, Optional


class ClinicalSummaryPrompt:
    """
    Prompt template per resums clínics amb arquitectura RAG semàntica
    """
    
    @staticmethod
    def build_prompt(
        patient_context: str,
        current_symptoms: List[str],
        medications: List[str],
        relevant_conditions: List[Dict[str, Any]],
        context: str,
        specialty: Optional[str] = None,
        language: str = "ca"
    ) -> str:
        """
        Build clinical summary prompt with semantic context
        
        Args:
            patient_context: Patient medical history
            current_symptoms: Current symptoms
            medications: Current medications
            relevant_conditions: Coded medical conditions
            context: Retrieved clinical protocols context
            specialty: Target specialty
            language: Output language (ca/es/en)
        
        Returns:
            Complete prompt for LLM
        """
        
        # Language-specific instructions
        instructions = {
            "ca": {
                "title": "RESUM CLÍNIC PREVI A CONSULTA",
                "instruction": "Genera un resum clínic concís i estructurat per a la consulta",
                "sections": {
                    "antecedents": "ANTECEDENTS RELLEVANTS",
                    "symptoms": "MOTIU DE CONSULTA",
                    "medications": "TRACTAMENT ACTUAL",
                    "assessment": "VALORACIÓ CLÍNICA",
                    "recommendations": "RECOMANACIONS"
                }
            },
            "es": {
                "title": "RESUMEN CLÍNICO PREVIO A CONSULTA",
                "instruction": "Genera un resumen clínico conciso y estructurado para la consulta",
                "sections": {
                    "antecedents": "ANTECEDENTES RELEVANTES",
                    "symptoms": "MOTIVO DE CONSULTA",
                    "medications": "TRATAMIENTO ACTUAL",
                    "assessment": "VALORACIÓN CLÍNICA",
                    "recommendations": "RECOMENDACIONES"
                }
            },
            "en": {
                "title": "CLINICAL SUMMARY FOR CONSULTATION",
                "instruction": "Generate a concise and structured clinical summary for consultation",
                "sections": {
                    "antecedents": "RELEVANT HISTORY",
                    "symptoms": "CHIEF COMPLAINT",
                    "medications": "CURRENT MEDICATIONS",
                    "assessment": "CLINICAL ASSESSMENT",
                    "recommendations": "RECOMMENDATIONS"
                }
            }
        }
        
        lang = instructions.get(language, instructions["ca"])
        
        # Build coded conditions section
        coded_conditions_text = ""
        if relevant_conditions:
            coded_conditions_text = "\n".join([
                f"- {cond['condition']}: SNOMED {cond.get('snomed_code', 'N/A')}, ICD-10 {cond.get('icd10_code', 'N/A')}"
                for cond in relevant_conditions
            ])
        
        # Build medications section
        medications_text = "\n".join([f"- {med}" for med in medications]) if medications else "Cap medicació actual"
        
        # Build specialty context
        specialty_context = f"\nEspecialitat destí: {specialty.upper()}\n" if specialty else ""
        
        # Build complete prompt with clear separation of instructions
        if language == "ca":
            prompt = f"""{lang['title']}

Pacient: {patient_context}
Símptomes: {', '.join(current_symptoms)}
Medicacions: {medications_text}
{specialty_context.strip()}

Genera un resum clínic professional amb aquestes seccions:

1. ANTECEDENTS RELLEVANTS
2. MOTIU DE CONSULTA
3. TRACTAMENT ACTUAL
4. VALORACIÓ CLÍNICA
5. RECOMANACIONS

Sigues concís, utilitza terminologia mèdica precisa i basa't en els protocols proporcionats.

⛔ INSTRUCCIÓ CRÍTICA SOBRE CODIS MÈDICS:
- ❌ NO escriguis SNOMED, ICD-10, ATC, o cap altre codi mèdic dins del text
- ❌ NO incloguis parèntesis amb codis com "(SNOMED: ...)" o "(ICD-10: ...)"
- ❌ NO generes cap codi - ni tan sols intents
- ✅ Els codis mèdics s'assignaran AUTOMÀTICAMENT pel sistema DESPRÉS de la teva generació
- ✅ Tu NOMÉS generes el text clínic en llenguatge natural, sense codis
"""
        else:  # es
            prompt = f"""{lang['title']}

Paciente: {patient_context}
Síntomas: {', '.join(current_symptoms)}
Medicaciones: {medications_text}
{specialty_context.strip()}

Genera un resumen clínico profesional con estas secciones:

1. ANTECEDENTES RELEVANTES
2. MOTIVO DE CONSULTA
3. TRATAMIENTO ACTUAL
4. VALORACIÓN CLÍNICA
5. RECOMENDACIONES

Sé conciso, utiliza terminología médica precisa y basa en los protocolos proporcionados.

⛔ INSTRUCCIÓN CRÍTICA SOBRE CÓDIGOS MÉDICOS:
- ❌ NO escribas SNOMED, ICD-10, ATC, o ningún otro código médico dentro del texto
- ❌ NO incluyas paréntesis con códigos como "(SNOMED: ...)" o "(ICD-10: ...)"
- ❌ NO generes ningún código - ni siquiera lo intentes
- ✅ Los códigos médicos se asignarán AUTOMÁTICAMENTE por el sistema DESPUÉS de tu generación
- ✅ TÚ SOLO generas el texto clínico en lenguaje natural, sin códigos
"""
        
        return prompt
    
    @staticmethod
    def build_simple_prompt(
        patient_context: str,
        current_symptoms: List[str],
        language: str = "ca"
    ) -> str:
        """
        Build simplified clinical summary prompt without coding
        
        Args:
            patient_context: Patient medical history
            current_symptoms: Current symptoms
            language: Output language
        
        Returns:
            Simplified prompt
        """
        
        instructions = {
            "ca": "Genera un resum clínic breu dels antecedents i símptomes actuals del pacient.",
            "es": "Genera un resumen clínico breve de los antecedentes y síntomas actuales del paciente.",
            "en": "Generate a brief clinical summary of the patient's history and current symptoms."
        }
        
        instruction = instructions.get(language, instructions["ca"])
        
        symptoms_text = "\n".join([f"- {symptom}" for symptom in current_symptoms])
        
        prompt = f"""
{instruction}

ANTECEDENTS:
{patient_context}

SÍMPTOMES ACTUALS:
{symptoms_text}

RESUM:
"""
        
        return prompt
