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

from pysonar_scanner.configuration.cli import CliConfigurationLoader
from pysonar_scanner.configuration.properties import SONAR_TOKEN, SONAR_PROJECT_BASE_DIR, Key
from pysonar_scanner.configuration.properties import PROPERTIES
from pysonar_scanner.configuration import sonar_project_properties, pyproject_toml

from pysonar_scanner.exceptions import MissingKeyException


def get_static_default_properties() -> dict[Key, any]:
    return {prop.name: prop.default_value for prop in PROPERTIES if prop.default_value is not None}


class ConfigurationLoader:
    @staticmethod
    def load() -> dict[Key, any]:
        # each property loader is required to return NO default values.
        # E.g. if no property has been set, an empty dict must be returned.
        # Default values should be set through the get_static_default_properties() method
        resolved_properties = get_static_default_properties()
        cli_properties = CliConfigurationLoader.load()
        # CLI properties have a higher priority than properties file,
        # but we need to resolve them first to load the properties file
        base_dir = Path(cli_properties.get(SONAR_PROJECT_BASE_DIR, "."))

        toml_path_property = cli_properties.get("toml-path", ".")
        toml_dir = Path(toml_path_property) if "toml-path" in cli_properties else base_dir
        toml_properties = pyproject_toml.load(toml_dir)

        resolved_properties.update(toml_properties.project_properties)
        resolved_properties.update(sonar_project_properties.load(base_dir))
        resolved_properties.update(toml_properties.sonar_properties)
        resolved_properties.update(cli_properties)
        return resolved_properties


def get_token(config: dict[Key, any]) -> str:
    if SONAR_TOKEN not in config:
        raise MissingKeyException(f'Missing property "{SONAR_TOKEN}"')
    return config[SONAR_TOKEN]
