# Integració SNOMED CT - Task #48

Documentació completa de la integració de SNOMED CT per codificació automàtica de diagnòstics i medicacions.

## 📋 Índex

1. [Visió General](#visió-general)
2. [Arquitectura](#arquitectura)
3. [Components](#components)
4. [Configuració](#configuració)
5. [Ús](#ús)
6. [Exemples](#exemples)
7. [Limitacions](#limitacions)
8. [Roadmap](#roadmap)

---

## 🎯 Visió General

### Objectiu

Proporcionar **codificació automàtica** de diagnòstics i medicacions utilitzant ontologies mèdiques estandarditzades (SNOMED CT, ICD-10, ATC) per millorar la precisió i interoperabilitat dels informes d'alta.

### Beneficis

✅ **Codis mèdics precisos**: SNOMED CT i ICD-10 validats per ontologia  
✅ **Interoperabilitat**: Codis estandarditzats reconeguts internacionalment  
✅ **Automatització**: Reducció de temps de codificació manual  
✅ **Qualitat**: Millora de mètriques d'avaluació (+30% esperat)  
✅ **Traçabilitat**: Confiança associada a cada codi generat  

### Impacte Esperat

```
Abans:  ICD-10 F1 = 0%    (codis generats però no exactes)
Després: ICD-10 F1 = 60-80% (codis validats per ontologia)

Score Global: 0.42 → 0.65-0.75 (+55% millora)
```

---

## 🏗️ Arquitectura

### Pipeline de Codificació

```
┌─────────────────────────────────────────────────────────────┐
│                   DISCHARGE SUMMARY API                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: Generate Summary (LLM)                             │
│  → Genera text amb diagnòstics i medicacions                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: Extract Structured Info (Parser)                   │
│  → Extreu diagnòstics, medicacions i codis del text         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: Enrich with Automatic Coding (NEW!)                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  MedicalCodingService                               │   │
│  │  ├─ code_diagnosis()                                │   │
│  │  │  ├─ SNOMED CT search (BioPortal)                 │   │
│  │  │  └─ ICD-10 search (BioPortal)                    │   │
│  │  └─ code_medication()                               │   │
│  │     ├─ ATC search (future)                          │   │
│  │     └─ SNOMED CT search                             │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: Return Enriched Response                           │
│  → Diagnòstics amb SNOMED + ICD-10                          │
│  → Medicacions amb ATC + SNOMED                             │
└─────────────────────────────────────────────────────────────┘
```

### Integració amb BioPortal

```
┌──────────────────────┐
│  MedicalCodingService│
└──────────┬───────────┘
           │
           ├─────────────────────┐
           │                     │
           ▼                     ▼
┌──────────────────┐  ┌──────────────────┐
│  SNOMEDClient    │  │ OntologyManager  │
└────────┬─────────┘  └────────┬─────────┘
         │                     │
         └──────────┬──────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  BioPortal API       │
         │  ├─ SNOMEDCT         │
         │  ├─ ICD10CM          │
         │  └─ MESH             │
         └──────────────────────┘
```

---

## 🔧 Components

### 1. MedicalCodingService

**Ubicació:** `src/main/core/coding/medical_coding_service.py`

**Responsabilitats:**
- Mapatge de diagnòstics a SNOMED CT i ICD-10
- Mapatge de medicacions a ATC i SNOMED CT
- Càlcul de confiança per cada codi
- Cache de resultats per rendiment

**Mètodes principals:**

```python
async def code_diagnosis(diagnosis_text: str, min_confidence: float = 0.6) -> DiagnosisCoding
async def code_medication(medication_text: str, min_confidence: float = 0.6) -> MedicationCoding
async def code_diagnoses_batch(diagnoses: List[str]) -> List[DiagnosisCoding]
async def code_medications_batch(medications: List[str]) -> List[MedicationCoding]
```

### 2. SNOMEDClient

**Ubicació:** `src/main/infrastructure/ontologies/snomed_client.py`

**Responsabilitats:**
- Connexió amb BioPortal API per SNOMED CT
- Cerca de conceptes per text
- Navegació jeràrquica (pares/fills)
- Obtenció de sinònims i definicions

### 3. OntologyManager

**Ubicació:** `src/main/infrastructure/ontologies/ontology_manager.py`

**Responsabilitats:**
- Gestió unificada de múltiples ontologies
- Cerca en ICD-10, MeSH, LOINC
- Cache de conceptes
- Mapatge entre ontologies

---

## ⚙️ Configuració

### 1. Obtenir API Key de BioPortal

1. Registra't a https://bioportal.bioontology.org/account
2. Crea un compte gratuït
3. Copia l'API key del teu perfil

### 2. Configurar Variables d'Entorn

Afegeix a `.env`:

```bash
# BioPortal API Configuration
BIOPORTAL_API_KEY=your_api_key_here
BIOPORTAL_BASE_URL=https://data.bioontology.org
```

### 3. Verificar Configuració

```bash
# Test de connexió
python scripts/tests/test_medical_coding.py
```

**Output esperat:**
```
✅ SNOMED CT client initialized
✅ Ontology Manager initialized
✅ Medical Coding Service ready
```

---

## 💻 Ús

### Ús Automàtic (Integrat en API)

El servei de coding s'executa **automàticament** quan generes un informe d'alta:

```bash
curl -X POST http://localhost:8000/generate/discharge-summary \
  -H "Content-Type: application/json" \
  -d '{
    "patient_context": "Home de 65 anys amb hipertensió",
    "admission_reason": "Dolor toràcic amb elevació de troponines",
    "procedures": ["Coronariografia", "Angioplastia"],
    "current_medications": ["Enalapril", "Atorvastatina"]
  }'
```

**Resposta amb codis enriquits:**

```json
{
  "diagnoses": [
    {
      "description": "Infart agut de miocardi",
      "snomed_code": "57054005",
      "icd10_code": "I21.0",
      "is_primary": true
    }
  ],
  "medications": [
    {
      "name": "Enalapril",
      "dosage": "10mg",
      "atc_code": "C09AA02"
    }
  ]
}
```

### Ús Programàtic

```python
from src.main.core.coding import MedicalCodingService
from src.main.infrastructure.ontologies import SNOMEDClient, OntologyManager

# Initialize
snomed_client = SNOMEDClient(api_key="your_key")
ontology_manager = OntologyManager(api_key="your_key")
coding_service = MedicalCodingService(snomed_client, ontology_manager)

# Code a diagnosis
result = await coding_service.code_diagnosis(
    "Diabetis mellitus tipus 2",
    min_confidence=0.6
)

print(f"SNOMED: {result.snomed_code.code}")  # 44054006
print(f"ICD-10: {result.icd10_code.code}")   # E11.9
```

---

## 📚 Exemples

### Exemple 1: Codificar Diagnòstic

```python
diagnosis = "Pneumònia adquirida a la comunitat"
result = await coding_service.code_diagnosis(diagnosis)

# Output:
# SNOMED CT: 385093006 - Community acquired pneumonia
# ICD-10: J18.1 - Lobar pneumonia, unspecified organism
# Confidence: 0.85
```

### Exemple 2: Codificar Medicació

```python
medication = "Metformina"
result = await coding_service.code_medication(medication)

# Output:
# SNOMED CT: 109081006 - Metformin
# ATC: A10BA02 (future implementation)
# Confidence: 0.92
```

### Exemple 3: Batch Coding

```python
diagnoses = [
    "Hipertensió arterial",
    "Dislipèmia",
    "Diabetis tipus 2"
]

results = await coding_service.code_diagnoses_batch(diagnoses)

# Processa 3 diagnòstics en paral·lel
# Temps: ~2s (vs ~6s seqüencial)
```

---

## ⚠️ Limitacions

### Limitacions Actuals

1. **ATC Codes**: No implementat encara (BioPortal no té ATC complet)
   - Solució temporal: Usar base de dades ATC dedicada
   - Roadmap: Integrar amb WHO ATC/DDD Index

2. **Idioma**: Millor rendiment en anglès
   - SNOMED CT té termes en català/castellà però limitats
   - Recomanació: Traduir termes clau a anglès per cerca

3. **Confiança**: Basada en similitud textual simple
   - Millora futura: Usar embeddings semàntics (BERTScore)

4. **Rate Limiting**: BioPortal té límits d'API
   - Compte gratuït: 15 requests/segon
   - Solució: Cache agressiu implementat

### Casos No Coberts

- Codis de procediments (CPT, HCPCS)
- Codis de laboratori (LOINC) - parcial
- Codis d'anatomia patològica
- Codis de radiologia

---

## 🗺️ Roadmap

### Fase 1: ✅ COMPLETADA
- [x] Servei bàsic de coding
- [x] Integració amb BioPortal
- [x] Cache de resultats
- [x] Integració en pipeline d'informes

### Fase 2: 🔄 EN PROGRÉS
- [ ] Tests de validació
- [ ] Re-avaluació pilot amb codis automàtics
- [ ] Documentació completa
- [ ] Mètriques de rendiment

### Fase 3: 📅 PLANIFICADA
- [ ] Integració ATC amb base de dades dedicada
- [ ] Millora de confiança amb embeddings semàntics
- [ ] Suport multiidioma millorat
- [ ] Query expansion amb sinònims SNOMED
- [ ] Validació creuada entre ontologies

### Fase 4: 🔮 FUTUR
- [ ] Fine-tuning de model per mapatge text→codi
- [ ] Integració amb altres ontologies (LOINC, CPT)
- [ ] Sistema de feedback per millorar precisió
- [ ] Dashboard de mètriques de codificació

---

## 📊 Mètriques de Rendiment

### Temps de Resposta (Esperat)

| Operació | Temps | Cache Hit |
|----------|-------|-----------|
| Single diagnosis | ~1-2s | ~0.01s |
| Single medication | ~1-2s | ~0.01s |
| Batch (10 items) | ~3-5s | ~0.1s |

### Precisió (Objectiu)

| Mètrica | Abans | Després | Objectiu |
|---------|-------|---------|----------|
| SNOMED F1 | 0.33 | 0.60 | 0.70 |
| ICD-10 F1 | 0.00 | 0.60 | 0.75 |
| ATC F1 | 0.37 | 0.50 | 0.65 |
| Overall Score | 0.42 | 0.65 | 0.75 |

---

## 🔗 Referències

- **BioPortal**: https://bioportal.bioontology.org/
- **SNOMED CT**: https://www.snomed.org/
- **ICD-10**: https://www.who.int/standards/classifications/classification-of-diseases
- **ATC/DDD**: https://www.whocc.no/atc_ddd_index/

---

## 👥 Contacte

Per preguntes o problemes amb la integració SNOMED CT:
- Crear issue a GitHub
- Revisar logs: `docker logs healthcare-rag-api`
- Verificar API key: `echo $BIOPORTAL_API_KEY`

---

**Última actualització:** 28 Abril 2026  
**Versió:** 1.0.0  
**Estat:** ✅ Implementat, 🧪 En Testing
