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
from dataclasses import dataclass
from pysonar_scanner.configuration import Configuration
from pysonar_scanner.utils import SQVersion, remove_trailing_slash
import requests


@dataclass(frozen=True)
class BaseUrls:
    base_url: str
    api_base_url: str
    is_sonar_qube_cloud: bool

    def __post_init__(self):
        object.__setattr__(self, "base_url", remove_trailing_slash(self.base_url))
        object.__setattr__(self, "api_base_url", remove_trailing_slash(self.api_base_url))


def get_base_urls(config: Configuration) -> BaseUrls:
    def is_sq_cloud_url(sonar_host_url: str) -> bool:
        sq_cloud_url = config.sonar.scanner.sonarcloud_url.strip() or "https://sonarcloud.io"
        return remove_trailing_slash(sonar_host_url) == remove_trailing_slash(sq_cloud_url)

    def is_blank(str) -> bool:
        return str.strip() == ""

    def region_with_dot(region: str) -> str:
        return region + "." if not is_blank(region) else ""

    sonar_host_url = remove_trailing_slash(config.sonar.host_url)
    if is_blank(sonar_host_url) or is_sq_cloud_url(sonar_host_url):
        region = region_with_dot(config.sonar.region)
        sonar_host_url = config.sonar.scanner.sonarcloud_url or f"https://{region}sonarcloud.io"
        api_base_url = config.sonar.scanner.api_base_url or f"https://api.{region}sonarcloud.io"
        return BaseUrls(base_url=sonar_host_url, api_base_url=api_base_url, is_sonar_qube_cloud=True)
    else:
        api_base_url = config.sonar.scanner.api_base_url or f"{sonar_host_url}/api/v2"
        return BaseUrls(base_url=sonar_host_url, api_base_url=api_base_url, is_sonar_qube_cloud=False)


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = f"Bearer {self.token}"
        return r


class SonarQubeApiException(Exception):
    pass


class SonarQubeApi:
    def __init__(self, base_urls: BaseUrls, token: str):
        self.base_urls = base_urls
        self.auth = BearerAuth(token)

    def is_sonar_qube_cloud(self) -> bool:
        return self.base_urls.is_sonar_qube_cloud

    def get_analysis_version(self) -> SQVersion:
        try:
            res = requests.get(f"{self.base_urls.api_base_url}/analysis/version", auth=self.auth)
            if res.status_code != 200:
                res = requests.get(f"{self.base_urls.base_url}/api/server/version", auth=self.auth)

            res.raise_for_status()
            return SQVersion.from_str(res.text)
        except requests.RequestException as e:
            raise SonarQubeApiException("Error while fetching the analysis version") from e
