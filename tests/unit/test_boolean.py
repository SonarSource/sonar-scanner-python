#
# Sonar Scanner Python
# Copyright (C) 2011-2026 SonarSource Sàrl
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

from pysonar_scanner.configuration.boolean import parse_bool


class TestParseBool(unittest.TestCase):
    def test_boolean_values_are_preserved(self):
        for value in (True, False):
            with self.subTest(value=value):
                self.assertIs(parse_bool(value), value)

    def test_string_values_are_case_insensitive(self):
        for value, expected in (
            ("true", True),
            ("TRUE", True),
            ("TrUe", True),
            ("false", False),
            ("FALSE", False),
            ("FaLsE", False),
        ):
            with self.subTest(value=value):
                self.assertIs(parse_bool(value), expected)

    def test_invalid_values_are_rejected(self):
        for value in ("", "invalid", "1", " true", None, 0, 1, [], {}):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "Expected 'true' or 'false'"):
                parse_bool(value)
