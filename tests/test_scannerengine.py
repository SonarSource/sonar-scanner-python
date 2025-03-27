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
import json
import logging
from math import log
from subprocess import PIPE
import unittest
import pathlib
import pyfakefs.fake_filesystem_unittest as pyfakefs

from pysonar_scanner import app_logging, cache
from pysonar_scanner import scannerengine
from pysonar_scanner.exceptions import ChecksumException, SQTooOldException
from pysonar_scanner.jre import JREProvisioner, JREResolvedPath, JREResolver
from pysonar_scanner.scannerengine import (
    CmdExecutor,
    LogLine,
    ScannerEngine,
    ScannerEngineProvisioner,
    default_log_line_listener,
    parse_log_line,
)
from unittest.mock import Mock

from pysonar_scanner.api import SQVersion
from tests import sq_api_utils
from unittest.mock import patch, MagicMock


class TestLogLine(unittest.TestCase):
    def test_without_stacktrace(self):
        line = '{"level":"INFO","message":"a message"}'
        log_line = scannerengine.parse_log_line(line)
        self.assertEqual(log_line, LogLine(level="INFO", message="a message", stacktrace=None))

    def test_with_stacktrace(self):
        line = '{"level":"INFO","message":"a message", "stacktrace":"a stacktrace"}'
        log_line = scannerengine.parse_log_line(line)
        self.assertEqual(log_line, LogLine(level="INFO", message="a message", stacktrace="a stacktrace"))

    def test_invalid_json(self):
        line = '"level":"INFO","message":"a message", "stacktrace":"a stacktrace"}'
        log_line = scannerengine.parse_log_line(line)
        self.assertEqual(log_line, LogLine(level="INFO", message=line, stacktrace=None))

    def test_no_level(self):
        line = '{"message":"a message"}'
        log_line = scannerengine.parse_log_line(line)
        self.assertEqual(log_line, LogLine(level="INFO", message="a message", stacktrace=None))


class TestCmdExecutor(unittest.TestCase):

    @patch("pysonar_scanner.scannerengine.Popen")
    def test_execute_successful(self, mock_popen):
        mock_process = MagicMock()
        mock_process.stdout = []
        mock_process.stderr = []
        mock_process.wait.return_value = 0
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        cmd_executor = scannerengine.CmdExecutor(["echo", "hello"], "key=value")
        return_code = cmd_executor.execute()

        mock_popen.assert_called_once_with(["echo", "hello"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        mock_process.stdin.write.assert_called_once_with(b"key=value")
        mock_process.stdin.close.assert_called_once()
        self.assertEqual(return_code, 0)

    @patch("pysonar_scanner.scannerengine.Popen")
    def test_error_log_extraction(self, popen_mock):
        log_info = [
            b'{"level":"INFO","message":"info2"}',
            b'{"level":"WARN","message":"info1"}',
        ]
        log_error = [
            b'{"level":"ERROR","message":"an error"}',
            b'{"level":"ERROR","message":"another error", "stacktrace":"a stacktrace"}',
        ]

        popen_mock.return_value.stdin = MagicMock()
        popen_mock.return_value.stdout = log_info
        popen_mock.return_value.stderr = log_error

        actual_lines = set()
        expected_lines = {
            LogLine(level="INFO", message="info2", stacktrace=None),
            LogLine(level="WARN", message="info1", stacktrace=None),
            LogLine(level="ERROR", message="an error", stacktrace=None),
            LogLine(level="ERROR", message="another error", stacktrace="a stacktrace"),
        }

        def log_line_listener(log_line: LogLine):
            actual_lines.add(log_line)

        scannerengine.CmdExecutor(["echo"], "", log_line_listener).execute()

        self.assertEqual(actual_lines, expected_lines)

    def test_to_logging_level(self):
        self.assertEqual(LogLine(level="ERROR", message="").get_logging_level(), logging.ERROR)
        self.assertEqual(LogLine(level="WARN", message="").get_logging_level(), logging.WARNING)
        self.assertEqual(LogLine(level="INFO", message="").get_logging_level(), logging.INFO)
        self.assertEqual(LogLine(level="DEBUG", message="").get_logging_level(), logging.DEBUG)
        self.assertEqual(LogLine(level="TRACE", message="").get_logging_level(), logging.DEBUG)
        self.assertEqual(LogLine(level="UNKNOWN", message="").get_logging_level(), logging.INFO)

    def test_default_log_line_listener(self):
        with self.subTest("log line without stacktrace"), self.assertLogs(level="INFO") as logs:
            scannerengine.default_log_line_listener(LogLine(level="INFO", message="info1", stacktrace=None))
            self.assertEqual(logs.output, ["INFO:root:info1"])

        with self.subTest("log line with stacktrace"), self.assertLogs(level="INFO") as logs:
            default_log_line_listener(LogLine(level="WARN", message="info2", stacktrace="a stacktrace"))
            self.assertEqual(logs.output, ["WARNING:root:info2", "WARNING:root:a stacktrace"])


class TestScannerEngineWithFake(pyfakefs.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    @patch("pysonar_scanner.scannerengine.CmdExecutor")
    @patch.object(JREResolver, "resolve_jre")
    @patch.object(ScannerEngineProvisioner, "provision")
    def test_command_building(self, provision_mock, resolve_jre_mock, execute_mock):
        provision_mock.return_value = pathlib.Path("/test/scanner-engine.jar")
        resolve_jre_mock.return_value = JREResolvedPath(pathlib.Path("jre/bin/java"))

        config = {
            "sonar.token": "myToken",
            "sonar.projectKey": "myProjectKey",
            "sonar.scanner.os": "linux",
            "sonar.scanner.arch": "x64",
        }

        expected_std_in = json.dumps(
            {
                "scannerProperties": [
                    {"key": "sonar.token", "value": "myToken"},
                    {"key": "sonar.projectKey", "value": "myProjectKey"},
                    {"key": "sonar.scanner.os", "value": "linux"},
                    {"key": "sonar.scanner.arch", "value": "x64"},
                ]
            }
        )

        scannerengine.ScannerEngine(sq_api_utils.get_sq_cloud(), cache.get_default()).run(config)

        execute_mock.assert_called_once_with(
            [pathlib.Path("jre/bin/java"), "-jar", pathlib.Path("/test/scanner-engine.jar")], expected_std_in
        )

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
