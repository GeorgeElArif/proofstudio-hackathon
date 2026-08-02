#!/usr/bin/env python3
"""PS-018 live URL smoke.

Default mode is local contract mode:
- no public URLs required
- no provider calls
- no B2 calls
- verifies Render deployment readiness and docs

Explicit live URL mode only runs when:
- PS018_RUN_LIVE_URL_SMOKE=true
- PROOFSTUDIO_PUBLIC_API_BASE_URL is a non-localhost HTTPS URL
- PROOFSTUDIO_PUBLIC_WEB_URL is a non-localhost HTTPS URL
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path("/tmp/proofstudio-ps-018")
SUMMARY_PATH = OUTPUT_DIR / "live-url-smoke-summary.json"
TRANSCRIPT_PATH = OUTPUT_DIR / "live-url-smoke-transcript.json"

CURRENT_SMOKE = "scripts/ps018_live_url_smoke.py"

REQUIRED_FILES = [
    "render.yaml",
    "docs/deployment/render.md",
    "docs/ps-018-public-deployment-target-live-url-smoke-proof.md",
    CURRENT_SMOKE,
]

HISTORICAL_SCRIPTS = [
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
    "scripts/ps017_deployment_prep_smoke.py",
]

TRUTH_BOUNDARY = (
    "PS-018 Level A proves ProofStudio has a selected deployment target "
    "(Render), a reviewable deployment plan (render.yaml), a Render runbook, "
    "and a gated live URL smoke path. It does not prove public deployment, "
    "a working public app URL, final Devpost submission, production availability, "
    "authentication, production persistence, background job reliability, "
    "legal authenticity, C2PA authenticity, semantic truth, or human authorship."
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(transcript: list[dict[str, Any]], step: str, ok: bool, detail: Any = None) -> None:
    transcript.append(
        {
            "step": step,
            "ok": ok,
            "detail": detail,
            "written_at": utc_now(),
        }
    )


def run(cmd: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd or ROOT),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8", errors="ignore")


def exists(path: str) -> bool:
    return (ROOT / path).exists()


def is_truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def is_nonlocal_https_url(value: str | None) -> bool:
    if not value:
        return False

    parsed = urllib.parse.urlparse(value)
    if parsed.scheme != "https":
        return False

    host = (parsed.hostname or "").lower()
    if host in {"localhost", "127.0.0.1", "0.0.0.0"}:
        return False

    return bool(host)


def http_request(
    url: str,
    method: str = "GET",
    origin: str | None = None,
    data: bytes | None = None,
    content_type: str | None = None,
    timeout: int = 20,
) -> tuple[int, str, dict[str, str]]:
    headers: dict[str, str] = {
        "User-Agent": "ProofStudio-PS018-Smoke/1.0",
    }

    if origin:
        headers["Origin"] = origin

    if content_type:
        headers["Content-Type"] = content_type

    if method == "OPTIONS":
        headers["Access-Control-Request-Method"] = "GET"

    request = urllib.request.Request(url, method=method, headers=headers, data=data)

    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8", errors="replace")
        response_headers = {k.lower(): v for k, v in response.headers.items()}
        return response.status, body, response_headers


def secret_scan_files() -> tuple[bool, list[tuple[str, str]]]:
    candidate_roots = [
        ROOT / "render.yaml",
        ROOT / "docs/deployment",
        ROOT / "docs/submission/submission-checklist.md",
        ROOT / "docs/submission/judge-evidence-pack.md",
        ROOT / "docs/ps-018-public-deployment-target-live-url-smoke-proof.md",
        ROOT / CURRENT_SMOKE,
        ROOT / "README.md",
        ROOT / "apps/web/README.md",
        ROOT / ".env.production.example",
    ]

    secret_assignment_keys = [
        "B2_APP_KEY",
        "CLOUDFLARE_API_TOKEN",
        "GEMINI_API_KEY",
        "GMI_API_KEY",
        "OPENAI_API_KEY",
    ]
    forbidden_patterns = [key + "=" for key in secret_assignment_keys]
    forbidden_patterns.append("Bearer" + " ")

    bad: list[tuple[str, str]] = []

    for root in candidate_roots:
        if not root.exists():
            continue

        files = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file()]

        for path in files:
            text = path.read_text(encoding="utf-8", errors="ignore")

            if path.name == ".env.production.example":
                for line in text.splitlines():
                    stripped = line.strip()
                    if not stripped or stripped.startswith("#") or "=" not in stripped:
                        continue

                    key, value = stripped.split("=", 1)
                    key_upper = key.upper()
                    value_lower = value.strip().lower()

                    if any(token in key_upper for token in ["KEY", "TOKEN", "SECRET", "PASSWORD"]):
                        if value_lower not in {"replace-me", "placeholder", "not-set"}:
                            bad.append((str(path.relative_to(ROOT)), f"{key}=<non-placeholder>"))
                continue

            for pattern in forbidden_patterns:
                if pattern in text:
                    bad.append((str(path.relative_to(ROOT)), pattern))

    return not bad, bad


def git_status_paths(paths: list[str]) -> list[str]:
    result = run(["git", "status", "--short", "--"] + paths)
    changed: list[str] = []

    for line in result.stdout.splitlines():
        if not line.strip():
            continue

        # Porcelain format: XY path
        changed_path = line[3:].strip()
        if changed_path:
            changed.append(changed_path)

    return changed


def check_required_files(summary: dict[str, Any], transcript: list[dict[str, Any]]) -> bool:
    missing = [path for path in REQUIRED_FILES if not exists(path)]
    ok = not missing
    summary["required_files_paths"] = list(REQUIRED_FILES)
    log(transcript, "required_files", ok, {"missing": missing, "required": REQUIRED_FILES})
    return ok


def check_render_config(summary: dict[str, Any], transcript: list[dict[str, Any]]) -> bool:
    text = read("render.yaml").lower()

    required_terms = [
        "proofstudio",
        "uvicorn proofstudio.api.app:app",
        "--port $port",
        "/health",
        "apps/web",
        "npm",
        "dist",
        "vite_proofstudio_api_base_url",
    ]

    missing = [term for term in required_terms if term not in text]

    forbidden = [
        "b2_app_key=",
        "cloudflare_api_token=",
        "gemini_api_key=",
        "bearer" + " ",
    ]

    found_forbidden = [pattern for pattern in forbidden if pattern in text]
    ok = not missing and not found_forbidden

    summary["render_config_checked"] = ok
    log(transcript, "render_config", ok, {"missing": missing, "forbidden": found_forbidden})
    return ok


def check_docs(summary: dict[str, Any], transcript: list[dict[str, Any]]) -> bool:
    files = {
        "render": "docs/deployment/render.md",
        "platform": "docs/deployment/platform-decision.md",
        "deploy_readme": "docs/deployment/README.md",
        "preflight": "docs/deployment/preflight-checklist.md",
        "submission": "docs/submission/submission-checklist.md",
        "evidence": "docs/submission/judge-evidence-pack.md",
        "proof": "docs/ps-018-public-deployment-target-live-url-smoke-proof.md",
    }

    lower = {name: read(path).lower() for name, path in files.items()}

    failures: list[str] = []

    for term in [
        "render",
        "backend",
        "frontend",
        "static site",
        "environment",
        "health check",
        "cors",
        "ps018_live_url_smoke.py",
        "public deployment is not proven",
    ]:
        if term not in lower["render"]:
            failures.append(f"render runbook missing {term}")

    if "selected: render" not in lower["platform"] and "selected target: render" not in lower["platform"]:
        failures.append("platform decision must mark Render selected")

    for term in [
        "docs/deployment/render.md",
        "scripts/ps018_live_url_smoke.py",
        "proofstudio_public_api_base_url",
        "proofstudio_public_web_url",
    ]:
        if term not in lower["deploy_readme"]:
            failures.append(f"deployment README missing {term}")

    for term in [
        "ps-018",
        "live url smoke",
        "/health",
        "/version",
        "safe dry-run",
    ]:
        if term not in lower["preflight"]:
            failures.append(f"preflight checklist missing {term}")

    if "pending until live url smoke passes" not in lower["submission"]:
        failures.append("submission checklist must keep public URL pending until live smoke passes")

    if "render" not in lower["evidence"] or "live url smoke" not in lower["evidence"]:
        failures.append("judge evidence pack must mention Render and live URL smoke")

    for term in [
        "selected target",
        "render config",
        "public url status",
        "live url smoke",
        "no fake url",
        "truth boundary",
    ]:
        if term not in lower["proof"]:
            failures.append(f"proof doc missing {term}")

    ok = not failures

    summary["render_runbook_checked"] = "render" in lower["render"] and "ps018_live_url_smoke.py" in lower["render"]
    summary["deployment_docs_updated"] = all(
        term in lower["deploy_readme"]
        for term in [
            "docs/deployment/render.md",
            "scripts/ps018_live_url_smoke.py",
            "proofstudio_public_api_base_url",
            "proofstudio_public_web_url",
        ]
    )
    summary["submission_docs_updated"] = (
        "pending until live url smoke passes" in lower["submission"]
        and "render" in lower["evidence"]
        and "live url smoke" in lower["evidence"]
    )

    log(transcript, "docs", ok, {"failures": failures})
    return ok


def check_env_template(summary: dict[str, Any], transcript: list[dict[str, Any]]) -> bool:
    path = ROOT / ".env.production.example"
    text = path.read_text(encoding="utf-8", errors="ignore")

    required_keys = [
        "PROOFSTUDIO_ENV",
        "PROOFSTUDIO_API_HOST",
        "PROOFSTUDIO_API_PORT",
        "PROOFSTUDIO_PUBLIC_API_BASE_URL",
        "PROOFSTUDIO_PUBLIC_WEB_URL",
        "PROOFSTUDIO_CORS_ORIGINS",
        "VITE_PROOFSTUDIO_API_BASE_URL",
        "PROOFSTUDIO_RUN_LIVE_DEFAULT",
    ]

    pairs: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        pairs[key.strip()] = value.strip()

    missing = [key for key in required_keys if key not in pairs]
    run_live_ok = pairs.get("PROOFSTUDIO_RUN_LIVE_DEFAULT") == "false"

    ok = not missing and run_live_ok
    summary["env_template_checked"] = ok
    log(transcript, "env_template", ok, {"missing": missing, "run_live_default": pairs.get("PROOFSTUDIO_RUN_LIVE_DEFAULT")})
    return ok


def check_historical_scripts(summary: dict[str, Any], transcript: list[dict[str, Any]]) -> bool:
    modified = git_status_paths(HISTORICAL_SCRIPTS)

    # The current PS-018 smoke is intentionally not historical.
    if CURRENT_SMOKE in modified:
        modified.remove(CURRENT_SMOKE)

    ok = not modified
    summary["historical_scripts_modified_paths"] = modified
    summary["historical_scripts_untouched"] = ok
    log(transcript, "historical_scripts", ok, {"modified": modified})
    return ok


def check_frontend_build(summary: dict[str, Any], transcript: list[dict[str, Any]]) -> bool:
    result = run(["npm", "run", "build"], cwd=ROOT / "apps/web")
    ok = result.returncode == 0

    summary["frontend_build_checked"] = True
    summary["frontend_build_status"] = "passed" if ok else "failed"

    log(
        transcript,
        "frontend_build",
        ok,
        {
            "returncode": result.returncode,
            "stdout_tail": result.stdout[-2000:],
            "stderr_tail": result.stderr[-2000:],
        },
    )
    return ok


def check_repo_changes(summary: dict[str, Any], transcript: list[dict[str, Any]]) -> bool:
    backend_paths = [
        "src/proofstudio/api",
        "src/proofstudio/providers",
        "src/proofstudio/provenance",
    ]
    frontend_app_paths = [
        "apps/web/src",
        "apps/web/index.html",
        "apps/web/package.json",
        "apps/web/package-lock.json",
        "apps/web/vite.config.ts",
        "apps/web/tsconfig.json",
    ]

    backend_changed_paths = git_status_paths(backend_paths)
    frontend_changed_paths = git_status_paths(frontend_app_paths)

    summary["backend_changed_paths"] = backend_changed_paths
    summary["frontend_app_changed_paths"] = frontend_changed_paths
    summary["backend_changed"] = bool(backend_changed_paths)
    summary["frontend_app_changed"] = bool(frontend_changed_paths)

    ok = not backend_changed_paths and not frontend_changed_paths
    log(
        transcript,
        "repo_changes",
        ok,
        {
            "backend_changed_paths": backend_changed_paths,
            "frontend_app_changed_paths": frontend_changed_paths,
        },
    )
    return ok


def run_live_url_smoke(summary: dict[str, Any], transcript: list[dict[str, Any]]) -> bool:
    api_base = os.getenv("PROOFSTUDIO_PUBLIC_API_BASE_URL", "").rstrip("/")
    web_url = os.getenv("PROOFSTUDIO_PUBLIC_WEB_URL", "").rstrip("/")
    live_enabled = is_truthy(os.getenv("PS018_RUN_LIVE_URL_SMOKE"))

    summary["live_url_mode_enabled"] = live_enabled

    if not live_enabled:
        summary["live_url_smoke_status"] = "skipped_missing_urls"
        summary["public_api_url_status"] = "not_set"
        summary["public_web_url_status"] = "not_set"
        summary["api_health_checked"] = False
        summary["api_version_checked"] = False
        summary["web_load_checked"] = False
        summary["cors_preflight_checked"] = False
        summary["safe_public_dry_run_checked"] = False
        summary["public_url_verified"] = False
        log(transcript, "live_url_smoke", True, {"status": "skipped_missing_urls", "reason": "live mode disabled"})
        return True

    if not is_nonlocal_https_url(api_base) or not is_nonlocal_https_url(web_url):
        summary["live_url_smoke_status"] = "skipped_missing_urls"
        summary["public_api_url_status"] = "invalid_or_missing"
        summary["public_web_url_status"] = "invalid_or_missing"
        summary["api_health_checked"] = False
        summary["api_version_checked"] = False
        summary["web_load_checked"] = False
        summary["cors_preflight_checked"] = False
        summary["safe_public_dry_run_checked"] = False
        summary["public_url_verified"] = False
        log(
            transcript,
            "live_url_smoke",
            False,
            {
                "status": "skipped_missing_urls",
                "api_base": api_base,
                "web_url": web_url,
                "reason": "live mode enabled but URLs are missing, non-HTTPS, or local",
            },
        )
        return False

    failures: list[str] = []

    try:
        status, body, _headers = http_request(f"{api_base}/health")
        summary["api_health_checked"] = 200 <= status < 300 and "ok" in body.lower()
        if not summary["api_health_checked"]:
            failures.append("api health failed")
    except Exception as exc:  # noqa: BLE001
        summary["api_health_checked"] = False
        failures.append(f"api health exception: {exc}")

    try:
        status, body, _headers = http_request(f"{api_base}/version")
        summary["api_version_checked"] = 200 <= status < 300 and bool(body.strip())
        if not summary["api_version_checked"]:
            failures.append("api version failed")
    except Exception as exc:  # noqa: BLE001
        summary["api_version_checked"] = False
        failures.append(f"api version exception: {exc}")

    try:
        status, body, _headers = http_request(web_url)
        lower_body = body.lower()
        summary["web_load_checked"] = 200 <= status < 300 and "<html" in lower_body
        if not summary["web_load_checked"]:
            failures.append("web html load failed")
    except Exception as exc:  # noqa: BLE001
        summary["web_load_checked"] = False
        failures.append(f"web load exception: {exc}")

    try:
        status, _body, headers = http_request(f"{api_base}/version", method="OPTIONS", origin=web_url)
        allow_origin = headers.get("access-control-allow-origin", "")
        summary["cors_preflight_checked"] = 200 <= status < 400 and allow_origin in {web_url, "*"}
        if not summary["cors_preflight_checked"]:
            failures.append("cors preflight failed")
    except Exception as exc:  # noqa: BLE001
        summary["cors_preflight_checked"] = False
        failures.append(f"cors preflight exception: {exc}")

    # Keep this conservative. The public contract may evolve, but default smoke must not call providers/B2.
    summary["safe_public_dry_run_checked"] = False
    summary["default_no_live_provider_call"] = True
    summary["default_no_b2_call"] = True

    ok = not failures
    summary["live_url_smoke_status"] = "passed" if ok else "failed"
    summary["public_api_url_status"] = "verified" if ok else "failed"
    summary["public_web_url_status"] = "verified" if ok else "failed"
    summary["public_url_verified"] = ok

    log(transcript, "live_url_smoke", ok, {"failures": failures, "api_base": api_base, "web_url": web_url})
    return ok


def write_outputs(summary: dict[str, Any], transcript: list[dict[str, Any]]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summary["written_at"] = utc_now()
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    TRANSCRIPT_PATH.write_text(json.dumps(transcript, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


def main() -> int:
    transcript: list[dict[str, Any]] = []

    summary: dict[str, Any] = {
        "ok": False,
        "slice": "PS-018",
        "selected_target": "render",
        "render_config_checked": False,
        "render_runbook_checked": False,
        "deployment_docs_updated": False,
        "submission_docs_updated": False,
        "env_template_checked": False,
        "no_secret_leakage": False,
        "historical_scripts_untouched": False,
        "frontend_build_checked": False,
        "frontend_build_status": "not_run",
        "local_contract_checked": False,
        "live_url_mode_enabled": False,
        "live_url_smoke_status": "skipped_missing_urls",
        "public_api_url_status": "not_set",
        "public_web_url_status": "not_set",
        "api_health_checked": False,
        "api_version_checked": False,
        "web_load_checked": False,
        "cors_preflight_checked": False,
        "safe_public_dry_run_checked": False,
        "default_no_live_provider_call": True,
        "default_no_b2_call": True,
        "public_url_verified": False,
        "backend_changed": False,
        "frontend_app_changed": False,
        "summary_path": str(SUMMARY_PATH),
        "transcript_path": str(TRANSCRIPT_PATH),
        "truth_boundary": TRUTH_BOUNDARY,
    }

    checks = [
        check_required_files(summary, transcript),
        check_render_config(summary, transcript),
        check_docs(summary, transcript),
        check_env_template(summary, transcript),
    ]

    secret_ok, secret_bad = secret_scan_files()
    summary["no_secret_leakage"] = secret_ok
    log(transcript, "secret_scan", secret_ok, {"bad": secret_bad})
    checks.append(secret_ok)

    checks.append(check_historical_scripts(summary, transcript))
    checks.append(check_repo_changes(summary, transcript))
    checks.append(check_frontend_build(summary, transcript))
    checks.append(run_live_url_smoke(summary, transcript))

    summary["local_contract_checked"] = all(checks[:-1])
    summary["ok"] = all(checks)

    write_outputs(summary, transcript)
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
