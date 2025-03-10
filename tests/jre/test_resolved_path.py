from pysonar_scanner.jre.resolved_path import JREResolvedPath
import unittest


class TestJREResolvedPath(unittest.TestCase):
    def test_empty_path(self):
        with self.assertRaises(ValueError):
            JREResolvedPath("")

    def test_any_path(self):
        path = "test"
        resolved_path = JREResolvedPath(path)
        self.assertEqual(resolved_path.path, path)
