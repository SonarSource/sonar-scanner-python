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
import subprocess
import threading

from py_sonar_scanner.configuration import Configuration


class Scanner:
    cfg: Configuration

    def __init__(self, cfg: Configuration):
        self.cfg = cfg

    def scan(self):
        cmd = [self.cfg.sonar_scanner_executable_path] + self.cfg.scan_arguments
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        def print_output(stream):
            for line in stream:
                decoded_line = line.decode('utf-8')
                print(decoded_line, end='', flush=True)

        output_thread = threading.Thread(target=print_output, args=(process.stdout,))
        error_thread = threading.Thread(target=print_output, args=(process.stderr,))
        output_thread.start()
        error_thread.start()

        process.wait()
        output_thread.join()
        error_thread.join()

        return process.returncode
