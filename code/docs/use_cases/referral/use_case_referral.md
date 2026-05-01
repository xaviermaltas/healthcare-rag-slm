# Cas d'Ús 2: Informe de Derivació a Especialista

**Estat**: ✅ Implementat i Avaluat  
**Qualitat**: 73.0% (Good)  
**Data última avaluació**: 30 Abril 2026

---

## 📋 Descripció

Generació assistida d'informes de derivació d'atenció primària a especialista. El sistema genera documents estructurats que faciliten la continuïtat assistencial i garanteixen que l'especialista rebi tota la informació clínicament rellevant.

### Objectius
- Millorar qualitat de derivacions (informació completa i estructurada)
- Reduir temps de redacció: **8 min → 4 min per derivació**
- Garantir coherència entre motiu i especialitat destí
- Codificació automàtica del motiu amb SNOMED CT

---

## 📝 Estructura de l'Informe

### Seccions Obligatòries

1. **DADES DEL PACIENT** - Edat, sexe, antecedents rellevants
2. **ESPECIALITAT DESTÍ** - Cardiologia, Neurologia, etc.
3. **URGÈNCIA** - Normal / Preferent / Urgent
4. **MOTIU DE DERIVACIÓ** - Descripció clínica, símptomes, durada
5. **ANTECEDENTS RELLEVANTS** - Patologies cròniques, intervencions prèvies
6. **EXPLORACIONS I PROVES** - Analítiques, proves d'imatge, ECG
7. **TRACTAMENT ACTUAL** - Medicació habitual
8. **INFORMACIÓ ADDICIONAL** - Qüestions específiques per l'especialista

---

## 🏗️ Arquitectura Tècnica

### Pipeline de Generació

```
1. Input (Dades pacient + motiu)
   ↓
2. Detecció Automàtica Especialitat (keywords)
   ↓
3. RAG Query Construction
   "Criteris de derivació a {specialty}. {motiu}"
   ↓
4. Recuperació Protocols (Qdrant)
   Top-5 documents rellevants
   ↓
5. Generació LLM (Llama3.2 3B)
   System prompt + Template + Context
   ↓
6. Codificació SNOMED CT
   Lookup local → BioPortal fallback
   ↓
7. Output (Informe + Metadata)
```

### Components Implementats

**Fitxers clau:**
- `src/main/api/routes/referral.py` - Endpoint principal
- `src/main/core/prompts/referral_template.py` - Templates i prompts
- `src/main/core/coding/medical_coding_service.py` - Codificació SNOMED

**Endpoint API:**
```http
POST /generate/referral
Content-Type: application/json

{
  "patient_context": "Dona de 42 anys, sense antecedents",
  "referral_reason": "Cefalea persistent de 4 mesos...",
  "relevant_history": ["Sense antecedents neurològics"],
  "examinations": ["Exploració neurològica: normal"],
  "current_medications": ["Paracetamol 1g si dolor"],
  "target_specialty": "Neurologia",  // Opcional
  "urgency": "normal",
  "language": "ca"
}
```

### Detecció Automàtica d'Especialitat

El sistema detecta l'especialitat basant-se en keywords del motiu i exploracions:

```python
specialty_keywords = {
    "Cardiologia": ["cor", "cardíac", "toràcic", "ecg", "coronari"],
    "Neurologia": ["cefalea", "neurològic", "convulsió", "ictus"],
    "Endocrinologia": ["tiroide", "hormonal", "diabetis"],
    "Dermatologia": ["pell", "dermatològic", "erupció"],
    "Gastroenterologia": ["abdominal", "digestiu", "estómac"],
    "Reumatologia": ["articular", "artritis", "reumàtic"],
    # ... 11 especialitats suportades
}
```

**Precisió**: 100% en els 6 casos avaluats

---

## 📊 Resultats d'Avaluació

### Mètriques Globals

| Mètrica | Score | Interpretació |
|---------|-------|---------------|
| **Overall Score** | **73.0%** | 🟡 Good |
| **BLEU** | 64.0% | Similitud amb referència |
| **ROUGE-L** | 75.9% | Overlap de contingut |
| **Completeness** | **100%** | Totes les seccions presents |
| **Specialty Accuracy** | **100%** | Detecció perfecta |
| **Urgency Accuracy** | **100%** | Classificació perfecta |
| **SNOMED CT F1** | 0% | Codis no assignats (lookup insuficient) |

### Distribució de Qualitat

```
🟢 Excellent (≥80%):     0 casos (0%)
🟡 Good (70-80%):        6 casos (100%) ✨
🟠 Acceptable (60-70%):  0 casos (0%)
🔴 Poor (<60%):          0 casos (0%)
```

**Consistència perfecta**: Tots els 6 casos superen el 70%

### Resultats per Cas

| Cas | Especialitat | Overall | BLEU | ROUGE-L | Completeness |
|-----|-------------|---------|------|---------|--------------|
| Neurologia (cefalea) | ✓ | 74.4% | 67.5% | 79.4% | 100% |
| Gastroenterologia (dolor abdominal) | ✓ | 74.2% | 68.9% | 77.0% | 100% |
| Endocrinologia (hipertiroïdisme) | ✓ | 73.7% | 66.2% | 77.3% | 100% |
| Reumatologia (artritis) | ✓ | 72.7% | 64.8% | 73.9% | 100% |
| Cardiologia (dolor toràcic) | ✓ | 72.4% | 64.5% | 72.5% | 100% |
| Dermatologia (psoriasi) | ✓ | 70.5% | 61.8% | 71.2% | 100% |

---

## ✅ Punts Forts

### 1. Detecció d'Especialitat (100%)
- Sistema robust basat en keywords mèdiques
- Cobertura de 11 especialitats principals
- Cap error en els 6 casos avaluats

### 2. Classificació d'Urgència (100%)
- Normal: Casos sense risc immediat
- Preferent: Casos amb símptomes significatius
- Urgent: (no avaluat en aquest dataset)

### 3. Completeness Estructural (100%)
- Totes les 8 seccions obligatòries presents
- Format consistent entre casos
- Estructura clara i professional

### 4. Qualitat del Text (75.9% ROUGE-L)
- Terminologia mèdica adequada
- Informació rellevant per l'especialista
- Coherència clínica

---

## ⚠️ Limitacions Identificades

### 1. SNOMED CT Coding (0% F1)

**Problema**: Els codis SNOMED CT no s'assignen.

**Causa**: 
- Termes no presents al lookup local (només 70 termes)
- BioPortal API no troba coincidències exactes
- Exemple: "Dolor toràcic atípic" → no match amb "Chest pain" (29857009)

**Impacte**: 
- Perd ~15% del overall score
- Dificulta integració amb sistemes d'informació clínica

**Solució proposada**:
- Ampliar lookup local a 500+ termes
- Implementar traducció automàtica ca→en
- Fuzzy matching amb threshold de similitud

### 2. Protocols No Recuperats

**Observació**: "No s'han recuperat protocols específics" en tots els casos

**Causa**:
- Corpus de Qdrant no conté protocols de derivació SAS reals
- Query massa genèrica

**Impacte**:
- LLM genera sense guia de protocols oficials
- Possibles desviacions de criteris SAS

**Solució proposada**:
- Indexar protocols de derivació SAS oficials
- Millorar query construction amb metadata
- Implementar reranking per rellevància

### 3. Variabilitat del LLM

**Observació**: Mateix cas pot generar outputs lleugerament diferents

**Causa**: 
- Model petit (Llama3.2 3B)
- Temperature 0.3 (no determinista)

**Solució proposada**:
- Model més gran (Llama3 8B o Mistral 7B)
- Temperature 0.0 per màxima determinisme

---

## 📈 Comparativa amb Cas d'Ús 1

| Mètrica | Cas 1 (Alta) | Cas 2 (Derivació) | Diferència |
|---------|--------------|-------------------|------------|
| **Overall Score** | 51.3% | 73.0% | **+21.7%** ✨ |
| **BLEU** | 17.6% | 64.0% | **+46.4%** |
| **ROUGE-L** | 33.1% | 75.9% | **+42.8%** |
| **Completeness** | 97.2% | 100% | **+2.8%** |
| **SNOMED F1** | 29.2% | 0% | **-29.2%** |

### Per què Cas 2 funciona millor?

1. **Estructura més simple**: 8 seccions vs 9 + subseccions complexes
2. **Menys codificació**: Només SNOMED vs SNOMED+ICD-10+ATC
3. **Output més predictible**: Format més estàndard
4. **Detecció robusta**: Especialitat fàcil de detectar per keywords
5. **Menys variabilitat**: Informes de derivació més homogenis

---

## 🚀 Millores Prioritàries

### Curt Termini (1-2 setmanes)

1. **Ampliar SNOMED CT Lookup Local**
   - Afegir 500+ termes comuns de derivació
   - Variants ca/es/en per cada terme
   - **Impacte esperat**: SNOMED F1 0% → 40-50%, Overall +10-15%

2. **Indexar Protocols de Derivació SAS**
   - Protocols oficials per especialitat
   - Criteris de derivació preferent/urgent
   - **Impacte esperat**: Protocols recuperats 0% → 80%+

3. **Millorar Query Construction**
   - Expandir amb sinònims mèdics
   - Combinar especialitat + símptomes
   - **Impacte esperat**: Recall +20-30%

### Mitjà Termini (2-4 setmanes)

4. **Implementar Reranking**
   - Cross-encoder per rellevància clínica
   - **Impacte esperat**: Precisió protocols +25-30%

5. **Model LLM Més Gran**
   - Llama3 8B o Mistral 7B
   - **Impacte esperat**: Variabilitat -40%, Qualitat +10%

6. **Traducció Automàtica**
   - ca/es → en abans de SNOMED lookup
   - **Impacte esperat**: SNOMED matching +30-40%

---

## 📁 Fitxers i Dataset

### Estructura de Fitxers

```
src/main/
├── api/routes/referral.py                    # Endpoint principal
├── core/prompts/referral_template.py         # Templates i prompts
└── core/coding/medical_coding_service.py     # Codificació SNOMED

data/evaluation/referral/
├── cases/                                    # 6 casos de test
│   ├── cardiology_chest_pain_001.json
│   ├── neurology_headache_001.json
│   ├── endocrinology_thyroid_001.json
│   ├── dermatology_rash_001.json
│   ├── gastro_abdominal_pain_001.json
│   └── rheumatology_arthritis_001.json
├── gold_standard/                            # Referències
│   └── *.txt (6 fitxers)
└── results/                                  # Outputs avaluació
    ├── evaluation_report_20260430_213525.json
    └── *_response.json (6 fitxers)

scripts/evaluation/
├── evaluate_referral.py                      # Script avaluació
└── analyze_referral_completeness.py          # Anàlisi completeness
```

### Dataset d'Avaluació

**6 casos de test** cobreixen les especialitats més comunes:

1. **Cardiologia** - Dolor toràcic atípic amb factors de risc cardiovascular
2. **Neurologia** - Cefalea persistent resistent a tractament
3. **Endocrinologia** - Hipertiroïdisme amb símptomes clàssics
4. **Dermatologia** - Lesions cutànies suggestives de psoriasi
5. **Gastroenterologia** - Dolor abdominal suggestiu de colelitiasi
6. **Reumatologia** - Poliartràlgies amb factor reumatoide positiu

---

## 🎯 Conclusió

El **Cas d'Ús 2 (Informe de Derivació)** és un **èxit** amb:
- ✅ 73% de qualitat global
- ✅ 100% de consistència entre casos
- ✅ Detecció perfecta d'especialitat i urgència
- ✅ Completeness estructural del 100%

**Estat**: **Production-ready** per ús assistit amb validació humana

**Següents passos recomanats**:
1. Ampliar SNOMED lookup (màxim impacte)
2. Indexar protocols SAS reals
3. Implementar reranking per millorar qualitat

**Objectiu**: Arribar a 80%+ de qualitat amb les millores proposades

---

**Última actualització**: 1 Maig 2026  
**Responsable**: Sistema Healthcare RAG  
**Contacte**: TFM Xavier Maltas
