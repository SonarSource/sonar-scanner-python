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
from pathlib import Path
from typing import Dict
import os
import tomli

from pysonar_scanner.configuration import properties


def flatten_config_dict(config: dict[str, any], prefix: str) -> dict[str, any]:
    """Flatten nested dictionaries into dot notation keys"""
    result = {}
    for key, value in config.items():
        if isinstance(value, dict):
            result.update(flatten_config_dict(value, f"{prefix}{key}."))
        else:
            property_name = f"{prefix}{key}"
            result[property_name] = value
    return result


def load(base_dir: Path) -> Dict[str, str]:
    filepath = base_dir / "pyproject.toml"
    if not os.path.isfile(filepath):
        return {}

    try:
        with open(filepath, "rb") as f:
            toml_dict = tomli.load(f)

        # Look for configuration in the tool.sonar section
        if "tool" in toml_dict and "sonar" in toml_dict["tool"]:
            sonar_config = toml_dict["tool"]["sonar"]
            python_to_java_names = {prop.python_name(): prop.name for prop in properties.PROPERTIES}
            flattened_sonar_config = flatten_config_dict(sonar_config, prefix="sonar.")
            return {python_to_java_names.get(key, key): value for key, value in flattened_sonar_config.items()}
        return {}
    except Exception:
        # If there's any error parsing the TOML file, return empty dict
        # SCANPY-135: We should log the pyproject.toml parsing error
        return {}
