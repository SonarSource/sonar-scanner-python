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
import time
from requests import Session


class SonarQubeClient():

    MAX_RETRIES: int = 20
    session: Session
    base_url: str

    def __init__(self, base_url):
        self.base_url = base_url
        self.session = Session()
        self.session.auth = ("admin", "admin")

    def get_system_health(self):
        return self.session.get(f"{self.base_url}/api/system/health")

    def get_system_status(self):
        return self.session.get(f"{self.base_url}/api/system/status")

    def wait_for_analysis_completion(self):
        empty_queue = False
        count = 0
        while not empty_queue:
            if count > self.MAX_RETRIES:
                raise RuntimeError("Too many retries on analysis report")
            response = self.session.get(
                f"{self.base_url}/api/analysis_reports/is_queue_empty")
            if "true" == response.text:
                empty_queue = True
            count = count + 1
            time.sleep(2)

    def get_project_issues(self, project_key: str):
        return self.session.get(f"{self.base_url}/api/issues/search?projects={project_key}")
