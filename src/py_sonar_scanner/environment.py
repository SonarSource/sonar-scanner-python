#
# Sonar Scanner Python
# Copyright (C) 2011-2023 SonarSource SA.
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
import os
import platform
import shutil
import urllib.request
import zipfile

from py_sonar_scanner.configuration import Configuration
from py_sonar_scanner.scanner import Scanner

systems = {
    'Darwin': 'macosx',
    'Windows': 'windows'
}


class Environment:
    cfg: Configuration

    def __init__(self, cfg: Configuration):
        self.cfg = cfg

    def setup(self):
        self.cleanup()
        if self._is_sonar_scanner_on_path():
            self.cfg.sonar_scanner_executable_path = 'sonar-scanner'
        else:
            system_name = systems.get(platform.uname().system, 'linux')
            self._install_scanner(system_name)
            sonar_scanner_home = os.path.join(self.cfg.sonar_scanner_path,
                                              f'sonar-scanner-{self.cfg.sonar_scanner_version}-{system_name}')
            self.cfg.sonar_scanner_executable_path = os.path.join(sonar_scanner_home, 'bin', 'sonar-scanner')

        print(self.cfg.sonar_scanner_executable_path)

    def _install_scanner(self, system_name: str):
        os.mkdir(self.cfg.sonar_scanner_path)
        # Download the binaries and unzip them
        # https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-${version}-${os}.zip
        scanner_res = urllib.request.urlopen(
            f'https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-{self.cfg.sonar_scanner_version}-{system_name}.zip')
        scanner_zip_path = os.path.join(self.cfg.sonar_scanner_path, 'scanner.zip')
        with open(scanner_zip_path, 'wb') as output:
            output.write(scanner_res.read())
        with zipfile.ZipFile(scanner_zip_path, "r") as zip_ref:
            zip_ref.extractall(self.cfg.sonar_scanner_path)
        os.remove(scanner_zip_path)
        self._change_permissions_recursive(self.cfg.sonar_scanner_path, 0o777)

    def _is_sonar_scanner_on_path(self) -> bool:
        return shutil.which('sonar-scanner') is not None

    def cleanup(self):
        if os.path.exists(self.cfg.sonar_scanner_path):
            shutil.rmtree(self.cfg.sonar_scanner_path)

    def _change_permissions_recursive(self, path, mode):
        for root, dirs, files in os.walk(path, topdown=False):
            for dir in [os.path.join(root, d) for d in dirs]:
                os.chmod(dir, mode)
            for file in [os.path.join(root, f) for f in files]:
                os.chmod(file, mode)

    def scanner(self) -> Scanner:
        return Scanner(self.cfg)
