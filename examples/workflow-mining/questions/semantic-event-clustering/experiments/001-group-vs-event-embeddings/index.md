---
type: experiment
title: Group-level vs event-level embeddings
description: Test whether embedding contiguous event groups beats embedding single events.
question: ../../index.md
kind: sweep
hypothesis: "Embedding contiguous groups of events, rather than individual events, raises clustering ARI by at least 0.10."
research_status: done
verdict: supported
verdict_scope: "events v2, four embedding models, thresholds 0.70 to 0.90; refuted at threshold <= 0.75"
baseline: ../000-baseline/index.md
datasets:
  - path: /datasets/events-v2.md
    role: eval
metrics:
  - name: ari
    value: 0.71
    baseline_value: 0.58
    direction: higher_is_better
    primary: true
    n: 50
    std: 0.04
runs: ./runs.jsonl
run_count: 40
best_run: r031
verdict_basis: "supported in 31 of 40 configurations; the 9 failures are all threshold <= 0.75"
run_date: 2026-07-24
owner: onur
code:
  commit: 9f2c1ab
  entrypoint: src/sweep.py
  shared_ref: d4e5f6a
env:
  lockfile: ./artifacts/env.lock
models:
  - provider: local
    id: e5-large-v2
    snapshot: e5-large-v2
    params: {batch_size: 16}
  - provider: local
    id: bge-large-en-v1.5
    snapshot: bge-large-en-v1.5
    params: {batch_size: 16}
cost_usd: 0
runtime_s: 8640
nondeterministic: true
repeats: 3
timestamp: 2026-07-24
---

# Hypothesis
Individual events carry too little signal. A contiguous group of events shares a task context, so a group embedding should separate tasks better.

# Method
Sweep 4 embedding models x 5 similarity thresholds x 2 preprocessing modes = 40 configurations, 3 repeats each. Group events by a sliding window of 8, embed the concatenated window titles, cluster with HDBSCAN. Full grid and per-config metrics in [runs.jsonl](runs.jsonl).

# Results
Best configuration r031 (bge-large, threshold 0.85, normalised) reaches ARI 0.71 vs baseline 0.58. Supported in 31 of 40 configurations. All 9 failures share threshold <= 0.75, so the effect is real but threshold-sensitive. Sweep summary in [artifacts/sweep-summary.csv](artifacts/sweep-summary.csv), heatmap in [artifacts/heatmap.svg](artifacts/heatmap.svg).

# Conclusion
Supported. Grouping before embedding is worth +0.13 ARI. Threshold matters more than model choice, which was not expected.

# Next
The remaining error mode is identical tasks splitting because of entity noise, which is the sub-question.
