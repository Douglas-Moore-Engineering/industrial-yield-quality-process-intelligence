"""On-demand reference AI validation inside the existing private Azure job."""
import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile

from azure.identity import ManagedIdentityCredential
from azure.storage.blob import BlobServiceClient

from iyqpis.azure_batch import put_verified, require_private_dns
from iyqpis.intelligence import train, verify_bundle
from iyqpis.pipeline import digest, verify_run, write_json
from iyqpis.reference import validate_reference


def main():
    account, run_id = os.environ["DATA_STORAGE_ACCOUNT"], os.environ["DATA_RUN_ID"]
    if not re.fullmatch(r"[a-z0-9]{3,24}", account) or not re.fullmatch(r"[a-f0-9]{32}", run_id):
        raise ValueError("Invalid source target")
    host = f"{account}.blob.core.windows.net"
    require_private_dns(host)
    with ManagedIdentityCredential(client_id=os.environ["AZURE_CLIENT_ID"]) as identity:
        with BlobServiceClient(f"https://{host}", credential=identity) as service:
            with tempfile.TemporaryDirectory(prefix="iyqpis-ai-") as temporary:
                root = Path(temporary)
                run = root / "data" / run_id
                run.mkdir(parents=True)
                marker = service.get_blob_client("curated-evidence", f"runs/{run_id}/manifest.json")
                manifest_bytes = marker.download_blob().readall()
                manifest = json.loads(manifest_bytes)
                if manifest["run_id"] != run_id or manifest["status"] != "complete":
                    raise ValueError("Invalid source manifest")
                for item in manifest["artifacts"]:
                    path = PurePosixPath(item["path"])
                    if path.is_absolute() or ".." in path.parts or "\\" in item["path"] or len(path.parts) < 2:
                        raise ValueError("Unsafe artifact path")
                    container, relative = path.parts[0], '/'.join(path.parts[1:])
                    if container not in {"validated", "contextualized", "curated-evidence"}:
                        raise ValueError("Unexpected source container")
                    target = run / path
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with target.open("wb") as stream:
                        service.get_blob_client(container, f"runs/{run_id}/{relative}").download_blob().readinto(stream)
                    if digest(target) != item["sha256"]:
                        raise ValueError("Source checksum mismatch")
                (run / "manifest.json").write_bytes(manifest_bytes)
                verify_run(run)
                bundle = train(run, root / "models")
                model = verify_bundle(bundle)
                report = validate_reference(run, bundle, root / "reference")
                evaluation = json.loads((bundle / "evaluation.json").read_text())
                prefix = f"models/{model['model_id']}"
                files = [(bundle / name, name) for name in ("model.json", "evaluation.json", "test-predictions.json", "manifest.json")]
                files.append((root / "reference/reference-validation.json", "reference-validation.json"))
                for source, name in files:
                    put_verified(service.get_blob_client("curated-evidence", f"{prefix}/{name}"), source, digest(source))
                completion = root / "release.json"
                write_json(completion, {"status": "complete", "scope": "reference_validation_only",
                           "model_id": model["model_id"], "data_run_id": run_id, "production_release": "BLOCKED",
                           "artifacts": [{"path": name, "sha256": digest(source)} for source, name in files]})
                put_verified(service.get_blob_client("curated-evidence", f"{prefix}/release.json"), completion, digest(completion))
                print(json.dumps({"status": "complete", "model_id": model["model_id"], "data_run_id": run_id,
                                  "artifacts": len(files), "production_release": "BLOCKED",
                                  "test_average_precision": evaluation["test"]["average_precision"],
                                  "test_recall": evaluation["test"]["recall"],
                                  "stale_abstains": report["stale_abstains"],
                                  "unknown_domain_abstains": report["unknown_domain_abstains"]}))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(json.dumps({"status": "failed", "error_type": type(error).__name__}))
        raise SystemExit(1) from None
