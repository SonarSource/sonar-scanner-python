# For developers

## Prerequisites

 - Python 3.10–3.14 (CI uses Python 3.12 for packaging and tooling)
 - [mise](https://mise.jdx.dev/)

## Install uv and dependencies

Run `mise install` to install the pinned uv and JFrog CLI versions, and activate mise in your shell.
The project uses uv 0.13.6 and commits `uv.lock` for reproducible dependency resolution.

Dependencies resolve exclusively through the default `repox` index. Generate an identity token in your
JFrog user profile and set credentials in your shell (do not commit them):

```shell
export UV_INDEX_REPOX_USERNAME="<username>"
export UV_INDEX_REPOX_PASSWORD="<identity-token>"
uv sync --locked
```

To select an existing interpreter explicitly, set `UV_PYTHON` to its path (for example,
`export UV_PYTHON="$(mise which python)"`). Set `UV_PYTHON_DOWNLOADS=never` to disable uv's automatic
Python downloads, as CI does.

For local installation from public PyPI, remove the entire `[[tool.uv.index]]` entry from
`pyproject.toml`, then run `uv lock --default-index https://pypi.org/simple` and `uv sync --locked`.
The re-lock is necessary because `uv.lock` records registry URLs. Keep these changes local and restore
both `pyproject.toml` and `uv.lock` before committing; CI requires Repox.

# Run the scanner

Run `uv run --locked pysonar`.

# Run the tests

## Run the tests only

Run `uv run --locked pytest tests/`

## Run the tests with coverage and results displayed in the terminal

Run `uv run --locked pytest --cov-report=term-missing --cov-config=pyproject.toml --cov=src --cov-branch tests`

## Run the tests with coverage and store the result in an xml file

Run `uv run --locked pytest --cov-report=xml:coverage.xml --cov-config=pyproject.toml --cov=src --cov-branch tests`

## Run the ITs

On Linux or macOS, install Java 21, `curl`, and `unzip`, then run `./scripts/run_its.sh`.
The script installs the Python dependencies, downloads and caches the same SonarQube version used in CI,
starts a fresh instance on port 9000, runs the ITs, and stops the instance when finished.
Port 9000 must be available.
Additional arguments are passed to pytest, for example `./scripts/run_its.sh -k test_minimal_project`.

To run pytest directly or use the VSCode test explorer, first start a disposable SonarQube instance on
`http://localhost:9000` with the default administrator credentials. Then run `uv run --locked pytest tests/its --its`
or add the `--its` argument to the `python.testing.pytestArgs` setting in `.vscode/settings.json`.

The following keys should be present:
```json
  "python.testing.unittestArgs": ["-v", "-s", "tests", "-p", "test_*.py"],
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.testing.pytestArgs": ["--its", "tests"],
```

### Debugging the ITs

To debug the sonar-scanner being run in the ITs, run `./scripts/run_its.sh --debug-its`.

The `pysonar` process will wait until VSCode or any other debug adapter protocol client connects on the port `5678`.

For VSCode, add the following launch configuration in the `configurations` array:
```json
{
    "name": "Python Debugger: Remote Attach",
    "type": "debugpy",
    "request": "attach",
    "connect": {
        "host": "localhost",
        "port": 5678
    },
}
```

# Build the package

Run `uv build --no-sources` to create the package.
The binaries will be located in the `dist` directory at the root level of the project.

# Publish the script

See [RELEASE.md](RELEASE.md).

# Update the package version

To update the version and lockfile together:

```shell
uv version --no-sync "X.Y.Z"
```

For a patch increment, run `uv version --no-sync --bump patch`.
Commit both `pyproject.toml` and `uv.lock`. CI validates the committed lockfile before appending its
build number in the disposable checkout and checks that stamping leaves dependency versions unchanged.
See [uv version](https://docs.astral.sh/uv/reference/cli/#uv-version) for other increments.

# Tooling
## Formatting

Run `uv run --locked black src/ tests/ --check` to check the formatting on all files.
To automatically apply formatting, run `uv run --locked black src/ tests/`.

## Type checking

Run `uv run --locked mypy src/ --ignore-missing-imports` to type check the scanner source.

## License header

Before pushing, please check if all files have a license header.
If not all files have a license header please execute:
```
uv run --locked licenseheaders -t license_header.tmpl -o "SonarSource Sàrl" -y 2011-2026 -n "Sonar Scanner Python" -E .py -d src/
uv run --locked licenseheaders -t license_header.tmpl -o "SonarSource Sàrl" -y 2011-2026 -n "Sonar Scanner Python" -E .py -d tests/
```
