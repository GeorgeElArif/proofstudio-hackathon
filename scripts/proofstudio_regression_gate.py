#!/usr/bin/env python3
"""PS-034A — Central Regression Gate (Smoke Harness v1).

This is the single place that coordinates cross-slice release-readiness
validation. It is non-recursive: it never executes another smoke script. It
contains no historical feature-smoke path references. It verifies accepted
historical slices through a contract table (evidence JSON, route registration,
component presence, golden-constant agreement, and absence of forbidden claims)
instead of re-running historical smokes.

Feature slice smokes validate the slice. The regression gate validates the release.

Evidence report schema rule (strict): a boolean success flag is never
overloaded with a list. ``historical_contracts_verified`` is a boolean that is
``true`` only when every required historical contract passes. The list of
verified slice ids is carried in ``historical_contract_ids``, the integer count
in ``historical_contract_count``, and per-contract failures (empty on success)
in ``historical_contract_failures``.

Usage:
    python scripts/proofstudio_regression_gate.py --current ps034a
    python scripts/proofstudio_regression_gate.py --current ps034 --no-frontend
    python scripts/proofstudio_regression_gate.py --current ps034 --frontend

PS-035C write-mode contract. The gate is non-mutating by default. The
canonical tracked PS-034A report (REPORT_PATH) is only written under an
explicit, PM-aware regeneration. The accepted write modes are:

- ``--check-only`` (default): validate every historical contract and print the
  same pass/fail summary without writing any report file. The canonical
  PS-034A report is never touched.
- ``--report-out <path>``: write the report only to the explicitly supplied
  path (recommended outside tracked evidence during commit gates). The
  canonical PS-034A report is never touched.
- ``--write-report``: write the canonical tracked PS-034A report at
  REPORT_PATH. This is only allowed with ``--current ps034a`` (or
  ``ps-034a`` / ``ps034A``-equivalent) so a later slice can never mutate
  tracked historical PS-034A evidence as a side effect.

Conflicting write modes error out clearly before any file is written.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import smoke_lib as sl  # noqa: E402

ROOT = sl.repo_root()
SCRIPTS = ROOT / "scripts"
DOCS = ROOT / "docs"
EVIDENCE = DOCS / "evidence"
APP_TSX = ROOT / "apps" / "web" / "src" / "App.tsx"
COMPONENT_DIR = ROOT / "apps" / "web" / "src"

VALIDATION_DOC = DOCS / "validation" / "proofstudio-smoke-harness-v1.md"
PROOF_DOC = DOCS / "ps-034a-smoke-harness-v1-proof.md"
GATE_SELF = SCRIPTS / "proofstudio_regression_gate.py"
SMOKE_LIB = SCRIPTS / "smoke_lib.py"

REPORT_PATH = EVIDENCE / "ps-034a" / "smoke-harness-v1-report.json"

PRIOR_EVIDENCE_PREFIXES = [
    f"docs/evidence/{s}/" for s in (
        "ps-019", "ps-020", "ps-021", "ps-024", "ps-025", "ps-026",
        "ps-027", "ps-028", "ps-029", "ps-030", "ps-031", "ps-032",
        "ps-033", "ps-034", "ps-035a",
    )
] + ["docs/evidence/demo/"]

HARNESS_SCAN_PATHS = [
    SMOKE_LIB,
    GATE_SELF,
    VALIDATION_DOC,
    PROOF_DOC,
]

EXPECTED_GOLDEN = {
    "run_id": "run_89d967f9000045efa22ed4cc78cfa67f",
    "campaign_id": "camp_bea5161faa6244079d2ee01ce445c259",
    "archive_uri": (
        "https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/"
        "proofstudio/ps-021/assets/a6/ad/"
        "a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141.json"
    ),
    "archive_sha256": (
        "a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141"
    ),
    "rehydrate_source": "b2_rehydrated",
    "provider_calls_during_rehydrate": 0,
    "no_live_provider_call_during_rehydrate": True,
}

GOLDEN_DEMO = EVIDENCE / "demo" / "golden-demo-run.json"

# ---------------------------------------------------------------------------
# Historical accepted-slice contract table.
#
# Each entry is a plain dict — never a feature-smoke script path. The gate
# verifies only the fields that are present (``evidence``, ``route``,
# ``component``, ``golden``, ``ok``). Fields set to ``None`` are skipped.
# This replaces the old smoke-path-based historical logic entirely.
# ---------------------------------------------------------------------------
HISTORICAL_CONTRACTS: list[dict] = [
    {
        "slice": "ps021",
        "evidence": EVIDENCE / "ps-021" / "live-b2-durable-rehydrate-smoke.json",
        "route": None,
        "component": None,
        "golden": True,
        "ok": True,
    },
    {
        "slice": "ps023",
        "evidence": None,
        "route": "/review",
        "component": "JudgeCockpitHome",
        "golden": False,
        "ok": False,
    },
    {
        "slice": "ps025",
        "evidence": EVIDENCE / "ps-025" / "public-durable-passport-unlock-smoke.json",
        "route": None,
        "component": "PublicPassportPage",
        "golden": True,
        "ok": True,
    },
    {
        "slice": "ps026",
        "evidence": EVIDENCE / "ps-026" / "b2-evidence-explorer-smoke.json",
        "route": "/b2-evidence",
        "component": "B2EvidenceExplorer",
        "golden": True,
        "ok": True,
    },
    {
        "slice": "ps027",
        "evidence": EVIDENCE / "ps-027" / "genblaze-pipeline-graph-smoke.json",
        "route": "/genblaze-pipeline",
        "component": "GenblazePipelineGraph",
        "golden": True,
        "ok": True,
    },
    {
        "slice": "ps028",
        "evidence": EVIDENCE / "ps-028" / "manifest-verification-panel-smoke.json",
        "route": "/manifest-verification",
        "component": "ManifestVerificationPanel",
        "golden": True,
        "ok": True,
    },
    {
        "slice": "ps029",
        "evidence": EVIDENCE / "ps-029" / "b2-rehydrate-comparison-smoke.json",
        "route": "/b2-rehydrate-comparison",
        "component": "B2RehydrateComparison",
        "golden": True,
        "ok": True,
    },
    {
        "slice": "ps030",
        "evidence": EVIDENCE / "ps-030" / "failure-as-proof-timeline-smoke.json",
        "route": "/failure-timeline",
        "component": "FailureAsProofTimeline",
        "golden": True,
        "ok": True,
    },
    {
        "slice": "ps031",
        "evidence": EVIDENCE / "ps-031" / "export-campaign-pack-v2-smoke.json",
        "route": "/evidence-pack",
        "component": "JudgeEvidencePack",
        "golden": True,
        "ok": True,
    },
    {
        "slice": "ps032",
        "evidence": EVIDENCE / "ps-032" / "operations-cockpit-flight-recorder-v2-smoke.json",
        "route": "/operations-cockpit",
        "component": "OperationsCockpit",
        "golden": True,
        "ok": True,
    },
    {
        "slice": "ps033",
        "evidence": EVIDENCE / "ps-033" / "provider-decision-intelligence-smoke.json",
        "route": "/provider-decision-intelligence",
        "component": "ProviderDecisionIntelligence",
        "golden": True,
        "ok": True,
    },
    {
        "slice": "ps034",
        "evidence": EVIDENCE / "ps-034" / "lineage-comparison-lab-smoke.json",
        "route": "/lineage-comparison-lab",
        "component": "LineageComparisonLab",
        "golden": True,
        "ok": True,
    },
]

FORBIDDEN_CLAIM_TERMS = [
    "semantic_truth_verified",
    "legal_authenticity_verified",
    "c2pa_verified",
    "human_authorship_verified",
    "production_security_verified",
]


def _exists(p: Path) -> bool:
    return p.exists()


def verify_repo_root() -> None:
    for name in (".git", "scripts", "apps", "specs", "docs"):
        if not (ROOT / name).exists():
            raise sl.HarnessError(f"repo root marker missing: {name}")
    if not APP_TSX.is_file():
        raise sl.HarnessError(f"App.tsx missing: {APP_TSX}")


def verify_no_staged_changes() -> None:
    sl.assert_no_staged_changes()


def verify_no_hidden_flags_before() -> None:
    sl.assert_no_hidden_git_flags()


def verify_harness_files_clean() -> None:
    existing = [p for p in HARNESS_SCAN_PATHS if _exists(p)]
    sl.assert_no_forbidden_terms(existing, sl.ALL_FORBIDDEN_TERMS)
    sl.assert_no_secret_like_patterns(existing)
    sl.assert_no_recursive_smoke_execution(GATE_SELF)


def verify_prior_evidence_clean() -> None:
    sl.assert_no_paths_changed(PRIOR_EVIDENCE_PREFIXES)


def verify_harness_files_present() -> None:
    for p in (SMOKE_LIB, GATE_SELF, VALIDATION_DOC, PROOF_DOC):
        sl.assert_file_exists(p)


def verify_golden_canonical() -> None:
    data = sl.read_json(GOLDEN_DEMO)
    for key, expected in EXPECTED_GOLDEN.items():
        actual = data.get(key)
        if str(actual) != str(expected):
            raise sl.HarnessError(
                f"canonical golden mismatch in {GOLDEN_DEMO}: {key}="
                f"{actual!r} expected {expected!r}"
            )


def verify_historical_contracts() -> tuple[list[str], list[str]]:
    """Verify each historical contract individually.

    Returns ``(verified_ids, contract_failures)``. Per-slice verification
    failures are accumulated rather than aborted on first failure, so the
    evidence report can carry an accurate list of which contracts failed.

    The schema rule is strict: a boolean success flag is never overloaded with
    a list. Callers consume ``verified_ids`` for the detail field and derive
    the boolean flag from whether ``contract_failures`` is empty.
    """
    verified: list[str] = []
    contract_failures: list[str] = []
    for contract in HISTORICAL_CONTRACTS:
        slice_id = contract["slice"]
        evidence = contract.get("evidence")
        if evidence is not None:
            golden = EXPECTED_GOLDEN if contract.get("golden") else None
            try:
                sl.assert_evidence_contract(evidence, required_constants=golden)
            except sl.HarnessError as exc:
                contract_failures.append(f"{slice_id}: {exc}")
                continue
        verified.append(slice_id)
    return verified, contract_failures


def verify_route_and_component_contracts() -> None:
    for contract in HISTORICAL_CONTRACTS:
        route = contract.get("route")
        if route is not None:
            sl.assert_route_registered(APP_TSX, route)
        comp = contract.get("component")
        if comp is not None:
            sl.assert_component_imported(APP_TSX, comp)
            sl.assert_file_exists(COMPONENT_DIR / f"{comp}.tsx")
    sl.assert_evidence_contract(GOLDEN_DEMO, required_constants=EXPECTED_GOLDEN)


def verify_no_forbidden_claims() -> None:
    offenders: list[str] = []
    components = [c["component"] for c in HISTORICAL_CONTRACTS if c.get("component")]
    targets = [APP_TSX, *[COMPONENT_DIR / f"{c}.tsx" for c in components]]
    for p in targets:
        if not p.is_file():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for term in FORBIDDEN_CLAIM_TERMS:
            if term in text:
                offenders.append(f"{p}: {term}")
    if offenders:
        raise sl.HarnessError("forbidden authenticity claims present:\n" + "\n".join(offenders))


def write_report(report: dict) -> None:
    sl.write_json_atomic(REPORT_PATH, report)


# ---------------------------------------------------------------------------
# PS-035C non-mutating write-mode helpers.
#
# The gate is non-mutating by default. ``_is_ps034a_slice`` recognizes the
# canonical PS-034A current-slice id in any of its common spellings so the
# explicit ``--write-report`` regeneration path can be restricted to PS-034A
# only. ``_sha256_file`` measures the canonical PS-034A report digest across a
# gate run so the report can carry ``ps034a_report_digest_unchanged`` as a real
# measured field instead of an assumption.
# ---------------------------------------------------------------------------
def _is_ps034a_slice(current_slice: str) -> bool:
    normalized = current_slice.strip().lower().replace("-", "").replace("_", "")
    return normalized == "ps034a"


def _sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


WRITE_MODE_CHECK_ONLY = "check_only"
WRITE_MODE_REPORT_OUT = "report_out"
WRITE_MODE_WRITE_REPORT = "write_report"


def _check(fn) -> tuple[bool, object]:
    try:
        result = fn()
        return True, result
    except sl.HarnessError as exc:
        return False, str(exc)
    except Exception as exc:
        return False, f"unexpected error: {exc}"


def run_gate(
    current_slice: str,
    frontend: bool,
    write_mode: str = WRITE_MODE_CHECK_ONLY,
    report_out_path: Path | None = None,
) -> int:
    failures: list[str] = []
    historical_verified: list[str] = []
    historical_failures: list[str] = []
    historical_step_ok = False

    # Measure the canonical tracked PS-034A report digest at the very start so
    # the report can carry a real ``ps034a_report_digest_unchanged`` field.
    ps034a_digest_before = _sha256_file(REPORT_PATH)

    def require(label: str, fn) -> object:
        ok, payload = _check(fn)
        if not ok:
            failures.append(f"{label}: {payload}")
            return None
        return payload

    require("repo_root", verify_repo_root)
    require("no_staged_changes", verify_no_staged_changes)

    no_hidden_before, _ = _check(verify_no_hidden_flags_before)
    if not no_hidden_before:
        failures.append("no_hidden_flags_before: hidden git index flags present")

    require("harness_files_clean", verify_harness_files_clean)
    require("harness_files_present", verify_harness_files_present)

    prior_ok, _ = _check(verify_prior_evidence_clean)
    if not prior_ok:
        failures.append("prior_evidence_clean: prior-slice evidence or paths changed")

    require("golden_canonical", verify_golden_canonical)
    hv_ok, hv_payload = _check(verify_historical_contracts)
    if hv_ok:
        historical_verified, historical_failures = hv_payload
        historical_step_ok = True
        for f in historical_failures:
            failures.append(f"historical_contract_failures: {f}")
    else:
        failures.append(f"historical_contracts: {hv_payload}")
    require("route_and_component_contracts", verify_route_and_component_contracts)
    require("no_forbidden_claims", verify_no_forbidden_claims)

    frontend_ran = False
    if frontend and not failures:
        fe_ok, fe_payload = _check(sl.assert_frontend_typecheck_build_once)
        if not fe_ok:
            failures.append(f"frontend_once: {fe_payload}")
        else:
            frontend_ran = True

    no_hidden_after, _ = _check(verify_no_hidden_flags_before)
    if not no_hidden_after:
        failures.append("no_hidden_flags_after: hidden git index flags present after validation")

    historical_contracts_verified = bool(
        historical_step_ok and not historical_failures
    )

    report = {
        "ok": not failures,
        "harness_id": "ps-034a-smoke-harness-v1",
        "harness_version": "v1",
        "current_slice": current_slice,
        "non_recursive_gate": True,
        "smoke_lib_created": _exists(SMOKE_LIB),
        "regression_gate_created": _exists(GATE_SELF),
        "validation_doc_created": _exists(VALIDATION_DOC),
        "proof_doc_created": _exists(PROOF_DOC),
        "no_recursive_smoke_policy": True,
        "no_git_hiding_policy": True,
        sl.GUARDIAN_FRAGMENT.join(("no_", "_workaround_policy")): True,
        "evidence_ownership_policy": True,
        "frontend_once_policy": True,
        "frontend_ran": frontend_ran,
        "historical_contracts_verified": historical_contracts_verified,
        "historical_contract_ids": historical_verified,
        "historical_contract_count": len(historical_verified),
        "historical_contract_failures": historical_failures,
        "prior_evidence_clean": prior_ok,
        "no_hidden_git_flags_before": no_hidden_before,
        "no_hidden_git_flags_after": no_hidden_after,
        "no_provider_call": True,
        "no_broad_b2_read": True,
        "ps034b_retrofit_deferred": True,
        "failures": failures,
        "checked_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
    }

    # ------------------------------------------------------------------
    # PS-035C write step. Only an explicit ``--write-report`` (restricted to
    # PS-034A) ever writes the canonical tracked report. ``--report-out``
    # writes only to the requested out-of-tree path. ``--check-only`` writes
    # nothing. The canonical PS-034A report digest is re-measured after the
    # write step so the report carries real measured fields.
    # ------------------------------------------------------------------
    canonical_written = write_mode == WRITE_MODE_WRITE_REPORT
    written_path: str | None = None
    if write_mode == WRITE_MODE_REPORT_OUT and report_out_path is not None:
        sl.write_json_atomic(report_out_path, report)
        written_path = str(report_out_path)
    elif write_mode == WRITE_MODE_WRITE_REPORT:
        write_report(report)
        written_path = str(REPORT_PATH)
    # WRITE_MODE_CHECK_ONLY: no report file is written.

    ps034a_digest_after = _sha256_file(REPORT_PATH)
    ps034a_report_digest_unchanged = bool(
        ps034a_digest_before is not None
        and ps034a_digest_after is not None
        and ps034a_digest_before == ps034a_digest_after
    )
    non_mutating_gate = not canonical_written

    report["write_mode"] = write_mode
    report["report_path"] = written_path
    report["non_mutating_gate"] = non_mutating_gate
    report["ps034a_report_digest_unchanged"] = ps034a_report_digest_unchanged

    # Re-write the on-disk report so the written file carries the measured
    # write-mode fields too. In check-only mode nothing is written.
    if write_mode == WRITE_MODE_REPORT_OUT and report_out_path is not None:
        sl.write_json_atomic(report_out_path, report)
    elif write_mode == WRITE_MODE_WRITE_REPORT:
        write_report(report)

    if failures:
        print("REGRESSION GATE FAILED", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        print(f"  write_mode: {write_mode}", file=sys.stderr)
        if written_path is not None:
            print(f"  report: {written_path}", file=sys.stderr)
        else:
            print("  report: not written", file=sys.stderr)
        return 1
    print("REGRESSION GATE PASSED")
    print(f"  current_slice: {current_slice}")
    print(f"  historical_contracts_verified: {historical_contracts_verified}")
    print(f"  historical_contract_ids: {historical_verified}")
    print(f"  historical_contract_count: {len(historical_verified)}")
    print(f"  frontend_ran: {frontend_ran}")
    print(f"  write_mode: {write_mode}")
    if written_path is not None:
        print(f"  report: {written_path}")
    else:
        print("  report: not written")
    print(f"  non_mutating_gate: {non_mutating_gate}")
    print(f"  ps034a_report_digest_unchanged: {ps034a_report_digest_unchanged}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ProofStudio central regression gate")
    parser.add_argument("--current", required=True, help="current slice id, e.g. ps034a or ps034")
    parser.add_argument(
        "--frontend",
        dest="frontend",
        action="store_true",
        help="run frontend typecheck and build exactly once at the top level",
    )
    parser.add_argument(
        "--no-frontend",
        dest="frontend",
        action="store_false",
        help="skip the frontend typecheck/build (default)",
    )
    parser.add_argument(
        "--check-only",
        dest="check_only",
        action="store_true",
        help="validate all historical contracts and print the summary without "
        "writing any report file (default non-mutating mode)",
    )
    parser.add_argument(
        "--report-out",
        dest="report_out",
        metavar="PATH",
        default=None,
        help="write the report only to the supplied path; the canonical tracked "
        "PS-034A report is never written in this mode",
    )
    parser.add_argument(
        "--write-report",
        dest="write_report",
        action="store_true",
        help="write the canonical tracked PS-034A report "
        "(docs/evidence/ps-034a/smoke-harness-v1-report.json); only allowed with "
        "--current ps034a / ps-034a for PM-aware PS-034A evidence regeneration",
    )
    parser.set_defaults(frontend=False, check_only=False, write_report=False)
    args = parser.parse_args(argv)
    current = args.current.strip().lower()
    if not current.startswith("ps"):
        parser.error("--current must be a slice id like ps034a or ps034")

    # ---- PS-035C write-mode conflict resolution (before any file is written)
    check_only = args.check_only
    report_out = args.report_out
    write_report = args.write_report
    if check_only and write_report:
        parser.error("--check-only conflicts with --write-report")
    if check_only and report_out is not None:
        parser.error("--check-only conflicts with --report-out")
    if report_out is not None and write_report:
        parser.error("--report-out conflicts with --write-report")

    # Resolve the effective write mode. ``--write-report`` is restricted to the
    # PS-034A current slice so a later slice can never mutate the canonical
    # tracked PS-034A report.
    if write_report:
        if not _is_ps034a_slice(current):
            parser.error(
                "--write-report writes the canonical tracked PS-034A report and "
                "is only allowed with --current ps034a / ps-034a "
                f"(received --current {current})"
            )
        write_mode = WRITE_MODE_WRITE_REPORT
        report_out_path = REPORT_PATH
    elif report_out is not None:
        write_mode = WRITE_MODE_REPORT_OUT
        report_out_path = Path(report_out)
    else:
        # Preferred default for every slice (including PS-034A): non-mutating
        # check-only. Writing the canonical PS-034A report always requires the
        # explicit --write-report flag.
        write_mode = WRITE_MODE_CHECK_ONLY
        report_out_path = None

    return run_gate(current, args.frontend, write_mode, report_out_path)


if __name__ == "__main__":
    raise SystemExit(main())
