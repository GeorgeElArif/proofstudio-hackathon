#!/usr/bin/env python3
"""PS-028 Manifest Verification Panel -- smoke / validation script.

PS-034B retrofit: this smoke defaults to safe local / check-only
behavior. It does not recursively execute prior slice smokes, does
not run the frontend toolchain, does not use Git index hiding, does
not snapshot/restore prior evidence, and does not self-unlink its
evidence file. Evidence is written only when ``--write-evidence`` is
passed.

    python scripts/ps028_manifest_verification_panel_smoke.py --local --check-only

It statically validates the PS028 surface without starting a
browser, without calling any provider, without reading any B2 object,
and without enabling broad durable reads.

Truth boundary: this script validates that the PS028 surface
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

# PS-028 changed / added files.
MANIFEST_VERIFICATION_CONST = REPO_ROOT / "apps" / "web" / "src" / "manifestVerification.ts"
MANIFEST_VERIFICATION_PANEL = REPO_ROOT / "apps" / "web" / "src" / "ManifestVerificationPanel.tsx"
HOMEPAGE = REPO_ROOT / "apps" / "web" / "src" / "JudgeCockpitHome.tsx"
APP_TSX = REPO_ROOT / "apps" / "web" / "src" / "App.tsx"
B2_EXPLORER = REPO_ROOT / "apps" / "web" / "src" / "B2EvidenceExplorer.tsx"
GENBLAZE_GRAPH = REPO_ROOT / "apps" / "web" / "src" / "GenblazePipelineGraph.tsx"
STYLES = REPO_ROOT / "apps" / "web" / "src" / "styles.css"
PROOF_DOC = REPO_ROOT / "docs" / "ps-028-manifest-verification-panel-proof.md"

PS027_SMOKE = REPO_ROOT / "scripts" / "ps027_genblaze_pipeline_graph_smoke.py"
PS026_SMOKE = REPO_ROOT / "scripts" / "ps026_b2_evidence_explorer_smoke.py"
PS025_SMOKE = REPO_ROOT / "scripts" / "ps025_public_durable_passport_unlock_smoke.py"
PS024_SMOKE = REPO_ROOT / "scripts" / "ps024_golden_demo_run_pinning_smoke.py"
PS023_SMOKE = REPO_ROOT / "scripts" / "ps023_judge_cockpit_home_smoke.py"

EVIDENCE_OUT = REPO_ROOT / "docs" / "evidence" / "ps-028" / "manifest-verification-panel-smoke.json"

# Files scanned for secrets and forbidden claims. The scanner script itself
# is intentionally excluded: it legitimately contains the detection literals
# (same convention as PS-023 / PS-024 / PS-025 / PS-026 / PS-027 smokes).
SCAN_FILES: tuple[Path, ...] = (
    MANIFEST_VERIFICATION_CONST,
    MANIFEST_VERIFICATION_PANEL,
    HOMEPAGE,
    APP_TSX,
    B2_EXPLORER,
    GENBLAZE_GRAPH,
    STYLES,
    PROOF_DOC,
)

# Subset of SCAN_FILES scanned for forbidden broad-B2-read and provider-call
# code patterns. Markdown documentation (the proof doc) legitimately mentions
# these literals when describing what the smoke rejects, so it is excluded.
# Only source code files (ts/tsx/py) are scanned here.
PROVIDER_AND_B2_SCAN_FILES: tuple[Path, ...] = (
    MANIFEST_VERIFICATION_CONST,
    MANIFEST_VERIFICATION_PANEL,
    HOMEPAGE,
    APP_TSX,
    B2_EXPLORER,
    GENBLAZE_GRAPH,
    STYLES,
)

TRUTH_BOUNDARY_TERMS: tuple[str, ...] = (
    "semantic truth",
    "legal authenticity",
    "C2PA authenticity",
    "human authorship",
)

FORBIDDEN_AFFIRMATIVE: tuple[str, ...] = (
    "ProofStudio proves the image is true",
    "ProofStudio proves media is true",
    "Genblaze independently certifies the truth of the media",
    "Genblaze independently certifies truth of the media",
    "Genblaze certifies the truth",
    "the panel proves semantic truth of the media",
    "the panel proves media is true",
    "media is legally authentic",
    "asset is C2PA-authenticated",
    "asset is C2PA authenticated",
    "archive is tamper-proof",
    "the panel proves Object Lock",
    "the panel proves tamper-proof storage",
    "browser fetched and hashed the B2 object",
    "browser verified the B2 object",
    "Object Lock is enabled",
    "tamper-proof storage is enabled",
    "enterprise-grade security",
    "multi-user security",
    "public deployment is verified",
    "public deployment verified",
)

CONTEXT_MARKERS_RE = re.compile(
    r"does not|do not|must not|\bnot\b|non-claim|non-claims|forbidden|"
    r"reject|rejected|avoid|without overclaim|unless actually implemented|"
    r"only inside non-claim|limitation|limitations|no affirmative|"
    r"unavailable|blocked|honestly|no live|no_new|no_fake|pending|planned|"
    r"did not fetch|does not claim|did not claim|without",
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
# PS-028 must NOT add code that fetches an arbitrary B2 object from untrusted
# input or builds a B2 URI from arbitrary user input.
BROAD_B2_READ_PATTERNS: tuple[str, ...] = (
    "read_archive_from_b2",
    "b2.fetch",
    "b2GetObject",
    "list_b2_objects",
    "fetchB2Object",
    "fetch(",
)

# Patterns that would indicate a new provider call path was introduced.
# PS-028 must NOT add code that calls any external media provider.
# Note: the substring "live_provider_call" is intentionally NOT in this list
# because it appears legitimately in negation constants such as
# MANIFEST_VERIFICATION_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE.
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
# Constant extraction from manifestVerification.ts
# ---------------------------------------------------------------------------

def _extract_string_const(text: str, name: str) -> str | None:
    """Pull an `export const NAME = "...";` value out of the constants file.

    Handles simple one-line consts. Multi-line string-concat consts are pulled
    via a wider regex that joins adjacent quoted fragments.
    """
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
    """Return the HTTP status code for GET /runs/<run_id>/passport.

    Uses FastAPI TestClient against a fresh empty store. This is the same
    local contract the PS-025 smoke proves. No provider is called and no B2
    object is read.
    """
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
    """Return the value of `field_key` for `source_id` from its evidence JSON.

    Returns None if the field is absent. Applies the PS-021 durable_source
    override.
    """
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
    }[source_id]


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_surface_exists() -> tuple[bool, list[str]]:
    """PS-028 surface exists as a frontend route + component + CTA."""
    problems: list[str] = []
    if not MANIFEST_VERIFICATION_PANEL.exists():
        problems.append(f"missing component {rel(MANIFEST_VERIFICATION_PANEL)}")
    if not MANIFEST_VERIFICATION_CONST.exists():
        problems.append(f"missing constants module {rel(MANIFEST_VERIFICATION_CONST)}")

    if MANIFEST_VERIFICATION_PANEL.exists():
        comp_text = read_text(MANIFEST_VERIFICATION_PANEL)
        for required in (
            "Manifest Verification Panel",
            "MANIFEST_VERIFICATION_FIELDS",
            "MANIFEST_VERIFICATION_SOURCES",
            "MANIFEST_VERIFICATION_MATRIX",
            "MANIFEST_VERIFICATION_TRUTH_BOUNDARY",
            "Open Genblaze Pipeline Graph",
            "Open B2 Evidence Explorer",
            "Open Golden Passport",
            "Back to Judge Cockpit Home",
        ):
            if required not in comp_text:
                problems.append(
                    f"ManifestVerificationPanel missing reference to {required!r}"
                )
    return (not problems, problems)


def check_route_exists() -> tuple[bool, list[str]]:
    """The /manifest-verification route is registered in App.tsx."""
    problems: list[str] = []
    if not APP_TSX.exists():
        return False, [f"missing {rel(APP_TSX)}"]
    text = read_text(APP_TSX)
    if "isManifestVerificationPath" not in text:
        problems.append(
            "App.tsx does not register an isManifestVerificationPath helper"
        )
    if "/manifest-verification" not in text:
        problems.append("App.tsx does not reference the /manifest-verification path")
    if "ManifestVerificationPanel" not in text:
        problems.append(
            "App.tsx does not render the ManifestVerificationPanel component"
        )
    return (not problems, problems)


def check_judge_links_panel() -> tuple[bool, list[str]]:
    """The Judge Cockpit links to /manifest-verification."""
    problems: list[str] = []
    if not HOMEPAGE.exists():
        return False, [f"missing {rel(HOMEPAGE)}"]
    text = read_text(HOMEPAGE)
    if "/manifest-verification" not in text:
        problems.append("homepage does not link to /manifest-verification")
    if "Open Manifest Verification Panel" not in text:
        problems.append(
            "homepage does not surface a Manifest Verification Panel CTA label"
        )
    return (not problems, problems)


def check_panel_links(manifest: dict) -> tuple[bool, list[str]]:
    """The panel links to /genblaze-pipeline, /b2-evidence, golden passport, /."""
    problems: list[str] = []
    if not MANIFEST_VERIFICATION_PANEL.exists():
        return False, [f"missing {rel(MANIFEST_VERIFICATION_PANEL)}"]
    text = read_text(MANIFEST_VERIFICATION_PANEL)
    if "/genblaze-pipeline" not in text:
        problems.append("panel does not link to /genblaze-pipeline")
    if "/b2-evidence" not in text:
        problems.append("panel does not link to /b2-evidence")
    golden_run_id = manifest.get("run_id")
    if not golden_run_id:
        problems.append("manifest missing run_id")
    elif (
        f"/passport/{golden_run_id}" not in text
        and '"/passport/" + MANIFEST_VERIFICATION_RUN_ID' not in text
    ):
        problems.append(
            "panel does not link to the golden passport via "
            "/passport/<golden_run_id>"
        )
    if 'href="/"' not in text:
        problems.append("panel does not link back to / (Judge Cockpit Home)")
    return (not problems, problems)


def check_sources_present(constants_text: str) -> tuple[bool, list[str]]:
    """All 5 required sources are listed in manifestVerification.ts."""
    problems: list[str] = []
    for required in (
        "Golden demo manifest",
        "PS-021 B2 durable rehydrate evidence",
        "PS-025 public durable passport evidence",
        "PS-026 B2 Evidence Explorer evidence",
        "PS-027 Genblaze Pipeline Graph evidence",
    ):
        if required not in constants_text:
            problems.append(f"manifestVerification.ts missing source {required!r}")
    for path_const in (
        "MANIFEST_VERIFICATION_SOURCE_PS024_MANIFEST",
        "MANIFEST_VERIFICATION_SOURCE_PS021_EVIDENCE",
        "MANIFEST_VERIFICATION_SOURCE_PS025_EVIDENCE",
        "MANIFEST_VERIFICATION_SOURCE_PS026_EVIDENCE",
        "MANIFEST_VERIFICATION_SOURCE_PS027_EVIDENCE",
    ):
        if path_const not in constants_text:
            problems.append(f"manifestVerification.ts missing constant {path_const!r}")
    return (not problems, problems)


def check_fields_present(constants_text: str) -> tuple[bool, list[str]]:
    """All 7 required fields are listed in manifestVerification.ts."""
    problems: list[str] = []
    for required in REQUIRED_FIELD_KEYS:
        # Field must appear as a key in MANIFEST_VERIFICATION_FIELDS.
        if f'key: "{required}"' not in constants_text:
            problems.append(
                f"manifestVerification.ts missing field key {required!r}"
            )
    return (not problems, problems)


def check_run_id_matches(constants_text: str) -> tuple[bool, list[str]]:
    """run_id matches across every source AND the frontend constant."""
    problems: list[str] = []
    want = _source_field_value("ps024", "run_id")
    for src_id in REQUIRED_SOURCE_IDS:
        got = _source_field_value(src_id, "run_id")
        if got != want:
            problems.append(
                f"run_id: source {src_id}={got!r} vs manifest={want!r}"
            )
    const = _extract_string_const(constants_text, "MANIFEST_VERIFICATION_RUN_ID")
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
        constants_text, "MANIFEST_VERIFICATION_CAMPAIGN_ID"
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
        constants_text, "MANIFEST_VERIFICATION_ARCHIVE_URI"
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
        constants_text, "MANIFEST_VERIFICATION_ARCHIVE_SHA256"
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
        constants_text, "MANIFEST_VERIFICATION_REHYDRATE_SOURCE"
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
        constants_text, "MANIFEST_VERIFICATION_PROVIDER_CALLS_DURING_REHYDRATE"
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
        "MANIFEST_VERIFICATION_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE",
    )
    if const is not True:
        problems.append(
            f"no_live_provider_call_during_rehydrate: frontend constant="
            f"{const!r}, expected True"
        )
    return (not problems, problems)


def check_truth_boundary() -> tuple[bool, list[str]]:
    """Truth boundary text is present and carries every required term."""
    if not MANIFEST_VERIFICATION_CONST.exists():
        return False, [f"missing {rel(MANIFEST_VERIFICATION_CONST)}"]
    const_text = read_text(MANIFEST_VERIFICATION_CONST)
    if "MANIFEST_VERIFICATION_TRUTH_BOUNDARY" not in const_text:
        return False, ["MANIFEST_VERIFICATION_TRUTH_BOUNDARY const is not declared"]
    missing_in_const = [
        t for t in TRUTH_BOUNDARY_TERMS if t.lower() not in const_text.lower()
    ]
    if missing_in_const:
        return False, [
            f"manifestVerification.ts truth boundary missing term "
            f"{missing_in_const[0]!r}"
        ]
    # Claim boundary must also be present.
    if "MANIFEST_CLAIM_BOUNDARY_ALLOWED" not in const_text:
        return False, ["MANIFEST_CLAIM_BOUNDARY_ALLOWED const is not declared"]
    if "MANIFEST_CLAIM_BOUNDARY_FORBIDDEN" not in const_text:
        return False, ["MANIFEST_CLAIM_BOUNDARY_FORBIDDEN const is not declared"]
    if not MANIFEST_VERIFICATION_PANEL.exists():
        return False, [f"missing {rel(MANIFEST_VERIFICATION_PANEL)}"]
    comp = read_text(MANIFEST_VERIFICATION_PANEL)
    if "MANIFEST_VERIFICATION_TRUTH_BOUNDARY" not in comp:
        return False, [
            "ManifestVerificationPanel does not import the truth boundary const"
        ]
    if "MANIFEST_CLAIM_BOUNDARY_ALLOWED" not in comp:
        return False, [
            "ManifestVerificationPanel does not render the allowed claims list"
        ]
    if "MANIFEST_CLAIM_BOUNDARY_FORBIDDEN" not in comp:
        return False, [
            "ManifestVerificationPanel does not render the forbidden claims list"
        ]
    return True, []


def check_no_broad_b2_read() -> tuple[bool, list[str]]:
    """No new broad B2 object read path is introduced.

    Two parts:
      (a) PS-028 source files must not contain any literal broad B2 read API
          call (client-side fetch / arbitrary B2 object lookup).
      (b) An arbitrary run_id still 404s through the public durable passport
          path -- the PS-025 narrow allowlist must still hold.
    """
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

    arbitrary_run_id = "run_ps028_must_still_404_0123456789abcdef"
    status = _get_passport_status(arbitrary_run_id)
    if status != 404:
        problems.append(
            f"arbitrary run id returned HTTP {status}, expected 404 "
            f"(broad public durable read must stay blocked)"
        )

    return (not problems, problems)


def check_no_provider_call() -> tuple[bool, list[str]]:
    """No new provider call path is introduced.

    PS-028 source files must not contain any literal provider-call pattern.
    """
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
    """No prior-slice evidence file is left modified by the PS-028 smoke run."""
    problems = sl.prior_evidence_dirty_problems(
        own_slice_prefix="docs/evidence/ps-028/",
        slice_label="PS-028",
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
    ):
        if not p.exists():
            missing_inputs.append(rel(p))
    if missing_inputs:
        print("PS028 smoke: MISSING INPUT FILES")
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
    }
    constants_text = (
        read_text(MANIFEST_VERIFICATION_CONST)
        if MANIFEST_VERIFICATION_CONST.exists()
        else ""
    )

    checks: list[tuple[str, tuple[bool, list[str]]]] = [
        ("surface_exists", check_surface_exists()),
        ("route_exists", check_route_exists()),
        ("judge_links_panel", check_judge_links_panel()),
        (
            "panel_links_genblaze_b2_passport_home",
            check_panel_links(manifest),
        ),
        ("sources_present", check_sources_present(constants_text)),
        ("fields_present", check_fields_present(constants_text)),
        ("run_id_matches", check_run_id_matches(constants_text)),
        ("campaign_id_matches", check_campaign_id_matches(constants_text)),
        ("archive_uri_match", check_archive_uri_match(constants_text)),
        ("archive_sha256_match", check_archive_sha256_match(constants_text)),
        ("rehydrate_source", check_rehydrate_source(constants_text)),
        ("provider_calls_zero", check_provider_calls_zero(constants_text)),
        ("no_live_provider_call", check_no_live_provider_call(constants_text)),
        ("truth_boundary", check_truth_boundary()),
        ("no_broad_b2_read", check_no_broad_b2_read()),
        ("no_provider_call", check_no_provider_call()),
        ("secret_scan", check_secrets()),
        ("forbidden_claims", check_forbidden_claims()),
        ("api_resolves_golden", check_api_resolves_golden(manifest)),
    ]

    all_pass, detail = sl.run_contract_checks("PS-028 Manifest Verification Panel", checks)

    if opts.write_evidence:
        evidence = {
            "ok": bool(all_pass),
            "route_or_surface": (
                "/manifest-verification (dedicated frontend route) + "
                "ManifestVerificationPanel component + CTAs from Judge Cockpit "
                "Home (golden demo run panel and Direct CTAs grid) + backlinks "
                "from B2 Evidence Explorer and Genblaze Pipeline Graph "
                "(page variants)"
            ),
            "run_id": manifest.get("run_id"),
            "campaign_id": manifest.get("campaign_id"),
            "archive_uri": manifest.get("archive_uri"),
            "archive_sha256": manifest.get("archive_sha256"),
            "rehydrate_source": "b2_rehydrated",
            "provider_calls_during_rehydrate": 0,
            "no_live_provider_call_during_rehydrate": True,
            "sources_verified": sources_verified,
            "fields_verified": fields_verified,
            "manifest_consistency_verified": manifest_consistency_verified,
            "manifest_panel_surface_verified": manifest_panel_surface_verified,
            "truth_boundary_present": truth_boundary_present,
            "source_ps021_evidence": rel(PS021_EVIDENCE),
            "source_ps024_manifest": rel(MANIFEST),
            "source_ps025_evidence": rel(PS025_EVIDENCE),
            "source_ps026_evidence": rel(PS026_EVIDENCE),
            "source_ps027_evidence": rel(PS027_EVIDENCE),
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
            "checks": detail,
            "truth_boundary": (
                "PS-028 proves the Manifest Verification Panel surfaces that the "
                "checked-in evidence (PS-021, PS-024, PS-025, PS-026, PS-027) "
                "agrees on the golden run identifiers, archive URI, archive "
                "SHA-256, rehydrate source (b2_rehydrated), zero provider calls "
                "during rehydrate, and the no-live-provider-call flag, without "
                "calling any provider, without reading any B2 object, and "
                "without claiming the browser fetched and hashed the B2 object. "
                "It does not prove semantic truth, legal authenticity, C2PA "
                "authenticity, or human authorship. The panel does not prove "
                "Object Lock or tamper-proof storage. The local contract is "
                "verified; the public deployment remains pending until the new "
                "backend is deployed and the public URL is verified end-to-end."
            ),
        }
        sl.write_json_atomic(EVIDENCE_OUT, evidence)
        print(f"evidence: {rel(EVIDENCE_OUT)}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(run())
