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
from typing import TypedDict
import unittest

from pysonar_scanner.api import BaseUrls, get_base_urls
from pysonar_scanner.configuration import Configuration, Scanner, Sonar


class ApiTest(unittest.TestCase):
    def test_BaseUrls_normalization(self):
        self.assertEqual(
            BaseUrls("test1/", "test2/", is_sonar_qube_cloud=True),
            BaseUrls("test1", "test2", is_sonar_qube_cloud=True),
        )

    def test_get_base_urls(self):
        class TestCaseDict(TypedDict):
            name: str
            config: Configuration
            expected: BaseUrls

        cases: list[TestCaseDict] = [
            # SQ:Cloud tests
            {
                "name": "default configuration defaults to SQ:cloud base urls",
                "config": Configuration(),
                "expected": BaseUrls(
                    base_url="https://sonarcloud.io", api_base_url="https://api.sonarcloud.io", is_sonar_qube_cloud=True
                ),
            },
            {
                "name": "sonar.host.url with whitespaces uses the SQ:cloud base urls",
                "config": Configuration(sonar=Sonar(host_url="  ")),
                "expected": BaseUrls(
                    base_url="https://sonarcloud.io", api_base_url="https://api.sonarcloud.io", is_sonar_qube_cloud=True
                ),
            },
            {
                "name": "when host_url is set to SQ:cloud, use SQ:cloud base urls",
                "config": Configuration(sonar=Sonar(host_url="https://sonarcloud.io")),
                "expected": BaseUrls(
                    base_url="https://sonarcloud.io", api_base_url="https://api.sonarcloud.io", is_sonar_qube_cloud=True
                ),
            },
            {
                "name": "When both host_url and sonarcloud_url are set, use sonarcloud_url to check if host is SQ:cloud",
                "config": Configuration(
                    sonar=Sonar(
                        host_url="https://sonarcloud.io",
                        scanner=Scanner(
                            sonarcloud_url="https://custom-sq-cloud.io",
                        ),
                    )
                ),
                "expected": BaseUrls(
                    base_url="https://sonarcloud.io",
                    api_base_url="https://sonarcloud.io/api/v2",
                    is_sonar_qube_cloud=False,
                ),
            },
            {
                "name": "when host_url with trailing slash is set to SQ:cloud, use SQ:cloud base urls",
                "config": Configuration(sonar=Sonar(host_url="https://sonarcloud.io/")),
                "expected": BaseUrls(
                    base_url="https://sonarcloud.io", api_base_url="https://api.sonarcloud.io", is_sonar_qube_cloud=True
                ),
            },
            # SQ:Cloud region tests
            {
                "name": "When region is set, use region in base urls",
                "config": Configuration(sonar=Sonar(host_url="https://sonarcloud.io", region="us")),
                "expected": BaseUrls(
                    base_url="https://us.sonarcloud.io",
                    api_base_url="https://api.us.sonarcloud.io",
                    is_sonar_qube_cloud=True,
                ),
            },
            {
                "name": "Ignore region when sonarcloud_url and api_base_url is set",
                "config": Configuration(
                    sonar=Sonar(
                        host_url="https://custom-sq-cloud.io",
                        region="us",
                        scanner=Scanner(
                            sonarcloud_url="https://custom-sq-cloud.io",
                            api_base_url="https://other-api.custom-sq-cloud.io",
                        ),
                    )
                ),
                "expected": BaseUrls(
                    base_url="https://custom-sq-cloud.io",
                    api_base_url="https://other-api.custom-sq-cloud.io",
                    is_sonar_qube_cloud=True,
                ),
            },
            # SQ:Server tests
            {
                "name": "When host_url is set to SQ:server, use SQ:server base urls",
                "config": Configuration(sonar=Sonar(host_url="https://sq.home")),
                "expected": BaseUrls(
                    base_url="https://sq.home", api_base_url="https://sq.home/api/v2", is_sonar_qube_cloud=False
                ),
            },
            {
                "name": "When host_url with trailing slash is set to SQ:server, use SQ:server base urls",
                "config": Configuration(sonar=Sonar(host_url="https://sq.home/")),
                "expected": BaseUrls(
                    base_url="https://sq.home", api_base_url="https://sq.home/api/v2", is_sonar_qube_cloud=False
                ),
            },
        ]

        for case in cases:
            expected = case["expected"]
            with self.subTest(case["name"], config=case["config"], expected=expected):
                base_urls = get_base_urls(case["config"])
                self.assertEqual(base_urls.base_url, expected.base_url)
                self.assertEqual(base_urls.api_base_url, expected.api_base_url)
                self.assertEqual(base_urls.is_sonar_qube_cloud, expected.is_sonar_qube_cloud)
                self.assertEqual(base_urls, expected)
