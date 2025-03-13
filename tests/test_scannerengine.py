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
import pathlib
import unittest
import pyfakefs.fake_filesystem_unittest as pyfakefs

from pysonar_scanner import cache
from pysonar_scanner.exceptions import ChecksumException, SQTooOldException
from pysonar_scanner.scannerengine import ScannerEngine, ScannerEngineProvisioner
from unittest.mock import Mock

from pysonar_scanner.api import SQVersion
from tests import sq_api_utils


class TestScannerEngine(pyfakefs.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_version_check(self):
        with self.subTest("SQ:Server is too old"):
            sq_cloud_api = sq_api_utils.get_sq_server()
            sq_cloud_api.get_analysis_version = Mock(return_value=SQVersion.from_str("9.9.9"))
            scannerengine = ScannerEngine(sq_cloud_api, cache.get_default())

            with self.assertRaises(SQTooOldException):
                scannerengine._ScannerEngine__version_check()

        with self.subTest("SQ:Server that is new than 10.6"):
            sq_cloud_api = sq_api_utils.get_sq_server()
            sq_cloud_api.get_analysis_version = Mock(return_value=SQVersion.from_str("10.7"))
            scannerengine = ScannerEngine(sq_cloud_api, cache.get_default())

            scannerengine._ScannerEngine__version_check()

            sq_cloud_api.get_analysis_version.assert_called_once()

        with self.subTest("SQ:Cloud "):
            sq_cloud_api = sq_api_utils.get_sq_cloud()
            sq_cloud_api.get_analysis_version = Mock()
            scannerengine = ScannerEngine(sq_cloud_api, cache.get_default())

            scannerengine._ScannerEngine__version_check()

            sq_cloud_api.get_analysis_version.assert_not_called()


class TestScannerEngineProvisioner(pyfakefs.TestCase):
    def setUp(self):
        self.setUpPyfakefs(allow_root_user=False)

        self.api = sq_api_utils.get_sq_server()
        self.cache = cache.Cache.create_cache(pathlib.Path("/some-folder/cache-folder"))
        self.test_file_content = b"test content"
        self.test_file_checksum = "6ae8a75555209fd6c44157c0aed8016e763ff435a19cf186f76863140143ff72"
        self.test_file_path = pathlib.Path("/some-folder/cache-folder/scanner-engine.jar")

    def test_happy_path(self):
        with sq_api_utils.sq_api_mocker() as mocker:
            mocker.mock_analysis_engine(filename="scanner-engine.jar", sha256=self.test_file_checksum)
            mocker.mock_analysis_engine_download(body=self.test_file_content)

            ScannerEngineProvisioner(self.api, self.cache).provision()

            self.assertTrue(self.test_file_path.exists())
            self.assertEqual(self.test_file_path.read_bytes(), self.test_file_content)

    def test_scanner_engine_is_cached(self):
        with sq_api_utils.sq_api_mocker(assert_all_requests_are_fired=False) as mocker:
            engine_info_rsps = mocker.mock_analysis_engine(
                filename="scanner-engine.jar", sha256=self.test_file_checksum
            )
            engine_download_rsps = mocker.mock_analysis_engine_download(status=500)

            self.fs.create_file(self.test_file_path, contents=self.test_file_content)

            ScannerEngineProvisioner(self.api, self.cache).provision()

            self.assertTrue(self.test_file_path.exists())
            self.assertEqual(self.test_file_path.read_bytes(), self.test_file_content)

            self.assertEqual(engine_info_rsps.call_count, 1)
            self.assertEqual(engine_download_rsps.call_count, 0)

    def test_checksum_is_invalid(self):
        with self.assertRaises(ChecksumException), sq_api_utils.sq_api_mocker() as mocker:
            mocker.mock_analysis_engine(filename="scanner-engine.jar", sha256="invalid-checksum")
            mocker.mock_analysis_engine_download(body=self.test_file_content)

            ScannerEngineProvisioner(self.api, self.cache).provision()

    def test_checksum_changed(self):
        with sq_api_utils.sq_api_mocker() as mocker:
            mocker.mock_analysis_engine(filename="scanner-engine.jar", sha256="invalid-checksum")
            mocker.mock_analysis_engine_download(body=self.test_file_content)
            correct_checksum_rsps = mocker.mock_analysis_engine(
                filename="scanner-engine.jar", sha256=self.test_file_checksum
            )

            ScannerEngineProvisioner(self.api, self.cache).provision()

            self.assertTrue(self.test_file_path.exists())
            self.assertEqual(self.test_file_path.read_bytes(), self.test_file_content)
            self.assertEqual(correct_checksum_rsps.call_count, 1)

    def test_permission_error(self):
        with self.assertRaises(PermissionError), sq_api_utils.sq_api_mocker() as mocker:
            mocker.mock_analysis_engine(filename="scanner-engine.jar", sha256=self.test_file_checksum)
            mocker.mock_analysis_engine_download(body=self.test_file_content)

            self.fs.chmod("/some-folder/cache-folder", mode=0o000)

            ScannerEngineProvisioner(self.api, self.cache).provision()
