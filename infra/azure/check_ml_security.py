"""Check the compiled reference ML template behind four scoped scanner dispositions.

This validates source configuration, not deployed networking or cloud recovery.
Fail closed when the bounded workspace design changes; reassess the dispositions.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def compact(value):
    return re.sub(r"\s+", "", str(value))


def resources(template):
    for resource in template.get("resources", []):
        yield resource
        nested = resource.get("properties", {}).get("template")
        if nested:
            yield from resources(nested)


def only(items, description):
    values = list(items)
    require(len(values) == 1, f"Expected exactly one {description}")
    return values[0]


def validate(template):
    all_resources = list(resources(template))
    workspaces = [r for r in all_resources if r["type"].lower().startswith("microsoft.machinelearningservices/")]
    require(len(workspaces) == 1 and workspaces[0]["type"].lower() == "microsoft.machinelearningservices/workspaces",
            "Reference disposition forbids ML compute, endpoints and scope expansion")
    workspace = workspaces[0]
    storage = only((r for r in all_resources if r["type"].lower() == "microsoft.storage/storageaccounts"), "ML storage account")
    require(compact(storage["name"]) == "[format('stml{0}',uniqueString(resourceGroup().id))]", "Storage naming expression changed; review evaluated name")
    require(storage["sku"]["name"] == "Standard_LRS", "Storage replication policy changed; review reference disposition")
    for resource in (storage, workspace):
        require(resource.get("tags") == "[variables('tags')]",
                "Reference purpose tag must use governed tags")
        require(resource["properties"].get("publicNetworkAccess") == "Disabled", "Public access must be disabled")
    require(template.get("variables", {}).get("tags", {}).get("purpose") == "temporary-learning", "Reference-only purpose changed")
    sp = storage["properties"]
    require(sp.get("allowBlobPublicAccess") is False and sp.get("allowSharedKeyAccess") is False,
            "Anonymous/shared-key storage access must stay disabled")
    require(sp.get("defaultToOAuthAuthentication") is True and sp.get("supportsHttpsTrafficOnly") is True
            and sp.get("minimumTlsVersion") == "TLS1_2", "Storage authentication/transport boundary changed")
    require(sp.get("networkAcls", {}).get("defaultAction") == "Deny" and sp["networkAcls"].get("bypass") == "None",
            "Storage must deny public traffic with no trusted-service bypass")
    wp = workspace["properties"]
    require(workspace.get("identity", {}).get("type") == "SystemAssigned"
            and wp.get("systemDatastoresAuthMode") == "identity", "Workspace must use identity-based storage")
    require(wp.get("managedNetwork", {}).get("isolationMode") == "Disabled"
            and not wp.get("managedNetwork", {}).get("outboundRules"), "Managed compute networking requires a new review")
    expected_storage = "[resourceId('Microsoft.Storage/storageAccounts',format('stml{0}',uniqueString(resourceGroup().id)))]"
    require(compact(wp.get("storageAccount")) == expected_storage, "Workspace must use the guarded storage account")
    endpoints = {"workspace": ("amlworkspace", "[resourceId('Microsoft.MachineLearningServices/workspaces',parameters('workspaceName'))]", 2),
                 "blob": ("blob", expected_storage, 1), "file": ("file", expected_storage, 1)}
    for label, (group, target, dns_count) in endpoints.items():
        module = only((r for r in template["resources"] if r.get("name") == f"ml-learning-{label}-endpoint"), f"{label} endpoint module")
        params = module["properties"]["parameters"]
        require(params["groupId"]["value"] == group and compact(params["targetId"]["value"]) == target,
                f"{label} endpoint targets the wrong service")
        require("snet-private-endpoints" in params["subnetId"]["value"], f"{label} endpoint subnet changed")
        dns = params["dnsZoneIds"]["value"]
        require(isinstance(dns, list) and len(dns) == dns_count, f"{label} DNS association missing")
        nested = list(resources(module["properties"]["template"]))
        endpoint = only((r for r in nested if r["type"].lower() == "microsoft.network/privateendpoints"), f"{label} private endpoint")
        properties = endpoint["properties"]
        require(properties.get("subnet", {}).get("id") == "[parameters('subnetId')]", f"{label} subnet is disconnected")
        connection = only(properties.get("privateLinkServiceConnections", []), f"{label} private connection")["properties"]
        require(connection.get("privateLinkServiceId") == "[parameters('targetId')]"
                and connection.get("groupIds") == ["[parameters('groupId')]"], f"{label} private connection is disconnected")
        zone = only((r for r in nested if r["type"].lower() == "microsoft.network/privateendpoints/privatednszonegroups"), f"{label} DNS zone group")
        require("dnsZoneIds" in json.dumps(zone["properties"]), f"{label} DNS parameter is disconnected")
    return {"status": "passed", "scope": "compiled reference ML configuration", "live_cloud_verified": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("template", type=Path)
    args = parser.parse_args()
    print(json.dumps(validate(json.loads(args.template.read_text()))))
