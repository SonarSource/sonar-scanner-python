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
import os
from pathlib import Path
import subprocess
import sys
from unittest import mock
from unittest.mock import MagicMock, patch

import pytest

from pyfakefs.fake_filesystem_unittest import TestCase
from pysonar_scanner.configuration.pyproject_toml import TomlConfigurationLoader
from pysonar_scanner.exceptions import InconsistentConfiguration


class TestTomlFile(TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_load_toml_file_with_sonarqube_config(self):
        self.fs.create_file(
            "pyproject.toml",
            contents="""
            [tool.sonar]
            projectKey = "my-project"
            projectName = "My Project"
            sources = "src"
            exclusions = "**/generated/**/*,**/deprecated/**/*,**/testdata/**/*"
            some.unknownProperty = "unknown_property_value"
            """,
        )
        properties = TomlConfigurationLoader.load(Path("."))

        self.assertEqual(properties.sonar_properties.get("sonar.projectKey"), "my-project")
        self.assertEqual(properties.sonar_properties.get("sonar.projectName"), "My Project")
        self.assertEqual(properties.sonar_properties.get("sonar.sources"), "src")
        self.assertEqual(
            properties.sonar_properties.get("sonar.exclusions"), "**/generated/**/*,**/deprecated/**/*,**/testdata/**/*"
        )
        self.assertEqual(properties.sonar_properties.get("sonar.some.unknownProperty"), "unknown_property_value")

    def test_load_toml_file_kebab_case(self):
        self.fs.create_file(
            "pyproject.toml",
            contents="""
            [tool.sonar]
            project-key = "my-project"
            project-name = "My Project"
            """,
        )
        properties = TomlConfigurationLoader.load(Path("."))

        self.assertEqual(properties.sonar_properties.get("sonar.projectKey"), "my-project")
        self.assertEqual(properties.sonar_properties.get("sonar.projectName"), "My Project")

    @patch("pysonar_scanner.configuration.pyproject_toml.logging")
    def test_load_toml_file_kebab_case_unknown_properties(self, mock_logging):
        self.fs.create_file(
            "pyproject.toml",
            contents="""
            [tool.sonar]
            coverage-report-paths = "coverage.xml"
            some-unknown-property = "some-value"
            nested-property.some-nested-key = "nested-value"
            """,
        )
        properties = TomlConfigurationLoader.load(Path("."))

        self.assertEqual(properties.sonar_properties.get("sonar.coverageReportPaths"), "coverage.xml")
        self.assertEqual(properties.sonar_properties.get("sonar.someUnknownProperty"), "some-value")
        self.assertEqual(properties.sonar_properties.get("sonar.nestedProperty.someNestedKey"), "nested-value")

        mock_logging.debug.assert_any_call(
            "Converting kebab-case property 'sonar.coverage-report-paths' to camelCase: 'sonar.coverageReportPaths'"
        )
        mock_logging.debug.assert_any_call(
            "Converting kebab-case property 'sonar.some-unknown-property' to camelCase: 'sonar.someUnknownProperty'"
        )
        mock_logging.debug.assert_any_call(
            "Converting kebab-case property 'sonar.nested-property.some-nested-key' to camelCase: 'sonar.nestedProperty.someNestedKey'"
        )

    def test_load_toml_file_without_sonar_section(self):
        self.fs.create_file(
            "pyproject.toml",
            contents="""
            [tool.black]
            line-length = 88
            target-version = ["py38"]
            
            [tool.isort]
            profile = "black"
            """,
        )
        properties = TomlConfigurationLoader.load(Path("."))

        self.assertEqual(len(properties.sonar_properties), 0)

    def test_load_missing_file(self):
        properties = TomlConfigurationLoader.load(Path("."))
        self.assertEqual(len(properties.sonar_properties), 0)

    def test_load_empty_file(self):
        self.fs.create_file("pyproject.toml", contents="")
        properties = TomlConfigurationLoader.load(Path("."))

        self.assertEqual(len(properties.sonar_properties), 0)

    @patch("pysonar_scanner.configuration.pyproject_toml.logging")
    def test_load_malformed_toml_file(self, mock_logging):
        self.fs.create_file(
            "pyproject.toml",
            contents="""
            [tool.sonar
            sonar.projectKey = "my-project"
            """,
        )
        properties = TomlConfigurationLoader.load(Path("."))

        self.assertEqual(len(properties.sonar_properties), 0)
        mock_logging.warning.assert_called_once_with(
            "There was an error reading the pyproject.toml file. No properties from the TOML file were extracted. Error: Expected ']' at the end of a table declaration (at line 2, column 24)",
        )

    def test_load_toml_with_nested_values(self):
        self.fs.create_file(
            "pyproject.toml",
            contents="""
            [tool.sonar]
            projectKey = "my-project"
            
            [tool.sonar.python]
            version = "3.9,3.10,3.11,3.12,3.13"
            coverage.reportPaths = "coverage.xml"
            """,
        )
        properties = TomlConfigurationLoader.load(Path("."))

        self.assertEqual(properties.sonar_properties.get("sonar.projectKey"), "my-project")
        self.assertEqual(properties.sonar_properties.get("sonar.python.version"), "3.9,3.10,3.11,3.12,3.13")
        self.assertEqual(properties.sonar_properties.get("sonar.python.coverage.reportPaths"), "coverage.xml")

    def test_load_toml_file_from_custom_dir(self):
        self.fs.create_dir("custom/path")
        self.fs.create_file(
            "custom/path/pyproject.toml",
            contents="""
            [tool.sonar]
            projectKey = "custom-path-project"
            projectName = "Custom Path Project"
            """,
        )
        properties = TomlConfigurationLoader.load(Path("custom/path"))

        self.assertEqual(properties.sonar_properties.get("sonar.projectKey"), "custom-path-project")
        self.assertEqual(properties.sonar_properties.get("sonar.projectName"), "Custom Path Project")

    def test_load_toml_file_from_direct_file_path(self):
        self.fs.create_dir("custom/path")
        self.fs.create_file(
            "custom/path/pyproject.toml",
            contents="""
            [tool.sonar]
            projectKey = "direct-file-project"
            projectName = "Direct File Project"
            """,
        )
        properties = TomlConfigurationLoader.load(Path("custom/path/pyproject.toml"))

        self.assertEqual(properties.sonar_properties.get("sonar.projectKey"), "direct-file-project")
        self.assertEqual(properties.sonar_properties.get("sonar.projectName"), "Direct File Project")

    def test_load_toml_file_from_direct_file_path_missing(self):
        properties = TomlConfigurationLoader.load(Path("nonexistent/pyproject.toml"))
        self.assertEqual(len(properties.sonar_properties), 0)

    def test_required_missing_file_fails_with_path(self):
        for toml_path in (Path("missing"), Path("missing/pyproject.toml")):
            with self.subTest(path=toml_path), self.assertRaises(InconsistentConfiguration) as raised:
                TomlConfigurationLoader.load(toml_path, required=True)

            self.assertIn(str(Path("missing/pyproject.toml")), str(raised.exception))

    def test_required_malformed_file_fails_with_path(self):
        filepath = Path("selected/pyproject.toml")
        self.fs.create_file(filepath, contents="[tool.sonar\n")

        with self.assertRaises(InconsistentConfiguration) as raised:
            TomlConfigurationLoader.load(filepath, required=True)

        self.assertIn(str(filepath), str(raised.exception))

    def test_required_unreadable_file_fails_with_path(self):
        filepath = Path("selected/pyproject.toml")
        self.fs.create_file(filepath, contents='[tool.sonar]\nproject-key = "selected-key"\n')

        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            with self.assertRaises(InconsistentConfiguration) as raised:
                TomlConfigurationLoader.load(filepath, required=True)

        self.assertIn(str(filepath), str(raised.exception))
        self.assertIn("Permission denied", str(raised.exception))

    def test_load_toml_file_project_content(self):
        self.fs.create_file(
            "pyproject.toml",
            contents=("""
                [project]
                name = "My Overridden Project Name"
                description = "My Project Description"
                requires-python = ["3.6", "3.7", "3.8"]
                [tool.sonar]
                project-key = "my-project"
                project-name = "My Project"
                """),
        )
        properties = TomlConfigurationLoader.load(Path("."))

        self.assertEqual(properties.sonar_properties.get("sonar.projectKey"), "my-project")
        self.assertEqual(properties.sonar_properties.get("sonar.projectName"), "My Project")
        self.assertEqual(properties.project_properties.get("sonar.projectName"), "My Overridden Project Name")
        self.assertEqual(properties.project_properties.get("sonar.projectDescription"), "My Project Description")
        self.assertEqual(properties.project_properties.get("sonar.python.version"), "3.6,3.7,3.8")


def run_dry_run(directory: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    env = {key: value for key, value in os.environ.items() if not key.startswith("SONAR_")}
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[2] / "src")
    return subprocess.run(
        [sys.executable, "-c", "from pysonar_scanner.__main__ import main; main()", "--dry-run", *args],
        cwd=directory,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )


@pytest.mark.parametrize("toml_path", ["config", "config/pyproject.toml"])
def test_explicit_relative_toml_path_is_relative_to_invocation_directory(tmp_path: Path, toml_path: str):
    for directory, key in (("config", "selected-key"), ("project/config", "wrong-key")):
        config_dir = tmp_path / directory
        config_dir.mkdir(parents=True)
        (config_dir / "pyproject.toml").write_text(f'[tool.sonar]\nproject-key = "{key}"\n', encoding="utf-8")

    process = run_dry_run(
        tmp_path,
        ["--sonar-project-base-dir", "project", "--toml-path", toml_path],
    )

    assert process.returncode == 0, process.stdout + process.stderr
    assert "Project Key: selected-key" in process.stdout
    assert "wrong-key" not in process.stdout


@pytest.mark.parametrize("option", ["--toml-path", "-Dtoml-path"])
@pytest.mark.parametrize("problem", ["missing", "malformed"])
def test_explicit_unusable_toml_fails_without_falling_back(tmp_path: Path, option: str, problem: str):
    (tmp_path / "pyproject.toml").write_text('[tool.sonar]\nproject-key = "fallback-key"\n', encoding="utf-8")
    selected_dir = tmp_path / "selected"
    selected_dir.mkdir()
    if problem == "malformed":
        (selected_dir / "pyproject.toml").write_text("[tool.sonar\n", encoding="utf-8")

    process = run_dry_run(tmp_path, [f"{option}=selected"])

    assert process.returncode == 1, process.stdout + process.stderr
    assert str(Path("selected/pyproject.toml")) in process.stderr
    assert "DRY RUN MODE - Configuration Report" not in process.stdout
    assert "fallback-key" not in process.stdout


@pytest.mark.parametrize("problem", ["missing", "malformed"])
def test_implicit_unusable_toml_keeps_configuration_optional(tmp_path: Path, problem: str):
    if problem == "malformed":
        (tmp_path / "pyproject.toml").write_text("[tool.sonar\n", encoding="utf-8")

    process = run_dry_run(tmp_path, ["--sonar-project-key", "cli-key"])

    assert process.returncode == 0, process.stdout + process.stderr
    assert "Project Key: cli-key" in process.stdout
    if problem == "malformed":
        assert "There was an error reading the pyproject.toml file" in process.stdout
