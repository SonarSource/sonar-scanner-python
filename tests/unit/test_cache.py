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
import pathlib
import unittest
import pyfakefs.fake_filesystem_unittest as pyfakefs

from pysonar_scanner.cache import Cache, CacheFile
import pysonar_scanner.cache as cache
from pysonar_scanner.configuration.properties import SONAR_USER_HOME


class TestCacheFile(unittest.TestCase):
    def test_is_valid(self):
        self.assertFalse(CacheFile(pathlib.Path("/tmp/none-existing-file"), checksum="123").is_valid())


class TestCache(pyfakefs.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_if_cache_folder_is_created(self):
        cache_path = pathlib.Path("/folder1/folder2/")

        cache = Cache.create_cache(cache_path)
        self.assertTrue(self.fs.exists(cache_path))
        self.assertEqual(cache.cache_folder, cache_path)

    def test_cache_constructor(self):
        with self.assertRaises(FileNotFoundError):
            Cache(pathlib.Path("/folder1/folder2/"))

    def test_get_file(self):
        cache = Cache.create_cache(pathlib.Path("/folder1/folder2/"))
        cache_file = cache.get_file("test", "123")
        self.assertEqual(cache_file.filepath, pathlib.Path("/folder1/folder2/test"))
        self.assertEqual(cache_file.checksum, "123")

    def test_preserves_valid_filenames(self):
        cache = Cache.create_cache(pathlib.Path("/folder1/folder2/"))
        for filename in (
            "sonar-scanner-engine-shaded-8.9.0.43852-all.jar",
            "OpenJDK21U-jre_x64_linux_hotspot_21.0.12.1_1.tar.gz",
            "jdk-21.0.12.1+1-jre.zip_unzip",
            "engine with spaces.jar",
        ):
            with self.subTest(filename=filename):
                expected_path = cache.cache_folder / filename
                self.assertEqual(cache.get_file_path(filename), expected_path)
                self.assertEqual(cache.get_file(filename, "123"), CacheFile(expected_path, "123"))

    def test_rejects_paths_as_filenames(self):
        cache = Cache.create_cache(pathlib.Path("/folder1/folder2/"))
        for filename in (
            "",
            ".",
            "..",
            "../engine.jar",
            "nested/engine.jar",
            "./engine.jar",
            "engine.jar/",
            "/tmp/engine.jar",
            r"..\engine.jar",
            r"nested\engine.jar",
            "engine.jar\\",
            r"C:\temp\engine.jar",
            "C:engine.jar",
            r"\\server\share\engine.jar",
            r"\\?\C:\engine.jar",
        ):
            for get_path in (cache.get_file_path, lambda name: cache.get_file(name, "123")):
                with self.subTest(filename=filename, method=get_path):
                    with self.assertRaises(ValueError) as error:
                        get_path(filename)
                    self.assertEqual(
                        str(error.exception), f"Invalid cache filename {filename!r}: expected a plain filename."
                    )

    def test_get_default(self):
        self.assertEqual(cache.get_cache({}).cache_folder, pathlib.Path.home() / ".sonar/cache")

    def test_uses_user_home(self):
        self.assertEqual(cache.get_cache({SONAR_USER_HOME: "my/home"}).cache_folder, pathlib.Path("my/home") / "cache")

    def test_exists(self):
        cache = Cache.create_cache(pathlib.Path("/folder1/folder2/"))
        cache_file = cache.get_file("test", "123")
        self.assertFalse(cache_file.exists())

        cache_file.filepath.touch()
        self.assertTrue(cache_file.exists())
