---
type: experiment
title: Bag-of-steps region matching, exploration
description: Explore whether a permissive bag-of-steps match can find process executions without a case id.
question: ../../index.md
kind: exploration
research_status: abandoned
research_status_reason: "superseded by the prior-art conclusion; adopting a published drift method is cheaper than inventing one, and this needed the parent question answered first"
verdict: inconclusive
baseline: none
baseline_reason: "no production or reference method exists for this question; nothing to replicate"
datasets:
  - path: /datasets/events-v2.md
    role: eval
run_date: 2026-07-23
owner: onur
cost_usd: 0
timestamp: 2026-07-26
---

# Goal
Not a hypothesis test. Explore whether treating a process as an unordered bag of steps, and marking any region containing more than half of them, finds real executions. Some processes have no clean start or end step, so strict sequence matching fails.

# Method
Define 7 steps for one known process by hand. Slide a window over events, score by fraction of steps present, mark regions above 0.5.

# Observations
Regions were found, but without a case id there is no way to tell whether a region is one execution or two interleaved ones. Precision could not be measured against the 200-item ground truth list because region boundaries were ambiguous.

# Why abandoned
The prior-art search finished after this started and showed drift detection is largely solved given labelled traces. The blocking dependency is the parent question, not this method. Recording it so nobody repeats the attempt.

# What was learned
Case id extraction is the real prerequisite, and the statistical token work under the parent question now supplies it.
