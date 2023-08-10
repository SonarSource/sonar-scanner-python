import subprocess
import threading
from cli.context import Context


class Scanner:
    def scan(self, ctx: Context):
        cmd = [ctx.sonar_scanner_executable_path] + ctx.scan_arguments
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
