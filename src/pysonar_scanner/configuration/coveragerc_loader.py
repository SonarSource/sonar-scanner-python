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
import configparser
import logging
import pathlib
from typing import Any


class CoverageRCConfigurationLoader:

    @staticmethod
    def load_exclusion_properties(base_dir: pathlib.Path) -> dict[str, str]:
        config_file_path = base_dir / ".coveragerc"
        coverage_properties = CoverageRCConfigurationLoader.__read_config(config_file_path)
        if len(coverage_properties) == 0:
            return {}
        translated_exclusions = CoverageRCConfigurationLoader.__extract_coverage_exclusion_patterns(
            config_file_path, coverage_properties
        )
        if len(translated_exclusions) == 0:
            return {}

        return {"sonar.coverage.exclusions": ", ".join(translated_exclusions)}

    @staticmethod
    def __read_config(config_file_path: pathlib.Path) -> dict[str, Any]:
        config_dict: dict[str, Any] = {}
        if not config_file_path.exists():
            logging.debug(f"Coverage file not found: {config_file_path}")
            return config_dict

        try:
            config_parser = configparser.ConfigParser()
            config_parser.read(config_file_path)
            for section in config_parser.sections():
                section_values = {}
                for key, value in config_parser.items(section):
                    section_values[key] = value
                config_dict[section] = section_values
        except Exception as e:
            logging.debug(f"Error decoding coverage file {config_file_path}: {e}")
        return config_dict

    @staticmethod
    def __extract_coverage_exclusion_patterns(
        config_file_path: pathlib.Path, coverage_properties: dict[str, Any]
    ) -> list[str]:
        if "run" not in coverage_properties or "omit" not in coverage_properties["run"]:
            logging.debug(f"Coverage file {config_file_path} has no exclusion properties")
            return []

        omit_exclusions = coverage_properties["run"]["omit"]
        return [patterns.strip() for patterns in omit_exclusions.splitlines() if patterns.strip()]
