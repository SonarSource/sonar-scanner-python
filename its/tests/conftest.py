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
from utils.sonarqube_client import SonarQubeClient
from requests.exceptions import ConnectionError


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return os.path.join(str(pytestconfig.rootdir), "compose.yaml")


def check_health(sonarqube_client: SonarQubeClient) -> bool:
    try:
        response = sonarqube_client.get_system_health()
        if response.status_code == 200:
            data = response.json()
            return data["health"] == "GREEN"
    except ConnectionError:
        return False


if "CIRRUS_OS" in os.environ:
    @pytest.fixture(scope="session")
    def sonarqube_client() -> SonarQubeClient:
        """Ensure that sonarqube service is up and responsive."""
        url = f"http://localhost:9000"
        sonarqube_client = SonarQubeClient(url)
        return sonarqube_client
else:
    @pytest.fixture(scope="session")
    def sonarqube_client(docker_ip, docker_services) -> SonarQubeClient:
        """Ensure that sonarqube service is up and responsive."""
        port = docker_services.port_for("sonarqube", 9000)
        url = f"http://{docker_ip}:{port}"
        sonarqube_client = SonarQubeClient(url)
        docker_services.wait_until_responsive(
            timeout=120.0, pause=5, check=lambda: check_health(sonarqube_client)
        )
        response = sonarqube_client.get_system_status()
        assert response.status_code == 200
        status = response.json()["status"]
        assert status == "UP"
        return sonarqube_client
