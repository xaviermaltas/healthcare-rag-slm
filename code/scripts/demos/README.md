# 🎭 Demo Scripts

Demos interactives dels casos d'ús del sistema Healthcare RAG.

## Demos Disponibles

### `demo_discharge_summary.py`
Demo interactiva de generació automàtica d'informes d'alta hospitalària.

**Cas clínic**: Infart Agut de Miocardi (IAMCEST)

**Què mostra**:
- Context del pacient i motiu d'ingrés
- Procediments realitzats
- Medicació actual
- Generació automàtica de l'informe
- Protocols SAS consultats
- Validació de l'informe
- Mètriques de rendiment
- Beneficis i impacte estimat

**Ús**:
```bash
../utils/activate_and_run.sh python demo_discharge_summary.py
```

**Durada**: ~45-50 segons

**Característiques**:
- ✅ Cas clínic real i complet
- ✅ Interactiu (pausa abans de generar)
- ✅ Mostra tot el procés pas a pas
- ✅ Visualització de resultats formatada
- ✅ Mètriques de temps i qualitat

## Prerequisits

- Sistema aixecat (`../lifecycle/start.sh`)
- Protocols SAS indexats (`../data/ingest_sas_protocols.py`)
- Model Llama3.2 disponible a Ollama

## Properes Demos

- `demo_referral_report.py` - Informe de derivació
- `demo_clinical_summary.py` - Resum clínic previ a consulta
