---
type: prior-art
title: Existing work on unsupervised topic modelling
description: Whether unsupervised topic discovery on news text is already solved well enough to adopt.
question: ./index.md
conclusion: partially_solved
searched_on: 2026-07-05
approved_by: sam
cost_usd: 12.40
valid_until: 2027-07-05
timestamp: 2026-07-05
---

# What is already known

Topic modelling on news text is a mature area. LDA and NMF are well documented with standard
implementations, and embedding-then-clustering pipelines are widely reported to beat them on
short text. Adjusted Rand Index against a labelled subset is the conventional evaluation.

# What is not settled for us

Published comparisons almost always evaluate against the corpus's own category labels, which are
coarse — four to twenty categories. Our editors work at a much finer grain, where two articles
about different companies in the same sector are different topics. No source we found evaluates
at that granularity, and none addresses proper nouns splitting otherwise-identical topics.

# Conclusion

Partially solved. Adopt the embedding-then-clustering shape rather than inventing one, and treat
the granularity problem and the proper-noun problem as the parts that are actually open.

# Cost note

Approved before running; cost about 12 USD in API spend. Expected to stay valid for a year, so do
not re-run before 2027-07-05.

# Sources

- Topic modelling survey literature
- Published embedding-plus-clustering comparisons on short text
