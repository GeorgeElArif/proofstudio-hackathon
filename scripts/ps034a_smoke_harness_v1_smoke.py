#!/usr/bin/env python3
"""PS-034A — Smoke Harness v1 slice smoke.

This smoke validates the PS-034A validation-infrastructure slice itself. It is
non-recursive: it never executes another feature smoke. It is allowed to invoke
the central regression gate, because the gate is the single cross-slice
coordinator and is not a feature smoke. The frontend typecheck/build is NOT
executed here; the build-once policy is verified as a capability and exercised
at the top-level validation step instead.

Recursive execution is detected structurally via AST parsing, not with brittle
text grep. The regression gate uses contract tables, not smoke script paths.

    python scripts/ps034a_smoke_harness_v1_smoke.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import smoke_lib as sl  # noqa: E402

ROOT = sl.repo_root()
SCRIPTS = ROOT / "scripts"
DOCS = ROOT / "docs"

SMOKE_LIB = SCRIPTS / "smoke_lib.py"
GATE = SCRIPTS / "proofstudio_regression_gate.py"
SELF = SCRIPTS / "ps034a_smoke_harness_v1_smoke.py"
VALIDATION_DOC = DOCS / "validation" / "proofstudio-smoke-harness-v1.md"
PROOF_DOC = DOCS / "ps-034a-smoke-harness-v1-proof.md"
REPORT = DOCS / "evidence" / "ps-034a" / "smoke-harness-v1-report.json"

REQUIRED_EXACT_LINES = [
    "Feature slice smokes validate the slice. The regression gate validates the release.",
    "No feature smoke may recursively execute another feature smoke.",
    "No smoke may hide evidence changes with Git index flags.",
    "A slice smoke may write only its own evidence file.",
    "Frontend typecheck and build run once at the top-level gate.",
    "Historical smoke local-mode retrofit is deferred to PS-034B.",
]

PROTECTED_PREFIXES = [
    "apps/",
    "src/",
    "workers/",
    "packages/",
    "render.yaml",
    ".env",
    "docs/evidence/ps-019/",
    "docs/evidence/ps-020/",
    "docs/evidence/ps-021/",
    "docs/evidence/ps-024/",
    "docs/evidence/ps-025/",
    "docs/evidence/ps-026/",
    "docs/evidence/ps-027/",
    "docs/evidence/ps-028/",
    "docs/evidence/ps-029/",
    "docs/evidence/ps-030/",
    "docs/evidence/ps-031/",
    "docs/evidence/ps-032/",
    "docs/evidence/ps-033/",
    "docs/evidence/ps-034/",
    "docs/evidence/demo/",
]


EXPECTED_HISTORICAL_IDS = {
    "ps021", "ps023", "ps025", "ps026", "ps027", "ps028",
    "ps029", "ps030", "ps031", "ps032", "ps033", "ps034",
}


def check_files_exist(failures: list[str]) -> None:
    for label, p in [
        ("smoke_lib", SMOKE_LIB),
        ("regression_gate", GATE),
        ("validation_doc", VALIDATION_DOC),
        ("proof_doc", PROOF_DOC),
        ("evidence_report", REPORT),
    ]:
        if not p.is_file():
            failures.append(f"files_exist: missing {label} at {p}")


def check_gate_non_recursive(failures: list[str]) -> None:
    try:
        sl.assert_no_recursive_smoke_execution(GATE)
    except sl.HarnessError as exc:
        failures.append(f"non_recursive: {exc}")


def check_no_banned_terms(failures: list[str]) -> None:
    targets = [SMOKE_LIB, GATE, SELF, VALIDATION_DOC, PROOF_DOC]
    existing = [p for p in targets if p.is_file()]
    try:
        sl.assert_no_forbidden_terms(existing, sl.ALL_FORBIDDEN_TERMS)
    except sl.HarnessError as exc:
        failures.append(str(exc))


def check_validation_doc_lines(failures: list[str]) -> None:
    if not VALIDATION_DOC.is_file():
        failures.append("validation_doc_lines: doc missing")
        return
    text = VALIDATION_DOC.read_text(encoding="utf-8", errors="replace")
    for line in REQUIRED_EXACT_LINES:
        if line not in text:
            failures.append(f"validation_doc_lines: missing exact line: {line}")


def check_proof_doc_plan(failures: list[str]) -> None:
    if not PROOF_DOC.is_file():
        failures.append("proof_doc_plan: doc missing")
        return
    text = PROOF_DOC.read_text(encoding="utf-8", errors="replace")
    if "PS-034B" not in text:
        failures.append("proof_doc_plan: PS-034B retrofit plan not documented")
    if "retrofit" not in text.lower():
        failures.append("proof_doc_plan: retrofit plan wording absent")


def check_frontend_once_capability(failures: list[str]) -> None:
    gate = GATE.read_text(encoding="utf-8", errors="replace")
    lib = SMOKE_LIB.read_text(encoding="utf-8", errors="replace")
    if "assert_frontend_typecheck_build_once" not in gate:
        failures.append("frontend_once: gate does not wire the build-once helper")
    if gate.count("assert_frontend_typecheck_build_once") != 1:
        failures.append("frontend_once: gate must reference the helper exactly once")
    if "--frontend" not in gate:
        failures.append("frontend_once: gate does not expose --frontend")
    if "_FRONTEND_INVOCATIONS" not in lib:
        failures.append("frontend_once: library lacks the once-invocation guard")


def check_evidence_ok(failures: list[str]) -> None:
    if not REPORT.is_file():
        failures.append("evidence_ok: report missing")
        return
    try:
        data = sl.read_json(REPORT)
    except sl.HarnessError as exc:
        failures.append(f"evidence_ok: {exc}")
        return
    if data.get("ok") is not True:
        failures.append("evidence_ok: report ok is not true")
    for key in ("non_recursive_gate", "no_git_hiding_policy",
                sl.GUARDIAN_FRAGMENT.join(("no_", "_workaround_policy")),
                "evidence_ownership_policy", "frontend_once_policy",
                "ps034b_retrofit_deferred"):
        if data.get(key) is not True:
            failures.append(f"evidence_ok: policy flag not true: {key}")

    # Strict evidence report schema: boolean success flag must stay a boolean,
    # and the verified slice ids must live in a dedicated detail field.
    verified = data.get("historical_contracts_verified")
    if verified is not True:
        failures.append(
            "evidence_ok: historical_contracts_verified must be boolean true"
        )
    if not isinstance(verified, bool):
        failures.append(
            "evidence_ok: historical_contracts_verified must not carry a list"
        )

    ids = data.get("historical_contract_ids")
    if not isinstance(ids, list) or not ids:
        failures.append(
            "evidence_ok: historical_contract_ids must be a non-empty list"
        )
    else:
        missing = sorted(EXPECTED_HISTORICAL_IDS - set(ids))
        extra = sorted(set(ids) - EXPECTED_HISTORICAL_IDS)
        if missing:
            failures.append(
                f"evidence_ok: historical_contract_ids missing {missing}"
            )
        if extra:
            failures.append(
                f"evidence_ok: historical_contract_ids unexpected {extra}"
            )

    count = data.get("historical_contract_count")
    if not isinstance(count, int) or isinstance(count, bool):
        failures.append(
            "evidence_ok: historical_contract_count must be an integer"
        )
    elif isinstance(ids, list) and count != len(ids):
        failures.append(
            "evidence_ok: historical_contract_count must equal "
            "len(historical_contract_ids)"
        )

    contract_failures = data.get("historical_contract_failures")
    if not isinstance(contract_failures, list):
        failures.append(
            "evidence_ok: historical_contract_failures must be a list"
        )
    elif contract_failures and verified is True:
        failures.append(
            "evidence_ok: historical_contract_failures must be empty when "
            "historical_contracts_verified is true"
        )


def run_gate_no_frontend(failures: list[str]) -> None:
    # PS-035C: the central gate is non-mutating by default. This smoke owns the
    # canonical PS-034A evidence regeneration, so it must pass --write-report
    # explicitly to keep regenerating the canonical tracked PS-034A report.
    res = sl.run_command(
        [sys.executable, str(GATE), "--current", "ps034a", "--no-frontend",
         "--write-report"],
        cwd=ROOT,
        timeout=300,
    )
    if res.returncode != 0:
        failures.append(
            "run_gate_no_frontend: nonzero exit\n"
            f"stdout:\n{res.stdout}\nstderr:\n{res.stderr}"
        )


def check_protected_paths_clean(failures: list[str]) -> None:
    try:
        sl.assert_no_paths_changed(PROTECTED_PREFIXES)
    except sl.HarnessError as exc:
        failures.append(f"protected_paths_clean: {exc}")


def main() -> int:
    failures: list[str] = []

    try:
        sl.assert_no_hidden_git_flags()
    except sl.HarnessError as exc:
        failures.append(f"hidden_flags_before: {exc}")

    check_files_exist(failures)
    check_gate_non_recursive(failures)
    check_no_banned_terms(failures)
    check_validation_doc_lines(failures)
    check_proof_doc_plan(failures)
    check_frontend_once_capability(failures)
    run_gate_no_frontend(failures)
    check_evidence_ok(failures)
    check_protected_paths_clean(failures)

    try:
        sl.assert_no_hidden_git_flags()
    except sl.HarnessError as exc:
        failures.append(f"hidden_flags_after: {exc}")

    if failures:
        print("PS-034A SMOKE FAILED", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("PS-034A SMOKE PASSED")
    print("  smoke_lib: present")
    print("  regression_gate: non-recursive (AST-based detection)")
    print("  no banned recursive / git-hiding / polling-watcher terms")
    print("  validation_doc: required exact lines present")
    print("  proof_doc: PS-034B retrofit plan present")
    print("  evidence_report: ok (strict schema: bool flag + ids list)")
    print("  protected paths (apps/src/workers/render/env/prior-evidence): clean")
    print("  hidden git flags: absent before and after")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
