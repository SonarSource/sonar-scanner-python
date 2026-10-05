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
import logging

import pytest

from pysonar_scanner import app_logging


def test_logging_output_destinations(capsys):
    logger = logging.getLogger()
    original_level = logger.level
    original_handlers = set(logger.handlers)
    try:
        app_logging.setup()
        app_logging.configure_logging_level(verbose=True)
        logging.info("hello world")
        logging.error("boom!")

        captured = capsys.readouterr()
        assert "INFO: hello world" in captured.out
        assert "ERROR: boom!" in captured.err
        assert len(captured.err.splitlines()) == 1
        assert len(captured.out.splitlines()) == 1
    finally:
        for handler in set(logger.handlers) - original_handlers:
            logger.removeHandler(handler)
        logger.setLevel(original_level)


@pytest.mark.parametrize(
    "key",
    [
        "sonar.token",
        "sonar.login",
        "sonar.password",
        "sonar.scanner.proxyPassword",
        "sonar.scanner.keystorePassword",
        "sonar.scanner.truststorePassword",
        "custom.apiToken",
        "custom.apiKey",
        "custom.api_key",
        "custom.access-key",
        "custom.credential",
        "custom.authorization",
        "custom.secret",
        "custom.secured",
        "sonar.scanner.javaOpts",
        "sonar.scanner.opts",
    ],
)
def test_redacts_sensitive_properties_without_mutating_them(key):
    config = {key: "dummy-value", "sonar.projectKey": "my-project", "sonar.cpd.py.minimumTokens": 100}
    assert app_logging.redact_properties(config) == {
        key: app_logging.REDACTED,
        "sonar.projectKey": "my-project",
        "sonar.cpd.py.minimumTokens": 100,
    }
    assert config[key] == "dummy-value"


def test_redacts_sensitive_jvm_arguments_without_mutating_them():
    command = [
        "java",
        "-Xmx256m",
        "-Djavax.net.ssl.keyStorePassword=dummy=value",
        "-Dcustom.apiKey=dummy-key",
        "-Dcustom.credential=dummy-credential",
        "-Dordinary=value",
        "-jar",
        "engine.jar",
    ]
    assert app_logging.redact_command(command) == [
        "java",
        "-Xmx256m",
        "-Djavax.net.ssl.keyStorePassword=******",
        "-Dcustom.apiKey=******",
        "-Dcustom.credential=******",
        "-Dordinary=value",
        "-jar",
        "engine.jar",
    ]
    assert command[2] == "-Djavax.net.ssl.keyStorePassword=dummy=value"
