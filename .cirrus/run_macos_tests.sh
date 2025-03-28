#!/bin/bash
set -euo pipefail

if [ $# -eq 0 ]; then
    echo "No arguments supplied"
fi

PYTHON_VERSION="$1"
echo "========================================================================"
echo "Running tests on macOS with Python version: $PYTHON_VERSION"
echo "========================================================================"
uv python install ${PYTHON_VERSION} --default --preview
poetry run python --version
poetry install
poetry run pytest tests/
