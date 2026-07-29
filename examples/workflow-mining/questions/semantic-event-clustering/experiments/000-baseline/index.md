---
type: experiment
title: Baseline, time-gap segmentation with one embedding model
description: Cheapest possible approach, so later work has something to beat.
question: ../../index.md
kind: baseline
research_status: done
verdict: n/a
baseline: none
baseline_reason: this document is the baseline
datasets:
  - path: /datasets/events-v2.md
    role: eval
metrics:
  - name: ari
    value: 0.58
    direction: higher_is_better
    primary: true
    n: 50
run_date: 2026-07-22
owner: onur
code:
  commit: d4e5f6a
  entrypoint: src/run.py
  shared_ref: d4e5f6a
env:
  lockfile: ./artifacts/env.lock
models:
  - provider: local
    id: all-MiniLM-L6-v2
    snapshot: all-MiniLM-L6-v2
    params: {batch_size: 32}
runtime_s: 210
timestamp: 2026-07-22
---

# Method
Deliberately brute force and small. Split events on a 90 second idle gap, embed each event's window title with one small local model, cluster with k-means at k=50. Evaluate against the 50-task hand-labelled set only. No entity handling, no tuning.

# Results
ARI 0.58. Per-cluster detail in [artifacts/clusters.csv](artifacts/clusters.csv).

# Conclusion
Gives every later experiment a number to beat, and it was cheap to produce. Time-gap splitting merges interleaved tasks, which is visible in the confusion detail.
