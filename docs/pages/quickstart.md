# Quickstart

## The short way: hand your agent a URL

```
https://reflow-ai.github.io/aorf/v0.1/aorf_scaffolding.md
```

Paste that into your coding agent, in the repository you want to use. Nothing to install.

The agent fetches a versioned, immutable instruction document, asks you four questions — what
you are trying to find out, what "done" looks like, the first question you need to answer, and
what data you have — and then writes three documents plus an `AGENTS.md`.

It will also tell you what a baseline for your first question would look like, and why it would
be cheap. That is a suggestion, not a gate. Decline it and `baseline: none` with your reason is
a perfectly valid permanent answer.

`/v0.1/` never changes once published. New versions get new URLs, so whatever you pinned keeps
behaving the way it did.

## The package

```bash
pip install aorf
```

```bash
aorf init                # scaffold three documents, nothing more
aorf check               # validate; exit 1 on error. This is the CI gate
aorf check --strict      # also fail on stale generated regions and depth 4+
aorf check --fix         # refresh derived content, never hand-written prose
aorf show --json         # your repo's rollups as data, for an agent in a terminal
aorf serve               # read-only dashboard on 127.0.0.1:8471
aorf build --out site/   # static export you can publish anywhere
```

Python 3.10+. Three runtime dependencies — `pyyaml`, `markdown-it-py`, `jinja2`. The server is
stdlib, and every chart is server-generated inline SVG, so there is no JavaScript charting
dependency and nothing is ever fetched from a CDN.

## Wire the checker into CI

The checker matters more than the dashboard: a dashboard that renders a repo which quietly lies
is worse than no dashboard.

```yaml
- run: pip install aorf
- run: aorf check .
```

If your repo uses git LFS for source data, remember `lfs: true` on checkout — otherwise the
checker and any published dashboard see pointer files.

```yaml
- uses: actions/checkout@v4
  with:
    lfs: true
```

## Day one is three documents

```
index.md                                          type: research
questions/<slug>/index.md                         type: question
questions/<slug>/experiments/001-<slug>/index.md   type: experiment
```

Everything else appears when earned:

| This appears | when |
|---|---|
| `synthesis.md` | a question reaches three experiments |
| `prior-art.md` | you actually run a search |
| `datasets/` | an experiment points at data |
| `findings/` | you discover something that is not an experiment result |
| nested `questions/` | a question genuinely splits |

## What a completed experiment looks like

```yaml
---
type: experiment
title: Remove the credit card requirement
description: Test whether dropping card-up-front raises trial-to-paid conversion.
question: ../../index.md
kind: hypothesis_test
hypothesis: "Removing the credit card requirement at signup raises trial-to-paid
  conversion by at least 4 percentage points."
research_status: done
verdict: supported
verdict_scope: "April to June 2026 cohorts, self-serve signups only"
baseline: ../000-baseline/index.md
datasets:
  - path: /datasets/signups-2026q2.md
    role: eval
metrics:
  - name: conversion_rate
    value: 0.34
    baseline_value: 0.28
    direction: higher_is_better
    primary: true
    n: 4188
    ci: [0.32, 0.36]
run_date: 2026-07-10
owner: akbay
tracker: GROW-118
---
```

Then the body: `# Hypothesis`, `# Method`, `# Results`, `# Conclusion`, `# Next`. All outputs go
in `artifacts/` next to the document — CSVs, images, HTML reports, a `runs.jsonl` for a sweep.
The dashboard renders each by type without you listing them anywhere.

## Two rules worth knowing up front

**The hypothesis is written before the run and never edited after.** If the result suggests a
different claim, that is a new experiment with `retests` pointing at the old one. `aorf check`
checks this against git history, because a hypothesis rewritten to match its result is not a
hypothesis.

**Record `refuted` and `inconclusive` as readily as `supported`.** A negative result recorded
once is what stops it being paid for twice, and it is exactly what every other tool throws away.

[The full specification &rarr;](./spec.html)
