---
type: synthesis
title: Article topic clustering, experiment comparison
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
| [001-document-vs-sentence-embeddings](./experiments/001-document-vs-sentence-embeddings/index.md) | supported | ari | 0.71 | 0.58 | +0.13 | 2026-07-24 |

### ~~ari, dataset v1, vs baseline~~ (invalidated)

| Experiment | Verdict | Metric | Value | Baseline | Delta | Ran |
|---|---|---|---|---|---|---|
| [~~002-proper-noun-stripping~~](./experiments/002-proper-noun-stripping/index.md) | refuted | ari | 0.63 | 0.54 | +0.09 | 2026-07-18 |

**Current best:** [001-document-vs-sentence-embeddings](./experiments/001-document-vs-sentence-embeddings/index.md) — ari 0.71, delta +0.13
<!-- AORF:END generated -->

# What the evidence says

Document-level embedding is the main lever so far, worth +0.13 ARI over TF-IDF, though the gain
depends on the clustering threshold. The proper-noun result on tokens v1 cannot be trusted because
the dataset was withdrawn; the sub-question re-tested the idea properly on v2 and found a method
that works for a different reason than the original one assumed.
