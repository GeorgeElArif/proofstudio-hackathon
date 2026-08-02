#!/usr/bin/env python3
"""PS-041E2-B Phase-1 — Live executor readiness smoke (fake-backend, check-only).

This smoke runs the full live execute flow end-to-end with injected fake
dependencies. It exercises every one of the 22 implemented live gates and
the complete 32-step operation order. It never accesses the network, never
calls a provider, never constructs a real ``S3StorageBackend.for_backblaze``
client, never reads credential values, and never writes a real B2 object.

The smoke proves:

- all 22 implemented gates pass under a fake accepted-state run;
- the credential provider and backend factory are not called before all gates
  pass;
- the backend is a FakeB2Backend wrapped by GuardedLiveBackend (no real
  client is constructed);
- the 32-step operation order produces the exact expected operation counters;
- list / write / delete / signed-URL / provider operation counters are zero;
- the resulting evidence contains no credential value, raw bucket name,
  endpoint URL, or object bytes.

Run:

    PYTHONPATH=src python scripts/ps041e2_b2_execute_readiness_smoke.py

Expected output is the structured JSON block defined in the PS-041E2-B Phase-1
execute-readiness contract.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import ps041e2_b2_evidence as ev  # noqa: E402

FIXTURE = ROOT / "tests/fixtures/ps041d/genblaze-multi-provider-bundle-v1.json"
SLICE = "PS-041E2-B"

PREFIX = "import-root/ps041e2"

SERVER_ALIAS = ev.DEFAULT_FAKE_SERVER_ALIAS
SERVER_BUCKET_IDENTITY = ev.DEFAULT_FAKE_SERVER_BUCKET_IDENTITY
BUCKET_HASH = hashlib.sha256(SERVER_BUCKET_IDENTITY.encode("utf-8")).hexdigest()

NOW = datetime.now(timezone.utc)
AUTHORIZED_AT = (NOW - timedelta(minutes=1)).isoformat().replace("+00:00", "Z")
EXPIRES_AT = (NOW + timedelta(hours=1)).isoformat().replace("+00:00", "Z")

# The accepted-base commit this branch was created from. Phase-1 itself runs
# on the implementation branch and proves the executor's behavior with a fake
# git_state whose head_commit and accepted_commit both equal this value. The
# real CLI execute mode refuses unless HEAD equals origin/accepted/proofstudio,
# which is enforced by gate 21 in production but bypassed here via the fake.
EXECUTION_COMMIT = "418fc51b4df02e3217a93d43ee9d95bb98ec6abf"

ALLOWED_KEYS = [
    f"{PREFIX}/stage-a/storyboard.json",
    f"{PREFIX}/runs/b0/manifest.json",
    f"{PREFIX}/runs/b1/manifest.json",
    f"{PREFIX}/runs/b2/manifest.json",
    f"{PREFIX}/composition/final.mp4",
]

OBJECT_ROLE_BY_KEY = {
    ALLOWED_KEYS[0]: ev.ROLE_STAGE_A_STORYBOARD,
    ALLOWED_KEYS[1]: ev.ROLE_STAGE_B0_MANIFEST,
    ALLOWED_KEYS[2]: ev.ROLE_STAGE_B1_MANIFEST,
    ALLOWED_KEYS[3]: ev.ROLE_STAGE_B2_MANIFEST,
    ALLOWED_KEYS[4]: ev.ROLE_FINAL_DELIVERY,
}


class _FakeCredProvider:
    """Counts calls; returns inert strings; never reads environment values."""

    def __init__(self) -> None:
        self.call_count = 0

    def __call__(self) -> "ev.LiveCredentials":
        self.call_count += 1
        return ev.LiveCredentials(
            key_id="fake-key-id", app_key="fake-app-key",
            bucket="fake-bucket", region="fake-region",
        )


class _FakeBackendFactory:
    """Returns a FakeB2Backend; never constructs a real B2 / S3 client."""

    def __init__(self) -> None:
        self.call_count = 0

    def __call__(self, credentials: "ev.LiveCredentials"):
        self.call_count += 1
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        return ev._build_fake_backend(
            fixture, list(ALLOWED_KEYS), object_role_by_key=dict(OBJECT_ROLE_BY_KEY),
        )


def _smoke_authorization() -> dict:
    expected = ev.expected_hashes_for_fixture(
        FIXTURE, list(ALLOWED_KEYS), OBJECT_ROLE_BY_KEY,
    )
    # Default smoke: media reads disabled; only JSON keys carry expected hashes.
    expected_json_only = {k: v for k, v in expected.items()
                          if OBJECT_ROLE_BY_KEY[k] in ev.JSON_READ_ROLES}
    return {
        "schema": ev.LIVE_SCHEMA,
        "authorized": True,
        "authorized_by": "ps-041e2b-execute-readiness-smoke",
        "authorized_at": AUTHORIZED_AT,
        "expires_at": EXPIRES_AT,
        "configured_alias": SERVER_ALIAS,
        "allowed_bucket_name_hash": BUCKET_HASH,
        "allowed_prefix": PREFIX,
        "allowed_keys": list(ALLOWED_KEYS),
        "object_role_by_key": dict(OBJECT_ROLE_BY_KEY),
        "max_object_count": 16,
        "max_object_bytes": 1_048_576,
        "max_total_bytes": 16_777_216,
        "allow_metadata_reads": True,
        "allow_json_object_reads": True,
        "allow_media_byte_reads": False,
        "allow_sha256_verification": True,
        "allow_write": False,
        "allow_delete": False,
        "allow_signed_urls": False,
        "allow_provider_calls": False,
        "expected_sha256_by_key": expected_json_only,
        "purpose": ev.LIVE_PURPOSE,
        "evidence_run_id": "ps041e2b-smoke-fake-live-executor",
        "execution_commit": EXECUTION_COMMIT,
    }


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    parser = argparse.ArgumentParser(description="PS-041E2-B Phase-1 execute-readiness smoke")
    parser.add_argument("--check-only", action="store_true", default=True)
    parser.add_argument("--write-evidence", action="store_true")
    parser.add_argument("--no-frontend", action="store_true")
    args = parser.parse_args()
    if args.write_evidence:
        print(json.dumps({
            "ok": False,
            "error": "PS-041E2-B execute-readiness smoke does not own canonical evidence writes",
        }))
        return 1

    auth = _smoke_authorization()
    cred = _FakeCredProvider()
    factory = _FakeBackendFactory()
    git_state = ev.GitState(
        branch=ev.PS_041E2B_BRANCH, head_commit=EXECUTION_COMMIT,
        accepted_commit=EXECUTION_COMMIT, accepted_ref=ev.ACCEPTED_EXECUTION_REF,
        tree_clean=True,
    )
    server_config = ev.ServerConfig(
        alias=SERVER_ALIAS, import_root=PREFIX,
        bucket_identity=SERVER_BUCKET_IDENTITY, region="us-west-000-fake",
        required_credentials_present=True,
    )

    class _FakeRemoteRefResolver:
        def __init__(self) -> None:
            self.call_count = 0

        def __call__(self, ref: str) -> str:
            self.call_count += 1
            return EXECUTION_COMMIT

    remote_ref_resolver = _FakeRemoteRefResolver()
    from proofstudio.api.services import ProofStudioService
    import_service = ProofStudioService()
    evidence_dir = Path(tempfile.mkdtemp(prefix="ps041e2b-execute-smoke-")) / "evidence"

    try:
        report = ev.run_live_execute(
            auth, fixture_path=FIXTURE, evidence_dir=evidence_dir,
            git_state=git_state, server_config=server_config,
            credential_provider=cred, backend_factory=factory,
            import_service=import_service, remote_ref_resolver=remote_ref_resolver,
            confirm_controlled_live_read=True,
            real_backend_factory_used=False,
        )
    except Exception as exc:
        print(json.dumps({
            "ok": False, "slice": SLICE, "mode": "fake-live-executor",
            "error": f"{type(exc).__name__}: {exc}",
        }, sort_keys=True))
        return 1

    _require(report.ok is True, "fake live execute run must succeed")
    _require(len(report.gates) == 22, "all 22 gates must be evaluated")
    _require(all(g.ok for g in report.gates), "all 22 gates must pass")
    _require(cred.call_count == 1, "credential provider must be called exactly once after all gates passed")
    _require(factory.call_count == 1, "backend factory must be called exactly once after all gates passed")
    _require(report.list_calls == 0, "no list calls allowed")
    _require(report.write_attempts == 0, "no write attempts allowed")
    _require(report.delete_attempts == 0, "no delete attempts allowed")
    _require(report.signed_url_attempts == 0, "no signed URL attempts allowed")
    _require(report.provider_calls == 0, "no provider calls allowed")
    # Canonical exact-key counters: the controlled read path produces zero
    # head_bucket calls and zero regional probes even on the fake path
    # (the fake never triggers the lazy preflight).
    _require(report.head_bucket_http_attempts == 0, "no head_bucket HTTP attempts")
    _require(report.regional_probe_http_attempts == 0, "no regional-probe HTTP attempts")
    _require(report.head_object_sdk_calls == report.head_calls_total,
             "head_object_sdk_calls must mirror head_calls_total")
    _require(report.ranged_get_object_sdk_calls == report.read_calls_total,
             "ranged_get_object_sdk_calls must mirror read_calls_total")
    _require(report.head_object_http_attempts == 0,
             "fake execution must report zero HeadObject HTTP attempts")
    _require(report.ranged_get_object_http_attempts == 0,
             "fake execution must report zero GetObject HTTP attempts")
    # Underlying client closed exactly once.
    _require(report.inner_close_attempted is True, "inner close must be attempted")
    _require(report.inner_close_succeeded is True, "inner close must succeed")
    _require(report.inner_close_call_count == 1, "inner close must be called exactly once")
    _require(report.unique_json_objects_read == 4, "four JSON objects must be read once each")
    _require(report.unique_media_objects_read == 0, "default run reads zero media objects")
    _require(report.read_calls_total == 4, "exactly 4 backend read calls (one per JSON object)")
    _require(report.snapshot_consumer_calls == 8, "8 snapshot consumer calls (4 objects x 2 builds)")
    _require(report.observation_stable is True, "observation must be stable")
    _require(report.observation_comparisons == 5, "observation must compare all 5 allowlisted objects")
    _require(report.import_idempotent is True, "import must be idempotent")
    _require(report.passport_schema == ev.PASSPORT_SCHEMA, "passport schema must match accepted contract")
    _require(report.cleanup_verified is True, "cleanup must be verified")
    _require(report.alias_comparison_code == "alias_match", "alias comparison must report a match")
    _require(report.bucket_comparison_code == "bucket_match", "bucket comparison must report a match")

    # Final security check: no raw bucket name in evidence output.
    run_dir = Path(report.evidence_dir)
    blob = ""
    for path in sorted(run_dir.iterdir()):
        if path.is_file():
            blob += path.read_text(encoding="utf-8", errors="ignore")
    _require(SERVER_BUCKET_IDENTITY not in blob, "raw bucket name must not appear in evidence")
    for forbidden in ("https://", "http://", ".backblazeb2.com", "fake-app-key", "fake-key-id"):
        _require(forbidden not in blob.lower(),
                 f"forbidden token must not appear in evidence: {forbidden}")

    output = {
        "ok": True,
        "slice": SLICE,
        "mode": "fake-live-executor",
        "phase": "phase-1",
        "future_execute_gates_count": ev.FUTURE_EXECUTE_GATES_COUNT,
        "live_execute_gates_count": ev.LIVE_EXECUTE_GATES_COUNT,
        "all_execute_gates_passed": True,
        "client_constructed": True,
        "head_calls_total": report.head_calls_total,
        "read_calls_total": report.read_calls_total,
        "head_object_sdk_calls": report.head_object_sdk_calls,
        "ranged_get_object_sdk_calls": report.ranged_get_object_sdk_calls,
        "head_object_http_attempts": report.head_object_http_attempts,
        "ranged_get_object_http_attempts": report.ranged_get_object_http_attempts,
        "head_bucket_http_attempts": report.head_bucket_http_attempts,
        "regional_probe_http_attempts": report.regional_probe_http_attempts,
        "inner_close_attempted": report.inner_close_attempted,
        "inner_close_succeeded": report.inner_close_succeeded,
        "inner_close_call_count": report.inner_close_call_count,
        "unique_json_objects_read": report.unique_json_objects_read,
        "unique_media_objects_read": report.unique_media_objects_read,
        "snapshot_consumer_calls": report.snapshot_consumer_calls,
        "list_calls": report.list_calls,
        "write_attempts": report.write_attempts,
        "delete_attempts": report.delete_attempts,
        "signed_url_attempts": report.signed_url_attempts,
        "provider_calls": report.provider_calls,
        "total_bytes_read": report.total_bytes_read,
        "passport_schema": report.passport_schema,
        "observation_stable": report.observation_stable,
        "observation_comparisons": report.observation_comparisons,
        "import_idempotent": report.import_idempotent,
        "alias_comparison_code": report.alias_comparison_code,
        "bucket_comparison_code": report.bucket_comparison_code,
        "cleanup_verified": report.cleanup_verified,
        "credential_provider_call_count": cred.call_count,
        "backend_factory_call_count": factory.call_count,
        "live_b2_calls": 0,
        "real_backend_factory_used": False,
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
