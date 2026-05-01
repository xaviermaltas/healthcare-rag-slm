# Cas d'Ús 1: Informe d'Alta Hospitalària

## 📋 Descripció

Generació assistida d'informes d'alta hospitalària seguint protocols oficials del SAS. El sistema utilitza RAG (Retrieval-Augmented Generation) per recuperar protocols clínics rellevants i generar informes estructurats amb codificació mèdica automàtica.

## 🎯 Objectius

- Reduir temps de redacció: **10 min → 6 min per informe**
- Impacte estimat: **1.285 hores estalviades/any** (19.300 informes/any al SAS)
- Garantir adherència a protocols oficials
- Codificació automàtica amb SNOMED CT, ICD-10 i ATC

## 🏗️ Arquitectura

```
Input (Context Pacient) 
    ↓
RAG Query (especialitat + motiu ingrés)
    ↓
Protocol Retrieval (Qdrant vectorial)
    ↓
LLM Generation (Llama3.2 3B)
    ↓
Text Clínic (sense codis)
    ↓
NER Extraction (diagnòstics + medicacions)
    ↓
Ontology Lookup (SNOMED/ICD-10/ATC)
    ↓
Code Assignment (post-processing)
    ↓
Output (Informe + Codis Validats)
```

## 📊 Resultats d'Avaluació (Actual)

### Mètriques Globals
- **Overall Score**: 51.3%
- **BLEU**: 17.6%
- **ROUGE-L**: 33.1%
- **Completeness**: 97.2%

### Precisió de Codis
- **SNOMED CT F1**: 29.2%
- **ICD-10 F1**: 37.5%
- **ATC F1**: 55.0%

### Detall per Cas

| Cas | Overall | SNOMED F1 | ICD-10 F1 | ATC F1 | Completeness |
|-----|---------|-----------|-----------|--------|--------------|
| Pneumonia | 58.8% | 50.0% | 50.0% | 66.7% | 100% |
| Stroke | 55.9% | 66.7% | 50.0% | 66.7% | 100% |
| Cardiology | 53.3% | 0.0% | 50.0% | 62.5% | 88.9% |
| Diabetes | 37.4% | 0.0% | 0.0% | 20.0% | 100% |

## ✅ Components Implementats

### 1. Prompt Engineering
- **System prompt** multiidioma (ca/es)
- **Few-shot examples** amb casos reals
- **Instruccions clares**: NO generar codis (delegat a post-processing)
- **Template estructurat** amb 9 seccions obligatòries

### 2. Ontology Lookup Tables
- **SNOMED CT**: 70 diagnòstics comuns (cardiovascular, metabòlic, respiratori, neurològic)
- **ICD-10**: 40 codis amb variants clíniques i acrònims
- **ATC**: 109 medicaments amb variants multiidioma

### 3. Medical Coding Service
- Lookup local (ràpid, 95% confidence)
- Fallback a BioPortal API (SNOMED CT, ICD-10)
- Suport multiidioma (ca/es/en)
- Extracció d'acrònims (IAMEST, MPOC, etc.)

### 4. Evaluation Pipeline
- 4 casos de test (cardiologia, endocrinologia, pneumonia, stroke)
- Gold standards de referència
- Mètriques: BLEU, ROUGE, code accuracy, completeness
- Base code matching (E11.9 ↔ E11.10 → 50% credit)

## 🔧 Millores Implementades

### Fase 1: Refactorització (Completada)
✅ Eliminades instruccions de codis del prompt LLM  
✅ Arquitectura correcta: Text → NER → Ontology → Codis  
✅ Few-shot examples amb casos reals  
✅ Lookup tables locals per SNOMED/ICD-10/ATC  

## ⚠️ Limitacions Conegudes

1. **Variabilitat del LLM**: mateix cas genera diferents diagnòstics entre execucions
2. **Codis incorrectes**: LLM ocasionalment genera codis inventats (abans de refactorització)
3. **Diagnòstics incomplets**: alguns casos només generen 1-2 diagnòstics quan n'hi ha 4
4. **Medicacions incompletes**: només detecta ~50% de medicacions esperades
5. **Model petit**: Llama3.2 3B té limitacions en raonament clínic complex

## 🚀 Millores Futures

### Curt Termini
- [ ] Validació post-generació: corregir codis incorrectes amb lookup
- [ ] Ampliar lookup tables amb més variants clíniques
- [ ] Millorar extracció de diagnòstics secundaris

### Mitjà Termini
- [ ] Model més gran: Mistral 7B o Llama3 8B
- [ ] RAG enhancement: protocols més específics per especialitat
- [ ] Cross-encoder reranking per rellevància clínica

### Llarg Termini
- [ ] Fine-tuning amb casos reals del SAS
- [ ] Integració amb historial clínic electrònic
- [ ] Validació amb experts mèdics

## 📁 Fitxers Clau

```
src/main/
├── api/routes/discharge_summary.py          # Endpoint principal
├── core/prompts/discharge_summary_template.py  # Prompts i templates
├── core/coding/
│   ├── medical_coding_service.py            # Servei de codificació
│   └── medical_translator.py                # Lookup tables
├── core/parsers/discharge_summary_parser.py # Extracció de codis
└── evaluation/metrics.py                    # Mètriques d'avaluació

scripts/evaluation/
└── evaluate_discharge_summary.py            # Script d'avaluació

data/evaluation/discharge_summary/
├── cases/                                   # Casos de test
├── gold_standard/                           # Referències
└── results/                                 # Resultats d'avaluació
```

## 🔗 API Endpoint

```http
POST /generate/discharge-summary
Content-Type: application/json

{
  "patient_context": "Home de 65 anys amb HTA i dislipèmia...",
  "admission_reason": "Dolor toràcic opressiu...",
  "procedures": ["Coronariografia", "Angioplàstia primària"],
  "current_medications": ["Enalapril 10mg/12h", "Atorvastatina 40mg/24h"],
  "language": "ca",
  "specialty": "Cardiologia"
}
```

**Response:**
```json
{
  "summary": "INFORME D'ALTA HOSPITALÀRIA\n\n1. DADES DEL PACIENT...",
  "diagnoses": [
    {
      "description": "Infart agut de miocardi amb elevació del segment ST",
      "snomed_code": "57054005",
      "icd10_code": "I21.0",
      "is_primary": true
    }
  ],
  "medications": [
    {
      "name": "Enalapril",
      "dose": "10mg",
      "frequency": "cada 12 hores",
      "atc_code": "C09AA02"
    }
  ],
  "metadata": {
    "specialty": "Cardiologia",
    "protocols_used": 5,
    "generation_time_ms": 2341
  }
}
```

## 📈 Fórmula Overall Score

```
Overall = 0.30 × (ROUGE-L + BLEU)/2 
        + 0.20 × Completeness
        + 0.30 × (SNOMED + ICD-10 + ATC)/3
        + 0.20 × Content Score
```

**Objectiu**: ≥ 60% per considerar el sistema production-ready

---

**Estat**: ✅ Funcional (51.3%) | 🔄 En millora contínua  
**Última avaluació**: 30 Abril 2026
