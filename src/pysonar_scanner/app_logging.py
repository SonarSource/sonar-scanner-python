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
import re
import shlex
import sys
from typing import Any

from pysonar_scanner.configuration.properties import SONAR_SCANNER_JAVA_OPTS, SONAR_SCANNER_OPTS

REDACTED = "******"
_JAVA_OPTIONS = (SONAR_SCANNER_JAVA_OPTS, SONAR_SCANNER_OPTS)


def _is_sensitive(key: str) -> bool:
    key = key.lower()
    return "password" in key or "secret" in key or key.endswith(("token", ".login", ".secured"))


def redact_properties(config: dict[str, Any]) -> dict[str, Any]:
    # JVM options can contain arbitrary credentials; the command diagnostic shows safe arguments separately.
    return {key: REDACTED if _is_sensitive(key) or key in _JAVA_OPTIONS else value for key, value in config.items()}


def redact_command(command: list[str]) -> list[str]:
    result = []
    for argument in command:
        key, separator, _ = argument.partition("=")
        result.append(
            f"{key}={REDACTED}" if separator and key.startswith("-D") and _is_sensitive(key[2:]) else argument
        )
    return result


class RedactingFormatter(logging.Formatter):
    def __init__(self) -> None:
        super().__init__("%(levelname)s: %(message)s")
        self._pattern: re.Pattern[str] | None = None

    def configure(self, config: dict[str, Any]) -> None:
        values = [str(value) for key, value in config.items() if _is_sensitive(key) and value is not None]
        for key in _JAVA_OPTIONS:
            try:
                arguments = shlex.split(config.get(key) or "")
            except ValueError:
                # Invalid JVM options are rejected when building the command, without echoing their value.
                continue
            for argument in arguments:
                name, separator, value = argument.partition("=")
                if separator and name.startswith("-D") and _is_sensitive(name[2:]):
                    values.append(value)

        # Diagnostics may contain plain text, Python repr or JSON-escaped credentials.
        variants = {
            variant
            for value in values
            if value
            for variant in (
                value,
                repr(value)[1:-1],
                json.dumps(value)[1:-1],
                json.dumps(value, ensure_ascii=False)[1:-1],
            )
        }
        self._pattern = (
            re.compile("|".join(re.escape(value) for value in sorted(variants, key=len, reverse=True)))
            if variants
            else None
        )

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        # Redact after formatting so exception tracebacks and messages from dependencies are covered too.
        return self._pattern.sub(REDACTED, message) if self._pattern else message


def configure_redaction(config: dict[str, Any]) -> None:
    for handler in logging.getLogger().handlers:
        if isinstance(handler.formatter, RedactingFormatter):
            handler.formatter.configure(config)


class LevelFilter(logging.Filter):
    def __init__(self, level):
        super().__init__()
        self.__level = level

    def filter(self, record):
        return record.levelno < self.__level


def setup() -> None:
    logger = logging.getLogger()

    non_error_handler = logging.StreamHandler(sys.stdout)
    non_error_handler.setLevel(logging.DEBUG)
    non_error_handler.addFilter(LevelFilter(logging.ERROR))

    error_handler = logging.StreamHandler(sys.stderr)
    error_handler.setLevel(logging.ERROR)

    formatter = RedactingFormatter()
    non_error_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)

    logger.addHandler(non_error_handler)
    logger.addHandler(error_handler)


def configure_logging_level(verbose: bool) -> None:
    logging.getLogger().setLevel(logging.DEBUG if verbose else logging.INFO)
