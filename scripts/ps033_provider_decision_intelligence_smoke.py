#!/usr/bin/env python3
"""PS-033 Provider Decision Intelligence -- smoke / validation script.

PS-034B retrofit: this smoke defaults to safe local / check-only
behavior. It does not recursively execute prior slice smokes, does
not run the frontend toolchain, does not use Git index hiding, does
not snapshot/restore prior evidence, and does not self-unlink its
evidence file. Evidence is written only when ``--write-evidence`` is
passed.

    python scripts/ps033_provider_decision_intelligence_smoke.py --local --check-only

It statically validates the PS033 surface without starting a
browser, without calling any provider, without reading any B2 object,
and without enabling broad durable reads.

Truth boundary: this script validates that the PS033 surface
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
PS032_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "ps-032" / "operations-cockpit-flight-recorder-v2-smoke.json"
ROADMAP = REPO_ROOT / "docs" / "roadmap" / "proofstudio-winning-implementation-roadmap-2026-06-29.md"
PS031A_ROADMAP = REPO_ROOT / "docs" / "roadmap" / "ps-031a-hardened-product-modules-correction.md"
PROVIDER_INVENTORY = REPO_ROOT / "docs" / "submission" / "provider-model-inventory.md"
PS005_PROOF = REPO_ROOT / "docs" / "ps-005-pollinations-fallback-proof.md"
PS006_PROOF = REPO_ROOT / "docs" / "ps-006-provider-router-core-proof.md"

# PS-033 changed / added files.
PDI_CONST = REPO_ROOT / "apps" / "web" / "src" / "providerDecisionIntelligence.ts"
PDI_COMPONENT = REPO_ROOT / "apps" / "web" / "src" / "ProviderDecisionIntelligence.tsx"
HOMEPAGE = REPO_ROOT / "apps" / "web" / "src" / "JudgeCockpitHome.tsx"
APP_TSX = REPO_ROOT / "apps" / "web" / "src" / "App.tsx"
PACK_COMPONENT = REPO_ROOT / "apps" / "web" / "src" / "JudgeEvidencePack.tsx"
OPERATIONS_COMPONENT = REPO_ROOT / "apps" / "web" / "src" / "OperationsCockpit.tsx"
FAILURE_TIMELINE_COMPONENT = REPO_ROOT / "apps" / "web" / "src" / "FailureAsProofTimeline.tsx"
B2_REHYDRATE_COMPONENT = REPO_ROOT / "apps" / "web" / "src" / "B2RehydrateComparison.tsx"
MANIFEST_PANEL = REPO_ROOT / "apps" / "web" / "src" / "ManifestVerificationPanel.tsx"
B2_EXPLORER = REPO_ROOT / "apps" / "web" / "src" / "B2EvidenceExplorer.tsx"
GENBLAZE_GRAPH = REPO_ROOT / "apps" / "web" / "src" / "GenblazePipelineGraph.tsx"
PUBLIC_PASSPORT = REPO_ROOT / "apps" / "web" / "src" / "PublicPassportPage.tsx"
STYLES = REPO_ROOT / "apps" / "web" / "src" / "styles.css"
PROOF_DOC = REPO_ROOT / "docs" / "ps-033-provider-decision-intelligence-proof.md"

PS032_SMOKE = REPO_ROOT / "scripts" / "ps032_operations_cockpit_flight_recorder_smoke.py"
PS031_SMOKE = REPO_ROOT / "scripts" / "ps031_export_campaign_pack_v2_smoke.py"
PS030_SMOKE = REPO_ROOT / "scripts" / "ps030_failure_as_proof_timeline_smoke.py"
PS029_SMOKE = REPO_ROOT / "scripts" / "ps029_b2_rehydrate_comparison_smoke.py"
PS028_SMOKE = REPO_ROOT / "scripts" / "ps028_manifest_verification_panel_smoke.py"
PS027_SMOKE = REPO_ROOT / "scripts" / "ps027_genblaze_pipeline_graph_smoke.py"
PS026_SMOKE = REPO_ROOT / "scripts" / "ps026_b2_evidence_explorer_smoke.py"
PS025_SMOKE = REPO_ROOT / "scripts" / "ps025_public_durable_passport_unlock_smoke.py"
PS024_SMOKE = REPO_ROOT / "scripts" / "ps024_golden_demo_run_pinning_smoke.py"
PS023_SMOKE = REPO_ROOT / "scripts" / "ps023_judge_cockpit_home_smoke.py"

EVIDENCE_OUT = REPO_ROOT / "docs" / "evidence" / "ps-033" / "provider-decision-intelligence-smoke.json"

# Files scanned for secrets and forbidden claims. The scanner script itself is
# intentionally excluded (same convention as PS-023 through PS-032 smokes).
SCAN_FILES: tuple[Path, ...] = (
    PDI_CONST,
    PDI_COMPONENT,
    HOMEPAGE,
    APP_TSX,
    PACK_COMPONENT,
    OPERATIONS_COMPONENT,
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
    PDI_CONST,
    PDI_COMPONENT,
    HOMEPAGE,
    APP_TSX,
    PACK_COMPONENT,
    OPERATIONS_COMPONENT,
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

# Forbidden affirmative overclaims for actual spend / latency / quota /
# production no-key. Matched outside a non-claim context.
SPEND_LATENCY_QUOTA_OVERCLAIMS: tuple[str, ...] = (
    "actual spend for the golden run was",
    "measured latency for the golden run is",
    "measured cost for the golden run is",
    "quota status for the golden run is",
    "quota remaining for the golden run is",
    "token usage for the golden run is",
    "production no-key generation is validated",
    "no-key generation works in production",
    "no-key generation ran for the golden run",
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
    r"not captured|not claimed|not validated|not verified|not equivalent",
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

# Spec-required truth classes.
REQUIRED_TRUTH_CLASSES: tuple[str, ...] = (
    "checked_in_evidence",
    "documented_provider_option",
    "router_policy",
    "fallback_policy",
    "cost_policy_estimate",
    "not_captured_in_evidence",
    "public_deployment_pending",
)

# Spec-required budget modes.
REQUIRED_BUDGET_MODES: tuple[str, ...] = (
    "free_safe",
    "balanced",
    "quality_max",
    "emergency_no_key",
)

# Spec-required fallback policy conditions.
REQUIRED_FALLBACK_CONDITIONS: tuple[str, ...] = (
    "key missing",
    "quota exhausted",
    "provider timeout",
    "provider unavailable",
    "moderation",
    "paid provider skipped",
    "fallback to no-key",
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
# Constant extraction from providerDecisionIntelligence.ts
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
    if not PDI_COMPONENT.exists():
        problems.append(f"missing component {rel(PDI_COMPONENT)}")
    return (not problems, problems)


def check_data_module_exists() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not PDI_CONST.exists():
        problems.append(f"missing constants module {rel(PDI_CONST)}")
    return (not problems, problems)


def check_route_exists() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not APP_TSX.exists():
        return False, [f"missing {rel(APP_TSX)}"]
    text = read_text(APP_TSX)
    if "isProviderDecisionIntelligencePath" not in text:
        problems.append(
            "App.tsx does not register an isProviderDecisionIntelligencePath helper"
        )
    if "/provider-decision-intelligence" not in text:
        problems.append(
            "App.tsx does not reference the /provider-decision-intelligence path"
        )
    if "ProviderDecisionIntelligence" not in text:
        problems.append(
            "App.tsx does not render the ProviderDecisionIntelligence component"
        )
    return (not problems, problems)


def check_judge_links_surface() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not HOMEPAGE.exists():
        return False, [f"missing {rel(HOMEPAGE)}"]
    text = read_text(HOMEPAGE)
    if "/provider-decision-intelligence" not in text:
        problems.append("homepage does not link to /provider-decision-intelligence")
    if "Open Provider Decision Intelligence" not in text:
        problems.append(
            "homepage does not surface a Provider Decision Intelligence CTA label"
        )
    return (not problems, problems)


def check_operations_links_surface() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not OPERATIONS_COMPONENT.exists():
        return False, [f"missing {rel(OPERATIONS_COMPONENT)}"]
    text = read_text(OPERATIONS_COMPONENT)
    if "/provider-decision-intelligence" not in text:
        problems.append(
            "Operations Cockpit does not link to /provider-decision-intelligence"
        )
    if "Open Provider Decision Intelligence" not in text:
        problems.append(
            "Operations Cockpit does not surface a Provider Decision Intelligence CTA"
        )
    return (not problems, problems)


def check_pack_links_surface() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not PACK_COMPONENT.exists():
        return False, [f"missing {rel(PACK_COMPONENT)}"]
    text = read_text(PACK_COMPONENT)
    if "/provider-decision-intelligence" not in text:
        problems.append(
            "Judge Evidence Pack does not link to /provider-decision-intelligence"
        )
    if "Open Provider Decision Intelligence" not in text:
        problems.append(
            "Judge Evidence Pack does not surface a Provider Decision Intelligence CTA"
        )
    return (not problems, problems)


def check_surface_links() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not PDI_COMPONENT.exists():
        return False, [f"missing {rel(PDI_COMPONENT)}"]
    comp_text = read_text(PDI_COMPONENT)
    if not PDI_CONST.exists():
        return False, [f"missing {rel(PDI_CONST)}"]
    const_text = read_text(PDI_CONST)
    for href, label in (
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
        and '"/passport/" + PROVIDER_DECISION_INTELLIGENCE_RUN_ID' not in comp_text
    ):
        problems.append(
            "surface does not link to the golden passport via " + golden_href
        )
    if 'href="/"' not in comp_text:
        problems.append("surface does not link back to / (Judge Cockpit Home)")
    return (not problems, problems)


def check_decision_identity_visible(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not PDI_COMPONENT.exists():
        return False, problems
    comp_text = read_text(PDI_COMPONENT)
    for required in (
        "Provider Decision Intelligence",
        "Why This Provider",
        "PS-033",
    ):
        if required not in comp_text:
            problems.append(
                f"decision identity missing label {required!r}"
            )
    for const_name in (
        "PROVIDER_DECISION_INTELLIGENCE_INTELLIGENCE_ID",
        "PROVIDER_DECISION_INTELLIGENCE_VERSION",
        "PROVIDER_DECISION_INTELLIGENCE_RUN_ID",
        "PROVIDER_DECISION_INTELLIGENCE_CAMPAIGN_ID",
        "PROVIDER_DECISION_INTELLIGENCE_PUBLIC_DEPLOYMENT_PENDING",
    ):
        if const_name not in constants_text:
            problems.append(
                f"providerDecisionIntelligence.ts missing identity const {const_name!r}"
            )
    if "public deployment" not in comp_text.lower():
        problems.append(
            "decision identity does not surface 'public deployment pending'"
        )
    return (not problems, problems)


def check_decision_summary_visible(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if "PROVIDER_DECISION_INTELLIGENCE_DECISION_SUMMARY" not in constants_text:
        problems.append(
            "providerDecisionIntelligence.ts does not declare "
            "PROVIDER_DECISION_INTELLIGENCE_DECISION_SUMMARY"
        )
    if "PROVIDER_DECISION_INTELLIGENCE_SELECTED_ROUTE_SUMMARY" not in constants_text:
        problems.append(
            "providerDecisionIntelligence.ts does not declare a selected route summary"
        )
    if not PDI_COMPONENT.exists():
        return False, problems
    comp_text = read_text(PDI_COMPONENT)
    if "Decision Summary" not in comp_text:
        problems.append("component does not render the Decision Summary heading")
    return (not problems, problems)


def check_golden_values_in_data(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    for const_name in (
        "PROVIDER_DECISION_INTELLIGENCE_ARCHIVE_URI",
        "PROVIDER_DECISION_INTELLIGENCE_ARCHIVE_SHA256",
        "PROVIDER_DECISION_INTELLIGENCE_REHYDRATE_SOURCE",
        "PROVIDER_DECISION_INTELLIGENCE_PROVIDER_CALLS_DURING_REHYDRATE",
        "PROVIDER_DECISION_INTELLIGENCE_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE",
    ):
        if const_name not in constants_text:
            problems.append(
                f"providerDecisionIntelligence.ts missing golden const {const_name!r}"
            )
    return (not problems, problems)


def check_provider_option_matrix(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if "PROVIDER_DECISION_INTELLIGENCE_PROVIDER_OPTIONS" not in constants_text:
        problems.append(
            "providerDecisionIntelligence.ts does not declare "
            "PROVIDER_DECISION_INTELLIGENCE_PROVIDER_OPTIONS"
        )
    if not PDI_COMPONENT.exists():
        return False, problems
    comp_text = read_text(PDI_COMPONENT)
    if "Provider Option Matrix" not in comp_text:
        problems.append(
            "component does not render the Provider Option Matrix heading"
        )
    # At least one documented provider option must be present.
    if "Cloudflare Workers AI" not in constants_text:
        problems.append("provider options missing Cloudflare Workers AI")
    if "Pollinations" not in constants_text:
        problems.append("provider options missing Pollinations")
    return (not problems, problems)


def check_option_fields(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    # Each option object must carry all required fields.
    required_fields = (
        "provider:",
        "modelOrRole:",
        "modalityOrOutput:",
        "keyRequirement:",
        "budgetClass:",
        "fallbackRole:",
        "evidenceStatus:",
        "riskNotes:",
        "truthClass:",
    )
    for field in required_fields:
        if field not in constants_text:
            problems.append(f"provider options missing field {field!r}")
    return (not problems, problems)


def check_truth_classes_exist(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    for cls in REQUIRED_TRUTH_CLASSES:
        if cls not in constants_text:
            problems.append(f"truth class missing {cls!r}")
    return (not problems, problems)


def check_budget_modes_exist(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if "PROVIDER_DECISION_INTELLIGENCE_BUDGET_MODES" not in constants_text:
        problems.append(
            "providerDecisionIntelligence.ts does not declare "
            "PROVIDER_DECISION_INTELLIGENCE_BUDGET_MODES"
        )
    if not PDI_COMPONENT.exists():
        return False, problems
    comp_text = read_text(PDI_COMPONENT)
    if "Budget Modes" not in comp_text:
        problems.append("component does not render the Budget Modes heading")
    return (not problems, problems)


def check_required_budget_modes(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    for mode in REQUIRED_BUDGET_MODES:
        # Budget mode keys are declared as label: "<mode>" inside the data.
        if f'label: "{mode}"' not in constants_text and f'"{mode}"' not in constants_text:
            problems.append(f"budget mode missing {mode!r}")
    return (not problems, problems)


def check_budget_modes_policy(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if "routing polic" not in constants_text.lower():
        problems.append(
            "budget modes are not labeled as routing policy (not live billing)"
        )
    if "policy" not in constants_text.lower():
        problems.append("budget modes do not mention policy")
    if not PDI_COMPONENT.exists():
        return False, problems
    comp_text = read_text(PDI_COMPONENT)
    if "routing polic" not in comp_text.lower():
        problems.append(
            "component does not label budget modes as routing policy"
        )
    return (not problems, problems)


def check_why_this_provider(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if "PROVIDER_DECISION_INTELLIGENCE_WHY_THIS_PROVIDER" not in constants_text:
        problems.append(
            "providerDecisionIntelligence.ts does not declare "
            "PROVIDER_DECISION_INTELLIGENCE_WHY_THIS_PROVIDER"
        )
    for fragment in (
        "whyAcceptable",
        "whatEvidenceBacksIt",
        "whatIsNotKnown",
        "howSystemBehavesIfKeyUnavailable",
        "howEmergencyNoKeyDiffersFromQuality",
    ):
        if fragment not in constants_text:
            problems.append(f"why-this-provider missing field {fragment!r}")
    if not PDI_COMPONENT.exists():
        return False, problems
    comp_text = read_text(PDI_COMPONENT)
    if "Why This Provider" not in comp_text:
        problems.append("component does not render the Why This Provider heading")
    return (not problems, problems)


def check_cost_time_ledger(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if "PROVIDER_DECISION_INTELLIGENCE_COST_TIME_LEDGER" not in constants_text:
        problems.append(
            "providerDecisionIntelligence.ts does not declare "
            "PROVIDER_DECISION_INTELLIGENCE_COST_TIME_LEDGER"
        )
    for field in (
        "provider:",
        "modelOrRole:",
        "attemptCount:",
        "fallbackCount:",
        "providerCallsDuringRehydrate:",
        "estimatedCostClass:",
        "measuredCost:",
        "measuredLatency:",
        "evidenceSource:",
        "truthClass:",
    ):
        if field not in constants_text:
            problems.append(f"cost/time ledger missing field {field!r}")
    if not PDI_COMPONENT.exists():
        return False, problems
    comp_text = read_text(PDI_COMPONENT)
    if "Cost and Time Ledger" not in comp_text:
        problems.append("component does not render the Cost and Time Ledger heading")
    return (not problems, problems)


def check_measured_cost_not_invented(constants_text: str) -> tuple[bool, list[str]]:
    """measured_cost is not invented -- it is the 'not captured' literal or a
    clearly policy/non-numeric class, never an actual currency / numeric
    spend."""
    problems: list[str] = []
    if "not captured in checked-in evidence" not in constants_text:
        problems.append(
            "cost/time ledger does not use the 'not captured in checked-in "
            "evidence' label for measured_cost"
        )
    # measured_cost / measured_latency assignments inside ledger rows: pull
    # every `measuredCost:` value and ensure none is a numeric currency.
    invented = re.findall(
        r'measuredCost:\s*"[^"]*(?:\$|USD|EUR|\d+\.\d{2,}|\d+\s*token)[^"]*"',
        constants_text,
        re.IGNORECASE,
    )
    if invented:
        problems.append(
            f"measured_cost appears invented: {invented[:3]!r}"
        )
    # No bare numeric measured cost (e.g. measuredCost: "12.50").
    bare_numeric = re.findall(
        r'measuredCost:\s*"[\d.,]+\s*(?:ms|s|usd|\$|credits)?"',
        constants_text,
        re.IGNORECASE,
    )
    for hit in bare_numeric:
        if "not captured" in hit.lower():
            continue
        problems.append(f"measured_cost appears numeric: {hit!r}")
    return (not problems, problems)


def check_measured_latency_not_invented(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    invented = re.findall(
        r'measuredLatency:\s*"[^"]*(?:\d+\s*ms|\d+\s*s\b|\d+\.\d+\s*ms)[^"]*"',
        constants_text,
        re.IGNORECASE,
    )
    for hit in invented:
        if "not captured" in hit.lower():
            continue
        problems.append(f"measured_latency appears invented: {hit!r}")
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
        "PROVIDER_DECISION_INTELLIGENCE_PROVIDER_CALLS_DURING_REHYDRATE",
    )
    if const != 0:
        problems.append(
            f"provider_calls_during_rehydrate: frontend constant={const!r}, "
            f"expected 0"
        )
    return (not problems, problems)


def check_emergency_no_key(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if "PROVIDER_DECISION_INTELLIGENCE_EMERGENCY_NO_KEY_MODE" not in constants_text:
        problems.append(
            "providerDecisionIntelligence.ts does not declare "
            "PROVIDER_DECISION_INTELLIGENCE_EMERGENCY_NO_KEY_MODE"
        )
    for fragment in (
        "whenUseful",
        "howProtectsDemosAndOnboarding",
        "qualityTradeoffs",
        "evidenceOrCodeSupport",
        "notVerifiedForGoldenRun",
    ):
        if fragment not in constants_text:
            problems.append(f"emergency no-key missing field {fragment!r}")
    if not PDI_COMPONENT.exists():
        return False, problems
    comp_text = read_text(PDI_COMPONENT)
    if "Emergency No-Key Mode" not in comp_text:
        problems.append(
            "component does not render the Emergency No-Key Mode heading"
        )
    return (not problems, problems)


def check_fallback_policy(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if "PROVIDER_DECISION_INTELLIGENCE_FALLBACK_POLICY" not in constants_text:
        problems.append(
            "providerDecisionIntelligence.ts does not declare "
            "PROVIDER_DECISION_INTELLIGENCE_FALLBACK_POLICY"
        )
    if not PDI_COMPONENT.exists():
        return False, problems
    comp_text = read_text(PDI_COMPONENT)
    if "Provider Failure / Fallback Policy" not in comp_text:
        problems.append(
            "component does not render the Provider Failure / Fallback Policy heading"
        )
    # Each required condition keyword must appear in the data.
    joined = constants_text.lower()
    for condition in REQUIRED_FALLBACK_CONDITIONS:
        if condition not in joined:
            problems.append(f"fallback policy missing condition {condition!r}")
    return (not problems, problems)


def check_designer_marketer(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if (
        "PROVIDER_DECISION_INTELLIGENCE_DESIGNER_MARKETER_INTERPRETATION"
        not in constants_text
    ):
        problems.append(
            "providerDecisionIntelligence.ts does not declare "
            "PROVIDER_DECISION_INTELLIGENCE_DESIGNER_MARKETER_INTERPRETATION"
        )
    for fragment in (
        "bestQualityMode",
        "cheapestSafeMode",
        "emergencyDemoMode",
        "whyProviderChoiceAffectsReview",
        "whyProofMattersForClientHandoff",
        "whenToExportEvidencePack",
    ):
        if fragment not in constants_text:
            problems.append(f"designer/marketer missing field {fragment!r}")
    if not PDI_COMPONENT.exists():
        return False, problems
    comp_text = read_text(PDI_COMPONENT)
    if "Designer / Marketer Interpretation" not in comp_text:
        problems.append(
            "component does not render the Designer / Marketer Interpretation heading"
        )
    return (not problems, problems)


def check_action_rail(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if "PROVIDER_DECISION_INTELLIGENCE_ACTION_ROUTES" not in constants_text:
        problems.append(
            "providerDecisionIntelligence.ts does not declare "
            "PROVIDER_DECISION_INTELLIGENCE_ACTION_ROUTES"
        )
    for href in (
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
                f"PROVIDER_DECISION_INTELLIGENCE_ACTION_ROUTES missing href {href!r}"
            )
    if '"/passport/" + PROVIDER_DECISION_INTELLIGENCE_RUN_ID' not in constants_text:
        problems.append(
            "action routes do not build the golden passport href"
        )
    if not PDI_COMPONENT.exists():
        return False, problems
    comp_text = read_text(PDI_COMPONENT)
    if "Action Rail" not in comp_text:
        problems.append("component does not render the Action Rail heading")
    return (not problems, problems)


def check_truth_boundary(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if "PROVIDER_DECISION_INTELLIGENCE_TRUTH_BOUNDARY" not in constants_text:
        problems.append(
            "providerDecisionIntelligence.ts does not declare "
            "PROVIDER_DECISION_INTELLIGENCE_TRUTH_BOUNDARY"
        )
        return (not problems, problems)
    missing = [
        t for t in TRUTH_BOUNDARY_TERMS if t.lower() not in constants_text.lower()
    ]
    if missing:
        problems.append(
            f"providerDecisionIntelligence.ts truth boundary missing term {missing[0]!r}"
        )
    if "PROVIDER_DECISION_INTELLIGENCE_CLAIM_BOUNDARY_ALLOWED" not in constants_text:
        problems.append("missing the allowed claim boundary")
    if "PROVIDER_DECISION_INTELLIGENCE_CLAIM_BOUNDARY_FORBIDDEN" not in constants_text:
        problems.append("missing the forbidden claim boundary")
    if not PDI_COMPONENT.exists():
        return False, problems
    comp_text = read_text(PDI_COMPONENT)
    if "Truth Boundary" not in comp_text:
        problems.append("component does not render the Truth Boundary heading")
    return (not problems, problems)


def check_limitations(constants_text: str) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if "PROVIDER_DECISION_INTELLIGENCE_LIMITATIONS" not in constants_text:
        problems.append(
            "providerDecisionIntelligence.ts does not declare "
            "PROVIDER_DECISION_INTELLIGENCE_LIMITATIONS"
        )
    for marker in (
        "no live provider call",
        "no broad b2 read",
        "no live pricing api",
        "no measured billing",
        "no measured latency",
        "no quota inspection",
        "public deployment pending",
        "checked-in evidence and documented policy only",
        "no invented provider failure events",
    ):
        if marker.lower() not in constants_text.lower():
            problems.append(f"limitations missing marker {marker!r}")
    if not PDI_COMPONENT.exists():
        return False, problems
    comp_text = read_text(PDI_COMPONENT)
    if "Limitations" not in comp_text:
        problems.append("component does not render the Limitations heading")
    return (not problems, problems)


def check_sections_visible() -> tuple[bool, list[str]]:
    """All required intelligence sections are visible in the component."""
    problems: list[str] = []
    if not PDI_COMPONENT.exists():
        return False, [f"missing {rel(PDI_COMPONENT)}"]
    comp_text = read_text(PDI_COMPONENT)
    for section in (
        "Provider Decision Identity",
        "Decision Summary",
        "Provider Option Matrix",
        "Budget Modes",
        "Why This Provider",
        "Cost and Time Ledger",
        "Emergency No-Key Mode",
        "Provider Failure / Fallback Policy",
        "Designer / Marketer Interpretation",
        "Action Rail",
        "Truth Boundary",
        "Limitations",
    ):
        if section not in comp_text:
            problems.append(
                f"ProviderDecisionIntelligence missing section heading {section!r}"
            )
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
    const = _extract_string_const(
        constants_text, "PROVIDER_DECISION_INTELLIGENCE_RUN_ID"
    )
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
        constants_text, "PROVIDER_DECISION_INTELLIGENCE_CAMPAIGN_ID"
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
        constants_text, "PROVIDER_DECISION_INTELLIGENCE_ARCHIVE_URI"
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
        constants_text, "PROVIDER_DECISION_INTELLIGENCE_ARCHIVE_SHA256"
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
        constants_text, "PROVIDER_DECISION_INTELLIGENCE_REHYDRATE_SOURCE"
    )
    if const != "b2_rehydrated":
        problems.append(
            f"rehydrate_source: frontend constant={const!r}, "
            f"expected 'b2_rehydrated'"
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
        "PROVIDER_DECISION_INTELLIGENCE_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE",
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

    arbitrary_run_id = "run_ps033_must_still_404_0123456789abcdef"
    status = _get_passport_status(arbitrary_run_id)
    if status != 404:
        problems.append(
            f"arbitrary run id returned HTTP {status}, expected 404 "
            f"(broad public durable read must stay blocked)"
        )

    return (not problems, problems)


def check_no_fake_failure_claim() -> tuple[bool, list[str]]:
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


def check_no_spend_latency_quota_claim() -> tuple[bool, list[str]]:
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
            for phrase in SPEND_LATENCY_QUOTA_OVERCLAIMS:
                if phrase in line_lower:
                    hit = True
                    break
            if not hit:
                continue
            if _line_has_nonclaim_context(lines, i):
                continue
            problems.append(
                f"{rel(path)}:{i + 1}: spend/latency/quota/no-key overclaim "
                f"with no non-claim context -> {line.strip()!r}"
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
    golden_run_id = manifest.get("run_id")
    passport = _get_golden_passport_json(golden_run_id)
    if not passport:
        status = _get_passport_status(golden_run_id)
        return False, [
            f"GET /runs/{golden_run_id}/passport did not resolve "
            f"(status={status})"
        ]
    return True, []


def check_provider_inventory_consistent() -> tuple[bool, list[str]]:
    """Provider options are limited to providers backed by the documented
    inventory / router proof. No invented provider."""
    problems: list[str] = []
    if not PROVIDER_INVENTORY.exists():
        problems.append(f"missing {rel(PROVIDER_INVENTORY)}")
        return (not problems, problems)
    inventory_text = read_text(PROVIDER_INVENTORY)
    constants_text = read_text(PDI_CONST) if PDI_CONST.exists() else ""
    documented = (
        "Cloudflare Workers AI",
        "Pollinations",
        "GMI Cloud",
        "Luma",
        "ElevenLabs",
        "OpenAI",
        "Runway",
        "NVIDIA NIM",
        "Gemini",
        "Imagen",
    )
    # Each provider name token surfaced in the option matrix must appear in
    # the documented inventory. We check the matrix provider names against the
    # inventory. (The data module surfaces provider tokens verbatim.)
    for token in documented:
        # Only require tokens actually used by the data to be in inventory; we
        # check the reverse below (every used provider token must be in the
        # inventory or be a generic label).
        pass
    # Reverse check: pull provider: "<name>" tokens from the data and ensure
    # each is either documented or a generic label (e.g. combination row).
    used = re.findall(r'provider:\s*"([^"]+)"', constants_text)
    generic_fragments = (
        "documented ",
        "not captured",
        "optional later",
    )
    for name in used:
        if any(g in name.lower() for g in generic_fragments):
            continue
        # The combined "ElevenLabs / OpenAI / Runway / Stability Audio /
        # NVIDIA NIM" row contains multiple tokens; check each documented
        # token it references is in the inventory.
        matched_any = False
        for token in documented:
            if token in name:
                if token in inventory_text:
                    matched_any = True
                else:
                    problems.append(
                        f"provider option {name!r} references {token!r} which "
                        f"is not in the documented inventory"
                    )
        if not matched_any:
            # Allow provider tokens that are documented elsewhere (e.g. router
            # proof) -- but flag unknown brand names not present anywhere.
            if name not in inventory_text:
                problems.append(
                    f"provider option {name!r} is not backed by the documented "
                    f"inventory"
                )
    return (not problems, problems)

# ---------------------------------------------------------------------------
# PS-034B retrofitted runner (safe local / check-only mode)
# ---------------------------------------------------------------------------

def check_no_prior_slice_evidence_modified() -> tuple[bool, list[str]]:
    problems = sl.prior_evidence_dirty_problems(
        own_slice_prefix="docs/evidence/ps-033/",
        slice_label="PS-033",
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
        PS032_EVIDENCE,
        PROVIDER_INVENTORY,
        PS005_PROOF,
        PS006_PROOF,
    ):
        if not p.exists():
            missing_inputs.append(rel(p))
    if missing_inputs:
        print("PS033 smoke: MISSING INPUT FILES")
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
    }
    constants_text = read_text(PDI_CONST) if PDI_CONST.exists() else ""

    checks: list[tuple[str, tuple[bool, list[str]]]] = [
        ("component_exists", check_component_exists()),
        ("data_module_exists", check_data_module_exists()),
        ("route_exists", check_route_exists()),
        ("judge_links_surface", check_judge_links_surface()),
        ("operations_links_surface", check_operations_links_surface()),
        ("pack_links_surface", check_pack_links_surface()),
        ("surface_links_surfaces", check_surface_links()),
        ("decision_identity_visible", check_decision_identity_visible(constants_text)),
        ("decision_summary_visible", check_decision_summary_visible(constants_text)),
        ("golden_values_in_data", check_golden_values_in_data(constants_text)),
        ("provider_option_matrix", check_provider_option_matrix(constants_text)),
        ("option_fields", check_option_fields(constants_text)),
        ("truth_classes_exist", check_truth_classes_exist(constants_text)),
        ("budget_modes_exist", check_budget_modes_exist(constants_text)),
        ("required_budget_modes", check_required_budget_modes(constants_text)),
        ("budget_modes_policy", check_budget_modes_policy(constants_text)),
        ("why_this_provider", check_why_this_provider(constants_text)),
        ("cost_time_ledger", check_cost_time_ledger(constants_text)),
        ("measured_cost_not_invented", check_measured_cost_not_invented(constants_text)),
        (
            "measured_latency_not_invented",
            check_measured_latency_not_invented(constants_text),
        ),
        ("provider_calls_zero", check_provider_calls_zero(constants_text)),
        ("emergency_no_key", check_emergency_no_key(constants_text)),
        ("fallback_policy", check_fallback_policy(constants_text)),
        ("designer_marketer", check_designer_marketer(constants_text)),
        ("action_rail", check_action_rail(constants_text)),
        ("truth_boundary", check_truth_boundary(constants_text)),
        ("limitations", check_limitations(constants_text)),
        ("sections_visible", check_sections_visible()),
        ("source_evidence_present", check_source_evidence_present(constants_text)),
        ("run_id_matches", check_run_id_matches(constants_text)),
        ("campaign_id_matches", check_campaign_id_matches(constants_text)),
        ("archive_uri_match", check_archive_uri_match(constants_text)),
        ("archive_sha256_match", check_archive_sha256_match(constants_text)),
        ("rehydrate_source", check_rehydrate_source(constants_text)),
        ("no_live_provider_call", check_no_live_provider_call(constants_text)),
        ("provider_inventory_consistent", check_provider_inventory_consistent()),
        ("no_provider_call", check_no_provider_call()),
        ("no_broad_b2_read", check_no_broad_b2_read()),
        ("no_fake_failure_claim", check_no_fake_failure_claim()),
        ("no_raw_media_byte_claim", check_no_raw_media_byte_claim()),
        (
            "no_spend_latency_quota_claim",
            check_no_spend_latency_quota_claim(),
        ),
        ("secret_scan", check_secrets()),
        ("forbidden_claims", check_forbidden_claims()),
        ("api_resolves_golden", check_api_resolves_golden(manifest)),
    ]

    all_pass, detail = sl.run_contract_checks("PS-033 Provider Decision Intelligence", checks)

    if opts.write_evidence:
        evidence = {
            "ok": bool(all_pass),
            "route_or_surface": (
                "/provider-decision-intelligence (dedicated frontend route) + "
                "ProviderDecisionIntelligence component + CTA from Judge Cockpit "
                "Home (golden demo run panel and Direct CTAs tile) + link from "
                "Operations Cockpit (page variant) + link from Judge Evidence "
                "Pack (page variant)"
            ),
            "intelligence_id": (
                "provider_decision_intelligence_ps033_" + manifest.get("run_id", "")
            ),
            "intelligence_version": intelligence_version_const or "",
            "run_id": manifest.get("run_id"),
            "campaign_id": manifest.get("campaign_id"),
            "archive_uri": manifest.get("archive_uri"),
            "archive_sha256": manifest.get("archive_sha256"),
            "rehydrate_source": "b2_rehydrated",
            "provider_calls_during_rehydrate": 0,
            "no_live_provider_call_during_rehydrate": True,
            "public_deployment_pending": bool(public_deployment_pending),
            "provider_decision_surface_verified": provider_decision_surface_verified,
            "decision_identity_visible": decision_identity_visible,
            "decision_summary_visible": decision_summary_visible,
            "provider_option_matrix_verified": provider_option_matrix_verified,
            "budget_modes_verified": budget_modes_verified,
            "why_this_provider_visible": why_this_provider_visible,
            "cost_time_ledger_visible": cost_time_ledger_visible,
            "emergency_no_key_mode_visible": emergency_no_key_mode_visible,
            "fallback_policy_visible": fallback_policy_visible,
            "designer_marketer_interpretation_visible": designer_marketer_interpretation_visible,
            "action_rail_verified": action_rail_verified,
            "truth_boundary_present": truth_boundary_present,
            "limitations_present": limitations_present,
            "cost_claims_are_policy_not_billing": bool(budget_modes_verified),
            "no_actual_spend_claim_without_evidence": bool(
                no_spend_latency_quota_claim
            ),
            "no_actual_latency_claim_without_evidence": bool(
                check_measured_latency_not_invented(constants_text)[0]
                and no_spend_latency_quota_claim
            ),
            "no_quota_status_claim_without_evidence": bool(
                no_spend_latency_quota_claim
            ),
            "no_real_provider_failure_claim_without_evidence": bool(
                no_fake_failure_claim
            ),
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
            "source_ps031a_roadmap_correction": rel(PS031A_ROADMAP),
            "source_implementation_roadmap": rel(ROADMAP),
            "source_provider_inventory": rel(PROVIDER_INVENTORY),
            "source_ps005_proof": rel(PS005_PROOF),
            "source_ps006_proof": rel(PS006_PROOF),
            "frontend_surface_verified": provider_decision_surface_verified,
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
        sl.write_json_atomic(EVIDENCE_OUT, evidence)
        print(f"evidence: {rel(EVIDENCE_OUT)}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(run())
