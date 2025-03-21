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
import argparse

from pysonar_scanner.configuration import properties


class CliConfigurationLoader:

    @classmethod
    def load(cls) -> dict[str, any]:
        args = cls.__parse_cli_args()

        config = {}
        for prop in properties.PROPERTIES:
            if prop.cli_getter is not None:
                value = prop.cli_getter(args)
                config[prop.name] = value

        return {k: v for k, v in config.items() if v is not None}

    @classmethod
    def __parse_cli_args(cls) -> argparse.Namespace:
        parser = argparse.ArgumentParser(description="Sonar scanner CLI for Python")

        parser.add_argument(
            "-t",
            "--token",
            "--sonar-token",
            "-Dsonar.token",
            type=str,
            help="Token used to authenticate against the SonarQube Server or SonarQube Cloud",
        )
        parser.add_argument(
            "--sonar-project-key",
            "-Dsonar.projectKey",
            type=str,
            help="Key of the project that usually corresponds to the project name in SonarQube",
        )
        parser.add_argument(
            "--sonar-project-name",
            "-Dsonar.projectName",
            type=str,
            help="Name of the project in SonarQube",
        )

        parser.add_argument(
            "-v",
            "--verbose",
            "--sonar-verbose",
            "-Dsonar.verbose",
            action="store_true",
            default=None,
            help="Increase output verbosity",
        )

        parser.add_argument(
            "--sonar-host-url",
            "-Dsonar.host.url",
            type=str,
            help="SonarQube Server base URL. For example, http://localhost:9000 for a local instance of SonarQube Server",
        )
        parser.add_argument(
            "--sonar-region",
            "-Dsonar.region",
            type=str,
            choices=["us"],
            help="The region to contact, only for SonarQube Cloud",
        )
        parser.add_argument(
            "--sonar-user-home", "-Dsonar.userHome", type=str, help="Base sonar directory, ~/.sonar by default"
        )

        parser.add_argument(
            "--sonar-scanner-cloud-url",
            "-Dsonar.scanner.cloudUrl",
            type=str,
            help="SonarQube Cloud base URL, https://sonarcloud.io for example",
        )
        parser.add_argument(
            "--sonar-scanner-api-url",
            "-Dsonar.scanner.apiUrl",
            type=str,
            help="Base URL for all REST-compliant API calls, https://api.sonarcloud.io for example",
        )
        parser.add_argument(
            "--sonar-scanner-os",
            "-Dsonar.scanner.os",
            type=str,
            choices=["windows", "linux", "macos", "alpine"],
            help="OS running the scanner",
        )
        parser.add_argument(
            "--sonar-scanner-arch",
            "-Dsonar.scanner.arch",
            type=str,
            choices=["x64", "aarch64"],
            help="Architecture on which the scanner will be running",
        )

        parser.add_argument(
            "--skip-jre-provisioning",
            "-Dsonar.scanner.skipJreProvisioning",
            action="store_true",
            default=None,
            help="If provided, the provisioning of the JRE will be skipped",
        )
        parser.add_argument(
            "--sonar-scanner-java-exe-path",
            "-Dsonar.scanner.javaExePath",
            type=str,
            help="If defined, the scanner engine will be run with this JRE",
        )
        parser.add_argument(
            "--sonar-scanner-java-opts",
            "-Dsonar.scanner.javaOpts",
            type=str,
            help="Arguments provided to the JVM when running the scanner",
        )

        parser.add_argument(
            "--sonar-scanner-internal-dump-to-file",
            "-Dsonar.scanner.internal.dumpToFile",
            type=str,
            help="Filename where the input to the scanner engine will be dumped. Useful for debugging",
        )
        parser.add_argument(
            "--sonar-scanner-internal-sq-version",
            "-Dsonar.scanner.internal.sqVersion",
            type=str,
            help="Emulate the result of the call to get SQ server version.  Useful for debugging with --sonar-scanner-internal-dump-to-file",
        )

        parser.add_argument(
            "--sonar-scanner-connect-timeout",
            "-Dsonar.scanner.connectTimeout",
            type=int,
            help="Time period to establish connections with the server (in seconds)",
        )
        parser.add_argument(
            "--sonar-scanner-socket-timeout",
            "-Dsonar.scanner.socketTimeout",
            type=int,
            help="Maximum time of inactivity between two data packets when exchanging data with the server (in seconds)",
        )
        parser.add_argument(
            "--sonar-scanner-response-timeout",
            "-Dsonar.scanner.responseTimeout",
            type=int,
            help="Time period required to process an HTTP call: from sending a request to receiving a response (in seconds)",
        )

        parser.add_argument(
            "--sonar-scanner-truststore-path",
            "-Dsonar.scanner.truststorePath",
            type=str,
            help="Path to the keystore containing trusted server certificates, used by the Scanner in addition to OS and the built-in certificates",
        )
        parser.add_argument(
            "--sonar-scanner-truststore-password",
            "-Dsonar.scanner.truststorePassword",
            type=str,
            help="Password to access the truststore",
        )

        parser.add_argument(
            "--sonar-scanner-keystore-path",
            "-Dsonar.scanner.keystorePath",
            type=str,
            help="Path to the keystore containing the client certificates used by the scanner. By default, <sonar.userHome>/ssl/keystore.p12",
        )
        parser.add_argument(
            "--sonar-scanner-keystore-password",
            "-Dsonar.scanner.keystorePassword",
            type=str,
            help="Password to access the keystore",
        )

        parser.add_argument("--sonar-scanner-proxy-host", "-Dsonar.scanner.proxyHost", type=str, help="Proxy host")
        parser.add_argument("--sonar-scanner-proxy-port", "-Dsonar.scanner.proxyPort", type=int, help="Proxy port")
        parser.add_argument("--sonar-scanner-proxy-user", "-Dsonar.scanner.proxyUser", type=str, help="Proxy user")
        parser.add_argument(
            "--sonar-scanner-proxy-password", "-Dsonar.scanner.proxyPassword", type=str, help="Proxy password"
        )

        parser.add_argument(
            "--sonar-project-base-dir",
            "-Dsonar.projectBaseDir",
            type=str,
            help="Directory containing the project to be analyzed. Default is the current directory",
        )

        parser.add_argument(
            "--toml-path",
            type=str,
            help="Path to the pyproject.toml file. If not provided, it will look in the SONAR_PROJECT_BASE_DIR",
        )

        parser.add_argument(
            "--sonar-project-version",
            "-Dsonar.projectVersion",
            type=str,
            help="Version of the project",
        )

        parser.add_argument(
            "--sonar-project-description",
            "-Dsonar.projectDescription",
            type=str,
            help="Description of the project",
        )

        parser.add_argument(
            "--sonar-python-version",
            "-Dsonar.python.version",
            type=str,
            help="Python version used for the project",
        )

        return parser.parse_args()
