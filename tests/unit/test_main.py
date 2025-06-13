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
import pathlib
from unittest.mock import patch, Mock
import unittest

from pysonar_scanner.__main__ import scan, check_version, create_jre
from pysonar_scanner.api import SQVersion, SonarQubeApi
from pysonar_scanner.cache import Cache
from pysonar_scanner.configuration.configuration_loader import ConfigurationLoader
from pysonar_scanner.configuration.properties import (
    SONAR_PROJECT_KEY,
    SONAR_TOKEN,
    SONAR_HOST_URL,
    SONAR_SCANNER_API_BASE_URL,
    SONAR_SCANNER_SONARCLOUD_URL,
    SONAR_SCANNER_PROXY_PORT,
    SONAR_SCANNER_OS,
    SONAR_SCANNER_ARCH,
    SONAR_SCANNER_JAVA_EXE_PATH,
)
from pysonar_scanner.exceptions import SQTooOldException
from pysonar_scanner.jre import JREResolvedPath, JREResolver
from pysonar_scanner.scannerengine import ScannerEngine, ScannerEngineProvisioner
from tests.unit import sq_api_utils


class TestMain(unittest.TestCase):

    @patch.object(pathlib.Path, "home", return_value=pathlib.Path("home/user"))
    @patch.object(
        ConfigurationLoader,
        "load",
        return_value={
            SONAR_TOKEN: "myToken",
            SONAR_PROJECT_KEY: "myProjectKey",
            SONAR_SCANNER_OS: "linux",
            SONAR_SCANNER_ARCH: "x64",
        },
    )
    @patch.object(
        ScannerEngineProvisioner, "provision", return_value=JREResolvedPath(pathlib.Path("scanner_engine_path"))
    )
    @patch("pysonar_scanner.__main__.create_jre", return_value=JREResolvedPath(pathlib.Path("jre_path")))
    @patch.object(ScannerEngine, "run", return_value=0)
    def test_minimal_success_run(self, run_mock, create_jre_mock, provision_mock, load_mock, path_home_mock):
        exitcode = scan()
        self.assertEqual(exitcode, 0)

        # Verify that run was called with the expected configuration
        run_mock.assert_called_once()
        config = run_mock.call_args[0][0]  # Extract the configuration arg

        # Check expected configuration with a single assertion
        expected_config = {
            SONAR_TOKEN: "myToken",
            SONAR_PROJECT_KEY: "myProjectKey",
            SONAR_SCANNER_OS: "linux",
            SONAR_SCANNER_ARCH: "x64",
            SONAR_HOST_URL: "https://sonarcloud.io",
            SONAR_SCANNER_API_BASE_URL: "https://api.sonarcloud.io",
            SONAR_SCANNER_SONARCLOUD_URL: "https://sonarcloud.io",
            SONAR_SCANNER_PROXY_PORT: "443",
            SONAR_SCANNER_JAVA_EXE_PATH: "jre_path",
        }

        self.assertEqual(expected_config, config)

    @patch.object(ConfigurationLoader, "load")
    def test_scan_with_exception(self, load_mock):
        load_mock.side_effect = Exception("Test exception")

        exitcode = scan()
        self.assertEqual(1, exitcode)

    def test_version_check_outdated_sonarqube(self):
        sq_cloud_api = sq_api_utils.get_sq_server()
        sq_cloud_api.get_analysis_version = Mock(return_value=SQVersion.from_str("9.9.9"))

        with self.assertRaises(SQTooOldException):
            check_version(sq_cloud_api)

    def test_version_check_recent_sonarqube(self):
        sq_cloud_api = sq_api_utils.get_sq_server()
        sq_cloud_api.get_analysis_version = Mock(return_value=SQVersion.from_str("10.7"))

        check_version(sq_cloud_api)
        sq_cloud_api.get_analysis_version.assert_called_once()

    def test_version_check_sonarqube_cloud(self):
        sq_cloud_api = sq_api_utils.get_sq_cloud()
        sq_cloud_api.get_analysis_version = Mock()

        check_version(sq_cloud_api)
        sq_cloud_api.get_analysis_version.assert_not_called()

    @patch("pysonar_scanner.scannerengine.CmdExecutor")
    @patch.object(JREResolver, "resolve_jre")
    def test_get_jre(self, resolve_jre_mock, cmd_executor_mock):
        resolve_jre_mock.return_value = JREResolvedPath(pathlib.Path("jre/bin/java"))
        api = SonarQubeApi(Mock(), Mock())
        cache = Cache(Mock())
        create_jre(api, cache, {SONAR_SCANNER_OS: "linux", SONAR_SCANNER_ARCH: "x64"})
