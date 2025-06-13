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
import os
import tempfile
import unittest

from tests.helpers.fs_helpers import TempFS
from pysonar_scanner.configuration import sonar_project_properties


class TestPropertiesFile(unittest.TestCase):
    def setUp(self):
        self._tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp_dir.cleanup)

        self._orig_cwd = os.getcwd()
        os.chdir(self._tmp_dir.name)
        self.addCleanup(lambda: os.chdir(self._orig_cwd))

        self.fs = TempFS(Path(self._tmp_dir.name))

    def test_load_sonar_project_properties(self):
        self.fs.create_file(
            "sonar-project.properties",
            contents=(
                "sonar.projectKey=my-project\n"
                "sonar.projectName=My Project\n"
                "sonar.sources=src # my sources\n"
                "sonar.sources=src\n"
                "sonar.exclusions=**/generated/**/*,**/deprecated/**/*,**/testdata/**/*\n"
                "sonar.some.unknownProperty=my_unknown_property_value\n"
            ),
        )
        properties = sonar_project_properties.load(Path("."))

        self.assertEqual(properties.get("sonar.projectKey"), "my-project")
        self.assertEqual(properties.get("sonar.projectName"), "My Project")
        self.assertEqual(properties.get("sonar.sources"), "src")
        self.assertEqual(properties.get("sonar.exclusions"), "**/generated/**/*,**/deprecated/**/*,**/testdata/**/*")
        self.assertEqual(properties.get("sonar.some.unknownProperty"), "my_unknown_property_value")

    def test_load_sonar_project_properties_custom_path(self):
        self.fs.create_file(
            "custom/path/sonar-project.properties",
            contents=("sonar.projectKey=my-project\n" "sonar.projectName=My Project\n"),
        )
        properties = sonar_project_properties.load(Path("custom/path"))

        self.assertEqual(properties.get("sonar.projectKey"), "my-project")
        self.assertEqual(properties.get("sonar.projectName"), "My Project")

    def test_load_missing_file(self):
        properties = sonar_project_properties.load(Path("custom/path"))
        self.assertEqual(len(properties), 0)

    def test_load_empty_file(self):
        self.fs.create_file("sonar-project.properties", contents="")
        properties = sonar_project_properties.load(Path("."))

        self.assertEqual(len(properties), 0)

    def test_load_with_malformed_lines_jproperties(self):
        self.fs.create_file(
            "sonar-project.properties",
            contents=(
                "valid.key=valid value\n"
                "malformed line without equals\n"
                "another.valid.key=another valid value\n"
                "=value without key\n"
            ),
        )

        properties = sonar_project_properties.load(Path("."))

        self.assertEqual(properties.get("valid.key"), "valid value")
        self.assertEqual(properties.get("another.valid.key"), "another valid value")
        self.assertEqual(properties.get("malformed"), "line without equals")
        self.assertEqual(properties.get(""), "value without key")
        self.assertEqual(len(properties), 4)
