---
type: dataset
title: Raw interaction events
description: Unmodified UI interaction event stream, the source of truth for this research.
version: "2026-06"
status: stable
resource: ./raw/interactions-2026-06.jsonl
generated: false
storage: git-lfs
checksum: sha256:8c1e4b7f0d39a6e3b7f2d5a8c1e4b7f0d3f9a1c0e8b7d2a5c41e6f80b9d3c7a2
row_count: 2841903
created: 2026-07-01
timestamp: 2026-07-01
---

# Provenance
Captured by the desktop agent, June 2026, 42 users. Committed via git LFS so the repo is self-contained with no external dependency.

# Format
JSONL. One object per event: timestamp, user_id, app, window_title, action_type, coordinates, text_content.

# Known issues
Window titles are truncated at 120 characters. Some apps report no window title at all.
