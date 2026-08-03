---
type: experiment
title: Document-level vs sentence-level embeddings
description: Test whether embedding whole articles beats embedding individual sentences and pooling.
question: ../../index.md
kind: sweep
hypothesis: "Embedding a whole article, rather than embedding its sentences separately and pooling them, raises clustering ARI by at least 0.05."
research_status: done
verdict: supported
verdict_scope: "tokens v2, four embedding models, similarity thresholds 0.70 to 0.90; does not hold at threshold <= 0.75"
baseline: ../000-baseline/index.md
datasets:
  - path: /datasets/tokens-v2.md
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
best_run: r038
verdict_basis: "supported in 12 of 20 model-threshold pairs; all 8 failures are at threshold <= 0.75"
run_date: 2026-07-24
owner: alex
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

A single sentence carries too little context to place an article. Pooling sentence embeddings
averages away the subject. Embedding the whole article should separate topics better.

# Method

Sweep 4 embedding models x 5 agglomerative similarity thresholds x 2 granularities (sentence,
document) = 40 configurations, 3 repeats each. Cluster with agglomerative clustering at the given
cosine threshold. Full grid and per-configuration metrics in [runs.jsonl](runs.jsonl).

# Results

Best configuration r038 (bge-large-en-v1.5, threshold 0.85, document granularity) reaches ARI 0.71
against the baseline's 0.58.

The per-configuration picture matters more than the headline. Comparing each
(model, threshold) pair at both granularities, document granularity gains at least the claimed
0.05 in 12 of 20 pairs. All 8 pairs where it does not are at threshold 0.70 or 0.75, where the
clustering is permissive enough that the extra context makes no difference. Summary in
[artifacts/sweep-summary.csv](artifacts/sweep-summary.csv); the ARI surface is in
[artifacts/heatmap.svg](artifacts/heatmap.svg).

# Conclusion

Supported, with a stated boundary: the gain is real at thresholds of 0.80 and above and absent
below. Threshold turned out to matter more than model choice, which was not expected.

# Next

The remaining error mode is that articles about the same subject split apart when they name
different people and companies. That is the sub-question.
