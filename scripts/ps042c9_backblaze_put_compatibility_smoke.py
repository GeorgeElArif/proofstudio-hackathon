#!/usr/bin/env python3
"""Strictly offline, non-mutating PS-042C9 implementation smoke."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "ps042c6_gmi_submit_reconciliation.py"
SELF = Path(__file__).resolve()
TESTS = ROOT / "tests" / "test_ps042c9_backblaze_put_compatibility.py"
REQUIRED_BRANCH = "ps-042c0/free-render-staging-v1"
REQUIRED_REVISION = "9e1d4e75738e9748bb94ed3235f9f9dd116db45b"
EXPECTED_CHANGED_PATHS = frozenset(
    {
        "scripts/ps042c6_gmi_submit_reconciliation.py",
        "scripts/ps042c9_backblaze_put_compatibility_smoke.py",
        "tests/test_ps042c9_backblaze_put_compatibility.py",
    }
)
REAL_CONTINUATION_LOCK = Path(
    "/home/george/.local/state/proofstudio/ps042c9-funded-b2-continuation.lock"
)
PROTECTED_HASHES = {
    Path("/home/george/.local/state/proofstudio/ps042c5-one-live-attempt.lock"):
        "6a8901647faf1c6a2cba1d2bd4698ee4b2e82738ea39a60d543a20a07e25bba8",
    Path(
        "/tmp/proofstudio-ps042c5-execution/"
        "d1b4e4640bb1d79ee158bf01617e0e17/failure-receipt.json"
    ): "3be63e463727cf4f023b084d28a361e4600f3e2bff4af2b5ece29b07a74b10da",
    Path("/home/george/.local/state/proofstudio/ps042c5-funded-live-attempt.lock"):
        "322b7ed94276e2f50094d8c5bb8e5e59f7b834f24e5fa8680d82644dbfef1a2d",
    Path(
        "/tmp/proofstudio-ps042c5-execution/"
        "c252577563896fa8866963d3a3f95650/failure-receipt.json"
    ): "fc38c2119eba2d04a301f9cd6fe4400a4330aa84b3ca39c333406e79cb853c9c",
    Path(
        "/tmp/proofstudio-ps042c6-resume/"
        "c252577563896fa8866963d3a3f95650/resume-receipt.json"
    ): "aeba6b71544494d944a5ab83ff2114720ffaba748e7571cdc9061b941c352f85",
    Path("/tmp/proofstudio-ps042c8-live-resume-20260801T141528Z/resume.log"):
        "b1063cc8121454d9749ff042827931fbd988d5f26a1739d8e215f59934091864",
}
PACKAGE_AND_LOCK_NAMES = frozenset(
    {
        "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
        "requirements.txt", "poetry.lock", "uv.lock",
    }
)
ZERO_NETWORK_COUNTERS = {
    "provider_posts": 0,
    "provider_status_gets": 0,
    "asset_gets": 0,
    "b2_heads": 0,
    "b2_puts": 0,
    "b2_gets": 0,
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def git(*args: str) -> str:
    return subprocess.run(
        ("git", *args), cwd=ROOT, check=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout.rstrip()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def changed_paths() -> frozenset[str]:
    paths: set[str] = set()
    for line in git("status", "--porcelain").splitlines():
        require(len(line) >= 4, "unparseable Git status")
        paths.add(line[3:].split(" -> ", 1)[-1])
    return frozenset(paths)


def load_runner():
    spec = importlib.util.spec_from_file_location("ps042c9_offline_runner", RUNNER)
    require(spec is not None and spec.loader is not None, "runner import unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def plain_put_keywords() -> set[str]:
    tree = ast.parse(RUNNER.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "BackblazeCompatibleB2Client":
            for child in ast.walk(node):
                if (
                    isinstance(child, ast.Call)
                    and isinstance(child.func, ast.Attribute)
                    and child.func.attr == "put_object"
                ):
                    return {keyword.arg for keyword in child.keywords if keyword.arg}
    raise RuntimeError("C9 plain PutObject call not found")


def run_smoke() -> dict[str, Any]:
    require(RUNNER.is_file() and SELF.is_file() and TESTS.is_file(), "C9 source missing")
    require(git("branch", "--show-current") == REQUIRED_BRANCH, "branch mismatch")
    require(git("rev-parse", "HEAD") == REQUIRED_REVISION, "HEAD changed")
    require(
        git("rev-parse", f"origin/{REQUIRED_BRANCH}") == REQUIRED_REVISION,
        "local origin ref changed",
    )
    changed = changed_paths()
    require(changed == EXPECTED_CHANGED_PATHS, f"patch scope mismatch: {sorted(changed)}")
    hidden = [
        line for line in git("ls-files", "-v").splitlines()
        if line and line[0] in {"h", "S"}
    ]
    require(not hidden, "hidden Git index flag detected")
    require(not REAL_CONTINUATION_LOCK.exists(), "real continuation lock exists")
    before = {path: path.read_bytes() for path in PROTECTED_HASHES}
    for path, expected in PROTECTED_HASHES.items():
        require(path.is_file(), "protected evidence missing")
        require(sha256_file(path) == expected, "protected evidence hash mismatch")

    runner = load_runner()
    require(not REAL_CONTINUATION_LOCK.exists(), "runner import created real lock")
    keywords = plain_put_keywords()
    require(
        keywords == {"Bucket", "Key", "Body", "ContentType"},
        f"plain PutObject fixture has unexpected fields: {sorted(keywords)}",
    )
    runner._verify_rehydrated_bytes("offline/key", b"fixture", b"fixture")
    with tempfile.TemporaryDirectory(prefix="ps042c9-offline-lock-") as temp:
        lock = Path(temp) / "continuation.lock"
        runner.create_c9_execution_lock(
            lock,
            now=datetime(2026, 8, 1, tzinfo=timezone.utc),
            branch=REQUIRED_BRANCH,
            expected_revision=REQUIRED_REVISION,
            proof_id=runner.FUNDED_PROOF_ID,
            request_id=runner.FUNDED_AUTHORIZED_REQUEST_ID,
        )
        require(lock.is_file(), "temporary single-writer lock not created")
        try:
            runner.create_c9_execution_lock(
                lock,
                now=datetime(2026, 8, 1, tzinfo=timezone.utc),
                branch=REQUIRED_BRANCH,
                expected_revision=REQUIRED_REVISION,
                proof_id=runner.FUNDED_PROOF_ID,
                request_id=runner.FUNDED_AUTHORIZED_REQUEST_ID,
            )
        except runner.SafetyError:
            pass
        else:
            raise RuntimeError("existing temporary continuation lock did not block")

    require(not REAL_CONTINUATION_LOCK.exists(), "smoke created real continuation lock")
    require(
        all(path.read_bytes() == raw for path, raw in before.items()),
        "protected evidence changed",
    )
    require(
        not any(Path(path).name in PACKAGE_AND_LOCK_NAMES for path in changed),
        "package or lockfile changed",
    )
    require(
        not any(path.startswith(("apps/", "src/")) for path in changed),
        "API or frontend source changed",
    )
    subprocess.run(("git", "diff", "--check"), cwd=ROOT, check=True)
    source = RUNNER.read_text()
    require("postwrite_byte_verification" in source, "postwrite boundary missing")
    require('"atomic_create_if_absent": False' in source, "non-atomic boundary missing")
    return {
        "slice": "PS-042C9",
        "mode": "strictly-offline-static-and-local-fixture-validation",
        "status": "PASS",
        "head": REQUIRED_REVISION,
        "origin_head": REQUIRED_REVISION,
        "changed_paths": sorted(changed),
        "network_clients_constructed": False,
        "network_counters": dict(ZERO_NETWORK_COUNTERS),
        "plain_put_keywords": sorted(keywords),
        "plain_put_no_if_none_match": True,
        "postwrite_byte_verification": True,
        "atomic_create_if_absent": False,
        "local_single_writer_enforced": True,
        "protected_evidence_unchanged": True,
        "offline_runner": True,
        "offline_precommit_gate": True,
    }


def main() -> int:
    try:
        result = run_smoke()
    except Exception as exc:
        print(f"PS-042C9 smoke FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    values = {
        "PS042C9_PROVIDER_POSTS": 0,
        "PS042C9_PROVIDER_STATUS_GETS": 0,
        "PS042C9_ASSET_GETS": 0,
        "PS042C9_B2_HEADS": 0,
        "PS042C9_B2_PUTS": 0,
        "PS042C9_B2_GETS": 0,
        "PS042C9_PLAIN_PUT_NO_IF_NONE_MATCH": "PASS",
        "PS042C9_POSTWRITE_BYTE_VERIFICATION": "PASS",
        "PS042C9_NON_ATOMIC_TRUTH_BOUNDARY": "PASS",
        "PS042C9_SINGLE_WRITER_BOUNDARY": "PASS",
        "PS042C9_ORIGINAL_LOCK_UNCHANGED": "PASS",
        "PS042C9_ORIGINAL_RECEIPT_UNCHANGED": "PASS",
        "PS042C9_FUNDED_LOCK_UNCHANGED": "PASS",
        "PS042C9_FUNDED_RECEIPT_UNCHANGED": "PASS",
        "PS042C9_PRIOR_RESUME_RECEIPT_UNCHANGED": "PASS",
        "PS042C9_PRIOR_LIVE_LOG_UNCHANGED": "PASS",
        "PS042C9_OFFLINE_RUNNER": "PASS",
        "PS042C9_OFFLINE_PRECOMMIT_GATE": "PASS",
    }
    for key, value in values.items():
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
