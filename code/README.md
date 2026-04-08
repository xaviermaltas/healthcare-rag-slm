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

- **Ingesta Intel·ligent**: Connectors per MedlinePlus, BioPortal i PDFs
- **Indexació Híbrida**: Combina cerca vectorial (BGE-M3), lexical (BM25) i ontològica
- **Processament Mèdic**: NER especialitzat en terminologia mèdica espanyola/catalana
- **Generació Contextual**: Templates mèdics especialitzats amb Ollama
- **Chunking Semàntic**: Respecta fronteres semàntiques en documents mèdics
- **API RESTful**: Endpoints complets per gestió i consultes RAG

## Requisits del Sistema

- **macOS**: M1/M2 (recomanat per Metal GPU)
- **RAM**: Mínim 16GB
- **Emmagatzematge**: 10GB lliures
- **Docker/OrbStack**: Instal·lat i funcionant
- **Homebrew**: Instal·lat
- **Python**: 3.11+ (compatible amb 3.14+)

## Instal·lació

### 1. Clonar el Repositori

```bash
git clone <repository-url>
cd healthcare-rag-slm/code
```

### 2. Crear Entorn Virtual (OBLIGATORI)

```bash
# Crear entorn virtual
python3 -m venv healthcare-rag-env

# Activar entorn virtual
source healthcare-rag-env/bin/activate

# Verificar que l'entorn està actiu (hauria d'aparèixer el nom)
# (healthcare-rag-env) xaviermaltastarridas@...

# Instal·lar dependències
python3 -m pip install --upgrade pip
python3 -m pip install -r code/requirements.txt
```

**Nota Important**: Si obtens "command not found: pip", utilitza sempre `python3 -m pip`.

### 3. Executar Script d'Instal·lació

```bash
# Fer executable l'script
chmod +x scripts/setup.sh

# Executar instal·lació automàtica
./scripts/setup.sh
```

L'script automàticament:
- ✅ Instal·la Ollama i models necessaris
- ✅ Inicia serveis Docker (Qdrant)
- ✅ Construeix i desplega l'API
- ✅ Verifica la instal·lació completa

### 4. Verificar Instal·lació

```bash
python3 scripts/verify_setup.py
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
# Crear entorn virtual (OBLIGATORI)
python3 -m venv healthcare-rag-env

# Activar entorn virtual
source healthcare-rag-env/bin/activate

# Actualitzar pip
python3 -m pip install --upgrade pip

# Instal·lar dependències
python3 -m pip install -r requirements.txt
```

### Pas 3: Iniciar Serveis

```bash
# Iniciar Qdrant
docker-compose up -d qdrant

# Construir i iniciar API
docker-compose up -d api
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

## Próximos Desarrollos

1. **Frontend Web**: Interfaz de usuario para profesionales sanitarios
2. **Autenticación**: Sistema de usuarios y control de acceso
3. **Más Conectores**: PubMed, bases de datos hospitalarias
4. **Ontologías Avanzadas**: SNOMED-CT completo, ICD-11
5. **Modelos Especializados**: Fine-tuning para dominio médico
6. **Evaluación**: Métricas específicas para RAG médico

## Soporte

Para problemas técnicos:
1. Ejecutar `python3 scripts/verify_setup.py`
2. Revisar logs: `docker-compose logs`
3. Consultar documentación API: http://localhost:8000/docs

## Licencia

Proyecto desarrollado como parte del Máster en Ciencia de Datos.

---

**Nota**: Este sistema está diseñado para asistir a profesionales sanitarios con información orientativa. No sustituye el criterio médico profesional.
