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
from logging import Logger

import toml

from py_sonar_scanner.logger import ApplicationLogger


class Configuration:
    sonar_scanner_executable_path: str
    sonar_scanner_path: str
    sonar_scanner_version: str
    scan_arguments: list[str]
    log: Logger

    def __init__(self):
        self.sonar_scanner_path = ".scanner"
        self.sonar_scanner_version = "4.6.2.2472"
        self.sonar_scanner_executable_path = ""
        self.scan_arguments = []
        self.log = ApplicationLogger.get_logger()

    def setup(self) -> None:
        """This is executed when run from the command line"""
        self.scan_arguments = sys.argv[1:]
        self.scan_arguments.extend(self._read_toml_args())

    def _read_toml_args(self) -> list[str]:
        scan_arguments: list[str] = []
        toml_data: dict = {}
        try:
            toml_data = self._read_toml_file()
        except OSError:
            self.log.error("Test error while opening file.")
        sonar_properties = self._extract_sonar_properties(toml_data)
        for key, value in sonar_properties.items():
            self._add_parameter_to_scanner_args(scan_arguments, key, value)
        return scan_arguments

    def _extract_sonar_properties(self, toml_properties):
        if "tool" not in toml_properties.keys():
            return {}
        tool_data = toml_properties["tool"]
        if not isinstance(tool_data, dict) or "sonar" not in tool_data.keys():
            return {}
        sonar_properties = tool_data["sonar"]
        return sonar_properties if isinstance(sonar_properties, dict) else {}

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
