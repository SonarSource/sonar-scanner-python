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
import time

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class JRECacheStatus(Enum):
    HIT = 1
    MISS = 2
    DISABLE = 3


@dataclass(frozen=True)
class Internal:
    dump_to_file: Optional[str] = None  # File path to dump the input to the scanner engine
    sq_version: Optional[str] = None


@dataclass(frozen=True)
class Scanner:
    app: str = "python"
    app_version: str = "1.0"
    bootstrap_start_time: int = int(time.time() * 1000)

    os: Optional[str] = None
    arch: Optional[str] = None

    connect_timeout: Optional[int] = None
    socket_timeout: Optional[int] = None
    response_timeout: Optional[int] = None

    truststore_path: Optional[str] = None
    truststore_password: Optional[str] = None
    keystore_path: Optional[str] = None
    keystore_password: Optional[str] = None

    proxy_host: Optional[str] = None
    proxy_port: Optional[int] = None
    proxy_user: Optional[str] = None
    proxy_password: Optional[str] = None

    was_jre_cache_hit: Optional[JRECacheStatus] = None
    was_engine_cache_hit: Optional[bool] = None
    skip_jre_provisioning: bool = False
    java_exe_path: Optional[str] = None
    java_opts: Optional[str] = None

    sonarcloud_url: str = ""
    api_base_url: str = ""

    internal: Internal = Internal()


@dataclass(frozen=True)
class Sonar:
    scanner: Scanner = Scanner()

    verbose: bool = False

    project_base_dir: Optional[str] = None
    user_home: Optional[str] = None

    token: str = ""
    host_url: str = ""
    region: str = ""


@dataclass(frozen=True)
class Configuration:
    sonar: Sonar = Sonar()


class ConfigurationLoader:
    pass
