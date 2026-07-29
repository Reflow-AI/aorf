---
type: experiment
title: First pass LLM labelling on 200 screenshots
description: Compare LLM labels against existing human labels on a small sample.
question: ../../index.md
kind: hypothesis_test
hypothesis: "An LLM labelling screenshots from a fixed prompt agrees with human labels at least 90% of the time."
research_status: done
verdict: inconclusive
verdict_scope: "200 screenshots, single prompt, one model snapshot"
baseline: none
baseline_reason: "no existing automated labeller to compare against; the human labels are the reference, not a baseline method"
metrics:
  - name: agreement
    value: 0.86
    direction: higher_is_better
    primary: true
    n: 200
    ci: [0.81, 0.90]
run_date: 2026-07-26
cost_usd: 3.40
models:
  - provider: openai
    id: gpt-4o
    snapshot: gpt-4o-2024-08-06
    params: {temperature: 0}
timestamp: 2026-07-26
---

# Hypothesis
A single well-written prompt is enough to match human labelling on this narrow task.

# Method
200 screenshots sampled from the existing labelled set. One prompt, kept in `src/prompts/label.v1.txt`. Compare exact label match.

# Results
0.86 agreement, CI 0.81 to 0.90. The bar is 0.90 and the interval touches it, so this neither passes nor clearly fails. Disagreements cluster on two label classes.

# Conclusion
Inconclusive at n=200. Worth one more run with a larger sample and a revised prompt targeting the two confused classes before deciding.
