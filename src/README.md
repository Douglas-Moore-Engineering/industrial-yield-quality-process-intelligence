# Source implementation

`pip install -r requirements-dev.txt` before running tests.

Start with the [ordered code walkthrough](../docs/code-walkthrough.md). The current recorded passing model benchmark follows `lenze.run` → calibration split → Isolation Forest fit → freeze → `metrics`, with frozen replay through `lenze_verification.verify`. `lenze_baseline.build` supplies retrospective training-feature profiles. The earlier reference AI/SECOM path below is separate.

| Module | Purpose |
|---|---|
| [iyqpis/contracts.py](iyqpis/contracts.py) | Data-quality validation library: validates records against the JSON Schema contracts in [data/contracts](../data/contracts) |
| [iyqpis/timestamps.py](iyqpis/timestamps.py) | Timestamp integrity checks (missing, unparseable, duplicate, out-of-order) per genealogy group |
| [iyqpis/adapters/manufacturing_spc.py](iyqpis/adapters/manufacturing_spc.py) | Raw CSV -> validated `telemetry`/`quality_result` adapter for the [manufacturing-spc sample dataset](../data/samples/raw/manufacturing-spc) |

All five dataset adapters are implemented and tested; see [data/samples/README.md](../data/samples/README.md) for their contract mapping.

The replayable batch runner is `iyqpis.pipeline`; the managed-identity Azure entrypoint is `iyqpis.azure_batch`. See [data engineering runbook](../runbooks/data-engineering.md) for local operation, Azure release prerequisites, costs and acceptance status.

Reference AI modules: `iyqpis.intelligence` (verified feature join, chronological benchmark, shadow inference), `iyqpis.operations` (local evidence/review ledger, registry rollback, monitoring and explicit-edge retrieval), `iyqpis.reference` (sample/synthetic acceptance sequence), and `iyqpis.azure_intelligence` (private on-demand Azure execution and checked publication). See the [reference AI runbook](../runbooks/reference-ai.md). These modules do not authorize production recommendations or plant-control writes.

