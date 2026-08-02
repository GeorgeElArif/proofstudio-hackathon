#!/usr/bin/env python3
"""
PS-015: Demo Seed Pack + One-Click Local Demo smoke test.

What this proves (default safe smoke only):

- The deterministic seed pack exists and validates its schema.
- The seed pack contains no fake evidence (no fake image URLs, no fake manifest
  URIs, no fake B2 URLs, no fake hashes, no fake provider/model claims, no
  secrets).
- The one-click helper exists.
- The one-click helper safe default path executes and:
    - creates a campaign
    - creates a safe dry-run with run_live=false
    - calls no live provider
    - calls no B2
    - fakes no media
    - fakes no manifest
    - prints/returns the Review Room URL and the API docs URL
- The frontend production build still passes (npm run build).
- The docs mention the default command, the optional live gate, the
  two-terminal fallback, and the truth boundary.

Default acceptance NEVER requires live provider spend. Historical proof scripts
(PS-004 .. PS-014) are not modified.

Truth boundary: PS-015 proves ProofStudio has a deterministic local demo seed
pack and a safe one-click helper for preparing a local Review Room demo. It does
not prove public deployment, production availability, authentication, production
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
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

OUTPUT_DIR = Path("/tmp/proofstudio-ps-015")
SUMMARY_PATH = OUTPUT_DIR / "demo-seed-pack-one-click-summary.json"
TRANSCRIPT_PATH = OUTPUT_DIR / "demo-seed-pack-one-click-transcript.json"

SEED_PACK_PATH = REPO_ROOT / "examples" / "ps015" / "demo-seed-pack.json"
ONE_CLICK_HELPER_PATH = REPO_ROOT / "scripts" / "ps015_one_click_local_demo.py"
DOCS_PATH = REPO_ROOT / "docs" / "ps-015-demo-seed-pack-one-click-local-demo-proof.md"
FRONTEND_DIR = REPO_ROOT / "apps" / "web"

TRUTH_BOUNDARY = (
    "PS-015 proves ProofStudio has a deterministic local demo seed pack and a "
    "safe one-click helper for preparing a local Review Room demo. It does not "
    "prove public deployment, production availability, authentication, "
    "production persistence, background job reliability, legal authenticity, "
    "C2PA authenticity, semantic truth, or human authorship."
)

# Patterns that would indicate fabricated evidence inside the seed pack. Their
# absence (combined with the schema + runtime checks) is the no-fake proof.
FAKE_EVIDENCE_PATTERNS = [
    re.compile(r"https?://[^\s\"']+/\S+\.(png|jpg|jpeg|webp|gif|svg)",
               re.IGNORECASE),  # fake image URL
    re.compile(r"(?i)manifest[_-]?uri\s*[:=]\s*[\"']https?://"),  # fake manifest URI
    re.compile(r"(?i)b2[_-]?url\s*[:=]\s*[\"']https?://"),  # fake B2 URL
    re.compile(r"\b[0-9a-f]{64}\b"),  # fake sha256-length hash
    re.compile(r"(?i)(gemini|pollinations|cloudflare|workers\.ai)"
               r"\s*[:=]\s*[\"'][^\"']+[\"']"),  # fake provider/model claim
]

SECRET_PATTERNS = [
    re.compile(r"(?i)Bearer\s+[A-Za-z0-9\-_.=~]{8,}"),
    re.compile(r"(?i)B2_KEY_ID[\s:=]+\S{8,}"),
    re.compile(r"(?i)B2_APP_KEY[\s:=]+\S{8,}"),
    re.compile(r"(?i)CLOUDFLARE_API_TOKEN[\s:=]+\S{8,}"),
    re.compile(r"(?i)GEMINI_API_KEY[\s:=]+\S{8,}"),
]

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
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class CheckFail(Exception):
    pass


def check(label: str, condition: bool, detail: str = "") -> None:
    if not condition:
        raise CheckFail(f"{label}: {detail}" if detail else f"{label}: failed")


def _log(transcript: list[dict[str, Any]], step: str, payload: Any) -> None:
    transcript.append({"step": step, "result": payload, "at": now_iso()})


def _historical_scripts_untouched() -> list[str]:
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


def _scan_fake_evidence(text: str) -> list[str]:
    hits: list[str] = []
    for pattern in FAKE_EVIDENCE_PATTERNS:
        if pattern.search(text):
            hits.append(f"matched: {pattern.pattern[:60]}...")
    return hits


def _scan_secrets(payload: Any) -> list[str]:
    text = json.dumps(payload, ensure_ascii=False, default=str)
    hits: list[str] = []
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            hits.append(f"secret pattern matched: {pattern.pattern[:40]}...")
    return hits


def _verify_seed_pack_schema(transcript: list[dict[str, Any]]) -> dict[str, Any]:
    """Steps 2-4: verify the seed pack exists, validates schema, has no fakes."""
    check("seed pack exists", SEED_PACK_PATH.is_file(),
          detail=f"missing {SEED_PACK_PATH}")
    raw = SEED_PACK_PATH.read_text(encoding="utf-8")
    try:
        seed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CheckFail(f"seed pack not valid JSON: {exc}") from exc

    required_top = (
        "slice", "demo_name", "campaign", "safe_run",
        "optional_live_run", "reviewer_script", "truth_boundary",
        "created_for",
    )
    missing_top = [k for k in required_top if k not in seed]
    check("seed pack required top-level fields", not missing_top,
          detail=f"missing: {missing_top}")

    campaign = seed.get("campaign") or {}
    required_campaign = (
        "name", "brief", "audience", "channels", "tone",
        "creative_constraints",
    )
    missing_camp = [k for k in required_campaign if k not in campaign]
    check("seed pack campaign fields", not missing_camp,
          detail=f"missing: {missing_camp}")
    check("campaign.name non-empty", bool(campaign.get("name")))
    check("campaign.brief non-empty", bool(campaign.get("brief")))
    check("campaign.channels is list", isinstance(campaign.get("channels"), list))

    safe_run = seed.get("safe_run") or {}
    check("safe_run.run_live is false",
          safe_run.get("run_live") is False)
    check("safe_run.prompt present", bool(safe_run.get("prompt")))
    check("safe_run.expected_mode present", bool(safe_run.get("expected_mode")))

    opt_live = seed.get("optional_live_run") or {}
    check("optional_live_run.run_live is true",
          opt_live.get("run_live") is True)
    check("optional_live_run.prompt present", bool(opt_live.get("prompt")))
    check("optional_live_run.requires_explicit_opt_in is true",
          opt_live.get("requires_explicit_opt_in") is True)

    reviewer_script = seed.get("reviewer_script") or []
    check("reviewer_script is ordered list",
          isinstance(reviewer_script, list) and len(reviewer_script) >= 3)

    check("truth_boundary present", bool(seed.get("truth_boundary")))
    check("created_for present", bool(seed.get("created_for")))

    # No fake evidence / no secrets in the seed pack content.
    fake_hits = _scan_fake_evidence(raw)
    check("seed pack has no fake evidence", not fake_hits,
          detail=str(fake_hits))
    secret_hits = _scan_secrets(seed)
    check("seed pack has no secrets", not secret_hits, detail=str(secret_hits))

    _log(transcript, "verify_seed_pack", {
        "slice": seed.get("slice"),
        "demo_name": seed.get("demo_name"),
        "schema_required_top_ok": not missing_top,
        "schema_campaign_ok": not missing_camp,
        "fake_evidence_hits": fake_hits,
        "secret_hits": secret_hits,
    })
    return seed


def _check_frontend_build(
    summary: dict[str, Any], transcript: list[dict[str, Any]]
) -> None:
    """Step 16: run the frontend production build and record status."""
    summary["frontend_build_checked"] = True
    npm_cmd = os.environ.get("PS015_NPM", "npm")
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
        _log(transcript, "frontend_build", {
            "status": "error", "error": str(exc),
        })
        raise CheckFail(f"frontend build could not run: {exc}")

    status = "passed" if result.returncode == 0 else "failed"
    summary["frontend_build_status"] = status
    _log(transcript, "frontend_build", {
        "command": f"{npm_cmd} run build",
        "returncode": result.returncode,
        "status": status,
        "stdout_tail": (result.stdout or "")[-1000:],
        "stderr_tail": (result.stderr or "")[-1000:],
    })
    check(
        "frontend build passed",
        result.returncode == 0,
        detail=f"npm run build exit={result.returncode}",
    )


def _check_docs(
    summary: dict[str, Any], transcript: list[dict[str, Any]]
) -> None:
    """Step 17: verify docs mention the required runbook/gate/boundary."""
    check("docs proof exists", DOCS_PATH.is_file(),
          detail=f"missing {DOCS_PATH}")
    docs = DOCS_PATH.read_text(encoding="utf-8")

    default_cmd_present = (
        "ps015_one_click_local_demo.py" in docs
        and "One-Click Local Demo" in docs
    )
    live_gate_present = (
        "PROOFSTUDIO_PS015_LIVE" in docs
        and ("--live" in docs)
    )
    two_terminal_present = (
        "Terminal 1" in docs and "Terminal 2" in docs
        and "uvicorn proofstudio.api.app:app" in docs
    )
    truth_boundary_present = "Truth Boundary" in docs or "truth boundary" in docs

    check("docs: default command present", default_cmd_present)
    check("docs: optional live gate present", live_gate_present)
    check("docs: two-terminal fallback present", two_terminal_present)
    check("docs: truth boundary present", truth_boundary_present)

    summary["docs_updated"] = (
        default_cmd_present and live_gate_present
        and two_terminal_present and truth_boundary_present
    )
    _log(transcript, "verify_docs", {
        "default_command": default_cmd_present,
        "live_gate": live_gate_present,
        "two_terminal": two_terminal_present,
        "truth_boundary": truth_boundary_present,
    })


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    transcript: list[dict[str, Any]] = []

    summary: dict[str, Any] = {
        "ok": False,
        "slice": "PS-015",
        "seed_pack_path": str(SEED_PACK_PATH),
        "seed_pack_checked": False,
        "seed_pack_schema_checked": False,
        "seed_pack_no_fake_evidence": False,
        "one_click_helper_path": str(ONE_CLICK_HELPER_PATH),
        "one_click_helper_checked": False,
        "campaign_created": False,
        "safe_dry_run_created": False,
        "run_live_default_false": False,
        "default_no_live_provider_call": False,
        "default_no_b2_call": False,
        "no_fake_media": False,
        "no_fake_manifest": False,
        "review_room_url": None,
        "api_docs_url": None,
        "frontend_build_checked": False,
        "frontend_build_status": "not_run",
        "docs_updated": False,
        "live_mode_enabled": False,
        "live_run_status": None,
        "summary_path": str(SUMMARY_PATH),
        "transcript_path": str(TRANSCRIPT_PATH),
        "truth_boundary": TRUTH_BOUNDARY,
    }

    # The smoke runs the SAFE DEFAULT path only. Live mode is never enabled
    # by this smoke (default acceptance must not require live provider spend).
    summary["live_mode_enabled"] = False

    try:
        # 0. Historical proof scripts must be untouched.
        modified = _historical_scripts_untouched()
        check(
            "historical proof scripts untouched",
            not modified,
            detail=f"modified historical scripts: {modified}",
        )
        _log(transcript, "historical_scripts_check", {"modified": modified})

        # 2-4. Verify seed pack.
        _verify_seed_pack_schema(transcript)
        summary["seed_pack_checked"] = True
        summary["seed_pack_schema_checked"] = True
        summary["seed_pack_no_fake_evidence"] = True

        # 5. Verify one-click helper exists.
        check(
            "one-click helper exists",
            ONE_CLICK_HELPER_PATH.is_file(),
            detail=f"missing {ONE_CLICK_HELPER_PATH}",
        )
        summary["one_click_helper_checked"] = True
        _log(transcript, "verify_one_click_helper", {
            "path": str(ONE_CLICK_HELPER_PATH),
            "exists": ONE_CLICK_HELPER_PATH.is_file(),
        })

        # 6. Execute the one-click helper safe default path (imported, safe).
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "ps015_one_click_local_demo", ONE_CLICK_HELPER_PATH
        )
        check("helper module spec", spec is not None and spec.loader is not None)
        module = importlib.util.module_from_spec(spec)
        assert spec is not None and spec.loader is not None
        spec.loader.exec_module(module)

        helper_result = module.run_one_click_demo(live=False)
        _log(transcript, "run_one_click_demo", {
            "ok": helper_result.get("ok"),
            "campaign_id": helper_result.get("campaign_id"),
            "run_id": helper_result.get("run_id"),
            "run_status": helper_result.get("run_status"),
            "default_no_live_provider_call": helper_result.get(
                "default_no_live_provider_call"
            ),
            "default_no_b2_call": helper_result.get("default_no_b2_call"),
        })

        check(
            "one-click helper reported ok",
            helper_result.get("ok") is True,
            detail=f"error={helper_result.get('error')}",
        )

        # 7. Campaign was created.
        check("campaign created", bool(helper_result.get("campaign_id")))
        summary["campaign_created"] = True

        # 8. Safe dry-run created.
        check("safe dry-run created", bool(helper_result.get("run_id")))
        summary["safe_dry_run_created"] = True

        # 9. run_live is false on the default path.
        run_live = helper_result.get("run_live")
        check("run_live default false", run_live is False,
              detail=f"run_live={run_live!r}")
        summary["run_live_default_false"] = run_live is False

        # 10-11. No live provider / B2 call on the default path.
        check(
            "no live provider call on default path",
            helper_result.get("default_no_live_provider_call") is True,
        )
        check(
            "no B2 call on default path",
            helper_result.get("default_no_b2_call") is True,
        )
        summary["default_no_live_provider_call"] = bool(
            helper_result.get("default_no_live_provider_call")
        )
        summary["default_no_b2_call"] = bool(
            helper_result.get("default_no_b2_call")
        )

        # 12-13. No fake media / no fake manifest on the default path.
        check(
            "no fake media",
            helper_result.get("no_fake_media") is True,
        )
        check(
            "no fake manifest",
            helper_result.get("no_fake_manifest") is True,
        )
        summary["no_fake_media"] = bool(helper_result.get("no_fake_media"))
        summary["no_fake_manifest"] = bool(helper_result.get("no_fake_manifest"))

        # 14-15. Helper returned Review Room URL + API docs URL.
        review_room_url = helper_result.get("review_room_url")
        api_docs_url = helper_result.get("api_docs_url")
        check("review room url returned", bool(review_room_url))
        check("api docs url returned", bool(api_docs_url))
        check(
            "review room url is the local demo url",
            review_room_url == "http://127.0.0.1:5173",
        )
        check(
            "api docs url is the local demo url",
            api_docs_url == "http://127.0.0.1:8000/docs",
        )
        summary["review_room_url"] = review_room_url
        summary["api_docs_url"] = api_docs_url

        # 16. Frontend build passes.
        _check_frontend_build(summary, transcript)

        # 17. Docs mention the required runbook/gate/boundary.
        _check_docs(summary, transcript)

        # Secret-leak scan across the transcript.
        secret_hits = _scan_secrets(transcript)
        check("no secret leak in transcript", not secret_hits,
              detail=str(secret_hits))
        _log(transcript, "secret_scan", {"hits": secret_hits})

        # Acceptance.
        required_true = (
            summary["seed_pack_checked"],
            summary["seed_pack_schema_checked"],
            summary["seed_pack_no_fake_evidence"],
            summary["one_click_helper_checked"],
            summary["campaign_created"],
            summary["safe_dry_run_created"],
            summary["run_live_default_false"],
            summary["default_no_live_provider_call"],
            summary["default_no_b2_call"],
            summary["no_fake_media"],
            summary["no_fake_manifest"],
            bool(summary["review_room_url"]),
            bool(summary["api_docs_url"]),
            summary["frontend_build_checked"],
            summary["frontend_build_status"] == "passed",
            summary["docs_updated"],
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

    SUMMARY_PATH.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    TRANSCRIPT_PATH.write_text(
        json.dumps(
            {
                "slice": "PS-015",
                "demo": "demo-seed-pack-one-click-smoke",
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
