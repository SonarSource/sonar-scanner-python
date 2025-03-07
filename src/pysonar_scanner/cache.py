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
import typing
import pathlib
from pysonar_scanner import utils


@dataclass(frozen=True)
class CacheFile:
    filepath: pathlib.Path
    checksum: str

    def is_valid(self) -> bool:
        try:
            with open(self.filepath, "rb") as f:
                calculated_checksum = utils.calculate_checksum(f)

            return calculated_checksum == self.checksum
        except (FileNotFoundError, PermissionError, OSError):
            return False

    def open(self) -> typing.BinaryIO:
        return open(self.filepath, mode="rb")


class Cache:
    def __init__(self, cache_folder: pathlib.Path):
        self.cache_folder = cache_folder

    def get_file(self, filename: str, checksum: str) -> CacheFile:
        path = self.cache_folder / filename
        return CacheFile(path, checksum)


def get_default() -> Cache:
    return Cache(pathlib.Path.home() / ".sonar-scanner")
