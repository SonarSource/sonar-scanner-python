
class Context:
    sonar_scanner_executable_path: str
    sonar_scanner_path: str
    jre_base_dir_path: str
    jre_bin_path: str
    sonar_scanner_version: str

    def __init__(self):
        self.jre_base_dir_path = '.jre'
        self.jre_bin_path = ''
        self.sonar_scanner_path = '.scanner'
        self.sonar_scanner_version = '4.6.2.2472'
        self.sonar_scanner_executable_path = ''
