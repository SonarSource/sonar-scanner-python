#
# Sonar Scanner Python
# Copyright (C) 2011-2026 SonarSource Sàrl
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
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

import pytest

from pysonar_scanner.__main__ import set_logging_options
from pysonar_scanner.configuration.properties import (
    SONAR_VERBOSE,
)
from pysonar_scanner.exceptions import InconsistentConfiguration


@pytest.mark.parametrize("value, expected_exit", [("false", 1), ("true", 0), ("invalid", 1)])
def test_dry_run_environment_value_controls_whether_analysis_is_skipped(tmp_path, value, expected_exit):
    env = {key: value for key, value in os.environ.items() if not key.startswith("SONAR")}
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[2] / "src")
    env["SONAR_SCANNER_DRY_RUN"] = value
    process = subprocess.run(
        [sys.executable, "-c", "from pysonar_scanner.__main__ import main; main()"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert process.returncode == expected_exit
    assert ("Running in DRY RUN mode" in process.stdout) is (value == "true")
    if value == "false":
        assert "Missing required properties" in process.stderr
    elif value == "invalid":
        assert "sonar.scanner.dryRun" in process.stderr
        assert "true or false" in process.stderr


def test_string_false_disables_verbose_logging():
    with patch("pysonar_scanner.__main__.app_logging.configure_logging_level") as configure:
        set_logging_options({SONAR_VERBOSE: "false"})
    configure.assert_called_once_with(verbose=False)


def test_invalid_verbosity_identifies_the_property():
    with pytest.raises(InconsistentConfiguration, match="sonar.verbose"):
        set_logging_options({SONAR_VERBOSE: "invalid"})
