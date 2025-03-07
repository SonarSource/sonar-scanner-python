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

from pysonar_scanner.cache import Cache, CacheFile
import pysonar_scanner.cache as cache


class TestCacheFile(unittest.TestCase):
    def test_is_valid(self):
        self.assertFalse(CacheFile(pathlib.Path("/tmp/none-existing-file"), checksum="123").is_valid())


class TestCache(unittest.TestCase):
    def test_get_file(self):
        cache = Cache(pathlib.Path("/tmp"))
        cache_file = cache.get_file("test", "123")
        self.assertEqual(cache_file.filepath, pathlib.Path("/tmp/test"))
        self.assertEqual(cache_file.checksum, "123")

    def test_get_default(self):
        self.assertEqual(cache.get_default().cache_folder, pathlib.Path.home() / ".sonar-scanner")
