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
import typing
from dataclasses import dataclass

import requests
import requests.auth

from typing import Optional
from pysonar_scanner.configuration import Configuration
from pysonar_scanner.exceptions import MissingKeyException, SonarQubeApiException
from pysonar_scanner.utils import Os, Arch, remove_trailing_slash


@dataclass(frozen=True)
class SQVersion:
    parts: list[str]

    def __get_part(self, index: int) -> int:
        if index >= len(self.parts):
            return 0
        part = self.parts[index]
        if not part.isdigit():
            return 0
        return int(part)

    def major(self) -> int:
        return self.__get_part(0)

    def minor(self) -> int:
        return self.__get_part(1)

    def does_support_bootstrapping(self) -> bool:
        if len(self.parts) == 0:
            return False

        return self.major() > MIN_SUPPORTED_SQ_VERSION.major() or (
            self.major() == MIN_SUPPORTED_SQ_VERSION.major() and self.minor() >= MIN_SUPPORTED_SQ_VERSION.minor()
        )

    def __str__(self) -> str:
        return ".".join(self.parts)

    @staticmethod
    def from_str(version: str) -> "SQVersion":
        return SQVersion(version.split("."))


MIN_SUPPORTED_SQ_VERSION: SQVersion = SQVersion.from_str("10.6")


@dataclass(frozen=True)
class BaseUrls:
    base_url: str
    api_base_url: str
    is_sonar_qube_cloud: bool

    def __post_init__(self):
        object.__setattr__(self, "base_url", remove_trailing_slash(self.base_url))
        object.__setattr__(self, "api_base_url", remove_trailing_slash(self.api_base_url))


@dataclass(frozen=True)
class JRE:
    id: str
    filename: str
    sha256: str
    java_path: str
    os: str
    arch: str
    download_url: Optional[str]

    @staticmethod
    def from_dict(dict: dict) -> "JRE":
        try:
            return JRE(
                id=dict["id"],
                filename=dict["filename"],
                sha256=dict["sha256"],
                java_path=dict["javaPath"],
                os=dict["os"],
                arch=dict["arch"],
                download_url=dict.get("downloadUrl", None),
            )
        except KeyError as e:
            raise MissingKeyException(f"Missing key in dictionary {dict}") from e


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


@dataclass(frozen=True)
class EngineInfo:
    filename: str
    sha256: str


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

    def get_analysis_engine(self) -> EngineInfo:
        try:
            res = requests.get(
                f"{self.base_urls.api_base_url}/analysis/engine", headers={"Accept": "application/json"}, auth=self.auth
            )
            res.raise_for_status()
            json = res.json()
            if "filename" not in json or "sha256" not in json:
                raise SonarQubeApiException("Invalid response from the server")
            return EngineInfo(filename=json["filename"], sha256=json["sha256"])
        except requests.RequestException as e:
            raise SonarQubeApiException("Error while fetching the analysis engine information") from e

    def download_analysis_engine(self, handle: typing.BinaryIO) -> None:
        """
        This method can raise a SonarQubeApiException if the server doesn't respond successfully.
        Alternative, if the file IO fails, an IOError or OSError can be raised.
        """

        try:
            res = requests.get(
                f"{self.base_urls.api_base_url}/analysis/engine",
                headers={"Accept": "application/octet-stream"},
                auth=self.auth,
            )
            self.__download_file(res, handle)
        except requests.RequestException as e:
            raise SonarQubeApiException("Error while fetching the analysis engine") from e

    def get_analysis_jres(self, os: Optional[Os] = None, arch: Optional[Arch] = None) -> list[JRE]:
        try:
            params = {
                "os": os.value if os else None,
                "arch": arch.value if arch else None,
            }
            res = requests.get(
                f"{self.base_urls.api_base_url}/analysis/jres",
                auth=self.auth,
                headers={"Accept": "application/json"},
                params=params,
            )
            res.raise_for_status()
            json_array = res.json()
            return [JRE.from_dict(jre) for jre in json_array]
        except (requests.RequestException, MissingKeyException) as e:
            raise SonarQubeApiException("Error while fetching the analysis version") from e

    def download_analysis_jre(self, id: str, handle: typing.BinaryIO) -> None:
        """
        This method can raise a SonarQubeApiException if the server doesn't respond successfully.
        Alternative, if the file IO fails, an IOError or OSError can be raised.
        """

        try:
            res = requests.get(
                f"{self.base_urls.api_base_url}/analysis/jres/{id}",
                headers={"Accept": "application/octet-stream"},
                auth=self.auth,
            )
            self.__download_file(res, handle)
        except requests.RequestException as e:
            raise SonarQubeApiException("Error while fetching the JRE") from e

    def __download_file(self, res: requests.Response, handle: typing.BinaryIO) -> None:
        res.raise_for_status()
        for chunk in res.iter_content(chunk_size=128):
            handle.write(chunk)
