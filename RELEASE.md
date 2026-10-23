# Releasing Sonar Scanner Python

Releases are published by the [sonar-release](.github/workflows/release.yml) workflow, which calls
[`gh-action_release@v7`](https://github.com/SonarSource/gh-action_release#migrating-from-v6-to-v7-draft-first-workflow_dispatch).
The workflow creates (or reuses) a draft GitHub release, publishes the package to PyPI or TestPyPI, then publishes the GitHub release.
Do not publish a GitHub release by hand: it no longer triggers anything.

## Release

1. Make sure the version in `pyproject.toml` is the one to release (see [Update the package version](CONTRIBUTING.md#update-the-package-version)).
2. Find the build number of the `master` commit to release: it is the `build-number` output of its [Build](.github/workflows/build.yml) workflow run.
   The release version is `<pyproject version>.<build number>`, e.g. `1.10.0.5900`.
3. Run the workflow:
   - **UI**: Actions → sonar-release → Run workflow, then enter the `version`.
   - **CLI**: `gh workflow run release.yml -f version=1.10.0.5900`
4. Once the workflow succeeds, review the release notes of the published GitHub release.

## Pre-release to TestPyPI

Run the same workflow with the `prerelease` checkbox ticked (CLI: `-f prerelease=true`).
The package is published to [TestPyPI](https://test.pypi.org/project/pysonar/) instead of PyPI.
The GitHub release is not flagged as a pre-release: `gh-action_release@v7` has no pre-release support.

## Retry a failed release

A failure leaves the draft release and the tag in place. Fix the root cause, then re-run the failed jobs from the workflow run page.
No rebuild is needed, and the same version is reused.
