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
import pysonar_scanner.api as api
from pysonar_scanner.api import SonarQubeApi
from pysonar_scanner.cache import Cache, CacheFile
from pysonar_scanner.exceptions import ChecksumException, SQTooOldException
from pysonar_scanner.configuration import Configuration
from pysonar_scanner.jre import JREResolvedPath
from subprocess import Popen, PIPE


class ScannerEngineProvisioner:
    def __init__(self, api: SonarQubeApi, cache: Cache):
        self.api = api
        self.cache = cache

    def provision(self) -> None:
        if self.__download_and_verify():
            return
        # Retry once in case the checksum failed due to the scanner engine being updated between getting the checksum and downloading the jar
        if self.__download_and_verify():
            return
        else:
            raise ChecksumException("Failed to download and verify scanner engine")

    def __download_and_verify(self) -> bool:
        engine_info = self.api.get_analysis_engine()
        cache_file = self.cache.get_file(engine_info.filename, engine_info.sha256)
        if not cache_file.is_valid():
            self.__download_scanner_engine(cache_file)
        return cache_file.is_valid()

    def __download_scanner_engine(self, cache_file: CacheFile) -> None:
        with cache_file.open(mode="wb") as f:
            self.api.download_analysis_engine(f)


class ScannerEngine:
    def __init__(self, api: SonarQubeApi, cache: Cache):
        self.api = api
        self.cache = cache

    def version_check(self):
        if self.api.is_sonar_qube_cloud():
            return
        version = self.api.get_analysis_version()
        if not version.does_support_bootstrapping():
            raise SQTooOldException(
                f"Only SonarQube versions >= {api.MIN_SUPPORTED_SQ_VERSION} are supported, but got {version}"
            )

    def fetch_scanner_engine(self):
        ScannerEngineProvisioner(self.api, self.cache).provision()

    def run(self, jre_path: JREResolvedPath, configuration: Configuration):
        print(str(jre_path))
        popen = Popen(["/home/thomas.serre/Projects/sonar-scanner-python/sonar_cache/sonar_cache/OpenJDK17U-jre_x64_linux_hotspot_17.0.13_11.tar.gz_unzip/jdk-17.0.13+11-jre/bin/java", "-jar", "/home/thomas.serre/Projects/sonar-scanner-python/sonar_cache/scanner-enterprise-2025.1.1.104738-all.jar"], stdout=PIPE, stderr=PIPE, stdin=PIPE)
        outs, errs = popen.communicate(configuration.to_json().encode())

        exitcode = popen.wait() # 0 means success
        print(exitcode)
        print(outs)
        print(errs)
        
import logging
def log_subprocess_output(pipe):
    for line in iter(pipe.readline, b''): # b'\n'-separated lines
        logging.info('got line from subprocess: %r', line)