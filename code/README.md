# Healthcare RAG System — Codi Font

Implementació del sistema RAG sanitari. Per a una visió general del projecte, consultar el [README principal](../README.md).

---

## Arquitectura del Sistema

El sistema implementa un pipeline RAG de 3 fases:

```
┌──────────────────────────────────────────────────────────────────────┐
│                      HEALTHCARE RAG SYSTEM                            │
│                                                                        │
│  ┌───────────────┐   ┌───────────────────┐   ┌────────────────────┐  │
│  │   INGESTA &   │──▶│   RECUPERACIÓ     │──▶│   GENERACIÓ &      │  │
│  │   INDEXACIÓ   │   │   SEMÀNTICA       │   │   CODIFICACIÓ      │  │
│  │               │   │                   │   │                    │  │
│  │ • TextCleaner │   │ • BGE-M3 query    │   │ • Llama 3.2 (SLM) │  │
│  │ • MedChunker  │   │ • Qdrant search   │   │ • Prompts mèdics   │  │
│  │ • BGE-M3 emb  │   │ • Top-K retrieval │   │ • SNOMED CT/ICD-10 │  │
│  │ • Qdrant idx  │   │ • Reranking       │   │ • Human-in-the-loop│  │
│  └───────────────┘   └───────────────────┘   └────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

### Desplegament Híbrid

```
macOS / Linux
├── Ollama (natiu, LLM local — Llama 3.2)
└── Docker Compose
    ├── Qdrant (base de dades vectorial)
    └── API (FastAPI backend)
```

### Stack

| Component | Tecnologia |
|-----------|-----------|
| LLM | Llama 3.2 via Ollama |
| Embeddings | BGE-M3 (1024 dim) |
| Base vectorial | Qdrant |
| Backend | FastAPI (Python 3.11+) |
| Frontend | React + TypeScript + TailwindCSS |
| Ontologies | SNOMED CT, ICD-10, ATC via BioPortal |
| Desplegament | Docker Compose |

---

## Estructura del Codi

```
code/
├── src/main/
│   ├── api/                    # API REST (FastAPI)
│   │   ├── routes/             # Endpoints (generation, health, documents)
│   │   ├── dependencies.py     # Injecció de dependències
│   │   └── middleware.py       # CORS, logging
│   ├── core/                   # Lògica de negoci
│   │   ├── ingestion/          # Pipeline d'ingesta
│   │   │   ├── chunking/       # MedicalChunker (semàntic per seccions)
│   │   │   ├── processors/     # TextCleaner, parsers
│   │   │   └── indexer.py      # Indexació a Qdrant
│   │   ├── retrieval/          # Cerca semàntica i reranking
│   │   ├── coding/             # Codificació ontològica (SNOMED, ICD-10, ATC)
│   │   ├── generation/         # Generació de documents clínics
│   │   ├── prompts/            # Templates mèdics per cas d'ús
│   │   ├── parsers/            # Parsers de documents
│   │   └── utils/              # Utilitats comunes
│   ├── infrastructure/         # Clients externs
│   │   ├── llm/                # Client Ollama
│   │   ├── embeddings/         # Client BGE-M3
│   │   ├── vector_db/          # Client Qdrant
│   │   └── ontologies/         # Client BioPortal
│   ├── evaluation/             # Avaluació del sistema
│   └── main.py                 # Entry point FastAPI
├── src/test/                   # Tests unitaris i d'integració
├── frontend/                   # UI React + TailwindCSS + Vite
├── config/                     # Configuració centralitzada (settings.py)
├── deploy/                     # Docker Compose i Dockerfile
├── scripts/                    # Bootstrap, verificació, utilitats
├── docs/                       # Documentació tècnica
└── requirements.txt            # Dependències Python
```

---

## Requisits

- **SO**: macOS o Linux
- **RAM**: 16 GB mínim
- **Emmagatzematge**: 10 GB lliures
- **Docker**: [Docker Desktop](https://www.docker.com/products/docker-desktop/) o [OrbStack](https://orbstack.dev/)
- **Ollama**: [ollama.com/download](https://ollama.com/download)
- **Python**: 3.11+
- **Node.js**: 18+ (per al frontend)

---

## Instal·lació

### Automàtica (recomanat)

```bash
cd healthcare-rag-slm/code
cp .env.example .env            # Configurar BIOPORTAL_API_KEY
chmod +x scripts/bootstrap.sh
./scripts/bootstrap.sh
```

L'script automàticament:
- Comprova Python 3.11+ i Docker
- Crea l'entorn virtual `healthcare-rag-env`
- Instal·la dependències Python
- Instal·la Ollama i descarrega Llama 3.2
- Inicia Qdrant i API via Docker Compose

### Manual

```bash
# 1. Entorn Python
python3 -m venv healthcare-rag-env
source healthcare-rag-env/bin/activate
pip install -r requirements.txt

# 2. Ollama
brew install ollama
brew services start ollama
ollama pull llama3.2

# 3. Serveis
docker compose -f deploy/compose/docker-compose.yml up -d

# 4. Verificar
python3 scripts/verify_setup.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev       # http://localhost:5173
```

---

## Entorn Virtual

> ⚠️ Sempre usa el Python de l'entorn virtual, mai el del sistema.

```bash
# Activar
source healthcare-rag-env/bin/activate

# Executar tests
pytest src/test/ -v

# O sense activar el venv
./scripts/activate_and_run.sh pytest src/test/ -v
```

### Configurar IDE (Windsurf / VS Code)

1. `Cmd+Shift+P` → **Python: Select Interpreter**
2. **Enter interpreter path...**
3. Ruta: `<projecte>/healthcare-rag-slm/code/healthcare-rag-env/bin/python3`

---

## Configuració (.env)

```bash
# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=healthcare_rag

# Embeddings
EMBEDDING_MODEL=BAAI/bge-m3
EMBEDDING_DEVICE=cpu

# BioPortal (obligatori per ontologies)
BIOPORTAL_API_KEY=your_api_key_here

# Idioma per defecte
DEFAULT_LANGUAGE=es
```

**Obtenir API keys:**
- BioPortal: https://bioportal.bioontology.org/account

---

## Serveis

| Servei | URL |
|--------|-----|
| API Healthcare RAG | http://localhost:8000 |
| Swagger UI (docs) | http://localhost:8000/docs |
| Frontend | http://localhost:5173 |
| Qdrant Dashboard | http://localhost:6333/dashboard |
| Ollama | http://localhost:11434 |

### Gestió de serveis

```bash
# Iniciar
docker compose -f deploy/compose/docker-compose.yml up -d

# Logs
docker compose -f deploy/compose/docker-compose.yml logs -f

# Aturar
docker compose -f deploy/compose/docker-compose.yml down
```

---

## Troubleshooting

### Ollama no respon
```bash
brew services restart ollama
ollama list                    # Verificar que llama3.2 està descarregat
```

### Qdrant no connecta
```bash
docker compose -f deploy/compose/docker-compose.yml restart qdrant
curl http://localhost:6333/healthz
```

### Problemes de memòria
- Reduir `EMBEDDING_BATCH_SIZE` a `.env`
- Verificar que no hi ha altres processos consumint RAM

---

## Documentació Addicional

| Document | Descripció |
|----------|------------|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Arquitectura completa del sistema |
| [`docs/SETUP.md`](docs/SETUP.md) | Guia de setup detallada |
| [`docs/DEMO.md`](docs/DEMO.md) | Guia de demostració |
| [`docs/LLM_MODEL_SELECTION.md`](docs/LLM_MODEL_SELECTION.md) | Comparativa de models LLM |
| [`docs/SNOMED_CT_INTEGRATION.md`](docs/SNOMED_CT_INTEGRATION.md) | Integració SNOMED CT |
| [`frontend/README.md`](frontend/README.md) | Documentació del frontend |

---

> ⚠️ Sistema d'assistència orientativa. No substitueix el criteri mèdic professional.
