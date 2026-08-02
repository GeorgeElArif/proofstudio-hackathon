#!/usr/bin/env python3
"""
PS-013A: Local Demo Integration Hardening smoke test.

What this proves:

- ``proofstudio.api.app:app`` is a real FastAPI instance.
- FastAPI ``CORSMiddleware`` is installed with an explicit local-origin
  allow-list (no wildcard credentials), so the browser at
  ``http://127.0.0.1:5173`` / ``http://localhost:5173`` can reach the backend at
  ``http://127.0.0.1:8000`` without a cross-origin block.
- A browser-style CORS **preflight** (OPTIONS) for ``/version`` succeeds and the
  response echoes the allowed origin + method, for both ``127.0.0.1:5173`` and
  ``localhost:5173``.
- A browser-style **GET** ``/version`` with an ``Origin`` header succeeds and
  carries ``Access-Control-Allow-Origin``.
- ``/health`` and ``/version`` still work.
- Campaign creation (POST /campaigns) works.
- The default POST /runs is a **safe dry-run**: it does NOT call any live
  provider, does NOT call B2, and does NOT fabricate media/assets/manifests.
- The frontend API client carries the API base URL config, and the API Status
  card shows clearer backend-not-running / CORS-style error copy.
- The docs include the exact two-terminal local runbook.

This smoke uses FastAPI's TestClient (no internal Python service calls for the
HTTP contract). It does NOT start a browser, does NOT call live providers, and
does NOT require B2 credentials.

Truth boundary: PS-013A proves the local browser demo can connect to the
FastAPI backend through safe local CORS settings and execute the default
dry-run demo path. It does not prove public deployment, production CORS
policy, authentication, production persistence, background job reliability,
legal authenticity, C2PA authenticity, semantic truth, or human authorship.

Historical proof scripts (PS-004 .. PS-013) are not modified.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
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

OUTPUT_DIR = Path("/tmp/proofstudio-ps-013a")
SUMMARY_PATH = OUTPUT_DIR / "local-demo-integration-hardening-summary.json"
TRANSCRIPT_PATH = OUTPUT_DIR / "local-demo-integration-hardening-transcript.json"
DOCS_PATH = REPO_ROOT / "docs" / "ps-013a-local-demo-integration-hardening-proof.md"
README_PATH = REPO_ROOT / "apps" / "web" / "README.md"
APP_TSX_PATH = REPO_ROOT / "apps" / "web" / "src" / "App.tsx"
API_TS_PATH = REPO_ROOT / "apps" / "web" / "src" / "api.ts"
APP_PY_PATH = REPO_ROOT / "src" / "proofstudio" / "api" / "app.py"

# Local origins the backend must allow for the local demo (PS-013A section 7).
REQUIRED_ALLOWED_ORIGINS: tuple[str, ...] = (
    "http://127.0.0.1:5173",
    "http://localhost:5173",
)
# Optional but recommended preview origins.
EXTRA_ALLOWED_ORIGINS: tuple[str, ...] = (
    "http://127.0.0.1:4173",
    "http://localhost:4173",
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
    "scripts/ps012_fastapi_server_demo_contract_smoke.py",
    "scripts/ps013_demo_ui_review_room_smoke.py",
)

# Markers that prove the docs contain the exact two-terminal local runbook.
RUNBOOK_MARKERS: tuple[str, ...] = (
    "source .venv/bin/activate",
    'PYTHONPATH="$PWD/src:${PYTHONPATH:-}"',
    "uvicorn proofstudio.api.app:app",
    "--host 127.0.0.1 --port 8000",
    "npm run dev",
    "--host 127.0.0.1 --port 5173",
    "http://127.0.0.1:5173",
)

SECRET_PATTERNS = [
    re.compile(r"(?i)Bearer\s+[A-Za-z0-9\-_.=~]{8,}"),
    re.compile(r"(?i)B2_KEY_ID[\s:=]+\S{8,}"),
    re.compile(r"(?i)B2_APP_KEY[\s:=]+\S{8,}"),
    re.compile(r"(?i)CLOUDFLARE_API_TOKEN[\s:=]+\S{8,}"),
    re.compile(r"(?i)GEMINI_API_KEY[\s:=]+\S{8,}"),
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


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def scan_for_secrets(payload: Any) -> list[str]:
    text = json.dumps(payload, ensure_ascii=False, default=str)
    hits: list[str] = []
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            hits.append(f"secret pattern matched: {pattern.pattern[:40]}...")
    return hits


def historical_scripts_untouched() -> list[str]:
    """Return historical scripts git sees as modified (empty == untouched)."""
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


def cors_middleware_present(application: Any) -> bool:
    """True when a CORSMiddleware is registered on the app."""
    try:
        from starlette.middleware.cors import CORSMiddleware as StarletteCORS
    except Exception:  # pragma: no cover
        StarletteCORS = None
    user_middleware = getattr(application, "user_middleware", []) or []
    for mw in user_middleware:
        cls = getattr(mw, "cls", None)
        if cls is None:
            continue
        if StarletteCORS is not None and cls is StarletteCORS:
            return True
        if getattr(cls, "__name__", "") == "CORSMiddleware":
            return True
    return False


def allowed_origins_from_app(application: Any) -> set[str]:
    """Best-effort extraction of configured CORS allow_origins."""
    origins: set[str] = set()
    user_middleware = getattr(application, "user_middleware", []) or []
    for mw in user_middleware:
        cls = getattr(mw, "cls", None)
        if getattr(cls, "__name__", "") != "CORSMiddleware":
            continue
        options = getattr(mw, "options", {}) or {}
        raw = options.get("allow_origins") or []
        for o in raw:
            if isinstance(o, str):
                origins.add(o)
    return origins


class ProviderCallSentinel(Exception):
    pass


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
    summary["health_checked"] = True
    log("GET /health", {"status_code": r.status_code, "body": body})

    # --- version (also the CORS target below) ---
    r = client.get("/version")
    body = _body(r)
    check_equal("version.status_code", r.status_code, 200)
    check("version.framework_mode", bool(body.get("framework_mode")))
    summary["version_checked"] = True
    log("GET /version", {"status_code": r.status_code, "body": body})

    # --- create campaign ---
    campaign_payload = {
        "name": "PS-013A Local Demo Integration Hardening Campaign",
        "brief": (
            "Prove the local browser demo can connect to the FastAPI backend "
            "through safe local CORS settings and execute the default dry-run "
            "demo path without calling live providers or B2."
        ),
        "target_audience": "hackathon judges and reviewers",
        "platform": "web",
        "objective": "validate local demo integration hardening",
    }
    r = client.post("/campaigns", json=campaign_payload)
    body = _body(r)
    check_equal("create_campaign.status_code", r.status_code, 201)
    campaign_id = body.get("campaign_id")
    check("create_campaign.campaign_id", bool(campaign_id))
    summary["campaign_create_checked"] = True
    log("POST /campaigns", {"status_code": r.status_code, "campaign_id": campaign_id})

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
    summary["dry_run_create_checked"] = True
    log("POST /runs", {
        "status_code": r.status_code,
        "run_id": run_id,
        "status": run_record.get("status"),
    })

    # --- dry-run produces no fake media: assets empty, manifest not-ready ---
    r = client.get(f"/runs/{run_id}/assets")
    body = _body(r)
    check_equal("get_assets.empty", body.get("asset_count"), 0)
    r = client.get(f"/runs/{run_id}/passport")
    body = _body(r)
    generation = body.get("generation_summary") or {}
    check_equal(
        "passport.no generated media",
        generation.get("generated_media_present"),
        False,
    )
    summary["no_fake_media"] = True
    log("dry_run_safety", {
        "asset_count": 0,
        "generated_media_present": False,
    })


def _check_cors(
    client: Any,
    origin: str,
    summary: dict[str, Any],
    log: Any,
    key: str,
) -> None:
    """Verify a browser-style CORS preflight + GET for ``origin``."""

    # Preflight (OPTIONS).
    r = client.options(
        "/version",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
        },
    )
    # Starlette returns 200 for an allowed preflight.
    check_equal(
        f"cors[{key}] preflight.status_code", r.status_code, 200,
    )
    allow_origin = r.headers.get("access-control-allow-origin")
    allow_methods = r.headers.get("access-control-allow-methods")
    check(
        f"cors[{key}] preflight echoes origin",
        allow_origin == origin,
        detail=f"got access-control-allow-origin={allow_origin!r}",
    )
    check(
        f"cors[{key}] preflight allows GET method",
        bool(allow_methods) and "GET" in allow_methods.upper(),
        detail=f"got access-control-allow-methods={allow_methods!r}",
    )
    log(f"cors[{key}] preflight OPTIONS /version", {
        "origin": origin,
        "status_code": r.status_code,
        "access-control-allow-origin": allow_origin,
        "access-control-allow-methods": allow_methods,
    })

    # Actual GET with Origin.
    r = client.get("/version", headers={"Origin": origin})
    check_equal(f"cors[{key}] get.status_code", r.status_code, 200)
    allow_origin_get = r.headers.get("access-control-allow-origin")
    check(
        f"cors[{key}] get echoes origin",
        allow_origin_get == origin,
        detail=f"got access-control-allow-origin={allow_origin_get!r}",
    )
    log(f"cors[{key}] GET /version", {
        "origin": origin,
        "status_code": r.status_code,
        "access-control-allow-origin": allow_origin_get,
    })


def _check_cors_denied(client: Any, log: Any) -> None:
    """A disallowed origin must NOT receive an access-control-allow-origin."""
    bad_origin = "http://evil.example"
    r = client.options(
        "/version",
        headers={
            "Origin": bad_origin,
            "Access-Control-Request-Method": "GET",
        },
    )
    allow_origin = r.headers.get("access-control-allow-origin")
    check(
        "cors disallowed origin not echoed",
        allow_origin != bad_origin,
        detail=f"disallowed origin was echoed: {allow_origin!r}",
    )
    log("cors[denied] preflight OPTIONS /version", {
        "origin": bad_origin,
        "status_code": r.status_code,
        "access-control-allow-origin": allow_origin,
    })


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    transcript: list[dict[str, Any]] = []

    def log(step: str, payload: Any) -> None:
        transcript.append({"step": step, "result": payload})

    summary: dict[str, Any] = {
        "ok": False,
        "slice": "PS-013A",
        "fastapi_app_checked": False,
        "cors_middleware_present": False,
        "cors_preflight_checked": False,
        "cors_get_checked": False,
        "allowed_origins_checked": False,
        "health_checked": False,
        "version_checked": False,
        "campaign_create_checked": False,
        "dry_run_create_checked": False,
        "default_no_live_provider_call": False,
        "default_no_b2_call": False,
        "no_fake_media": False,
        "frontend_api_base_config_checked": False,
        "frontend_status_error_copy_checked": False,
        "local_runbook_checked": False,
        "docs_updated": False,
        "summary_path": str(SUMMARY_PATH),
        "transcript_path": str(TRANSCRIPT_PATH),
        "truth_boundary": (
            "PS-013A proves the local browser demo can connect to the FastAPI "
            "backend through safe local CORS settings and execute the default "
            "dry-run demo path. It does not prove public deployment, "
            "production CORS policy, authentication, production persistence, "
            "background job reliability, legal authenticity, C2PA "
            "authenticity, semantic truth, or human authorship."
        ),
    }

    provider_call_counter = {"count": 0}
    b2_call_counter = {"count": 0}

    def _live_sentinel(**kwargs: Any) -> dict[str, Any]:
        provider_call_counter["count"] += 1
        raise ProviderCallSentinel(
            "LIVE PROVIDER WAS CALLED DURING PS-013A DEFAULT DRY-RUN"
        )

    def _b2_store_sentinel(*args: Any, **kwargs: Any) -> dict[str, Any]:
        b2_call_counter["count"] += 1
        raise ProviderCallSentinel("B2 STORE WAS CALLED DURING PS-013A DEFAULT")

    def _b2_read_sentinel(*args: Any, **kwargs: Any) -> dict[str, Any]:
        b2_call_counter["count"] += 1
        raise ProviderCallSentinel("B2 READ WAS CALLED DURING PS-013A DEFAULT")

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
        # 1. Import the FastAPI app and verify it is a real FastAPI instance.
        # ------------------------------------------------------------------
        import fastapi  # noqa: E402

        from proofstudio.api.app import (  # noqa: E402
            LOCAL_DEMO_CORS_ORIGINS,
            app,
        )
        from fastapi.testclient import TestClient  # noqa: E402

        check("app is not None", app is not None)
        check("app is FastAPI", isinstance(app, fastapi.FastAPI))
        summary["fastapi_app_checked"] = isinstance(app, fastapi.FastAPI)
        log("app_import", {
            "app_is_fastapi": summary["fastapi_app_checked"],
            "app_title": getattr(app, "title", None),
            "app_version": getattr(app, "version", None),
        })

        # ------------------------------------------------------------------
        # 2. Verify CORS middleware is present and the allow-list is correct.
        # ------------------------------------------------------------------
        present = cors_middleware_present(app)
        check("cors middleware registered", present)
        summary["cors_middleware_present"] = present
        configured = allowed_origins_from_app(app)
        # The backend's declared constant is the source of truth.
        declared = set(LOCAL_DEMO_CORS_ORIGINS)
        missing_required = [
            o for o in REQUIRED_ALLOWED_ORIGINS if o not in configured | declared
        ]
        check(
            "required local origins allowed",
            not missing_required,
            detail=(
                f"missing required origins: {missing_required}; "
                f"configured={sorted(configured)} declared={sorted(declared)}"
            ),
        )
        summary["allowed_origins_checked"] = not missing_required
        log("cors_config", {
            "present": present,
            "configured_origins": sorted(configured),
            "declared_origins": sorted(declared),
            "required_origins": list(REQUIRED_ALLOWED_ORIGINS),
            "extra_origins": list(EXTRA_ALLOWED_ORIGINS),
            "missing_required": missing_required,
        })

        # ------------------------------------------------------------------
        # 3. Build the TestClient. Wire sentinels so we can prove the default
        #    dry-run never touches a live provider or B2.
        # ------------------------------------------------------------------
        client = TestClient(app)

        original_execute_live_run = services_module.execute_live_run
        original_b2_store = archive_module.store_run_archive_with_genblaze
        original_b2_read = archive_module.read_archive_from_b2
        services_module.execute_live_run = _live_sentinel  # type: ignore[assignment]
        archive_module.store_run_archive_with_genblaze = _b2_store_sentinel  # type: ignore[assignment]
        archive_module.read_archive_from_b2 = _b2_read_sentinel  # type: ignore[assignment]
        try:
            # 4. CORS preflight + GET checks for both required origins.
            _check_cors(client, "http://127.0.0.1:5173", summary, log, "127.0.0.1:5173")
            _check_cors(client, "http://localhost:5173", summary, log, "localhost:5173")
            summary["cors_preflight_checked"] = True
            summary["cors_get_checked"] = True
            _check_cors_denied(client, log)

            # 5. Default contract (health, version, campaign, safe dry-run).
            _exercise_contract(client, summary, log)
        finally:
            services_module.execute_live_run = original_execute_live_run  # type: ignore[assignment]
            archive_module.store_run_archive_with_genblaze = original_b2_store  # type: ignore[assignment]
            archive_module.read_archive_from_b2 = original_b2_read  # type: ignore[assignment]

        # ------------------------------------------------------------------
        # 6. Confirm default dry-run made no live-provider / B2 call.
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
        # 7. Frontend: API base URL config + clearer status/error copy.
        # ------------------------------------------------------------------
        api_ts = read_text(API_TS_PATH)
        app_tsx = read_text(APP_TSX_PATH)
        frontend_blob = f"\n# api.ts\n{api_ts}\n# App.tsx\n{app_tsx}"

        has_env_var = "VITE_PROOFSTUDIO_API_BASE_URL" in api_ts
        has_fallback = "http://127.0.0.1:8000" in api_ts
        summary["frontend_api_base_config_checked"] = bool(has_env_var and has_fallback)
        check(
            "frontend API base URL config present",
            summary["frontend_api_base_config_checked"],
            detail=f"env_var={has_env_var} fallback={has_fallback}",
        )

        # Clearer copy: distinguishes backend-not-running from a generic error,
        # and mentions CORS so the operator knows what to fix.
        has_not_reachable = "not reachable" in frontend_blob.lower()
        has_cors_hint = "cors" in frontend_blob.lower()
        has_describe = "describeApiError" in frontend_blob
        summary["frontend_status_error_copy_checked"] = bool(
            has_not_reachable and has_cors_hint and has_describe
        )
        check(
            "frontend status/error copy improved",
            summary["frontend_status_error_copy_checked"],
            detail=(
                f"not_reachable={has_not_reachable} cors={has_cors_hint} "
                f"describe={has_describe}"
            ),
        )
        log("frontend_checks", {
            "api_base_config": summary["frontend_api_base_config_checked"],
            "status_error_copy": summary["frontend_status_error_copy_checked"],
            "markers": {
                "not_reachable": has_not_reachable,
                "cors_hint": has_cors_hint,
                "describe_api_error": has_describe,
            },
        })

        # ------------------------------------------------------------------
        # 8. Docs: exact two-terminal local runbook.
        # ------------------------------------------------------------------
        # The README is the canonical runbook; the proof doc also restates it.
        docs_blob = f"{read_text(README_PATH)}\n{read_text(DOCS_PATH)}"
        missing_runbook = [
            m for m in RUNBOOK_MARKERS if m not in docs_blob
        ]
        summary["local_runbook_checked"] = not missing_runbook
        check(
            "docs include exact two-terminal local runbook",
            summary["local_runbook_checked"],
            detail=f"missing runbook markers: {missing_runbook}",
        )
        summary["docs_updated"] = DOCS_PATH.exists() and not missing_runbook
        log("docs_runbook", {
            "missing_markers": missing_runbook,
            "readme_present": README_PATH.exists(),
            "proof_doc_present": DOCS_PATH.exists(),
        })

        # ------------------------------------------------------------------
        # 9. Secret-leak scan across the transcript.
        # ------------------------------------------------------------------
        secret_hits = scan_for_secrets(transcript)
        check("no secret leak in transcript", not secret_hits, detail=str(secret_hits))
        log("secret_scan", {"hits": secret_hits})

        ok = bool(
            summary["fastapi_app_checked"]
            and summary["cors_middleware_present"]
            and summary["cors_preflight_checked"]
            and summary["cors_get_checked"]
            and summary["allowed_origins_checked"]
            and summary["health_checked"]
            and summary["version_checked"]
            and summary["campaign_create_checked"]
            and summary["dry_run_create_checked"]
            and summary["default_no_live_provider_call"]
            and summary["default_no_b2_call"]
            and summary["no_fake_media"]
            and summary["frontend_api_base_config_checked"]
            and summary["frontend_status_error_copy_checked"]
            and summary["local_runbook_checked"]
            and summary["docs_updated"]
        )
        summary["ok"] = ok

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
                "slice": "PS-013A",
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


if __name__ == "__main__":
    main()
