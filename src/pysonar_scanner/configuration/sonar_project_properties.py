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
import logging
from pathlib import Path
from typing import Dict
import os
from jproperties import Properties


def load(base_dir: Path) -> Dict[str, str]:
    filepath = base_dir / "sonar-project.properties"
    if not os.path.isfile(filepath):
        logging.debug(f"no sonar-project.properties file found at {filepath}")
        return {}

    logging.debug(f"sonar-project.properties loaded from {filepath}")
    props = Properties()
    with open(filepath, "rb") as f:
        props.load(f)

    return {key: value.data for key, value in props.items() if value.data is not None}
