"""Pydantic request/response models for the PS-008 backend API skeleton.

These models are the first-class product-concept vocabulary exposed by the
ProofStudio API:

- CampaignCreate / CampaignRecord - the campaign (brief container)
- RunCreate / RunRecord           - a generation run request and its record
- AttemptRecord                   - a provider attempt (PS-006 20-field shape)
- AssetRecord                     - a generated/stored asset reference
- ManifestRecord                  - Genblaze manifest metadata for a run
- ErrorResponse                   - clear, non-crashing error envelope

Pydantic v2 is used because FastAPI is available in the project venv. If
Pydantic were unavailable the service layer would still work with plain
dicts; these models exist to give the API a typed, validated surface and to
keep attempt records aligned with the PS-006 20-field ProviderAttempt
contract (see specs/14-ps-006-provider-router-core.md section 7 and
specs/15-ps-007-live-provider-router-chain.md section 9).

Truth boundary: these models carry metadata and references only. They never
carry raw generated media bytes and they never fabricate provenance.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

SLICE_ID = "PS-008"
SERVICE_NAME = "proofstudio-api"

# PS-010 run-archive schema. Bumped only if the archive shape changes in a
# way that breaks rehydration. Rehydrate validates this before restoring.
ARCHIVE_SCHEMA_VERSION = "ps-010.1"

# Honest archive storage modes reported in the PS-010 summary.
# ``b2_object_content`` means the archive bytes were actually read back from B2.
# ``local_after_b2_store`` means the archive was stored as a real B2 asset but
# rehydration read the local copy (documented fallback).
ARCHIVE_STORAGE_MODE_B2 = "b2_object_content"
ARCHIVE_STORAGE_MODE_LOCAL = "local_after_b2_store"

ARCHIVE_TRUTH_BOUNDARY = (
    "PS-010 proves ProofStudio can archive a run into a durable artifact and "
    "reconstruct its API readback state from that evidence without rerunning "
    "providers. It does not prove production-database persistence, multi-user "
    "recovery, auth/security, legal authenticity, C2PA authenticity, or "
    "semantic truth."
)

# Canonical run statuses. Dry-run is the default and must never claim a live
# provider executed or produced media.
RUN_STATUS_DRY_RUN_CREATED = "dry_run_created"
RUN_STATUS_QUEUED = "queued"
RUN_STATUS_LIVE_NOT_SUPPORTED = "live_execution_not_supported_in_ps008"
RUN_STATUS_FAILED = "failed"

# PS-009 live run statuses. ``live_running`` is the transient state set before
# the live bridge executes; the terminal states below are what callers observe.
# Only an honestly successful live run (providers returned real media AND B2 +
# Genblaze storage verified) may carry ``live_completed``.
RUN_STATUS_LIVE_RUNNING = "live_running"
RUN_STATUS_LIVE_COMPLETED = "live_completed"
RUN_STATUS_LIVE_FAILED = "live_failed"
RUN_STATUS_LIVE_BLOCKED = "live_blocked"

LIVE_RUN_STATUSES = frozenset(
    {
        RUN_STATUS_LIVE_RUNNING,
        RUN_STATUS_LIVE_COMPLETED,
        RUN_STATUS_LIVE_FAILED,
        RUN_STATUS_LIVE_BLOCKED,
    }
)

CAMPAIGN_STATUS_CREATED = "created"

# The 20 required ProviderAttempt fields per PS-006 section 7 / PS-007 section 9.
# AttemptRecord mirrors this contract so live attempts from the PS-007 pipeline
# can be stored verbatim in later slices without a schema migration.
REQUIRED_ATTEMPT_FIELDS: tuple[str, ...] = (
    "attempt_id",
    "attempt_index",
    "provider",
    "model",
    "api_method",
    "job_type",
    "status",
    "normalized_status",
    "started_at",
    "finished_at",
    "latency_ms",
    "retryable",
    "fallback_allowed",
    "skip_reason",
    "raw_error_type",
    "sanitized_error_message",
    "estimated_cost",
    "free_or_paid",
    "output_asset_refs",
    "notes",
)


class _BaseAPIModel(BaseModel):
    """Shared Pydantic config: forbid surprise leakage, allow extras where
    forward-compatibility is useful."""

    model_config = ConfigDict(extra="ignore")


# ---------------------------------------------------------------------------
# Campaign
# ---------------------------------------------------------------------------


class CampaignCreate(_BaseAPIModel):
    """Request body for POST /campaigns.

    ``name`` and ``brief`` are required; the rest are optional product context
    fields. No media, no provider selection, no live calls happen here.
    """

    name: str = Field(..., min_length=1, description="Human-readable campaign name.")
    brief: str = Field(..., min_length=1, description="Campaign brief text.")
    target_audience: str | None = Field(default=None)
    platform: str | None = Field(default=None)
    objective: str | None = Field(default=None)


class CampaignRecord(_BaseAPIModel):
    """Stored campaign record returned by GET /campaigns/{id} and POST /campaigns."""

    campaign_id: str
    name: str
    brief: str
    target_audience: str | None = None
    platform: str | None = None
    objective: str | None = None
    status: str = CAMPAIGN_STATUS_CREATED
    created_at: str
    slice: str = SLICE_ID


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------


class RunCreate(_BaseAPIModel):
    """Request body for POST /runs.

    Defaults are intentionally safe:

    - ``dry_run`` defaults to ``True``
    - ``run_live`` defaults to ``False``

    A dry run MUST NOT trigger live provider calls, B2 uploads, or fake media.
    Live execution is an explicit opt-in and is not implemented in PS-008
    (later slices connect the service layer to the PS-007 pipeline).
    """

    campaign_id: str = Field(..., min_length=1)
    prompt: str | None = Field(default=None)
    budget_mode: str | None = Field(default="free-only")
    dry_run: bool = Field(default=True)
    run_live: bool = Field(default=False)


class RunRecord(_BaseAPIModel):
    """Stored run record returned by GET /runs/{id} and POST /runs.

    Carries the product concepts that later slices populate:

    - ``selected_provider`` / ``selected_model`` / ``fallback_used``
    - ``prompt_packet_ref`` / ``attempt_ledger_ref`` / ``provider_note_ref``
    - ``manifest_uri`` (B2-backed manifest, present only after a live run)
    - ``asset_count`` and ``attempt_count``
    - ``links`` for discoverability of sub-resources

    PS-009 adds live-run metadata fields:

    - ``api_method`` / ``job_type`` - how the selected provider was called
    - ``attempts`` / ``assets`` - the full PS-006 attempt ledger and asset
      refs captured by the live bridge (the same data is also registered as
      sub-resources for the attempts/assets readback endpoints)
    - ``manifest_hash`` / ``in_memory_manifest_verify`` /
      ``stored_manifest_verify`` / ``transfer_failures`` /
      ``stored_transfer_failures`` - the Genblaze manifest verification
      evidence for a live-completed run
    - ``local_image`` / ``local_prompt_packet`` / ``local_attempt_ledger`` /
      ``local_provider_note`` - on-disk artifact paths for a live run
    - ``truth_boundary`` - the honesty string inherited from the live bridge
    - ``error`` / ``blocked_reason`` - present only for live_failed /
      live_blocked runs so callers never have to guess why a live run stopped
    """

    run_id: str
    campaign_id: str
    status: str
    prompt: str | None = None
    budget_mode: str = "free-only"
    dry_run: bool = True
    run_live: bool = False
    selected_provider: str | None = None
    selected_model: str | None = None
    api_method: str | None = None
    job_type: str | None = None
    fallback_used: bool = False
    attempt_count: int = 0
    asset_count: int = 0
    manifest_uri: str | None = None
    prompt_packet_ref: str | None = None
    attempt_ledger_ref: str | None = None
    provider_note_ref: str | None = None
    created_at: str
    started_at: str | None = None
    finished_at: str | None = None
    links: dict[str, str] = Field(default_factory=dict)
    slice: str = SLICE_ID
    # PS-009 live-run metadata. These default to empty/null so dry-run runs
    # never pretend to carry live evidence.
    attempts: list[dict[str, Any]] = Field(default_factory=list)
    assets: list[dict[str, Any]] = Field(default_factory=list)
    manifest_hash: str | None = None
    in_memory_manifest_verify: bool | None = None
    stored_manifest_verify: bool | None = None
    transfer_failures: list[Any] = Field(default_factory=list)
    stored_transfer_failures: list[Any] = Field(default_factory=list)
    local_image: str | None = None
    local_prompt_packet: str | None = None
    local_attempt_ledger: str | None = None
    local_provider_note: str | None = None
    truth_boundary: str | None = None
    error: str | None = None
    blocked_reason: str | None = None


# ---------------------------------------------------------------------------
# Attempt (PS-006 20-field shape)
# ---------------------------------------------------------------------------


class AttemptRecord(_BaseAPIModel):
    """A provider attempt record.

    Mirrors the PS-006 20-field ``ProviderAttempt`` shape so live attempts from
    the PS-007 pipeline can be stored verbatim. Dry-run runs carry zero
    attempts; an AttemptRecord is only ever written when a real provider
    attempt occurred, so the presence of an AttemptRecord always reflects a
    real (or real-attempted) provider interaction.
    """

    attempt_id: str
    attempt_index: int
    provider: str
    model: str
    api_method: str
    job_type: str
    status: str
    normalized_status: str
    started_at: str
    finished_at: str
    latency_ms: int = 0
    retryable: bool = False
    fallback_allowed: bool = False
    skip_reason: str | None = None
    raw_error_type: str | None = None
    sanitized_error_message: str | None = None
    estimated_cost: dict[str, Any] = Field(default_factory=dict)
    free_or_paid: str = "unknown"
    output_asset_refs: list[dict[str, Any]] = Field(default_factory=list)
    notes: str = ""


# ---------------------------------------------------------------------------
# Asset
# ---------------------------------------------------------------------------


class AssetRecord(_BaseAPIModel):
    """A generated/stored asset reference for a run.

    References only: never raw bytes. ``produced_real_media`` is the honesty
    flag inherited from the PS-007 provider adapters; it must be ``True`` only
    when a real provider produced real media. Dry-run runs carry zero assets.
    """

    asset_id: str
    run_id: str
    kind: str
    provider: str | None = None
    model: str | None = None
    api_method: str | None = None
    media_type: str | None = None
    size_bytes: int | None = None
    sha256: str | None = None
    url: str | None = None
    b2_url: str | None = None
    manifest_ref: str | None = None
    produced_real_media: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------


class ManifestRecord(_BaseAPIModel):
    """Genblaze manifest metadata for a run.

    When ``ready`` is ``False`` the run has not produced a manifest yet
    (dry-run runs, or live runs not yet stored). The ``not_ready_reason``
    field explains why without crashing the caller.
    """

    run_id: str
    ready: bool = False
    manifest_uri: str | None = None
    manifest_hash: str | None = None
    in_memory_manifest_verify: bool | None = None
    stored_manifest_verify: bool | None = None
    transfer_failures: list[Any] = Field(default_factory=list)
    stored_transfer_failures: list[Any] = Field(default_factory=list)
    asset_count: int = 0
    not_ready_reason: str | None = None


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class ErrorResponse(_BaseAPIModel):
    """Clear, non-crashing error envelope for missing/invalid resources.

    Returned with an appropriate HTTP status (404 for missing resources) so
    callers never see a raw traceback.
    """

    ok: bool = False
    error: str
    detail: str | None = None
    resource: str | None = None
    resource_id: str | None = None
    slice: str = SLICE_ID


class InternalErrorResponse(BaseModel):
    """Non-disclosing error returned by the internal proof read boundary."""

    model_config = ConfigDict(extra="forbid")
    ok: bool = False
    code: str
    message: str


class InternalProofRoomResponse(BaseModel):
    """Bounded campaign proof composite; FastAPI remains the data authority."""

    model_config = ConfigDict(extra="forbid")
    source: str = "proof_api"
    campaign: dict[str, Any]
    selected_run: dict[str, Any] | None = None
    attempts: list[dict[str, Any]] = Field(default_factory=list, max_length=1000)
    assets: list[dict[str, Any]] = Field(default_factory=list, max_length=1000)
    manifest: dict[str, Any] | None = None
    passport_ref: str | None = None
    export_refs: list[str] = Field(default_factory=list, max_length=100)


class InternalPassportResponse(BaseModel):
    """Strict wrapper around the existing FastAPI-assembled Passport."""

    model_config = ConfigDict(extra="forbid")
    source: str = "proof_api"
    campaign_access_scope: str
    passport: dict[str, Any]


__all__ = [
    "SLICE_ID",
    "SERVICE_NAME",
    "ARCHIVE_SCHEMA_VERSION",
    "ARCHIVE_STORAGE_MODE_B2",
    "ARCHIVE_STORAGE_MODE_LOCAL",
    "ARCHIVE_TRUTH_BOUNDARY",
    "RUN_STATUS_DRY_RUN_CREATED",
    "RUN_STATUS_QUEUED",
    "RUN_STATUS_LIVE_NOT_SUPPORTED",
    "RUN_STATUS_FAILED",
    "RUN_STATUS_LIVE_RUNNING",
    "RUN_STATUS_LIVE_COMPLETED",
    "RUN_STATUS_LIVE_FAILED",
    "RUN_STATUS_LIVE_BLOCKED",
    "LIVE_RUN_STATUSES",
    "CAMPAIGN_STATUS_CREATED",
    "REQUIRED_ATTEMPT_FIELDS",
    "CampaignCreate",
    "CampaignRecord",
    "RunCreate",
    "RunRecord",
    "AttemptRecord",
    "AssetRecord",
    "ManifestRecord",
    "ErrorResponse",
    "InternalErrorResponse",
    "InternalProofRoomResponse",
    "InternalPassportResponse",
]
