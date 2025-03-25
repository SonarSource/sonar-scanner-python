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
import pathlib
from subprocess import CompletedProcess
import subprocess

from utils.sonarqube_client import SonarQubeClient


SCANNER_CMD: str = "pysonar-scanner"
SOURCES_FOLDER_PATH: pathlib.Path = pathlib.Path(__file__).resolve().parent / "../sources"


class CliClient:
    def __init__(self, sq_client: SonarQubeClient):
        self.sq_client = sq_client

    def run_analysis(self, sources_dir: str, params: list[str] = None, token: str = None) -> CompletedProcess:
        if params is None:
            params = []

        token = token or self.sq_client.get_user_token()

        params.append(f"--sonar-host-url={self.sq_client.base_url}")
        params.append(f"--token={token}")
        workdir = SOURCES_FOLDER_PATH / sources_dir
        command = [SCANNER_CMD] + params
        process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=workdir)
        self.sq_client.wait_for_analysis_completion()
        return process
