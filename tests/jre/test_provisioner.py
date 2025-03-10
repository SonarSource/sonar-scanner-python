from pysonar_scanner.jre.resolved_path import JREResolvedPath
import unittest


class TestJREProvisioner(unittest.TestCase):

    def test_resolve(self):
        path = JREResjsnedPath.resolve("java/lang/String")
        self.assertEqual(path, "java/lang/String.class")
