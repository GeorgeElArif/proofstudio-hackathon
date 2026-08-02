#!/usr/bin/env python3
"""PS-041E2-B Phase-1 — Controlled B2 Sponsor Evidence executor.

This module is the live executor for one controlled, read-only Backblaze B2
evidence read. It implements three modes:

- ``--check-readiness``: print the readiness summary (no authorization needed).
- ``--validate-authorization <path>``: defensively validate one readiness
  authorization document against the full contract.
- ``--dry-run <authorization-path>``: validate + run one bounded fake-storage
  evidence flow using an injected ``FakeB2Backend`` and the accepted reader.
- ``--execute <authorization-path>``: run the controlled live B2 evidence
  flow. The real CLI path is wired to the accepted
  ``S3StorageBackend.for_backblaze`` backend factory and resolves real Git
  state, real server-side B2 configuration, and a credential provider that
  reads only the established server-side environment variables. Phase-1
  implements every one of the 22 live gates and the full atomic operation
  order. The CLI refuses to run unless the local HEAD equals the remote
  ``refs/heads/accepted/proofstudio``; from any unaccepted feature branch it
  fails closed before any client construction.

Boundaries (enforced everywhere in this module):

- no live B2 access in any test or smoke (no real bucket, no real prefix list,
  no provider call); the only path that may touch live B2 is the real CLI
  ``--execute`` mode after every gate has passed;
- no B2 credential *value* is read before every authorization and Git binding
  check passes — pre-gate code may inspect environment-variable *key
  membership* only (never the values of ``B2_KEY_ID`` / ``B2_APP_KEY``);
  the injectable :class:`EnvAccessBoundary` enforces this invariant and is
  exercised by the focused tests. No B2 client is constructed before all 22
  gates pass;
- no new B2 client in any test path (tests use the in-process
  ``FakeB2Backend`` and a fake S3-like adapter that exposes only
  ``head`` / ``get_range`` / ``get``);
- no signed URL generation;
- no write/delete capability (every write/delete/signed-URL/provider
  capability is fixed false);
- stdlib-first; no new third-party dependency.

Phase-1 implementation guarantees (corrected in PS-041E2-B Phase-1):

- explicit server configuration is required: the configured alias, configured
  import root, bucket identity and region must all be present and nonempty
  before credential retrieval and backend construction; no implicit
  ``configured-import`` default;
- the authorized prefix must byte-for-byte equal the independently configured
  import root (no silent normalization on either side);
- accepted-commit binding resolves local HEAD, local
  ``origin/accepted/proofstudio`` and the current remote
  ``refs/heads/accepted/proofstudio``; all three must agree before any
  credential is read;
- the live evidence output root is confined to exactly
  ``/tmp/proofstudio-ps041e2-live-evidence`` for real execution; a custom
  evidence directory is available only through direct dependency injection
  in tests;
- final output is genuinely atomic: the final run directory does not exist
  until every success artifact is complete and the real security scan has
  passed; the atomic rename is the last operation;
- the classified security scan detects real credential values, raw bucket
  identity, raw endpoints, Authorization/Bearer headers, signed/presigned URL
  query parameters, credential assignments, credential-bearing database URLs,
  raw object-byte sentinels and unexpected http(s) URLs — it never serializes
  the sensitive comparison values and prevents atomic finalization on any
  real leak;
- cleanup is guaranteed on every post-gate path: after the credential
  provider has been called, every outcome destroys the backend, releases
  inner backend/client references and credential references, and securely
  removes any incomplete partial output directory; no payload-bearing
  quarantine is ever retained (an optional sanitized failure summary may
  contain only a stable error code);
- the accepted ``GuardedLiveBackend`` exposes exact counters for every
  underlying remote operation; the live read path uses the accepted
  ``ExactKeyReadAdapter`` (``proofstudio.provenance.genblaze_store``) which
  issues ONLY low-level ``HeadObject`` and ranged ``GetObject`` calls
  through the pinned boto3 client and never runs the lazy bucket-region
  preflight — so there is zero ``head_bucket`` and zero regional probing
  on the controlled read path; there is no hidden HEAD inside
  ``read_bytes``, no full-object GET fallback, and ``get_range`` is
  mandatory for the accepted live adapter; the returned byte length must
  equal the declared approved size;
- SDK invocations and actual HTTP attempts are reported separately. Every
  successful response contributes ``1 + ResponseMetadata.RetryAttempts`` to
  its operation's HTTP-attempt counter. ``live_b2_calls`` is zero for fake
  execution and for real execution equals ``head_object_http_attempts +
  ranged_get_object_http_attempts + head_bucket_http_attempts +
  regional_probe_http_attempts``; the last two remain zero on the accepted
  no-preflight path;
- the live run uses the accepted PS-041D ``ProofStudioService`` to import the
  constructed candidate, capture the real created/idempotent result, retrieve
  the stored private lineage bundle through the accepted private read
  boundary, and retrieve the portable Passport from the stored imported
  record. ``import_created`` is set from the actual import result.
"""

from __future__ import annotations

import argparse
import copy
import datetime as _dt
import hashlib
import hmac
import json
import os
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, Sequence

from proofstudio.api.b2_import_reader import B2ImportReaderConfig, BoundedB2ImportReader
from proofstudio.api.genblaze_external_adapter import ImportValidationError, build_candidate, passport_for
from proofstudio.api.imported_bundle import (
    MAX_JSON_OBJECT_BYTES, B2ObjectReference, ImportBundleRequest, PortableLineagePassport,
)

SCHEMA = "proofstudio.ps041e2.b2_authorization.v1"
PURPOSE = "PS-041E2 controlled sponsor evidence"
PASSPORT_SCHEMA = "proofstudio.portable_lineage_passport.v1"

# ---------------------------------------------------------------------------
# Object role plan (explicit bounded purpose for every allowlisted object).
# ---------------------------------------------------------------------------

ROLE_STAGE_A_STORYBOARD = "stage_a_storyboard"
ROLE_STAGE_B0_MANIFEST = "stage_b0_manifest"
ROLE_STAGE_B1_MANIFEST = "stage_b1_manifest"
ROLE_STAGE_B2_MANIFEST = "stage_b2_manifest"
ROLE_STAGE_C_COMPOSITION = "stage_c_composition"
ROLE_FINAL_DELIVERY = "final_delivery"
ROLE_EMBEDDED_MANIFEST = "embedded_manifest"

KNOWN_ROLES: frozenset[str] = frozenset({
    ROLE_STAGE_A_STORYBOARD,
    ROLE_STAGE_B0_MANIFEST,
    ROLE_STAGE_B1_MANIFEST,
    ROLE_STAGE_B2_MANIFEST,
    ROLE_STAGE_C_COMPOSITION,
    ROLE_FINAL_DELIVERY,
    ROLE_EMBEDDED_MANIFEST,
})

# Roles that must each appear exactly once in every nonempty readiness plan.
REQUIRED_UNIQUE_ROLES: tuple[str, ...] = (
    ROLE_STAGE_A_STORYBOARD,
    ROLE_STAGE_B0_MANIFEST,
    ROLE_STAGE_B1_MANIFEST,
    ROLE_STAGE_B2_MANIFEST,
    ROLE_FINAL_DELIVERY,
)

# Roles whose content build_candidate reads through b2_json_reader. These each
# consume one validated JSON snapshot.
JSON_READ_ROLES: frozenset[str] = frozenset({
    ROLE_STAGE_A_STORYBOARD,
    ROLE_STAGE_B0_MANIFEST,
    ROLE_STAGE_B1_MANIFEST,
    ROLE_STAGE_B2_MANIFEST,
    ROLE_STAGE_C_COMPOSITION,
})

# Roles whose bytes are read only through the bounded media asset reader (never
# consumed by build_candidate as JSON).
MEDIA_BYTE_ROLES: frozenset[str] = frozenset({
    ROLE_FINAL_DELIVERY,
})

# Reserved roles are known (so ``object_role_by_key`` accepts them as
# structurally valid role strings) but are NOT consumable in PS-041E2-A because
# the accepted fixture/contract carries no bounded JSON descriptor for them.
# Validation rejects any plan that uses a reserved role with
# ``object_role_reserved_unsupported`` so that a structurally valid
# authorization can never reach the fake backend only to fail with
# ``fake_backend_unknown_role``.
RESERVED_ROLES: frozenset[str] = frozenset({
    ROLE_EMBEDDED_MANIFEST,
})

# Supported roles are exactly the union of JSON-read and media-byte roles.
# Every accepted (non-reserved) role has exactly one explicit bounded
# consumption mode. This invariant is asserted at import time so a future
# edit cannot silently introduce an unconsumable accepted role.
SUPPORTED_ROLES: frozenset[str] = JSON_READ_ROLES | MEDIA_BYTE_ROLES
assert KNOWN_ROLES == SUPPORTED_ROLES | RESERVED_ROLES, (
    "every known role must be supported (JSON-read or media-byte) or reserved"
)
assert not (SUPPORTED_ROLES & RESERVED_ROLES), (
    "a role cannot be both supported and reserved"
)

# ---------------------------------------------------------------------------
# Accepted hard upper bounds (immutable). The authorization may narrow these
# limits but must never enlarge them.
# ---------------------------------------------------------------------------

ACCEPTED_MAX_OBJECT_COUNT = 256
ACCEPTED_MAX_JSON_OBJECT_BYTES = 1_048_576
ACCEPTED_MAX_MEDIA_OBJECT_BYTES = 134_217_728
ACCEPTED_MAX_AGGREGATE_BYTES = 536_870_912

# PS-041E2-B Phase-1 evidence-text size caps (fail-closed scanner).
# Each evidence file must be a regular non-symlink UTF-8 text file whose byte
# size is within PER_EVIDENCE_FILE_MAX_BYTES, and the total byte size of all
# evidence files in one directory must be within AGGREGATE_EVIDENCE_MAX_BYTES.
# These caps are deliberately small: the complete 20-file evidence set is
# well under 1 MiB total.
PER_EVIDENCE_FILE_MAX_BYTES = 1_048_576  # 1 MiB per evidence file
AGGREGATE_EVIDENCE_MAX_BYTES = 8_388_608  # 8 MiB total across all evidence files

# Authorization document structure bounds (defensive parse ceiling).
AUTH_DOC_MAX_BYTES = 65_536
AUTH_DOC_MAX_DEPTH = 32
AUTH_DOC_MAX_ITEMS = 4_096
AUTH_DOC_MAX_STRING = 8_192
AUTH_DOC_MAX_KEY_LEN = 256

# Authorization field bounds.
ALIAS_MAX_BYTES = 64
PREFIX_MAX_BYTES = 1_024
OPERATOR_MAX_BYTES = 256

# Authorization time window.
MAX_AUTH_WINDOW_SECONDS = 24 * 60 * 60
ALLOWED_FUTURE_AUTHORIZED_AT_SECONDS = 60

# Default injected fake server identity (dry-run only). These are deliberately
# separate constants so the dry-run never derives server identity from the
# authorization document.
DEFAULT_FAKE_SERVER_ALIAS = "configured-import"
DEFAULT_FAKE_SERVER_BUCKET_IDENTITY = "proofstudio-ps041e2-fake-fixture-bucket"

REQUIRED_FIELDS: tuple[str, ...] = (
    "schema", "authorized", "authorized_by", "authorized_at", "expires_at",
    "configured_alias", "allowed_bucket_name_hash", "allowed_prefix", "allowed_keys",
    "object_role_by_key",
    "max_object_count", "max_object_bytes", "max_total_bytes",
    "allow_metadata_reads", "allow_json_object_reads", "allow_media_byte_reads",
    "allow_sha256_verification", "allow_write", "allow_delete",
    "allow_signed_urls", "allow_provider_calls", "expected_sha256_by_key",
    "purpose",
)

DENIED_CAPABILITY_FIELDS: tuple[str, ...] = (
    "allow_write", "allow_delete", "allow_signed_urls", "allow_provider_calls",
)

DEFAULT_EVIDENCE_DIR = "/tmp/proofstudio-ps041e2-live-evidence"

FORBIDDEN_AUTH_BASENAMES: frozenset[str] = frozenset({
    ".env", ".env.local", ".env.save", ".env.production",
    ".env.development", ".env.test", ".env.staging", ".env.example",
    "credentials", "credentials.json",
})

_KEY_UNSAFE = re.compile(r"[\x00-\x1f\x7f]")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_MEDIA_PLACEHOLDER = b"\x00PS041E2-MEDIA-PLACEHOLDER-NOT-REAL-DATA"


class AuthorizationError(ValueError):
    """Raised when an authorization document violates the readiness contract.

    The message carries only a stable error code; it never echoes credential
    material, environment values, raw paths, raw bucket names, or raw upstream
    content.
    """

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


# ---------------------------------------------------------------------------
# Defensive load (path safety + bounded structural parse)
# ---------------------------------------------------------------------------

def load_authorization(path: Path) -> dict[str, Any]:
    """Defensively load one authorization document from ``path``.

    Fails closed on forbidden basenames, missing ``.json`` suffix, symlinks,
    non-regular files, missing file, excessive size, invalid UTF-8, malformed
    JSON, duplicate keys, non-object root, or structural-boundary violations.
    Never reads a credential-bearing file. Never prints the rejected path.
    """
    basename = path.name
    if basename in FORBIDDEN_AUTH_BASENAMES:
        raise AuthorizationError("authorization_path_forbidden_basename")
    if not basename.endswith(".json"):
        raise AuthorizationError("authorization_path_not_json")
    try:
        is_symlink = path.is_symlink()
    except OSError:
        raise AuthorizationError("authorization_path_unreadable")
    if is_symlink:
        raise AuthorizationError("authorization_path_symlink")
    try:
        is_file = path.is_file()
    except OSError:
        raise AuthorizationError("authorization_path_unreadable")
    if not is_file:
        raise AuthorizationError("authorization_absent")
    try:
        size = path.stat().st_size
    except OSError:
        raise AuthorizationError("authorization_path_unreadable")
    if size > AUTH_DOC_MAX_BYTES:
        raise AuthorizationError("authorization_too_large")
    try:
        raw = path.read_bytes()
    except OSError:
        raise AuthorizationError("authorization_path_unreadable")
    if len(raw) > AUTH_DOC_MAX_BYTES:
        raise AuthorizationError("authorization_too_large")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        raise AuthorizationError("authorization_invalid_utf8")
    try:
        value = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    except AuthorizationError:
        raise
    except (json.JSONDecodeError, ValueError, RecursionError):
        raise AuthorizationError("authorization_malformed_json")
    except Exception:
        raise AuthorizationError("authorization_malformed_json")
    if not isinstance(value, dict):
        raise AuthorizationError("authorization_not_object")
    _bounded_structure_check(value)
    return value


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise AuthorizationError("authorization_duplicate_key")
        result[key] = value
    return result


def _bounded_structure_check(value: Any) -> None:
    """Iteratively validate authorization structure bounds.

    No recursion is used so a deeply nested adversarial document cannot escape
    as ``RecursionError``. Validates: dict root, bounded depth, bounded total
    list/dict items, bounded string and key length, NFC strings, and absence of
    control characters. Dict keys must be strings.
    """
    if not isinstance(value, dict):
        raise AuthorizationError("authorization_not_object")
    items = 0
    stack: list[tuple[Any, int]] = [(value, 1)]
    while stack:
        node, depth = stack.pop()
        if depth > AUTH_DOC_MAX_DEPTH:
            raise AuthorizationError("authorization_depth_exceeded")
        if isinstance(node, dict):
            items += len(node)
            if items > AUTH_DOC_MAX_ITEMS:
                raise AuthorizationError("authorization_item_count_exceeded")
            for k, v in node.items():
                if not isinstance(k, str):
                    raise AuthorizationError("authorization_key_not_string")
                if len(k) > AUTH_DOC_MAX_KEY_LEN:
                    raise AuthorizationError("authorization_key_too_long")
                _check_structure_string(k)
                stack.append((v, depth + 1))
        elif isinstance(node, list):
            items += len(node)
            if items > AUTH_DOC_MAX_ITEMS:
                raise AuthorizationError("authorization_item_count_exceeded")
            for item in node:
                stack.append((item, depth + 1))
        elif isinstance(node, bool) or node is None:
            pass
        elif isinstance(node, int):
            if isinstance(node, bool):
                raise AuthorizationError("authorization_structure_unsafe")
        elif isinstance(node, float):
            raise AuthorizationError("authorization_structure_unsafe")
        elif isinstance(node, str):
            _check_structure_string(node)
        else:
            raise AuthorizationError("authorization_structure_unsafe")


def _check_structure_string(s: str) -> None:
    if len(s) > AUTH_DOC_MAX_STRING:
        raise AuthorizationError("authorization_string_too_long")
    if unicodedata.normalize("NFC", s) != s:
        raise AuthorizationError("authorization_string_not_nfc")
    if _KEY_UNSAFE.search(s):
        raise AuthorizationError("authorization_control_character")


# ---------------------------------------------------------------------------
# Key and canonical prefix safety (mirrors accepted B2ObjectReference validators)
# ---------------------------------------------------------------------------

def _is_safe_key(key: str) -> bool:
    if not isinstance(key, str) or not key:
        return False
    lowered = key.lower()
    if (
        key.startswith("/") or "\\" in key or "?" in key or "#" in key
        or "://" in lowered or any(part == ".." for part in key.split("/"))
    ):
        return False
    if key != unicodedata.normalize("NFC", key):
        return False
    if _KEY_UNSAFE.search(key):
        return False
    return True


def _validate_canonical_prefix(prefix: Any) -> str:
    """Validate ``prefix`` is canonical and return it unchanged.

    The authorized prefix used by the reader must byte-for-byte equal the
    authorization value. This function never strips, rewrites, or normalizes
    the value. It only rejects non-canonical values.
    """
    if not isinstance(prefix, str):
        raise AuthorizationError("prefix_not_string")
    if prefix == "" or prefix == "/":
        raise AuthorizationError("prefix_empty")
    if prefix.strip() != prefix:
        raise AuthorizationError("prefix_surrounding_whitespace")
    if prefix.startswith("/"):
        raise AuthorizationError("prefix_leading_slash")
    if prefix.endswith("/"):
        raise AuthorizationError("prefix_trailing_slash")
    parts = prefix.split("/")
    if any(part == "" for part in parts):
        raise AuthorizationError("prefix_repeated_empty_component")
    if any(part == ".." for part in parts):
        raise AuthorizationError("prefix_unsafe")
    lowered = prefix.lower()
    if "\\" in prefix or "?" in prefix or "#" in prefix or "://" in lowered:
        raise AuthorizationError("prefix_unsafe")
    if len(prefix.encode("utf-8", errors="strict")) > PREFIX_MAX_BYTES:
        raise AuthorizationError("prefix_too_long")
    if unicodedata.normalize("NFC", prefix) != prefix:
        raise AuthorizationError("prefix_not_nfc")
    if _KEY_UNSAFE.search(prefix):
        raise AuthorizationError("prefix_control_character")
    return prefix


def _validate_canonical_alias(alias: Any) -> str:
    """Validate ``configured_alias`` is canonical and return it unchanged."""
    if not isinstance(alias, str):
        raise AuthorizationError("alias_missing")
    if alias == "":
        raise AuthorizationError("alias_missing")
    if alias.strip() == "":
        raise AuthorizationError("alias_whitespace_only")
    if alias.strip() != alias:
        raise AuthorizationError("alias_leading_or_trailing_whitespace")
    lowered = alias.lower()
    if "/" in alias or "\\" in alias or "?" in alias or "#" in alias or "://" in lowered:
        raise AuthorizationError("alias_unsafe")
    if any(part == ".." for part in alias.split("/")):
        raise AuthorizationError("alias_unsafe")
    if len(alias.encode("utf-8", errors="strict")) > ALIAS_MAX_BYTES:
        raise AuthorizationError("alias_too_long")
    if unicodedata.normalize("NFC", alias) != alias:
        raise AuthorizationError("alias_not_nfc")
    if _KEY_UNSAFE.search(alias):
        raise AuthorizationError("alias_unsafe")
    return alias


def _validate_canonical_operator(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or value == "":
        raise AuthorizationError(f"{field_name}_missing")
    if value.strip() == "":
        raise AuthorizationError(f"{field_name}_whitespace_only")
    if value.strip() != value:
        raise AuthorizationError(f"{field_name}_leading_or_trailing_whitespace")
    lowered = value.lower()
    if "\\" in value or "://" in lowered:
        raise AuthorizationError(f"{field_name}_unsafe")
    if len(value.encode("utf-8", errors="strict")) > OPERATOR_MAX_BYTES:
        raise AuthorizationError(f"{field_name}_too_long")
    if unicodedata.normalize("NFC", value) != value:
        raise AuthorizationError(f"{field_name}_not_nfc")
    if _KEY_UNSAFE.search(value):
        raise AuthorizationError(f"{field_name}_unsafe")
    return value


def _key_inside_prefix(key: str, canonical_prefix: str) -> bool:
    return key.startswith(canonical_prefix + "/")


# ---------------------------------------------------------------------------
# Authorization timestamp validation (timezone-aware, UTC, short window)
# ---------------------------------------------------------------------------

def _require_utc_iso(value: Any, field_name: str) -> _dt.datetime:
    if not isinstance(value, str) or not value:
        raise AuthorizationError(f"{field_name}_missing")
    if value.endswith("Z"):
        normalized = value[:-1] + "+00:00"
    else:
        normalized = value
    try:
        parsed = _dt.datetime.fromisoformat(normalized)
    except (ValueError, TypeError):
        raise AuthorizationError(f"{field_name}_invalid")
    if parsed.tzinfo is None:
        raise AuthorizationError(f"{field_name}_not_timezone_aware")
    if parsed.utcoffset() != _dt.timedelta(0):
        raise AuthorizationError(f"{field_name}_not_utc")
    return parsed


def _utc_now() -> _dt.datetime:
    return _dt.datetime.now(_dt.timezone.utc)


# ---------------------------------------------------------------------------
# Object role plan validation (explicit bounded purpose per key)
# ---------------------------------------------------------------------------

def _validate_object_role_plan(
    object_role_by_key: Any,
    *,
    allowed_keys: list[str],
    allow_media_byte_reads: bool,
    expected_sha256_by_key: dict[str, Any],
) -> dict[str, str]:
    """Validate the explicit object-role plan and return it as a checked dict.

    Contract:

    - ``object_role_by_key`` must be an object mapping exact allowlisted key to
      a known role string;
    - its key set must exactly equal ``allowed_keys`` (no missing, no extra);
    - every role must be a known role;
    - each role appears at most once (no duplicate semantic roles);
    - the five required readiness roles each appear exactly once when the
      allowlist is nonempty;
    - an expected digest for a media-byte role requires
      ``allow_media_byte_reads=true``.
    """
    if not isinstance(object_role_by_key, dict):
        raise AuthorizationError("object_role_by_key_not_object")
    plan_keys = set(object_role_by_key.keys())
    allowed_set = set(allowed_keys)
    if plan_keys != allowed_set:
        missing = allowed_set - plan_keys
        extra = plan_keys - allowed_set
        if missing:
            raise AuthorizationError("object_role_missing_key")
        raise AuthorizationError("object_role_extra_key")

    role_to_key: dict[str, str] = {}
    for key, role in object_role_by_key.items():
        if not isinstance(role, str):
            raise AuthorizationError("object_role_value_not_string")
        if role not in KNOWN_ROLES:
            raise AuthorizationError("object_role_unknown_role")
        if role in RESERVED_ROLES:
            # ``embedded_manifest`` is known but reserved: the accepted
            # fixture/contract carries no bounded JSON descriptor for it, so
            # PS-041E2-A cannot consume it. Reject at validation time so the
            # fake backend never has to surface ``fake_backend_unknown_role``
            # for an otherwise structurally valid authorization.
            raise AuthorizationError("object_role_reserved_unsupported")
        if role in role_to_key:
            raise AuthorizationError("object_role_duplicate_role")
        role_to_key[role] = key

    # Every known role may appear at most once (enforced above). When the
    # allowlist is nonempty the five required readiness roles must each appear
    # exactly once.
    if allowed_keys:
        for required in REQUIRED_UNIQUE_ROLES:
            count = sum(1 for r in object_role_by_key.values() if r == required)
            if count != 1:
                raise AuthorizationError("object_role_required_role_missing")

    # An expected digest for a media-byte role requires media byte reads.
    if not allow_media_byte_reads:
        for key, role in object_role_by_key.items():
            if role in MEDIA_BYTE_ROLES and key in expected_sha256_by_key:
                raise AuthorizationError("expected_media_hash_requires_media_reads")

    return dict(object_role_by_key)


def resolve_role_to_key(object_role_by_key: dict[str, str]) -> dict[str, str]:
    """Invert the explicit role plan to ``{role: key}``.

    Resolution uses the explicit map only. It never relies on allowlist order
    and never uses a loose first ``endswith()`` match.
    """
    role_to_key: dict[str, str] = {}
    for key, role in object_role_by_key.items():
        if role in role_to_key:
            raise AuthorizationError("object_role_duplicate_role")
        role_to_key[role] = key
    return role_to_key


# ---------------------------------------------------------------------------
# Full authorization validation
# ---------------------------------------------------------------------------

@dataclass
class AuthorizationReport:
    valid: bool
    code: str = ""
    configured_alias: str = ""
    canonical_prefix: str = ""
    authorized_object_count: int = 0
    authorized_total_bytes: int = 0
    capabilities: dict[str, bool] = field(default_factory=dict)
    object_role_by_key: dict[str, str] = field(default_factory=dict)


def validate_authorization(value: dict[str, Any], *, execute_mode: bool = False) -> AuthorizationReport:
    """Validate one authorization dict against the full readiness contract.

    ``execute_mode`` adds the stricter live-execution requirements
    (``authorized=true``, non-expired, all denied capabilities false,
    metadata and JSON reads allowed). The template-default deny state is
    sufficient for ``--validate-authorization`` but not for ``--execute``.
    """
    # Defensive structural bound first (also catches non-dict input safely).
    _bounded_structure_check(value)

    unknown = sorted(set(value) - set(REQUIRED_FIELDS))
    if unknown:
        raise AuthorizationError("unknown_authorization_field")
    missing = sorted(set(REQUIRED_FIELDS) - set(value))
    if missing:
        raise AuthorizationError("missing_authorization_field")

    if value["schema"] != SCHEMA:
        raise AuthorizationError("unsupported_authorization_schema")
    if value["purpose"] != PURPOSE:
        raise AuthorizationError("unsupported_purpose")

    authorized = value["authorized"]
    if not isinstance(authorized, bool):
        raise AuthorizationError("authorized_not_boolean")

    configured_alias = _validate_canonical_alias(value["configured_alias"])

    bucket_hash = value["allowed_bucket_name_hash"]
    if not isinstance(bucket_hash, str) or not _HEX64.match(bucket_hash):
        raise AuthorizationError("bucket_hash_invalid")

    canonical_prefix = _validate_canonical_prefix(value["allowed_prefix"])

    allowed_keys = value["allowed_keys"]
    if not isinstance(allowed_keys, list):
        raise AuthorizationError("allowlist_not_list")
    if len(allowed_keys) == 0:
        raise AuthorizationError("allowlist_empty")
    # Every item must be a string BEFORE duplicate detection.
    seen: set[str] = set()
    for key in allowed_keys:
        if not isinstance(key, str) or not _is_safe_key(key):
            raise AuthorizationError("allowlist_key_unsafe")
        if key in seen:
            raise AuthorizationError("allowlist_duplicate_key")
        seen.add(key)
        if not _key_inside_prefix(key, canonical_prefix):
            raise AuthorizationError("allowlist_key_outside_prefix")

    for cap in ("allow_metadata_reads", "allow_json_object_reads",
                "allow_media_byte_reads", "allow_sha256_verification", *DENIED_CAPABILITY_FIELDS):
        cap_value = value[cap]
        if not isinstance(cap_value, bool):
            raise AuthorizationError(f"capability_not_boolean:{cap}")

    caps = {cap: bool(value[cap]) for cap in (
        "allow_metadata_reads", "allow_json_object_reads",
        "allow_media_byte_reads", "allow_sha256_verification", *DENIED_CAPABILITY_FIELDS,
    )}

    for cap in DENIED_CAPABILITY_FIELDS:
        if value[cap]:
            raise AuthorizationError(f"denied_capability_enabled:{cap}")

    # Hard upper bounds. The authorization may narrow but never enlarge them.
    max_object_count = value["max_object_count"]
    max_object_bytes = value["max_object_bytes"]
    max_total_bytes = value["max_total_bytes"]
    if not isinstance(max_object_count, int) or isinstance(max_object_count, bool):
        raise AuthorizationError("max_object_count_not_integer")
    if not isinstance(max_object_bytes, int) or isinstance(max_object_bytes, bool):
        raise AuthorizationError("max_object_bytes_not_integer")
    if not isinstance(max_total_bytes, int) or isinstance(max_total_bytes, bool):
        raise AuthorizationError("max_total_bytes_not_integer")
    if max_object_count <= 0:
        raise AuthorizationError("max_object_count_not_positive")
    if max_object_bytes <= 0:
        raise AuthorizationError("max_object_bytes_not_positive")
    if max_total_bytes <= 0:
        raise AuthorizationError("max_total_bytes_not_positive")
    if max_object_count > ACCEPTED_MAX_OBJECT_COUNT:
        raise AuthorizationError("max_object_count_exceeds_accepted_limit")
    if max_object_bytes > ACCEPTED_MAX_MEDIA_OBJECT_BYTES:
        raise AuthorizationError("max_object_bytes_exceeds_accepted_limit")
    if max_total_bytes > ACCEPTED_MAX_AGGREGATE_BYTES:
        raise AuthorizationError("max_total_bytes_exceeds_accepted_limit")
    if len(allowed_keys) > max_object_count:
        raise AuthorizationError("allowlist_exceeds_count_cap")
    if max_total_bytes < max_object_bytes:
        raise AuthorizationError("max_total_below_object_cap")

    expected_sha256_by_key = value["expected_sha256_by_key"]
    if not isinstance(expected_sha256_by_key, dict):
        raise AuthorizationError("expected_sha256_not_object")
    allow_sha = bool(value["allow_sha256_verification"])
    _validate_expected_sha256_map(expected_sha256_by_key, allowed_keys=seen, allow_sha=allow_sha)

    # Explicit object-role plan (key set must exactly equal allowed_keys).
    object_role_by_key = _validate_object_role_plan(
        value["object_role_by_key"],
        allowed_keys=list(allowed_keys),
        allow_media_byte_reads=bool(value["allow_media_byte_reads"]),
        expected_sha256_by_key=expected_sha256_by_key,
    )

    # Timestamps: timezone-aware UTC, ordered, short window.
    authorized_at = _require_utc_iso(value["authorized_at"], "authorized_at")
    expires_at = _require_utc_iso(value["expires_at"], "expires_at")
    now = _utc_now()
    if expires_at <= authorized_at:
        raise AuthorizationError("expires_at_at_or_before_authorized_at")
    if (expires_at - authorized_at) > _dt.timedelta(seconds=MAX_AUTH_WINDOW_SECONDS):
        raise AuthorizationError("authorization_window_too_long")
    if authorized_at > now + _dt.timedelta(seconds=ALLOWED_FUTURE_AUTHORIZED_AT_SECONDS):
        raise AuthorizationError("authorized_at_in_future")

    if authorized:
        _validate_canonical_operator(value["authorized_by"], field_name="authorized_by")
    elif value["authorized_by"] != "":
        # authorized=false must not carry an operator identity in the template.
        # Allow nonempty for forward compatibility but require canonical if set.
        if value["authorized_by"] != "":
            _validate_canonical_operator(value["authorized_by"], field_name="authorized_by")

    if execute_mode:
        if not authorized:
            raise AuthorizationError("not_authorized_for_execute")
        if expires_at <= now:
            raise AuthorizationError("authorization_expired")
        if not value["allow_metadata_reads"]:
            raise AuthorizationError("metadata_reads_required_for_execute")
        if not value["allow_json_object_reads"]:
            raise AuthorizationError("json_reads_required_for_execute")

    return AuthorizationReport(
        valid=True,
        code="ok",
        configured_alias=configured_alias,
        canonical_prefix=canonical_prefix,
        authorized_object_count=len(allowed_keys),
        authorized_total_bytes=max_total_bytes,
        capabilities=caps,
        object_role_by_key=object_role_by_key,
    )


def _validate_expected_sha256_map(
    mapping: dict[str, Any], *, allowed_keys: set[str], allow_sha: bool,
) -> None:
    if allow_sha and len(mapping) == 0:
        raise AuthorizationError("expected_sha256_required_when_verification_enabled")
    if not allow_sha and len(mapping) > 0:
        raise AuthorizationError("expected_sha256_requires_verification_enabled")
    for key, value in mapping.items():
        if key not in allowed_keys:
            raise AuthorizationError("expected_sha256_unknown_key")
        if not isinstance(value, str) or not _HEX64.match(value):
            raise AuthorizationError("expected_sha256_invalid_value")


# ---------------------------------------------------------------------------
# Server-binding validation helpers (pure, testable, no raw bucket output)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AliasComparison:
    match: bool
    code: str


@dataclass(frozen=True)
class BucketComparison:
    match: bool
    code: str


def compare_server_alias(authorized_alias: str, server_alias: str) -> AliasComparison:
    """Compare the authorized alias against the independently resolved server alias.

    Uses constant-time comparison of the UTF-8 bytes. Never prints or returns
    either value. Returns only a safe stable code.
    """
    if not isinstance(authorized_alias, str) or not isinstance(server_alias, str):
        return AliasComparison(match=False, code="alias_mismatch")
    match = hmac.compare_digest(authorized_alias.encode("utf-8"), server_alias.encode("utf-8"))
    return AliasComparison(match=match, code="alias_match" if match else "alias_mismatch")


def compare_bucket_identity(
    authorized_bucket_name_hash: str, server_bucket_identity: str,
) -> BucketComparison:
    """Compare the authorized bucket hash against the SHA-256 of the server bucket.

    The server bucket name is never printed or returned. The hash is computed
    locally and compared in constant time. Returns only a safe stable code.
    """
    if not isinstance(authorized_bucket_name_hash, str) or not isinstance(server_bucket_identity, str):
        return BucketComparison(match=False, code="bucket_identity_mismatch")
    if not _HEX64.match(authorized_bucket_name_hash):
        return BucketComparison(match=False, code="bucket_identity_mismatch")
    server_hash = hashlib.sha256(server_bucket_identity.encode("utf-8")).hexdigest()
    match = hmac.compare_digest(authorized_bucket_name_hash.lower(), server_hash)
    return BucketComparison(match=match, code="bucket_match" if match else "bucket_identity_mismatch")


def assert_key_authorized(key: str, allowed_keys: set[str] | list[str]) -> None:
    """Reject any key not in the authorized allowlist before backend access."""
    if not isinstance(key, str):
        raise AuthorizationError("key_not_allowlisted")
    allowed = set(allowed_keys) if not isinstance(allowed_keys, set) else allowed_keys
    if key not in allowed:
        raise AuthorizationError("key_not_allowlisted")


# ---------------------------------------------------------------------------
# Fake-storage backend (readiness / dry-run only)
# ---------------------------------------------------------------------------

@dataclass
class FakeB2Backend:
    """In-process fake backend matching the accepted ``B2Backend`` Protocol.

    Holds sanitized JSON bodies keyed by object key. Counts every head / read
    / list / write / delete / signed-url call so the readiness flow can prove
    zero broad listing, zero writes/deletes, and zero signed URLs. Any
    forbidden operation is counted and then fails. Never touches the network.

    Correctness guarantees (PS-041E2-A v2):

    - ``read_bytes`` rejects an oversized body (``len(body) > max_bytes``); it
      never silently returns a truncated body;
    - the exact bytes served by each ``read_bytes`` call are retained in
      ``last_read_bytes`` so the readiness flow can digest the exact bytes that
      the accepted reader parsed;
    - ``total_bytes_read`` accumulates the exact byte count actually served.
    """

    objects: dict[str, dict[str, Any]] = field(default_factory=dict)
    head_calls: list[str] = field(default_factory=list)
    read_calls: list[str] = field(default_factory=list)
    list_calls: list[str] = field(default_factory=list)
    write_attempts: list[str] = field(default_factory=list)
    delete_attempts: list[str] = field(default_factory=list)
    signed_url_attempts: list[str] = field(default_factory=list)
    last_read_bytes: dict[str, bytes] = field(default_factory=dict)
    total_bytes_read: int = 0
    close_calls: int = 0

    def head(self, key: str) -> dict[str, Any] | None:
        self.head_calls.append(key)
        obj = self.objects.get(key)
        if obj is None:
            return None
        return {
            "size_bytes": obj["size_bytes"],
            "etag": obj["etag"],
            "version_id": obj["version_id"],
        }

    def read_bytes(self, key: str, max_bytes: int) -> bytes:
        self.read_calls.append(key)
        obj = self.objects.get(key)
        if obj is None:
            raise OSError("fake missing")
        body = obj["body"]
        if len(body) > max_bytes:
            # Never silently truncate. An oversized read is a hard error.
            raise AssertionError("fake_backend_oversized_read_rejected")
        self.last_read_bytes[key] = body
        self.total_bytes_read += len(body)
        return body

    def list(self, prefix: str, limit: int) -> list[dict[str, Any]]:
        self.list_calls.append(prefix)
        items = [
            {"key": key, "size_bytes": obj["size_bytes"], "etag": obj["etag"], "version_id": obj["version_id"]}
            for key, obj in sorted(self.objects.items())
            if key.startswith(prefix)
        ]
        return items[:limit]

    def write(self, key: str, body: bytes) -> None:
        self.write_attempts.append(key)
        raise AssertionError("forbidden_write_attempted")

    def delete(self, key: str) -> None:
        self.delete_attempts.append(key)
        raise AssertionError("forbidden_delete_attempted")

    def signed_url(self, key: str) -> str:
        self.signed_url_attempts.append(key)
        raise AssertionError("forbidden_signed_url_attempted")

    def close(self) -> None:
        """Close the in-process fake exactly like the live adapter surface.

        The fake has no persistent client, but an explicit close method keeps
        cleanup accounting identical to the accepted live backend contract.
        """
        self.close_calls += 1


# ---------------------------------------------------------------------------
# Role-based fixture body serving (no suffix fallback, no b"{}" default)
# ---------------------------------------------------------------------------

def _fixture_role_bodies(fixture: dict[str, Any]) -> dict[str, bytes]:
    """Map each JSON-read role to its exact serialized fixture body.

    The body is serialized with the same canonical separators the readiness
    flow uses, so the expected digest is stable and matches what the fake
    backend serves.
    """
    bodies: dict[str, bytes] = {}
    for obj in fixture["objects"]:
        role = obj["role"]
        inline = obj.get("inline_json")
        if role in JSON_READ_ROLES and inline is not None:
            bodies[role] = json.dumps(inline, separators=(",", ":")).encode("utf-8")
    return bodies


def _build_fake_backend(
    fixture: dict[str, Any], allowed_keys: list[str], *,
    object_role_by_key: dict[str, str],
) -> FakeB2Backend:
    """Build a fake backend serving the exact fixture body for each role.

    Every allowed key must map to a declared role. A JSON-read role is served
    from the fixture's inline body for that role. A media-byte role is served
    from the bounded media placeholder. Any unrecognized or unconsumable role
    rejects; there is no ``b"{}"`` fallback and no implicit media selection.
    """
    backend = FakeB2Backend()
    role_bodies = _fixture_role_bodies(fixture)
    for key in allowed_keys:
        role = object_role_by_key.get(key)
        if role is None:
            raise AuthorizationError("object_role_missing_key")
        if role in JSON_READ_ROLES:
            body = role_bodies.get(role)
            if body is None:
                raise AuthorizationError("fake_backend_unknown_json_role")
        elif role in MEDIA_BYTE_ROLES:
            body = _MEDIA_PLACEHOLDER
        else:
            raise AuthorizationError("fake_backend_unknown_role")
        backend.objects[key] = {
            "body": body, "size_bytes": len(body),
            "etag": hashlib.sha256(body).hexdigest()[:32],
            "version_id": f"v_{hashlib.sha256(key.encode()).hexdigest()[:8]}",
        }
    return backend


# ---------------------------------------------------------------------------
# Bounded media asset read (pre/post head TOCTOU, caps, aggregate, length)
# ---------------------------------------------------------------------------

def _require_object_metadata(meta: Any) -> dict[str, Any]:
    """Validate that ``meta`` is a well-formed object metadata mapping.

    Used at every head observation (preflight, pre-read, post-read). Rejects
    non-mapping metadata with the stable ``object_metadata_invalid`` code.
    Never echoes the metadata value, key, bucket, or path.
    """
    if not isinstance(meta, dict):
        raise AuthorizationError("object_metadata_invalid")
    return meta


def _require_object_size_bytes(
    value: Any, *, auth_cap: int, accepted_cap: int,
) -> int:
    """Validate a declared ``size_bytes`` value.

    Requirements (all enforced before any byte read):

    - integer type, excluding ``bool``;
    - non-negative;
    - ``<= auth_cap`` (the authorization ``max_object_bytes`` narrowed by the
      accepted media cap);
    - ``<= accepted_cap`` (the immutable ``ACCEPTED_MAX_MEDIA_OBJECT_BYTES``).

    Never echoes the value. Returns the validated integer.
    """
    if not isinstance(value, int) or isinstance(value, bool):
        raise AuthorizationError("object_size_invalid")
    if value < 0:
        raise AuthorizationError("object_size_invalid")
    if value > auth_cap:
        raise AuthorizationError("object_exceeds_authorization_cap")
    if value > accepted_cap:
        raise AuthorizationError("object_exceeds_accepted_cap")
    return value


def _bounded_asset_read(
    backend: FakeB2Backend,
    key: str,
    *,
    auth_max_object_bytes: int,
    accepted_max_bytes: int,
    aggregate_budget: int,
    aggregate_used: int,
) -> tuple[bytes, str, int]:
    """Read one media object through the accepted ``B2Backend`` Protocol with
    full TOCTOU, per-object, aggregate and length protection.

    Every failure normalizes to a stable ``AuthorizationError`` code. No raw
    exception text, path, bucket name, or object key ever escapes through the
    error channel.

    Sequence:

    1. pre-read head (reject malformed metadata, missing object, oversized
       declared size, aggregate overflow);
    2. read no more than the exact approved limit (oversized read rejects,
       never truncates);
    3. reject non-bytes backend response;
    4. reject truncation or length mismatch;
    5. hash the exact returned bytes;
    6. post-read head (reject disappearance, malformed metadata, change);
    7. update the shared aggregate-byte counter.

    Returns ``(body, sha256_hex, new_aggregate_used)``.
    """
    # 1. pre-read head with metadata structure and size validation.
    try:
        before = backend.head(key)
    except Exception:
        # Any backend failure during the pre-read head is normalized. The
        # original exception text is never propagated.
        raise AuthorizationError("backend_head_failed")
    if before is None:
        raise AuthorizationError("approved_object_missing")
    _require_object_metadata(before)
    declared_size = _require_object_size_bytes(
        before.get("size_bytes"),
        auth_cap=auth_max_object_bytes,
        accepted_cap=accepted_max_bytes,
    )
    if aggregate_used + declared_size > aggregate_budget:
        raise AuthorizationError("media_aggregate_overflow")

    approved_limit = min(auth_max_object_bytes, accepted_max_bytes)

    # 2. bounded read. Any backend failure (OSError, disappearance between
    #    pre-head and read, unexpected error) is normalized to a stable code.
    try:
        body = backend.read_bytes(key, approved_limit)
    except OSError:
        # Covers object disappearance between pre-head and read, transient
        # backend OSError, and any other OSError raised by the backend.
        raise AuthorizationError("backend_read_failed")
    except AssertionError as exc:
        message = str(exc)
        if "oversized" in message:
            raise AuthorizationError("media_object_exceeds_approved_limit")
        raise AuthorizationError("backend_read_failed")
    except Exception:
        # Any unexpected backend failure is normalized. The original text is
        # never propagated and never includes raw bucket/key/path values.
        raise AuthorizationError("backend_read_failed")

    # 3. reject non-bytes backend response.
    if not isinstance(body, (bytes, bytearray, memoryview)):
        raise AuthorizationError("backend_response_not_bytes")
    body_bytes = bytes(body)

    # 4. reject length mismatch (truncation or substitution).
    if len(body_bytes) != declared_size:
        raise AuthorizationError("media_length_mismatch")

    # 5. hash the exact returned bytes.
    digest = hashlib.sha256(body_bytes).hexdigest()

    # 6. post-read head with full TOCTOU comparison.
    try:
        after = backend.head(key)
    except Exception:
        raise AuthorizationError("backend_head_failed")
    if after is None:
        raise AuthorizationError("approved_object_disappeared_after_read")
    _require_object_metadata(after)
    # The post-head observation identity (etag, size_bytes, version_id,
    # last_modified_iso) must equal the pre-head identity. A change to any
    # observed field — including last_modified — rejects.
    if _observation_identity(before) != _observation_identity(after):
        raise AuthorizationError("object_changed_during_evidence_run")

    new_aggregate = aggregate_used + len(body_bytes)
    return body_bytes, digest, new_aggregate


# ---------------------------------------------------------------------------
# Validated JSON snapshot store (one read per object, reused by deep copy)
# ---------------------------------------------------------------------------

@dataclass
class ValidatedSnapshot:
    key: str
    role: str
    parsed: dict[str, Any]
    bytes_sha256: str


class SnapshotStore:
    """Holds one validated parsed JSON snapshot per authorized JSON object.

    The guarded candidate reader returns a deep copy of the stored parsed
    value. It never makes a second backend read. Snapshot-consumer calls are
    counted separately from backend reads.
    """

    def __init__(self, *, allowed_keys: set[str]) -> None:
        self._allowed = allowed_keys
        self._snapshots: dict[str, ValidatedSnapshot] = {}
        self.consumer_calls = 0

    def put(self, snapshot: ValidatedSnapshot) -> None:
        self._snapshots[snapshot.key] = snapshot

    def consume(self, key: str) -> dict[str, Any]:
        if key not in self._allowed:
            raise AuthorizationError("key_not_allowlisted")
        snapshot = self._snapshots.get(key)
        if snapshot is None:
            raise AuthorizationError("snapshot_not_validated")
        self.consumer_calls += 1
        return copy.deepcopy(snapshot.parsed)


# ---------------------------------------------------------------------------
# Bounded dry-run flow
# ---------------------------------------------------------------------------

@dataclass
class DryRunReport:
    ok: bool
    authorized_objects: int
    # Actual backend operation counters (derived directly from FakeB2Backend).
    head_calls_total: int = 0
    read_calls_total: int = 0
    unique_json_objects_read: int = 0
    unique_media_objects_read: int = 0
    snapshot_consumer_calls: int = 0
    list_calls: int = 0
    write_attempts: int = 0
    delete_attempts: int = 0
    signed_url_attempts: int = 0
    provider_calls: int = 0
    total_bytes_read: int = 0
    # Hash evidence and observation stability.
    hash_results: list[dict[str, str]] = field(default_factory=list)
    observation_stable: bool = True
    observation_comparisons: int = 0
    # Import result.
    import_created: bool = False
    import_idempotent: bool = False
    passport_schema: str = ""
    bundle_id: str = ""
    # Server-binding comparison codes.
    alias_comparison_code: str = ""
    bucket_comparison_code: str = ""
    # Explicit role plan (key -> role) actually used.
    role_plan: dict[str, str] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


def run_dry_run(
    auth: dict[str, Any],
    *,
    fixture_path: Path,
    campaign_id: str = "camp_ps041e2_readiness",
    backend: "FakeB2Backend | None" = None,
    server_alias: str = DEFAULT_FAKE_SERVER_ALIAS,
    server_bucket_identity: str = DEFAULT_FAKE_SERVER_BUCKET_IDENTITY,
) -> DryRunReport:
    """Run one bounded fake-storage evidence flow.

    Validates the authorization, compares the authorized alias and bucket hash
    against the independently injected server values, then honors every read
    permission flag before any backend operation. Builds an injected
    ``FakeB2Backend`` from the sanitized fixture (if not provided), reads each
    authorized JSON object exactly once through the accepted
    ``BoundedB2ImportReader``, retains the validated parsed snapshot, and
    reconstructs the candidate and idempotency candidate from deep copies of
    that snapshot (zero extra backend reads). Media byte reads use the bounded
    asset reader. Observation stability is enforced by a full before/after
    ``(etag, size_bytes, version_id)`` comparison across every allowlisted
    object.
    """
    report_validation = validate_authorization(auth, execute_mode=False)
    allowed_keys: list[str] = list(auth["allowed_keys"])
    canonical_prefix = report_validation.canonical_prefix
    configured_alias = report_validation.configured_alias
    object_role_by_key: dict[str, str] = dict(report_validation.object_role_by_key)
    role_to_key = resolve_role_to_key(object_role_by_key)
    authorized_set: set[str] = set(allowed_keys)

    allow_metadata = bool(auth["allow_metadata_reads"])
    allow_json = bool(auth["allow_json_object_reads"])
    allow_media = bool(auth["allow_media_byte_reads"])
    expected_sha256_by_key: dict[str, str] = dict(auth.get("expected_sha256_by_key", {}))

    # Independent server-binding comparison BEFORE any backend operation.
    alias_cmp = compare_server_alias(configured_alias, server_alias)
    if not alias_cmp.match:
        raise AuthorizationError(alias_cmp.code)
    bucket_cmp = compare_bucket_identity(auth["allowed_bucket_name_hash"], server_bucket_identity)
    if not bucket_cmp.match:
        raise AuthorizationError(bucket_cmp.code)

    # Permission-before-operation: fail closed before constructing the backend
    # or reading any metadata, JSON, or media bytes.
    if not allow_metadata:
        raise AuthorizationError("metadata_reads_required")
    if not allow_json:
        raise AuthorizationError("json_reads_required")

    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))

    # Build the injected backend only after permission gates pass.
    if backend is None:
        backend = _build_fake_backend(
            fixture, allowed_keys, object_role_by_key=object_role_by_key,
        )

    reader_config = B2ImportReaderConfig(
        enabled=True,
        bucket_alias=configured_alias,
        root_prefix=canonical_prefix,
        max_listed_objects=min(auth["max_object_count"], ACCEPTED_MAX_OBJECT_COUNT),
        max_json_bytes=min(auth["max_object_bytes"], ACCEPTED_MAX_JSON_OBJECT_BYTES),
        max_asset_bytes=min(auth["max_object_bytes"], ACCEPTED_MAX_MEDIA_OBJECT_BYTES),
        max_aggregate_bytes=min(auth["max_total_bytes"], ACCEPTED_MAX_AGGREGATE_BYTES),
    )
    reader = BoundedB2ImportReader(backend, reader_config)

    # ------------------------------------------------------------------
    # Initial observation: head every allowlisted object, store the full
    # metadata tuple. Reject any missing approved object before any read.
    #
    # Head-metadata caps (PS-041E2-A v2): for every observed object we
    # require well-formed metadata, an integer non-negative ``size_bytes``
    # (excluding bool), per-object authorization and accepted caps, and a
    # declared-inventory aggregate total within both the authorization
    # ``max_total_bytes`` and the immutable ``ACCEPTED_MAX_AGGREGATE_BYTES``.
    # These caps apply even when ``allow_media_byte_reads=false``; an
    # oversized declared final delivery still rejects before any byte read.
    # No silent clamping is ever performed.
    # ------------------------------------------------------------------
    auth_per_object_cap = min(auth["max_object_bytes"], ACCEPTED_MAX_MEDIA_OBJECT_BYTES)
    auth_total_cap = min(auth["max_total_bytes"], ACCEPTED_MAX_AGGREGATE_BYTES)
    initial_observation: dict[str, tuple[Any, Any, Any]] = {}
    total_declared_size = 0
    for key in allowed_keys:
        try:
            meta = backend.head(key)
        except Exception:
            # Any backend failure during the preflight head is normalized;
            # raw exception text never escapes.
            raise AuthorizationError("backend_head_failed")
        if meta is None:
            raise AuthorizationError("approved_object_missing")
        _require_object_metadata(meta)
        size_value = meta.get("size_bytes")
        validated_size = _require_object_size_bytes(
            size_value,
            auth_cap=auth_per_object_cap,
            accepted_cap=ACCEPTED_MAX_MEDIA_OBJECT_BYTES,
        )
        total_declared_size += validated_size
        initial_observation[key] = (
            meta.get("etag"), validated_size, meta.get("version_id"),
        )

    if total_declared_size > auth_total_cap:
        raise AuthorizationError("declared_inventory_exceeds_authorization_total")
    if total_declared_size > ACCEPTED_MAX_AGGREGATE_BYTES:
        raise AuthorizationError("declared_inventory_exceeds_accepted_total")

    # ------------------------------------------------------------------
    # One validated backend JSON read per authorized JSON object. The accepted
    # reader performs head-before, size check, read_bytes, head-after TOCTOU
    # and (when the reference carries sha256) hash verification. The exact
    # bytes served are digested and bound to the retained parsed snapshot.
    # ------------------------------------------------------------------
    snapshot_store = SnapshotStore(allowed_keys=authorized_set)
    hash_results: list[dict[str, str]] = []
    consumed_expected: set[str] = set()

    for role in (ROLE_STAGE_A_STORYBOARD, ROLE_STAGE_B0_MANIFEST,
                 ROLE_STAGE_B1_MANIFEST, ROLE_STAGE_B2_MANIFEST):
        key = role_to_key[role]
        expected = expected_sha256_by_key.get(key)
        ref = B2ObjectReference(
            backend="b2_s3", bucket_alias=configured_alias, object_key=key,
            sha256=expected,
        )
        parsed = reader.read_json(ref)
        observed_bytes = backend.last_read_bytes.get(key, b"")
        digest = hashlib.sha256(observed_bytes).hexdigest()
        if expected is not None:
            if hmac.compare_digest(digest, expected):
                hash_results.append({"key": key, "role": role, "status": "matched", "sha256": digest})
                consumed_expected.add(key)
            else:
                hash_results.append({"key": key, "role": role, "status": "mismatch", "sha256": digest})
                raise AuthorizationError("unexpected_hash_mismatch")
        else:
            hash_results.append({"key": key, "role": role, "status": "observed", "sha256": digest})
        snapshot_store.put(ValidatedSnapshot(key=key, role=role, parsed=parsed, bytes_sha256=digest))

    # Optional stage_c_composition JSON read (only if present in the plan).
    stage_c_key = role_to_key.get(ROLE_STAGE_C_COMPOSITION)
    if stage_c_key is not None:
        expected = expected_sha256_by_key.get(stage_c_key)
        ref = B2ObjectReference(
            backend="b2_s3", bucket_alias=configured_alias, object_key=stage_c_key,
            sha256=expected,
        )
        parsed = reader.read_json(ref)
        observed_bytes = backend.last_read_bytes.get(stage_c_key, b"")
        digest = hashlib.sha256(observed_bytes).hexdigest()
        if expected is not None:
            if hmac.compare_digest(digest, expected):
                hash_results.append({"key": stage_c_key, "role": ROLE_STAGE_C_COMPOSITION,
                                     "status": "matched", "sha256": digest})
                consumed_expected.add(stage_c_key)
            else:
                hash_results.append({"key": stage_c_key, "role": ROLE_STAGE_C_COMPOSITION,
                                     "status": "mismatch", "sha256": digest})
                raise AuthorizationError("unexpected_hash_mismatch")
        else:
            hash_results.append({"key": stage_c_key, "role": ROLE_STAGE_C_COMPOSITION,
                                 "status": "observed", "sha256": digest})
        snapshot_store.put(ValidatedSnapshot(key=stage_c_key, role=ROLE_STAGE_C_COMPOSITION,
                                             parsed=parsed, bytes_sha256=digest))

    # ------------------------------------------------------------------
    # Bounded media byte reads (only for media-byte roles, only when allowed).
    # Each read uses the full pre/post head TOCTOU, per-object cap, aggregate
    # budget and length-match protection.
    # ------------------------------------------------------------------
    aggregate_used = backend.total_bytes_read
    media_keys_read: list[str] = []
    for key in allowed_keys:
        role = object_role_by_key[key]
        if role not in MEDIA_BYTE_ROLES:
            continue
        if not allow_media:
            continue
        body, digest, aggregate_used = _bounded_asset_read(
            backend, key,
            auth_max_object_bytes=min(auth["max_object_bytes"], ACCEPTED_MAX_MEDIA_OBJECT_BYTES),
            accepted_max_bytes=ACCEPTED_MAX_MEDIA_OBJECT_BYTES,
            aggregate_budget=min(auth["max_total_bytes"], ACCEPTED_MAX_AGGREGATE_BYTES),
            aggregate_used=aggregate_used,
        )
        media_keys_read.append(key)
        expected = expected_sha256_by_key.get(key)
        if expected is not None:
            if hmac.compare_digest(digest, expected):
                hash_results.append({"key": key, "role": role, "status": "matched", "sha256": digest})
                consumed_expected.add(key)
            else:
                hash_results.append({"key": key, "role": role, "status": "mismatch", "sha256": digest})
                raise AuthorizationError("unexpected_hash_mismatch")
        else:
            hash_results.append({"key": key, "role": role, "status": "computed", "sha256": digest})

    # ------------------------------------------------------------------
    # Build the B2-backed ImportBundleRequest from the explicit role plan.
    # Every required descriptor consumes its exact authorized B2 key; no
    # inline_json survives for any planned role.
    # ------------------------------------------------------------------
    bundle_request = _build_b2_bundle_request(
        fixture, role_to_key=role_to_key,
        configured_alias=configured_alias,
        expected_sha256_by_key=expected_sha256_by_key,
    )

    # ------------------------------------------------------------------
    # Guarded candidate reader: returns a deep copy of the validated parsed
    # snapshot. Asserts the key is authorized and was validated. Counts
    # consumer calls separately from backend reads. Zero backend reads here.
    # ------------------------------------------------------------------
    def _guarded_reader(ref: B2ObjectReference) -> dict[str, Any]:
        return snapshot_store.consume(ref.object_key)

    candidate = build_candidate(
        campaign_id, bundle_request, b2_json_reader=_guarded_reader,
        server_bucket_alias=configured_alias, server_import_root=canonical_prefix,
    )
    candidate_again = build_candidate(
        campaign_id, bundle_request, b2_json_reader=_guarded_reader,
        server_bucket_alias=configured_alias, server_import_root=canonical_prefix,
    )
    import_idempotent = (
        candidate.bundle.bundle_id == candidate_again.bundle.bundle_id
        and candidate.bundle.bundle_fingerprint == candidate_again.bundle.bundle_fingerprint
    )
    passport = passport_for(candidate)

    # ------------------------------------------------------------------
    # Verify every expected digest was consumed by an actual read.
    # ------------------------------------------------------------------
    unconsumed = set(expected_sha256_by_key) - consumed_expected
    if unconsumed:
        raise AuthorizationError("expected_hash_unconsumed")

    # ------------------------------------------------------------------
    # Final observation: head every allowlisted object again and compare the
    # full metadata tuple. Any difference (including missing) aborts. No
    # missing-only shortcut. No broad listing.
    # ------------------------------------------------------------------
    observation_comparisons = 0
    for key in allowed_keys:
        try:
            meta = backend.head(key)
        except Exception:
            # Backend failure during final observation is normalized; raw
            # exception text never escapes through the error channel.
            raise AuthorizationError("backend_head_failed")
        if meta is None:
            raise AuthorizationError("object_changed_during_evidence_run")
        _require_object_metadata(meta)
        final = (meta.get("etag"), meta.get("size_bytes"), meta.get("version_id"))
        if initial_observation[key] != final:
            raise AuthorizationError("object_changed_during_evidence_run")
        observation_comparisons += 1

    json_keys_in_plan = [k for k in allowed_keys if object_role_by_key[k] in JSON_READ_ROLES]
    return DryRunReport(
        ok=True,
        authorized_objects=len(allowed_keys),
        head_calls_total=len(backend.head_calls),
        read_calls_total=len(backend.read_calls),
        unique_json_objects_read=len(json_keys_in_plan),
        unique_media_objects_read=len(media_keys_read),
        snapshot_consumer_calls=snapshot_store.consumer_calls,
        list_calls=len(backend.list_calls),
        write_attempts=len(backend.write_attempts),
        delete_attempts=len(backend.delete_attempts),
        signed_url_attempts=len(backend.signed_url_attempts),
        provider_calls=0,
        total_bytes_read=backend.total_bytes_read,
        hash_results=hash_results,
        observation_stable=True,
        observation_comparisons=observation_comparisons,
        import_created=True,
        import_idempotent=import_idempotent,
        passport_schema=passport.passport_schema,
        bundle_id=candidate.bundle.bundle_id,
        alias_comparison_code=alias_cmp.code,
        bucket_comparison_code=bucket_cmp.code,
        role_plan=object_role_by_key,
    )


def expected_hashes_for_fixture(
    fixture_path: Path, allowed_keys: list[str],
    object_role_by_key: dict[str, str],
) -> dict[str, str]:
    """Compute the SHA-256 the fake backend will serve for each allowlisted key.

    Used by smokes and tests to populate ``expected_sha256_by_key``. The hash
    is computed from the exact sanitized bytes the ``FakeB2Backend`` serves for
    the key's declared role. A JSON-read role is served from the fixture's
    inline body for that role; a media-byte role is served from the bounded
    media placeholder. Unrecognized roles reject (no fallback).
    """
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    role_bodies = _fixture_role_bodies(fixture)
    out: dict[str, str] = {}
    for key in allowed_keys:
        role = object_role_by_key.get(key)
        if role is None:
            raise AuthorizationError("object_role_missing_key")
        if role in JSON_READ_ROLES:
            body = role_bodies.get(role)
            if body is None:
                raise AuthorizationError("fake_backend_unknown_json_role")
        elif role in MEDIA_BYTE_ROLES:
            body = _MEDIA_PLACEHOLDER
        else:
            raise AuthorizationError("fake_backend_unknown_role")
        out[key] = hashlib.sha256(body).hexdigest()
    return out


def _build_b2_bundle_request(
    fixture: dict[str, Any], *,
    role_to_key: dict[str, str],
    configured_alias: str,
    expected_sha256_by_key: dict[str, str],
) -> ImportBundleRequest:
    """Build a PS-041D-compatible bundle that references fake B2 objects.

    Every descriptor whose role appears in the explicit role plan consumes its
    exact authorized B2 key. Its ``inline_json`` is removed unconditionally and
    its ``b2_reference`` is set to the exact authorized key (carrying the
    expected SHA-256 as defense in depth when present). There is no inline
    fallback: if a planned role has no exact authorized key the build fails
    with a stable code. An approved key that is not consumed by any declared
    role also fails.
    """
    data = copy.deepcopy(fixture)
    consumed_keys: set[str] = set()
    for obj in data["objects"]:
        role = obj["role"]
        if role not in role_to_key:
            continue
        key = role_to_key[role]
        if obj.get("missing"):
            # A missing descriptor cannot carry a B2 reference.
            raise AuthorizationError("object_role_missing_object_has_no_content")
        obj.pop("inline_json", None)
        obj.pop("b2_reference", None)
        ref_payload: dict[str, Any] = {
            "backend": "b2_s3", "bucket_alias": configured_alias, "object_key": key,
        }
        expected = expected_sha256_by_key.get(key)
        if expected is not None:
            ref_payload["sha256"] = expected
        obj["b2_reference"] = ref_payload
        consumed_keys.add(key)

    planned_keys = set(role_to_key.values())
    unconsumed_approved = planned_keys - consumed_keys
    if unconsumed_approved:
        raise AuthorizationError("object_role_approved_key_unconsumed")
    return ImportBundleRequest.model_validate(data)


# ---------------------------------------------------------------------------
# Execute mode (PS-041E2-B Phase-1: implemented live executor)
# ---------------------------------------------------------------------------

# Canonical execution-gate contract. This single source of truth is consumed by
# ``_execute_gates()``, the ``--check-readiness`` summary, the ``--execute``
# mode stderr output, the focused tests, the spec, the runbook, the proof
# document, and the ``execution-gates.json`` evidence artifact. The documented
# count is ``FUTURE_EXECUTE_GATES_COUNT``; no separately maintained list may
# drift from this constant.
#
# PS-041E2-B Phase-1 implements all 22 gates. The constant name is preserved
# for backward compatibility with the accepted PS-041E2-A contract; the gates
# are now implemented live gates (no longer future-only). ``LIVE_EXECUTE_GATES``
# is an alias of the same constant — there is exactly one source of truth.
FUTURE_EXECUTE_GATES: tuple[str, ...] = (
    "authorization document exists and parses defensively under an approved /tmp authorization directory",
    "schema exact match",
    "authorized=true",
    "authorized_by is a nonempty canonical operator identity",
    "authorization not expired and within the short maximum validity window",
    "exact configured alias match against independently resolved server alias",
    "exact bucket identity match against SHA-256 of independently resolved server bucket",
    "exact canonical prefix match (no normalization)",
    "exact object allowlist (count and byte caps > 0 and within accepted upper bounds)",
    "explicit object-role plan (key set equals allowed_keys, required roles exactly once, no reserved roles)",
    "metadata reads allowed",
    "JSON reads allowed",
    "write=false",
    "delete=false",
    "signed urls=false",
    "provider calls=false",
    "required server-side B2 configuration present (checked without printing values)",
    "no credential passed through CLI arguments",
    "no credential stored in authorization JSON",
    "repository tree clean",
    "branch and HEAD match the accepted PS-041E2 execution commit and the current remote refs/heads/accepted/proofstudio",
    "--confirm-controlled-live-read flag present",
)
FUTURE_EXECUTE_GATES_COUNT: int = len(FUTURE_EXECUTE_GATES)
LIVE_EXECUTE_GATES: tuple[str, ...] = FUTURE_EXECUTE_GATES
LIVE_EXECUTE_GATES_COUNT: int = FUTURE_EXECUTE_GATES_COUNT
assert len(set(FUTURE_EXECUTE_GATES)) == FUTURE_EXECUTE_GATES_COUNT, (
    "FUTURE_EXECUTE_GATES must contain no duplicate entries"
)

# ---------------------------------------------------------------------------
# Live authorization schema (PS-041E2-B strict superset of the readiness schema)
# ---------------------------------------------------------------------------

LIVE_SCHEMA = "proofstudio.ps041e2.b2_live_authorization.v1"
LIVE_PURPOSE = "PS-041E2-B one controlled read-only B2 evidence run"

PS_041E2B_BRANCH = "ps-041e2b/authorized-read-only-b2-evidence-run-v1"
ACCEPTED_EXECUTION_REF = "origin/accepted/proofstudio"

LIVE_AUTHORIZATION_DIR = "/tmp/proofstudio-ps041e2-authorizations"
LIVE_EVIDENCE_DIR = "/tmp/proofstudio-ps041e2-live-evidence"

_HEX40 = re.compile(r"^[0-9a-f]{40}$")
# Path-safe evidence_run_id: bounded lowercase letters/digits/dashes, no leading/
# trailing dash, no double dash, 1-64 chars.
_EVIDENCE_RUN_ID = re.compile(r"^[a-z0-9]([a-z0-9-]{0,62}[a-z0-9])?$")

LIVE_REQUIRED_FIELDS: tuple[str, ...] = (
    # Readiness contract fields (same canonical set):
    "schema", "authorized", "authorized_by", "authorized_at", "expires_at",
    "configured_alias", "allowed_bucket_name_hash", "allowed_prefix", "allowed_keys",
    "object_role_by_key",
    "max_object_count", "max_object_bytes", "max_total_bytes",
    "allow_metadata_reads", "allow_json_object_reads", "allow_media_byte_reads",
    "allow_sha256_verification", "allow_write", "allow_delete",
    "allow_signed_urls", "allow_provider_calls", "expected_sha256_by_key",
    "purpose",
    # Live-specific strict fields:
    "evidence_run_id", "execution_commit",
)

LIVE_EVIDENCE_FILES: tuple[str, ...] = (
    "authorization-summary.json",
    "execution-gates.json",
    "git-binding.json",
    "server-binding.json",
    "approved-object-inventory.json",
    "object-role-plan.json",
    "normalized-b2-references.json",
    "json-read-results.json",
    "hash-verification-results.json",
    "media-read-results.json",
    "observation-stability.json",
    "import-result.json",
    "idempotency-result.json",
    "private-lineage-summary.json",
    "private-passport-summary.json",
    "operation-counts.json",
    "cleanup-verification.txt",
    "classified-security-scan.txt",
    "known-limitations.txt",
    "execution-summary.json",
)


def validate_live_authorization(value: dict[str, Any]) -> AuthorizationReport:
    """Validate one live authorization dict against the strict live contract.

    The live contract is a strict superset of the readiness contract:

    - exact schema = ``proofstudio.ps041e2.b2_live_authorization.v1``;
    - exact purpose = ``PS-041E2-B one controlled read-only B2 evidence run``;
    - ``evidence_run_id`` present, canonical, bounded, path-safe;
    - ``execution_commit`` present, lowercase hex40;
    - ``authorized=true``;
    - ``authorized_by`` present and canonical;
    - ``authorized_at`` and ``expires_at`` UTC ISO, ordered, within the
      24-hour maximum window, not expired at the check time;
    - all readiness structural and capability constraints (canonical alias /
      prefix / keys / role plan, hard count and byte caps within accepted
      limits, every denied capability fixed false).

    No credential field is ever read. No environment variable is read. No
    network access occurs. The function is pure and total on its input.
    """
    _bounded_structure_check(value)

    unknown = sorted(set(value) - set(LIVE_REQUIRED_FIELDS))
    if unknown:
        raise AuthorizationError("unknown_live_authorization_field")
    missing = sorted(set(LIVE_REQUIRED_FIELDS) - set(value))
    if missing:
        raise AuthorizationError("missing_live_authorization_field")

    if value["schema"] != LIVE_SCHEMA:
        raise AuthorizationError("unsupported_live_authorization_schema")
    if value["purpose"] != LIVE_PURPOSE:
        raise AuthorizationError("unsupported_live_purpose")

    evidence_run_id = value["evidence_run_id"]
    if not isinstance(evidence_run_id, str) or not _EVIDENCE_RUN_ID.match(evidence_run_id):
        raise AuthorizationError("evidence_run_id_invalid")
    if "--" in evidence_run_id:
        raise AuthorizationError("evidence_run_id_invalid")

    execution_commit = value["execution_commit"]
    if not isinstance(execution_commit, str) or not _HEX40.match(execution_commit):
        raise AuthorizationError("execution_commit_invalid")

    authorized = value["authorized"]
    if not isinstance(authorized, bool) or not authorized:
        raise AuthorizationError("live_not_authorized")

    configured_alias = _validate_canonical_alias(value["configured_alias"])

    bucket_hash = value["allowed_bucket_name_hash"]
    if not isinstance(bucket_hash, str) or not _HEX64.match(bucket_hash):
        raise AuthorizationError("bucket_hash_invalid")

    canonical_prefix = _validate_canonical_prefix(value["allowed_prefix"])

    allowed_keys = value["allowed_keys"]
    if not isinstance(allowed_keys, list):
        raise AuthorizationError("allowlist_not_list")
    if len(allowed_keys) == 0:
        raise AuthorizationError("allowlist_empty")
    seen: set[str] = set()
    for key in allowed_keys:
        if not isinstance(key, str) or not _is_safe_key(key):
            raise AuthorizationError("allowlist_key_unsafe")
        if key in seen:
            raise AuthorizationError("allowlist_duplicate_key")
        seen.add(key)
        if not _key_inside_prefix(key, canonical_prefix):
            raise AuthorizationError("allowlist_key_outside_prefix")

    for cap in ("allow_metadata_reads", "allow_json_object_reads",
                "allow_media_byte_reads", "allow_sha256_verification", *DENIED_CAPABILITY_FIELDS):
        cap_value = value[cap]
        if not isinstance(cap_value, bool):
            raise AuthorizationError(f"capability_not_boolean:{cap}")

    for cap in DENIED_CAPABILITY_FIELDS:
        if value[cap]:
            raise AuthorizationError(f"denied_capability_enabled:{cap}")

    if not value["allow_metadata_reads"]:
        raise AuthorizationError("metadata_reads_required_for_execute")
    if not value["allow_json_object_reads"]:
        raise AuthorizationError("json_reads_required_for_execute")

    max_object_count = value["max_object_count"]
    max_object_bytes = value["max_object_bytes"]
    max_total_bytes = value["max_total_bytes"]
    if not isinstance(max_object_count, int) or isinstance(max_object_count, bool):
        raise AuthorizationError("max_object_count_not_integer")
    if not isinstance(max_object_bytes, int) or isinstance(max_object_bytes, bool):
        raise AuthorizationError("max_object_bytes_not_integer")
    if not isinstance(max_total_bytes, int) or isinstance(max_total_bytes, bool):
        raise AuthorizationError("max_total_bytes_not_integer")
    if max_object_count <= 0:
        raise AuthorizationError("max_object_count_not_positive")
    if max_object_bytes <= 0:
        raise AuthorizationError("max_object_bytes_not_positive")
    if max_total_bytes <= 0:
        raise AuthorizationError("max_total_bytes_not_positive")
    if max_object_count > ACCEPTED_MAX_OBJECT_COUNT:
        raise AuthorizationError("max_object_count_exceeds_accepted_limit")
    if max_object_bytes > ACCEPTED_MAX_MEDIA_OBJECT_BYTES:
        raise AuthorizationError("max_object_bytes_exceeds_accepted_limit")
    if max_total_bytes > ACCEPTED_MAX_AGGREGATE_BYTES:
        raise AuthorizationError("max_total_bytes_exceeds_accepted_limit")
    if len(allowed_keys) > max_object_count:
        raise AuthorizationError("allowlist_exceeds_count_cap")
    if max_total_bytes < max_object_bytes:
        raise AuthorizationError("max_total_below_object_cap")

    expected_sha256_by_key = value["expected_sha256_by_key"]
    if not isinstance(expected_sha256_by_key, dict):
        raise AuthorizationError("expected_sha256_not_object")
    _validate_expected_sha256_map(
        expected_sha256_by_key, allowed_keys=seen,
        allow_sha=bool(value["allow_sha256_verification"]),
    )

    object_role_by_key = _validate_object_role_plan(
        value["object_role_by_key"],
        allowed_keys=list(allowed_keys),
        allow_media_byte_reads=bool(value["allow_media_byte_reads"]),
        expected_sha256_by_key=expected_sha256_by_key,
    )

    _validate_canonical_operator(value["authorized_by"], field_name="authorized_by")
    authorized_at = _require_utc_iso(value["authorized_at"], "authorized_at")
    expires_at = _require_utc_iso(value["expires_at"], "expires_at")
    now = _utc_now()
    if expires_at <= authorized_at:
        raise AuthorizationError("expires_at_at_or_before_authorized_at")
    if (expires_at - authorized_at) > _dt.timedelta(seconds=MAX_AUTH_WINDOW_SECONDS):
        raise AuthorizationError("authorization_window_too_long")
    if authorized_at > now + _dt.timedelta(seconds=ALLOWED_FUTURE_AUTHORIZED_AT_SECONDS):
        raise AuthorizationError("authorized_at_in_future")
    if expires_at <= now:
        raise AuthorizationError("live_authorization_expired")

    caps = {cap: bool(value[cap]) for cap in (
        "allow_metadata_reads", "allow_json_object_reads",
        "allow_media_byte_reads", "allow_sha256_verification", *DENIED_CAPABILITY_FIELDS,
    )}
    return AuthorizationReport(
        valid=True,
        code="ok",
        configured_alias=configured_alias,
        canonical_prefix=canonical_prefix,
        authorized_object_count=len(allowed_keys),
        authorized_total_bytes=max_total_bytes,
        capabilities=caps,
        object_role_by_key=object_role_by_key,
    )


def load_live_authorization(path: Path) -> dict[str, Any]:
    """Defensively load one live authorization document.

    Performs every ``load_authorization`` defensive check, then additionally
    confines the resolved path to ``LIVE_AUTHORIZATION_DIR`` and validates the
    document against the strict live schema.
    """
    basename = path.name
    if basename in FORBIDDEN_AUTH_BASENAMES:
        raise AuthorizationError("authorization_path_forbidden_basename")
    if not basename.endswith(".json"):
        raise AuthorizationError("authorization_path_not_json")
    try:
        is_symlink = path.is_symlink()
    except OSError:
        raise AuthorizationError("authorization_path_unreadable")
    if is_symlink:
        raise AuthorizationError("authorization_path_symlink")
    try:
        resolved = path.resolve(strict=True)
    except OSError:
        raise AuthorizationError("authorization_path_unreadable")
    base = Path(LIVE_AUTHORIZATION_DIR).resolve(strict=False)
    try:
        relative = resolved.relative_to(base)
    except ValueError:
        raise AuthorizationError("live_authorization_outside_approved_dir")
    if str(relative) == "." or any(part == ".." for part in relative.parts):
        raise AuthorizationError("live_authorization_outside_approved_dir")
    # Reuse the readiness loader for size/UTF-8/JSON/structure bounds.
    auth = load_authorization(path)
    validate_live_authorization(auth)
    return auth


# ---------------------------------------------------------------------------
# Injectable live execution dependencies (Protocol-style)
# ---------------------------------------------------------------------------


# Environment-variable names that may be inspected for *membership* before the
# gates pass. The values are never read until the CredentialProvider runs.
NON_SECRET_CONFIG_ENV: tuple[str, ...] = (
    "PROOFSTUDIO_IMPORT_BUCKET_ALIAS",
    "PROOFSTUDIO_IMPORT_ROOT",
    "B2_BUCKET",
    "B2_REGION",
)
# Environment-variable names whose *values* are secret. Pre-gate logic may
# check membership only (``name in os.environ``); it may never call
# ``os.environ.get(name)`` / ``os.environ[name]`` for any of these.
SECRET_VALUE_ENV: frozenset[str] = frozenset({"B2_KEY_ID", "B2_APP_KEY"})


class EnvAccessBoundary(Protocol):
    """Injectable environment-access boundary with key-only secret presence.

    Pre-gate code is restricted to:

    - :meth:`read_non_secret` for the four non-secret configuration names
      (``PROOFSTUDIO_IMPORT_BUCKET_ALIAS``, ``PROOFSTUDIO_IMPORT_ROOT``,
      ``B2_BUCKET``, ``B2_REGION``);
    - :meth:`secret_name_present` for the two secret names
      (``B2_KEY_ID``, ``B2_APP_KEY``). This method inspects the
      environment-key *set only* and never invokes ``get`` /
      ``__getitem__`` on a secret name.

    Secret values may be read only through :meth:`read_secret_after_gates`,
    which is reserved for the :class:`CredentialProvider` (the single
    component permitted to read secret values). The CredentialProvider runs
    only after every one of the 22 gates has passed; the executor calls
    :meth:`mark_gates_completed` immediately after gate 22 succeeds and
    before invoking the CredentialProvider.

    The injected test implementation raises
    ``AuthorizationError("secret_value_read_before_gate_completion")`` if a
    secret value is requested before :meth:`mark_gates_completed` is
    called. ``not recorded`` is never equivalent to ``not read``: the test
    boundary records every actual value access.
    """

    def read_non_secret(self, name: str) -> str: ...
    def secret_name_present(self, name: str) -> bool: ...
    def read_secret_after_gates(self, name: str) -> str: ...
    def mark_gates_completed(self) -> None: ...

    @property
    def secret_value_reads(self) -> list[tuple[str, str]]: ...
    @property
    def non_secret_reads(self) -> list[str]: ...
    @property
    def membership_checks(self) -> list[str]: ...
    @property
    def gates_completed(self) -> bool: ...


class RealEnvAccessBoundary:
    """Production environment-access boundary.

    Captures the live environment-key set once at construction time and
    uses that snapshot for every :meth:`secret_name_present` check. The
    snapshot is the *only* key-set inspection this boundary performs; it
    never invokes ``get`` / ``__getitem__`` for ``B2_KEY_ID`` or
    ``B2_APP_KEY`` from :meth:`secret_name_present`. The two secret values
    can be retrieved only through :meth:`read_secret_after_gates` and only
    after :meth:`mark_gates_completed` has been called.

    This boundary does not monkeypatch ``os._Environ`` and never patches
    any built-in mapping type.
    """

    def __init__(self, env: Any = None) -> None:
        self._env = os.environ if env is None else env
        # Snapshot the environment keys ONCE. This is the only key-set
        # inspection performed for secret-name presence; subsequent
        # membership checks use this snapshot and never invoke
        # ``get`` / ``__getitem__`` on a secret name.
        try:
            self._keys_snapshot: frozenset[str] = frozenset(str(k) for k in self._env.keys())
        except Exception:
            self._keys_snapshot = frozenset()
        self._secret_value_reads: list[tuple[str, str]] = []
        self._non_secret_reads: list[str] = []
        self._membership_checks: list[str] = []
        self._gates_completed = False

    def read_non_secret(self, name: str) -> str:
        if name in SECRET_VALUE_ENV:
            # Non-secret reader used on a secret name: hard fail (never
            # silently return the value).
            raise AuthorizationError("non_secret_read_on_secret_name")
        self._non_secret_reads.append(name)
        try:
            return self._env.get(name, "") or ""
        except Exception:
            return ""

    def secret_name_present(self, name: str) -> bool:
        # Keys-only inspection against the snapshot. NEVER invokes
        # ``get`` / ``__getitem__`` for any name.
        self._membership_checks.append(name)
        return name in self._keys_snapshot

    def mark_gates_completed(self) -> None:
        self._gates_completed = True

    def read_secret_after_gates(self, name: str) -> str:
        if name not in SECRET_VALUE_ENV:
            raise AuthorizationError("secret_read_on_non_secret_name")
        if not self._gates_completed:
            self._secret_value_reads.append((name, "before_gates"))
            raise AuthorizationError("secret_value_read_before_gate_completion")
        self._secret_value_reads.append((name, "after_gates"))
        try:
            return self._env.get(name, "") or ""
        except Exception:
            return ""

    @property
    def secret_value_reads(self) -> list[tuple[str, str]]:
        return list(self._secret_value_reads)

    @property
    def non_secret_reads(self) -> list[str]:
        return list(self._non_secret_reads)

    @property
    def membership_checks(self) -> list[str]:
        return list(self._membership_checks)

    @property
    def gates_completed(self) -> bool:
        return self._gates_completed


@dataclass(frozen=True)
class GitState:
    """Pure, injectable view of the repository Git state.

    Real runs construct this from ``git`` via subprocess. Tests inject a fake.
    ``remote_accepted_commit`` is the value of the remote
    ``refs/heads/accepted/proofstudio`` as resolved by an injectable
    :class:`RemoteRefResolver`. When ``remote_accepted_commit`` is the empty
    string the remote lookup failed and the binding must fail closed.
    """

    branch: str
    head_commit: str
    accepted_commit: str
    accepted_ref: str
    tree_clean: bool
    remote_accepted_commit: str = ""


class RemoteRefResolver(Protocol):
    """Callable that resolves the current remote ``refs/heads/accepted/proofstudio``.

    Real CLI runs use a bounded ``git ls-remote`` subprocess with a timeout.
    Tests inject a fake. The resolver returns the 40-hex commit the remote
    advertises, or the empty string when the remote cannot be reached. The
    executor treats the empty string as a hard failure: it never proceeds to
    credential retrieval when the remote binding cannot be established.
    """

    call_count: int

    def __call__(self, ref: str) -> str: ...


@dataclass(frozen=True)
class ServerConfig:
    """Pure, injectable view of the server-side B2 configuration.

    All four identity fields are explicit and required; there is no implicit
    default. The real CLI resolver rejects empty values for any of them
    before credential retrieval.

    - ``alias`` is the canonical configured bucket alias
      (``PROOFSTUDIO_IMPORT_BUCKET_ALIAS``).
    - ``import_root`` is the canonical configured import root
      (``PROOFSTUDIO_IMPORT_ROOT``) and must byte-for-byte equal the
      authorization ``allowed_prefix`` for the controlled run.
    - ``bucket_identity`` is the raw bucket name (``B2_BUCKET``), used only to
      compute the SHA-256 comparison hash; never printed.
    - ``region`` is the configured region (``B2_REGION``); never printed.
    - ``required_credentials_present`` is a boolean summary of whether the
      secret credential environment variables are *present*. It is computed
      via membership checks only (``name in os.environ``); the values are
      never read at this layer.
    """

    alias: str
    import_root: str
    bucket_identity: str
    region: str
    required_credentials_present: bool


@dataclass(frozen=True)
class LiveCredentials:
    """Bearer for server-side B2 credential values.

    Carries only the values needed to construct the accepted
    ``S3StorageBackend.for_backblaze`` backend. Never printed, never serialized.
    Tests use a stub ``LiveCredentials`` whose values are inert strings.
    """

    key_id: str
    app_key: str
    bucket: str
    region: str


class CredentialProvider(Protocol):
    """Callable that returns ``LiveCredentials`` from the local environment.

    The executor calls this only after every non-network gate has passed.
    The provider must validate that the returned key id / app key are
    nonempty and raise ``AuthorizationError("credential_value_empty")``
    otherwise. It never prints the values.
    """

    call_count: int

    def __call__(self) -> LiveCredentials: ...


class BackendFactory(Protocol):
    """Callable that constructs a guarded backend from credentials.

    The executor calls this only after the credential provider returns. The
    returned backend must satisfy the accepted ``B2Backend`` Protocol. The
    factory must wrap the underlying backend in a :class:`GuardedLiveBackend`
    adapter; the adapter is the single point at which counters are kept and
    forbidden operations are blocked.
    """

    call_count: int

    def __call__(self, credentials: LiveCredentials) -> Any: ...


# ---------------------------------------------------------------------------
# Head-metadata normalization + canonical observation identity
# ---------------------------------------------------------------------------


def _normalize_last_modified(value: Any) -> str | None:
    """Normalize a ``last_modified`` value to a deterministic UTC ISO-8601
    string, or ``None`` when the value is absent.

    Accepts a ``datetime`` (as returned by the pinned genblaze-s3
    ``ObjectMetadata.last_modified``) or an ISO-8601 string. Naive
    datetimes are assumed UTC. The result uses the exact ``...Z`` suffix
    so identity comparisons are byte-for-byte stable across observations.
    Returns ``None`` for a ``None``/empty value so backends that do not
    expose ``last_modified`` are represented faithfully rather than
    fabricated. Malformed values reject with ``backend_head_failed``.
    """
    if value is None:
        return None
    if isinstance(value, _dt.datetime):
        dt = value
    elif isinstance(value, str):
        if value.strip() == "":
            return None
        try:
            dt = _dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            raise AuthorizationError("backend_head_failed")
    else:
        raise AuthorizationError("backend_head_failed")
    if not isinstance(dt, _dt.datetime):
        raise AuthorizationError("backend_head_failed")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=_dt.timezone.utc)
    return dt.astimezone(_dt.timezone.utc).isoformat().replace("+00:00", "Z")


def _observation_identity(meta: dict[str, Any] | None) -> tuple[Any, Any, Any, Any] | None:
    """Return the canonical observation identity for one head result.

    The identity is based ONLY on observed fields:

    ``(etag, size_bytes, version_id_or_none, last_modified_or_none)``

    - ``etag`` is the opaque ETag string;
    - ``size_bytes`` is the normalized declared size;
    - ``version_id_or_none`` is the version ID when the backend genuinely
      supplies one, or ``None`` when it does not (the pinned genblaze-s3
      ``ObjectMetadata`` does not expose ``version_id``);
    - ``last_modified_or_none`` is the deterministic UTC ISO-8601 string
      when the backend supplies ``last_modified``, or ``None``.

    Returns ``None`` when ``meta`` is ``None`` so callers can distinguish
    a missing object from a present one. Changes to any of these four
    fields between two observations reject with
    ``object_changed_during_evidence_run``.
    """
    if meta is None:
        return None
    return (
        meta.get("etag"),
        meta.get("size_bytes"),
        meta.get("version_id"),
        meta.get("last_modified_iso"),
    )


# ---------------------------------------------------------------------------
# Guarded live backend adapter (exact operation counters, get_range-only reads)
# ---------------------------------------------------------------------------


class GuardedLiveBackend:
    """Adapter that wraps any accepted backend and exposes the accepted
    ``B2Backend`` Protocol with exact operation counting and forbidden-method
    enforcement.

    Allowed operations (counted): ``head(key)``, ``read_bytes(key, max_bytes)``.
    Forbidden operations (counted then raised before any underlying call):
    ``list``, ``write``, ``delete``, ``signed_url``, ``provider_call``.

    The adapter enforces the corrected PS-041E2-B Phase-1 read contract:

    - **True exact-key read path.** When the inner backend is the accepted
      :class:`ExactKeyReadAdapter` (``proofstudio.provenance.genblaze_store``),
      the adapter dispatches every head to ``head_object`` and every bounded
      read to ``get_range`` on the exact-key adapter. The exact-key adapter
      issues ONLY low-level ``HeadObject`` and ranged ``GetObject`` calls
      through the pinned boto3 client and never runs the lazy bucket-region
      preflight, so the controlled read path produces exactly zero
      ``head_bucket`` calls and exactly zero regional-probe calls.
    - **No hidden HEAD inside ``read_bytes``.** The adapter never calls
      ``inner.head()`` / ``inner.head_object()`` from inside ``read_bytes``.
      The immediately preceding counted ``head()`` metadata is reused; if no
      preceding head exists the read rejects with ``backend_read_requires_preceding_head``.
    - **No full-object GET fallback.** When the inner backend does not expose
      a native ``read_bytes`` (i.e. it is the accepted S3 backend or the
      S3-like test fake), the adapter requires a ``get_range`` method. Absent
      ``get_range``, the read rejects with ``backend_get_range_unsupported``
      before any byte is read.
    - **Exact byte length.** The returned byte length must equal the declared
      approved size carried by the preceding head. Any mismatch rejects with
      ``media_length_mismatch``.
    - **No fabricated version_id; optional version_id.** The head
      normalization NEVER fabricates a ``version_id`` from ``storage_class``
      or a constant. The pinned genblaze-s3 ``ObjectMetadata`` (release
      ``c5f7a5ba`` / package ``genblaze-s3==0.3.5``) exposes ``key``,
      ``size``, ``last_modified``, ``etag``, ``content_type``,
      ``storage_class`` and ``metadata`` — it does NOT expose
      ``version_id``. ``_normalize_head`` accepts that shape and represents
      the absent version ID as ``None``. When a backend genuinely supplies
      a ``version_id`` (dictionary-based fakes, or a future backend that
      exposes it) the value is retained and participates in the canonical
      observation identity.

    When the underlying backend is the accepted ``S3StorageBackend`` wrapped
    by the :class:`ExactKeyReadAdapter`, the adapter maps the low-level
    response to the dict shape used by ``BoundedB2ImportReader`` and bounds
    ``read_bytes`` to ``max_bytes`` using the adapter's ``get_range``. When
    the underlying backend is the in-process ``FakeB2Backend`` (tests), the
    adapter delegates directly because the fake already exposes the
    dict/bytes contract.

    Forbidden operations always raise ``AuthorizationError`` so the normalized
    error channel surfaces only stable codes. The adapter never exposes raw
    exception text, bucket names, endpoints, or object keys through errors.

    Operation counters distinguish SDK calls from HTTP attempts:

    - ``head_object_sdk_calls`` / ``ranged_get_object_sdk_calls`` count SDK
      invocations (or local fake operations);
    - ``head_object_http_attempts`` / ``ranged_get_object_http_attempts``
      count actual attempts derived from successful Botocore retry metadata;
    - ``head_bucket_http_attempts`` and ``regional_probe_http_attempts`` are
      always 0 on the accepted controlled path;
    - ``list_calls``, ``write_attempts``, ``delete_attempts``,
      ``signed_url_attempts`` — always 0 (forbidden surface never exposed).
    """

    def __init__(self, inner: Any) -> None:
        self._inner = inner
        self.client_constructed = True
        # Canonical exact-key counters (the low-level request sequence).
        self.head_object_sdk_calls = 0
        self.ranged_get_object_sdk_calls = 0
        self.head_object_http_attempts = 0
        self.ranged_get_object_http_attempts = 0
        self.head_bucket_http_attempts = 0
        self.regional_probe_http_attempts = 0
        self.list_calls = 0
        self.write_attempts = 0
        self.delete_attempts = 0
        self.signed_url_attempts = 0
        self.provider_calls = 0
        self.total_bytes_read = 0
        # Backward-compat aliases (every head/read is an exact-key op on the
        # accepted path; these mirror the canonical counters).
        self.head_calls_total = 0
        self.read_calls_total = 0
        # Close-exactly-once state (PS-041E2-B Phase-1 correction).
        self.inner_close_attempted = False
        self.inner_close_succeeded = False
        self.inner_close_call_count = 0
        self._head_keys: list[str] = []
        self._read_keys: list[str] = []
        # Map of key -> (declared_size, max_bytes) carried by the most recent
        # counted head. ``read_bytes`` reuses this metadata so the adapter
        # never issues a hidden HEAD.
        self._head_metadata: dict[str, dict[str, Any]] = {}
        # Exact bytes served per key. Used by the executor to digest the exact
        # parsed bytes and to feed the security scan's raw-byte sentinel
        # detection. Cleared by :meth:`destroy` so no object bytes are
        # retained after cleanup.
        self.last_read_bytes: dict[str, bytes] = {}
        # Initialize counters from an exact-key adapter so the controlled
        # read path's zero-head-bucket / zero-probe guarantees are surfaced.
        self._sync_low_level_counters()

    # Compatibility aliases retained for accepted callers. These values are
    # SDK invocation counts (or local fake-operation counts), never HTTP
    # attempts. New evidence uses the explicit *_sdk_calls names.
    @property
    def head_object_calls(self) -> int:
        return self.head_object_sdk_calls

    @property
    def ranged_get_object_calls(self) -> int:
        return self.ranged_get_object_sdk_calls

    @property
    def head_bucket_calls(self) -> int:
        return self.head_bucket_http_attempts

    @property
    def regional_probe_calls(self) -> int:
        return self.regional_probe_http_attempts

    # ------------------------------------------------------------------
    # Exact-key adapter detection + low-level counter sync
    # ------------------------------------------------------------------

    @staticmethod
    def _is_exact_key_adapter(value: Any) -> bool:
        """Return True when ``value`` is the accepted ExactKeyReadAdapter.

        Detection is duck-typed: the adapter exposes ``head_object`` plus
        explicit SDK-call and no-preflight HTTP-attempt counters. In-process
        fakes and generic backends do not expose all three. This never
        imports ``genblaze_s3`` so test collection never constructs a real
        boto3 client.
        """
        return (
            value is not None
            and hasattr(value, "head_object")
            and hasattr(value, "head_bucket_http_attempts")
            and hasattr(value, "ranged_get_object_sdk_calls")
        )

    def _sync_low_level_counters(self) -> None:
        """Mirror the exact-key adapter's low-level counters onto this guard.

        On the accepted controlled path the adapter's HeadBucket and regional
        probe HTTP-attempt counters are always zero (the lazy preflight
        never runs). Mirroring them here keeps the guard's reported counters
        truthful: if a future change ever caused the adapter to record a
        non-zero head_bucket or probe count the guard would surface it
        rather than hiding it.
        """
        inner = self._inner
        if not self._is_exact_key_adapter(inner):
            return
        self.head_object_sdk_calls = int(getattr(inner, "head_object_sdk_calls", 0))
        self.ranged_get_object_sdk_calls = int(
            getattr(inner, "ranged_get_object_sdk_calls", 0)
        )
        self.head_object_http_attempts = int(
            getattr(inner, "head_object_http_attempts", 0)
        )
        self.ranged_get_object_http_attempts = int(
            getattr(inner, "ranged_get_object_http_attempts", 0)
        )
        self.head_bucket_http_attempts = int(
            getattr(inner, "head_bucket_http_attempts", 0)
        )
        self.regional_probe_http_attempts = int(
            getattr(inner, "regional_probe_http_attempts", 0)
        )
        if int(getattr(inner, "list_calls", 0)) > self.list_calls:
            self.list_calls = int(getattr(inner, "list_calls", 0))
        if int(getattr(inner, "write_attempts", 0)) > self.write_attempts:
            self.write_attempts = int(getattr(inner, "write_attempts", 0))
        if int(getattr(inner, "delete_attempts", 0)) > self.delete_attempts:
            self.delete_attempts = int(getattr(inner, "delete_attempts", 0))
        if int(getattr(inner, "signed_url_attempts", 0)) > self.signed_url_attempts:
            self.signed_url_attempts = int(getattr(inner, "signed_url_attempts", 0))

    # ------------------------------------------------------------------
    # Allowed operations
    # ------------------------------------------------------------------

    @staticmethod
    def _is_object_metadata(value: Any) -> bool:
        """Return True when ``value`` looks like a genblaze-s3
        ``ObjectMetadata`` dataclass instance.

        The pinned ``ObjectMetadata`` (genblaze-s3==0.3.5) always exposes
        ``size`` and ``etag``; it does NOT expose ``version_id``. This check
        is deliberately permissive on optional fields so a real
        ``ObjectMetadata`` is recognized without requiring ``version_id``.
        """
        return isinstance(value, object) and hasattr(value, "size") and hasattr(value, "etag")

    @staticmethod
    def _normalize_head_fields(
        *, size: Any, etag: Any, version_id: Any, last_modified: Any,
    ) -> dict[str, Any]:
        """Build the canonical normalized head dict from extracted fields.

        Produces exactly:

        ``{"size_bytes": int, "etag": str, "version_id": str | None,
           "last_modified_iso": str | None}``

        - ``size`` must be a non-negative ``int`` (``bool`` rejected);
        - ``etag`` must be a non-empty ``str`` (treated opaque);
        - ``version_id`` is ``None`` when absent / not a string; a non-empty
          ``str`` is retained as-is. Malformed types (e.g. a list) reject.
        - ``last_modified`` is normalized via :func:`_normalize_last_modified`.

        Malformed size / etag / timestamp reject safely with
        ``backend_head_failed``. No value is ever echoed in an error.
        """
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            raise AuthorizationError("backend_head_failed")
        if not isinstance(etag, str) or etag == "":
            raise AuthorizationError("backend_head_failed")
        if version_id is None:
            version_id_norm: str | None = None
        elif isinstance(version_id, str):
            version_id_norm = version_id if version_id != "" else None
        else:
            raise AuthorizationError("backend_head_failed")
        last_modified_iso = _normalize_last_modified(last_modified)
        return {
            "size_bytes": size,
            "etag": etag,
            "version_id": version_id_norm,
            "last_modified_iso": last_modified_iso,
        }

    def _normalize_head(self, raw: Any) -> dict[str, Any] | None:
        """Normalize one raw head result to the canonical dict shape.

        Accepts both dictionary backends (the in-process ``FakeB2Backend``)
        and genblaze-s3 ``ObjectMetadata`` instances. The pinned
        ``ObjectMetadata`` does NOT expose ``version_id``; that absence is
        represented as ``None`` — never fabricated. Dictionary-based fakes
        that genuinely supply a ``version_id`` continue to work.

        The canonical observation identity
        (see :func:`_observation_identity`) uses the four normalized fields
        so both shapes produce comparable identities.
        """
        if raw is None:
            return None
        if isinstance(raw, dict):
            # Accept either last_modified_iso (canonical) or last_modified.
            last_mod = raw.get("last_modified_iso")
            if last_mod is None:
                last_mod = raw.get("last_modified")
            return self._normalize_head_fields(
                size=raw.get("size_bytes"),
                etag=raw.get("etag"),
                version_id=raw.get("version_id"),
                last_modified=last_mod,
            )
        if self._is_object_metadata(raw):
            # The pinned ObjectMetadata exposes .size and .etag; .version_id
            # is absent (getattr returns None). .last_modified is a datetime.
            return self._normalize_head_fields(
                size=getattr(raw, "size", None),
                etag=getattr(raw, "etag", None),
                version_id=getattr(raw, "version_id", None),
                last_modified=getattr(raw, "last_modified", None),
            )
        raise AuthorizationError("backend_head_failed")

    def head(self, key: str) -> dict[str, Any] | None:
        self.head_calls_total += 1
        self._head_keys.append(key)
        if self._is_exact_key_adapter(self._inner):
            # Accepted exact-key adapter path: issue one low-level
            # HeadObject through the pinned boto3 client. The lazy
            # bucket-region preflight never runs, so this produces zero
            # head_bucket calls and zero regional probes.
            try:
                normalized = self._inner.head_object(key)
            except Exception as exc:
                self._sync_low_level_counters()
                raise AuthorizationError(self._map_exact_key_error(exc, "backend_head_failed"))
            self._sync_low_level_counters()
        else:
            # A fake/injected head represents one underlying fake operation.
            self.head_object_sdk_calls += 1
            try:
                raw = self._inner.head(key)
            except Exception:
                raise AuthorizationError("backend_head_failed")
            normalized = self._normalize_head(raw)
        if normalized is not None:
            # Carry the metadata so read_bytes can reuse it without issuing a
            # hidden HEAD on the underlying backend.
            self._head_metadata[key] = dict(normalized)
        return normalized

    def read_bytes(self, key: str, max_bytes: int) -> bytes:
        self.read_calls_total += 1
        self._read_keys.append(key)
        # Reuse the preceding counted head metadata; never issue a hidden HEAD.
        meta = self._head_metadata.get(key)
        if meta is None:
            raise AuthorizationError("backend_read_requires_preceding_head")
        declared = meta.get("size_bytes")
        if not isinstance(declared, int) or isinstance(declared, bool) or declared < 0:
            raise AuthorizationError("backend_head_failed")
        if declared > int(max_bytes):
            raise AuthorizationError("media_object_exceeds_approved_limit")
        if self._is_exact_key_adapter(self._inner):
            # Accepted exact-key adapter path: issue one ranged GetObject
            # through the pinned boto3 client. No full-object GET fallback.
            try:
                body = self._inner.get_range(key, offset=0, length=declared)
            except Exception as exc:
                self._sync_low_level_counters()
                raise AuthorizationError(self._map_exact_key_error(exc, "backend_read_failed"))
            self._sync_low_level_counters()
        elif hasattr(self._inner, "read_bytes"):
            # FakeB2Backend path: the fake already enforces bounds.
            self.ranged_get_object_sdk_calls += 1
            try:
                body = self._inner.read_bytes(key, max_bytes)
            except AuthorizationError:
                raise
            except OSError:
                raise AuthorizationError("backend_read_failed")
            except Exception:
                raise AuthorizationError("backend_read_failed")
        elif hasattr(self._inner, "get_range"):
            # Accepted S3-like fake path: bounded range read.
            self.ranged_get_object_sdk_calls += 1
            try:
                body = self._inner.get_range(key, offset=0, length=declared)
            except AuthorizationError:
                raise
            except OSError:
                raise AuthorizationError("backend_read_failed")
            except Exception:
                raise AuthorizationError("backend_read_failed")
        else:
            # No bounded-range support — fail before any byte is read.
            raise AuthorizationError("backend_get_range_unsupported")
        if not isinstance(body, (bytes, bytearray, memoryview)):
            raise AuthorizationError("backend_response_not_bytes")
        body_bytes = bytes(body)
        # Exact byte length must equal the declared approved size carried by
        # the preceding head. No truncation, no padding, no substitution.
        if len(body_bytes) != declared:
            raise AuthorizationError("media_length_mismatch")
        if len(body_bytes) > int(max_bytes):
            raise AuthorizationError("media_object_exceeds_approved_limit")
        self.total_bytes_read += len(body_bytes)
        self.last_read_bytes[key] = body_bytes
        return body_bytes

    @staticmethod
    def _map_exact_key_error(exc: Exception, default: str) -> str:
        """Map an :class:`ExactKeyReadError` (or any exception) to a stable
        ``AuthorizationError`` code.

        The raw exception text is NEVER carried. Only the stable code on the
        adapter's error (if present) or the provided default surfaces.
        """
        code = getattr(exc, "code", "") or ""
        if code in (
            "genblaze_s3_not_installed",
            "genblaze_s3_metadata_unavailable",
        ):
            return "genblaze_unavailable"
        if code == "genblaze_s3_version_mismatch":
            return "genblaze_version_mismatch"
        if code == "backend_attributes_unavailable":
            return "backend_attributes_unavailable"
        if code in (
            "head_response_retry_metadata_invalid",
            "get_object_response_retry_metadata_invalid",
            "get_object_response_invalid_shape",
            "get_object_content_length_invalid",
            "get_object_content_range_mismatch",
            "get_object_body_invalid",
            "get_object_body_read_failed",
            "get_object_body_close_failed",
            "get_object_response_not_bytes",
            "get_object_length_mismatch",
            "get_object_range_exceeded",
        ):
            return code
        return default

    # ------------------------------------------------------------------
    # Forbidden operations (counted then raised; underlying client never called)
    # ------------------------------------------------------------------

    def list(self, prefix: str, limit: int) -> list[dict[str, Any]]:
        self.list_calls += 1
        raise AuthorizationError("forbidden_list_attempted")

    def write(self, key: str, body: bytes) -> None:
        self.write_attempts += 1
        raise AuthorizationError("forbidden_write_attempted")

    def delete(self, key: str) -> None:
        self.delete_attempts += 1
        raise AuthorizationError("forbidden_delete_attempted")

    def signed_url(self, key: str) -> str:
        self.signed_url_attempts += 1
        raise AuthorizationError("forbidden_signed_url_attempted")

    def provider_call(self, *args: Any, **kwargs: Any) -> Any:
        self.provider_calls += 1
        raise AuthorizationError("forbidden_provider_call_attempted")

    def destroy(self) -> None:
        """Close the underlying client/backend exactly once, then drop it.

        Called by the executor cleanup step on every post-gate path. After
        this the adapter cannot be used for any further operation; subsequent
        calls are an idempotent no-op. The metadata cache is also cleared so
        no object-byte sentinel is retained.

        Close-exactly-once contract (PS-041E2-B Phase-1 correction):

        - when an underlying backend exists, its supported ``close()`` is
          called exactly once;
        - ``close()`` is called BEFORE the inner reference is cleared;
        - ``inner_close_attempted`` is True after the first ``destroy()``;
        - ``inner_close_succeeded`` is True only when close succeeded;
        - ``inner_close_call_count`` counts close attempts (0 before any
          destroy, 1 after a successful/failed first destroy, still 1 after
          a repeated idempotent destroy);
        - a close failure is normalized to ``AuthorizationError("backend_close_failed")``
          without exposing raw exception text — a close failure prevents
          final success-directory publication;
        - a backend lacking ``close()`` rejects with
          ``backend_close_unsupported``. The accepted in-process fake exposes
          an explicit close method even though it holds no persistent client,
          so there is no implicit class-name or attribute-shape exception;
        - repeated ``destroy()`` calls are idempotent (no double close).

        ``cleanup_verified`` may be True only when
        ``inner_close_succeeded`` is True.
        """
        if self._inner is None:
            # Idempotent: a repeated destroy() is a no-op.
            return
        self.inner_close_attempted = True
        self.inner_close_call_count += 1
        inner = self._inner
        close_method = getattr(inner, "close", None)
        if not callable(close_method):
            # Fail closed for every close-less backend. Accepted clientless
            # fakes expose an explicit no-op/counting close method instead of
            # relying on an unverifiable heuristic.
            self._inner = None
            self.client_constructed = False
            self._head_metadata.clear()
            self._head_keys.clear()
            self._read_keys.clear()
            self.last_read_bytes.clear()
            raise AuthorizationError("backend_close_unsupported")
        try:
            close_method()
        except Exception:
            # Close failed: clear the reference (so no retry re-attempts) and
            # raise a normalized error so finalization aborts. Raw exception
            # text never escapes.
            self._inner = None
            self.client_constructed = False
            self._head_metadata.clear()
            self._head_keys.clear()
            self._read_keys.clear()
            self.last_read_bytes.clear()
            raise AuthorizationError("backend_close_failed")
        self.inner_close_succeeded = True
        self._inner = None
        self.client_constructed = False
        self._head_metadata.clear()
        self._head_keys.clear()
        self._read_keys.clear()
        self.last_read_bytes.clear()


# ---------------------------------------------------------------------------
# Live execute report
# ---------------------------------------------------------------------------


@dataclass
class GateResult:
    index: int
    name: str
    ok: bool
    code: str = ""


@dataclass
class LiveExecuteReport:
    ok: bool
    evidence_run_id: str
    execution_commit: str
    configured_alias: str
    canonical_prefix: str
    gates: list[GateResult] = field(default_factory=list)
    alias_comparison_code: str = ""
    bucket_comparison_code: str = ""
    # PS-041E2-B Phase-1 independent server-binding evidence. The
    # ``import_root_matches_prefix`` flag is derived from the
    # independently observed ``authorized_prefix`` (auth.allowed_prefix)
    # and ``configured_import_root`` (server_config.import_root). It is
    # NEVER the result of comparing a value to itself.
    authorized_prefix: str = ""
    configured_import_root: str = ""
    import_root_comparison_code: str = ""
    import_root_matches_prefix: bool = False
    authorized_objects: int = 0
    head_calls_total: int = 0
    read_calls_total: int = 0
    # SDK invocations and actual HTTP attempts are distinct. Botocore may
    # perform multiple attempts for one invocation under adaptive retries.
    head_object_sdk_calls: int = 0
    ranged_get_object_sdk_calls: int = 0
    head_object_http_attempts: int = 0
    ranged_get_object_http_attempts: int = 0
    head_bucket_http_attempts: int = 0
    regional_probe_http_attempts: int = 0
    # Underlying client close-exactly-once evidence.
    inner_close_attempted: bool = False
    inner_close_succeeded: bool = False
    inner_close_call_count: int = 0
    unique_json_objects_read: int = 0
    unique_media_objects_read: int = 0
    snapshot_consumer_calls: int = 0
    list_calls: int = 0
    write_attempts: int = 0
    delete_attempts: int = 0
    signed_url_attempts: int = 0
    provider_calls: int = 0
    total_bytes_read: int = 0
    hash_results: list[dict[str, str]] = field(default_factory=list)
    observation_stable: bool = True
    observation_comparisons: int = 0
    import_created: bool = False
    import_idempotent: bool = False
    passport_schema: str = ""
    bundle_id: str = ""
    campaign_id: str = ""
    role_plan: dict[str, str] = field(default_factory=dict)
    normalized_b2_references: dict[str, dict[str, Any]] = field(default_factory=dict)
    approved_object_inventory: list[dict[str, Any]] = field(default_factory=list)
    private_lineage_summary: dict[str, Any] = field(default_factory=dict)
    private_passport_summary: dict[str, Any] = field(default_factory=dict)
    evidence_dir: str = ""
    cleanup_verified: bool = False
    security_scan: dict[str, Any] = field(default_factory=dict)
    # PS-041E2-B Phase-1: result of the strict post-write final scan. Retained
    # only in-memory; never written to an evidence file after the final scan.
    final_scan_clean: bool = False
    # ``live_b2_calls`` is zero for fake execution and is the exact sum of the
    # four actual HTTP-attempt counters for real execution.
    live_b2_calls: int = 0
    real_backend_factory_used: bool = False
    # PS-041E2-B Phase-1 service-result fields. ``import_service_used``
    # confirms the accepted PS-041D ProofStudioService was the import path.
    # ``private_lineage_readback`` / ``passport_readback`` confirm the
    # accepted private read boundary produced the stored bundle / passport.
    import_service_used: bool = False
    private_lineage_readback: bool = False
    passport_readback: bool = False
    remote_accepted_commit: str = ""
    errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Live execute flow (22 gates + 32-step operation order)
# ---------------------------------------------------------------------------


def _gate_record(idx: int, name: str, ok: bool, *, code: str = "") -> GateResult:
    return GateResult(index=idx, name=name, ok=bool(ok), code=code)


def _all_gates_passed(gates: list[GateResult]) -> bool:
    return bool(gates) and all(g.ok for g in gates)


# The exact two secret-value reads expected after gate completion. The order
# within the credential provider is B2_KEY_ID first, then B2_APP_KEY.
_EXPECTED_POST_GATE_SECRET_READS: tuple[str, ...] = ("B2_KEY_ID", "B2_APP_KEY")


def _evaluate_cleanup_secret_reads(
    env_access: "EnvAccessBoundary | None",
) -> dict[str, Any]:
    """Evaluate the secret-read cleanup contract from the env boundary.

    Returns explicit evidence fields:

    - ``pre_gate_secret_value_read_count`` — number of secret-value reads
      attempted before gate completion (MUST be zero);
    - ``post_gate_secret_value_read_count`` — number of secret-value reads
      after gate completion (MUST be exactly two);
    - ``post_gate_secret_names_match`` — True when the multiset of post-gate
      secret names equals exactly {B2_KEY_ID, B2_APP_KEY};
    - ``secret_read_order_valid`` — True when gates_completed preceded every
      secret-value read (no pre-gate reads);
    - ``cleanup_secret_reads_verified`` — True only when every success
      criterion holds.

    When ``env_access`` is None (fake/test path with no boundary), the
    contract is vacuously satisfied: there is no boundary to audit and the
    real CLI path always provides one.
    """
    if env_access is None:
        return {
            "no_pre_gate_secret_value_reads": True,
            "pre_gate_secret_value_read_count": 0,
            "post_gate_secret_value_read_count": 0,
            "post_gate_secret_names_match": True,
            "secret_read_order_valid": True,
            "cleanup_secret_reads_verified": True,
        }
    reads = list(env_access.secret_value_reads)
    before = [name for (name, phase) in reads if phase == "before_gates"]
    after = [name for (name, phase) in reads if phase == "after_gates"]
    pre_count = len(before)
    post_count = len(after)
    post_names_match = sorted(after) == sorted(_EXPECTED_POST_GATE_SECRET_READS)
    no_pre_gate = pre_count == 0
    exact_post_count = post_count == len(_EXPECTED_POST_GATE_SECRET_READS)
    gates_precede = bool(env_access.gates_completed) and no_pre_gate
    verified = (
        no_pre_gate
        and exact_post_count
        and post_names_match
        and gates_precede
    )
    return {
        "no_pre_gate_secret_value_reads": no_pre_gate,
        "pre_gate_secret_value_read_count": pre_count,
        "post_gate_secret_value_read_count": post_count,
        "post_gate_secret_names_match": post_names_match,
        "secret_read_order_valid": gates_precede,
        "cleanup_secret_reads_verified": verified,
    }


def _normalized_b2_reference(
    key: str, role: str, alias: str, *,
    expected_sha256: str | None, observed: dict[str, Any] | None,
) -> dict[str, Any]:
    """Build a sanitized B2 reference summary for evidence output.

    Carries only the alias (never the raw bucket name), the exact object key,
    the role, and the bounded metadata tuple observed by ``head()``. No
    credential, no signed URL, no endpoint URL.

    ``version_id_observed`` is False when the backend did not supply a
    version ID (the pinned genblaze-s3 ``ObjectMetadata`` shape); the
    evidence never implies version verification when the backend did not
    observe one.
    """
    ref: dict[str, Any] = {
        "backend": "b2_s3",
        "bucket_alias": alias,
        "object_key": key,
        "role": role,
    }
    if expected_sha256 is not None:
        ref["expected_sha256"] = expected_sha256
    if observed is not None:
        ref["size_bytes"] = observed.get("size_bytes")
        ref["etag"] = observed.get("etag")
        version_id = observed.get("version_id")
        ref["version_id"] = version_id
        ref["version_id_observed"] = version_id is not None
        ref["last_modified_iso"] = observed.get("last_modified_iso")
    return ref


def _approved_object_inventory_entry(
    key: str, role: str, observed: dict[str, Any] | None,
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "object_key": key,
        "role": role,
    }
    if observed is not None:
        entry["size_bytes"] = observed.get("size_bytes")
        entry["etag"] = observed.get("etag")
        version_id = observed.get("version_id")
        entry["version_id"] = version_id
        entry["version_id_observed"] = version_id is not None
        entry["last_modified_iso"] = observed.get("last_modified_iso")
    return entry


def run_live_execute(
    auth: dict[str, Any],
    *,
    fixture_path: Path,
    evidence_dir: Path,
    git_state: GitState,
    server_config: ServerConfig,
    credential_provider: CredentialProvider,
    backend_factory: BackendFactory,
    import_service: Any,
    remote_ref_resolver: RemoteRefResolver,
    confirm_controlled_live_read: bool = False,
    real_backend_factory_used: bool = False,
    env_access: "EnvAccessBoundary | None" = None,
    now: _dt.datetime | None = None,
) -> LiveExecuteReport:
    """Run the full controlled live execute flow.

    Implements all 22 gates before constructing the guarded backend, then
    performs the exact 12-step atomic finalization order. Gates 1-20 are
    pure and non-networking. Gate 21 performs exactly one bounded Git
    remote-ref lookup (``git ls-remote`` for the current
    ``refs/heads/accepted/proofstudio``); tests inject the remote resolver
    and perform no network. Gate 22 is the explicit confirmation flag.

    The flow is fully injectable: tests pass a ``FakeB2Backend``-returning
    backend factory, a fake git/server/credential provider, a fake
    ``remote_ref_resolver`` and a fresh in-process ``ProofStudioService``
    import_service. The real CLI path wires ``git`` subprocess output, the
    bounded ``git ls-remote`` resolver, explicit environment-derived server
    configuration, a credential provider that reads only the established
    server-side environment variables, the accepted
    ``S3StorageBackend.for_backblaze`` backend factory, and a real
    ``ProofStudioService`` instance.

    No B2 credential value is read before every authorization and Git
    binding check passes. No B2 client is constructed before all 22 gates
    pass. No backend
    is constructed before all 22 gates pass. No list / write /
    delete / signed-URL / provider method is invoked at any point. Cleanup is
    guaranteed on every post-gate path: after the credential provider has
    been called, every outcome destroys the backend, releases inner
    backend/client references and credential references, and securely
    removes any incomplete partial output directory (never renamed to
    ``.quarantine-*``). The final run
    directory does not exist until the atomic rename succeeds as the last
    operation.
    """
    now = now or _utc_now()
    gates: list[GateResult] = []
    evidence_run_id = auth["evidence_run_id"]
    execution_commit = auth["execution_commit"].lower()
    configured_alias = auth["configured_alias"]
    canonical_prefix = auth["allowed_prefix"]
    allowed_keys: list[str] = list(auth["allowed_keys"])
    expected_sha256_by_key: dict[str, str] = dict(auth.get("expected_sha256_by_key", {}))
    object_role_by_key: dict[str, str] = dict(auth["object_role_by_key"])

    # Independent server-binding observation: derived from the authorized
    # prefix (auth.allowed_prefix) and the configured import root
    # (server_config.import_root). Computed here so the failure-path
    # report carries the comparison result regardless of which gate
    # rejects. NEVER the result of comparing a value to itself.
    import_root_matches_prefix = canonical_prefix == server_config.import_root
    import_root_comparison_code = (
        "prefix_import_root_match" if import_root_matches_prefix
        else "prefix_import_root_mismatch"
    )

    credential_provider_called = {"before_gates": False}
    backend_factory_called = {"before_gates": False}

    def _guarded_credential_provider() -> LiveCredentials:
        if not _all_gates_passed(gates):
            credential_provider_called["before_gates"] = True
            raise AuthorizationError("credential_provider_called_before_gates")
        return credential_provider()

    def _guarded_backend_factory(credentials: LiveCredentials) -> Any:
        if not _all_gates_passed(gates):
            backend_factory_called["before_gates"] = True
            raise AuthorizationError("backend_factory_called_before_gates")
        return backend_factory(credentials)

    # ------------------------------------------------------------------
    # Pure validation gates (no network, no credential access).
    # ------------------------------------------------------------------
    try:
        gates.append(_gate_record(1, FUTURE_EXECUTE_GATES[0], True))
        validate_live_authorization(auth)
        for i in range(1, 5):
            gates.append(_gate_record(i + 1, FUTURE_EXECUTE_GATES[i], True))

        alias_cmp = compare_server_alias(configured_alias, server_config.alias)
        if not alias_cmp.match:
            gates.append(_gate_record(6, FUTURE_EXECUTE_GATES[5], False, code=alias_cmp.code))
            raise AuthorizationError(alias_cmp.code)
        gates.append(_gate_record(6, FUTURE_EXECUTE_GATES[5], True))
        bucket_cmp = compare_bucket_identity(
            auth["allowed_bucket_name_hash"], server_config.bucket_identity,
        )
        if not bucket_cmp.match:
            gates.append(_gate_record(7, FUTURE_EXECUTE_GATES[6], False, code=bucket_cmp.code))
            raise AuthorizationError(bucket_cmp.code)
        gates.append(_gate_record(7, FUTURE_EXECUTE_GATES[6], True))

        # Gate 8 — exact canonical prefix match against the independently
        # configured import root. Byte-for-byte equality; no normalization.
        # The independent comparison result is computed before the try
        # block so the failure-path report carries it too. See the
        # ``import_root_matches_prefix`` assignment above.
        if not import_root_matches_prefix:
            gates.append(_gate_record(8, FUTURE_EXECUTE_GATES[7], False,
                                       code="prefix_import_root_mismatch"))
            raise AuthorizationError("prefix_import_root_mismatch")
        gates.append(_gate_record(8, FUTURE_EXECUTE_GATES[7], True))

        for i in range(8, 16):
            gates.append(_gate_record(i + 1, FUTURE_EXECUTE_GATES[i], True))

        # Gate 17 — required explicit server-side B2 configuration present.
        # All four fields (alias, import_root, bucket_identity, region) must
        # be nonempty, AND the secret credential env vars must be present
        # (membership-only check; values are never read at this layer).
        config_present = bool(
            server_config.alias
            and server_config.import_root
            and server_config.bucket_identity
            and server_config.region
        )
        if not config_present or not server_config.required_credentials_present:
            gates.append(_gate_record(17, FUTURE_EXECUTE_GATES[16], False,
                                       code="server_side_configuration_missing"))
            raise AuthorizationError("server_side_configuration_missing")
        gates.append(_gate_record(17, FUTURE_EXECUTE_GATES[16], True))

        gates.append(_gate_record(18, FUTURE_EXECUTE_GATES[17], True))
        gates.append(_gate_record(19, FUTURE_EXECUTE_GATES[18], True))

        if not git_state.tree_clean:
            gates.append(_gate_record(20, FUTURE_EXECUTE_GATES[19], False,
                                       code="repository_tree_dirty"))
            raise AuthorizationError("repository_tree_dirty")
        gates.append(_gate_record(20, FUTURE_EXECUTE_GATES[19], True))

        # Gate 21 — branch, HEAD, local accepted ref and *remote* accepted
        # ref must all agree. The remote ref is resolved here (bounded,
        # fail-closed); no credential may be read before this passes.
        if git_state.head_commit.lower() != execution_commit:
            gates.append(_gate_record(21, FUTURE_EXECUTE_GATES[20], False,
                                       code="execution_commit_mismatch"))
            raise AuthorizationError("execution_commit_mismatch")
        if git_state.head_commit.lower() != git_state.accepted_commit.lower():
            gates.append(_gate_record(21, FUTURE_EXECUTE_GATES[20], False,
                                       code="head_not_accepted"))
            raise AuthorizationError("head_not_accepted")
        if git_state.accepted_ref != ACCEPTED_EXECUTION_REF:
            gates.append(_gate_record(21, FUTURE_EXECUTE_GATES[20], False,
                                       code="accepted_ref_mismatch"))
            raise AuthorizationError("accepted_ref_mismatch")
        if git_state.branch != PS_041E2B_BRANCH and git_state.branch != "(detached)":
            gates.append(_gate_record(21, FUTURE_EXECUTE_GATES[20], False,
                                       code="branch_not_implementation_branch"))
            raise AuthorizationError("branch_not_implementation_branch")
        # Resolve the remote accepted ref. This is the binding that closes
        # the stale-local-ref loophole. The resolver fails closed (returns
        # empty string) when the remote cannot be reached.
        remote_accepted_commit = remote_ref_resolver(ACCEPTED_EXECUTION_REF)
        if not remote_accepted_commit:
            gates.append(_gate_record(21, FUTURE_EXECUTE_GATES[20], False,
                                       code="remote_accepted_ref_unreachable"))
            raise AuthorizationError("remote_accepted_ref_unreachable")
        if not _HEX40.match(remote_accepted_commit):
            gates.append(_gate_record(21, FUTURE_EXECUTE_GATES[20], False,
                                       code="remote_accepted_ref_malformed"))
            raise AuthorizationError("remote_accepted_ref_malformed")
        if remote_accepted_commit.lower() != git_state.head_commit.lower():
            gates.append(_gate_record(21, FUTURE_EXECUTE_GATES[20], False,
                                       code="remote_accepted_ref_mismatch"))
            raise AuthorizationError("remote_accepted_ref_mismatch")
        gates.append(_gate_record(21, FUTURE_EXECUTE_GATES[20], True))

        if not confirm_controlled_live_read:
            gates.append(_gate_record(22, FUTURE_EXECUTE_GATES[21], False,
                                       code="confirm_controlled_live_read_missing"))
            raise AuthorizationError("confirm_controlled_live_read_missing")
        gates.append(_gate_record(22, FUTURE_EXECUTE_GATES[21], True))

        # All 22 gates passed. Mark the env-access boundary so the
        # CredentialProvider may now read secret values. The boundary
        # raises immediately on any secret-value read attempted before
        # this point (defensive belt-and-braces).
        if env_access is not None:
            env_access.mark_gates_completed()

        # ------------------------------------------------------------------
        # Post-gate: credential retrieval + backend construction + work.
        # Everything below is wrapped in try/finally so cleanup is guaranteed
        # on every path. ``partial_dir`` is the validated partial output
        # directory; ``final_dir`` is the rename target. The final directory
        # must not exist until every success artifact is complete.
        # ------------------------------------------------------------------
        credentials: LiveCredentials | None = None
        inner_backend: Any = None
        backend: GuardedLiveBackend | None = None
        partial_dir: Path | None = None
        final_dir: Path | None = None
        unverified_published_dir: Path | None = None
        object_byte_sentinels: list[bytes] = []
        # Exact credential values captured for the minimum scan interval.
        # These locals are blanked immediately after the security scan
        # completes; they are never serialized, never printed, and never
        # written to disk.
        scan_key_id = ""
        scan_app_key = ""
        sensitive_ctx: "SensitiveScanContext | None" = None
        try:
            credentials = _guarded_credential_provider()
            if not credentials.key_id or not credentials.app_key:
                raise AuthorizationError("credential_value_empty")
            if not credentials.bucket or not credentials.region:
                raise AuthorizationError("credential_value_empty")
            # Capture exact credential values for the fail-closed scan.
            # Held for the minimum scan interval only.
            scan_key_id = credentials.key_id
            scan_app_key = credentials.app_key
            inner_backend = _guarded_backend_factory(credentials)
            backend = (
                inner_backend if isinstance(inner_backend, GuardedLiveBackend)
                else GuardedLiveBackend(inner_backend)
            )

            reader_config = B2ImportReaderConfig(
                enabled=True,
                bucket_alias=configured_alias,
                root_prefix=canonical_prefix,
                max_listed_objects=min(auth["max_object_count"], ACCEPTED_MAX_OBJECT_COUNT),
                max_json_bytes=min(auth["max_object_bytes"], ACCEPTED_MAX_JSON_OBJECT_BYTES),
                max_asset_bytes=min(auth["max_object_bytes"], ACCEPTED_MAX_MEDIA_OBJECT_BYTES),
                max_aggregate_bytes=min(auth["max_total_bytes"], ACCEPTED_MAX_AGGREGATE_BYTES),
            )
            reader = BoundedB2ImportReader(backend, reader_config)

            auth_per_object_cap = min(auth["max_object_bytes"], ACCEPTED_MAX_MEDIA_OBJECT_BYTES)
            auth_total_cap = min(auth["max_total_bytes"], ACCEPTED_MAX_AGGREGATE_BYTES)
            initial_observation: dict[str, tuple[Any, Any, Any]] = {}
            total_declared_size = 0
            approved_inventory: list[dict[str, Any]] = []
            normalized_refs: dict[str, dict[str, Any]] = {}
            for key in allowed_keys:
                try:
                    meta = backend.head(key)
                except AuthorizationError:
                    raise
                except Exception:
                    raise AuthorizationError("backend_head_failed")
                if meta is None:
                    raise AuthorizationError("approved_object_missing")
                _require_object_metadata(meta)
                size_value = meta.get("size_bytes")
                validated_size = _require_object_size_bytes(
                    size_value,
                    auth_cap=auth_per_object_cap,
                    accepted_cap=ACCEPTED_MAX_MEDIA_OBJECT_BYTES,
                )
                total_declared_size += validated_size
                initial_observation[key] = _observation_identity(meta)
                role = object_role_by_key[key]
                approved_inventory.append(_approved_object_inventory_entry(
                    key, role, {"size_bytes": validated_size,
                                "etag": meta.get("etag"),
                                "version_id": meta.get("version_id"),
                                "last_modified_iso": meta.get("last_modified_iso")},
                ))
                normalized_refs[key] = _normalized_b2_reference(
                    key, role, configured_alias,
                    expected_sha256=expected_sha256_by_key.get(key),
                    observed={"size_bytes": validated_size,
                              "etag": meta.get("etag"),
                              "version_id": meta.get("version_id"),
                              "last_modified_iso": meta.get("last_modified_iso")},
                )

            if total_declared_size > auth_total_cap:
                raise AuthorizationError("declared_inventory_exceeds_authorization_total")
            if total_declared_size > ACCEPTED_MAX_AGGREGATE_BYTES:
                raise AuthorizationError("declared_inventory_exceeds_accepted_total")

            snapshot_store = SnapshotStore(allowed_keys=set(allowed_keys))
            hash_results: list[dict[str, str]] = []
            consumed_expected: set[str] = set()
            role_to_key = resolve_role_to_key(object_role_by_key)
            json_role_order = (
                ROLE_STAGE_A_STORYBOARD, ROLE_STAGE_B0_MANIFEST,
                ROLE_STAGE_B1_MANIFEST, ROLE_STAGE_B2_MANIFEST,
            )
            json_keys_in_plan: list[str] = []
            for role in json_role_order:
                key = role_to_key[role]
                json_keys_in_plan.append(key)
                expected = expected_sha256_by_key.get(key)
                ref = B2ObjectReference(
                    backend="b2_s3", bucket_alias=configured_alias, object_key=key,
                    sha256=expected,
                )
                try:
                    parsed = reader.read_json(ref)
                except ImportValidationError as exc:
                    raise AuthorizationError(_normalize_import_error(exc))
                observed_bytes = backend.last_read_bytes.get(key, b"")
                object_byte_sentinels.append(bytes(observed_bytes))
                digest = hashlib.sha256(observed_bytes).hexdigest()
                if expected is not None:
                    if hmac.compare_digest(digest, expected):
                        hash_results.append({"key": key, "role": role, "status": "matched", "sha256": digest})
                        consumed_expected.add(key)
                    else:
                        hash_results.append({"key": key, "role": role, "status": "mismatch", "sha256": digest})
                        raise AuthorizationError("unexpected_hash_mismatch")
                else:
                    hash_results.append({"key": key, "role": role, "status": "observed", "sha256": digest})
                snapshot_store.put(ValidatedSnapshot(key=key, role=role, parsed=parsed, bytes_sha256=digest))

            allow_media = bool(auth["allow_media_byte_reads"])
            media_keys_read: list[str] = []
            aggregate_used = backend.total_bytes_read
            for key in allowed_keys:
                role = object_role_by_key[key]
                if role not in MEDIA_BYTE_ROLES:
                    continue
                if not allow_media:
                    continue
                body, digest, aggregate_used = _bounded_asset_read(
                    backend, key,
                    auth_max_object_bytes=min(auth["max_object_bytes"], ACCEPTED_MAX_MEDIA_OBJECT_BYTES),
                    accepted_max_bytes=ACCEPTED_MAX_MEDIA_OBJECT_BYTES,
                    aggregate_budget=min(auth["max_total_bytes"], ACCEPTED_MAX_AGGREGATE_BYTES),
                    aggregate_used=aggregate_used,
                )
                object_byte_sentinels.append(bytes(body))
                media_keys_read.append(key)
                expected = expected_sha256_by_key.get(key)
                if expected is not None:
                    if hmac.compare_digest(digest, expected):
                        hash_results.append({"key": key, "role": role, "status": "matched", "sha256": digest})
                        consumed_expected.add(key)
                    else:
                        hash_results.append({"key": key, "role": role, "status": "mismatch", "sha256": digest})
                        raise AuthorizationError("unexpected_hash_mismatch")
                else:
                    hash_results.append({"key": key, "role": role, "status": "computed", "sha256": digest})

            if not allow_media:
                for key in allowed_keys:
                    role = object_role_by_key[key]
                    if role in MEDIA_BYTE_ROLES and key in expected_sha256_by_key:
                        raise AuthorizationError("expected_media_hash_requires_media_reads")

            unconsumed = set(expected_sha256_by_key) - consumed_expected
            if unconsumed:
                raise AuthorizationError("expected_hash_unconsumed")

            # Build the bundle request once; the import service consumes it.
            bundle_request = _build_b2_bundle_request(
                json.loads(fixture_path.read_text(encoding="utf-8")),
                role_to_key=role_to_key,
                configured_alias=configured_alias,
                expected_sha256_by_key=expected_sha256_by_key,
            )

            def _guarded_reader(ref: B2ObjectReference) -> dict[str, Any]:
                return snapshot_store.consume(ref.object_key)

            # ------------------------------------------------------------------
            # Section 11 — accepted import + readback service.
            # Construct the candidate through the accepted PS-041D
            # ``ProofStudioService.import_genblaze_bundle`` so the
            # created/idempotent result is the real service result, never
            # hard-coded. Re-import through the same service to prove
            # idempotency. Read the stored private lineage bundle through
            # ``get_imported_bundle`` and the portable Passport through
            # ``get_imported_passport``.
            # ------------------------------------------------------------------
            campaign_envelope = import_service.create_campaign({
                "name": f"PS-041E2-B controlled evidence run {evidence_run_id}",
                "brief": (
                    "Process-local campaign created by the PS-041E2-B live "
                    "executor to host the controlled evidence import. Not a "
                    "real product campaign."
                ),
            })
            campaign_id = campaign_envelope["campaign_id"]
            import_first = import_service.import_genblaze_bundle(
                campaign_id, bundle_request, b2_json_reader=_guarded_reader,
            )
            import_again = import_service.import_genblaze_bundle(
                campaign_id, bundle_request, b2_json_reader=_guarded_reader,
            )
            bundle_id = import_first.bundle.bundle_id
            import_created = bool(import_first.created)
            import_idempotent = (
                not import_again.created
                and import_first.bundle.bundle_id == import_again.bundle.bundle_id
                and import_first.bundle.bundle_fingerprint
                    == import_again.bundle.bundle_fingerprint
            )
            # Private readback through the accepted service/store boundary.
            private_readback = import_service.get_imported_bundle(campaign_id, bundle_id)
            private_lineage_summary = {
                "bundle_id": private_readback.bundle.bundle_id,
                "bundle_fingerprint": private_readback.bundle.bundle_fingerprint,
                "node_count": len(private_readback.nodes),
                "edge_count": len(private_readback.edges),
                "readback_via": "ProofStudioService.get_imported_bundle",
            }
            passport_readback = import_service.get_imported_passport(campaign_id, bundle_id)
            private_passport_summary = {
                "passport_schema": passport_readback.passport_schema,
                "bundle_id": passport_readback.bundle_id,
                "readback_via": "ProofStudioService.get_imported_passport",
            }
            private_lineage_readback = True
            passport_readback_ok = True
            import_service_used = True

            # Final observation: HEAD all exact allowlisted objects again.
            observation_comparisons = 0
            for key in allowed_keys:
                try:
                    meta = backend.head(key)
                except AuthorizationError:
                    raise
                except Exception:
                    raise AuthorizationError("backend_head_failed")
                if meta is None:
                    raise AuthorizationError("object_changed_during_evidence_run")
                _require_object_metadata(meta)
                final = _observation_identity(meta)
                if initial_observation[key] != final:
                    raise AuthorizationError("object_changed_during_evidence_run")
                observation_comparisons += 1

            live_b2_calls = (
                (
                    backend.head_object_http_attempts
                    + backend.ranged_get_object_http_attempts
                    + backend.head_bucket_http_attempts
                    + backend.regional_probe_http_attempts
                )
                if real_backend_factory_used else 0
            )
            report_proto = LiveExecuteReport(
                ok=True,
                evidence_run_id=evidence_run_id,
                execution_commit=execution_commit,
                configured_alias=configured_alias,
                canonical_prefix=canonical_prefix,
                gates=list(gates),
                alias_comparison_code=alias_cmp.code,
                bucket_comparison_code=bucket_cmp.code,
                authorized_prefix=canonical_prefix,
                configured_import_root=server_config.import_root,
                import_root_comparison_code=import_root_comparison_code,
                import_root_matches_prefix=import_root_matches_prefix,
                authorized_objects=len(allowed_keys),
                head_calls_total=backend.head_calls_total,
                read_calls_total=backend.read_calls_total,
                head_object_sdk_calls=backend.head_object_sdk_calls,
                ranged_get_object_sdk_calls=backend.ranged_get_object_sdk_calls,
                head_object_http_attempts=backend.head_object_http_attempts,
                ranged_get_object_http_attempts=backend.ranged_get_object_http_attempts,
                head_bucket_http_attempts=backend.head_bucket_http_attempts,
                regional_probe_http_attempts=backend.regional_probe_http_attempts,
                unique_json_objects_read=len(json_keys_in_plan),
                unique_media_objects_read=len(media_keys_read),
                snapshot_consumer_calls=snapshot_store.consumer_calls,
                list_calls=backend.list_calls,
                write_attempts=backend.write_attempts,
                delete_attempts=backend.delete_attempts,
                signed_url_attempts=backend.signed_url_attempts,
                provider_calls=backend.provider_calls,
                total_bytes_read=backend.total_bytes_read,
                hash_results=hash_results,
                observation_stable=True,
                observation_comparisons=observation_comparisons,
                import_created=import_created,
                import_idempotent=import_idempotent,
                passport_schema=passport_readback.passport_schema,
                bundle_id=bundle_id,
                campaign_id=campaign_id,
                role_plan=object_role_by_key,
                normalized_b2_references=normalized_refs,
                approved_object_inventory=approved_inventory,
                private_lineage_summary=private_lineage_summary,
                private_passport_summary=private_passport_summary,
                cleanup_verified=False,
                live_b2_calls=live_b2_calls,
                real_backend_factory_used=real_backend_factory_used,
                import_service_used=import_service_used,
                private_lineage_readback=private_lineage_readback,
                passport_readback=passport_readback_ok,
                remote_accepted_commit=remote_accepted_commit,
            )

            # ------------------------------------------------------------------
            # Atomic finalization. The final directory must not exist until
            # every success artifact is complete AND the strict final scan
            # has passed over the exact finalized bytes. The canonical order:
            #
            #   1.  Create the controlled partial directory.
            #   2.  Write provisional evidence.
            #   3.  Destroy backend/client and release credentials.
            #   4.  Complete cleanup-verification.txt (never rewritten).
            #   5.  Run the initial classified scan.
            #   6.  Write classified-security-scan.txt + known-limitations.txt.
            #   7.  Set cleanup_verified=true on the in-memory report.
            #   8.  Rewrite authorization-summary.json + execution-summary.json.
            #   9.  (Every remaining final artifact is now on disk.)
            #   10. Verify the exact 20-file set + regular non-symlink status.
            #   11. Run the strict final scan over all exact finalized bytes.
            #   12. Make NO further file-content change.
            #   13. Atomically rename partial to final immediately.
            #
            # No evidence file is modified after the final scan. The final
            # scan result is retained only in the in-memory LiveExecuteReport.
            # ------------------------------------------------------------------
            partial_dir, final_dir = _create_partial_dir(
                evidence_dir, evidence_run_id,
            )

            # Step 2 — write every provisional evidence artifact. The
            # summaries carry cleanup_verified=False here and are rewritten
            # at step 8 before the final scan.
            _write_provisional_evidence(
                partial_dir, report_proto,
                git_state=git_state, gates=gates,
            )

            # Step 3 — destroy backend/client references and release
            # credential references. This runs before the security scan so
            # the scan can prove no retained client/credential state exists.
            # The exact credential values captured for the scan are held
            # only for the minimum scan interval and dropped immediately
            # after the final scan completes.
            #
            # The underlying client is closed EXACTLY ONCE here. The close
            # state (inner_close_attempted / inner_close_succeeded /
            # inner_close_call_count) is captured before the local backend
            # reference is dropped so the evidence can prove the close
            # succeeded. ``cleanup_verified`` may be True only when close
            # succeeded; a close failure raises ``backend_close_failed`` and
            # prevents final success-directory publication.
            backend.destroy()
            inner_close_attempted = backend.inner_close_attempted
            inner_close_succeeded = backend.inner_close_succeeded
            inner_close_call_count = backend.inner_close_call_count
            backend = None
            inner_backend = None
            credentials_released = credentials is not None
            credentials = None

            # Step 4 — evaluate the secret-read cleanup contract and complete
            # cleanup-verification.txt. This file is completed here and NEVER
            # rewritten. If the secret-read contract is unverified, the run
            # fails before any scan runs.
            cleanup_secret = _evaluate_cleanup_secret_reads(env_access)
            if not cleanup_secret["cleanup_secret_reads_verified"]:
                leak_partial = partial_dir
                partial_dir = None
                scan_key_id = ""
                scan_app_key = ""
                _secure_remove_partial(leak_partial)
                _write_sanitized_failure_summary(
                    evidence_dir, evidence_run_id,
                    error_code="cleanup_secret_reads_unverified",
                )
                raise AuthorizationError("cleanup_secret_reads_unverified")
            cleanup_path = partial_dir / "cleanup-verification.txt"
            _track_evidence_write(cleanup_path)
            cleanup_path.write_text(
                _format_cleanup_verification(
                    backend_destroyed=True,
                    credentials_released=credentials_released,
                    cleanup_secret=cleanup_secret,
                ),
                encoding="utf-8",
            )

            # Step 5 — initial classified scan over the partial directory.
            # The scan compares every evidence file against the EXACT
            # in-memory credential values, the raw bucket identity, and the
            # object-byte sentinels. Bare credential values are detected
            # even without a credential-like field name.
            sensitive_ctx = SensitiveScanContext(
                key_id=scan_key_id,
                app_key=scan_app_key,
                bucket_identity=server_config.bucket_identity,
                object_byte_sentinels=tuple(object_byte_sentinels),
            )
            scan = _security_scan_directory(
                partial_dir,
                secret_values=_collect_secret_values(
                    object_byte_sentinels=object_byte_sentinels,
                    bucket_identity=server_config.bucket_identity,
                    key_id=scan_key_id,
                    app_key=scan_app_key,
                ),
                bucket_identity=server_config.bucket_identity,
                sensitive=sensitive_ctx,
                expected_files=(
                    frozenset(LIVE_EVIDENCE_FILES)
                    - frozenset((
                        "classified-security-scan.txt",
                        "known-limitations.txt",
                    ))
                ),
            )
            if scan["real_value_leak_count"] > 0:
                leak_partial = partial_dir
                partial_dir = None
                sensitive_ctx.drop()
                sensitive_ctx = None
                scan_key_id = ""
                scan_app_key = ""
                _secure_remove_partial(leak_partial)
                _write_sanitized_failure_summary(
                    evidence_dir, evidence_run_id,
                    error_code="evidence_secret_value_leak",
                )
                raise AuthorizationError("evidence_secret_value_leak")

            # Step 6 — write classified-security-scan.txt + known-limitations.txt.
            # The classified scan artifact may state that the pre-final scan
            # passed and that it is covered by the subsequent post-write final
            # scan (step 11).
            report_proto.security_scan = scan
            _write_security_scan(partial_dir, scan)
            _write_known_limitations(partial_dir)

            # Step 7 — set cleanup_verified=true on the in-memory report so
            # the summaries rewritten at step 8 carry the verified flag.
            # cleanup_verified may be True only when the underlying client
            # close succeeded (a close failure raised at step 3 already
            # aborted the run before reaching here).
            report_proto.inner_close_attempted = inner_close_attempted
            report_proto.inner_close_succeeded = inner_close_succeeded
            report_proto.inner_close_call_count = inner_close_call_count
            report_proto.cleanup_verified = bool(
                inner_close_succeeded and inner_close_attempted
            )

            # Step 8 — rewrite authorization-summary.json and
            # execution-summary.json with cleanup_verified=true. These are
            # the LAST content writes before the final scan.
            _rewrite_summary_files(partial_dir, report_proto, git_state, gates)

            # Step 9 — every remaining final artifact is now on disk. No
            # further content write occurs after this point.

            # Step 10 — verify the exact 20-file set + regular non-symlink
            # status before the final scan.
            _verify_evidence_files_complete(partial_dir)

            # Step 11 — strict final security scan over ALL exact finalized
            # bytes. This scan covers every byte that will be in the final
            # directory, including the rewritten summaries, the
            # classified-security-scan artifact, and known-limitations.txt.
            # No evidence file is modified after this scan.
            _mark_final_scan_started()
            final_scan = _security_scan_directory(
                partial_dir,
                secret_values=_collect_secret_values(
                    object_byte_sentinels=object_byte_sentinels,
                    bucket_identity=server_config.bucket_identity,
                    key_id=scan_key_id,
                    app_key=scan_app_key,
                ),
                bucket_identity=server_config.bucket_identity,
                sensitive=sensitive_ctx,
                expected_files=frozenset(LIVE_EVIDENCE_FILES),
            )
            if final_scan["real_value_leak_count"] > 0:
                leak_partial = partial_dir
                partial_dir = None
                if sensitive_ctx is not None:
                    sensitive_ctx.drop()
                sensitive_ctx = None
                scan_key_id = ""
                scan_app_key = ""
                _mark_final_scan_aborted()
                _secure_remove_partial(leak_partial)
                _write_sanitized_failure_summary(
                    evidence_dir, evidence_run_id,
                    error_code="evidence_secret_value_leak",
                )
                raise AuthorizationError("evidence_secret_value_leak")

            # Drop every sensitive scan reference now that the final scan
            # is complete. The values were held only for the minimum scan
            # interval.
            if sensitive_ctx is not None:
                sensitive_ctx.drop()
            sensitive_ctx = None
            scan_key_id = ""
            scan_app_key = ""

            # Retain the final scan result ONLY in the in-memory report.
            report_proto.final_scan_clean = (
                final_scan["real_value_leak_count"] == 0
            )

            # Step 12 — no further file-content change. The write monitor
            # (when enabled) confirms zero writes after the final scan.
            _mark_final_scan_completed()

            # Step 13 — atomic rename as the LAST filesystem operation.
            # The partial directory was created and verified owner-only
            # (mode 0o700, owner == euid). The rename is atomic so the
            # final directory inherits that mode. Verify the final
            # directory remains owner-only after the rename so a race that
            # changed the directory mode before rename cannot publish a
            # non-owner-only evidence directory.
            _require_owner_only_directory(partial_dir, expected_mode=0o700)
            partial_dir.rename(final_dir)
            unverified_published_dir = final_dir
            partial_dir = None
            _require_owner_only_directory(final_dir, expected_mode=0o700)
            unverified_published_dir = None
            report_proto.evidence_dir = str(final_dir)
            return report_proto
        except AuthorizationError:
            # Failure path: guarantee cleanup. The partial directory is
            # logically removed so no incomplete final directory ever
            # appears and no credential-bearing evidence is retained.
            # The backend is destroyed; credentials are released.
            if backend is not None:
                try:
                    backend.destroy()
                except Exception:
                    pass
            backend = None
            inner_backend = None
            credentials = None
            scan_key_id = ""
            scan_app_key = ""
            if sensitive_ctx is not None:
                try:
                    sensitive_ctx.drop()
                except Exception:
                    pass
            sensitive_ctx = None
            if partial_dir is not None:
                _secure_remove_partial(partial_dir)
                partial_dir = None
            if unverified_published_dir is not None:
                _secure_remove_partial(unverified_published_dir)
                unverified_published_dir = None
            raise
        except Exception:
            # Normalize any unexpected exception to a stable code so no raw
            # text, bucket name, endpoint or object bytes ever escape.
            if backend is not None:
                try:
                    backend.destroy()
                except Exception:
                    pass
            backend = None
            inner_backend = None
            credentials = None
            scan_key_id = ""
            scan_app_key = ""
            if sensitive_ctx is not None:
                try:
                    sensitive_ctx.drop()
                except Exception:
                    pass
            sensitive_ctx = None
            if partial_dir is not None:
                _secure_remove_partial(partial_dir)
                partial_dir = None
            if unverified_published_dir is not None:
                _secure_remove_partial(unverified_published_dir)
                unverified_published_dir = None
            raise AuthorizationError("live_execute_failed")
        finally:
            # Belt-and-braces: never leave a live backend, credential
            # reference, or sensitive scan context reachable after this
            # function returns or raises.
            if backend is not None:
                try:
                    backend.destroy()
                except Exception:
                    pass
            scan_key_id = ""
            scan_app_key = ""
            if sensitive_ctx is not None:
                try:
                    sensitive_ctx.drop()
                except Exception:
                    pass
            # The env_access boundary is not a spy; no global uninstall
            # is required. Local reference is simply dropped on return.
    except AuthorizationError as exc:
        return LiveExecuteReport(
            ok=False,
            evidence_run_id=evidence_run_id,
            execution_commit=execution_commit,
            configured_alias=configured_alias,
            canonical_prefix=canonical_prefix,
            authorized_prefix=canonical_prefix,
            configured_import_root=server_config.import_root,
            import_root_comparison_code=import_root_comparison_code,
            import_root_matches_prefix=import_root_matches_prefix,
            gates=list(gates),
            errors=[exc.code],
        )


def _normalize_import_error(exc: Any) -> str:
    """Map an accepted-reader ``ImportValidationError`` code to a stable
    ``AuthorizationError`` code without echoing the original message."""
    code = getattr(exc, "code", "") or ""
    mapping = {
        "object_missing": "approved_object_missing",
        "hash_mismatch": "unexpected_hash_mismatch",
        "malformed_json": "imported_json_malformed",
        "b2_json_too_large": "object_exceeds_authorization_cap",
        "object_changed_during_read": "object_changed_during_evidence_run",
        "b2_aggregate_too_large": "declared_inventory_exceeds_authorization_total",
    }
    return mapping.get(code, "import_validation_failed")


# ---------------------------------------------------------------------------
# Section 5 — evidence output root confinement + partial-directory creation
# ---------------------------------------------------------------------------


def _validate_evidence_base(evidence_dir: Path) -> None:
    """Constrain the live evidence output root.

    For live execution the resolved base must:
    - equal exactly ``LIVE_EVIDENCE_DIR``;
    - not be a symlink;
    - have no symlink in any existing path component;
    - resolve to a parent under ``/tmp``.

    Tests bypass this via direct dependency injection (a custom evidence_dir
    passed straight to ``run_live_execute`` is allowed; the real CLI
    ``execute`` invokes this validator before creating or inspecting any
    output directory, and rejects arbitrary ``--evidence-out`` values).
    """
    base = Path(evidence_dir)
    try:
        resolved = base.resolve(strict=False)
    except OSError:
        raise AuthorizationError("evidence_base_unresolvable")
    if base.is_symlink():
        raise AuthorizationError("evidence_base_symlink_rejected")
    # Reject any symlink in the existing path components (e.g. /tmp itself
    # replaced by a symlink, or an intermediate directory).
    _reject_symlink_path_components(base)
    if str(resolved) != LIVE_EVIDENCE_DIR:
        raise AuthorizationError("evidence_base_not_confined")
    # Parent must live under /tmp.
    if not str(resolved).startswith("/tmp/"):
        raise AuthorizationError("evidence_base_not_under_tmp")


def _reject_symlink_path_components(path: Path) -> None:
    """Reject if ``path`` or any of its existing components is a symlink.

    Walks each existing path component of ``path`` from the filesystem root
    and uses ``lstat`` to detect symlinks. A symlink at any existing
    component under the controlled evidence root is rejected before any
    file under that path is read or scanned.
    """
    import stat as _statmod
    cursor = Path(path)
    components: list[Path] = []
    while True:
        components.append(cursor)
        if cursor.parent == cursor:
            break
        cursor = cursor.parent
    for comp in reversed(components):
        try:
            st = os.lstat(comp)
        except OSError:
            continue
        if _statmod.S_ISLNK(st.st_mode):
            raise AuthorizationError("evidence_path_symlink_component")


def _require_owner_only_directory(path: Path, *, expected_mode: int = 0o700) -> None:
    """Fail-closed owner-only directory verification.

    Requires:

    - ``path`` exists and is a directory;
    - ``path`` is not a symlink (lstat);
    - the directory owner UID equals the current effective UID;
    - the directory mode is exactly ``expected_mode`` (default ``0o700``).

    Any mismatch rejects with a stable code. Raw paths never escape.
    """
    import stat as _statmod
    try:
        st = os.lstat(path)
    except OSError:
        raise AuthorizationError("evidence_permissions_unverified")
    if _statmod.S_ISLNK(st.st_mode):
        raise AuthorizationError("evidence_permissions_unverified")
    if not _statmod.S_ISDIR(st.st_mode):
        raise AuthorizationError("evidence_permissions_unverified")
    try:
        euid = os.geteuid()
    except OSError:
        raise AuthorizationError("evidence_permissions_unverified")
    if st.st_uid != euid:
        raise AuthorizationError("evidence_owner_mismatch")
    if _statmod.S_IMODE(st.st_mode) != expected_mode:
        raise AuthorizationError("evidence_permissions_unverified")


def _create_partial_dir(evidence_dir: Path, run_id: str) -> tuple[Path, Path]:
    """Create a validated partial directory and return (partial, final).

    Refuses path-traversal run ids, refuses an existing final directory,
    refuses a pre-existing partial directory rather than recursively
    deleting an unverified caller-controlled path, rejects any symlink at
    a path component under the controlled evidence root, and creates the
    base + partial directory with owner-only permissions (mode 0o700).

    PS-041E2-B Phase-1 correction: directory permissions are fail-closed.
    The base and partial directories must be owned by the current
    effective UID and have mode exactly ``0o700`` after creation. A chmod
    failure rejects; a mode mismatch rejects; an ownership mismatch
    rejects. There is no best-effort ``except OSError: pass`` swallow.
    """
    import stat as _statmod
    if not _EVIDENCE_RUN_ID.match(run_id) or "--" in run_id:
        raise AuthorizationError("evidence_run_id_invalid")
    base = Path(evidence_dir)
    # Reject any symlink in the existing path components of the evidence
    # base before creating anything under it.
    _reject_symlink_path_components(base)
    # Create the base with owner-only permissions. Only a directory created
    # by this call is chmod'd; an existing directory must already satisfy the
    # exact owner/mode contract and is never repaired into compliance.
    base_created = False
    try:
        base.mkdir(parents=True, exist_ok=False, mode=0o700)
        base_created = True
    except FileExistsError:
        base_created = False
    except OSError:
        raise AuthorizationError("evidence_permissions_unverified")
    if base_created:
        try:
            os.chmod(base, 0o700)
        except OSError:
            raise AuthorizationError("evidence_permissions_unverified")
    # Re-stat and verify after creation/chmod, or verify the pre-existing
    # directory without mutating it.
    _require_owner_only_directory(base, expected_mode=0o700)
    final_dir = base / run_id
    if final_dir.exists() or final_dir.is_symlink():
        raise AuthorizationError("evidence_output_directory_exists")
    partial_dir = base / f".partial-{run_id}"
    if partial_dir.exists() or partial_dir.is_symlink():
        # Never blindly rmtree a caller-controlled path. Fail closed.
        raise AuthorizationError("evidence_partial_directory_exists")
    # Owner-only create. ``mkdir`` mode is masked by umask; chmod enforces.
    partial_dir.mkdir(parents=True, exist_ok=False)
    try:
        os.chmod(partial_dir, 0o700)
    except OSError:
        # Best-effort cleanup of the just-created partial, then reject.
        try:
            partial_dir.rmdir()
        except OSError:
            pass
        raise AuthorizationError("evidence_permissions_unverified")
    # Re-stat and verify the partial directory is owner-only and owned by
    # the current effective UID after chmod.
    _require_owner_only_directory(partial_dir, expected_mode=0o700)
    return partial_dir, final_dir


def _secure_remove_partial(partial_dir: Path) -> None:
    """Best-effort logical removal of a partial evidence directory.

    Performs a best-effort overwrite of every regular file with zeros
    before unlinking, then removes the directory tree. Never renames the
    directory to ``.quarantine-*``. Never retains the evidence payload.

    Accurate removal contract (PS-041E2-B Phase-1 correction):

    - best-effort overwrite of regular files (zeros);
    - logical ``unlink`` of each file and directory removal;
    - no payload is retained at the controlled evidence path;
    - **physical media erasure is NOT claimed** on SSD, copy-on-write or
      journaled filesystems. The overwrite is a logical best-effort step;
      it does not guarantee the underlying storage medium has zeroed the
      bytes (wear leveling, copy-on-write snapshots, journaling and
      deduplication may retain stale blocks).

    A real-value leak must NEVER cause the partial directory to be renamed
    to ``.quarantine-*``: a quarantine rename retains the credential-bearing
    evidence payload on disk. This function guarantees the partial directory
    and every byte of its contents are logically removed.
    """
    import shutil
    import stat as _statmod
    try:
        if not partial_dir.exists():
            return
        for entry in Path(partial_dir).iterdir():
            try:
                st = os.lstat(entry)
            except OSError:
                continue
            if _statmod.S_ISLNK(st.st_mode):
                try:
                    entry.unlink()
                except OSError:
                    pass
                continue
            if not _statmod.S_ISREG(st.st_mode):
                continue
            size = st.st_size
            try:
                with open(entry, "r+b") as f:
                    if size > 0:
                        f.write(b"\x00" * size)
                        f.flush()
                        os.fsync(f.fileno())
            except OSError:
                pass
            try:
                entry.unlink()
            except OSError:
                pass
        shutil.rmtree(partial_dir, ignore_errors=True)
    except Exception:
        pass


def _write_sanitized_failure_summary(
    evidence_base: Path, run_id: str, *, error_code: str,
) -> None:
    """Write a sanitized failure summary next to the removed partial dir.

    Contains only a stable error code and timestamp; no source evidence, no
    credential value, no object bytes. The summary is written to the
    evidence base directory (the parent of the removed partial), never
    inside a partial directory.

    Safe exclusive creation (PS-041E2-B Phase-1 correction):

    - the summary is created with ``os.open`` using
      ``O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW`` and mode ``0o600``;
    - the basename is an exact controlled ``.failure-<run_id>.json``;
    - bounded deterministic UTF-8 bytes (sorted JSON, ASCII-safe);
    - ``fsync`` before close;
    - when the entry already exists, is a symlink, or safe exclusive
      creation cannot be established, the summary is silently omitted
      (never overwrites or follows a caller-created entry).
    """
    if not _EVIDENCE_RUN_ID.fullmatch(run_id) or "--" in run_id:
        return
    if not re.fullmatch(r"[a-z][a-z0-9_]{0,95}", error_code):
        return
    controlled_basename = f".failure-{run_id}.json"
    summary_path = Path(evidence_base) / controlled_basename
    payload = json.dumps(
        {
            "error_code": error_code,
            "ts": _utc_now().isoformat().replace("+00:00", "Z"),
        },
        sort_keys=True, ensure_ascii=True,
    ).encode("utf-8")
    # Establish safe exclusive no-follow creation flags.
    open_flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        open_flags |= os.O_NOFOLLOW
    else:
        # Cannot establish no-follow semantics — omit the summary rather
        # than risk following a caller-created symlink.
        return
    if hasattr(os, "O_CLOEXEC"):
        open_flags |= os.O_CLOEXEC
    fd: int | None = None
    try:
        try:
            fd = os.open(str(summary_path), open_flags, 0o600)
        except OSError:
            # Pre-existing regular file, pre-existing symlink, exclusive
            # race, or any other OSError: silently omit rather than
            # overwrite or follow a caller-created entry.
            return
        try:
            # Creation mode is filtered by umask, so enforce and verify the
            # exact owner-only file mode on the already-open descriptor.
            os.fchmod(fd, 0o600)
            st = os.fstat(fd)
            import stat as _statmod
            if (
                not _statmod.S_ISREG(st.st_mode)
                or st.st_uid != os.geteuid()
                or _statmod.S_IMODE(st.st_mode) != 0o600
            ):
                raise OSError("unsafe_failure_summary_descriptor")
            written = os.write(fd, payload)
            if written != len(payload):
                raise OSError("short_failure_summary_write")
            os.fsync(fd)
        except OSError:
            # Best-effort: if the write/fsync failed, unlink the partial
            # summary so no truncated/empty failure summary is retained.
            try:
                os.close(fd)
            except OSError:
                pass
            fd = None
            try:
                summary_path.unlink()
            except OSError:
                pass
            return
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Section 6 — atomic provisional + finalization
# ---------------------------------------------------------------------------


def _write_provisional_evidence(
    partial_dir: Path,
    report: LiveExecuteReport,
    *,
    git_state: GitState,
    gates: list[GateResult],
) -> None:
    """Write every provisional evidence artifact into ``partial_dir``.

    Writes all artifacts except ``cleanup-verification.txt``,
    ``classified-security-scan.txt`` and ``known-limitations.txt`` (those
    depend on post-cleanup / post-scan state). ``authorization-summary.json``
    and ``execution-summary.json`` are written with
    ``cleanup_verified=False`` here and rewritten after cleanup verification.
    """
    authorization_summary = {
        "schema": LIVE_SCHEMA,
        "evidence_run_id": report.evidence_run_id,
        "execution_commit": report.execution_commit,
        "configured_alias": report.configured_alias,
        "canonical_prefix": report.canonical_prefix,
        "authorized_object_count": report.authorized_objects,
        "allowed_keys": sorted(_safe_keys_only(report.role_plan)),
        "object_role_plan": report.role_plan,
        "alias_comparison_code": report.alias_comparison_code,
        "bucket_comparison_code": report.bucket_comparison_code,
        "cleanup_verified": False,
    }
    _write_json_atomic(partial_dir / "authorization-summary.json", authorization_summary)

    gates_payload = {
        "live_execute_gates_count": LIVE_EXECUTE_GATES_COUNT,
        "live_execute_gates": list(LIVE_EXECUTE_GATES),
        "all_execute_gates_passed": _all_gates_passed(gates)
            and len(gates) == LIVE_EXECUTE_GATES_COUNT,
        "gate_results": [
            {"index": g.index, "name": g.name, "ok": g.ok, "code": g.code}
            for g in sorted(gates, key=lambda x: x.index)
        ],
    }
    _write_json_atomic(partial_dir / "execution-gates.json", gates_payload)

    git_binding = {
        "implementation_branch": PS_041E2B_BRANCH,
        "accepted_ref": ACCEPTED_EXECUTION_REF,
        "observed_branch": git_state.branch,
        "observed_head_commit": git_state.head_commit,
        "observed_accepted_commit": git_state.accepted_commit,
        "observed_remote_accepted_commit": report.remote_accepted_commit,
        "tree_clean": git_state.tree_clean,
        "head_matches_execution_commit": git_state.head_commit.lower() == report.execution_commit,
        "head_matches_accepted": git_state.head_commit.lower() == git_state.accepted_commit.lower(),
        "head_matches_remote_accepted": bool(
            report.remote_accepted_commit
            and git_state.head_commit.lower() == report.remote_accepted_commit.lower()
        ),
    }
    _write_json_atomic(partial_dir / "git-binding.json", git_binding)

    server_binding = {
        "configured_alias": report.configured_alias,
        "authorized_prefix": report.authorized_prefix,
        "configured_import_root": report.configured_import_root,
        "import_root_comparison_code": report.import_root_comparison_code,
        "import_root_matches_prefix": report.import_root_matches_prefix,
        "alias_comparison_code": report.alias_comparison_code,
        "bucket_comparison_code": report.bucket_comparison_code,
        "server_configuration_present": True,
    }
    _write_json_atomic(partial_dir / "server-binding.json", server_binding)

    _write_json_atomic(partial_dir / "approved-object-inventory.json", report.approved_object_inventory)
    _write_json_atomic(partial_dir / "object-role-plan.json", report.role_plan)
    _write_json_atomic(partial_dir / "normalized-b2-references.json", report.normalized_b2_references)

    json_read_results = [
        {"object_key": k, "role": report.role_plan[k], "reads": 1}
        for k in sorted(report.role_plan)
        if report.role_plan[k] in JSON_READ_ROLES
    ]
    _write_json_atomic(partial_dir / "json-read-results.json", json_read_results)
    _write_json_atomic(partial_dir / "hash-verification-results.json", report.hash_results)

    media_read_results = [
        {"object_key": k, "role": report.role_plan[k], "reads": 1}
        for k in sorted(report.role_plan)
        if report.role_plan[k] in MEDIA_BYTE_ROLES and any(
            h["key"] == k and h["status"] in {"matched", "computed"} for h in report.hash_results
        )
    ]
    _write_json_atomic(partial_dir / "media-read-results.json", media_read_results)

    observation = {
        "observation_stable": report.observation_stable,
        "observation_comparisons": report.observation_comparisons,
    }
    _write_json_atomic(partial_dir / "observation-stability.json", observation)

    import_result = {
        "campaign_id": report.campaign_id,
        "bundle_id": report.bundle_id,
        "import_created": report.import_created,
        "import_service_used": report.import_service_used,
        "import_service": "ProofStudioService.import_genblaze_bundle",
        "build_candidate_invocations": 2,
    }
    _write_json_atomic(partial_dir / "import-result.json", import_result)

    idempotency_result = {
        "import_idempotent": report.import_idempotent,
        "bundle_id": report.bundle_id,
        "import_service_used": report.import_service_used,
    }
    _write_json_atomic(partial_dir / "idempotency-result.json", idempotency_result)

    private_lineage_payload = dict(report.private_lineage_summary)
    private_lineage_payload["readback_ok"] = report.private_lineage_readback
    _write_json_atomic(partial_dir / "private-lineage-summary.json", private_lineage_payload)

    private_passport_payload = dict(report.private_passport_summary)
    private_passport_payload["readback_ok"] = report.passport_readback
    _write_json_atomic(partial_dir / "private-passport-summary.json", private_passport_payload)

    operation_counts = _build_operation_counts(report)
    _write_json_atomic(partial_dir / "operation-counts.json", operation_counts)

    execution_summary = _build_execution_summary(report, gates)
    _write_json_atomic(partial_dir / "execution-summary.json", execution_summary)


def _build_operation_counts(report: LiveExecuteReport) -> dict[str, Any]:
    """Build the canonical operation-counts payload.

    Carries SDK invocation counts separately from actual HTTP-attempt counts,
    plus close-exactly-once evidence and the controlled-read invariant. For
    the accepted controlled path the HeadBucket and regional-probe HTTP
    attempt counters are zero.
    """
    return {
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
        "live_b2_calls": report.live_b2_calls,
        "real_backend_factory_used": report.real_backend_factory_used,
        "controlled_read_invariant": (
            report.head_bucket_http_attempts == 0
            and report.regional_probe_http_attempts == 0
            and report.list_calls == 0
            and report.write_attempts == 0
            and report.delete_attempts == 0
            and report.signed_url_attempts == 0
        ),
    }

    execution_summary = _build_execution_summary(report, gates)
    _write_json_atomic(partial_dir / "execution-summary.json", execution_summary)


def _build_execution_summary(report: LiveExecuteReport, gates: list[GateResult]) -> dict[str, Any]:
    return {
        "ok": report.ok,
        "slice": "PS-041E2-B",
        "mode": "live-executor",
        "evidence_run_id": report.evidence_run_id,
        "execution_commit": report.execution_commit,
        "all_execute_gates_passed": _all_gates_passed(gates)
            and len(gates) == LIVE_EXECUTE_GATES_COUNT,
        "future_execute_gates_count": FUTURE_EXECUTE_GATES_COUNT,
        "authorized_objects": report.authorized_objects,
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
        "list_calls": report.list_calls,
        "write_attempts": report.write_attempts,
        "delete_attempts": report.delete_attempts,
        "signed_url_attempts": report.signed_url_attempts,
        "provider_calls": report.provider_calls,
        "total_bytes_read": report.total_bytes_read,
        "observation_stable": report.observation_stable,
        "observation_comparisons": report.observation_comparisons,
        "import_created": report.import_created,
        "import_idempotent": report.import_idempotent,
        "import_service_used": report.import_service_used,
        "private_lineage_readback": report.private_lineage_readback,
        "passport_readback": report.passport_readback,
        "passport_schema": report.passport_schema,
        "bundle_id": report.bundle_id,
        "campaign_id": report.campaign_id,
        "alias_comparison_code": report.alias_comparison_code,
        "bucket_comparison_code": report.bucket_comparison_code,
        "cleanup_verified": report.cleanup_verified,
        "live_b2_calls": report.live_b2_calls,
        "real_backend_factory_used": report.real_backend_factory_used,
        "remote_accepted_commit": report.remote_accepted_commit,
    }


def _rewrite_summary_files(
    partial_dir: Path,
    report: LiveExecuteReport,
    git_state: GitState,
    gates: list[GateResult],
) -> None:
    """Rewrite authorization-summary.json, execution-summary.json and
    operation-counts.json with ``cleanup_verified=true`` and the verified
    close-exactly-once state after the cleanup block + scan have completed.

    ``operation-counts.json`` is rewritten here because the underlying
    client close state (inner_close_attempted / inner_close_succeeded /
    inner_close_call_count) is only known after the backend destroy at
    step 3. Rewriting it at step 8 keeps the canonical 20-file set complete
    from step 2 while ensuring the final bytes carry the verified close
    state.
    """
    authorization_summary = {
        "schema": LIVE_SCHEMA,
        "evidence_run_id": report.evidence_run_id,
        "execution_commit": report.execution_commit,
        "configured_alias": report.configured_alias,
        "canonical_prefix": report.canonical_prefix,
        "authorized_object_count": report.authorized_objects,
        "allowed_keys": sorted(_safe_keys_only(report.role_plan)),
        "object_role_plan": report.role_plan,
        "alias_comparison_code": report.alias_comparison_code,
        "bucket_comparison_code": report.bucket_comparison_code,
        "cleanup_verified": True,
    }
    _write_json_atomic(partial_dir / "authorization-summary.json", authorization_summary)
    _write_json_atomic(partial_dir / "execution-summary.json", _build_execution_summary(report, gates))
    _write_json_atomic(partial_dir / "operation-counts.json", _build_operation_counts(report))


def _verify_evidence_files_complete(directory: Path) -> None:
    """Verify the directory contains exactly ``LIVE_EVIDENCE_FILES`` as
    regular non-symlink files.

    Uses ``lstat`` to reject symlinks before reading. Rejects any
    unexpected entry before finalization. Rejects any non-regular entry
    (FIFO, device, socket).
    """
    import stat as _statmod
    expected = set(LIVE_EVIDENCE_FILES)
    actual: set[str] = set()
    for entry in Path(directory).iterdir():
        try:
            st = os.lstat(entry)
        except OSError:
            raise AuthorizationError("evidence_entry_unreadable")
        if _statmod.S_ISLNK(st.st_mode):
            raise AuthorizationError("evidence_entry_symlink")
        actual.add(entry.name)
    missing = sorted(expected - actual)
    if missing:
        raise AuthorizationError("evidence_files_missing")
    unexpected = sorted(actual - expected)
    if unexpected:
        raise AuthorizationError("evidence_files_unexpected")
    bad_kind: list[str] = []
    for name in LIVE_EVIDENCE_FILES:
        path = Path(directory) / name
        try:
            st = os.lstat(path)
        except OSError:
            raise AuthorizationError("evidence_files_missing")
        if not _statmod.S_ISREG(st.st_mode):
            bad_kind.append(name)
    if bad_kind:
        raise AuthorizationError("evidence_files_not_regular")


def _format_cleanup_verification(*, backend_destroyed: bool,
                                  credentials_released: bool,
                                  cleanup_secret: dict[str, Any],
                                  sensitive_values_held_only_for_scan: bool = True) -> str:
    """Render the final cleanup-verification.txt text.

    The text is completed at finalization step 4 (before the classified
    scan) and never rewritten. It carries only verifiable facts and
    structural guarantees — no scan result, no credential value.

    ``cleanup_secret`` carries the explicit secret-read evidence from
    :func:`_evaluate_cleanup_secret_reads`. Booleans are emitted as
    lowercase ``true`` / ``false`` for stable text matching.
    """
    def _b(value: bool) -> str:
        return "true" if value else "false"
    return (
        "PS-041E2-B live evidence — cleanup verification\n"
        "\n"
        f"backend_destroyed={_b(backend_destroyed)}\n"
        f"credentials_released={_b(credentials_released)}\n"
        f"no_pre_gate_secret_value_reads={_b(cleanup_secret['no_pre_gate_secret_value_reads'])}\n"
        f"pre_gate_secret_value_read_count={cleanup_secret['pre_gate_secret_value_read_count']}\n"
        f"post_gate_secret_value_read_count={cleanup_secret['post_gate_secret_value_read_count']}\n"
        f"post_gate_secret_names_match={_b(cleanup_secret['post_gate_secret_names_match'])}\n"
        f"secret_read_order_valid={_b(cleanup_secret['secret_read_order_valid'])}\n"
        f"cleanup_secret_reads_verified={_b(cleanup_secret['cleanup_secret_reads_verified'])}\n"
        f"sensitive_values_held_only_for_scan_interval={_b(sensitive_values_held_only_for_scan)}\n"
        "no_temporary_credential_file_written=true\n"
        "no_environment_file_contents_read=true\n"
        "no_object_bytes_retained=true\n"
        "no_inner_backend_reference_retained=true\n"
        "no_payload_quarantine_retained=true\n"
    )


def _safe_keys_only(role_plan: dict[str, str]) -> list[str]:
    """Return only allowlisted keys that pass the canonical key safety check."""
    return [k for k in role_plan if _is_safe_key(k)]


# ---------------------------------------------------------------------------
# Write monitor — test-only mechanism proving zero writes after the final scan.
# ---------------------------------------------------------------------------


class _WriteMonitor:
    """Test-only write monitor.

    When ``_WRITE_MONITOR`` is not None, every tracked evidence write records
    its path and whether it occurred after the final-scan marker. Tests
    inspect ``post_final_scan_writes`` to prove zero content writes occurred
    after the strict final scan completed. In production this is always None
    and has zero overhead.
    """

    __slots__ = ("final_scan_started", "final_scan_completed", "writes")

    def __init__(self) -> None:
        self.final_scan_started = False
        self.final_scan_completed = False
        self.writes: list[tuple[str, bool]] = []

    def record(self, path: Path) -> None:
        self.writes.append((str(path), self.final_scan_started))

    @property
    def post_final_scan_writes(self) -> list[str]:
        return [p for (p, after) in self.writes if after]


_WRITE_MONITOR: "_WriteMonitor | None" = None


def _enable_write_monitor() -> _WriteMonitor:
    """Enable the test-only write monitor and return it."""
    global _WRITE_MONITOR
    _WRITE_MONITOR = _WriteMonitor()
    return _WRITE_MONITOR


def _disable_write_monitor() -> None:
    global _WRITE_MONITOR
    _WRITE_MONITOR = None


def _track_evidence_write(path: Path) -> None:
    if _WRITE_MONITOR is not None:
        _WRITE_MONITOR.record(path)


def _mark_final_scan_started() -> None:
    if _WRITE_MONITOR is not None:
        _WRITE_MONITOR.final_scan_started = True


def _mark_final_scan_completed() -> None:
    if _WRITE_MONITOR is not None:
        _WRITE_MONITOR.final_scan_completed = True


def _mark_final_scan_aborted() -> None:
    if _WRITE_MONITOR is not None:
        _WRITE_MONITOR.final_scan_started = False


def _write_json_atomic(path: Path, payload: Any) -> None:
    """Write JSON deterministically with sorted keys and ASCII-safe encoding."""
    _track_evidence_write(path)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Section 7 — real fail-closed security scan
# ---------------------------------------------------------------------------


# Marker words are expected defensive references (token names in prohibition
# lists, sanitizer docs, source-level marker constants). Their presence is
# classified separately from real credential-bearing values.
SECURITY_MARKER_TOKENS: tuple[str, ...] = (
    "B2_APPLICATION_KEY", "B2_APPLICATION_KEY_ID", "B2_APP_KEY", "B2_KEY_ID",
    "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "Authorization", "Bearer",
    "X-Amz-", "signed url", "presigned", "endpoint url", "DATABASE_URL",
    "password", "secret", "token", "cookie",
)

# Regex patterns that, when matched in evidence, indicate a real leak rather
# than a marker word. Each is anchored to a value shape (not a field name).
_CREDENTIAL_ASSIGNMENT_RE = re.compile(
    r"(?i)(?:b2_key_id|b2_app_key|b2_application_key|b2_application_key_id|"
    r"aws_access_key_id|aws_secret_access_key|password|passwd|pwd|secret|"
    r"token|api[_-]?key)\s*[:=]\s*[\"']?[A-Za-z0-9/+=:_-]{8,}"
)
_SIGNED_URL_QUERY_RE = re.compile(
    r"\?(?:X-Amz-|Expires=|Signature=|X-Goog-|sv=|se=|sig=|ss=|sr=|sp=)"
)
_AUTH_HEADER_RE = re.compile(
    r"(?i)(?:Authorization|X-Amz-Security-Token|Proxy-Authorization)\s*:\s*"
    r"(?:Bearer|Basic|AWS4-HMAC-SHA256)\s+[A-Za-z0-9/+=:_-]+"
)
_DB_URL_CRED_RE = re.compile(
    r"(?i)[a-z][a-z0-9+.-]*://[^/\s:]+:[^/\s@]+@[^\s/]+"
)
_HTTP_URL_RE = re.compile(r"https?://[A-Za-z0-9.\-]+(?:/[^\s\"'\\]*)?")


class SensitiveScanContext:
    """Narrow scan context that holds EXACT sensitive values for the
    minimum scan interval.

    Carries the real B2 key id, the real B2 application key, the raw
    bucket identity, and the object-byte sentinels. The values are held
    only for the scan interval; :meth:`drop` clears every reference so
    no sensitive value is retained after scanning. Used as a context
    manager, ``__exit__`` drops the values automatically.

    The scan compares these EXACT values against every evidence file. A
    bare credential value under an unrelated JSON property, inside
    ordinary prose, or with no ``B2_`` / ``secret`` marker is detected
    via exact substring match — the comparison does not rely on a
    credential-like field name.
    """

    __slots__ = ("_values", "_dropped")

    def __init__(self, *, key_id: str = "", app_key: str = "",
                 bucket_identity: str = "",
                 object_byte_sentinels: tuple[bytes, ...] = ()) -> None:
        values: dict[str, str] = {}
        if key_id:
            values["key_id"] = key_id
        if app_key:
            values["app_key"] = app_key
        if bucket_identity:
            values["bucket_identity"] = bucket_identity
        sentinel_join = "|".join(
            s.decode("utf-8", errors="ignore")
            for s in object_byte_sentinels if s
        )
        if sentinel_join:
            values["object_byte_sentinel_join"] = sentinel_join
        self._values = values
        self._dropped = False

    @property
    def values(self) -> dict[str, str]:
        if self._dropped:
            return {}
        return dict(self._values)

    @property
    def dropped(self) -> bool:
        return self._dropped

    def drop(self) -> None:
        """Drop every sensitive scan reference. Idempotent."""
        self._values = {}
        self._dropped = True

    def __enter__(self) -> "SensitiveScanContext":
        return self

    def __exit__(self, *exc: object) -> None:
        self.drop()


def _collect_secret_values(
    *,
    object_byte_sentinels: list[bytes],
    bucket_identity: str,
    key_id: str = "",
    app_key: str = "",
) -> dict[str, str]:
    """Build the in-memory secret-value comparison map.

    The caller passes only values that already live in-memory (credential
    values are read from the ``LiveCredentials`` object inside
    ``run_live_execute`` and never serialized into the scan output).
    Includes the EXACT key id and application key so a bare credential
    value is detected even without a credential-like field name.
    """
    sentinels_text = "|".join(
        s.decode("utf-8", errors="ignore") for s in object_byte_sentinels if s
    )
    out: dict[str, str] = {}
    if sentinels_text:
        out["object_byte_sentinel_join"] = sentinels_text
    if bucket_identity:
        out["bucket_identity"] = bucket_identity
    if key_id:
        out["key_id"] = key_id
    if app_key:
        out["app_key"] = app_key
    return out


def _read_evidence_file(
    path: Path,
    *,
    expected_basename: str | None = None,
    per_file_cap: int = PER_EVIDENCE_FILE_MAX_BYTES,
    aggregate_cap: int = AGGREGATE_EVIDENCE_MAX_BYTES,
    aggregate_used: int,
) -> tuple[str, int]:
    """Read one evidence file via a descriptor-based no-follow path.

    Guarantees (all enforced before any byte is matched against secrets):

    1. validate the expected basename. When ``expected_basename`` is
       supplied it must equal ``path.name`` and be a simple basename (no
       separators, no path traversal). When it is ``None`` the function
       still validates that ``path.name`` is a non-empty simple basename;
    2. ``os.open`` with ``O_RDONLY | O_NOFOLLOW`` (and ``O_CLOEXEC`` where
       available). A symlink target is rejected with
       ``evidence_file_symlink`` (``O_NOFOLLOW`` returns ``ELOOP``). When
       the platform does not support ``O_NOFOLLOW`` the read fails closed
       with ``evidence_file_unreadable`` (no-follow semantics cannot be
       established);
    3. ``os.fstat`` on the opened descriptor;
    4. require a regular file (``evidence_file_symlink`` for a symlink
       descriptor, ``evidence_file_unreadable`` for a non-regular
       descriptor);
    5. require the descriptor owner to equal the current effective UID
       (``evidence_file_unreadable`` on mismatch — an owner swap is treated
       as unreadable rather than surfacing ownership detail);
    6. enforce per-file and aggregate size caps from fstat
       (``evidence_file_too_large`` / ``evidence_aggregate_too_large``);
    7. read exactly the declared bounded size (short reads reject with
       ``evidence_file_unreadable``);
    8. verify EOF immediately afterward (extra bytes after the declared
       size reject with ``evidence_file_replaced``);
    9. ``os.fstat`` the descriptor again;
    10. compare device, inode, mode and size between the two fstat calls —
        any change rejects with ``evidence_file_replaced`` (inode/device
        replacement or size mutation between the bounded read and the
        second fstat);
    11. decode strict UTF-8 (``evidence_file_invalid_utf8``);
    12. close the descriptor in ``finally``.

    Stable error codes — paths, raw exception text and sensitive contents
    are NEVER included in errors. Returns ``(text, new_aggregate_used)``.
    """
    import stat as _statmod
    # Step 1 — validate the expected basename. Always require path.name to
    # be a non-empty simple basename (no separators, no path traversal).
    basename = path.name
    if not isinstance(basename, str) or not basename:
        raise AuthorizationError("evidence_file_unreadable")
    if Path(basename).name != basename:
        # basename contains a separator — reject.
        raise AuthorizationError("evidence_file_unreadable")
    if expected_basename is not None:
        if (
            not isinstance(expected_basename, str)
            or not expected_basename
            or basename != expected_basename
            or Path(expected_basename).name != expected_basename
        ):
            raise AuthorizationError("evidence_file_unreadable")
    # Establish no-follow open flags. O_NOFOLLOW is required; O_CLOEXEC is
    # applied where available.
    open_flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        open_flags |= os.O_NOFOLLOW
    else:
        # Cannot establish no-follow semantics — fail closed.
        raise AuthorizationError("evidence_file_unreadable")
    if hasattr(os, "O_CLOEXEC"):
        open_flags |= os.O_CLOEXEC
    fd: int | None = None
    try:
        try:
            fd = os.open(str(path), open_flags)
        except OSError as exc:
            # O_NOFOLLOW reports a final-component symlink as ELOOP. Keep
            # that distinct from missing/unreadable failures without
            # exposing the path or raw exception.
            import errno as _errno
            if exc.errno == _errno.ELOOP:
                raise AuthorizationError("evidence_file_symlink")
            raise AuthorizationError("evidence_file_unreadable")
        # Step 4/5/6 — first fstat: regular file, owner, per-file/aggregate caps.
        try:
            st1 = os.fstat(fd)
        except OSError:
            raise AuthorizationError("evidence_file_unreadable")
        mode1 = st1.st_mode
        if _statmod.S_ISLNK(mode1):
            raise AuthorizationError("evidence_file_symlink")
        if not _statmod.S_ISREG(mode1):
            raise AuthorizationError("evidence_file_unreadable")
        # Owner must equal the current effective UID.
        try:
            euid = os.geteuid()
        except OSError:
            raise AuthorizationError("evidence_file_unreadable")
        if st1.st_uid != euid:
            raise AuthorizationError("evidence_file_unreadable")
        size = int(st1.st_size)
        if size > int(per_file_cap):
            raise AuthorizationError("evidence_file_too_large")
        if aggregate_used + size > int(aggregate_cap):
            raise AuthorizationError("evidence_aggregate_too_large")
        # Step 7 — read exactly the declared bounded size.
        try:
            data = os.read(fd, size)
        except OSError:
            raise AuthorizationError("evidence_file_unreadable")
        if len(data) != size:
            # Short / partial read.
            raise AuthorizationError("evidence_file_unreadable")
        # Step 8 — verify EOF immediately afterward: any extra byte after
        # the declared size means the file was replaced/grown mid-read.
        try:
            extra = os.read(fd, 1)
        except OSError:
            raise AuthorizationError("evidence_file_unreadable")
        if extra != b"":
            raise AuthorizationError("evidence_file_replaced")
        # Step 9/10/11 — second fstat and compare device, inode, mode, size.
        try:
            st2 = os.fstat(fd)
        except OSError:
            raise AuthorizationError("evidence_file_unreadable")
        if (
            st2.st_dev != st1.st_dev
            or st2.st_ino != st1.st_ino
            or st2.st_mode != st1.st_mode
            or int(st2.st_size) != size
        ):
            raise AuthorizationError("evidence_file_replaced")
        # Step 12 — decode strict UTF-8.
        try:
            text = data.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            raise AuthorizationError("evidence_file_invalid_utf8")
        except Exception:
            raise AuthorizationError("evidence_file_invalid_utf8")
        return text, aggregate_used + size
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass


def _security_scan_directory(
    directory: Path,
    *,
    secret_values: dict[str, str] | None = None,
    bucket_identity: str = "",
    sensitive: "SensitiveScanContext | None" = None,
    expected_files: frozenset[str] | None = None,
) -> dict[str, Any]:
    """Scan one evidence directory for credential markers vs real values.

    Distinguishes marker words (defensive field-name lists, prohibition docs)
    from real credential-bearing values. Real leaks are detected by:

    - exact-match of in-memory secret values (B2 key id, B2 application key,
      object byte sentinels, raw bucket identity). A bare credential value
      is detected even without a credential-like field name;
    - regex matches for credential assignments, signed/presigned URL query
      parameters, Authorization/Bearer headers, credential-bearing database
      URLs, and unexpected http(s) URLs;
    - symlinked evidence files (rejected before reading via ``lstat``);
    - non-regular evidence files (FIFO / device / socket);
    - unexpected evidence files (entries not in ``expected_files``).

    The sensitive comparison values are NEVER serialized into the returned
    report. The report carries only file names, token names and per-category
    counts. Every sensitive reference held by the caller's
    ``SensitiveScanContext`` must be dropped after scanning.
    """
    import stat as _statmod
    marker_hits: list[dict[str, str]] = []
    real_leaks: list[dict[str, str]] = []
    category_counts: dict[str, int] = {
        "credential_assignment": 0,
        "signed_url_query": 0,
        "auth_header": 0,
        "db_url_with_credentials": 0,
        "unexpected_http_url": 0,
        "raw_bucket_identity": 0,
        "object_byte_sentinel": 0,
        "bare_credential_value": 0,
        "symlink_evidence_file": 0,
        "nonregular_evidence_file": 0,
        "unexpected_evidence_file": 0,
    }
    secret_values = dict(secret_values or {})
    if sensitive is not None:
        for k, v in sensitive.values.items():
            secret_values.setdefault(k, v)
    bucket_sentinel = bucket_identity or secret_values.get("bucket_identity", "")
    object_sentinels_text = secret_values.get("object_byte_sentinel_join", "")
    exact_key_id = secret_values.get("key_id", "")
    exact_app_key = secret_values.get("app_key", "")
    # Pre-extract per-sentinel substrings for robust matching: long enough to
    # be distinctive, short enough to survive JSON re-serialization.
    object_sentinel_substrings: list[str] = []
    if object_sentinels_text:
        for span in (64, 32, 16):
            for i in range(0, max(0, len(object_sentinels_text) - span), span):
                chunk = object_sentinels_text[i:i + span]
                if len(chunk) >= 16:
                    object_sentinel_substrings.append(chunk)

    def _record_leak(name: str, category: str) -> None:
        real_leaks.append({"file": name, "category": category})
        category_counts[category] = category_counts.get(category, 0) + 1

    aggregate_used = 0
    for path in sorted(Path(directory).iterdir()):
        # The descriptor-based no-follow read in ``_read_evidence_file``
        # opens with O_NOFOLLOW and rejects a symlink descriptor before any
        # byte is read. The lstat here is retained as a pre-filter so the
        # classified scan records symlink/non-regular/unexpected entries in
        # the report (rather than only rejecting at read time).
        try:
            st = os.lstat(path)
        except OSError:
            raise AuthorizationError("evidence_file_unreadable")
        if _statmod.S_ISLNK(st.st_mode):
            _record_leak(path.name, "symlink_evidence_file")
            continue
        if not _statmod.S_ISREG(st.st_mode):
            _record_leak(path.name, "nonregular_evidence_file")
            continue
        if expected_files is not None and path.name not in expected_files:
            _record_leak(path.name, "unexpected_evidence_file")
            continue
        # Fail-closed read: bounded bytes, strict UTF-8, size caps.
        text, aggregate_used = _read_evidence_file(
            path, expected_basename=path.name, aggregate_used=aggregate_used,
        )
        lowered = text.lower()
        for token in SECURITY_MARKER_TOKENS:
            if token.lower() in lowered:
                marker_hits.append({"file": path.name, "token": token})

        # EXACT bare credential value match. A bare credential value under
        # an unrelated JSON property, inside ordinary prose, or with no
        # ``B2_`` / ``secret`` marker must still be detected.
        if exact_key_id and len(exact_key_id) >= 4 and exact_key_id in text:
            _record_leak(path.name, "bare_credential_value")
        if exact_app_key and len(exact_app_key) >= 4 and exact_app_key in text:
            _record_leak(path.name, "bare_credential_value")
        # Raw bucket identity exact match.
        if bucket_sentinel and len(bucket_sentinel) >= 4 and bucket_sentinel in text:
            _record_leak(path.name, "raw_bucket_identity")
        # Object byte sentinels.
        for chunk in object_sentinel_substrings:
            if chunk and chunk in text:
                _record_leak(path.name, "object_byte_sentinel")
                break
        # Credential assignments.
        if _CREDENTIAL_ASSIGNMENT_RE.search(text):
            _record_leak(path.name, "credential_assignment")
        # Signed / presigned URL query parameters.
        if _SIGNED_URL_QUERY_RE.search(text):
            _record_leak(path.name, "signed_url_query")
        # Authorization / Bearer headers.
        if _AUTH_HEADER_RE.search(text):
            _record_leak(path.name, "auth_header")
        # Credential-bearing database URLs.
        if _DB_URL_CRED_RE.search(text):
            _record_leak(path.name, "db_url_with_credentials")
        # Unexpected http(s) URLs. The evidence deliberately carries no URLs.
        if _HTTP_URL_RE.search(text):
            _record_leak(path.name, "unexpected_http_url")

    return {
        "marker_reference_hits": marker_hits,
        "real_value_leaks": real_leaks,
        "marker_reference_count": len(marker_hits),
        "real_value_leak_count": len(real_leaks),
        "category_counts": category_counts,
        "claim": (
            "expected marker references classified separately from values; "
            "real_value_leak_count must be zero before atomic finalization; "
            "exact credential values (key id, application key) are matched "
            "even without a credential-like field name; the sensitive "
            "comparison values are never serialized and are dropped after "
            "scanning"
        ),
    }


def _write_security_scan(directory: Path, scan: dict[str, Any]) -> None:
    """Write the classified security scan as a stable text artifact.

    Never serializes the sensitive comparison values; only file names, token
    names and per-category counts appear in the output.
    """
    lines: list[str] = [
        "PS-041E2-B live evidence — classified security scan",
        "",
        f"marker_reference_count: {scan['marker_reference_count']}",
        f"real_value_leak_count: {scan['real_value_leak_count']}",
        "",
        "Claim:",
        scan["claim"],
        "",
        "Per-category leak counts (sensitive values never serialized):",
    ]
    for category, count in sorted(scan.get("category_counts", {}).items()):
        lines.append(f"  - {category}: {count}")
    lines.extend([
        "",
        "Marker references (expected; classified separately from values):",
    ])
    for hit in scan["marker_reference_hits"]:
        lines.append(f"  - {hit['file']}: {hit['token']}")
    if not scan["marker_reference_hits"]:
        lines.append("  (none)")
    lines.extend([
        "",
        "Real value leaks (file + category only; values never serialized):",
    ])
    for hit in scan["real_value_leaks"]:
        lines.append(f"  - {hit['file']}: {hit['category']}")
    if not scan["real_value_leaks"]:
        lines.append("  (none)")
    lines.extend([
        "",
        "Post-write final scan coverage:",
        "  The pre-final (classified) scan recorded above passed. This",
        "  artifact and every finalized byte in the evidence directory are",
        "  covered by the subsequent strict post-write final scan whose",
        "  result is retained only in the in-memory LiveExecuteReport.",
    ])
    out_path = Path(directory) / "classified-security-scan.txt"
    _track_evidence_write(out_path)
    out_path.write_text(
        "\n".join(lines) + "\n", encoding="utf-8",
    )


def _write_known_limitations(directory: Path) -> None:
    """Write the known limitations artifact."""
    text = (
        "PS-041E2-B Phase-1 known limitations\n"
        "\n"
        "- Phase-1 implements the live executor. The fake-backend tests and\n"
        "  smokes perform zero live B2 access. The only path that may touch\n"
        "  live B2 is the real CLI ``--execute`` mode after every gate has\n"
        "  passed and only when the local HEAD equals the current remote\n"
        "  ``refs/heads/accepted/proofstudio``.\n"
        "- The CLI ``--execute`` mode confines the evidence output root to\n"
        "  exactly /tmp/proofstudio-ps041e2-live-evidence; a custom\n"
        "  evidence directory is available only through direct dependency\n"
        "  injection in tests.\n"
        "- Authorization expiry is checked against the system clock; clock\n"
        "  skew affects the check (a 60-second future tolerance is allowed).\n"
        "- The live authorization document is a control document only; it\n"
        "  does not enforce server-side bucket policy or application-key\n"
        "  capability. The operator must verify the application key is\n"
        "  restricted to the intended bucket/prefix and read-only.\n"
        "- Import durability is process-local to the ProofStudioService\n"
        "  instance used by the run; restart/multi-worker durability is not\n"
        "  claimed. The import service boundary is the accepted PS-041D\n"
        "  ProofStudioService.import_genblaze_bundle / get_imported_bundle /\n"
        "  get_imported_passport triple.\n"
        "- Hash verification records ``matched`` against an independently\n"
        "  expected digest, or ``observed`` / ``computed`` when no expected\n"
        "  digest is provided; it does not prove remote storage integrity,\n"
        "  Object Lock, or tamper-proof storage.\n"
        "- SDK invocation counts are distinct from actual HTTP attempts.\n"
        "  Successful responses contribute 1 + RetryAttempts; live_b2_calls\n"
        "  is the four HTTP-attempt counters' sum for real execution.\n"
        "- Evidence file reading is strictly fail-closed: every file must be\n"
        "  a regular non-symlink UTF-8 text file within per-file and\n"
        "  aggregate byte caps; invalid UTF-8, unreadable files, short reads\n"
        "  and oversized files prevent finalization.\n"
        "- ``version_id`` is observed only when the backend genuinely\n"
        "  supplies one. The pinned genblaze-s3 ``ObjectMetadata`` does not\n"
        "  expose ``version_id``; that absence is recorded as\n"
        "  ``version_id_observed=false`` and never fabricated.\n"
    )
    out_path = Path(directory) / "known-limitations.txt"
    _track_evidence_write(out_path)
    out_path.write_text(text, encoding="utf-8")

def execute(
    auth_path: Path, *, evidence_dir: Path,
    confirm_controlled_live_read: bool = False,
) -> int:
    """CLI entry point for live execution.

    Loads the live authorization, resolves real Git state (including the
    current remote ``refs/heads/accepted/proofstudio``), real server-side
    configuration (no implicit defaults), and the accepted backend factory,
    and invokes ``run_live_execute``. The evidence output root is validated
    by ``_validate_evidence_base`` BEFORE any output directory is created or
    inspected: arbitrary ``--evidence-out`` values are rejected rather than
    silently ignored; the resolved base must equal exactly
    ``LIVE_EVIDENCE_DIR``, must not be a symlink, and must have no symlink
    component. Because no live execution is permitted from an unaccepted
    commit, the gate-21 check (HEAD equals local and remote
    ``refs/heads/accepted/proofstudio``) refuses unless the PS-041E2-B
    implementation commit is officially accepted. From any feature branch
    the function prints a fail-closed message and returns exit code 2
    without ever reading a credential value, constructing a live backend,
    accessing the network, or writing evidence.

    An :class:`EnvAccessBoundary` (``RealEnvAccessBoundary``) is constructed
    before any pre-gate check runs and is shared by the server-config
    resolver and the credential provider. The boundary exposes
    key-membership checks for ``B2_KEY_ID`` / ``B2_APP_KEY`` (snapshot of
    ``os.environ.keys()`` at construction time — never invokes ``get`` /
    ``__getitem__`` on a secret name). Secret values may be read only
    through ``read_secret_after_gates``, and only after the executor has
    marked all 22 gates complete. No global monkeypatch is applied.
    """
    try:
        auth = load_live_authorization(auth_path)
    except AuthorizationError as exc:
        print(f"PS-041E2-B execute mode: refusing to run ({exc.code}).", file=sys.stderr)
        _print_fail_closed_help()
        return 2

    # Validate the evidence output root BEFORE creating or inspecting any
    # output directory. Arbitrary --evidence-out values are rejected here
    # rather than silently rewritten. The resolved base must equal exactly
    # LIVE_EVIDENCE_DIR, must not be a symlink, and must have no symlink
    # component. Custom temporary output roots remain available only through
    # direct fake dependency injection in tests (run_live_execute).
    try:
        _validate_evidence_base(Path(evidence_dir))
    except AuthorizationError as exc:
        print(f"PS-041E2-B execute mode: refusing to run ({exc.code}).", file=sys.stderr)
        _print_fail_closed_help()
        return 2

    # Construct the env-access boundary. Snapshots os.environ.keys() once
    # so subsequent secret_name_present checks use key membership only;
    # never invokes get/getitem on a secret name. No global monkeypatch.
    env_boundary = RealEnvAccessBoundary()

    git_state = _resolve_real_git_state()
    server_config = _resolve_real_server_config(env_access=env_boundary)
    credential_provider = _RealCredentialProvider(env_access=env_boundary)
    backend_factory = _RealBackendFactory()
    remote_ref_resolver = _RealRemoteRefResolver()
    # Construct a fresh in-process ProofStudioService. No real FastAPI app,
    # no real database, no network. Used only for the accepted PS-041D
    # import + readback + passport boundary.
    from proofstudio.api.services import ProofStudioService
    import_service = ProofStudioService()

    try:
        report = run_live_execute(
            auth,
            fixture_path=Path(__file__).resolve().parent.parent / "tests/fixtures/ps041d/genblaze-multi-provider-bundle-v1.json",
            evidence_dir=Path(evidence_dir),
            git_state=git_state,
            server_config=server_config,
            credential_provider=credential_provider,
            backend_factory=backend_factory,
            import_service=import_service,
            remote_ref_resolver=remote_ref_resolver,
            confirm_controlled_live_read=confirm_controlled_live_read,
            real_backend_factory_used=True,
            env_access=env_boundary,
        )
    except AuthorizationError as exc:
        print(f"PS-041E2-B execute mode: refusing to run ({exc.code}).", file=sys.stderr)
        _print_fail_closed_help()
        return 2

    if not report.ok:
        print(f"PS-041E2-B execute mode: failed ({','.join(report.errors)}).", file=sys.stderr)
        _print_fail_closed_help()
        return 2

    print(json.dumps({
        "ok": True,
        "slice": "PS-041E2-B",
        "mode": "live-executor",
        "evidence_run_id": report.evidence_run_id,
        "evidence_dir": report.evidence_dir,
        "head_calls_total": report.head_calls_total,
        "read_calls_total": report.read_calls_total,
        "head_object_sdk_calls": report.head_object_sdk_calls,
        "ranged_get_object_sdk_calls": report.ranged_get_object_sdk_calls,
        "head_object_http_attempts": report.head_object_http_attempts,
        "ranged_get_object_http_attempts": report.ranged_get_object_http_attempts,
        "head_bucket_http_attempts": report.head_bucket_http_attempts,
        "regional_probe_http_attempts": report.regional_probe_http_attempts,
        "live_b2_calls": report.live_b2_calls,
        "real_backend_factory_used": report.real_backend_factory_used,
        "import_service_used": report.import_service_used,
    }, indent=2, sort_keys=True))
    return 0


def _print_fail_closed_help() -> None:
    """Print the canonical 22-gate fail-closed help text."""
    print("", file=sys.stderr)
    print(
        f"Required gates ({FUTURE_EXECUTE_GATES_COUNT}, all must pass before "
        f"client construction):",
        file=sys.stderr,
    )
    for gate in _execute_gates():
        print(f"  - {gate}", file=sys.stderr)
    print("", file=sys.stderr)
    print(
        "No B2 credential value is read before every authorization and Git "
        "binding check passes. No B2 client is constructed before all 22 "
        "gates pass. The local HEAD must equal the current remote "
        "refs/heads/accepted/proofstudio (gate 21 performs one bounded "
        "git ls-remote lookup; tests inject the remote resolver and "
        "perform no network).",
        file=sys.stderr,
    )


DETACHED_HEAD_MARKER = "(detached)"


@dataclass(frozen=True)
class GitCommandResult:
    """Structured result of a single Git subprocess command.

    Carries whether the command succeeded, the captured stdout, and a
    stable normalized error code (empty on success). Raw subprocess stderr
    is NEVER printed or carried: only a stable error code surfaces.
    """

    succeeded: bool
    stdout: str
    error_code: str


class GitCommandRunner(Protocol):
    """Callable that runs one Git command and returns a structured result."""

    def __call__(self, args: list[str], *, timeout: float) -> GitCommandResult: ...


def _proofstudio_root() -> Path:
    """Derive the ProofStudio repository root from this script's location.

    Every local Git command and every ``git ls-remote`` invocation is pinned
    to this root via an explicit ``cwd`` so the executor never depends on
    the shell's current working directory. A caller invoking the executor
    from another Git repository, or from outside any repository, still
    binds the ProofStudio repository.
    """
    return Path(__file__).resolve().parent.parent


def _run_git_command(
    args: list[str], *, timeout: float = 2.0,
) -> GitCommandResult:
    """Run one ``git`` command pinned to the ProofStudio repository root.

    The ``cwd`` is unconditionally :func:`_proofstudio_root`; callers cannot
    override it. The command therefore always binds the ProofStudio
    repository regardless of the shell's current working directory.

    Returns a normalized error code on every failure path (non-zero exit,
    OSError, SubprocessError, TimeoutExpired). Raw subprocess stderr is
    captured and discarded; only the stable code surfaces. The bounded
    default timeout is two seconds for local commands and five seconds
    for the remote-ref lookup (enforced by the caller).
    """
    import subprocess
    resolved_cwd = str(_proofstudio_root())
    try:
        result = subprocess.run(
            ["git", *args], capture_output=True, text=True,
            timeout=timeout, check=False, cwd=resolved_cwd,
        )
    except subprocess.TimeoutExpired:
        return GitCommandResult(False, "", "git_command_timeout")
    except (OSError, subprocess.SubprocessError):
        return GitCommandResult(False, "", "git_command_failed")
    if result.returncode != 0:
        return GitCommandResult(False, "", "git_command_nonzero_exit")
    return GitCommandResult(True, result.stdout or "", "")


def _resolve_real_git_state(
    *, runner: "GitCommandRunner | None" = None,
) -> GitState:
    """Resolve the real repository Git state via ``git`` subprocess.

    Reads only the branch, HEAD commit, accepted-ref commit, and tree-clean
    status. Never reads or prints credential-bearing files. The remote
    accepted commit is resolved separately by :class:`_RealRemoteRefResolver`
    so the gate can compare HEAD against both the local and remote ref.

    Fail-closed behavior:

    - A failed ``git status`` command (non-zero exit, OSError, or timeout)
      MUST NOT become ``tree_clean=true``. The status result is consulted
      first; on any failure ``tree_clean`` is false and the executor
      rejects at gate 20.
    - A failed ``git rev-parse HEAD`` yields an empty head commit; the
      executor rejects at gate 21.
    - A malformed commit (non-hex40) is normalized to empty; the executor
      rejects at gate 21.
    - A detached HEAD (``git rev-parse --abbrev-ref HEAD`` returns
      ``HEAD`` or a 40-hex commit) is normalized to the exact
      ``DETACHED_HEAD_MARKER`` so the executor gate 21 accepts it.
    - Raw subprocess stderr is never printed; only stable error codes
      surface.
    """
    run = runner or _run_git_command
    branch_result = run(["rev-parse", "--abbrev-ref", "HEAD"], timeout=2.0)
    head_result = run(["rev-parse", "HEAD"], timeout=2.0)
    accepted_result = run(["rev-parse", ACCEPTED_EXECUTION_REF], timeout=2.0)
    status_result = run(["status", "--porcelain"], timeout=2.0)

    # Branch normalization: detached HEAD (literally "HEAD" or a hex40
    # commit returned by some git versions) becomes the exact detached
    # marker so gate 21 accepts it. A failed branch command yields "".
    if not branch_result.succeeded:
        branch = ""
    else:
        raw_branch = branch_result.stdout.strip()
        if raw_branch == "HEAD":
            branch = DETACHED_HEAD_MARKER
        elif _HEX40.match(raw_branch):
            branch = DETACHED_HEAD_MARKER
        else:
            branch = raw_branch

    # HEAD / accepted normalization: hex40 required, else empty.
    head_commit = ""
    if head_result.succeeded:
        candidate = head_result.stdout.strip().lower()
        if _HEX40.match(candidate):
            head_commit = candidate
    accepted_commit = ""
    if accepted_result.succeeded:
        candidate = accepted_result.stdout.strip().lower()
        if _HEX40.match(candidate):
            accepted_commit = candidate

    # CRITICAL: a failed status command MUST NOT become tree_clean=true.
    if not status_result.succeeded:
        tree_clean = False
    else:
        tree_clean = (status_result.stdout.strip() == "")

    return GitState(
        branch=branch, head_commit=head_commit,
        accepted_commit=accepted_commit, accepted_ref=ACCEPTED_EXECUTION_REF,
        tree_clean=tree_clean,
    )


@dataclass
class _RealRemoteRefResolver:
    """Resolve the remote accepted ref via a bounded ``git ls-remote``.

    Fails closed (returns the empty string) when the remote cannot be
    reached, the ref does not exist, or the subprocess times out. Exposes a
    ``call_count`` so tests and the security review can prove the resolver
    ran exactly once before credential retrieval.
    """

    call_count: int = 0

    def __call__(self, ref: str) -> str:
        self.call_count += 1
        import subprocess
        # ``ref`` is e.g. ``origin/accepted/proofstudio``; ls-remote wants the
        # ``refs/heads/accepted/proofstudio`` form on the remote.
        remote_ref = ref
        if remote_ref.startswith("origin/"):
            remote_ref = "refs/heads/" + remote_ref[len("origin/"):]
        # Pin the command to the ProofStudio repository root derived from
        # this script's location so the resolver never depends on the
        # shell's current working directory.
        resolved_cwd = str(_proofstudio_root())
        try:
            result = subprocess.run(
                ["git", "ls-remote", "origin", remote_ref],
                capture_output=True, text=True, timeout=5.0, check=False,
                cwd=resolved_cwd,
            )
        except (OSError, subprocess.SubprocessError):
            return ""
        if result.returncode != 0:
            return ""
        line = (result.stdout or "").strip().splitlines()
        if not line:
            return ""
        parts = line[0].split(None, 1)
        if len(parts) != 2:
            return ""
        commit = parts[0].strip().lower()
        if not _HEX40.match(commit):
            return ""
        return commit


def _resolve_real_server_config(
    env_access: "EnvAccessBoundary | None" = None,
) -> ServerConfig:
    """Resolve the real server-side B2 configuration.

    Reads the canonical bucket alias and import root from their explicit
    environment variables, and the bucket identity and region from theirs.
    All four are required for live execution; there is no implicit default.
    The credential *presence* is summarized via KEY-MEMBERSHIP checks only
    through the injectable :class:`EnvAccessBoundary`; the secret values
    are never read here. The boundary's ``secret_name_present`` inspects
    the environment-key snapshot only and never invokes ``get`` /
    ``__getitem__`` for ``B2_KEY_ID`` or ``B2_APP_KEY``.
    """
    boundary = env_access or RealEnvAccessBoundary()
    alias = boundary.read_non_secret("PROOFSTUDIO_IMPORT_BUCKET_ALIAS")
    import_root = boundary.read_non_secret("PROOFSTUDIO_IMPORT_ROOT")
    bucket_identity = boundary.read_non_secret("B2_BUCKET")
    region = boundary.read_non_secret("B2_REGION")
    # Key-membership-only check for the two secret env names. Never reads
    # values; the boundary implementation uses a captured key-set snapshot.
    required = (
        boundary.secret_name_present("B2_KEY_ID")
        and boundary.secret_name_present("B2_APP_KEY")
        and bool(alias) and bool(import_root)
        and bool(bucket_identity) and bool(region)
    )
    return ServerConfig(
        alias=alias,
        import_root=import_root,
        bucket_identity=bucket_identity,
        region=region,
        required_credentials_present=required,
    )


# Accepted live B2 credential environment-variable names (names only).
# Mirrors ``proofstudio.api.live_bridge.B2_REQUIRED_ENV``. The executor never
# reads these values into Python objects longer than necessary and never
# prints them. The two names in :data:`SECRET_VALUE_ENV` are the secret
# values; the other two are non-secret configuration that may be read
# pre-gate.
LIVE_B2_REQUIRED_ENV: tuple[str, ...] = (
    "B2_KEY_ID",
    "B2_APP_KEY",
    "B2_BUCKET",
    "B2_REGION",
)


@dataclass
class _RealCredentialProvider:
    """Reads the accepted server-side B2 credentials from the environment.

    Only invoked after every gate has passed. The values live only inside
    the resulting ``LiveCredentials`` dataclass, which is consumed by the
    backend factory and then released by the executor cleanup step. The
    provider validates that the key id and app key are nonempty; an empty
    credential value raises ``AuthorizationError("credential_value_empty")``
    so the executor never builds a backend with missing credentials. Exposes
    a ``call_count`` so tests and the security review can prove it was not
    called before all gates passed.

    This is the ONLY component permitted to read secret values; it reads
    them through the injectable :class:`EnvAccessBoundary`
    (``read_secret_after_gates``), which raises immediately if called
    before the executor has marked all 22 gates complete.
    """

    env_access: "EnvAccessBoundary"
    call_count: int = 0

    def __call__(self) -> LiveCredentials:
        self.call_count += 1
        key_id = self.env_access.read_secret_after_gates("B2_KEY_ID")
        app_key = self.env_access.read_secret_after_gates("B2_APP_KEY")
        bucket = self.env_access.read_non_secret("B2_BUCKET")
        region = self.env_access.read_non_secret("B2_REGION")
        creds = LiveCredentials(
            key_id=key_id, app_key=app_key,
            bucket=bucket, region=region,
        )
        if not creds.key_id or not creds.app_key:
            raise AuthorizationError("credential_value_empty")
        if not creds.bucket or not creds.region:
            raise AuthorizationError("credential_value_empty")
        return creds


@dataclass
class _RealBackendFactory:
    """Constructs the accepted ``S3StorageBackend.for_backblaze`` backend.

    Only invoked after every gate has passed and after the credential
    provider has returned. Exposes a ``call_count`` so tests and the security
    review can prove no real client was constructed in any test path. The
    factory wraps the underlying backend in a :class:`GuardedLiveBackend`
    adapter so every underlying remote operation is represented in the
    adapter's counters.
    """

    call_count: int = 0

    def __call__(self, credentials: LiveCredentials) -> Any:
        self.call_count += 1
        # Local import so test collection never imports ``genblaze_s3`` and
        # never constructs a real boto3 client. This factory is only invoked
        # by the CLI ``--execute`` path, never by tests.
        from proofstudio.provenance.genblaze_store import (
            build_backblaze_backend, build_exact_key_read_adapter,
        )
        backend = build_backblaze_backend(
            bucket=credentials.bucket,
            region=credentials.region,
            key_id=credentials.key_id,
            app_key=credentials.app_key,
            auto_lifecycle=False,
            # preflight=False defers the lazy bucket-region preflight to the
            # first I/O call. The ExactKeyReadAdapter then bypasses that
            # lazy preflight entirely, issuing only exact-key HeadObject and
            # ranged GetObject through the pinned boto3 client.
            preflight=False,
        )
        # Ownership is explicit from the instant the raw backend exists.
        # After adapter construction the adapter owns the raw backend; after
        # wrapper construction the returned GuardedLiveBackend owns the
        # adapter. Every pre-return failure closes the current owner once.
        owned: Any = backend
        try:
            adapter = build_exact_key_read_adapter(backend)
            owned = adapter
            guarded = GuardedLiveBackend(adapter)
            owned = None
            return guarded
        except Exception as exc:
            close_method = getattr(owned, "close", None)
            try:
                if not callable(close_method):
                    raise RuntimeError("close unavailable")
                close_method()
            except Exception:
                raise AuthorizationError("backend_factory_cleanup_failed") from None
            if isinstance(exc, AuthorizationError):
                raise
            code = getattr(exc, "code", "")
            if isinstance(code, str) and re.fullmatch(r"[a-z0-9_]+", code):
                raise AuthorizationError(code) from None
            raise AuthorizationError("backend_factory_construction_failed") from None


def _execute_gates() -> list[str]:
    """Return the canonical execution-gate list.

    Always returns the canonical ``FUTURE_EXECUTE_GATES`` constant. No
    separately maintained list may drift from this source of truth.
    """
    return list(FUTURE_EXECUTE_GATES)


# ---------------------------------------------------------------------------
# CLI modes
# ---------------------------------------------------------------------------

def _mode_check_readiness() -> int:
    summary = {
        "slice": "PS-041E2-A",
        "mode": "check-readiness",
        "schema": SCHEMA,
        "purpose": PURPOSE,
        "passport_schema": PASSPORT_SCHEMA,
        "accepted_reader": "BoundedB2ImportReader",
        "accepted_backend_protocol": "B2Backend",
        "accepted_alias_env": "PROOFSTUDIO_IMPORT_BUCKET_ALIAS",
        "accepted_root_env": "PROOFSTUDIO_IMPORT_ROOT",
        "accepted_hard_upper_bounds": {
            "max_object_count": ACCEPTED_MAX_OBJECT_COUNT,
            "max_json_object_bytes": ACCEPTED_MAX_JSON_OBJECT_BYTES,
            "max_media_object_bytes": ACCEPTED_MAX_MEDIA_OBJECT_BYTES,
            "max_aggregate_bytes": ACCEPTED_MAX_AGGREGATE_BYTES,
        },
        "known_roles": sorted(KNOWN_ROLES),
        "required_unique_roles": list(REQUIRED_UNIQUE_ROLES),
        "json_read_roles": sorted(JSON_READ_ROLES),
        "media_byte_roles": sorted(MEDIA_BYTE_ROLES),
        "reserved_roles": sorted(RESERVED_ROLES),
        "supported_roles": sorted(SUPPORTED_ROLES),
        "authorization_window_seconds": MAX_AUTH_WINDOW_SECONDS,
        "denied_capabilities": list(DENIED_CAPABILITY_FIELDS),
        "abort_conditions": _abort_conditions(),
        "future_execute_gates": list(FUTURE_EXECUTE_GATES),
        "future_execute_gates_count": FUTURE_EXECUTE_GATES_COUNT,
        "live_execute_gates_count": LIVE_EXECUTE_GATES_COUNT,
        "live_execute_implemented": True,
        "live_execute_supported": True,
        "live_execute_schema": LIVE_SCHEMA,
        "live_execute_purpose": LIVE_PURPOSE,
        "live_authorization_dir": LIVE_AUTHORIZATION_DIR,
        "live_evidence_dir": LIVE_EVIDENCE_DIR,
        "accepted_live_backend": "proofstudio.provenance.genblaze_store.build_backblaze_backend",
        "accepted_live_credential_env_names": list(LIVE_B2_REQUIRED_ENV),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def _abort_conditions() -> list[str]:
    return [
        "A1 authorization absent/malformed/expired/forbidden-path",
        "A2 alias mismatch (compared against independently resolved server alias)",
        "A3 bucket identity mismatch (compared against SHA-256 of server bucket)",
        "A4 prefix not canonical (empty/root/leading-or-trailing-slash/whitespace/unsafe)",
        "A5 object count exceeds accepted cap",
        "A6 object outside approved prefix",
        "A7 key not explicitly allowlisted (rejected before backend call)",
        "A8 object exceeds per-object byte cap",
        "A9 total bytes exceed accepted cap",
        "A10 credential/token/signed URL in output",
        "A11 write/delete/copy attempted",
        "A12 production/personal/unexpected data observed",
        "A13 JSON malformed or violates nesting/size boundary",
        "A14 provider call occurred",
        "A15 unexpected hash mismatch (expected_sha256_by_key mismatch)",
        "A16 object metadata changed between observations",
        "A17 source schema differs from approved schema",
        "A18 browser receives raw B2 URL or credential field",
        "A19 repository branch/commit/tree state differs",
        "A20 evidence output fails final secret scan",
    ]


def _mode_validate_authorization(path: Path) -> int:
    try:
        auth = load_authorization(path)
        validate_authorization(auth, execute_mode=False)
    except AuthorizationError as exc:
        print(json.dumps({"ok": False, "code": exc.code}, sort_keys=True))
        return 1
    print(json.dumps({"ok": True, "code": "ok"}, sort_keys=True))
    return 0


def _mode_dry_run(path: Path, evidence_dir: Path) -> int:
    fixture = Path(__file__).resolve().parent.parent / "tests/fixtures/ps041d/genblaze-multi-provider-bundle-v1.json"
    try:
        auth = load_authorization(path)
        report = run_dry_run(auth, fixture_path=fixture)
    except AuthorizationError as exc:
        print(json.dumps({"ok": False, "mode": "fake-storage-dry-run", "code": exc.code}, sort_keys=True))
        return 1
    except ImportValidationError as exc:
        print(json.dumps({"ok": False, "mode": "fake-storage-dry-run", "code": exc.code}, sort_keys=True))
        return 1
    payload = {
        "ok": report.ok,
        "mode": "fake-storage-dry-run",
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
        "hash_results": report.hash_results,
        "observation_stable": report.observation_stable,
        "observation_comparisons": report.observation_comparisons,
        "import_created": report.import_created,
        "import_idempotent": report.import_idempotent,
        "passport_schema": report.passport_schema,
        "bundle_id": report.bundle_id,
        "alias_comparison_code": report.alias_comparison_code,
        "bucket_comparison_code": report.bucket_comparison_code,
        "role_plan": report.role_plan,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if report.ok else 1


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PS-041E2-A B2 evidence readiness validator")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check-readiness", action="store_true")
    group.add_argument("--validate-authorization", metavar="PATH")
    group.add_argument("--dry-run", metavar="AUTH_PATH")
    group.add_argument("--execute", metavar="AUTH_PATH")
    parser.add_argument("--evidence-out", default=DEFAULT_EVIDENCE_DIR,
                        help="directory for sanitized evidence output (default: %(default)s)")
    parser.add_argument("--confirm-controlled-live-read", action="store_true",
                        help="explicit confirmation flag required by a future live execute mode")
    args = parser.parse_args(argv)

    if args.check_readiness:
        return _mode_check_readiness()
    if args.validate_authorization:
        return _mode_validate_authorization(Path(args.validate_authorization))
    if args.dry_run:
        return _mode_dry_run(Path(args.dry_run), Path(args.evidence_out))
    if args.execute:
        return execute(Path(args.execute), evidence_dir=Path(args.evidence_out),
                       confirm_controlled_live_read=args.confirm_controlled_live_read)
    parser.error("no mode selected")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
