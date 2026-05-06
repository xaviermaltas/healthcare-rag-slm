#!/bin/bash

# Script per testejar models LLM
# Compara Mistral 7B vs Llama 3.2

set -e

echo "🧪 Healthcare RAG System - Model Testing Script"
echo "=================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que Ollama està corrent
print_status "Verificant Ollama..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    print_error "Ollama no està corrent a http://localhost:11434"
    echo "Inicia Ollama amb: ollama serve"
    exit 1
fi
print_success "Ollama està corrent"

# Verificar models disponibles
print_status "Verificant models disponibles..."
MODELS=$(curl -s http://localhost:11434/api/tags | jq -r '.models[].name')
echo "Models disponibles:"
echo "$MODELS"
echo ""

# Verificar que backend està corrent
print_status "Verificant backend API..."
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    print_warning "Backend API no està corrent a http://localhost:8000"
    echo "Inicia el backend amb: cd code && python -m uvicorn src.main.api.main:app --reload"
    echo ""
fi

echo ""
echo "=================================================="
print_success "Verificació completada!"
echo ""
echo "Per executar els tests:"
echo "  ./code/scripts/utils/activate_and_run.sh python3 code/scripts/test_both_models.py"
echo ""
