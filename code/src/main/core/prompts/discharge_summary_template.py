"""
Discharge Summary Prompt Template
Template per generar informes d'alta hospitalària amb estructura validada
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class DischargeSummaryPrompt:
    """
    Prompt template per informe d'alta hospitalària
    
    Estructura basada en protocols SAS i estàndards clínics
    Suporta català i castellà
    """
    
    # Seccions obligatòries de l'informe
    REQUIRED_SECTIONS = [
        "datos_paciente",
        "motivo_ingreso",
        "diagnostico_principal",
        "tratamiento",
        "recomendaciones"
    ]
    
    @staticmethod
    def get_system_prompt(language: str = "es") -> str:
        """
        Obté el system prompt segons l'idioma
        
        Args:
            language: Idioma (es/ca)
            
        Returns:
            System prompt per configurar el comportament del LLM
        """
        if language == "ca":
            return """Ets un assistent mèdic especialitzat en la generació d'informes d'alta hospitalària.

INSTRUCCIONS CRÍTIQUES:
1. Genera informes clínics professionals seguint protocols oficials del SAS
2. Utilitza terminologia mèdica precisa i codis SNOMED CT / ICD-10 quan sigui possible
3. Estructura l'informe amb les seccions obligatòries
4. Sigues concís però complet - inclou tota la informació clínicament rellevant
5. Utilitza llenguatge tècnic però comprensible
6. **OBLIGATORI**: SEMPRE inclou codis mèdics en el format exacte especificat:
   - SNOMED CT: número de 6-18 dígits (ex: 57054005, 59621000)
   - ICD-10: lletra + 2 dígits + opcional .dígits (ex: I21.0, E11.10, J44.1)
   - ATC: lletra + 2 dígits + 2 lletres + 2 dígits (ex: C09AA02, B01AC06, A10BA02)
7. Basa't en els protocols i guies clíniques proporcionades
8. Assegura't que les recomanacions de seguiment siguin específiques i accionables

EXEMPLES DE CODIS CORRECTES:
- Infart agut de miocardi → SNOMED CT: 57054005, ICD-10: I21.0
- Hipertensió arterial → SNOMED CT: 59621000, ICD-10: I10
- Enalapril → ATC: C09AA02
- Metformina → ATC: A10BA02

IMPORTANT: La resposta ha de ser un informe mèdic formal, no una conversa. CADA diagnòstic i medicació HA DE tenir el seu codi corresponent."""
        
        else:  # es
            return """Eres un asistente médico especializado en la generación de informes de alta hospitalaria.

INSTRUCCIONES CRÍTICAS:
1. Genera informes clínicos profesionales siguiendo protocolos oficiales del SAS
2. Utiliza terminología médica precisa y códigos SNOMED CT / ICD-10 cuando sea posible
3. Estructura el informe con las secciones obligatorias
4. Sé conciso pero completo - incluye toda la información clínicamente relevante
5. Utiliza lenguaje técnico pero comprensible
6. **OBLIGATORIO**: SIEMPRE incluye códigos médicos en el formato exacto especificado:
   - SNOMED CT: número de 6-18 dígitos (ej: 57054005, 59621000)
   - ICD-10: letra + 2 dígitos + opcional .dígitos (ej: I21.0, E11.10, J44.1)
   - ATC: letra + 2 dígitos + 2 letras + 2 dígitos (ej: C09AA02, B01AC06, A10BA02)
7. Basa tu respuesta en los protocolos y guías clínicas proporcionadas
8. Asegúrate de que las recomendaciones de seguimiento sean específicas y accionables

EJEMPLOS DE CÓDIGOS CORRECTOS:
- Infarto agudo de miocardio → SNOMED CT: 57054005, ICD-10: I21.0
- Hipertensión arterial → SNOMED CT: 59621000, ICD-10: I10
- Enalapril → ATC: C09AA02
- Metformina → ATC: A10BA02

IMPORTANTE: La respuesta debe ser un informe médico formal, no una conversación. CADA diagnóstico y medicación DEBE tener su código correspondiente."""
    
    @staticmethod
    def get_template(language: str = "es") -> str:
        """
        Obté el template de l'informe segons l'idioma
        
        Args:
            language: Idioma (es/ca)
            
        Returns:
            Template estructurat per l'informe
        """
        if language == "ca":
            return """INFORME D'ALTA HOSPITALÀRIA

1. DADES DEL PACIENT
{patient_context}

2. MOTIU D'INGRÉS
{admission_reason}

3. DIAGNÒSTIC PRINCIPAL
[Descripció completa del diagnòstic principal]
- Codi SNOMED CT: [número de 6-18 dígits, exemple: 57054005]
- Codi ICD-10: [lletra + 2 dígits, exemple: I21.0]

4. DIAGNÒSTICS SECUNDARIS
- [Diagnòstic secundari 1]
  - Codi SNOMED CT: [número, exemple: 59621000]
  - Codi ICD-10: [codi, exemple: I10]
- [Diagnòstic secundari 2]
  - Codi SNOMED CT: [número, exemple: 370992007]
  - Codi ICD-10: [codi, exemple: E78.2]

5. PROCEDIMENTS REALITZATS
{procedures}

6. TRACTAMENT I MEDICACIÓ A L'ALTA
- [Nom medicament] [dosi]mg cada [freqüència] (Codi ATC: [exemple: C09AA02])
- [Nom medicament] [dosi]mg cada [freqüència] (Codi ATC: [exemple: B01AC06])
{medications}

7. EVOLUCIÓ CLÍNICA
[Resum detallat de l'evolució durant l'ingrés hospitalari]

8. RECOMANACIONS DE SEGUIMENT
- Control per [especialitat] en [temps]
- [Proves complementàries específiques]
- [Modificacions en el tractament]
- [Signes d'alarma a vigilar]

9. CONTRAINDICACIONS I PRECAUCIONS
- [Al·lèrgies medicamentoses]
- [Interaccions a evitar]
- [Precaucions específiques]

---
FONTS CONSULTADES:
{sources}"""
        
        else:  # es
            return """INFORME DE ALTA HOSPITALARIA

1. DATOS DEL PACIENTE
{patient_context}

2. MOTIVO DE INGRESO
{admission_reason}

3. DIAGNÓSTICO PRINCIPAL
[Descripción completa del diagnóstico principal]
- Código SNOMED CT: [número de 6-18 dígitos, ejemplo: 57054005]
- Código ICD-10: [letra + 2 dígitos, ejemplo: I21.0]

4. DIAGNÓSTICOS SECUNDARIOS
- [Diagnóstico secundario 1]
  - Código SNOMED CT: [número, ejemplo: 59621000]
  - Código ICD-10: [código, ejemplo: I10]
- [Diagnóstico secundario 2]
  - Código SNOMED CT: [número, ejemplo: 370992007]
  - Código ICD-10: [código, ejemplo: E78.2]

5. PROCEDIMIENTOS REALIZADOS
{procedures}

6. TRATAMIENTO Y MEDICACIÓN AL ALTA
- [Nombre medicamento] [dosis]mg cada [frecuencia] (Código ATC: [ejemplo: C09AA02])
- [Nombre medicamento] [dosis]mg cada [frecuencia] (Código ATC: [ejemplo: B01AC06])
{medications}

7. EVOLUCIÓN CLÍNICA
[Resumen detallado de la evolución durante el ingreso hospitalario]

8. RECOMENDACIONES DE SEGUIMIENTO
- Control por [especialidad] en [tiempo]
- [Pruebas complementarias específicas]
- [Modificaciones en el tratamiento]
- [Signos de alarma a vigilar]

9. CONTRAINDICACIONES Y PRECAUCIONES
- [Alergias medicamentosas]
- [Interacciones a evitar]
- [Precauciones específicas]

---
FUENTES CONSULTADAS:
{sources}"""
    
    @staticmethod
    def build_prompt(
        patient_context: str,
        admission_reason: str,
        procedures: List[str],
        medications: List[str],
        retrieved_protocols: List[Dict],
        language: str = "es"
    ) -> str:
        """
        Construeix el prompt complet per generar l'informe
        
        Args:
            patient_context: Context del pacient (edat, antecedents, etc.)
            admission_reason: Motiu d'ingrés
            procedures: Llista de procediments realitzats
            medications: Llista de medicacions actuals
            retrieved_protocols: Protocols i guies clíniques recuperades
            language: Idioma (es/ca)
            
        Returns:
            Prompt complet per enviar al LLM
        """
        # Format procedures
        procedures_text = "\n".join([f"- {proc}" for proc in procedures]) if procedures else "[No especificats]"
        
        # Format medications
        medications_text = "\n".join([f"- {med}" for med in medications]) if medications else "[No especificades]"
        
        # Format sources
        sources_text = ""
        if retrieved_protocols:
            sources_text = "\n".join([
                f"- {doc.get('source', 'Unknown')}: {doc.get('content', '')[:200]}..."
                for doc in retrieved_protocols[:5]  # Top 5 protocols
            ])
        else:
            sources_text = "[No s'han recuperat protocols específics]" if language == "ca" else "[No se han recuperado protocolos específicos]"
        
        # Get template
        template = DischargeSummaryPrompt.get_template(language)
        
        # Fill template
        filled_template = template.format(
            patient_context=patient_context,
            admission_reason=admission_reason,
            procedures=procedures_text,
            medications=medications_text,
            sources=sources_text
        )
        
        # Build context from protocols
        context_text = ""
        if retrieved_protocols:
            if language == "ca":
                context_text = "\n\nCONTEXT CLÍNIC (protocols i guies recuperades):\n"
            else:
                context_text = "\n\nCONTEXTO CLÍNICO (protocolos y guías recuperadas):\n"
            
            for i, doc in enumerate(retrieved_protocols[:3], 1):  # Top 3 for context
                context_text += f"\n{i}. {doc.get('content', '')[:500]}...\n"
        
        # Final prompt
        if language == "ca":
            final_prompt = f"""{context_text}

Genera un informe d'alta hospitalària professional seguint aquesta estructura:

{filled_template}

RECORDATORI CRÍTIC - FORMAT DE CODIS:
✓ CADA diagnòstic HA DE tenir:
  - Codi SNOMED CT: número de 6-18 dígits (exemple: 57054005)
  - Codi ICD-10: format lletra+dígits (exemple: I21.0)

✓ CADA medicació HA DE tenir:
  - Codi ATC: format exacte lletra+2dígits+2lletres+2dígits (exemple: C09AA02)

✓ Exemples de codis vàlids:
  - Infart agut de miocardi: SNOMED 57054005, ICD-10 I21.0
  - Hipertensió arterial: SNOMED 59621000, ICD-10 I10
  - Enalapril: ATC C09AA02
  - Metformina: ATC A10BA02

NO utilitzis placeholders com [codi] o [número]. Utilitza codis reals basant-te en els protocols."""
        else:
            final_prompt = f"""{context_text}

Genera un informe de alta hospitalaria profesional siguiendo esta estructura:

{filled_template}

RECORDATORIO CRÍTICO - FORMATO DE CÓDIGOS:
✓ CADA diagnóstico DEBE tener:
  - Código SNOMED CT: número de 6-18 dígitos (ejemplo: 57054005)
  - Código ICD-10: formato letra+dígitos (ejemplo: I21.0)

✓ CADA medicación DEBE tener:
  - Código ATC: formato exacto letra+2dígitos+2letras+2dígitos (ejemplo: C09AA02)

✓ Ejemplos de códigos válidos:
  - Infarto agudo de miocardio: SNOMED 57054005, ICD-10 I21.0
  - Hipertensión arterial: SNOMED 59621000, ICD-10 I10
  - Enalapril: ATC C09AA02
  - Metformina: ATC A10BA02

NO uses placeholders como [código] o [número]. Utiliza códigos reales basándote en los protocolos."""
        
        return final_prompt
    
    @staticmethod
    def validate_response(response: str, language: str = "es") -> Dict[str, bool]:
        """
        Valida que la resposta contingui les seccions obligatòries
        
        Args:
            response: Resposta generada pel LLM
            language: Idioma (es/ca)
            
        Returns:
            Dict amb validació de cada secció
        """
        validation = {}
        
        if language == "ca":
            sections = {
                "datos_paciente": ["DADES DEL PACIENT", "1."],
                "motivo_ingreso": ["MOTIU D'INGRÉS", "2."],
                "diagnostico_principal": ["DIAGNÒSTIC PRINCIPAL", "3.", "Codi:"],
                "diagnosticos_secundarios": ["DIAGNÒSTICS SECUNDARIS", "4."],
                "procedimientos": ["PROCEDIMENTS REALITZATS", "5."],
                "tratamiento": ["TRACTAMENT I MEDICACIÓ", "6."],
                "evolucion": ["EVOLUCIÓ CLÍNICA", "7."],
                "recomendaciones": ["RECOMANACIONS DE SEGUIMENT", "8."],
                "contraindicaciones": ["CONTRAINDICACIONS", "9."],
                "firma": ["FIRMA I DATA", "10."]
            }
        else:
            sections = {
                "datos_paciente": ["DATOS DEL PACIENTE", "1."],
                "motivo_ingreso": ["MOTIVO DE INGRESO", "2."],
                "diagnostico_principal": ["DIAGNÓSTICO PRINCIPAL", "3.", "Código:"],
                "diagnosticos_secundarios": ["DIAGNÓSTICOS SECUNDARIOS", "4."],
                "procedimientos": ["PROCEDIMIENTOS REALIZADOS", "5."],
                "tratamiento": ["TRATAMIENTO Y MEDICACIÓN", "6."],
                "evolucion": ["EVOLUCIÓN CLÍNICA", "7."],
                "recomendaciones": ["RECOMENDACIONES DE SEGUIMIENTO", "8."],
                "contraindicaciones": ["CONTRAINDICACIONES", "9."],
                "firma": ["FIRMA Y FECHA", "10."]
            }
        
        # Check each section
        for section_key, keywords in sections.items():
            validation[section_key] = any(keyword in response for keyword in keywords)
        
        return validation
    
    @staticmethod
    def extract_codes(response: str) -> Dict[str, List[str]]:
        """
        Extreu codis ontològics de la resposta
        
        Args:
            response: Resposta generada pel LLM
            
        Returns:
            Dict amb codis SNOMED, ICD-10 i ATC extrets
        """
        import re
        
        codes = {
            "snomed": [],
            "icd10": [],
            "atc": []
        }
        
        # SNOMED CT codes (numeric, 6-18 digits)
        snomed_pattern = r'\b\d{6,18}\b'
        codes["snomed"] = list(set(re.findall(snomed_pattern, response)))
        
        # ICD-10 codes (letter + 2 digits + optional decimal + digits)
        icd10_pattern = r'\b[A-Z]\d{2}(?:\.\d{1,2})?\b'
        codes["icd10"] = list(set(re.findall(icd10_pattern, response)))
        
        # ATC codes (letter + 2 digits + letter + letter + 2 digits)
        atc_pattern = r'\b[A-Z]\d{2}[A-Z]{2}\d{2}\b'
        codes["atc"] = list(set(re.findall(atc_pattern, response)))
        
        return codes
