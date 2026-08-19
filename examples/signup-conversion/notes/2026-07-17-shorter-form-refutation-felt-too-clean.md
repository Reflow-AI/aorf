---
title: The shorter-form refutation felt too clean
brief: >-
  Removing three fields changed conversion by almost nothing. Plausible, but worth checking the
  instrumentation caught partial form fills before treating the question as closed.
date: 2026-07-17
status: dropped
dropped_reason: >-
  Checked the event stream directly; partial fills were being recorded correctly the whole time.
  The refutation stands as written.
---

The result from
[the shorter form experiment](/questions/onboarding-friction/experiments/002-shorter-signup-form/index.md)
is a clean null, and clean nulls are worth one look at the measurement before they are believed.

Looked. The instrumentation was fine. Keeping the note because "did we check the tracking" is
exactly the question that gets asked again six months later.
