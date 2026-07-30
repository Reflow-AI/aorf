---
type: question
title: Can we cluster articles into coherent topics?
description: Group articles so that each cluster corresponds to what an editor would call one topic.
parent: ../../index.md
research_status: active
primary_metric: ari
metric_direction: higher_is_better
metric_target: 0.85
owner: alex
tags: [clustering, embeddings]
timestamp: 2026-07-26
---

# Question

Can articles be grouped into clusters that correspond to what an editor would call one topic,
without any labelled training data?

# Why this matters

Everything else in this research assumes topic-level units exist. If the clusters do not match
an editor's judgement, no amount of downstream work recovers from it.

# Current best result

Document-level embeddings, ARI 0.71 against a baseline of 0.58, on tokens v2. See
[001](experiments/001-document-vs-sentence-embeddings/index.md).

# Prior art

See [prior-art.md](prior-art.md).

# Experiments

See [synthesis.md](synthesis.md).

# Sub-questions

- [How do we stop proper nouns from splitting the same topic?](questions/proper-noun-handling/index.md) (answered)
