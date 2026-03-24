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
import platform
import unittest
from unittest.mock import patch

import pyfakefs.fake_filesystem_unittest as pyfakefs

from pysonar_scanner.__main__ import run_dry_run
from pysonar_scanner.configuration.properties import (
    SONAR_PROJECT_KEY,
    SONAR_PROJECT_NAME,
    SONAR_ORGANIZATION,
    SONAR_SOURCES,
    SONAR_TESTS,
    SONAR_PYTHON_COVERAGE_REPORT_PATHS,
    SONAR_PROJECT_BASE_DIR,
    SONAR_HOST_URL,
)
from pysonar_scanner.dry_run_reporter import (
    DryRunReporter,
    CoverageReportValidator,
    ValidationResult,
)


class TestValidationResult(unittest.TestCase):

    def test_valid_when_no_errors(self):
        result = ValidationResult()
        self.assertTrue(result.is_valid())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.warnings), 0)

    def test_invalid_when_errors_present(self):
        result = ValidationResult()
        result.add_error("Test error")
        self.assertFalse(result.is_valid())
        self.assertEqual(len(result.errors), 1)

    def test_can_add_warnings_without_becoming_invalid(self):
        result = ValidationResult()
        result.add_warning("Test warning")
        self.assertTrue(result.is_valid())
        self.assertEqual(len(result.warnings), 1)

    def test_can_add_infos(self):
        result = ValidationResult()
        result.add_info("Test info")
        self.assertTrue(result.is_valid())
        self.assertEqual(len(result.infos), 1)

    def test_multiple_errors_and_warnings(self):
        result = ValidationResult()
        result.add_error("Error 1")
        result.add_error("Error 2")
        result.add_warning("Warning 1")
        self.assertFalse(result.is_valid())
        self.assertEqual(len(result.errors), 2)
        self.assertEqual(len(result.warnings), 1)


class TestDryRunReporter(unittest.TestCase):

    @patch("pysonar_scanner.dry_run_reporter.logging")
    def test_report_configuration_logs_all_sections(self, mock_logging):
        config = {
            SONAR_PROJECT_KEY: "my-project",
            SONAR_PROJECT_NAME: "My Project",
            SONAR_ORGANIZATION: "my-org",
            SONAR_SOURCES: "src",
            SONAR_TESTS: "tests",
            SONAR_PYTHON_COVERAGE_REPORT_PATHS: "coverage.xml",
            SONAR_HOST_URL: "https://sonarqube.example.com",
        }

        DryRunReporter.report_configuration(config)

        logged_messages = [str(c) for c in mock_logging.info.call_args_list]
        joined = " ".join(logged_messages)
        self.assertIn("DRY RUN MODE - Configuration Report", joined)
        self.assertIn("my-project", joined)
        self.assertIn("My Project", joined)
        self.assertIn("my-org", joined)
        self.assertIn("src", joined)
        self.assertIn("tests", joined)
        self.assertIn("coverage.xml", joined)
        self.assertIn("https://sonarqube.example.com", joined)

    @patch("pysonar_scanner.dry_run_reporter.logging")
    def test_report_configuration_shows_na_for_missing_values(self, mock_logging):
        DryRunReporter.report_configuration({})

        logged_messages = [str(c) for c in mock_logging.info.call_args_list]
        joined = " ".join(logged_messages)
        self.assertIn("N/A", joined)

    @patch("pysonar_scanner.dry_run_reporter.logging")
    def test_report_validation_results_valid(self, mock_logging):
        result = ValidationResult()
        exit_code = DryRunReporter.report_validation_results(result)

        self.assertEqual(exit_code, 0)
        logged_messages = [str(c) for c in mock_logging.info.call_args_list]
        joined = " ".join(logged_messages)
        self.assertIn("PASSED", joined)

    @patch("pysonar_scanner.dry_run_reporter.logging")
    def test_report_validation_results_valid_with_infos_and_warnings(self, mock_logging):
        result = ValidationResult()
        result.add_info("Coverage report check passed: coverage.xml")
        result.add_warning("No tests directory specified")
        exit_code = DryRunReporter.report_validation_results(result)

        self.assertEqual(exit_code, 0)
        logged_messages = [str(c) for c in mock_logging.info.call_args_list]
        self.assertIn("PASSED", " ".join(logged_messages))
        mock_logging.warning.assert_called()

    @patch("pysonar_scanner.dry_run_reporter.logging")
    def test_report_validation_results_invalid(self, mock_logging):
        result = ValidationResult()
        result.add_error("Coverage file not found")
        result.add_warning("Unexpected root element")
        exit_code = DryRunReporter.report_validation_results(result)

        self.assertEqual(exit_code, 1)
        mock_logging.warning.assert_called()
        mock_logging.error.assert_called()

    def test_format_key_handles_camel_case(self):
        self.assertEqual(DryRunReporter._format_key("sonar.projectKey"), "Project Key")
        self.assertEqual(DryRunReporter._format_key("sonar.projectName"), "Project Name")

    def test_format_key_handles_dotted_paths(self):
        self.assertEqual(DryRunReporter._format_key("sonar.host.url"), "Host Url")
        self.assertEqual(
            DryRunReporter._format_key("sonar.python.coverage.reportPaths"), "Python Coverage Report Paths"
        )

    def test_format_key_handles_simple_keys(self):
        self.assertEqual(DryRunReporter._format_key("sonar.sources"), "Sources")
        self.assertEqual(DryRunReporter._format_key("sonar.organization"), "Organization")


class TestCoverageReportValidator(pyfakefs.TestCase):

    def setUp(self):
        self.setUpPyfakefs()

    def test_validate_no_paths(self):
        result = CoverageReportValidator.validate_coverage_reports(None, ".")

        self.assertTrue(result.is_valid())
        self.assertEqual(len(result.warnings), 1)
        self.assertIn("No coverage report paths specified", result.warnings[0])

    def test_validate_empty_string_paths(self):
        result = CoverageReportValidator.validate_coverage_reports("", ".")

        self.assertTrue(result.is_valid())
        self.assertEqual(len(result.warnings), 1)
        self.assertIn("No coverage report paths specified", result.warnings[0])

    def test_validate_single_report_file_not_found(self):
        self.fs.create_dir("/project")

        result = CoverageReportValidator.validate_coverage_reports("coverage.xml", "/project")

        self.assertFalse(result.is_valid())
        self.assertEqual(len(result.errors), 1)
        self.assertIn("not found", result.errors[0])

    def test_validate_single_report_valid_cobertura(self):
        self.fs.create_dir("/project")
        self.fs.create_file("/project/coverage.xml", contents='<?xml version="1.0"?>\n<coverage></coverage>')

        result = CoverageReportValidator.validate_coverage_reports("coverage.xml", "/project")

        self.assertTrue(result.is_valid())
        self.assertEqual(len(result.warnings), 0)
        self.assertEqual(len(result.infos), 1)
        self.assertIn("Coverage report check passed", result.infos[0])

    def test_validate_multiple_coverage_reports(self):
        self.fs.create_dir("/project")
        self.fs.create_file("/project/coverage1.xml", contents='<?xml version="1.0"?>\n<coverage></coverage>')
        self.fs.create_file("/project/coverage2.xml", contents='<?xml version="1.0"?>\n<coverage></coverage>')

        result = CoverageReportValidator.validate_coverage_reports("coverage1.xml, coverage2.xml", "/project")

        self.assertTrue(result.is_valid())

    def test_validate_report_not_a_file(self):
        self.fs.create_dir("/project")
        self.fs.create_dir("/project/coverage.xml")

        result = CoverageReportValidator.validate_coverage_reports("coverage.xml", "/project")

        self.assertFalse(result.is_valid())
        self.assertIn("not a file", result.errors[0])

    def test_validate_report_invalid_xml(self):
        self.fs.create_dir("/project")
        self.fs.create_file("/project/coverage.xml", contents="not valid xml")

        result = CoverageReportValidator.validate_coverage_reports("coverage.xml", "/project")

        self.assertFalse(result.is_valid())
        self.assertIn("not valid XML", result.errors[0])

    def test_validate_report_wrong_root_element(self):
        self.fs.create_dir("/project")
        self.fs.create_file("/project/coverage.xml", contents='<?xml version="1.0"?>\n<report></report>')

        result = CoverageReportValidator.validate_coverage_reports("coverage.xml", "/project")

        self.assertTrue(result.is_valid())
        self.assertEqual(len(result.warnings), 1)
        self.assertIn("report", result.warnings[0])
        self.assertIn("expected 'coverage'", result.warnings[0])

    @unittest.skipIf(platform.system() == "Windows", "Unix permissions not supported on Windows")
    def test_validate_report_permission_denied(self):
        self.fs.create_dir("/project")
        self.fs.create_file("/project/coverage.xml", contents='<?xml version="1.0"?>\n<coverage></coverage>')
        self.fs.chmod("/project/coverage.xml", mode=0o000, force_unix_mode=True)

        result = CoverageReportValidator.validate_coverage_reports("coverage.xml", "/project")

        self.assertFalse(result.is_valid())
        self.assertIn("permission denied", result.errors[0])

    def test_validate_report_binary_content(self):
        self.fs.create_dir("/project")
        self.fs.create_file("/project/coverage.xml", contents=b"\x80\x81\x82\x83\xff\xfe")

        result = CoverageReportValidator.validate_coverage_reports("coverage.xml", "/project")

        self.assertTrue(result.is_valid())
        self.assertEqual(len(result.warnings), 1)
        self.assertIn("binary format", result.warnings[0])
        self.assertEqual(len(result.errors), 0)

    def test_validate_mixed_valid_and_missing_reports(self):
        self.fs.create_dir("/project")
        self.fs.create_file("/project/exists.xml", contents='<?xml version="1.0"?>\n<coverage></coverage>')

        result = CoverageReportValidator.validate_coverage_reports("exists.xml, missing.xml", "/project")

        self.assertFalse(result.is_valid())
        self.assertEqual(len(result.errors), 1)
        self.assertIn("missing.xml", result.errors[0])


class TestRunDryRun(pyfakefs.TestCase):

    def setUp(self):
        self.setUpPyfakefs()

    @patch("pysonar_scanner.__main__.logging")
    def test_run_dry_run_no_coverage_reports(self, mock_logging):
        self.fs.create_dir("/project")
        config = {
            SONAR_PROJECT_KEY: "my-project",
            SONAR_PROJECT_BASE_DIR: "/project",
        }

        exit_code = run_dry_run(config)

        self.assertEqual(exit_code, 0)

    @patch("pysonar_scanner.__main__.logging")
    def test_run_dry_run_with_valid_coverage_reports(self, mock_logging):
        self.fs.create_dir("/project")
        self.fs.create_file("/project/coverage.xml", contents='<?xml version="1.0"?>\n<coverage></coverage>')
        config = {
            SONAR_PROJECT_KEY: "my-project",
            SONAR_PROJECT_BASE_DIR: "/project",
            SONAR_PYTHON_COVERAGE_REPORT_PATHS: "coverage.xml",
        }

        exit_code = run_dry_run(config)

        self.assertEqual(exit_code, 0)

    @patch("pysonar_scanner.__main__.logging")
    def test_run_dry_run_with_missing_coverage_reports(self, mock_logging):
        self.fs.create_dir("/project")
        config = {
            SONAR_PROJECT_KEY: "my-project",
            SONAR_PROJECT_BASE_DIR: "/project",
            SONAR_PYTHON_COVERAGE_REPORT_PATHS: "coverage.xml",
        }

        exit_code = run_dry_run(config)

        self.assertEqual(exit_code, 1)

    @patch("pysonar_scanner.__main__.logging")
    def test_run_dry_run_logs_dry_run_mode(self, mock_logging):
        self.fs.create_dir("/project")
        config = {SONAR_PROJECT_BASE_DIR: "/project"}

        run_dry_run(config)

        mock_logging.info.assert_any_call("Running in DRY RUN mode")
        mock_logging.info.assert_any_call("No server connection will be made and no analysis will be submitted")
