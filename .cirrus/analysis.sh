#!/bin/bash
function run_analysis {
  # extra analysis parameters are set in the 'sonar-project.properties'
  pysonar-scanner \
  -Dsonar.host.url="$SONAR_HOST_URL" \
  -Dsonar.token="$SONAR_TOKEN" \
  -Dsonar.analysis.buildNumber=$CI_BUILD_NUMBER \
  -Dsonar.analysis.pipeline="$PIPELINE_ID" \
  -Dsonar.analysis.sha1="$GIT_SHA1" \
  -Dsonar.analysis.repository="$GITHUB_REPO" \
  "$@"
}

# Fetch all commit history so that SonarQube has exact blame information
# for issue auto-assignment
# This command can fail with "fatal: --unshallow on a complete repository does not make sense"
# if there are not enough commits in the Git repository
# For this reason errors are ignored with "|| true"
git fetch --unshallow || git fetch --all || true

if [ "${GITHUB_BASE_BRANCH}" != "false" ]; then
  echo '======= Fetch references from github for PR analysis'
  git fetch origin "${GITHUB_BASE_BRANCH}"
fi

if [ -z "$PIPELINE_ID" ]; then
  PIPELINE_ID=$BUILD_NUMBER
fi

if [ "${GITHUB_BRANCH}" == "master" ] && [ "$PULL_REQUEST" == "false" ]; then
  echo '======= Build and analyze master'
  git fetch origin "${GITHUB_BRANCH}"
  run_analysis "$@"

elif [[ "${GITHUB_BRANCH}" == "branch-"* ]] && [ "$PULL_REQUEST" == "false" ]; then
  echo '======= Build and analyze maintenance branches as long-living branches'

  git fetch origin "${GITHUB_BRANCH}"
  run_analysis -Dsonar.branch.name="$GITHUB_BRANCH" "$@"

elif [ "$PULL_REQUEST" != "false" ]; then
  echo '======= Build and analyze pull request'
  run_analysis -Dsonar.analysis.prNumber="$PULL_REQUEST" "$@"

else
  echo '======= Build, no analysis'
fi