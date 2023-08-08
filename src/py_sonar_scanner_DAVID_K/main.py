#!/usr/bin/env python3
"""
Module Docstring
"""

__author__ = "Python Squad"
__version__ = "0.1.0"

from py_sonar_scanner_DAVID_K.configuration_properties_config import ConfigurationPropertiesConfig
from py_sonar_scanner_DAVID_K.context import Context
from py_sonar_scanner_DAVID_K.environment_config import EnvironmentConfig
from py_sonar_scanner_DAVID_K.scanner import Scanner


def scan():
    ctx = Context()

    ConfigurationPropertiesConfig().setup(ctx)
    EnvironmentConfig().setup(ctx)
    Scanner().scan(ctx)


if __name__ == "__main__":
    scan()
