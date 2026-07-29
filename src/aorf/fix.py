"""`check --fix`: refresh derived content, never hand-written prose.

Two things are derived and therefore fixable: the generated region of each `synthesis.md`,
and each metric's `baseline_value`. Everything else is a human's sentence and stays exactly
as written, including unknown fields, which OKF requires consumers to preserve.

The frontmatter rewrite here is deliberately textual rather than a YAML round-trip. Dumping
a parsed document back through pyyaml would reorder keys, restyle quoting, and expand flow
mappings — a diff touching every line of a file where one number changed. A line-scoped
substitution keeps the diff honest.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from . import parse
from .model import Model
from .project import synthesis_body, synthesis_status


@dataclass
class FixResult:
    changed: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def any(self) -> bool:
        return bool(self.changed)


def _write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _render_document(fm_text: str, body: str) -> str:
    return f"---\n{fm_text.strip()}\n---\n{body}"


def _frontmatter_text(path: Path) -> tuple[str, str]:
    raw = path.read_text(encoding="utf-8")
    fm, body = parse.split_frontmatter(raw)
    return fm, body


_STATUS_LINE = re.compile(r"^status:.*$", re.MULTILINE)


def fix_synthesis(m: Model, result: FixResult) -> None:
    for q in m.all_questions.values():
        if q.synthesis is None:
            continue
        fm_text, body = _frontmatter_text(q.synthesis.path)
        want_body = parse.replace_generated(body, synthesis_body(m, q))
        want_status = synthesis_status(q)

        new_fm = fm_text
        if _STATUS_LINE.search(fm_text):
            new_fm = _STATUS_LINE.sub(f"status: {want_status}", fm_text, count=1)
        else:
            new_fm = f"{fm_text.rstrip()}\nstatus: {want_status}"

        if want_body != body or new_fm.strip() != fm_text.strip():
            _write(q.synthesis.path, _render_document(new_fm, want_body))
            result.changed.append(q.synthesis.rel)


def _replace_baseline_value(fm_text: str, metric_name: str, value: float) -> str | None:
    """Rewrite the `baseline_value:` belonging to one named metric in a metrics list.

    Walks the list item by item so a repo with several metrics updates only the right one.
    Returns None when the metric or its baseline_value line cannot be located, in which case
    the caller leaves the file alone and the checker keeps reporting it — silently doing
    nothing would be worse than a persistent error.
    """
    lines = fm_text.split("\n")
    start = None
    for i, line in enumerate(lines):
        if re.match(rf"^\s*-\s+name:\s*{re.escape(metric_name)}\s*$", line):
            start = i
            break
    if start is None:
        return None
    indent = len(lines[start]) - len(lines[start].lstrip())
    for j in range(start + 1, len(lines)):
        line = lines[j]
        if line.strip() and (len(line) - len(line.lstrip())) <= indent:
            break  # next list item or next key: the metric block ended
        if re.match(r"^\s*baseline_value:", line):
            pad = " " * (len(line) - len(line.lstrip()))
            formatted = f"{value:g}"
            lines[j] = f"{pad}baseline_value: {formatted}"
            return "\n".join(lines)
    return None


def fix_baseline_values(m: Model, result: FixResult) -> None:
    """Bring every denormalized baseline_value back in line with its source.

    Skips invalidated experiments, matching R12 and R21: the baseline of an invalidated
    result is not a number worth restoring.
    """
    by_rel = {e.rel: e for e in m.experiments}
    for e in m.experiments:
        if not e.has_baseline or not e.is_current:
            continue
        target = m.resolve_doc(e.rel, e.baseline_raw)
        base = by_rel.get(target.rel) if target else None
        if base is None:
            continue
        base_values = {x.name: x.value for x in base.metrics}
        pending: list[tuple[str, float]] = []
        for metric in e.metrics:
            theirs = base_values.get(metric.name)
            if theirs is None or metric.baseline_value is None:
                continue
            if abs(theirs - metric.baseline_value) > 1e-9:
                pending.append((metric.name, theirs))
        if not pending:
            continue
        fm_text, body = _frontmatter_text(e.doc.path)
        updated = fm_text
        applied = []
        for name, value in pending:
            attempt = _replace_baseline_value(updated, name, value)
            if attempt is None:
                result.notes.append(
                    f"{e.rel}: could not locate baseline_value for metric {name!r}; fix it by "
                    f"hand"
                )
                continue
            updated = attempt
            applied.append(name)
        if applied:
            _write(e.doc.path, _render_document(updated, body))
            result.changed.append(e.rel)


def apply(path: Path | str) -> FixResult:
    """Refresh derived content, then report what moved.

    Runs to a fixed point in one pass: baseline_values first, because a corrected delta
    changes what the synthesis tables say.
    """
    from .model import load

    result = FixResult()
    m = load(path)
    fix_baseline_values(m, result)
    m = load(path)  # re-read so synthesis sees the corrected numbers
    fix_synthesis(m, result)
    return result
