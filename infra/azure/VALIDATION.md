# Platform foundation validation

Local and Azure validation completed. The approved development deployment in East US 2 reports Succeeded. All three private endpoints report Succeeded with Approved connections. Data-plane acceptance from a private client has not run. Full deployment output remains in ignored local files.

## Command evidence

`az bicep build --file infra/main.bicep` (invoked by `platform.ps1 -Action Validate`, output directed to a unique temporary file): exit 0, no warnings or errors. Bicep 0.47.16.

```text
Bicep compilation passed. Run Checkov separately; no Azure changes made.
```

`./infra/azure/Test-PlatformGuards.ps1`: exit 0. Azure CLI is stubbed; this verifies command behavior without cloud access.

```text
PASS: deployment guards and missing/invalid local context (8 cases).
```

`checkov -d infra/ --framework bicep --compact --quiet`: exit 0, Checkov 3.3.20.

```text
Passed checks: 18, Failed checks: 0, Skipped checks: 1
```

`CKV_AZURE_166` is an explicit exception for registry quarantine pending a scanner/release workflow. See README. Checkov is a limited static scan, not proof of runtime security, vulnerability scanning coverage or production approval. Its Windows launcher also printed `File association not found for extension .py`; the scanner ran and returned the results above.

`git diff --check`: exit 0.

## Completion self-check

- PASS: Bicep validation exited cleanly; output shown above.
- PASS WITH EXCEPTION: Checkov ran with zero failed checks; one explicit quarantine exception remains.
- PASS (static): public PaaS access disabled, private endpoints and DNS wired, local authentication disabled where exposed, managed identities and scoped registry roles, Key Vault recovery protection, no secrets or credentials in outputs. TLS behavior requires live service acceptance; NSGs permit HTTPS only.
- PASS: inventory was empty in the verified company subscription, so no existing resources were recreated or modified.
- PASS: implementation is under `infra/`, validation workflow under `.github/`, planning artifacts under `.azure/`; original architecture diagrams and pre-Azure governance records are unchanged.
- PASS: user approval, ARM validation/what-if and deployment in East US 2. Live checks confirm private endpoints are approved, Key Vault RBAC/purge protection enabled, and public access disabled.
- PENDING: private-client DNS/RBAC/diagnostic acceptance and production evidence gates.

Deployment correction: Azure rejected an Allow rule targeting AzurePlatformDNS. The rule now targets the Azure DNS address 168.63.129.16. The incremental retry retained the existing resources and succeeded. See https://learn.microsoft.com/en-us/azure/virtual-network/what-is-ip-address-168-63-129-16 for platform DNS behavior.
