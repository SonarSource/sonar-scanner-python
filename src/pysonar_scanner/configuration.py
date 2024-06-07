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

import argparse
import os
import sys
from logging import Logger
from typing import Union

import toml

from pysonar_scanner.logger import ApplicationLogger


class Configuration:
    log: Logger
    sonar_scanner_executable_path: str
    sonar_scanner_path: str
    sonar_scanner_version: str
    scan_arguments: list[str]
    wrapper_arguments: argparse.Namespace

    def __init__(self):
        self.log = ApplicationLogger.get_logger()
        self.sonar_scanner_path = ".scanner"
        self.sonar_scanner_version = "6.0.0.4432"
        self.sonar_scanner_executable_path = ""
        self.scan_arguments = []
        self.wrapper_arguments = argparse.Namespace(debug=False, read_project_config=False)
        self.unknown_arguments = []

    def setup(self) -> None:
        """This is executed when run from the command line"""
        self._read_wrapper_arguments()
        ApplicationLogger.set_debug(self.is_debug())
        self.scan_arguments = self._read_toml_args()
        # The sonar-scanner-cli may crash with an error when receiving unexpected arguments
        # Therefore, arguments only expected by the sonar-scanner-python are filtered out.
        self._append_common_arguments()
        # If duplicate properties are provided, newer values will override older ones.
        # We therefore read CLI arguments last so that they have priority over toml configuration.
        self.scan_arguments.extend(self.unknown_arguments)

    def _append_common_arguments(self):
        if self.wrapper_arguments.debug:
            self.scan_arguments.append("-X")
        if self.wrapper_arguments.project_home is not None:
            self.scan_arguments.append(f"-Dproject.home={self.wrapper_arguments.project_home}")

    def _read_wrapper_arguments(self):
        argument_parser = argparse.ArgumentParser()
        argument_parser.add_argument("-toml.path", "-Dtoml.path", "--toml.path", dest="toml_path")
        argument_parser.add_argument("-project.home", "-Dproject.home", "--project.home", dest="project_home")
        argument_parser.add_argument("-X", action="store_true", dest="debug")
        argument_parser.add_argument(
            "-read.project.config",
            "-Dread.project.config",
            "--read-project-config",
            "-read-project-config",
            action="store_true",
            dest="read_project_config",
        )
        self.wrapper_arguments, self.unknown_arguments = argument_parser.parse_known_args(args=sys.argv[1:])

    def _read_toml_args(self) -> list[str]:
        scan_arguments: list[str] = []
        toml_data: dict = {}
        try:
            toml_data = self._read_toml_file()
        except OSError as e:
            self.log.exception("Error while opening .toml file: %s", str(e))
        if self.wrapper_arguments.read_project_config:
            common_toml_properties = self._extract_common_properties(toml_data)
            for key, value in common_toml_properties.items():
                self._add_parameter_to_scanner_args(scan_arguments, key, value)
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

    def _extract_common_properties(self, toml_properties):
        properties = {}
        if "tool" in toml_properties.keys() and "poetry" in toml_properties["tool"]:
            poetry_properties = toml_properties["tool"]["poetry"]
            properties = self._extract_from_poetry_properties(poetry_properties)
        return properties

    def _extract_from_poetry_properties(self, poetry_properties):
        result = {}
        if "name" in poetry_properties:
            result["project.name"] = poetry_properties["name"]
        if "version" in poetry_properties:
            result["projectVersion"] = poetry_properties["version"]
        # Note: Python version can be extracted from dependencies.python, however it
        # may be specified with constraints, e.g ">3.8", which is not currently supported by sonar-python
        return result

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
        if self.wrapper_arguments.toml_path is not None:
            return self.wrapper_arguments.toml_path
        elif self.wrapper_arguments.project_home is not None:
            return os.path.join(self.wrapper_arguments.project_home, "pyproject.toml")
        else:
            return os.path.join(os.curdir, "pyproject.toml")

    def is_debug(self) -> bool:
        return self.wrapper_arguments.debug
