#!/bin/bash

function run_analysis {
  # deal with strange SonarQube configuration for the US region
  SONAR_REGION=""
  if [ "$SONAR_HOST_URL" == "https://sonarqube.us" ]; then
    SONAR_REGION="-Dsonar.region=us"
  fi

  # extra analysis parameters are set in the 'sonar-project.properties'
  pysonar \
  -Dsonar.host.url="$SONAR_HOST_URL" \
  ${SONAR_REGION} \
  -Dsonar.token="$SONAR_TOKEN" \
  -Dsonar.analysis.buildNumber=$CI_BUILD_NUMBER \
  -Dsonar.analysis.pipeline="$PIPELINE_ID" \
  -Dsonar.analysis.sha1="$GIT_SHA1" \
  -Dsonar.analysis.repository="$GITHUB_REPO" \
  "$@"
}

# generic environment variables
export GIT_SHA1=$CIRRUS_CHANGE_IN_REPO
export GITHUB_BRANCH=$CIRRUS_BRANCH
export GITHUB_REPO=${CIRRUS_REPO_FULL_NAME}
export PULL_REQUEST=${CIRRUS_PR:-false}
export PIPELINE_ID=${CIRRUS_BUILD_ID}

if $(git rev-parse --is-shallow-repository); then
  # repository is shallow
  # If there are not enough commits in the Git repository, this command will fail with "fatal: --unshallow on a complete repository does not make sense"
  # For this reason errors are ignored with "|| true"
  git fetch --unshallow || true
else
  # repo is not shallow, retrieving all
  git fetch --all
fi

if [ "${GITHUB_BRANCH}" == "master" ] && [ "$PULL_REQUEST" == "false" ]; then
  echo '======= Analyze master'
  run_analysis "$@"

elif [[ "${GITHUB_BRANCH}" == "branch-"* ]] && [ "$PULL_REQUEST" == "false" ]; then
  echo '======= Analyze maintenance branches as long-living branches'
  run_analysis -Dsonar.branch.name="$GITHUB_BRANCH" "$@"

elif [ "$PULL_REQUEST" != "false" ]; then
  echo '======= Analyze pull request'
  run_analysis -Dsonar.analysis.prNumber="$PULL_REQUEST" "$@"

else
  echo '======= No analysis'
fi
