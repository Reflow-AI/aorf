"""The examples are the acceptance criteria: they must validate clean and project stably.

Golden snapshots live in `tests/golden/`. Regenerate deliberately with
`python tests/regolden.py` after an intentional projection change, and read the diff — a
churning snapshot is how a silent change to the dashboard contract gets noticed.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aorf.check import check_path
from aorf.model import load
from aorf.project import project, to_json

GOLDEN = Path(__file__).parent / "golden"
EXAMPLE_NAMES = ["signup-conversion", "topic-clustering", "minimal-spike"]


def example_path(examples_dir: Path, name: str) -> Path:
    return examples_dir / name


@pytest.mark.parametrize("name", EXAMPLE_NAMES)
def test_example_validates_clean(examples_dir: Path, name: str):
    """`aorf check` on the examples must exit 0. This is wired into CI."""
    _, report = check_path(example_path(examples_dir, name))
    assert report.ok, "\n".join(i.format() for i in report.errors)


@pytest.mark.parametrize("name", EXAMPLE_NAMES)
def test_example_has_no_warnings(examples_dir: Path, name: str):
    _, report = check_path(example_path(examples_dir, name))
    ignorable = {"R18"}  # hypothesis-frozen is informational outside a git checkout
    warnings = [i for i in report.warnings if i.rule not in ignorable]
    assert not warnings, "\n".join(i.format() for i in warnings)


@pytest.mark.parametrize("name", EXAMPLE_NAMES)
def test_example_passes_strict(examples_dir: Path, name: str):
    _, report = check_path(example_path(examples_dir, name), strict=True)
    assert report.ok, "\n".join(i.format() for i in report.errors)


@pytest.mark.parametrize("name", EXAMPLE_NAMES)
def test_projection_matches_golden(examples_dir: Path, name: str):
    """The projection is the contract the dashboard depends on, so it is snapshotted."""
    actual = json.loads(to_json(load(example_path(examples_dir, name))))
    golden_file = GOLDEN / f"{name}.json"
    assert golden_file.exists(), "missing snapshot; run python tests/regolden.py"
    expected = json.loads(golden_file.read_text(encoding="utf-8"))
    assert actual == expected, (
        f"projection for {name} changed. If deliberate, run python tests/regolden.py "
        f"and review the diff."
    )


@pytest.mark.parametrize("name", EXAMPLE_NAMES)
def test_projection_is_deterministic(examples_dir: Path, name: str):
    """Nothing in project.py may read the clock, or the snapshots would churn daily."""
    path = example_path(examples_dir, name)
    assert to_json(load(path)) == to_json(load(path))


def test_signup_conversion_shape(examples_dir: Path):
    """Spot-check the derivations rather than only that they are stable."""
    data = project(load(example_path(examples_dir, "signup-conversion")))
    question = data["questions"][0]
    assert question["primary_metric"] == "conversion_rate"
    assert question["hypotheses_tested"] == 3
    assert question["invalidated_count"] == 0
    # 0.34 vs a 0.28 baseline: the credit-card experiment wins.
    assert question["best"]["id"] == "001-remove-cc-requirement"
    assert question["best"]["metric"]["delta"] == pytest.approx(0.06)
    assert len(data["ledger"]) == 3


def test_topic_clustering_excludes_invalidated_from_best(examples_dir: Path):
    """The invalidated proper-noun result must not become the current best."""
    data = project(load(example_path(examples_dir, "topic-clustering")))
    by_slug = {q["slug"]: q for q in data["questions"]}
    clustering = by_slug["article-topic-clustering"]
    assert clustering["invalidated_count"] == 1
    assert clustering["best"]["id"] == "001-document-vs-sentence-embeddings"
    # but it stays in the ledger, which is the whole point
    ledger_ids = {r["id"] for r in data["ledger"]}
    assert "002-proper-noun-stripping" in ledger_ids
    invalidated = next(r for r in data["ledger"] if r["id"] == "002-proper-noun-stripping")
    assert invalidated["verdict_state"] == "invalidated"
    assert invalidated["invalidation_reason"]


def test_topic_clustering_partitions_by_comparability(examples_dir: Path):
    """The v1 and v2 results must not share a table."""
    from aorf.project import comparability_groups

    model = load(example_path(examples_dir, "topic-clustering"))
    question = next(
        q for q in model.all_questions.values() if q.slug == "article-topic-clustering"
    )
    groups = comparability_groups(model, question)
    assert len(groups) == 2
    invalidated = [g for g in groups if g["invalidated"]]
    assert len(invalidated) == 1
    assert invalidated[0]["key"]["dataset_version"] == "v1"


def test_minimal_spike_falls_back_to_target(examples_dir: Path):
    """With `baseline: none` there is no delta, so metric_target is the reference."""
    data = project(load(example_path(examples_dir, "minimal-spike")))
    question = data["questions"][0]
    assert question["reference"]["kind"] == "target"
    assert question["reference"]["value"] == pytest.approx(0.90)
    assert question["best"]["metric"]["delta"] is None


def test_answered_subquestion_carries_evidence(examples_dir: Path):
    data = project(load(example_path(examples_dir, "topic-clustering")))
    answered = next(q for q in data["questions"] if q["status"] == "answered")
    assert answered["answer"]
    assert answered["best"]["id"] == "002-statistical-token-classification"


def test_every_example_renders_every_page(examples_dir: Path):
    """Seven views over three examples: no page may raise on real data."""
    from aorf.render.html import Renderer

    for name in EXAMPLE_NAMES:
        renderer = Renderer(load(example_path(examples_dir, name)))
        for path in renderer.all_paths():
            html = renderer.page_for(path)
            assert html, f"{name}{path} rendered empty"
            assert "<!doctype html>" in html.lower()


def test_unknown_page_is_none(examples_dir: Path):
    from aorf.render.html import Renderer

    renderer = Renderer(load(example_path(examples_dir, "minimal-spike")))
    assert renderer.page_for("/question-does-not-exist.html") is None
    assert renderer.page_for("/nonsense") is None


def test_unknown_fields_are_preserved(tmp_path: Path):
    """OKF requires consumers to preserve fields they do not know."""
    from conftest import build_repo, question_fm

    build_repo(tmp_path, question=question_fm(okf_usage_window="2026-Q2", custom_thing=[1, 2]))
    model = load(tmp_path)
    question = next(iter(model.all_questions.values()))
    assert question.doc.fm["okf_usage_window"] == "2026-Q2"
    assert question.doc.fm["custom_thing"] == [1, 2]
    _, report = check_path(tmp_path)
    assert report.ok
