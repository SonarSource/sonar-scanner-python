import unittest
from unittest.mock import patch, Mock
from urllib.error import HTTPError
from py_sonar_scanner.configuration import Configuration
from py_sonar_scanner.environment import Environment


class TestEnvironment(unittest.TestCase):

    @patch("py_sonar_scanner.environment.write_binaries")
    @patch("py_sonar_scanner.environment.urllib.request.urlopen")
    def test_download_scanner(self, mock_urlopen, mock_write_binaries):
        cfg = Configuration()
        environment = Environment(cfg)
        environment.scanner_base_url = "http://scanner.com/download"
        mock_urlopen.return_value = bytes()

        expected_destination = "destination/scanner.zip"
        destination = environment._download_scanner_binaries("destination", "test_version", "os_name")

        mock_urlopen.assert_called_once_with("http://scanner.com/download-test_version-os_name.zip")
        mock_write_binaries.assert_called_once_with(bytes(), expected_destination)
        assert destination == expected_destination

    @patch("py_sonar_scanner.environment.write_binaries")
    @patch("py_sonar_scanner.environment.urllib.request.urlopen")
    def test_download_scanner_http_error(self, mock_urlopen, mock_write_binaries):
        cfg = Configuration()
        environment = Environment(cfg)
        environment.scanner_base_url = "http://scanner.com/download"
        url = "http://scanner.com/download-test_version-os_name.zip"
        mock_urlopen.side_effect = Mock(side_effect=HTTPError(url, 504, "Test", {}, None))

        with self.assertLogs(environment.log) as log:
            with self.assertRaises(HTTPError):
                environment._download_scanner_binaries("destination", "test_version", "os_name")
            mock_urlopen.assert_called_once_with(url)
            assert not mock_write_binaries.called
            expected_error_message = "ERROR: could not download scanner binaries - 504 - Test"
            assert log.records[0].getMessage() == expected_error_message

    @patch("py_sonar_scanner.environment.unzip_binaries")
    @patch("py_sonar_scanner.environment.os")
    def test_install_scanner(self, mock_os, mock_unzip_binaries):
        cfg = Configuration()
        scanner_path = "scanner_path"
        scanner_version = "1"
        cfg.sonar_scanner_path = scanner_path
        cfg.sonar_scanner_version = scanner_version

        environment = Environment(cfg)
        mock_os.remove = Mock()
        mock_os.mkdir = Mock()

        download_destination = "path"
        environment._download_scanner_binaries = Mock(return_value=download_destination)
        environment._change_permissions_recursive = Mock()

        system_name = "test"
        environment._install_scanner(system_name)

        mock_os.mkdir.assert_called_once_with(scanner_path)
        environment._download_scanner_binaries.assert_called_once_with(
            scanner_path, scanner_version, system_name
        )
        mock_unzip_binaries.assert_called_once_with(download_destination, scanner_path)

        mock_os.remove.assert_called_once_with(download_destination)
        environment._change_permissions_recursive.assert_called_once_with(
           scanner_path, 0o777 
        )

    def test_setup_when_scanner_is_on_path(self):
        cfg = Configuration()
        environment = Environment(cfg)
        environment.cleanup = Mock()
        environment._is_sonar_scanner_on_path = Mock(return_value=True)
        
        environment.setup()

        environment.cleanup.assert_called_once()
        assert cfg.sonar_scanner_executable_path == "sonar-scanner"

    @patch("py_sonar_scanner.environment.systems")
    def test_setup_when_scanner_is_not_on_path(self, mock_systems):
        cfg = Configuration()
        cfg.sonar_scanner_path = "path"
        cfg.sonar_scanner_version = "4.1.2"
        environment = Environment(cfg)
        environment.cleanup = Mock()
        system_name = "test"
        mock_systems.get = Mock(return_value=system_name)
        environment._is_sonar_scanner_on_path = Mock(return_value=False)
        environment._install_scanner = Mock()
        expected_path = "path/sonar-scanner-4.1.2-test/bin/sonar-scanner"

        environment.setup()

        environment.cleanup.assert_called_once()
        mock_systems.get.assert_called_once()
        environment._install_scanner.assert_called_once_with(system_name)

        assert cfg.sonar_scanner_executable_path == expected_path

    @patch("py_sonar_scanner.environment.os.path")
    @patch("py_sonar_scanner.environment.shutil")
    def test_cleanup_when_scanner_path_exists(self, mock_shutil, mock_os_path):
        cfg = Configuration()
        scanner_path = "path"
        cfg.sonar_scanner_path = scanner_path
        environment = Environment(cfg)
        mock_os_path.exists = Mock(return_value=True)
        mock_shutil.rmtree = Mock()

        environment.cleanup()

        mock_os_path.exists.assert_called_once_with(scanner_path)
        mock_shutil.rmtree.assert_called_once_with(scanner_path)

    @patch("py_sonar_scanner.environment.os.path")
    @patch("py_sonar_scanner.environment.shutil")
    def test_cleanup_when_scanner_path_does_not_exist(self, mock_shutil, mock_os_path):
        cfg = Configuration()
        scanner_path = "path"
        cfg.sonar_scanner_path = scanner_path
        environment = Environment(cfg)
        mock_os_path.exists = Mock(return_value=False)
        mock_shutil.rmtree = Mock()
        
        environment.cleanup()

        mock_os_path.exists.assert_called_once_with(scanner_path)
        assert not mock_shutil.rmtree.called

    @patch("py_sonar_scanner.environment.shutil")
    def test_is_sonar_scanner_on_path(self, mock_shutil):
        cfg = Configuration()
        scanner_path = "path"
        cfg.sonar_scanner_path = scanner_path
        environment = Environment(cfg)
        mock_shutil.which = Mock()
        
        environment._is_sonar_scanner_on_path()

        mock_shutil.which.assert_called_once_with("sonar-scanner")
