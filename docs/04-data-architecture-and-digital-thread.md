# Data Architecture and Digital Thread

## Table of contents

- [Data architecture principles](#data-architecture-principles)
- [Canonical domains](#canonical-domains)
- [Data zones](#data-zones)
- [Digital thread](#digital-thread)
- [Industrial knowledge graph](#industrial-knowledge-graph)
- [Data-quality controls](#data-quality-controls)

## Data architecture principles

- preserve immutable source evidence
- validate before feature/model consumption
- separate source observations from model inference
- preserve event time and ingestion time
- support deterministic replay
- make lineage queryable
- keep contracts independent of a single equipment vendor or cloud platform

## Canonical domains

Material, production, asset/equipment, sensor/telemetry, process, product, quality, maintenance, operator action, model/prediction, alert, recommendation, decision/outcome and event.

## Data zones

`Raw / immutable → validated → contextualized → feature/model-ready → curated/evidence`

Raw observations are never overwritten by derived predictions.

## Digital thread

The digital thread connects:

`Material lot → production campaign/run → process window → equipment state → intermediate product → quality result → downstream transformation → finished product`

This enables containment, investigation and historical replay.

## Industrial knowledge graph

Relationship-heavy evidence is represented through entities such as:
- plant
- line
- machine
- component
- sensor
- material lot
- run
- recipe
- product
- quality test
- defect
- maintenance event
- process event
- prediction
- recommendation
- decision

Example relationships:

`MATERIAL → PROCESSED_BY → MACHINE`

`PRODUCT → PRODUCED_DURING → RUN`

`DEFECT → OBSERVED_IN → PRODUCT`

`PROCESS_EVENT → PRECEDED → QUALITY_EVENT`

## Data-quality controls

The system must detect stale, missing, duplicated, misordered and invalid telemetry, schema drift, unit mismatches, timestamp integrity issues and broken genealogy links before decision support is produced.
