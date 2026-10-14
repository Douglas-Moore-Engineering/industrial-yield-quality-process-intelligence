# Contribution Standard

Changes must preserve requirements traceability, architecture-decision records, security boundaries, verification evidence, and rollback capability.

1. Create a short-lived feature branch.
2. Link the change to a requirement, ADR, defect, or approved architecture task.
3. Update affected diagrams and traceability records.
4. Add or update tests and verification evidence.
5. Require review before merge to the protected default branch.

Direct commits to the protected default branch should be disabled once repository protection is configured.

## Measurement and repository evidence

Maintain the seven-section README order and link quantitative results to the [measurement index](governance/measurements/README.md). Preserve exact units, denominators, original evidence versions and actual decision authority. New evaluations receive new record IDs; retrospective documentation is not a newly executed test. Keep customer outcomes **not measured** until observed and attributed.

Project-specific requirements, evidence, measurements and decision records remain in Git. Run `python scripts/check_repository_contract.py` before committing. Its structural checks cannot authenticate evidence or approve a release.



## Review package changes

Preserve Demo → Code walkthrough → Results navigation and the seven README sections. Run `python scripts/execute_notebooks.py` after notebook changes; commit safe executed outputs. Source and evidence hashes distinguish local demonstration from historical model/cloud runs. Update `docs/results.md` with the actual scope and outcome. Keep raw-data exploration, new model selection and full inference replay separate from ordinary documentation CI.
