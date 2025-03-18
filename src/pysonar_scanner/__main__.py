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

import pathlib 

from pysonar_scanner.configuration import ConfigurationLoader
from pysonar_scanner.api import get_base_urls, SonarQubeApi
from pysonar_scanner.scannerengine import ScannerEngine
from pysonar_scanner.cache import Cache
from pysonar_scanner.jre import JREProvisioner, JREResolver

def scan():
    configuration = ConfigurationLoader().initialize_configuration()
    baseUrls = get_base_urls(configuration) 
    cache = Cache.create_cache(pathlib.Path("sonar_cache"))
    token = configuration.sonar.token
    api = SonarQubeApi(baseUrls, token)
    scanner = ScannerEngine(api, cache)
    scanner.version_check()
    scanner.fetch_scanner_engine()
    jre_provisionner = JREProvisioner(api, cache)
    jre_resolver = JREResolver(configuration, jre_provisionner)
    jre_resolved_path = jre_resolver.resolve_jre()
    scanner.run(jre_resolved_path, configuration)
    