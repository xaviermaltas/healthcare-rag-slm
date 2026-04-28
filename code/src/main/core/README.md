# Core Module - Healthcare RAG System

Mòduls de lògica de negoci central del sistema RAG per generació de documents clínics.

## 📁 Estructura

```
src/main/core/
├── coding/                    # 🆕 Codificació automàtica de diagnòstics i medicacions
│   ├── __init__.py
│   └── medical_coding_service.py
├── generation/                # Generació de respostes amb LLM
│   ├── __init__.py
│   └── response_generator.py
├── indexing/                  # Indexació de documents mèdics
│   ├── __init__.py
│   ├── document_indexer.py
│   ├── metadata_extractor.py
│   └── semantic_chunker.py
├── ingestion/                 # Ingestió i processament de documents
│   ├── __init__.py
│   ├── pdf_processor.py
│   ├── text_cleaner.py
│   └── ...
├── parsers/                   # Parsers per extreure informació estructurada
│   ├── __init__.py
│   └── discharge_summary_parser.py
├── prompts/                   # Templates de prompts per LLM
│   ├── __init__.py
│   └── discharge_summary_template.py
├── retrieval/                 # Recuperació i enriquiment semàntic
│   ├── __init__.py
│   ├── hybrid_retriever.py
│   ├── query_processing/
│   └── semantic_annotation.py
└── specialty_detector.py      # Detector d'especialitat mèdica
```

---

## 🧩 Mòduls

### 1. 🆕 **coding/** - Codificació Automàtica de Termes Mèdics

**Propòsit:** Mapatge automàtic de diagnòstics i medicacions a codis estandarditzats (SNOMED CT, ICD-10, ATC).

**Components:**

#### `medical_coding_service.py`

Servei central per codificació automàtica utilitzant ontologies mèdiques.

**Classes principals:**

```python
@dataclass
class MedicalCode:
    """Representa un codi mèdic amb metadata"""
    code: str           # Codi (ex: "57054005", "I21.0", "C09AA02")
    system: str         # Sistema (SNOMED_CT, ICD10, ATC)
    display: str        # Nom del concepte
    confidence: float   # Confiança del mapatge (0.0-1.0)

@dataclass
class DiagnosisCoding:
    """Resultat de codificar un diagnòstic"""
    diagnosis_text: str
    snomed_code: Optional[MedicalCode]
    icd10_code: Optional[MedicalCode]

@dataclass
class MedicationCoding:
    """Resultat de codificar una medicació"""
    medication_text: str
    atc_code: Optional[MedicalCode]
    snomed_code: Optional[MedicalCode]

class MedicalCodingService:
    """Servei de codificació automàtica"""
    
    async def code_diagnosis(diagnosis_text: str, min_confidence: float = 0.6) -> DiagnosisCoding
    async def code_medication(medication_text: str, min_confidence: float = 0.6) -> MedicationCoding
    async def code_diagnoses_batch(diagnoses: List[str]) -> List[DiagnosisCoding]
    async def code_medications_batch(medications: List[str]) -> List[MedicationCoding]
```

**Flux de treball:**

```
Input: "Diabetis mellitus tipus 2"
  ↓
1. Cerca a SNOMED CT (BioPortal API)
   - Semantic types: ['Disease or Syndrome', 'Finding']
   - Retorna: Concept 44054006 "Type 2 diabetes mellitus"
  ↓
2. Cerca a ICD-10 (BioPortal API)
   - Ontology: ICD10CM
   - Retorna: Code E11.9 "Type 2 diabetes mellitus without complications"
  ↓
3. Calcula confiança (similitud textual Jaccard)
   - SNOMED: 0.85
   - ICD-10: 0.82
  ↓
4. Valida threshold (min_confidence = 0.6)
   - Ambdós > 0.6 ✅
  ↓
Output: DiagnosisCoding(
    diagnosis_text="Diabetis mellitus tipus 2",
    snomed_code=MedicalCode(code="44054006", system="SNOMED_CT", ...),
    icd10_code=MedicalCode(code="E11.9", system="ICD10", ...)
)
```

**Optimitzacions:**

- **Cache intern:** Resultats guardats en memòria per evitar crides repetides a l'API
- **Batch processing:** Processament paral·lel de múltiples diagnòstics/medicacions
- **Graceful degradation:** Retorna `None` si no troba codis o confiança baixa

**Dependencies:**
- `SNOMEDClient` (infrastructure/ontologies)
- `OntologyManager` (infrastructure/ontologies)
- BioPortal API key (configuració)

**Ús:**

```python
from src.main.core.coding import MedicalCodingService

# Inicialitzar
coding_service = MedicalCodingService(snomed_client, ontology_manager)

# Codificar diagnòstic
result = await coding_service.code_diagnosis("Infart agut de miocardi")
print(f"SNOMED: {result.snomed_code.code}")  # 57054005
print(f"ICD-10: {result.icd10_code.code}")   # I21.0

# Batch
diagnoses = ["Hipertensió", "Diabetis", "Obesitat"]
results = await coding_service.code_diagnoses_batch(diagnoses)
```

**Integració amb API:**

El servei s'integra automàticament en el pipeline de generació d'informes d'alta:

```
STEP 7: Parser extreu diagnòstics del text LLM
  ↓
STEP 7.5: MedicalCodingService enriqueix amb codis validats
  ↓
STEP 8: Retorna resposta amb codis SNOMED CT + ICD-10
```

**Limitacions actuals:**
- ATC codes: No implementat (BioPortal no té ATC complet)
- Idioma: Millor rendiment en anglès
- Confiança: Basada en similitud textual simple (futur: embeddings semàntics)

**Roadmap:**
- [ ] Integració amb base de dades ATC dedicada
- [ ] Millora de confiança amb BERTScore
- [ ] Suport multiidioma millorat
- [ ] Fine-tuning de model per mapatge text→codi

---

### 2. **generation/** - Generació de Respostes

**Propòsit:** Generació de respostes utilitzant LLM amb context recuperat.

**Components:**
- `response_generator.py`: Orquestració de generació amb prompts i context

---

### 3. **indexing/** - Indexació de Documents

**Propòsit:** Processament i indexació de documents mèdics per cerca semàntica.

**Components:**
- `document_indexer.py`: Indexació de documents a Qdrant
- `metadata_extractor.py`: Extracció de metadata (especialitat, tipus document)
- `semantic_chunker.py`: Divisió semàntica de documents

---

### 4. **ingestion/** - Ingestió de Documents

**Propòsit:** Processament inicial de documents (PDF, TXT, etc.).

**Components:**
- `pdf_processor.py`: Extracció de text de PDFs
- `text_cleaner.py`: Neteja i normalització de text
- Altres processadors específics per format

---

### 5. **parsers/** - Parsers d'Informació Estructurada

**Propòsit:** Extracció d'informació estructurada de text generat.

**Components:**

#### `discharge_summary_parser.py`

Parser per extreure informació estructurada d'informes d'alta.

**Funcionalitat:**
- Extracció de seccions (diagnòstics, medicacions, seguiment)
- Extracció de codis mèdics (SNOMED CT, ICD-10, ATC)
- Suport per formats multi-línia amb sub-bullets

**Mètodes:**
```python
class DischargeSummaryParser:
    @classmethod
    def extract_sections(cls, text: str) -> Dict[str, str]
    
    @classmethod
    def extract_diagnoses(cls, text: str, section_text: str) -> List[ExtractedDiagnosis]
    
    @classmethod
    def extract_medications(cls, text: str, section_text: str) -> List[ExtractedMedication]
    
    @classmethod
    def extract_follow_up(cls, text: str, section_text: str) -> List[ExtractedFollowUp]
```

**Patrons regex:**
- SNOMED CT: `(?:SNOMED|Codi SNOMED)[\s:]*(\d{6,18})`
- ICD-10: `(?:ICD-10|Codi ICD-10)[\s:]*([A-Z]\d{2}(?:\.\d{1,2})?)`
- ATC: `(?:ATC|Codi ATC)[\s:]*([A-Z]\d{2}[A-Z]{2}\d{2})`

---

### 6. **prompts/** - Templates de Prompts

**Propòsit:** Definició de prompts estructurats per guiar el LLM.

**Components:**

#### `discharge_summary_template.py`

Template per generació d'informes d'alta hospitalària.

**Funcionalitat:**
- System prompt amb instruccions mèdiques
- Template multiidioma (català/castellà)
- Exemples de formats de codis (SNOMED CT, ICD-10, ATC)
- Recordatoris crítics sobre format obligatori

**Estructura:**
```python
class DischargeSummaryPrompt:
    @staticmethod
    def build_prompt(
        patient_context: str,
        admission_reason: str,
        procedures: List[str],
        current_medications: List[str],
        retrieved_protocols: List[str],
        language: str = "ca"
    ) -> str
```

---

### 7. **retrieval/** - Recuperació Semàntica

**Propòsit:** Recuperació de documents rellevants amb enriquiment semàntic.

**Components:**
- `hybrid_retriever.py`: Combinació de cerca vectorial + keyword
- `query_processing/`: Processament de queries (NER, expansion)
- `semantic_annotation.py`: Anotació semàntica amb SNOMED CT

---

### 8. **specialty_detector.py** - Detector d'Especialitat

**Propòsit:** Detecció automàtica d'especialitat mèdica a partir del context.

**Funcionalitat:**
- Anàlisi de termes clínics
- Mapatge a especialitats (Cardiologia, Neurologia, etc.)
- Score de confiança

---

## 🔗 Relacions entre Mòduls

```
┌─────────────────────────────────────────────────────────────┐
│                      API Layer                              │
│              (api/routes/discharge_summary.py)              │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  retrieval/  │    │ generation/  │    │   parsers/   │
│              │    │              │    │              │
│ - Cerca docs │    │ - Genera amb │    │ - Extreu     │
│ - Enriqueix  │    │   LLM        │    │   info       │
└──────────────┘    └──────────────┘    └──────────────┘
        │                   │                   │
        │                   │                   ▼
        │                   │            ┌──────────────┐
        │                   │            │   coding/    │ 🆕
        │                   │            │              │
        │                   │            │ - Valida     │
        │                   │            │   codis      │
        │                   │            └──────────────┘
        │                   │                   │
        └───────────────────┴───────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │   infrastructure/     │
                │   - ontologies/       │
                │   - llm/              │
                │   - vector_db/        │
                └───────────────────────┘
```

---

## 🧪 Testing

Cada mòdul té tests associats a `scripts/tests/`:

```bash
# Test coding service
./scripts/utils/activate_and_run.sh python scripts/tests/test_medical_coding.py

# Test parsers
./scripts/utils/activate_and_run.sh python scripts/tests/test_parsers.py

# Test prompts
./scripts/utils/activate_and_run.sh python scripts/tests/test_prompts.py
```

---

## 📚 Documentació Addicional

- **SNOMED CT Integration:** `docs/SNOMED_CT_INTEGRATION.md`
- **Evaluation System:** `src/main/evaluation/README.md`
- **API Documentation:** `docs/API.md`

---

**Última actualització:** 28 Abril 2026  
**Versió:** 2.0.0 (amb integració SNOMED CT)
