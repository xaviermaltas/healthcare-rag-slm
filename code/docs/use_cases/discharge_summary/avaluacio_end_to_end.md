# 🏥 AVALUACIÓ COMPLETA END-TO-END DEL SISTEMA HEALTHCARE RAG

**Data:** 3 de Maig de 2026  
**Versió del Sistema:** v1.0  
**Model LLM:** Llama 3.2  
**Model Embeddings:** BGE-M3 (1024 dimensions)

---

## 📋 ÍNDEX

1. [CAS 1: Informe d'Alta Hospitalària](#cas-1-informe-dalta-hospitalària)
2. [CAS 2: Informe de Derivació](#cas-2-informe-de-derivació)
3. [CAS 3: Resum Clínic Previ a Consulta](#cas-3-resum-clínic-previ-a-consulta)
4. [Anàlisi Comparativa](#anàlisi-comparativa)
5. [Conclusions i Recomanacions](#conclusions-i-recomanacions)

---

# CAS 1: INFORME D'ALTA HOSPITALÀRIA

## 🎯 OBJECTIU

Generar un informe d'alta hospitalària professional amb diagnòstics codificats (SNOMED CT, ICD-10) i medicacions codificades (ATC), basat en protocols clínics recuperats semànticament.

---

## 🔄 FLUX COMPLET DEL PROCÉS

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ENTRADA: Request del Client                       │
│  - patient_context: "Home 65 anys, HTA, dislipèmia..."              │
│  - admission_reason: "Dolor toràcic, ECG ST↑, troponines↑"          │
│  - procedures: ["ECG", "Coronariografia", "Angioplastia"]           │
│  - current_medications: ["Enalapril", "Atorvastatina", "AAS"]      │
│  - specialty: "Cardiologia"                                          │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│              STEP 1: DETECCIÓ D'ESPECIALITAT                         │
│  📍 src/main/core/specialty_detector.py                             │
│                                                                       │
│  QUÈ FEM: Analitzar el context clínic per detectar l'especialitat   │
│  PER QUÈ: Filtrar protocols rellevants a Qdrant                     │
│                                                                       │
│  PROCÉS:                                                             │
│  1. Extreu keywords del patient_context + admission_reason          │
│  2. Busca matches amb diccionari d'especialitats                    │
│  3. Calcula confidence score                                         │
│                                                                       │
│  OUTPUT: specialty="Cardiologia", confidence=1.0                     │
│  TEMPS: ~0.1s                                                        │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│         STEP 2: GENERACIÓ DE QUERY SEMÀNTICA                         │
│  📍 src/main/api/routes/discharge_summary.py                        │
│                                                                       │
│  QUÈ FEM: Construir query per buscar protocols clínics              │
│  PER QUÈ: Recuperar guies clíniques rellevants per RAG              │
│                                                                       │
│  PROCÉS:                                                             │
│  1. Combina admission_reason + procedures                           │
│  2. Afegeix context de medicacions                                  │
│  3. Query: "Dolor toràcic ECG elevació ST troponines                │
│             coronariografia angioplastia"                            │
│                                                                       │
│  OUTPUT: semantic_query (string)                                     │
│  TEMPS: ~0.05s                                                       │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│    STEP 3: EMBEDDING DE LA QUERY (BGE-M3)                           │
│  📍 src/main/infrastructure/embeddings/bge_m3.py                    │
│                                                                       │
│  QUÈ FEM: Convertir text a vector d'embeddings                      │
│  PER QUÈ: Cerca vectorial semàntica a Qdrant                        │
│                                                                       │
│  PROCÉS:                                                             │
│  1. Model: BAAI/bge-m3 (1024 dimensions)                            │
│  2. encode(query) → numpy array [1024]                              │
│  3. Normalització L2                                                 │
│                                                                       │
│  OUTPUT: query_vector [1024 floats]                                 │
│  TEMPS: ~0.3s                                                        │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│      STEP 4: CERCA SEMÀNTICA A QDRANT                               │
│  📍 Qdrant Vector Database (localhost:6333)                         │
│  📍 Collection: "healthcare_rag"                                     │
│                                                                       │
│  QUÈ FEM: Buscar protocols clínics similars                         │
│  PER QUÈ: Recuperar context per generar informe basat en evidència  │
│                                                                       │
│  PROCÉS:                                                             │
│  1. query_points(                                                    │
│       collection="healthcare_rag",                                   │
│       query=query_vector,                                            │
│       filter={"specialty": "Cardiologia"},                           │
│       limit=5,                                                       │
│       score_threshold=0.5                                            │
│     )                                                                │
│  2. Similarity: Cosine distance                                      │
│  3. Retorna top-5 documents amb score                                │
│                                                                       │
│  OUTPUT: [                                                           │
│    {content: "Protocol AMI...", score: 0.85, specialty: "Cardio"},  │
│    {content: "Guia IAMEST...", score: 0.78, specialty: "Cardio"},   │
│    {content: "Protocol Angioplastia...", score: 0.72, ...},         │
│    ...                                                               │
│  ]                                                                   │
│  TEMPS: ~0.5s                                                        │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│       STEP 5: CONSTRUCCIÓ DEL PROMPT                                │
│  📍 src/main/core/prompts/discharge_summary_template.py             │
│                                                                       │
│  QUÈ FEM: Crear prompt estructurat amb context + instruccions       │
│  PER QUÈ: Guiar el LLM per generar informe de qualitat              │
│                                                                       │
│  PROCÉS:                                                             │
│  1. System prompt: Regles anti-al·lucinació + few-shot examples     │
│  2. Context clínic: Top-3 protocols recuperats                      │
│  3. Template estructurat: 9 seccions obligatòries                   │
│  4. Dades del pacient: context + admission + procedures + meds      │
│                                                                       │
│  COMPONENTS DEL PROMPT:                                              │
│  ┌─────────────────────────────────────────────────────┐            │
│  │ SYSTEM PROMPT (anti-hallucination rules)            │            │
│  │ + Few-shot examples (AMI, Pneumonia, Stroke)        │            │
│  ├─────────────────────────────────────────────────────┤            │
│  │ CONTEXT CLÍNIC:                                      │            │
│  │ 1. Protocol AMI (score: 0.85)                       │            │
│  │ 2. Guia IAMEST (score: 0.78)                        │            │
│  │ 3. Protocol Angioplastia (score: 0.72)              │            │
│  ├─────────────────────────────────────────────────────┤            │
│  │ TEMPLATE ESTRUCTURAT:                                │            │
│  │ 1. Dades pacient: [patient_context]                 │            │
│  │ 2. Motiu ingrés: [admission_reason]                 │            │
│  │ 3. Diagnòstic principal: [A GENERAR]                │            │
│  │ 4. Diagnòstics secundaris: [A GENERAR]              │            │
│  │ 5. Procediments: [procedures]                       │            │
│  │ 6. Tractament: [medications]                        │            │
│  │ 7-9. Evolució, seguiment, contraindicacions         │            │
│  └─────────────────────────────────────────────────────┘            │
│                                                                       │
│  OUTPUT: prompt_complet (string ~2000 tokens)                       │
│  TEMPS: ~0.2s                                                        │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│         STEP 6: GENERACIÓ AMB LLM (Ollama)                          │
│  📍 Ollama (localhost:11434)                                         │
│  📍 Model: llama3.2:latest                                           │
│                                                                       │
│  QUÈ FEM: Generar text de l'informe d'alta                          │
│  PER QUÈ: Crear document clínic professional                        │
│                                                                       │
│  PROCÉS:                                                             │
│  1. POST /api/generate                                               │
│  2. model: "llama3.2:latest"                                         │
│  3. prompt: [prompt_complet]                                         │
│  4. temperature: 0.3 (més determinista)                              │
│  5. Streaming: false                                                 │
│                                                                       │
│  TEMPS: ~45-60 segons ⚠️ BOTTLENECK PRINCIPAL                       │
│                                                                       │
│  OUTPUT: informe_text (markdown estructurat)                        │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│      STEP 7: EXTRACCIÓ D'ENTITATS CLÍNIQUES                         │
│  📍 src/main/api/routes/discharge_summary.py                        │
│                                                                       │
│  QUÈ FEM: Parsejar l'informe generat per extreure diagnòstics       │
│  PER QUÈ: Preparar per codificació semàntica                        │
│                                                                       │
│  PROCÉS:                                                             │
│  1. Regex per secció "DIAGNÒSTIC PRINCIPAL"                         │
│  2. Regex per secció "DIAGNÒSTICS SECUNDARIS"                       │
│  3. Regex per secció "TRACTAMENT I MEDICACIÓ"                       │
│  4. Neteja de text (remove bullets, numbers)                        │
│                                                                       │
│  OUTPUT:                                                             │
│  diagnoses = [                                                       │
│    "Insuficiència cardíaca aguda descompensada",  # ❌ AL·LUCINACIÓ │
│    "Hipertensió arterial",                                           │
│    "Dislipèmia"                                                      │
│  ]                                                                   │
│  medications = ["Enalapril", "Atorvastatina", "AAS"]                │
│  TEMPS: ~0.5s                                                        │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│    STEP 8: CODIFICACIÓ SEMÀNTICA - SNOMED CT                        │
│  📍 src/main/core/coding/semantic_coding_service.py                 │
│  📍 src/main/core/ontology/ontology_indexer.py                      │
│                                                                       │
│  QUÈ FEM: Assignar codis SNOMED CT als diagnòstics                  │
│  PER QUÈ: Estandardització terminològica                            │
│                                                                       │
│  PROCÉS PER CADA DIAGNÒSTIC:                                         │
│  ┌─────────────────────────────────────────────────────┐            │
│  │ 8.1. EMBEDDING DEL TERME                             │            │
│  │   - Input: "Insuficiència cardíaca aguda"           │            │
│  │   - BGE-M3.encode() → vector [1024]                 │            │
│  │   - Temps: ~0.3s                                     │            │
│  ├─────────────────────────────────────────────────────┤            │
│  │ 8.2. CERCA A QDRANT ONTOLOGIES                       │            │
│  │   - Collection: "medical_ontologies"                │            │
│  │   - Filter: {ontology_type: "SNOMED_CT"}            │            │
│  │   - query_points(vector, limit=3)                   │            │
│  │   - Similarity threshold: 0.7                       │            │
│  │   - Temps: ~0.4s                                     │            │
│  ├─────────────────────────────────────────────────────┤            │
│  │ 8.3. RESULTATS SEMANTIC RETRIEVAL                   │            │
│  │   [                                                  │            │
│  │     {code: "42343007",                              │            │
│  │      term: "Acute decompensated heart failure",     │            │
│  │      score: 0.89},                                  │            │
│  │     {code: "84114007",                              │            │
│  │      term: "Heart failure",                         │            │
│  │      score: 0.82}                                   │            │
│  │   ]                                                  │            │
│  ├─────────────────────────────────────────────────────┤            │
│  │ 8.4. SELECCIÓ DEL MILLOR CODI                       │            │
│  │   - Best match: 42343007 (score: 0.89 > 0.7) ✅    │            │
│  │   - Source: "semantic_retrieval"                    │            │
│  ├─────────────────────────────────────────────────────┤            │
│  │ 8.5. FALLBACK (si score < 0.7)                      │            │
│  │   - BioPortal API search (si disponible)            │            │
│  │   - URL: https://data.bioontology.org/search        │            │
│  │   - Params: {q: terme, ontologies: "SNOMEDCT"}     │            │
│  │   - Headers: {Authorization: "apikey {KEY}"}       │            │
│  │   - Temps: ~500-800ms                                │            │
│  │   - ⚠️ NO s'executa si semantic retrieval té èxit  │            │
│  └─────────────────────────────────────────────────────┘            │
│                                                                       │
│  OUTPUT PER DIAGNÒSTIC:                                              │
│  {                                                                   │
│    description: "Insuficiència cardíaca aguda descompensada",       │
│    snomed_code: "42343007",                                          │
│    confidence: 0.89,                                                 │
│    source: "semantic_retrieval"                                      │
│  }                                                                   │
│  TEMPS TOTAL: ~1.5s per 3 diagnòstics                               │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│    STEP 9: CODIFICACIÓ SEMÀNTICA - ICD-10                           │
│  📍 src/main/core/coding/semantic_coding_service.py                 │
│                                                                       │
│  QUÈ FEM: Assignar codis ICD-10 als diagnòstics                     │
│  PER QUÈ: Codificació per facturació i estadístiques                │
│                                                                       │
│  PROCÉS (IDÈNTIC A SNOMED):                                          │
│  1. Embedding del terme                                              │
│  2. query_points(collection="medical_ontologies",                    │
│                  filter={ontology_type: "ICD10"})                    │
│  3. Best match: I50 (Heart failure) score: 0.87                     │
│  4. Fallback a BioPortal si score < 0.7                             │
│                                                                       │
│  OUTPUT:                                                             │
│  {                                                                   │
│    description: "Insuficiència cardíaca aguda descompensada",       │
│    icd10_code: "I50",                                                │
│    confidence: 0.87,                                                 │
│    source: "semantic_retrieval"                                      │
│  }                                                                   │
│  TEMPS TOTAL: ~1.5s per 3 diagnòstics                               │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│    STEP 10: CODIFICACIÓ SEMÀNTICA - ATC                             │
│  📍 src/main/core/coding/semantic_coding_service.py                 │
│                                                                       │
│  QUÈ FEM: Assignar codis ATC a medicacions                          │
│  PER QUÈ: Classificació farmacològica estàndard                     │
│                                                                       │
│  PROCÉS PER CADA MEDICACIÓ:                                          │
│  1. Neteja del nom: "Enalapril 10mg" → "Enalapril"                 │
│  2. Embedding: BGE-M3.encode("Enalapril")                           │
│  3. query_points(collection="medical_ontologies",                    │
│                  filter={ontology_type: "ATC"})                      │
│  4. Best match: C09AA02 (Enalapril) score: 0.95                    │
│                                                                       │
│  QUAN ES FA QUERY A BIOPORTAL:                                       │
│  - Si semantic retrieval score < 0.7                                 │
│  - POST https://data.bioontology.org/search                          │
│  - Headers: {Authorization: "apikey {BIOPORTAL_API_KEY}"}          │
│  - Params: {q: "Enalapril", ontologies: "ATC"}                     │
│  - ⚠️ Requereix BIOPORTAL_API_KEY al .env                          │
│  - ⚠️ ERROR ACTUAL: Mètode _search_bioportal_atc no implementat    │
│                                                                       │
│  OUTPUT:                                                             │
│  medications = [                                                     │
│    {name: "Enalapril", dosage: "10mg", atc_code: "C09AA02"},       │
│    {name: "Atorvastatina", dosage: "40mg", atc_code: "C10AA05"},   │
│    {name: "AAS", dosage: "100mg", atc_code: "B01AC06"}             │
│  ]                                                                   │
│  TEMPS TOTAL: ~2.5s per 5 medicacions                               │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│         STEP 11: CONSTRUCCIÓ DE LA RESPOSTA                         │
│  📍 src/main/api/routes/discharge_summary.py                        │
│                                                                       │
│  QUÈ FEM: Estructurar resposta JSON amb tots els components         │
│  PER QUÈ: Retornar al client en format estandarditzat               │
│                                                                       │
│  COMPONENTS:                                                         │
│  {                                                                   │
│    "summary": "[Text complet de l'informe]",                        │
│    "diagnoses": [                                                    │
│      {                                                               │
│        "description": "Insuficiència cardíaca aguda",               │
│        "snomed_code": "42343007",                                    │
│        "icd10_code": "I50",                                          │
│        "is_primary": true                                            │
│      },                                                              │
│      ...                                                             │
│    ],                                                                │
│    "medications": [...],                                             │
│    "follow_up_recommendations": [...],                               │
│    "contraindications": [...],                                       │
│    "sources": [                                                      │
│      {                                                               │
│        "title": "Protocol AMI",                                      │
│        "specialty": "Cardiologia",                                   │
│        "score": 0.85,                                                │
│        "official": true                                              │
│      }                                                               │
│    ],                                                                │
│    "validation_status": {                                            │
│      "all_sections_present": true,                                   │
│      "has_diagnoses": true,                                          │
│      "has_medications": true                                         │
│    },                                                                │
│    "generation_metadata": {                                          │
│      "generation_time_seconds": 58.3,                                │
│      "protocols_retrieved": 5,                                       │
│      "specialty_detected": "Cardiologia",                            │
│      "specialty_confidence": 1.0                                     │
│    }                                                                 │
│  }                                                                   │
│  TEMPS: ~0.3s                                                        │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    SORTIDA: Response al Client                       │
│                    HTTP 200 OK + JSON                                │
│                    TEMPS TOTAL: ~60 segons                           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## ⏱️ TEMPS DE RESPOSTA PER COMPONENT

```
INFORME D'ALTA (Total: ~60s)
├─ Detecció especialitat:        0.1s   (0.2%)
├─ Embedding query:               0.3s   (0.5%)
├─ Cerca Qdrant (protocols):      0.5s   (0.8%)
├─ Construcció prompt:            0.2s   (0.3%)
├─ Generació LLM:                45.0s  (75.0%) ← BOTTLENECK PRINCIPAL
├─ Extracció entitats:            0.5s   (0.8%)
├─ Codificació SNOMED (x3):       1.5s   (2.5%)
│  ├─ Embedding:                  0.3s
│  ├─ Qdrant search:              0.4s
│  └─ BioPortal (si cal):         0.8s
├─ Codificació ICD-10 (x3):       1.5s   (2.5%)
├─ Codificació ATC (x5):          2.5s   (4.2%)
└─ Construcció resposta:          0.3s   (0.5%)
```

---

## 📊 RESULTATS DE L'AVALUACIÓ

### **Mètriques Globals**

| Mètrica | Valor | Objectiu | Estat |
|---------|-------|----------|-------|
| **Overall Score** | 37.4% | >60% | 🔴 Insuficient |
| **BLEU Score** | 0.158 | >0.3 | 🔴 Baix |
| **ROUGE-L F1** | 0.286 | >0.5 | 🔴 Baix |
| **Completeness** | 100% | 100% | ✅ Excel·lent |
| **SNOMED CT F1** | 0.0% | >80% | 🔴 Crític |
| **ICD-10 F1** | 16.7% | >80% | 🔴 Molt baix |
| **ATC F1** | 20.0% | >80% | 🔴 Molt baix |

### **Resultats per Cas**

| Cas | Overall Score | SNOMED F1 | ICD-10 F1 | ATC F1 | Completeness |
|-----|---------------|-----------|-----------|--------|--------------|
| **Cardiology AMI** | 40.8% | 0% | 33.3% | 0% | 100% |
| **Pneumonia** | 40.3% | 0% | 33.3% | 0% | 100% |
| **Stroke** | 36.0% | 0% | 0% | 40% | 100% |
| **Diabetes** | 32.5% | 0% | 0% | 40% | 100% |

---

## 🔍 ANÀLISI DETALLADA

### **CAS 1: Cardiology AMI (40.8%)**

**Diagnòstics Generats:**
1. ❌ "Insuficiència cardíaca aguda descompensada" (SNOMED: 42343007, ICD-10: I50.9)
   - **Problema:** Hauria de ser "Infart agut de miocardi" (SNOMED: 57054005, ICD-10: I21.0)
   - **Causa:** LLM al·lucina diagnòstic incorrecte

2. ⚠️ Diagnòstic secundari amb ICD-10: I21.9
   - **Observació:** Codi correcte però assignat al diagnòstic secundari en lloc del principal

**Medicacions:**
- Aspirina 100mg → ATC: None ❌
- Enalapril 10mg → ATC: None ❌
- Atorvastatina 40mg → ATC: None ❌

**Errors de Log:**
```
ERROR: 'SemanticCodingService' object has no attribute '_search_bioportal_atc'
WARNING: Automatic coding failed: 'MedicalCodingService' object has no attribute '_get_atc_code_legacy'
```

---

### **CAS 2: Pneumonia (40.3%)**

**Diagnòstics Generats:**
1. ✅ "Pneumònia adquirida a la comunitat" (SNOMED: None, ICD-10: None)
   - **Problema:** Diagnòstic correcte però sense codis assignats
   - **Causa:** Terme no indexat a Qdrant ontologies

2. ❌ "Infecció respiratòria aguda" (SNOMED: 233604007, ICD-10: None)
   - **Problema:** Diagnòstic massa genèric, no sol·licitat

**Errors de Log:**
```
WARNING: No SNOMED code found for: Pneumònia adquirida a la comunitat
WARNING: No ICD-10 code found for: Pneumònia adquirida a la comunitat
```

---

### **CAS 3: Stroke (36.0%)**

**Diagnòstics Generats:**
1. ✅ "Accident cerebrovascular isquèmic (ACVI)" (SNOMED: None, ICD-10: None)
   - **Problema:** Diagnòstic correcte però sense codis
   - **Causa:** Terme "ACVI" no reconegut

2. "Parèsia facial dreta" (SNOMED: None, ICD-10: G51.4)
   - **Observació:** Símptoma, no diagnòstic principal

**Medicacions:**
- Enalapril 10mg → ATC: C09AA02 ✅

---

## ❌ PROBLEMES IDENTIFICATS

### **1. Ontologies Incompletes a Qdrant**

**Termes Catalans No Indexats:**
- "Pneumònia adquirida a la comunitat"
- "Cetoacidosi diabètica"
- "Accident cerebrovascular isquèmic"
- "ACVI" (acrònim)

**Impacte:** 0% F1 SNOMED CT

---

### **2. Mètodes de Fallback Inexistents**

**Errors Crítics:**
```python
# semantic_coding_service.py
AttributeError: 'SemanticCodingService' object has no attribute '_search_bioportal_atc'

# medical_coding_service.py
AttributeError: 'MedicalCodingService' object has no attribute '_get_atc_code_legacy'
```

**Impacte:** Codificació ATC falla completament quan semantic retrieval no troba resultats

---

### **3. Al·lucinacions del LLM**

**Exemples:**
- AMI → Genera "Insuficiència cardíaca" en lloc de "Infart agut de miocardi"
- Afegeix diagnòstics secundaris no sol·licitats
- Interpreta símptomes en lloc de copiar diagnòstic explícit

**Causa:** Prompt insuficientment restrictiu, manca d'examples específics per cada cas

---

### **4. Codificació No S'Aplica al Diagnòstic Principal**

**Observació:** Els codis trobats s'assignen a diagnòstics secundaris, no al principal

**Exemple:**
- Diagnòstic principal: "Insuficiència cardíaca" → SNOMED: 42343007
- Diagnòstic secundari: None → ICD-10: I21.9 (Infart!)

---

## ✅ ASPECTES POSITIUS

1. **Completeness: 100%** - Totes les seccions presents
2. **Semantic Retrieval funciona** - Troba protocols rellevants (scores 0.72-0.85)
3. **Alguns codis correctes** - ICD-10 i ATC funcionen parcialment
4. **Temps de resposta acceptable** - ~60s dins del rang esperat

---

## 🎯 RECOMANACIONS

### **PRIORITAT ALTA (Bloqueig Crític)**

1. **Implementar mètodes de fallback ATC**
   ```python
   # semantic_coding_service.py
   async def _search_bioportal_atc(self, medication: str) -> Optional[MedicalCode]:
       # Implementar cerca a BioPortal per ATC
   ```

2. **Expandir ontologies indexades**
   - Afegir termes catalans comuns
   - Indexar acrònim i variants (ACVI, IAM, etc.)
   - Generar dataset amb 500+ termes més freqüents

### **PRIORITAT MITJANA**

3. **Millorar prompt anti-al·lucinació**
   - Afegir exemple específic d'AMI al few-shot
   - Reforçar instrucció: "Usa EXACTAMENT la terminologia del motiu d'ingrés"

4. **Optimitzar temps de generació LLM**
   - Considerar model més petit (Llama 3.1 8B)
   - Implementar streaming per millor UX

### **PRIORITAT BAIXA**

5. **Afegir validació post-generació**
   - Verificar que diagnòstic principal coincideix amb admission_reason
   - Alertar si codis SNOMED/ICD-10 no coincideixen

---

