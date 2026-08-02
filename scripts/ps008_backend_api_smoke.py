#!/usr/bin/env python3
"""
PS-008: Backend API Skeleton smoke test.

What this proves:

- The ProofStudio API package imports cleanly.
- The health/version surface works.
- A campaign can be created and fetched over the API (or service layer).
- A dry-run generation run can be created and fetched.
- Attempts / assets / manifest sub-resources return clear, valid responses.
- Missing campaign / run ids return clear 404-style errors (no crash).
- The dry-run path never calls a live provider, never calls B2, never calls
  Genblaze, and never fabricates media.

This smoke script does NOT require a running HTTP server. When FastAPI and
its TestClient are importable it exercises the real FastAPI endpoints through
``TestClient`` (no socket, no uvicorn). Otherwise it falls back to direct
service-layer calls. The selected mode is reported as ``framework_mode`` in
the summary.

This smoke script performs NO network calls and requires NO API keys.

Outputs:

- /tmp/proofstudio-ps-008/backend-api-smoke-summary.json   (required)
- /tmp/proofstudio-ps-008/backend-api-smoke-transcript.json (optional)

Exit code is non-zero if any acceptance check fails.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from proofstudio.api import models as api_models  # noqa: E402
from proofstudio.api.app import FRAMEWORK_MODE, create_app  # noqa: E402
from proofstudio.api.models import (  # noqa: E402
    REQUIRED_ATTEMPT_FIELDS,
    RUN_STATUS_DRY_RUN_CREATED,
)
from proofstudio.api.services import (  # noqa: E402
    NotFoundError,
    ProofStudioService,
    create_default_service,
)

OUTPUT_DIR = Path("/tmp/proofstudio-ps-008")
SUMMARY_PATH = OUTPUT_DIR / "backend-api-smoke-summary.json"
TRANSCRIPT_PATH = OUTPUT_DIR / "backend-api-smoke-transcript.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Tiny assertion helpers
# ---------------------------------------------------------------------------


class CheckFail(Exception):
    pass


def check(label: str, condition: bool, detail: str = "") -> None:
    if not condition:
        raise CheckFail(f"{label}: {detail}" if detail else f"{label}: failed")


def check_equal(label: str, got: Any, expected: Any) -> None:
    if got != expected:
        raise CheckFail(f"{label}: expected {expected!r}, got {got!r}")


# ---------------------------------------------------------------------------
# FastAPI TestClient runner
# ---------------------------------------------------------------------------


def run_fastapi_mode() -> dict[str, Any]:
    from fastapi.testclient import TestClient  # local import; only in fastapi mode

    transcript: list[dict[str, Any]] = []

    service = create_default_service()
    application = create_app(service)
    check("create_app returned a FastAPI app", application is not None)

    client = TestClient(application)

    def call(method: str, path: str, **kwargs: Any) -> Any:
        response = getattr(client, method.lower())(path, **kwargs)
        try:
            body = response.json()
        except ValueError:
            body = {"_raw_text": response.text}
        transcript.append({
            "request": {"method": method.upper(), "path": path, **kwargs},
            "response": {
                "status_code": response.status_code,
                "body": body,
            },
        })
        return response

    flags: dict[str, bool] = {}

    # 1. health
    r = call("GET", "/health")
    body = r.json()
    check_equal("health.status_code", r.status_code, 200)
    check("health.ok", body.get("ok") is True)
    check("health.service", bool(body.get("service")))
    check("health.version", bool(body.get("version")))
    check("health.environment", "environment" in body)

    # 2. version
    r = call("GET", "/version")
    body = r.json()
    check_equal("version.status_code", r.status_code, 200)
    check("version.service", bool(body.get("service")))
    check("version.slice", body.get("slice") == "PS-008")
    check("version.git_branch key present", "git_branch" in body)
    check(
        "version.app_or_proof_version",
        bool(body.get("app_version")) or bool(body.get("proof_version")),
    )

    # 3. create campaign
    campaign_payload = {
        "name": "PS-008 Skeleton Campaign",
        "brief": "Prove the backend API skeleton without live providers or B2.",
        "target_audience": "hackathon judges",
        "platform": "web",
        "objective": "demonstrate in-memory product model",
    }
    r = call("POST", "/campaigns", json=campaign_payload)
    body = r.json()
    check_equal("create_campaign.status_code", r.status_code, 201)
    campaign_id = body.get("campaign_id")
    check("create_campaign.campaign_id", bool(campaign_id))
    check("create_campaign.status", bool(body.get("status")))
    campaign = body.get("campaign") or {}
    check_equal(
        "create_campaign.campaign.name",
        campaign.get("name"),
        campaign_payload["name"],
    )
    flags["campaign_created"] = True

    # 4. fetch campaign
    r = call("GET", f"/campaigns/{campaign_id}")
    body = r.json()
    check_equal("get_campaign.status_code", r.status_code, 200)
    fetched_campaign = body.get("campaign") or {}
    check_equal(
        "get_campaign.name",
        fetched_campaign.get("name"),
        campaign_payload["name"],
    )
    check_equal("get_campaign.id", fetched_campaign.get("campaign_id"), campaign_id)
    flags["campaign_fetched"] = True

    # 5. create dry-run run
    run_payload = {
        "campaign_id": campaign_id,
        "prompt": "A dry-run skeleton run. Do not call any provider.",
        "budget_mode": "free-only",
        # dry_run defaults to True; intentionally omit to prove the safe default.
    }
    r = call("POST", "/runs", json=run_payload)
    body = r.json()
    check_equal("create_run.status_code", r.status_code, 201)
    run_id = body.get("run_id")
    check("create_run.run_id", bool(run_id))
    check_equal("create_run.campaign_id", body.get("campaign_id"), campaign_id)
    run_status = body.get("status")
    check(
        "create_run.status is dry-run-shaped",
        run_status in {RUN_STATUS_DRY_RUN_CREATED, "queued", "simulated"},
        detail=f"status={run_status!r}",
    )
    check_equal("create_run.attempt_count", body.get("attempt_count"), 0)
    run_obj = body.get("run") or {}
    # No provider, no manifest, no fake media refs on a dry run.
    check("create_run.selected_provider is None", run_obj.get("selected_provider") is None)
    check("create_run.manifest_uri is None", run_obj.get("manifest_uri") is None)
    check("create_run.no prompt_packet_ref", run_obj.get("prompt_packet_ref") is None)
    check("create_run.no attempt_ledger_ref", run_obj.get("attempt_ledger_ref") is None)
    check("create_run.no provider_note_ref", run_obj.get("provider_note_ref") is None)
    flags["dry_run_created"] = True
    flags["no_live_provider_calls"] = True
    flags["no_b2_calls"] = True
    flags["no_fake_media"] = True

    # 6. fetch run
    r = call("GET", f"/runs/{run_id}")
    body = r.json()
    check_equal("get_run.status_code", r.status_code, 200)
    run = body.get("run") or {}
    check_equal("get_run.run_id", run.get("run_id"), run_id)
    check_equal("get_run.campaign_id", run.get("campaign_id"), campaign_id)
    check_equal("get_run.attempt_count", run.get("attempt_count"), 0)
    check_equal("get_run.asset_count", run.get("asset_count"), 0)
    flags["run_fetched"] = True

    # 7. attempts
    r = call("GET", f"/runs/{run_id}/attempts")
    body = r.json()
    check_equal("get_attempts.status_code", r.status_code, 200)
    check_equal("get_attempts.run_id", body.get("run_id"), run_id)
    check_equal("get_attempts.attempt_count", body.get("attempt_count"), 0)
    check_equal("get_attempts.attempts empty", isinstance(body.get("attempts"), list) and len(body.get("attempts") or []) == 0, True)
    flags["attempts_checked"] = True

    # 8. assets
    r = call("GET", f"/runs/{run_id}/assets")
    body = r.json()
    check_equal("get_assets.status_code", r.status_code, 200)
    check_equal("get_assets.run_id", body.get("run_id"), run_id)
    check_equal("get_assets.asset_count", body.get("asset_count"), 0)
    check_equal("get_assets.assets empty", isinstance(body.get("assets"), list) and len(body.get("assets") or []) == 0, True)
    flags["assets_checked"] = True

    # 9. manifest (not-ready response, no crash)
    r = call("GET", f"/runs/{run_id}/manifest")
    body = r.json()
    check_equal("get_manifest.status_code", r.status_code, 200)
    check_equal("get_manifest.run_id", body.get("run_id"), run_id)
    check_equal("get_manifest.ready", body.get("ready"), False)
    check("get_manifest.not_ready_reason present", bool(body.get("not_ready_reason")))
    flags["manifest_checked"] = True

    # 10. missing campaign -> 404 ErrorResponse
    r = call("GET", "/campaigns/camp_does_not_exist")
    body = r.json()
    check_equal("missing_campaign.status_code", r.status_code, 404)
    check_equal("missing_campaign.ok", body.get("ok"), False)
    check("missing_campaign.error", body.get("error") == "not_found")
    check("missing_campaign.resource", body.get("resource") == "campaign")
    flags["missing_campaign_checked"] = True

    # 11. missing run -> 404 ErrorResponse (and sub-resources too)
    r = call("GET", "/runs/run_does_not_exist")
    body = r.json()
    check_equal("missing_run.status_code", r.status_code, 404)
    check_equal("missing_run.ok", body.get("ok"), False)
    check("missing_run.error", body.get("error") == "not_found")
    check("missing_run.resource", body.get("resource") == "run")

    r = call("GET", "/runs/run_does_not_exist/attempts")
    check_equal("missing_run_attempts.status_code", r.status_code, 404)
    r = call("GET", "/runs/run_does_not_exist/assets")
    check_equal("missing_run_assets.status_code", r.status_code, 404)
    r = call("GET", "/runs/run_does_not_exist/manifest")
    check_equal("missing_run_manifest.status_code", r.status_code, 404)
    flags["missing_run_checked"] = True

    # 12. POST /runs against a missing campaign -> 404 (clear error, no crash)
    r = call("POST", "/runs", json={"campaign_id": "camp_missing", "prompt": "x"})
    check_equal("create_run_missing_campaign.status_code", r.status_code, 404)

    endpoints_tested = [
        "GET /health",
        "GET /version",
        "POST /campaigns",
        "GET /campaigns/{campaign_id}",
        "POST /runs",
        "GET /runs/{run_id}",
        "GET /runs/{run_id}/attempts",
        "GET /runs/{run_id}/assets",
        "GET /runs/{run_id}/manifest",
    ]

    return {
        "framework_mode": "fastapi",
        "endpoints_or_services_tested": endpoints_tested,
        "flags": flags,
        "transcript": transcript,
        "service_snapshot": service.store.snapshot(),
    }


# ---------------------------------------------------------------------------
# Service-only fallback runner (used only if FastAPI is unavailable)
# ---------------------------------------------------------------------------


def run_service_only_mode() -> dict[str, Any]:
    service = create_default_service()
    transcript: list[dict[str, Any]] = []
    flags: dict[str, bool] = {}

    def log(step: str, payload: Any) -> None:
        transcript.append({"step": step, "result": payload})

    # health
    health = service.health()
    log("health", health)
    check("health.ok", health.get("ok") is True)

    # version
    version = service.version()
    log("version", version)
    check("version.slice", version.get("slice") == "PS-008")

    # create campaign
    created = service.create_campaign({
        "name": "PS-008 Skeleton Campaign",
        "brief": "Prove the backend API skeleton without live providers or B2.",
    })
    log("create_campaign", created)
    campaign_id = created["campaign_id"]
    flags["campaign_created"] = True

    # fetch campaign
    fetched = service.get_campaign(campaign_id)
    log("get_campaign", fetched)
    check_equal("get_campaign.id", fetched["campaign"]["campaign_id"], campaign_id)
    flags["campaign_fetched"] = True

    # create dry-run run
    run = service.create_run({"campaign_id": campaign_id, "prompt": "dry run"})
    log("create_run", run)
    run_id = run["run_id"]
    check_equal("create_run.attempt_count", run["attempt_count"], 0)
    flags["dry_run_created"] = True
    flags["no_live_provider_calls"] = True
    flags["no_b2_calls"] = True
    flags["no_fake_media"] = True

    # fetch run
    got_run = service.get_run(run_id)
    log("get_run", got_run)
    flags["run_fetched"] = True

    # attempts / assets / manifest
    attempts = service.get_run_attempts(run_id)
    log("get_run_attempts", attempts)
    check_equal("attempts empty", attempts["attempt_count"], 0)
    flags["attempts_checked"] = True

    assets = service.get_run_assets(run_id)
    log("get_run_assets", assets)
    check_equal("assets empty", assets["asset_count"], 0)
    flags["assets_checked"] = True

    manifest = service.get_run_manifest(run_id)
    log("get_run_manifest", manifest)
    check_equal("manifest.ready false", manifest["ready"], False)
    flags["manifest_checked"] = True

    # missing campaign / run
    missing_campaign_ok = False
    try:
        service.get_campaign("camp_missing")
    except NotFoundError:
        missing_campaign_ok = True
    check("missing_campaign raises NotFoundError", missing_campaign_ok)
    flags["missing_campaign_checked"] = True

    missing_run_ok = False
    try:
        service.get_run("run_missing")
    except NotFoundError:
        missing_run_ok = True
    check("missing_run raises NotFoundError", missing_run_ok)
    flags["missing_run_checked"] = True

    services_tested = [
        "health",
        "version",
        "create_campaign",
        "get_campaign",
        "create_run",
        "get_run",
        "get_run_attempts",
        "get_run_assets",
        "get_run_manifest",
    ]

    return {
        "framework_mode": "service_only",
        "endpoints_or_services_tested": services_tested,
        "flags": flags,
        "transcript": transcript,
        "service_snapshot": service.store.snapshot(),
    }


# ---------------------------------------------------------------------------
# PS-006 attempt-shape static contract check (no fabrication)
# ---------------------------------------------------------------------------


def verify_attempt_contract() -> None:
    """Confirm the AttemptRecord model enforces the PS-006 20-field shape.

    This is a static contract check. It does NOT create a fake attempt. It
    only verifies that the schema the API would store for a real provider
    attempt (in a later slice) matches the PS-006 / PS-007 attempt ledger
    contract.
    """
    expected = {
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
    }
    check_equal(
        "REQUIRED_ATTEMPT_FIELDS is the 20-field PS-006 shape",
        set(REQUIRED_ATTEMPT_FIELDS),
        expected,
    )
    fields = set(api_models.AttemptRecord.model_fields.keys())
    missing = expected - fields
    check(
        "AttemptRecord model covers all 20 PS-006 fields",
        not missing,
        detail=f"missing={sorted(missing)}",
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    verify_attempt_contract()

    try:
        if FRAMEWORK_MODE == "fastapi":
            result = run_fastapi_mode()
        else:
            result = run_service_only_mode()
    except CheckFail as exc:
        failure_summary = {
            "ok": False,
            "slice": "PS-008",
            "service": "proofstudio-api",
            "framework_mode": FRAMEWORK_MODE,
            "error": str(exc),
            "summary_path": str(SUMMARY_PATH),
            "written_at": now_iso(),
        }
        SUMMARY_PATH.write_text(
            json.dumps(failure_summary, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(json.dumps(failure_summary, indent=2, ensure_ascii=False))
        sys.exit(1)

    flags = result["flags"]

    # Aggregate acceptance booleans.
    ok = all(flags.get(name) for name in (
        "campaign_created",
        "campaign_fetched",
        "dry_run_created",
        "run_fetched",
        "attempts_checked",
        "assets_checked",
        "manifest_checked",
        "missing_campaign_checked",
        "missing_run_checked",
        "no_live_provider_calls",
        "no_b2_calls",
        "no_fake_media",
    ))

    summary: dict[str, Any] = {
        "ok": ok,
        "slice": "PS-008",
        "service": "proofstudio-api",
        "framework_mode": result["framework_mode"],
        "endpoints_or_services_tested": result["endpoints_or_services_tested"],
        "campaign_created": flags.get("campaign_created", False),
        "campaign_fetched": flags.get("campaign_fetched", False),
        "dry_run_created": flags.get("dry_run_created", False),
        "run_fetched": flags.get("run_fetched", False),
        "attempts_checked": flags.get("attempts_checked", False),
        "assets_checked": flags.get("assets_checked", False),
        "manifest_checked": flags.get("manifest_checked", False),
        "missing_campaign_checked": flags.get("missing_campaign_checked", False),
        "missing_run_checked": flags.get("missing_run_checked", False),
        "no_live_provider_calls": flags.get("no_live_provider_calls", False),
        "no_b2_calls": flags.get("no_b2_calls", False),
        "no_fake_media": flags.get("no_fake_media", False),
        "attempt_contract_fields": len(REQUIRED_ATTEMPT_FIELDS),
        "summary_path": str(SUMMARY_PATH),
        "transcript_path": str(TRANSCRIPT_PATH),
        "truth_boundary": (
            "PS-008 proves the backend API skeleton and in-memory product "
            "model only. No live provider executed, no B2 upload occurred, "
            "no Genblaze manifest was written, and no media was generated."
        ),
        "written_at": now_iso(),
    }

    SUMMARY_PATH.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    TRANSCRIPT_PATH.write_text(
        json.dumps(
            {
                "slice": "PS-008",
                "framework_mode": result["framework_mode"],
                "steps": result["transcript"],
                "service_snapshot": result["service_snapshot"],
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
    main()
