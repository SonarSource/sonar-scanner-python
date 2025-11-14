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
import logging
import unittest

import pytest

from pysonar_scanner import app_logging


class TestAppLogging(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def set_capsys(self, capsys):
        self.capsys = capsys

    def setUp(self) -> None:
        app_logging.setup()

    def test_logging_output_destinations(self):
        logging.info("hello world")
        logging.error("boom!")

        captured = self.capsys.readouterr()
        self.assertIn("INFO: hello world", captured.out)
        self.assertIn("ERROR: boom!", captured.err)
        self.assertEqual(len(captured.err.splitlines()), 1)
        self.assertEqual(len(captured.out.splitlines()), 1)
