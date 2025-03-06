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


def remove_trailing_slash(url: str) -> str:
    return url.rstrip("/ ").lstrip()


@dataclass(frozen=True)
class SQVersion:
    parts: list[str]

    def does_support_bootstrapping(self) -> bool:
        if len(self.parts) == 0:
            return False
        major_str = self.parts[0]
        minor_str = self.parts[1] if len(self.parts) > 1 else "0"
        if not major_str.isdigit() or not minor_str.isdigit():
            return False
        major = int(major_str)
        minor = int(minor_str)

        return major > 10 or (major == 10 and minor >= 6)

    def __str__(self) -> str:
        return ".".join(self.parts)

    @staticmethod
    def from_str(version: str) -> "SQVersion":
        return SQVersion(version.split("."))


MIN_SUPPORTED_SQ_VERSION: SQVersion = SQVersion.from_str("10.6")
