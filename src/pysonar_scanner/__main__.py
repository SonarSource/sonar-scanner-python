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

from pysonar_scanner import cache
from pysonar_scanner.configuration import Configuration, ConfigurationLoader
from pysonar_scanner.api import get_base_urls, SonarQubeApi
from pysonar_scanner.scannerengine import ScannerEngine
from pysonar_scanner.cache import Cache
from pysonar_scanner.jre import JREProvisioner, JREResolvedPath, JREResolver


def scan():
    configuration = ConfigurationLoader().initialize_configuration()
    cache_manager = cache.get_default()
    api = __build_api(configuration)
    scanner = ScannerEngine(api, cache_manager)
    return scanner.run(configuration)


def __build_api(configuration) -> SonarQubeApi:
    base_urls = get_base_urls(configuration)
    return SonarQubeApi(base_urls, configuration.sonar.token)
