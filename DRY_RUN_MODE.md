# Dry Run / Debug Mode for Pysonar Scanner

The Pysonar scanner supports a **dry-run mode** that helps you troubleshoot configuration issues without connecting to a SonarQube server or submitting analysis results. This is particularly useful when:

- Setting up new projects
- Adjusting coverage report paths
- Validating configuration properties
- Debugging analysis failures related to configuration

## Enabling Dry Run Mode

To run the scanner in dry-run mode, add the `--dry-run` flag:

```bash
pysonar --token "myToken" --project-key "my:project" --dry-run
```

Alternatively, use the property format:

```bash
pysonar -Dsonar.scanner.dryRun=true
```

Or set it as an environment variable:

```bash
export SONAR_SCANNER_DRY_RUN=true
pysonar
```

## What Dry Run Mode Does

When dry-run mode is enabled, the scanner:

1. **Skips SonarQube server validation** - No connection attempt to the SonarQube server is made
2. **Skips analysis submission** - No data is sent to or modified on the server
3. **Resolves configuration** - Loads configuration from all sources (CLI, environment variables, pyproject.toml, etc.)
4. **Reports resolved configuration** - Displays the detected settings including:
   - Project key and name
   - Organization (if applicable)
   - Detected main source directories
   - Detected test source directories
   - Configured coverage report paths
   - Server URL (if configured)
5. **Validates coverage reports** - Checks coverage report paths and formats with clear error reporting

## Configuration Report Output

In dry-run mode, the scanner outputs a configuration summary. Example:

```
================================================================================
DRY RUN MODE - Configuration Report
================================================================================

Project Configuration:
  Project Key: my:project
  Project Name: My Project
  Organization: my-org

Server Configuration:
  Host Url: https://sonarcloud.io

Source Configuration:
  Sources: src
  Tests: tests

Coverage Configuration:
  Coverage Report Paths: coverage/cobertura.xml

================================================================================
DRY RUN MODE - Validation Results
================================================================================

✓ Configuration validation PASSED

================================================================================
```

## Coverage Report Validation

The scanner validates coverage reports by checking:

1. **File existence** - Verifies that the file exists at the specified path
2. **File readability** - Ensures the file is readable and accessible
3. **File format** - Validates that coverage reports are in valid Cobertura XML format
4. **Root element** - Checks that XML root element is `<coverage>` (expected Cobertura format)

### Example: Coverage Report Validation Output

Successful validation:

```
Coverage Report Paths: coverage.xml

✓ Coverage report is valid Cobertura XML: coverage.xml
```

Missing file error:

```
✗ Configuration validation FAILED with the following issues:
  • Coverage report not found: coverage.xml (resolved to /project/coverage.xml)
```

Invalid format error:

```
✗ Configuration validation FAILED with the following issues:
  • Coverage report is not valid XML (Cobertura format): coverage.xml
    Parse error: XML not well-formed (invalid token)
```

## Exit Codes

- **0**: Configuration validation passed, no errors found
- **1**: Configuration validation failed, errors were found

## Use Cases

### 1. Validating Coverage Report Paths

Before running a full analysis, verify that coverage reports are correctly configured:

```bash
pysonar \
  --token "myToken" \
  --project-key "my:project" \
  --sonar-python-coverage-report-paths "coverage/cobertura.xml" \
  --dry-run
```

### 2. Checking Configuration Resolution

Verify that all configuration sources are properly resolved:

```bash
# Set configuration in multiple places
export SONAR_HOST_URL="https://sonarqube.example.com"
pysonar \
  --token "myToken" \
  --project-key "my:project" \
  --dry-run
```

This helps ensure that environment variables, CLI arguments, and configuration files are being read correctly.

### 3. Troubleshooting Failed Analysis

If an analysis fails, use dry-run mode to quickly identify configuration issues without waiting for a full analysis:

```bash
# First, validate the configuration
pysonar \
  --token "myToken" \
  --project-key "my:project" \
  --sonar-python-coverage-report-paths "coverage/cobertura.xml" \
  --dry-run

# If successful, run the full analysis
pysonar \
  --token "myToken" \
  --project-key "my:project" \
  --sonar-python-coverage-report-paths "coverage/cobertura.xml"
```

### 4. Setting Up New Projects

When onboarding a new project, use dry-run mode to validate the setup before the first full analysis:

```bash
# Create your configuration in pyproject.toml or via CLI
# Then validate it:
pysonar --dry-run -v
```

## Common Issues and Solutions

### Issue: Coverage report not found

**Error message:**
```
Coverage report not found: coverage.xml (resolved to /project/coverage.xml)
```

**Solution:**
- Verify the file path is correct relative to the project base directory
- Check that the file actually exists: `ls -la /project/coverage.xml`
- Use absolute paths if relative paths are not working
- Ensure the scanner is run from the correct directory

### Issue: Coverage report is not readable

**Error message:**
```
Coverage report is not readable (permission denied): coverage.xml
```

**Solution:**
- Check file permissions: `ls -l coverage.xml`
- Make the file readable: `chmod 644 coverage.xml`
- Ensure the process running the scanner has read access

### Issue: Invalid XML format

**Error message:**
```
Coverage report is not valid XML (Cobertura format): coverage.xml
  Parse error: XML not well-formed (invalid token)
```

**Solution:**
- Verify the coverage report was generated correctly
- Try generating the coverage report again
- Check the coverage tool documentation for proper output format

### Issue: Wrong root element

**Warning message:**
```
Coverage report root element is 'report', expected 'coverage' (Cobertura format)
```

**Solution:**
- The coverage report may not be in Cobertura XML format
- Check that your coverage tool is configured to output Cobertura XML
- For Python projects using coverage.py, use: `coverage xml`

## Integration with CI/CD

Dry-run mode is particularly useful in CI/CD pipelines to fail fast on configuration issues:

### GitHub Actions Example

```yaml
- name: Validate configuration
  run: |
    pysonar \
      --token ${{ secrets.SONAR_TOKEN }} \
      --project-key ${{ env.SONAR_PROJECT_KEY }} \
      --sonar-python-coverage-report-paths "coverage/cobertura.xml" \
      --dry-run

- name: Run analysis
  run: |
    pysonar \
      --token ${{ secrets.SONAR_TOKEN }} \
      --project-key ${{ env.SONAR_PROJECT_KEY }} \
      --sonar-python-coverage-report-paths "coverage/cobertura.xml"
```

### GitLab CI Example

```yaml
validate_config:
  script:
    - pysonar
        --token $SONAR_TOKEN
        --project-key $SONAR_PROJECT_KEY
        --sonar-python-coverage-report-paths "coverage/cobertura.xml"
        --dry-run

analyze:
  script:
    - pysonar
        --token $SONAR_TOKEN
        --project-key $SONAR_PROJECT_KEY
        --sonar-python-coverage-report-paths "coverage/cobertura.xml"
```

## Additional Resources

- [CLI Arguments Reference](CLI_ARGS.md)
- [SonarQube Analysis Parameters](https://docs.sonarsource.com/sonarqube-server/latest/analyzing-source-code/analysis-parameters/)
- [Cobertura XML Format](https://cobertura.github.io/cobertura/)
