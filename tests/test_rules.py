"""One deliberately broken fixture per integrity rule, asserting the exact error.

Every test starts from a repo that validates clean, breaks exactly one thing, and asserts
that one rule fires. `test_valid_repo_is_clean` is what makes the rest meaningful: without it,
a rule that fires on everything would still pass its own test.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from aorf.check import check_path
from conftest import (
    assert_no_rule,
    assert_rule,
    baseline_fm,
    build_repo,
    dataset_fm,
    experiment_fm,
    issues_for,
    question_fm,
    research_fm,
    write_doc,
)


def test_valid_repo_is_clean(valid_repo: Path):
    _, report = check_path(valid_repo)
    assert report.ok, [i.format() for i in report.errors]
    # R26 wants a synthesis at three experiments; this repo has two, so it must stay quiet.
    assert not report.warnings, [i.format() for i in report.warnings]


# --- R01 display contract ----------------------------------------------------------------


@pytest.mark.parametrize("field", ["title", "description"])
def test_r01_missing_display_field(tmp_path: Path, field: str):
    fm = question_fm()
    del fm[field]
    build_repo(tmp_path, question=fm)
    issues = assert_rule(tmp_path, "R01")
    assert any(field in i.message for i in issues)


def test_r01_missing_status_field(tmp_path: Path):
    fm = experiment_fm()
    del fm["research_status"]
    build_repo(tmp_path, experiment=fm)
    issues = assert_rule(tmp_path, "R01")
    assert any("research_status" in i.message for i in issues)


def test_r01_dataset_status_is_required(tmp_path: Path):
    """Dataset status is required by the display contract, not optional as v0.1 first said."""
    fm = dataset_fm()
    del fm["status"]
    build_repo(tmp_path, dataset=fm)
    issues = assert_rule(tmp_path, "R01")
    assert any("status" in i.message for i in issues)


def test_r01_synthesis_status_is_required(tmp_path: Path):
    build_repo(tmp_path)
    write_doc(
        tmp_path / "questions" / "the-thing" / "synthesis.md",
        {
            "type": "synthesis",
            "title": "Comparison",
            "description": "Results side by side.",
            "question": "./index.md",
        },
    )
    assert_rule(tmp_path, "R01")


def test_r01_unknown_type(tmp_path: Path):
    build_repo(tmp_path)
    write_doc(
        tmp_path / "findings" / "odd.md",
        {"type": "observation", "title": "Odd", "description": "Not an AORF type."},
    )
    issues = assert_rule(tmp_path, "R01")
    assert any("unknown type" in i.message for i in issues)


def test_r01_unparseable_frontmatter(tmp_path: Path):
    build_repo(tmp_path)
    (tmp_path / "findings").mkdir(exist_ok=True)
    (tmp_path / "findings" / "broken.md").write_text(
        "---\ntype: finding\n  bad: [indent\n---\nbody\n", encoding="utf-8"
    )
    assert_rule(tmp_path, "R01")


# --- R02 enums ---------------------------------------------------------------------------


def test_r02_bad_enum(tmp_path: Path):
    build_repo(tmp_path, experiment=experiment_fm(verdict="probably"))
    issues = assert_rule(tmp_path, "R02")
    assert any("verdict" in i.message for i in issues)


def test_r02_na_verdict_only_for_baseline(tmp_path: Path):
    build_repo(tmp_path, experiment=experiment_fm(verdict="n/a"))
    issues = assert_rule(tmp_path, "R02")
    assert any("n/a" in i.message for i in issues)


def test_r02_na_verdict_is_fine_on_baseline(valid_repo: Path):
    assert_no_rule(valid_repo, "R02")


# --- R03 links ---------------------------------------------------------------------------


def test_r03_dangling_document_link(tmp_path: Path):
    build_repo(tmp_path, experiment=experiment_fm(baseline="../999-nope/index.md"))
    assert_rule(tmp_path, "R03")


def test_r03_dangling_dataset_reference(tmp_path: Path):
    build_repo(
        tmp_path, experiment=experiment_fm(datasets=[{"path": "/datasets/gone.md", "role": "eval"}])
    )
    assert_rule(tmp_path, "R03")


def test_r03_link_escaping_repo_is_rejected(tmp_path: Path):
    root = tmp_path / "repo"
    build_repo(root, experiment=experiment_fm(supersedes="../../../outside.md"))
    issues = [i for i in check_path(root)[1].issues if i.rule in ("R03", "R25")]
    assert issues, "a link climbing out of the repository must be reported"


def test_r03_missing_sweep_runs_file(tmp_path: Path):
    build_repo(tmp_path, experiment=experiment_fm(kind="sweep", runs="./runs.jsonl"))
    issues = assert_rule(tmp_path, "R03")
    assert any("runs" in i.message for i in issues)


# --- R04 done means done -----------------------------------------------------------------


def test_r04_done_without_verdict(tmp_path: Path):
    fm = experiment_fm()
    del fm["verdict"]
    build_repo(tmp_path, experiment=fm)
    assert_rule(tmp_path, "R04")


def test_r04_done_with_pending_verdict(tmp_path: Path):
    build_repo(tmp_path, experiment=experiment_fm(verdict="pending"))
    assert_rule(tmp_path, "R04")


def test_r04_done_without_metrics(tmp_path: Path):
    fm = experiment_fm()
    del fm["metrics"]
    build_repo(tmp_path, experiment=fm)
    assert_rule(tmp_path, "R04")


def test_r04_exploration_needs_no_metrics(tmp_path: Path):
    fm = experiment_fm(kind="exploration", verdict="inconclusive")
    del fm["metrics"]
    del fm["hypothesis"]
    build_repo(tmp_path, experiment=fm)
    assert_no_rule(tmp_path, "R04")


def test_r04_done_without_run_date(tmp_path: Path):
    fm = experiment_fm()
    del fm["run_date"]
    build_repo(tmp_path, experiment=fm)
    issues = assert_rule(tmp_path, "R04")
    assert any("run_date" in i.message for i in issues)


# --- R05 one primary metric --------------------------------------------------------------


def test_r05_two_primary_metrics(tmp_path: Path):
    build_repo(
        tmp_path,
        experiment=experiment_fm(
            metrics=[
                {"name": "score", "value": 0.7, "baseline_value": 0.5,
                 "direction": "higher_is_better", "primary": True},
                {"name": "other", "value": 0.2, "direction": "lower_is_better", "primary": True},
            ]
        ),
    )
    assert_rule(tmp_path, "R05")


def test_r05_no_primary_among_several(tmp_path: Path):
    build_repo(
        tmp_path,
        experiment=experiment_fm(
            metrics=[
                {"name": "score", "value": 0.7, "direction": "higher_is_better"},
                {"name": "other", "value": 0.2, "direction": "lower_is_better"},
            ]
        ),
    )
    assert_rule(tmp_path, "R05")


def test_r05_single_unmarked_metric_is_a_warning(tmp_path: Path):
    build_repo(
        tmp_path,
        experiment=experiment_fm(
            metrics=[{"name": "score", "value": 0.7, "direction": "higher_is_better"}]
        ),
    )
    assert_rule(tmp_path, "R05", level="warning")


# --- R06 through R11 ---------------------------------------------------------------------


def test_r06_baseline_none_without_reason(tmp_path: Path):
    fm = baseline_fm()
    del fm["baseline_reason"]
    build_repo(tmp_path, baseline=fm)
    assert_rule(tmp_path, "R06")


def test_r07_hypothesis_kind_without_hypothesis(tmp_path: Path):
    fm = experiment_fm()
    del fm["hypothesis"]
    build_repo(tmp_path, experiment=fm)
    assert_rule(tmp_path, "R07")


def test_r07_baseline_with_hypothesis_warns(tmp_path: Path):
    build_repo(tmp_path, baseline=baseline_fm(hypothesis="Baselines should not assert."))
    assert_rule(tmp_path, "R07", level="warning")


def test_r08_sweep_without_runs(tmp_path: Path):
    build_repo(tmp_path, experiment=experiment_fm(kind="sweep"))
    assert_rule(tmp_path, "R08")


def test_r09_invalidated_without_finding(tmp_path: Path):
    build_repo(tmp_path, experiment=experiment_fm(verdict_state="invalidated"))
    assert_rule(tmp_path, "R09")


def test_r09_superseded_without_successor(tmp_path: Path):
    build_repo(tmp_path, experiment=experiment_fm(verdict_state="superseded"))
    issues = assert_rule(tmp_path, "R09")
    assert any("superseded_by" in i.message for i in issues)


def test_r10_answered_without_evidence(tmp_path: Path):
    build_repo(
        tmp_path, question=question_fm(research_status="answered", answer="Yes, it works.")
    )
    issues = assert_rule(tmp_path, "R10")
    assert any("answer_evidence" in i.message for i in issues)


def test_r10_answered_without_answer(tmp_path: Path):
    build_repo(
        tmp_path,
        question=question_fm(
            research_status="answered",
            answer_evidence=["./experiments/001-the-thing/index.md"],
        ),
    )
    assert_rule(tmp_path, "R10")


def test_r11_abandoned_experiment_without_reason(tmp_path: Path):
    fm = experiment_fm(research_status="abandoned")
    del fm["metrics"]
    build_repo(tmp_path, experiment=fm)
    assert_rule(tmp_path, "R11")


def test_r11_abandoned_question_without_reason(tmp_path: Path):
    build_repo(tmp_path, question=question_fm(research_status="abandoned"))
    assert_rule(tmp_path, "R11")


# --- R12 dataset comparability -----------------------------------------------------------


def test_r12_baseline_on_a_different_dataset_version(tmp_path: Path):
    build_repo(tmp_path)
    write_doc(tmp_path / "datasets" / "data-v2.md", dataset_fm(title="Test data v2", version="v2"))
    write_doc(
        tmp_path / "questions" / "the-thing" / "experiments" / "001-the-thing" / "index.md",
        experiment_fm(datasets=[{"path": "/datasets/data-v2.md", "role": "eval"}]),
    )
    assert_rule(tmp_path, "R12")


def test_r12_skipped_for_invalidated(tmp_path: Path):
    """One problem, one error: an invalidated result is exempt from the comparability check."""
    build_repo(tmp_path)
    write_doc(tmp_path / "datasets" / "data-v2.md", dataset_fm(title="Test data v2", version="v2"))
    write_doc(
        tmp_path / "findings" / "defect.md",
        {
            "type": "finding",
            "title": "The data was wrong",
            "description": "A defect in v1.",
            "scope": "repo",
            "severity": "blocking",
            "discovered": "2026-07-03",
            "status": "open",
        },
    )
    write_doc(
        tmp_path / "questions" / "the-thing" / "experiments" / "001-the-thing" / "index.md",
        experiment_fm(
            datasets=[{"path": "/datasets/data-v2.md", "role": "eval"}],
            verdict_state="invalidated",
            invalidated_by="/findings/defect.md",
            invalidation_reason="ran on the wrong dataset version",
        ),
    )
    assert_no_rule(tmp_path, "R12")


# --- R13, R14 data rules -----------------------------------------------------------------


def test_r13_generated_without_generator(tmp_path: Path):
    build_repo(tmp_path, dataset=dataset_fm(generated=True, storage="none"))
    assert_rule(tmp_path, "R13")


def test_r13_generated_data_committed_warns(tmp_path: Path):
    build_repo(
        tmp_path,
        dataset=dataset_fm(generated=True, generator="/shared/build.py", storage="git"),
    )
    (tmp_path / "shared").mkdir(exist_ok=True)
    (tmp_path / "shared" / "build.py").write_text("# generator\n", encoding="utf-8")
    assert_rule(tmp_path, "R13", level="warning")


def test_r14_source_data_not_committed_warns(tmp_path: Path):
    build_repo(tmp_path, dataset=dataset_fm(storage="external"))
    assert_rule(tmp_path, "R14", level="warning")


# --- R15 stale running -------------------------------------------------------------------


def test_r15_long_running_experiment_warns(tmp_path: Path):
    fm = experiment_fm(research_status="running", timestamp="2020-01-01")
    for key in ("verdict", "metrics", "run_date"):
        fm.pop(key, None)
    build_repo(tmp_path, experiment=fm)
    assert_rule(tmp_path, "R15", level="warning")


# --- R16 generated regions ---------------------------------------------------------------


def test_r16_stale_generated_region(tmp_path: Path):
    build_repo(tmp_path)
    write_doc(
        tmp_path / "questions" / "the-thing" / "synthesis.md",
        {
            "type": "synthesis",
            "title": "Comparison",
            "description": "Results side by side.",
            "question": "./index.md",
            "status": "stable",
        },
        "<!-- AORF:BEGIN generated -->\nstale content\n<!-- AORF:END generated -->\n",
    )
    assert_rule(tmp_path, "R16", level="warning")
    assert_rule(tmp_path, "R16", level="error", strict=True)


# --- R17 depth ---------------------------------------------------------------------------


def _nest(root: Path, depth: int) -> None:
    """Build a chain of nested questions `depth` levels deep."""
    build_repo(root, slug="q1")
    path = root / "questions" / "q1"
    for level in range(2, depth + 1):
        path = path / "questions" / f"q{level}"
        write_doc(path / "index.md", question_fm(title=f"Level {level}"))


def test_r17_depth_three_warns(tmp_path: Path):
    """Depth 3 warns but stays a warning under --strict; only depth 4 escalates."""
    _nest(tmp_path, 3)
    assert_rule(tmp_path, "R17", level="warning")
    assert not [i for i in issues_for(tmp_path, "R17", strict=True) if i.level == "error"]


def test_r17_depth_four_errors_under_strict(tmp_path: Path):
    _nest(tmp_path, 4)
    assert_rule(tmp_path, "R17", level="warning")
    assert_rule(tmp_path, "R17", level="error", strict=True)


def test_r17_depth_two_is_fine(tmp_path: Path):
    _nest(tmp_path, 2)
    assert_no_rule(tmp_path, "R17", strict=True)


# --- R19, R20 tags -----------------------------------------------------------------------


def test_r19_undeclared_tag(tmp_path: Path):
    build_repo(
        tmp_path,
        research=research_fm(tag_vocabulary=["alpha"]),
        question=question_fm(tags=["beta"]),
    )
    issues = assert_rule(tmp_path, "R19")
    assert any("beta" in i.message for i in issues)


def test_r19_tags_without_vocabulary(tmp_path: Path):
    build_repo(tmp_path, question=question_fm(tags=["beta"]))
    assert_rule(tmp_path, "R19")


def test_r19_no_tags_skips_the_rule(valid_repo: Path):
    assert_no_rule(valid_repo, "R19")


def test_r20_vocabulary_must_be_kebab_case(tmp_path: Path):
    build_repo(
        tmp_path,
        research=research_fm(tag_vocabulary=["Not Kebab"]),
        question=question_fm(tags=["Not Kebab"]),
    )
    assert_rule(tmp_path, "R20")


def test_r20_duplicate_vocabulary_entry(tmp_path: Path):
    build_repo(
        tmp_path,
        research=research_fm(tag_vocabulary=["alpha", "alpha"]),
        question=question_fm(tags=["alpha"]),
    )
    issues = assert_rule(tmp_path, "R20")
    assert any("duplicated" in i.message for i in issues)


# --- R21 baseline_value ------------------------------------------------------------------


def test_r21_baseline_value_drift_is_an_error(tmp_path: Path):
    """The whole justification for denormalizing baseline_value is that this rule exists."""
    build_repo(
        tmp_path,
        experiment=experiment_fm(
            metrics=[
                {
                    "name": "score",
                    "value": 0.70,
                    "baseline_value": 0.42,  # the baseline actually measured 0.50
                    "direction": "higher_is_better",
                    "primary": True,
                }
            ]
        ),
    )
    issues = assert_rule(tmp_path, "R21")
    assert any("0.5" in i.message for i in issues)


def test_r21_unsourced_baseline_value_warns(tmp_path: Path):
    build_repo(
        tmp_path,
        experiment=experiment_fm(
            metrics=[
                {"name": "score", "value": 0.7, "baseline_value": 0.5,
                 "direction": "higher_is_better", "primary": True},
                {"name": "extra", "value": 0.3, "baseline_value": 0.9,
                 "direction": "lower_is_better", "primary": False},
            ]
        ),
    )
    assert_rule(tmp_path, "R21", level="warning")


def test_r21_skipped_for_invalidated(tmp_path: Path):
    write_doc(
        (tmp_path / "findings" / "defect.md"),
        {
            "type": "finding", "title": "Defect", "description": "A defect.",
            "scope": "repo", "severity": "info", "discovered": "2026-07-03", "status": "open",
        },
    )
    build_repo(
        tmp_path,
        experiment=experiment_fm(
            verdict_state="invalidated",
            invalidated_by="/findings/defect.md",
            invalidation_reason="wrong data",
            metrics=[
                {"name": "score", "value": 0.7, "baseline_value": 0.42,
                 "direction": "higher_is_better", "primary": True}
            ],
        ),
    )
    assert_no_rule(tmp_path, "R21")


# --- R22 metric comparability ------------------------------------------------------------


def test_r22_metric_name_must_match_the_question(tmp_path: Path):
    build_repo(
        tmp_path,
        experiment=experiment_fm(
            metrics=[
                {"name": "accuracy", "value": 0.7, "direction": "higher_is_better",
                 "primary": True}
            ]
        ),
    )
    issues = assert_rule(tmp_path, "R22")
    assert any("accuracy" in i.message for i in issues)


def test_r22_direction_must_match_the_question(tmp_path: Path):
    build_repo(
        tmp_path,
        experiment=experiment_fm(
            metrics=[
                {"name": "score", "value": 0.7, "baseline_value": 0.5,
                 "direction": "lower_is_better", "primary": True}
            ]
        ),
    )
    issues = assert_rule(tmp_path, "R22")
    assert any("direction" in i.message for i in issues)


# --- R23 version compatibility -----------------------------------------------------------


def test_r23_unknown_major_version_errors(tmp_path: Path):
    build_repo(tmp_path, research=research_fm(aorf_version="1.0"))
    assert_rule(tmp_path, "R23")


def test_r23_unknown_minor_version_warns(tmp_path: Path):
    build_repo(tmp_path, research=research_fm(aorf_version="0.2"))
    assert_rule(tmp_path, "R23", level="warning")


# --- R24 dates ---------------------------------------------------------------------------


def test_r24_non_iso_date(tmp_path: Path):
    build_repo(tmp_path, experiment=experiment_fm(run_date="1 July 2026"))
    assert_rule(tmp_path, "R24")


def test_r24_yaml_native_dates_are_accepted(tmp_path: Path):
    """An unquoted YAML date parses to datetime.date and must normalize, not fail."""
    root = tmp_path / "repo"
    build_repo(root)
    path = root / "questions" / "the-thing" / "experiments" / "001-the-thing" / "index.md"
    path.write_text(
        path.read_text(encoding="utf-8").replace("run_date: '2026-07-02'", "run_date: 2026-07-02"),
        encoding="utf-8",
    )
    assert_no_rule(root, "R24")


# --- R25 link relativity -----------------------------------------------------------------


def test_r25_deep_relative_path(tmp_path: Path):
    build_repo(
        tmp_path,
        experiment=experiment_fm(
            datasets=[{"path": "../../../../datasets/data.md", "role": "eval"}]
        ),
    )
    issues = assert_rule(tmp_path, "R25")
    assert any("root-relative" in i.message for i in issues)


def test_r25_one_hop_is_allowed(valid_repo: Path):
    """`../000-baseline/index.md` is the sibling case: short and self-evidently correct."""
    assert_no_rule(valid_repo, "R25")


def test_r25_structural_links_exempt_at_any_depth(tmp_path: Path):
    _nest(tmp_path, 2)
    assert_no_rule(tmp_path, "R25")


# --- R26 synthesis when earned -----------------------------------------------------------


def test_r26_three_experiments_want_a_synthesis(tmp_path: Path):
    build_repo(tmp_path)
    base = tmp_path / "questions" / "the-thing" / "experiments"
    write_doc(base / "002-another" / "index.md", experiment_fm(title="Another"))
    assert_rule(tmp_path, "R26", level="warning")


def test_r26_quiet_below_the_threshold(valid_repo: Path):
    assert_no_rule(valid_repo, "R26")


# --- not an AORF repo at all -------------------------------------------------------------


def test_missing_root_index_is_reported(tmp_path: Path):
    (tmp_path / "notes.md").write_text("# just notes\n", encoding="utf-8")
    _, report = check_path(tmp_path)
    assert not report.ok
    assert any("not an AORF repository" in i.message for i in report.errors)
