"""ProofStudio backend API skeleton subpackage (PS-008).

PS-008 exposes the product concepts (campaign, generation run, provider
attempts, generated assets, manifest evidence) through a thin API/service
layer built on top of an in-memory store.

Layering (see specs/16-ps-008-backend-api-skeleton.md):

- ``models``    - Pydantic request/response records (CampaignCreate, RunRecord,
                  AttemptRecord, ManifestRecord, ErrorResponse, ...).
- ``store``     - In-memory store. No production database in this slice.
- ``services``  - Business logic, separated from route handlers so it can be
                  exercised directly without an HTTP server.
- ``app``       - FastAPI app wiring endpoints to the service layer. If
                  FastAPI is not importable at runtime, ``app`` still exposes an
                  importable ``app`` / ``create_app()`` placeholder.

Truth boundary for PS-008:

- No live provider calls by default.
- No B2 calls.
- No Genblaze calls.
- No fake generated media.
- No authentication, no deployment, no frontend.

The default ``POST /runs`` path is a dry run: it records a run with status
``dry_run_created`` and never contacts a provider, B2, or Genblaze.
"""

from __future__ import annotations

# PS-041E0: the exact selective Genblaze v0.7.0 connector compatibility guard MUST
# run before any ProofStudio module that directly or transitively imports
# Genblaze. ``proofstudio.api.services`` imports ``genblaze_external_adapter``
# (which imports ``genblaze_core``), ``live_bridge`` (providers +
# ``genblaze_store``), ``archive`` (``genblaze_store``) and ``store``
# (``genblaze_external_adapter``); therefore the guard has to execute at the
# top of this package, before any of those submodules is imported.
# ``genblaze_runtime`` itself is stdlib-only (``importlib.metadata`` +
# ``typing``); it imports no Genblaze package, no provider, no boto3, no
# network client, and no environment configuration.
#
# This is the one additional repository file PS-041E0 owns beyond the original
# seven, justified by the direct, reproducible dependency-security requirement
# that the package initializer imports Genblaze-dependent submodules before
# ``app`` is reached. Without wiring the guard here, a missing/mismatched
# Genblaze distribution would raise an uncontrolled ``ImportError`` (with a
# stack trace) from ``services`` / ``genblaze_external_adapter`` instead of the
# controlled ``GenblazeRuntimeVersionError``.
from proofstudio.api.genblaze_runtime import verify_runtime_versions_cached

# Execute once per process; the cached result is reused by
# ``proofstudio.api.app.create_app()`` so the underlying metadata check runs
# exactly once during normal startup. A missing or mismatched distribution
# raises ``GenblazeRuntimeVersionError`` here, before ``services`` /
# ``genblaze_external_adapter`` / any route becomes importable.
verify_runtime_versions_cached()

from proofstudio.api.models import (
    AssetRecord,
    AttemptRecord,
    CampaignCreate,
    CampaignRecord,
    ErrorResponse,
    ManifestRecord,
    RunCreate,
    RunRecord,
)
from proofstudio.api.services import (
    NotFoundError,
    ProofStudioService,
    create_default_service,
)
from proofstudio.api.store import InMemoryStore

try:  # pragma: no cover - exercised at import time
    from proofstudio.api.app import app, create_app
except Exception:  # pragma: no cover - FastAPI not importable in this env
    app = None  # type: ignore[assignment]
    create_app = None  # type: ignore[assignment]

__all__ = [
    "AssetRecord",
    "AttemptRecord",
    "CampaignCreate",
    "CampaignRecord",
    "ErrorResponse",
    "ManifestRecord",
    "RunCreate",
    "RunRecord",
    "InMemoryStore",
    "NotFoundError",
    "ProofStudioService",
    "create_default_service",
    "app",
    "create_app",
]
