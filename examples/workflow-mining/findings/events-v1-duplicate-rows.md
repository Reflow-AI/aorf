---
type: finding
title: events v1 had 12% duplicate rows
description: A double ingest inflated cluster sizes and invalidated results computed on v1.
scope: repo
severity: blocking
affects:
  - /datasets/events-v1.md
  - /questions/semantic-event-clustering/experiments/002-entity-stripping/index.md
discovered: 2026-07-20
source: "noticed incidentally while eyeballing cluster sizes in 002"
status: resolved
timestamp: 2026-07-21
---

# What happened
Cluster sizes looked implausibly uniform. Counting distinct event ids showed 12% duplicates, traced to the ingest running twice on the June batch.

# Impact
Any metric computed on events v1 is inflated. Experiment 002 under semantic-event-clustering is invalidated.

# Resolution
`build_events.py` now deduplicates on ingest. Regenerated as [events v2](../datasets/events-v2.md). Affected experiments marked `verdict_state: invalidated`.
