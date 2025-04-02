# Sonar Scanner Python CLI Arguments

## Authentication

| Option | Description |
| ------ | ----------- |
| `--sonar-host-url`, `-Dsonar.host.url` | SonarQube Server base URL. For example, http://localhost:9000 for a local instance of SonarQube Server |
| `--sonar-region`, `-Dsonar.region` | The region to contact, only for SonarQube Cloud |
| `-t`, `--token`, `--sonar-token`, `-Dsonar.token` | Token used to authenticate against the SonarQube Server or SonarQube Cloud |

## Project Configuration

| Option | Description |
| ------ | ----------- |
| `--sonar-project-base-dir`, `-Dsonar.projectBaseDir` | Directory containing the project to be analyzed. Default is the current directory |
| `--sonar-project-description`, `-Dsonar.projectDescription` | Description of the project |
| `--sonar-project-key`, `-Dsonar.projectKey` | Key of the project that usually corresponds to the project name in SonarQube |
| `--sonar-project-name`, `-Dsonar.projectName` | Name of the project in SonarQube |
| `--sonar-project-version`, `-Dsonar.projectVersion` | Version of the project |
| `--sonar-sources`, `-Dsonar.sources` | The analysis scope for main source code (non-test code) in the project |
| `--sonar-tests`, `-Dsonar.tests` | The analysis scope for test source code in the project |

## Analysis Configuration

| Option | Description |
| ------ | ----------- |
| `--sonar-filesize-limit`, `-Dsonar.filesize.limit` | Sets the limit in MB for files to be discarded from the analysis scope if the size is greater than specified |
| `--sonar-python-version`, `-Dsonar.python.version` | Python version used for the project |
| `-v`, `--verbose`, `--no-verbose`, `--sonar-verbose`, `--no-sonar-verbose`, `-Dsonar.verbose` | Increase output verbosity |

## Report Integration

| Option | Description |
| ------ | ----------- |
| `--sonar-external-issues-report-paths`, `-Dsonar.externalIssuesReportPaths` | Comma-delimited list of paths to generic issue reports |
| `--sonar-python-bandit-report-paths`, `--bandit-report-paths`, `-Dsonar.python.bandit.reportPaths` | Comma-separated bandit report paths, relative to project's root |
| `--sonar-python-coverage-report-paths`, `--coverage-report-paths`, `-Dsonar.python.coverage.reportPaths` | Comma-delimited list of paths to coverage reports in the Cobertura XML format. |
| `--sonar-python-flake8-report-paths`, `--flake8-report-paths`, `-Dsonar.python.flake8.reportPaths` | Comma-separated flake8 report paths, relative to project's root |
| `--sonar-python-mypy-report-paths`, `--mypy-report-paths`, `-Dsonar.python.mypy.reportPaths` | Comma-separated mypy report paths, relative to project's root |
| `--sonar-python-pylint-report-path`, `--pylint-report-path`, `-Dsonar.python.pylint.reportPath` | Path to third-parties issues report file for pylint |
| `--sonar-python-ruff-report-paths`, `--ruff-report-paths`, `-Dsonar.python.ruff.reportPaths` | Comma-separated ruff report paths, relative to project's root |
| `--sonar-python-xunit-report-path`, `--xunit-report-path`, `-Dsonar.python.xunit.reportPath` | Path to the report of test execution, relative to project's root |
| `--sonar-python-xunit-skip-details`, `--no-sonar-python-xunit-skip-details`, `--xunit-skip-details`, `--no-xunit-skip-details` | When enabled, the test execution statistics is provided only on project level |
| `--sonar-sarif-report-paths`, `-Dsonar.sarifReportPaths` | Comma-delimited list of paths to SARIF issue reports |

## Other

| Option | Description |
| ------ | ----------- |
| `--skip-jre-provisioning`, `-Dsonar.scanner.skipJreProvisioning` | If provided, the provisioning of the JRE will be skipped |
| `--sonar-branch-name`, `-Dsonar.branch.name` | Name of the branch being analyzed |
| `--sonar-build-string`, `-Dsonar.buildString` | The string passed with this property will be stored with the analysis and available in the results of api/project_analyses/search, thus allowing you to later identify a specific analysis and obtain its key for use with api/new_code_periods/set on the SPECIFIC_ANALYSIS type |
| `--sonar-cpd-python-minimum-lines`, `-Dsonar.cpd.python.minimumLines` | Minimum number of tokens to be considered as a duplicated block of code |
| `--sonar-cpd-python-minimum-tokens`, `-Dsonar.cpd.python.minimumTokens` | Minimum number of tokens to be considered as a duplicated block of code |
| `--sonar-links-ci`, `-Dsonar.links.ci` | The URL of the continuous integration system used |
| `--sonar-links-homepage`, `-Dsonar.links.homepage` | The URL of the build project home page |
| `--sonar-links-issue`, `-Dsonar.links.issue` | The URL to the issue tracker being used |
| `--sonar-links-scm`, `-Dsonar.links.scm` | The URL of the build project source code repository |
| `--sonar-log-level`, `-Dsonar.log.level` | Log level during the analysis |
| `--sonar-modules`, `-Dsonar.modules` | Comma-delimited list of modules to analyze |
| `--sonar-newcode-reference-branch`, `-Dsonar.newCode.referenceBranch` | Reference branch for new code definition |
| `--sonar-pullrequest-base`, `-Dsonar.pullrequest.base` | Base branch of the pull request being analyzed |
| `--sonar-pullrequest-branch`, `-Dsonar.pullrequest.branch` | Branch of the pull request being analyzed |
| `--sonar-pullrequest-key`, `-Dsonar.pullrequest.key` | Key of the pull request being analyzed |
| `--sonar-python-skip-unchanged`, `--no-sonar-python-skip-unchanged` | Override the SonarQube configuration of skipping or not the analysis of unchanged Python files |
| `--sonar-qualitygate-timeout`, `-Dsonar.qualitygate.timeout` | The number of seconds that the scanner should wait for a report to be processed |
| `--sonar-qualitygate-wait`, `--no-sonar-qualitygate-wait` | Forces the analysis step to poll the server instance and wait for the Quality Gate status |
| `--sonar-scanner-api-url`, `-Dsonar.scanner.apiUrl` | Base URL for all REST-compliant API calls, https://api.sonarcloud.io for example |
| `--sonar-scanner-arch`, `-Dsonar.scanner.arch` | Architecture on which the scanner will be running |
| `--sonar-scanner-cloud-url`, `-Dsonar.scanner.cloudUrl` | SonarQube Cloud base URL, https://sonarcloud.io for example |
| `--sonar-scanner-connect-timeout`, `-Dsonar.scanner.connectTimeout` | Time period to establish connections with the server (in seconds) |
| `--sonar-scanner-internal-dump-to-file`, `-Dsonar.scanner.internal.dumpToFile` | Filename where the input to the scanner engine will be dumped. Useful for debugging |
| `--sonar-scanner-internal-sq-version`, `-Dsonar.scanner.internal.sqVersion` | Emulate the result of the call to get SQ server version.  Useful for debugging with --sonar-scanner-internal-dump-to-file |
| `--sonar-scanner-java-exe-path`, `-Dsonar.scanner.javaExePath` | If defined, the scanner engine will be run with this JRE |
| `--sonar-scanner-java-opts`, `-Dsonar.scanner.javaOpts` | Arguments provided to the JVM when running the scanner |
| `--sonar-scanner-keystore-password`, `-Dsonar.scanner.keystorePassword` | Password to access the keystore |
| `--sonar-scanner-keystore-path`, `-Dsonar.scanner.keystorePath` | Path to the keystore containing the client certificates used by the scanner. By default, <sonar.userHome>/ssl/keystore.p12 |
| `--sonar-scanner-metadata-filepath`, `-Dsonar.scanner.metadataFilepath` | Sets the location where the scanner writes the report-task.txt file containing among other things the ceTaskId |
| `--sonar-scanner-os`, `-Dsonar.scanner.os` | OS running the scanner |
| `--sonar-scanner-proxy-host`, `-Dsonar.scanner.proxyHost` | Proxy host |
| `--sonar-scanner-proxy-password`, `-Dsonar.scanner.proxyPassword` | Proxy password |
| `--sonar-scanner-proxy-port`, `-Dsonar.scanner.proxyPort` | Proxy port |
| `--sonar-scanner-proxy-user`, `-Dsonar.scanner.proxyUser` | Proxy user |
| `--sonar-scanner-response-timeout`, `-Dsonar.scanner.responseTimeout` | Time period required to process an HTTP call: from sending a request to receiving a response (in seconds) |
| `--sonar-scanner-socket-timeout`, `-Dsonar.scanner.socketTimeout` | Maximum time of inactivity between two data packets when exchanging data with the server (in seconds) |
| `--sonar-scanner-truststore-password`, `-Dsonar.scanner.truststorePassword` | Password to access the truststore |
| `--sonar-scanner-truststore-path`, `-Dsonar.scanner.truststorePath` | Path to the keystore containing trusted server certificates, used by the Scanner in addition to OS and the built-in certificates |
| `--sonar-scm-exclusions-disabled`, `--no-sonar-scm-exclusions-disabled` | Defines whether files ignored by the SCM, e.g., files listed in .gitignore, will be excluded from the analysis or not |
| `--sonar-scm-force-reload-all`, `--no-sonar-scm-force-reload-all` | Set this property to true to load blame information for all files, which may significantly increase analysis duration |
| `--sonar-scm-revision`, `-Dsonar.scm.revision` | Overrides the revision, for instance, the Git sha1, displayed in analysis results |
| `--sonar-source-encoding`, `-Dsonar.sourceEncoding` | Encoding of the source files. For example, UTF-8, MacRoman, Shift_JIS |
| `--sonar-user-home`, `-Dsonar.userHome` | Base sonar directory, ~/.sonar by default |
| `--sonar-working-directory`, `-Dsonar.working.directory` | Path to the working directory used by the Sonar scanner during a project analysis to store temporary data |
| `--toml-path` | Path to the pyproject.toml file. If not provided, it will look in the SONAR_PROJECT_BASE_DIR |
| `-Dsonar.python.skipUnchanged` | Equivalent to --sonar-python-skip-unchanged |
| `-Dsonar.python.xunit.skipDetails` | Equivalent to -Dsonar.python.xunit.skipDetails |
| `-Dsonar.qualitygate.wait` | Equivalent to --sonar-qualitygate-wait |
| `-Dsonar.scm.exclusions.disabled` | Equivalent to --sonar-scm-exclusions-disabled |
| `-Dsonar.scm.forceReloadAll` | Equivalent to --sonar-scm-force-reload-all |
