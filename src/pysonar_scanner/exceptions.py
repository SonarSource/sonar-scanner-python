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


from dataclasses import dataclass
import logging

EXCEPTION_RETURN_CODE = 1


@dataclass
class MissingProperty:
    property: str
    cli_arg: str


class MissingPropertyException(Exception):
    @staticmethod
    def from_missing_keys(*properties: MissingProperty) -> "MissingPropertyException":
        missing_properties = ", ".join([f"{prop.property} ({prop.cli_arg})" for prop in properties])
        return MissingPropertyException(f"Missing required properties: {missing_properties}")


class SonarQubeApiException(Exception):
    pass


class SQTooOldException(Exception):
    pass


class InconsistentConfiguration(Exception):
    pass


class ChecksumException(Exception):
    pass


class UnexpectedCliArgument(Exception):
    pass


class JreProvisioningException(Exception):
    pass


class NoJreAvailableException(JreProvisioningException):
    pass


class UnsupportedArchiveFormat(JreProvisioningException):
    pass


def log_error(e: Exception):
    logger = logging.getLogger()
    is_debug_level = logger.getEffectiveLevel() <= logging.DEBUG

    logger.error(str(e), exc_info=is_debug_level)

    return EXCEPTION_RETURN_CODE
