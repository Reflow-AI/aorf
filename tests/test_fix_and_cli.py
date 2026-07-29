"""`check --fix` must be idempotent and must never touch hand-written prose.

This is the load-bearing property of the whole design: experiment frontmatter is the only
hand-written source of truth and everything else is derived, which is only safe if the thing
doing the deriving cannot eat a human's sentences.
"""

from __future__ import annotations

import json
from pathlib import Path

from aorf import fix
from aorf.check import check_path
from aorf.cli import main
from aorf.parse import split_frontmatter
from conftest import build_repo, experiment_fm, write_doc

PROSE = """
# What the evidence says

This paragraph is hand-written and must survive `--fix` byte for byte, including this
deliberately awkward sentence and its trailing spaces.
"""


def repo_with_synthesis(root: Path) -> Path:
    build_repo(root)
    write_doc(
        root / "questions" / "the-thing" / "synthesis.md",
        {
            "type": "synthesis",
            "title": "Comparison",
            "description": "Results side by side.",
            "question": "./index.md",
            "status": "draft",
        },
        f"<!-- AORF:BEGIN generated -->\nstale\n<!-- AORF:END generated -->\n{PROSE}",
    )
    return root


def test_fix_refreshes_the_generated_region(tmp_path: Path):
    root = repo_with_synthesis(tmp_path / "repo")
    result = fix.apply(root)
    assert result.any
    text = (root / "questions" / "the-thing" / "synthesis.md").read_text(encoding="utf-8")
    assert "stale" not in text
    assert "001-the-thing" in text


def test_fix_preserves_prose_outside_the_markers(tmp_path: Path):
    root = repo_with_synthesis(tmp_path / "repo")
    fix.apply(root)
    text = (root / "questions" / "the-thing" / "synthesis.md").read_text(encoding="utf-8")
    assert PROSE.strip() in text


def test_fix_is_idempotent(tmp_path: Path):
    root = repo_with_synthesis(tmp_path / "repo")
    fix.apply(root)
    after_first = (root / "questions" / "the-thing" / "synthesis.md").read_text(encoding="utf-8")
    second = fix.apply(root)
    after_second = (root / "questions" / "the-thing" / "synthesis.md").read_text(encoding="utf-8")
    assert after_first == after_second
    assert not second.any, f"second pass still changed: {second.changed}"


def test_fix_adds_a_generated_region_when_absent(tmp_path: Path):
    root = tmp_path / "repo"
    build_repo(root)
    write_doc(
        root / "questions" / "the-thing" / "synthesis.md",
        {
            "type": "synthesis",
            "title": "Comparison",
            "description": "Results side by side.",
            "question": "./index.md",
            "status": "draft",
        },
        "# Only prose here\n",
    )
    fix.apply(root)
    text = (root / "questions" / "the-thing" / "synthesis.md").read_text(encoding="utf-8")
    assert "AORF:BEGIN generated" in text
    assert "# Only prose here" in text


def test_fix_corrects_a_drifted_baseline_value(tmp_path: Path):
    """R21's counterpart: the denormalized copy is repaired from its source."""
    root = tmp_path / "repo"
    build_repo(
        root,
        experiment=experiment_fm(
            metrics=[
                {
                    "name": "score",
                    "value": 0.70,
                    "baseline_value": 0.42,  # the baseline measured 0.50
                    "direction": "higher_is_better",
                    "primary": True,
                }
            ]
        ),
    )
    assert [i for i in check_path(root)[1].errors if i.rule == "R21"]
    fix.apply(root)
    _, report = check_path(root)
    assert not [i for i in report.errors if i.rule == "R21"], [i.format() for i in report.errors]
    text = (
        root / "questions" / "the-thing" / "experiments" / "001-the-thing" / "index.md"
    ).read_text(encoding="utf-8")
    assert "baseline_value: 0.5" in text


def test_fix_leaves_other_frontmatter_untouched(tmp_path: Path):
    """A line-scoped substitution, not a YAML round-trip: only the number moves."""
    root = tmp_path / "repo"
    build_repo(
        root,
        experiment=experiment_fm(
            tracker="LIN-482",
            metrics=[
                {"name": "score", "value": 0.70, "baseline_value": 0.42,
                 "direction": "higher_is_better", "primary": True}
            ],
        ),
    )
    path = root / "questions" / "the-thing" / "experiments" / "001-the-thing" / "index.md"
    before_fm, before_body = split_frontmatter(path.read_text(encoding="utf-8"))
    fix.apply(root)
    after_fm, after_body = split_frontmatter(path.read_text(encoding="utf-8"))
    assert after_body == before_body
    changed = [
        (a, b)
        for a, b in zip(before_fm.split("\n"), after_fm.split("\n"), strict=True)
        if a != b
    ]
    assert len(changed) == 1, changed
    assert "baseline_value" in changed[0][0]


def test_fix_on_a_clean_repo_does_nothing(valid_repo: Path):
    assert not fix.apply(valid_repo).any


# --- CLI ---------------------------------------------------------------------------------


def test_check_exit_code_zero(valid_repo: Path, capsys):
    assert main(["check", str(valid_repo)]) == 0
    assert "Clean." in capsys.readouterr().out


def test_check_exit_code_one_on_error(tmp_path: Path, capsys):
    build_repo(tmp_path, experiment=experiment_fm(verdict="pending"))
    assert main(["check", str(tmp_path)]) == 1
    assert "R04" in capsys.readouterr().out


def test_check_exit_code_two_on_unreadable_path(tmp_path: Path):
    assert main(["check", str(tmp_path / "nope")]) == 2


def test_check_json_is_machine_readable(valid_repo: Path, capsys):
    main(["check", str(valid_repo), "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["counts"]["error"] == 0
    assert isinstance(payload["issues"], list)


def test_show_json_is_the_projection(valid_repo: Path, capsys):
    assert main(["show", str(valid_repo)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["research"]["title"] == "Test research"
    assert payload["questions"][0]["best"]["id"] == "001-the-thing"


def test_init_scaffolds_three_documents(tmp_path: Path, capsys):
    target = tmp_path / "fresh"
    assert main(["init", str(target), "--title", "My research"]) == 0
    created = capsys.readouterr().out
    assert "index.md" in created
    assert "AGENTS.md" in created
    docs = sorted(p.relative_to(target).as_posix() for p in target.rglob("*.md"))
    # Exactly the three documents plus the agent contract: minimal mode is normative.
    assert docs == [
        "AGENTS.md",
        "index.md",
        "questions/what-is-the-first-thing-we-need-to-find-out/experiments/001-first-experiment/index.md",
        "questions/what-is-the-first-thing-we-need-to-find-out/index.md",
    ]


def test_init_output_validates(tmp_path: Path):
    target = tmp_path / "fresh"
    main(["init", str(target), "--title", "My research", "--question", "Does it work?"])
    _, report = check_path(target)
    assert report.ok, "\n".join(i.format() for i in report.errors)


def test_init_refuses_a_populated_directory(tmp_path: Path):
    target = tmp_path / "fresh"
    target.mkdir()
    (target / "notes.md").write_text("hello", encoding="utf-8")
    assert main(["init", str(target)]) == 2


def test_build_writes_a_static_site(examples_dir: Path, tmp_path: Path):
    from aorf.build import build_site

    out = tmp_path / "site"
    written = build_site(examples_dir / "signup-conversion", out)
    assert written > 0
    assert (out / "index.html").is_file()
    assert (out / "static" / "aorf.css").is_file()
    assert (out / ".nojekyll").is_file()
    assert (out / "404.html").is_file()
    # the PNG artifact must be copied, or the inline-image branch has nothing to show
    pngs = list((out / "artifacts").rglob("*.png"))
    assert pngs, "artifacts were not copied into the export"


def test_build_base_prefix_rewrites_root_links(examples_dir: Path, tmp_path: Path):
    """A GitHub Pages project site is served under /<repo>/, so links must be prefixed."""
    from aorf.build import build_site

    out = tmp_path / "site"
    build_site(examples_dir / "minimal-spike", out, base="/aorf/demo")
    html = (out / "index.html").read_text(encoding="utf-8")
    assert 'href="/aorf/demo/static/aorf.css"' in html
    assert 'href="/static/aorf.css"' not in html


def test_build_and_serve_agree_on_urls(examples_dir: Path, tmp_path: Path):
    """The one-renderer claim: every path build writes is a path serve answers."""
    from aorf.build import build_site
    from aorf.model import load
    from aorf.render.html import Renderer

    out = tmp_path / "site"
    build_site(examples_dir / "workflow-mining", out)
    renderer = Renderer(load(examples_dir / "workflow-mining"))
    for url_path in renderer.all_paths():
        assert (out / url_path.lstrip("/")).is_file(), f"{url_path} missing from the export"
        assert renderer.page_for(url_path) is not None
