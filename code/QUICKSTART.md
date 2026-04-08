# 🚀 Guia Ràpida d'Arrencada

## Estructura del Projecte

```
code/
├── config/              # Configuració del sistema
├── data/                # Dades locals
├── docs/                # Documentació detallada
├── scripts/             # Scripts d'utilitat
├── deploy/              # Infraestructura Docker
│   ├── docker/          # Dockerfile
│   └── compose/         # docker-compose.yml
├── src/
│   ├── main/            # Codi de producció
│   │   ├── api/         # FastAPI REST API
│   │   ├── core/        # Lògica de negoci (ingestion, indexing, retrieval, generation)
│   │   ├── infrastructure/  # Clients tècnics (Ollama, Qdrant)
│   │   └── main.py      # Entry point
│   └── test/            # Tests
└── requirements.txt
```

## ⚡ Arrencada Ràpida

### Primera vegada (Setup inicial)

```bash
# Instal·lació i configuració inicial (només una vegada)
./scripts/bootstrap.sh
```

### Ús diari

```bash
# Aixecar el sistema
./scripts/start.sh

# Aturar el sistema
./scripts/stop.sh
```

### Després de canvis al codi

```bash
# Reconstruir imatges Docker
./scripts/rebuild.sh
```

## 📋 Scripts Disponibles

| Script | Propòsit | Quan usar-lo |
|--------|----------|-------------|
| `bootstrap.sh` | Instal·lació inicial | Primera vegada |
| `start.sh` | Aixecar sistema | Ús diari |
| `stop.sh` | Aturar sistema | Ús diari |
| `rebuild.sh` | Reconstruir | Després de canvis |

Veure `scripts/README.md` per més detalls.

## Arrencada Manual (Alternativa)

### 1. Activar Entorn Virtual (Opcional)

```bash
source healthcare-rag-env/bin/activate
```

### 2. Navegar al Directori de Deploy

```bash
cd deploy/compose
```

### 3. Aturar Contenidors Anteriors

```bash
docker-compose down
```

### 4. Construir Imatges

```bash
docker-compose build --no-cache
```

### 5. Aixecar Contenidors

```bash
docker-compose up -d
```

### 6. Verificar Estat

```bash
docker ps
curl http://localhost:8000/health/
```

## Endpoints Disponibles

| Endpoint | Descripció |
|----------|------------|
| `http://localhost:8000/health/live` | Comprova si l'API està viva |
| `http://localhost:8000/health/ready` | Comprova si el sistema està preparat |
| `http://localhost:8000/health/` | Estat complet de tots els components |
| `http://localhost:8000/docs` | Documentació interactiva (Swagger) |
| `http://localhost:6333/dashboard` | Dashboard de Qdrant |

## Comandaments Útils

### Veure Logs

```bash
# Logs de l'API
docker logs healthcare-rag-api

# Logs de Qdrant
docker logs healthcare-rag-qdrant

# Seguir logs en temps real
docker logs -f healthcare-rag-api
```

### Aturar el Sistema

```bash
# Opció recomanada (manté volums)
./scripts/stop.sh

# O manualment
cd deploy/compose
docker-compose stop
```

### Reiniciar Contenidors

```bash
cd deploy/compose
docker-compose restart
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

## Verificació del Sistema

Després d'aixecar els contenidors, executa:

```bash
# Verificar API
curl http://localhost:8000/health/

# Resposta esperada:
# {
#   "status": "healthy",
#   "components": {
#     "ollama": {"status": "healthy", ...},
#     "qdrant": {"status": "healthy", ...},
#     "embeddings": {"status": "disabled", ...}
#   }
# }
```

## Estat Actual del Sistema

### ✅ Funcional
- API FastAPI amb estructura modular
- Health endpoints
- Connexió amb Ollama (Mistral)
- Connexió amb Qdrant
- Middleware de logging
- Arquitectura neta: config / deploy / src/main / src/test

### ⏸️ Temporalment Desactivat
- Embeddings (torch)
- Indexació vectorial de documents
- Cerca semàntica

## Documentació Completa

Per més detalls, consulta:
- **[docs/SETUP.md](docs/SETUP.md)** - Guia d'instal·lació completa
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Arquitectura del sistema

## Resolució de Problemes

### Port 8000 ja en ús

```bash
lsof -ti:8000 | xargs kill -9
```

### Ollama no respon

```bash
# Verificar que Ollama està executant-se
ollama list

# Si no està executant-se
ollama serve
```

### Reconstruir des de zero

```bash
cd deploy/compose
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## Desenvolupament Local (sense Docker)

```bash
# Activar entorn virtual
source healthcare-rag-env/bin/activate

# Configurar variables d'entorn
export QDRANT_HOST=localhost
export OLLAMA_BASE_URL=http://localhost:11434

# Executar l'API
python -m uvicorn src.main.main:app --reload --host 0.0.0.0 --port 8000
```

## Suport

Per problemes o preguntes, consulta la documentació completa a `docs/`.
