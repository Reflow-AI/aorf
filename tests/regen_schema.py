"""Regenerate spec/aorf-v0.1.schema.json from spec.py.

    python tests/regen_schema.py

The schema is committed so the website can serve it and consumers can pin it, but it is
generated so it cannot become a second definition of the same fields.
"""

from __future__ import annotations

import json
from pathlib import Path

from aorf import spec

TARGET = Path(__file__).resolve().parent.parent / "spec" / "aorf-v0.1.schema.json"


def main() -> int:
    TARGET.write_text(
        json.dumps(spec.json_schema(), indent=2, sort_keys=False) + "\n", encoding="utf-8"
    )
    print(f"wrote {TARGET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
