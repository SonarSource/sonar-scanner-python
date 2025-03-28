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

from pyfakefs.fake_filesystem_unittest import TestCase
from pysonar_scanner.configuration.pyproject_toml import TomlConfigurationLoader


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

    def test_load_malformed_toml_file(self):
        self.fs.create_file(
            "pyproject.toml",
            contents="""
            [tool.sonar
            sonar.projectKey = "my-project"
            """,
        )
        properties = TomlConfigurationLoader.load(Path("."))

        self.assertEqual(len(properties.sonar_properties), 0)

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

    def test_load_toml_file_project_content(self):
        self.fs.create_file(
            "pyproject.toml",
            contents=(
                """
                [project]
                name = "My Overridden Project Name"
                description = "My Project Description"
                requires-python = ["3.6", "3.7", "3.8"]
                [tool.sonar]
                project-key = "my-project"
                project-name = "My Project"
                """
            ),
        )
        properties = TomlConfigurationLoader.load(Path("."))

        self.assertEqual(properties.sonar_properties.get("sonar.projectKey"), "my-project")
        self.assertEqual(properties.sonar_properties.get("sonar.projectName"), "My Project")
        self.assertEqual(properties.project_properties.get("sonar.projectName"), "My Overridden Project Name")
        self.assertEqual(properties.project_properties.get("sonar.projectDescription"), "My Project Description")
        self.assertEqual(properties.project_properties.get("sonar.python.version"), "3.6,3.7,3.8")
