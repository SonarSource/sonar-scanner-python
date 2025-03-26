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
import os
from unittest.mock import patch

import pyfakefs.fake_filesystem_unittest as pyfakefs

from pysonar_scanner.configuration import configuration_loader
from pysonar_scanner.configuration.properties import (
    SONAR_PROJECT_KEY,
    SONAR_PROJECT_NAME,
    SONAR_PROJECT_BASE_DIR,
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
    SONAR_PROJECT_DESCRIPTION,
    SONAR_PYTHON_VERSION,
    SONAR_HOST_URL,
    SONAR_SCANNER_JAVA_OPTS,
    SONAR_SCANNER_ARCH,
    SONAR_SCANNER_OS,
)
from pysonar_scanner.configuration.configuration_loader import ConfigurationLoader
from pysonar_scanner.exceptions import MissingKeyException
from pysonar_scanner.utils import Arch, Os


# Mock utils.get_os and utils.get_arch at the module level
@patch("pysonar_scanner.utils.get_arch", return_value=Arch.X64)
@patch("pysonar_scanner.utils.get_os", return_value=Os.LINUX)
class TestConfigurationLoader(pyfakefs.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.setUpPyfakefs()
        self.env_patcher = patch.dict("os.environ", {}, clear=True)
        self.env_patcher.start()

    @patch("sys.argv", ["myscript.py", "--token", "myToken", "--sonar-project-key", "myProjectKey"])
    def test_defaults(self, mock_get_os, mock_get_arch):
        custom_dir = "/my_analysis_directory"
        self.fs.create_dir(custom_dir)
        os.chdir(custom_dir)
        configuration = ConfigurationLoader.load()
        expected_configuration = {
            SONAR_TOKEN: "myToken",
            SONAR_PROJECT_KEY: "myProjectKey",
            SONAR_SCANNER_APP: "python",
            SONAR_SCANNER_APP_VERSION: "1.0",
            SONAR_SCANNER_BOOTSTRAP_START_TIME: configuration[SONAR_SCANNER_BOOTSTRAP_START_TIME],
            SONAR_VERBOSE: False,
            SONAR_SCANNER_SKIP_JRE_PROVISIONING: False,
            SONAR_PROJECT_BASE_DIR: "/my_analysis_directory",
            SONAR_SCANNER_CONNECT_TIMEOUT: 5,
            SONAR_SCANNER_SOCKET_TIMEOUT: 60,
            SONAR_SCANNER_RESPONSE_TIMEOUT: 0,
            SONAR_SCANNER_KEYSTORE_PASSWORD: "changeit",
            SONAR_SCANNER_TRUSTSTORE_PASSWORD: "changeit",
            SONAR_SCANNER_OS: Os.LINUX.value,
            SONAR_SCANNER_ARCH: Arch.X64.value,
        }
        self.assertDictEqual(configuration, expected_configuration)

    @patch("pysonar_scanner.configuration.configuration_loader.get_static_default_properties", return_value={})
    @patch("pysonar_scanner.configuration.dynamic_defaults_loader.load", return_value={})
    @patch("sys.argv", ["myscript.py"])
    def test_no_defaults_in_configuration_loaders(
        self, get_static_default_properties_mock, mock_load, mock_get_os, mock_get_arch
    ):
        config = ConfigurationLoader.load()
        self.assertDictEqual(config, {})

    @patch("pysonar_scanner.configuration.configuration_loader.get_static_default_properties", return_value={})
    @patch("sys.argv", ["myscript.py"])
    def test_dynamic_defaults_are_loaded(self, get_static_default_properties_mock, mock_get_os, mock_get_arch):
        config = ConfigurationLoader.load()
        self.assertDictEqual(
            config,
            {
                SONAR_PROJECT_BASE_DIR: os.getcwd(),
                SONAR_SCANNER_OS: Os.LINUX.value,
                SONAR_SCANNER_ARCH: Arch.X64.value,
            },
        )

    def test_get_token(self, mock_get_os, mock_get_arch):
        with self.subTest("Token is present"):
            self.assertEqual(configuration_loader.get_token({SONAR_TOKEN: "myToken"}), "myToken")

        with self.subTest("Token is absent"), self.assertRaises(MissingKeyException):
            configuration_loader.get_token({})

    @patch("sys.argv", ["myscript.py", "--token", "myToken", "--sonar-project-key", "myProjectKey"])
    def test_load_sonar_project_properties(self, mock_get_os, mock_get_arch):

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
            SONAR_PROJECT_BASE_DIR: os.getcwd(),
            SONAR_SCANNER_CONNECT_TIMEOUT: 5,
            SONAR_SCANNER_SOCKET_TIMEOUT: 60,
            SONAR_SCANNER_RESPONSE_TIMEOUT: 0,
            SONAR_SCANNER_KEYSTORE_PASSWORD: "changeit",
            SONAR_SCANNER_TRUSTSTORE_PASSWORD: "changeit",
            SONAR_SCANNER_OS: Os.LINUX.value,
            SONAR_SCANNER_ARCH: Arch.X64.value,
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
    def test_load_sonar_project_properties_from_custom_path(self, mock_get_os, mock_get_arch):
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
            SONAR_SCANNER_CONNECT_TIMEOUT: 5,
            SONAR_SCANNER_SOCKET_TIMEOUT: 60,
            SONAR_SCANNER_RESPONSE_TIMEOUT: 0,
            SONAR_SCANNER_KEYSTORE_PASSWORD: "changeit",
            SONAR_SCANNER_TRUSTSTORE_PASSWORD: "changeit",
            SONAR_SCANNER_OS: Os.LINUX.value,
            SONAR_SCANNER_ARCH: Arch.X64.value,
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
    def test_load_pyproject_toml_from_base_dir(self, mock_get_os, mock_get_arch):
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
            SONAR_SCANNER_CONNECT_TIMEOUT: 5,
            SONAR_SCANNER_SOCKET_TIMEOUT: 60,
            SONAR_SCANNER_RESPONSE_TIMEOUT: 0,
            SONAR_SCANNER_KEYSTORE_PASSWORD: "changeit",
            SONAR_SCANNER_TRUSTSTORE_PASSWORD: "changeit",
            SONAR_SCANNER_OS: Os.LINUX.value,
            SONAR_SCANNER_ARCH: Arch.X64.value,
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
    def test_load_pyproject_toml_from_toml_path(self, mock_get_os, mock_get_arch):
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
            SONAR_PROJECT_BASE_DIR: os.getcwd(),
            SONAR_SCANNER_CONNECT_TIMEOUT: 5,
            SONAR_SCANNER_SOCKET_TIMEOUT: 60,
            SONAR_SCANNER_RESPONSE_TIMEOUT: 0,
            SONAR_SCANNER_KEYSTORE_PASSWORD: "changeit",
            SONAR_SCANNER_TRUSTSTORE_PASSWORD: "changeit",
            SONAR_SCANNER_OS: Os.LINUX.value,
            SONAR_SCANNER_ARCH: Arch.X64.value,
            TOML_PATH: "custom/path",
        }
        self.assertDictEqual(configuration, expected_configuration)

    @patch("sys.argv", ["myscript.py"])
    @patch.dict("os.environ", {"SONAR_TOKEN": "TokenFromEnv", "SONAR_PROJECT_KEY": "KeyFromEnv"}, clear=True)
    def test_load_from_env_variables_only(self, mock_get_os, mock_get_arch):
        """Test that configuration can be loaded exclusively from environment variables"""
        configuration = ConfigurationLoader.load()

        # Check that environment variables are loaded correctly
        self.assertEqual(configuration[SONAR_TOKEN], "TokenFromEnv")
        self.assertEqual(configuration[SONAR_PROJECT_KEY], "KeyFromEnv")

        # Default values should still be populated
        self.assertEqual(configuration[SONAR_SCANNER_APP], "python")

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
    @patch.dict(
        "os.environ",
        {
            "SONAR_TOKEN": "TokenFromEnv",  # Should be overridden by CLI
            "SONAR_HOST_URL": "https://sonar.env.example.com",  # Not set elsewhere, should be used
            "SONAR_USER_HOME": "/env/sonar/home",  # Should be used (overriding sonar-project.properties)
            "SONAR_SCANNER_JAVA_OPTS": "-Xmx2048m",  # Unique to env vars
            "SONAR_SCANNER_JSON_PARAMS": '{"sonar.exclusions": "json-exclusions/**/*", "SONAR_HOST_URL": "https://sonar.env.example.com"}',  # JSON params
        },
        clear=True,
    )
    def test_properties_priority(self, mock_get_os, mock_get_arch):
        """Test the priority order of different configuration sources:
        1. CLI args (highest)
        2. Environment variables
        3. Generic environment variable
        4. pyproject.toml [tool.sonar] section
        5. sonar-project.properties
        6. Generic properties from pyproject.toml [project] section
        7. Default values (lowest)
        """
        # Create both configuration files
        self.fs.create_file(
            "sonar-project.properties",
            contents=(
                """
                sonar.projectKey=ProjectKeyFromProperties
                sonar.projectName=Properties Project
                sonar.projectDescription=Properties Project Description
                sonar.sources=src/properties
                sonar.tests=test/properties
                sonar.exclusions=properties-exclusions/**/*
                sonar.userHome=/properties/sonar/home
                """
            ),
        )
        self.fs.create_file(
            "pyproject.toml",
            contents=(
                """
                [project]
                name = "My Overridden Project Name"
                description = "My Project Description"
                requires-python = ["3.6", "3.7", "3.8"]
                [tool.sonar]
                projectKey = "toml-project-key"
                project-name = "TOML Project"
                sources = "src/toml"
                exclusions = "toml-exclusions/**/*"
                userHome = "/toml/sonar/home"
                """
            ),
        )

        configuration = ConfigurationLoader.load()

        # Test Default values (lowest priority)
        self.assertNotEqual(configuration[SONAR_SCANNER_CONNECT_TIMEOUT], "5")  # Default value would be 5

        # Generic pyproject.toml properties from [project] section
        self.assertEqual(configuration[SONAR_PYTHON_VERSION], "3.6,3.7,3.8")

        # sonar-project.properties values
        self.assertEqual(configuration[SONAR_TESTS], "test/properties")
        self.assertEqual(
            configuration[SONAR_PROJECT_DESCRIPTION], "Properties Project Description"
        )  # Overrides [project] toml

        # pyproject.toml [tool.sonar] section overrides sonar-project.properties
        self.assertEqual(configuration[SONAR_SOURCES], "src/toml")
        self.assertEqual(configuration[SONAR_PROJECT_NAME], "TOML Project")  # Overrides sonar-project.properties

        # JSON params from environment variable should override toml but be overridden by regular env vars
        self.assertEqual(configuration[SONAR_EXCLUSIONS], "json-exclusions/**/*")  # JSON overrides toml

        # Environment variables override pyproject.toml [tool.sonar] and JSON params
        self.assertEqual(configuration[SONAR_HOST_URL], "https://sonar.env.example.com")
        self.assertEqual(configuration[SONAR_SCANNER_JAVA_OPTS], "-Xmx2048m")
        self.assertEqual(configuration[SONAR_USER_HOME], "/env/sonar/home")  # Env var overrides [sonar] toml

        # CLI args have highest priority
        self.assertEqual(configuration[SONAR_PROJECT_KEY], "ProjectKeyFromCLI")
        self.assertEqual(configuration[SONAR_TOKEN], "myToken")  # CLI overrides env var


# If you have test functions outside of classes, use patch as a decorator for each function
@patch("pysonar_scanner.utils.get_arch", return_value=Arch.X64.value)
@patch("pysonar_scanner.utils.get_os", return_value=Os.LINUX.value)
def test_standalone_function(mock_get_os, mock_get_arch):
    # ...existing test code...
    pass
