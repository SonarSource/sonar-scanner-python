#
# Sonar Scanner Python
# Copyright (C) 2011-2023 SonarSource SA.
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
import sys

from py_sonar_scanner.configuration import Configuration
from py_sonar_scanner.environment import Environment
from py_sonar_scanner.logger import ApplicationLogger


def scan():
    log = ApplicationLogger.get_logger()
    debug_enabled = False
    try:
        cfg = Configuration()
        cfg.setup()
        debug_enabled = cfg.is_debug()

        env = Environment(cfg)
        env.setup()
        env.scanner().scan()
        env.cleanup()
    except Exception as e:
        log.exception("Error during SonarScanner execution: %s", str(e))
        if not debug_enabled:
            log.info("Re-run SonarScanner using the -X switch to enable full debug logging.")


if __name__ == "__main__":
    scan()
