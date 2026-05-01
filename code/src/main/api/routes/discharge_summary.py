"""
Discharge Summary Generation Endpoint
Generates hospital discharge summaries using RAG with SAS protocols
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

from src.main.core.prompts.discharge_summary_template import DischargeSummaryPrompt
from src.main.core.parsers.discharge_summary_parser import DischargeSummaryParser
from src.main.core.specialty_detector import SpecialtyDetector
from src.main.infrastructure.embeddings.bge_m3 import BGEM3Embeddings
from src.main.infrastructure.llm.ollama_client import OllamaClient
from src.main.api.dependencies import get_ollama_client, get_embeddings_model, get_medical_coding_service
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/generate", tags=["generation"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class DischargeSummaryRequest(BaseModel):
    """Request model for discharge summary generation"""
    
    patient_context: str = Field(
        ...,
        description="Patient context (age, gender, relevant medical history)",
        min_length=10,
        max_length=2000,
        example="Pacient home de 65 anys amb antecedents de hipertensió arterial i dislipèmia"
    )
    
    admission_reason: str = Field(
        ...,
        description="Reason for hospital admission",
        min_length=5,
        max_length=500,
        example="Dolor toràcic opressiu amb elevació de troponines"
    )
    
    procedures: List[str] = Field(
        default_factory=list,
        description="List of procedures performed during hospitalization",
        max_items=20,
        example=["ECG de 12 derivacions", "Coronariografia", "Angioplastia primària"]
    )
    
    current_medications: List[str] = Field(
        default_factory=list,
        description="Current medications at discharge",
        max_items=30,
        example=["AAS 100mg/24h", "Clopidogrel 75mg/24h", "Atorvastatina 80mg/24h"]
    )
    
    language: str = Field(
        default="es",
        description="Language for the discharge summary (es/ca)",
        pattern="^(es|ca)$",
        example="es"
    )
    
    specialty: Optional[str] = Field(
        default=None,
        description="Medical specialty for filtering protocols",
        example="Cardiologia"
    )
    
    @validator('procedures', 'current_medications')
    def validate_lists(cls, v):
        """Validate that list items are not empty"""
        if v:
            for item in v:
                if not item or not item.strip():
                    raise ValueError("List items cannot be empty")
        return v


class DiagnosisInfo(BaseModel):
    """Diagnosis information with codes"""
    description: str
    snomed_code: Optional[str] = None
    icd10_code: Optional[str] = None
    is_primary: bool = False


class MedicationInfo(BaseModel):
    """Medication information with codes"""
    name: str
    dosage: str
    atc_code: Optional[str] = None
    duration: Optional[str] = None


class ProtocolSource(BaseModel):
    """Protocol source information"""
    title: str
    specialty: str
    score: float
    official: bool = False


class ValidationStatus(BaseModel):
    """Validation status of the generated summary"""
    all_sections_present: bool
    missing_sections: List[str] = Field(default_factory=list)
    has_diagnoses: bool
    has_medications: bool
    has_follow_up: bool


class DischargeSummaryResponse(BaseModel):
    """Response model for discharge summary generation"""
    
    summary: str = Field(
        ...,
        description="Complete discharge summary document"
    )
    
    diagnoses: List[DiagnosisInfo] = Field(
        default_factory=list,
        description="List of diagnoses with SNOMED CT and ICD-10 codes"
    )
    
    medications: List[MedicationInfo] = Field(
        default_factory=list,
        description="List of medications with ATC codes"
    )
    
    follow_up_recommendations: List[str] = Field(
        default_factory=list,
        description="Follow-up recommendations"
    )
    
    contraindications: List[str] = Field(
        default_factory=list,
        description="Contraindications and warnings"
    )
    
    sources: List[ProtocolSource] = Field(
        default_factory=list,
        description="SAS protocols used as sources"
    )
    
    validation_status: ValidationStatus = Field(
        ...,
        description="Validation status of the generated summary"
    )
    
    generation_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata about the generation process"
    )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _extract_diagnosis_name(description: str) -> str:
    """
    Extract a clean diagnosis name from a verbose LLM-generated description.
    Strips code references and connector phrases so the coding service
    receives a meaningful clinical term. Also extracts acronyms from parentheses.
    """
    import re
    text = description

    # Remove code references: "Codi SNOMED CT és 422504002", "ICD-10: I63", etc.
    text = re.sub(
        r'(?:Codi\s+)?(?:SNOMED(?:\s+CT)?|ICD-10|ATC)\s*(?:és|es|is|:)?\s*[\w.]+',
        '', text, flags=re.IGNORECASE
    )

    # Remove common Catalan/Spanish connector phrases at the start
    text = re.sub(
        r'^(?:El|La|Els|Les)\s+(?:diagnòstic|diagnóstico)\s+(?:principal|secundari)?\s+(?:és|es|del\s+pacient)?\s*(?:un|una)?\s*',
        '', text, flags=re.IGNORECASE
    )
    text = re.sub(
        r'^(?:El|La)\s+pacient\s+(?:presenta|té|pateix)\s*(?:un|una)?\s*',
        '', text, flags=re.IGNORECASE
    )

    # Extract acronym from parentheses if present (e.g., "IAMEST", "MPOC")
    # Try acronym first as it's often more specific for lookup
    acronym_match = re.search(r'\(([A-Z]{3,})\)', text)
    if acronym_match:
        acronym = acronym_match.group(1)
        # Return acronym if it's meaningful (3+ uppercase letters)
        if len(acronym) >= 3:
            return acronym.lower()

    # Take only the first meaningful clause (before first comma/period/parenthesis)
    parts = re.split(r'[,.(]', text)
    result = ''
    for part in parts:
        candidate = part.strip()
        if len(candidate.split()) >= 2:
            result = candidate
            break
    if not result:
        result = text.strip()

    return re.sub(r'\s+', ' ', result).strip() or description


def _inject_codes_into_summary(
    summary_text: str,
    diagnoses: List["DiagnosisInfo"],
    medications: List["MedicationInfo"]
) -> str:
    """
    Inject BioPortal-validated codes into the generated summary text.
    Replaces placeholders or invalid values with real validated codes.
    Uses sequential assignment: codes are matched in order of appearance.
    """
    import re

    text = summary_text

    # Queues of validated codes (in order)
    snomed_queue = [d.snomed_code for d in diagnoses if d.snomed_code]
    icd10_queue  = [d.icd10_code  for d in diagnoses if d.icd10_code]
    atc_queue    = [m.atc_code    for m in medications if m.atc_code]

    # --- SNOMED CT ---
    def replace_snomed(m):
        current = m.group(1).strip().strip('[]')
        if not re.match(r'^\d{6,18}$', current) and snomed_queue:
            return f"{m.group(0).split(':')[0]}: {snomed_queue.pop(0)}"
        return m.group(0)

    text = re.sub(
        r'(?:Codi\s+SNOMED\s+CT|Código\s+SNOMED\s+CT|SNOMED\s+CT)\s*:\s*(.+?)(?=\n|$)',
        replace_snomed, text, flags=re.IGNORECASE
    )

    # --- ICD-10 ---
    def replace_icd10(m):
        current = m.group(1).strip().strip('[]')
        if not re.match(r'^[A-Z]\d{2}(?:\.\d{1,2})?$', current) and icd10_queue:
            return f"{m.group(0).split(':')[0]}: {icd10_queue.pop(0)}"
        return m.group(0)

    text = re.sub(
        r'(?:Codi\s+ICD-10|Código\s+ICD-10|ICD-10)\s*:\s*(.+?)(?=\n|$)',
        replace_icd10, text, flags=re.IGNORECASE
    )

    # --- ATC (inside parentheses like "(Codi ATC: C09AA02)") ---
    def replace_atc(m):
        current = m.group(1).strip().strip('[]')
        if not re.match(r'^[A-Z]\d{2}[A-Z]{2}\d{2}$', current) and atc_queue:
            return f"{m.group(0).split(':')[0]}: {atc_queue.pop(0)}{m.group(2)}"
        return m.group(0)

    text = re.sub(
        r'(?:Codi\s+ATC|Código\s+ATC|ATC)\s*:\s*(.+?)(\)|\n|$)',
        replace_atc, text, flags=re.IGNORECASE
    )

    return text


# ============================================================================
# ENDPOINT
# ============================================================================

@router.post(
    "/discharge-summary",
    response_model=DischargeSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Hospital Discharge Summary",
    description="Generates a structured hospital discharge summary using RAG with SAS protocols",
    responses={
        200: {"description": "Discharge summary generated successfully"},
        400: {"description": "Invalid request parameters"},
        500: {"description": "Internal server error during generation"}
    }
)
async def generate_discharge_summary(
    request: DischargeSummaryRequest,
    ollama_client: OllamaClient = Depends(get_ollama_client),
    embeddings_client: BGEM3Embeddings = Depends(get_embeddings_model),
    coding_service = Depends(get_medical_coding_service)
) -> DischargeSummaryResponse:
    """
    Generate a hospital discharge summary using RAG
    
    This endpoint:
    1. Retrieves relevant SAS protocols from Qdrant
    2. Constructs a prompt using the DischargeSummaryPrompt template
    3. Generates the summary using Ollama
    4. Validates the response structure
    5. Extracts medical codes (SNOMED CT, ICD-10, ATC)
    6. Returns a structured response
    """
    
    start_time = datetime.now()
    
    try:
        logger.info(f"Generating discharge summary - Language: {request.language}, Specialty: {request.specialty}")
        
        # ====================================================================
        # STEP 1: Initialize Qdrant client
        # ====================================================================
        # Note: Ollama and Embeddings clients are injected via dependencies
        
        qdrant_client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT
        )
        
        # ====================================================================
        # STEP 2: Construct query for protocol retrieval
        # ====================================================================
        
        # Build query from admission reason and patient context
        query_text = f"{request.admission_reason} {request.patient_context}"
        if request.procedures:
            query_text += " " + " ".join(request.procedures[:3])  # Top 3 procedures
        
        logger.info(f"Retrieval query: {query_text[:100]}...")
        
        # Generate embedding
        query_result = await embeddings_client.encode_query(query_text)
        query_embedding = query_result.get('dense', query_result.get('embedding', []))
        
        # ====================================================================
        # STEP 3: Detect specialty and retrieve relevant protocols
        # ====================================================================
        
        # Detect specialty from clinical context
        specialty_match = SpecialtyDetector.detect_specialty(
            patient_context=request.patient_context,
            admission_reason=request.admission_reason,
            procedures=request.procedures,
            medications=request.current_medications,
            explicit_specialty=request.specialty
        )
        
        detected_specialty = specialty_match.specialty
        specialty_confidence = specialty_match.confidence
        
        logger.info(f"Detected specialty: {detected_specialty} (confidence: {specialty_confidence:.2f})")
        logger.info(f"Matched terms: {', '.join(specialty_match.matched_terms[:3])}")
        
        # Build filter for specialty
        query_filter = Filter(
            must=[
                FieldCondition(key="type", match=MatchValue(value="protocol_sas"))
            ]
        )
        
        # Try with specialty filter first
        query_filter.must.append(
            FieldCondition(key="specialty", match=MatchValue(value=detected_specialty))
        )
        
        # Search in Qdrant with specialty filter
        protocol_results = qdrant_client.query_points(
            collection_name=settings.QDRANT_COLLECTION,
            query=query_embedding,
            limit=5,
            score_threshold=0.3,
            query_filter=query_filter
        ).points
        
        logger.info(f"Retrieved {len(protocol_results)} protocols for {detected_specialty}")
        
        # Fallback: if not enough protocols, search in related specialties
        if len(protocol_results) < 2 and specialty_confidence > 0.5:
            related_specialties = SpecialtyDetector.get_related_specialties(detected_specialty)
            logger.info(f"Fallback: searching in related specialties: {related_specialties}")
            
            # Remove specialty filter and search again
            query_filter_fallback = Filter(
                must=[
                    FieldCondition(key="type", match=MatchValue(value="protocol_sas"))
                ]
            )
            
            fallback_results = qdrant_client.query_points(
                collection_name=settings.QDRANT_COLLECTION,
                query=query_embedding,
                limit=5,
                score_threshold=0.25,  # Lower threshold for fallback
                query_filter=query_filter_fallback
            ).points
            
            # Combine results, prioritizing specialty matches
            protocol_results = protocol_results + [
                r for r in fallback_results 
                if r.id not in [p.id for p in protocol_results]
            ][:5 - len(protocol_results)]
            
            logger.info(f"After fallback: {len(protocol_results)} total protocols")
        
        # Format protocols for prompt
        retrieved_protocols = []
        sources = []
        
        for hit in protocol_results:
            protocol_info = {
                'title': hit.payload.get('title', 'Unknown'),
                'content': hit.payload.get('content', ''),
                'specialty': hit.payload.get('specialty', 'Unknown'),
                'score': hit.score
            }
            retrieved_protocols.append(protocol_info)
            
            sources.append(ProtocolSource(
                title=protocol_info['title'],
                specialty=protocol_info['specialty'],
                score=round(hit.score, 4),
                official=hit.payload.get('official', False)
            ))
        
        # ====================================================================
        # STEP 4: Build prompt using DischargeSummaryPrompt template
        # ====================================================================
        
        prompt = DischargeSummaryPrompt.build_prompt(
            patient_context=request.patient_context,
            admission_reason=request.admission_reason,
            procedures=request.procedures,
            medications=request.current_medications,
            retrieved_protocols=retrieved_protocols,
            language=request.language
        )
        
        logger.info(f"Prompt built - Length: {len(prompt)} chars")
        
        # ====================================================================
        # STEP 5: Generate summary with Ollama
        # ====================================================================
        
        generation_response = await ollama_client.generate(
            prompt=prompt,
            model=settings.OLLAMA_MODEL,
            temperature=0.3,  # Low temperature for factual medical content
            max_tokens=800  # Reduced for faster generation on CPU
        )
        
        generated_summary = generation_response.get('response', '')
        
        if not generated_summary:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate summary - empty response from LLM"
            )
        
        logger.info(f"Summary generated - Length: {len(generated_summary)} chars")
        
        # ====================================================================
        # STEP 6: Validate response structure
        # ====================================================================
        
        validation_result = DischargeSummaryPrompt.validate_response(
            response=generated_summary,
            language=request.language
        )
        
        missing_sections = [
            section for section, present in validation_result.items()
            if not present
        ]
        
        validation_status = ValidationStatus(
            all_sections_present=len(missing_sections) == 0,
            missing_sections=missing_sections,
            has_diagnoses=True,  # Will be updated after extraction
            has_medications=True,  # Will be updated after extraction
            has_follow_up=True  # Will be updated after extraction
        )
        
        # ====================================================================
        # STEP 7: Extract structured information with improved parser
        # ====================================================================
        
        # Extract sections from the generated summary
        sections = DischargeSummaryParser.extract_sections(generated_summary)
        
        # Extract diagnoses with the new parser
        extracted_diagnoses = DischargeSummaryParser.extract_diagnoses(
            text=generated_summary,
            section_text=sections.get('main_diagnosis', '') + '\n' + sections.get('secondary_diagnoses', '')
        )
        
        # Build diagnoses list
        diagnoses = []
        for extracted_diag in extracted_diagnoses:
            diagnoses.append(DiagnosisInfo(
                description=extracted_diag.description,
                snomed_code=extracted_diag.snomed_code,
                icd10_code=extracted_diag.icd10_code,
                is_primary=extracted_diag.is_primary
            ))
        
        # Extract medications with the new parser
        extracted_medications = DischargeSummaryParser.extract_medications(
            text=generated_summary,
            section_text=sections.get('treatment', '')
        )
        
        # Build medications list
        medications = []
        for extracted_med in extracted_medications:
            medications.append(MedicationInfo(
                name=extracted_med.name,
                dosage=extracted_med.dosage or "See summary",
                frequency=extracted_med.frequency,
                route=extracted_med.route,
                atc_code=extracted_med.atc_code
            ))
        
        # Update validation status
        validation_status.has_diagnoses = len(diagnoses) > 0
        validation_status.has_medications = len(medications) > 0
        
        # ====================================================================
        # STEP 7.5: Enrich with automatic medical coding (if available)
        # ====================================================================
        
        if coding_service:
            try:
                logger.info("🔍 NOVA ARQUITECTURA: Enriching with semantic medical coding...")
                
                # Enrich diagnoses with missing codes (SEMANTIC APPROACH)
                for diag in diagnoses:
                    # Only enrich if codes are missing
                    if not diag.snomed_code or not diag.icd10_code:
                        # Clean up LLM-generated verbose descriptions before lookup
                        clean_desc = _extract_diagnosis_name(diag.description)
                        logger.debug(f"Semantic coding: '{diag.description[:60]}' → '{clean_desc}'")
                        
                        # Try SEMANTIC SNOMED coding first
                        if not diag.snomed_code:
                            snomed_code = await coding_service.get_snomed_code_semantic(clean_desc)
                            if snomed_code and snomed_code.confidence >= 0.6:
                                diag.snomed_code = snomed_code.code
                                logger.info(f"✅ SNOMED ({snomed_code.source}): {diag.snomed_code} for '{clean_desc}'")
                        
                        # Try SEMANTIC ICD-10 coding
                        if not diag.icd10_code:
                            icd10_code = await coding_service.get_icd10_code_semantic(clean_desc)
                            if icd10_code and icd10_code.confidence >= 0.6:
                                diag.icd10_code = icd10_code.code
                                logger.info(f"✅ ICD-10 ({icd10_code.source}): {diag.icd10_code} for '{clean_desc}'")
                        
                        # Fallback to legacy if semantic fails
                        if not diag.snomed_code or not diag.icd10_code:
                            logger.debug(f"Falling back to legacy coding for: {clean_desc}")
                            legacy_result = await coding_service.code_diagnosis(
                                diagnosis_text=clean_desc,
                                min_confidence=0.6
                            )
                            
                            if legacy_result.snomed_code and not diag.snomed_code:
                                diag.snomed_code = legacy_result.snomed_code.code
                                logger.info(f"⚠️ SNOMED (legacy): {diag.snomed_code} for '{clean_desc}'")
                            
                            if legacy_result.icd10_code and not diag.icd10_code:
                                diag.icd10_code = legacy_result.icd10_code.code
                                logger.info(f"⚠️ ICD-10 (legacy): {diag.icd10_code} for '{clean_desc}'")
                
                # Enrich medications with missing ATC codes (SEMANTIC APPROACH)
                for med in medications:
                    if not med.atc_code:
                        # Try SEMANTIC ATC coding first
                        atc_code = await coding_service.get_atc_code_semantic(med.name)
                        if atc_code and atc_code.confidence >= 0.6:
                            med.atc_code = atc_code.code
                            logger.info(f"✅ ATC ({atc_code.source}): {med.atc_code} for '{med.name}'")
                        else:
                            # Fallback to legacy
                            logger.debug(f"Falling back to legacy ATC coding for: {med.name}")
                            legacy_result = await coding_service.code_medication(
                                medication_text=med.name,
                                min_confidence=0.6
                            )
                            
                            if legacy_result.atc_code:
                                med.atc_code = legacy_result.atc_code.code
                                logger.info(f"⚠️ ATC (legacy): {med.atc_code} for '{med.name}'")
                
                logger.info(f"🎯 Semantic coding completed: {len(diagnoses)} diagnoses, {len(medications)} medications")
                
                # STEP 7.6: Inject validated BioPortal codes back into the summary text
                # Replaces LLM-generated placeholders/wrong codes with real validated codes
                generated_summary = _inject_codes_into_summary(
                    generated_summary, diagnoses, medications
                )
                logger.debug("BioPortal codes injected into summary text")
            
            except Exception as e:
                logger.warning(f"Automatic coding failed: {e}")
                # Continue without enrichment
        else:
            logger.debug("Medical coding service not available - skipping automatic coding")
        
        # ====================================================================
        # STEP 8: Extract follow-up recommendations
        # ====================================================================
        
        # Extract follow-up with the new parser
        extracted_follow_ups = DischargeSummaryParser.extract_follow_up(
            text=generated_summary,
            section_text=sections.get('follow_up', '')
        )
        
        follow_up = [fu.description for fu in extracted_follow_ups]
        contraindications = []  # TODO: Implement contraindications extraction
        
        # Update validation status
        validation_status.has_follow_up = len(follow_up) > 0
        
        # ====================================================================
        # STEP 9: Build response
        # ====================================================================
        
        end_time = datetime.now()
        generation_time = (end_time - start_time).total_seconds()
        
        response = DischargeSummaryResponse(
            summary=generated_summary,
            diagnoses=diagnoses,
            medications=medications,
            follow_up_recommendations=follow_up,
            contraindications=contraindications,
            sources=sources,
            validation_status=validation_status,
            generation_metadata={
                'generation_time_seconds': round(generation_time, 2),
                'protocols_retrieved': len(protocol_results),
                'language': request.language,
                'specialty_requested': request.specialty,
                'specialty_detected': detected_specialty,
                'specialty_confidence': round(specialty_confidence, 2),
                'specialty_matched_terms': specialty_match.matched_terms[:3],
                'model': settings.OLLAMA_MODEL,
                'timestamp': end_time.isoformat()
            }
        )
        
        logger.info(f"Discharge summary generated successfully in {generation_time:.2f}s")
        
        return response
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error generating discharge summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate discharge summary: {str(e)}"
        )
