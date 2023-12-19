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
