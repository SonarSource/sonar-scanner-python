# sonar-scanner-python
A wrapper around SonarScanner CLI, available on PyPI.

# Installation

Install with pip:
```
pip install sonar-scanner-python
```

# Usage 

## Configuration 

There are two ways of setting up sonar-scanner-python.

### with a pyproject.toml file

Inside a `pyproject.toml` setup your Sonar configuration under the `tool.sonar` table.

```
# must be unique in a given SonarQube/SonarCloud instance
[tool.sonar]
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

The configuration parameters can be found in the [SonarQube documentation](https://docs.sonarsource.com/sonarqube/9.9/analyzing-source-code/analysis-parameters/)
In the `pyproject.toml` file the prefix `sonar.` for parameter keys should be omitted. 
For example, `sonar.scm.provider` in the documentation will become `scm.provider` in the `pyproject.toml` file.

### with a sonar-project.properties file

Exactly like [__SonarScanner__](https://docs.sonarsource.com/sonarqube/9.9/analyzing-source-code/scanners/sonarscanner/) 
you can configure a project analysis with a `sonar-project.properties` file:

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

## Running an analysis

Once the project is configured, you can run the following command:

```
$ sonar-scanner-python
```

It is still possible to pass configuration parameters when running the `sonar-scanner-python` command, for example:

```
$ sonar-scanner-python -Dsonar.login=myAuthenticationToken
```

You can use all the argument allowed by __SonarScanner__. 
For more information on __SonarScanner__ please refer to the [SonarScanner documentation](https://docs.sonarsource.com/sonarqube/9.9/analyzing-source-code/scanners/sonarscanner/)

You can also use environment variables:

```
$ export SONAR_HOST_URL="http://localhost:9000"
$ sonar-scanner-python
```

# For developers

## Prerequisites

 - Python 3.12
 - [Hatch](https://hatch.pypa.io/latest/install/)

## Install virtual env and create a new environment

Run `python3 -m pip install --user virtualenv`

Then create a new env with `python3 -m venv <name of your venv>`

Activate the venv with `source <name of your venv>/bin/activate`

# Run the main script

Run `python3 main.py <args>`

# Run the tests

Run `hatch run test:test`

# Build the package

Run `hatch build` to create the package. 
The binaries will be located in the `dist` directory at the root level of the project.

# Publish the script

Run if needed `python3 -python3 -m pip install --upgrade twine` to upgrade to the latest version of twine

Run `python3 -m twine upload --repository testpypi dist/*` 

`--repository testpypi` can be removed to push to the prod PyPI instance.
Also `dist/*` can be a bit more precise to upload a specific version of the binaries

# Update the package version

To update the version use the hatch command:

```
hatch version "X.Y.Z"
```
For more options on the version update see [the hatch documentation](https://hatch.pypa.io/latest/version/)

# Tooling 
## Formatting 

Run `hatch run tool:format` to run the formatter on all files.

## Type checking

Run `hatch run tool:type_check` to execute the type checking on all files.

## License header

Before pushing, please check if all files have a license header.
If not all files have a license header please execute: `hatch run tool:license`.


# License

Copyright 2011-2023 SonarSource.

Licensed under the [GNU Lesser General Public License, Version 3.0](http://www.gnu.org/licenses/lgpl.txt)
