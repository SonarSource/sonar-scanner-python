import unittest
from unittest.mock import patch, Mock
from py_sonar_scanner.configuration import Configuration


class TestConfiguration(unittest.TestCase):

    @patch('py_sonar_scanner.configuration.sys')
    def test_argument_parsing_empty_toml(self, mock_sys):

        configuration = Configuration()
        configuration._read_toml_args = Mock(return_value=[])

        mock_sys.argv = [
            "path/to/scanner/py-sonar-scanner",
            "-DSomeJVMArg"
        ]
        configuration.setup()
        self.assertListEqual(configuration.scan_arguments, ["-DSomeJVMArg"])

        mock_sys.argv = [
            "path/to/scanner/py-sonar-scanner",
            "-DSomeJVMArg",
            "-DAnotherJVMArg",
            "-dNotAJVMArg",
            "-SomeNonsense",
        ]
        configuration.setup()
        self.assertListEqual(configuration.scan_arguments, [
            "-DSomeJVMArg",
            "-DAnotherJVMArg",
            "-dNotAJVMArg",
            "-SomeNonsense"
        ])
