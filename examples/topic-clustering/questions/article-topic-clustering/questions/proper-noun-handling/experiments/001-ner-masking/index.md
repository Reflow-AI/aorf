---
type: experiment
title: Off-the-shelf NER for masking
description: Test whether a standard NER model identifies the proper nouns worth masking.
question: ../../index.md
kind: hypothesis_test
hypothesis: "Masking the person and organisation spans found by an off-the-shelf NER model raises ARI by at least 0.05 over no masking."
research_status: done
verdict: refuted
verdict_scope: "tokens v2, spaCy en_core_web_trf, PERSON and ORG spans only"
baseline: ../000-baseline/index.md
retests: /questions/article-topic-clustering/experiments/002-proper-noun-stripping/index.md
retest_reason: "the original regex-masking result was invalidated on tokens v1; this re-tests the idea properly on v2 with a real NER model"
datasets:
  - path: /datasets/tokens-v2.md
    role: eval
metrics:
  - name: ari
    value: 0.72
    baseline_value: 0.71
    direction: higher_is_better
    primary: true
    n: 50
  - name: cluster_leakage
    value: 0.13
    baseline_value: 0.14
    direction: lower_is_better
    primary: false
    n: 50
run_date: 2026-07-24
owner: alex
code:
  commit: b2c3d4e
  entrypoint: src/run.py
  shared_ref: d4e5f6a
models:
  - provider: spacy
    id: en_core_web_trf
    snapshot: en_core_web_trf-3.7.3
    params: {}
timestamp: 2026-07-24
---

# Hypothesis

If the problem is proper nouns, a model built to find proper nouns should find the ones worth
masking.

# Method

Run spaCy `en_core_web_trf` over each article, replace every PERSON and ORG span with a type
placeholder, then the inherited pipeline unchanged.

# Results

ARI 0.72 against 0.71 — a gain of 0.01, well below the 0.05 claimed. Cluster leakage barely moved.
Error breakdown in [artifacts/ner-errors.md](artifacts/ner-errors.md).

# Conclusion

Refuted. The NER model works correctly and the hypothesis is still wrong, which is the useful part.
NER finds proper nouns by *type*, and type is not what determines whether a name is incidental. An
article about a central bank names that bank because it is the subject; an article about a merger
names the analyst quoted because they happened to be quoted. Both are ORG or PERSON spans. Masking
by type removes signal and noise in roughly equal measure, so the two effects cancel.

# Next

Distinguish incidental from subject-carrying names by how they distribute across articles rather
than by their grammatical type. That is experiment 002.
