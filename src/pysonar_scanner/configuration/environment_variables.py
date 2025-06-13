#
# Sonar Scanner Python
# Copyright (C) 2011-2024 SonarSource SA.
# mailto:info AT sonarsource DOT com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful,
#
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
import logging
import os
import json
from typing import Dict

from pysonar_scanner.configuration.properties import Key, PROPERTIES


def load() -> Dict[Key, str]:
    """
    Load configuration properties from environment variables.

    Returns:
        Dictionary of property keys and their values extracted from environment variables.
    """
    # Extract properties from environment variables using the env_variable_name() method

    # First check for JSON params environment variable
    properties = load_json_env_variables()
    # Extract properties from environment variables using the mapping in Property objects
    properties.update(load_properties_env_variables())

    return properties


def load_json_env_variables():
    properties = {}
    if "SONAR_SCANNER_JSON_PARAMS" in os.environ:
        try:
            json_params = os.environ["SONAR_SCANNER_JSON_PARAMS"]
            json_properties = json.loads(json_params)
            properties.update(json_properties)
        except json.JSONDecodeError as e:
            logging.warning(
                f"The JSON in SONAR_SCANNER_JSON_PARAMS environment variable is invalid. The other environment variables will still be loaded. Error : {e}"
            )
    logging.debug("Loaded environment properties: " + ", ".join(f"{key}={value}" for key, value in properties.items()))
    return properties


def load_properties_env_variables():
    properties = {}
    for prop in PROPERTIES:
        env_var_name = prop.env_variable_name()
        if env_var_name in os.environ:
            properties[prop.name] = os.environ[env_var_name]
            if prop.deprecation_message:
                logging.warning(prop.deprecation_message)
    return properties
