#!/bin/bash

# Script per AIXECAR el Frontend del Healthcare RAG System
# Utilitza fnm per gestionar Node.js i arrenca el servidor de desenvolupament

set -e

echo "🎨 Healthcare RAG System - Aixecant Frontend"
echo "=============================================="
echo ""

# Colors per output
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

# Navegar al directori arrel del projecte
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

print_status "Directori del projecte: $PROJECT_ROOT"
print_status "Directori del frontend: $FRONTEND_DIR"
echo ""

# Verificar que el directori frontend existeix
if [ ! -d "$FRONTEND_DIR" ]; then
    print_error "El directori frontend no existeix: $FRONTEND_DIR"
    exit 1
fi

cd "$FRONTEND_DIR"

# Verificar fnm
print_status "Verificant fnm (Fast Node Manager)..."
if ! command -v fnm &> /dev/null; then
    print_error "fnm no està instal·lat"
    echo ""
    echo "Instal·la fnm amb:"
    echo "  brew install fnm"
    echo "  echo 'eval \"\$(fnm env --use-on-cd)\"' >> ~/.zshrc"
    echo "  source ~/.zshrc"
    exit 1
fi

print_success "fnm està instal·lat"

# Configurar fnm per aquesta sessió
eval "$(fnm env --use-on-cd)"

# Verificar Node.js
print_status "Verificant Node.js..."
if ! command -v node &> /dev/null; then
    print_warning "Node.js no està instal·lat"
    print_status "Instal·lant Node.js LTS amb fnm..."
    fnm install --lts
    fnm default lts-latest
    print_success "Node.js instal·lat: $(node --version)"
else
    print_success "Node.js disponible: $(node --version)"
fi

# Verificar npm
if ! command -v npm &> /dev/null; then
    print_error "npm no està disponible"
    exit 1
fi

print_success "npm disponible: $(npm --version)"
echo ""

# Verificar si node_modules existeix
if [ ! -d "node_modules" ]; then
    print_warning "node_modules no trobat. Instal·lant dependències..."
    npm install
    print_success "Dependències instal·lades"
else
    print_success "node_modules trobat"
fi

echo ""

# Verificar fitxer .env.local
if [ ! -f ".env.local" ]; then
    print_warning ".env.local no trobat"
    if [ -f ".env.example" ]; then
        print_status "Copiant .env.example a .env.local..."
        cp .env.example .env.local
        print_success ".env.local creat"
    else
        print_warning "Creant .env.local amb configuració per defecte..."
        echo "VITE_API_URL=http://localhost:8000" > .env.local
        print_success ".env.local creat"
    fi
else
    print_success ".env.local trobat"
fi

echo ""

# Verificar que el backend està corrent
print_status "Verificant backend API..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    print_success "Backend API està actiu (http://localhost:8000)"
else
    print_warning "Backend API no respon a http://localhost:8000"
    print_warning "Assegura't que el backend està corrent abans de fer requests"
    echo ""
    echo "Per aixecar el backend, executa:"
    echo "  cd $PROJECT_ROOT"
    echo "  ./scripts/lifecycle/start.sh"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print_success "Frontend preparat per arrencar!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
print_status "Arrencant servidor de desenvolupament..."
print_status "URL: http://localhost:5173"
echo ""
print_warning "Prem Ctrl+C per aturar el servidor"
echo ""

# Arrencar el servidor de desenvolupament
npm run dev
