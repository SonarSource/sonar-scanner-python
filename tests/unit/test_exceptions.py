#
# Sonar Scanner Python
# Copyright (C) 2011-2024 SonarSource Sàrl.
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
import pytest
import unittest
import logging
from pysonar_scanner.exceptions import log_error, EXCEPTION_RETURN_CODE


class TestExceptions(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def set_caplog(self, caplog: pytest.LogCaptureFixture):
        self.caplog = caplog

    def test_log_error_returns_exception_return_code(self):
        exception = Exception("Test exception")
        result = log_error(exception)
        self.assertEqual(result, EXCEPTION_RETURN_CODE)

    def setUp(self) -> None:
        self.caplog.clear()

    def test_log_error_logs_message(self):
        # Test that log_error logs the exception message
        exception = Exception("Test exception")
        with self.caplog.at_level(logging.ERROR):
            log_error(exception)

        self.assertIn("Test exception", self.caplog.text)
        self.assertNotIn("Traceback", self.caplog.text)

    def test_log_error_includes_stack_trace_in_debug_mode(self):
        # raises an exception to get an Exception object with a strace trace
        try:
            raise Exception("Test exception")
        except Exception as exception:
            with self.caplog.at_level(logging.DEBUG):
                log_error(exception)

        self.assertIn("Test exception", self.caplog.text)
        self.assertIn("Traceback", self.caplog.text)
