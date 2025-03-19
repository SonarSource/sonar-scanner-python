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
import unittest
from unittest import mock
from unittest.mock import patch
from io import StringIO

from pysonar_scanner.jre import JRE
from pysonar_scanner.__main__ import scan
from pysonar_scanner.scannerengine import ScannerEngine

LOG_FAILURE_EXAMPLE = """
{"level":"INFO","message":"CPD Executor CPD calculation finished (done) | time=15ms"}\n
{"level":"INFO","message":"SCM revision ID \'a53e6a3193a049d0f77fc2ff16cf52e7a66c7adb\'"}\n
{"level":"INFO","message":"Analysis report generated in 152ms, dir size=760.6 kB"}\n
{"level":"INFO","message":"Analysis report compressed in 83ms, zip size=321.7 kB"}\n
{"level":"ERROR","message":"You\'re not authorized to analyze this project or the project doesn\'t exist on SonarQube and you\'re not authorized to create it. Please contact an administrator."}\n'
"""


class TestMain(unittest.TestCase):

    @patch("pysonar_scanner.scannerengine.Popen")
    @patch("pysonar_scanner.__main__.__resolve_jre")
    @patch("pysonar_scanner.scannerengine.ScannerEngine.fetch_scanner_engine")
    @patch(
        "sys.argv",
        ["pysonar-scanner", "-t", "myToken", "--sonar-project-key", "myProjectKey"],
    )
    def test_minimal_run_success(self, mock_fetch_scanner_engine, mock_resolve_jre, mock_popen):
        mock_resolve_jre.return_value = JRE("", "", "", "", "", "", None)
        mock_fetch_scanner_engine.return_value = None
        process_mock = mock.Mock()
        attrs = {"communicate.return_value": ("output", "error"), "wait.return_value": 0}
        process_mock.configure_mock(**attrs)
        mock_popen.return_value = process_mock

        exitcode = scan()
        self.assertEqual(exitcode, 0)

    @patch("pysonar_scanner.scannerengine.Popen")
    @patch("pysonar_scanner.__main__.__resolve_jre")
    @patch("pysonar_scanner.scannerengine.ScannerEngine.fetch_scanner_engine")
    @patch(
        "sys.argv",
        ["pysonar-scanner", "-t", "myToken", "--sonar-project-key", "myProjectKey"],
    )
    def test_minimal_run_failure(self, mock_fetch_scanner_engine, mock_resolve_jre, mock_popen):
        mock_resolve_jre.return_value = JRE("", "", "", "", "", "", None)
        mock_fetch_scanner_engine.return_value = None
        process_mock = mock.Mock()
        attrs = {"communicate.return_value": (LOG_FAILURE_EXAMPLE, "error"), "wait.return_value": 2}
        process_mock.configure_mock(**attrs)
        mock_popen.return_value = process_mock
        with self.assertRaises(RuntimeError) as error:
            scan()
        print(str(error))
        self.assertIn("Scan failed with exit code 2", str(error.exception))
