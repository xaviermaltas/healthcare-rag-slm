# Healthcare RAG - Guia de Demostració

Guia completa per demostrar les funcionalitats del sistema Healthcare RAG.

---

## 🎯 Objectius de la Demostració

1. **Pipeline RAG complet** end-to-end
2. **Medical NER** amb diccionaris multiidioma
3. **Retrieval** amb traçabilitat de fonts
4. **Generació** amb LLM local (Mistral)
5. **Multiidioma** (espanyol, català)

---

## 📋 Prerequisites

```bash
# 1. Sistema aixecat
./scripts/start.sh

# 2. Verificar health
curl -s http://localhost:8000/health/detailed | python3 -m json.tool

# 3. Document de prova creat
ls data/raw/protocol_diabetes_test.txt
```

---

## 🚀 Demostració Completa (20 min)

### **Pas 1: Upload Document (2 min)**

```bash
# Pujar document de prova
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@data/raw/protocol_diabetes_test.txt" \
  -F "language=es" \
  | python3 -m json.tool

# Output esperat:
# {
#   "document_id": "protocol_diabetes_test_txt",
#   "filename": "protocol_diabetes_test.txt",
#   "status": "processing",
#   "chunks_created": 18,
#   "message": "Document uploaded successfully. 18 chunks will be processed in background."
# }
```

**Espera 15-20 segons** mentre es processa en background.

```bash
# Verificar indexació
curl -s "http://localhost:8000/documents/" | python3 -m json.tool | head -50
```

---

### **Pas 2: Query Simple (3 min)**

```bash
# Query: Tractament primera línia
curl -X POST "http://localhost:8000/query/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cuál es el tratamiento de primera línea para diabetes tipo 2?",
    "top_k": 3,
    "language": "es"
  }' | python3 -m json.tool > /tmp/demo_query1.json

# Mostrar resposta
cat /tmp/demo_query1.json | jq -r '.response'

# Mostrar fonts
echo "========================================="
echo "FONTS UTILITZADES:"
echo "========================================="
cat /tmp/demo_query1.json | jq '.sources[] | {score: .score, content: .content[:100]}'

# Mostrar mètriques
echo ""
echo "========================================="
echo "MÈTRIQUES:"
echo "========================================="
cat /tmp/demo_query1.json | jq '{
  docs_found: .retrieval_stats.documents_found,
  top_score: .retrieval_stats.top_score,
  total_time: .generation_stats.total_time
}'
```

**Explicar:**
- Query → BGE-M3 embedding
- Vector search a Qdrant (top-3 chunks)
- Context enviat a Mistral LLM
- Resposta generada amb fonts traçables

---

### **Pas 3: Query Complexa (3 min)**

```bash
# Query complexa amb múltiples entitats
curl -X POST "http://localhost:8000/query/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Paciente con diabetes tipo 2 e insuficiencia cardíaca. ¿Qué tratamiento es más seguro: metformina o inhibidores SGLT2?",
    "top_k": 5,
    "temperature": 0.3,
    "language": "es"
  }' | python3 -m json.tool > /tmp/demo_query2.json

# Mostrar resposta
cat /tmp/demo_query2.json | jq -r '.response'

# Mostrar entitats detectades
echo ""
echo "========================================="
echo "ENTITATS MÈDIQUES DETECTADES:"
echo "========================================="
cat /tmp/demo_query2.json | jq '.medical_entities'
```

**Hauria de detectar:**
- DISEASE: diabetes tipo 2, insuficiencia cardíaca
- MEDICATION: metformina, inhibidores SGLT2

---

### **Pas 4: Medical NER (2 min)**

```bash
# Extracció d'entitats mèdiques
curl -X POST "http://localhost:8000/query/entities" \
  -H "Content-Type: application/json" \
  -d '{"query": "Paciente con diabetes tipo 2, hipertensión y dislipemia tratado con metformina, enalapril y atorvastatina"}' \
  | python3 -m json.tool

# Hauria de detectar:
# - DISEASE: diabetes tipo 2, hipertensión, dislipemia
# - MEDICATION: metformina, enalapril, atorvastatina
```

**Explicar:**
- NER custom amb diccionaris mèdics (es/ca)
- Detecta 6 tipus: DISEASE, MEDICATION, SYMPTOM, ANATOMY, PROCEDURE, SPECIALTY
- Base per futures integracions amb SNOMED CT

---

### **Pas 5: Cas d'Ús - Informe d'Alta (5 min)**

```bash
# Simular generació informe d'alta
curl -X POST "http://localhost:8000/query/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Generar informe de alta para paciente varón de 58 años ingresado por descompensación hiperglucémica. Diagnóstico: Diabetes mellitus tipo 2 de nuevo diagnóstico. HbA1c al ingreso: 11.2%. Glucemias capilares durante ingreso: 180-250 mg/dL. Se inicia tratamiento con metformina 850mg/12h e insulina glargina 14 UI nocturna. Educación diabetológica realizada. Alta con glucemia 145 mg/dL. Incluir: diagnóstico codificado, tratamiento al alta, recomendaciones y seguimiento.",
    "top_k": 8,
    "temperature": 0.3,
    "language": "es"
  }' | python3 -m json.tool > /tmp/demo_informe.json

# Mostrar informe generat
echo "========================================="
echo "INFORME D'ALTA GENERAT:"
echo "========================================="
cat /tmp/demo_informe.json | jq -r '.response'

echo ""
echo "========================================="
echo "FONTS UTILITZADES:"
echo "========================================="
cat /tmp/demo_informe.json | jq '.sources[] | {score: .score, content: .content[:80]}'

echo ""
echo "========================================="
echo "ENTITATS MÈDIQUES:"
echo "========================================="
cat /tmp/demo_informe.json | jq '.medical_entities'
```

**L'informe hauria d'incloure:**
1. **Diagnòstic principal**: Diabetes mellitus tipo 2
2. **Tractament al alta**: Metformina 850mg/12h + Insulina glargina 14 UI
3. **Recomanacions**: Dieta, exercici, automonitorització
4. **Seguiment**: Control HbA1c en 3 mesos

**Explicar:**
- Cas d'ús real: Informe d'alta hospitalària
- Impacte: 19.300 informes/any al SAS
- Reducció estimada: 10→6 min/informe = 1.285 hores/any
- Traçabilitat: fonts amb scores

---

### **Pas 6: Multiidioma (2 min)**

```bash
# Query en català
curl -X POST "http://localhost:8000/query/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Quin és el tractament de primera línia per a la diabetis tipus 2?",
    "top_k": 3,
    "language": "ca"
  }' | python3 -m json.tool | jq -r '.response'

# Hauria de respondre en català
```

**Explicar:**
- Suport multiidioma (es/ca/en)
- BGE-M3 embeddings multilingües
- Prompts adaptats per idioma

---

### **Pas 7: Retrieval Sense Generació (1 min)**

```bash
# Només retrieval (sense LLM) - més ràpid
curl -X POST "http://localhost:8000/query/retrieve?query=criterios%20diagnostico%20diabetes&top_k=3" \
  | python3 -m json.tool

# Retorna només els chunks recuperats sense generar resposta
# Útil per debugging o quan no necessites generació
```

---

## 📊 Anàlisi de Resultats

### **Script d'Anàlisi**

```bash
# Crear script d'anàlisi
cat > /tmp/analyze_results.sh << 'SCRIPT'
#!/bin/bash

echo "========================================="
echo "ANÀLISI DE RESULTATS - HEALTHCARE RAG"
echo "========================================="

echo ""
echo "Query 1 (Simple):"
cat /tmp/demo_query1.json | jq '{
  response_length: (.response | length),
  sources_count: (.sources | length),
  top_score: .retrieval_stats.top_score,
  total_time: .generation_stats.total_time
}'

echo ""
echo "Query 2 (Complexa):"
cat /tmp/demo_query2.json | jq '{
  response_length: (.response | length),
  sources_count: (.sources | length),
  entities_count: (.medical_entities | length),
  top_score: .retrieval_stats.top_score,
  total_time: .generation_stats.total_time
}'

echo ""
echo "Informe Alta:"
cat /tmp/demo_informe.json | jq '{
  response_length: (.response | length),
  sources_count: (.sources | length),
  entities_count: (.medical_entities | length),
  avg_score: .retrieval_stats.avg_score,
  total_time: .generation_stats.total_time
}'

echo "========================================="
SCRIPT

chmod +x /tmp/analyze_results.sh
/tmp/analyze_results.sh
```

---

## ✅ Verificació Final

### **Health Check Complet**

```bash
# Verificar estat de tots els components
curl -s "http://localhost:8000/health/detailed" | python3 -m json.tool

# Hauries de veure tot "healthy":
# {
#   "status": "healthy",
#   "components": {
#     "ollama": {
#       "status": "healthy",
#       "model": "mistral"
#     },
#     "qdrant": {
#       "status": "healthy",
#       "collections": 1,
#       "vectors_count": 18
#     },
#     "embeddings": {
#       "status": "healthy",
#       "model": "BAAI/bge-m3",
#       "device": "cpu"
#     }
#   }
# }
```

---

### **Estadístiques del Sistema**

```bash
# Veure estadístiques de Qdrant
curl -s "http://localhost:8000/collections/healthcare_rag/stats" \
  | python3 -m json.tool

# Hauries de veure:
# {
#   "vectors_count": 18,
#   "indexed_vectors_count": 18,
#   "points_count": 18,
#   "segments_count": 1
# }
```

---

## 🧹 Cleanup (Opcional)

```bash
# Si vols parar el sistema
./scripts/stop.sh

# Si vols eliminar les dades (ATENCIÓ: elimina tot)
docker-compose -f deploy/compose/docker-compose.yml down -v

# Si vols mantenir-lo running per més proves
# → No facis res, deixa'l running
```

---

## 📊 Resum de la Demostració

### **Proves Realitzades**

| # | Prova | Endpoint | Temps | Resultat |
|---|-------|----------|-------|----------|
| 1 | Upload document | `POST /documents/upload` | ~15s | ✅ 18 chunks indexats |
| 2 | Query simple | `POST /query/` | ~7s | ✅ Resposta correcta |
| 3 | Query complexa | `POST /query/` | ~8s | ✅ Resposta detallada |
| 4 | Medical NER | `POST /query/entities` | ~0.5s | ✅ 6 entitats |
| 5 | Informe alta | `POST /query/` | ~10s | ✅ Informe complet |
| 6 | Multiidioma | `POST /query/` | ~7s | ✅ Resposta en català |
| 7 | Retrieval només | `POST /query/retrieve` | ~2s | ✅ 3 chunks |

---

### **Mètriques Obtingudes**

| Mètrica | Valor | Objectiu | Estat |
|---------|-------|----------|-------|
| **Precisió retrieval** | 0.72-0.85 | >0.7 | ✅ |
| **Latència query** | 7-10s | <5s | 🟡 |
| **Documents indexats** | 18 chunks | - | ✅ |
| **Entitats detectades** | 6/6 | - | ✅ |
| **Multiidioma** | es, ca | - | ✅ |

---

## 🎯 Punts Clau per la Reunió

### **Funcionalitats Demostrades**

1. ✅ **Pipeline RAG complet**: Upload → Chunking → Embeddings → Retrieval → Generation
2. ✅ **Medical NER**: Detecció automàtica d'entitats mèdiques (DISEASE, MEDICATION, SYMPTOM, etc.)
3. ✅ **Multiidioma**: Suport espanyol i català
4. ✅ **Traçabilitat**: Fonts amb scores de rellevància
5. ✅ **Cas d'ús real**: Generació informe d'alta hospitalària
6. ✅ **Retrieval flexible**: Amb o sense generació LLM
7. ✅ **Extracció entitats**: Endpoint dedicat per NER

---

### **Arquitectura Implementada**

```
Document (PDF/TXT)
    ↓
Chunking Semàntic (18 chunks)
    ↓
BGE-M3 Embeddings (1024-dim)
    ↓
Qdrant Vector DB
    ↓
Query + Medical NER
    ↓
Vector Search (top-K)
    ↓
Mistral LLM Generation
    ↓
Response + Sources + Entitats Mèdiques
```

---

### **Següents Passos**

1. **Integració SNOMED CT**: Anotació semàntica amb codis internacionals (implementat, pendent integració pipeline)
2. **Reranking**: Cross-encoder per millorar precisió
3. **Prompts específics**: Plantilles per informe alta/derivació/resum
4. **Corpus SAS**: Protocols reals del Servei Andalús de Salut
5. **Avaluació**: Mètriques BLEU, ROUGE, BERTScore
6. **Optimització**: Reducció latència <5s

---

## 📚 Recursos Addicionals

- **Documentació API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health/detailed
- **Arquitectura**: `docs/ARCHITECTURE.md`
- **Setup**: `docs/SETUP.md`

---

**Document preparat per:** Xavier Maltas Tarridas  
**Data:** Abril 2026  
**Versió:** 2.0 (Unificat)
