"""Read-only acceptance probe, executed inside the private data job network."""
import json
import os
import re
from datetime import datetime

from azure.identity import ManagedIdentityCredential
from azure.storage.blob import BlobServiceClient
from iyqpis.azure_batch import remote_digest, require_private_dns


def main():
    account = os.environ["DATA_STORAGE_ACCOUNT"]
    run_id = os.environ["DATA_RUN_ID"]
    if not re.fullmatch(r"[a-z0-9]{3,24}", account) or not re.fullmatch(r"[a-f0-9]{32}", run_id):
        raise ValueError("Invalid acceptance target")
    replay_start = datetime.fromisoformat(os.environ["REPLAY_STARTED_AT"].replace("Z", "+00:00"))
    host = f"{account}.blob.core.windows.net"
    require_private_dns(host)
    with ManagedIdentityCredential(client_id=os.environ["AZURE_CLIENT_ID"]) as identity:
        with BlobServiceClient(f"https://{host}", credential=identity) as service:
            marker = service.get_blob_client("curated-evidence", f"runs/{run_id}/manifest.json")
            manifest = json.loads(marker.download_blob().readall())
            if manifest["run_id"] != run_id or manifest["status"] != "complete":
                raise ValueError("Invalid completion marker")
            unchanged = marker.get_blob_properties().last_modified < replay_start
            records = 0
            for artifact in manifest["artifacts"]:
                container, path = artifact["path"].split("/", 1)
                if container not in {"validated", "contextualized", "curated-evidence"} or ".." in path.split("/"):
                    raise ValueError("Invalid artifact path")
                blob = service.get_blob_client(container, f"runs/{run_id}/{path}")
                if remote_digest(blob) != artifact["sha256"]:
                    raise ValueError("Remote checksum mismatch")
                unchanged = unchanged and blob.get_blob_properties().last_modified < replay_start
                if container == "validated":
                    records += artifact["records"]
            if not unchanged or records != 1104500 or len(manifest["artifacts"]) != 16 or len(manifest["datasets"]) != 5:
                raise ValueError("Full-run replay acceptance failed")
            print(json.dumps({"status": "verified", "run_id": run_id, "datasets": 5,
                              "validated_records": records, "artifacts": 16,
                              "remote_checksums_match": True, "unchanged_since_before_replay": True}))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(json.dumps({"status": "failed", "error_type": type(error).__name__}))
        raise SystemExit(1) from None
