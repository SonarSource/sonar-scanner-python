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
from io import StringIO

from pysonar_scanner.configuration import CliConfigurationLoader


class TestCliConfigurationLoader(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    @patch("sys.argv", ["myscript.py", "--token", "myToken", "--sonar-project-key", "myProjectKey"])
    def test_minimal_cli_args(self):
        configuration = CliConfigurationLoader.load()

        expected_configuration = {
            "sonar.token": "myToken",
            "sonar.projectKey": "myProjectKey",
        }
        self.assertDictEqual(configuration, expected_configuration)

    def test_alternative_cli_args(self):
        alternatives = [
            ["-t", "myToken", "-v", "--sonar-project-key", "myProjectKey"],
            ["--sonar-token", "myToken", "--sonar-verbose", "--sonar-project-key", "myProjectKey"],
        ]
        for alternative in alternatives:
            with patch("sys.argv", ["myscript.py", *alternative]), patch("sys.stderr", new=StringIO()):
                configuration = CliConfigurationLoader.load()
                expected_configuration = {
                    "sonar.token": "myToken",
                    "sonar.verbose": True,
                    "sonar.projectKey": "myProjectKey",
                }
                self.assertDictEqual(configuration, expected_configuration)

    def test_multiple_alias_cli_args(self):
        alternatives = [
            ["-t", "overwrittenToken", "--sonar-token", "sonarToken"],
            ["--sonar-token", "overwrittenToken", "-t", "sonarToken"],
        ]
        for alternative in alternatives:
            with patch("sys.argv", ["myscript.py", *alternative]), patch("sys.stderr", new=StringIO()):
                configuration = CliConfigurationLoader.load()
                expected_configuration = {
                    "sonar.token": "sonarToken",
                }
                self.assertDictEqual(configuration, expected_configuration)

    @patch(
        "sys.argv",
        ["myscript.py", "-t", "myToken", "--sonar-project-key", "myProjectKey", "--sonar-scanner-os", "windows2"],
    )
    def test_impossible_os_choice(self):
        with patch("sys.stderr", new=StringIO()) as mock_stderr:
            with self.assertRaises(SystemExit):
                CliConfigurationLoader.load()

        error_output = mock_stderr.getvalue()
        self.assertIn("""argument --sonar-scanner-os: invalid choice: 'windows2'""", error_output)

    @patch(
        "sys.argv",
        [
            "myscript.py",
            "-t",
            "myToken",
            "--sonar-project-key",
            "myProjectKey",
            "-v",
            "--sonar-host-url",
            "mySonarHostUrl",
            "--sonar-region",
            "us",
            "--sonar-user-home",
            "mySonarUserHome",
            "--sonar-scanner-cloud-url",
            "mySonarScannerCloudUrl",
            "--sonar-scanner-api-url",
            "mySonarScannerApiUrl",
            "--sonar-scanner-os",
            "windows",
            "--sonar-scanner-arch",
            "x64",
            "--skip-jre-provisioning",
            "--sonar-scanner-java-exe-path",
            "mySonarScannerJavaExePath",
            "--sonar-scanner-java-opts",
            "mySonarScannerJavaOpts",
            "--sonar-scanner-internal-dump-to-file",
            "mySonarScannerInternalDumpToFile",
            "--sonar-scanner-internal-sq-version",
            "mySonarScannerInternalSqVersion",
            "--sonar-scanner-connect-timeout",
            "42",
            "--sonar-scanner-socket-timeout",
            "43",
            "--sonar-scanner-response-timeout",
            "44",
            "--sonar-scanner-truststore-path",
            "mySonarScannerTruststorePath",
            "--sonar-scanner-truststore-password",
            "mySonarScannerTruststorePassword",
            "--sonar-scanner-keystore-path",
            "mySonarScannerKeystorePath",
            "--sonar-scanner-keystore-password",
            "mySonarScannerKeystorePassword",
            "--sonar-scanner-proxy-host",
            "mySonarScannerProxyHost",
            "--sonar-scanner-proxy-port",
            "45",
            "--sonar-scanner-proxy-user",
            "mySonarScannerProxyUser",
            "--sonar-scanner-proxy-password",
            "mySonarScannerProxyPassword",
            "--sonar-project-base-dir",
            "mySonarProjectBaseDir",
        ],
    )
    def test_all_cli_args(self):
        configuration = CliConfigurationLoader.load()
        expected_configuration = {
            "sonar.token": "myToken",
            "sonar.projectKey": "myProjectKey",
            "sonar.verbose": True,
            "sonar.host.url": "mySonarHostUrl",
            "sonar.scanner.sonarcloudUrl": "mySonarScannerCloudUrl",
            "sonar.scanner.apiBaseUrl": "mySonarScannerApiUrl",
            "sonar.scanner.os": "windows",
            "sonar.scanner.arch": "x64",
            "sonar.scanner.connectTimeout": 42,
            "sonar.scanner.internal.dumpToFile": "mySonarScannerInternalDumpToFile",
            "sonar.scanner.internal.sqVersion": "mySonarScannerInternalSqVersion",
            "sonar.scanner.socketTimeout": 43,
            "sonar.scanner.responseTimeout": 44,
            "sonar.scanner.truststorePath": "mySonarScannerTruststorePath",
            "sonar.scanner.truststorePassword": "mySonarScannerTruststorePassword",
            "sonar.scanner.keystorePath": "mySonarScannerKeystorePath",
            "sonar.scanner.keystorePassword": "mySonarScannerKeystorePassword",
            "sonar.scanner.proxyHost": "mySonarScannerProxyHost",
            "sonar.scanner.proxyPort": 45,
            "sonar.scanner.proxyUser": "mySonarScannerProxyUser",
            "sonar.scanner.proxyPassword": "mySonarScannerProxyPassword",
            "sonar.scanner.skipJreProvisioning": True,
            "sonar.scanner.javaExePath": "mySonarScannerJavaExePath",
            "sonar.scanner.javaOpts": "mySonarScannerJavaOpts",
            "sonar.region": "us",
            "sonar.userHome": "mySonarUserHome",
            "sonar.projectBaseDir": "mySonarProjectBaseDir",
        }

        self.assertEqual(configuration, expected_configuration)
