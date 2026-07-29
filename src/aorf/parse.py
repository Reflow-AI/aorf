"""Document discovery, frontmatter parsing and link resolution.

Reading only. Nothing here writes, executes or fetches.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from . import spec


class AorfError(Exception):
    """A repo the tool cannot read at all, as distinct from one that fails validation."""


@dataclass
class Document:
    path: Path  # absolute
    rel: str  # repo-root-relative, forward slashes, no leading slash
    fm: dict
    body: str
    fm_error: str = ""  # unparseable YAML; recorded rather than raised

    @property
    def type(self) -> str:
        t = self.fm.get("type")
        return t if isinstance(t, str) else ""

    @property
    def dir(self) -> str:
        d = str(Path(self.rel).parent).replace("\\", "/")
        return "" if d == "." else d

    @property
    def status(self) -> str:
        f = spec.status_field_for(self.type)
        v = self.fm.get(f) if f else None
        return v if isinstance(v, str) else ""

    @property
    def depth(self) -> int:
        """Question nesting depth: root is 0, `questions/<slug>/` is 1, one per nesting level.

        Counting `questions/` segments means an experiment reports its owning question's
        depth, which is what the depth cap is actually about.
        """
        return sum(1 for p in self.dir.split("/") if p == "questions")

    def __repr__(self) -> str:  # keeps assertion output readable
        return f"<Document {self.rel} type={self.type or '?'}>"


@dataclass
class Repo:
    root: Path
    docs: list[Document] = field(default_factory=list)
    by_rel: dict[str, Document] = field(default_factory=dict)


# --- path safety -------------------------------------------------------------------------


def inside(root: Path, candidate: Path) -> bool:
    """True when candidate resolves to something inside root.

    Resolves symlinks on both sides, so a link pointing out of the repo is rejected rather
    than followed. Used by the checker and by the server, which must never serve a file the
    repo does not contain.
    """
    try:
        r = root.resolve(strict=False)
        c = candidate.resolve(strict=False)
    except (OSError, RuntimeError):  # RuntimeError: symlink loop
        return False
    return c == r or r in c.parents


def _is_payload(rel_parts: tuple[str, ...]) -> bool:
    return any(p in spec.PAYLOAD_DIRS for p in rel_parts[:-1])


def is_document(root: Path, path: Path) -> bool:
    """Spec 3.2, normative. Kept as one predicate so discovery is decidable and testable."""
    if path.suffix != ".md" or not path.is_file():
        return False
    try:
        rel = path.relative_to(root)
    except ValueError:
        return False
    parts = rel.parts
    if _is_payload(parts):
        return False
    if path.name in spec.RESERVED_NON_DOCS:
        return False
    if path.name in spec.DOC_FILENAMES:
        return True
    # A direct .md child of datasets/ or findings/, at any position in the tree.
    return len(parts) >= 2 and parts[-2] in spec.DOC_DIRS


# --- frontmatter -------------------------------------------------------------------------


def _normalize(value):
    """Dates to ISO strings, recursively.

    PyYAML turns an unquoted `2026-07-26` into a `datetime.date`. Every consumer wants a
    string, and quoting every date in every example would be churn for nothing, so accept
    both spellings and normalize here. The spec says ISO-8601; this is what enforces that
    one representation reaches the rest of the program.
    """
    if isinstance(value, dt.datetime):
        return value.date().isoformat()
    if isinstance(value, dt.date):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _normalize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalize(v) for v in value]
    return value


def split_frontmatter(text: str) -> tuple[str, str]:
    """Return (yaml_text, body). Empty yaml_text when there is no frontmatter block."""
    if not text.startswith("---"):
        return "", text
    lines = text.split("\n")
    for i in range(1, len(lines)):
        if lines[i].rstrip() == "---":
            return "\n".join(lines[1:i]), "\n".join(lines[i + 1 :])
    return "", text  # unterminated block: treat the whole file as body


def read_document(root: Path, path: Path) -> Document:
    text = path.read_text(encoding="utf-8")
    raw, body = split_frontmatter(text)
    rel = path.relative_to(root).as_posix()
    if not raw.strip():
        return Document(path, rel, {}, body, fm_error="no YAML frontmatter block")
    try:
        loaded = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        return Document(path, rel, {}, body, fm_error=f"unparseable YAML: {exc}")
    if not isinstance(loaded, dict):
        return Document(path, rel, {}, body, fm_error="frontmatter is not a mapping")
    return Document(path, rel, _normalize(loaded), body)


def discover(root: Path) -> Repo:
    root = Path(root)
    if not root.is_dir():
        raise AorfError(f"not a directory: {root}")
    repo = Repo(root=root)
    for path in sorted(root.rglob("*.md")):
        parts = path.relative_to(root).parts
        if any(p.startswith(".") for p in parts):
            continue
        if not is_document(root, path):
            continue
        if path.is_symlink() and not inside(root, path):
            continue
        doc = read_document(root, path)
        repo.docs.append(doc)
        repo.by_rel[doc.rel] = doc
    return repo


# --- link resolution (spec 3.3) ----------------------------------------------------------


def parent_hops(link: str) -> int:
    return sum(1 for seg in link.split("/") if seg == "..")


def resolve(root: Path, from_rel: str, link: str) -> Path:
    """Resolve a link as written in `from_rel`'s frontmatter.

    A leading `/` resolves from the repository root; anything else resolves relative to the
    containing document.
    """
    link = link.strip()
    if link.startswith("/"):
        return root / link.lstrip("/")
    base = (root / from_rel).parent
    return base / link


def resolve_rel(root: Path, from_rel: str, link: str) -> str | None:
    """Resolved link as a repo-relative posix path, or None when it escapes the repo."""
    target = resolve(root, from_rel, link)
    if not inside(root, target):
        return None
    try:
        return target.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()
    except ValueError:
        return None


# --- generated regions ------------------------------------------------------------------


def generated_region(body: str) -> tuple[int, int] | None:
    """Character span between the markers, exclusive of them, or None when absent."""
    start = body.find(spec.GEN_BEGIN)
    if start < 0:
        return None
    end = body.find(spec.GEN_END, start)
    if end < 0:
        return None
    return start + len(spec.GEN_BEGIN), end


def replace_generated(body: str, content: str) -> str:
    """Swap the generated region's contents, preserving everything outside the markers.

    Appends a fresh region when the markers are absent, so a hand-written synthesis picks
    up generation without anyone editing it.
    """
    span = generated_region(body)
    if span is None:
        sep = "" if body.endswith("\n") or not body else "\n"
        return f"{body}{sep}\n{spec.GEN_BEGIN}\n{content}\n{spec.GEN_END}\n"
    start, end = span
    return f"{body[:start]}\n{content}\n{body[end:]}"
