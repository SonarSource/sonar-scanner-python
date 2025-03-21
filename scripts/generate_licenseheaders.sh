#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
pushd "$SCRIPT_DIR/.."

poetry run licenseheaders -t license_header.tmpl -o "SonarSource SA" -y 2011-2024 -n "Sonar Scanner Python" -E .py -d src/
poetry run licenseheaders -t license_header.tmpl -o "SonarSource SA" -y 2011-2024 -n "Sonar Scanner Python" -E .py -d tests/
poetry run licenseheaders -t license_header.tmpl -o "SonarSource SA" -y 2011-2024 -n "Sonar Scanner Python" -E .py -d its -x its/sources/**.py

popd
