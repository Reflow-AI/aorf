# Rationale

Why the format records hypotheses and verdicts, and why its constraints are shaped the way they
are.

## What is missing from a research repository

A repository that has run experiments for a few weeks usually contains the runs and not the
reasoning. Parameters, metrics and artifacts are recorded by whatever tracker is in use. What is
generally not recorded anywhere durable is:

- what was expected before the run,
- what the result was taken to mean,
- the conditions under which that conclusion is asserted,
- which approaches were tried and set aside, and why.

That information usually existed only in conversation. Once the people involved have moved on, or
enough time has passed, it is not recoverable from the artifacts. The observable symptom is that the
question "what have we already tried here" cannot be answered from the repository, including by the
people who produced it.

## Machine-readability is why it can be maintained now

Keeping a written record of hypotheses and verdicts is not a new idea, and the standard objection is
that the bookkeeping does not survive contact with real work. That objection is well founded when a
person maintains it by hand.

What changed is that an agent reading the repository can maintain it as a side effect of doing the
work — writing the hypothesis before the run because the format requires it, and the verdict
afterwards because the checker fails without it.

The relevant test is whether a fresh session, given only the repository, can state the goal, the
open questions and the tested hypotheses without further explanation. If it cannot, the structure is
not carrying the context, and that is a property of the repository rather than of the model.

## Evidence on hypothesis-before-run

The one practice here with an empirical literature behind it is committing to a hypothesis before
collecting data.

Registered Reports, where the hypothesis and analysis plan are reviewed before data collection,
report positive results for roughly **44%** of tested hypotheses, against approximately **96%** in
the conventional literature. Preregistered studies report significant results around **48%** of the
time versus **66%** for non-preregistered ones. Nature reported this as
[a rise in null findings](https://www.nature.com/articles/d41586-018-07118-1), and
[Nature Neuroscience](https://www.nature.com/articles/s41593-024-01762-9) describes the reduction in
publication bias as the intended mechanism.

Two qualifications matter when reading those numbers:

- **The comparison is not like-for-like.** Registered Reports are disproportionately confirmatory
  hypothesis tests, which are the studies most likely to return a null result. Some of the gap is
  selection rather than bias correction. The direction of the effect is well supported; the
  magnitude should not be taken at face value.
- **The mechanism is specific.** The effect comes from fixing the claim before seeing the data. A
  hypothesis edited afterwards to match the result provides none of it. This is why the format
  treats a hypothesis as immutable once an experiment starts running, and why `aorf check` verifies
  that against git history.

## Negative results

A refuted hypothesis is a durable result: it removes an option. An unrecorded one gets retried,
usually by someone who was not there the first time.

So `verdict` accepts `refuted` and `inconclusive` on equal footing with `supported`, an abandoned
experiment requires a stated reason rather than being deleted, and an invalidated result stays in
the hypothesis ledger with its reason attached. That an approach was tried is permanent information
even when its measurement turns out not to count.

The same reasoning covers prior-art searches. `prior-art.md` records `approved_by`, `cost_usd` and
`valid_until`, and the format asks an agent to get approval before running a paid search and to read
an existing, unexpired prior-art document rather than repeating one.

## Why derived summaries are generated rather than written

The format's central constraint:

> Experiment frontmatter is the only hand-written source of truth. Every rollup is derived.

The reason is a failure mode rather than a preference. Asking anyone to update several denormalised
summaries at the end of every experiment is asking them to maintain a database by hand, and it fails
silently: a repository whose summaries have drifted is byte-for-byte identical to one that is
current, while the reading rules instruct readers to trust the summaries.

Partial compliance is therefore worse than no convention. A stale summary read confidently produces
a wrong answer; an absent one sends the reader to the experiments. This is why `aorf check` exists,
why it is the documented CI gate, and why `check --fix` regenerates derived content instead of
asking anyone to keep it in step.

There is one deliberate exception. `baseline_value` duplicates a number that already exists in the
baseline experiment, so a document can be read on its own and a delta computed without following a
link. Rule R21 checks that copy against its source on every run and `--fix` repairs it. Without that
rule the field would be the most hazardous thing in the format, since a drifted `baseline_value`
makes every delta wrong while looking rigorous.

## What the format is not

**Not an experiment tracker.** MLflow, Weights & Biases and similar tools record runs, and record
them better than a markdown file could. AORF sits above that layer and models what those tools do
not: the claim and its outcome. A `tracker` field connects the two.

**Not a mandated process.** Three documents are required; everything else appears when there is
something to put in it. A scaffold that emits nine files of placeholders makes a repository read as
populated while the reading rules return empty answers, which is worse than an obviously incomplete
one.

**Not a baseline requirement.** A baseline is recommended, because without a reference point a
sequence of experiments produces results but no measurable progress. It is not required, because a
fabricated reference makes every delta meaningless while appearing rigorous. `baseline: none` with a
stated reason is a complete answer, and the dashboard then compares against the question's
`metric_target`.
