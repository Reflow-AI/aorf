---
type: experiment
title: Baseline, parent best pipeline with no entity handling
description: Inherit the parent question's best configuration as this sub-question's baseline.
question: ../../index.md
kind: baseline
research_status: done
verdict: n/a
baseline: none
baseline_reason: "this document is the baseline; it re-runs the parent's best configuration r031 unchanged"
datasets:
  - path: /datasets/events-v2.md
    role: eval
metrics:
  - name: ari
    value: 0.71
    direction: higher_is_better
    primary: true
    n: 50
  - name: cluster_leakage
    value: 0.14
    direction: lower_is_better
    primary: false
    n: 50
run_date: 2026-07-24
owner: onur
code:
  commit: 9f2c1ab
  entrypoint: ../../../001-group-vs-event-embeddings/src/sweep.py
  shared_ref: d4e5f6a
timestamp: 2026-07-24
---

# Method
Re-run the parent question's winning configuration (r031: bge-large, threshold 0.85, normalised) with no entity handling at all, on events v2.

# Results
ARI 0.71, reproducing the parent result within noise.

# Conclusion
Anchors this sub-question to the same scale as its parent, so improvements here are directly comparable upward.
