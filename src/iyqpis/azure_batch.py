"""On-demand Azure entrypoint: private raw lake -> batch -> verified immutable outputs."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import socket
import ipaddress
import tempfile

from iyqpis.build_validated import ADAPTERS
from iyqpis.pipeline import build_run, verify_run


def require_private_dns(host: str) -> None:
    addresses = {item[4][0] for item in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)}
    networks = [ipaddress.ip_network(prefix) for prefix in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")]
    if not addresses or any(not any(ipaddress.ip_address(address) in network for network in networks) for address in addresses):
        raise ValueError("Storage must resolve exclusively to private IPv4 addresses")


def raw_destination(root: Path, name: str, dataset: str) -> Path:
    key = PurePosixPath(name)
    if "\\" in name or key.is_absolute() or ".." in key.parts or not key.parts or key.parts[0] != dataset:
        raise ValueError("Unsafe raw blob path")
    path = root.joinpath(*key.parts).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Raw blob escapes local directory")
    return path


def remote_digest(blob) -> str:
    h = hashlib.sha256()
    for chunk in blob.download_blob().chunks():
        h.update(chunk)
    return h.hexdigest()


def put_verified(blob, path: Path, expected: str) -> None:
    from azure.core.exceptions import ResourceExistsError
    with path.open("rb") as source:
        try:
            blob.upload_blob(source, blob_type="BlockBlob", overwrite=False, metadata={"sha256": expected})
        except ResourceExistsError:
            pass  # Retry only succeeds if the existing bytes are identical.
    if remote_digest(blob) != expected:
        raise ValueError("Published blob checksum mismatch; existing data was not overwritten")


def publish(service, run: Path) -> dict:
    manifest = verify_run(run)
    for artifact in manifest["artifacts"]:
        container, relative = artifact["path"].split("/", 1)
        if container not in {"validated", "contextualized", "curated-evidence"}:
            raise ValueError("Unapproved output container")
        blob = service.get_blob_client(container, f"runs/{run.name}/{relative}")
        put_verified(blob, run / artifact["path"], artifact["sha256"])
    # Consumers must use this last-written marker, never partially populated prefixes.
    marker = run / "manifest.json"
    put_verified(service.get_blob_client("curated-evidence", f"runs/{run.name}/manifest.json"), marker,
                 hashlib.sha256(marker.read_bytes()).hexdigest())
    return {"status": "complete", "run_id": run.name, "artifacts": len(manifest["artifacts"])}


def main() -> None:
    from azure.identity import ManagedIdentityCredential
    from azure.storage.blob import BlobServiceClient
    account = os.environ["DATA_STORAGE_ACCOUNT"]
    if not re.fullmatch(r"[a-z0-9]{3,24}", account):
        raise ValueError("Invalid storage account")
    host = f"{account}.blob.core.windows.net"
    require_private_dns(host)
    selected = os.environ.get("DATASETS", "manufacturing-spc").split(",")
    if any(name not in ADAPTERS for name in selected):
        raise ValueError("Unknown dataset")
    # Required explicit timestamp makes retries deterministic; no clock-based default.
    ingest_time = os.environ["INGEST_TIME"]
    credential = ManagedIdentityCredential(client_id=os.environ["AZURE_CLIENT_ID"])
    with credential, BlobServiceClient(f"https://{host}", credential=credential) as service:
        with tempfile.TemporaryDirectory(prefix="iyqpis-batch-") as directory:
            root = Path(directory)
            raw = root / "raw"
            container = service.get_container_client("raw")
            for dataset in selected:
                for blob in container.list_blobs(name_starts_with=dataset + "/"):
                    if blob.name.endswith("/") or getattr(blob, "size", None) == 0:
                        continue
                    target = raw_destination(raw, blob.name, dataset)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with target.open("wb") as output:
                        # Pin each download to the ETag from enumeration.
                        from azure.core import MatchConditions
                        container.download_blob(blob.name, etag=blob.etag,
                                                match_condition=MatchConditions.IfNotModified).readinto(output)
            run = build_run(raw, root / "runs", ingest_time, selected)
            print(json.dumps(publish(service, run)))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        # Azure SDK messages can contain resource URLs and IDs. Do not log row payloads.
        print(json.dumps({"status": "failed", "error_type": type(error).__name__}))
        raise SystemExit(1) from None
