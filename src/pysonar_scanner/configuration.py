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
from typing import Optional, Dict


class JRECacheStatus(Enum):
    HIT = 1
    MISS = 2
    DISABLE = 3


@dataclass(frozen=True)
class Internal:
    dump_to_file: Optional[str] = None  # File path to dump the input to the scanner engine
    sq_version: Optional[str] = None


@dataclass(frozen=True)
class Scanner:
    app: str = "python"
    app_version: str = "1.0"
    bootstrap_start_time: int = int(time.time() * 1000)

    os: Optional[str] = None
    arch: Optional[str] = None

    connect_timeout: Optional[int] = None
    socket_timeout: Optional[int] = None
    response_timeout: Optional[int] = None

    truststore_path: Optional[str] = None
    truststore_password: Optional[str] = None
    keystore_path: Optional[str] = None
    keystore_password: Optional[str] = None

    proxy_host: Optional[str] = None
    proxy_port: Optional[int] = None
    proxy_user: Optional[str] = None
    proxy_password: Optional[str] = None

    was_jre_cache_hit: Optional[JRECacheStatus] = None
    was_engine_cache_hit: Optional[bool] = None
    skip_jre_provisioning: bool = False
    java_exe_path: Optional[str] = None
    java_opts: Optional[str] = None

    sonarcloud_url: str = ""
    api_base_url: str = ""

    internal: Internal = Internal()


@dataclass(frozen=True)
class Sonar:
    scanner: Scanner = Scanner()

    verbose: bool = False

    project_base_dir: Optional[str] = None
    user_home: Optional[str] = None

    token: str = ""
    project_key: str = ""
    host_url: str = ""
    region: str = ""


@dataclass(frozen=True)
class Configuration:
    sonar: Sonar = Sonar()

    def __to_dict(self) -> Dict:
        scanner = self.sonar.scanner
        sonar = self.sonar

        properties = [
            {"key": "sonar.scanner.app", "value": scanner.app},
            {"key": "sonar.scanner.appVersion", "value": scanner.app_version},
            {"key": "sonar.token", "value": sonar.token},
            {"key": "sonar.projectKey", "value": sonar.project_key}
        ]

        optional_properties = [
            ("sonar.region", sonar.region),
            ("sonar.host.url", sonar.host_url),
            ("sonar.projectBaseDir", sonar.project_base_dir),
            ("sonar.verbose", sonar.verbose),
            ("sonar.userHome", sonar.user_home),
            ("sonar.scanner.apiBaseUrl", scanner.api_base_url),
            ("sonar.scanner.bootstrapStartTime", scanner.bootstrap_start_time),
            ("sonar.scanner.os", scanner.os),
            ("sonar.scanner.arch", scanner.arch),
            ("sonar.scanner.connectTimeout", scanner.connect_timeout),
            ("sonar.scanner.socketTimeout", scanner.socket_timeout),
            ("sonar.scanner.responseTimeout", scanner.response_timeout),
            ("sonar.scanner.truststorePath", scanner.truststore_path),
            ("sonar.scanner.truststorePassword", scanner.truststore_password),
            ("sonar.scanner.keystorePath", scanner.keystore_path),
            ("sonar.scanner.keystorePassword", scanner.keystore_password),
            ("sonar.scanner.proxyHost", scanner.proxy_host),
            ("sonar.scanner.proxyPort", scanner.proxy_port),
            ("sonar.scanner.proxyUser", scanner.proxy_user),
            ("sonar.scanner.proxyPassword", scanner.proxy_password),
            ("sonar.scanner.wasJreCacheHit", scanner.was_jre_cache_hit.name if scanner.was_jre_cache_hit else None),
            ("sonar.scanner.wasEngineCacheHit", scanner.was_engine_cache_hit),
        ]

        for key, value in optional_properties:
            if value is not None and value != "":
                properties.append({"key": key, "value": value})

        return {"scannerProperties": properties}

    def to_json(self) -> str:
        return json.dumps(self.__to_dict(), indent=2)


class ConfigurationLoader:

    @classmethod
    def initialize_configuration(cls) -> Configuration:
        args = cls.__parse_cli_args()

        internal = Internal(args.sonar_scanner_internal_dump_to_file, args.sonar_scanner_internal_sq_version)

        scanner = Scanner(
            os=args.sonar_scanner_os,
            arch=args.sonar_scanner_arch,
            connect_timeout=args.sonar_scanner_connect_timeout,
            socket_timeout=args.sonar_scanner_socket_timeout,
            response_timeout=args.sonar_scanner_response_timeout,
            truststore_path=args.sonar_scanner_truststore_path,
            truststore_password=args.sonar_scanner_truststore_password,
            keystore_path=args.sonar_scanner_keystore_path,
            keystore_password=args.sonar_scanner_keystore_password,
            proxy_host=args.sonar_scanner_proxy_host,
            proxy_port=args.sonar_scanner_proxy_port,
            proxy_user=args.sonar_scanner_proxy_user,
            proxy_password=args.sonar_scanner_proxy_password,
            skip_jre_provisioning=args.skip_jre_provisioning,
            java_exe_path=args.sonar_scanner_java_exe_path,
            java_opts=args.sonar_scanner_java_opts,
            sonarcloud_url=args.sonar_scanner_cloud_url,
            api_base_url=args.sonar_scanner_api_url,
            internal=internal,
        )

        sonar = Sonar(
            scanner=scanner,
            verbose=args.verbose,
            project_base_dir=args.sonar_project_base_dir,
            user_home=args.sonar_user_home,
            token=args.token,
            project_key=args.sonar_project_key,
            host_url=args.sonar_host_url,
            region=args.sonar_region,
        )

        return Configuration(sonar)

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
            "-v", "--verbose", "--sonar-verbose", action="store_true", default=False, help="Increase output verbosity"
        )

        parser.add_argument(
            "--sonar-host-url",
            type=str,
            default="",
            help="SonarQube Server base URL. For example, http://localhost:9000 for a local instance of SonarQube Server",
        )
        parser.add_argument(
            "--sonar-region",
            type=str,
            default="",
            choices=["us"],
            help="The region to contact, only for SonarQube Cloud",
        )
        parser.add_argument("--sonar-user-home", type=str, help="Base sonar directory, ~/.sonar by default")

        parser.add_argument(
            "--sonar-scanner-cloud-url",
            type=str,
            default="",
            help="SonarQube Cloud base URL, https://sonarcloud.io for example",
        )
        parser.add_argument(
            "--sonar-scanner-api-url",
            type=str,
            default="",
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
