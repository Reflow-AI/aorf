---
type: synthesis
title: Onboarding friction, experiment comparison
description: Side-by-side results for every experiment under this question.
question: ./index.md
status: stable
timestamp: 2026-07-26
---

<!-- AORF:BEGIN generated -->
### conversion_rate, dataset v1, vs baseline

| Experiment | Verdict | Metric | Value | Baseline | Delta | Ran |
|---|---|---|---|---|---|---|
| [000-baseline](./experiments/000-baseline/index.md) | n/a | conversion_rate | 0.28 | — | — | 2026-07-03 |
| [001-remove-cc-requirement](./experiments/001-remove-cc-requirement/index.md) | supported | conversion_rate | 0.34 | 0.28 | +0.06 | 2026-07-10 |
| [002-shorter-signup-form](./experiments/002-shorter-signup-form/index.md) | refuted | conversion_rate | 0.285 | 0.28 | +0.005 | 2026-07-15 |
| [003-interactive-checklist](./experiments/003-interactive-checklist/index.md) | inconclusive | conversion_rate | 0.3 | 0.28 | +0.02 | 2026-07-22 |

**Current best:** [001-remove-cc-requirement](./experiments/001-remove-cc-requirement/index.md) — conversion_rate 0.34, delta +0.06
<!-- AORF:END generated -->

# What the evidence says
The card requirement dominates. Form length is not the lever. The checklist may help but n is too small to call.
