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
        
        # Build complete prompt
        prompt = f"""
{lang['title']}
{'=' * 80}

{lang['instruction']}.
{specialty_context}

CONTEXT CLÍNIC RELLEVANT (Protocols i guies):
{context}

INFORMACIÓ DEL PACIENT:

{lang['sections']['antecedents']}:
{patient_context}

Condicions codificades:
{coded_conditions_text if coded_conditions_text else "No s'han identificat condicions codificades"}

{lang['sections']['symptoms']}:
{chr(10).join([f"- {symptom}" for symptom in current_symptoms])}

{lang['sections']['medications']}:
{medications_text}

INSTRUCCIONS:
1. Genera un resum clínic concís (màxim 500 paraules)
2. Estructura el resum amb les següents seccions:
   - {lang['sections']['antecedents']}
   - {lang['sections']['symptoms']}
   - {lang['sections']['medications']}
   - {lang['sections']['assessment']}
   - {lang['sections']['recommendations']}
3. Utilitza terminologia mèdica precisa
4. Inclou els codis SNOMED CT i ICD-10 quan estiguin disponibles
5. Basa't en els protocols clínics proporcionats al context
6. Sigues concís però complet
7. Prioritza la informació rellevant per a l'especialitat destí

RESUM CLÍNIC:
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
