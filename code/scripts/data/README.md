# 📊 Data Scripts

Scripts per ingesta i processament de dades mèdiques.

## Scripts Disponibles

### `ingest_sas_protocols.py`
Indexa protocols clínics del SAS (Servei Andalús de Salut) a Qdrant.

**Què fa**:
- Crea protocols simulats per diferents especialitats
- Genera embeddings amb BGE-M3
- Indexa a Qdrant amb metadata (especialitat, tipus, oficial)

**Protocols inclosos**:
- Cardiologia: Infart Agut de Miocardi, Insuficiència Cardíaca
- Endocrinologia: Diabetis Mellitus
- Neurologia: Accident Cerebrovascular
- Pneumologia: MPOC, Pneumònia
- Nefrologia: Insuficiència Renal

**Ús**:
```bash
../utils/activate_and_run.sh python ingest_sas_protocols.py
```

**Temps estimat**: 2-3 minuts

---

### `ingest_medical_knowledge.py`
Indexa coneixement mèdic d'ontologies i articles científics.

**Què fa**:
- Descarrega conceptes de SNOMED CT, MeSH, ICD-10
- Descarrega articles de PubMed (altament citats + recents)
- Genera embeddings amb BGE-M3
- Indexa tot a Qdrant

**Prerequisits**:
- API key de BioPortal configurada a `.env`
- Connexió a internet

**Ús**:
```bash
../utils/activate_and_run.sh python ingest_medical_knowledge.py
```

**Temps estimat**: 10-15 minuts

## Prerequisits Generals

- Sistema aixecat (`../lifecycle/start.sh`)
- Qdrant operatiu
- Model d'embeddings BGE-M3 disponible

## Ordre Recomanat

1. `ingest_sas_protocols.py` (essencial per demos i tests)
2. `ingest_medical_knowledge.py` (opcional, per funcionalitats avançades)
