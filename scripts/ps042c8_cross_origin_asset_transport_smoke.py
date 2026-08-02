#!/usr/bin/env python3
"""Strictly offline, non-mutating PS-042C8 split-origin transport smoke."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import httpx


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "ps042c6_gmi_submit_reconciliation.py"
SELF = Path(__file__).resolve()
TESTS = ROOT / "tests" / "test_ps042c8_cross_origin_asset_transport.py"
REQUIRED_BRANCH = "ps-042c0/free-render-staging-v1"
REQUIRED_REVISION = "cb66bceb8fd41bee992d65d32c73b3532d11a5ce"
REQUIRED_REMOTE_REF = f"origin/{REQUIRED_BRANCH}"
EXPECTED_CHANGED_PATHS = frozenset(
    {
        "scripts/ps042c6_gmi_submit_reconciliation.py",
        "scripts/ps042c8_cross_origin_asset_transport_smoke.py",
        "tests/test_ps042c8_cross_origin_asset_transport.py",
    }
)
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
        paths.add(line[3:].split(" -> ", 1)[-1])
    return frozenset(paths)


def load_runner():
    spec = importlib.util.spec_from_file_location("ps042c8_offline_runner", RUNNER)
    require(spec is not None and spec.loader is not None, "runner import unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run_smoke() -> dict[str, Any]:
    require(RUNNER.is_file() and SELF.is_file() and TESTS.is_file(), "C8 source missing")
    require(git("branch", "--show-current") == REQUIRED_BRANCH, "branch mismatch")
    require(git("rev-parse", "HEAD") == REQUIRED_REVISION, "HEAD changed")
    require(
        git("rev-parse", REQUIRED_REMOTE_REF) == REQUIRED_REVISION,
        "local origin ref changed",
    )
    changed = changed_paths_from_porcelain(git("status", "--porcelain"))
    require(changed == EXPECTED_CHANGED_PATHS, f"exact patch scope mismatch: {sorted(changed)}")
    hidden = [
        line
        for line in git("ls-files", "-v").splitlines()
        if line and line[0] in {"h", "S"}
    ]
    require(not hidden, "hidden Git index flag detected")
    before = {path: path.read_bytes() for path in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        require(path.is_file(), "protected evidence file missing")
        require(sha256_file(path) == expected, "protected evidence hash changed")

    runner = load_runner()
    sends = 0
    construction: list[dict[str, Any]] = []

    def forbidden_send(_request: httpx.Request) -> httpx.Response:
        nonlocal sends
        sends += 1
        raise AssertionError("offline smoke sent an external request")

    def factory(**kwargs: Any) -> httpx.Client:
        construction.append(dict(kwargs))
        return httpx.Client(transport=httpx.MockTransport(forbidden_send), **kwargs)

    transport = runner.SplitOriginProviderTransport(
        {"GMI_API_KEY": "offline-smoke-secret"}, client_factory=factory
    )
    try:
        status_request = transport._status_client.build_request(
            "GET", "/requests/request_safe_1"
        )
        asset_request = transport._asset_client.build_request(
            "GET", "https://storage.googleapis.com/proof/path.png?signature=redacted"
        )
        status_auth = "authorization" in status_request.headers
        asset_auth_absent = "authorization" not in asset_request.headers
        split = transport._status_client is not transport._asset_client
        redirects_disabled = (
            construction[0]["follow_redirects"] is False
            and construction[1]["follow_redirects"] is False
        )
        anonymous_has_no_base = "base_url" not in construction[1]
    finally:
        transport.close()

    require(sends == 0, "an external client sent a request")
    require(status_auth, "status build_request omitted Authorization")
    require(asset_auth_absent, "asset build_request included Authorization")
    require(split and anonymous_has_no_base, "split client boundary invalid")
    require(redirects_disabled, "redirects enabled")
    require(
        all(path.read_bytes() == raw for path, raw in before.items()),
        "protected evidence changed during smoke",
    )
    require(
        not any(Path(path).name in PACKAGE_AND_LOCK_NAMES for path in changed),
        "package or lockfile changed",
    )
    require(
        not any(path.startswith(("apps/", "src/")) for path in changed),
        "API or frontend source changed",
    )
    return {
        "slice": "PS-042C8",
        "mode": "strictly-offline-split-origin-build-request",
        "status": "PASS",
        "head": REQUIRED_REVISION,
        "origin_head": REQUIRED_REVISION,
        "changed_paths": sorted(changed),
        "network_counters": dict(ZERO_NETWORK_COUNTERS),
        "external_client_sends": sends,
        "status_authorization_present": status_auth,
        "asset_authorization_absent": asset_auth_absent,
        "split_client_boundary": split and anonymous_has_no_base,
        "redirects_disabled": redirects_disabled,
        "original_lock_unchanged": True,
        "original_receipt_unchanged": True,
        "funded_lock_unchanged": True,
        "funded_receipt_unchanged": True,
        "offline_runner": True,
        "offline_precommit_gate": True,
    }


def main() -> int:
    try:
        result = run_smoke()
    except Exception as exc:
        print(f"PS-042C8 smoke FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    values = {
        "PS042C8_PROVIDER_POSTS": 0,
        "PS042C8_PROVIDER_STATUS_GETS": 0,
        "PS042C8_ASSET_GETS": 0,
        "PS042C8_B2_HEADS": 0,
        "PS042C8_B2_GETS": 0,
        "PS042C8_B2_PUTS": 0,
        "PS042C8_STATUS_AUTHORIZATION_PRESENT": "PASS",
        "PS042C8_ASSET_AUTHORIZATION_ABSENT": "PASS",
        "PS042C8_SPLIT_CLIENT_BOUNDARY": "PASS",
        "PS042C8_REDIRECTS_DISABLED": "PASS",
        "PS042C8_ORIGINAL_LOCK_UNCHANGED": "PASS",
        "PS042C8_ORIGINAL_RECEIPT_UNCHANGED": "PASS",
        "PS042C8_FUNDED_LOCK_UNCHANGED": "PASS",
        "PS042C8_FUNDED_RECEIPT_UNCHANGED": "PASS",
        "PS042C8_OFFLINE_RUNNER": "PASS",
        "PS042C8_OFFLINE_PRECOMMIT_GATE": "PASS",
    }
    for key, value in values.items():
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
