#!/bin/bash

# Healthcare RAG System Setup Script
# Installs and configures the complete system

set -e

echo "🏥 Healthcare RAG System Setup"
echo "=============================="

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

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This script is designed for macOS. Please adapt for your OS."
    exit 1
fi

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    print_error "Homebrew is required but not installed. Please install it first."
    exit 1
fi

print_status "Checking system requirements..."

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    print_status "Installing Ollama..."
    brew install ollama
    print_success "Ollama installed"
else
    print_success "Ollama already installed"
fi

# Check if OrbStack/Docker is running
if ! docker info &> /dev/null; then
    print_error "Docker/OrbStack is not running. Please start it first."
    exit 1
fi

print_success "Docker/OrbStack is running"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.11"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
    print_status "Installing Python 3.11..."
    brew install python@3.11
    print_success "Python 3.11 installed"
else
    print_success "Python 3.11+ is available"
fi

# Start Ollama service
print_status "Starting Ollama service..."
brew services start ollama
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
print_status "Creating Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

print_success "Python dependencies installed"

# Create necessary directories
print_status "Creating data directories..."
mkdir -p data/raw data/processed data/embeddings data/indexes data/qdrant_storage
mkdir -p config/ontologies

print_success "Data directories created"

# Start Qdrant with Docker
print_status "Starting Qdrant vector database..."
docker-compose up -d qdrant

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
docker-compose up -d api

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
python3 scripts/verify_setup.py

print_success "Healthcare RAG System setup completed successfully!"
echo ""
echo "🌐 Services available at:"
echo "  - Ollama: http://localhost:11434"
echo "  - Qdrant: http://localhost:6333"
echo "  - API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo ""
echo "🧪 Test the system:"
echo "  curl -X POST \"http://localhost:8000/query/\" \\"
echo "       -H \"Content-Type: application/json\" \\"
echo "       -d '{\"query\": \"¿Cuáles son los síntomas de la diabetes?\"}'"
echo ""
echo "📚 For more information, see README.md"
