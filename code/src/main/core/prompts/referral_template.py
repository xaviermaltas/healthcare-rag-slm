"""
Referral Document Prompt Template
Template per generar informes de derivació a especialista
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ReferralPrompt:
    """
    Prompt template per informe de derivació
    
    Estructura basada en protocols SAS de derivació
    Suporta català i castellà
    """
    
    # Especialitats suportades
    SPECIALTIES = [
        "Cardiologia",
        "Neurologia",
        "Endocrinologia",
        "Dermatologia",
        "Gastroenterologia",
        "Reumatologia",
        "Pneumologia",
        "Nefrologia",
        "Urologia",
        "Oftalmologia",
        "Otorrinolaringologia"
    ]
    
    # Nivells d'urgència
    URGENCY_LEVELS = ["normal", "preferent", "urgent"]
    
    @staticmethod
    def get_system_prompt(language: str = "ca") -> str:
        """
        Obté el system prompt segons l'idioma
        
        Args:
            language: Idioma (es/ca)
            
        Returns:
            System prompt per configurar el comportament del LLM
        """
        if language == "ca":
            return """Ets un assistent mèdic especialitzat en la generació d'informes de derivació a especialista.

INSTRUCCIONS CRÍTIQUES:
1. Genera informes de derivació professionals seguint protocols oficials del SAS
2. Utilitza terminologia mèdica precisa i noms estàndard de malalties
3. Estructura l'informe amb les seccions obligatòries
4. Sigues concís però complet - inclou només informació rellevant per l'especialista
5. Assegura't que el motiu de derivació sigui clar i específic
6. Inclou només antecedents i proves rellevants per la consulta
8. **ESPECIALITAT DESTÍ**: Ha de ser coherent amb el motiu de derivació

⛔ INSTRUCCIÓ CRÍTICA SOBRE CODIS MÈDICS:
7. **ZERO CODIS MÈDICS EN EL TEXT**: 
   - ❌ NO escriguis SNOMED, ICD-10, ATC, o cap altre codi mèdic dins del text
   - ❌ NO incloguis parèntesis amb codis com "(SNOMED: ...)" o "(ICD-10: ...)"
   - ❌ NO generes cap codi - ni tan sols intents
   - ✅ Els codis mèdics s'assignaran AUTOMÀTICAMENT pel sistema DESPRÉS de la teva generació
   - ✅ Tu NOMÉS generes el text clínic en llenguatge natural, sense codis

EXEMPLE D'INFORME BEN ESTRUCTURAT:

ESPECIALITAT DESTÍ: Cardiologia
URGÈNCIA: Preferent

MOTIU DE DERIVACIÓ:
Dolor toràcic atípic de 2 mesos d'evolució, no relacionat amb l'esforç. ECG basal normal però perfil lipídic alterat.

ANTECEDENTS RELLEVANTS:
- Hipertensió arterial en tractament amb IECA
- Diabetis mellitus tipus 2 amb bon control metabòlic
- Tabaquisme actiu (20 cigarrets/dia)

EXPLORACIONS I PROVES REALITZADES:
- ECG basal: ritme sinusal, sense alteracions
- Analítica: glucosa 110 mg/dL, HbA1c 6.5%, colesterol total 280 mg/dL, LDL 180 mg/dL

TRACTAMENT ACTUAL:
- Enalapril 10mg cada 12 hores
- Metformina 850mg cada 12 hores
- Atorvastatina 20mg cada 24 hores

IMPORTANT: Utilitza noms estàndard de malalties i medicaments. NO incloguis codis mèdics."""
        
        else:  # es
            return """Eres un asistente médico especializado en la generación de informes de derivación a especialista.

INSTRUCCIONES CRÍTICAS:
1. Genera informes de derivación profesionales siguiendo protocolos oficiales del SAS
2. Utiliza terminología médica precisa y nombres estándar de enfermedades
3. Estructura el informe con las secciones obligatorias
4. Sé conciso pero completo - incluye solo información relevante para el especialista
5. Asegúrate de que el motivo de derivación sea claro y específico
6. Incluye solo antecedentes y pruebas relevantes para la consulta
8. **ESPECIALIDAD DESTINO**: Debe ser coherente con el motivo de derivación

⛔ INSTRUCCIÓN CRÍTICA SOBRE CÓDIGOS MÉDICOS:
7. **CERO CÓDIGOS MÉDICOS EN EL TEXTO**: 
   - ❌ NO escribas SNOMED, ICD-10, ATC, o ningún otro código médico dentro del texto
   - ❌ NO incluyas paréntesis con códigos como "(SNOMED: ...)" o "(ICD-10: ...)"
   - ❌ NO generes ningún código - ni siquiera lo intentes
   - ✅ Los códigos médicos se asignarán AUTOMÁTICAMENTE por el sistema DESPUÉS de tu generación
   - ✅ TÚ SOLO generas el texto clínico en lenguaje natural, sin códigos

EJEMPLO DE INFORME BIEN ESTRUCTURADO:

ESPECIALIDAD DESTINO: Cardiología
URGENCIA: Preferente

MOTIVO DE DERIVACIÓN:
Dolor torácico atípico de 2 meses de evolución, no relacionado con el esfuerzo. ECG basal normal pero perfil lipídico alterado.

ANTECEDENTES RELEVANTES:
- Hipertensión arterial en tratamiento con IECA
- Diabetes mellitus tipo 2 con buen control metabólico
- Tabaquismo activo (20 cigarrillos/día)

EXPLORACIONES Y PRUEBAS REALIZADAS:
- ECG basal: ritmo sinusal, sin alteraciones
- Analítica: glucosa 110 mg/dL, HbA1c 6.5%, colesterol total 280 mg/dL, LDL 180 mg/dL

TRATAMIENTO ACTUAL:
- Enalapril 10mg cada 12 horas
- Metformina 850mg cada 12 horas
- Atorvastatina 20mg cada 24 horas

IMPORTANTE: Utiliza nombres estándar de enfermedades y medicamentos. NO incluyas códigos médicos."""
    
    @staticmethod
    def get_template(language: str = "ca") -> str:
        """
        Obté el template de l'informe segons l'idioma
        
        Args:
            language: Idioma (es/ca)
            
        Returns:
            Template estructurat per l'informe
        """
        if language == "ca":
            return """INFORME DE DERIVACIÓ A ESPECIALISTA

1. DADES DEL PACIENT
{patient_context}

2. ESPECIALITAT DESTÍ
{target_specialty}

3. URGÈNCIA
{urgency}

4. MOTIU DE DERIVACIÓ
{referral_reason}

5. ANTECEDENTS RELLEVANTS
{relevant_history}

6. EXPLORACIONS I PROVES REALITZADES
{examinations}

7. TRACTAMENT ACTUAL
{current_medications}

8. INFORMACIÓ ADDICIONAL
{additional_info}

---
PROTOCOLS CONSULTATS:
{sources}"""
        
        else:  # es
            return """INFORME DE DERIVACIÓN A ESPECIALISTA

1. DATOS DEL PACIENTE
{patient_context}

2. ESPECIALIDAD DESTINO
{target_specialty}

3. URGENCIA
{urgency}

4. MOTIVO DE DERIVACIÓN
{referral_reason}

5. ANTECEDENTES RELEVANTES
{relevant_history}

6. EXPLORACIONES Y PRUEBAS REALIZADAS
{examinations}

7. TRATAMIENTO ACTUAL
{current_medications}

8. INFORMACIÓN ADICIONAL
{additional_info}

---
PROTOCOLOS CONSULTADOS:
{sources}"""
    
    @staticmethod
    def build_prompt(
        patient_context: str,
        referral_reason: str,
        relevant_history: List[str],
        examinations: List[str],
        current_medications: List[str],
        target_specialty: Optional[str] = None,
        urgency: str = "normal",
        additional_info: Optional[str] = None,
        retrieved_protocols: List[Dict] = None,
        language: str = "ca"
    ) -> str:
        """
        Construeix el prompt complet per generar l'informe de derivació
        
        Args:
            patient_context: Context del pacient (edat, sexe, etc.)
            referral_reason: Motiu de la derivació
            relevant_history: Llista d'antecedents rellevants
            examinations: Llista d'exploracions i proves realitzades
            current_medications: Llista de medicacions actuals
            target_specialty: Especialitat destí (opcional, pot detectar-se)
            urgency: Nivell d'urgència (normal/preferent/urgent)
            additional_info: Informació addicional opcional
            retrieved_protocols: Protocols de derivació recuperats
            language: Idioma (es/ca)
            
        Returns:
            Prompt complet per enviar al LLM
        """
        # Format history
        history_text = "\n".join([f"- {item}" for item in relevant_history]) if relevant_history else "[Sense antecedents rellevants]"
        
        # Format examinations
        examinations_text = "\n".join([f"- {exam}" for exam in examinations]) if examinations else "[No s'han realitzat proves]"
        
        # Format medications
        medications_text = "\n".join([f"- {med}" for med in current_medications]) if current_medications else "[Sense medicació habitual]"
        
        # Format specialty
        specialty_text = target_specialty if target_specialty else "[A determinar segons el motiu]"
        
        # Format urgency
        urgency_map_ca = {"normal": "Normal", "preferent": "Preferent", "urgent": "Urgent"}
        urgency_map_es = {"normal": "Normal", "preferent": "Preferente", "urgent": "Urgente"}
        urgency_text = urgency_map_ca.get(urgency, "Normal") if language == "ca" else urgency_map_es.get(urgency, "Normal")
        
        # Format additional info
        additional_text = additional_info if additional_info else ("[Sense informació addicional]" if language == "ca" else "[Sin información adicional]")
        
        # Format sources
        sources_text = ""
        if retrieved_protocols:
            sources_text = "\n".join([
                f"- {doc.get('source', 'Unknown')}: {doc.get('content', '')[:200]}..."
                for doc in retrieved_protocols[:3]
            ])
        else:
            sources_text = "[No s'han recuperat protocols específics]" if language == "ca" else "[No se han recuperado protocolos específicos]"
        
        # Get template
        template = ReferralPrompt.get_template(language)
        
        # Fill template
        filled_template = template.format(
            patient_context=patient_context,
            target_specialty=specialty_text,
            urgency=urgency_text,
            referral_reason=referral_reason,
            relevant_history=history_text,
            examinations=examinations_text,
            current_medications=medications_text,
            additional_info=additional_text,
            sources=sources_text
        )
        
        # Build context from protocols
        context_text = ""
        if retrieved_protocols:
            if language == "ca":
                context_text = "\n\nCONTEXT CLÍNIC (protocols de derivació recuperats):\n"
            else:
                context_text = "\n\nCONTEXTO CLÍNICO (protocolos de derivación recuperados):\n"
            
            for i, doc in enumerate(retrieved_protocols[:3], 1):
                context_text += f"\n{i}. {doc.get('content', '')[:500]}...\n"
        
        # Final prompt
        if language == "ca":
            final_prompt = f"""{context_text}

Genera un informe de derivació a especialista professional seguint aquesta estructura:

{filled_template}

RECORDATORI CRÍTIC:
✓ Motiu de derivació clar i específic
✓ Només antecedents i proves rellevants per l'especialista
✓ Especialitat coherent amb el motiu
✓ NO incloguis codis mèdics - s'assignaran automàticament"""
        else:
            final_prompt = f"""{context_text}

Genera un informe de derivación a especialista profesional siguiendo esta estructura:

{filled_template}

RECORDATORIO CRÍTICO:
✓ Motivo de derivación claro y específico
✓ Solo antecedentes y pruebas relevantes para el especialista
✓ Especialidad coherente con el motivo
✓ NO incluyas códigos médicos - se asignarán automáticamente"""
        
        return final_prompt
