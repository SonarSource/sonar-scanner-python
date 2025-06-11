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
import sys


class LevelFilter(logging.Filter):
    def __init__(self, level):
        super().__init__()
        self.__level = level

    def filter(self, record):
        return record.levelno < self.__level


def setup() -> None:
    logger = logging.getLogger()

    non_error_handler = logging.StreamHandler(sys.stdout)
    non_error_handler.setLevel(logging.DEBUG)
    non_error_handler.addFilter(LevelFilter(logging.ERROR))

    error_handler = logging.StreamHandler(sys.stderr)
    error_handler.setLevel(logging.ERROR)

    formatter = logging.Formatter("%(levelname)s: %(message)s")
    non_error_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)

    logger.addHandler(non_error_handler)
    logger.addHandler(error_handler)


def configure_logging_level(verbose: bool) -> None:
    logging.getLogger().setLevel(logging.DEBUG if verbose else logging.INFO)
