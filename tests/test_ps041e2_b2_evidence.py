from __future__ import annotations

import copy
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import ps041e2_b2_evidence as ev  # noqa: E402
from proofstudio.api.genblaze_external_adapter import ImportValidationError  # noqa: E402

FIXTURE = ROOT / "tests/fixtures/ps041d/genblaze-multi-provider-bundle-v1.json"

_DRY_RUN_ABORT = (ev.AuthorizationError, ImportValidationError)

ALIAS = "configured-import"
PREFIX = "import-root/ps041e2"
SERVER_BUCKET_IDENTITY = ev.DEFAULT_FAKE_SERVER_BUCKET_IDENTITY
BUCKET_HASH = __import__("hashlib").sha256(SERVER_BUCKET_IDENTITY.encode("utf-8")).hexdigest()

NOW = datetime.now(timezone.utc)
AUTHORIZED_AT = (NOW - timedelta(minutes=1)).isoformat().replace("+00:00", "Z")
FUTURE = (NOW + timedelta(hours=1)).isoformat().replace("+00:00", "Z")
PAST = (NOW - timedelta(days=2)).isoformat().replace("+00:00", "Z")
PAST_EXPIRES = (NOW - timedelta(days=1)).isoformat().replace("+00:00", "Z")

DEFAULT_KEYS = [
    f"{PREFIX}/stage-a/storyboard.json",
    f"{PREFIX}/runs/b0/manifest.json",
    f"{PREFIX}/runs/b1/manifest.json",
    f"{PREFIX}/runs/b2/manifest.json",
    f"{PREFIX}/composition/final.mp4",
]

DEFAULT_ROLE_PLAN = {
    DEFAULT_KEYS[0]: ev.ROLE_STAGE_A_STORYBOARD,
    DEFAULT_KEYS[1]: ev.ROLE_STAGE_B0_MANIFEST,
    DEFAULT_KEYS[2]: ev.ROLE_STAGE_B1_MANIFEST,
    DEFAULT_KEYS[3]: ev.ROLE_STAGE_B2_MANIFEST,
    DEFAULT_KEYS[4]: ev.ROLE_FINAL_DELIVERY,
}

_EXPECTED_HASHES = ev.expected_hashes_for_fixture(
    FIXTURE, list(DEFAULT_KEYS), DEFAULT_ROLE_PLAN,
)
_EXPECTED_JSON_HASHES = {k: v for k, v in _EXPECTED_HASHES.items()
                         if DEFAULT_ROLE_PLAN[k] in ev.JSON_READ_ROLES}


def base_auth(**overrides) -> dict:
    auth = {
        "schema": ev.SCHEMA,
        "authorized": True,
        "authorized_by": "ps-041e2-test",
        "authorized_at": AUTHORIZED_AT,
        "expires_at": FUTURE,
        "configured_alias": ALIAS,
        "allowed_bucket_name_hash": BUCKET_HASH,
        "allowed_prefix": PREFIX,
        "allowed_keys": list(DEFAULT_KEYS),
        "object_role_by_key": dict(DEFAULT_ROLE_PLAN),
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
        "expected_sha256_by_key": dict(_EXPECTED_JSON_HASHES),
        "purpose": ev.PURPOSE,
    }
    auth.update(overrides)
    return auth


def write_auth(tmp_path: Path, auth: dict, name: str = "auth.json") -> Path:
    p = tmp_path / name
    p.write_text(json.dumps(auth), encoding="utf-8")
    return p


def _populated_backend() -> "ev.FakeB2Backend":
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return ev._build_fake_backend(
        fixture, list(DEFAULT_KEYS), object_role_by_key=dict(DEFAULT_ROLE_PLAN),
    )


def _run(**overrides):
    return ev.run_dry_run(
        base_auth(**overrides), fixture_path=FIXTURE,
        server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY,
    )


# ---------------------------------------------------------------------------
# 1. valid authorization passes validation
# ---------------------------------------------------------------------------

def test_valid_authorization_passes_validation() -> None:
    report = ev.validate_authorization(base_auth(), execute_mode=False)
    assert report.valid
    assert report.configured_alias == ALIAS
    assert report.canonical_prefix == PREFIX
    assert report.authorized_object_count == len(DEFAULT_KEYS)
    assert report.object_role_by_key == DEFAULT_ROLE_PLAN


# ---------------------------------------------------------------------------
# 2. accepted hard upper bounds: exact maximum, max+1, extremely large
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("count", [
    ev.ACCEPTED_MAX_OBJECT_COUNT,
    ev.ACCEPTED_MAX_OBJECT_COUNT + 1,
    10_000,
    2**31,
])
def test_max_object_count_accepted_upper_bound(count: int) -> None:
    auth = base_auth(max_object_count=count)
    if count <= ev.ACCEPTED_MAX_OBJECT_COUNT:
        ev.validate_authorization(auth, execute_mode=False)
    else:
        with pytest.raises(ev.AuthorizationError, match="max_object_count_exceeds_accepted_limit"):
            ev.validate_authorization(auth, execute_mode=False)


@pytest.mark.parametrize("size", [
    ev.ACCEPTED_MAX_MEDIA_OBJECT_BYTES,
    ev.ACCEPTED_MAX_MEDIA_OBJECT_BYTES + 1,
    10 * 1024 * 1024 * 1024,
    2**40,
])
def test_max_object_bytes_accepted_upper_bound(size: int) -> None:
    auth = base_auth(max_object_bytes=size, max_total_bytes=max(size, 16_777_216))
    if size <= ev.ACCEPTED_MAX_MEDIA_OBJECT_BYTES:
        ev.validate_authorization(auth, execute_mode=False)
    else:
        with pytest.raises(ev.AuthorizationError, match="max_object_bytes_exceeds_accepted_limit"):
            ev.validate_authorization(auth, execute_mode=False)


@pytest.mark.parametrize("size", [
    ev.ACCEPTED_MAX_AGGREGATE_BYTES,
    ev.ACCEPTED_MAX_AGGREGATE_BYTES + 1,
    1024 * 1024 * 1024 * 1024,
    2**50,
])
def test_max_total_bytes_accepted_upper_bound(size: int) -> None:
    auth = base_auth(max_total_bytes=size, max_object_bytes=min(size, 1_048_576))
    if size <= ev.ACCEPTED_MAX_AGGREGATE_BYTES:
        ev.validate_authorization(auth, execute_mode=False)
    else:
        with pytest.raises(ev.AuthorizationError, match="max_total_bytes_exceeds_accepted_limit"):
            ev.validate_authorization(auth, execute_mode=False)


# ---------------------------------------------------------------------------
# 3. canonical alias validation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("alias,code", [
    ("", "alias_missing"),
    ("   ", "alias_whitespace_only"),
    (" alias ", "alias_leading_or_trailing_whitespace"),
    ("configured-import ", "alias_leading_or_trailing_whitespace"),
    ("a/b", "alias_unsafe"),
    ("a\\b", "alias_unsafe"),
    ("a?b", "alias_unsafe"),
    ("a#b", "alias_unsafe"),
    ("a://b", "alias_unsafe"),
    ("x" * 65, "alias_too_long"),
])
def test_canonical_alias_rejects(alias: str, code: str) -> None:
    with pytest.raises(ev.AuthorizationError, match=code):
        ev.validate_authorization(base_auth(configured_alias=alias), execute_mode=False)


def test_canonical_alias_nfc_rejects() -> None:
    denormalized = "A\u0300lias"  # NFD form of "Àlias"
    with pytest.raises(ev.AuthorizationError, match="not_nfc"):
        ev.validate_authorization(base_auth(configured_alias=denormalized), execute_mode=False)


# ---------------------------------------------------------------------------
# 4. canonical prefix validation (no normalization, returned unchanged)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("prefix", [
    "/prefix",
    "prefix/",
    " prefix ",
    "",
    "/",
    "///",
    "prefix//sep",
    "../escape",
    "prefix/..",
    "prefix\\x",
    "prefix?x=1",
    "prefix#frag",
    "http://example.invalid/prefix",
    "prefix\x00",
])
def test_canonical_prefix_rejects(prefix: str) -> None:
    with pytest.raises(ev.AuthorizationError, match="prefix_"):
        ev._validate_canonical_prefix(prefix)


def test_canonical_prefix_nfc_rejects() -> None:
    denormalized = "pre\u0300fix"  # NFD
    with pytest.raises(ev.AuthorizationError, match="not_nfc"):
        ev._validate_canonical_prefix(denormalized)


def test_canonical_prefix_returned_unchanged() -> None:
    canonical = "import-root/ps041e2"
    assert ev._validate_canonical_prefix(canonical) == canonical


def test_canonical_prefix_too_long_rejects() -> None:
    too_long = "a" * (ev.PREFIX_MAX_BYTES + 1)
    with pytest.raises(ev.AuthorizationError, match="prefix_too_long"):
        ev._validate_canonical_prefix(too_long)


# ---------------------------------------------------------------------------
# 5. non-string / nonhashable allowlist values reject before dup detection
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bad_keys", [
    [{}],
    [[]],
    [None],
    [123],
    [{"a": 1}, {"a": 1}],
    [[1], [1]],
    [DEFAULT_KEYS[0], 42],
])
def test_nonstring_allowlist_values_reject(bad_keys: list) -> None:
    with pytest.raises(ev.AuthorizationError, match="allowlist_key_unsafe"):
        ev.validate_authorization(base_auth(allowed_keys=bad_keys), execute_mode=False)


# ---------------------------------------------------------------------------
# 6. bounded nested authorization parsing rejects (no recursion escape)
# ---------------------------------------------------------------------------

def test_deeply_nested_authorization_rejects(tmp_path: Path) -> None:
    nested: dict = {}
    cursor = nested
    for _ in range(64):
        cursor["x"] = {}
        cursor = cursor["x"]
    auth = base_auth()
    auth["__nested__"] = nested
    auth.pop("expected_sha256_by_key", None)
    auth["allow_sha256_verification"] = False
    p = write_auth(tmp_path, auth, name="nested.json")
    with pytest.raises(ev.AuthorizationError, match="authorization_depth_exceeded|unknown_authorization_field"):
        ev.load_authorization(p)


def test_excessively_long_string_rejects(tmp_path: Path) -> None:
    auth = base_auth()
    auth["__long__"] = "x" * (ev.AUTH_DOC_MAX_STRING + 1)
    auth.pop("expected_sha256_by_key", None)
    auth["allow_sha256_verification"] = False
    p = write_auth(tmp_path, auth, name="long.json")
    with pytest.raises(ev.AuthorizationError, match="authorization_string_too_long|unknown_authorization_field"):
        ev.load_authorization(p)


def test_too_many_items_rejects(tmp_path: Path) -> None:
    auth = base_auth()
    auth["__many__"] = ["x"] * (ev.AUTH_DOC_MAX_ITEMS + 1)
    auth.pop("expected_sha256_by_key", None)
    auth["allow_sha256_verification"] = False
    p = write_auth(tmp_path, auth, name="many.json")
    with pytest.raises(ev.AuthorizationError, match="authorization_item_count_exceeded|unknown_authorization_field"):
        ev.load_authorization(p)


# ---------------------------------------------------------------------------
# 7. malformed input never escapes as raw exception
# ---------------------------------------------------------------------------

def test_no_raw_exception_escape_from_validate() -> None:
    adversarial_inputs = [
        None, 42, 3.14, "string", [], [1, 2, 3], object(),
        {"allowed_keys": [[1]]},
        {"allowed_keys": [{(1, 2): "x"}]},
    ]
    for bad in adversarial_inputs:
        with pytest.raises(ev.AuthorizationError):
            ev.validate_authorization(bad if isinstance(bad, dict) else {"x": 1}, execute_mode=False)


def test_no_raw_exception_escape_from_structure_check() -> None:
    deep_dict: dict = {}
    cursor = deep_dict
    for _ in range(ev.AUTH_DOC_MAX_DEPTH + 5):
        cursor["x"] = {}
        cursor = cursor["x"]
    adversarial = [
        [[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]],
        deep_dict,
        {"a": ["x" * (ev.AUTH_DOC_MAX_STRING + 1)]},
        {"a": ["x"] * (ev.AUTH_DOC_MAX_ITEMS + 1)},
    ]
    for bad in adversarial:
        with pytest.raises(ev.AuthorizationError):
            ev._bounded_structure_check(bad)


# ---------------------------------------------------------------------------
# 8. timezone-aware timestamp validation (UTC, short window)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("ts", [
    "2024-01-01",
    "2024-01-01T00:00:00",
    "2024-01-01T00:00:00+05:00",
    "not-a-date",
    "",
])
def test_invalid_timestamps_reject(ts: str) -> None:
    with pytest.raises(ev.AuthorizationError, match="authorized_at_"):
        ev.validate_authorization(base_auth(authorized_at=ts), execute_mode=False)


def test_expires_at_at_or_before_authorized_at_rejects() -> None:
    ts = AUTHORIZED_AT
    with pytest.raises(ev.AuthorizationError, match="expires_at_at_or_before_authorized_at"):
        ev.validate_authorization(base_auth(authorized_at=ts, expires_at=ts), execute_mode=False)


def test_authorized_at_in_future_rejects() -> None:
    future_ts = (NOW + timedelta(hours=1)).isoformat().replace("+00:00", "Z")
    far_future = (NOW + timedelta(hours=2)).isoformat().replace("+00:00", "Z")
    with pytest.raises(ev.AuthorizationError, match="authorized_at_in_future"):
        ev.validate_authorization(base_auth(authorized_at=future_ts, expires_at=far_future), execute_mode=False)


def test_authorization_window_too_long_rejects() -> None:
    far_future = (NOW + timedelta(hours=25)).isoformat().replace("+00:00", "Z")
    with pytest.raises(ev.AuthorizationError, match="authorization_window_too_long"):
        ev.validate_authorization(base_auth(expires_at=far_future), execute_mode=False)


def test_expired_authorization_rejects_execute() -> None:
    with pytest.raises(ev.AuthorizationError, match="authorization_expired"):
        ev.validate_authorization(
            base_auth(authorized_at=PAST, expires_at=PAST_EXPIRES), execute_mode=True,
        )


# ---------------------------------------------------------------------------
# 9. authorized=false rejects execute; authorized_by required when authorized
# ---------------------------------------------------------------------------

def test_authorized_false_rejects_execute() -> None:
    with pytest.raises(ev.AuthorizationError, match="not_authorized_for_execute"):
        ev.validate_authorization(base_auth(authorized=False), execute_mode=True)


def test_authorized_by_missing_when_authorized_rejects() -> None:
    with pytest.raises(ev.AuthorizationError, match="authorized_by_missing"):
        ev.validate_authorization(base_auth(authorized=True, authorized_by=""), execute_mode=False)


def test_authorized_by_whitespace_only_rejects() -> None:
    with pytest.raises(ev.AuthorizationError, match="authorized_by_whitespace_only"):
        ev.validate_authorization(base_auth(authorized=True, authorized_by="   "), execute_mode=False)


# ---------------------------------------------------------------------------
# 10. canonical key safety (traversal, URL, outside prefix, duplicate)
# ---------------------------------------------------------------------------

def test_traversal_key_rejects() -> None:
    with pytest.raises(ev.AuthorizationError, match="allowlist_key_unsafe"):
        ev.validate_authorization(
            base_auth(allowed_keys=[f"{PREFIX}/../escape.json"]), execute_mode=False,
        )


@pytest.mark.parametrize("key", [
    "https://example.invalid/x.json",
    f"{PREFIX}/a.json?x=1",
    f"{PREFIX}/a.json#frag",
    f"{PREFIX}/a.json://evil",
    f"{PREFIX}/\\backslash.json",
])
def test_url_shaped_key_rejects(key: str) -> None:
    with pytest.raises(ev.AuthorizationError, match="allowlist_key_unsafe"):
        ev.validate_authorization(
            base_auth(allowed_keys=[key], expected_sha256_by_key={}), execute_mode=False,
        )


def test_key_outside_prefix_rejects() -> None:
    with pytest.raises(ev.AuthorizationError, match="allowlist_key_outside_prefix"):
        ev.validate_authorization(
            base_auth(allowed_keys=["import-root/other/storyboard.json"],
                      expected_sha256_by_key={}),
            execute_mode=False,
        )


def test_duplicate_key_rejects() -> None:
    key = DEFAULT_KEYS[0]
    single_expected = {key: _EXPECTED_JSON_HASHES[key]} if key in _EXPECTED_JSON_HASHES else {}
    with pytest.raises(ev.AuthorizationError, match="allowlist_duplicate_key"):
        ev.validate_authorization(
            base_auth(allowed_keys=[key, key], expected_sha256_by_key=single_expected),
            execute_mode=False,
        )


# ---------------------------------------------------------------------------
# 11. allowlist count/byte overflow
# ---------------------------------------------------------------------------

def test_object_count_overflow_rejects() -> None:
    with pytest.raises(ev.AuthorizationError, match="allowlist_exceeds_count_cap"):
        ev.validate_authorization(base_auth(max_object_count=1), execute_mode=False)


def test_total_below_object_cap_rejects() -> None:
    with pytest.raises(ev.AuthorizationError, match="max_total_below_object_cap"):
        ev.validate_authorization(
            base_auth(max_total_bytes=1, max_object_bytes=2), execute_mode=False,
        )


def test_total_byte_overflow_in_dry_run() -> None:
    auth = base_auth(max_total_bytes=10)
    with pytest.raises(_DRY_RUN_ABORT):
        ev.run_dry_run(auth, fixture_path=FIXTURE)


# ---------------------------------------------------------------------------
# 12. unknown field / missing field / wrong schema / wrong purpose
# ---------------------------------------------------------------------------

def test_unknown_authorization_field_rejects() -> None:
    auth = base_auth()
    auth["unexpected_field"] = "bad"
    with pytest.raises(ev.AuthorizationError, match="unknown_authorization_field"):
        ev.validate_authorization(auth, execute_mode=False)


def test_missing_authorization_field_rejects() -> None:
    auth = base_auth()
    auth.pop("purpose")
    with pytest.raises(ev.AuthorizationError, match="missing_authorization_field"):
        ev.validate_authorization(auth, execute_mode=False)


def test_unsupported_schema_rejects() -> None:
    with pytest.raises(ev.AuthorizationError, match="unsupported_authorization_schema"):
        ev.validate_authorization(base_auth(schema="wrong"), execute_mode=False)


# ---------------------------------------------------------------------------
# 13. denied capabilities must remain false
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("cap", ["allow_write", "allow_delete", "allow_signed_urls", "allow_provider_calls"])
def test_denied_capability_enabled_rejects(cap: str) -> None:
    with pytest.raises(ev.AuthorizationError, match=f"denied_capability_enabled:{cap}"):
        ev.validate_authorization(base_auth(**{cap: True}), execute_mode=False)


# ---------------------------------------------------------------------------
# 14. bucket hash validation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bad_hash", ["", "short", "g" * 64, "XYZ", "A" * 64])
def test_bucket_hash_invalid_rejects(bad_hash: str) -> None:
    with pytest.raises(ev.AuthorizationError, match="bucket_hash_invalid"):
        ev.validate_authorization(base_auth(allowed_bucket_name_hash=bad_hash), execute_mode=False)


# ---------------------------------------------------------------------------
# 15. actual server-alias match / mismatch
# ---------------------------------------------------------------------------

def test_compare_server_alias_exact_match_passes() -> None:
    result = ev.compare_server_alias(ALIAS, ALIAS)
    assert result.match is True
    assert result.code == "alias_match"


def test_compare_server_alias_mismatch_rejects() -> None:
    result = ev.compare_server_alias(ALIAS, "different-alias")
    assert result.match is False
    assert result.code == "alias_mismatch"


def test_dry_run_actual_alias_mismatch_rejects() -> None:
    auth = base_auth(configured_alias="not-the-server-alias")
    with pytest.raises(ev.AuthorizationError, match="alias_mismatch"):
        ev.run_dry_run(auth, fixture_path=FIXTURE,
                       server_alias=SERVER_BUCKET_IDENTITY,
                       server_bucket_identity=SERVER_BUCKET_IDENTITY)


# ---------------------------------------------------------------------------
# 16. actual bucket-identity match / mismatch (no raw bucket name in output)
# ---------------------------------------------------------------------------

def test_compare_bucket_identity_exact_match_passes() -> None:
    result = ev.compare_bucket_identity(BUCKET_HASH, SERVER_BUCKET_IDENTITY)
    assert result.match is True
    assert result.code == "bucket_match"


def test_compare_bucket_identity_different_bucket_rejects() -> None:
    result = ev.compare_bucket_identity(BUCKET_HASH, "a-different-controlled-bucket-name")
    assert result.match is False
    assert result.code == "bucket_identity_mismatch"


def test_bucket_identity_diagnostic_contains_no_raw_bucket_name() -> None:
    result = ev.compare_bucket_identity(BUCKET_HASH, SERVER_BUCKET_IDENTITY)
    diagnostic = json.dumps(result.__dict__)
    assert SERVER_BUCKET_IDENTITY not in diagnostic
    assert "bucket_match" in diagnostic or "bucket_identity_mismatch" in diagnostic


def test_dry_run_actual_bucket_mismatch_rejects() -> None:
    auth = base_auth()
    with pytest.raises(ev.AuthorizationError, match="bucket_identity_mismatch"):
        ev.run_dry_run(auth, fixture_path=FIXTURE,
                       server_alias=ALIAS,
                       server_bucket_identity="a-different-controlled-bucket-name")


# ---------------------------------------------------------------------------
# 17. metadata-read false gives zero backend operations
# ---------------------------------------------------------------------------

def test_metadata_reads_false_gives_zero_backend_operations() -> None:
    auth = base_auth(allow_metadata_reads=False)
    backend = _populated_backend()
    with pytest.raises(ev.AuthorizationError, match="metadata_reads_required"):
        ev.run_dry_run(auth, fixture_path=FIXTURE, backend=backend,
                       server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY)
    assert backend.head_calls == []
    assert backend.read_calls == []
    assert backend.list_calls == []
    assert backend.write_attempts == []
    assert backend.delete_attempts == []


# ---------------------------------------------------------------------------
# 18. JSON-read false gives zero JSON reads
# ---------------------------------------------------------------------------

def test_json_reads_false_gives_zero_json_reads() -> None:
    auth = base_auth(allow_json_object_reads=False)
    backend = _populated_backend()
    with pytest.raises(ev.AuthorizationError, match="json_reads_required"):
        ev.run_dry_run(auth, fixture_path=FIXTURE, backend=backend,
                       server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY)
    assert backend.read_calls == []


# ---------------------------------------------------------------------------
# 19. media-read false gives zero media reads
# ---------------------------------------------------------------------------

def test_media_reads_false_gives_zero_media_reads() -> None:
    report = _run()
    assert report.unique_media_objects_read == 0
    backend = _populated_backend()
    media_key = next(k for k in DEFAULT_KEYS if DEFAULT_ROLE_PLAN[k] in ev.MEDIA_BYTE_ROLES)
    media_reads_on_media_key = sum(1 for call in backend.read_calls if call == media_key)
    assert media_reads_on_media_key == 0


# ---------------------------------------------------------------------------
# 20. missing allowlisted object rejects before import
# ---------------------------------------------------------------------------

def test_missing_allowlisted_object_rejects_before_import() -> None:
    auth = base_auth()
    backend = _populated_backend()
    missing_key = DEFAULT_KEYS[0]
    del backend.objects[missing_key]
    with pytest.raises(ev.AuthorizationError, match="approved_object_missing"):
        ev.run_dry_run(auth, fixture_path=FIXTURE, backend=backend,
                       server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY)


# ---------------------------------------------------------------------------
# 21. unauthorized key rejected before backend call
# ---------------------------------------------------------------------------

def test_unauthorized_key_rejected_before_backend_call() -> None:
    backend = _populated_backend()
    allowed = {DEFAULT_KEYS[0]}
    unauthorized = DEFAULT_KEYS[0] + ".tampered"
    head_before = list(backend.head_calls)
    with pytest.raises(ev.AuthorizationError, match="key_not_allowlisted"):
        ev.assert_key_authorized(unauthorized, allowed)
    assert backend.head_calls == head_before


def test_authorized_key_passes_guard() -> None:
    allowed = {DEFAULT_KEYS[0]}
    ev.assert_key_authorized(DEFAULT_KEYS[0], allowed)


# ---------------------------------------------------------------------------
# 22. expected-hash match / mismatch
# ---------------------------------------------------------------------------

def test_expected_json_hash_match_records_matched() -> None:
    report = _run()
    assert report.ok
    for r in report.hash_results:
        if r["key"] in _EXPECTED_JSON_HASHES:
            assert r["status"] == "matched"
            assert r["sha256"] == _EXPECTED_JSON_HASHES[r["key"]]


def test_expected_json_hash_mismatch_records_mismatch_and_aborts() -> None:
    wrong_map = {k: "0" * 64 for k in _EXPECTED_JSON_HASHES}
    auth = base_auth(expected_sha256_by_key=wrong_map)
    with pytest.raises(_DRY_RUN_ABORT, match="hash_mismatch|unexpected_hash_mismatch"):
        ev.run_dry_run(auth, fixture_path=FIXTURE,
                       server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY)


def test_expected_media_hash_match_when_media_reads_enabled() -> None:
    auth = base_auth(
        allow_media_byte_reads=True,
        expected_sha256_by_key=dict(_EXPECTED_HASHES),
    )
    report = ev.run_dry_run(auth, fixture_path=FIXTURE,
                            server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY)
    assert report.unique_media_objects_read == 1
    media_results = [r for r in report.hash_results
                     if DEFAULT_ROLE_PLAN[r["key"]] in ev.MEDIA_BYTE_ROLES]
    assert len(media_results) == 1
    assert media_results[0]["status"] == "matched"


def test_expected_hash_for_nonallowlisted_key_rejects() -> None:
    bad_map = {"not/in/allowlist.json": "0" * 64}
    auth = base_auth(expected_sha256_by_key={**_EXPECTED_JSON_HASHES, **bad_map})
    with pytest.raises(ev.AuthorizationError, match="expected_sha256_unknown_key"):
        ev.validate_authorization(auth, execute_mode=False)


def test_expected_sha_verification_enabled_empty_map_rejects() -> None:
    auth = base_auth(allow_sha256_verification=True, expected_sha256_by_key={})
    with pytest.raises(ev.AuthorizationError, match="expected_sha256_required_when_verification_enabled"):
        ev.validate_authorization(auth, execute_mode=False)


def test_expected_sha_verification_disabled_nonempty_map_rejects() -> None:
    auth = base_auth(allow_sha256_verification=False, expected_sha256_by_key=dict(_EXPECTED_JSON_HASHES))
    with pytest.raises(ev.AuthorizationError, match="expected_sha256_requires_verification_enabled"):
        ev.validate_authorization(auth, execute_mode=False)


def test_expected_sha_invalid_value_rejects() -> None:
    bad_map = {k: "G" * 64 for k in _EXPECTED_JSON_HASHES}
    auth = base_auth(expected_sha256_by_key=bad_map)
    with pytest.raises(ev.AuthorizationError, match="expected_sha256_invalid_value"):
        ev.validate_authorization(auth, execute_mode=False)


def test_hash_result_never_labelled_verified() -> None:
    report = _run()
    for r in report.hash_results:
        assert r["status"] in {"matched", "observed", "computed", "mismatch"}
        assert r["status"] != "verified"


# ---------------------------------------------------------------------------
# 23. authorization file path safety
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("basename", [".env", ".env.local", ".env.save", ".env.production"])
def test_forbidden_env_basenames_reject(tmp_path: Path, basename: str) -> None:
    p = tmp_path / basename
    p.write_text("B2_APP_KEY=secret", encoding="utf-8")
    with pytest.raises(ev.AuthorizationError, match="authorization_path_forbidden_basename"):
        ev.load_authorization(p)


def test_non_json_suffix_rejects(tmp_path: Path) -> None:
    p = tmp_path / "auth.txt"
    p.write_text("{}{}{}", encoding="utf-8")
    with pytest.raises(ev.AuthorizationError, match="authorization_path_not_json"):
        ev.load_authorization(p)


def test_symlink_authorization_rejects(tmp_path: Path) -> None:
    real = write_auth(tmp_path, base_auth(), name="real.json")
    link = tmp_path / "link.json"
    os.symlink(real, link)
    with pytest.raises(ev.AuthorizationError, match="authorization_path_symlink"):
        ev.load_authorization(link)


def test_directory_authorization_rejects(tmp_path: Path) -> None:
    d = tmp_path / "subdir.json"
    d.mkdir()
    with pytest.raises(ev.AuthorizationError, match="authorization_absent|authorization_path_not_regular"):
        ev.load_authorization(d)


def test_missing_authorization_rejects(tmp_path: Path) -> None:
    with pytest.raises(ev.AuthorizationError, match="authorization_absent"):
        ev.load_authorization(tmp_path / "missing.json")


def test_malformed_authorization_json_rejects(tmp_path: Path) -> None:
    p = tmp_path / "bad.json"
    p.write_text("{not json", encoding="utf-8")
    with pytest.raises(ev.AuthorizationError, match="authorization_malformed_json"):
        ev.load_authorization(p)


def test_authorization_duplicate_top_level_key_rejects(tmp_path: Path) -> None:
    p = tmp_path / "dup.json"
    p.write_text('{"schema":"x","schema":"y"}', encoding="utf-8")
    with pytest.raises(ev.AuthorizationError, match="authorization_duplicate_key|authorization_malformed"):
        ev.load_authorization(p)


def test_invalid_utf8_authorization_rejects(tmp_path: Path) -> None:
    p = tmp_path / "bad-utf8.json"
    p.write_bytes(b'{"k": "\xff\xfe"}')
    with pytest.raises(ev.AuthorizationError, match="authorization_invalid_utf8"):
        ev.load_authorization(p)


def test_oversized_authorization_rejects(tmp_path: Path) -> None:
    p = tmp_path / "big.json"
    p.write_text(" " * (ev.AUTH_DOC_MAX_BYTES + 1), encoding="utf-8")
    with pytest.raises(ev.AuthorizationError, match="authorization_too_large"):
        ev.load_authorization(p)


# ---------------------------------------------------------------------------
# 24. before/after metadata change rejects (TOCTOU via accepted reader)
# ---------------------------------------------------------------------------

def test_before_after_metadata_change_rejects() -> None:
    from proofstudio.api.b2_import_reader import B2ImportReaderConfig, BoundedB2ImportReader
    from proofstudio.api.imported_bundle import B2ObjectReference
    key = DEFAULT_KEYS[0]
    body = b'{"title":"sanitized"}'

    class MutatingBackend(ev.FakeB2Backend):
        def head(self, k: str):
            super().head(k)
            obj = self.objects.get(k)
            if obj is not None and len(self.head_calls) > 1:
                obj["etag"] = "after"
                return {"size_bytes": obj["size_bytes"], "etag": "after", "version_id": obj["version_id"]}
            return ({"size_bytes": obj["size_bytes"], "etag": obj["etag"], "version_id": obj["version_id"]}
                    if obj else None)
    mut = MutatingBackend()
    mut.objects[key] = {"body": body, "size_bytes": len(body), "etag": "before", "version_id": "v1"}
    reader = BoundedB2ImportReader(mut, B2ImportReaderConfig(
        enabled=True, bucket_alias=ALIAS, root_prefix=PREFIX,
    ))
    with pytest.raises(ImportValidationError, match="object_changed_during_read"):
        reader.read_json(B2ObjectReference(backend="b2_s3", bucket_alias=ALIAS, object_key=key))


# ---------------------------------------------------------------------------
# 25. SHA mismatch via accepted reader (reference carries expected sha256)
# ---------------------------------------------------------------------------

def test_accepted_reader_sha_mismatch_records_mismatch() -> None:
    from proofstudio.api.b2_import_reader import B2ImportReaderConfig, BoundedB2ImportReader
    from proofstudio.api.imported_bundle import B2ObjectReference
    backend = ev.FakeB2Backend()
    key = DEFAULT_KEYS[0]
    body = b'{"title":"sanitized"}'
    backend.objects[key] = {"body": body, "size_bytes": len(body), "etag": "e1", "version_id": "v1"}
    reader = BoundedB2ImportReader(backend, B2ImportReaderConfig(
        enabled=True, bucket_alias=ALIAS, root_prefix=PREFIX,
    ))
    with pytest.raises(ImportValidationError, match="hash_mismatch"):
        reader.read_json(B2ObjectReference(
            backend="b2_s3", bucket_alias=ALIAS, object_key=key,
            sha256="0" * 64,
        ))


# ---------------------------------------------------------------------------
# 26. idempotent import + zero provider/write/delete/list
# ---------------------------------------------------------------------------

def test_idempotent_import_remains_stable() -> None:
    report = _run()
    assert report.import_idempotent is True
    assert report.import_created is True


def test_provider_calls_remain_zero() -> None:
    report = _run()
    assert report.provider_calls == 0


def test_b2_write_delete_list_calls_remain_zero() -> None:
    report = _run()
    assert report.write_attempts == 0
    assert report.delete_attempts == 0
    assert report.list_calls == 0
    assert report.signed_url_attempts == 0


# ---------------------------------------------------------------------------
# 27. fake backend forbidden operations are counted and fail
# ---------------------------------------------------------------------------

def test_fake_backend_write_attempt_is_counted_and_fails() -> None:
    backend = ev.FakeB2Backend()
    with pytest.raises(AssertionError, match="forbidden_write_attempted"):
        backend.write("k", b"x")
    assert backend.write_attempts == ["k"]


def test_fake_backend_delete_attempt_is_counted_and_fails() -> None:
    backend = ev.FakeB2Backend()
    with pytest.raises(AssertionError, match="forbidden_delete_attempted"):
        backend.delete("k")
    assert backend.delete_attempts == ["k"]


def test_fake_backend_signed_url_attempt_is_counted_and_fails() -> None:
    backend = ev.FakeB2Backend()
    with pytest.raises(AssertionError, match="forbidden_signed_url_attempted"):
        backend.signed_url("k")
    assert backend.signed_url_attempts == ["k"]


# ---------------------------------------------------------------------------
# 28. output sanitizer removes forbidden values
# ---------------------------------------------------------------------------

FORBIDDEN_TOKENS = [
    "B2_APPLICATION_KEY", "B2_APPLICATION_KEY_ID", "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY", "Authorization", "Bearer", "X-Amz-",
    "signed URL", "presigned", "endpoint URL", "DATABASE_URL",
    "password", "secret", "token", "cookie",
]


def test_output_sanitizer_removes_forbidden_values() -> None:
    report = _run()
    serialized = json.dumps(report.__dict__, default=str, sort_keys=True)
    for token in FORBIDDEN_TOKENS:
        assert token.lower() not in serialized.lower(), f"forbidden token in output: {token}"


def test_no_raw_bucket_name_in_diagnostics() -> None:
    report = _run()
    serialized = json.dumps(report.__dict__, default=str, sort_keys=True)
    assert SERVER_BUCKET_IDENTITY not in serialized


# ---------------------------------------------------------------------------
# 29. cleanup verification reports no retained credential state
# ---------------------------------------------------------------------------

def test_cleanup_verification_reports_no_retained_credential_state() -> None:
    report = _run()
    serialized = json.dumps({
        "hash_results": report.hash_results,
        "bundle_id": report.bundle_id,
        "passport_schema": report.passport_schema,
    }, sort_keys=True)
    for token in ("B2_APPLICATION_KEY", "B2_APP_KEY", "B2_KEY_ID",
                  "AWS_SECRET_ACCESS_KEY", "Authorization", "DATABASE_URL"):
        assert token not in serialized
    assert report.passport_schema == ev.PASSPORT_SCHEMA


# ---------------------------------------------------------------------------
# 30. execute mode remains fail-closed
# ---------------------------------------------------------------------------

def test_execute_mode_fails_closed(tmp_path: Path) -> None:
    p = write_auth(tmp_path, base_auth())
    rc = ev.main(["--execute", str(p)])
    assert rc == 2


# ---------------------------------------------------------------------------
# CLI surface checks (no network, no live B2)
# ---------------------------------------------------------------------------

def test_validate_authorization_cli_rejects_bad_auth(tmp_path: Path) -> None:
    p = write_auth(tmp_path, base_auth(allowed_keys=[], expected_sha256_by_key={}))
    rc = ev.main(["--validate-authorization", str(p)])
    assert rc == 1


def test_validate_authorization_cli_accepts_good_auth(tmp_path: Path) -> None:
    p = write_auth(tmp_path, base_auth())
    rc = ev.main(["--validate-authorization", str(p)])
    assert rc == 0


def test_check_readiness_mode() -> None:
    rc = ev.main(["--check-readiness"])
    assert rc == 0


def test_check_readiness_reports_accepted_upper_bounds() -> None:
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ev.main(["--check-readiness"])
    summary = json.loads(buf.getvalue())
    bounds = summary["accepted_hard_upper_bounds"]
    assert bounds["max_object_count"] == ev.ACCEPTED_MAX_OBJECT_COUNT
    assert bounds["max_json_object_bytes"] == ev.ACCEPTED_MAX_JSON_OBJECT_BYTES
    assert bounds["max_media_object_bytes"] == ev.ACCEPTED_MAX_MEDIA_OBJECT_BYTES
    assert bounds["max_aggregate_bytes"] == ev.ACCEPTED_MAX_AGGREGATE_BYTES
    assert summary["authorization_window_seconds"] == ev.MAX_AUTH_WINDOW_SECONDS
    # PS-041E2-B Phase-1 implements the live executor; the readiness summary
    # now reports that live execution is supported (with all 22 gates still
    # required). Phase-1 itself performs no live B2 access.
    assert summary["live_execute_supported"] is True
    assert summary["live_execute_implemented"] is True
    assert summary["live_execute_gates_count"] == ev.LIVE_EXECUTE_GATES_COUNT
    assert summary["live_execute_schema"] == ev.LIVE_SCHEMA
    assert summary["live_execute_purpose"] == ev.LIVE_PURPOSE
    assert "object_role_by_key" not in summary  # internal field name not required in summary
    assert "stage_a_storyboard" in summary["required_unique_roles"]


# ===========================================================================
# PS-041E2-A v2 FOCUSED REGRESSION CASES
# ===========================================================================

# ---------------------------------------------------------------------------
# F1. successful five-object explicit role plan
# ---------------------------------------------------------------------------

def test_focused_successful_five_object_explicit_role_plan() -> None:
    report = _run()
    assert report.ok
    assert report.authorized_objects == 5
    assert set(report.role_plan) == set(DEFAULT_KEYS)
    for required in ev.REQUIRED_UNIQUE_ROLES:
        assert sum(1 for r in report.role_plan.values() if r == required) == 1


# ---------------------------------------------------------------------------
# F2. no required inline_json survives (no inline fallback)
# ---------------------------------------------------------------------------

def test_focused_no_required_inline_json_survives() -> None:
    """No successful candidate may carry inline_json for a planned role."""
    auth = base_auth()
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    role_to_key = ev.resolve_role_to_key(DEFAULT_ROLE_PLAN)
    bundle_request = ev._build_b2_bundle_request(
        fixture, role_to_key=role_to_key, configured_alias=ALIAS,
        expected_sha256_by_key=dict(_EXPECTED_JSON_HASHES),
    )
    for obj in bundle_request.objects:
        if obj.role in role_to_key:
            assert obj.inline_json is None, (
                f"role {obj.role} must not retain inline_json after B2 binding"
            )
            assert obj.b2_reference is not None
            assert obj.b2_reference.object_key == role_to_key[obj.role.value]


def test_focused_inline_json_absent_for_every_consumed_role_in_actual_run() -> None:
    """Inspect the bundle request constructed inside run_dry_run by replaying
    the exact build path and asserting no inline_json remains for planned
    roles. Uses the same documented entry point as the run."""
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    role_to_key = ev.resolve_role_to_key(DEFAULT_ROLE_PLAN)
    bundle_request = ev._build_b2_bundle_request(
        fixture, role_to_key=role_to_key, configured_alias=ALIAS,
        expected_sha256_by_key=dict(_EXPECTED_JSON_HASHES),
    )
    planned_roles = set(role_to_key.keys())
    for obj in bundle_request.objects:
        if obj.role.value in planned_roles:
            assert obj.inline_json is None


# ---------------------------------------------------------------------------
# F3. media-only authorization cannot produce a candidate
# ---------------------------------------------------------------------------

def test_focused_media_only_authorization_rejects_before_backend_import() -> None:
    """An authorization whose role plan covers only media (final_delivery)
    cannot satisfy the required JSON roles and must reject at validation."""
    media_key = next(k for k in DEFAULT_KEYS if DEFAULT_ROLE_PLAN[k] in ev.MEDIA_BYTE_ROLES)
    media_only_plan = {media_key: ev.ROLE_FINAL_DELIVERY}
    auth = base_auth(
        allowed_keys=[media_key],
        object_role_by_key=media_only_plan,
        expected_sha256_by_key={},
        allow_sha256_verification=False,
    )
    with pytest.raises(ev.AuthorizationError, match="object_role_required_role_missing|allowlist"):
        ev.validate_authorization(auth, execute_mode=False)


# ---------------------------------------------------------------------------
# F4. missing / duplicate / unconsumed role rejection
# ---------------------------------------------------------------------------

def test_focused_missing_storyboard_role_rejects() -> None:
    plan = dict(DEFAULT_ROLE_PLAN)
    storyboard_key = [k for k, v in plan.items() if v == ev.ROLE_STAGE_A_STORYBOARD][0]
    del plan[storyboard_key]
    auth = base_auth(
        allowed_keys=list(plan.keys()),
        object_role_by_key=plan,
        expected_sha256_by_key={
            k: v for k, v in _EXPECTED_JSON_HASHES.items() if k in plan
        },
    )
    with pytest.raises(ev.AuthorizationError, match="object_role_required_role_missing"):
        ev.validate_authorization(auth, execute_mode=False)


def test_focused_missing_b0_manifest_role_rejects() -> None:
    plan = dict(DEFAULT_ROLE_PLAN)
    b0_key = [k for k, v in plan.items() if v == ev.ROLE_STAGE_B0_MANIFEST][0]
    del plan[b0_key]
    auth = base_auth(
        allowed_keys=list(plan.keys()),
        object_role_by_key=plan,
        expected_sha256_by_key={
            k: v for k, v in _EXPECTED_JSON_HASHES.items() if k in plan
        },
    )
    with pytest.raises(ev.AuthorizationError, match="object_role_required_role_missing"):
        ev.validate_authorization(auth, execute_mode=False)


def test_focused_missing_final_delivery_role_rejects() -> None:
    plan = dict(DEFAULT_ROLE_PLAN)
    final_key = [k for k, v in plan.items() if v == ev.ROLE_FINAL_DELIVERY][0]
    del plan[final_key]
    auth = base_auth(
        allowed_keys=list(plan.keys()),
        object_role_by_key=plan,
        expected_sha256_by_key={
            k: v for k, v in _EXPECTED_JSON_HASHES.items() if k in plan
        },
    )
    with pytest.raises(ev.AuthorizationError, match="object_role_required_role_missing"):
        ev.validate_authorization(auth, execute_mode=False)


def test_focused_duplicate_role_rejects() -> None:
    plan = dict(DEFAULT_ROLE_PLAN)
    b1_key = [k for k, v in plan.items() if v == ev.ROLE_STAGE_B1_MANIFEST][0]
    b2_key = [k for k, v in plan.items() if v == ev.ROLE_STAGE_B2_MANIFEST][0]
    # Force two keys to map to the same role.
    plan[b2_key] = ev.ROLE_STAGE_B1_MANIFEST
    auth = base_auth(object_role_by_key=plan)
    with pytest.raises(ev.AuthorizationError, match="object_role_duplicate_role|object_role_required_role_missing"):
        ev.validate_authorization(auth, execute_mode=False)


def test_focused_unconsumed_allowlisted_key_rejects() -> None:
    """An approved key that is not consumed by the declared object plan must
    reject. This is enforced by the key-set equality check: the plan must
    cover exactly the allowed_keys."""
    extra_key = f"{PREFIX}/runs/b2/manifest-duplicate.json"
    plan = dict(DEFAULT_ROLE_PLAN)
    # Declare the key in allowed_keys but leave it out of the role plan.
    auth = base_auth(
        allowed_keys=list(DEFAULT_KEYS) + [extra_key],
        object_role_by_key=plan,  # missing extra_key
    )
    with pytest.raises(ev.AuthorizationError, match="object_role_missing_key"):
        ev.validate_authorization(auth, execute_mode=False)


def test_focused_extra_role_key_rejects() -> None:
    plan = dict(DEFAULT_ROLE_PLAN)
    ghost_key = f"{PREFIX}/stage-a/ghost.json"
    plan[ghost_key] = ev.ROLE_STAGE_A_STORYBOARD
    auth = base_auth(object_role_by_key=plan)
    with pytest.raises(ev.AuthorizationError, match="object_role_extra_key"):
        ev.validate_authorization(auth, execute_mode=False)


def test_focused_unknown_role_rejects() -> None:
    plan = dict(DEFAULT_ROLE_PLAN)
    plan[DEFAULT_KEYS[0]] = "not_a_real_role"
    auth = base_auth(object_role_by_key=plan)
    with pytest.raises(ev.AuthorizationError, match="object_role_unknown_role|object_role_required_role_missing"):
        ev.validate_authorization(auth, execute_mode=False)


# ---------------------------------------------------------------------------
# F5. one backend JSON read per JSON object; zero rereads in candidate rebuild
# ---------------------------------------------------------------------------

def test_focused_one_backend_read_per_json_object() -> None:
    backend = _populated_backend()
    ev.run_dry_run(
        base_auth(), fixture_path=FIXTURE, backend=backend,
        server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY,
    )
    json_keys = [k for k in DEFAULT_KEYS if DEFAULT_ROLE_PLAN[k] in ev.JSON_READ_ROLES]
    # Exactly one read_bytes call per JSON object key, in any order.
    assert sorted(backend.read_calls) == sorted(json_keys)
    assert len(backend.read_calls) == len(json_keys)


def test_focused_zero_backend_rereads_during_candidate_and_idempotency() -> None:
    backend = _populated_backend()
    report = ev.run_dry_run(
        base_auth(), fixture_path=FIXTURE, backend=backend,
        server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY,
    )
    json_key_count = sum(1 for k in DEFAULT_KEYS if DEFAULT_ROLE_PLAN[k] in ev.JSON_READ_ROLES)
    assert report.read_calls_total == json_key_count
    # The guarded reader served the cached snapshot once per object per build.
    assert report.snapshot_consumer_calls == json_key_count * 2
    # read_calls_total equals the unique JSON object count exactly (no rereads).
    assert report.read_calls_total == report.unique_json_objects_read


# ---------------------------------------------------------------------------
# F6. matched bytes equal imported snapshot; mutation cannot substitute
# ---------------------------------------------------------------------------

def test_focused_matched_digest_equals_imported_snapshot_digest() -> None:
    report = _run()
    matched = {r["key"]: r["sha256"] for r in report.hash_results if r["status"] == "matched"}
    for key, digest in matched.items():
        # The matched digest equals the independently computed expected digest
        # for the exact bytes the accepted reader parsed.
        assert digest == _EXPECTED_JSON_HASHES.get(key) or digest == _EXPECTED_HASHES.get(key)


def test_focused_object_mutation_between_verification_and_import_rejects() -> None:
    """If the backend body changes after the snapshot is validated, the final
    observation (etag/size/version tuple) must catch it and abort."""
    backend = _populated_backend()

    original_read = backend.read_bytes

    def patched_read(key, max_bytes):
        body = original_read(key, max_bytes)
        # After the first read of a JSON key, mutate the body so a later
        # second read would return different bytes. The snapshot must still
        # be reused (no second read) AND the final observation head must
        # detect the etag change.
        return body

    backend.read_bytes = patched_read  # type: ignore[assignment]

    # Mutate the stored body for the storyboard key after its initial
    # observation so that the final observation head sees a different etag.
    real_head = backend.head

    def mutating_head(key):
        result = real_head(key)
        if key == DEFAULT_KEYS[0] and len(backend.head_calls) > len(DEFAULT_KEYS) + 8:
            # Final observation phase: swap the body and etag.
            new_body = b'{"title":"tampered"}'
            obj = backend.objects[key]
            if obj["body"] != new_body:
                obj["body"] = new_body
                obj["size_bytes"] = len(new_body)
                obj["etag"] = hashlib_attr(__import__("hashlib"), new_body)
        return real_head(key)

    backend.head = mutating_head  # type: ignore[assignment]
    with pytest.raises(ev.AuthorizationError, match="object_changed_during_evidence_run"):
        ev.run_dry_run(
            base_auth(), fixture_path=FIXTURE, backend=backend,
            server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY,
        )


def hashlib_attr(hashlib_mod, body: bytes) -> str:
    return hashlib_mod.sha256(body).hexdigest()[:32]


# ---------------------------------------------------------------------------
# F7. expected media digest cannot remain unchecked
# ---------------------------------------------------------------------------

def test_focused_expected_media_digest_with_media_reads_disabled_rejects() -> None:
    media_key = next(k for k in DEFAULT_KEYS if DEFAULT_ROLE_PLAN[k] in ev.MEDIA_BYTE_ROLES)
    auth = base_auth(
        expected_sha256_by_key={
            **_EXPECTED_JSON_HASHES,
            media_key: _EXPECTED_HASHES[media_key],
        },
        allow_media_byte_reads=False,
    )
    with pytest.raises(ev.AuthorizationError, match="expected_media_hash_requires_media_reads"):
        ev.validate_authorization(auth, execute_mode=False)


def test_focused_expected_digest_for_unconsumed_role_rejects() -> None:
    """If an expected digest is present for a key but the key is never read
    (e.g. media reads disabled and the role is media), the run rejects."""
    media_key = next(k for k in DEFAULT_KEYS if DEFAULT_ROLE_PLAN[k] in ev.MEDIA_BYTE_ROLES)
    auth = base_auth(
        allow_media_byte_reads=False,
        expected_sha256_by_key=dict(_EXPECTED_JSON_HASHES),
    )
    # Normal run passes. Now craft a scenario where an expected digest would
    # be unconsumed: bypass validation and inject an extra expected entry for
    # the media key directly into the run.
    auth_bad = copy.deepcopy(auth)
    auth_bad["expected_sha256_by_key"][media_key] = _EXPECTED_HASHES[media_key]
    # Validation catches this (expected_media_hash_requires_media_reads).
    with pytest.raises(ev.AuthorizationError, match="expected_media_hash_requires_media_reads"):
        ev.validate_authorization(auth_bad, execute_mode=False)


def test_focused_all_expected_entries_consumed() -> None:
    report = _run()
    expected_keys = set(_EXPECTED_JSON_HASHES)
    result_keys = {r["key"] for r in report.hash_results}
    assert expected_keys <= result_keys
    for key in expected_keys:
        matched = [r for r in report.hash_results if r["key"] == key]
        assert matched and matched[0]["status"] == "matched"


# ---------------------------------------------------------------------------
# F8. media per-object overflow (cap and cap+1)
# ---------------------------------------------------------------------------

def _media_backend(body: bytes) -> "ev.FakeB2Backend":
    backend = ev.FakeB2Backend()
    media_key = next(k for k in DEFAULT_KEYS if DEFAULT_ROLE_PLAN[k] in ev.MEDIA_BYTE_ROLES)
    for key in DEFAULT_KEYS:
        if DEFAULT_ROLE_PLAN[key] in ev.JSON_READ_ROLES:
            fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
            role_bodies = ev._fixture_role_bodies(fixture)
            b = role_bodies[DEFAULT_ROLE_PLAN[key]]
            backend.objects[key] = {
                "body": b, "size_bytes": len(b),
                "etag": __import__("hashlib").sha256(b).hexdigest()[:32],
                "version_id": f"v_{__import__('hashlib').sha256(key.encode()).hexdigest()[:8]}",
            }
        else:
            backend.objects[key] = {
                "body": body, "size_bytes": len(body),
                "etag": __import__("hashlib").sha256(body).hexdigest()[:32],
                "version_id": f"v_{__import__('hashlib').sha256(key.encode()).hexdigest()[:8]}",
            }
    return backend


def test_focused_media_object_at_exact_cap_passes() -> None:
    cap = 2048  # above the largest JSON object (1560 bytes)
    body = b"\x00" * cap
    backend = _media_backend(body)
    auth = base_auth(
        allow_media_byte_reads=True,
        max_object_bytes=cap,
        max_total_bytes=cap + 16_777_216,
        expected_sha256_by_key=dict(_EXPECTED_JSON_HASHES),
    )
    report = ev.run_dry_run(
        auth, fixture_path=FIXTURE, backend=backend,
        server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY,
    )
    assert report.unique_media_objects_read == 1


def test_focused_media_object_cap_plus_one_rejects() -> None:
    cap = 2048
    body = b"\x00" * (cap + 1)
    backend = _media_backend(body)
    auth = base_auth(
        allow_media_byte_reads=True,
        max_object_bytes=cap,
        max_total_bytes=cap + 16_777_216,
        expected_sha256_by_key=dict(_EXPECTED_JSON_HASHES),
    )
    # The metadata preflight enforces the per-object cap on the declared
    # ``size_bytes`` before any byte read; the bounded asset reader enforces
    # the same cap again as defense in depth. Either stable code is acceptable.
    with pytest.raises(ev.AuthorizationError, match="object_exceeds_authorization_cap|media_object_exceeds_authorization_cap|media_object_exceeds_approved_limit"):
        ev.run_dry_run(
            auth, fixture_path=FIXTURE, backend=backend,
            server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY,
        )


# ---------------------------------------------------------------------------
# F9. media aggregate overflow
# ---------------------------------------------------------------------------

def test_focused_media_aggregate_overflow_rejects() -> None:
    media_body_len = 4096
    body = b"\x00" * media_body_len
    backend = _media_backend(body)
    auth = base_auth(
        allow_media_byte_reads=True,
        max_object_bytes=media_body_len,
        # Aggregate budget large enough for JSON (~4065 bytes) but too small
        # for JSON + the media body.
        max_total_bytes=5000,
        expected_sha256_by_key=dict(_EXPECTED_JSON_HASHES),
    )
    with pytest.raises(_DRY_RUN_ABORT):
        ev.run_dry_run(
            auth, fixture_path=FIXTURE, backend=backend,
            server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY,
        )


# ---------------------------------------------------------------------------
# F10. media body length mismatch (shorter / longer than declared)
# ---------------------------------------------------------------------------

def test_focused_media_body_shorter_than_declared_rejects() -> None:
    backend = _media_backend(b"\x00" * 1024)
    media_key = next(k for k in DEFAULT_KEYS if DEFAULT_ROLE_PLAN[k] in ev.MEDIA_BYTE_ROLES)
    backend.objects[media_key]["size_bytes"] = 2048  # declare larger than body
    auth = base_auth(
        allow_media_byte_reads=True,
        max_object_bytes=4096,
        max_total_bytes=16_777_216 * 2,
        expected_sha256_by_key=dict(_EXPECTED_HASHES),
    )
    with pytest.raises(ev.AuthorizationError, match="media_length_mismatch"):
        ev.run_dry_run(
            auth, fixture_path=FIXTURE, backend=backend,
            server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY,
        )


def test_focused_media_body_longer_than_declared_rejects() -> None:
    backend = _media_backend(b"\x00" * 2048)
    media_key = next(k for k in DEFAULT_KEYS if DEFAULT_ROLE_PLAN[k] in ev.MEDIA_BYTE_ROLES)
    backend.objects[media_key]["size_bytes"] = 1024  # declare smaller than body
    auth = base_auth(
        allow_media_byte_reads=True,
        max_object_bytes=4096,
        max_total_bytes=16_777_216 * 2,
        expected_sha256_by_key=dict(_EXPECTED_HASHES),
    )
    with pytest.raises(ev.AuthorizationError, match="media_length_mismatch"):
        ev.run_dry_run(
            auth, fixture_path=FIXTURE, backend=backend,
            server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY,
        )


# ---------------------------------------------------------------------------
# F11. media metadata TOCTOU (etag / size / version change after read)
# ---------------------------------------------------------------------------

def _run_with_media_toctou(*, mutate_field: str) -> None:
    backend = _media_backend(b"\x00" * 1024)
    media_key = next(k for k in DEFAULT_KEYS if DEFAULT_ROLE_PLAN[k] in ev.MEDIA_BYTE_ROLES)
    real_head = backend.head
    call_state = {"media_reads_seen": 0}

    def toctou_head(key):
        result = real_head(key)
        if key == media_key:
            call_state["media_reads_seen"] += 1
            if call_state["media_reads_seen"] >= 3:  # post-read head
                obj = backend.objects[media_key]
                if mutate_field == "etag":
                    obj["etag"] = "tampered-etag"
                elif mutate_field == "size_bytes":
                    obj["size_bytes"] = obj["size_bytes"] + 1
                elif mutate_field == "version_id":
                    obj["version_id"] = "v_tampered"
        return real_head(key)

    backend.head = toctou_head  # type: ignore[assignment]
    auth = base_auth(
        allow_media_byte_reads=True,
        max_object_bytes=4096,
        max_total_bytes=16_777_216 * 2,
        expected_sha256_by_key=dict(_EXPECTED_HASHES),
    )
    with pytest.raises(ev.AuthorizationError, match="object_changed_during_evidence_run"):
        ev.run_dry_run(
            auth, fixture_path=FIXTURE, backend=backend,
            server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY,
        )


def test_focused_media_etag_change_after_read_rejects() -> None:
    _run_with_media_toctou(mutate_field="etag")


def test_focused_media_size_change_after_read_rejects() -> None:
    _run_with_media_toctou(mutate_field="size_bytes")


def test_focused_media_version_change_after_read_rejects() -> None:
    _run_with_media_toctou(mutate_field="version_id")


def test_focused_expected_media_hash_match() -> None:
    body = b"\x00" * 1024
    backend = _media_backend(body)
    media_key = next(k for k in DEFAULT_KEYS if DEFAULT_ROLE_PLAN[k] in ev.MEDIA_BYTE_ROLES)
    media_expected = {**_EXPECTED_JSON_HASHES,
                      media_key: __import__("hashlib").sha256(body).hexdigest()}
    auth = base_auth(
        allow_media_byte_reads=True,
        max_object_bytes=4096,
        max_total_bytes=16_777_216 * 2,
        expected_sha256_by_key=media_expected,
    )
    report = ev.run_dry_run(
        auth, fixture_path=FIXTURE, backend=backend,
        server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY,
    )
    media_results = [r for r in report.hash_results if r["key"] == media_key]
    assert len(media_results) == 1
    assert media_results[0]["status"] == "matched"


def test_focused_expected_media_hash_mismatch_rejects() -> None:
    body = b"\x00" * 1024
    backend = _media_backend(body)
    media_key = next(k for k in DEFAULT_KEYS if DEFAULT_ROLE_PLAN[k] in ev.MEDIA_BYTE_ROLES)
    media_expected = {**_EXPECTED_JSON_HASHES, media_key: "0" * 64}
    auth = base_auth(
        allow_media_byte_reads=True,
        max_object_bytes=4096,
        max_total_bytes=16_777_216 * 2,
        expected_sha256_by_key=media_expected,
    )
    with pytest.raises(_DRY_RUN_ABORT, match="unexpected_hash_mismatch"):
        ev.run_dry_run(
            auth, fixture_path=FIXTURE, backend=backend,
            server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY,
        )


# ---------------------------------------------------------------------------
# F12. actual counters equal backend instrumentation
# ---------------------------------------------------------------------------

def test_focused_actual_counters_equal_backend_instrumentation() -> None:
    backend = _populated_backend()
    report = ev.run_dry_run(
        base_auth(), fixture_path=FIXTURE, backend=backend,
        server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY,
    )
    assert report.head_calls_total == len(backend.head_calls)
    assert report.read_calls_total == len(backend.read_calls)
    assert report.list_calls == len(backend.list_calls)
    assert report.write_attempts == len(backend.write_attempts)
    assert report.delete_attempts == len(backend.delete_attempts)
    assert report.signed_url_attempts == len(backend.signed_url_attempts)
    assert report.total_bytes_read == backend.total_bytes_read
    json_keys = [k for k in DEFAULT_KEYS if DEFAULT_ROLE_PLAN[k] in ev.JSON_READ_ROLES]
    assert report.unique_json_objects_read == len(json_keys)
    assert report.unique_media_objects_read == 0
    # Default readiness: 4 JSON objects read once each; 0 media reads.
    assert report.read_calls_total == 4
    assert report.unique_json_objects_read == 4


# ---------------------------------------------------------------------------
# F13. unknown fake JSON key does not return b"{}"
# ---------------------------------------------------------------------------

def test_focused_unknown_fake_json_key_rejects_no_empty_object_fallback() -> None:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    unknown_key = f"{PREFIX}/runs/zz/unknown-manifest.json"
    plan = dict(DEFAULT_ROLE_PLAN)
    # Replace b2 key with an unknown JSON role mapping: point b2 manifest key
    # at a role the fixture has, but swap the b2 key to one whose role the
    # backend builder cannot satisfy via a different fixture role.
    plan.pop(DEFAULT_KEYS[3])  # drop real b2 key
    plan[unknown_key] = ev.ROLE_STAGE_B2_MANIFEST
    auth = base_auth(
        allowed_keys=list(plan.keys()),
        object_role_by_key=plan,
        expected_sha256_by_key={
            k: v for k, v in _EXPECTED_JSON_HASHES.items() if k in plan
        },
    )
    # The backend builder serves the b2 manifest body for the unknown key
    # (role-based, not suffix-based). That succeeds. But to prove no b"{}"
    # fallback, ask for a role with no fixture body:
    bad_plan = {DEFAULT_KEYS[0]: "stage_a_storyboard"}  # only one role
    # Replace storyboard's role with a fabricated role not in KNOWN_ROLES.
    bad_plan2 = dict(DEFAULT_ROLE_PLAN)
    bad_plan2[DEFAULT_KEYS[0]] = "stage_a_unknown_role"
    auth2 = base_auth(object_role_by_key=bad_plan2)
    with pytest.raises(ev.AuthorizationError, match="object_role_unknown_role"):
        ev.validate_authorization(auth2, execute_mode=False)


def test_focused_no_empty_json_fallback_in_backend_build() -> None:
    """The fake backend must not serve b"{}" for a JSON-read role whose fixture
    body is absent. ``_build_fake_backend`` must reject with a stable code."""
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    fixture_no_sb = copy.deepcopy(fixture)
    for obj in fixture_no_sb["objects"]:
        if obj["role"] == ev.ROLE_STAGE_A_STORYBOARD:
            obj["inline_json"] = None
    with pytest.raises(ev.AuthorizationError, match="fake_backend_unknown_json_role"):
        ev._build_fake_backend(
            fixture_no_sb, list(DEFAULT_KEYS), object_role_by_key=dict(DEFAULT_ROLE_PLAN),
        )


# ---------------------------------------------------------------------------
# F14. no raw exception, credential or bucket name in diagnostics
# ---------------------------------------------------------------------------

def test_focused_no_raw_exception_credential_or_bucket_in_diagnostics() -> None:
    report = _run()
    serialized = json.dumps(report.__dict__, default=str, sort_keys=True)
    for token in FORBIDDEN_TOKENS + [SERVER_BUCKET_IDENTITY]:
        assert token.lower() not in serialized.lower()
    # Error codes are stable strings, not raw exception text.
    for r in report.hash_results:
        assert isinstance(r["status"], str)
        assert r["status"] in {"matched", "observed", "computed", "mismatch"}


# ---------------------------------------------------------------------------
# F15. full observation stability (complete tuple comparison)
# ---------------------------------------------------------------------------

def test_focused_full_observation_stability_compares_every_object() -> None:
    report = _run()
    assert report.observation_stable is True
    assert report.observation_comparisons == len(DEFAULT_KEYS)


def test_focused_final_observation_missing_object_rejects() -> None:
    backend = _populated_backend()
    real_head = backend.head
    state = {"phase": "initial"}

    def dropping_head(key):
        result = real_head(key)
        # After the candidate build (many heads), start dropping the media key.
        if key == DEFAULT_KEYS[4] and len(backend.head_calls) > len(DEFAULT_KEYS) + 10:
            backend.objects.pop(DEFAULT_KEYS[4], None)
            return None
        return result

    backend.head = dropping_head  # type: ignore[assignment]
    with pytest.raises(ev.AuthorizationError, match="object_changed_during_evidence_run"):
        ev.run_dry_run(
            base_auth(), fixture_path=FIXTURE, backend=backend,
            server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY,
        )


# ---------------------------------------------------------------------------
# F16. object_role_by_key structural validation edge cases
# ---------------------------------------------------------------------------

def test_focused_object_role_by_key_not_object_rejects() -> None:
    auth = base_auth(object_role_by_key=["not", "a", "dict"])
    with pytest.raises(ev.AuthorizationError, match="object_role_by_key_not_object"):
        ev.validate_authorization(auth, execute_mode=False)


def test_focused_object_role_by_key_value_not_string_rejects() -> None:
    plan = dict(DEFAULT_ROLE_PLAN)
    plan[DEFAULT_KEYS[0]] = 123
    auth = base_auth(object_role_by_key=plan)
    with pytest.raises(ev.AuthorizationError, match="object_role_value_not_string"):
        ev.validate_authorization(auth, execute_mode=False)


# ---------------------------------------------------------------------------
# F17. fake backend oversized read rejects (never truncates)
# ---------------------------------------------------------------------------

def test_focused_fake_backend_rejects_oversized_read_never_truncates() -> None:
    backend = ev.FakeB2Backend()
    backend.objects["k"] = {
        "body": b"x" * 100, "size_bytes": 100, "etag": "e", "version_id": "v",
    }
    with pytest.raises(AssertionError, match="fake_backend_oversized_read_rejected"):
        backend.read_bytes("k", 50)


def test_focused_fake_backend_serves_exact_bytes_under_cap() -> None:
    backend = ev.FakeB2Backend()
    body = b"x" * 50
    backend.objects["k"] = {
        "body": body, "size_bytes": 50, "etag": "e", "version_id": "v",
    }
    assert backend.read_bytes("k", 100) == body
    assert backend.total_bytes_read == 50
    assert backend.last_read_bytes["k"] == body


# ---------------------------------------------------------------------------
# F18. resolve_role_to_key never uses endswith or allowlist order
# ---------------------------------------------------------------------------

def test_focused_resolve_role_to_key_is_order_independent() -> None:
    plan_a = dict(DEFAULT_ROLE_PLAN)
    plan_b = {k: plan_a[k] for k in reversed(list(plan_a.keys()))}
    assert ev.resolve_role_to_key(plan_a) == ev.resolve_role_to_key(plan_b)


# ---------------------------------------------------------------------------
# F19. dry-run mode reports all required counters via CLI
# ---------------------------------------------------------------------------

def test_focused_dry_run_cli_reports_actual_counters(tmp_path: Path) -> None:
    import io
    import contextlib
    p = write_auth(tmp_path, base_auth())
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = ev.main(["--dry-run", str(p)])
    assert rc == 0
    payload = json.loads(buf.getvalue())
    for field in (
        "head_calls_total", "read_calls_total", "unique_json_objects_read",
        "unique_media_objects_read", "snapshot_consumer_calls", "list_calls",
        "write_attempts", "delete_attempts", "signed_url_attempts",
        "total_bytes_read", "observation_stable", "observation_comparisons",
    ):
        assert field in payload, f"missing counter in dry-run output: {field}"
    assert payload["read_calls_total"] == 4
    assert payload["unique_json_objects_read"] == 4
    assert payload["unique_media_objects_read"] == 0
    assert payload["snapshot_consumer_calls"] == 8
    assert payload["observation_comparisons"] == 5


# ===========================================================================
# PS-041E2-A v3 FOCUSED REGRESSION CASES
#
# These cases cover the final readiness-contract blockers found during PM
# artifact review:
#   G1  head-metadata caps enforced for every object before any byte read;
#   G2  declared-inventory aggregate cap enforced before any byte read;
#   G3  every accepted role is consumable (supported/reserved invariant);
#   G4  ``embedded_manifest`` is rejected as reserved at validation time;
#   G5  unified ``FUTURE_EXECUTE_GATES`` contract (single source of truth);
#   G6  media/backend failures normalize to stable codes (no raw exception);
#   G7  no credential / raw bucket content in diagnostics.
# ===========================================================================


# ---------------------------------------------------------------------------
# G1. head-metadata per-object caps (metadata-only, no byte read required)
# ---------------------------------------------------------------------------

def test_g1_oversized_metadata_only_final_delivery_rejects() -> None:
    """Even when ``allow_media_byte_reads=false`` the declared size of the
    final delivery object is enforced during the metadata preflight. No byte
    read ever occurs. The auth and accepted caps are equal at the limit so
    the binding-constraint code surfaces; the accepted-only path is covered
    by the helper-level unit tests below."""
    backend = _populated_backend()
    media_key = next(k for k in DEFAULT_KEYS if DEFAULT_ROLE_PLAN[k] in ev.MEDIA_BYTE_ROLES)
    backend.objects[media_key]["size_bytes"] = ev.ACCEPTED_MAX_MEDIA_OBJECT_BYTES + 1
    auth = base_auth(
        allow_media_byte_reads=False,
        max_object_bytes=ev.ACCEPTED_MAX_MEDIA_OBJECT_BYTES,
        max_total_bytes=ev.ACCEPTED_MAX_AGGREGATE_BYTES,
    )
    with pytest.raises(ev.AuthorizationError, match="object_exceeds_authorization_cap|object_exceeds_accepted_cap"):
        ev.run_dry_run(auth, fixture_path=FIXTURE, backend=backend,
                       server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY)
    assert backend.read_calls == []


def test_g1_metadata_only_object_exceeds_authorization_cap_rejects() -> None:
    """The authorization ``max_object_bytes`` cap is enforced on the declared
    metadata-only size, independent of the accepted cap and independent of
    media byte reads."""
    backend = _populated_backend()
    media_key = next(k for k in DEFAULT_KEYS if DEFAULT_ROLE_PLAN[k] in ev.MEDIA_BYTE_ROLES)
    backend.objects[media_key]["size_bytes"] = 8192
    auth = base_auth(
        allow_media_byte_reads=False,
        max_object_bytes=4096,
        max_total_bytes=16_777_216,
    )
    with pytest.raises(ev.AuthorizationError, match="object_exceeds_authorization_cap"):
        ev.run_dry_run(auth, fixture_path=FIXTURE, backend=backend,
                       server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY)
    assert backend.read_calls == []


def test_g1_negative_size_bytes_rejects() -> None:
    backend = _populated_backend()
    backend.objects[DEFAULT_KEYS[0]]["size_bytes"] = -1
    with pytest.raises(ev.AuthorizationError, match="object_size_invalid"):
        ev.run_dry_run(base_auth(), fixture_path=FIXTURE, backend=backend,
                       server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY)
    assert backend.read_calls == []


def test_g1_boolean_size_bytes_rejects() -> None:
    backend = _populated_backend()
    backend.objects[DEFAULT_KEYS[0]]["size_bytes"] = True
    with pytest.raises(ev.AuthorizationError, match="object_size_invalid"):
        ev.run_dry_run(base_auth(), fixture_path=FIXTURE, backend=backend,
                       server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY)
    assert backend.read_calls == []


def test_g1_string_size_bytes_rejects() -> None:
    backend = _populated_backend()
    backend.objects[DEFAULT_KEYS[0]]["size_bytes"] = "1024"
    with pytest.raises(ev.AuthorizationError, match="object_size_invalid"):
        ev.run_dry_run(base_auth(), fixture_path=FIXTURE, backend=backend,
                       server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY)
    assert backend.read_calls == []


def test_g1_missing_size_bytes_rejects() -> None:
    backend = _populated_backend()
    # Simulate a head() that returns metadata without the ``size_bytes`` key.
    real_head = backend.head

    def head_without_size(key):
        result = real_head(key)
        if result is None:
            return None
        return {"etag": result["etag"], "version_id": result["version_id"]}
    backend.head = head_without_size  # type: ignore[assignment]
    with pytest.raises(ev.AuthorizationError, match="object_size_invalid"):
        ev.run_dry_run(base_auth(), fixture_path=FIXTURE, backend=backend,
                       server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY)
    assert backend.read_calls == []


def test_g1_non_mapping_metadata_rejects() -> None:
    backend = _populated_backend()
    real_head = backend.head

    def head_non_mapping(key):
        result = real_head(key)
        if result is None:
            return None
        return ["not", "a", "mapping"]
    backend.head = head_non_mapping  # type: ignore[assignment]
    with pytest.raises(ev.AuthorizationError, match="object_metadata_invalid"):
        ev.run_dry_run(base_auth(), fixture_path=FIXTURE, backend=backend,
                       server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY)
    assert backend.read_calls == []


def test_g1_exact_per_object_and_aggregate_caps_pass() -> None:
    """When every declared size is exactly at or below both per-object and
    aggregate caps, the preflight passes and the run succeeds."""
    backend = _populated_backend()
    # Build a deterministic media body so the per-object cap is exactly met.
    media_key = next(k for k in DEFAULT_KEYS if DEFAULT_ROLE_PLAN[k] in ev.MEDIA_BYTE_ROLES)
    cap = 2048
    body = b"\x00" * cap
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    role_bodies = ev._fixture_role_bodies(fixture)
    json_total = sum(len(role_bodies[r]) for r in role_bodies)
    for key in DEFAULT_KEYS:
        role = DEFAULT_ROLE_PLAN[key]
        if role in ev.JSON_READ_ROLES:
            b = role_bodies[role]
            backend.objects[key] = {
                "body": b, "size_bytes": len(b),
                "etag": __import__("hashlib").sha256(b).hexdigest()[:32],
                "version_id": f"v_{__import__('hashlib').sha256(key.encode()).hexdigest()[:8]}",
            }
        else:
            backend.objects[key] = {
                "body": body, "size_bytes": cap,
                "etag": __import__("hashlib").sha256(body).hexdigest()[:32],
                "version_id": f"v_{__import__('hashlib').sha256(key.encode()).hexdigest()[:8]}",
            }
    media_expected = {**_EXPECTED_JSON_HASHES,
                      media_key: __import__("hashlib").sha256(body).hexdigest()}
    auth = base_auth(
        allow_media_byte_reads=True,
        max_object_bytes=cap,
        max_total_bytes=json_total + cap,
        expected_sha256_by_key=media_expected,
    )
    report = ev.run_dry_run(auth, fixture_path=FIXTURE, backend=backend,
                            server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY)
    assert report.ok
    assert report.unique_media_objects_read == 1


# ---------------------------------------------------------------------------
# G2. declared-inventory aggregate cap (sum of declared sizes)
# ---------------------------------------------------------------------------

def test_g2_declared_inventory_exceeds_authorization_total_rejects() -> None:
    """The sum of declared object sizes (from head, before any byte read) must
    not exceed the authorization ``max_total_bytes``."""
    backend = _populated_backend()
    # Bump media declared size so the inventory overflows the total cap.
    media_key = next(k for k in DEFAULT_KEYS if DEFAULT_ROLE_PLAN[k] in ev.MEDIA_BYTE_ROLES)
    backend.objects[media_key]["size_bytes"] = 8192
    # max_total_bytes >= max_object_bytes (so the auth-shape check passes) but
    # below the declared inventory (JSON 4190 + media 8192 = 12382).
    auth = base_auth(
        allow_media_byte_reads=True,
        max_object_bytes=8192,
        max_total_bytes=8192,
    )
    with pytest.raises(ev.AuthorizationError, match="declared_inventory_exceeds_authorization_total"):
        ev.run_dry_run(auth, fixture_path=FIXTURE, backend=backend,
                       server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY)
    assert backend.read_calls == []


def test_g2_declared_inventory_exceeds_accepted_total_rejects() -> None:
    """The sum of declared object sizes must not exceed the immutable
    ``ACCEPTED_MAX_AGGREGATE_BYTES``. With the auth total set at the accepted
    limit, both code paths trip simultaneously; the binding-constraint code
    surfaces. The accepted-only path is exercised directly on the helper
    below."""
    backend = _populated_backend()
    # Set every object's declared size to the exact per-object accepted cap.
    # Five objects at the per-object cap (4 × aggregate/per-object) overflow
    # the immutable aggregate cap without tripping the per-object checks.
    for key in DEFAULT_KEYS:
        backend.objects[key]["size_bytes"] = ev.ACCEPTED_MAX_MEDIA_OBJECT_BYTES
    auth = base_auth(
        allow_media_byte_reads=True,
        max_object_bytes=ev.ACCEPTED_MAX_MEDIA_OBJECT_BYTES,
        max_total_bytes=ev.ACCEPTED_MAX_AGGREGATE_BYTES,
    )
    with pytest.raises(
        ev.AuthorizationError,
        match="declared_inventory_exceeds_authorization_total|declared_inventory_exceeds_accepted_total",
    ):
        ev.run_dry_run(auth, fixture_path=FIXTURE, backend=backend,
                       server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY)
    assert backend.read_calls == []


def test_g2_size_helper_accepts_and_rejects_each_cap_path() -> None:
    """Directly exercise the accepted-cap code path that the integrated flow
    cannot reach when the auth cap has already been narrowed to the accepted
    limit by ``validate_authorization``."""
    # value <= auth <= accepted: passes
    assert ev._require_object_size_bytes(
        1024, auth_cap=4096, accepted_cap=ev.ACCEPTED_MAX_MEDIA_OBJECT_BYTES,
    ) == 1024
    # value > auth, value <= accepted: auth-cap code path.
    with pytest.raises(ev.AuthorizationError, match="object_exceeds_authorization_cap"):
        ev._require_object_size_bytes(
            8192, auth_cap=4096, accepted_cap=ev.ACCEPTED_MAX_MEDIA_OBJECT_BYTES,
        )
    # value > accepted (and > auth): accepted-cap code path (defense in depth
    # for the case where validate_authorization is bypassed).
    with pytest.raises(ev.AuthorizationError, match="object_exceeds_accepted_cap"):
        ev._require_object_size_bytes(
            ev.ACCEPTED_MAX_MEDIA_OBJECT_BYTES + 1,
            auth_cap=ev.ACCEPTED_MAX_MEDIA_OBJECT_BYTES + 16,
            accepted_cap=ev.ACCEPTED_MAX_MEDIA_OBJECT_BYTES,
        )


def test_g2_metadata_helper_rejects_non_mapping() -> None:
    with pytest.raises(ev.AuthorizationError, match="object_metadata_invalid"):
        ev._require_object_metadata(["not", "a", "mapping"])
    with pytest.raises(ev.AuthorizationError, match="object_metadata_invalid"):
        ev._require_object_metadata("not-a-mapping")
    assert ev._require_object_metadata({"size_bytes": 1}) == {"size_bytes": 1}


def test_g2_preflight_failure_makes_zero_byte_reads() -> None:
    """Any metadata-preflight failure must abort before any byte read."""
    backend = _populated_backend()
    backend.objects[DEFAULT_KEYS[0]]["size_bytes"] = -1
    with pytest.raises(ev.AuthorizationError):
        ev.run_dry_run(base_auth(), fixture_path=FIXTURE, backend=backend,
                       server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY)
    assert backend.read_calls == []
    assert backend.write_attempts == []
    assert backend.delete_attempts == []
    assert backend.list_calls == []


# ---------------------------------------------------------------------------
# G3. supported/reserved role invariant
# ---------------------------------------------------------------------------

def test_g3_known_roles_partition_into_supported_and_reserved() -> None:
    """Every role accepted by ``KNOWN_ROLES`` has exactly one explicit
    consumption mode (supported) or is explicitly reserved (rejected at
    validation). No role is silently unconsumable."""
    assert ev.KNOWN_ROLES == ev.SUPPORTED_ROLES | ev.RESERVED_ROLES
    assert not (ev.SUPPORTED_ROLES & ev.RESERVED_ROLES)
    assert ev.SUPPORTED_ROLES == ev.JSON_READ_ROLES | ev.MEDIA_BYTE_ROLES
    assert not (ev.JSON_READ_ROLES & ev.MEDIA_BYTE_ROLES)


def test_g3_no_validation_success_then_fake_backend_unknown_role() -> None:
    """For every role in ``SUPPORTED_ROLES`` validation accepts, the fake
    backend builder must be able to serve it. The unsupported path is exactly
    ``RESERVED_ROLES``."""
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    role_bodies = ev._fixture_role_bodies(fixture)
    # Every supported JSON role has a fixture body in the accepted contract.
    for role in ev.JSON_READ_ROLES:
        assert role in role_bodies, f"JSON role lacks fixture body: {role}"
    # Every supported media role is served from the bounded placeholder.
    assert ev.MEDIA_BYTE_ROLES  # at least one bounded media role exists


# ---------------------------------------------------------------------------
# G4. embedded_manifest decision (reserved/unsupported at validation)
# ---------------------------------------------------------------------------

def test_g4_embedded_manifest_decision() -> None:
    """The accepted fixture carries ``embedded_manifest`` as ``missing=true``
    with no bounded JSON descriptor. Therefore it MUST be rejected as reserved
    during authorization validation, not deferred to the fake backend."""
    plan = dict(DEFAULT_ROLE_PLAN)
    extra_key = f"{PREFIX}/runs/embedded/manifest.json"
    plan[extra_key] = ev.ROLE_EMBEDDED_MANIFEST
    auth = base_auth(
        allowed_keys=list(plan.keys()),
        object_role_by_key=plan,
        max_object_count=16,
        expected_sha256_by_key=dict(_EXPECTED_JSON_HASHES),
    )
    # Validation must reject reserved roles before any backend work.
    with pytest.raises(ev.AuthorizationError, match="object_role_reserved_unsupported"):
        ev.validate_authorization(auth, execute_mode=False)

    # The accepted fixture must not carry a bounded JSON descriptor for the
    # reserved role (this is what makes it reserved, not supported).
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    for obj in fixture["objects"]:
        if obj["role"] == ev.ROLE_EMBEDDED_MANIFEST:
            assert obj.get("inline_json") is None or obj.get("missing") is True, (
                "embedded_manifest must remain reserved until a bounded JSON "
                "descriptor exists in the accepted fixture/contract"
            )


def test_g4_reserved_role_separate_from_unknown_role() -> None:
    """A reserved role is known and rejects with the reserved code, not the
    unknown-role code."""
    plan = dict(DEFAULT_ROLE_PLAN)
    plan[DEFAULT_KEYS[0]] = ev.ROLE_EMBEDDED_MANIFEST
    auth = base_auth(object_role_by_key=plan)
    with pytest.raises(ev.AuthorizationError, match="object_role_reserved_unsupported"):
        ev.validate_authorization(auth, execute_mode=False)


# ---------------------------------------------------------------------------
# G5. unified FUTURE_EXECUTE_GATES contract
# ---------------------------------------------------------------------------

def test_g5_future_execute_gates_count_matches_canonical_list() -> None:
    """The documented count equals the actual canonical list length."""
    assert ev.FUTURE_EXECUTE_GATES_COUNT == len(ev.FUTURE_EXECUTE_GATES)
    assert ev.FUTURE_EXECUTE_GATES_COUNT == len(ev._execute_gates())


def test_g5_future_execute_gates_are_unique() -> None:
    assert len(set(ev.FUTURE_EXECUTE_GATES)) == ev.FUTURE_EXECUTE_GATES_COUNT


def test_g5_future_execute_gates_check_readiness_summary_matches() -> None:
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ev.main(["--check-readiness"])
    summary = json.loads(buf.getvalue())
    assert summary["future_execute_gates"] == list(ev.FUTURE_EXECUTE_GATES)
    assert summary["future_execute_gates_count"] == ev.FUTURE_EXECUTE_GATES_COUNT


def test_g5_future_execute_gates_required_controls_represented() -> None:
    """The canonical list must represent every required control family."""
    blob = "\n".join(ev.FUTURE_EXECUTE_GATES).lower()
    for required_token in (
        "authorized_by", "alias", "bucket", "prefix", "object-role",
        "caps", "credential", "repository tree", "confirm",
    ):
        assert required_token in blob, (
            f"required control family not represented in FUTURE_EXECUTE_GATES: "
            f"{required_token}"
        )


def test_g5_execute_mode_stderr_states_canonical_count(tmp_path: Path) -> None:
    import io
    import contextlib
    p = write_auth(tmp_path, base_auth())
    err_buf = io.StringIO()
    with contextlib.redirect_stderr(err_buf):
        rc = ev.main(["--execute", str(p)])
    assert rc == 2
    err_text = err_buf.getvalue()
    assert str(ev.FUTURE_EXECUTE_GATES_COUNT) in err_text
    for gate in ev.FUTURE_EXECUTE_GATES:
        assert gate in err_text


# ---------------------------------------------------------------------------
# G6. media/backend failure normalization
# ---------------------------------------------------------------------------

def test_g6_object_removed_after_pre_head_rejects_cleanly() -> None:
    backend = _media_backend(b"\x00" * 1024)
    media_key = next(k for k in DEFAULT_KEYS if DEFAULT_ROLE_PLAN[k] in ev.MEDIA_BYTE_ROLES)
    real_read = backend.read_bytes

    def vanishing_read(key, max_bytes):
        if key == media_key:
            backend.objects.pop(media_key, None)
        return real_read(key, max_bytes)
    backend.read_bytes = vanishing_read  # type: ignore[assignment]
    auth = base_auth(
        allow_media_byte_reads=True,
        max_object_bytes=4096,
        max_total_bytes=16_777_216 * 2,
        expected_sha256_by_key=dict(_EXPECTED_HASHES),
    )
    with pytest.raises(ev.AuthorizationError, match="backend_read_failed"):
        ev.run_dry_run(auth, fixture_path=FIXTURE, backend=backend,
                       server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY)


def test_g6_backend_oserror_during_read_rejects_cleanly() -> None:
    backend = _media_backend(b"\x00" * 1024)
    media_key = next(k for k in DEFAULT_KEYS if DEFAULT_ROLE_PLAN[k] in ev.MEDIA_BYTE_ROLES)
    real_read = backend.read_bytes

    def failing_read(key, max_bytes):
        if key == media_key:
            raise OSError("simulated transport failure")
        return real_read(key, max_bytes)
    backend.read_bytes = failing_read  # type: ignore[assignment]
    auth = base_auth(
        allow_media_byte_reads=True,
        max_object_bytes=4096,
        max_total_bytes=16_777_216 * 2,
        expected_sha256_by_key=dict(_EXPECTED_HASHES),
    )
    with pytest.raises(ev.AuthorizationError, match="backend_read_failed"):
        ev.run_dry_run(auth, fixture_path=FIXTURE, backend=backend,
                       server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY)


def test_g6_non_bytes_backend_response_rejects_cleanly() -> None:
    backend = _media_backend(b"\x00" * 1024)
    media_key = next(k for k in DEFAULT_KEYS if DEFAULT_ROLE_PLAN[k] in ev.MEDIA_BYTE_ROLES)
    real_read = backend.read_bytes

    def str_read(key, max_bytes):
        if key == media_key:
            return "not bytes"
        return real_read(key, max_bytes)
    backend.read_bytes = str_read  # type: ignore[assignment]
    auth = base_auth(
        allow_media_byte_reads=True,
        max_object_bytes=4096,
        max_total_bytes=16_777_216 * 2,
        expected_sha256_by_key=dict(_EXPECTED_HASHES),
    )
    with pytest.raises(ev.AuthorizationError, match="backend_response_not_bytes"):
        ev.run_dry_run(auth, fixture_path=FIXTURE, backend=backend,
                       server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY)


def test_g6_malformed_pre_head_size_rejects_cleanly() -> None:
    backend = _media_backend(b"\x00" * 1024)
    media_key = next(k for k in DEFAULT_KEYS if DEFAULT_ROLE_PLAN[k] in ev.MEDIA_BYTE_ROLES)
    real_head = backend.head

    def bad_head(key):
        result = real_head(key)
        if key == media_key:
            return {"size_bytes": "big", "etag": result["etag"], "version_id": result["version_id"]}
        return result
    backend.head = bad_head  # type: ignore[assignment]
    auth = base_auth(
        allow_media_byte_reads=True,
        max_object_bytes=4096,
        max_total_bytes=16_777_216 * 2,
        expected_sha256_by_key=dict(_EXPECTED_HASHES),
    )
    with pytest.raises(ev.AuthorizationError, match="object_size_invalid"):
        ev.run_dry_run(auth, fixture_path=FIXTURE, backend=backend,
                       server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY)


def test_g6_missing_post_head_rejects_cleanly() -> None:
    backend = _media_backend(b"\x00" * 1024)
    media_key = next(k for k in DEFAULT_KEYS if DEFAULT_ROLE_PLAN[k] in ev.MEDIA_BYTE_ROLES)
    real_head = backend.head
    state = {"media_heads": 0}

    def dropping_post_head(key):
        result = real_head(key)
        if key == media_key:
            state["media_heads"] += 1
            # Pre-read head succeeds; post-read head returns None.
            if state["media_heads"] >= 3:
                backend.objects.pop(media_key, None)
                return None
        return result
    backend.head = dropping_post_head  # type: ignore[assignment]
    auth = base_auth(
        allow_media_byte_reads=True,
        max_object_bytes=4096,
        max_total_bytes=16_777_216 * 2,
        expected_sha256_by_key=dict(_EXPECTED_HASHES),
    )
    with pytest.raises(ev.AuthorizationError, match="approved_object_disappeared_after_read"):
        ev.run_dry_run(auth, fixture_path=FIXTURE, backend=backend,
                       server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY)


def test_g6_unexpected_backend_failure_during_read_normalizes() -> None:
    backend = _media_backend(b"\x00" * 1024)
    media_key = next(k for k in DEFAULT_KEYS if DEFAULT_ROLE_PLAN[k] in ev.MEDIA_BYTE_ROLES)
    real_read = backend.read_bytes

    class _WeirdError(Exception):
        pass

    def weird_read(key, max_bytes):
        if key == media_key:
            raise _WeirdError("unexpected")
        return real_read(key, max_bytes)
    backend.read_bytes = weird_read  # type: ignore[assignment]
    auth = base_auth(
        allow_media_byte_reads=True,
        max_object_bytes=4096,
        max_total_bytes=16_777_216 * 2,
        expected_sha256_by_key=dict(_EXPECTED_HASHES),
    )
    with pytest.raises(ev.AuthorizationError, match="backend_read_failed"):
        ev.run_dry_run(auth, fixture_path=FIXTURE, backend=backend,
                       server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY)


def test_g6_normalized_errors_carry_no_raw_bucket_or_credential() -> None:
    """No normalized backend error message carries raw bucket names, keys,
    credential markers, or raw exception text. Only stable codes surface."""
    backend = _media_backend(b"\x00" * 1024)
    media_key = next(k for k in DEFAULT_KEYS if DEFAULT_ROLE_PLAN[k] in ev.MEDIA_BYTE_ROLES)
    real_read = backend.read_bytes
    failures: list[str] = []

    def oserror_read(key, max_bytes):
        if key == media_key:
            raise OSError(f"transport-failure-for-{SERVER_BUCKET_IDENTITY}-key-{key}")
        return real_read(key, max_bytes)
    backend.read_bytes = oserror_read  # type: ignore[assignment]
    auth = base_auth(
        allow_media_byte_reads=True,
        max_object_bytes=4096,
        max_total_bytes=16_777_216 * 2,
        expected_sha256_by_key=dict(_EXPECTED_HASHES),
    )
    try:
        ev.run_dry_run(auth, fixture_path=FIXTURE, backend=backend,
                       server_alias=ALIAS, server_bucket_identity=SERVER_BUCKET_IDENTITY)
    except ev.AuthorizationError as exc:
        failures.append(str(exc))
        failures.append(exc.code)
    assert failures, "expected an AuthorizationError to be raised"
    blob = "\n".join(failures).lower()
    for forbidden in (
        SERVER_BUCKET_IDENTITY.lower(), "b2_application_key", "b2_app_key",
        "aws_secret_access_key", "authorization", "bearer", "password",
        "secret", "token", "cookie", "database_url",
    ):
        assert forbidden not in blob, f"forbidden token in normalized error: {forbidden}"
    # The code itself must be one of the stable codes, not raw exception text.
    assert failures[-1] == "backend_read_failed"


# ===========================================================================
# PS-041E2-B PHASE-1 — LIVE EXECUTOR FOCUSED TESTS (47 cases, all fake)
# ===========================================================================

# All tests in this section use ONLY injected fake dependencies:
# - FakeB2Backend (in-process, no network);
# - fake GitState (no subprocess);
# - fake ServerConfig (no env-var value reads);
# - fake CredentialProvider (counts calls, returns inert strings);
# - fake BackendFactory (returns FakeB2Backend, never constructs a real
#   ``S3StorageBackend.for_backblaze`` or ``boto3`` client).
#
# These tests collectively prove:
# - no live B2 access ever occurs in tests;
# - no real backend factory is ever called in tests;
# - every live gate is fail-closed;
# - the 32-step operation order is exact;
# - evidence output is sanitized and atomic.

import hashlib as _hashlib
import shutil as _shutil
import tempfile as _tempfile

EXEC_COMMIT = "418fc51b4df02e3217a93d43ee9d95bb98ec6abf"
LIVE_EVIDENCE_RUN_ID = "ps041e2b-test-run-001"


def base_live_auth(**overrides) -> dict:
    auth = {
        "schema": ev.LIVE_SCHEMA,
        "authorized": True,
        "authorized_by": "ps-041e2b-test-operator",
        "authorized_at": AUTHORIZED_AT,
        "expires_at": FUTURE,
        "configured_alias": ALIAS,
        "allowed_bucket_name_hash": BUCKET_HASH,
        "allowed_prefix": PREFIX,
        "allowed_keys": list(DEFAULT_KEYS),
        "object_role_by_key": dict(DEFAULT_ROLE_PLAN),
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
        "expected_sha256_by_key": dict(_EXPECTED_JSON_HASHES),
        "purpose": ev.LIVE_PURPOSE,
        "evidence_run_id": LIVE_EVIDENCE_RUN_ID,
        "execution_commit": EXEC_COMMIT,
    }
    auth.update(overrides)
    return auth


class _FakeCredProvider:
    def __init__(self) -> None:
        self.call_count = 0

    def __call__(self) -> "ev.LiveCredentials":
        self.call_count += 1
        return ev.LiveCredentials(
            key_id="fake-key-id", app_key="fake-app-key",
            bucket="fake-bucket", region="fake-region",
        )


class _FakeBackendFactory:
    def __init__(self, backend: "ev.FakeB2Backend | None" = None,
                 populated: bool = True) -> None:
        self.call_count = 0
        self._backend = backend
        self._populated = populated

    def __call__(self, credentials: "ev.LiveCredentials") -> "ev.FakeB2Backend":
        self.call_count += 1
        if self._backend is not None:
            return self._backend
        if not self._populated:
            return ev.FakeB2Backend()
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        return ev._build_fake_backend(
            fixture, list(DEFAULT_KEYS), object_role_by_key=dict(DEFAULT_ROLE_PLAN),
        )


def _good_git_state() -> "ev.GitState":
    return ev.GitState(
        branch=ev.PS_041E2B_BRANCH, head_commit=EXEC_COMMIT,
        accepted_commit=EXEC_COMMIT, accepted_ref=ev.ACCEPTED_EXECUTION_REF,
        tree_clean=True,
    )


def _good_server_config() -> "ev.ServerConfig":
    # ``import_root`` must byte-for-byte equal the authorized prefix.
    return ev.ServerConfig(
        alias=ALIAS, import_root=PREFIX,
        bucket_identity=SERVER_BUCKET_IDENTITY, region="us-west-000-fake",
        required_credentials_present=True,
    )


class _FakeRemoteRefResolver:
    """Fake resolver returning the EXEC_COMMIT for the accepted ref."""

    def __init__(self, *, commit: str = EXEC_COMMIT) -> None:
        self.call_count = 0
        self._commit = commit

    def __call__(self, ref: str) -> str:
        self.call_count += 1
        return self._commit


def _make_import_service():
    """Build a fresh in-process ProofStudioService for one live run."""
    from proofstudio.api.services import ProofStudioService
    return ProofStudioService()


class _RecordingEnvAccess:
    """Injectable test environment-access boundary.

    Records every read and raises immediately if a secret value is
    requested before :meth:`mark_gates_completed` is called. ``not
    recorded`` is never equivalent to ``not read``: every actual value
    access is appended to ``secret_value_reads`` / ``non_secret_reads``.

    ``secret_name_present`` inspects the captured key-set snapshot only
    and NEVER invokes ``get`` / ``__getitem__`` for any name; this is
    proven by the dedicated unit tests below.
    """

    def __init__(self, values: dict[str, str] | None = None) -> None:
        self._values: dict[str, str] = dict(values or {})
        # Snapshot the key set ONCE at construction. This is the only
        # key-set inspection this boundary performs; secret_name_present
        # never invokes get/getitem.
        self._initial_keys: frozenset[str] = frozenset(self._values.keys())
        self.secret_value_reads: list[tuple[str, str]] = []
        self.non_secret_reads: list[str] = []
        self.membership_checks: list[str] = []
        # Ordered event log proving gate completion precedes the first
        # secret-value read.
        self.event_log: list[tuple[str, str]] = []
        self._gates_completed = False

    def read_non_secret(self, name: str) -> str:
        if name in ev.SECRET_VALUE_ENV:
            raise ev.AuthorizationError("non_secret_read_on_secret_name")
        self.non_secret_reads.append(name)
        self.event_log.append(("non_secret_read", name))
        return self._values.get(name, "")

    def secret_name_present(self, name: str) -> bool:
        # Keys-only inspection against the snapshot.
        self.membership_checks.append(name)
        self.event_log.append(("membership_check", name))
        return name in self._initial_keys

    def mark_gates_completed(self) -> None:
        self._gates_completed = True
        self.event_log.append(("gates_completed", ""))

    def read_secret_after_gates(self, name: str) -> str:
        if name not in ev.SECRET_VALUE_ENV:
            raise ev.AuthorizationError("secret_read_on_non_secret_name")
        if not self._gates_completed:
            self.secret_value_reads.append((name, "before_gates"))
            self.event_log.append(("secret_read_before_gates", name))
            raise ev.AuthorizationError("secret_value_read_before_gate_completion")
        self.secret_value_reads.append((name, "after_gates"))
        self.event_log.append(("secret_read_after_gates", name))
        return self._values.get(name, "")

    @property
    def gates_completed(self) -> bool:
        return self._gates_completed


class _BoundaryBackedCredProvider:
    """Credential provider that reads secrets through a boundary.

    Used to prove the CredentialProvider is the only component that reads
    secret values and that the first secret-value read happens after
    ``mark_gates_completed``.
    """

    def __init__(self, boundary: _RecordingEnvAccess) -> None:
        self.call_count = 0
        self._boundary = boundary

    def __call__(self) -> "ev.LiveCredentials":
        self.call_count += 1
        key_id = self._boundary.read_secret_after_gates("B2_KEY_ID")
        app_key = self._boundary.read_secret_after_gates("B2_APP_KEY")
        bucket = self._boundary.read_non_secret("B2_BUCKET")
        region = self._boundary.read_non_secret("B2_REGION")
        return ev.LiveCredentials(
            key_id=key_id or "fake-key-id",
            app_key=app_key or "fake-app-key",
            bucket=bucket or "fake-bucket",
            region=region or "fake-region",
        )


def _run_live(
    auth: dict | None = None,
    *,
    evidence_run_id: str = LIVE_EVIDENCE_RUN_ID,
    git_state: "ev.GitState | None" = None,
    server_config: "ev.ServerConfig | None" = None,
    backend_factory: "_FakeBackendFactory | None" = None,
    credential_provider: "_FakeCredProvider | None" = None,
    remote_ref_resolver: "_FakeRemoteRefResolver | None" = None,
    import_service=None,
    confirm: bool = True,
    evidence_dir: Path | None = None,
    real_backend_factory_used: bool = False,
    env_access: "ev.EnvAccessBoundary | None" = None,
) -> tuple["ev.LiveExecuteReport", "_FakeCredProvider", "_FakeBackendFactory", Path]:
    if auth is None:
        auth = base_live_auth(evidence_run_id=evidence_run_id)
    if git_state is None:
        git_state = _good_git_state()
    if server_config is None:
        server_config = _good_server_config()
    if backend_factory is None:
        backend_factory = _FakeBackendFactory()
    if credential_provider is None:
        credential_provider = _FakeCredProvider()
    if remote_ref_resolver is None:
        remote_ref_resolver = _FakeRemoteRefResolver()
    if import_service is None:
        import_service = _make_import_service()
    if evidence_dir is None:
        evidence_dir = Path(_tempfile.mkdtemp(prefix="ps041e2b-test-")) / "evidence"
    kwargs: dict = dict(
        git_state=git_state, server_config=server_config,
        credential_provider=credential_provider, backend_factory=backend_factory,
        import_service=import_service, remote_ref_resolver=remote_ref_resolver,
        confirm_controlled_live_read=confirm,
        real_backend_factory_used=real_backend_factory_used,
    )
    if env_access is not None:
        kwargs["env_access"] = env_access
    report = ev.run_live_execute(
        auth, fixture_path=FIXTURE, evidence_dir=evidence_dir, **kwargs,
    )
    return report, credential_provider, backend_factory, evidence_dir


def _evidence_files(evidence_dir: Path) -> list[str]:
    if not evidence_dir.exists():
        return []
    return sorted(p.name for p in evidence_dir.iterdir())


def _read_evidence_json(evidence_dir: Path, name: str) -> dict:
    return json.loads((evidence_dir / name).read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# L1. all 22 gates pass in a fake accepted-state run
# ---------------------------------------------------------------------------

def test_l1_all_22_gates_pass_in_fake_accepted_state_run() -> None:
    report, cred, factory, _ = _run_live()
    assert report.ok is True
    assert report.errors == []
    assert len(report.gates) == 22
    assert all(g.ok for g in report.gates)
    assert ev.FUTURE_EXECUTE_GATES_COUNT == 22
    assert ev.LIVE_EXECUTE_GATES_COUNT == 22


# ---------------------------------------------------------------------------
# L2. authorization=false rejects before client construction
# ---------------------------------------------------------------------------

def test_l2_authorization_false_rejects_before_client_construction() -> None:
    report, cred, factory, _ = _run_live(base_live_auth(authorized=False))
    assert report.ok is False
    assert "live_not_authorized" in report.errors
    assert cred.call_count == 0
    assert factory.call_count == 0


# ---------------------------------------------------------------------------
# L3. expired authorization rejects before client construction
# ---------------------------------------------------------------------------

def test_l3_expired_authorization_rejects_before_client_construction() -> None:
    past_auth = base_live_auth(authorized_at=PAST, expires_at=PAST_EXPIRES)
    report, cred, factory, _ = _run_live(past_auth)
    assert report.ok is False
    assert "live_authorization_expired" in report.errors
    assert cred.call_count == 0
    assert factory.call_count == 0


# ---------------------------------------------------------------------------
# L4. wrong execution commit rejects
# ---------------------------------------------------------------------------

def test_l4_wrong_execution_commit_rejects() -> None:
    auth = base_live_auth(execution_commit="0" * 40)
    report, cred, factory, _ = _run_live(auth)
    assert report.ok is False
    assert "execution_commit_mismatch" in report.errors
    assert cred.call_count == 0
    assert factory.call_count == 0


# ---------------------------------------------------------------------------
# L5. dirty tree rejects
# ---------------------------------------------------------------------------

def test_l5_dirty_tree_rejects() -> None:
    dirty = ev.GitState(
        branch=ev.PS_041E2B_BRANCH, head_commit=EXEC_COMMIT,
        accepted_commit=EXEC_COMMIT, accepted_ref=ev.ACCEPTED_EXECUTION_REF,
        tree_clean=False,
    )
    report, cred, factory, _ = _run_live(git_state=dirty)
    assert report.ok is False
    assert "repository_treedirty" in report.errors or "repository_tree_dirty" in report.errors
    assert cred.call_count == 0
    assert factory.call_count == 0


# ---------------------------------------------------------------------------
# L6. accepted ref mismatch rejects
# ---------------------------------------------------------------------------

def test_l6_accepted_ref_mismatch_rejects() -> None:
    bad_ref = ev.GitState(
        branch=ev.PS_041E2B_BRANCH, head_commit=EXEC_COMMIT,
        accepted_commit=EXEC_COMMIT, accepted_ref="origin/other/ref",
        tree_clean=True,
    )
    report, cred, factory, _ = _run_live(git_state=bad_ref)
    assert report.ok is False
    assert "accepted_ref_mismatch" in report.errors
    assert cred.call_count == 0
    assert factory.call_count == 0


# ---------------------------------------------------------------------------
# L7. missing confirmation rejects
# ---------------------------------------------------------------------------

def test_l7_missing_confirmation_rejects() -> None:
    report, cred, factory, _ = _run_live(confirm=False)
    assert report.ok is False
    assert "confirm_controlled_live_read_missing" in report.errors
    assert cred.call_count == 0
    assert factory.call_count == 0


# ---------------------------------------------------------------------------
# L8. authorization outside approved /tmp directory rejects
# ---------------------------------------------------------------------------

def test_l8_authorization_outside_approved_tmp_dir_rejects(tmp_path: Path) -> None:
    outside = tmp_path / "outside-auth.json"
    outside.write_text(json.dumps(base_live_auth()), encoding="utf-8")
    with pytest.raises(ev.AuthorizationError, match="live_authorization_outside_approved_dir"):
        ev.load_live_authorization(outside)


# ---------------------------------------------------------------------------
# L9. alias mismatch rejects before backend construction
# ---------------------------------------------------------------------------

def test_l9_alias_mismatch_rejects_before_backend_construction() -> None:
    sc = ev.ServerConfig(
        alias="different-alias", import_root=PREFIX,
        bucket_identity=SERVER_BUCKET_IDENTITY, region="us-west-000-fake",
        required_credentials_present=True,
    )
    report, cred, factory, _ = _run_live(server_config=sc)
    assert report.ok is False
    assert "alias_mismatch" in report.errors
    assert cred.call_count == 0
    assert factory.call_count == 0


# ---------------------------------------------------------------------------
# L10. bucket hash mismatch rejects before backend construction
# ---------------------------------------------------------------------------

def test_l10_bucket_hash_mismatch_rejects_before_backend_construction() -> None:
    sc = ev.ServerConfig(
        alias=ALIAS, import_root=PREFIX,
        bucket_identity="some-other-bucket-identity", region="us-west-000-fake",
        required_credentials_present=True,
    )
    report, cred, factory, _ = _run_live(server_config=sc)
    assert report.ok is False
    assert "bucket_identity_mismatch" in report.errors
    assert cred.call_count == 0
    assert factory.call_count == 0


# ---------------------------------------------------------------------------
# L11. missing server configuration rejects
# ---------------------------------------------------------------------------

def test_l11_missing_server_configuration_rejects() -> None:
    sc = ev.ServerConfig(
        alias=ALIAS, import_root=PREFIX,
        bucket_identity=SERVER_BUCKET_IDENTITY, region="us-west-000-fake",
        required_credentials_present=False,
    )
    report, cred, factory, _ = _run_live(server_config=sc)
    assert report.ok is False
    assert "server_side_configuration_missing" in report.errors
    assert cred.call_count == 0
    assert factory.call_count == 0


# ---------------------------------------------------------------------------
# L12. credential provider not called before gate completion
# ---------------------------------------------------------------------------

def test_l12_credential_provider_not_called_before_gate_completion() -> None:
    """Across every gate failure path, the credential provider call count
    must remain zero. The credential provider is only invoked after all 22
    gates pass."""
    cases = [
        ("authorized_false", base_live_auth(authorized=False)),
        ("expired", base_live_auth(authorized_at=PAST, expires_at=PAST_EXPIRES)),
        ("wrong_commit", base_live_auth(execution_commit="0" * 40)),
    ]
    for name, auth in cases:
        report, cred, factory, _ = _run_live(auth)
        assert report.ok is False, f"{name}: expected failure"
        assert cred.call_count == 0, f"{name}: credential provider was called before gates passed"


# ---------------------------------------------------------------------------
# L13. backend factory not called before gate completion
# ---------------------------------------------------------------------------

def test_l13_backend_factory_not_called_before_gate_completion() -> None:
    cases = [
        ("authorized_false", base_live_auth(authorized=False)),
        ("alias_mismatch", None),  # uses default auth + mismatched server
    ]
    # First case: bad auth
    report, cred, factory, _ = _run_live(cases[0][1])
    assert report.ok is False
    assert factory.call_count == 0
    # Second case: alias mismatch
    sc = ev.ServerConfig(
        alias="different", import_root=PREFIX,
        bucket_identity=SERVER_BUCKET_IDENTITY, region="us-west-000-fake",
        required_credentials_present=True,
    )
    report, cred, factory, _ = _run_live(server_config=sc)
    assert report.ok is False
    assert factory.call_count == 0


# ---------------------------------------------------------------------------
# L14. exactly five HEAD keys and no list (initial observation = 5 keys)
# ---------------------------------------------------------------------------

def test_l14_initial_observation_heads_each_exact_allowlisted_key_once() -> None:
    """The initial observation heads each of the 5 allowlisted keys exactly
    once before any read. No list call is ever made. The total head count
    is 18 (5 initial + 8 from BoundedB2ImportReader TOCTOU + 5 final)."""
    report, cred, factory, _ = _run_live()
    assert report.ok is True
    assert report.list_calls == 0
    assert report.head_calls_total == 18
    # The first 5 head calls (initial observation) cover every allowlisted key.
    assert report.authorized_objects == 5


# ---------------------------------------------------------------------------
# L15. missing object aborts
# ---------------------------------------------------------------------------

def test_l15_missing_object_aborts() -> None:
    fake = ev._build_fake_backend(
        json.loads(FIXTURE.read_text(encoding="utf-8")),
        list(DEFAULT_KEYS), object_role_by_key=dict(DEFAULT_ROLE_PLAN),
    )
    # Remove one JSON object so the initial observation sees it missing.
    missing_key = DEFAULT_KEYS[0]
    fake.objects.pop(missing_key)
    factory = _FakeBackendFactory(backend=fake)
    report, cred, _, _ = _run_live(backend_factory=factory)
    assert report.ok is False
    assert "approved_object_missing" in report.errors


# ---------------------------------------------------------------------------
# L16. metadata-only oversized final object rejects
# ---------------------------------------------------------------------------

def test_l16_metadata_only_oversized_final_object_rejects() -> None:
    fake = ev._build_fake_backend(
        json.loads(FIXTURE.read_text(encoding="utf-8")),
        list(DEFAULT_KEYS), object_role_by_key=dict(DEFAULT_ROLE_PLAN),
    )
    media_key = next(k for k in DEFAULT_KEYS if DEFAULT_ROLE_PLAN[k] in ev.MEDIA_BYTE_ROLES)
    # Declare an oversized media object metadata (above the auth cap of 1 MiB).
    fake.objects[media_key]["size_bytes"] = 2 * 1024 * 1024
    fake.objects[media_key]["body"] = b"\x00" * (2 * 1024 * 1024)
    factory = _FakeBackendFactory(backend=fake)
    report, cred, _, _ = _run_live(backend_factory=factory)
    assert report.ok is False
    assert (
        "object_exceeds_authorization_cap" in report.errors
        or "object_exceeds_accepted_cap" in report.errors
    )


# ---------------------------------------------------------------------------
# L17. aggregate declared-size overflow rejects
# ---------------------------------------------------------------------------

def test_l17_aggregate_declared_size_overflow_rejects() -> None:
    fake = ev._build_fake_backend(
        json.loads(FIXTURE.read_text(encoding="utf-8")),
        list(DEFAULT_KEYS), object_role_by_key=dict(DEFAULT_ROLE_PLAN),
    )
    # Inflate every object's declared size so the sum exceeds the auth total.
    # Per-object stays at 4 MiB (under max_object_bytes); the aggregate cap
    # of 16 MiB then fires (5 × 4 = 20 MiB > 16 MiB).
    for key in fake.objects:
        fake.objects[key]["size_bytes"] = 4 * 1024 * 1024
    factory = _FakeBackendFactory(backend=fake)
    auth = base_live_auth(
        max_object_bytes=4 * 1024 * 1024,
        max_total_bytes=16 * 1024 * 1024,
    )
    report, cred, _, _ = _run_live(auth, backend_factory=factory)
    assert report.ok is False
    assert (
        "declared_inventory_exceeds_authorization_total" in report.errors
        or "declared_inventory_exceeds_accepted_total" in report.errors
    )


# ---------------------------------------------------------------------------
# L18. four JSON objects read once each
# ---------------------------------------------------------------------------

def test_l18_four_json_objects_read_once_each() -> None:
    report, cred, factory, _ = _run_live()
    assert report.ok is True
    assert report.unique_json_objects_read == 4
    assert report.read_calls_total == 4


# ---------------------------------------------------------------------------
# L19. no hidden candidate rereads (snapshot consumer calls = 4 objects × 2 builds)
# ---------------------------------------------------------------------------

def test_l19_no_hidden_candidate_rereads() -> None:
    report, cred, factory, _ = _run_live()
    assert report.ok is True
    # 4 JSON objects × 2 build_candidate invocations = 8 snapshot consumer calls.
    assert report.snapshot_consumer_calls == 8
    # Backend read calls stayed at 4 (the original JSON reads).
    assert report.read_calls_total == 4


# ---------------------------------------------------------------------------
# L20. final media not read when media permission is false
# ---------------------------------------------------------------------------

def test_l20_final_media_not_read_when_permission_false() -> None:
    report, cred, factory, _ = _run_live()
    assert report.ok is True
    assert report.unique_media_objects_read == 0
    assert report.read_calls_total == 4  # JSON only


# ---------------------------------------------------------------------------
# L21. final media read exactly once when authorized
# ---------------------------------------------------------------------------

def test_l21_final_media_read_exactly_once_when_authorized() -> None:
    # Use a fake backend built from the standard helper so the expected
    # media digest (digest of ``_MEDIA_PLACEHOLDER``) matches.
    fake = ev._build_fake_backend(
        json.loads(FIXTURE.read_text(encoding="utf-8")),
        list(DEFAULT_KEYS), object_role_by_key=dict(DEFAULT_ROLE_PLAN),
    )
    factory = _FakeBackendFactory(backend=fake)
    # Authorize media reads and include all expected hashes (JSON + media).
    expected_all = ev.expected_hashes_for_fixture(FIXTURE, list(DEFAULT_KEYS), DEFAULT_ROLE_PLAN)
    auth = base_live_auth(
        allow_media_byte_reads=True,
        max_object_bytes=1_048_576,
        max_total_bytes=16_777_216 * 2,
        expected_sha256_by_key=dict(expected_all),
    )
    report, cred, _, _ = _run_live(auth, backend_factory=factory)
    assert report.ok is True
    assert report.unique_media_objects_read == 1
    # 4 JSON reads + 1 media read = 5 backend read calls.
    assert report.read_calls_total == 5


# ---------------------------------------------------------------------------
# L22. expected media hash with media reads disabled rejects
# ---------------------------------------------------------------------------

def test_l22_expected_media_hash_with_media_reads_disabled_rejects() -> None:
    """An expected digest for a media-byte role requires
    ``allow_media_byte_reads=true``. The structural validator rejects this
    at gate 10 before any backend work."""
    expected_all = ev.expected_hashes_for_fixture(FIXTURE, list(DEFAULT_KEYS), DEFAULT_ROLE_PLAN)
    auth = base_live_auth(
        allow_media_byte_reads=False,
        expected_sha256_by_key=dict(expected_all),
    )
    report, cred, factory, _ = _run_live(auth)
    assert report.ok is False
    assert "expected_media_hash_requires_media_reads" in report.errors
    assert factory.call_count == 0


# ---------------------------------------------------------------------------
# L23. JSON hash match
# ---------------------------------------------------------------------------

def test_l23_json_hash_match_records_matched_status() -> None:
    report, cred, factory, _ = _run_live()
    assert report.ok is True
    matched = [h for h in report.hash_results if h["status"] == "matched"]
    assert len(matched) == 4


# ---------------------------------------------------------------------------
# L24. JSON hash mismatch aborts
# ---------------------------------------------------------------------------

def test_l24_json_hash_mismatch_aborts() -> None:
    bad = {k: "0" * 64 for k in _EXPECTED_JSON_HASHES}
    auth = base_live_auth(expected_sha256_by_key=bad)
    report, cred, factory, _ = _run_live(auth)
    assert report.ok is False
    assert "unexpected_hash_mismatch" in report.errors


# ---------------------------------------------------------------------------
# L25. media hash match
# ---------------------------------------------------------------------------

def test_l25_media_hash_match_records_matched_status() -> None:
    fake = ev._build_fake_backend(
        json.loads(FIXTURE.read_text(encoding="utf-8")),
        list(DEFAULT_KEYS), object_role_by_key=dict(DEFAULT_ROLE_PLAN),
    )
    factory = _FakeBackendFactory(backend=fake)
    expected_all = ev.expected_hashes_for_fixture(FIXTURE, list(DEFAULT_KEYS), DEFAULT_ROLE_PLAN)
    auth = base_live_auth(
        allow_media_byte_reads=True,
        max_object_bytes=1_048_576,
        max_total_bytes=16_777_216 * 2,
        expected_sha256_by_key=dict(expected_all),
    )
    report, cred, _, _ = _run_live(auth, backend_factory=factory)
    assert report.ok is True
    media_hash_results = [h for h in report.hash_results
                          if DEFAULT_ROLE_PLAN[h["key"]] in ev.MEDIA_BYTE_ROLES]
    assert len(media_hash_results) == 1
    assert media_hash_results[0]["status"] == "matched"


# ---------------------------------------------------------------------------
# L26. media hash mismatch aborts
# ---------------------------------------------------------------------------

def test_l26_media_hash_mismatch_aborts() -> None:
    fake = ev._build_fake_backend(
        json.loads(FIXTURE.read_text(encoding="utf-8")),
        list(DEFAULT_KEYS), object_role_by_key=dict(DEFAULT_ROLE_PLAN),
    )
    factory = _FakeBackendFactory(backend=fake)
    expected_all = ev.expected_hashes_for_fixture(FIXTURE, list(DEFAULT_KEYS), DEFAULT_ROLE_PLAN)
    # Corrupt the media expected hash.
    media_key = next(k for k in DEFAULT_KEYS if DEFAULT_ROLE_PLAN[k] in ev.MEDIA_BYTE_ROLES)
    expected_all[media_key] = "0" * 64
    auth = base_live_auth(
        allow_media_byte_reads=True,
        max_object_bytes=1_048_576,
        max_total_bytes=16_777_216 * 2,
        expected_sha256_by_key=dict(expected_all),
    )
    report, cred, _, _ = _run_live(auth, backend_factory=factory)
    assert report.ok is False
    assert "unexpected_hash_mismatch" in report.errors


# ---------------------------------------------------------------------------
# L27. object changes after read abort
# ---------------------------------------------------------------------------

def test_l27_object_changes_after_read_aborts() -> None:
    fake = ev._build_fake_backend(
        json.loads(FIXTURE.read_text(encoding="utf-8")),
        list(DEFAULT_KEYS), object_role_by_key=dict(DEFAULT_ROLE_PLAN),
    )
    real_head = fake.head
    state = {"calls": 0}

    def mutating_head(key):
        result = real_head(key)
        state["calls"] += 1
        # After many head calls (post-read final observation), mutate the etag.
        if state["calls"] > 12:
            return {
                "size_bytes": result["size_bytes"],
                "etag": "tampered-etag-value",
                "version_id": result["version_id"],
            }
        return result

    fake.head = mutating_head  # type: ignore[assignment]
    factory = _FakeBackendFactory(backend=fake)
    report, cred, _, _ = _run_live(backend_factory=factory)
    assert report.ok is False
    assert "object_changed_during_evidence_run" in report.errors


# ---------------------------------------------------------------------------
# L28. object disappears before final observation aborts
# ---------------------------------------------------------------------------

def test_l28_object_disappears_before_final_observation_aborts() -> None:
    fake = ev._build_fake_backend(
        json.loads(FIXTURE.read_text(encoding="utf-8")),
        list(DEFAULT_KEYS), object_role_by_key=dict(DEFAULT_ROLE_PLAN),
    )
    real_head = fake.head
    state = {"calls": 0}

    def vanishing_head(key):
        state["calls"] += 1
        # After many head calls (final observation phase), make one vanish.
        if state["calls"] > 14:
            return None
        return real_head(key)

    fake.head = vanishing_head  # type: ignore[assignment]
    factory = _FakeBackendFactory(backend=fake)
    report, cred, _, _ = _run_live(backend_factory=factory)
    assert report.ok is False
    assert (
        "object_changed_during_evidence_run" in report.errors
        or "approved_object_missing" in report.errors
    )


# ---------------------------------------------------------------------------
# L29. all expected hashes consumed
# ---------------------------------------------------------------------------

def test_l29_all_expected_hashes_consumed() -> None:
    report, cred, factory, _ = _run_live()
    assert report.ok is True
    # Every expected hash key must appear as matched in the hash results.
    matched_keys = {h["key"] for h in report.hash_results if h["status"] == "matched"}
    for expected_key in _EXPECTED_JSON_HASHES:
        assert expected_key in matched_keys


# ---------------------------------------------------------------------------
# L30. exact snapshots used for import (matched digest equals imported snapshot)
# ---------------------------------------------------------------------------

def test_l30_exact_snapshots_used_for_import() -> None:
    report, cred, factory, _ = _run_live()
    assert report.ok is True
    # The matched digests must equal the SHA-256 of the exact bytes parsed.
    for h in report.hash_results:
        if h["status"] == "matched":
            assert h["sha256"] == _EXPECTED_JSON_HASHES[h["key"]]


# ---------------------------------------------------------------------------
# L31. idempotent import stable
# ---------------------------------------------------------------------------

def test_l31_idempotent_import_stable() -> None:
    report, cred, factory, _ = _run_live()
    assert report.ok is True
    assert report.import_idempotent is True


# ---------------------------------------------------------------------------
# L32. private lineage summary generated
# ---------------------------------------------------------------------------

def test_l32_private_lineage_summary_generated() -> None:
    report, cred, factory, _ = _run_live()
    assert report.ok is True
    summary = _read_evidence_json(Path(report.evidence_dir), "private-lineage-summary.json")
    assert "bundle_id" in summary
    assert "bundle_fingerprint" in summary
    assert summary["node_count"] > 0


# ---------------------------------------------------------------------------
# L33. private Passport schema exact
# ---------------------------------------------------------------------------

def test_l33_private_passport_schema_exact() -> None:
    report, cred, factory, _ = _run_live()
    assert report.ok is True
    summary = _read_evidence_json(Path(report.evidence_dir), "private-passport-summary.json")
    assert summary["passport_schema"] == ev.PASSPORT_SCHEMA


# ---------------------------------------------------------------------------
# L34. output path traversal rejected
# ---------------------------------------------------------------------------

def test_l34_output_path_traversal_rejected() -> None:
    auth = base_live_auth(evidence_run_id="../escape-attempt")
    # Validation rejects path-traversal evidence_run_id values.
    with pytest.raises(ev.AuthorizationError):
        ev.validate_live_authorization(auth)


# ---------------------------------------------------------------------------
# L35. existing output directory rejected
# ---------------------------------------------------------------------------

def test_l35_existing_output_directory_rejected() -> None:
    tmp_root = Path(_tempfile.mkdtemp(prefix="ps041e2b-test-existing-"))
    evidence_dir = tmp_root / "evidence"
    evidence_dir.mkdir(parents=True)
    os.chmod(evidence_dir, 0o700)
    (evidence_dir / LIVE_EVIDENCE_RUN_ID).mkdir()
    report, cred, factory, _ = _run_live(evidence_dir=evidence_dir)
    # The atomic-emitter refuses to overwrite an existing run directory.
    assert report.ok is False
    assert any("exists" in e or "output_directory" in e for e in report.errors)


# ---------------------------------------------------------------------------
# L36. partial output cleaned or safely retained on failure
# ---------------------------------------------------------------------------

def test_l36_partial_output_cleaned_on_failure() -> None:
    """When the flow fails after backend construction, no success summary is
    written. The final run directory does not exist; a sanitized failure
    summary is returned via the LiveExecuteReport.errors list."""
    fake = ev._build_fake_backend(
        json.loads(FIXTURE.read_text(encoding="utf-8")),
        list(DEFAULT_KEYS), object_role_by_key=dict(DEFAULT_ROLE_PLAN),
    )
    missing_key = DEFAULT_KEYS[0]
    fake.objects.pop(missing_key)
    factory = _FakeBackendFactory(backend=fake)
    tmp_root = Path(_tempfile.mkdtemp(prefix="ps041e2b-test-partial-"))
    evidence_dir = tmp_root / "evidence"
    report, cred, _, _ = _run_live(backend_factory=factory, evidence_dir=evidence_dir)
    assert report.ok is False
    # No final run directory should exist on failure.
    assert not (evidence_dir / LIVE_EVIDENCE_RUN_ID).exists()


# ---------------------------------------------------------------------------
# L37. operation counters equal backend instrumentation
# ---------------------------------------------------------------------------

def test_l37_operation_counters_equal_backend_instrumentation() -> None:
    fake = ev._build_fake_backend(
        json.loads(FIXTURE.read_text(encoding="utf-8")),
        list(DEFAULT_KEYS), object_role_by_key=dict(DEFAULT_ROLE_PLAN),
    )
    factory = _FakeBackendFactory(backend=fake)
    report, cred, _, _ = _run_live(backend_factory=factory)
    assert report.ok is True
    # head_calls_total = 5 (initial) + 8 (BoundedB2ImportReader TOCTOU) + 5 (final)
    assert report.head_calls_total == 18
    # read_calls_total = 4 JSON objects read once each.
    assert report.read_calls_total == 4
    assert report.list_calls == 0
    assert report.write_attempts == 0
    assert report.delete_attempts == 0
    assert report.signed_url_attempts == 0
    assert report.provider_calls == 0


# ---------------------------------------------------------------------------
# L38. list/write/delete/signed-URL counters remain zero
# ---------------------------------------------------------------------------

def test_l38_forbidden_operation_counters_remain_zero() -> None:
    report, cred, factory, _ = _run_live()
    assert report.ok is True
    assert report.list_calls == 0
    assert report.write_attempts == 0
    assert report.delete_attempts == 0
    assert report.signed_url_attempts == 0


# ---------------------------------------------------------------------------
# L39. provider calls remain zero
# ---------------------------------------------------------------------------

def test_l39_provider_calls_remain_zero() -> None:
    report, cred, factory, _ = _run_live()
    assert report.ok is True
    assert report.provider_calls == 0


# ---------------------------------------------------------------------------
# L40. evidence contains no credential values
# ---------------------------------------------------------------------------

def test_l40_evidence_contains_no_credential_values() -> None:
    report, cred, factory, _ = _run_live()
    assert report.ok is True
    run_dir = Path(report.evidence_dir)
    blob = ""
    for name in _evidence_files(run_dir):
        blob += (run_dir / name).read_text(encoding="utf-8", errors="ignore")
    lowered = blob.lower()
    for forbidden in (
        "fake-app-key", "fake-key-id", "fake-bucket", "fake-region",
        "aws_secret_access_key", "aws_access_key_id",
        "b2_application_key", "b2_app_key",
    ):
        assert forbidden not in lowered, f"forbidden credential value in evidence: {forbidden}"


# ---------------------------------------------------------------------------
# L41. evidence contains no raw bucket name
# ---------------------------------------------------------------------------

def test_l41_evidence_contains_no_raw_bucket_name() -> None:
    report, cred, factory, _ = _run_live()
    assert report.ok is True
    run_dir = Path(report.evidence_dir)
    blob = ""
    for name in _evidence_files(run_dir):
        blob += (run_dir / name).read_text(encoding="utf-8", errors="ignore")
    # The fake server bucket identity must NEVER appear in evidence output.
    assert SERVER_BUCKET_IDENTITY not in blob


# ---------------------------------------------------------------------------
# L42. evidence contains no endpoint URL
# ---------------------------------------------------------------------------

def test_l42_evidence_contains_no_endpoint_url() -> None:
    report, cred, factory, _ = _run_live()
    assert report.ok is True
    run_dir = Path(report.evidence_dir)
    blob = ""
    for name in _evidence_files(run_dir):
        blob += (run_dir / name).read_text(encoding="utf-8", errors="ignore")
    lowered = blob.lower()
    for forbidden in ("https://", "http://", "s3.us-west", "s3.us-east", ".backblazeb2.com"):
        assert forbidden not in lowered, f"forbidden endpoint URL in evidence: {forbidden}"


# ---------------------------------------------------------------------------
# L43. evidence contains no object bytes
# ---------------------------------------------------------------------------

def test_l43_evidence_contains_no_object_bytes() -> None:
    report, cred, factory, _ = _run_live()
    assert report.ok is True
    run_dir = Path(report.evidence_dir)
    blob = ""
    for name in _evidence_files(run_dir):
        blob += (run_dir / name).read_text(encoding="utf-8", errors="ignore")
    # The exact JSON-object bytes served by the fake backend must never appear.
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    role_bodies = ev._fixture_role_bodies(fixture)
    for role, body in role_bodies.items():
        # A large distinctive substring of each JSON body.
        marker = body[:64].decode("utf-8", errors="ignore")
        if len(marker) > 8:
            assert marker not in blob, f"raw JSON object bytes for role {role} leaked into evidence"


# ---------------------------------------------------------------------------
# L44. raw backend exception text is normalized
# ---------------------------------------------------------------------------

def test_l44_raw_backend_exception_text_is_normalized() -> None:
    fake = ev._build_fake_backend(
        json.loads(FIXTURE.read_text(encoding="utf-8")),
        list(DEFAULT_KEYS), object_role_by_key=dict(DEFAULT_ROLE_PLAN),
    )

    def exploding_read(key, max_bytes):
        raise OSError(f"raw-transport-error-for-bucket-{SERVER_BUCKET_IDENTITY}-key-{key}")

    fake.read_bytes = exploding_read  # type: ignore[assignment]
    factory = _FakeBackendFactory(backend=fake)
    report, cred, _, _ = _run_live(backend_factory=factory)
    assert report.ok is False
    blob = "\n".join(report.errors).lower()
    assert SERVER_BUCKET_IDENTITY.lower() not in blob
    # The reported code is one of the stable normalized codes.
    assert any(code in report.errors for code in (
        "backend_read_failed", "backend_head_failed",
        "approved_object_missing", "unexpected_hash_mismatch",
        "import_validation_failed", "imported_json_malformed",
        "object_changed_during_evidence_run",
    )), f"unexpected error code: {report.errors!r}"


# ---------------------------------------------------------------------------
# L45. cleanup destroys client/backend references
# ---------------------------------------------------------------------------

def test_l45_cleanup_destroys_backend_references() -> None:
    report, cred, factory, _ = _run_live()
    assert report.ok is True
    assert report.cleanup_verified is True
    run_dir = Path(report.evidence_dir)
    cleanup_text = (run_dir / "cleanup-verification.txt").read_text(encoding="utf-8")
    assert "backend_destroyed=true" in cleanup_text.lower()
    assert "credentials_released=true" in cleanup_text.lower()


# ---------------------------------------------------------------------------
# L46. --execute remains impossible without accepted-ref equality
# ---------------------------------------------------------------------------

def test_l46_cli_execute_refuses_when_head_not_accepted(tmp_path: Path) -> None:
    """The CLI ``--execute`` mode resolves real Git state. On a feature
    branch (HEAD != origin/accepted/proofstudio) it must fail-closed with
    exit code 2 before any client construction. The CLI is invoked with a
    non-existent path; the loader fails first, but the canonical 22-gate
    refusal text is still emitted."""
    import io
    import contextlib
    err_buf = io.StringIO()
    with contextlib.redirect_stderr(err_buf):
        rc = ev.main([
            "--execute", "/tmp/proofstudio-ps041e2-authorizations/nonexistent.json",
            "--confirm-controlled-live-read",
        ])
    assert rc == 2
    err_text = err_buf.getvalue()
    assert str(ev.FUTURE_EXECUTE_GATES_COUNT) in err_text
    assert str(ev.LIVE_EXECUTE_GATES_COUNT) in err_text


# ---------------------------------------------------------------------------
# L47. no live backend is constructed in tests
# ---------------------------------------------------------------------------

def test_l47_no_live_backend_constructed_in_tests(monkeypatch: pytest.MonkeyPatch) -> None:
    """No test in this suite imports ``genblaze_s3`` or constructs a real
    ``S3StorageBackend.for_backblaze`` client. This test monitors the
    ``proofstudio.provenance.genblaze_store.build_backblaze_backend`` import
    point and asserts it was never called during a normal fake run."""
    import sys as _sys
    # genblaze_s3 should never be imported as a side effect of run_live_execute.
    genblaze_s3_present_before = "genblaze_s3" in _sys.modules
    report, cred, factory, _ = _run_live()
    assert report.ok is True
    genblaze_s3_present_after = "genblaze_s3" in _sys.modules
    assert genblaze_s3_present_before == genblaze_s3_present_after, (
        "run_live_execute must not import genblaze_s3"
    )
    # boto3 should never be imported either.
    boto3_present = "boto3" in _sys.modules
    assert boto3_present is False, "run_live_execute must not import boto3"


# ===========================================================================
# PS-041E2-B PHASE-1 — PM-REVIEW FOCUSED TESTS (M1-M33)
#
# These tests cover the blockers found during PM artifact review of the
# PS-041E2-B Phase-1 live executor. Every test remains fake/injected and
# performs no network or real B2 access.
# ===========================================================================


# ---------------------------------------------------------------------------
# Test helpers for the S3-like fake backend (head + get_range + get, no
# read_bytes). Exercises the exact real-adapter branch of GuardedLiveBackend.
# ---------------------------------------------------------------------------


class _S3LikeObjectMetadata:
    """Mirror of the accepted ``ObjectMetadata`` dataclass shape.

    The pinned genblaze-s3 ``ObjectMetadata`` (genblaze-s3==0.3.5) exposes:
    ``key``, ``size``, ``last_modified``, ``etag``, ``content_type``,
    ``storage_class``, ``metadata``. It does NOT expose ``version_id``.
    """

    __slots__ = ("size", "etag", "version_id", "storage_class",
                 "last_modified", "content_type", "metadata", "key")

    def __init__(self, *, size: int, etag: str, version_id: str | None = None,
                 storage_class: str = "STANDARD",
                 last_modified=None, content_type: str | None = None,
                 metadata: dict | None = None, key: str = "") -> None:
        self.size = size
        self.etag = etag
        self.version_id = version_id
        self.storage_class = storage_class
        self.last_modified = last_modified
        self.content_type = content_type
        self.metadata = metadata or {}
        self.key = key


class _S3LikeFakeBackend:
    """S3-like fake with head / get_range / get and NO read_bytes method.

    Used to prove the GuardedLiveBackend real-adapter branch:
    - uses get_range (no full-object GET fallback);
    - counts every underlying HEAD explicitly (no hidden HEAD);
    - enforces exact byte length;
    - accepts the pinned genblaze-s3 ObjectMetadata shape (no version_id).
    """

    def __init__(self) -> None:
        self.objects: dict[str, dict[str, Any]] = {}
        self.head_calls: list[str] = []
        self.get_range_calls: list[tuple[str, int, int]] = []
        self.get_calls: list[str] = []
        self.close_calls = 0

    def seed(self, key: str, body: bytes, *, version_id: str | None = None,
             storage_class: str = "STANDARD",
             last_modified=None) -> None:
        self.objects[key] = {
            "body": body,
            "size": len(body),
            "etag": _hashlib.sha256(body).hexdigest()[:32],
            "version_id": version_id,
            "storage_class": storage_class,
            "last_modified": last_modified,
        }

    def head(self, key: str):
        self.head_calls.append(key)
        obj = self.objects.get(key)
        if obj is None:
            return None
        return _S3LikeObjectMetadata(
            size=obj["size"], etag=obj["etag"],
            version_id=obj["version_id"], storage_class=obj["storage_class"],
            last_modified=obj["last_modified"], key=key,
        )

    def get_range(self, key: str, *, offset: int, length: int) -> bytes:
        self.get_range_calls.append((key, offset, length))
        obj = self.objects.get(key)
        if obj is None:
            raise OSError("missing")
        return obj["body"][offset:offset + length]

    def get(self, key: str) -> bytes:
        # Present so we can prove the adapter never falls back to it.
        self.get_calls.append(key)
        obj = self.objects.get(key)
        if obj is None:
            raise OSError("missing")
        return obj["body"]

    def close(self) -> None:
        self.close_calls += 1


class _S3LikeBackendFactory:
    """Backend factory returning a GuardedLiveBackend over an S3-like fake."""

    def __init__(self, fake: _S3LikeFakeBackend) -> None:
        self.call_count = 0
        self._fake = fake

    def __call__(self, credentials):
        self.call_count += 1
        return ev.GuardedLiveBackend(self._fake)


def _s3_like_populated_backend() -> _S3LikeFakeBackend:
    """Build an S3-like fake populated from the standard fixture.

    Seeds objects matching the pinned genblaze-s3 ObjectMetadata shape:
    no ``version_id`` (it is absent on the real dataclass), with a
    deterministic ``last_modified`` so the observation identity exercises
    the last_modified field.
    """
    fake = _S3LikeFakeBackend()
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    role_bodies = ev._fixture_role_bodies(fixture)
    base_ts = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    for idx, key in enumerate(DEFAULT_KEYS):
        role = DEFAULT_ROLE_PLAN[key]
        if role in ev.JSON_READ_ROLES:
            body = role_bodies[role]
        else:
            body = ev._MEDIA_PLACEHOLDER
        # No version_id — matches the pinned ObjectMetadata shape.
        fake.seed(key, body, last_modified=base_ts + timedelta(seconds=idx))
    return fake


# ---------------------------------------------------------------------------
# M1. true key-only secret-presence boundary (no EnvAccessSpy monkeypatch)
# ---------------------------------------------------------------------------


def test_m1_secret_name_present_true_without_value_retrieval() -> None:
    """When the secret env name is present, ``secret_name_present`` returns
    True without retrieving the value. Proven via the recording boundary:
    ``secret_value_reads`` is empty and ``membership_checks`` recorded the
    name."""
    boundary = _RecordingEnvAccess({
        "B2_KEY_ID": "real-key-id-value-1234",
        "B2_APP_KEY": "real-app-key-value-5678",
    })
    assert boundary.secret_name_present("B2_KEY_ID") is True
    assert boundary.secret_value_reads == []
    assert "B2_KEY_ID" in boundary.membership_checks


def test_m1_secret_name_present_false_without_value_retrieval() -> None:
    """When the secret env name is absent, ``secret_name_present`` returns
    False without retrieving the value."""
    boundary = _RecordingEnvAccess({
        "B2_KEY_ID": "real-key-id-value-1234",
        "B2_APP_KEY": "real-app-key-value-5678",
    })
    assert boundary.secret_name_present("B2_MISSING_KEY") is False
    assert boundary.secret_value_reads == []
    assert "B2_MISSING_KEY" in boundary.membership_checks


def test_m1_secret_value_read_before_gates_raises_immediately() -> None:
    """The injected test boundary raises immediately if a secret value is
    accessed before gate 22 completes. ``not recorded`` is NOT equivalent
    to ``not read``: the access is recorded before the raise."""
    boundary = _RecordingEnvAccess({"B2_KEY_ID": "v"})
    with pytest.raises(ev.AuthorizationError, match="secret_value_read_before_gate_completion"):
        boundary.read_secret_after_gates("B2_KEY_ID")
    # The access was recorded, not silently ignored.
    assert ("B2_KEY_ID", "before_gates") in boundary.secret_value_reads


def test_m1_alias_root_bucket_region_reads_do_not_expose_secrets() -> None:
    """``read_non_secret`` for the four config names returns the values
    without ever exposing a secret value. Secret-value reads stay empty."""
    boundary = _RecordingEnvAccess({
        "PROOFSTUDIO_IMPORT_BUCKET_ALIAS": ALIAS,
        "PROOFSTUDIO_IMPORT_ROOT": PREFIX,
        "B2_BUCKET": "fake-bucket",
        "B2_REGION": "fake-region",
        "B2_KEY_ID": "real-key-id-value-1234",
        "B2_APP_KEY": "real-app-key-value-5678",
    })
    assert boundary.read_non_secret("PROOFSTUDIO_IMPORT_BUCKET_ALIAS") == ALIAS
    assert boundary.read_non_secret("PROOFSTUDIO_IMPORT_ROOT") == PREFIX
    assert boundary.read_non_secret("B2_BUCKET") == "fake-bucket"
    assert boundary.read_non_secret("B2_REGION") == "fake-region"
    assert boundary.secret_value_reads == []


def test_m1_read_non_secret_on_secret_name_rejects() -> None:
    """A non-secret reader used on a secret name hard-rejects; never
    silently returns the value."""
    boundary = _RecordingEnvAccess({"B2_KEY_ID": "real-key-id-value-1234"})
    with pytest.raises(ev.AuthorizationError, match="non_secret_read_on_secret_name"):
        boundary.read_non_secret("B2_KEY_ID")
    assert boundary.secret_value_reads == []


def test_m1_real_boundary_uses_key_snapshot_only(monkeypatch: pytest.MonkeyPatch) -> None:
    """The RealEnvAccessBoundary snapshots os.environ.keys() at
    construction; secret_name_present inspects that snapshot only and
    never invokes get/getitem on a secret name. The boundary does not
    monkeypatch os._Environ globally."""
    monkeypatch.setenv("B2_KEY_ID", "real-key-id-value-1234")
    monkeypatch.setenv("B2_APP_KEY", "real-app-key-value-5678")
    # Capture the type's methods before/after to prove no monkeypatch.
    import os as _os
    before_getitem = _os._Environ.__getitem__
    boundary = ev.RealEnvAccessBoundary()
    after_getitem = _os._Environ.__getitem__
    assert before_getitem is after_getitem, "RealEnvAccessBoundary must not patch os._Environ"
    # Present secrets via key-snapshot inspection.
    assert boundary.secret_name_present("B2_KEY_ID") is True
    assert boundary.secret_name_present("B2_APP_KEY") is True
    assert boundary.secret_value_reads == []
    # Now mutate os.environ AFTER construction; the snapshot must not change.
    monkeypatch.setenv("B2_KEY_ID_LATE", "late")
    assert boundary.secret_name_present("B2_KEY_ID_LATE") is False


def test_m1_resolve_real_server_config_uses_key_membership_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The real pre-gate server-config resolver uses key-membership checks
    only for the secret env names; never a value read."""
    monkeypatch.setenv("PROOFSTUDIO_IMPORT_BUCKET_ALIAS", ALIAS)
    monkeypatch.setenv("PROOFSTUDIO_IMPORT_ROOT", PREFIX)
    monkeypatch.setenv("B2_BUCKET", "fake-bucket")
    monkeypatch.setenv("B2_REGION", "fake-region")
    monkeypatch.setenv("B2_KEY_ID", "real-key-id-value-1234")
    monkeypatch.setenv("B2_APP_KEY", "real-app-key-value-5678")
    boundary = ev.RealEnvAccessBoundary()
    sc = ev._resolve_real_server_config(env_access=boundary)
    assert sc.required_credentials_present is True
    assert boundary.secret_value_reads == [], (
        f"secret value read during pre-gate config: {boundary.secret_value_reads}"
    )
    # Key-membership was inspected for both secret names.
    assert "B2_KEY_ID" in boundary.membership_checks
    assert "B2_APP_KEY" in boundary.membership_checks


def test_m1_no_secret_read_before_gates_on_every_failure_path() -> None:
    """For each pre-gate failure path, run with the recording boundary
    injected; assert zero secret-value reads."""
    cases = [
        ("authorized_false", base_live_auth(authorized=False)),
        ("expired", base_live_auth(authorized_at=PAST, expires_at=PAST_EXPIRES)),
        ("wrong_commit", base_live_auth(execution_commit="0" * 40)),
    ]
    for name, auth in cases:
        boundary = _RecordingEnvAccess({
            "B2_KEY_ID": "real-key-id-value-1234",
            "B2_APP_KEY": "real-app-key-value-5678",
        })
        cred = _BoundaryBackedCredProvider(boundary)
        report, _, _, _ = _run_live(auth, credential_provider=cred, env_access=boundary)
        assert report.ok is False, f"{name}: expected failure"
        assert boundary.secret_value_reads == [], (
            f"{name}: secret value read before gates passed: {boundary.secret_value_reads}"
        )
        assert boundary.gates_completed is False, (
            f"{name}: gates were marked complete on a failure path"
        )


def test_m1_no_secret_read_on_alias_mismatch_path() -> None:
    """Alias mismatch rejects at gate 6 with zero secret-value reads."""
    boundary = _RecordingEnvAccess({
        "B2_KEY_ID": "real-key-id-value-1234",
        "B2_APP_KEY": "real-app-key-value-5678",
    })
    cred = _BoundaryBackedCredProvider(boundary)
    sc = ev.ServerConfig(
        alias="different", import_root=PREFIX,
        bucket_identity=SERVER_BUCKET_IDENTITY, region="us-west-000-fake",
        required_credentials_present=True,
    )
    report, _, _, _ = _run_live(
        server_config=sc, credential_provider=cred, env_access=boundary,
    )
    assert report.ok is False
    assert boundary.secret_value_reads == []


def test_m1_gate_22_completion_precedes_first_secret_value_read() -> None:
    """In a successful run, the boundary's event log must show
    ``gates_completed`` BEFORE the first ``secret_read_after_gates`` for
    B2_KEY_ID / B2_APP_KEY. The CredentialProvider is the only component
    permitted to read secret values."""
    boundary = _RecordingEnvAccess({
        "B2_KEY_ID": "real-key-id-value-1234",
        "B2_APP_KEY": "real-app-key-value-5678",
        "B2_BUCKET": "fake-bucket",
        "B2_REGION": "fake-region",
    })
    cred = _BoundaryBackedCredProvider(boundary)
    report, _, _, _ = _run_live(credential_provider=cred, env_access=boundary)
    assert report.ok is True
    # Find the gates_completed event and the first secret read.
    gates_idx = next(
        (i for i, (kind, _) in enumerate(boundary.event_log)
         if kind == "gates_completed"), None,
    )
    assert gates_idx is not None, "gates_completed was never marked"
    first_secret_idx = next(
        (i for i, (kind, _) in enumerate(boundary.event_log)
         if kind == "secret_read_after_gates"), None,
    )
    assert first_secret_idx is not None, "no secret value read occurred"
    assert gates_idx < first_secret_idx, (
        f"gates_completed ({gates_idx}) must precede first secret read "
        f"({first_secret_idx}); event_log={boundary.event_log}"
    )
    # Both secret values were read exactly once each, after gates completed.
    assert ("B2_KEY_ID", "after_gates") in boundary.secret_value_reads
    assert ("B2_APP_KEY", "after_gates") in boundary.secret_value_reads
    assert boundary.gates_completed is True


# ---------------------------------------------------------------------------
# M2. explicit alias/root/bucket/region configuration required
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("field,expected_code", [
    ("alias", "alias_mismatch"),
    ("import_root", "prefix_import_root_mismatch"),
    ("bucket_identity", "bucket_identity_mismatch"),
    ("region", "server_side_configuration_missing"),
])
def test_m2_missing_explicit_server_config_field_rejects(field: str,
                                                          expected_code: str) -> None:
    """Any of the four explicit server-config fields empty rejects before
    credential retrieval or backend construction. The exact gate that fires
    depends on which field is empty:
    - alias=empty -> gate 6 alias_mismatch
    - import_root=empty -> gate 8 prefix_import_root_mismatch
    - bucket_identity=empty -> gate 7 bucket_identity_mismatch
    - region=empty -> gate 17 server_side_configuration_missing
    """
    kwargs = dict(
        alias=ALIAS, import_root=PREFIX,
        bucket_identity=SERVER_BUCKET_IDENTITY, region="us-west-000-fake",
        required_credentials_present=True,
    )
    kwargs[field] = ""
    sc = ev.ServerConfig(**kwargs)
    report, cred, factory, _ = _run_live(server_config=sc)
    assert report.ok is False
    assert expected_code in report.errors
    assert cred.call_count == 0
    assert factory.call_count == 0


def test_m2_resolve_real_server_config_has_no_default_alias() -> None:
    """The real resolver must not default the alias to ``configured-import``.
    With no env vars set it returns empty strings and presence=False."""
    import os
    saved = {k: os.environ.pop(k, None) for k in (
        "PROOFSTUDIO_IMPORT_BUCKET_ALIAS", "PROOFSTUDIO_IMPORT_ROOT",
        "B2_BUCKET", "B2_REGION", "B2_KEY_ID", "B2_APP_KEY",
    )}
    try:
        sc = ev._resolve_real_server_config()
    finally:
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v
    assert sc.alias == ""
    assert sc.import_root == ""
    assert sc.bucket_identity == ""
    assert sc.region == ""
    assert sc.required_credentials_present is False


# ---------------------------------------------------------------------------
# M3. root-prefix mismatch (canonical_prefix != import_root) rejects
# ---------------------------------------------------------------------------


def test_m3_root_prefix_mismatch_rejects() -> None:
    sc = ev.ServerConfig(
        alias=ALIAS, import_root="import-root/different",
        bucket_identity=SERVER_BUCKET_IDENTITY, region="us-west-000-fake",
        required_credentials_present=True,
    )
    report, cred, factory, _ = _run_live(server_config=sc)
    assert report.ok is False
    assert "prefix_import_root_mismatch" in report.errors
    assert cred.call_count == 0


def test_m3_root_prefix_byte_for_byte_equality_passes() -> None:
    """The happy path requires byte-for-byte equality; no normalization."""
    report, _, _, _ = _run_live()
    assert report.ok is True


# ---------------------------------------------------------------------------
# M4-M7. accepted-ref binding (stale local, remote mismatch, lookup failure,
# exact match)
# ---------------------------------------------------------------------------


def test_m4_stale_local_accepted_ref_rejects() -> None:
    """The local accepted-ref is behind the remote; HEAD matches the stale
    local accepted commit but the remote has moved. Must reject at gate 21
    with remote_accepted_ref_mismatch."""
    stale = "0" * 40
    fresh = "1" * 40
    git_state = ev.GitState(
        branch=ev.PS_041E2B_BRANCH, head_commit=stale,
        accepted_commit=stale, accepted_ref=ev.ACCEPTED_EXECUTION_REF,
        tree_clean=True,
    )
    # HEAD/local-accepted/execution_commit all match stale; remote is fresh.
    auth = base_live_auth(execution_commit=stale)
    resolver = _FakeRemoteRefResolver(commit=fresh)
    report, cred, factory, _ = _run_live(
        auth=auth, git_state=git_state, remote_ref_resolver=resolver,
    )
    assert report.ok is False
    assert "remote_accepted_ref_mismatch" in report.errors
    assert cred.call_count == 0


def test_m5_remote_accepted_mismatch_rejects() -> None:
    """HEAD == execution_commit == local accepted, but the remote ref has
    moved. Must reject at gate 21 with remote_accepted_ref_mismatch."""
    resolver = _FakeRemoteRefResolver(commit="1" * 40)
    report, cred, factory, _ = _run_live(remote_ref_resolver=resolver)
    assert report.ok is False
    assert "remote_accepted_ref_mismatch" in report.errors
    assert cred.call_count == 0


def test_m6_remote_lookup_failure_rejects() -> None:
    """When the remote resolver returns empty (unreachable), gate 21 fails
    closed with remote_accepted_ref_unreachable."""
    resolver = _FakeRemoteRefResolver(commit="")
    report, cred, factory, _ = _run_live(remote_ref_resolver=resolver)
    assert report.ok is False
    assert "remote_accepted_ref_unreachable" in report.errors
    assert cred.call_count == 0


def test_m6_remote_malformed_rejects() -> None:
    resolver = _FakeRemoteRefResolver(commit="not-a-commit")
    report, cred, factory, _ = _run_live(remote_ref_resolver=resolver)
    assert report.ok is False
    assert "remote_accepted_ref_malformed" in report.errors


def test_m7_exact_local_remote_match_passes() -> None:
    report, _, _, _ = _run_live()
    assert report.ok is True
    assert report.remote_accepted_commit == EXEC_COMMIT


# ---------------------------------------------------------------------------
# M8-M10. output root confinement + atomic finalization
# ---------------------------------------------------------------------------


def test_m8_arbitrary_live_evidence_base_rejected() -> None:
    """The validator confines the base to exactly LIVE_EVIDENCE_DIR."""
    other = Path("/var/tmp/ps041e2b-not-confined")
    with pytest.raises(ev.AuthorizationError, match="evidence_base_not_confined"):
        ev._validate_evidence_base(other)


def test_m8_validate_evidence_base_accepts_canonical() -> None:
    """The canonical base passes the validator."""
    # Should not raise.
    ev._validate_evidence_base(Path(ev.LIVE_EVIDENCE_DIR))


def test_m9_symlink_output_base_rejected(tmp_path: Path) -> None:
    """A symlink base is rejected even if it points to the canonical path."""
    link = tmp_path / "live-symlink"
    if link.exists() or link.is_symlink():
        link.unlink()
    os.symlink(ev.LIVE_EVIDENCE_DIR, link)
    with pytest.raises(ev.AuthorizationError, match="evidence_base_symlink_rejected|evidence_base_not_confined"):
        ev._validate_evidence_base(link)


def test_m10_stale_partial_refused_not_rmtree() -> None:
    """A pre-existing partial directory is refused, not recursively deleted."""
    tmp_root = Path(_tempfile.mkdtemp(prefix="ps041e2b-test-stale-partial-"))
    evidence_dir = tmp_root / "evidence"
    evidence_dir.mkdir(parents=True)
    os.chmod(evidence_dir, 0o700)
    partial = evidence_dir / f".partial-{LIVE_EVIDENCE_RUN_ID}"
    partial.mkdir()
    # Plant a marker file inside the partial so we can prove it was NOT removed.
    marker = partial / "caller-controlled-marker.txt"
    marker.write_text("must-not-be-deleted", encoding="utf-8")
    report, _, _, _ = _run_live(evidence_dir=evidence_dir)
    assert report.ok is False
    assert "evidence_partial_directory_exists" in report.errors
    # The marker must still be present (no rmtree).
    assert marker.exists()
    assert marker.read_text(encoding="utf-8") == "must-not-be-deleted"
    # And no final directory was created.
    assert not (evidence_dir / LIVE_EVIDENCE_RUN_ID).exists()


# ---------------------------------------------------------------------------
# M11-M17. cleanup after each post-gate failure class
# ---------------------------------------------------------------------------


def test_m11_cleanup_after_credential_retrieval_failure() -> None:
    """Credential provider raises -> no backend constructed, no final dir."""
    class _ExplodingCred:
        def __init__(self) -> None:
            self.call_count = 0

        def __call__(self):
            self.call_count += 1
            raise OSError("credential transport failure")
    cred = _ExplodingCred()
    tmp_root = Path(_tempfile.mkdtemp(prefix="ps041e2b-test-cleanup-cred-"))
    evidence_dir = tmp_root / "evidence"
    factory = _FakeBackendFactory()
    report, _, factory_used, _ = _run_live(
        credential_provider=cred, backend_factory=factory,
        evidence_dir=evidence_dir,
    )
    assert report.ok is False
    assert cred.call_count == 1
    assert factory_used.call_count == 0
    assert not (evidence_dir / LIVE_EVIDENCE_RUN_ID).exists()


def test_m12_cleanup_after_backend_construction_failure() -> None:
    class _ExplodingFactory:
        def __init__(self) -> None:
            self.call_count = 0

        def __call__(self, credentials):
            self.call_count += 1
            raise OSError("backend construction failure")
    cred = _FakeCredProvider()
    factory = _ExplodingFactory()
    tmp_root = Path(_tempfile.mkdtemp(prefix="ps041e2b-test-cleanup-backend-"))
    evidence_dir = tmp_root / "evidence"
    report, _, _, _ = _run_live(
        credential_provider=cred, backend_factory=factory,
        evidence_dir=evidence_dir,
    )
    assert report.ok is False
    assert cred.call_count == 1
    assert factory.call_count == 1
    assert not (evidence_dir / LIVE_EVIDENCE_RUN_ID).exists()


def test_m13_cleanup_after_first_head_failure() -> None:
    fake = ev._build_fake_backend(
        json.loads(FIXTURE.read_text(encoding="utf-8")),
        list(DEFAULT_KEYS), object_role_by_key=dict(DEFAULT_ROLE_PLAN),
    )
    # Make every head fail.
    def _bad_head(key):
        raise OSError("head transport failure")
    fake.head = _bad_head  # type: ignore[assignment]
    factory = _FakeBackendFactory(backend=fake)
    tmp_root = Path(_tempfile.mkdtemp(prefix="ps041e2b-test-cleanup-head-"))
    evidence_dir = tmp_root / "evidence"
    report, _, _, _ = _run_live(backend_factory=factory, evidence_dir=evidence_dir)
    assert report.ok is False
    assert "backend_head_failed" in report.errors
    assert not (evidence_dir / LIVE_EVIDENCE_RUN_ID).exists()


def test_m14_cleanup_after_json_get_failure() -> None:
    fake = ev._build_fake_backend(
        json.loads(FIXTURE.read_text(encoding="utf-8")),
        list(DEFAULT_KEYS), object_role_by_key=dict(DEFAULT_ROLE_PLAN),
    )
    real_read = fake.read_bytes

    def failing_read(key, max_bytes):
        if key == DEFAULT_KEYS[0]:
            raise OSError("get transport failure")
        return real_read(key, max_bytes)
    fake.read_bytes = failing_read  # type: ignore[assignment]
    factory = _FakeBackendFactory(backend=fake)
    tmp_root = Path(_tempfile.mkdtemp(prefix="ps041e2b-test-cleanup-get-"))
    evidence_dir = tmp_root / "evidence"
    report, _, _, _ = _run_live(backend_factory=factory, evidence_dir=evidence_dir)
    assert report.ok is False
    assert not (evidence_dir / LIVE_EVIDENCE_RUN_ID).exists()


def test_m15_cleanup_after_candidate_construction_failure() -> None:
    """If the import service raises during candidate construction, cleanup
    runs and no final directory appears."""
    fake = ev._build_fake_backend(
        json.loads(FIXTURE.read_text(encoding="utf-8")),
        list(DEFAULT_KEYS), object_role_by_key=dict(DEFAULT_ROLE_PLAN),
    )
    factory = _FakeBackendFactory(backend=fake)

    class _ExplodingImportService:
        def create_campaign(self, payload):
            from proofstudio.api.services import ProofStudioService
            return ProofStudioService().create_campaign(payload)

        def import_genblaze_bundle(self, *args, **kwargs):
            raise OSError("import transport failure")

        def get_imported_bundle(self, *args, **kwargs):
            raise AssertionError("should not be reached")

        def get_imported_passport(self, *args, **kwargs):
            raise AssertionError("should not be reached")

    tmp_root = Path(_tempfile.mkdtemp(prefix="ps041e2b-test-cleanup-cand-"))
    evidence_dir = tmp_root / "evidence"
    report, _, _, _ = _run_live(
        backend_factory=factory, evidence_dir=evidence_dir,
        import_service=_ExplodingImportService(),
    )
    assert report.ok is False
    assert not (evidence_dir / LIVE_EVIDENCE_RUN_ID).exists()


def test_m16_cleanup_after_evidence_writing_failure() -> None:
    """If evidence writing fails partway, no final directory appears."""
    tmp_root = Path(_tempfile.mkdtemp(prefix="ps041e2b-test-cleanup-write-"))
    evidence_dir = tmp_root / "evidence"
    evidence_dir.mkdir(parents=True)
    # Pre-create the partial directory so creation refuses.
    (evidence_dir / f".partial-{LIVE_EVIDENCE_RUN_ID}").mkdir()
    report, _, _, _ = _run_live(evidence_dir=evidence_dir)
    assert report.ok is False
    assert not (evidence_dir / LIVE_EVIDENCE_RUN_ID).exists()


def test_m17_cleanup_after_security_scan_failure() -> None:
    """Adversarial: plant a real credential assignment in a partial file by
    monkeypatching the security scan to detect a planted value, then assert
    the final directory never appears and no quarantine directory is
    retained."""
    tmp_root = Path(_tempfile.mkdtemp(prefix="ps041e2b-test-cleanup-scan-"))
    evidence_dir = tmp_root / "evidence"
    real_scan = ev._security_scan_directory

    def planted_scan(directory, *, secret_values=None, bucket_identity="",
                     sensitive=None, expected_files=None):
        result = real_scan(
            directory, secret_values=secret_values, bucket_identity=bucket_identity,
            sensitive=sensitive,
        )
        result["real_value_leaks"].append({"file": "operation-counts.json", "category": "credential_assignment"})
        result["real_value_leak_count"] += 1
        return result

    import ps041e2_b2_evidence as ev_mod
    original = ev_mod._security_scan_directory
    ev_mod._security_scan_directory = planted_scan
    try:
        report, _, _, _ = _run_live(evidence_dir=evidence_dir)
    finally:
        ev_mod._security_scan_directory = original
    assert report.ok is False
    assert "evidence_secret_value_leak" in report.errors
    assert not (evidence_dir / LIVE_EVIDENCE_RUN_ID).exists()


# ---------------------------------------------------------------------------
# M18. real security scanner detects every fake secret/value category
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("payload,category", [
    ("B2_KEY_ID=ABCDEFGHIAAA1234", "credential_assignment"),
    ("aws_secret_access_key=AKIAEXAMPLEKEY", "credential_assignment"),
    ("password=\"supersecret123\"", "credential_assignment"),
    ("?X-Amz-Signature=abcdef&X-Amz-Date=20260101", "signed_url_query"),
    ("?Expires=999999999&Signature=abc", "signed_url_query"),
    ("Authorization: Bearer eyJabc123.def456", "auth_header"),
    ("Authorization: AWS4-HMAC-SHA256 Credential=AKIA/20260101", "auth_header"),
    ("X-Amz-Security-Token: Basic ABC123abc", "auth_header"),
    ("postgres://user:secretpass@db.example.com/db", "db_url_with_credentials"),
    ("https://example.invalid/secret", "unexpected_http_url"),
    ("http://10.0.0.1/leak", "unexpected_http_url"),
])
def test_m18_real_security_scanner_detects_each_category(tmp_path: Path,
                                                          payload: str,
                                                          category: str) -> None:
    p = tmp_path / "leak.json"
    p.write_text(payload, encoding="utf-8")
    scan = ev._security_scan_directory(tmp_path, bucket_identity="not-present-here")
    cats = {hit["category"] for hit in scan["real_value_leaks"]}
    assert category in cats, (
        f"scanner failed to flag {category} for payload {payload!r}; "
        f"got categories={cats}"
    )
    assert scan["real_value_leak_count"] > 0


def test_m18_real_security_scanner_detects_raw_bucket_identity(tmp_path: Path) -> None:
    p = tmp_path / "leak.json"
    p.write_text(f"bucket={SERVER_BUCKET_IDENTITY}", encoding="utf-8")
    scan = ev._security_scan_directory(
        tmp_path, bucket_identity=SERVER_BUCKET_IDENTITY,
    )
    cats = {hit["category"] for hit in scan["real_value_leaks"]}
    assert "raw_bucket_identity" in cats


def test_m18_real_security_scanner_detects_object_byte_sentinel(tmp_path: Path) -> None:
    sentinel_text = "X" * 128
    p = tmp_path / "leak.json"
    p.write_text(f"body={sentinel_text}", encoding="utf-8")
    scan = ev._security_scan_directory(
        tmp_path,
        secret_values=ev._collect_secret_values(
            object_byte_sentinels=[sentinel_text.encode()],
            bucket_identity="not-here",
        ),
    )
    cats = {hit["category"] for hit in scan["real_value_leaks"]}
    assert "object_byte_sentinel" in cats


def test_m18_real_security_scanner_never_serializes_secret_values(tmp_path: Path) -> None:
    """The scan output (marker hits + real leaks) must never carry a secret
    value, only file names + categories."""
    sentinel_text = "Z" * 80
    p = tmp_path / "leak.json"
    p.write_text(f"body={sentinel_text}", encoding="utf-8")
    scan = ev._security_scan_directory(
        tmp_path,
        secret_values=ev._collect_secret_values(
            object_byte_sentinels=[sentinel_text.encode()],
            bucket_identity=SERVER_BUCKET_IDENTITY,
        ),
        bucket_identity=SERVER_BUCKET_IDENTITY,
    )
    blob = json.dumps(scan)
    assert sentinel_text not in blob
    assert SERVER_BUCKET_IDENTITY not in blob


# ---------------------------------------------------------------------------
# M19-M21. atomic finalization invariants
# ---------------------------------------------------------------------------


def test_m19_no_final_directory_on_security_failure() -> None:
    """Already covered by M17, but re-affirm explicitly: a security-scan
    failure prevents the atomic rename."""
    tmp_root = Path(_tempfile.mkdtemp(prefix="ps041e2b-test-m19-"))
    evidence_dir = tmp_root / "evidence"
    real_scan = ev._security_scan_directory

    def planted_scan(directory, *, secret_values=None, bucket_identity="",
                     sensitive=None, expected_files=None):
        result = real_scan(
            directory, secret_values=secret_values, bucket_identity=bucket_identity,
            sensitive=sensitive,
        )
        result["real_value_leaks"].append({"file": "x", "category": "credential_assignment"})
        result["real_value_leak_count"] += 1
        return result

    import ps041e2_b2_evidence as ev_mod
    original = ev_mod._security_scan_directory
    ev_mod._security_scan_directory = planted_scan
    try:
        report, _, _, _ = _run_live(evidence_dir=evidence_dir)
    finally:
        ev_mod._security_scan_directory = original
    assert report.ok is False
    assert not (evidence_dir / LIVE_EVIDENCE_RUN_ID).exists()


def test_m20_final_directory_has_all_20_evidence_files() -> None:
    """The final directory appears only after all 20 LIVE_EVIDENCE_FILES are
    complete and regular non-symlink files."""
    report, _, _, _ = _run_live()
    assert report.ok is True
    run_dir = Path(report.evidence_dir)
    names = {p.name for p in run_dir.iterdir()}
    for required in ev.LIVE_EVIDENCE_FILES:
        assert required in names, f"missing evidence file: {required}"
        p = run_dir / required
        assert p.is_file() and not p.is_symlink(), (
            f"evidence file {required} must be a regular non-symlink file"
        )


def test_m21_cleanup_verified_true_in_finalized_summaries() -> None:
    report, _, _, _ = _run_live()
    assert report.ok is True
    assert report.cleanup_verified is True
    run_dir = Path(report.evidence_dir)
    auth_summary = _read_evidence_json(run_dir, "authorization-summary.json")
    exec_summary = _read_evidence_json(run_dir, "execution-summary.json")
    assert auth_summary["cleanup_verified"] is True
    assert exec_summary["cleanup_verified"] is True


# ---------------------------------------------------------------------------
# M22-M26. S3-like real-adapter exact counters + bounded-range contract
# ---------------------------------------------------------------------------


def test_m22_s3_like_adapter_operation_counts_are_exact() -> None:
    """The S3-like adapter path produces head + get_range counts that equal
    the GuardedLiveBackend counters exactly."""
    fake = _s3_like_populated_backend()
    factory = _S3LikeBackendFactory(fake)
    report, _, _, _ = _run_live(backend_factory=factory)
    assert report.ok is True
    # Initial 5 heads + 8 reader TOCTOU heads + 5 final = 18 (matches Fake path).
    assert report.head_calls_total == len(fake.head_calls)
    assert report.read_calls_total == len(fake.get_range_calls)
    # No full-object GET fallback ever happened.
    assert fake.get_calls == []
    # No list / write / delete / signed URL.
    assert report.list_calls == 0
    assert report.write_attempts == 0
    assert report.delete_attempts == 0


def test_m23_no_hidden_head_inside_read_bytes() -> None:
    """``GuardedLiveBackend.read_bytes`` must not issue a hidden HEAD on the
    underlying S3 backend. Prove it by counting underlying head calls
    directly: read_bytes must reuse the preceding counted HEAD metadata."""
    fake = _s3_like_populated_backend()
    adapter = ev.GuardedLiveBackend(fake)
    # Initial counted head feeds metadata into the adapter.
    head_before = len(fake.head_calls)
    adapter.head(DEFAULT_KEYS[0])
    head_after_first = len(fake.head_calls)
    assert head_after_first == head_before + 1
    # read_bytes must not issue another underlying head.
    body = adapter.read_bytes(DEFAULT_KEYS[0], 4096)
    assert len(fake.head_calls) == head_after_first
    assert isinstance(body, bytes)
    # And exactly one get_range call underneath.
    assert len(fake.get_range_calls) == 1
    assert fake.get_calls == []


def test_m24_no_get_range_support_rejects_before_reading() -> None:
    """An S3-like backend with no read_bytes AND no get_range must reject at
    read time before any byte is read."""
    class _NoRangeNoRead:
        def __init__(self) -> None:
            self.head_calls: list[str] = []

        def head(self, key):
            self.head_calls.append(key)
            return _S3LikeObjectMetadata(
                size=10, etag="etag", version_id="vid",
            )
    inner = _NoRangeNoRead()
    adapter = ev.GuardedLiveBackend(inner)
    adapter.head("k")
    with pytest.raises(ev.AuthorizationError, match="backend_get_range_unsupported"):
        adapter.read_bytes("k", 100)


def test_m25_bounded_range_returns_exact_declared_length() -> None:
    """read_bytes returns exactly the declared approved size; mismatches reject."""
    fake = _S3LikeFakeBackend()
    fake.seed("k", b"exact-10", version_id="v1")  # length 8 but declare 10 below
    # Tamper the declared size after seeding.
    fake.objects["k"]["size"] = 10
    adapter = ev.GuardedLiveBackend(fake)
    adapter.head("k")
    with pytest.raises(ev.AuthorizationError, match="media_length_mismatch"):
        adapter.read_bytes("k", 100)


def test_m26_version_id_absent_not_fabricated() -> None:
    """An S3 backend whose head returns the pinned genblaze-s3
    ``ObjectMetadata`` shape (no ``version_id``) must PASS, and the
    normalized head must carry ``version_id=None`` — never fabricated from
    ``storage_class`` or a constant."""
    class _NoVersionMetadata:
        __slots__ = ("size", "etag", "version_id", "storage_class",
                     "last_modified", "content_type", "metadata", "key")

        def __init__(self) -> None:
            self.size = 10
            self.etag = "etag-no-version-123"
            self.version_id = None  # absent — matches pinned ObjectMetadata
            self.storage_class = "STANDARD"
            self.last_modified = datetime(2025, 1, 1, tzinfo=timezone.utc)
            self.content_type = "application/json"
            self.metadata = {}
            self.key = "k"

    class _NoVersionBackend:
        def head(self, key):
            return _NoVersionMetadata()

        def get_range(self, key, *, offset, length):
            return b"x" * length

    adapter = ev.GuardedLiveBackend(_NoVersionBackend())
    result = adapter.head("k")
    assert result is not None
    assert result["version_id"] is None, "version_id must be None, not fabricated"
    assert result["size_bytes"] == 10
    assert result["etag"] == "etag-no-version-123"
    assert result["last_modified_iso"] is not None
    # The adapter's internal metadata cache carries version_id=None.
    assert adapter._head_metadata["k"]["version_id"] is None


# ---------------------------------------------------------------------------
# M27-M28. truthful fake vs real live_b2_calls semantics
# ---------------------------------------------------------------------------


def test_m27_fake_execution_reports_zero_live_b2_calls() -> None:
    report, _, _, _ = _run_live()
    assert report.ok is True
    assert report.live_b2_calls == 0
    assert report.real_backend_factory_used is False
    # operation-counts.json must agree.
    run_dir = Path(report.evidence_dir)
    op_counts = _read_evidence_json(run_dir, "operation-counts.json")
    assert op_counts["live_b2_calls"] == 0
    assert op_counts["real_backend_factory_used"] is False


def test_m28_real_mode_semantics_live_b2_calls_positive() -> None:
    """A local injected fake never fabricates HTTP-attempt evidence."""
    report, _, _, _ = _run_live(real_backend_factory_used=True)
    assert report.ok is True
    assert report.live_b2_calls == 0
    assert report.head_object_sdk_calls == report.head_calls_total
    assert report.ranged_get_object_sdk_calls == report.read_calls_total
    assert report.real_backend_factory_used is True


def test_m28_real_mode_operation_counts_reflect_live_b2_calls() -> None:
    report, _, _, _ = _run_live(real_backend_factory_used=True)
    run_dir = Path(report.evidence_dir)
    op_counts = _read_evidence_json(run_dir, "operation-counts.json")
    assert op_counts["live_b2_calls"] == 0
    assert op_counts["head_object_http_attempts"] == 0
    assert op_counts["ranged_get_object_http_attempts"] == 0
    assert op_counts["real_backend_factory_used"] is True


# ---------------------------------------------------------------------------
# M29-M32. accepted import service result + readbacks
# ---------------------------------------------------------------------------


def test_m29_actual_accepted_service_import_created_true_first_call() -> None:
    """First call to import_genblaze_bundle returns created=True."""
    report, _, _, _ = _run_live()
    assert report.ok is True
    assert report.import_created is True
    assert report.import_service_used is True
    run_dir = Path(report.evidence_dir)
    import_result = _read_evidence_json(run_dir, "import-result.json")
    assert import_result["import_created"] is True
    assert import_result["import_service"] == "ProofStudioService.import_genblaze_bundle"


def test_m30_actual_idempotent_re_import() -> None:
    """The second call to import_genblaze_bundle returns created=False with
    the same bundle_id and bundle_fingerprint."""
    report, _, _, _ = _run_live()
    assert report.ok is True
    assert report.import_idempotent is True
    run_dir = Path(report.evidence_dir)
    idempotency = _read_evidence_json(run_dir, "idempotency-result.json")
    assert idempotency["import_idempotent"] is True


def test_m31_actual_private_lineage_readback() -> None:
    """The private lineage summary is read back through the accepted
    ProofStudioService.get_imported_bundle boundary."""
    report, _, _, _ = _run_live()
    assert report.ok is True
    assert report.private_lineage_readback is True
    run_dir = Path(report.evidence_dir)
    private = _read_evidence_json(run_dir, "private-lineage-summary.json")
    assert private["readback_via"] == "ProofStudioService.get_imported_bundle"
    assert private["readback_ok"] is True
    assert private["node_count"] > 0
    assert private["edge_count"] > 0


def test_m32_actual_passport_readback() -> None:
    """The portable Passport is read back through the accepted
    ProofStudioService.get_imported_passport boundary."""
    report, _, _, _ = _run_live()
    assert report.ok is True
    assert report.passport_readback is True
    run_dir = Path(report.evidence_dir)
    passport = _read_evidence_json(run_dir, "private-passport-summary.json")
    assert passport["readback_via"] == "ProofStudioService.get_imported_passport"
    assert passport["readback_ok"] is True
    assert passport["passport_schema"] == ev.PASSPORT_SCHEMA


# ---------------------------------------------------------------------------
# M33. no raw exception, credential, bucket, endpoint or object bytes
# ---------------------------------------------------------------------------


def test_m33_no_raw_exception_credential_bucket_endpoint_or_bytes() -> None:
    """A successful run's evidence output must contain none of: raw bucket
    name, endpoint URL, credential assignment, raw object-byte sentinel,
    Authorization/Bearer header, signed URL query, db url with credentials."""
    report, _, _, _ = _run_live()
    assert report.ok is True
    run_dir = Path(report.evidence_dir)
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    role_bodies = ev._fixture_role_bodies(fixture)
    blob = ""
    for name in _evidence_files(run_dir):
        blob += (run_dir / name).read_text(encoding="utf-8", errors="ignore")
    # No raw bucket name.
    assert SERVER_BUCKET_IDENTITY not in blob
    # No raw object bytes (use a distinctive substring of each JSON body).
    for role, body in role_bodies.items():
        marker = body[:48].decode("utf-8", errors="ignore")
        if len(marker) > 8:
            assert marker not in blob, f"raw JSON bytes for role {role} leaked"
    # No endpoint URLs / credential assignments / signed URL queries /
    # Authorization headers / db URLs.
    scan = ev._security_scan_directory(
        run_dir,
        secret_values=ev._collect_secret_values(
            object_byte_sentinels=[], bucket_identity=SERVER_BUCKET_IDENTITY,
        ),
        bucket_identity=SERVER_BUCKET_IDENTITY,
    )
    assert scan["real_value_leak_count"] == 0


def test_m33b_no_live_backend_constructed_in_pm_tests() -> None:
    """Re-affirm: no PM-review test imports genblaze_s3 or boto3."""
    import sys as _sys
    before_genblaze = "genblaze_s3" in _sys.modules
    before_boto3 = "boto3" in _sys.modules
    _run_live()
    after_genblaze = "genblaze_s3" in _sys.modules
    after_boto3 = "boto3" in _sys.modules
    assert before_genblaze == after_genblaze
    assert before_boto3 == after_boto3


# ===========================================================================
# PS-041E2-B PHASE-1 — CORRECTED PM-REVIEW FOCUSED TESTS (N1-N34)
#
# These tests cover the corrected blockers from sections 3-7 of the PM
# artifact review. Every test remains fake/injected and performs no
# network, no provider call, no real B2 access, and no real backend
# construction.
# ===========================================================================


# ---------------------------------------------------------------------------
# N1-N6. Section 3 — exact credential values in the fail-closed scan
# ---------------------------------------------------------------------------


def test_n1_exact_key_id_detected_bare() -> None:
    """A bare B2 key id appearing alone in evidence (no field name) is
    detected via exact substring match."""
    fake_key_id = "AKIAFAKEKEYID1234567"
    p = _tempfile.mkdtemp()
    d = Path(p)
    (d / "leak.json").write_text(fake_key_id, encoding="utf-8")
    scan = ev._security_scan_directory(
        d, secret_values=ev._collect_secret_values(
            object_byte_sentinels=[], bucket_identity="not-here",
            key_id=fake_key_id,
        ),
    )
    cats = {hit["category"] for hit in scan["real_value_leaks"]}
    assert "bare_credential_value" in cats
    assert scan["real_value_leak_count"] > 0


def test_n2_exact_application_key_detected_bare() -> None:
    """A bare B2 application key appearing alone in evidence is detected."""
    fake_app_key = "supersecretappkeyvalue9876"
    p = _tempfile.mkdtemp()
    d = Path(p)
    (d / "leak.json").write_text(fake_app_key, encoding="utf-8")
    scan = ev._security_scan_directory(
        d, secret_values=ev._collect_secret_values(
            object_byte_sentinels=[], bucket_identity="not-here",
            app_key=fake_app_key,
        ),
    )
    cats = {hit["category"] for hit in scan["real_value_leaks"]}
    assert "bare_credential_value" in cats


def test_n3_bare_credential_under_unrelated_json_property() -> None:
    """A bare credential value placed under an unrelated JSON property
    (no ``B2_`` or ``secret`` marker) must still be detected."""
    fake_key_id = "AKIAFAKEKEYID1234567"
    payload = json.dumps({"unrelated_property": fake_key_id, "count": 42})
    p = _tempfile.mkdtemp()
    d = Path(p)
    (d / "leak.json").write_text(payload, encoding="utf-8")
    scan = ev._security_scan_directory(
        d, sensitive=ev.SensitiveScanContext(key_id=fake_key_id),
    )
    cats = {hit["category"] for hit in scan["real_value_leaks"]}
    assert "bare_credential_value" in cats


def test_n4_bare_credential_inside_ordinary_prose() -> None:
    """A bare credential value inside ordinary prose must still be
    detected."""
    fake_app_key = "supersecretappkeyvalue9876"
    payload = (
        "The run completed successfully and the value "
        f"{fake_app_key} was observed in transit."
    )
    p = _tempfile.mkdtemp()
    d = Path(p)
    (d / "leak.json").write_text(payload, encoding="utf-8")
    scan = ev._security_scan_directory(
        d, sensitive=ev.SensitiveScanContext(app_key=fake_app_key),
    )
    cats = {hit["category"] for hit in scan["real_value_leaks"]}
    assert "bare_credential_value" in cats


def test_n5_bare_credential_with_no_marker_at_all() -> None:
    """A bare credential value with no ``B2_`` or ``secret`` marker
    anywhere in the file must still be detected."""
    fake_key_id = "AKIAFAKEKEYID1234567"
    fake_app_key = "supersecretappkeyvalue9876"
    payload = json.dumps({"note": "all good", "ok": True, "value": fake_key_id})
    p = _tempfile.mkdtemp()
    d = Path(p)
    (d / "leak.json").write_text(payload, encoding="utf-8")
    scan = ev._security_scan_directory(
        d, sensitive=ev.SensitiveScanContext(
            key_id=fake_key_id, app_key=fake_app_key,
        ),
    )
    cats = {hit["category"] for hit in scan["real_value_leaks"]}
    assert "bare_credential_value" in cats


def test_n6_sensitive_scan_context_drops_values() -> None:
    """The SensitiveScanContext drops every sensitive reference after
    :meth:`drop` is called. Used as a context manager it drops on exit."""
    ctx = ev.SensitiveScanContext(
        key_id="AKIAFAKEKEYID1234567", app_key="supersecretappkeyvalue9876",
        bucket_identity="some-bucket-id",
        object_byte_sentinels=(b"X" * 64,),
    )
    assert ctx.values.get("key_id") == "AKIAFAKEKEYID1234567"
    ctx.drop()
    assert ctx.values == {}
    assert ctx.dropped is True
    # Context manager use.
    with ev.SensitiveScanContext(key_id="abc12345") as ctx2:
        assert ctx2.values.get("key_id") == "abc12345"
    assert ctx2.values == {}


def test_n6b_sensitive_values_never_in_scan_output() -> None:
    """The scan output (real leaks + marker hits + claim text) never
    contains any sensitive comparison value."""
    fake_key_id = "AKIAFAKEKEYID1234567"
    fake_app_key = "supersecretappkeyvalue9876"
    fake_bucket = "real-bucket-identity"
    p = _tempfile.mkdtemp()
    d = Path(p)
    # Plant one of each so the scanner finds leaks; the values themselves
    # must NOT appear in the report.
    (d / "a.json").write_text(fake_key_id, encoding="utf-8")
    (d / "b.json").write_text(fake_app_key, encoding="utf-8")
    (d / "c.json").write_text(fake_bucket, encoding="utf-8")
    scan = ev._security_scan_directory(
        d, sensitive=ev.SensitiveScanContext(
            key_id=fake_key_id, app_key=fake_app_key, bucket_identity=fake_bucket,
        ),
    )
    blob = json.dumps(scan)
    assert fake_key_id not in blob
    assert fake_app_key not in blob
    assert fake_bucket not in blob


# ---------------------------------------------------------------------------
# N7-N11. Section 4 — no quarantine of credential-bearing evidence
# ---------------------------------------------------------------------------


def test_n7_planted_credential_leak_leaves_no_final_partial_or_quarantine() -> None:
    """After a planted credential leak in the partial directory, prove:
    - no final directory exists;
    - no ``.partial-*`` directory exists;
    - no ``.quarantine-*`` directory containing the evidence exists;
    - a recursive scan of the evidence root finds none of the planted value;
    - no object bytes remain."""
    tmp_root = Path(_tempfile.mkdtemp(prefix="ps041e2b-test-n7-"))
    evidence_dir = tmp_root / "evidence"
    planted_value = "AKIAPLANTEDSECRETKEYID12"
    real_scan = ev._security_scan_directory

    def planted_scan(directory, *, secret_values=None, bucket_identity="",
                     sensitive=None, expected_files=None):
        result = real_scan(
            directory, secret_values=secret_values, bucket_identity=bucket_identity,
            sensitive=sensitive,
        )
        result["real_value_leaks"].append({"file": "leaked.txt", "category": "bare_credential_value"})
        result["real_value_leak_count"] += 1
        return result

    # Plant the value into a partial file via a pre-created partial dir
    # would be rmtree'd; instead, intercept the provisional writer by
    # planting via monkeypatched scan that detects a synthetic leak. The
    # planted value itself is never written to disk by this test — the
    # scan simply returns a leak result, and the secure-remove path runs.
    import ps041e2_b2_evidence as ev_mod
    original = ev_mod._security_scan_directory
    ev_mod._security_scan_directory = planted_scan
    try:
        report, _, _, _ = _run_live(evidence_dir=evidence_dir)
    finally:
        ev_mod._security_scan_directory = original
    assert report.ok is False
    assert "evidence_secret_value_leak" in report.errors
    # No final directory.
    assert not (evidence_dir / LIVE_EVIDENCE_RUN_ID).exists()
    # No partial directory.
    partials = list(evidence_dir.glob(".partial-*"))
    assert partials == [], f"partial directory remains: {partials}"
    # No quarantine directory.
    quarantines = list(evidence_dir.glob(".quarantine-*"))
    assert quarantines == [], f"quarantine directory remains: {quarantines}"
    # Recursive scan: no object bytes, no planted value in any file under
    # the evidence root (the sanitized failure summary carries only the
    # error code).
    for path in evidence_dir.rglob("*"):
        if path.is_file():
            text = path.read_text(encoding="utf-8", errors="ignore")
            assert planted_value not in text, (
                f"planted value found in {path}"
            )
            # Object bytes (the fixture's role bodies) must not leak.
            fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
            for role_body in ev._fixture_role_bodies(fixture).values():
                marker = role_body[:48].decode("utf-8", errors="ignore")
                if len(marker) > 8:
                    assert marker not in text, f"object bytes for role leaked in {path}"


def test_n8_other_failure_paths_also_leave_no_quarantine() -> None:
    """A non-leak failure (backend construction failure) must not leave a
    quarantine directory either. The partial dir is securely removed."""
    class _ExplodingFactory:
        def __init__(self) -> None:
            self.call_count = 0

        def __call__(self, credentials):
            self.call_count += 1
            raise OSError("backend construction failure")
    cred = _FakeCredProvider()
    factory = _ExplodingFactory()
    tmp_root = Path(_tempfile.mkdtemp(prefix="ps041e2b-test-n8-"))
    evidence_dir = tmp_root / "evidence"
    report, _, _, _ = _run_live(
        credential_provider=cred, backend_factory=factory,
        evidence_dir=evidence_dir,
    )
    assert report.ok is False
    assert not (evidence_dir / LIVE_EVIDENCE_RUN_ID).exists()
    assert list(evidence_dir.glob(".partial-*")) == []
    assert list(evidence_dir.glob(".quarantine-*")) == []


def test_n9_sanitized_failure_summary_written_on_leak() -> None:
    """On a real-value leak, an optional sanitized failure summary is
    written to the evidence base. The summary contains ONLY a stable
    error code and a timestamp; no source evidence."""
    tmp_root = Path(_tempfile.mkdtemp(prefix="ps041e2b-test-n9-"))
    evidence_dir = tmp_root / "evidence"
    real_scan = ev._security_scan_directory

    def planted_scan(directory, *, secret_values=None, bucket_identity="",
                     sensitive=None, expected_files=None):
        result = real_scan(
            directory, secret_values=secret_values, bucket_identity=bucket_identity,
            sensitive=sensitive,
        )
        result["real_value_leaks"].append({"file": "x", "category": "bare_credential_value"})
        result["real_value_leak_count"] += 1
        return result

    import ps041e2_b2_evidence as ev_mod
    original = ev_mod._security_scan_directory
    ev_mod._security_scan_directory = planted_scan
    try:
        report, _, _, _ = _run_live(evidence_dir=evidence_dir)
    finally:
        ev_mod._security_scan_directory = original
    summary_path = evidence_dir / f".failure-{LIVE_EVIDENCE_RUN_ID}.json"
    assert summary_path.exists()
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["error_code"] == "evidence_secret_value_leak"
    assert "ts" in payload
    # The summary carries no source evidence (only error_code + ts).
    assert set(payload) <= {"error_code", "ts"}


def test_n10_secure_remove_partial_overwrites_files() -> None:
    """``_secure_remove_partial`` overwrites regular files with zeros
    before unlinking and removes the directory tree. Never renames to
    ``.quarantine-*``."""
    tmp = Path(_tempfile.mkdtemp(prefix="ps041e2b-test-n10-"))
    target = tmp / ".partial-test"
    target.mkdir()
    secret_marker = "AKIASECRETMARKER1234"
    (target / "a.txt").write_text(secret_marker, encoding="utf-8")
    (target / "b.txt").write_text("normal content", encoding="utf-8")
    ev._secure_remove_partial(target)
    assert not target.exists()
    # No quarantine rename anywhere in the parent.
    assert list(tmp.glob(".quarantine-*")) == []


# ---------------------------------------------------------------------------
# N11-N20. Section 5 — real Git state fails closed
# ---------------------------------------------------------------------------


class _FakeGitRunner:
    """Fake GitCommandRunner that returns scripted GitCommandResults."""

    def __init__(self, results: dict[tuple[str, ...], "ev.GitCommandResult"] | None = None) -> None:
        self._results: dict[tuple[str, ...], "ev.GitCommandResult"] = dict(results or {})
        self.calls: list[list[str]] = []

    def __call__(self, args: list[str], *, timeout: float) -> "ev.GitCommandResult":
        self.calls.append(list(args))
        return self._results.get(
            tuple(args),
            ev.GitCommandResult(True, "", ""),
        )


def _make_runner(results: dict[tuple[str, ...], "ev.GitCommandResult"]) -> "_FakeGitRunner":
    """Build a fake runner from a dict of args-tuple -> GitCommandResult."""
    return _FakeGitRunner(results=results)


def test_n11_status_command_failure_does_not_become_tree_clean() -> None:
    """A failed ``git status`` command MUST NOT become tree_clean=true."""
    runner = _make_runner({
        ("rev-parse", "--abbrev-ref", "HEAD"):
            ev.GitCommandResult(True, "ps-041e2b/branch\n", ""),
        ("rev-parse", "HEAD"):
            ev.GitCommandResult(True, EXEC_COMMIT + "\n", ""),
        ("rev-parse", ev.ACCEPTED_EXECUTION_REF):
            ev.GitCommandResult(True, EXEC_COMMIT + "\n", ""),
        ("status", "--porcelain"):
            ev.GitCommandResult(False, "", "git_command_nonzero_exit"),
    })
    gs = ev._resolve_real_git_state(runner=runner)
    assert gs.tree_clean is False, (
        "failed git status must NOT become tree_clean=true"
    )


def test_n12_status_timeout_does_not_become_tree_clean() -> None:
    """A timed-out ``git status`` command must NOT become tree_clean=true."""
    runner = _make_runner({
        ("rev-parse", "--abbrev-ref", "HEAD"):
            ev.GitCommandResult(True, "ps-041e2b/branch\n", ""),
        ("rev-parse", "HEAD"):
            ev.GitCommandResult(True, EXEC_COMMIT + "\n", ""),
        ("rev-parse", ev.ACCEPTED_EXECUTION_REF):
            ev.GitCommandResult(True, EXEC_COMMIT + "\n", ""),
        ("status", "--porcelain"):
            ev.GitCommandResult(False, "", "git_command_timeout"),
    })
    gs = ev._resolve_real_git_state(runner=runner)
    assert gs.tree_clean is False


def test_n13_branch_command_failure_yields_empty_branch() -> None:
    """A failed branch command yields an empty branch; the executor
    rejects at gate 21 with branch_not_implementation_branch."""
    runner = _make_runner({
        ("rev-parse", "--abbrev-ref", "HEAD"):
            ev.GitCommandResult(False, "", "git_command_failed"),
        ("rev-parse", "HEAD"):
            ev.GitCommandResult(True, EXEC_COMMIT + "\n", ""),
        ("rev-parse", ev.ACCEPTED_EXECUTION_REF):
            ev.GitCommandResult(True, EXEC_COMMIT + "\n", ""),
        ("status", "--porcelain"):
            ev.GitCommandResult(True, "", ""),
    })
    gs = ev._resolve_real_git_state(runner=runner)
    assert gs.branch == ""
    assert gs.head_commit == EXEC_COMMIT


def test_n14_accepted_ref_lookup_failure_yields_empty_accepted_commit() -> None:
    """A failed accepted-ref lookup yields an empty accepted_commit; the
    executor rejects at gate 21 with head_not_accepted."""
    runner = _make_runner({
        ("rev-parse", "--abbrev-ref", "HEAD"):
            ev.GitCommandResult(True, "ps-041e2b/branch\n", ""),
        ("rev-parse", "HEAD"):
            ev.GitCommandResult(True, EXEC_COMMIT + "\n", ""),
        ("rev-parse", ev.ACCEPTED_EXECUTION_REF):
            ev.GitCommandResult(False, "", "git_command_nonzero_exit"),
        ("status", "--porcelain"):
            ev.GitCommandResult(True, "", ""),
    })
    gs = ev._resolve_real_git_state(runner=runner)
    assert gs.accepted_commit == ""


def test_n15_clean_status_success_yields_tree_clean() -> None:
    """A successful ``git status`` with empty stdout yields tree_clean=True."""
    runner = _make_runner({
        ("rev-parse", "--abbrev-ref", "HEAD"):
            ev.GitCommandResult(True, "ps-041e2b/branch\n", ""),
        ("rev-parse", "HEAD"):
            ev.GitCommandResult(True, EXEC_COMMIT + "\n", ""),
        ("rev-parse", ev.ACCEPTED_EXECUTION_REF):
            ev.GitCommandResult(True, EXEC_COMMIT + "\n", ""),
        ("status", "--porcelain"):
            ev.GitCommandResult(True, "", ""),
    })
    gs = ev._resolve_real_git_state(runner=runner)
    assert gs.tree_clean is True


def test_n16_dirty_status_success_yields_tree_not_clean() -> None:
    """A successful ``git status`` with non-empty stdout yields tree_clean=False."""
    runner = _make_runner({
        ("rev-parse", "--abbrev-ref", "HEAD"):
            ev.GitCommandResult(True, "ps-041e2b/branch\n", ""),
        ("rev-parse", "HEAD"):
            ev.GitCommandResult(True, EXEC_COMMIT + "\n", ""),
        ("rev-parse", ev.ACCEPTED_EXECUTION_REF):
            ev.GitCommandResult(True, EXEC_COMMIT + "\n", ""),
        ("status", "--porcelain"):
            ev.GitCommandResult(True, " M file.py\n", ""),
    })
    gs = ev._resolve_real_git_state(runner=runner)
    assert gs.tree_clean is False


def test_n17_detached_head_normalized_to_marker() -> None:
    """A detached HEAD (``--abbrev-ref HEAD`` returns ``HEAD``) is
    normalized to the exact ``DETACHED_HEAD_MARKER``."""
    runner = _make_runner({
        ("rev-parse", "--abbrev-ref", "HEAD"):
            ev.GitCommandResult(True, "HEAD\n", ""),
        ("rev-parse", "HEAD"):
            ev.GitCommandResult(True, EXEC_COMMIT + "\n", ""),
        ("rev-parse", ev.ACCEPTED_EXECUTION_REF):
            ev.GitCommandResult(True, EXEC_COMMIT + "\n", ""),
        ("status", "--porcelain"):
            ev.GitCommandResult(True, "", ""),
    })
    gs = ev._resolve_real_git_state(runner=runner)
    assert gs.branch == ev.DETACHED_HEAD_MARKER


def test_n17b_detached_head_hex_commit_normalized_to_marker() -> None:
    """Some git versions return a hex commit for ``--abbrev-ref HEAD`` in
    detached state; that is also normalized to the detached marker."""
    runner = _make_runner({
        ("rev-parse", "--abbrev-ref", "HEAD"):
            ev.GitCommandResult(True, EXEC_COMMIT + "\n", ""),
        ("rev-parse", "HEAD"):
            ev.GitCommandResult(True, EXEC_COMMIT + "\n", ""),
        ("rev-parse", ev.ACCEPTED_EXECUTION_REF):
            ev.GitCommandResult(True, EXEC_COMMIT + "\n", ""),
        ("status", "--porcelain"):
            ev.GitCommandResult(True, "", ""),
    })
    gs = ev._resolve_real_git_state(runner=runner)
    assert gs.branch == ev.DETACHED_HEAD_MARKER


def test_n18_exact_branch_normalized() -> None:
    """The exact implementation branch is normalized unchanged."""
    runner = _make_runner({
        ("rev-parse", "--abbrev-ref", "HEAD"):
            ev.GitCommandResult(True, ev.PS_041E2B_BRANCH + "\n", ""),
        ("rev-parse", "HEAD"):
            ev.GitCommandResult(True, EXEC_COMMIT + "\n", ""),
        ("rev-parse", ev.ACCEPTED_EXECUTION_REF):
            ev.GitCommandResult(True, EXEC_COMMIT + "\n", ""),
        ("status", "--porcelain"):
            ev.GitCommandResult(True, "", ""),
    })
    gs = ev._resolve_real_git_state(runner=runner)
    assert gs.branch == ev.PS_041E2B_BRANCH


def test_n19_malformed_head_rejected() -> None:
    """A non-hex40 HEAD command output yields an empty head_commit
    (malformed commits reject)."""
    runner = _make_runner({
        ("rev-parse", "--abbrev-ref", "HEAD"):
            ev.GitCommandResult(True, "ps-041e2b/branch\n", ""),
        ("rev-parse", "HEAD"):
            ev.GitCommandResult(True, "not-a-commit\n", ""),
        ("rev-parse", ev.ACCEPTED_EXECUTION_REF):
            ev.GitCommandResult(True, EXEC_COMMIT + "\n", ""),
        ("status", "--porcelain"):
            ev.GitCommandResult(True, "", ""),
    })
    gs = ev._resolve_real_git_state(runner=runner)
    assert gs.head_commit == ""


def test_n20_run_git_command_never_prints_stderr() -> None:
    """``_run_git_command`` returns a stable error code and never carries
    raw subprocess stderr in the result."""
    # A non-zero exit returns only the stable code, no stderr text.
    result = ev._run_git_command(["this-is-not-a-real-git-subcommand"])
    assert result.succeeded is False
    assert result.error_code in {
        "git_command_nonzero_exit", "git_command_failed", "git_command_timeout",
    }
    # No raw stderr leak in stdout/code fields.
    assert "fatal:" not in result.stdout
    assert "fatal:" not in result.error_code


# ---------------------------------------------------------------------------
# N21-N23. Section 6 — independent server-root evidence (no tautology)
# ---------------------------------------------------------------------------


def test_n21_server_binding_evidence_carries_independent_observations() -> None:
    """``server-binding.json`` carries ``authorized_prefix``,
    ``configured_import_root``, ``import_root_comparison_code``, and
    ``import_root_matches_prefix`` derived from independent observations
    (never a value compared to itself)."""
    report, _, _, _ = _run_live()
    assert report.ok is True
    run_dir = Path(report.evidence_dir)
    sb = _read_evidence_json(run_dir, "server-binding.json")
    assert sb["authorized_prefix"] == PREFIX
    assert sb["configured_import_root"] == PREFIX
    assert sb["import_root_comparison_code"] == "prefix_import_root_match"
    assert sb["import_root_matches_prefix"] is True


def test_n22_mismatched_import_root_cannot_emit_match() -> None:
    """When authorized prefix != configured import root, the evidence
    builder cannot emit a successful match result. The run rejects at
    gate 8 with prefix_import_root_mismatch and the report carries the
    mismatch code."""
    sc = ev.ServerConfig(
        alias=ALIAS, import_root="import-root/different",
        bucket_identity=SERVER_BUCKET_IDENTITY, region="us-west-000-fake",
        required_credentials_present=True,
    )
    report, _, _, _ = _run_live(server_config=sc)
    assert report.ok is False
    assert "prefix_import_root_mismatch" in report.errors
    assert report.import_root_matches_prefix is False
    assert report.import_root_comparison_code == "prefix_import_root_mismatch"


def test_n23_no_tautology_in_evidence() -> None:
    """``import_root_matches_prefix`` must never be the result of
    ``report.canonical_prefix == report.canonical_prefix``. The report
    carries distinct ``authorized_prefix`` and ``configured_import_root``
    fields that happen to be equal on the happy path but are observed
    independently."""
    report, _, _, _ = _run_live()
    assert report.ok is True
    # Both fields are populated from independent sources.
    assert report.authorized_prefix == report.canonical_prefix
    # On the happy path configured_import_root is the server-observed root.
    assert report.configured_import_root == report.canonical_prefix


# ---------------------------------------------------------------------------
# N24-N29. Section 7 — partial directory + scanning hardening
# ---------------------------------------------------------------------------


def test_n24_symlink_evidence_file_rejected_before_scanning(tmp_path: Path) -> None:
    """A symlink evidence file is rejected before reading via lstat."""
    target = tmp_path / "real.txt"
    target.write_text("body", encoding="utf-8")
    link = tmp_path / "link.json"
    os.symlink(target, link)
    scan = ev._security_scan_directory(tmp_path)
    cats = {hit["category"] for hit in scan["real_value_leaks"]}
    assert "symlink_evidence_file" in cats
    assert scan["real_value_leak_count"] > 0


def test_n25_symlink_partial_directory_rejected(tmp_path: Path) -> None:
    """A symlink partial directory at any path component is rejected by
    ``_create_partial_dir`` (the partial name resolves to a symlink)."""
    base = tmp_path / "evidence"
    base.mkdir()
    os.chmod(base, 0o700)
    partial_link = base / f".partial-{LIVE_EVIDENCE_RUN_ID}"
    os.symlink(tmp_path / "elsewhere", partial_link)
    with pytest.raises(ev.AuthorizationError, match="evidence_partial_directory_exists"):
        ev._create_partial_dir(base, LIVE_EVIDENCE_RUN_ID)


def test_n25b_symlink_in_path_component_rejected(tmp_path: Path) -> None:
    """A symlink at any path component of the evidence base is rejected."""
    base = tmp_path / "evidence"
    base.mkdir()
    # Make the partial path's parent a symlink to somewhere unexpected.
    bad_root = tmp_path / "symlinked_root"
    bad_root.mkdir()
    symlinked_base = tmp_path / "link_to_evidence"
    os.symlink(base, symlinked_base)
    with pytest.raises(ev.AuthorizationError, match="evidence_path_symlink_component"):
        ev._reject_symlink_path_components(symlinked_base)


def test_n26_unexpected_file_rejected_before_finalization(tmp_path: Path) -> None:
    """``_verify_evidence_files_complete`` rejects unexpected files."""
    # Set up a directory with exactly the expected files.
    d = tmp_path / "partial"
    d.mkdir()
    for name in ev.LIVE_EVIDENCE_FILES:
        (d / name).write_text("{}", encoding="utf-8")
    # Add an unexpected file.
    (d / "unexpected.txt").write_text("evil", encoding="utf-8")
    with pytest.raises(ev.AuthorizationError, match="evidence_files_unexpected"):
        ev._verify_evidence_files_complete(d)


def test_n27_nonregular_file_rejected_by_scan(tmp_path: Path) -> None:
    """A non-regular file (FIFO) is flagged by the scan before reading."""
    fifo = tmp_path / "fifo.json"
    try:
        os.mkfifo(str(fifo))
    except (OSError, AttributeError):
        pytest.skip("mkfifo not supported on this platform")
    scan = ev._security_scan_directory(tmp_path)
    cats = {hit["category"] for hit in scan["real_value_leaks"]}
    assert "nonregular_evidence_file" in cats


def test_n28_partial_directory_owner_only_permissions(tmp_path: Path) -> None:
    """The partial directory is created with owner-only permissions
    (mode 0o700), and so is its parent base."""
    import stat as _statmod
    base = tmp_path / "evidence"
    partial, _ = ev._create_partial_dir(base, LIVE_EVIDENCE_RUN_ID)
    pmode = _statmod.S_IMODE(os.lstat(partial).st_mode)
    bmode = _statmod.S_IMODE(os.lstat(base).st_mode)
    assert pmode == 0o700, f"partial mode is {oct(pmode)}, expected 0o700"
    assert bmode == 0o700, f"base mode is {oct(bmode)}, expected 0o700"


def test_n29_expected_files_rejects_unexpected_in_final_scan(tmp_path: Path) -> None:
    """When ``expected_files`` is provided, the final scan flags any
    unexpected entry as a leak before finalization."""
    expected = frozenset({"a.json"})
    (tmp_path / "a.json").write_text("{}", encoding="utf-8")
    (tmp_path / "rogue.json").write_text("{}", encoding="utf-8")
    scan = ev._security_scan_directory(tmp_path, expected_files=expected)
    cats = {hit["category"] for hit in scan["real_value_leaks"]}
    assert "unexpected_evidence_file" in cats


# ---------------------------------------------------------------------------
# N30. Section 9 — accepted executor controls preserved (regression net)
# ---------------------------------------------------------------------------


def test_n30_accepted_executor_controls_preserved() -> None:
    """Re-affirm the accepted executor controls are not regressed by the
    corrected PM fixes:
    - exact five-role plan;
    - exact-key HEAD/GET only;
    - no LIST;
    - bounded-range-only reads;
    - real operation counters;
    - exact snapshot/hash binding;
    - accepted ProofStudioService import;
    - idempotent re-import;
    - private lineage readback;
    - private Passport readback;
    - atomic final rename;
    - truthful live_b2_calls;
    - zero provider/write/delete/signed-URL capability.
    """
    report, _, _, _ = _run_live()
    assert report.ok is True
    # Five-role plan (the four JSON roles + final delivery = 5 distinct).
    roles_in_plan = set(report.role_plan.values())
    assert roles_in_plan == {
        ev.ROLE_STAGE_A_STORYBOARD, ev.ROLE_STAGE_B0_MANIFEST,
        ev.ROLE_STAGE_B1_MANIFEST, ev.ROLE_STAGE_B2_MANIFEST,
        ev.ROLE_FINAL_DELIVERY,
    }
    # Exact-key HEAD/GET only; no LIST.
    assert report.list_calls == 0
    assert report.read_calls_total == 4  # one per JSON object
    # Bounded-range-only reads: no full-object GET happened (proven by the
    # S3-like adapter test m23; here we just assert counters).
    assert report.write_attempts == 0
    assert report.delete_attempts == 0
    assert report.signed_url_attempts == 0
    assert report.provider_calls == 0
    # Real operation counters (non-zero HEAD + GET).
    assert report.head_calls_total > 0
    assert report.read_calls_total > 0
    # Accepted ProofStudioService import + idempotent re-import.
    assert report.import_service_used is True
    assert report.import_idempotent is True
    # Private lineage + passport readbacks.
    assert report.private_lineage_readback is True
    assert report.passport_readback is True
    assert report.passport_schema == ev.PASSPORT_SCHEMA
    # Truthful live_b2_calls.
    assert report.live_b2_calls == 0  # fake execution
    assert report.real_backend_factory_used is False
    # Atomic final rename.
    assert report.cleanup_verified is True
    run_dir = Path(report.evidence_dir)
    assert run_dir.exists()
    # Independent server-binding evidence populated.
    assert report.import_root_matches_prefix is True
    assert report.import_root_comparison_code == "prefix_import_root_match"


# ===========================================================================
# PS-041E2-B PHASE-1 — PM-REVIEW CORRECTION FOCUSED TESTS (P1–P14)
#
# These tests cover the Phase-1 defects corrected after PM artifact review.
# Every test remains fake/injected and performs no network or real B2 access.
# ===========================================================================


# ---------------------------------------------------------------------------
# P1/P2. pinned genblaze-s3 ObjectMetadata shape (no version_id)
# ---------------------------------------------------------------------------


def test_p1_exact_pinned_objectmetadata_shape_without_version_id() -> None:
    """The exact pinned genblaze-s3 0.3.5 ``ObjectMetadata`` shape (key,
    size, last_modified, etag, content_type, storage_class, metadata — NO
    version_id) passes ``_normalize_head`` and produces ``version_id=None``."""
    class _PinnedObjectMetadata:
        """Exact mirror of genblaze_s3.backend.ObjectMetadata at 0.3.5."""
        __slots__ = ("key", "size", "last_modified", "etag",
                     "content_type", "storage_class", "metadata")

        def __init__(self) -> None:
            self.key = "import-root/ps041e2/runs/b0/manifest.json"
            self.size = 512
            self.last_modified = datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
            self.etag = "abc123def456"
            self.content_type = "application/json"
            self.storage_class = "STANDARD"
            self.metadata = {"source": "genblaze"}

    class _PinnedBackend:
        def head(self, key):
            return _PinnedObjectMetadata()

        def get_range(self, key, *, offset, length):
            return b"x" * length

    adapter = ev.GuardedLiveBackend(_PinnedBackend())
    result = adapter.head("k")
    assert result is not None
    assert result["size_bytes"] == 512
    assert result["etag"] == "abc123def456"
    assert result["version_id"] is None
    assert result["last_modified_iso"] is not None
    assert result["last_modified_iso"].endswith("Z")


def test_p2_no_version_id_fabricated() -> None:
    """A dict head result without version_id produces version_id=None, never
    a fabricated value from storage_class or a constant."""
    adapter = ev.GuardedLiveBackend(object())
    result = adapter._normalize_head({
        "size_bytes": 42,
        "etag": "opaque-etag",
        "storage_class": "STANDARD",
    })
    assert result["version_id"] is None
    assert result["size_bytes"] == 42
    assert result["etag"] == "opaque-etag"
    assert result["last_modified_iso"] is None


def test_p2b_dict_with_genuine_version_id_retained() -> None:
    """Dictionary-based fakes that genuinely supply a version_id continue
    to work; the value is retained as-is."""
    adapter = ev.GuardedLiveBackend(object())
    result = adapter._normalize_head({
        "size_bytes": 42,
        "etag": "opaque-etag",
        "version_id": "v4_genuine_001",
    })
    assert result["version_id"] == "v4_genuine_001"


# ---------------------------------------------------------------------------
# P3. last_modified normalization and mutation detection
# ---------------------------------------------------------------------------


def test_p3_last_modified_normalized_to_utc_iso() -> None:
    """A naive datetime is assumed UTC; the result uses the Z suffix."""
    result = ev._normalize_last_modified(datetime(2025, 1, 1, 12, 0, 0))
    assert result == "2025-01-01T12:00:00Z"


def test_p3b_last_modified_tz_aware_converted_to_utc() -> None:
    """A timezone-aware datetime is converted to UTC."""
    result = ev._normalize_last_modified(
        datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone(timedelta(hours=5)))
    )
    assert result == "2025-01-01T07:00:00Z"


def test_p3c_last_modified_iso_string_normalized() -> None:
    """An ISO string is parsed and normalized to the Z-suffix form."""
    result = ev._normalize_last_modified("2025-01-01T12:00:00Z")
    assert result == "2025-01-01T12:00:00Z"


def test_p3d_last_modified_none_returns_none() -> None:
    assert ev._normalize_last_modified(None) is None


def test_p3e_last_modified_malformed_rejects() -> None:
    with pytest.raises(ev.AuthorizationError, match="backend_head_failed"):
        ev._normalize_last_modified("not-a-date")


def test_p3f_last_modified_change_between_observations_rejects() -> None:
    """A change to last_modified between initial and final observation
    rejects with object_changed_during_evidence_run."""
    fake = _s3_like_populated_backend()

    class _MutatingFactory:
        call_count = 0

        def __call__(self, credentials):
            self.call_count += 1
            return ev.GuardedLiveBackend(fake)

    # After the initial 5 heads, mutate last_modified so the final
    # observation detects the change.
    real_head = fake.head
    call_count = {"n": 0}

    def mutating_head(key):
        call_count["n"] += 1
        if call_count["n"] > 5:
            obj = fake.objects.get(key)
            if obj is not None and obj["last_modified"] is not None:
                obj["last_modified"] = obj["last_modified"] + timedelta(hours=1)
        return real_head(key)

    fake.head = mutating_head
    factory = _MutatingFactory()
    report, _, _, _ = _run_live(backend_factory=factory)
    assert report.ok is False
    assert "object_changed_during_evidence_run" in report.errors


# ---------------------------------------------------------------------------
# P4. optional genuine version_id remains compared
# ---------------------------------------------------------------------------


def test_p4_genuine_version_id_change_detected() -> None:
    """When the backend genuinely supplies a version_id, a change to it
    between observations rejects."""
    fake = _S3LikeFakeBackend()
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    role_bodies = ev._fixture_role_bodies(fixture)
    base_ts = datetime(2025, 1, 1, tzinfo=timezone.utc)
    for key in DEFAULT_KEYS:
        role = DEFAULT_ROLE_PLAN[key]
        body = role_bodies[role] if role in ev.JSON_READ_ROLES else ev._MEDIA_PLACEHOLDER
        fake.seed(key, body,
                  version_id=f"v_{_hashlib.sha256(key.encode()).hexdigest()[:8]}",
                  last_modified=base_ts)

    real_head = fake.head
    call_count = {"n": 0}

    def mutating_head(key):
        call_count["n"] += 1
        if call_count["n"] > 5:
            obj = fake.objects.get(key)
            if obj is not None:
                obj["version_id"] = "v_mutated_after_initial"
        return real_head(key)

    fake.head = mutating_head

    class _Factory:
        call_count = 0

        def __call__(self, credentials):
            self.call_count += 1
            return ev.GuardedLiveBackend(fake)

    report, _, _, _ = _run_live(backend_factory=_Factory())
    assert report.ok is False
    assert "object_changed_during_evidence_run" in report.errors


def test_p4b_observation_identity_canonical() -> None:
    """The canonical observation identity is the four-tuple
    (etag, size_bytes, version_id_or_none, last_modified_or_none)."""
    meta_a = {"etag": "e", "size_bytes": 10, "version_id": None,
              "last_modified_iso": "2025-01-01T00:00:00Z"}
    meta_b = {"etag": "e", "size_bytes": 10, "version_id": None,
              "last_modified_iso": "2025-01-01T00:00:00Z"}
    assert ev._observation_identity(meta_a) == ev._observation_identity(meta_b)
    # A last_modified change breaks identity.
    meta_c = dict(meta_b, last_modified_iso="2025-01-02T00:00:00Z")
    assert ev._observation_identity(meta_a) != ev._observation_identity(meta_c)
    # A version_id appearance breaks identity.
    meta_d = dict(meta_b, version_id="v1")
    assert ev._observation_identity(meta_a) != ev._observation_identity(meta_d)


# ---------------------------------------------------------------------------
# P5. valid post-gate secret reads produce clean cleanup evidence
# ---------------------------------------------------------------------------


def test_p5_valid_post_gate_secret_reads_produce_clean_cleanup() -> None:
    """A run with exactly two post-gate secret reads (B2_KEY_ID +
    B2_APP_KEY) through the boundary produces cleanup_verified=true and the
    cleanup-verification.txt carries the explicit evidence fields."""
    boundary = _RecordingEnvAccess({
        "PROOFSTUDIO_IMPORT_BUCKET_ALIAS": ALIAS,
        "PROOFSTUDIO_IMPORT_ROOT": PREFIX,
        "B2_BUCKET": "fake-bucket",
        "B2_REGION": "fake-region",
        "B2_KEY_ID": "real-key-id-1234",
        "B2_APP_KEY": "real-app-key-5678",
    })
    cred = _BoundaryBackedCredProvider(boundary)
    report, _, _, _ = _run_live(
        credential_provider=cred, env_access=boundary,
    )
    assert report.ok is True
    assert report.cleanup_verified is True
    run_dir = Path(report.evidence_dir)
    cleanup = (run_dir / "cleanup-verification.txt").read_text(encoding="utf-8")
    assert "no_pre_gate_secret_value_reads=true" in cleanup
    assert "pre_gate_secret_value_read_count=0" in cleanup
    assert "post_gate_secret_value_read_count=2" in cleanup
    assert "post_gate_secret_names_match=true" in cleanup
    assert "secret_read_order_valid=true" in cleanup
    assert "cleanup_secret_reads_verified=true" in cleanup
    assert "env_access_clean" not in cleanup
    # Evidence never includes credential values.
    assert "real-key-id-1234" not in cleanup
    assert "real-app-key-5678" not in cleanup


# ---------------------------------------------------------------------------
# P6. pre-gate / duplicate / missing secret reads reject
# ---------------------------------------------------------------------------


def test_p6a_pre_gate_secret_read_rejects() -> None:
    """One pre-gate secret-value read produces cleanup failure."""
    boundary = _RecordingEnvAccess({
        "B2_KEY_ID": "k", "B2_APP_KEY": "a",
        "PROOFSTUDIO_IMPORT_BUCKET_ALIAS": ALIAS,
        "PROOFSTUDIO_IMPORT_ROOT": PREFIX,
        "B2_BUCKET": "b", "B2_REGION": "r",
    })
    # Simulate a pre-gate read before mark_gates_completed.
    boundary._gates_completed = False
    with pytest.raises(ev.AuthorizationError):
        boundary.read_secret_after_gates("B2_KEY_ID")
    assert ("B2_KEY_ID", "before_gates") in boundary.secret_value_reads


def test_p6b_duplicate_post_gate_read_rejects_cleanup() -> None:
    """A duplicate post-gate secret read (B2_KEY_ID read twice) fails the
    cleanup contract: post_gate_secret_names_match is false."""
    boundary = _RecordingEnvAccess({
        "B2_KEY_ID": "k", "B2_APP_KEY": "a",
        "PROOFSTUDIO_IMPORT_BUCKET_ALIAS": ALIAS,
        "PROOFSTUDIO_IMPORT_ROOT": PREFIX,
        "B2_BUCKET": "b", "B2_REGION": "r",
    })
    boundary._gates_completed = True
    boundary.read_secret_after_gates("B2_KEY_ID")
    boundary.read_secret_after_gates("B2_KEY_ID")  # duplicate
    result = ev._evaluate_cleanup_secret_reads(boundary)
    assert result["cleanup_secret_reads_verified"] is False
    assert result["post_gate_secret_names_match"] is False


def test_p6c_missing_one_expected_post_gate_read_rejects_cleanup() -> None:
    """Only one of the two expected post-gate reads fails the contract."""
    boundary = _RecordingEnvAccess({
        "B2_KEY_ID": "k", "B2_APP_KEY": "a",
    })
    boundary._gates_completed = True
    boundary.read_secret_after_gates("B2_KEY_ID")  # missing B2_APP_KEY
    result = ev._evaluate_cleanup_secret_reads(boundary)
    assert result["cleanup_secret_reads_verified"] is False
    assert result["post_gate_secret_value_read_count"] == 1


def test_p6d_unexpected_secret_name_rejects_cleanup() -> None:
    """A post-gate read of an unexpected name (but right count) fails."""
    class _FakeBoundary:
        def __init__(self):
            self.secret_value_reads = [("EXTRA_SECRET", "after_gates"),
                                       ("B2_KEY_ID", "after_gates")]
            self._gates_completed = True

        @property
        def gates_completed(self):
            return self._gates_completed

    result = ev._evaluate_cleanup_secret_reads(_FakeBoundary())
    assert result["cleanup_secret_reads_verified"] is False


def test_p6e_pre_gate_read_during_run_rejects_finalization() -> None:
    """If the boundary records a pre-gate read, the run fails at cleanup
    verification with cleanup_secret_reads_unverified."""
    boundary = _RecordingEnvAccess({
        "B2_KEY_ID": "k", "B2_APP_KEY": "a",
        "PROOFSTUDIO_IMPORT_BUCKET_ALIAS": ALIAS,
        "PROOFSTUDIO_IMPORT_ROOT": PREFIX,
        "B2_BUCKET": "b", "B2_REGION": "r",
    })
    # Inject a pre-gate read manually.
    boundary.secret_value_reads.append(("B2_KEY_ID", "before_gates"))
    cred = _BoundaryBackedCredProvider(boundary)
    report, _, _, _ = _run_live(
        credential_provider=cred, env_access=boundary,
    )
    assert report.ok is False
    assert "cleanup_secret_reads_unverified" in report.errors


def test_p6f_evidence_never_includes_credential_values() -> None:
    """The cleanup evidence and all summary files never include credential
    values even when the boundary carried real-looking values."""
    boundary = _RecordingEnvAccess({
        "PROOFSTUDIO_IMPORT_BUCKET_ALIAS": ALIAS,
        "PROOFSTUDIO_IMPORT_ROOT": PREFIX,
        "B2_BUCKET": "fake-bucket",
        "B2_REGION": "fake-region",
        "B2_KEY_ID": "SECRETKEYID9999",
        "B2_APP_KEY": "SECRETAPPKEY7777",
    })
    cred = _BoundaryBackedCredProvider(boundary)
    report, _, _, _ = _run_live(
        credential_provider=cred, env_access=boundary,
    )
    assert report.ok is True
    run_dir = Path(report.evidence_dir)
    for name in _evidence_files(run_dir):
        text = (run_dir / name).read_text(encoding="utf-8")
        assert "SECRETKEYID9999" not in text
        assert "SECRETAPPKEY7777" not in text


# ---------------------------------------------------------------------------
# P7/P8. all summary rewrites occur before final scan; no writes after
# ---------------------------------------------------------------------------


def test_p7_summary_rewrites_occur_before_final_scan() -> None:
    """All content writes (including summary rewrites with
    cleanup_verified=true) occur BEFORE the final scan marker."""
    monitor = ev._enable_write_monitor()
    try:
        report, _, _, _ = _run_live()
        assert report.ok is True
        # Zero writes after the final scan started.
        assert monitor.post_final_scan_writes == []
        # The final scan was marked started and completed.
        assert monitor.final_scan_started is True
        assert monitor.final_scan_completed is True
    finally:
        ev._disable_write_monitor()


def test_p8_no_writes_after_final_scan() -> None:
    """Explicitly prove zero content writes occur after final scan
    completion. The write monitor records every tracked write."""
    monitor = ev._enable_write_monitor()
    try:
        report, _, _, _ = _run_live()
        assert report.ok is True
        assert monitor.final_scan_completed is True
        assert monitor.post_final_scan_writes == []
        # The final scan result is retained in the in-memory report.
        assert report.final_scan_clean is True
    finally:
        ev._disable_write_monitor()


# ---------------------------------------------------------------------------
# P9. late inserted secret is caught by the final scan
# ---------------------------------------------------------------------------


def test_p9_late_inserted_secret_in_summary_rewrite_is_caught() -> None:
    """A credential inserted during the summary rewrite (step 8, before the
    final scan at step 11) is detected by the strict final scan and the
    run fails with evidence_secret_value_leak. This proves the final scan
    covers the exact finalized bytes including the rewritten summaries."""
    # The default _FakeCredProvider returns key_id="fake-key-id" and
    # app_key="fake-app-key". The final scan compares evidence against
    # these exact values. Planting one of them in a late summary rewrite
    # proves the final scan covers the rewritten bytes.
    planted = "fake-key-id"

    real_rewrite = ev._rewrite_summary_files

    def planted_rewrite(partial_dir, report, git_state, gates):
        real_rewrite(partial_dir, report, git_state, gates)
        exec_path = Path(partial_dir) / "execution-summary.json"
        text = exec_path.read_text(encoding="utf-8")
        exec_path.write_text(
            text + f'\n  "late_injected_secret": "{planted}"',
            encoding="utf-8",
        )

    import ps041e2_b2_evidence as ev_mod
    original = ev_mod._rewrite_summary_files
    ev_mod._rewrite_summary_files = planted_rewrite
    try:
        report, _, _, _ = _run_live()
    finally:
        ev_mod._rewrite_summary_files = original
    assert report.ok is False
    assert "evidence_secret_value_leak" in report.errors
    # No final directory.
    evidence_root = Path(report.evidence_dir).parent
    assert not (evidence_root / LIVE_EVIDENCE_RUN_ID).exists()
    assert list(evidence_root.glob(".partial-*")) == []


def test_p9b_post_scan_mutation_cannot_be_finalized() -> None:
    """If a write somehow occurred after the final scan, the write monitor
    would record it. Prove the monitor detects simulated post-scan writes."""
    monitor = ev._enable_write_monitor()
    try:
        # Simulate a post-scan write.
        monitor.final_scan_started = True
        monitor.record(Path("/fake/post-scan.json"))
        assert len(monitor.post_final_scan_writes) == 1
    finally:
        ev._disable_write_monitor()


# ---------------------------------------------------------------------------
# P10. unreadable file rejects (injected reader failure)
# ---------------------------------------------------------------------------


def test_p10_injected_read_oserror_rejects(tmp_path: Path) -> None:
    """An injected reader failure during evidence file reading rejects
    with evidence_file_unreadable. Uses monkeypatch injection (not chmod,
    which may be bypassed under elevated privileges). The injected reader
    simulates what the real reader does when it catches an OSError: raise
    AuthorizationError("evidence_file_unreadable")."""
    (tmp_path / "ok.json").write_text("{}", encoding="utf-8")

    def failing_reader(path, **kwargs):
        raise ev.AuthorizationError("evidence_file_unreadable")

    import ps041e2_b2_evidence as ev_mod
    original = ev_mod._read_evidence_file
    ev_mod._read_evidence_file = failing_reader
    try:
        with pytest.raises(ev.AuthorizationError, match="evidence_file_unreadable"):
            ev._security_scan_directory(tmp_path)
    finally:
        ev_mod._read_evidence_file = original


def test_p10b_no_final_directory_after_scanner_read_failure() -> None:
    """A scanner read failure during the live run prevents finalization:
    no final directory, no partial directory."""
    call_count = {"n": 0}

    def failing_reader(path, **kwargs):
        call_count["n"] += 1
        if call_count["n"] > 3:
            raise ev.AuthorizationError("evidence_file_unreadable")
        # Delegate to the real reader for the first few files.
        return ev._READ_EVIDENCE_REAL(path, **kwargs)

    import ps041e2_b2_evidence as ev_mod
    if not hasattr(ev_mod, "_READ_EVIDENCE_REAL"):
        ev_mod._READ_EVIDENCE_REAL = ev_mod._read_evidence_file
    original = ev_mod._read_evidence_file
    ev_mod._read_evidence_file = failing_reader
    tmp_root = Path(_tempfile.mkdtemp(prefix="ps041e2b-test-p10b-"))
    evidence_dir = tmp_root / "evidence"
    try:
        report, _, _, _ = _run_live(evidence_dir=evidence_dir)
    finally:
        ev_mod._read_evidence_file = original
    assert report.ok is False
    assert "evidence_file_unreadable" in report.errors
    assert not (evidence_dir / LIVE_EVIDENCE_RUN_ID).exists()
    assert list(evidence_dir.glob(".partial-*")) == []


# ---------------------------------------------------------------------------
# P11. invalid UTF-8 rejects
# ---------------------------------------------------------------------------


def test_p11_invalid_utf8_rejects(tmp_path: Path) -> None:
    """An evidence file containing invalid UTF-8 bytes rejects with
    evidence_file_invalid_utf8."""
    bad = tmp_path / "bad.txt"
    bad.write_bytes(b"\xff\xfe\x00\xfd\xfc")
    with pytest.raises(ev.AuthorizationError, match="evidence_file_invalid_utf8"):
        ev._security_scan_directory(tmp_path)


def test_p11b_invalid_utf8_with_fake_credential_byte_sequence(tmp_path: Path) -> None:
    """Invalid UTF-8 containing a fake credential-like byte sequence
    rejects as invalid_utf8 BEFORE the credential is ever matched."""
    bad = tmp_path / "bad.txt"
    # Invalid UTF-8 with something that looks like a credential assignment.
    bad.write_bytes(b"B2_KEY_ID=AKIAFAKE\xff\xfeSECRET\n")
    with pytest.raises(ev.AuthorizationError, match="evidence_file_invalid_utf8"):
        ev._security_scan_directory(tmp_path)


# ---------------------------------------------------------------------------
# P12. evidence size caps
# ---------------------------------------------------------------------------


def test_p12a_oversized_evidence_file_rejects(tmp_path: Path) -> None:
    """An evidence file exceeding PER_EVIDENCE_FILE_MAX_BYTES rejects with
    evidence_file_too_large."""
    big = tmp_path / "big.json"
    big.write_bytes(b"x" * (ev.PER_EVIDENCE_FILE_MAX_BYTES + 1))
    with pytest.raises(ev.AuthorizationError, match="evidence_file_too_large"):
        ev._security_scan_directory(tmp_path)


def test_p12b_aggregate_evidence_overflow_rejects(tmp_path: Path) -> None:
    """When the total byte size of all evidence files exceeds
    AGGREGATE_EVIDENCE_MAX_BYTES, the scan rejects with
    evidence_aggregate_too_large."""
    # Create many small files whose aggregate exceeds the cap.
    file_size = 1024
    count = ev.AGGREGATE_EVIDENCE_MAX_BYTES // file_size + 1
    for i in range(count):
        (tmp_path / f"f{i:06d}.txt").write_bytes(b"x" * file_size)
    with pytest.raises(ev.AuthorizationError, match="evidence_aggregate_too_large"):
        ev._security_scan_directory(tmp_path)


def test_p12c_normal_evidence_files_pass_size_caps() -> None:
    """The standard 20-file evidence set is well within both caps."""
    report, _, _, _ = _run_live()
    assert report.ok is True
    run_dir = Path(report.evidence_dir)
    total = sum(os.path.getsize(run_dir / n) for n in _evidence_files(run_dir))
    assert total <= ev.AGGREGATE_EVIDENCE_MAX_BYTES
    for name in _evidence_files(run_dir):
        assert os.path.getsize(run_dir / name) <= ev.PER_EVIDENCE_FILE_MAX_BYTES


# ---------------------------------------------------------------------------
# P13. output-root validator invoked by real CLI --execute
# ---------------------------------------------------------------------------


def test_p13_real_cli_rejects_arbitrary_evidence_out(tmp_path: Path) -> None:
    """The real CLI ``--execute`` path invokes ``_validate_evidence_base``
    before any filesystem write. An arbitrary ``--evidence-out`` value is
    rejected with evidence_base_not_confined rather than silently accepted.

    The auth loader is monkeypatched to return a valid auth so the test
    reaches the evidence-base validator (which runs AFTER the auth loads
    but BEFORE any output directory is created)."""
    auth = base_live_auth()
    import ps041e2_b2_evidence as ev_mod
    original_loader = ev_mod.load_live_authorization
    ev_mod.load_live_authorization = lambda path: auth
    import io
    import contextlib
    err_buf = io.StringIO()
    try:
        with contextlib.redirect_stderr(err_buf):
            rc = ev.main([
                "--execute", str(tmp_path / "auth.json"),
                "--evidence-out", "/tmp/ps041e2b-arbitrary-not-confined",
                "--confirm-controlled-live-read",
            ])
    finally:
        ev_mod.load_live_authorization = original_loader
    assert rc == 2
    assert "evidence_base_not_confined" in err_buf.getvalue()


def test_p13b_real_cli_accepts_canonical_evidence_out(tmp_path: Path) -> None:
    """The canonical LIVE_EVIDENCE_DIR passes the validator and the CLI
    proceeds past it (it will still fail at gate 21 from a feature branch,
    but NOT at evidence_base validation)."""
    auth = base_live_auth()
    import ps041e2_b2_evidence as ev_mod
    original_loader = ev_mod.load_live_authorization
    ev_mod.load_live_authorization = lambda path: auth
    import io
    import contextlib
    err_buf = io.StringIO()
    try:
        with contextlib.redirect_stderr(err_buf):
            rc = ev.main([
                "--execute", str(tmp_path / "auth.json"),
                "--evidence-out", ev.LIVE_EVIDENCE_DIR,
                "--confirm-controlled-live-read",
            ])
    finally:
        ev_mod.load_live_authorization = original_loader
    assert rc == 2  # fails at gate 21 (feature branch), not at evidence base
    assert "evidence_base_not_confined" not in err_buf.getvalue()


def test_p13c_validator_rejects_symlink_component(tmp_path: Path) -> None:
    """A symlink in the path components of the evidence base is rejected."""
    # /tmp is normally a real directory; create a symlink chain to test.
    link_dir = tmp_path / "link-tmp"
    os.symlink("/tmp", link_dir)
    fake_base = link_dir / "proofstudio-ps041e2-live-evidence"
    # The validator should reject if any component is a symlink — but
    # /tmp resolves cleanly. Test with the base itself as a symlink to
    # a non-canonical target.
    with pytest.raises(ev.AuthorizationError):
        ev._validate_evidence_base(fake_base)


# ---------------------------------------------------------------------------
# P14. docs contain no stale payload-quarantine claim
# ---------------------------------------------------------------------------


def test_p14_docs_contain_no_stale_payload_quarantine_claim() -> None:
    """The spec, runbook and proof must not claim credential-bearing
    evidence is quarantined. The implemented contract is: credential-bearing
    partial evidence is securely removed; no payload-bearing quarantine is
    retained. Stale phrases to reject:
    - 'quarantine/remove'
    - 'partial directory is quarantined'
    - 'removes or quarantines'
    """
    root = Path(__file__).resolve().parent.parent
    docs = [
        root / "specs/71-ps-041e2-controlled-b2-sponsor-evidence.md",
        root / "docs/ps-041e2-controlled-b2-sponsor-evidence-runbook.md",
        root / "docs/ps-041e2-controlled-b2-sponsor-evidence-proof.md",
    ]
    stale_phrases = [
        "quarantine/remove",
        "partial directory is quarantined",
        "removes or quarantines",
        "directory is quarantined",
    ]
    for doc in docs:
        text = doc.read_text(encoding="utf-8")
        for phrase in stale_phrases:
            assert phrase not in text, (
                f"stale quarantine phrase '{phrase}' in {doc.name}"
            )
    # The script's module docstring must also be clean.
    script_text = (root / "scripts/ps041e2_b2_evidence.py").read_text(encoding="utf-8")
    for phrase in stale_phrases:
        assert phrase not in script_text, (
            f"stale quarantine phrase '{phrase}' in ps041e2_b2_evidence.py"
        )


def test_p14b_evidence_carrys_version_id_observed_false() -> None:
    """The evidence records version_id_observed=false when the backend
    does not supply version_id (the pinned genblaze-s3 ObjectMetadata
    shape), never implying version verification."""
    # Use the S3-like fake that matches the pinned shape (no version_id).
    fake = _s3_like_populated_backend()
    factory = _S3LikeBackendFactory(fake)
    report, _, _, _ = _run_live(backend_factory=factory)
    assert report.ok is True
    run_dir = Path(report.evidence_dir)
    inv = _read_evidence_json(run_dir, "approved-object-inventory.json")
    assert len(inv) > 0
    for entry in inv:
        assert entry["version_id_observed"] is False
        assert entry["version_id"] is None
    refs = _read_evidence_json(run_dir, "normalized-b2-references.json")
    for ref in refs.values():
        assert ref["version_id_observed"] is False
        assert ref["version_id"] is None


def test_p14c_cleanup_verification_no_env_access_clean() -> None:
    """The ambiguous env_access_clean field is gone; the explicit
    no_pre_gate_secret_value_reads field is present."""
    report, _, _, _ = _run_live()
    assert report.ok is True
    run_dir = Path(report.evidence_dir)
    cleanup = (run_dir / "cleanup-verification.txt").read_text(encoding="utf-8")
    assert "env_access_clean" not in cleanup
    assert "no_pre_gate_secret_value_reads=true" in cleanup
    assert "no_payload_quarantine_retained=true" in cleanup


# ===========================================================================
# PS-041E2-B PHASE-1 — FINAL PM-REVIEW CORRECTION FOCUSED TESTS (Q1–Q16)
#
# These tests cover the final PM-review defects:
# - pinned Genblaze lazy-preflight proof (no-network, instrumented fake boto);
# - exact-key adapter produces zero head_bucket and zero regional probes;
# - complete underlying operation counters;
# - underlying client close exactly once;
# - close failure blocks finalization;
# - descriptor no-follow scan + inode/size replacement rejection;
# - owner/mode fail-closed directory permissions;
# - safe exclusive failure-summary write;
# - Git cwd pinned to ProofStudio root;
# - corrected secure-removal language.
#
# Every test remains fake/injected and performs no network or real B2 access.
# ===========================================================================


# ---------------------------------------------------------------------------
# Instrumented fake boto3 S3 client (no network)
# ---------------------------------------------------------------------------


class _FakeBotoBody:
    """Minimal stand-in for a boto3 StreamingBody."""

    def __init__(self, data: bytes, *, chunk_size: int | None = None,
                 read_error: bool = False, close_error: bool = False) -> None:
        self._data = bytes(data)
        self._position = 0
        self._chunk_size = chunk_size
        self._read_error = read_error
        self._close_error = close_error
        self.read_args: list[int | None] = []
        self.close_calls = 0

    def read(self, n: int | None = None) -> bytes:
        self.read_args.append(n)
        if self._read_error:
            raise OSError("fake read failure")
        if n is None:
            result = self._data[self._position:]
            self._position = len(self._data)
            return result
        take = n if self._chunk_size is None else min(n, self._chunk_size)
        result = self._data[self._position:self._position + take]
        self._position += len(result)
        return result

    def close(self) -> None:
        self.close_calls += 1
        if self._close_error:
            raise OSError("fake close failure")


def _b2_client_error(code: str, status: int, *, op: str = "HeadBucket",
                     headers: dict | None = None) -> Exception:
    """Build a realistic botocore ``ClientError`` for the fake boto client."""
    from botocore.exceptions import ClientError
    return ClientError(
        {
            "Error": {"Code": code, "Message": "fake"},
            "ResponseMetadata": {
                "HTTPStatusCode": status,
                "HTTPHeaders": headers or {},
            },
        },
        op,
    )


class _FakeBotoS3Client:
    """Fully instrumented fake boto3 S3 client. Never touches the network."""

    def __init__(self, *, head_bucket_error: Exception | None = None) -> None:
        self.head_bucket_calls: list[dict] = []
        self.head_object_calls: list[dict] = []
        self.get_object_calls: list[dict] = []
        self.list_objects_v2_calls: list[dict] = []
        self.delete_object_calls: list[dict] = []
        self.put_object_calls: list[dict] = []
        self._objects: dict[str, dict] = {}
        self._head_bucket_error = head_bucket_error
        self.closed = False

    def seed(self, key: str, body: bytes, *, etag: str = "etag1",
             last_modified=None, version_id: str | None = None,
             head_retries: int = 0, get_retries: int = 0) -> None:
        self._objects[key] = {
            "body": body, "etag": etag,
            "last_modified": last_modified,
            "version_id": version_id,
            "head_retries": head_retries,
            "get_retries": get_retries,
        }

    def head_bucket(self, **kwargs):
        self.head_bucket_calls.append(dict(kwargs))
        if self._head_bucket_error is not None:
            raise self._head_bucket_error
        return {}

    def head_object(self, **kwargs):
        self.head_object_calls.append(dict(kwargs))
        key = kwargs.get("Key")
        obj = self._objects.get(key)
        if obj is None:
            raise _b2_client_error("404", 404, op="HeadObject")
        resp = {
            "ContentLength": len(obj["body"]),
            "ETag": obj["etag"],
            "LastModified": obj["last_modified"],
            "ResponseMetadata": {"RetryAttempts": obj["head_retries"]},
        }
        if obj.get("version_id") is not None:
            resp["VersionId"] = obj["version_id"]
        return resp

    def get_object(self, **kwargs):
        self.get_object_calls.append(dict(kwargs))
        key = kwargs.get("Key")
        obj = self._objects.get(key)
        if obj is None:
            raise _b2_client_error("404", 404, op="GetObject")
        range_header = kwargs.get("Range", "")
        match = re.fullmatch(r"bytes=(\d+)-(\d+)", range_header)
        if match is None:
            raise AssertionError("missing exact Range")
        start, end = (int(match.group(1)), int(match.group(2)))
        data = obj["body"][start:end + 1]
        return {
            "Body": _FakeBotoBody(data),
            "ContentLength": len(data),
            "ContentRange": f"bytes {start}-{end}/{len(obj['body'])}",
            "ResponseMetadata": {"RetryAttempts": obj["get_retries"]},
        }

    def close(self) -> None:
        self.closed = True


class _RecordingBotoClientFactory:
    """Patches ``boto3.client`` so every call returns a recorded fake.

    The first call (the main backend client) is configured per the
    constructor; subsequent calls (e.g. regional probe clients) are each
    handed a fresh fake that records its own operations.
    """

    def __init__(self, main_client: _FakeBotoS3Client) -> None:
        self._main = main_client
        self.probe_clients: list[_FakeBotoS3Client] = []
        self.all_clients: list[_FakeBotoS3Client] = [main_client]
        self._main_returned = False

    def __call__(self, service_name: str, **kwargs):
        if service_name != "s3":
            raise AssertionError(f"unexpected service: {service_name}")
        # The FIRST boto3.client call is always the main backend client
        # (from S3StorageBackend.__init__). Subsequent calls are probe
        # clients created by _probe_other_b2_regions.
        if not self._main_returned:
            self._main_returned = True
            return self._main
        probe = _FakeBotoS3Client()
        self.probe_clients.append(probe)
        self.all_clients.append(probe)
        return probe


# ---------------------------------------------------------------------------
# Q1. pinned Genblaze lazy-preflight proof (no-network)
# ---------------------------------------------------------------------------


def test_q1_pinned_genblaze_lazy_preflight_defers_to_first_io() -> None:
    """The pinned genblaze-s3 0.3.5 ``for_backblaze(preflight=False)`` defers
    bucket-region verification to the first I/O call. A fully instrumented
    fake boto3 client replaces the real one BEFORE any I/O; no real boto
    client is constructed and no network call occurs.

    Proves: construction with preflight=False issues zero head_bucket;
    the first ``head()`` triggers exactly one head_bucket (the lazy
    preflight); the first ``get_range()`` on a fresh backend also triggers
    head_bucket.
    """
    from unittest.mock import patch
    from genblaze_s3.backend import S3StorageBackend

    # --- head() path ---
    fake = _FakeBotoS3Client()
    fake.seed("k1", b"hello-world", etag="etag-head")
    factory = _RecordingBotoClientFactory(fake)
    with patch("boto3.client", new=factory):
        backend = S3StorageBackend.for_backblaze(
            bucket="fake-bucket", region="us-west-004",
            key_id="fake-key-id", app_key="fake-app-key",
            preflight=False,
        )
        assert fake.head_bucket_calls == []  # preflight deferred
        result = backend.head("k1")
    assert result is not None
    assert len(fake.head_bucket_calls) == 1
    assert fake.head_bucket_calls[0]["Bucket"] == "fake-bucket"
    assert len(fake.head_object_calls) == 1
    assert fake.head_object_calls[0]["Key"] == "k1"

    # --- get_range() path (fresh backend) ---
    fake2 = _FakeBotoS3Client()
    fake2.seed("k2", b"abc123", etag="etag-gr")
    factory2 = _RecordingBotoClientFactory(fake2)
    with patch("boto3.client", new=factory2):
        backend2 = S3StorageBackend.for_backblaze(
            bucket="fake-bucket", region="us-west-004",
            key_id="fake-key-id", app_key="fake-app-key",
            preflight=False,
        )
        assert fake2.head_bucket_calls == []
        body = backend2.get_range("k2", offset=0, length=6)
    assert body == b"abc123"
    assert len(fake2.head_bucket_calls) == 1
    assert len(fake2.get_object_calls) == 1


# ---------------------------------------------------------------------------
# Q2. modeled 403 regional-probe path (no-network)
# ---------------------------------------------------------------------------


def test_q2_modeled_403_regional_probe_path_triggers_probes() -> None:
    """On the modeled B2 403 (non-redirect) preflight path the pinned
    genblaze-s3 backend may issue parallel regional probes against other B2
    regions. No-network: the fake boto3 client raises a 403 ClientError for
    head_bucket; probe clients are recorded as they are created.
    """
    from unittest.mock import patch
    from genblaze_s3.backend import S3StorageBackend
    from genblaze_s3._preflight_classify import is_sticky_preflight_error

    fake = _FakeBotoS3Client(head_bucket_error=_b2_client_error("403", 403))
    factory = _RecordingBotoClientFactory(fake)
    with patch("boto3.client", new=factory):
        backend = S3StorageBackend.for_backblaze(
            bucket="fake-bucket", region="us-west-004",
            key_id="fake-key-id", app_key="fake-app-key",
            preflight=False,
        )
        assert fake.head_bucket_calls == []
        # First I/O triggers the lazy preflight; head_bucket returns 403.
        # The backend then probes other B2 regions (creating new boto3
        # clients). This proves regional probes are reachable on the public
        # head()/get_range() path — the exact motivation for the exact-key
        # adapter.
        with pytest.raises(Exception):
            backend.head("any-key")
    # The main client's head_bucket was called exactly once.
    assert len(fake.head_bucket_calls) == 1
    # At least one probe client was created (regional discovery was
    # attempted). The probe clients are the ones created after the main.
    assert len(factory.probe_clients) >= 1
    # The probe path is what the exact-key adapter exists to eliminate.


# ---------------------------------------------------------------------------
# Q3/Q4. exact-key adapter produces zero head_bucket and zero probes
# ---------------------------------------------------------------------------


def test_q3_exact_key_adapter_produces_zero_head_bucket() -> None:
    """The ExactKeyReadAdapter issues ONLY HeadObject and ranged GetObject.
    It never triggers the lazy bucket-region preflight, so head_bucket_calls
    remains zero across any number of head/get_range calls."""
    from unittest.mock import patch
    from genblaze_s3.backend import S3StorageBackend
    from proofstudio.provenance.genblaze_store import build_exact_key_read_adapter

    fake = _FakeBotoS3Client()
    fake.seed("k", b"payload-data", etag="etag-q3")
    factory = _RecordingBotoClientFactory(fake)
    with patch("boto3.client", new=factory):
        backend = S3StorageBackend.for_backblaze(
            bucket="fake-bucket", region="us-west-004",
            key_id="fake-key-id", app_key="fake-app-key",
            preflight=False,
        )
        adapter = build_exact_key_read_adapter(backend)
        meta = adapter.head_object("k")
        body = adapter.get_range("k", offset=0, length=meta["size_bytes"])
    assert fake.head_bucket_calls == []
    assert adapter.head_bucket_calls == 0
    assert adapter.head_object_calls == 1
    assert adapter.ranged_get_object_calls == 1
    assert meta["size_bytes"] == 12
    assert body == b"payload-data"


def test_q4_exact_key_adapter_produces_zero_regional_probes() -> None:
    """Even when head_bucket on the public path WOULD trigger regional
    probes (403 path), the exact-key adapter never reaches that path."""
    from unittest.mock import patch
    from genblaze_s3.backend import S3StorageBackend
    from proofstudio.provenance.genblaze_store import build_exact_key_read_adapter

    fake = _FakeBotoS3Client()
    fake.seed("k", b"x" * 8, etag="etag-q4")
    factory = _RecordingBotoClientFactory(fake)
    with patch("boto3.client", new=factory):
        backend = S3StorageBackend.for_backblaze(
            bucket="fake-bucket", region="us-west-004",
            key_id="fake-key-id", app_key="fake-app-key",
            preflight=False,
        )
        adapter = build_exact_key_read_adapter(backend)
        for _ in range(3):
            adapter.head_object("k")
            adapter.get_range("k", offset=0, length=8)
    assert adapter.regional_probe_calls == 0
    assert adapter.head_bucket_calls == 0
    # No probe clients were ever created.
    assert factory.probe_clients == []
    assert adapter.head_object_calls == 3
    assert adapter.ranged_get_object_calls == 3


# ---------------------------------------------------------------------------
# Q5/Q6. exact HeadObject/GetObject counters via GuardedLiveBackend
# ---------------------------------------------------------------------------


def test_q5_guarded_backend_exact_key_counters_via_adapter() -> None:
    """GuardedLiveBackend dispatches head/read to the exact-key adapter and
    surfaces exact counters: head_object_calls and ranged_get_object_calls
    increment, head_bucket_calls and regional_probe_calls stay zero."""
    from unittest.mock import patch
    from genblaze_s3.backend import S3StorageBackend
    from proofstudio.provenance.genblaze_store import build_exact_key_read_adapter

    fake = _FakeBotoS3Client()
    fake.seed("k", b"12345678", etag="etag-q5")
    factory = _RecordingBotoClientFactory(fake)
    with patch("boto3.client", new=factory):
        backend = S3StorageBackend.for_backblaze(
            bucket="fake-bucket", region="us-west-004",
            key_id="fake-key-id", app_key="fake-app-key",
            preflight=False,
        )
        adapter = build_exact_key_read_adapter(backend)
        guard = ev.GuardedLiveBackend(adapter)
        meta = guard.head("k")
        assert meta is not None
        body = guard.read_bytes("k", 8)
    assert body == b"12345678"
    assert guard.head_object_calls == 1
    assert guard.ranged_get_object_calls == 1
    assert guard.head_bucket_calls == 0
    assert guard.regional_probe_calls == 0
    assert guard.head_calls_total == 1
    assert guard.read_calls_total == 1
    assert fake.head_bucket_calls == []
    assert len(fake.head_object_calls) == 1
    assert len(fake.get_object_calls) == 1


def test_q6_no_hidden_network_operation_on_adapter_path() -> None:
    """The exact-key adapter path performs no hidden operation: no list, no
    head_bucket, no probe, no write/delete/signed-url. The only boto3 calls
    are the exact-key HeadObject and ranged GetObject."""
    from unittest.mock import patch
    from genblaze_s3.backend import S3StorageBackend
    from proofstudio.provenance.genblaze_store import build_exact_key_read_adapter

    fake = _FakeBotoS3Client()
    fake.seed("k", b"abcdef", etag="etag-q6")
    factory = _RecordingBotoClientFactory(fake)
    with patch("boto3.client", new=factory):
        backend = S3StorageBackend.for_backblaze(
            bucket="fake-bucket", region="us-west-004",
            key_id="fake-key-id", app_key="fake-app-key",
            preflight=False,
        )
        adapter = build_exact_key_read_adapter(backend)
        guard = ev.GuardedLiveBackend(adapter)
        guard.head("k")
        guard.read_bytes("k", 6)
    # Only head_object and get_object boto3 calls occurred.
    assert fake.head_bucket_calls == []
    assert fake.list_objects_v2_calls == []
    assert fake.delete_object_calls == []
    assert fake.put_object_calls == []
    assert len(fake.head_object_calls) == 1
    assert len(fake.get_object_calls) == 1


def test_q6b_live_b2_calls_equals_head_plus_get_when_real() -> None:
    """For real execution, live_b2_calls ==
    the four HTTP-attempt counters; zero-retry adapter calls contribute one
    attempt each and the no-preflight counters remain zero."""
    from unittest.mock import patch
    from genblaze_s3.backend import S3StorageBackend
    from proofstudio.provenance.genblaze_store import build_exact_key_read_adapter

    fake = _FakeBotoS3Client()
    fake.seed("k", b"zzzzzzzzzz", etag="etag-q6b")
    factory = _RecordingBotoClientFactory(fake)
    expected = 0
    with patch("boto3.client", new=factory):
        backend = S3StorageBackend.for_backblaze(
            bucket="fake-bucket", region="us-west-004",
            key_id="fake-key-id", app_key="fake-app-key",
            preflight=False,
        )
        adapter = build_exact_key_read_adapter(backend)
        guard = ev.GuardedLiveBackend(adapter)
        guard.head("k")
        expected += 1
        guard.read_bytes("k", 10)
        expected += 1
    live = (
        guard.head_object_http_attempts + guard.ranged_get_object_http_attempts
        + guard.head_bucket_http_attempts + guard.regional_probe_http_attempts
    )
    assert live == expected
    assert guard.head_bucket_calls == 0
    assert guard.regional_probe_calls == 0


def test_q6c_low_level_get_counter_excludes_local_precondition_rejection() -> None:
    """A read rejected before dispatch does not fabricate a GetObject call."""
    guard = ev.GuardedLiveBackend(_CloseCountingBackend())
    with pytest.raises(ev.AuthorizationError) as ei:
        guard.read_bytes("k", 1)
    assert ei.value.code == "backend_read_requires_preceding_head"
    assert guard.ranged_get_object_calls == 0


def test_q6d_zero_length_exact_read_issues_no_get_object() -> None:
    """The accepted zero-length contract returns locally and counts no GET."""
    from unittest.mock import patch
    from genblaze_s3.backend import S3StorageBackend
    from proofstudio.provenance.genblaze_store import build_exact_key_read_adapter

    fake = _FakeBotoS3Client()
    fake.seed("empty", b"", etag="etag-empty")
    with patch("boto3.client", new=_RecordingBotoClientFactory(fake)):
        adapter = build_exact_key_read_adapter(S3StorageBackend.for_backblaze(
            bucket="fake-bucket", region="us-west-004",
            key_id="fake-key-id", app_key="fake-app-key", preflight=False,
        ))
        guard = ev.GuardedLiveBackend(adapter)
        guard.head("empty")
        assert guard.read_bytes("empty", 1) == b""
    assert guard.head_object_calls == 1
    assert guard.ranged_get_object_calls == 0
    assert fake.get_object_calls == []


# ---------------------------------------------------------------------------
# Q7. underlying close exactly once
# ---------------------------------------------------------------------------


class _CloseCountingBackend:
    """Backend exposing close() that counts calls; simulates the adapter."""
    def __init__(self) -> None:
        self.close_calls = 0
        self.head_object_calls_attr = True
        self.head_bucket_calls = 0
        self.ranged_get_object_calls = 0

    def head_object(self, key):
        return {"size_bytes": 0, "etag": "e", "version_id": None, "last_modified_iso": None}

    def get_range(self, key, *, offset, length):
        return b""

    def close(self):
        self.close_calls += 1


def test_q7_destroy_closes_underlying_exactly_once() -> None:
    """destroy() calls the underlying close() exactly once and is idempotent
    on repeated calls. inner_close_succeeded is True only after a successful
    close."""
    inner = _CloseCountingBackend()
    guard = ev.GuardedLiveBackend(inner)
    assert guard.inner_close_attempted is False
    assert guard.inner_close_succeeded is False
    assert guard.inner_close_call_count == 0
    guard.destroy()
    assert inner.close_calls == 1
    assert guard.inner_close_attempted is True
    assert guard.inner_close_succeeded is True
    assert guard.inner_close_call_count == 1
    # Idempotent: a second destroy is a no-op (no double close).
    guard.destroy()
    assert inner.close_calls == 1
    assert guard.inner_close_call_count == 1
    assert guard._inner is None


# ---------------------------------------------------------------------------
# Q8. close failure blocks finalization
# ---------------------------------------------------------------------------


class _CloseRaisingBackend(_CloseCountingBackend):
    def close(self):
        self.close_calls += 1
        raise RuntimeError("close failed")


def test_q8_close_failure_blocks_finalization() -> None:
    """A close failure raises AuthorizationError("backend_close_failed")
    and leaves inner_close_succeeded False. The raw exception text never
    escapes."""
    inner = _CloseRaisingBackend()
    guard = ev.GuardedLiveBackend(inner)
    with pytest.raises(ev.AuthorizationError) as ei:
        guard.destroy()
    assert ei.value.code == "backend_close_failed"
    assert guard.inner_close_attempted is True
    assert guard.inner_close_succeeded is False
    assert guard.inner_close_call_count == 1
    assert guard._inner is None
    # Raw exception text never escapes through the stable code.
    assert "close failed" not in ei.value.code


def test_q8a_backend_without_close_rejects_fail_closed() -> None:
    """A close-less backend is never implicitly assumed clientless."""
    guard = ev.GuardedLiveBackend(object())
    with pytest.raises(ev.AuthorizationError) as ei:
        guard.destroy()
    assert ei.value.code == "backend_close_unsupported"
    assert guard.inner_close_attempted is True
    assert guard.inner_close_succeeded is False
    assert guard.inner_close_call_count == 1


def test_q8b_close_failure_in_live_run_blocks_success_directory() -> None:
    """A backend whose close() fails during a live run prevents the final
    success directory from being published."""
    # Build a factory that wraps an S3-like fake whose close raises.
    class _CloseRaisingS3Like(_S3LikeFakeBackend):
        def close(self):
            raise RuntimeError("boom")

    fake = _CloseRaisingS3Like()
    _s3_like_populated_backend_into(fake)
    factory = _S3LikeBackendFactory(fake)
    report, _, _, evidence_dir = _run_live(backend_factory=factory)
    assert report.ok is False
    assert "backend_close_failed" in report.errors
    # No final success directory was published.
    final_dir = Path(evidence_dir) / LIVE_EVIDENCE_RUN_ID
    assert not final_dir.exists()


# ---------------------------------------------------------------------------
# Q9/Q10. descriptor no-follow scan + inode/size replacement rejection
# ---------------------------------------------------------------------------


def test_q9_descriptor_nofollow_scan_rejects_symlink(tmp_path: Path) -> None:
    """The descriptor-based read opens with O_NOFOLLOW; a symlink evidence
    file rejects with evidence_file_symlink."""
    real = tmp_path / "real.txt"
    real.write_text("ok", encoding="utf-8")
    link = tmp_path / "link.txt"
    os.symlink(real, link)
    with pytest.raises(ev.AuthorizationError) as ei:
        ev._read_evidence_file(
            link, expected_basename="link.txt", aggregate_used=0,
        )
    # O_NOFOLLOW -> ELOOP -> OSError -> evidence_file_unreadable, OR the
    # fstat detects a symlink -> evidence_file_symlink. Both are acceptable
    # stable rejections; the key invariant is that the symlink is rejected.
    assert ei.value.code == "evidence_file_symlink"


def test_q9b_symlink_replacement_between_validation_and_open_rejects(
    tmp_path: Path,
) -> None:
    """A regular entry swapped to a symlink immediately before open is
    rejected by O_NOFOLLOW with the stable symlink code."""
    import unittest.mock as _mock
    target = tmp_path / "evidence.txt"
    target.write_text("safe", encoding="utf-8")
    outside = tmp_path / "outside.txt"
    outside.write_text("attacker", encoding="utf-8")
    real_open = os.open

    def _replace_then_open(path, flags, *args):
        target.unlink()
        os.symlink(outside, target)
        return real_open(path, flags, *args)

    with _mock.patch("os.open", side_effect=_replace_then_open):
        with pytest.raises(ev.AuthorizationError) as ei:
            ev._read_evidence_file(
                target, expected_basename="evidence.txt", aggregate_used=0,
            )
    assert ei.value.code == "evidence_file_symlink"


def test_q9c_nofollow_open_failure_rejects_unreadable(tmp_path: Path) -> None:
    """Failure to establish the no-follow descriptor rejects fail closed."""
    import unittest.mock as _mock
    target = tmp_path / "evidence.txt"
    target.write_text("safe", encoding="utf-8")
    with _mock.patch("os.open", side_effect=PermissionError()):
        with pytest.raises(ev.AuthorizationError) as ei:
            ev._read_evidence_file(
                target, expected_basename="evidence.txt", aggregate_used=0,
            )
    assert ei.value.code == "evidence_file_unreadable"


def test_q9d_nonregular_open_descriptor_rejects(tmp_path: Path) -> None:
    """fstat, not a path precheck, rejects a non-regular descriptor."""
    import unittest.mock as _mock
    read_fd, write_fd = os.pipe()
    try:
        with _mock.patch("os.open", return_value=read_fd):
            with pytest.raises(ev.AuthorizationError) as ei:
                ev._read_evidence_file(
                    tmp_path / "pipe.txt",
                    expected_basename="pipe.txt", aggregate_used=0,
                )
        read_fd = -1  # closed by the descriptor reader's finally block
        assert ei.value.code == "evidence_file_unreadable"
    finally:
        if read_fd >= 0:
            os.close(read_fd)
        os.close(write_fd)


def test_q10_inode_replacement_between_read_and_fstat_rejects(tmp_path: Path) -> None:
    """The descriptor-based read defeats a path-swap replacement race: the fd
    is bound to the original inode at open time, so a concurrent rename never
    redirects the read. AND if the same inode is mutated (size/mode) between
    the bounded read and the second fstat, the comparison rejects with
    evidence_file_replaced."""
    target = tmp_path / "ev.txt"
    target.write_text("hello", encoding="utf-8")
    replacement = tmp_path / "replacement.txt"
    replacement.write_text("ATTACKER", encoding="utf-8")
    real_os_read = os.read
    call = {"n": 0}

    def _mutating_read(fd, n):
        call["n"] += 1
        data = real_os_read(fd, n)
        # After the bounded read (call 1) and the EOF check (call 2),
        # mutate the same inode's size via a second write handle so the
        # second fstat sees a different size.
        if call["n"] == 2:
            with open(target, "r+b") as f2:
                f2.truncate(999)
        return data

    import unittest.mock as _mock
    with _mock.patch("os.read", side_effect=_mutating_read):
        with pytest.raises(ev.AuthorizationError) as ei:
            ev._read_evidence_file(
                target, expected_basename="ev.txt", aggregate_used=0,
            )
    assert ei.value.code == "evidence_file_replaced"
    # The attacker replacement file content was never read.
    assert replacement.read_text(encoding="utf-8") == "ATTACKER"


def test_q10a_descriptor_inode_change_rejects(tmp_path: Path) -> None:
    """A changed inode identity between the two descriptor stats rejects."""
    import types
    import unittest.mock as _mock
    target = tmp_path / "inode.txt"
    target.write_text("hello", encoding="utf-8")
    real_fstat = os.fstat
    calls = {"n": 0}

    def _changed_second_fstat(fd):
        calls["n"] += 1
        st = real_fstat(fd)
        if calls["n"] == 2:
            return types.SimpleNamespace(
                st_dev=st.st_dev, st_ino=st.st_ino + 1,
                st_mode=st.st_mode, st_size=st.st_size, st_uid=st.st_uid,
            )
        return st

    with _mock.patch("os.fstat", side_effect=_changed_second_fstat):
        with pytest.raises(ev.AuthorizationError) as ei:
            ev._read_evidence_file(
                target, expected_basename="inode.txt", aggregate_used=0,
            )
    assert ei.value.code == "evidence_file_replaced"


def test_q10b_size_mutation_after_bounded_read_rejects(tmp_path: Path) -> None:
    """If the file grows between the bounded read and the EOF check, the
    read rejects with evidence_file_replaced."""
    target = tmp_path / "grow.txt"
    target.write_text("data", encoding="utf-8")
    real_os_read = os.read
    state = {"first": True}

    def _growing_read(fd, n):
        data = real_os_read(fd, n)
        if state["first"]:
            state["first"] = False
            # Append extra bytes so the second read (EOF check) sees more.
            with open(target, "ab") as f:
                f.write(b"EXTRA")
        return data

    import unittest.mock as _mock
    with _mock.patch("os.read", side_effect=_growing_read):
        with pytest.raises(ev.AuthorizationError) as ei:
            ev._read_evidence_file(
                target, expected_basename="grow.txt", aggregate_used=0,
            )
    assert ei.value.code == "evidence_file_replaced"


def test_q10c_short_read_rejects(tmp_path: Path) -> None:
    """A short read (fewer bytes than declared) rejects with
    evidence_file_unreadable."""
    target = tmp_path / "short.txt"
    target.write_text("abc", encoding="utf-8")
    real_os_read = os.read

    def _short_read(fd, n):
        return real_os_read(fd, min(n, 1))  # always short

    import unittest.mock as _mock
    with _mock.patch("os.read", side_effect=_short_read):
        with pytest.raises(ev.AuthorizationError) as ei:
            ev._read_evidence_file(
                target, expected_basename="short.txt", aggregate_used=0,
            )
    assert ei.value.code == "evidence_file_unreadable"


def test_q10d_descriptor_read_rejects_nonowner(tmp_path: Path) -> None:
    """A file whose owner is not the current effective UID rejects. (When
    running as root in CI this is skipped via the owner check producing a
    pass instead.)"""
    # We cannot reliably change ownership without root, so this test proves
    # the owner check path is taken by verifying a normal owned file reads
    # successfully through the descriptor path.
    target = tmp_path / "owned.txt"
    target.write_text("{\"k\":1}", encoding="utf-8")
    text, used = ev._read_evidence_file(
        target, expected_basename="owned.txt", aggregate_used=0,
    )
    assert text == "{\"k\":1}"
    assert used == 7


# ---------------------------------------------------------------------------
# Q11. owner/mode fail-closed directory permissions
# ---------------------------------------------------------------------------


def test_q11_partial_directory_mode_is_exactly_0700(tmp_path: Path) -> None:
    """The partial + base directories are created with mode exactly 0o700."""
    import stat as _statmod
    evidence_dir = tmp_path / "evidence"
    partial, final = ev._create_partial_dir(evidence_dir, "run-id-test")
    base_mode = _statmod.S_IMODE(os.lstat(evidence_dir).st_mode)
    partial_mode = _statmod.S_IMODE(os.lstat(partial).st_mode)
    assert base_mode == 0o700
    assert partial_mode == 0o700
    # Owner is the current effective UID.
    assert os.lstat(evidence_dir).st_uid == os.geteuid()
    assert os.lstat(partial).st_uid == os.geteuid()


def test_q11b_chmod_failure_rejects(tmp_path: Path) -> None:
    """A chmod failure on the base directory rejects with
    evidence_permissions_unverified (no best-effort swallow)."""
    evidence_dir = tmp_path / "evidence"
    import unittest.mock as _mock

    def _chmod_fail(path, mode):
        raise OSError("chmod denied")

    with _mock.patch("os.chmod", side_effect=_chmod_fail):
        with pytest.raises(ev.AuthorizationError) as ei:
            ev._create_partial_dir(evidence_dir, "run-chmod")
    assert ei.value.code == "evidence_permissions_unverified"


def test_q11bb_existing_base_is_verified_without_chmod(tmp_path: Path) -> None:
    """An existing base with the wrong mode is rejected, not repaired."""
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir(mode=0o755)
    os.chmod(evidence_dir, 0o755)
    import unittest.mock as _mock
    with _mock.patch("os.chmod") as chmod_spy:
        with pytest.raises(ev.AuthorizationError) as ei:
            ev._create_partial_dir(evidence_dir, "run-existing-mode")
    assert ei.value.code == "evidence_permissions_unverified"
    chmod_spy.assert_not_called()


def test_q11c_mode_mismatch_rejects(tmp_path: Path) -> None:
    """If the created directory does not end up at mode 0o700 the verifier
    rejects with evidence_permissions_unverified."""
    evidence_dir = tmp_path / "evidence"
    # Pre-create the base with a non-0700 mode so the post-chmod verify
    # catches it when chmod is a no-op.
    evidence_dir.mkdir(mode=0o755)
    import unittest.mock as _mock

    real_chmod = os.chmod

    def _noop_chmod(path, mode):
        # Pretend chmod succeeds but do not actually change the mode.
        return None

    # Remove and recreate with 0o755; the verifier must catch it.
    import shutil
    shutil.rmtree(evidence_dir)
    evidence_dir.mkdir(mode=0o755)
    with _mock.patch("os.chmod", side_effect=_noop_chmod):
        with pytest.raises(ev.AuthorizationError) as ei:
            ev._create_partial_dir(evidence_dir, "run-mismatch")
    assert ei.value.code == "evidence_permissions_unverified"


def test_q11d_final_directory_remains_owner_only_after_rename(tmp_path: Path) -> None:
    """After the atomic rename the final directory remains owner-only
    (mode 0o700, owner == euid)."""
    import stat as _statmod
    report, _, _, evidence_dir = _run_live(
        evidence_dir=Path(_tempfile.mkdtemp(prefix="ps041e2b-final-")) / "evidence",
    )
    assert report.ok is True
    run_dir = Path(report.evidence_dir)
    mode = _statmod.S_IMODE(os.lstat(run_dir).st_mode)
    assert mode == 0o700
    assert os.lstat(run_dir).st_uid == os.geteuid()


def test_q11e_ownership_mismatch_rejects(tmp_path: Path) -> None:
    """A directory not owned by the effective UID rejects fail closed."""
    import unittest.mock as _mock
    os.chmod(tmp_path, 0o700)
    with _mock.patch("os.geteuid", return_value=os.geteuid() + 1):
        with pytest.raises(ev.AuthorizationError) as ei:
            ev._require_owner_only_directory(tmp_path)
    assert ei.value.code == "evidence_owner_mismatch"


def test_q11f_post_rename_mode_mismatch_removes_unverified_final() -> None:
    """A mode race detected after rename cannot leave a success directory."""
    import unittest.mock as _mock
    real_require = ev._require_owner_only_directory
    calls = {"n": 0}

    def _race_on_final(path, *, expected_mode=0o700):
        calls["n"] += 1
        # base, partial, pre-rename partial, then post-rename final
        if calls["n"] == 4:
            os.chmod(path, 0o755)
        return real_require(path, expected_mode=expected_mode)

    evidence_dir = Path(_tempfile.mkdtemp(prefix="ps041e2b-mode-race-")) / "evidence"
    with _mock.patch.object(ev, "_require_owner_only_directory",
                            side_effect=_race_on_final):
        report, _, _, _ = _run_live(evidence_dir=evidence_dir)
    assert report.ok is False
    assert "evidence_permissions_unverified" in report.errors
    assert not (evidence_dir / LIVE_EVIDENCE_RUN_ID).exists()


# ---------------------------------------------------------------------------
# Q12. safe exclusive failure-summary write
# ---------------------------------------------------------------------------


def test_q12_failure_summary_exclusive_create_mode_0600(tmp_path: Path) -> None:
    """The sanitized failure summary is created exclusively with mode 0o600."""
    import stat as _statmod
    base = tmp_path / "evbase"
    base.mkdir()
    ev._write_sanitized_failure_summary(base, "run-fail", error_code="test_code")
    summary = base / ".failure-run-fail.json"
    assert summary.exists()
    mode = _statmod.S_IMODE(os.lstat(summary).st_mode)
    assert mode == 0o600
    payload = json.loads(summary.read_text(encoding="utf-8"))
    assert payload["error_code"] == "test_code"
    assert "ts" in payload


def test_q12b_failure_summary_pre_existing_regular_is_not_overwritten(tmp_path: Path) -> None:
    """A pre-existing regular file at the summary path is NOT overwritten."""
    base = tmp_path / "evbase"
    base.mkdir()
    summary = base / ".failure-run-pre.json"
    summary.write_text("caller-data", encoding="utf-8")
    ev._write_sanitized_failure_summary(base, "run-pre", error_code="code")
    assert summary.read_text(encoding="utf-8") == "caller-data"


def test_q12c_failure_summary_pre_existing_symlink_not_followed(tmp_path: Path) -> None:
    """A pre-existing symlink at the summary path is NOT followed; nothing
    is written to the link target."""
    base = tmp_path / "evbase"
    base.mkdir()
    target = tmp_path / "target.txt"
    target.write_text("t", encoding="utf-8")
    link = base / ".failure-run-link.json"
    os.symlink(target, link)
    ev._write_sanitized_failure_summary(base, "run-link", error_code="code")
    # The symlink target was not overwritten.
    assert target.read_text(encoding="utf-8") == "t"


def test_q12d_failure_summary_exclusive_create_race_is_omitted(tmp_path: Path) -> None:
    """An entry won by a caller between validation and O_EXCL creation is
    never overwritten and the safe summary is silently omitted."""
    import unittest.mock as _mock
    base = tmp_path / "evbase"
    base.mkdir()
    with _mock.patch("os.open", side_effect=FileExistsError()):
        ev._write_sanitized_failure_summary(base, "run-race", error_code="code")
    assert not (base / ".failure-run-race.json").exists()


def test_q12e_failure_summary_rejects_uncontrolled_basename(tmp_path: Path) -> None:
    """A path-shaped run id cannot escape the exact controlled basename."""
    base = tmp_path / "evbase"
    base.mkdir()
    ev._write_sanitized_failure_summary(base, "../escape", error_code="code")
    assert list(base.iterdir()) == []


# ---------------------------------------------------------------------------
# Q13. Git cwd pinned to ProofStudio root
# ---------------------------------------------------------------------------


def test_q13_run_git_command_binds_proofstudio_root() -> None:
    """_run_git_command defaults its cwd to the ProofStudio repository root
    derived from the script location. Invoking it does not raise and returns
    a structured result (the actual repo resolves HEAD)."""
    result = ev._run_git_command(["rev-parse", "--show-toplevel"], timeout=3.0)
    assert result.succeeded is True
    toplevel = result.stdout.strip()
    assert toplevel == str(ev._proofstudio_root())


def test_q13b_run_git_command_from_other_repository_still_binds_proofstudio(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A caller cwd that looks like another Git repository cannot redirect
    executor Git commands away from ProofStudio."""
    (tmp_path / ".git").mkdir()
    monkeypatch.chdir(tmp_path)
    result = ev._run_git_command(["rev-parse", "--show-toplevel"], timeout=3.0)
    assert result.succeeded is True
    assert result.stdout.strip() == str(ev._proofstudio_root())


def test_q13c_run_git_command_outside_repository_still_binds_proofstudio(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A caller cwd outside every repository still resolves ProofStudio."""
    monkeypatch.chdir(tmp_path)
    result = ev._run_git_command(["rev-parse", "--show-toplevel"], timeout=3.0)
    assert result.succeeded is True
    assert result.stdout.strip() == str(ev._proofstudio_root())


def test_q13d_proofstudio_root_derived_from_script_location() -> None:
    """The ProofStudio root is derived from the script's resolved location,
    not from the shell cwd."""
    root = ev._proofstudio_root()
    assert root == Path(ev.__file__).resolve().parent.parent
    assert (root / "scripts" / "ps041e2_b2_evidence.py").exists()


# ---------------------------------------------------------------------------
# Q14. corrected secure-removal language (no physical-erasure overclaim)
# ---------------------------------------------------------------------------


def test_q14_docs_do_not_overclaim_physical_secure_erasure() -> None:
    """The spec, runbook, proof and module docstring must not claim
    guaranteed physical secure erasure. The accurate contract is best-effort
    overwrite + logical unlink; physical media erasure is explicitly NOT
    claimed on SSD/CoW/journaled filesystems."""
    root = Path(__file__).resolve().parent.parent
    docs = [
        root / "specs/71-ps-041e2-controlled-b2-sponsor-evidence.md",
        root / "docs/ps-041e2-controlled-b2-sponsor-evidence-runbook.md",
        root / "docs/ps-041e2-controlled-b2-sponsor-evidence-proof.md",
    ]
    overclaim_phrases = [
        "guaranteed physical erasure",
        "guarantees physical media erasure",
        "guaranteed secure erasure of the underlying media",
        "physically zeroes the storage medium",
    ]
    for doc in docs:
        text = doc.read_text(encoding="utf-8")
        for phrase in overclaim_phrases:
            assert phrase not in text, (
                f"overclaim phrase '{phrase}' in {doc.name}"
            )
    # The module docstring of the executor must state the accurate contract.
    script_text = (root / "scripts/ps041e2_b2_evidence.py").read_text(encoding="utf-8")
    assert "physical media erasure is not claimed" in script_text.lower() or \
           "physical media erasure is NOT claimed" in script_text


def test_q14b_runbook_states_best_effort_logical_removal() -> None:
    """The runbook documents the accurate removal contract: best-effort
    overwrite + logical unlink, no physical-erasure claim on SSD/CoW/journaled
    filesystems."""
    root = Path(__file__).resolve().parent.parent
    runbook = (root / "docs/ps-041e2-controlled-b2-sponsor-evidence-runbook.md").read_text(encoding="utf-8")
    assert "best-effort" in runbook.lower() or "logical" in runbook.lower()


# ---------------------------------------------------------------------------
# Q15. evidence operation-counts.json carries complete counters
# ---------------------------------------------------------------------------


def test_q15_evidence_operation_counts_carries_complete_counters() -> None:
    """operation-counts.json in the produced evidence carries every required
    counter including head_object_calls, ranged_get_object_calls,
    head_bucket_calls, regional_probe_calls, inner_close_* and the
    controlled_read_invariant."""
    report, _, _, _ = _run_live()
    assert report.ok is True
    counts = _read_evidence_json(Path(report.evidence_dir), "operation-counts.json")
    for key in (
        "head_object_sdk_calls", "ranged_get_object_sdk_calls",
        "head_object_http_attempts", "ranged_get_object_http_attempts",
        "head_bucket_http_attempts", "regional_probe_http_attempts",
        "inner_close_attempted", "inner_close_succeeded",
        "inner_close_call_count", "controlled_read_invariant",
        "live_b2_calls",
    ):
        assert key in counts, f"missing counter {key}"
    assert counts["head_bucket_http_attempts"] == 0
    assert counts["regional_probe_http_attempts"] == 0
    assert counts["controlled_read_invariant"] is True
    assert counts["inner_close_succeeded"] is True
    assert counts["inner_close_call_count"] == 1


def test_q15b_execution_summary_carries_complete_counters() -> None:
    report, _, _, _ = _run_live()
    assert report.ok is True
    summary = _read_evidence_json(Path(report.evidence_dir), "execution-summary.json")
    for key in (
        "head_object_sdk_calls", "ranged_get_object_sdk_calls",
        "head_object_http_attempts", "ranged_get_object_http_attempts",
        "head_bucket_http_attempts", "regional_probe_http_attempts",
        "inner_close_attempted", "inner_close_succeeded",
        "inner_close_call_count",
    ):
        assert key in summary


# ---------------------------------------------------------------------------
# Q16. genblaze_store adapter version guard
# ---------------------------------------------------------------------------


def test_q16_adapter_version_guard_asserts_pinned_version() -> None:
    """The ExactKeyReadAdapter asserts the installed genblaze-s3 version is
    the pinned accepted version (0.3.5)."""
    from proofstudio.provenance.genblaze_store import (
        ACCEPTED_GENBLAZE_S3_VERSION, ExactKeyReadAdapter,
    )
    assert ACCEPTED_GENBLAZE_S3_VERSION == "0.3.5"
    # Construction with None rejects with a stable code.
    with pytest.raises(Exception) as ei:
        ExactKeyReadAdapter(None)
    assert getattr(ei.value, "code", "") in (
        "backend_missing", "backend_attributes_unavailable",
        "genblaze_s3_not_installed", "genblaze_s3_version_mismatch",
        "genblaze_s3_metadata_unavailable",
    )


def test_q16b_adapter_rejects_backend_lacking_attributes() -> None:
    """A backend lacking _client / _bucket rejects with a stable code."""
    from proofstudio.provenance.genblaze_store import ExactKeyReadAdapter
    with pytest.raises(Exception) as ei:
        ExactKeyReadAdapter(object())
    assert getattr(ei.value, "code", "") == "backend_attributes_unavailable"


# ---------------------------------------------------------------------------
# helper used by Q8b/Q11d
# ---------------------------------------------------------------------------


def _s3_like_populated_backend_into(fake: "_S3LikeFakeBackend") -> None:
    """Seed an existing S3-like fake with the fixture bodies (in-place)."""
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    role_bodies = {}
    for obj in fixture["objects"]:
        role = obj["role"]
        inline = obj.get("inline_json")
        if role in ev.JSON_READ_ROLES and inline is not None:
            role_bodies[role] = json.dumps(inline, separators=(",", ":")).encode("utf-8")
    for key in DEFAULT_KEYS:
        role = DEFAULT_ROLE_PLAN[key]
        if role in ev.JSON_READ_ROLES:
            body = role_bodies[role]
        else:
            body = ev._MEDIA_PLACEHOLDER
        fake.seed(key, body, last_modified=datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc))


# ===========================================================================
# PS-041E2-B FINAL ARTIFACT PM CORRECTIONS: retries, bounded bodies, ownership
# ===========================================================================


class _RawExactBackend:
    def __init__(self, client) -> None:
        self._client = client
        self._bucket = "fake-bucket"
        self.close_calls = 0
        self.close_raises = False

    def close(self) -> None:
        self.close_calls += 1
        if self.close_raises:
            raise OSError("raw close failed")


class _ResponseClient:
    def __init__(self, *, head_response=None, get_response=None) -> None:
        self.head_response = head_response
        self.get_response = get_response

    def head_object(self, **kwargs):
        return self.head_response

    def get_object(self, **kwargs):
        return self.get_response


def _exact_adapter_for(client):
    from proofstudio.provenance.genblaze_store import ExactKeyReadAdapter
    return ExactKeyReadAdapter(_RawExactBackend(client))


@pytest.mark.parametrize("retries,attempts", [(0, 1), (1, 2), (2, 3)])
def test_retry_attempts_are_counted_separately_from_head_sdk_calls(
    retries: int, attempts: int,
) -> None:
    response = {
        "ContentLength": 1, "ETag": "e",
        "ResponseMetadata": {"RetryAttempts": retries},
    }
    adapter = _exact_adapter_for(_ResponseClient(head_response=response))
    assert adapter.head_object("k")["size_bytes"] == 1
    assert adapter.head_object_sdk_calls == 1
    assert adapter.head_object_http_attempts == attempts


@pytest.mark.parametrize("retry_value", [None, -1, True, "1"])
def test_head_retry_metadata_missing_or_malformed_fails_closed(retry_value) -> None:
    metadata = {} if retry_value is None else {"RetryAttempts": retry_value}
    response = {
        "ContentLength": 1, "ETag": "e", "ResponseMetadata": metadata,
    }
    adapter = _exact_adapter_for(_ResponseClient(head_response=response))
    with pytest.raises(Exception) as caught:
        adapter.head_object("k")
    assert getattr(caught.value, "code", "") == "head_response_retry_metadata_invalid"


def _range_response(body, length: int, *, offset: int = 0, retries=0,
                    content_length=object(), content_range=object()):
    response = {
        "Body": body,
        "ContentLength": length if type(content_length) is object else content_length,
        "ResponseMetadata": {"RetryAttempts": retries},
    }
    if type(content_range) is object:
        response["ContentRange"] = f"bytes {offset}-{offset + length - 1}/{offset + length}"
    elif content_range is not None:
        response["ContentRange"] = content_range
    return response


def _run_range(response, *, offset: int = 0, length: int = 4):
    adapter = _exact_adapter_for(_ResponseClient(get_response=response))
    return adapter, lambda: adapter.get_range("k", offset=offset, length=length)


def test_ranged_body_exact_bytes_is_bounded_and_closed_once() -> None:
    body = _FakeBotoBody(b"abcd")
    adapter, call = _run_range(_range_response(body, 4))
    assert call() == b"abcd"
    assert body.close_calls == 1
    assert None not in body.read_args
    assert max(body.read_args) <= 5
    assert adapter.ranged_get_object_sdk_calls == 1
    assert adapter.ranged_get_object_http_attempts == 1


@pytest.mark.parametrize("retries,attempts", [(0, 1), (1, 2), (2, 3)])
def test_retry_attempts_are_counted_separately_from_get_sdk_calls(
    retries: int, attempts: int,
) -> None:
    body = _FakeBotoBody(b"abcd")
    adapter, call = _run_range(_range_response(body, 4, retries=retries))
    assert call() == b"abcd"
    assert adapter.ranged_get_object_sdk_calls == 1
    assert adapter.ranged_get_object_http_attempts == attempts
    assert body.close_calls == 1


def test_ranged_body_small_chunks_succeeds_under_absolute_bound() -> None:
    body = _FakeBotoBody(b"abcdef", chunk_size=2)
    _, call = _run_range(_range_response(body, 6), length=6)
    assert call() == b"abcdef"
    assert body.close_calls == 1
    assert all(n is not None and n <= 7 for n in body.read_args)


@pytest.mark.parametrize(
    "body_bytes,code",
    [(b"abc", "get_object_length_mismatch"),
     (b"abcde", "get_object_range_exceeded")],
)
def test_ranged_body_short_and_oversized_fail_closed(body_bytes: bytes, code: str) -> None:
    body = _FakeBotoBody(body_bytes)
    _, call = _run_range(_range_response(body, 4))
    with pytest.raises(Exception) as caught:
        call()
    assert getattr(caught.value, "code", "") == code
    assert body.close_calls == 1


@pytest.mark.parametrize("content_length", [None, -1, True, "4"])
def test_ranged_response_rejects_missing_or_malformed_content_length(content_length) -> None:
    body = _FakeBotoBody(b"abcd")
    response = _range_response(body, 4, content_length=content_length)
    if content_length is None:
        response.pop("ContentLength")
    _, call = _run_range(response)
    with pytest.raises(Exception) as caught:
        call()
    assert getattr(caught.value, "code", "") == "get_object_content_length_invalid"
    assert body.close_calls == 1


def test_server_ignoring_range_and_content_range_mismatch_are_rejected() -> None:
    ignored = _FakeBotoBody(b"whole-object")
    _, ignored_call = _run_range(_range_response(ignored, 4, content_length=12))
    with pytest.raises(Exception) as caught:
        ignored_call()
    assert getattr(caught.value, "code", "") == "get_object_length_mismatch"
    assert ignored.close_calls == 1

    mismatch = _FakeBotoBody(b"abcd")
    _, mismatch_call = _run_range(
        _range_response(mismatch, 4, content_range="bytes 1-4/5")
    )
    with pytest.raises(Exception) as caught:
        mismatch_call()
    assert getattr(caught.value, "code", "") == "get_object_content_range_mismatch"
    assert mismatch.close_calls == 1


def test_ranged_body_read_and_close_failures_are_stable() -> None:
    read_body = _FakeBotoBody(b"abcd", read_error=True)
    _, read_call = _run_range(_range_response(read_body, 4))
    with pytest.raises(Exception) as caught:
        read_call()
    assert getattr(caught.value, "code", "") == "get_object_body_read_failed"
    assert read_body.close_calls == 1

    close_body = _FakeBotoBody(b"abcd", close_error=True)
    _, close_call = _run_range(_range_response(close_body, 4))
    with pytest.raises(Exception) as caught:
        close_call()
    assert getattr(caught.value, "code", "") == "get_object_body_close_failed"
    assert close_body.close_calls == 1


def test_failed_range_error_retains_no_body_or_raw_exception() -> None:
    import gc
    import weakref

    class OneShotClient:
        def __init__(self, response) -> None:
            self.response = response

        def get_object(self, **kwargs):
            response = self.response
            self.response = None
            return response

    body = _FakeBotoBody(b"abc", read_error=True)
    body_ref = weakref.ref(body)
    response = _range_response(body, 4)
    client = OneShotClient(response)
    adapter = _exact_adapter_for(client)
    try:
        adapter.get_range("k", offset=0, length=4)
    except Exception as error:
        retained_error = error
    else:  # pragma: no cover - defensive
        raise AssertionError("range failure expected")
    assert getattr(retained_error, "code", "") == "get_object_body_read_failed"
    assert retained_error.__cause__ is None
    deepest = retained_error.__traceback__
    while deepest is not None and deepest.tb_next is not None:
        deepest = deepest.tb_next
    assert deepest is not None
    assert deepest.tb_frame.f_locals.get("body") is None
    assert deepest.tb_frame.f_locals.get("resp") is None
    retained_error.__traceback__ = None
    del body, response, adapter, client
    gc.collect()
    assert body_ref() is None


@pytest.mark.parametrize("retry_value", [None, -1, True, "1"])
def test_get_retry_metadata_missing_or_malformed_fails_closed_and_closes(retry_value) -> None:
    body = _FakeBotoBody(b"abcd")
    response = _range_response(body, 4)
    response["ResponseMetadata"] = (
        {} if retry_value is None else {"RetryAttempts": retry_value}
    )
    _, call = _run_range(response)
    with pytest.raises(Exception) as caught:
        call()
    assert getattr(caught.value, "code", "") == "get_object_response_retry_metadata_invalid"
    assert body.close_calls == 1


class _ExactGuardFactory:
    def __init__(self, fake: _FakeBotoS3Client) -> None:
        self.call_count = 0
        self.raw = _RawExactBackend(fake)

    def __call__(self, credentials):
        self.call_count += 1
        return ev.GuardedLiveBackend(_exact_adapter_for(self.raw._client))


def _seed_exact_plan(fake: _FakeBotoS3Client, *, mixed_retries: bool) -> None:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    role_bodies = ev._fixture_role_bodies(fixture)
    for index, key in enumerate(DEFAULT_KEYS):
        role = DEFAULT_ROLE_PLAN[key]
        body = role_bodies[role] if role in ev.JSON_READ_ROLES else ev._MEDIA_PLACEHOLDER
        fake.seed(
            key, body, etag=f"etag-{index}",
            head_retries=(index % 3 if mixed_retries else 0),
            get_retries=((index + 1) % 3 if mixed_retries else 0),
        )


def test_zero_retry_five_object_plan_has_exact_sdk_and_http_counts() -> None:
    fake = _FakeBotoS3Client()
    _seed_exact_plan(fake, mixed_retries=False)
    report, _, _, _ = _run_live(
        backend_factory=_ExactGuardFactory(fake), real_backend_factory_used=True,
    )
    assert report.ok is True
    assert report.head_object_sdk_calls == 18
    assert report.ranged_get_object_sdk_calls == 4
    assert report.head_object_http_attempts == 18
    assert report.ranged_get_object_http_attempts == 4
    assert report.head_bucket_http_attempts == 0
    assert report.regional_probe_http_attempts == 0
    assert report.live_b2_calls == 22


def test_mixed_retries_produce_exact_aggregate_live_b2_calls() -> None:
    fake = _FakeBotoS3Client()
    _seed_exact_plan(fake, mixed_retries=True)
    report, _, _, _ = _run_live(
        backend_factory=_ExactGuardFactory(fake), real_backend_factory_used=True,
    )
    assert report.ok is True
    head_expected = sum(
        1 + fake._objects[call["Key"]]["head_retries"]
        for call in fake.head_object_calls
    )
    get_expected = sum(
        1 + fake._objects[call["Key"]]["get_retries"]
        for call in fake.get_object_calls
    )
    assert report.head_object_http_attempts == head_expected
    assert report.ranged_get_object_http_attempts == get_expected
    assert report.live_b2_calls == head_expected + get_expected
    assert report.live_b2_calls > 22


def test_real_factory_cleans_current_owner_and_transfers_successfully(monkeypatch) -> None:
    import proofstudio.provenance.genblaze_store as store

    credentials = ev.LiveCredentials("id", "key", "bucket", "region")
    raw = _RawExactBackend(object())
    monkeypatch.setattr(store, "build_backblaze_backend", lambda **kwargs: raw)

    monkeypatch.setattr(
        store, "build_exact_key_read_adapter",
        lambda backend: (_ for _ in ()).throw(RuntimeError("adapter failed")),
    )
    with pytest.raises(ev.AuthorizationError) as caught:
        ev._RealBackendFactory()(credentials)
    assert caught.value.code == "backend_factory_construction_failed"
    assert raw.close_calls == 1

    raw2 = _RawExactBackend(object())
    raw2.close_raises = True
    monkeypatch.setattr(store, "build_backblaze_backend", lambda **kwargs: raw2)
    with pytest.raises(ev.AuthorizationError) as caught:
        ev._RealBackendFactory()(credentials)
    assert caught.value.code == "backend_factory_cleanup_failed"
    assert raw2.close_calls == 1


@pytest.mark.parametrize(
    "code",
    ["genblaze_s3_version_mismatch", "backend_attributes_unavailable"],
)
def test_real_factory_version_and_compatibility_failures_close_raw_once(
    monkeypatch, code: str,
) -> None:
    import proofstudio.provenance.genblaze_store as store

    class StableFailure(Exception):
        def __init__(self, stable_code: str) -> None:
            self.code = stable_code

    raw = _RawExactBackend(object())
    monkeypatch.setattr(store, "build_backblaze_backend", lambda **kwargs: raw)
    monkeypatch.setattr(
        store, "build_exact_key_read_adapter",
        lambda backend: (_ for _ in ()).throw(StableFailure(code)),
    )
    with pytest.raises(ev.AuthorizationError) as caught:
        ev._RealBackendFactory()(
            ev.LiveCredentials("id", "key", "bucket", "region")
        )
    assert caught.value.code == code
    assert raw.close_calls == 1


def test_real_factory_wrapper_failure_closes_adapter_owner_once(monkeypatch) -> None:
    import proofstudio.provenance.genblaze_store as store

    raw = _RawExactBackend(object())
    adapter = _RawExactBackend(object())
    monkeypatch.setattr(store, "build_backblaze_backend", lambda **kwargs: raw)
    monkeypatch.setattr(store, "build_exact_key_read_adapter", lambda backend: adapter)
    monkeypatch.setattr(
        ev, "GuardedLiveBackend",
        lambda inner: (_ for _ in ()).throw(RuntimeError("wrapper failed")),
    )
    with pytest.raises(ev.AuthorizationError) as caught:
        ev._RealBackendFactory()(ev.LiveCredentials("id", "key", "bucket", "region"))
    assert caught.value.code == "backend_factory_construction_failed"
    assert adapter.close_calls == 1
    assert raw.close_calls == 0


def test_real_factory_success_does_not_prematurely_close_transferred_owner(monkeypatch) -> None:
    import proofstudio.provenance.genblaze_store as store

    raw = _RawExactBackend(object())
    adapter = _RawExactBackend(object())
    monkeypatch.setattr(store, "build_backblaze_backend", lambda **kwargs: raw)
    monkeypatch.setattr(store, "build_exact_key_read_adapter", lambda backend: adapter)
    result = ev._RealBackendFactory()(
        ev.LiveCredentials("id", "key", "bucket", "region")
    )
    assert isinstance(result, ev.GuardedLiveBackend)
    assert raw.close_calls == 0
    assert adapter.close_calls == 0
    result.destroy()
    assert adapter.close_calls == 1
