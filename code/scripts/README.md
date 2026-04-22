# 📜 Scripts del Sistema Healthcare RAG

Aquesta carpeta conté tots els scripts organitzats per funcionalitat.

## 📂 Estructura de Directoris

```
scripts/
├── lifecycle/     # Gestió del cicle de vida del sistema
├── utils/         # Utilitats generals
├── data/          # Ingesta i processament de dades
├── tests/         # Scripts de test i validació
└── demos/         # Demos interactives dels casos d'ús
```

---

## 🔄 Lifecycle - Gestió del Sistema

### 🎯 `lifecycle/bootstrap.sh` - Instal·lació Inicial

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
./scripts/lifecycle/bootstrap.sh
```

**Nota:** Aquest script només cal executar-lo una vegada. Després usa `start.sh` i `stop.sh`.

---

### 🚀 `lifecycle/start.sh` - Aixecar el Sistema

**Quan usar-lo:** Cada vegada que vulguis **aixecar** el sistema.

**Què fa:**
- ✅ Verifica que Docker està executant-se
- ✅ Inicia Ollama si no està executant-se
- ✅ Aixeca contenidors Docker (API + Qdrant)
- ✅ **Manté volums i dades existents**
- ✅ Verifica la salut del sistema

**Ús:**
```bash
./scripts/lifecycle/start.sh
```

**Característiques:**
- 💾 **Preserva volums** - Les dades de Qdrant es mantenen
- 🤖 **Gestiona Ollama** - L'inicia automàticament si cal
- ⚡ **Ràpid** - No reconstrueix imatges

---

### 🛑 `lifecycle/stop.sh` - Aturar el Sistema

**Quan usar-lo:** Cada vegada que vulguis **aturar** el sistema.

**Què fa:**
- ✅ Atura contenidors Docker (API + Qdrant)
- ✅ **Manté volums i dades existents**
- ✅ Pregunta si vols aturar Ollama també
- ✅ Mostra estat dels volums preservats

**Ús:**
```bash
./scripts/lifecycle/stop.sh
```

**Característiques:**
- 💾 **Preserva volums** - Les dades NO s'eliminen
- 🤖 **Ollama opcional** - Pots decidir si l'aturas o no
- 🔄 **Reversible** - Pots tornar a aixecar amb `start.sh`

---

### 🔨 `lifecycle/rebuild.sh` - Reconstruir des de Zero

**Quan usar-lo:** Quan facis **canvis al codi** i necessitis reconstruir les imatges Docker.

**Què fa:**
- ⚠️ Atura i elimina contenidors existents
- ⚠️ Reconstrueix imatges Docker des de zero (`--no-cache`)
- ✅ Aixeca contenidors amb les noves imatges
- ✅ Verifica la salut del sistema

**Ús:**
```bash
./scripts/lifecycle/rebuild.sh
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
./scripts/lifecycle/bootstrap.sh
```

### Ús diari
```bash
# Aixecar el sistema
./scripts/lifecycle/start.sh

# ... treballar amb el sistema ...

# Aturar el sistema
./scripts/lifecycle/stop.sh
```

### Després de fer canvis al codi
```bash
# Reconstruir amb els canvis
./scripts/lifecycle/rebuild.sh
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
./scripts/lifecycle/rebuild.sh
```

### Vull començar de zero completament
```bash
# 1. Aturar tot
./scripts/lifecycle/stop.sh

# 2. Eliminar volums
cd deploy/compose
docker-compose down -v

# 3. Tornar a executar bootstrap
cd ../..
./scripts/lifecycle/bootstrap.sh
```

---

## 🛠️ Utils - Utilitats Generals

### 🔧 `utils/activate_and_run.sh` - Executar amb Entorn Virtual

**Quan usar-lo:** Per executar qualsevol script Python amb l'entorn virtual activat.

**Què fa:**
- ✅ Activa l'entorn virtual automàticament
- ✅ Executa la comanda especificada
- ✅ Desactiva l'entorn després

**Ús:**
```bash
./scripts/utils/activate_and_run.sh python <script.py>
./scripts/utils/activate_and_run.sh pytest tests/
```

### ✅ `utils/verify_setup.py` - Verificar Configuració del Sistema

**Quan usar-lo:** Per verificar que tot està correctament configurat.

**Què fa:**
- ✅ Verifica versió de Python
- ✅ Verifica paquets instal·lats
- ✅ Verifica estructura de directoris
- ✅ Verifica connexió a Ollama, Qdrant i API
- ✅ Verifica models d'embeddings

**Ús:**
```bash
./scripts/utils/activate_and_run.sh python scripts/utils/verify_setup.py
```

---

## 📊 Data - Ingesta i Processament

### 🧬 `data/ingest_medical_knowledge.py` - Ingesta d'Ontologies i PubMed

**Quan usar-lo:** Per poblar la base de dades amb coneixement mèdic (ontologies + articles).

**Què fa:**
- ✅ Descarrega conceptes de SNOMED CT, MeSH, ICD-10
- ✅ Descarrega articles de PubMed (altament citats + recents)
- ✅ Genera embeddings amb BGE-M3
- ✅ Indexa tot a Qdrant

**Ús:**
```bash
./scripts/utils/activate_and_run.sh python scripts/data/ingest_medical_knowledge.py
```

**Prerequisits:**
- Sistema aixecat (`./scripts/lifecycle/start.sh`)
- API key de BioPortal configurada a `.env`

### 🏥 `data/ingest_sas_protocols.py` - Ingesta de Protocols SAS

**Quan usar-lo:** Per indexar protocols clínics del SAS a Qdrant.

**Què fa:**
- ✅ Crea protocols simulats per diferents especialitats
- ✅ Genera embeddings amb BGE-M3
- ✅ Indexa protocols a Qdrant amb metadata

**Ús:**
```bash
./scripts/utils/activate_and_run.sh python scripts/data/ingest_sas_protocols.py
```

---

## 🧪 Tests - Validació i Testing

### 🧪 `tests/run_ontology_tests.sh` - Tests d'Integració d'Ontologies

**Què fa:**
- ✅ Prova connexió a BioPortal
- ✅ Verifica SNOMED CT, MeSH, ICD-10
- ✅ Prova cerca de conceptes

**Ús:**
```bash
./scripts/tests/run_ontology_tests.sh
```

### 🧪 `tests/run_query_expansion_tests.sh` - Tests d'Expansió de Queries

**Què fa:**
- ✅ Prova expansió semàntica de queries
- ✅ Verifica integració amb ontologies

**Ús:**
```bash
./scripts/tests/run_query_expansion_tests.sh
```

### 📋 `tests/test_discharge_summary_endpoint.py` - Test Complet d'Informes d'Alta

**Què fa:**
- ✅ Testa endpoint `/generate/discharge-summary`
- ✅ 3 casos clínics complets (Infart, Diabetis, AVC)
- ✅ Validació de resposta i estructura

**Ús:**
```bash
./scripts/utils/activate_and_run.sh python scripts/tests/test_discharge_summary_endpoint.py
```

### ⚡ `tests/test_discharge_simple.py` - Test Ràpid

**Què fa:**
- ✅ Test ràpid amb cas clínic simple
- ✅ Verificació bàsica de funcionalitat

**Ús:**
```bash
./scripts/utils/activate_and_run.sh python scripts/tests/test_discharge_simple.py
```

### 🔍 `tests/test_sas_protocols_retrieval.py` - Test de Retrieval de Protocols

**Què fa:**
- ✅ Verifica recuperació de protocols de Qdrant
- ✅ Testa filtratge per especialitat

**Ús:**
```bash
./scripts/utils/activate_and_run.sh python scripts/tests/test_sas_protocols_retrieval.py
```

---

## 🎭 Demos - Casos d'Ús Interactius

### 🏥 `demos/demo_discharge_summary.py` - Demo Informe d'Alta

**Què fa:**
- ✅ Demo interactiva del cas d'ús principal
- ✅ Cas clínic real d'Infart Agut de Miocardi
- ✅ Mostra tot el procés de generació
- ✅ Visualitza protocols utilitzats i validació

**Ús:**
```bash
./scripts/utils/activate_and_run.sh python scripts/demos/demo_discharge_summary.py
```

**Característiques:**
- 📊 Mostra temps de generació i mètriques
- 📚 Llista protocols SAS consultats
- ✅ Validació automàtica de l'informe
- 💡 Mostra beneficis i impacte estimat

---

## 📚 Més Informació

- **Guia ràpida:** `../QUICKSTART.md`
- **Setup detallat:** `../docs/SETUP.md`
- **Arquitectura:** `../docs/ARCHITECTURE.md`
- **Tests:** `../tests/` (tests unitaris i d'integració)
