---
type: research
title: Can an LLM label screenshots well enough to skip manual annotation?
description: Two day spike to find out whether we can stop hand-labelling screenshots.
research_status: active
aorf_version: "0.1"
timestamp: 2026-07-26
---

# Problem statement
Hand-labelling screenshots for the action detection training set costs about 6 hours per 1000 images.

# Goal and success criteria
Decide, within two days, whether an LLM can label at 90% agreement with a human. If yes, we stop hand-labelling.

# Questions
- [Does an LLM agree with human labels on screenshots?](questions/llm-agreement/index.md) (active)
