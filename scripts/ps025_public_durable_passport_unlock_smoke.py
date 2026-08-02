#!/usr/bin/env python3
"""PS-025 Public Durable Passport Unlock -- smoke / validation script.

This is the canonical PS-025 validation command (safe local/check mode):

    python scripts/ps025_public_durable_passport_unlock_smoke.py --local --check-only

It validates the narrowest safe public durable passport unlock for the single
verified golden demo run, without rerunning providers, without enabling broad
public durable reads, and without faking a public deployment that was not
tested.

PS-034B retrofit: this smoke now defaults to safe local / check-only behavior.
It no longer recursively executes prior slice smokes. Any optional live /
network URL path is gated behind an explicit ``--live`` flag and is never used
by default. Evidence is written only when ``--write-evidence`` is passed.

It performs these checks (local / check mode):

 1. manifest_exists       -- the golden demo manifest exists and carries the
                             required durable evidence fields.
 2. api_resolves_golden   -- GET /runs/<golden_run_id>/passport resolves (via
                             FastAPI TestClient) with HTTP 200.
 3. run_id_matches        -- returned run_id matches the PS-024 golden manifest.
 4. campaign_id_matches   -- returned campaign_id matches the PS-024 manifest.
 5. archive_match         -- returned archive_uri and archive_sha256 match the
                             PS-024 manifest AND the PS-021 source evidence.
 6. provider_calls_zero   -- provider_calls_during_rehydrate equals 0.
 7. no_live_provider_call -- no_live_provider_call_during_rehydrate is true.
 8. truth_boundary        -- the response carries the truth boundary text.
 9. no_broad_durable_read -- an arbitrary run id still returns 404 (no broad
                             public durable read is enabled).
10. homepage_links        -- the judge cockpit homepage links to the golden
                             passport only because the unlock is verified.
11. secret_scan           -- changed PS-025 files contain no secrets.
12. forbidden_claims      -- no forbidden affirmative claim is asserted outside a
                             non-claim / negation context.

Public deployment honesty: this smoke proves the LOCAL contract (FastAPI
TestClient against a fresh empty store). The public Render deployment is NOT
tested here unless ``--live`` is explicitly passed with a configured base URL.

Truth boundary: this script validates that the PS-025 unlock is honest and
narrow. It does not prove semantic truth, legal authenticity, C2PA
authenticity, or human authorship.

Exit code is 0 only when every check passes.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

sys.path.insert(0, str(Path(__file__).resolve().parent))
import smoke_lib as sl  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

MANIFEST = REPO_ROOT / "docs" / "evidence" / "demo" / "golden-demo-run.json"
PS021_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "ps-021" / "live-b2-durable-rehydrate-smoke.json"
HOMEPAGE = REPO_ROOT / "apps" / "web" / "src" / "JudgeCockpitHome.tsx"
PROOF_DOC = REPO_ROOT / "docs" / "ps-025-public-durable-passport-unlock-proof.md"
DURABLE_PASSPORT_PY = REPO_ROOT / "src" / "proofstudio" / "api" / "durable_passport.py"
SERVICES_PY = REPO_ROOT / "src" / "proofstudio" / "api" / "services.py"
EVIDENCE_OUT = REPO_ROOT / "docs" / "evidence" / "ps-025" / "public-durable-passport-unlock-smoke.json"
PS024_SMOKE = REPO_ROOT / "scripts" / "ps024_golden_demo_run_pinning_smoke.py"
PS023_SMOKE = REPO_ROOT / "scripts" / "ps023_judge_cockpit_home_smoke.py"

# Files scanned for secrets and forbidden claims. The scanner script itself
# is intentionally excluded: it legitimately contains the detection literals
# (same convention as the PS-023/PS-024 smokes).
SCAN_FILES: tuple[Path, ...] = (
    HOMEPAGE,
    PROOF_DOC,
    DURABLE_PASSPORT_PY,
    SERVICES_PY,
)

# Configured public API base URL. When set, the smoke hits the live API instead
# of the in-process TestClient (used to verify a real public deployment). When
# unset, the LOCAL contract is proven via TestClient and public deployment is
# recorded as pending.
API_BASE_ENV = "PROOFSTUDIO_PS025_API_BASE_URL"

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
# API access: TestClient (local contract) or configured base URL (public).
# ---------------------------------------------------------------------------

def _get_passport_json(
    run_id: str, *, live: bool = False
) -> tuple[int, dict[str, Any] | None, str]:
    """Return (status_code, parsed_json_or_None, transport) for the passport route.

    PS-034B: the live/network URL path is used ONLY when ``live`` is True.
    By default the LOCAL in-process TestClient contract is exercised.
    """
    if live:
        base = os.environ.get(API_BASE_ENV, "").strip()
        if base:
            base = base.rstrip("/")
            url = f"{base}/runs/{run_id}/passport"
            try:
                req = Request(url, headers={"Accept": "application/json"})
                with urlopen(req, timeout=20) as resp:  # noqa: S310 - configured base
                    status = resp.status
                    body = resp.read().decode("utf-8")
            except HTTPError as exc:
                return exc.code, None, f"live:{base}"
            except URLError:
                return 0, None, f"live:{base}"
            try:
                return status, json.loads(body) if body else None, f"live:{base}"
            except json.JSONDecodeError:
                return status, None, f"live:{base}"

    # Local contract: in-process TestClient against a fresh empty store.
    from fastapi.testclient import TestClient  # type: ignore

    from proofstudio.api.app import create_app
    from proofstudio.api.services import create_default_service

    app = create_app(create_default_service())
    client = TestClient(app)
    response = client.get(f"/runs/{run_id}/passport")
    parsed: dict[str, Any] | None = None
    try:
        parsed = response.json() if response.text else None
    except Exception:
        parsed = None
    return response.status_code, parsed, "testclient"


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_manifest_exists(manifest: dict) -> tuple[bool, list[str]]:
    required = ("run_id", "campaign_id", "archive_uri", "archive_sha256")
    missing = [f for f in required if not manifest.get(f)]
    return (not missing, [f"manifest missing required field {f!r}" for f in missing])


def check_api_resolves_golden(status: int) -> tuple[bool, list[str]]:
    if status == 200:
        return True, []
    return False, [f"golden passport route returned HTTP {status}, expected 200"]


def check_run_id_matches(passport: dict, manifest: dict) -> tuple[bool, list[str]]:
    got = (passport.get("passport_identity") or {}).get("run_id")
    want = manifest.get("run_id")
    if got == want:
        return True, []
    return False, [f"run_id: got {got!r}, expected {want!r}"]


def check_campaign_id_matches(passport: dict, manifest: dict) -> tuple[bool, list[str]]:
    got = (passport.get("passport_identity") or {}).get("campaign_id")
    want = manifest.get("campaign_id")
    if got == want:
        return True, []
    return False, [f"campaign_id: got {got!r}, expected {want!r}"]


def check_archive_match(passport: dict, manifest: dict, ps021: dict) -> tuple[bool, list[str]]:
    archive = passport.get("archive_and_rehydration") or {}
    problems: list[str] = []
    for field in ("archive_uri", "archive_sha256"):
        got = archive.get(field)
        want_manifest = manifest.get(field)
        want_evidence = ps021.get(field)
        if got != want_manifest:
            problems.append(f"{field}: passport={got!r} vs manifest={want_manifest!r}")
        if got != want_evidence:
            problems.append(f"{field}: passport={got!r} vs ps021_evidence={want_evidence!r}")
    return (not problems, problems)


def check_provider_calls_zero(passport: dict) -> tuple[bool, list[str]]:
    unlock = passport.get("golden_demo_unlock") or {}
    value = unlock.get("provider_calls_during_rehydrate")
    if value == 0:
        return True, []
    return False, [f"provider_calls_during_rehydrate: got {value!r}, expected 0"]


def check_no_live_provider_call(passport: dict) -> tuple[bool, list[str]]:
    archive = passport.get("archive_and_rehydration") or {}
    unlock = passport.get("golden_demo_unlock") or {}
    archive_flag = archive.get("no_live_provider_call_during_rehydrate")
    unlock_flag = unlock.get("no_live_provider_call_during_rehydrate")
    if archive_flag is True and unlock_flag is True:
        return True, []
    return False, [
        f"no_live_provider_call_during_rehydrate: archive={archive_flag!r}, "
        f"unlock={unlock_flag!r}, both must be true"
    ]


def check_truth_boundary(passport: dict) -> tuple[bool, list[str]]:
    tb = passport.get("truth_boundary")
    if not isinstance(tb, str) or not tb:
        return False, ["passport truth_boundary is missing or not a string"]
    missing = [t for t in TRUTH_BOUNDARY_TERMS if t.lower() not in tb.lower()]
    if missing:
        return False, [f"truth_boundary missing term {missing[0]!r}"]
    return True, []


def check_no_broad_durable_read(status_arbitrary: int) -> tuple[bool, list[str]]:
    # An arbitrary run id MUST NOT resolve through the public durable path.
    # 404 is the honest, safe outcome. Anything else means broad reads leaked.
    if status_arbitrary == 404:
        return True, []
    return False, [
        f"arbitrary run id returned HTTP {status_arbitrary}, expected 404 "
        f"(broad public durable read must stay blocked)"
    ]


def check_homepage_links(manifest: dict, golden_resolved: bool) -> tuple[bool, list[str]]:
    text = read_text(HOMEPAGE)
    problems: list[str] = []
    golden_run_id = manifest.get("run_id")
    if not golden_run_id or golden_run_id not in text:
        problems.append("homepage does not reference the golden run_id")
    # The link must be dynamic (built from a constant), never a literal pinned
    # href, so no fabricated URL is hard-coded.
    if re.search(r'href="/passport/run_[a-f0-9]+"', text):
        problems.append("homepage contains a literal pinned /passport/run_... href")
    if "goldenPassportHref" not in text and "GOLDEN_DEMO_RUN_ID" not in text:
        problems.append("homepage does not build a dynamic golden passport href")
    if not golden_resolved:
        problems.append("homepage links to golden passport but the route did not resolve")
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
# Runner
# ---------------------------------------------------------------------------

def run(argv: list[str] | None = None) -> int:
    opts = sl.parse_slice_smoke_cli(argv, allow_live=True)
    missing_inputs: list[str] = []
    for p in (MANIFEST, PS021_EVIDENCE, HOMEPAGE):
        if not p.exists():
            missing_inputs.append(rel(p))
    if missing_inputs:
        print("PS-025 smoke: MISSING INPUT FILES")
        for f in missing_inputs:
            print(f"  - {f}")
        return 1

    manifest = load_json(MANIFEST)
    ps021 = load_json(PS021_EVIDENCE)
    golden_run_id = manifest.get("run_id")

    # PS-034B: live/network path is used only when --live is explicitly passed.
    golden_status, golden_passport, transport = _get_passport_json(
        golden_run_id, live=opts.live
    )
    arbitrary_run_id = "run_ps025_does_not_exist_0123456789abcdef"
    arbitrary_status, _arbitrary_body, _ = _get_passport_json(
        arbitrary_run_id, live=opts.live
    )

    golden_resolved = (
        golden_status == 200 and isinstance(golden_passport, dict)
    )
    passport_for_checks = golden_passport if golden_resolved else {}

    pre_checks: list[tuple[str, tuple[bool, list[str]]]] = [
        ("manifest_exists", check_manifest_exists(manifest)),
        ("api_resolves_golden", check_api_resolves_golden(golden_status)),
        ("no_broad_durable_read", check_no_broad_durable_read(arbitrary_status)),
        ("homepage_links", check_homepage_links(manifest, golden_resolved)),
        ("secret_scan", check_secrets()),
        ("forbidden_claims", check_forbidden_claims()),
    ]

    if golden_resolved:
        contract_checks: list[tuple[str, tuple[bool, list[str]]]] = [
            ("run_id_matches", check_run_id_matches(passport_for_checks, manifest)),
            ("campaign_id_matches", check_campaign_id_matches(passport_for_checks, manifest)),
            ("archive_match", check_archive_match(passport_for_checks, manifest, ps021)),
            ("provider_calls_zero", check_provider_calls_zero(passport_for_checks)),
            ("no_live_provider_call", check_no_live_provider_call(passport_for_checks)),
            ("truth_boundary", check_truth_boundary(passport_for_checks)),
        ]
    else:
        contract_checks = [
            ("run_id_matches", (False, ["skipped: golden passport did not resolve"])),
            ("campaign_id_matches", (False, ["skipped: golden passport did not resolve"])),
            ("archive_match", (False, ["skipped: golden passport did not resolve"])),
            ("provider_calls_zero", (False, ["skipped: golden passport did not resolve"])),
            ("no_live_provider_call", (False, ["skipped: golden passport did not resolve"])),
            ("truth_boundary", (False, ["skipped: golden passport did not resolve"])),
        ]

    checks = pre_checks + contract_checks
    all_pass, detail = sl.run_contract_checks(
        "PS-025 Public Durable Passport Unlock", checks
    )

    if opts.write_evidence:
        local_contract_proof = golden_resolved and all(
            ok for _name, (ok, _p) in contract_checks
        )
        unlock = (passport_for_checks.get("golden_demo_unlock") or {}) if golden_resolved else {}
        archive = (passport_for_checks.get("archive_and_rehydration") or {}) if golden_resolved else {}
        evidence = {
            "ok": bool(all_pass),
            "run_id": golden_run_id,
            "campaign_id": manifest.get("campaign_id"),
            "archive_uri": archive.get("archive_uri") or manifest.get("archive_uri"),
            "archive_sha256": archive.get("archive_sha256") or manifest.get("archive_sha256"),
            "rehydrate_source": unlock.get("rehydrate_source") or manifest.get("rehydrate_source"),
            "provider_calls_during_rehydrate": unlock.get(
                "provider_calls_during_rehydrate"
            ),
            "no_live_provider_call_during_rehydrate": (
                bool(unlock.get("no_live_provider_call_during_rehydrate"))
                if golden_resolved
                else None
            ),
            "no_broad_public_durable_read": arbitrary_status == 404,
            "source_manifest": rel(MANIFEST),
            "checked_at": _utc_now_iso(),
            "local_contract_proof": bool(local_contract_proof),
            "public_deployment_pending": not opts.live,
            "api_transport": transport,
            "checks": detail,
            "truth_boundary": (
                "PS-025 proves the golden demo run resolves as a public durable "
                "passport from checked-in evidence with zero provider calls and "
                "no broad public durable read. It does not prove semantic truth, "
                "legal authenticity, C2PA authenticity, or human authorship."
            ),
        }
        sl.write_json_atomic(EVIDENCE_OUT, evidence)
        print(f"evidence: {rel(EVIDENCE_OUT)}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(run())
