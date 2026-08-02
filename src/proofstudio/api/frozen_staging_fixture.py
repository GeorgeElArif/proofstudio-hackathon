"""Deterministic frozen-fixture initialization for free Render staging.

Activation requires both:

- PROOFSTUDIO_FIXTURES_FROZEN=true
- PROOFSTUDIO_ENV=staging

The loader reads checked-in evidence only. It performs no provider call, no
B2 read or write, no OAuth action, no email action, and no paid operation.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from proofstudio.api.genblaze_external_adapter import parse_bundle_bytes

ENV_FIXTURES_FROZEN = "PROOFSTUDIO_FIXTURES_FROZEN"
ENVIRONMENT = "PROOFSTUDIO_ENV"

CANONICAL_CAMPAIGN_ID = "camp_bea5161faa6244079d2ee01ce445c259"
CANONICAL_RUN_ID = "run_89d967f9000045efa22ed4cc78cfa67f"

GOLDEN_REL = Path("docs/evidence/demo/golden-demo-run.json")
DIGEST_REGISTRY_REL = Path("docs/evidence/golden-fixture-digests.json")
MANIFEST_REL = Path("docs/evidence/ps-035a/manifest-fixture.json")
LINEAGE_REL = Path(
    "tests/fixtures/ps041d/genblaze-multi-provider-bundle-v1.json"
)
LINEAGE_SHA256 = "81e22dea8b73b17e9bf7b23134b7696978d8116be6ebaccf9fe2095dce3801c1"

SEED_STATUS = "golden_demo_evidence_derived"
SEED_SLICE = "PS-042C1"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _load_json(data: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(data)
    except Exception as exc:
        raise RuntimeError(f"frozen_fixture_invalid_json:{label}") from exc

    if not isinstance(value, dict):
        raise RuntimeError(f"frozen_fixture_invalid_object:{label}")

    return value


def _registered_bytes(
    root: Path,
    registry: dict[str, Any],
    relative_path: Path,
) -> bytes:
    entries = registry.get("fixtures")
    if not isinstance(entries, list):
        raise RuntimeError("frozen_fixture_digest_registry_invalid")

    relative_text = relative_path.as_posix()
    entry = next(
        (
            item
            for item in entries
            if isinstance(item, dict) and item.get("path") == relative_text
        ),
        None,
    )
    if entry is None:
        raise RuntimeError(
            f"frozen_fixture_digest_entry_missing:{relative_text}"
        )

    path = root / relative_path
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise RuntimeError(
            f"frozen_fixture_file_missing:{relative_text}"
        ) from exc

    actual_sha256 = hashlib.sha256(data).hexdigest()
    expected_sha256 = entry.get("sha256")
    expected_size = entry.get("size_bytes")

    if actual_sha256 != expected_sha256:
        raise RuntimeError(
            f"frozen_fixture_digest_mismatch:{relative_text}"
        )
    if len(data) != expected_size:
        raise RuntimeError(
            f"frozen_fixture_size_mismatch:{relative_text}"
        )

    return data


def _refuse_b2(*_args: Any, **_kwargs: Any) -> Any:
    raise RuntimeError("frozen_fixture_b2_read_refused")


def maybe_seed_frozen_staging_fixture(
    service: Any,
    *,
    repo_root: Path | None = None,
) -> Any:
    """Seed the exact checked-in judge campaign when explicitly enabled."""

    if os.getenv(ENV_FIXTURES_FROZEN) != "true":
        return service

    if os.getenv(ENVIRONMENT, "").strip().lower() != "staging":
        raise RuntimeError(
            "frozen_fixture_requires_staging_environment"
        )

    root = repo_root or _repo_root()

    registry = _load_json(
        (root / DIGEST_REGISTRY_REL).read_bytes(),
        DIGEST_REGISTRY_REL.as_posix(),
    )
    golden_bytes = _registered_bytes(root, registry, GOLDEN_REL)
    manifest_bytes = _registered_bytes(root, registry, MANIFEST_REL)

    golden = _load_json(golden_bytes, GOLDEN_REL.as_posix())
    manifest_fixture = _load_json(
        manifest_bytes,
        MANIFEST_REL.as_posix(),
    )

    campaign_id = golden.get("campaign_id")
    run_id = golden.get("run_id")

    if campaign_id != CANONICAL_CAMPAIGN_ID:
        raise RuntimeError("frozen_fixture_campaign_id_mismatch")
    if run_id != CANONICAL_RUN_ID:
        raise RuntimeError("frozen_fixture_run_id_mismatch")

    if manifest_fixture.get("campaign_id") != campaign_id:
        raise RuntimeError("frozen_fixture_manifest_campaign_mismatch")
    if manifest_fixture.get("run_id") != run_id:
        raise RuntimeError("frozen_fixture_manifest_run_mismatch")

    manifest_hash = hashlib.sha256(manifest_bytes).hexdigest()
    if manifest_hash != golden.get("manifest_hash"):
        raise RuntimeError("frozen_fixture_manifest_hash_mismatch")
    if manifest_hash != golden.get("manifest_sha256"):
        raise RuntimeError("frozen_fixture_manifest_sha256_mismatch")

    created_at = registry.get("checked_at")
    if not isinstance(created_at, str) or not created_at:
        raise RuntimeError("frozen_fixture_timestamp_missing")

    campaign_record = {
        "campaign_id": campaign_id,
        "name": "ProofStudio Golden Demo",
        "brief": (
            "Checked-in, evidence-derived staging campaign for the "
            "credential-free and account-authorized judge journeys."
        ),
        "target_audience": "Hackathon judges",
        "platform": "ProofStudio free Render staging",
        "objective": "Inspect recorded provenance and lineage evidence.",
        "status": "created",
        "created_at": created_at,
        "slice": SEED_SLICE,
    }

    run_record = {
        "run_id": run_id,
        "campaign_id": campaign_id,
        "status": SEED_STATUS,
        "prompt": None,
        "budget_mode": "free-only",
        "dry_run": False,
        "run_live": False,
        "selected_provider": None,
        "selected_model": None,
        "api_method": None,
        "job_type": None,
        "fallback_used": False,
        "attempt_count": 0,
        "asset_count": 0,
        "manifest_uri": golden.get("manifest_uri"),
        "prompt_packet_ref": None,
        "attempt_ledger_ref": None,
        "provider_note_ref": None,
        "created_at": created_at,
        "started_at": None,
        "finished_at": None,
        "links": {
            "self": f"/runs/{run_id}",
            "attempts": f"/runs/{run_id}/attempts",
            "assets": f"/runs/{run_id}/assets",
            "manifest": f"/runs/{run_id}/manifest",
            "passport": f"/runs/{run_id}/passport",
        },
        "slice": SEED_SLICE,
        "attempts": [],
        "assets": [],
        "manifest_hash": manifest_hash,
        "in_memory_manifest_verify": True,
        "stored_manifest_verify": None,
        "transfer_failures": [],
        "stored_transfer_failures": [],
        "local_image": None,
        "local_prompt_packet": None,
        "local_attempt_ledger": None,
        "local_provider_note": None,
        "truth_boundary": golden.get("truth_boundary"),
        "error": None,
        "blocked_reason": None,
    }

    manifest_record = {
        "run_id": run_id,
        "ready": True,
        "manifest_uri": golden.get("manifest_uri"),
        "manifest_hash": manifest_hash,
        "in_memory_manifest_verify": True,
        "stored_manifest_verify": None,
        "transfer_failures": [],
        "stored_transfer_failures": [],
        "asset_count": 0,
        "not_ready_reason": None,
    }

    service.store.create_campaign(campaign_id, campaign_record)
    service.store.create_run(run_id, run_record)
    service.store.set_attempts(run_id, [])
    service.store.set_assets(run_id, [])
    service.store.set_manifest(run_id, manifest_record)

    try:
        lineage_bytes = (root / LINEAGE_REL).read_bytes()
    except OSError as exc:
        raise RuntimeError("frozen_fixture_lineage_missing") from exc

    lineage_sha256 = hashlib.sha256(lineage_bytes).hexdigest()
    if lineage_sha256 != LINEAGE_SHA256:
        raise RuntimeError(
            f"frozen_fixture_lineage_digest_mismatch:{LINEAGE_REL.as_posix()}"
        )

    payload = parse_bundle_bytes(lineage_bytes)
    imported = service.import_genblaze_bundle(
        campaign_id,
        payload,
        b2_json_reader=_refuse_b2,
    )

    if imported.bundle.campaign_id != campaign_id:
        raise RuntimeError("frozen_fixture_lineage_campaign_mismatch")
    if not imported.nodes:
        raise RuntimeError("frozen_fixture_lineage_nodes_missing")
    if not imported.edges:
        raise RuntimeError("frozen_fixture_lineage_edges_missing")

    return service


__all__ = [
    "CANONICAL_CAMPAIGN_ID",
    "CANONICAL_RUN_ID",
    "DIGEST_REGISTRY_REL",
    "ENVIRONMENT",
    "ENV_FIXTURES_FROZEN",
    "GOLDEN_REL",
    "LINEAGE_REL",
    "MANIFEST_REL",
    "maybe_seed_frozen_staging_fixture",
]
