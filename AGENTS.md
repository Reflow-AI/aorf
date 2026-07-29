# AGENTS.md — working on the `aorf` package

This repository *defines* AORF; it is not itself an AORF research repository, so there is no root
`index.md` here. The contract that travels into research repos is
[`src/aorf/assets/AGENTS.md`](src/aorf/assets/AGENTS.md) — edit that file if you mean to change
what agents are told about the format.

## The rules that matter here

**`src/aorf/spec.py` is the only place a field may be defined.** `check.py` enforces it and
`spec/aorf-v0.1.schema.json` is generated from it. If you find yourself writing a field name in a
second place, that is the bug.

**Every integrity rule is one function in `check.py`, named `rNN_…`, with a docstring saying why
the rule exists.** Add a rule and you add a test in `tests/test_rules.py` that breaks exactly one
thing and asserts that one rule fires. `tests/test_spec.py` enforces the numbering, the
docstrings, and that the rule appears in the spec's table.

**`project.py` returns plain data and never reads the clock.** It is the contract the dashboard
and `aorf show --json` share, and it is snapshotted in `tests/golden/`. Nothing in it may be
non-deterministic or the snapshots churn.

**There is one renderer.** `urls.py` defines a single flat URL space; `serve` answers those paths
and `build` writes files at the same names. If you are tempted to add a second code path for
static output, add to `urls.py` instead.

**`serve` never writes.** Only `check --fix`, `build` and `init` write anything, and `--fix` only
touches derived content: generated regions and drifted `baseline_value`s. Never round-trip
frontmatter through pyyaml — it reorders keys and restyles quoting, producing a diff that touches
every line of a file where one number changed.

## Commands

```bash
pip install -e ".[dev]"
pytest -q
ruff check src/ tests/ docs/
```

After an intentional change, regenerate and **read the diff**:

```bash
python tests/regen_schema.py    # spec/aorf-v0.1.schema.json
python tests/regolden.py        # tests/golden/*.json
```

CI fails if either is stale, and if `aorf check --fix` on `examples/` produces any diff.

## Changing the spec

`spec/AORF-v0.1.md` is **frozen**. v0.1 is published and the scaffolding URL `/v0.1/` is
immutable, so a change to observable behaviour belongs in v0.2 with a new document and a new URL,
not in an edit here. Fixing a typo or clarifying prose that does not change what validates is
fine.

`docs/pages/spec.md` inlines the frozen spec via `{{SPEC}}` at build time, so never copy spec text
into the website by hand.

## Dependencies

Three runtime dependencies — `pyyaml`, `markdown-it-py`, `jinja2` — and that is the budget. The
server is stdlib, charts are server-generated inline SVG, and the dashboard's CSP permits no
outbound requests, so adding a CDN-delivered library is not a small decision but a change to the
security posture. Nothing in this package may execute a notebook, a script, or a generator.
