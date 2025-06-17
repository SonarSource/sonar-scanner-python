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
from typing import Any

from pysonar_scanner.configuration import properties
from pysonar_scanner.exceptions import UnexpectedCliArgument


class PyScannerHelpFormatter(argparse.HelpFormatter):
    recommended_args = {"help", "token", "sonar_project_key"}

    def _format_actions_usage(self, actions, groups):
        filtered_actions = [action for action in actions if action.dest in PyScannerHelpFormatter.recommended_args]
        return super()._format_actions_usage(filtered_actions, groups)


class CliConfigurationLoader:

    @classmethod
    def load(cls) -> dict[str, Any]:
        args, unknown_args = cls.__parse_cli_args()
        config = {}
        for prop in properties.PROPERTIES:
            if prop.cli_getter is not None:
                value = prop.cli_getter(args)
                config[prop.name] = value

        # Handle unknown args starting with '-D'
        for arg in unknown_args:
            if not arg.startswith("-D"):
                raise UnexpectedCliArgument(f"Unexpected argument: {arg}\nRun with --help for more information.")
            key_value = arg[2:].split("=", 1)
            if len(key_value) == 2:
                key, value = key_value
                config[key] = value
            else:
                # If no value is provided, set the key to "true"
                config[arg[2:]] = "true"

        return {k: v for k, v in config.items() if v is not None}

    @classmethod
    def __parse_cli_args(cls) -> tuple[argparse.Namespace, list[str]]:
        parser = cls.__create_parser()
        return parser.parse_known_args()

    @classmethod
    def __create_parser(cls):
        parser = argparse.ArgumentParser(
            description="Sonar scanner CLI for Python",
            epilog="Analysis properties not listed here will also be accepted, as long as they start with the -D prefix.",
            formatter_class=PyScannerHelpFormatter,
        )

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
            "--project-key",
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
            "--sonar-sources",
            "-Dsonar.sources",
            type=str,
            help="The analysis scope for main source code (non-test code) in the project",
        )
        parser.add_argument(
            "--sonar-tests",
            "-Dsonar.tests",
            type=str,
            help="The analysis scope for test source code in the project",
        )

        parser.add_argument(
            "--sonar-project-base-dir",
            "-Dsonar.projectBaseDir",
            type=str,
            help="Directory containing the project to be analyzed. Default is the current directory",
        )
        parser.add_argument(
            "--sonar-external-issues-report-paths",
            "-Dsonar.externalIssuesReportPaths",
            type=str,
            help="Comma-delimited list of paths to generic issue reports",
        )
        parser.add_argument(
            "--sonar-sarif-report-paths",
            "-Dsonar.sarifReportPaths",
            type=str,
            help="Comma-delimited list of paths to SARIF issue reports",
        )
        parser.add_argument(
            "--sonar-links-ci", "-Dsonar.links.ci", type=str, help="The URL of the continuous integration system used"
        )
        parser.add_argument(
            "--sonar-links-homepage", "-Dsonar.links.homepage", type=str, help="The URL of the build project home page"
        )
        parser.add_argument(
            "--sonar-links-issue", "-Dsonar.links.issue", type=str, help="The URL to the issue tracker being used"
        )

        parser.add_argument(
            "--sonar-source-encoding",
            "-Dsonar.sourceEncoding",
            type=str,
            help="Encoding of the source files. For example, UTF-8, MacRoman, Shift_JIS",
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

        parser.add_argument(
            "--sonar-modules", "-Dsonar.modules", type=str, help="Comma-delimited list of modules to analyze"
        )

        server_connection_group = parser.add_argument_group("SonarQube Connection")
        server_connection_group.add_argument(
            "--sonar-host-url",
            "-Dsonar.host.url",
            type=str,
            help="SonarQube Server base URL. For example, http://localhost:9000 for a local instance of SonarQube Server",
        )
        server_connection_group.add_argument(
            "--sonar-region",
            "-Dsonar.region",
            type=str,
            choices=["us"],
            help="The region to contact, only for SonarQube Cloud",
        )
        server_connection_group.add_argument(
            "--sonar-organization",
            "-Dsonar.organization",
            type=str,
            help="The key of the organization to which the project belongs",
        )
        server_connection_group.add_argument(
            "--sonar-scanner-cloud-url",
            "-Dsonar.scanner.cloudUrl",
            type=str,
            help="SonarQube Cloud base URL, https://sonarcloud.io for example",
        )
        server_connection_group.add_argument(
            "--sonar-scanner-api-url",
            "-Dsonar.scanner.apiUrl",
            type=str,
            help="Base URL for all REST-compliant API calls, https://api.sonarcloud.io for example",
        )
        server_connection_group.add_argument(
            "--sonar-scanner-connect-timeout",
            "-Dsonar.scanner.connectTimeout",
            type=int,
            help="Time period to establish connections with the server (in seconds)",
        )
        server_connection_group.add_argument(
            "--sonar-scanner-socket-timeout",
            "-Dsonar.scanner.socketTimeout",
            type=int,
            help="Maximum time of inactivity between two data packets when exchanging data with the server (in seconds)",
        )
        server_connection_group.add_argument(
            "--sonar-scanner-response-timeout",
            "-Dsonar.scanner.responseTimeout",
            type=int,
            help="Time period required to process an HTTP call: from sending a request to receiving a response (in seconds)",
        )

        scanner_behavior_group = parser.add_argument_group("Scanner Behavior & Advanced Settings")
        scanner_behavior_group.add_argument(
            "-v",
            "--verbose",
            "--sonar-verbose",
            "-Dsonar.verbose",
            action=argparse.BooleanOptionalAction,
            default=None,
            help="Increase output verbosity",
        )
        scanner_behavior_group.add_argument(
            "--sonar-user-home", "-Dsonar.userHome", type=str, help="Base sonar directory, ~/.sonar by default"
        )
        scanner_behavior_group.add_argument(
            "--sonar-scanner-os",
            "-Dsonar.scanner.os",
            type=str,
            choices=["windows", "linux", "macos", "alpine"],
            help="OS running the scanner",
        )
        scanner_behavior_group.add_argument(
            "--sonar-scanner-arch",
            "-Dsonar.scanner.arch",
            type=str,
            choices=["x64", "aarch64"],
            help="Architecture on which the scanner will be running",
        )
        scanner_behavior_group.add_argument(
            "--sonar-scanner-metadata-filepath",
            "-Dsonar.scanner.metadataFilepath",
            type=str,
            help="Sets the location where the scanner writes the report-task.txt file containing among other things the ceTaskId",
        )
        scanner_behavior_group.add_argument(
            "--sonar-scanner-internal-dump-to-file",
            "-Dsonar.scanner.internal.dumpToFile",
            type=str,
            help="Filename where the input to the scanner engine will be dumped. Useful for debugging",
        )
        scanner_behavior_group.add_argument(
            "--sonar-scanner-internal-sq-version",
            "-Dsonar.scanner.internal.sqVersion",
            type=str,
            help="Emulate the result of the call to get SQ server version.  Useful for debugging with --sonar-scanner-internal-dump-to-file",
        )
        scanner_behavior_group.add_argument(
            "--sonar-scm-exclusions-disabled",
            type=bool,
            action=argparse.BooleanOptionalAction,
            help="Defines whether files ignored by the SCM, e.g., files listed in .gitignore, will be excluded from the analysis or not",
        )
        scanner_behavior_group.add_argument(
            "-Dsonar.scm.exclusions.disabled",
            type=bool,
            help="Equivalent to --sonar-scm-exclusions-disabled",
        )
        scanner_behavior_group.add_argument(
            "--sonar-filesize-limit",
            "-Dsonar.filesize.limit",
            type=int,
            help="Sets the limit in MB for files to be discarded from the analysis scope if the size is greater than specified",
        )
        scanner_behavior_group.add_argument(
            "--sonar-cpd-python-minimum-tokens",
            "-Dsonar.cpd.python.minimumTokens",
            type=int,
            help="Minimum number of tokens to be considered as a duplicated block of code",
        )
        scanner_behavior_group.add_argument(
            "--sonar-cpd-python-minimum-lines",
            "-Dsonar.cpd.python.minimumLines",
            type=int,
            help="Minimum number of tokens to be considered as a duplicated block of code",
        )
        scanner_behavior_group.add_argument(
            "--sonar-log-level",
            "-Dsonar.log.level",
            type=str,
            choices=["TRACE", "DEBUG", "INFO", "WARN", "ERROR"],
            help="Log level during the analysis",
        )
        scanner_behavior_group.add_argument(
            "--sonar-qualitygate-wait",
            type=bool,
            action=argparse.BooleanOptionalAction,
            help="Forces the analysis step to poll the server instance and wait for the Quality Gate status",
        )
        scanner_behavior_group.add_argument(
            "-Dsonar.qualitygate.wait",
            type=bool,
            help="Equivalent to --sonar-qualitygate-wait",
        )
        scanner_behavior_group.add_argument(
            "--sonar-qualitygate-timeout",
            "-Dsonar.qualitygate.timeout",
            type=int,
            help="The number of seconds that the scanner should wait for a report to be processed",
        )
        scanner_behavior_group.add_argument(
            "--sonar-build-string",
            "-Dsonar.buildString",
            type=str,
            help="The string passed with this property will be stored with the analysis and available in the results of api/project_analyses/search, thus allowing you to later identify a specific analysis and obtain its key for use with api/new_code_periods/set on the SPECIFIC_ANALYSIS type",
        )
        scanner_behavior_group.add_argument(
            "--sonar-working-directory",
            "-Dsonar.working.directory",
            type=str,
            help="Path to the working directory used by the Sonar scanner during a project analysis to store temporary data",
        )
        scanner_behavior_group.add_argument(
            "--sonar-scm-force-reload-all",
            type=bool,
            action=argparse.BooleanOptionalAction,
            help="Set this property to true to load blame information for all files, which may significantly increase analysis duration",
        )
        scanner_behavior_group.add_argument(
            "-Dsonar.scm.forceReloadAll",
            type=bool,
            help="Equivalent to --sonar-scm-force-reload-all",
        )
        scanner_behavior_group.add_argument(
            "--sonar-python-skip-unchanged",
            type=bool,
            action=argparse.BooleanOptionalAction,
            help="Override the SonarQube configuration of skipping or not the analysis of unchanged Python files",
        )

        jvm_group = parser.add_argument_group("JVM Settings")
        jvm_group.add_argument(
            "--skip-jre-provisioning",
            "-Dsonar.scanner.skipJreProvisioning",
            action="store_true",
            default=None,
            help="If provided, the provisioning of the JRE will be skipped",
        )
        jvm_group.add_argument(
            "--sonar-scanner-java-exe-path",
            "-Dsonar.scanner.javaExePath",
            type=str,
            help="If defined, the scanner engine will be run with this JRE",
        )
        jvm_group.add_argument(
            "--sonar-scanner-java-opts",
            "-Dsonar.scanner.javaOpts",
            type=str,
            help="Arguments provided to the JVM when running the scanner",
        )
        jvm_group.add_argument(
            "--sonar-scanner-java-heap-size",
            "--java-heap-size",
            "-Dsonar.scanner.javaHeapSize",
            type=str,
            help="Arguments specifies the heap size provided to the JVM when running the scanner",
        )

        truststore_group = parser.add_argument_group("Truststore arguments")
        truststore_group.add_argument(
            "--sonar-scanner-truststore-path",
            "-Dsonar.scanner.truststorePath",
            type=str,
            help="Path to the keystore containing trusted server certificates, used by the Scanner in addition to OS and the built-in certificates",
        )
        truststore_group.add_argument(
            "--sonar-scanner-truststore-password",
            "-Dsonar.scanner.truststorePassword",
            type=str,
            help="Password to access the truststore",
        )

        keystore_group = parser.add_argument_group("Keystore arguments")
        keystore_group.add_argument(
            "--sonar-scanner-keystore-path",
            "-Dsonar.scanner.keystorePath",
            type=str,
            help="Path to the keystore containing the client certificates used by the scanner. By default, <sonar.userHome>/ssl/keystore.p12",
        )
        keystore_group.add_argument(
            "--sonar-scanner-keystore-password",
            "-Dsonar.scanner.keystorePassword",
            type=str,
            help="Password to access the keystore",
        )

        proxy_group = parser.add_argument_group("Proxy arguments")
        proxy_group.add_argument("--sonar-scanner-proxy-host", "-Dsonar.scanner.proxyHost", type=str, help="Proxy host")
        proxy_group.add_argument("--sonar-scanner-proxy-port", "-Dsonar.scanner.proxyPort", type=int, help="Proxy port")
        proxy_group.add_argument("--sonar-scanner-proxy-user", "-Dsonar.scanner.proxyUser", type=str, help="Proxy user")
        proxy_group.add_argument(
            "--sonar-scanner-proxy-password", "-Dsonar.scanner.proxyPassword", type=str, help="Proxy password"
        )

        version_control_group = parser.add_argument_group("Version control arguments")
        version_control_group.add_argument(
            "--sonar-links-scm",
            "-Dsonar.links.scm",
            type=str,
            help="The URL of the build project source code repository",
        )
        version_control_group.add_argument(
            "--sonar-branch-name", "-Dsonar.branch.name", type=str, help="Name of the branch being analyzed"
        )
        version_control_group.add_argument(
            "--sonar-pullrequest-key",
            "-Dsonar.pullrequest.key",
            type=str,
            help="Key of the pull request being analyzed",
        )
        version_control_group.add_argument(
            "--sonar-pullrequest-branch",
            "-Dsonar.pullrequest.branch",
            type=str,
            help="Branch of the pull request being analyzed",
        )
        version_control_group.add_argument(
            "--sonar-pullrequest-base",
            "-Dsonar.pullrequest.base",
            type=str,
            help="Base branch of the pull request being analyzed",
        )
        version_control_group.add_argument(
            "--sonar-newcode-reference-branch",
            "-Dsonar.newCode.referenceBranch",
            type=str,
            help="Reference branch for new code definition",
        )
        version_control_group.add_argument(
            "--sonar-scm-revision",
            "-Dsonar.scm.revision",
            type=str,
            help="Overrides the revision, for instance, the Git sha1, displayed in analysis results",
        )

        reports_group = parser.add_argument_group("3rd party reports arguments")
        reports_group.add_argument(
            "--sonar-python-pylint-report-path",
            "--pylint-report-path",
            "-Dsonar.python.pylint.reportPath",
            type=str,
            help="Path to third-parties issues report file for pylint",
        )
        reports_group.add_argument(
            "--sonar-python-coverage-report-paths",
            "--coverage-report-paths",
            "-Dsonar.python.coverage.reportPaths",
            type=str,
            help="Comma-delimited list of paths to coverage reports in the Cobertura XML format.",
        )
        reports_group.add_argument(
            "--sonar-coverage-exclusions",
            "--sonar.coverage.exclusions",
            "-Dsonar.coverage.exclusions",
            type=str,
            help="Defines the source files to be excluded from the code coverage analysis.",
        )
        reports_group.add_argument(
            "-Dsonar.python.skipUnchanged",
            type=bool,
            help="Equivalent to --sonar-python-skip-unchanged",
        )
        reports_group.add_argument(
            "--sonar-python-xunit-report-path",
            "--xunit-report-path",
            "-Dsonar.python.xunit.reportPath",
            type=str,
            help="Path to the report of test execution, relative to project's root",
        )
        reports_group.add_argument(
            "--sonar-python-xunit-skip-details",
            "--xunit-skip-details",
            type=bool,
            action=argparse.BooleanOptionalAction,
            help="When enabled, the test execution statistics is provided only on project level",
        )
        reports_group.add_argument(
            "-Dsonar.python.xunit.skipDetails",
            type=bool,
            help="Equivalent to -Dsonar.python.xunit.skipDetails",
        )
        reports_group.add_argument(
            "--sonar-python-mypy-report-paths",
            "--mypy-report-paths",
            "-Dsonar.python.mypy.reportPaths",
            type=str,
            help="Comma-separated mypy report paths, relative to project's root",
        )
        reports_group.add_argument(
            "--sonar-python-bandit-report-paths",
            "--bandit-report-paths",
            "-Dsonar.python.bandit.reportPaths",
            type=str,
            help="Comma-separated bandit report paths, relative to project's root",
        )
        reports_group.add_argument(
            "--sonar-python-flake8-report-paths",
            "--flake8-report-paths",
            "-Dsonar.python.flake8.reportPaths",
            type=str,
            help="Comma-separated flake8 report paths, relative to project's root",
        )
        reports_group.add_argument(
            "--sonar-python-ruff-report-paths",
            "--ruff-report-paths",
            "-Dsonar.python.ruff.reportPaths",
            type=str,
            help="Comma-separated ruff report paths, relative to project's root",
        )

        return parser
