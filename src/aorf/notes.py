"""Reading `notes/`, which is payload and therefore gets its own reader.

Deliberately outside `parse.discover` and `project`: a note is not a document, nothing
derives from one, and nothing here may reach a rollup. That is also why the dashboard gives
notes their own section rather than mixing them into the research pages — shown next to
questions and findings they would borrow a standing they do not have.

Nothing in this module may fail on a malformed note. The spec forbids requiring any
frontmatter field, so every field has a fallback and a note with no frontmatter at all is a
complete note.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from . import parse, spec

# `notes/YYYY-MM-DD-slug.md`. The date prefix is the convention that makes the directory
# listing sort itself, so it is also the fallback for a note that omits `date`.
FILENAME_DATE = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.*)$")


@dataclass(frozen=True)
class Note:
    rel: str
    dir: str  # the notes/ directory this lives in, so nested ones stay distinguishable
    title: str
    brief: str
    date: str
    status: str
    promoted_to: str
    dropped_reason: str
    body: str


@dataclass(frozen=True)
class Notes:
    """Every note in the repo, plus the root `notes/index.md` explainer when there is one."""

    intro: str = ""
    intro_rel: str = ""
    items: list[Note] = field(default_factory=list)

    def __bool__(self) -> bool:
        return bool(self.items or self.intro)

    def by_status(self, status: str) -> list[Note]:
        return [n for n in self.items if n.status == status]


def _text(value) -> str:
    return "" if value is None else str(value).strip()


def _title_from(stem: str) -> str:
    """`2026-08-19-tokeniser-doubt` -> `Tokeniser doubt`. A name is required to show a row."""
    match = FILENAME_DATE.match(stem)
    words = (match.group(2) if match else stem).replace("-", " ").replace("_", " ").strip()
    return words[:1].upper() + words[1:] if words else stem


def _read(root: Path, path: Path) -> Note:
    rel = path.relative_to(root).as_posix()
    raw, body = parse.split_frontmatter(path.read_text(encoding="utf-8"))
    fm: dict = {}
    if raw.strip():
        try:
            loaded = yaml.safe_load(raw)
        except yaml.YAMLError:
            loaded = None  # an unparseable note is still a note; keep the body
        if isinstance(loaded, dict):
            fm = parse._normalize(loaded)

    stem = path.name.removesuffix(".md")
    match = FILENAME_DATE.match(stem)
    # An unrecognised status is passed through untouched: notes are never validated, and
    # silently rewriting an author's word would be the wrong kind of helpful.
    status = _text(fm.get("status")) or spec.NOTE_STATUS[0]
    return Note(
        rel=rel,
        dir=path.parent.relative_to(root).as_posix(),
        title=_text(fm.get("title")) or _title_from(stem),
        brief=_text(fm.get("brief")),
        date=_text(fm.get("date")) or (match.group(1) if match else ""),
        status=status,
        promoted_to=_text(fm.get("promoted_to")),
        dropped_reason=_text(fm.get("dropped_reason")),
        body=body.strip(),
    )


def load(root: Path | str) -> Notes:
    """Every `.md` under any `notes/` directory, newest first.

    `index.md` is never a note: in the root `notes/` it is the directory's explainer, and
    anywhere else it is still just payload prose.
    """
    root = Path(root)
    if not root.is_dir():
        return Notes()
    items: list[Note] = []
    intro, intro_rel = "", ""
    for path in sorted(root.rglob("*.md")):
        parts = path.relative_to(root).parts
        if any(p.startswith(".") for p in parts):
            continue
        if "notes" not in parts[:-1]:
            continue
        if path.is_symlink() and not parse.inside(root, path):
            continue
        if path.name == "index.md":
            if parts == ("notes", "index.md"):
                _, intro = parse.split_frontmatter(path.read_text(encoding="utf-8"))
                intro, intro_rel = intro.strip(), path.relative_to(root).as_posix()
            continue
        items.append(_read(root, path))
    # Newest first: a notes directory is read from the top, unlike a question tree.
    items.sort(key=lambda n: (n.date, n.rel), reverse=True)
    return Notes(intro=intro, intro_rel=intro_rel, items=items)
