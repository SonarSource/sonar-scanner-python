#!/usr/bin/env bash
set -euo pipefail

unzip -q sonarqube_cache/sonarqube.zip -d sonarqube

PLATFORM="linux-x86-64"
if [[ "$(uname)" == "Darwin" ]]; then
  PLATFORM="macosx-universal-64"
fi

cd $(ls -d sonarqube/*/)
./bin/${PLATFORM}/sonar.sh start
cd -

unset SONAR_TOKEN
unset SONAR_HOST_URL

poetry install 
poetry run pytest --its tests/its
