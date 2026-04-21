# Healthcare RAG System - Arquitectura Tècnica

## Visió General del Sistema

El Healthcare RAG System implementa una arquitectura de 3 blocs principals per proporcionar capacitats de generació augmentada per recuperació especialitzada en el domini mèdic.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           HEALTHCARE RAG SYSTEM                                 │
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────────┐    ┌─────────────────────────┐ │
│  │    BLOCK 1      │───▶│       BLOCK 2       │───▶│        BLOCK 3          │ │
│  │   INGESTION     │    │     INDEXING        │    │   RETRIEVAL &           │ │
│  │                 │    │                     │    │   GENERATION            │ │
│  │ • Connectors    │    │ • Vector Index      │    │ • Query Processing      │ │
│  │ • Processors    │    │ • Lexical Index     │    │ • Hybrid Retrieval      │ │
│  │ • Chunking      │    │ • Ontological Index │    │ • RRF Fusion            │ │
│  │ • Enrichment    │    │ • Embeddings        │    │ • Reranking             │ │
│  └─────────────────┘    └─────────────────────┘    └─────────────────────────┘ │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                            API LAYER                                        │ │
│  │  FastAPI + Pydantic + Async + Health Checks + Documentation                │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Arquitectura d'Infraestructura

### Arquitectura Híbrida macOS + Docker

```
macOS M1/M2 Host
├── Ollama (NATIU)
│   ├── Mistral 7B
│   ├── Llama 3.2
│   └── Metal GPU Acceleration
│
└── Docker Compose
    ├── Qdrant Container
    │   ├── Vector Database
    │   ├── Collections Management
    │   └── Persistent Storage
    │
    └── API Container
        ├── FastAPI Application
        ├── Python Dependencies
        └── Health Monitoring
```

## Estructura de Directoris

```
healthcare-rag-slm/code/
├── src/main/                     # Codi principal de l'aplicació
│   ├── api/                      # Capa de presentació (FastAPI)
│   │   ├── routes/              # Endpoints REST
│   │   ├── dependencies.py      # Singleton instances
│   │   └── middleware.py        # Logging, CORS, error handling
│   │
│   ├── core/                     # Lògica de negoci (RAG Pipeline)
│   │   ├── ingestion/           # Ingesta de documents
│   │   │   ├── connectors/      # Connectors per descarregar dades externes
│   │   │   │   ├── base_connector.py       # Interface base
│   │   │   │   ├── bioportal_connector.py  # BioPortal (SNOMED/MeSH/ICD)
│   │   │   │   └── pubmed_connector.py     # PubMed articles
│   │   │   ├── chunking/        # Fragmentació de documents
│   │   │   └── document_processor.py  # Orquestrador ingesta
│   │   │
│   │   └── retrieval/           # Recuperació de documents
│   │       ├── query_processing/  # NER mèdic, query expansion
│   │       ├── semantic_annotation.py  # Mapatge text → codis
│   │       ├── retriever.py     # Vector search + filtratge
│   │       └── reranker.py      # Reordenació per rellevància
│   │
│   └── infrastructure/           # Clients per serveis externs
│       ├── llm/                 # Clients LLM
│       │   └── ollama_client.py
│       ├── vector_db/           # Clients Vector DB
│       │   └── qdrant_client.py
│       ├── embeddings/          # Models d'embeddings
│       │   └── bge_m3.py
│       └── ontologies/          # Clients ontologies
│           ├── snomed_client.py      # Client SNOMED CT (runtime)
│           └── ontology_manager.py   # Manager unificat (runtime)
│
├── config/                      # Configuració centralitzada
│   ├── settings.py             # Settings amb Pydantic
│   └── prompts/                # Templates LLM
│
├── scripts/                     # Scripts d'utilitat
│   ├── start.sh                # Aixecar sistema
│   ├── stop.sh                 # Parar sistema
│   └── ingest_medical_knowledge.py  # Ingesta ontologies + PubMed
│
├── data/                        # Dades del sistema
│   ├── raw/                    # Documents originals
│   ├── processed/              # Documents processats
│   └── embeddings/             # Cache embeddings
│
├── docs/                        # Documentació unificada
│   ├── ARCHITECTURE.md         # Arquitectura completa
│   ├── SETUP.md                # Setup complet (API keys, ontologies)
│   └── DEMO.md                 # Guia demostració
│
├── deploy/                      # Desplegament
│   └── compose/
│       ├── docker-compose.yml
│       └── Dockerfile
│
└── tests/                       # Tests
    ├── unit/
    └── integration/
```

## Bloc 1: Ingestion Module

### Propòsit
Ingesta, processament i preparació de documents mèdics de múltiples fonts per a la seva indexació posterior.

### Components

#### 1.1 Connectors (`core/ingestion/connectors/`)

**Arquitectura de Connectors Unificats**

Tots els connectors segueixen el **patró Strategy** amb una interface comuna:

**BaseConnector** (`base_connector.py`)
- Classe abstracta que defineix la interfície comuna
- Mètodes obligatoris:
  - `connect()` → Establir connexió amb API/servei
  - `fetch_documents()` → Descarregar documents per indexar
  - `disconnect()` → Tancar connexió
- Gestió d'errors i logging unificat
- Rate limiting automàtic

**BioPortalConnector** (`bioportal_connector.py`)
- **Propòsit:** Descarregar conceptes d'ontologies per indexar offline
- **APIs suportades:** SNOMED CT, MeSH, ICD-10-CM
- **Funcionalitats:**
  - Cerca de conceptes per query
  - Descàrrega de jerarquies (parents/children)
  - Extracció de sinònims i definicions
  - Batch processing per optimització
- **Ús:** Scripts d'ingesta (`scripts/ingest_medical_knowledge.py`)

**PubMedConnector** (`pubmed_connector.py`)
- **Propòsit:** Descarregar articles científics per indexar
- **APIs utilitzades:** NCBI E-utilities (esearch, efetch, elink)
- **Funcionalitats:**
  - Cerca d'articles per query
  - Filtratge per citacions (>50 cites = altament citat)
  - Filtratge per data (recents <2 anys, clàssics >10 anys)
  - Extracció completa (títol, abstract, autors, MeSH terms, DOI)
  - Comptatge automàtic de citacions
- **Estratègia:** 50% articles clàssics + 50% articles recents
- **Rate limiting:** 3 req/s (sense API key), 10 req/s (amb API key)
- **Ús:** Scripts d'ingesta

**Diferència amb `infrastructure/ontologies/`:**
- `connectors/` → Descàrrega massiva per **indexar offline**
- `infrastructure/ontologies/` → Consultes **runtime** durant queries

#### 1.2 Processors (`ingestion/processors/`)

**TextCleaner** (`text_cleaner.py`)
- Normalització de text mèdic
- Correcció d'errors d'encoding
- Preservació de terminologia mèdica
- Neteja d'headers/footers
- Funcions principals:
  - `clean_text()`: Neteja principal
  - `extract_medical_entities()`: Extracció d'entitats
  - `split_sentences()`: Segmentació respectant abreviatures mèdiques

#### 1.3 Chunking (`ingestion/chunking/`)

**MedicalChunker** (`medical_chunker.py`)
- Chunking semàntic especialitzat per documents mèdics
- Respecta fronteres semàntiques (seccions, paràgrafs)
- Gestió d'overlap intel·ligent
- Tipus de chunks:
  - Seccions de documents (Introducció, Metodologia, etc.)
  - Grups de paràgrafs relacionats
  - Splits de chunks grans amb overlap
- Configuració: `chunk_size=512`, `chunk_overlap=50`

## Bloc 2: Indexing Module

### Propòsit
Creació d'índexs híbrids (vectorial, lexical, ontològic) per permetre recuperació multimodal de documents mèdics.

### Components

#### 2.1 Embeddings (`indexing/embeddings/`)

**BGEM3Embeddings** (`bge_m3.py`)
- Model d'embeddings multilingüe BAAI/bge-m3
- Suport per català, espanyol i anglès
- Dimensions: 1024
- Funcionalitats:
  - `encode_texts()`: Codificació de textos en lots
  - `encode_query()`: Codificació de queries
  - `encode_documents()`: Codificació per indexació
- Cache persistent per optimitzar rendiment
- Suport per GPU (Metal) i CPU

#### 2.2 Vector Index (`indexing/vectorial/`)

**HealthcareQdrantClient** (`qdrant_client.py`)
- Client especialitzat per Qdrant
- Gestió de col·leccions mèdiques
- Configuració optimitzada per documents mèdics:
  - Distance: Cosine similarity
  - HNSW parameters optimitzats
  - Segments configuration per rendiment
- Funcionalitats:
  - `add_documents()`: Afegir documents amb vectors
  - `search_similar()`: Cerca per similitud vectorial
  - `search_by_text_filter()`: Cerca amb filtres
  - Health checks i monitorització

#### 2.3 Lexical Index (`indexing/lexical/`)
- Implementació BM25 per cerca lexical
- Tokenització específica per terminologia mèdica
- Expansió de queries amb sinònims mèdics

#### 2.4 Ontological Index (`indexing/ontological/`)
- Integració amb ontologies mèdiques (SNOMED-CT, ICD)
- Mapejat de conceptes mèdics
- Expansió semàntica de queries

## Bloc 3: Retrieval & Generation

### Propòsit
Processament de queries, recuperació híbrida de documents rellevants i generació de respostes contextuals.

### Components

#### 3.1 Query Processing (`retrieval/query_processing/`)

**MedicalNER** (`medical_ner.py`)
- Reconeixement d'entitats mèdiques en espanyol i català
- Diccionaris especialitzats:
  - Malalties: diabetes, hipertensió, càncer, etc.
  - Símptomes: dolor, febre, tos, etc.
  - Medicaments: paracetamol, ibuprofeno, etc.
  - Anatomia: cor, pulmó, fetge, etc.
  - Procediments: cirurgia, biopsia, etc.
- Patrons regex per:
  - Codis mèdics (ICD, SNOMED)
  - Dosis i medicació
  - Signes vitals
- Expansió de termes amb sinònims

#### 3.2 Hybrid Retrieval (`retrieval/retrievers/`)
- Combinació de cerca vectorial, lexical i ontològica
- Estratègies de recuperació adaptatives
- Filtres per font, idioma i tipus de document

#### 3.3 RRF Fusion (`retrieval/fusion/`)
- Reciprocal Rank Fusion per combinar resultats
- Normalització de scores entre diferents índexs
- Configuració de pesos per tipus de cerca

#### 3.4 Reranking (`retrieval/reranking/`)
- Reordenació semàntica amb cross-encoders
- Millora de la rellevància dels resultats
- Optimització per queries mèdiques

## Generation Module

### Propòsit
Generació de respostes contextuals utilitzant models de llenguatge especialitzats i templates mèdics.

### Components

#### Models (`generation/models/`)

**OllamaClient** (`ollama_client.py`)
- Client async per Ollama
- Suport per múltiples models (Mistral, Llama)
- Funcionalitats:
  - `generate()`: Generació de text
  - `chat()`: Mode conversacional
  - `generate_medical_response()`: Generació amb context mèdic
- Gestió de models:
  - `pull_model()`: Descàrrega de models
  - `delete_model()`: Eliminació de models
  - `get_available_models()`: Llistat de models

#### Prompts (`generation/prompts/`)
- Templates especialitzats per dominio mèdic
- Prompts multilingües (espanyol, català, anglès)
- Instruccions específiques per professionals sanitaris
- Context safety per evitar diagnòstics definitius

#### Context Management (`generation/context/`)
- Gestió de context RAG
- Formatació de documents recuperats
- Limitació de longitud de context
- Preservació de fonts i metadades

## API Layer

### Propòsit
Interfície REST per accedir a totes les funcionalitats del sistema RAG.

### Estructura

#### Main Application (`api/main.py`)
- Aplicació FastAPI principal
- Gestió del cicle de vida de l'aplicació
- Middleware de CORS i logging
- Exception handlers personalitzats

#### Routes (`api/routes/`)

**Health** (`health.py`)
- Endpoints de monitorització del sistema
- Health checks per components individuals
- Readiness i liveness checks per Kubernetes

**Query** (`query.py`)
- Endpoint principal RAG: `POST /query/`
- Extracció d'entitats: `POST /query/entities`
- Recuperació sense generació: `POST /query/retrieve`
- Suport multilingüe i configuració flexible

**Documents** (`documents.py`)
- Upload de documents: `POST /documents/upload`
- Gestió de documents: `GET /documents/`, `DELETE /documents/{id}`
- Processament en background
- Suport per PDF i text pla

**Collections** (`collections.py`)
- Informació de col·leccions: `GET /collections/`
- Estadístiques: `GET /collections/stats`
- Neteja: `DELETE /collections/clear`

**Models** (`models.py`)
- Gestió de models Ollama
- Informació d'embeddings
- Cache management

**Admin** (`admin.py`)
- Endpoints d'administració
- Inicialització del sistema
- Operacions de manteniment

#### Dependencies (`api/dependencies.py`)
- Instàncies compartides de components
- Gestió del cicle de vida
- Cleanup automàtic

#### Middleware (`api/middleware.py`)
- Logging de requests/responses
- Request ID tracking
- Mesura de temps de processament

## Configuració del Sistema

### Settings (`config/settings.py`)
Configuració centralitzada amb Pydantic BaseSettings:

```python
# Configuració d'aplicació
APP_NAME: str = "Healthcare RAG System"
APP_VERSION: str = "1.0.0"
DEBUG: bool = True

# Configuració API
API_HOST: str = "0.0.0.0"
API_PORT: int = 8000

# Configuració Ollama
OLLAMA_BASE_URL: str = "http://localhost:11434"
OLLAMA_MODEL: str = "mistral"

# Configuració Qdrant
QDRANT_HOST: str = "localhost"
QDRANT_PORT: int = 6333
QDRANT_COLLECTION: str = "healthcare_rag"

# Configuració Embeddings
EMBEDDING_MODEL: str = "BAAI/bge-m3"
EMBEDDING_DEVICE: str = "cpu"
EMBEDDING_BATCH_SIZE: int = 32

# Configuració APIs externes
BIOPORTER_API_KEY: str = ""
MEDLINEPLUS_BASE_URL: str = "https://wsearch.nlm.nih.gov/ws/query"

# Configuració Chunking
CHUNK_SIZE: int = 512
CHUNK_OVERLAP: int = 50

# Configuració Retrieval
RETRIEVAL_TOP_K: int = 10
RERANK_TOP_K: int = 5
```

## Flux de Dades

### 1. Ingesta de Documents
```
Document → Connector → TextCleaner → MedicalChunker → Chunks
```

### 2. Indexació
```
Chunks → BGE-M3 → Embeddings → Qdrant → Vector Index
       → BM25 → Lexical Index
       → Ontologies → Ontological Index
```

### 3. Query Processing
```
Query → MedicalNER → Entities → Query Expansion → Enhanced Query
```

### 4. Retrieval
```
Enhanced Query → Vector Search → Results₁
               → Lexical Search → Results₂  → RRF Fusion → Reranking → Final Results
               → Ontological Search → Results₃
```

### 5. Generation
```
Final Results → Context Building → Medical Template → Ollama → Response
```

## Optimitzacions i Rendiment

### Caching
- **Embeddings Cache**: Cache persistent per evitar recalcular embeddings
- **Model Cache**: Models Ollama carregats en memòria
- **Query Cache**: Cache de queries freqüents

### Async Processing
- Tots els components utilitzen async/await
- Processament en background per uploads
- Concurrent requests handling

### Memory Management
- Batch processing per embeddings
- Streaming responses per generació
- Cleanup automàtic de recursos

### Monitoring
- Health checks automàtics
- Mètriques de rendiment
- Logging estructurat
- Request tracking

## Escalabilitat

### Horizontal Scaling
- API stateless per múltiples instàncies
- Qdrant clustering support
- Load balancing ready

### Vertical Scaling
- GPU acceleration per embeddings
- Configurable batch sizes
- Memory-efficient processing

### Storage Scaling
- Persistent volumes per Qdrant
- Configurable storage backends
- Data retention policies
