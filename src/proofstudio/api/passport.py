"""PS-011 Review Room / Provenance Passport API.

This module turns the evidence stored by the service layer into a single
structured, judge-facing Provenance Passport object. A passport answers:

- What was generated?
- Which provider/model made it?
- Which attempts happened?
- Did fallback happen?
- What failed or was skipped?
- What assets exist and what are their hashes?
- Where is the manifest and was it verified?
- Is archive/rehydration evidence available?
- What does this proof claim, and what does it NOT claim?

The passport is a read-only view. It is built ONLY from normal service
readbacks (``get_run`` / ``get_run_attempts`` / ``get_run_assets`` /
``get_run_manifest``) plus optional, caller-supplied archive/rehydration
evidence. It never calls a provider, never reruns generation, never writes
media, and never fakes manifest verification or archive proof (see
specs/19-ps-011-review-room-provenance-passport-api.md section 7).

Public surface:

- :data:`PASSPORT_SCHEMA_VERSION`
- :data:`PASSPORT_TRUTH_BOUNDARY`
- :data:`REQUIRED_ATTEMPT_FIELDS`
- :func:`build_provenance_passport`  - assemble the passport dict from readbacks
- :func:`validate_provenance_passport` - validate the full passport schema
- :func:`write_passport_local`       - write a passport dict to disk as JSON
- :func:`timeline_from_attempts`     - compact judge-friendly timeline

Truth boundary: the passport proves that ProofStudio can transform stored run
evidence into a structured review artifact. It does not prove semantic truth,
legal authenticity, C2PA authenticity, human authorship, final production
security, or production persistence.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from proofstudio.api.models import (
    REQUIRED_ATTEMPT_FIELDS,
    RUN_STATUS_LIVE_COMPLETED,
)

SLICE_ID = "PS-011"
PASSPORT_SCHEMA_VERSION = "ps-011.1"
PASSPORT_ARTIFACT_TYPE = "provenance_passport"

# Canonical non-claims the passport must always surface. These are the
# boundaries a reviewer/judge must understand. The passport must never assert
# the opposite of any of these.
PASSPORT_NON_CLAIMS: tuple[str, ...] = (
    "semantic_truth",
    "legal_authenticity",
    "c2pa_authenticity",
    "human_authorship",
    "final_production_security",
)

PASSPORT_TRUTH_BOUNDARY = (
    "PS-011 proves ProofStudio can transform stored run evidence (provider "
    "attempts, asset hashes, manifest verification, archive/rehydration "
    "metadata) into a structured Review Room / Provenance Passport object "
    "using normal service readbacks. It does not prove semantic truth, legal "
    "authenticity, C2PA authenticity, human authorship, final production "
    "security, or production persistence."
)

# Fields a passport top-level section must carry.
PASSPORT_IDENTITY_FIELDS: tuple[str, ...] = (
    "passport_id",
    "passport_schema_version",
    "run_id",
    "campaign_id",
    "created_at",
    "source",
)

RUN_SUMMARY_FIELDS: tuple[str, ...] = (
    "status",
    "selected_provider",
    "selected_model",
    "api_method",
    "job_type",
    "fallback_used",
    "attempt_count",
    "asset_count",
    "manifest_uri",
    "manifest_hash",
)

CAMPAIGN_SNAPSHOT_FIELDS: tuple[str, ...] = (
    "campaign_id",
    "name",
    "brief",
    "target_audience",
    "platform",
    "objective",
)

GENERATION_SUMMARY_FIELDS: tuple[str, ...] = (
    "generated_media_present",
    "primary_asset_uri",
    "primary_asset_media_type",
    "primary_asset_sha256",
    "primary_asset_size_bytes",
)

TIMELINE_ENTRY_FIELDS: tuple[str, ...] = (
    "attempt_index",
    "provider",
    "model",
    "api_method",
    "status",
    "normalized_status",
    "latency_ms",
    "retryable",
    "fallback_allowed",
    "skip_reason",
    "sanitized_error_message",
    "output_asset_refs",
)

ASSET_SUMMARY_FIELDS: tuple[str, ...] = (
    "url",
    "media_type",
    "sha256",
    "size_bytes",
    "metadata",
)

MANIFEST_VERIFICATION_FIELDS: tuple[str, ...] = (
    "manifest_uri",
    "manifest_hash",
    "in_memory_manifest_verify",
    "stored_manifest_verify",
    "transfer_failures",
    "stored_transfer_failures",
)

ARCHIVE_AND_REHYDRATION_FIELDS: tuple[str, ...] = (
    "archive_uri",
    "archive_sha256",
    "archive_storage_mode",
    "rehydrate_source",
    "rehydrate_completed",
    "restored_manifest_uri",
    "restored_manifest_hash",
    "no_live_provider_call_during_rehydrate",
)

REVIEW_ROOM_SUMMARY_FIELDS: tuple[str, ...] = (
    "one_sentence_summary",
    "risk_flags",
    "reviewer_next_actions",
)

# Allowed normalized statuses that count as a real failure (not a skip).
_FAILURE_NORMALIZED_STATUSES = frozenset(
    {
        "MODEL_UNAVAILABLE",
        "SAFETY_BLOCKED",
        "TIMEOUT",
        "BAD_REQUEST",
        "PROVIDER_DOWN",
        "UNSUPPORTED_MODE",
        "QUOTA_OR_BILLING_BLOCKED",
        "UNKNOWN_ERROR",
    }
)

# Canonical source labels for passport_identity.source.
SOURCE_LIVE_RUN = "live_run"
SOURCE_REHYDRATED_RUN = "rehydrated_run"
SOURCE_ARCHIVE_REHYDRATED_RUN = "archive_rehydrated_run"
SOURCE_STORE_READBACK = "store_readback"

ARCHIVE_NOT_AVAILABLE = "not_available"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_passport_id(run_id: str) -> str:
    return f"passport_{run_id}_{uuid.uuid4().hex[:12]}"


def _is_failure_status(normalized_status: Any) -> bool:
    return bool(normalized_status) and normalized_status in _FAILURE_NORMALIZED_STATUSES


def _select_primary_asset(assets: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Pick the primary generated-media asset from an asset list.

    Prefers an asset that honestly produced real media, then a
    ``generated_image`` kind, then the first asset. Returns ``None`` only when
    the list is empty.
    """
    if not assets:
        return None
    for asset in assets:
        if asset.get("produced_real_media") is True:
            return asset
    for asset in assets:
        kind = (asset.get("kind") or "").lower()
        if kind in {"generated_image", "image"}:
            return asset
    return assets[0]


def _asset_uri(asset: dict[str, Any]) -> str | None:
    return (
        asset.get("b2_url")
        or asset.get("url")
        or asset.get("local_path")
        or None
    )


def timeline_from_attempts(attempts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build a compact, judge-friendly timeline from full PS-006 attempts.

    The timeline is always derived from the full attempts (never the source of
    truth on its own). Each entry carries the readable subset defined by
    :data:`TIMELINE_ENTRY_FIELDS`.
    """
    timeline: list[dict[str, Any]] = []
    for attempt in attempts:
        timeline.append(
            {
                "attempt_index": attempt.get("attempt_index"),
                "provider": attempt.get("provider"),
                "model": attempt.get("model"),
                "api_method": attempt.get("api_method"),
                "status": attempt.get("status"),
                "normalized_status": attempt.get("normalized_status"),
                "latency_ms": attempt.get("latency_ms"),
                "retryable": bool(attempt.get("retryable")),
                "fallback_allowed": bool(attempt.get("fallback_allowed")),
                "skip_reason": attempt.get("skip_reason"),
                "sanitized_error_message": attempt.get("sanitized_error_message"),
                "output_asset_refs": list(attempt.get("output_asset_refs") or []),
            }
        )
    return timeline


def _build_run_summary(
    run: dict[str, Any],
    attempts: list[dict[str, Any]],
    assets: list[dict[str, Any]],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    manifest_uri = (
        manifest.get("manifest_uri")
        if manifest.get("ready")
        else run.get("manifest_uri")
    )
    manifest_hash = (
        manifest.get("manifest_hash")
        if manifest.get("ready")
        else run.get("manifest_hash")
    )
    return {
        "status": run.get("status"),
        "selected_provider": run.get("selected_provider"),
        "selected_model": run.get("selected_model"),
        "api_method": run.get("api_method"),
        "job_type": run.get("job_type"),
        "fallback_used": bool(run.get("fallback_used")),
        "attempt_count": len(attempts) or int(run.get("attempt_count") or 0),
        "asset_count": len(assets) or int(run.get("asset_count") or 0),
        "manifest_uri": manifest_uri,
        "manifest_hash": manifest_hash,
    }


def _build_campaign_snapshot(campaign: dict[str, Any]) -> dict[str, Any]:
    return {
        "campaign_id": campaign.get("campaign_id"),
        "name": campaign.get("name"),
        "brief": campaign.get("brief"),
        "target_audience": campaign.get("target_audience"),
        "platform": campaign.get("platform"),
        "objective": campaign.get("objective"),
    }


def _build_generation_summary(
    run: dict[str, Any], assets: list[dict[str, Any]]
) -> dict[str, Any]:
    primary = _select_primary_asset(assets)
    generated_media_present = bool(
        primary and primary.get("produced_real_media") is True
    )
    summary: dict[str, Any] = {
        "generated_media_present": generated_media_present,
        "primary_asset_uri": _asset_uri(primary) if primary else None,
        "primary_asset_media_type": primary.get("media_type") if primary else None,
        "primary_asset_sha256": primary.get("sha256") if primary else None,
        "primary_asset_size_bytes": primary.get("size_bytes") if primary else None,
    }
    # image_mime_type / image_sha256 are surfaced when the run record (or the
    # primary asset) carries them. They are optional in the schema but very
    # useful for a reviewer.
    image_mime_type = run.get("image_mime_type")
    image_sha256 = run.get("image_sha256")
    if image_mime_type is None and primary is not None:
        if primary.get("produced_real_media") is True:
            image_mime_type = primary.get("media_type")
    if image_sha256 is None and primary is not None:
        if primary.get("produced_real_media") is True:
            image_sha256 = primary.get("sha256")
    summary["image_mime_type"] = image_mime_type
    summary["image_sha256"] = image_sha256
    return summary


def _build_assets_summary(assets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for asset in assets:
        summaries.append(
            {
                "url": _asset_uri(asset),
                "media_type": asset.get("media_type"),
                "sha256": asset.get("sha256"),
                "size_bytes": asset.get("size_bytes"),
                "metadata": {
                    "kind": asset.get("kind"),
                    "provider": asset.get("provider"),
                    "model": asset.get("model"),
                    "api_method": asset.get("api_method"),
                    "produced_real_media": bool(asset.get("produced_real_media")),
                    "b2_asset_id": asset.get("b2_asset_id"),
                    "b2_url": asset.get("b2_url"),
                    "manifest_ref": asset.get("manifest_ref"),
                },
            }
        )
    return summaries


def _build_manifest_verification(
    run: dict[str, Any], manifest: dict[str, Any]
) -> dict[str, Any]:
    ready = bool(manifest.get("ready"))
    manifest_uri = manifest.get("manifest_uri") if ready else run.get("manifest_uri")
    manifest_hash = manifest.get("manifest_hash") if ready else run.get("manifest_hash")
    return {
        "manifest_uri": manifest_uri,
        "manifest_hash": manifest_hash,
        "in_memory_manifest_verify": (
            manifest.get("in_memory_manifest_verify")
            if ready
            else run.get("in_memory_manifest_verify")
        ),
        "stored_manifest_verify": (
            manifest.get("stored_manifest_verify")
            if ready
            else run.get("stored_manifest_verify")
        ),
        "transfer_failures": list(
            manifest.get("transfer_failures")
            if ready
            else (run.get("transfer_failures") or [])
        ),
        "stored_transfer_failures": list(
            manifest.get("stored_transfer_failures")
            if ready
            else (run.get("stored_transfer_failures") or [])
        ),
    }


def _build_archive_and_rehydration(
    archive_evidence: dict[str, Any] | None,
) -> dict[str, Any]:
    """Build the archive/rehydration section honestly.

    When ``archive_evidence`` is missing or clearly incomplete, the section
    keeps every required key but sets ``status`` to ``not_available`` with a
    reason. It is never omitted (spec section 8.8).
    """
    base = {field: None for field in ARCHIVE_AND_REHYDRATION_FIELDS}
    base["no_live_provider_call_during_rehydrate"] = None
    if not archive_evidence:
        base["status"] = ARCHIVE_NOT_AVAILABLE
        base["reason"] = (
            "No archive/rehydration evidence was supplied when building this "
            "passport. The passport was assembled from in-store readbacks only."
        )
        return base

    evidence = dict(archive_evidence)
    rehydrate_completed = bool(evidence.get("rehydrate_completed"))
    has_archive_ref = bool(evidence.get("archive_uri") or evidence.get("archive_sha256"))

    if not rehydrate_completed and not has_archive_ref:
        base["status"] = ARCHIVE_NOT_AVAILABLE
        base["reason"] = (
            "Archive/rehydration evidence was supplied but does not indicate a "
            "completed archive or rehydration."
        )
        return base

    section = {
        "status": "available",
        "archive_uri": evidence.get("archive_uri"),
        "archive_sha256": evidence.get("archive_sha256"),
        "archive_storage_mode": evidence.get("archive_storage_mode"),
        "rehydrate_source": evidence.get("rehydrate_source"),
        "rehydrate_completed": rehydrate_completed,
        "restored_manifest_uri": evidence.get("restored_manifest_uri"),
        "restored_manifest_hash": evidence.get("restored_manifest_hash"),
        "no_live_provider_call_during_rehydrate": bool(
            evidence.get("no_live_provider_call_during_rehydrate")
        )
        if evidence.get("no_live_provider_call_during_rehydrate") is not None
        else None,
    }
    return section


def _build_trust_boundary(
    *,
    attempt_count: int,
    has_manifest: bool,
    archive_section: dict[str, Any],
    assets: list[dict[str, Any]],
) -> dict[str, Any]:
    claims: list[str] = []
    if attempt_count > 0:
        claims.append("provider_attempt_evidence_was_captured")
    if any(a.get("sha256") for a in assets):
        claims.append("asset_hashes_were_recorded")
    if has_manifest:
        claims.append("manifest_verification_occurred")
    if archive_section.get("status") == "available":
        claims.append("archive_rehydration_evidence_present")

    # Non-claims are fixed and always present so a reviewer never over-reads.
    non_claims = list(PASSPORT_NON_CLAIMS)
    return {"claims": claims, "non_claims": non_claims}


def _build_risk_flags(
    *,
    run: dict[str, Any],
    attempts: list[dict[str, Any]],
    manifest_verification: dict[str, Any],
    archive_section: dict[str, Any],
    generation_summary: dict[str, Any],
) -> list[str]:
    flags: list[str] = []
    if bool(run.get("fallback_used")):
        flags.append("fallback_used")
    if any(_is_failure_status(a.get("normalized_status")) for a in attempts):
        flags.append("failed_attempts_present")
    manifest_uri = manifest_verification.get("manifest_uri")
    stored_ok = manifest_verification.get("stored_manifest_verify") is True
    if manifest_uri and not stored_ok:
        flags.append("manifest_not_verified")
    if not manifest_uri:
        flags.append("manifest_not_verified")
    if archive_section.get("status") != "available":
        flags.append("archive_not_available")
    if not generation_summary.get("generated_media_present"):
        flags.append("generated_media_missing")
    return flags


def _build_review_room_summary(
    *,
    run: dict[str, Any],
    risk_flags: list[str],
    attempt_count: int,
    generation_summary: dict[str, Any],
    manifest_verification: dict[str, Any],
    archive_section: dict[str, Any],
) -> dict[str, Any]:
    status = run.get("status") or "unknown"
    selected_provider = run.get("selected_provider") or "(none)"
    selected_model = run.get("selected_model") or "(none)"
    generated = bool(generation_summary.get("generated_media_present"))
    manifest_verified = manifest_verification.get("stored_manifest_verify") is True

    if status == RUN_STATUS_LIVE_COMPLETED and generated and manifest_verified:
        sentence = (
            f"Live run completed via {selected_provider}/{selected_model} "
            f"with {attempt_count} attempt(s), a verified manifest, and a "
            f"generated asset whose hash is recorded."
        )
    elif status == RUN_STATUS_LIVE_COMPLETED and generated:
        sentence = (
            f"Live run completed via {selected_provider}/{selected_model} with "
            f"a generated asset recorded, but manifest verification is not "
            f"confirmed."
        )
    elif archive_section.get("status") == "available":
        sentence = (
            f"Run evidence was rehydrated from durable archive "
            f"({archive_section.get('rehydrate_source')}) for review; current "
            f"status is {status}."
        )
    else:
        sentence = (
            f"Run is in status {status} via {selected_provider}/"
            f"{selected_model}; review the attempt timeline and risk flags "
            f"before drawing conclusions."
        )

    actions: list[str] = []
    if not generated:
        actions.append(
            "Confirm whether generated media is expected; do not treat a "
            "missing asset as produced media."
        )
    if "manifest_not_verified" in risk_flags:
        actions.append(
            "Do not trust asset integrity until the manifest is verified."
        )
    if "failed_attempts_present" in risk_flags or "fallback_used" in risk_flags:
        actions.append(
            "Review the full attempt timeline to understand provider "
            "failures/fallback before approving."
        )
    if "archive_not_available" in risk_flags:
        actions.append(
            "Archive this run so its evidence can be rehydrated later."
        )
    if not actions:
        actions.append(
            "Evidence looks complete; proceed with normal review, respecting "
            "the non-claims in the trust boundary."
        )

    return {
        "one_sentence_summary": sentence,
        "risk_flags": risk_flags,
        "reviewer_next_actions": actions,
    }


def _resolve_source(
    source: str, run: dict[str, Any], archive_evidence: dict[str, Any] | None
) -> str:
    if source and source != "auto":
        return source
    if archive_evidence and archive_evidence.get("rehydrate_completed"):
        return SOURCE_ARCHIVE_REHYDRATED_RUN
    status = run.get("status")
    if status == RUN_STATUS_LIVE_COMPLETED:
        return SOURCE_LIVE_RUN
    return SOURCE_STORE_READBACK


def build_provenance_passport(
    *,
    run: dict[str, Any],
    campaign: dict[str, Any],
    attempts: list[dict[str, Any]],
    assets: list[dict[str, Any]],
    manifest: dict[str, Any],
    archive_evidence: dict[str, Any] | None = None,
    source: str = "auto",
    passport_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Assemble a Provenance Passport dict from service readbacks.

    All inputs are plain dicts/lists as returned by the normal service
    readback methods (``get_run`` / ``get_run_attempts`` / ``get_run_assets`` /
    ``get_run_manifest``). ``archive_evidence`` is optional caller-supplied
    durable-archive/rehydration metadata; when absent the
    ``archive_and_rehydration`` section is explicitly ``not_available``.

    This function performs no network access, calls no provider, writes no
    media, and fabricates no manifest or archive proof.
    """
    run_record = dict(run or {})
    campaign_record = dict(campaign or {})
    attempt_records = [dict(a) for a in (attempts or [])]
    asset_records = [dict(a) for a in (assets or [])]
    manifest_record = dict(manifest or {})

    resolved_source = _resolve_source(source, run_record, archive_evidence)
    run_summary = _build_run_summary(
        run_record, attempt_records, asset_records, manifest_record
    )
    campaign_snapshot = _build_campaign_snapshot(campaign_record)
    generation_summary = _build_generation_summary(run_record, asset_records)
    timeline = timeline_from_attempts(attempt_records)
    assets_summary = _build_assets_summary(asset_records)
    manifest_verification = _build_manifest_verification(
        run_record, manifest_record
    )
    archive_section = _build_archive_and_rehydration(archive_evidence)
    trust_boundary = _build_trust_boundary(
        attempt_count=len(attempt_records),
        has_manifest=bool(manifest_verification.get("manifest_uri")),
        archive_section=archive_section,
        assets=asset_records,
    )
    risk_flags = _build_risk_flags(
        run=run_record,
        attempts=attempt_records,
        manifest_verification=manifest_verification,
        archive_section=archive_section,
        generation_summary=generation_summary,
    )
    review_room_summary = _build_review_room_summary(
        run=run_record,
        risk_flags=risk_flags,
        attempt_count=len(attempt_records),
        generation_summary=generation_summary,
        manifest_verification=manifest_verification,
        archive_section=archive_section,
    )

    passport: dict[str, Any] = {
        "passport_identity": {
            "passport_id": passport_id or _new_passport_id(
                run_record.get("run_id") or "unknown"
            ),
            "passport_schema_version": PASSPORT_SCHEMA_VERSION,
            "run_id": run_record.get("run_id"),
            "campaign_id": run_record.get("campaign_id")
            or campaign_record.get("campaign_id"),
            "created_at": created_at or _utc_now_iso(),
            "source": resolved_source,
        },
        "run_summary": run_summary,
        "campaign_snapshot": campaign_snapshot,
        "generation_summary": generation_summary,
        "attempt_timeline": timeline,
        "raw_attempts": attempt_records,
        "assets": assets_summary,
        "manifest_verification": manifest_verification,
        "archive_and_rehydration": archive_section,
        "trust_boundary": trust_boundary,
        "review_room_summary": review_room_summary,
        "slice": SLICE_ID,
        "artifact_type": PASSPORT_ARTIFACT_TYPE,
        "truth_boundary": PASSPORT_TRUTH_BOUNDARY,
    }
    return passport


def _missing_fields(record: Any, fields: tuple[str, ...], path: str) -> list[str]:
    """Return error strings for any of ``fields`` missing from ``record``."""
    if not isinstance(record, dict):
        return [f"{path}: must be a dict, got {type(record).__name__}"]
    return [
        f"{path}: missing required field {field!r}"
        for field in fields
        if field not in record
    ]


def validate_provenance_passport(passport: Any) -> list[str]:
    """Validate the full passport schema.

    Returns a list of human-readable error strings (empty when valid). This
    enforces:

    - every required top-level section exists,
    - each section carries its required fields,
    - ``raw_attempts`` use the full PS-006 20-field shape (never compact),
    - the trust boundary carries both claims and non_claims,
    - the non-claims include semantic_truth / legal_authenticity /
      c2pa_authenticity / human_authorship / final_production_security,
    - the archive section is either explicitly ``not_available`` or carries the
      required fields.
    """
    if not isinstance(passport, dict):
        return [f"passport must be a dict, got {type(passport).__name__}"]

    errors: list[str] = []

    required_sections = (
        "passport_identity",
        "run_summary",
        "campaign_snapshot",
        "generation_summary",
        "attempt_timeline",
        "raw_attempts",
        "assets",
        "manifest_verification",
        "archive_and_rehydration",
        "trust_boundary",
        "review_room_summary",
    )
    for section in required_sections:
        if section not in passport:
            errors.append(f"missing required passport section {section!r}")

    if errors:
        return errors

    errors += _missing_fields(
        passport.get("passport_identity"), PASSPORT_IDENTITY_FIELDS, "passport_identity"
    )
    identity = passport.get("passport_identity") or {}
    if identity.get("passport_schema_version") != PASSPORT_SCHEMA_VERSION:
        errors.append(
            f"passport_identity.passport_schema_version must be "
            f"{PASSPORT_SCHEMA_VERSION!r}, got "
            f"{identity.get('passport_schema_version')!r}"
        )

    errors += _missing_fields(
        passport.get("run_summary"), RUN_SUMMARY_FIELDS, "run_summary"
    )
    errors += _missing_fields(
        passport.get("campaign_snapshot"),
        CAMPAIGN_SNAPSHOT_FIELDS,
        "campaign_snapshot",
    )
    errors += _missing_fields(
        passport.get("generation_summary"),
        GENERATION_SUMMARY_FIELDS,
        "generation_summary",
    )
    errors += _missing_fields(
        passport.get("manifest_verification"),
        MANIFEST_VERIFICATION_FIELDS,
        "manifest_verification",
    )

    # attempt_timeline entries (compact but must carry the readable subset).
    timeline = passport.get("attempt_timeline")
    if not isinstance(timeline, list):
        errors.append(
            f"attempt_timeline must be a list, got {type(timeline).__name__}"
        )
    else:
        for index, entry in enumerate(timeline):
            errors += _missing_fields(
                entry, TIMELINE_ENTRY_FIELDS, f"attempt_timeline[{index}]"
            )

    # raw_attempts: the source of truth. Must be a list and each entry must
    # carry the full PS-006 20-field shape. Compact attempts are rejected.
    raw_attempts = passport.get("raw_attempts")
    if not isinstance(raw_attempts, list):
        errors.append(
            f"raw_attempts must be a list, got {type(raw_attempts).__name__}"
        )
    else:
        for index, attempt in enumerate(raw_attempts):
            if not isinstance(attempt, dict):
                errors.append(
                    f"raw_attempts[{index}]: must be a dict, got "
                    f"{type(attempt).__name__}"
                )
                continue
            for field_name in REQUIRED_ATTEMPT_FIELDS:
                if field_name not in attempt:
                    errors.append(
                        f"raw_attempts[{index}]: missing required PS-006 field "
                        f"{field_name!r}"
                    )

    # The compact timeline count must equal the raw attempt count so they
    # cannot drift.
    if isinstance(timeline, list) and isinstance(raw_attempts, list):
        if len(timeline) != len(raw_attempts):
            errors.append(
                f"attempt_timeline length ({len(timeline)}) must equal "
                f"raw_attempts length ({len(raw_attempts)})"
            )

    # assets
    assets = passport.get("assets")
    if not isinstance(assets, list):
        errors.append(f"assets must be a list, got {type(assets).__name__}")
    else:
        for index, asset in enumerate(assets):
            errors += _missing_fields(asset, ASSET_SUMMARY_FIELDS, f"assets[{index}]")

    # archive_and_rehydration: must be explicitly not_available OR carry fields.
    archive_section = passport.get("archive_and_rehydration")
    if not isinstance(archive_section, dict):
        errors.append(
            f"archive_and_rehydration must be a dict, got "
            f"{type(archive_section).__name__}"
        )
    else:
        archive_status = archive_section.get("status")
        if archive_status == ARCHIVE_NOT_AVAILABLE:
            if not archive_section.get("reason"):
                errors.append(
                    "archive_and_rehydration: not_available status requires a "
                    "'reason'"
                )
        else:
            errors += _missing_fields(
                archive_section,
                ARCHIVE_AND_REHYDRATION_FIELDS,
                "archive_and_rehydration",
            )
            if archive_status != "available":
                errors.append(
                    f"archive_and_rehydration.status must be 'available' or "
                    f"'not_available', got {archive_status!r}"
                )

    # trust_boundary: claims + non_claims, with mandatory non-claims.
    trust = passport.get("trust_boundary")
    if not isinstance(trust, dict):
        errors.append(
            f"trust_boundary must be a dict, got {type(trust).__name__}"
        )
    else:
        for key in ("claims", "non_claims"):
            if key not in trust:
                errors.append(f"trust_boundary: missing required key {key!r}")
            elif not isinstance(trust.get(key), list):
                errors.append(
                    f"trust_boundary.{key} must be a list, got "
                    f"{type(trust.get(key)).__name__}"
                )
        non_claims = trust.get("non_claims")
        if isinstance(non_claims, list):
            for required in PASSPORT_NON_CLAIMS:
                if required not in non_claims:
                    errors.append(
                        f"trust_boundary.non_claims must include "
                        f"{required!r}"
                    )

    # review_room_summary
    errors += _missing_fields(
        passport.get("review_room_summary"),
        REVIEW_ROOM_SUMMARY_FIELDS,
        "review_room_summary",
    )

    return errors


def write_passport_local(passport: dict[str, Any], path: str | Path) -> Path:
    """Write a passport dict to ``path`` as pretty JSON. Returns the path."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(passport, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    return out


__all__ = [
    "SLICE_ID",
    "PASSPORT_SCHEMA_VERSION",
    "PASSPORT_ARTIFACT_TYPE",
    "PASSPORT_TRUTH_BOUNDARY",
    "PASSPORT_NON_CLAIMS",
    "PASSPORT_IDENTITY_FIELDS",
    "RUN_SUMMARY_FIELDS",
    "CAMPAIGN_SNAPSHOT_FIELDS",
    "GENERATION_SUMMARY_FIELDS",
    "TIMELINE_ENTRY_FIELDS",
    "ASSET_SUMMARY_FIELDS",
    "MANIFEST_VERIFICATION_FIELDS",
    "ARCHIVE_AND_REHYDRATION_FIELDS",
    "REVIEW_ROOM_SUMMARY_FIELDS",
    "SOURCE_LIVE_RUN",
    "SOURCE_REHYDRATED_RUN",
    "SOURCE_ARCHIVE_REHYDRATED_RUN",
    "SOURCE_STORE_READBACK",
    "ARCHIVE_NOT_AVAILABLE",
    "build_provenance_passport",
    "validate_provenance_passport",
    "write_passport_local",
    "timeline_from_attempts",
]
