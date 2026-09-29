# Supplied dataset compatibility review

## Publisher documentation review

The user subsequently authorized this source for a separate milling reference model and supplied [the dataset description](https://zenodo.org/records/5602977/files/Datasets_description_macromilling_v2.pdf?download=1). Text extraction from its five pages confirms (pages 2-3):

- The process mills AL7075-T6 aluminium workpieces on a Deckel Maho DMC 75 V Linear machining centre.
- Inputs are acceleration RMS (`AcelR`, m/s2), feed per tooth (`fz`, mm/tooth), tool diameter (`Diam`, mm), cutting depth (`ae`, mm), material hardness (`HB`, Brinell), and geometry (`geom`, documented in mm).
- The target is measured surface roughness `Ra` in micrometres, measured after machining with a Surfcom 130 instrument. Treat it as a regression target. The prose defines arithmetic average roughness while the table calls it RMS; preserve this documentation discrepancy rather than silently changing the target definition.
- The documented seven-column schema contains no part identifier, experiment/run identifier or timestamp. It does not establish that rows are independent parts. Random row splitting alone cannot establish performance on unseen machining runs.
- The description does not explain the CSV's multiple-period numeric encoding. Resolve that before training; do not assume ordinary decimal parsing or silently remove punctuation.

This is a relevant reference dataset, but final suitability remains conditional on numeric decoding and defensible evaluation grouping. The document's illustrative roughness categories are not a customer-approved rejection threshold. Regression acceptance must be specified before examining holdout performance; existing SECOM recall and false-alert criteria do not automatically apply.

Reviewed 2026-09-28. Source: [Zenodo record 5602977](https://zenodo.org/records/5602977), `Macromilling_dataset_1.csv`.

**Decision: incompatible with independent confirmation of frozen SECOM candidate `66587bfb754049a71963a17a84300510`.**

The publisher describes macro-mechanical milling quality estimation: predicting surface roughness from vibration and cutting parameters. The CSV preamble declares six inputs (`AcelR fz Diam ae HB geom`), one output (`Ra`), and 12,363 observations. That count is a declaration in the file, not a verified full-file row count. Only the preamble and two initial records were read; no training or confirmation evaluation was performed.

The frozen candidate requires the same 590 SECOM sensor definitions, binary failure outcomes, and event timestamps from the same process. This file describes a different process, six different inputs and a continuous roughness target. Renaming its columns, padding missing sensors, or inventing a roughness cutoff cannot establish compatibility.

The candidate, decision cutoff and acceptance criteria remain frozen. No confirmation reservation was consumed and no Azure deployment was changed.

This source can be assessed for a separate machining regression benchmark. Before modeling, verify the publisher's variable definitions, numeric encoding (some cells contain multiple periods), units, experiment grouping and feature availability. Define a machining quality criterion and reserve independent experiment groups before candidate selection. Such a benchmark would provide separate evidence; it would not confirm the SECOM model or establish readiness for a customer facility.
