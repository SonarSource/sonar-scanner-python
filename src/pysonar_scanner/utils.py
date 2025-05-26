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
import hashlib
import pathlib
import platform
import sys
import tarfile
import typing
from enum import Enum

OsStr = typing.Literal["windows", "linux", "mac", "alpine", "other"]
ArchStr = typing.Literal["x64", "aarch64", "other"]


def remove_trailing_slash(url: str) -> str:
    return url.rstrip("/ ").lstrip()


def calculate_checksum(filehandle: typing.BinaryIO) -> str:
    sha256_hash = hashlib.sha256()
    for byte_block in iter(lambda: filehandle.read(4096), b""):
        sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


class Os(Enum):
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "mac"
    ALPINE = "alpine"
    OTHER = "other"


def get_os() -> Os:
    def is_alpine() -> bool:
        try:
            os_release = pathlib.Path("/etc/os-release")
            if not os_release.exists():
                os_release = pathlib.Path("/usr/lib/os-release")
            if not os_release.exists():
                return False
            os_release_str = os_release.read_text()
            return "ID=alpine" in os_release_str or 'ID="alpine"' in os_release_str
        except OSError:
            return False

    os_name = platform.system()
    if os_name == "Windows":
        return Os.WINDOWS
    elif os_name == "Darwin":
        return Os.MACOS
    elif os_name == "Linux":
        if is_alpine():
            return Os.ALPINE
        else:
            return Os.LINUX
    return Os.OTHER


class Arch(Enum):
    X64 = "x64"
    AARCH64 = "aarch64"
    OTHER = "other"


def get_arch() -> Arch:
    machine = platform.machine().lower()
    if machine in ["amd64", "x86_64"]:
        return Arch.X64
    elif machine == "arm64":
        return Arch.AARCH64
    return Arch.OTHER


def filter_none_values(dictionary: dict) -> dict:
    return {k: v for k, v in dictionary.items() if v is not None}


def extract_tar(path: pathlib.Path, target_dir: pathlib.Path):
    with tarfile.open(path, "r:gz") as tar_ref:
        if sys.version_info >= (3, 12):
            tar_ref.extractall(target_dir, filter="data")
        else:
            tar_ref.extractall(target_dir)
