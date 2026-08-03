---
type: synthesis
title: Proper-noun handling, experiment comparison
description: Results for experiments under the proper-noun handling sub-question.
question: ./index.md
status: stable
timestamp: 2026-07-25
---

<!-- AORF:BEGIN generated -->
### ari, dataset v2, vs baseline

| Experiment | Verdict | Metric | Value | Baseline | Delta | Ran |
|---|---|---|---|---|---|---|
| [000-baseline](./experiments/000-baseline/index.md) | n/a | ari | 0.71 | — | — | 2026-07-24 |
| [001-ner-masking](./experiments/001-ner-masking/index.md) | refuted | ari | 0.72 | 0.71 | +0.01 | 2026-07-24 |
| [002-statistical-token-classification](./experiments/002-statistical-token-classification/index.md) | supported | ari | 0.79 | 0.71 | +0.08 | 2026-07-25 |

**Current best:** [002-statistical-token-classification](./experiments/002-statistical-token-classification/index.md) — ari 0.79, delta +0.08
<!-- AORF:END generated -->

# What the evidence says

NER masking is the obvious approach and it does not work, because grammatical type does not predict
whether a name carries the subject. Distribution across articles does: masking only the tokens that
appear evenly across unrelated articles gains +0.08 ARI and more than halves cluster leakage.
