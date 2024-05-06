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
from subprocess import CompletedProcess
import subprocess
import os
from utils.sonarqube_client import SonarQubeClient


class CliClient():

    SCANNER_CMD: str = "pysonar"
    SOURCES_FOLDER_PATH: str = os.path.join(
        os.path.dirname(__file__), "../sources")

    def run_analysis(self, client: SonarQubeClient, params: list[str] = None, sources_dir: str = None) -> CompletedProcess:
        if params is None:
            params = []
        workdir = os.path.join(self.SOURCES_FOLDER_PATH, sources_dir)
        command = [self.SCANNER_CMD] + params
        print("WORKDIR = ", workdir)
        print("COMMAND = ", command)
        process = subprocess.run(command, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, text=True, cwd=workdir)
        client.wait_for_analysis_completion()
        return process
