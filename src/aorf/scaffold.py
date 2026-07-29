"""`aorf init`: the three documents day one actually needs, and nothing else.

Minimal mode is normative, so this is deliberately not a generator of nine files full of TBD.
A scaffold that emits placeholder documents makes the repo read as populated while the reading
rules return confidently empty answers — worse than an absent scaffold.

`init` is the secondary path. The primary one is handing an agent the scaffolding URL, which
needs no install at all.
"""

from __future__ import annotations

from pathlib import Path

from . import spec
from .parse import AorfError

ASSETS = Path(__file__).parent / "assets"

_RESEARCH = """---
type: research
title: {title}
description: {description}
research_status: active
aorf_version: "{version}"
---

# Problem statement

{description}

# Goal and success criteria

State what "done" looks like as something measurable. If you have a north-star metric, add
`primary_metric`, `metric_direction` and `metric_target` to the frontmatter above so the
dashboard has a headline.

# Scope and non-goals

What this research will not attempt, so a later reader does not assume it was missed.

# Questions

- [{question_title}](questions/{question_slug}/index.md)

# Datasets

None referenced yet. Add `datasets/<name>.md` when an experiment points at data.

# Findings

None yet. Add `findings/<slug>.md` when something is discovered that is not an experiment
result — a data defect, a model that changed underneath you.
"""

_QUESTION = """---
type: question
title: {title}
description: {description}
parent: ../../index.md
research_status: open
---

# Question

{title}

# Why this matters

What decision changes depending on the answer. If nothing changes, this is not a question
worth running experiments on.

# Current best result

Nothing yet.

# Prior art

No search recorded. When you run one, write it up in `prior-art.md` next to this file — and
get approval before spending money on it.

# Experiments

- [001-first-experiment](experiments/001-first-experiment/index.md)

# Sub-questions

None.
"""

_EXPERIMENT = """---
type: experiment
title: First experiment
description: One sentence on what this experiment does.
question: ../../index.md
kind: hypothesis_test
research_status: planned
hypothesis: "State one falsifiable claim with an expected measurable effect, before running."
baseline: none
baseline_reason: "No baseline yet. Replace this with a path to a baseline experiment once one
  exists — a number to beat is what makes the results after it mean something."
---

# Hypothesis

State the claim here as well, in full. Write it **before** the run and do not edit it
afterwards: if the result suggests a different claim, that is a new experiment with `retests`
pointing at this one.

# Method

What you will actually do. Enough that someone else could repeat it.

# Results

Fill in after running. Then add to the frontmatter: `verdict`, `metrics`, `run_date`, and set
`research_status: done`.

# Conclusion

What the numbers mean. Record `refuted` and `inconclusive` as readily as `supported` — a
negative result recorded once is what stops it being paid for twice.

# Next

What this makes worth doing, or worth abandoning.
"""


def _write(path: Path, content: str, created: list[str], root: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    created.append(path.relative_to(root).as_posix())


def init(
    root: Path,
    title: str = "",
    question: str = "",
    force: bool = False,
) -> list[str]:
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)

    existing = [p for p in root.iterdir() if p.name not in (".git", ".gitignore")]
    if (root / "index.md").exists() and not force:
        raise AorfError(
            f"{root / 'index.md'} already exists. This looks like an AORF repository already; "
            f"pass --force to write into it anyway."
        )
    if existing and not force:
        names = ", ".join(sorted(p.name for p in existing)[:5])
        raise AorfError(
            f"{root} is not empty ({names}). Pass --force if you meant to scaffold in place."
        )

    title = title or "Untitled research"
    question_title = question or "What is the first thing we need to find out?"
    slug = "".join(
        c if c.isalnum() else "-" for c in question_title.lower()
    ).strip("-")[:48].strip("-") or "first-question"

    created: list[str] = []
    _write(
        root / "index.md",
        _RESEARCH.format(
            title=title,
            description="One sentence stating the problem this research exists to solve.",
            version=spec.AORF_VERSION,
            question_title=question_title,
            question_slug=slug,
        ),
        created,
        root,
    )
    _write(
        root / "questions" / slug / "index.md",
        _QUESTION.format(
            title=question_title,
            description="One sentence on what answering this would tell you.",
        ),
        created,
        root,
    )
    _write(
        root / "questions" / slug / "experiments" / "001-first-experiment" / "index.md",
        _EXPERIMENT,
        created,
        root,
    )
    (root / "questions" / slug / "experiments" / "001-first-experiment" / "artifacts").mkdir(
        parents=True, exist_ok=True
    )

    _write(root / "AGENTS.md", (ASSETS / "AGENTS.md").read_text(encoding="utf-8"), created, root)
    if not (root / ".gitignore").exists():
        _write(
            root / ".gitignore",
            (ASSETS / "gitignore").read_text(encoding="utf-8"),
            created,
            root,
        )
    if not (root / ".gitattributes").exists():
        _write(
            root / ".gitattributes",
            (ASSETS / "gitattributes").read_text(encoding="utf-8"),
            created,
            root,
        )
    return created
