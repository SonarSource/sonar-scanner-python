#!/usr/bin/env bash
set -euo pipefail

: "${BUILD_NUMBER:?}" "${GITHUB_ENV:?}"

uv lock --check
previous_lock=$(mktemp)
trap 'rm -f "$previous_lock"' EXIT
cp uv.lock "$previous_lock"
current_version=$(uv version --short)
project_version="${current_version}.${BUILD_NUMBER}"
uv version --no-sync "$project_version"

python - "$previous_lock" <<'PY'
import sys
import tomllib
from pathlib import Path


def dependencies(path):
    lock = tomllib.loads(Path(path).read_text())
    return [package for package in lock["package"] if package["name"] != "pysonar"]


if dependencies(sys.argv[1]) != dependencies("uv.lock"):
    sys.exit("Version stamping changed locked dependencies")
PY

{
  echo "CURRENT_VERSION=$current_version"
  echo "PROJECT_VERSION=$project_version"
} >> "$GITHUB_ENV"
