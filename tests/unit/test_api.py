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

import io

from pysonar_scanner import api
from pysonar_scanner.api import JRE, BaseUrls, EngineInfo, SonarQubeApi, SonarQubeApiException, get_base_urls
from pysonar_scanner.configuration.properties import (
    Key,
    SONAR_HOST_URL,
    SONAR_REGION,
    SONAR_SCANNER_API_BASE_URL,
    SONAR_SCANNER_SONARCLOUD_URL,
)
from pysonar_scanner.api import SQVersion
from pysonar_scanner.exceptions import InconsistentConfiguration
from tests.unit import sq_api_utils
from tests.unit.sq_api_utils import sq_api_mocker

import unittest


class TestSQVersion(unittest.TestCase):
    def test_does_support_bootstrapping(self):
        self.assertTrue(SQVersion.from_str("10.6").does_support_bootstrapping())
        self.assertTrue(SQVersion.from_str("10.6.5").does_support_bootstrapping())
        self.assertTrue(SQVersion.from_str("10.6.5a").does_support_bootstrapping())
        self.assertTrue(SQVersion.from_str("10.7").does_support_bootstrapping())
        self.assertTrue(SQVersion.from_str("11.1").does_support_bootstrapping())
        self.assertTrue(SQVersion.from_str("11.1.1").does_support_bootstrapping())
        self.assertTrue(SQVersion.from_str("11").does_support_bootstrapping())

        self.assertFalse(SQVersion.from_str("9.9.9").does_support_bootstrapping())
        self.assertFalse(SQVersion.from_str("9.9.9a").does_support_bootstrapping())
        self.assertFalse(SQVersion.from_str("9.9").does_support_bootstrapping())
        self.assertFalse(SQVersion.from_str("9").does_support_bootstrapping())
        self.assertFalse(SQVersion.from_str("10.5").does_support_bootstrapping())
        self.assertFalse(SQVersion.from_str("10").does_support_bootstrapping())

        self.assertFalse(SQVersion.from_str("a").does_support_bootstrapping())
        self.assertFalse(SQVersion.from_str("1.a").does_support_bootstrapping())

    def test_str(self):
        self.assertEqual(str(SQVersion.from_str("10.6")), "10.6")
        self.assertEqual(str(SQVersion.from_str("9.9.9aa")), "9.9.9aa")


class TestApi(unittest.TestCase):
    def test_BaseUrls_normalization(self):
        self.assertEqual(
            BaseUrls("test1/", "test2/", is_sonar_qube_cloud=True),
            BaseUrls("test1", "test2", is_sonar_qube_cloud=True),
        )

    def test_get_base_urls(self):
        class TestCaseDict(TypedDict):
            name: str
            config: dict[Key, any]
            expected: BaseUrls

        cases: list[TestCaseDict] = [
            # SQ:Cloud tests
            {
                "name": "default configuration defaults to SQ:cloud base urls",
                "config": {
                    SONAR_HOST_URL: "",
                    SONAR_SCANNER_SONARCLOUD_URL: "",
                    SONAR_SCANNER_API_BASE_URL: "",
                    SONAR_REGION: "",
                },
                "expected": BaseUrls(
                    base_url="https://sonarcloud.io", api_base_url="https://api.sonarcloud.io", is_sonar_qube_cloud=True
                ),
            },
            {
                "name": "sonar.host.url with whitespaces uses the SQ:cloud base urls",
                "config": {
                    SONAR_HOST_URL: "  ",
                    SONAR_SCANNER_SONARCLOUD_URL: "",
                    SONAR_SCANNER_API_BASE_URL: "",
                    SONAR_REGION: "",
                },
                "expected": BaseUrls(
                    base_url="https://sonarcloud.io", api_base_url="https://api.sonarcloud.io", is_sonar_qube_cloud=True
                ),
            },
            {
                "name": "when host_url is set to SQ:cloud, use SQ:cloud base urls",
                "config": {
                    SONAR_HOST_URL: "https://sonarcloud.io",
                    SONAR_SCANNER_SONARCLOUD_URL: "",
                    SONAR_SCANNER_API_BASE_URL: "",
                    SONAR_REGION: "",
                },
                "expected": BaseUrls(
                    base_url="https://sonarcloud.io", api_base_url="https://api.sonarcloud.io", is_sonar_qube_cloud=True
                ),
            },
            {
                "name": "When both host_url and sonarcloud_url are set, use sonarcloud_url to check if host is SQ:cloud",
                "config": {
                    SONAR_HOST_URL: "https://sonarcloud.io",
                    SONAR_SCANNER_SONARCLOUD_URL: "https://custom-sq-cloud.io",
                    SONAR_SCANNER_API_BASE_URL: "",
                    SONAR_REGION: "",
                },
                "expected": BaseUrls(
                    base_url="https://sonarcloud.io",
                    api_base_url="https://sonarcloud.io/api/v2",
                    is_sonar_qube_cloud=False,
                ),
            },
            {
                "name": "when host_url with trailing slash is set to SQ:cloud, use SQ:cloud base urls",
                "config": {
                    SONAR_HOST_URL: "https://sonarcloud.io/",
                    SONAR_SCANNER_SONARCLOUD_URL: "",
                    SONAR_SCANNER_API_BASE_URL: "",
                    SONAR_REGION: "",
                },
                "expected": BaseUrls(
                    base_url="https://sonarcloud.io", api_base_url="https://api.sonarcloud.io", is_sonar_qube_cloud=True
                ),
            },
            # Region parameter
            {
                "name": "When region is set to US, use US base urls",
                "config": {
                    SONAR_HOST_URL: "/",
                    SONAR_SCANNER_SONARCLOUD_URL: "",
                    SONAR_SCANNER_API_BASE_URL: "",
                    SONAR_REGION: "us",
                },
                "expected": BaseUrls(
                    base_url="https://sonarqube.us", api_base_url="https://api.sonarqube.us", is_sonar_qube_cloud=True
                ),
            },
            {
                "name": "US region and US base url is fine",
                "config": {
                    SONAR_HOST_URL: "https://sonarqube.us",
                    SONAR_SCANNER_SONARCLOUD_URL: "",
                    SONAR_SCANNER_API_BASE_URL: "",
                    SONAR_REGION: "us",
                },
                "expected": BaseUrls(
                    base_url="https://sonarqube.us", api_base_url="https://api.sonarqube.us", is_sonar_qube_cloud=True
                ),
            },
            # SQ:Server tests
            {
                "name": "When host_url is set to SQ:server, use SQ:server base urls",
                "config": {
                    SONAR_HOST_URL: "https://sq.home",
                    SONAR_SCANNER_SONARCLOUD_URL: "",
                    SONAR_SCANNER_API_BASE_URL: "",
                    SONAR_REGION: "",
                },
                "expected": BaseUrls(
                    base_url="https://sq.home", api_base_url="https://sq.home/api/v2", is_sonar_qube_cloud=False
                ),
            },
            {
                "name": "When host_url with trailing slash is set to SQ:server, use SQ:server base urls",
                "config": {
                    SONAR_HOST_URL: "https://sq.home/",
                    SONAR_SCANNER_SONARCLOUD_URL: "",
                    SONAR_SCANNER_API_BASE_URL: "",
                    SONAR_REGION: "",
                },
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

    def test_inconsistent_urls_raises_exception(self):
        class TestCaseDict(TypedDict):
            name: str
            config: dict[Key, any]
            expected: str

        cases: list[TestCaseDict] = [
            {
                "name": "US region and global SQCloud URL",
                "config": {
                    SONAR_HOST_URL: "https://sonarcloud.io",
                    SONAR_SCANNER_SONARCLOUD_URL: "",
                    SONAR_SCANNER_API_BASE_URL: "",
                    SONAR_REGION: "us",
                },
                "expected": "Inconsistent values for properties 'sonar.region' and 'sonar.host.url'. "
                "Please only specify one of the two properties.",
            },
            {
                "name": "Region set with unknown SQCloud URL",
                "config": {
                    SONAR_HOST_URL: "https://custom-sq-cloud.io",
                    SONAR_SCANNER_SONARCLOUD_URL: "https://custom-sq-cloud.io",
                    SONAR_SCANNER_API_BASE_URL: "https://other-api.custom-sq-cloud.io",
                    SONAR_REGION: "us",
                },
                "expected": "Inconsistent values for properties 'sonar.region' and 'sonar.host.url'. "
                "Please only specify one of the two properties.",
            },
            {
                "name": "Unsupported region parameter",
                "config": {
                    SONAR_HOST_URL: "",
                    SONAR_SCANNER_SONARCLOUD_URL: "",
                    SONAR_SCANNER_API_BASE_URL: "",
                    SONAR_REGION: "fr",
                },
                "expected": "Invalid region 'fr'. Valid regions are: 'us'. "
                "Please check the 'sonar.region' property "
                "or the 'SONAR_REGION' environment variable.",
            },
        ]

        for case in cases:
            config = case["config"]
            expected = case["expected"]
            with self.subTest(case["name"], config=config, expected=expected):
                with self.assertRaises(InconsistentConfiguration, msg=expected):
                    get_base_urls(config)


class TestSonarQubeApiWithUnreachableSQServer(unittest.TestCase):
    def setUp(self):
        self.sq = SonarQubeApi(
            base_urls=BaseUrls("https://localhost:1000", "https://localhost:1000/api", is_sonar_qube_cloud=True),
            token="<invalid_token>",
        )

    def test_get_analysis_version(self):
        with self.assertRaises(SonarQubeApiException):
            self.sq.get_analysis_version()


class TestSonarQubeApi(unittest.TestCase):
    def setUp(self):
        self.sq = sq_api_utils.get_sq_server()

    def test_get_analysis_version(self):
        with self.subTest("/analysis/version returns 200"), sq_api_mocker() as mocker:
            mocker.mock_analysis_version("10.7")
            self.assertEqual(self.sq.get_analysis_version(), SQVersion.from_str("10.7"))

        with self.subTest("/analysis/version returns error"), sq_api_mocker() as mocker:
            mocker.mock_analysis_version(status=404)
            mocker.mock_server_version("10.8")
            self.assertEqual(self.sq.get_analysis_version(), SQVersion.from_str("10.8"))

        with (
            self.subTest("both version endpoints return error"),
            sq_api_mocker() as mocker,
            self.assertRaises(SonarQubeApiException),
        ):
            mocker.mock_analysis_version(status=404)
            mocker.mock_server_version(status=404)
            self.sq.get_analysis_version()

        with (
            self.subTest("request raises an exception"),
            sq_api_mocker() as mocker,
            self.assertRaises(SonarQubeApiException),
        ):
            self.sq.get_analysis_version()

    def test_get_analysis_engine(self):
        with self.subTest("get_analysis_engine works"), sq_api_mocker() as mocker:
            engine_info = EngineInfo(filename="sonar-scanner-engine-shaded-8.9.0.43852-all.jar", sha256="1234567890")
            mocker.mock_analysis_engine(filename=engine_info.filename, sha256=engine_info.sha256)
            self.assertEqual(self.sq.get_analysis_engine(), engine_info)

        with (
            self.subTest("get_analysis_engine returns error"),
            sq_api_mocker() as mocker,
            self.assertRaises(SonarQubeApiException),
        ):
            mocker.mock_analysis_engine(status=404)
            self.sq.get_analysis_engine()

        with (
            self.subTest("get_analysis_engine response misses sha256"),
            sq_api_mocker() as mocker,
            self.assertRaises(SonarQubeApiException),
        ):
            mocker.mock_analysis_engine(filename="sonar-scanner-engine-shaded-8.9.0.43852-all.jar")
            self.sq.get_analysis_engine()

    def test_download_analysis_engine(self):
        with self.subTest("download_analysis_engine works"), sq_api_mocker() as mocker:
            file_content = b"fake_engine_binary"
            mocker.mock_analysis_engine_download(body=file_content)
            fake_file = io.BytesIO()

            self.sq.download_analysis_engine(fake_file)

            self.assertEqual(fake_file.getvalue(), file_content)

        with (
            self.subTest("download_analysis_engine returns 404"),
            sq_api_mocker() as mocker,
            self.assertRaises(SonarQubeApiException),
        ):
            mocker.mock_analysis_engine_download(status=404)
            self.sq.download_analysis_engine(io.BytesIO())

        with (
            self.subTest("download_analysis_engine: requests throws exception"),
            sq_api_mocker() as mocker,
            self.assertRaises(SonarQubeApiException),
        ):
            # since the api is not mocked, requests will throw an exception
            self.sq.download_analysis_engine(io.BytesIO())

    def test_get_analysis_jres(self):
        expected_jres: list[JRE] = [
            JRE(
                id="jre1",
                filename="jre1.tar.gz",
                sha256="dummysha256value1",
                java_path="/path/to/jre1/bin/java",
                os="linux",
                arch="x64",
                download_url="https://example.com/jre1.tar.gz",
            ),
            JRE(
                id="jre2",
                filename="jre2.tar.gz",
                sha256="dummysha256value2",
                java_path="/path/to/jre2/bin/java",
                os="windows",
                arch="x64",
                download_url=None,
            ),
        ]

        with self.subTest("get_analysis_jres works (linux)"), sq_api_mocker() as mocker:
            mocker.mock_analysis_jres([sq_api_utils.jre_to_dict(jre) for jre in expected_jres])

            actual_jres = self.sq.get_analysis_jres(os="linux", arch="x64")
            self.assertEqual(actual_jres, expected_jres)

        with self.subTest("get_analysis_jres works (windows)"), sq_api_mocker() as mocker:
            mocker.mock_analysis_jres(
                [sq_api_utils.jre_to_dict(jre) for jre in expected_jres], os_matcher="windows", arch_matcher="aarch64"
            )
            actual_jres = self.sq.get_analysis_jres(os="windows", arch="aarch64")
            self.assertEqual(actual_jres, expected_jres)

        with (
            self.subTest("get_analysis_jres returns error"),
            sq_api_mocker() as mocker,
            self.assertRaises(SonarQubeApiException),
        ):
            mocker.mock_analysis_jres(status=404)
            self.sq.get_analysis_jres(os="linux", arch="x64")

        with (
            self.subTest("get_analysis_jres returns error when keys are missing"),
            sq_api_mocker() as mocker,
            self.assertRaises(SonarQubeApiException),
        ):
            mocker.mock_analysis_jres([{"id": "jre1"}])
            self.sq.get_analysis_jres(os="linux", arch="x64")

    def test_download_analysis_jre(self):
        jre_id = "jre1"
        jre_file_content = b"fake_jre_binary"
        with self.subTest("download_analysis_jre works"), sq_api_mocker() as mocker:
            mocker.mock_analysis_jre_download(id=jre_id, body=jre_file_content)
            fake_file = io.BytesIO()

            self.sq.download_analysis_jre(jre_id, fake_file)

            self.assertEqual(fake_file.getvalue(), jre_file_content)

        with self.subTest("download_analysis_jre works with redirect"), sq_api_mocker() as mocker:
            mocker.mock_analysis_jre_download(
                id=jre_id, status=302, redirect_url="/api/v2/analysis/jres/redirected-jre"
            )
            mocker.mock_analysis_jre_download(id="redirected-jre", body=jre_file_content)
            fake_file = io.BytesIO()

            self.sq.download_analysis_jre(jre_id, fake_file)

            self.assertEqual(fake_file.getvalue(), jre_file_content)

        with (
            self.subTest("download_analysis_jre returns 404"),
            sq_api_mocker() as mocker,
            self.assertRaises(SonarQubeApiException),
        ):
            mocker.mock_analysis_jre_download(id=jre_id, status=404)
            self.sq.download_analysis_jre(jre_id, io.BytesIO())

        with (
            self.subTest("download_analysis_jre: requests throws exception"),
            sq_api_mocker() as mocker,
            self.assertRaises(SonarQubeApiException),
        ):
            # since the api is not mocked, requests will throw an exception
            self.sq.download_analysis_jre(jre_id, io.BytesIO())

    def test_to_api_configuration(self):
        with self.subTest("Missing keys"):
            expected = {
                SONAR_HOST_URL: "",
                SONAR_SCANNER_SONARCLOUD_URL: "",
                SONAR_SCANNER_API_BASE_URL: "",
                SONAR_REGION: "",
            }
            self.assertEqual(expected, api.to_api_configuration({}))

        with self.subTest("All keys"):
            expected = {
                SONAR_HOST_URL: "https://sonarcloud.io",
                SONAR_SCANNER_SONARCLOUD_URL: "https://sonarcloud.io",
                SONAR_SCANNER_API_BASE_URL: "https://api.sonarcloud.io",
                SONAR_REGION: "us",
            }
            self.assertEqual(expected, api.to_api_configuration(expected))
