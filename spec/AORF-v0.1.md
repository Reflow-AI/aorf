# AORF v0.1 — Open Research Format

**Status:** frozen. **Version:** 0.1. **Licence:** CC BY 4.0 (see `spec/LICENSE`).

AORF is a convention for research repositories that makes the *scientific* layer
machine-readable: not what you ran, but what you believed, whether it held, and what is still
open.

> Every experiment tracker records runs, params, metrics and artifacts. None of them records a
> hypothesis or a verdict. AORF records those, in plain markdown, so both your teammates and
> your coding agent can answer "what have we already tried, and what happened" without asking
> you.

Every document is markdown with YAML frontmatter. `type` is required on every document.
**Unknown fields must be preserved, never stripped.**

## Relation to OKF

AORF is a **profile of** Google Cloud's
[Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md),
not a rival. OKF says how to write agent-readable knowledge; AORF says what a research repo's
knowledge is made of. Concretely:

- Every AORF document is a valid OKF document: `type` required, `title` and `description` used
  as OKF intends.
- Where OKF already names a thing, AORF reuses the name. No synonyms are invented.
- `status` keeps OKF's document-lifecycle meaning (`draft|stable|deprecated`). Research state
  lives in a separate field, **`research_status`**. This split is deliberate and must not be
  merged.
- Cross-document links are markdown links with root-relative paths, as in OKF's own examples.
- AORF hardens several OKF *recommended* fields into required; see the display contract below.

**One departure, stated openly:** OKF publishes its spec externally and expects consumers to
know it. AORF ships its spec *inside* each repository as `AGENTS.md`, because the consumer is a
coding agent that reads that file automatically.

## The one design rule everything follows

**Experiment frontmatter is the only hand-written source of truth. Every rollup is derived.**

Asking a human or an agent to update four denormalized places at the end of every experiment is
asking them to maintain a database by hand. It fails silently: a drifted repo is byte-identical
to a maintained one, while the reading rules tell readers to trust the rollups. At 80%
compliance the convention is *worse than nothing*, because a confidently read stale rollup
beats you, where an absent one sends you to look at the experiments.

There is exactly one deliberate exception, `baseline_value`, and rule R21 exists to make it
safe. See §6.

---

## 1. The display contract

A renderer must be able to present **any** AORF document without special-casing its type and
without reading its body. So these are required on every document, no exceptions, and the
checker treats a missing one as an **error**, never a warning:

| Field | Why the renderer needs it |
|---|---|
| `type` | picks the view and the icon |
| `title` | the heading, and every link label pointing at this document |
| `description` | the one-line summary in tables, cards, tooltips and search results |
| a status field | the status chip. **Every document carries one.** `research_status` on research, question and experiment; `status` on dataset, finding and synthesis; `conclusion` on prior-art |

Deliberately **not** required everywhere:

- **`resource`** is required only where an underlying asset exists, which in practice means
  `dataset`. A question and an experiment have no external asset, and forcing the field would
  produce invented values — the "stub full of TBD" failure mode, where the repo reads as
  populated while the reading rules return confidently empty answers. For an experiment that
  does point outward, `tracker` already covers it.
- **`timestamp`** stays optional because git can recover it. `run_date` is required on
  completed experiments precisely because git cannot.

### Tag vocabulary

`tags` stays optional: requiring it on every experiment is real authoring friction, and an
experiment already inherits its question's topic for filtering. But free-text tags fill a
filter with near-duplicates (`clustering`, `cluster`, `clusters`), which is worse than no
filter. So the rule is conditional — **if a repo uses tags at all, the root `index.md` declares
the closed set, and every tag must come from it:**

```yaml
tag_vocabulary: [funnel, growth, clustering, embeddings, sop, drift, entities]
```

Lowercase kebab-case, declared once at the root, validated by the checker (R19, R20). Adding a
tag becomes a deliberate one-line decision rather than a typo.

---

## 2. Repository layout

```
/
├── AGENTS.md                    # the spec itself, self-describing
├── index.md                     # type: research
├── log.md                       # optional, chronological, free-form payload
├── .gitignore                   # ships with the scaffold; ignores derived data
├── .gitattributes               # ships with the scaffold; git LFS for large source data
├── datasets/
│   └── <name>.md                # type: dataset
├── findings/
│   └── <slug>.md                # type: finding
├── shared/                      # payload: code used by more than one experiment
└── questions/
    └── <slug>/
        ├── index.md             # type: question
        ├── prior-art.md         # type: prior-art, optional
        ├── synthesis.md         # type: synthesis, generated
        ├── experiments/
        │   └── <NNN-slug>/
        │       ├── index.md     # type: experiment
        │       ├── runs.jsonl   # required when kind: sweep
        │       ├── src/         # payload
        │       └── artifacts/   # payload: ALL outputs go here
        └── questions/           # optional nesting, same shape
```

## 3. Document discovery (normative)

An AORF document is:

- any file named `index.md`, `synthesis.md` or `prior-art.md`, **or**
- any `.md` file directly inside `datasets/` or `findings/`.

Reserved payload directories, **never** scanned as documents: `artifacts/`, `src/`, `shared/`.
Everything inside them is content: free-form, any filename. `AGENTS.md`, `README.md` and
`log.md` are not documents.

This is why "all outputs go in `artifacts/`" is a spec rule and not a style preference: it is
what makes document discovery decidable. Without it, an artifact write-up like `power.md` gets
validated as an AORF document and fails.

## 4. Link resolution (normative)

- A link beginning with `/` resolves from the repository root.
- Any other link resolves relative to the containing document.
- **Structural links** (`parent`, `question`) may be relative at any depth. They are fixed and
  unambiguous.
- **Every other link** may be relative with **at most one `..`**. Anything that needs to climb
  further must be root-relative. (R25)

The one-hop limit is empirical, not aesthetic. At depth 2 a cross-tree relative path reached
142 characters containing `questions/` twice; two of three such paths written by hand were
wrong, and a third was then broken by a mechanical rewrite. One `..` covers the sibling case
(`../000-baseline/index.md`), which is short and self-evidently correct. Beyond that a leading
`/` is both shorter and checkable.

Dates everywhere are ISO-8601 `YYYY-MM-DD`. An unquoted YAML date is accepted and normalized to
that form. (R24)

---

## 5. Document types

### 5.1 `type: research` (root `index.md`)

| Field | Req | Notes |
|---|---|---|
| `type` | yes | `research` |
| `title` | yes | |
| `description` | yes | one sentence |
| `research_status` | yes | `active` \| `paused` \| `concluded` |
| `aorf_version` | yes | `"0.1"` |
| `primary_metric` | no | north-star metric name, for the dashboard headline |
| `metric_direction` | no | `higher_is_better` \| `lower_is_better` |
| `metric_target` | no | number |
| `tags` | no | values must come from `tag_vocabulary` |
| `tag_vocabulary` | when tags are used anywhere | the closed tag set, declared once here |
| `timestamp` | no | derivable from git |

Body: `# Problem statement`, `# Goal and success criteria`, `# Scope and non-goals`,
`# Questions`, `# Datasets`, `# Findings`.

### 5.2 `type: question`

| Field | Req | Notes |
|---|---|---|
| `type` | yes | `question` |
| `title` | yes | phrased as a question |
| `description` | yes | one sentence |
| `parent` | yes | path to the parent `index.md` |
| `research_status` | yes | `open` \| `literature_review` \| `active` \| `answered` \| `abandoned` |
| `primary_metric` | no | the comparability contract for this question |
| `metric_direction` | no | |
| `metric_target` | no | |
| `answer` | when `answered` | one sentence |
| `answer_evidence` | when `answered` | list of experiment paths, non-empty |
| `closed_reason` | when `abandoned` | |
| `closed` | no | date |
| `owner` | no | |
| `tracker` | no | e.g. `LIN-482`. One issue per question, not per experiment |
| `tags` | no | from the root `tag_vocabulary` |
| `timestamp` | no | |

Body: `# Question`, `# Why this matters`, `# Current best result`, `# Prior art`,
`# Experiments`, `# Sub-questions`.

### 5.3 `type: experiment`

| Field | Req | Notes |
|---|---|---|
| `type` | yes | `experiment` |
| `title` | yes | |
| `description` | yes | one sentence |
| `question` | yes | owning question |
| `kind` | yes | `baseline` \| `hypothesis_test` \| `exploration` \| `ablation` \| `sweep` \| `replication` |
| `research_status` | yes | `planned` \| `running` \| `blocked` \| `abandoned` \| `done` |
| `research_status_reason` | when `blocked`/`abandoned` | |
| `hypothesis` | when kind is `hypothesis_test`/`ablation`/`sweep` | one falsifiable sentence with an expected measurable effect |
| `verdict` | when `done` | `pending` \| `supported` \| `refuted` \| `inconclusive` \| `n/a`. **`n/a` is valid only when `kind: baseline`** |
| `verdict_scope` | recommended | conditions under which the verdict holds |
| `verdict_state` | no | `current` (default) \| `invalidated` \| `superseded` |
| `invalidated_by` | when `invalidated` | path to a finding |
| `invalidation_reason` | when `invalidated` | |
| `superseded_by` | when `superseded` | |
| `supersedes` | no | |
| `retests` / `retest_reason` | no | required together |
| `also_informs` | no | other questions this result bears on |
| `baseline` | yes | a path, or the literal `none`. **The field is required; a baseline is not** |
| `baseline_reason` | when `none` | |
| `datasets` | recommended | list of `{path, role}`, role in `eval`/`train`/`reference` |
| `metrics` | when `done`, except `kind: exploration` | see below |
| `run_date` | when `done` | when it ran, distinct from `timestamp` |
| `runs` | when `kind: sweep` | path to `runs.jsonl` |
| `run_count`, `best_run`, `verdict_basis` | recommended for sweeps | |
| `owner`, `cost_usd`, `runtime_s` | no | |
| `code` | recommended | `{commit, entrypoint, shared_ref, dirty}` |
| `env` | recommended | `{lockfile, python}` |
| `models` | when a model is used | list of `{provider, id, snapshot, params}`. `snapshot` must be pinned, never a floating alias |
| `nondeterministic`, `repeats` | no | |
| `tags`, `tracker`, `timestamp` | no | |

`metrics` entry:

```yaml
metrics:
  - name: ari                      # required, must equal the question's primary_metric
    value: 0.71                    # required, numeric
    direction: higher_is_better    # required, must match the question's metric_direction
    baseline_value: 0.58           # required unless kind: baseline or baseline: none
    primary: true                  # exactly one metric must be primary
    unit: ratio                    # optional
    n: 50                          # optional
    ci: [0.68, 0.74]               # optional
    std: 0.04                      # optional, required if nondeterministic
```

Body: `# Hypothesis` (or `# Goal` for explorations), `# Method`, `# Results`, `# Conclusion`,
`# Next`.

`runs.jsonl`: one JSON object per line, required keys `run_id`, `params`, `metrics`; optional
`artifacts`, `run_date`, `status`, `repeats`.

### 5.4 `type: dataset`

| Field | Req | Notes |
|---|---|---|
| `type`, `title`, `description` | yes | |
| `version` | yes | |
| `resource` | yes | path or URL to the data. Not existence-checked: it may be gitignored, an unfetched LFS pointer, or a URL |
| `status` | yes | OKF lifecycle: `draft` \| `stable` \| `deprecated` |
| `generated` | yes | `true` if derived from another dataset |
| `generator` | when `generated: true` | path to the script that produces it |
| `storage` | yes | `git` \| `git-lfs` \| `none` \| `external` |
| `checksum` | recommended | `sha256:...` |
| `row_count`, `created` | no | |
| `supersedes` / `superseded_by` | no | |
| `defect` | when `deprecated` | why it was withdrawn |

Body: `# Provenance`, `# Format`, `# Changelog`, `# Known issues`.

**Data rules (normative):**

- **If it can be regenerated, it does not go in the repo.** `generated: true` implies
  `storage: none` and a gitignore entry. The `generator` field plus the exact command in
  `# Provenance` is the record.
- **Self-containment first.** Source data that cannot be regenerated is committed via **git
  LFS** (`storage: git-lfs`) so the repo has no external dependency. `storage: external` is
  discouraged and needs a stated reason in `# Provenance`.
- **A dataset referenced by any `done` experiment is immutable.** A fix creates a new versioned
  document with `supersedes`; it never mutates the old one.
- **Baselines are re-run per dataset version.**

### 5.5 `type: prior-art`

| Field | Req | Notes |
|---|---|---|
| `type`, `title`, `description` | yes | |
| `question` | yes | |
| `conclusion` | yes | `solved` \| `partially_solved` \| `open` |
| `searched_on` | yes | date |
| `approved_by` | yes | who authorised the spend |
| `cost_usd` | recommended | be honest |
| `valid_until` | recommended | do not re-run before this date |
| `sources` | recommended | |

Body: `# What is already known`, `# What is not settled for us`, `# Conclusion`, `# Cost note`,
`# Sources`.

**Cost gate (normative):**

> Before running any external or literature search that costs money, state the intended scope
> and expected cost and get explicit approval from the user. Never run a broad multi-source
> search unprompted. If a `prior-art.md` exists for this question and its `valid_until` has not
> passed, read it instead of searching again.

### 5.6 `type: finding`

For something learned that is not an experiment result: a data defect, a silently changed
model, an incidental discovery.

| Field | Req | Notes |
|---|---|---|
| `type`, `title`, `description` | yes | |
| `scope` | yes | `repo` \| `question` |
| `severity` | yes | `info` \| `important` \| `blocking` |
| `affects` | recommended | list of document paths |
| `discovered` | yes | date |
| `source` | no | how it surfaced |
| `status` | yes | `open` \| `resolved` |

### 5.7 `type: synthesis` (generated)

Per-question comparison. `type`, `title`, `description`, `question` and `status` required.
`status` uses OKF lifecycle values and is written by the generator: `stable` once the question
has three or more experiments, `draft` before that. A derived document is still a document, so
it carries a status chip like any other.

Generated content sits between `<!-- AORF:BEGIN generated -->` and
`<!-- AORF:END generated -->`. **Hand-written narrative lives outside the markers and is
preserved.** Rows are partitioned by comparability group
`(primary_metric, dataset_version, baseline)`; numbers from different groups never share a
column. A `kind: baseline` experiment belongs to the group it anchors.

---

## 6. Derivation rules (normative)

Any consumer — a dashboard, or an agent reading frontmatter directly — must compute these the
same way, or two readers of the same repo get different answers.

- **Comparability group** = `(primary_metric, dataset_version, baseline)`. Compare only within
  a group.
- **Delta** is direction-aware: `value - baseline_value` for `higher_is_better`, negated for
  `lower_is_better`, so positive always means better.
- **Current best** = the largest delta among experiments that are `done`, not `kind: baseline`,
  and `verdict_state: current`. Fall back to raw value when nothing carries a baseline.
- **Invalidated and superseded results never inform a current-best or headline number, but stay
  in the hypothesis ledger with their reason.** That a thing was tried is permanent knowledge
  even when the number is not.
- **Reference line** = the baseline's value where one exists, otherwise the question's
  `metric_target`.
- **Sweep**: the headline is `best_run`'s value for the primary metric; report the spread too.
- A **sub-question's baseline inherits the parent's current best**: its `000-baseline` re-runs
  the parent's winning configuration unchanged, which keeps metrics comparable up the tree.

### `baseline_value`, the one deliberate denormalization

`baseline_value` duplicates a number that already lives in the baseline experiment. This
contradicts the design rule in the introduction, and it is kept anyway for one reason: it lets
a document be read on its own, and lets an agent compute a delta without following a link.

That trade is only safe because **R21 checks the copy against its source** and `aorf check
--fix` repairs it. Without R21 this field would be the single most dangerous thing in the
format: a drifted `baseline_value` makes every delta in the repo wrong while looking rigorous.

---

## 7. Integrity rules

`aorf check` enforces all of these. R01–R20 are the frozen v0.1 set; R21–R26 close gaps that
set left open.

| # | Rule | Level |
|---|---|---|
| R01 | The display contract (§1) holds on every document: `type`, `title`, `description` and a status field present and non-empty. Includes `status` on dataset and synthesis | error |
| R02 | Enum values valid, including nested `metrics[].direction` and `datasets[].role`. `verdict: n/a` only on `kind: baseline` | error |
| R03 | Every link field resolves: document links to a document, file links to a file | error |
| R04 | `done` implies a verdict that is not `pending`, at least one metric (except `exploration`), and a `run_date` | error |
| R05 | Exactly one `primary: true` metric | error (warning when a lone metric is unmarked) |
| R06 | `baseline: none` requires `baseline_reason` | error |
| R07 | `hypothesis_test`/`ablation`/`sweep` require a `hypothesis`; a `baseline` carrying one warns | error / warning |
| R08 | `kind: sweep` requires a `runs` file | error |
| R09 | `invalidated` requires `invalidated_by` and `invalidation_reason`; `superseded` requires `superseded_by` | error |
| R10 | `answered` requires `answer` and a non-empty `answer_evidence` | error |
| R11 | `abandoned`/`blocked` require a reason field | error |
| R12 | An experiment must not compare against a baseline that used a different dataset version. Skipped when `verdict_state: invalidated` | error |
| R13 | `generated: true` requires `generator`, and warns unless `storage: none` | error / warning |
| R14 | `generated: false` warns unless `storage` is `git` or `git-lfs` | warning |
| R15 | `running` with a timestamp older than 30 days | warning |
| R16 | Generated regions match what the generator would write now | warning, error under `--strict` |
| R17 | Question nesting depth 3 warns; depth 4 errors under `--strict`. Root is depth 0, `questions/<slug>/` is 1 | warning / error |
| R18 | `hypothesis` must not change once `research_status` has left `planned`. Checked against git history; skipped with a note where git cannot answer | error |
| R19 | Every `tags` value appears in the root `tag_vocabulary`. Repos using no tags skip this entirely | error |
| R20 | `tag_vocabulary` entries are lowercase kebab-case and unique | error |
| R21 | A metric's `baseline_value` equals the referenced baseline's same-named metric. Skipped when `invalidated`; warns when the baseline never measured that metric | error / warning |
| R22 | An experiment's primary metric `name` equals the question's `primary_metric`, and its `direction` matches `metric_direction` | error |
| R23 | `aorf_version`: unknown minor warns and proceeds, unknown major errors | error / warning |
| R24 | Dates are ISO-8601 `YYYY-MM-DD` | error |
| R25 | A relative link outside `parent`/`question` may climb at most one level; deeper must be root-relative | error |
| R26 | A question with three or more experiments has earned a `synthesis.md` | warning |

The published [JSON Schema](./aorf-v0.1.schema.json) expresses types, enums and
unconditionally required fields **only**. Conditional requirements and every cross-document
rule are enforced by `aorf check`, because no JSON Schema can check that a `baseline_value`
matches the document it refers to.

---

## 8. Minimal mode (normative)

**Day one requires exactly three documents:** root `index.md`, one
`questions/<slug>/index.md`, one experiment `index.md`.

Everything else appears when earned: `synthesis.md` at three or more experiments,
`prior-art.md` when a search is run, `datasets/` when data is referenced, `findings/` when
something is discovered, nesting when a question genuinely splits.

A scaffold that emits nine files of "TBD" is worse than an absent one, because the reading
rules then return confidently empty answers.

## 9. Baseline policy (normative)

A baseline is **strongly recommended, not required.** Its purpose is to give the iterations
after it a meaning: without a number to beat, a sequence of experiments produces results but no
measurable progress. When one exists it should be the most brute-force approach on the smallest
usable data, so it is cheap and fast to produce.

The `baseline` field is required on every experiment; what is optional is the baseline.
`baseline: none` plus a `baseline_reason` is a first-class answer, and the dashboard then
compares against the question's `metric_target`.

**Forcing a fabricated baseline is worse than declaring its absence** — an invented reference
number makes every delta in the repo meaningless while looking rigorous.

An agent's job here: when a question has no baseline and one is applicable, **propose** one and
say what it would be and why it is cheap. Do not create it unprompted and do not block on it.
If the user declines or none applies, write `baseline: none` with their reason and move on
without raising it again for that question.

## 10. The `AGENTS.md` contract

`AGENTS.md` travels inside each repository and is the only part of AORF guaranteed to be
present. It must contain: document discovery (§3) and link resolution (§4) verbatim; the
document types and their required fields; the reading rules; the derivation rules (§6); the
writing rules including hypothesis-before-run and minimal mode; the baseline behaviour (§9);
the cost gate (§5.5); and a pointer to the scaffolding document for a repo that is not yet set
up. Scaffolding instructions themselves stay out of it — they must not occupy context in every
later session.

The reference template ships with the `aorf` package and is written by `aorf init`.
