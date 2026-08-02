#!/usr/bin/env python3
"""PS-035C Non-Mutating Regression Gate Mode -- local / static smoke.

This smoke is LOCAL / STATIC ONLY. It:

- runs the central regression gate (``scripts/proofstudio_regression_gate.py``)
  in its PS-035C write modes and proves the non-mutating contract
- does not call providers
- does not read or write B2
- does not run the frontend (the gate is invoked with --no-frontend)
- does not call any feature smoke
- does not mutate prior evidence
- writes only:
  ``docs/evidence/ps-035c/non-mutating-regression-gate-mode-report.json``

It proves:

- ``--check-only`` is supported and is the default for a non-PS034A slice
- ``--report-out <path>`` writes only to the requested path
- ``--write-report`` is supported for ``--current ps034a`` and is rejected for
  any non-PS034A current slice
- the canonical tracked PS-034A report
  (``docs/evidence/ps-034a/smoke-harness-v1-report.json``) is never written as
  a side effect of validating a later slice
- conflicting write modes error out before any file is written
- the frontend is not run unless explicitly requested
- no live provider call, no live B2 read, and no live B2 write occur

The single exception to "never touch the canonical PS-034A report" is the
explicit ``--current ps034a --write-report`` proof, which regenerates the
canonical report by design and is restored from git immediately afterward
(verified by SHA-256 digest). This is the only permitted canonical-report
write, and it is wrapped so the restore always runs.

Exit code is 0 only when every check passes.

    python scripts/ps035c_non_mutating_regression_gate_mode_smoke.py
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
GATE = SCRIPTS / "proofstudio_regression_gate.py"
GATE_SRC = GATE.read_text(encoding="utf-8", errors="replace")
REPORT = (
    ROOT / "docs" / "evidence" / "ps-035c"
    / "non-mutating-regression-gate-mode-report.json"
)
CANONICAL_PS034A = (
    ROOT / "docs" / "evidence" / "ps-034a" / "smoke-harness-v1-report.json"
)
PROOF_DOC = ROOT / "docs" / "ps-035c-non-mutating-regression-gate-mode-proof.md"

# Allowed changed files for PS-035C (mirrors the spec section 8 implementation
# candidates plus this smoke and its evidence).
ALLOWED_CHANGED_FILES = {
    "scripts/proofstudio_regression_gate.py",
    "scripts/ps034a_smoke_harness_v1_smoke.py",
    "scripts/ps035c_non_mutating_regression_gate_mode_smoke.py",
    "docs/evidence/ps-035c/non-mutating-regression-gate-mode-report.json",
    "docs/ps-035c-non-mutating-regression-gate-mode-proof.md",
    "docs/validation/proofstudio-smoke-harness-v1.md",
    "specs/07-master-spec-plan.md",
    "specs/08-roadmap-slices.md",
}

# Forbidden positive overclaim phrases. A phrase is acceptable only if a
# negation cue appears within the context window around it.
FORBIDDEN_OVERCLAIM_PHRASES = [
    "tamper-proof storage",
    "tamper proof storage",
    "Object Lock enabled",
    "live B2 Object Lock",
    "real billing API integration",
    "production multi-user budget accounting",
    "production immutability",
    "B2 immutability",
    "C2PA authentic",
    "production security verified",
    "product correctness verified",
    "human authorship verified",
    "legal authenticity verified",
    "semantic truth verified",
]

NEGATION_CUES = (
    "does not",
    "do not",
    "doesn't",
    "don't",
    "did not",
    "not prove",
    "not claim",
    "must not",
    "no claim",
    "no claim of",
    "no overclaim",
    "without",
    "non-claim",
    "never claim",
    "not implemented",
    "forbidden",
    "is not",
    "are not",
    "cannot",
    "not a ",
    "not an ",
    "not tamper-proof",
    "not object lock",
    "not production immutability",
    "not real billing",
    "not production multi-user",
    "not b2 immutability",
    "not product correctness",
    "not production security",
)

_OVERCLAIM_BEFORE_WINDOW = 260
_OVERCLAIM_AFTER_WINDOW = 200
_WS_RE = re.compile(r"\s+")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _flat(text: str) -> str:
    return _WS_RE.sub(" ", text).strip()


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


def _no_forbidden_overclaims_in_text(text: str, label: str, failures: list[str]) -> bool:
    flat_low = _flat(text).lower()
    ok = True
    for phrase in FORBIDDEN_OVERCLAIM_PHRASES:
        p_low = phrase.lower()
        start = 0
        while True:
            idx = flat_low.find(p_low, start)
            if idx == -1:
                break
            win_start = max(0, idx - _OVERCLAIM_BEFORE_WINDOW)
            win_end = min(len(flat_low), idx + len(p_low) + _OVERCLAIM_AFTER_WINDOW)
            window = flat_low[win_start:win_end]
            if not any(cue.lower() in window for cue in NEGATION_CUES):
                failures.append(
                    f"no_forbidden_overclaims/{label}: phrase {phrase!r} "
                    f"appears as a positive claim (no negation cue in context)"
                )
                ok = False
            start = idx + len(p_low)
    return ok


def _run_gate(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(GATE), *args],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=300,
    )


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


# Hidden Git index flags. Per `git ls-files -v`, the first character of each
# line is the marker: lowercase letters indicate assume-unchanged bits are set
# and `S` (uppercase) indicates the skip-worktree bit is set. The no-hidden-
# Git-flags policy must catch both:
#   h = assume-unchanged
#   S = skip-worktree
_HIDDEN_GIT_MARKERS = {"h", "S"}


def _hidden_git_flag_paths() -> list[str]:
    """Return tracked paths whose index entry has a hidden Git flag set.

    Reads ``git ls-files -v``; for every line the marker is ``line[0]``. A path
    is reported when its marker is ``h`` (assume-unchanged) or ``S``
    (skip-worktree).
    """
    res = subprocess.run(
        ["git", "ls-files", "-v"], cwd=str(ROOT), capture_output=True, text=True
    )
    offenders: list[str] = []
    for line in res.stdout.splitlines():
        if not line:
            continue
        marker = line[0]
        if marker in _HIDDEN_GIT_MARKERS:
            parts = line.split(None, 1)
            offenders.append(parts[1] if len(parts) > 1 else line)
    return offenders


def _no_hidden_git_flags() -> bool:
    return not _hidden_git_flag_paths()


def main() -> int:
    failures: list[str] = []

    baseline_digest = _sha256_file(CANONICAL_PS034A)
    if baseline_digest is None:
        failures.append(
            "setup: canonical PS-034A report missing at "
            f"{CANONICAL_PS034A}"
        )

    _pre_hidden = _hidden_git_flag_paths()
    if _pre_hidden:
        failures.append(
            "no_hidden_git_flags: hidden git index flags present before: "
            + ", ".join(_pre_hidden)
        )

    # ---- CLI flags present in the gate source ----
    current_flag_supported = "--current" in GATE_SRC
    frontend_flag_supported = "--frontend" in GATE_SRC
    no_frontend_flag_supported = "--no-frontend" in GATE_SRC
    check_only_flag_in_source = "--check-only" in GATE_SRC
    report_out_flag_in_source = "--report-out" in GATE_SRC
    write_report_flag_in_source = "--write-report" in GATE_SRC
    for flag, present in (
        ("--current", current_flag_supported),
        ("--frontend", frontend_flag_supported),
        ("--no-frontend", no_frontend_flag_supported),
        ("--check-only", check_only_flag_in_source),
        ("--report-out", report_out_flag_in_source),
        ("--write-report", write_report_flag_in_source),
    ):
        if not present:
            failures.append(f"cli_flags: gate does not expose {flag}")

    # ---- default invocation for a later slice is non-mutating (check-only) ----
    default_res = _run_gate(["--current", "ps035c", "--no-frontend"])
    default_is_check_only = (
        default_res.returncode == 0
        and "write_mode: check_only" in default_res.stdout
        and "report: not written" in default_res.stdout
        and "non_mutating_gate: True" in default_res.stdout
    )
    if not default_is_check_only:
        failures.append(
            "default_is_check_only_for_non_ps034a: default ps035c run did not "
            f"report check-only non-mutating mode\nstdout:\n{default_res.stdout}"
            f"\nstderr:\n{default_res.stderr}"
        )
    default_digest_after = _sha256_file(CANONICAL_PS034A)
    default_digest_unchanged = (
        baseline_digest is not None
        and default_digest_after == baseline_digest
    )
    if not default_digest_unchanged:
        failures.append(
            "default_is_check_only_for_non_ps034a: canonical PS-034A report "
            "digest changed after default ps035c run"
        )

    # ---- explicit --check-only supported and leaves git clean + digest unchanged ----
    check_only_res = _run_gate(["--current", "ps035c", "--no-frontend", "--check-only"])
    write_mode_check_only_supported = (
        check_only_res.returncode == 0
        and "write_mode: check_only" in check_only_res.stdout
        and "ps034a_report_digest_unchanged: True" in check_only_res.stdout
    )
    if not write_mode_check_only_supported:
        failures.append(
            "write_mode_check_only_supported: --check-only did not pass or did "
            f"not report check-only mode\nstdout:\n{check_only_res.stdout}"
            f"\nstderr:\n{check_only_res.stderr}"
        )
    check_only_digest_after = _sha256_file(CANONICAL_PS034A)
    check_only_leaves_ps034a_digest_unchanged = (
        baseline_digest is not None
        and check_only_digest_after == baseline_digest
    )
    if not check_only_leaves_ps034a_digest_unchanged:
        failures.append(
            "check_only_leaves_ps034a_digest_unchanged: canonical PS-034A "
            "report digest changed after --check-only run"
        )
    # check-only must leave git status clean except PS-035C implementation files.
    check_only_leaves_git_clean = True
    for path in _git_status_paths():
        if path not in ALLOWED_CHANGED_FILES:
            failures.append(
                "check_only_leaves_git_clean: unexpected dirty path after "
                f"--check-only: {path}"
            )
            check_only_leaves_git_clean = False
    if (
        "docs/evidence/ps-034a/smoke-harness-v1-report.json"
        in _git_status_paths()
    ):
        failures.append(
            "check_only_leaves_git_clean: canonical PS-034A report is dirty "
            "after --check-only"
        )
        check_only_leaves_git_clean = False

    # ---- explicit --report-out supported; writes only requested out-of-tree path ----
    report_out_path = Path("/tmp/proofstudio-ps035c-regression-report.json")
    if report_out_path.exists():
        report_out_path.unlink()
    report_out_res = _run_gate(
        ["--current", "ps035c", "--no-frontend", "--report-out", str(report_out_path)]
    )
    report_out_report: dict = {}
    report_out_writes_only_to_requested_path = False
    report_out_does_not_dirty_tracked_evidence = True
    if report_out_res.returncode != 0:
        failures.append(
            "write_mode_report_out_supported: --report-out did not pass\n"
            f"stdout:\n{report_out_res.stdout}\nstderr:\n{report_out_res.stderr}"
        )
    else:
        if "write_mode: report_out" not in report_out_res.stdout:
            failures.append(
                "write_mode_report_out_supported: --report-out did not report "
                "report_out mode"
            )
        if not report_out_path.is_file():
            failures.append(
                "report_out_writes_only_to_requested_path: requested /tmp "
                f"report not written at {report_out_path}"
            )
        else:
            try:
                report_out_report = json.loads(_read_text(report_out_path))
            except json.JSONDecodeError as exc:
                failures.append(
                    f"report_out_writes_only_to_requested_path: invalid JSON: {exc}"
                )
            report_out_writes_only_to_requested_path = (
                report_out_report.get("write_mode") == "report_out"
                and report_out_report.get("report_path") == str(report_out_path)
                and report_out_report.get("non_mutating_gate") is True
                and report_out_report.get("ps034a_report_digest_unchanged") is True
            )
            if not report_out_writes_only_to_requested_path:
                failures.append(
                    "report_out_writes_only_to_requested_path: report-out "
                    f"fields mismatch: {report_out_report}"
                )
    report_out_digest_after = _sha256_file(CANONICAL_PS034A)
    if not (
        baseline_digest is not None
        and report_out_digest_after == baseline_digest
    ):
        failures.append(
            "report_out_does_not_dirty_tracked_evidence: canonical PS-034A "
            "report digest changed after --report-out run"
        )
        report_out_does_not_dirty_tracked_evidence = False
    if (
        "docs/evidence/ps-034a/smoke-harness-v1-report.json"
        in _git_status_paths()
    ):
        failures.append(
            "report_out_does_not_dirty_tracked_evidence: canonical PS-034A "
            "report is dirty after --report-out"
        )
        report_out_does_not_dirty_tracked_evidence = False

    # Clean up the /tmp report-out artifact.
    if report_out_path.exists():
        report_out_path.unlink()

    # ---- --write-report supported for ps034a (regenerate + immediate restore) ----
    write_report_required_for_canonical_ps034a_report = False
    write_report_supported = False
    write_res = _run_gate(
        ["--current", "ps034a", "--no-frontend", "--write-report"]
    )
    try:
        if write_res.returncode != 0:
            failures.append(
                "write_mode_write_report_supported: --current ps034a "
                f"--write-report did not pass\nstdout:\n{write_res.stdout}"
                f"\nstderr:\n{write_res.stderr}"
            )
        elif "write_mode: write_report" not in write_res.stdout:
            failures.append(
                "write_mode_write_report_supported: --write-report did not "
                "report write_report mode"
            )
        else:
            write_report_supported = True
        # The canonical report must have been regenerated (digest changed).
        write_digest_after = _sha256_file(CANONICAL_PS034A)
        canonical_was_written = (
            baseline_digest is not None
            and write_digest_after is not None
            and write_digest_after != baseline_digest
        )
        if not canonical_was_written:
            failures.append(
                "write_mode_write_report_supported: --write-report did not "
                "regenerate the canonical PS-034A report (digest unchanged)"
            )
        # Immediate restore from git (the only permitted canonical-report write).
        restore = subprocess.run(
            ["git", "checkout", "--", str(CANONICAL_PS034A)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        if restore.returncode != 0:
            failures.append(
                "write_mode_write_report_supported: git restore of canonical "
                f"PS-034A report failed\nstderr:\n{restore.stderr}"
            )
        restored_digest = _sha256_file(CANONICAL_PS034A)
        if not (
            baseline_digest is not None
            and restored_digest == baseline_digest
        ):
            failures.append(
                "write_mode_write_report_supported: canonical PS-034A report "
                "digest not restored to baseline after --write-report proof"
            )
        else:
            write_report_required_for_canonical_ps034a_report = (
                write_report_supported and canonical_was_written
            )
    finally:
        # Guarantee the canonical report is restored even on exception.
        subprocess.run(
            ["git", "checkout", "--", str(CANONICAL_PS034A)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )

    # ---- conflicting flags fail before writing ----
    conflicts_ok = True
    conflict_cases = [
        (["--current", "ps035c", "--no-frontend", "--check-only", "--write-report"],
         "--check-only + --write-report"),
        (["--current", "ps035c", "--no-frontend", "--check-only",
          "--report-out", "/tmp/proofstudio-ps035c-conflict-a.json"],
         "--check-only + --report-out"),
        (["--current", "ps035c", "--no-frontend",
          "--report-out", "/tmp/proofstudio-ps035c-conflict-b.json",
          "--write-report"],
         "--report-out + --write-report"),
    ]
    for args, label in conflict_cases:
        res = _run_gate(args)
        if res.returncode == 0:
            failures.append(
                f"conflict_handling/{label}: conflicting flags did not error "
                f"(exit 0)\nstdout:\n{res.stdout}"
            )
            conflicts_ok = False
    # No file may be written by a conflict case.
    for tmp in (
        "/tmp/proofstudio-ps035c-conflict-a.json",
        "/tmp/proofstudio-ps035c-conflict-b.json",
    ):
        if Path(tmp).exists():
            failures.append(
                f"conflict_handling: file written despite conflict: {tmp}"
            )
            conflicts_ok = False
            Path(tmp).unlink()

    # ---- --write-report for a non-PS034A slice is rejected before writing ----
    reject_res = _run_gate(["--current", "ps035c", "--no-frontend", "--write-report"])
    write_report_rejected_for_non_ps034a = reject_res.returncode != 0
    if not write_report_rejected_for_non_ps034a:
        failures.append(
            "write_mode_write_report_supported: --write-report was not rejected "
            "for a non-PS034A current slice"
        )

    # ---- frontend not run unless requested ----
    frontend_not_run_unless_requested = (
        report_out_report.get("frontend_ran") is False
        and "REGRESSION GATE PASSED" in report_out_res.stdout
    )
    if not frontend_not_run_unless_requested:
        failures.append(
            "frontend_not_run_unless_requested: gate ran the frontend or "
            "report-out report did not carry frontend_ran=false"
        )

    # ---- no provider calls / no B2 reads / no B2 writes (static proof) ----
    no_provider_calls = bool(report_out_report.get("no_provider_call") is True)
    no_b2_reads = bool(report_out_report.get("no_broad_b2_read") is True)
    # The gate and this smoke import no B2/provider modules and make no live B2
    # write. Assert statically that the gate source references no b2 module.
    no_b2_writes = "b2sdk" not in GATE_SRC and "b2_upload" not in GATE_SRC
    if not no_provider_calls:
        failures.append(
            "no_provider_calls: gate report-out did not assert no_provider_call"
        )
    if not no_b2_reads:
        failures.append(
            "no_b2_reads: gate report-out did not assert no_broad_b2_read"
        )
    if not no_b2_writes:
        failures.append("no_b2_writes: gate source references a b2 module")

    _post_hidden = _hidden_git_flag_paths()
    if _post_hidden:
        failures.append(
            "no_hidden_git_flags: hidden git index flags present after: "
            + ", ".join(_post_hidden)
        )
    no_hidden_git_flags = not _post_hidden

    # ---- truth boundary preserved in the proof doc ----
    proof_flat = _flat(_read_text(PROOF_DOC)).lower()
    truth_boundary_preserved = (
        "truth boundary" in proof_flat
        and "not tamper-proof" in proof_flat
        and "not b2 immutability" in proof_flat
        and "not production security" in proof_flat
        and "validation mutation" in proof_flat
    )
    if not truth_boundary_preserved:
        failures.append(
            "truth_boundary_preserved: proof doc missing truth boundary / "
            "non-claims (not tamper-proof, not B2 immutability, not production "
            "security, validation mutation)"
        )

    # ---- no forbidden overclaims in proof doc ----
    no_forbidden_overclaims = _no_forbidden_overclaims_in_text(
        _read_text(PROOF_DOC), "proof_doc", failures
    )

    # ---- no forbidden file changes ----
    no_forbidden_file_changes = True
    try:
        changed = _git_status_paths()
    except Exception as exc:  # pragma: no cover - defensive
        failures.append(f"no_forbidden_file_changes: git status failed: {exc}")
        no_forbidden_file_changes = False
        changed = []
    for path in changed:
        if path not in ALLOWED_CHANGED_FILES:
            failures.append(
                f"no_forbidden_file_changes: forbidden/out-of-allowed path "
                f"changed: {path}"
            )
            no_forbidden_file_changes = False

    # ---- final canonical digest cross-check ----
    final_digest = _sha256_file(CANONICAL_PS034A)
    non_mutating_gate = (
        baseline_digest is not None
        and final_digest is not None
        and baseline_digest == final_digest
    )
    if not non_mutating_gate:
        failures.append(
            "non_mutating_gate: canonical PS-034A report digest differs from "
            "baseline at end of smoke"
        )

    ok = (
        current_flag_supported
        and frontend_flag_supported
        and no_frontend_flag_supported
        and check_only_flag_in_source
        and report_out_flag_in_source
        and write_report_flag_in_source
        and write_mode_check_only_supported
        and write_report_supported
        and report_out_writes_only_to_requested_path
        and default_is_check_only
        and check_only_leaves_git_clean
        and check_only_leaves_ps034a_digest_unchanged
        and report_out_does_not_dirty_tracked_evidence
        and write_report_required_for_canonical_ps034a_report
        and conflicts_ok
        and write_report_rejected_for_non_ps034a
        and frontend_not_run_unless_requested
        and no_provider_calls
        and no_b2_reads
        and no_b2_writes
        and no_hidden_git_flags
        and truth_boundary_preserved
        and no_forbidden_overclaims
        and no_forbidden_file_changes
        and non_mutating_gate
        and not failures
    )

    report = {
        "ok": bool(ok),
        "slice_id": "ps035c",
        "checked_at": _utc_now_iso(),
        "non_mutating_gate": bool(non_mutating_gate),
        "write_mode_check_only_supported": bool(write_mode_check_only_supported),
        "write_mode_report_out_supported": bool(
            report_out_writes_only_to_requested_path
        ),
        "write_mode_write_report_supported": bool(write_report_supported),
        "default_is_check_only_for_non_ps034a": bool(default_is_check_only),
        "check_only_leaves_git_clean": bool(check_only_leaves_git_clean),
        "check_only_leaves_ps034a_digest_unchanged": bool(
            check_only_leaves_ps034a_digest_unchanged
        ),
        "report_out_writes_only_to_requested_path": bool(
            report_out_writes_only_to_requested_path
        ),
        "report_out_does_not_dirty_tracked_evidence": bool(
            report_out_does_not_dirty_tracked_evidence
        ),
        "write_report_required_for_canonical_ps034a_report": bool(
            write_report_required_for_canonical_ps034a_report
        ),
        "write_report_rejected_for_non_ps034a": bool(
            write_report_rejected_for_non_ps034a
        ),
        "conflicting_flags_rejected_before_write": bool(conflicts_ok),
        "current_flag_supported": bool(current_flag_supported),
        "frontend_flag_supported": bool(frontend_flag_supported),
        "no_frontend_flag_supported": bool(no_frontend_flag_supported),
        "no_provider_calls": bool(no_provider_calls),
        "no_b2_reads": bool(no_b2_reads),
        "no_b2_writes": bool(no_b2_writes),
        "no_hidden_git_flags": bool(no_hidden_git_flags),
        "frontend_not_run_unless_requested": bool(frontend_not_run_unless_requested),
        "truth_boundary_preserved": bool(truth_boundary_preserved),
        "no_forbidden_overclaims": bool(no_forbidden_overclaims),
        "no_forbidden_file_changes": bool(no_forbidden_file_changes),
        "ps034a_report_digest": {
            "baseline_sha256": baseline_digest,
            "final_sha256": final_digest,
            "canonical_path": str(CANONICAL_PS034A.relative_to(ROOT)),
        },
        "truth_boundary": (
            "ProofStudio proves what the pipeline did. PS-035C fixes validation "
            "mutation only: the central regression gate, in non-mutating mode, "
            "no longer overwrites tracked historical PS-034A evidence as a side "
            "effect of validating a later slice. PS-035C does not prove product "
            "correctness, production security, B2 immutability, tamper-proof "
            "storage, real billing API integration, billing behavior, semantic "
            "truth, legal authenticity, C2PA authenticity, human authorship, or "
            "browser-side B2 byte verification."
        ),
        "non_claims": {
            "not_product_correctness": True,
            "not_production_security": True,
            "not_b2_immutability": True,
            "not_tamper_proof": True,
            "not_real_billing_api_integration": True,
            "not_billing_behavior": True,
        },
        "failures": failures,
    }

    # Scan the assembled report JSON text for forbidden overclaims before write.
    report_text = json.dumps(report, indent=2, sort_keys=False)
    if not _no_forbidden_overclaims_in_text(report_text, "report", failures):
        no_forbidden_overclaims = False
        report["no_forbidden_overclaims"] = False
        ok = False
        report["ok"] = False
        report["failures"] = failures

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(report, indent=2, sort_keys=False) + "\n"
    tmp = REPORT.with_suffix(REPORT.suffix + ".tmp")
    tmp.write_text(payload, encoding="utf-8")
    os.replace(tmp, REPORT)

    if failures:
        print("PS-035C NON-MUTATING REGRESSION GATE MODE SMOKE FAILED", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("PS-035C NON-MUTATING REGRESSION GATE MODE SMOKE PASSED")
    print(f"  write_mode_check_only_supported: {report['write_mode_check_only_supported']}")
    print(f"  write_mode_report_out_supported: {report['write_mode_report_out_supported']}")
    print(f"  write_mode_write_report_supported: {report['write_mode_write_report_supported']}")
    print(f"  default_is_check_only_for_non_ps034a: {report['default_is_check_only_for_non_ps034a']}")
    print(f"  check_only_leaves_ps034a_digest_unchanged: {report['check_only_leaves_ps034a_digest_unchanged']}")
    print(f"  report_out_does_not_dirty_tracked_evidence: {report['report_out_does_not_dirty_tracked_evidence']}")
    print(f"  write_report_required_for_canonical_ps034a_report: {report['write_report_required_for_canonical_ps034a_report']}")
    print(f"  write_report_rejected_for_non_ps034a: {report['write_report_rejected_for_non_ps034a']}")
    print(f"  conflicting_flags_rejected_before_write: {report['conflicting_flags_rejected_before_write']}")
    print(f"  non_mutating_gate: {report['non_mutating_gate']}")
    print(f"  report: {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
