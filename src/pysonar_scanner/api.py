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
from typing import Any, NoReturn, Optional

import requests
import requests.auth

from pysonar_scanner.configuration.properties import (
    SONAR_HOST_URL,
    SONAR_SCANNER_SONARCLOUD_URL,
    SONAR_SCANNER_API_BASE_URL,
    SONAR_REGION,
    Key,
)
from pysonar_scanner.utils import remove_trailing_slash, OsStr, ArchStr
from pysonar_scanner.exceptions import (
    SonarQubeApiException,
    InconsistentConfiguration,
    SonarQubeApiUnauthroizedException,
)

GLOBAL_SONARCLOUD_URL = "https://sonarcloud.io"
US_SONARCLOUD_URL = "https://sonarqube.us"

UNAUTHORIZED_STATUS_CODES = (401, 403)

ACCEPT_JSON = {"Accept": "application/json"}
ACCEPT_OCTET_STREAM = {"Accept": "application/octet-stream"}


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
    id: Optional[str]
    filename: str
    sha256: str
    java_path: str
    os: str
    arch: str
    download_url: Optional[str]

    @staticmethod
    def from_dict(dict: dict) -> "JRE":
        return JRE(
            id=dict.get("id", None),
            filename=dict["filename"],
            sha256=dict["sha256"],
            java_path=dict["javaPath"],
            os=dict["os"],
            arch=dict["arch"],
            download_url=dict.get("downloadUrl", None),
        )


@dataclass(frozen=True)
class ApiConfiguration:
    sonar_host_url: str
    sonar_scanner_sonarcloud_url: str
    sonar_scanner_api_base_url: str
    sonar_region: str


def to_api_configuration(config_dict: dict[Key, Any]) -> ApiConfiguration:
    return ApiConfiguration(
        sonar_host_url=config_dict.get(SONAR_HOST_URL, ""),
        sonar_scanner_sonarcloud_url=config_dict.get(SONAR_SCANNER_SONARCLOUD_URL, ""),
        sonar_scanner_api_base_url=config_dict.get(SONAR_SCANNER_API_BASE_URL, ""),
        sonar_region=config_dict.get(SONAR_REGION, ""),
    )


def get_base_urls(config_dict: dict[Key, Any]) -> BaseUrls:
    def is_sq_cloud_url(api_config: ApiConfiguration, sonar_host_url: str) -> bool:
        sq_cloud_url = api_config.sonar_scanner_sonarcloud_url or GLOBAL_SONARCLOUD_URL
        return remove_trailing_slash(sonar_host_url) in [remove_trailing_slash(sq_cloud_url), US_SONARCLOUD_URL]

    def is_blank(str) -> bool:
        return str.strip() == ""

    api_config: ApiConfiguration = to_api_configuration(config_dict)

    sonar_host_url = remove_trailing_slash(api_config.sonar_host_url)
    region = api_config.sonar_region
    if region and region != "us":
        raise InconsistentConfiguration(
            f"Invalid region '{region}'. Valid regions are: 'us'. "
            "Please check the 'sonar.region' property or the 'SONAR_REGION' environment variable."
        )
    if is_inconsistent_configuration(region, sonar_host_url):
        raise InconsistentConfiguration(
            "Inconsistent values for properties 'sonar.region' and 'sonar.host.url'. "
            + "Please only specify one of the two properties."
        )
    if is_blank(sonar_host_url) or is_sq_cloud_url(api_config, sonar_host_url):
        default_url = US_SONARCLOUD_URL if region == "us" else GLOBAL_SONARCLOUD_URL
        default_api_base_url = "https://api.sonarqube.us" if region == "us" else "https://api.sonarcloud.io"
        sonar_host_url = api_config.sonar_scanner_sonarcloud_url or default_url
        api_base_url = api_config.sonar_scanner_api_base_url or default_api_base_url
        return BaseUrls(base_url=sonar_host_url, api_base_url=api_base_url, is_sonar_qube_cloud=True)
    else:
        api_base_url = api_config.sonar_scanner_api_base_url or f"{sonar_host_url}/api/v2"
        return BaseUrls(base_url=sonar_host_url, api_base_url=api_base_url, is_sonar_qube_cloud=False)


def is_inconsistent_configuration(region, sonar_host_url):
    if not region or not sonar_host_url:
        return False
    if region == "us" and sonar_host_url.startswith(US_SONARCLOUD_URL):
        return False
    return True


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
    download_url: Optional[str] = None


class SonarQubeApi:
    def __init__(self, base_urls: BaseUrls, token: str):
        self.base_urls = base_urls
        self.auth = BearerAuth(token)

    def __raise_exception(self, exception: Exception) -> NoReturn:
        if (
            isinstance(exception, requests.RequestException)
            and exception.response is not None
            and exception.response.status_code in UNAUTHORIZED_STATUS_CODES
        ):
            raise SonarQubeApiUnauthroizedException.create_default(self.base_urls.base_url) from exception
        else:
            raise SonarQubeApiException("Error while fetching the analysis version") from exception

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
            self.__raise_exception(e)

    def get_analysis_engine(self) -> EngineInfo:
        try:
            res = requests.get(f"{self.base_urls.api_base_url}/analysis/engine", headers=ACCEPT_JSON, auth=self.auth)
            res.raise_for_status()
            json = res.json()
            if "filename" not in json or "sha256" not in json:
                raise SonarQubeApiException("Invalid response from the server")
            return EngineInfo(
                filename=json["filename"], sha256=json["sha256"], download_url=json.get("downloadUrl", None)
            )
        except requests.RequestException as e:
            self.__raise_exception(e)

    def download_analysis_engine(self, handle: typing.BinaryIO) -> None:
        """
        This method can raise a SonarQubeApiException if the server doesn't respond successfully.
        Alternative, if the file IO fails, an IOError or OSError can be raised.
        """
        try:
            res = requests.get(
                f"{self.base_urls.api_base_url}/analysis/engine",
                headers=ACCEPT_OCTET_STREAM,
                auth=self.auth,
            )
            self.__download_file(res, handle)
        except requests.RequestException as e:
            self.__raise_exception(e)

    def get_analysis_jres(self, os: OsStr, arch: ArchStr) -> list[JRE]:
        try:
            params = {"os": os, "arch": arch}
            res = requests.get(
                f"{self.base_urls.api_base_url}/analysis/jres",
                auth=self.auth,
                headers=ACCEPT_JSON,
                params=params,
            )
            res.raise_for_status()
            json_array = res.json()
            return [JRE.from_dict(jre) for jre in json_array]
        except (requests.RequestException, KeyError) as e:
            self.__raise_exception(e)

    def download_analysis_jre(self, id: str, handle: typing.BinaryIO) -> None:
        """
        This method can raise a SonarQubeApiException if the server doesn't respond successfully.
        Alternative, if the file IO fails, an IOError or OSError can be raised.
        """

        try:
            res = requests.get(
                f"{self.base_urls.api_base_url}/analysis/jres/{id}",
                headers=ACCEPT_OCTET_STREAM,
                auth=self.auth,
            )
            self.__download_file(res, handle)
        except requests.RequestException as e:
            self.__raise_exception(e)

    def download_file_from_url(self, url: str, handle: typing.BinaryIO) -> None:
        """
        This method can raise a SonarQubeApiException if the server doesn't respond successfully.
        Alternative, if the file IO fails, an IOError or OSError can be raised.
        """
        try:
            res = requests.get(
                url,
                headers=ACCEPT_OCTET_STREAM,
            )
            self.__download_file(res, handle)
        except requests.RequestException as e:
            self.__raise_exception(e)

    def __download_file(self, res: requests.Response, handle: typing.BinaryIO) -> None:
        res.raise_for_status()
        for chunk in res.iter_content(chunk_size=128):
            handle.write(chunk)
