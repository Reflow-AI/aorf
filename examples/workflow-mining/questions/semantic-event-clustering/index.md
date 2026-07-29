---
type: question
title: Can we group raw events into semantically meaningful clusters?
description: Collapse fine-grained events into task-level units so downstream work operates on tasks, not clicks.
parent: ../../index.md
research_status: active
primary_metric: ari
metric_direction: higher_is_better
metric_target: 0.85
owner: onur
tags: [clustering, embeddings]
timestamp: 2026-07-26
---

# Question
Can sequential raw events be grouped into clusters that correspond to what a person would call one task?

# Why this matters
The root goal is describing a person's work from raw events. Everything downstream depends on having task-level units. Ten events that are all "log into Google" must become one thing.

# Current best result
Group-level embeddings, ARI 0.71 vs baseline 0.58, on events v2. See [001](experiments/001-group-vs-event-embeddings/index.md).

# Prior art
See [prior-art.md](prior-art.md).

# Experiments
See [synthesis.md](synthesis.md).

# Sub-questions
- [How do we stop entity noise from splitting identical tasks?](questions/entity-canonicalization/index.md) (answered)
