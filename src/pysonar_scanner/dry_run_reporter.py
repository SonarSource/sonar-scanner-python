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
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Optional

from pysonar_scanner.configuration.properties import (
    SONAR_PROJECT_KEY,
    SONAR_ORGANIZATION,
    SONAR_SOURCES,
    SONAR_TESTS,
    SONAR_PYTHON_COVERAGE_REPORT_PATHS,
    SONAR_PROJECT_NAME,
    SONAR_HOST_URL,
)


class DryRunReporter:
    @staticmethod
    def report_configuration(config: dict[str, Any]) -> None:
        logging.info("=" * 80)
        logging.info("DRY RUN MODE - Configuration Report")
        logging.info("=" * 80)

        DryRunReporter._log_section(
            "Project Configuration",
            {
                SONAR_PROJECT_KEY: config.get(SONAR_PROJECT_KEY),
                SONAR_PROJECT_NAME: config.get(SONAR_PROJECT_NAME),
                SONAR_ORGANIZATION: config.get(SONAR_ORGANIZATION, "N/A (likely SonarQube Server)"),
            },
        )

        DryRunReporter._log_section(
            "Server Configuration",
            {
                SONAR_HOST_URL: config.get(SONAR_HOST_URL, "N/A"),
            },
        )

        DryRunReporter._log_section(
            "Source Configuration",
            {
                SONAR_SOURCES: config.get(SONAR_SOURCES, "N/A"),
                SONAR_TESTS: config.get(SONAR_TESTS, "N/A"),
            },
        )

        DryRunReporter._log_section(
            "Coverage Configuration",
            {
                SONAR_PYTHON_COVERAGE_REPORT_PATHS: config.get(SONAR_PYTHON_COVERAGE_REPORT_PATHS, "N/A"),
            },
        )

    @staticmethod
    def report_validation_results(validation_result: "ValidationResult") -> int:
        logging.info("=" * 80)
        logging.info("DRY RUN MODE - Validation Results")
        logging.info("=" * 80)

        if validation_result.is_valid():
            for info in validation_result.infos:
                logging.info(f"✓ {info}")
            for warning in validation_result.warnings:
                logging.warning(f"• {warning}")
            logging.info("✓ Configuration validation PASSED")
            logging.info("=" * 80)
            return 0
        else:
            logging.warning("✗ Configuration validation FAILED with the following issues:")
            for error in validation_result.errors:
                logging.error(f"  • {error}")
            for warning in validation_result.warnings:
                logging.warning(f"  • {warning}")
            logging.info("=" * 80)
            return 1

    @staticmethod
    def _log_section(title: str, values: dict[str, Any]) -> None:
        logging.info(f"\n{title}:")
        for key, value in values.items():
            formatted_key = DryRunReporter._format_key(key)
            logging.info(f"  {formatted_key}: {value}")

    @staticmethod
    def _format_key(key: str) -> str:
        if key.startswith("sonar."):
            key = key[6:]
        key = key.replace(".", " ").replace("_", " ")
        key = re.sub(r"([a-z])([A-Z])", r"\1 \2", key)
        return key.title()


class ValidationResult:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.infos: list[str] = []

    def add_error(self, message: str) -> None:
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def add_info(self, message: str) -> None:
        self.infos.append(message)

    def is_valid(self) -> bool:
        return len(self.errors) == 0


class CoverageReportValidator:
    @staticmethod
    def validate_coverage_reports(
        coverage_paths: Optional[str],
        project_base_dir: str,
        validation_result: ValidationResult,
    ) -> None:
        if not coverage_paths:
            validation_result.add_warning("No coverage report paths specified")
            return

        base_path = Path(project_base_dir)
        report_paths = [p.strip() for p in coverage_paths.split(",")]

        for report_path in report_paths:
            CoverageReportValidator._validate_single_report(report_path, base_path, validation_result)

    @staticmethod
    def _validate_single_report(report_path: str, base_path: Path, validation_result: ValidationResult) -> None:
        # Resolve relative path
        full_path = base_path / report_path if not Path(report_path).is_absolute() else Path(report_path)

        if not full_path.exists():
            validation_result.add_error(f"Coverage report not found: {report_path} (resolved to {full_path})")
            return

        if not full_path.is_file():
            validation_result.add_error(f"Coverage report is not a file: {report_path} (resolved to {full_path})")
            return

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                tree = ET.parse(f)
                root = tree.getroot()
                if root.tag != "coverage":
                    validation_result.add_warning(
                        f"Coverage report root element is '{root.tag}', expected 'coverage' (Cobertura format)"
                    )
                else:
                    validation_result.add_info(f"Coverage report is valid Cobertura XML: {report_path}")
        except PermissionError:
            validation_result.add_error(f"Coverage report is not readable (permission denied): {report_path}")
        except UnicodeDecodeError:
            validation_result.add_warning(
                f"Coverage report may not be text-based (is it in binary format?): {report_path}"
            )
        except ET.ParseError as e:
            validation_result.add_error(
                f"Coverage report is not valid XML (Cobertura format): {report_path}\n  Parse error: {str(e)}"
            )
        except Exception as e:
            validation_result.add_error(f"Error validating coverage report format: {report_path}\n  Error: {str(e)}")
