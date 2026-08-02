#!/usr/bin/env python3
"""PS-027 Genblaze Pipeline Graph -- smoke / validation script.

PS-034B retrofit: this smoke defaults to safe local / check-only
behavior. It does not recursively execute prior slice smokes, does
not run the frontend toolchain, does not use Git index hiding, does
not snapshot/restore prior evidence, and does not self-unlink its
evidence file. Evidence is written only when ``--write-evidence`` is
passed.

    python scripts/ps027_genblaze_pipeline_graph_smoke.py --local --check-only

It statically validates the PS027 surface without starting a
browser, without calling any provider, without reading any B2 object,
and without enabling broad durable reads.

Truth boundary: this script validates that the PS027 surface
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

# PS-027 changed / added files.
GENBLAZE_PIPELINE_CONST = REPO_ROOT / "apps" / "web" / "src" / "genblazePipeline.ts"
GENBLAZE_PIPELINE_GRAPH = REPO_ROOT / "apps" / "web" / "src" / "GenblazePipelineGraph.tsx"
HOMEPAGE = REPO_ROOT / "apps" / "web" / "src" / "JudgeCockpitHome.tsx"
APP_TSX = REPO_ROOT / "apps" / "web" / "src" / "App.tsx"
B2_EXPLORER = REPO_ROOT / "apps" / "web" / "src" / "B2EvidenceExplorer.tsx"
STYLES = REPO_ROOT / "apps" / "web" / "src" / "styles.css"
PROOF_DOC = REPO_ROOT / "docs" / "ps-027-genblaze-pipeline-graph-proof.md"

PS026_SMOKE = REPO_ROOT / "scripts" / "ps026_b2_evidence_explorer_smoke.py"
PS025_SMOKE = REPO_ROOT / "scripts" / "ps025_public_durable_passport_unlock_smoke.py"
PS024_SMOKE = REPO_ROOT / "scripts" / "ps024_golden_demo_run_pinning_smoke.py"
PS023_SMOKE = REPO_ROOT / "scripts" / "ps023_judge_cockpit_home_smoke.py"

EVIDENCE_OUT = REPO_ROOT / "docs" / "evidence" / "ps-027" / "genblaze-pipeline-graph-smoke.json"

# Files scanned for secrets and forbidden claims. The scanner script itself
# is intentionally excluded: it legitimately contains the detection literals
# (same convention as PS-023/PS-024/PS-025/PS-026 smokes).
SCAN_FILES: tuple[Path, ...] = (
    GENBLAZE_PIPELINE_CONST,
    GENBLAZE_PIPELINE_GRAPH,
    HOMEPAGE,
    APP_TSX,
    B2_EXPLORER,
    STYLES,
    PROOF_DOC,
)

# Subset of SCAN_FILES that are scanned for forbidden broad-B2-read and
# provider-call code patterns. Markdown documentation (e.g. the proof doc)
# legitimately mentions these literals when describing what the smoke
# rejects, so it is excluded. Only source code files (ts/tsx/py) are scanned
# here.
PROVIDER_AND_B2_SCAN_FILES: tuple[Path, ...] = (
    GENBLAZE_PIPELINE_CONST,
    GENBLAZE_PIPELINE_GRAPH,
    HOMEPAGE,
    APP_TSX,
    B2_EXPLORER,
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
    "media is legally authentic",
    "asset is C2PA-authenticated",
    "asset is C2PA authenticated",
    "archive is tamper-proof",
    "tamper-proof storage",
    "Object Lock",
    "enterprise-grade security",
    "multi-user security",
)

CONTEXT_MARKERS_RE = re.compile(
    r"does not|do not|must not|\bnot\b|non-claim|non-claims|non-claims|forbidden|"
    r"reject|rejected|avoid|without overclaim|unless actually implemented|"
    r"only inside non-claim|limitation|limitations|no affirmative|"
    r"unavailable|blocked|honestly|no live|no_new|no_fake|pending|planned",
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
# PS-027 must NOT add code that fetches an arbitrary B2 object from untrusted
# input or builds a B2 URI from arbitrary user input.
BROAD_B2_READ_PATTERNS: tuple[str, ...] = (
    "read_archive_from_b2",
    "b2.fetch",
    "b2GetObject",
    "list_b2_objects",
    "fetchB2Object",
)

# Patterns that would indicate a new provider call path was introduced.
# PS-027 must NOT add code that calls any external media provider.
# Note: the substring "live_provider_call" is intentionally NOT in this list
# because it appears legitimately in negation constants such as
# GENBLAZE_PIPELINE_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE. The patterns here
# match actual provider-call code paths only.
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
# Constant extraction from genblazePipeline.ts
# ---------------------------------------------------------------------------

def _extract_string_const(text: str, name: str) -> str | None:
    """Pull a `export const NAME = "...";` value out of genblazePipeline.ts.

    Handles simple one-line consts. Multi-line string-concat consts are pulled
    via a wider regex that joins adjacent quoted fragments.
    """
    # Try single-line first.
    m = re.search(
        r'export\s+const\s+' + re.escape(name) + r'\s*=\s*"((?:[^"\\]|\\.)*)"\s*;',
        text,
    )
    if m:
        return m.group(1)
    # Try multi-line concatenated string: capture every "..." fragment.
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
# Checks
# ---------------------------------------------------------------------------

def check_surface_exists() -> tuple[bool, list[str]]:
    """PS-027 surface exists as a frontend route + component + CTA."""
    problems: list[str] = []
    if not GENBLAZE_PIPELINE_GRAPH.exists():
        problems.append(f"missing component {rel(GENBLAZE_PIPELINE_GRAPH)}")
    if not GENBLAZE_PIPELINE_CONST.exists():
        problems.append(f"missing constants module {rel(GENBLAZE_PIPELINE_CONST)}")

    if GENBLAZE_PIPELINE_GRAPH.exists():
        comp_text = read_text(GENBLAZE_PIPELINE_GRAPH)
        for required in (
            "Genblaze Pipeline Graph",
            "GENBLAZE_PIPELINE_ARCHIVE_URI",
            "GENBLAZE_PIPELINE_ARCHIVE_SHA256",
            "GENBLAZE_PIPELINE_REHYDRATE_SOURCE",
            "GENBLAZE_PIPELINE_PROVIDER_CALLS_DURING_REHYDRATE",
            "GENBLAZE_PIPELINE_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE",
            "GENBLAZE_PIPELINE_TRUTH_BOUNDARY",
            "GENBLAZE_PIPELINE_NODES",
            "GENBLAZE_PIPELINE_EDGES",
            "Open B2 Evidence Explorer",
            "Back to Judge Cockpit Home",
        ):
            if required not in comp_text:
                problems.append(
                    f"GenblazePipelineGraph missing reference to {required!r}"
                )

    return (not problems, problems)


def check_route_exists() -> tuple[bool, list[str]]:
    """The /genblaze-pipeline route is registered in App.tsx."""
    problems: list[str] = []
    if not APP_TSX.exists():
        return False, [f"missing {rel(APP_TSX)}"]
    text = read_text(APP_TSX)
    if "isGenblazePipelinePath" not in text:
        problems.append("App.tsx does not register an isGenblazePipelinePath helper")
    if "/genblaze-pipeline" not in text:
        problems.append("App.tsx does not reference the /genblaze-pipeline path")
    if "GenblazePipelineGraph" not in text:
        problems.append("App.tsx does not render the GenblazePipelineGraph component")
    return (not problems, problems)


def check_judge_links_graph() -> tuple[bool, list[str]]:
    """The Judge Cockpit links to /genblaze-pipeline."""
    problems: list[str] = []
    if not HOMEPAGE.exists():
        return False, [f"missing {rel(HOMEPAGE)}"]
    text = read_text(HOMEPAGE)
    if "/genblaze-pipeline" not in text:
        problems.append("homepage does not link to /genblaze-pipeline")
    if "Open Genblaze Pipeline Graph" not in text:
        problems.append("homepage does not surface a Genblaze Pipeline Graph CTA label")
    return (not problems, problems)


def check_graph_links(
    manifest: dict, ps026: dict
) -> tuple[bool, list[str]]:
    """The graph links to /b2-evidence, the golden passport, and /."""
    problems: list[str] = []
    if not GENBLAZE_PIPELINE_GRAPH.exists():
        return False, [f"missing {rel(GENBLAZE_PIPELINE_GRAPH)}"]
    text = read_text(GENBLAZE_PIPELINE_GRAPH)
    if "/b2-evidence" not in text:
        problems.append("graph does not link to /b2-evidence")
    golden_run_id = manifest.get("run_id") or ps026.get("run_id")
    if not golden_run_id:
        problems.append("manifest/ps026 missing run_id")
    elif f'"/passport/" + ' not in text and f"/passport/{golden_run_id}" not in text:
        problems.append(
            "graph does not link to the golden passport via /passport/<golden_run_id>"
        )
    if 'href="/"' not in text:
        problems.append("graph does not link back to / (Judge Cockpit Home)")
    return (not problems, problems)


# Required pipeline nodes (PS-027 spec). The exact required labels.
REQUIRED_PIPELINE_NODES: tuple[str, ...] = (
    "Campaign brief",
    "Provider Router",
    "Genblaze orchestration",
    "Media generation attempt",
    "Asset / manifest capture",
    "Backblaze B2 archive",
    "Provenance passport",
    "Durable rehydrate",
    "Judge review",
)

# Required edge story text (PS-027 spec). Each must appear in the source.
REQUIRED_PIPELINE_EDGES: tuple[str, ...] = (
    "Brief enters pipeline",
    "Router selects provider path",
    "Genblaze-backed flow records generation/provenance",
    "Asset and manifest are archived to B2",
    "Passport exposes run proof",
    "Rehydrate loads durable archive",
    "Rehydrate uses zero provider calls",
    "Judge reviews evidence",
)


def check_pipeline_nodes() -> tuple[bool, list[str]]:
    """Every required pipeline node label is present in the source."""
    problems: list[str] = []
    if not GENBLAZE_PIPELINE_CONST.exists():
        return False, [f"missing {rel(GENBLAZE_PIPELINE_CONST)}"]
    text = read_text(GENBLAZE_PIPELINE_CONST)
    for required in REQUIRED_PIPELINE_NODES:
        if required not in text:
            problems.append(f"pipeline node missing: {required!r}")
    # Also confirm the graph renders the node constants.
    if GENBLAZE_PIPELINE_GRAPH.exists():
        graph_text = read_text(GENBLAZE_PIPELINE_GRAPH)
        if "GENBLAZE_PIPELINE_NODES" not in graph_text:
            problems.append("GenblazePipelineGraph does not render GENBLAZE_PIPELINE_NODES")
    return (not problems, problems)


def check_pipeline_edges() -> tuple[bool, list[str]]:
    """Every required edge/story phrase is present in the source."""
    problems: list[str] = []
    if not GENBLAZE_PIPELINE_CONST.exists():
        return False, [f"missing {rel(GENBLAZE_PIPELINE_CONST)}"]
    text = read_text(GENBLAZE_PIPELINE_CONST)
    for required in REQUIRED_PIPELINE_EDGES:
        if required not in text:
            problems.append(f"pipeline edge missing: {required!r}")
    if GENBLAZE_PIPELINE_GRAPH.exists():
        graph_text = read_text(GENBLAZE_PIPELINE_GRAPH)
        if "GENBLAZE_PIPELINE_EDGES" not in graph_text:
            problems.append("GenblazePipelineGraph does not render GENBLAZE_PIPELINE_EDGES")
    return (not problems, problems)


def check_run_id_matches(constants_text: str, manifest: dict) -> tuple[bool, list[str]]:
    got = _extract_string_const(constants_text, "GENBLAZE_PIPELINE_RUN_ID")
    want = manifest.get("run_id")
    if got == want:
        return True, []
    return False, [f"run_id: graph={got!r} vs manifest={want!r}"]


def check_campaign_id_matches(constants_text: str, manifest: dict) -> tuple[bool, list[str]]:
    got = _extract_string_const(constants_text, "GENBLAZE_PIPELINE_CAMPAIGN_ID")
    want = manifest.get("campaign_id")
    if got == want:
        return True, []
    return False, [f"campaign_id: graph={got!r} vs manifest={want!r}"]


def check_archive_uri_match(
    constants_text: str, manifest: dict, ps021: dict, ps025: dict, ps026: dict
) -> tuple[bool, list[str]]:
    got = _extract_string_const(constants_text, "GENBLAZE_PIPELINE_ARCHIVE_URI")
    problems: list[str] = []
    if got != manifest.get("archive_uri"):
        problems.append(
            f"archive_uri: graph={got!r} vs manifest={manifest.get('archive_uri')!r}"
        )
    if got != ps021.get("archive_uri"):
        problems.append(
            f"archive_uri: graph={got!r} vs ps021={ps021.get('archive_uri')!r}"
        )
    if got != ps025.get("archive_uri"):
        problems.append(
            f"archive_uri: graph={got!r} vs ps025={ps025.get('archive_uri')!r}"
        )
    if got != ps026.get("archive_uri"):
        problems.append(
            f"archive_uri: graph={got!r} vs ps026={ps026.get('archive_uri')!r}"
        )
    return (not problems, problems)


def check_archive_sha256_match(
    constants_text: str, manifest: dict, ps021: dict, ps025: dict, ps026: dict
) -> tuple[bool, list[str]]:
    got = _extract_string_const(constants_text, "GENBLAZE_PIPELINE_ARCHIVE_SHA256")
    problems: list[str] = []
    if got != manifest.get("archive_sha256"):
        problems.append(
            f"archive_sha256: graph={got!r} vs manifest="
            f"{manifest.get('archive_sha256')!r}"
        )
    if got != ps021.get("archive_sha256"):
        problems.append(
            f"archive_sha256: graph={got!r} vs ps021="
            f"{ps021.get('archive_sha256')!r}"
        )
    if got != ps025.get("archive_sha256"):
        problems.append(
            f"archive_sha256: graph={got!r} vs ps025="
            f"{ps025.get('archive_sha256')!r}"
        )
    if got != ps026.get("archive_sha256"):
        problems.append(
            f"archive_sha256: graph={got!r} vs ps026="
            f"{ps026.get('archive_sha256')!r}"
        )
    return (not problems, problems)


def check_rehydrate_source(constants_text: str) -> tuple[bool, list[str]]:
    got = _extract_string_const(constants_text, "GENBLAZE_PIPELINE_REHYDRATE_SOURCE")
    if got == "b2_rehydrated":
        return True, []
    return False, [f"rehydrate_source: graph={got!r}, expected 'b2_rehydrated'"]


def check_provider_calls_zero(constants_text: str) -> tuple[bool, list[str]]:
    got = _extract_number_const(constants_text, "GENBLAZE_PIPELINE_PROVIDER_CALLS_DURING_REHYDRATE")
    if got == 0:
        return True, []
    return False, [
        f"provider_calls_during_rehydrate: graph={got!r}, expected 0"
    ]


def check_no_live_provider_call() -> tuple[bool, list[str]]:
    if not GENBLAZE_PIPELINE_CONST.exists():
        return False, [f"missing {rel(GENBLAZE_PIPELINE_CONST)}"]
    text = read_text(GENBLAZE_PIPELINE_CONST)
    got = _extract_bool_const(text, "GENBLAZE_PIPELINE_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE")
    if got is True:
        return True, []
    return False, [
        f"no_live_provider_call_during_rehydrate: graph={got!r}, expected True"
    ]


def check_truth_boundary() -> tuple[bool, list[str]]:
    """Truth boundary text is present and carries every required term."""
    if not GENBLAZE_PIPELINE_CONST.exists():
        return False, [f"missing {rel(GENBLAZE_PIPELINE_CONST)}"]
    const_text = read_text(GENBLAZE_PIPELINE_CONST)
    if "GENBLAZE_PIPELINE_TRUTH_BOUNDARY" not in const_text:
        return False, ["GENBLAZE_PIPELINE_TRUTH_BOUNDARY const is not declared"]
    missing_in_const = [
        t for t in TRUTH_BOUNDARY_TERMS if t.lower() not in const_text.lower()
    ]
    if missing_in_const:
        return False, [
            f"genblazePipeline.ts truth boundary missing term {missing_in_const[0]!r}"
        ]
    if not GENBLAZE_PIPELINE_GRAPH.exists():
        return False, [f"missing {rel(GENBLAZE_PIPELINE_GRAPH)}"]
    comp = read_text(GENBLAZE_PIPELINE_GRAPH)
    if "GENBLAZE_PIPELINE_TRUTH_BOUNDARY" not in comp:
        return False, [
            "GenblazePipelineGraph does not import the truth boundary const"
        ]
    return True, []


def check_no_broad_b2_read() -> tuple[bool, list[str]]:
    """No new broad B2 object read path is introduced.

    Two parts:
      (a) PS-027 source files must not contain any literal broad B2 read API
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

    arbitrary_run_id = "run_ps027_must_still_404_0123456789abcdef"
    status = _get_passport_status(arbitrary_run_id)
    if status != 404:
        problems.append(
            f"arbitrary run id returned HTTP {status}, expected 404 "
            f"(broad public durable read must stay blocked)"
        )

    return (not problems, problems)


def check_no_provider_call() -> tuple[bool, list[str]]:
    """No new provider call path is introduced.

    PS-027 source files must not contain any literal provider-call pattern.
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
    """No prior-slice evidence file is left modified by the PS-027 smoke run."""
    problems = sl.prior_evidence_dirty_problems(
        own_slice_prefix="docs/evidence/ps-027/",
        slice_label="PS-027",
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
    ):
        if not p.exists():
            missing_inputs.append(rel(p))
    if missing_inputs:
        print("PS027 smoke: MISSING INPUT FILES")
        for f in missing_inputs:
            print(f"  - {f}")
        return 1

    manifest = load_json(MANIFEST)
    ps021 = load_json(PS021_EVIDENCE)
    ps025 = load_json(PS025_EVIDENCE)
    ps026 = load_json(PS026_EVIDENCE)
    constants_text = read_text(GENBLAZE_PIPELINE_CONST) if GENBLAZE_PIPELINE_CONST.exists() else ""

    checks: list[tuple[str, tuple[bool, list[str]]]] = [
        ("surface_exists", check_surface_exists()),
        ("route_exists", check_route_exists()),
        ("judge_links_graph", check_judge_links_graph()),
        ("graph_links_b2_passport_home", check_graph_links(manifest, ps026)),
        ("pipeline_nodes", check_pipeline_nodes()),
        ("pipeline_edges", check_pipeline_edges()),
        ("run_id_matches", check_run_id_matches(constants_text, manifest)),
        ("campaign_id_matches", check_campaign_id_matches(constants_text, manifest)),
        (
            "archive_uri_match",
            check_archive_uri_match(constants_text, manifest, ps021, ps025, ps026),
        ),
        (
            "archive_sha256_match",
            check_archive_sha256_match(constants_text, manifest, ps021, ps025, ps026),
        ),
        ("rehydrate_source", check_rehydrate_source(constants_text)),
        ("provider_calls_zero", check_provider_calls_zero(constants_text)),
        ("no_live_provider_call", check_no_live_provider_call()),
        ("truth_boundary", check_truth_boundary()),
        ("no_broad_b2_read", check_no_broad_b2_read()),
        ("no_provider_call", check_no_provider_call()),
        ("secret_scan", check_secrets()),
        ("forbidden_claims", check_forbidden_claims()),
        ("api_resolves_golden", check_api_resolves_golden(manifest)),
    ]

    all_pass, detail = sl.run_contract_checks("PS-027 Genblaze Pipeline Graph", checks)

    if opts.write_evidence:
        evidence = {
            "ok": bool(all_pass),
            "route_or_surface": (
                "/genblaze-pipeline (dedicated frontend route) + "
                "GenblazePipelineGraph component + CTAs from Judge Cockpit Home "
                "(golden demo run panel and Direct CTAs grid) + backlink from "
                "B2 Evidence Explorer (page variant)"
            ),
            "run_id": manifest.get("run_id"),
            "campaign_id": manifest.get("campaign_id"),
            "archive_uri": manifest.get("archive_uri"),
            "archive_sha256": manifest.get("archive_sha256"),
            "rehydrate_source": "b2_rehydrated",
            "provider_calls_during_rehydrate": 0,
            "no_live_provider_call_during_rehydrate": True,
            "pipeline_nodes_verified": bool(check_pipeline_nodes()[0]),
            "pipeline_edges_verified": bool(check_pipeline_edges()[0]),
            "genblaze_surface_verified": bool(check_surface_exists()[0]),
            "truth_boundary_present": bool(check_truth_boundary()[0]),
            "source_ps021_evidence": rel(PS021_EVIDENCE),
            "source_ps024_manifest": rel(MANIFEST),
            "source_ps025_evidence": rel(PS025_EVIDENCE),
            "source_ps026_evidence": rel(PS026_EVIDENCE),
            "frontend_surface_verified": bool(check_surface_exists()[0]),
            "api_surface_verified": bool(check_api_resolves_golden(manifest)[0]),
            "no_provider_call": bool(check_no_provider_call()[0]),
            "no_broad_b2_read": bool(check_no_broad_b2_read()[0]),
            "no_prior_slice_evidence_modified": bool(prior_clean_ok),
            "public_deployment_pending": bool(public_deployment_pending),
            "local_contract_proof": local_contract_proof,
            "public_deployment_verified": public_deployment_verified,
            "checked_at": _utc_now_iso(),
            "api_transport": "testclient",
            "checks": detail,
            "truth_boundary": (
                "PS-027 proves the Genblaze Pipeline Graph surfaces the verified "
                "pipeline evidence (run_id, campaign_id, archive URI, archive "
                "SHA-256, rehydrate source, zero provider calls during "
                "rehydrate) recorded by PS-021 and pinned by PS-024/PS-025/"
                "PS-026, distinguishes verified pipeline evidence from inferred "
                "product explanation, local contract proof, and public "
                "deployment pending, without calling any provider, without "
                "reading any B2 object, and without enabling broad durable "
                "reads. It does not prove semantic truth, legal authenticity, "
                "C2PA authenticity, or human authorship. Genblaze is used in "
                "the ProofStudio pipeline; it does not independently certify "
                "the truth of the media. The local contract is verified; the "
                "public deployment remains pending until the new backend is "
                "deployed and the public URL is verified end-to-end."
            ),
        }
        sl.write_json_atomic(EVIDENCE_OUT, evidence)
        print(f"evidence: {rel(EVIDENCE_OUT)}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(run())
