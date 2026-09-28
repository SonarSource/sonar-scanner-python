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
from pathlib import Path

import pytest

from pysonar_scanner.cache import Cache
from pysonar_scanner.jre import JREProvisioner
from pysonar_scanner.scannerengine import ScannerEngineProvisioner
from tests.unit import sq_api_utils


@pytest.mark.parametrize("artifact", ["jre", "engine"])
def test_rejects_path_in_server_filename_before_downloading(tmp_path: Path, artifact: str) -> None:
    cache = Cache.create_cache(tmp_path / "cache")
    api = sq_api_utils.get_sq_server()
    outside_path = tmp_path / "outside.bin"
    outside_content = b"existing file outside the cache"
    outside_path.write_bytes(outside_content)
    filename = "../outside.bin"
    download_content = b"test content"
    checksum = "6ae8a75555209fd6c44157c0aed8016e763ff435a19cf186f76863140143ff72"

    with sq_api_utils.sq_api_mocker(assert_all_requests_are_fired=False) as mocker:
        provisioner: JREProvisioner | ScannerEngineProvisioner
        if artifact == "jre":
            metadata_rsps = mocker.mock_analysis_jres(
                body=[
                    {
                        "id": "jre",
                        "filename": filename,
                        "sha256": checksum,
                        "javaPath": "bin/java",
                        "os": "linux",
                        "arch": "x64",
                    }
                ]
            )
            api_download_rsps = mocker.mock_analysis_jre_download(id="jre", body=download_content)
            provisioner = JREProvisioner(api, cache, "linux", "x64")
        else:
            metadata_rsps = mocker.mock_analysis_engine(filename=filename, sha256=checksum)
            api_download_rsps = mocker.mock_analysis_engine_download(body=download_content)
            provisioner = ScannerEngineProvisioner(api, cache)

        with pytest.raises(ValueError) as error:
            provisioner.provision()

        assert str(error.value) == "Invalid cache filename '../outside.bin': expected a plain filename."
        assert outside_path.read_bytes() == outside_content
        assert list(cache.cache_folder.iterdir()) == []
        assert metadata_rsps.call_count == 1
        assert api_download_rsps.call_count == 0
