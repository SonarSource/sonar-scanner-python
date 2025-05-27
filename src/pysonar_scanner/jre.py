#
# Sonar Scanner Python
# Copyright (C) 2011-2024 SonarSource SA.
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
import logging
import pathlib
import shutil
import tarfile
import zipfile
from dataclasses import dataclass
from typing import Any, Optional

from pysonar_scanner import utils
from pysonar_scanner.api import JRE, SonarQubeApi
from pysonar_scanner.cache import Cache
from pysonar_scanner.exceptions import (
    ChecksumException,
    NoJreAvailableException,
    UnsupportedArchiveFormat,
)
from pysonar_scanner.exceptions import JreProvisioningException
from pysonar_scanner.configuration.properties import (
    SONAR_SCANNER_JAVA_EXE_PATH,
    SONAR_SCANNER_SKIP_JRE_PROVISIONING,
    SONAR_SCANNER_OS,
    Key,
    SONAR_SCANNER_ARCH,
)


@dataclass(frozen=True)
class JREResolvedPath:
    path: pathlib.Path

    @staticmethod
    def from_string(path: str) -> "JREResolvedPath":
        if not path:
            raise ValueError("JRE path cannot be empty")
        return JREResolvedPath(pathlib.Path(path))


class JREProvisioner:
    def __init__(
        self, api: SonarQubeApi, cache: Cache, sonar_scanner_os: utils.OsStr, sonar_scanner_arch: utils.ArchStr
    ):
        self.api = api
        self.cache = cache
        self.sonar_scanner_os = sonar_scanner_os
        self.sonar_scanner_arch = sonar_scanner_arch

    def provision(self) -> JREResolvedPath:
        jre, resolved_path = self.__attempt_provisioning_jre_with_retry()
        return self.__unpack_jre(jre, resolved_path)

    def __attempt_provisioning_jre_with_retry(self) -> tuple[JRE, pathlib.Path]:
        jre_and_resolved_path = self.__attempt_provisioning_jre()
        if jre_and_resolved_path is None:
            logging.warning("Something went wrong while provisionning the JRE. Retrying...")
            jre_and_resolved_path = self.__attempt_provisioning_jre()
        if jre_and_resolved_path is None:
            raise ChecksumException.create("JRE")

        return jre_and_resolved_path

    def __attempt_provisioning_jre(self) -> Optional[tuple[JRE, pathlib.Path]]:
        jre = self.__get_available_jre()

        jre_path = self.__get_jre_from_cache(jre)
        if jre_path is not None:
            return (jre, jre_path)

        jre_path = self.__download_jre(jre)
        return (jre, jre_path) if jre_path is not None else None

    def __get_available_jre(self) -> JRE:
        jres = self.api.get_analysis_jres(os=self.sonar_scanner_os, arch=self.sonar_scanner_arch)
        if len(jres) == 0:
            raise NoJreAvailableException(
                f"No JREs are available for {self.sonar_scanner_os} and {self.sonar_scanner_arch}"
            )
        return jres[0]

    def __get_jre_from_cache(self, jre: JRE) -> Optional[pathlib.Path]:
        cache_file = self.cache.get_file(jre.filename, jre.sha256)
        return cache_file.filepath if cache_file.is_valid() else None

    def __download_jre(self, jre: JRE) -> Optional[pathlib.Path]:
        cache_file = self.cache.get_file(jre.filename, jre.sha256)
        cache_file.filepath.unlink(missing_ok=True)

        with cache_file.open(mode="wb") as f:
            if jre.download_url is not None:
                self.api.download_file_from_url(jre.download_url, f)
            elif jre.id is not None:
                self.api.download_analysis_jre(jre.id, f)
            else:
                raise JreProvisioningException(
                    "Failed to download the JRE using SonarQube. If this problem persists, you can use the option --sonar-scanner-java-exe-path to use your own local JRE."
                )

        return cache_file.filepath if cache_file.is_valid() else None

    def __unpack_jre(self, jre: JRE, file_path: pathlib.Path) -> JREResolvedPath:
        unzip_dir = self.__prepare_unzip_dir(file_path)
        self.__extract_jre(file_path, unzip_dir)
        return JREResolvedPath(unzip_dir / jre.java_path)

    def __prepare_unzip_dir(self, file_path: pathlib.Path) -> pathlib.Path:
        unzip_dir = self.cache.get_file_path(f"{file_path.name}_unzip")
        try:
            if unzip_dir.exists():
                shutil.rmtree(unzip_dir)
            unzip_dir.mkdir(parents=True)
            return unzip_dir
        except OSError as e:
            raise JreProvisioningException(f"Failed to prepare unzip directory: {unzip_dir}") from e

    def __extract_jre(self, file_path: pathlib.Path, unzip_dir: pathlib.Path):
        if file_path.suffix == ".zip":
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                zip_ref.extractall(unzip_dir)
        elif file_path.suffix in [".gz", ".tgz"]:
            utils.extract_tar(file_path, unzip_dir)
        else:
            raise UnsupportedArchiveFormat(
                f"Received JRE is packaged as an unsupported archive format: {file_path.suffix}"
            )


@dataclass(frozen=True)
class JREResolverConfiguration:
    sonar_scanner_java_exe_path: Optional[str]
    sonar_scanner_skip_jre_provisioning: bool
    sonar_scanner_os: Optional[str]

    @staticmethod
    def from_dict(config_dict: dict[Key, Any]) -> "JREResolverConfiguration":
        return JREResolverConfiguration(
            sonar_scanner_java_exe_path=config_dict.get(SONAR_SCANNER_JAVA_EXE_PATH, None),
            sonar_scanner_skip_jre_provisioning=config_dict.get(SONAR_SCANNER_SKIP_JRE_PROVISIONING, False),
            sonar_scanner_os=config_dict.get(SONAR_SCANNER_OS, None),
        )


class JREResolver:
    def __init__(self, configuration: JREResolverConfiguration, jre_provisioner: JREProvisioner):
        self.configuration = configuration
        self.jre_provisioner = jre_provisioner

    def resolve_jre(self) -> JREResolvedPath:
        exe_suffix = ".exe" if self.configuration.sonar_scanner_os == "windows" else ""
        if self.configuration.sonar_scanner_java_exe_path:
            return JREResolvedPath(pathlib.Path(self.configuration.sonar_scanner_java_exe_path))
        if not self.configuration.sonar_scanner_skip_jre_provisioning:
            return self.__provision_jre()
        java_path = pathlib.Path(f"java{exe_suffix}")
        return JREResolvedPath(java_path)

    def __provision_jre(self) -> JREResolvedPath:
        return self.jre_provisioner.provision()
