#!/bin/bash
# Script to run ontology integration tests
# This is a SCRIPT (not a test) that executes the actual tests

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "🧪 Running Ontology Integration Tests"
echo "======================================"
echo ""

# Activate virtual environment and run tests
./scripts/activate_and_run.sh python3 tests/integration/test_ontologies_integration.py

echo ""
echo "✅ Tests completed!"
