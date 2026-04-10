#!/bin/bash
# Activa el virtualenv del projecte i executa la comanda passada com a argument.
# Ús: ./scripts/activate_and_run.sh <comanda>
# Exemples:
#   ./scripts/activate_and_run.sh python3 src/test/unit/core/test_core_components.py
#   ./scripts/activate_and_run.sh python3 src/test/integration/api/test_embeddings.py
#   ./scripts/activate_and_run.sh pytest src/test/ -v

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV="$PROJECT_ROOT/healthcare-rag-env"

# Comprova que el venv existeix
if [ ! -f "$VENV/bin/activate" ]; then
  echo "ERROR: No s'ha trobat el virtualenv a $VENV"
  exit 1
fi

# Activa el venv
source "$VENV/bin/activate"
echo "Venv activat: $(python3 --version) | $(which python3)"
echo ""

# Exporta PYTHONPATH perquè els imports de src.main.* funcionin
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Executa la comanda passada com a arguments
exec "$@"
