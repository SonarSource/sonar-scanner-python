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
        name="sonar.scanner.app", 
        default_value="python", 
        cli_getter=None
    ),
    Property(
        name="sonar.scanner.appVersion", 
        default_value="1.0", 
        cli_getter=None
    ),
    Property(
        name="sonar.scanner.bootstrapStartTime",
        default_value=int(time.time() * 1000),
        cli_getter=None
    ),
    Property(
        name="sonar.scanner.wasJreCacheHit", 
        default_value=None, 
        cli_getter=None
    ),
    Property(
        name="sonar.scanner.wasEngineCacheHit", 
        default_value=None, 
        cli_getter=None
    ),
    Property(
        name="sonar.verbose", 
        default_value=False, 
        cli_getter=lambda args: args.verbose
    ),
    Property(
        name="sonar.host.url", 
        default_value=None, 
        cli_getter=lambda args: args.sonar_host_url
    ),  
    Property(
        name="sonar.region", 
        default_value=None, 
        cli_getter=lambda args: args.sonar_region
    ),
    Property(
        name="sonar.scanner.sonarcloudUrl",
        default_value=None,
        cli_getter=lambda args: args.sonar_scanner_cloud_url
    ),  
    Property(
        name="sonar.scanner.apiBaseUrl", 
        default_value=None, 
        cli_getter=lambda args: args.sonar_scanner_api_url
    ),  
    Property(
        name="sonar.token", 
        default_value=None, 
        cli_getter=lambda args: args.token
    ),
    Property(
        name="sonar.scanner.os", 
        default_value=None, 
        cli_getter=lambda args: args.sonar_scanner_os
    ),
    Property(
        name="sonar.scanner.arch", 
        default_value=None, 
        cli_getter=lambda args: args.sonar_scanner_arch
    ),
    Property(
        name="sonar.scanner.skipJreProvisioning",
        default_value=False,
        cli_getter=lambda args: args.skip_jre_provisioning
    ),
    Property(
        name="sonar.userHome", 
        default_value="~/.sonar", 
        cli_getter=lambda args: args.sonar_user_home
    ),  
    Property(
        name="sonar.scanner.javaExePath", 
        default_value=None, 
        cli_getter=lambda args: args.sonar_scanner_java_exe_path
    ),
    Property(
        name="sonar.scanner.internal.dumpToFile",
        default_value=None,
        cli_getter=lambda args: args.sonar_scanner_internal_dump_to_file
    ),
    Property(
        name="sonar.scanner.internal.sqVersion",
        default_value=None,
        cli_getter=lambda args: args.sonar_scanner_internal_sq_version
    ),
    Property(
        name="sonar.scanner.connectTimeout",
        default_value=5,
        cli_getter=lambda args: args.sonar_scanner_connect_timeout
    ),
    Property(
        name="sonar.scanner.socketTimeout",
        default_value=60,
        cli_getter=lambda args: args.sonar_scanner_socket_timeout
    ),
    Property(
        name="sonar.scanner.responseTimeout",
        default_value=0,
        cli_getter=lambda args: args.sonar_scanner_response_timeout
    ),
    Property(
        name="sonar.scanner.truststorePath",
        default_value=None,  
        cli_getter=lambda args: args.sonar_scanner_truststore_path
    ),
    Property(
        name="sonar.scanner.truststorePassword",
        default_value="changeit",  
        cli_getter=lambda args: args.sonar_scanner_truststore_password
    ),
    Property(
        name="sonar.scanner.keystorePath",
        default_value=None,
        cli_getter=lambda args: args.sonar_scanner_keystore_path
    ),  
    Property(
        name="sonar.scanner.keystorePassword",
        default_value="changeit",  
        cli_getter=lambda args: args.sonar_scanner_keystore_password
    ),
    Property(
        name="sonar.scanner.proxyHost", 
        default_value=None, 
        cli_getter=lambda args: args.sonar_scanner_proxy_host
    ),
    Property(
        name="sonar.scanner.proxyPort", 
        default_value=None, 
        cli_getter=lambda args: args.sonar_scanner_proxy_port
    ),  
    Property(
        name="sonar.scanner.proxyUser", 
        default_value=None, 
        cli_getter=lambda args: args.sonar_scanner_proxy_user
    ),
    Property(
        name="sonar.scanner.proxyPassword",
        default_value=None,
        cli_getter=lambda args: args.sonar_scanner_proxy_password
    ),
    Property(
        name="sonar.projectBaseDir", 
        default_value=None, 
        cli_getter=lambda args: args.sonar_project_base_dir
    ),  
    Property(
        name="sonar.scanner.javaOpts", 
        default_value=None, 
        cli_getter=lambda args: args.sonar_scanner_java_opts
    ),
    Property(
        name="sonar.projectKey", 
        default_value=None, 
        cli_getter=lambda args: args.sonar_project_key
    ),
]
# fmt: on
