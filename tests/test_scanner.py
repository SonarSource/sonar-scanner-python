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
import unittest
from unittest.mock import Mock, patch, call
import threading
from py_sonar_scanner.scanner import Scanner
from py_sonar_scanner.configuration import Configuration


class TestScanner(unittest.TestCase):
    def test_scanner_compute_command(self):
        cfg = Configuration()
        cfg.sonar_scanner_executable_path = "test"
        cfg.scan_arguments = ["a", "b"]
        scanner = Scanner(cfg)

        self.assertEqual(scanner.compute_command(), ["test", "a", "b"])

        cfg.sonar_scanner_executable_path = "test"
        cfg.scan_arguments = []
        scanner = Scanner(cfg)

        self.assertEqual(scanner.compute_command(), ["test"])

        cfg.sonar_scanner_executable_path = ""
        cfg.scan_arguments = []
        scanner = Scanner(cfg)

        self.assertRaises(ValueError, scanner.compute_command)

    def test_process_output(self):
        scanner = Scanner(Configuration())
        output_thread = threading.Thread()
        error_thread = threading.Thread()
        success_code = 0
        process = Mock(returncode = success_code)
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
        self.assertEqual(return_code, success_code)
    
    @patch("py_sonar_scanner.scanner.Thread")
    def test_scan(self, mock_thread):
        scanner = Scanner(Configuration())
        process = Mock()
        scanner.execute_command = Mock(return_value=process)
        scanner.process_output = Mock()

        scanner.scan()

        scanner.execute_command.assert_called_once()
        call_thread_stdout = call(target=scanner._log_output, args=(process.stdout,))
        call_thread_stderr = call(target=scanner._log_output, args=(process.stderr,))
        mock_thread.assert_has_calls([call_thread_stdout, call_thread_stderr])
        self.assertEqual(mock_thread.call_count, 2)
        scanner.process_output.assert_called_once()

    @patch("py_sonar_scanner.scanner.Popen")
    def test_execute_command(self, mock_popen):
        from subprocess import PIPE
        scanner = Scanner(Configuration())
        command = "test"
        scanner.compute_command = Mock(return_value=command)
        
        scanner.execute_command()

        scanner.compute_command.assert_called_once()
        mock_popen.assert_called_once_with(command, stdout=PIPE, stderr=PIPE)

    def test_log_output(self):
        scanner = Scanner(Configuration())
        input_lines = [bytes("test\n", encoding="utf-8"), 
                       bytes("\nother line\n\n", encoding="utf-8"),
                       bytes("", encoding="utf-8"),
                       bytes("last \n line", encoding="utf-8")]
        with self.assertLogs(scanner.log) as log:
            scanner._log_output(input_lines)
            self.assertEqual(log.records[0].getMessage(), "test")
            self.assertEqual(log.records[1].getMessage(), "\nother line")
            self.assertEqual(log.records[2].getMessage(), "")
            self.assertEqual(log.records[3].getMessage(), "last \n line")


