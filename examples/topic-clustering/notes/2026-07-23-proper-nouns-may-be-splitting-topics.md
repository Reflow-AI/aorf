---
title: Proper nouns may be splitting topics
brief: >-
  Skimming the baseline clusters, several look like they grouped on person and place names
  rather than on subject matter. Two clusters are the same topic, split by which politician
  is named.
date: 2026-07-23
status: promoted
promoted_to: /questions/article-topic-clustering/questions/proper-noun-handling/index.md
---

Eyeballing the baseline output, not measured. Clusters 4 and 11 both look like budget coverage;
the difference between them seems to be which minister is quoted. Same for 7 and 9 on the
transport story.

If that is real, TF-IDF is weighting names heavily because they are rare, and the embedding
model may be doing something similar for a different reason.

No idea yet whether stripping them helps or destroys the signal — some topics genuinely are
about a specific person. Worth a look, not worth reorganising anything around yet.
