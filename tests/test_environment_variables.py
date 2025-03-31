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
from json import JSONDecodeError
import unittest
from unittest.mock import MagicMock, patch

from pysonar_scanner.configuration import environment_variables
from pysonar_scanner.configuration.properties import (
    SONAR_HOST_URL,
    SONAR_REGION,
    SONAR_SCANNER_ARCH,
    SONAR_SCANNER_JAVA_OPTS,
    SONAR_SCANNER_OS,
    SONAR_TOKEN,
    SONAR_USER_HOME,
    SONAR_PROJECT_KEY,
)


class TestEnvironmentVariables(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_empty_environment(self):
        with patch.dict("os.environ", {}, clear=True):
            properties = environment_variables.load()
            self.assertEqual(len(properties), 0)
            self.assertDictEqual(properties, {})

    def test__environment_variables(self):
        env = {
            "SONAR_TOKEN": "my-token",
            "SONAR_HOST_URL": "https://sonarqube.example.com",
            "SONAR_USER_HOME": "/custom/sonar/home",
            "SONAR_SCANNER_JAVA_OPTS": "-Xmx1024m -XX:MaxPermSize=256m",
            "SONAR_REGION": "us",
        }
        with patch.dict("os.environ", env, clear=True):
            properties = environment_variables.load()
            expected_properties = {
                SONAR_TOKEN: "my-token",
                SONAR_HOST_URL: "https://sonarqube.example.com",
                SONAR_USER_HOME: "/custom/sonar/home",
                SONAR_SCANNER_JAVA_OPTS: "-Xmx1024m -XX:MaxPermSize=256m",
                SONAR_REGION: "us",
            }
            self.assertEqual(len(properties), 5)
            self.assertDictEqual(properties, expected_properties)

    def test_irrelevant_environment_variables(self):
        env = {"UNRELATED_VAR": "some-value", "PATH": "/usr/bin:/bin", "HOME": "/home/user"}
        with patch.dict("os.environ", env, clear=True):
            properties = environment_variables.load()
            self.assertEqual(len(properties), 0)
            self.assertDictEqual(properties, {})

    def test_mixed_environment_variables(self):
        env = {
            "SONAR_TOKEN": "my-token",
            "SONAR_HOST_URL": "https://sonarqube.example.com",
            "SONAR_PROJECT_KEY": "MyProjectKey",
            "UNRELATED_VAR": "some-value",
            "SONAR_SCANNER_OS": "linux",
            "SONAR_SCANNER_ARCH": "x64",
            "PATH": "/usr/bin:/bin",
        }
        with patch.dict("os.environ", env, clear=True):
            properties = environment_variables.load()
            expected_properties = {
                SONAR_TOKEN: "my-token",
                SONAR_HOST_URL: "https://sonarqube.example.com",
                SONAR_PROJECT_KEY: "MyProjectKey",
                SONAR_SCANNER_OS: "linux",
                SONAR_SCANNER_ARCH: "x64",
            }
            self.assertEqual(len(properties), 5)
            self.assertDictEqual(properties, expected_properties)

    def test_environment_variables_from_json_params(self):
        env = {
            "SONAR_SCANNER_JSON_PARAMS": '{"sonar.token": "json-token", "sonar.host.url": "https://json.example.com"}'
        }
        with patch.dict("os.environ", env, clear=True):
            properties = environment_variables.load()
            expected_properties = {
                SONAR_TOKEN: "json-token",
                SONAR_HOST_URL: "https://json.example.com",
            }
            self.assertEqual(len(properties), 2)
            self.assertDictEqual(properties, expected_properties)

    @patch("pysonar_scanner.configuration.environment_variables.app_logging.get_logger")
    def test_invalid_json_params(self, mock_get_logger):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        env = {"SONAR_SCANNER_JSON_PARAMS": '{"sonar.token": "json-token"'}
        with patch.dict("os.environ", env, clear=True):
            properties = environment_variables.load()
            self.assertEqual(len(properties), 0)
            self.assertDictEqual(properties, {})

        mock_logger.warning.assert_called_once_with(
            "The JSON in SONAR_SCANNER_JSON_PARAMS environment variable is invalid. The other environment variables will still be loaded.",
            unittest.mock.ANY,
        )

    def test_environment_variables_priority_over_json_params(self):
        env = {
            "SONAR_TOKEN": "regular-token",  # This should take priority
            "SONAR_HOST_URL": "https://regular.example.com",  # This should take priority
            "SONAR_SCANNER_JSON_PARAMS": '{"sonar.token": "json-token", "sonar.host.url": "https://json.example.com", "sonar.region": "eu"}',
        }
        with patch.dict("os.environ", env, clear=True):
            properties = environment_variables.load()
            expected_properties = {
                SONAR_TOKEN: "regular-token",  # Regular env var takes priority
                SONAR_HOST_URL: "https://regular.example.com",  # Regular env var takes priority
                SONAR_REGION: "eu",  # Only in JSON, so this value is used
            }
            self.assertEqual(len(properties), 3)
            self.assertDictEqual(properties, expected_properties)
