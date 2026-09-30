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
from importlib import metadata
from unittest.mock import patch

from pysonar_scanner.version import UNKNOWN_VERSION, get_version


def test_get_version_from_package_metadata():
    with patch("pysonar_scanner.version.metadata.version", return_value="1.8.0"):
        assert get_version() == "1.8.0"


def test_get_version_when_metadata_is_unavailable():
    for failure in (metadata.PackageNotFoundError("pysonar"), OSError("unreadable metadata")):
        with patch("pysonar_scanner.version.metadata.version", side_effect=failure):
            assert get_version() == UNKNOWN_VERSION

    with patch("pysonar_scanner.version.metadata.version", return_value=""):
        assert get_version() == UNKNOWN_VERSION
