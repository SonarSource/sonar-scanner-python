# sonar-scanner-python
A wrapper around SonarScanner CLI, available on PyPI.

# Installation 

## Install virtual env and create a new environment

Run `python3 -m pip install --user virtualenv`

Then create a new env with `python3 -m venv <name of your venv>`

Activate the venv with `source <name of your venv>/bin/activate`

Install the dependencies with `pip install -r requirements.txt`

# Run the main script

Run `python3 main.py <args>`

# Run the tests

Run `python3 test/tests.py`


# Publish the script

Make sure to have the latest version of PyPA with `python3 -m pip install --upgrade build`

Run `python3 -m build` to create the binaries

Run if needed `python3 -python3 -m pip install --upgrade twine` to upgrade to the latest version of twine

Run `python3 -m twine upload --repository testpypi dist/*` 

`--repository testpypi` can be removed to push to the prod PyPI instance.
Also `dist/*` can be a bit more precise to upload a specific version of the binaries
