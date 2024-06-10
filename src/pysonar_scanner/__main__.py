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
from pysonar_scanner.configuration import Configuration
from pysonar_scanner.environment import Environment
from pysonar_scanner.logger import ApplicationLogger


def scan():
    log = ApplicationLogger.get_logger()
    cfg = Configuration()
    try:
        cfg.setup()
        env = Environment(cfg)
        env.scan()
    except Exception as e:
        log.exception("Error during SonarScanner execution: %s", str(e))
        if not cfg.is_debug():
            log.info("Re-run SonarScanner using the -X switch to enable full debug logging.")


if __name__ == "__main__":
    scan()
