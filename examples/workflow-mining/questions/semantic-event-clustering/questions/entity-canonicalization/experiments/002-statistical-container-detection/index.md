---
type: experiment
title: Statistical token classification into entity, container and enum
description: Classify varying tokens by their distribution across cases, then mask only true entities.
question: ../../index.md
kind: hypothesis_test
hypothesis: "Classifying tokens by cross-case frequency into entity, container and enum, and masking only entities, raises ARI by at least 0.05 over the no-masking baseline."
research_status: done
verdict: supported
verdict_scope: "events v2, 42 users, June 2026"
baseline: ../000-baseline/index.md
also_informs:
  - /questions/sop-drift-detection/index.md
datasets:
  - path: /datasets/events-v2.md
    role: eval
metrics:
  - name: ari
    value: 0.79
    baseline_value: 0.71
    direction: higher_is_better
    primary: true
    n: 50
    ci: [0.75, 0.83]
  - name: cluster_leakage
    value: 0.06
    baseline_value: 0.14
    direction: lower_is_better
    primary: false
run_date: 2026-07-25
owner: onur
code:
  commit: c3d4e5f
  entrypoint: src/run.py
  shared_ref: d4e5f6a
env:
  lockfile: ./artifacts/env.lock
runtime_s: 940
timestamp: 2026-07-25
---

# Hypothesis
A token that varies from case to case is an entity and should be masked. A token that appears in nearly every case is a container and carries signal. A token drawn from a small closed set is an enum and should be normalised, not masked.

# Method
For each candidate token, compute its document frequency across cases and its cardinality. Classify: high variance and high cardinality is an entity, high frequency and low cardinality is a container, low cardinality with a bounded vocabulary is an enum. Mask entities, keep containers, normalise enums to a canonical form. Then the baseline pipeline.

# Results
ARI 0.79 vs 0.71 baseline, +0.08 (CI 0.75 to 0.83). Cluster leakage down from 0.14 to 0.06. Token classification examples in [artifacts/token-classes.csv](artifacts/token-classes.csv).

# Conclusion
Supported, and it explains why 001 failed: the split that matters is statistical, not linguistic. This also gives the drift-detection question a usable case id, which is why it is marked as also informing that question.

# Next
Check whether the enum normalisation generalises to users outside the June cohort.
