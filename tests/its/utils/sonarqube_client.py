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
import logging
import time
from typing import Optional, TypedDict
from requests import Session

logger = logging.getLogger(__name__)


class SystemHealth(TypedDict):
    health: str


class SystemStatus(TypedDict):
    id: str
    version: str
    status: str


class IssuesSearch(TypedDict):
    issues: list


class ProjectAnalyses(TypedDict):
    key: str
    date: str
    projectVersion: str


class ProjectAnalysesSearch(TypedDict):
    analyses: list[ProjectAnalyses]


class SonarQubeClient:
    MAX_RETRIES: int = 5

    def __init__(self, base_url):
        self.base_url = base_url
        self.session = Session()
        self.session.auth = ("admin", "admin")
        self.__token: Optional[str] = None

    def get_user_token(self) -> str:
        if not self.__token:
            self.__token = self.generate_token("test-token")
        return self.__token

    def generate_token(self, name: str) -> str:
        token_response = self.session.post(f"{self.base_url}/api/user_tokens/generate", data={"name": name})
        token_response.raise_for_status()
        token_json = token_response.json()
        return token_json["token"]

    def get_system_health(self) -> SystemHealth:
        resp = self.session.get(f"{self.base_url}/api/system/health")
        resp.raise_for_status()
        return resp.json()

    def get_system_status(self) -> SystemStatus:
        resp = self.session.get(f"{self.base_url}/api/system/status")
        resp.raise_for_status()
        return resp.json()

    def wait_for_analysis_completion(self):
        empty_queue = False
        count = 0
        while not empty_queue:
            logger.info("Waiting for analysis completion")
            if count > self.MAX_RETRIES:
                raise RuntimeError("Too many retries on analysis report")
            response = self.session.get(f"{self.base_url}/api/analysis_reports/is_queue_empty")
            if "true" == response.text:
                empty_queue = True
            count = count + 1
            time.sleep(2)

    def get_project_issues(self, project_key: str) -> IssuesSearch:
        resp = self.session.get(f"{self.base_url}/api/issues/search?projects={project_key}")
        resp.raise_for_status()
        return resp.json()

    def get_project_analyses(self, project_key: str) -> ProjectAnalysesSearch:
        resp = self.session.get(f"{self.base_url}/api/project_analyses/search?project={project_key}")
        resp.raise_for_status()
        return resp.json()
