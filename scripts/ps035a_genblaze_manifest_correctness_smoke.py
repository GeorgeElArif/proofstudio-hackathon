#!/usr/bin/env python3
"""PS-035a Genblaze Manifest Correctness -- local / static smoke.

This smoke is LOCAL / STATIC ONLY. It:

- reads checked-in files only (requirements, golden run, manifest fixture,
  PS-024 smoke source, proof doc)
- does not call providers
- does not read or write B2
- does not run the frontend
- does not run the backend
- does not call the central regression gate
- does not mutate prior evidence
- writes only:
  ``docs/evidence/ps-035a/genblaze-manifest-correctness-report.json``

It verifies the PS-035a Genblaze manifest correctness contract:

- the selected Genblaze version path is truthful (primary v0.4.0 or the
  published-version fallback) and matches reality on the configured index
- all three Genblaze packages are pinned to exact versions in requirements
- the installed versions (importlib.metadata.version) match the chosen pins
- no artifact makes a false v0.4.0 claim when the fallback is used
- the canonical golden run id, campaign id, and archive SHA-256 are preserved
- the golden run carries a non-null ``manifest_uri`` and a non-null 64-hex
  ``manifest_hash``
- the checked-in manifest fixture exists and its independent SHA-256 recompute
  equals the golden ``manifest_hash``
- the golden run records the exact Genblaze versions actually installed
- the PS-024 smoke was migrated from the null-manifest contract to the
  real-manifest contract
- no live provider call and no broad B2 read occur
- the truth boundary is preserved and no forbidden overclaims / file changes
  are present

Exit code is 0 only when every check passes.

    python scripts/ps035a_genblaze_manifest_correctness_smoke.py
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from importlib.metadata import version as _md_version, PackageNotFoundError
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIREMENTS = ROOT / "apps" / "api" / "requirements.txt"
GOLDEN = ROOT / "docs" / "evidence" / "demo" / "golden-demo-run.json"
FIXTURE = ROOT / "docs" / "evidence" / "ps-035a" / "manifest-fixture.json"
REPORT = (
    ROOT / "docs" / "evidence" / "ps-035a"
    / "genblaze-manifest-correctness-report.json"
)
PS024_SMOKE = ROOT / "scripts" / "ps024_golden_demo_run_pinning_smoke.py"
PROOF_DOC = (
    ROOT / "docs" / "ps-035a-genblaze-v040-manifest-correctness-proof.md"
)

GENBLAZE_PACKAGES = ("genblaze-core", "genblaze-s3", "genblaze-gmicloud")
SHA256_HEX_RE = re.compile(r"^[0-9a-f]{64}$")

# Canonical golden-run identity (must be preserved unchanged).
GOLDEN_RUN_ID = "run_89d967f9000045efa22ed4cc78cfa67f"
GOLDEN_CAMPAIGN_ID = "camp_bea5161faa6244079d2ee01ce445c259"
GOLDEN_ARCHIVE_SHA256 = (
    "a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141"
)

# Two-path dependency pin contract (PS-035a spec section 12).
TARGET_VERSION_REQUESTED = "0.4.0"
FALLBACK_PINS = {
    "genblaze-core": "0.3.4",
    "genblaze-s3": "0.3.4",
    "genblaze-gmicloud": "0.3.2",
}
PRIMARY_PINS = {
    "genblaze-core": "0.4.0",
    "genblaze-s3": "0.4.0",
    "genblaze-gmicloud": "0.4.0",
}

# Allowed changed files for PS-035a (mirrors the spec recommended implementation
# files plus this smoke and its evidence).
ALLOWED_CHANGED_FILES = {
    "apps/api/requirements.txt",
    "docs/evidence/demo/golden-demo-run.json",
    "scripts/ps024_golden_demo_run_pinning_smoke.py",
    "scripts/ps035a_genblaze_manifest_correctness_smoke.py",
    "docs/evidence/ps-035a/genblaze-manifest-correctness-report.json",
    "docs/evidence/ps-035a/manifest-fixture.json",
    "docs/ps-035a-genblaze-v040-manifest-correctness-proof.md",
    "docs/validation/proofstudio-smoke-harness-v1.md",
    "specs/07-master-spec-plan.md",
    "specs/08-roadmap-slices.md",
    "specs/47-ps-035a-genblaze-v040-manifest-correctness.md",
}

# Forbidden overclaim phrases that must never appear as POSITIVE claims. When
# the fallback path is used, a positive "v0.4.0" claim is also forbidden.
FORBIDDEN_OVERCLAIM_PHRASES = [
    "production secure",
    "C2PA authentic",
    "human authorship proven",
    "Object Lock enabled",
    "tamper-proof storage",
    "browser-side B2 byte verification",
    "live B2 Object Lock",
]

# Negation / non-claim cues. A forbidden phrase is acceptable only if a cue
# appears within the context window around it. "fallback", "unavailable",
# "not", "do not claim", "historical" are cues that mark a v0.4.0 mention as a
# truthful statement of fact rather than a positive capability claim.
NEGATION_CUES = (
    "does not",
    "do not",
    "doesn't",
    "don't",
    "not prove",
    "not claim",
    "must not",
    "no claim",
    "no overclaim",
    "no fake",
    "without",
    "unless",
    "non-claim",
    "never claim",
    "not implemented",
    "forbidden",
    "is not",
    "are not",
    "cannot",
    "can't",
    "do not claim",
    "must not claim",
    "not authorized",
    "unavailable",
    "fallback",
    "was probed",
    "probed unavailable",
    "not available",
    "historical",
    "remains unavailable",
    "not published",
    "not installed",
    "not used",
    "no live b2",
    "no live provider",
    "not v0.4.0",
)

_OVERCLAIM_BEFORE_WINDOW = 260
_OVERCLAIM_AFTER_WINDOW = 200

_WS_RE = re.compile(r"\s+")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _read_json(path: Path) -> dict:
    return json.loads(_read_text(path))


def _flat(text: str) -> str:
    return _WS_RE.sub(" ", text).strip()


def _read_flat(path: Path) -> str:
    return _flat(_read_text(path)) if path.is_file() else ""


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _genblaze_pins_from_requirements() -> dict[str, str]:
    """Parse exact Genblaze pins from apps/api/requirements.txt."""
    pins: dict[str, str] = {}
    if not REQUIREMENTS.is_file():
        return pins
    line_re = re.compile(r"^\s*([A-Za-z0-9_.-]+)\s*==\s*([0-9A-Za-z_.-]+)\s*$")
    for raw in _read_text(REQUIREMENTS).splitlines():
        line = raw.split("#", 1)[0]
        m = line_re.match(line)
        if not m:
            continue
        name, ver = m.group(1).strip(), m.group(2).strip()
        if name in GENBLAZE_PACKAGES:
            pins[name] = ver
    return pins


def _installed_versions() -> dict[str, str | None]:
    out: dict[str, str | None] = {}
    for pkg in GENBLAZE_PACKAGES:
        try:
            out[pkg] = _md_version(pkg)
        except PackageNotFoundError:
            out[pkg] = None
    return out


def _git_status_paths() -> list[str]:
    res = subprocess.run(
        ["git", "status", "--short", "--untracked-files=all"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    paths: list[str] = []
    for line in res.stdout.splitlines():
        if not line.strip() or line.startswith("## "):
            continue
        paths.append(line[3:])
    return paths


def _check_truthful_version_path(failures: list[str], installed: dict, pins: dict) -> tuple[bool, bool, bool]:
    """Determine and verify the selected version path.

    Returns (target_version_available, version_fallback_used,
    version_claim_truthful).
    """
    # Primary path is viable only when installed == 0.4.0 for all three.
    primary_active = all(installed.get(p) == PRIMARY_PINS[p] for p in GENBLAZE_PACKAGES)
    target_available = primary_active
    fallback_used = not primary_active

    expected = PRIMARY_PINS if primary_active else FALLBACK_PINS
    chosen = "primary v0.4.0" if primary_active else "published-version fallback"

    claim_truthful = True
    for pkg in GENBLAZE_PACKAGES:
        inst = installed.get(pkg)
        pin = pins.get(pkg)
        exp = expected[pkg]
        if inst != exp:
            failures.append(
                f"installed {pkg}=={inst!r} does not match {chosen} pin {exp!r}"
            )
            claim_truthful = False
        if pin is None:
            failures.append(f"{pkg} is not pinned in requirements (bare name)")
            claim_truthful = False
        elif pin != exp:
            failures.append(
                f"requirements pin {pkg}=={pin!r} does not match {chosen} {exp!r}"
            )
            claim_truthful = False

    return target_available, fallback_used, claim_truthful


def _check_requirements_pinned(failures: list[str], pins: dict) -> bool:
    ok = True
    for pkg in GENBLAZE_PACKAGES:
        if pkg not in pins:
            failures.append(f"{pkg} not pinned in requirements")
            ok = False
    # Reject any bare (unpinned) Genblaze name in requirements.
    if REQUIREMENTS.is_file():
        bare_re = re.compile(r"^\s*(genblaze-core|genblaze-s3|genblaze-gmicloud)\s*$")
        for i, raw in enumerate(_read_text(REQUIREMENTS).splitlines(), 1):
            line = raw.split("#", 1)[0]
            if bare_re.match(line):
                failures.append(f"requirements line {i}: bare unpinned name {line.strip()!r}")
                ok = False
    return ok


def _check_golden_identity_preserved(failures: list[str], golden: dict) -> tuple[bool, bool, bool]:
    rid = golden.get("run_id") == GOLDEN_RUN_ID
    cid = golden.get("campaign_id") == GOLDEN_CAMPAIGN_ID
    arc = golden.get("archive_sha256") == GOLDEN_ARCHIVE_SHA256
    if not rid:
        failures.append(
            f"golden run_id changed: {golden.get('run_id')!r} != {GOLDEN_RUN_ID!r}"
        )
    if not cid:
        failures.append(
            f"golden campaign_id changed: {golden.get('campaign_id')!r} != {GOLDEN_CAMPAIGN_ID!r}"
        )
    if not arc:
        failures.append(
            f"golden archive_sha256 changed: {golden.get('archive_sha256')!r}"
        )
    return rid, cid, arc


def _check_manifest_fields(failures: list[str], golden: dict) -> tuple[bool, bool, bool]:
    uri = golden.get("manifest_uri")
    h = golden.get("manifest_hash")
    uri_ok = isinstance(uri, str) and bool(uri)
    hash_non_null = isinstance(h, str) and bool(h)
    hash_fmt = isinstance(h, str) and bool(SHA256_HEX_RE.match(h or ""))
    if not uri_ok:
        failures.append(f"golden manifest_uri non-null contract failed: {uri!r}")
    if not hash_non_null:
        failures.append(f"golden manifest_hash non-null contract failed: {h!r}")
    if not hash_fmt:
        failures.append(f"golden manifest_hash not 64-hex SHA-256: {h!r}")
    # manifest_sha256 (if present) must match manifest_hash.
    ms = golden.get("manifest_sha256")
    if ms is not None and ms != h:
        failures.append(
            f"golden manifest_sha256 {ms!r} does not match manifest_hash {h!r}"
        )
    return uri_ok, hash_non_null, hash_fmt


def _check_genblaze_versions_recorded(failures: list[str], golden: dict, installed: dict) -> bool:
    gv = golden.get("genblaze_versions")
    if not isinstance(gv, dict) or not gv:
        failures.append("golden run does not record genblaze_versions mapping")
        return False
    ok = True
    for pkg in GENBLAZE_PACKAGES:
        rec = gv.get(pkg)
        if not rec:
            failures.append(f"golden genblaze_versions missing {pkg}")
            ok = False
        elif rec != installed.get(pkg):
            failures.append(
                f"golden genblaze_versions[{pkg}]={rec!r} != installed {installed.get(pkg)!r}"
            )
            ok = False
    return ok


def _check_fixture(failures: list[str], golden: dict) -> tuple[bool, bool, bool]:
    """Fixture exists, hash recomputes, and matches golden manifest_hash."""
    present = FIXTURE.is_file()
    if not present:
        failures.append(f"manifest fixture missing: {FIXTURE}")
        return False, False, False
    recomputed = _sha256_bytes(FIXTURE.read_bytes())
    recompute_ok = bool(SHA256_HEX_RE.match(recomputed))
    matches = recomputed == golden.get("manifest_hash")
    if not recompute_ok:
        failures.append(f"fixture recompute not 64-hex: {recomputed!r}")
    if not matches:
        failures.append(
            f"fixture SHA-256 {recomputed!r} != golden manifest_hash "
            f"{golden.get('manifest_hash')!r}"
        )
    return present, recompute_ok, matches


def _check_ps024_migrated(failures: list[str]) -> bool:
    """The PS-024 smoke must carry the real-manifest contract, not the old
    null-manifest contract."""
    if not PS024_SMOKE.is_file():
        failures.append(f"PS-024 smoke missing: {PS024_SMOKE}")
        return False
    src = _read_text(PS024_SMOKE)
    # Old null-manifest contract removed.
    old_assertion = "manifest_uri and manifest_hash must be null"
    if old_assertion in src:
        failures.append(
            "PS-024 smoke still carries the old null-manifest assertion"
        )
        return False
    # New real-manifest contract present.
    has_contract = "def check_manifest_contract" in src
    requires_uri = 'isinstance(manifest_uri, str)' in src and "must be a non-empty string" in src
    requires_hash = "SHA256_HEX_RE.match(manifest_hash)" in src or "SHA256_HEX_RE.match" in src
    requires_recompute = "manifest_fixture" in src.lower() and "sha256" in src.lower()
    if not (has_contract and requires_uri and requires_hash and requires_recompute):
        failures.append(
            "PS-024 smoke does not enforce the real-manifest contract "
            f"(contract={has_contract}, uri={requires_uri}, hash={requires_hash}, "
            f"recompute={requires_recompute})"
        )
        return False
    return True


def _check_truth_boundary(failures: list[str]) -> bool:
    tb = (
        "ProofStudio proves what the pipeline did. It does not prove semantic "
        "truth, legal authenticity, C2PA authenticity, or human authorship."
    )
    if tb not in _read_flat(FIXTURE):
        failures.append("manifest fixture missing the truth boundary")
        return False
    if not PROOF_DOC.is_file() or "Truth Boundary" not in _read_flat(PROOF_DOC):
        failures.append("proof doc missing Truth Boundary section")
        return False
    return True


def _check_no_forbidden_overclaims(failures: list[str]) -> bool:
    """Forbid overclaim phrases (and positive v0.4.0 claims when fallback is
    used) as POSITIVE claims across the PS-035a proof doc, golden run, and
    fixture."""
    phrases = list(FORBIDDEN_OVERCLAIM_PHRASES)
    # When the fallback is used a positive v0.4.0 claim is itself an overclaim.
    phrases.append("v0.4.0")

    scan_docs = [PROOF_DOC, GOLDEN, FIXTURE]
    ok = True
    for doc in scan_docs:
        if not doc.is_file():
            continue
        flat = _read_flat(doc).lower()
        for phrase in phrases:
            p_low = phrase.lower()
            start = 0
            while True:
                idx = flat.find(p_low, start)
                if idx == -1:
                    break
                win_start = max(0, idx - _OVERCLAIM_BEFORE_WINDOW)
                win_end = min(len(flat), idx + len(p_low) + _OVERCLAIM_AFTER_WINDOW)
                window = flat[win_start:win_end]
                if not any(cue in window for cue in NEGATION_CUES):
                    failures.append(
                        f"no_forbidden_overclaims/{doc.name}: phrase "
                        f"{phrase!r} appears as a positive claim "
                        f"(no negation cue in context)"
                    )
                    ok = False
                start = idx + len(p_low)
    return ok


def _check_no_forbidden_file_changes(failures: list[str]) -> bool:
    ok = True
    try:
        paths = _git_status_paths()
    except Exception as exc:  # pragma: no cover - defensive
        failures.append(f"no_forbidden_file_changes: git status failed: {exc}")
        return False
    for path in paths:
        if path not in ALLOWED_CHANGED_FILES:
            failures.append(
                f"no_forbidden_file_changes: forbidden/out-of-allowed path changed: "
                f"{path}"
            )
            ok = False
    return ok


def main() -> int:
    failures: list[str] = []

    files_present = REQUIREMENTS.is_file() and GOLDEN.is_file()
    if not files_present:
        failures.append("required input file missing (requirements or golden run)")

    pins = _genblaze_pins_from_requirements()
    installed = _installed_versions()
    golden = _read_json(GOLDEN) if GOLDEN.is_file() else {}

    requirements_pinned = _check_requirements_pinned(failures, pins)
    target_available, fallback_used, claim_truthful = (
        _check_truthful_version_path(failures, installed, pins)
    )

    rid_ok, cid_ok, arc_ok = _check_golden_identity_preserved(failures, golden)
    uri_ok, hash_non_null, hash_fmt = _check_manifest_fields(failures, golden)
    gv_recorded = _check_genblaze_versions_recorded(failures, golden, installed)
    fix_present, fix_recompute, fix_matches = _check_fixture(failures, golden)
    ps024_migrated = _check_ps024_migrated(failures)
    truth_ok = _check_truth_boundary(failures)
    no_overclaims = _check_no_forbidden_overclaims(failures)
    no_bad_files = _check_no_forbidden_file_changes(failures)

    # In-memory and stored manifest verification are both scoped to the
    # checked-in local fixture (no live B2 by default). Record explicit scope.
    in_memory_verify = bool(fix_present and fix_recompute and fix_matches)
    stored_verify = bool(fix_present and fix_recompute and fix_matches)

    # This smoke makes no provider call and performs no B2 read/write.
    no_live_provider_call = True
    no_broad_b2_read = True

    ok = (
        files_present
        and requirements_pinned
        and claim_truthful
        and rid_ok
        and cid_ok
        and arc_ok
        and uri_ok
        and hash_non_null
        and hash_fmt
        and gv_recorded
        and fix_present
        and fix_recompute
        and fix_matches
        and ps024_migrated
        and truth_ok
        and no_overclaims
        and no_bad_files
        and in_memory_verify
        and stored_verify
        and not failures
    )

    report = {
        "ok": bool(ok),
        "slice_id": "ps035a",
        "checked_at": _utc_now_iso(),
        "target_version_requested": TARGET_VERSION_REQUESTED,
        "target_version_available": bool(target_available),
        "version_fallback_used": bool(fallback_used),
        "selected_package_path": (
            "primary-v0.4.0" if not fallback_used else "published-version-fallback"
        ),
        "pinned_genblaze_versions": pins,
        "installed_genblaze_versions": installed,
        "version_claim_truthful": bool(claim_truthful),
        "requirements_pinned": bool(requirements_pinned),
        "golden_run_id_preserved": bool(rid_ok),
        "golden_campaign_id_preserved": bool(cid_ok),
        "archive_sha256_preserved": bool(arc_ok),
        "manifest_uri_non_null": bool(uri_ok),
        "manifest_hash_non_null": bool(hash_non_null),
        "manifest_hash_sha256_format": bool(hash_fmt),
        "genblaze_versions_recorded": bool(gv_recorded),
        "manifest_fixture_present": bool(fix_present),
        "manifest_fixture_sha256_recomputed": bool(fix_recompute),
        "manifest_fixture_hash_matches_golden": bool(fix_matches),
        "in_memory_manifest_verify": bool(in_memory_verify),
        "in_memory_manifest_verify_scope": "checked-in-local-fixture",
        "stored_manifest_verify": bool(stored_verify),
        "stored_manifest_verify_scope": "checked-in-local-fixture",
        "ps024_smoke_migrated": bool(ps024_migrated),
        "no_live_provider_call": bool(no_live_provider_call),
        "no_broad_b2_read": bool(no_broad_b2_read),
        "truth_boundary_preserved": bool(truth_ok),
        "no_forbidden_overclaims": bool(no_overclaims),
        "no_forbidden_file_changes": bool(no_bad_files),
        "failures": failures,
    }

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(report, indent=2, sort_keys=False) + "\n"
    tmp = REPORT.with_suffix(REPORT.suffix + ".tmp")
    tmp.write_text(payload, encoding="utf-8")
    import os
    os.replace(tmp, REPORT)

    if failures:
        print("PS-035A GENBLAZE MANIFEST CORRECTNESS SMOKE FAILED", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("PS-035A GENBLAZE MANIFEST CORRECTNESS SMOKE PASSED")
    print(f"  selected_package_path: {report['selected_package_path']}")
    print(f"  version_fallback_used: {fallback_used}")
    print(f"  version_claim_truthful: {claim_truthful}")
    print(f"  manifest_fixture_hash_matches_golden: {fix_matches}")
    print(f"  ps024_smoke_migrated: {ps024_migrated}")
    print(f"  report: {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
