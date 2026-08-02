#!/usr/bin/env python3
"""
PS-017: Public Deployment Prep + Environment Hardening smoke test.

What this proves (docs + env template + tiny CORS/env compatibility fix + smoke;
NO live providers, NO B2):

- All required deployment docs exist.
- `.env.production.example` exists and contains placeholders only.
- `.env.production.example` includes every required production env key.
- No real secrets appear in the env template or deployment docs.
- The CORS docs explain local vs production origins, reject wildcard production
  CORS, and document the frontend API base URL strategy.
- The platform decision is marked pending unless a platform is actually
  selected (it is not, in this slice).
- The preflight checklist includes both before-deploy and after-deploy checks.
- The backend can still import the FastAPI app and the tiny CORS/env reader
  works (local preserved, production merged, wildcard refused).
- `/health` and `/version` work through FastAPI's TestClient.
- A default safe dry-run still avoids providers and B2 (status
  `dry_run_created`, no attempts, no assets, no manifest).
- The frontend production build passes.
- No historical proof scripts are modified.
- No backend changes beyond the explicitly-allowed tiny CORS/env reader.

Default acceptance NEVER calls live providers or B2.

Truth boundary: PS-017 proves ProofStudio has deployment preparation,
environment templates, and preflight checks for moving from local demo to public
hosting. It does not prove public deployment, a working public app URL, final
Devpost submission, production availability, authentication, production
persistence, background job reliability, legal authenticity, C2PA authenticity,
semantic truth, or human authorship.
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

OUTPUT_DIR = Path("/tmp/proofstudio-ps-017")
SUMMARY_PATH = OUTPUT_DIR / "deployment-prep-summary.json"
TRANSCRIPT_PATH = OUTPUT_DIR / "deployment-prep-transcript.json"

DEPLOYMENT_DIR = REPO_ROOT / "docs" / "deployment"
PROOF_DOC = (
    REPO_ROOT
    / "docs"
    / "ps-017-public-deployment-prep-env-hardening-proof.md"
)
ENV_TEMPLATE = REPO_ROOT / ".env.production.example"
FRONTEND_DIR = REPO_ROOT / "apps" / "web"
SRC_DIR = REPO_ROOT / "src"

TRUTH_BOUNDARY = (
    "PS-017 proves ProofStudio has deployment preparation, environment "
    "templates, and preflight checks for moving from local demo to public "
    "hosting. It does not prove public deployment, a working public app URL, "
    "final Devpost submission, production availability, authentication, "
    "production persistence, background job reliability, legal authenticity, "
    "C2PA authenticity, semantic truth, or human authorship."
)

REQUIRED_DEPLOYMENT_DOCS = (
    "README.md",
    "environment.md",
    "cors-and-security.md",
    "platform-decision.md",
    "preflight-checklist.md",
)

# Every required key that must appear in .env.production.example. The smoke
# checks the key name is present as `KEY=` (the file format). Values must be
# placeholders.
REQUIRED_ENV_KEYS = (
    "PROOFSTUDIO_ENV",
    "PROOFSTUDIO_API_HOST",
    "PROOFSTUDIO_API_PORT",
    "PROOFSTUDIO_PUBLIC_API_BASE_URL",
    "PROOFSTUDIO_PUBLIC_WEB_URL",
    "PROOFSTUDIO_CORS_ORIGINS",
    "VITE_PROOFSTUDIO_API_BASE_URL",
    "PROOFSTUDIO_RUN_LIVE_DEFAULT",
)

OPTIONAL_ENV_KEYS = (
    "B2_BUCKET",
    "B2_REGION",
    "B2_KEY_ID",
    "B2_APP_KEY",
    "CLOUDFLARE_ACCOUNT_ID",
    "CLOUDFLARE_API_TOKEN",
    "GEMINI_API_KEY",
    "ELEVENLABS_API_KEY",
)

# Values that are acceptable placeholders in .env.production.example. Anything
# else on the right-hand side of a KEY= line is treated as a potential secret.
PLACEHOLDER_VALUES = {
    "production",
    "0.0.0.0",
    "8000",
    "false",
    "replace-me",
    "https://replace-with-api-host",
    "https://replace-with-web-host",
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
    "scripts/ps014_live_demo_flow_review_room_smoke.py",
    "scripts/ps015_demo_seed_pack_one_click_smoke.py",
    "scripts/ps016_submission_evidence_pack_smoke.py",
)

# Backend files that PS-017 is allowed to touch (the tiny CORS/env reader).
ALLOWED_BACKEND_PATHS = ("src/proofstudio/api/app.py",)

# Real-secret patterns. These match assignments whose value is NOT a known
# placeholder and looks long/complex enough to be a real credential.
SECRET_KEY_PATTERNS = (
    "B2_KEY_ID",
    "B2_APP_KEY",
    "CLOUDFLARE_API_TOKEN",
    "GEMINI_API_KEY",
    "ELEVENLABS_API_KEY",
    "GMI_API_KEY",
)

# A real-looking secret value: long, mixed-case/digit token, NOT a placeholder.
REAL_SECRET_VALUE = re.compile(r"^[A-Za-z0-9_\-]{16,}$")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class CheckFail(Exception):
    pass


def check(label: str, condition: bool, detail: str = "") -> None:
    if not condition:
        raise CheckFail(f"{label}: {detail}" if detail else f"{label}: failed")


def _log(transcript: list[dict[str, Any]], step: str, payload: Any) -> None:
    transcript.append({"step": step, "result": payload, "at": now_iso()})


def _read(path: Path) -> str:
    check(f"file exists: {path}", path.is_file(), detail=str(path))
    return path.read_text(encoding="utf-8")


def _git_modified(paths: tuple[str, ...]) -> list[str]:
    """Return the subset of `paths` git sees as modified/added (empty == clean)."""
    if not paths:
        return []
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "--", *paths],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=10.0,
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


def _parse_env_assignments(text: str) -> dict[str, str]:
    """Return {KEY: value} for non-comment, non-blank KEY=value lines."""
    out: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            out[key] = value
    return out


def _scan_secrets(text: str) -> list[str]:
    """Detect real-looking secret values in arbitrary text."""
    hits: list[str] = []
    for pattern in (
        re.compile(r"(?i)Bearer\s+[A-Za-z0-9\-_.=~]{8,}"),
        re.compile(r"(?i)backblazeb2\.com"),
    ):
        if pattern.search(text):
            hits.append(pattern.pattern[:60])
    return hits


def _check_deployment_docs_exist(
    summary: dict[str, Any], transcript: list[dict[str, Any]]
) -> None:
    created: list[str] = []
    for doc in REQUIRED_DEPLOYMENT_DOCS:
        path = DEPLOYMENT_DIR / doc
        check(f"deployment doc exists: {doc}", path.is_file(), detail=str(path))
        created.append(f"docs/deployment/{doc}")
    check("proof doc exists", PROOF_DOC.is_file(), detail=str(PROOF_DOC))
    created.append(str(PROOF_DOC.relative_to(REPO_ROOT)))
    created.append("scripts/ps017_deployment_prep_smoke.py")
    summary["deployment_docs_created_paths"] = created
    summary["deployment_docs_created"] = bool(
        created and all((REPO_ROOT / p).exists() for p in created)
    )
    _log(transcript, "deployment_docs_exist", {"docs": created})


def _check_env_template(
    summary: dict[str, Any], transcript: list[dict[str, Any]]
) -> None:
    summary["env_template_checked"] = True
    text = _read(ENV_TEMPLATE)
    assignments = _parse_env_assignments(text)
    check("env template has at least one assignment", bool(assignments))

    # Required keys present.
    missing = [k for k in REQUIRED_ENV_KEYS if k not in assignments]
    check("env template has all required keys", not missing, detail=str(missing))
    summary["required_env_keys_checked"] = not missing
    summary["required_env_keys_items"] = list(REQUIRED_ENV_KEYS)

    # Optional keys present (placeholders only).
    missing_optional = [k for k in OPTIONAL_ENV_KEYS if k not in assignments]
    summary["optional_env_keys_items"] = list(OPTIONAL_ENV_KEYS)
    # Optional keys are recommended but not strictly required to all be present.
    # Still, the template provides them; flag if any are missing.
    check(
        "env template has all optional placeholder keys",
        not missing_optional,
        detail=str(missing_optional),
    )

    # Every value must be a known placeholder. Anything else looks like a secret.
    bad_values: dict[str, str] = {}
    for key, value in assignments.items():
        if value in PLACEHOLDER_VALUES:
            continue
        # Allow an https URL that's still a placeholder host.
        if value.startswith("https://") and "replace-with" in value:
            continue
        bad_values[key] = value
    check(
        "env template values are placeholders only",
        not bad_values,
        detail=str(bad_values),
    )

    # Specifically: secret-like keys must NOT carry a real-looking token.
    real_secret_hits: list[str] = []
    for key in SECRET_KEY_PATTERNS:
        if key in assignments:
            value = assignments[key]
            if value in PLACEHOLDER_VALUES:
                continue
            if REAL_SECRET_VALUE.match(value):
                real_secret_hits.append(key)
    check(
        "env template has no real secret values",
        not real_secret_hits,
        detail=str(real_secret_hits),
    )
    summary["env_template_no_real_secrets"] = not real_secret_hits

    # PROOFSTUDIO_RUN_LIVE_DEFAULT must be false.
    check(
        "PROOFSTUDIO_RUN_LIVE_DEFAULT is false in template",
        assignments.get("PROOFSTUDIO_RUN_LIVE_DEFAULT") == "false",
        detail=str(assignments.get("PROOFSTUDIO_RUN_LIVE_DEFAULT")),
    )

    _log(transcript, "env_template_check", {
        "missing_required": missing,
        "missing_optional": missing_optional,
        "bad_values": bad_values,
        "real_secret_hits": real_secret_hits,
        "run_live_default": assignments.get("PROOFSTUDIO_RUN_LIVE_DEFAULT"),
    })


def _check_cors_docs(
    summary: dict[str, Any], transcript: list[dict[str, Any]]
) -> None:
    text = _read(DEPLOYMENT_DIR / "cors-and-security.md")
    low = text.lower()
    required_tokens = (
        "production cors",
        "wildcard",
        "proofstudio_cors_origins",
        "allow_credentials",
        "vite_proofstudio_api_base_url",
    )
    missing = [t for t in required_tokens if t not in low]
    check("cors docs cover required tokens", not missing, detail=str(missing))
    # Must explicitly say wildcard production CORS is unsafe / refused.
    check(
        "cors docs reject wildcard production CORS",
        "unsafe" in low or "refus" in low or "never" in low,
        detail="must say wildcard production CORS is unsafe/refused",
    )
    summary["cors_strategy_checked"] = True
    _log(transcript, "cors_docs_check", {"missing_tokens": missing})


def _check_frontend_api_base_strategy(
    summary: dict[str, Any], transcript: list[dict[str, Any]]
) -> None:
    # Documented in cors-and-security.md and environment.md.
    cors_text = _read(DEPLOYMENT_DIR / "cors-and-security.md").lower()
    env_text = _read(DEPLOYMENT_DIR / "environment.md").lower()
    required = (
        "vite_proofstudio_api_base_url",
        "127.0.0.1:8000",
        "build",
    )
    # At least one of the two docs must mention each token.
    missing = [
        t for t in required if t not in cors_text and t not in env_text
    ]
    check(
        "frontend API base URL strategy documented",
        not missing,
        detail=str(missing),
    )
    summary["frontend_api_base_strategy_checked"] = True
    _log(
        transcript,
        "frontend_api_base_strategy_check",
        {"missing": missing},
    )


def _check_platform_decision(
    summary: dict[str, Any], transcript: list[dict[str, Any]]
) -> None:
    text = _read(DEPLOYMENT_DIR / "platform-decision.md")
    low = text.lower()
    check(
        "platform decision marked pending",
        "pending" in low,
        detail="must mark selected: pending (or similar)",
    )
    # Must not claim a specific platform is THE selected one. "selected:
    # pending" is honest; "selected: <platform>" or "we selected/chose/picked"
    # would be an overclaim. Mentions of candidate platform names inside the
    # candidate list are fine and expected.
    specific_platforms = (
        "render",
        "railway",
        "fly.io",
        "vercel",
        "netlify",
        "cloudflare pages",
    )
    selected_claims: list[str] = []
    for platform in specific_platforms:
        if f"selected: {platform}" in low or f"selected:{platform}" in low:
            selected_claims.append(platform)
    for phrase in (
        "we selected",
        "we chose",
        "we picked",
        "platform is selected and deployed",
        "deployment is live",
    ):
        if phrase in low:
            selected_claims.append(phrase)
    check(
        "platform decision does not overclaim a selection",
        not selected_claims,
        detail=str(selected_claims),
    )
    summary["platform_decision_checked"] = True
    _log(
        transcript,
        "platform_decision_check",
        {"selected_claims": selected_claims},
    )


def _check_preflight_checklist(
    summary: dict[str, Any], transcript: list[dict[str, Any]]
) -> None:
    text = _read(DEPLOYMENT_DIR / "preflight-checklist.md").lower()
    before_required = (
        "choose platform",
        "cors",
        "run local smoke",
        "frontend build",
        "live mode default",
        "no `.env`",
    )
    after_required = (
        "/health",
        "/version",
        "frontend api status",
        "dry-run",
        "no provider",
        "submission checklist",
    )
    missing_before = [t for t in before_required if t not in text]
    missing_after = [t for t in after_required if t not in text]
    check(
        "preflight has before-deploy checks",
        not missing_before,
        detail=str(missing_before),
    )
    check(
        "preflight has after-deploy checks",
        not missing_after,
        detail=str(missing_after),
    )
    summary["preflight_checklist_checked"] = True
    _log(
        transcript,
        "preflight_checklist_check",
        {"missing_before": missing_before, "missing_after": missing_after},
    )


def _check_backend_import_and_health(
    summary: dict[str, Any], transcript: list[dict[str, Any]]
) -> None:
    # Ensure a stale PROOFSTUDIO_CORS_ORIGINS from the outer shell does not
    # pollute the import-time / health TestClient checks below.
    os.environ.pop("PROOFSTUDIO_CORS_ORIGINS", None)

    from proofstudio.api.app import (  # type: ignore[import-not-found]
        LOCAL_DEMO_CORS_ORIGINS,
        _resolve_cors_origins,
        app,
        create_app,
    )

    check("FastAPI app imported", app is not None, detail="app is None")
    summary["fastapi_import_checked"] = app is not None

    # Tiny CORS/env reader behavior.
    local_only = _resolve_cors_origins()
    check(
        "CORS reader preserves local origins when env unset",
        all(o in local_only for o in LOCAL_DEMO_CORS_ORIGINS),
        detail=str(local_only),
    )
    os.environ["PROOFSTUDIO_CORS_ORIGINS"] = "*"
    wildcard_result = _resolve_cors_origins()
    check(
        "CORS reader refuses wildcard production CORS",
        wildcard_result == list(LOCAL_DEMO_CORS_ORIGINS),
        detail=str(wildcard_result),
    )
    os.environ["PROOFSTUDIO_CORS_ORIGINS"] = (
        "https://replace-with-web-host, http://127.0.0.1:5173"
    )
    merged = _resolve_cors_origins()
    check(
        "CORS reader merges explicit production origins (deduped)",
        "https://replace-with-web-host" in merged
        and merged.count("http://127.0.0.1:5173") == 1,
        detail=str(merged),
    )
    os.environ.pop("PROOFSTUDIO_CORS_ORIGINS", None)

    # Health + version through TestClient.
    from fastapi.testclient import TestClient  # type: ignore[import-not-found]

    test_app = create_app()
    check("create_app() returns an app", test_app is not None)
    assert test_app is not None  # for type checkers
    client = TestClient(test_app)

    health_resp = client.get("/health")
    check(
        "/health returns 200",
        health_resp.status_code == 200,
        detail=str(health_resp.status_code),
    )
    health_body = health_resp.json()
    check(
        "/health body ok=true",
        health_body.get("ok") is True,
        detail=str(health_body),
    )
    summary["health_checked"] = True

    version_resp = client.get("/version")
    check(
        "/version returns 200",
        version_resp.status_code == 200,
        detail=str(version_resp.status_code),
    )
    version_body = version_resp.json()
    check(
        "/version body has version",
        bool(version_body.get("version")),
        detail=str(version_body),
    )
    summary["version_checked"] = True

    _log(transcript, "backend_import_and_health", {
        "app_imported": app is not None,
        "local_origins_preserved": list(LOCAL_DEMO_CORS_ORIGINS),
        "wildcard_refused": wildcard_result == list(LOCAL_DEMO_CORS_ORIGINS),
        "merged_origins": merged,
        "health_status": health_resp.status_code,
        "version_status": version_resp.status_code,
    })


def _check_default_safe_dry_run(
    summary: dict[str, Any], transcript: list[dict[str, Any]]
) -> None:
    """Drive a default safe dry-run in-process and prove no provider/B2 call."""
    os.environ.pop("PROOFSTUDIO_CORS_ORIGINS", None)
    from proofstudio.api.app import create_app  # type: ignore[import-not-found]
    from fastapi.testclient import TestClient  # type: ignore[import-not-found]

    test_app = create_app()
    assert test_app is not None
    client = TestClient(test_app)

    # Create a campaign.
    camp_resp = client.post(
        "/campaigns",
        json={
            "name": "ps017 deployment prep safe dry-run",
            "brief": "Verify the default path avoids providers and B2.",
        },
    )
    check(
        "POST /campaigns returns 201",
        camp_resp.status_code == 201,
        detail=str(camp_resp.status_code),
    )
    campaign_id = camp_resp.json().get("campaign_id")
    check("campaign_id returned", bool(campaign_id))

    # Default run: no run_live, no dry_run=False -> safe dry-run.
    run_resp = client.post(
        "/runs",
        json={"campaign_id": campaign_id, "prompt": "safe dry-run only"},
    )
    check(
        "POST /runs returns 201",
        run_resp.status_code == 201,
        detail=str(run_resp.status_code),
    )
    run_body = run_resp.json()
    run_id = run_body.get("run_id")
    run = run_body.get("run", {})

    # The default run must be a dry-run (not live).
    check(
        "default run is dry_run=true",
        run.get("dry_run") is True,
        detail=str(run.get("dry_run")),
    )
    check(
        "default run is run_live=false",
        run.get("run_live") is False,
        detail=str(run.get("run_live")),
    )
    status = run.get("status")
    check(
        "default run status is dry_run_created",
        status == "dry_run_created",
        detail=str(status),
    )

    # No attempts, no assets, no manifest on the default path.
    attempts = client.get(f"/runs/{run_id}/attempts").json()
    assets = client.get(f"/runs/{run_id}/assets").json()
    manifest = client.get(f"/runs/{run_id}/manifest").json()

    check(
        "default run has zero attempts",
        attempts.get("attempt_count") == 0,
        detail=str(attempts.get("attempt_count")),
    )
    check(
        "default run has zero assets",
        assets.get("asset_count") == 0,
        detail=str(assets.get("asset_count")),
    )
    check(
        "default run manifest not ready",
        manifest.get("ready") is False,
        detail=str(manifest.get("ready")),
    )

    # Honest structural evidence of a provider/B2 call:
    # - a live provider call populates selected_provider and creates attempts;
    # - a B2 call produces assets with b2_url or sets stored_manifest_verify.
    # The default dry-run path does none of these.
    provider_call_evidence = bool(run.get("selected_provider")) or (
        attempts.get("attempt_count", 0) > 0
    )
    b2_call_evidence = any(
        asset.get("b2_url") for asset in assets.get("assets", [])
    ) or bool(manifest.get("stored_manifest_verify")) or bool(
        run.get("stored_manifest_verify")
    )

    summary["default_no_live_provider_call"] = not provider_call_evidence
    summary["default_no_b2_call"] = not b2_call_evidence
    check(
        "default run made no live provider call",
        not provider_call_evidence,
        detail="provider selected or attempts recorded on default run",
    )
    check(
        "default run made no B2 call",
        not b2_call_evidence,
        detail="b2 asset url or stored manifest verify present on default run",
    )

    _log(transcript, "default_safe_dry_run", {
        "campaign_id": campaign_id,
        "run_id": run_id,
        "status": status,
        "dry_run": run.get("dry_run"),
        "run_live": run.get("run_live"),
        "attempt_count": attempts.get("attempt_count"),
        "asset_count": assets.get("asset_count"),
        "manifest_ready": manifest.get("ready"),
        "provider_call_evidence": provider_call_evidence,
        "b2_call_evidence": b2_call_evidence,
    })


def _check_frontend_build(
    summary: dict[str, Any], transcript: list[dict[str, Any]]
) -> None:
    summary["frontend_build_checked"] = True
    try:
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=str(FRONTEND_DIR),
            capture_output=True,
            text=True,
            timeout=240.0,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        summary["frontend_build_status"] = f"error: {exc}"
        _log(transcript, "frontend_build", {"status": "error", "error": str(exc)})
        check("frontend build could run", False, detail=str(exc))
        return

    status = "passed" if result.returncode == 0 else "failed"
    summary["frontend_build_status"] = status
    _log(transcript, "frontend_build", {
        "command": "npm run build",
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


def _check_backend_changed_documented(
    summary: dict[str, Any], transcript: list[dict[str, Any]]
) -> None:
    """PS-017 may touch src/ ONLY for the tiny CORS/env reader on app.py.

    ``backend_changed`` is honestly True iff any file under src/ is modified.
    The accompanying check enforces that any such change is in the allow-list.
    """
    modified = _git_modified(("src/",))
    modified_rel: list[str] = []
    for path in modified:
        try:
            rel = str(Path(path).resolve().relative_to(REPO_ROOT))
        except ValueError:
            rel = path
        modified_rel.append(rel)
    disallowed = [p for p in modified_rel if p not in ALLOWED_BACKEND_PATHS]
    summary["backend_changed"] = bool(modified_rel)
    summary["backend_changed_paths"] = modified_rel
    _log(transcript, "backend_changed_check", {
        "modified": modified_rel,
        "disallowed": disallowed,
        "allowed": list(ALLOWED_BACKEND_PATHS),
    })
    check(
        "backend changes are limited to the allowed CORS/env reader",
        not disallowed,
        detail=str(disallowed),
    )


def _check_frontend_app_changed(
    summary: dict[str, Any], transcript: list[dict[str, Any]]
) -> None:
    modified = _git_modified(("apps/web/src",))
    summary["frontend_app_changed_paths"] = modified
    summary["frontend_app_changed"] = bool(modified)
    _log(transcript, "frontend_app_changed_check", {"modified": modified})


def _check_historical_scripts(
    summary: dict[str, Any], transcript: list[dict[str, Any]]
) -> None:
    modified = _git_modified(HISTORICAL_SCRIPTS)
    summary["historical_scripts_untouched"] = not modified
    summary["historical_scripts_modified_paths"] = modified
    _log(transcript, "historical_scripts_check", {"modified": modified})
    check(
        "historical proof scripts untouched",
        not modified,
        detail=str(modified),
    )


def _check_no_secrets_anywhere(
    summary: dict[str, Any], transcript: list[dict[str, Any]]
) -> None:
    """Scan env template + deployment docs + proof doc for real secret patterns."""
    targets = [
        ENV_TEMPLATE,
        DEPLOYMENT_DIR / "README.md",
        DEPLOYMENT_DIR / "environment.md",
        DEPLOYMENT_DIR / "cors-and-security.md",
        DEPLOYMENT_DIR / "platform-decision.md",
        DEPLOYMENT_DIR / "preflight-checklist.md",
        PROOF_DOC,
    ]
    hits: dict[str, list[str]] = {}
    for path in targets:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        found = _scan_secrets(text)
        if found:
            hits[str(path.relative_to(REPO_ROOT))] = found
    # Also enforce: every value in the env template is a placeholder (re-check
    # here so this summary field is robust even if the env check is reordered).
    if ENV_TEMPLATE.is_file():
        assignments = _parse_env_assignments(ENV_TEMPLATE.read_text("utf-8"))
        for key in SECRET_KEY_PATTERNS:
            value = assignments.get(key)
            if value and value not in PLACEHOLDER_VALUES and REAL_SECRET_VALUE.match(value):
                hits.setdefault(str(ENV_TEMPLATE), []).append(key)
    summary["no_secret_leakage"] = not hits
    _log(transcript, "no_secrets_scan", {"hits": hits})
    check(
        "no real secrets in env template, deployment docs, or proof doc",
        not hits,
        detail=str(hits),
    )


def _check_proof_doc(transcript: list[dict[str, Any]]) -> None:
    text = _read(PROOF_DOC).lower()
    required_sections = (
        "status",
        "files created",
        "backend changed",
        "frontend changed",
        "environment template",
        "cors strategy",
        "frontend api base url strategy",
        "no-secret",
        "default no-live",
        "deployment status",
        "limitations",
        "next milestone",
        "truth boundary",
    )
    missing = [s for s in required_sections if s not in text]
    check("proof doc has required sections", not missing, detail=str(missing))
    _log(transcript, "proof_doc_check", {"missing": missing})


def _normalize_summary(summary: dict[str, Any]) -> dict[str, Any]:
    """Guarantee stable schema: booleans are booleans, lists use *_paths/items."""
    bool_keys = (
        "ok",
        "env_template_checked",
        "env_template_no_real_secrets",
        "required_env_keys_checked",
        "deployment_docs_created",
        "cors_strategy_checked",
        "frontend_api_base_strategy_checked",
        "platform_decision_checked",
        "preflight_checklist_checked",
        "fastapi_import_checked",
        "health_checked",
        "version_checked",
        "default_no_live_provider_call",
        "default_no_b2_call",
        "frontend_build_checked",
        "backend_changed",
        "frontend_app_changed",
        "historical_scripts_untouched",
        "no_secret_leakage",
    )
    for key in bool_keys:
        summary[key] = bool(summary.get(key, False))

    # Statuses are strings.
    if not isinstance(summary.get("frontend_build_status"), str):
        summary["frontend_build_status"] = "not_run"
    if not isinstance(summary.get("deployment_status"), str):
        summary["deployment_status"] = "prep_only"
    if not isinstance(summary.get("public_url_status"), str):
        summary["public_url_status"] = "pending"
    return summary


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    transcript: list[dict[str, Any]] = []

    summary: dict[str, Any] = {
        "ok": False,
        "slice": "PS-017",
        "env_template_checked": False,
        "env_template_no_real_secrets": False,
        "required_env_keys_checked": False,
        "deployment_docs_created": False,
        "deployment_docs_created_paths": [],
        "cors_strategy_checked": False,
        "frontend_api_base_strategy_checked": False,
        "platform_decision_checked": False,
        "preflight_checklist_checked": False,
        "fastapi_import_checked": False,
        "health_checked": False,
        "version_checked": False,
        "default_no_live_provider_call": False,
        "default_no_b2_call": False,
        "frontend_build_checked": False,
        "frontend_build_status": "not_run",
        "backend_changed": False,
        "backend_changed_paths": [],
        "frontend_app_changed": False,
        "frontend_app_changed_paths": [],
        "historical_scripts_untouched": False,
        "historical_scripts_modified_paths": [],
        "no_secret_leakage": False,
        "deployment_status": "prep_only",
        "public_url_status": "pending",
        "required_env_keys_items": [],
        "optional_env_keys_items": [],
        "summary_path": str(SUMMARY_PATH),
        "transcript_path": str(TRANSCRIPT_PATH),
        "truth_boundary": TRUTH_BOUNDARY,
    }

    try:
        # 2. Required deployment docs exist.
        _check_deployment_docs_exist(summary, transcript)

        # 3 + 4 + 5 + 6. Env template exists, placeholders only, required keys,
        #    no real secrets.
        _check_env_template(summary, transcript)

        # 7. CORS docs include explicit production origin guidance.
        _check_cors_docs(summary, transcript)

        # 8. Frontend API base URL strategy documented.
        _check_frontend_api_base_strategy(summary, transcript)

        # 9. Platform decision pending.
        _check_platform_decision(summary, transcript)

        # 10. Preflight checklist before/after.
        _check_preflight_checklist(summary, transcript)

        # 11 + 12. Backend import + /health + /version.
        _check_backend_import_and_health(summary, transcript)

        # 13. Default safe dry-run avoids providers/B2.
        _check_default_safe_dry_run(summary, transcript)

        # 14. Frontend build.
        _check_frontend_build(summary, transcript)

        # 15. Backend changes limited to the allowed CORS/env reader.
        _check_backend_changed_documented(summary, transcript)

        # (frontend app changed is informational; api.ts is allowed to be tiny.)
        _check_frontend_app_changed(summary, transcript)

        # 16. Historical scripts untouched.
        _check_historical_scripts(summary, transcript)

        # No secrets anywhere.
        _check_no_secrets_anywhere(summary, transcript)

        # Proof doc sections.
        _check_proof_doc(transcript)

        required_true = (
            summary["env_template_checked"],
            summary["env_template_no_real_secrets"],
            summary["required_env_keys_checked"],
            summary["deployment_docs_created"],
            summary["cors_strategy_checked"],
            summary["frontend_api_base_strategy_checked"],
            summary["platform_decision_checked"],
            summary["preflight_checklist_checked"],
            summary["fastapi_import_checked"],
            summary["health_checked"],
            summary["version_checked"],
            summary["default_no_live_provider_call"],
            summary["default_no_b2_call"],
            summary["frontend_build_checked"],
            summary["frontend_build_status"] == "passed",
            summary["historical_scripts_untouched"],
            summary["no_secret_leakage"],
        )
        summary["ok"] = bool(all(required_true))

    except CheckFail as exc:
        summary["ok"] = False
        summary["error"] = str(exc)
        _log(transcript, "check_failed", {"error": str(exc)})
    except Exception as exc:  # pragma: no cover - crash guard
        summary["ok"] = False
        summary["error"] = f"{type(exc).__name__}: {exc}"
        import traceback as _tb
        _log(transcript, "unhandled_crash", {
            "error": summary["error"],
            "traceback": _tb.format_exc(),
        })

    summary["written_at"] = now_iso()

    # Final secret scan across the transcript before writing.
    transcript_secret_hits = _scan_secrets(
        json.dumps(transcript, ensure_ascii=False, default=str)
    )
    if transcript_secret_hits:
        summary["no_secret_leakage"] = False
        summary["ok"] = False
        summary["error"] = f"secret leak in transcript: {transcript_secret_hits}"
        _log(transcript, "transcript_secret_scan", {"hits": transcript_secret_hits})

    _normalize_summary(summary)
    SUMMARY_PATH.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    TRANSCRIPT_PATH.write_text(
        json.dumps(
            {
                "slice": "PS-017",
                "demo": "deployment-prep-smoke",
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
