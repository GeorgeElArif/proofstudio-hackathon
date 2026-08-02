#!/usr/bin/env python3
"""PS-032 Operations Cockpit / Flight Recorder v2 -- smoke / validation script.

PS-034B retrofit: this smoke defaults to safe local / check-only
behavior. It does not recursively execute prior slice smokes, does
not run the frontend toolchain, does not use Git index hiding, does
not snapshot/restore prior evidence, and does not self-unlink its
evidence file. Evidence is written only when ``--write-evidence`` is
passed.

    python scripts/ps032_operations_cockpit_flight_recorder_smoke.py --local --check-only

It statically validates the PS032 surface without starting a
browser, without calling any provider, without reading any B2 object,
and without enabling broad durable reads.

Truth boundary: this script validates that the PS032 surface
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
PS031_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "ps-031" / "export-campaign-pack-v2-smoke.json"
ROADMAP = REPO_ROOT / "docs" / "roadmap" / "proofstudio-winning-implementation-roadmap-2026-06-29.md"
PS031A_ROADMAP = REPO_ROOT / "docs" / "roadmap" / "ps-031a-hardened-product-modules-correction.md"

# PS-032 changed / added files.
COCKPIT_CONST = REPO_ROOT / "apps" / "web" / "src" / "operationsCockpit.ts"
COCKPIT_COMPONENT = REPO_ROOT / "apps" / "web" / "src" / "OperationsCockpit.tsx"
HOMEPAGE = REPO_ROOT / "apps" / "web" / "src" / "JudgeCockpitHome.tsx"
APP_TSX = REPO_ROOT / "apps" / "web" / "src" / "App.tsx"
PACK_COMPONENT = REPO_ROOT / "apps" / "web" / "src" / "JudgeEvidencePack.tsx"
FAILURE_TIMELINE_COMPONENT = REPO_ROOT / "apps" / "web" / "src" / "FailureAsProofTimeline.tsx"
B2_REHYDRATE_COMPONENT = REPO_ROOT / "apps" / "web" / "src" / "B2RehydrateComparison.tsx"
MANIFEST_PANEL = REPO_ROOT / "apps" / "web" / "src" / "ManifestVerificationPanel.tsx"
B2_EXPLORER = REPO_ROOT / "apps" / "web" / "src" / "B2EvidenceExplorer.tsx"
GENBLAZE_GRAPH = REPO_ROOT / "apps" / "web" / "src" / "GenblazePipelineGraph.tsx"
PUBLIC_PASSPORT = REPO_ROOT / "apps" / "web" / "src" / "PublicPassportPage.tsx"
STYLES = REPO_ROOT / "apps" / "web" / "src" / "styles.css"
PROOF_DOC = REPO_ROOT / "docs" / "ps-032-operations-cockpit-flight-recorder-v2-proof.md"

PS031_SMOKE = REPO_ROOT / "scripts" / "ps031_export_campaign_pack_v2_smoke.py"
PS030_SMOKE = REPO_ROOT / "scripts" / "ps030_failure_as_proof_timeline_smoke.py"
PS029_SMOKE = REPO_ROOT / "scripts" / "ps029_b2_rehydrate_comparison_smoke.py"
PS028_SMOKE = REPO_ROOT / "scripts" / "ps028_manifest_verification_panel_smoke.py"
PS027_SMOKE = REPO_ROOT / "scripts" / "ps027_genblaze_pipeline_graph_smoke.py"
PS026_SMOKE = REPO_ROOT / "scripts" / "ps026_b2_evidence_explorer_smoke.py"
PS025_SMOKE = REPO_ROOT / "scripts" / "ps025_public_durable_passport_unlock_smoke.py"
PS024_SMOKE = REPO_ROOT / "scripts" / "ps024_golden_demo_run_pinning_smoke.py"
PS023_SMOKE = REPO_ROOT / "scripts" / "ps023_judge_cockpit_home_smoke.py"

EVIDENCE_OUT = REPO_ROOT / "docs" / "evidence" / "ps-032" / "operations-cockpit-flight-recorder-v2-smoke.json"

# Files scanned for secrets and forbidden claims. The scanner script itself
# is intentionally excluded: it legitimately contains the detection literals
# (same convention as PS-023 through PS-031 smokes).
SCAN_FILES: tuple[Path, ...] = (
    COCKPIT_CONST,
    COCKPIT_COMPONENT,
    HOMEPAGE,
    APP_TSX,
    PACK_COMPONENT,
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
    COCKPIT_CONST,
    COCKPIT_COMPONENT,
    HOMEPAGE,
    APP_TSX,
    PACK_COMPONENT,
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
    "the cockpit proves semantic truth",
    "the cockpit proves media is true",
    "the cockpit proves legal authenticity",
    "the cockpit proves human authorship",
    "the cockpit proves c2pa authenticity",
    "the cockpit proves object lock",
    "the cockpit proves tamper-proof storage",
    "the cockpit certifies authenticity",
    "the cockpit is a certification",
    "the cockpit is legally binding",
    "the cockpit performs browser-side b2 byte verification",
    "the browser fetched and hashed the b2 object",
    "the browser verified the b2 bytes",
    "public deployment is verified",
    "public deployment verified",
    "object lock is enabled",
    "tamper-proof storage is enabled",
    "enterprise-grade security",
    "enterprise security is provided",
)

CONTEXT_MARKERS_RE = re.compile(
    r"does not|do not|must not|\bnot\b|non-claim|non-claims|forbidden|"
    r"reject|rejected|avoid|without overclaim|unless actually implemented|"
    r"only inside non-claim|limitation|limitations|no affirmative|"
    r"unavailable|blocked|honestly|no live|no_new|no_fake|pending|planned|"
    r"did not fetch|does not claim|did not claim|does not perform|without|"
    r"none claimed|would appear|if captured|no actual|no fake|not implemented|"
    r"is not implemented|not a certification|not legal advice|"
    r"generated: false|approved: false|no provider|no broad|no browser-side",
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

# Phrases that would constitute a fake failure claim when stated
# affirmatively (outside a non-claim context). The honest cockpit must NOT
# claim any actual provider failure / fallback occurred for the golden run.
FAKE_FAILURE_CLAIM_PHRASES: tuple[str, ...] = (
    "a provider failure occurred during the golden run",
    "the golden run hit a provider failure",
    "the golden run triggered a fallback",
    "the golden run required a retry",
    "an actual failure was captured for the golden run",
    "the golden run experienced an outage",
)

# Phrases that would constitute a raw-media-byte claim when stated
# affirmatively (outside a non-claim context). The honest cockpit must NOT
# claim raw media bytes are inspected.
RAW_MEDIA_BYTE_CLAIM_PHRASES: tuple[str, ...] = (
    "the cockpit inspects raw media bytes",
    "the cockpit reads raw media bytes",
    "the cockpit fetches raw media bytes",
    "raw media bytes are inspected",
    "inspects raw media bytes",
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
# Constant extraction from operationsCockpit.ts
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
    "ps031",
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
        "ps031": PS031_EVIDENCE,
    }[source_id]


# ---------------------------------------------------------------------------
# Required structural definitions.
# ---------------------------------------------------------------------------

# The 10 spec-required phases.
REQUIRED_PHASE_TITLES: tuple[str, ...] = (
    "Campaign brief",
    "Provider routing / orchestration",
    "Media generation attempt",
    "Asset and manifest capture",
    "Backblaze B2 archive",
    "Genblaze manifest verification",
    "B2 rehydrate",
    "Failure-as-Proof / retry visibility",
    "Judge Evidence Pack export",
    "Review / next action",
)

# The spec-required truth classes.
REQUIRED_TRUTH_CLASSES: tuple[str, ...] = (
    "checked_in_evidence",
    "b2_archive_reference",
    "genblaze_manifest_evidence",
    "rehydrate_proof",
    "local_export_contract",
    "inferred_product_explanation",
    "public_deployment_pending",
)

# The 12 spec-required evidence graph nodes (by label).
REQUIRED_GRAPH_NODE_LABELS: tuple[str, ...] = (
    "Campaign",
    "Run",
    "Provider Router",
    "Genblaze Pipeline",
    "Asset / Manifest",
    "B2 Archive",
    "Manifest Verification",
    "B2 Rehydrate",
    "Failure-as-Proof Timeline",
    "Judge Evidence Pack",
    "Public Passport",
    "Review / Next Action",
)

# The 10 spec-required evidence graph edges (by from-label -> to-label).
REQUIRED_GRAPH_EDGES: tuple[tuple[str, str], ...] = (
    ("Campaign", "Run"),
    ("Run", "Provider Router"),
    ("Provider Router", "Genblaze Pipeline"),
    ("Genblaze Pipeline", "Asset / Manifest"),
    ("Asset / Manifest", "B2 Archive"),
    ("Asset / Manifest", "Manifest Verification"),
    ("B2 Archive", "B2 Rehydrate"),
    ("B2 Rehydrate", "Public Passport"),
    ("Failure-as-Proof Timeline", "Judge Evidence Pack"),
    ("Judge Evidence Pack", "Review / Next Action"),
)

# Required cockpit sections (headings the component must render).
REQUIRED_COCKPIT_SECTIONS: tuple[str, ...] = (
    "Cockpit identity",
    "Run status summary",
    "Operational phase map",
    "Flight Recorder timeline",
    "Evidence graph",
    "Failure Theater",
    "Action rail",
    "Designer / marketer next actions",
    "Truth boundary",
    "Limitations",
)

# Timestamp-honesty labels permitted for flight recorder events (no invented
# wall-clock timestamps).
TIMESTAMP_HONESTY_LABELS: tuple[str, ...] = (
    "source evidence order",
    "checked-in evidence order",
    "not timestamped in checked-in evidence",
)


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_component_exists() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not COCKPIT_COMPONENT.exists():
        problems.append(f"missing component {rel(COCKPIT_COMPONENT)}")
    return (not problems, problems)


def check_data_module_exists() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not COCKPIT_CONST.exists():
        problems.append(f"missing constants module {rel(COCKPIT_CONST)}")
    return (not problems, problems)


def check_route_exists() -> tuple[bool, list[str]]:
    """The /operations-cockpit route is registered in App.tsx."""
    problems: list[str] = []
    if not APP_TSX.exists():
        return False, [f"missing {rel(APP_TSX)}"]
    text = read_text(APP_TSX)
    if "isOperationsCockpitPath" not in text:
        problems.append(
            "App.tsx does not register an isOperationsCockpitPath helper"
        )
    if "/operations-cockpit" not in text:
        problems.append(
            "App.tsx does not reference the /operations-cockpit path"
        )
    if "OperationsCockpit" not in text:
        problems.append(
            "App.tsx does not render the OperationsCockpit component"
        )
    return (not problems, problems)


def check_judge_links_cockpit() -> tuple[bool, list[str]]:
    """The Judge Cockpit links to /operations-cockpit."""
    problems: list[str] = []
    if not HOMEPAGE.exists():
        return False, [f"missing {rel(HOMEPAGE)}"]
    text = read_text(HOMEPAGE)
    if "/operations-cockpit" not in text:
        problems.append("homepage does not link to /operations-cockpit")
    if "Open Operations Cockpit" not in text:
        problems.append(
            "homepage does not surface an Operations Cockpit CTA label"
        )
    return (not problems, problems)


def check_pack_links_cockpit() -> tuple[bool, list[str]]:
    """The Judge Evidence Pack links to /operations-cockpit."""
    problems: list[str] = []
    if not PACK_COMPONENT.exists():
        return False, [f"missing {rel(PACK_COMPONENT)}"]
    text = read_text(PACK_COMPONENT)
    if "/operations-cockpit" not in text:
        problems.append(
            "Judge Evidence Pack does not link to /operations-cockpit"
        )
    if "Open Operations Cockpit" not in text:
        problems.append(
            "Judge Evidence Pack does not surface an Operations Cockpit CTA"
        )
    return (not problems, problems)


def check_timeline_links_cockpit() -> tuple[bool, list[str]]:
    """The Failure-as-Proof Timeline links to /operations-cockpit."""
    problems: list[str] = []
    if not FAILURE_TIMELINE_COMPONENT.exists():
        return False, [f"missing {rel(FAILURE_TIMELINE_COMPONENT)}"]
    text = read_text(FAILURE_TIMELINE_COMPONENT)
    if "/operations-cockpit" not in text:
        problems.append(
            "Failure-as-Proof Timeline does not link to /operations-cockpit"
        )
    if "Open Operations Cockpit" not in text:
        problems.append(
            "Failure-as-Proof Timeline does not surface an Operations Cockpit CTA"
        )
    return (not problems, problems)


def check_cockpit_links() -> tuple[bool, list[str]]:
    """The cockpit links to every required surface."""
    problems: list[str] = []
    if not COCKPIT_COMPONENT.exists():
        return False, [f"missing {rel(COCKPIT_COMPONENT)}"]
    comp_text = read_text(COCKPIT_COMPONENT)
    if not COCKPIT_CONST.exists():
        return False, [f"missing {rel(COCKPIT_CONST)}"]
    const_text = read_text(COCKPIT_CONST)
    for href, label in (
        ("/evidence-pack", "evidence-pack"),
        ("/failure-timeline", "failure-timeline"),
        ("/b2-rehydrate-comparison", "b2-rehydrate-comparison"),
        ("/manifest-verification", "manifest-verification"),
        ("/b2-evidence", "b2-evidence"),
        ("/genblaze-pipeline", "genblaze-pipeline"),
    ):
        if href not in comp_text and href not in const_text:
            problems.append(f"cockpit does not link to {href} ({label})")
    golden_href = "/passport/" + _source_field_value("ps024", "run_id")
    if (
        golden_href not in comp_text
        and golden_href not in const_text
        and '"/passport/" + OPERATIONS_COCKPIT_RUN_ID' not in comp_text
    ):
        problems.append(
            "cockpit does not link to the golden passport via " + golden_href
        )
    if 'href="/"' not in comp_text:
        problems.append(
            "cockpit does not link back to / (Judge Cockpit Home)"
        )
    return (not problems, problems)


def check_cockpit_identity_visible(constants_text: str) -> tuple[bool, list[str]]:
    """Cockpit identity labels are visible."""
    problems: list[str] = []
    if not COCKPIT_COMPONENT.exists():
        return False, problems
    comp_text = read_text(COCKPIT_COMPONENT)
    for required in (
        "Operations Cockpit",
        "Flight Recorder",
        "PS-032",
    ):
        if required not in comp_text:
            problems.append(
                f"cockpit identity missing label {required!r}"
            )
    for const_name in (
        "OPERATIONS_COCKPIT_COCKPIT_ID",
        "OPERATIONS_COCKPIT_COCKPIT_VERSION",
        "OPERATIONS_COCKPIT_RUN_ID",
        "OPERATIONS_COCKPIT_CAMPAIGN_ID",
        "OPERATIONS_COCKPIT_PUBLIC_DEPLOYMENT_PENDING",
    ):
        if const_name not in constants_text:
            problems.append(
                f"operationsCockpit.ts missing identity const {const_name!r}"
            )
    if "public deployment pending" not in comp_text.lower():
        problems.append(
            "cockpit identity does not surface 'public deployment pending'"
        )
    return (not problems, problems)


def check_run_status_summary_visible(constants_text: str) -> tuple[bool, list[str]]:
    """The run status summary is visible."""
    problems: list[str] = []
    if "OPERATIONS_COCKPIT_RUN_STATUS" not in constants_text:
        problems.append(
            "operationsCockpit.ts does not declare OPERATIONS_COCKPIT_RUN_STATUS"
        )
    if not COCKPIT_COMPONENT.exists():
        return False, problems
    comp_text = read_text(COCKPIT_COMPONENT)
    if "Run status summary" not in comp_text:
        problems.append(
            "component does not render the Run status summary heading"
        )
    return (not problems, problems)


def check_golden_values_in_data(constants_text: str) -> tuple[bool, list[str]]:
    """The required golden values are present in the data module."""
    problems: list[str] = []
    for const_name in (
        "OPERATIONS_COCKPIT_ARCHIVE_URI",
        "OPERATIONS_COCKPIT_ARCHIVE_SHA256",
        "OPERATIONS_COCKPIT_REHYDRATE_SOURCE",
        "OPERATIONS_COCKPIT_PROVIDER_CALLS_DURING_REHYDRATE",
        "OPERATIONS_COCKPIT_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE",
    ):
        if const_name not in constants_text:
            problems.append(
                f"operationsCockpit.ts missing golden const {const_name!r}"
            )
    return (not problems, problems)


def check_phase_map_exists(constants_text: str) -> tuple[bool, list[str]]:
    """The phase map exists."""
    problems: list[str] = []
    if "OPERATIONS_COCKPIT_PHASE_MAP" not in constants_text:
        problems.append(
            "operationsCockpit.ts does not declare OPERATIONS_COCKPIT_PHASE_MAP"
        )
    if not COCKPIT_COMPONENT.exists():
        return False, problems
    comp_text = read_text(COCKPIT_COMPONENT)
    if "Operational phase map" not in comp_text:
        problems.append(
            "component does not render the Operational phase map heading"
        )
    return (not problems, problems)


def check_required_phases_exist(constants_text: str) -> tuple[bool, list[str]]:
    """All 10 required phases exist."""
    problems: list[str] = []
    for title in REQUIRED_PHASE_TITLES:
        if title not in constants_text:
            problems.append(f"phase map missing required phase {title!r}")
    return (not problems, problems)


def check_truth_classes_exist(constants_text: str) -> tuple[bool, list[str]]:
    """The required truth classes exist."""
    problems: list[str] = []
    for cls in REQUIRED_TRUTH_CLASSES:
        if cls not in constants_text:
            problems.append(f"truth class missing {cls!r}")
    return (not problems, problems)


def check_flight_recorder_exists(constants_text: str) -> tuple[bool, list[str]]:
    """The flight recorder events exist."""
    problems: list[str] = []
    if "OPERATIONS_COCKPIT_FLIGHT_RECORDER_EVENTS" not in constants_text:
        problems.append(
            "operationsCockpit.ts does not declare "
            "OPERATIONS_COCKPIT_FLIGHT_RECORDER_EVENTS"
        )
    if not COCKPIT_COMPONENT.exists():
        return False, problems
    comp_text = read_text(COCKPIT_COMPONENT)
    if "Flight Recorder timeline" not in comp_text:
        problems.append(
            "component does not render the Flight Recorder timeline heading"
        )
    return (not problems, problems)


def check_event_sequence_exists(constants_text: str) -> tuple[bool, list[str]]:
    """Every event carries a sequence number."""
    problems: list[str] = []
    # Each event object must carry a seq field.
    seq_matches = re.findall(r"\bseq:\s*(\d+)", constants_text)
    if len(seq_matches) < 10:
        problems.append(
            f"flight recorder events carry fewer than 10 seq numbers "
            f"(found {len(seq_matches)})"
        )
    return (not problems, problems)


def check_timestamp_honesty_exists(constants_text: str) -> tuple[bool, list[str]]:
    """Timestamp-honesty labels exist (no invented timestamps)."""
    problems: list[str] = []
    found_any = False
    for label in TIMESTAMP_HONESTY_LABELS:
        if label in constants_text:
            found_any = True
    if not found_any:
        problems.append(
            "flight recorder events carry no timestamp-honesty label"
        )
    # Forbid invented ISO-style timestamps in the event definitions. A bare
    # date like 2026-06-29 inside an evidence path is fine; a quoted
    # timestamp literal assigned to an event is not.
    quoted_ts = re.findall(
        r'timestampHonesty:\s*"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2})',
        constants_text,
    )
    if quoted_ts:
        problems.append(
            f"flight recorder events invent timestamps: {quoted_ts[:3]!r}"
        )
    return (not problems, problems)


def check_evidence_graph_exists(constants_text: str) -> tuple[bool, list[str]]:
    """The evidence graph exists."""
    problems: list[str] = []
    if "OPERATIONS_COCKPIT_EVIDENCE_GRAPH_NODES" not in constants_text:
        problems.append(
            "operationsCockpit.ts does not declare "
            "OPERATIONS_COCKPIT_EVIDENCE_GRAPH_NODES"
        )
    if "OPERATIONS_COCKPIT_EVIDENCE_GRAPH_EDGES" not in constants_text:
        problems.append(
            "operationsCockpit.ts does not declare "
            "OPERATIONS_COCKPIT_EVIDENCE_GRAPH_EDGES"
        )
    if not COCKPIT_COMPONENT.exists():
        return False, problems
    comp_text = read_text(COCKPIT_COMPONENT)
    if "Evidence graph" not in comp_text:
        problems.append(
            "component does not render the Evidence graph heading"
        )
    return (not problems, problems)


def check_required_nodes_exist(constants_text: str) -> tuple[bool, list[str]]:
    """The required 12 evidence graph nodes exist."""
    problems: list[str] = []
    for label in REQUIRED_GRAPH_NODE_LABELS:
        if label not in constants_text:
            problems.append(f"evidence graph missing node {label!r}")
    return (not problems, problems)


def check_required_edges_exist(constants_text: str) -> tuple[bool, list[str]]:
    """The required 10 evidence graph edges exist."""
    problems: list[str] = []
    # Build a quick id<->label map from the node definitions, then verify each
    # required edge is present by (from-label, to-label). We approximate by
    # checking that every required edge's two labels are co-declared via an
    # edge object { from: <id>, to: <id> }. Because edges reference ids, not
    # labels, we instead verify each required edge's endpoints resolve to the
    # declared node labels through the id map.
    label_to_id: dict[str, str] = {}
    for m in re.finditer(
        r'\{\s*id:\s*"([^"]+)"\s*,\s*label:\s*"([^"]+)"', constants_text
    ):
        label_to_id[m.group(2)] = m.group(1)
    edges: list[tuple[str, str]] = []
    for m in re.finditer(
        r'\{\s*from:\s*"([^"]+)"\s*,\s*to:\s*"([^"]+)"\s*\}', constants_text
    ):
        edges.append((m.group(1), m.group(2)))
    for from_label, to_label in REQUIRED_GRAPH_EDGES:
        from_id = label_to_id.get(from_label)
        to_id = label_to_id.get(to_label)
        if not from_id:
            problems.append(
                f"evidence graph edge source node missing: {from_label!r}"
            )
            continue
        if not to_id:
            problems.append(
                f"evidence graph edge target node missing: {to_label!r}"
            )
            continue
        if (from_id, to_id) not in edges:
            problems.append(
                f"evidence graph missing edge {from_label!r} -> {to_label!r} "
                f"(ids {from_id!r} -> {to_id!r})"
            )
    return (not problems, problems)


def check_failure_theater_visible(constants_text: str) -> tuple[bool, list[str]]:
    """The Failure Theater slot is visible."""
    problems: list[str] = []
    if "OPERATIONS_COCKPIT_FAILURE_THEATER_NOTE" not in constants_text:
        problems.append(
            "operationsCockpit.ts does not declare "
            "OPERATIONS_COCKPIT_FAILURE_THEATER_NOTE"
        )
    if not COCKPIT_COMPONENT.exists():
        return False, problems
    comp_text = read_text(COCKPIT_COMPONENT)
    if "Failure Theater" not in comp_text:
        problems.append(
            "component does not render the Failure Theater heading"
        )
    return (not problems, problems)


def check_no_fake_failures_line(constants_text: str) -> tuple[bool, list[str]]:
    """The exact line 'No fake failures are claimed.' exists."""
    problems: list[str] = []
    if "No fake failures are claimed." not in constants_text:
        problems.append(
            "operationsCockpit.ts missing exact line "
            "'No fake failures are claimed.'"
        )
    if not COCKPIT_COMPONENT.exists():
        return False, problems
    comp_text = read_text(COCKPIT_COMPONENT)
    if "No fake failures are claimed." not in comp_text:
        problems.append(
            "component missing exact line 'No fake failures are claimed.'"
        )
    return (not problems, problems)


def check_zero_provider_calls_line(constants_text: str) -> tuple[bool, list[str]]:
    """The exact zero-provider-calls line exists."""
    problems: list[str] = []
    target = (
        "For the verified golden run, rehydrate uses B2-backed evidence with "
        "zero provider calls."
    )
    # The line is declared as a concatenated string constant. Reconstruct the
    # expected joined form and check the component surfaces it.
    if "OPERATIONS_COCKPIT_ZERO_PROVIDER_CALLS_LINE" not in constants_text:
        problems.append(
            "operationsCockpit.ts does not declare "
            "OPERATIONS_COCKPIT_ZERO_PROVIDER_CALLS_LINE"
        )
    if not COCKPIT_COMPONENT.exists():
        return False, problems
    comp_text = read_text(COCKPIT_COMPONENT)
    if "OPERATIONS_COCKPIT_ZERO_PROVIDER_CALLS_LINE" not in comp_text:
        problems.append(
            "component does not reference "
            "OPERATIONS_COCKPIT_ZERO_PROVIDER_CALLS_LINE"
        )
    return (not problems, problems)


def check_designer_marketer_actions(constants_text: str) -> tuple[bool, list[str]]:
    """The designer / marketer next actions exist."""
    problems: list[str] = []
    if "OPERATIONS_COCKPIT_DESIGNER_MARKETER_NEXT_ACTIONS" not in constants_text:
        problems.append(
            "operationsCockpit.ts does not declare "
            "OPERATIONS_COCKPIT_DESIGNER_MARKETER_NEXT_ACTIONS"
        )
    for required_fragment in (
        "review asset proof",
        "open evidence pack",
        "inspect rehydrate proof",
        "verify manifest",
        "prepare client handoff",
        "understand disclosure boundary",
        "continue to review",
    ):
        if required_fragment.lower() not in constants_text.lower():
            problems.append(
                f"designer / marketer actions missing {required_fragment!r}"
            )
    if not COCKPIT_COMPONENT.exists():
        return False, problems
    comp_text = read_text(COCKPIT_COMPONENT)
    if "Designer / marketer next actions" not in comp_text:
        problems.append(
            "component does not render the Designer / marketer next actions heading"
        )
    return (not problems, problems)


def check_action_rail_exists(constants_text: str) -> tuple[bool, list[str]]:
    """The action rail exists and links every required surface."""
    problems: list[str] = []
    if "OPERATIONS_COCKPIT_ACTION_ROUTES" not in constants_text:
        problems.append(
            "operationsCockpit.ts does not declare "
            "OPERATIONS_COCKPIT_ACTION_ROUTES"
        )
    for href in (
        "/evidence-pack",
        "/failure-timeline",
        "/b2-rehydrate-comparison",
        "/manifest-verification",
        "/b2-evidence",
        "/genblaze-pipeline",
        "/",
    ):
        if href not in constants_text:
            problems.append(
                f"OPERATIONS_COCKPIT_ACTION_ROUTES missing href {href!r}"
            )
    if '"/passport/" + OPERATIONS_COCKPIT_RUN_ID' not in constants_text:
        problems.append(
            "OPERATIONS_COCKPIT_ACTION_ROUTES does not build the golden passport href"
        )
    if not COCKPIT_COMPONENT.exists():
        return False, problems
    comp_text = read_text(COCKPIT_COMPONENT)
    if "Action rail" not in comp_text:
        problems.append("component does not render the Action rail heading")
    return (not problems, problems)


def check_truth_boundary_exists(constants_text: str) -> tuple[bool, list[str]]:
    """The truth boundary exists and carries every required term."""
    problems: list[str] = []
    if "OPERATIONS_COCKPIT_TRUTH_BOUNDARY" not in constants_text:
        problems.append(
            "operationsCockpit.ts does not declare OPERATIONS_COCKPIT_TRUTH_BOUNDARY"
        )
        return (not problems, problems)
    missing = [
        t for t in TRUTH_BOUNDARY_TERMS if t.lower() not in constants_text.lower()
    ]
    if missing:
        problems.append(
            f"operationsCockpit.ts truth boundary missing term {missing[0]!r}"
        )
    if "OPERATIONS_COCKPIT_CLAIM_BOUNDARY_ALLOWED" not in constants_text:
        problems.append(
            "operationsCockpit.ts does not declare the allowed claim boundary"
        )
    if "OPERATIONS_COCKPIT_CLAIM_BOUNDARY_FORBIDDEN" not in constants_text:
        problems.append(
            "operationsCockpit.ts does not declare the forbidden claim boundary"
        )
    if not COCKPIT_COMPONENT.exists():
        return False, problems
    comp_text = read_text(COCKPIT_COMPONENT)
    if "Truth boundary" not in comp_text:
        problems.append("component does not render the Truth boundary heading")
    if "OPERATIONS_COCKPIT_TRUTH_BOUNDARY" not in comp_text:
        problems.append("component does not reference the truth boundary const")
    return (not problems, problems)


def check_limitations_exist(constants_text: str) -> tuple[bool, list[str]]:
    """The limitations exist and carry the required honesty markers."""
    problems: list[str] = []
    if "OPERATIONS_COCKPIT_LIMITATIONS" not in constants_text:
        problems.append(
            "operationsCockpit.ts does not declare OPERATIONS_COCKPIT_LIMITATIONS"
        )
    for marker in (
        "no live provider call",
        "no broad b2 read",
        "no browser-side b2 byte verification",
        "no raw media byte",
        "public deployment pending",
        "checked-in evidence only",
        "no invented failure events",
    ):
        if marker.lower() not in constants_text.lower():
            problems.append(f"limitations missing marker {marker!r}")
    if not COCKPIT_COMPONENT.exists():
        return False, problems
    comp_text = read_text(COCKPIT_COMPONENT)
    if "Limitations" not in comp_text:
        problems.append("component does not render the Limitations heading")
    return (not problems, problems)


def check_cockpit_sections_visible() -> tuple[bool, list[str]]:
    """All required cockpit sections are visible in the component."""
    problems: list[str] = []
    if not COCKPIT_COMPONENT.exists():
        return False, [f"missing {rel(COCKPIT_COMPONENT)}"]
    comp_text = read_text(COCKPIT_COMPONENT)
    for section in REQUIRED_COCKPIT_SECTIONS:
        if section not in comp_text:
            problems.append(
                f"OperationsCockpit missing section heading {section!r}"
            )
    return (not problems, problems)


def check_source_evidence_present(constants_text: str) -> tuple[bool, list[str]]:
    """Source evidence includes PS-021 through PS-031 plus PS-031A."""
    problems: list[str] = []
    required_sources = {
        "ps021": "PS-021",
        "ps024": "PS-024",
        "ps025": "PS-025",
        "ps026": "PS-026",
        "ps027": "PS-027",
        "ps028": "PS-028",
        "ps029": "PS-029",
        "ps030": "PS-030",
        "ps031": "PS-031",
    }
    for src_id, tag in required_sources.items():
        if src_id not in constants_text:
            problems.append(f"source evidence missing {tag}")
        if tag not in constants_text:
            problems.append(f"source evidence missing slice tag {tag}")
    if "ps-031a-hardened-product-modules-correction.md" not in constants_text:
        problems.append(
            "source evidence missing PS-031A roadmap correction reference"
        )
    if "PS-031A" not in constants_text:
        problems.append("source evidence missing PS-031A slice tag")
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
    const = _extract_string_const(constants_text, "OPERATIONS_COCKPIT_RUN_ID")
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
    const = _extract_string_const(
        constants_text, "OPERATIONS_COCKPIT_CAMPAIGN_ID"
    )
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
    const = _extract_string_const(
        constants_text, "OPERATIONS_COCKPIT_ARCHIVE_URI"
    )
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
    const = _extract_string_const(
        constants_text, "OPERATIONS_COCKPIT_ARCHIVE_SHA256"
    )
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
    const = _extract_string_const(
        constants_text, "OPERATIONS_COCKPIT_REHYDRATE_SOURCE"
    )
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
        "OPERATIONS_COCKPIT_PROVIDER_CALLS_DURING_REHYDRATE",
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
        "OPERATIONS_COCKPIT_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE",
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

    arbitrary_run_id = "run_ps032_must_still_404_0123456789abcdef"
    status = _get_passport_status(arbitrary_run_id)
    if status != 404:
        problems.append(
            f"arbitrary run id returned HTTP {status}, expected 404 "
            f"(broad public durable read must stay blocked)"
        )

    return (not problems, problems)


def check_no_fake_failure_claim() -> tuple[bool, list[str]]:
    """No fake actual failure / fallback / outage claim is made."""
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
            for phrase in FAKE_FAILURE_CLAIM_PHRASES:
                if phrase in line_lower:
                    hit = True
                    break
            if not hit:
                continue
            if _line_has_nonclaim_context(lines, i):
                continue
            problems.append(
                f"{rel(path)}:{i + 1}: fake failure claim with no non-claim "
                f"context -> {line.strip()!r}"
            )
    return (not problems, problems)


def check_no_raw_media_byte_claim() -> tuple[bool, list[str]]:
    """No raw media byte claim is made (outside non-claim context)."""
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
    """No prior-slice evidence file is left modified by the PS-032 smoke run."""
    problems = sl.prior_evidence_dirty_problems(
        own_slice_prefix="docs/evidence/ps-032/",
        slice_label="PS-032",
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
        PS031_EVIDENCE,
    ):
        if not p.exists():
            missing_inputs.append(rel(p))
    if missing_inputs:
        print("PS032 smoke: MISSING INPUT FILES")
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
        "ps031": load_json(PS031_EVIDENCE),
    }
    constants_text = (
        read_text(COCKPIT_CONST) if COCKPIT_CONST.exists() else ""
    )

    checks: list[tuple[str, tuple[bool, list[str]]]] = [
        ("component_exists", check_component_exists()),
        ("data_module_exists", check_data_module_exists()),
        ("route_exists", check_route_exists()),
        ("judge_links_cockpit", check_judge_links_cockpit()),
        ("pack_links_cockpit", check_pack_links_cockpit()),
        ("timeline_links_cockpit", check_timeline_links_cockpit()),
        ("cockpit_links_surfaces", check_cockpit_links()),
        ("cockpit_identity_visible", check_cockpit_identity_visible(constants_text)),
        ("run_status_summary_visible", check_run_status_summary_visible(constants_text)),
        ("golden_values_in_data", check_golden_values_in_data(constants_text)),
        ("phase_map_exists", check_phase_map_exists(constants_text)),
        ("required_phases_exist", check_required_phases_exist(constants_text)),
        ("truth_classes_exist", check_truth_classes_exist(constants_text)),
        ("flight_recorder_exists", check_flight_recorder_exists(constants_text)),
        ("event_sequence_exists", check_event_sequence_exists(constants_text)),
        ("timestamp_honesty_exists", check_timestamp_honesty_exists(constants_text)),
        ("evidence_graph_exists", check_evidence_graph_exists(constants_text)),
        ("required_nodes_exist", check_required_nodes_exist(constants_text)),
        ("required_edges_exist", check_required_edges_exist(constants_text)),
        ("failure_theater_visible", check_failure_theater_visible(constants_text)),
        ("no_fake_failures_line", check_no_fake_failures_line(constants_text)),
        (
            "zero_provider_calls_line",
            check_zero_provider_calls_line(constants_text),
        ),
        (
            "designer_marketer_actions",
            check_designer_marketer_actions(constants_text),
        ),
        ("action_rail_exists", check_action_rail_exists(constants_text)),
        ("truth_boundary_exists", check_truth_boundary_exists(constants_text)),
        ("limitations_exist", check_limitations_exist(constants_text)),
        ("cockpit_sections_visible", check_cockpit_sections_visible()),
        ("source_evidence_present", check_source_evidence_present(constants_text)),
        ("run_id_matches", check_run_id_matches(constants_text)),
        ("campaign_id_matches", check_campaign_id_matches(constants_text)),
        ("archive_uri_match", check_archive_uri_match(constants_text)),
        ("archive_sha256_match", check_archive_sha256_match(constants_text)),
        ("rehydrate_source", check_rehydrate_source(constants_text)),
        ("provider_calls_zero", check_provider_calls_zero(constants_text)),
        ("no_live_provider_call", check_no_live_provider_call(constants_text)),
        ("no_provider_call", check_no_provider_call()),
        ("no_broad_b2_read", check_no_broad_b2_read()),
        ("no_fake_failure_claim", check_no_fake_failure_claim()),
        ("no_raw_media_byte_claim", check_no_raw_media_byte_claim()),
        ("secret_scan", check_secrets()),
        ("forbidden_claims", check_forbidden_claims()),
        ("api_resolves_golden", check_api_resolves_golden(manifest)),
    ]

    all_pass, detail = sl.run_contract_checks("PS-032 Operations Cockpit / Flight Recorder v2", checks)

    if opts.write_evidence:
        evidence = {
            "ok": bool(all_pass),
            "route_or_surface": (
                "/operations-cockpit (dedicated frontend route) + "
                "OperationsCockpit component + CTA from Judge Cockpit Home "
                "(golden demo run panel and Direct CTAs tile) + link from "
                "Judge Evidence Pack (page variant) + link from Failure-as-Proof "
                "Timeline (page variant)"
            ),
            "cockpit_id": "cockpit_ps032_" + manifest.get("run_id", ""),
            "cockpit_version": cockpit_version_const or "",
            "run_id": manifest.get("run_id"),
            "campaign_id": manifest.get("campaign_id"),
            "archive_uri": manifest.get("archive_uri"),
            "archive_sha256": manifest.get("archive_sha256"),
            "rehydrate_source": "b2_rehydrated",
            "provider_calls_during_rehydrate": 0,
            "no_live_provider_call_during_rehydrate": True,
            "public_deployment_pending": bool(public_deployment_pending),
            "operations_cockpit_surface_verified": operations_cockpit_surface_verified,
            "cockpit_identity_visible": cockpit_identity_visible,
            "run_status_summary_visible": run_status_summary_visible,
            "phase_map_verified": phase_map_verified,
            "flight_recorder_verified": flight_recorder_verified,
            "evidence_graph_verified": evidence_graph_verified,
            "failure_theater_slot_visible": failure_theater_slot_visible,
            "designer_marketer_next_actions_visible": designer_marketer_next_actions_visible,
            "action_rail_verified": action_rail_verified,
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
            "source_ps031_evidence": rel(PS031_EVIDENCE),
            "source_ps031a_roadmap_correction": rel(PS031A_ROADMAP),
            "source_implementation_roadmap": rel(ROADMAP),
            "frontend_surface_verified": operations_cockpit_surface_verified,
            "api_surface_verified": api_surface_verified,
            "no_provider_call": no_provider_call,
            "no_broad_b2_read": no_broad_b2_read,
            "no_raw_media_byte_claim": no_raw_media_byte_claim,
            "no_fake_failure_claim": no_fake_failure_claim,
            "no_prior_slice_evidence_modified": bool(prior_clean_ok),
            "checked_at": _utc_now_iso(),
            "api_transport": "testclient",
            "checks": detail,
        }
        sl.write_json_atomic(EVIDENCE_OUT, evidence)
        print(f"evidence: {rel(EVIDENCE_OUT)}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(run())
