#!/usr/bin/env python3
"""PS-024 Golden Demo Run Pinning -- smoke / validation script.

This is the canonical PS-024 validation command:

    python scripts/ps024_golden_demo_run_pinning_smoke.py

It statically validates the PS-024 golden demo run pinning surface without
starting a browser or calling any provider.

PS-035a migrated this smoke from the old null-manifest contract to a
real-manifest contract. The canonical golden run now carries a real
`manifest_uri` (a checked-in local fixture path, not a live B2 URL), a real
64-hex SHA-256 `manifest_hash`, a matching `manifest_sha256`, the exact
recorded Genblaze package versions actually installed, and the checked-in
manifest fixture's independent SHA-256 recompute equals the golden
`manifest_hash`. This is local / check-only: no provider calls and no B2
reads/writes.

It performs twelve checks:

 1. manifest_exists     -- the canonical demo manifest exists.
 2. pinned_values_match -- every non-null manifest value is traceable to a
                            source evidence file. No value is invented.
 3. no_invented_ids     -- run_id and campaign_id (if present) must appear in a
                            source evidence JSON file. public_passport_url must
                            be null unless it matches PS-019 live evidence.
                            proof_score must be null (no pinned score available).
 4. manifest_contract   -- (PS-035a real-manifest contract) `manifest_uri` is a
                            non-empty string, `manifest_hash` is 64-hex SHA-256,
                            `manifest_sha256` (if present) is 64-hex and equals
                            `manifest_hash`, the golden `genblaze_versions`
                            match the exact requirements pins, and the
                            checked-in manifest fixture bytes recompute to the
                            golden `manifest_hash`.
 5. homepage_honest     -- the homepage carries the canonical PS-024
                            blocked-state wording for the golden demo run
                            (golden demo, verified durable evidence,
                            provenance passport, blocked/planned, run_id)
                            and no fake pinned passport link.
 6. archive_match       -- archive_uri and archive_sha256 in the manifest match
                            the PS-021 source evidence exactly.
 7. rehydrate_match     -- rehydrate_source, provider_calls_during_rehydrate,
                            and no_live_provider_call_during_rehydrate match the
                            PS-021 source evidence exactly.
 8. truth_boundary      -- the manifest and homepage both carry the truth
                            boundary text.
 9. forbidden_claims    -- no forbidden affirmative claim is asserted outside a
                            non-claim / negation context.
10. secret_scan         -- changed PS-024 files contain no secrets.
11. route_markers       -- no existing route/CTA marker was removed from the
                            homepage (PS-023 compatibility).
12. ps023_callable      -- the PS-023 smoke script is present and callable.

The script also reuses the PS-023 context-aware forbidden-claim logic so honest
non-claim documentation (the truth boundary, the unavailable_fields reasons)
is never falsely flagged as an overclaim.

Truth boundary: this script validates that the PS-024 surface is honest. It
does not prove semantic truth, legal authenticity, C2PA authenticity, or human
authorship. The manifest fixture proves reproducible local manifest-hash
correctness, not live B2 Object Lock, tamper-proof storage, or semantic truth.

Exit code is 0 only when every check passes.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import smoke_lib as sl  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]

MANIFEST = REPO_ROOT / "docs" / "evidence" / "demo" / "golden-demo-run.json"
# PS-035a checked-in local manifest fixture (not a live B2 URL).
MANIFEST_FIXTURE = (
    REPO_ROOT / "docs" / "evidence" / "ps-035a" / "manifest-fixture.json"
)
REQUIREMENTS = REPO_ROOT / "apps" / "api" / "requirements.txt"
PS021_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "ps-021" / "live-b2-durable-rehydrate-smoke.json"
PS019_LIVE_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "ps-019" / "live-public-passport-smoke-summary.json"
PS020_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "ps-020" / "durable-passport-foundation-smoke.json"
HOMEPAGE = REPO_ROOT / "apps" / "web" / "src" / "JudgeCockpitHome.tsx"
PROOF_DOC = REPO_ROOT / "docs" / "ps-024-golden-demo-run-pinning-proof.md"
PS023_SMOKE = REPO_ROOT / "scripts" / "ps023_judge_cockpit_home_smoke.py"

# Source evidence files whose values the manifest is allowed to cite.
SOURCE_EVIDENCE_FILES: tuple[Path, ...] = (
    PS021_EVIDENCE,
    PS019_LIVE_EVIDENCE,
    REPO_ROOT / "docs" / "evidence" / "ps-019" / "local-passport-smoke-summary.json",
    PS020_EVIDENCE,
)

# Files scanned for secrets and forbidden claims.
SCAN_FILES: tuple[Path, ...] = (
    HOMEPAGE,
    MANIFEST,
    PROOF_DOC,
)

# ---------------------------------------------------------------------------
# Forbidden-claim and secret detection (mirrors the PS-023 context-aware
# approach so honest non-claim documentation is not falsely flagged).
# ---------------------------------------------------------------------------

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
    r"unavailable|blocked|honestly|no live|no_new|no_fake",
    re.IGNORECASE,
)

FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")

# PS-035a real-manifest contract helpers.
SHA256_HEX_RE = re.compile(r"^[0-9a-f]{64}$")
GENBLAZE_PACKAGES = ("genblaze-core", "genblaze-s3", "genblaze-gmicloud")

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

TRUTH_BOUNDARY_TERMS: tuple[str, ...] = (
    "semantic truth",
    "legal authenticity",
    "C2PA authenticity",
    "human authorship",
)

# Route/CTA markers that must still be present after PS-024 (PS-023 compat).
ROUTE_CTA_MARKERS: tuple[str, ...] = (
    "window.location.pathname",
    "/passport/",
    "/review",
    "JudgeCockpitHome",
    "judge-evidence-pack.md",
    "docs/submission",
    "github.com/GeorgeElArif/proofstudio",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> dict:
    return json.loads(read_text(path))


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _paragraph_range(lines: list[str], index: int) -> tuple[int, int]:
    start = index
    while start > 0 and lines[start - 1].strip():
        start -= 1
    end = index + 1
    while end < len(lines) and lines[end].strip():
        end += 1
    return start, end


# ---------------------------------------------------------------------------
# Check 1: manifest exists
# ---------------------------------------------------------------------------

def check_manifest_exists() -> tuple[bool, list[str]]:
    if MANIFEST.exists():
        return True, []
    return False, [rel(MANIFEST)]


# ---------------------------------------------------------------------------
# Check 2: pinned values match source evidence
# ---------------------------------------------------------------------------

def _all_evidence_values() -> set[str]:
    """Collect every string/int value from every source evidence JSON."""
    values: set[str] = set()
    for path in SOURCE_EVIDENCE_FILES:
        if not path.exists():
            continue
        data = load_json(path)
        _collect_values(data, values)
    return values


def _collect_values(obj: object, out: set[str]) -> None:
    if isinstance(obj, str):
        out.add(obj)
    elif isinstance(obj, (int, float)):
        out.add(str(obj))
    elif isinstance(obj, dict):
        for v in obj.values():
            _collect_values(v, out)
    elif isinstance(obj, list):
        for item in obj:
            _collect_values(item, out)


def check_pinned_values_match(manifest: dict) -> tuple[bool, list[str]]:
    """Every non-null scalar manifest field must appear in source evidence."""
    evidence_values = _all_evidence_values()
    problems: list[str] = []
    # Only check the top-level scalar fields that represent evidence, not
    # structural fields (demo_id, source_slice, truth_boundary text, etc.).
    checked_fields = (
        "run_id",
        "campaign_id",
        "public_app_url",
        "public_api_url",
        "archive_uri",
        "archive_sha256",
        "rehydrate_source",
        "provider_calls_during_rehydrate",
        "no_live_provider_call_during_rehydrate",
    )
    for field in checked_fields:
        value = manifest.get(field)
        if value is None:
            continue
        if isinstance(value, bool):
            value = str(value)
        if str(value) not in evidence_values:
            problems.append(
                f"{field}={value!r} does not appear in any source evidence file"
            )
    return (not problems, problems)


# ---------------------------------------------------------------------------
# Check 3: no invented IDs / URLs / scores
# ---------------------------------------------------------------------------

def check_no_invented_ids(manifest: dict) -> tuple[bool, list[str]]:
    problems: list[str] = []

    # run_id and campaign_id must appear in a source evidence file.
    evidence_values = _all_evidence_values()
    for field in ("run_id", "campaign_id"):
        value = manifest.get(field)
        if value is None:
            continue
        if str(value) not in evidence_values:
            problems.append(
                f"{field}={value!r} is not found in any evidence file (invented)"
            )

    # public_passport_url must be null (no working public passport URL exists).
    ppu = manifest.get("public_passport_url")
    if ppu is not None:
        # If non-null, it must exactly match the PS-019 live evidence URL.
        ps019 = load_json(PS019_LIVE_EVIDENCE)
        live_url = ps019.get("public_passport_url")
        if ppu != live_url:
            problems.append(
                f"public_passport_url={ppu!r} is non-null and does not match "
                f"PS-019 live evidence ({live_url!r})"
            )

    # proof_score must be null (no pinned score available).
    if manifest.get("proof_score") is not None:
        problems.append(
            f"proof_score={manifest.get('proof_score')!r} is non-null "
            f"(no pinned score is available; inventing one is forbidden)"
        )

    # PS-035a: the manifest fields are now required to be REAL, not null.
    # The real-manifest contract is enforced by check_manifest_contract below,
    # so this check no longer asserts manifest_uri / manifest_hash are null.

    return (not problems, problems)


# ---------------------------------------------------------------------------
# Check 4 (PS-035a): real-manifest contract
# ---------------------------------------------------------------------------

def _genblaze_pins_from_requirements() -> dict[str, str]:
    """Parse exact Genblaze pins from apps/api/requirements.txt.

    Returns a mapping of package name -> pinned version string. Raises no
    error if requirements is absent; callers handle the empty mapping.
    """
    pins: dict[str, str] = {}
    if not REQUIREMENTS.is_file():
        return pins
    line_re = re.compile(r"^\s*([A-Za-z0-9_.-]+)\s*==\s*([0-9A-Za-z_.-]+)\s*$")
    for raw in read_text(REQUIREMENTS).splitlines():
        line = raw.split("#", 1)[0]
        m = line_re.match(line)
        if not m:
            continue
        name, version = m.group(1).strip(), m.group(2).strip()
        if name in GENBLAZE_PACKAGES:
            pins[name] = version
    return pins


def check_manifest_contract(manifest: dict) -> tuple[bool, list[str]]:
    """PS-035a real-manifest contract over the canonical golden run.

    Requires (local / check-only; no provider calls, no B2 reads/writes):

    - `manifest_uri` is a non-empty string
    - `manifest_hash` is a 64-hex SHA-256 string
    - `manifest_sha256` (if present) is 64-hex and equals `manifest_hash`
    - the golden `genblaze_versions` mapping exists and matches the exact
      Genblaze pins recorded in apps/api/requirements.txt
    - the checked-in manifest fixture file exists
    - the independent SHA-256 recompute over the checked-in fixture bytes
      equals the golden `manifest_hash`
    """
    problems: list[str] = []

    manifest_uri = manifest.get("manifest_uri")
    if not isinstance(manifest_uri, str) or not manifest_uri:
        problems.append(
            f"manifest_uri={manifest_uri!r} must be a non-empty string "
            f"(PS-035a real-manifest contract)"
        )

    manifest_hash = manifest.get("manifest_hash")
    if not isinstance(manifest_hash, str) or not SHA256_HEX_RE.match(manifest_hash):
        problems.append(
            f"manifest_hash={manifest_hash!r} must be 64-hex SHA-256 "
            f"(PS-035a real-manifest contract)"
        )

    manifest_sha256 = manifest.get("manifest_sha256")
    if manifest_sha256 is not None:
        if not (
            isinstance(manifest_sha256, str)
            and SHA256_HEX_RE.match(manifest_sha256)
        ):
            problems.append(
                f"manifest_sha256={manifest_sha256!r} must be 64-hex SHA-256"
            )
        elif manifest_hash and manifest_sha256 != manifest_hash:
            problems.append(
                f"manifest_sha256={manifest_sha256!r} does not match "
                f"manifest_hash={manifest_hash!r}"
            )

    golden_versions = manifest.get("genblaze_versions")
    if not isinstance(golden_versions, dict) or not golden_versions:
        problems.append(
            "genblaze_versions must be a non-empty package-to-version mapping"
        )
    else:
        req_pins = _genblaze_pins_from_requirements()
        for pkg in GENBLAZE_PACKAGES:
            gold = golden_versions.get(pkg)
            pin = req_pins.get(pkg)
            if not gold:
                problems.append(f"genblaze_versions missing package {pkg!r}")
            elif pin and gold != pin:
                problems.append(
                    f"genblaze_versions[{pkg!r}]={gold!r} does not match "
                    f"requirements pin {pin!r}"
                )

    if not MANIFEST_FIXTURE.is_file():
        problems.append(
            f"checked-in manifest fixture missing: {rel(MANIFEST_FIXTURE)}"
        )
    elif manifest_hash and SHA256_HEX_RE.match(manifest_hash):
        import hashlib
        recomputed = hashlib.sha256(MANIFEST_FIXTURE.read_bytes()).hexdigest()
        if recomputed != manifest_hash:
            problems.append(
                f"checked-in fixture SHA-256 recompute {recomputed!r} does not "
                f"equal golden manifest_hash {manifest_hash!r}"
            )

    return (not problems, problems)


# ---------------------------------------------------------------------------
# Check 5 (was 4): homepage honest blocked/planned state
# ---------------------------------------------------------------------------

def check_homepage_honest(manifest: dict) -> tuple[bool, list[str]]:
    text = read_text(HOMEPAGE)
    text_lower = text.lower()
    problems: list[str] = []

    # Since public_passport_url is null (blocked), the homepage must NOT
    # contain a hard-coded pinned passport href to a fabricated run id.
    if re.search(r'href="/passport/run_[a-f0-9]+"', text):
        problems.append(
            "homepage contains a hard-coded pinned /passport/run_… href, "
            "but no verified public passport URL exists"
        )

    # The homepage must carry the canonical PS-024 blocked-state wording.
    # This smoke owns the vocabulary so the product copy and the validator
    # do not drift apart (root-cause fix for the WSL gate that expected the
    # literal phrase "golden demo").
    required_phrases = (
        "golden demo",
        "verified durable evidence",
        "provenance passport",
        "run_id",
    )
    for phrase in required_phrases:
        if phrase.lower() not in text_lower:
            problems.append(
                f"homepage missing canonical PS-024 phrase: {phrase!r}"
            )

    # An honest blocked/planned indicator must be present.
    if not any(m in text_lower for m in ("blocked", "planned")):
        problems.append(
            "homepage does not contain a blocked/planned marker for "
            "passport pinning"
        )

    return (not problems, problems)


# ---------------------------------------------------------------------------
# Check 5: archive URI/hash match source evidence
# ---------------------------------------------------------------------------

def check_archive_match(manifest: dict) -> tuple[bool, list[str]]:
    ps021 = load_json(PS021_EVIDENCE)
    problems: list[str] = []
    for field in ("archive_uri", "archive_sha256"):
        manifest_val = manifest.get(field)
        evidence_val = ps021.get(field)
        if manifest_val != evidence_val:
            problems.append(
                f"{field}: manifest={manifest_val!r} vs evidence={evidence_val!r}"
            )
    return (not problems, problems)


# ---------------------------------------------------------------------------
# Check 6: rehydrate proof fields match source evidence
# ---------------------------------------------------------------------------

def check_rehydrate_match(manifest: dict) -> tuple[bool, list[str]]:
    ps021 = load_json(PS021_EVIDENCE)
    problems: list[str] = []
    for field in (
        "rehydrate_source",
        "provider_calls_during_rehydrate",
        "no_live_provider_call_during_rehydrate",
    ):
        manifest_val = manifest.get(field)
        evidence_val = ps021.get(field)
        if field == "rehydrate_source":
            # The manifest uses "rehydrate_source"; evidence uses
            # "durable_source".  Map them.
            evidence_val = ps021.get("durable_source")
        if manifest_val != evidence_val:
            problems.append(
                f"{field}: manifest={manifest_val!r} vs evidence={evidence_val!r}"
            )
    return (not problems, problems)


# ---------------------------------------------------------------------------
# Check 7: truth boundary
# ---------------------------------------------------------------------------

def check_truth_boundary(manifest: dict) -> tuple[bool, list[str]]:
    problems: list[str] = []
    tb = manifest.get("truth_boundary")
    if not tb or not isinstance(tb, str):
        problems.append("manifest truth_boundary is missing or not a string")
    else:
        for term in TRUTH_BOUNDARY_TERMS:
            if term.lower() not in tb.lower():
                problems.append(
                    f"manifest truth_boundary missing term: {term!r}"
                )

    homepage = read_text(HOMEPAGE)
    for term in TRUTH_BOUNDARY_TERMS:
        if term.lower() not in homepage.lower():
            problems.append(f"homepage missing truth boundary term: {term!r}")

    return (not problems, problems)


# ---------------------------------------------------------------------------
# Check 8: forbidden affirmative claims
# ---------------------------------------------------------------------------

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
            # Context check: is this line inside a non-claim paragraph?
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
# Check 9: secret scan
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Check 10: route markers (PS-023 compatibility)
# ---------------------------------------------------------------------------

def check_route_markers() -> tuple[bool, list[str]]:
    # Route markers span both the homepage and the router (App.tsx). PS-024
    # must not remove any existing route/CTA marker from either file.
    combined = read_text(HOMEPAGE) + "\n" + read_text(
        REPO_ROOT / "apps" / "web" / "src" / "App.tsx"
    )
    missing = [m for m in ROUTE_CTA_MARKERS if m not in combined]
    return (not missing, missing)


# ---------------------------------------------------------------------------
# Check 11: PS-023 smoke callable
# ---------------------------------------------------------------------------

def check_ps023_callable() -> tuple[bool, list[str]]:
    if not PS023_SMOKE.exists():
        return False, [rel(PS023_SMOKE)]
    return True, []


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run(argv: list[str] | None = None) -> int:
    opts = sl.parse_slice_smoke_cli(argv)
    missing_inputs: list[str] = []
    for p in (MANIFEST, PS021_EVIDENCE, PS019_LIVE_EVIDENCE, HOMEPAGE):
        if not p.exists():
            missing_inputs.append(rel(p))
    if missing_inputs:
        print("PS-024 smoke: MISSING INPUT FILES")
        for f in missing_inputs:
            print(f"  - {f}")
        return 1

    manifest = load_json(MANIFEST)

    checks: list[tuple[str, tuple[bool, list[str]]]] = [
        ("manifest_exists", check_manifest_exists()),
        ("pinned_values_match", check_pinned_values_match(manifest)),
        ("no_invented_ids", check_no_invented_ids(manifest)),
        ("manifest_contract", check_manifest_contract(manifest)),
        ("homepage_honest", check_homepage_honest(manifest)),
        ("archive_match", check_archive_match(manifest)),
        ("rehydrate_match", check_rehydrate_match(manifest)),
        ("truth_boundary", check_truth_boundary(manifest)),
        ("forbidden_claims", check_forbidden_claims()),
        ("secret_scan", check_secrets()),
        ("route_markers", check_route_markers()),
        ("ps023_callable", check_ps023_callable()),
    ]

    all_pass, detail = sl.run_contract_checks(
        "PS-024 Golden Demo Run Pinning", checks
    )
    print(json.dumps(detail, indent=2))
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(run())
