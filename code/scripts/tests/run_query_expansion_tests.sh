#!/bin/bash
# Script to run query expansion integration tests

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

echo "🧪 Running Query Expansion Integration Tests"
echo "=============================================="
echo ""

# Activate virtual environment and run tests
./scripts/utils/activate_and_run.sh python3 tests/integration/test_query_expansion_integration.py

echo ""
echo "✅ Tests completed!"
