"""Read-only localhost dashboard.

Strictly read-only: `serve` never writes to the repository. Only `check --fix`, `build` and
`init` write anything.

The threat model is that a research repo contains author-controlled content — markdown, CSV,
SVG, HTML artifacts — and this process serves it over HTTP on a machine with the author's
files on it. So: bind loopback, confirm every resolved path is inside the repo, refuse
symlinks that escape, never execute anything, and send a CSP that forbids outbound requests.
"""

from __future__ import annotations

import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from . import parse
from .model import load
from .render.artifacts import content_type
from .render.html import STATIC, Renderer

# No external fetches, no CDN, no remote fonts. `frame-src 'self'` permits the sandboxed
# artifact iframes, which carry an opaque origin because sandbox omits allow-same-origin.
CSP = (
    "default-src 'self'; "
    "img-src 'self' data:; "
    "style-src 'self'; "
    "script-src 'self'; "
    "frame-src 'self'; "
    "object-src 'self'; "
    "form-action 'none'; "
    "base-uri 'none'; "
    "frame-ancestors 'none'"
)


class Handler(BaseHTTPRequestHandler):
    server_version = "aorf"
    sys_version = ""
    repo_root: Path
    renderer: Renderer

    # -- plumbing -----------------------------------------------------------------------
    def log_message(self, fmt: str, *args) -> None:  # quieter than the default
        print(f"  {self.address_string()} {fmt % args}")

    def _headers(
        self,
        status: HTTPStatus,
        ctype: str,
        length: int,
        csp: str = CSP,
        extra: dict | None = None,
    ):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(length))
        # Exactly one CSP header. Sending a second would leave the browser intersecting two
        # policies, which is safe but makes the effective policy on a response impossible to
        # read off — so an artifact response replaces this value rather than adding to it.
        self.send_header("Content-Security-Policy", csp)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        # The repo is being edited while this runs; a cached page would show stale results.
        self.send_header("Cache-Control", "no-store")
        for key, value in (extra or {}).items():
            self.send_header(key, value)
        self.end_headers()

    def _send_bytes(
        self, status: HTTPStatus, ctype: str, body: bytes, csp: str = CSP, extra=None
    ) -> None:
        self._headers(status, ctype, len(body), csp, extra)
        if self.command != "HEAD":
            self.wfile.write(body)

    def _send_text(self, status: HTTPStatus, body: str, ctype="text/html; charset=utf-8") -> None:
        self._send_bytes(status, ctype, body.encode("utf-8"))

    def _not_found(self, what: str) -> None:
        self._send_text(
            HTTPStatus.NOT_FOUND,
            f"<!doctype html><meta charset=utf-8><title>Not found</title>"
            f"<p>No such page: {what}</p><p><a href='/'>Overview</a></p>",
        )

    def _forbidden(self) -> None:
        self._send_text(HTTPStatus.FORBIDDEN, "<!doctype html><meta charset=utf-8>Forbidden")

    # -- routing ------------------------------------------------------------------------
    def do_HEAD(self) -> None:  # noqa: N802
        self.do_GET()

    def do_GET(self) -> None:  # noqa: N802
        path = unquote(urlparse(self.path).path)

        if path.startswith("/static/"):
            return self._serve_static(path[len("/static/") :])
        if path.startswith("/artifacts/"):
            return self._serve_artifact(path[len("/artifacts/") :])

        # Reload from disk each request: the author is editing the repo while watching it,
        # and a dashboard showing a stale model would defeat the purpose.
        try:
            self.renderer = Renderer(load(self.repo_root))
        except Exception as exc:  # a broken repo should still explain itself in the browser
            return self._send_text(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                f"<!doctype html><meta charset=utf-8><title>aorf</title>"
                f"<h1>Could not read the repository</h1><pre>{exc}</pre>",
            )

        page = self.renderer.page_for(path)
        if page is None:
            return self._not_found(path)
        return self._send_text(HTTPStatus.OK, page)

    # -- files --------------------------------------------------------------------------
    def _resolve_within(self, base: Path, relative: str) -> Path | None:
        """Resolve `relative` under `base`, or None if it escapes.

        Handles both traversal (`../`) and symlinks that point outside, because
        `inside()` resolves links on both sides before comparing.
        """
        if relative.startswith("/") or "\x00" in relative:
            return None
        candidate = base / relative
        if not parse.inside(base, candidate):
            return None
        if not candidate.is_file():
            return None
        # A symlink inside the repo pointing outside it resolves out of bounds; inside()
        # already rejected that. What remains is to refuse links whose target is missing.
        return candidate

    def _serve_static(self, name: str) -> None:
        target = self._resolve_within(STATIC, name)
        if target is None:
            return self._not_found(f"/static/{name}")
        self._send_bytes(HTTPStatus.OK, content_type(target.suffix), target.read_bytes())

    def _serve_artifact(self, relative: str) -> None:
        target = self._resolve_within(self.repo_root, relative)
        if target is None:
            return self._forbidden()
        # Only payload directories are servable. Serving arbitrary repo files would turn the
        # dashboard into a file browser for everything beside it on disk.
        parts = target.resolve().relative_to(self.repo_root.resolve()).parts
        if "artifacts" not in parts:
            return self._forbidden()
        csp, extra = CSP, {}
        if target.suffix.lower() in (".html", ".htm", ".svg"):
            # Defence in depth: even inside the sandboxed frame, this document gets no
            # scripting and no outbound requests of its own. Inline styles stay allowed
            # because a chart exported to HTML or SVG is almost always styled inline.
            csp = "sandbox; default-src 'none'; img-src 'self' data:; style-src 'unsafe-inline'"
            extra["X-Frame-Options"] = "SAMEORIGIN"
        self._send_bytes(
            HTTPStatus.OK, content_type(target.suffix), target.read_bytes(), csp, extra
        )


def make_server(root: Path, host: str = "127.0.0.1", port: int = 8471) -> ThreadingHTTPServer:
    root = Path(root).resolve()
    model = load(root)  # fail fast on an unreadable repo rather than at first request

    class Bound(Handler):
        repo_root = root
        renderer = Renderer(model)

    return ThreadingHTTPServer((host, port), Bound)


def serve(
    root: Path, host: str = "127.0.0.1", port: int = 8471, open_browser: bool = False
) -> int:
    httpd = make_server(root, host, port)
    url = f"http://{host}:{port}/"
    if host not in ("127.0.0.1", "localhost", "::1"):
        print(
            f"warning: binding {host}, not loopback. This exposes the repository, including "
            f"artifact files, to anything that can reach this port.",
        )
    print(f"aorf serving {root} at {url}  (read-only, Ctrl-C to stop)")
    if open_browser:
        webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        httpd.server_close()
    return 0
