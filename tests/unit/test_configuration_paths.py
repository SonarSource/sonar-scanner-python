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
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


def run_dry_run(directory: Path, args: list[str], environment: dict[str, str]) -> subprocess.CompletedProcess[str]:
    env = {key: value for key, value in os.environ.items() if not key.startswith("SONAR_")}
    env.update(environment)
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[2] / "src")
    return subprocess.run(
        [sys.executable, "-c", "from pysonar_scanner.__main__ import main; main()", "--dry-run", *args],
        cwd=directory,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )


@pytest.mark.parametrize("source", ["environment", "json", "cli"])
def test_project_base_dir_selects_configuration_before_dry_run(tmp_path: Path, source: str):
    (tmp_path / "pyproject.toml").write_text('[tool.sonar]\nproject-key = "wrong-key"\n', encoding="utf-8")
    project_dir = tmp_path / "selected-project"
    project_dir.mkdir()
    (project_dir / "pyproject.toml").write_text(
        '[tool.sonar]\nproject-key = "selected-key"\nproject-name = "Selected project"\n'
        '[tool.pytest.ini_options]\ntestpaths = ["specs"]\n',
        encoding="utf-8",
    )
    (project_dir / "specs").mkdir()
    args = []
    if source == "environment":
        environment = {"SONAR_PROJECT_BASE_DIR": "selected-project"}
    elif source == "json":
        environment = {"SONAR_SCANNER_JSON_PARAMS": json.dumps({"sonar.projectBaseDir": "selected-project"})}
    else:
        environment = {"SONAR_PROJECT_BASE_DIR": "ignored-project"}
        args = ["--sonar-project-base-dir", "selected-project"]

    process = run_dry_run(tmp_path, args, environment)

    assert process.returncode == 0, process.stdout + process.stderr
    assert "Project Key: selected-key" in process.stdout
    assert "Project Name: Selected project" in process.stdout
    assert "Tests: specs" in process.stdout
    assert "wrong-key" not in process.stdout


def test_explicit_relative_toml_path_is_relative_to_invocation_directory(tmp_path: Path):
    for directory, key in (("config", "selected-key"), ("project/config", "wrong-key")):
        config_dir = tmp_path / directory
        config_dir.mkdir(parents=True)
        (config_dir / "pyproject.toml").write_text(f'[tool.sonar]\nproject-key = "{key}"\n', encoding="utf-8")

    process = run_dry_run(
        tmp_path,
        ["--sonar-project-base-dir", "project", "--toml-path", "config/pyproject.toml"],
        {},
    )

    assert process.returncode == 0, process.stdout + process.stderr
    assert "Project Key: selected-key" in process.stdout
    assert "wrong-key" not in process.stdout
