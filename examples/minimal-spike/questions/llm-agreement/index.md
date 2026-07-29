---
type: question
title: Does an LLM agree with human labels on screenshots?
description: Measure agreement between LLM-produced labels and the existing human labels.
parent: ../../index.md
research_status: active
primary_metric: agreement
metric_direction: higher_is_better
metric_target: 0.90
timestamp: 2026-07-26
---

# Question
On our existing labelled set, how often does an LLM produce the same label as the human annotator?

# Why this matters
This is the whole spike. If agreement is high we delete a recurring 6 hour cost.

# Current best result
0.86 agreement, below the 0.90 bar. See [001](experiments/001-gpt-labeling-spike/index.md).

# Experiments
- [001 first pass](experiments/001-gpt-labeling-spike/index.md) (done, inconclusive)
