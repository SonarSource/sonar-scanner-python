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
        self.scan_arguments = sys.argv[1:]
        self.scan_arguments.extend(self._read_toml_args())

    def _read_toml_args(self) -> list[str]:
        scan_arguments: list[str] = []
        try:
            parsed_data = self._read_toml_file()
            if ("tool" not in parsed_data) or ("sonar" not in parsed_data["tool"]):
                return scan_arguments
            sonar_properties = parsed_data["tool"]["sonar"]
            for key, value in sonar_properties.items():
                self._add_parameter_to_scanner_args(scan_arguments, key, value)
        except BaseException as e:
            print(e)
            raise e
        return scan_arguments

    def _add_parameter_to_scanner_args(self, scan_arguments: list[str], key: str, value: Union[str, dict]):
        if isinstance(value, str):
            scan_arguments.append(f"-Dsonar.{key}={value}")
        if isinstance(value, dict):
            for k, v in value.items():
                self._add_parameter_to_scanner_args(scan_arguments, f"{key}.{k}", v)

    def _read_toml_file(self) -> dict:
        toml_file_path = self._get_toml_file_path()
        if not os.path.isfile(toml_file_path):
            return {}
        with open(toml_file_path, "r") as file:
            # TODO: actually search for pyproject.toml
            toml_data = file.read()
            return toml.loads(toml_data)

    def _get_toml_file_path(self) -> str:
        args = self._get_arguments_dict()
        if "-Dtoml.path" in args:
            return args["-Dtoml.path"]
        elif "-Dproject.home" in args:
            return os.path.join(args["-Dproject.home"], "pyproject.toml")
        else:
            return os.path.join(os.curdir, "pyproject.toml")

    def _get_arguments_dict(self):
        args = self.scan_arguments
        arguments_dict = {}
        i = 0
        while i < len(args):
            current_arg = args[i]

            if "=" in current_arg:
                arg_parts = current_arg.split("=", 1)
                arguments_dict[arg_parts[0]] = arg_parts[1]
            else:
                if i + 1 < len(args) and "=" not in args[i + 1]:
                    arguments_dict[current_arg] = args[i + 1]
                    i += 1
                else:
                    arguments_dict[current_arg] = None

            i += 1
        return arguments_dict
