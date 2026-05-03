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
2. Utilitza terminologia mèdica precisa i noms estàndard de malalties i medicaments
3. Estructura l'informe amb les seccions obligatòries
4. Sigues concís però complet - inclou tota la informació clínicament rellevant
5. Utilitza llenguatge tècnic però comprensible
6. Basa't en els protocols i guies clíniques proporcionades
7. Assegura't que les recomanacions de seguiment siguin específiques i accionables

🚨 REGLES ANTI-AL·LUCINACIÓ (CRÍTIQUES):
8. **USA NOMÉS DADES PROPORCIONADES**: NO inventis diagnòstics, símptomes o dades que no estiguin explícitament en el motiu d'ingrés o context del pacient
9. **DIAGNÒSTIC PRINCIPAL**: Extreu-lo DIRECTAMENT del motiu d'ingrés. Si el motiu diu "infart agut de miocardi", el diagnòstic principal HA DE SER "infart agut de miocardi", NO "insuficiència cardíaca" ni cap altra condició
10. **DIAGNÒSTICS SECUNDARIS**: Només dels antecedents del pacient (context), MAI del motiu d'ingrés
11. **MEDICACIONS**: Usa EXACTAMENT els noms proporcionats, NO canviïs noms comercials per genèrics ni viceversa
12. **NO generis codis mèdics** (SNOMED, ICD-10, ATC) - aquests s'assignaran automàticament després.

📚 EXEMPLES D'EXTRACCIÓ CORRECTA DE DIAGNÒSTIC:

EXEMPLE 1 - Cardiologia:
Motiu d'ingrés: "Dolor toràcic opressiu... ECG amb elevació del segment ST en derivacions anteriors, elevació de troponines"
→ Diagnòstic principal: Infart agut de miocardi amb elevació del segment ST (IAMEST)
✅ CORRECTE: Usa la terminologia mèdica estàndard basada en els símptomes + proves
❌ INCORRECTE: "Insuficiència cardíaca" (això és una complicació, no el diagnòstic d'ingrés)

EXEMPLE 2 - Pneumologia:
Motiu d'ingrés: "Febre, tos productiva, dispnea... Radiografia de tòrax amb infiltrat alveolar"
→ Diagnòstic principal: Pneumònia adquirida a la comunitat
✅ CORRECTE: Diagnòstic específic basat en clínica + imatge
❌ INCORRECTE: "Infecció respiratòria aguda" (massa genèric)

EXEMPLE 3 - Neurologia:
Motiu d'ingrés: "Hemiparèsia dreta d'inici sobtat... TC cranial amb hipodensitat en territori ACM esquerra"
→ Diagnòstic principal: Accident cerebrovascular isquèmic (ACVI)
✅ CORRECTE: Diagnòstic precís segons clínica + imatge
❌ INCORRECTE: "Ictus" (terme col·loquial, usa terminologia mèdica estàndard)

ESTRUCTURA CORRECTA:

3. DIAGNÒSTIC PRINCIPAL
[Diagnòstic específic derivat del motiu d'ingrés amb terminologia mèdica estàndard]

4. DIAGNÒSTICS SECUNDARIS
- [Antecedent 1 del context del pacient]
- [Antecedent 2 del context del pacient]
- [Antecedent 3 del context del pacient]

6. TRACTAMENT I MEDICACIÓ A L'ALTA
- Àcid acetilsalicílic 100mg cada 24 hores
- Clopidogrel 75mg cada 24 hores
- Atorvastatina 80mg cada 24 hores
- Enalapril 10mg cada 12 hores
- Bisoprolol 5mg cada 24 hores

IMPORTANT: Utilitza noms estàndard de malalties i medicaments. NO incloguis codis mèdics."""
        
        else:  # es
            return """Eres un asistente médico especializado en la generación de informes de alta hospitalaria.

INSTRUCCIONES CRÍTICAS:
1. Genera informes clínicos profesionales siguiendo protocolos oficiales del SAS
2. Utiliza terminología médica precisa y nombres estándar de enfermedades y medicamentos
3. Estructura el informe con las secciones obligatorias
4. Sé conciso pero completo - incluye toda la información clínicamente relevante
5. Utiliza lenguaje técnico pero comprensible
6. Basa tu respuesta en los protocolos y guías clínicas proporcionadas
7. Asegúrate de que las recomendaciones de seguimiento sean específicas y accionables

🚨 REGLAS ANTI-ALUCINACIÓN (CRÍTICAS):
8. **USA SOLO DATOS PROPORCIONADOS**: NO inventes diagnósticos, síntomas o datos que no estén explícitamente en el motivo de ingreso o contexto del paciente
9. **DIAGNÓSTICO PRINCIPAL**: Extráelo DIRECTAMENTE del motivo de ingreso. Si el motivo dice "infarto agudo de miocardio", el diagnóstico principal DEBE SER "infarto agudo de miocardio", NO "insuficiencia cardíaca" ni ninguna otra condición
10. **DIAGNÓSTICOS SECUNDARIOS**: Solo de los antecedentes del paciente (contexto), NUNCA del motivo de ingreso
11. **MEDICACIONES**: Usa EXACTAMENTE los nombres proporcionados, NO cambies nombres comerciales por genéricos ni viceversa
12. **NO generes códigos médicos** (SNOMED, ICD-10, ATC) - estos se asignarán automáticamente después.

📚 EJEMPLOS DE EXTRACCIÓN CORRECTA DE DIAGNÓSTICO:

EJEMPLO 1 - Cardiología:
Motivo de ingreso: "Dolor torácico opresivo... ECG con elevación del segmento ST en derivaciones anteriores, elevación de troponinas"
→ Diagnóstico principal: Infarto agudo de miocardio con elevación del segmento ST (IAMEST)
✅ CORRECTO: Usa la terminología médica estándar basada en los síntomas + pruebas
❌ INCORRECTO: "Insuficiencia cardíaca" (esto es una complicación, no el diagnóstico de ingreso)

EJEMPLO 2 - Neumología:
Motivo de ingreso: "Fiebre, tos productiva, disnea... Radiografía de tórax con infiltrado alveolar"
→ Diagnóstico principal: Neumonía adquirida en la comunidad
✅ CORRECTO: Diagnóstico específico basado en clínica + imagen
❌ INCORRECTO: "Infección respiratoria aguda" (demasiado genérico)

EJEMPLO 3 - Neurología:
Motivo de ingreso: "Hemiparesia derecha de inicio súbito... TC craneal con hipodensidad en territorio ACM izquierda"
→ Diagnóstico principal: Accidente cerebrovascular isquémico (ACVI)
✅ CORRECTO: Diagnóstico preciso según clínica + imagen
❌ INCORRECTO: "Ictus" (término coloquial, usa terminología médica estándar)

ESTRUCTURA CORRECTA:

3. DIAGNÓSTICO PRINCIPAL
[Diagnóstico específico derivado del motivo de ingreso con terminología médica estándar]

4. DIAGNÓSTICOS SECUNDARIOS
- [Antecedente 1 del contexto del paciente]
- [Antecedente 2 del contexto del paciente]
- [Antecedente 3 del contexto del paciente]

6. TRATAMIENTO Y MEDICACIÓN AL ALTA
- Ácido acetilsalicílico 100mg cada 24 horas
- Clopidogrel 75mg cada 24 horas
- Atorvastatina 80mg cada 24 horas
- Enalapril 10mg cada 12 horas
- Bisoprolol 5mg cada 24 horas

IMPORTANTE: Utiliza nombres estándar de enfermedades y medicamentos. NO incluyas códigos médicos."""
    
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
[Descripció completa del diagnòstic principal derivat del motiu d'ingrés]

4. DIAGNÒSTICS SECUNDARIS
- [Diagnòstic secundari 1]
- [Diagnòstic secundari 2]
- [Diagnòstic secundari 3 si escau]

5. PROCEDIMENTS REALITZATS
{procedures}

6. TRACTAMENT I MEDICACIÓ A L'ALTA
- [Nom medicament] [dosi]mg cada [freqüència]
- [Nom medicament] [dosi]mg cada [freqüència]
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
[Descripción completa del diagnóstico principal derivado del motivo de ingreso]

4. DIAGNÓSTICOS SECUNDARIOS
- [Diagnóstico secundario 1]
- [Diagnóstico secundario 2]
- [Diagnóstico secundario 3 si procede]

5. PROCEDIMIENTOS REALIZADOS
{procedures}

6. TRATAMIENTO Y MEDICACIÓN AL ALTA
- [Nombre medicamento] [dosis]mg cada [frecuencia]
- [Nombre medicamento] [dosis]mg cada [frecuencia]
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

RECORDATORI CRÍTIC - ZERO TOLERÀNCIA A AL·LUCINACIONS:
✓ USA NOMÉS dades del motiu d'ingrés i context del pacient
✓ El DIAGNÒSTIC PRINCIPAL ha de coincidir EXACTAMENT amb la condició descrita al motiu d'ingrés
✓ Utilitza noms estàndard de malalties i medicaments TAL COM APAREIXEN a les dades proporcionades
✓ NO incloguis codis mèdics (SNOMED, ICD-10, ATC) - s'assignaran automàticament
✓ Si tens dubtes sobre un diagnòstic, usa la terminologia EXACTA del motiu d'ingrés"""
        else:
            final_prompt = f"""{context_text}

Genera un informe de alta hospitalaria profesional siguiendo esta estructura:

{filled_template}

RECORDATORIO CRÍTICO - CERO TOLERANCIA A ALUCINACIONES:
✓ USA SOLO datos del motivo de ingreso y contexto del paciente
✓ El DIAGNÓSTICO PRINCIPAL debe coincidir EXACTAMENTE con la condición descrita en el motivo de ingreso
✓ Utiliza nombres estándar de enfermedades y medicamentos TAL COMO APARECEN en los datos proporcionados
✓ NO incluyas códigos médicos (SNOMED, ICD-10, ATC) - se asignarán automáticamente
✓ Si tienes dudas sobre un diagnóstico, usa la terminología EXACTA del motivo de ingreso"""
        
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
