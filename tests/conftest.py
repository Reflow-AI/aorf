"""A builder for minimal AORF repositories.

Per-rule fixtures are constructed in code rather than checked in as directories: the broken
thing then sits three lines above the assertion about it, instead of in a file you have to go
and read. `valid_repo()` is clean by construction, and each rule test breaks exactly one
field, which is what makes the tests prove the rules are independent.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def write_doc(path: Path, frontmatter: dict, body: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    dumped = yaml.safe_dump(frontmatter, sort_keys=False, default_flow_style=False, width=200)
    path.write_text(f"---\n{dumped}---\n{body}", encoding="utf-8")


def research_fm(**over) -> dict:
    return {
        "type": "research",
        "title": "Test research",
        "description": "A repository built for tests.",
        "research_status": "active",
        "aorf_version": "0.1",
        **over,
    }


def question_fm(**over) -> dict:
    return {
        "type": "question",
        "title": "Does the thing work?",
        "description": "Whether the thing works.",
        "parent": "../../index.md",
        "research_status": "active",
        "primary_metric": "score",
        "metric_direction": "higher_is_better",
        "metric_target": 0.9,
        **over,
    }


def baseline_fm(**over) -> dict:
    return {
        "type": "experiment",
        "title": "Baseline",
        "description": "The cheapest approach, so later work has something to beat.",
        "question": "../../index.md",
        "kind": "baseline",
        "research_status": "done",
        "verdict": "n/a",
        "baseline": "none",
        "baseline_reason": "this document is the baseline",
        "datasets": [{"path": "/datasets/data.md", "role": "eval"}],
        "metrics": [
            {"name": "score", "value": 0.50, "direction": "higher_is_better", "primary": True}
        ],
        "run_date": "2026-07-01",
        **over,
    }


def experiment_fm(**over) -> dict:
    return {
        "type": "experiment",
        "title": "The thing",
        "description": "Test whether the thing raises the score.",
        "question": "../../index.md",
        "kind": "hypothesis_test",
        "research_status": "done",
        "hypothesis": "Doing the thing raises the score by at least 0.10.",
        "verdict": "supported",
        "verdict_scope": "test conditions",
        "baseline": "../000-baseline/index.md",
        "datasets": [{"path": "/datasets/data.md", "role": "eval"}],
        "metrics": [
            {
                "name": "score",
                "value": 0.70,
                "baseline_value": 0.50,
                "direction": "higher_is_better",
                "primary": True,
            }
        ],
        "run_date": "2026-07-02",
        **over,
    }


def dataset_fm(**over) -> dict:
    return {
        "type": "dataset",
        "title": "Test data",
        "description": "Data used by the tests.",
        "version": "v1",
        "resource": "./data.csv",
        "status": "stable",
        "generated": False,
        "storage": "git-lfs",
        **over,
    }


def build_repo(
    root: Path,
    research: dict | None = None,
    question: dict | None = None,
    baseline: dict | None = None,
    experiment: dict | None = None,
    dataset: dict | None = None,
    slug: str = "the-thing",
) -> Path:
    """A valid three-document repo plus a baseline and a dataset. Override any part."""
    write_doc(root / "index.md", research or research_fm(), "# Problem statement\n\nTesting.\n")
    write_doc(root / "questions" / slug / "index.md", question or question_fm(), "# Question\n")
    if baseline is not None or baseline is None:
        write_doc(
            root / "questions" / slug / "experiments" / "000-baseline" / "index.md",
            baseline or baseline_fm(),
            "# Method\n",
        )
    write_doc(
        root / "questions" / slug / "experiments" / "001-the-thing" / "index.md",
        experiment or experiment_fm(),
        "# Hypothesis\n\nAs above.\n",
    )
    write_doc(root / "datasets" / "data.md", dataset or dataset_fm(), "# Provenance\n")
    return root


@pytest.fixture
def valid_repo(tmp_path: Path) -> Path:
    return build_repo(tmp_path / "repo")


@pytest.fixture
def examples_dir() -> Path:
    return EXAMPLES


def issues_for(root: Path, rule: str, strict: bool = False):
    from aorf.check import check_path

    _, report = check_path(root, strict=strict)
    return [i for i in report.issues if i.rule == rule]


def assert_rule(root: Path, rule: str, level: str = "error", strict: bool = False):
    """Assert a rule fired at a level, and return the matching issues."""
    found = issues_for(root, rule, strict=strict)
    levels = {i.level for i in found}
    assert found, f"expected {rule} to fire; got {_summary(root, strict)}"
    assert level in levels, f"expected {rule} at {level}, got {sorted(levels)}"
    return found


def assert_no_rule(root: Path, rule: str, strict: bool = False):
    found = issues_for(root, rule, strict=strict)
    assert not found, f"{rule} fired unexpectedly: {[i.message for i in found]}"


def _summary(root: Path, strict: bool) -> str:
    from aorf.check import check_path

    _, report = check_path(root, strict=strict)
    return ", ".join(f"{i.rule}:{i.level}" for i in report.issues) or "no issues"
