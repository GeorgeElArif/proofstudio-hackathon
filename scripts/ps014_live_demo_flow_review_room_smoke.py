#!/usr/bin/env python3
"""
PS-014: Live Demo Flow / End-to-End Review Room Path smoke test.

What this proves (default safe smoke):

- The Review Room frontend exists and references every required PS-012 contract
  endpoint.
- The UI keeps ``run_live`` OFF by default, shows the explicit live-mode
  warning, exposes a **Create Safe Dry Run** action and an explicit **Create
  Live Proof Run** action.
- The UI renders the Evidence Overview, Attempt Timeline, Assets, Manifest,
  Provenance Passport, and Truth Boundary panels, and contains no fake media
  success and no fake manifest success.
- The FastAPI backend still passes the default safe dry-run HTTP flow
  (health/version/campaign/dry-run/passport) and the default smoke does NOT
  call any live provider and does NOT call B2.
- The frontend production build passes (``npm run build``).

Optional explicit live smoke (``PROOFSTUDIO_PS014_LIVE=1``):

- Calls ``POST /runs`` with ``run_live=true`` against the real provider/B2
  chain (only when credentials are configured).
- Verifies the run status is ``live_completed``, ``live_failed``, or
  ``live_blocked``.
- If completed: ``selected_provider`` and ``selected_model`` exist, attempts and
  assets exist, a manifest exists, the passport exists, and
  ``stored_manifest_verify`` is true.
- If failed/blocked: no fake media, no fake manifest, a clear failure state.

Default acceptance NEVER requires live provider spend. Historical proof scripts
(PS-004 .. PS-013A) are not modified.

Truth boundary: PS-014 proves ProofStudio has a local end-to-end Review Room
demo path for safe dry-runs and explicit live proof runs. It does not prove
public deployment, production availability, authentication, production
persistence, background job reliability, legal authenticity, C2PA
authenticity, semantic truth, or human authorship.
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
    RUN_STATUS_LIVE_BLOCKED,
    RUN_STATUS_LIVE_COMPLETED,
    RUN_STATUS_LIVE_FAILED,
)

OUTPUT_DIR = Path("/tmp/proofstudio-ps-014")
SUMMARY_PATH = OUTPUT_DIR / "live-demo-flow-review-room-summary.json"
TRANSCRIPT_PATH = OUTPUT_DIR / "live-demo-flow-review-room-transcript.json"

FRONTEND_DIR = REPO_ROOT / "apps" / "web"
APP_TSX_PATH = FRONTEND_DIR / "src" / "App.tsx"
API_TS_PATH = FRONTEND_DIR / "src" / "api.ts"
STYLES_CSS_PATH = FRONTEND_DIR / "src" / "styles.css"
PACKAGE_JSON_PATH = FRONTEND_DIR / "package.json"
README_PATH = FRONTEND_DIR / "README.md"

LIVE_WARNING = "Live mode may call external providers and B2."

# Required PS-012 contract endpoint path fragments the frontend must reference.
REQUIRED_ENDPOINT_FRAGMENTS: tuple[str, ...] = (
    "/health",
    "/version",
    "/campaigns",
    "/runs/${",  # api.ts uses template literals for /runs/{run_id}/...
    "/runs/${runId}/attempts",
    "/runs/${runId}/assets",
    "/runs/${runId}/manifest",
    "/runs/${runId}/passport",
    "/campaigns/${campaignId}",
)

# UI section markers that must be present in App.tsx.
REQUIRED_SECTIONS: dict[str, str] = {
    "evidence_overview": "Evidence Overview",
    "attempts": "Attempt Timeline",
    "assets": "Assets",
    "manifest": "Manifest",
    "passport": "Provenance Passport",
    "trust_boundary": "Truth Boundary",
}

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
    "scripts/ps013a_local_demo_integration_hardening_smoke.py",
)

SECRET_PATTERNS = [
    re.compile(r"(?i)Bearer\s+[A-Za-z0-9\-_.=~]{8,}"),
    re.compile(r"(?i)B2_KEY_ID[\s:=]+\S{8,}"),
    re.compile(r"(?i)B2_APP_KEY[\s:=]+\S{8,}"),
    re.compile(r"(?i)CLOUDFLARE_API_TOKEN[\s:=]+\S{8,}"),
    re.compile(r"(?i)GEMINI_API_KEY[\s:=]+\S{8,}"),
]

# Patterns that would indicate the UI fabricates media/manifest success at the
# source level. Their absence (combined with the runtime dry-run contract) is
# the no-fake proof.
FAKE_MEDIA_PATTERNS = [
    re.compile(r"data:image/[^\"')]+\w"),  # inline data-URI media
    re.compile(r"produced_real_media\s*[:=]\s*true"),  # UI claiming real media
]
FAKE_MANIFEST_PATTERNS = [
    # UI hardcoding a manifest URI as if verification succeeded.
    re.compile(r'manifest[_-]?uri\s*[:=]\s*["\']https?://'),
    re.compile(r'stored[_-]?manifest[_-]?verify\s*[:=]\s*true'),
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


class ProviderCallSentinel(Exception):
    pass


def _exercise_safe_dry_run_contract(
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
    log("GET /health", {"status_code": r.status_code, "ok": body.get("ok")})

    # --- version ---
    r = client.get("/version")
    body = _body(r)
    check_equal("version.status_code", r.status_code, 200)
    check("version.framework_mode", bool(body.get("framework_mode")))
    log("GET /version", {
        "status_code": r.status_code,
        "framework_mode": body.get("framework_mode"),
        "capabilities": body.get("capabilities"),
    })

    # --- create campaign ---
    campaign_payload = {
        "name": "PS-014 Live Demo Flow Review Room Campaign",
        "brief": (
            "Prove the Review Room UI supports the complete product demo path: "
            "create campaign, safe dry-run by default, explicit live mode, "
            "live proof run, evidence/attempts/assets/manifest/passport, and "
            "the truth boundary. Default smoke must not call providers or B2."
        ),
        "target_audience": "hackathon judges and reviewers",
        "platform": "web",
        "objective": "validate the live demo flow review room path",
    }
    r = client.post("/campaigns", json=campaign_payload)
    body = _body(r)
    check_equal("create_campaign.status_code", r.status_code, 201)
    campaign_id = body.get("campaign_id")
    check("create_campaign.campaign_id", bool(campaign_id))
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
    log("POST /runs (dry-run)", {
        "status_code": r.status_code,
        "run_id": run_id,
        "status": run_record.get("status"),
    })

    # --- readbacks: run / attempts / assets / manifest / passport ---
    r = client.get(f"/runs/{run_id}")
    body = _body(r)
    run_readback = body.get("run") or {}
    check_equal("get_run.status", run_readback.get("status"), RUN_STATUS_DRY_RUN_CREATED)
    check_equal("get_run.attempt_count", run_readback.get("attempt_count"), 0)
    check_equal("get_run.asset_count", run_readback.get("asset_count"), 0)
    log("GET /runs/{id}", {
        "status_code": r.status_code,
        "status": run_readback.get("status"),
        "attempt_count": run_readback.get("attempt_count"),
        "asset_count": run_readback.get("asset_count"),
    })

    r = client.get(f"/runs/{run_id}/attempts")
    body = _body(r)
    check_equal("get_attempts.attempt_count", body.get("attempt_count"), 0)

    r = client.get(f"/runs/{run_id}/assets")
    body = _body(r)
    check_equal("get_assets.asset_count", body.get("asset_count"), 0)

    r = client.get(f"/runs/{run_id}/manifest")
    body = _body(r)
    check_equal("get_manifest.ready", body.get("ready"), False)
    check("get_manifest.not_ready_reason", bool(body.get("not_ready_reason")))
    log("GET /runs/{id}/manifest", {
        "ready": body.get("ready"),
        "not_ready_reason": body.get("not_ready_reason"),
    })

    r = client.get(f"/runs/{run_id}/passport")
    body = _body(r)
    generation = body.get("generation_summary") or {}
    check_equal(
        "passport.no generated media",
        generation.get("generated_media_present"),
        False,
    )
    archive = body.get("archive_and_rehydration") or {}
    check("passport.archive not available", archive.get("status") != "available")
    check("passport.trust_boundary present", bool(body.get("trust_boundary")))
    log("GET /runs/{id}/passport", {
        "generated_media_present": generation.get("generated_media_present"),
        "archive_status": archive.get("status"),
        "trust_boundary_present": bool(body.get("trust_boundary")),
    })
    summary["passport_checked"] = True

    # Dry-run produces no fake media/manifest by design.
    summary["no_fake_media"] = True
    summary["no_fake_manifest"] = True
    summary["safe_api_flow_checked"] = True


def _check_frontend_source(summary: dict[str, Any], log: Any) -> None:
    """Static checks over the Review Room frontend source."""
    app_tsx = read_text(APP_TSX_PATH)
    api_ts = read_text(API_TS_PATH)
    styles = read_text(STYLES_CSS_PATH)
    frontend_blob = f"{app_tsx}\n{api_ts}\n{styles}"

    # Frontend files exist.
    check("App.tsx present", bool(app_tsx), detail="App.tsx missing")
    check("api.ts present", bool(api_ts), detail="api.ts missing")
    check("styles.css present", bool(styles), detail="styles.css missing")

    # 3. Explicit live mode warning.
    has_warning = LIVE_WARNING in app_tsx
    check("live mode warning present", has_warning, detail="warning text missing")
    summary["live_mode_warning_present"] = has_warning

    # 4. Default run_live is false (toggle starts unchecked).
    has_default_false = re.search(
        r"const\s+\[runLive,\s*setRunLive\]\s*=\s*useState\(false\)", app_tsx,
    ) is not None
    check(
        "default run_live is false",
        has_default_false,
        detail="runLive useState(false) not found",
    )
    summary["default_safe_mode_checked"] = has_default_false

    # 5. Safe dry-run action visible + 6. explicit live proof run action.
    has_safe_dry_run = "Create Safe Dry Run" in app_tsx
    has_live_proof_run = "Create Live Proof Run" in app_tsx
    check("safe dry-run action present", has_safe_dry_run)
    check("live proof run action present", has_live_proof_run)
    summary["safe_dry_run_action_present"] = has_safe_dry_run
    summary["live_run_action_present"] = has_live_proof_run

    # Live mode is explicit: the live button must be gated behind runLive.
    has_explicit_gate = (
        'disabled={runBusy || !runLive}' in app_tsx
        and "handleCreateRun(true)" in app_tsx
    )
    check("live mode explicit opt-in", has_explicit_gate)
    summary["live_mode_explicit_checked"] = has_explicit_gate

    # 7. All required endpoints referenced (in api.ts).
    missing_endpoints = [
        frag for frag in REQUIRED_ENDPOINT_FRAGMENTS if frag not in api_ts
    ]
    check(
        "all required endpoints referenced",
        not missing_endpoints,
        detail=f"missing endpoint fragments: {missing_endpoints}",
    )
    summary["api_endpoints_referenced"] = not missing_endpoints

    # 8-13. Required UI sections present.
    for key, marker in REQUIRED_SECTIONS.items():
        present = marker in app_tsx
        check(f"section {key} present", present, detail=f"marker {marker!r} missing")
        if key == "evidence_overview":
            summary["evidence_overview_present"] = present
        elif key == "attempts":
            summary["attempts_panel_present"] = present
        elif key == "assets":
            summary["assets_panel_present"] = present
        elif key == "manifest":
            summary["manifest_panel_present"] = present
        elif key == "passport":
            summary["passport_panel_present"] = present
        elif key == "trust_boundary":
            summary["trust_boundary_present"] = present

    # 14/15. No fake media / no fake manifest success at the source level.
    fake_media_hits = [
        p.pattern for p in FAKE_MEDIA_PATTERNS if p.search(frontend_blob)
    ]
    fake_manifest_hits = [
        p.pattern for p in FAKE_MANIFEST_PATTERNS if p.search(frontend_blob)
    ]
    # The no_fake flags are set true only if BOTH the source is clean AND the
    # runtime contract confirms zero assets / no media (runtime part set later).
    summary["_source_no_fake_media"] = not fake_media_hits
    summary["_source_no_fake_manifest"] = not fake_manifest_hits
    check("no fake media in source", not fake_media_hits, detail=str(fake_media_hits))
    check(
        "no fake manifest in source",
        not fake_manifest_hits,
        detail=str(fake_manifest_hits),
    )

    # Asset preview honesty: the UI must attempt a preview only for image assets
    # with a URL and must fall back to metadata-only on load failure (onError).
    has_preview = "AssetPreview" in app_tsx and "onError" in app_tsx
    has_metadata_only_fallback = (
        "metadata only" in app_tsx.lower() or "metadata-only" in app_tsx.lower()
    )
    check(
        "asset preview is honest (onError fallback, no placeholder)",
        has_preview and has_metadata_only_fallback,
        detail=f"preview={has_preview} fallback={has_metadata_only_fallback}",
    )

    log("frontend_source_checks", {
        "live_warning": summary["live_mode_warning_present"],
        "default_safe": summary["default_safe_mode_checked"],
        "safe_dry_run_action": summary["safe_dry_run_action_present"],
        "live_proof_run_action": summary["live_run_action_present"],
        "live_explicit_gate": summary["live_mode_explicit_checked"],
        "endpoints_referenced": summary["api_endpoints_referenced"],
        "sections": {
            k: summary[f"{k}_present"]
            for k in (
                "evidence_overview",
                "attempts_panel",
                "assets_panel",
                "manifest_panel",
                "passport_panel",
                "trust_boundary",
            )
        },
        "source_no_fake_media": summary["_source_no_fake_media"],
        "source_no_fake_manifest": summary["_source_no_fake_manifest"],
        "asset_preview_honest": has_preview and has_metadata_only_fallback,
    })


def _check_frontend_build(summary: dict[str, Any], log: Any) -> None:
    """Run the frontend production build and record its status."""
    summary["frontend_build_checked"] = True
    npm_cmd = os.environ.get("PS014_NPM", "npm")
    try:
        result = subprocess.run(
            [npm_cmd, "run", "build"],
            cwd=str(FRONTEND_DIR),
            capture_output=True,
            text=True,
            timeout=180.0,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        summary["frontend_build_status"] = f"error: {exc}"
        log("frontend_build", {"status": "error", "error": str(exc)})
        raise CheckFail(f"frontend build could not run: {exc}")

    status = "passed" if result.returncode == 0 else "failed"
    summary["frontend_build_status"] = status
    log("frontend_build", {
        "command": f"{npm_cmd} run build",
        "returncode": result.returncode,
        "status": status,
        "stdout_tail": (result.stdout or "")[-1200:],
        "stderr_tail": (result.stderr or "")[-1200:],
    })
    check(
        "frontend build passed",
        result.returncode == 0,
        detail=f"npm run build exit={result.returncode}",
    )


def _run_optional_live_smoke(summary: dict[str, Any], log: Any) -> None:
    """Optional explicit live proof run. Only when PROOFSTUDIO_PS014_LIVE=1."""
    from fastapi.testclient import TestClient  # noqa: E402

    from proofstudio.api.app import app  # noqa: E402

    check("live smoke: app available", app is not None)
    client = TestClient(app)  # NO sentinels: live mode is allowed to call out.

    # Create a campaign for the live run.
    r = client.post(
        "/campaigns",
        json={
            "name": "PS-014 Explicit Live Proof Run Campaign",
            "brief": "Optional explicit live proof run for PS-014.",
            "platform": "web",
            "objective": "validate live demo flow end-to-end",
        },
    )
    check_equal("live create_campaign.status_code", r.status_code, 201)
    campaign_id = r.json().get("campaign_id")
    check("live create_campaign.campaign_id", bool(campaign_id))

    r = client.post(
        "/runs",
        json={
            "campaign_id": campaign_id,
            "prompt": "A small proof image for the PS-014 live demo flow.",
            "budget_mode": "free-only",
            "run_live": True,
        },
    )
    check_equal("live create_run.status_code", r.status_code, 201)
    body = r.json()
    run_id = body.get("run_id")
    check("live create_run.run_id", bool(run_id))
    run = body.get("run") or {}
    status = run.get("status")
    log("live POST /runs (run_live=true)", {
        "run_id": run_id,
        "status": status,
        "selected_provider": run.get("selected_provider"),
        "selected_model": run.get("selected_model"),
    })

    acceptable = {
        RUN_STATUS_LIVE_COMPLETED,
        RUN_STATUS_LIVE_FAILED,
        RUN_STATUS_LIVE_BLOCKED,
    }
    check(
        "live run status is completed/failed/blocked",
        status in acceptable,
        detail=f"status={status!r}",
    )
    summary["live_run_status"] = status
    summary["live_run_completed"] = status == RUN_STATUS_LIVE_COMPLETED

    if status == RUN_STATUS_LIVE_COMPLETED:
        # selected_provider / selected_model exist.
        provider = run.get("selected_provider")
        model = run.get("selected_model")
        check("live completed: selected_provider exists", bool(provider))
        check("live completed: selected_model exists", bool(model))
        summary["selected_provider"] = provider
        summary["selected_model"] = model

        # attempts exist.
        r = client.get(f"/runs/{run_id}/attempts")
        attempts_body = r.json()
        attempts = attempts_body.get("attempts") or []
        check("live completed: attempts exist", len(attempts) > 0)
        log("live attempts", {"count": len(attempts)})

        # assets exist.
        r = client.get(f"/runs/{run_id}/assets")
        assets_body = r.json()
        assets = assets_body.get("assets") or []
        check("live completed: assets exist", len(assets) > 0)
        log("live assets", {"count": len(assets)})

        # manifest exists + stored_manifest_verify true.
        r = client.get(f"/runs/{run_id}/manifest")
        manifest_body = r.json()
        check_equal("live manifest.ready", manifest_body.get("ready"), True)
        check_equal(
            "live manifest.stored_manifest_verify",
            manifest_body.get("stored_manifest_verify"),
            True,
        )
        summary["manifest_uri"] = manifest_body.get("manifest_uri")
        log("live manifest", {
            "ready": manifest_body.get("ready"),
            "manifest_uri": manifest_body.get("manifest_uri"),
            "stored_manifest_verify": manifest_body.get("stored_manifest_verify"),
        })

        # passport exists.
        r = client.get(f"/runs/{run_id}/passport")
        check_equal("live passport.status_code", r.status_code, 200)
        passport_body = r.json()
        gen = passport_body.get("generation_summary") or {}
        check_equal(
            "live passport.generated_media_present",
            gen.get("generated_media_present"),
            True,
        )
        summary["passport_checked"] = True
        log("live passport", {
            "generated_media_present": gen.get("generated_media_present"),
            "trust_boundary_present": bool(passport_body.get("trust_boundary")),
        })
    else:
        # failed / blocked: honest failure state, no fake media/manifest.
        r = client.get(f"/runs/{run_id}/assets")
        assets = (r.json() or {}).get("assets") or []
        r = client.get(f"/runs/{run_id}/manifest")
        manifest = r.json() or {}
        check(
            "live failed/blocked: no fake media",
            not assets or all(
                not (a.get("produced_real_media")) for a in assets
            ),
        )
        check(
            "live failed/blocked: no fake manifest",
            manifest.get("ready") is not True,
        )
        # passport still explains the failure honestly.
        r = client.get(f"/runs/{run_id}/passport")
        check_equal("live failed/blocked passport.status_code", r.status_code, 200)
        summary["passport_checked"] = True
        log("live failed/blocked", {
            "status": status,
            "asset_count": len(assets),
            "manifest_ready": manifest.get("ready"),
            "blocked_reason": run.get("blocked_reason"),
            "error": run.get("error"),
        })


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    transcript: list[dict[str, Any]] = []

    def log(step: str, payload: Any) -> None:
        transcript.append({"step": step, "result": payload})

    summary: dict[str, Any] = {
        "ok": False,
        "slice": "PS-014",
        "frontend_path": str(FRONTEND_DIR.relative_to(REPO_ROOT)),
        "default_safe_mode_checked": False,
        "live_mode_explicit_checked": False,
        "live_mode_warning_present": False,
        "safe_dry_run_action_present": False,
        "live_run_action_present": False,
        "api_endpoints_referenced": False,
        "evidence_overview_present": False,
        "attempts_panel_present": False,
        "assets_panel_present": False,
        "manifest_panel_present": False,
        "passport_panel_present": False,
        "trust_boundary_present": False,
        "default_no_live_provider_call": False,
        "default_no_b2_call": False,
        "no_fake_media": False,
        "no_fake_manifest": False,
        "frontend_build_checked": False,
        "frontend_build_status": "not_run",
        "safe_api_flow_checked": False,
        "live_mode_enabled": False,
        "live_run_status": None,
        "live_run_completed": False,
        "selected_provider": None,
        "selected_model": None,
        "manifest_uri": None,
        "passport_checked": False,
        "summary_path": str(SUMMARY_PATH),
        "transcript_path": str(TRANSCRIPT_PATH),
        "truth_boundary": (
            "PS-014 proves ProofStudio has a local end-to-end Review Room demo "
            "path for safe dry-runs and explicit live proof runs. It does not "
            "prove public deployment, production availability, authentication, "
            "production persistence, background job reliability, legal "
            "authenticity, C2PA authenticity, semantic truth, or human "
            "authorship."
        ),
    }

    provider_call_counter = {"count": 0}
    b2_call_counter = {"count": 0}

    def _live_sentinel(**kwargs: Any) -> dict[str, Any]:
        provider_call_counter["count"] += 1
        raise ProviderCallSentinel(
            "LIVE PROVIDER WAS CALLED DURING PS-014 DEFAULT SAFE SMOKE"
        )

    def _b2_store_sentinel(*args: Any, **kwargs: Any) -> dict[str, Any]:
        b2_call_counter["count"] += 1
        raise ProviderCallSentinel("B2 STORE WAS CALLED DURING PS-014 DEFAULT")

    def _b2_read_sentinel(*args: Any, **kwargs: Any) -> dict[str, Any]:
        b2_call_counter["count"] += 1
        raise ProviderCallSentinel("B2 READ WAS CALLED DURING PS-014 DEFAULT")

    live_enabled = os.environ.get("PROOFSTUDIO_PS014_LIVE") == "1"
    summary["live_mode_enabled"] = live_enabled

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
        # 1. Frontend source checks (sections, warnings, endpoints, no-fake).
        # ------------------------------------------------------------------
        _check_frontend_source(summary, log)

        # ------------------------------------------------------------------
        # 2. Default safe dry-run HTTP contract via TestClient + sentinels.
        # ------------------------------------------------------------------
        import fastapi  # noqa: E402

        from proofstudio.api.app import app  # noqa: E402
        from fastapi.testclient import TestClient  # noqa: E402

        check("app is not None", app is not None)
        check("app is FastAPI", isinstance(app, fastapi.FastAPI))
        log("app_import", {
            "app_is_fastapi": isinstance(app, fastapi.FastAPI),
            "app_title": getattr(app, "title", None),
        })

        client = TestClient(app)
        original_execute_live_run = services_module.execute_live_run
        original_b2_store = archive_module.store_run_archive_with_genblaze
        original_b2_read = archive_module.read_archive_from_b2
        services_module.execute_live_run = _live_sentinel  # type: ignore[assignment]
        archive_module.store_run_archive_with_genblaze = _b2_store_sentinel  # type: ignore[assignment]
        archive_module.read_archive_from_b2 = _b2_read_sentinel  # type: ignore[assignment]
        try:
            _exercise_safe_dry_run_contract(client, summary, log)
        finally:
            services_module.execute_live_run = original_execute_live_run  # type: ignore[assignment]
            archive_module.store_run_archive_with_genblaze = original_b2_store  # type: ignore[assignment]
            archive_module.read_archive_from_b2 = original_b2_read  # type: ignore[assignment]

        # ------------------------------------------------------------------
        # 3. Confirm the default smoke made no live-provider / B2 call.
        # ------------------------------------------------------------------
        check_equal(
            "no live provider call during default smoke",
            provider_call_counter["count"],
            0,
        )
        check_equal(
            "no B2 call during default smoke",
            b2_call_counter["count"],
            0,
        )
        summary["default_no_live_provider_call"] = provider_call_counter["count"] == 0
        summary["default_no_b2_call"] = b2_call_counter["count"] == 0
        # Combine source + runtime no-fake proof.
        summary["no_fake_media"] = bool(
            summary.get("_source_no_fake_media", False)
        )
        summary["no_fake_manifest"] = bool(
            summary.get("_source_no_fake_manifest", False)
        )
        log("call_sentinels", {
            "provider_calls": provider_call_counter["count"],
            "b2_calls": b2_call_counter["count"],
        })

        # ------------------------------------------------------------------
        # 4. Frontend production build passes.
        # ------------------------------------------------------------------
        _check_frontend_build(summary, log)

        # ------------------------------------------------------------------
        # 5. Optional explicit live proof run.
        # ------------------------------------------------------------------
        if live_enabled:
            _run_optional_live_smoke(summary, log)
            log("live_mode", {"enabled": True, "status": summary["live_run_status"]})
        else:
            log("live_mode", {"enabled": False, "note": "skipped (default safe)"})

        # ------------------------------------------------------------------
        # 6. Secret-leak scan across the transcript.
        # ------------------------------------------------------------------
        secret_hits = scan_for_secrets(transcript)
        check("no secret leak in transcript", not secret_hits, detail=str(secret_hits))
        log("secret_scan", {"hits": secret_hits})

        # ------------------------------------------------------------------
        # 7. Acceptance: every required field must be true / satisfied.
        # ------------------------------------------------------------------
        required_true = (
            summary["default_safe_mode_checked"],
            summary["live_mode_explicit_checked"],
            summary["live_mode_warning_present"],
            summary["safe_dry_run_action_present"],
            summary["live_run_action_present"],
            summary["api_endpoints_referenced"],
            summary["evidence_overview_present"],
            summary["attempts_panel_present"],
            summary["assets_panel_present"],
            summary["manifest_panel_present"],
            summary["passport_panel_present"],
            summary["trust_boundary_present"],
            summary["default_no_live_provider_call"],
            summary["default_no_b2_call"],
            summary["no_fake_media"],
            summary["no_fake_manifest"],
            summary["frontend_build_checked"],
            summary["frontend_build_status"] == "passed",
            summary["safe_api_flow_checked"],
            summary["passport_checked"],
        )
        # Live mode, when enabled, must additionally produce a terminal status.
        live_ok = True
        if live_enabled:
            live_ok = summary["live_run_status"] in (
                RUN_STATUS_LIVE_COMPLETED,
                RUN_STATUS_LIVE_FAILED,
                RUN_STATUS_LIVE_BLOCKED,
            )

        ok = bool(all(required_true) and live_ok)
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

    # Drop private helper keys before writing the summary.
    for key in list(summary.keys()):
        if key.startswith("_"):
            summary.pop(key, None)

    summary["written_at"] = now_iso()

    SUMMARY_PATH.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    TRANSCRIPT_PATH.write_text(
        json.dumps(
            {
                "slice": "PS-014",
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
