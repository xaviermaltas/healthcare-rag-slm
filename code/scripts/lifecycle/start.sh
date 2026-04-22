#!/bin/bash

# Script per AIXECAR el sistema Healthcare RAG
# Manté volums i dades existents
# Aixeca Ollama si no està executant-se

set -e

echo "🚀 Healthcare RAG System - Aixecant Sistema"
echo "=============================================="
echo ""

# Navegar al directori arrel del projecte
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

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

# Comprovar i iniciar Ollama si cal
echo "🤖 Verificant Ollama..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama no està executant-se. Iniciant..."
    
    # Intentar iniciar Ollama amb brew services
    if command -v brew &> /dev/null; then
        brew services start ollama
        echo "   Esperant que Ollama s'iniciï..."
        sleep 5
        
        # Verificar que s'ha iniciat
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            echo "✅ Ollama iniciat correctament"
        else
            echo "⚠️  Ollama no respon. Pot ser que necessitis executar 'ollama serve' manualment"
        fi
    else
        echo "⚠️  No es pot iniciar Ollama automàticament"
        echo "   Executa manualment: ollama serve"
    fi
else
    echo "✅ Ollama ja està executant-se"
fi

echo ""

# Navegar al directori de compose
cd deploy/compose

# Aixecar contenidors (sense rebuild, mantenint volums)
echo "🐳 Aixecant contenidors Docker..."
docker compose up -d

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

# Comprovar Ollama
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama: OK"
else
    echo "⚠️  Ollama: No respon"
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
echo "   - Ollama: http://localhost:11434"
echo ""
echo "📝 Per veure logs:"
echo "   docker logs -f healthcare-rag-api"
echo ""
echo "🛑 Per aturar el sistema:"
echo "   ./scripts/lifecycle/stop.sh"
echo ""
echo "🔨 Per reconstruir des de zero:"
echo "   ./scripts/lifecycle/rebuild.sh"
echo "=============================================="
