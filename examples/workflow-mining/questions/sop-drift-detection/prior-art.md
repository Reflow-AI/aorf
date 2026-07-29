---
type: prior-art
title: Concept drift detection in process mining
description: Whether process drift detection is already solved well enough to adopt rather than invent.
question: ./index.md
conclusion: partially_solved
searched_on: 2026-07-26
approved_by: akbay
cost_usd: 8.10
timestamp: 2026-07-26
---

# What is already known
Concept drift detection for process mining is an established subfield with published methods and evaluation datasets. Sudden, gradual, recurring and incremental drift are all named and studied. Statistical tests over sliding windows of trace features are the standard approach.

# What is not settled for us
Published methods assume a clean event log with case ids and known activity labels. We have neither until the parent question is answered.

# Conclusion
Partially solved. Do not invent a drift detector. Adopt an existing windowed statistical method once we have reliable activity labels. This turned a research question into a mostly-integration question, which is a cheaper path than we assumed.

# Cost note
Approved before running, cost about 8 USD. This answer is expected to stay valid for at least a year; do not re-run.

# Sources
- Process mining concept drift survey literature
- Published drift benchmark datasets
