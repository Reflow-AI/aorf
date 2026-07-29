"""Security tests: path traversal, symlink escape, artifact containment.

`aorf serve` renders author-controlled content from a directory on the author's machine, so
these are not hypothetical. Each test asserts on the actual HTTP response, not on the helper
that is supposed to prevent it.
"""

from __future__ import annotations

import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from aorf import parse
from aorf.server import CSP, make_server
from conftest import build_repo


@pytest.fixture
def server(tmp_path: Path):
    """A live server over a repo with one artifact of each interesting kind."""
    root = tmp_path / "repo"
    build_repo(root)
    artifacts = root / "questions" / "the-thing" / "experiments" / "001-the-thing" / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    (artifacts / "report.html").write_text(
        "<h1>author html</h1><script>window.top.location='http://evil'</script>",
        encoding="utf-8",
    )
    (artifacts / "table.csv").write_text("a,b\n1,2\n", encoding="utf-8")

    # A file beside the repo that nothing should ever be able to reach.
    (tmp_path / "secret.txt").write_text("do not serve me", encoding="utf-8")

    httpd = make_server(root, port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{httpd.server_address[1]}"
    yield base, root, tmp_path
    httpd.shutdown()
    httpd.server_close()


def fetch(url: str):
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return response.status, response.read(), dict(response.headers)
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(), dict(exc.headers)


def test_binds_loopback_only(server):
    base, _, _ = server
    assert base.startswith("http://127.0.0.1:")


def test_overview_sends_restrictive_csp(server):
    base, _, _ = server
    status, _, headers = fetch(f"{base}/")
    assert status == 200
    assert headers["Content-Security-Policy"] == CSP
    # No outbound anything: a dashboard that can fetch is a dashboard that can exfiltrate.
    assert "default-src 'self'" in CSP
    assert "https:" not in CSP


@pytest.mark.parametrize(
    "attack",
    [
        "/artifacts/../../secret.txt",
        "/artifacts/../secret.txt",
        "/artifacts/%2e%2e/%2e%2e/secret.txt",
        "/artifacts/....//....//secret.txt",
        "/static/../../../etc/passwd",
    ],
)
def test_path_traversal_is_refused(server, attack):
    base, _, _ = server
    status, body, _ = fetch(f"{base}{attack}")
    assert status in (403, 404), f"{attack} returned {status}"
    assert b"do not serve me" not in body


def test_repo_files_outside_artifacts_are_refused(server):
    """Only payload directories are servable; the dashboard is not a file browser."""
    base, _, _ = server
    status, body, _ = fetch(f"{base}/artifacts/index.md")
    assert status == 403
    assert b"type: research" not in body


def test_symlink_escaping_the_repo_is_refused(server):
    base, root, outside = server
    artifacts = root / "questions" / "the-thing" / "experiments" / "001-the-thing" / "artifacts"
    link = artifacts / "escape.txt"
    try:
        link.symlink_to(outside / "secret.txt")
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unavailable on this platform")
    rel = link.relative_to(root).as_posix()
    status, body, _ = fetch(f"{base}/artifacts/{rel}")
    assert status in (403, 404)
    assert b"do not serve me" not in body


def test_symlinked_artifact_is_not_discovered(server):
    """Discovery skips symlinks, so a link cannot smuggle a file into a published site."""
    base, root, outside = server
    artifacts = root / "questions" / "the-thing" / "experiments" / "001-the-thing" / "artifacts"
    try:
        (artifacts / "sneaky.csv").symlink_to(outside / "secret.txt")
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unavailable on this platform")
    from aorf.render.artifacts import discover

    names = [a.name for a in discover(root, "questions/the-thing/experiments/001-the-thing")]
    assert "sneaky.csv" not in names


def test_author_html_is_framed_and_sandboxed(server):
    """User HTML never runs same-origin. sandbox without allow-same-origin is the point."""
    base, _, _ = server
    status, body, _ = fetch(f"{base}/experiment-the-thing--001-the-thing.html")
    assert status == 200
    page = body.decode()
    assert 'sandbox="allow-scripts"' in page
    # The script must not be inlined into the dashboard document itself.
    assert "window.top.location" not in page


def test_artifact_html_carries_its_own_sandbox_header(server):
    base, root, _ = server
    rel = "questions/the-thing/experiments/001-the-thing/artifacts/report.html"
    status, _, headers = fetch(f"{base}/artifacts/{rel}")
    assert status == 200
    assert "sandbox" in headers.get("Content-Security-Policy", "")


def test_markdown_html_is_escaped_not_passed_through(tmp_path: Path):
    from aorf.render.html import md

    rendered = str(md("Text <script>alert(1)</script> more"))
    assert "<script>" not in rendered
    assert "&lt;script&gt;" in rendered


def test_serve_writes_nothing(server):
    """`serve` is strictly read-only; only check --fix, build and init write."""
    base, root, _ = server
    before = {p: p.stat().st_mtime_ns for p in sorted(root.rglob("*")) if p.is_file()}
    for path in ("/", "/ledger.html", "/datasets.html", "/findings.html", "/progress.html"):
        fetch(f"{base}{path}")
    after = {p: p.stat().st_mtime_ns for p in sorted(root.rglob("*")) if p.is_file()}
    assert before == after


def test_inside_rejects_escaping_paths(tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()
    assert parse.inside(root, root / "a" / "b.md")
    assert not parse.inside(root, root / ".." / "b.md")
    assert not parse.inside(root, tmp_path / "other.md")


def test_inside_follows_symlinks_before_comparing(tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()
    (tmp_path / "target.txt").write_text("x", encoding="utf-8")
    link = root / "link.txt"
    try:
        link.symlink_to(tmp_path / "target.txt")
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unavailable on this platform")
    assert not parse.inside(root, link)
