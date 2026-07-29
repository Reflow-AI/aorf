"""One flat URL space, used identically by `serve` and `build`.

`serve` answers these paths and `build` writes files at exactly the same names, which is what
makes "do not write two renderers" actually hold: the templates never learn which mode they
are in, so a link cannot be right in one and broken in the other.

Flat rather than nested because a nested static export needs every link rewritten per depth,
and that rewriting is where link bugs live.
"""

from __future__ import annotations

import re

PAGES = ("index", "ledger", "progress", "datasets", "findings")

_SLUG_STRIP = re.compile(r"[^a-z0-9]+")


def slug(text: str) -> str:
    return _SLUG_STRIP.sub("-", text.lower()).strip("-")


def question_slug(rel: str) -> str:
    """`questions/a/questions/b/index.md` -> `a--b`, which keeps nesting legible."""
    parts = [p for p in rel.split("/") if p not in ("questions", "index.md")]
    return "--".join(slug(p) for p in parts if p)


def experiment_slug(rel: str) -> str:
    """`questions/a/experiments/001-x/index.md` -> `a--001-x`."""
    parts = [p for p in rel.split("/") if p not in ("questions", "experiments", "index.md")]
    return "--".join(slug(p) for p in parts if p)


def doc_slug(rel: str) -> str:
    return slug(rel.rsplit("/", 1)[-1].removesuffix(".md"))


def page(name: str) -> str:
    return f"/{name}.html"


def question(rel: str) -> str:
    return f"/question-{question_slug(rel)}.html"


def experiment(rel: str) -> str:
    return f"/experiment-{experiment_slug(rel)}.html"


def dataset(rel: str) -> str:
    return f"/dataset-{doc_slug(rel)}.html"


def finding(rel: str) -> str:
    return f"/finding-{doc_slug(rel)}.html"


def artifact(repo_rel: str) -> str:
    return f"/artifacts/{repo_rel}"


def static(name: str) -> str:
    return f"/static/{name}"


def for_document(rel: str, doc_type: str) -> str:
    """The page that presents a document, given its type.

    Used to turn a frontmatter link into a dashboard link so `affects`, `supersedes` and
    `answer_evidence` are clickable rather than decorative.
    """
    return {
        "research": lambda r: page("index"),
        "question": question,
        "experiment": experiment,
        "dataset": dataset,
        "finding": finding,
        "synthesis": lambda r: question(r.rsplit("/", 1)[0] + "/index.md"),
        "prior-art": lambda r: question(r.rsplit("/", 1)[0] + "/index.md"),
    }.get(doc_type, lambda r: page("index"))(rel)


def all_page_names() -> tuple[str, ...]:
    return PAGES
