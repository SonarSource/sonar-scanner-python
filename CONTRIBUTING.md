# For developers

## Prerequisites

 - Python 3.12
 - [pipx](https://github.com/pypa/pipx)

## Install poetry

Install poetry with `pipx install poetry`

# Run the main script

Run `python src/pysonar_scanner`

# Run the tests

Run `poetry install` to install the dependencies. By default, the dependencies are installed from the Jfrog private repository.

To configure your credentials for Jfrog, go to your Jfrog user profile, and generate an identity token. Then set the following two environment variables:
```shell
poetry config http-basic.jfrog-server <username> <password>
```
Where `<username>` is your Jfrog username and `<password>` is the identity token you generated.

If you wish to install the dependencies from the public PyPI repository, remove the following source from `pyproject.toml`:
```toml
[[tool.poetry.source]]
name = 'jfrog-server'
url = 'https://repox.jfrog.io/artifactory/api/pypi/sonarsource-pypi/simple'
```

## Run the tests only

Run `poetry run pytest tests/`

## Run the tests with coverage and results displayed in the terminal

Run `poetry run pytest --cov-report=term-missing --cov-config=pyproject.toml --cov=src --cov-branch tests`

## Run the tests with coverage and store the result in an xml file

Run `poetry run pytest --cov-report=xml:coverage.xml --cov-config=pyproject.toml --cov=src --cov-branch tests`

## Run the ITs

Run `poetry run pytest tests/its --its` to run the its.

To see the ITs in the VSCode test explorer, add the `--its` argument to the `python.testing.pytestArgs` setting in `.vscode/settings.json`.

The the following keys should be present:
```json
  "python.testing.unittestArgs": ["-v", "-s", "tests", "-p", "test_*.py"],
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.testing.pytestArgs": ["--its", "tests"],
```

### Debugging the ITs

To debug the sonar-scanner being run in the its, the ITs have to be run with `poetry run pytest tests/its --its --debug-its`

The `pysonar-scanner` process will wait until VSCode or any other debug adapter protocol client connects on the port `5678`.

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

Run `poetry build` to create the package. 
The binaries will be located in the `dist` directory at the root level of the project.

# Publish the script

Create a GitHub release.

# Update the package version

To update the version use the Poetry command:

```
poetry version "X.Y.Z"
```
or
```shell
poetry version patch
```
For more options on the version update see [the Poetry documentation](https://python-poetry.org/docs/cli/#version)

# Tooling 
## Formatting 

Run `poetry run black src/ tests/ --check` to run the check the formatting on all files.
To automatically apply formatting, run `poetry run black src/ tests/`.

## Type checking

Run `poetry run mypy src/ tests/ --ignore-missing-imports` to execute the type checking on all files.

## License header

Before pushing, please check if all files have a license header.
If not all files have a license header please execute: 
```
poetry run licenseheaders -t license_header.tmpl -o "SonarSource SA" -y 2011-2024 -n "Sonar Scanner Python" -E .py -d src/
poetry run licenseheaders -t license_header.tmpl -o "SonarSource SA" -y 2011-2024 -n "Sonar Scanner Python" -E .py -d tests/
```
