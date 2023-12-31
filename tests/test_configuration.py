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
import os
import unittest
from unittest.mock import patch, Mock
from py_sonar_scanner.configuration import Configuration
from py_sonar_scanner.logger import ApplicationLogger

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_TOML_FILE = "test_toml_file.toml"
SAMPLE_SCANNER_PATH = "path/to/scanner/py-sonar-scanner"


class TestConfiguration(unittest.TestCase):
    @patch("py_sonar_scanner.configuration.sys")
    def test_argument_parsing(self, mock_sys):
        configuration = Configuration()
        self.assertFalse(configuration.is_debug())

        mock_sys.argv = [SAMPLE_SCANNER_PATH]
        configuration.setup()
        self.assertListEqual(configuration.scan_arguments, [])

        mock_sys.argv = [SAMPLE_SCANNER_PATH, "-DSomeJVMArg"]
        configuration.setup()
        self.assertListEqual(configuration.scan_arguments, ["-DSomeJVMArg"])

        mock_sys.argv = [
            SAMPLE_SCANNER_PATH,
            "-DSomeJVMArg",
            "-DAnotherJVMArg",
            "-dNotAJVMArg",
            "-SomeNonsense",
        ]
        configuration.setup()
        self.assertListEqual(
            configuration.scan_arguments, ["-DSomeJVMArg", "-DAnotherJVMArg", "-dNotAJVMArg", "-SomeNonsense"]
        )

        mock_sys.argv = [SAMPLE_SCANNER_PATH, f"-Dtoml.path={CURRENT_DIR}/resources/pyproject.toml"]
        configuration.setup()
        self.assertListEqual(
            configuration.scan_arguments,
            ["-Dsonar.a=b", "-Dsonar.c=d", f"-Dtoml.path={CURRENT_DIR}/resources/pyproject.toml"],
        )

        mock_sys.argv = [SAMPLE_SCANNER_PATH, f"-Dproject.home={CURRENT_DIR}/resources/"]
        configuration.setup()
        self.assertListEqual(
            configuration.scan_arguments, ["-Dsonar.a=b", "-Dsonar.c=d", f"-Dproject.home={CURRENT_DIR}/resources/"]
        )

        mock_sys.argv = [SAMPLE_SCANNER_PATH, "-Dproject.home=tests2"]
        configuration.setup()
        self.assertListEqual(configuration.scan_arguments, ["-Dproject.home=tests2"])

        mock_sys.argv = [SAMPLE_SCANNER_PATH, "-Dproject.home=tests=2"]
        configuration.setup()
        self.assertListEqual(configuration.scan_arguments, ["-Dproject.home=tests=2"])

        mock_sys.argv = [SAMPLE_SCANNER_PATH, "-X"]
        configuration.setup()
        self.assertTrue(configuration.is_debug())

    @patch("py_sonar_scanner.configuration.sys")
    def test_dict_with_no_valid_values(self, mock_sys):
        configuration = Configuration()
        mock_sys.argv = [SAMPLE_SCANNER_PATH]

        test_dict = {}
        configuration._read_toml_file = Mock(return_value=test_dict)
        configuration.setup()
        self.assertListEqual(configuration.scan_arguments, [])

        test_dict = {"tool": "some_property"}
        configuration._read_toml_file = Mock(return_value=test_dict)
        configuration.setup()
        self.assertListEqual(configuration.scan_arguments, [])

        test_dict = {"tool": {"sonar": "some_property"}}
        configuration._read_toml_file = Mock(return_value=test_dict)
        configuration.setup()
        self.assertListEqual(configuration.scan_arguments, [])

    @patch("py_sonar_scanner.configuration.sys")
    def test_dict_with_valid_values(self, mock_sys):
        configuration = Configuration()
        mock_sys.argv = [SAMPLE_SCANNER_PATH]

        test_dict = {"tool": {"sonar": {"property1": "value1"}}}
        configuration._read_toml_file = Mock(return_value=test_dict)
        configuration.setup()
        self.assertListEqual(configuration.scan_arguments, ["-Dsonar.property1=value1"])

        test_dict = {"tool": {"sonar": {"property1": "value1", "property2": "value2"}}}
        configuration._read_toml_file = Mock(return_value=test_dict)
        configuration.setup()
        self.assertListEqual(configuration.scan_arguments, ["-Dsonar.property1=value1", "-Dsonar.property2=value2"])

        test_dict = {"tool": {"sonar": {"property_class": {"property1": "value1"}}}}
        configuration._read_toml_file = Mock(return_value=test_dict)
        configuration.setup()
        self.assertListEqual(configuration.scan_arguments, ["-Dsonar.property_class.property1=value1"])

        test_dict = {"tool": {"sonar": {"property1": "value1", "property_class": {"sub_property": "sub_value"}}}}
        configuration._read_toml_file = Mock(return_value=test_dict)
        configuration.setup()
        self.assertListEqual(
            configuration.scan_arguments, ["-Dsonar.property1=value1", "-Dsonar.property_class.sub_property=sub_value"]
        )

    @patch("py_sonar_scanner.configuration.sys")
    def test_toml_with_valid_values(self, mock_sys):
        configuration = Configuration()
        toml_file_path = os.path.join(CURRENT_DIR, "resources", TEST_TOML_FILE)
        mock_sys.argv = [SAMPLE_SCANNER_PATH, f"-Dtoml.path={toml_file_path}"]
        configuration.setup()
        self.assertListEqual(
            configuration.scan_arguments,
            [
                "-Dsonar.property1=value1",
                "-Dsonar.property2=value2",
                "-Dsonar.property_class.property1=value1",
                f"-Dtoml.path={CURRENT_DIR}/resources/test_toml_file.toml",
            ],
        )

    @patch("py_sonar_scanner.configuration.sys")
    def test_duplicate_values_toml_cli(self, mock_sys):
        configuration = Configuration()
        toml_file_path = os.path.join(CURRENT_DIR, "resources", TEST_TOML_FILE)
        mock_sys.argv = [SAMPLE_SCANNER_PATH, f"-Dtoml.path={toml_file_path}", "-Dsonar.property1=value1"]
        configuration.setup()
        self.assertListEqual(
            configuration.scan_arguments,
            [
                "-Dsonar.property1=value1",
                "-Dsonar.property2=value2",
                "-Dsonar.property_class.property1=value1",
                f"-Dtoml.path={CURRENT_DIR}/resources/test_toml_file.toml",
                "-Dsonar.property1=value1",
            ],
        )

    @patch("builtins.open")
    @patch("py_sonar_scanner.configuration.sys")
    def test_error_while_reading_toml_file(self, mock_sys, mock_open):
        toml_file_path = os.path.join(CURRENT_DIR, "resources", TEST_TOML_FILE)
        mock_sys.argv = ["path/to/scanner/py-sonar-scanner", f"-Dtoml.path={toml_file_path}"]

        mock_open.side_effect = OSError("Test error while opening file.")
        with self.assertLogs(ApplicationLogger.get_logger()) as log:
            configuration = Configuration()
            configuration.setup()

            self.assertListEqual(
                configuration.scan_arguments,
                [
                    f"-Dtoml.path={CURRENT_DIR}/resources/test_toml_file.toml",
                ],
            )

            self.assertEqual(
                "Error while opening .toml file: Test error while opening file.", log.records[0].getMessage()
            )
