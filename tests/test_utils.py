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
import pathlib
import unittest
import unittest.mock
import pyfakefs.fake_filesystem_unittest as pyfakefs

from pysonar_scanner.utils import get_arch, get_os, remove_trailing_slash, calculate_checksum


class TestUtils(unittest.TestCase):
    def test_removing_trailinlg_slash(self):
        self.assertEqual(remove_trailing_slash("test/"), "test")
        self.assertEqual(remove_trailing_slash(" test/ "), "test")
        self.assertEqual(remove_trailing_slash(" test / "), "test")
        self.assertEqual(remove_trailing_slash("test"), "test")

    def test_get_os(self):
        with self.subTest("os=Windows"), unittest.mock.patch("platform.system", return_value="Windows"):
            self.assertEqual(get_os(), "windows")

        with self.subTest("os=Darwin"), unittest.mock.patch("platform.system", return_value="Darwin"):
            self.assertEqual(get_os(), "mac")

    def test_get_arch(self):
        x64_machine_strs = ["amd64", "AmD64", "x86_64", "X86_64"]
        for machine_str in x64_machine_strs:
            with self.subTest("amd64", machine_str=machine_str), unittest.mock.patch(
                "platform.machine", return_value=machine_str
            ):
                self.assertEqual(get_arch(), "x64")
        arm_machine_strs = ["arm64", "ARm64"]
        for machine_str in arm_machine_strs:
            with self.subTest("arm", machine_str=machine_str), unittest.mock.patch(
                "platform.machine", return_value=machine_str
            ):
                self.assertEqual(get_arch(), "aarch64")


class TestAlpineDetection(unittest.TestCase):
    def setUp(self):
        self.alpine_texts: list[str] = [
            """
            NAME="Alpine Linux"
            ID=alpine
            VERSION_ID=3.21.3
            PRETTY_NAME="Alpine Linux v3.21"
            HOME_URL="https://alpinelinux.org/"
            BUG_REPORT_URL="https://gitlab.alpinelinux.org/alpine/aports/-/issues""",
            """
            ID="alpine"
            VERSION_ID=3.21.3
            PRETTY_NAME="Alpine Linux v3.21"
            HOME_URL="https://alpinelinux.org/"
            BUG_REPORT_URL="https://gitlab.alpinelinux.org/alpine/aports/-/issues""",
        ]
        self.ubuntu_text = """
            PRETTY_NAME="Ubuntu 22.04.5 LTS"
            NAME="Ubuntu"
            VERSION_ID="22.04"
            VERSION="22.04.5 LTS (Jammy Jellyfish)"
            VERSION_CODENAME=jammy
            ID=ubuntu
            ID_LIKE=debian
            HOME_URL="https://www.ubuntu.com/"
            SUPPORT_URL="https://help.ubuntu.com/"
            BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
            PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
            UBUNTU_CODENAME=jammy
        """

        self.os_release_locations = [pathlib.Path("/etc/os-release"), pathlib.Path("/usr/lib/os-release")]

    def test_os_release_for_alpine(self):
        for os_release_location in self.os_release_locations:
            for alpine_text in self.alpine_texts:
                with (
                    self.subTest("os=alpine", text=alpine_text),
                    unittest.mock.patch("platform.system", return_value="Linux"),
                    pyfakefs.Patcher() as patcher,
                ):
                    assert patcher.fs is not None
                    patcher.fs.create_file(os_release_location, contents=alpine_text)
                    self.assertEqual(get_os(), "alpine")

    def test_os_release_for_generic_linux(self):
        for os_release_location in self.os_release_locations:
            with (
                self.subTest("os=ubuntu", text=self.ubuntu_text),
                unittest.mock.patch("platform.system", return_value="Linux"),
                pyfakefs.Patcher() as patcher,
            ):
                assert patcher.fs is not None
                patcher.fs.create_file(os_release_location, contents=self.ubuntu_text)
                self.assertEqual(get_os(), "linux")

    def test_os_release_does_not_exist(self):
        with (
            self.subTest("os_release does not exist"),
            unittest.mock.patch("platform.system", return_value="Linux"),
            pyfakefs.Patcher(),
        ):
            self.assertFalse(pathlib.Path("/etc/os-release").exists())
            self.assertFalse(pathlib.Path("/usr/lib/os-release").exists())
            self.assertEqual(get_os(), "linux")


class TestCalculateChecksum(unittest.TestCase):
    def test_calculate_checksum(self):
        self.assertEqual(
            calculate_checksum(BytesIO(b"test")), "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
        )
        self.assertEqual(
            calculate_checksum(BytesIO(b"test test")),
            "03ffdf45276dd38ffac79b0e9c6c14d89d9113ad783d5922580f4c66a3305591",
        )
