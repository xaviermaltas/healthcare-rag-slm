#!/bin/bash

# Script per ATURAR el sistema Healthcare RAG
# Manté volums i dades existents
# Opcionalment atura Ollama

set -e

echo "🛑 Healthcare RAG System - Aturant Sistema"
echo "=============================================="
echo ""

# Navegar al directori arrel del projecte
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "📂 Directori actual: $(pwd)"
echo ""

# Aturar contenidors Docker (mantenint volums)
echo "🐳 Aturant contenidors Docker..."
cd deploy/compose
docker-compose stop

echo ""
echo "📊 Estat dels contenidors:"
docker ps -a --filter "name=healthcare-rag"

echo ""
echo "💾 Volums preservats:"
docker volume ls --filter "name=healthcare-rag" 2>/dev/null || echo "   (No hi ha volums amb nom healthcare-rag)"

echo ""

# Preguntar si vol aturar Ollama
read -p "🤖 Vols aturar Ollama també? (s/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[SsYy]$ ]]; then
    echo "🛑 Aturant Ollama..."
    if command -v brew &> /dev/null; then
        brew services stop ollama
        echo "✅ Ollama aturat"
    else
        echo "⚠️  No es pot aturar Ollama automàticament"
        echo "   Si Ollama s'està executant manualment, atura'l amb Ctrl+C"
    fi
else
    echo "ℹ️  Ollama segueix executant-se"
fi

echo ""
echo "=============================================="
echo "✅ Sistema aturat correctament!"
echo ""
echo "📝 Nota: Els volums i dades s'han mantingut"
echo ""
echo "🚀 Per tornar a aixecar el sistema:"
echo "   ./scripts/lifecycle/start.sh"
echo ""
echo "🗑️  Per eliminar tot (incloent volums):"
echo "   cd deploy/compose && docker-compose down -v"
echo "=============================================="
