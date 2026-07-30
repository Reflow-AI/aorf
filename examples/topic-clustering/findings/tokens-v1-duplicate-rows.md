---
type: finding
title: tokens v1 had 12% duplicate rows
description: A double-emit in the paragraph splitter inflated cluster sizes and invalidated results computed on v1.
scope: repo
severity: blocking
affects:
  - /datasets/tokens-v1.md
  - /questions/article-topic-clustering/experiments/002-proper-noun-stripping/index.md
discovered: 2026-07-20
source: "noticed incidentally while eyeballing cluster sizes in experiment 002"
status: resolved
timestamp: 2026-07-21
---

# What happened

Cluster sizes looked implausibly uniform. Counting distinct article ids showed 12% duplicates,
traced to the paragraph splitter in `build_tokens.py` emitting each article once per paragraph
batch instead of once per article.

# Impact

Any metric computed on tokens v1 is inflated, including the baseline it was compared against, so
the *delta* is wrong in both directions and cannot be corrected after the fact. Experiment 002
under article-topic-clustering is invalidated.

# Resolution

`build_tokens.py` now emits one row per article, verified by an id-uniqueness assertion.
Regenerated as [tokens v2](../datasets/tokens-v2.md). The affected experiment is marked
`verdict_state: invalidated` and kept, rather than deleted — that the approach was tried is worth
knowing even though its numbers are not.
