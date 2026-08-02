#!/usr/bin/env python3
"""Strictly offline, non-mutating PS-042C6 repository-state smoke."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "ps042c6_gmi_submit_reconciliation.py"
SELF = Path(__file__).resolve()
TESTS = ROOT / "tests" / "test_ps042c6_gmi_submit_reconciliation.py"
ATTEMPT_LOCK = Path(
    "/home/george/.local/state/proofstudio/ps042c5-one-live-attempt.lock"
)
FAILURE_RECEIPT = Path(
    "/tmp/proofstudio-ps042c5-execution/"
    "d1b4e4640bb1d79ee158bf01617e0e17/failure-receipt.json"
)
EXPECTED_ATTEMPT_LOCK_SHA256 = (
    "6a8901647faf1c6a2cba1d2bd4698ee4b2e82738ea39a60d543a20a07e25bba8"
)
EXPECTED_FAILURE_RECEIPT_SHA256 = (
    "3be63e463727cf4f023b084d28a361e4600f3e2bff4af2b5ece29b07a74b10da"
)
BASE_REVISION = "ca3b2d1e0ba4cea3978b2ffe33ab25dff8acedb8"
REQUIRED_START_REVISION = "578c268b38c397c440598e3d6a05f5e467d10a1d"
REQUIRED_BRANCH = "ps-042c0/free-render-staging-v1"
REQUIRED_REMOTE_REF = f"origin/{REQUIRED_BRANCH}"
EXPECTED_CHANGED_PATHS = frozenset(
    {
        "scripts/ps042c5_one_real_genblaze_proof.py",
        "scripts/ps042c6_gmi_submit_reconciliation.py",
        "scripts/ps042c6_gmi_submit_reconciliation_smoke.py",
        "tests/test_ps042c6_gmi_submit_reconciliation.py",
    }
)
PACKAGE_AND_LOCK_NAMES = frozenset(
    {
        "package.json",
        "package-lock.json",
        "pnpm-lock.yaml",
        "yarn.lock",
        "requirements.txt",
        "poetry.lock",
        "uv.lock",
    }
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def git(*args: str) -> str:
    return subprocess.run(
        ("git", *args),
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout.rstrip()


def git_succeeds(*args: str) -> bool:
    return (
        subprocess.run(
            ("git", *args),
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode
        == 0
    )


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def changed_paths_from_porcelain(porcelain: str) -> frozenset[str]:
    paths: set[str] = set()
    for line in porcelain.splitlines():
        require(len(line) >= 4, "unparseable Git status")
        value = line[3:]
        if " -> " in value:
            value = value.split(" -> ", 1)[1]
        paths.add(value)
    return frozenset(paths)


def evaluate_repository_scope(
    *,
    branch: str,
    head: str,
    origin_head: str,
    start_revision_is_ancestor: bool,
    working_tree_changed_paths: frozenset[str],
    cumulative_source_paths: frozenset[str],
) -> dict[str, Any]:
    repository_state = (
        "postcommit" if not working_tree_changed_paths else "precommit"
    )
    head_matches_origin = head == origin_head
    authorized_combined_source_paths = (
        cumulative_source_paths
        if repository_state == "postcommit"
        else cumulative_source_paths | working_tree_changed_paths
    )
    repository_source_scope_exact = (
        authorized_combined_source_paths == EXPECTED_CHANGED_PATHS
    )

    require(branch == REQUIRED_BRANCH, f"repository branch mismatch: {branch}")
    if repository_state == "postcommit":
        require(head_matches_origin, f"HEAD does not match {REQUIRED_REMOTE_REF}")
        require(
            start_revision_is_ancestor,
            "required starting revision is not an ancestor of HEAD",
        )
    require(
        repository_source_scope_exact,
        "exact source scope mismatch: "
        f"{sorted(authorized_combined_source_paths)}",
    )
    return {
        "repository_state": repository_state,
        "working_tree_changed_paths": sorted(working_tree_changed_paths),
        "cumulative_source_paths": sorted(cumulative_source_paths),
        "authorized_combined_source_paths": sorted(
            authorized_combined_source_paths
        ),
        "head_matches_origin": head_matches_origin,
        "repository_source_scope_exact": repository_source_scope_exact,
    }


def repository_scope() -> dict[str, Any]:
    working_tree_changed_paths = changed_paths_from_porcelain(
        git("status", "--porcelain")
    )
    cumulative_source_paths = frozenset(
        git("diff", "--name-only", f"{BASE_REVISION}..HEAD", "--").splitlines()
    )
    return evaluate_repository_scope(
        branch=git("branch", "--show-current"),
        head=git("rev-parse", "HEAD"),
        origin_head=git("rev-parse", REQUIRED_REMOTE_REF),
        start_revision_is_ancestor=git_succeeds(
            "merge-base", "--is-ancestor", REQUIRED_START_REVISION, "HEAD"
        ),
        working_tree_changed_paths=working_tree_changed_paths,
        cumulative_source_paths=cumulative_source_paths,
    )


def load_runner():
    spec = importlib.util.spec_from_file_location("ps042c6_offline_smoke_runner", RUNNER)
    require(spec is not None and spec.loader is not None, "runner import unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class PresenceOnlyMapping(Mapping[str, str]):
    """A mapping that proves code checks names without reading secret values."""

    def __init__(self, names: set[str]):
        self._names = names

    def __contains__(self, key: object) -> bool:
        return key in self._names

    def __getitem__(self, _key: str) -> str:
        raise AssertionError("credential value was inspected")

    def __iter__(self) -> Iterator[str]:
        return iter(self._names)

    def __len__(self) -> int:
        return len(self._names)


def run_smoke() -> dict[str, Any]:
    require(RUNNER.is_file() and SELF.is_file() and TESTS.is_file(), "PS-042C6 file missing")
    scope = repository_scope()
    changed = frozenset(scope["working_tree_changed_paths"])
    authorized = frozenset(scope["authorized_combined_source_paths"])
    hidden = [
        line
        for line in git("ls-files", "-v").splitlines()
        if line and line[0] in {"h", "S"}
    ]
    require(not hidden, "hidden assume-unchanged or skip-worktree flag detected")

    require(ATTEMPT_LOCK.is_file(), "current attempt lock missing")
    require(FAILURE_RECEIPT.is_file(), "current failure receipt missing")
    require(
        sha256_file(ATTEMPT_LOCK) == EXPECTED_ATTEMPT_LOCK_SHA256,
        "current attempt lock changed",
    )
    require(
        sha256_file(FAILURE_RECEIPT) == EXPECTED_FAILURE_RECEIPT_SHA256,
        "current failure receipt changed",
    )

    package_or_lock_changed = [
        path for path in authorized if Path(path).name in PACKAGE_AND_LOCK_NAMES
    ]
    require(not package_or_lock_changed, "package manifest or lockfile changed")
    require(
        not any(
            path.startswith(("docs/evidence/", "docs/ps-", "specs/"))
            for path in authorized
        ),
        "historical evidence changed",
    )
    require(
        not any(path.startswith(("apps/", "src/")) for path in authorized),
        "API or frontend source changed",
    )

    runner = load_runner()
    presence_probe = PresenceOnlyMapping(set(runner.REQUIRED_CREDENTIALS))
    presence = runner.credential_presence(presence_probe)
    require(all(presence.values()), "credential presence name check failed")
    self_test = runner.offline_self_test(PresenceOnlyMapping(set()))
    require(self_test["status"] == "PASS", "offline self-test failed")
    require(
        self_test["network_client_constructed"] is False,
        "offline self-test constructed a network client",
    )
    require(runner.RESUME_GENERATION_POST_LIMIT == 0, "resume POST maximum is not zero")
    reconciliation = runner.reconcile(FAILURE_RECEIPT, ATTEMPT_LOCK)
    require(
        reconciliation["state"] == "NEEDS_PROVIDER_CONSOLE_RECONCILIATION",
        "current legacy receipt reconciliation mismatch",
    )
    require(
        reconciliation["network_counters"]
        == {
            "provider_posts": 0,
            "provider_status_gets": 0,
            "asset_gets": 0,
            "b2_heads": 0,
            "b2_gets": 0,
            "b2_puts": 0,
        },
        "offline reconciliation network counter mismatch",
    )
    return {
        "slice": "PS-042C6",
        "mode": "offline-repository-state-smoke",
        "status": "PASS",
        **scope,
        "changed_paths": sorted(changed),
        "attempt_lock_retained": True,
        "attempt_lock_sha256_unchanged": True,
        "current_failure_receipt_unchanged": True,
        "current_receipt_reconciliation": reconciliation["state"],
        "credential_values_inspected": False,
        "provider_client_constructed": False,
        "b2_client_constructed": False,
        "resume_provider_post_hard_maximum": 0,
        "package_and_lockfiles_unchanged": True,
        "historical_evidence_unchanged": True,
        "api_and_frontend_source_unchanged": True,
        "provider_posts": 0,
        "provider_status_gets": 0,
        "asset_gets": 0,
        "b2_heads": 0,
        "b2_gets": 0,
        "b2_puts": 0,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="PS-042C6 offline repository-state smoke"
    )
    parser.add_argument("--check-only", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    build_parser().parse_args(argv)
    try:
        report = run_smoke()
    except Exception as exc:
        print(f"PS-042C6 offline smoke FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
