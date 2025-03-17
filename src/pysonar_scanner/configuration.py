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
import json
import argparse
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional, Dict

from pysonar_scanner import utils
from pysonar_scanner.api import BaseUrls
from pysonar_scanner.utils import filter_none_values


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


def get_static_default_properties() -> dict[str, any]:
    return {prop.name: prop.default_value for prop in PROPERTIES if prop.default_value is not None}


class ConfigurationLoader:
    def load(self) -> dict[str, any]:
        return {
            **get_static_default_properties(),
            **filter_none_values(CliConfigurationLoader.load()),
        }


class CliConfigurationLoader:

    @classmethod
    def load(cls) -> dict[str, any]:
        args = cls.__parse_cli_args()

        configuration = {}
        for prop in PROPERTIES:
            if prop.cli_getter is not None:
                value = prop.cli_getter(args)
                configuration[prop.name] = value

        return {k: v for k, v in configuration.items() if v is not None}

    @classmethod
    def __parse_cli_args(cls) -> argparse.Namespace:
        parser = argparse.ArgumentParser(description="Sonar scanner CLI for python")

        parser.add_argument(
            "-t",
            "--token",
            "--sonar-token",
            type=str,
            required=True,
            help="Token used to authenticate against the SonarQube Server or SonarQube cloud",
        )
        parser.add_argument(
            "--sonar-project-key",
            type=str,
            required=True,
            help="Key of the project that usually corresponds to the project name in SonarQube",
        )

        parser.add_argument(
            "-v", "--verbose", "--sonar-verbose", action="store_true", default=None, help="Increase output verbosity"
        )

        parser.add_argument(
            "--sonar-host-url",
            type=str,
            help="SonarQube Server base URL. For example, http://localhost:9000 for a local instance of SonarQube Server",
        )
        parser.add_argument(
            "--sonar-region",
            type=str,
            choices=["us"],
            help="The region to contact, only for SonarQube Cloud",
        )
        parser.add_argument("--sonar-user-home", type=str, help="Base sonar directory, ~/.sonar by default")

        parser.add_argument(
            "--sonar-scanner-cloud-url",
            type=str,
            help="SonarQube Cloud base URL, https://sonarcloud.io for example",
        )
        parser.add_argument(
            "--sonar-scanner-api-url",
            type=str,
            help="Base URL for all REST-compliant API calls, https://api.sonarcloud.io for example",
        )
        parser.add_argument(
            "--sonar-scanner-os",
            type=str,
            choices=["windows", "linux", "macos", "alpine"],
            help="OS running the scanner",
        )
        parser.add_argument(
            "--sonar-scanner-arch",
            type=str,
            choices=["x64", "aarch64"],
            help="Architecture on which the scanner will be running",
        )

        parser.add_argument(
            "--skip-jre-provisioning",
            action="store_true",
            default=None,
            help="If provided, the provisioning of the JRE will be skipped",
        )
        parser.add_argument(
            "--sonar-scanner-java-exe-path", type=str, help="If defined, the scanner engine will be run with this JRE"
        )
        parser.add_argument(
            "--sonar-scanner-java-opts", type=str, help="Arguments provided to the JVM when running the scanner"
        )

        parser.add_argument(
            "--sonar-scanner-internal-dump-to-file",
            type=str,
            help="Filename where the input to the scanner engine will be dumped. Useful for debugging",
        )
        parser.add_argument(
            "--sonar-scanner-internal-sq-version",
            type=str,
            help="Emulate the result of the call to get SQ server version.  Useful for debugging with --sonar-scanner-internal-dump-to-file",
        )

        parser.add_argument(
            "--sonar-scanner-connect-timeout",
            type=int,
            help="Time period to establish connections with the server (in seconds)",
        )
        parser.add_argument(
            "--sonar-scanner-socket-timeout",
            type=int,
            help="Maximum time of inactivity between two data packets when exchanging data with the server (in seconds)",
        )
        parser.add_argument(
            "--sonar-scanner-response-timeout",
            type=int,
            help="Time period required to process an HTTP call: from sending a request to receiving a response (in seconds)",
        )

        parser.add_argument(
            "--sonar-scanner-truststore-path",
            type=str,
            help="Path to the keystore containing trusted server certificates, used by the Scanner in addition to OS and the built-in certificates",
        )
        parser.add_argument("--sonar-scanner-truststore-password", type=str, help="Password to access the truststore")

        parser.add_argument(
            "--sonar-scanner-keystore-path",
            type=str,
            help="Path to the keystore containing the client certificates used by the scanner. By default, <sonar.userHome>/ssl/keystore.p12",
        )
        parser.add_argument("--sonar-scanner-keystore-password", type=str, help="Password to access the keystore")

        parser.add_argument("--sonar-scanner-proxy-host", type=str, help="Proxy host")
        parser.add_argument("--sonar-scanner-proxy-port", type=int, help="Proxy port")
        parser.add_argument("--sonar-scanner-proxy-user", type=str, help="Proxy user")
        parser.add_argument("--sonar-scanner-proxy-password", type=str, help="Proxy password")

        parser.add_argument(
            "--sonar-project-base-dir",
            type=str,
            help="Directory containing the project to be analyzed. Default is the current directory",
        )

        return parser.parse_args()
