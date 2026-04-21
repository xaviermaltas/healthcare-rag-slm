# Healthcare RAG - Setup Complet

Guia completa per configurar i executar el sistema Healthcare RAG amb ontologies mèdiques (SNOMED CT, MeSH, ICD-10) i articles PubMed.

---

## 📋 Prerequisites

### **1. Sistema Operatiu**
- macOS M1/M2 (recomanat) o Linux
- Docker Desktop instal·lat i running
- Python 3.9+

### **2. Verificar Entorn**

```bash
# Verificar Docker
docker --version
docker ps

# Verificar Python
python3 --version

# Verificar Ollama (ha d'estar instal·lat nativament)
ollama --version
```

---

## 🔑 Configuració API Keys

### **1. BioPortal API Key (Obligatori per Ontologies)**

**Pas 1:** Registra't a BioPortal
- URL: https://bioportal.bioontology.org/account
- Crea un compte gratuït

**Pas 2:** Obtenir API Key
- Fes login
- Ves a "Account Details"
- Copia la teva API key (format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

**Pas 3:** Configurar `.env`

```bash
# Navegar al projecte
cd /Users/xaviermaltastarridas/Desktop/myRepos/healthcare-rag-slm/code

# Copiar exemple
cp .env.example .env

# Editar fitxer
nano .env

# Afegir API key
BIOPORTAL_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
BIOPORTAL_BASE_URL=https://data.bioontology.org

# Guardar: Ctrl+O, Enter, Ctrl+X
```

---

### **2. NCBI API Key (Opcional per PubMed)**

**Beneficis:**
- Augmenta rate limit de 3 → 10 requests/segon
- Recomanat per ingesta massiva

**Pas 1:** Registra't a NCBI
- URL: https://www.ncbi.nlm.nih.gov/account/

**Pas 2:** Crear API Key
- Ves a: https://www.ncbi.nlm.nih.gov/account/settings/
- Crea una nova API key

**Pas 3:** Afegir a configuració

```bash
# Editar .env
nano .env

# Afegir (opcional)
NCBI_API_KEY=your-ncbi-api-key-here
NCBI_EMAIL=your-email@example.com
```

---

## 🚀 Instal·lació

### **1. Clonar Repositori**

```bash
git clone <repository-url>
cd healthcare-rag-slm/code
```

---

### **2. Crear Entorn Virtual**

```bash
# Crear entorn
python3 -m venv healthcare-rag-env

# Activar entorn
source healthcare-rag-env/bin/activate

# Verificar
which python3
# Ha de mostrar: .../healthcare-rag-env/bin/python3
```

---

### **3. Instal·lar Dependències**

```bash
# Instal·lar requirements
pip install -r requirements.txt

# Verificar instal·lació
pip list | grep -E "fastapi|qdrant|transformers|torch"
```

---

### **4. Configurar Ollama**

```bash
# Verificar que Ollama està running
ollama list

# Descarregar model Mistral (si no el tens)
ollama pull mistral

# Verificar
ollama list
# Ha de mostrar: mistral:latest
```

---

## 🐳 Aixecar el Sistema

### **Opció 1: Script Automàtic (Recomanat)**

```bash
# Aixecar tots els serveis
./scripts/start.sh

# Espera ~30 segons mentre s'inicialitzen els serveis
```

**Output esperat:**
```
✅ Qdrant: OK
✅ API: OK
✅ Ollama: OK

📍 Endpoints disponibles:
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Qdrant: http://localhost:6333
   - Qdrant Dashboard: http://localhost:6333/dashboard
   - Ollama: http://localhost:11434
```

---

### **Opció 2: Manual**

```bash
# Aixecar Qdrant i API
docker-compose -f deploy/compose/docker-compose.yml up -d

# Verificar
docker ps
# Ha de mostrar: healthcare-rag-api, healthcare-rag-qdrant

# Verificar logs
docker logs -f healthcare-rag-api
```

---

## 🧬 Ingesta d'Ontologies i PubMed

### **1. Executar Script d'Ingesta**

```bash
# Assegura't que el sistema està running
./scripts/start.sh

# Executar ingesta
python3 scripts/ingest_medical_knowledge.py
```

---

### **2. Què fa el Script**

**Ontologies (SNOMED CT, MeSH, ICD-10):**
- Per cada tema mèdic (diabetes, hipertensió, etc.):
  - Cerca 50 conceptes a cada ontologia
  - Extreu sinònims, definicions, jerarquies
  - Total: ~500 conceptes

**PubMed:**
- Per cada tema mèdic:
  - 10 articles altament citats (>50 citacions, >10 anys)
  - 10 articles recents (<2 anys)
  - Total: ~200 articles

**Temps estimat:** 10-15 minuts

---

### **3. Output Esperat**

```
🚀 Starting Medical Knowledge Ingestion
Topics to process: 10

🔌 Initializing connectors...
  ✓ OntologyManager initialized
  ✓ PubMed connector initialized

📊 ONTOLOGY STATISTICS
  SNOMEDCT: 350,000+ classes
  MESH: 30,000+ descriptors
  ICD10CM: 70,000+ codes

📚 INGESTING ONTOLOGY CONCEPTS
  ✓ diabetes mellitus type 2: 50 concepts
    - SNOMEDCT: 25 concepts
    - MESH: 15 concepts
    - ICD10CM: 10 concepts
  ...

📄 INGESTING PUBMED ARTICLES
  ✓ diabetes mellitus type 2: 20 articles
    - 10 highly cited (avg 156 citations)
    - 10 recent (2024-2026)
  ...

✅ INGESTION COMPLETE
  ✅ Ontology concepts: 500
  ✅ PubMed articles: 200
  ✅ Total documents: 700
```

---

## ✅ Verificació

### **1. Health Check**

```bash
# Verificar estat del sistema
curl -s http://localhost:8000/health/detailed | python3 -m json.tool
```

**Output esperat:**
```json
{
  "status": "healthy",
  "components": {
    "ollama": {
      "status": "healthy",
      "model": "mistral"
    },
    "qdrant": {
      "status": "healthy",
      "collections": 1,
      "vectors_count": 700
    },
    "embeddings": {
      "status": "healthy",
      "model": "BAAI/bge-m3"
    }
  }
}
```

---

### **2. Test Query**

```bash
# Query simple
curl -X POST "http://localhost:8000/query/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cuál es el tratamiento de primera línea para diabetes tipo 2?",
    "top_k": 3,
    "language": "es"
  }' | python3 -m json.tool
```

---

### **3. Verificar Documents Indexats**

```bash
# Llistar documents
curl -s "http://localhost:8000/documents/" | python3 -m json.tool | head -50

# Estadístiques col·lecció
curl -s "http://localhost:8000/collections/healthcare_rag/stats" | python3 -m json.tool
```

---

## 🎯 Temes Mèdics Configurats

El sistema està pre-configurat amb aquests 10 temes:

1. **Diabetes mellitus type 2**
2. **Hypertension**
3. **Heart failure**
4. **Chronic kidney disease**
5. **Asthma**
6. **COPD**
7. **Depression**
8. **Anxiety disorder**
9. **Stroke**
10. **Myocardial infarction**

### **Afegir Nous Temes**

```python
# Edita scripts/ingest_medical_knowledge.py
MEDICAL_TOPICS = [
    "diabetes mellitus type 2",
    "hypertension",
    # Afegeix els teus temes aquí
    "rheumatoid arthritis",
    "multiple sclerosis"
]

# Re-executa ingesta
python3 scripts/ingest_medical_knowledge.py
```

---

## 🔧 Configuració Avançada

### **1. Ajustar Paràmetres d'Ingesta**

```python
# Edita scripts/ingest_medical_knowledge.py

# Més conceptes per tema
concepts_count = await ingest_ontology_concepts(
    ontology_manager=ontology_manager,
    topics=MEDICAL_TOPICS,
    concepts_per_topic=100  # Default: 50
)

# Més articles per tema
articles_count = await ingest_pubmed_articles(
    pubmed_connector=pubmed_connector,
    topics=MEDICAL_TOPICS,
    articles_per_topic=40  # Default: 20
)
```

---

### **2. Configurar Rate Limits**

```bash
# Edita .env

# BioPortal (màxim 1000 req/dia gratuït)
BIOPORTAL_RATE_LIMIT=10  # req/s

# PubMed
NCBI_RATE_LIMIT=3  # sense API key
NCBI_RATE_LIMIT=10  # amb API key
```

---

### **3. Configurar Chunking**

```bash
# Edita .env

# Mida chunks (tokens)
CHUNK_SIZE=512  # Default: 512
CHUNK_OVERLAP=50  # Default: 50

# Per documents més llargs
CHUNK_SIZE=1024
CHUNK_OVERLAP=100
```

---

## 🐛 Troubleshooting

### **Error: "BIOPORTAL_API_KEY not set"**

```bash
# Verifica .env
cat .env | grep BIOPORTAL_API_KEY

# Si no existeix, afegeix-la
echo "BIOPORTAL_API_KEY=your-key-here" >> .env

# Reinicia API
docker restart healthcare-rag-api
```

---

### **Error: "HTTP 401 Unauthorized" (BioPortal)**

- API key incorrecta o expirada
- Verifica a https://bioportal.bioontology.org/account
- Regenera API key si cal

---

### **Error: "HTTP 429 Too Many Requests"**

**BioPortal:**
- Límit: 1.000 requests/dia (gratuït)
- Solució: Espera 24h o crea un altre compte

**PubMed:**
- Límit: 3 req/s (sense API key)
- Solució: Afegeix NCBI API key per 10 req/s

---

### **Error: "Ollama connection refused"**

```bash
# Verifica que Ollama està running
ollama list

# Si no està running, inicia'l
open -a Ollama  # macOS

# Verifica port
curl http://localhost:11434/api/tags
```

---

### **Error: "Qdrant connection refused"**

```bash
# Verifica que Qdrant està running
docker ps | grep qdrant

# Si no està running
docker-compose -f deploy/compose/docker-compose.yml up -d qdrant

# Verifica port
curl http://localhost:6333/collections
```

---

## 🧹 Manteniment

### **Parar el Sistema**

```bash
# Parar tots els serveis
./scripts/stop.sh

# O manualment
docker-compose -f deploy/compose/docker-compose.yml down
```

---

### **Netejar Dades**

```bash
# Eliminar tots els documents indexats
curl -X DELETE "http://localhost:8000/collections/healthcare_rag/clear"

# Eliminar volumes Docker (ATENCIÓ: elimina tot)
docker-compose -f deploy/compose/docker-compose.yml down -v
```

---

### **Reconstruir des de Zero**

```bash
# Reconstruir tot
./scripts/rebuild.sh

# O manualment
docker-compose -f deploy/compose/docker-compose.yml down -v
docker-compose -f deploy/compose/docker-compose.yml build --no-cache
docker-compose -f deploy/compose/docker-compose.yml up -d
```

---

## 📚 Recursos

- **BioPortal**: https://bioportal.bioontology.org
- **BioPortal API Docs**: https://data.bioontology.org/documentation
- **PubMed**: https://pubmed.ncbi.nlm.nih.gov
- **PubMed E-utilities**: https://www.ncbi.nlm.nih.gov/books/NBK25501/
- **SNOMED CT Browser**: https://browser.ihtsdotools.org
- **MeSH Browser**: https://meshb.nlm.nih.gov
- **ICD-10-CM**: https://www.cdc.gov/nchs/icd/icd-10-cm.htm
- **Ollama**: https://ollama.ai
- **Qdrant**: https://qdrant.tech

---

## 🎓 Següents Passos

Després del setup, consulta:
- `docs/ARCHITECTURE.md` → Arquitectura completa del sistema
- `docs/DEMO.md` → Guia de demostració pas a pas
- `http://localhost:8000/docs` → API documentation (Swagger UI)

---

**Document preparat per:** Xavier Maltas Tarridas  
**Data:** Abril 2026  
**Versió:** 2.0 (Unificat)
