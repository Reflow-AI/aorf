---
type: experiment
title: Baseline, parent's best pipeline with no masking
description: Re-run the parent question's winning configuration unchanged, so this sub-question has a comparable reference.
question: ../../index.md
kind: baseline
research_status: done
verdict: n/a
baseline: none
baseline_reason: "this document is the baseline; it re-runs the parent question's best configuration r038 unchanged"
datasets:
  - path: /datasets/tokens-v2.md
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
owner: alex
code:
  commit: 9f2c1ab
  entrypoint: ../../../001-document-vs-sentence-embeddings/src/sweep.py
  shared_ref: d4e5f6a
timestamp: 2026-07-24
---

# Method

No new method. This re-runs configuration r038 from the parent question's sweep — bge-large-en-v1.5,
threshold 0.85, document granularity — with no proper-noun handling at all.

A sub-question's baseline inherits the parent's current best. Inventing a fresh, cheaper baseline
here would make the numbers under this sub-question incomparable with the numbers above it, and
the whole point of the sub-question is to improve on what the parent already achieved.

# Results

ARI 0.71, matching the parent's best run, which is the confirmation that the re-run is faithful.
Cluster leakage 0.14 is recorded here as a secondary metric so the masking experiments have
something to compare against on that axis too.

# Conclusion

Reference established. Anything under this sub-question has to beat 0.71 to be worth adopting.
