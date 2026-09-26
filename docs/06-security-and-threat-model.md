# Security Architecture and Threat Model

## Table of contents

- [Security objective](#security-objective)
- [Trust zones](#trust-zones)
- [Primary threats](#primary-threats)
- [Required controls](#required-controls)
- [Safety boundary](#safety-boundary)

## Security objective

Protect operational continuity, manufacturing data integrity, model integrity, decision evidence and identity while ensuring analytics connectivity does not create an uncontrolled route into plant control.

## Trust zones

1. Level 0/1 — sensors and actuators
2. Level 2 — PLC/DCS/local control
3. Level 3 — SCADA/historian/MES/plant operations
4. Industrial DMZ — controlled broker/gateway/buffer
5. Enterprise data and AI platform

## Primary threats

- credential misuse
- unauthorized control-path creation
- telemetry or label tampering
- model/artifact substitution
- poisoned training data
- stale or replayed messages
- dependency/supply-chain compromise
- privilege escalation
- data exfiltration
- model or service outage causing unsafe reliance
- compromised decision evidence

## Required controls

- network segmentation
- least privilege
- managed identities/service identities
- explicit ingress/egress policy
- immutable raw evidence
- signed or digest-pinned model artifacts
- provenance and lineage
- separation of duties
- audit logging
- model rollback
- abstention/degraded mode
- human authorization
- incident runbooks

## Safety boundary

AI does not bypass safety controls, interlocks or established operational procedures. The analytics platform is not a safety instrumented system and is not authoritative for plant safety.
