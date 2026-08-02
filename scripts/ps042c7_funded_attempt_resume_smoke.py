#!/usr/bin/env python3
"""Strictly offline, non-mutating PS-042C7 funded-attempt smoke."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "ps042c6_gmi_submit_reconciliation.py"
SELF = Path(__file__).resolve()
TESTS = ROOT / "tests" / "test_ps042c7_funded_attempt_resume.py"
REQUIRED_BRANCH = "ps-042c0/free-render-staging-v1"
REQUIRED_START_REVISION = "d19d1188a3f3c4c925b85859daf9f0d6153abf12"
REQUIRED_REMOTE_REF = f"origin/{REQUIRED_BRANCH}"
ORIGINAL_LOCK = Path(
    "/home/george/.local/state/proofstudio/ps042c5-one-live-attempt.lock"
)
ORIGINAL_RECEIPT = Path(
    "/tmp/proofstudio-ps042c5-execution/"
    "d1b4e4640bb1d79ee158bf01617e0e17/failure-receipt.json"
)
FUNDED_LOCK = Path(
    "/home/george/.local/state/proofstudio/ps042c5-funded-live-attempt.lock"
)
FUNDED_RECEIPT = Path(
    "/tmp/proofstudio-ps042c5-execution/"
    "c252577563896fa8866963d3a3f95650/failure-receipt.json"
)
EXPECTED_HASHES = {
    ORIGINAL_LOCK: "6a8901647faf1c6a2cba1d2bd4698ee4b2e82738ea39a60d543a20a07e25bba8",
    ORIGINAL_RECEIPT: "3be63e463727cf4f023b084d28a361e4600f3e2bff4af2b5ece29b07a74b10da",
    FUNDED_LOCK: "322b7ed94276e2f50094d8c5bb8e5e59f7b834f24e5fa8680d82644dbfef1a2d",
    FUNDED_RECEIPT: "fc38c2119eba2d04a301f9cd6fe4400a4330aa84b3ca39c333406e79cb853c9c",
}
EXPECTED_CHANGED_PATHS = frozenset(
    {
        "scripts/ps042c6_gmi_submit_reconciliation.py",
        "scripts/ps042c7_funded_attempt_resume_smoke.py",
        "tests/test_ps042c7_funded_attempt_resume.py",
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
ZERO_NETWORK_COUNTERS = {
    "provider_posts": 0,
    "provider_status_gets": 0,
    "asset_gets": 0,
    "b2_heads": 0,
    "b2_gets": 0,
    "b2_puts": 0,
}


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


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def changed_paths_from_porcelain(value: str) -> frozenset[str]:
    paths: set[str] = set()
    for line in value.splitlines():
        require(len(line) >= 4, "unparseable Git status")
        path = line[3:].split(" -> ", 1)[-1]
        paths.add(path)
    return frozenset(paths)


def repository_scope() -> dict[str, Any]:
    branch = git("branch", "--show-current")
    head = git("rev-parse", "HEAD")
    origin = git("rev-parse", REQUIRED_REMOTE_REF)
    changed = changed_paths_from_porcelain(git("status", "--porcelain"))
    require(branch == REQUIRED_BRANCH, "repository branch mismatch")
    require(head == REQUIRED_START_REVISION, "HEAD is not the required start revision")
    require(origin == REQUIRED_START_REVISION, "origin ref is not the required revision")
    require(changed == EXPECTED_CHANGED_PATHS, f"exact source scope mismatch: {sorted(changed)}")
    return {
        "branch": branch,
        "head": head,
        "origin_head": origin,
        "changed_paths": sorted(changed),
        "repository_source_scope_exact": True,
    }


def load_runner():
    spec = importlib.util.spec_from_file_location("ps042c7_offline_runner", RUNNER)
    require(spec is not None and spec.loader is not None, "runner import unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run_smoke() -> dict[str, Any]:
    require(RUNNER.is_file() and SELF.is_file() and TESTS.is_file(), "C7 source missing")
    scope = repository_scope()
    hidden = [
        line
        for line in git("ls-files", "-v").splitlines()
        if line and line[0] in {"h", "S"}
    ]
    require(not hidden, "hidden Git index flag detected")
    before = {path: path.read_bytes() for path in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        require(path.is_file(), f"immutable artifact missing: {path.name}")
        require(sha256_file(path) == expected, f"immutable artifact changed: {path.name}")

    runner = load_runner()

    def forbidden_client(*_args: Any, **_kwargs: Any) -> Any:
        raise AssertionError("offline reconcile constructed a network client")

    runner._default_provider_transport = forbidden_client
    runner._default_b2_transport = forbidden_client
    reconciliation = runner.reconcile(FUNDED_RECEIPT, FUNDED_LOCK, "funded")
    require(
        reconciliation["state"] == "READY_TO_RESUME_EXISTING_SUCCESSFUL_REQUEST",
        "funded reconciliation state mismatch",
    )
    require(
        reconciliation["network_counters"] == ZERO_NETWORK_COUNTERS,
        "offline reconciliation network counter mismatch",
    )
    require(
        all(path.read_bytes() == raw for path, raw in before.items()),
        "immutable artifact changed during smoke",
    )
    changed = frozenset(scope["changed_paths"])
    require(
        not any(Path(path).name in PACKAGE_AND_LOCK_NAMES for path in changed),
        "package or lockfile changed",
    )
    require(
        not any(path.startswith(("apps/", "src/")) for path in changed),
        "API or frontend source changed",
    )
    return {
        "slice": "PS-042C7",
        "mode": "strictly-offline-funded-attempt-reconcile",
        "status": "PASS",
        **scope,
        "provider_client_constructed": False,
        "b2_client_constructed": False,
        "funded_reconciliation_state": reconciliation["state"],
        "network_counters": reconciliation["network_counters"],
        "original_lock_unchanged": True,
        "original_receipt_unchanged": True,
        "funded_lock_unchanged": True,
        "funded_receipt_unchanged": True,
        "package_and_lockfiles_unchanged": True,
        "api_and_frontend_source_unchanged": True,
    }


def main() -> int:
    try:
        result = run_smoke()
    except Exception as exc:
        print(f"PS-042C7 smoke FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
