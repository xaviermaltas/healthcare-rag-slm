# Guia d'Instal·lació i Configuració

## Requisits Previs

- **Python 3.11+**
- **Docker i Docker Compose**
- **Ollama** (instal·lat localment)
- **Git**

## Estructura del Projecte

```
code/
├── config/          # Configuració del sistema
├── data/            # Dades locals i caches
├── docs/            # Documentació
├── scripts/         # Scripts d'utilitat
├── deploy/          # Infraestructura Docker
│   ├── docker/      # Dockerfile
│   └── compose/     # docker-compose.yml
├── src/
│   ├── main/        # Codi de producció
│   │   ├── api/     # FastAPI endpoints
│   │   ├── core/    # Lògica de negoci
│   │   └── infrastructure/  # Clients tècnics
│   └── test/        # Tests
└── requirements.txt
```

## Pas 1: Clonar el Repositori

```bash
cd /Users/xaviermaltastarridas/Desktop/myRepos/healthcare-rag-slm/code
```

## Pas 2: Configurar Entorn Virtual Python (Opcional però Recomanat)

```bash
# Crear entorn virtual
python3.11 -m venv healthcare-rag-env

# Activar entorn virtual
source healthcare-rag-env/bin/activate

# Instal·lar dependències
pip install -r requirements.txt
```

## Pas 3: Configurar Ollama

```bash
# Instal·lar Ollama (si no està instal·lat)
# Visita: https://ollama.ai

# Descarregar model Mistral
ollama pull mistral

# Verificar que Ollama està executant-se
ollama list
```

## Pas 4: Configurar Variables d'Entorn

Crea un fitxer `.env` a l'arrel del projecte:

```bash
# Application
APP_NAME=Healthcare RAG System
APP_VERSION=1.0.0
APP_ENV=development
DEBUG=true

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=mistral
OLLAMA_TIMEOUT=120

# Qdrant
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_COLLECTION=healthcare_documents
QDRANT_VECTOR_SIZE=1024

# Logging
LOG_LEVEL=INFO
```

## Pas 5: Aixecar el Sistema

### Opció A: Instal·lació Automàtica (Recomanat)

```bash
# Des de l'arrel del projecte
./scripts/bootstrap.sh
```

Aquest script farà tots els passos anteriors automàticament.

### Opció B: Manual

```bash
# Navegar al directori de compose
cd deploy/compose

# Aturar contenidors anteriors (si n'hi ha)
docker-compose stop

# Construir imatges des de zero
docker-compose build --no-cache

# Aixecar contenidors
docker-compose up -d

# Verificar estat dels contenidors
docker ps
```

## Pas 6: Verificar el Sistema

```bash
# Comprovar salut de l'API
curl http://localhost:8000/health/live

# Comprovar estat complet del sistema
curl http://localhost:8000/health/

# Comprovar Qdrant
curl http://localhost:6333/health

# Obrir documentació de l'API
open http://localhost:8000/docs

# Obrir dashboard de Qdrant
open http://localhost:6333/dashboard
```

## Pas 7: Veure Logs

```bash
# Logs de l'API
docker logs healthcare-rag-api

# Logs de Qdrant
docker logs healthcare-rag-qdrant

# Seguir logs en temps real
docker logs -f healthcare-rag-api
```

## 📋 Scripts de Gestió del Sistema

El projecte inclou scripts per gestionar el cicle de vida del sistema:

| Script | Propòsit | Quan usar-lo |
|--------|----------|-------------|
| `bootstrap.sh` | Instal·lació inicial completa | Primera vegada |
| `start.sh` | Aixecar sistema (manté volums) | Ús diari |
| `stop.sh` | Aturar sistema (manté volums) | Ús diari |
| `rebuild.sh` | Reconstruir després de canvis | Després de modificar codi |

**Veure `scripts/README.md` per documentació completa.**

## Comandaments Útils

### Aturar el Sistema

```bash
# Opció recomanada (manté volums)
./scripts/stop.sh

# O manualment
cd deploy/compose
docker-compose stop
```

### Eliminar Tot (incloent volums)

```bash
cd deploy/compose
docker-compose down -v
```

### Reconstruir després de Canvis

```bash
# Opció recomanada
./scripts/rebuild.sh

# O manualment
cd deploy/compose
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Reiniciar Contenidors

```bash
cd deploy/compose
docker-compose restart
```

### Eliminar Volums i Dades

```bash
cd deploy/compose
docker-compose down -v
```

## Resolució de Problemes

### Error: "No module named 'src'"

Assegura't que `PYTHONPATH=/app` està configurat al Dockerfile.

### Error: "Connection refused" a Ollama

Verifica que Ollama està executant-se localment:

```bash
ollama list
```

Si no està executant-se:

```bash
ollama serve
```

### Error: Qdrant "unhealthy"

Això és un warning conegut amb OrbStack. El sistema segueix funcionant correctament.

### Error: Port 8000 ja en ús

Atura qualsevol servei que estigui utilitzant el port 8000:

```bash
lsof -ti:8000 | xargs kill -9
```

## Desenvolupament Local (sense Docker)

Si vols executar l'API localment sense Docker:

```bash
# Activar entorn virtual
source healthcare-rag-env/bin/activate

# Configurar variables d'entorn per local
export QDRANT_HOST=localhost
export OLLAMA_BASE_URL=http://localhost:11434

# Executar l'API
cd /Users/xaviermaltastarridas/Desktop/myRepos/healthcare-rag-slm/code
python -m uvicorn src.main.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints Disponibles

- **GET /health/live** - Comprova si l'API està viva
- **GET /health/ready** - Comprova si el sistema està preparat
- **GET /health/** - Estat complet de tots els components
- **GET /docs** - Documentació interactiva de l'API (Swagger)
- **GET /redoc** - Documentació alternativa (ReDoc)

## Estat Actual del Sistema

### ✅ Funcional
- API FastAPI
- Health endpoints
- Connexió amb Ollama
- Connexió amb Qdrant
- Middleware de logging

### ⏸️ Temporalment Desactivat
- Embeddings (dependència torch)
- Indexació de documents amb vectors
- Cerca semàntica

Aquestes funcionalitats es poden reactivar més endavant quan sigui necessari.
