# 🧪 Test Scripts

Scripts per validar i testejar el sistema Healthcare RAG.

## Scripts Disponibles

### Tests d'Endpoint

#### `test_discharge_summary_endpoint.py`
Test complet de l'endpoint `/generate/discharge-summary` amb 3 casos clínics.

```bash
../utils/activate_and_run.sh python test_discharge_summary_endpoint.py
```

#### `test_discharge_simple.py`
Test ràpid amb un cas clínic simple.

```bash
../utils/activate_and_run.sh python test_discharge_simple.py
```

### Tests d'Integració

#### `run_ontology_tests.sh`
Tests d'integració amb ontologies mèdiques (SNOMED CT, MeSH, ICD-10).

```bash
./run_ontology_tests.sh
```

#### `run_query_expansion_tests.sh`
Tests d'expansió semàntica de queries.

```bash
./run_query_expansion_tests.sh
```

### Tests de Retrieval

#### `test_sas_protocols_retrieval.py`
Verifica la recuperació de protocols SAS de Qdrant.

```bash
../utils/activate_and_run.sh python test_sas_protocols_retrieval.py
```

## Prerequisits

- Sistema aixecat (`../lifecycle/start.sh`)
- Protocols indexats (`../data/ingest_sas_protocols.py`)
