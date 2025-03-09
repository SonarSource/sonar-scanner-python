from typing import TypedDict
from pysonar_scanner.configuration import Configuration, Sonar, Scanner, Environment
from pysonar_scanner.jre.resolver import JREResolver as JRE
from pysonar_scanner.jre.resolved_path import JREResolvedPath
from unittest.mock import Mock
import unittest


class TestJREResolver(unittest.TestCase):
    def test_resolve_jre(self):
        class TestCaseDict(TypedDict):
            name: str
            config: Configuration
            expected: JREResolvedPath

        provisioner = Mock()
        provisioner_jre_path = JREResolvedPath("java")
        mock_function = {"provision.return_value": provisioner_jre_path}
        provisioner.configure_mock(**mock_function)

        cases: list[TestCaseDict] = [
            {
                "name": "if java exe path is set return it",
                "config": Configuration(Sonar(Scanner(java_exe_path="a/b"))),
                "expected": JREResolvedPath("a/b"),
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
                "name": "if skip_jre_provisioning is True and java_home is set",
                "config": Configuration(
                    Sonar(Scanner(skip_jre_provisioning=True)),
                    Environment(java_home="path/java"),
                ),
                "expected": JREResolvedPath("path/java/bin/java"),
            },
            {
                "name": "if skip_jre_provisioning is True and java_home is set for windows",
                "config": Configuration(
                    Sonar(Scanner(skip_jre_provisioning=True, os="windows")),
                    Environment(java_home="path/java"),
                ),
                "expected": JREResolvedPath("path/java/bin/java.exe"),
            },
            {
                "name": "if skip_jre_provisioning is True and java_home is not set return the default",
                "config": Configuration(Sonar(Scanner(skip_jre_provisioning=True))),
                "expected": JREResolvedPath("java"),
            },
            {
                "name": "if skip_jre_provisioning is True and java_home is not set return the default for windows",
                "config": Configuration(
                    Sonar(Scanner(os="windows", skip_jre_provisioning=True))
                ),
                "expected": JREResolvedPath("java.exe"),
            },
        ]

        for case in cases:
            expected = case["expected"]
            with self.subTest(case["name"], config=case["config"], expected=expected):
                actual = JRE(provisioner).resolve_jre(case["config"])
                self.assertEqual(actual, expected)
