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

import pyfakefs.fake_filesystem_unittest as pyfakefs

from pysonar_scanner.configuration import configuration_loader
from pysonar_scanner.configuration.properties import (
    SONAR_PROJECT_KEY,
    SONAR_PROJECT_NAME,
    SONAR_SCANNER_APP,
    SONAR_SCANNER_APP_VERSION,
    SONAR_SCANNER_BOOTSTRAP_START_TIME,
    SONAR_SCANNER_CONNECT_TIMEOUT,
    SONAR_SCANNER_KEYSTORE_PASSWORD,
    SONAR_SCANNER_RESPONSE_TIMEOUT,
    SONAR_SCANNER_SKIP_JRE_PROVISIONING,
    SONAR_SCANNER_SOCKET_TIMEOUT,
    SONAR_SCANNER_TRUSTSTORE_PASSWORD,
    SONAR_EXCLUSIONS,
    SONAR_SOURCES,
    SONAR_TESTS,
    SONAR_TOKEN,
    SONAR_USER_HOME,
    SONAR_VERBOSE,
    TOML_PATH,
)
from pysonar_scanner.configuration.configuration_loader import ConfigurationLoader, SONAR_PROJECT_BASE_DIR
from pysonar_scanner.exceptions import MissingKeyException


class TestConfigurationLoader(pyfakefs.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.setUpPyfakefs()

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

    @patch("pysonar_scanner.configuration.configuration_loader.get_static_default_properties", return_value={})
    @patch("sys.argv", ["myscript.py"])
    def test_no_defaults_in_configuration_loaders(self, get_static_default_properties_mock):
        config = ConfigurationLoader.load()
        self.assertDictEqual(config, {})

    def test_get_token(self):
        with self.subTest("Token is present"):
            self.assertEqual(configuration_loader.get_token({SONAR_TOKEN: "myToken"}), "myToken")

        with self.subTest("Token is absent"), self.assertRaises(MissingKeyException):
            configuration_loader.get_token({})

    @patch("sys.argv", ["myscript.py", "--token", "myToken", "--sonar-project-key", "myProjectKey"])
    def test_load_sonar_project_properties(self):

        self.fs.create_file(
            "sonar-project.properties",
            contents=(
                """
                sonar.projectKey=overwritten-project-key
                sonar.projectName=My Project\n
                sonar.sources=src # my sources\n
                sonar.exclusions=**/generated/**/*,**/deprecated/**/*,**/testdata/**/*\n
                """
            ),
        )
        configuration = ConfigurationLoader.load()
        expected_configuration = {
            SONAR_TOKEN: "myToken",
            SONAR_PROJECT_KEY: "myProjectKey",
            SONAR_PROJECT_NAME: "My Project",
            SONAR_SOURCES: "src # my sources",
            SONAR_EXCLUSIONS: "**/generated/**/*,**/deprecated/**/*,**/testdata/**/*",
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

    @patch(
        "sys.argv",
        [
            "myscript.py",
            "--token",
            "myToken",
            "--sonar-project-key",
            "myProjectKey",
            "--sonar-project-base-dir",
            "custom/path",
        ],
    )
    def test_load_sonar_project_properties_from_custom_path(self):
        self.fs.create_dir("custom/path")
        self.fs.create_file(
            "custom/path/sonar-project.properties",
            contents=(
                """
                sonar.projectKey=custom-path-project-key
                sonar.projectName=Custom Path Project
                sonar.sources=src/main
                sonar.tests=src/test
                """
            ),
        )
        configuration = ConfigurationLoader.load()
        expected_configuration = {
            SONAR_TOKEN: "myToken",
            SONAR_PROJECT_KEY: "myProjectKey",
            SONAR_PROJECT_NAME: "Custom Path Project",
            SONAR_SOURCES: "src/main",
            SONAR_PROJECT_BASE_DIR: "custom/path",
            SONAR_TESTS: "src/test",
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

    @patch(
        "sys.argv",
        [
            "myscript.py",
            "--token",
            "myToken",
            "--sonar-project-key",
            "myProjectKey",
            "--sonar-project-base-dir",
            "custom/path",
        ],
    )
    def test_load_pyproject_toml_from_base_dir(self):
        self.fs.create_dir("custom/path")
        self.fs.create_file(
            "custom/path/pyproject.toml",
            contents=(
                """
                [tool.sonar]
                 projectKey = "custom-path-project-key"
                 project-name = "Custom Path Project"
                 sources = "src/main"
                 tests= "src/test"
                """
            ),
        )
        configuration = ConfigurationLoader.load()
        expected_configuration = {
            SONAR_TOKEN: "myToken",
            SONAR_PROJECT_KEY: "myProjectKey",
            SONAR_PROJECT_NAME: "Custom Path Project",
            SONAR_SOURCES: "src/main",
            SONAR_PROJECT_BASE_DIR: "custom/path",
            SONAR_TESTS: "src/test",
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

    @patch(
        "sys.argv",
        [
            "myscript.py",
            "--token",
            "myToken",
            "--sonar-project-key",
            "myProjectKey",
            "--toml-path",
            "custom/path",
        ],
    )
    def test_load_pyproject_toml_from_toml_path(self):
        self.fs.create_dir("custom/path")
        self.fs.create_file(
            "custom/path/pyproject.toml",
            contents=(
                """
                [tool.sonar]
                projectKey = "custom-path-project-key"
                project-name = "Custom Path Project"
                sources = "src/main"
                tests= "src/test"
                """
            ),
        )
        configuration = ConfigurationLoader.load()
        expected_configuration = {
            SONAR_TOKEN: "myToken",
            SONAR_PROJECT_KEY: "myProjectKey",
            SONAR_PROJECT_NAME: "Custom Path Project",
            SONAR_SOURCES: "src/main",
            SONAR_TESTS: "src/test",
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
            TOML_PATH: "custom/path",
        }
        self.assertDictEqual(configuration, expected_configuration)

    @patch(
        "sys.argv",
        [
            "myscript.py",
            "--token",
            "myToken",
            "--sonar-project-key",
            "ProjectKeyFromCLI",
        ],
    )
    def test_properties_and_toml_priority(self):
        """Test that sonar-project.properties has priority over pyproject.toml when both exist"""
        # Create both configuration files
        self.fs.create_file(
            "sonar-project.properties",
            contents=(
                """
                sonar.projectKey=ProjectKeyFromProperties
                sonar.projectName=Properties Project
                sonar.sources=src/properties
                sonar.tests=test/properties
                sonar.exclusions=properties-exclusions/**/*
                """
            ),
        )
        self.fs.create_file(
            "pyproject.toml",
            contents=(
                """
                [tool.sonar]
                projectKey = "toml-project-key"
                project-name = "TOML Project"
                sources = "src/toml"
                exclusions = "toml-exclusions/**/*"
                """
            ),
        )

        configuration = ConfigurationLoader.load()

        # TOML values have priority over sonar-project.properties
        self.assertEqual(configuration[SONAR_PROJECT_NAME], "TOML Project")
        self.assertEqual(configuration[SONAR_SOURCES], "src/toml")
        self.assertEqual(configuration[SONAR_TESTS], "test/properties")
        self.assertEqual(configuration[SONAR_EXCLUSIONS], "toml-exclusions/**/*")

        # CLI args still have highest priority
        self.assertEqual(configuration[SONAR_PROJECT_KEY], "ProjectKeyFromCLI")
