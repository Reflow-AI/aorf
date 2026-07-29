"""The dashboard projection: pure data, no HTML.

This is the contract the dashboard depends on and the thing `show --json` hands an agent, so
it is testable on its own and deterministic — nothing here reads the clock, or the golden
snapshots would churn daily.

Every derivation an agent is told to reproduce in AGENTS.md is implemented exactly once,
here: comparability grouping, direction-aware deltas, invalidation handling, sweep best-run
selection.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from . import spec
from .model import Experiment, Metric, Model, Question


def _metric_dict(m: Metric | None) -> dict | None:
    if m is None:
        return None
    return {
        "name": m.name,
        "value": m.value,
        "direction": m.direction,
        "baseline_value": m.baseline_value,
        "delta": m.delta,
        "unit": m.unit,
        "n": m.n,
        "ci": m.ci or None,
        "std": m.std,
    }


def _last_activity(e: Experiment) -> str:
    return e.run_date or str(e.doc.fm.get("timestamp", ""))


# --- comparability -----------------------------------------------------------------------


@dataclass(frozen=True)
class GroupKey:
    metric: str
    dataset_version: str
    baseline: str

    def label(self) -> str:
        parts = [self.metric or "no metric"]
        parts.append(f"dataset {self.dataset_version}" if self.dataset_version else "no dataset")
        parts.append("no baseline" if self.baseline in ("", "none") else "vs baseline")
        return ", ".join(parts)


def group_key(m: Model, e: Experiment) -> GroupKey:
    """`(primary_metric, dataset_version, baseline)` — spec 3.10.

    Numbers from different groups never share a column, because they are not comparable.
    """
    primary = e.primary
    versions = e.dataset_versions
    baseline_rel = ""
    if e.kind == "baseline":
        # A baseline is the reference for its own group, so it sits in the table it
        # anchors rather than in a lonely "no baseline" group of one. Its `baseline: none`
        # describes how it was produced, not what it should be compared against.
        baseline_rel = e.rel
    elif e.has_baseline:
        target = m.resolve_doc(e.rel, e.baseline_raw)
        baseline_rel = target.rel if target else e.baseline_raw
    return GroupKey(
        metric=primary.name if primary else "",
        dataset_version=", ".join(versions),
        baseline=baseline_rel or "none",
    )


def comparability_groups(m: Model, q: Question) -> list[dict]:
    """Experiment rows partitioned into comparable sets, most populated group first."""
    buckets: dict[GroupKey, list[Experiment]] = {}
    for e in q.experiments:
        buckets.setdefault(group_key(m, e), []).append(e)

    groups = []
    for key, exps in buckets.items():
        rows = [experiment_row(m, e) for e in exps]
        groups.append(
            {
                "key": {
                    "metric": key.metric,
                    "dataset_version": key.dataset_version,
                    "baseline": key.baseline,
                },
                "label": key.label(),
                # A group is struck through when nothing in it may inform the current best.
                "invalidated": all(not e.is_current for e in exps),
                "rows": rows,
            }
        )
    groups.sort(key=lambda g: (-len(g["rows"]), g["label"]))
    return groups


def experiment_row(m: Model, e: Experiment) -> dict:
    return {
        "rel": e.rel,
        "id": e.id,
        "title": str(e.doc.fm.get("title", "")),
        "description": str(e.doc.fm.get("description", "")),
        "kind": e.kind,
        "status": e.status,
        "status_reason": str(e.doc.fm.get("research_status_reason", "")),
        "verdict": e.verdict,
        "verdict_scope": str(e.doc.fm.get("verdict_scope", "")),
        "verdict_state": e.verdict_state,
        "verdict_basis": str(e.doc.fm.get("verdict_basis", "")),
        "invalidation_reason": str(e.doc.fm.get("invalidation_reason", "")),
        "retest_reason": str(e.doc.fm.get("retest_reason", "")),
        "hypothesis": e.hypothesis,
        "baseline": e.baseline_raw,
        "baseline_reason": str(e.doc.fm.get("baseline_reason", "")),
        "primary": _metric_dict(e.primary),
        "metrics": [_metric_dict(x) for x in e.metrics],
        "dataset_versions": e.dataset_versions,
        "run_date": e.run_date,
        "owner": str(e.doc.fm.get("owner", "")),
        "tags": [str(t) for t in (e.doc.fm.get("tags") or [])],
        "tracker": str(e.doc.fm.get("tracker", "")),
        "cost_usd": e.doc.fm.get("cost_usd"),
        "runtime_s": e.doc.fm.get("runtime_s"),
        "run_count": e.doc.fm.get("run_count"),
        "best_run": str(e.doc.fm.get("best_run", "")),
        "runs": str(e.doc.fm.get("runs", "")),
        "models": [x for x in (e.doc.fm.get("models") or []) if isinstance(x, dict)],
        "code": e.doc.fm.get("code") if isinstance(e.doc.fm.get("code"), dict) else {},
        "env": e.doc.fm.get("env") if isinstance(e.doc.fm.get("env"), dict) else {},
        "nondeterministic": bool(e.doc.fm.get("nondeterministic")),
        "repeats": e.doc.fm.get("repeats"),
        "last_activity": _last_activity(e),
    }


# --- question rollups --------------------------------------------------------------------


def question_row(m: Model, q: Question) -> dict:
    best = q.best
    tested = [e for e in q.experiments if e.hypothesis]
    invalidated = [e for e in q.experiments if not e.is_current]
    activity = [a for a in (_last_activity(e) for e in q.experiments) if a]
    baseline = q.baseline
    baseline_primary = baseline.primary if baseline else None

    # With no baseline there is no delta, so the question's target becomes the reference.
    reference = None
    if baseline_primary is not None and baseline_primary.value is not None:
        reference = {"kind": "baseline", "value": baseline_primary.value, "rel": baseline.rel}
    elif q.metric_target is not None:
        reference = {"kind": "target", "value": q.metric_target, "rel": ""}

    return {
        "rel": q.rel,
        "slug": q.slug,
        "title": str(q.doc.fm.get("title", "")),
        "description": str(q.doc.fm.get("description", "")),
        "status": q.status,
        "depth": q.depth,
        "primary_metric": q.primary_metric,
        "metric_direction": q.metric_direction,
        "metric_target": q.metric_target,
        "reference": reference,
        "owner": str(q.doc.fm.get("owner", "")),
        "tracker": str(q.doc.fm.get("tracker", "")),
        "tags": [str(t) for t in (q.doc.fm.get("tags") or [])],
        "answer": str(q.doc.fm.get("answer", "")),
        "closed_reason": str(q.doc.fm.get("closed_reason", "")),
        "experiment_count": len(q.experiments),
        "hypotheses_tested": len(tested),
        "invalidated_count": len(invalidated),
        "best": (
            {
                "rel": best[0].rel,
                "id": best[0].id,
                "title": str(best[0].doc.fm.get("title", "")),
                "metric": _metric_dict(best[1]),
            }
            if best
            else None
        ),
        "prior_art": (
            {
                "rel": q.prior_art.rel,
                "conclusion": str(q.prior_art.fm.get("conclusion", "")),
                "searched_on": str(q.prior_art.fm.get("searched_on", "")),
                "valid_until": str(q.prior_art.fm.get("valid_until", "")),
                "cost_usd": q.prior_art.fm.get("cost_usd"),
            }
            if q.prior_art
            else None
        ),
        "synthesis": q.synthesis.rel if q.synthesis else "",
        "last_activity": max(activity) if activity else "",
        "children": [c.rel for c in q.children],
    }


def question_detail(m: Model, q: Question) -> dict:
    row = question_row(m, q)
    row["groups"] = comparability_groups(m, q)
    row["progress"] = progress_series(m, q)
    row["body"] = q.doc.body
    row["prior_art_body"] = q.prior_art.body if q.prior_art else ""
    row["child_rows"] = [question_row(m, c) for c in q.children]
    return row


def progress_series(m: Model, q: Question) -> dict:
    """Primary metric over run_date, with a reference line.

    Only current, dated, primary-metric-bearing experiments plot; an invalidated point would
    draw a trend that is not real.
    """
    points = []
    for e in q.experiments:
        metric = e.primary
        if not e.is_current or metric is None or metric.value is None or not e.run_date:
            continue
        if q.primary_metric and metric.name != q.primary_metric:
            continue
        points.append(
            {
                "rel": e.rel,
                "id": e.id,
                "date": e.run_date,
                "value": metric.value,
                "kind": e.kind,
                "verdict": e.verdict,
            }
        )
    points.sort(key=lambda p: (p["date"], p["id"]))
    return {
        "metric": q.primary_metric,
        "direction": q.metric_direction or "higher_is_better",
        "reference": question_row(m, q)["reference"],
        "points": points,
    }


# --- ledger ------------------------------------------------------------------------------


def ledger(m: Model) -> list[dict]:
    """Every hypothesis in the repo, one flat list.

    The answer to "which hypotheses have we tried". Invalidated entries stay in, with their
    reason, because that a thing was tried is permanent even when the number is not.
    """
    rows = []
    for q in m.all_questions.values():
        for e in q.experiments:
            if not e.hypothesis:
                continue
            metric = e.primary
            rows.append(
                {
                    "rel": e.rel,
                    "id": e.id,
                    "hypothesis": e.hypothesis,
                    "verdict": e.verdict,
                    "verdict_state": e.verdict_state,
                    "verdict_scope": str(e.doc.fm.get("verdict_scope", "")),
                    "invalidation_reason": str(e.doc.fm.get("invalidation_reason", "")),
                    "kind": e.kind,
                    "status": e.status,
                    "question_rel": q.rel,
                    "question_title": str(q.doc.fm.get("title", "")),
                    "metric": _metric_dict(metric),
                    "run_date": e.run_date,
                    "owner": str(e.doc.fm.get("owner", "")),
                    "tags": [str(t) for t in (e.doc.fm.get("tags") or [])],
                }
            )
    rows.sort(key=lambda r: (r["question_rel"], r["id"]))
    return rows


# --- top level ---------------------------------------------------------------------------


def _flatten(m: Model) -> list[Question]:
    out: list[Question] = []
    for root in m.questions:
        out.extend(root.walk())
    return out


def project(m: Model) -> dict:
    research = m.research
    fm = research.fm if research else {}
    questions = _flatten(m)

    headline = None
    metric_name = str(fm.get("primary_metric", ""))
    if metric_name:
        candidates = []
        for q in questions:
            best = q.best
            if best and best[1].name == metric_name:
                candidates.append((q, best))
        if candidates:
            direction = str(fm.get("metric_direction", "higher_is_better"))
            pick = (min if direction == "lower_is_better" else max)(
                candidates, key=lambda c: c[1][1].value if c[1][1].value is not None else 0
            )
            headline = {
                "metric": metric_name,
                "value": pick[1][1].value,
                "target": fm.get("metric_target"),
                "direction": direction,
                "question_rel": pick[0].rel,
            }

    return {
        "aorf_version": spec.AORF_VERSION,
        "research": {
            "rel": research.rel if research else "",
            "title": str(fm.get("title", "")),
            "description": str(fm.get("description", "")),
            "status": str(fm.get("research_status", "")),
            "declared_version": str(fm.get("aorf_version", "")),
            "primary_metric": metric_name,
            "metric_direction": str(fm.get("metric_direction", "")),
            "metric_target": fm.get("metric_target"),
            "tags": [str(t) for t in (fm.get("tags") or [])],
            "tag_vocabulary": m.tag_vocabulary,
            "body": research.body if research else "",
            "headline": headline,
        },
        "questions": [question_row(m, q) for q in questions],
        "ledger": ledger(m),
        "datasets": [
            {
                "rel": d.rel,
                "title": str(d.fm.get("title", "")),
                "description": str(d.fm.get("description", "")),
                "version": str(d.fm.get("version", "")),
                "status": str(d.fm.get("status", "")),
                "generated": bool(d.fm.get("generated")),
                "generator": str(d.fm.get("generator", "")),
                "storage": str(d.fm.get("storage", "")),
                "resource": str(d.fm.get("resource", "")),
                "checksum": str(d.fm.get("checksum", "")),
                "row_count": d.fm.get("row_count"),
                "created": str(d.fm.get("created", "")),
                "supersedes": str(d.fm.get("supersedes", "")),
                "superseded_by": str(d.fm.get("superseded_by", "")),
                "defect": str(d.fm.get("defect", "")),
                "body": d.body,
            }
            for d in sorted(m.datasets, key=lambda d: d.rel)
        ],
        "findings": [
            {
                "rel": f.rel,
                "title": str(f.fm.get("title", "")),
                "description": str(f.fm.get("description", "")),
                "scope": str(f.fm.get("scope", "")),
                "severity": str(f.fm.get("severity", "")),
                "status": str(f.fm.get("status", "")),
                "discovered": str(f.fm.get("discovered", "")),
                "source": str(f.fm.get("source", "")),
                "affects": [str(a) for a in (f.fm.get("affects") or [])],
                "body": f.body,
            }
            for f in sorted(m.findings, key=lambda f: f.rel)
        ],
        "log": m.log,
    }


def blocking_findings(data: dict) -> list[dict]:
    return [f for f in data["findings"] if f["severity"] == "blocking" and f["status"] == "open"]


def to_json(m: Model) -> str:
    return json.dumps(project(m), indent=2, sort_keys=True, ensure_ascii=False)


# --- generated synthesis -----------------------------------------------------------------


def _fmt(value) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        text = f"{value:.4f}".rstrip("0").rstrip(".")
        return text or "0"
    return str(value)


def _fmt_delta(value) -> str:
    if value is None:
        return "—"
    return f"{'+' if value >= 0 else ''}{_fmt(value)}"


def synthesis_body(m: Model, q: Question) -> str:
    """The generated region of a question's synthesis.md.

    One table per comparability group, because a single table would put numbers that are not
    comparable in the same column. Deterministic, so `check --fix` is idempotent.
    """
    groups = comparability_groups(m, q)
    if not groups:
        return "_No experiments under this question yet._"

    lines: list[str] = []
    for group in groups:
        heading = group["label"]
        if group["invalidated"]:
            heading = f"~~{heading}~~ (invalidated)"
        lines.append(f"### {heading}")
        lines.append("")
        lines.append("| Experiment | Verdict | Metric | Value | Baseline | Delta | Ran |")
        lines.append("|---|---|---|---|---|---|---|")
        for row in group["rows"]:
            metric = row["primary"] or {}
            name = row["id"]
            if row["verdict_state"] != "current":
                name = f"~~{name}~~"
            lines.append(
                "| {id} | {verdict} | {metric} | {value} | {base} | {delta} | {ran} |".format(
                    id=f"[{name}](./experiments/{row['id']}/index.md)",
                    verdict=row["verdict"] or "—",
                    metric=metric.get("name") or "—",
                    value=_fmt(metric.get("value")),
                    base=_fmt(metric.get("baseline_value")),
                    delta=_fmt_delta(metric.get("delta")),
                    ran=row["run_date"] or "—",
                )
            )
        lines.append("")

    best = q.best
    if best:
        lines.append(
            f"**Current best:** [{best[0].id}](./experiments/{best[0].id}/index.md) — "
            f"{best[1].name} {_fmt(best[1].value)}"
            + (f", delta {_fmt_delta(best[1].delta)}" if best[1].delta is not None else "")
        )
    else:
        lines.append("**Current best:** none yet.")
    return "\n".join(lines).strip()


def synthesis_status(q: Question) -> str:
    """Draft until the question has earned a synthesis, stable after."""
    return "stable" if len(q.experiments) >= spec.MINIMAL_MODE_SYNTHESIS_AT else "draft"
