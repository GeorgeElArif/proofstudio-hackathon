#!/usr/bin/env python3
"""
PS-013: Demo UI Shell / Review Room Frontend smoke test.

What this proves:

- A frontend demo shell exists under ``apps/web/`` that consumes the PS-012
  FastAPI demo contract.
- The frontend technology is detected (``vite_react_ts`` /
  ``vite_react_js`` / ``static_html_js`` / ``existing_frontend``) and the
  expected files are present.
- The API base URL is configurable via ``VITE_PROOFSTUDIO_API_BASE_URL`` with a
  documented fallback to ``http://127.0.0.1:8000``.
- The UI source references every required PS-012 endpoint (either inline or via
  the helper module in ``apps/web/src/api.ts``):
    GET  /health
    GET  /version
    POST /campaigns
    GET  /campaigns/{campaign_id}
    POST /runs
    GET  /runs/{run_id}
    GET  /runs/{run_id}/attempts
    GET  /runs/{run_id}/assets
    GET  /runs/{run_id}/manifest
    GET  /runs/{run_id}/passport
- All required UI sections are present:
    health/status, campaign builder, run creator, evidence overview,
    attempts, assets, manifest, passport, trust boundary.
- ``run_live`` defaults safe/false; live mode requires an explicit action and
  carries the warning "Live mode may call external providers and B2."
- No hardcoded fake media success, no hardcoded fake manifest success, no
  obvious secrets are present in the frontend source.
- If Node + a package file are available, an install/build is attempted
  (best-effort; never required for ``ok``).

This smoke does NOT start a browser, does NOT call live providers, and does
NOT require B2 credentials.

Truth boundary: PS-013 proves ProofStudio has a local demo UI shell for
reviewing campaign/run evidence through the FastAPI API. It does not prove
production deployment, a public app URL, auth, persistence, legal
authenticity, C2PA authenticity, semantic truth, or human authorship.

Historical proof scripts (PS-004 .. PS-012) are not modified.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

WEB_DIR = REPO_ROOT / "apps" / "web"
WEB_SRC_DIR = WEB_DIR / "src"
DOCS_PATH = REPO_ROOT / "docs" / "ps-013-demo-ui-review-room-frontend-proof.md"

OUTPUT_DIR = Path("/tmp/proofstudio-ps-013")
SUMMARY_PATH = OUTPUT_DIR / "demo-ui-review-room-summary.json"
TRANSCRIPT_PATH = OUTPUT_DIR / "demo-ui-review-room-transcript.json"

# Endpoint path fragments the UI source must reference (covered by api.ts
# helpers or inline). ``/campaigns`` covers the campaign GET/POST templated
# paths; ``/runs`` covers run GET/POST + the sub-resource prefixes.
REQUIRED_ENDPOINT_MARKERS: tuple[str, ...] = (
    "/health",
    "/version",
    "/campaigns",
    "/runs",
    "/attempts",
    "/assets",
    "/manifest",
    "/passport",
)

# Required UI sections, detected by section id markers in the source. Each
# entry maps to one or more substrings that prove the section is implemented.
SECTION_MARKERS: dict[str, tuple[str, ...]] = {
    "health": ('id="api-status"', "GET /health"),
    "campaign_builder": ('id="campaign-builder"', "Campaign Builder", "POST /campaigns"),
    "run_creator": ('id="run-creator"', "Run Creator", "run_live"),
    "evidence_overview": ('id="evidence-overview"', "Evidence Overview"),
    "attempts": ('id="attempts"', "Attempt Timeline"),
    "assets": ('id="assets"', "Assets"),
    "manifest": ('id="manifest"', "Manifest"),
    "passport": ('id="passport"', "Provenance Passport"),
    "trust_boundary": ('id="trust-boundary"', "Truth Boundary"),
}

LIVE_WARNING = "Live mode may call external providers and B2."

# Patterns that would indicate hardcoded fake media / manifest success.
# The UI may READ these fields from the API; it must never hard-code a
# successful value as a literal.
FAKE_MEDIA_PATTERNS = [
    re.compile(r"produced_real_media\s*:\s*true", re.IGNORECASE),
    re.compile(r"produced_real_media\s*=\s*true", re.IGNORECASE),
    re.compile(r"generated_media_present\s*:\s*true", re.IGNORECASE),
    # hardcoded fake media URLs presented as real generated output
    re.compile(r"""(src|url)\s*=\s*['"]https?://[^'"]*\.(png|jpe?g|webp|gif)['"]"""),
]
FAKE_MANIFEST_PATTERNS = [
    re.compile(r"stored_manifest_verify\s*:\s*true", re.IGNORECASE),
    re.compile(r"stored_manifest_verify\s*=\s*true", re.IGNORECASE),
    re.compile(r"""manifest_uri\s*:\s*['"]https?://""", re.IGNORECASE),
    re.compile(r"in_memory_manifest_verify\s*:\s*true", re.IGNORECASE),
]

SECRET_PATTERNS = [
    re.compile(r"(?i)Bearer\s+[A-Za-z0-9\-_.=~]{8,}"),
    re.compile(r"(?i)B2_KEY_ID[\s:=]+\S{8,}"),
    re.compile(r"(?i)B2_APP_KEY[\s:=]+\S{8,}"),
    re.compile(r"(?i)CLOUDFLARE_API_TOKEN[\s:=]+\S{8,}"),
    re.compile(r"(?i)GEMINI_API_KEY[\s:=]+\S{8,}"),
    re.compile(r"(?i)GENBLAZE_[A-Z_]*KEY[\s:=]+\S{8,}"),
    re.compile(r"(?i)GMICLOUD_API_KEY[\s:=]+\S{8,}"),
]

# Expected Vite + React + TS file set (the spec's "if using Vite React" list).
EXPECTED_VITE_FILES: tuple[str, ...] = (
    "package.json",
    "index.html",
    "src/main.tsx",
    "src/App.tsx",
    "src/api.ts",
    "src/styles.css",
    "README.md",
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
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class CheckFail(Exception):
    pass


def check(label: str, condition: bool, detail: str = "") -> None:
    if not condition:
        raise CheckFail(f"{label}: {detail}" if detail else f"{label}: failed")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def collect_source_text() -> tuple[str, list[Path]]:
    """Concatenate all frontend source files into one searchable blob."""
    if not WEB_SRC_DIR.exists():
        return ("", [])
    files: list[Path] = []
    for pattern in ("*.tsx", "*.ts", "*.jsx", "*.js", "*.css", "*.html"):
        files.extend(sorted(WEB_SRC_DIR.rglob(pattern)))
    files.append(WEB_DIR / "index.html")
    parts: list[str] = []
    seen: set[Path] = set()
    unique: list[Path] = []
    for f in files:
        try:
            f = f.resolve()
        except OSError:
            continue
        if f in seen or not f.is_file():
            continue
        seen.add(f)
        unique.append(f)
        parts.append(f"\n# >>> {f.relative_to(REPO_ROOT)}\n{read_text(f)}")
    return ("\n".join(parts), unique)


def detect_frontend_type() -> tuple[str, dict[str, bool]]:
    pkg = (WEB_DIR / "package.json").is_file()
    api_ts = (WEB_SRC_DIR / "api.ts").is_file()
    main_tsx = (WEB_SRC_DIR / "main.tsx").is_file()
    main_jsx = (WEB_SRC_DIR / "main.jsx").is_file()
    index_html = (WEB_DIR / "index.html").is_file()
    flags = {
        "package_json": pkg,
        "api_ts": api_ts,
        "main_tsx": main_tsx,
        "main_jsx": main_jsx,
        "index_html": index_html,
    }
    pkg_text = read_text(WEB_DIR / "package.json")
    has_vite = "vite" in pkg_text.lower() and "react" in pkg_text.lower()
    if pkg and has_vite and (main_tsx or api_ts):
        return ("vite_react_ts", flags)
    if pkg and has_vite and main_jsx:
        return ("vite_react_js", flags)
    if index_html and not pkg:
        return ("static_html_js", flags)
    if WEB_DIR.exists() and any(WEB_DIR.iterdir()):
        return ("existing_frontend", flags)
    return ("none", flags)


def historical_scripts_untouched() -> list[str]:
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


def scan_patterns(text: str, patterns: list[re.Pattern[str]]) -> list[str]:
    hits: list[str] = []
    for pat in patterns:
        m = pat.search(text)
        if m:
            hits.append(m.group(0))
    return hits


def attempt_build() -> tuple[bool, str, str]:
    """Best-effort install/build. Never required for ok.

    Returns (checked, status, detail).
    """
    if not (WEB_DIR / "package.json").is_file():
        return (False, "skipped", "no package.json")
    npm = shutil.which("npm")
    node = shutil.which("node")
    if not npm or not node:
        return (False, "skipped", "npm/node not on PATH")
    # Install only if node_modules is absent.
    install_detail = ""
    if not (WEB_DIR / "node_modules").is_dir():
        rc, out = _run([npm, "install", "--no-audit", "--no-fund"], WEB_DIR)
        if rc != 0:
            return (True, "failed", f"npm install rc={rc}; {out[-400:]}")
        install_detail = "npm install ok; "
    rc, out = _run([npm, "run", "build"], WEB_DIR)
    if rc == 0:
        return (True, "passed", install_detail + "npm run build ok")
    return (True, "failed", install_detail + f"npm run build rc={rc}; {out[-400:]}")


def _run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=300.0,
            check=False,
        )
        out = (result.stdout or "") + (result.stderr or "")
        return (result.returncode, out)
    except subprocess.TimeoutExpired:
        return (124, "timeout")
    except (OSError, subprocess.SubprocessError) as exc:
        return (-1, f"{type(exc).__name__}: {exc}")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    transcript: list[dict[str, Any]] = []

    def log(step: str, payload: Any) -> None:
        transcript.append({"step": step, "result": payload})

    summary: dict[str, Any] = {
        "ok": False,
        "slice": "PS-013",
        "frontend_path": str(WEB_DIR.relative_to(REPO_ROOT)),
        "frontend_type": "none",
        "package_file_present": False,
        "api_base_config_present": False,
        "health_section_present": False,
        "campaign_builder_present": False,
        "run_creator_present": False,
        "evidence_overview_present": False,
        "attempts_panel_present": False,
        "assets_panel_present": False,
        "manifest_panel_present": False,
        "passport_panel_present": False,
        "trust_boundary_present": False,
        "default_run_live_safe": False,
        "live_mode_warning_present": False,
        "no_fake_media": False,
        "no_fake_manifest": False,
        "no_secrets": False,
        "build_checked": False,
        "build_status": "not_attempted",
        "summary_path": str(SUMMARY_PATH),
        "transcript_path": str(TRANSCRIPT_PATH),
        "truth_boundary": (
            "PS-013 proves ProofStudio has a local demo UI shell for reviewing "
            "campaign/run evidence through the FastAPI API. It does not prove "
            "production deployment, a public app URL, auth, persistence, legal "
            "authenticity, C2PA authenticity, semantic truth, or human "
            "authorship."
        ),
    }

    try:
        # 0. Historical proof scripts must be untouched.
        modified = historical_scripts_untouched()
        check(
            "historical proof scripts untouched",
            not modified,
            detail=f"modified: {modified}",
        )
        log("historical_scripts_check", {"modified": modified})

        # 1. Frontend directory + files exist.
        check("apps/web exists", WEB_DIR.is_dir())
        frontend_type, flags = detect_frontend_type()
        summary["frontend_type"] = frontend_type
        summary["package_file_present"] = flags["package_json"]
        check(
            "frontend type detected",
            frontend_type in {"vite_react_ts", "vite_react_js", "static_html_js",
                              "existing_frontend"},
            detail=frontend_type,
        )
        log("frontend_detect", {"type": frontend_type, "flags": flags})

        # Expected Vite file set (only enforced for the vite variants).
        if frontend_type.startswith("vite"):
            missing_files = [
                f for f in EXPECTED_VITE_FILES if not (WEB_DIR / f).is_file()
            ]
            check("expected vite files present", not missing_files,
                  detail=f"missing: {missing_files}")
            log("vite_files", {"missing": missing_files})
        else:
            missing_files = []
            log("vite_files", {"skipped": frontend_type})

        source_text, source_files = collect_source_text()
        check("frontend source is non-empty", bool(source_text.strip()))
        log("source_files", {
            "count": len(source_files),
            "files": [str(p.relative_to(REPO_ROOT)) for p in source_files],
        })

        # 2. API base URL config present.
        api_ts_text = read_text(WEB_SRC_DIR / "api.ts") or source_text
        has_env_var = "VITE_PROOFSTUDIO_API_BASE_URL" in api_ts_text
        has_fallback = "http://127.0.0.1:8000" in api_ts_text
        summary["api_base_config_present"] = bool(has_env_var and has_fallback)
        check(
            "api base url config present",
            summary["api_base_config_present"],
            detail=(
                f"env_var={has_env_var} fallback={has_fallback}; "
                "expected VITE_PROOFSTUDIO_API_BASE_URL + http://127.0.0.1:8000"
            ),
        )
        log("api_base_config", {
            "env_var": has_env_var,
            "fallback": has_fallback,
        })

        # 3. UI source references every required endpoint.
        missing_endpoints = [
            ep for ep in REQUIRED_ENDPOINT_MARKERS if ep not in source_text
        ]
        check(
            "all required endpoints referenced",
            not missing_endpoints,
            detail=f"missing endpoint markers: {missing_endpoints}",
        )
        log("endpoint_references", {"missing": missing_endpoints})

        # 4. Required UI sections present.
        section_results: dict[str, bool] = {}
        missing_sections: list[str] = []
        for name, markers in SECTION_MARKERS.items():
            present = any(m in source_text for m in markers)
            section_results[name] = present
            if not present:
                missing_sections.append(name)
        summary["health_section_present"] = section_results["health"]
        summary["campaign_builder_present"] = section_results["campaign_builder"]
        summary["run_creator_present"] = section_results["run_creator"]
        summary["evidence_overview_present"] = section_results["evidence_overview"]
        summary["attempts_panel_present"] = section_results["attempts"]
        summary["assets_panel_present"] = section_results["assets"]
        summary["manifest_panel_present"] = section_results["manifest"]
        summary["passport_panel_present"] = section_results["passport"]
        summary["trust_boundary_present"] = section_results["trust_boundary"]
        check(
            "all required UI sections present",
            not missing_sections,
            detail=f"missing sections: {missing_sections}",
        )
        log("ui_sections", section_results)

        # 5. run_live defaults safe/false.
        # Accept either an explicit useState(false) default on a runLive
        # state, or a run_live literal that defaults to false.
        run_live_safe = bool(
            re.search(r"runLive[^=]*=\s*useState\(\s*false\s*\)", source_text)
            or re.search(r"run_live\s*:\s*false", source_text)
        )
        summary["default_run_live_safe"] = run_live_safe
        check(
            "run_live defaults to false/safe",
            run_live_safe,
            detail="no safe run_live=false default found in UI source",
        )
        log("run_live_default", {"safe": run_live_safe})

        # 6. Live mode warning present.
        has_live_warning = LIVE_WARNING in source_text
        summary["live_mode_warning_present"] = has_live_warning
        check(
            "live mode warning present",
            has_live_warning,
            detail=f"expected exact text: {LIVE_WARNING!r}",
        )
        log("live_mode_warning", {"present": has_live_warning})

        # 7. No hardcoded fake media success.
        media_hits = scan_patterns(source_text, FAKE_MEDIA_PATTERNS)
        summary["no_fake_media"] = not media_hits
        check(
            "no hardcoded fake media success",
            not media_hits,
            detail=f"matched patterns: {media_hits}",
        )
        log("fake_media_scan", {"hits": media_hits})

        # 8. No hardcoded fake manifest success.
        manifest_hits = scan_patterns(source_text, FAKE_MANIFEST_PATTERNS)
        summary["no_fake_manifest"] = not manifest_hits
        check(
            "no hardcoded fake manifest success",
            not manifest_hits,
            detail=f"matched patterns: {manifest_hits}",
        )
        log("fake_manifest_scan", {"hits": manifest_hits})

        # 9. No obvious secrets in the frontend source.
        secret_hits: list[str] = []
        for f in source_files:
            secret_hits.extend(scan_patterns(read_text(f), SECRET_PATTERNS))
        # Also scan the whole blob once more for resilience.
        secret_hits.extend(scan_patterns(source_text, SECRET_PATTERNS))
        secret_hits = sorted(set(secret_hits))
        summary["no_secrets"] = not secret_hits
        check(
            "no secrets in frontend source",
            not secret_hits,
            detail=f"matched patterns: {secret_hits[:5]}",
        )
        log("secret_scan", {"hits": secret_hits})

        # 10. Best-effort build (never required for ok).
        build_checked, build_status, build_detail = attempt_build()
        summary["build_checked"] = build_checked
        summary["build_status"] = build_status
        log("build", {
            "checked": build_checked,
            "status": build_status,
            "detail": build_detail,
        })

        ok = bool(
            summary["package_file_present"]
            and summary["api_base_config_present"]
            and summary["health_section_present"]
            and summary["campaign_builder_present"]
            and summary["run_creator_present"]
            and summary["evidence_overview_present"]
            and summary["attempts_panel_present"]
            and summary["assets_panel_present"]
            and summary["manifest_panel_present"]
            and summary["passport_panel_present"]
            and summary["trust_boundary_present"]
            and summary["default_run_live_safe"]
            and summary["live_mode_warning_present"]
            and summary["no_fake_media"]
            and summary["no_fake_manifest"]
            and summary["no_secrets"]
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
                "slice": "PS-013",
                "frontend_type": summary.get("frontend_type"),
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
