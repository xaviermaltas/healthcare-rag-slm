# 📜 Scripts del Sistema Healthcare RAG

Aquesta carpeta conté els scripts per gestionar el cicle de vida del sistema Healthcare RAG.

## 📋 Scripts Disponibles

### 🎯 `bootstrap.sh` - Instal·lació Inicial del Sistema

**Quan usar-lo:** **Una sola vegada** quan configures el projecte per primera vegada.

**Què fa:**
- ✅ Instal·la dependències del sistema (Ollama, Python 3.11)
- ✅ Inicia el servei d'Ollama
- ✅ Descarrega models d'Ollama (Mistral, Llama3.2)
- ✅ Crea entorn virtual Python
- ✅ Instal·la dependències Python
- ✅ Crea directoris necessaris
- ✅ Aixeca Qdrant i API per primera vegada
- ✅ Verifica que tot funciona

**Ús:**
```bash
./scripts/bootstrap.sh
```

**Nota:** Aquest script només cal executar-lo una vegada. Després usa `start.sh` i `stop.sh`.

---

### 🚀 `start.sh` - Aixecar el Sistema

**Quan usar-lo:** Cada vegada que vulguis **aixecar** el sistema.

**Què fa:**
- ✅ Verifica que Docker està executant-se
- ✅ Inicia Ollama si no està executant-se
- ✅ Aixeca contenidors Docker (API + Qdrant)
- ✅ **Manté volums i dades existents**
- ✅ Verifica la salut del sistema

**Ús:**
```bash
./scripts/start.sh
```

**Característiques:**
- 💾 **Preserva volums** - Les dades de Qdrant es mantenen
- 🤖 **Gestiona Ollama** - L'inicia automàticament si cal
- ⚡ **Ràpid** - No reconstrueix imatges

---

### 🛑 `stop.sh` - Aturar el Sistema

**Quan usar-lo:** Cada vegada que vulguis **aturar** el sistema.

**Què fa:**
- ✅ Atura contenidors Docker (API + Qdrant)
- ✅ **Manté volums i dades existents**
- ✅ Pregunta si vols aturar Ollama també
- ✅ Mostra estat dels volums preservats

**Ús:**
```bash
./scripts/stop.sh
```

**Característiques:**
- 💾 **Preserva volums** - Les dades NO s'eliminen
- 🤖 **Ollama opcional** - Pots decidir si l'aturas o no
- 🔄 **Reversible** - Pots tornar a aixecar amb `start.sh`

---

### 🔨 `rebuild.sh` - Reconstruir des de Zero

**Quan usar-lo:** Quan facis **canvis al codi** i necessitis reconstruir les imatges Docker.

**Què fa:**
- ⚠️ Atura i elimina contenidors existents
- ⚠️ Reconstrueix imatges Docker des de zero (`--no-cache`)
- ✅ Aixeca contenidors amb les noves imatges
- ✅ Verifica la salut del sistema

**Ús:**
```bash
./scripts/rebuild.sh
```

**⚠️ ATENCIÓ:**
- Aquest script elimina contenidors però **manté volums**
- Triga més temps perquè reconstrueix tot
- Només usa'l quan hagis fet canvis al codi

---

## 🔄 Flux de Treball Típic

### Primera vegada (Setup inicial)
```bash
# 1. Instal·lació inicial (només una vegada)
./scripts/bootstrap.sh
```

### Ús diari
```bash
# Aixecar el sistema
./scripts/start.sh

# ... treballar amb el sistema ...

# Aturar el sistema
./scripts/stop.sh
```

### Després de fer canvis al codi
```bash
# Reconstruir amb els canvis
./scripts/rebuild.sh
```

---

## 📊 Comparativa de Scripts

| Script | Elimina contenidors | Reconstrueix imatges | Manté volums | Gestiona Ollama | Quan usar |
|--------|---------------------|----------------------|--------------|-----------------|-----------|
| `bootstrap.sh` | - | ✅ | ✅ | ✅ Inicia | Primera vegada |
| `start.sh` | ❌ | ❌ | ✅ | ✅ Inicia | Ús diari (aixecar) |
| `stop.sh` | ❌ | ❌ | ✅ | ⚠️ Opcional | Ús diari (aturar) |
| `rebuild.sh` | ✅ | ✅ | ✅ | ❌ | Després de canvis |

---

## 🗑️ Eliminar Tot (Incloent Volums)

Si vols eliminar **tot** (contenidors + volums + dades):

```bash
cd deploy/compose
docker-compose down -v
```

**⚠️ ATENCIÓ:** Això eliminarà totes les dades de Qdrant i hauràs de tornar a indexar documents.

---

## 🔍 Verificar Estat del Sistema

Després d'aixecar el sistema amb `start.sh`, pots verificar:

```bash
# Estat dels contenidors
docker ps

# Salut de l'API
curl http://localhost:8000/health/

# Obrir documentació
open http://localhost:8000/docs

# Veure logs
docker logs -f healthcare-rag-api
```

---

## 🆘 Resolució de Problemes

### Error: "Docker no està executant-se"
```bash
# Inicia Docker Desktop o OrbStack
```

### Error: "Ollama no respon"
```bash
# Inicia Ollama manualment
ollama serve

# O amb brew services
brew services start ollama
```

### Els contenidors no arranquen
```bash
# Veure logs per detectar errors
docker logs healthcare-rag-api
docker logs healthcare-rag-qdrant

# Reconstruir des de zero
./scripts/rebuild.sh
```

### Vull començar de zero completament
```bash
# 1. Aturar tot
./scripts/stop.sh

# 2. Eliminar volums
cd deploy/compose
docker-compose down -v

# 3. Tornar a executar bootstrap
cd ../..
./scripts/bootstrap.sh
```

---

### 🧬 `ingest_medical_knowledge.py` - Ingesta d'Ontologies i PubMed

**Quan usar-lo:** Per poblar la base de dades amb coneixement mèdic (ontologies + articles).

**Què fa:**
- ✅ Descarrega conceptes de SNOMED CT, MeSH, ICD-10
- ✅ Descarrega articles de PubMed (altament citats + recents)
- ✅ Genera embeddings amb BGE-M3
- ✅ Indexa tot a Qdrant

**Ús:**
```bash
./scripts/activate_and_run.sh python3 scripts/ingest_medical_knowledge.py
```

**Prerequisits:**
- Sistema aixecat (`./scripts/start.sh`)
- API key de BioPortal configurada a `.env`

---

### 🧪 `run_ontology_tests.sh` - Tests d'Integració d'Ontologies

**Quan usar-lo:** Per verificar que les ontologies funcionen correctament.

**Què fa:**
- ✅ Prova connexió a BioPortal
- ✅ Verifica SNOMED CT, MeSH, ICD-10
- ✅ Prova cerca de conceptes
- ✅ Prova mapatge de text clínic

**Ús:**
```bash
./scripts/run_ontology_tests.sh
```

**Nota:** Els tests reals estan a `/tests/integration/`, aquest script només els executa.

---

### 🔧 `activate_and_run.sh` - Executar amb Entorn Virtual

**Quan usar-lo:** Per executar qualsevol script Python amb l'entorn virtual activat.

**Què fa:**
- ✅ Activa l'entorn virtual automàticament
- ✅ Executa la comanda especificada
- ✅ Desactiva l'entorn després

**Ús:**
```bash
./scripts/activate_and_run.sh python3 <script.py>
./scripts/activate_and_run.sh pytest tests/
```

---

## 📚 Més Informació

- **Guia ràpida:** `../QUICKSTART.md`
- **Setup detallat:** `../docs/SETUP.md`
- **Arquitectura:** `../docs/ARCHITECTURE.md`
- **Tests:** `../tests/` (tests unitaris i d'integració)
