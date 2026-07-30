---
type: research
title: Unsupervised topic clustering of a news corpus
description: Group news articles into coherent topics without labelled training data.
research_status: active
aorf_version: "0.1"
tags: [topics, clustering, drift]
tag_vocabulary: [clustering, drift, embeddings, entities, normalisation, topics]
timestamp: 2026-07-26
---

# Problem statement

We have a large corpus of news articles with no topic labels. Editors currently tag articles by
hand, which does not scale and is inconsistent between people. We want to group articles into
topics automatically, closely enough that an editor would accept the grouping.

# Goal and success criteria

Given the article corpus, produce clusters that correspond to what an editor would call a topic.
Success: Adjusted Rand Index of at least 0.85 against a 50-article hand-labelled evaluation set.

# Scope and non-goals

In scope: text representation, clustering method, handling of proper nouns, detecting when the
topic mix shifts. Out of scope: naming the clusters in human-readable form, serving the model,
and the editorial interface.

# Questions

- [Can we cluster articles into coherent topics?](questions/article-topic-clustering/index.md) (active)
- [Can we detect when the topic mix shifts over time?](questions/topic-drift-detection/index.md) (literature_review)

# Datasets

- [News article corpus](datasets/articles-raw.md) (source of truth)
- [Tokenised articles v2](datasets/tokens-v2.md) (derived, current)
- [Tokenised articles v1](datasets/tokens-v1.md) (derived, withdrawn)

# Findings

- [tokens v1 had duplicate rows](findings/tokens-v1-duplicate-rows.md) (blocking, resolved)
