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
import unittest
from unittest.mock import patch

import pytest

from pysonar_scanner import app_logging


class TestAppLogging(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def set_capsys(self, capsys):
        self.capsys = capsys

    def setUp(self) -> None:
        logger = logging.getLogger()
        handlers = patch.object(logger, "handlers", [])
        handlers.start()
        self.addCleanup(handlers.stop)
        level = logger.level
        self.addCleanup(logger.setLevel, level)
        app_logging.setup()
        app_logging.configure_logging_level(verbose=True)

    def test_logging_output_destinations(self):
        logging.info("hello world")
        logging.error("boom!")

        captured = self.capsys.readouterr()
        self.assertIn("INFO: hello world", captured.out)
        self.assertIn("ERROR: boom!", captured.err)
        self.assertEqual(len(captured.err.splitlines()), 1)
        self.assertEqual(len(captured.out.splitlines()), 1)

    def test_redacts_formatted_messages_and_tracebacks_on_both_streams(self):
        credential = 'dummy-"quoted"-\\value-é'
        app_logging.configure_redaction({"sonar.token": credential})
        logging.debug("Configuration: %r", {"sonar.token": credential})
        logging.getLogger("dependency").warning("JSON: %s", json.dumps({"value": credential}))
        try:
            raise ValueError(f"Rejected {credential}")
        except ValueError:
            logging.exception("Failed with %s", credential)

        captured = self.capsys.readouterr()
        for output in (captured.out, captured.err):
            self.assertNotIn(credential, output)
            self.assertNotIn(repr(credential)[1:-1], output)
            self.assertNotIn(json.dumps(credential)[1:-1], output)
            self.assertIn(app_logging.REDACTED, output)
        self.assertIn("ValueError: Rejected ******", captured.err)

    def test_redacts_overlapping_and_short_values_without_replacing_the_mask(self):
        app_logging.configure_redaction(
            {"sonar.token": "prefix-long", "sonar.password": "prefix", "custom.secret": "*"}
        )
        logging.info("prefix-long prefix *")
        self.assertEqual(self.capsys.readouterr().out, "INFO: ****** ****** ******\n")

    def test_reconfiguring_does_not_keep_previous_values_or_mask_empty_values(self):
        app_logging.configure_redaction({"sonar.token": "previous-value"})
        app_logging.configure_redaction({"sonar.token": "", "sonar.password": None})
        logging.info("previous-value is ordinary text now")
        self.assertEqual(self.capsys.readouterr().out, "INFO: previous-value is ordinary text now\n")

    def test_redacts_credentials_from_both_jvm_option_properties(self):
        config = {
            "sonar.scanner.javaOpts": '-Xmx256m -Djavax.net.ssl.keyStorePassword="dummy value=one"',
            "sonar.scanner.opts": "-Dsonar.login=dummy-deprecated",
        }
        app_logging.configure_redaction(config)
        logging.error("JVM echoed dummy value=one and dummy-deprecated")
        self.assertEqual(self.capsys.readouterr().err, "ERROR: JVM echoed ****** and ******\n")

    def test_invalid_jvm_options_do_not_break_redaction_setup(self):
        app_logging.configure_redaction({"sonar.token": "dummy-value", "sonar.scanner.javaOpts": 'unclosed "'})
        logging.error("dummy-value")
        self.assertEqual(self.capsys.readouterr().err, "ERROR: ******\n")


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
        "custom.secret",
        "custom.secured",
    ],
)
def test_redacts_sensitive_properties_and_jvm_arguments_without_mutating_them(key):
    config = {key: "dummy-value", "sonar.projectKey": "my-project", "sonar.cpd.py.minimumTokens": 100}
    assert app_logging.redact_properties(config) == {
        key: app_logging.REDACTED,
        "sonar.projectKey": "my-project",
        "sonar.cpd.py.minimumTokens": 100,
    }
    assert config[key] == "dummy-value"
    command = ["java", "-Xmx256m", f"-D{key}=dummy=value", "-Dordinary=value", "-jar", "engine.jar"]
    assert app_logging.redact_command(command) == [
        "java",
        "-Xmx256m",
        f"-D{key}=******",
        "-Dordinary=value",
        "-jar",
        "engine.jar",
    ]
    assert command[2] == f"-D{key}=dummy=value"
