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
from unittest.mock import patch, Mock, MagicMock
from py_sonar_scanner.__main__ import scan
from py_sonar_scanner.logger import ApplicationLogger
from py_sonar_scanner.scanner import Scanner


class TestMain(unittest.TestCase):
    @patch("py_sonar_scanner.scanner.Scanner")
    @patch("py_sonar_scanner.__main__.Environment")
    @patch("py_sonar_scanner.__main__.Configuration")
    def test_main_scan(self, mock_cfg, mock_env, mock_scanner):
        configuration_instance = MagicMock()
        configuration_instance.setup = Mock()
        mock_cfg.return_value = configuration_instance

        environment_instance = MagicMock()
        environment_instance.setup = Mock()
        mock_scanner.scan = Mock()
        environment_instance.scanner.return_value = mock_scanner
        mock_env.return_value = environment_instance

        scan()

        configuration_instance.setup.assert_called_once()
        environment_instance.setup.assert_called_once()
        environment_instance.scanner.assert_called_once()
        mock_scanner.scan.assert_called_once()

    @patch("py_sonar_scanner.scanner.Scanner")
    @patch("py_sonar_scanner.__main__.Environment")
    @patch("py_sonar_scanner.configuration.sys")
    def test_main_scan_fail(self, mock_sys, mock_env, mock_scanner):
        mock_sys.argv = ["path/to/scanner/py-sonar-scanner"]
        environment_instance = MagicMock()
        environment_instance.setup = Mock(side_effect=Exception("Something"))
        mock_scanner.scan = Mock()
        environment_instance.scanner.return_value = mock_scanner
        mock_env.return_value = environment_instance

        with self.assertLogs(ApplicationLogger.get_logger()) as log:
            scan()
            self.assertEqual(2, len(log.records))
            self.assertEqual("Error during SonarScanner execution: Something", log.records[0].getMessage())
            self.assertFalse(log.records[0].exc_info)
            self.assertEqual(
                "Re-run SonarScanner using the -X switch to enable full debug logging.", log.records[1].getMessage()
            )

    @patch("py_sonar_scanner.scanner.Scanner")
    @patch("py_sonar_scanner.__main__.Environment")
    @patch("py_sonar_scanner.configuration.sys")
    def test_main_scan_debug_fail(self, mock_sys, mock_env, mock_scanner):
        mock_sys.argv = ["path/to/scanner/py-sonar-scanner", "-X"]

        environment_instance = MagicMock()
        environment_instance.setup = Mock(side_effect=Exception("Something"))
        mock_scanner.scan = Mock()
        environment_instance.scanner.return_value = mock_scanner
        mock_env.return_value = environment_instance

        with self.assertLogs(ApplicationLogger.get_logger()) as log:
            scan()
            self.assertEqual(1, len(log.records))
            self.assertEqual("Error during SonarScanner execution: Something", log.records[0].getMessage())
            self.assertTrue(log.records[0].exc_info)
