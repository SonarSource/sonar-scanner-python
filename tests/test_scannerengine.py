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

from pysonar_scanner.api import BaseUrls, SonarQubeApi
from pysonar_scanner.exceptions import SQTooOldException
from pysonar_scanner.scannerengine import ScannerEngine
from unittest.mock import Mock

from pysonar_scanner.utils import SQVersion
from tests import sqapiutils


class TestScannerEngine(unittest.TestCase):
    def test_version_check(self):
        with self.subTest("SQ:Server is too old"):
            sq_cloud_api = sqapiutils.get_sq_server()
            sq_cloud_api.get_analysis_version = Mock(return_value=SQVersion.from_str("9.9.9"))
            scannerengine = ScannerEngine(sq_cloud_api)

            with self.assertRaises(SQTooOldException):
                scannerengine._ScannerEngine__version_check()

        with self.subTest("SQ:Server that is new than 10.6"):
            sq_cloud_api = sqapiutils.get_sq_server()
            sq_cloud_api.get_analysis_version = Mock(return_value=SQVersion.from_str("10.7"))
            scannerengine = ScannerEngine(sq_cloud_api)

            scannerengine._ScannerEngine__version_check()

            sq_cloud_api.get_analysis_version.assert_called_once()

        with self.subTest("SQ:Cloud "):
            sq_cloud_api = sqapiutils.get_sq_cloud()
            sq_cloud_api.get_analysis_version = Mock()
            scannerengine = ScannerEngine(sq_cloud_api)

            scannerengine._ScannerEngine__version_check()

            sq_cloud_api.get_analysis_version.assert_not_called()
