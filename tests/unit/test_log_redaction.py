#
# Sonar Scanner Python
# Copyright (C) 2011-2026 SonarSource Sàrl
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
import json
import logging
import pathlib
from unittest.mock import Mock

import pytest

from pysonar_scanner import __main__ as main
from pysonar_scanner import scannerengine
from pysonar_scanner.jre import JREResolvedPath


@pytest.fixture
def restore_logging_handlers(caplog):
    logger = logging.getLogger()
    original_handlers = set(logger.handlers)
    original_level = logger.level
    yield
    for handler in set(logger.handlers) - original_handlers:
        logger.removeHandler(handler)
    logger.setLevel(original_level)


@pytest.mark.parametrize("token_source", ["cli", "environment", "json", "properties", "toml"])
def test_verbose_scan_masks_credentials_but_preserves_engine_input(
    token_source, monkeypatch, caplog, restore_logging_handlers, tmp_path
):
    credentials = {
        "sonar.token": "dummy-auth-value",
        "sonar.login": "dummy-login-value",
        "sonar.password": "dummy-password-value",
        "sonar.scanner.proxyPassword": "dummy-proxy-value",
        "sonar.scanner.keystorePassword": 'dummy-key-\\value-"é',
        "sonar.scanner.truststorePassword": "dummy-trust-value",
        "custom.secret": "dummy-custom-value",
        "custom.apiKey": "dummy-api-key-value",
        "custom.credential": "dummy-credential-value",
    }
    environment_properties = {key: value for key, value in credentials.items() if key != "sonar.token"}
    environment_properties["sonar.organization"] = "visible-organization"
    arguments = ["pysonar", "--verbose", "--project-key=visible-project"]
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("os.environ", {})
    if token_source == "cli":
        arguments.append(f"--token={credentials['sonar.token']}")
    elif token_source == "environment":
        monkeypatch.setenv("SONAR_TOKEN", credentials["sonar.token"])
    elif token_source == "json":
        environment_properties["sonar.token"] = credentials["sonar.token"]
    elif token_source == "properties":
        (tmp_path / "sonar-project.properties").write_text(f"sonar.token={credentials['sonar.token']}\n")
    else:
        (tmp_path / "pyproject.toml").write_text(f'[tool.sonar]\ntoken = "{credentials["sonar.token"]}"\n')
    # This lower-priority value must never appear in the early environment diagnostic.
    environment_properties.setdefault("sonar.token", "dummy-overridden-value")
    if token_source in ("properties", "toml"):
        environment_properties.pop("sonar.token")
    monkeypatch.setenv("SONAR_SCANNER_JSON_PARAMS", json.dumps(environment_properties))
    jvm_credential = "dummy jvm=value"
    arguments.append(
        f'--sonar-scanner-java-opts=-Xmx256m -Djavax.net.ssl.keyStorePassword="{jvm_credential}" '
        '-Dcustom.apiKey="dummy jvm api key"'
    )
    monkeypatch.setattr("sys.argv", arguments)
    # Capture configuration-loading diagnostics before --verbose takes effect.
    caplog.set_level("DEBUG")
    monkeypatch.setattr(main.cache, "get_cache", Mock())
    monkeypatch.setattr(main, "build_api", Mock())
    monkeypatch.setattr(main, "check_version", Mock())
    monkeypatch.setattr(main, "update_config_with_api_urls", Mock())
    engine = scannerengine.ScannerEngine(JREResolvedPath(pathlib.Path("java")), pathlib.Path("engine.jar"))
    monkeypatch.setattr(main, "create_scanner_engine", Mock(return_value=engine))
    process = Mock(stdout=[], stderr=[], returncode=0)
    popen = Mock(return_value=process)
    monkeypatch.setattr(scannerengine, "Popen", popen)

    assert main.scan() == 0

    output = "\n".join(caplog.messages)
    for value in [*credentials.values(), jvm_credential, "dummy-overridden-value", "dummy jvm api key"]:
        assert value not in output
        assert repr(value)[1:-1] not in output
        assert json.dumps(value)[1:-1] not in output
    assert "Final loaded configuration:" in output
    assert "visible-project" in output
    assert "-Xmx256m" in output
    assert "-Djavax.net.ssl.keyStorePassword=******" in output
    assert "-Dcustom.apiKey=******" in output
    environment_log = next(line for line in output.splitlines() if "Loaded environment properties:" in line)
    assert "'sonar.scanner.proxyPassword': '******'" in environment_log
    assert "'sonar.organization': 'visible-organization'" in environment_log
    engine_log = next(line for line in caplog.messages if line.startswith("Properties:"))
    logged_payload = json.loads(engine_log.removeprefix("Properties: "))
    logged_properties = {item["key"]: item["value"] for item in logged_payload["scannerProperties"]}
    assert logged_properties["sonar.projectKey"] == "visible-project"
    for key in credentials:
        assert logged_properties[key] == "******"
    payload = json.loads(process.stdin.write.call_args.args[0])
    properties = {item["key"]: item["value"] for item in payload["scannerProperties"]}
    for key, value in credentials.items():
        assert properties[key] == value
    assert f"-Djavax.net.ssl.keyStorePassword={jvm_credential}" in popen.call_args.args[0]
