---
type: experiment
title: Remove the credit card requirement
description: Test whether dropping card-up-front raises trial-to-paid conversion.
question: ../../index.md
kind: hypothesis_test
hypothesis: "Removing the credit card requirement at signup raises trial-to-paid conversion by at least 4 percentage points."
research_status: done
verdict: supported
verdict_scope: "April to June 2026 cohorts, self-serve signups only"
baseline: ../000-baseline/index.md
datasets:
  - path: /datasets/signups-2026q2.md
    role: eval
metrics:
  - name: conversion_rate
    value: 0.34
    baseline_value: 0.28
    direction: higher_is_better
    primary: true
    n: 4188
    ci: [0.32, 0.36]
run_date: 2026-07-10
owner: akbay
tracker: GROW-118
timestamp: 2026-07-10
---

# Hypothesis
Card-up-front is the largest single drop-off in the baseline funnel. Removing it should convert more of the top of funnel, even if per-user intent falls.

# Method
50/50 split on new self-serve signups for three weeks. Variant removes the card step entirely and asks for payment at day 14. Identical email sequence in both arms.

# Results
Conversion 0.34 vs 0.28 baseline, +0.06 (95% CI 0.32 to 0.36), n=4188. Per-arm detail in [artifacts/arms.csv](artifacts/arms.csv). Full writeup in [artifacts/report.html](artifacts/report.html).

# Conclusion
Supported. The card requirement was costing roughly 6 percentage points of conversion. Note the scope: self-serve only, we did not test sales-assisted signups.

# Next
Check whether the day-14 payment prompt causes a second drop-off that eats the gain over a longer window.
