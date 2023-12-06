import unittest
from unittest.mock import Mock
import threading
from py_sonar_scanner.scanner import Scanner
from py_sonar_scanner.configuration import Configuration


class TestScanner(unittest.TestCase):

    def test_scanner_compute_command(self):
        cfg = Configuration()
        cfg.sonar_scanner_executable_path = "test"
        cfg.scan_arguments = ["a", "b"]
        scanner = Scanner(cfg)

        assert scanner.compute_command() == ["test", "a", "b"]

        cfg.sonar_scanner_executable_path = "test"
        cfg.scan_arguments = []
        scanner = Scanner(cfg)

        assert scanner.compute_command() == ["test"]

        cfg.sonar_scanner_executable_path = ""
        cfg.scan_arguments = []
        scanner = Scanner(cfg)

        self.assertRaises(ValueError, scanner.compute_command)

    def test_process_output(self):
        scanner = Scanner(Configuration())
        output_thread = threading.Thread()
        error_thread = threading.Thread()

        process = Mock()
        output_thread.start = Mock()
        error_thread.start = Mock()
        output_thread.join = Mock()
        error_thread.join = Mock()
        process.wait = Mock()

        return_code = scanner.process_output(output_thread, error_thread, process)

        output_thread.start.assert_called_once()
        error_thread.start.assert_called_once()
        output_thread.join.assert_called_once()
        error_thread.join.assert_called_once()
        process.wait.assert_called_once()

    def test_scan(self):
        scanner = Scanner(Configuration())

        scanner.execute_command = Mock()
        scanner.process_output = Mock()

        scanner.scan()

        scanner.execute_command.assert_called_once()
        scanner.process_output.assert_called_once()
