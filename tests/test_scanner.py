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
