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
from __future__ import annotations
import os
import platform
import pyfiglet
import shutil
import urllib.request
from urllib.error import HTTPError

from pysonar_scanner.logger import ApplicationLogger
from pysonar_scanner.configuration import Configuration
from pysonar_scanner.utils.binaries_utils import write_binaries, unzip_binaries
from pysonar_scanner.scanner import Scanner

systems = {"Darwin": "macosx", "Windows": "windows"}


class Environment:
    cfg: Configuration

    # a full download path for a scanner has the following shape:
    # https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-${version}-${os}.zip
    scanner_base_url: str = "https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli"

    def __init__(self, cfg: Configuration):
        self.cfg = cfg
        self.log = ApplicationLogger.get_logger()

    def scan(self):
        try:
            self.setup()
            self.scanner().scan()
        finally:
            self.cleanup()

    def setup(self):
        self.cleanup()
        if self._is_sonar_scanner_on_path():
            self.cfg.sonar_scanner_executable_path = "sonar-scanner"
        else:
            system_name = systems.get(platform.uname().system, "linux")
            self._install_scanner(system_name)
            sonar_scanner_home = os.path.join(
                self.cfg.sonar_scanner_path,
                f"sonar-scanner-{self.cfg.sonar_scanner_version}-{system_name}",
            )
            self.cfg.sonar_scanner_executable_path = os.path.join(sonar_scanner_home, "bin", "sonar-scanner")

        ascii_banner = pyfiglet.figlet_format("Sonar Scanner")
        self.log.info(ascii_banner)

    def scanner(self) -> Scanner:
        return Scanner(self.cfg)

    def _is_sonar_scanner_on_path(self) -> bool:
        return shutil.which("sonar-scanner") is not None

    def cleanup(self):
        if os.path.exists(self.cfg.sonar_scanner_path):
            shutil.rmtree(self.cfg.sonar_scanner_path)

    def _install_scanner(self, system_name: str):
        os.mkdir(self.cfg.sonar_scanner_path)
        # Download the binaries and unzip them
        scanner_zip_path = self._download_scanner_binaries(
            self.cfg.sonar_scanner_path, self.cfg.sonar_scanner_version, system_name
        )
        unzip_binaries(scanner_zip_path, self.cfg.sonar_scanner_path)
        os.remove(scanner_zip_path)
        self._change_permissions_recursive(self.cfg.sonar_scanner_path, 0o777)

    def _change_permissions_recursive(self, path, mode):
        for root, dirs, files in os.walk(path, topdown=False):
            for dir in [os.path.join(root, d) for d in dirs]:
                os.chmod(dir, mode)
            for file in [os.path.join(root, f) for f in files]:
                os.chmod(file, mode)

    def _download_scanner_binaries(self, destination: str, scanner_version: str, system_name: str) -> str:
        try:
            scanner_res = urllib.request.urlopen(f"{self.scanner_base_url}-{scanner_version}-{system_name}.zip")
            scanner_zip_path = os.path.join(destination, "scanner.zip")
            write_binaries(scanner_res, scanner_zip_path)
            return scanner_zip_path
        except HTTPError as error:
            self.log.error(f"ERROR: could not download scanner binaries - {error.code} - {error.msg}")
            raise error
