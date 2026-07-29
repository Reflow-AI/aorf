# AORF v0.1 scaffolding instructions

**This document is versioned and immutable. `/v0.1/` never changes once published; new versions
get new URLs.** Whatever is live is what runs, so it has to be stable.

You are an agent that has been handed this URL. Your job is to turn the user's repository into
an AORF research repository, then get out of the way.

---

## Step 0 — Check whether this is needed

If the repository already has a root `index.md` with `type: research`, it is already set up.
**Stop, read its `AGENTS.md`, and continue with the user's actual request instead.** Do not
re-scaffold.

## Step 1 — Interview the user first, briefly

Ask these, in one message, and wait. Do not invent answers, and do not create any file yet.

1. **What are you trying to find out?** One or two sentences. This becomes the root
   `index.md`'s problem statement.
2. **What would "done" look like?** If they can name a metric and a target, capture them; if
   they cannot, that is fine and those fields stay out.
3. **What is the first question you need to answer?** This becomes the first
   `questions/<slug>/index.md`.
4. **What data do you have?** If they name a dataset, note whether it is raw source data or
   something derived from it — that determines its `storage` later. If there is no data yet,
   skip `datasets/` entirely.

If the user has already told you all of this in the conversation, do not ask again. Confirm
what you understood in one line and proceed.

## Step 2 — Write exactly three documents

Minimal mode is normative. **Day one is three documents and nothing else:**

```
index.md                                        type: research
questions/<slug>/index.md                       type: question
questions/<slug>/experiments/001-<slug>/index.md  type: experiment
```

Plus `AGENTS.md`, `.gitignore` and `.gitattributes` (Step 4).

Do **not** create `datasets/`, `findings/`, `synthesis.md`, `prior-art.md`, or nested
`questions/` now. They appear when earned: `synthesis.md` at three experiments, `prior-art.md`
when a search is actually run, `datasets/` when an experiment points at data, `findings/` when
something is discovered.

**A scaffold that emits nine files of "TBD" is worse than an absent one**, because the reading
rules then return confidently empty answers about a repo that looks populated.

Every document is markdown with YAML frontmatter. Every document carries `type`, `title`,
`description` and a status field — no exceptions, because a renderer must be able to show a
chip for anything it is handed.

### `index.md`

```yaml
---
type: research
title: <the user's research, named>
description: <one sentence: the problem this research exists to solve>
research_status: active
aorf_version: "0.1"
# Only if the user named one. Do not invent a metric.
primary_metric: <name>
metric_direction: higher_is_better   # or lower_is_better
metric_target: <number>
---
```

Body sections: `# Problem statement`, `# Goal and success criteria`, `# Scope and non-goals`,
`# Questions`, `# Datasets`, `# Findings`. Write the user's own words into the first two. Under
`# Questions`, link the question you are about to create. Under `# Datasets` and `# Findings`,
write one honest line saying nothing is recorded yet — not a placeholder table.

### `questions/<slug>/index.md`

```yaml
---
type: question
title: <phrased as an actual question, ending in ?>
description: <one sentence: what answering this would tell them>
parent: ../../index.md
research_status: open
primary_metric: <name>          # the comparability contract for this question
metric_direction: higher_is_better
metric_target: <number>
---
```

Body: `# Question`, `# Why this matters`, `# Current best result`, `# Prior art`,
`# Experiments`, `# Sub-questions`.

`# Why this matters` should say what decision changes depending on the answer. If nothing
changes, say so — it is a sign this is not a question worth running experiments on, and the
user should know that now rather than after three experiments.

### `questions/<slug>/experiments/001-<slug>/index.md`

Create the directory `artifacts/` alongside it, empty. All outputs go there; this is what makes
document discovery decidable, not a style preference.

```yaml
---
type: experiment
title: <what this experiment does>
description: <one sentence>
question: ../../index.md
kind: hypothesis_test          # or baseline, exploration, ablation, sweep, replication
research_status: planned
hypothesis: "<one falsifiable sentence with an expected measurable effect>"
baseline: none
baseline_reason: "<why there is no baseline yet>"
---
```

Body: `# Hypothesis`, `# Method`, `# Results`, `# Conclusion`, `# Next`. Leave `# Results` and
`# Conclusion` explicitly empty with a line saying they are filled in after the run.

**The hypothesis is written before the run and never edited afterwards.** If the result later
suggests a different claim, that is a *new* experiment with `retests` pointing at this one. A
hypothesis rewritten to match its result is not a hypothesis, and `aorf check` will catch it
against git history.

## Step 3 — Raise the baseline question, once

A baseline is what makes iteration mean something: without a number to beat, a sequence of
experiments produces results but no measurable progress.

So after writing the three documents, **tell the user what a baseline for this question would
be** — the most brute-force approach on the smallest usable data — and why it would be cheap.
Then let it go. Do not create it unprompted and do not block on it. If they decline or none
applies, `baseline: none` with their reason is a completely valid, permanent answer.

**Never fabricate a baseline number.** An invented reference makes every delta in the repo
meaningless while looking rigorous.

## Step 4 — Write `AGENTS.md`, `.gitignore`, `.gitattributes`

`AGENTS.md` is the contract that makes the repo self-describing, and the only part of AORF
guaranteed to be present in later sessions. Write it to cover, in this order:

1. **Document discovery**: `index.md`, `synthesis.md`, `prior-art.md` anywhere, plus any `.md`
   directly in `datasets/` or `findings/`. `artifacts/`, `src/` and `shared/` are payload
   directories and are never validated as documents.
2. **Link resolution**: a leading `/` is repo-root-relative; `parent` and `question` may be
   relative at any depth; every other link may climb at most one `..`, and anything deeper must
   be root-relative.
3. **The document types and their required fields**, compactly enough to write a valid document
   without fetching the spec.
4. **Reading rules**: root `index.md`, then questions, then experiment frontmatter. Frontmatter
   before bodies.
5. **Derivation rules**, so a later agent computes the same rollups a dashboard would:
   comparability group `(primary_metric, dataset_version, baseline)`; direction-aware deltas;
   invalidated results excluded from current-best but kept in the hypothesis ledger; sweep
   headline from `best_run`.
6. **Writing rules**: hypothesis before the run and frozen after; experiment frontmatter is the
   only hand-written source of truth; all outputs in `artifacts/`; minimal mode.
7. **The baseline behaviour** from Step 3: propose, do not impose.
8. **The cost gate** below, verbatim in spirit.

Do **not** copy these scaffolding instructions into `AGENTS.md`. They are needed once; they must
not occupy context in every later session. Point at this URL for the not-yet-set-up case and
stop there.

The canonical template is at
<https://github.com/Reflow-AI/aorf/blob/main/src/aorf/assets/AGENTS.md> — copy it and adjust
nothing but the repository's own name.

`.gitignore` must ignore derived data (`**/derived/`) plus the usual Python and environment
noise. `.gitattributes` should route large source data (`*.csv`, `*.jsonl`, `*.parquet`) through
git LFS, but keep `**/runs.jsonl` out of LFS so sweep records stay readable in a diff.

## Step 5 — Verify and hand back

Tell the user, in three lines:

- what you created,
- that `pip install aorf && aorf check` validates it and `aorf serve` gives them a local
  dashboard,
- what the next single step is (usually: fill in `# Method`, run it, then record the verdict).

If `aorf` happens to be installed, run `aorf check` and fix anything it reports before handing
back.

---

## The cost gate (normative)

> **Before running any external or literature search that costs money, state the intended scope
> and the expected cost and get explicit approval from the user. Never run a broad multi-source
> search unprompted. If a `prior-art.md` exists for this question and its `valid_until` has not
> passed, read it instead of searching again.**

## Why any of this

Record the verdict, including `refuted` and `inconclusive`. A negative result recorded once is
the thing that stops it being paid for twice — and it is the part every experiment tracker
throws away.

Full specification: <https://reflow-ai.github.io/aorf/spec.html>.
An equivalent alternative to all of the above: `pip install aorf && aorf init`.
