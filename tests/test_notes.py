"""`notes/` is payload, so these tests guard two claims at once.

That nothing in `notes/` reaches validation or a rollup, and that the dashboard still shows it —
in its own section, which is the only place a thing with no `type` and no status belongs.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from aorf import notes
from aorf.model import load
from aorf.project import project
from aorf.render.html import Renderer
from conftest import build_repo


def write_note(root: Path, name: str, text: str) -> Path:
    d = root / "notes"
    d.mkdir(parents=True, exist_ok=True)
    path = d / name
    path.write_text(text, encoding="utf-8")
    return path


# --- reading ------------------------------------------------------------------------------


def test_a_note_with_no_frontmatter_is_a_complete_note(tmp_path: Path):
    """The spec forbids requiring any field, so the reader must not need one."""
    build_repo(tmp_path)
    write_note(tmp_path, "2026-08-19-a-thought.md", "Just a thought.\n")
    loaded = notes.load(tmp_path)
    assert len(loaded.items) == 1
    n = loaded.items[0]
    assert n.title == "A thought"  # derived from the filename
    assert n.date == "2026-08-19"  # derived from the filename
    assert n.status == "open"
    assert n.body == "Just a thought."


def test_frontmatter_wins_over_the_filename(tmp_path: Path):
    build_repo(tmp_path)
    write_note(
        tmp_path,
        "2026-08-19-slug.md",
        "---\ntitle: A real name\nbrief: The point.\ndate: 2026-01-01\nstatus: promoted\n"
        "promoted_to: /questions/the-thing/index.md\n---\n\nBody.\n",
    )
    n = notes.load(tmp_path).items[0]
    assert (n.title, n.brief, n.date, n.status) == (
        "A real name",
        "The point.",
        "2026-01-01",
        "promoted",
    )
    assert n.promoted_to == "/questions/the-thing/index.md"


def test_an_unparseable_note_still_keeps_its_body(tmp_path: Path):
    """Notes are never validated, so a broken one must degrade rather than raise."""
    build_repo(tmp_path)
    write_note(tmp_path, "2026-08-19-broken.md", "---\ntitle: [unclosed\n---\n\nStill here.\n")
    n = notes.load(tmp_path).items[0]
    assert n.body == "Still here."
    assert n.title == "Broken"


def test_notes_are_newest_first(tmp_path: Path):
    build_repo(tmp_path)
    for day in ("2026-08-01", "2026-08-19", "2026-08-10"):
        write_note(tmp_path, f"{day}-x.md", "x\n")
    assert [n.date for n in notes.load(tmp_path).items] == [
        "2026-08-19",
        "2026-08-10",
        "2026-08-01",
    ]


def test_root_index_is_the_intro_and_not_a_note(tmp_path: Path):
    build_repo(tmp_path)
    write_note(tmp_path, "index.md", "# Notes\n\nWhat this directory is.\n")
    write_note(tmp_path, "2026-08-19-x.md", "x\n")
    loaded = notes.load(tmp_path)
    assert "What this directory is." in loaded.intro
    assert [n.rel for n in loaded.items] == ["notes/2026-08-19-x.md"]


def test_a_nested_notes_directory_is_read_and_labelled(tmp_path: Path):
    """A question may keep its own notes; the dashboard has to say which directory they are in."""
    build_repo(tmp_path)
    d = tmp_path / "questions" / "the-thing" / "notes"
    d.mkdir(parents=True)
    (d / "2026-08-19-local.md").write_text("Local thought.\n", encoding="utf-8")
    n = notes.load(tmp_path).items[0]
    assert n.dir == "questions/the-thing/notes"


def test_no_notes_directory_is_falsy(tmp_path: Path):
    build_repo(tmp_path)
    assert not notes.load(tmp_path)


# --- isolation from the research ----------------------------------------------------------


def test_notes_never_reach_the_projection(tmp_path: Path):
    """The spec requires exclusion from every rollup, and the projection is every rollup."""
    build_repo(tmp_path)
    write_note(tmp_path, "index.md", "# Notes\n")
    write_note(tmp_path, "2026-08-19-x.md", "---\ntitle: Secret\n---\n\nBody.\n")
    data = project(load(tmp_path))
    assert "Secret" not in str(data)
    assert "notes/" not in str(data)


# --- rendering ----------------------------------------------------------------------------


def _renderer(root: Path) -> Renderer:
    return Renderer(load(root))


def test_no_notes_means_no_section_at_all(tmp_path: Path):
    """An empty tab in every repo would be the dashboard asking for an optional directory."""
    build_repo(tmp_path)
    r = _renderer(tmp_path)
    assert "Notes" not in [label for label, _ in r.nav]
    assert "/notes.html" not in r.all_paths()
    assert r.page_for("/notes.html") is None


def test_notes_get_their_own_page_and_nav_entry(tmp_path: Path):
    build_repo(tmp_path)
    write_note(tmp_path, "2026-08-19-x.md", "---\ntitle: A thought\nbrief: The point.\n---\n")
    r = _renderer(tmp_path)
    assert ("Notes", "/notes.html") in r.nav
    assert "/notes.html" in r.all_paths()
    html = r.page_for("/notes.html")
    assert "A thought" in html and "The point." in html


def test_the_page_groups_by_status_in_lifecycle_order(tmp_path: Path):
    build_repo(tmp_path)
    for status in ("dropped", "open", "promoted"):
        write_note(
            tmp_path,
            f"2026-08-19-{status}.md",
            f"---\ntitle: {status.capitalize()} one\nstatus: {status}\n---\n",
        )
    html = _renderer(tmp_path).page_for("/notes.html")
    order = [html.index(f">{s.capitalize()} ") for s in ("Open", "Promoted", "Dropped")]
    assert order == sorted(order), "status groups are out of lifecycle order"


def test_an_unknown_status_is_shown_rather_than_dropped(tmp_path: Path):
    """Nothing here is validated, so nothing here may be silently discarded either."""
    build_repo(tmp_path)
    write_note(tmp_path, "2026-08-19-x.md", "---\ntitle: Odd\nstatus: marinating\n---\n")
    html = _renderer(tmp_path).page_for("/notes.html")
    assert "marinating" in html and "Odd" in html


def test_promoted_to_becomes_a_dashboard_link(tmp_path: Path):
    """A promotion the reader cannot follow is a promotion they have to go and look up."""
    build_repo(tmp_path)
    write_note(
        tmp_path,
        "2026-08-19-x.md",
        "---\ntitle: Became a question\nstatus: promoted\n"
        "promoted_to: /questions/the-thing/index.md\n---\n",
    )
    html = _renderer(tmp_path).page_for("/notes.html")
    assert 'href="/question-the-thing.html"' in html


def test_a_note_cannot_inject_html(tmp_path: Path):
    """Notes are the least-validated content in a repo, so the renderer must not trust them.

    Raw HTML is disabled for documents already; a note bypassing that would make `notes/` the
    soft spot in a dashboard whose whole claim is that nothing in it executes.
    """
    build_repo(tmp_path)
    write_note(
        tmp_path,
        "2026-08-19-x.md",
        "---\ntitle: <img src=x onerror=alert(1)>\nbrief: <b>bold</b>\n---\n\n"
        "<script>alert(2)</script>\n",
    )
    html = _renderer(tmp_path).page_for("/notes.html")
    # Escaped in all three places a note can carry text: title, brief and body.
    assert "&lt;img src=x onerror=alert(1)&gt;" in html
    assert "&lt;b&gt;bold&lt;/b&gt;" in html
    assert "&lt;script&gt;alert(2)&lt;/script&gt;" in html
    assert "<img" not in html
    assert "<script>alert" not in html


# --- the examples ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "name,expected", [("topic-clustering", 4), ("signup-conversion", 2), ("minimal-spike", 1)]
)
def test_every_example_ships_notes(examples_dir: Path, name: str, expected: int):
    """The examples are the acceptance criteria, and notes are now part of the format."""
    assert len(notes.load(examples_dir / name).items) == expected


def test_the_examples_demonstrate_every_status(examples_dir: Path):
    statuses = set()
    for name in ("topic-clustering", "signup-conversion", "minimal-spike"):
        statuses |= {n.status for n in notes.load(examples_dir / name).items}
    assert statuses == {"open", "promoted", "dropped"}


def test_build_writes_the_notes_page(examples_dir: Path, tmp_path: Path):
    from aorf.build import build_site

    out = tmp_path / "site"
    build_site(examples_dir / "topic-clustering", out)
    html = (out / "notes.html").read_text(encoding="utf-8")
    assert "Proper nouns may be splitting topics" in html
