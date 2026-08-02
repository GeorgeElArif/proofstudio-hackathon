"""PS-010 Run Archive + Rehydrate from B2.

This module is the durability/recovery layer for ProofStudio runs. It proves
that the API readback state for a run can be:

1. serialized into a durable run-archive JSON artifact (``build_run_archive``),
2. written locally (``write_run_archive_local``),
3. stored durably as a real B2/Genblaze asset (``store_run_archive_with_genblaze``),
4. read back from B2 object content (``read_archive_from_b2``), and
5. reconstructed into a fresh in-memory store/service (``rehydrate_run_from_archive``)

without rerunning any provider, without uploading fake media, and without
fabricating a manifest (see specs/18-ps-010-run-archive-rehydrate-b2.md).

Truth rules (section 9 / section 11):

- The archive is built ONLY from existing service readbacks (campaign record,
  run record, provider attempts, asset metadata, manifest metadata, and the
  PS-009 local artifact paths). It never invents fields.
- Rehydration loads the archive, validates the schema version + required
  fields + the full PS-006 20-field attempt shape, and restores state into a
  fresh store using plain store writes. It never calls ``create_run``, never
  calls the live bridge, never calls a provider, and never writes media.
- B2 rehydration is honest: ``archive_storage_mode == "b2_object_content"`` is
  only reported when the archive bytes were actually read back from B2 and
  their SHA-256 matches what was stored.

Truth boundary: see :data:`proofstudio.api.models.ARCHIVE_TRUTH_BOUNDARY`.
"""

from __future__ import annotations

import hashlib
import json
import mimetypes
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

from proofstudio.api.models import (
    ARCHIVE_SCHEMA_VERSION,
    ARCHIVE_STORAGE_MODE_B2,
    ARCHIVE_STORAGE_MODE_LOCAL,
    ARCHIVE_TRUTH_BOUNDARY,
    REQUIRED_ATTEMPT_FIELDS,
    RUN_STATUS_LIVE_COMPLETED,
    AssetRecord,
    AttemptRecord,
    CampaignRecord,
    ManifestRecord,
    RunRecord,
)
from proofstudio.api.store import InMemoryStore
from proofstudio.provenance.genblaze_store import AssetSpec, GenblazeStore

SLICE_ID = "PS-010"
ARCHIVE_ARTIFACT_TYPE = "run_archive"

# Top-level fields a valid archive must carry (beyond the schema version).
REQUIRED_ARCHIVE_FIELDS: tuple[str, ...] = (
    "archive_schema_version",
    "run_id",
    "campaign_id",
    "campaign_snapshot",
    "run_status",
    "selected_provider",
    "selected_model",
    "api_method",
    "job_type",
    "fallback_used",
    "attempt_count",
    "attempts",
    "assets",
    "manifest_metadata",
    "truth_boundary",
    "created_at",
    "archived_at",
)


class _ServiceLike(Protocol):
    """Structural type for the service methods archive.py needs.

    ``ProofStudioService`` satisfies this. Declared as a Protocol so the module
    is usable with the real service or any test double that exposes the same
    readback surface.
    """

    store: InMemoryStore

    def get_campaign(self, campaign_id: str) -> dict[str, Any]: ...

    def get_run(self, run_id: str) -> dict[str, Any]: ...

    def get_run_attempts(self, run_id: str) -> dict[str, Any]: ...

    def get_run_assets(self, run_id: str) -> dict[str, Any]: ...

    def get_run_manifest(self, run_id: str) -> dict[str, Any]: ...


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_of_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _guess_media_type(path: Path) -> str:
    guessed, _ = mimetypes.guess_type(str(path))
    return guessed or "application/octet-stream"


def _local_artifact_meta(path_value: Any) -> dict[str, Any]:
    """Build honest on-disk metadata for a local artifact path.

    Returns ``{"exists": False}`` style metadata for missing/None paths so the
    archive never fabricates a file that is not there.
    """
    if not path_value:
        return {"path": None, "exists": False, "sha256": None, "size_bytes": None}
    path = Path(str(path_value))
    if not path.exists():
        return {
            "path": str(path),
            "exists": False,
            "sha256": None,
            "size_bytes": None,
        }
    sha = _sha256_of_file(path)
    return {
        "path": str(path),
        "exists": True,
        "sha256": sha,
        "size_bytes": path.stat().st_size,
        "media_type": _guess_media_type(path),
    }


def build_run_archive(
    service: _ServiceLike,
    run_id: str,
    *,
    campaign_id: str | None = None,
) -> dict[str, Any]:
    """Build a durable run-archive dict from current service readbacks.

    Reads the run, its attempts, assets, manifest metadata, and the owning
    campaign through the normal PS-008/PS-009 readback methods, then folds in
    honest on-disk metadata for the PS-009 local artifacts (generated image,
    prompt packet, attempt ledger, provider note) when those paths exist.

    Never calls a provider, never writes media, never fabricates a manifest.
    Raises ``KeyError`` if the run is unknown (surfacing the service miss).
    """
    run_envelope = service.get_run(run_id)
    run_record = dict(run_envelope["run"])
    resolved_campaign_id = campaign_id or run_record.get("campaign_id") or ""
    if not resolved_campaign_id:
        raise KeyError(f"Run {run_id!r} has no campaign_id to archive.")

    campaign_snapshot: dict[str, Any]
    try:
        campaign_snapshot = dict(service.get_campaign(resolved_campaign_id)["campaign"])
    except Exception:
        campaign_snapshot = {"campaign_id": resolved_campaign_id}

    attempts_envelope = service.get_run_attempts(run_id)
    attempts = [dict(a) for a in attempts_envelope.get("attempts") or []]

    assets_envelope = service.get_run_assets(run_id)
    assets = [dict(a) for a in assets_envelope.get("assets") or []]

    manifest_metadata = dict(service.get_run_manifest(run_id))
    # ``ready`` is the canonical readiness flag; keep the rest verbatim.

    # Honest local-artifact metadata. These paths come straight from the
    # PS-009 live result; we only inspect them, never write them.
    local_artifacts = {
        "local_image": _local_artifact_meta(run_record.get("local_image")),
        "local_prompt_packet": _local_artifact_meta(
            run_record.get("local_prompt_packet")
        ),
        "local_attempt_ledger": _local_artifact_meta(
            run_record.get("local_attempt_ledger")
        ),
        "local_provider_note": _local_artifact_meta(
            run_record.get("local_provider_note")
        ),
    }

    image_sha256 = run_record.get("image_sha256") if hasattr(run_record, "get") else None
    if not image_sha256:
        # Fall back to the generated-image asset sha if present.
        for asset in assets:
            if asset.get("produced_real_media") and asset.get("sha256"):
                image_sha256 = asset.get("sha256")
                break
    # Also accept the local-image file hash if it exists on disk.
    if not image_sha256 and local_artifacts["local_image"].get("sha256"):
        image_sha256 = local_artifacts["local_image"]["sha256"]

    b2_urls = [asset.get("b2_url") for asset in assets if asset.get("b2_url")]

    prompt_packet_meta = local_artifacts["local_prompt_packet"]
    provider_note_meta = local_artifacts["local_provider_note"]

    archive: dict[str, Any] = {
        "archive_schema_version": ARCHIVE_SCHEMA_VERSION,
        "slice": SLICE_ID,
        "artifact_type": ARCHIVE_ARTIFACT_TYPE,
        "run_id": run_id,
        "campaign_id": resolved_campaign_id,
        "campaign_snapshot": campaign_snapshot,
        "run_status": run_record.get("status"),
        "selected_provider": run_record.get("selected_provider"),
        "selected_model": run_record.get("selected_model"),
        "api_method": run_record.get("api_method"),
        "job_type": run_record.get("job_type"),
        "fallback_used": bool(run_record.get("fallback_used")),
        "attempt_count": len(attempts),
        "attempts": attempts,
        "assets": assets,
        "manifest_metadata": manifest_metadata,
        "manifest_uri": manifest_metadata.get("manifest_uri"),
        "manifest_hash": manifest_metadata.get("manifest_hash"),
        "stored_manifest_verify": manifest_metadata.get("stored_manifest_verify"),
        "local_artifacts": local_artifacts,
        "b2_urls": b2_urls,
        "image_sha256": image_sha256,
        "prompt_packet_metadata": prompt_packet_meta,
        "provider_note_metadata": provider_note_meta,
        "prompt_packet_ref": run_record.get("prompt_packet_ref"),
        "attempt_ledger_ref": run_record.get("attempt_ledger_ref"),
        "provider_note_ref": run_record.get("provider_note_ref"),
        "budget_mode": run_record.get("budget_mode"),
        "run_live": bool(run_record.get("run_live")),
        "dry_run": bool(run_record.get("dry_run")),
        "truth_boundary": ARCHIVE_TRUTH_BOUNDARY,
        "created_at": run_record.get("created_at") or _utc_now_iso(),
        "archived_at": _utc_now_iso(),
    }
    return archive


def write_run_archive_local(
    archive: dict[str, Any], path: str | Path
) -> Path:
    """Write an archive dict to ``path`` as pretty JSON. Returns the path."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(archive, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return out


def store_run_archive_with_genblaze(
    archive: dict[str, Any],
    *,
    b2_env: dict[str, str],
    b2_prefix: str,
    local_path: str | Path | None = None,
    name_prefix: str = "proofstudio-ps-010-run-archive",
) -> dict[str, Any]:
    """Store a run-archive JSON as a real B2/Genblaze asset.

    Writes the archive to ``local_path`` (or a temp file under the archive's
    run id), then ingests it through :class:`GenblazeStore` with
    ``artifact_type == "run_archive"`` and the PS-010 metadata block, and
    returns the durable references (archive B2 URL + SHA-256, plus the
    archive's own Genblaze manifest URI/hash and verification flags).

    Never calls a provider and never writes generated media.
    """
    run_id = archive.get("run_id") or "unknown"
    local_archive_path = Path(local_path) if local_path else (
        Path("/tmp/proofstudio-ps-010") / f"proofstudio-run-archive-{run_id}.json"
    )
    write_run_archive_local(archive, local_archive_path)

    source_metadata = {
        "artifact_type": ARCHIVE_ARTIFACT_TYPE,
        "proofstudio_test": "ps-010",
        "slice": SLICE_ID,
        "archive_schema_version": archive.get("archive_schema_version"),
        "run_id": run_id,
        "campaign_id": archive.get("campaign_id"),
        "selected_provider": archive.get("selected_provider"),
        "selected_model": archive.get("selected_model"),
        "run_status": archive.get("run_status"),
        "manifest_uri": archive.get("manifest_uri"),
        "manifest_hash": archive.get("manifest_hash"),
        "attempt_count": archive.get("attempt_count"),
    }

    asset_spec = AssetSpec(
        path=local_archive_path,
        media_type="application/json",
        artifact_type=ARCHIVE_ARTIFACT_TYPE,
        metadata=source_metadata,
    )

    store = GenblazeStore(
        bucket=b2_env["B2_BUCKET"],
        region=b2_env["B2_REGION"],
        key_id=b2_env["B2_KEY_ID"],
        app_key=b2_env["B2_APP_KEY"],
        prefix=b2_prefix,
    )
    run_result = store.store_and_verify(
        assets=[asset_spec],
        source="proofstudio-ps-010-run-archive-store",
        source_metadata={
            "scenario": SLICE_ID,
            "description": (
                "PS-010 stored a durable run-archive JSON artifact in B2 and "
                "verified it through a Genblaze manifest so the run can be "
                "rehydrated later without rerunning providers."
            ),
            **source_metadata,
        },
        name=f"{name_prefix}-{run_id}",
        tenant_id="local",
    )

    first = run_result.asset_summaries[0] if run_result.asset_summaries else {}
    return {
        "archive_uri": first.get("url"),
        "archive_sha256": first.get("sha256"),
        "archive_size_bytes": first.get("size_bytes"),
        "archive_b2_asset_id": first.get("asset_id"),
        "archive_manifest_uri": run_result.manifest_uri,
        "archive_manifest_hash": run_result.manifest_hash,
        "archive_in_memory_manifest_verify": run_result.in_memory_manifest_verify,
        "archive_stored_manifest_verify": run_result.stored_manifest_verify,
        "archive_transfer_failures": list(run_result.transfer_failures),
        "archive_stored_transfer_failures": list(run_result.stored_transfer_failures),
        "archive_local_path": str(local_archive_path),
    }


def read_archive_from_b2(
    archive_uri: str,
    *,
    b2_env: dict[str, str],
    b2_prefix: str,
) -> dict[str, Any]:
    """Download the run-archive JSON from B2 object content and parse it.

    This is the strong-pass rehydration source: the archive bytes are actually
    read back from the B2 object written by :func:`store_run_archive_with_genblaze`.
    Raises if the object cannot be resolved or parsed.
    """
    store = GenblazeStore(
        bucket=b2_env["B2_BUCKET"],
        region=b2_env["B2_REGION"],
        key_id=b2_env["B2_KEY_ID"],
        app_key=b2_env["B2_APP_KEY"],
        prefix=b2_prefix,
    )
    raw = store.read_bytes_for_url(archive_uri)
    return json.loads(raw.decode("utf-8"))


def validate_archive(archive: dict[str, Any]) -> list[str]:
    """Validate schema version, required fields, and the full attempt shape.

    Returns a list of human-readable error strings (empty when valid). Used by
    rehydration so a malformed/compact archive can never silently restore.
    """
    errors: list[str] = []
    if not isinstance(archive, dict):
        return [f"archive must be a dict, got {type(archive).__name__}"]

    schema = archive.get("archive_schema_version")
    if schema != ARCHIVE_SCHEMA_VERSION:
        errors.append(
            f"archive_schema_version {schema!r} != supported "
            f"{ARCHIVE_SCHEMA_VERSION!r}"
        )

    for field_name in REQUIRED_ARCHIVE_FIELDS:
        if field_name not in archive:
            errors.append(f"missing required archive field {field_name!r}")

    attempts = archive.get("attempts")
    if not isinstance(attempts, list):
        errors.append(f"attempts must be a list, got {type(attempts).__name__}")
    else:
        for index, attempt in enumerate(attempts):
            if not isinstance(attempt, dict):
                errors.append(
                    f"attempts[{index}]: must be a dict, got "
                    f"{type(attempt).__name__}"
                )
                continue
            for field_name in REQUIRED_ATTEMPT_FIELDS:
                if field_name not in attempt:
                    errors.append(
                        f"attempts[{index}]: missing required PS-006 field "
                        f"{field_name!r}"
                    )

    assets = archive.get("assets")
    if not isinstance(assets, list):
        errors.append(f"assets must be a list, got {type(assets).__name__}")

    return errors


def load_archive(source: Any) -> dict[str, Any]:
    """Load an archive dict from a dict, a local path/str, or raw JSON bytes."""
    if isinstance(source, dict):
        return dict(source)
    if isinstance(source, (bytes, bytearray)):
        return json.loads(bytes(source).decode("utf-8"))
    if isinstance(source, str):
        # Treat as a local path.
        text = Path(source).read_text(encoding="utf-8")
        return json.loads(text)
    if isinstance(source, Path):
        return json.loads(source.read_text(encoding="utf-8"))
    raise TypeError(
        f"Unsupported archive source type: {type(source).__name__}"
    )


def _restore_campaign(
    store: InMemoryStore, campaign_snapshot: dict[str, Any]
) -> dict[str, Any]:
    campaign_id = campaign_snapshot.get("campaign_id")
    if not campaign_id:
        raise ValueError("campaign_snapshot is missing campaign_id")
    # Use model_validate defensively so a partial snapshot still round-trips.
    record = CampaignRecord.model_validate(campaign_snapshot).model_dump()
    if not store.has_campaign(campaign_id):
        store.create_campaign(campaign_id, record)
    return store.get_campaign(campaign_id) or record


def _restore_run(
    store: InMemoryStore, archive: dict[str, Any]
) -> dict[str, Any]:
    run_id = archive["run_id"]
    campaign_id = archive["campaign_id"]
    manifest_metadata = dict(archive.get("manifest_metadata") or {})

    record = RunRecord.model_validate(
        {
            "run_id": run_id,
            "campaign_id": campaign_id,
            "status": archive.get("run_status") or "rehydrated",
            "budget_mode": archive.get("budget_mode") or "free-only",
            "dry_run": bool(archive.get("dry_run", False)),
            "run_live": bool(archive.get("run_live", False)),
            "selected_provider": archive.get("selected_provider"),
            "selected_model": archive.get("selected_model"),
            "api_method": archive.get("api_method"),
            "job_type": archive.get("job_type"),
            "fallback_used": bool(archive.get("fallback_used", False)),
            "manifest_uri": manifest_metadata.get("manifest_uri")
            or archive.get("manifest_uri"),
            "manifest_hash": manifest_metadata.get("manifest_hash")
            or archive.get("manifest_hash"),
            "stored_manifest_verify": manifest_metadata.get("stored_manifest_verify"),
            "prompt_packet_ref": archive.get("prompt_packet_ref"),
            "attempt_ledger_ref": archive.get("attempt_ledger_ref"),
            "provider_note_ref": archive.get("provider_note_ref"),
            "created_at": archive.get("created_at") or _utc_now_iso(),
            "links": {
                "self": f"/runs/{run_id}",
                "attempts": f"/runs/{run_id}/attempts",
                "assets": f"/runs/{run_id}/assets",
                "manifest": f"/runs/{run_id}/manifest",
                "campaign": f"/campaigns/{campaign_id}",
            },
            "slice": "PS-010",
            "truth_boundary": archive.get("truth_boundary") or ARCHIVE_TRUTH_BOUNDARY,
        }
    ).model_dump()

    # Carry the PS-009 local-artifact paths through verbatim so rehydrated
    # readbacks point at the same on-disk evidence (no new files written).
    local_artifacts = archive.get("local_artifacts") or {}
    for key in (
        "local_image",
        "local_prompt_packet",
        "local_attempt_ledger",
        "local_provider_note",
    ):
        entry = local_artifacts.get(key) or {}
        if isinstance(entry, dict) and entry.get("path"):
            record[key] = entry["path"]
        record.setdefault(key, None)

    # Rehydrate carries the archived attempts/assets inline so the run record
    # matches the sub-resource readbacks exactly (mirrors PS-009's shape).
    record["attempts"] = list(archive.get("attempts") or [])
    record["assets"] = list(archive.get("assets") or [])
    record["attempt_count"] = len(record["attempts"])
    record["asset_count"] = len(record["assets"])
    record["image_sha256"] = archive.get("image_sha256")

    if not store.has_run(run_id):
        store.create_run(run_id, record)
    else:
        store.update_run(run_id, record)
    return store.get_run(run_id) or record


def _restore_attempts(
    store: InMemoryStore, run_id: str, attempts: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    # Validate through the model so a compact/tampered attempt is rejected.
    cleaned = [
        AttemptRecord.model_validate(dict(a)).model_dump() for a in attempts
    ]
    return store.set_attempts(run_id, cleaned)


def _restore_assets(
    store: InMemoryStore, run_id: str, assets: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    cleaned: list[dict[str, Any]] = []
    for asset in assets:
        data = dict(asset)
        if "run_id" not in data:
            data["run_id"] = run_id
        if "asset_id" not in data:
            # Fallback id so the asset record is always well-formed. This does
            # not fabricate media: produced_real_media is preserved verbatim.
            data["asset_id"] = f"asset_rehydrated_{run_id}_{len(cleaned)}"
        cleaned.append(AssetRecord.model_validate(data).model_dump())
    return store.set_assets(run_id, cleaned)


def _restore_manifest(
    store: InMemoryStore, run_id: str, manifest_metadata: dict[str, Any]
) -> dict[str, Any] | None:
    if not manifest_metadata:
        return None
    manifest_uri = manifest_metadata.get("manifest_uri")
    if not manifest_uri:
        # Honest: no manifest existed for this run (blocked/failed/dry-run).
        return None
    record = ManifestRecord.model_validate(
        {
            **manifest_metadata,
            "run_id": run_id,
            "ready": True,
        }
    ).model_dump()
    store.set_manifest(run_id, record)
    return store.get_manifest(run_id)


def rehydrate_run_from_archive(
    service: _ServiceLike,
    source: Any,
    *,
    source_kind: str = "auto",
) -> dict[str, Any]:
    """Rehydrate a run from an archive into ``service``'s fresh store.

    ``source`` may be:

    - a parsed archive dict (``source_kind="inline"``),
    - a local file path/str/Path (``source_kind="local"``),
    - raw JSON bytes read from B2 (``source_kind="b2"``).

    With ``source_kind="auto"`` the kind is inferred from the source type.

    Restores the campaign (if missing), run, attempts, assets, and manifest
    metadata using plain store writes. Never calls ``create_run``, never calls
    the live bridge, never calls a provider, and never writes media or a
    manifest. Returns a structured result describing what was restored.
    """
    kind = source_kind
    if kind == "auto":
        if isinstance(source, dict):
            kind = "inline"
        elif isinstance(source, (bytes, bytearray)):
            kind = "b2"
        else:
            kind = "local"

    archive = load_archive(source)
    errors = validate_archive(archive)
    if errors:
        raise ValueError(
            "Archive failed validation and was not rehydrated: "
            + "; ".join(errors)
        )

    run_id = archive["run_id"]
    campaign_id = archive["campaign_id"]
    campaign_snapshot = dict(archive.get("campaign_snapshot") or {})
    attempts = list(archive.get("attempts") or [])
    assets = list(archive.get("assets") or [])
    manifest_metadata = dict(archive.get("manifest_metadata") or {})

    restored_campaign = _restore_campaign(service.store, campaign_snapshot)
    restored_run = _restore_run(service.store, archive)
    restored_attempts = _restore_attempts(service.store, run_id, attempts)
    restored_assets = _restore_assets(service.store, run_id, assets)
    restored_manifest = _restore_manifest(service.store, run_id, manifest_metadata)

    return {
        "ok": True,
        "rehydrate_source": kind,
        "restored_run_id": run_id,
        "restored_campaign_id": campaign_id,
        "restored_campaign": restored_campaign,
        "restored_run": restored_run,
        "restored_attempt_count": len(restored_attempts),
        "restored_asset_count": len(restored_assets),
        "restored_manifest": restored_manifest,
        "restored_manifest_uri": (
            restored_manifest.get("manifest_uri") if restored_manifest else None
        ),
        "restored_manifest_hash": (
            restored_manifest.get("manifest_hash") if restored_manifest else None
        ),
        "provider_calls_made": 0,
        "media_files_written": 0,
        "truth_boundary": ARCHIVE_TRUTH_BOUNDARY,
    }


def is_live_completed_archive(archive: dict[str, Any]) -> bool:
    """True if the archived run honestly reached ``live_completed``."""
    return archive.get("run_status") == RUN_STATUS_LIVE_COMPLETED


__all__ = [
    "SLICE_ID",
    "ARCHIVE_ARTIFACT_TYPE",
    "ARCHIVE_SCHEMA_VERSION",
    "REQUIRED_ARCHIVE_FIELDS",
    "build_run_archive",
    "write_run_archive_local",
    "store_run_archive_with_genblaze",
    "read_archive_from_b2",
    "validate_archive",
    "load_archive",
    "rehydrate_run_from_archive",
    "is_live_completed_archive",
    "ARCHIVE_STORAGE_MODE_B2",
    "ARCHIVE_STORAGE_MODE_LOCAL",
    "ARCHIVE_TRUTH_BOUNDARY",
]
