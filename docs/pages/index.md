# Your research repo forgets what you learned. This fixes that.

After a few weeks nobody can answer "what did we already try, and what was the result" — not
your teammates, not your agent, not you. The experiments happened; the knowledge they produced
is not recoverable from what they left behind.

AORF records the scientific layer instead of the mechanical one: **the hypothesis, the verdict,
and what is still open.** It is plain markdown with YAML frontmatter, so it lives in your repo
and diffs in your PRs. A coding agent that opens the repo can state the goal, the open
questions and every hypothesis already tested without being told anything.

<div class="cta">
  <p class="cta-lede">Give your agent this URL and answer four questions:</p>
  <p class="cta-url"><code>https://reflow-ai.github.io/aorf/v0.1/aorf_scaffolding.md</code></p>
  <p class="cta-sub">Nothing to install. Or: <code>pip install aorf &amp;&amp; aorf init</code></p>
</div>

## What it looks like

This is not a mockup. It is the real `aorf build` output over
[an example repository](./demo.html), published by CI on every commit.

<div class="frame-wrap">
  <iframe src="./demo/signup-conversion/index.html" title="AORF dashboard, live example"
          loading="lazy"></iframe>
</div>

<p class="frame-caption"><a href="./demo/signup-conversion/index.html">Open the full dashboard
&rarr;</a></p>

## The one thing no other tool records

Every experiment tracker records runs, params, metrics and artifacts. None of them records a
hypothesis or a verdict.

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

From that, and nothing else, a reader gets the claim, the outcome, the conditions the outcome
holds under, and a number that means something because there is a reference to compare it to.
The [hypothesis ledger](./demo/signup-conversion/ledger.html) is every one of those in a repo on
one page — including the refuted ones, and the ones whose numbers later stopped counting.

## Three things, one repository

**The spec.** An `AGENTS.md` that travels inside each research repo and makes it
self-describing. Drop it in and an agent knows how to read and extend the repo — including how
to derive the same rollups the dashboard shows.

**The format.** [AORF v0.1](./spec.html), a profile of Google Cloud's
[Open Knowledge Format](./okf.html). Every AORF document is a valid OKF document.

**The package.** `pip install aorf` gives you `aorf check` (26 integrity rules), `aorf show
--json` (your repo's rollups as data, for an agent in a terminal), `aorf serve` (a local
dashboard) and `aorf build` (a static export you can publish).

## Why the checker matters more than the dashboard

Asking a human or an agent to update four denormalized rollups at the end of every experiment is
asking them to maintain a database by hand. It fails silently: a drifted repo is byte-identical
to a maintained one.

At 80% compliance the convention is **worse than nothing** — a confidently read stale rollup
beats you, where an absent one sends you to look at the experiments. So exactly one thing is
hand-written, experiment frontmatter, and everything else is derived and checked.

[Read the argument in full &rarr;](./why.html)
