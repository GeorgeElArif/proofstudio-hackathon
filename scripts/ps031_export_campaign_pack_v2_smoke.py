#!/usr/bin/env python3
"""PS-031 Export Campaign Pack v2 -- smoke / validation script.

PS-034B retrofit: this smoke defaults to safe local / check-only
behavior. It does not recursively execute prior slice smokes, does
not run the frontend toolchain, does not use Git index hiding, does
not snapshot/restore prior evidence, and does not self-unlink its
evidence file. Evidence is written only when ``--write-evidence`` is
passed.

    python scripts/ps031_export_campaign_pack_v2_smoke.py --local --check-only

It statically validates the PS031 surface without starting a
browser, without calling any provider, without reading any B2 object,
and without enabling broad durable reads.

Truth boundary: this script validates that the PS031 surface
is honest. It does not prove semantic truth, legal authenticity,
C2PA authenticity, or human authorship.

Exit code is 0 only when every check passes.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import argparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import smoke_lib as sl  # noqa: E402
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

MANIFEST = REPO_ROOT / "docs" / "evidence" / "demo" / "golden-demo-run.json"
PS021_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "ps-021" / "live-b2-durable-rehydrate-smoke.json"
PS025_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "ps-025" / "public-durable-passport-unlock-smoke.json"
PS026_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "ps-026" / "b2-evidence-explorer-smoke.json"
PS027_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "ps-027" / "genblaze-pipeline-graph-smoke.json"
PS028_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "ps-028" / "manifest-verification-panel-smoke.json"
PS029_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "ps-029" / "b2-rehydrate-comparison-smoke.json"
PS030_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "ps-030" / "failure-as-proof-timeline-smoke.json"
ROADMAP = REPO_ROOT / "docs" / "roadmap" / "proofstudio-winning-implementation-roadmap-2026-06-29.md"

# PS-031 changed / added files.
PACK_CONST = REPO_ROOT / "apps" / "web" / "src" / "judgeEvidencePack.ts"
PACK_COMPONENT = REPO_ROOT / "apps" / "web" / "src" / "JudgeEvidencePack.tsx"
HOMEPAGE = REPO_ROOT / "apps" / "web" / "src" / "JudgeCockpitHome.tsx"
APP_TSX = REPO_ROOT / "apps" / "web" / "src" / "App.tsx"
FAILURE_TIMELINE_COMPONENT = REPO_ROOT / "apps" / "web" / "src" / "FailureAsProofTimeline.tsx"
B2_REHYDRATE_COMPONENT = REPO_ROOT / "apps" / "web" / "src" / "B2RehydrateComparison.tsx"
MANIFEST_PANEL = REPO_ROOT / "apps" / "web" / "src" / "ManifestVerificationPanel.tsx"
B2_EXPLORER = REPO_ROOT / "apps" / "web" / "src" / "B2EvidenceExplorer.tsx"
GENBLAZE_GRAPH = REPO_ROOT / "apps" / "web" / "src" / "GenblazePipelineGraph.tsx"
PUBLIC_PASSPORT = REPO_ROOT / "apps" / "web" / "src" / "PublicPassportPage.tsx"
STYLES = REPO_ROOT / "apps" / "web" / "src" / "styles.css"
PROOF_DOC = REPO_ROOT / "docs" / "ps-031-export-campaign-pack-v2-proof.md"

PS030_SMOKE = REPO_ROOT / "scripts" / "ps030_failure_as_proof_timeline_smoke.py"
PS029_SMOKE = REPO_ROOT / "scripts" / "ps029_b2_rehydrate_comparison_smoke.py"
PS028_SMOKE = REPO_ROOT / "scripts" / "ps028_manifest_verification_panel_smoke.py"
PS027_SMOKE = REPO_ROOT / "scripts" / "ps027_genblaze_pipeline_graph_smoke.py"
PS026_SMOKE = REPO_ROOT / "scripts" / "ps026_b2_evidence_explorer_smoke.py"
PS025_SMOKE = REPO_ROOT / "scripts" / "ps025_public_durable_passport_unlock_smoke.py"
PS024_SMOKE = REPO_ROOT / "scripts" / "ps024_golden_demo_run_pinning_smoke.py"
PS023_SMOKE = REPO_ROOT / "scripts" / "ps023_judge_cockpit_home_smoke.py"

EVIDENCE_OUT = REPO_ROOT / "docs" / "evidence" / "ps-031" / "export-campaign-pack-v2-smoke.json"

# Files scanned for secrets and forbidden claims. The scanner script itself
# is intentionally excluded: it legitimately contains the detection literals
# (same convention as PS-023 through PS-030 smokes).
SCAN_FILES: tuple[Path, ...] = (
    PACK_CONST,
    PACK_COMPONENT,
    HOMEPAGE,
    APP_TSX,
    FAILURE_TIMELINE_COMPONENT,
    B2_REHYDRATE_COMPONENT,
    MANIFEST_PANEL,
    B2_EXPLORER,
    GENBLAZE_GRAPH,
    PUBLIC_PASSPORT,
    STYLES,
    PROOF_DOC,
)

# Subset of SCAN_FILES scanned for forbidden broad-B2-read and provider-call
# code patterns. Markdown documentation (the proof doc) legitimately mentions
# these literals when describing what the smoke rejects, so it is excluded.
# Only source code files (ts/tsx/py) are scanned here.
PROVIDER_AND_B2_SCAN_FILES: tuple[Path, ...] = (
    PACK_CONST,
    PACK_COMPONENT,
    HOMEPAGE,
    APP_TSX,
    FAILURE_TIMELINE_COMPONENT,
    B2_REHYDRATE_COMPONENT,
    MANIFEST_PANEL,
    B2_EXPLORER,
    GENBLAZE_GRAPH,
    PUBLIC_PASSPORT,
    STYLES,
)

TRUTH_BOUNDARY_TERMS: tuple[str, ...] = (
    "semantic truth",
    "legal authenticity",
    "C2PA authenticity",
    "human authorship",
)

# Forbidden affirmative authenticity / overclaim phrases. Each is matched
# case-insensitively against a line; if the surrounding paragraph does not
# carry a non-claim context marker, the line is flagged.
FORBIDDEN_AFFIRMATIVE: tuple[str, ...] = (
    "the pack proves semantic truth",
    "the pack proves media is true",
    "the pack proves legal authenticity",
    "the pack proves human authorship",
    "the pack proves c2pa authenticity",
    "the pack proves object lock",
    "the pack proves tamper-proof storage",
    "the pack certifies authenticity",
    "the pack is a certification",
    "the pack is legally binding",
    "the pack includes raw media bytes",
    "the pack contains raw media bytes",
    "the pack produces a zip export",
    "the pack is a zip export",
    "the browser fetched and hashed the b2 object",
    "the browser verified the b2 bytes",
    "public deployment is verified",
    "public deployment verified",
    "object lock is enabled",
    "tamper-proof storage is enabled",
    "enterprise-grade security",
    "the pack is approved",
)

CONTEXT_MARKERS_RE = re.compile(
    r"does not|do not|must not|\bnot\b|non-claim|non-claims|forbidden|"
    r"reject|rejected|avoid|without overclaim|unless actually implemented|"
    r"only inside non-claim|limitation|limitations|no affirmative|"
    r"unavailable|blocked|honestly|no live|no_new|no_fake|pending|planned|"
    r"did not fetch|does not claim|did not claim|without|none claimed|"
    r"would appear|if captured|no actual|no fake|not implemented|"
    r"is not implemented|not a certification|not legal advice|"
    r"generated: false|approved: false",
    re.IGNORECASE,
)

FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")

SECRET_SUBSTRINGS: tuple[str, ...] = (
    "B2_APP_KEY=",
    "CLOUDFLARE_API_TOKEN=",
    "GEMINI_API_KEY=",
    "GMI_API_KEY=",
    "ELEVENLABS_API_KEY=",
    "Bearer ",
    "AKIA",
    "AWS_SECRET_ACCESS_KEY",
)
SECRET_KEY_RE = re.compile(r"(?<![A-Za-z])sk-[A-Za-z0-9]")

# Patterns that would indicate a new broad B2 object read path was introduced.
BROAD_B2_READ_PATTERNS: tuple[str, ...] = (
    "read_archive_from_b2",
    "b2.fetch",
    "b2GetObject",
    "list_b2_objects",
    "fetchB2Object",
    "fetch(",
)

# Patterns that would indicate a new provider call path was introduced.
PROVIDER_CALL_PATTERNS: tuple[str, ...] = (
    "call_provider",
    "fetchFromProvider",
    "requests.post",
    "urlopen(",
    "httpx.post",
    "client.post(",
)

# Phrases that would constitute a raw-media-byte export claim when stated
# affirmatively (outside a non-claim context). The honest pack must NOT claim
# raw media bytes are included.
RAW_MEDIA_BYTE_CLAIM_PHRASES: tuple[str, ...] = (
    "the pack includes raw media bytes",
    "the pack contains raw media bytes",
    "raw media bytes are included in the pack",
    "includes raw media bytes",
    "contains raw media bytes",
)

# Phrases that would constitute a zip export claim when stated affirmatively
# (outside a non-claim context). The honest pack must NOT claim zip export
# unless zip generation is actually implemented (it is not in PS-031).
ZIP_CLAIM_PHRASES: tuple[str, ...] = (
    "the pack produces a zip export",
    "the pack is a zip export",
    "produces a zip export",
    "zip export is available",
    "zip download is available",
)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> dict:
    return json.loads(read_text(path))


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _paragraph_range(lines: list[str], index: int) -> tuple[int, int]:
    start = index
    while start > 0 and lines[start - 1].strip():
        start -= 1
    end = index + 1
    while end < len(lines) and lines[end].strip():
        end += 1
    return start, end


def _line_has_nonclaim_context(lines: list[str], index: int) -> bool:
    start, end = _paragraph_range(lines, index)
    window = "\n".join(lines[start:end])
    return bool(CONTEXT_MARKERS_RE.search(window))


# ---------------------------------------------------------------------------
# Constant extraction from judgeEvidencePack.ts
# ---------------------------------------------------------------------------

def _extract_string_const(text: str, name: str) -> str | None:
    m = re.search(
        r'export\s+const\s+' + re.escape(name) + r'\s*=\s*"((?:[^"\\]|\\.)*)"\s*;',
        text,
    )
    if m:
        return m.group(1)
    m = re.search(
        r'export\s+const\s+' + re.escape(name) + r'\s*=\s*((?:"(?:[^"\\]|\\.)*"\s*(?:\+|\+?\s*\n)?\s*)+);',
        text,
    )
    if m:
        fragments = re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))
        return "".join(fragments) if fragments else None
    return None


def _extract_number_const(text: str, name: str) -> int | None:
    m = re.search(
        r'export\s+const\s+' + re.escape(name) + r'\s*=\s*(-?\d+)\s*;',
        text,
    )
    return int(m.group(1)) if m else None


def _extract_bool_const(text: str, name: str) -> bool | None:
    m = re.search(
        r'export\s+const\s+' + re.escape(name) + r'\s*=\s*(true|false)\s*;',
        text,
    )
    if not m:
        return None
    return m.group(1) == "true"


# ---------------------------------------------------------------------------
# API access (TestClient local contract)
# ---------------------------------------------------------------------------

def _get_passport_status(run_id: str) -> int:
    from fastapi.testclient import TestClient  # type: ignore

    from proofstudio.api.app import create_app
    from proofstudio.api.services import create_default_service

    app = create_app(create_default_service())
    client = TestClient(app)
    response = client.get(f"/runs/{run_id}/passport")
    return response.status_code


def _get_golden_passport_json(run_id: str) -> dict[str, Any] | None:
    from fastapi.testclient import TestClient  # type: ignore

    from proofstudio.api.app import create_app
    from proofstudio.api.services import create_default_service

    app = create_app(create_default_service())
    client = TestClient(app)
    response = client.get(f"/runs/{run_id}/passport")
    if response.status_code != 200 or not response.text:
        return None
    try:
        parsed = response.json()
    except Exception:
        return None
    return parsed if isinstance(parsed, dict) else None


# ---------------------------------------------------------------------------
# Source value extraction (with PS-021 durable_source key override)
# ---------------------------------------------------------------------------

REQUIRED_SOURCE_IDS: tuple[str, ...] = (
    "ps024",
    "ps021",
    "ps025",
    "ps026",
    "ps027",
    "ps028",
    "ps029",
    "ps030",
)

SOURCE_KEY_OVERRIDES: dict[str, dict[str, str]] = {
    "ps021": {"rehydrate_source": "durable_source"},
}

SOURCE_JSON: dict[str, dict] = {}


def _source_field_value(source_id: str, field_key: str) -> Any:
    src = SOURCE_JSON.get(source_id, {})
    key = SOURCE_KEY_OVERRIDES.get(source_id, {}).get(field_key, field_key)
    return src.get(key)


def _source_evidence_path(source_id: str) -> Path:
    return {
        "ps024": MANIFEST,
        "ps021": PS021_EVIDENCE,
        "ps025": PS025_EVIDENCE,
        "ps026": PS026_EVIDENCE,
        "ps027": PS027_EVIDENCE,
        "ps028": PS028_EVIDENCE,
        "ps029": PS029_EVIDENCE,
        "ps030": PS030_EVIDENCE,
    }[source_id]


# ---------------------------------------------------------------------------
# Required pack sections (the 15 headings the component must render).
# ---------------------------------------------------------------------------

REQUIRED_PACK_SECTIONS: tuple[str, ...] = (
    "Pack identity",
    "Campaign / run identity",
    "Final asset / archive summary",
    "Prompt / generation evidence summary",
    "Provider / model / attempt ledger summary",
    "B2 archive evidence",
    "Genblaze manifest evidence",
    "B2 rehydrate proof",
    "Failure-as-Proof summary",
    "Public passport link",
    "Review / approval status",
    "Disclosure readiness notes",
    "Truth boundary",
    "Limitations",
    "Next actions for judge / client",
)

# Required pack JSON shape keys (buildJudgeEvidencePackJson return).
REQUIRED_PACK_JSON_KEYS: tuple[str, ...] = (
    "pack_id",
    "pack_version",
    "generated_from",
    "generated_at",
    "campaign_id",
    "run_id",
    "archive_uri",
    "archive_sha256",
    "rehydrate_source",
    "provider_calls_during_rehydrate",
    "no_live_provider_call_during_rehydrate",
    "source_evidence",
    "route_map",
    "proof_chain",
    "failure_as_proof_summary",
    "disclosure_notes",
    "truth_boundary",
    "limitations",
    "public_deployment_pending",
)


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_surface_exists() -> tuple[bool, list[str]]:
    """PS-031 surface exists as a frontend route + component + CTA + link."""
    problems: list[str] = []
    if not PACK_COMPONENT.exists():
        problems.append(f"missing component {rel(PACK_COMPONENT)}")
    if not PACK_CONST.exists():
        problems.append(f"missing constants module {rel(PACK_CONST)}")

    if PACK_COMPONENT.exists():
        comp_text = read_text(PACK_COMPONENT)
        for required in (
            "Judge Evidence Pack",
            "Local browser export",
            "Download pack JSON",
            "Download pack README / Markdown",
            "Proof chain",
            "Route map",
            "Open Failure-as-Proof Timeline",
            "Open B2 Rehydrate Comparison",
            "Open Manifest Verification Panel",
            "Open B2 Evidence Explorer",
            "Open Genblaze Pipeline Graph",
            "Open Golden Passport",
            "Back to Judge Cockpit Home",
        ):
            if required not in comp_text:
                problems.append(
                    f"JudgeEvidencePack missing reference to {required!r}"
                )
    return (not problems, problems)


def check_route_exists() -> tuple[bool, list[str]]:
    """The /evidence-pack route is registered in App.tsx."""
    problems: list[str] = []
    if not APP_TSX.exists():
        return False, [f"missing {rel(APP_TSX)}"]
    text = read_text(APP_TSX)
    if "isEvidencePackPath" not in text:
        problems.append(
            "App.tsx does not register an isEvidencePackPath helper"
        )
    if "/evidence-pack" not in text:
        problems.append(
            "App.tsx does not reference the /evidence-pack path"
        )
    if "JudgeEvidencePack" not in text:
        problems.append(
            "App.tsx does not render the JudgeEvidencePack component"
        )
    return (not problems, problems)


def check_judge_links_pack() -> tuple[bool, list[str]]:
    """The Judge Cockpit links to /evidence-pack."""
    problems: list[str] = []
    if not HOMEPAGE.exists():
        return False, [f"missing {rel(HOMEPAGE)}"]
    text = read_text(HOMEPAGE)
    if "/evidence-pack" not in text:
        problems.append("homepage does not link to /evidence-pack")
    if "Open Judge Evidence Pack" not in text:
        problems.append(
            "homepage does not surface a Judge Evidence Pack CTA label"
        )
    return (not problems, problems)


def check_timeline_links_pack() -> tuple[bool, list[str]]:
    """The Failure-as-Proof Timeline links to /evidence-pack."""
    problems: list[str] = []
    if not FAILURE_TIMELINE_COMPONENT.exists():
        return False, [f"missing {rel(FAILURE_TIMELINE_COMPONENT)}"]
    text = read_text(FAILURE_TIMELINE_COMPONENT)
    if "/evidence-pack" not in text:
        problems.append("Failure-as-Proof Timeline does not link to /evidence-pack")
    if "Open Judge Evidence Pack" not in text:
        problems.append(
            "Failure-as-Proof Timeline does not surface a Judge Evidence Pack CTA label"
        )
    return (not problems, problems)


def check_pack_links(constants_text: str, manifest: dict) -> tuple[bool, list[str]]:
    """The pack links to timeline, rehydrate, manifest, b2, genblaze, passport."""
    problems: list[str] = []
    if not PACK_COMPONENT.exists():
        return False, [f"missing {rel(PACK_COMPONENT)}"]
    comp_text = read_text(PACK_COMPONENT)
    const_text = constants_text

    for href, label in (
        ("/failure-timeline", "failure timeline"),
        ("/b2-rehydrate-comparison", "b2 rehydrate comparison"),
        ("/manifest-verification", "manifest verification"),
        ("/b2-evidence", "b2 evidence"),
        ("/genblaze-pipeline", "genblaze pipeline"),
    ):
        if href not in comp_text and href not in const_text:
            problems.append(f"pack does not link to {href} ({label})")

    golden_run_id = manifest.get("run_id")
    if not golden_run_id:
        problems.append("manifest missing run_id")
    else:
        golden_href = f"/passport/{golden_run_id}"
        if (
            golden_href not in comp_text
            and golden_href not in const_text
            and '"/passport/" + JUDGE_EVIDENCE_PACK_RUN_ID' not in comp_text
        ):
            problems.append(
                "pack does not link to the golden passport via "
                f"{golden_href}"
            )

    if 'href="/"' not in comp_text:
        problems.append(
            "pack does not link back to / (Judge Cockpit Home)"
        )
    return (not problems, problems)


def check_pack_exports() -> tuple[bool, list[str]]:
    """The pack JSON export action and the pack Markdown export action exist."""
    problems: list[str] = []
    if not PACK_COMPONENT.exists():
        return False, [f"missing {rel(PACK_COMPONENT)}"]
    comp_text = read_text(PACK_COMPONENT)
    if "Download pack JSON" not in comp_text:
        problems.append("pack does not surface a Download pack JSON action")
    if "Download pack README / Markdown" not in comp_text:
        problems.append(
            "pack does not surface a Download pack README / Markdown action"
        )
    if "buildJudgeEvidencePackJson" not in comp_text:
        problems.append(
            "pack component does not call buildJudgeEvidencePackJson"
        )
    if "buildJudgeEvidencePackMarkdown" not in comp_text:
        problems.append(
            "pack component does not call buildJudgeEvidencePackMarkdown"
        )
    # The export must be honest about being a local browser export.
    if "Local browser export" not in comp_text:
        problems.append(
            "pack does not label the export as Local browser export"
        )
    if "Blob" not in comp_text:
        problems.append(
            "pack does not implement a browser-side Blob download"
        )
    return (not problems, problems)


def check_pack_sections_visible() -> tuple[bool, list[str]]:
    """All required 15 pack sections are visible in the component."""
    problems: list[str] = []
    if not PACK_COMPONENT.exists():
        return False, [f"missing {rel(PACK_COMPONENT)}"]
    comp_text = read_text(PACK_COMPONENT)
    for section in REQUIRED_PACK_SECTIONS:
        if section not in comp_text:
            problems.append(
                f"JudgeEvidencePack missing section heading {section!r}"
            )
    return (not problems, problems)


def check_pack_json_shape(constants_text: str) -> tuple[bool, list[str]]:
    """The required pack JSON shape is present in the data/source module."""
    problems: list[str] = []
    if not PACK_CONST.exists():
        return False, [f"missing {rel(PACK_CONST)}"]
    if "buildJudgeEvidencePackJson" not in constants_text:
        problems.append(
            "judgeEvidencePack.ts does not declare buildJudgeEvidencePackJson"
        )
    if "JudgeEvidencePackJson" not in constants_text:
        problems.append(
            "judgeEvidencePack.ts does not declare the JudgeEvidencePackJson type"
        )
    for key in REQUIRED_PACK_JSON_KEYS:
        if key not in constants_text:
            problems.append(
                f"judgeEvidencePack.ts pack JSON shape missing key {key!r}"
            )
    # Verify the function returns every required key by scanning the literal
    # return body.
    m = re.search(
        r"buildJudgeEvidencePackJson\([^)]*\)\s*:\s*JudgeEvidencePackJson\s*\{(.*)\n\}",
        constants_text,
        re.DOTALL,
    )
    if m:
        body = m.group(1)
        for key in REQUIRED_PACK_JSON_KEYS:
            if key not in body:
                problems.append(
                    f"buildJudgeEvidencePackJson return body missing key {key!r}"
                )
    return (not problems, problems)


def check_route_map_present(constants_text: str) -> tuple[bool, list[str]]:
    """The route map is present in the data/source module."""
    problems: list[str] = []
    if "JUDGE_EVIDENCE_PACK_ROUTES" not in constants_text:
        problems.append(
            "judgeEvidencePack.ts does not declare JUDGE_EVIDENCE_PACK_ROUTES"
        )
    if not PACK_CONST.exists():
        return False, problems
    # Every required href must appear in the routes list or be derivable.
    for href in (
        "/failure-timeline",
        "/b2-rehydrate-comparison",
        "/manifest-verification",
        "/b2-evidence",
        "/genblaze-pipeline",
        "/",
    ):
        if href not in constants_text:
            problems.append(
                f"JUDGE_EVIDENCE_PACK_ROUTES missing href {href!r}"
            )
    if '"/passport/" + JUDGE_EVIDENCE_PACK_RUN_ID' not in constants_text:
        problems.append(
            "JUDGE_EVIDENCE_PACK_ROUTES does not build the golden passport href"
        )
    return (not problems, problems)


def check_proof_chain_present(constants_text: str) -> tuple[bool, list[str]]:
    """The proof chain is present in the data/source module."""
    problems: list[str] = []
    if "JUDGE_EVIDENCE_PACK_PROOF_CHAIN" not in constants_text:
        problems.append(
            "judgeEvidencePack.ts does not declare JUDGE_EVIDENCE_PACK_PROOF_CHAIN"
        )
    for required_title in (
        "Pack identity established",
        "Golden run identity pinned",
        "B2 archive recorded",
        "Genblaze manifest captured",
        "Public passport contract unlocked locally",
        "Rehydrate proven durable without provider rerun",
        "Failure-as-Proof carried into the pack",
        "Public deployment pending remains explicit",
    ):
        if required_title not in constants_text:
            problems.append(
                f"proof chain missing step title {required_title!r}"
            )
    return (not problems, problems)


def check_failure_as_proof_visible(constants_text: str) -> tuple[bool, list[str]]:
    """The Failure-as-Proof summary is visible."""
    problems: list[str] = []
    if "JUDGE_EVIDENCE_PACK_FAILURE_AS_PROOF_SUMMARY" not in constants_text:
        problems.append(
            "judgeEvidencePack.ts does not declare "
            "JUDGE_EVIDENCE_PACK_FAILURE_AS_PROOF_SUMMARY"
        )
    if not PACK_COMPONENT.exists():
        return False, problems
    comp_text = read_text(PACK_COMPONENT)
    if "Failure-as-Proof summary" not in comp_text:
        problems.append(
            "component does not render the Failure-as-Proof summary heading"
        )
    return (not problems, problems)


def check_disclosure_notes_visible(constants_text: str) -> tuple[bool, list[str]]:
    """The disclosure notes are visible."""
    problems: list[str] = []
    if "JUDGE_EVIDENCE_PACK_DISCLOSURE_NOTES" not in constants_text:
        problems.append(
            "judgeEvidencePack.ts does not declare "
            "JUDGE_EVIDENCE_PACK_DISCLOSURE_NOTES"
        )
    if not PACK_COMPONENT.exists():
        return False, problems
    comp_text = read_text(PACK_COMPONENT)
    if "Disclosure readiness notes" not in comp_text:
        problems.append(
            "component does not render the Disclosure readiness notes heading"
        )
    return (not problems, problems)


def check_limitations_visible(constants_text: str) -> tuple[bool, list[str]]:
    """The limitations are visible."""
    problems: list[str] = []
    if "JUDGE_EVIDENCE_PACK_LIMITATIONS" not in constants_text:
        problems.append(
            "judgeEvidencePack.ts does not declare JUDGE_EVIDENCE_PACK_LIMITATIONS"
        )
    if not PACK_COMPONENT.exists():
        return False, problems
    comp_text = read_text(PACK_COMPONENT)
    if "Limitations" not in comp_text:
        problems.append("component does not render the Limitations heading")
    return (not problems, problems)


def check_truth_boundary_visible(constants_text: str) -> tuple[bool, list[str]]:
    """The truth boundary is visible and carries every required term."""
    problems: list[str] = []
    if "JUDGE_EVIDENCE_PACK_TRUTH_BOUNDARY" not in constants_text:
        problems.append(
            "judgeEvidencePack.ts does not declare JUDGE_EVIDENCE_PACK_TRUTH_BOUNDARY"
        )
        return (not problems, problems)
    missing = [
        t for t in TRUTH_BOUNDARY_TERMS if t.lower() not in constants_text.lower()
    ]
    if missing:
        problems.append(
            f"judgeEvidencePack.ts truth boundary missing term {missing[0]!r}"
        )
    if not PACK_COMPONENT.exists():
        return False, problems
    comp_text = read_text(PACK_COMPONENT)
    if "Truth boundary" not in comp_text:
        problems.append("component does not render the Truth boundary heading")
    if "JUDGE_EVIDENCE_PACK_TRUTH_BOUNDARY" not in comp_text:
        problems.append(
            "component does not reference the truth boundary const"
        )
    if "JUDGE_EVIDENCE_PACK_CLAIM_BOUNDARY_ALLOWED" not in constants_text:
        problems.append(
            "judgeEvidencePack.ts does not declare the allowed claim boundary"
        )
    if "JUDGE_EVIDENCE_PACK_CLAIM_BOUNDARY_FORBIDDEN" not in constants_text:
        problems.append(
            "judgeEvidencePack.ts does not declare the forbidden claim boundary"
        )
    return (not problems, problems)


def check_run_id_matches(constants_text: str) -> tuple[bool, list[str]]:
    want = _source_field_value("ps024", "run_id")
    problems: list[str] = []
    for src_id in REQUIRED_SOURCE_IDS:
        got = _source_field_value(src_id, "run_id")
        if got != want:
            problems.append(
                f"run_id: source {src_id}={got!r} vs manifest={want!r}"
            )
    const = _extract_string_const(constants_text, "JUDGE_EVIDENCE_PACK_RUN_ID")
    if const != want:
        problems.append(
            f"run_id: frontend constant={const!r} vs manifest={want!r}"
        )
    return (not problems, problems)


def check_campaign_id_matches(constants_text: str) -> tuple[bool, list[str]]:
    want = _source_field_value("ps024", "campaign_id")
    problems: list[str] = []
    for src_id in REQUIRED_SOURCE_IDS:
        got = _source_field_value(src_id, "campaign_id")
        if got != want:
            problems.append(
                f"campaign_id: source {src_id}={got!r} vs manifest={want!r}"
            )
    const = _extract_string_const(constants_text, "JUDGE_EVIDENCE_PACK_CAMPAIGN_ID")
    if const != want:
        problems.append(
            f"campaign_id: frontend constant={const!r} vs manifest={want!r}"
        )
    return (not problems, problems)


def check_archive_uri_match(constants_text: str) -> tuple[bool, list[str]]:
    want = _source_field_value("ps024", "archive_uri")
    problems: list[str] = []
    for src_id in REQUIRED_SOURCE_IDS:
        got = _source_field_value(src_id, "archive_uri")
        if got != want:
            problems.append(
                f"archive_uri: source {src_id}={got!r} vs manifest={want!r}"
            )
    const = _extract_string_const(constants_text, "JUDGE_EVIDENCE_PACK_ARCHIVE_URI")
    if const != want:
        problems.append(
            f"archive_uri: frontend constant={const!r} vs manifest={want!r}"
        )
    return (not problems, problems)


def check_archive_sha256_match(constants_text: str) -> tuple[bool, list[str]]:
    want = _source_field_value("ps024", "archive_sha256")
    problems: list[str] = []
    for src_id in REQUIRED_SOURCE_IDS:
        got = _source_field_value(src_id, "archive_sha256")
        if got != want:
            problems.append(
                f"archive_sha256: source {src_id}={got!r} vs manifest={want!r}"
            )
    const = _extract_string_const(constants_text, "JUDGE_EVIDENCE_PACK_ARCHIVE_SHA256")
    if const != want:
        problems.append(
            f"archive_sha256: frontend constant={const!r} vs manifest={want!r}"
        )
    return (not problems, problems)


def check_rehydrate_source(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    for src_id in REQUIRED_SOURCE_IDS:
        got = _source_field_value(src_id, "rehydrate_source")
        if got != "b2_rehydrated":
            problems.append(
                f"rehydrate_source: source {src_id}={got!r}, "
                f"expected 'b2_rehydrated'"
            )
    const = _extract_string_const(constants_text, "JUDGE_EVIDENCE_PACK_REHYDRATE_SOURCE")
    if const != "b2_rehydrated":
        problems.append(
            f"rehydrate_source: frontend constant={const!r}, "
            f"expected 'b2_rehydrated'"
        )
    return (not problems, problems)


def check_provider_calls_zero(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    for src_id in REQUIRED_SOURCE_IDS:
        got = _source_field_value(src_id, "provider_calls_during_rehydrate")
        if got != 0:
            problems.append(
                f"provider_calls_during_rehydrate: source {src_id}={got!r}, "
                f"expected 0"
            )
    const = _extract_number_const(
        constants_text,
        "JUDGE_EVIDENCE_PACK_PROVIDER_CALLS_DURING_REHYDRATE",
    )
    if const != 0:
        problems.append(
            f"provider_calls_during_rehydrate: frontend constant={const!r}, "
            f"expected 0"
        )
    return (not problems, problems)


def check_no_live_provider_call(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    for src_id in REQUIRED_SOURCE_IDS:
        got = _source_field_value(src_id, "no_live_provider_call_during_rehydrate")
        if got is not True:
            problems.append(
                f"no_live_provider_call_during_rehydrate: source "
                f"{src_id}={got!r}, expected True"
            )
    const = _extract_bool_const(
        constants_text,
        "JUDGE_EVIDENCE_PACK_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE",
    )
    if const is not True:
        problems.append(
            f"no_live_provider_call_during_rehydrate: frontend constant="
            f"{const!r}, expected True"
        )
    return (not problems, problems)


def check_no_provider_call() -> tuple[bool, list[str]]:
    """No new provider call path is introduced."""
    problems: list[str] = []
    for path in PROVIDER_AND_B2_SCAN_FILES:
        if not path.exists():
            continue
        text = read_text(path)
        for pattern in PROVIDER_CALL_PATTERNS:
            if pattern in text:
                problems.append(
                    f"{rel(path)}: forbidden provider-call pattern {pattern!r}"
                )
    return (not problems, problems)


def check_no_broad_b2_read() -> tuple[bool, list[str]]:
    """No new broad B2 object read path is introduced."""
    problems: list[str] = []
    for path in PROVIDER_AND_B2_SCAN_FILES:
        if not path.exists():
            continue
        text = read_text(path)
        for pattern in BROAD_B2_READ_PATTERNS:
            if pattern in text:
                problems.append(
                    f"{rel(path)}: forbidden B2 read pattern {pattern!r}"
                )

    arbitrary_run_id = "run_ps031_must_still_404_0123456789abcdef"
    status = _get_passport_status(arbitrary_run_id)
    if status != 404:
        problems.append(
            f"arbitrary run id returned HTTP {status}, expected 404 "
            f"(broad public durable read must stay blocked)"
        )

    return (not problems, problems)


def check_no_raw_media_byte_claim() -> tuple[bool, list[str]]:
    """No raw media byte export claim is made (outside non-claim context)."""
    problems: list[str] = []
    for path in SCAN_FILES:
        if not path.exists():
            continue
        text = read_text(path)
        lines = text.splitlines()
        in_fence = False
        for i, line in enumerate(lines):
            if FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            line_lower = line.lower()
            hit = False
            for phrase in RAW_MEDIA_BYTE_CLAIM_PHRASES:
                if phrase in line_lower:
                    hit = True
                    break
            if not hit:
                continue
            if _line_has_nonclaim_context(lines, i):
                continue
            problems.append(
                f"{rel(path)}:{i + 1}: raw media byte claim with no non-claim "
                f"context -> {line.strip()!r}"
            )
    return (not problems, problems)


def check_no_zip_claim() -> tuple[bool, list[str]]:
    """No zip export claim is made (outside non-claim context).

    zip generation is NOT implemented in PS-031, so any affirmative zip claim
    is a forbidden overclaim.
    """
    problems: list[str] = []
    for path in SCAN_FILES:
        if not path.exists():
            continue
        text = read_text(path)
        lines = text.splitlines()
        in_fence = False
        for i, line in enumerate(lines):
            if FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            line_lower = line.lower()
            hit = False
            for phrase in ZIP_CLAIM_PHRASES:
                if phrase in line_lower:
                    hit = True
                    break
            if not hit:
                continue
            if _line_has_nonclaim_context(lines, i):
                continue
            problems.append(
                f"{rel(path)}:{i + 1}: zip claim with no non-claim context "
                f"-> {line.strip()!r}"
            )
    return (not problems, problems)


def check_secrets() -> tuple[bool, list[str]]:
    hits: list[str] = []
    for path in SCAN_FILES:
        if not path.exists():
            continue
        text = read_text(path)
        for needle in SECRET_SUBSTRINGS:
            if needle in text:
                idx = text.find(needle)
                line_no = text.count("\n", 0, idx) + 1
                hits.append(f"{rel(path)}:{line_no}: secret literal {needle!r}")
        for m in SECRET_KEY_RE.finditer(text):
            idx = m.start()
            line_no = text.count("\n", 0, idx) + 1
            hits.append(f"{rel(path)}:{line_no}: secret literal {m.group(0)!r}")
    return (not hits, hits)


def check_forbidden_claims() -> tuple[bool, list[str]]:
    violations: list[str] = []
    for path in SCAN_FILES:
        if not path.exists():
            continue
        text = read_text(path)
        lines = text.splitlines()
        in_fence = False
        for i, line in enumerate(lines):
            if FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            line_lower = line.lower()
            hit = False
            for phrase in FORBIDDEN_AFFIRMATIVE:
                if phrase in line_lower:
                    hit = True
                    break
            if not hit:
                continue
            if in_fence:
                continue
            if _line_has_nonclaim_context(lines, i):
                continue
            violations.append(
                f"{rel(path)}:{i + 1}: affirmative claim with no non-claim "
                f"context -> {line.strip()!r}"
            )
    return (not violations, violations)


def check_api_resolves_golden(manifest: dict) -> tuple[bool, list[str]]:
    """The PS-025 golden demo unlock must still resolve the golden passport."""
    golden_run_id = manifest.get("run_id")
    passport = _get_golden_passport_json(golden_run_id)
    if not passport:
        status = _get_passport_status(golden_run_id)
        return False, [
            f"GET /runs/{golden_run_id}/passport did not resolve "
            f"(status={status})"
        ]
    return True, []

# ---------------------------------------------------------------------------
# PS-034B retrofitted runner (safe local / check-only mode)
# ---------------------------------------------------------------------------

def check_no_prior_slice_evidence_modified() -> tuple[bool, list[str]]:
    """No prior-slice evidence file is left modified by the PS-031 smoke run."""
    problems = sl.prior_evidence_dirty_problems(
        own_slice_prefix="docs/evidence/ps-031/",
        slice_label="PS-031",
    )
    return (not problems, problems)


def run(argv=None) -> int:
    opts = sl.parse_slice_smoke_cli(argv)
    missing_inputs: list[str] = []
    for p in (
        MANIFEST,
        PS021_EVIDENCE,
        PS025_EVIDENCE,
        PS026_EVIDENCE,
        PS027_EVIDENCE,
        PS028_EVIDENCE,
        PS029_EVIDENCE,
        PS030_EVIDENCE,
    ):
        if not p.exists():
            missing_inputs.append(rel(p))
    if missing_inputs:
        print("PS031 smoke: MISSING INPUT FILES")
        for f in missing_inputs:
            print(f"  - {f}")
        return 1

    manifest = load_json(MANIFEST)
    global SOURCE_JSON
    SOURCE_JSON = {
        "ps024": load_json(MANIFEST),
        "ps021": load_json(PS021_EVIDENCE),
        "ps025": load_json(PS025_EVIDENCE),
        "ps026": load_json(PS026_EVIDENCE),
        "ps027": load_json(PS027_EVIDENCE),
        "ps028": load_json(PS028_EVIDENCE),
        "ps029": load_json(PS029_EVIDENCE),
        "ps030": load_json(PS030_EVIDENCE),
    }
    constants_text = (
        read_text(PACK_CONST) if PACK_CONST.exists() else ""
    )

    checks: list[tuple[str, tuple[bool, list[str]]]] = [
        ("surface_exists", check_surface_exists()),
        ("route_exists", check_route_exists()),
        ("judge_links_pack", check_judge_links_pack()),
        ("timeline_links_pack", check_timeline_links_pack()),
        (
            "pack_links_timeline_rehydrate_manifest_b2_genblaze_passport_home",
            check_pack_links(constants_text, manifest),
        ),
        ("pack_json_export", check_pack_exports()),
        ("pack_sections_visible", check_pack_sections_visible()),
        ("pack_json_shape", check_pack_json_shape(constants_text)),
        ("route_map_present", check_route_map_present(constants_text)),
        ("proof_chain_present", check_proof_chain_present(constants_text)),
        (
            "failure_as_proof_visible",
            check_failure_as_proof_visible(constants_text),
        ),
        (
            "disclosure_notes_visible",
            check_disclosure_notes_visible(constants_text),
        ),
        ("limitations_visible", check_limitations_visible(constants_text)),
        ("truth_boundary_visible", check_truth_boundary_visible(constants_text)),
        ("run_id_matches", check_run_id_matches(constants_text)),
        ("campaign_id_matches", check_campaign_id_matches(constants_text)),
        ("archive_uri_match", check_archive_uri_match(constants_text)),
        ("archive_sha256_match", check_archive_sha256_match(constants_text)),
        ("rehydrate_source", check_rehydrate_source(constants_text)),
        ("provider_calls_zero", check_provider_calls_zero(constants_text)),
        ("no_live_provider_call", check_no_live_provider_call(constants_text)),
        ("no_provider_call", check_no_provider_call()),
        ("no_broad_b2_read", check_no_broad_b2_read()),
        ("no_raw_media_byte_claim", check_no_raw_media_byte_claim()),
        ("no_zip_claim", check_no_zip_claim()),
        ("secret_scan", check_secrets()),
        ("forbidden_claims", check_forbidden_claims()),
        ("api_resolves_golden", check_api_resolves_golden(manifest)),
    ]

    all_pass, detail = sl.run_contract_checks("PS-031 Export Campaign Pack v2", checks)

    if opts.write_evidence:
        evidence = {
            "ok": bool(all_pass),
            "route_or_surface": (
                "/evidence-pack (dedicated frontend route) + JudgeEvidencePack "
                "component + CTA from Judge Cockpit Home (golden demo run panel "
                "and Direct CTAs grid) + link from Failure-as-Proof Timeline "
                "(page variant) + local browser export of pack JSON and pack "
                "README / Markdown"
            ),
            "pack_id": "pack_ps031_" + manifest.get("run_id", ""),
            "pack_version": "2.0.0",
            "run_id": manifest.get("run_id"),
            "campaign_id": manifest.get("campaign_id"),
            "archive_uri": manifest.get("archive_uri"),
            "archive_sha256": manifest.get("archive_sha256"),
            "rehydrate_source": "b2_rehydrated",
            "provider_calls_during_rehydrate": 0,
            "no_live_provider_call_during_rehydrate": True,
            "evidence_pack_surface_verified": evidence_pack_surface_verified,
            "json_export_available": json_export_available,
            "markdown_export_available": markdown_export_available,
            "pack_identity_verified": pack_identity_verified,
            "pack_sections_verified": pack_sections_verified,
            "route_map_verified": route_map_verified,
            "proof_chain_verified": proof_chain_verified,
            "failure_as_proof_summary_visible": failure_as_proof_summary_visible,
            "disclosure_notes_visible": disclosure_notes_visible,
            "truth_boundary_present": truth_boundary_present,
            "limitations_present": limitations_present,
            "source_ps021_evidence": rel(PS021_EVIDENCE),
            "source_ps024_manifest": rel(MANIFEST),
            "source_ps025_evidence": rel(PS025_EVIDENCE),
            "source_ps026_evidence": rel(PS026_EVIDENCE),
            "source_ps027_evidence": rel(PS027_EVIDENCE),
            "source_ps028_evidence": rel(PS028_EVIDENCE),
            "source_ps029_evidence": rel(PS029_EVIDENCE),
            "source_ps030_evidence": rel(PS030_EVIDENCE),
            "source_implementation_roadmap": rel(ROADMAP),
            "frontend_surface_verified": frontend_surface_verified,
            "api_surface_verified": api_surface_verified,
            "no_provider_call": no_provider_call,
            "no_broad_b2_read": no_broad_b2_read,
            "no_raw_media_byte_claim": no_raw_media_byte_claim,
            "no_zip_claim_unless_implemented": no_zip_claim_unless_implemented,
            "no_prior_slice_evidence_modified": bool(prior_clean_ok),
            "public_deployment_pending": bool(public_deployment_pending),
            "checked_at": _utc_now_iso(),
            "api_transport": "testclient",
            "pack_values_verified": pack_values_verified,
            "checks": detail,
            "truth_boundary": (
                "PS-031 proves the Judge Evidence Pack surfaces that the "
                "checked-in evidence (PS-021, PS-024, PS-025, PS-026, PS-027, "
                "PS-028, PS-029, PS-030) records a B2 rehydrate proof with zero "
                "provider calls during rehydrate, agrees on the golden run "
                "identifiers, archive URI, and archive SHA-256, and records "
                "rehydrate_source = b2_rehydrated. The pack is generated locally "
                "from checked-in ProofStudio evidence. The pack does not prove "
                "semantic truth, legal authenticity, C2PA authenticity, or human "
                "authorship. The pack does not prove Object Lock or tamper-proof "
                "storage. The pack did not fetch and hash the B2 object in the "
                "browser. The pack does not include raw media bytes and does not "
                "produce a zip export. The local contract is verified; the public "
                "deployment remains pending until the new backend is deployed "
                "and the public URL is verified end-to-end."
            ),
        }
        sl.write_json_atomic(EVIDENCE_OUT, evidence)
        print(f"evidence: {rel(EVIDENCE_OUT)}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(run())
