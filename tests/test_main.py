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

from pysonar_scanner.exceptions import MissingKeyException
from pysonar_scanner.jre import JRE, JREResolvedPath
from pysonar_scanner.__main__ import scan
from pysonar_scanner import __main__ as main
from pysonar_scanner.scannerengine import ScannerEngine


class TestMain(unittest.TestCase):

    @patch("pysonar_scanner.scannerengine.Popen")
    @patch.object(ScannerEngine, "_ScannerEngine__resolve_jre")
    @patch.object(ScannerEngine, "_ScannerEngine__fetch_scanner_engine")
    @patch(
        "sys.argv",
        ["pysonar-scanner", "-t", "myToken", "--sonar-project-key", "myProjectKey"],
    )
    def test_minimal_run_success(self, mock_fetch_scanner_engine, mock_resolve_jre, mock_popen):
        mock_resolve_jre.return_value = JREResolvedPath("")
        mock_fetch_scanner_engine.return_value = None
        process_mock = mock.Mock()
        attrs = {"communicate.return_value": ("output", "error"), "wait.return_value": 0}
        process_mock.configure_mock(**attrs)
        mock_popen.return_value = process_mock

        exitcode = scan()
        self.assertEqual(exitcode, 0)

    @patch("pysonar_scanner.scannerengine.Popen")
    @patch.object(ScannerEngine, "_ScannerEngine__resolve_jre")
    @patch.object(ScannerEngine, "_ScannerEngine__fetch_scanner_engine")
    @patch(
        "sys.argv",
        ["pysonar-scanner", "-t", "myToken", "--sonar-project-key", "myProjectKey"],
    )
    def test_minimal_run_failure(self, mock_fetch_scanner_engine, mock_resolve_jre, mock_popen):
        mock_resolve_jre.return_value = JREResolvedPath("")
        process_mock = mock.Mock()
        mock_fetch_scanner_engine.return_value = None
        attrs = {"communicate.return_value": ("output", "error"), "wait.return_value": 2}
        process_mock.configure_mock(**attrs)
        mock_popen.return_value = process_mock
        with self.assertRaises(RuntimeError) as error:
            scan()
        print(str(error))
        self.assertIn("Scan failed with exit code 2", str(error.exception))
