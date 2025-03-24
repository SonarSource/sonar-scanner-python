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
import os
import pytest
import pytest_docker.plugin as docker
from utils.cli_client import CliClient
from utils.sonarqube_client import SonarQubeClient
from requests.exceptions import ConnectionError, HTTPError


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig: pytest.Config):
    return pytestconfig.rootpath / "compose.yaml"


def check_health(sonarqube_client: SonarQubeClient) -> bool:
    try:
        return sonarqube_client.get_system_health()["health"] == "GREEN"
    except (ConnectionError, HTTPError):
        return False


if "CIRRUS_OS" in os.environ:
    from time import sleep

    @pytest.fixture(scope="session")
    def sonarqube_client() -> SonarQubeClient:
        """Ensure that sonarqube service is up and responsive."""
        url = "http://localhost:9000"
        sonarqube_client = SonarQubeClient(url)
        while not check_health(sonarqube_client):
            print("Waiting for SonarQube to be up")
            sleep(10)
        status = sonarqube_client.get_system_status()["status"]
        assert status == "UP"
        return sonarqube_client

else:

    @pytest.fixture(scope="session")
    def sonarqube_client(docker_ip: str, docker_services: docker.Services) -> SonarQubeClient:
        """Ensure that sonarqube service is up and responsive."""
        port = docker_services.port_for("sonarqube", 9000)
        url = f"http://{docker_ip}:{port}"
        sonarqube_client = SonarQubeClient(url)
        docker_services.wait_until_responsive(timeout=120.0, pause=5, check=lambda: check_health(sonarqube_client))
        status = sonarqube_client.get_system_status()["status"]
        assert status == "UP"
        return sonarqube_client


@pytest.fixture
def cli(sonarqube_client: SonarQubeClient) -> CliClient:
    return CliClient(sonarqube_client)
