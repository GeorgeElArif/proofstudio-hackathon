#!/usr/bin/env python3
"""PS-034 Lineage + Comparison Lab -- smoke / validation.

PS-034B retrofit: this smoke defaults to safe local / check-only behavior.
It does not run the frontend toolchain, does not use Git index hiding, and
does not self-unlink its evidence file. Evidence is written only when
``--write-evidence`` is passed.

    python scripts/ps034_lineage_comparison_lab_smoke.py --local --check-only

It statically validates the PS-034 Lineage + Comparison Lab surface without
starting a browser, without calling any provider, without reading any B2
object, and without enabling broad durable reads.

Non-recursive prior-slice regression contract: PS-034 does NOT execute any
historical smoke. It verifies the prior accepted slice state in place: each
checked-in evidence file still exists, still records ok=true, and still
re-pins the golden constants consistently with the PS-024 manifest.

Truth boundary: this script validates that the PS-034 surface is honest. It
does not prove semantic truth, legal authenticity, C2PA authenticity, or
human authorship.

Exit code is 0 only when every check passes.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import argparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import smoke_lib as sl  # noqa: E402

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
PS032_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "ps-032" / "operations-cockpit-flight-recorder-v2-smoke.json"
PS033_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "ps-033" / "provider-decision-intelligence-smoke.json"
ROADMAP = REPO_ROOT / "docs" / "roadmap" / "proofstudio-winning-implementation-roadmap-2026-06-29.md"
PS031A_ROADMAP = REPO_ROOT / "docs" / "roadmap" / "ps-031a-hardened-product-modules-correction.md"

# PS-034 changed / added files.
LCL_CONST = REPO_ROOT / "apps" / "web" / "src" / "lineageComparisonLab.ts"
LCL_COMPONENT = REPO_ROOT / "apps" / "web" / "src" / "LineageComparisonLab.tsx"
HOMEPAGE = REPO_ROOT / "apps" / "web" / "src" / "JudgeCockpitHome.tsx"
APP_TSX = REPO_ROOT / "apps" / "web" / "src" / "App.tsx"
PACK_COMPONENT = REPO_ROOT / "apps" / "web" / "src" / "JudgeEvidencePack.tsx"
OPERATIONS_COMPONENT = REPO_ROOT / "apps" / "web" / "src" / "OperationsCockpit.tsx"
PDI_COMPONENT = REPO_ROOT / "apps" / "web" / "src" / "ProviderDecisionIntelligence.tsx"
FAILURE_TIMELINE_COMPONENT = REPO_ROOT / "apps" / "web" / "src" / "FailureAsProofTimeline.tsx"
B2_REHYDRATE_COMPONENT = REPO_ROOT / "apps" / "web" / "src" / "B2RehydrateComparison.tsx"
MANIFEST_PANEL = REPO_ROOT / "apps" / "web" / "src" / "ManifestVerificationPanel.tsx"
B2_EXPLORER = REPO_ROOT / "apps" / "web" / "src" / "B2EvidenceExplorer.tsx"
GENBLAZE_GRAPH = REPO_ROOT / "apps" / "web" / "src" / "GenblazePipelineGraph.tsx"
PUBLIC_PASSPORT = REPO_ROOT / "apps" / "web" / "src" / "PublicPassportPage.tsx"
STYLES = REPO_ROOT / "apps" / "web" / "src" / "styles.css"
PROOF_DOC = REPO_ROOT / "docs" / "ps-034-lineage-comparison-lab-proof.md"

# PS-023 foundational home smoke. PS-023 produces no evidence file; its
# acceptance is represented by the smoke script and the home component being
# present in the tree.
PS023_SMOKE = REPO_ROOT / "scripts" / "ps023_judge_cockpit_home_smoke.py"

# Prior accepted slice evidence files for the non-recursive regression
# contract. PS-033 .. PS-025 each own a checked-in smoke evidence JSON that
# records ok=true and re-pins the golden constants. PS-024 is the golden
# manifest itself (no separate evidence file).
PRIOR_SLICE_EVIDENCE: tuple[tuple[str, Path], ...] = (
    ("ps033", PS033_EVIDENCE),
    ("ps032", PS032_EVIDENCE),
    ("ps031", PS031_EVIDENCE),
    ("ps030", PS030_EVIDENCE),
    ("ps029", PS029_EVIDENCE),
    ("ps028", PS028_EVIDENCE),
    ("ps027", PS027_EVIDENCE),
    ("ps026", PS026_EVIDENCE),
    ("ps025", PS025_EVIDENCE),
)

# Golden constant fields that every prior-slice evidence file must re-pin
# consistently with the PS-024 manifest.
GOLDEN_CONSTANT_FIELDS: tuple[str, ...] = (
    "run_id",
    "campaign_id",
    "archive_uri",
    "archive_sha256",
    "rehydrate_source",
)

# Sibling app routes that PS-034 links to. These must still be registered in
# App.tsx so the lab's outbound links resolve.
REQUIRED_SIBLING_ROUTES: tuple[tuple[str, str], ...] = (
    ("/provider-decision-intelligence", "isProviderDecisionIntelligencePath"),
    ("/operations-cockpit", "isOperationsCockpitPath"),
    ("/evidence-pack", "isEvidencePackPath"),
    ("/failure-timeline", "isFailureTimelinePath"),
    ("/b2-rehydrate-comparison", "isB2RehydrateComparisonPath"),
    ("/manifest-verification", "isManifestVerificationPath"),
    ("/b2-evidence", "isB2EvidencePath"),
    ("/genblaze-pipeline", "isGenblazePipelinePath"),
)

EVIDENCE_OUT = REPO_ROOT / "docs" / "evidence" / "ps-034" / "lineage-comparison-lab-smoke.json"

# Files scanned for secrets and forbidden claims. The scanner script itself is
# intentionally excluded (same convention as PS-023 through PS-033 smokes).
SCAN_FILES: tuple[Path, ...] = (
    LCL_CONST,
    LCL_COMPONENT,
    HOMEPAGE,
    APP_TSX,
    PACK_COMPONENT,
    OPERATIONS_COMPONENT,
    PDI_COMPONENT,
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
# code patterns. Markdown documentation is excluded.
PROVIDER_AND_B2_SCAN_FILES: tuple[Path, ...] = (
    LCL_CONST,
    LCL_COMPONENT,
    HOMEPAGE,
    APP_TSX,
    PACK_COMPONENT,
    OPERATIONS_COMPONENT,
    PDI_COMPONENT,
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

FORBIDDEN_AFFIRMATIVE: tuple[str, ...] = (
    "the surface proves semantic truth",
    "the surface proves media is true",
    "the surface proves legal authenticity",
    "the surface proves human authorship",
    "the surface proves c2pa authenticity",
    "the surface proves object lock",
    "the surface proves tamper-proof storage",
    "the surface certifies authenticity",
    "the surface is a certification",
    "the surface is legally binding",
    "the surface performs browser-side b2 byte verification",
    "the browser fetched and hashed the b2 object",
    "the browser verified the b2 bytes",
    "public deployment is verified",
    "public deployment verified",
    "object lock is enabled",
    "tamper-proof storage is enabled",
    "enterprise-grade security",
    "enterprise security is provided",
)

# Forbidden affirmative overclaims for second variant / provider swap rerun /
# model score / winner / spend / latency. Matched outside a non-claim context.
LINEAGE_OVERCLAIMS: tuple[str, ...] = (
    "a second real variant was captured",
    "two real variants were captured",
    "multiple real variants are captured",
    "a second verified run is available",
    "a provider swap rerun was executed",
    "a provider swap rerun was completed",
    "the provider swap rerun produced",
    "the provider swap rerun completed",
    "model audition results were captured",
    "the model score for the golden run is",
    "a quality score was assigned",
    "the winner of the audition is",
    "the winner is candidate",
    "a winner label was assigned to",
    "actual spend for the golden run was",
    "measured cost for the golden run is",
    "measured latency for the golden run is",
    "production no-key generation is validated",
)

FAKE_FAILURE_CLAIM_PHRASES: tuple[str, ...] = (
    "a provider failure occurred during the golden run",
    "the golden run hit a provider failure",
    "the golden run triggered a fallback",
    "the golden run required a retry",
    "an actual failure was captured for the golden run",
    "the golden run experienced an outage",
    "the golden run fell back to pollinations",
)

RAW_MEDIA_BYTE_CLAIM_PHRASES: tuple[str, ...] = (
    "the surface inspects raw media bytes",
    "the surface reads raw media bytes",
    "the surface fetches raw media bytes",
    "raw media bytes are inspected",
    "inspects raw media bytes",
)

CONTEXT_MARKERS_RE = re.compile(
    r"does not|do not|must not|\bnot\b|non-claim|non-claims|forbidden|"
    r"reject|rejected|avoid|without overclaim|unless actually implemented|"
    r"only inside non-claim|limitation|limitations|no affirmative|"
    r"unavailable|blocked|honestly|no live|no_new|no_fake|pending|planned|"
    r"did not fetch|does not claim|did not claim|does not perform|without|"
    r"none claimed|would appear|if captured|no actual|no fake|not implemented|"
    r"is not implemented|not a certification|not legal advice|"
    r"generated: false|approved: false|no provider|no broad|no browser-side|"
    r"not captured|not claimed|not validated|not verified|not equivalent|"
    r"no invented|no second|no provider swap|no model score|no winner|"
    r"no measured",
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

BROAD_B2_READ_PATTERNS: tuple[str, ...] = (
    "read_archive_from_b2",
    "b2.fetch",
    "b2GetObject",
    "list_b2_objects",
    "fetchB2Object",
    "fetch(",
)

PROVIDER_CALL_PATTERNS: tuple[str, ...] = (
    "call_provider",
    "fetchFromProvider",
    "requests.post",
    "urlopen(",
    "httpx.post",
    "client.post(",
)

REQUIRED_VARIANT_NODE_KINDS: tuple[str, ...] = (
    "campaign",
    "golden_run",
    "asset_manifest",
    "b2_archive",
    "rehydrated_evidence",
    "public_passport",
    "judge_evidence_pack",
    "review_next_action",
)

REQUIRED_VARIANT_NODE_LABELS: tuple[str, ...] = (
    "Campaign",
    "Golden Run",
    "Asset / Manifest",
    "B2 Archive",
    "Rehydrated Evidence",
    "Public Passport",
    "Judge Evidence Pack",
    "Review / Next Action",
)

REQUIRED_RELATIONSHIP_LABELS: tuple[str, ...] = (
    "owns",
    "generated",
    "archived_to",
    "rehydrated_from",
    "exposes",
    "exports",
    "awaits_review",
)

REQUIRED_MANIFEST_DIFF_FIELDS: tuple[str, ...] = (
    "run_id",
    "campaign_id",
    "archive_uri",
    "archive_sha256",
    "rehydrate_source",
    "provider_calls_during_rehydrate",
    "no_live_provider_call_during_rehydrate",
    "public_deployment_pending",
)

REQUIRED_AUDITION_COLUMNS: tuple[str, ...] = (
    "candidate",
    "provider / model role",
    "modality",
    "evidence status",
    "quality review status",
    "cost / time status",
    "proof status",
    "decision",
)

REQUIRED_SWAP_STEPS: tuple[str, ...] = (
    "keep campaign_id",
    "create new run_id",
    "preserve source prompt/brief if available",
    "route through provider decision policy",
    "capture new asset/manifest",
    "archive to b2",
    "compare manifest diff",
    "attach to variant family",
    "update review/export state",
)

REQUIRED_CHECKLIST_LABELS: tuple[str, ...] = (
    "golden run exists",
    "b2 archive exists",
    "manifest hash exists",
    "rehydrate proof exists",
    "provider calls during rehydrate captured",
    "evidence pack exists",
    "operations cockpit exists",
    "provider decision policy exists",
    "second real variant exists",
    "model scores captured",
    "measured cost captured",
    "measured latency captured",
    "review decision captured",
)

# Exact truth-line literals mirrored verbatim from lineageComparisonLab.ts so
# the smoke can verify they appear in both the data module and the component.
LINEAGE_COMPARISON_LAB_ONLY_ONE_RUN_LINE = (
    "Only one verified golden run is available in checked-in evidence."
)
LINEAGE_COMPARISON_LAB_NO_PROVIDER_SWAP_LINE = (
    "No provider swap rerun is claimed for the verified golden run."
)
LINEAGE_COMPARISON_LAB_SELECTED_PROVIDER_NOT_CAPTURED = (
    "selected provider/model not captured in checked-in evidence"
)
LINEAGE_COMPARISON_LAB_AUDITION_SLOT_NOT_RUN = "audition slot not run"


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
# Constant extraction from lineageComparisonLab.ts
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
    "ps032",
    "ps033",
)

SOURCE_KEY_OVERRIDES: dict[str, dict[str, str]] = {
    "ps021": {"rehydrate_source": "durable_source"},
}

SOURCE_JSON: dict[str, dict] = {}


def _source_field_value(source_id: str, field_key: str) -> Any:
    src = SOURCE_JSON.get(source_id, {})
    key = SOURCE_KEY_OVERRIDES.get(source_id, {}).get(field_key, field_key)
    return src.get(key)


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_component_exists() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not LCL_COMPONENT.exists():
        problems.append(f"missing component {rel(LCL_COMPONENT)}")
    return (not problems, problems)


def check_data_module_exists() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not LCL_CONST.exists():
        problems.append(f"missing constants module {rel(LCL_CONST)}")
    return (not problems, problems)


def check_route_exists() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not APP_TSX.exists():
        return False, [f"missing {rel(APP_TSX)}"]
    text = read_text(APP_TSX)
    if "isLineageComparisonLabPath" not in text:
        problems.append(
            "App.tsx does not register an isLineageComparisonLabPath helper"
        )
    if "/lineage-comparison-lab" not in text:
        problems.append(
            "App.tsx does not reference the /lineage-comparison-lab path"
        )
    if "LineageComparisonLab" not in text:
        problems.append(
            "App.tsx does not render the LineageComparisonLab component"
        )
    return (not problems, problems)


def _check_link_surface(path: Path, surface_name: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not path.exists():
        return False, [f"missing {rel(path)}"]
    text = read_text(path)
    if "/lineage-comparison-lab" not in text:
        problems.append(f"{surface_name} does not link to /lineage-comparison-lab")
    if "Open Lineage + Comparison Lab" not in text:
        problems.append(
            f"{surface_name} does not surface a Lineage + Comparison Lab CTA label"
        )
    return (not problems, problems)


def check_judge_links_surface() -> tuple[bool, list[str]]:
    return _check_link_surface(HOMEPAGE, "Judge Cockpit Home")


def check_operations_links_surface() -> tuple[bool, list[str]]:
    return _check_link_surface(OPERATIONS_COMPONENT, "Operations Cockpit")


def check_provider_decision_links_surface() -> tuple[bool, list[str]]:
    return _check_link_surface(PDI_COMPONENT, "Provider Decision Intelligence")


def check_pack_links_surface() -> tuple[bool, list[str]]:
    return _check_link_surface(PACK_COMPONENT, "Judge Evidence Pack")


def check_surface_links() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not LCL_COMPONENT.exists():
        return False, [f"missing {rel(LCL_COMPONENT)}"]
    comp_text = read_text(LCL_COMPONENT)
    if not LCL_CONST.exists():
        return False, [f"missing {rel(LCL_CONST)}"]
    const_text = read_text(LCL_CONST)
    for href, label in (
        ("/provider-decision-intelligence", "provider-decision-intelligence"),
        ("/operations-cockpit", "operations-cockpit"),
        ("/evidence-pack", "evidence-pack"),
        ("/failure-timeline", "failure-timeline"),
        ("/b2-rehydrate-comparison", "b2-rehydrate-comparison"),
        ("/manifest-verification", "manifest-verification"),
        ("/b2-evidence", "b2-evidence"),
        ("/genblaze-pipeline", "genblaze-pipeline"),
    ):
        if href not in comp_text and href not in const_text:
            problems.append(f"surface does not link to {href} ({label})")
    golden_href = "/passport/" + _source_field_value("ps024", "run_id")
    if (
        golden_href not in comp_text
        and golden_href not in const_text
        and '"/passport/" + LINEAGE_COMPARISON_LAB_RUN_ID' not in comp_text
    ):
        problems.append(
            "surface does not link to the golden passport via " + golden_href
        )
    if 'href="/"' not in comp_text:
        problems.append("surface does not link back to / (Judge Cockpit Home)")
    return (not problems, problems)


def check_lab_identity_visible(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not LCL_COMPONENT.exists():
        return False, problems
    comp_text = read_text(LCL_COMPONENT)
    for required in (
        "Lineage + Comparison Lab",
        "Model Audition Board",
        "Manifest Diff",
        "Provider Swap Re-run",
        "Variant Family Tree",
        "PS-034",
    ):
        if required not in comp_text:
            problems.append(f"lab identity missing label {required!r}")
    for const_name in (
        "LINEAGE_COMPARISON_LAB_ID",
        "LINEAGE_COMPARISON_LAB_VERSION",
        "LINEAGE_COMPARISON_LAB_RUN_ID",
        "LINEAGE_COMPARISON_LAB_CAMPAIGN_ID",
        "LINEAGE_COMPARISON_LAB_PUBLIC_DEPLOYMENT_PENDING",
    ):
        if const_name not in constants_text:
            problems.append(
                f"lineageComparisonLab.ts missing identity const {const_name!r}"
            )
    if "public deployment" not in comp_text.lower():
        problems.append(
            "lab identity does not surface 'public deployment pending'"
        )
    return (not problems, problems)


def check_lineage_summary_visible(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if "LINEAGE_COMPARISON_LAB_LINEAGE_SUMMARY" not in constants_text:
        problems.append(
            "lineageComparisonLab.ts does not declare "
            "LINEAGE_COMPARISON_LAB_LINEAGE_SUMMARY"
        )
    if not LCL_COMPONENT.exists():
        return False, problems
    comp_text = read_text(LCL_COMPONENT)
    if "Lineage Summary" not in comp_text:
        problems.append("component does not render the Lineage Summary heading")
    if "LINEAGE_COMPARISON_LAB_ONLY_ONE_RUN_LINE" not in comp_text:
        problems.append("component does not reference the only-one-run truth const")
    return (not problems, problems)


def check_golden_values_in_data(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    for const_name in (
        "LINEAGE_COMPARISON_LAB_ARCHIVE_URI",
        "LINEAGE_COMPARISON_LAB_ARCHIVE_SHA256",
        "LINEAGE_COMPARISON_LAB_REHYDRATE_SOURCE",
        "LINEAGE_COMPARISON_LAB_PROVIDER_CALLS_DURING_REHYDRATE",
        "LINEAGE_COMPARISON_LAB_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE",
    ):
        if const_name not in constants_text:
            problems.append(
                f"lineageComparisonLab.ts missing golden const {const_name!r}"
            )
    return (not problems, problems)


def check_variant_family_tree(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if "LINEAGE_COMPARISON_LAB_VARIANT_FAMILY_NODES" not in constants_text:
        problems.append(
            "lineageComparisonLab.ts does not declare variant family nodes"
        )
    if "LINEAGE_COMPARISON_LAB_VARIANT_FAMILY_EDGES" not in constants_text:
        problems.append(
            "lineageComparisonLab.ts does not declare variant family edges"
        )
    if not LCL_COMPONENT.exists():
        return False, problems
    comp_text = read_text(LCL_COMPONENT)
    if "Variant Family Tree" not in comp_text:
        problems.append("component does not render the Variant Family Tree heading")
    return (not problems, problems)


def check_required_variant_nodes(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    for kind in REQUIRED_VARIANT_NODE_KINDS:
        if f'kind: "{kind}"' not in constants_text:
            problems.append(f"variant family tree missing node kind {kind!r}")
    for label in REQUIRED_VARIANT_NODE_LABELS:
        if label not in constants_text:
            problems.append(f"variant family tree missing node label {label!r}")
    return (not problems, problems)


def check_required_relationship_labels(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    for label in REQUIRED_RELATIONSHIP_LABELS:
        if f'label: "{label}"' not in constants_text:
            problems.append(f"variant family tree missing relationship {label!r}")
    return (not problems, problems)


def check_future_variant_slot_honest(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if "future variant slot" not in constants_text:
        problems.append("variant family tree missing honest 'future variant slot'")
    if "not captured in checked-in evidence" not in constants_text:
        problems.append(
            "variant family tree missing honest 'not captured in checked-in "
            "evidence'"
        )
    return (not problems, problems)


def check_manifest_diff_exists(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if "LINEAGE_COMPARISON_LAB_MANIFEST_DIFF" not in constants_text:
        problems.append(
            "lineageComparisonLab.ts does not declare "
            "LINEAGE_COMPARISON_LAB_MANIFEST_DIFF"
        )
    if not LCL_COMPONENT.exists():
        return False, problems
    comp_text = read_text(LCL_COMPONENT)
    if "Manifest Diff" not in comp_text:
        problems.append("component does not render the Manifest Diff heading")
    return (not problems, problems)


def check_manifest_diff_fields(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    for field in REQUIRED_MANIFEST_DIFF_FIELDS:
        if f'field: "{field}"' not in constants_text:
            problems.append(f"manifest diff missing field {field!r}")
    for field in (
        "leftSource:",
        "leftValue:",
        "rightComparison:",
        "rightValue:",
        "matchStatus:",
        "evidenceSource:",
        "truthClass:",
    ):
        if field not in constants_text:
            problems.append(f"manifest diff missing column {field!r}")
    return (not problems, problems)


def check_manifest_diff_match_status(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if 'matchStatus: "match"' not in constants_text:
        problems.append("manifest diff has no 'match' row")
    if (
        'matchStatus: "not_captured"' not in constants_text
        and 'matchStatus: "partial"' not in constants_text
    ):
        problems.append("manifest diff has no honest non-match row")
    if not LCL_COMPONENT.exists():
        return False, problems
    comp_text = read_text(LCL_COMPONENT)
    if "match status" not in comp_text.lower():
        problems.append("component does not surface manifest diff match status")
    return (not problems, problems)


def check_manifest_diff_missing_honest(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if "not captured in checked-in evidence" not in constants_text:
        problems.append(
            "manifest diff does not use the honest 'not captured in checked-in "
            "evidence' label"
        )
    return (not problems, problems)


def check_model_audition_board(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if "LINEAGE_COMPARISON_LAB_MODEL_AUDITION_BOARD" not in constants_text:
        problems.append(
            "lineageComparisonLab.ts does not declare "
            "LINEAGE_COMPARISON_LAB_MODEL_AUDITION_BOARD"
        )
    if not LCL_COMPONENT.exists():
        return False, problems
    comp_text = read_text(LCL_COMPONENT)
    if "Model Audition Board" not in comp_text:
        problems.append(
            "component does not render the Model Audition Board heading"
        )
    return (not problems, problems)


def check_model_audition_columns(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    for field in (
        "candidate:",
        "providerModelRole:",
        "modality:",
        "evidenceStatus:",
        "qualityReviewStatus:",
        "costTimeStatus:",
        "proofStatus:",
        "decision:",
    ):
        if field not in constants_text:
            problems.append(f"model audition board missing field {field!r}")
    if not LCL_COMPONENT.exists():
        return False, problems
    comp_text = read_text(LCL_COMPONENT)
    for col in REQUIRED_AUDITION_COLUMNS:
        if col not in comp_text.lower():
            problems.append(f"component missing audition column {col!r}")
    return (not problems, problems)


def check_selected_provider_not_captured(
    constants_text: str,
) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if (
        LINEAGE_COMPARISON_LAB_SELECTED_PROVIDER_NOT_CAPTURED not in constants_text
    ):
        problems.append(
            "model audition board does not disclose 'selected provider/model "
            "not captured'"
        )
    return (not problems, problems)


def check_audition_slots_not_run(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if LINEAGE_COMPARISON_LAB_AUDITION_SLOT_NOT_RUN not in constants_text:
        problems.append(
            "model audition board does not mark future slots as 'audition slot "
            "not run'"
        )
    return (not problems, problems)


def check_provider_swap_planner(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if "LINEAGE_COMPARISON_LAB_PROVIDER_SWAP_RERUN_PLANNER" not in constants_text:
        problems.append(
            "lineageComparisonLab.ts does not declare the provider swap planner"
        )
    if not LCL_COMPONENT.exists():
        return False, problems
    comp_text = read_text(LCL_COMPONENT)
    if "Provider Swap Re-run Planner" not in comp_text:
        problems.append(
            "component does not render the Provider Swap Re-run Planner heading"
        )
    return (not problems, problems)


def check_provider_swap_steps(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    joined = constants_text.lower()
    for step in REQUIRED_SWAP_STEPS:
        if step not in joined:
            problems.append(f"provider swap planner missing step {step!r}")
    return (not problems, problems)


def check_no_provider_swap_line(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if LINEAGE_COMPARISON_LAB_NO_PROVIDER_SWAP_LINE not in constants_text:
        problems.append(
            "provider swap planner missing the exact no-swap truth line"
        )
    if not LCL_COMPONENT.exists():
        return False, problems
    comp_text = read_text(LCL_COMPONENT)
    if "LINEAGE_COMPARISON_LAB_NO_PROVIDER_SWAP_LINE" not in comp_text:
        problems.append(
            "component does not reference the no-swap truth const"
        )
    return (not problems, problems)


def check_comparison_readiness(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if (
        "LINEAGE_COMPARISON_LAB_COMPARISON_READINESS_CHECKLIST"
        not in constants_text
    ):
        problems.append(
            "lineageComparisonLab.ts does not declare the comparison readiness "
            "checklist"
        )
    if not LCL_COMPONENT.exists():
        return False, problems
    comp_text = read_text(LCL_COMPONENT)
    if "Comparison Readiness Checklist" not in comp_text:
        problems.append(
            "component does not render the Comparison Readiness Checklist heading"
        )
    return (not problems, problems)


def check_checklist_items(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    joined = constants_text.lower()
    for label in REQUIRED_CHECKLIST_LABELS:
        if label not in joined:
            problems.append(f"comparison readiness checklist missing item {label!r}")
    if 'present: true' not in constants_text:
        problems.append("comparison readiness checklist has no present item")
    if 'present: false' not in constants_text:
        problems.append("comparison readiness checklist has no honestly missing item")
    return (not problems, problems)


def check_designer_marketer(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if (
        "LINEAGE_COMPARISON_LAB_DESIGNER_MARKETER_INTERPRETATION"
        not in constants_text
    ):
        problems.append(
            "lineageComparisonLab.ts does not declare the designer/marketer "
            "interpretation"
        )
    for fragment in (
        "whyLineageMatters",
        "whyComparingVariantsHelpsCampaigns",
        "whyManifestDiffMatters",
        "howProviderSwapsHelpCreativeTeams",
        "whenToRerunWithAnotherModel",
        "whenToExportTheEvidencePack",
        "whyMissingVariantDataIsNotAFailure",
    ):
        if fragment not in constants_text:
            problems.append(f"designer/marketer missing field {fragment!r}")
    if not LCL_COMPONENT.exists():
        return False, problems
    comp_text = read_text(LCL_COMPONENT)
    if "Designer / Marketer Interpretation" not in comp_text:
        problems.append(
            "component does not render the Designer / Marketer Interpretation heading"
        )
    return (not problems, problems)


def check_action_rail(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if "LINEAGE_COMPARISON_LAB_ACTION_ROUTES" not in constants_text:
        problems.append(
            "lineageComparisonLab.ts does not declare "
            "LINEAGE_COMPARISON_LAB_ACTION_ROUTES"
        )
    for href in (
        "/provider-decision-intelligence",
        "/operations-cockpit",
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
                f"LINEAGE_COMPARISON_LAB_ACTION_ROUTES missing href {href!r}"
            )
    if '"/passport/" + LINEAGE_COMPARISON_LAB_RUN_ID' not in constants_text:
        problems.append("action routes do not build the golden passport href")
    if not LCL_COMPONENT.exists():
        return False, problems
    comp_text = read_text(LCL_COMPONENT)
    if "Action Rail" not in comp_text:
        problems.append("component does not render the Action Rail heading")
    return (not problems, problems)


def check_truth_boundary(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if "LINEAGE_COMPARISON_LAB_TRUTH_BOUNDARY" not in constants_text:
        problems.append(
            "lineageComparisonLab.ts does not declare a truth boundary"
        )
        return (not problems, problems)
    missing = [
        t for t in TRUTH_BOUNDARY_TERMS if t.lower() not in constants_text.lower()
    ]
    if missing:
        problems.append(
            f"lineageComparisonLab.ts truth boundary missing term {missing[0]!r}"
        )
    if "LINEAGE_COMPARISON_LAB_CLAIM_BOUNDARY_ALLOWED" not in constants_text:
        problems.append("missing the allowed claim boundary")
    if "LINEAGE_COMPARISON_LAB_CLAIM_BOUNDARY_FORBIDDEN" not in constants_text:
        problems.append("missing the forbidden claim boundary")
    if not LCL_COMPONENT.exists():
        return False, problems
    comp_text = read_text(LCL_COMPONENT)
    if "Truth Boundary" not in comp_text:
        problems.append("component does not render the Truth Boundary heading")
    return (not problems, problems)


def check_limitations(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if "LINEAGE_COMPARISON_LAB_LIMITATIONS" not in constants_text:
        problems.append(
            "lineageComparisonLab.ts does not declare "
            "LINEAGE_COMPARISON_LAB_LIMITATIONS"
        )
    for marker in (
        "no live provider call",
        "no provider swap rerun executed",
        "no second real variant captured",
        "no model score captured",
        "no broad b2 read",
        "no live pricing api",
        "no measured billing",
        "no measured latency",
        "public deployment pending",
        "checked-in evidence and documented policy only",
        "no invented variant events",
    ):
        if marker.lower() not in constants_text.lower():
            problems.append(f"limitations missing marker {marker!r}")
    if not LCL_COMPONENT.exists():
        return False, problems
    comp_text = read_text(LCL_COMPONENT)
    if "Limitations" not in comp_text:
        problems.append("component does not render the Limitations heading")
    return (not problems, problems)


def check_only_one_run_line(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if LINEAGE_COMPARISON_LAB_ONLY_ONE_RUN_LINE not in constants_text:
        problems.append(
            "data module missing the exact only-one-run truth line"
        )
    if not LCL_COMPONENT.exists():
        return False, problems
    comp_text = read_text(LCL_COMPONENT)
    if "LINEAGE_COMPARISON_LAB_ONLY_ONE_RUN_LINE" not in comp_text:
        problems.append("component does not reference the only-one-run truth const")
    return (not problems, problems)


def check_source_evidence_present(constants_text: str) -> tuple[bool, list[str]]:
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
        "ps032": "PS-032",
        "ps033": "PS-033",
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
    const = _extract_string_const(constants_text, "LINEAGE_COMPARISON_LAB_RUN_ID")
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
        constants_text, "LINEAGE_COMPARISON_LAB_CAMPAIGN_ID"
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
        constants_text, "LINEAGE_COMPARISON_LAB_ARCHIVE_URI"
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
        constants_text, "LINEAGE_COMPARISON_LAB_ARCHIVE_SHA256"
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
        constants_text, "LINEAGE_COMPARISON_LAB_REHYDRATE_SOURCE"
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
        "LINEAGE_COMPARISON_LAB_PROVIDER_CALLS_DURING_REHYDRATE",
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
        "LINEAGE_COMPARISON_LAB_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE",
    )
    if const is not True:
        problems.append(
            f"no_live_provider_call_during_rehydrate: frontend constant="
            f"{const!r}, expected True"
        )
    return (not problems, problems)


def check_no_provider_call() -> tuple[bool, list[str]]:
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

    arbitrary_run_id = "run_ps034_must_still_404_0123456789abcdef"
    status = _get_passport_status(arbitrary_run_id)
    if status != 404:
        problems.append(
            f"arbitrary run id returned HTTP {status}, expected 404 "
            f"(broad public durable read must stay blocked)"
        )

    return (not problems, problems)


def _scan_for_claim(
    phrases: tuple[str, ...],
) -> tuple[bool, list[str]]:
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
            for phrase in phrases:
                if phrase in line_lower:
                    hit = True
                    break
            if not hit:
                continue
            if _line_has_nonclaim_context(lines, i):
                continue
            problems.append(
                f"{rel(path)}:{i + 1}: overclaim with no non-claim context -> "
                f"{line.strip()!r}"
            )
    return (not problems, problems)


def check_no_fake_failure_claim() -> tuple[bool, list[str]]:
    return _scan_for_claim(FAKE_FAILURE_CLAIM_PHRASES)


def check_no_raw_media_byte_claim() -> tuple[bool, list[str]]:
    return _scan_for_claim(RAW_MEDIA_BYTE_CLAIM_PHRASES)


def check_no_lineage_overclaim() -> tuple[bool, list[str]]:
    """No second-variant / provider-swap-rerun / model-score / winner /
    spend / latency overclaim without evidence."""
    return _scan_for_claim(LINEAGE_OVERCLAIMS)


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
    return _scan_for_claim(FORBIDDEN_AFFIRMATIVE)


def check_api_resolves_golden(manifest: dict) -> tuple[bool, list[str]]:
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
# Non-recursive prior-slice regression contract
# ---------------------------------------------------------------------------
#
# PS-034 does NOT execute any historical smoke. Historical smokes already
# include their own transitive regressions, and nesting them made the chain
# O(n^2) and prone to timeout (PS-030 timed out after 300s when nested under
# PS-034). Instead we verify the prior accepted slice state in place: each
# checked-in evidence file still exists, still records ok=true, and still
# re-pins the golden constants consistently with the PS-024 manifest.

def _prior_slice_contract(manifest: dict) -> dict[str, tuple[bool, list[str]]]:
    """Verify the prior accepted slice state without running any historical smoke.

    Returns a mapping of result key (``ps033_passes`` .. ``ps023_passes``) to
    ``(ok, problems)``. The keys are retained for result continuity but their
    meaning is "prior accepted regression contract is still satisfied", NOT
    "recursively executed the full historical smoke".
    """
    results: dict[str, tuple[bool, list[str]]] = {}
    want = {f: manifest.get(f) for f in GOLDEN_CONSTANT_FIELDS}

    # PS-024 golden manifest: golden constants present.
    ps024_problems: list[str] = []
    if not MANIFEST.exists():
        ps024_problems.append(f"missing PS-024 golden manifest {rel(MANIFEST)}")
    else:
        for f in GOLDEN_CONSTANT_FIELDS:
            if manifest.get(f) in (None, ""):
                ps024_problems.append(
                    f"PS-024 manifest missing golden field {f!r}"
                )
    results["ps024_passes"] = (not ps024_problems, ps024_problems)

    # PS-023 foundational home smoke: no evidence file; represented by the
    # smoke script and the home component being present.
    ps023_problems: list[str] = []
    if not PS023_SMOKE.exists():
        ps023_problems.append(f"missing PS-023 smoke {rel(PS023_SMOKE)}")
    if not HOMEPAGE.exists():
        ps023_problems.append(
            f"missing PS-023 home component {rel(HOMEPAGE)}"
        )
    results["ps023_passes"] = (not ps023_problems, ps023_problems)

    # PS-033 .. PS-025: checked-in evidence present, ok=true, golden constants
    # re-pinned consistently with the PS-024 manifest.
    for slice_id, path in PRIOR_SLICE_EVIDENCE:
        problems: list[str] = []
        if not path.exists():
            problems.append(f"missing prior accepted evidence {rel(path)}")
        else:
            try:
                ev = json.loads(read_text(path))
            except Exception as exc:
                problems.append(f"{rel(path)} not valid JSON: {exc}")
                ev = {}
            if ev.get("ok") is not True:
                problems.append(
                    f"{rel(path)} ok={ev.get('ok')!r}, expected true"
                )
            for f in GOLDEN_CONSTANT_FIELDS:
                got = ev.get(f)
                if got != want[f]:
                    problems.append(
                        f"{rel(path)} {f}={got!r}, manifest={want[f]!r}"
                    )
        results[f"{slice_id}_passes"] = (not problems, problems)
    return results


def check_sibling_routes_exist() -> tuple[bool, list[str]]:
    """Verify the sibling routes / golden passport surface that PS-034 links to
    are still registered in App.tsx. Read-only: no historical smoke is run."""
    problems: list[str] = []
    if not APP_TSX.exists():
        return False, [f"missing {rel(APP_TSX)}"]
    text = read_text(APP_TSX)
    for href, helper in REQUIRED_SIBLING_ROUTES:
        if helper not in text:
            problems.append(
                f"App.tsx missing route helper {helper!r} for {href}"
            )
        if href not in text:
            problems.append(f"App.tsx missing route path {href!r}")
    if "getPublicPassportRunId" not in text:
        problems.append(
            "App.tsx missing golden passport route (getPublicPassportRunId)"
        )
    if PUBLIC_PASSPORT.exists():
        if "getPublicPassportRunId" not in read_text(PUBLIC_PASSPORT):
            problems.append(
                f"{rel(PUBLIC_PASSPORT)} missing getPublicPassportRunId export"
            )
    else:
        problems.append(f"missing golden passport surface {rel(PUBLIC_PASSPORT)}")
    return (not problems, problems)


def check_no_prior_slice_evidence_modified() -> tuple[bool, list[str]]:
    problems = sl.prior_evidence_dirty_problems(
        own_slice_prefix="docs/evidence/ps-034/",
        slice_label="PS-034",
    )
    return (not problems, problems)


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

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
        PS032_EVIDENCE,
        PS033_EVIDENCE,
        ROADMAP,
        PS031A_ROADMAP,
    ):
        if not p.exists():
            missing_inputs.append(rel(p))
    if missing_inputs:
        print("PS-034 smoke: MISSING INPUT FILES")
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
        "ps032": load_json(PS032_EVIDENCE),
        "ps033": load_json(PS033_EVIDENCE),
    }
    constants_text = read_text(LCL_CONST) if LCL_CONST.exists() else ""

    checks: list[tuple[str, tuple[bool, list[str]]]] = [
        ("component_exists", check_component_exists()),
        ("data_module_exists", check_data_module_exists()),
        ("route_exists", check_route_exists()),
        ("sibling_routes_exist", check_sibling_routes_exist()),
        ("judge_links_surface", check_judge_links_surface()),
        ("operations_links_surface", check_operations_links_surface()),
        ("provider_decision_links_surface", check_provider_decision_links_surface()),
        ("pack_links_surface", check_pack_links_surface()),
        ("surface_links_surfaces", check_surface_links()),
        ("lab_identity_visible", check_lab_identity_visible(constants_text)),
        ("lineage_summary_visible", check_lineage_summary_visible(constants_text)),
        ("golden_values_in_data", check_golden_values_in_data(constants_text)),
        ("variant_family_tree", check_variant_family_tree(constants_text)),
        ("required_variant_nodes", check_required_variant_nodes(constants_text)),
        (
            "required_relationship_labels",
            check_required_relationship_labels(constants_text),
        ),
        (
            "future_variant_slot_honest",
            check_future_variant_slot_honest(constants_text),
        ),
        ("manifest_diff_exists", check_manifest_diff_exists(constants_text)),
        ("manifest_diff_fields", check_manifest_diff_fields(constants_text)),
        (
            "manifest_diff_match_status",
            check_manifest_diff_match_status(constants_text),
        ),
        (
            "manifest_diff_missing_honest",
            check_manifest_diff_missing_honest(constants_text),
        ),
        ("model_audition_board", check_model_audition_board(constants_text)),
        ("model_audition_columns", check_model_audition_columns(constants_text)),
        (
            "selected_provider_not_captured",
            check_selected_provider_not_captured(constants_text),
        ),
        ("audition_slots_not_run", check_audition_slots_not_run(constants_text)),
        ("provider_swap_planner", check_provider_swap_planner(constants_text)),
        ("provider_swap_steps", check_provider_swap_steps(constants_text)),
        ("no_provider_swap_line", check_no_provider_swap_line(constants_text)),
        ("comparison_readiness", check_comparison_readiness(constants_text)),
        ("checklist_items", check_checklist_items(constants_text)),
        ("designer_marketer", check_designer_marketer(constants_text)),
        ("action_rail", check_action_rail(constants_text)),
        ("truth_boundary", check_truth_boundary(constants_text)),
        ("limitations", check_limitations(constants_text)),
        ("only_one_run_line", check_only_one_run_line(constants_text)),
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
        ("no_lineage_overclaim", check_no_lineage_overclaim()),
        ("secret_scan", check_secrets()),
        ("forbidden_claims", check_forbidden_claims()),
        ("api_resolves_golden", check_api_resolves_golden(manifest)),
    ]

    # Non-recursive prior-slice regression contract. PS-034 does NOT execute
    # any historical smoke (historical smokes already include their own
    # transitive regressions and time out when nested, making the former
    # recursive chain O(n^2)). Instead we verify the prior accepted slice
    # state in place: each checked-in evidence file still exists, still
    # records ok=true, and still re-pins the golden constants consistently
    # with the PS-024 manifest; the sibling routes PS-034 links to are still
    # registered; and no prior-slice evidence is dirty in git status. The
    # per-slice result keys (ps033_passes .. ps023_passes) are retained for
    # result continuity, but their meaning is now "prior accepted regression
    # contract is still satisfied".
    contract = _prior_slice_contract(manifest)
    ps033_ok, ps033_problems = contract["ps033_passes"]
    ps032_ok, ps032_problems = contract["ps032_passes"]
    ps031_ok, ps031_problems = contract["ps031_passes"]
    ps030_ok, ps030_problems = contract["ps030_passes"]
    ps029_ok, ps029_problems = contract["ps029_passes"]
    ps028_ok, ps028_problems = contract["ps028_passes"]
    ps027_ok, ps027_problems = contract["ps027_passes"]
    ps026_ok, ps026_problems = contract["ps026_passes"]
    ps025_ok, ps025_problems = contract["ps025_passes"]
    ps024_ok, ps024_problems = contract["ps024_passes"]
    ps023_ok, ps023_problems = contract["ps023_passes"]

    prior_clean_ok, prior_clean_problems = check_no_prior_slice_evidence_modified()

    downstream_checks: list[tuple[str, tuple[bool, list[str]]]] = [
        (
            "ps033_passes",
            (ps033_ok, ps033_problems),
        ),
        (
            "ps032_passes",
            (ps032_ok, ps032_problems),
        ),
        (
            "ps031_passes",
            (ps031_ok, ps031_problems),
        ),
        (
            "ps030_passes",
            (ps030_ok, ps030_problems),
        ),
        (
            "ps029_passes",
            (ps029_ok, ps029_problems),
        ),
        (
            "ps028_passes",
            (ps028_ok, ps028_problems),
        ),
        (
            "ps027_passes",
            (ps027_ok, ps027_problems),
        ),
        (
            "ps026_passes",
            (ps026_ok, ps026_problems),
        ),
        (
            "ps025_passes",
            (ps025_ok, ps025_problems),
        ),
        (
            "ps024_passes",
            (ps024_ok, ps024_problems),
        ),
        (
            "ps023_passes",
            (ps023_ok, ps023_problems),
        ),
        (
            "no_prior_slice_evidence_modified",
            (prior_clean_ok, prior_clean_problems),
        ),
    ]
    checks += downstream_checks

    all_pass, detail = sl.run_contract_checks("PS-034 Lineage + Comparison Lab", checks)

    lineage_comparison_surface_verified = bool(
        check_component_exists()[0]
        and check_data_module_exists()[0]
        and check_route_exists()[0]
        and check_surface_links()[0]
    )
    lab_identity_visible = bool(check_lab_identity_visible(constants_text)[0])
    lineage_summary_visible = bool(
        check_lineage_summary_visible(constants_text)[0]
    )
    variant_family_tree_verified = bool(
        check_variant_family_tree(constants_text)[0]
        and check_required_variant_nodes(constants_text)[0]
        and check_required_relationship_labels(constants_text)[0]
        and check_future_variant_slot_honest(constants_text)[0]
    )
    manifest_diff_verified = bool(
        check_manifest_diff_exists(constants_text)[0]
        and check_manifest_diff_fields(constants_text)[0]
        and check_manifest_diff_match_status(constants_text)[0]
        and check_manifest_diff_missing_honest(constants_text)[0]
    )
    model_audition_board_visible = bool(
        check_model_audition_board(constants_text)[0]
        and check_model_audition_columns(constants_text)[0]
        and check_selected_provider_not_captured(constants_text)[0]
        and check_audition_slots_not_run(constants_text)[0]
    )
    provider_swap_rerun_planner_visible = bool(
        check_provider_swap_planner(constants_text)[0]
        and check_provider_swap_steps(constants_text)[0]
        and check_no_provider_swap_line(constants_text)[0]
    )
    comparison_readiness_checklist_visible = bool(
        check_comparison_readiness(constants_text)[0]
        and check_checklist_items(constants_text)[0]
    )
    designer_marketer_interpretation_visible = bool(
        check_designer_marketer(constants_text)[0]
    )
    action_rail_verified = bool(check_action_rail(constants_text)[0])
    truth_boundary_present = bool(check_truth_boundary(constants_text)[0])
    limitations_present = bool(check_limitations(constants_text)[0])
    api_surface_verified = bool(check_api_resolves_golden(manifest)[0])
    no_provider_call = bool(check_no_provider_call()[0])
    no_broad_b2_read = bool(check_no_broad_b2_read()[0])
    no_raw_media_byte_claim = bool(check_no_raw_media_byte_claim()[0])
    no_fake_failure_claim = bool(check_no_fake_failure_claim()[0])
    no_lineage_overclaim = bool(check_no_lineage_overclaim()[0])
    no_forbidden_authenticity = bool(check_forbidden_claims()[0])
    public_deployment_pending = bool(
        _extract_bool_const(
            constants_text,
            "LINEAGE_COMPARISON_LAB_PUBLIC_DEPLOYMENT_PENDING",
        )
        is True
    )
    lab_version_const = _extract_string_const(
        constants_text, "LINEAGE_COMPARISON_LAB_VERSION"
    )

    evidence = {
        "ok": bool(all_pass),
        "route_or_surface": (
            "/lineage-comparison-lab (dedicated frontend route) + "
            "LineageComparisonLab component + CTA from Judge Cockpit Home "
            "(golden demo run panel and Direct CTAs tile) + link from "
            "Operations Cockpit (page variant) + link from Provider Decision "
            "Intelligence (page variant) + link from Judge Evidence Pack "
            "(page variant)"
        ),
        "lab_id": "lineage_comparison_lab_ps034_" + manifest.get("run_id", ""),
        "lab_version": lab_version_const or "",
        "run_id": manifest.get("run_id"),
        "campaign_id": manifest.get("campaign_id"),
        "archive_uri": manifest.get("archive_uri"),
        "archive_sha256": manifest.get("archive_sha256"),
        "rehydrate_source": "b2_rehydrated",
        "provider_calls_during_rehydrate": 0,
        "no_live_provider_call_during_rehydrate": True,
        "public_deployment_pending": bool(public_deployment_pending),
        "lineage_comparison_surface_verified": lineage_comparison_surface_verified,
        "lab_identity_visible": lab_identity_visible,
        "lineage_summary_visible": lineage_summary_visible,
        "variant_family_tree_verified": variant_family_tree_verified,
        "manifest_diff_verified": manifest_diff_verified,
        "model_audition_board_visible": model_audition_board_visible,
        "provider_swap_rerun_planner_visible": provider_swap_rerun_planner_visible,
        "comparison_readiness_checklist_visible": comparison_readiness_checklist_visible,
        "designer_marketer_interpretation_visible": designer_marketer_interpretation_visible,
        "action_rail_verified": action_rail_verified,
        "truth_boundary_present": truth_boundary_present,
        "limitations_present": limitations_present,
        "only_one_verified_run_disclosed": bool(
            check_only_one_run_line(constants_text)[0]
        ),
        "no_provider_swap_rerun_claim": bool(
            check_no_provider_swap_line(constants_text)[0]
            and no_lineage_overclaim
        ),
        "no_second_variant_claim_without_evidence": bool(no_lineage_overclaim),
        "no_model_score_claim_without_evidence": bool(no_lineage_overclaim),
        "no_winner_claim_without_evidence": bool(no_lineage_overclaim),
        "no_actual_spend_claim_without_evidence": bool(no_lineage_overclaim),
        "no_actual_latency_claim_without_evidence": bool(no_lineage_overclaim),
        "source_ps021_evidence": rel(PS021_EVIDENCE),
        "source_ps024_manifest": rel(MANIFEST),
        "source_ps025_evidence": rel(PS025_EVIDENCE),
        "source_ps026_evidence": rel(PS026_EVIDENCE),
        "source_ps027_evidence": rel(PS027_EVIDENCE),
        "source_ps028_evidence": rel(PS028_EVIDENCE),
        "source_ps029_evidence": rel(PS029_EVIDENCE),
        "source_ps030_evidence": rel(PS030_EVIDENCE),
        "source_ps031_evidence": rel(PS031_EVIDENCE),
        "source_ps032_evidence": rel(PS032_EVIDENCE),
        "source_ps033_evidence": rel(PS033_EVIDENCE),
        "source_ps031a_roadmap_correction": rel(PS031A_ROADMAP),
        "source_implementation_roadmap": rel(ROADMAP),
        "frontend_surface_verified": lineage_comparison_surface_verified,
        "api_surface_verified": api_surface_verified,
        "no_provider_call": no_provider_call,
        "no_broad_b2_read": no_broad_b2_read,
        "no_raw_media_byte_claim": no_raw_media_byte_claim,
        "no_fake_failure_claim": no_fake_failure_claim,
        "no_forbidden_authenticity": no_forbidden_authenticity,
        "no_prior_slice_evidence_modified": bool(prior_clean_ok),
        "checked_at": _utc_now_iso(),
        "api_transport": "testclient",
        "checks": detail,
    }

    if opts.write_evidence:
        sl.write_json_atomic(EVIDENCE_OUT, evidence)
        print(f"evidence: {rel(EVIDENCE_OUT)}")

    if not ps033_ok:
        print("--- PS-033 prior accepted regression contract not satisfied ---")
        for problem in ps033_problems:
            print(f"    - {problem}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(run())
