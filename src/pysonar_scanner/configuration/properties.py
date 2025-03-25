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
import time
import argparse
from dataclasses import dataclass
from typing import Callable, Optional

Key = str

SONAR_HOST_URL: Key = "sonar.host.url"
SONAR_SCANNER_SONARCLOUD_URL: Key = "sonar.scanner.sonarcloudUrl"
SONAR_SCANNER_API_BASE_URL: Key = "sonar.scanner.apiBaseUrl"
SONAR_REGION: Key = "sonar.region"
SONAR_SCANNER_APP: Key = "sonar.scanner.app"
SONAR_SCANNER_APP_VERSION: Key = "sonar.scanner.appVersion"
SONAR_SCANNER_BOOTSTRAP_START_TIME: Key = "sonar.scanner.bootstrapStartTime"
SONAR_SCANNER_WAS_JRE_CACHE_HIT: Key = "sonar.scanner.wasJreCacheHit"
SONAR_SCANNER_WAS_ENGINE_CACHE_HIT: Key = "sonar.scanner.wasEngineCacheHit"
SONAR_VERBOSE: Key = "sonar.verbose"
SONAR_TOKEN: Key = "sonar.token"
SONAR_SCANNER_OS: Key = "sonar.scanner.os"
SONAR_SCANNER_ARCH: Key = "sonar.scanner.arch"
SONAR_SCANNER_SKIP_JRE_PROVISIONING: Key = "sonar.scanner.skipJreProvisioning"
SONAR_USER_HOME: Key = "sonar.userHome"
SONAR_SCANNER_JAVA_EXE_PATH: Key = "sonar.scanner.javaExePath"
SONAR_SCANNER_INTERNAL_DUMP_TO_FILE: Key = "sonar.scanner.internal.dumpToFile"
SONAR_SCANNER_INTERNAL_SQ_VERSION: Key = "sonar.scanner.internal.sqVersion"
SONAR_SCANNER_CONNECT_TIMEOUT: Key = "sonar.scanner.connectTimeout"
SONAR_SCANNER_SOCKET_TIMEOUT: Key = "sonar.scanner.socketTimeout"
SONAR_SCANNER_RESPONSE_TIMEOUT: Key = "sonar.scanner.responseTimeout"
SONAR_SCANNER_TRUSTSTORE_PATH: Key = "sonar.scanner.truststorePath"
SONAR_SCANNER_TRUSTSTORE_PASSWORD: Key = "sonar.scanner.truststorePassword"
SONAR_SCANNER_KEYSTORE_PATH: Key = "sonar.scanner.keystorePath"
SONAR_SCANNER_KEYSTORE_PASSWORD: Key = "sonar.scanner.keystorePassword"
SONAR_SCANNER_PROXY_HOST: Key = "sonar.scanner.proxyHost"
SONAR_SCANNER_PROXY_PORT: Key = "sonar.scanner.proxyPort"
SONAR_SCANNER_PROXY_USER: Key = "sonar.scanner.proxyUser"
SONAR_SCANNER_PROXY_PASSWORD: Key = "sonar.scanner.proxyPassword"
SONAR_PROJECT_BASE_DIR: Key = "sonar.projectBaseDir"
SONAR_SCANNER_JAVA_OPTS: Key = "sonar.scanner.javaOpts"
SONAR_PROJECT_KEY: Key = "sonar.projectKey"
SONAR_PROJECT_NAME: Key = "sonar.projectName"
SONAR_SOURCES: Key = "sonar.sources"
SONAR_EXCLUSIONS: Key = "sonar.exclusions"
SONAR_TESTS: Key = "sonar.tests"
SONAR_PROJECT_VERSION: Key = "sonar.projectVersion"
SONAR_PROJECT_DESCRIPTION: Key = "sonar.projectDescription"
SONAR_PYTHON_VERSION: Key = "sonar.python.version"

# pysonar scanner specific properties
TOML_PATH: Key = "toml-path"


@dataclass
class Property:
    name: Key
    """name in the format of `sonar.scanner.appVersion`"""

    default_value: Optional[any]
    """default value for the property; if None, no default value is set"""

    cli_getter: Optional[Callable[[argparse.Namespace], any]] = None
    """function to get the value from the CLI arguments namespace. If None, the property is not settable via CLI"""

    def python_name(self) -> str:
        """Convert Java-style camel case name to Python-style kebab-case name."""
        result = []
        for i, char in enumerate(self.name):
            if char.isupper() and i > 0:
                result.append("-")
            result.append(char.lower())
        return "".join(result)


# fmt: off
PROPERTIES: list[Property] = [
    Property(
        name=SONAR_SCANNER_APP, 
        default_value="python", 
        cli_getter=None
    ),
    Property(
        name=SONAR_SCANNER_APP_VERSION, 
        default_value="1.0", 
        cli_getter=None
    ),
    Property(
        name=SONAR_SCANNER_BOOTSTRAP_START_TIME,
        default_value=int(time.time() * 1000),
        cli_getter=None
    ),
    Property(
        name=SONAR_SCANNER_WAS_JRE_CACHE_HIT, 
        default_value=None, 
        cli_getter=None
    ),
    Property(
        name=SONAR_SCANNER_WAS_ENGINE_CACHE_HIT, 
        default_value=None, 
        cli_getter=None
    ),
    Property(
        name=SONAR_VERBOSE, 
        default_value=False, 
        cli_getter=lambda args: args.verbose
    ),
    Property(
        name=SONAR_HOST_URL, 
        default_value=None, 
        cli_getter=lambda args: args.sonar_host_url
    ),  
    Property(
        name=SONAR_REGION, 
        default_value=None, 
        cli_getter=lambda args: args.sonar_region
    ),
    Property(
        name=SONAR_SCANNER_SONARCLOUD_URL,
        default_value=None,
        cli_getter=lambda args: args.sonar_scanner_cloud_url
    ),  
    Property(
        name=SONAR_SCANNER_API_BASE_URL, 
        default_value=None,
        cli_getter=lambda args: args.sonar_scanner_api_url
    ),  
    Property(
        name=SONAR_TOKEN, 
        default_value=None, 
        cli_getter=lambda args: args.token
    ),
    Property(
        name=SONAR_SCANNER_OS, 
        default_value=None, 
        cli_getter=lambda args: args.sonar_scanner_os
    ),
    Property(
        name=SONAR_SCANNER_ARCH, 
        default_value=None, 
        cli_getter=lambda args: args.sonar_scanner_arch
    ),
    Property(
        name=SONAR_SCANNER_SKIP_JRE_PROVISIONING,
        default_value=False,
        cli_getter=lambda args: args.skip_jre_provisioning
    ),
    Property(
        name=SONAR_USER_HOME, 
        default_value="~/.sonar", 
        cli_getter=lambda args: args.sonar_user_home
    ),  
    Property(
        name=SONAR_SCANNER_JAVA_EXE_PATH, 
        default_value=None, 
        cli_getter=lambda args: args.sonar_scanner_java_exe_path
    ),
    Property(
        name=SONAR_SCANNER_INTERNAL_DUMP_TO_FILE,
        default_value=None,
        cli_getter=lambda args: args.sonar_scanner_internal_dump_to_file
    ),
    Property(
        name=SONAR_SCANNER_INTERNAL_SQ_VERSION,
        default_value=None,
        cli_getter=lambda args: args.sonar_scanner_internal_sq_version
    ),
    Property(
        name=SONAR_SCANNER_CONNECT_TIMEOUT,
        default_value=5,
        cli_getter=lambda args: args.sonar_scanner_connect_timeout
    ),
    Property(
        name=SONAR_SCANNER_SOCKET_TIMEOUT,
        default_value=60,
        cli_getter=lambda args: args.sonar_scanner_socket_timeout
    ),
    Property(
        name=SONAR_SCANNER_RESPONSE_TIMEOUT,
        default_value=0,
        cli_getter=lambda args: args.sonar_scanner_response_timeout
    ),
    Property(
        name=SONAR_SCANNER_TRUSTSTORE_PATH,
        default_value=None,  
        cli_getter=lambda args: args.sonar_scanner_truststore_path
    ),
    Property(
        name=SONAR_SCANNER_TRUSTSTORE_PASSWORD,
        default_value="changeit",  
        cli_getter=lambda args: args.sonar_scanner_truststore_password
    ),
    Property(
        name=SONAR_SCANNER_KEYSTORE_PATH,
        default_value=None,
        cli_getter=lambda args: args.sonar_scanner_keystore_path
    ),  
    Property(
        name=SONAR_SCANNER_KEYSTORE_PASSWORD,
        default_value="changeit",  
        cli_getter=lambda args: args.sonar_scanner_keystore_password
    ),
    Property(
        name=SONAR_SCANNER_PROXY_HOST, 
        default_value=None, 
        cli_getter=lambda args: args.sonar_scanner_proxy_host
    ),
    Property(
        name=SONAR_SCANNER_PROXY_PORT, 
        default_value=None, 
        cli_getter=lambda args: args.sonar_scanner_proxy_port
    ),  
    Property(
        name=SONAR_SCANNER_PROXY_USER, 
        default_value=None, 
        cli_getter=lambda args: args.sonar_scanner_proxy_user
    ),
    Property(
        name=SONAR_SCANNER_PROXY_PASSWORD,
        default_value=None,
        cli_getter=lambda args: args.sonar_scanner_proxy_password
    ),
    Property(
        name=SONAR_PROJECT_BASE_DIR, 
        default_value=None, 
        cli_getter=lambda args: args.sonar_project_base_dir
    ),  
    Property(
        name=SONAR_SCANNER_JAVA_OPTS, 
        default_value=None, 
        cli_getter=lambda args: args.sonar_scanner_java_opts
    ),
    Property(
        name=SONAR_PROJECT_KEY, 
        default_value=None, 
        cli_getter=lambda args: args.sonar_project_key
    ),
    Property(
            name=SONAR_PROJECT_NAME,
            default_value=None,
            cli_getter=lambda args: args.sonar_project_name
    ),
    Property(
            name=TOML_PATH,
            default_value=None,
            cli_getter=lambda args: args.toml_path
    ),
    Property(
                name=SONAR_PROJECT_VERSION,
                default_value=None,
                cli_getter=lambda args: args.sonar_project_version
    ),
    Property(
                name=SONAR_PROJECT_DESCRIPTION,
                default_value=None,
                cli_getter=lambda args: args.sonar_project_description
    ),
    Property(
                name=SONAR_PYTHON_VERSION,
                default_value=None,
                cli_getter=lambda args: args.sonar_python_version
    ),
]
# fmt: on
