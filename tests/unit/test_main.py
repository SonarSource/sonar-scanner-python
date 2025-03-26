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
from unittest.mock import patch

from pyfakefs import fake_filesystem_unittest as pyfakefs

from pysonar_scanner.__main__ import scan
from pysonar_scanner.configuration.configuration_loader import ConfigurationLoader
from pysonar_scanner.configuration.properties import (
    SONAR_PROJECT_KEY,
    SONAR_TOKEN,
    SONAR_HOST_URL,
    SONAR_SCANNER_API_BASE_URL,
    SONAR_SCANNER_SONARCLOUD_URL,
    SONAR_SCANNER_PROXY_PORT,
)
from pysonar_scanner.scannerengine import ScannerEngine


class TestMain(pyfakefs.TestCase):
    @patch.object(ConfigurationLoader, "load", return_value={SONAR_TOKEN: "myToken", SONAR_PROJECT_KEY: "myProjectKey"})
    @patch.object(ScannerEngine, "run", return_value=0)
    def test_minimal_success_run(self, run_mock, load_mock):
        exitcode = scan()
        self.assertEqual(exitcode, 0)

        # Verify that run was called with the expected configuration
        run_mock.assert_called_once()
        config = run_mock.call_args[0][0]  # Extract the configuration arg

        # Check expected configuration with a single assertion
        expected_config = {
            SONAR_TOKEN: "myToken",
            SONAR_PROJECT_KEY: "myProjectKey",
            SONAR_HOST_URL: "https://sonarcloud.io",
            SONAR_SCANNER_API_BASE_URL: "https://api.sonarcloud.io",
            SONAR_SCANNER_SONARCLOUD_URL: "https://sonarcloud.io",
            SONAR_SCANNER_PROXY_PORT: "443",
        }

        self.assertEqual(expected_config, config)
