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

from pysonar_scanner.configuration import ConfigurationLoader, Configuration, Scanner, Internal, Sonar


class TestMain(unittest.TestCase):

    @patch("sys.argv", ["myscript.py"])
    def test_missing_cli_args(self):
        with patch("sys.stderr", new=StringIO()) as mock_stderr, self.assertRaises(SystemExit):
            ConfigurationLoader.initialize_configuration()

        error_output = mock_stderr.getvalue()
        self.assertIn("the following arguments are required: -t/--token", error_output)

    @patch("sys.argv", ["myscript.py", "--token", "myToken"])
    def test_minimal_cli_args(self):
        configuration = ConfigurationLoader.initialize_configuration()
        expected_internal = Internal()
        expected_scanner = Scanner(internal=expected_internal)
        expected_sonar = Sonar(scanner=expected_scanner, token="myToken")
        expected_configuration = Configuration(sonar=expected_sonar)
        self.assertEqual(configuration, expected_configuration)

    @patch("sys.argv", ["myscript.py", "-t", "myToken", "-v"])
    def test_alternative_cli_args(self):
        alternatives = [["-t", "myToken", "-v"], ["--sonar-token", "myToken", "--sonar-verbose"]]
        for alternative in alternatives:
            with patch("sys.argv", ["myscript.py", *alternative]), patch("sys.stderr", new=StringIO()):
                configuration = ConfigurationLoader.initialize_configuration()
                expected_internal = Internal()
                expected_scanner = Scanner(internal=expected_internal)
                expected_sonar = Sonar(scanner=expected_scanner, token="myToken", verbose=True)
                expected_configuration = Configuration(sonar=expected_sonar)
                self.assertEqual(configuration, expected_configuration)

    @patch("sys.argv", ["myscript.py", "-t", "myToken", "--sonar-scanner-os", "windows2"])
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
            verbose=True,
            host_url="mySonarHostUrl",
            region="us",
            user_home="mySonarUserHome",
            project_base_dir="mySonarProjectBaseDir",
        )

        expected_configuration = Configuration(sonar=expected_sonar)
        self.assertEqual(configuration, expected_configuration)
