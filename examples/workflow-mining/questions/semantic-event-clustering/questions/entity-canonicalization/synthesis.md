---
type: synthesis
title: Entity canonicalization, experiment comparison
description: Results for experiments under the entity canonicalization sub-question.
question: ./index.md
status: stable
timestamp: 2026-07-25
---

<!-- AORF:BEGIN generated -->
### ari, dataset v2, vs baseline

| Experiment | Verdict | Metric | Value | Baseline | Delta | Ran |
|---|---|---|---|---|---|---|
| [000-baseline](./experiments/000-baseline/index.md) | n/a | ari | 0.71 | — | — | 2026-07-24 |
| [001-ner-entity-stripping](./experiments/001-ner-entity-stripping/index.md) | refuted | ari | 0.72 | 0.71 | +0.01 | 2026-07-24 |
| [002-statistical-container-detection](./experiments/002-statistical-container-detection/index.md) | supported | ari | 0.79 | 0.71 | +0.08 | 2026-07-25 |

**Current best:** [002-statistical-container-detection](./experiments/002-statistical-container-detection/index.md) — ari 0.79, delta +0.08
<!-- AORF:END generated -->

# What the evidence says
NER is the obvious approach and it does not work here, because the tokens that matter are not named entities. Frequency statistics across cases separate entity from container from enum far better.
