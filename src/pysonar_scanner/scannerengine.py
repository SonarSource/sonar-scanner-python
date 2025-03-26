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
from enum import Enum
import json
import logging
from operator import le
import pathlib
from threading import Thread
from typing import IO, Callable, Optional

from dataclasses import dataclass

import pysonar_scanner.api as api

from pysonar_scanner.api import SonarQubeApi
from pysonar_scanner.cache import Cache, CacheFile
from pysonar_scanner.configuration.properties import SONAR_SCANNER_OS, SONAR_SCANNER_ARCH
from pysonar_scanner.exceptions import ChecksumException, SQTooOldException
from pysonar_scanner.jre import JREProvisioner, JREResolvedPath, JREResolver, JREResolverConfiguration
from subprocess import Popen, PIPE


@dataclass(frozen=True)
class LogLine:
    level: str
    message: str
    stacktrace: Optional[str] = None

    def get_logging_level(self) -> int:
        if self.level == "ERROR":
            return logging.ERROR
        if self.level == "WARN":
            return logging.WARNING
        if self.level == "INFO":
            return logging.INFO
        if self.level == "DEBUG":
            return logging.DEBUG
        if self.level == "TRACE":
            return logging.DEBUG
        return logging.INFO


def parse_log_line(line: str) -> LogLine:
    try:
        line_json = json.loads(line)
        level = line_json.get("level", "INFO")
        message = line_json.get("message", line)
        stacktrace = line_json.get("stacktrace")
        return LogLine(level=level, message=message, stacktrace=stacktrace)
    except json.JSONDecodeError:
        return LogLine(level="INFO", message=line, stacktrace=None)


def default_log_line_listener(log_line: LogLine):
    logging.log(log_line.get_logging_level(), log_line.message)
    if log_line.stacktrace is not None:
        logging.log(log_line.get_logging_level(), log_line.stacktrace)


class CmdExecutor:
    def __init__(
        self,
        cmd: list[str],
        properties_str: str,
        log_line_listener: Callable[[LogLine], None] = default_log_line_listener,
    ):
        self.cmd = cmd
        self.properties_str = properties_str
        self.log_line_listener = log_line_listener

    def execute(self):
        process = Popen(self.cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        process.stdin.write(self.properties_str.encode())
        process.stdin.close()

        output_thread = Thread(target=self.__log_output, args=(process.stdout,))
        error_thread = Thread(target=self.__log_output, args=(process.stderr,))

        return self.__process_output(output_thread, error_thread, process)

    def __log_output(self, stream: IO[bytes]):
        for line in stream:
            decoded_line = line.decode("utf-8").rstrip()
            log_line = parse_log_line(decoded_line)
            self.log_line_listener(log_line)

    def __process_output(self, output_thread: Thread, error_thread: Thread, process: Popen) -> int:
        output_thread.start()
        error_thread.start()
        process.wait()
        output_thread.join()
        error_thread.join()

        return process.returncode


class ScannerEngineProvisioner:
    def __init__(self, api: SonarQubeApi, cache: Cache):
        self.api = api
        self.cache = cache

    def provision(self) -> pathlib.Path:
        scanner_file = self.__download_and_verify()
        if scanner_file is not None:
            return scanner_file.filepath
        # Retry once in case the checksum failed due to the scanner engine being updated between getting the checksum and downloading the jar
        scanner_file = self.__download_and_verify()
        if scanner_file is not None:
            return scanner_file.filepath
        else:
            raise ChecksumException("Failed to download and verify scanner engine")

    def __download_and_verify(self) -> Optional[CacheFile]:
        engine_info = self.api.get_analysis_engine()
        cache_file = self.cache.get_file(engine_info.filename, engine_info.sha256)
        if not cache_file.is_valid():
            self.__download_scanner_engine(cache_file)
        return cache_file if cache_file.is_valid() else None

    def __download_scanner_engine(self, cache_file: CacheFile) -> None:
        with cache_file.open(mode="wb") as f:
            self.api.download_analysis_engine(f)


class ScannerEngine:
    def __init__(self, api: SonarQubeApi, cache: Cache):
        self.api = api
        self.cache = cache

    def __fetch_scanner_engine(self) -> pathlib.Path:
        return ScannerEngineProvisioner(self.api, self.cache).provision()

    def run(self, config: dict[str, any]):
        self.__version_check()
        jre_path = self.__resolve_jre(config)
        scanner_engine_path = self.__fetch_scanner_engine()
        cmd = self.__build_command(jre_path, scanner_engine_path)
        properties_str = self.__config_to_json(config)
        return CmdExecutor(cmd, properties_str).execute()

    def __build_command(self, jre_path: JREResolvedPath, scanner_engine_path: pathlib.Path) -> list[str]:
        cmd = []
        cmd.append(jre_path.path)
        cmd.append("-jar")
        cmd.append(scanner_engine_path)
        return cmd

    def __config_to_json(self, config: dict[str, any]) -> str:
        scanner_properties = [{"key": k, "value": v} for k, v in config.items()]
        return json.dumps({"scannerProperties": scanner_properties})

    def __version_check(self):
        if self.api.is_sonar_qube_cloud():
            return
        version = self.api.get_analysis_version()
        if not version.does_support_bootstrapping():
            raise SQTooOldException(
                f"Only SonarQube versions >= {api.MIN_SUPPORTED_SQ_VERSION} are supported, but got {version}"
            )

    def __resolve_jre(self, config: dict[str, any]) -> JREResolvedPath:
        jre_provisionner = JREProvisioner(self.api, self.cache, config[SONAR_SCANNER_OS], config[SONAR_SCANNER_ARCH])
        jre_resolver = JREResolver(JREResolverConfiguration.from_dict(config), jre_provisionner)
        return jre_resolver.resolve_jre()
