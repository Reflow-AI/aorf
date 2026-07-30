# Shared code

Used by more than one experiment. Do not copy these into experiment folders.

- `build_tokens.py` tokenises the raw corpus into the tokens dataset
- `metrics.py` cluster quality metrics (ARI, leakage, purity)
- `load.py` dataset loading helpers

Experiments record the commit of this folder they ran against, in `code.shared_ref`. This
directory is a payload directory: nothing in it is an AORF document.
