# Manufacturing SPC: Cpk that comes from a real Xbar-R chart, not a claim

5 processes, 450 subgroups, and 2,250 individual measurements, where
process capability (Cp/Cpk), control limits, and out-of-control detection
all come from the same Xbar-R control-chart math a real shop-floor SPC
system runs — not a column of random floats with a "Cpk" number written
in a README.

**Free, public domain (CC0), no signup, no attribution required.** Generated
by [Misata](https://www.misata.studio), not sampled from any real
production line.

## Why this exists

A "measurement" column of independently random floats can't sit at a
declared Cp/Cpk, can't split into the right within/between variance an
Xbar-R chart actually estimates from, and can't trigger a Western Electric
Rule violation at a believable rate. This dataset builds all three.

| | typical synthetic QC data | this dataset |
| --- | --- | --- |
| Cpk | asserted in a description | computed from a real Xbar-R baseline (Rbar/d2), matches the declared target within sampling tolerance |
| Cp vs Cpk | not distinguished | one process built off-center on purpose: Cp measurably exceeds Cpk |
| Control limits | not present | UCL/LCL = grand_mean ± A2 x Rbar, the standard constants for n=5 |
| Out-of-control signal | absent, or randomly flagged | an engineered tool-wear drift that actually trips Western Electric rules where it happens, and nowhere else |

## Files

| file | rows | what it is |
| --- | --- | --- |
| `processes.csv` | 5 | one row per process: part, characteristic, spec limits, target Cpk |
| `subgroups.csv` | 450 | one row per subgroup: xbar, range, Western Electric rule flags |
| `measurements.csv` | 2,250 | one row per individual reading (5 per subgroup) |
| `capability_summary.csv` | 5 | one row per process: measured Cp/Cpk, control limits, baseline stats |
| `INTEGRITY.txt` | | every claim below, re-measured against these exact files |

## processes.csv

| column | meaning |
| --- | --- |
| `process_id` | process identity |
| `part_name` | Shaft Diameter, Bore Diameter, Housing Bolt Torque, Valve Seal Thickness, or Bearing Race Width |
| `characteristic` | what's being measured |
| `unit` | mm or Nm |
| `lsl` / `usl` | lower/upper spec limit |
| `target_cpk` | the process capability this process was built to |

## subgroups.csv / measurements.csv / capability_summary.csv

| column | meaning |
| --- | --- |
| `subgroup_id` | subgroup identity (5 measurements each, one per production shift) |
| `xbar` / `r` | subgroup mean and range, recomputable from the 5 raw measurements |
| `rule1_beyond_3sigma`, `rule3_2of3_beyond_2sigma`, `rule4_8_consecutive_same_side` | the three Western Electric Rules checked |
| `out_of_control` | true if any rule fired |
| `sigma_within` | estimated from the baseline's Rbar/d2, the real Xbar-R estimator |
| `cp` / `cpk` | measured process capability from the baseline period |
| `ucl_xbar` / `lcl_xbar` | control limits, grand_mean ± A2 x Rbar |

## The processes, measured

| process | spec | target Cpk | measured Cpk | notes |
| --- | --- | --- | --- | --- |
| Shaft Diameter | 24.95-25.05mm | 1.67 | 1.58 | excellent / six-sigma-level, centered |
| Bore Diameter | 39.96-40.04mm | 1.33 | 1.28 | the AIAG/automotive-industry minimum, centered |
| Housing Bolt Torque | 40-50Nm | 1.33 | 1.41 | off-center: Cp 1.94 vs Cpk 1.41, a real Cp/Cpk gap |
| Valve Seal Thickness | 1.92-2.08mm | 0.85 | 0.83 | a real failing process, below the 1.33 minimum |
| Bearing Race Width | 11.94-12.06mm | 1.33 | 1.30 (baseline) | a tool-wear drift trips rules on 100% of its final subgroups |

## Make your own

```bash
pip install misata
curl -O https://raw.githubusercontent.com/rasinmuhammed/misata/main/examples/manufacturing_spc.py
python -c "from manufacturing_spc import build, verify; t = build(seed=19); verify(t)"
```

Change the seed for a fresh run. Each process's spec limits, target Cpk,
and off-center/drift behavior stay declared in the script; the Xbar-R
control-chart math and Western Electric rule detection recompute from them
regardless.

## Honest limits

This is process-control math for continuous dimensional and torque
measurements — it doesn't model attribute/pass-fail SPC (p-charts,
c-charts). Sigma is estimated from a 54-subgroup baseline, a realistic but
modest sample; the measured Cpk for any single run carries the sampling
noise that sample size implies. Spec limits and target Cpk values are
declared, realistic-shaped assumptions for five illustrative parts, not
measured from a real production line's actual PPAP submission.

- Docs: https://www.misata.studio/docs/domains/manufacturing-spc
- How the guarantees are tested: https://www.misata.studio/gauntlet
- Source: https://github.com/rasinmuhammed/misata
