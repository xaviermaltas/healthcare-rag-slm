# 📋 Healthcare RAG - Project Tasks & Planning

**Última actualització:** 21 d'Abril de 2026  
**Focus:** Casos d'Ús Clínics (Informe d'Alta, Derivació, Resum Clínic)

---

## 📊 ESTAT ACTUAL DEL PROJECTE

### ✅ Completat (v0.1 + v0.2)
- Infrastructure completa (Docker, FastAPI, Qdrant, Ollama)
- Pipeline RAG base funcional end-to-end
- BGE-M3 embeddings operatius
- MedicalNER integrat
- Connectors BioPortal, PubMed implementats
- **Query Expansion amb ontologies** ✅ **NOU (21 Abril)**
- **529 documents indexats** (468 ontologies + 61 PubMed) ✅ **NOU (21 Abril)**

### 🎯 Objectiu Actual
**Implementar els 3 casos d'ús clínics prioritaris amb prompts específics i validació**

---

## 🔴 MILESTONE: v0.3 - Clinical Use Cases (PRIORITAT MÀXIMA)

### 🎯 CAS D'ÚS 1: INFORME D'ALTA HOSPITALÀRIA

#### Task #30: Crear endpoint `/generate/discharge-summary`
**Priority:** 🔴 Critical | **Estimació:** 2 dies | **Status:** 📋 Todo

**Descripció:**
Endpoint específic per generar informes d'alta hospitalària amb estructura validada.

**Tasques:**
- [ ] Crear nou router `discharge_summary.py`
- [ ] Definir `DischargeSummaryRequest` amb camps:
  - `patient_context`: str (context del pacient)
  - `admission_reason`: str (motiu d'ingrés)
  - `procedures`: List[str] (procediments realitzats)
  - `current_medications`: List[str] (medicacions actuals)
  - `language`: str = "es" (ca/es)
- [ ] Definir `DischargeSummaryResponse` amb:
  - `summary`: str (informe generat)
  - `diagnoses`: List[Dict] (diagnòstics amb codis SNOMED/ICD-10)
  - `medications`: List[Dict] (medicacions amb codis)
  - `follow_up_recommendations`: List[str]
  - `contraindications`: List[str]
  - `sources`: List[Dict] (protocols utilitzats)
- [ ] Integrar Query Expansion per buscar protocols SAS
- [ ] Validar que retorna codis SNOMED/ICD-10 vàlids
- [ ] Tests amb 3 casos reals

**Dependències:** Task #31 (Prompt template)

---

#### Task #31: Crear prompt template per informe d'alta
**Priority:** 🔴 Critical | **Estimació:** 1 dia | **Status:** 📋 Todo

**Descripció:**
Template estructurat amb seccions obligatòries per informe d'alta.

**Tasques:**
- [ ] Crear `prompts/discharge_summary_template.py`
- [ ] Definir estructura amb seccions:
  ```
  1. DATOS DEL PACIENTE
  2. MOTIVO DE INGRESO
  3. DIAGNÓSTICO PRINCIPAL (con código SNOMED/ICD-10)
  4. DIAGNÓSTICOS SECUNDARIOS
  5. PROCEDIMIENTOS REALIZADOS
  6. TRATAMIENTO Y MEDICACIÓN (con códigos)
  7. EVOLUCIÓN CLÍNICA
  8. RECOMENDACIONES DE SEGUIMIENTO
  9. CONTRAINDICACIONES
  10. FIRMA Y FECHA
  ```
- [ ] Suport multiidioma (ca/es)
- [ ] Validació de camps obligatoris
- [ ] Instruccions per incloure codis ontològics
- [ ] Tests amb 2 exemples

**Dependències:** Cap

---

#### Task #32: Indexar protocols SAS per informes d'alta
**Priority:** 🔴 Critical | **Estimació:** 1 dia | **Status:** 📋 Todo

**Descripció:**
Buscar i indexar protocols oficials del SAS per informes d'alta.

**Tasques:**
- [ ] Buscar protocols SAS online (PDF/web)
- [ ] Descarregar 5-10 protocols rellevants
- [ ] Processar amb PDFConnector
- [ ] Afegir metadata especial: `type: "protocol_sas"`, `specialty`, `official: true`
- [ ] Indexar a Qdrant amb boost factor
- [ ] Verificar retrieval prioritza protocols oficials

**Dependències:** Cap (ja tenim DocumentIndexer)

---

#### Task #33: Filtratge semàntic per especialitat
**Priority:** 🟠 High | **Estimació:** 1 dia | **Status:** 📋 Todo

**Descripció:**
Filtrar documents recuperats per especialitat mèdica rellevant.

**Tasques:**
- [ ] Afegir paràmetre `specialty` a QueryRequest
- [ ] Implementar filtre a Qdrant per metadata `specialty`
- [ ] Configurar boost per documents de l'especialitat
- [ ] Integrar amb MedicalNER (detectar SPECIALTY)
- [ ] Tests amb queries d'especialitats diferents

**Dependències:** Task #30

---

#### Task #34: Dataset d'avaluació per informe d'alta
**Priority:** 🟠 High | **Estimació:** 1 dia | **Status:** 📋 Todo

**Descripció:**
Crear dataset de prova amb casos reals i ground truth.

**Tasques:**
- [ ] Crear 10-15 casos de prova amb:
  - Context del pacient
  - Diagnòstic esperat
  - Codis SNOMED/ICD-10 esperats
  - Medicacions esperades
- [ ] Definir mètriques d'avaluació:
  - Completesa (tots els camps presents)
  - Codis correctes (SNOMED/ICD-10 vàlids)
  - Adherència a protocol (segueix estructura)
  - Coherència clínica (manual review)
- [ ] Crear script d'avaluació automàtica
- [ ] Documentar casos i mètriques

**Dependències:** Task #30, Task #31

---

### 🎯 CAS D'ÚS 2: INFORME DE DERIVACIÓ

#### Task #35: Crear endpoint `/generate/referral`
**Priority:** 🟠 High | **Estimació:** 1.5 dies | **Status:** 📋 Todo

**Descripció:**
Endpoint per generar informes de derivació a especialista.

**Tasques:**
- [ ] Crear router `referral.py`
- [ ] Definir `ReferralRequest` amb:
  - `patient_context`: str
  - `referral_reason`: str (motiu derivació)
  - `target_specialty`: str (especialitat destí)
  - `clinical_history`: str (antecedents)
  - `language`: str = "es"
- [ ] Definir `ReferralResponse` amb:
  - `referral_document`: str
  - `reason_codes`: List[Dict] (codis SNOMED)
  - `target_specialty`: str (validat)
  - `urgency_level`: str
  - `sources`: List[Dict]
- [ ] Validar coherència motiu ↔ especialitat
- [ ] Tests amb 3 casos

**Dependències:** Task #36

---

#### Task #36: Crear prompt template per derivació
**Priority:** 🟠 High | **Estimació:** 0.5 dies | **Status:** 📋 Todo

**Descripció:**
Template per informe de derivació amb validació d'especialitat.

**Tasques:**
- [ ] Crear `prompts/referral_template.py`
- [ ] Estructura:
  ```
  1. DATOS DEL PACIENTE
  2. ESPECIALIDAD DESTINO
  3. MOTIVO DE DERIVACIÓN (con código SNOMED)
  4. ANTECEDENTES RELEVANTES
  5. EXPLORACIÓN FÍSICA
  6. PRUEBAS COMPLEMENTARIAS
  7. TRATAMIENTO ACTUAL
  8. NIVEL DE URGENCIA
  ```
- [ ] Validació especialitat destí coherent amb motiu
- [ ] Suport ca/es

**Dependències:** Cap

---

#### Task #37: Indexar protocols de derivació SAS
**Priority:** 🟠 High | **Estimació:** 0.5 dies | **Status:** 📋 Todo

**Descripció:**
Protocols específics per criteris de derivació.

**Tasques:**
- [ ] Buscar protocols de derivació SAS
- [ ] Indexar amb metadata `type: "referral_protocol"`
- [ ] Verificar retrieval

**Dependències:** Cap

---

#### Task #38: Dataset d'avaluació per derivació
**Priority:** 🟡 Medium | **Estimació:** 0.5 dies | **Status:** 📋 Todo

**Descripció:**
5-10 casos de prova per derivació.

**Tasques:**
- [ ] Crear casos amb diferents especialitats
- [ ] Definir ground truth
- [ ] Script d'avaluació

**Dependències:** Task #35

---

### 🎯 CAS D'ÚS 3: RESUM CLÍNIC PREVI A CONSULTA

#### Task #39: Crear endpoint `/generate/clinical-summary`
**Priority:** 🟡 Medium | **Estimació:** 1 dia | **Status:** 📋 Todo

**Descripció:**
Endpoint per generar resums clínics concisos.

**Tasques:**
- [ ] Crear router `clinical_summary.py`
- [ ] Definir `ClinicalSummaryRequest` amb:
  - `patient_history`: str
  - `consultation_reason`: str
  - `max_length`: int = 500
  - `language`: str = "es"
- [ ] Definir `ClinicalSummaryResponse` amb:
  - `summary`: str (concís)
  - `key_conditions`: List[Dict] (amb codis)
  - `current_medications`: List[Dict]
  - `alerts`: List[str] (al·lèrgies, contraindicacions)
  - `sources`: List[Dict]
- [ ] Tests amb 2 casos

**Dependències:** Task #40

---

#### Task #40: Crear prompt template per resum clínic
**Priority:** 🟡 Medium | **Estimació:** 0.5 dies | **Status:** 📋 Todo

**Descripció:**
Template per resum concís i accionable.

**Tasques:**
- [ ] Crear `prompts/clinical_summary_template.py`
- [ ] Estructura:
  ```
  1. ANTECEDENTES RELEVANTES (conciso)
  2. MEDICACIÓN ACTUAL
  3. ALERGIAS Y CONTRAINDICACIONES
  4. MOTIVO DE CONSULTA
  5. PUNTOS CLAVE PARA LA CONSULTA
  ```
- [ ] Límit de longitud configurable
- [ ] Priorització d'informació rellevant

**Dependències:** Cap

---

#### Task #41: Dataset d'avaluació per resum clínic
**Priority:** 🟡 Medium | **Estimació:** 0.5 dies | **Status:** 📋 Todo

**Descripció:**
5-10 casos de prova per resums.

**Tasques:**
- [ ] Crear casos amb diferents complexitats
- [ ] Definir ground truth
- [ ] Mètriques: concisió, completesa, rellevància

**Dependències:** Task #39

---

## 🔧 MILESTONE: v0.3 - Technical Improvements

### Task #42: Implementar reranking amb cross-encoder
**Priority:** 🟠 High | **Estimació:** 2 dies | **Status:** 📋 Todo

**Descripció:**
Reordenar documents recuperats per rellevància clínica.

**Tasques:**
- [ ] Seleccionar model cross-encoder (ms-marco-MiniLM o similar)
- [ ] Implementar `CrossEncoderReranker` class
- [ ] Integrar al pipeline després de retrieval
- [ ] Configurar top-k per reranking (ex: 20 → 5)
- [ ] Afegir scoring per citacions (PubMed)
- [ ] Boost per protocols oficials
- [ ] Tests de rendiment (latència <5s total)
- [ ] Comparar amb/sense reranking

**Dependències:** Cap

---

### Task #43: Implementar mètriques d'avaluació
**Priority:** 🟠 High | **Estimació:** 2 dies | **Status:** 📋 Todo

**Descripció:**
Sistema complet de mètriques per avaluar qualitat.

**Tasques:**
- [ ] Implementar BLEU score
- [ ] Implementar ROUGE score (ROUGE-1, ROUGE-L)
- [ ] Implementar BERTScore
- [ ] Mètriques de retrieval (Precision@k, Recall@k, MRR)
- [ ] Mètriques clíniques custom:
  - Completesa de camps obligatoris
  - Validesa de codis SNOMED/ICD-10
  - Adherència a protocols
- [ ] Dashboard per visualitzar mètriques
- [ ] Script d'avaluació batch

**Dependències:** Task #34, #38, #41

---

### Task #44: Optimitzar latència del pipeline
**Priority:** 🟡 Medium | **Estimació:** 2 dies | **Status:** 📋 Todo

**Descripció:**
Reduir temps de resposta a <5s per query.

**Tasques:**
- [ ] Profiling del pipeline complet
- [ ] Identificar bottlenecks
- [ ] Implementar batch processing per embeddings
- [ ] Cache de queries freqüents (Redis opcional)
- [ ] Optimitzar queries a Qdrant (HNSW params)
- [ ] Parallel processing on possible
- [ ] Documentar millores

**Dependències:** Task #42

---

### Task #45: Crear tests unitaris per casos d'ús
**Priority:** 🟠 High | **Estimació:** 2 dies | **Status:** 📋 Todo

**Descripció:**
Tests complets per endpoints de casos d'ús.

**Tasques:**
- [ ] Tests per `/generate/discharge-summary`
- [ ] Tests per `/generate/referral`
- [ ] Tests per `/generate/clinical-summary`
- [ ] Tests per prompts templates
- [ ] Tests per validació de codis
- [ ] Tests per filtratge semàntic
- [ ] Mocking de Ollama per tests ràpids
- [ ] Coverage >80%

**Dependències:** Task #30, #35, #39

---

### Task #46: Documentació completa de casos d'ús
**Priority:** 🟡 Medium | **Estimació:** 1 dia | **Status:** 📋 Todo

**Descripció:**
Documentar cada cas d'ús amb exemples.

**Tasques:**
- [ ] Crear `docs/USE_CASES.md`
- [ ] Documentar cada endpoint amb:
  - Descripció del cas d'ús
  - Request/Response examples
  - Exemples de cURL
  - Mètriques d'avaluació
  - Limitacions conegudes
- [ ] Crear col·lecció Postman/Insomnia
- [ ] Video demo (opcional)

**Dependències:** Task #30, #35, #39

---

## 📊 RESUM DE TASQUES

### Per Milestone

| Milestone | Total | Done | Todo | Estimació |
|-----------|-------|------|------|-----------|
| v0.1 - Infrastructure | 8 | 8 | 0 | - |
| v0.2 - Core Components | 7 | 7 | 0 | - |
| **v0.3 - Clinical Use Cases** | **17** | **0** | **17** | **19-22 dies** |
| v1.0 - Production Ready | 5 | 0 | 5 | 15-20 dies |
| v2.0 - Advanced Features | 3 | 0 | 3 | 15-19 dies |

### Per Cas d'Ús

| Cas d'Ús | Tasques | Estimació |
|----------|---------|-----------|
| 🔴 Informe d'Alta | 5 | 6 dies |
| 🟠 Informe de Derivació | 4 | 3 dies |
| 🟡 Resum Clínic | 3 | 2 dies |
| 🔧 Technical Improvements | 5 | 8-10 dies |

### Per Prioritat

| Prioritat | Nombre | Estimació |
|-----------|--------|-----------|
| 🔴 Critical | 3 | 4 dies |
| 🟠 High | 8 | 10-12 dies |
| 🟡 Medium | 6 | 5-6 dies |

---

## 🎯 SPRINTS RECOMANATS

### Sprint 1: Informe d'Alta (Setmana 1-2)
**Objectiu:** Cas d'ús 1 funcional end-to-end

**Tasques:**
1. Task #31: Prompt template (1 dia)
2. Task #32: Protocols SAS (1 dia)
3. Task #30: Endpoint discharge-summary (2 dies)
4. Task #33: Filtratge semàntic (1 dia)
5. Task #34: Dataset avaluació (1 dia)

**Deliverable:** Demo funcional d'informe d'alta amb validació

---

### Sprint 2: Derivació + Resum (Setmana 3)
**Objectiu:** Casos d'ús 2 i 3 funcionals

**Tasques:**
1. Task #36: Prompt derivació (0.5 dies)
2. Task #35: Endpoint referral (1.5 dies)
3. Task #37: Protocols derivació (0.5 dies)
4. Task #40: Prompt resum (0.5 dies)
5. Task #39: Endpoint clinical-summary (1 dia)
6. Task #38, #41: Datasets avaluació (1 dia)

**Deliverable:** 3 casos d'ús funcionals

---

### Sprint 3: Millores Tècniques (Setmana 4)
**Objectiu:** Optimització i avaluació

**Tasques:**
1. Task #42: Reranking (2 dies)
2. Task #43: Mètriques avaluació (2 dies)
3. Task #44: Optimitzar latència (2 dies)
4. Task #45: Tests unitaris (2 dies)

**Deliverable:** Sistema optimitzat amb mètriques

---

### Sprint 4: Documentació i Poliment (Setmana 5)
**Objectiu:** Preparar per presentació TFM

**Tasques:**
1. Task #46: Documentació completa (1 dia)
2. Crear presentació i demos
3. Preparar dataset d'avaluació final
4. Executar avaluació completa
5. Anàlisi de resultats

**Deliverable:** Sistema complet documentat i avaluat

---

## 📝 NOTES IMPORTANTS

### Desviació del Focus Original
- ❌ Estàvem implementant tecnologia sense casos d'ús concrets
- ✅ Ara enfocats en 3 casos d'ús clínics prioritaris
- ✅ Cada tasca està alineada amb necessitats reals del TFM

### Què Tenim Ja Implementat
- ✅ Query Expansion funcional (21 Abril)
- ✅ 529 documents indexats (ontologies + PubMed)
- ✅ Pipeline RAG base complet
- ✅ MedicalNER integrat

### Què Falta Críticament
- ❌ Prompts específics per casos d'ús
- ❌ Validació de codis SNOMED/ICD-10
- ❌ Protocols SAS indexats
- ❌ Datasets d'avaluació
- ❌ Mètriques d'avaluació

### Impacte Esperat
- **Informe d'Alta:** 19.300 informes/any al SAS, 10→6 min = 1.285h estalviades/any
- **Qualitat:** Adherència a protocols oficials, codificació correcta
- **Traçabilitat:** Fonts + codis ontològics en cada resposta

---

## 🚀 PRÒXIM PAS IMMEDIAT

**Començar AVUI amb Task #31 (Prompt template informe d'alta)**

Això ens permet:
1. Definir estructura exacta del document
2. Validar amb casos reals
3. Tenir base per implementar endpoint
4. Alinear amb requisits del TFM

**Temps estimat:** 4-6 hores  
**Bloqueig:** Cap

---

**Última actualització:** 21 d'Abril de 2026, 21:15h
