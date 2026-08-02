"""Provenance subpackage.

Reusable helpers that connect ProofStudio artifacts (generated media, prompt
packets, attempt ledgers, provider notes) to the durable Backblaze B2 system of
record through the Genblaze pipeline + manifest layer.

PS-007 introduces:

- :mod:`proofstudio.provenance.genblaze_store` — reusable B2 + Genblaze upload,
  manifest write, read-back, and verification helper based on the proven
  PS-001A / PS-004 / PS-005 working pattern.
"""

from proofstudio.provenance.genblaze_store import (
    GenblazeRunResult,
    GenblazeStore,
    build_backblaze_backend,
)

__all__ = [
    "GenblazeStore",
    "GenblazeRunResult",
    "build_backblaze_backend",
]
