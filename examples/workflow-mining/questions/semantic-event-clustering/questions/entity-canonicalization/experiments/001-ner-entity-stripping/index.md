---
type: experiment
title: Off-the-shelf NER for entity masking
description: Test whether a standard NER model identifies the tokens worth masking.
question: ../../index.md
kind: hypothesis_test
hypothesis: "Masking tokens identified by an off-the-shelf NER model raises ARI by at least 0.05 over the no-masking baseline."
research_status: done
verdict: refuted
verdict_scope: "events v2, spaCy en_core_web_trf"
baseline: ../000-baseline/index.md
retests: /questions/semantic-event-clustering/experiments/002-entity-stripping/index.md
retest_reason: "the original entity-stripping result was invalidated with events v1; re-testing properly on v2"
datasets:
  - path: /datasets/events-v2.md
    role: eval
metrics:
  - name: ari
    value: 0.72
    baseline_value: 0.71
    direction: higher_is_better
    primary: true
    n: 50
run_date: 2026-07-24
owner: onur
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
Names and ids are named entities, so a named entity recogniser should find exactly the tokens to mask.

# Method
Run spaCy NER over window titles and text content, mask PERSON, ORG and CARDINAL spans, then the baseline pipeline.

# Results
ARI 0.72 vs 0.71. No meaningful change. Error analysis in [artifacts/ner-errors.md](artifacts/ner-errors.md) shows why: the tokens that split clusters are mostly not named entities. They are record ids embedded in titles, status words like "in progress", and shared document names that appear in every case.

# Conclusion
Refuted. NER is the intuitive tool and the wrong one. The useful distinction is not entity-vs-not, it is varies-per-case vs shared-across-cases.

# Next
Classify tokens by their distribution across cases instead of by linguistic type.
