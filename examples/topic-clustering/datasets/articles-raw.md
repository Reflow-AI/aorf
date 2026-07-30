---
type: dataset
title: News article corpus
description: Unmodified article text and publication dates, the source of truth for this research.
version: "2026-06"
status: stable
resource: ./raw/articles-2026-06.jsonl
generated: false
storage: git-lfs
checksum: sha256:8c1e4b7f0d39a6e3b7f2d5a8c1e4b7f0d3f9a1c0e8b7d2a5c41e6f80b9d3c7a2
row_count: 184203
created: 2026-07-01
timestamp: 2026-07-01
---

# Provenance

Public news corpus, articles published January 2024 to June 2026, collected once and never
modified. Committed via git LFS so the repository has no external dependency.

# Format

JSONL, one object per article: `id`, `published_at`, `headline`, `body`, `source`.

# Known issues

Roughly 3% of articles have an empty body and only a headline. Wire-service copy appears more
than once under different ids, which is genuine duplication in the source rather than an ingest
defect.
