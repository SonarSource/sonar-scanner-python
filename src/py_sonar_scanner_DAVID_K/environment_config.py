import os.path
import platform
import shutil
import urllib.request
import zipfile

from py_sonar_scanner_DAVID_K.context import Context

systems = {
    'Darwin': 'macosx',
    'Windows': 'windows'
}


class ScannerConfig:
    def setup(self, ctx: Context):
        system_name = systems.get(platform.uname().system, 'linux')

        self._cleanup(ctx)

        # Download the binaries and unzip them
        # https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-${version}-${os}.zip
        self._install(ctx, system_name)

        self._change_permissions_recursive(ctx.sonar_scanner_path, 0o777)

        sonar_scanner_home = os.path.join(ctx.sonar_scanner_path,
                                          f'sonar-scanner-{ctx.sonar_scanner_version}-{system_name}')
        ctx.sonar_scanner_executable_path = os.path.join(sonar_scanner_home, 'bin', 'sonar-scanner')
        print(ctx.sonar_scanner_executable_path)

    def _install(self, ctx, system_name):
        scanner_res = urllib.request.urlopen(
            f'https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-{ctx.sonar_scanner_version}-{system_name}.zip')
        scanner_zip_path = os.path.join(ctx.sonar_scanner_path, 'scanner.zip')
        with open(scanner_zip_path, 'wb') as output:
            output.write(scanner_res.read())
        with zipfile.ZipFile(scanner_zip_path, "r") as zip_ref:
            zip_ref.extractall(ctx.sonar_scanner_path)
        os.remove(scanner_zip_path)

    def _cleanup(self, ctx):
        if os.path.exists(ctx.sonar_scanner_path):
            shutil.rmtree(ctx.sonar_scanner_path)
        os.mkdir(ctx.sonar_scanner_path)

    def _change_permissions_recursive(self, path, mode):
        for root, dirs, files in os.walk(path, topdown=False):
            for dir in [os.path.join(root, d) for d in dirs]:
                os.chmod(dir, mode)
            for file in [os.path.join(root, f) for f in files]:
                os.chmod(file, mode)


class EnvironmentConfig:
    def setup(self, ctx: Context):
        ScannerConfig().setup(ctx)
