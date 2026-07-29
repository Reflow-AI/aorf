---
type: question
title: How do we stop entity noise from splitting identical tasks?
description: Identify and neutralise the varying tokens that make the same task look different.
parent: ../../index.md
research_status: answered
primary_metric: ari
metric_direction: higher_is_better
answer: "Classify varying tokens statistically into entity, container and enum, then mask only entities. ARI 0.79 vs 0.71."
answer_evidence:
  - ./experiments/002-statistical-container-detection/index.md
closed: 2026-07-25
owner: onur
tags: [entities, normalisation]
timestamp: 2026-07-25
---

# Question
Which varying tokens in an event stream should be masked before embedding, and how do we tell them apart?

# Why this matters
The parent question got to ARI 0.71 with grouped embeddings, and the dominant remaining error is identical tasks splitting into separate clusters because of names and ids. Fixing this raises the parent metric directly.

# Current best result
Statistical container detection, ARI 0.79 vs parent baseline 0.71. See [002](experiments/002-statistical-container-detection/index.md).

# Experiments
See [synthesis.md](synthesis.md).
