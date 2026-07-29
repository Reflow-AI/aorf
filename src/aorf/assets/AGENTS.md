# AGENTS.md — how to read and extend this research repository

This repository follows **AORF v0.1** (Open Research Format), a profile of Google Cloud's
Open Knowledge Format. Every document is markdown with YAML frontmatter.

This file is the whole contract. You do not need any tool installed to read this repo
correctly, and you do not need to fetch the spec.

---

## 1. Which files are documents

An AORF document is:

- any file named `index.md`, `synthesis.md` or `prior-art.md`, **or**
- any `.md` file directly inside `datasets/` or `findings/`.

`artifacts/`, `src/` and `shared/` are **payload directories**. Never validate their contents
as documents; anything inside them is free-form content with any filename. `log.md`,
`README.md` and this file are not documents either.

Layout:

```
/
├── AGENTS.md          this file
├── index.md           type: research
├── log.md             optional, chronological
├── datasets/<name>.md type: dataset
├── findings/<slug>.md type: finding
├── shared/            payload: code used by more than one experiment
└── questions/<slug>/
    ├── index.md       type: question
    ├── prior-art.md   type: prior-art, optional
    ├── synthesis.md   type: synthesis, generated
    ├── experiments/<NNN-slug>/
    │   ├── index.md   type: experiment
    │   ├── runs.jsonl required when kind: sweep
    │   ├── src/       payload
    │   └── artifacts/ payload: ALL outputs go here
    └── questions/     optional nesting, same shape, 2 levels maximum
```

## 2. Link resolution

- A link starting with `/` resolves from the repository root.
- Anything else resolves relative to the containing document.
- `parent` and `question` are structural and may be relative at any depth.
- Every other link may climb **at most one** `../`. Anything deeper must be root-relative.
  Deep relative paths get written wrong by hand and broken by mechanical rewrites.

## 3. Document types and required fields

Every document, without exception, carries `type`, `title`, `description` and a status field.
The status field is `research_status` on research/question/experiment, `status` on
dataset/finding/synthesis, and `conclusion` on prior-art. A document missing any of these
cannot be displayed, so treat it as broken.

**research** (root `index.md`): `research_status` (`active|paused|concluded`), `aorf_version`.
Optional: `primary_metric`, `metric_direction`, `metric_target`, `tags`, `tag_vocabulary`.

**question**: `parent`, `research_status`
(`open|literature_review|active|answered|abandoned`). Optional: `primary_metric`,
`metric_direction`, `metric_target`, `owner`, `tracker`, `tags`. When `answered`: `answer`
and a non-empty `answer_evidence` list. When `abandoned`: `closed_reason`.

**experiment**: `question`, `kind`
(`baseline|hypothesis_test|exploration|ablation|sweep|replication`), `research_status`
(`planned|running|blocked|abandoned|done`), `baseline` (a path or the literal `none`).
- `hypothesis` when kind is `hypothesis_test`, `ablation` or `sweep`.
- `verdict` when done (`pending|supported|refuted|inconclusive`, or `n/a` for a baseline),
  plus `metrics` and `run_date`. An `exploration` owes no metrics.
- `baseline_reason` when `baseline: none`; `research_status_reason` when blocked or abandoned.
- `runs` when kind is `sweep`. `verdict_state` (`current|invalidated|superseded`) with
  `invalidated_by` + `invalidation_reason`, or `superseded_by`.
- Recommended: `verdict_scope`, `datasets`, `code`, `env`, `models` with pinned `snapshot`.

Each `metrics` entry: `name`, `value`, `direction`, `primary` (exactly one true per
experiment), and `baseline_value` when a baseline exists. Optional `unit`, `n`, `ci`, `std`.

**dataset**: `version`, `resource`, `status` (`draft|stable|deprecated`), `generated`,
`storage` (`git|git-lfs|none|external`), `generator` when generated, `defect` when deprecated.

**prior-art**: `question`, `conclusion` (`solved|partially_solved|open`), `searched_on`,
`approved_by`. Recommended `cost_usd`, `valid_until`, `sources`.

**finding**: `scope` (`repo|question`), `severity` (`info|important|blocking`), `discovered`,
`status` (`open|resolved`). Recommended `affects`.

**synthesis**: `question`, `status`. Generated; see section 5.

Dates are ISO-8601 `YYYY-MM-DD`. Preserve any field you do not recognise — never strip it.

## 4. How to read this repo

To answer "what is this about", "what is open", "what have we tried", in this order:

1. Root `index.md` — goal, scope, north-star metric.
2. Each `questions/*/index.md` — the open questions and their status.
3. Experiment frontmatter — read **frontmatter before bodies**. The frontmatter is the data;
   the body is the write-up.
4. `findings/` — an open `blocking` finding means results touching it are not trustworthy.
5. `prior-art.md` — what is already known, and what a search already cost.

Experiment frontmatter is the only hand-written source of truth. Everything else is derived.

## 5. How to derive the rollups

Compute these yourself with the rules below and you will get the same answer the dashboard
does. Getting them subtly wrong, differently each session, is worse than not answering.

- **Comparability group** = `(primary_metric, dataset_version, baseline)`. Only compare
  numbers within one group. A `kind: baseline` experiment belongs to the group it anchors.
- **Delta** is direction-aware: `value - baseline_value` for `higher_is_better`, negated for
  `lower_is_better`, so positive always means better.
- **Current best** = the largest delta among experiments that are `done`, not `kind:
  baseline`, and `verdict_state: current`. Fall back to raw value when nothing has a
  baseline.
- **Invalidated and superseded results are excluded from any current-best or headline number,
  but stay in the hypothesis ledger with their reason.** That a thing was tried is permanent
  knowledge even when the number is not.
- **Reference line** = the baseline's value when one exists, otherwise the question's
  `metric_target`.
- **Sweep**: the headline number is `best_run`'s value for the primary metric. Report the
  spread too — "supported in 31 of 40 configurations" is a different claim from "supported".
- **Generated regions** live between `<!-- AORF:BEGIN generated -->` and
  `<!-- AORF:END generated -->` in `synthesis.md`. Text outside the markers is hand-written:
  never touch it.

## 6. How to extend this repo

- **A hypothesis is written before the run and never edited afterwards.** If the result
  suggests a different claim, that is a new experiment with `retests` pointing at the old one.
  A hypothesis rewritten to match its result is not a hypothesis.
- **Record the verdict**, including `refuted` and `inconclusive`. A negative result recorded
  once is the thing that stops it being paid for twice.
- **All outputs go in `artifacts/`.** This is what makes document discovery decidable, not a
  style preference.
- **Minimal mode: create nothing before it is earned.** Day one is three documents — root
  `index.md`, one question, one experiment. `synthesis.md` appears at three experiments,
  `prior-art.md` when a search is run, `datasets/` when data is referenced, `findings/` when
  something is discovered, nesting when a question genuinely splits. A scaffold full of "TBD"
  is worse than an absent one, because the reading rules then return confidently empty
  answers.
- **A dataset referenced by any completed experiment is immutable.** Fix it by creating a new
  version with `supersedes`; never edit the old one. Re-run the baseline per dataset version.
- **If data can be regenerated, it does not go in the repo**: `generated: true`,
  `storage: none`, a gitignore entry, and the exact command in `# Provenance`. Source data
  that cannot be regenerated is committed via git LFS.
- **Tags**, if used at all, must come from the root `tag_vocabulary`. Adding one is a
  deliberate one-line edit, not a typo.

## 7. Baselines: propose, do not impose

A baseline is what makes iteration mean something — without a number to beat, a sequence of
experiments produces results but no measurable progress.

So: **when a question has no baseline and one is applicable, propose one.** Say what it would
be and why it is cheap — the most brute-force approach on the smallest usable data. Do not
create it unprompted, and do not block on it. If the user declines or none applies, write
`baseline: none` with their reason in `baseline_reason` and move on without raising it again
for that question. A fabricated baseline is worse than a declared absence: an invented
reference number makes every delta in the repo meaningless while looking rigorous.

## 8. Cost gate

**Before running any external or literature search that costs money, state the intended scope
and the expected cost, and get explicit approval from the user. Never run a broad
multi-source search unprompted. If a `prior-art.md` exists for this question and its
`valid_until` has not passed, read it instead of searching again.**

---

**Not yet set up?** If this repository has no root `index.md`, fetch the scaffolding
instructions at <https://reflow-ai.github.io/aorf/v0.1/aorf_scaffolding.md> and follow them.

**Optional tooling.** `pip install aorf` gives you `aorf check` (validates everything above),
`aorf show --json` (this repo's rollups as data) and `aorf serve` (a local dashboard). The
format works without it; the checker exists because a repo that quietly drifts is worse than
one that is obviously incomplete.
