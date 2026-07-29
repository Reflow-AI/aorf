# Why NER missed the tokens that matter

| token pattern | example | NER label | should mask? |
|---|---|---|---|
| record id in title | `CASE-40192 - Review` | none | yes |
| shared doc name | `Case Tracker (Google Docs)` | ORG | no, appears in every case |
| status word | `In Progress` | none | no, but should be normalised |
| person name | `John Doe` | PERSON | yes |

NER caught 1 of the 4 categories, and mislabelled the shared container as an entity to mask,
which actively hurt by removing a useful signal.
