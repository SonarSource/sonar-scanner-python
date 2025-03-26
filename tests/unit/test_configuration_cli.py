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

from pysonar_scanner.configuration.configuration_loader import CliConfigurationLoader
from pysonar_scanner.configuration.properties import (
    SONAR_HOST_URL,
    SONAR_REGION,
    SONAR_SCANNER_API_BASE_URL,
    SONAR_SCANNER_ARCH,
    SONAR_SCANNER_CONNECT_TIMEOUT,
    SONAR_SCANNER_INTERNAL_DUMP_TO_FILE,
    SONAR_SCANNER_INTERNAL_SQ_VERSION,
    SONAR_SCANNER_JAVA_EXE_PATH,
    SONAR_SCANNER_JAVA_OPTS,
    SONAR_SCANNER_KEYSTORE_PASSWORD,
    SONAR_SCANNER_KEYSTORE_PATH,
    SONAR_SCANNER_OS,
    SONAR_SCANNER_PROXY_HOST,
    SONAR_SCANNER_PROXY_PASSWORD,
    SONAR_SCANNER_PROXY_PORT,
    SONAR_SCANNER_PROXY_USER,
    SONAR_SCANNER_RESPONSE_TIMEOUT,
    SONAR_SCANNER_SKIP_JRE_PROVISIONING,
    SONAR_SCANNER_SOCKET_TIMEOUT,
    SONAR_SCANNER_SONARCLOUD_URL,
    SONAR_SCANNER_TRUSTSTORE_PASSWORD,
    SONAR_SCANNER_TRUSTSTORE_PATH,
    SONAR_PROJECT_BASE_DIR,
    SONAR_PROJECT_KEY,
    SONAR_TOKEN,
    SONAR_USER_HOME,
    SONAR_VERBOSE,
    SONAR_PROJECT_NAME,
)


class TestCliConfigurationLoader(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    @patch("sys.argv", ["myscript.py", "--token", "myToken", "--sonar-project-key", "myProjectKey"])
    def test_minimal_cli_args(self):
        configuration = CliConfigurationLoader.load()

        expected_configuration = {
            SONAR_TOKEN: "myToken",
            SONAR_PROJECT_KEY: "myProjectKey",
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
                    SONAR_TOKEN: "myToken",
                    SONAR_VERBOSE: True,
                    SONAR_PROJECT_KEY: "myProjectKey",
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
                    SONAR_TOKEN: "sonarToken",
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
        self.assertIn("""invalid choice: 'windows2'""", error_output)

    @patch(
        "sys.argv",
        [
            "myscript.py",
            "-t",
            "myToken",
            "--sonar-project-key",
            "myProjectKey",
            "--sonar-project-name",
            "myProjectName",
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
            SONAR_TOKEN: "myToken",
            SONAR_PROJECT_KEY: "myProjectKey",
            SONAR_PROJECT_NAME: "myProjectName",
            SONAR_VERBOSE: True,
            SONAR_HOST_URL: "mySonarHostUrl",
            SONAR_SCANNER_SONARCLOUD_URL: "mySonarScannerCloudUrl",
            SONAR_SCANNER_API_BASE_URL: "mySonarScannerApiUrl",
            SONAR_SCANNER_OS: "windows",
            SONAR_SCANNER_ARCH: "x64",
            SONAR_SCANNER_CONNECT_TIMEOUT: 42,
            SONAR_SCANNER_INTERNAL_DUMP_TO_FILE: "mySonarScannerInternalDumpToFile",
            SONAR_SCANNER_INTERNAL_SQ_VERSION: "mySonarScannerInternalSqVersion",
            SONAR_SCANNER_SOCKET_TIMEOUT: 43,
            SONAR_SCANNER_RESPONSE_TIMEOUT: 44,
            SONAR_SCANNER_TRUSTSTORE_PATH: "mySonarScannerTruststorePath",
            SONAR_SCANNER_TRUSTSTORE_PASSWORD: "mySonarScannerTruststorePassword",
            SONAR_SCANNER_KEYSTORE_PATH: "mySonarScannerKeystorePath",
            SONAR_SCANNER_KEYSTORE_PASSWORD: "mySonarScannerKeystorePassword",
            SONAR_SCANNER_PROXY_HOST: "mySonarScannerProxyHost",
            SONAR_SCANNER_PROXY_PORT: 45,
            SONAR_SCANNER_PROXY_USER: "mySonarScannerProxyUser",
            SONAR_SCANNER_PROXY_PASSWORD: "mySonarScannerProxyPassword",
            SONAR_SCANNER_SKIP_JRE_PROVISIONING: True,
            SONAR_SCANNER_JAVA_EXE_PATH: "mySonarScannerJavaExePath",
            SONAR_SCANNER_JAVA_OPTS: "mySonarScannerJavaOpts",
            SONAR_REGION: "us",
            SONAR_USER_HOME: "mySonarUserHome",
            SONAR_PROJECT_BASE_DIR: "mySonarProjectBaseDir",
        }

        self.assertEqual(configuration, expected_configuration)

    @patch(
        "sys.argv",
        [
            "myscript.py",
            "-Dsonar.token=myToken",
            "-Dsonar.projectKey=myProjectKey",
            "-Dsonar.verbose",
            "-Dsonar.host.url=mySonarHostUrl",
            "-Dsonar.scanner.cloudUrl=mySonarScannerCloudUrl",
            "-Dsonar.scanner.apiUrl=mySonarScannerApiUrl",
            "-Dsonar.scanner.os=windows",
            "-Dsonar.scanner.arch=x64",
            "-Dsonar.scanner.connectTimeout=42",
            "-Dsonar.scanner.internal.dumpToFile=mySonarScannerInternalDumpToFile",
            "-Dsonar.scanner.internal.sqVersion=mySonarScannerInternalSqVersion",
            "-Dsonar.scanner.socketTimeout=43",
            "-Dsonar.scanner.responseTimeout=44",
            "-Dsonar.scanner.truststorePath=mySonarScannerTruststorePath",
            "-Dsonar.scanner.truststorePassword=mySonarScannerTruststorePassword",
            "-Dsonar.scanner.keystorePath=mySonarScannerKeystorePath",
            "-Dsonar.scanner.keystorePassword=mySonarScannerKeystorePassword",
            "-Dsonar.scanner.proxyHost=mySonarScannerProxyHost",
            "-Dsonar.scanner.proxyPort=45",
            "-Dsonar.scanner.proxyUser=mySonarScannerProxyUser",
            "-Dsonar.scanner.proxyPassword=mySonarScannerProxyPassword",
            "-Dsonar.scanner.skipJreProvisioning",
            "-Dsonar.scanner.javaExePath=mySonarScannerJavaExePath",
            "-Dsonar.scanner.javaOpts=mySonarScannerJavaOpts",
            "-Dsonar.region=us",
            "-Dsonar.userHome=mySonarUserHome",
            "-Dsonar.projectBaseDir=mySonarProjectBaseDir",
        ],
    )
    def test_jvm_style_cli_args(self):
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
        for key in expected_configuration:
            self.assertEqual(configuration[key], expected_configuration[key])
        self.assertEqual(configuration, expected_configuration)
