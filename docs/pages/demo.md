# Live example

**These are not mockups.** Each one is the actual output of `aorf build` over an example
repository in the [GitHub repo](https://github.com/Reflow-AI/aorf/tree/main/examples), rebuilt by
CI on every commit. If the tool broke, this page would break with it.

## Trial-to-paid conversion — start here

A non-technical domain, understandable without background: where trial users drop off before
paying. One question, a baseline and three experiments covering all three verdicts, and four
artifact types.

<div class="cards">
  <a class="card" href="./demo/signup-conversion/index.html">
    <strong>Overview</strong>
    <span>The whole effort on one screen: every question, its status, hypotheses tested, and best
    delta against baseline.</span>
  </a>
  <a class="card" href="./demo/signup-conversion/ledger.html">
    <strong>Hypothesis ledger</strong>
    <span>Every hypothesis in the repo on one page, with what happened to it. No other tool can
    show this.</span>
  </a>
  <a class="card" href="./demo/signup-conversion/experiment-onboarding-friction--000-baseline.html">
    <strong>Artifact variety</strong>
    <span>A PNG chart, a sortable CSV, an SVG and a sandboxed HTML report, dispatched by
    type.</span>
  </a>
  <a class="card" href="./demo/signup-conversion/question-onboarding-friction.html">
    <strong>A question</strong>
    <span>Current best, prior-art conclusion, and the experiments partitioned by comparability
    group.</span>
  </a>
</div>

## Workflow mining — what it looks like at scale

Nineteen documents, two levels of nesting, a 40-configuration sweep, a dataset superseded after a
defect was found, and a result that was invalidated because of it.

<div class="cards">
  <a class="card" href="./demo/workflow-mining/index.html">
    <strong>Overview with a blocking finding</strong>
    <span>A nested question tree, and a banner for the data defect that invalidated a
    result.</span>
  </a>
  <a class="card" href="./demo/workflow-mining/question-semantic-event-clustering.html">
    <strong>Comparability groups</strong>
    <span>Results on dataset v1 and v2 in separate tables, the v1 group struck through. Numbers
    from different groups never share a column.</span>
  </a>
  <a class="card" href="./demo/workflow-mining/experiment-semantic-event-clustering--001-group-vs-event-embeddings.html">
    <strong>A sweep</strong>
    <span>Forty runs from <code>runs.jsonl</code> as a sortable table and a scatter — because
    "supported in 31 of 40 configurations" is a different claim from "supported".</span>
  </a>
  <a class="card" href="./demo/workflow-mining/ledger.html">
    <strong>An invalidated hypothesis</strong>
    <span>Struck through, with its reason, still listed. That it was tried is permanent knowledge
    even when the number is not.</span>
  </a>
</div>

## What each claim looks like in practice

| Claim | Where you can see it |
|---|---|
| Research status at a glance | the overview table — one row per question, indented by nesting |
| Collaboration with no install | this page. It is a static export; there is no server |
| Picking up after a long gap | the hypothesis ledger, plus a `prior-art.md` with a `valid_until` |
| Negative results kept | two refuted and one inconclusive verdict in the conversion example |
| Results that stopped counting | the invalidated v1 group in workflow mining |
| A question actually answered | the `entity-canonicalization` sub-question, with its evidence linked |

Every page here was rendered by the same code that `aorf serve` runs locally, over the same
projection that `aorf show --json` prints. There is one renderer, and one set of derivation
rules.
