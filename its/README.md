# Integration tests for py-sonar-scanner

## Prerequisits

- Python 3.12
- Docker

## Setup

Before executing the tests be sure to install the dependencies.

In the __its__ folder:
- Create a virtual environment `python3 -m venv <name>`
- Source the environment `source <name>/bin/activate`
- Install its dependencies `poetry install`
- Install cli that will be used in the test:
    - to install the built package execute `pip install ../dist/py_sonar_scanner-<version>-py3-none-any-.whl` 
    - to install the current dev version `pip install ..`


## Running the integration tests

You can now run the tests with `poetry run pytest`

