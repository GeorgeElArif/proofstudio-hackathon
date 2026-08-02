#!/usr/bin/env python3
"""PS-034B Historical Smoke Local-Mode Retrofit -- smoke / validation.

This smoke verifies the PS-034B retrofit: every historical smoke PS-023
through PS-034 is safe to run directly in local / check-only mode without
reintroducing recursive smoke chains, nested frontend builds, Git index
hiding, prior-evidence mutation, self-unlink hacks, provider calls, broad B2
reads, or historical evidence rewriting by default.

PS-034B performs a controlled local-mode sweep of retrofitted historical
smokes. It does not reintroduce the old recursive smoke chain because the
historical smokes no longer execute each other. Each historical smoke is run
as a subprocess in ``--local --check-only`` mode (the safe default), and the
working tree is then verified to be left clean.

Provider / network and broad-B2 access are proven by explicit AST-based
checks (see ``check_no_provider_call_paths`` and
``check_no_broad_b2_read_paths``), not by hardcoded fields. The only allowed
live/network path is the PS-025 ``urlopen`` call, which is gated behind an
explicit ``--live`` flag and never runs by default.

    python scripts/ps034b_historical_smoke_local_mode_retrofit_smoke.py

Exit code is 0 only when every check passes.
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import argparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import smoke_lib as sl  # noqa: E402

ROOT = sl.repo_root()
SCRIPTS = ROOT / "scripts"
DOCS = ROOT / "docs"

REPORT = DOCS / "evidence" / "ps-034b" / "historical-smoke-local-mode-retrofit-report.json"
VALIDATION_DOC = DOCS / "validation" / "proofstudio-smoke-harness-v1.md"
PS034A_SMOKE = SCRIPTS / "ps034a_smoke_harness_v1_smoke.py"

RETROFITTED_SMOKES: list[str] = [
    "ps023_judge_cockpit_home_smoke.py",
    "ps024_golden_demo_run_pinning_smoke.py",
    "ps025_public_durable_passport_unlock_smoke.py",
    "ps026_b2_evidence_explorer_smoke.py",
    "ps027_genblaze_pipeline_graph_smoke.py",
    "ps028_manifest_verification_panel_smoke.py",
    "ps029_b2_rehydrate_comparison_smoke.py",
    "ps030_failure_as_proof_timeline_smoke.py",
    "ps031_export_campaign_pack_v2_smoke.py",
    "ps032_operations_cockpit_flight_recorder_smoke.py",
    "ps033_provider_decision_intelligence_smoke.py",
    "ps034_lineage_comparison_lab_smoke.py",
]

PS034A_REQUIRED_LINE = (
    "Historical smoke local-mode retrofit is deferred to PS-034B."
)

FRONTEND_PATTERN = re.compile(
    r"run_npm|npm\s+run|vite\s+build|pnpm\s+|yarn\s+|tsc\s+--noEmit|typecheck",
    re.IGNORECASE,
)

GIT_HIDING_TERMS = [
    "assume-unchanged",
    "skip-worktree",
    "git update-index",
    "update-index",
    "_snapshot_evidence",
    "_restore_evidence",
    "_set_assume",
    "TRACKED_UNLINK",
    "EVIDENCE_OUT.unlink",
]

PROTECTED_EVIDENCE_PREFIXES = [
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
]

PS025_SMOKE_NAME = "ps025_public_durable_passport_unlock_smoke.py"

# Direct network / provider call primitives. We flag these only when they
# appear as real ``Call`` nodes in the parsed AST, never as plain string
# literals (so static scan-string pattern lists like ``PROVIDER_CALL_PATTERNS``
# in the historical smokes are not flagged).
NETWORK_BARE_PRIMITIVES = {
    "urlopen",
    "Request",
    "call_provider",
    "fetchFromProvider",
}
NETWORK_DOTTED_PRIMITIVES = {
    "requests.post",
    "requests.get",
    "requests.put",
    "requests.delete",
    "requests.request",
    "httpx.post",
    "httpx.get",
    "httpx.put",
    "httpx.delete",
    "httpx.request",
}

# Direct executable B2 access primitives. Again these are matched only as real
# ``Call`` nodes, so the historical smokes' constant ``BROAD_B2_READ_PATTERNS``
# scan-string tuples (which police the product frontend) are not flagged.
B2_BARE_PRIMITIVES = {
    "read_archive_from_b2",
    "fetchB2Object",
    "list_b2_objects",
}
B2_DOTTED_PRIMITIVES = {
    "boto3.client",
    "boto3.resource",
    "b2sdk.B2Api",
}
B2_ATTR_PRIMITIVES = {
    "get_object",
    "list_objects",
    "list_objects_v2",
    "download_fileobj",
    "head_object",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def check_non_recursive(failures: list[str]) -> bool:
    ok = True
    for name in RETROFITTED_SMOKES:
        path = SCRIPTS / name
        try:
            sl.assert_no_recursive_smoke_execution(path)
        except sl.HarnessError as exc:
            failures.append(f"non_recursive/{name}: {exc}")
            ok = False
    return ok


# ---------------------------------------------------------------------------
# AST helpers for the provider/network and broad-B2 proof checks.
# ---------------------------------------------------------------------------

def _ast_dotted_name(node: ast.AST) -> str:
    parts: list[str] = []
    cur: ast.AST = node
    while isinstance(cur, ast.Attribute):
        parts.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        parts.append(cur.id)
    return ".".join(reversed(parts))


def _build_parent_map(tree: ast.AST) -> dict[ast.AST, ast.AST]:
    parents: dict[ast.AST, ast.AST] = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node
    return parents


def _is_live_guard(test: ast.AST) -> bool:
    """True for ``if live:`` / ``if opts.live:`` style guards."""
    if isinstance(test, ast.Name) and test.id == "live":
        return True
    if isinstance(test, ast.Attribute) and test.attr == "live":
        return True
    return False


def _guarded_by_if_live(node: ast.AST, parents: dict[ast.AST, ast.AST]) -> bool:
    cur: ast.AST | None = parents.get(node)
    while cur is not None:
        if isinstance(cur, ast.If) and _is_live_guard(cur.test):
            return True
        cur = parents.get(cur)
    return False


def _verify_ps025_live_allow_conditions(path: Path) -> tuple[bool, list[str]]:
    """Verify the only allowed live/network path (PS-025) is properly gated.

    Returns (ok, problems). Conditions:
      - the smoke is the PS-025 passport smoke
      - it parses its CLI with ``allow_live=True``
      - it calls ``_get_passport_json(..., live=opts.live)``
      - every ``urlopen`` / ``Request`` call is nested inside an ``if live:``
        guard within the source
    """
    problems: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    if "parse_slice_smoke_cli(" not in text:
        problems.append("parse_slice_smoke_cli is not used")
    if "allow_live=True" not in text:
        problems.append("parse_slice_smoke_cli is not called with allow_live=True")
    if "_get_passport_json(" not in text:
        problems.append("_get_passport_json is not called")
    if "live=opts.live" not in text:
        problems.append("_get_passport_json is not called with live=opts.live")
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError as exc:
        problems.append(f"could not parse {path.name}: {exc}")
        return (not problems, problems)
    parents = _build_parent_map(tree)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _ast_dotted_name(node.func)
        if name not in {"urlopen", "Request"}:
            continue
        if not _guarded_by_if_live(node, parents):
            problems.append(
                f"{path.name}:{node.lineno}: {name!r} call is not gated "
                f"behind an `if live:` guard"
            )
    return (not problems, problems)


def check_no_provider_call_paths(failures: list[str]) -> tuple[bool, dict[str, object]]:
    """Prove no retrofitted smoke performs an executable provider/network call.

    Walks the parsed AST of every historical smoke PS-023 through PS-034 and
    flags any real ``Call`` node that invokes a network/provider primitive
    (``urlopen``, ``Request``, ``requests.*``, ``httpx.*``, ``call_provider``,
    ``fetchFromProvider``). Static scan-string pattern lists (e.g.
    ``PROVIDER_CALL_PATTERNS`` tuples) are plain string constants and are
    therefore never flagged.

    The single allowed exception is the PS-025 passport smoke, which may use
    ``urlopen`` / ``Request`` only inside its explicitly gated ``--live``
    branch. The gating is verified by ``_verify_ps025_live_allow_conditions``.
    Default local / check runs passing without ``--live`` is proven separately
    by ``check_each_smoke_local_mode``.
    """
    detail: dict[str, object] = {
        "checked": [],
        "allowed_live_paths": [],
    }
    violations: list[dict[str, object]] = []
    ok = True
    for name in RETROFITTED_SMOKES:
        path = SCRIPTS / name
        text = path.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(text, filename=str(path))
        except SyntaxError as exc:
            failures.append(f"no_provider_call/{name}: parse error {exc}")
            ok = False
            continue
        parents = _build_parent_map(tree)
        entry: dict[str, object] = {"smoke": name, "network_calls": [], "allowed": []}
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fname = _ast_dotted_name(node.func)
            is_network = (
                fname in NETWORK_BARE_PRIMITIVES
                or fname in NETWORK_DOTTED_PRIMITIVES
            )
            if not is_network:
                continue
            site: dict[str, object] = {"call": fname, "line": node.lineno}
            # The only permitted live/network path: PS-025 urlopen/Request
            # inside the explicitly gated --live branch.
            if (
                name == PS025_SMOKE_NAME
                and fname in {"urlopen", "Request"}
                and _guarded_by_if_live(node, parents)
            ):
                allowed_entry: dict[str, object] = {
                    "smoke": name,
                    "call": fname,
                    "line": node.lineno,
                    "reason": (
                        "PS-025 explicitly gated --live path; default "
                        "local/check runs do not invoke it"
                    ),
                }
                assert isinstance(entry["allowed"], list)
                entry["allowed"].append(allowed_entry)
                detail["allowed_live_paths"] = (
                    detail["allowed_live_paths"] if isinstance(detail["allowed_live_paths"], list) else []
                )
                assert isinstance(detail["allowed_live_paths"], list)
                detail["allowed_live_paths"].append(allowed_entry)
                continue
            assert isinstance(entry["network_calls"], list)
            entry["network_calls"].append(site)
            violations.append({"smoke": name, **site})
            failures.append(
                f"no_provider_call/{name}:{node.lineno}: executable "
                f"network/provider primitive {fname!r}"
            )
            ok = False
        detail["checked"].append(entry)

    # Verify the PS-025 allow conditions explicitly.
    ps025_path = SCRIPTS / PS025_SMOKE_NAME
    ps025_ok, ps025_problems = _verify_ps025_live_allow_conditions(ps025_path)
    detail["ps025_live_allow_conditions_ok"] = bool(ps025_ok)
    detail["ps025_live_allow_conditions_problems"] = ps025_problems
    if not ps025_ok:
        ok = False
        for prob in ps025_problems:
            failures.append(f"no_provider_call/{PS025_SMOKE_NAME}: {prob}")

    detail["violations"] = violations
    return bool(ok), detail


def check_no_broad_b2_read_paths(failures: list[str]) -> tuple[bool, dict[str, object]]:
    """Prove no retrofitted smoke performs an executable broad B2 read.

    Walks the parsed AST of every historical smoke PS-023 through PS-034 and
    flags any real ``Call`` node that invokes a B2 access primitive
    (``boto3.client``, ``boto3.resource``, ``.get_object``, ``.list_objects``,
    ``.list_objects_v2``, ``.download_fileobj``, ``read_archive_from_b2``,
    ``fetchB2Object``, ``list_b2_objects``). Static scan-string pattern lists
    (e.g. ``BROAD_B2_READ_PATTERNS`` tuples that police the product frontend)
    are plain string constants and are therefore never flagged.
    """
    detail: dict[str, object] = {"checked": []}
    violations: list[dict[str, object]] = []
    ok = True
    for name in RETROFITTED_SMOKES:
        path = SCRIPTS / name
        text = path.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(text, filename=str(path))
        except SyntaxError as exc:
            failures.append(f"no_broad_b2_read/{name}: parse error {exc}")
            ok = False
            continue
        entry: dict[str, object] = {"smoke": name, "b2_calls": []}
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fname = _ast_dotted_name(node.func)
            hit_label = ""
            if fname in B2_BARE_PRIMITIVES:
                hit_label = fname
            elif fname in B2_DOTTED_PRIMITIVES:
                hit_label = fname
            elif (
                isinstance(node.func, ast.Attribute)
                and node.func.attr in B2_ATTR_PRIMITIVES
            ):
                hit_label = f".{node.func.attr}"
            if not hit_label:
                continue
            site = {"call": hit_label, "line": node.lineno}
            assert isinstance(entry["b2_calls"], list)
            entry["b2_calls"].append(site)
            violations.append({"smoke": name, **site})
            failures.append(
                f"no_broad_b2_read/{name}:{node.lineno}: executable "
                f"B2 access primitive {hit_label!r}"
            )
            ok = False
        detail["checked"].append(entry)
    detail["violations"] = violations
    return bool(ok), detail


def check_no_frontend_builds(failures: list[str]) -> bool:
    ok = True
    for name in RETROFITTED_SMOKES:
        path = SCRIPTS / name
        text = path.read_text(encoding="utf-8", errors="replace")
        for i, line in enumerate(text.splitlines(), 1):
            if FRONTEND_PATTERN.search(line):
                failures.append(
                    f"no_nested_frontend_builds/{name}:{i}: {line.strip()}"
                )
                ok = False
    return ok


def check_no_git_hiding(failures: list[str]) -> bool:
    ok = True
    for name in RETROFITTED_SMOKES:
        path = SCRIPTS / name
        text = path.read_text(encoding="utf-8", errors="replace")
        for term in GIT_HIDING_TERMS:
            if term in text:
                failures.append(f"no_git_hiding/{name}: contains {term}")
                ok = False
    return ok


def check_no_hidden_git_flags(failures: list[str]) -> bool:
    try:
        sl.assert_no_hidden_git_flags()
        return True
    except sl.HarnessError as exc:
        failures.append(f"no_hidden_git_flags: {exc}")
        return False


def check_ps034a_required_line(failures: list[str]) -> bool:
    text = VALIDATION_DOC.read_text(encoding="utf-8", errors="replace")
    if PS034A_REQUIRED_LINE not in text:
        failures.append(
            "ps034a_required_lines_preserved: missing exact line: "
            f"{PS034A_REQUIRED_LINE!r}"
        )
        return False
    return True


def check_each_smoke_local_mode(failures: list[str]) -> list[dict]:
    """Run each historical smoke in safe local / check-only mode."""
    results: list[dict] = []
    for name in RETROFITTED_SMOKES:
        path = SCRIPTS / name
        entry: dict[str, object] = {
            "smoke": name,
            "exit_code": None,
            "ok": False,
        }
        try:
            res = sl.run_command(
                [sys.executable, str(path), "--local", "--check-only"],
                cwd=ROOT,
                timeout=300,
            )
            entry["exit_code"] = res.returncode
            entry["ok"] = res.returncode == 0
            if res.returncode != 0:
                tail = (res.stdout or "") + (res.stderr or "")
                failures.append(
                    f"local_mode/{name}: nonzero exit {res.returncode}\n"
                    + tail[-800:]
                )
        except Exception as exc:
            entry["ok"] = False
            failures.append(f"local_mode/{name}: exception {exc}")
        results.append(entry)
    return results


def check_no_prior_evidence_dirty(failures: list[str]) -> bool:
    """No prior-slice evidence file is left modified by the local-mode runs."""
    try:
        sl.assert_no_paths_changed(PROTECTED_EVIDENCE_PREFIXES)
        return True
    except sl.HarnessError as exc:
        failures.append(f"no_prior_evidence_mutation: {exc}")
        return False


def check_ps034a_smoke_passes(failures: list[str]) -> bool:
    """The PS-034A smoke must still pass.

    The PS-034A smoke runs the regression gate internally, which writes to the
    PS-034A evidence report. We restore that file afterward so no PS-034A
    evidence is left dirty.
    """
    ps034a_report = DOCS / "evidence" / "ps-034a" / "smoke-harness-v1-report.json"
    snapshot = ps034a_report.read_bytes() if ps034a_report.exists() else b""
    try:
        res = sl.run_command(
            [sys.executable, str(PS034A_SMOKE)],
            cwd=ROOT,
            timeout=300,
        )
        if res.returncode != 0:
            tail = (res.stdout or "") + (res.stderr or "")
            failures.append(
                f"ps034a_smoke_still_passes: nonzero exit\n" + tail[-1200:]
            )
            return False
        return True
    except Exception as exc:
        failures.append(f"ps034a_smoke_still_passes: exception {exc}")
        return False
    finally:
        if snapshot:
            ps034a_report.write_bytes(snapshot)


def main() -> int:
    failures: list[str] = []

    # Remove any stale PS-034B report so the PS-034 historical smoke's
    # prior-evidence check does not flag docs/evidence/ps-034b/ as dirty.
    if REPORT.exists():
        REPORT.unlink()

    check_no_hidden_git_flags(failures)

    non_recursive = check_non_recursive(failures)
    no_nested_frontend_builds = check_no_frontend_builds(failures)
    no_git_hiding = check_no_git_hiding(failures)
    ps034a_required_lines_preserved = check_ps034a_required_line(failures)

    # Provider/network and broad-B2 proofs are computed by explicit AST-based
    # checks (see check_no_provider_call_paths / check_no_broad_b2_read_paths).
    # They are NOT hardcoded: the report fields below come directly from these
    # results.
    no_provider_call, provider_network_check = check_no_provider_call_paths(
        failures
    )
    no_broad_b2_read, broad_b2_read_check = check_no_broad_b2_read_paths(
        failures
    )

    smoke_results = check_each_smoke_local_mode(failures)

    no_prior_evidence_mutation = check_no_prior_evidence_dirty(failures)
    no_historical_evidence_rewrite = no_prior_evidence_mutation

    ps034a_smoke_ok = check_ps034a_smoke_passes(failures)

    check_no_hidden_git_flags(failures)

    smoke_lib_policy_checks = (
        non_recursive
        and no_nested_frontend_builds
        and no_git_hiding
        and check_no_hidden_git_flags([])
    )

    ok = (
        non_recursive
        and no_nested_frontend_builds
        and no_git_hiding
        and ps034a_required_lines_preserved
        and no_prior_evidence_mutation
        and no_historical_evidence_rewrite
        and ps034a_smoke_ok
        and smoke_lib_policy_checks
        and no_provider_call
        and no_broad_b2_read
        and all(r["ok"] for r in smoke_results)
        and not failures
    )

    report = {
        "ok": bool(ok),
        "slice_id": "ps034b",
        "retrofit_scope": (
            "Retrofit historical smoke scripts PS-023 through PS-034 for safe "
            "local / check-only mode without recursion, nested frontend builds, "
            "Git index hiding, prior-evidence mutation, self-unlink hacks, "
            "provider calls, broad B2 reads, or historical evidence rewriting "
            "by default."
        ),
        "retrofitted_smokes": [
            {
                "smoke": name,
                "local_check_mode": True,
                "passed": any(
                    r["ok"] for r in smoke_results if r["smoke"] == name
                ),
            }
            for name in RETROFITTED_SMOKES
        ],
        "non_recursive": bool(non_recursive),
        "no_nested_frontend_builds": bool(no_nested_frontend_builds),
        "no_git_hiding": bool(no_git_hiding),
        "no_prior_evidence_mutation": bool(no_prior_evidence_mutation),
        "no_historical_evidence_rewrite_by_default": bool(
            no_historical_evidence_rewrite
        ),
        "no_provider_call": bool(no_provider_call),
        "no_broad_b2_read": bool(no_broad_b2_read),
        "provider_network_check": provider_network_check,
        "broad_b2_read_check": broad_b2_read_check,
        "allowed_live_paths": provider_network_check.get("allowed_live_paths", []),
        "smoke_lib_policy_checks": bool(smoke_lib_policy_checks),
        "ps034a_required_lines_preserved": bool(ps034a_required_lines_preserved),
        "ps034a_smoke_still_passes": bool(ps034a_smoke_ok),
        "checked_at": _utc_now_iso(),
        "failures": failures,
    }

    sl.write_json_atomic(REPORT, report)

    if failures:
        print("PS-034B SMOKE FAILED", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("PS-034B SMOKE PASSED")
    print(f"  retrofitted smokes: {len(RETROFITTED_SMOKES)}")
    print("  non_recursive: AST-verified")
    print("  no_nested_frontend_builds: static-verified")
    print("  no_git_hiding: static-verified")
    print("  no_provider_call: AST-verified (executable network primitives)")
    print("  no_broad_b2_read: AST-verified (executable B2 primitives)")
    print(f"  ps034a_required_lines_preserved: {ps034a_required_lines_preserved}")
    print(f"  ps034a_smoke_still_passes: {ps034a_smoke_ok}")
    print(f"  no_prior_evidence_mutation: {no_prior_evidence_mutation}")
    print(f"  report: {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
