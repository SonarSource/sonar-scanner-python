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
import pathlib
from unittest.mock import Mock
from typing_extensions import TypedDict
import unittest

from pysonar_scanner import cache, utils
from pysonar_scanner.api import JRE
from pysonar_scanner.configuration import Configuration, Scanner, Sonar
from pysonar_scanner.exceptions import ChecksumException, NoJreAvailableException, UnsupportedArchiveFormat
from pysonar_scanner.jre import JREProvisioner, JREResolvedPath, JREResolver
from tests import sq_api_utils

import zipfile


class TestJREProvisioner(unittest.TestCase):

    def test_resolve(self):
        pass


class TestJREResolvedPath(unittest.TestCase):
    def test_empty_path(self):
        with self.assertRaises(ValueError):
            JREResolvedPath.from_string("")

    def test_any_path(self):
        path = pathlib.Path("test")
        resolved_path = JREResolvedPath(path)
        self.assertEqual(resolved_path.path, path)


class TestJREResolver(unittest.TestCase):
    def test_resolve_jre(self):
        class TestCaseDict(TypedDict):
            name: str
            config: Configuration
            expected: JREResolvedPath

        provisioner = Mock()
        provisioner_jre_path = JREResolvedPath.from_string("java")
        mock_function = {"provision.return_value": provisioner_jre_path}
        provisioner.configure_mock(**mock_function)

        cases: list[TestCaseDict] = [
            {
                "name": "if java exe path is set return it",
                "config": Configuration(Sonar(Scanner(java_exe_path="a/b"))),
                "expected": JREResolvedPath.from_string("a/b"),
            },
            # Default value of skip_jre_provisioning is False
            {
                "name": "if java_exe_path is not set provision jre",
                "config": Configuration(Sonar(Scanner(java_exe_path=None))),
                "expected": provisioner_jre_path,
            },
            {
                "name": "if java_exe_path is an empty string provision jre",
                "config": Configuration(Sonar(Scanner(java_exe_path=""))),
                "expected": provisioner_jre_path,
            },
            {
                "name": "if skip_jre_provisioning is false provision jre",
                "config": Configuration(Sonar(Scanner(skip_jre_provisioning=False))),
                "expected": provisioner_jre_path,
            },
            {
                "name": "if skip_jre_provisioning is True and java_home is not set return the default",
                "config": Configuration(Sonar(Scanner(skip_jre_provisioning=True))),
                "expected": JREResolvedPath.from_string("java"),
            },
            {
                "name": "if skip_jre_provisioning is True and java_home is not set return the default for windows",
                "config": Configuration(Sonar(Scanner(os="windows", skip_jre_provisioning=True))),
                "expected": JREResolvedPath.from_string("java.exe"),
            },
        ]

        for case in cases:
            expected = case["expected"]
            with self.subTest(case["name"], config=case["config"], expected=expected):
                actual = JREResolver(case["config"], provisioner).resolve_jre()
                self.assertEqual(actual, expected)
