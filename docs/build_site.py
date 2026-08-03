"""Build the AORF website from `docs/pages/*.md`.

    python docs/build_site.py [--out _site] [--base /aorf]

Site content is authored in markdown and rendered with the same markdown-it the package
already depends on, so the site has no toolchain of its own and no seven hand-maintained HTML
files to drift apart.

The demo pages are NOT built here — they are the real output of `aorf build` over the example
repositories, so the demo is the actual tool rather than a mockup. CI runs both.
"""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

from markdown_it import MarkdownIt

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
PAGES = HERE / "pages"

# Order matters: it is the nav order and the reading order.
NAV = [
    ("index", "Overview"),
    ("rationale", "Rationale"),
    ("quickstart", "Quickstart"),
    ("spec", "Specification"),
    ("okf", "Relation to OKF"),
    ("examples", "Examples"),
    ("faq", "FAQ"),
]

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="stylesheet" href="{base}/site.css">
</head>
<body>
<header class="top">
  <a class="brand" href="{base}/index.html"><strong>AORF</strong>
    <span class="sub">Open Research Format</span></a>
  <nav>{nav}</nav>
</header>
<main>
{body}
</main>
<footer>
  <p><strong>AORF v0.1</strong> · spec under
    <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>, code under MIT ·
    <a href="https://github.com/Reflow-AI/aorf">GitHub</a> ·
    <a href="https://pypi.org/project/aorf/">PyPI</a></p>
</footer>
</body>
</html>
"""


def markdown() -> MarkdownIt:
    return (
        MarkdownIt("commonmark", {"html": True, "linkify": False})
        .enable("table")
        .enable("strikethrough")
    )


def first_heading(text: str) -> str:
    match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else "AORF"


def first_paragraph(text: str) -> str:
    body = re.sub(r"^#.*$", "", text, count=1, flags=re.MULTILINE).strip()
    for block in body.split("\n\n"):
        cleaned = re.sub(r"[*_`>#\[\]]|\(.*?\)", "", block).strip()
        if cleaned and not cleaned.startswith("|"):
            return " ".join(cleaned.split())[:180]
    return "A convention for research repositories that makes the scientific layer readable."


def build_nav(current: str, base: str) -> str:
    parts = []
    for name, label in NAV:
        href = f"{base}/{name}.html"
        cls = ' class="here"' if name == current else ""
        parts.append(f'<a href="{href}"{cls}>{label}</a>')
    return "".join(parts)


def render_page(path: Path, base: str, md: MarkdownIt) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8")
    name = path.stem
    # `{{SPEC}}` pulls in the frozen spec so the site cannot drift from spec/AORF-v0.1.md.
    if "{{SPEC}}" in text:
        spec_text = (REPO / "spec" / "AORF-v0.1.md").read_text(encoding="utf-8")
        spec_text = re.sub(r"^#\s+.+$", "", spec_text, count=1, flags=re.MULTILINE)
        # The spec's own relative links are written for its home in `spec/`, where they are
        # correct on GitHub. Inlining moves the text up one directory, so they need the prefix
        # back or they 404 on the site — which is exactly the class of breakage the format's
        # own link rules exist to prevent.
        spec_text = re.sub(r"\]\(\./(?!spec/)", "](./spec/", spec_text)
        text = text.replace("{{SPEC}}", spec_text)
    title = first_heading(text)
    html = TEMPLATE.format(
        title=f"{title} · AORF" if name != "index" else title,
        description=first_paragraph(text).replace('"', "&quot;"),
        base=base,
        nav=build_nav(name, base),
        body=md.render(text),
    )
    return f"{name}.html", html


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the AORF website.")
    parser.add_argument("--out", default=str(REPO / "_site"))
    parser.add_argument(
        "--base", default="", help="URL path prefix, e.g. /aorf for a project Pages site"
    )
    args = parser.parse_args(argv)

    out = Path(args.out)
    base = args.base.rstrip("/")
    out.mkdir(parents=True, exist_ok=True)
    md = markdown()

    written = 0
    for path in sorted(PAGES.glob("*.md")):
        name, html = render_page(path, base, md)
        (out / name).write_text(html, encoding="utf-8")
        written += 1

    shutil.copy2(HERE / "site.css", out / "site.css")
    written += 1

    # The versioned scaffolding document, served verbatim as markdown: an agent fetches it.
    version_dir = out / "v0.1"
    version_dir.mkdir(parents=True, exist_ok=True)
    for path in sorted((HERE / "v0.1").glob("*")):
        if path.is_file():
            shutil.copy2(path, version_dir / path.name)
            written += 1

    # The generated JSON Schema, so consumers can pin it.
    spec_out = out / "spec"
    spec_out.mkdir(parents=True, exist_ok=True)
    for name in ("aorf-v0.1.schema.json", "AORF-v0.1.md"):
        source = REPO / "spec" / name
        if source.is_file():
            shutil.copy2(source, spec_out / name)
            written += 1

    (out / ".nojekyll").write_text("", encoding="utf-8")
    print(f"wrote {written + 1} file(s) to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
