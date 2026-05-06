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
NC='\033[0m' # No Color

# Funcions per imprimir
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

# Testejar Mistral 7B
print_status "Testeig Mistral 7B..."
echo ""

# Test 1: Discharge Summary
print_status "Test 1: Discharge Summary amb Mistral 7B"
curl -X POST "http://localhost:8000/generate/discharge-summary" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_context": "Home de 68 anys, masculí",
    "admission_reason": "Dolor toràcic",
    "hospital_course": "Pacient ingressat per dolor toràcic. Realitzades proves cardíaques. Diagnòstic: Infart agut de miocardi.",
    "discharge_condition": "Estable, milloria clínica",
    "medications": ["Aspirina 100mg", "Atorvastatina 40mg"],
    "follow_up_instructions": "Control per cardiologia en 1 setmana",
    "language": "ca"
  }' 2>/dev/null | jq '.' > /tmp/mistral_discharge.json

if [ -f /tmp/mistral_discharge.json ]; then
    print_success "Discharge Summary generat amb Mistral 7B"
    echo "Resultat guardat a /tmp/mistral_discharge.json"
    echo ""
else
    print_error "Error generant Discharge Summary"
fi

# Test 2: Referral
print_status "Test 2: Referral amb Mistral 7B"
curl -X POST "http://localhost:8000/generate/referral" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_context": "Home de 68 anys",
    "specialty": "Cardiologia",
    "reason": "Dolor toràcic persistent",
    "clinical_history": "Hipertensió arterial, dislipidèmia",
    "current_medications": ["Ramipril 5mg", "Atorvastatina 40mg"],
    "language": "ca"
  }' 2>/dev/null | jq '.' > /tmp/mistral_referral.json

if [ -f /tmp/mistral_referral.json ]; then
    print_success "Referral generat amb Mistral 7B"
    echo "Resultat guardat a /tmp/mistral_referral.json"
    echo ""
else
    print_error "Error generant Referral"
fi

# Test 3: Clinical Summary
print_status "Test 3: Clinical Summary amb Mistral 7B"
curl -X POST "http://localhost:8000/generate/clinical-summary" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_context": "Home de 68 anys",
    "current_symptoms": ["Dolor toràcic", "Dispnea"],
    "medications": ["Aspirina", "Atorvastatina"],
    "specialty": "Cardiologia",
    "language": "ca"
  }' 2>/dev/null | jq '.' > /tmp/mistral_clinical.json

if [ -f /tmp/mistral_clinical.json ]; then
    print_success "Clinical Summary generat amb Mistral 7B"
    echo "Resultat guardat a /tmp/mistral_clinical.json"
    echo ""
else
    print_error "Error generant Clinical Summary"
fi

echo ""
echo "=================================================="
print_success "Testeig completat!"
echo ""
echo "Resultats guardats a:"
echo "  - /tmp/mistral_discharge.json"
echo "  - /tmp/mistral_referral.json"
echo "  - /tmp/mistral_clinical.json"
echo ""
echo "Per veure els resultats:"
echo "  cat /tmp/mistral_discharge.json | jq '.data.discharge_document'"
echo "  cat /tmp/mistral_referral.json | jq '.data.referral_document'"
echo "  cat /tmp/mistral_clinical.json | jq '.data.clinical_summary'"
echo ""
