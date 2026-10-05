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

from typing import Any

from pysonar_scanner.exceptions import InconsistentConfiguration


def parse_bool(value: bool | str) -> bool:
    """Parse a boolean without treating nonempty strings such as 'false' as true."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
    raise ValueError("Expected 'true' or 'false'")


def get_boolean_property(config: dict[str, Any], key: str) -> bool:
    try:
        return parse_bool(config.get(key, False))
    except ValueError as e:
        raise InconsistentConfiguration(f"Invalid boolean value for '{key}': expected true or false.") from e
