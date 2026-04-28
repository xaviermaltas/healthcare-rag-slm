# Sistema d'Avaluació per Informes d'Alta Hospitalària

## 📋 Índex

1. [Introducció](#introducció)
2. [Per què necessitem avaluació?](#per-què-necessitem-avaluació)
3. [Arquitectura del sistema](#arquitectura-del-sistema)
4. [Components](#components)
5. [Mètriques implementades](#mètriques-implementades)
6. [Com funciona](#com-funciona)
7. [Interpretació de resultats](#interpretació-de-resultats)
8. [Ús del sistema](#ús-del-sistema)

---

## 🎯 Introducció

Aquest mòdul implementa un **sistema complet d'avaluació automàtica** per mesurar la qualitat dels informes d'alta hospitalària generats pel nostre sistema RAG.

L'avaluació es basa en comparar els informes generats amb **gold standards** (informes de referència escrits per professionals mèdics) utilitzant múltiples mètriques objectives.

---

## 🤔 Per què necessitem avaluació?

### **Problema: Validació Subjectiva**
Sense avaluació automàtica:
- ❌ "L'informe sembla bé" → Opinió subjectiva
- ❌ No podem detectar regressions quan fem canvis
- ❌ Difícil comparar diferents versions del sistema
- ❌ No tenim dades objectives per publicacions

### **Solució: Avaluació Objectiva**
Amb aquest sistema:
- ✅ **Mètriques quantitatives**: BLEU 0.72, ROUGE-L 0.78
- ✅ **Detecció de regressions**: Score baixa de 0.78 → 0.65
- ✅ **Benchmark per millores**: Abans 0.78 → Després 0.85 (+9%)
- ✅ **Dades per publicacions**: Dataset validat amb mètriques estàndard

### **Casos d'Ús**

1. **Validació de millores**
   ```
   Abans d'integrar SNOMED CT:  Score 0.78
   Després d'integrar SNOMED CT: Score 0.85
   → Millora del 9% ✅
   ```

2. **Control de qualitat**
   ```
   Cas Cardiologia:     0.85 🟢 EXCELLENT
   Cas Endocrinologia:  0.72 🟡 GOOD
   Cas Neurologia:      0.68 🟠 ACCEPTABLE
   → Neurologia necessita millores
   ```

3. **Regression testing**
   ```
   Commit A: Score 0.82
   Commit B: Score 0.75
   → Alerta! Possible regressió
   ```

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    SISTEMA D'AVALUACIÓ                      │
└─────────────────────────────────────────────────────────────┘

INPUT                    PROCÉS                    OUTPUT
┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│ Cas Clínic   │───────>│   API Call   │───────>│   Informe    │
│   (JSON)     │        │  /generate/  │        │   Generat    │
└──────────────┘        └──────────────┘        └──────────────┘
                                                        │
                                                        ↓
┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│ Gold Standard│───────>│  Comparació  │───────>│  Mètriques   │
│    (TXT)     │        │  + Càlculs   │        │   + Score    │
└──────────────┘        └──────────────┘        └──────────────┘
                                                        │
                                                        ↓
                                                ┌──────────────┐
                                                │    Report    │
                                                │  Avaluació   │
                                                └──────────────┘
```

---

## 📦 Components

### **1. Dataset de Test**
**Ubicació:** `data/evaluation/discharge_summary/`

```
discharge_summary/
├── cases/                  # Casos clínics d'entrada (JSON)
├── gold_standard/          # Informes de referència (TXT)
└── results/                # Resultats d'avaluació (auto-generat)
```

#### **1.1 Casos Clínics (JSON)**
Cada cas conté:
- **Context clínic**: Dades del pacient, antecedents
- **Motiu d'ingrés**: Símptomes, signes vitals
- **Procediments**: Proves realitzades
- **Medicacions actuals**: Tractament previ
- **Metadata**: Codis esperats, comptadors

**Exemple:**
```json
{
  "case_id": "cardiology_ami_001",
  "specialty": "Cardiologia",
  "patient_context": "Home de 65 anys amb HTA...",
  "admission_reason": "Dolor toràcic opressiu...",
  "procedures": ["ECG", "Coronariografia"],
  "current_medications": ["Enalapril", "Atorvastatina"],
  "metadata": {
    "expected_codes": {
      "snomed": ["57054005"],
      "icd10": ["I21.0"],
      "atc": ["B01AC06", "C09AA02"]
    },
    "expected_diagnoses_count": 3,
    "expected_medications_count": 5
  }
}
```

#### **1.2 Gold Standards (TXT)**
Informes d'alta **perfectes** escrits per professionals:
- ✅ Estructura completa (9 seccions)
- ✅ Codis SNOMED CT validats
- ✅ Codis ICD-10 correctes
- ✅ Codis ATC per medicacions
- ✅ Redacció clínica professional

### **2. Mòdul de Mètriques**
**Ubicació:** `src/main/evaluation/metrics.py`

Classes principals:
- `DischargeSummaryMetrics`: Calculador de mètriques
- `EvaluationResult`: Resultats d'avaluació
- Funcions: `calculate_bleu_score()`, `calculate_rouge_scores()`, `calculate_bertscore()`

### **3. Script d'Avaluació**
**Ubicació:** `scripts/evaluation/evaluate_discharge_summary.py`

Automatitza tot el procés:
1. Carrega casos de test
2. Genera informes via API
3. Compara amb gold standards
4. Calcula mètriques
5. Genera reports

---

## 📊 Mètriques Implementades

### **A. Similitud Textual (30% del score global)**

#### **BLEU Score**
- **Què mesura**: Overlap de n-grams (seqüències de paraules)
- **Rang**: 0.0 - 1.0 (més alt = millor)
- **Interpretació**:
  - 0.7-1.0: Excel·lent similitud
  - 0.5-0.7: Bona similitud
  - <0.5: Similitud baixa

**Exemple:**
```
Generat:    "El pacient presenta infart de miocardi"
Referència: "Infart agut de miocardi"
BLEU: 0.75 (75% de coincidència)
```

#### **ROUGE Scores**
- **ROUGE-1**: Overlap de paraules individuals
- **ROUGE-2**: Overlap de bigrames (2 paraules consecutives)
- **ROUGE-L**: Longest Common Subsequence

**Exemple:**
```
Generat:    "Diabetis mellitus tipus 2 amb cetoacidosi"
Referència: "Diabetis mellitus tipus 2 de debut amb cetoacidosi diabètica"

ROUGE-1: 0.85 (85% de paraules coincidents)
ROUGE-2: 0.70 (70% de bigrames coincidents)
ROUGE-L: 0.80 (80% de seqüència comuna)
```

#### **BERTScore** (opcional)
- **Què mesura**: Similitud semàntica amb model BERT
- **Avantatge**: Detecta paràfrasis i sinònims
- **Requereix**: Model BERT (opcional, es pot saltar)

---

### **B. Completesa Estructural (20% del score global)**

Comprova presència de les **9 seccions obligatòries**:

1. ✅ Dades del pacient
2. ✅ Motiu d'ingrés
3. ✅ Diagnòstic principal
4. ✅ Diagnòstics secundaris
5. ✅ Procediments realitzats
6. ✅ Tractament i medicació
7. ✅ Evolució clínica
8. ✅ Recomanacions de seguiment
9. ✅ Contraindicacions

**Càlcul:**
```
Completeness Score = Seccions Presents / 9

Exemple:
- 9/9 seccions → 100%
- 7/9 seccions → 77.8%
- 5/9 seccions → 55.6%
```

---

### **C. Precisió de Codis (30% del score global)**

Extreu i valida codis mèdics:

#### **SNOMED CT** (Diagnòstics)
```
Pattern: \b(\d{6,18})\b

Esperats:  [57054005, 59621000, 370992007]
Generats:  [57054005, 59621000]

Precision: 2/2 = 100% (tots els generats són correctes)
Recall:    2/3 = 66.7% (falta un codi)
F1:        2 * (1.0 * 0.667) / (1.0 + 0.667) = 0.80
```

#### **ICD-10** (Classificació de malalties)
```
Pattern: \b([A-Z]\d{2}(?:\.\d{1,2})?)\b

Esperats:  [I21.0, I10, E78.2]
Generats:  [I21.0, I10, E78.2]

Precision: 100%
Recall:    100%
F1:        1.00
```

#### **ATC** (Medicacions)
```
Pattern: \b([A-Z]\d{2}[A-Z]{2}\d{2})\b

Esperats:  [B01AC06, C09AA02, C10AA05, B01AC04, C07AB07]
Generats:  [B01AC06, C09AA02, C10AA05, B01AC04]

Precision: 4/4 = 100%
Recall:    4/5 = 80%
F1:        0.89
```

**Score de Codis:**
```
Code Accuracy = (SNOMED_F1 + ICD10_F1 + ATC_F1) / 3
              = (0.80 + 1.00 + 0.89) / 3
              = 0.90
```

---

### **D. Contingut Clínic (20% del score global)**

Compta elements clínics:

```
Diagnòstics:
- Generats: 3
- Esperats: 3
- Ratio: 3/3 = 100%

Medicacions:
- Generades: 4
- Esperades: 5
- Ratio: 4/5 = 80%

Content Score = (100% + 80%) / 2 = 90%
```

---

### **E. Score Global (Overall Score)**

**Fórmula ponderada:**
```
Overall Score = 
    0.30 × Text Similarity +
    0.20 × Completeness +
    0.30 × Code Accuracy +
    0.20 × Content Score

Exemple:
= 0.30 × 0.75 +  // BLEU + ROUGE-L / 2
  0.20 × 1.00 +  // 9/9 seccions
  0.30 × 0.90 +  // Codis
  0.20 × 0.90    // Contingut
= 0.225 + 0.200 + 0.270 + 0.180
= 0.875 (87.5%)
```

---

## 🔄 Com Funciona

### **Workflow Complet**

```
1. PREPARACIÓ
   ├─ Llegir cas clínic (JSON)
   ├─ Llegir gold standard (TXT)
   └─ Extreure metadata (codis esperats)

2. GENERACIÓ
   ├─ Cridar API /generate/discharge-summary
   ├─ Passar context clínic
   └─ Rebre informe generat

3. COMPARACIÓ
   ├─ Text generat vs gold standard
   ├─ Extreure codis del text generat
   └─ Comptar seccions presents

4. CÀLCUL DE MÈTRIQUES
   ├─ BLEU, ROUGE, BERTScore
   ├─ Completeness
   ├─ Code Precision/Recall/F1
   └─ Content counts

5. AGREGACIÓ
   ├─ Calcular score global
   ├─ Classificar qualitat
   └─ Generar report

6. OUTPUT
   ├─ Mostrar resultats per pantalla
   ├─ Guardar informe generat
   └─ Exportar report JSON
```

### **Exemple d'Execució**

```bash
# Executar avaluació
python scripts/evaluation/evaluate_discharge_summary.py

# Output:
================================================================================
  Evaluating: cardiology_ami_001
================================================================================

Generating discharge summary...
Calculating metrics...

📊 EVALUATION RESULTS - cardiology_ami_001
================================================================================

📝 TEXT SIMILARITY:
   BLEU:      0.7234
   ROUGE-1:   0.8156
   ROUGE-2:   0.6892
   ROUGE-L:   0.7845

📋 STRUCTURAL COMPLETENESS: 100%
   Sections present: 9/9

🏥 CODE ACCURACY:
   SNOMED CT - P: 100%, R: 66.7%, F1: 0.8000
   ICD-10    - P: 100%, R: 100%, F1: 1.0000
   ATC       - P: 80%, R: 80%, F1: 0.8000

📊 CLINICAL CONTENT:
   Diagnoses:   3 / 3 expected
   Medications: 4 / 5 expected

⭐ OVERALL SCORE: 0.7856 (78.6%)
   Quality: 🟡 GOOD
```

---

## 📈 Interpretació de Resultats

### **Classificació de Qualitat**

| Score | Qualitat | Icona | Interpretació |
|-------|----------|-------|---------------|
| ≥0.8  | EXCELLENT | 🟢 | Informe d'alta qualitat, llest per producció |
| 0.7-0.8 | GOOD | 🟡 | Bon informe, petites millores possibles |
| 0.6-0.7 | ACCEPTABLE | 🟠 | Acceptable, necessita revisions |
| <0.6 | POOR | 🔴 | Necessita millores significatives |

### **Diagnòstic de Problemes**

#### **Score baix en Text Similarity (<0.6)**
**Problema:** Redacció molt diferent del gold standard
**Solucions:**
- Millorar el prompt template
- Afegir més exemples al prompt
- Ajustar temperatura del LLM

#### **Score baix en Completeness (<0.8)**
**Problema:** Falten seccions obligatòries
**Solucions:**
- Revisar validació de resposta
- Millorar instruccions del prompt
- Afegir post-processing per assegurar seccions

#### **Score baix en Code Accuracy (<0.7)**
**Problema:** Codis incorrectes o incomplets
**Solucions:**
- Integrar validació SNOMED CT (Task #48)
- Millorar extracció de codis
- Afegir mapatge automàtic text → codi

#### **Score baix en Content (<0.7)**
**Problema:** Falten diagnòstics o medicacions
**Solucions:**
- Millorar parser d'extracció
- Revisar protocols recuperats (RAG)
- Ajustar filtratge per especialitat

---

## 🚀 Ús del Sistema

### **1. Avaluació Completa**

```bash
# Avaluar tots els casos
cd code
python scripts/evaluation/evaluate_discharge_summary.py

# Output: Report complet amb mitjanes
```

### **2. Avaluació d'un Sol Cas**

```python
from src.main.evaluation.metrics import DischargeSummaryMetrics

# Carregar cas i gold standard
case_data = load_case("cardiology_ami_001.json")
reference = load_gold_standard("cardiology_ami_001.txt")

# Generar informe
generated = generate_discharge_summary(case_data)

# Avaluar
result = DischargeSummaryMetrics.evaluate(
    generated_text=generated['summary'],
    reference_text=reference,
    case_metadata=case_data['metadata']
)

print(f"Overall Score: {result.overall_score:.4f}")
```

### **3. Integració en CI/CD**

```yaml
# .github/workflows/evaluation.yml
- name: Run Evaluation
  run: |
    python scripts/evaluation/evaluate_discharge_summary.py
    
- name: Check Quality Threshold
  run: |
    # Fail if average score < 0.7
    python scripts/check_evaluation_threshold.py --min-score 0.7
```

---

## 📚 Referències

### **Mètriques Utilitzades**

- **BLEU**: Papineni et al. (2002) - "BLEU: a Method for Automatic Evaluation of Machine Translation"
- **ROUGE**: Lin (2004) - "ROUGE: A Package for Automatic Evaluation of Summaries"
- **BERTScore**: Zhang et al. (2020) - "BERTScore: Evaluating Text Generation with BERT"

### **Codis Mèdics**

- **SNOMED CT**: https://www.snomed.org/
- **ICD-10**: https://www.who.int/classifications/icd/en/
- **ATC**: https://www.whocc.no/atc_ddd_index/

---

## 🔧 Manteniment

### **Afegir Nous Casos de Test**

1. Crear fitxer JSON a `data/evaluation/discharge_summary/cases/`
2. Crear gold standard a `data/evaluation/discharge_summary/gold_standard/`
3. Executar avaluació

### **Actualitzar Mètriques**

Editar `src/main/evaluation/metrics.py`:
- Afegir noves mètriques
- Ajustar pesos del score global
- Millorar extractors de codis

### **Personalitzar Reports**

Editar `scripts/evaluation/evaluate_discharge_summary.py`:
- Canviar format d'output
- Afegir visualitzacions
- Exportar a altres formats (CSV, HTML)

---

## ❓ FAQ

**Q: Per què necessitem gold standards?**
A: Són la "veritat" contra la qual comparem. Sense ells, no podem mesurar objectivament la qualitat.

**Q: Quants casos necessitem?**
A: Mínim 10-15 per tenir estadístiques representatives. Més casos = millor validació.

**Q: Què fem si el score és baix?**
A: Analitzar quina mètrica falla i aplicar les solucions corresponents (veure "Diagnòstic de Problemes").

**Q: Es pot executar sense BERTScore?**
A: Sí, BERTScore és opcional. El sistema funciona amb BLEU i ROUGE.

**Q: Com afegim nous tipus de codis?**
A: Afegir pattern a `metrics.py` i actualitzar `_extract_codes()` i `_calculate_code_metrics()`.
