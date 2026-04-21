# Healthcare RAG System

Sistema de Generació Augmentada per Recuperació (RAG) especialitzat per al sector sanitari, desenvolupat com a projecte final de màster en Ciència de Dades.

## Arquitectura del Sistema

El sistema implementa una arquitectura híbrida de 3 blocs principals:

```
┌─────────────────────────────────────────────────────────────────┐
│                    HEALTHCARE RAG SYSTEM                        │
│                                                                  │
│  ┌──────────┐    ┌──────────────────┐    ┌──────────────────┐  │
│  │  BLOC 1  │───▶│     BLOC 2       │───▶│     BLOC 3       │  │
│  │ INGESTION│    │    INDEXING      │    │   RETRIEVAL &    │  │
│  │          │    │                  │    │   GENERATION     │  │
│  └──────────┘    └──────────────────┘    └──────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Arquitectura Híbrida

```
macOS M1/M2
├── Ollama NATIU (aprofita Metal GPU)
└── Docker Compose
    ├── Qdrant (Base de dades vectorial)
    └── API (FastAPI)
```

## Característiques Principals

- **Ontologies Mèdiques**: Integració SNOMED CT, MeSH, ICD-10 via BioPortal API
- **PubMed Integration**: Articles científics amb filtratge per citacions i data
- **Ingesta Intel·ligent**: Connectors unificats per ontologies i literatura mèdica
- **Indexació Híbrida**: Cerca vectorial (BGE-M3 1024-dim) amb Qdrant
- **Medical NER**: Extracció d'entitats mèdiques (DISEASE, MEDICATION, SYMPTOM, etc.)
- **Generació Contextual**: LLM local (Mistral) amb templates mèdics
- **Multiidioma**: Suport espanyol, català i anglès
- **API RESTful**: Endpoints complets amb documentació OpenAPI

## Requisits del Sistema

- **SO**: macOS (recomanat M1/M2 per Metal GPU) o Linux
- **RAM**: Mínim 16GB
- **Emmagatzematge**: 10GB lliures
- **Docker**: Instal·lat i funcionant ([Docker Desktop](https://www.docker.com/products/docker-desktop/) o [OrbStack](https://orbstack.dev/))
- **Ollama**: [ollama.com/download](https://ollama.com/download)
- **Python**: 3.11+

## Instal·lació

### 1. Clonar el Repositori

```bash
git clone <repository-url>
cd healthcare-rag-slm/code
```

### 2. Configurar Variables d'Entorn

```bash
cp .env.example .env
# Edita .env i afegeix les API keys necessàries:
# - BIOPORTAL_API_KEY (obligatori per ontologies)
# - NCBI_API_KEY (opcional per PubMed)
```

**Obtenir API keys:**
- BioPortal: https://bioportal.bioontology.org/account
- NCBI: https://www.ncbi.nlm.nih.gov/account/settings/

### 3. Instal·lació Automàtica (recomanat)

```bash
chmod +x scripts/bootstrap.sh
./scripts/bootstrap.sh
```

L'script automàticament:
- ✅ Comprova Python 3.11+ i Docker
- ✅ Crea l'entorn virtual `healthcare-rag-env`
- ✅ Instal·la totes les dependències Python
- ✅ Instal·la Ollama i descarrega els models LLM
- ✅ Inicia Qdrant i API via Docker Compose
- ✅ Verifica la instal·lació completa

### 4. Verificar Instal·lació

```bash
python3 scripts/verify_setup.py
```

## Entorn Virtual i Intèrpret Python

> ⚠️ **Important**: Sempre usa el Python de l'entorn virtual, mai el del sistema.

El `bootstrap.sh` crea automàticament `healthcare-rag-env/`. L'intèrpret a usar és:

```
healthcare-rag-env/bin/python3
```

### Executar tests o scripts

```bash
# Amb l'script d'execució directa (recomanat, no cal activar el venv)
./scripts/activate_and_run.sh pytest src/test/ -v
./scripts/activate_and_run.sh python3 src/test/unit/core/test_core_components.py

# O activant el venv manualment
source healthcare-rag-env/bin/activate
pytest src/test/ -v
```

### Configurar IDE (Windsurf / VS Code)

Selecciona l'intèrpret del venv manualment:

1. `Cmd+Shift+P` → **Python: Select Interpreter**
2. Clica **"Enter interpreter path..."**
3. Introdueix la ruta absoluta al teu entorn:
   ```
   /ruta/al/teu/projecte/healthcare-rag-slm/code/healthcare-rag-env/bin/python3
   ```

## Instal·lació Manual (Opcional)

Si prefereixes fer la instal·lació pas a pas:

### Pas 1: Instal·lar Ollama

```bash
brew install ollama
brew services start ollama

# Descarregar models
ollama pull mistral
ollama pull llama3.2
```

### Pas 2: Configurar Entorn Python

```bash
# Crear entorn virtual
python3 -m venv healthcare-rag-env
source healthcare-rag-env/bin/activate

# Instal·lar dependències
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

### Pas 3: Configurar `.env`

```bash
cp .env.example .env
```

### Pas 4: Iniciar Serveis

```bash
docker compose up -d qdrant
docker compose up -d api
```

## Estructura del Proyecto

```
healthcare-rag-slm/code/
├── config/                     # Configuración del sistema
│   ├── settings.py            # Configuración centralizada
│   └── ontologies/            # Ontologías médicas
├── ingestion/                 # Bloque 1: Ingesta de datos
│   ├── connectors/           # Conectores de fuentes
│   ├── processors/           # Procesadores de documentos
│   ├── chunking/            # Estrategias de chunking
│   └── enrichment/          # Enriquecimiento ontológico
├── indexing/                 # Bloque 2: Indexación híbrida
│   ├── embeddings/          # Gestión de embeddings
│   ├── vectorial/           # Índice vectorial (Qdrant)
│   ├── lexical/            # Índice lexical (BM25)
│   └── ontological/        # Índice ontológico
├── retrieval/               # Bloque 3: Recuperación
│   ├── query_processing/   # Procesamiento de queries
│   ├── retrievers/         # Recuperadores híbridos
│   ├── fusion/            # Fusión RRF
│   └── reranking/         # Reranking semántico
├── generation/             # Generación con SLM
│   ├── models/            # Cliente Ollama
│   ├── prompts/          # Templates médicos
│   └── context/          # Gestión de contexto
├── api/                   # API REST
│   ├── routes/           # Endpoints
│   └── models/          # Modelos Pydantic
├── scripts/              # Scripts de utilidad
└── data/                # Datos del sistema
```

## Gestió de l'Entorn Virtual

```bash
# Activar l'entorn (cada vegada que obris un terminal nou)
source healthcare-rag-env/bin/activate

# Desactivar l'entorn (quan acabis de treballar)
deactivate

# Verificar que l'entorn està actiu
which python3  # Hauria de mostrar el path de l'entorn virtual

# Llistar paquets instal·lats
pip list
```

## Ús del Sistema

### API Endpoints

#### Consulta RAG Principal
```bash
curl -X POST "http://localhost:8000/query/" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "¿Cuáles son los síntomas de la diabetes tipo 2?",
       "model": "mistral",
       "language": "es",
       "top_k": 10
     }'
```

#### Subir Documentos
```bash
curl -X POST "http://localhost:8000/documents/upload" \
     -F "file=@documento_medico.pdf" \
     -F "source=medical_documents" \
     -F "language=es"
```

#### Estado del Sistema
```bash
curl "http://localhost:8000/health/"
```

### Servicios Disponibles

- **API Healthcare RAG**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard
- **Ollama API**: http://localhost:11434

## Configuración

### Variables de Entorno (.env)

```bash
# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=healthcare_rag

# Embeddings
EMBEDDING_MODEL=BAAI/bge-m3
EMBEDDING_DEVICE=cpu

# BioPortal (opcional)
BIOPORTER_API_KEY=your_api_key_here

# Idioma por defecto
DEFAULT_LANGUAGE=es
```

## Comandos Útiles

### Gestión de Servicios
```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar servicios
docker-compose down

# Reconstruir
docker-compose up -d --build
```

### Gestión de Modelos Ollama
```bash
# Listar modelos
ollama list

# Descargar modelo
ollama pull llama3.2:3b

# Probar modelo
ollama run mistral "Explica qué es la hipertensión"
```

### Gestión de Datos
```bash
# Limpiar base de datos vectorial
curl -X DELETE "http://localhost:8000/collections/clear"

# Ver estadísticas
curl "http://localhost:8000/collections/stats"
```

## Desarrollo

### Estructura de Módulos

- **Ingestion**: Procesamiento de documentos médicos
- **Indexing**: Indexación híbrida (vectorial + lexical + ontológica)
- **Retrieval**: Recuperación inteligente con fusión RRF
- **Generation**: Generación contextual con templates médicos

### Añadir Nuevos Conectores

1. Heredar de `BaseConnector`
2. Implementar métodos abstractos
3. Añadir al pipeline de ingestion

### Personalizar Templates

Los templates médicos están en `generation/prompts/medical_templates.py`

## Troubleshooting

### Ollama no responde
```bash
brew services restart ollama
ps aux | grep ollama
```

### Qdrant no conecta
```bash
docker-compose restart qdrant
curl http://localhost:6333/healthz
```

### API no inicia
```bash
docker-compose logs api
docker-compose restart api
```

### Problemas de memoria
- Reducir `EMBEDDING_BATCH_SIZE`
- Usar modelos más pequeños (`llama3.2:3b`)
- Aumentar memoria Docker

## Monitorización

### Health Checks
```bash
# Estado general
curl http://localhost:8000/health/

# Componentes individuales
curl http://localhost:8000/health/ollama
curl http://localhost:8000/health/qdrant
curl http://localhost:8000/health/embeddings
```

### Métricas
- Tiempo de respuesta de queries
- Uso de memoria de embeddings
- Estadísticas de recuperación
- Rendimiento de modelos

## 📚 Documentació

### **Documentació Unificada**

Tota la documentació del projecte està centralitzada a `/docs`:

| Document | Descripció |
|----------|------------|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Arquitectura completa del sistema |
| [`docs/SETUP.md`](docs/SETUP.md) | Guia de setup complet (API keys, ontologies, PubMed) |
| [`docs/DEMO.md`](docs/DEMO.md) | Guia de demostració pas a pas |

### **API Documentation**

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🚀 Próximos Desarrollos

1. ✅ **Ontologies Mèdiques**: SNOMED CT, MeSH, ICD-10 (completat)
2. ✅ **PubMed Integration**: Articles amb filtratge per citacions (completat)
3. ⏳ **Query Expansion**: Sinònims ontològics
4. ⏳ **Reranking**: Cross-encoder per rellevància clínica
5. ⏳ **Prompts Específics**: Templates per casos d'ús (informe alta, derivació, resum)
6. ⏳ **Avaluació**: Mètriques BLEU, ROUGE, BERTScore

---

## 🆘 Soporte

Para problemas técnicos:
1. Consultar `docs/SETUP.md` per troubleshooting
2. Ejecutar `python3 scripts/verify_setup.py`
3. Revisar logs: `docker-compose logs`
4. Consultar documentación API: http://localhost:8000/docs

## Licencia

Proyecto desarrollado como parte del Máster en Ciencia de Datos.

---

**Nota**: Este sistema está diseñado para asistir a profesionales sanitarios con información orientativa. No sustituye el criterio médico profesional.
