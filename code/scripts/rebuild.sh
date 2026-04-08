#!/bin/bash

# Script per RECONSTRUIR el sistema Healthcare RAG des de zero
# ATENCIÓ: Aquest script elimina contenidors i reconstrueix imatges
# Usa start.sh per aixecar el sistema mantenint volums

set -e

echo "🔨 Healthcare RAG System - Reconstrucció Completa"
echo "=============================================="
echo "⚠️  ATENCIÓ: Aquest script reconstruirà tot des de zero"
echo ""

# Navegar al directori arrel del projecte
cd "$(dirname "$0")/.."

echo "📂 Directori actual: $(pwd)"
echo ""

# Comprovar si Docker està executant-se
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker no està executant-se"
    echo "   Si us plau, inicia Docker Desktop o OrbStack"
    exit 1
fi

echo "✅ Docker està executant-se"
echo ""

# Comprovar si Ollama està executant-se
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Advertència: Ollama no sembla estar executant-se"
    echo "   Executa: ollama serve"
    echo ""
fi

# Navegar al directori de compose
cd deploy/compose

echo "🛑 Aturant contenidors anteriors..."
docker-compose down

echo ""
echo "🔨 Construint imatges Docker..."
docker-compose build --no-cache

echo ""
echo "🚀 Aixecant contenidors..."
docker-compose up -d

echo ""
echo "⏳ Esperant que els serveis estiguin llestos..."
sleep 5

echo ""
echo "📊 Estat dels contenidors:"
docker ps --filter "name=healthcare-rag"

echo ""
echo "🔍 Verificant salut del sistema..."
echo ""

# Comprovar Qdrant
if curl -s http://localhost:6333/health > /dev/null 2>&1; then
    echo "✅ Qdrant: OK"
else
    echo "❌ Qdrant: Error"
fi

# Comprovar API
sleep 2
if curl -s http://localhost:8000/health/live > /dev/null 2>&1; then
    echo "✅ API: OK"
else
    echo "❌ API: Error"
fi

echo ""
echo "=============================================="
echo "✨ Sistema aixecat correctament!"
echo ""
echo "📍 Endpoints disponibles:"
echo "   - API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Qdrant: http://localhost:6333"
echo "   - Qdrant Dashboard: http://localhost:6333/dashboard"
echo ""
echo "📝 Per veure logs:"
echo "   docker logs -f healthcare-rag-api"
echo ""
echo "🛑 Per aturar el sistema:"
echo "   cd deploy/compose && docker-compose down"
echo "=============================================="
