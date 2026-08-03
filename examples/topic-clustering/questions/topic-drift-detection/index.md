---
type: question
title: Can we detect when the topic mix shifts over time?
description: Notice that the corpus has started covering different things, without re-labelling everything.
parent: ../../index.md
research_status: literature_review
primary_metric: drift_detection_f1
metric_direction: higher_is_better
owner: sam
tags: [drift, topics]
timestamp: 2026-07-26
---

# Question

Given clusters fitted on one period and a stream of new articles, can we detect that the topic mix
has changed — as opposed to normal week-to-week variation?

# Why this matters

The root goal assumes topics are stable, and news topics are not. A model fitted in January
silently degrades by June, and without a drift signal nobody notices until the clusters are
visibly wrong.

# Current best result

None yet. Waiting on the parent question: there is no point detecting drift in clusters that are
not yet reliable.

# Prior art

See [prior-art.md](prior-art.md). Partially solved externally, which changed the plan here.

# Experiments

- [001 bag-of-terms exploration](experiments/001-bag-of-terms-exploration/index.md) (abandoned)

# Sub-questions

None.
