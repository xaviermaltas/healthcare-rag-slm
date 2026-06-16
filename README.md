# Healthcare RAG-SLM: Assistència a la Documentació Clínica mitjançant RAG, Ontologies i Models de Llenguatge Petits

> **Treball Final de Màster** — Ciència de Dades (UOC)  
> **Autor:** Xavier Maltas Tarridas  
> **Director:** Carlos Luis Sánchez Bocanegra  
> **Data:** Juny 2026

---

## Resum

Aquest projecte implementa un sistema d'assistència a la documentació clínica que combina **Retrieval-Augmented Generation (RAG)**, **ontologies mèdiques estàndard** (SNOMED CT, ICD-10, ATC) i un **model de llenguatge petit (SLM)** executat localment. L'objectiu és reduir la càrrega burocràtica dels professionals sanitaris — que dediquen el **49,2% del seu temps** a tasques administratives — mitjançant la generació assistida d'informes clínics basats en protocols oficials.

El sistema opera sota un paradigma **human-in-the-loop**: genera esborranys de documents clínics que el professional sempre revisa i valida abans de la seva incorporació a la història clínica, garantint la seguretat del pacient.

### Característiques Clau

- **100% on-premise**: Totes les dades romanen al servidor local. Compliment RGPD.
- **CPU-only**: Funciona en hardware estàndard (16GB RAM, sense GPU).
- **Open-source**: Zero costos de llicències (Llama 3.2, Qdrant, FastAPI, React).
- **Multilingüe**: Suport per català, castellà i anglès.
- **Integració ontològica**: Codificació automàtica amb SNOMED CT, ICD-10 i ATC.

---

## Casos d'Ús

| Cas d'ús | Descripció |
|----------|------------|
| **Informe d'alta hospitalària** | Procés assistencial, diagnòstics codificats i recomanacions de seguiment |
| **Informe de derivació** | Derivació a especialista amb motiu clínic i antecedents |
| **Resum clínic previ a consulta** | Síntesi de la informació clínica rellevant del pacient |

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────┐
│                     HEALTHCARE RAG SYSTEM                            │
│                                                                      │
│  ┌──────────────┐   ┌──────────────────┐   ┌────────────────────┐  │
│  │  INGESTA &   │──▶│   RECUPERACIÓ    │──▶│   GENERACIÓ &      │  │
│  │  INDEXACIÓ   │   │   SEMÀNTICA      │   │   CODIFICACIÓ      │  │
│  │              │   │                  │   │                    │  │
│  │ • TextCleaner│   │ • BGE-M3 query   │   │ • Llama 3.2 (SLM) │  │
│  │ • MedChunker │   │ • Qdrant search  │   │ • Prompts mèdics   │  │
│  │ • BGE-M3 emb │   │ • Top-K retrieval│   │ • SNOMED CT/ICD-10 │  │
│  │ • Qdrant     │   │                  │   │ • Human-in-the-loop│  │
│  └──────────────┘   └──────────────────┘   └────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Stack Tecnològic

| Component | Tecnologia | Funció |
|-----------|-----------|--------|
| LLM | Llama 3.2 (2GB) via Ollama | Generació de text clínic |
| Embeddings | BGE-M3 (1024 dim) | Representació semàntica multilingüe |
| Base vectorial | Qdrant | Emmagatzematge i cerca de vectors |
| Backend | FastAPI (Python) | API REST |
| Frontend | React + TailwindCSS | Interfície d'usuari |
| Ontologies | SNOMED CT, ICD-10, ATC | Codificació mèdica estàndard |
| Desplegament | Docker Compose | Orquestració de serveis |

---

## Resultats

### Mètriques Principals

| Mètrica | Valor |
|---------|-------|
| Overall Score — Derivació | **73%** |
| Overall Score — Resum Clínic | **58-71%** |
| Overall Score — Alta Hospitalària | **51,3%** |
| F1 Ontològic (català) | 29-37% |
| Precisió diagnòstica | 100% (0% al·lucinacions) |
| Latència mitjana | 16,69s |
| RAM consumida | ~4,5 GB |
| Mida del model | 2,0 GB |

- ✅ CPU-only, sense GPU (latència 16,69s, RAM ~4,5GB, model 2GB)
- ✅ Zero al·lucinacions diagnòstiques en les proves
- ✅ 100% local, sense dependències cloud

### Limitacions

- F1 ontològic baix en català (cobertura limitada de les ontologies en llengües minoritàries)
- Avaluació amb gold standards sintètics (no dades reals d'hospitals)
- No valida interaccions farmacològiques ni contraindicacions

---

## Estructura del Repositori

```
healthcare-rag-slm/
├── code/                    # Implementació del sistema
│   ├── src/main/           # Codi font principal
│   │   ├── api/            # API REST (FastAPI)
│   │   ├── core/           # Lògica de negoci
│   │   │   ├── ingestion/  # Pipeline d'ingesta i chunking
│   │   │   ├── retrieval/  # Cerca semàntica i reranking
│   │   │   ├── coding/     # Codificació ontològica
│   │   │   └── parsers/    # Parsers de documents
│   │   └── infrastructure/ # Clients externs (Ollama, Qdrant)
│   ├── src/test/           # Tests unitaris i d'integració
│   ├── frontend/           # UI React + TailwindCSS
│   ├── config/             # Configuració centralitzada
│   ├── data/               # Dades i gold standards
│   ├── deploy/             # Docker Compose
│   └── docs/               # Documentació tècnica
├── memoria/                # Memòria acadèmica del TFM (LaTeX)
└── presentacio/            # Materials de presentació i defensa
```

---

## Instal·lació

**Requisits:** macOS/Linux, 16GB RAM, Docker, Ollama, Python 3.11+

```bash
git clone https://github.com/xaviermaltas/healthcare-rag-slm.git
cd healthcare-rag-slm/code
cp .env.example .env          # Configurar BIOPORTAL_API_KEY
./scripts/bootstrap.sh         # Instal·lació automàtica
```

> Instruccions detallades a [`code/README.md`](code/README.md)

---

## Treball Futur

- Validació clínica amb professionals sanitaris i dades reals
- Ampliació del corpus de protocols (totes les especialitats)
- Embeddings clínics específics per millorar cobertura en català
- Detecció d'interaccions farmacològiques

---

## Documents

- 📄 **Memòria**: [`memoria/TFM.tex`](memoria/TFM.tex)
- 📊 **Presentació**: [`presentacio/TFM_slides.pdf`](presentacio/TFM_slides.pdf)

---

## Llicència

Projecte desenvolupat com a Treball Final de Màster en Ciència de Dades (UOC). Codi open-source.

---

> **⚠️ Nota Important**: Aquest sistema està dissenyat per assistir professionals sanitaris amb informació orientativa. No substitueix el criteri mèdic professional. Tot document generat requereix validació per part d'un professional sanitari qualificat.