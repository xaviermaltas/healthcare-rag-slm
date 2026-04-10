#!/bin/bash

# Healthcare RAG System Setup Script
# Installs and configures the complete system

set -e

echo "🏥 Healthcare RAG System Setup"
echo "=============================="
echo ""
echo "Prerequisits necessaris:"
echo "  ✔ macOS amb Homebrew (https://brew.sh)"
echo "  ✔ Docker o OrbStack en execució (https://orbstack.dev)"
echo "  ✔ Python 3.11+ instal·lat"
echo ""
echo "Aquest script crearà l'entorn virtual 'healthcare-rag-env'."
echo "Un cop instal·lat, SEMPRE usa aquest intèrpret Python:"
echo "  ./healthcare-rag-env/bin/python3"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

print_status "Checking system requirements..."

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    print_warning "Ollama not found. Install it from https://ollama.com/download"
    if [[ "$OSTYPE" == "darwin"* ]] && command -v brew &> /dev/null; then
        print_status "Installing Ollama via Homebrew..."
        brew install ollama
        print_success "Ollama installed"
    else
        print_error "Please install Ollama manually and re-run this script."
        exit 1
    fi
else
    print_success "Ollama already installed"
fi

# Check if OrbStack/Docker is running
if ! docker info &> /dev/null; then
    print_error "Docker/OrbStack is not running. Please start it first."
    exit 1
fi

print_success "Docker/OrbStack is running"

# Check Python version (3.11+)
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
    print_error "Python 3.11+ is required. Current: $(python3 --version 2>&1)"
    print_error "Install from https://www.python.org/downloads/ or via Homebrew: brew install python@3.12"
    exit 1
else
    print_success "Python $(python3 --version 2>&1 | cut -d' ' -f2) available"
fi

# Start Ollama service
print_status "Starting Ollama service..."
if [[ "$OSTYPE" == "darwin"* ]] && command -v brew &> /dev/null; then
    brew services start ollama
else
    ollama serve &>/dev/null &
fi
sleep 3

# Download required models
print_status "Downloading Mistral model (this may take a few minutes)..."
ollama pull mistral

print_status "Downloading Llama 3.2 model..."
ollama pull llama3.2

# Verify Ollama is working
print_status "Testing Ollama connection..."
if curl -s http://localhost:11434/api/tags > /dev/null; then
    print_success "Ollama is accessible on localhost:11434"
else
    print_error "Ollama connection failed"
    exit 1
fi

# Create Python virtual environment
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_NAME="healthcare-rag-env"

print_status "Creating Python virtual environment ($VENV_NAME)..."
python3 -m venv "$PROJECT_ROOT/$VENV_NAME"
source "$PROJECT_ROOT/$VENV_NAME/bin/activate"

# Install Python dependencies
print_status "Installing Python dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r "$PROJECT_ROOT/requirements.txt"

# Set up .env if not present
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    print_status "Creating .env from .env.example..."
    cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
    print_warning "Review and edit .env with your API keys before running the system"
else
    print_success ".env already exists"
fi

print_success "Python dependencies installed"

# Create necessary directories
print_status "Creating data directories..."
mkdir -p data/raw data/processed data/embeddings data/indexes data/qdrant_storage
mkdir -p config/ontologies

print_success "Data directories created"

# Start Qdrant with Docker
COMPOSE_FILE="$PROJECT_ROOT/deploy/compose/docker-compose.yml"
print_status "Starting Qdrant vector database..."
docker compose -f "$COMPOSE_FILE" up -d qdrant

# Wait for Qdrant to be ready
print_status "Waiting for Qdrant to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:6333/healthz > /dev/null; then
        print_success "Qdrant is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Qdrant failed to start"
        exit 1
    fi
    sleep 2
done

# Build and start API service
print_status "Building and starting API service..."
docker compose -f "$COMPOSE_FILE" up -d api

# Wait for API to be ready
print_status "Waiting for API to be ready..."
for i in {1..60}; do
    if curl -s http://localhost:8000/health/live > /dev/null; then
        print_success "API is ready"
        break
    fi
    if [ $i -eq 60 ]; then
        print_error "API failed to start"
        exit 1
    fi
    sleep 2
done

# Run system verification
print_status "Running system verification..."
python3 "$PROJECT_ROOT/scripts/verify_setup.py"

print_success "Healthcare RAG System setup completed successfully!"
echo ""
echo "🌐 Serveis disponibles:"
echo "  - Ollama: http://localhost:11434"
echo "  - Qdrant: http://localhost:6333"
echo "  - API:    http://localhost:8000"
echo "  - Docs:   http://localhost:8000/docs"
echo ""
echo "🐍 Entorn virtual creat a: $PROJECT_ROOT/$VENV_NAME"
echo ""
echo "   Per activar-lo manualment:"
echo "   source $PROJECT_ROOT/$VENV_NAME/bin/activate"
echo ""
echo "   O usa l'script d'execució directa (sense activar):"
echo "   ./scripts/activate_and_run.sh python3 src/test/unit/core/test_core_components.py"
echo "   ./scripts/activate_and_run.sh pytest src/test/ -v"
echo ""
echo "⚠️  IMPORTANT — Intèrpret Python per al teu IDE (Windsurf/VS Code):"
echo "   Selecciona manualment: $PROJECT_ROOT/$VENV_NAME/bin/python3"
echo "   Cmd+Shift+P → 'Python: Select Interpreter' → Enter interpreter path"
echo ""
echo "📚 Més informació: README.md"
