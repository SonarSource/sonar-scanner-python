#!/usr/bin/env bash
set -euo pipefail

sonar_args=(
  "-Dsonar.analysis.buildNumber=${BUILD_NUMBER:?}"
  "-Dsonar.analysis.pipeline=${GITHUB_RUN_ID:?}"
  "-Dsonar.analysis.repository=${GITHUB_REPOSITORY:?}"
)

if [[ "${GITHUB_EVENT_NAME:?}" == "pull_request" ]]; then
  sonar_args+=("-Dsonar.analysis.prNumber=${PULL_REQUEST:?}")
elif [[ "${GITHUB_REF_NAME:?}" == "${DEFAULT_BRANCH:?}" ]]; then
  :
elif [[ "$GITHUB_REF_NAME" == branch-* || "$GITHUB_REF_NAME" == feature/long/* ]]; then
  sonar_args+=("-Dsonar.branch.name=$GITHUB_REF_NAME")
else
  echo "Sonar analysis is disabled for $GITHUB_REF_NAME"
  exit 0
fi

platforms=(next)
if [[ "${RUN_SHADOW_SCANS:-false}" == "true" ]]; then
  platforms+=(sqc-us sqc-eu)
fi
for platform in "${platforms[@]}"; do
  export SONAR_REGION=""
  case "$platform" in
    next)
      export SONAR_HOST_URL="${NEXT_URL:?}" SONAR_TOKEN="${NEXT_TOKEN:?}"
      ;;
    sqc-us)
      export SONAR_HOST_URL="${SQC_US_URL:?}" SONAR_TOKEN="${SQC_US_TOKEN:?}" SONAR_REGION=us
      ;;
    sqc-eu)
      export SONAR_HOST_URL="${SQC_EU_URL:?}" SONAR_TOKEN="${SQC_EU_TOKEN:?}"
      ;;
  esac
  uv run --locked pysonar "${sonar_args[@]}"
done
