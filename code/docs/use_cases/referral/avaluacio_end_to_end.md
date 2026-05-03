# 📋 CAS 2: INFORME DE DERIVACIÓ - AVALUACIÓ END-TO-END

**Data:** 3 de Maig de 2026  
**Versió del Sistema:** v1.0  
**Model LLM:** Llama 3.2  
**Model Embeddings:** BGE-M3 (1024 dimensions)

---

## 🎯 OBJECTIU

Generar un informe de derivació a especialista amb motiu clínic codificat (SNOMED CT), antecedents rellevants i informació necessària per continuïtat assistencial.

---

## 📊 ESTRUCTURA DEL DOCUMENT

1. [Flux Complet del Procés](#flux-complet-del-procés)
2. [Temps de Resposta per Component](#temps-de-resposta-per-component)
3. [Punts Clau del Flux](#punts-clau-del-flux)
4. [Mètriques Esperades](#mètriques-esperades)
5. [Avantatges d'Aquest Cas d'Ús](#avantatges-daquest-cas-dús)
6. [Riscos i Mitigacions](#riscos-i-mitigacions)

---

## 🔄 FLUX COMPLET DEL PROCÉS

Aquest cas d'ús és **33% més ràpid** que l'informe d'alta (40s vs 60s) i requereix **menys codificació** (només motiu de derivació vs múltiples diagnòstics).

### STEP 1: Validació d'Especialitat Destí (~0.1s)

**Ubicació:** `src/main/api/routes/referral.py`

**Procés:**
1. Comprova `target_specialty` vs llista d'especialitats vàlides
2. Si no especificada, detecta automàticament del `referral_reason`
3. Valida coherència motiu-especialitat
4. Valida nivell d'urgència (urgent/preferent/ordinària)

**Output:** `{specialty: "Digestologia", confidence: 0.95}`

---

### STEP 2: Codificació Semàntica del Motiu (~0.7s)

**Ubicació:** `src/main/core/coding/semantic_coding_service.py`

**Procés Detallat:**

```
Input: "Dolor abdominal persistent, pèrdua de pes"

1. Neteja i preprocessament
   └─> "dolor abdominal persistent"

2. Embedding (BGE-M3)
   └─> vector [1024] (~0.3s)

3. Cerca Qdrant
   └─> query_points(collection="medical_ontologies",
                     filter={ontology_type: "SNOMED_CT"})
   └─> Temps: ~0.4s

4. Resultats:
   ├─ Best: "21522001" (Abdominal pain) - Score: 0.92 ✅
   ├─ Alt: "271681002" (Stomach ache) - Score: 0.85
   └─ Alt: "102568007" (Chronic abdominal pain) - Score: 0.81

5. Fallback a BioPortal (SI score < 0.7)
   └─> En aquest cas: NO (score = 0.92)
```

**Output:** `{snomed_code: "21522001", confidence: 0.92, source: "semantic_retrieval"}`

**Quan es fa Query a BioPortal:**
- Freqüència: ~5% dels casos
- Motius: termes poc comuns, terminologia regional
- Temps: ~500-800ms addicionals

---

### STEP 3: Cerca de Protocols de Derivació (~0.8s)

**Ubicació:** Qdrant Collection `healthcare_rag`

**Query Construïda:**
```
"derivació digestologia dolor abdominal pèrdua pes"
```

**Filtres Aplicats:**
```json
{
  "specialty": "Digestologia",
  "document_type": "protocol_derivacio"
}
```

**Protocols Recuperats (Top-3):**
1. **Protocol SAS 2025** (score: 0.82)
   - Criteris derivació dolor abdominal persistent
   - Pèrdua de pes >5% com a símptoma d'alarma

2. **Guia CAMFiC 2024** (score: 0.75)
   - Criteris derivació preferent a Digestologia

3. **Protocol intern CAP** (score: 0.68)
   - Avaluació inicial abans de derivació

---

### STEP 4: Generació amb LLM (~35s)

**Ubicació:** Ollama `llama3.2:latest`

**Configuració:**
```json
{
  "temperature": 0.2,
  "max_tokens": 800,
  "top_p": 0.9
}
```

**Prompt Components:**
- System: Regles per informe de derivació
- Context: Top-3 protocols recuperats
- Template: 6 seccions obligatòries
- Dades: patient_context + referral_reason + medications

**Output:** Informe estructurat de ~800 tokens

---

### STEP 5: Validació (~0.3s)

**Validacions Aplicades:**

✅ **Completitud:** Totes les 6 seccions presents  
✅ **Codi SNOMED:** Vàlid i coherent amb motiu  
✅ **Coherència:** Especialitat coherent amb motiu  
✅ **Urgència:** Justificada segons protocols

---

### STEP 6: Resposta JSON (~0.2s)

**Estructura Final:**
```json
{
  "referral_summary": "[Text complet]",
  "referral_reason": {
    "description": "Dolor abdominal persistent, pèrdua de pes",
    "snomed_code": "21522001",
    "confidence": 0.92
  },
  "target_specialty": "Digestologia",
  "urgency_level": "preferent",
  "relevant_history": [...],
  "current_medications": [...],
  "requested_tests": [...],
  "sources": [...],
  "validation_status": {...},
  "generation_metadata": {
    "generation_time_seconds": 38.5,
    "protocols_retrieved": 3,
    "bioportal_queries": 0
  }
}
```

---

## ⏱️ TEMPS DE RESPOSTA PER COMPONENT

```
INFORME DE DERIVACIÓ (Total: ~40s)
├─ Validació especialitat:        0.1s   (0.3%)
├─ Codificació SNOMED motiu:      0.7s   (1.8%)
│  ├─ Embedding:                  0.3s
│  └─ Qdrant search:              0.4s
├─ Embedding query protocols:     0.3s   (0.8%)
├─ Cerca Qdrant (protocols):      0.5s   (1.3%)
├─ Construcció prompt:            0.2s   (0.5%)
├─ Generació LLM:                35.0s  (87.5%) ← BOTTLENECK
├─ Extracció i validació:         0.3s   (0.8%)
└─ Construcció resposta:          0.2s   (0.5%)
─────────────────────────────────────────────────
TOTAL                            ~40.0s  (100%)
```

**Comparació amb Informe d'Alta:**
- ✅ **33% més ràpid** (40s vs 60s)
- ✅ **Menys codificació** (1 terme vs 5-10 termes)
- ✅ **Text més curt** (800 tokens vs 2000 tokens)
- ✅ **Menys seccions** (6 vs 9)

---

## 🔍 PUNTS CLAU DEL FLUX

### 1. Quan es fan Queries a BioPortal

**Freqüència:** ~5% dels casos (molt menys que informe d'alta: 10-15%)

**Exemples que NO requereixen BioPortal (score >0.7):**
- "Dolor abdominal" → 21522001 (score: 0.92) ✅
- "Dolor toràcic" → 29857009 (score: 0.95) ✅
- "Hemiparèsia" → 278286009 (score: 0.89) ✅

**Exemples que SÍ requereixen BioPortal (score <0.7):**
- "Mal de panxa persistent" → score: 0.62 → Query BioPortal
- "Marejos constants" → score: 0.58 → Query BioPortal

**Query BioPortal:**
```http
POST https://data.bioontology.org/search
Authorization: apikey {BIOPORTAL_API_KEY}

{
  "q": "mal de panxa persistent",
  "ontologies": "SNOMEDCT",
  "page_size": 5
}
```

---

### 2. Diferències amb Informe d'Alta

| Aspecte | Informe d'Alta | Informe Derivació |
|---------|----------------|-------------------|
| **Ontologies** | SNOMED, ICD-10, ATC | Només SNOMED |
| **Codificació** | 5-10 termes | 1 terme |
| **Temps LLM** | ~45-60s | ~30-45s |
| **Longitud** | ~2000 tokens | ~800 tokens |
| **Seccions** | 9 | 6 |
| **Queries BioPortal** | 10-15% | 5% |
| **Complexitat** | Alta | Mitjana |
| **Risc al·lucinació** | Alt | Mitjà |

---

### 3. Validació de Coherència Especialitat-Motiu

**Matriu de Validació:**

```python
COHERENCE_MATRIX = {
    "dolor_abdominal": ["Digestologia", "Cirurgia General"],
    "dolor_toracic": ["Cardiologia", "Pneumologia"],
    "hemiparesia": ["Neurologia"],
    "dispnea": ["Pneumologia", "Cardiologia"],
    "artralgia": ["Reumatologia", "Traumatologia"]
}
```

**Exemples:**
- ✅ Dolor abdominal → Digestologia (COHERENT)
- ✅ Dolor toràcic → Cardiologia (COHERENT)
- ⚠️ Dolor abdominal → Cardiologia (WARNING)

---

### 4. Nivells d'Urgència

**URGENT (<24h):**
- Símptomes d'alarma greus
- Sospita patologia maligna
- Risc vital

**PREFERENT (<30 dies):**
- Símptomes d'alarma moderats
- Pèrdua de pes >5%
- Dolor persistent sense diagnòstic

**ORDINÀRIA (<60 dies):**
- Símptomes crònics estables
- Seguiment patologia coneguda

---

## 📊 MÈTRIQUES ESPERADES

| Mètrica | Objectiu | Estimat | Estat |
|---------|----------|---------|-------|
| **SNOMED Accuracy** | >90% | ~85% | 🟡 Acceptable |
| **Specialty Coherence** | >95% | ~92% | 🟡 Acceptable |
| **Completeness** | 100% | 100% | ✅ Excel·lent |
| **Urgency Justification** | >90% | ~88% | 🟡 Acceptable |
| **Generation Time** | <45s | ~40s | ✅ Excel·lent |
| **BioPortal Fallback** | <10% | ~5% | ✅ Excel·lent |
| **Overall Quality** | >80% | ~85% | ✅ Excel·lent |

---

## ✅ AVANTATGES D'AQUEST CAS D'ÚS

### 1. Simplicitat i Eficiència
- Menys codificació: 1 terme vs 5-10 termes
- Més ràpid: 33% menys temps
- Menys seccions: 6 vs 9

### 2. Major Precisió
- Focus únic: Un sol diagnòstic
- Menys risc d'al·lucinació
- Validació més senzilla

### 3. Menys Dependència Externa
- BioPortal: Només 5% vs 10-15%
- Ontologies locals suficients
- Fallback rar

### 4. Millor UX
- Temps <45s (acceptable)
- Qualitat consistent
- Validacions clares

---

## ⚠️ RISCOS I MITIGACIONS

### 1. Especialitat Incorrecta

**Risc:** Derivació a especialitat equivocada

**Mitigació:**
```python
if coherence_check == "WARNING":
    return {
        "warning": "Especialitat pot no ser coherent",
        "suggested_specialty": get_suggested_specialty(motiu)
    }
```

### 2. Motiu Insuficient

**Risc:** Informació incompleta per especialista

**Mitigació:**
- Validació longitud mínima (>20 caràcters)
- Prompt demana detalls específics
- Suggeriments de proves complementàries

### 3. Urgència Mal Classificada

**Risc:** Casos urgents classificats com ordinaris

**Mitigació:**
```python
ALARM_KEYWORDS = [
    "sang", "hemorràgia", "pèrdua de pes",
    "febre persistent", "dolor intens"
]

if any(keyword in referral_reason for keyword in ALARM_KEYWORDS):
    suggested_urgency = max(suggested_urgency, "preferent")
```

---

**Document generat:** 3 de Maig de 2026  
**Última actualització:** 18:30 UTC+02:00

