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
from __future__ import annotations
import os
import sys
from typing import Union
import toml


class Configuration:
    sonar_scanner_executable_path: str
    sonar_scanner_path: str
    sonar_scanner_version: str
    scan_arguments: list[str]

    def __init__(self):
        self.sonar_scanner_path = ".scanner"
        self.sonar_scanner_version = "4.6.2.2472"
        self.sonar_scanner_executable_path = ""
        self.scan_arguments = []

    def setup(self) -> None:
        """This is executed when run from the command line"""

        scan_arguments = sys.argv[1:]
        scan_arguments.extend(self._read_toml_args())

        self.scan_arguments = scan_arguments

    def _read_toml_args(self) -> list[str]:
        scan_arguments: list[str] = []
        try:
            if os.path.isfile("pyproject.toml"):
                with open("pyproject.toml", "r") as file:
                    # TODO: actually search for pyproject.toml
                    toml_data = file.read()
                    parsed_data = toml.loads(toml_data)
                    print(parsed_data)
                    if "sonar" in parsed_data:
                        sonar_properties = parsed_data["sonar"]
                        for key, value in sonar_properties.items():
                            self._add_parameter_to_scanner_args(scan_arguments, key, value)
        except BaseException as e:
            print(e)
        return scan_arguments

    def _add_parameter_to_scanner_args(self, scan_arguments: list[str], key: str, value: Union[str, dict]):
        if isinstance(value, str):
            scan_arguments.append(f"-Dsonar.{key}={value}")
        if isinstance(value, dict):
            for k, v in value.items():
                self._add_parameter_to_scanner_args(scan_arguments, f"{key}.{k}", v)
