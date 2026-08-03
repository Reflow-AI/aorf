---
type: experiment
title: Strip proper nouns before embedding
description: Test whether replacing names and organisations with placeholders raises clustering quality.
question: ../../index.md
kind: hypothesis_test
hypothesis: "Replacing person and organisation names with placeholders before embedding raises clustering ARI by at least 0.05."
research_status: done
verdict: refuted
verdict_scope: "tokens v1 only; the result is not trustworthy because that dataset was withdrawn"
verdict_state: invalidated
invalidated_by: /findings/tokens-v1-duplicate-rows.md
invalidation_reason: "ran on tokens v1, which had 12% duplicate rows inflating every cluster size"
superseded_by: /questions/article-topic-clustering/questions/proper-noun-handling/experiments/002-statistical-token-classification/index.md
baseline: ../000-baseline/index.md
datasets:
  - path: /datasets/tokens-v1.md
    role: eval
metrics:
  - name: ari
    value: 0.63
    baseline_value: 0.54
    direction: higher_is_better
    primary: true
    n: 50
run_date: 2026-07-18
owner: alex
code:
  commit: 7a8b9c0
  entrypoint: src/run.py
  shared_ref: a1b2c3d
timestamp: 2026-07-21
---

# Hypothesis

Articles on the same subject look different to the embedder because they name different people
and companies. Masking those names should bring them together.

# Method

Regex-based masking of capitalised token runs, then the baseline pipeline unchanged.

# Results

ARI 0.63 against a v1 baseline of 0.54. At the time this read as +0.09 and therefore supported.

# Conclusion

**Do not use this result.** It ran on tokens v1, later withdrawn for duplicate rows, so both the
measurement and the baseline it was compared against are inflated. Because both moved, the delta
cannot be salvaged by rescaling either one.

The underlying question was worth keeping, so it was re-opened properly as a sub-question, where a
better method was found and measured on v2. This document stays for the record: that regex masking
was tried is worth knowing, and its number is not.
