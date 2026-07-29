"""Artifact rendering, dispatched by extension.

MLflow's artifact viewer is the reference for this list and for putting user HTML in a
sandboxed iframe. The security posture: nothing here executes anything, user HTML never runs
same-origin, SVG is treated as active content because it can carry script, and anything over
the size cap becomes a download link rather than a page that takes a second to paint.
"""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from html import escape
from pathlib import Path

from .. import urls

MAX_INLINE_BYTES = 512 * 1024
MAX_TABLE_ROWS = 200

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
CODE_EXT = {".txt", ".log", ".py", ".sql", ".yaml", ".yml", ".sh", ".toml", ".ini", ".jsonl"}
TABLE_EXT = {".csv", ".tsv"}


@dataclass
class Artifact:
    repo_rel: str  # path relative to the repository root
    name: str
    size: int
    ext: str

    @property
    def url(self) -> str:
        return urls.artifact(self.repo_rel)

    @property
    def kind(self) -> str:
        if self.ext in IMAGE_EXT:
            return "image"
        if self.ext == ".svg":
            return "svg"
        if self.ext == ".html":
            return "html"
        if self.ext in TABLE_EXT:
            return "table"
        if self.ext == ".md":
            return "markdown"
        if self.ext == ".json":
            return "json"
        if self.ext == ".pdf":
            return "pdf"
        if self.ext in CODE_EXT:
            return "code"
        return "download"


def discover(root: Path, experiment_dir: str) -> list[Artifact]:
    """Everything under the experiment's `artifacts/`, recursively.

    Discovery is by location, not by frontmatter: "all outputs go in artifacts/" is what
    makes this possible without anyone maintaining a list.
    """
    base = root / experiment_dir / "artifacts"
    if not base.is_dir():
        return []
    out = []
    for path in sorted(base.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        try:
            rel = path.relative_to(root).as_posix()
        except ValueError:
            continue
        out.append(
            Artifact(
                repo_rel=rel,
                name=path.relative_to(base).as_posix(),
                size=path.stat().st_size,
                ext=path.suffix.lower(),
            )
        )
    return out


def _size_label(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.0f} KB"
    return f"{n / (1024 * 1024):.1f} MB"


def _too_big(a: Artifact) -> str:
    return (
        f'<p class="empty">{escape(a.name)} is {_size_label(a.size)}, over the inline limit. '
        f'<a href="{a.url}" download>Download</a> it instead.</p>'
    )


def _table(text: str, delimiter: str) -> str:
    rows = list(csv.reader(io.StringIO(text), delimiter=delimiter))
    if not rows:
        return '<p class="empty">Empty table.</p>'
    head, body = rows[0], rows[1:]
    shown = body[:MAX_TABLE_ROWS]
    out = ['<div class="scroll"><table class="data sortable"><thead><tr>']
    out += [f"<th>{escape(c)}</th>" for c in head]
    out.append("</tr></thead><tbody>")
    for row in shown:
        out.append("<tr>" + "".join(f"<td>{escape(c)}</td>" for c in row) + "</tr>")
    out.append("</tbody></table></div>")
    if len(body) > len(shown):
        out.append(
            f'<p class="empty">{len(body) - len(shown)} more row(s) not shown.</p>'
        )
    return "".join(out)


def _runs_table(text: str) -> tuple[str, list[dict]]:
    """`runs.jsonl` gets a sortable table plus a scatter, per spec 4.4."""
    runs: list[dict] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(entry, dict):
            runs.append(entry)
    if not runs:
        return '<p class="empty">No runs parsed.</p>', []

    param_keys, metric_keys = [], []
    for run in runs:
        for k in (run.get("params") or {}):
            if k not in param_keys:
                param_keys.append(k)
        for k in (run.get("metrics") or {}):
            if k not in metric_keys:
                metric_keys.append(k)

    out = ['<div class="scroll"><table class="data sortable"><thead><tr><th>run</th>']
    out += [f"<th>{escape(k)}</th>" for k in param_keys]
    out += [f'<th class="num">{escape(k)}</th>' for k in metric_keys]
    out.append("<th>status</th></tr></thead><tbody>")
    for run in runs[:MAX_TABLE_ROWS]:
        params, metrics = run.get("params") or {}, run.get("metrics") or {}
        out.append(f'<tr><td class="mono">{escape(str(run.get("run_id", "")))}</td>')
        out += [f"<td>{escape(str(params.get(k, '')))}</td>" for k in param_keys]
        out += [f'<td class="num">{escape(str(metrics.get(k, "")))}</td>' for k in metric_keys]
        out.append(f"<td>{escape(str(run.get('status', '')))}</td></tr>")
    out.append("</tbody></table></div>")
    if len(runs) > MAX_TABLE_ROWS:
        out.append(f'<p class="empty">{len(runs) - MAX_TABLE_ROWS} more run(s) not shown.</p>')
    return "".join(out), runs


def render(root: Path, a: Artifact, md_render) -> str:
    """One artifact as an HTML fragment. `md_render` is injected to avoid a circular import."""
    if a.size > MAX_INLINE_BYTES and a.kind not in ("image", "pdf", "html"):
        return _too_big(a)

    if a.kind == "image":
        return (
            f'<img class="artifact-image" src="{a.url}" alt="{escape(a.name)}" loading="lazy">'
        )

    if a.kind == "svg":
        # SVG can carry script, so it is framed rather than inlined. Inlining it would put
        # author-controlled markup directly in the dashboard's own origin.
        return (
            f'<iframe class="artifact-frame" src="{a.url}" title="{escape(a.name)}" '
            f'sandbox loading="lazy"></iframe>'
        )

    if a.kind == "html":
        # allow-scripts without allow-same-origin: the frame runs in an opaque origin, so it
        # cannot touch the dashboard, its storage, or its DOM.
        return (
            f'<iframe class="artifact-frame tall" src="{a.url}" title="{escape(a.name)}" '
            f'sandbox="allow-scripts" loading="lazy"></iframe>'
        )

    if a.kind == "pdf":
        return (
            f'<object class="artifact-frame tall" data="{a.url}" type="application/pdf">'
            f'<p class="empty">Inline PDF is unavailable. '
            f'<a href="{a.url}" download>Download {escape(a.name)}</a>.</p></object>'
        )

    path = root / a.repo_rel
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return f'<p class="empty">Could not read {escape(a.name)}.</p>'

    if a.kind == "table":
        return _table(text, "\t" if a.ext == ".tsv" else ",")

    if a.kind == "markdown":
        return f'<div class="prose">{md_render(text)}</div>'

    if a.kind == "json":
        if a.name.endswith("runs.jsonl"):
            table, _ = _runs_table(text)
            return table
        try:
            pretty = json.dumps(json.loads(text), indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            pretty = text
        return f'<pre class="code">{escape(pretty)}</pre>'

    if a.kind == "code":
        if a.name.endswith(".jsonl"):
            table, _ = _runs_table(text)
            if table:
                return table
        return f'<pre class="code">{escape(text)}</pre>'

    return (
        f'<p class="empty"><a href="{a.url}" download>Download {escape(a.name)}</a> '
        f"({_size_label(a.size)})</p>"
    )


def runs_for(root: Path, repo_rel: str) -> list[dict]:
    """Parsed runs.jsonl, for the sweep scatter. Empty on anything unreadable."""
    path = root / repo_rel
    if not path.is_file():
        return []
    _, runs = _runs_table(path.read_text(encoding="utf-8", errors="replace"))
    return runs


def content_type(ext: str) -> str:
    return {
        ".html": "text/html; charset=utf-8",
        ".svg": "image/svg+xml",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".pdf": "application/pdf",
        ".csv": "text/csv; charset=utf-8",
        ".tsv": "text/tab-separated-values; charset=utf-8",
        ".json": "application/json; charset=utf-8",
        ".jsonl": "application/x-ndjson; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".js": "text/javascript; charset=utf-8",
        ".md": "text/markdown; charset=utf-8",
    }.get(ext.lower(), "application/octet-stream")
