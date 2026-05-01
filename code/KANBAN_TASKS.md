# 📋 Healthcare RAG - Kanban & Roadmap

**Última actualització:** 1 de Maig de 2026  
**GitHub Project:** [healthcare-rag-slm](https://github.com/xaviermaltas/healthcare-rag-slm)  
**Principi:** El SLM genera text natural; les dades (codis, protocols) venen del pipeline RAG

---

## 📊 RESULTATS AVALUACIÓ

| Cas d'Ús | Overall | Completeness | SNOMED F1 | ICD-10 F1 | ATC F1 |
|----------|---------|--------------|-----------|-----------|--------|
| 1. Informe d'Alta | 51.3% | 97.2% | 29.2% | 37.5% | 55.0% |
| 2. Derivació | 73.0% | 100% | 0% | - | - |
| 3. Resum Clínic | ⏳ | - | - | - | - |

**Objectius:** Cas 1 ≥65% | Cas 2 ≥80% | Cas 3 ≥75% | SNOMED F1 ≥50%

---

## 🔄 IN PROGRESS

| # | Títol | Prioritat |
|---|-------|-----------|
| [#32](https://github.com/xaviermaltas/healthcare-rag-slm/issues/31) | Endpoint `/generate/referral` | HIGH |
| [#35](https://github.com/xaviermaltas/healthcare-rag-slm/issues/34) | Dataset d'avaluació per derivació | MODERATE |

---

## 📌 READY

| # | Títol | Prioritat |
|---|-------|-----------|
| [#12](https://github.com/xaviermaltas/healthcare-rag-slm/issues/12) | Medical NER | HIGH |
| [#14](https://github.com/xaviermaltas/healthcare-rag-slm/issues/14) | Tests unitaris | HIGH |
| [#15](https://github.com/xaviermaltas/healthcare-rag-slm/issues/15) | Tests d'integració | HIGH |

---

## 📋 BACKLOG

### HIGH
| # | Títol |
|---|-------|
| [#21](https://github.com/xaviermaltas/healthcare-rag-slm/issues/20) | Autenticació i autorització |
| [#22](https://github.com/xaviermaltas/healthcare-rag-slm/issues/21) | CI/CD pipeline |
| [#24](https://github.com/xaviermaltas/healthcare-rag-slm/issues/23) | Health checks complets |
| [#34](https://github.com/xaviermaltas/healthcare-rag-slm/issues/33) | Indexar protocols de derivació SAS |
| [#39](https://github.com/xaviermaltas/healthcare-rag-slm/issues/38) | Reranking amb cross-encoder |
| [#40](https://github.com/xaviermaltas/healthcare-rag-slm/issues/39) | Mètriques d'avaluació completes |
| [#42](https://github.com/xaviermaltas/healthcare-rag-slm/issues/41) | Tests unitaris per casos d'ús |

### MODERATE
| # | Títol |
|---|-------|
| [#16](https://github.com/xaviermaltas/healthcare-rag-slm/issues/17) | Optimitzar rendiment |
| [#17](https://github.com/xaviermaltas/healthcare-rag-slm/issues/18) | Logging estructurat |
| [#20](https://github.com/xaviermaltas/healthcare-rag-slm/issues/19) | Gestió d'errors |
| [#23](https://github.com/xaviermaltas/healthcare-rag-slm/issues/22) | Monitorització Prometheus |
| [#36](https://github.com/xaviermaltas/healthcare-rag-slm/issues/35) | Endpoint `/generate/clinical-summary` |
| [#37](https://github.com/xaviermaltas/healthcare-rag-slm/issues/36) | Prompt template per resum clínic |
| [#38](https://github.com/xaviermaltas/healthcare-rag-slm/issues/37) | Dataset d'avaluació per resum clínic |
| [#41](https://github.com/xaviermaltas/healthcare-rag-slm/issues/40) | Optimitzar latència del pipeline |
| [#43](https://github.com/xaviermaltas/healthcare-rag-slm/issues/42) | Documentació completa de casos d'ús |

### LOW
| # | Títol |
|---|-------|
| [#25](https://github.com/xaviermaltas/healthcare-rag-slm/issues/24) | Frontend web |
| [#26](https://github.com/xaviermaltas/healthcare-rag-slm/issues/25) | Sistema de feedback |
| [#27](https://github.com/xaviermaltas/healthcare-rag-slm/issues/26) | Multi-idioma |

---

## ✅ COMPLETED

| # | Títol | Prioritat |
|---|-------|-----------|
| [#13](https://github.com/xaviermaltas/healthcare-rag-slm/issues/13) | Implementar pipeline RAG complet | CRITICAL |
| [#28](https://github.com/xaviermaltas/healthcare-rag-slm/issues/27) | Endpoint `/generate/discharge-summary` | CRITICAL |
| [#11](https://github.com/xaviermaltas/healthcare-rag-slm/issues/11) | Reactivar sistema d'embeddings | CRITICAL |
| [#29](https://github.com/xaviermaltas/healthcare-rag-slm/issues/28) | Indexar protocols SAS per informes d'alta | CRITICAL |
| [#33](https://github.com/xaviermaltas/healthcare-rag-slm/issues/32) | Prompt template per derivació | HIGH |
| [#31](https://github.com/xaviermaltas/healthcare-rag-slm/issues/30) | Dataset d'avaluació per informe d'alta | HIGH |
| [#48](https://github.com/xaviermaltas/healthcare-rag-slm/issues/48) | Integració SNOMED CT per validació de codis | HIGH |
| [#30](https://github.com/xaviermaltas/healthcare-rag-slm/issues/29) | Filtratge semàntic per especialitat | HIGH |
| [#47](https://github.com/xaviermaltas/healthcare-rag-slm/issues/46) | Millorar extracció de diagnòstics i medicacions | HIGH |
| [#9](https://github.com/xaviermaltas/healthcare-rag-slm/issues/4) | Implementar connectors d'ingestion | HIGH |
| [#44](https://github.com/xaviermaltas/healthcare-rag-slm/issues/43) | Optimitzar rendiment per CPU | HIGH |
| [#19](https://github.com/xaviermaltas/healthcare-rag-slm/issues/16) | Documentació API | MODERATE |
| [#45](https://github.com/xaviermaltas/healthcare-rag-slm/issues/44) | Refactoritzar estructura de scripts | MODERATE |
| [#46](https://github.com/xaviermaltas/healthcare-rag-slm/issues/45) | Demo interactiva informe d'alta | MODERATE |
| [#1](https://github.com/xaviermaltas/healthcare-rag-slm/issues/1) | Refactoritzar estructura del projecte | LOW |
| [#2](https://github.com/xaviermaltas/healthcare-rag-slm/issues/6) | Configurar Docker Compose | LOW |
| [#3](https://github.com/xaviermaltas/healthcare-rag-slm/issues/2) | Implementar API FastAPI | LOW |
| [#4](https://github.com/xaviermaltas/healthcare-rag-slm/issues/7) | Implementar Ollama Client | LOW |
| [#10](https://github.com/xaviermaltas/healthcare-rag-slm/issues/5) | Implementar processadors de text | LOW |
| [#5](https://github.com/xaviermaltas/healthcare-rag-slm/issues/8) | Implementar Qdrant Client | LOW |
| [#6](https://github.com/xaviermaltas/healthcare-rag-slm/issues/9) | Crear scripts de gestió | LOW |
| [#7](https://github.com/xaviermaltas/healthcare-rag-slm/issues/10) | Documentar sistema complet | LOW |
| [#8](https://github.com/xaviermaltas/healthcare-rag-slm/issues/3) | Configurar sistema de configuració | LOW |

---

## 🗺️ ROADMAP DE MILLORES

### ⚠️ DECISIÓ ARQUITECTÒNICA CRÍTICA

**Problema identificat:** Diccionaris estàtics (558 termes) són un anti-pattern per RAG.

**Solució correcta:**
```
❌ INCORRECTE: 558 termes hardcoded en diccionaris Python
✅ CORRECTE: Ontologies completes indexades a Qdrant + Retrieval semàntic
```

**Nou enfocament:**
1. Indexar SNOMED CT complet (350K+ conceptes) a Qdrant
2. Indexar ICD-10 complet (70K+ codis) a Qdrant  
3. Indexar ATC complet (6K+ medicaments) a Qdrant
4. Retrieval semàntic per codificació
5. Diccionari mínim (30 termes ultra-comuns) com a fallback

---

### FASE 1: Ontologies i Codificació 🔴 ← PRIORITAT IMMEDIATA

| Tasca | Estat | Issues Relacionades |
|-------|-------|---------------------|
| ~~Ampliar diccionaris SNOMED/ICD-10/ATC~~ | ❌ CANCEL·LAT | Enfocament incorrecte |
| **Indexar SNOMED CT complet a Qdrant** | ⬜ | — |
| **Indexar ICD-10 complet a Qdrant** | ⬜ | — |
| **Indexar ATC complet a Qdrant** | ⬜ | — |
| **Implementar retrieval semàntic d'ontologies** | ⬜ | — |
| Crear diccionari mínim fallback (30 termes) | ⬜ | — |
| Refactoritzar pipeline codificació (SLM→NER→Retrieval→Codis) | ⬜ | — |

### FASE 2: Millorar Retrieval 🟠

| Tasca | Estat | Issues Relacionades |
|-------|-------|---------------------|
| Cross-Encoder Reranking | ⬜ | #39 |
| Query Expansion amb sinònims mèdics multilingüe | ⬜ | — |
| Millorar metadata documents Qdrant | ⬜ | — |
| Indexar corpus qualitat (NICE, WHO, PAPPS) | ⬜ | #34 |

### FASE 3: Re-avaluació 🔵

| Tasca | Estat | Issues Relacionades |
|-------|-------|---------------------|
| Re-avaluar Cas 1 (objectiu ≥65%) | ⬜ | #40 |
| Re-avaluar Cas 2 (objectiu ≥80%) | ⬜ | #40 |

### FASE 4: Cas d'Ús 3 - Resum Clínic 🟡

| Tasca | Estat | Issues Relacionades |
|-------|-------|---------------------|
| Endpoint `/generate/clinical-summary` | ⬜ | #36 |
| Prompt template resum clínic | ⬜ | #37 |
| Dataset avaluació (4-6 casos + gold standard) | ⬜ | #38 |
| Script avaluació i documentació | ⬜ | #43 |

### FASE 5: Testing 🔧

| Tasca | Estat | Issues Relacionades |
|-------|-------|---------------------|
| Tests unitaris per endpoints | ⬜ | #14, #42 |
| Tests d'integració | ⬜ | #15 |
| Tests codificació (SNOMED, ICD-10, ATC) | ⬜ | #42 |

### FASE 6: Documentació i TFM 📝

| Tasca | Estat | Issues Relacionades |
|-------|-------|---------------------|
| Documentació completa casos d'ús | ⬜ | #43 |
| Memòria TFM | ⬜ | — |

### FASE 7: Optimitzacions opcionals ⚪

| Tasca | Estat | Issues Relacionades |
|-------|-------|---------------------|
| Model SLM més gran (Llama3 8B / Mistral 7B) | ⬜ | — |
| SNOMED CT complet (PostgreSQL + fuzzy) | ⬜ | — |
| Optimitzar latència | ⬜ | #41 |
| CI/CD pipeline | ⬜ | #22 |

---

## 📅 ORDRE D'EXECUCIÓ

```
FASE 1 (Ontologies) ──→ FASE 3 (Re-avaluació) ──→ FASE 6 (Docs/TFM)
       ↕                        ↕
FASE 2 (Retrieval)  ──→ FASE 4 (Cas d'Ús 3)   ──→ FASE 5 (Tests)
```

---

**Última actualització:** 1 de Maig de 2026
