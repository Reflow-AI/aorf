---
type: dataset
title: Normalised events v2
description: Normalised event stream with the duplicate-row defect fixed.
version: v2
status: stable
resource: ./derived/events-v2.jsonl
generated: true
generator: /shared/build_events.py
storage: none
checksum: sha256:0c9a6e3b7f2d5a8c1e4b7f0d39a6e3b7f2d5a8c1e4b7f0d3f9a1c0e8b7d2a5c4
row_count: 47633
created: 2026-07-21
supersedes: ./events-v1.md
timestamp: 2026-07-21
---

# Provenance
Generated from [raw interactions](raw-interactions.md) by `shared/build_events.py` at commit `d4e5f6a`, which added ingest deduplication. Derived, not committed, regenerate with `python shared/build_events.py --out datasets/derived/events-v2.jsonl`.

# Changelog
- 2026-07-21 created, supersedes v1

# Known issues
None known.
