#!/usr/bin/env python3
"""Offline readiness smoke for PS-042C5.

This smoke performs no network I/O and writes no tracked evidence. It verifies
only the current slice, including its targeted fake-client test module.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import inspect
import json
import subprocess
import sys
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "ps042c5_one_real_genblaze_proof.py"
TESTS = ROOT / "tests" / "test_ps042c5_one_real_genblaze_proof.py"
SELF = Path(__file__).resolve()
EXPECTED_FILES = {
    "scripts/ps042c5_one_real_genblaze_proof.py",
    "scripts/ps042c5_one_real_genblaze_proof_smoke.py",
    "tests/test_ps042c5_one_real_genblaze_proof.py",
}
PRECOMMIT_REVISION = "53d4870b8e8dc0ffd916e8c0f7ee77172112c8df"
TRUSTED_ANCESTOR_COMMIT = "34e23ba80b60f3bdcaa6b46c3728310faa11ddfa"


@dataclass(frozen=True)
class SmokeRepoState:
    branch: str
    head: str
    origin: str
    changed_paths: frozenset[str]
    staged_paths: frozenset[str]
    worktree_clean: bool
    trusted_ancestor_merge_base: str
    tracked_files: frozenset[str]
    required_files_exist: bool


def git(*args: str) -> str:
    return subprocess.run(
        ("git", *args),
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout.strip()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def load_runner():
    spec = importlib.util.spec_from_file_location("ps042c5_smoke_runner", RUNNER)
    require(spec is not None and spec.loader is not None, "runner import spec unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def changed_paths_from_porcelain(porcelain: str) -> frozenset[str]:
    paths: set[str] = set()
    for line in porcelain.splitlines():
        if not line:
            continue
        fields = line.split(maxsplit=1)
        require(len(fields) == 2, f"unparseable Git status line: {line!r}")
        path = fields[1]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.add(path)
    return frozenset(paths)


def inspect_repository_state(
    git_state: Callable[..., str] = git,
    file_exists: Callable[[str], bool] | None = None,
) -> SmokeRepoState:
    exists = file_exists or (lambda path: (ROOT / path).is_file())
    porcelain = git_state("status", "--porcelain")
    try:
        merge_base = git_state("merge-base", "HEAD", TRUSTED_ANCESTOR_COMMIT)
    except subprocess.CalledProcessError:
        merge_base = ""
    return SmokeRepoState(
        branch=git_state("branch", "--show-current"),
        head=git_state("rev-parse", "HEAD"),
        origin=git_state("rev-parse", "origin/ps-042c0/free-render-staging-v1"),
        changed_paths=changed_paths_from_porcelain(porcelain),
        staged_paths=frozenset(
            line for line in git_state("diff", "--cached", "--name-only").splitlines() if line
        ),
        worktree_clean=not bool(porcelain),
        trusted_ancestor_merge_base=merge_base,
        tracked_files=frozenset(
            line
            for line in git_state("ls-files", "--", *sorted(EXPECTED_FILES)).splitlines()
            if line
        ),
        required_files_exist=all(exists(path) for path in EXPECTED_FILES),
    )


def validate_repository_state(requested: str, state: SmokeRepoState) -> str:
    require(state.branch == "ps-042c0/free-render-staging-v1", "observed branch")
    if requested == "auto":
        if state.changed_paths == EXPECTED_FILES:
            resolved = "precommit"
        elif state.worktree_clean:
            resolved = "postcommit"
        else:
            raise RuntimeError(
                f"auto repository state is neither exact precommit scope nor clean: "
                f"{sorted(state.changed_paths)}"
            )
    else:
        resolved = requested

    if resolved == "precommit":
        require(state.head == PRECOMMIT_REVISION, "precommit HEAD mismatch")
        require(state.origin == PRECOMMIT_REVISION, "precommit origin mismatch")
        require(
            state.changed_paths == EXPECTED_FILES,
            f"exact patch scope mismatch: {sorted(state.changed_paths)}",
        )
        require(not state.staged_paths, "repository changes are staged")
    elif resolved == "postcommit":
        require(state.worktree_clean, "postcommit worktree is not clean")
        require(not state.staged_paths, "repository changes are staged")
        require(state.head == state.origin, "postcommit HEAD does not match origin")
        require(
            state.trusted_ancestor_merge_base == TRUSTED_ANCESTOR_COMMIT,
            "trusted ancestor is not an ancestor of postcommit HEAD",
        )
        require(state.required_files_exist, "one or more PS-042C5 files are missing")
        require(
            state.tracked_files == EXPECTED_FILES,
            f"PS-042C5 tracked file set mismatch: {sorted(state.tracked_files)}",
        )
    else:
        raise RuntimeError(f"unsupported repository state: {resolved}")
    return resolved


def run_smoke(
    repository_state: str = "auto",
    *,
    git_state: Callable[..., str] = git,
    file_exists: Callable[[str], bool] | None = None,
) -> dict:
    require(RUNNER.is_file(), "runner missing")
    require(TESTS.is_file(), "targeted tests missing")
    runner = load_runner()
    require(runner.REQUIRED_BRANCH == "ps-042c0/free-render-staging-v1", "branch constant")
    require(
        runner.TRUSTED_ANCESTOR_COMMIT == TRUSTED_ANCESTOR_COMMIT,
        "trusted ancestor constant",
    )
    require(not hasattr(runner, "EXPECTED_ORIGIN_COMMIT"), "stale origin commit constant")
    require(not hasattr(runner, "EXPECTED_BASE_COMMIT"), "stale base commit constant")
    require(runner.PROVIDER_NAME == "gmicloud-image", "provider constant")
    require(runner.MODEL == "seedream-5.0-lite", "model constant")
    require(runner.EXPECTED_PRICE_USD == Decimal("0.035"), "price constant")
    require(runner.MAX_COST_USD == Decimal("0.05"), "ceiling constant")
    require(runner.GENERATION_SUBMIT_LIMIT == 1, "one-submit enforcement")
    require(runner.OUTPUT_COUNT == 1, "one-output enforcement")
    require(runner.AUTOMATIC_RETRY_COUNT == 0, "zero retry")
    require(runner.FALLBACK_PROVIDER_COUNT == 0, "zero fallback")
    require(runner.GENERATION_PREFLIGHT is False, "preflight disabled")
    require(runner.ASSET_DOWNLOAD_ATTEMPTS == 1, "one download")
    require(
        hashlib.sha256(runner.CANONICAL_PROMPT.encode("utf-8")).hexdigest()
        == runner.PROMPT_SHA256,
        "prompt hash",
    )
    plan_a = runner.make_key_plan("a" * 32)
    plan_b = runner.make_key_plan("b" * 32)
    require(plan_a.prefix != plan_b.prefix, "unique run-scoped prefixes")
    require(plan_a.receipt == plan_a.ordered[-1], "receipt-last plan")
    require(
        all(key.startswith(f"{runner.BASE_PREFIX}/{plan_a.proof_id}/") for key in plan_a.ordered),
        "key prefix confinement",
    )
    source = RUNNER.read_text(encoding="utf-8")
    require("list_objects" not in source and "list_buckets" not in source, "no B2 listing")
    require("RetryPolicy.disabled()" in source, "connector retry policy")
    require("fallback_models=[]" in source, "no fallback models")
    require("preflight=False" in source, "generation preflight")
    require("second generation POST blocked before sending" in source, "submit boundary")
    require("verification receipt was not written last" in source, "receipt-last assertion")
    require("assert_redacted" in source, "redaction rules")
    require("--expected-revision" in source, "expected revision CLI argument")
    require(
        "expected_revision" in inspect.signature(runner.execute_proof).parameters,
        "execute proof expected revision parameter",
    )
    require(
        "expected_revision" in inspect.signature(runner.validate_execute_gates).parameters,
        "revision gate expected revision parameter",
    )
    require("state.head != expected_revision" in source, "HEAD expected revision gate")
    require("state.origin != expected_revision" in source, "origin expected revision gate")
    require("state.head != state.origin" in source, "HEAD origin equality gate")
    require(
        "state.trusted_ancestor_merge_base != TRUSTED_ANCESTOR_COMMIT" in source,
        "trusted ancestry gate",
    )
    require(
        "expected_revision = state.head" not in source
        and "expected_revision=state.head" not in source,
        "expected revision must not be inferred from HEAD",
    )

    observed = inspect_repository_state(git_state, file_exists)
    resolved_state = validate_repository_state(repository_state, observed)
    paths = observed.changed_paths
    require(
        not paths.intersection(
            p for p in paths if p.startswith(("docs/evidence/", "specs/", "apps/", "src/"))
        ),
        "historical evidence/spec/API/frontend changed",
    )
    require(
        not paths.intersection({"package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock"}),
        "package or lockfile changed",
    )

    pytest_run = subprocess.run(
        (sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(TESTS)),
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    require(pytest_run.returncode == 0, "targeted tests failed:\n" + pytest_run.stdout)
    passed_fragment = next(
        (line.strip() for line in pytest_run.stdout.splitlines() if " passed" in line),
        "targeted tests passed",
    )
    self_test = runner.offline_self_test({})
    require(self_test["status"] == "PASS", "offline self-test")
    return {
        "slice": "PS-042C5",
        "mode": "offline-readiness-smoke",
        "status": "PASS",
        "runner_exists": True,
        "safety_constants_verified": True,
        "price_and_ceiling_verified": True,
        "prompt_hash_verified": True,
        "provider_and_model_verified": True,
        "one_submit_enforced": True,
        "zero_retries": True,
        "zero_fallback": True,
        "unique_run_scoped_prefix": True,
        "receipt_last_semantics": True,
        "exact_key_only_b2": True,
        "redaction_rules": True,
        "targeted_tests": passed_fragment,
        "historical_evidence_unchanged": True,
        "package_and_lockfiles_unchanged": True,
        "api_and_frontend_source_unchanged": True,
        "repository_state": resolved_state,
        "worktree_clean": observed.worktree_clean,
        "head_matches_origin": observed.head == observed.origin,
        "trusted_ancestor_verified": (
            observed.trusted_ancestor_merge_base == TRUSTED_ANCESTOR_COMMIT
        ),
        "provider_calls": 0,
        "b2_reads": 0,
        "b2_writes": 0,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PS-042C5 offline readiness smoke")
    parser.add_argument(
        "--repository-state",
        choices=("auto", "precommit", "postcommit"),
        default="auto",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = run_smoke(args.repository_state)
    except Exception as exc:
        print(f"PS-042C5 offline smoke FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
