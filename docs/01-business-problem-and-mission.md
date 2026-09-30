# Business Problem and System Mission

## Table of contents

- [Problem statement](#problem-statement)
- [Mission](#mission)
- [Business objectives](#business-objectives)
- [Initial validation domain](#initial-validation-domain)
- [Success measures](#success-measures)

## Problem statement

Industrial yield and quality losses often emerge from interactions across material properties, process settings, equipment condition, environmental state, production context, maintenance state and operator interventions. These interactions can remain below individual alarm thresholds while the combined manufacturing state is already moving toward scrap, rework or off-spec output.

Traditional workflows frequently detect the problem too late:

`Produce → inspect → fail → scrap/rework → investigate`

The target operating model is:

`Observe → contextualize → predict → explain → recommend → authorize → verify → learn`

## Mission

IYQPIS will detect emerging process instability, predict yield and quality risk before material becomes unrecoverable, trace potentially affected material through the production lifecycle, identify plausible contributing conditions, evaluate bounded corrective actions, and present evidence-backed recommendations to authorized operators and engineers.

## Business objectives

| Objective | Intended outcome |
|---|---|
| Increase first-pass yield | More conforming output from the same material input |
| Reduce scrap and rework | Lower material loss and cost of poor quality |
| Reduce detection latency | Identify instability earlier |
| Reduce diagnosis latency | Shorten time from event to plausible cause |
| Improve traceability | Rapidly identify exposed material/product |
| Preserve throughput | Avoid quality gains that simply reduce productive capacity |
| Preserve safety | Keep existing safety/interlock systems authoritative |
| Improve process learning | Retain evidence and outcomes for future investigations |
| Improve modernization ramp-up | Detect domain shift and unfamiliar process behavior |

## Initial validation domain

The core architecture is intended to be industry-agnostic. Copper rod/wire is the illustrative domain scenario in the historical design baseline because it exposes continuous-process, quality, genealogy and physical-process concerns. It is not an onboarded or validated customer site. The current passing implementation benchmark is the separate Lenze geared-motor reference using publisher precomputed features; see [Azure results](azure-validation-results.md). Cross-industry applicability remains subject to domain and site validation.

## Success measures

No fabricated improvement targets are assumed. Pilot targets are set only after an authorized baseline establishes first-pass yield, scrap rate, cost of poor quality, alert burden, detection latency and diagnosis latency.
