---
type: prior-art
title: Concept drift detection for streaming text
description: Whether drift detection is already solved well enough to adopt rather than invent.
question: ./index.md
conclusion: partially_solved
searched_on: 2026-07-26
approved_by: sam
cost_usd: 8.10
valid_until: 2027-07-26
timestamp: 2026-07-26
---

# What is already known

Concept drift detection is an established subfield with named drift types — sudden, gradual,
recurring, incremental — published methods, and benchmark datasets. The standard approach is a
statistical test over a sliding window of feature distributions, with well-documented detectors
and evaluation protocols.

# What is not settled for us

Published methods assume a stable feature space and, usually, labelled data to measure degradation
against. We have neither until the parent question produces reliable clusters. Nothing we found
addresses the case where the clustering itself is the thing being monitored.

# Conclusion

Partially solved. **Do not build a drift detector.** Adopt a published windowed statistical test
once the parent question yields stable clusters. This changes the shape of the work from research
to mostly integration, which is a cheaper path than we had assumed when we opened the question.

# Cost note

Approved before running; cost about 8 USD. Expected to stay valid for at least a year, so do not
re-run before 2027-07-26.

# Sources

- Concept drift survey literature
- Published drift benchmark datasets and detector implementations
