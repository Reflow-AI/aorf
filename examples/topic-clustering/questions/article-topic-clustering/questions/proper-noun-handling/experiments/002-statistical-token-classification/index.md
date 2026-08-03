---
type: experiment
title: Statistical token classification into subject, incidental and boilerplate
description: Classify capitalised tokens by how they distribute across articles, then mask only the incidental ones.
question: ../../index.md
kind: hypothesis_test
hypothesis: "Classifying capitalised tokens by their cross-article distribution into subject, incidental and boilerplate, and masking only the incidental ones, raises ARI by at least 0.05 over no masking."
research_status: done
verdict: supported
verdict_scope: "tokens v2, 184k articles, January 2024 to June 2026; thresholds fitted on a held-out month"
baseline: ../000-baseline/index.md
also_informs:
  - /questions/topic-drift-detection/index.md
datasets:
  - path: /datasets/tokens-v2.md
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
    n: 50
run_date: 2026-07-25
owner: alex
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

Whether a name should be masked is a property of its distribution, not its grammatical type. A
name that appears in many otherwise-unrelated articles is incidental. A name concentrated in a
small set of closely related articles is the subject.

# Method

For every capitalised token, compute document frequency and the concentration of its occurrences
across baseline clusters. Classify into three buckets:

- **boilerplate** — very high document frequency, spread evenly (wire-service names, weekdays)
- **incidental** — moderate frequency, spread evenly across unrelated articles
- **subject** — concentrated in few, closely related articles

Mask boilerplate and incidental; keep subject tokens. Thresholds fitted on a held-out month and
then frozen. Classification counts in
[artifacts/token-classes.csv](artifacts/token-classes.csv).

# Results

ARI 0.79 against 0.71, a gain of 0.08 with a confidence interval of [0.75, 0.83] that excludes the
baseline. Cluster leakage more than halved, from 0.14 to 0.06, which is the clearer signal: the
gain comes from articles that were previously bleeding into neighbouring clusters.

# Conclusion

Supported. The distinction that mattered was distributional, not grammatical — which is why
experiment 001 could use a correct NER model and still fail.

The stated scope is doing real work here. Thresholds were fitted on this corpus and this date
range; on a corpus with different boilerplate conventions they would need refitting, and nothing
here shows the three-bucket split survives that.

# Next

The token classification produces a per-article subject-token set as a by-product, which is
exactly the input the topic-drift question needs. Recorded via `also_informs`.
