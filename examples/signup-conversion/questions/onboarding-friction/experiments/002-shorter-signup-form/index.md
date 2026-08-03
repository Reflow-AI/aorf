---
type: experiment
title: Shorten the signup form
description: Test whether cutting the signup form from 7 fields to 3 raises conversion.
question: ../../index.md
kind: hypothesis_test
hypothesis: "Cutting the signup form from 7 fields to 3 raises trial-to-paid conversion by at least 2 percentage points."
research_status: done
verdict: refuted
verdict_scope: "April to June 2026 cohorts; form fields only, card step unchanged"
baseline: ../000-baseline/index.md
datasets:
  - path: /datasets/signups-2026q2.md
    role: eval
metrics:
  - name: conversion_rate
    value: 0.285
    baseline_value: 0.28
    direction: higher_is_better
    primary: true
    n: 3902
    ci: [0.271, 0.299]
run_date: 2026-07-15
owner: jordan
timestamp: 2026-07-15
---

# Hypothesis
Form length is friction, so fewer fields should convert more signups.

# Method
50/50 split, three weeks. Variant asks name, email, password only. Removed fields are collected later in-product.

# Results
0.285 vs 0.28, +0.005, well inside the confidence interval. No detectable effect.

# Conclusion
Refuted at the stated threshold. Form length is not a meaningful lever on our funnel. Prior art predicted a small effect and that is what we found.

# Next
Do not re-test form length variants. The remaining candidate is the activation checklist.
