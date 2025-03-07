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
from pysonar_scanner.api import SonarQubeApi
from pysonar_scanner.cache import Cache, CacheFile
from pysonar_scanner.exceptions import SQTooOldException, ChecksumException


class ScannerEngine:
    def __init__(self, api: SonarQubeApi, cache: Cache):
        self.api = api
        self.cache = cache

    def __version_check(self):
        if self.api.is_sonar_qube_cloud():
            return
        version = self.api.get_analysis_version()
        if not version.does_support_bootstrapping():
            raise SQTooOldException(version)

    def __fetch_scanner_engine(self):
        def download_and_verify():
            cache_file = fetch_cache_file()
            if not cache_file.is_valid():
                download_scanner_engine(cache_file)
            return cache_file.is_valid()

        def fetch_cache_file():
            engine_info = self.api.get_analysis_engine()
            return self.cache.get_file(engine_info.filename, engine_info.sha256)

        def download_scanner_engine(cache_file: CacheFile):
            with cache_file.open() as f:
                self.api.download_analysis_engine(f)

        if download_and_verify():
            return
        if download_and_verify():
            return
        else:
            raise ChecksumException("Failed to download and verify scanner engine")
