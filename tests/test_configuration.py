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
import json
import time

from unittest.mock import patch
from io import StringIO

from pysonar_scanner.configuration import ConfigurationLoader, Configuration, JRECacheStatus, Scanner, Internal, Sonar


class TestMain(unittest.TestCase):

    @patch("sys.argv", ["myscript.py"])
    def test_missing_cli_args(self):
        with patch("sys.stderr", new=StringIO()) as mock_stderr, self.assertRaises(SystemExit):
            ConfigurationLoader.initialize_configuration()

        error_output = mock_stderr.getvalue()
        self.assertIn("the following arguments are required: -t/--token", error_output)

    @patch("sys.argv", ["myscript.py", "--token", "myToken", "--sonar-project-key", "myProjectKey"])
    def test_minimal_cli_args(self):
        configuration = ConfigurationLoader.initialize_configuration()
        expected_internal = Internal()
        expected_scanner = Scanner(internal=expected_internal)
        expected_sonar = Sonar(scanner=expected_scanner, token="myToken", project_key="myProjectKey")
        expected_configuration = Configuration(sonar=expected_sonar)
        self.assertEqual(configuration, expected_configuration)

    def test_alternative_cli_args(self):
        alternatives = [ ["-t", "myToken", "-v", "--sonar-project-key", "myProjectKey"], ["--sonar-token", "myToken", "--sonar-verbose", "--sonar-project-key", "myProjectKey"]]
        for alternative in alternatives:
            with patch("sys.argv", ["myscript.py", *alternative]), patch("sys.stderr", new=StringIO()):
                configuration = ConfigurationLoader.initialize_configuration()
                expected_internal = Internal()
                expected_scanner = Scanner(internal=expected_internal)
                expected_sonar = Sonar(scanner=expected_scanner, token="myToken", project_key="myProjectKey", verbose=True)
                expected_configuration = Configuration(sonar=expected_sonar)
                self.assertEqual(configuration, expected_configuration)

    @patch("sys.argv", ["myscript.py", "-t", "myToken", "--sonar-project-key", "myProjectKey", "--sonar-scanner-os", "windows2"])
    def test_impossible_os_choice(self):
        with patch("sys.stderr", new=StringIO()) as mock_stderr:
            with self.assertRaises(SystemExit):
                ConfigurationLoader.initialize_configuration()

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
        configuration = ConfigurationLoader.initialize_configuration()
        expected_internal = Internal(
            dump_to_file="mySonarScannerInternalDumpToFile", sq_version="mySonarScannerInternalSqVersion"
        )

        expected_scanner = Scanner(
            internal=expected_internal,
            os="windows",
            arch="x64",
            connect_timeout=42,
            socket_timeout=43,
            response_timeout=44,
            truststore_path="mySonarScannerTruststorePath",
            truststore_password="mySonarScannerTruststorePassword",
            keystore_path="mySonarScannerKeystorePath",
            keystore_password="mySonarScannerKeystorePassword",
            proxy_host="mySonarScannerProxyHost",
            proxy_port=45,
            proxy_user="mySonarScannerProxyUser",
            proxy_password="mySonarScannerProxyPassword",
            skip_jre_provisioning=True,
            java_exe_path="mySonarScannerJavaExePath",
            java_opts="mySonarScannerJavaOpts",
            sonarcloud_url="mySonarScannerCloudUrl",
            api_base_url="mySonarScannerApiUrl",
        )

        expected_sonar = Sonar(
            scanner=expected_scanner,
            token="myToken",
            project_key="myProjectKey",
            verbose=True,
            host_url="mySonarHostUrl",
            region="us",
            user_home="mySonarUserHome",
            project_base_dir="mySonarProjectBaseDir",
        )

        expected_configuration = Configuration(sonar=expected_sonar)
        self.assertEqual(configuration, expected_configuration)

    def test_minimal_json(self):
        minimal_json = Configuration(sonar=Sonar(token="myToken", project_key="myProjectKey")).to_json()

        minimal_dict = json.loads(minimal_json)
        self.assertIn("scannerProperties", minimal_dict)
        self.assertIn("sonar.scanner.bootstrapStartTime", [prop["key"] for prop in minimal_dict["scannerProperties"]])
        bootstrap_start_time = [
            prop["value"]
            for prop in minimal_dict["scannerProperties"]
            if prop["key"] == "sonar.scanner.bootstrapStartTime"
        ][0]
        self.assertAlmostEqual(
            bootstrap_start_time, int(time.time() * 1000), delta=1000 * 60
        )  # 1 minute delta between the configuration creation and this test

        expected_json = json.dumps(
            {
                "scannerProperties": [
                    {"key": "sonar.scanner.app", "value": "python"},
                    {"key": "sonar.scanner.appVersion", "value": "1.0"},
                    {"key": "sonar.token", "value": "myToken"},
                    {"key": "sonar.projectKey", "value": "myProjectKey"},
                    {"key": "sonar.verbose", "value": False},
                    {"key": "sonar.scanner.bootstrapStartTime", "value": bootstrap_start_time},
                ]
            }
        )
        expected_dict = json.loads(expected_json)
        self.assertDictEqual(minimal_dict, expected_dict)

    def test_full_json(self):
        internal = Internal(
            dump_to_file="mySonarScannerInternalDumpToFile", sq_version="mySonarScannerInternalSqVersion"
        )

        scanner = Scanner(
            internal=internal,
            os="windows",
            arch="x64",
            connect_timeout=42,
            socket_timeout=43,
            response_timeout=44,
            truststore_path="mySonarScannerTruststorePath",
            truststore_password="mySonarScannerTruststorePassword",
            keystore_path="mySonarScannerKeystorePath",
            keystore_password="mySonarScannerKeystorePassword",
            proxy_host="mySonarScannerProxyHost",
            proxy_port=45,
            proxy_user="mySonarScannerProxyUser",
            proxy_password="mySonarScannerProxyPassword",
            skip_jre_provisioning=True,
            java_exe_path="mySonarScannerJavaExePath",
            java_opts="mySonarScannerJavaOpts",
            sonarcloud_url="mySonarScannerCloudUrl",
            api_base_url="mySonarScannerApiUrl",
            was_engine_cache_hit=True,
            was_jre_cache_hit=JRECacheStatus.HIT,
        )

        sonar = Sonar(
            scanner=scanner,
            token="myToken",
            project_key="myProjectKey",
            verbose=True,
            host_url="mySonarHostUrl",
            region="us",
            user_home="mySonarUserHome",
            project_base_dir="mySonarProjectBaseDir",
        )

        full_configuration = Configuration(sonar=sonar)

        full_json = full_configuration.to_json()
        full_dict = json.loads(full_json)
        self.assertIn("scannerProperties", full_dict)
        self.assertIn("sonar.scanner.bootstrapStartTime", [prop["key"] for prop in full_dict["scannerProperties"]])
        bootstrap_start_time = [
            prop["value"]
            for prop in full_dict["scannerProperties"]
            if prop["key"] == "sonar.scanner.bootstrapStartTime"
        ][0]
        self.assertAlmostEqual(
            bootstrap_start_time, int(time.time() * 1000), delta=1000 * 60
        )  # 1 minute delta between the configuration creation and this test

        expected_json = json.dumps(
            {
                "scannerProperties": [
                    {"key": "sonar.scanner.app", "value": "python"},
                    {"key": "sonar.scanner.appVersion", "value": "1.0"},
                    {"key": "sonar.token", "value": "myToken"},
                    {"key": "sonar.projectKey", "value": "myProjectKey"},
                    {"key": "sonar.region", "value": "us"},
                    {"key": "sonar.host.url", "value": "mySonarHostUrl"},
                    {"key": "sonar.projectBaseDir", "value": "mySonarProjectBaseDir"},
                    {"key": "sonar.verbose", "value": True},
                    {"key": "sonar.userHome", "value": "mySonarUserHome"},
                    {"key": "sonar.scanner.apiBaseUrl", "value": "mySonarScannerApiUrl"},
                    {"key": "sonar.scanner.bootstrapStartTime", "value": bootstrap_start_time},
                    {"key": "sonar.scanner.os", "value": "windows"},
                    {"key": "sonar.scanner.arch", "value": "x64"},
                    {"key": "sonar.scanner.connectTimeout", "value": 42},
                    {"key": "sonar.scanner.socketTimeout", "value": 43},
                    {"key": "sonar.scanner.responseTimeout", "value": 44},
                    {"key": "sonar.scanner.truststorePath", "value": "mySonarScannerTruststorePath"},
                    {"key": "sonar.scanner.truststorePassword", "value": "mySonarScannerTruststorePassword"},
                    {"key": "sonar.scanner.keystorePath", "value": "mySonarScannerKeystorePath"},
                    {"key": "sonar.scanner.keystorePassword", "value": "mySonarScannerKeystorePassword"},
                    {"key": "sonar.scanner.proxyHost", "value": "mySonarScannerProxyHost"},
                    {"key": "sonar.scanner.proxyPort", "value": 45},
                    {"key": "sonar.scanner.proxyUser", "value": "mySonarScannerProxyUser"},
                    {"key": "sonar.scanner.proxyPassword", "value": "mySonarScannerProxyPassword"},
                    {"key": "sonar.scanner.wasJreCacheHit", "value": "HIT"},
                    {"key": "sonar.scanner.wasEngineCacheHit", "value": True},
                ]
            }
        )
        expected_dict = json.loads(expected_json)
        self.assertDictEqual(full_dict, expected_dict)
