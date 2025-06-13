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
from unittest.mock import patch

from pysonar_scanner.utils import (
    Arch,
    Os,
    get_arch,
    get_os,
    remove_trailing_slash,
    calculate_checksum,
    extract_tar,
)


class TestUtils(unittest.TestCase):
    def test_removing_trailinlg_slash(self):
        self.assertEqual(remove_trailing_slash("test/"), "test")
        self.assertEqual(remove_trailing_slash(" test/ "), "test")
        self.assertEqual(remove_trailing_slash(" test / "), "test")
        self.assertEqual(remove_trailing_slash("test"), "test")

    def test_get_os(self):
        with (
            self.subTest("os=Windows"),
            patch("platform.system", return_value="Windows"),
        ):
            self.assertEqual(get_os(), Os.WINDOWS)

        with self.subTest("os=Darwin"), patch("platform.system", return_value="Darwin"):
            self.assertEqual(get_os(), Os.MACOS)

    def test_get_arch(self):
        x64_machine_strs = ["amd64", "AmD64", "x86_64", "X86_64"]
        for machine_str in x64_machine_strs:
            with (
                self.subTest("amd64", machine_str=machine_str),
                patch("platform.machine", return_value=machine_str),
            ):
                self.assertEqual(get_arch(), Arch.X64)
        arm_machine_strs = ["arm64", "ARm64"]
        for machine_str in arm_machine_strs:
            with (
                self.subTest("arm", machine_str=machine_str),
                patch("platform.machine", return_value=machine_str),
            ):
                self.assertEqual(get_arch(), Arch.AARCH64)


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
                    patch("platform.system", return_value="Linux"),
                    _mock_os_release({os_release_location: alpine_text}),
                ):
                    self.assertEqual(get_os(), Os.ALPINE)

    def test_os_release_for_generic_linux(self):
        for os_release_location in self.os_release_locations:
            with (
                self.subTest("os=ubuntu", text=self.ubuntu_text),
                patch("platform.system", return_value="Linux"),
                _mock_os_release({os_release_location: self.ubuntu_text}),
            ):
                self.assertEqual(get_os(), Os.LINUX)

    def test_os_release_does_not_exist(self):
        with (
            self.subTest("os_release does not exist"),
            patch("platform.system", return_value="Linux"),
            _mock_os_release({}),
        ):
            self.assertFalse(pathlib.Path("/etc/os-release").exists())
            self.assertFalse(pathlib.Path("/usr/lib/os-release").exists())
            self.assertEqual(get_os(), Os.LINUX)


class TestCalculateChecksum(unittest.TestCase):
    def test_calculate_checksum(self):
        self.assertEqual(
            calculate_checksum(BytesIO(b"test")), "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
        )
        self.assertEqual(
            calculate_checksum(BytesIO(b"test test")),
            "03ffdf45276dd38ffac79b0e9c6c14d89d9113ad783d5922580f4c66a3305591",
        )


# ---------------------------------------------------------------------------
# Helper utilities used internally by the tests
# ---------------------------------------------------------------------------


def _mock_os_release(paths_to_contents: dict[pathlib.Path, str]):
    """Context manager that patches pathlib.Path.exists/read_text for given paths."""

    def _exists(self: pathlib.Path) -> bool:  # noqa: D401
        return self in paths_to_contents

    def _read_text(self: pathlib.Path) -> str:  # noqa: D401
        if self not in paths_to_contents:
            raise FileNotFoundError(self)
        return paths_to_contents[self]

    return unittest.mock.patch.multiple(
        pathlib.Path,
        exists=_exists,
        read_text=_read_text,
    )


class TestExtractTar(unittest.TestCase):
    def setUp(self):
        self.test_path = pathlib.Path("/fake/path/archive.tar.gz")
        self.test_target_dir = pathlib.Path("/fake/target/dir")

    @unittest.mock.patch("tarfile.open")
    @unittest.mock.patch("sys.version_info", (3, 12, 0))
    def test_extract_tar_python_3_12_or_higher(self, mock_open):
        mock_tar = unittest.mock.MagicMock()
        mock_open.return_value.__enter__.return_value = mock_tar

        extract_tar(self.test_path, self.test_target_dir)

        mock_open.assert_called_once_with(self.test_path, "r:gz")
        mock_tar.extractall.assert_called_once_with(self.test_target_dir, filter="data")

    @unittest.mock.patch("tarfile.open")
    @unittest.mock.patch("sys.version_info", (3, 11, 0))
    def test_extract_tar_python_older_than_3_12(self, mock_open):
        mock_tar = unittest.mock.MagicMock()
        mock_open.return_value.__enter__.return_value = mock_tar

        extract_tar(self.test_path, self.test_target_dir)

        mock_open.assert_called_once_with(self.test_path, "r:gz")
        mock_tar.extractall.assert_called_once_with(self.test_target_dir)
