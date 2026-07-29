"""Regenerate the projection snapshots. Run deliberately, then read the diff.

    python tests/regolden.py

A snapshot that changes without anyone noticing is a change to the dashboard's data contract
that nobody reviewed, so this is a separate explicit command rather than an --update flag on
the test run.
"""

from __future__ import annotations

from pathlib import Path

from aorf.model import load
from aorf.project import to_json

HERE = Path(__file__).resolve().parent
EXAMPLES = HERE.parent / "examples"
GOLDEN = HERE / "golden"


def main() -> int:
    GOLDEN.mkdir(exist_ok=True)
    for path in sorted(EXAMPLES.iterdir()):
        if not (path / "index.md").is_file():
            continue
        target = GOLDEN / f"{path.name}.json"
        target.write_text(to_json(load(path)) + "\n", encoding="utf-8")
        print(f"wrote {target.relative_to(HERE.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
