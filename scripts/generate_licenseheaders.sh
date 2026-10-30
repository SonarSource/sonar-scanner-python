#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
pushd "$SCRIPT_DIR/.."

uv run --locked --no-build licenseheaders -t license_header.tmpl -o "SonarSource Sàrl" -y 2011-2026 -n "Sonar Scanner Python" -E .py -d src/
uv run --locked --no-build licenseheaders -t license_header.tmpl -o "SonarSource Sàrl" -y 2011-2026 -n "Sonar Scanner Python" -E .py -d tests/

popd
