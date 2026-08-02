#!/usr/bin/env python3
"""PS-030 Failure-as-Proof Timeline -- smoke / validation script.

PS-034B retrofit: this smoke defaults to safe local / check-only
behavior. It does not recursively execute prior slice smokes, does
not run the frontend toolchain, does not use Git index hiding, does
not snapshot/restore prior evidence, and does not self-unlink its
evidence file. Evidence is written only when ``--write-evidence`` is
passed.

    python scripts/ps030_failure_as_proof_timeline_smoke.py --local --check-only

It statically validates the PS030 surface without starting a
browser, without calling any provider, without reading any B2 object,
and without enabling broad durable reads.

Truth boundary: this script validates that the PS030 surface
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
ROADMAP = REPO_ROOT / "docs" / "roadmap" / "proofstudio-winning-implementation-roadmap-2026-06-29.md"

# PS-030 changed / added files.
FAILURE_TIMELINE_CONST = REPO_ROOT / "apps" / "web" / "src" / "failureAsProofTimeline.ts"
FAILURE_TIMELINE_COMPONENT = REPO_ROOT / "apps" / "web" / "src" / "FailureAsProofTimeline.tsx"
HOMEPAGE = REPO_ROOT / "apps" / "web" / "src" / "JudgeCockpitHome.tsx"
APP_TSX = REPO_ROOT / "apps" / "web" / "src" / "App.tsx"
B2_REHYDRATE_COMPONENT = REPO_ROOT / "apps" / "web" / "src" / "B2RehydrateComparison.tsx"
MANIFEST_PANEL = REPO_ROOT / "apps" / "web" / "src" / "ManifestVerificationPanel.tsx"
B2_EXPLORER = REPO_ROOT / "apps" / "web" / "src" / "B2EvidenceExplorer.tsx"
GENBLAZE_GRAPH = REPO_ROOT / "apps" / "web" / "src" / "GenblazePipelineGraph.tsx"
PUBLIC_PASSPORT = REPO_ROOT / "apps" / "web" / "src" / "PublicPassportPage.tsx"
STYLES = REPO_ROOT / "apps" / "web" / "src" / "styles.css"
PROOF_DOC = REPO_ROOT / "docs" / "ps-030-failure-as-proof-timeline-proof.md"

PS029_SMOKE = REPO_ROOT / "scripts" / "ps029_b2_rehydrate_comparison_smoke.py"
PS028_SMOKE = REPO_ROOT / "scripts" / "ps028_manifest_verification_panel_smoke.py"
PS027_SMOKE = REPO_ROOT / "scripts" / "ps027_genblaze_pipeline_graph_smoke.py"
PS026_SMOKE = REPO_ROOT / "scripts" / "ps026_b2_evidence_explorer_smoke.py"
PS025_SMOKE = REPO_ROOT / "scripts" / "ps025_public_durable_passport_unlock_smoke.py"
PS024_SMOKE = REPO_ROOT / "scripts" / "ps024_golden_demo_run_pinning_smoke.py"
PS023_SMOKE = REPO_ROOT / "scripts" / "ps023_judge_cockpit_home_smoke.py"

EVIDENCE_OUT = REPO_ROOT / "docs" / "evidence" / "ps-030" / "failure-as-proof-timeline-smoke.json"

# Files scanned for secrets and forbidden claims. The scanner script itself
# is intentionally excluded: it legitimately contains the detection literals
# (same convention as PS-023 through PS-029 smokes).
SCAN_FILES: tuple[Path, ...] = (
    FAILURE_TIMELINE_CONST,
    FAILURE_TIMELINE_COMPONENT,
    HOMEPAGE,
    APP_TSX,
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
    FAILURE_TIMELINE_CONST,
    FAILURE_TIMELINE_COMPONENT,
    HOMEPAGE,
    APP_TSX,
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
    "the timeline proves semantic truth",
    "the timeline proves media is true",
    "the timeline proves legal authenticity",
    "the timeline proves human authorship",
    "the timeline proves C2PA authenticity",
    "the timeline proves Object Lock",
    "the timeline proves tamper-proof storage",
    "the timeline certifies authenticity",
    "a provider failure occurred during the golden run",
    "a fallback occurred during the golden run",
    "an actual provider outage occurred",
    "a real provider failure is recorded",
    "a real fallback is recorded",
    "the browser fetched and hashed the B2 object",
    "the browser verified the B2 bytes",
    "public deployment is verified",
    "public deployment verified",
    "Object Lock is enabled",
    "tamper-proof storage is enabled",
    "enterprise-grade security",
)

CONTEXT_MARKERS_RE = re.compile(
    r"does not|do not|must not|\bnot\b|non-claim|non-claims|forbidden|"
    r"reject|rejected|avoid|without overclaim|unless actually implemented|"
    r"only inside non-claim|limitation|limitations|no affirmative|"
    r"unavailable|blocked|honestly|no live|no_new|no_fake|pending|planned|"
    r"did not fetch|does not claim|did not claim|without|none claimed|"
    r"would appear|if captured|no actual|no fake",
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


# ---------------------------------------------------------------------------
# Constant extraction from failureAsProofTimeline.ts
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
)

REQUIRED_FIELD_KEYS: tuple[str, ...] = (
    "run_id",
    "campaign_id",
    "archive_uri",
    "archive_sha256",
    "rehydrate_source",
    "provider_calls_during_rehydrate",
    "no_live_provider_call_during_rehydrate",
)

# PS-021 records rehydrate_source under "durable_source"; every other source
# uses the canonical key name.
SOURCE_KEY_OVERRIDES: dict[str, dict[str, str]] = {
    "ps021": {"rehydrate_source": "durable_source"},
}

# Maps the canonical source id to the loaded evidence dict.
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
    }[source_id]


# ---------------------------------------------------------------------------
# Required timeline event keys
# ---------------------------------------------------------------------------

REQUIRED_EVENT_TITLES: tuple[str, ...] = (
    "Golden run identity established",
    "Provider routing / orchestration path recorded",
    "Generation / provenance path captured",
    "B2 archive created",
    "Golden manifest pinned",
    "Public passport contract unlocked locally",
    "B2 Evidence Explorer surface created",
    "Genblaze Pipeline Graph surface created",
    "Manifest Verification Panel confirms consistency",
    "B2 Rehydrate Comparison confirms durable rehydrate without provider rerun",
    "Where captured failures, retries, and fallbacks would appear",
    "Public deployment pending remains explicit",
)


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_surface_exists() -> tuple[bool, list[str]]:
    """PS-030 surface exists as a frontend route + component + CTA."""
    problems: list[str] = []
    if not FAILURE_TIMELINE_COMPONENT.exists():
        problems.append(f"missing component {rel(FAILURE_TIMELINE_COMPONENT)}")
    if not FAILURE_TIMELINE_CONST.exists():
        problems.append(f"missing constants module {rel(FAILURE_TIMELINE_CONST)}")

    if FAILURE_TIMELINE_COMPONENT.exists():
        comp_text = read_text(FAILURE_TIMELINE_COMPONENT)
        for required in (
            "Failure-as-Proof Timeline",
            "Failure-as-Proof",
            "Failure Theater",
            "Archive / Rehydrate Lab foundation",
            "No live provider rerun required for rehydrate",
            "Open B2 Rehydrate Comparison",
            "Open Manifest Verification Panel",
            "Open B2 Evidence Explorer",
            "Open Genblaze Pipeline Graph",
            "Open Golden Passport",
            "Back to Judge Cockpit Home",
        ):
            if required not in comp_text:
                problems.append(
                    f"FailureAsProofTimeline missing reference to {required!r}"
                )
    return (not problems, problems)


def check_route_exists() -> tuple[bool, list[str]]:
    """The /failure-timeline route is registered in App.tsx."""
    problems: list[str] = []
    if not APP_TSX.exists():
        return False, [f"missing {rel(APP_TSX)}"]
    text = read_text(APP_TSX)
    if "isFailureTimelinePath" not in text:
        problems.append(
            "App.tsx does not register an isFailureTimelinePath helper"
        )
    if "/failure-timeline" not in text:
        problems.append(
            "App.tsx does not reference the /failure-timeline path"
        )
    if "FailureAsProofTimeline" not in text:
        problems.append(
            "App.tsx does not render the FailureAsProofTimeline component"
        )
    return (not problems, problems)


def check_judge_links_timeline() -> tuple[bool, list[str]]:
    """The Judge Cockpit links to /failure-timeline."""
    problems: list[str] = []
    if not HOMEPAGE.exists():
        return False, [f"missing {rel(HOMEPAGE)}"]
    text = read_text(HOMEPAGE)
    if "/failure-timeline" not in text:
        problems.append("homepage does not link to /failure-timeline")
    if "Open Failure-as-Proof Timeline" not in text:
        problems.append(
            "homepage does not surface a Failure-as-Proof Timeline CTA label"
        )
    return (not problems, problems)


def check_timeline_links(manifest: dict) -> tuple[bool, list[str]]:
    """The timeline links to rehydrate, manifest, b2, genblaze, passport, home."""
    problems: list[str] = []
    if not FAILURE_TIMELINE_COMPONENT.exists():
        return False, [f"missing {rel(FAILURE_TIMELINE_COMPONENT)}"]
    text = read_text(FAILURE_TIMELINE_COMPONENT)
    if "/b2-rehydrate-comparison" not in text:
        problems.append("timeline does not link to /b2-rehydrate-comparison")
    if "/manifest-verification" not in text:
        problems.append("timeline does not link to /manifest-verification")
    if "/b2-evidence" not in text:
        problems.append("timeline does not link to /b2-evidence")
    if "/genblaze-pipeline" not in text:
        problems.append("timeline does not link to /genblaze-pipeline")
    golden_run_id = manifest.get("run_id")
    if not golden_run_id:
        problems.append("manifest missing run_id")
    elif (
        f"/passport/{golden_run_id}" not in text
        and '"/passport/" + FAILURE_TIMELINE_RUN_ID' not in text
    ):
        problems.append(
            "timeline does not link to the golden passport via "
            "/passport/<golden_run_id>"
        )
    if 'href="/"' not in text:
        problems.append(
            "timeline does not link back to / (Judge Cockpit Home)"
        )
    return (not problems, problems)


def check_sources_present(constants_text: str) -> tuple[bool, list[str]]:
    """All 7 required sources are listed in failureAsProofTimeline.ts."""
    problems: list[str] = []
    for required in (
        "Golden demo manifest",
        "PS-021 B2 durable rehydrate evidence",
        "PS-025 public durable passport evidence",
        "PS-026 B2 Evidence Explorer evidence",
        "PS-027 Genblaze Pipeline Graph evidence",
        "PS-028 Manifest Verification Panel evidence",
        "PS-029 B2 Rehydrate Comparison evidence",
    ):
        if required not in constants_text:
            problems.append(
                f"failureAsProofTimeline.ts missing source {required!r}"
            )
    for path_const in (
        "FAILURE_TIMELINE_SOURCE_PS024_MANIFEST",
        "FAILURE_TIMELINE_SOURCE_PS021_EVIDENCE",
        "FAILURE_TIMELINE_SOURCE_PS025_EVIDENCE",
        "FAILURE_TIMELINE_SOURCE_PS026_EVIDENCE",
        "FAILURE_TIMELINE_SOURCE_PS027_EVIDENCE",
        "FAILURE_TIMELINE_SOURCE_PS028_EVIDENCE",
        "FAILURE_TIMELINE_SOURCE_PS029_EVIDENCE",
    ):
        if path_const not in constants_text:
            problems.append(
                f"failureAsProofTimeline.ts missing constant {path_const!r}"
            )
    return (not problems, problems)


def check_events_present(constants_text: str) -> tuple[bool, list[str]]:
    """All required timeline event titles are listed."""
    problems: list[str] = []
    for title in REQUIRED_EVENT_TITLES:
        if title not in constants_text:
            problems.append(
                f"failureAsProofTimeline.ts missing event title {title!r}"
            )
    return (not problems, problems)


def check_roadmap_referenced(constants_text: str) -> tuple[bool, list[str]]:
    """The implementation roadmap is referenced."""
    problems: list[str] = []
    if "FAILURE_TIMELINE_IMPLEMENTATION_ROADMAP" not in constants_text:
        problems.append(
            "failureAsProofTimeline.ts does not declare "
            "FAILURE_TIMELINE_IMPLEMENTATION_ROADMAP"
        )
    if not ROADMAP.exists():
        problems.append(f"missing roadmap {rel(ROADMAP)}")
    else:
        roadmap_text = read_text(ROADMAP)
        if "PS-030" not in roadmap_text or "Failure-as-Proof" not in roadmap_text:
            problems.append(
                "roadmap does not reference PS-030 / Failure-as-Proof"
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
    const = _extract_string_const(constants_text, "FAILURE_TIMELINE_RUN_ID")
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
    const = _extract_string_const(constants_text, "FAILURE_TIMELINE_CAMPAIGN_ID")
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
    const = _extract_string_const(constants_text, "FAILURE_TIMELINE_ARCHIVE_URI")
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
    const = _extract_string_const(constants_text, "FAILURE_TIMELINE_ARCHIVE_SHA256")
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
        constants_text, "FAILURE_TIMELINE_REHYDRATE_SOURCE"
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
        "FAILURE_TIMELINE_PROVIDER_CALLS_DURING_REHYDRATE",
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
        got = _source_field_value(
            src_id, "no_live_provider_call_during_rehydrate"
        )
        if got is not True:
            problems.append(
                f"no_live_provider_call_during_rehydrate: source "
                f"{src_id}={got!r}, expected True"
            )
    const = _extract_bool_const(
        constants_text,
        "FAILURE_TIMELINE_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE",
    )
    if const is not True:
        problems.append(
            f"no_live_provider_call_during_rehydrate: frontend constant="
            f"{const!r}, expected True"
        )
    return (not problems, problems)


def check_no_provider_rerun_story() -> tuple[bool, list[str]]:
    """The no-provider-rerun story is visible in the component + constants."""
    if not FAILURE_TIMELINE_CONST.exists():
        return False, [f"missing {rel(FAILURE_TIMELINE_CONST)}"]
    const_text = read_text(FAILURE_TIMELINE_CONST)
    if "FAILURE_TIMELINE_NO_PROVIDER_RERUN_STORY" not in const_text:
        return False, [
            "FAILURE_TIMELINE_NO_PROVIDER_RERUN_STORY const is not declared"
        ]
    if "No live provider rerun required for rehydrate" not in read_text(
        FAILURE_TIMELINE_COMPONENT
    ):
        return False, [
            "FailureAsProofTimeline does not render the no-provider-rerun "
            "story heading"
        ]
    if "provider_calls_during_rehydrate = 0" not in const_text:
        return False, [
            "no-provider-rerun story does not cite "
            "provider_calls_during_rehydrate = 0"
        ]
    if "no_live_provider_call_during_rehydrate = true" not in const_text:
        return False, [
            "no-provider-rerun story does not cite "
            "no_live_provider_call_during_rehydrate = true"
        ]
    return True, []


def check_failure_as_proof_visible() -> tuple[bool, list[str]]:
    """The Failure-as-Proof section + required visible language are present."""
    problems: list[str] = []
    const_text = read_text(FAILURE_TIMELINE_CONST) if FAILURE_TIMELINE_CONST.exists() else ""
    comp_text = read_text(FAILURE_TIMELINE_COMPONENT) if FAILURE_TIMELINE_COMPONENT.exists() else ""
    if "FAILURE_TIMELINE_FAILURE_AS_PROOF_EXPLANATION" not in const_text:
        problems.append(
            "FAILURE_TIMELINE_FAILURE_AS_PROOF_EXPLANATION const is not declared"
        )
    if "Failure-as-Proof" not in comp_text:
        problems.append("component does not render the Failure-as-Proof heading")
    # Required visible language. The literal lives in the constants module
    # (single source of truth); the component must render it by referencing
    # the named const. This mirrors how PS-029 handled the no-provider-rerun
    # story literal (const-defined, component-referenced).
    for line_const, needle in (
        ("FAILURE_TIMELINE_NO_FAKE_FAILURES_LINE", "No fake failures are claimed."),
        (
            "FAILURE_TIMELINE_WHERE_FAILURES_APPEAR_LINE",
            "This timeline shows where captured failures, retries, and fallbacks would appear.",
        ),
        (
            "FAILURE_TIMELINE_ZERO_PROVIDER_CALLS_LINE",
            "For the verified golden run, rehydrate uses B2-backed evidence with zero provider calls.",
        ),
    ):
        if line_const not in const_text:
            problems.append(f"{line_const} const is not declared")
        if needle not in const_text:
            problems.append(f"constants missing required line {needle!r}")
        if line_const not in comp_text:
            problems.append(
                f"component does not render required line via {line_const}"
            )
    return (not problems, problems)


def check_failure_theater_visible() -> tuple[bool, list[str]]:
    """The Failure Theater / failure-placement model is visible."""
    problems: list[str] = []
    const_text = read_text(FAILURE_TIMELINE_CONST) if FAILURE_TIMELINE_CONST.exists() else ""
    comp_text = read_text(FAILURE_TIMELINE_COMPONENT) if FAILURE_TIMELINE_COMPONENT.exists() else ""
    if "FAILURE_TIMELINE_FAILURE_THEATER_SLOTS" not in const_text:
        problems.append(
            "FAILURE_TIMELINE_FAILURE_THEATER_SLOTS const is not declared"
        )
    if "Failure Theater" not in comp_text:
        problems.append("component does not render the Failure Theater heading")
    for slot_key in (
        "captured_failure",
        "retry_decision",
        "fallback",
        "skipped_provider",
        "disabled_provider",
        "quota_block",
    ):
        if f'key: "{slot_key}"' not in const_text:
            problems.append(
                f"failure theater missing slot {slot_key!r}"
            )
    return (not problems, problems)


def check_archive_rehydrate_lab_visible() -> tuple[bool, list[str]]:
    """The Archive / Rehydrate Lab foundation card is visible."""
    problems: list[str] = []
    const_text = read_text(FAILURE_TIMELINE_CONST) if FAILURE_TIMELINE_CONST.exists() else ""
    comp_text = read_text(FAILURE_TIMELINE_COMPONENT) if FAILURE_TIMELINE_COMPONENT.exists() else ""
    if "FAILURE_TIMELINE_ARCHIVE_REHYDRATE_LAB_NOTE" not in const_text:
        problems.append(
            "FAILURE_TIMELINE_ARCHIVE_REHYDRATE_LAB_NOTE const is not declared"
        )
    if "Archive / Rehydrate Lab foundation" not in comp_text:
        problems.append(
            "component does not render the Archive / Rehydrate Lab foundation heading"
        )
    if "/b2-rehydrate-comparison" not in comp_text:
        problems.append(
            "lab foundation does not link to /b2-rehydrate-comparison"
        )
    if "PS-031" not in const_text or "PS-043" not in const_text:
        problems.append(
            "lab note does not reference later PS-031 / PS-043 work"
        )
    return (not problems, problems)


def check_no_fake_failures() -> tuple[bool, list[str]]:
    """No fake actual failure/fallback/outage claim is introduced."""
    problems: list[str] = []
    fake_claim_phrases = (
        "a provider failure occurred",
        "a fallback occurred",
        "an actual provider outage occurred",
        "a real provider failure",
        "a retry occurred during the golden run",
        "an incident event occurred",
        "a recovery event occurred",
    )
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
            for phrase in fake_claim_phrases:
                if phrase in line_lower:
                    start, end = _paragraph_range(lines, i)
                    window = "\n".join(lines[start:end])
                    if CONTEXT_MARKERS_RE.search(window):
                        continue
                    problems.append(
                        f"{rel(path)}:{i + 1}: fake failure claim with no "
                        f"non-claim context -> {line.strip()!r}"
                    )
    return (not problems, problems)


def check_truth_boundary() -> tuple[bool, list[str]]:
    """Truth boundary text is present and carries every required term."""
    if not FAILURE_TIMELINE_CONST.exists():
        return False, [f"missing {rel(FAILURE_TIMELINE_CONST)}"]
    const_text = read_text(FAILURE_TIMELINE_CONST)
    if "FAILURE_TIMELINE_TRUTH_BOUNDARY" not in const_text:
        return False, [
            "FAILURE_TIMELINE_TRUTH_BOUNDARY const is not declared"
        ]
    missing_in_const = [
        t for t in TRUTH_BOUNDARY_TERMS if t.lower() not in const_text.lower()
    ]
    if missing_in_const:
        return False, [
            f"failureAsProofTimeline.ts truth boundary missing term "
            f"{missing_in_const[0]!r}"
        ]
    if "FAILURE_TIMELINE_CLAIM_BOUNDARY_ALLOWED" not in const_text:
        return False, [
            "FAILURE_TIMELINE_CLAIM_BOUNDARY_ALLOWED const is not declared"
        ]
    if "FAILURE_TIMELINE_CLAIM_BOUNDARY_FORBIDDEN" not in const_text:
        return False, [
            "FAILURE_TIMELINE_CLAIM_BOUNDARY_FORBIDDEN const is not declared"
        ]
    if not FAILURE_TIMELINE_COMPONENT.exists():
        return False, [f"missing {rel(FAILURE_TIMELINE_COMPONENT)}"]
    comp = read_text(FAILURE_TIMELINE_COMPONENT)
    if "FAILURE_TIMELINE_TRUTH_BOUNDARY" not in comp:
        return False, [
            "FailureAsProofTimeline does not import the truth boundary const"
        ]
    if "FAILURE_TIMELINE_CLAIM_BOUNDARY_ALLOWED" not in comp:
        return False, [
            "FailureAsProofTimeline does not render the allowed claims list"
        ]
    if "FAILURE_TIMELINE_CLAIM_BOUNDARY_FORBIDDEN" not in comp:
        return False, [
            "FailureAsProofTimeline does not render the forbidden claims list"
        ]
    return True, []


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

    arbitrary_run_id = "run_ps030_must_still_404_0123456789abcdef"
    status = _get_passport_status(arbitrary_run_id)
    if status != 404:
        problems.append(
            f"arbitrary run id returned HTTP {status}, expected 404 "
            f"(broad public durable read must stay blocked)"
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
                if phrase.lower() in line_lower:
                    hit = True
                    break
            if not hit:
                continue
            if in_fence:
                continue
            start, end = _paragraph_range(lines, i)
            window = "\n".join(lines[start:end])
            if CONTEXT_MARKERS_RE.search(window):
                continue
            violations.append(
                f"{rel(path)}:{i + 1}: affirmative claim with no non-claim "
                f"context -> {line.strip()!r}"
            )
    return (not violations, violations)

# ---------------------------------------------------------------------------
# PS-034B retrofitted runner (safe local / check-only mode)
# ---------------------------------------------------------------------------

def check_no_prior_slice_evidence_modified() -> tuple[bool, list[str]]:
    """No prior-slice evidence file is left modified by the PS-030 smoke run."""
    problems = sl.prior_evidence_dirty_problems(
        own_slice_prefix="docs/evidence/ps-030/",
        slice_label="PS-030",
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
    ):
        if not p.exists():
            missing_inputs.append(rel(p))
    if missing_inputs:
        print("PS030 smoke: MISSING INPUT FILES")
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
    }
    constants_text = (
        read_text(FAILURE_TIMELINE_CONST)
        if FAILURE_TIMELINE_CONST.exists()
        else ""
    )

    checks: list[tuple[str, tuple[bool, list[str]]]] = [
        ("surface_exists", check_surface_exists()),
        ("route_exists", check_route_exists()),
        ("judge_links_timeline", check_judge_links_timeline()),
        (
            "timeline_links_rehydrate_manifest_b2_genblaze_passport_home",
            check_timeline_links(manifest),
        ),
        ("sources_present", check_sources_present(constants_text)),
        ("events_present", check_events_present(constants_text)),
        ("roadmap_referenced", check_roadmap_referenced(constants_text)),
        ("run_id_matches", check_run_id_matches(constants_text)),
        ("campaign_id_matches", check_campaign_id_matches(constants_text)),
        ("archive_uri_match", check_archive_uri_match(constants_text)),
        ("archive_sha256_match", check_archive_sha256_match(constants_text)),
        ("rehydrate_source", check_rehydrate_source(constants_text)),
        ("provider_calls_zero", check_provider_calls_zero(constants_text)),
        ("no_live_provider_call", check_no_live_provider_call(constants_text)),
        ("no_provider_rerun_story", check_no_provider_rerun_story()),
        ("failure_as_proof_visible", check_failure_as_proof_visible()),
        ("failure_theater_visible", check_failure_theater_visible()),
        ("archive_rehydrate_lab_visible", check_archive_rehydrate_lab_visible()),
        ("no_fake_failures", check_no_fake_failures()),
        ("truth_boundary", check_truth_boundary()),
        ("no_provider_call", check_no_provider_call()),
        ("no_broad_b2_read", check_no_broad_b2_read()),
        ("secret_scan", check_secrets()),
        ("forbidden_claims", check_forbidden_claims()),
        ("api_resolves_golden", check_api_resolves_golden(manifest)),
    ]

    all_pass, detail = sl.run_contract_checks("PS-030 Failure-as-Proof Timeline", checks)

    if opts.write_evidence:
        evidence = {
            "ok": bool(all_pass),
            "route_or_surface": (
                "/failure-timeline (dedicated frontend route) + "
                "FailureAsProofTimeline component + CTA from Judge Cockpit "
                "Home (golden demo run panel and Direct CTAs grid) + backlinks "
                "from B2 Rehydrate Comparison and Manifest Verification Panel "
                "(page variants)"
            ),
            "run_id": manifest.get("run_id"),
            "campaign_id": manifest.get("campaign_id"),
            "archive_uri": manifest.get("archive_uri"),
            "archive_sha256": manifest.get("archive_sha256"),
            "rehydrate_source": "b2_rehydrated",
            "provider_calls_during_rehydrate": 0,
            "no_live_provider_call_during_rehydrate": True,
            "timeline_sources_verified": sources_verified,
            "timeline_events_verified": events_verified,
            "failure_as_proof_surface_verified": failure_as_proof_surface_verified,
            "failure_theater_visible": failure_theater_visible,
            "archive_rehydrate_lab_foundation_visible": (
                archive_rehydrate_lab_foundation_visible
            ),
            "no_provider_rerun_story_visible": no_provider_rerun_story_visible,
            "no_fake_failure_claims": no_fake_failure_claims,
            "truth_boundary_present": truth_boundary_present,
            "source_ps021_evidence": rel(PS021_EVIDENCE),
            "source_ps024_manifest": rel(MANIFEST),
            "source_ps025_evidence": rel(PS025_EVIDENCE),
            "source_ps026_evidence": rel(PS026_EVIDENCE),
            "source_ps027_evidence": rel(PS027_EVIDENCE),
            "source_ps028_evidence": rel(PS028_EVIDENCE),
            "source_ps029_evidence": rel(PS029_EVIDENCE),
            "source_implementation_roadmap": rel(ROADMAP),
            "frontend_surface_verified": frontend_surface_verified,
            "api_surface_verified": api_surface_verified,
            "no_provider_call": no_provider_call,
            "no_broad_b2_read": no_broad_b2_read,
            "no_prior_slice_evidence_modified": bool(prior_clean_ok),
            "public_deployment_pending": bool(public_deployment_pending),
            "local_contract_proof": local_contract_proof,
            "public_deployment_verified": public_deployment_verified,
            "checked_at": _utc_now_iso(),
            "api_transport": "testclient",
            "timeline_values_verified": timeline_values_verified,
            "checks": detail,
            "truth_boundary": (
                "PS-030 proves the Failure-as-Proof Timeline surfaces that the "
                "checked-in evidence (PS-021, PS-024, PS-025, PS-026, PS-027, "
                "PS-028, PS-029) records a B2 rehydrate proof with zero provider "
                "calls during rehydrate, agrees on the golden run identifiers, "
                "archive URI, and archive SHA-256, and records rehydrate_source = "
                "b2_rehydrated, while showing where captured failures, retries, "
                "and fallbacks would appear if future evidence captured them. No "
                "actual provider failure or fallback is claimed unless checked-in "
                "evidence proves it. The timeline does not prove semantic truth, "
                "legal authenticity, C2PA authenticity, or human authorship. The "
                "timeline does not prove Object Lock or tamper-proof storage. The "
                "timeline did not fetch and hash the B2 object in the browser. "
                "The local contract is verified; the public deployment remains "
                "pending until the new backend is deployed and the public URL "
                "is verified end-to-end."
            ),
        }
        sl.write_json_atomic(EVIDENCE_OUT, evidence)
        print(f"evidence: {rel(EVIDENCE_OUT)}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(run())
