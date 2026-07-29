"""The command line: check, show, serve, build, init.

Exit codes: 0 clean, 1 validation errors, 2 the repo could not be read at all. CI depends on
the distinction between 1 and 2 — a broken repo and an unreadable path are different
failures.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .parse import AorfError


def _add_path(p: argparse.ArgumentParser) -> None:
    p.add_argument("path", nargs="?", default=".", help="repository root (default: .)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aorf",
        description="Validate and browse an AORF research repository.",
    )
    parser.add_argument("--version", action="version", version=f"aorf {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="validate the repository; exit 1 on error")
    _add_path(check)
    check.add_argument(
        "--strict", action="store_true", help="escalate stale generated regions and depth 4+"
    )
    check.add_argument("--json", action="store_true", dest="as_json", help="machine-readable")
    check.add_argument(
        "--fix", action="store_true", help="refresh derived content, never hand-written prose"
    )

    show = sub.add_parser("show", help="print the dashboard projection for an agent")
    _add_path(show)
    show.add_argument("--json", action="store_true", dest="as_json", default=True)

    serve = sub.add_parser("serve", help="read-only dashboard on localhost")
    _add_path(serve)
    serve.add_argument("--port", type=int, default=8471)
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--open", action="store_true", dest="open_browser")

    build = sub.add_parser("build", help="static export for GitHub Pages")
    _add_path(build)
    build.add_argument("--out", default="site", help="output directory (default: site)")
    build.add_argument("--base", default="", help="URL path prefix, e.g. /aorf/demo")

    init = sub.add_parser("init", help="scaffold a minimal AORF repository")
    _add_path(init)
    init.add_argument("--title", default="", help="research title")
    init.add_argument("--question", default="", help="the first question")
    init.add_argument("--force", action="store_true", help="write into a non-empty directory")

    return parser


def _cmd_check(args) -> int:
    from . import check as check_mod
    from . import fix as fix_mod

    if args.fix:
        result = fix_mod.apply(args.path)
        for rel in result.changed:
            print(f"fixed: {rel}", file=sys.stderr)
        for note in result.notes:
            print(f"note: {note}", file=sys.stderr)
        if not result.any:
            print("nothing to fix", file=sys.stderr)

    model, report = check_mod.check_path(args.path, strict=args.strict)

    if args.as_json:
        payload = report.as_dict()
        payload["fixed"] = sorted(result.changed) if args.fix else []
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for issue in report.issues:
            print(issue.format())
        counts = report.as_dict()["counts"]
        summary = (
            f"{counts['error']} error(s), {counts['warning']} warning(s)"
            f"{' [strict]' if args.strict else ''}"
        )
        docs = len(model.repo.docs)
        print(f"\n{docs} document(s) checked. {summary}.")
        if report.ok and not report.warnings:
            print("Clean.")
    return 0 if report.ok else 1


def _cmd_show(args) -> int:
    from .model import load
    from .project import to_json

    print(to_json(load(args.path)))
    return 0


def _cmd_serve(args) -> int:
    from .server import serve

    return serve(
        Path(args.path), host=args.host, port=args.port, open_browser=args.open_browser
    )


def _cmd_build(args) -> int:
    from .build import build_site

    written = build_site(Path(args.path), Path(args.out), base=args.base)
    print(f"wrote {written} file(s) to {args.out}")
    return 0


def _cmd_init(args) -> int:
    from .scaffold import init

    created = init(
        Path(args.path), title=args.title, question=args.question, force=args.force
    )
    for rel in created:
        print(f"created: {rel}")
    print(
        "\nThree documents is day one. Everything else appears when earned:\n"
        "  synthesis.md at three experiments, prior-art.md when a search is run,\n"
        "  datasets/ when data is referenced, findings/ when something is discovered.\n"
        "Next: aorf check"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    handlers = {
        "check": _cmd_check,
        "show": _cmd_show,
        "serve": _cmd_serve,
        "build": _cmd_build,
        "init": _cmd_init,
    }
    try:
        return handlers[args.command](args)
    except AorfError as exc:
        print(f"aorf: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
