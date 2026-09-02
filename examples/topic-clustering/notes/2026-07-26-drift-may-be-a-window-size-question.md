---
title: Drift may be a window-size question
brief: >-
  Most of the drift-detection literature assumes a fixed window. Our topic mix moves on both
  a weekly news cycle and a much slower seasonal one, so a single window may be the wrong shape.
date: 2026-07-26
status: open
---

Reading around drift detection while the literature review is open. Nearly everything found so
far picks one window length and compares distributions across it.

Two timescales are visible in the corpus by eye: a fast one that tracks whatever the week's story
is, and a slow one that looks seasonal. A detector tuned to the fast one will probably call the
slow one drift constantly.

Relevant to [the drift question](/questions/topic-drift-detection/index.md) but not an answer to
it, and not something to fold into that document on the strength of a hunch.
