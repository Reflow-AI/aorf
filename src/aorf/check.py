"""The integrity rules.

Each rule is one function taking the Model and yielding Issues, so each is independently
testable against one deliberately broken fixture. Rules 1-20 are the frozen v0.1 set;
21-26 were added during M0 to close gaps the frozen list left open.

The bias throughout: a missing thing the renderer needs is an error, because a dashboard
that renders a repo which quietly lies is worse than no dashboard. A stylistic or
recoverable problem is a warning.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

from . import parse, spec
from .model import Experiment, Model, Question

ERROR, WARNING, INFO = "error", "warning", "info"

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


@dataclass(frozen=True)
class Issue:
    level: str
    rule: str
    path: str
    message: str

    def format(self) -> str:
        return f"{self.path}: {self.level}: [{self.rule}] {self.message}"


@dataclass
class Report:
    issues: list[Issue]
    strict: bool = False

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.level == ERROR]

    @property
    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.level == WARNING]

    @property
    def ok(self) -> bool:
        return not self.errors

    def as_dict(self) -> dict:
        return {
            "ok": self.ok,
            "strict": self.strict,
            "counts": {
                "error": len(self.errors),
                "warning": len(self.warnings),
                "info": sum(1 for i in self.issues if i.level == INFO),
            },
            "issues": [
                {"level": i.level, "rule": i.rule, "path": i.path, "message": i.message}
                for i in self.issues
            ],
        }


# --- helpers -----------------------------------------------------------------------------


def _nonempty(value) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def _experiments(m: Model) -> list[Experiment]:
    return m.experiments


def _questions(m: Model) -> list[Question]:
    return list(m.all_questions.values())


def _reason_field(status: str) -> str:
    return "research_status_reason"


# --- rules -------------------------------------------------------------------------------


def r01_display_contract(m: Model):
    """The display contract holds on every document, including dataset and synthesis status.

    No document type is exempt from carrying a status: the renderer must be able to show a
    chip for anything it is handed.
    """
    for doc in m.repo.docs:
        if doc.fm_error:
            yield Issue(ERROR, "R01", doc.rel, doc.fm_error)
            continue
        if not doc.type:
            yield Issue(ERROR, "R01", doc.rel, "missing required field: type")
            continue
        if doc.type not in spec.TYPES:
            # OKF says consumers must tolerate unknown types; AORF documents are a closed
            # set, so an unknown type here means a typo, not an extension.
            yield Issue(
                ERROR,
                "R01",
                doc.rel,
                f"unknown type {doc.type!r}; expected one of {', '.join(sorted(spec.TYPES))}",
            )
            continue
        for name in ("title", "description"):
            if not _nonempty(doc.fm.get(name)):
                yield Issue(ERROR, "R01", doc.rel, f"missing required field: {name}")
        status_field = spec.status_field_for(doc.type)
        if status_field and not _nonempty(doc.fm.get(status_field)):
            yield Issue(
                ERROR,
                "R01",
                doc.rel,
                f"missing required status field {status_field!r}; the renderer has no chip "
                f"to show for this document",
            )
        for name, f in spec.TYPES[doc.type].fields.items():
            if f.required and name not in ("type", "title", "description", status_field):
                if not _nonempty(doc.fm.get(name)):
                    yield Issue(ERROR, "R01", doc.rel, f"missing required field: {name}")


def r02_enums(m: Model):
    """Enum values valid, including nested metric and dataset-reference enums."""
    for doc in m.repo.docs:
        t = spec.TYPES.get(doc.type)
        if not t:
            continue
        for name, f in t.fields.items():
            if not f.enum:
                continue
            value = doc.fm.get(name)
            if value is None:
                continue
            if not isinstance(value, str) or value not in f.enum:
                yield Issue(
                    ERROR,
                    "R02",
                    doc.rel,
                    f"{name}={value!r} is not one of: {', '.join(f.enum)}",
                )
        for i, entry in enumerate(doc.fm.get("metrics") or []):
            if isinstance(entry, dict):
                d = entry.get("direction")
                if d is not None and d not in spec.DIRECTIONS:
                    yield Issue(
                        ERROR,
                        "R02",
                        doc.rel,
                        f"metrics[{i}].direction={d!r} is not one of: "
                        f"{', '.join(spec.DIRECTIONS)}",
                    )
        for i, entry in enumerate(doc.fm.get("datasets") or []):
            if isinstance(entry, dict):
                role = entry.get("role")
                if role is not None and role not in spec.DATASET_ROLES:
                    yield Issue(
                        ERROR,
                        "R02",
                        doc.rel,
                        f"datasets[{i}].role={role!r} is not one of: "
                        f"{', '.join(spec.DATASET_ROLES)}",
                    )
    # verdict: n/a is meaningful only for a baseline, which asserts nothing.
    for e in _experiments(m):
        if e.verdict == "n/a" and e.kind != "baseline":
            yield Issue(
                ERROR,
                "R02",
                e.rel,
                "verdict: n/a is valid only when kind: baseline; a non-baseline experiment "
                "owes a real verdict",
            )


def r03_links_resolve(m: Model):
    """Every link field resolves: document links to a document, file links to a file."""
    for doc in m.repo.docs:
        for name, f in spec.link_fields(doc.type).items():
            raw = doc.fm.get(name)
            if raw is None:
                continue
            values = raw if isinstance(raw, list) else [raw]
            for value in values:
                if not isinstance(value, str) or not value.strip():
                    yield Issue(ERROR, "R03", doc.rel, f"{name} is not a usable path")
                    continue
                if name == "baseline" and value == "none":
                    continue
                target = parse.resolve(m.root, doc.rel, value)
                if not parse.inside(m.root, target):
                    yield Issue(
                        ERROR, "R03", doc.rel, f"{name} -> {value} escapes the repository"
                    )
                    continue
                if f.kind == "filelink":
                    if not target.is_file():
                        yield Issue(ERROR, "R03", doc.rel, f"{name} -> {value} does not exist")
                    continue
                rel = parse.resolve_rel(m.root, doc.rel, value)
                if rel not in m.repo.by_rel:
                    hint = (
                        " (file exists but is not an AORF document; see spec 3.2)"
                        if target.is_file()
                        else ""
                    )
                    yield Issue(
                        ERROR, "R03", doc.rel, f"{name} -> {value} resolves to nothing{hint}"
                    )
        # datasets[].path is nested, so it is checked separately.
        for i, entry in enumerate(doc.fm.get("datasets") or []):
            if not isinstance(entry, dict):
                continue
            value = entry.get("path")
            if not isinstance(value, str):
                yield Issue(ERROR, "R03", doc.rel, f"datasets[{i}].path is missing")
                continue
            rel = parse.resolve_rel(m.root, doc.rel, value)
            if rel not in m.repo.by_rel:
                yield Issue(
                    ERROR, "R03", doc.rel, f"datasets[{i}].path -> {value} resolves to nothing"
                )


def r04_done_is_complete(m: Model):
    """`done` implies a real verdict, at least one metric, and a run_date."""
    for e in _experiments(m):
        if e.status != "done":
            continue
        if not e.verdict:
            yield Issue(ERROR, "R04", e.rel, "research_status: done requires a verdict")
        elif e.verdict == "pending":
            yield Issue(
                ERROR, "R04", e.rel, "research_status: done with verdict: pending is not done"
            )
        if e.kind not in spec.NO_METRICS_KINDS and not e.metrics:
            yield Issue(
                ERROR,
                "R04",
                e.rel,
                f"research_status: done requires at least one metric for kind: {e.kind}",
            )
        if not e.run_date:
            yield Issue(
                ERROR,
                "R04",
                e.rel,
                "research_status: done requires run_date; git cannot recover when it ran",
            )


def r05_one_primary_metric(m: Model):
    """Exactly one `primary: true` metric, so the dashboard's headline is unambiguous."""
    for e in _experiments(m):
        ms = e.metrics
        if not ms:
            continue
        primaries = [x for x in ms if x.primary]
        if len(primaries) == 1:
            continue
        if not primaries and len(ms) == 1:
            yield Issue(
                WARNING,
                "R05",
                e.rel,
                "the single metric is not marked primary: true; add it so the intent is "
                "explicit rather than inferred",
            )
        elif not primaries:
            yield Issue(
                ERROR, "R05", e.rel, f"{len(ms)} metrics and none marked primary: true"
            )
        else:
            names = ", ".join(x.name for x in primaries)
            yield Issue(ERROR, "R05", e.rel, f"more than one primary metric: {names}")


def r06_baseline_none_needs_reason(m: Model):
    """`baseline: none` is a first-class answer, but it must say why.

    A baseline is suggested, never forced. What is forced is the explicit statement, because
    an absent `baseline` field is indistinguishable from an oversight.
    """
    for e in _experiments(m):
        if e.baseline_raw == "none" and not _nonempty(e.doc.fm.get("baseline_reason")):
            yield Issue(
                ERROR,
                "R06",
                e.rel,
                "baseline: none requires baseline_reason; declaring the absence is fine, "
                "leaving it unexplained is not",
            )


def r07_hypothesis_required(m: Model):
    """A kind that asserts something owes a falsifiable sentence."""
    for e in _experiments(m):
        if e.kind in spec.HYPOTHESIS_KINDS and not _nonempty(e.doc.fm.get("hypothesis")):
            yield Issue(ERROR, "R07", e.rel, f"kind: {e.kind} requires a hypothesis")
        if e.kind == "baseline" and _nonempty(e.doc.fm.get("hypothesis")):
            yield Issue(
                WARNING,
                "R07",
                e.rel,
                "kind: baseline carries a hypothesis; a baseline measures, it does not assert",
            )


def r08_sweep_needs_runs(m: Model):
    """`kind: sweep` requires a runs file; existence is checked by R03."""
    for e in _experiments(m):
        if e.kind == "sweep" and not _nonempty(e.doc.fm.get("runs")):
            yield Issue(ERROR, "R08", e.rel, "kind: sweep requires a runs file")


def r09_verdict_state_companions(m: Model):
    """`invalidated` needs its finding and reason; `superseded` needs its successor."""
    for e in _experiments(m):
        if e.verdict_state == "invalidated":
            if not _nonempty(e.doc.fm.get("invalidated_by")):
                yield Issue(
                    ERROR, "R09", e.rel, "verdict_state: invalidated requires invalidated_by"
                )
            if not _nonempty(e.doc.fm.get("invalidation_reason")):
                yield Issue(
                    ERROR,
                    "R09",
                    e.rel,
                    "verdict_state: invalidated requires invalidation_reason",
                )
        elif e.verdict_state == "superseded" and not _nonempty(e.doc.fm.get("superseded_by")):
            yield Issue(ERROR, "R09", e.rel, "verdict_state: superseded requires superseded_by")


def r10_answered_needs_evidence(m: Model):
    """An answered question states its answer and points at what supports it."""
    for q in _questions(m):
        if q.status != "answered":
            continue
        if not _nonempty(q.doc.fm.get("answer")):
            yield Issue(ERROR, "R10", q.rel, "research_status: answered requires answer")
        evidence = q.doc.fm.get("answer_evidence")
        if not isinstance(evidence, list) or not evidence:
            yield Issue(
                ERROR,
                "R10",
                q.rel,
                "research_status: answered requires a non-empty answer_evidence list",
            )


def r11_closed_states_need_reasons(m: Model):
    """A stopped thing says why it stopped, or the next reader repeats it."""
    for e in _experiments(m):
        if e.status in ("blocked", "abandoned") and not _nonempty(
            e.doc.fm.get("research_status_reason")
        ):
            yield Issue(
                ERROR,
                "R11",
                e.rel,
                f"research_status: {e.status} requires research_status_reason",
            )
    for q in _questions(m):
        if q.status == "abandoned" and not _nonempty(q.doc.fm.get("closed_reason")):
            yield Issue(ERROR, "R11", q.rel, "research_status: abandoned requires closed_reason")


def r12_baseline_comparability(m: Model):
    """An experiment must not compare against a baseline that used a different dataset.

    Skipped for an already-invalidated experiment, so one problem produces one error rather
    than two.
    """
    for e in _experiments(m):
        if not e.has_baseline or not e.is_current:
            continue
        target = m.resolve_doc(e.rel, e.baseline_raw)
        if target is None:
            continue  # R03 owns the dangling link
        base = next((x for x in _experiments(m) if x.rel == target.rel), None)
        if base is None:
            continue
        mine, theirs = e.dataset_versions, base.dataset_versions
        if mine and theirs and mine != theirs:
            yield Issue(
                ERROR,
                "R12",
                e.rel,
                f"compares against a baseline run on a different dataset version "
                f"({', '.join(theirs)} vs {', '.join(mine)}); re-run the baseline per "
                f"dataset version",
            )


def r13_generated_needs_generator(m: Model):
    """If it can be regenerated, it does not go in the repo."""
    for d in m.datasets:
        if d.fm.get("generated") is not True:
            continue
        if not _nonempty(d.fm.get("generator")):
            yield Issue(ERROR, "R13", d.rel, "generated: true requires generator")
        if d.fm.get("storage") != "none":
            yield Issue(
                WARNING,
                "R13",
                d.rel,
                f"generated: true with storage: {d.fm.get('storage')!r}; a derived dataset "
                f"belongs in .gitignore with storage: none",
            )


def r14_source_data_is_committed(m: Model):
    """Source data that cannot be regenerated should not be an external dependency."""
    for d in m.datasets:
        if d.fm.get("generated") is not False:
            continue
        if d.fm.get("storage") not in ("git", "git-lfs"):
            yield Issue(
                WARNING,
                "R14",
                d.rel,
                f"generated: false with storage: {d.fm.get('storage')!r}; source data is "
                f"normally committed via git-lfs so the repo is self-contained. State the "
                f"reason in # Provenance if this is deliberate",
            )


def r15_stale_running(m: Model):
    """An experiment that has been running for a month is probably not running."""
    today = date.today()
    for e in _experiments(m):
        if e.status != "running":
            continue
        stamp = e.doc.fm.get("timestamp") or e.doc.fm.get("run_date")
        if not isinstance(stamp, str) or not DATE_RE.match(stamp):
            continue
        try:
            when = datetime.strptime(stamp, "%Y-%m-%d").date()
        except ValueError:
            continue
        if today - when > timedelta(days=spec.STALE_RUNNING_DAYS):
            days = (today - when).days
            yield Issue(
                WARNING,
                "R15",
                e.rel,
                f"research_status: running and last touched {days} days ago; if it finished, "
                f"record the verdict",
            )


def r16_generated_regions_current(m: Model):
    """Generated regions match what the generator would write now. Error under --strict."""
    from .project import synthesis_body

    for q in _questions(m):
        if q.synthesis is None:
            continue
        want = synthesis_body(m, q)
        span = parse.generated_region(q.synthesis.body)
        have = q.synthesis.body[span[0] : span[1]].strip() if span else ""
        if have != want.strip():
            detail = "has no generated region" if span is None else "is out of date"
            yield Issue(
                WARNING,
                "R16",
                q.synthesis.rel,
                f"generated region {detail}; run `aorf check --fix`",
            )


def r17_depth(m: Model):
    """Nesting deeper than 2 warns; deeper than 3 errors under --strict."""
    for q in _questions(m):
        if q.depth >= spec.DEPTH_ERROR:
            yield Issue(
                WARNING,
                "R17",
                q.rel,
                f"question nesting depth {q.depth}; at this depth cross-tree paths become "
                f"unreadable and unwritable by hand. Split the research instead",
            )
        elif q.depth >= spec.DEPTH_WARN:
            yield Issue(
                WARNING,
                "R17",
                q.rel,
                f"question nesting depth {q.depth}; 2 is the practical limit",
            )


def _git(root: Path, *args: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout if out.returncode == 0 else None


def r18_hypothesis_frozen(m: Model):
    """A hypothesis must not change once the experiment has started running.

    This is the one rule that needs history, because the whole point of hypothesis-before-run
    is that the claim predates the result. Skipped with a note where git cannot answer,
    rather than silently passing.
    """
    if not m.experiments:
        return
    if _git(m.root, "rev-parse", "--git-dir") is None:
        yield Issue(
            INFO,
            "R18",
            ".",
            "not a git repository, so hypothesis-frozen could not be checked",
        )
        return
    for e in _experiments(m):
        if e.status == "planned" or not e.hypothesis:
            continue
        log = _git(m.root, "log", "--format=%H", "--reverse", "--", e.rel)
        if log is None:
            continue
        shas = [line.strip() for line in log.splitlines() if line.strip()]
        if len(shas) < 2:
            continue
        seen: list[str] = []
        started = False
        for sha in shas:
            blob = _git(m.root, "show", f"{sha}:{e.rel}")
            if blob is None:
                continue
            raw, _ = parse.split_frontmatter(blob)
            try:
                import yaml

                fm = yaml.safe_load(raw) or {}
            except Exception:
                continue
            if not isinstance(fm, dict):
                continue
            if str(fm.get("research_status", "")) != "planned":
                started = True
            if started:
                h = str(fm.get("hypothesis", "")).strip()
                if h and h not in seen:
                    seen.append(h)
        if len(seen) > 1:
            yield Issue(
                ERROR,
                "R18",
                e.rel,
                "hypothesis changed after the experiment started running; a hypothesis "
                "rewritten to match the result is not a hypothesis. Record a new experiment "
                "with retests instead",
            )


def r19_tags_declared(m: Model):
    """Every tag comes from the root vocabulary. Repos using no tags skip this entirely."""
    vocab = set(m.tag_vocabulary)
    used = any(_nonempty(d.fm.get("tags")) for d in m.repo.docs)
    if not used:
        return
    if not vocab:
        yield Issue(
            ERROR,
            "R19",
            m.research.rel if m.research else "index.md",
            "tags are used in this repo but the root declares no tag_vocabulary; an "
            "undeclared vocabulary fills the filter with near-duplicates",
        )
        return
    for doc in m.repo.docs:
        tags = doc.fm.get("tags")
        if not isinstance(tags, list):
            continue
        for tag in tags:
            if str(tag) not in vocab:
                yield Issue(
                    ERROR,
                    "R19",
                    doc.rel,
                    f"tag {tag!r} is not in the root tag_vocabulary; either a typo or a "
                    f"one-line addition to the vocabulary",
                )


def r20_vocabulary_wellformed(m: Model):
    """Vocabulary entries are lowercase kebab-case and unique."""
    if not m.research:
        return
    vocab = m.research.fm.get("tag_vocabulary")
    if not isinstance(vocab, list):
        return
    seen = set()
    for tag in vocab:
        t = str(tag)
        if not KEBAB_RE.match(t):
            yield Issue(
                ERROR, "R20", m.research.rel, f"tag_vocabulary entry {t!r} is not lowercase "
                f"kebab-case"
            )
        if t in seen:
            yield Issue(ERROR, "R20", m.research.rel, f"tag_vocabulary entry {t!r} is duplicated")
        seen.add(t)


def r21_baseline_value_matches(m: Model):
    """A metric's baseline_value must equal the referenced baseline's own measurement.

    baseline_value is denormalized on purpose: it keeps a document readable on its own, and
    lets an agent compute a delta without following a link. That trade is only safe if the
    copy is checked, because a drifted baseline_value makes every delta in the repo wrong
    while looking rigorous. Skipped for invalidated experiments, matching R12.
    """
    for e in _experiments(m):
        if not e.has_baseline or not e.is_current:
            continue
        target = m.resolve_doc(e.rel, e.baseline_raw)
        base = next((x for x in _experiments(m) if target and x.rel == target.rel), None)
        if base is None:
            continue
        base_by_name = {x.name: x for x in base.metrics}
        for metric in e.metrics:
            if metric.baseline_value is None:
                if metric.name in base_by_name:
                    yield Issue(
                        WARNING,
                        "R21",
                        e.rel,
                        f"metric {metric.name!r} has no baseline_value but the baseline "
                        f"measured it; without one there is no delta to show",
                    )
                continue
            theirs = base_by_name.get(metric.name)
            if theirs is None:
                yield Issue(
                    WARNING,
                    "R21",
                    e.rel,
                    f"metric {metric.name!r} carries baseline_value "
                    f"{metric.baseline_value} but the baseline does not measure "
                    f"{metric.name!r}; the number has no source",
                )
                continue
            if theirs.value is not None and abs(theirs.value - metric.baseline_value) > 1e-9:
                yield Issue(
                    ERROR,
                    "R21",
                    e.rel,
                    f"metric {metric.name!r} baseline_value {metric.baseline_value} does not "
                    f"match the baseline's {theirs.value} in {base.rel}; run "
                    f"`aorf check --fix`",
                )


def r22_metric_comparability(m: Model):
    """The question's primary_metric is a contract its experiments must honour.

    R12 protects the dataset axis; without this the metric axis is unprotected, and a
    renamed or re-oriented metric silently produces a column of numbers that are not
    comparable.
    """
    for q in _questions(m):
        want, direction = q.primary_metric, q.metric_direction
        if not want:
            continue
        for e in q.experiments:
            metric = e.primary
            if metric is None:
                continue
            if metric.name != want:
                yield Issue(
                    ERROR,
                    "R22",
                    e.rel,
                    f"primary metric is {metric.name!r} but the question's primary_metric is "
                    f"{want!r}; numbers under one question must be comparable",
                )
            elif direction and metric.direction != direction:
                yield Issue(
                    ERROR,
                    "R22",
                    e.rel,
                    f"metric {metric.name!r} direction {metric.direction!r} contradicts the "
                    f"question's metric_direction {direction!r}",
                )


def r23_version_compatibility(m: Model):
    """An unknown minor version warns and proceeds; an unknown major errors."""
    if not m.research:
        return
    raw = m.research.fm.get("aorf_version")
    if raw is None:
        return
    declared = str(raw).strip()
    if declared == spec.AORF_VERSION:
        return
    ours_major = spec.AORF_VERSION.split(".")[0]
    theirs_major = declared.split(".")[0]
    if theirs_major != ours_major:
        yield Issue(
            ERROR,
            "R23",
            m.research.rel,
            f"aorf_version {declared!r} is a different major version than this tool's "
            f"{spec.AORF_VERSION!r}; upgrade aorf rather than trusting this output",
        )
    else:
        yield Issue(
            WARNING,
            "R23",
            m.research.rel,
            f"aorf_version {declared!r} is newer or older than this tool's "
            f"{spec.AORF_VERSION!r}; fields this tool does not know are preserved but not "
            f"validated",
        )


def r24_dates_are_iso(m: Model):
    """Dates are ISO-8601 YYYY-MM-DD. A YAML native date is accepted and normalized."""
    for doc in m.repo.docs:
        t = spec.TYPES.get(doc.type)
        if not t:
            continue
        for name, f in t.fields.items():
            if f.kind != "date":
                continue
            value = doc.fm.get(name)
            if value is None:
                continue
            if not isinstance(value, str) or not DATE_RE.match(value):
                yield Issue(
                    ERROR, "R24", doc.rel, f"{name}={value!r} is not an ISO-8601 date (YYYY-MM-DD)"
                )


def r25_link_relativity(m: Model):
    """Deep relative paths must be root-relative.

    From the trials: a depth-2 cross-tree path reached 142 characters containing
    `questions/` twice; two of three such paths written by hand were wrong, and a third was
    broken by a mechanical rewrite. One `..` covers the sibling case and stays obviously
    correct; beyond that, a leading `/` is both shorter and checkable. Structural links
    (`parent`, `question`) are exempt at any depth because they are fixed and unambiguous.
    """
    for doc in m.repo.docs:
        fields = dict(spec.link_fields(doc.type))
        for name in fields:
            if name in spec.STRUCTURAL_LINKS:
                continue
            raw = doc.fm.get(name)
            if raw is None:
                continue
            for value in raw if isinstance(raw, list) else [raw]:
                if not isinstance(value, str) or value.startswith("/") or value == "none":
                    continue
                hops = parse.parent_hops(value)
                if hops > spec.MAX_RELATIVE_PARENT_HOPS:
                    yield Issue(
                        ERROR,
                        "R25",
                        doc.rel,
                        f"{name} -> {value} climbs {hops} levels; use a root-relative path "
                        f"(leading /) for anything more than one level up",
                    )
        for i, entry in enumerate(doc.fm.get("datasets") or []):
            if not isinstance(entry, dict):
                continue
            value = entry.get("path")
            if isinstance(value, str) and not value.startswith("/"):
                hops = parse.parent_hops(value)
                if hops > spec.MAX_RELATIVE_PARENT_HOPS:
                    yield Issue(
                        ERROR,
                        "R25",
                        doc.rel,
                        f"datasets[{i}].path -> {value} climbs {hops} levels; use a "
                        f"root-relative path",
                    )


def r26_synthesis_when_earned(m: Model):
    """A question with three or more experiments has earned a synthesis.

    The other half of minimal mode: nothing exists before it is earned, and once it is
    earned its absence is a gap rather than restraint.
    """
    for q in _questions(m):
        if len(q.experiments) >= spec.MINIMAL_MODE_SYNTHESIS_AT and q.synthesis is None:
            yield Issue(
                WARNING,
                "R26",
                q.rel,
                f"{len(q.experiments)} experiments and no synthesis.md; at this point the "
                f"comparison is worth having",
            )


RULES = [
    r01_display_contract,
    r02_enums,
    r03_links_resolve,
    r04_done_is_complete,
    r05_one_primary_metric,
    r06_baseline_none_needs_reason,
    r07_hypothesis_required,
    r08_sweep_needs_runs,
    r09_verdict_state_companions,
    r10_answered_needs_evidence,
    r11_closed_states_need_reasons,
    r12_baseline_comparability,
    r13_generated_needs_generator,
    r14_source_data_is_committed,
    r15_stale_running,
    r16_generated_regions_current,
    r17_depth,
    r18_hypothesis_frozen,
    r19_tags_declared,
    r20_vocabulary_wellformed,
    r21_baseline_value_matches,
    r22_metric_comparability,
    r23_version_compatibility,
    r24_dates_are_iso,
    r25_link_relativity,
    r26_synthesis_when_earned,
]

# Rules whose level is raised from warning to error by --strict, per spec 3.12.
STRICT_ESCALATE = {"R16"}
STRICT_ESCALATE_DEEP_ONLY = {"R17"}


def run(m: Model, strict: bool = False) -> Report:
    issues: list[Issue] = []
    for rule in RULES:
        issues.extend(rule(m))

    if strict:
        escalated = []
        for issue in issues:
            if issue.level == WARNING and issue.rule in STRICT_ESCALATE:
                issue = Issue(ERROR, issue.rule, issue.path, issue.message)
            elif (
                issue.level == WARNING
                and issue.rule in STRICT_ESCALATE_DEEP_ONLY
                and f"depth {spec.DEPTH_ERROR}" in issue.message
            ):
                issue = Issue(ERROR, issue.rule, issue.path, issue.message)
            escalated.append(issue)
        issues = escalated

    order = {ERROR: 0, WARNING: 1, INFO: 2}
    issues.sort(key=lambda i: (order.get(i.level, 3), i.path, i.rule))
    return Report(issues=issues, strict=strict)


def check_path(path: Path | str, strict: bool = False) -> tuple[Model, Report]:
    from .model import load

    m = load(path)
    if m.research is None:
        report = Report(
            issues=[
                Issue(
                    ERROR,
                    "R01",
                    "index.md",
                    "no root index.md with type: research; this is not an AORF repository",
                )
            ],
            strict=strict,
        )
        return m, report
    return m, run(m, strict=strict)
