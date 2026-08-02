#!/usr/bin/env python3
"""PS-036 Archive / Rehydrate / B2 Audit Vault -- smoke / validation script.

This smoke validates ONLY the PS-036 slice. It is local / static by default:
it does not start a browser, does not run the frontend typecheck / build,
does not call any provider, does not read or write any B2 object, does not
perform a broad B2 scan, does not call the central regression gate, and does
not recursively execute another feature smoke. Default behavior is
non-mutating local validation (``--check-only``); no evidence file is written
unless ``--write-evidence`` is explicit.

Standard flags (PS-034B / PS-035D feature-smoke contract):

    --check-only      default; non-mutating local validation; writes nothing
    --write-evidence  writes only docs/evidence/ps-036/ evidence
    --no-frontend     skip the frontend typecheck/build (always skipped; a
                      feature smoke never runs the frontend)

Truth boundary: this smoke validates that the PS-036 vault surface is honest.
It does not prove semantic truth, legal authenticity, C2PA authenticity, human
authorship, Object Lock / tamper-proof storage, browser-side B2 byte
verification, or production security. It is not live B2 verification.

Exit code is 0 only when every check passes.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import smoke_lib as sl  # noqa: E402

REPO_ROOT = sl.repo_root()
APPS_WEB_SRC = REPO_ROOT / "apps" / "web" / "src"
DATA_MODULE = APPS_WEB_SRC / "b2AuditVault.ts"
COMPONENT = APPS_WEB_SRC / "B2AuditVault.tsx"
APP_TSX = APPS_WEB_SRC / "App.tsx"
HOMEPAGE = APPS_WEB_SRC / "JudgeCockpitHome.tsx"
SMOKE_SELF = REPO_ROOT / "scripts" / "ps036_archive_rehydrate_b2_audit_vault_smoke.py"
PROOF_DOC = REPO_ROOT / "docs" / "ps-036-archive-rehydrate-b2-audit-vault-proof.md"
AGENTS_MD = REPO_ROOT / "AGENTS.md"
GOLDEN_DEMO = REPO_ROOT / "docs" / "evidence" / "demo" / "golden-demo-run.json"
EVIDENCE_OUT = (
    REPO_ROOT
    / "docs"
    / "evidence"
    / "ps-036"
    / "archive-rehydrate-b2-audit-vault-report.json"
)
ROUTE_PATH = "/b2-audit-vault"

# Files scanned for forbidden overclaims and secrets. The smoke script itself
# is intentionally excluded from the forbidden-claim / secret scans because it
# legitimately contains the detection literals (same convention as PS-023
# through PS-035 smokes). It IS scanned for the bad hidden-flag command literal
# and recursive-smoke execution.
CLAIM_SCAN_FILES: tuple[Path, ...] = (
    DATA_MODULE,
    COMPONENT,
    APP_TSX,
    HOMEPAGE,
    PROOF_DOC,
)

# Source files scanned for provider-call / B2-read / B2-write code patterns.
PROVIDER_B2_SCAN_FILES: tuple[Path, ...] = (
    DATA_MODULE,
    COMPONENT,
    APP_TSX,
    HOMEPAGE,
)

# Files scanned for the bad lowercase-only hidden-flag command literal. Includes
# the smoke itself: the literal must never appear contiguously in any changed
# file, and the smoke builds the search needle from fragments so it does not
# self-trip.
BAD_LITERAL_SCAN_FILES: tuple[Path, ...] = (
    DATA_MODULE,
    COMPONENT,
    APP_TSX,
    HOMEPAGE,
    PROOF_DOC,
    SMOKE_SELF,
)

# Required vault UI strings (spec section 20). Each must appear in the vault
# component and/or data module so the contract is deterministic.
REQUIRED_UI_STRINGS: tuple[str, ...] = (
    "Archive / Rehydrate / B2 Audit Vault",
    "B2 system of record",
    "archive reference",
    "archive sha256",
    "manifest hash",
    "rehydrate source",
    "provider calls during rehydrate",
    "no live provider call during rehydrate",
    "local verification",
    "not live B2 verification",
    "not Object Lock",
    "not tamper-proof",
    "not production security",
    "not legal authenticity",
    "not semantic truth",
)

# Required audit / boundary contract strings (spec section 20). These must
# appear across the vault surface (component + data module) and/or the proof
# doc so the audit contract is deterministic.
REQUIRED_AUDIT_STRINGS: tuple[str, ...] = (
    "notes",
    "B2 evidence",
    "no broad B2 reads",
    "hidden Git flags h and S",
    "do not claim Object Lock / tamper-proof storage unless implemented and verified",
    "do not claim browser-side B2 byte verification unless implemented and verified",
    "do not claim actual spend/latency/quota unless captured",
    "do not claim provider failures/reruns/variants unless evidenced",
)

# Boundary phrases the vault must surface (spec section 11 / section 16).
BOUNDARY_PHRASES: tuple[str, ...] = (
    "It is not live B2 verification",
    "It is not Object Lock",
    "It is not tamper-proof",
    "It is not production security",
    "It is not legal authenticity",
    "It is not semantic truth",
)

# AGENTS.md operating-law strings that must remain intact so the h/S hidden
# Git flag rule is not weakened to a lowercase-only check.
AGENTS_HS_RULE_STRINGS: tuple[str, ...] = (
    "hidden Git flags h and S",
    "fail when line[0] is h or S",
)
AGENTS_RED_LINE_STRINGS: tuple[str, ...] = (
    "do not claim legal authenticity",
    "do not claim Object Lock",
    "do not claim C2PA",
    "do not claim enterprise security",
)

# Forbidden affirmative overclaim phrases. Each is matched case-insensitively
# against a line; if the surrounding paragraph does not carry a non-claim
# context marker, the line is flagged.
FORBIDDEN_AFFIRMATIVE: tuple[str, ...] = (
    "the vault proves semantic truth",
    "the vault proves legal authenticity",
    "the vault proves c2pa authenticity",
    "the vault proves human authorship",
    "the vault proves object lock",
    "the vault proves tamper-proof storage",
    "the vault proves production security",
    "object lock is enabled",
    "tamper-proof storage is enabled",
    "public deployment is verified",
    "public deployment verified",
    "the browser verified the b2 bytes",
    "the browser fetched and hashed the b2 object",
    "enterprise-grade security",
    "live b2 verification succeeded",
)

CONTEXT_MARKERS_RE = re.compile(
    r"does not|do not|must not|\bnot\b|non-claim|non-claims|forbidden|"
    r"reject|rejected|avoid|without overclaim|unless actually implemented|"
    r"only inside non-claim|limitation|limitations|no affirmative|"
    r"unavailable|blocked|honestly|no live|no_new|no_fake|pending|planned|"
    r"did not fetch|does not claim|did not claim|without|none claimed|"
    r"would appear|if captured|no actual|no fake|not implemented|"
    r"is not implemented|not a certification|not legal advice|"
    r"it is not|it did not",
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

# Validation needles used to detect a newly-introduced live provider-call
# path in the scanned app source. These are SCANNER NEEDLES (string
# constants), not executable calls: this smoke performs no network, provider,
# or B2 behavior whatsoever. The needles that resemble executable call syntax
# are assembled from fragments so a naive regex audit scanning THIS smoke
# cannot self-trip. At runtime each fragment concatenation evaluates to the
# exact literal the scanned files are tested against.
FORBIDDEN_LIVE_CALL_NEEDLES: tuple[str, ...] = (
    "call_provider",
    "fetchFromProvider",
    "requests" + ".post",
    "urlopen" + "(",
    "httpx" + ".post",
    "client.post(",
)

# Validation needles used to detect a newly-introduced broad B2 object read
# path in the scanned app source. Scanner needles only; no executable
# behavior. The browser-fetch needle is fragmented so it cannot self-trip a
# regex audit.
FORBIDDEN_B2_READ_NEEDLES: tuple[str, ...] = (
    "read_archive_from_b2",
    "b2.fetch",
    "b2GetObject",
    "list_b2_objects",
    "fetchB2Object",
    "fetch" + "(",
)

# Validation needles used to detect a newly-introduced B2 object write path
# in the scanned app source. Scanner needles only; no executable behavior.
FORBIDDEN_B2_WRITE_NEEDLES: tuple[str, ...] = (
    "upload_to_b2",
    "b2.put",
    "b2PutObject",
    "put_b2_object",
    "uploadB2Object",
    "write_archive_to_b2",
)

# Validation needles used to detect a newly-introduced broad B2 scan path in
# the scanned app source. Scanner needles only; no executable behavior.
FORBIDDEN_B2_SCAN_NEEDLES: tuple[str, ...] = (
    "list_all_b2_objects",
    "scan_b2_bucket",
    "listObjectsV2",
    "b2_list_buckets",
    "enumerate_b2_prefix",
)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def read_text(path: Path) -> str:
    return sl.read_text(path)


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


def _scan_affirmative(
    paths: tuple[Path, ...],
    phrases: tuple[str, ...],
) -> list[str]:
    """Return problem strings for forbidden affirmative claims.

    A phrase is flagged only when the surrounding paragraph lacks a non-claim
    context marker (mirrors PS-031 / PS-034 / PS-035).
    """
    problems: list[str] = []
    for path in paths:
        if not path.is_file():
            continue
        lines = read_text(path).splitlines()
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
                f"{rel(path)}:{i + 1}: affirmative claim with no non-claim "
                f"context -> {line.strip()!r}"
            )
    return problems


def _git_status_entries() -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for line in sl.git_status_short().splitlines():
        if not line.strip():
            continue
        tag = line[:2]
        path = line[3:]
        out.append((tag, path))
    return out


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_route_registered() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not APP_TSX.is_file():
        return False, [f"missing {rel(APP_TSX)}"]
    text = read_text(APP_TSX)
    if "isB2AuditVaultPath" not in text:
        problems.append("App.tsx does not register an isB2AuditVaultPath helper")
    if ROUTE_PATH not in text:
        problems.append(f"App.tsx does not reference the {ROUTE_PATH} path")
    if "B2AuditVault" not in text:
        problems.append("App.tsx does not render the B2AuditVault component")
    if '<B2AuditVault variant="page" />' not in text:
        problems.append(
            'App.tsx does not render <B2AuditVault variant="page" />'
        )
    return (not problems, problems)


def check_vault_component_present() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not COMPONENT.is_file():
        return False, [f"missing component {rel(COMPONENT)}"]
    text = read_text(COMPONENT)
    for needle in (
        "Archive / Rehydrate / B2 Audit Vault",
        "export function B2AuditVault",
        'variant = "page"',
    ):
        if needle not in text:
            problems.append(f"component missing reference to {needle!r}")
    return (not problems, problems)


def check_data_module_present() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not DATA_MODULE.is_file():
        return False, [f"missing data module {rel(DATA_MODULE)}"]
    text = read_text(DATA_MODULE)
    for needle in (
        "B2_AUDIT_VAULT_RECORDS",
        "B2_AUDIT_VAULT_TRUTH_BOUNDARY",
        "B2_AUDIT_VAULT_BOUNDARY_RED_LINES",
        "B2_AUDIT_VAULT_NOT_CLAIMED",
    ):
        if needle not in text:
            problems.append(f"data module missing {needle!r}")
    return (not problems, problems)


def _vault_blob() -> str:
    blob = ""
    for path in (DATA_MODULE, COMPONENT):
        if path.is_file():
            blob += "\n" + read_text(path)
    return blob


def check_required_ui_strings() -> tuple[bool, list[str]]:
    """Required vault UI strings (spec section 20) must be present."""
    problems: list[str] = []
    blob = _vault_blob()
    if not blob:
        return False, ["vault component + data module missing"]
    for needle in REQUIRED_UI_STRINGS:
        if needle not in blob:
            problems.append(f"vault surface missing required UI string {needle!r}")
    return (not problems, problems)


def check_required_audit_strings() -> tuple[bool, list[str]]:
    """Required audit / boundary contract strings must be present somewhere
    in the vault surface or the proof doc."""
    problems: list[str] = []
    blob = _vault_blob()
    if PROOF_DOC.is_file():
        blob += "\n" + read_text(PROOF_DOC)
    if not blob:
        return False, ["vault surface + proof doc missing"]
    for needle in REQUIRED_AUDIT_STRINGS:
        if needle not in blob:
            problems.append(
                f"vault/proof missing required audit string {needle!r}"
            )
    return (not problems, problems)


def check_boundary_copy_present() -> tuple[bool, list[str]]:
    problems: list[str] = []
    blob = _vault_blob()
    if not blob:
        return False, ["boundary copy sources missing"]
    for phrase in BOUNDARY_PHRASES:
        if phrase.lower() not in blob.lower():
            problems.append(f"boundary copy missing phrase {phrase!r}")
    return (not problems, problems)


def check_b2_evidence_status_present() -> tuple[bool, list[str]]:
    problems: list[str] = []
    blob = _vault_blob()
    if "B2 evidence status" not in blob and "b2_evidence_status" not in blob:
        problems.append("vault surface missing B2 evidence status record")
    if "B2 evidence" not in blob:
        problems.append("vault surface missing 'B2 evidence' framing")
    return (not problems, problems)


def check_local_verification_status_present() -> tuple[bool, list[str]]:
    problems: list[str] = []
    blob = _vault_blob()
    if "local verification" not in blob:
        problems.append("vault surface missing 'local verification' framing")
    if "not live B2 verification" not in blob:
        problems.append("vault surface missing 'not live B2 verification' note")
    return (not problems, problems)


def check_not_claimed_status_present() -> tuple[bool, list[str]]:
    problems: list[str] = []
    blob = _vault_blob()
    for needle in (
        "not claimed",
        "not Object Lock",
        "not tamper-proof",
        "not production security",
        "not legal authenticity",
        "not semantic truth",
    ):
        if needle not in blob:
            problems.append(f"vault surface missing not-claimed status {needle!r}")
    return (not problems, problems)


def check_truth_boundary_preserved() -> tuple[bool, list[str]]:
    """AGENTS.md h/S rule and red lines must remain intact (not weakened)."""
    problems: list[str] = []
    if not AGENTS_MD.is_file():
        return False, [f"missing {rel(AGENTS_MD)}"]
    text = read_text(AGENTS_MD)
    for needle in AGENTS_HS_RULE_STRINGS:
        if needle not in text:
            problems.append(f"AGENTS.md missing h/S rule string {needle!r}")
    for needle in AGENTS_RED_LINE_STRINGS:
        if needle not in text:
            problems.append(f"AGENTS.md missing red line {needle!r}")
    blob = _vault_blob()
    for phrase in BOUNDARY_PHRASES:
        if phrase.lower() not in blob.lower():
            problems.append(f"vault boundary copy missing phrase {phrase!r}")
    return (not problems, problems)


def check_golden_constants_match() -> tuple[bool, list[str]]:
    """Published vault constants must match the golden manifest verbatim.

    The vault reuses the verified golden constants from apps/web/src/b2Evidence.ts
    (PS-026) read-only by import, so the verbatim values live in b2Evidence.ts.
    This check scans the data module, the component, AND the reused b2Evidence.ts
    source so the golden values are verified present in the vault's dependency
    graph (same single-source-of-truth convention as b2RehydrateComparison.ts).
    """
    problems: list[str] = []
    if not GOLDEN_DEMO.is_file():
        return False, [f"missing golden manifest {rel(GOLDEN_DEMO)}"]
    golden = sl.read_json(GOLDEN_DEMO)
    b2_evidence_src = APPS_WEB_SRC / "b2Evidence.ts"
    scan_text = _vault_blob()
    if b2_evidence_src.is_file():
        scan_text += "\n" + read_text(b2_evidence_src)
    if not scan_text.strip():
        return False, ["no vault source scanned"]
    pairs = (
        ("run_id", golden.get("run_id")),
        ("campaign_id", golden.get("campaign_id")),
        ("archive_uri", golden.get("archive_uri")),
        ("archive_sha256", golden.get("archive_sha256")),
        ("rehydrate_source", golden.get("rehydrate_source")),
        ("manifest_hash", golden.get("manifest_hash")),
    )
    for field, want in pairs:
        if not want:
            continue
        if str(want) not in scan_text:
            problems.append(
                f"vault dependency graph missing golden {field} value {want!r}"
            )
    # provider_calls_during_rehydrate is an integer 0; verify the value is
    # present and equals 0.
    pcr = golden.get("provider_calls_during_rehydrate")
    if pcr is not None:
        if str(pcr) not in scan_text:
            problems.append(
                f"vault dependency graph missing provider_calls_during_rehydrate value {pcr!r}"
            )
    # The data module must reuse the no-live-provider-call constant read-only.
    if not DATA_MODULE.is_file():
        return False, [f"missing data module {rel(DATA_MODULE)}"]
    dmod = read_text(DATA_MODULE)
    if "GOLDEN_DEMO_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE" not in dmod:
        problems.append(
            "data module does not reuse "
            "GOLDEN_DEMO_NO_LIVE_PROVIDER_CALL_DURING_REHYDRATE"
        )
    return (not problems, problems)


def check_manifest_hash_present_or_honest() -> tuple[bool, list[str]]:
    """The manifest hash must be present and match accepted evidence, OR the
    vault must carry an honest 'not available' state. Here the manifest hash
    IS present in accepted evidence, so it must match verbatim."""
    problems: list[str] = []
    if not GOLDEN_DEMO.is_file():
        return False, [f"missing golden manifest {rel(GOLDEN_DEMO)}"]
    golden = sl.read_json(GOLDEN_DEMO)
    want = golden.get("manifest_hash")
    blob = _vault_blob()
    if want and str(want) not in blob:
        problems.append(
            f"vault surface missing accepted manifest_hash value {want!r}"
        )
    if "manifest hash" not in blob:
        problems.append("vault surface missing 'manifest hash' label")
    return (not problems, problems)


def check_no_provider_calls() -> tuple[bool, list[str]]:
    problems: list[str] = []
    for path in PROVIDER_B2_SCAN_FILES:
        if not path.is_file():
            continue
        text = read_text(path)
        for pattern in FORBIDDEN_LIVE_CALL_NEEDLES:
            if pattern in text:
                problems.append(
                    f"{rel(path)}: forbidden provider-call pattern {pattern!r}"
                )
    return (not problems, problems)


def check_no_b2_reads() -> tuple[bool, list[str]]:
    problems: list[str] = []
    for path in PROVIDER_B2_SCAN_FILES:
        if not path.is_file():
            continue
        text = read_text(path)
        for pattern in FORBIDDEN_B2_READ_NEEDLES:
            if pattern in text:
                problems.append(
                    f"{rel(path)}: forbidden B2 read pattern {pattern!r}"
                )
    return (not problems, problems)


def check_no_b2_writes() -> tuple[bool, list[str]]:
    problems: list[str] = []
    for path in PROVIDER_B2_SCAN_FILES:
        if not path.is_file():
            continue
        text = read_text(path)
        for pattern in FORBIDDEN_B2_WRITE_NEEDLES:
            if pattern in text:
                problems.append(
                    f"{rel(path)}: forbidden B2 write pattern {pattern!r}"
                )
    return (not problems, problems)


def check_no_b2_scans() -> tuple[bool, list[str]]:
    problems: list[str] = []
    for path in PROVIDER_B2_SCAN_FILES:
        if not path.is_file():
            continue
        text = read_text(path)
        for pattern in FORBIDDEN_B2_SCAN_NEEDLES:
            if pattern in text:
                problems.append(
                    f"{rel(path)}: forbidden broad B2 scan pattern {pattern!r}"
                )
    return (not problems, problems)


def check_no_recursive_smokes() -> tuple[bool, list[str]]:
    problems: list[str] = []
    try:
        sl.assert_no_recursive_smoke_execution(SMOKE_SELF)
    except sl.HarnessError as exc:
        problems.append(str(exc))
    return (not problems, problems)


def check_no_bad_hidden_flag_literal() -> tuple[bool, list[str]]:
    """The bad lowercase-only hidden-flag command literal must be absent.

    The search needle is assembled from fragments so the smoke itself never
    contains the contiguous forbidden literal and therefore does not self-trip.
    """
    needle = "gr" + "ep" + " -" + "E " + "'^" + "[a-z]" + "'"
    problems: list[str] = []
    for path in BAD_LITERAL_SCAN_FILES:
        if not path.is_file():
            continue
        if needle in read_text(path):
            problems.append(
                f"{rel(path)}: contains the forbidden lowercase-only "
                f"hidden-flag command literal"
            )
    return (not problems, problems)


def _hidden_flag_hits() -> tuple[list[str], list[str]]:
    """Return (h_hits, S_hits) from ``git ls-files -v``.

    This is the explicit h/S checker required by the operating law: it reads
    ``git ls-files -v`` and flags a line when ``line[0]`` is ``h`` (assume
    unchanged) or ``S`` (skip-worktree, uppercase). A lowercase-only marker
    check is not sufficient because it misses uppercase ``S`` skip-worktree.
    This intentionally does NOT reuse the shared lowercase-only marker check.
    """
    res = sl.run_command(["git", "ls-files", "-v"], cwd=REPO_ROOT)
    h_hits: list[str] = []
    s_hits: list[str] = []
    for line in res.stdout.splitlines():
        if not line:
            continue
        first = line[0]
        if first == "h":
            h_hits.append(line)
        elif first == "S":
            s_hits.append(line)
    return h_hits, s_hits


def check_hidden_git_flags_h() -> tuple[bool, list[str]]:
    h_hits, _ = _hidden_flag_hits()
    return (not h_hits, h_hits)


def check_hidden_git_flags_S() -> tuple[bool, list[str]]:
    _, s_hits = _hidden_flag_hits()
    return (not s_hits, s_hits)


def check_no_forbidden_overclaims() -> tuple[bool, list[str]]:
    problems = _scan_affirmative(CLAIM_SCAN_FILES, FORBIDDEN_AFFIRMATIVE)
    return (not problems, problems)


def check_secrets_absent() -> tuple[bool, list[str]]:
    problems: list[str] = []
    for path in CLAIM_SCAN_FILES:
        if not path.is_file():
            continue
        text = read_text(path)
        for needle in SECRET_SUBSTRINGS:
            if needle in text:
                idx = text.find(needle)
                line_no = text.count("\n", 0, idx) + 1
                problems.append(f"{rel(path)}:{line_no}: secret literal {needle!r}")
        for m in SECRET_KEY_RE.finditer(text):
            idx = m.start()
            line_no = text.count("\n", 0, idx) + 1
            problems.append(f"{rel(path)}:{line_no}: secret literal {m.group(0)!r}")
    return (not problems, problems)


def check_git_diff_check_clean() -> tuple[bool, list[str]]:
    res = sl.run_command(["git", "diff", "--check"], cwd=REPO_ROOT)
    problems: list[str] = []
    output = (res.stdout or "").strip()
    if res.returncode != 0 or output:
        text = output or f"git diff --check exited {res.returncode}"
        problems.append(f"git diff --check not clean: {text}")
    return (not problems, problems)


def check_prior_evidence_clean() -> tuple[bool, list[str]]:
    """No tracked evidence outside docs/evidence/ps-036/ may be left dirty."""
    problems: list[str] = []
    try:
        entries = _git_status_entries()
    except sl.HarnessError as exc:
        return False, [f"could not run git status: {exc}"]
    for _tag, path in entries:
        path = path.strip().strip('"')
        if path.startswith("docs/evidence/") and not path.startswith(
            "docs/evidence/ps-036/"
        ):
            problems.append(
                f"prior-slice evidence left dirty by PS-036 smoke: {path}"
            )
    return (not problems, problems)


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None) -> tuple[bool, bool, bool]:
    """Return (write_evidence, check_only, no_frontend).

    Default is non-mutating local validation: check_only=True,
    write_evidence=False, no_frontend=True.
    """
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--check-only", action="store_true", default=True)
    p.add_argument(
        "--write-evidence",
        dest="write_evidence",
        action="store_true",
        default=False,
    )
    p.add_argument(
        "--no-frontend",
        dest="no_frontend",
        action="store_true",
        default=True,
    )
    ns, _unknown = p.parse_known_args(list(argv) if argv is not None else None)
    write_evidence = bool(ns.write_evidence)
    check_only = not write_evidence
    return write_evidence, check_only, bool(ns.no_frontend)


def run(argv: list[str] | None = None) -> int:
    write_evidence, _check_only, _no_frontend = parse_args(argv)

    missing: list[str] = []
    for p in (GOLDEN_DEMO,):
        if not p.exists():
            missing.append(rel(p))
    if missing:
        print("PS036 smoke: MISSING INPUT FILES")
        for f in missing:
            print(f"  - {f}")
        return 1

    checks: list[tuple[str, tuple[bool, list[str]]]] = [
        ("route_present", check_route_registered()),
        ("vault_component_present", check_vault_component_present()),
        ("vault_data_module_present", check_data_module_present()),
        ("required_ui_strings", check_required_ui_strings()),
        ("archive_reference_present", _check_field_present("archive reference")),
        ("archive_sha256_present", _check_field_present("archive sha256")),
        ("manifest_hash_present_or_honestly_unavailable",
         check_manifest_hash_present_or_honest()),
        ("rehydrate_source_present", _check_field_present("rehydrate source")),
        ("provider_calls_during_rehydrate_present",
         _check_field_present("provider calls during rehydrate")),
        ("no_live_provider_call_during_rehydrate_present",
         _check_field_present("no live provider call during rehydrate")),
        ("b2_evidence_status_present", check_b2_evidence_status_present()),
        ("local_verification_status_present",
         check_local_verification_status_present()),
        ("not_claimed_status_present", check_not_claimed_status_present()),
        ("required_audit_strings", check_required_audit_strings()),
        ("boundary_copy_present", check_boundary_copy_present()),
        ("golden_constants_match", check_golden_constants_match()),
        ("no_provider_calls", check_no_provider_calls()),
        ("no_b2_reads", check_no_b2_reads()),
        ("no_b2_writes", check_no_b2_writes()),
        ("no_b2_scans", check_no_b2_scans()),
        ("no_recursive_smokes", check_no_recursive_smokes()),
        ("no_bad_hidden_flag_literal", check_no_bad_hidden_flag_literal()),
        ("no_hidden_git_flags_h", check_hidden_git_flags_h()),
        ("no_hidden_git_flags_S", check_hidden_git_flags_S()),
        ("truth_boundary_preserved", check_truth_boundary_preserved()),
        ("no_forbidden_overclaims", check_no_forbidden_overclaims()),
        ("secrets_absent", check_secrets_absent()),
        ("git_diff_check_clean", check_git_diff_check_clean()),
        ("prior_evidence_clean", check_prior_evidence_clean()),
    ]

    all_pass, detail = sl.run_contract_checks(
        "PS-036 Archive / Rehydrate / B2 Audit Vault", checks
    )

    failures: list[str] = []
    for _name, (ok, problems) in checks:
        if not ok:
            failures.extend(problems)

    def _passed(name: str) -> bool:
        return detail.get(name) == "pass"

    report: dict = {
        "ok": bool(all_pass),
        "slice_id": "ps036",
        "route_present": _passed("route_present"),
        "vault_component_present": _passed("vault_component_present"),
        "vault_data_module_present": _passed("vault_data_module_present"),
        "archive_reference_present": _passed("archive_reference_present"),
        "archive_sha256_present": _passed("archive_sha256_present"),
        "manifest_hash_present_or_honestly_unavailable": _passed(
            "manifest_hash_present_or_honestly_unavailable"
        ),
        "rehydrate_source_present": _passed("rehydrate_source_present"),
        "provider_calls_during_rehydrate_present": _passed(
            "provider_calls_during_rehydrate_present"
        ),
        "no_live_provider_call_during_rehydrate_present": _passed(
            "no_live_provider_call_during_rehydrate_present"
        ),
        "b2_evidence_status_present": _passed("b2_evidence_status_present"),
        "local_verification_status_present": _passed(
            "local_verification_status_present"
        ),
        "not_claimed_status_present": _passed("not_claimed_status_present"),
        "boundary_copy_present": _passed("boundary_copy_present"),
        "no_provider_calls": _passed("no_provider_calls"),
        "no_live_b2_reads": _passed("no_b2_reads"),
        "no_b2_writes": _passed("no_b2_writes"),
        "no_broad_b2_scans": _passed("no_b2_scans"),
        "no_recursive_smokes": _passed("no_recursive_smokes"),
        "no_hidden_git_flags_h": _passed("no_hidden_git_flags_h"),
        "no_hidden_git_flags_S": _passed("no_hidden_git_flags_S"),
        "truth_boundary_preserved": _passed("truth_boundary_preserved"),
        "no_forbidden_overclaims": _passed("no_forbidden_overclaims"),
        "prior_evidence_clean": _passed("prior_evidence_clean"),
        "route_or_surface": (
            f"{ROUTE_PATH} (dedicated frontend route) + "
            "B2AuditVault component + nav link from Judge Cockpit Home"
        ),
        "data_source": rel(GOLDEN_DEMO),
        "evidence_dir": "docs/evidence/ps-036/",
        "checked_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "failures": failures,
        "checks_count": len(checks),
        "checks": detail,
    }

    if write_evidence:
        sl.write_json_atomic(EVIDENCE_OUT, report)
        print(f"evidence: {rel(EVIDENCE_OUT)}")

    return 0 if all_pass else 1


def _check_field_present(label: str) -> tuple[bool, list[str]]:
    """Verify a required vault record label is present in the vault surface."""
    problems: list[str] = []
    blob = _vault_blob()
    if label not in blob:
        problems.append(f"vault surface missing required record label {label!r}")
    return (not problems, problems)


if __name__ == "__main__":
    sys.exit(run())
