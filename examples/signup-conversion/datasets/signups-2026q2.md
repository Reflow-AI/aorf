---
type: dataset
title: Q2 2026 signups
description: One row per trial signup with funnel step timestamps.
version: v1
status: stable
resource: ./signups-2026q2.csv
generated: false
storage: git-lfs
checksum: sha256:3f9a1c0e8b7d2a5c41e6f80b9d3c7a2e5b8f1d40c9a6e3b7f2d5a8c1e4b7f0d39
row_count: 18432
created: 2026-07-01
timestamp: 2026-07-01
---

# Provenance
Exported from the product analytics warehouse on 2026-07-01. Source of truth, committed via git LFS.

# Format
CSV, 12 columns, one row per signup.

# Known issues
Mobile app signups before 2026-05-12 have a null `activation_at`.
