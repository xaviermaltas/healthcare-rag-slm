# Casos d'Ús - Healthcare RAG System

Aquest directori conté la documentació completa de cada cas d'ús implementat al sistema Healthcare RAG.

## 📁 Estructura

Cada cas d'ús té la seva pròpia carpeta amb un document unificat que inclou:
- Descripció i objectius
- Arquitectura tècnica
- Resultats d'avaluació
- Punts forts i limitacions
- Millores proposades

```
use_cases/
├── discharge_summary/
│   └── use_case_discharge_summary.md    # Cas d'Ús 1: Informe d'Alta
├── referral/
│   └── use_case_referral.md             # Cas d'Ús 2: Informe de Derivació
└── clinical_summary/
    └── use_case_clinical_summary.md     # Cas d'Ús 3: Resum Clínic (pendent)
```

---

## 📊 Resum dels Casos d'Ús

### 1. Informe d'Alta Hospitalària
**Estat**: ✅ Implementat i Avaluat  
**Qualitat**: 51.3% (Acceptable)  
**Fitxer**: [`discharge_summary/use_case_discharge_summary.md`](discharge_summary/use_case_discharge_summary.md)

**Descripció**: Generació assistida d'informes d'alta hospitalària amb diagnòstics codificats (SNOMED CT, ICD-10) i medicacions (ATC).

**Mètriques clau**:
- BLEU: 17.6%
- ROUGE-L: 33.1%
- Completeness: 97.2%
- SNOMED F1: 29.2%
- ICD-10 F1: 37.5%
- ATC F1: 55.0%

**Impacte**: 19.300 informes/any al SAS, reducció de 10→6 min/informe

---

### 2. Informe de Derivació a Especialista
**Estat**: ✅ Implementat i Avaluat  
**Qualitat**: 73.0% (Good) ⭐  
**Fitxer**: [`referral/use_case_referral.md`](referral/use_case_referral.md)

**Descripció**: Generació d'informes de derivació d'atenció primària a especialista amb detecció automàtica d'especialitat i classificació d'urgència.

**Mètriques clau**:
- BLEU: 64.0%
- ROUGE-L: 75.9%
- Completeness: 100%
- Specialty Detection: 100%
- Urgency Classification: 100%

**Impacte**: Reducció de 8→4 min/derivació, millora qualitat informació

---

### 3. Resum Clínic Previ a Consulta
**Estat**: ⏳ Pendent Implementació  
**Fitxer**: `clinical_summary/use_case_clinical_summary.md` (a crear)

**Descripció**: Síntesi automatitzada de la informació clínica rellevant del pacient abans de la consulta.

**Objectiu**: Reducció temps preparació consulta, millora continuïtat assistencial

---

## 📈 Comparativa de Qualitat

| Cas d'Ús | Overall Score | Completeness | Punts Forts | Limitacions |
|----------|---------------|--------------|-------------|-------------|
| **1. Informe d'Alta** | 51.3% | 97.2% | Codificació múltiple (SNOMED+ICD+ATC) | Variabilitat alta, codis incomplets |
| **2. Informe Derivació** | **73.0%** ✨ | **100%** | Detecció especialitat perfecta | SNOMED coding 0% |
| **3. Resum Clínic** | TBD | TBD | - | - |

---

## 🎯 Objectius Globals

### Mètriques d'Èxit
- **Overall Score**: ≥ 60% (acceptable), ≥ 80% (excel·lent)
- **Completeness**: ≥ 95%
- **Clinical Accuracy**: ≥ 70%
- **Code Accuracy**: ≥ 50% (SNOMED/ICD-10/ATC)

### Impacte Esperat
- **Reducció temps**: 30-50% en redacció d'informes
- **Millora qualitat**: Informació estructurada i completa
- **Adherència protocols**: Guiat per protocols oficials SAS
- **Traçabilitat**: Fonts i codis ontològics verificables

---

## 🚀 Millores Comunes Prioritàries

### 1. SNOMED CT Integration (CRÍTIC)
- Ampliar lookup local a 500+ termes
- Implementar traducció automàtica ca→en
- Fuzzy matching amb threshold

### 2. Corpus de Protocols SAS (CRÍTIC)
- Indexar protocols oficials per especialitat
- Guies clíniques actualitzades
- Criteris de derivació i alta

### 3. Query Expansion (ALTA)
- Sinònims mèdics automàtics
- Variants multiidioma
- Expansió per especialitat

### 4. Reranking (ALTA)
- Cross-encoder per rellevància clínica
- Prioritzar protocols oficials
- Score per especialitat matching

### 5. Model LLM Més Gran (MITJANA)
- Llama3 8B o Mistral 7B
- Millor raonament clínic
- Menys variabilitat

---

## 📖 Com Utilitzar Aquesta Documentació

1. **Per entendre un cas d'ús**: Llegeix el document unificat a la seva carpeta
2. **Per comparar casos**: Consulta aquest README
3. **Per implementar millores**: Revisa la secció "Millores Prioritàries" de cada cas
4. **Per avaluar resultats**: Consulta la secció "Resultats d'Avaluació" de cada document

---

## 🔄 Manteniment

Cada document de cas d'ús s'actualitza quan:
- Es fa una nova avaluació
- S'implementen millores significatives
- Canvien els requisits o protocols
- Es detecten noves limitacions

**Última revisió general**: 1 Maig 2026

---

**Responsable**: TFM Xavier Maltas  
**Sistema**: Healthcare RAG - Junta de Andalucía
