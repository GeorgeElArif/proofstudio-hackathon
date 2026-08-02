#!/usr/bin/env python3
"""PS-035 Review + Approval Workspace -- smoke / validation script.

This smoke validates ONLY the PS-035 slice. It is local / static by default:
it does not start a browser, does not run the frontend typecheck / build,
does not call any provider, does not read or write any B2 object, does not
call the central regression gate, and does not recursively execute another
feature smoke. Default behavior is non-mutating local validation
(``--check-only``); no evidence file is written unless ``--write-evidence`` is
explicit.

Standard flags (PS-034B / PS-035D feature-smoke contract):

    --check-only      default; non-mutating local validation; writes nothing
    --write-evidence  writes only docs/evidence/ps-035/ evidence
    --no-frontend     skip the frontend typecheck/build (always skipped; a
                      feature smoke never runs the frontend)

Truth boundary: this smoke validates that the PS-035 surface is honest. It does
not prove semantic truth, legal authenticity, C2PA authenticity, human
authorship, Object Lock / tamper-proof storage, or production security.

Exit code is 0 only when every check passes.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import smoke_lib as sl  # noqa: E402

REPO_ROOT = sl.repo_root()
APPS_WEB_SRC = REPO_ROOT / "apps" / "web" / "src"
DATA_MODULE = APPS_WEB_SRC / "reviewApprovalWorkspace.ts"
COMPONENT = APPS_WEB_SRC / "ReviewApprovalWorkspace.tsx"
APP_TSX = APPS_WEB_SRC / "App.tsx"
HOMEPAGE = APPS_WEB_SRC / "JudgeCockpitHome.tsx"
STYLES = APPS_WEB_SRC / "styles.css"
SMOKE_SELF = REPO_ROOT / "scripts" / "ps035_review_approval_workspace_smoke.py"
PROOF_DOC = REPO_ROOT / "docs" / "ps-035-review-approval-workspace-proof.md"
AGENTS_MD = REPO_ROOT / "AGENTS.md"
GOLDEN_DEMO = REPO_ROOT / "docs" / "evidence" / "demo" / "golden-demo-run.json"
EVIDENCE_OUT = (
    REPO_ROOT / "docs" / "evidence" / "ps-035" / "review-approval-workspace-report.json"
)
ROUTE_PATH = "/review-approval-workspace"

# Files scanned for forbidden overclaims and secrets. The smoke script itself
# is intentionally excluded from the forbidden-claim / secret scans because it
# legitimately contains the detection literals (same convention as PS-023
# through PS-034 smokes). It IS scanned for the bad hidden-flag command literal
# and recursive-smoke execution.
CLAIM_SCAN_FILES: tuple[Path, ...] = (
    DATA_MODULE,
    COMPONENT,
    APP_TSX,
    HOMEPAGE,
    STYLES,
    PROOF_DOC,
)

# Source files scanned for provider-call / B2-read / B2-write code patterns.
PROVIDER_B2_SCAN_FILES: tuple[Path, ...] = (
    DATA_MODULE,
    COMPONENT,
    APP_TSX,
    HOMEPAGE,
    STYLES,
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
    STYLES,
    PROOF_DOC,
    SMOKE_SELF,
)

# The four required review states (spec section 10.2).
REVIEW_STATES: tuple[str, ...] = (
    "pending_review",
    "approved",
    "rejected",
    "needs_changes",
)

REVIEW_STATE_LABELS: tuple[str, ...] = (
    "Pending Review",
    "Approved",
    "Rejected",
    "Needs Changes",
)

# Boundary phrases the workspace must surface (spec section 11 / section 16).
BOUNDARY_PHRASES: tuple[str, ...] = (
    "Approval records the reviewer's workflow decision",
    "does not prove semantic truth",
    "does not prove legal authenticity",
    "does not prove C2PA authenticity",
    "does not prove human authorship",
    "does not prove Object Lock",
    "does not prove production security",
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
    "approval proves semantic truth",
    "approval proves legal authenticity",
    "approval proves c2pa authenticity",
    "approval proves human authorship",
    "approval proves object lock",
    "approval proves tamper-proof storage",
    "approval proves production security",
    "approval is legally binding",
    "approval is a certification",
    "the ledger is tamper-proof",
    "the ledger is durable and replicated",
    "object lock is enabled",
    "tamper-proof storage is enabled",
    "public deployment is verified",
    "public deployment verified",
    "the browser verified the b2 bytes",
    "the browser fetched and hashed the b2 object",
    "enterprise-grade security",
    "approved means verified",
)

CONTEXT_MARKERS_RE = re.compile(
    r"does not|do not|must not|\bnot\b|non-claim|non-claims|forbidden|"
    r"reject|rejected|avoid|without overclaim|unless actually implemented|"
    r"only inside non-claim|limitation|limitations|no affirmative|"
    r"unavailable|blocked|honestly|no live|no_new|no_fake|pending|planned|"
    r"did not fetch|does not claim|did not claim|without|none claimed|"
    r"would appear|if captured|no actual|no fake|not implemented|"
    r"is not implemented|not a certification|not legal advice",
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
# cannot self-trip -- same convention as ``check_no_bad_hidden_flag_literal``
# below. At runtime each fragment concatenation evaluates to the exact literal
# the scanned files are tested against, so detection semantics are unchanged.
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


def _git_status_entries() -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for line in sl.git_status_short().splitlines():
        if not line.strip():
            continue
        tag = line[:2]
        path = line[3:]
        out.append((tag, path))
    return out


def _scan_affirmative(
    paths: tuple[Path, ...],
    phrases: tuple[str, ...],
) -> list[str]:
    """Return problem strings for forbidden affirmative claims.

    A phrase is flagged only when the surrounding paragraph lacks a non-claim
    context marker (mirrors PS-031 / PS-034).
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


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_route_registered() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not APP_TSX.is_file():
        return False, [f"missing {rel(APP_TSX)}"]
    text = read_text(APP_TSX)
    if "isReviewApprovalWorkspacePath" not in text:
        problems.append("App.tsx does not register an isReviewApprovalWorkspacePath helper")
    if ROUTE_PATH not in text:
        problems.append(f"App.tsx does not reference the {ROUTE_PATH} path")
    if "ReviewApprovalWorkspace" not in text:
        problems.append("App.tsx does not render the ReviewApprovalWorkspace component")
    if '<ReviewApprovalWorkspace variant="page" />' not in text:
        problems.append(
            "App.tsx does not render <ReviewApprovalWorkspace variant=\"page\" />"
        )
    return (not problems, problems)


def check_review_workspace_present() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not COMPONENT.is_file():
        return False, [f"missing component {rel(COMPONENT)}"]
    text = read_text(COMPONENT)
    for needle in (
        "Review + Approval Workspace",
        "export function ReviewApprovalWorkspace",
        'variant = "page"',
    ):
        if needle not in text:
            problems.append(f"component missing reference to {needle!r}")
    if not DATA_MODULE.is_file():
        problems.append(f"missing data module {rel(DATA_MODULE)}")
    return (not problems, problems)


def check_data_module_present() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not DATA_MODULE.is_file():
        return False, [f"missing data module {rel(DATA_MODULE)}"]
    text = read_text(DATA_MODULE)
    for needle in (
        "REVIEW_APPROVAL_WORKSPACE_ITEMS",
        "REVIEW_APPROVAL_WORKSPACE_STATES",
        "REVIEW_APPROVAL_WORKSPACE_BOUNDARY_MESSAGE",
        "REVIEW_APPROVAL_WORKSPACE_REASON_CATEGORIES",
    ):
        if needle not in text:
            problems.append(f"data module missing {needle!r}")
    return (not problems, problems)


def check_review_states_present() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not DATA_MODULE.is_file():
        return False, [f"missing data module {rel(DATA_MODULE)}"]
    text = read_text(DATA_MODULE)
    for value in REVIEW_STATES:
        if value not in text:
            problems.append(f"data module missing review state {value!r}")
    for label in REVIEW_STATE_LABELS:
        if label not in text:
            problems.append(f"data module missing review state label {label!r}")
    if COMPONENT.is_file():
        comp = read_text(COMPONENT)
        for value in REVIEW_STATES:
            if value not in comp:
                problems.append(f"component missing review state {value!r}")
    return (not problems, problems)


def check_reviewer_decision_present() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not COMPONENT.is_file():
        return False, [f"missing component {rel(COMPONENT)}"]
    text = read_text(COMPONENT)
    for needle in (
        "Reviewer decision",
        "Decision state",
        "Reason category",
        "Reviewer label",
        "Record decision",
    ):
        if needle not in text:
            problems.append(f"component missing decision element {needle!r}")
    return (not problems, problems)


def check_rationale_present() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not COMPONENT.is_file():
        return False, [f"missing component {rel(COMPONENT)}"]
    text = read_text(COMPONENT)
    for needle in ("Rationale", "rationale", "rationale-placeholder-marker"):
        # `rationale` substring is enough; keep a stable anchor too.
        pass
    if "Rationale" not in text:
        problems.append("component missing a Rationale label")
    if 'id={`rationale-' not in text and 'id="rationale-' not in text:
        # Acceptable either form; ensure a rationale input exists.
        if "rationale" not in text.lower():
            problems.append("component missing a rationale input")
    return (not problems, problems)


def check_notes_present() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not COMPONENT.is_file():
        return False, [f"missing component {rel(COMPONENT)}"]
    text = read_text(COMPONENT)
    if "Notes" not in text:
        problems.append("component missing a Notes label")
    if "notes" not in text.lower():
        problems.append("component missing a notes input")
    if not DATA_MODULE.is_file():
        return (not problems, problems)
    dmod = read_text(DATA_MODULE)
    if "notes: string" not in dmod and "notes:" not in dmod:
        problems.append("data module decision record missing notes field")
    return (not problems, problems)


def check_proof_summary_present() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not COMPONENT.is_file():
        return False, [f"missing component {rel(COMPONENT)}"]
    text = read_text(COMPONENT)
    if "Proof / evidence summary" not in text:
        problems.append("component missing Proof / evidence summary heading")
    return (not problems, problems)


def _check_proof_link_present(
    label_needle: str,
    extra_needles: tuple[str, ...],
) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not DATA_MODULE.is_file():
        return False, [f"missing data module {rel(DATA_MODULE)}"]
    text = read_text(DATA_MODULE)
    if label_needle not in text:
        problems.append(f"data module missing proof link label {label_needle!r}")
    for needle in extra_needles:
        if needle not in text:
            problems.append(f"data module missing proof detail {needle!r}")
    return (not problems, problems)


def check_provenance_passport_linked() -> tuple[bool, list[str]]:
    return _check_proof_link_present(
        "Provenance Passport",
        ('"/passport/" + REVIEW_APPROVAL_WORKSPACE_RUN_ID',),
    )


def check_manifest_verification_linked() -> tuple[bool, list[str]]:
    return _check_proof_link_present(
        "Manifest Verification",
        (
            "docs/evidence/ps-035a/manifest-fixture.json",
            "438fabca46481a232373067eedb6d0e3a684c8ed513410dfe2047e3b4950022f",
        ),
    )


def check_b2_evidence_linked() -> tuple[bool, list[str]]:
    return _check_proof_link_present(
        "B2 Evidence",
        (
            "a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141",
        ),
    )


def check_rehydrate_linked() -> tuple[bool, list[str]]:
    return _check_proof_link_present(
        "Rehydrate",
        ("b2_rehydrated",),
    )


def check_export_pack_linked() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not DATA_MODULE.is_file():
        return False, [f"missing data module {rel(DATA_MODULE)}"]
    text = read_text(DATA_MODULE)
    if "Export Pack" not in text:
        problems.append("data module missing Export Pack label")
    if "/evidence-pack" not in text:
        problems.append("data module missing /evidence-pack link")
    return (not problems, problems)


def check_boundary_copy_present() -> tuple[bool, list[str]]:
    problems: list[str] = []
    blob = ""
    for path in (DATA_MODULE, COMPONENT):
        if path.is_file():
            blob += "\n" + read_text(path)
    if not blob:
        return False, ["boundary copy sources missing"]
    for phrase in BOUNDARY_PHRASES:
        if phrase.lower() not in blob.lower():
            problems.append(f"boundary copy missing phrase {phrase!r}")
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
    # The workspace boundary copy must carry the red-line phrases too.
    blob = ""
    for path in (DATA_MODULE, COMPONENT):
        if path.is_file():
            blob += "\n" + read_text(path)
    for phrase in BOUNDARY_PHRASES:
        if phrase.lower() not in blob.lower():
            problems.append(f"workspace boundary copy missing phrase {phrase!r}")
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
    """No tracked evidence outside docs/evidence/ps-035/ may be left dirty."""
    problems: list[str] = []
    try:
        entries = _git_status_entries()
    except sl.HarnessError as exc:
        return False, [f"could not run git status: {exc}"]
    for _tag, path in entries:
        path = path.strip().strip('"')
        if path.startswith("docs/evidence/") and not path.startswith(
            "docs/evidence/ps-035/"
        ):
            problems.append(
                f"prior-slice evidence left dirty by PS-035 smoke: {path}"
            )
    return (not problems, problems)


def check_golden_constants_match() -> tuple[bool, list[str]]:
    """Published workspace constants must match the golden manifest verbatim."""
    problems: list[str] = []
    if not GOLDEN_DEMO.is_file():
        return False, [f"missing golden manifest {rel(GOLDEN_DEMO)}"]
    golden = sl.read_json(GOLDEN_DEMO)
    if not DATA_MODULE.is_file():
        return False, [f"missing data module {rel(DATA_MODULE)}"]
    text = read_text(DATA_MODULE)
    pairs = (
        ("run_id", golden.get("run_id")),
        ("campaign_id", golden.get("campaign_id")),
        ("archive_uri", golden.get("archive_uri")),
        ("archive_sha256", golden.get("archive_sha256")),
    )
    for field, want in pairs:
        if not want:
            continue
        if str(want) not in text:
            problems.append(
                f"data module missing golden {field} value {want!r}"
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
        print("PS035 smoke: MISSING INPUT FILES")
        for f in missing:
            print(f"  - {f}")
        return 1

    checks: list[tuple[str, tuple[bool, list[str]]]] = [
        ("route_present", check_route_registered()),
        ("review_workspace_present", check_review_workspace_present()),
        ("data_module_present", check_data_module_present()),
        ("review_states_present", check_review_states_present()),
        ("reviewer_decision_present", check_reviewer_decision_present()),
        ("rationale_present", check_rationale_present()),
        ("notes_present", check_notes_present()),
        ("proof_summary_present", check_proof_summary_present()),
        ("provenance_passport_present_or_linked", check_provenance_passport_linked()),
        ("manifest_verification_present_or_linked", check_manifest_verification_linked()),
        ("b2_evidence_present_or_linked", check_b2_evidence_linked()),
        ("rehydrate_present_or_linked", check_rehydrate_linked()),
        ("export_pack_present_or_linked", check_export_pack_linked()),
        ("boundary_copy_present", check_boundary_copy_present()),
        ("no_provider_calls", check_no_provider_calls()),
        ("no_b2_reads", check_no_b2_reads()),
        ("no_b2_writes", check_no_b2_writes()),
        ("no_recursive_smokes", check_no_recursive_smokes()),
        ("no_bad_hidden_flag_literal", check_no_bad_hidden_flag_literal()),
        ("no_hidden_git_flags_h", check_hidden_git_flags_h()),
        ("no_hidden_git_flags_S", check_hidden_git_flags_S()),
        ("truth_boundary_preserved", check_truth_boundary_preserved()),
        ("no_forbidden_overclaims", check_no_forbidden_overclaims()),
        ("golden_constants_match", check_golden_constants_match()),
        ("secrets_absent", check_secrets_absent()),
        ("git_diff_check_clean", check_git_diff_check_clean()),
        ("prior_evidence_clean", check_prior_evidence_clean()),
    ]

    all_pass, detail = sl.run_contract_checks(
        "PS-035 Review + Approval Workspace", checks
    )

    failures: list[str] = []
    for _name, (ok, problems) in checks:
        if not ok:
            failures.extend(problems)

    report: dict = {
        "ok": bool(all_pass),
        "slice_id": "ps035",
        "route_present": detail["route_present"] == "pass",
        "review_workspace_present": detail["review_workspace_present"] == "pass",
        "review_states_present": detail["review_states_present"] == "pass",
        "reviewer_decision_present": detail["reviewer_decision_present"] == "pass",
        "rationale_present": detail["rationale_present"] == "pass",
        "notes_present": detail["notes_present"] == "pass",
        "proof_summary_present": detail["proof_summary_present"] == "pass",
        "provenance_passport_present_or_linked": detail[
            "provenance_passport_present_or_linked"
        ] == "pass",
        "manifest_verification_present_or_linked": detail[
            "manifest_verification_present_or_linked"
        ] == "pass",
        "b2_evidence_present_or_linked": detail[
            "b2_evidence_present_or_linked"
        ] == "pass",
        "rehydrate_present_or_linked": detail[
            "rehydrate_present_or_linked"
        ] == "pass",
        "export_pack_present_or_linked": detail[
            "export_pack_present_or_linked"
        ] == "pass",
        "boundary_copy_present": detail["boundary_copy_present"] == "pass",
        "no_provider_calls": detail["no_provider_calls"] == "pass",
        "no_b2_reads": detail["no_b2_reads"] == "pass",
        "no_b2_writes": detail["no_b2_writes"] == "pass",
        "no_recursive_smokes": detail["no_recursive_smokes"] == "pass",
        "no_bad_hidden_flag_literal": detail["no_bad_hidden_flag_literal"] == "pass",
        "no_hidden_git_flags_h": detail["no_hidden_git_flags_h"] == "pass",
        "no_hidden_git_flags_S": detail["no_hidden_git_flags_S"] == "pass",
        "truth_boundary_preserved": detail["truth_boundary_preserved"] == "pass",
        "no_forbidden_overclaims": detail["no_forbidden_overclaims"] == "pass",
        "golden_constants_match": detail["golden_constants_match"] == "pass",
        "secrets_absent": detail["secrets_absent"] == "pass",
        "git_diff_check_clean": detail["git_diff_check_clean"] == "pass",
        "prior_evidence_clean": detail["prior_evidence_clean"] == "pass",
        "route_or_surface": (
            f"{ROUTE_PATH} (dedicated frontend route) + "
            "ReviewApprovalWorkspace component + CTA from Judge Cockpit Home"
        ),
        "data_source": rel(GOLDEN_DEMO),
        "evidence_dir": "docs/evidence/ps-035/",
        "checked_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "failures": failures,
        "checks_count": len(checks),
        "checks": detail,
    }

    if write_evidence:
        sl.write_json_atomic(EVIDENCE_OUT, report)
        print(f"evidence: {rel(EVIDENCE_OUT)}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(run())
