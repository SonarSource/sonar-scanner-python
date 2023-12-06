#
# Sonar Scanner Python
# Copyright (C) 2011-2023 SonarSource SA.
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
import threading
from threading import Thread
from subprocess import Popen, PIPE

from py_sonar_scanner.configuration import Configuration


class Scanner:
    cfg: Configuration

    def __init__(self, cfg: Configuration):
        self.cfg = cfg

    def scan(self):
        process = self.execute_command()
        output_thread = threading.Thread(target=self._print_output, args=(process.stdout,))
        error_thread = threading.Thread(target=self._print_output, args=(process.stderr,))
        return self.process_output(output_thread, error_thread, process)

    def process_output(self, output_thread: Thread, error_thread: Thread, process: Popen) -> int:
        output_thread.start()
        error_thread.start()
        process.wait()
        output_thread.join()
        error_thread.join()

        return process.returncode

    def compute_command(self) -> list[str]:
        if (not self.cfg.sonar_scanner_executable_path):
            raise ValueError("No executable path provided")
        return [self.cfg.sonar_scanner_executable_path] + self.cfg.scan_arguments

    def execute_command(self) -> Popen:
        cmd = self.compute_command()
        return Popen(cmd, stdout=PIPE, stderr=PIPE)

    def _print_output(self, stream: list[str]):
        for line in stream:
            decoded_line = line.decode('utf-8')
            print(decoded_line, end='', flush=True)
