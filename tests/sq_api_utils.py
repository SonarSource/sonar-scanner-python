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
import contextlib
from typing import Optional
from typing_extensions import Self
from pysonar_scanner.api import BaseUrls, SonarQubeApi
import responses


def get_sq_server() -> SonarQubeApi:
    return SonarQubeApi(
        base_urls=BaseUrls(base_url="http://sq.home", api_base_url="http://sq.home/api/v2", is_sonar_qube_cloud=False),
        token="<fake_token>",
    )


def get_sq_cloud() -> SonarQubeApi:
    return SonarQubeApi(
        base_urls=BaseUrls(
            base_url="http://sonarcloud.io", api_base_url="http://api.sonarcloud.io", is_sonar_qube_cloud=True
        ),
        token="<fake_token>",
    )


class SQApiMocker:
    def __init__(self, base_url: str = "http://sq.home", rsps: Optional[responses.RequestsMock] = None):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v2"
        self.rsps = rsps or responses

    def mock_analysis_version(self, version: str = "", status: int = 200) -> Self:
        self.rsps.get(url=f"{self.api_url}/analysis/version", body=version, status=status)
        return self

    def mock_server_version(self, version: str = "", status: int = 200) -> Self:
        self.rsps.get(url=f"{self.base_url}/api/server/version", body=version, status=status)
        return self


@contextlib.contextmanager
def sq_api_mocker(base_url: str = "http://sq.home"):
    with responses.RequestsMock() as rsps:
        yield SQApiMocker(base_url=base_url, rsps=rsps)
