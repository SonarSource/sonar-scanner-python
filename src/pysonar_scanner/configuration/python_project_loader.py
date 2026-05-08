#
# Sonar Scanner Python
# Copyright (C) 2011-2026 SonarSource Sàrl
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
import configparser
import logging
import pathlib
from typing import Optional

import tomli

from pysonar_scanner.configuration.properties import SONAR_TESTS

_CONVENTIONAL_TEST_DIRS = ["tests", "test", "testing"]
_SETUP_CFG_PYTEST_SECTION = "tool:pytest"


def load(base_dir: pathlib.Path) -> dict[str, str]:
    """Infer sonar.tests from Python tooling configuration and filesystem conventions.

    Returns sonar.tests if a test directory can be reliably inferred; empty dict otherwise.
    Filesystem convention fallback only runs when no config file declares a testpaths key.
    """
    for loader in [_load_from_pyproject_toml, _load_from_pytest_ini, _load_from_tox_ini, _load_from_setup_cfg]:
        result = loader(base_dir)
        if result is None:
            continue  # file absent or no testpaths key — try next source
        if result:
            return {SONAR_TESTS: result}
        return {}  # testpaths declared but all paths were invalid — stop chain, set nothing

    # No config file declared a testpaths key; fall back to filesystem conventions.
    filesystem_result = _load_from_filesystem(base_dir)
    if filesystem_result:
        return {SONAR_TESTS: filesystem_result}
    return {}


def _existing_paths(base_dir: pathlib.Path, paths: list[str]) -> list[str]:
    """Filter a list of candidate paths to those that exist as directories under base_dir.

    Absolute paths are relativised against the project root. If an absolute path falls
    outside the project root it is skipped with a warning. Relative paths that resolve
    to a file (not a directory) are skipped with a debug message.
    """
    abs_base = base_dir.resolve()
    result = []
    for p in paths:
        path = pathlib.Path(p)
        if path.root:  # rooted path: absolute on POSIX, or rooted (possibly drive-relative) on Windows
            try:
                # On Windows, abs_base.resolve() adds a drive letter (e.g. C:\project) while a path
                # read from config may be drive-relative (/project/tests, no drive). Attach the base
                # drive so relative_to() can compare them correctly.
                candidate = pathlib.Path(abs_base.drive + str(path)) if abs_base.drive and not path.drive else path
                p = candidate.relative_to(abs_base).as_posix()
                logging.debug(f"Converted absolute testpath '{path}' to relative path '{p}' against project root")
            except ValueError:
                logging.warning(
                    f"Ignoring '{path}' in testpaths — path is outside the project root '{abs_base}' "
                    f"and cannot be expressed as a relative path for sonar.tests"
                )
                continue
        resolved = base_dir / p
        if resolved.is_dir():
            result.append(p)
        elif resolved.exists():
            logging.debug(
                f"Ignoring '{p}' in testpaths — it is a file, not a directory; sonar.tests uses directory roots"
            )
    return result


def _load_from_pyproject_toml(base_dir: pathlib.Path) -> Optional[str]:
    pyproject_path = base_dir / "pyproject.toml"
    if not pyproject_path.is_file():
        return None
    try:
        with open(pyproject_path, "rb") as f:
            toml_dict = tomli.load(f)
        testpaths = toml_dict.get("tool", {}).get("pytest", {}).get("ini_options", {}).get("testpaths")
        if not testpaths:
            return None
        raw = [str(p) for p in (testpaths if isinstance(testpaths, list) else testpaths.split()) if str(p).strip()]
        if not raw:
            return None
        paths = _existing_paths(base_dir, raw)
        if paths:
            result = ",".join(paths)
            logging.debug(f"Detected test paths from pyproject.toml [tool.pytest.ini_options]: {result}")
            return result
        logging.warning(
            f"testpaths is set in pyproject.toml [tool.pytest.ini_options] to {raw} "
            f"but none of those paths exist as directories — sonar.tests will not be auto-detected"
        )
        return ""  # declared but all paths invalid: stop the chain
    except Exception as e:
        logging.debug(f"Error reading pyproject.toml for pytest testpaths: {e}")
    return None


def _load_from_pytest_ini(base_dir: pathlib.Path) -> Optional[str]:
    pytest_ini_path = base_dir / "pytest.ini"
    if not pytest_ini_path.is_file():
        return None
    try:
        config = configparser.ConfigParser()
        config.read(pytest_ini_path)
        if "pytest" not in config or "testpaths" not in config["pytest"]:
            return None
        raw = [p for p in config["pytest"]["testpaths"].split() if p]
        if not raw:
            return None
        paths = _existing_paths(base_dir, raw)
        if paths:
            result = ",".join(paths)
            logging.debug(f"Detected test paths from pytest.ini: {result}")
            return result
        logging.warning(
            f"testpaths is set in pytest.ini to {raw} "
            f"but none of those paths exist as directories — sonar.tests will not be auto-detected"
        )
        return ""
    except Exception as e:
        logging.debug(f"Error reading pytest.ini for testpaths: {e}")
    return None


def _load_from_tox_ini(base_dir: pathlib.Path) -> Optional[str]:
    tox_ini_path = base_dir / "tox.ini"
    if not tox_ini_path.is_file():
        return None
    try:
        config = configparser.ConfigParser()
        config.read(tox_ini_path)
        if "pytest" not in config or "testpaths" not in config["pytest"]:
            return None
        raw = [p for p in config["pytest"]["testpaths"].split() if p]
        if not raw:
            return None
        paths = _existing_paths(base_dir, raw)
        if paths:
            result = ",".join(paths)
            logging.debug(f"Detected test paths from tox.ini: {result}")
            return result
        logging.warning(
            f"testpaths is set in tox.ini to {raw} "
            f"but none of those paths exist as directories — sonar.tests will not be auto-detected"
        )
        return ""
    except Exception as e:
        logging.debug(f"Error reading tox.ini for testpaths: {e}")
    return None


def _load_from_setup_cfg(base_dir: pathlib.Path) -> Optional[str]:
    setup_cfg_path = base_dir / "setup.cfg"
    if not setup_cfg_path.is_file():
        return None
    try:
        config = configparser.ConfigParser()
        config.read(setup_cfg_path)
        if _SETUP_CFG_PYTEST_SECTION not in config or "testpaths" not in config[_SETUP_CFG_PYTEST_SECTION]:
            return None
        raw = [p for p in config[_SETUP_CFG_PYTEST_SECTION]["testpaths"].split() if p]
        if not raw:
            return None
        paths = _existing_paths(base_dir, raw)
        if paths:
            result = ",".join(paths)
            logging.debug(f"Detected test paths from setup.cfg [tool:pytest]: {result}")
            return result
        logging.warning(
            f"testpaths is set in setup.cfg [tool:pytest] to {raw} "
            f"but none of those paths exist as directories — sonar.tests will not be auto-detected"
        )
        return ""
    except Exception as e:
        logging.debug(f"Error reading setup.cfg for pytest testpaths: {e}")
    return None


def _load_from_filesystem(base_dir: pathlib.Path) -> Optional[str]:
    found = [d for d in _CONVENTIONAL_TEST_DIRS if (base_dir / d).is_dir()]
    if found:
        result = ",".join(found)
        logging.debug(f"Detected test paths from filesystem conventions: {result}")
        return result
    return None
