"""Bounded reference assurance tools; cloud execution requires a private Azure client.

No deployment, role change, account key, existing-data deletion or notification send.
Recovery creates its own disposable container and retains it after successful restore.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import ipaddress
import json
from itertools import islice
import os
from pathlib import Path
import re
import socket
import subprocess
import time
import uuid

RESOURCE_GROUP = "rg-iyqpis-dev-platform"
WORKSPACE = "log-iyqpis-dev"
ACTION_GROUP = "ag-iyqpis-dev-operations"
JOB = "job-iyqpis-dev-data"


class AssuranceError(ValueError):
    """A bounded, safe-to-record guard failure."""


def field(value, name, default=None):
    return value.get(name, default) if isinstance(value, dict) else getattr(value, name, default)


def require(condition, message):
    if not condition:
        raise AssuranceError(message)


def az(*arguments):
    result = subprocess.run(["az", *arguments, "--only-show-errors", "-o", "json"],
                            capture_output=True, text=True, timeout=120)
    require(result.returncode == 0, "Azure command failed; inspect access privately. Raw service errors are not copied to evidence.")
    return json.loads(result.stdout)


def verify_context(context):
    for key in ("subscriptionId", "tenantId"):
        require(str(uuid.UUID(context[key])) == context[key].lower(), "Invalid expected Azure context")
    require(context.get("accountEmail") and "REPLACE" not in context["accountEmail"].upper(), "Expected account is required")
    actual = az("account", "show")
    require(actual.get("id", "").lower() == context["subscriptionId"].lower()
            and actual.get("tenantId", "").lower() == context["tenantId"].lower()
            and actual.get("user", {}).get("name", "").lower() == context["accountEmail"].lower(), "Wrong Azure context")


def private_dns(host):
    addresses = {item[4][0] for item in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)}
    networks = [ipaddress.ip_network(n) for n in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")]
    require(addresses and all(any(ipaddress.ip_address(a) in n for n in networks) for a in addresses),
            "Storage must resolve exclusively to private IPv4 addresses")


def retention_ready(read_retention):
    # The pinned Blob SDK's get_service_properties omits container retention.
    # Read the management-plane containerDeleteRetentionPolicy explicitly.
    policy = read_retention()
    require(field(policy, "enabled") is True and isinstance(field(policy, "days"), int)
            and 7 <= field(policy, "days") <= 30, "Reviewed container soft-delete retention of 7–30 days is required")


def recover(service, read_retention, *, approve=False, evidence=None, before_delete=lambda: None, pause=time.sleep,
            checkpoint=lambda evidence: None):
    """Exercise whole-container soft delete; never accepts an existing target name."""
    require(approve, "Pass --approve-disposable-recovery after reviewing the disposable-container scope")
    evidence = evidence if evidence is not None else {}
    evidence.update(status="started", scope="disposable container recovery", production_rto_verified=False)
    retention_ready(read_retention)  # Fail before creation when recovery is not configured.
    run_id = uuid.uuid4().hex
    name = "iyqpis-recovery-" + run_id
    payload = os.urandom(512)
    digest = hashlib.sha256(payload).hexdigest()
    evidence.update(container=name, run_id=run_id, expected_sha256=digest, phase="creating")
    checkpoint(evidence)
    # create_container refuses existing names; no overwrite or user-supplied target.
    container = service.create_container(name, metadata={"purpose": "iyqpis-recovery-drill", "run_id": run_id})
    evidence["phase"] = "created"
    blob = container.get_blob_client("probe.bin")
    blob.upload_blob(payload, overwrite=False)
    require(hashlib.sha256(blob.download_blob().readall()).hexdigest() == digest, "Initial probe checksum mismatch")
    before_delete()
    retention_ready(read_retention)
    metadata = field(container.get_container_properties(), "metadata", {})
    require(metadata.get("purpose") == "iyqpis-recovery-drill" and metadata.get("run_id") == run_id,
            "Disposable container ownership changed")
    objects = list(islice(container.list_blobs(), 2))
    require(len(objects) == 1 and field(objects[0], "name") == "probe.bin", "Unexpected contents; deletion refused")
    started = time.monotonic()
    evidence["phase"] = "delete_requested"
    checkpoint(evidence)  # Persist the unique target before any deletion.
    container.delete_container()
    require(container.exists() is False, "Deleted container is still active; restore not established")
    evidence["phase"] = "deleted"
    version = None
    for attempt in range(15):
        matches = [item for item in service.list_containers(name_starts_with=name, include_deleted=True)
                   if field(item, "name") == name and field(item, "deleted") is True]
        require(len(matches) <= 1, "Ambiguous deleted container version; automatic restore refused")
        if matches:
            version = field(matches[0], "version")
            require(isinstance(version, str) and version, "Deleted container version missing")
            break
        if attempt < 14:
            pause(2)
    require(version, "Deleted container version not visible; retain evidence for operator recovery")
    evidence.update(deleted_container_version=version, phase="restore_requested")
    checkpoint(evidence)
    restored = service.undelete_container(deleted_container_name=name, deleted_container_version=version)
    actual = hashlib.sha256(restored.get_blob_client("probe.bin").download_blob().readall()).hexdigest()
    require(actual == digest, "Restored probe checksum mismatch")
    evidence.update(status="passed", phase="restored", restored_sha256=actual,
                    delete_to_verified_restore_seconds=round(time.monotonic() - started, 3),
                    retained_disposable_container=name)
    return evidence


def diagnostic(run_id):
    require(re.fullmatch(r"[a-f0-9]{32}", run_id), "Diagnostic run ID must be 32 lowercase hexadecimal characters")
    return dict(event_type="iyqpis_monitoring", schema_version=1, scope="reference_diagnostic",
                diagnostic=True, diagnostic_run_id=run_id, status="failed", data_quality_passed=False,
                performance_passed=None, drift_review_required=None)


def inspect_monitoring(context, run_id):
    diagnostic(run_id)  # Validate before inserting into a KQL string.
    root = f"/subscriptions/{context['subscriptionId']}/resourceGroups/{RESOURCE_GROUP}"
    workspace_id = root + f"/providers/Microsoft.OperationalInsights/workspaces/{WORKSPACE}"
    group_id = root + f"/providers/Microsoft.Insights/actionGroups/{ACTION_GROUP}"
    workspace = az("rest", "--method", "get", "--url", "https://management.azure.com" + workspace_id + "?api-version=2025-02-01")
    expected_customer = str(uuid.UUID(workspace["properties"]["customerId"]))
    group = az("rest", "--method", "get", "--url", "https://management.azure.com" + group_id + "?api-version=2023-01-01")["properties"]
    receiver_count = sum(len(value) for key, value in group.items() if key.endswith("Receivers") and isinstance(value, list))
    group_ready = group.get("enabled") is True and receiver_count > 0
    rules = []
    for suffix in ("job-failure", "model-data-health"):
        rule_id = root + "/providers/Microsoft.Insights/scheduledQueryRules/alert-iyqpis-dev-" + suffix
        rule = az("rest", "--method", "get", "--url", "https://management.azure.com" + rule_id + "?api-version=2023-12-01")
        properties = rule["properties"]
        rules.append(dict(name=suffix, enabled=properties.get("enabled") is True,
                          expected_scope=workspace_id.lower() in [s.lower() for s in properties.get("scopes", [])],
                          expected_action_group=group_id.lower() in [s.lower() for s in properties.get("actions", {}).get("actionGroups", [])]))
    query = (f"ContainerAppConsoleLogs | where TimeGenerated >= ago(2h) | where JobName startswith '{JOB}' "
             "| extend event=parse_json(Log) "
             f"| where tostring(event.diagnostic_run_id) == '{run_id}' and tostring(event.diagnostic) == 'true' "
             "| summarize matching_events=count(), failure_events=countif(tostring(event.status) == 'failed')")
    rows = az("monitor", "log-analytics", "query", "--workspace", expected_customer, "--analytics-query", query)
    require(isinstance(rows, list) and len(rows) == 1, "Unexpected log-query response; cannot infer ingestion")
    matched, failures = int(rows[0]["matching_events"]), int(rows[0]["failure_events"])
    return dict(status="observed" if matched > 0 and failures > 0 and group_ready and all(all(r[k] for k in ("enabled", "expected_scope", "expected_action_group")) for r in rules) else "pending",
                scope="read-only monitoring observation", diagnostic_run_id=run_id, rules=rules,
                action_group_enabled=group.get("enabled") is True, action_group_receiver_count=receiver_count,
                matching_events=matched, failure_events=failures, notification_delivery_verified=False,
                end_to_end_verified=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("recover", "inspect", "emit-diagnostic"))
    parser.add_argument("--context", type=Path, default=Path(__file__).with_name("context.local.json"))
    parser.add_argument("--storage-account")
    parser.add_argument("--run-id")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--approve-disposable-recovery", action="store_true")
    args = parser.parse_args()
    if args.action == "emit-diagnostic":
        print(json.dumps(diagnostic(args.run_id or "")), flush=True)
        return 1  # Clearly marked diagnostic failure; run only in reviewed job override.
    require(args.output, "An output evidence file is required")
    # Refuse to overwrite historical evidence, including on a failed attempt.
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as output:
        def checkpoint(record):
            output.seek(0)
            json.dump(record, output, indent=2)
            output.write("\n")
            output.truncate()
            output.flush()
            os.fsync(output.fileno())

        evidence = {"status": "started", "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
                    "live_cloud_completed": False, "production_release": "BLOCKED"}
        try:
            if args.action == "recover":
                require(args.approve_disposable_recovery, "Explicit disposable-recovery approval is required")
            context = json.loads(args.context.read_text())
            verify_context(context)
            if args.action == "inspect":
                evidence.update(inspect_monitoring(context, args.run_id or ""))
            else:
                require(re.fullmatch(r"[a-z0-9]{3,24}", args.storage_account or ""), "Invalid storage account")
                account = az("storage", "account", "show", "-g", RESOURCE_GROUP, "-n", args.storage_account)
                require(account.get("publicNetworkAccess") == "Disabled" and account.get("allowSharedKeyAccess") is False
                        and account.get("location", "").replace(" ", "").lower() == "eastus2", "Unexpected storage boundary")
                host = args.storage_account + ".blob.core.windows.net"
                private_dns(host)
                policy_url = (f"https://management.azure.com/subscriptions/{context['subscriptionId']}/resourceGroups/{RESOURCE_GROUP}"
                              f"/providers/Microsoft.Storage/storageAccounts/{args.storage_account}/blobServices/default?api-version=2023-05-01")
                def read_retention():
                    return az("rest", "--method", "get", "--url", policy_url)["properties"].get("containerDeleteRetentionPolicy")
                from azure.identity import AzureCliCredential
                from azure.storage.blob import BlobServiceClient
                with AzureCliCredential(tenant_id=context["tenantId"]) as credential:
                    with BlobServiceClient("https://" + host, credential=credential,
                                           connection_timeout=10, read_timeout=30, retry_total=2) as service:
                        recover(service, read_retention, approve=True, evidence=evidence, before_delete=lambda: verify_context(context),
                                checkpoint=checkpoint)
            evidence["live_cloud_completed"] = True
            return 0 if evidence["status"] in ("passed", "observed") else 2
        except Exception as error:
            evidence.update(status="failed", error_type=type(error).__name__)
            if isinstance(error, AssuranceError):
                evidence["reason"] = str(error)
            return 1
        finally:
            checkpoint(evidence)
            print(json.dumps({"status": evidence["status"], "evidence": str(args.output)}))


if __name__ == "__main__":
    raise SystemExit(main())
