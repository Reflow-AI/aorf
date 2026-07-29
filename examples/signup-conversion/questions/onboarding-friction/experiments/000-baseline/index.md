---
type: experiment
title: Baseline, current funnel as shipped
description: Measure the existing funnel with no changes, on the smallest usable cohort.
question: ../../index.md
kind: baseline
research_status: done
verdict: n/a
baseline: none
baseline_reason: this document is the baseline
datasets:
  - path: /datasets/signups-2026q2.md
    role: eval
metrics:
  - name: conversion_rate
    value: 0.28
    direction: higher_is_better
    primary: true
    n: 4210
run_date: 2026-07-03
owner: akbay
timestamp: 2026-07-03
---

# Method
April 2026 cohort only, the smallest cohort with a complete 30 day trial window. Count signups reaching a paid plan within 30 days. One SQL query, `src/baseline.sql`. Deliberately the most brute-force version: no segmentation, no weighting.

# Results
Conversion 0.28 on n=4210. Step-level drop-off in [artifacts/funnel.csv](artifacts/funnel.csv), chart in [artifacts/funnel.svg](artifacts/funnel.svg).

# Conclusion
Establishes the number every later experiment is measured against. Largest single loss is the card entry step, 41% of all drop-off.
