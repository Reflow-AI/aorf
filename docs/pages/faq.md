# FAQ

## Does this replace MLflow or Weights & Biases?

No, and it does not overlap with them much. They record **runs**: params, metrics, artifacts,
system stats. AORF records the layer above: **the hypothesis and the verdict.** Neither of those
exists in any experiment tracker's data model.

They sit together. Put your run URL or ID in the experiment's `tracker` field, keep using the
tracker for what it is good at, and let AORF hold the claim and its outcome. MLflow's artifact
viewer is in fact the reference implementation for AORF's artifact dispatch — including the
sandboxed-iframe treatment of user HTML.

## Do I need the package?

No. The format is plain markdown and the reading and derivation rules are in the `AGENTS.md` that
sits in the repo, so an agent can parse the frontmatter and compute the same overview a dashboard
would, with nothing installed.

What the package adds: `aorf check`, which is genuinely load-bearing. Not because parsing is hard
but because *deriving* is easy to get subtly wrong — comparability grouping, direction-aware
deltas, keeping invalidated results out of the headline but in the ledger. An agent doing that ad
hoc gets it right most of the time, differently each session. At 80% right a rollup is worse than
no rollup.

`aorf show --json` is the convenience version of the same thing: the projection as data, for when
a browser dashboard is useless because you are an agent in a terminal.

## What about my issue tracker?

They own different things and connect with one field.

Linear or Jira owns **scheduling and priority**: what is being worked on, by whom, this sprint.
AORF owns **hypotheses and evidence**: what was claimed, what happened, what that rules out. One
`tracker` field on a question links them — one issue per question, not per experiment, because an
issue per experiment turns your tracker into a lab notebook and it is bad at that.

## Why not just use a `RESULTS.md` file?

Because it drifts, and you cannot tell that it has. A stale hand-maintained summary is
byte-identical to a current one, and the reading rules tell readers to trust it. That is the
failure this format is shaped around: exactly one thing is hand-written — experiment frontmatter
— and everything derived from it is regenerable and checkable.

## Is a baseline required?

No. It is strongly recommended, because without a number to beat a sequence of experiments
produces results but no measurable progress. But the `baseline` field being required is not the
same as a baseline being required: `baseline: none` with a `baseline_reason` is a permanent,
first-class answer, and the dashboard then compares against the question's `metric_target`
instead.

Forcing a fabricated baseline would be worse than declaring its absence, because an invented
reference number makes every delta in the repo meaningless while looking rigorous.

## Why is `baseline_value` duplicated on every metric?

It is the one deliberate denormalization in the format, and it contradicts the design rule that
everything except experiment frontmatter is derived. It is kept because it lets a document be read
on its own, and lets an agent compute a delta without following a link.

That is only safe because rule **R21** checks the copy against its source and `aorf check --fix`
repairs it. Without R21 it would be the most dangerous field in the format: a drifted
`baseline_value` makes every delta wrong while looking rigorous.

## What happens when a dataset turns out to be broken?

You write a `findings/` document, mark the affected experiments `verdict_state: invalidated`
pointing at it, and create a **new** dataset version with `supersedes`. You never edit the old
dataset document — a dataset referenced by a completed experiment is immutable, because the
results are attached to the data they were computed on.

The invalidated results stay in the hypothesis ledger, struck through, with the reason. They stop
informing any current-best number. Both examples on the [demo page](./demo.html) show this.

## Can I nest questions arbitrarily deep?

You can nest two levels comfortably. Depth 3 warns and depth 4 fails under `--strict`, because
cross-tree paths stop being writable by hand well before that. A sub-question's baseline inherits
its parent's current best — its `000-baseline` re-runs the parent's winning configuration
unchanged — which keeps metrics comparable up the tree.

## Is `aorf serve` safe to run?

It is read-only and binds `127.0.0.1` by default. Every requested path is resolved and confirmed
to be inside the repository, symlinks that escape are refused, only `artifacts/` is servable, and
nothing is ever executed — no notebooks, no scripts, no generators. Author HTML and SVG go in
sandboxed iframes with no same-origin access, markdown is rendered with raw HTML disabled, and the
page carries a CSP that permits no outbound requests at all. There is no telemetry and no network
access at runtime.

Binding a non-loopback host requires an explicit flag and prints a warning.

## What does "Agentic" in the name mean?

The acronym stands, and the gloss is just **Open Research Format** — "agent-first" belongs in a
tagline, not a name. Anything called agentic in 2026 will read as dated in 2028, while the format
should still be readable.

## What is not in v0.1?

**Stable IDs.** Cross-references are paths, which means renaming a question directory breaks
links pointing into it. The one-hop link rule keeps paths short enough that this is tolerable, and
an `id` field is the obvious v0.2 addition.

**Anything that executes.** No runners, no notebook execution, no generator invocation. The tool
reads and renders; running your experiments is your business.
