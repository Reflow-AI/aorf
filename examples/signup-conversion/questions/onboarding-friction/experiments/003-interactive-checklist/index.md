---
type: experiment
title: Interactive activation checklist
description: Test whether an interactive checklist during onboarding raises conversion.
question: ../../index.md
kind: hypothesis_test
hypothesis: "Replacing the static welcome page with an interactive activation checklist raises trial-to-paid conversion by at least 3 percentage points."
research_status: done
verdict: inconclusive
verdict_scope: "two week run, underpowered"
baseline: ../000-baseline/index.md
datasets:
  - path: /datasets/signups-2026q2.md
    role: eval
metrics:
  - name: conversion_rate
    value: 0.30
    baseline_value: 0.28
    direction: higher_is_better
    primary: true
    n: 1120
    ci: [0.274, 0.326]
run_date: 2026-07-22
owner: akbay
timestamp: 2026-07-22
---

# Hypothesis
Users who complete three activation actions convert far better, so guiding them there should raise conversion.

# Method
50/50 split, two weeks only (cut short by the release freeze). Variant shows a 4 item interactive checklist.

# Results
0.30 vs 0.28, +0.02, CI spans the baseline. Underpowered: n=1120 against a needed n of roughly 3800 for a 3pp effect.

# Conclusion
Inconclusive. The direction is encouraging but the run cannot distinguish +0.02 from noise.

# Next
Re-run for four weeks after the freeze. Power calculation in [artifacts/power.md](artifacts/power.md).
