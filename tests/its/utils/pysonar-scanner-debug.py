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
"""
This module is the entry point for debugging the pysonar scanner in the its.
The pysonar-scanner-debug is started with the working directory set to the root of the project, so that python
(and pydebug by extension) can find the pysonar-scanner-debug module. However, since the scanner should run in the
 analyzed project, the working directory is changed to the root of the analyzed project before running the scanner.

The pysonar-scanner-debug expects the PYSONAR_SCANNER_DEBUG_WORKDIR environment variable to be set to the directory
where the scanner should be run. This is set to the directory containing the sources to be analyzed.
"""

import os
import sys
from pysonar_scanner.__main__ import scan

if __name__ == "__main__":
    workdir = os.getenv("PYSONAR_SCANNER_DEBUG_WORKDIR", ".")
    os.chdir(workdir)
    sys.exit(scan())
