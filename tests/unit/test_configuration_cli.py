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
import unittest

from unittest.mock import patch
from io import StringIO

from pysonar_scanner.configuration.configuration_loader import CliConfigurationLoader
from pysonar_scanner.configuration.properties import (
    SONAR_HOST_URL,
    SONAR_ORGANIZATION,
    SONAR_PYTHON_BANDIT_REPORT_PATHS,
    SONAR_PYTHON_FLAKE8_REPORT_PATHS,
    SONAR_PYTHON_MYPY_REPORT_PATHS,
    SONAR_PYTHON_RUFF_REPORT_PATHS,
    SONAR_REGION,
    SONAR_SCANNER_API_BASE_URL,
    SONAR_SCANNER_ARCH,
    SONAR_SCANNER_CONNECT_TIMEOUT,
    SONAR_SCANNER_INTERNAL_DUMP_TO_FILE,
    SONAR_SCANNER_INTERNAL_SQ_VERSION,
    SONAR_SCANNER_JAVA_EXE_PATH,
    SONAR_SCANNER_JAVA_OPTS,
    SONAR_SCANNER_JAVA_HEAP_SIZE,
    SONAR_SCANNER_KEYSTORE_PASSWORD,
    SONAR_SCANNER_KEYSTORE_PATH,
    SONAR_SCANNER_OS,
    SONAR_SCANNER_PROXY_HOST,
    SONAR_SCANNER_PROXY_PASSWORD,
    SONAR_SCANNER_PROXY_PORT,
    SONAR_SCANNER_PROXY_USER,
    SONAR_SCANNER_RESPONSE_TIMEOUT,
    SONAR_SCANNER_SKIP_JRE_PROVISIONING,
    SONAR_SCANNER_SOCKET_TIMEOUT,
    SONAR_SCANNER_SONARCLOUD_URL,
    SONAR_SCANNER_TRUSTSTORE_PASSWORD,
    SONAR_SCANNER_TRUSTSTORE_PATH,
    SONAR_PROJECT_BASE_DIR,
    SONAR_PROJECT_KEY,
    SONAR_TOKEN,
    SONAR_USER_HOME,
    SONAR_VERBOSE,
    SONAR_SOURCES,
    SONAR_TESTS,
    SONAR_PROJECT_NAME,
    SONAR_PROJECT_VERSION,
    SONAR_PROJECT_DESCRIPTION,
    SONAR_FILESIZE_LIMIT,
    SONAR_CPD_PYTHON_MINIMUM_TOKENS,
    SONAR_CPD_PYTHON_MINIMUM_LINES,
    SONAR_SCM_EXCLUSIONS_DISABLED,
    SONAR_LOG_LEVEL,
    SONAR_SCANNER_METADATA_FILEPATH,
    SONAR_QUALITYGATE_WAIT,
    SONAR_QUALITYGATE_TIMEOUT,
    SONAR_EXTERNAL_ISSUES_REPORT_PATHS,
    SONAR_SARIF_REPORT_PATHS,
    SONAR_LINKS_CI,
    SONAR_LINKS_HOMEPAGE,
    SONAR_LINKS_ISSUE,
    SONAR_LINKS_SCM,
    SONAR_BRANCH_NAME,
    SONAR_PULLREQUEST_KEY,
    SONAR_PULLREQUEST_BRANCH,
    SONAR_PULLREQUEST_BASE,
    SONAR_NEWCODE_REFERENCE_BRANCH,
    SONAR_SCM_REVISION,
    SONAR_BUILD_STRING,
    SONAR_SOURCE_ENCODING,
    SONAR_WORKING_DIRECTORY,
    SONAR_SCM_FORCE_RELOAD_ALL,
    SONAR_PYTHON_PYLINT_REPORT_PATH,
    SONAR_PYTHON_COVERAGE_REPORT_PATHS,
    SONAR_COVERAGE_EXCLUSIONS,
    SONAR_PYTHON_SKIP_UNCHANGED,
    SONAR_PYTHON_XUNIT_REPORT_PATH,
    SONAR_PYTHON_XUNIT_SKIP_DETAILS,
    SONAR_MODULES,
)
from pysonar_scanner.exceptions import UnexpectedCliArgument

EXPECTED_CONFIGURATION = {
    SONAR_TOKEN: "myToken",
    SONAR_PROJECT_KEY: "myProjectKey",
    SONAR_PROJECT_NAME: "myProjectName",
    SONAR_PROJECT_VERSION: "myProjectVersion",
    SONAR_PROJECT_DESCRIPTION: "myProjectDescription",
    SONAR_PROJECT_BASE_DIR: "mySonarProjectBaseDir",
    SONAR_VERBOSE: True,
    SONAR_SOURCES: "mySources",
    SONAR_TESTS: "myTests",
    SONAR_HOST_URL: "mySonarHostUrl",
    SONAR_SCANNER_SONARCLOUD_URL: "mySonarScannerCloudUrl",
    SONAR_SCANNER_API_BASE_URL: "mySonarScannerApiUrl",
    SONAR_SCANNER_OS: "windows",
    SONAR_SCANNER_ARCH: "x64",
    SONAR_SCANNER_CONNECT_TIMEOUT: 42,
    SONAR_SCANNER_INTERNAL_DUMP_TO_FILE: "mySonarScannerInternalDumpToFile",
    SONAR_SCANNER_INTERNAL_SQ_VERSION: "mySonarScannerInternalSqVersion",
    SONAR_SCANNER_SOCKET_TIMEOUT: 43,
    SONAR_SCANNER_RESPONSE_TIMEOUT: 44,
    SONAR_SCANNER_TRUSTSTORE_PATH: "mySonarScannerTruststorePath",
    SONAR_SCANNER_TRUSTSTORE_PASSWORD: "mySonarScannerTruststorePassword",
    SONAR_SCANNER_KEYSTORE_PATH: "mySonarScannerKeystorePath",
    SONAR_SCANNER_KEYSTORE_PASSWORD: "mySonarScannerKeystorePassword",
    SONAR_SCANNER_PROXY_HOST: "mySonarScannerProxyHost",
    SONAR_SCANNER_PROXY_PORT: 45,
    SONAR_SCANNER_PROXY_USER: "mySonarScannerProxyUser",
    SONAR_SCANNER_PROXY_PASSWORD: "mySonarScannerProxyPassword",
    SONAR_SCANNER_SKIP_JRE_PROVISIONING: True,
    SONAR_SCANNER_JAVA_EXE_PATH: "mySonarScannerJavaExePath",
    SONAR_SCANNER_JAVA_OPTS: "mySonarScannerJavaOpts",
    SONAR_SCANNER_JAVA_HEAP_SIZE: "8000Mb",
    SONAR_SCANNER_METADATA_FILEPATH: "myMetadataFilepath",
    SONAR_REGION: "us",
    SONAR_ORGANIZATION: "mySonarOrganization",
    SONAR_USER_HOME: "mySonarUserHome",
    SONAR_FILESIZE_LIMIT: 1000,
    SONAR_CPD_PYTHON_MINIMUM_TOKENS: 15,
    SONAR_CPD_PYTHON_MINIMUM_LINES: 100,
    SONAR_SCM_EXCLUSIONS_DISABLED: True,
    SONAR_LOG_LEVEL: "INFO",
    SONAR_QUALITYGATE_WAIT: True,
    SONAR_QUALITYGATE_TIMEOUT: 120,
    SONAR_EXTERNAL_ISSUES_REPORT_PATHS: "path/to/external/issues",
    SONAR_SARIF_REPORT_PATHS: "path/to/sarif/reports",
    SONAR_LINKS_CI: "http://ci.example.com",
    SONAR_LINKS_HOMEPAGE: "http://homepage.example.com",
    SONAR_LINKS_ISSUE: "http://issues.example.com",
    SONAR_LINKS_SCM: "http://scm.example.com",
    SONAR_BRANCH_NAME: "feature-branch",
    SONAR_PULLREQUEST_KEY: "123",
    SONAR_PULLREQUEST_BRANCH: "feature-branch",
    SONAR_PULLREQUEST_BASE: "main",
    SONAR_NEWCODE_REFERENCE_BRANCH: "develop",
    SONAR_SCM_REVISION: "abc123",
    SONAR_BUILD_STRING: "build-42",
    SONAR_SOURCE_ENCODING: "UTF-8",
    SONAR_WORKING_DIRECTORY: "/tmp/sonar",
    SONAR_SCM_FORCE_RELOAD_ALL: True,
    SONAR_PYTHON_PYLINT_REPORT_PATH: "path/to/pylint/report",
    SONAR_PYTHON_COVERAGE_REPORT_PATHS: "path/to/coverage1,path/to/coverage2",
    SONAR_COVERAGE_EXCLUSIONS: "*/.local/*,/usr/*,utils/tirefire.py",
    SONAR_PYTHON_SKIP_UNCHANGED: True,
    SONAR_PYTHON_XUNIT_REPORT_PATH: "path/to/xunit/report",
    SONAR_PYTHON_XUNIT_SKIP_DETAILS: True,
    SONAR_PYTHON_MYPY_REPORT_PATHS: "path/to/mypy/reports",
    SONAR_PYTHON_BANDIT_REPORT_PATHS: "path/to/bandit/reports",
    SONAR_PYTHON_FLAKE8_REPORT_PATHS: "path/to/flake8/reports",
    SONAR_PYTHON_RUFF_REPORT_PATHS: "path/to/ruff/reports",
    SONAR_MODULES: "module1,module2",
}


class TestCliConfigurationLoader(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    @patch("sys.argv", ["myscript.py", "--token", "myToken", "--sonar-project-key", "myProjectKey"])
    def test_minimal_cli_args(self):
        configuration = CliConfigurationLoader.load()

        expected_configuration = {
            SONAR_TOKEN: "myToken",
            SONAR_PROJECT_KEY: "myProjectKey",
        }
        self.assertDictEqual(configuration, expected_configuration)

    def test_alternative_cli_args(self):
        alternatives = [
            ["-t", "myToken", "-v", "--project-key", "myProjectKey", "--sonar-scanner-java-heap-size", "8000Mb"],
            [
                "--sonar-token",
                "myToken",
                "--sonar-verbose",
                "--sonar-project-key",
                "myProjectKey",
                "--java-heap-size",
                "8000Mb",
            ],
        ]
        for alternative in alternatives:
            with patch("sys.argv", ["myscript.py", *alternative]), patch("sys.stderr", new=StringIO()):
                configuration = CliConfigurationLoader.load()
                expected_configuration = {
                    SONAR_TOKEN: "myToken",
                    SONAR_VERBOSE: True,
                    SONAR_PROJECT_KEY: "myProjectKey",
                    SONAR_SCANNER_JAVA_HEAP_SIZE: "8000Mb",
                }
                self.assertDictEqual(configuration, expected_configuration)

    def test_alternative_report_cli_args(self):
        base_args = ["myscript.py", "-t", "myToken", "--sonar-project-key", "myProjectKey"]
        report_args = [
            "--bandit-report-paths",
            "path/to/bandit/reports",
            "--flake8-report-paths",
            "path/to/flake8/reports",
            "--mypy-report-paths",
            "path/to/mypy/reports",
            "--pylint-report-path",
            "path/to/pylint/report",
            "--coverage-report-paths",
            "path/to/coverage/reports",
            "--xunit-report-path",
            "path/to/xunit/report",
            "--ruff-report-paths",
            "path/to/ruff/reports",
            "--xunit-skip-details",
        ]

        expected_configuration = {
            SONAR_TOKEN: "myToken",
            SONAR_PROJECT_KEY: "myProjectKey",
            SONAR_PYTHON_BANDIT_REPORT_PATHS: "path/to/bandit/reports",
            SONAR_PYTHON_FLAKE8_REPORT_PATHS: "path/to/flake8/reports",
            SONAR_PYTHON_MYPY_REPORT_PATHS: "path/to/mypy/reports",
            SONAR_PYTHON_PYLINT_REPORT_PATH: "path/to/pylint/report",
            SONAR_PYTHON_COVERAGE_REPORT_PATHS: "path/to/coverage/reports",
            SONAR_PYTHON_XUNIT_REPORT_PATH: "path/to/xunit/report",
            SONAR_PYTHON_RUFF_REPORT_PATHS: "path/to/ruff/reports",
            SONAR_PYTHON_XUNIT_SKIP_DETAILS: True,
        }

        with patch("sys.argv", base_args + report_args), patch("sys.stderr", new=StringIO()):
            configuration = CliConfigurationLoader.load()
            self.assertDictEqual(configuration, expected_configuration)

    def test_multiple_alias_cli_args(self):
        alternatives = [
            ["-t", "overwrittenToken", "--sonar-token", "sonarToken"],
            ["--sonar-token", "overwrittenToken", "-t", "sonarToken"],
        ]
        for alternative in alternatives:
            with patch("sys.argv", ["myscript.py", *alternative]), patch("sys.stderr", new=StringIO()):
                configuration = CliConfigurationLoader.load()
                expected_configuration = {
                    SONAR_TOKEN: "sonarToken",
                }
                self.assertDictEqual(configuration, expected_configuration)

    @patch(
        "sys.argv",
        ["myscript.py", "-t", "myToken", "--sonar-project-key", "myProjectKey", "--sonar-scanner-os", "windows2"],
    )
    def test_impossible_os_choice(self):
        with patch("sys.stderr", new=StringIO()) as mock_stderr:
            with self.assertRaises(SystemExit):
                CliConfigurationLoader.load()

        error_output = mock_stderr.getvalue()
        self.assertIn("""invalid choice: 'windows2'""", error_output)

    @patch(
        "sys.argv",
        [
            "myscript.py",
            "-t",
            "myToken",
            "--sonar-project-key",
            "myProjectKey",
            "--sonar-project-name",
            "myProjectName",
            "--sonar-project-version",
            "myProjectVersion",
            "--sonar-project-description",
            "myProjectDescription",
            "--sonar-sources",
            "mySources",
            "--sonar-tests",
            "myTests",
            "-v",
            "--sonar-host-url",
            "mySonarHostUrl",
            "--sonar-region",
            "us",
            "--sonar-organization",
            "mySonarOrganization",
            "--sonar-user-home",
            "mySonarUserHome",
            "--sonar-scanner-cloud-url",
            "mySonarScannerCloudUrl",
            "--sonar-scanner-api-url",
            "mySonarScannerApiUrl",
            "--sonar-scanner-os",
            "windows",
            "--sonar-scanner-arch",
            "x64",
            "--skip-jre-provisioning",
            "--sonar-scanner-java-exe-path",
            "mySonarScannerJavaExePath",
            "--sonar-scanner-java-opts",
            "mySonarScannerJavaOpts",
            "--sonar-scanner-metadata-filepath",
            "myMetadataFilepath",
            "--sonar-scanner-internal-dump-to-file",
            "mySonarScannerInternalDumpToFile",
            "--sonar-scanner-internal-sq-version",
            "mySonarScannerInternalSqVersion",
            "--sonar-scanner-connect-timeout",
            "42",
            "--sonar-scanner-socket-timeout",
            "43",
            "--sonar-scanner-response-timeout",
            "44",
            "--sonar-scanner-truststore-path",
            "mySonarScannerTruststorePath",
            "--sonar-scanner-truststore-password",
            "mySonarScannerTruststorePassword",
            "--sonar-scanner-keystore-path",
            "mySonarScannerKeystorePath",
            "--sonar-scanner-keystore-password",
            "mySonarScannerKeystorePassword",
            "--sonar-scanner-proxy-host",
            "mySonarScannerProxyHost",
            "--sonar-scanner-proxy-port",
            "45",
            "--sonar-scanner-proxy-user",
            "mySonarScannerProxyUser",
            "--sonar-scanner-proxy-password",
            "mySonarScannerProxyPassword",
            "--sonar-project-base-dir",
            "mySonarProjectBaseDir",
            "--sonar-filesize-limit",
            "1000",
            "--sonar-scm-exclusions-disabled",
            "--sonar-cpd-python-minimum-tokens",
            "15",
            "--sonar-cpd-python-minimum-lines",
            "100",
            "--sonar-log-level",
            "INFO",
            "--sonar-qualitygate-wait",
            "--sonar-qualitygate-timeout",
            "120",
            "--sonar-external-issues-report-paths",
            "path/to/external/issues",
            "--sonar-sarif-report-paths",
            "path/to/sarif/reports",
            "--sonar-links-ci",
            "http://ci.example.com",
            "--sonar-links-homepage",
            "http://homepage.example.com",
            "--sonar-links-issue",
            "http://issues.example.com",
            "--sonar-links-scm",
            "http://scm.example.com",
            "--sonar-branch-name",
            "feature-branch",
            "--sonar-pullrequest-key",
            "123",
            "--sonar-pullrequest-branch",
            "feature-branch",
            "--sonar-pullrequest-base",
            "main",
            "--sonar-newcode-reference-branch",
            "develop",
            "--sonar-scm-revision",
            "abc123",
            "--sonar-build-string",
            "build-42",
            "--sonar-source-encoding",
            "UTF-8",
            "--sonar-working-directory",
            "/tmp/sonar",
            "--sonar-scm-force-reload-all",
            "--sonar-python-pylint-report-path",
            "path/to/pylint/report",
            "--sonar-python-coverage-report-paths",
            "path/to/coverage1,path/to/coverage2",
            "--sonar-coverage-exclusions",
            "*/.local/*,/usr/*,utils/tirefire.py",
            "--sonar-python-skip-unchanged",
            "--sonar-python-xunit-report-path",
            "path/to/xunit/report",
            "--sonar-python-xunit-skip-details",
            "--sonar-python-mypy-report-paths",
            "path/to/mypy/reports",
            "--sonar-python-bandit-report-paths",
            "path/to/bandit/reports",
            "--sonar-python-flake8-report-paths",
            "path/to/flake8/reports",
            "--sonar-python-ruff-report-paths",
            "path/to/ruff/reports",
            "--sonar-modules",
            "module1,module2",
            "--sonar-scanner-java-heap-size",
            "8000Mb",
        ],
    )
    def test_all_cli_args(self):
        configuration = CliConfigurationLoader.load()
        self.assertEqual(configuration, EXPECTED_CONFIGURATION)

    @patch(
        "sys.argv",
        [
            "myscript.py",
            "-Dsonar.token=myToken",
            "-Dsonar.projectKey=myProjectKey",
            "-Dsonar.projectName=myProjectName",
            "-Dsonar.projectVersion=myProjectVersion",
            "-Dsonar.projectDescription=myProjectDescription",
            "-Dsonar.verbose",
            "-Dsonar.sources=mySources",
            "-Dsonar.tests=myTests",
            "-Dsonar.host.url=mySonarHostUrl",
            "-Dsonar.scanner.cloudUrl=mySonarScannerCloudUrl",
            "-Dsonar.scanner.apiUrl=mySonarScannerApiUrl",
            "-Dsonar.scanner.os=windows",
            "-Dsonar.scanner.arch=x64",
            "-Dsonar.scanner.connectTimeout=42",
            "-Dsonar.scanner.internal.dumpToFile=mySonarScannerInternalDumpToFile",
            "-Dsonar.scanner.internal.sqVersion=mySonarScannerInternalSqVersion",
            "-Dsonar.scanner.socketTimeout=43",
            "-Dsonar.scanner.responseTimeout=44",
            "-Dsonar.scanner.truststorePath=mySonarScannerTruststorePath",
            "-Dsonar.scanner.truststorePassword=mySonarScannerTruststorePassword",
            "-Dsonar.scanner.keystorePath=mySonarScannerKeystorePath",
            "-Dsonar.scanner.keystorePassword=mySonarScannerKeystorePassword",
            "-Dsonar.scanner.proxyHost=mySonarScannerProxyHost",
            "-Dsonar.scanner.proxyPort=45",
            "-Dsonar.scanner.proxyUser=mySonarScannerProxyUser",
            "-Dsonar.scanner.proxyPassword=mySonarScannerProxyPassword",
            "-Dsonar.scanner.skipJreProvisioning",
            "-Dsonar.scanner.javaExePath=mySonarScannerJavaExePath",
            "-Dsonar.scanner.javaOpts=mySonarScannerJavaOpts",
            "-Dsonar.scanner.metadataFilepath=myMetadataFilepath",
            "-Dsonar.region=us",
            "-Dsonar.organization=mySonarOrganization",
            "-Dsonar.userHome=mySonarUserHome",
            "-Dsonar.projectBaseDir=mySonarProjectBaseDir",
            "-Dsonar.filesize.limit=1000",
            "-Dsonar.scm.exclusions.disabled=true",
            "-Dsonar.cpd.python.minimumTokens=15",
            "-Dsonar.cpd.python.minimumLines=100",
            "-Dsonar.qualitygate.wait=true",
            "-Dsonar.qualitygate.timeout=120",
            "-Dsonar.externalIssuesReportPaths=path/to/external/issues",
            "-Dsonar.sarifReportPaths=path/to/sarif/reports",
            "-Dsonar.links.ci=http://ci.example.com",
            "-Dsonar.links.homepage=http://homepage.example.com",
            "-Dsonar.links.issue=http://issues.example.com",
            "-Dsonar.links.scm=http://scm.example.com",
            "-Dsonar.branch.name=feature-branch",
            "-Dsonar.pullrequest.key=123",
            "-Dsonar.pullrequest.branch=feature-branch",
            "-Dsonar.pullrequest.base=main",
            "-Dsonar.newCode.referenceBranch=develop",
            "-Dsonar.scm.revision=abc123",
            "-Dsonar.buildString=build-42",
            "-Dsonar.sourceEncoding=UTF-8",
            "-Dsonar.working.directory=/tmp/sonar",
            "-Dsonar.scm.forceReloadAll=true",
            "-Dsonar.log.level=INFO",
            "-Dsonar.python.pylint.reportPath=path/to/pylint/report",
            "-Dsonar.python.coverage.reportPaths=path/to/coverage1,path/to/coverage2",
            "-Dsonar.coverage.exclusions=*/.local/*,/usr/*,utils/tirefire.py",
            "-Dsonar.python.skipUnchanged=true",
            "-Dsonar.python.xunit.reportPath=path/to/xunit/report",
            "-Dsonar.python.xunit.skipDetails=true",
            "-Dsonar.python.mypy.reportPaths=path/to/mypy/reports",
            "-Dsonar.python.bandit.reportPaths=path/to/bandit/reports",
            "-Dsonar.python.flake8.reportPaths=path/to/flake8/reports",
            "-Dsonar.python.ruff.reportPaths=path/to/ruff/reports",
            "-Dsonar.modules=module1,module2",
            "-Dsonar.scanner.javaHeapSize=8000Mb",
        ],
    )
    def test_jvm_style_cli_args(self):
        configuration = CliConfigurationLoader.load()
        self.assertEqual(configuration, EXPECTED_CONFIGURATION)

    def test_both_boolean_args_given(self):
        patch_template = ["myscript.py", "--token", "myToken", "--sonar-project-key", "myProjectKey"]

        with patch("sys.argv", patch_template):
            configuration = CliConfigurationLoader.load()
            self.assertFalse(configuration.get(SONAR_SCM_EXCLUSIONS_DISABLED))

        # the python args parser allows to use --no-* prefix to pass a False value to a boolean option
        with patch("sys.argv", [*patch_template, "--no-sonar-scm-exclusions-disabled"]):
            configuration = CliConfigurationLoader.load()
            self.assertFalse(configuration.get(SONAR_SCM_EXCLUSIONS_DISABLED))

        # When both options are given, a logic OR is applied on the two
        with patch(
            "sys.argv", [*patch_template, "--no-sonar-scm-exclusions-disabled", "-Dsonar.scm.exclusions.disabled=true"]
        ):
            configuration = CliConfigurationLoader.load()
            self.assertTrue(configuration.get(SONAR_SCM_EXCLUSIONS_DISABLED))

        with patch(
            "sys.argv", [*patch_template, "-Dsonar.scm.exclusions.disabled=true", "--sonar-scm-exclusions-disabled"]
        ):
            configuration = CliConfigurationLoader.load()
            self.assertTrue(configuration.get(SONAR_SCM_EXCLUSIONS_DISABLED))

        with patch("sys.argv", [*patch_template, "--sonar-scm-exclusions-disabled"]):
            configuration = CliConfigurationLoader.load()
            self.assertTrue(configuration.get(SONAR_SCM_EXCLUSIONS_DISABLED))

        with patch("sys.argv", [*patch_template, "-Dsonar.scm.exclusions.disabled=true"]):
            configuration = CliConfigurationLoader.load()
            self.assertTrue(configuration.get(SONAR_SCM_EXCLUSIONS_DISABLED))

    @patch(
        "sys.argv",
        [
            "myscript.py",
            "--token",
            "myToken",
            "--sonar-project-key",
            "myProjectKey",
            "-Dunknown.property=unknownValue",
            "-Danother.unknown.property=anotherValue",
        ],
    )
    def test_unknown_args_with_D_prefix(self):
        configuration = CliConfigurationLoader.load()
        expected_configuration = {
            SONAR_TOKEN: "myToken",
            SONAR_PROJECT_KEY: "myProjectKey",
            "unknown.property": "unknownValue",
            "another.unknown.property": "anotherValue",
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
            "-Dunknown.flag",
        ],
    )
    def test_unknown_args_no_value(self):
        configuration = CliConfigurationLoader.load()
        expected_configuration = {
            SONAR_TOKEN: "myToken",
            SONAR_PROJECT_KEY: "myProjectKey",
            "unknown.flag": "true",
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
            "-unknown.property=some_value",
        ],
    )
    def test_unknown_args_missing_D_prefix(self):
        with self.assertRaises(
            UnexpectedCliArgument, msg="Unexpected argument format: -unknown.property=some_value=another_value"
        ):
            CliConfigurationLoader.load()

    @patch(
        "sys.argv",
        [
            "myscript.py",
            "--token",
            "myToken",
            "--sonar-project-key",
            "myProjectKey",
            "-Dsonar.unknown.property=some_value=another_value",
        ],
    )
    def test_unknown_args_unexpected_format(self):
        configuration = CliConfigurationLoader.load()
        expected_configuration = {
            SONAR_TOKEN: "myToken",
            SONAR_PROJECT_KEY: "myProjectKey",
            "sonar.unknown.property": "some_value=another_value",
        }
        self.assertDictEqual(configuration, expected_configuration)
