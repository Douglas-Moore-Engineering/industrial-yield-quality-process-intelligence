# Capacity and Performance Planning

## Table of contents
- [Sizing principle](#sizing-principle)
- [Sizing dimensions](#sizing-dimensions)
- [Azure sizing gate](#azure-sizing-gate)

## Sizing principle

Capacity is parameterized because actual plant tag counts, sampling rates, retention needs and concurrent investigation loads are not yet known. Azure sizing must follow measured pilot evidence rather than arbitrary SKU selection.

## Sizing dimensions

| Dimension | Sizing formula / evidence |
|---|---|
| Events/sec | Σ(tags per asset × assets × sample frequency) + event sources |
| Daily records | events/sec × 86,400, adjusted for aggregation/compression |
| Raw storage/day | records × encoded bytes/record + metadata + replication |
| Retention | raw + curated + evidence/audit retention |
| Model scoring load | active production windows × score frequency × models/window |
| Training load | history depth × feature width × retraining cadence × candidate experiments |
| Graph size | entities + relationship edges across material/product/asset/event lineage |
| Recovery buffer | maximum disconnected duration × ingress volume × safety factor |
| Network bandwidth | peak encoded event rate × protocol overhead × burst factor |
| Concurrency | operators + engineers + APIs + scheduled investigations |

## Azure sizing gate

Do not select Azure SKUs or tiers until event rate, payload size, retention, RPO/RTO, latency and concurrency are measured from the pilot environment.
