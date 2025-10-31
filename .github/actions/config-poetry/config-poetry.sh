#!/bin/bash
# Config script for SonarSource Poetry projects.

set -euo pipefail

: "${ARTIFACTORY_URL:?}"
: "${ARTIFACTORY_PYPI_REPO:?}" "${ARTIFACTORY_ACCESS_TOKEN:?}" 
: "${BUILD_NUMBER:?}" "${GITHUB_REPOSITORY:?}" 

set_build_env() {
  export PROJECT=${GITHUB_REPOSITORY#*/}
  echo "PROJECT: $PROJECT"
}

config_poetry() {
  echo "config add repox"
  jf config add repox --artifactory-url "$ARTIFACTORY_URL" --access-token "$ARTIFACTORY_ACCESS_TOKEN" 
  echo "poetry-config"
  jf poetry-config --server-id-resolve repox --repo-resolve "$ARTIFACTORY_PYPI_REPO" 
  echo "poetry install"
  jf poetry install --build-name="$PROJECT" --build-number="$BUILD_NUMBER" -v
}

main() {
  set_build_env
  config_poetry
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
