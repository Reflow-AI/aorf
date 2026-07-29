---
type: experiment
title: Strip entities before embedding
description: Test whether replacing names and ids with placeholders raises clustering quality.
question: ../../index.md
kind: hypothesis_test
hypothesis: "Replacing person names and record ids with placeholders before embedding raises clustering ARI by at least 0.05."
research_status: done
verdict: refuted
verdict_scope: "events v1 only; result not trustworthy, dataset withdrawn"
verdict_state: invalidated
invalidated_by: /findings/events-v1-duplicate-rows.md
invalidation_reason: "ran on events v1, which had 12% duplicate rows inflating cluster sizes"
superseded_by: /questions/semantic-event-clustering/questions/entity-canonicalization/experiments/002-statistical-container-detection/index.md
baseline: ../000-baseline/index.md
datasets:
  - path: /datasets/events-v1.md
    role: eval
metrics:
  - name: ari
    value: 0.63
    baseline_value: 0.54
    direction: higher_is_better
    primary: true
    n: 50
run_date: 2026-07-18
owner: onur
code:
  commit: 7a8b9c0
  entrypoint: src/run.py
  shared_ref: a1b2c3d
timestamp: 2026-07-21
---

# Hypothesis
Identical tasks look different to the embedder because they contain different names and ids. Masking those should merge them.

# Method
Regex-based masking of names, emails and ids, then the baseline pipeline unchanged.

# Results
ARI 0.63 vs a v1 baseline of 0.54. At the time this read as +0.09 and therefore supported.

# Conclusion
Do not trust this result. It ran on events v1, later withdrawn for duplicate rows, so both the value and the baseline are inflated. The underlying question was re-opened properly as a sub-question, where a better method was found. Kept for the record, not as evidence.
