from io import BytesIO
import hashlib
import json
from pathlib import Path

import pytest

from iyqpis import azure_batch
from iyqpis.pipeline import digest, write_json


def run_fixture(tmp_path):
    run = tmp_path / "test-run"
    path = run / "validated/fixture/telemetry.jsonl"
    path.parent.mkdir(parents=True)
    path.write_bytes(b'{"example": 1}\n')
    write_json(run / "manifest.json", {"run_id": run.name, "status": "complete",
               "artifacts": [{"path": path.relative_to(run).as_posix(), "sha256": digest(path)}]})
    return run


class Service:
    def get_blob_client(self, container, blob):
        return container, blob


def test_manifest_is_last_and_failed_upload_has_no_commit(tmp_path, monkeypatch):
    run = run_fixture(tmp_path)
    writes = []
    monkeypatch.setattr(azure_batch, "put_verified", lambda blob, path, checksum: writes.append(blob))
    azure_batch.publish(Service(), run)
    assert writes[-1] == ("curated-evidence", "runs/test-run/manifest.json")
    writes.clear()
    def fail(blob, path, checksum):
        writes.append(blob)
        raise ConnectionError("interrupted")
    monkeypatch.setattr(azure_batch, "put_verified", fail)
    with pytest.raises(ConnectionError):
        azure_batch.publish(Service(), run)
    assert all(not name.endswith("manifest.json") for _, name in writes)


@pytest.mark.parametrize("name", ["../outside", "/fixture/file", "fixture/../../outside", "fixture\\file", "wrong/file"])
def test_remote_paths_cannot_escape(tmp_path, name):
    with pytest.raises(ValueError):
        azure_batch.raw_destination(tmp_path, name, "fixture")


def test_public_or_mixed_dns_rejected(monkeypatch):
    monkeypatch.setattr(azure_batch.socket, "getaddrinfo", lambda *a, **k: [(2, 1, 6, "", ("10.80.0.5", 443)),
                                                                         (2, 1, 6, "", ("20.1.2.3", 443))])
    with pytest.raises(ValueError, match="private"):
        azure_batch.require_private_dns("example.blob.core.windows.net")


def test_existing_output_must_match_bytes(tmp_path):
    from azure.core.exceptions import ResourceExistsError
    path = tmp_path / "output"
    path.write_bytes(b"expected")
    class Blob:
        def upload_blob(self, stream, **kwargs):
            assert kwargs["overwrite"] is False
            raise ResourceExistsError("exists")
        def download_blob(self):
            return self
        def chunks(self):
            yield b"different"
    with pytest.raises(ValueError, match="checksum"):
        azure_batch.put_verified(Blob(), path, digest(path))
