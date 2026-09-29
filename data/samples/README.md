# Sample data

Only synthetic, public, or otherwise appropriately licensed sample data should be committed here. Do not commit customer or proprietary plant telemetry.

## Raw source datasets

`raw/` holds unmodified third-party datasets in the immutable raw zone (see [data architecture](../../docs/04-data-architecture-and-digital-thread.md#data-zones)). None have been edited; only directory placement and, for one PDF, a filename space-to-underscore rename. Contracts adapters under `src/` read these and emit validated records — raw files are never overwritten by derived output.

| Dataset | Source | License | Rows x cols | Mapped contract(s) | Notes |
|---|---|---|---|---|---|
| [bosch-injector-eol](raw/bosch-injector-eol/) | Robert Bosch GmbH / SoliDAIR project (v2c2.at Open Dataset Description Form) | CC BY-NC-ND 4.0 | 1,000 x 71 (67 anonymized inputs + 4 EoL outputs) | `telemetry` (inputs), `quality_result` (EoL outputs) | Real (anonymized) automotive fuel-injector line data. Feature names are obfuscated by the provider; no event timestamps or asset IDs are present, so those fields must be synthesized/declared, not inferred, when adapted. Non-commercial, no-derivatives: keep the CSV/PDF byte-identical to the original. |
| [ai4i-2020-predictive-maintenance](raw/ai4i-2020-predictive-maintenance/) | UCI Machine Learning Repository (AI4I 2020) | UCI ML Repository terms (free for research/academic use) | 10,000 x 14 | `telemetry` (temps/speed/torque/tool wear), `maintenance_event` (failure + 5 failure-mode flags) | `Product ID` serves as `asset_id`; no wall-clock timestamps, only `UDI` sequence. |
| [manufacturing-spc](raw/manufacturing-spc/) | Misata (github.com/rasinmuhammed/misata) | CC0 (public domain) | 2,250 measurements / 450 subgroups / 5 processes | `telemetry` (measurements), `quality_result` (subgroups, Xbar-R/Western Electric disposition) | Synthetic but dimensionally realistic Xbar-R control-chart data with genuine timestamps and full genealogy (measurement → subgroup → process). Best current fit for the P0 "reference dataset preserving temporal and genealogy behavior" backlog item. |
| [secom](raw/secom/) | UCI Machine Learning Repository (SECOM) | UCI ML Repository terms (free for research/academic use) | 1,567 x 590 sensor features + pass/fail label | `telemetry` (590 anonymized sensors), `quality_result` (pass/fail disposition) | `secom_labels.data` carries a real per-row timestamp; contains missing values (`NaN`) that must be preserved as `UNCERTAIN`/`BAD` quality, not silently dropped. |
| [steel-plates-faults](raw/steel-plates-faults/) | UCI Machine Learning Repository (Steel Plates Faults) | UCI ML Repository terms (free for research/academic use) | 1,941 x 27 geometry/luminosity features + 7 one-hot fault types | `quality_result` (defect/fault classification) | No timestamps or asset IDs; one-hot fault columns (`Pastry`, `Z_Scratch`, `K_Scatch`, `Stains`, `Dirtiness`, `Bumps`, `Other_Faults`) map to `measurement_name`/`disposition` per plate. |

Production adoption of any of these still requires the same data-owner review, identifier mapping and retention/classification approval as real plant data — see [contract rules](../contracts/README.md#contract-rules).

## Landed in the Azure data lake (2026-09-28)

All five raw datasets and their adapter output are landed in the dev platform's private ADLS Gen2 account (see [infra/azure/README.md](../../infra/azure/README.md)):

| Container | Contents |
|---|---|
| `raw` | Byte-identical copies of the files under `raw/` above, one folder per dataset |
| `validated` | Contract-validated JSONL from [src/iyqpis/build_validated.py](../../src/iyqpis/build_validated.py) — one file per (dataset, contract), ~1.1M records total, each passing `validate_batch_strict` before upload |

The generated JSONL is **not committed to git** (largest file alone is ~380 MB) — it's fully reproducible from the raw CSVs via `python -m iyqpis.build_validated data/samples/raw <output-dir>`, and lives only in the data lake. Landing required briefly setting the storage account's `publicNetworkAccess` to `Enabled` (single-IP allowlisted) plus a temporary Storage Blob Data Contributor grant on the operator's own account; both were removed and verified reverted (`Disabled`, no IP rules, no leftover role assignment) immediately after upload.
