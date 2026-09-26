# Azure Entry Gate

## Table of contents

- [Purpose](#purpose)
- [Required evidence](#required-evidence)
- [What is intentionally not selected yet](#what-is-intentionally-not-selected-yet)
- [Next phase](#next-phase)

## Purpose

Azure architecture mapping begins only after cloud-agnostic requirements and operating evidence are stable enough to make infrastructure choices defensible.

## Required evidence

See [azure_entry_criteria.csv](../governance/azure_entry_criteria.csv).

Required evidence includes:
- canonical schemas/data contracts
- measured event rate, burst and retention
- latency/warning-horizon target
- approved OT trust boundary
- identity/authorization matrix
- data classification and retention
- model release/evidence manifest
- RPO/RTO and availability targets
- pilot acceptance thresholds
- accepted trade studies and ADRs
- reviewed threat model
- measured cost-model inputs

## What is intentionally not selected yet

No Azure service, SKU, region, subscription hierarchy, VNet topology, private endpoint plan, storage tier, compute SKU, ML workspace or IaC resource is considered approved merely because it appears in a future design option.

## Next phase

The next phase maps each architecture capability to Azure alternatives, performs documented trade studies, selects the target topology, defines security/network/identity/observability controls and only then creates deployable IaC.
