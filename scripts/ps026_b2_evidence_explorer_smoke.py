#!/usr/bin/env python3
"""PS-026 B2 Evidence Explorer -- smoke / validation script.

PS-034B retrofit: this smoke defaults to safe local / check-only
behavior. It does not recursively execute prior slice smokes, does
not run the frontend toolchain, does not use Git index hiding, does
not snapshot/restore prior evidence, and does not self-unlink its
evidence file. Evidence is written only when ``--write-evidence`` is
passed.

    python scripts/ps026_b2_evidence_explorer_smoke.py --local --check-only

It statically validates the PS026 surface without starting a
browser, without calling any provider, without reading any B2 object,
and without enabling broad durable reads.

Truth boundary: this script validates that the PS026 surface
is honest. It does not prove semantic truth, legal authenticity,
C2PA authenticity, or human authorship.

Exit code is 0 only when every check passes.
"""

from __future__ import annotations

import json
import os
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

# PS-026 changed / added files.
B2_EVIDENCE_CONST = REPO_ROOT / "apps" / "web" / "src" / "b2Evidence.ts"
B2_EXPLORER = REPO_ROOT / "apps" / "web" / "src" / "B2EvidenceExplorer.tsx"
HOMEPAGE = REPO_ROOT / "apps" / "web" / "src" / "JudgeCockpitHome.tsx"
APP_TSX = REPO_ROOT / "apps" / "web" / "src" / "App.tsx"
PUBLIC_PASSPORT_PAGE = REPO_ROOT / "apps" / "web" / "src" / "PublicPassportPage.tsx"
STYLES = REPO_ROOT / "apps" / "web" / "src" / "styles.css"
PROOF_DOC = REPO_ROOT / "docs" / "ps-026-b2-evidence-explorer-proof.md"

PS025_SMOKE = REPO_ROOT / "scripts" / "ps025_public_durable_passport_unlock_smoke.py"
PS024_SMOKE = REPO_ROOT / "scripts" / "ps024_golden_demo_run_pinning_smoke.py"
PS023_SMOKE = REPO_ROOT / "scripts" / "ps023_judge_cockpit_home_smoke.py"

EVIDENCE_OUT = REPO_ROOT / "docs" / "evidence" / "ps-026" / "b2-evidence-explorer-smoke.json"

# Files scanned for secrets and forbidden claims. The scanner script itself
# is intentionally excluded: it legitimately contains the detection literals
# (same convention as PS-023/PS-024/PS-025 smokes).
SCAN_FILES: tuple[Path, ...] = (
    B2_EVIDENCE_CONST,
    B2_EXPLORER,
    HOMEPAGE,
    APP_TSX,
    PUBLIC_PASSPORT_PAGE,
    STYLES,
    PROOF_DOC,
)

# Subset of SCAN_FILES that are scanned for forbidden broad-B2-read code
# patterns. Markdown documentation (e.g. the proof doc) legitimately mentions
# these literals when describing what the smoke rejects, so it is excluded.
# Only source code files (ts/tsx/py) are scanned here.
BROAD_B2_READ_SCAN_FILES: tuple[Path, ...] = (
    B2_EVIDENCE_CONST,
    B2_EXPLORER,
    HOMEPAGE,
    APP_TSX,
    PUBLIC_PASSPORT_PAGE,
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
    "proves legal authenticity",
    "proves human authorship",
    "is C2PA verified",
    "C2PA certified",
    "tamper-proof storage",
    "Object Lock",
    "enterprise-grade security",
    "multi-user security",
)

CONTEXT_MARKERS_RE = re.compile(
    r"does not|do not|must not|\bnot\b|non-claim|non-claims|forbidden|"
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
# PS-026 must NOT add code that fetches an arbitrary B2 object from untrusted
# input or builds a B2 URI from arbitrary user input. These literal patterns
# would only appear if PS-026 reintroduced client-side B2 access, which is
# explicitly forbidden by the spec.
BROAD_B2_READ_PATTERNS: tuple[str, ...] = (
    "read_archive_from_b2",
    "b2.fetch",
    "b2GetObject",
    "list_b2_objects",
    "fetchB2Object",
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
# Constant extraction from b2Evidence.ts
# ---------------------------------------------------------------------------

def _extract_string_const(text: str, name: str) -> str | None:
    """Pull a `export const NAME = "...";` value out of b2Evidence.ts."""
    m = re.search(
        r'export\s+const\s+' + re.escape(name) + r'\s*=\s*"((?:[^"\\]|\\.)*)"\s*;',
        text,
    )
    return m.group(1) if m else None


def _extract_number_const(text: str, name: str) -> int | None:
    m = re.search(
        r'export\s+const\s+' + re.escape(name) + r'\s*=\s*(-?\d+)\s*;',
        text,
    )
    return int(m.group(1)) if m else None


def _extract_bool_const(text: Path, name: str) -> bool | None:
    text_str = text.read_text(encoding="utf-8")
    m = re.search(
        r'export\s+const\s+' + re.escape(name) + r'\s*=\s*(true|false)\s*;',
        text_str,
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
    """PS-026 surface exists as a frontend route + component + CTA."""
    problems: list[str] = []
    if not B2_EXPLORER.exists():
        problems.append(f"missing component {rel(B2_EXPLORER)}")
    if not B2_EVIDENCE_CONST.exists():
        problems.append(f"missing constants module {rel(B2_EVIDENCE_CONST)}")

    if APP_TSX.exists():
        app_text = read_text(APP_TSX)
        if "isB2EvidencePath" not in app_text:
            problems.append("App.tsx does not register a /b2-evidence route helper")
        if "/b2-evidence" not in app_text:
            problems.append("App.tsx does not reference the /b2-evidence path")
        if "B2EvidenceExplorer" not in app_text:
            problems.append("App.tsx does not render the B2EvidenceExplorer component")
    else:
        problems.append(f"missing {rel(APP_TSX)}")

    if HOMEPAGE.exists():
        home_text = read_text(HOMEPAGE)
        if "/b2-evidence" not in home_text:
            problems.append("homepage does not link to /b2-evidence")
        if "Open B2 Evidence Explorer" not in home_text:
            problems.append("homepage does not surface a B2 Evidence CTA label")
    else:
        problems.append(f"missing {rel(HOMEPAGE)}")

    if PUBLIC_PASSPORT_PAGE.exists():
        page_text = read_text(PUBLIC_PASSPORT_PAGE)
        if "B2EvidenceExplorer" not in page_text:
            problems.append(
                "PublicPassportPage does not embed the B2 Evidence Explorer"
            )
        if "/b2-evidence" not in page_text:
            problems.append("PublicPassportPage does not link to /b2-evidence")
    else:
        problems.append(f"missing {rel(PUBLIC_PASSPORT_PAGE)}")

    if B2_EXPLORER.exists():
        comp_text = read_text(B2_EXPLORER)
        for required in (
            "B2 Evidence Explorer",
            "GOLDEN_DEMO_ARCHIVE_URI",
            "GOLDEN_DEMO_ARCHIVE_SHA256",
            "GOLDEN_DEMO_REHYDRATE_SOURCE",
            "GOLDEN_DEMO_PROVIDER_CALLS_DURING_REHYDRATE",
            "GOLDEN_DEMO_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE",
            "B2_EVIDENCE_TRUTH_BOUNDARY",
        ):
            if required not in comp_text:
                problems.append(
                    f"B2EvidenceExplorer missing reference to {required!r}"
                )

    return (not problems, problems)


def check_run_id_matches(constants_text: str, manifest: dict) -> tuple[bool, list[str]]:
    got = _extract_string_const(constants_text, "GOLDEN_DEMO_RUN_ID")
    want = manifest.get("run_id")
    if got == want:
        return True, []
    return False, [f"run_id: explorer={got!r} vs manifest={want!r}"]


def check_campaign_id_matches(constants_text: str, manifest: dict) -> tuple[bool, list[str]]:
    got = _extract_string_const(constants_text, "GOLDEN_DEMO_CAMPAIGN_ID")
    want = manifest.get("campaign_id")
    if got == want:
        return True, []
    return False, [f"campaign_id: explorer={got!r} vs manifest={want!r}"]


def check_archive_uri_match(
    constants_text: str, manifest: dict, ps021: dict
) -> tuple[bool, list[str]]:
    got = _extract_string_const(constants_text, "GOLDEN_DEMO_ARCHIVE_URI")
    problems: list[str] = []
    if got != manifest.get("archive_uri"):
        problems.append(
            f"archive_uri: explorer={got!r} vs manifest={manifest.get('archive_uri')!r}"
        )
    if got != ps021.get("archive_uri"):
        problems.append(
            f"archive_uri: explorer={got!r} vs ps021={ps021.get('archive_uri')!r}"
        )
    return (not problems, problems)


def check_archive_sha256_match(
    constants_text: str, manifest: dict, ps021: dict
) -> tuple[bool, list[str]]:
    got = _extract_string_const(constants_text, "GOLDEN_DEMO_ARCHIVE_SHA256")
    problems: list[str] = []
    if got != manifest.get("archive_sha256"):
        problems.append(
            f"archive_sha256: explorer={got!r} vs manifest="
            f"{manifest.get('archive_sha256')!r}"
        )
    if got != ps021.get("archive_sha256"):
        problems.append(
            f"archive_sha256: explorer={got!r} vs ps021="
            f"{ps021.get('archive_sha256')!r}"
        )
    return (not problems, problems)


def check_rehydrate_source(constants_text: str) -> tuple[bool, list[str]]:
    got = _extract_string_const(constants_text, "GOLDEN_DEMO_REHYDRATE_SOURCE")
    if got == "b2_rehydrated":
        return True, []
    return False, [f"rehydrate_source: explorer={got!r}, expected 'b2_rehydrated'"]


def check_provider_calls_zero(constants_text: str) -> tuple[bool, list[str]]:
    got = _extract_number_const(constants_text, "GOLDEN_DEMO_PROVIDER_CALLS_DURING_REHYDRATE")
    if got == 0:
        return True, []
    return False, [
        f"provider_calls_during_rehydrate: explorer={got!r}, expected 0"
    ]


def check_no_live_provider_call() -> tuple[bool, list[str]]:
    got = _extract_bool_const(B2_EVIDENCE_CONST, "GOLDEN_DEMO_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE")
    if got is True:
        return True, []
    return False, [
        f"no_live_provider_call_during_rehydrate: explorer={got!r}, expected True"
    ]


def check_truth_boundary() -> tuple[bool, list[str]]:
    """Truth boundary text is present and carries every required term.

    The const is defined in b2Evidence.ts (possibly via string concatenation)
    and rendered by the B2EvidenceExplorer component. We scan the full source
    text of both files for every required truth-boundary term so the check is
    robust to string-concat styling, and we also confirm the component imports
    the const so the boundary is actually rendered.
    """
    if not B2_EVIDENCE_CONST.exists():
        return False, [f"missing {rel(B2_EVIDENCE_CONST)}"]
    const_text = read_text(B2_EVIDENCE_CONST)
    # The const must be declared in the constants module.
    if "B2_EVIDENCE_TRUTH_BOUNDARY" not in const_text:
        return False, ["B2_EVIDENCE_TRUTH_BOUNDARY const is not declared"]
    # Every required truth-boundary term must appear in the module text
    # (inside the const definition, regardless of string-concat styling).
    missing_in_const = [
        t for t in TRUTH_BOUNDARY_TERMS if t.lower() not in const_text.lower()
    ]
    if missing_in_const:
        return False, [
            f"b2Evidence.ts truth boundary missing term {missing_in_const[0]!r}"
        ]
    # The component must import and render the const.
    if not B2_EXPLORER.exists():
        return False, [f"missing {rel(B2_EXPLORER)}"]
    comp = read_text(B2_EXPLORER)
    if "B2_EVIDENCE_TRUTH_BOUNDARY" not in comp:
        return False, [
            "B2EvidenceExplorer does not import the truth boundary const"
        ]
    return True, []


def check_no_broad_b2_read() -> tuple[bool, list[str]]:
    """No new broad B2 object read path is introduced.

    Two parts:
      (a) PS-026 source files must not contain any literal broad B2 read API
          call (client-side fetch / arbitrary B2 object lookup).
      (b) An arbitrary run_id still 404s through the public durable passport
          path -- the PS-025 narrow allowlist must still hold.
    """
    problems: list[str] = []
    for path in BROAD_B2_READ_SCAN_FILES:
        if not path.exists():
            continue
        text = read_text(path)
        for pattern in BROAD_B2_READ_PATTERNS:
            if pattern in text:
                problems.append(
                    f"{rel(path)}: forbidden B2 read pattern {pattern!r}"
                )

    arbitrary_run_id = "run_ps026_must_still_404_0123456789abcdef"
    status = _get_passport_status(arbitrary_run_id)
    if status != 404:
        problems.append(
            f"arbitrary run id returned HTTP {status}, expected 404 "
            f"(broad public durable read must stay blocked)"
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
    unlock = passport.get("golden_demo_unlock") or {}
    archive = passport.get("archive_and_rehydration") or {}
    problems: list[str] = []
    if unlock.get("run_id") != golden_run_id:
        problems.append("API unlock run_id drift")
    if unlock.get("archive_uri") != manifest.get("archive_uri"):
        problems.append("API unlock archive_uri drift")
    if unlock.get("archive_sha256") != manifest.get("archive_sha256"):
        problems.append("API unlock archive_sha256 drift")
    if unlock.get("provider_calls_during_rehydrate") != 0:
        problems.append("API unlock provider_calls drift")
    if unlock.get("no_live_provider_call_during_rehydrate") is not True:
        problems.append("API unlock no_live_provider_call drift")
    if archive.get("rehydrate_source") != "b2_rehydrated":
        problems.append("API archive rehydrate_source drift")
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
    """No prior-slice evidence file is left modified by the PS-026 smoke run.

    Regression smokes (PS-025 in particular) rewrite their own evidence JSON
    with a fresh timestamp on every run. PS-026 snapshots and restores those
    files around the regression subprocesses; this check independently confirms
    via git that no prior historical predecessor evidence is left dirty.
    PS-026 owns only its own evidence output.
    """
    problems = sl.prior_evidence_dirty_problems(
        own_slice_prefix="docs/evidence/ps-026/",
        slice_label="PS-026",
    )
    return (not problems, problems)


def run(argv=None) -> int:
    opts = sl.parse_slice_smoke_cli(argv)
    missing_inputs: list[str] = []
    for p in (
        MANIFEST,
        PS021_EVIDENCE,
        PS025_EVIDENCE,
    ):
        if not p.exists():
            missing_inputs.append(rel(p))
    if missing_inputs:
        print("PS026 smoke: MISSING INPUT FILES")
        for f in missing_inputs:
            print(f"  - {f}")
        return 1

    manifest = load_json(MANIFEST)
    ps021 = load_json(PS021_EVIDENCE)
    ps025 = load_json(PS025_EVIDENCE)
    constants_text = read_text(B2_EVIDENCE_CONST) if B2_EVIDENCE_CONST.exists() else ""

    checks: list[tuple[str, tuple[bool, list[str]]]] = [
        ("surface_exists", check_surface_exists()),
        ("run_id_matches", check_run_id_matches(constants_text, manifest)),
        ("campaign_id_matches", check_campaign_id_matches(constants_text, manifest)),
        ("archive_uri_match", check_archive_uri_match(constants_text, manifest, ps021)),
        ("archive_sha256_match", check_archive_sha256_match(constants_text, manifest, ps021)),
        ("rehydrate_source", check_rehydrate_source(constants_text)),
        ("provider_calls_zero", check_provider_calls_zero(constants_text)),
        ("no_live_provider_call", check_no_live_provider_call()),
        ("truth_boundary", check_truth_boundary()),
        ("no_broad_b2_read", check_no_broad_b2_read()),
        ("secret_scan", check_secrets()),
        ("forbidden_claims", check_forbidden_claims()),
        ("api_resolves_golden", check_api_resolves_golden(manifest)),
    ]

    all_pass, detail = sl.run_contract_checks("PS-026 B2 Evidence Explorer", checks)

    if opts.write_evidence:
        evidence = {
            "ok": bool(all_pass),
            "route_or_surface": "/b2-evidence (dedicated frontend route) + "
            "B2EvidenceExplorer section embedded in /passport/<golden_run_id> + "
            "CTAs from Judge Cockpit Home and the Public Passport hero",
            "run_id": manifest.get("run_id"),
            "campaign_id": manifest.get("campaign_id"),
            "archive_uri": manifest.get("archive_uri"),
            "archive_sha256": manifest.get("archive_sha256"),
            "rehydrate_source": "b2_rehydrated",
            "provider_calls_during_rehydrate": 0,
            "no_live_provider_call_during_rehydrate": True,
            "truth_boundary_present": bool(
                check_truth_boundary()[0]
            ),
            "source_manifest": rel(MANIFEST),
            "source_ps025_evidence": rel(PS025_EVIDENCE),
            "source_ps021_evidence": rel(PS021_EVIDENCE),
            "frontend_surface_verified": bool(
                check_surface_exists()[0]
            ),
            "api_surface_verified": bool(
                check_api_resolves_golden(manifest)[0]
            ),
            "no_broad_b2_read": bool(check_no_broad_b2_read()[0]),
            "public_deployment_pending": bool(public_deployment_pending),
            "local_contract_proof": local_contract_proof,
            "public_deployment_verified": public_deployment_verified,
            "checked_at": _utc_now_iso(),
            "api_transport": "testclient",
            "checks": detail,
            "truth_boundary": (
                "PS-026 proves the B2 Evidence Explorer surfaces the verified "
                "durable evidence (archive URI, SHA-256, rehydrate source, zero "
                "provider calls during rehydrate) recorded by PS-021 and pinned by "
                "PS-024/PS-025, without calling any provider, without reading any "
                "B2 object, and without enabling broad durable reads. It does not "
                "prove semantic truth, legal authenticity, C2PA authenticity, or "
                "human authorship. The local contract is verified; the public "
                "deployment remains pending until the new backend is deployed and "
                "the public URL is verified end-to-end."
            ),
        }
        sl.write_json_atomic(EVIDENCE_OUT, evidence)
        print(f"evidence: {rel(EVIDENCE_OUT)}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(run())
