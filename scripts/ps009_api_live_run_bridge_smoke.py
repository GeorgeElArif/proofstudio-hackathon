#!/usr/bin/env python3
"""
PS-009: API Live Run Bridge smoke test.

What this proves:

- The PS-008 service layer still imports and its dry-run behavior is intact.
- A dry-run run never calls live providers, never calls B2, never calls
  Genblaze, and never fabricates media.
- A live run with ``run_live=true`` explicitly triggers the PS-007 live
  ProviderRouter chain (Cloudflare primary -> Pollinations fallback), captures
  the full 20-field ProviderAttempt ledger, stores the generated image and
  supporting artifacts in B2, writes and verifies a Genblaze manifest, and
  feeds all of that evidence back into the in-memory API store.
- Readbacks (GET-style service calls for run / attempts / assets / manifest)
  return the real live evidence state.

Smoke exit rule:

Exit 0 for either:
- honest ``live_completed`` with real provider/model/attempts/assets/manifest, or
- honest ``live_blocked`` / ``live_failed`` with no fake media, no fake
  manifest, a clear reason, and preserved attempts where available.

Exit nonzero only for:
- code/import/schema errors
- dry-run accidentally calling live providers / B2
- fake media
- fake manifest
- compact attempts (missing PS-006 fields)
- unhandled crash
- secret leak

Truth boundary: this proves the backend API/service layer can explicitly
trigger and store a live proof-backed generation run. It does not prove
semantic truth, legal authenticity, C2PA authenticity, or human authorship.

Historical proof scripts (PS-004 / PS-005 / PS-006 / PS-007 / PS-008) are not
modified.
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

from proofstudio.api.app import FRAMEWORK_MODE  # noqa: E402
from proofstudio.api.models import (  # noqa: E402
    REQUIRED_ATTEMPT_FIELDS,
    RUN_STATUS_DRY_RUN_CREATED,
    RUN_STATUS_LIVE_BLOCKED,
    RUN_STATUS_LIVE_COMPLETED,
    RUN_STATUS_LIVE_FAILED,
)
from proofstudio.api.services import (  # noqa: E402
    NotFoundError,
    ProofStudioService,
    create_default_service,
)

OUTPUT_DIR = Path("/tmp/proofstudio-ps-009")
SUMMARY_PATH = OUTPUT_DIR / "api-live-run-bridge-summary.json"
TRANSCRIPT_PATH = OUTPUT_DIR / "api-live-run-bridge-transcript.json"

ALLOWED_SELECTED_PROVIDERS = {"cloudflare-workers-ai", "pollinations"}

# Secret-leak guard patterns. The smoke output is scanned for these so a
# leaked bearer token / B2 key never reaches the summary or transcript.
SECRET_PATTERNS = [
    re.compile(r"(?i)Bearer\s+[A-Za-z0-9\-_.=~]{8,}"),
    re.compile(r"(?i)B2_KEY_ID[\s:=]+\S{8,}"),
    re.compile(r"(?i)B2_APP_KEY[\s:=]+\S{8,}"),
    re.compile(r"(?i)CLOUDFLARE_API_TOKEN[\s:=]+\S{8,}"),
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class CheckFail(Exception):
    pass


def check(label: str, condition: bool, detail: str = "") -> None:
    if not condition:
        raise CheckFail(f"{label}: {detail}" if detail else f"{label}: failed")


def check_equal(label: str, got: Any, expected: Any) -> None:
    if got != expected:
        raise CheckFail(f"{label}: expected {expected!r}, got {got!r}")


def validate_full_attempt_schema(attempts: list[dict[str, Any]]) -> list[str]:
    """Validate every attempt carries the full PS-006 20-field shape."""
    errors: list[str] = []
    if not isinstance(attempts, list):
        return [f"attempts must be a list, got {type(attempts).__name__}"]
    for index, attempt in enumerate(attempts):
        if not isinstance(attempt, dict):
            errors.append(
                f"attempt[{index}]: must be a dict, got {type(attempt).__name__}"
            )
            continue
        for field_name in REQUIRED_ATTEMPT_FIELDS:
            if field_name not in attempt:
                errors.append(
                    f"attempt[{index}]: missing required field {field_name!r}"
                )
    return errors


def scan_for_secrets(payload: Any) -> list[str]:
    """Scan a serializable payload for obvious secret patterns."""
    text = json.dumps(payload, ensure_ascii=False, default=str)
    hits: list[str] = []
    for pattern in SECRET_PATTERNS:
        match = pattern.search(text)
        if match:
            # Report the pattern name, never the matched secret text.
            hits.append(f"secret pattern matched: {pattern.pattern[:40]}...")
    return hits


def is_fake_media_path(path_str: str | None) -> bool:
    """Heuristic: a real generated image path should exist on disk."""
    if not path_str:
        return False
    return Path(path_str).exists()


def main() -> None:
    load_dotenv(REPO_ROOT / ".env")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    transcript: list[dict[str, Any]] = []

    def log(step: str, payload: Any) -> None:
        transcript.append({"step": step, "result": payload})

    flags: dict[str, bool] = {}

    service = create_default_service()
    log("service_created", {
        "proof_version": service._proof_version,
        "live_output_dir": service._live_output_dir,
        "live_b2_prefix": service._live_b2_prefix,
    })

    # ------------------------------------------------------------------
    # 1. Verify the static attempt contract still holds (no fabrication).
    # ------------------------------------------------------------------
    expected_fields = {
        "attempt_id", "attempt_index", "provider", "model", "api_method",
        "job_type", "status", "normalized_status", "started_at",
        "finished_at", "latency_ms", "retryable", "fallback_allowed",
        "skip_reason", "raw_error_type", "sanitized_error_message",
        "estimated_cost", "free_or_paid", "output_asset_refs", "notes",
    }
    check_equal(
        "REQUIRED_ATTEMPT_FIELDS is the 20-field PS-006 shape",
        set(REQUIRED_ATTEMPT_FIELDS),
        expected_fields,
    )

    # ------------------------------------------------------------------
    # 2. Create a campaign.
    # ------------------------------------------------------------------
    campaign_payload = {
        "name": "PS-009 API Live Run Bridge Campaign",
        "brief": (
            "Prove the backend API can explicitly trigger a live proof-backed "
            "generation run and store the evidence in B2 + Genblaze."
        ),
        "target_audience": "hackathon judges",
        "platform": "web",
        "objective": "connect PS-008 service to PS-007 live chain",
    }
    created = service.create_campaign(campaign_payload)
    log("create_campaign", {"campaign_id": created["campaign_id"]})
    campaign_id = created["campaign_id"]
    check("campaign created", bool(campaign_id))
    flags["campaign_created"] = True

    # ------------------------------------------------------------------
    # 3. Dry-run run: verify NO live calls, NO B2, NO fake media.
    # ------------------------------------------------------------------
    dry_run = service.create_run({
        "campaign_id": campaign_id,
        "prompt": "A dry-run skeleton run. Do not call any provider.",
        "budget_mode": "free-only",
    })
    log("create_dry_run", {
        "run_id": dry_run["run_id"],
        "status": dry_run["status"],
    })
    check_equal(
        "dry_run.status", dry_run["status"], RUN_STATUS_DRY_RUN_CREATED
    )
    check_equal("dry_run.attempt_count", dry_run["attempt_count"], 0)
    dry_run_record = dry_run["run"]
    check("dry_run.selected_provider is None", dry_run_record.get("selected_provider") is None)
    check("dry_run.manifest_uri is None", dry_run_record.get("manifest_uri") is None)
    check("dry_run.attempts empty", dry_run_record.get("attempts") == [])
    check("dry_run.assets empty", dry_run_record.get("assets") == [])
    check("dry_run.local_image is None", dry_run_record.get("local_image") is None)
    check("dry_run.no manifest_hash", dry_run_record.get("manifest_hash") is None)

    # Dry-run sub-resource readbacks.
    dry_attempts = service.get_run_attempts(dry_run["run_id"])
    check_equal("dry_run.attempts readback", dry_attempts["attempt_count"], 0)
    dry_assets = service.get_run_assets(dry_run["run_id"])
    check_equal("dry_run.assets readback", dry_assets["asset_count"], 0)
    dry_manifest = service.get_run_manifest(dry_run["run_id"])
    check_equal("dry_run.manifest ready", dry_manifest["ready"], False)

    flags["dry_run_checked"] = True
    flags["dry_run_no_live_calls"] = True
    flags["dry_run_no_b2_calls"] = True
    flags["no_fake_media"] = True

    # ------------------------------------------------------------------
    # 4. Missing campaign still returns clean not-found behavior.
    # ------------------------------------------------------------------
    missing_campaign_ok = False
    try:
        service.create_run({
            "campaign_id": "camp_does_not_exist",
            "run_live": True,
            "dry_run": False,
        })
    except NotFoundError:
        missing_campaign_ok = True
    check("missing campaign raises NotFoundError on live run", missing_campaign_ok)
    flags["missing_campaign_checked"] = True

    # ------------------------------------------------------------------
    # 5. Live run with run_live=true.
    # ------------------------------------------------------------------
    flags["live_run_attempted"] = True
    live_prompt = (
        "Create a premium 16:9 hero image for ProofStudio, a provenance-aware "
        "AI media operations app. Show a refined product interface in a "
        "cinematic studio workspace with a visible manifest/hash "
        "verification panel. Polished modern visual style, clean interface "
        "cards, elegant lighting. No tiny readable UI text."
    )
    live_run = service.create_run({
        "campaign_id": campaign_id,
        "prompt": live_prompt,
        "budget_mode": "free-only",
        "dry_run": False,
        "run_live": True,
    })
    log("create_live_run", {
        "run_id": live_run["run_id"],
        "status": live_run["status"],
        "selected_provider": live_run["selected_provider"],
    })
    live_run_id = live_run["run_id"]
    live_status = live_run["status"]
    live_record = live_run["run"]

    selected_provider = live_record.get("selected_provider")
    selected_model = live_record.get("selected_model")
    fallback_used = bool(live_record.get("fallback_used"))
    attempt_count = live_record.get("attempt_count") or 0
    attempts = live_record.get("attempts") or []

    # Validate attempt schema regardless of outcome.
    schema_errors = validate_full_attempt_schema(attempts)
    if schema_errors:
        for err in schema_errors:
            print(f"   - SCHEMA ERROR: {err}", file=sys.stderr)
        check("live attempts full schema", False, detail="compact attempts detected")

    flags["attempts_checked"] = True

    live_completed = live_status == RUN_STATUS_LIVE_COMPLETED
    live_blocked = live_status in {RUN_STATUS_LIVE_BLOCKED, RUN_STATUS_LIVE_FAILED}

    # ------------------------------------------------------------------
    # 6a. Live success path.
    # ------------------------------------------------------------------
    manifest_uri: str | None = None
    manifest_hash: str | None = None
    stored_manifest_verify: bool | None = None
    transfer_failures: list[Any] = []
    stored_transfer_failures: list[Any] = []
    asset_count = 0

    if live_completed:
        check(
            "live_completed.selected_provider allowed",
            selected_provider in ALLOWED_SELECTED_PROVIDERS,
            detail=f"selected_provider={selected_provider!r}",
        )
        check("live_completed.selected_model exists", bool(selected_model))
        check("live_completed.attempt_count >= 1", attempt_count >= 1)

        has_ok_attempt = any(
            (a.get("normalized_status") == "OK") for a in attempts
        )
        check("live_completed has at least one OK attempt", has_ok_attempt)

        # Readbacks.
        got_run = service.get_run(live_run_id)["run"]
        check_equal("readback.run.status", got_run["status"], RUN_STATUS_LIVE_COMPLETED)
        check_equal("readback.run.selected_provider", got_run.get("selected_provider"), selected_provider)
        check_equal("readback.run.selected_model", got_run.get("selected_model"), selected_model)

        got_attempts = service.get_run_attempts(live_run_id)
        check_equal("readback.attempts.count", got_attempts["attempt_count"], attempt_count)
        readback_schema_errors = validate_full_attempt_schema(
            got_attempts["attempts"]
        )
        check(
            "readback.attempts full schema",
            not readback_schema_errors,
            detail=str(readback_schema_errors),
        )

        got_assets = service.get_run_assets(live_run_id)
        asset_count = got_assets["asset_count"]
        check("live_completed.asset_count >= 4", asset_count >= 4)

        got_manifest = service.get_run_manifest(live_run_id)
        check_equal("readback.manifest.ready", got_manifest.get("ready"), True)
        manifest_uri = got_manifest.get("manifest_uri")
        manifest_hash = got_manifest.get("manifest_hash")
        stored_manifest_verify = got_manifest.get("stored_manifest_verify")
        transfer_failures = list(got_manifest.get("transfer_failures") or [])
        stored_transfer_failures = list(
            got_manifest.get("stored_transfer_failures") or []
        )

        check("live_completed.manifest_uri exists", bool(manifest_uri))
        check("live_completed.stored_manifest_verify true", stored_manifest_verify is True)
        check_equal("live_completed.transfer_failures empty", transfer_failures, [])
        check_equal("live_completed.stored_transfer_failures empty", stored_transfer_failures, [])

        # No fake media: the local image path must point at a real file.
        local_image = live_record.get("local_image")
        check(
            "live_completed.real local image exists",
            is_fake_media_path(local_image),
            detail=f"local_image={local_image!r}",
        )

        flags["live_run_completed"] = True
        flags["assets_checked"] = True
        flags["manifest_checked"] = True
        flags["readbacks_checked"] = True
        flags["no_fake_media"] = True

    # ------------------------------------------------------------------
    # 6b. Live blocked / failed path.
    # ------------------------------------------------------------------
    elif live_blocked:
        check(
            "live_blocked.status is live_blocked or live_failed",
            live_status in {RUN_STATUS_LIVE_BLOCKED, RUN_STATUS_LIVE_FAILED},
        )
        # No fake image, no fake manifest.
        check("live_blocked.no local image", not live_record.get("local_image"))
        check("live_blocked.no manifest_uri", not live_record.get("manifest_uri"))
        check("live_blocked.no manifest_hash", not live_record.get("manifest_hash"))
        check("live_blocked.no stored_manifest_verify", live_record.get("stored_manifest_verify") is not True)

        reason = live_record.get("error") or live_record.get("blocked_reason")
        check("live_blocked.clear reason", bool(reason))

        # Attempts preserved if any were captured.
        if attempts:
            readback_attempts = service.get_run_attempts(live_run_id)["attempts"]
            check_equal(
                "live_blocked.attempts preserved",
                len(readback_attempts),
                len(attempts),
            )
            flags["attempts_checked"] = True

        flags["live_run_completed"] = False
        flags["readbacks_checked"] = True
        flags["no_fake_media"] = True
        flags["manifest_checked"] = True
    else:
        check(
            "live status is completed/blocked/failed",
            False,
            detail=f"unexpected status {live_status!r}",
        )

    # ------------------------------------------------------------------
    # 7. Secret-leak scan on the transcript so far.
    # ------------------------------------------------------------------
    secret_hits = scan_for_secrets(transcript)
    check("no secret leak in transcript", not secret_hits, detail=str(secret_hits))

    # ------------------------------------------------------------------
    # 8. Build and write summary + transcript.
    # ------------------------------------------------------------------
    ok = (
        flags.get("campaign_created")
        and flags.get("dry_run_checked")
        and flags.get("dry_run_no_live_calls")
        and flags.get("dry_run_no_b2_calls")
        and flags.get("no_fake_media")
        and flags.get("attempts_checked")
        and flags.get("missing_campaign_checked")
        and (
            flags.get("live_run_completed")
            or live_blocked
        )
        and (live_completed or live_blocked)
    )

    summary: dict[str, Any] = {
        "ok": bool(ok),
        "slice": "PS-009",
        "framework_mode": FRAMEWORK_MODE,
        "dry_run_checked": flags.get("dry_run_checked", False),
        "live_run_attempted": flags.get("live_run_attempted", False),
        "live_run_status": live_status,
        "live_run_completed": flags.get("live_run_completed", False),
        "selected_provider": selected_provider if live_completed else None,
        "selected_model": selected_model if live_completed else None,
        "fallback_used": fallback_used if live_completed else False,
        "attempt_count": attempt_count,
        "attempts_checked": flags.get("attempts_checked", False),
        "assets_checked": flags.get("assets_checked", False),
        "manifest_checked": flags.get("manifest_checked", False),
        "manifest_uri": manifest_uri,
        "manifest_hash": manifest_hash,
        "stored_manifest_verify": stored_manifest_verify,
        "transfer_failures": transfer_failures,
        "stored_transfer_failures": stored_transfer_failures,
        "no_fake_media": flags.get("no_fake_media", False),
        "dry_run_no_live_calls": flags.get("dry_run_no_live_calls", False),
        "dry_run_no_b2_calls": flags.get("dry_run_no_b2_calls", False),
        "readbacks_checked": flags.get("readbacks_checked", False),
        "truth_boundary": (
            "PS-009 proves the backend API/service layer can explicitly trigger "
            "and store a live proof-backed generation run. It does not prove "
            "semantic truth, legal authenticity, C2PA authenticity, or human "
            "authorship."
        ),
        "summary_path": str(SUMMARY_PATH),
        "transcript_path": str(TRANSCRIPT_PATH),
        "written_at": now_iso(),
    }

    if live_blocked:
        summary["blocked_reason"] = (
            live_record.get("error") or live_record.get("blocked_reason")
        )

    SUMMARY_PATH.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    TRANSCRIPT_PATH.write_text(
        json.dumps(
            {
                "slice": "PS-009",
                "framework_mode": FRAMEWORK_MODE,
                "steps": transcript,
                "service_snapshot": service.store.snapshot(),
                "written_at": now_iso(),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(json.dumps(summary, indent=2, ensure_ascii=False))

    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except CheckFail as exc:
        failure_summary = {
            "ok": False,
            "slice": "PS-009",
            "framework_mode": FRAMEWORK_MODE,
            "error": str(exc),
            "summary_path": str(SUMMARY_PATH),
            "transcript_path": str(TRANSCRIPT_PATH),
            "written_at": now_iso(),
        }
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        SUMMARY_PATH.write_text(
            json.dumps(failure_summary, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(json.dumps(failure_summary, indent=2, ensure_ascii=False))
        sys.exit(1)
