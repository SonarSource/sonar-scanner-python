#
# Sonar Scanner Python
# Copyright (C) 2011-2026 SonarSource Sàrl
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
from typing import Any

from pysonar_scanner.configuration.cli import CliConfigurationLoader
from pysonar_scanner.configuration.coveragerc_loader import CoverageRCConfigurationLoader
from pysonar_scanner.configuration.pyproject_toml import TomlConfigurationLoader
from pysonar_scanner.configuration.properties import (
    SONAR_PROJECT_KEY,
    SONAR_TOKEN,
    SONAR_PROJECT_BASE_DIR,
    SONAR_EXCLUSIONS,
    SONAR_SOURCES,
    SONAR_TESTS,
    SONAR_PYTHON_TEST_FILE_HEURISTIC_DISABLED,
    Key,
)
from pysonar_scanner.configuration.properties import PROPERTIES
from pysonar_scanner.configuration import (
    sonar_project_properties,
    environment_variables,
    dynamic_defaults_loader,
    test_paths_loader,
)

from pysonar_scanner.exceptions import MissingProperty, MissingPropertyException


def get_static_default_properties() -> dict[Key, Any]:
    return {prop.name: prop.default_value for prop in PROPERTIES if prop.default_value is not None}


class ConfigurationLoader:
    @staticmethod
    def load() -> dict[Key, Any]:
        logging.debug("Loading configuration properties...")

        # each property loader is required to return NO default values.
        # E.g. if no property has been set, an empty dict must be returned.
        # Default values should be set through the get_static_default_properties() method
        cli_properties = CliConfigurationLoader.load()
        # CLI properties have a higher priority than properties file,
        # but we need to resolve them first to load the properties file
        base_dir = Path(cli_properties.get(SONAR_PROJECT_BASE_DIR, "."))

        toml_path_property = cli_properties.get("toml-path", ".")
        toml_path = Path(toml_path_property) if "toml-path" in cli_properties else base_dir
        toml_properties = TomlConfigurationLoader.load(toml_path)
        coverage_properties = CoverageRCConfigurationLoader.load_exclusion_properties(base_dir)

        resolved_properties = get_static_default_properties()
        resolved_properties.update(dynamic_defaults_loader.load())
        resolved_properties.update(coverage_properties)
        resolved_properties.update(toml_properties.project_properties)
        resolved_properties.update(sonar_project_properties.load(base_dir))
        resolved_properties.update(toml_properties.sonar_properties)
        resolved_properties.update(environment_variables.load())
        resolved_properties.update(cli_properties)

        # Auto-detect sonar.tests only when the user has not set it in any higher-priority source
        # and has not explicitly disabled the sonar-python test file heuristic. When the heuristic
        # is disabled the intent is to analyse all files as main code with no test classification.
        heuristic_disabled = (
            str(resolved_properties.get(SONAR_PYTHON_TEST_FILE_HEURISTIC_DISABLED, "")).lower() == "true"
        )
        tests_auto_detected = False
        if SONAR_TESTS not in resolved_properties and not heuristic_disabled:
            inferred_props, disable_heuristic = test_paths_loader.load(base_dir)
            resolved_properties.update(inferred_props)
            tests_auto_detected = SONAR_TESTS in resolved_properties
            if disable_heuristic and SONAR_PYTHON_TEST_FILE_HEURISTIC_DISABLED not in resolved_properties:
                resolved_properties[SONAR_PYTHON_TEST_FILE_HEURISTIC_DISABLED] = "true"

        sources_defaulted = SONAR_SOURCES not in resolved_properties
        if sources_defaulted:
            logging.info(
                "sonar.sources is not set; defaulting to the current directory '.'. "
                "Set sonar.sources explicitly to override this behavior."
            )
            resolved_properties[SONAR_SOURCES] = "."

        if (sources_defaulted or tests_auto_detected) and SONAR_TESTS in resolved_properties:
            test_dirs = [d.strip() for d in resolved_properties[SONAR_TESTS].split(",") if d.strip()]
            test_exclusion_patterns = ",".join(f"{d}/**" for d in test_dirs)
            existing = resolved_properties.get(SONAR_EXCLUSIONS, "")
            resolved_properties[SONAR_EXCLUSIONS] = (
                f"{existing},{test_exclusion_patterns}" if existing else test_exclusion_patterns
            )
            logging.info(
                "Adding test directories to sonar.exclusions to avoid overlap with sonar.sources: '%s'. "
                "To manage this manually, set sonar.sources to a path that does not include the test directories, "
                "or set sonar.tests explicitly to disable auto-detection.",
                test_exclusion_patterns,
            )

        return resolved_properties

    @staticmethod
    def check_configuration(config: dict[Key, Any]) -> None:
        missing_keys = []
        if SONAR_TOKEN not in config:
            missing_keys.append(MissingProperty(SONAR_TOKEN, "--token"))

        if SONAR_PROJECT_KEY not in config:
            missing_keys.append(MissingProperty(SONAR_PROJECT_KEY, "--project-key"))

        if len(missing_keys) > 0:
            raise MissingPropertyException.from_missing_keys(*missing_keys)


def get_token(config: dict[Key, Any]) -> str:
    if SONAR_TOKEN not in config:
        raise MissingPropertyException(f'Missing property "{SONAR_TOKEN}"')
    return config[SONAR_TOKEN]
