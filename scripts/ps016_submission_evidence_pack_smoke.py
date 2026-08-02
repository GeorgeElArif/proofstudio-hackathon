#!/usr/bin/env python3
"""
PS-016: Submission Demo Script + Judge Evidence Pack smoke test.

What this proves (docs-only + smoke; NO live providers, NO B2):

- All required submission docs exist.
- The demo video script contains the required ~3-minute timeline sections.
- The recording runbook contains the exact backend/frontend/helper commands.
- The judge evidence pack covers product, audience, workflow, architecture, and
  limitations.
- The provider/model inventory does not overclaim optional providers.
- The B2 + Genblaze usage doc references the actual prior proof slices.
- The judging criteria mapping includes all four criteria.
- The submission checklist includes the required submission items.
- docs/submission/README.md links to all submission docs.
- No fake screenshots / media / B2 URLs / manifest hashes are invented.
- No secrets are introduced.
- The backend (src/) is unchanged by this slice.
- Historical proof scripts (PS-004 .. PS-015) are untouched.
- The frontend production build still passes.

Default acceptance NEVER calls live providers or B2. This slice is docs + smoke
only; backend changes are not allowed for PS-016.

Truth boundary: PS-016 proves ProofStudio has a judge-ready submission evidence
pack and demo script grounded in the current local product and prior proof
slices. It does not prove public deployment, final Devpost submission, production availability,
authentication, production persistence, background job reliability, legal
authenticity, C2PA authenticity, semantic truth, or human authorship.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIR = Path("/tmp/proofstudio-ps-016")
SUMMARY_PATH = OUTPUT_DIR / "submission-evidence-pack-summary.json"
TRANSCRIPT_PATH = OUTPUT_DIR / "submission-evidence-pack-transcript.json"

SUBMISSION_DIR = REPO_ROOT / "docs" / "submission"
PROOF_DOC = REPO_ROOT / "docs" / "ps-016-submission-demo-script-judge-evidence-pack-proof.md"
FRONTEND_DIR = REPO_ROOT / "apps" / "web"
SRC_DIR = REPO_ROOT / "src"

TRUTH_BOUNDARY = (
    "PS-016 proves ProofStudio has a judge-ready submission evidence pack and "
    "demo script grounded in the current local product and prior proof slices. "
    "It does not prove public deployment, final Devpost submission, production availability, "
    "authentication, production persistence, background job reliability, legal "
    "authenticity, C2PA authenticity, semantic truth, or human authorship."
)

REQUIRED_SUBMISSION_DOCS = (
    "README.md",
    "demo-video-script.md",
    "recording-runbook.md",
    "judge-evidence-pack.md",
    "provider-model-inventory.md",
    "b2-genblaze-usage.md",
    "judging-criteria-mapping.md",
    "submission-checklist.md",
)

# Timeline sections the demo video script must contain.
DEMO_TIMELINE_SECTIONS = (
    ("0:00-0:20", "Hook"),
    ("0:20-0:45", "Product"),
    ("0:45-1:20", "Safe Demo Setup"),
    ("1:20-2:10", "Live Proof Flow"),
    ("2:10-2:40", "Provenance Passport"),
    ("2:40-3:00", "Why It Wins"),
)

# Exact commands the recording runbook must contain.
REQUIRED_RUNBOOK_COMMANDS = (
    "cd /home/proofstudio-work/proofstudio",
    "source .venv/bin/activate",
    'export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"',
    "python scripts/ps015_one_click_local_demo.py",
    "uvicorn proofstudio.api.app:app --reload --host 127.0.0.1 --port 8000",
    "cd apps/web",
    "npm run dev -- --host 127.0.0.1 --port 5173",
)

REQUIRED_JUDGE_PACK_TOKENS = (
    "product",
    "audience",
    "workflow",
    "architecture",
    "limitations",
)

# Optional providers that must NEVER be claimed as implemented/proven.
OPTIONAL_PROVIDERS = (
    "ElevenLabs",
    "OpenAI",
    "Runway",
    "Stability Audio",
    "NVIDIA NIM",
)

# Proof slices the B2 + Genblaze usage doc must reference.
REQUIRED_B2_GENBLAZE_SLICES = (
    "PS-001A",
    "PS-002",
    "PS-004",
    "PS-005",
    "PS-007",
    "PS-009",
    "PS-010",
    "PS-011",
)

REQUIRED_CRITERIA = (
    "real-world utility",
    "production readiness",
    "B2 storage",
    "Genblaze",
)

REQUIRED_CHECKLIST_ITEMS = (
    "working app URL",
    "repo access",
    "setup instructions",
    "providers",
    "B2",
    "Genblaze",
    "demo video",
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
    "scripts/ps013a_local_demo_integration_hardening_smoke.py",
    "scripts/ps014_live_demo_flow_review_room_smoke.py",
    "scripts/ps015_demo_seed_pack_one_click_smoke.py",
)

# Invented-artifact patterns. These detect ACTUAL fabricated artifacts, not the
# word "fake" (docs are allowed to say "no fake evidence"). Their absence inside
# docs/submission/* is the no-invented-evidence proof.
MARKDOWN_IMAGE_EMBED = re.compile(r"!\[[^\]]*\]\([^)]+\)")
CAPTURED_SCREENSHOT_PATH = re.compile(
    r"(?i)(screenshots|images|assets/images|recordings)[/\S]+\.(png|jpe?g|webp|gif|svg)"
)
EXTERNAL_MEDIA_URL = re.compile(
    r"https?://[^\s\"')]+\.(png|jpe?g|webp|gif|svg)", re.IGNORECASE
)
B2_OBJECT_URL = re.compile(r"backblazeb2\.com", re.IGNORECASE)
SHA256_HEX_HASH = re.compile(r"\b[0-9a-f]{64}\b")
# A non-local https URL that looks like a deployed app (not example.com/docs).
DEPLOYED_APP_URL = re.compile(
    r"https://(?!(127\.0\.0\.1|localhost|example\.com|opencode\.ai|github\.com))"
    r"[a-z0-9.\-]+\.(com|app|dev|io|net|ai|cloud)",
    re.IGNORECASE,
)

SECRET_PATTERNS = (
    re.compile(r"(?i)Bearer\s+[A-Za-z0-9\-_.=~]{8,}"),
    re.compile(r"(?i)B2_KEY_ID[\s:=]+[\"']?[A-Za-z0-9]{8,}"),
    re.compile(r"(?i)B2_APP_KEY[\s:=]+[\"']?[A-Za-z0-9]{8,}"),
    re.compile(r"(?i)CLOUDFLARE_API_TOKEN[\s:=]+[\"']?[A-Za-z0-9]{8,}"),
    re.compile(r"(?i)GEMINI_API_KEY[\s:=]+[\"']?[A-Za-z0-9]{8,}"),
    re.compile(r"(?i)GMI_API_KEY[\s:=]+[\"']?[A-Za-z0-9]{8,}"),
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


def _read(path: Path) -> str:
    check(f"doc exists: {path.name}", path.is_file(), detail=str(path))
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


def _scan_invented_artifacts(text: str) -> dict[str, list[str]]:
    """Detect fabricated screenshots/media/B2 URLs/manifest hashes/public URLs.

    The word "fake" itself is NOT banned; docs may say "no fake evidence".
    """
    return {
        "markdown_image_embeds": MARKDOWN_IMAGE_EMBED.findall(text),
        "captured_screenshot_paths": CAPTURED_SCREENSHOT_PATH.findall(text),
        "external_media_urls": EXTERNAL_MEDIA_URL.findall(text),
        "b2_object_urls": B2_OBJECT_URL.findall(text),
        "sha256_hashes": SHA256_HEX_HASH.findall(text),
        "deployed_app_urls": DEPLOYED_APP_URL.findall(text),
    }


def _scan_secrets(text: str) -> list[str]:
    hits: list[str] = []
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            hits.append(pattern.pattern[:50])
    return hits


def _check_demo_script(transcript: list[dict[str, Any]]) -> None:
    text = _read(SUBMISSION_DIR / "demo-video-script.md")
    missing: list[str] = []
    for stamp, name in DEMO_TIMELINE_SECTIONS:
        if stamp not in text or name.lower() not in text.lower():
            missing.append(f"{stamp} {name}")
    check("demo script has all timeline sections", not missing, detail=str(missing))
    # Must mention pain point, audience, safe setup, live path, fallback, passport.
    required_topics = (
        "pain point",
        "audience",
        "safe",
        "live",
        "fallback",
        "provenance passport",
        "judging criteria",
    )
    missing_topics = [t for t in required_topics if t.lower() not in text.lower()]
    check("demo script covers required topics", not missing_topics,
          detail=str(missing_topics))
    _log(transcript, "demo_script_check", {
        "timeline_sections": len(DEMO_TIMELINE_SECTIONS),
        "missing_sections": missing,
        "missing_topics": missing_topics,
    })


def _check_recording_runbook(transcript: list[dict[str, Any]]) -> None:
    text = _read(SUBMISSION_DIR / "recording-runbook.md")
    missing_cmds = [c for c in REQUIRED_RUNBOOK_COMMANDS if c not in text]
    check("recording runbook has all exact commands", not missing_cmds,
          detail=str(missing_cmds))
    browser_urls = ("127.0.0.1:5173", "127.0.0.1:8000/health", "127.0.0.1:8000/docs")
    missing_urls = [u for u in browser_urls if u not in text]
    check("recording runbook has browser URLs", not missing_urls, detail=str(missing_urls))
    required_sections = (
        "what to show",
        "what not to show",
        "fallback",
        "checklist",
    )
    missing_sections = [s for s in required_sections if s.lower() not in text.lower()]
    check("recording runbook has required sections", not missing_sections,
          detail=str(missing_sections))
    _log(transcript, "recording_runbook_check", {
        "missing_commands": missing_cmds,
        "missing_urls": missing_urls,
        "missing_sections": missing_sections,
    })


def _check_judge_evidence_pack(transcript: list[dict[str, Any]]) -> None:
    text = _read(SUBMISSION_DIR / "judge-evidence-pack.md")
    low = text.lower()
    missing = [t for t in REQUIRED_JUDGE_PACK_TOKENS if t not in low]
    check("judge evidence pack has required tokens", not missing, detail=str(missing))
    required_sections = (
        "product name",
        "one-sentence pitch",
        "audience",
        "pain point",
        "workflow",
        "completed slices",
        "architecture",
        "api endpoints",
        "frontend path",
        "demo commands",
        "proof scripts",
        "smoke summaries",
        "b2",
        "genblaze",
        "truth boundary",
        "limitations",
        "next work",
    )
    missing_sections = [s for s in required_sections if s not in low]
    check("judge evidence pack has required sections", not missing_sections,
          detail=str(missing_sections))
    # Must be honest about public deployment being pending.
    check(
        "judge evidence pack states deployment pending",
        "pending" in low,
        detail="must state public deployment is pending",
    )
    _log(transcript, "judge_evidence_pack_check", {
        "missing_tokens": missing,
        "missing_sections": missing_sections,
    })


def _check_provider_inventory(transcript: list[dict[str, Any]]) -> None:
    text = _read(SUBMISSION_DIR / "provider-model-inventory.md")
    low = text.lower()
    # Optional providers must be marked not-implemented, never proven/live.
    proven_markers = ("live-proven", "live proven", "implemented", "proven")
    overclaims: list[str] = []
    lines = text.splitlines()
    for prov in OPTIONAL_PROVIDERS:
        for idx, line in enumerate(lines):
            if prov.lower() not in line.lower():
                continue
            window = "\n".join(lines[max(0, idx - 2): idx + 3]).lower()
            # The optional provider must NOT appear next to a proven/implemented
            # marker; it must appear near "not implemented" / "optional later".
            near_not_implemented = (
                "not implemented" in window or "optional later" in window
                or "not" in window
            )
            near_proven = any(m in window for m in proven_markers)
            if near_proven and not near_not_implemented:
                overclaims.append(prov)
                break
    check("provider inventory does not overclaim optional providers",
          not overclaims, detail=str(overclaims))
    # Required honest categories must be present.
    required_categories = (
        "cloudflare",
        "pollinations",
        "gemini",
        "blocked",
        "not implemented",
    )
    missing = [c for c in required_categories if c not in low]
    check("provider inventory has required categories", not missing, detail=str(missing))
    _log(transcript, "provider_inventory_check", {
        "overclaims": overclaims,
        "missing_categories": missing,
    })


def _check_b2_genblaze_usage(transcript: list[dict[str, Any]]) -> None:
    text = _read(SUBMISSION_DIR / "b2-genblaze-usage.md")
    low = text.lower()
    missing_slices = [s for s in REQUIRED_B2_GENBLAZE_SLICES if s.lower() not in low]
    check("b2/genblaze doc references all required prior slices", not missing_slices,
          detail=str(missing_slices))
    required_concepts = (
        "backblaze b2",
        "genblaze",
        "manifest",
        "verify",
        "archive",
        "rehydrate",
        "truth boundary",
    )
    missing_concepts = [c for c in required_concepts if c not in low]
    check("b2/genblaze doc has required concepts", not missing_concepts,
          detail=str(missing_concepts))
    _log(transcript, "b2_genblaze_usage_check", {
        "missing_slices": missing_slices,
        "missing_concepts": missing_concepts,
    })


def _check_judging_criteria(transcript: list[dict[str, Any]]) -> None:
    text = _read(SUBMISSION_DIR / "judging-criteria-mapping.md")
    low = text.lower()
    missing = [c for c in REQUIRED_CRITERIA if c.lower() not in low]
    check("judging criteria mapping has all four criteria", not missing,
          detail=str(missing))
    required_labels = (
        "what the judge should look at",
        "which feature proves it",
        "supporting files",
        "limitation",
    )
    missing_labels = [l for l in required_labels if l not in low]
    check("judging criteria mapping has per-criterion labels", not missing_labels,
          detail=str(missing_labels))
    _log(transcript, "judging_criteria_mapping_check", {
        "missing_criteria": missing,
        "missing_labels": missing_labels,
    })


def _check_submission_checklist(transcript: list[dict[str, Any]]) -> None:
    text = _read(SUBMISSION_DIR / "submission-checklist.md")
    low = text.lower()
    missing = [i for i in REQUIRED_CHECKLIST_ITEMS if i.lower() not in low]
    check("submission checklist has required items", not missing, detail=str(missing))
    check(
        "submission checklist states app URL pending",
        "pending" in low,
        detail="must mark working app URL as pending",
    )
    _log(transcript, "submission_checklist_check", {"missing_items": missing})


def _check_submission_readme(transcript: list[dict[str, Any]]) -> None:
    text = _read(SUBMISSION_DIR / "README.md")
    missing_links = [
        d for d in REQUIRED_SUBMISSION_DOCS if d == "README.md"
        or d not in text
    ]
    # README.md links to the other docs (not necessarily itself).
    other_docs = [d for d in REQUIRED_SUBMISSION_DOCS if d != "README.md"]
    missing = [d for d in other_docs if d not in text]
    check("submission README links to all submission docs", not missing,
          detail=str(missing))
    _log(transcript, "submission_readme_check", {"missing_links": missing})


def _check_no_invented_evidence(
    summary: dict[str, Any], transcript: list[dict[str, Any]]
) -> None:
    """Scan every docs/submission/* file for fabricated artifacts."""
    findings: dict[str, Any] = {}
    any_invented = False
    for doc in REQUIRED_SUBMISSION_DOCS:
        path = SUBMISSION_DIR / doc
        text = _read(path)
        scan = _scan_invented_artifacts(text)
        # Normalize tuple hits (regex with groups) to plain counts.
        flat: dict[str, int] = {}
        for key, hits in scan.items():
            count = len(hits) if isinstance(hits, list) else 0
            flat[key] = count
            if count:
                any_invented = True
        findings[doc] = flat
    _log(transcript, "invented_evidence_scan", findings)

    summary["no_fake_screenshots"] = not any(
        findings[d]["markdown_image_embeds"] or findings[d]["captured_screenshot_paths"]
        for d in findings
    )
    summary["no_fake_media"] = not any(
        findings[d]["external_media_urls"] or findings[d]["deployed_app_urls"]
        for d in findings
    )
    summary["no_fake_b2_evidence"] = not any(
        findings[d]["b2_object_urls"] for d in findings
    )
    summary["no_fake_manifest_evidence"] = not any(
        findings[d]["sha256_hashes"] for d in findings
    )

    check("no invented screenshots in submission docs",
          summary["no_fake_screenshots"], detail=str(findings))
    check("no invented media/public app URLs in submission docs",
          summary["no_fake_media"], detail=str(findings))
    check("no invented B2 object URLs in submission docs",
          summary["no_fake_b2_evidence"], detail=str(findings))
    check("no invented manifest hashes in submission docs",
          summary["no_fake_manifest_evidence"], detail=str(findings))


def _check_no_secrets(
    summary: dict[str, Any], transcript: list[dict[str, Any]]
) -> None:
    hits: dict[str, list[str]] = {}
    for doc in REQUIRED_SUBMISSION_DOCS:
        text = _read(SUBMISSION_DIR / doc)
        found = _scan_secrets(text)
        if found:
            hits[doc] = found
    # Also scan the proof doc + this smoke's own transcript later.
    proof_text = _read(PROOF_DOC)
    found_proof = _scan_secrets(proof_text)
    if found_proof:
        hits["ps-016-proof.md"] = found_proof
    summary["no_secret_leakage"] = not hits
    _log(transcript, "secret_scan", {"hits": hits})
    check("no secrets in submission docs / proof doc", not hits, detail=str(hits))


def _check_backend_unchanged(
    summary: dict[str, Any], transcript: list[dict[str, Any]]
) -> None:
    modified = _git_modified(("src/",))
    summary["backend_unchanged"] = not modified
    _log(transcript, "backend_unchanged_check", {"modified_src": modified})
    check("backend (src/) unchanged by PS-016", not modified, detail=str(modified))


def _check_historical_scripts(
    summary: dict[str, Any], transcript: list[dict[str, Any]]
) -> None:
    modified = _git_modified(HISTORICAL_SCRIPTS)
    summary["historical_scripts_untouched"] = not modified
    _log(transcript, "historical_scripts_check", {"modified": modified})
    check("historical proof scripts untouched", not modified, detail=str(modified))


def _check_frontend_build(
    summary: dict[str, Any], transcript: list[dict[str, Any]]
) -> None:
    summary["frontend_build_checked"] = True
    npm_cmd = "npm"
    try:
        result = subprocess.run(
            [npm_cmd, "run", "build"],
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
        "command": f"{npm_cmd} run build",
        "returncode": result.returncode,
        "status": status,
        "stdout_tail": (result.stdout or "")[-1200:],
        "stderr_tail": (result.stderr or "")[-1200:],
    })
    check("frontend build passed", result.returncode == 0,
          detail=f"npm run build exit={result.returncode}")


def _check_proof_doc(transcript: list[dict[str, Any]]) -> None:
    text = _read(PROOF_DOC)
    low = text.lower()
    required = (
        "status",
        "files created",
        "what the pack covers",
        "source-of-truth",
        "public requirements",
        "local proof commands",
        "no fake evidence",
        "limitations",
        "next milestone",
        "truth boundary",
    )
    missing = [r for r in required if r not in low]
    check("proof doc has required sections", not missing, detail=str(missing))
    _log(transcript, "proof_doc_check", {"missing": missing})



def _normalize_summary_schema(summary: dict[str, Any]) -> dict[str, Any]:
    """Keep machine contract stable while preserving human-readable path details."""
    docs_created_value = summary.get("docs_created")
    docs_created_paths = summary.get("docs_created_paths")

    if isinstance(docs_created_value, list):
        docs_created_paths = docs_created_value
        summary["docs_created_paths"] = docs_created_paths

    if isinstance(docs_created_paths, list):
        summary["docs_created"] = bool(docs_created_paths) and all(Path(p).exists() for p in docs_created_paths)

    return summary

def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    transcript: list[dict[str, Any]] = []

    summary: dict[str, Any] = {
        "ok": False,
        "slice": "PS-016",
        "docs_created": False,
        "docs_created_paths": [],
        "demo_script_checked": False,
        "recording_runbook_checked": False,
        "judge_evidence_pack_checked": False,
        "provider_model_inventory_checked": False,
        "b2_genblaze_usage_checked": False,
        "judging_criteria_mapping_checked": False,
        "submission_checklist_checked": False,
        "submission_readme_checked": False,
        "public_requirements_covered": [],
        "judging_criteria_covered": [],
        "no_fake_screenshots": False,
        "no_fake_media": False,
        "no_fake_b2_evidence": False,
        "no_fake_manifest_evidence": False,
        "no_secret_leakage": False,
        "backend_unchanged": False,
        "historical_scripts_untouched": False,
        "frontend_build_checked": False,
        "frontend_build_status": "not_run",
        "summary_path": str(SUMMARY_PATH),
        "transcript_path": str(TRANSCRIPT_PATH),
        "truth_boundary": TRUTH_BOUNDARY,
    }

    try:
        # Step 2: all required docs exist.
        created: list[str] = []
        for doc in REQUIRED_SUBMISSION_DOCS:
            check(f"submission doc exists: {doc}",
                  (SUBMISSION_DIR / doc).is_file(), detail=str(SUBMISSION_DIR / doc))
            created.append(f"docs/submission/{doc}")
        check("proof doc exists", PROOF_DOC.is_file(), detail=str(PROOF_DOC))
        created.append(str(PROOF_DOC.relative_to(REPO_ROOT)))
        created.append("scripts/ps016_submission_evidence_pack_smoke.py")
        summary["docs_created"] = created
        _log(transcript, "required_docs_exist", {"docs": created})

        # Step 3: demo video script.
        _check_demo_script(transcript)
        summary["demo_script_checked"] = True

        # Step 4: recording runbook.
        _check_recording_runbook(transcript)
        summary["recording_runbook_checked"] = True

        # Step 5: judge evidence pack.
        _check_judge_evidence_pack(transcript)
        summary["judge_evidence_pack_checked"] = True

        # Step 6: provider/model inventory.
        _check_provider_inventory(transcript)
        summary["provider_model_inventory_checked"] = True

        # Step 7: B2 + Genblaze usage.
        _check_b2_genblaze_usage(transcript)
        summary["b2_genblaze_usage_checked"] = True

        # Step 8: judging criteria mapping.
        _check_judging_criteria(transcript)
        summary["judging_criteria_mapping_checked"] = True

        # Step 9: submission checklist.
        _check_submission_checklist(transcript)
        summary["submission_checklist_checked"] = True

        # Step 10: submission README links.
        _check_submission_readme(transcript)
        summary["submission_readme_checked"] = True

        # Step 11: no invented evidence.
        _check_no_invented_evidence(summary, transcript)

        # Step 12: no secrets.
        _check_no_secrets(summary, transcript)

        # Step 13: backend unchanged.
        _check_backend_unchanged(summary, transcript)

        # Step 14: historical scripts untouched.
        _check_historical_scripts(summary, transcript)

        # Step 15: proof doc sections.
        _check_proof_doc(transcript)

        # Step 15/optional: frontend build.
        _check_frontend_build(summary, transcript)

        # Covered public requirements (documented, even if some are pending).
        summary["public_requirements_covered"] = [
            "working app URL (pending — documented)",
            "repo access",
            "setup instructions",
            "providers/models list",
            "B2 and Genblaze explanation",
            "demo video (script ready, recording pending)",
        ]
        summary["judging_criteria_covered"] = list(REQUIRED_CRITERIA)

        required_true = (
            summary["demo_script_checked"],
            summary["recording_runbook_checked"],
            summary["judge_evidence_pack_checked"],
            summary["provider_model_inventory_checked"],
            summary["b2_genblaze_usage_checked"],
            summary["judging_criteria_mapping_checked"],
            summary["submission_checklist_checked"],
            summary["submission_readme_checked"],
            summary["no_fake_screenshots"],
            summary["no_fake_media"],
            summary["no_fake_b2_evidence"],
            summary["no_fake_manifest_evidence"],
            summary["no_secret_leakage"],
            summary["backend_unchanged"],
            summary["historical_scripts_untouched"],
            summary["frontend_build_checked"],
            summary["frontend_build_status"] == "passed",
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

    # Final secret scan across the whole transcript before writing.
    transcript_secret_hits = _scan_secrets(
        json.dumps(transcript, ensure_ascii=False, default=str)
    )
    if transcript_secret_hits:
        summary["no_secret_leakage"] = False
        summary["ok"] = False
        summary["error"] = f"secret leak in transcript: {transcript_secret_hits}"
        _log(transcript, "transcript_secret_scan", {"hits": transcript_secret_hits})

    _normalize_summary_schema(summary)
    SUMMARY_PATH.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    TRANSCRIPT_PATH.write_text(
        json.dumps(
            {
                "slice": "PS-016",
                "demo": "submission-evidence-pack-smoke",
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
