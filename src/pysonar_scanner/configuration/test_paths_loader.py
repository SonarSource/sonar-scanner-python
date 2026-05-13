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


def load(base_dir: pathlib.Path) -> tuple[dict[str, str], bool]:
    """Infer sonar.tests from Python tooling configuration and filesystem conventions.

    Returns (properties, disable_heuristic) where:
    - properties contains sonar.tests if a test directory was reliably inferred
    - disable_heuristic is True when a config file declared testpaths but all paths were
      invalid — the user expressed intent, so the sonar-python heuristic should not fire
    """
    for loader in [_load_from_pyproject_toml, _load_from_pytest_ini, _load_from_tox_ini, _load_from_setup_cfg]:
        result = loader(base_dir)
        if result is None:
            continue  # file absent, no testpaths key, or empty testpaths (no restriction) — try next
        if result:
            return {SONAR_TESTS: result}, False
        return {}, True  # declared but all paths invalid: user expressed intent, disable heuristic

    # No config file gave a non-empty testpaths declaration; fall back to filesystem conventions.
    filesystem_result = _load_from_filesystem(base_dir)
    if filesystem_result:
        return {SONAR_TESTS: filesystem_result}, False
    return {}, False


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
    except tomli.TOMLDecodeError as e:
        logging.debug(f"Error reading pyproject.toml for pytest testpaths: {e}")
        return None
    ini_options = toml_dict.get("tool", {}).get("pytest", {}).get("ini_options", {})
    if "testpaths" not in ini_options:
        return None
    testpaths = ini_options["testpaths"]
    if not isinstance(testpaths, (list, str)):
        logging.warning(
            f"testpaths in pyproject.toml [tool.pytest.ini_options] has an unexpected type "
            f"({type(testpaths).__name__}) — expected a list or string, skipping"
        )
        return None
    raw = [str(p) for p in (testpaths if isinstance(testpaths, list) else testpaths.split()) if str(p).strip()]
    if not raw:
        return None  # testpaths = [] means "no path restriction" — same as key absent, continue chain
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


def _load_from_ini_file(base_dir: pathlib.Path, filename: str, section: str) -> Optional[str]:
    config_path = base_dir / filename
    if not config_path.is_file():
        return None
    try:
        config = configparser.ConfigParser()
        config.read(config_path)
    except configparser.Error as e:
        logging.debug(f"Error reading {filename} for pytest testpaths: {e}")
        return None
    if section not in config or "testpaths" not in config[section]:
        return None
    raw = [p for p in config[section]["testpaths"].split() if p]
    if not raw:
        return None  # empty testpaths means "no path restriction" — same as key absent, continue chain
    paths = _existing_paths(base_dir, raw)
    if paths:
        result = ",".join(paths)
        logging.debug(f"Detected test paths from {filename} [{section}]: {result}")
        return result
    logging.warning(
        f"testpaths is set in {filename} [{section}] to {raw} "
        f"but none of those paths exist as directories — sonar.tests will not be auto-detected"
    )
    return ""


def _load_from_pytest_ini(base_dir: pathlib.Path) -> Optional[str]:
    return _load_from_ini_file(base_dir, "pytest.ini", "pytest")


def _load_from_tox_ini(base_dir: pathlib.Path) -> Optional[str]:
    return _load_from_ini_file(base_dir, "tox.ini", "pytest")


def _load_from_setup_cfg(base_dir: pathlib.Path) -> Optional[str]:
    return _load_from_ini_file(base_dir, "setup.cfg", _SETUP_CFG_PYTEST_SECTION)


def _load_from_filesystem(base_dir: pathlib.Path) -> Optional[str]:
    found = [d for d in _CONVENTIONAL_TEST_DIRS if (base_dir / d).is_dir()]
    if found:
        result = ",".join(found)
        logging.debug(f"Detected test paths from filesystem conventions: {result}")
        return result
    return None
