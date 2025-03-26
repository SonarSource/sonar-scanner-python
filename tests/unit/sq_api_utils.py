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
from pysonar_scanner import utils
from pysonar_scanner.api import JRE, BaseUrls, SonarQubeApi
import responses
from responses import matchers


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

    def mock_analysis_version(self, version: str = "", status: int = 200) -> responses.BaseResponse:
        return self.rsps.get(url=f"{self.api_url}/analysis/version", body=version, status=status)

    def mock_analysis_engine(
        self, filename: Optional[str] = None, sha256: Optional[str] = None, status: int = 200
    ) -> responses.BaseResponse:
        def prepare_json_obj() -> dict:
            json_response = {}
            if filename:
                json_response["filename"] = filename
            if sha256:
                json_response["sha256"] = sha256
            return json_response

        return self.rsps.get(
            url=f"{self.api_url}/analysis/engine",
            json=prepare_json_obj(),
            status=status,
            match=[matchers.header_matcher({"Accept": "application/json"})],
        )

    def mock_analysis_engine_download(self, body: bytes = b"", status: int = 200) -> responses.BaseResponse:
        return self.rsps.get(
            url=f"{self.api_url}/analysis/engine",
            body=body,
            status=status,
            match=[matchers.header_matcher({"Accept": "application/octet-stream"})],
        )

    def mock_analysis_jres(
        self,
        body: Optional[list[dict]] = None,
        os_matcher: Optional[str] = None,
        arch_matcher: Optional[str] = None,
        status: int = 200,
    ) -> responses.BaseResponse:
        return self.rsps.get(
            url=f"{self.api_url}/analysis/jres",
            json=body,
            status=status,
            match=[
                matchers.header_matcher({"Accept": "application/json"}),
                matchers.query_param_matcher(utils.filter_none_values({"os": os_matcher, "arch": arch_matcher})),
            ],
        )

    def mock_analysis_jre_download(
        self, id: str, body: bytes = b"", status: int = 200, redirect_url: Optional[str] = None
    ) -> responses.BaseResponse:
        return self.rsps.get(
            url=f"{self.api_url}/analysis/jres/{id}",
            body=body,
            headers={"Location": redirect_url} if redirect_url else None,
            status=status,
            match=[matchers.header_matcher({"Accept": "application/octet-stream"})],
        )

    def mock_server_version(self, version: str = "", status: int = 200) -> responses.BaseResponse:
        return self.rsps.get(url=f"{self.base_url}/api/server/version", body=version, status=status)


@contextlib.contextmanager
def sq_api_mocker(base_url: str = "http://sq.home", assert_all_requests_are_fired: bool = True):
    with responses.RequestsMock(assert_all_requests_are_fired=assert_all_requests_are_fired) as rsps:
        yield SQApiMocker(base_url=base_url, rsps=rsps)


def jre_to_dict(jre: JRE) -> dict:
    return {
        "id": jre.id,
        "filename": jre.filename,
        "sha256": jre.sha256,
        "javaPath": jre.java_path,
        "os": jre.os,
        "arch": jre.arch,
        "downloadUrl": jre.download_url,
    }
