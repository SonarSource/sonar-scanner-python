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
import json
import logging
import pathlib
import shlex
from dataclasses import dataclass
from subprocess import PIPE, Popen
from threading import Thread
from typing import IO, Any, Callable, Optional

from pysonar_scanner.api import EngineInfo, SonarQubeApi
from pysonar_scanner.cache import Cache, CacheFile
from pysonar_scanner.configuration.properties import (
    SONAR_SCANNER_JAVA_OPTS,
    SONAR_SCANNER_OPTS,
)
from pysonar_scanner.exceptions import ChecksumException
from pysonar_scanner.jre import JREResolvedPath


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
        logging.warning("Something went wrong while downloading the scanner engine. Retrying...")
        scanner_file = self.__download_and_verify()
        if scanner_file is not None:
            return scanner_file.filepath
        else:
            raise ChecksumException.create("scanner engine JAR")

    def __download_and_verify(self) -> Optional[CacheFile]:
        engine_info = self.api.get_analysis_engine()
        cache_file = self.cache.get_file(engine_info.filename, engine_info.sha256)
        if not cache_file.is_valid():
            logging.debug("No valid cached analysis engine jar was found")
            self.__download_scanner_engine(cache_file, engine_info)
        return cache_file if cache_file.is_valid() else None

    def __download_scanner_engine(self, cache_file: CacheFile, engine_info: EngineInfo) -> None:
        with cache_file.open(mode="wb") as f:
            if engine_info.download_url is not None:
                self.api.download_file_from_url(engine_info.download_url, f)
            else:
                self.api.download_analysis_engine(f)


class ScannerEngine:
    def __init__(self, jre_path: JREResolvedPath, scanner_engine_path: pathlib.Path):
        self.jre_path = jre_path
        self.scanner_engine_path = scanner_engine_path

    def run(self, config: dict[str, Any]):
        # Extract Java options if present; they must influence the JVM invocation, not the scanner engine itself
        java_opts = config.get(SONAR_SCANNER_JAVA_OPTS)
        java_opts = config.get(SONAR_SCANNER_OPTS) if not java_opts else java_opts

        cmd = self.__build_command(self.jre_path, self.scanner_engine_path, java_opts)
        logging.debug(f"Command: {cmd}")
        properties_str = self.__config_to_json(config)
        logging.debug(f"Properties: {properties_str}")
        return CmdExecutor(cmd, properties_str).execute()

    def __build_command(
        self,
        jre_path: JREResolvedPath,
        scanner_engine_path: pathlib.Path,
        java_opts: Optional[str] = None,
    ) -> list[str]:
        cmd: list[str] = []
        cmd.append(str(jre_path.path))

        if java_opts:
            cmd.extend(self.__decompose_java_opts(java_opts))

        cmd.append("-jar")
        cmd.append(str(scanner_engine_path))
        return cmd

    def __config_to_json(self, config: dict[str, Any]) -> str:
        # SONAR_SCANNER_JAVA_OPTS are properties that shouldn't be passed to the engine, only to the JVM
        scanner_properties = [
            {"key": k, "value": v}
            for k, v in config.items()
            if k != SONAR_SCANNER_JAVA_OPTS and k != SONAR_SCANNER_OPTS
        ]
        return json.dumps({"scannerProperties": scanner_properties})

    def __decompose_java_opts(self, java_opts: str) -> list[str]:
        return shlex.split(java_opts.strip())
