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

from pysonar_scanner.configuration import python_project_loader
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
        result = python_project_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "tests,integration")

    def test_load_from_pyproject_toml_single_entry(self):
        self.fs.create_file(
            "pyproject.toml",
            contents="""
            [tool.pytest.ini_options]
            testpaths = ["tests"]
            """,
        )
        self.fs.create_dir("tests")
        result = python_project_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "tests")

    def test_load_from_pyproject_toml_no_pytest_section(self):
        self.fs.create_file(
            "pyproject.toml",
            contents="""
            [tool.sonar]
            projectKey = "my-project"
            """,
        )
        result = python_project_loader.load(Path("."))
        self.assertNotIn(SONAR_TESTS, result)

    def test_load_from_pyproject_toml_empty_testpaths(self):
        self.fs.create_file(
            "pyproject.toml",
            contents="""
            [tool.pytest.ini_options]
            testpaths = []
            """,
        )
        result = python_project_loader.load(Path("."))
        self.assertNotIn(SONAR_TESTS, result)

    def test_load_from_pyproject_toml_nonexistent_path_not_returned(self):
        self.fs.create_file(
            "pyproject.toml",
            contents="""
            [tool.pytest.ini_options]
            testpaths = ["tests"]
            """,
        )
        # tests/ directory does NOT exist
        result = python_project_loader.load(Path("."))
        self.assertNotIn(SONAR_TESTS, result)

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
        result = python_project_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "tests")

    @patch("pysonar_scanner.configuration.python_project_loader.logging")
    def test_load_from_pyproject_toml_malformed(self, mock_logging):
        self.fs.create_file(
            "pyproject.toml",
            contents="this is not valid toml ][",
        )
        result = python_project_loader.load(Path("."))
        self.assertNotIn(SONAR_TESTS, result)
        mock_logging.debug.assert_called()

    # --- pytest.ini ---

    def test_load_from_pytest_ini(self):
        self.fs.create_file(
            "pytest.ini",
            contents="[pytest]\ntestpaths = tests integration\n",
        )
        self.fs.create_dir("tests")
        self.fs.create_dir("integration")
        result = python_project_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "tests,integration")

    def test_load_from_pytest_ini_multiline(self):
        self.fs.create_file(
            "pytest.ini",
            contents="[pytest]\ntestpaths =\n    tests\n    integration\n",
        )
        self.fs.create_dir("tests")
        self.fs.create_dir("integration")
        result = python_project_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "tests,integration")

    def test_load_from_pytest_ini_no_testpaths(self):
        self.fs.create_file(
            "pytest.ini",
            contents="[pytest]\naddopts = --strict-markers\n",
        )
        result = python_project_loader.load(Path("."))
        self.assertNotIn(SONAR_TESTS, result)

    def test_load_from_pytest_ini_nonexistent_path_not_returned(self):
        self.fs.create_file(
            "pytest.ini",
            contents="[pytest]\ntestpaths = tests\n",
        )
        # tests/ directory does NOT exist
        result = python_project_loader.load(Path("."))
        self.assertNotIn(SONAR_TESTS, result)

    # --- tox.ini ---

    def test_load_from_tox_ini(self):
        self.fs.create_file(
            "tox.ini",
            contents="[pytest]\ntestpaths = tests\n",
        )
        self.fs.create_dir("tests")
        result = python_project_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "tests")

    def test_load_from_tox_ini_multiple_paths(self):
        self.fs.create_file(
            "tox.ini",
            contents="[pytest]\ntestpaths = tests integration\n",
        )
        self.fs.create_dir("tests")
        self.fs.create_dir("integration")
        result = python_project_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "tests,integration")

    def test_load_from_tox_ini_multiline(self):
        self.fs.create_file(
            "tox.ini",
            contents="[pytest]\ntestpaths =\n    tests\n    integration\n",
        )
        self.fs.create_dir("tests")
        self.fs.create_dir("integration")
        result = python_project_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "tests,integration")

    def test_load_from_tox_ini_no_pytest_section(self):
        self.fs.create_file(
            "tox.ini",
            contents="[tox]\nenvlist = py39\n",
        )
        result = python_project_loader.load(Path("."))
        self.assertNotIn(SONAR_TESTS, result)

    def test_load_from_tox_ini_no_testpaths(self):
        self.fs.create_file(
            "tox.ini",
            contents="[pytest]\naddopts = --strict-markers\n",
        )
        result = python_project_loader.load(Path("."))
        self.assertNotIn(SONAR_TESTS, result)

    def test_load_from_tox_ini_nonexistent_path_not_returned(self):
        self.fs.create_file(
            "tox.ini",
            contents="[pytest]\ntestpaths = tests\n",
        )
        # tests/ directory does NOT exist
        result = python_project_loader.load(Path("."))
        self.assertNotIn(SONAR_TESTS, result)

    # --- setup.cfg ---

    def test_load_from_setup_cfg(self):
        self.fs.create_file(
            "setup.cfg",
            contents="[tool:pytest]\ntestpaths = tests\n",
        )
        self.fs.create_dir("tests")
        result = python_project_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "tests")

    def test_load_from_setup_cfg_multiple_paths(self):
        self.fs.create_file(
            "setup.cfg",
            contents="[tool:pytest]\ntestpaths = tests integration e2e\n",
        )
        self.fs.create_dir("tests")
        self.fs.create_dir("integration")
        self.fs.create_dir("e2e")
        result = python_project_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "tests,integration,e2e")

    def test_load_from_setup_cfg_no_pytest_section(self):
        self.fs.create_file(
            "setup.cfg",
            contents="[metadata]\nname = my-package\n",
        )
        result = python_project_loader.load(Path("."))
        self.assertNotIn(SONAR_TESTS, result)

    def test_load_from_setup_cfg_nonexistent_path_not_returned(self):
        self.fs.create_file(
            "setup.cfg",
            contents="[tool:pytest]\ntestpaths = tests\n",
        )
        # tests/ directory does NOT exist
        result = python_project_loader.load(Path("."))
        self.assertNotIn(SONAR_TESTS, result)

    # --- filesystem fallback ---

    def test_load_from_filesystem_tests_dir(self):
        self.fs.create_dir("tests")
        result = python_project_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "tests")

    def test_load_from_filesystem_test_dir(self):
        self.fs.create_dir("test")
        result = python_project_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "test")

    def test_load_from_filesystem_testing_dir(self):
        self.fs.create_dir("testing")
        result = python_project_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "testing")

    def test_load_from_filesystem_multiple_conventional_dirs(self):
        self.fs.create_dir("tests")
        self.fs.create_dir("test")
        result = python_project_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "tests,test")

    def test_load_from_filesystem_no_conventional_dir(self):
        self.fs.create_dir("src")
        result = python_project_loader.load(Path("."))
        self.assertNotIn(SONAR_TESTS, result)

    # --- nothing found ---

    def test_load_returns_empty_when_nothing_configured(self):
        result = python_project_loader.load(Path("."))
        self.assertEqual(result, {})

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
            contents="[pytest]\ntestpaths = from_ini\n",
        )
        self.fs.create_dir("from_toml")
        result = python_project_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "from_toml")

    def test_pytest_ini_takes_priority_over_tox_ini(self):
        self.fs.create_file(
            "pytest.ini",
            contents="[pytest]\ntestpaths = from_ini\n",
        )
        self.fs.create_file(
            "tox.ini",
            contents="[pytest]\ntestpaths = from_tox\n",
        )
        self.fs.create_dir("from_ini")
        result = python_project_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "from_ini")

    def test_tox_ini_takes_priority_over_setup_cfg(self):
        self.fs.create_file(
            "tox.ini",
            contents="[pytest]\ntestpaths = from_tox\n",
        )
        self.fs.create_file(
            "setup.cfg",
            contents="[tool:pytest]\ntestpaths = from_setup_cfg\n",
        )
        self.fs.create_dir("from_tox")
        result = python_project_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "from_tox")

    def test_pytest_ini_takes_priority_over_setup_cfg(self):
        self.fs.create_file(
            "pytest.ini",
            contents="[pytest]\ntestpaths = from_ini\n",
        )
        self.fs.create_file(
            "setup.cfg",
            contents="[tool:pytest]\ntestpaths = from_setup_cfg\n",
        )
        self.fs.create_dir("from_ini")
        result = python_project_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "from_ini")

    def test_setup_cfg_takes_priority_over_filesystem(self):
        self.fs.create_file(
            "setup.cfg",
            contents="[tool:pytest]\ntestpaths = from_setup_cfg\n",
        )
        self.fs.create_dir("from_setup_cfg")
        self.fs.create_dir("tests")
        result = python_project_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "from_setup_cfg")

    def test_config_without_testpaths_falls_through_to_filesystem(self):
        self.fs.create_file(
            "pyproject.toml",
            contents="""
            [tool.sonar]
            projectKey = "my-project"
            """,
        )
        self.fs.create_dir("tests")
        result = python_project_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "tests")

    def test_declared_nonexistent_testpaths_stops_chain(self):
        """When testpaths is explicitly declared but all paths are missing, the chain stops.
        No fallthrough to the next config source or filesystem convention."""
        self.fs.create_file(
            "pytest.ini",
            contents="[pytest]\ntestpaths = nonexistent\n",
        )
        self.fs.create_file(
            "setup.cfg",
            contents="[tool:pytest]\ntestpaths = from_setup_cfg\n",
        )
        self.fs.create_dir("from_setup_cfg")
        self.fs.create_dir("tests")  # filesystem fallback would find this
        result = python_project_loader.load(Path("."))
        self.assertNotIn(SONAR_TESTS, result)

    # --- custom base_dir ---

    def test_load_from_custom_base_dir(self):
        self.fs.create_dir("custom/path")
        self.fs.create_file(
            "custom/path/pytest.ini",
            contents="[pytest]\ntestpaths = custom_tests\n",
        )
        self.fs.create_dir("custom/path/custom_tests")
        result = python_project_loader.load(Path("custom/path"))
        self.assertEqual(result[SONAR_TESTS], "custom_tests")

    # --- absolute paths ---
    # Tests use /project as the explicit base_dir so that outside-root paths (/other/...)
    # are unambiguously not under the project and inside-root paths (/project/...) are
    # unambiguously convertible, regardless of the fake cwd.

    @patch("pysonar_scanner.configuration.python_project_loader.logging")
    def test_absolute_path_outside_project_root_emits_warning(self, mock_logging):
        self.fs.create_dir("/project")
        self.fs.create_file("/project/pytest.ini", contents="[pytest]\ntestpaths = /other/tests\n")
        self.fs.create_dir("/other/tests")
        python_project_loader.load(Path("/project"))
        warning_calls = [str(c) for c in mock_logging.warning.call_args_list]
        self.assertTrue(
            any("/other/tests" in c for c in warning_calls),
            f"Expected a warning mentioning the outside-root path, got: {warning_calls}",
        )

    def test_absolute_path_outside_project_root_stops_chain(self):
        """Absolute path outside the project root is discarded; chain stops — no filesystem fallback."""
        self.fs.create_dir("/project")
        self.fs.create_file("/project/pytest.ini", contents="[pytest]\ntestpaths = /other/tests\n")
        self.fs.create_dir("/other/tests")
        self.fs.create_dir("/project/tests")  # filesystem fallback would pick this up if chain continued
        result = python_project_loader.load(Path("/project"))
        self.assertNotIn(SONAR_TESTS, result)

    def test_absolute_path_inside_project_root_is_converted_to_relative(self):
        """Absolute path under the project root is relativised and used as sonar.tests."""
        self.fs.create_dir("/project/tests")
        self.fs.create_file("/project/pytest.ini", contents="[pytest]\ntestpaths = /project/tests\n")
        result = python_project_loader.load(Path("/project"))
        self.assertEqual(result[SONAR_TESTS], "tests")

    def test_absolute_path_inside_project_root_nested(self):
        """A deeper absolute path is relativised correctly."""
        self.fs.create_dir("/project/src/tests")
        self.fs.create_file("/project/pytest.ini", contents="[pytest]\ntestpaths = /project/src/tests\n")
        result = python_project_loader.load(Path("/project"))
        self.assertEqual(result[SONAR_TESTS], "src/tests")

    def test_absolute_path_mixed_with_valid_relative_path(self):
        """Valid relative path is kept even when another entry is outside the project root."""
        self.fs.create_dir("/project/tests")
        self.fs.create_file(
            "/project/pytest.ini",
            contents="[pytest]\ntestpaths = /other/tests tests\n",
        )
        result = python_project_loader.load(Path("/project"))
        self.assertEqual(result[SONAR_TESTS], "tests")

    def test_absolute_path_outside_root_in_pyproject_toml_stops_chain(self):
        self.fs.create_dir("/project")
        self.fs.create_file(
            "/project/pyproject.toml",
            contents="""
            [tool.pytest.ini_options]
            testpaths = ["/other/tests"]
            """,
        )
        self.fs.create_dir("/project/tests")  # filesystem fallback
        result = python_project_loader.load(Path("/project"))
        self.assertNotIn(SONAR_TESTS, result)

    def test_absolute_path_inside_root_in_pyproject_toml_is_converted(self):
        self.fs.create_dir("/project/tests")
        self.fs.create_file(
            "/project/pyproject.toml",
            contents="""
            [tool.pytest.ini_options]
            testpaths = ["/project/tests"]
            """,
        )
        result = python_project_loader.load(Path("/project"))
        self.assertEqual(result[SONAR_TESTS], "tests")

    def test_absolute_path_outside_root_in_tox_ini_stops_chain(self):
        self.fs.create_dir("/project")
        self.fs.create_file("/project/tox.ini", contents="[pytest]\ntestpaths = /other/tests\n")
        self.fs.create_dir("/project/tests")
        result = python_project_loader.load(Path("/project"))
        self.assertNotIn(SONAR_TESTS, result)

    def test_absolute_path_outside_root_in_setup_cfg_stops_chain(self):
        self.fs.create_dir("/project")
        self.fs.create_file("/project/setup.cfg", contents="[tool:pytest]\ntestpaths = /other/tests\n")
        self.fs.create_dir("/project/tests")
        result = python_project_loader.load(Path("/project"))
        self.assertNotIn(SONAR_TESTS, result)

    # --- Windows drive-letter paths (Windows only) ---
    # pathlib path semantics are platform-native: Path('C:/project').is_absolute() is False on POSIX,
    # so these tests only make sense on Windows where pathlib uses WindowsPath semantics.

    @unittest.skipUnless(sys.platform.startswith("win"), "Windows drive-letter path semantics")
    def test_windows_drive_path_inside_root_is_relativized(self):
        """C:\\project\\tests under C:\\project is relativised to 'tests'."""
        self.fs.create_dir("C:/project/tests")
        self.fs.create_file("C:/project/pytest.ini", contents="[pytest]\ntestpaths = C:\\project\\tests\n")
        result = python_project_loader.load(Path("C:/project"))
        self.assertEqual(result[SONAR_TESTS], "tests")

    @unittest.skipUnless(sys.platform.startswith("win"), "Windows drive-letter path semantics")
    def test_windows_drive_path_nested_inside_root_is_relativized(self):
        """C:\\project\\src\\tests under C:\\project is relativised to 'src/tests'."""
        self.fs.create_dir("C:/project/src/tests")
        self.fs.create_file("C:/project/pytest.ini", contents="[pytest]\ntestpaths = C:\\project\\src\\tests\n")
        result = python_project_loader.load(Path("C:/project"))
        self.assertEqual(result[SONAR_TESTS], "src/tests")

    @unittest.skipUnless(sys.platform.startswith("win"), "Windows drive-letter path semantics")
    @patch("pysonar_scanner.configuration.python_project_loader.logging")
    def test_windows_drive_path_outside_root_emits_warning(self, mock_logging):
        """C:\\other\\tests outside C:\\project emits a warning."""
        self.fs.create_dir("C:/project")
        self.fs.create_file("C:/project/pytest.ini", contents="[pytest]\ntestpaths = C:\\other\\tests\n")
        self.fs.create_dir("C:/other/tests")
        python_project_loader.load(Path("C:/project"))
        warning_calls = [str(c) for c in mock_logging.warning.call_args_list]
        self.assertTrue(
            any("other" in c for c in warning_calls),
            f"Expected a warning mentioning the outside-root path, got: {warning_calls}",
        )

    @unittest.skipUnless(sys.platform.startswith("win"), "Windows drive-letter path semantics")
    def test_windows_drive_path_outside_root_stops_chain(self):
        """C:\\other\\tests outside C:\\project is discarded; chain stops — no filesystem fallback."""
        self.fs.create_dir("C:/project")
        self.fs.create_file("C:/project/pytest.ini", contents="[pytest]\ntestpaths = C:\\other\\tests\n")
        self.fs.create_dir("C:/other/tests")
        self.fs.create_dir("C:/project/tests")  # filesystem fallback would pick this up if chain continued
        result = python_project_loader.load(Path("C:/project"))
        self.assertNotIn(SONAR_TESTS, result)

    @unittest.skipUnless(sys.platform.startswith("win"), "Windows drive-letter path semantics")
    @patch("pysonar_scanner.configuration.python_project_loader.logging")
    def test_windows_different_drive_emits_warning(self, mock_logging):
        """D:\\tests on a different drive than C:\\project emits a warning."""
        self.fs.create_dir("C:/project")
        self.fs.create_file("C:/project/pytest.ini", contents="[pytest]\ntestpaths = D:\\tests\n")
        self.fs.create_dir("D:/tests")
        python_project_loader.load(Path("C:/project"))
        warning_calls = [str(c) for c in mock_logging.warning.call_args_list]
        self.assertTrue(
            any("D:" in c for c in warning_calls),
            f"Expected a warning mentioning the different-drive path, got: {warning_calls}",
        )

    # --- file paths (not directories) ---

    @patch("pysonar_scanner.configuration.python_project_loader.logging")
    def test_file_path_in_testpaths_emits_debug_log(self, mock_logging):
        self.fs.create_file(
            "pytest.ini",
            contents="[pytest]\ntestpaths = tests/test_api.py\n",
        )
        self.fs.create_file("tests/test_api.py", contents="")
        python_project_loader.load(Path("."))
        debug_calls = [str(c) for c in mock_logging.debug.call_args_list]
        self.assertTrue(
            any("tests/test_api.py" in c for c in debug_calls),
            f"Expected a debug message mentioning the file path, got: {debug_calls}",
        )

    def test_file_path_in_testpaths_stops_chain(self):
        """A file path is dropped; if that leaves no valid directory paths the chain stops.
        tests/ is created implicitly by create_file and would be found by filesystem fallback
        if the chain continued — but it must not."""
        self.fs.create_file(
            "pytest.ini",
            contents="[pytest]\ntestpaths = tests/test_api.py\n",
        )
        self.fs.create_file("tests/test_api.py", contents="")
        # tests/ exists on disk (implicit from create_file), but testpaths names the file,
        # not the directory — chain stops at pytest.ini, filesystem fallback never runs.
        result = python_project_loader.load(Path("."))
        self.assertNotIn(SONAR_TESTS, result)

    def test_file_path_mixed_with_valid_directory_path(self):
        """Valid directory path is kept even when another entry points to a file."""
        self.fs.create_file(
            "pytest.ini",
            contents="[pytest]\ntestpaths = tests/test_api.py unit\n",
        )
        self.fs.create_file("tests/test_api.py", contents="")
        self.fs.create_dir("unit")
        result = python_project_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "unit")

    # --- declared-but-missing path warnings ---

    @patch("pysonar_scanner.configuration.python_project_loader.logging")
    def test_nonexistent_testpaths_in_pytest_ini_emits_warning(self, mock_logging):
        self.fs.create_file(
            "pytest.ini",
            contents="[pytest]\ntestpaths = nonexistent\n",
        )
        python_project_loader.load(Path("."))
        warning_calls = [str(c) for c in mock_logging.warning.call_args_list]
        self.assertTrue(
            any("nonexistent" in c for c in warning_calls),
            f"Expected a warning mentioning the missing path, got: {warning_calls}",
        )

    @patch("pysonar_scanner.configuration.python_project_loader.logging")
    def test_nonexistent_testpaths_in_pyproject_toml_emits_warning(self, mock_logging):
        self.fs.create_file(
            "pyproject.toml",
            contents="""
            [tool.pytest.ini_options]
            testpaths = ["nonexistent"]
            """,
        )
        python_project_loader.load(Path("."))
        warning_calls = [str(c) for c in mock_logging.warning.call_args_list]
        self.assertTrue(
            any("nonexistent" in c for c in warning_calls),
            f"Expected a warning mentioning the missing path, got: {warning_calls}",
        )

    @patch("pysonar_scanner.configuration.python_project_loader.logging")
    def test_nonexistent_testpaths_in_tox_ini_emits_warning(self, mock_logging):
        self.fs.create_file(
            "tox.ini",
            contents="[pytest]\ntestpaths = missing_dir\n",
        )
        python_project_loader.load(Path("."))
        warning_calls = [str(c) for c in mock_logging.warning.call_args_list]
        self.assertTrue(
            any("missing_dir" in c for c in warning_calls),
            f"Expected a warning mentioning the missing path, got: {warning_calls}",
        )

    @patch("pysonar_scanner.configuration.python_project_loader.logging")
    def test_nonexistent_testpaths_in_setup_cfg_emits_warning(self, mock_logging):
        self.fs.create_file(
            "setup.cfg",
            contents="[tool:pytest]\ntestpaths = missing_dir\n",
        )
        python_project_loader.load(Path("."))
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
            contents="[project]\nname = my-project\n",
        )
        self.fs.create_dir("tests")
        result = python_project_loader.load(Path("."))
        self.assertEqual(result[SONAR_TESTS], "tests")
