# Lifecycle tailoring record

Version 1; 2026-09-30; private engineering. Owner: proposed DME systems engineering role. Approver: unassigned. Status: retrospective proposal; no tailoring approval asserted.

Use an iterative reference-development lifecycle followed by separately approved site adaptation, offline site V&V, shadow, advisory canary, ORR, CAR and production activation. Preserve the 21-phase skill sequence and the project's existing release IDs. Customer agreement processes are pending engagement, not permanently waived.

The reference workload uses publisher precomputed features and manual batch execution. File-based feature management is proportionate; an online store is not required by this execution pattern. Rationale, downstream effects and review triggers are recorded in [features/README.md](../../features/README.md). Approval of this applicability decision remains pending.

Production stages are blocked, not marked N/A. Bounded autonomy requires a separate assurance case and authority; the current system has no approved OT write path. Live streaming, online serving and customer support scope are decided only from actual requirements. No technology or phase is silently omitted.

Entry to reference replay requires frozen inputs/model/protocol integrity and the approved bounded execution context. Exit is limited to evidence-backed replay; unresolved monitoring/recovery controls remain open. Site entry requires an approved sponsor, source rights, source mapping, temporal feature validity, thresholds and operating ownership. Shadow/canary/ORR/CAR exits require their own representative evidence and approval.

Re-enter relevant phases when schema, feature extraction, source/site, model, cutoff/criterion, dependency, IaC, identity/network, support scope or risk changes. Identify invalidated evidence before promotion. Map applicable 15288/12207 outcomes during the open standards review; these phase names alone do not establish alignment.
