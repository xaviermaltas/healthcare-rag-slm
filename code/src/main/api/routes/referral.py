"""
Referral Document Generation Endpoint
Endpoint per generar informes de derivació a especialista
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from src.main.infrastructure.llm.ollama_client import OllamaClient
from src.main.infrastructure.vector_db.qdrant_client import HealthcareQdrantClient
from src.main.core.prompts.referral_template import ReferralPrompt
from src.main.core.utils.output_cleaner import OutputCleaner
from src.main.core.utils.code_injector import CodeInjector
from src.main.core.coding.medical_coding_service import MedicalCodingService
from src.main.api.dependencies import get_ollama_client, get_qdrant_client, get_medical_coding_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/generate", tags=["generation"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ReferralRequest(BaseModel):
    """Request model per generació d'informe de derivació"""
    patient_context: str = Field(
        ...,
        description="Context del pacient (edat, sexe, antecedents bàsics)",
        example="Dona de 45 anys, sense antecedents rellevants"
    )
    referral_reason: str = Field(
        ...,
        description="Motiu de la derivació amb símptomes i durada",
        example="Cefalea persistent de 3 mesos d'evolució, resistente a tractament analgèsic habitual"
    )
    relevant_history: List[str] = Field(
        default_factory=list,
        description="Antecedents rellevants per la derivació",
        example=["Sense antecedents neurològics previs", "Sense traumatisme cranial recent"]
    )
    examinations: List[str] = Field(
        default_factory=list,
        description="Exploracions i proves realitzades",
        example=["Exploració neurològica bàsica: sense focalitat", "Fons d'ull: normal"]
    )
    current_medications: List[str] = Field(
        default_factory=list,
        description="Medicació actual del pacient",
        example=["Paracetamol 1g si dolor", "Ibuprofèn 600mg si dolor"]
    )
    target_specialty: Optional[str] = Field(
        None,
        description="Especialitat destí (opcional, es pot detectar automàticament)",
        example="Neurologia"
    )
    urgency: str = Field(
        default="normal",
        description="Nivell d'urgència: normal, preferent, urgent",
        example="normal"
    )
    additional_info: Optional[str] = Field(
        None,
        description="Informació addicional per l'especialista",
        example="Pacient molt preocupada per la persistència dels símptomes"
    )
    language: str = Field(
        default="ca",
        description="Idioma de l'informe (ca/es)",
        example="ca"
    )


class ReferralReasonCode(BaseModel):
    """Codi SNOMED CT del motiu de derivació"""
    description: str
    snomed_code: Optional[str] = None
    confidence: float = 0.0


class ReferralResponse(BaseModel):
    """Response model amb l'informe generat"""
    referral_document: str = Field(
        ...,
        description="Informe de derivació generat"
    )
    target_specialty: str = Field(
        ...,
        description="Especialitat destí detectada o especificada"
    )
    urgency_level: str = Field(
        ...,
        description="Nivell d'urgència"
    )
    referral_reason_codes: List[ReferralReasonCode] = Field(
        default_factory=list,
        description="Codis SNOMED CT del motiu de derivació"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata sobre la generació"
    )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _detect_specialty(referral_reason: str, examinations: List[str]) -> str:
    """
    Detecta l'especialitat més adequada basant-se en el motiu de derivació.
    Utilitza keywords simples per ara (es pot millorar amb NER).
    """
    text = (referral_reason + " " + " ".join(examinations)).lower()
    
    # Keywords per especialitat
    specialty_keywords = {
        "Cardiologia": ["cor", "cardíac", "toràcic", "dolor toràcic", "ecg", "coronari", "infart", "angina", "hipertensió"],
        "Neurologia": ["cefalea", "cap", "neurològic", "convulsió", "epilèpsia", "ictus", "tremolor", "parkinson", "esclerosi"],
        "Endocrinologia": ["diabetis", "tiroide", "hormonal", "obesitat", "metabolisme", "glucosa", "insulina"],
        "Dermatologia": ["pell", "dermatològic", "erupció", "lesió cutània", "psoriasi", "eczema"],
        "Gastroenterologia": ["abdominal", "digestiu", "estómac", "intestí", "diarrea", "restrenyiment", "hígat"],
        "Reumatologia": ["articular", "artritis", "artròsi", "reumàtic", "lupus", "articulació"],
        "Pneumologia": ["respiratori", "pulmonar", "tos", "dispnea", "asma", "mpoc", "bronquitis"],
        "Nefrologia": ["renal", "ronyó", "urinari", "insuficiència renal"],
        "Urologia": ["pròstata", "urològic", "incontinència", "infecció urinària"],
        "Oftalmologia": ["ull", "visió", "oftàlmic", "cataracta", "glaucoma"],
        "Otorrinolaringologia": ["oïda", "nas", "gola", "otitis", "sinusitis", "faringitis"]
    }
    
    # Comptar matches per especialitat
    specialty_scores = {}
    for specialty, keywords in specialty_keywords.items():
        score = sum(1 for keyword in keywords if keyword in text)
        if score > 0:
            specialty_scores[specialty] = score
    
    # Retornar especialitat amb més matches
    if specialty_scores:
        return max(specialty_scores, key=specialty_scores.get)
    
    # Default si no es detecta res
    return "Medicina Interna"


async def _code_referral_reason(
    referral_reason: str,
    coding_service: MedicalCodingService
) -> List[ReferralReasonCode]:
    """
    🔍 NOVA ARQUITECTURA: Codifica el motiu de derivació amb retrieval semàntic
    Extreu les condicions principals i les codifica amb SNOMED CT.
    """
    # Simplificat: agafem el motiu sencer com a diagnòstic
    # En producció, caldria fer NER per extreure condicions específiques
    
    try:
        logger.info(f"🔍 Semantic coding referral reason: '{referral_reason}'")
        
        # Try SEMANTIC SNOMED coding first
        snomed_code = await coding_service.get_snomed_code_semantic(referral_reason)
        
        if snomed_code and snomed_code.confidence >= 0.7:
            logger.info(f"✅ SNOMED ({snomed_code.source}): {snomed_code.code} for referral reason")
            return [ReferralReasonCode(
                description=referral_reason,
                snomed_code=snomed_code.code,
                confidence=snomed_code.confidence
            )]
        
        # Fallback to legacy if semantic fails
        logger.debug("Falling back to legacy coding for referral reason")
        legacy_coded = await coding_service.code_diagnosis(referral_reason, min_confidence=0.7)
        
        if legacy_coded and legacy_coded.snomed_code:
            logger.info(f"⚠️ SNOMED (legacy): {legacy_coded.snomed_code.code} for referral reason")
            return [ReferralReasonCode(
                description=referral_reason,
                snomed_code=legacy_coded.snomed_code.code,
                confidence=legacy_coded.snomed_code.confidence
            )]
            
    except Exception as e:
        logger.warning(f"Error in semantic coding referral reason: {e}")
    
    # Retornar sense codi si tot falla
    logger.warning(f"❌ No SNOMED code found for referral reason: '{referral_reason}'")
    return [ReferralReasonCode(
        description=referral_reason,
        snomed_code=None,
        confidence=0.0
    )]


# ============================================================================
# ENDPOINT
# ============================================================================

@router.post("/referral", response_model=ReferralResponse)
async def generate_referral(
    request: ReferralRequest,
    llm_client: OllamaClient = Depends(get_ollama_client),
    vector_db: HealthcareQdrantClient = Depends(get_qdrant_client),
    coding_service: MedicalCodingService = Depends(get_medical_coding_service)
) -> ReferralResponse:
    """
    Genera un informe de derivació a especialista.
    
    El sistema:
    1. Detecta l'especialitat destí (si no es proporciona)
    2. Recupera protocols de derivació rellevants
    3. Genera l'informe estructurat
    4. Codifica el motiu amb SNOMED CT
    
    Args:
        request: Dades per generar l'informe
        
    Returns:
        Informe de derivació generat amb codis SNOMED CT
    """
    start_time = datetime.now()
    
    try:
        # STEP 1: Detectar especialitat si no es proporciona
        target_specialty = request.target_specialty
        if not target_specialty:
            target_specialty = _detect_specialty(
                request.referral_reason,
                request.examinations
            )
            logger.info(f"Auto-detected specialty: {target_specialty}")
        
        # STEP 2: Construir query per RAG
        # Combinem motiu + especialitat per recuperar protocols rellevants
        rag_query = f"Criteris de derivació a {target_specialty}. {request.referral_reason}"
        
        # STEP 3: Recuperar protocols de derivació
        logger.info(f"Retrieving referral protocols for: {target_specialty}")
        search_results = await vector_db.search_by_text_filter(
            text_query=rag_query,
            limit=5
        )
        
        retrieved_protocols = [
            {
                "source": result.get("metadata", {}).get("source", "Unknown"),
                "content": result.get("text", "")
            }
            for result in search_results
        ]
        
        logger.info(f"Retrieved {len(retrieved_protocols)} protocols")
        
        # STEP 4: Construir prompt
        prompt = ReferralPrompt.build_prompt(
            patient_context=request.patient_context,
            referral_reason=request.referral_reason,
            relevant_history=request.relevant_history,
            examinations=request.examinations,
            current_medications=request.current_medications,
            target_specialty=target_specialty,
            urgency=request.urgency,
            additional_info=request.additional_info,
            retrieved_protocols=retrieved_protocols,
            language=request.language
        )
        
        system_prompt = ReferralPrompt.get_system_prompt(language=request.language)
        
        logger.info(f"Prompt built - Length: {len(prompt)} chars")
        
        # STEP 5: Generar informe amb LLM
        logger.info("Generating referral document with LLM...")
        response = await llm_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=2000,
            temperature=0.3
        )
        referral_document = response.get("response", "") if isinstance(response, dict) else str(response)
        
        if not referral_document or len(referral_document.strip()) < 50:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate referral - empty or too short response from LLM"
            )
        
        # Clean output - remove internal instructions and unnecessary text
        referral_document = OutputCleaner.extract_main_content(referral_document, language=request.language)
        referral_document = OutputCleaner.clean_referral_report(referral_document, language=request.language)
        
        # Check if LLM generated codes (BEFORE injection)
        import re
        has_llm_codes = bool(re.search(r'\((?:SNOMED|ICD-10|ATC)', referral_document, re.IGNORECASE))
        if has_llm_codes:
            logger.warning(f"⚠️ LLM GENERATED CODES (should not happen): {referral_document[:500]}")
        else:
            logger.info(f"✅ LLM did NOT generate codes - clean text ready for injection")
        
        logger.info(f"Referral document generated and cleaned - Length: {len(referral_document)} chars")
        
        # STEP 6: Codificar motiu de derivació amb SNOMED CT
        logger.info("Coding referral reason with SNOMED CT...")
        referral_reason_codes = await _code_referral_reason(
            request.referral_reason,
            coding_service
        )
        
        # Inject medical codes into referral document
        # Prepare referral reason for code injection
        referral_reason_for_injection = []
        if referral_reason_codes and len(referral_reason_codes) > 0:
            # referral_reason_codes is a list of ReferralReasonCode objects
            first_code = referral_reason_codes[0]
            referral_reason_for_injection = [
                {
                    'description': request.referral_reason,
                    'snomed_code': first_code.snomed_code,
                    'icd10_code': None  # ReferralReasonCode doesn't have icd10_code
                }
            ]
        
        referral_document = CodeInjector.inject_all_codes(
            referral_document,
            diagnoses=referral_reason_for_injection,
            language=request.language
        )
        
        # STEP 7: Construir resposta
        generation_time = (datetime.now() - start_time).total_seconds() * 1000
        
        response = ReferralResponse(
            referral_document=referral_document,
            target_specialty=target_specialty,
            urgency_level=request.urgency,
            referral_reason_codes=referral_reason_codes,
            metadata={
                "protocols_used": len(retrieved_protocols),
                "generation_time_ms": round(generation_time, 2),
                "language": request.language,
                "auto_detected_specialty": request.target_specialty is None
            }
        )
        
        logger.info(f"✅ Referral generated successfully in {generation_time:.0f}ms")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating referral: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate referral: {str(e)}"
        )
