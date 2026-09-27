# Integration and Interface Architecture

## Interface classes

| Interface | Direction | Pattern | Requirement |
|---|---|---|---|
| OT telemetry | Plant → intelligence | broker/replication/collector | read-oriented; buffer/replay; no direct control write |
| Historian | Plant → intelligence | incremental pull/replication | preserve source timestamps and tag metadata |
| MES/production | authorized metadata exchange | API/event/file | run/order/recipe IDs become canonical context |
| Quality/LIMS | Quality → intelligence | API/event/batch | retain method, limits and disposition |
| CMMS/EAM | Maintenance → intelligence | API/batch | link work orders/components to canonical asset IDs |
| Identity | Enterprise → platform | federated authentication | human/service identity; least privilege |
| Decision UI/API | Platform → users | API/web app | role-based evidence and confidence |
| Existing control workflow | Human → plant controls | existing authorized process | AI cannot bypass established authority |

## Interface design principles

- contracts are versioned
- source time is preserved
- idempotency/replay is supported where required
- failures are observable
- plant-to-enterprise paths are explicitly authorized
- no undocumented reverse control path is introduced
