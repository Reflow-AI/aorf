---
type: dataset
title: Tokenised articles v1
description: First tokenisation pass over the article corpus. Withdrawn, contained duplicate rows.
version: v1
status: deprecated
resource: ./derived/tokens-v1.jsonl
generated: true
generator: /shared/build_tokens.py
storage: none
checksum: sha256:d5a8c1e4b7f0d39a6e3b7f2c41e6f80b9d3c7a2e5b8f1d40c9a6e3b7f2d5a8c1
row_count: 54120
created: 2026-07-02
superseded_by: ./tokens-v2.md
defect: "the paragraph splitter emitted each article twice, so 12% of rows are duplicates and every cluster size is inflated"
timestamp: 2026-07-20
---

# Provenance

Generated from the [news article corpus](articles-raw.md) by `shared/build_tokens.py` at commit
`a1b2c3d`. Derived, so not committed; gitignored under `datasets/derived/`.

# Format

JSONL, one object per article: `id`, `tokens`, `published_at`.

# Changelog

- 2026-07-02 created
- 2026-07-20 withdrawn, see [finding](../findings/tokens-v1-duplicate-rows.md)

# Known issues

12% duplicate rows. No result computed on this version is comparable to v2, and results that
used it have been marked invalidated rather than deleted.
