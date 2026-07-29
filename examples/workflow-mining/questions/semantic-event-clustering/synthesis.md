---
type: synthesis
title: Semantic event clustering, experiment comparison
description: Results across all experiments under this question, grouped by dataset version.
question: ./index.md
status: stable
timestamp: 2026-07-26
---

<!-- AORF:BEGIN generated -->
### ari, dataset v2, vs baseline

| Experiment | Verdict | Metric | Value | Baseline | Delta | Ran |
|---|---|---|---|---|---|---|
| [000-baseline](./experiments/000-baseline/index.md) | n/a | ari | 0.58 | — | — | 2026-07-22 |
| [001-group-vs-event-embeddings](./experiments/001-group-vs-event-embeddings/index.md) | supported | ari | 0.71 | 0.58 | +0.13 | 2026-07-24 |

### ~~ari, dataset v1, vs baseline~~ (invalidated)

| Experiment | Verdict | Metric | Value | Baseline | Delta | Ran |
|---|---|---|---|---|---|---|
| [~~002-entity-stripping~~](./experiments/002-entity-stripping/index.md) | refuted | ari | 0.63 | 0.54 | +0.09 | 2026-07-18 |

**Current best:** [001-group-vs-event-embeddings](./experiments/001-group-vs-event-embeddings/index.md) — ari 0.71, delta +0.13
<!-- AORF:END generated -->

# What the evidence says
Grouping before embedding is the main lever so far. The entity-stripping result cannot be trusted because it ran on withdrawn data; the sub-question re-tested it properly.
