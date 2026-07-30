---
type: dataset
title: Tokenised articles v2
description: Tokenised article text with the duplicate-row defect fixed.
version: v2
status: stable
resource: ./derived/tokens-v2.jsonl
generated: true
generator: /shared/build_tokens.py
storage: none
checksum: sha256:0c9a6e3b7f2d5a8c1e4b7f0d39a6e3b7f2d5a8c1e4b7f0d3f9a1c0e8b7d2a5c4
row_count: 47633
created: 2026-07-21
supersedes: ./tokens-v1.md
timestamp: 2026-07-21
---

# Provenance

Generated from the [news article corpus](articles-raw.md) by `shared/build_tokens.py` at commit
`d4e5f6a`, which fixed the double-emit in the paragraph splitter. Derived and not committed;
regenerate with:

```
python shared/build_tokens.py --out datasets/derived/tokens-v2.jsonl
```

# Format

JSONL, one object per article: `id`, `tokens`, `published_at`.

# Changelog

- 2026-07-21 created, supersedes v1

# Known issues

None known.
