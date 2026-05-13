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
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from pyfakefs.fake_filesystem_unittest import TestCase

from pysonar_scanner.configuration import test_paths_loader
from pysonar_scanner.configuration.properties import SONAR_TESTS


class TestPythonProjectLoader(TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    # --- pyproject.toml ---

    def test_load_from_pyproject_toml_list(self):
        self.fs.create_file(
            "pyproject.toml",
            contents="""
            [tool.pytest.ini_options]
            testpaths = ["tests", "integration"]
            """,
        )
        self.fs.create_dir("tests")
        self.fs.create_dir("integration")
        result, disable = test_paths_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "tests,integration")
        self.assertFalse(disable)

    def test_load_from_pyproject_toml_single_entry(self):
        self.fs.create_file(
            "pyproject.toml",
            contents="""
            [tool.pytest.ini_options]
            testpaths = ["tests"]
            """,
        )
        self.fs.create_dir("tests")
        result, disable = test_paths_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "tests")
        self.assertFalse(disable)

    def test_load_from_pyproject_toml_no_pytest_section(self):
        self.fs.create_file(
            "pyproject.toml",
            contents="""
            [tool.sonar]
            projectKey = "my-project"
            """,
        )
        result, disable = test_paths_loader.load(Path("."))
        self.assertNotIn(SONAR_TESTS, result)
        self.assertFalse(disable)

    def test_load_from_pyproject_toml_empty_testpaths_falls_through_to_filesystem(self):
        # testpaths = [] means "no path restriction" — same as key absent.
        # Our chain continues and the filesystem fallback still runs.
        self.fs.create_file(
            "pyproject.toml",
            contents="""
            [tool.pytest.ini_options]
            testpaths = []
            """,
        )
        self.fs.create_dir("tests")
        result, disable = test_paths_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "tests")
        self.assertFalse(disable)

    def test_load_from_pyproject_toml_nonexistent_path_not_returned(self):
        self.fs.create_file(
            "pyproject.toml",
            contents="""
            [tool.pytest.ini_options]
            testpaths = ["tests"]
            """,
        )
        # tests/ directory does NOT exist — user expressed intent but paths are invalid
        result, disable = test_paths_loader.load(Path("."))
        self.assertNotIn(SONAR_TESTS, result)
        self.assertTrue(disable)

    def test_load_from_pyproject_toml_filters_nonexistent_paths(self):
        self.fs.create_file(
            "pyproject.toml",
            contents="""
            [tool.pytest.ini_options]
            testpaths = ["tests", "nonexistent"]
            """,
        )
        self.fs.create_dir("tests")
        # nonexistent/ is not on disk — only tests/ should be returned
        result, disable = test_paths_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "tests")
        self.assertFalse(disable)

    @patch("pysonar_scanner.configuration.test_paths_loader.logging")
    def test_load_from_pyproject_toml_unexpected_testpaths_type(self, mock_logging):
        # An unexpected type (e.g. integer) is not user intent about test paths — we warn
        # and return None so the chain continues (filesystem fallback still runs).
        self.fs.create_file(
            "pyproject.toml",
            contents="""
            [tool.pytest.ini_options]
            testpaths = 1
            """,
        )
        self.fs.create_dir("tests")
        result, disable = test_paths_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "tests")
        self.assertFalse(disable)
        mock_logging.warning.assert_called()

    @patch("pysonar_scanner.configuration.test_paths_loader.logging")
    def test_load_from_pyproject_toml_malformed(self, mock_logging):
        self.fs.create_file(
            "pyproject.toml",
            contents="this is not valid toml ][",
        )
        result, disable = test_paths_loader.load(Path("."))
        self.assertNotIn(SONAR_TESTS, result)
        self.assertFalse(disable)
        mock_logging.debug.assert_called()

    # --- pytest.ini ---

    def test_load_from_pytest_ini(self):
        self.fs.create_file(
            "pytest.ini",
            contents="""\
[pytest]
testpaths = tests integration
""",
        )
        self.fs.create_dir("tests")
        self.fs.create_dir("integration")
        result, disable = test_paths_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "tests,integration")
        self.assertFalse(disable)

    def test_load_from_pytest_ini_multiline(self):
        self.fs.create_file(
            "pytest.ini",
            contents="""\
[pytest]
testpaths =
    tests
    integration
""",
        )
        self.fs.create_dir("tests")
        self.fs.create_dir("integration")
        result, disable = test_paths_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "tests,integration")
        self.assertFalse(disable)

    def test_load_from_pytest_ini_no_testpaths(self):
        self.fs.create_file(
            "pytest.ini",
            contents="""\
[pytest]
addopts = --strict-markers
""",
        )
        result, disable = test_paths_loader.load(Path("."))
        self.assertNotIn(SONAR_TESTS, result)
        self.assertFalse(disable)

    def test_load_from_pytest_ini_empty_testpaths_falls_through_to_filesystem(self):
        # Empty testpaths means "no path restriction" — chain continues to filesystem.
        self.fs.create_file(
            "pytest.ini",
            contents="""\
[pytest]
testpaths =
""",
        )
        self.fs.create_dir("tests")
        result, disable = test_paths_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "tests")
        self.assertFalse(disable)

    def test_load_from_pytest_ini_nonexistent_path_not_returned(self):
        self.fs.create_file(
            "pytest.ini",
            contents="""\
[pytest]
testpaths = tests
""",
        )
        # tests/ directory does NOT exist — user expressed intent but paths are invalid
        result, disable = test_paths_loader.load(Path("."))
        self.assertNotIn(SONAR_TESTS, result)
        self.assertTrue(disable)

    # --- tox.ini ---

    def test_load_from_tox_ini(self):
        self.fs.create_file(
            "tox.ini",
            contents="""\
[pytest]
testpaths = tests
""",
        )
        self.fs.create_dir("tests")
        result, disable = test_paths_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "tests")
        self.assertFalse(disable)

    def test_load_from_tox_ini_multiple_paths(self):
        self.fs.create_file(
            "tox.ini",
            contents="""\
[pytest]
testpaths = tests integration
""",
        )
        self.fs.create_dir("tests")
        self.fs.create_dir("integration")
        result, disable = test_paths_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "tests,integration")
        self.assertFalse(disable)

    def test_load_from_tox_ini_multiline(self):
        self.fs.create_file(
            "tox.ini",
            contents="""\
[pytest]
testpaths =
    tests
    integration
""",
        )
        self.fs.create_dir("tests")
        self.fs.create_dir("integration")
        result, disable = test_paths_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "tests,integration")
        self.assertFalse(disable)

    def test_load_from_tox_ini_no_pytest_section(self):
        self.fs.create_file(
            "tox.ini",
            contents="""\
[tox]
envlist = py39
""",
        )
        result, disable = test_paths_loader.load(Path("."))
        self.assertNotIn(SONAR_TESTS, result)
        self.assertFalse(disable)

    def test_load_from_tox_ini_no_testpaths(self):
        self.fs.create_file(
            "tox.ini",
            contents="""\
[pytest]
addopts = --strict-markers
""",
        )
        result, disable = test_paths_loader.load(Path("."))
        self.assertNotIn(SONAR_TESTS, result)
        self.assertFalse(disable)

    def test_load_from_tox_ini_nonexistent_path_not_returned(self):
        self.fs.create_file(
            "tox.ini",
            contents="""\
[pytest]
testpaths = tests
""",
        )
        # tests/ directory does NOT exist — user expressed intent but paths are invalid
        result, disable = test_paths_loader.load(Path("."))
        self.assertNotIn(SONAR_TESTS, result)
        self.assertTrue(disable)

    # --- setup.cfg ---

    def test_load_from_setup_cfg(self):
        self.fs.create_file(
            "setup.cfg",
            contents="""\
[tool:pytest]
testpaths = tests
""",
        )
        self.fs.create_dir("tests")
        result, disable = test_paths_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "tests")
        self.assertFalse(disable)

    def test_load_from_setup_cfg_multiple_paths(self):
        self.fs.create_file(
            "setup.cfg",
            contents="""\
[tool:pytest]
testpaths = tests integration e2e
""",
        )
        self.fs.create_dir("tests")
        self.fs.create_dir("integration")
        self.fs.create_dir("e2e")
        result, disable = test_paths_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "tests,integration,e2e")
        self.assertFalse(disable)

    def test_load_from_setup_cfg_no_pytest_section(self):
        self.fs.create_file(
            "setup.cfg",
            contents="""\
[metadata]
name = my-package
""",
        )
        result, disable = test_paths_loader.load(Path("."))
        self.assertNotIn(SONAR_TESTS, result)
        self.assertFalse(disable)

    def test_load_from_setup_cfg_nonexistent_path_not_returned(self):
        self.fs.create_file(
            "setup.cfg",
            contents="""\
[tool:pytest]
testpaths = tests
""",
        )
        # tests/ directory does NOT exist — user expressed intent but paths are invalid
        result, disable = test_paths_loader.load(Path("."))
        self.assertNotIn(SONAR_TESTS, result)
        self.assertTrue(disable)

    # --- filesystem fallback ---

    def test_load_from_filesystem_tests_dir(self):
        self.fs.create_dir("tests")
        result, disable = test_paths_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "tests")
        self.assertFalse(disable)

    def test_load_from_filesystem_test_dir(self):
        self.fs.create_dir("test")
        result, disable = test_paths_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "test")
        self.assertFalse(disable)

    def test_load_from_filesystem_testing_dir(self):
        self.fs.create_dir("testing")
        result, disable = test_paths_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "testing")
        self.assertFalse(disable)

    def test_load_from_filesystem_multiple_conventional_dirs(self):
        self.fs.create_dir("tests")
        self.fs.create_dir("test")
        result, disable = test_paths_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "tests,test")
        self.assertFalse(disable)

    def test_load_from_filesystem_no_conventional_dir(self):
        self.fs.create_dir("src")
        result, disable = test_paths_loader.load(Path("."))
        self.assertNotIn(SONAR_TESTS, result)
        self.assertFalse(disable)

    # --- nothing found ---

    def test_load_returns_empty_when_nothing_configured(self):
        result, disable = test_paths_loader.load(Path("."))
        self.assertEqual(result, {})
        self.assertFalse(disable)

    # --- priority order ---

    def test_pyproject_toml_takes_priority_over_pytest_ini(self):
        self.fs.create_file(
            "pyproject.toml",
            contents="""
            [tool.pytest.ini_options]
            testpaths = ["from_toml"]
            """,
        )
        self.fs.create_file(
            "pytest.ini",
            contents="""\
[pytest]
testpaths = from_ini
""",
        )
        self.fs.create_dir("from_toml")
        result, disable = test_paths_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "from_toml")
        self.assertFalse(disable)

    def test_pytest_ini_takes_priority_over_tox_ini(self):
        self.fs.create_file(
            "pytest.ini",
            contents="""\
[pytest]
testpaths = from_ini
""",
        )
        self.fs.create_file(
            "tox.ini",
            contents="""\
[pytest]
testpaths = from_tox
""",
        )
        self.fs.create_dir("from_ini")
        result, disable = test_paths_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "from_ini")
        self.assertFalse(disable)

    def test_tox_ini_takes_priority_over_setup_cfg(self):
        self.fs.create_file(
            "tox.ini",
            contents="""\
[pytest]
testpaths = from_tox
""",
        )
        self.fs.create_file(
            "setup.cfg",
            contents="""\
[tool:pytest]
testpaths = from_setup_cfg
""",
        )
        self.fs.create_dir("from_tox")
        result, disable = test_paths_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "from_tox")
        self.assertFalse(disable)

    def test_pytest_ini_takes_priority_over_setup_cfg(self):
        self.fs.create_file(
            "pytest.ini",
            contents="""\
[pytest]
testpaths = from_ini
""",
        )
        self.fs.create_file(
            "setup.cfg",
            contents="""\
[tool:pytest]
testpaths = from_setup_cfg
""",
        )
        self.fs.create_dir("from_ini")
        result, disable = test_paths_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "from_ini")
        self.assertFalse(disable)

    def test_setup_cfg_takes_priority_over_filesystem(self):
        self.fs.create_file(
            "setup.cfg",
            contents="""\
[tool:pytest]
testpaths = from_setup_cfg
""",
        )
        self.fs.create_dir("from_setup_cfg")
        self.fs.create_dir("tests")
        result, disable = test_paths_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "from_setup_cfg")
        self.assertFalse(disable)

    def test_config_without_testpaths_falls_through_to_filesystem(self):
        self.fs.create_file(
            "pyproject.toml",
            contents="""
            [tool.sonar]
            projectKey = "my-project"
            """,
        )
        self.fs.create_dir("tests")
        result, disable = test_paths_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "tests")
        self.assertFalse(disable)

    def test_declared_nonexistent_testpaths_stops_chain_and_disables_heuristic(self):
        """When testpaths is explicitly declared but all paths are missing, the chain stops
        and disable_heuristic is True — the user expressed intent, so sonar-python should
        not run its own heuristic on top."""
        self.fs.create_file(
            "pytest.ini",
            contents="""\
[pytest]
testpaths = nonexistent
""",
        )
        self.fs.create_file(
            "setup.cfg",
            contents="""\
[tool:pytest]
testpaths = from_setup_cfg
""",
        )
        self.fs.create_dir("from_setup_cfg")
        self.fs.create_dir("tests")  # filesystem fallback would find this
        result, disable = test_paths_loader.load(Path("."))
        self.assertNotIn(SONAR_TESTS, result)
        self.assertTrue(disable)

    def test_empty_testpaths_falls_through_to_filesystem(self):
        """testpaths = [] / empty testpaths means 'no path restriction' — chain continues,
        filesystem fallback still runs, disable_heuristic is False."""
        self.fs.create_file(
            "pytest.ini",
            contents="""\
[pytest]
testpaths =
""",
        )
        self.fs.create_file(
            "setup.cfg",
            contents="""\
[tool:pytest]
testpaths = from_setup_cfg
""",
        )
        self.fs.create_dir("from_setup_cfg")
        result, disable = test_paths_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "from_setup_cfg")
        self.assertFalse(disable)

    # --- custom base_dir ---

    def test_load_from_custom_base_dir(self):
        self.fs.create_dir("custom/path")
        self.fs.create_file(
            "custom/path/pytest.ini",
            contents="""\
[pytest]
testpaths = custom_tests
""",
        )
        self.fs.create_dir("custom/path/custom_tests")
        result, disable = test_paths_loader.load(Path("custom/path"))
        self.assertEqual(result[SONAR_TESTS], "custom_tests")
        self.assertFalse(disable)

    # --- absolute paths ---
    # Tests use /project as the explicit base_dir so that outside-root paths (/other/...)
    # are unambiguously not under the project and inside-root paths (/project/...) are
    # unambiguously convertible, regardless of the fake cwd.

    @patch("pysonar_scanner.configuration.test_paths_loader.logging")
    def test_absolute_path_outside_project_root_emits_warning(self, mock_logging):
        self.fs.create_dir("/project")
        self.fs.create_file(
            "/project/pytest.ini",
            contents="""\
[pytest]
testpaths = /other/tests
""",
        )
        self.fs.create_dir("/other/tests")
        test_paths_loader.load(Path("/project"))
        warning_calls = [str(c) for c in mock_logging.warning.call_args_list]
        self.assertTrue(
            any("/other/tests" in c for c in warning_calls),
            f"Expected a warning mentioning the outside-root path, got: {warning_calls}",
        )

    def test_absolute_path_outside_project_root_stops_chain_and_disables_heuristic(self):
        """Absolute path outside the project root is discarded; chain stops with disable_heuristic=True."""
        self.fs.create_dir("/project")
        self.fs.create_file(
            "/project/pytest.ini",
            contents="""\
[pytest]
testpaths = /other/tests
""",
        )
        self.fs.create_dir("/other/tests")
        self.fs.create_dir("/project/tests")  # filesystem fallback would pick this up if chain continued
        result, disable = test_paths_loader.load(Path("/project"))
        self.assertNotIn(SONAR_TESTS, result)
        self.assertTrue(disable)

    def test_absolute_path_inside_project_root_is_converted_to_relative(self):
        """Absolute path under the project root is relativised and used as sonar.tests."""
        self.fs.create_dir("/project/tests")
        self.fs.create_file(
            "/project/pytest.ini",
            contents="""\
[pytest]
testpaths = /project/tests
""",
        )
        result, disable = test_paths_loader.load(Path("/project"))
        self.assertEqual(result[SONAR_TESTS], "tests")
        self.assertFalse(disable)

    def test_absolute_path_inside_project_root_nested(self):
        """A deeper absolute path is relativised correctly."""
        self.fs.create_dir("/project/src/tests")
        self.fs.create_file(
            "/project/pytest.ini",
            contents="""\
[pytest]
testpaths = /project/src/tests
""",
        )
        result, disable = test_paths_loader.load(Path("/project"))
        self.assertEqual(result[SONAR_TESTS], "src/tests")
        self.assertFalse(disable)

    def test_absolute_path_mixed_with_valid_relative_path(self):
        """Valid relative path is kept even when another entry is outside the project root."""
        self.fs.create_dir("/project/tests")
        self.fs.create_file(
            "/project/pytest.ini",
            contents="""\
[pytest]
testpaths = /other/tests tests
""",
        )
        result, disable = test_paths_loader.load(Path("/project"))
        self.assertEqual(result[SONAR_TESTS], "tests")
        self.assertFalse(disable)

    def test_absolute_path_outside_root_in_pyproject_toml_stops_chain_and_disables_heuristic(self):
        self.fs.create_dir("/project")
        self.fs.create_file(
            "/project/pyproject.toml",
            contents="""
            [tool.pytest.ini_options]
            testpaths = ["/other/tests"]
            """,
        )
        self.fs.create_dir("/project/tests")  # filesystem fallback
        result, disable = test_paths_loader.load(Path("/project"))
        self.assertNotIn(SONAR_TESTS, result)
        self.assertTrue(disable)

    def test_absolute_path_inside_root_in_pyproject_toml_is_converted(self):
        self.fs.create_dir("/project/tests")
        self.fs.create_file(
            "/project/pyproject.toml",
            contents="""
            [tool.pytest.ini_options]
            testpaths = ["/project/tests"]
            """,
        )
        result, disable = test_paths_loader.load(Path("/project"))
        self.assertEqual(result[SONAR_TESTS], "tests")
        self.assertFalse(disable)

    def test_absolute_path_outside_root_in_tox_ini_stops_chain_and_disables_heuristic(self):
        self.fs.create_dir("/project")
        self.fs.create_file(
            "/project/tox.ini",
            contents="""\
[pytest]
testpaths = /other/tests
""",
        )
        self.fs.create_dir("/project/tests")
        result, disable = test_paths_loader.load(Path("/project"))
        self.assertNotIn(SONAR_TESTS, result)
        self.assertTrue(disable)

    def test_absolute_path_outside_root_in_setup_cfg_stops_chain_and_disables_heuristic(self):
        self.fs.create_dir("/project")
        self.fs.create_file(
            "/project/setup.cfg",
            contents="""\
[tool:pytest]
testpaths = /other/tests
""",
        )
        self.fs.create_dir("/project/tests")
        result, disable = test_paths_loader.load(Path("/project"))
        self.assertNotIn(SONAR_TESTS, result)
        self.assertTrue(disable)

    # --- Windows drive-letter paths (Windows only) ---
    # pathlib path semantics are platform-native: Path('C:/project').is_absolute() is False on POSIX,
    # so these tests only make sense on Windows where pathlib uses WindowsPath semantics.

    @unittest.skipUnless(sys.platform.startswith("win"), "Windows drive-letter path semantics")
    def test_windows_drive_path_inside_root_is_relativized(self):
        """C:\\project\\tests under C:\\project is relativised to 'tests'."""
        self.fs.create_dir("C:/project/tests")
        self.fs.create_file(
            "C:/project/pytest.ini",
            contents="""\
[pytest]
testpaths = C:\\project\\tests
""",
        )
        result, disable = test_paths_loader.load(Path("C:/project"))
        self.assertEqual(result[SONAR_TESTS], "tests")
        self.assertFalse(disable)

    @unittest.skipUnless(sys.platform.startswith("win"), "Windows drive-letter path semantics")
    def test_windows_drive_path_nested_inside_root_is_relativized(self):
        """C:\\project\\src\\tests under C:\\project is relativised to 'src/tests'."""
        self.fs.create_dir("C:/project/src/tests")
        self.fs.create_file(
            "C:/project/pytest.ini",
            contents="""\
[pytest]
testpaths = C:\\project\\src\\tests
""",
        )
        result, disable = test_paths_loader.load(Path("C:/project"))
        self.assertEqual(result[SONAR_TESTS], "src/tests")
        self.assertFalse(disable)

    @unittest.skipUnless(sys.platform.startswith("win"), "Windows drive-letter path semantics")
    @patch("pysonar_scanner.configuration.test_paths_loader.logging")
    def test_windows_drive_path_outside_root_emits_warning(self, mock_logging):
        """C:\\other\\tests outside C:\\project emits a warning."""
        self.fs.create_dir("C:/project")
        self.fs.create_file(
            "C:/project/pytest.ini",
            contents="""\
[pytest]
testpaths = C:\\other\\tests
""",
        )
        self.fs.create_dir("C:/other/tests")
        test_paths_loader.load(Path("C:/project"))
        warning_calls = [str(c) for c in mock_logging.warning.call_args_list]
        self.assertTrue(
            any("other" in c for c in warning_calls),
            f"Expected a warning mentioning the outside-root path, got: {warning_calls}",
        )

    @unittest.skipUnless(sys.platform.startswith("win"), "Windows drive-letter path semantics")
    def test_windows_drive_path_outside_root_stops_chain_and_disables_heuristic(self):
        """C:\\other\\tests outside C:\\project: chain stops with disable_heuristic=True."""
        self.fs.create_dir("C:/project")
        self.fs.create_file(
            "C:/project/pytest.ini",
            contents="""\
[pytest]
testpaths = C:\\other\\tests
""",
        )
        self.fs.create_dir("C:/other/tests")
        self.fs.create_dir("C:/project/tests")  # filesystem fallback would pick this up if chain continued
        result, disable = test_paths_loader.load(Path("C:/project"))
        self.assertNotIn(SONAR_TESTS, result)
        self.assertTrue(disable)

    @unittest.skipUnless(sys.platform.startswith("win"), "Windows drive-letter path semantics")
    @patch("pysonar_scanner.configuration.test_paths_loader.logging")
    def test_windows_different_drive_emits_warning(self, mock_logging):
        """D:\\tests on a different drive than C:\\project emits a warning."""
        self.fs.create_dir("C:/project")
        self.fs.create_file(
            "C:/project/pytest.ini",
            contents="""\
[pytest]
testpaths = D:\\tests
""",
        )
        self.fs.create_dir("D:/tests")
        test_paths_loader.load(Path("C:/project"))
        warning_calls = [str(c) for c in mock_logging.warning.call_args_list]
        self.assertTrue(
            any("D:" in c for c in warning_calls),
            f"Expected a warning mentioning the different-drive path, got: {warning_calls}",
        )

    # --- file paths (not directories) ---

    @patch("pysonar_scanner.configuration.test_paths_loader.logging")
    def test_file_path_in_testpaths_emits_debug_log(self, mock_logging):
        self.fs.create_file(
            "pytest.ini",
            contents="""\
[pytest]
testpaths = tests/test_api.py
""",
        )
        self.fs.create_file("tests/test_api.py", contents="")
        test_paths_loader.load(Path("."))
        debug_calls = [str(c) for c in mock_logging.debug.call_args_list]
        self.assertTrue(
            any("tests/test_api.py" in c for c in debug_calls),
            f"Expected a debug message mentioning the file path, got: {debug_calls}",
        )

    def test_file_path_in_testpaths_stops_chain_and_disables_heuristic(self):
        """A file path is dropped; if that leaves no valid directory paths the chain stops
        with disable_heuristic=True — user expressed intent about test paths."""
        self.fs.create_file(
            "pytest.ini",
            contents="""\
[pytest]
testpaths = tests/test_api.py
""",
        )
        self.fs.create_file("tests/test_api.py", contents="")
        # tests/ exists on disk (implicit from create_file), but testpaths names the file,
        # not the directory — chain stops at pytest.ini, filesystem fallback never runs.
        result, disable = test_paths_loader.load(Path("."))
        self.assertNotIn(SONAR_TESTS, result)
        self.assertTrue(disable)

    def test_file_path_mixed_with_valid_directory_path(self):
        """Valid directory path is kept even when another entry points to a file."""
        self.fs.create_file(
            "pytest.ini",
            contents="""\
[pytest]
testpaths = tests/test_api.py unit
""",
        )
        self.fs.create_file("tests/test_api.py", contents="")
        self.fs.create_dir("unit")
        result, disable = test_paths_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "unit")
        self.assertFalse(disable)

    # --- declared-but-missing path warnings ---

    @patch("pysonar_scanner.configuration.test_paths_loader.logging")
    def test_nonexistent_testpaths_in_pytest_ini_emits_warning(self, mock_logging):
        self.fs.create_file(
            "pytest.ini",
            contents="""\
[pytest]
testpaths = nonexistent
""",
        )
        test_paths_loader.load(Path("."))
        warning_calls = [str(c) for c in mock_logging.warning.call_args_list]
        self.assertTrue(
            any("nonexistent" in c for c in warning_calls),
            f"Expected a warning mentioning the missing path, got: {warning_calls}",
        )

    @patch("pysonar_scanner.configuration.test_paths_loader.logging")
    def test_nonexistent_testpaths_in_pyproject_toml_emits_warning(self, mock_logging):
        self.fs.create_file(
            "pyproject.toml",
            contents="""
            [tool.pytest.ini_options]
            testpaths = ["nonexistent"]
            """,
        )
        test_paths_loader.load(Path("."))
        warning_calls = [str(c) for c in mock_logging.warning.call_args_list]
        self.assertTrue(
            any("nonexistent" in c for c in warning_calls),
            f"Expected a warning mentioning the missing path, got: {warning_calls}",
        )

    @patch("pysonar_scanner.configuration.test_paths_loader.logging")
    def test_nonexistent_testpaths_in_tox_ini_emits_warning(self, mock_logging):
        self.fs.create_file(
            "tox.ini",
            contents="""\
[pytest]
testpaths = missing_dir
""",
        )
        test_paths_loader.load(Path("."))
        warning_calls = [str(c) for c in mock_logging.warning.call_args_list]
        self.assertTrue(
            any("missing_dir" in c for c in warning_calls),
            f"Expected a warning mentioning the missing path, got: {warning_calls}",
        )

    @patch("pysonar_scanner.configuration.test_paths_loader.logging")
    def test_nonexistent_testpaths_in_setup_cfg_emits_warning(self, mock_logging):
        self.fs.create_file(
            "setup.cfg",
            contents="""\
[tool:pytest]
testpaths = missing_dir
""",
        )
        test_paths_loader.load(Path("."))
        warning_calls = [str(c) for c in mock_logging.warning.call_args_list]
        self.assertTrue(
            any("missing_dir" in c for c in warning_calls),
            f"Expected a warning mentioning the missing path, got: {warning_calls}",
        )

    # --- filesystem fallback only when no testpaths key present ---

    def test_filesystem_fallback_skipped_when_config_has_no_testpaths_key_but_pyproject_present(self):
        """pyproject.toml present with no pytest section → fall through to filesystem."""
        self.fs.create_file(
            "pyproject.toml",
            contents="""\
[project]
name = my-project
""",
        )
        self.fs.create_dir("tests")
        result, disable = test_paths_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "tests")
        self.assertFalse(disable)
