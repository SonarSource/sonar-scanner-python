from pysonar_scanner.configuration import Configuration
from pysonar_scanner.jre.resolved_path import JREResolvedPath

class JREProvisioner():

    def provision(self, configuration: Configuration) -> JREResolvedPath:
        return JREResolvedPath("test")


    def _get_metatada(self, configuration: Configuration):
        return None
