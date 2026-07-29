"""Typed views over the discovered documents, plus the question tree.

Construction never fails on a broken repo: a missing parent or an unresolvable link leaves
a hole that `check.py` reports. A model that refused to build would make the checker
useless exactly when it is needed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from . import parse, spec
from .parse import Document, Repo


@dataclass
class Metric:
    name: str
    value: float | None
    direction: str
    baseline_value: float | None = None
    primary: bool = False
    unit: str = ""
    n: float | None = None
    ci: list[float] = field(default_factory=list)
    std: float | None = None

    @property
    def delta(self) -> float | None:
        """Signed improvement over the baseline, positive meaning better.

        Direction-aware, so a lower_is_better metric that went down reads as a gain. Every
        consumer must use this rather than subtracting by hand.
        """
        if self.value is None or self.baseline_value is None:
            return None
        raw = self.value - self.baseline_value
        return raw if self.direction == "higher_is_better" else -raw


def _num(v) -> float | None:
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def metrics_of(doc: Document) -> list[Metric]:
    out = []
    for entry in doc.fm.get("metrics") or []:
        if not isinstance(entry, dict):
            continue
        ci = entry.get("ci")
        out.append(
            Metric(
                name=str(entry.get("name", "")),
                value=_num(entry.get("value")),
                direction=str(entry.get("direction", "")),
                baseline_value=_num(entry.get("baseline_value")),
                primary=bool(entry.get("primary")),
                unit=str(entry.get("unit", "")),
                n=_num(entry.get("n")),
                ci=[float(x) for x in ci] if isinstance(ci, list) else [],
                std=_num(entry.get("std")),
            )
        )
    return out


def primary_metric(doc: Document) -> Metric | None:
    ms = metrics_of(doc)
    for m in ms:
        if m.primary:
            return m
    return ms[0] if len(ms) == 1 else None


@dataclass
class Experiment:
    doc: Document
    question_rel: str | None

    @property
    def rel(self) -> str:
        return self.doc.rel

    @property
    def id(self) -> str:
        """The `NNN-slug` directory name, which is what humans call the experiment."""
        return Path(self.doc.dir).name

    @property
    def kind(self) -> str:
        return str(self.doc.fm.get("kind", ""))

    @property
    def status(self) -> str:
        return str(self.doc.fm.get("research_status", ""))

    @property
    def verdict(self) -> str:
        return str(self.doc.fm.get("verdict", ""))

    @property
    def verdict_state(self) -> str:
        return str(self.doc.fm.get("verdict_state", "current"))

    @property
    def is_current(self) -> bool:
        """Whether this result may inform the current best.

        An invalidated or superseded experiment stays in the hypothesis ledger — that it was
        tried is permanent knowledge — but must never feed a headline number.
        """
        return self.verdict_state == "current"

    @property
    def hypothesis(self) -> str:
        return str(self.doc.fm.get("hypothesis", ""))

    @property
    def baseline_raw(self) -> str:
        return str(self.doc.fm.get("baseline", ""))

    @property
    def has_baseline(self) -> bool:
        return self.baseline_raw not in ("", "none")

    @property
    def metrics(self) -> list[Metric]:
        return metrics_of(self.doc)

    @property
    def primary(self) -> Metric | None:
        return primary_metric(self.doc)

    @property
    def run_date(self) -> str:
        return str(self.doc.fm.get("run_date", ""))

    @property
    def dataset_versions(self) -> list[str]:
        """Versions of the eval datasets, which is what comparability turns on."""
        return sorted(
            {v for v in (self._dataset_version(d) for d in self._dataset_refs("eval")) if v}
        )

    def _dataset_refs(self, role: str | None = None) -> list[dict]:
        refs = [d for d in (self.doc.fm.get("datasets") or []) if isinstance(d, dict)]
        return [d for d in refs if role is None or d.get("role") == role]

    def _dataset_version(self, ref: dict) -> str:
        return str(self._resolved_datasets.get(str(ref.get("path", "")), ""))

    # Filled by Model.build once every dataset document is known.
    _resolved_datasets: dict[str, str] = field(default_factory=dict)


@dataclass
class Question:
    doc: Document
    parent_rel: str | None
    experiments: list[Experiment] = field(default_factory=list)
    children: list[Question] = field(default_factory=list)
    synthesis: Document | None = None
    prior_art: Document | None = None

    @property
    def rel(self) -> str:
        return self.doc.rel

    @property
    def slug(self) -> str:
        return Path(self.doc.dir).name

    @property
    def status(self) -> str:
        return str(self.doc.fm.get("research_status", ""))

    @property
    def primary_metric(self) -> str:
        return str(self.doc.fm.get("primary_metric", ""))

    @property
    def metric_direction(self) -> str:
        return str(self.doc.fm.get("metric_direction", ""))

    @property
    def metric_target(self) -> float | None:
        return _num(self.doc.fm.get("metric_target"))

    @property
    def depth(self) -> int:
        return self.doc.depth

    def walk(self):
        yield self
        for child in self.children:
            yield from child.walk()

    @property
    def current_experiments(self) -> list[Experiment]:
        return [e for e in self.experiments if e.is_current]

    @property
    def best(self) -> tuple[Experiment, Metric] | None:
        """Best current, completed, non-baseline result by direction-aware delta.

        Falls back to raw value when nothing carries a baseline, so a question with
        `baseline: none` throughout still shows a leader.
        """
        candidates = [
            (e, e.primary)
            for e in self.current_experiments
            if e.status == "done" and e.kind != "baseline" and e.primary is not None
        ]
        if not candidates:
            return None
        with_delta = [(e, m) for e, m in candidates if m.delta is not None]
        if with_delta:
            return max(with_delta, key=lambda p: p[1].delta)
        scored = [(e, m) for e, m in candidates if m.value is not None]
        if not scored:
            return None
        lower_better = scored[0][1].direction == "lower_is_better"
        return min(scored, key=lambda p: p[1].value) if lower_better else max(
            scored, key=lambda p: p[1].value
        )

    @property
    def baseline(self) -> Experiment | None:
        for e in self.experiments:
            if e.kind == "baseline":
                return e
        return None


@dataclass
class Model:
    repo: Repo
    research: Document | None = None
    questions: list[Question] = field(default_factory=list)  # roots
    all_questions: dict[str, Question] = field(default_factory=dict)
    experiments: list[Experiment] = field(default_factory=list)
    datasets: list[Document] = field(default_factory=list)
    findings: list[Document] = field(default_factory=list)
    log: str = ""

    @property
    def root(self) -> Path:
        return self.repo.root

    def resolve_doc(self, from_rel: str, link: str) -> Document | None:
        rel = parse.resolve_rel(self.root, from_rel, link)
        return self.repo.by_rel.get(rel) if rel else None

    def experiments_of(self, question_rel: str) -> list[Experiment]:
        q = self.all_questions.get(question_rel)
        return q.experiments if q else []

    @property
    def tag_vocabulary(self) -> list[str]:
        if not self.research:
            return []
        v = self.research.fm.get("tag_vocabulary")
        return [str(x) for x in v] if isinstance(v, list) else []


def build(repo: Repo) -> Model:
    m = Model(repo=repo)
    by_type: dict[str, list[Document]] = {}
    for doc in repo.docs:
        by_type.setdefault(doc.type, []).append(doc)

    roots = by_type.get("research", [])
    m.research = next((d for d in roots if d.rel == "index.md"), roots[0] if roots else None)
    m.datasets = by_type.get("dataset", [])
    m.findings = by_type.get("finding", [])

    log = repo.root / "log.md"
    if log.is_file() and parse.inside(repo.root, log):
        m.log = log.read_text(encoding="utf-8")

    dataset_version_by_rel = {d.rel: str(d.fm.get("version", "")) for d in m.datasets}

    for doc in by_type.get("question", []):
        parent = doc.fm.get("parent")
        parent_rel = (
            parse.resolve_rel(repo.root, doc.rel, str(parent)) if isinstance(parent, str) else None
        )
        q = Question(doc=doc, parent_rel=parent_rel)
        m.all_questions[doc.rel] = q

    for doc in by_type.get("experiment", []):
        link = doc.fm.get("question")
        q_rel = parse.resolve_rel(repo.root, doc.rel, str(link)) if isinstance(link, str) else None
        exp = Experiment(doc=doc, question_rel=q_rel)
        # Map each dataset reference, as written, to that dataset's version, so
        # comparability can be checked without re-resolving links downstream.
        for ref in exp._dataset_refs():
            written = str(ref.get("path", ""))
            resolved = parse.resolve_rel(repo.root, doc.rel, written)
            exp._resolved_datasets[written] = dataset_version_by_rel.get(resolved or "", "")
        m.experiments.append(exp)
        if q_rel and q_rel in m.all_questions:
            m.all_questions[q_rel].experiments.append(exp)

    for q in m.all_questions.values():
        q.experiments.sort(key=lambda e: e.id)

    for doc in by_type.get("synthesis", []):
        link = doc.fm.get("question")
        rel = parse.resolve_rel(repo.root, doc.rel, str(link)) if isinstance(link, str) else None
        if rel in m.all_questions:
            m.all_questions[rel].synthesis = doc

    for doc in by_type.get("prior-art", []):
        link = doc.fm.get("question")
        rel = parse.resolve_rel(repo.root, doc.rel, str(link)) if isinstance(link, str) else None
        if rel in m.all_questions:
            m.all_questions[rel].prior_art = doc

    # A question whose parent is another question is nested under it; everything else,
    # including a question with a dangling parent, is a root so it stays visible.
    for q in m.all_questions.values():
        parent = m.all_questions.get(q.parent_rel or "")
        if parent is not None and parent is not q:
            parent.children.append(q)
        else:
            m.questions.append(q)
    for q in m.all_questions.values():
        q.children.sort(key=lambda c: c.slug)
    m.questions.sort(key=lambda c: c.slug)
    return m


def load(path: Path | str) -> Model:
    return build(parse.discover(Path(path)))


def default_depth_limits() -> tuple[int, int]:
    return spec.DEPTH_WARN, spec.DEPTH_ERROR
