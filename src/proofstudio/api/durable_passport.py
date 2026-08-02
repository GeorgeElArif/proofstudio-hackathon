"""Durable passport rehydrate helpers for PS-020.

This module is deliberately gated.

Default behavior:
- no B2 read
- no B2 write
- no provider call
- no fake archive
- no fake passport

The first PS-020 implementation supports deterministic local durable-index
rehydration for tests and public-route hardening. Real B2 reads remain behind
an explicit flag and existing PS-010 archive helpers.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from proofstudio.api.archive import read_archive_from_b2
from proofstudio.api.passport import PASSPORT_TRUTH_BOUNDARY, build_provenance_passport

DURABLE_SOURCE_IN_MEMORY = "in_memory"
DURABLE_SOURCE_LOCAL_REHYDRATED = "local_rehydrated"
DURABLE_SOURCE_B2_REHYDRATED = "b2_rehydrated"
DURABLE_SOURCE_MISSING = "missing"

ENV_READ_ENABLED = "PROOFSTUDIO_DURABLE_PASSPORT_READ_ENABLED"
ENV_B2_READ_ENABLED = "PROOFSTUDIO_DURABLE_PASSPORT_B2_READ_ENABLED"
ENV_INDEX_DIR = "PROOFSTUDIO_DURABLE_PASSPORT_INDEX_DIR"
ENV_INDEX_FILE = "PROOFSTUDIO_DURABLE_PASSPORT_INDEX_FILE"
ENV_B2_PREFIX = "PROOFSTUDIO_B2_PREFIX"

# PS-025 -- public durable passport unlock for the single verified golden demo
# run. This is a deliberately narrow allowlist: ONLY the run_id recorded in the
# checked-in golden demo manifest resolves through this path. It reads the
# checked-in manifest only (a public, evidence-derived file with no secrets),
# performs no B2 read, calls no provider, and never fabricates attempts, assets,
# or manifest verification. Any other run_id falls through to the normal
# missing-run path (NotFoundError -> 404), so arbitrary public durable reads are
# NOT enabled.
ENV_GOLDEN_DEMO_MANIFEST = "PROOFSTUDIO_GOLDEN_DEMO_MANIFEST"
GOLDEN_DEMO_MANIFEST_REL = Path("docs") / "evidence" / "demo" / "golden-demo-run.json"
GOLDEN_DEMO_UNLOCK_SCOPE = "golden_demo_only"
GOLDEN_DEMO_SOURCE = "golden_demo_evidence_derived"
GOLDEN_DEMO_INDEX_SCHEMA_VERSION = "ps-025.evidence_derived.v1"

REQUIRED_B2_ENV = ("B2_KEY_ID", "B2_APP_KEY", "B2_BUCKET", "B2_REGION")


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def durable_read_enabled() -> bool:
    return _truthy(os.getenv(ENV_READ_ENABLED))


def durable_b2_read_enabled() -> bool:
    return durable_read_enabled() and _truthy(os.getenv(ENV_B2_READ_ENABLED))


def b2_env_from_os() -> dict[str, str] | None:
    values = {name: os.getenv(name) or "" for name in REQUIRED_B2_ENV}
    if any(not value for value in values.values()):
        return None
    return values


def b2_prefix_from_os() -> str:
    return os.getenv(ENV_B2_PREFIX) or "proofstudio"


def build_run_index(
    archive: dict[str, Any],
    *,
    archive_uri: str | None = None,
    archive_sha256: str | None = None,
    archive_storage_mode: str = "local",
) -> dict[str, Any]:
    run_id = archive.get("run_id")
    campaign_id = archive.get("campaign_id")
    if not run_id:
        raise ValueError("Cannot build durable run index without run_id")

    return {
        "index_schema_version": "ps-020.v1",
        "run_id": run_id,
        "campaign_id": campaign_id,
        "archive_uri": archive_uri,
        "archive_sha256": archive_sha256,
        "archive_storage_mode": archive_storage_mode,
        "manifest_uri": archive.get("manifest_uri"),
        "manifest_hash": archive.get("manifest_hash"),
        "created_at": archive.get("archived_at") or archive.get("created_at"),
        "proofstudio_schema_version": archive.get("archive_schema_version"),
        "source": "proofstudio_run_archive",
        "truth_boundary": (
            "Durable index only points to stored run-archive evidence. "
            "It does not prove legal authenticity, semantic truth, or human authorship."
        ),
        "archive_inline": archive if archive_storage_mode == "local_inline" else None,
    }


def write_run_index_local(index: dict[str, Any], index_dir: str | Path) -> Path:
    run_id = index.get("run_id")
    if not run_id:
        raise ValueError("Cannot write durable run index without run_id")

    root = Path(index_dir)
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{run_id}.json"
    path.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def _read_index_file(path: Path, run_id: str) -> dict[str, Any] | None:
    if not path.exists():
        return None

    payload = json.loads(path.read_text(encoding="utf-8"))

    if isinstance(payload, dict) and payload.get("run_id") == run_id:
        return payload

    if isinstance(payload, dict) and isinstance(payload.get(run_id), dict):
        return payload[run_id]

    return None


def read_run_index_local(run_id: str) -> dict[str, Any] | None:
    file_value = os.getenv(ENV_INDEX_FILE)
    if file_value:
        found = _read_index_file(Path(file_value), run_id)
        if found:
            return found

    dir_value = os.getenv(ENV_INDEX_DIR)
    if dir_value:
        found = _read_index_file(Path(dir_value) / f"{run_id}.json", run_id)
        if found:
            return found

    return None


def _archive_from_index(index: dict[str, Any]) -> tuple[dict[str, Any], str]:
    inline = index.get("archive_inline")
    if isinstance(inline, dict):
        return inline, DURABLE_SOURCE_LOCAL_REHYDRATED

    archive_uri = index.get("archive_uri")
    if not archive_uri:
        raise FileNotFoundError("Durable run index has no archive_inline or archive_uri")

    if not durable_b2_read_enabled():
        raise PermissionError("B2 durable passport read is disabled")

    b2_env = b2_env_from_os()
    if not b2_env:
        raise PermissionError("B2 durable passport read is enabled but B2 env is incomplete")

    archive = read_archive_from_b2(
        archive_uri,
        b2_env=b2_env,
        b2_prefix=b2_prefix_from_os(),
    )
    return archive, DURABLE_SOURCE_B2_REHYDRATED


def try_rehydrate_passport(service: Any, run_id: str) -> dict[str, Any] | None:
    if not durable_read_enabled():
        return None

    index = read_run_index_local(run_id)
    if not index:
        return None

    archive, durable_source = _archive_from_index(index)

    result = service.rehydrate_run_from_archive(
        archive,
        source_kind="inline" if durable_source == DURABLE_SOURCE_LOCAL_REHYDRATED else "b2",
    )

    archive_evidence = {
        "archive_uri": index.get("archive_uri"),
        "archive_sha256": index.get("archive_sha256"),
        "archive_storage_mode": index.get("archive_storage_mode"),
        "rehydrate_source": durable_source,
        "rehydrate_completed": bool(result.get("ok")),
        "restored_manifest_uri": result.get("restored_manifest_uri"),
        "restored_manifest_hash": result.get("restored_manifest_hash"),
        "no_live_provider_call_during_rehydrate": result.get("provider_calls_made") == 0,
    }

    passport = service.get_run_passport(
        run_id,
        archive_evidence=archive_evidence,
        source="archive_rehydrated_run",
    )
    passport["durable_passport"] = {
        "status": "available",
        "source": durable_source,
        "index_schema_version": index.get("index_schema_version"),
        "run_id": run_id,
        "campaign_id": index.get("campaign_id"),
        "truth_boundary": index.get("truth_boundary"),
    }
    return passport


# ---------------------------------------------------------------------------
# PS-025 -- golden demo public durable passport unlock (evidence-derived only)
# ---------------------------------------------------------------------------

def _golden_demo_manifest_path() -> Path:
    """Resolve the golden demo manifest path.

    Order: explicit env override, then the repo-relative path from this file
    (``src/proofstudio/api/durable_passport.py`` -> repo root is parents[3]),
    then a CWD-relative fallback. The manifest is a checked-in public evidence
    file with no secrets; reading it is always safe.
    """
    env_value = os.getenv(ENV_GOLDEN_DEMO_MANIFEST)
    if env_value:
        return Path(env_value)
    try:
        repo_root = Path(__file__).resolve().parents[3]
        candidate = repo_root / GOLDEN_DEMO_MANIFEST_REL
        if candidate.exists():
            return candidate
    except Exception:
        pass
    return Path.cwd() / GOLDEN_DEMO_MANIFEST_REL


def load_golden_demo_manifest() -> dict[str, Any] | None:
    """Load the checked-in golden demo manifest, or None if it cannot resolve.

    Returns None (instead of raising) so the public passport path can fall
    through to an honest 404 when the manifest is unavailable, rather than
    crashing the request.
    """
    path = _golden_demo_manifest_path()
    try:
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def golden_demo_run_id() -> str | None:
    """Return the verified golden demo run_id from the manifest, or None."""
    manifest = load_golden_demo_manifest()
    if not manifest:
        return None
    run_id = manifest.get("run_id")
    return run_id if isinstance(run_id, str) and run_id else None


def golden_demo_unlock_enabled() -> bool:
    """True when the golden demo unlock path is available.

    It is available when the manifest resolves AND records the required durable
    evidence fields. It is intentionally NOT gated behind the durable read / B2
    read flags: the whole point of PS-025 is to unlock the single golden run
    publicly without enabling broad durable reads and without requiring B2
    credentials. Safety comes from the narrow allowlist (run_id equality), not
    from a gate.
    """
    manifest = load_golden_demo_manifest()
    if not manifest:
        return False
    required = ("run_id", "campaign_id", "archive_uri", "archive_sha256")
    return all(manifest.get(field) for field in required)


def try_golden_demo_passport(service: Any, run_id: str) -> dict[str, Any] | None:
    """Resolve the golden demo passport from checked-in evidence only.

    Returns None when ``run_id`` is not exactly the verified golden demo run_id,
    so any other run_id falls through to the normal missing-run -> 404 path.
    When it matches, builds a Provenance Passport from the manifest's durable
    fields only: no B2 read, no provider call, no fabricated attempts/assets/
    manifest. The PS-021 rehydrate provenance (``rehydrate_source =
    b2_rehydrated``, zero provider calls) is recorded verbatim from the manifest
    so the passport honestly reflects the underlying durable evidence.
    """
    if not run_id:
        return None
    manifest = load_golden_demo_manifest()
    if not manifest:
        return None
    if run_id != manifest.get("run_id"):
        return None

    campaign_id = manifest.get("campaign_id")
    archive_uri = manifest.get("archive_uri")
    archive_sha256 = manifest.get("archive_sha256")
    rehydrate_source = manifest.get("rehydrate_source")
    provider_calls = manifest.get("provider_calls_during_rehydrate")
    no_live = manifest.get("no_live_provider_call_during_rehydrate")
    manifest_truth_boundary = manifest.get("truth_boundary") or PASSPORT_TRUTH_BOUNDARY

    archive_evidence: dict[str, Any] = {
        "archive_uri": archive_uri,
        "archive_sha256": archive_sha256,
        "archive_storage_mode": "b2_object_content",
        "rehydrate_source": rehydrate_source,
        "rehydrate_completed": True,
        "restored_manifest_uri": None,
        "restored_manifest_hash": None,
        "no_live_provider_call_during_rehydrate": bool(no_live),
    }

    run_record: dict[str, Any] = {
        "run_id": run_id,
        "campaign_id": campaign_id,
        "status": GOLDEN_DEMO_SOURCE,
    }
    campaign_record: dict[str, Any] = {"campaign_id": campaign_id}

    passport = build_provenance_passport(
        run=run_record,
        campaign=campaign_record,
        attempts=[],
        assets=[],
        manifest={},
        archive_evidence=archive_evidence,
        source=GOLDEN_DEMO_SOURCE,
    )

    passport["golden_demo_unlock"] = {
        "public_unlock_scope": GOLDEN_DEMO_UNLOCK_SCOPE,
        "source": GOLDEN_DEMO_SOURCE,
        "source_manifest": str(GOLDEN_DEMO_MANIFEST_REL),
        "run_id": run_id,
        "campaign_id": campaign_id,
        "archive_uri": archive_uri,
        "archive_sha256": archive_sha256,
        "rehydrate_source": rehydrate_source,
        "provider_calls_during_rehydrate": provider_calls,
        "no_live_provider_call_during_rehydrate": bool(no_live),
        "no_broad_public_durable_read": True,
        "local_contract_proof": "available_via_testclient_or_configured_base_url",
        "public_deployment_pending": True,
        "truth_boundary": manifest_truth_boundary,
    }
    passport["durable_passport"] = {
        "status": "available",
        "source": GOLDEN_DEMO_SOURCE,
        "index_schema_version": GOLDEN_DEMO_INDEX_SCHEMA_VERSION,
        "run_id": run_id,
        "campaign_id": campaign_id,
        "truth_boundary": manifest_truth_boundary,
    }
    return passport
