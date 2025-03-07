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
from io import BytesIO
import unittest

from pysonar_scanner.utils import SQVersion, calculate_checksum, remove_trailing_slash


class TestUtils(unittest.TestCase):
    def test_removing_trailinlg_slash(self):
        self.assertEqual(remove_trailing_slash("test/"), "test")
        self.assertEqual(remove_trailing_slash(" test/ "), "test")
        self.assertEqual(remove_trailing_slash(" test / "), "test")
        self.assertEqual(remove_trailing_slash("test"), "test")


class TestSQVersion(unittest.TestCase):
    def test_does_support_bootstrapping(self):
        self.assertTrue(SQVersion.from_str("10.6").does_support_bootstrapping())
        self.assertTrue(SQVersion.from_str("10.6.5").does_support_bootstrapping())
        self.assertTrue(SQVersion.from_str("10.6.5a").does_support_bootstrapping())
        self.assertTrue(SQVersion.from_str("10.7").does_support_bootstrapping())
        self.assertTrue(SQVersion.from_str("11.1").does_support_bootstrapping())
        self.assertTrue(SQVersion.from_str("11.1.1").does_support_bootstrapping())
        self.assertTrue(SQVersion.from_str("11").does_support_bootstrapping())

        self.assertFalse(SQVersion.from_str("9.9.9").does_support_bootstrapping())
        self.assertFalse(SQVersion.from_str("9.9.9a").does_support_bootstrapping())
        self.assertFalse(SQVersion.from_str("9.9").does_support_bootstrapping())
        self.assertFalse(SQVersion.from_str("9").does_support_bootstrapping())
        self.assertFalse(SQVersion.from_str("10.5").does_support_bootstrapping())
        self.assertFalse(SQVersion.from_str("10").does_support_bootstrapping())

        self.assertFalse(SQVersion.from_str("a").does_support_bootstrapping())
        self.assertFalse(SQVersion.from_str("1.a").does_support_bootstrapping())

    def test_str(self):
        self.assertEqual(str(SQVersion.from_str("10.6")), "10.6")
        self.assertEqual(str(SQVersion.from_str("9.9.9aa")), "9.9.9aa")


class TestCalculateChecksum(unittest.TestCase):
    def test_calculate_checksum(self):
        self.assertEqual(
            calculate_checksum(BytesIO(b"test")), "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
        )
        self.assertEqual(
            calculate_checksum(BytesIO(b"test test")),
            "03ffdf45276dd38ffac79b0e9c6c14d89d9113ad783d5922580f4c66a3305591",
        )
