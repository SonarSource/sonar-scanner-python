# sonar-scanner-python
A wrapper around SonarScanner CLI, available on PyPI.

# Installation 
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
