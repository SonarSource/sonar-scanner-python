# pysonar
A Python scanner for SonarQube, available on PyPI.

# Requirements

 - SonarQube v10.6 or above
 - Python 3.9 or above

# Installation

Install with pip:
```
pip install pysonar
```

# Usage

Once installed, the `pysonar` scanner can be run from the command line to perform an analysis.
It assumes a running SonarQube server or a project configured on SonarCloud.

## Setting up analysis properties

In order for the analysis to run, analysis properties need to be defined. 
There are multiple ways of providing these properties, described below in descending order of priority:

1. Through CLI arguments to the `pysonar` command
2. Environment variables for individual properties (e.g. `SONAR_TOKEN`, `SONAR_VERBOSE`, `SONAR_HOST_URL`, ...)
3. Generic environment variable `SONAR_SCANNER_JSON_PARAMS` 
4. Under the `[tool.sonar]` key of the `pyproject.toml` file
5. In a dedicated `sonar-project.properties` file
6. Through common properties extracted from the `pyproject.toml`

### Through CLI arguments

Analysis properties can be provided as CLI arguments to the `pysonar` command.
They can be provided in a similar way as when running the SonarScanner CLI directly 
(see [documentation](https://docs.sonarsource.com/sonarqube-server/2025.1/analyzing-source-code/scanners/sonarscanner/#running-from-zip-file)).
This means that analysis properties provided that way should be prepended with `-D`, for instance:

```
$ pysonar -Dsonar.token=myAuthenticationToken 
```

You can use all the arguments allowed by __SonarScanner__. 
For more information on __SonarScanner__ please refer to the [SonarScanner documentation](https://docs.sonarsource.com/sonarqube-server/2025.1/analyzing-source-code/analysis-parameters/).

Additionally, some common properties can be provided using a shorter alias, such as:
```
pysonar --token "MyToken"
```

See [CLI_ARGS](https://github.com/SonarSource/sonar-scanner-python/blob/master/CLI_ARGS.md) for more details.

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

The configuration parameters can be found in the [SonarQube documentation](https://docs.sonarsource.com/sonarqube-server/2025.1/analyzing-source-code/analysis-parameters/).

In the `pyproject.toml` file the prefix `sonar.` for parameter keys should be omitted. 
For example, `sonar.scm.provider` in the documentation will become `scm.provider` in the `pyproject.toml` file.

Properties in `pyproject.toml` files are expected to be provided in camel case. However, kebab case is also accepted:

```
[tool.sonar]
project-key=My Project key # valid alias for projectKey
```

By default, the scanner will expect the `pyproject.toml` file to be present in the current directory. However, its path can be provided manually through the `toml-path` CLI argument as well as through the `sonar.projectBaseDir` argument. For instance:

```
pysonar --toml-path "path/to/pyproject.toml"
```

Or:

```
pysonar --sonar-project-base-dir "path/to/projectBaseDir"
```

Or:

```
pysonar -Dsonar.projectBaseDir="path/to/projectBaseDir"
```

### Through project properties extracted from the `pyproject.toml`

When a `pyproject.toml` file is available, the scanner can deduce analysis properties from the project configuration. This is currently supported only for projects using `poetry`.

### With a sonar-project.properties file

Exactly like [__SonarScanner__](https://docs.sonarsource.com/sonarqube-server/2025.1/analyzing-source-code/scanners/sonarscanner/),
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
$ pysonar 
```

See the __SonarScanner__ [documentation](https://docs.sonarsource.com/sonarqube-server/2025.1/setup-and-upgrade/environment-variables/) for more information.

# Installation from testPyPI

To install the latest pre-released version of Sonar Scanner Python. Execute the following command: 

```shell
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pysonar
```

# License

Copyright 2011-2024 SonarSource.

Licensed under the [GNU Lesser General Public License, Version 3.0](http://www.gnu.org/licenses/lgpl.txt)
