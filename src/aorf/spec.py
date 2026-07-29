"""The AORF v0.1 schema. The single source of truth.

`check.py` enforces what is declared here and the JSON Schema published on the website is
generated from it. Never define a field in two places.

What lives here: document discovery, enums, per-type field tables, link classification.
What lives in `check.py`: the conditional rules, because "required when `research_status`
is `done` unless `kind` is `baseline`" is a predicate, and encoding predicates as data
buys nothing but indirection.
"""

from __future__ import annotations

from dataclasses import dataclass

AORF_VERSION = "0.1"

# --- document discovery (spec 3.2) -------------------------------------------------------
# Reserved payload directories. Never scanned for documents; contents are free-form.
PAYLOAD_DIRS = frozenset({"artifacts", "src", "shared"})
# Filenames that are documents wherever they appear outside a payload directory.
DOC_FILENAMES = frozenset({"index.md", "synthesis.md", "prior-art.md"})
# Directories whose direct .md children are documents.
DOC_DIRS = frozenset({"datasets", "findings"})
# Reserved by OKF, not an AORF document: free-form chronological payload.
RESERVED_NON_DOCS = frozenset({"log.md", "AGENTS.md", "README.md"})

# --- enums -------------------------------------------------------------------------------
RESEARCH_STATUS = ("active", "paused", "concluded")
QUESTION_STATUS = ("open", "literature_review", "active", "answered", "abandoned")
EXPERIMENT_STATUS = ("planned", "running", "blocked", "abandoned", "done")
OKF_LIFECYCLE = ("draft", "stable", "deprecated")
KINDS = ("baseline", "hypothesis_test", "exploration", "ablation", "sweep", "replication")
# "n/a" is valid only on kind: baseline, which has nothing to be right or wrong about.
# It exists rather than allowing an absent verdict so the renderer always has a chip.
VERDICTS = ("pending", "supported", "refuted", "inconclusive", "n/a")
VERDICT_STATES = ("current", "invalidated", "superseded")
DIRECTIONS = ("higher_is_better", "lower_is_better")
DATASET_ROLES = ("eval", "train", "reference")
STORAGE = ("git", "git-lfs", "none", "external")
PRIOR_ART_CONCLUSIONS = ("solved", "partially_solved", "open")
FINDING_SCOPES = ("repo", "question")
SEVERITIES = ("info", "important", "blocking")
FINDING_STATUS = ("open", "resolved")

# Kinds that assert something and therefore owe a hypothesis (spec 3.6).
HYPOTHESIS_KINDS = frozenset({"hypothesis_test", "ablation", "sweep"})
# Kinds exempt from carrying metrics when done: an exploration's output is understanding.
NO_METRICS_KINDS = frozenset({"exploration"})

# --- field kinds -------------------------------------------------------------------------
# doclink   a path to another AORF document; must resolve to a discovered document
# filelink  a path to a file in the repo; must exist on disk
# asset     a path or URL to an underlying resource; NOT existence-checked, because a
#           generated dataset is gitignored, an LFS pointer may be unfetched, and OKF
#           allows a URL. Emptiness is checked; reachability is not our business.
# ref       an informational path (a commit entrypoint, a lockfile). Never checked; it may
#           point into git history rather than the working tree.
KINDS_WITH_LINKS = frozenset({"doclink", "doclinks", "filelink"})


@dataclass(frozen=True)
class F:
    """One field in one document type."""

    kind: str = "str"
    required: bool = False
    enum: tuple[str, ...] | None = None
    note: str = ""
    # Set when the field is required only under a condition; the predicate lives in
    # check.py. Recorded here so the generated JSON Schema can describe it honestly.
    required_when: str = ""


@dataclass(frozen=True)
class DocType:
    status_field: str
    fields: dict[str, F]
    sections: tuple[str, ...] = ()


# The display contract (spec 3.0): required on every document, no exceptions, error not
# warning, because the renderer cannot present a document that lacks them.
_DISPLAY = {
    "type": F(required=True, note="picks the view and the icon"),
    "title": F(required=True, note="heading, and every link label pointing here"),
    "description": F(required=True, note="one-line summary in tables, cards and tooltips"),
}

_METRIC_FIELDS = {
    "name": F(required=True, note="stable within a question"),
    "value": F(kind="num", required=True),
    "direction": F(required=True, enum=DIRECTIONS),
    "baseline_value": F(kind="num", required_when="baseline is set and kind is not baseline"),
    "primary": F(kind="bool", required_when="exactly one metric per experiment"),
    "unit": F(),
    "n": F(kind="num"),
    "ci": F(kind="numlist"),
    "std": F(kind="num", required_when="nondeterministic is true"),
}

_DATASET_REF_FIELDS = {
    "path": F(kind="doclink", required=True),
    "role": F(required=True, enum=DATASET_ROLES),
}

_MODEL_FIELDS = {
    "provider": F(required=True),
    "id": F(required=True),
    "snapshot": F(required=True, note="pinned; never a floating alias"),
    "params": F(kind="map"),
}

TYPES: dict[str, DocType] = {
    "research": DocType(
        status_field="research_status",
        sections=(
            "Problem statement",
            "Goal and success criteria",
            "Scope and non-goals",
            "Questions",
            "Datasets",
            "Findings",
        ),
        fields={
            **_DISPLAY,
            "research_status": F(required=True, enum=RESEARCH_STATUS),
            "aorf_version": F(required=True, note='"0.1"'),
            "primary_metric": F(note="north-star metric name, for the dashboard headline"),
            "metric_direction": F(enum=DIRECTIONS),
            "metric_target": F(kind="num"),
            "tags": F(kind="list", note="values must come from tag_vocabulary"),
            "tag_vocabulary": F(
                kind="list",
                required_when="tags are used anywhere in the repo",
                note="the closed tag set, declared once here",
            ),
            "timestamp": F(kind="date", note="derivable from git"),
        },
    ),
    "question": DocType(
        status_field="research_status",
        sections=(
            "Question",
            "Why this matters",
            "Current best result",
            "Prior art",
            "Experiments",
            "Sub-questions",
        ),
        fields={
            **_DISPLAY,
            "parent": F(kind="doclink", required=True, note="structural; may be relative"),
            "research_status": F(required=True, enum=QUESTION_STATUS),
            "primary_metric": F(note="the comparability contract for this question"),
            "metric_direction": F(enum=DIRECTIONS),
            "metric_target": F(kind="num"),
            "answer": F(required_when="research_status is answered"),
            "answer_evidence": F(kind="doclinks", required_when="research_status is answered"),
            "closed_reason": F(required_when="research_status is abandoned"),
            "closed": F(kind="date"),
            "owner": F(),
            "tracker": F(note="one issue per question, not per experiment"),
            "tags": F(kind="list"),
            "timestamp": F(kind="date"),
        },
    ),
    "experiment": DocType(
        status_field="research_status",
        sections=("Hypothesis", "Method", "Results", "Conclusion", "Next"),
        fields={
            **_DISPLAY,
            "question": F(kind="doclink", required=True, note="structural; may be relative"),
            "kind": F(required=True, enum=KINDS),
            "research_status": F(required=True, enum=EXPERIMENT_STATUS),
            "research_status_reason": F(required_when="research_status is blocked or abandoned"),
            "hypothesis": F(
                required_when="kind is hypothesis_test, ablation or sweep",
                note="one falsifiable sentence with an expected measurable effect",
            ),
            "verdict": F(
                enum=VERDICTS,
                required_when="research_status is done",
                note="n/a only when kind is baseline",
            ),
            "verdict_scope": F(note="recommended: conditions under which the verdict holds"),
            "verdict_state": F(enum=VERDICT_STATES, note="defaults to current"),
            "invalidated_by": F(kind="doclink", required_when="verdict_state is invalidated"),
            "invalidation_reason": F(required_when="verdict_state is invalidated"),
            "supersedes": F(kind="doclink"),
            "superseded_by": F(kind="doclink", required_when="verdict_state is superseded"),
            "retests": F(kind="doclink", note="required together with retest_reason"),
            "retest_reason": F(note="required together with retests"),
            "also_informs": F(kind="doclinks", note="other questions this result bears on"),
            "baseline": F(
                kind="doclink",
                required=True,
                note="a path, or the literal none. The field is required; a baseline is not",
            ),
            "baseline_reason": F(required_when="baseline is none"),
            "datasets": F(kind="datasets", note="recommended"),
            "metrics": F(
                kind="metrics",
                required_when="research_status is done and kind is not exploration",
            ),
            "run_date": F(kind="date", required_when="research_status is done"),
            "runs": F(kind="filelink", required_when="kind is sweep"),
            "run_count": F(kind="num"),
            "best_run": F(),
            "verdict_basis": F(),
            "owner": F(),
            "cost_usd": F(kind="num"),
            "runtime_s": F(kind="num"),
            "code": F(kind="map", note="{commit, entrypoint, shared_ref, dirty}"),
            "env": F(kind="map", note="{lockfile, python}"),
            "models": F(kind="models", required_when="a model is used"),
            "nondeterministic": F(kind="bool"),
            "repeats": F(kind="num"),
            "tags": F(kind="list"),
            "tracker": F(),
            "timestamp": F(kind="date"),
        },
    ),
    "dataset": DocType(
        status_field="status",
        sections=("Provenance", "Format", "Changelog", "Known issues"),
        fields={
            **_DISPLAY,
            "version": F(required=True),
            "resource": F(kind="asset", required=True, note="path or URL to the data"),
            "status": F(required=True, enum=OKF_LIFECYCLE, note="OKF lifecycle"),
            "generated": F(kind="bool", required=True, note="true if derived"),
            "generator": F(kind="filelink", required_when="generated is true"),
            "storage": F(required=True, enum=STORAGE),
            "checksum": F(note="recommended: sha256:..."),
            "row_count": F(kind="num"),
            "created": F(kind="date"),
            "supersedes": F(kind="doclink"),
            "superseded_by": F(kind="doclink"),
            "defect": F(required_when="status is deprecated"),
            "timestamp": F(kind="date"),
        },
    ),
    "prior-art": DocType(
        status_field="conclusion",
        sections=(
            "What is already known",
            "What is not settled for us",
            "Conclusion",
            "Cost note",
            "Sources",
        ),
        fields={
            **_DISPLAY,
            "question": F(kind="doclink", required=True),
            "conclusion": F(required=True, enum=PRIOR_ART_CONCLUSIONS),
            "searched_on": F(kind="date", required=True),
            "approved_by": F(required=True, note="who authorised the spend"),
            "cost_usd": F(kind="num", note="recommended: be honest"),
            "valid_until": F(kind="date", note="do not re-run before this date"),
            "sources": F(kind="list"),
            "timestamp": F(kind="date"),
        },
    ),
    "finding": DocType(
        status_field="status",
        sections=(),
        fields={
            **_DISPLAY,
            "scope": F(required=True, enum=FINDING_SCOPES),
            "severity": F(required=True, enum=SEVERITIES),
            "affects": F(kind="doclinks", note="recommended"),
            "discovered": F(kind="date", required=True),
            "source": F(note="how it surfaced"),
            "status": F(required=True, enum=FINDING_STATUS),
            "timestamp": F(kind="date"),
        },
    ),
    "synthesis": DocType(
        status_field="status",
        sections=(),
        fields={
            **_DISPLAY,
            "question": F(kind="doclink", required=True),
            # Written by the generator, not by hand. A derived document is still a
            # document, so it carries a status chip like any other.
            "status": F(required=True, enum=OKF_LIFECYCLE),
            "timestamp": F(kind="date"),
        },
    ),
}

# --- link classification (spec 3.3) ------------------------------------------------------
# Structural links may be relative at any depth: `../../index.md` from an experiment to
# its question is unambiguous and stable.
STRUCTURAL_LINKS = frozenset({"parent", "question"})
# Every other link may be relative with at most one `..`. Beyond that, root-relative is
# required. This is the empirical rule from the trials: a depth-2 cross-tree path reached
# 142 characters containing `questions/` twice, and two of three such paths written by
# hand were wrong. One `..` covers the sibling case (`../000-baseline/index.md`), which is
# both short and self-evidently correct.
MAX_RELATIVE_PARENT_HOPS = 1

# --- generated regions ------------------------------------------------------------------
GEN_BEGIN = "<!-- AORF:BEGIN generated -->"
GEN_END = "<!-- AORF:END generated -->"

# --- limits -----------------------------------------------------------------------------
DEPTH_WARN = 3  # root index.md is depth 0; questions/<slug>/ is depth 1
DEPTH_ERROR = 4  # error under --strict
STALE_RUNNING_DAYS = 30
MINIMAL_MODE_SYNTHESIS_AT = 3  # experiments, before which a question owes no synthesis


def status_field_for(doc_type: str) -> str | None:
    t = TYPES.get(doc_type)
    return t.status_field if t else None


def link_fields(doc_type: str) -> dict[str, F]:
    t = TYPES.get(doc_type)
    if not t:
        return {}
    return {n: f for n, f in t.fields.items() if f.kind in KINDS_WITH_LINKS}


def json_schema() -> dict:
    """Generate the published JSON Schema.

    It expresses types, enums and unconditionally required fields. It deliberately does not
    express the conditional rules or any cross-document rule, because JSON Schema cannot
    check that a baseline_value matches the document it refers to. The website says so
    plainly rather than implying the schema is the whole spec.
    """
    kind_to_json = {
        "num": {"type": "number"},
        "bool": {"type": "boolean"},
        "date": {"type": "string", "description": "ISO-8601 date, YYYY-MM-DD"},
        "list": {"type": "array", "items": {"type": "string"}},
        "numlist": {"type": "array", "items": {"type": "number"}},
        "map": {"type": "object"},
        "doclinks": {"type": "array", "items": {"type": "string"}},
    }

    def obj(fields: dict[str, F]) -> dict:
        props, required = {}, []
        for name, f in fields.items():
            schema = dict(kind_to_json.get(f.kind, {"type": "string"}))
            if f.enum:
                schema = {"enum": list(f.enum)}
            hint = f"required when: {f.required_when}" if f.required_when else ""
            notes = [n for n in (f.note, hint) if n]
            if notes:
                schema["description"] = "; ".join(notes)
            props[name] = schema
            if f.required:
                required.append(name)
        out = {"type": "object", "properties": props, "additionalProperties": True}
        if required:
            out["required"] = required
        return out

    defs = {
        "metric": obj(_METRIC_FIELDS),
        "datasetRef": obj(_DATASET_REF_FIELDS),
        "model": obj(_MODEL_FIELDS),
    }
    nested = {
        "metrics": {"type": "array", "items": {"$ref": "#/$defs/metric"}},
        "datasets": {"type": "array", "items": {"$ref": "#/$defs/datasetRef"}},
        "models": {"type": "array", "items": {"$ref": "#/$defs/model"}},
    }

    one_of = []
    for name, t in TYPES.items():
        schema = obj(t.fields)
        for fname, f in t.fields.items():
            if f.kind in nested:
                schema["properties"][fname] = dict(nested[f.kind])
        schema["properties"]["type"] = {"const": name}
        one_of.append(schema)

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"https://reflow-ai.github.io/aorf/spec/aorf-v{AORF_VERSION}.schema.json",
        "title": f"AORF v{AORF_VERSION} document frontmatter",
        "description": (
            "Frontmatter of a single AORF document. Expresses types, enums and "
            "unconditionally required fields only. Conditional requirements and every "
            "cross-document rule are enforced by `aorf check`, not by this schema."
        ),
        "$defs": defs,
        "oneOf": one_of,
    }
