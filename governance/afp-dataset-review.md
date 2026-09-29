# Automated fiber placement dataset review

Reviewed 2026-09-28. User-supplied archive endpoint: https://zenodo.org/api/records/17048470/files-archive. Source record: https://zenodo.org/records/17048470.

Downloaded the record's `Cardoso_etal_2025_AFP_Raw_Dataset.zip` into ignored local artifacts. Its MD5 `06cd012474869b324c83438b71da05b0` matches the publisher's listing. Inspected archive paths and README without extracting or executing code.

The archive contains 18 CSV files: robot paths, laser x coordinates and laser z profiles for each of six passes, arranged into two layers within one part/session. The publisher describes a cross-ply composite laminate and provides a separate processing-code repository.

This is relevant to a separate geometric-inspection and traceability reference scenario. Explicit part/layer/pass organization is useful for testing contextualization. However, six passes within one session do not constitute six independent production trials. The archive inventory does not contain a separate defect-label or ground-truth file; label availability and reference metrology require further investigation before claiming supervised defect-detection accuracy.

It cannot confirm either the SECOM failure model or the milling surface-roughness model: process, inputs and target differ. Do not merge its sensor columns with those datasets or use its single-session measurements as proof of cross-part generalization. No training, acceptance evaluation or Azure deployment was performed during this review. The authorized milling reference work remains a separate workstream.
