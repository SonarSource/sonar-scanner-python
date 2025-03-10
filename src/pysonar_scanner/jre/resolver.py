from pysonar_scanner.configuration import Configuration
from pysonar_scanner.jre.resolved_path import JREResolvedPath
from pysonar_scanner.jre.provisioner import JREProvisioner


class JREResolver:
    def __init__(self, jre_provisioner: JREProvisioner):
        self.jre_provisioner = jre_provisioner

    def resolve_jre(self, configuration: Configuration):
        windows_exe_suffix = (
            ".exe" if configuration.sonar.scanner.os == "windows" else ""
        )
        if configuration.sonar.scanner.java_exe_path:
            return JREResolvedPath(configuration.sonar.scanner.java_exe_path)
        if not configuration.sonar.scanner.skip_jre_provisioning:
            return self._provision_jre(configuration)
        if configuration.environment.java_home:
            return JREResolvedPath(
                f"{configuration.environment.java_home}/bin/java{windows_exe_suffix}"
            )
        java_path = f"java{windows_exe_suffix}"
        return JREResolvedPath(java_path)

    def _provision_jre(self, configuration: Configuration):
        return self.jre_provisioner.provision(configuration)
