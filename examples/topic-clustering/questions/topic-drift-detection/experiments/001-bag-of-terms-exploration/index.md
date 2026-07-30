---
type: experiment
title: Bag-of-terms window comparison, exploration
description: Explore whether comparing term distributions between adjacent windows flags topic shifts.
question: ../../index.md
kind: exploration
research_status: abandoned
research_status_reason: "superseded by the prior-art conclusion: adopting a published drift detector is cheaper than inventing one, and this needed the parent question answered first"
verdict: inconclusive
baseline: none
baseline_reason: "no reference method exists for this question yet; there is nothing to replicate or beat"
datasets:
  - path: /datasets/tokens-v2.md
    role: eval
run_date: 2026-07-23
owner: sam
cost_usd: 0
timestamp: 2026-07-26
---

# Goal

Not a hypothesis test. Explore whether a crude signal — comparing raw term-frequency distributions
between adjacent four-week windows — flags the periods where an editor would say the topic mix
changed.

# Method

Split the corpus into four-week windows. For each adjacent pair, compute a chi-squared statistic
over the 5,000 most frequent terms. Flag any pair above an arbitrary percentile. Compare flagged
periods against six shifts an editor identified by hand.

# Observations

Windows were flagged, and some coincided with the editor's six shifts. But the signal fires just as
often on ordinary news cycles: an election week or a major sports event moves term frequencies as
much as a genuine change in what the corpus covers.

With only six hand-identified shifts there is no way to separate the two cases. Precision could not
be estimated meaningfully at that sample size.

# Why abandoned

Two reasons, and the second is the real one:

1. The prior-art search finished after this started and showed drift detection is largely solved
   given a stable feature space. Building a detector here would be reinventing it, worse.
2. The blocking dependency is the parent question. Term frequencies are the wrong feature space
   entirely — drift should be measured over topic assignments, which do not exist reliably yet.

Recorded rather than deleted so nobody spends another two days on the same approach.

# What was learned

A crude term-frequency signal cannot distinguish a news cycle from a topic shift, which is worth
knowing independently of the method eventually adopted. The statistical token classification under
the parent question produces per-article subject tokens, and that is a far better feature space to
measure drift over than raw term frequencies.
