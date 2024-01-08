# sonar-scanner-python
A wrapper around SonarScanner CLI, available on PyPI.

# Installation

Install with pip:
```
pip install sonar-scanner-python FIXME -- The actual package name is not yet defined. Refer to PYSCAN-35
```

# Usage

Once installed, the `sonar-scanner-python` can be run from the command line to perform an analysis.
It assumes a running SonarQube server or a project configured on SonarCloud.

## Setting up analysis properties

In order for the analysis to run, analysis properties need to be defined. 
There are multiple ways of providing these properties, described below in descending order of priority:

* Through CLI arguments to the `sonar-scanner-python` command
* Under the `[tool.sonar]` key of the `pyproject.toml` file
* In a dedicated `sonar-project.properties` file
* Through environment variables

### Through CLI arguments

Analysis properties can be provided as CLI arguments to the `sonar-scanner-python` command.
They follow the same convention as when running the SonarScanner CLI directly 
(see [documentation](https://docs.sonarsource.com/sonarqube/9.9/analyzing-source-code/scanners/sonarscanner/#running-from-zip-file)).
This means that analysis properties provided that way should be prepended with `-D`, for instance:

```
$ sonar-scanner-python -Dsonar.login=myAuthenticationToken FIXME -- The actual command name is not yet defined. Refer to PYSCAN-35
```

You can use all the argument allowed by __SonarScanner__. 
For more information on __SonarScanner__ please refer to the [SonarScanner documentation](https://docs.sonarsource.com/sonarqube/9.9/analyzing-source-code/scanners/sonarscanner/)

### With a pyproject.toml file

Inside a `pyproject.toml`, Sonar analysis properties can be defined under the `tool.sonar` table.

```
[tool.sonar]
# must be unique in a given SonarQube/SonarCloud instance
projectKey=my:project

# --- optional properties ---
# defaults to project key
#projectName=My project
# defaults to 'not provided'
#projectVersion=1.0
 
# Path is relative to the pyproject.toml file. Defaults to .
#sources=.
 
# Encoding of the source code. Default is default system encoding
#sourceEncoding=UTF-8
```

The configuration parameters can be found in the [SonarQube documentation](https://docs.sonarsource.com/sonarqube/9.9/analyzing-source-code/analysis-parameters/).

In the `pyproject.toml` file the prefix `sonar.` for parameter keys should be omitted. 
For example, `sonar.scm.provider` in the documentation will become `scm.provider` in the `pyproject.toml` file.

By default, the scanner will expect the `pyproject.toml` file to be present in the current directory. 
However, its path can be provided manually through the `toml.path` ([PYSCAN-40](https://sonarsource.atlassian.net/jira/software/c/projects/PYSCAN/issues/PYSCAN-40)) CLI argument as well as through the `sonar.projectHome` argument. For instance:

```
sonar-scanner-python -Dtoml.path="path/to/pyproject.toml"
```

Or:

```
sonar-scanner-python -Dsonar.projectHome="path/to/projectHome"
```

### With a sonar-project.properties file

Exactly like [__SonarScanner__](https://docs.sonarsource.com/sonarqube/9.9/analyzing-source-code/scanners/sonarscanner/),
the analysis can also be configured with a `sonar-project.properties` file:

```
# must be unique in a given SonarQube/SonarCloud instance
sonar.projectKey=my:project

# --- optional properties ---

# defaults to project key
#sonar.projectName=My project
# defaults to 'not provided'
#sonar.projectVersion=1.0
 
# Path is relative to the sonar-project.properties file. Defaults to .
#sonar.sources=.
 
# Encoding of the source code. Default is default system encoding
#sonar.sourceEncoding=UTF-8
```

### Through environment variables

It is also possible to define configure the scanner through environment variables:

```
$ export SONAR_HOST_URL="http://localhost:9000"
$ sonar-scanner-python FIXME -- The actual command name is not yet defined. Refer to PYSCAN-35
```

See the __SonarScanner__ [documentation](https://docs.sonarsource.com/sonarqube/9.9/analyzing-source-code/scanners/sonarscanner/) for more information.

# For developers

## Prerequisites

 - Python 3.12
<<<<<<< HEAD
 - [pipx](https://github.com/pypa/pipx)
=======
>>>>>>> fbee484 (PYSCAN-36: Migrate from Hatch to Poetry (#27))

## Install poetry

Install poetry with `pipx install poetry`

Install poetry with `pip install poetry`

Install setuptools with `pip install setuptools`

# Run the main script

Run `python src/py_sonar_scanner`

# Run the tests

Run `poetry install` to install the dependencies

## Run the tests only

Run `poetry run pytest test/`

## Run the tests with coverage and results displayed in the terminal

Run `poetry run pytest --cov-report=term-missing --cov-config=pyproject.toml --cov=src --cov-branch tests`

## Run the tests with coverage and store the result in an xml file

Run `poetry run pytest --cov-report=xml:coverage.xml --cov-config=pyproject.toml --cov=src --cov-branch tests`

# Build the package

Run `poetry build` to create the package. 
The binaries will be located in the `dist` directory at the root level of the project.

# Publish the script

Run if needed `python3 -python3 -m pip install --upgrade twine` to upgrade to the latest version of twine

Run `python3 -m twine upload --repository testpypi dist/*` 

`--repository testpypi` can be removed to push to the prod PyPI instance.
Also `dist/*` can be a bit more precise to upload a specific version of the binaries

# Update the package version

To update the version use the hatch command:

```
poetry version "X.Y.Z"
```
For more options on the version update see [the hatch documentation](https://hatch.pypa.io/latest/version/)

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
poetry run licenseheaders -t license_header.tmpl -o "SonarSource SA" -y 2011-2023 -n "Sonar Scanner Python" -E .py -d src/
poetry run licenseheaders -t license_header.tmpl -o "SonarSource SA" -y 2011-2023 -n "Sonar Scanner Python" -E .py -d tests/
```

# License

Copyright 2011-2023 SonarSource.

Licensed under the [GNU Lesser General Public License, Version 3.0](http://www.gnu.org/licenses/lgpl.txt)
