"""The views. One renderer, used by both `serve` and `build`.

Markdown is rendered with raw HTML disabled, so a document body cannot inject markup into
the dashboard's own origin. Artifact HTML is the only author-controlled markup that reaches
a browser, and it goes in a sandboxed frame.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown_it import MarkdownIt
from markupsafe import Markup

from .. import urls
from ..model import Model
from ..project import (
    blocking_findings,
    project,
    question_detail,
)
from . import artifacts as artifacts_mod
from . import charts

TEMPLATES = Path(__file__).parent / "templates"
STATIC = Path(__file__).parent / "static"


@lru_cache(maxsize=1)
def _markdown() -> MarkdownIt:
    # html=False escapes raw HTML rather than passing it through: spec 4.5.
    return (
        MarkdownIt("commonmark", {"html": False, "linkify": False, "typographer": False})
        .enable("table")
        .enable("strikethrough")
    )


_HREF = re.compile(r'href="([^"]+)"')


def md(text: str) -> Markup:
    """Rendered markdown, marked safe.

    Safe because the renderer runs with `html: False`, so raw HTML in a document body is
    escaped to text rather than passed through. Without the Markup wrapper Jinja would escape
    the tags this function just produced, and every prose block would render as its own
    source.
    """
    return Markup(_markdown().render(text or ""))


def _fmt(value, digits: int = 4) -> str:
    if value is None or value == "":
        return "—"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        return f"{value:.{digits}f}".rstrip("0").rstrip(".") or "0"
    return str(value)


def _fmt_delta(value) -> str:
    if value is None:
        return "—"
    return f"{'+' if value >= 0 else ''}{_fmt(value)}"


def _environment() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["md"] = md
    env.filters["num"] = _fmt
    env.filters["delta"] = _fmt_delta
    env.globals.update(
        urls=urls,
        page=urls.page,
        question_url=urls.question,
        experiment_url=urls.experiment,
        dataset_url=urls.dataset,
        finding_url=urls.finding,
        static_url=urls.static,
        progress_chart=charts.progress_chart,
        sweep_scatter=charts.sweep_scatter,
        delta_bar=charts.delta_bar,
    )
    return env


class Renderer:
    """Holds the model and hands out rendered pages by URL path."""

    def __init__(self, model: Model):
        self.model = model
        self.env = _environment()
        self.data = project(model)
        self._current = ""  # URL path being rendered, so nav can mark the current page
        self.blocking = blocking_findings(self.data)
        self.nav = [
            ("Overview", urls.page("index")),
            ("Hypotheses", urls.page("ledger")),
            ("Progress", urls.page("progress")),
            ("Datasets", urls.page("datasets")),
            ("Findings", urls.page("findings")),
        ]

    # -- helpers ------------------------------------------------------------------------
    @property
    def root(self) -> Path:
        return self.model.root

    def _base(self, **kwargs) -> dict:
        return {
            "research": self.data["research"],
            "nav": self.nav,
            "blocking": self.blocking,
            "aorf_version": self.data["aorf_version"],
            "request_path": self._current,
            **kwargs,
        }

    def _render(self, template: str, **context) -> str:
        return self.env.get_template(template).render(**self._base(**context))

    def _question_by_slug(self, slug: str):
        for q in self.model.all_questions.values():
            if urls.question_slug(q.rel) == slug:
                return q
        return None

    def _experiment_by_slug(self, slug: str):
        for e in self.model.experiments:
            if urls.experiment_slug(e.rel) == slug:
                return e
        return None

    def prose(self, doc_rel: str, text: str) -> Markup:
        """Rendered body markdown, with links to sibling documents pointed at their pages.

        An author writes `[001](./experiments/001-x/index.md)` because that is the link that
        works on GitHub. Left alone it 404s in the dashboard, so every cross-reference an
        author bothered to write would be broken here. Anything that does not resolve to a
        known document is left exactly as written.
        """
        html = md(text)

        def rewrite(match: re.Match) -> str:
            href = match.group(1)
            target, _, anchor = href.partition("#")
            if not target.endswith(".md") or "://" in target:
                return match.group(0)
            doc = self.model.resolve_doc(doc_rel, target)
            if doc is None:
                return match.group(0)
            url = urls.for_document(doc.rel, doc.type)
            return f'href="{url}{"#" + anchor if anchor else ""}"'

        return Markup(_HREF.sub(rewrite, str(html)))

    def _doc_link(self, from_rel: str, link: str) -> dict:
        """Turn a frontmatter path into a dashboard link, so cross-references are clickable."""
        doc = self.model.resolve_doc(from_rel, link)
        if doc is None:
            return {"url": "", "label": link, "resolved": False}
        return {
            "url": urls.for_document(doc.rel, doc.type),
            "label": str(doc.fm.get("title", doc.rel)),
            "resolved": True,
        }

    # -- pages --------------------------------------------------------------------------
    def overview(self) -> str:
        return self._render(
            "overview.html",
            questions=self.data["questions"],
            datasets=self.data["datasets"],
            findings=self.data["findings"],
            ledger=self.data["ledger"],
            research_body=self.prose(
                self.data["research"]["rel"], self.data["research"]["body"]
            ),
            log=(
                self.prose(self.data["research"]["rel"], self.data["log"])
                if self.data["log"]
                else ""
            ),
        )

    def ledger(self) -> str:
        rows = self.data["ledger"]
        verdicts = sorted({r["verdict"] for r in rows if r["verdict"]})
        return self._render(
            "ledger.html",
            rows=rows,
            verdicts=verdicts,
            questions=self.data["questions"],
        )

    def progress(self) -> str:
        panels = []
        for q in self.model.all_questions.values():
            detail = question_detail(self.model, q)
            panels.append(
                {
                    "title": detail["title"],
                    "url": urls.question(q.rel),
                    "series": detail["progress"],
                    "status": detail["status"],
                }
            )
        panels.sort(key=lambda p: p["title"])
        return self._render("progress.html", panels=panels)

    def datasets(self) -> str:
        by_rel = {d["rel"]: d for d in self.data["datasets"]}
        for d in self.data["datasets"]:
            for field in ("supersedes", "superseded_by"):
                d[f"{field}_link"] = (
                    self._doc_link(d["rel"], d[field]) if d[field] else None
                )
        return self._render("datasets.html", datasets=self.data["datasets"], by_rel=by_rel)

    def findings(self) -> str:
        for f in self.data["findings"]:
            f["affects_links"] = [self._doc_link(f["rel"], a) for a in f["affects"]]
        return self._render("findings.html", findings=self.data["findings"])

    def question(self, slug: str) -> str | None:
        q = self._question_by_slug(slug)
        if q is None:
            return None
        detail = question_detail(self.model, q)
        evidence = [
            self._doc_link(q.rel, link) for link in (q.doc.fm.get("answer_evidence") or [])
        ]
        return self._render(
            "question.html",
            q=detail,
            body=self.prose(q.rel, detail["body"]),
            prior_art_body=(
                self.prose(q.prior_art.rel, q.prior_art.body) if q.prior_art else ""
            ),
            evidence=evidence,
            synthesis_body=self.prose(q.synthesis.rel, q.synthesis.body) if q.synthesis else "",
            parent=(
                {
                    "url": urls.question(q.parent_rel),
                    "label": str(
                        self.model.repo.by_rel[q.parent_rel].fm.get("title", "")
                    ),
                }
                if q.parent_rel in self.model.all_questions
                else None
            ),
        )

    def experiment(self, slug: str) -> str | None:
        e = self._experiment_by_slug(slug)
        if e is None:
            return None
        from ..project import experiment_row

        row = experiment_row(self.model, e)
        found = artifacts_mod.discover(self.root, e.doc.dir)
        rendered = [
            {
                "artifact": a,
                "html": artifacts_mod.render(self.root, a, md),
            }
            for a in found
        ]
        runs = (
            artifacts_mod.runs_for(self.root, f"{e.doc.dir}/{row['runs'].lstrip('./')}")
            if row["runs"]
            else []
        )
        question = self.model.all_questions.get(e.question_rel or "")
        links = {
            name: self._doc_link(e.rel, value)
            for name, value in (
                ("baseline", row["baseline"] if e.has_baseline else ""),
                ("invalidated_by", str(e.doc.fm.get("invalidated_by", ""))),
                ("supersedes", str(e.doc.fm.get("supersedes", ""))),
                ("superseded_by", str(e.doc.fm.get("superseded_by", ""))),
                ("retests", str(e.doc.fm.get("retests", ""))),
            )
            if value
        }
        datasets = []
        for ref in e.doc.fm.get("datasets") or []:
            if not isinstance(ref, dict):
                continue
            written = str(ref.get("path", ""))
            doc = self.model.resolve_doc(e.rel, written)
            datasets.append(
                {
                    **self._doc_link(e.rel, written),
                    "role": str(ref.get("role", "")),
                    "version": str(doc.fm.get("version", "")) if doc else "",
                    "status": str(doc.fm.get("status", "")) if doc else "",
                }
            )
        return self._render(
            "experiment.html",
            e=row,
            body=self.prose(e.rel, e.doc.body),
            artifacts=rendered,
            runs=runs,
            scatter=charts.sweep_scatter(runs, row["primary"]["name"] if row["primary"] else ""),
            links=links,
            datasets=datasets,
            also_informs=[
                self._doc_link(e.rel, x) for x in (e.doc.fm.get("also_informs") or [])
            ],
            question=(
                {"url": urls.question(question.rel), "label": str(question.doc.fm.get("title", ""))}
                if question
                else None
            ),
        )

    def dataset(self, slug: str) -> str | None:
        match = next((d for d in self.data["datasets"] if urls.doc_slug(d["rel"]) == slug), None)
        if match is None:
            return None
        for field in ("supersedes", "superseded_by"):
            match[f"{field}_link"] = (
                self._doc_link(match["rel"], match[field]) if match[field] else None
            )
        used_by = []
        for e in self.model.experiments:
            for ref in e.doc.fm.get("datasets") or []:
                if not isinstance(ref, dict):
                    continue
                doc = self.model.resolve_doc(e.rel, str(ref.get("path", "")))
                if doc is not None and doc.rel == match["rel"]:
                    used_by.append(
                        {
                            "url": urls.experiment(e.rel),
                            "label": str(e.doc.fm.get("title", "")),
                            "id": e.id,
                            "role": str(ref.get("role", "")),
                        }
                    )
                    break
        return self._render(
            "dataset.html",
            d=match,
            body=self.prose(match["rel"], match["body"]),
            used_by=used_by,
        )

    def finding(self, slug: str) -> str | None:
        match = next((f for f in self.data["findings"] if urls.doc_slug(f["rel"]) == slug), None)
        if match is None:
            return None
        match["affects_links"] = [self._doc_link(match["rel"], a) for a in match["affects"]]
        return self._render("finding.html", f=match, body=self.prose(match["rel"], match["body"]))

    # -- dispatch -----------------------------------------------------------------------
    def page_for(self, path: str) -> str | None:
        """Render the page at a URL path, or None when there is nothing there."""
        path = path or "/"
        self._current = "/index.html" if path == "/" else path
        if path in ("/", "/index.html"):
            return self.overview()
        if not path.startswith("/") or not path.endswith(".html"):
            return None
        name = path[1:-len(".html")]
        simple = {
            "ledger": self.ledger,
            "progress": self.progress,
            "datasets": self.datasets,
            "findings": self.findings,
        }
        if name in simple:
            return simple[name]()
        for prefix, handler in (
            ("question-", self.question),
            ("experiment-", self.experiment),
            ("dataset-", self.dataset),
            ("finding-", self.finding),
        ):
            if name.startswith(prefix):
                return handler(name[len(prefix) :])
        return None

    def all_paths(self) -> list[str]:
        """Every page the static export must write."""
        pages = ("ledger", "progress", "datasets", "findings")
        paths = ["/index.html"] + [urls.page(p) for p in pages]
        paths += [urls.question(q.rel) for q in self.model.all_questions.values()]
        paths += [urls.experiment(e.rel) for e in self.model.experiments]
        paths += [urls.dataset(d["rel"]) for d in self.data["datasets"]]
        paths += [urls.finding(f["rel"]) for f in self.data["findings"]]
        return paths

    def static_files(self) -> list[Path]:
        return [p for p in sorted(STATIC.iterdir()) if p.is_file()]
