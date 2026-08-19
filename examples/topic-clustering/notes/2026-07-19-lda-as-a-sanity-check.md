---
title: Try LDA as a sanity check
brief: >-
  Wondered whether a classical topic model should be run alongside the embedding approach, as
  a reference point rather than a serious contender.
date: 2026-07-19
status: dropped
dropped_reason: >-
  Answered by the prior-art search: LDA on short news text is well documented as weaker than
  embedding-based clustering, and it would not be comparable on our primary metric anyway.
---

The thought was that a well-understood baseline would make the embedding numbers easier to
trust, even if it lost.

Dropped after reading [the prior-art write-up](/questions/article-topic-clustering/prior-art.md),
which covers this directly. Keeping the note so the same idea does not get re-raised and
re-investigated in three months.
