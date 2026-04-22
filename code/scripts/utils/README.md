# 🛠️ Utility Scripts

Utilitats generals per al sistema Healthcare RAG.

## Scripts Disponibles

### `activate_and_run.sh`
Executa scripts Python amb l'entorn virtual activat automàticament.

**Ús**:
```bash
./activate_and_run.sh python <script.py>
./activate_and_run.sh pytest tests/
```

**Característiques**:
- ✅ Activa l'entorn virtual automàticament
- ✅ Executa la comanda especificada
- ✅ Desactiva l'entorn després
- ✅ Mostra la versió de Python utilitzada

**Exemples**:
```bash
# Executar un script
./activate_and_run.sh python ../data/ingest_sas_protocols.py

# Executar tests
./activate_and_run.sh pytest ../../tests/

# Executar demo
./activate_and_run.sh python ../demos/demo_discharge_summary.py
```

---

### `verify_setup.py`
Verifica que tot el sistema està correctament configurat.

**Què verifica**:
- ✅ Versió de Python
- ✅ Paquets Python instal·lats
- ✅ Estructura de directoris
- ✅ Fitxers de configuració
- ✅ Connexió a Ollama
- ✅ Connexió a Qdrant
- ✅ Connexió a l'API
- ✅ Model d'embeddings

**Ús**:
```bash
./activate_and_run.sh python verify_setup.py
```

**Output**:
- Mostra resultat de cada verificació
- Resum final amb tests passats/fallats
- Missatge d'èxit si tot està correcte

**Quan usar-lo**:
- Després de `bootstrap.sh`
- Abans de començar a treballar
- Per diagnosticar problemes
- Després de canvis de configuració

## Notes

Aquests scripts són utilitzats per altres scripts del sistema. No cal executar-los directament normalment, excepte `verify_setup.py` per diagnòstic.
