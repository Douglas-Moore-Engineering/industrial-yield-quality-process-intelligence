# Security Policy

This repository describes a cyber-physical industrial AI system. Treat architecture, threat-model, operational, and future deployment material as sensitive engineering information.

## Rules
- Never commit credentials, tokens, certificates, production connection strings, customer data, or proprietary plant telemetry.
- Keep OT integrations read-oriented during the advisory phase unless separately approved through formal change control.
- Do not create uncontrolled write paths from analytics/cloud services into PLC, SCADA, SIS, or other operational-control systems.
- Production recommendations require policy validation and authorized human approval until explicitly superseded by an approved safety case.
- Report suspected credential exposure or unauthorized repository access immediately and rotate affected secrets outside Git history.
