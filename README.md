# pysonar-scanner
A wrapper around SonarScanner CLI, available on PyPI.

# Disclaimer 

This project is currently in beta and APIs are subject to change. 
These changes include configuration parameter names.

# Requirements

 - SonarQube v9.9 or higher
 - Python 3.8 or above

# Installation

Install with pip:
```
pip install pysonar-scanner
```

# Usage

Once installed, the `pysonar-scanner` can be run from the command line to perform an analysis.
It assumes a running SonarQube server or a project configured on SonarCloud.

## Setting up analysis properties

In order for the analysis to run, analysis properties need to be defined. 
There are multiple ways of providing these properties, described below in descending order of priority:

* Through CLI arguments to the `pysonar-scanner` command
* Under the `[tool.sonar]` key of the `pyproject.toml` file
* Through common properties extracted from the `pyproject.toml`
* In a dedicated `sonar-project.properties` file
* Through environment variables

### Through CLI arguments

Analysis properties can be provided as CLI arguments to the `pysonar-scanner` command.
They follow the same convention as when running the SonarScanner CLI directly 
(see [documentation](https://docs.sonarsource.com/sonarqube/9.9/analyzing-source-code/scanners/sonarscanner/#running-from-zip-file)).
This means that analysis properties provided that way should be prepended with `-D`, for instance:

```
$ pysonar-scanner -Dsonar.login=myAuthenticationToken 
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
pysonar-scanner -Dtoml.path="path/to/pyproject.toml"
```

Or:

```
pysonar-scanner -Dsonar.projectHome="path/to/projectHome"
```


### Through project properties extracted from the `pyproject.toml`

When a `pyproject.toml` file is available, it is possible to set the `-read-project-config` flag
to allow the scanner to deduce analysis properties from the project configuration.

This is currently supported only for projects using `poetry`.

The Sonar scanner will then use the project name and version defined through Poetry, they won't have to be duplicated under a dedicated `tool.sonar` section.

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
$ pysonar-scanner 
```

See the __SonarScanner__ [documentation](https://docs.sonarsource.com/sonarqube/9.9/analyzing-source-code/scanners/sonarscanner/) for more information.

# Installation from testPyPI

To install the latest pre-released version of Sonar Scanner Python. Execute the following command: 

```shell
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pysonar-scanner
```

# License

Copyright 2011-2024 SonarSource.

Licensed under the [GNU Lesser General Public License, Version 3.0](http://www.gnu.org/licenses/lgpl.txt)
