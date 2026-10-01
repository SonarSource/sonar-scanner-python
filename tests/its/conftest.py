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
from time import monotonic, sleep

import pytest
from requests.exceptions import ConnectionError, HTTPError, Timeout

from tests.its.utils.cli_client import CliClient
from tests.its.utils.sonarqube_client import SonarQubeClient


def check_health(sonarqube_client: SonarQubeClient) -> bool:
    try:
        return sonarqube_client.get_system_health()["health"] == "GREEN"
    except (ConnectionError, HTTPError, Timeout):
        return False


@pytest.fixture(scope="session")
def sonarqube_client() -> SonarQubeClient:
    """Ensure that sonarqube service is up and responsive."""
    url = "http://localhost:9000"
    sonarqube_client = SonarQubeClient(url)
    deadline = monotonic() + 120
    while not check_health(sonarqube_client):
        if monotonic() >= deadline:
            pytest.fail(f"SonarQube at {url} did not become ready within 120 seconds.")
        print("Waiting for SonarQube to be up")
        sleep(10)
    status = sonarqube_client.get_system_status()["status"]
    assert status == "UP"
    return sonarqube_client


def pytest_addoption(parser):
    parser.addoption("--debug-its", action="store_true", default=False, help="run scanner")


@pytest.fixture
def is_debugging(pytestconfig) -> bool:
    return pytestconfig.getoption("--debug-its")


@pytest.fixture
def cli(sonarqube_client: SonarQubeClient, is_debugging: bool, caplog: pytest.CaptureFixture) -> CliClient:
    return CliClient(sonarqube_client, is_debugging, caplog)
