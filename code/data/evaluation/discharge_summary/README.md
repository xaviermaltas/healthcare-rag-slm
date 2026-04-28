# Dataset d'Avaluació - Informes d'Alta Hospitalària

Aquest dataset conté casos clínics de referència per avaluar la qualitat dels informes d'alta generats pel sistema.

## 📚 Documentació Completa

**Llegeix la documentació detallada:** [`src/main/evaluation/README.md`](../../../src/main/evaluation/README.md)

---

## 🎯 Què és això?

Un **sistema d'avaluació automàtica** que compara els informes generats pel nostre sistema amb informes perfectes (gold standards) per mesurar la qualitat objectivament.

**Analogia:** És com un examen estandarditzat per al nostre sistema.

---

## 📁 Estructura

```
discharge_summary/
├── cases/              # 📋 Casos clínics d'entrada (JSON)
│   ├── cardiology_ami_001.json
│   ├── endocrinology_diabetes_001.json
│   └── ...
├── gold_standard/      # ✅ Informes perfectes de referència (TXT)
│   ├── cardiology_ami_001.txt
│   ├── endocrinology_diabetes_001.txt
│   └── ...
├── results/            # 📊 Resultats d'avaluació (auto-generat)
│   ├── cardiology_ami_001_generated.txt
│   ├── cardiology_ami_001_response.json
│   └── evaluation_report_YYYYMMDD_HHMMSS.json
└── README.md          # Aquest fitxer
```

---

## 🔄 Com Funciona?

```
1. INPUT: Cas clínic (JSON)
   ↓
2. PROCÉS: API genera informe
   ↓
3. COMPARACIÓ: Generat vs Gold Standard
   ↓
4. MÈTRIQUES: BLEU, ROUGE, Codis, Completesa
   ↓
5. OUTPUT: Score global + Report detallat
```

---

## 📊 Què Mesurem?

### **1. Similitud Textual (30%)**
- **BLEU**: Coincidència de paraules consecutives
- **ROUGE**: Overlap de seqüències
- **Exemple**: "Infart agut de miocardi" vs "Infart de miocardi" → 0.85

### **2. Completesa Estructural (20%)**
- Presència de 9 seccions obligatòries
- **Exemple**: 9/9 seccions → 100%

### **3. Precisió de Codis (30%)**
- **SNOMED CT**: Codis de diagnòstics
- **ICD-10**: Classificació de malalties
- **ATC**: Codis de medicacions
- **Exemple**: 4/5 codis correctes → 80%

### **4. Contingut Clínic (20%)**
- Nombre de diagnòstics i medicacions
- **Exemple**: 3/3 diagnòstics, 4/5 medicacions → 90%

### **Score Global**
```
Overall = 0.30×Text + 0.20×Completesa + 0.30×Codis + 0.20×Contingut

Qualitat:
🟢 ≥0.8  EXCELLENT
🟡 0.7-0.8  GOOD
🟠 0.6-0.7  ACCEPTABLE
🔴 <0.6  NEEDS IMPROVEMENT
```

---

## 🚀 Ús Ràpid

```bash
# Executar avaluació de tots els casos
python scripts/evaluation/evaluate_discharge_summary.py

# Output: Report amb mitjanes i resultats per cas
```

---

## 📋 Format dels Fitxers

### **Cas Clínic (JSON)**
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
      "atc": ["B01AC06"]
    },
    "expected_diagnoses_count": 3,
    "expected_medications_count": 5
  }
}
```

### **Gold Standard (TXT)**
Informe d'alta complet amb:
- ✅ 9 seccions estructurades
- ✅ Codis SNOMED CT validats
- ✅ Codis ICD-10 correctes
- ✅ Codis ATC per medicacions
- ✅ Redacció professional

---

## 🎯 Per Què Ho Necessitem?

| Abans (Subjectiu) | Després (Objectiu) |
|-------------------|-------------------|
| ❌ "Sembla bé" | ✅ "Score 0.78, BLEU 0.72" |
| ❌ No detectem regressions | ✅ Score baixa → Alerta |
| ❌ Difícil comparar versions | ✅ v1: 0.75 → v2: 0.82 |
| ❌ Sense dades per publicar | ✅ Dataset validat |

---

## 📈 Casos d'Ús

**1. Validar millores**
```
Abans SNOMED CT:  0.78
Després SNOMED CT: 0.85
→ Millora del 9% ✅
```

**2. Comparar especialitats**
```
Cardiologia:     0.85 🟢
Endocrinologia:  0.72 🟡
Neurologia:      0.68 🟠
→ Neurologia necessita millores
```

**3. Regression testing**
```
Commit A: 0.82
Commit B: 0.75
→ Alerta! Possible regressió
```

---

## 🔧 Afegir Nous Casos

1. Crear `cases/nou_cas.json` amb el format especificat
2. Crear `gold_standard/nou_cas.txt` amb l'informe perfecte
3. Executar avaluació

---

## 📚 Més Informació

- **Documentació completa**: [`src/main/evaluation/README.md`](../../../src/main/evaluation/README.md)
- **Codi de mètriques**: [`src/main/evaluation/metrics.py`](../../../src/main/evaluation/metrics.py)
- **Script d'avaluació**: [`scripts/evaluation/evaluate_discharge_summary.py`](../../../scripts/evaluation/evaluate_discharge_summary.py)
