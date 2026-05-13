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
import logging
import os
import pathlib
from subprocess import CompletedProcess
from typing import Optional
import subprocess

import pytest


from tests.its.utils.sonarqube_client import SonarQubeClient


SOURCES_FOLDER_PATH: pathlib.Path = pathlib.Path(__file__).resolve().parent / "../sources"
DEBUGPY_PORT: int = 5678


class CliClient:
    def __init__(self, sq_client: SonarQubeClient, is_debugging: bool, caplog: pytest.CaptureFixture):
        self.sq_client = sq_client
        self.is_debugging = is_debugging
        self.caplog = caplog

    def run_analysis(self, sources_dir: str, params: list[str] = None, token: str = None) -> CompletedProcess:
        if params is None:
            params = []
        token = token or self.sq_client.get_user_token()
        workdir = SOURCES_FOLDER_PATH / sources_dir

        if self.is_debugging:
            return self.__run_analysis_with_debugging(workdir, params, token)
        else:
            return self.__run_analysis_normal(workdir, params, token)

    def __run_analysis_with_debugging(self, workdir: pathlib.Path, params: list[str], token: str) -> CompletedProcess:
        with self.caplog.at_level(logging.INFO):
            logging.info("Starting debugpy server on port %d", DEBUGPY_PORT)

        command = [
            "debugpy",
            "--wait-for-client",
            "--listen",
            str(DEBUGPY_PORT),
            "-m",
            "tests.its.utils.pysonar-debug",
            f"--sonar-host-url={self.sq_client.base_url}",
            f"--token={token}",
            *params,
        ]

        subproc_env = os.environ.copy()
        subproc_env["PYSONAR_SCANNER_DEBUG_WORKDIR"] = str(workdir)

        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=subproc_env,
        )
        self._wait_for_ce_completion(workdir)
        return process

    def __run_analysis_normal(self, workdir: pathlib.Path, params: list[str], token: str) -> CompletedProcess:
        command = [
            "pysonar",
            f"--sonar-host-url={self.sq_client.base_url}",
            f"--token={token}",
            *params,
        ]

        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=workdir,
        )
        self._wait_for_ce_completion(workdir)
        return process

    def _wait_for_ce_completion(self, workdir: pathlib.Path) -> None:
        task_id = self._read_ce_task_id(workdir)
        if task_id:
            self.sq_client.wait_for_ce_task_by_id(task_id)

    @staticmethod
    def _read_ce_task_id(workdir: pathlib.Path) -> Optional[str]:
        report_task_file = workdir / ".sonar" / "report-task.txt"
        if not report_task_file.is_file():
            return None
        for line in report_task_file.read_text().splitlines():
            if line.startswith("ceTaskId="):
                return line.split("=", 1)[1].strip()
        return None
