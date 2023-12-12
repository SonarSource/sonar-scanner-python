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
import logging
from logging import Logger
from typing import Optional

class ApplicationLogger():

    _log: Optional[Logger] = None

    @classmethod
    def get_logger(cls) -> Logger:
        if not cls._log:
            cls._log = logging.getLogger("main")
            cls._setup_logger(cls._log)
        return cls._log 

    @staticmethod
    def _setup_logger(log: Logger):
        log.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.terminator = ""
        log.addHandler(handler)