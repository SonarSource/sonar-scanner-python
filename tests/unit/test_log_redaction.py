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


@pytest.mark.parametrize("token_source", ["cli", "environment", "json", "properties", "toml"])
def test_verbose_scan_masks_credentials_but_preserves_engine_input(token_source, monkeypatch, capsys, tmp_path):
    credentials = {
        "sonar.token": "dummy-auth-value",
        "sonar.login": "dummy-login-value",
        "sonar.password": "dummy-password-value",
        "sonar.scanner.proxyPassword": "dummy-proxy-value",
        "sonar.scanner.keystorePassword": 'dummy-key-\\value-"é',
        "sonar.scanner.truststorePassword": "dummy-trust-value",
        "custom.secret": "dummy-custom-value",
    }
    environment_properties = {key: value for key, value in credentials.items() if key != "sonar.token"}
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
    arguments.append(f'--sonar-scanner-java-opts=-Xmx256m -Djavax.net.ssl.keyStorePassword="{jvm_credential}"')
    monkeypatch.setattr("sys.argv", arguments)
    # Exercise an already-enabled logger, which exposes configuration-loading diagnostics.
    monkeypatch.setattr(logging.getLogger(), "handlers", [])
    monkeypatch.setattr(logging.getLogger(), "level", logging.DEBUG)
    monkeypatch.setattr(main.cache, "get_cache", Mock())
    monkeypatch.setattr(main, "build_api", Mock())
    monkeypatch.setattr(main, "check_version", Mock())
    monkeypatch.setattr(main, "update_config_with_api_urls", Mock())
    engine = scannerengine.ScannerEngine(JREResolvedPath(pathlib.Path("java")), pathlib.Path("engine.jar"))
    monkeypatch.setattr(main, "create_scanner_engine", Mock(return_value=engine))
    process = Mock()
    process.stdout = [
        json.dumps({"level": "INFO", "message": f"Engine echoed {credentials['sonar.token']}"}).encode(),
    ]
    process.stderr = [
        json.dumps(
            {
                "level": "ERROR",
                "message": f"Engine echoed {jvm_credential}",
                "stacktrace": f"Trace contains {credentials['sonar.scanner.keystorePassword']}",
            }
        ).encode(),
    ]
    process.returncode = 0
    popen = Mock(return_value=process)
    monkeypatch.setattr(scannerengine, "Popen", popen)

    assert main.scan() == 0

    captured = capsys.readouterr()
    output = captured.out + captured.err
    for value in [*credentials.values(), jvm_credential, "dummy-overridden-value"]:
        assert value not in output
        assert repr(value)[1:-1] not in output
        assert json.dumps(value)[1:-1] not in output
    assert "Final loaded configuration:" in output
    assert "visible-project" in output
    assert "-Xmx256m" in output
    assert "-Djavax.net.ssl.keyStorePassword=******" in output
    assert "Engine echoed ******" in captured.out
    assert "Engine echoed ******" in captured.err
    assert "Trace contains ******" in captured.err
    assert '"scannerProperties"' not in output
    payload = json.loads(process.stdin.write.call_args.args[0])
    properties = {item["key"]: item["value"] for item in payload["scannerProperties"]}
    for key, value in credentials.items():
        assert properties[key] == value
    assert f"-Djavax.net.ssl.keyStorePassword={jvm_credential}" in popen.call_args.args[0]
