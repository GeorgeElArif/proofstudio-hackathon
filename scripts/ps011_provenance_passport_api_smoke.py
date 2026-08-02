#!/usr/bin/env python3
"""
PS-011: Review Room / Provenance Passport API smoke test.

What this proves:

- A Provenance Passport object can be built for a run from normal service
  readbacks (get_run / get_run_attempts / get_run_assets / get_run_manifest).
- The passport is built from a PS-010-style REHYDRATED service/store, which
  proves the passport works after durable recovery (memory loss + rehydrate).
- The passport carries all required sections: passport_identity, run_summary,
  campaign_snapshot, generation_summary, attempt_timeline, raw_attempts,
  assets, manifest_verification, archive_and_rehydration, trust_boundary,
  review_room_summary.
- raw_attempts use the full PS-006 20-field shape (never compact).
- The attempt_timeline is derived from the full attempts and stays in sync.
- The trust boundary includes both claims and non_claims, and the non_claims
  always cover semantic_truth / legal_authenticity / c2pa_authenticity /
  human_authorship / final_production_security.
- No live provider is called during passport generation itself.
- No fake media is created during passport generation.
- No manifest verification or archive proof is fabricated.

Smoke exit rule:

Exit 0 for either:
- honest live_completed run -> archive -> rehydrate -> passport created and
  validated, or
- honest live blocked/failed run -> passport still created but clearly reflects
  the blocked/no-media state (no fake success, no fake media).

Exit nonzero for:
- provider call during passport generation
- compact raw attempts
- fake manifest verification
- fake archive/rehydration proof
- fake media
- missing trust boundary / missing non_claims
- unhandled crash
- secret leak
- historical proof script modifications

Truth boundary: PS-011 proves ProofStudio can transform stored run evidence
into a structured Review Room / Provenance Passport object. It does not prove
semantic truth, legal authenticity, C2PA authenticity, human authorship, final
production security, or production persistence.

Historical proof scripts (PS-004 / PS-005 / PS-006 / PS-007 / PS-008 / PS-009 /
PS-010) are not modified.
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
from proofstudio.api.app import FRAMEWORK_MODE  # noqa: E402
from proofstudio.api.archive import (  # noqa: E402
    ARCHIVE_SCHEMA_VERSION,
    ARCHIVE_STORAGE_MODE_B2,
    ARCHIVE_STORAGE_MODE_LOCAL,
    build_run_archive,
    read_archive_from_b2,
    rehydrate_run_from_archive,
    store_run_archive_with_genblaze,
    validate_archive,
    write_run_archive_local,
)
from proofstudio.api.live_bridge import B2_REQUIRED_ENV  # noqa: E402
from proofstudio.api.models import (  # noqa: E402
    REQUIRED_ATTEMPT_FIELDS,
    RUN_STATUS_LIVE_BLOCKED,
    RUN_STATUS_LIVE_COMPLETED,
    RUN_STATUS_LIVE_FAILED,
)
from proofstudio.api.passport import (  # noqa: E402
    ARCHIVE_NOT_AVAILABLE,
    PASSPORT_NON_CLAIMS,
    PASSPORT_SCHEMA_VERSION,
    PASSPORT_TRUTH_BOUNDARY,
    SOURCE_ARCHIVE_REHYDRATED_RUN,
    SOURCE_LIVE_RUN,
    build_provenance_passport,
    validate_provenance_passport,
    write_passport_local,
)
from proofstudio.api.services import (  # noqa: E402
    ProofStudioService,
    create_default_service,
)

OUTPUT_DIR = Path("/tmp/proofstudio-ps-011")
LIVE_OUTPUT_DIR = OUTPUT_DIR / "live-run"
PASSPORT_PATH = OUTPUT_DIR / "provenance-passport.json"
SUMMARY_PATH = OUTPUT_DIR / "provenance-passport-summary.json"
TRANSCRIPT_PATH = OUTPUT_DIR / "provenance-passport-transcript.json"

ALLOWED_SELECTED_PROVIDERS = {"cloudflare-workers-ai", "pollinations"}
PS011_B2_PREFIX = "proofstudio/ps-011"

# Historical proof scripts that must never be modified by this slice.
HISTORICAL_SCRIPTS = (
    "scripts/ps004_provider_router_cloudflare_smoke.py",
    "scripts/ps005_pollinations_fallback_smoke.py",
    "scripts/ps006_provider_router_core_smoke.py",
    "scripts/ps007_live_provider_router_chain_smoke.py",
    "scripts/ps008_backend_api_smoke.py",
    "scripts/ps009_api_live_run_bridge_smoke.py",
    "scripts/ps010_run_archive_rehydrate_b2_smoke.py",
)

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
    errors: list[str] = []
    if not isinstance(attempts, list):
        return [f"attempts must be a list, got {type(attempts).__name__}"]
    for index, attempt in enumerate(attempts):
        if not isinstance(attempt, dict):
            errors.append(f"attempt[{index}]: not a dict")
            continue
        for field_name in REQUIRED_ATTEMPT_FIELDS:
            if field_name not in attempt:
                errors.append(
                    f"attempt[{index}]: missing required field {field_name!r}"
                )
    return errors


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


def historical_scripts_untouched() -> list[str]:
    """Return a list of historical scripts that git sees as modified.

    Empty list means all historical proof scripts are untouched.
    """
    import subprocess

    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "--", *HISTORICAL_SCRIPTS],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=5.0,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    modified: list[str] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        # Format: "XY path". Take the path portion.
        parts = line.split(None, 1)
        if len(parts) == 2:
            modified.append(parts[1])
    return modified


def _resolve_b2_env() -> dict[str, str] | None:
    missing = [name for name in B2_REQUIRED_ENV if not os.getenv(name)]
    if missing:
        return None
    return {name: os.environ[name] for name in B2_REQUIRED_ENV}


def main() -> None:
    load_dotenv(REPO_ROOT / ".env")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    transcript: list[dict[str, Any]] = []

    def log(step: str, payload: Any) -> None:
        transcript.append({"step": step, "result": payload})

    summary: dict[str, Any] = {
        "ok": False,
        "slice": "PS-011",
        "framework_mode": FRAMEWORK_MODE,
        "live_run_attempted": False,
        "live_run_status": None,
        "live_run_completed": False,
        "rehydrate_used": False,
        "passport_created": False,
        "passport_validated": False,
        "passport_source": None,
        "passport_path": str(PASSPORT_PATH),
        "run_id": None,
        "campaign_id": None,
        "selected_provider": None,
        "selected_model": None,
        "fallback_used": False,
        "attempt_count": 0,
        "timeline_entries": 0,
        "asset_count": 0,
        "manifest_uri": None,
        "manifest_hash": None,
        "stored_manifest_verify": None,
        "archive_uri": None,
        "archive_sha256": None,
        "rehydrate_source": None,
        "trust_boundary_checked": False,
        "non_claims_checked": False,
        "no_provider_call_during_passport": False,
        "no_fake_media": False,
        "summary_path": str(SUMMARY_PATH),
        "transcript_path": str(TRANSCRIPT_PATH),
        "truth_boundary": PASSPORT_TRUTH_BOUNDARY,
    }

    b2_env = _resolve_b2_env()
    log("env", {
        "b2_available": b2_env is not None,
        "framework_mode": FRAMEWORK_MODE,
        "passport_schema_version": PASSPORT_SCHEMA_VERSION,
    })

    fresh_service: ProofStudioService | None = None

    try:
        # ------------------------------------------------------------------
        # 0. Historical proof scripts must be untouched.
        # ------------------------------------------------------------------
        modified = historical_scripts_untouched()
        check(
            "historical proof scripts untouched",
            not modified,
            detail=f"modified historical scripts: {modified}",
        )
        log("historical_scripts_check", {"modified": modified})

        # ------------------------------------------------------------------
        # 1. Static contract checks.
        # ------------------------------------------------------------------
        expected_attempt_fields = {
            "attempt_id", "attempt_index", "provider", "model", "api_method",
            "job_type", "status", "normalized_status", "started_at",
            "finished_at", "latency_ms", "retryable", "fallback_allowed",
            "skip_reason", "raw_error_type", "sanitized_error_message",
            "estimated_cost", "free_or_paid", "output_asset_refs", "notes",
        }
        check_equal(
            "REQUIRED_ATTEMPT_FIELDS 20-field shape",
            set(REQUIRED_ATTEMPT_FIELDS),
            expected_attempt_fields,
        )
        check_equal(
            "PASSPORT_SCHEMA_VERSION set",
            PASSPORT_SCHEMA_VERSION,
            "ps-011.1",
        )
        check_equal(
            "ARCHIVE_SCHEMA_VERSION set",
            ARCHIVE_SCHEMA_VERSION,
            "ps-010.1",
        )
        required_non_claims = {
            "semantic_truth",
            "legal_authenticity",
            "c2pa_authenticity",
            "human_authorship",
            "final_production_security",
        }
        check(
            "PASSPORT_NON_CLAIMS covers all required non-claims",
            required_non_claims.issubset(set(PASSPORT_NON_CLAIMS)),
            detail=str(PASSPORT_NON_CLAIMS),
        )

        # ------------------------------------------------------------------
        # 2. Create service + campaign.
        # ------------------------------------------------------------------
        service = ProofStudioService(
            live_output_dir=str(LIVE_OUTPUT_DIR),
            live_b2_prefix=PS011_B2_PREFIX,
        )
        campaign_payload = {
            "name": "PS-011 Provenance Passport Review Room Campaign",
            "brief": (
                "Prove a Provenance Passport can be assembled from a "
                "rehydrated run and presented for review without rerunning "
                "providers or fabricating media/manifests."
            ),
            "target_audience": "hackathon judges and reviewers",
            "platform": "web",
            "objective": "explain stored evidence in one review artifact",
        }
        created = service.create_campaign(campaign_payload)
        campaign_id = created["campaign_id"]
        check("campaign created", bool(campaign_id))
        summary["campaign_id"] = campaign_id
        log("create_campaign", {"campaign_id": campaign_id})

        # ------------------------------------------------------------------
        # 3. Live run with run_live=true.
        # ------------------------------------------------------------------
        summary["live_run_attempted"] = True
        live_prompt = (
            "Create a premium 16:9 hero image for ProofStudio, a provenance-aware "
            "AI media operations platform. Show a clean review-room dashboard with "
            "a visible provenance passport panel listing provider, model, attempt "
            "timeline, asset hashes, and manifest verification. Cinematic studio "
            "lighting, polished modern interface cards. No tiny readable UI text."
        )
        live_run = service.create_run({
            "campaign_id": campaign_id,
            "prompt": live_prompt,
            "budget_mode": "free-only",
            "dry_run": False,
            "run_live": True,
        })
        live_run_id = live_run["run_id"]
        live_status = live_run["status"]
        live_record = live_run["run"]
        selected_provider = live_record.get("selected_provider")
        selected_model = live_record.get("selected_model")
        fallback_used = bool(live_record.get("fallback_used"))
        attempts = live_record.get("attempts") or []
        attempt_count = live_record.get("attempt_count") or 0

        summary["run_id"] = live_run_id
        summary["live_run_status"] = live_status
        summary["selected_provider"] = selected_provider
        summary["selected_model"] = selected_model
        summary["fallback_used"] = fallback_used
        summary["attempt_count"] = attempt_count

        log("create_live_run", {
            "run_id": live_run_id,
            "status": live_status,
            "selected_provider": selected_provider,
            "selected_model": selected_model,
            "attempt_count": attempt_count,
        })

        live_completed = live_status == RUN_STATUS_LIVE_COMPLETED
        live_blocked = live_status in {RUN_STATUS_LIVE_BLOCKED, RUN_STATUS_LIVE_FAILED}
        summary["live_run_completed"] = live_completed

        # Attempts must always be full PS-006 records regardless of outcome.
        schema_errors = validate_full_attempt_schema(attempts)
        if schema_errors:
            for err in schema_errors:
                print(f"   - SCHEMA ERROR: {err}", file=sys.stderr)
            check("live attempts full schema", False, detail="compact attempts detected")

        manifest_uri: str | None = None
        manifest_hash: str | None = None
        stored_manifest_verify: bool | None = None
        asset_count = 0

        if live_completed:
            check(
                "live_completed.selected_provider allowed",
                selected_provider in ALLOWED_SELECTED_PROVIDERS,
                detail=f"selected_provider={selected_provider!r}",
            )
            check("live_completed.selected_model exists", bool(selected_model))
            got_manifest = service.get_run_manifest(live_run_id)
            manifest_uri = got_manifest.get("manifest_uri")
            manifest_hash = got_manifest.get("manifest_hash")
            stored_manifest_verify = got_manifest.get("stored_manifest_verify")
            check("live_completed.manifest_uri exists", bool(manifest_uri))
            check(
                "live_completed.stored_manifest_verify true",
                stored_manifest_verify is True,
            )
            asset_count = service.get_run_assets(live_run_id)["asset_count"]
            check("live_completed.asset_count >= 1", asset_count >= 1)
            summary["manifest_uri"] = manifest_uri
            summary["manifest_hash"] = manifest_hash
            summary["stored_manifest_verify"] = stored_manifest_verify
            summary["asset_count"] = asset_count
        elif live_blocked:
            reason = live_record.get("error") or live_record.get("blocked_reason")
            check("live_blocked.clear reason", bool(reason))
            check("live_blocked.no local image", not live_record.get("local_image"))
            check("live_blocked.no manifest_uri", not live_record.get("manifest_uri"))
            check(
                "live_blocked.no stored_manifest_verify",
                live_record.get("stored_manifest_verify") is not True,
            )
            summary["blocked_reason"] = reason
        else:
            check(
                "live status is completed/blocked/failed",
                False,
                detail=f"unexpected status {live_status!r}",
            )

        log("live_run_outcome", {
            "live_completed": live_completed,
            "live_blocked": live_blocked,
            "manifest_uri": manifest_uri,
            "asset_count": asset_count,
        })

        # ------------------------------------------------------------------
        # 4. PS-010-style archive + rehydrate (preferred for PS-011 so the
        #    passport is proven against durable recovery).
        # ------------------------------------------------------------------
        archive = build_run_archive(service, live_run_id)
        archive_errors = validate_archive(archive)
        check(
            "archive validates (schema + required fields + full attempts)",
            not archive_errors,
            detail=str(archive_errors),
        )
        check_equal(
            "archive attempts full schema on read",
            validate_full_attempt_schema(archive["attempts"]),
            [],
        )
        local_archive_path = write_run_archive_local(
            archive,
            OUTPUT_DIR / f"proofstudio-run-archive-{live_run_id}.json",
        )
        log("build_run_archive", {
            "local_path": str(local_archive_path),
            "attempt_count": archive["attempt_count"],
        })

        archive_uri: str | None = None
        archive_sha256: str | None = None
        archive_storage_mode: str | None = None
        archive_stored = False

        if b2_env is not None:
            try:
                stored = store_run_archive_with_genblaze(
                    archive,
                    b2_env=b2_env,
                    b2_prefix=PS011_B2_PREFIX,
                    local_path=local_archive_path,
                )
                archive_uri = stored["archive_uri"]
                archive_sha256 = stored["archive_sha256"]
                archive_stored = True
                log("store_run_archive_with_genblaze", {
                    "archive_uri": archive_uri,
                    "archive_sha256": archive_sha256,
                })
            except Exception as exc:
                archive_stored = False
                log("store_run_archive_failed", {
                    "error": f"{type(exc).__name__}: {exc}",
                })
        else:
            log("store_run_archive_skipped", {"reason": "B2 env not available"})

        # Fresh service/store to simulate memory loss.
        fresh_service = create_default_service()
        check(
            "fresh store is empty of the run",
            not fresh_service.store.has_run(live_run_id),
        )

        rehydrate_source: str
        rehydrate_archive: dict[str, Any]

        if archive_stored and archive_uri:
            try:
                rehydrate_archive = read_archive_from_b2(
                    archive_uri, b2_env=b2_env, b2_prefix=PS011_B2_PREFIX
                )
                check_equal(
                    "b2 archive run_id matches",
                    rehydrate_archive.get("run_id"),
                    live_run_id,
                )
                rehydrate_source = "b2"
                archive_storage_mode = ARCHIVE_STORAGE_MODE_B2
            except Exception as exc:
                rehydrate_archive = archive
                rehydrate_source = "local"
                archive_storage_mode = ARCHIVE_STORAGE_MODE_LOCAL
                log("read_archive_from_b2_failed_local_fallback", {
                    "error": f"{type(exc).__name__}: {exc}",
                })
        else:
            rehydrate_archive = archive
            rehydrate_source = "local"
            archive_storage_mode = "local_only"
            log("rehydrate_from_local", {
                "note": "B2 storage unavailable; local-only rehydrate.",
            })

        rehydrate_result = rehydrate_run_from_archive(
            fresh_service, rehydrate_archive, source_kind="inline"
        )
        check("rehydrate ok", rehydrate_result["ok"] is True)
        check_equal(
            "rehydrate provider_calls_made == 0",
            rehydrate_result["provider_calls_made"],
            0,
        )
        summary["rehydrate_used"] = True
        summary["rehydrate_source"] = rehydrate_source
        log("rehydrate_run_from_archive", {
            "rehydrate_source": rehydrate_source,
            "restored_run_id": rehydrate_result["restored_run_id"],
            "restored_attempt_count": rehydrate_result["restored_attempt_count"],
            "restored_asset_count": rehydrate_result["restored_asset_count"],
            "restored_manifest_uri": rehydrate_result.get("restored_manifest_uri"),
        })

        # Confirm restored readbacks carry the same full attempt shape.
        restored_attempts = fresh_service.get_run_attempts(live_run_id)["attempts"]
        check_equal(
            "restored attempts full schema",
            validate_full_attempt_schema(restored_attempts),
            [],
        )
        restored_assets = fresh_service.get_run_assets(live_run_id)["assets"]
        if live_completed:
            restored_manifest = fresh_service.get_run_manifest(live_run_id)
            check_equal(
                "restored manifest_uri matches",
                restored_manifest.get("manifest_uri"),
                manifest_uri,
            )
            check_equal(
                "restored manifest_hash matches",
                restored_manifest.get("manifest_hash"),
                manifest_hash,
            )

        # ------------------------------------------------------------------
        # 5. Build the passport from the REHYDRATED service/store, with the
        #    PS-010 archive evidence attached. No provider must be called and
        #    no media must be written during this step.
        # ------------------------------------------------------------------
        archive_evidence = {
            "archive_uri": archive_uri,
            "archive_sha256": archive_sha256,
            "archive_storage_mode": archive_storage_mode,
            "rehydrate_source": rehydrate_source,
            "rehydrate_completed": True,
            "restored_manifest_uri": rehydrate_result.get("restored_manifest_uri"),
            "restored_manifest_hash": rehydrate_result.get("restored_manifest_hash"),
            "no_live_provider_call_during_rehydrate": True,
        }

        provider_call_counter = {"count": 0}

        def _live_sentinel(**kwargs: Any) -> dict[str, Any]:
            provider_call_counter["count"] += 1
            raise AssertionError(
                "LIVE PROVIDER WAS CALLED DURING PS-011 PASSPORT GENERATION"
            )

        original_execute_live_run = services_module.execute_live_run
        services_module.execute_live_run = _live_sentinel  # type: ignore[assignment]
        files_before_passport = snapshot_files(OUTPUT_DIR)
        try:
            passport = fresh_service.get_run_passport(
                live_run_id,
                archive_evidence=archive_evidence,
                source=SOURCE_ARCHIVE_REHYDRATED_RUN,
            )
        finally:
            services_module.execute_live_run = original_execute_live_run  # type: ignore[assignment]
        files_after_passport = snapshot_files(OUTPUT_DIR)
        new_files = files_after_passport - files_before_passport

        summary["no_provider_call_during_passport"] = (
            provider_call_counter["count"] == 0
        )
        summary["no_fake_media"] = new_files == set()
        check_equal(
            "no provider call during passport generation",
            provider_call_counter["count"],
            0,
        )
        check(
            "no fake media written during passport generation",
            new_files == set(),
            detail=f"new files: {sorted(new_files)}",
        )

        summary["passport_created"] = True
        summary["passport_source"] = passport["passport_identity"]["source"]
        summary["timeline_entries"] = len(passport["attempt_timeline"])

        log("passport_built", {
            "passport_id": passport["passport_identity"]["passport_id"],
            "source": passport["passport_identity"]["source"],
            "sections": sorted(passport.keys()),
            "timeline_entries": len(passport["attempt_timeline"]),
            "raw_attempts": len(passport["raw_attempts"]),
            "assets": len(passport["assets"]),
        })

        # ------------------------------------------------------------------
        # 6. Validate the full passport schema.
        # ------------------------------------------------------------------
        validation_errors = validate_provenance_passport(passport)
        check(
            "passport schema validates",
            not validation_errors,
            detail=str(validation_errors),
        )
        summary["passport_validated"] = True

        # ------------------------------------------------------------------
        # 7. Validate the attempt timeline is derived from full attempts.
        # ------------------------------------------------------------------
        check_equal(
            "timeline length equals raw attempts length",
            len(passport["attempt_timeline"]),
            len(passport["raw_attempts"]),
        )
        for index, entry in enumerate(passport["attempt_timeline"]):
            for field_name in (
                "attempt_index", "provider", "model", "api_method", "status",
                "normalized_status", "latency_ms", "retryable",
                "fallback_allowed", "skip_reason", "sanitized_error_message",
                "output_asset_refs",
            ):
                check(
                    f"timeline[{index}] has {field_name}",
                    field_name in entry,
                )
            raw = passport["raw_attempts"][index]
            check_equal(
                f"timeline[{index}] provider matches raw",
                entry["provider"],
                raw["provider"],
            )
            check_equal(
                f"timeline[{index}] normalized_status matches raw",
                entry["normalized_status"],
                raw["normalized_status"],
            )

        # ------------------------------------------------------------------
        # 8. Validate raw attempts have the full 20-field shape.
        # ------------------------------------------------------------------
        check_equal(
            "raw attempts full 20-field shape",
            validate_full_attempt_schema(passport["raw_attempts"]),
            [],
        )

        # ------------------------------------------------------------------
        # 9. Validate manifest verification section.
        # ------------------------------------------------------------------
        mv = passport["manifest_verification"]
        for field_name in (
            "manifest_uri", "manifest_hash", "in_memory_manifest_verify",
            "stored_manifest_verify", "transfer_failures",
            "stored_transfer_failures",
        ):
            check(f"manifest_verification has {field_name}", field_name in mv)
        if live_completed:
            check_equal(
                "passport manifest_uri matches run",
                mv["manifest_uri"],
                manifest_uri,
            )
            check_equal(
                "passport manifest_hash matches run",
                mv["manifest_hash"],
                manifest_hash,
            )
            check_equal(
                "passport stored_manifest_verify true",
                mv["stored_manifest_verify"],
                True,
            )
            check_equal("passport transfer_failures empty", mv["transfer_failures"], [])
            check_equal(
                "passport stored_transfer_failures empty",
                mv["stored_transfer_failures"],
                [],
            )
        else:
            # Honest blocked: no fabricated manifest verification.
            check(
                "blocked passport no fake stored_manifest_verify",
                mv["stored_manifest_verify"] is not True,
            )
            check(
                "blocked passport no fake manifest_uri",
                not mv["manifest_uri"],
            )

        # ------------------------------------------------------------------
        # 10. Validate archive/rehydration section.
        # ------------------------------------------------------------------
        archive_section = passport["archive_and_rehydration"]
        check_equal(
            "archive_and_rehydration status available",
            archive_section["status"],
            "available",
        )
        check_equal(
            "archive_and_rehydration rehydrate_completed",
            archive_section["rehydrate_completed"],
            True,
        )
        check_equal(
            "archive_and_rehydration no_live_provider_call",
            archive_section["no_live_provider_call_during_rehydrate"],
            True,
        )
        if archive_uri:
            check_equal(
                "passport archive_uri matches",
                archive_section["archive_uri"],
                archive_uri,
            )
            check_equal(
                "passport archive_sha256 matches",
                archive_section["archive_sha256"],
                archive_sha256,
            )
        summary["archive_uri"] = archive_section.get("archive_uri") or archive_uri
        summary["archive_sha256"] = (
            archive_section.get("archive_sha256") or archive_sha256
        )

        # ------------------------------------------------------------------
        # 11. Validate trust boundary / non-claims.
        # ------------------------------------------------------------------
        trust = passport["trust_boundary"]
        check("trust_boundary has claims", isinstance(trust.get("claims"), list))
        check(
            "trust_boundary has non_claims",
            isinstance(trust.get("non_claims"), list),
        )
        for required in (
            "semantic_truth",
            "legal_authenticity",
            "c2pa_authenticity",
            "human_authorship",
            "final_production_security",
        ):
            check(
                f"trust_boundary non_claim {required} present",
                required in trust["non_claims"],
            )
        # No non-claim must ever be asserted as a positive claim.
        positive_claim_forbidden = set(trust["non_claims"])
        check(
            "trust_boundary claims do not assert forbidden truths",
            not (set(trust["claims"]) & positive_claim_forbidden),
        )
        summary["trust_boundary_checked"] = True
        summary["non_claims_checked"] = True

        # ------------------------------------------------------------------
        # 12. Write the three required output artifacts.
        # ------------------------------------------------------------------
        write_passport_local(passport, PASSPORT_PATH)
        log("write_passport_local", {"path": str(PASSPORT_PATH)})

        # Review-room-friendly subset for the summary.
        review_room = passport["review_room_summary"]
        passport_digest = {
            "passport_id": passport["passport_identity"]["passport_id"],
            "passport_schema_version": PASSPORT_SCHEMA_VERSION,
            "run_id": live_run_id,
            "campaign_id": campaign_id,
            "source": passport["passport_identity"]["source"],
            "one_sentence_summary": review_room["one_sentence_summary"],
            "risk_flags": review_room["risk_flags"],
            "reviewer_next_actions": review_room["reviewer_next_actions"],
            "claims": passport["trust_boundary"]["claims"],
            "non_claims": passport["trust_boundary"]["non_claims"],
            "selected_provider": selected_provider,
            "selected_model": selected_model,
            "fallback_used": fallback_used,
            "attempt_count": attempt_count,
            "timeline_entries": summary["timeline_entries"],
            "asset_count": asset_count,
            "manifest_uri": manifest_uri,
            "manifest_hash": manifest_hash,
            "stored_manifest_verify": stored_manifest_verify,
            "archive_uri": archive_uri,
            "archive_sha256": archive_sha256,
            "rehydrate_source": rehydrate_source,
        }
        log("passport_digest", passport_digest)

        # ------------------------------------------------------------------
        # 13. Secret-leak scan.
        # ------------------------------------------------------------------
        secret_hits = scan_for_secrets(transcript)
        check("no secret leak in transcript", not secret_hits, detail=str(secret_hits))
        secret_hits_passport = scan_for_secrets(passport)
        check(
            "no secret leak in passport",
            not secret_hits_passport,
            detail=str(secret_hits_passport),
        )

        # ------------------------------------------------------------------
        # 14. Determine honest ok.
        # ------------------------------------------------------------------
        if live_completed:
            ok = (
                summary["passport_created"]
                and summary["passport_validated"]
                and summary["rehydrate_used"]
                and summary["trust_boundary_checked"]
                and summary["non_claims_checked"]
                and summary["no_provider_call_during_passport"]
                and summary["no_fake_media"]
                and summary["passport_source"] == SOURCE_ARCHIVE_REHYDRATED_RUN
                and passport["manifest_verification"]["manifest_uri"] == manifest_uri
            )
        else:
            # Honest blocked: passport created but clearly reflects no media.
            ok = (
                summary["passport_created"]
                and summary["passport_validated"]
                and summary["rehydrate_used"]
                and summary["trust_boundary_checked"]
                and summary["non_claims_checked"]
                and summary["no_provider_call_during_passport"]
                and summary["no_fake_media"]
                and "generated_media_missing" in review_room["risk_flags"]
                and passport["manifest_verification"]["manifest_uri"] is None
            )
        summary["ok"] = bool(ok)

    except CheckFail as exc:
        summary["ok"] = False
        summary["error"] = str(exc)
        log("check_failed", {"error": str(exc)})
    except Exception as exc:  # pragma: no cover - crash guard
        summary["ok"] = False
        summary["error"] = f"{type(exc).__name__}: {exc}"
        import traceback as _tb
        log("unhandled_crash", {
            "error": summary["error"],
            "traceback": _tb.format_exc(),
        })

    summary["written_at"] = now_iso()

    SUMMARY_PATH.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    TRANSCRIPT_PATH.write_text(
        json.dumps(
            {
                "slice": "PS-011",
                "framework_mode": FRAMEWORK_MODE,
                "steps": transcript,
                "fresh_store_snapshot_after_passport": (
                    fresh_service.store.snapshot()
                    if fresh_service is not None
                    else None
                ),
                "written_at": now_iso(),
            },
            indent=2,
            ensure_ascii=False,
            default=str,
        ),
        encoding="utf-8",
    )

    print(json.dumps(summary, indent=2, ensure_ascii=False, default=str))

    if not summary["ok"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
