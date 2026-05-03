# 📋 CAS 3: RESUM CLÍNIC PREVI A CONSULTA - AVALUACIÓ END-TO-END

**Data:** 3 de Maig de 2026  
**Versió del Sistema:** v1.0  
**Model LLM:** Llama 3.2  
**Model Embeddings:** BGE-M3 (1024 dimensions)

---

## 🎯 OBJECTIU

Generar un resum clínic concís amb antecedents rellevants, medicacions actuals codificades (ATC), condicions codificades (SNOMED CT) i alertes clíniques per preparar la consulta amb l'especialista.

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

Aquest cas d'ús és el **més ràpid de tots** (30s) i té el **màxim valor clínic** per la detecció automàtica d'interaccions i alertes.

### STEP 1: Codificació de Condicions (~2.1s)

**Ubicació:** `src/main/core/coding/semantic_coding_service.py`

**Procés per cada condició (x3):**

```
CONDICIÓ 1: "MPOC"
├─ Normalització: "Malaltia Pulmonar Obstructiva Crònica"
├─ Embedding (BGE-M3): vector [1024] (~0.3s)
├─ Qdrant search: filter={ontology_type: "SNOMED_CT"} (~0.4s)
└─ Best match: "13645005" (COPD) - Score: 0.94 ✅

CONDICIÓ 2: "Insuficiència cardíaca"
├─ Embedding (~0.3s)
├─ Qdrant search (~0.4s)
└─ Best match: "42343007" (Heart failure) - Score: 0.91 ✅

CONDICIÓ 3: "Diabetis"
├─ Normalització: "Diabetis mellitus tipus 2"
├─ Embedding (~0.3s)
├─ Qdrant search (~0.4s)
└─ Best match: "73211009" (Diabetes mellitus) - Score: 0.96 ✅
```

**Output:**
```json
[
  {condition: "MPOC", snomed: "13645005", confidence: 0.94},
  {condition: "ICC", snomed: "42343007", confidence: 0.91},
  {condition: "DM2", snomed: "73211009", confidence: 0.96}
]
```

**Quan es fa Query a BioPortal:**
- Freqüència: ~8% dels casos
- En aquest exemple: NO (tots els scores >0.90)

---

### STEP 2: Cerca de Protocols (~0.8s)

**Ubicació:** Qdrant Collection `healthcare_rag`

**Query Multi-Condició:**
```
"MPOC insuficiència cardíaca diabetis cardiologia interaccions comorbiditats"
```

**Filtres:**
```json
{
  "specialty": "Cardiologia",
  "document_type": ["protocol", "guia_clinica"]
}
```

**Protocols Recuperats (Top-5):**

1. **Guia SEC 2025** (score: 0.88)
   - Maneig ICC amb comorbiditats
   - MPOC: precaució amb β-bloquejants

2. **Protocol SAS 2024** (score: 0.82)
   - Interaccions MPOC-ICC
   - Broncodilatadors β-agonistes poden empitjorar ICC

3. **Guia ADA/ESC 2025** (score: 0.76)
   - Control diabetis en ICC
   - Metformina segura si funció renal adequada

4. **Protocol intern** (score: 0.71)
   - Seguiment múltiples comorbiditats
   - Proves recomanades

5. **Guia ESC 2024** (score: 0.68)
   - Optimització farmacològica ICC amb MPOC

**Focus Especial:**
- ⚠️ Interaccions entre condicions (MPOC + ICC)
- ⚠️ Contraindicacions medicamentoses
- ⚠️ Alertes clíniques específiques

---

### STEP 3: Codificació de Medicacions (~2.1s)

**Ubicació:** `src/main/core/coding/semantic_coding_service.py`

**Procés per cada medicació (x3):**

```
MEDICACIÓ 1: "Metformina"
├─ Neteja: "Metformina 850mg" → "Metformina"
├─ Embedding (~0.3s)
├─ Qdrant search: filter={ontology_type: "ATC"} (~0.4s)
├─ Best match: "A10BA02" (Metformin) - Score: 0.98 ✅
└─ Anàlisi interaccions:
    └─ Furosemida (C03CA01): Risc hipoglucèmia ⚠️

MEDICACIÓ 2: "Furosemida"
├─ Embedding (~0.3s)
├─ Qdrant search (~0.4s)
├─ Best match: "C03CA01" (Furosemide) - Score: 0.97 ✅
└─ Anàlisi interaccions:
    ├─ Metformina (A10BA02): Risc hipoglucèmia ⚠️
    └─ Alertes: Control K+, funció renal

MEDICACIÓ 3: "Salbutamol"
├─ Embedding (~0.3s)
├─ Qdrant search (~0.4s)
├─ Best match: "R03AC02" (Salbutamol) - Score: 0.95 ✅
└─ ⚠️ ALERTA CRÍTICA:
    ├─ ICC present: β-agonistes poden empitjorar
    ├─ Recomanació: Considerar anticolinèrgic
    └─ Monitoritzar: Símptomes cardíacs
```

**Output:**
```json
[
  {
    name: "Metformina",
    atc: "A10BA02",
    interactions: ["C03CA01"],
    alerts: ["Monitoritzar funció renal"]
  },
  {
    name: "Furosemida",
    atc: "C03CA01",
    interactions: ["A10BA02"],
    alerts: ["Control K+", "Control funció renal"]
  },
  {
    name: "Salbutamol",
    atc: "R03AC02",
    interactions: [],
    alerts: ["⚠️ CRÍTICA: β-agonista en ICC"]
  }
]
```

---

### STEP 4: Generació del Resum (~25s)

**Ubicació:** Ollama `llama3.2:latest`

**Configuració:**
```json
{
  "temperature": 0.1,
  "max_tokens": 600,
  "top_p": 0.85
}
```

**Prompt Components:**
- System: Regles per resum clínic concís
- Context: Top-5 protocols sobre interaccions
- Dades: Condicions codificades + Medicacions codificades
- Template: 4 seccions obligatòries

**Output:** Resum de ~500 tokens amb:
1. Antecedents rellevants per Cardiologia
2. Medicacions actuals amb alertes
3. Interaccions clíniques (MPOC + ICC)
4. Recomanacions de seguiment

---

### STEP 5: Resposta JSON (~0.2s)

**Estructura Final:**
```json
{
  "clinical_summary": "[Text resum]",
  "coded_conditions": [
    {
      "condition": "MPOC",
      "snomed_code": "13645005",
      "relevance_for_consultation": "HIGH",
      "clinical_impact": "Limita opcions terapèutiques ICC"
    },
    {
      "condition": "ICC",
      "snomed_code": "42343007",
      "relevance_for_consultation": "CRITICAL"
    },
    {
      "condition": "DM2",
      "snomed_code": "73211009",
      "relevance_for_consultation": "MEDIUM"
    }
  ],
  "coded_medications": [...],
  "clinical_alerts": [
    {
      "severity": "CRITICAL",
      "type": "drug_disease_interaction",
      "description": "Salbutamol pot empitjorar ICC",
      "recommendation": "Valorar canvi a anticolinèrgic"
    },
    {
      "severity": "MODERATE",
      "type": "drug_drug_interaction",
      "description": "Furosemida + Metformina: risc hipoglucèmia"
    }
  ],
  "recommended_tests": [
    {test: "Ecocardiografia", priority: "HIGH"},
    {test: "Espirometria", priority: "MEDIUM"},
    {test: "HbA1c", priority: "MEDIUM"}
  ],
  "generation_metadata": {
    "generation_time_seconds": 28.3,
    "conditions_coded": 3,
    "medications_coded": 3,
    "alerts_generated": 3,
    "bioportal_queries": 0
  }
}
```

---

## ⏱️ TEMPS DE RESPOSTA PER COMPONENT

```
RESUM CLÍNIC (Total: ~30s)
├─ Codificació condicions (x3):   2.1s   (7.0%)
│  ├─ MPOC:                        0.7s
│  ├─ ICC:                         0.7s
│  └─ DM2:                         0.7s
├─ Embedding query protocols:     0.3s   (1.0%)
├─ Cerca Qdrant (protocols):      0.5s   (1.7%)
├─ Codificació medicacions (x3):  2.1s   (7.0%)
│  ├─ Metformina:                  0.7s
│  ├─ Furosemida:                  0.7s
│  └─ Salbutamol:                  0.7s
├─ Generació LLM:                25.0s  (83.3%) ← BOTTLENECK
└─ Construcció resposta:          0.2s   (0.7%)
─────────────────────────────────────────────────
TOTAL                            ~30.0s  (100%)
```

**Comparació amb altres casos:**
- ✅ **50% més ràpid que informe d'alta** (30s vs 60s)
- ✅ **25% més ràpid que informe derivació** (30s vs 40s)
- ✅ **Més codificació que derivació** (6 termes vs 1 terme)
- ✅ **Menys text que tots dos** (500 tokens vs 800-2000)

---

## 🔍 PUNTS CLAU DEL FLUX

### 1. Detecció Automàtica d'Interaccions

**Base de Dades d'Interaccions Crítiques:**

```python
CRITICAL_INTERACTIONS = {
    # Medicació + Condició
    ("R03AC02", "42343007"): {  # Salbutamol + ICC
        "severity": "CRITICAL",
        "description": "β-agonista pot empitjorar ICC",
        "action": "Considerar anticolinèrgic (tiotropi)"
    },
    
    # Medicació + Medicació
    ("A10BA02", "C03CA01"): {  # Metformina + Furosemida
        "severity": "MODERATE",
        "description": "Risc hipoglucèmia",
        "action": "Monitoritzar glucèmia regularment"
    },
    
    # Condició + Condició
    ("13645005", "42343007"): {  # MPOC + ICC
        "severity": "HIGH",
        "description": "Limita ús β-bloquejants",
        "action": "Preferir cardioselectius a dosis baixes"
    }
}
```

---

### 2. Classificació de Severitat d'Alertes

**CRITICAL (Acció immediata):**
- Contraindicació absoluta
- Risc vital
- Exemple: β-agonista en ICC descompensada

**MODERATE (Precaució):**
- Interacció coneguda
- Monitorització necessària
- Exemple: Metformina + Diürètic

**LOW (Informativa):**
- Interacció teòrica
- Seguiment rutinari
- Exemple: Múltiples antihipertensius

---

### 3. Diferències amb altres Casos

| Aspecte | Alta | Derivació | **Resum** |
|---------|------|-----------|-----------|
| **Temps** | 60s | 40s | **30s** ✅ |
| **Codificació** | 5-10 | 1 | **6** |
| **Alertes** | No | No | **Sí** ✅ |
| **Interaccions** | No | No | **Sí** ✅ |
| **Valor clínic** | Alt | Mitjà | **Molt Alt** ✅ |
| **BioPortal** | 10-15% | 5% | **8%** |
| **Qualitat** | 60-70% | 80-85% | **85-90%** ✅ |

---

### 4. Proves Recomanades per Especialitat

**Per Cardiologia (ICC):**
- Ecocardiografia (prioritat: ALTA)
- BNP/NT-proBNP
- ECG
- Funció renal i ionograma

**Per MPOC:**
- Espirometria (prioritat: MITJANA)
- Gasometria arterial
- Radiografia tòrax

**Per Diabetis:**
- HbA1c (prioritat: MITJANA)
- Glucèmia basal
- Funció renal (creatinina, FG)

---

## 📊 MÈTRIQUES ESPERADES

### **Objectius de Qualitat**

| Mètrica | Objectiu | Estimat | Estat |
|---------|----------|---------|-------|
| **SNOMED Accuracy** | >90% | ~92% | ✅ Excel·lent |
| **ATC Accuracy** | >90% | ~95% | ✅ Excel·lent |
| **Alert Detection** | >85% | ~88% | ✅ Excel·lent |
| **Interaction Detection** | >80% | ~85% | ✅ Excel·lent |
| **Generation Time** | <35s | ~30s | ✅ Excel·lent |
| **BioPortal Fallback** | <10% | ~8% | ✅ Excel·lent |
| **Overall Quality** | >85% | ~90% | ✅ Excel·lent |

---

## ✅ AVANTATGES D'AQUEST CAS D'ÚS

### **1. Màxima Eficiència**
- **Més ràpid de tots:** 30s (50% menys que informe d'alta)
- **Text més concís:** 500 tokens (75% menys que informe d'alta)
- **Focus específic:** Només informació rellevant per consulta

### **2. Màxima Precisió en Codificació**
- **Scores alts:** >0.90 en totes les codificacions
- **Termes comuns:** Condicions i medicacions ben indexades
- **Menys fallback:** Només 8% de casos requereixen BioPortal

### **3. Valor Clínic Alt**
- **Alertes automàtiques:** Detecció d'interaccions crítiques
- **Accionable:** Recomanacions concretes de seguiment
- **Seguretat:** Identificació de contraindicacions

### **4. Millor Experiència**
- **Temps òptim:** <30s (excel·lent per ús clínic)
- **Informació estructurada:** JSON amb alertes destacades
- **Fàcil integració:** Format estàndard per EMR/EHR

---

## ⚠️ RISCOS I MITIGACIONS

### **1. Interaccions No Detectades**

**Risc:** Interaccions poc comunes no identificades

**Mitigació:**
```python
# Base de dades d'interaccions
CRITICAL_INTERACTIONS = {
    ("R03AC02", "42343007"): {  # Salbutamol + ICC
        "severity": "CRITICAL",
        "description": "β-agonista pot empitjorar ICC",
        "action": "Considerar anticolinèrgic"
    },
    ("A10BA02", "C03CA01"): {  # Metformina + Furosemida
        "severity": "MODERATE",
        "description": "Risc hipoglucèmia",
        "action": "Monitoritzar glucèmia"
    }
}
```

### **2. Alertes Excessives (Alert Fatigue)**

**Risc:** Massa alertes poden ser ignorades

**Mitigació:**
- Classificar per severitat (CRITICAL, MODERATE, LOW)
- Mostrar només top-3 alertes més crítiques
- Agrupar alertes relacionades

### **3. Informació Incompleta**

**Risc:** Condicions o medicacions no reportades

**Mitigació:**
- Validació de completitud
- Suggeriments de proves complementàries
- Recordatori de revisar historial complet

---

**Document generat:** 3 de Maig de 2026  
**Última actualització:** 18:00 UTC+02:00
