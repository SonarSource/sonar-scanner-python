#
# Sonar Scanner Python
# Copyright (C) 2011-2023 SonarSource SA.
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
import unittest
from unittest.mock import patch
from py_sonar_scanner.configuration import Configuration


class TestConfiguration(unittest.TestCase):
    @patch("py_sonar_scanner.configuration.sys")
    def test_argument_parsing(self, mock_sys):
        configuration = Configuration()

        mock_sys.argv = ["path/to/scanner/py-sonar-scanner"]
        configuration.setup()
        self.assertListEqual(configuration.scan_arguments, [])

        mock_sys.argv = ["path/to/scanner/py-sonar-scanner", "-DSomeJVMArg"]
        configuration.setup()
        self.assertListEqual(configuration.scan_arguments, ["-DSomeJVMArg"])

        mock_sys.argv = [
            "path/to/scanner/py-sonar-scanner",
            "-DSomeJVMArg",
            "-DAnotherJVMArg",
            "-dNotAJVMArg",
            "-SomeNonsense",
        ]
        configuration.setup()
        self.assertListEqual(
            configuration.scan_arguments, ["-DSomeJVMArg", "-DAnotherJVMArg", "-dNotAJVMArg", "-SomeNonsense"]
        )

        mock_sys.argv = ["path/to/scanner/py-sonar-scanner", "-Dtoml.path=tests/resources/pyproject.toml"]
        configuration.setup()
        self.assertListEqual(
            configuration.scan_arguments, ["-Dtoml.path=tests/resources/pyproject.toml", "-Dsonar.a=b", "-Dsonar.c=d"]
        )

        mock_sys.argv = ["path/to/scanner/py-sonar-scanner", "-Dproject.home=tests/resources/"]
        configuration.setup()
        self.assertListEqual(
            configuration.scan_arguments, ["-Dproject.home=tests/resources/", "-Dsonar.a=b", "-Dsonar.c=d"]
        )

        mock_sys.argv = ["path/to/scanner/py-sonar-scanner", "-Dproject.home=tests2"]
        configuration.setup()
        self.assertListEqual(configuration.scan_arguments, ["-Dproject.home=tests2"])

        mock_sys.argv = ["path/to/scanner/py-sonar-scanner", "-Dproject.home=tests=2"]
        configuration.setup()
        self.assertListEqual(configuration.scan_arguments, ["-Dproject.home=tests=2"])
