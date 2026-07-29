---
type: dataset
title: Normalised events v1
description: First normalisation pass over raw interactions. Withdrawn, contained duplicate rows.
version: v1
status: deprecated
resource: ./derived/events-v1.jsonl
generated: true
generator: /shared/build_events.py
storage: none
checksum: sha256:d5a8c1e4b7f0d39a6e3b7f2c41e6f80b9d3c7a2e5b8f1d40c9a6e3b7f2d5a8c1
row_count: 54120
created: 2026-07-02
superseded_by: ./events-v2.md
defect: "double ingest produced 12% duplicate event rows, inflating cluster sizes"
timestamp: 2026-07-20
---

# Provenance
Generated from [raw interactions](raw-interactions.md) by `shared/build_events.py` at commit `a1b2c3d`. Derived, so not committed. Gitignored under `datasets/derived/`.

# Changelog
- 2026-07-02 created
- 2026-07-20 withdrawn, see [finding](../findings/events-v1-duplicate-rows.md)

# Known issues
12% duplicate rows. Any result computed on this version is not comparable to v2.
