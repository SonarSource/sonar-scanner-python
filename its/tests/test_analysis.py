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
from utils.sonarqube_client import SonarQubeClient
from utils.cli_client import CliClient


def test_minimal_project(sonarqube_client: SonarQubeClient):
    process = CliClient().run_analysis(sonarqube_client, sources_dir="minimal")
    assert process.returncode == 0
    response = sonarqube_client.get_project_issues("minimal")
    data = response.json()
    assert len(data["issues"]) == 1
    analyses_data = sonarqube_client.get_project_analyses("minimal").json()
    latest_analysis_data = analyses_data['analyses'][0]
    assert latest_analysis_data['projectVersion'] == '1.2'


def test_minimal_project_read_poetry_data(sonarqube_client: SonarQubeClient):
    process = CliClient().run_analysis(sonarqube_client, params=["-read.project.config"], sources_dir="minimal")
    assert process.returncode == 0
    response = sonarqube_client.get_project_issues("minimal")
    data = response.json()
    assert len(data["issues"]) == 1
    analyses_data = sonarqube_client.get_project_analyses("minimal").json()
    latest_analysis_data = analyses_data['analyses'][0]
    assert latest_analysis_data['projectVersion'] == '1.5'


def test_minimal_project_unexpected_arg(sonarqube_client: SonarQubeClient):
    process = CliClient().run_analysis(sonarqube_client, params=["-unexpected"], sources_dir="minimal")
    assert process.returncode == 0
    assert "ERROR Unrecognized option: -unexpected" in process.stdout


def test_minimal_project_wrong_home(sonarqube_client: SonarQubeClient):
    process = CliClient().run_analysis(sonarqube_client, params=["-Dproject.home='unknown/path'"],
                                       sources_dir="minimal")
    assert process.returncode == 0
    assert "Project home must be an existing directory" in process.stdout
