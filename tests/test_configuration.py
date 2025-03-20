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
import unittest

from unittest.mock import patch

from pysonar_scanner.configuration import ConfigurationLoader
from pysonar_scanner import configuration
from pysonar_scanner.configuration.properties import (
    SONAR_PROJECT_KEY,
    SONAR_SCANNER_APP,
    SONAR_SCANNER_APP_VERSION,
    SONAR_SCANNER_BOOTSTRAP_START_TIME,
    SONAR_SCANNER_CONNECT_TIMEOUT,
    SONAR_SCANNER_KEYSTORE_PASSWORD,
    SONAR_SCANNER_RESPONSE_TIMEOUT,
    SONAR_SCANNER_SKIP_JRE_PROVISIONING,
    SONAR_SCANNER_SOCKET_TIMEOUT,
    SONAR_SCANNER_TRUSTSTORE_PASSWORD,
    SONAR_TOKEN,
    SONAR_USER_HOME,
    SONAR_VERBOSE,
)
from pysonar_scanner.exceptions import MissingKeyException


class TestConfigurationLoader(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    @patch("sys.argv", ["myscript.py", "--token", "myToken", "--sonar-project-key", "myProjectKey"])
    def test_defaults(self):
        configuration = ConfigurationLoader.load()
        expected_configuration = {
            SONAR_TOKEN: "myToken",
            SONAR_PROJECT_KEY: "myProjectKey",
            SONAR_SCANNER_APP: "python",
            SONAR_SCANNER_APP_VERSION: "1.0",
            SONAR_SCANNER_BOOTSTRAP_START_TIME: configuration[SONAR_SCANNER_BOOTSTRAP_START_TIME],
            SONAR_VERBOSE: False,
            SONAR_SCANNER_SKIP_JRE_PROVISIONING: False,
            SONAR_USER_HOME: "~/.sonar",
            SONAR_SCANNER_CONNECT_TIMEOUT: 5,
            SONAR_SCANNER_SOCKET_TIMEOUT: 60,
            SONAR_SCANNER_RESPONSE_TIMEOUT: 0,
            SONAR_SCANNER_KEYSTORE_PASSWORD: "changeit",
            SONAR_SCANNER_TRUSTSTORE_PASSWORD: "changeit",
        }
        self.assertDictEqual(configuration, expected_configuration)

    @patch("pysonar_scanner.configuration.get_static_default_properties", result={})
    @patch("sys.argv", ["myscript.py"])
    def test_no_defaults_in_configuration_loaders(self, get_static_default_properties_mock):
        config = ConfigurationLoader.load()
        self.assertDictEqual(config, {})

    def test_get_token(self):
        with self.subTest("Token is present"):
            self.assertEqual(configuration.get_token({SONAR_TOKEN: "myToken"}), "myToken")

        with self.subTest("Token is absent"), self.assertRaises(MissingKeyException):
            configuration.get_token({})
