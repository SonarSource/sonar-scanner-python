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

# SonarQube/SonarCloud configuration properties
SONAR_HOST_URL = "sonar.host.url"
SONAR_SCANNER_SONARCLOUD_URL = "sonar.scanner.sonarcloudUrl"
SONAR_SCANNER_API_BASE_URL = "sonar.scanner.apiBaseUrl"
SONAR_REGION = "sonar.region"
SONAR_SCANNER_APP = "sonar.scanner.app"
SONAR_SCANNER_APP_VERSION = "sonar.scanner.appVersion"
SONAR_SCANNER_BOOTSTRAP_START_TIME = "sonar.scanner.bootstrapStartTime"
SONAR_SCANNER_WAS_JRE_CACHE_HIT = "sonar.scanner.wasJreCacheHit"
SONAR_SCANNER_WAS_ENGINE_CACHE_HIT = "sonar.scanner.wasEngineCacheHit"
SONAR_VERBOSE = "sonar.verbose"
SONAR_TOKEN = "sonar.token"
SONAR_SCANNER_OS = "sonar.scanner.os"
SONAR_SCANNER_ARCH = "sonar.scanner.arch"
SONAR_SCANNER_SKIP_JRE_PROVISIONING = "sonar.scanner.skipJreProvisioning"
SONAR_USER_HOME = "sonar.userHome"
SONAR_SCANNER_JAVA_EXE_PATH = "sonar.scanner.javaExePath"
SONAR_SCANNER_INTERNAL_DUMP_TO_FILE = "sonar.scanner.internal.dumpToFile"
SONAR_SCANNER_INTERNAL_SQ_VERSION = "sonar.scanner.internal.sqVersion"
SONAR_SCANNER_CONNECT_TIMEOUT = "sonar.scanner.connectTimeout"
SONAR_SCANNER_SOCKET_TIMEOUT = "sonar.scanner.socketTimeout"
SONAR_SCANNER_RESPONSE_TIMEOUT = "sonar.scanner.responseTimeout"
SONAR_SCANNER_TRUSTSTORE_PATH = "sonar.scanner.truststorePath"
SONAR_SCANNER_TRUSTSTORE_PASSWORD = "sonar.scanner.truststorePassword"
SONAR_SCANNER_KEYSTORE_PATH = "sonar.scanner.keystorePath"
SONAR_SCANNER_KEYSTORE_PASSWORD = "sonar.scanner.keystorePassword"
SONAR_SCANNER_PROXY_HOST = "sonar.scanner.proxyHost"
SONAR_SCANNER_PROXY_PORT = "sonar.scanner.proxyPort"
SONAR_SCANNER_PROXY_USER = "sonar.scanner.proxyUser"
SONAR_SCANNER_PROXY_PASSWORD = "sonar.scanner.proxyPassword"
SONAR_PROJECT_BASE_DIR = "sonar.projectBaseDir"
SONAR_SCANNER_JAVA_OPTS = "sonar.scanner.javaOpts"
SONAR_PROJECT_KEY = "sonar.projectKey"


@dataclass
class Property:
    name: str
    """name in the format of `sonar.scanner.appVersion`"""

    default_value: Optional[any]
    """default value for the property; if None, no default value is set"""

    cli_getter: Optional[Callable[[argparse.Namespace], any]] = None
    """function to get the value from the CLI arguments namespace. If None, the property is not settable via CLI"""


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
]
# fmt: on
