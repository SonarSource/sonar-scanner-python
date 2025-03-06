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
from dataclasses import dataclass
import pathlib

from pysonar_scanner.api import SonarQubeApi
from pysonar_scanner.cache import Cache
from pysonar_scanner.configuration import Configuration


@dataclass(frozen=True)
class JREResolvedPath:
    path: pathlib.Path

    @staticmethod
    def from_string(path: str) -> "JREResolvedPath":
        if not path:
            raise ValueError("JRE path cannot be empty")
        return JREResolvedPath(pathlib.Path(path))


class JREProvisioner:
    def __init__(self, api: SonarQubeApi, cache: Cache):
        self.api = api
        self.cache = cache

    def provision(self) -> JREResolvedPath:
        return JREResolvedPath("test")


class JREResolver:
    def __init__(self, configuration: Configuration, jre_provisioner: JREProvisioner):
        self.configuration = configuration
        self.jre_provisioner = jre_provisioner

    def resolve_jre(self):
        windows_exe_suffix = ".exe" if self.configuration.sonar.scanner.os == "windows" else ""
        if self.configuration.sonar.scanner.java_exe_path:
            return JREResolvedPath.from_string(self.configuration.sonar.scanner.java_exe_path)
        if not self.configuration.sonar.scanner.skip_jre_provisioning:
            return self.__provision_jre()
        java_path = pathlib.Path(f"java{exe_suffix}")
        return JREResolvedPath(java_path)

    def __provision_jre(self):
        return self.jre_provisioner.provision()
