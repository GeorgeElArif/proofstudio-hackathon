#!/usr/bin/env python3
"""
PS-012: FastAPI Server Mode + Demo API Contract smoke test.

What this proves:

- ``proofstudio.api.app:app`` is a real FastAPI instance (not None) once the
  fastapi/uvicorn/httpx dependencies are installed.
- The required HTTP contract endpoints exist and behave correctly through a
  FastAPI TestClient (no internal Python service calls in this smoke -- it
  exercises the real HTTP layer):
    GET  /health
    GET  /version
    POST /campaigns
    GET  /campaigns/{campaign_id}
    POST /runs                         (default = safe dry-run)
    GET  /runs/{run_id}
    GET  /runs/{run_id}/attempts
    GET  /runs/{run_id}/assets
    GET  /runs/{run_id}/manifest
    GET  /runs/{run_id}/passport
- Route handlers delegate to ``ProofStudioService``; no business logic is
  duplicated in the handlers.
- The default POST /runs is a safe dry-run: it does NOT call any live provider,
  does NOT call B2, and does NOT fabricate media/assets/manifests.
- The passport endpoint returns an honest no-evidence / no-media passport for a
  dry-run run (uses ``get_run_passport``, never reruns providers).

Optional live mode:

- ``PROOFSTUDIO_PS012_LIVE=1`` will additionally create a live run
  (``run_live=true``) and record its status. Default acceptance never requires
  live provider calls, provider credits, or B2.

Truth boundary: PS-012 proves ProofStudio has a runnable FastAPI demo API
contract. It does not prove production deployment, a public app URL,
authentication, production database persistence, background job reliability,
legal authenticity, C2PA authenticity, semantic truth, or human authorship.

Historical proof scripts (PS-004 .. PS-011) are not modified.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import proofstudio.api.services as services_module  # noqa: E402
import proofstudio.api.archive as archive_module  # noqa: E402
from proofstudio.api.models import (  # noqa: E402
    RUN_STATUS_DRY_RUN_CREATED,
)
from proofstudio.api.passport import (  # noqa: E402
    PASSPORT_TRUTH_BOUNDARY,
)

OUTPUT_DIR = Path("/tmp/proofstudio-ps-012")
SUMMARY_PATH = OUTPUT_DIR / "fastapi-server-demo-contract-summary.json"
TRANSCRIPT_PATH = OUTPUT_DIR / "fastapi-server-demo-contract-transcript.json"
DOCS_PATH = REPO_ROOT / "docs" / "ps-012-fastapi-server-demo-contract-proof.md"

# The 10 required contract routes (method, path).
REQUIRED_ROUTES: tuple[tuple[str, str], ...] = (
    ("GET", "/health"),
    ("GET", "/version"),
    ("POST", "/campaigns"),
    ("GET", "/campaigns/{campaign_id}"),
    ("POST", "/runs"),
    ("GET", "/runs/{run_id}"),
    ("GET", "/runs/{run_id}/attempts"),
    ("GET", "/runs/{run_id}/assets"),
    ("GET", "/runs/{run_id}/manifest"),
    ("GET", "/runs/{run_id}/passport"),
)

# Historical proof scripts that must never be modified by this slice.
HISTORICAL_SCRIPTS = (
    "scripts/ps004_provider_router_cloudflare_smoke.py",
    "scripts/ps005_pollinations_fallback_smoke.py",
    "scripts/ps006_provider_router_core_smoke.py",
    "scripts/ps007_live_provider_router_chain_smoke.py",
    "scripts/ps008_backend_api_smoke.py",
    "scripts/ps009_api_live_run_bridge_smoke.py",
    "scripts/ps010_run_archive_rehydrate_b2_smoke.py",
    "scripts/ps011_provenance_passport_api_smoke.py",
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


def scan_for_secrets(payload: Any) -> list[str]:
    text = json.dumps(payload, ensure_ascii=False, default=str)
    hits: list[str] = []
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            hits.append(f"secret pattern matched: {pattern.pattern[:40]}...")
    return hits


def historical_scripts_untouched() -> list[str]:
    """Return historical scripts git sees as modified (empty == untouched)."""
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
        parts = line.split(None, 1)
        if len(parts) == 2:
            modified.append(parts[1])
    return modified


def route_signatures(application: Any) -> set[tuple[str, str]]:
    """Collect (method, path) signatures declared on the FastAPI app."""
    signatures: set[tuple[str, str]] = set()
    for route in getattr(application, "routes", []):
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", None) or set()
        if not path:
            continue
        for method in methods:
            if method in {"HEAD"}:
                continue
            signatures.add((method, path))
    return signatures


class ProviderCallSentinel(Exception):
    pass


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    transcript: list[dict[str, Any]] = []

    def log(step: str, payload: Any) -> None:
        transcript.append({"step": step, "result": payload})

    summary: dict[str, Any] = {
        "ok": False,
        "slice": "PS-012",
        "framework_mode": None,
        "fastapi_available": False,
        "app_is_fastapi": False,
        "server_contract_checked": False,
        "health_checked": False,
        "version_checked": False,
        "campaign_create_checked": False,
        "campaign_get_checked": False,
        "dry_run_create_checked": False,
        "run_get_checked": False,
        "attempts_get_checked": False,
        "assets_get_checked": False,
        "manifest_get_checked": False,
        "passport_get_checked": False,
        "default_no_live_provider_call": False,
        "default_no_b2_call": False,
        "no_fake_media": False,
        "live_mode_enabled": os.environ.get("PROOFSTUDIO_PS012_LIVE") == "1",
        "live_run_status": None,
        "route_count": 0,
        "docs_available": DOCS_PATH.exists(),
        "summary_path": str(SUMMARY_PATH),
        "transcript_path": str(TRANSCRIPT_PATH),
        "truth_boundary": (
            "PS-012 proves ProofStudio has a runnable FastAPI demo API contract. "
            "It does not prove production deployment, a public app URL, "
            "authentication, production database persistence, background job "
            "reliability, legal authenticity, C2PA authenticity, semantic truth, "
            "or human authorship."
        ),
    }

    client = None
    provider_call_counter = {"count": 0}
    b2_call_counter = {"count": 0}

    def _live_sentinel(**kwargs: Any) -> dict[str, Any]:
        provider_call_counter["count"] += 1
        raise ProviderCallSentinel(
            "LIVE PROVIDER WAS CALLED DURING PS-012 DEFAULT DRY-RUN"
        )

    def _b2_store_sentinel(*args: Any, **kwargs: Any) -> dict[str, Any]:
        b2_call_counter["count"] += 1
        raise ProviderCallSentinel("B2 STORE WAS CALLED DURING PS-012 DEFAULT")

    def _b2_read_sentinel(*args: Any, **kwargs: Any) -> dict[str, Any]:
        b2_call_counter["count"] += 1
        raise ProviderCallSentinel("B2 READ WAS CALLED DURING PS-012 DEFAULT")

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
        # 1. Import the app module and verify FastAPI server mode is real.
        # ------------------------------------------------------------------
        import fastapi  # noqa: E402

        from proofstudio.api.app import app, FRAMEWORK_MODE  # noqa: E402
        from fastapi.testclient import TestClient  # noqa: E402
        framework_mode = FRAMEWORK_MODE
        summary["framework_mode"] = framework_mode
        summary["fastapi_available"] = framework_mode == "fastapi"

        check("app is not None", app is not None)
        check("app is FastAPI", isinstance(app, fastapi.FastAPI))
        summary["app_is_fastapi"] = isinstance(app, fastapi.FastAPI)
        log("app_import", {
            "framework_mode": framework_mode,
            "app_is_fastapi": summary["app_is_fastapi"],
            "app_title": getattr(app, "title", None),
            "app_version": getattr(app, "version", None),
        })

        # ------------------------------------------------------------------
        # 2. Validate the required endpoint routes exist.
        # ------------------------------------------------------------------
        signatures = route_signatures(app)
        missing = [sig for sig in REQUIRED_ROUTES if sig not in signatures]
        check(
            "all required contract routes exist",
            not missing,
            detail=f"missing routes: {missing}",
        )
        summary["server_contract_checked"] = not missing
        summary["route_count"] = sum(1 for sig in REQUIRED_ROUTES if sig in signatures)
        log("route_contract", {
            "route_count": summary["route_count"],
            "declared_signatures": sorted(sorted(s) for s in signatures),
        })

        # ------------------------------------------------------------------
        # 3. Build the TestClient and wire sentinels so we can prove the
        #    default dry-run path never touches a live provider or B2.
        # ------------------------------------------------------------------
        client = TestClient(app)

        original_execute_live_run = services_module.execute_live_run
        original_b2_store = archive_module.store_run_archive_with_genblaze
        original_b2_read = archive_module.read_archive_from_b2
        services_module.execute_live_run = _live_sentinel  # type: ignore[assignment]
        archive_module.store_run_archive_with_genblaze = _b2_store_sentinel  # type: ignore[assignment]
        archive_module.read_archive_from_b2 = _b2_read_sentinel  # type: ignore[assignment]
        try:
            _exercise_contract(client, summary, log)
        finally:
            services_module.execute_live_run = original_execute_live_run  # type: ignore[assignment]
            archive_module.store_run_archive_with_genblaze = original_b2_store  # type: ignore[assignment]
            archive_module.read_archive_from_b2 = original_b2_read  # type: ignore[assignment]

        # ------------------------------------------------------------------
        # 4. Confirm default dry-run made no live-provider call and no B2 call.
        # ------------------------------------------------------------------
        check_equal(
            "no live provider call during default dry-run",
            provider_call_counter["count"],
            0,
        )
        check_equal(
            "no B2 call during default dry-run",
            b2_call_counter["count"],
            0,
        )
        summary["default_no_live_provider_call"] = provider_call_counter["count"] == 0
        summary["default_no_b2_call"] = b2_call_counter["count"] == 0
        log("call_sentinels", {
            "provider_calls": provider_call_counter["count"],
            "b2_calls": b2_call_counter["count"],
        })

        # ------------------------------------------------------------------
        # 5. Secret-leak scan across the transcript.
        # ------------------------------------------------------------------
        secret_hits = scan_for_secrets(transcript)
        check("no secret leak in transcript", not secret_hits, detail=str(secret_hits))
        log("secret_scan", {"hits": secret_hits})

        # ------------------------------------------------------------------
        # 6. Optional live mode (never required for ok).
        # ------------------------------------------------------------------
        if summary["live_mode_enabled"]:
            _exercise_live(client, summary, log)

        summary["docs_available"] = DOCS_PATH.exists()

        ok = (
            summary["app_is_fastapi"]
            and summary["server_contract_checked"]
            and summary["health_checked"]
            and summary["version_checked"]
            and summary["campaign_create_checked"]
            and summary["campaign_get_checked"]
            and summary["dry_run_create_checked"]
            and summary["run_get_checked"]
            and summary["attempts_get_checked"]
            and summary["assets_get_checked"]
            and summary["manifest_get_checked"]
            and summary["passport_get_checked"]
            and summary["default_no_live_provider_call"]
            and summary["default_no_b2_call"]
            and summary["no_fake_media"]
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
                "slice": "PS-012",
                "framework_mode": summary.get("framework_mode"),
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

    if not summary["ok"]:
        sys.exit(1)


def _exercise_contract(
    client: Any,
    summary: dict[str, Any],
    log: Any,
) -> None:
    """Run the default (dry-run) HTTP contract through the TestClient."""

    def _body(resp: Any) -> dict[str, Any]:
        return resp.json() if resp.content else {}

    # --- health ---
    r = client.get("/health")
    body = _body(r)
    check_equal("health.status_code", r.status_code, 200)
    check("health.ok", body.get("ok") is True)
    check("health.service", bool(body.get("service")))
    check("health.mode", bool(body.get("mode")))
    check("health.version", bool(body.get("version")))
    summary["health_checked"] = True
    log("GET /health", {"status_code": r.status_code, "body": body})

    # --- version ---
    r = client.get("/version")
    body = _body(r)
    check_equal("version.status_code", r.status_code, 200)
    check("version.service", bool(body.get("service")))
    check("version.version", bool(body.get("version")))
    check("version.framework_mode", bool(body.get("framework_mode")))
    capabilities = body.get("capabilities") or []
    required_capabilities = {
        "provider_router",
        "live_run_bridge",
        "b2_archive_rehydrate",
        "provenance_passport",
        "fastapi_server",
    }
    check(
        "version.capabilities covers required set",
        required_capabilities.issubset(set(capabilities)),
        detail=str(capabilities),
    )
    summary["version_checked"] = True
    log("GET /version", {"status_code": r.status_code, "body": body})

    # --- create campaign ---
    campaign_payload = {
        "name": "PS-012 FastAPI Server Demo Contract Campaign",
        "brief": (
            "Prove the FastAPI server demo contract over HTTP without calling "
            "live providers or B2 and without fabricating media."
        ),
        "target_audience": "hackathon judges and reviewers",
        "platform": "web",
        "objective": "validate the runnable HTTP API contract",
    }
    r = client.post("/campaigns", json=campaign_payload)
    body = _body(r)
    check_equal("create_campaign.status_code", r.status_code, 201)
    campaign_id = body.get("campaign_id")
    check("create_campaign.campaign_id", bool(campaign_id))
    campaign = body.get("campaign") or {}
    check_equal(
        "create_campaign.name",
        campaign.get("name"),
        campaign_payload["name"],
    )
    summary["campaign_create_checked"] = True
    log("POST /campaigns", {"status_code": r.status_code, "campaign_id": campaign_id})

    # --- get campaign ---
    r = client.get(f"/campaigns/{campaign_id}")
    body = _body(r)
    check_equal("get_campaign.status_code", r.status_code, 200)
    fetched = body.get("campaign") or {}
    check_equal("get_campaign.id", fetched.get("campaign_id"), campaign_id)
    summary["campaign_get_checked"] = True
    log("GET /campaigns/{id}", {"status_code": r.status_code})

    # --- clean 404 for a missing campaign ---
    r404 = client.get("/campaigns/does_not_exist_ps012")
    check_equal("get_missing_campaign.status_code", r404.status_code, 404)
    log("GET /campaigns/{missing}", {"status_code": r404.status_code})

    # --- create dry-run run (default safe) ---
    run_payload = {
        "campaign_id": campaign_id,
        "prompt": "A safe dry-run run. Do not call any provider.",
        "budget_mode": "free-only",
        "run_live": False,
    }
    r = client.post("/runs", json=run_payload)
    body = _body(r)
    check_equal("create_run.status_code", r.status_code, 201)
    run_id = body.get("run_id")
    check("create_run.run_id", bool(run_id))
    run_record = body.get("run") or {}
    check_equal(
        "create_run.status is dry_run_created",
        run_record.get("status"),
        RUN_STATUS_DRY_RUN_CREATED,
    )
    check("create_run.no provider selected", not run_record.get("selected_provider"))
    check("create_run.no manifest_uri", not run_record.get("manifest_uri"))
    summary["dry_run_create_checked"] = True
    log("POST /runs", {
        "status_code": r.status_code,
        "run_id": run_id,
        "status": run_record.get("status"),
    })

    # --- get run ---
    r = client.get(f"/runs/{run_id}")
    body = _body(r)
    check_equal("get_run.status_code", r.status_code, 200)
    got_run = body.get("run") or {}
    check_equal("get_run.id", got_run.get("run_id"), run_id)
    check_equal(
        "get_run.dry_run flag true",
        got_run.get("dry_run"),
        True,
    )
    summary["run_get_checked"] = True
    log("GET /runs/{id}", {"status_code": r.status_code})

    # --- get attempts (must be empty for dry-run) ---
    r = client.get(f"/runs/{run_id}/attempts")
    body = _body(r)
    check_equal("get_attempts.status_code", r.status_code, 200)
    check_equal("get_attempts.empty", body.get("attempt_count"), 0)
    check_equal("get_attempts.list empty", body.get("attempts"), [])
    summary["attempts_get_checked"] = True
    log("GET /runs/{id}/attempts", {"attempt_count": body.get("attempt_count")})

    # --- get assets (must be empty for dry-run -> no fake media) ---
    r = client.get(f"/runs/{run_id}/assets")
    body = _body(r)
    check_equal("get_assets.status_code", r.status_code, 200)
    check_equal("get_assets.empty", body.get("asset_count"), 0)
    check_equal("get_assets.list empty", body.get("assets"), [])
    summary["assets_get_checked"] = True
    summary["no_fake_media"] = body.get("asset_count") == 0
    log("GET /runs/{id}/assets", {"asset_count": body.get("asset_count")})

    # --- get manifest (must be not-ready for dry-run, no fake verification) ---
    r = client.get(f"/runs/{run_id}/manifest")
    body = _body(r)
    check_equal("get_manifest.status_code", r.status_code, 200)
    check("get_manifest.not ready", body.get("ready") is False)
    check("get_manifest.no manifest_uri", not body.get("manifest_uri"))
    check(
        "get_manifest.stored_manifest_verify not faked",
        body.get("stored_manifest_verify") is not True,
    )
    summary["manifest_get_checked"] = True
    log("GET /runs/{id}/manifest", {
        "ready": body.get("ready"),
        "not_ready_reason": body.get("not_ready_reason"),
    })

    # --- get passport (honest no-media / no-evidence state) ---
    r = client.get(f"/runs/{run_id}/passport")
    body = _body(r)
    check_equal("get_passport.status_code", r.status_code, 200)
    generation = body.get("generation_summary") or {}
    check_equal(
        "passport.generated_media_present false",
        generation.get("generated_media_present"),
        False,
    )
    manifest_verification = body.get("manifest_verification") or {}
    check(
        "passport.no faked manifest_uri",
        not manifest_verification.get("manifest_uri"),
    )
    check(
        "passport.stored_manifest_verify not faked",
        manifest_verification.get("stored_manifest_verify") is not True,
    )
    archive_section = body.get("archive_and_rehydration") or {}
    check_equal(
        "passport.archive not_available",
        archive_section.get("status"),
        "not_available",
    )
    trust = body.get("trust_boundary") or {}
    non_claims = trust.get("non_claims") or []
    for required in (
        "semantic_truth",
        "legal_authenticity",
        "c2pa_authenticity",
        "human_authorship",
        "final_production_security",
    ):
        check(
            f"passport.non_claim {required} present",
            required in non_claims,
        )
    summary["passport_get_checked"] = True
    log("GET /runs/{id}/passport", {
        "generated_media_present": generation.get("generated_media_present"),
        "archive_status": archive_section.get("status"),
        "non_claims": non_claims,
    })

    # --- clean 404 for a missing run ---
    r404 = client.get("/runs/does_not_exist_ps012")
    check_equal("get_missing_run.status_code", r404.status_code, 404)
    log("GET /runs/{missing}", {"status_code": r404.status_code})


def _exercise_live(
    client: Any,
    summary: dict[str, Any],
    log: Any,
) -> None:
    """Optional live-run path. Never required for default ok.

    Creates a fresh campaign + a ``run_live=true`` run and records the status.
    A blocked/failed live run (e.g. no provider credits) is recorded honestly
    and does not fail the smoke, because default acceptance must not depend on
    live provider availability.
    """
    try:
        campaign = client.post(
            "/campaigns",
            json={
                "name": "PS-012 Optional Live Campaign",
                "brief": "Optional live run for PS-012 server contract.",
            },
        ).json()
        campaign_id = campaign.get("campaign_id")
        r = client.post(
            "/runs",
            json={
                "campaign_id": campaign_id,
                "prompt": "PS-012 optional live run via the FastAPI contract.",
                "budget_mode": "free-only",
                "dry_run": False,
                "run_live": True,
            },
        )
        body = r.json()
        run_record = body.get("run") or {}
        summary["live_run_status"] = run_record.get("status") or body.get("status")
        log("POST /runs (live, optional)", {
            "status_code": r.status_code,
            "live_run_status": summary["live_run_status"],
            "selected_provider": run_record.get("selected_provider"),
        })
    except Exception as exc:  # pragma: no cover - live path is best-effort
        summary["live_run_status"] = f"live_error: {type(exc).__name__}"
        log("POST /runs (live, optional) failed", {
            "error": f"{type(exc).__name__}: {exc}",
        })


if __name__ == "__main__":
    main()
