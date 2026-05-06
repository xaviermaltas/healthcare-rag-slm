#!/bin/bash

# Script per comparar models LLM
# Compara Mistral 7B vs Llama 3.2 amb mateixos inputs

set -e

echo "🧪 Healthcare RAG System - Model Comparison"
echo "=============================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_header() {
    echo -e "${CYAN}=== $1 ===${NC}"
}

# Verificar que Ollama està corrent
print_status "Verificant Ollama..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    print_error "Ollama no està corrent"
    exit 1
fi
print_success "Ollama està corrent"

# Verificar que backend està corrent
print_status "Verificant backend API..."
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    print_error "Backend API no està corrent a http://localhost:8000"
    exit 1
fi
print_success "Backend API està corrent"

# Crear directori per resultats
mkdir -p /tmp/model_comparison
print_success "Directori de resultats creat: /tmp/model_comparison"
echo ""

echo "=============================================="
print_success "Verificacions completades!"
echo ""
echo "Executa els tests amb:"
echo "  ./code/scripts/utils/activate_and_run.sh python3 code/scripts/test_both_models.py"
echo ""
