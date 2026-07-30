# AORF, the Open Research Format

AORF is a convention for laying out a research repository so that the reasoning in it is
machine-readable: not only what was run, but what was expected, what the result was, and what
remains open.

Documents are markdown with YAML frontmatter. There is no database and no service. The format is a
profile of Google Cloud's [Open Knowledge Format](./okf.html), so every AORF document is also a
valid OKF document.

## What it records

An experiment tracker records runs: parameters, metrics, artifacts, timings. AORF records the layer
above that — the claim being tested and what happened to it.

```yaml
kind: hypothesis_test
hypothesis: "Removing the credit card requirement at signup raises trial-to-paid
  conversion by at least 4 percentage points."
research_status: done
verdict: supported
verdict_scope: "April to June 2026 cohorts, self-serve signups only"
baseline: ../000-baseline/index.md
metrics:
  - name: conversion_rate
    value: 0.34
    baseline_value: 0.28
    direction: higher_is_better
    primary: true
```

Four things are readable from that without opening the body: the claim, the outcome, the conditions
the outcome is asserted under, and a measurement with a reference to compare it against.

## Repository layout

```
/
├── AGENTS.md                    the format's rules, so the repo is self-describing
├── index.md                     type: research
├── datasets/<name>.md           type: dataset
├── findings/<slug>.md           type: finding
├── shared/                      payload: code used by more than one experiment
└── questions/<slug>/
    ├── index.md                 type: question
    ├── prior-art.md             type: prior-art, optional
    ├── synthesis.md             type: synthesis, generated
    └── experiments/<NNN-slug>/
        ├── index.md             type: experiment
        ├── runs.jsonl           required when kind: sweep
        ├── src/                 payload
        └── artifacts/           payload: all outputs go here
```

Three documents are required to start: the root `index.md`, one question, one experiment. The rest
appear when there is something to put in them — `synthesis.md` at three experiments, `prior-art.md`
when a search has been run, `datasets/` when an experiment references data.

## The tooling

`pip install aorf` provides four commands. None of them is required to use the format.

| Command | What it does |
|---|---|
| `aorf check` | validates the repository against 26 integrity rules; exits 1 on error |
| `aorf show --json` | prints the repository's derived rollups as data |
| `aorf serve` | a read-only local dashboard |
| `aorf build` | a static export |

`aorf check` is the part that carries weight. The format's central constraint is that experiment
frontmatter is the only hand-written source of truth and every summary is derived from it. That
constraint is only worth anything if something enforces it, because a repository whose summaries
have drifted is byte-for-byte indistinguishable from one that is current.

## Where to start

- [Rationale](./rationale.html) — why the format records what it records
- [Quickstart](./quickstart.html) — setting up a repository, with or without the package
- [Specification](./spec.html) — AORF v0.1 in full, plus the JSON Schema
- [Examples](./examples.html) — three repositories, rendered by `aorf build`
- [Relation to OKF](./okf.html) — what AORF inherits, and the one place it diverges

To set up a repository without installing anything, an agent can be given the scaffolding
document directly:

```
https://reflow-ai.github.io/aorf/v0.1/aorf_scaffolding.md
```

It contains the format's rules and an interview to fill in the first three documents. The
equivalent with the package installed is `aorf init`.
