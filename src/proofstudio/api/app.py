"""FastAPI app for the PS-008 backend API skeleton.

Wires the required endpoints (see specs/16-ps-008-backend-api-skeleton.md
section 6) to the service layer in ``services.py``. The service layer holds
all business logic; this module only translates HTTP <-> service calls and
maps service errors to clean HTTP error envelopes.

Endpoints:

- ``GET  /health``
- ``GET  /version``
- ``POST /campaigns``
- ``GET  /campaigns/{campaign_id}``
- ``POST /runs``
- ``GET  /runs/{run_id}``
- ``GET  /runs/{run_id}/attempts``
- ``GET  /runs/{run_id}/assets``
- ``GET  /runs/{run_id}/manifest``
- ``GET  /runs/{run_id}/passport``

If FastAPI is not importable in the runtime environment, this module still
exposes ``app`` (None) and ``create_app()`` (returns None) plus
``FRAMEWORK_MODE == "service_only"`` so callers can fall back to direct
service-layer calls. The PS-008 smoke script uses this flag to pick the right
exercise path.
"""

from __future__ import annotations

import hmac
import logging
import os
import re
import unicodedata
from typing import Any

# PS-041E0: import the stdlib-only guard BEFORE any ProofStudio module that
# directly or transitively imports Genblaze. ``genblaze_runtime`` imports only
# ``importlib.metadata`` and ``typing``; it never imports Genblaze packages,
# providers, boto3, network clients, or environment configuration.
from proofstudio.api.genblaze_runtime import (
    GenblazeRuntimeVersionError,
    verify_runtime_versions_cached,
)

# PS-041E0: execute the exact-equality runtime-version assertion once at module
# import, BEFORE any Genblaze-dependent ProofStudio module is imported. The
# cached verifier is shared with ``proofstudio.api.__init__`` (which runs
# first), so the underlying ``importlib.metadata`` check runs exactly once per
# process even when ``create_app()`` is invoked repeatedly. A missing or
# mismatched distribution raises :class:`GenblazeRuntimeVersionError` here, so
# ``proofstudio.api.services`` / ``genblaze_external_adapter`` and every route
# stay unimported on failure.
verify_runtime_versions_cached()

# Only after the guard has passed is it safe to import Genblaze-dependent
# ProofStudio modules. ``models`` is Genblaze-free but is grouped here per the
# PS-041E0 startup order; ``services``, ``store``, ``archive``, ``live_bridge``,
# and ``genblaze_external_adapter`` transitively import ``genblaze_core`` or
# ``proofstudio.provenance.genblaze_store``.
from proofstudio.api.models import (
    SLICE_ID,
    AssetRecord,
    AttemptRecord,
    CampaignCreate,
    CampaignRecord,
    ErrorResponse,
    InternalErrorResponse,
    InternalPassportResponse,
    InternalProofRoomResponse,
    ManifestRecord,
    RunCreate,
    RunRecord,
)
from proofstudio.api.services import (
    FRAMEWORK_MODE,
    NotFoundError,
    ProofStudioService,
    create_default_service,
)
from proofstudio.api.genblaze_external_adapter import (
    ImportValidationError,
    parse_bundle_bytes,
)

try:
    from fastapi import FastAPI, Request
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from fastapi.testclient import TestClient

    _FASTAPI_AVAILABLE = True
except Exception:  # pragma: no cover - FastAPI not importable in this env
    _FASTAPI_AVAILABLE = False
    FastAPI = None  # type: ignore[assignment, misc]
    Request = None  # type: ignore[assignment, misc]
    CORSMiddleware = None  # type: ignore[assignment, misc]
    JSONResponse = None  # type: ignore[assignment, misc]
    TestClient = None  # type: ignore[assignment, misc]


# PS-013A: explicit local demo frontend origins allowed by CORS. We use an
# explicit allow-list (never a wildcard with credentials) so the Vite dev
# server (5173) and the Vite preview server (4173) on both 127.0.0.1 and
# localhost can reach the FastAPI backend safely for local demos. These map to
# the two-terminal local runbook documented in apps/web/README.md.
LOCAL_DEMO_CORS_ORIGINS: tuple[str, ...] = (
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://127.0.0.1:4173",
    "http://localhost:4173",
)

# PS-017: name of the env var that adds production frontend origins to the
# CORS allow-list. See docs/deployment/cors-and-security.md.
CORS_ORIGINS_ENV_VAR = "PROOFSTUDIO_CORS_ORIGINS"
INTERNAL_SERVICE_TOKEN_ENV_VAR = "PROOFSTUDIO_INTERNAL_SERVICE_TOKEN"
INTERNAL_SERVICE_TOKEN_HEADER = "X-ProofStudio-Internal-Token"
IMPORT_OPERATOR_TOKEN_ENV_VAR = "PROOFSTUDIO_IMPORT_OPERATOR_TOKEN"
IMPORT_OPERATOR_TOKEN_HEADER = "X-ProofStudio-Import-Token"
PROOF_IDENTIFIER_MAX_LENGTH = 128
PROOF_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_PLACEHOLDER_MARKERS = ("change_me", "replace-with", "your-", "placeholder", "example.")

logger = logging.getLogger("proofstudio.api")


def _resolve_cors_origins() -> list[str]:
    """Return the CORS allow-list, merging local defaults with env origins.

    Reads ``PROOFSTUDIO_CORS_ORIGINS`` (comma-separated). If unset, returns the
    local demo origins only (backward compatible with PS-013A). If set to a
    wildcard (``*``), the wildcard is refused and the local allow-list is used,
    because wildcard production CORS is unsafe in front of a backend that can
    issue live provider/B2 runs. See docs/deployment/cors-and-security.md.
    """
    origins: list[str] = list(LOCAL_DEMO_CORS_ORIGINS)
    raw = os.environ.get(CORS_ORIGINS_ENV_VAR, "").strip()
    if not raw:
        return origins
    # Wildcard production CORS is never silently enabled.
    if raw.strip() == "*":
        logger.warning(
            "PROOFSTUDIO_CORS_ORIGINS is '*'; refusing wildcard production "
            "CORS. Falling back to local demo origins only."
        )
        return origins
    for piece in raw.split(","):
        origin = piece.strip()
        if origin and origin not in origins:
            origins.append(origin)
    return origins


def _not_found_response(exc: NotFoundError) -> "JSONResponse":
    body = ErrorResponse(
        error="not_found",
        detail=exc.detail,
        resource=exc.resource,
        resource_id=exc.resource_id,
    )
    assert JSONResponse is not None
    return JSONResponse(status_code=404, content=body.model_dump())


def _safe_error(status: int, code: str, message: str) -> "JSONResponse":
    assert JSONResponse is not None
    body = InternalErrorResponse(code=code, message=message)
    return JSONResponse(status_code=status, content=body.model_dump())


def _valid_identifier(value: str) -> bool:
    return (
        isinstance(value, str)
        and value == unicodedata.normalize("NFC", value)
        and PROOF_IDENTIFIER_PATTERN.fullmatch(value) is not None
    )


def _configured_internal_token() -> str | None:
    value = os.environ.get(INTERNAL_SERVICE_TOKEN_ENV_VAR, "")
    lowered = value.strip().lower()
    if len(value) < 24 or value != value.strip() or any(marker in lowered for marker in _PLACEHOLDER_MARKERS):
        return None
    return value


def _protected_read_token(request: "Request") -> "JSONResponse | None":
    expected = _configured_internal_token()
    supplied = request.headers.get(INTERNAL_SERVICE_TOKEN_HEADER)
    if expected is None or supplied is None or not hmac.compare_digest(
        expected.encode("utf-8"), supplied.encode("utf-8")
    ):
        return _safe_error(401, "internal_auth_required", "Internal proof read authentication is required.")
    return None


def _configured_operator_token() -> str | None:
    value = os.environ.get(IMPORT_OPERATOR_TOKEN_ENV_VAR, "")
    lowered = value.strip().lower()
    if len(value) < 24 or value != value.strip() or any(marker in lowered for marker in _PLACEHOLDER_MARKERS):
        return None
    return value


def _protected_operator_token(request: "Request") -> "JSONResponse | None":
    expected = _configured_operator_token()
    supplied = request.headers.get(IMPORT_OPERATOR_TOKEN_HEADER)
    if expected is None or supplied is None or not hmac.compare_digest(
        expected.encode("utf-8"), supplied.encode("utf-8")
    ):
        return _safe_error(401, "operator_auth_required", "Internal import operator authentication is required.")
    return None


def _build_app(service: ProofStudioService) -> "FastAPI":
    assert FastAPI is not None
    application = FastAPI(
        title="ProofStudio API",
        version="0.1.0",
        description=(
            "ProofStudio backend API. Exposes campaign, run, provider-attempt, "
            "asset, and manifest concepts over an in-memory store. Dry-run by "
            "default: no live provider calls, no B2, no Genblaze, no fake "
            "media. PS-009 adds an explicit run_live=true bridge to the PS-007 "
            "live provider-router chain."
        ),
    )

    # PS-013A: local demo CORS. Explicit allow-list of local frontend origins,
    # all methods, all headers, no credentials. Safe for a local judge/demo
    # flow; never uses wildcard credentials. This is what lets the browser at
    # http://127.0.0.1:5173 fetch http://127.0.0.1:8000 without a CORS block.
    #
    # PS-017: also merges production origins from PROOFSTUDIO_CORS_ORIGINS
    # (see docs/deployment/cors-and-security.md). Wildcards are refused.
    assert CORSMiddleware is not None
    application.add_middleware(
        CORSMiddleware,
        allow_origins=_resolve_cors_origins(),
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=False,
    )

    @application.get("/health", tags=["meta"])
    def health() -> dict[str, Any]:
        return service.health()

    @application.get("/version", tags=["meta"])
    def version() -> dict[str, Any]:
        return service.version()

    @application.post("/campaigns", tags=["campaigns"], status_code=201)
    def create_campaign(payload: CampaignCreate) -> dict[str, Any]:
        return service.create_campaign(payload)

    @application.get("/campaigns/{campaign_id}", tags=["campaigns"], response_model=None)
    def get_campaign(campaign_id: str, request: Request) -> dict[str, Any] | JSONResponse:
        if not _valid_identifier(campaign_id):
            return _safe_error(400, "invalid_request", "A valid proof identifier is required.")
        if denied := _protected_read_token(request):
            return denied
        try:
            return service.get_campaign(campaign_id)
        except NotFoundError as exc:
            return _not_found_response(exc)

    @application.post("/runs", tags=["runs"], status_code=201, response_model=None)
    def create_run(payload: RunCreate) -> dict[str, Any] | JSONResponse:
        try:
            return service.create_run(payload)
        except NotFoundError as exc:
            return _not_found_response(exc)

    @application.get("/runs/{run_id}", tags=["runs"], response_model=None)
    def get_run(run_id: str, request: Request) -> dict[str, Any] | JSONResponse:
        if not _valid_identifier(run_id):
            return _safe_error(400, "invalid_request", "A valid proof identifier is required.")
        if denied := _protected_read_token(request):
            return denied
        try:
            return service.get_run(run_id)
        except NotFoundError as exc:
            return _not_found_response(exc)

    @application.get("/runs/{run_id}/attempts", tags=["runs"], response_model=None)
    def get_run_attempts(run_id: str, request: Request) -> dict[str, Any] | JSONResponse:
        if not _valid_identifier(run_id):
            return _safe_error(400, "invalid_request", "A valid proof identifier is required.")
        if denied := _protected_read_token(request):
            return denied
        try:
            return service.get_run_attempts(run_id)
        except NotFoundError as exc:
            return _not_found_response(exc)

    @application.get("/runs/{run_id}/assets", tags=["runs"], response_model=None)
    def get_run_assets(run_id: str, request: Request) -> dict[str, Any] | JSONResponse:
        if not _valid_identifier(run_id):
            return _safe_error(400, "invalid_request", "A valid proof identifier is required.")
        if denied := _protected_read_token(request):
            return denied
        try:
            return service.get_run_assets(run_id)
        except NotFoundError as exc:
            return _not_found_response(exc)

    @application.get("/runs/{run_id}/manifest", tags=["runs"], response_model=None)
    def get_run_manifest(run_id: str, request: Request) -> dict[str, Any] | JSONResponse:
        if not _valid_identifier(run_id):
            return _safe_error(400, "invalid_request", "A valid proof identifier is required.")
        if denied := _protected_read_token(request):
            return denied
        try:
            return service.get_run_manifest(run_id)
        except NotFoundError as exc:
            return _not_found_response(exc)

    @application.get("/runs/{run_id}/passport", tags=["runs"], response_model=None)
    def get_run_passport(run_id: str) -> dict[str, Any] | JSONResponse:
        from proofstudio.api.durable_passport import golden_demo_run_id, try_golden_demo_passport

        if _valid_identifier(run_id) and run_id == golden_demo_run_id():
            passport = try_golden_demo_passport(service, run_id)
            if passport is not None:
                return passport
        return _safe_error(404, "proof_not_found", "Proof was not found.")

    @application.get(
        "/internal/campaigns/{campaign_id}/proof-room",
        tags=["internal"],
        response_model=InternalProofRoomResponse,
    )
    def get_internal_proof_room(
        campaign_id: str,
        request: Request,
        runId: str | None = None,
    ) -> InternalProofRoomResponse | JSONResponse:
        if not _valid_identifier(campaign_id) or (runId is not None and not _valid_identifier(runId)):
            return _safe_error(400, "invalid_request", "A valid proof identifier is required.")
        if denied := _protected_read_token(request):
            return denied
        try:
            campaign = service.get_campaign(campaign_id)["campaign"]
            if runId is None:
                return InternalProofRoomResponse(campaign=campaign)
            run = service.get_run(runId)["run"]
            if run.get("campaign_id") != campaign_id:
                return _safe_error(404, "proof_not_found", "Proof was not found.")
            safe_run = {key: value for key, value in run.items() if not key.startswith("local_")}
            return InternalProofRoomResponse(
                campaign=campaign,
                selected_run=safe_run,
                attempts=service.get_run_attempts(runId)["attempts"],
                assets=service.get_run_assets(runId)["assets"],
                manifest=service.get_run_manifest(runId),
                passport_ref=f"/account/campaigns/{campaign_id}/passport/{runId}",
            )
        except NotFoundError:
            return _safe_error(404, "proof_not_found", "Proof was not found.")

    @application.get(
        "/internal/campaigns/{campaign_id}/runs/{run_id}/passport",
        tags=["internal"],
        response_model=InternalPassportResponse,
    )
    def get_internal_passport(
        campaign_id: str,
        run_id: str,
        request: Request,
    ) -> InternalPassportResponse | JSONResponse:
        if not _valid_identifier(campaign_id) or not _valid_identifier(run_id):
            return _safe_error(400, "invalid_request", "A valid proof identifier is required.")
        if denied := _protected_read_token(request):
            return denied
        try:
            service.get_campaign(campaign_id)
            run = service.get_run(run_id)["run"]
            if run.get("campaign_id") != campaign_id:
                return _safe_error(404, "proof_not_found", "Proof was not found.")
            return InternalPassportResponse(
                campaign_access_scope=campaign_id,
                passport=service.get_run_passport(run_id, source="memory"),
            )
        except NotFoundError:
            return _safe_error(404, "proof_not_found", "Proof was not found.")

    @application.post(
        "/internal/operator/campaigns/{campaign_id}/genblaze-bundles",
        tags=["internal"],
        response_model=None,
    )
    async def import_genblaze_bundle(campaign_id: str, request: Request) -> dict[str, Any] | JSONResponse:
        if not _valid_identifier(campaign_id):
            return _safe_error(400, "invalid_request", "A valid proof identifier is required.")
        if denied := _protected_operator_token(request):
            return denied
        declared = request.headers.get("content-length")
        if declared is not None:
            try:
                if int(declared) > 1_048_576:
                    return _safe_error(413, "bundle_too_large", "The import bundle exceeds the permitted size.")
            except ValueError:
                return _safe_error(400, "invalid_request", "The request metadata is invalid.")
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > 1_048_576:
                return _safe_error(413, "bundle_too_large", "The import bundle exceeds the permitted size.")
        raw = bytes(body)
        try:
            payload = parse_bundle_bytes(raw)
            result = service.import_genblaze_bundle(campaign_id, payload)
        except ImportValidationError as exc:
            messages = {
                "campaign_not_found": "The campaign was not found.",
                "import_conflict": "The import conflicts with existing evidence.",
                "golden_namespace_conflict": "The import conflicts with protected evidence.",
                "b2_import_disabled": "The optional import storage dependency is unavailable.",
            }
            return _safe_error(exc.status, exc.code, messages.get(exc.code, "The import bundle was rejected."))
        return JSONResponse(status_code=201 if result.created else 200, content=result.model_dump(mode="json"))

    @application.get("/internal/campaigns/{campaign_id}/import-bundles", tags=["internal"], response_model=None)
    def list_import_bundles(campaign_id: str, request: Request) -> dict[str, Any] | JSONResponse:
        if not _valid_identifier(campaign_id):
            return _safe_error(400, "invalid_request", "A valid proof identifier is required.")
        if denied := _protected_read_token(request):
            return denied
        try:
            bundles = service.list_imported_bundles(campaign_id)
            return {"source": "proof_api", "campaign_access_scope": campaign_id,
                    "bundles": [bundle.model_dump(mode="json") for bundle in bundles]}
        except NotFoundError:
            return _safe_error(404, "proof_not_found", "Proof was not found.")

    @application.get("/internal/campaigns/{campaign_id}/import-bundles/{bundle_id}", tags=["internal"], response_model=None)
    def get_import_bundle(campaign_id: str, bundle_id: str, request: Request) -> dict[str, Any] | JSONResponse:
        if not _valid_identifier(campaign_id) or not _valid_identifier(bundle_id):
            return _safe_error(400, "invalid_request", "A valid proof identifier is required.")
        if denied := _protected_read_token(request):
            return denied
        try:
            result = service.get_imported_bundle(campaign_id, bundle_id)
            return {"source": "proof_api", "campaign_access_scope": campaign_id,
                    "lineage": result.model_dump(mode="json")}
        except NotFoundError:
            return _safe_error(404, "proof_not_found", "Proof was not found.")

    @application.get("/internal/campaigns/{campaign_id}/import-bundles/{bundle_id}/passport", tags=["internal"], response_model=None)
    def get_import_bundle_passport(campaign_id: str, bundle_id: str, request: Request) -> dict[str, Any] | JSONResponse:
        if not _valid_identifier(campaign_id) or not _valid_identifier(bundle_id):
            return _safe_error(400, "invalid_request", "A valid proof identifier is required.")
        if denied := _protected_read_token(request):
            return denied
        try:
            passport = service.get_imported_passport(campaign_id, bundle_id)
            return {"source": "proof_api", "campaign_access_scope": campaign_id,
                    "passport": passport.model_dump(mode="json")}
        except NotFoundError:
            return _safe_error(404, "proof_not_found", "Proof was not found.")

    return application


def create_app(service: ProofStudioService | None = None) -> "FastAPI | None":
    """Build a FastAPI app bound to ``service``.

    Returns ``None`` when FastAPI is not importable (service-only mode). The
    service layer remains usable directly in that case.

    PS-041E0: the exact selective Genblaze v0.7.0 connector compatibility guard runs once at
    package import (``proofstudio.api.__init__``) and again here returns the
    cached verified result without re-querying ``importlib.metadata``. It is
    therefore safe to call repeatedly (e.g. from tests) and a partial upgrade
    still fails closed before any worker becomes ready. Mixed worker versions
    are forbidden.
    """
    if not _FASTAPI_AVAILABLE:
        return None
    verify_runtime_versions_cached()
    return _build_app(service or create_default_service())


# Module-level singleton app for ``uvicorn proofstudio.api.app:app`` and for
# the smoke script's TestClient path. In service-only mode this is None.
app: "FastAPI | None" = create_app() if _FASTAPI_AVAILABLE else None


__all__ = [
    "app",
    "create_app",
    "FRAMEWORK_MODE",
    "LOCAL_DEMO_CORS_ORIGINS",
    "CORS_ORIGINS_ENV_VAR",
    "IMPORT_OPERATOR_TOKEN_ENV_VAR",
    "_resolve_cors_origins",
    "SLICE_ID",
    "ErrorResponse",
    "CampaignCreate",
    "CampaignRecord",
    "RunCreate",
    "RunRecord",
    "AttemptRecord",
    "AssetRecord",
    "ManifestRecord",
    "NotFoundError",
    "ProofStudioService",
    "create_default_service",
]
