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
        fix_message = (
            "You can provide these properties using one of the following methods:\n"
            "- Command line arguments (e.g., --sonar.projectKey=myproject)\n"
            "- Environment variables (e.g., SONAR_PROJECTKEY=myproject)\n"
            "- Properties file (sonar-project.properties)\n"
            "- Project configuration files (e.g., build.gradle, pom.xml)"
        )
        return MissingPropertyException(f"Missing required properties: {missing_properties}\n\n{fix_message}")


class SonarQubeApiException(Exception):
    pass


class SonarQubeApiUnauthroizedException(SonarQubeApiException):
    @staticmethod
    def create_default(server_url: str) -> "SonarQubeApiUnauthroizedException":
        return SonarQubeApiUnauthroizedException(
            f'The provided token is invalid for the server at "{server_url}". Please check that both the token and the server URL are correct.'
        )


class SQTooOldException(Exception):
    pass


class InconsistentConfiguration(Exception):
    pass


class ChecksumException(Exception):
    @staticmethod
    def create(what: str) -> "ChecksumException":
        return ChecksumException(f"Checksum mismatch. The downloaded {what} is corrupted.")


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

    if is_debug_level:
        logger.error("The following exception occured while running the analysis", exc_info=True)
    else:
        logger.error(str(e), exc_info=False)
        logger.info("For more details, please enable debug logging by passing the --verbose option.")

    return EXCEPTION_RETURN_CODE
