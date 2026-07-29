---
type: question
title: Can we detect when an established process starts being done differently?
description: Notice that the same process is now executed in a new way, without re-labelling everything.
parent: ../../index.md
research_status: literature_review
primary_metric: drift_detection_f1
metric_direction: higher_is_better
owner: onur
tags: [drift, sop]
timestamp: 2026-07-26
---

# Question
Given a known process and a stream of new executions, can we detect that the process is now being carried out differently, rather than that a different process is happening?

# Why this matters
The root goal assumes processes are stable, and they are not. If we cannot tell change from noise, every task description we produce decays silently.

# Current best result
None yet. Blocked on the parent question: we cannot detect drift in something we cannot yet identify reliably.

# Prior art
See [prior-art.md](prior-art.md). Partially solved externally, which changed our plan.

# Experiments
- [001 bag-of-steps exploration](experiments/001-bag-of-steps-exploration/index.md) (abandoned)
