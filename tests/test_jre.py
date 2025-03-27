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
import io
import pathlib
import tarfile
from unittest.mock import Mock, patch
from typing_extensions import TypedDict
import unittest
import pyfakefs.fake_filesystem_unittest as pyfakefs

from pysonar_scanner import cache, utils
from pysonar_scanner.api import JRE
from pysonar_scanner.configuration.properties import (
    SONAR_SCANNER_JAVA_EXE_PATH,
    SONAR_SCANNER_OS,
    SONAR_SCANNER_SKIP_JRE_PROVISIONING,
)
from pysonar_scanner.exceptions import ChecksumException, NoJreAvailableException, UnsupportedArchiveFormat
from pysonar_scanner.jre import JREProvisioner, JREResolvedPath, JREResolver, JREResolverConfiguration
from pysonar_scanner.utils import Os, Arch
from tests import sq_api_utils

import zipfile


@patch("pysonar_scanner.utils.get_os", return_value=Os.LINUX)
@patch("pysonar_scanner.utils.get_arch", return_value=Arch.X64)
class TestJREProvisioner(pyfakefs.TestCase):
    def setUp(self):
        self.setUpPyfakefs(allow_root_user=False)

        self.cache = cache.get_default()
        self.api = sq_api_utils.get_sq_server()

        self.__setup_zip_file()
        self.__setup_tar_file()

        self.other_jre = self.other_jre = JRE(
            id="2",
            filename="fake_jre.zip",
            sha256="fakechecksum",
            java_path="fake_java",
            os=Os.WINDOWS.value,
            arch="x64",
            download_url="http://example.com/fake_jre.zip",
        )

    def __setup_zip_file(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zip_file:
            zip_file.writestr("readme.md", b"hello world")

        self.zip_name = "jre.zip"
        self.zip_bytes = buffer.getvalue()
        self.zip_checksum = utils.calculate_checksum(io.BytesIO(self.zip_bytes))
        self.zip_jre = JRE(
            id="zip_jre",
            filename=self.zip_name,
            sha256=self.zip_checksum,
            java_path="java",
            os=Os.LINUX.value,
            arch=Arch.AARCH64.value,
            download_url=None,
        )

    def __setup_tar_file(self):
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w:gz") as tar_file:
            tarinfo = tarfile.TarInfo(name="readme.md")
            tarinfo.size = len(b"hello world")
            tar_file.addfile(tarinfo, io.BytesIO(b"hello world"))

        self.tar_gz_name = "jre17.0.13.tar.gz"
        self.tar_gz_bytes = buffer.getvalue()
        self.tar_gz_checksum = utils.calculate_checksum(io.BytesIO(self.tar_gz_bytes))
        self.tar_gz_jre = JRE(
            id="tar_gz_jre",
            filename=self.tar_gz_name,
            sha256=self.tar_gz_checksum,
            java_path="java",
            os=Os.LINUX.value,
            arch=Arch.AARCH64.value,
            download_url=None,
        )

        self.tgz_name = "jre.tgz"
        self.tgz_bytes = self.tar_gz_bytes
        self.tgz_checksum = self.tar_gz_checksum
        self.tgz_jre = JRE(
            id="tgz_jre",
            filename=self.tgz_name,
            sha256=self.tgz_checksum,
            java_path="java",
            os=Os.LINUX.value,
            arch=Arch.AARCH64.value,
            download_url=None,
        )

    def test_if_patching_worked(self, get_os_mock, get_arch_mock):
        self.assertEqual(utils.get_os(), Os.LINUX)
        self.assertEqual(utils.get_arch(), Arch.X64)

    def test_successfully_downloading_jre(self, get_os_mock, get_arch_mock):
        class JRETestCase(TypedDict):
            jre: JRE
            bytes: bytes
            checksum: str
            unzip_dir: str

        jres_to_test: list[JRETestCase] = [
            {"jre": self.zip_jre, "bytes": self.zip_bytes, "checksum": self.zip_checksum, "unzip_dir": "jre.zip_unzip"},
            {
                "jre": self.tar_gz_jre,
                "bytes": self.tar_gz_bytes,
                "checksum": self.tar_gz_checksum,
                "unzip_dir": "jre17.0.13.tar.gz_unzip",
            },
            {"jre": self.tgz_jre, "bytes": self.tgz_bytes, "checksum": self.tgz_checksum, "unzip_dir": "jre.tgz_unzip"},
        ]
        for testcase in jres_to_test:
            testcase_jre = testcase["jre"]
            jres = [testcase_jre, self.other_jre]
            with self.subTest(jre=testcase), sq_api_utils.sq_api_mocker() as mocker:
                mocker.mock_analysis_jres(body=[sq_api_utils.jre_to_dict(jre) for jre in jres])
                mocker.mock_analysis_jre_download(id=testcase_jre.id, body=testcase["bytes"], status=200)

                provisioner = JREProvisioner(self.api, self.cache, utils.get_os().value, utils.get_arch().value)
                jre_path = provisioner.provision()

                cache_file = self.cache.get_file(testcase_jre.filename, testcase["checksum"])
                self.assertTrue(cache_file.is_valid())

                unziped_dir = self.cache.get_file_path(testcase["unzip_dir"])
                self.assertEqual(jre_path, JREResolvedPath(unziped_dir / "java"))

                self.assertTrue(unziped_dir.exists())
                self.assertTrue((unziped_dir / "readme.md").exists())
                self.assertEqual((unziped_dir / "readme.md").read_bytes(), b"hello world")

    def test_invalid_checksum(self, *args):
        with self.assertRaises(ChecksumException), sq_api_utils.sq_api_mocker() as mocker:
            jre_dict = sq_api_utils.jre_to_dict(self.zip_jre)
            jre_dict["sha256"] = "invalid"
            mocker.mock_analysis_jres(body=[jre_dict])
            mocker.mock_analysis_jre_download(id="zip_jre", body=self.zip_bytes, status=200)

            JREProvisioner(self.api, self.cache, utils.get_os().value, utils.get_arch().value).provision()

    def test_retry_mechanism(self, *args):
        with sq_api_utils.sq_api_mocker() as mocker:
            jre_dict_with_invalid_checksum = sq_api_utils.jre_to_dict(self.zip_jre)
            jre_dict_with_invalid_checksum["sha256"] = "invalid"

            jre_dict = sq_api_utils.jre_to_dict(self.zip_jre)
            mocker.mock_analysis_jres(body=[jre_dict_with_invalid_checksum])
            mocker.mock_analysis_jres(body=[jre_dict])
            mocker.mock_analysis_jre_download(id="zip_jre", body=self.zip_bytes, status=200)

            JREProvisioner(self.api, self.cache, utils.get_os().value, utils.get_arch().value).provision()

            cache_file = self.cache.get_file(self.zip_jre.filename, self.zip_checksum)
            self.assertTrue(cache_file.is_valid())

    def test_already_cached(self, *args):
        with sq_api_utils.sq_api_mocker(assert_all_requests_are_fired=False) as mocker:
            jre_dict = sq_api_utils.jre_to_dict(self.zip_jre)
            metadata_rsps = mocker.mock_analysis_jres(body=[jre_dict])
            download_rsps = mocker.mock_analysis_jre_download(id="zip_jre", status=500)

            with self.cache.get_file(self.zip_jre.filename, self.zip_checksum).open(mode="wb") as f:
                f.write(self.zip_bytes)

            JREProvisioner(self.api, self.cache, utils.get_os().value, utils.get_arch().value).provision()

            cache_file = self.cache.get_file(self.zip_jre.filename, self.zip_checksum)
            self.assertTrue(cache_file.is_valid())

            self.assertEqual(metadata_rsps.call_count, 1, msg="Metadata should be fetched once")
            self.assertEqual(download_rsps.call_count, 0, msg="Download should not be attempted")

    def test_file_already_exists_with_invalid_checksum(self, *args):
        with sq_api_utils.sq_api_mocker() as mocker:
            jre_dict = sq_api_utils.jre_to_dict(self.zip_jre)
            mocker.mock_analysis_jres(body=[jre_dict])
            mocker.mock_analysis_jre_download(id="zip_jre", body=self.zip_bytes, status=200)

            with self.cache.get_file(self.zip_jre.filename, self.zip_checksum).open(mode="wb") as f:
                f.write(b"invalid content")
            cache_file = self.cache.get_file(self.zip_jre.filename, self.zip_checksum)
            self.assertFalse(
                cache_file.is_valid(), msg="Cache file should have invalid checksum before provisioner ran"
            )

            JREProvisioner(self.api, self.cache, utils.get_os().value, utils.get_arch().value).provision()

            self.assertTrue(cache_file.is_valid(), msg="Cache file should have valid checksum after provisioner ran")

    def test_no_jre_available(self, *args):
        with self.assertRaises(NoJreAvailableException), sq_api_utils.sq_api_mocker() as mocker:
            mocker.mock_analysis_jres(body=[])
            JREProvisioner(self.api, self.cache, utils.get_os().value, utils.get_arch().value).provision()

    def test_unzip_dir_already_exists(self, *args):
        with sq_api_utils.sq_api_mocker() as mocker:
            mocker.mock_analysis_jres(body=[sq_api_utils.jre_to_dict(self.zip_jre)])
            mocker.mock_analysis_jre_download(id="zip_jre", body=self.zip_bytes, status=200)

            unzip_dir = self.cache.get_file_path("jre.zip_unzip")
            unzip_dir.mkdir()
            (unzip_dir / "subdir").mkdir()
            old_text_file = unzip_dir / "subdir/test.txt"
            old_text_file.write_text("test")

            JREProvisioner(self.api, self.cache, utils.get_os().value, utils.get_arch().value).provision()

            self.assertTrue(unzip_dir.exists())
            self.assertTrue((unzip_dir / "readme.md").exists())
            self.assertEqual((unzip_dir / "readme.md").read_bytes(), b"hello world")
            self.assertFalse(old_text_file.exists())

    def test_unsupported_jre(self, *args):
        unsupported_archive_jre = JRE(
            id="unsupported",
            filename="jre.txt",
            sha256=self.zip_checksum,
            java_path="java",
            os=Os.LINUX.value,
            arch=Arch.AARCH64.value,
            download_url=None,
        )

        with self.assertRaises(UnsupportedArchiveFormat), sq_api_utils.sq_api_mocker() as mocker:
            mocker.mock_analysis_jres(body=[sq_api_utils.jre_to_dict(unsupported_archive_jre)])
            mocker.mock_analysis_jre_download(id="unsupported", body=self.zip_bytes, status=200)
            JREProvisioner(self.api, self.cache, utils.get_os().value, utils.get_arch().value).provision()


class TestJREResolvedPath(unittest.TestCase):
    def test_empty_path(self):
        with self.assertRaises(ValueError):
            JREResolvedPath.from_string("")

    def test_any_path(self):
        path = pathlib.Path("test")
        resolved_path = JREResolvedPath(path)
        self.assertEqual(resolved_path.path, path)


class TestJREResolverConfiguration(unittest.TestCase):
    def test_default(self):
        config = JREResolverConfiguration.from_dict({})

        self.assertIsNone(config.sonar_scanner_java_exe_path)
        self.assertFalse(config.sonar_scanner_skip_jre_provisioning)
        self.assertIsNone(config.sonar_scanner_os)

    def test(self):
        config = JREResolverConfiguration.from_dict(
            {
                SONAR_SCANNER_JAVA_EXE_PATH: "a/b",
                SONAR_SCANNER_SKIP_JRE_PROVISIONING: True,
                SONAR_SCANNER_OS: Os.WINDOWS.value,
            }
        )

        self.assertEqual(config.sonar_scanner_java_exe_path, "a/b")
        self.assertTrue(config.sonar_scanner_skip_jre_provisioning)
        self.assertEqual(config.sonar_scanner_os, Os.WINDOWS.value)


class TestJREResolver(unittest.TestCase):
    def test_resolve_jre(self):
        class TestCaseDict(TypedDict):
            name: str
            config: JREResolverConfiguration
            expected: JREResolvedPath

        provisioner = Mock()
        provisioner_jre_path = JREResolvedPath.from_string("java")
        mock_function = {"provision.return_value": provisioner_jre_path}
        provisioner.configure_mock(**mock_function)

        cases: list[TestCaseDict] = [
            {
                "name": "if java exe path is set return it",
                "config": JREResolverConfiguration(
                    sonar_scanner_java_exe_path="a/b", sonar_scanner_skip_jre_provisioning=False, sonar_scanner_os=None
                ),
                "expected": JREResolvedPath.from_string("a/b"),
            },
            {
                "name": "if java_exe_path is not set provision jre",
                "config": JREResolverConfiguration(
                    sonar_scanner_java_exe_path=None, sonar_scanner_skip_jre_provisioning=False, sonar_scanner_os=None
                ),
                "expected": provisioner_jre_path,
            },
            {
                "name": "if java_exe_path is an empty string provision jre",
                "config": JREResolverConfiguration(
                    sonar_scanner_java_exe_path="", sonar_scanner_skip_jre_provisioning=False, sonar_scanner_os=None
                ),
                "expected": provisioner_jre_path,
            },
            {
                "name": "if skip_jre_provisioning is false provision jre",
                "config": JREResolverConfiguration(
                    sonar_scanner_skip_jre_provisioning=False, sonar_scanner_java_exe_path=None, sonar_scanner_os=None
                ),
                "expected": provisioner_jre_path,
            },
            {
                "name": "if skip_jre_provisioning is True and java_home is not set return the default",
                "config": JREResolverConfiguration(
                    sonar_scanner_skip_jre_provisioning=True, sonar_scanner_java_exe_path=None, sonar_scanner_os=None
                ),
                "expected": JREResolvedPath.from_string("java"),
            },
            {
                "name": "if skip_jre_provisioning is True and java_home is not set return the default for windows",
                "config": JREResolverConfiguration(
                    sonar_scanner_os=Os.WINDOWS.value,
                    sonar_scanner_skip_jre_provisioning=True,
                    sonar_scanner_java_exe_path=None,
                ),
                "expected": JREResolvedPath.from_string("java.exe"),
            },
        ]

        for case in cases:
            expected = case["expected"]
            with self.subTest(case["name"], config=case["config"], expected=expected):
                actual = JREResolver(case["config"], provisioner).resolve_jre()
                self.assertEqual(actual, expected)
