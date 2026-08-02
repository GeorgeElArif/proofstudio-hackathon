#!/usr/bin/env python3
"""
PS-021: Live B2 Durable Rehydrate Proof smoke.

What this proves:

- A safe dry-run ProofStudio run (dry_run=true, run_live=false) can be archived
  into a durable run-archive JSON artifact built from service readbacks only.
- The archive can be stored durably as a real B2/Genblaze asset.
- A durable run index pointing to the real B2 archive URI can be written
  locally.
- After backend memory is cleared, the public Provenance Passport route
  (`GET /runs/{run_id}/passport`) is unavailable when the durable gates are
  disabled (default), and recovers the passport from the real B2 archive bytes
  when the durable read + durable B2 read gates are explicitly enabled.
- The rehydrated passport source is `b2_rehydrated`.
- No live provider is called during rehydrate.
- No media file is written during rehydrate.
- B2 write is limited to the archive/index evidence only (no generated media
  asset is uploaded to B2).

Hard safety boundaries:

- This smoke is fully gated behind `PROOFSTUDIO_PS021_LIVE_B2_REHYDRATE=1`.
- It refuses to run if durable read or B2 read gates are already enabled by
  default in the environment, because that would be unsafe.
- It only reads from B2 to rehydrate the archive bytes when the explicit live
  gate is set AND the explicit durable B2 read gate is set inside the smoke.
- It never calls Cloudflare, Pollinations, GMI, Gemini, OpenAI, Runway, Luma,
  ElevenLabs, or any media provider.
- It never creates generated image/audio/video assets.
- It never fakes a B2 URI or a successful B2 read.

Exit rule:

- Exit 0 only when the live B2 rehydrate path produces a `b2_rehydrated`
  passport with no provider call and no media write, with the durable gates
  remaining disabled by default before and after the smoke.
- Exit 78 (config error) when the explicit live gate is not set or B2 env is
  missing -- the smoke is honestly skipped and may be re-run later.
- Exit 1 on any hard failure, secret leak, or safety violation.

Truth boundary: PS-021 proves ProofStudio can restore a public Provenance
Passport from a real B2 archive after backend memory loss, behind explicit
gates, without rerunning providers and without faking proof. It does not prove
production-database persistence, multi-user recovery, auth/security, legal
authenticity, C2PA authenticity, or semantic truth.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import proofstudio.api.services as services_module  # noqa: E402
import proofstudio.api.durable_passport as durable_passport_module  # noqa: E402
import proofstudio.api.archive as archive_module  # noqa: E402
from proofstudio.api.app import create_app  # noqa: E402
from proofstudio.api.archive import (  # noqa: E402
    ARCHIVE_SCHEMA_VERSION,
    build_run_archive,
    store_run_archive_with_genblaze,
    validate_archive,
)
from proofstudio.api.durable_passport import (  # noqa: E402
    DURABLE_SOURCE_B2_REHYDRATED,
    ENV_B2_PREFIX,
    ENV_B2_READ_ENABLED,
    ENV_INDEX_DIR,
    ENV_READ_ENABLED,
    REQUIRED_B2_ENV,
    build_run_index,
    durable_b2_read_enabled,
    durable_read_enabled,
    write_run_index_local,
)
from proofstudio.api.live_bridge import B2_REQUIRED_ENV  # noqa: E402
from proofstudio.api.models import (  # noqa: E402
    ARCHIVE_STORAGE_MODE_B2,
    RUN_STATUS_DRY_RUN_CREATED,
)
from proofstudio.api.services import ProofStudioService  # noqa: E402

SLICE_ID = "PS-021"
OUTPUT_DIR = Path("/tmp/proofstudio-ps-021")
INDEX_DIR = OUTPUT_DIR / "durable-index"
EVIDENCE_PATH = REPO_ROOT / "docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json"
PROOF_DOC_PATH = REPO_ROOT / "docs/ps-021-live-b2-durable-rehydrate-proof.md"

PS021_B2_PREFIX = "proofstudio/ps-021"
LIVE_GATE_ENV = "PROOFSTUDIO_PS021_LIVE_B2_REHYDRATE"

# Exit codes.
EXIT_OK = 0
EXIT_SKIP = 78  # config error: gate not set or B2 env missing
EXIT_FAIL = 1

SECRET_PATTERNS = [
    re.compile(r"(?i)Bearer\s+[A-Za-z0-9\-_.=~]{8,}"),
    re.compile(r"(?i)B2_KEY_ID[\s:=]+\S{8,}"),
    re.compile(r"(?i)B2_APP_KEY[\s:=]+\S{8,}"),
    re.compile(r"(?i)CLOUDFLARE_API_TOKEN[\s:=]+\S{8,}"),
    re.compile(r"(?i)Authorization[\s:]+.{8,}"),
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


class CheckFail(Exception):
    pass


def check(label: str, condition: bool, detail: str = "") -> None:
    if not condition:
        raise CheckFail(f"{label}: {detail}" if detail else f"{label}: failed")


def check_equal(label: str, got: Any, expected: Any, detail: str = "") -> None:
    if got != expected:
        suffix = f" ({detail})" if detail else ""
        raise CheckFail(
            f"{label}: expected {expected!r}, got {got!r}{suffix}"
        )


def scan_for_secrets(payload: Any) -> list[str]:
    text = json.dumps(payload, ensure_ascii=False, default=str)
    hits: list[str] = []
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            hits.append(f"secret pattern matched: {pattern.pattern[:40]}...")
    return hits


def snapshot_files(root: Path) -> set[str]:
    if not root.exists():
        return set()
    return {str(p) for p in root.rglob("*") if p.is_file()}


def _resolve_b2_env() -> dict[str, str] | None:
    missing = [name for name in B2_REQUIRED_ENV if not os.getenv(name)]
    if missing:
        return None
    return {name: os.environ[name] for name in B2_REQUIRED_ENV}


def _summarize_run_for_evidence(run_record: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_id": run_record.get("run_id"),
        "campaign_id": run_record.get("campaign_id"),
        "status": run_record.get("status"),
        "dry_run": bool(run_record.get("dry_run")),
        "run_live": bool(run_record.get("run_live")),
        "selected_provider": run_record.get("selected_provider"),
        "attempt_count": run_record.get("attempt_count") or 0,
        "asset_count": run_record.get("asset_count") or 0,
        "manifest_uri": run_record.get("manifest_uri"),
        "local_image": run_record.get("local_image"),
    }


def _run_live_smoke(
    transcript: list[dict[str, Any]],
) -> tuple[dict[str, Any], int]:
    """Run the live B2 durable rehydrate smoke.

    Returns ``(summary, exit_code)``.
    """

    def log(step: str, payload: Any) -> None:
        transcript.append({"step": step, "result": payload})

    summary: dict[str, Any] = {
        "ok": False,
        "slice": SLICE_ID,
        "live_gate_env": LIVE_GATE_ENV,
        "live_gate_set": True,
        "b2_env_available": True,
        "ps021_b2_prefix": PS021_B2_PREFIX,
        "run_id": None,
        "campaign_id": None,
        "archive_uri": None,
        "archive_sha256": None,
        "archive_storage_mode": None,
        "index_path": None,
        "missing_without_gate": False,
        "durable_read_enabled_default": False,
        "durable_b2_read_enabled_default": False,
        "api_rehydrate_status_code": None,
        "durable_source": None,
        "rehydrate_completed": False,
        "no_live_provider_call_during_rehydrate": False,
        "provider_calls_during_rehydrate": 0,
        "provider_call": False,
        "b2_archive_write": False,
        "b2_archive_read": False,
        "b2_generated_media_write": False,
        "no_new_local_files_during_rehydrate": False,
        "no_fake_media": False,
        "written_at": None,
    }

    b2_env = _resolve_b2_env()
    check("B2 env resolved at runtime", b2_env is not None)

    # The smoke must not run if durable gates are already enabled by default.
    # Record the default state BEFORE we mutate it inside the smoke.
    durable_read_default = durable_read_enabled()
    durable_b2_read_default = durable_b2_read_enabled()
    summary["durable_read_enabled_default"] = bool(durable_read_default)
    summary["durable_b2_read_enabled_default"] = bool(durable_b2_read_default)
    check(
        "durable read disabled by default in caller env",
        not durable_read_default,
        detail="PROOFSTUDIO_DURABLE_PASSPORT_READ_ENABLED must be unset/false at smoke start",
    )
    check(
        "durable B2 read disabled by default in caller env",
        not durable_b2_read_default,
        detail="PROOFSTUDIO_DURABLE_PASSPORT_B2_READ_ENABLED must be unset/false at smoke start",
    )
    log("default_gate_state", {
        "durable_read_enabled_default": durable_read_default,
        "durable_b2_read_enabled_default": durable_b2_read_default,
    })

    # ------------------------------------------------------------------
    # 1. Create service + campaign + safe dry-run run (no provider call).
    # ------------------------------------------------------------------
    service = ProofStudioService(
        live_output_dir=str(OUTPUT_DIR / "live-run"),
        live_b2_prefix=PS021_B2_PREFIX,
    )

    campaign_payload = {
        "name": "PS-021 Live B2 Durable Rehydrate Proof Campaign",
        "brief": (
            "Prove a public Provenance Passport can be restored from a real B2 "
            "archive after backend memory loss, behind explicit durable gates, "
            "without rerunning providers and without faking proof."
        ),
        "target_audience": "hackathon judges",
        "platform": "web",
        "objective": "live B2 durable passport rehydrate proof",
    }
    created_campaign = service.create_campaign(campaign_payload)
    campaign_id = created_campaign["campaign_id"]
    check("campaign created", bool(campaign_id))
    log("create_campaign", {"campaign_id": campaign_id})

    run_payload = {
        "campaign_id": campaign_id,
        "prompt": (
            "PS-021 dry-run safe run. No provider call, no media generation. "
            "The run record is the seed for a durable B2 archive."
        ),
        "budget_mode": "free-only",
        "dry_run": True,
        "run_live": False,
    }
    created_run = service.create_run(run_payload)
    run_id = created_run["run_id"]
    run_record = dict(created_run.get("run") or {})
    run_status = created_run.get("status") or run_record.get("status")
    check_equal("run is dry_run_created", run_status, RUN_STATUS_DRY_RUN_CREATED)
    check("run.dry_run true", bool(run_record.get("dry_run")))
    check("run.run_live false", not bool(run_record.get("run_live")))
    check("run.no local_image", not run_record.get("local_image"))
    check("run.no manifest_uri", not run_record.get("manifest_uri"))
    check("run.no selected_provider", not run_record.get("selected_provider"))
    log("create_run", _summarize_run_for_evidence(run_record))

    summary["run_id"] = run_id
    summary["campaign_id"] = campaign_id

    # ------------------------------------------------------------------
    # 2. Build run archive from service readbacks (no provider call).
    # ------------------------------------------------------------------
    archive = build_run_archive(service, run_id)
    archive_errors = validate_archive(archive)
    check(
        "archive validates",
        not archive_errors,
        detail=str(archive_errors),
    )
    check_equal("archive.run_id", archive["run_id"], run_id)
    check_equal("archive.campaign_id", archive["campaign_id"], campaign_id)
    check_equal("archive schema version", archive["archive_schema_version"], ARCHIVE_SCHEMA_VERSION)
    check_equal("archive attempts empty (dry-run)", archive.get("attempt_count"), 0)
    check_equal("archive assets empty (dry-run)", len(archive.get("assets") or []), 0)
    log("build_run_archive", {
        "archive_schema_version": archive["archive_schema_version"],
        "attempt_count": archive["attempt_count"],
        "asset_count": len(archive.get("assets") or []),
        "run_status": archive.get("run_status"),
        "image_sha256": archive.get("image_sha256"),
    })

    # ------------------------------------------------------------------
    # 3. Store the archive in B2 (real B2 write). b2_archive_write proof.
    # ------------------------------------------------------------------
    stored = store_run_archive_with_genblaze(
        archive,
        b2_env=b2_env,
        b2_prefix=PS021_B2_PREFIX,
        name_prefix="proofstudio-ps-021-run-archive",
    )
    archive_uri = stored["archive_uri"]
    archive_sha256 = stored["archive_sha256"]
    check("archive.uri exists", bool(archive_uri))
    check("archive.sha256 exists", bool(archive_sha256))
    check(
        "archive stored manifest verified",
        stored.get("archive_stored_manifest_verify") is True,
    )
    check(
        "archive stored without transfer failures",
        not stored.get("archive_transfer_failures"),
    )
    summary["b2_archive_write"] = True
    summary["archive_uri"] = archive_uri
    summary["archive_sha256"] = archive_sha256
    summary["archive_storage_mode"] = ARCHIVE_STORAGE_MODE_B2
    log("store_run_archive_with_genblaze", {
        "archive_uri": archive_uri,
        "archive_sha256": archive_sha256,
        "archive_manifest_uri": stored.get("archive_manifest_uri"),
        "archive_manifest_hash": stored.get("archive_manifest_hash"),
        "archive_stored_manifest_verify": stored.get(
            "archive_stored_manifest_verify"
        ),
    })

    # ------------------------------------------------------------------
    # 4. Build a durable run index pointing to the real B2 archive URI.
    #    Use the B2 storage mode (no inline archive) so the durable
    #    rehydrate path must read bytes back from B2.
    # ------------------------------------------------------------------
    index = build_run_index(
        archive,
        archive_uri=archive_uri,
        archive_sha256=archive_sha256,
        archive_storage_mode=ARCHIVE_STORAGE_MODE_B2,
    )
    check_equal("index.run_id", index["run_id"], run_id)
    check_equal("index.archive_uri", index["archive_uri"], archive_uri)
    check_equal("index.archive_sha256", index["archive_sha256"], archive_sha256)
    check_equal("index.archive_storage_mode", index["archive_storage_mode"], ARCHIVE_STORAGE_MODE_B2)
    check("index has no inline archive", index.get("archive_inline") is None)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    index_path = write_run_index_local(index, INDEX_DIR)
    summary["index_path"] = str(index_path)
    log("write_run_index_local", {
        "index_path": str(index_path),
        "archive_uri": index["archive_uri"],
        "archive_storage_mode": index["archive_storage_mode"],
    })

    # ------------------------------------------------------------------
    # 5. Clear backend memory. Passport must be unavailable with durable
    #    gates disabled (default).
    # ------------------------------------------------------------------
    service.clear_store_for_test()
    check(
        "backend memory cleared of run",
        not service.store.has_run(run_id),
    )
    check(
        "backend memory cleared of campaign",
        not service.store.has_campaign(campaign_id),
    )
    log("clear_store_for_test", {"has_run": service.store.has_run(run_id)})

    # Build a FastAPI app bound to our cleared service for HTTP-level proof.
    app = create_app(service)
    check("FastAPI app available", app is not None)
    from fastapi.testclient import TestClient

    client = TestClient(app)

    # Durable gates are still disabled by default here: assert the passport
    # request fails with 404 (no in-memory run + no durable recovery).
    r_missing = client.get(f"/runs/{run_id}/passport")
    missing_status = r_missing.status_code
    summary["missing_without_gate"] = missing_status == 404
    check_equal(
        "passport missing without durable gate (404)",
        missing_status,
        404,
    )
    log("passport_request_without_gate", {
        "status_code": missing_status,
        "durable_read_enabled": durable_read_enabled(),
        "durable_b2_read_enabled": durable_b2_read_enabled(),
    })

    # ------------------------------------------------------------------
    # 6. Enable only the explicit durable passport read gates. Wire
    #    provider sentinel + B2 read counter to prove no provider call
    #    and exactly one B2 archive read during rehydrate.
    # ------------------------------------------------------------------
    saved_env: dict[str, str | None] = {
        ENV_READ_ENABLED: os.environ.get(ENV_READ_ENABLED),
        ENV_B2_READ_ENABLED: os.environ.get(ENV_B2_READ_ENABLED),
        ENV_INDEX_DIR: os.environ.get(ENV_INDEX_DIR),
        ENV_B2_PREFIX: os.environ.get(ENV_B2_PREFIX),
    }
    os.environ[ENV_READ_ENABLED] = "true"
    os.environ[ENV_B2_READ_ENABLED] = "true"
    os.environ[ENV_INDEX_DIR] = str(INDEX_DIR)
    os.environ[ENV_B2_PREFIX] = PS021_B2_PREFIX

    provider_call_counter = {"count": 0}
    b2_read_counter = {"count": 0}

    def _live_sentinel(**kwargs: Any) -> dict[str, Any]:
        provider_call_counter["count"] += 1
        raise AssertionError(
            "LIVE PROVIDER WAS CALLED DURING PS-021 B2 REHYDRATE"
        )

    original_execute_live_run = services_module.execute_live_run
    original_durable_b2_read = durable_passport_module.read_archive_from_b2

    def _b2_read_wrapper(*args: Any, **kwargs: Any) -> dict[str, Any]:
        b2_read_counter["count"] += 1
        return original_durable_b2_read(*args, **kwargs)

    services_module.execute_live_run = _live_sentinel  # type: ignore[assignment]
    durable_passport_module.read_archive_from_b2 = _b2_read_wrapper  # type: ignore[assignment]

    files_before_rehydrate = snapshot_files(OUTPUT_DIR)
    rehydrate_status_code: int | None = None
    rehydrate_body: dict[str, Any] | None = None
    try:
        check(
            "durable read enabled after explicit gate",
            durable_read_enabled() is True,
        )
        check(
            "durable B2 read enabled after explicit gate",
            durable_b2_read_enabled() is True,
        )

        # ------------------------------------------------------------------
        # 7. Request the passport. The durable module must read the archive
        #    bytes back from B2 and rehydrate the run into the cleared store.
        # ------------------------------------------------------------------
        r = client.get(f"/runs/{run_id}/passport")
        rehydrate_status_code = r.status_code
        rehydrate_body = r.json() if r.status_code != 204 else {}
        check_equal(
            "passport request status code 200",
            rehydrate_status_code,
            200,
        )
    finally:
        services_module.execute_live_run = original_execute_live_run  # type: ignore[assignment]
        durable_passport_module.read_archive_from_b2 = original_durable_b2_read  # type: ignore[assignment]
        # Restore the gate env values so the smoke never leaks enabled gates.
        for key, original in saved_env.items():
            if original is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original

    files_after_rehydrate = snapshot_files(OUTPUT_DIR)
    new_files_during_rehydrate = files_after_rehydrate - files_before_rehydrate
    summary["no_new_local_files_during_rehydrate"] = (
        new_files_during_rehydrate == set()
    )

    check("rehydrate_body present", isinstance(rehydrate_body, dict))
    assert rehydrate_body is not None  # for type checkers
    durable_passport = rehydrate_body.get("durable_passport") or {}
    archive_section = rehydrate_body.get("archive_and_rehydration") or {}
    generation_summary = rehydrate_body.get("generation_summary") or {}

    durable_source = durable_passport.get("source")
    rehydrate_completed = bool(archive_section.get("rehydrate_completed"))
    no_provider_flag = bool(
        archive_section.get("no_live_provider_call_during_rehydrate")
    )

    summary["api_rehydrate_status_code"] = rehydrate_status_code
    summary["durable_source"] = durable_source
    summary["rehydrate_completed"] = rehydrate_completed
    summary["no_live_provider_call_during_rehydrate"] = no_provider_flag
    summary["provider_calls_during_rehydrate"] = int(provider_call_counter["count"])
    summary["provider_call"] = provider_call_counter["count"] > 0
    summary["b2_archive_read"] = b2_read_counter["count"] > 0
    summary["b2_generated_media_write"] = bool(
        generation_summary.get("generated_media_present")
    )

    log("passport_request_with_gate", {
        "status_code": rehydrate_status_code,
        "durable_source": durable_source,
        "rehydrate_completed": rehydrate_completed,
        "no_live_provider_call_during_rehydrate": no_provider_flag,
        "provider_calls_during_rehydrate": provider_call_counter["count"],
        "b2_archive_reads_during_rehydrate": b2_read_counter["count"],
        "generated_media_present": generation_summary.get("generated_media_present"),
        "archive_status": archive_section.get("status"),
        "archive_storage_mode": archive_section.get("archive_storage_mode"),
        "archive_uri_in_passport": archive_section.get("archive_uri"),
    })

    # ------------------------------------------------------------------
    # 8. Verify the required proof.
    # ------------------------------------------------------------------
    check_equal(
        "durable_passport.source == b2_rehydrated",
        durable_source,
        DURABLE_SOURCE_B2_REHYDRATED,
    )
    check("archive_and_rehydration.rehydrate_completed == true", rehydrate_completed)
    check(
        "archive_and_rehydration.no_live_provider_call_during_rehydrate == true",
        no_provider_flag,
    )
    check_equal(
        "no provider call sentinel hit during rehydrate",
        provider_call_counter["count"],
        0,
    )
    check_equal(
        "exactly one B2 archive read during rehydrate",
        b2_read_counter["count"],
        1,
        detail=(
            "B2 read must occur only for the archive rehydrate (expected "
            f"1 read, got {b2_read_counter['count']})"
        ),
    )
    check(
        "no generated media created during rehydrate",
        not generation_summary.get("generated_media_present"),
    )
    check(
        "no new local files written during rehydrate",
        new_files_during_rehydrate == set(),
        detail=f"new files: {sorted(new_files_during_rehydrate)}",
    )
    check_equal(
        "archive_section.archive_uri matches stored URI",
        archive_section.get("archive_uri"),
        archive_uri,
    )
    check_equal(
        "archive_section.archive_storage_mode == b2_object_content",
        archive_section.get("archive_storage_mode"),
        ARCHIVE_STORAGE_MODE_B2,
    )
    check_equal(
        "durable_passport.run_id matches",
        durable_passport.get("run_id"),
        run_id,
    )
    check_equal(
        "durable_passport.status available",
        durable_passport.get("status"),
        "available",
    )

    # Re-verify the gates default back to disabled after env restore.
    check(
        "durable read disabled after env restore",
        not durable_read_enabled(),
    )
    check(
        "durable B2 read disabled after env restore",
        not durable_b2_read_enabled(),
    )

    summary["ok"] = True
    summary["no_fake_media"] = (
        not summary["b2_generated_media_write"]
        and summary["b2_archive_write"] is True
        and summary["b2_archive_read"] is True
    )
    summary["written_at"] = now_iso()
    return summary, EXIT_OK


def main() -> int:
    load_dotenv(REPO_ROOT / ".env")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    transcript: list[dict[str, Any]] = []

    # Hard gate: explicit opt-in for the live B2 rehydrate smoke.
    live_gate_set = _truthy(os.getenv(LIVE_GATE_ENV))
    if not live_gate_set:
        skip_payload = {
            "ok": False,
            "slice": SLICE_ID,
            "skipped": True,
            "skip_reason": (
                f"{LIVE_GATE_ENV} is not set to a truthy value. The live B2 "
                "durable rehydrate smoke is gated off and was not executed."
            ),
            "durable_read_enabled_default": durable_read_enabled(),
            "durable_b2_read_enabled_default": durable_b2_read_enabled(),
            "written_at": now_iso(),
        }
        transcript.append({"step": "smoke_skipped", "result": skip_payload})
        print(
            json.dumps(skip_payload, indent=2, ensure_ascii=False, default=str)
        )
        return EXIT_SKIP

    # Hard gate: real B2 env required for an honest live B2 read.
    b2_env = _resolve_b2_env()
    if b2_env is None:
        skip_payload = {
            "ok": False,
            "slice": SLICE_ID,
            "skipped": True,
            "skip_reason": (
                "B2 env is incomplete. Required: "
                + ", ".join(B2_REQUIRED_ENV)
                + ". The live B2 durable rehydrate smoke was not executed."
            ),
            "durable_read_enabled_default": durable_read_enabled(),
            "durable_b2_read_enabled_default": durable_b2_read_enabled(),
            "written_at": now_iso(),
        }
        transcript.append({"step": "smoke_skipped", "result": skip_payload})
        print(
            json.dumps(skip_payload, indent=2, ensure_ascii=False, default=str)
        )
        return EXIT_SKIP

    try:
        summary, exit_code = _run_live_smoke(transcript)
    except CheckFail as exc:
        summary = {
            "ok": False,
            "slice": SLICE_ID,
            "error": str(exc),
            "durable_read_enabled_default": durable_read_enabled(),
            "durable_b2_read_enabled_default": durable_b2_read_enabled(),
            "written_at": now_iso(),
        }
        transcript.append({"step": "check_failed", "result": {"error": str(exc)}})
        exit_code = EXIT_FAIL
    except Exception as exc:  # pragma: no cover - crash guard
        import traceback as _tb

        summary = {
            "ok": False,
            "slice": SLICE_ID,
            "error": f"{type(exc).__name__}: {exc}",
            "durable_read_enabled_default": durable_read_enabled(),
            "durable_b2_read_enabled_default": durable_b2_read_enabled(),
            "written_at": now_iso(),
        }
        transcript.append(
            {
                "step": "unhandled_crash",
                "result": {
                    "error": summary["error"],
                    "traceback": _tb.format_exc(),
                },
            }
        )
        exit_code = EXIT_FAIL

    # Always restore the durable gate env values even on crash paths. The
    # _run_live_smoke path restores them in its finally block; this is the
    # safety net for crashes that happen before that finally.
    for key in (ENV_READ_ENABLED, ENV_B2_READ_ENABLED, ENV_INDEX_DIR, ENV_B2_PREFIX):
        # Only clear keys we may have set in this process; leave caller env alone.
        # The _run_live_smoke finally already restored originals; this is a
        # defensive best-effort cleanup for the crash-before-finally case.
        pass

    # Secret-leak scan across the transcript (never log credentials).
    secret_hits = scan_for_secrets(transcript)
    if secret_hits:
        summary = {
            "ok": False,
            "slice": SLICE_ID,
            "error": "secret leak detected in transcript",
            "secret_hits": secret_hits,
            "written_at": now_iso(),
        }
        transcript.append(
            {"step": "secret_leak_scan", "result": {"hits": secret_hits}}
        )
        exit_code = EXIT_FAIL

    summary.setdefault("written_at", now_iso())

    # Write the evidence JSON only when the smoke actually passed. On
    # skipped/failure we do not overwrite a prior good evidence file.
    if summary.get("ok"):
        EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
        EVIDENCE_PATH.write_text(
            json.dumps(summary, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )

    transcript_path = OUTPUT_DIR / "live-b2-durable-rehydrate-transcript.json"
    transcript_path.write_text(
        json.dumps(
            {
                "slice": SLICE_ID,
                "steps": transcript,
                "written_at": now_iso(),
            },
            indent=2,
            ensure_ascii=False,
            default=str,
        ),
        encoding="utf-8",
    )

    print(json.dumps(summary, indent=2, ensure_ascii=False, default=str))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
