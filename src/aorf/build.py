"""Static export, sharing the renderer with `serve`.

Because `urls.py` defines one flat URL space and both modes answer it, the export is a
straight walk over `Renderer.all_paths()` — no link rewriting, which is where static-export
bugs live.

`--base` handles the GitHub Pages project-site case, where the whole site is served under
`/<repo>/`. It rewrites root-relative hrefs at write time rather than threading a prefix
through every template.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from . import parse
from .model import load
from .render.html import Renderer

# Only attribute values that start with `/` — a rewrite of `"/artifacts/x"` must not also
# touch `"https://example.com/"` or text content that happens to contain a slash.
_ROOT_REF = re.compile(r'((?:href|src|data)=")/')


def _apply_base(html: str, base: str) -> str:
    if not base:
        return html
    prefix = "/" + base.strip("/")
    return _ROOT_REF.sub(rf'\1{prefix}/', html)


def build_site(root: Path, out: Path, base: str = "") -> int:
    root, out = Path(root).resolve(), Path(out)
    model = load(root)
    renderer = Renderer(model)

    out.mkdir(parents=True, exist_ok=True)
    written = 0

    for url_path in renderer.all_paths():
        html = renderer.page_for(url_path)
        if html is None:
            continue
        target = out / url_path.lstrip("/")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(_apply_base(html, base), encoding="utf-8")
        written += 1

    static_out = out / "static"
    static_out.mkdir(parents=True, exist_ok=True)
    for asset in renderer.static_files():
        shutil.copy2(asset, static_out / asset.name)
        written += 1

    written += _copy_artifacts(root, out)

    # A 404 that keeps the site's chrome, rather than GitHub's default page.
    (out / "404.html").write_text(
        _apply_base(
            "<!doctype html><meta charset=utf-8><title>Not found</title>"
            '<link rel=stylesheet href="/static/aorf.css">'
            '<main><h1>Not found</h1><p>That page is not part of this export.</p>'
            '<p><a href="/index.html">Overview</a></p></main>',
            base,
        ),
        encoding="utf-8",
    )
    written += 1
    # Tell Pages not to run the output through Jekyll, which would drop files it dislikes.
    (out / ".nojekyll").write_text("", encoding="utf-8")
    return written + 1


def _copy_artifacts(root: Path, out: Path) -> int:
    """Copy every `artifacts/` tree, preserving repo-relative paths so URLs still resolve.

    Symlinks are skipped rather than followed: a link pointing outside the repo would
    otherwise be copied into a published site.
    """
    count = 0
    for artifacts_dir in root.rglob("artifacts"):
        if not artifacts_dir.is_dir() or artifacts_dir.is_symlink():
            continue
        if not parse.inside(root, artifacts_dir):
            continue
        for path in sorted(artifacts_dir.rglob("*")):
            if not path.is_file() or path.is_symlink():
                continue
            if not parse.inside(root, path):
                continue
            rel = path.relative_to(root)
            target = out / "artifacts" / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            count += 1
    return count
