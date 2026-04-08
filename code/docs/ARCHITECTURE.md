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
├── config/                    # Configuració centralitzada (settings, ontologies)
├── ingestion/                 # Bloc 1: Ingesta intel·ligent
│   ├── connectors/           # Connectors fonts de dades (MedlinePlus, BioPortal, PDFs)
│   ├── processors/           # Processadors de text mèdic
│   ├── chunking/            # Chunking semàntic especialitzat
│   └── enrichment/          # Enriqueciment ontològic
├── indexing/                 # Bloc 2: Indexació híbrida
│   ├── embeddings/          # Models d'embeddings (BGE-M3)
│   ├── vectorial/           # Índex vectorial (Qdrant)
│   ├── lexical/            # Índex lexical (BM25)
│   └── ontological/        # Índex ontològic (SNOMED-CT)
├── retrieval/               # Bloc 3: Recuperació avançada
│   ├── query_processing/   # NER mèdic i processament queries
│   ├── retrievers/         # Recuperadors híbrids
│   ├── fusion/            # Fusió RRF de resultats
│   └── reranking/         # Reranking semàntic
├── generation/             # Generació amb SLM
│   ├── models/            # Client Ollama
│   ├── prompts/          # Templates mèdics multilingües
│   └── context/          # Gestió de context RAG
├── api/                   # API REST FastAPI
│   ├── routes/           # Endpoints (health, query, documents, etc.)
│   └── models/          # Models Pydantic
├── scripts/              # Scripts d'utilitat (setup, verificació)
├── data/                # Dades del sistema (raw, processed, cache)
├── docs/               # Documentació tècnica
├── tests/              # Tests unitaris i d'integració
└── [fitxers configuració]  # .env, docker-compose.yml, requirements.txt
```

## Bloc 1: Ingestion Module

### Propòsit
Ingesta, processament i preparació de documents mèdics de múltiples fonts per a la seva indexació posterior.

### Components

#### 1.1 Connectors (`ingestion/connectors/`)

**BaseConnector** (`base_connector.py`)
- Classe abstracta que defineix la interfície comuna per tots els connectors
- Mètodes: `connect()`, `fetch_documents()`, `disconnect()`
- Gestió d'errors i logging unificat

**MedlinePlusConnector** (`medlineplus.py`)
- Connector per a l'API de MedlinePlus
- Cerca d'articles mèdics en anglès i espanyol
- Processament de metadades mèdiques
- Rate limiting i gestió d'errors HTTP

**BioPortalConnector** (`bioporter.py`)
- Connector per a ontologies biomèdiques
- Accés a SNOMED-CT, ICD-10, ICD-11
- Expansió de termes mèdics
- Mapejat de codis mèdics

**PDFConnector** (`pdf_connector.py`)
- Processament de PDFs mèdics
- Extracció de text amb PyPDF2
- Detecció d'idioma (espanyol/català)
- Preservació de metadades del document

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
