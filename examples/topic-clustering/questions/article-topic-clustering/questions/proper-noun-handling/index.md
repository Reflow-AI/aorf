---
type: question
title: How do we stop proper nouns from splitting the same topic?
description: Identify which names carry the subject and which are incidental, and mask only the incidental ones.
parent: ../../index.md
research_status: answered
primary_metric: ari
metric_direction: higher_is_better
answer: "Classify capitalised tokens statistically by how they distribute across articles, then mask only the incidental ones. ARI 0.79 against 0.71 for no masking."
answer_evidence:
  - ./experiments/002-statistical-token-classification/index.md
closed: 2026-07-25
owner: alex
tags: [entities, normalisation]
timestamp: 2026-07-25
---

# Question

Two articles about the same subject often name different people and organisations, which pushes
them into different clusters. Which of those names should be removed before embedding, and which
of them *are* the subject?

# Why this matters

This is the dominant remaining error mode of the parent question's best pipeline. Masking every
proper noun is not the answer: an article about a specific central bank is *about* that bank, so
removing the name destroys the signal along with the noise.

# Current best result

Statistical token classification, ARI 0.79 against the inherited baseline of 0.71. See
[002](experiments/002-statistical-token-classification/index.md).

# Experiments

See [synthesis.md](synthesis.md).

# Sub-questions

None.
