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

import unittest

from pysonar_scanner.configuration.properties import (
    Property,
    SONAR_HOST_URL,
    SONAR_TOKEN,
    SONAR_VERBOSE,
    SONAR_SCANNER_APP_VERSION,
    SONAR_SCANNER_SOCKET_TIMEOUT,
    SONAR_SCANNER_PROXY_PASSWORD,
    SONAR_SCANNER_INTERNAL_DUMP_TO_FILE,
    SONAR_PROJECT_KEY,
    SONAR_PROJECT_BASE_DIR,
    PROPERTIES,
)


class TestProperties(unittest.TestCase):
    def test_python_name_conversion(self):
        """Test conversion of property names to Python-style kebab-case names"""
        test_cases = [
            # Simple properties
            (SONAR_HOST_URL, "sonar.host.url"),
            (SONAR_TOKEN, "sonar.token"),
            (SONAR_VERBOSE, "sonar.verbose"),
            # CamelCase properties
            (SONAR_SCANNER_APP_VERSION, "sonar.scanner.app-version"),
            (SONAR_SCANNER_SOCKET_TIMEOUT, "sonar.scanner.socket-timeout"),
            (SONAR_SCANNER_PROXY_PASSWORD, "sonar.scanner.proxy-password"),
            # Complex properties
            (SONAR_SCANNER_INTERNAL_DUMP_TO_FILE, "sonar.scanner.internal.dump-to-file"),
            (SONAR_PROJECT_KEY, "sonar.project-key"),
            (SONAR_PROJECT_BASE_DIR, "sonar.project-base-dir"),
        ]

        for name, expected_python_name in test_cases:
            # Find property in PROPERTIES list
            prop = next((p for p in PROPERTIES if p.name == name), None)
            if prop:
                self.assertEqual(
                    prop.python_name(),
                    expected_python_name,
                    f"Failed to convert {name} to Python name, got {prop.python_name()}",
                )
            else:
                # Create test property if not in list
                prop = Property(name=name, default_value=None)
                self.assertEqual(
                    prop.python_name(),
                    expected_python_name,
                    f"Failed to convert {name} to Python name, got {prop.python_name()}",
                )

    def test_env_variable_name_conversion(self):
        """Test conversion of property names to environment variable format"""
        test_cases = [
            # Simple properties
            (SONAR_HOST_URL, "SONAR_HOST_URL"),
            (SONAR_TOKEN, "SONAR_TOKEN"),
            (SONAR_VERBOSE, "SONAR_VERBOSE"),
            # CamelCase properties
            (SONAR_SCANNER_APP_VERSION, "SONAR_SCANNER_APP_VERSION"),
            (SONAR_SCANNER_SOCKET_TIMEOUT, "SONAR_SCANNER_SOCKET_TIMEOUT"),
            (SONAR_SCANNER_PROXY_PASSWORD, "SONAR_SCANNER_PROXY_PASSWORD"),
            # Complex properties
            (SONAR_SCANNER_INTERNAL_DUMP_TO_FILE, "SONAR_SCANNER_INTERNAL_DUMP_TO_FILE"),
            (SONAR_PROJECT_KEY, "SONAR_PROJECT_KEY"),
            (SONAR_PROJECT_BASE_DIR, "SONAR_PROJECT_BASE_DIR"),
        ]

        for name, expected_env_name in test_cases:
            # Find property in PROPERTIES list
            prop = next((p for p in PROPERTIES if p.name == name), None)
            if prop:
                self.assertEqual(
                    prop.env_variable_name(),
                    expected_env_name,
                    f"Failed to convert {name} to environment variable name, got {prop.env_variable_name()}",
                )
            else:
                # Create test property if not in list
                prop = Property(name=name, default_value=None)
                self.assertEqual(
                    prop.env_variable_name(),
                    expected_env_name,
                    f"Failed to convert {name} to environment variable name, got {prop.env_variable_name()}",
                )
