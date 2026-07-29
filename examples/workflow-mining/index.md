---
type: research
title: Workflow mining from raw interaction data
description: Understand what work people actually do, from raw UI interaction events.
research_status: active
aorf_version: "0.1"
tags: [workflow, clustering, sop]
tag_vocabulary: [clustering, drift, embeddings, entities, normalisation, sop, workflow]
timestamp: 2026-07-26
---

# Problem statement
We capture raw UI interaction events but cannot say what work a person actually did. Events are too fine-grained: a single login is 10 events, and the same task looks different across users and tools.

# Goal and success criteria
Given a day of one person's raw events, produce a semantically accurate description of the tasks they performed. Success: on a 50-task hand-labelled set, we recover the correct task boundaries and labels for at least 80% of tasks.

# Scope and non-goals
In scope: clustering, entity handling, task boundary detection. Out of scope: the customer-facing visualisation, production deployment.

# Questions
- [Can we group raw events into semantically meaningful clusters?](questions/semantic-event-clustering/index.md) (active)
- [Can we detect when an established process starts being done differently?](questions/sop-drift-detection/index.md) (literature_review)

# Datasets
- [Raw interaction events](datasets/raw-interactions.md) (source of truth)
- [Normalised events v2](datasets/events-v2.md) (derived, current)
- [Normalised events v1](datasets/events-v1.md) (derived, withdrawn)

# Findings
- [events v1 had duplicate rows](findings/events-v1-duplicate-rows.md) (blocking, resolved)
