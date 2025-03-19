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
import pathlib
from typing import Optional

import pysonar_scanner.api as api

from pysonar_scanner.api import SonarQubeApi
from pysonar_scanner.cache import Cache, CacheFile
from pysonar_scanner.exceptions import ChecksumException, SQTooOldException
from pysonar_scanner.configuration import Configuration
from pysonar_scanner.jre import JREProvisioner, JREResolvedPath, JREResolver
from subprocess import Popen, PIPE


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

    def run(self, configuration: Configuration):
        self.__version_check()
        jre_path = self.__resolve_jre(configuration)
        scanner_engine_path = self.__fetch_scanner_engine()
        cmd = self.__build_command(jre_path, scanner_engine_path)
        return self.__execute_scanner_engine(configuration, cmd)

    def __build_command(self, jre_path: JREResolvedPath, scanner_engine_path: pathlib.Path) -> list[str]:
        cmd = []
        cmd.append(jre_path.path)
        cmd.append("-jar")
        cmd.append(scanner_engine_path)
        return cmd

    def __execute_scanner_engine(self, configuration: Configuration, cmd: list[str]) -> int:
        popen = Popen(cmd, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        outs, _ = popen.communicate(configuration.to_json().encode())
        exitcode = popen.wait()  # 0 means success
        if exitcode != 0:
            errors = self.__extract_errors_from_log(outs)
            raise RuntimeError(f"Scan failed with exit code {exitcode}", errors)
        return exitcode

    def __extract_errors_from_log(self, outs: str) -> list[str]:
        try:
            errors = []
            for line in outs.decode("utf-8").split("\n"):
                if line.strip() == "":
                    continue
                out_json = json.loads(line)
                if out_json["level"] == "ERROR":
                    errors.append(out_json["message"])
            return errors
        except Exception as e:
            print(e)
            return []

    def __version_check(self):
        if self.api.is_sonar_qube_cloud():
            return
        version = self.api.get_analysis_version()
        if not version.does_support_bootstrapping():
            raise SQTooOldException(
                f"Only SonarQube versions >= {api.MIN_SUPPORTED_SQ_VERSION} are supported, but got {version}"
            )

    def __resolve_jre(self, configuration: Configuration) -> JREResolvedPath:
        jre_provisionner = JREProvisioner(self.api, self.cache)
        jre_resolver = JREResolver(configuration, jre_provisionner)
        return jre_resolver.resolve_jre()
