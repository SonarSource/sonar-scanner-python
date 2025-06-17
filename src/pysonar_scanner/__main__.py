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
from typing import Any
from pysonar_scanner import app_logging
from pysonar_scanner import cache
from pysonar_scanner import exceptions
from pysonar_scanner.api import get_base_urls, SonarQubeApi, BaseUrls, MIN_SUPPORTED_SQ_VERSION
from pysonar_scanner.configuration import configuration_loader
from pysonar_scanner.configuration.configuration_loader import ConfigurationLoader
from pysonar_scanner.configuration.properties import (
    SONAR_VERBOSE,
    SONAR_HOST_URL,
    SONAR_SCANNER_API_BASE_URL,
    SONAR_SCANNER_SONARCLOUD_URL,
    SONAR_SCANNER_PROXY_PORT,
    SONAR_SCANNER_JAVA_EXE_PATH,
    SONAR_SCANNER_OS,
    SONAR_SCANNER_ARCH,
)
from pysonar_scanner.exceptions import SQTooOldException
from pysonar_scanner.jre import JREResolvedPath, JREProvisioner, JREResolver, JREResolverConfiguration
from pysonar_scanner.scannerengine import ScannerEngine, ScannerEngineProvisioner


def main():
    exit(scan())


def scan():
    try:
        return do_scan()
    except Exception as e:
        return exceptions.log_error(e)


def do_scan():
    app_logging.setup()
    logging.info(
        "Enhance your workflow: Pair pysonar with SonarQube Server per your license or SonarQube Cloud for deeper analysis, and try SonarQube-IDE in your favourite IDE."
    )
    logging.info("Starting Pysonar, the Sonar scanner CLI for Python")
    config = ConfigurationLoader.load()
    set_logging_options(config)

    ConfigurationLoader.check_configuration(config)

    api = build_api(config)
    check_version(api)
    update_config_with_api_urls(config, api.base_urls)
    logging.debug(f"Final loaded configuration: {config}")

    cache_manager = cache.get_cache(config)
    scanner = create_scanner_engine(api, cache_manager, config)

    logging.info("Starting the analysis...")
    return scanner.run(config)


def set_logging_options(config):
    app_logging.configure_logging_level(verbose=config.get(SONAR_VERBOSE, False))


def build_api(config: dict[str, Any]) -> SonarQubeApi:
    token = configuration_loader.get_token(config)
    base_urls = get_base_urls(config)
    return SonarQubeApi(base_urls, token)


def check_version(api: SonarQubeApi):
    if api.is_sonar_qube_cloud():
        logging.debug(f"SonarQube Cloud url: {api.base_urls.base_url}")
        return
    version = api.get_analysis_version()
    logging.debug(f"SonarQube url: {api.base_urls.base_url}")

    if not version.does_support_bootstrapping():
        raise SQTooOldException(
            f"This scanner only supports SonarQube versions >= {MIN_SUPPORTED_SQ_VERSION}. \n"
            f"The server at {api.base_urls.base_url} is on version {version}\n"
            "Please either upgrade your SonarQube server or use the Sonar Scanner CLI (see https://docs.sonarsource.com/sonarqube-server/latest/analyzing-source-code/scanners/sonarscanner/)."
        )


def update_config_with_api_urls(config, base_urls: BaseUrls):
    config[SONAR_HOST_URL] = base_urls.base_url
    config[SONAR_SCANNER_API_BASE_URL] = base_urls.api_base_url
    if base_urls.is_sonar_qube_cloud:
        config[SONAR_SCANNER_SONARCLOUD_URL] = base_urls.base_url
    config[SONAR_SCANNER_PROXY_PORT] = "443" if base_urls.base_url.startswith("https") else "80"


def create_scanner_engine(api, cache_manager, config):
    jre_path = create_jre(api, cache_manager, config)
    config[SONAR_SCANNER_JAVA_EXE_PATH] = str(jre_path.path)
    logging.debug(f"JRE path: {jre_path.path}")
    scanner_engine_path = ScannerEngineProvisioner(api, cache_manager).provision()
    scanner = ScannerEngine(jre_path, scanner_engine_path)
    return scanner


def create_jre(api, cache, config: dict[str, Any]) -> JREResolvedPath:
    jre_provisioner = JREProvisioner(api, cache, config[SONAR_SCANNER_OS], config[SONAR_SCANNER_ARCH])
    jre_resolver = JREResolver(JREResolverConfiguration.from_dict(config), jre_provisioner)
    return jre_resolver.resolve_jre()
