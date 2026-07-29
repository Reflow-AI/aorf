# Why record hypotheses and verdicts

Five arguments, in priority order. The third is the one with evidence behind it.

## 1. The repo becomes unusable, including to its owner

After a few weeks nobody can answer "what did we already try and what was the result". The runs
are all there — in the tracker, in the notebooks, in the artifact bucket. What is missing is the
layer above them: what you believed before you ran, and what you concluded after.

That layer only ever existed in someone's head and in a Slack thread, so it is gone. The
experiments happened. The knowledge they produced is not recoverable.

## 2. Agents lose context between sessions

If the structure does not carry the context, you re-explain the project in every new thread.
Every session starts by paying for the same orientation.

The test is concrete: **if a fresh agent session needs no extra instructions to state the goal,
the open questions and the tested hypotheses, the repo is structured correctly.** If it needs
you to explain, the structure is not carrying its weight — and that is a property of the repo,
not of the model.

## 3. Negative results are the thing you pay for twice

Hypothesis-before-run with a recorded verdict is the one practice here with real evidence behind
it.

Registered Reports — where the hypothesis and analysis plan are reviewed *before* data
collection — report positive results in roughly **44%** of tested hypotheses, against about
**96%** in the conventional literature. Preregistered studies report significant results around
**48%** of the time versus **66%** for non-preregistered ones. Nature covered this as
[a sharp rise in null findings](https://www.nature.com/articles/d41586-018-07118-1);
[Nature Neuroscience](https://www.nature.com/articles/s41593-024-01762-9) treats the reduced
publication bias as the mechanism working as intended.

**Two honest caveats**, because the argument is stronger with them than without:

- **The comparison is not like-for-like.** Registered Reports skew toward confirmatory
  hypothesis tests, which are exactly the studies most likely to return a null. Some of that gap
  is selection, not bias correction. The direction of the effect is well supported; the precise
  size is not.
- **Preregistration is criticised as bureaucratic overhead**, and that criticism is fair when a
  human maintains the bookkeeping. The answer is that here the agent carries it — writing the
  hypothesis down before the run, and the verdict after, is a side effect of how the repo is
  structured rather than a separate discipline. That is what makes this newly practical rather
  than newly virtuous.

## 4. Research spend is repeated spend

A recorded prior-art search and a recorded refutation both stop you paying twice for the same
answer.

This is why `prior-art.md` carries `approved_by`, `cost_usd` and `valid_until`, and why the spec
puts a hard **cost gate** on agents: state the scope and expected cost, get approval, and if a
prior-art document exists and has not expired, read it instead of searching again. A broad
multi-source literature search run unprompted is a real bill for an answer someone already
bought.

## 5. Nobody can work on anyone else's research

Without a shared structure, reviewing someone's research means reading their notebooks. With
one, and a published static dashboard, the effort is reviewable by anyone with a browser and no
install.

---

## What this is not

**It is not an experiment tracker.** MLflow, Weights & Biases and friends record runs, params,
metrics and artifacts, and they do it well. AORF sits *above* that layer and records the thing
none of them models: the claim and its outcome. One `tracker` field connects the two.

**It is not a process you have to follow.** Day one is three documents. Everything else appears
when it is earned — `synthesis.md` at three experiments, `prior-art.md` when a search is
actually run, `datasets/` when an experiment points at data. A scaffold full of "TBD" is worse
than an absent one, because the reading rules then return confidently empty answers about a repo
that looks populated.

**It is not a baseline mandate.** A baseline is strongly recommended, because without a number
to beat a sequence of experiments produces results but no measurable progress. It is not
required, because a fabricated reference number makes every delta in the repo meaningless while
looking rigorous. `baseline: none` with a reason is a permanent, first-class answer.

[How to start &rarr;](./quickstart.html)
