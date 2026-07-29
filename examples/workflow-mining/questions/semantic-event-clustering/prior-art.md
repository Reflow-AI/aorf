---
type: prior-art
title: Existing work on session and task segmentation
description: Whether event-stream task segmentation is already solved elsewhere.
question: ./index.md
conclusion: open
searched_on: 2026-07-05
approved_by: akbay
cost_usd: 12.40
timestamp: 2026-07-05
---

# What is already known
Web session segmentation by time gap is well established and cheap. Process mining has mature tooling for event logs that already carry a case id.

# What is not settled for us
Our events have no case id, and time gaps do not align with task boundaries because people interleave tasks. No source covers segmenting untagged desktop interaction streams into semantic tasks.

# Conclusion
Open. Time-gap segmentation is worth having as a cheap baseline, but the core problem is not solved in the literature we can find.

# Cost note
This search was approved before running and cost about 12 USD in API spend. Do not repeat it before 2027 unless the question changes.

# Sources
- Process mining survey literature
- Web session identification methods
