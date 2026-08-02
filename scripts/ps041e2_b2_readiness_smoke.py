#!/usr/bin/env python3
"""PS-041E2-A — B2 evidence readiness smoke (fake-storage, check-only).

This smoke runs one bounded fake-storage evidence flow end-to-end and
confirms every readiness contract for the later controlled live-B2 read.
It never accesses the network, never calls a provider, and never constructs
a live storage client. Server identity (alias and bucket) is injected as
independent constants, never derived from the authorization document.

Run:

    PYTHONPATH=src python scripts/ps041e2_b2_readiness_smoke.py

Expected output is the structured JSON block defined in the PS-041E2-A
readiness contract, including actual backend operation counters.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import ps041e2_b2_evidence as ev  # noqa: E402
from proofstudio.api.genblaze_external_adapter import ImportValidationError  # noqa: E402

FIXTURE = ROOT / "tests/fixtures/ps041d/genblaze-multi-provider-bundle-v1.json"
SLICE = "PS-041E2-A"

PREFIX = "import-root/ps041e2"

# Independently injected fake server identity. These constants are deliberately
# separate from the authorization document values; the dry-run compares them.
SERVER_ALIAS = ev.DEFAULT_FAKE_SERVER_ALIAS
SERVER_BUCKET_IDENTITY = ev.DEFAULT_FAKE_SERVER_BUCKET_IDENTITY
BUCKET_HASH = hashlib.sha256(SERVER_BUCKET_IDENTITY.encode("utf-8")).hexdigest()

NOW = datetime.now(timezone.utc)
AUTHORIZED_AT = (NOW - timedelta(minutes=1)).isoformat().replace("+00:00", "Z")
EXPIRES_AT = (NOW + timedelta(hours=1)).isoformat().replace("+00:00", "Z")

ALLOWED_KEYS = [
    f"{PREFIX}/stage-a/storyboard.json",
    f"{PREFIX}/runs/b0/manifest.json",
    f"{PREFIX}/runs/b1/manifest.json",
    f"{PREFIX}/runs/b2/manifest.json",
    f"{PREFIX}/composition/final.mp4",
]

# Explicit object-role plan. Every allowlisted key maps to exactly one bounded
# role. Resolution uses this map only — never allowlist order, never a loose
# endswith() match.
OBJECT_ROLE_BY_KEY = {
    ALLOWED_KEYS[0]: ev.ROLE_STAGE_A_STORYBOARD,
    ALLOWED_KEYS[1]: ev.ROLE_STAGE_B0_MANIFEST,
    ALLOWED_KEYS[2]: ev.ROLE_STAGE_B1_MANIFEST,
    ALLOWED_KEYS[3]: ev.ROLE_STAGE_B2_MANIFEST,
    ALLOWED_KEYS[4]: ev.ROLE_FINAL_DELIVERY,
}


def _smoke_authorization() -> dict:
    expected = ev.expected_hashes_for_fixture(
        FIXTURE, list(ALLOWED_KEYS), OBJECT_ROLE_BY_KEY,
    )
    # Media reads are disabled; only JSON keys carry an expected digest.
    expected_json_only = {k: v for k, v in expected.items()
                          if OBJECT_ROLE_BY_KEY[k] in ev.JSON_READ_ROLES}
    return {
        "schema": ev.SCHEMA,
        "authorized": True,
        "authorized_by": "ps-041e2-readiness-smoke",
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
        "purpose": ev.PURPOSE,
    }


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _verify_readiness_contracts(report: "ev.DryRunReport", auth: dict) -> None:
    _require(report.ok, "dry-run must succeed")
    _require(report.authorized_objects == len(auth["allowed_keys"]),
             "authorized object count must match allowlist")
    _require(report.provider_calls == 0, "provider calls must be zero")
    _require(report.write_attempts == 0, "B2 write attempts must be zero")
    _require(report.delete_attempts == 0, "B2 delete attempts must be zero")
    _require(report.list_calls == 0, "B2 broad list calls must be zero")
    _require(report.signed_url_attempts == 0, "signed URL attempts must be zero")
    _require(report.import_idempotent is True, "import must be idempotent")
    _require(report.observation_stable is True, "TOCTOU observations must be stable")
    _require(report.observation_comparisons == len(auth["allowed_keys"]),
             "observation must compare every allowlisted object")
    _require(report.passport_schema == ev.PASSPORT_SCHEMA,
             "passport schema must match accepted contract")
    _require(report.alias_comparison_code == "alias_match",
             "alias comparison must report a match against injected server alias")
    _require(report.bucket_comparison_code == "bucket_match",
             "bucket comparison must report a match against injected server bucket")
    # Default five-object readiness: 4 JSON objects read once each, 0 media.
    json_key_count = sum(1 for k in auth["allowed_keys"]
                         if auth["object_role_by_key"][k] in ev.JSON_READ_ROLES)
    _require(report.unique_json_objects_read == json_key_count,
             "unique JSON objects read must equal the JSON-role key count")
    _require(report.unique_media_objects_read == 0,
             "default readiness must read zero media objects")
    _require(report.read_calls_total == json_key_count,
             "backend read operations must equal the JSON-role key count (one read per object)")
    _require(report.snapshot_consumer_calls == json_key_count * 2,
             "snapshot consumer calls must equal JSON objects x 2 builds (candidate + idempotency)")
    _require(report.total_bytes_read > 0, "total bytes read must be positive")
    _require(len(report.hash_results) > 0, "at least one hash result expected")
    allowed_statuses = {"matched", "observed", "computed", "mismatch"}
    for result in report.hash_results:
        _require(result["status"] in allowed_statuses,
                 f"hash result status must be one of {allowed_statuses}")
        _require(result["status"] != "verified", "status must never be 'verified' (overclaim)")
        _require(len(result["sha256"]) == 64, "sha256 must be 64 hex chars")

    canonical_prefix = ev._validate_canonical_prefix(auth["allowed_prefix"])
    for key in auth["allowed_keys"]:
        _require(ev._key_inside_prefix(key, canonical_prefix),
                 f"key must be inside approved prefix: {key}")
        _require(ev._is_safe_key(key), f"key must be safe: {key}")
    _require(len(auth["allowed_keys"]) == len(set(auth["allowed_keys"])),
             "allowlist must not contain duplicates")
    _require(len(auth["allowed_keys"]) <= auth["max_object_count"],
             "allowlist must not exceed count cap")
    _require(auth["max_object_count"] <= ev.ACCEPTED_MAX_OBJECT_COUNT,
             "max_object_count must not exceed accepted hard upper bound")
    _require(auth["max_object_bytes"] <= ev.ACCEPTED_MAX_MEDIA_OBJECT_BYTES,
             "max_object_bytes must not exceed accepted hard upper bound")
    _require(auth["max_total_bytes"] <= ev.ACCEPTED_MAX_AGGREGATE_BYTES,
             "max_total_bytes must not exceed accepted hard upper bound")
    for cap in ev.DENIED_CAPABILITY_FIELDS:
        _require(auth[cap] is False, f"denied capability must be false: {cap}")

    # Explicit role plan: key set exactly equals allowed_keys.
    _require(set(auth["object_role_by_key"]) == set(auth["allowed_keys"]),
             "object_role_by_key key set must equal allowed_keys")
    for required in ev.REQUIRED_UNIQUE_ROLES:
        count = sum(1 for r in auth["object_role_by_key"].values() if r == required)
        _require(count == 1, f"required role must appear exactly once: {required}")


def main() -> int:
    parser = argparse.ArgumentParser(description="PS-041E2-A B2 evidence readiness smoke")
    parser.add_argument("--check-only", action="store_true", default=True)
    parser.add_argument("--write-evidence", action="store_true")
    parser.add_argument("--no-frontend", action="store_true")
    args = parser.parse_args()
    if args.write_evidence:
        print(json.dumps({"ok": False, "error": "PS-041E2-A smoke does not own canonical evidence writes"}))
        return 1

    auth = _smoke_authorization()
    try:
        report = ev.run_dry_run(
            auth, fixture_path=FIXTURE,
            server_alias=SERVER_ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY,
        )
        _verify_readiness_contracts(report, auth)
    except (ev.AuthorizationError, ImportValidationError, AssertionError) as exc:
        print(json.dumps({
            "ok": False,
            "slice": SLICE,
            "mode": "fake-storage-readiness",
            "error": str(exc),
        }, sort_keys=True))
        return 1

    output = {
        "ok": True,
        "slice": SLICE,
        "mode": "fake-storage-readiness",
        "authorized_objects": report.authorized_objects,
        "head_calls_total": report.head_calls_total,
        "read_calls_total": report.read_calls_total,
        "unique_json_objects_read": report.unique_json_objects_read,
        "unique_media_objects_read": report.unique_media_objects_read,
        "snapshot_consumer_calls": report.snapshot_consumer_calls,
        "list_calls": report.list_calls,
        "write_attempts": report.write_attempts,
        "delete_attempts": report.delete_attempts,
        "signed_url_attempts": report.signed_url_attempts,
        "provider_calls": report.provider_calls,
        "total_bytes_read": report.total_bytes_read,
        "observation_stable": report.observation_stable,
        "observation_comparisons": report.observation_comparisons,
        "alias_comparison_code": report.alias_comparison_code,
        "bucket_comparison_code": report.bucket_comparison_code,
        "hash_result_statuses": sorted({r["status"] for r in report.hash_results}),
        "passport_schema": report.passport_schema,
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
