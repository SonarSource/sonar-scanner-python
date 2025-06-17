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
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock, patch

from pyfakefs.fake_filesystem_unittest import TestCase
from pysonar_scanner.configuration.pyproject_toml import TomlConfigurationLoader
from pysonar_scanner.configuration.coveragerc_loader import CoverageRCConfigurationLoader


class TestCoverageRcFile(TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_load_coverage_file(self):
        self.fs.create_file(
            ".coveragerc",
            contents="""
            [run]
            omit =
                */.local/*
                /usr/*
                utils/tirefire.py
            """,
        )
        properties = CoverageRCConfigurationLoader.load_exclusion_properties(Path("."))

        self.assertEqual(properties["sonar.coverage.exclusions"], "*/.local/*, /usr/*, utils/tirefire.py")

    @patch("pysonar_scanner.configuration.coveragerc_loader.logging")
    def test_load_missing_file(self, mock_logging):
        properties = CoverageRCConfigurationLoader.load_exclusion_properties(Path("."))
        self.assertEqual(len(properties), 0)
        mock_logging.debug.assert_called_with("Coverage file not found: .coveragerc")

    @patch("pysonar_scanner.configuration.coveragerc_loader.logging")
    def test_load_without_run_section(self, mock_logging):
        self.fs.create_file(
            ".coveragerc",
            contents="""
                    [something_else]
                    """,
        )
        properties = CoverageRCConfigurationLoader.load_exclusion_properties(Path("."))
        self.assertEqual(len(properties), 0)
        mock_logging.debug.assert_called_with("Coverage file has no exclusion properties")

    @patch("pysonar_scanner.configuration.coveragerc_loader.logging")
    def test_load_malformed_file(self, mock_logging):
        self.fs.create_file(
            ".coveragerc",
            contents="""
                    [run
                    omit = 
                    """,
        )
        properties = CoverageRCConfigurationLoader.load_exclusion_properties(Path("."))
        self.assertEqual(len(properties), 0)
