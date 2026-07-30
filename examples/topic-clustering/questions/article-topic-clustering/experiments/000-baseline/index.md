---
type: experiment
title: Baseline, TF-IDF with k-means
description: The cheapest approach that produces clusters at all, so later work has a number to beat.
question: ../../index.md
kind: baseline
research_status: done
verdict: n/a
baseline: none
baseline_reason: this document is the baseline
datasets:
  - path: /datasets/tokens-v2.md
    role: eval
metrics:
  - name: ari
    value: 0.58
    direction: higher_is_better
    primary: true
    n: 50
run_date: 2026-07-22
owner: alex
code:
  commit: d4e5f6a
  entrypoint: src/run.py
  shared_ref: d4e5f6a
env:
  lockfile: ./artifacts/env.lock
runtime_s: 210
timestamp: 2026-07-22
---

# Method

Deliberately brute force and small. TF-IDF over unigrams with English stopwords removed, then
k-means at k=50, chosen to match the number of topics in the evaluation set. Evaluated against the
50-article hand-labelled set only. No embeddings, no tuning, no proper-noun handling.

# Results

ARI 0.58. Per-cluster detail in [artifacts/clusters.csv](artifacts/clusters.csv).

# Conclusion

Good enough to be a reference and cheap enough to have been worth producing in an afternoon.
The visible failure mode is that clusters split on shared vocabulary rather than subject: two
articles about unrelated events at the same company land together.
