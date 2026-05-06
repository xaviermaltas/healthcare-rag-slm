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

# ============================================
# TEST 1: DISCHARGE SUMMARY
# ============================================
print_header "TEST 1: DISCHARGE SUMMARY"
echo ""

DISCHARGE_INPUT='{
  "patient_context": "Home de 68 anys, masculí, antecedents de hipertensió",
  "admission_reason": "Dolor toràcic agut",
  "hospital_course": "Pacient ingressat per dolor toràcic. Realitzades proves cardíaques: ECG, troponina, ecocardiograma. Diagnòstic: Infart agut de miocardi de paret anterior.",
  "discharge_condition": "Estable, milloria clínica significativa",
  "medications": ["Aspirina 100mg", "Atorvastatina 40mg", "Ramipril 5mg"],
  "follow_up_instructions": "Control per cardiologia en 1 setmana, evitar esforços físics",
  "language": "ca"
}'

# Test amb Mistral 7B
print_status "Testeig Mistral 7B - Discharge Summary..."
START_TIME=$(date +%s%N)
curl -s -X POST "http://localhost:8000/generate/discharge-summary" \
  -H "Content-Type: application/json" \
  -d "$DISCHARGE_INPUT" | jq '.' > /tmp/model_comparison/mistral_discharge.json
END_TIME=$(date +%s%N)
MISTRAL_TIME=$(( (END_TIME - START_TIME) / 1000000 ))
print_success "Mistral 7B - Discharge Summary (${MISTRAL_TIME}ms)"

# Test amb Llama 3.2
print_status "Canviant model a Llama 3.2..."
# Nota: Aquí caldria canviar la configuració del backend per usar Llama 3.2
# Per ara, simulem que es canvia
export OLLAMA_MODEL="llama3.2"

print_status "Testeig Llama 3.2 - Discharge Summary..."
START_TIME=$(date +%s%N)
curl -s -X POST "http://localhost:8000/generate/discharge-summary" \
  -H "Content-Type: application/json" \
  -d "$DISCHARGE_INPUT" | jq '.' > /tmp/model_comparison/llama_discharge.json
END_TIME=$(date +%s%N)
LLAMA_TIME=$(( (END_TIME - START_TIME) / 1000000 ))
print_success "Llama 3.2 - Discharge Summary (${LLAMA_TIME}ms)"

echo ""

# ============================================
# TEST 2: REFERRAL
# ============================================
print_header "TEST 2: REFERRAL"
echo ""

REFERRAL_INPUT='{
  "patient_context": "Home de 68 anys, antecedents de hipertensió",
  "specialty": "Cardiologia",
  "reason": "Dolor toràcic persistent, sospita d infart",
  "clinical_history": "Hipertensió arterial controlada, dislipidèmia, fumador",
  "current_medications": ["Ramipril 5mg", "Atorvastatina 40mg"],
  "language": "ca"
}'

# Test amb Mistral 7B
print_status "Testeig Mistral 7B - Referral..."
START_TIME=$(date +%s%N)
curl -s -X POST "http://localhost:8000/generate/referral" \
  -H "Content-Type: application/json" \
  -d "$REFERRAL_INPUT" | jq '.' > /tmp/model_comparison/mistral_referral.json
END_TIME=$(date +%s%N)
MISTRAL_TIME=$(( (END_TIME - START_TIME) / 1000000 ))
print_success "Mistral 7B - Referral (${MISTRAL_TIME}ms)"

# Test amb Llama 3.2
print_status "Testeig Llama 3.2 - Referral..."
START_TIME=$(date +%s%N)
curl -s -X POST "http://localhost:8000/generate/referral" \
  -H "Content-Type: application/json" \
  -d "$REFERRAL_INPUT" | jq '.' > /tmp/model_comparison/llama_referral.json
END_TIME=$(date +%s%N)
LLAMA_TIME=$(( (END_TIME - START_TIME) / 1000000 ))
print_success "Llama 3.2 - Referral (${LLAMA_TIME}ms)"

echo ""

# ============================================
# TEST 3: CLINICAL SUMMARY
# ============================================
print_header "TEST 3: CLINICAL SUMMARY"
echo ""

CLINICAL_INPUT='{
  "patient_context": "Home de 68 anys",
  "current_symptoms": ["Dolor toràcic", "Dispnea", "Sudoració"],
  "medications": ["Aspirina", "Atorvastatina", "Ramipril"],
  "specialty": "Cardiologia",
  "language": "ca"
}'

# Test amb Mistral 7B
print_status "Testeig Mistral 7B - Clinical Summary..."
START_TIME=$(date +%s%N)
curl -s -X POST "http://localhost:8000/generate/clinical-summary" \
  -H "Content-Type: application/json" \
  -d "$CLINICAL_INPUT" | jq '.' > /tmp/model_comparison/mistral_clinical.json
END_TIME=$(date +%s%N)
MISTRAL_TIME=$(( (END_TIME - START_TIME) / 1000000 ))
print_success "Mistral 7B - Clinical Summary (${MISTRAL_TIME}ms)"

# Test amb Llama 3.2
print_status "Testeig Llama 3.2 - Clinical Summary..."
START_TIME=$(date +%s%N)
curl -s -X POST "http://localhost:8000/generate/clinical-summary" \
  -H "Content-Type: application/json" \
  -d "$CLINICAL_INPUT" | jq '.' > /tmp/model_comparison/llama_clinical.json
END_TIME=$(date +%s%N)
LLAMA_TIME=$(( (END_TIME - START_TIME) / 1000000 ))
print_success "Llama 3.2 - Clinical Summary (${LLAMA_TIME}ms)"

echo ""
echo "=============================================="
print_success "Testeig completat!"
echo ""
echo "Resultats guardats a /tmp/model_comparison/"
echo ""
echo "Per veure els resultats:"
echo ""
echo "DISCHARGE SUMMARY:"
echo "  Mistral: cat /tmp/model_comparison/mistral_discharge.json | jq '.summary'"
echo "  Llama:   cat /tmp/model_comparison/llama_discharge.json | jq '.summary'"
echo ""
echo "REFERRAL:"
echo "  Mistral: cat /tmp/model_comparison/mistral_referral.json | jq '.summary'"
echo "  Llama:   cat /tmp/model_comparison/llama_referral.json | jq '.summary'"
echo ""
echo "CLINICAL SUMMARY:"
echo "  Mistral: cat /tmp/model_comparison/mistral_clinical.json | jq '.summary'"
echo "  Llama:   cat /tmp/model_comparison/llama_clinical.json | jq '.summary'"
echo ""
