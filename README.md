# aorf

Track research questions, hypotheses and verdicts in plain markdown, so agents and teammates can
see what you tried and what happened. A profile of Google's Open Knowledge Format.

**[Website](https://reflow-ai.github.io/aorf/)** ·
**[Specification](https://reflow-ai.github.io/aorf/spec.html)** ·
**[Live example](https://reflow-ai.github.io/aorf/demo.html)**

---

Every experiment tracker records runs, params, metrics and artifacts. None of them records a
hypothesis or a verdict. AORF records those, in plain markdown, so both your teammates and your
coding agent can answer "what have we already tried, and what happened" without asking you.

## Start

Hand your agent this URL, in the repository you want to use. Nothing to install:

```
https://reflow-ai.github.io/aorf/v0.1/aorf_scaffolding.md
```

Or use the package:

```bash
pip install aorf
```

```bash
aorf init          # scaffold three documents, nothing more
aorf check         # validate; exit 1 on error. The CI gate
aorf serve         # read-only dashboard on 127.0.0.1:8471
```

## What it records

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

The claim, the outcome, the conditions the outcome holds under, and a number that means something
because there is a reference to compare it against.

## Commands

| | |
|---|---|
| `aorf check [PATH] [--strict] [--json] [--fix]` | validate; exit 1 on error, 2 on an unreadable path |
| `aorf show [PATH] [--json]` | the repo's rollups as data, for an agent in a terminal |
| `aorf serve [PATH] [--port 8471] [--open]` | read-only local dashboard |
| `aorf build [PATH] [--out site/] [--base /prefix]` | static export for GitHub Pages |
| `aorf init [PATH] [--title …] [--question …]` | scaffold a minimal repository |

`check --fix` refreshes derived content only — the generated regions of `synthesis.md` and any
drifted `baseline_value`. It never touches hand-written prose.

## Layout

```
/
├── AGENTS.md                    # the spec itself, so the repo is self-describing
├── index.md                     # type: research
├── datasets/<name>.md           # type: dataset
├── findings/<slug>.md           # type: finding
├── shared/                      # payload: code used by more than one experiment
└── questions/<slug>/
    ├── index.md                 # type: question
    ├── prior-art.md             # type: prior-art, optional
    ├── synthesis.md             # type: synthesis, generated
    └── experiments/<NNN-slug>/
        ├── index.md             # type: experiment
        ├── runs.jsonl           # required when kind: sweep
        ├── src/                 # payload
        └── artifacts/           # payload: ALL outputs go here
```

Day one is three documents: root `index.md`, one question, one experiment. Everything else appears
when earned — `synthesis.md` at three experiments, `prior-art.md` when a search is run,
`datasets/` when an experiment points at data.

## Why the checker is load-bearing

Asking a human or an agent to update four denormalized rollups at the end of every experiment is
asking them to maintain a database by hand. It fails silently: a drifted repo is byte-identical to
a maintained one, while the reading rules tell readers to trust the rollups.

At 80% compliance the convention is worse than nothing, because a confidently read stale rollup
beats you where an absent one sends you to look at the experiments. So **experiment frontmatter is
the only hand-written source of truth, and every rollup is derived** — and `aorf check` enforces 26
integrity rules over it.

## This repository

```
spec/AORF-v0.1.md               the frozen specification (CC BY 4.0)
spec/aorf-v0.1.schema.json      generated from src/aorf/spec.py
src/aorf/spec.py                THE schema. Single source of truth
src/aorf/check.py               the 26 integrity rules, one function each
src/aorf/project.py             the dashboard projection: pure data, no HTML
src/aorf/render/                jinja2 views, artifact dispatch, inline SVG charts
src/aorf/assets/AGENTS.md       the template that travels into each research repo
examples/                       three real repositories; the published demo is their build output
docs/                           the website source, and the versioned scaffolding document
tests/                          one broken fixture per rule, golden projections, security tests
```

Development:

```bash
pip install -e ".[dev]"
```

```bash
pytest -q
ruff check src/ tests/ docs/
python tests/regolden.py         # after an intentional projection change
python tests/regen_schema.py     # after a schema change
python docs/build_site.py        # the website, into _site/
```

Python 3.10+. Three runtime dependencies: `pyyaml`, `markdown-it-py`, `jinja2`. The server is
stdlib and every chart is server-generated inline SVG, so there is no JavaScript charting
dependency, nothing is fetched from a CDN, and nothing is ever executed.

## Licence

Code: [MIT](./LICENSE). Specification text: [CC BY 4.0](./spec/LICENSE).
