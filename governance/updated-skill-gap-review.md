# Updated skill lifecycle review

Scope: existing industrial manufacturing reference environment, with frozen Lenze model. Governing source: `.codex/skills/build-production-ai-systems/SKILL.md` on `origin/main`, reviewed 2026-09-28. No production plant or owner is assigned.

The skill adds explicit baseline/threshold and feature gates. Existing benchmark results are preserved. Evidence added after training is labeled retrospective; missing historical gates cannot be made to have passed by creating documents now.

| Lifecycle phase | Current evidence and remaining gap |
|---|---|
| 1 Business/systems definition | Reference-only scope established; customer authority absent |
| 2 Architecture/technical management | Existing requirements and architecture; Lenze production traceability incomplete |
| 3 Cloud foundation | Existing private East US 2 platform |
| 4 Platform/DevSecOps | Manual job and guarded publishing verified; protected automated promotion remains disabled |
| 5 Security/observability baseline | Private endpoints, identity and operations controls implemented; not full assurance |
| 6 Data engineering | Lenze file checksums and joins verified; extraction provenance incomplete |
| 7 Process/data baseline | Normal training population characterized; raw process/time history unavailable |
| 8 Process/data thresholds | Integrity/finiteness contracts enforced; plant limits, capacity and freshness criteria unapproved |
| 9 Feature engineering | Identity selection of publisher features; upstream formulas/units/windows unverified |
| 10 Feature baseline/validation | Training-only distribution evidence added retrospectively; point-in-time validation unresolved |
| 11 Feature management | File catalog appropriate to reference batch use; online store not required by current scope |
| 12 ML/MLOps | Frozen model meets reference criteria locally/Azure; no calibrated probability claim |
| 13 Decision integration | Existing illustrative human review; Lenze operational workflow not qualified |
| 14 Security assurance | Full access, supply-chain and threat-control evidence still required for production |
| 15 Reliability/operability | Production SLO/load/recovery evidence absent |
| 16 Production release | NO-GO; retain reference-only authority |

## Threshold evidence

Version: `governance/lenze-protocol.json` v1. Recall >= 0.50: observed 0.65 (208/320). False alerts / all test rows <= 0.10: observed 0.077411 (122/1,576). G2 reference benchmark passes. Source/model hashes, test method and Azure execution are in `.azure/lenze-acceptance.json`. Engineering owner: reference engineering role; independent production reviewer unassigned. These reference criteria are not customer-approved operational thresholds. The cutoff and criteria remain unchanged.

## Next gates

Obtain upstream feature definitions and extraction provenance to resolve temporal/physical validity; establish approved process criteria from a representative source; per-record frozen-model consistency is now verified across Windows/Linux/Azure (see `.azure/lenze-decision-consistency.json`); qualify live-input refusal behavior separately; complete release-integrity, recovery and access-control evidence before expanding operational use. No additional cloud service is justified by this review.
