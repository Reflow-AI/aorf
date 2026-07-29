# Shared code

Used by more than one experiment. Do not copy these into experiment folders.

- `build_events.py` normalises raw interactions into the events dataset
- `metrics.py` cluster quality metrics (ARI, leakage, purity)
- `load.py` dataset loading helpers

Experiments record the commit of this folder they ran against, in `code.shared_ref`.
