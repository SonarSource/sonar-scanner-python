#!/bin/env bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
pushd "$SCRIPT_DIR/../its"

python3 -m venv .its-venv
source .its-venv/bin/activate
poetry install
pip install ..

poetry run pytest

popd
