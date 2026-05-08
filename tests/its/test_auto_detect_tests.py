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
import pytest
from tests.its.utils.sonarqube_client import SonarQubeClient
from tests.its.utils.cli_client import CliClient


pytestmark = pytest.mark.its


def test_auto_detect_tests_from_pyproject_toml(sonarqube_client: SonarQubeClient, cli: CliClient):
    """sonar.tests should be inferred from [tool.pytest.ini_options] testpaths in pyproject.toml."""
    process = cli.run_analysis(sources_dir="with-tests", params=["--verbose"])
    assert process.returncode == 0, process.stdout

    task = sonarqube_client.get_latest_ce_task()
    projects = sonarqube_client.search_projects()
    project_keys = [p["key"] for p in projects]

    assert task is not None and task["status"] == "SUCCESS", (
        f"SonarQube CE task did not succeed.\n"
        f"Task: {task}\n"
        f"Existing projects: {project_keys}\n"
        f"Scanner output:\n{process.stdout}"
    )
    assert task.get("componentKey") == "with-tests", (
        f"CE task succeeded for wrong component '{task.get('componentKey')}', expected 'with-tests'.\n"
        f"Existing projects: {project_keys}\n"
        f"Scanner output:\n{process.stdout}"
    )

    test_files = sonarqube_client.get_project_test_files("with-tests")
    test_file_paths = [c["path"] for c in test_files]
    assert any("test_app.py" in p for p in test_file_paths), (
        f"Expected tests/test_app.py to be classified as a test file in SonarQube — "
        f"sonar.tests auto-detection may not have run correctly.\n"
        f"Test files found: {test_file_paths}\n"
        f"Scanner output:\n{process.stdout}"
    )
