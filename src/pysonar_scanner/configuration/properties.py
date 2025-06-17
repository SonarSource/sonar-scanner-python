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
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional

Key = str

SONAR_HOST_URL: Key = "sonar.host.url"
SONAR_SCANNER_SONARCLOUD_URL: Key = "sonar.scanner.sonarcloudUrl"
SONAR_SCANNER_API_BASE_URL: Key = "sonar.scanner.apiBaseUrl"
SONAR_REGION: Key = "sonar.region"
SONAR_ORGANIZATION: Key = "sonar.organization"
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
SONAR_SCANNER_METADATA_FILEPATH: Key = "sonar.scanner.metadataFilePath"
SONAR_SCANNER_JAVA_OPTS: Key = "sonar.scanner.javaOpts"
SONAR_SCANNER_JAVA_HEAP_SIZE: Key = "sonar.scanner.javaHeapSize"
SONAR_PROJECT_BASE_DIR: Key = "sonar.projectBaseDir"
SONAR_PROJECT_KEY: Key = "sonar.projectKey"
SONAR_PROJECT_NAME: Key = "sonar.projectName"
SONAR_PROJECT_VERSION: Key = "sonar.projectVersion"
SONAR_PROJECT_DESCRIPTION: Key = "sonar.projectDescription"
SONAR_SCM_EXCLUSIONS_DISABLED = "sonar.scm.exclusions.disabled"
SONAR_SOURCES: Key = "sonar.sources"
SONAR_EXCLUSIONS: Key = "sonar.exclusions"
SONAR_TESTS: Key = "sonar.tests"
SONAR_FILESIZE_LIMIT: Key = "sonar.filesize.limit"
SONAR_CPD_PYTHON_MINIMUM_TOKENS: Key = "sonar.cpd.python.minimumTokens"
SONAR_CPD_PYTHON_MINIMUM_LINES: Key = "sonar.cpd.python.minimumLines"
SONAR_LOG_LEVEL: Key = "sonar.log.level"
SONAR_QUALITYGATE_WAIT: Key = "sonar.qualitygate.wait"
SONAR_QUALITYGATE_TIMEOUT: Key = "sonar.qualitygate.timeout"
SONAR_EXTERNAL_ISSUES_REPORT_PATHS: Key = "sonar.externalIssuesReportPaths"
SONAR_SARIF_REPORT_PATHS: Key = "sonar.sarifReportPaths"
SONAR_LINKS_CI: Key = "sonar.links.ci"
SONAR_LINKS_HOMEPAGE: Key = "sonar.links.homepage"
SONAR_LINKS_ISSUE: Key = "sonar.links.issue"
SONAR_LINKS_SCM: Key = "sonar.links.scm"
SONAR_BRANCH_NAME: Key = "sonar.branch.name"
SONAR_PULLREQUEST_KEY: Key = "sonar.pullrequest.key"
SONAR_PULLREQUEST_BRANCH: Key = "sonar.pullrequest.branch"
SONAR_PULLREQUEST_BASE: Key = "sonar.pullrequest.base"
SONAR_PYTHON_VERSION: Key = "sonar.python.version"
SONAR_PYTHON_PYLINT_REPORT_PATH: Key = "sonar.python.pylint.reportPath"
SONAR_PYTHON_COVERAGE_REPORT_PATHS: Key = "sonar.python.coverage.reportPaths"
SONAR_COVERAGE_EXCLUSIONS: Key = "sonar.coverage.exclusions"
SONAR_PYTHON_SKIP_UNCHANGED: Key = "sonar.python.skipUnchanged"
SONAR_NEWCODE_REFERENCE_BRANCH: Key = "sonar.newCode.referenceBranch"
SONAR_SCM_REVISION: Key = "sonar.scm.revision"
SONAR_BUILD_STRING: Key = "sonar.buildString"
SONAR_SOURCE_ENCODING: Key = "sonar.sourceEncoding"
SONAR_WORKING_DIRECTORY: Key = "sonar.working.directory"
SONAR_SCM_FORCE_RELOAD_ALL: Key = "sonar.scm.forceReloadAll"
SONAR_MODULES: Key = "sonar.modules"
SONAR_PYTHON_XUNIT_REPORT_PATH: Key = "sonar.python.xunit.reportPath"
SONAR_PYTHON_XUNIT_SKIP_DETAILS: Key = "sonar.python.xunit.skipDetails"
SONAR_PYTHON_MYPY_REPORT_PATHS: Key = "sonar.python.mypy.reportPaths"
SONAR_PYTHON_BANDIT_REPORT_PATHS: Key = "sonar.python.bandit.reportPaths"
SONAR_PYTHON_FLAKE8_REPORT_PATHS: Key = "sonar.python.flake8.reportPaths"
SONAR_PYTHON_RUFF_REPORT_PATHS: Key = "sonar.python.ruff.reportPaths"
TOML_PATH: Key = "toml-path"

# ============ DEPRECATED ==============
SONAR_SCANNER_OPTS: Key = "sonar.scanner.opts"


@dataclass
class Property:
    name: Key
    """name in the format of `sonar.scanner.appVersion`"""

    default_value: Optional[Any]
    """default value for the property; if None, no default value is set"""

    cli_getter: Optional[Callable[[argparse.Namespace], Any]] = None
    """function to get the value from the CLI arguments namespace. If None, the property is not settable via CLI"""

    deprecation_message: Optional[str] = None

    def python_name(self) -> str:
        """Convert Java-style camel case name to Python-style kebab-case name."""
        result = []
        for i, char in enumerate(self.name):
            if char.isupper() and i > 0:
                result.append("-")
            result.append(char.lower())
        return "".join(result)

    def env_variable_name(self) -> str:
        """Convert property name to environment variable name format.
        Example: sonar.scanner.proxyPort -> SONAR_SCANNER_PROXY_PORT"""
        # Replace dots with underscores
        env_name = self.name.replace(".", "_")

        # Insert underscores before uppercase letters (camelCase to snake_case)
        result = []
        for i, char in enumerate(env_name):
            if char.isupper() and i > 0 and env_name[i - 1] != "_":
                result.append("_")
            result.append(char)
        # Convert to uppercase
        return "".join(result).upper()


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
        name=SONAR_ORGANIZATION, 
        default_value=None, 
        cli_getter=lambda args: args.sonar_organization
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
        default_value=None,
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
        name=SONAR_SCANNER_JAVA_HEAP_SIZE,
        default_value=None,
        cli_getter=lambda args: args.sonar_scanner_java_heap_size
    ),
    Property(
        name=SONAR_SCANNER_METADATA_FILEPATH,
        default_value=None,
        cli_getter=lambda args: args.sonar_scanner_metadata_filepath
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
        name=SONAR_SOURCES,
        default_value=None,
        cli_getter=lambda args: args.sonar_sources
    ),
    Property(
        name=SONAR_TESTS,
        default_value=None,
        cli_getter=lambda args: args.sonar_tests
    ),
    Property(
        name=SONAR_FILESIZE_LIMIT,
        default_value=None,
        cli_getter=lambda args: args.sonar_filesize_limit
    ),
    Property(
        name=SONAR_SCM_EXCLUSIONS_DISABLED,
        default_value=None,
        cli_getter=lambda args: args.sonar_scm_exclusions_disabled or getattr(args, "Dsonar.scm.exclusions.disabled")
    ),
    Property(
        name=SONAR_CPD_PYTHON_MINIMUM_TOKENS,
        default_value=None,
        cli_getter=lambda args: args.sonar_cpd_python_minimum_tokens
    ),
    Property(
        name=SONAR_CPD_PYTHON_MINIMUM_LINES,
        default_value=None,
        cli_getter=lambda args: args.sonar_cpd_python_minimum_lines
    ),
    Property(
        name=SONAR_LOG_LEVEL,
        default_value=None,
        cli_getter=lambda args: args.sonar_log_level
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
    Property(
        name=SONAR_QUALITYGATE_WAIT, 
        default_value=None, 
        cli_getter=lambda args: args.sonar_qualitygate_wait or getattr(args, "Dsonar.qualitygate.wait")
    ),
    Property(
        name=SONAR_QUALITYGATE_TIMEOUT, 
        default_value=None, 
        cli_getter=lambda args: args.sonar_qualitygate_timeout
    ),
    Property(
        name=SONAR_EXTERNAL_ISSUES_REPORT_PATHS, 
        default_value=None, 
        cli_getter=lambda args: args.sonar_external_issues_report_paths
    ),
    Property(
        name=SONAR_SARIF_REPORT_PATHS, 
        default_value=None,
        cli_getter=lambda args: args.sonar_sarif_report_paths
    ),
    Property(
        name=SONAR_LINKS_CI, 
        default_value=None, 
        cli_getter=lambda args: args.sonar_links_ci
    ),
    Property(
        name=SONAR_LINKS_HOMEPAGE, 
        default_value=None, 
        cli_getter=lambda args: args.sonar_links_homepage
    ),
    Property(
        name=SONAR_LINKS_ISSUE, 
        default_value=None, 
        cli_getter=lambda args: args.sonar_links_issue
    ),
    Property(
        name=SONAR_LINKS_SCM, 
        default_value=None, 
        cli_getter=lambda args: args.sonar_links_scm
    ),
    Property(
        name=SONAR_BRANCH_NAME, 
        default_value=None, 
        cli_getter=lambda args: args.sonar_branch_name
    ),
    Property(
        name=SONAR_PULLREQUEST_KEY, 
        default_value=None, 
        cli_getter=lambda args: args.sonar_pullrequest_key
    ),
    Property(
        name=SONAR_PULLREQUEST_BRANCH, 
        default_value=None, 
        cli_getter=lambda args: args.sonar_pullrequest_branch
    ),
    Property(
        name=SONAR_PULLREQUEST_BASE, 
        default_value=None, 
        cli_getter=lambda args: args.sonar_pullrequest_base
    ),
    Property(
        name=SONAR_NEWCODE_REFERENCE_BRANCH, 
        default_value=None, 
        cli_getter=lambda args: args.sonar_newcode_reference_branch
    ),
    Property(
        name=SONAR_SCM_REVISION, 
        default_value=None, 
        cli_getter=lambda args: args.sonar_scm_revision
    ),
    Property(
        name=SONAR_BUILD_STRING, 
        default_value=None, 
        cli_getter=lambda args: args.sonar_build_string
    ),
    Property(
        name=SONAR_SOURCE_ENCODING, 
        default_value=None, 
        cli_getter=lambda args: args.sonar_source_encoding
    ),
    Property(
        name=SONAR_WORKING_DIRECTORY, 
        default_value=None, 
        cli_getter=lambda args: args.sonar_working_directory
    ),
    Property(
        name=SONAR_SCM_FORCE_RELOAD_ALL, 
        default_value=None, 
        cli_getter=lambda args: args.sonar_scm_force_reload_all or getattr(args, "Dsonar.scm.forceReloadAll")
    ),
    Property(
        name=SONAR_PYTHON_PYLINT_REPORT_PATH,
        default_value=None,
        cli_getter=lambda args: args.sonar_python_pylint_report_path
    ),
    Property(
        name=SONAR_PYTHON_COVERAGE_REPORT_PATHS,
        default_value=None,
        cli_getter=lambda args: args.sonar_python_coverage_report_paths
    ),
    Property(
        name=SONAR_COVERAGE_EXCLUSIONS,
        default_value=None,
        cli_getter=lambda args: args.sonar_coverage_exclusions
    ),
    Property(
        name=SONAR_PYTHON_SKIP_UNCHANGED,
        default_value=None,
        cli_getter=lambda args: args.sonar_python_skip_unchanged or getattr(args, "Dsonar.python.skipUnchanged")
    ),
    Property(
        name=SONAR_PYTHON_XUNIT_REPORT_PATH,
        default_value=None,
        cli_getter=lambda args: args.sonar_python_xunit_report_path
    ),
    Property(
        name=SONAR_PYTHON_XUNIT_SKIP_DETAILS,
        default_value=None,
        cli_getter=lambda args: args.sonar_python_xunit_skip_details or getattr(args, "Dsonar.python.xunit.skipDetails")
    ),
    Property(
        name=SONAR_PYTHON_MYPY_REPORT_PATHS,
        default_value=None,
        cli_getter=lambda args: args.sonar_python_mypy_report_paths
    ),
    Property(
        name=SONAR_PYTHON_BANDIT_REPORT_PATHS,
        default_value=None,
        cli_getter=lambda args: args.sonar_python_bandit_report_paths
    ),
    Property(
        name=SONAR_PYTHON_FLAKE8_REPORT_PATHS,
        default_value=None,
        cli_getter=lambda args: args.sonar_python_flake8_report_paths
    ),
    Property(
        name=SONAR_PYTHON_RUFF_REPORT_PATHS,
        default_value=None,
        cli_getter=lambda args: args.sonar_python_ruff_report_paths
    ),
    Property(
        name=SONAR_MODULES,
        default_value=None,
        cli_getter=lambda args: args.sonar_modules
    ),
    Property(
        name=SONAR_SCANNER_OPTS,
        default_value=None,
        cli_getter=None,
        deprecation_message="SONAR_SCANNER_OPTS is deprecated, please use SONAR_SCANNER_JAVA_OPTS instead."
    )
]
# fmt: on
