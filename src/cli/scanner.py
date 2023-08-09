import subprocess
import threading
from cli.context import Context


class Scanner:
    def scan(self, ctx: Context):
        cmd = [ctx.sonar_scanner_executable_path] + ctx.scan_arguments
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        def print_output():
            while True:
                # TODO: print error as well
                output_line = process.stdout.readline()
                if not output_line:
                    break
                decoded_line = output_line.decode('utf-8')
                print(decoded_line, end='', flush=True)

        output_thread = threading.Thread(target=print_output)
        output_thread.start()

        process.wait()
        output_thread.join()

        return process.returncode
