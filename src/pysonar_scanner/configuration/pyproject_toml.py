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
from pathlib import Path
from typing import Any, Dict
import os
import tomli

from pysonar_scanner.configuration import properties


class TomlProperties:
    sonar_properties: Dict[str, str]
    project_properties: Dict[str, str]

    def __init__(self, sonar_properties: Dict[str, str], project_properties: Dict[str, str]):
        self.sonar_properties = sonar_properties
        self.project_properties = project_properties


class TomlConfigurationLoader:
    @staticmethod
    def load(base_dir: Path) -> TomlProperties:
        filepath = base_dir / "pyproject.toml"
        if not os.path.isfile(filepath):
            logging.debug(f"No pyproject.toml at {filepath}")
            return TomlProperties({}, {})
        logging.debug(f"pyproject.toml loaded from {filepath}")
        try:
            with open(filepath, "rb") as f:
                toml_dict = tomli.load(f)
            # Look for configuration in the tool.sonar section
            sonar_properties = TomlConfigurationLoader.__read_sonar_properties(toml_dict)
            # Look for general project configuration
            project_properties = TomlConfigurationLoader.__read_project_properties(toml_dict)
            return TomlProperties(sonar_properties, project_properties)
        except Exception as e:
            logging.warning(
                f"There was an error reading the pyproject.toml file. No properties from the TOML file were extracted. Error: {e}"
            )
            return TomlProperties({}, {})

    @staticmethod
    def __read_sonar_properties(toml_dict) -> Dict[str, str]:
        if "tool" in toml_dict and "sonar" in toml_dict["tool"]:
            sonar_config = toml_dict["tool"]["sonar"]
            python_to_java_names = {prop.python_name(): prop.name for prop in properties.PROPERTIES}
            flattened_sonar_config = TomlConfigurationLoader.__flatten_config_dict(sonar_config, prefix="sonar.")
            return {
                python_to_java_names.get(key, TomlConfigurationLoader.__kebab_to_camel_case(key)): value
                for key, value in flattened_sonar_config.items()
            }
        return {}

    @staticmethod
    def __read_project_properties(toml_dict) -> Dict[str, str]:
        # Extract project metadata
        project_properties = {}
        if "project" in toml_dict:
            project_data = toml_dict["project"]
            # Known pyproject.toml project keys and associated Sonar property names
            property_mapping = {
                "name": properties.SONAR_PROJECT_NAME,
                "description": properties.SONAR_PROJECT_DESCRIPTION,
                "version": properties.SONAR_PROJECT_VERSION,
                "requires-python": properties.SONAR_PYTHON_VERSION,
            }

            for toml_key, sonar_property in property_mapping.items():
                if toml_key in project_data:
                    string_property = TomlConfigurationLoader.__convert_arrays_to_string(project_data[toml_key])
                    project_properties[sonar_property] = string_property
        return project_properties

    @staticmethod
    def __flatten_config_dict(config: dict[str, Any], prefix: str) -> dict[str, Any]:
        """Flatten nested dictionaries into dot notation keys"""
        result = {}
        for key, value in config.items():
            if isinstance(value, dict):
                result.update(TomlConfigurationLoader.__flatten_config_dict(value, f"{prefix}{key}."))
            else:
                property_name = f"{prefix}{key}"
                result[property_name] = value
        return result

    @staticmethod
    def __convert_arrays_to_string(property) -> str:
        if isinstance(property, list):
            return ",".join(str(item) for item in property)
        else:
            return property

    @staticmethod
    def __kebab_to_camel_case(key: str) -> str:
        if "-" in key:
            parts = key.split("-")
            result = parts[0] + "".join(word.capitalize() for word in parts[1:])
            logging.debug(f"Converting kebab-case property '{key}' to camelCase: '{result}'")
            return result
        return key
