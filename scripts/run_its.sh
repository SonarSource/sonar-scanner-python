#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."
SONARQUBE_VERSION="${SONARQUBE_VERSION:-25.3.0.104237}"
ARCHIVE="sonarqube_cache/sonarqube-${SONARQUBE_VERSION}.zip"

case "$(uname)" in
  Linux) PLATFORM="linux-x86-64" ;;
  Darwin) PLATFORM="macosx-universal-64" ;;
  *) echo "Integration tests require Linux or macOS." >&2; exit 1 ;;
esac

unset SONAR_TOKEN SONAR_HOST_URL
poetry install

mkdir -p sonarqube_cache
if [[ ! -f "$ARCHIVE" ]]; then
  curl --fail --location "https://repo.maven.apache.org/maven2/org/sonarsource/sonarqube/sonar-application/${SONARQUBE_VERSION}/sonar-application-${SONARQUBE_VERSION}.zip" -o "$ARCHIVE.part"
  mv "$ARCHIVE.part" "$ARCHIVE"
fi

RUN_DIR=$(mktemp -d "${TMPDIR:-/tmp}/pysonar-its.XXXXXX")
unzip -q "$ARCHIVE" -d "$RUN_DIR"
SONAR_SCRIPT="$RUN_DIR/sonarqube-${SONARQUBE_VERSION}/bin/${PLATFORM}/sonar.sh"

# Stop the test server and remove its temporary files when the script exits.
trap '"$SONAR_SCRIPT" stop || true; rm -rf "$RUN_DIR"' EXIT

"$SONAR_SCRIPT" start

poetry run pytest --its tests/its "$@"
