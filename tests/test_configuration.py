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
from pysonar_scanner.exceptions import MissingKeyException


class TestConfigurationLoader(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    @patch("sys.argv", ["myscript.py", "--token", "myToken", "--sonar-project-key", "myProjectKey"])
    def test_defaults(self):
        configuration = ConfigurationLoader().load()
        expected_configuration = {
            "sonar.token": "myToken",
            "sonar.projectKey": "myProjectKey",
            "sonar.scanner.app": "python",
            "sonar.scanner.appVersion": "1.0",
            "sonar.scanner.bootstrapStartTime": configuration["sonar.scanner.bootstrapStartTime"],
            "sonar.verbose": False,
            "sonar.scanner.skipJreProvisioning": False,
            "sonar.userHome": "~/.sonar",
            "sonar.scanner.connectTimeout": 5,
            "sonar.scanner.socketTimeout": 60,
            "sonar.scanner.responseTimeout": 0,
            "sonar.scanner.keystorePassword": "changeit",
            "sonar.scanner.truststorePassword": "changeit",
        }
        self.assertDictEqual(configuration, expected_configuration)

    @patch("pysonar_scanner.configuration.get_static_default_properties", result={})
    @patch("sys.argv", ["myscript.py"])
    def test_no_defaults_in_configuration_loaders(self, get_static_default_properties_mock):
        config = ConfigurationLoader().load()
        self.assertDictEqual(config, {})

    def test_get_token(self):
        with self.subTest("Token is present"):
            self.assertEqual(configuration.get_token({"sonar.token": "myToken"}), "myToken")

        with self.subTest("Token is absent"), self.assertRaises(MissingKeyException):
            configuration.get_token({})
