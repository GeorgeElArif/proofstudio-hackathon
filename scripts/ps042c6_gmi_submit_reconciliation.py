#!/usr/bin/env python3
"""PS-042C6 fail-closed GMI submit reconciliation and resume-only recovery.

Plan, self-test, and reconcile are offline. Resume is deliberately built around
an injected GET-only provider boundary: it has no path that can transmit POST.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import logging
import os
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
_C5_PATH = ROOT / "scripts" / "ps042c5_one_real_genblaze_proof.py"
_C5_SPEC = importlib.util.spec_from_file_location("ps042c6_c5_boundary", _C5_PATH)
if _C5_SPEC is None or _C5_SPEC.loader is None:
    raise RuntimeError("PS-042C5 boundary import unavailable")
c5 = importlib.util.module_from_spec(_C5_SPEC)
sys.modules[_C5_SPEC.name] = c5
_C5_SPEC.loader.exec_module(c5)


REQUIRED_BRANCH = "ps-042c0/free-render-staging-v1"
ORIGINAL_PROOF_ID = "d1b4e4640bb1d79ee158bf01617e0e17"
ORIGINAL_SUBMIT_REVISION = "ca3b2d1e0ba4cea3978b2ffe33ab25dff8acedb8"
FUNDED_PROOF_ID = "c252577563896fa8866963d3a3f95650"
FUNDED_SUBMIT_REVISION = "d19d1188a3f3c4c925b85859daf9f0d6153abf12"
FUNDED_AUTHORIZED_REQUEST_ID = "439b863f-d0e4-48d8-adfd-1e7912ac0534"
DEFAULT_ATTEMPT_LOCK = Path(
    "/home/george/.local/state/proofstudio/ps042c5-one-live-attempt.lock"
)
DEFAULT_FAILURE_RECEIPT = Path(
    "/tmp/proofstudio-ps042c5-execution/"
    f"{ORIGINAL_PROOF_ID}/failure-receipt.json"
)
ATTEMPT_LOCK_SHA256 = "6a8901647faf1c6a2cba1d2bd4698ee4b2e82738ea39a60d543a20a07e25bba8"
FAILURE_RECEIPT_SHA256 = "3be63e463727cf4f023b084d28a361e4600f3e2bff4af2b5ece29b07a74b10da"
FUNDED_ATTEMPT_LOCK = Path(
    "/home/george/.local/state/proofstudio/ps042c5-funded-live-attempt.lock"
)
FUNDED_FAILURE_RECEIPT = Path(
    "/tmp/proofstudio-ps042c5-execution/"
    f"{FUNDED_PROOF_ID}/failure-receipt.json"
)
FUNDED_ATTEMPT_LOCK_SHA256 = (
    "322b7ed94276e2f50094d8c5bb8e5e59f7b834f24e5fa8680d82644dbfef1a2d"
)
FUNDED_FAILURE_RECEIPT_SHA256 = (
    "fc38c2119eba2d04a301f9cd6fe4400a4330aa84b3ca39c333406e79cb853c9c"
)
RESUME_AUTHORIZATION_TOKEN = "AUTHORIZE_RESUME_EXISTING_GMI_REQUEST"
C9_CONTINUATION_AUTHORIZATION_TOKEN = "AUTHORIZE_B2_COMPATIBLE_CONTINUATION"
C9_PRIOR_RESUME_RECEIPT = Path(
    "/tmp/proofstudio-ps042c6-resume/"
    f"{FUNDED_PROOF_ID}/resume-receipt.json"
)
C9_PRIOR_RESUME_RECEIPT_SHA256 = (
    "aeba6b71544494d944a5ab83ff2114720ffaba748e7571cdc9061b941c352f85"
)
C9_DEFAULT_EXECUTION_LOCK = Path(
    "/home/george/.local/state/proofstudio/"
    "ps042c9-funded-b2-continuation.lock"
)
C9_LOCAL_RECEIPT_SCHEMA = "proofstudio.ps042c9.local-continuation-receipt.v1"
C9_VERIFICATION_RECEIPT_SCHEMA = "proofstudio.ps042c9.verification-receipt.v1"
C9_B2_WRITE_MODE = "plain-put-after-exact-absence-preflight"
C9_PROVIDER_STATUS_GET_LIMIT = 1
C9_ASSET_GET_LIMIT = 1
C9_B2_HEAD_LIMIT = 5
C9_B2_PUT_LIMIT = 5
C9_B2_GET_LIMIT = 5
MAX_ADDITIONAL_GENERATION_COST_USD = Decimal("0.00")
RESUME_GENERATION_POST_LIMIT = 0
RESUME_AUTOMATIC_RETRIES = 0
RESUME_FALLBACKS = 0
RESUME_PREFLIGHT = False
MAX_STATUS_GETS = 12
STATUS_POLL_INTERVAL_SECONDS = 5.0
# One URL-path segment: ASCII alphanumeric first, then documented safe punctuation.
REQUEST_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,199}")
GMI_STATUS_BASE_URL = "https://console.gmicloud.ai/api/v1/ie/requestqueue/apikey"
GMI_ASSET_HOST = "storage.googleapis.com"
PROOF_ID_PATTERN = re.compile(r"[0-9a-f]+")
REVISION_PATTERN = re.compile(r"[0-9a-f]{40}")
LOCAL_RECEIPT_SCHEMAS = frozenset(
    {
        c5.LOCAL_RECEIPT_SCHEMA,
        "proofstudio.ps042c5.local-execution-receipt.v2",
    }
)
SUBMIT_CLASSIFICATIONS = frozenset(
    {
        c5.ACCEPTED,
        c5.DEFINITIVE_PROVIDER_REJECTION,
        c5.AMBIGUOUS_PROVIDER_RESPONSE,
        c5.AMBIGUOUS_TRANSPORT_OUTCOME,
    }
)
PENDING_STATUSES = frozenset({"queued", "dispatched", "processing"})
TERMINAL_FAILURE_STATUSES = frozenset({"failed", "cancelled"})
SUCCESS_STATUS = "success"
REQUIRED_CREDENTIALS = c5.REQUIRED_CREDENTIALS
RESUME_RECEIPT_SCHEMA = "proofstudio.ps042c6.local-resume-receipt.v1"
COMPLETION_MARKER_SCHEMA = "proofstudio.ps042c6.completion-marker.v1"


class SafetyError(RuntimeError):
    """Safe, fail-closed validation or recovery error."""


class ResumeIncompleteError(SafetyError):
    """GET-only polling ended without a terminal result; later resume is safe."""


class ResumeTerminalError(SafetyError):
    """The existing request reached failed or cancelled."""

    def __init__(self, status: str):
        super().__init__(f"existing provider request reached {status}")
        self.status = status


class AssetDownloadError(SafetyError):
    """A failed asset response carrying only a safe, bounded diagnostic."""

    def __init__(self, message: str, diagnostic: Mapping[str, Any]):
        super().__init__(message)
        self.diagnostic = dict(diagnostic)


class B2CompatibilityError(SafetyError):
    """A B2 boundary failure carrying only an allowlisted diagnostic."""

    def __init__(self, message: str, diagnostic: Mapping[str, Any]):
        super().__init__(message)
        self.diagnostic = dict(diagnostic)


@dataclass(frozen=True)
class AttemptProfile:
    name: str
    proof_id: str
    submit_revision: str
    attempt_lock_path: Path
    attempt_lock_sha256: str
    failure_receipt_path: Path
    failure_receipt_sha256: str
    accepted_lock_field_set: frozenset[str]
    required_cost_ceiling: Decimal
    generation_submit_limit: int


ORIGINAL_AMBIGUOUS_ATTEMPT = AttemptProfile(
    name="ORIGINAL_AMBIGUOUS_ATTEMPT",
    proof_id=ORIGINAL_PROOF_ID,
    submit_revision=ORIGINAL_SUBMIT_REVISION,
    attempt_lock_path=DEFAULT_ATTEMPT_LOCK,
    attempt_lock_sha256=ATTEMPT_LOCK_SHA256,
    failure_receipt_path=DEFAULT_FAILURE_RECEIPT,
    failure_receipt_sha256=FAILURE_RECEIPT_SHA256,
    accepted_lock_field_set=frozenset(
        {
            "authorized_at_utc",
            "branch",
            "revision",
            "maximum_cost_usd",
            "generation_submit_limit",
        }
    ),
    required_cost_ceiling=Decimal("0.05"),
    generation_submit_limit=1,
)
FUNDED_ACCEPTED_ATTEMPT = AttemptProfile(
    name="FUNDED_ACCEPTED_ATTEMPT",
    proof_id=FUNDED_PROOF_ID,
    submit_revision=FUNDED_SUBMIT_REVISION,
    attempt_lock_path=FUNDED_ATTEMPT_LOCK,
    attempt_lock_sha256=FUNDED_ATTEMPT_LOCK_SHA256,
    failure_receipt_path=FUNDED_FAILURE_RECEIPT,
    failure_receipt_sha256=FUNDED_FAILURE_RECEIPT_SHA256,
    accepted_lock_field_set=frozenset(
        {
            "authorized_at_utc",
            "branch",
            "revision",
            "maximum_cost_usd",
            "expected_cost_usd",
            "generation_submit_limit",
        }
    ),
    required_cost_ceiling=Decimal("0.05"),
    generation_submit_limit=1,
)
ATTEMPT_PROFILES = {
    "original": ORIGINAL_AMBIGUOUS_ATTEMPT,
    "funded": FUNDED_ACCEPTED_ATTEMPT,
}
AUTHORIZED_RESUME_REQUEST_IDS = {
    FUNDED_ACCEPTED_ATTEMPT.name: FUNDED_AUTHORIZED_REQUEST_ID,
}
PROFILE_COUNTER_INVARIANTS = {
    ORIGINAL_AMBIGUOUS_ATTEMPT.name: {
        "generation_posts": 1,
        "status_poll_gets": 0,
        "asset_download_gets": 0,
        "b2_heads": 5,
        "b2_gets": 0,
        "b2_puts": 0,
        "other_network_methods": 0,
    },
    FUNDED_ACCEPTED_ATTEMPT.name: {
        "generation_posts": 1,
        "status_poll_gets": 1,
        "asset_download_gets": 1,
        "b2_heads": 5,
        "b2_gets": 0,
        "b2_puts": 0,
        "other_network_methods": 0,
    },
}


@dataclass(frozen=True)
class AttemptLock:
    branch: str
    revision: str
    maximum_cost_usd: Decimal
    generation_submit_limit: int
    sha256: str
    expected_cost_usd: Decimal | None = None


@dataclass(frozen=True)
class OriginalAttempt:
    proof_id: str
    counters: dict[str, int]
    successful_writes: tuple[str, ...]
    failed_key: str | None
    reason_code: str
    outer_exception_type: str
    submit_classification: str | None
    submit_diagnostic: Mapping[str, Any] | None
    second_post_forbidden: bool
    resume_possible: bool
    sha256: str = ""


@dataclass(frozen=True)
class PriorResumeAttempt:
    proof_id: str
    provider_request_id: str
    reason_code: str
    provider_status: str
    counters: dict[str, int]
    successful_writes: tuple[str, ...]
    combined_lineage: dict[str, Any]
    new_submit_authorized: bool
    sha256: str


@dataclass(frozen=True)
class ResumeRepoState:
    branch: str
    head: str
    origin: str
    clean: bool
    source_revision_is_ancestor: bool


@dataclass
class ResumeCounters:
    generation_posts: int = 0
    status_poll_gets: int = 0
    asset_download_gets: int = 0
    b2_heads: int = 0
    b2_gets: int = 0
    b2_puts: int = 0
    retries: int = 0
    fallbacks: int = 0
    other_network_methods: int = 0


class ResponseLike(Protocol):
    status_code: int
    headers: Mapping[str, str]
    content: bytes

    def json(self) -> Any: ...


class ProviderGetTransport(Protocol):
    def get(self, url: str, **kwargs: Any) -> ResponseLike: ...
    def close(self) -> None: ...


class B2Transport(Protocol):
    def head_object(self, **kwargs: Any) -> Any: ...
    def put_object(self, **kwargs: Any) -> Any: ...
    def get_object(self, **kwargs: Any) -> Any: ...
    def close(self) -> None: ...


@dataclass
class ResumeDependencies:
    repo_state: Callable[[str], ResumeRepoState]
    provider_transport: Callable[[Mapping[str, str]], ProviderGetTransport]
    b2_transport: Callable[[Mapping[str, str]], B2Transport]
    now: Callable[[], datetime] = lambda: datetime.now(timezone.utc)
    sleep: Callable[[float], None] = time.sleep
    local_receipt_root: Path = field(
        default_factory=lambda: Path(tempfile.gettempdir()) / "proofstudio-ps042c6-resume"
    )
    completion_root: Path = field(
        default_factory=lambda: Path(tempfile.gettempdir()) / "proofstudio-ps042c6-completion"
    )


@dataclass
class ContinuationDependencies:
    repo_state: Callable[[str], ResumeRepoState]
    provider_transport: Callable[[Mapping[str, str]], ProviderGetTransport]
    b2_transport: Callable[[Mapping[str, str]], B2Transport]
    now: Callable[[], datetime] = lambda: datetime.now(timezone.utc)
    local_receipt_root: Path = field(
        default_factory=lambda: Path(tempfile.gettempdir())
        / "proofstudio-ps042c9-continuation"
    )
    completion_root: Path = field(
        default_factory=lambda: Path(tempfile.gettempdir())
        / "proofstudio-ps042c9-completion"
    )
    execution_lock: Path = field(default_factory=lambda: C9_DEFAULT_EXECUTION_LOCK)


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _require_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise SafetyError(f"{field_name} must be a non-negative integer")
    return value


def resolve_attempt_profile(value: str | AttemptProfile) -> AttemptProfile:
    if isinstance(value, AttemptProfile):
        if not any(value is profile for profile in ATTEMPT_PROFILES.values()):
            raise SafetyError("attempt profile is not recognized")
        return value
    try:
        return ATTEMPT_PROFILES[value]
    except (KeyError, TypeError) as exc:
        raise SafetyError("attempt profile must be original or funded") from exc


def credential_presence(env: Mapping[str, str]) -> dict[str, bool]:
    """Inspect names only; no credential value is read."""
    return {name: name in env for name in REQUIRED_CREDENTIALS}


def _load_json_object(path: Path) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise SafetyError("required local JSON file is missing or unreadable") from exc
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SafetyError("local receipt is not valid JSON") from exc
    if not isinstance(value, dict):
        raise SafetyError("local receipt must be a JSON object")
    return value, raw


def parse_failure_receipt(path: Path) -> OriginalAttempt:
    receipt, raw = _load_json_object(path)
    if receipt.get("schema") not in LOCAL_RECEIPT_SCHEMAS:
        raise SafetyError("unsupported failure receipt schema")
    proof_id = receipt.get("proof_id")
    if not isinstance(proof_id, str) or PROOF_ID_PATTERN.fullmatch(proof_id) is None:
        raise SafetyError("failure receipt proof ID must be lowercase hexadecimal")
    if receipt.get("complete_proof") is not False or receipt.get("status") != "incomplete":
        raise SafetyError("failure receipt does not describe an incomplete proof")
    counters_value = receipt.get("original_network_counters", receipt.get("network_counters"))
    if not isinstance(counters_value, Mapping):
        raise SafetyError("failure receipt network counters are missing")
    counter_names = (
        "generation_posts",
        "status_poll_gets",
        "asset_download_gets",
        "b2_heads",
        "b2_gets",
        "b2_puts",
        "other_network_methods",
    )
    counters = {
        name: _require_int(counters_value.get(name), f"network_counters.{name}")
        for name in counter_names
    }
    writes_value = receipt.get(
        "b2_keys_successfully_written", receipt.get("successfully_written_keys")
    )
    if not isinstance(writes_value, list) or any(
        not isinstance(key, str) for key in writes_value
    ):
        raise SafetyError("failure receipt successful-write list is malformed")
    failed_key = receipt.get("failed_b2_key", receipt.get("failed_key"))
    if failed_key is not None and not isinstance(failed_key, str):
        raise SafetyError("failure receipt failed key is malformed")
    reason = receipt.get("reason_code")
    if not isinstance(reason, str) or not reason:
        raise SafetyError("failure receipt reason code is malformed")
    outer = receipt.get("outer_exception_type", reason)
    if not isinstance(outer, str) or not outer:
        raise SafetyError("failure receipt outer exception type is malformed")
    classification = receipt.get("provider_submit_classification")
    if classification is not None and classification not in SUBMIT_CLASSIFICATIONS:
        raise SafetyError("failure receipt submit classification is unknown")
    diagnostic = receipt.get("provider_response_diagnostic")
    if diagnostic is not None:
        if not isinstance(diagnostic, Mapping):
            raise SafetyError("failure receipt provider diagnostic is malformed")
        if diagnostic.get("submit_classification") != classification:
            raise SafetyError("failure receipt provider classifications disagree")
    second_forbidden = receipt.get(
        "second_post_forbidden", counters["generation_posts"] >= 1
    )
    if not isinstance(second_forbidden, bool):
        raise SafetyError("failure receipt second-POST flag is malformed")
    resume_possible = receipt.get(
        "resume_by_known_request_id_may_be_possible",
        counters["generation_posts"] == 1
        and classification != c5.DEFINITIVE_PROVIDER_REJECTION,
    )
    if not isinstance(resume_possible, bool):
        raise SafetyError("failure receipt resume flag is malformed")
    return OriginalAttempt(
        proof_id=proof_id,
        counters=counters,
        successful_writes=tuple(writes_value),
        failed_key=failed_key,
        reason_code=reason,
        outer_exception_type=outer,
        submit_classification=classification,
        submit_diagnostic=diagnostic,
        second_post_forbidden=second_forbidden,
        resume_possible=resume_possible,
        sha256=_sha256(raw),
    )


def parse_prior_resume_receipt(
    path: Path,
    *,
    expected_path: Path = C9_PRIOR_RESUME_RECEIPT,
    expected_sha256: str = C9_PRIOR_RESUME_RECEIPT_SHA256,
) -> PriorResumeAttempt:
    """Validate the immutable first-resume failure used to authorize C9."""
    if path != expected_path:
        raise SafetyError("prior resume receipt path mismatch")
    receipt, raw = _load_json_object(path)
    digest = _sha256(raw)
    if digest != expected_sha256:
        raise SafetyError("prior resume receipt has been modified")
    if receipt.get("schema") != RESUME_RECEIPT_SCHEMA:
        raise SafetyError("prior resume receipt schema mismatch")
    proof_id = receipt.get("proof_id")
    request_id = receipt.get("provider_request_id")
    reason = receipt.get("reason_code")
    provider_status = receipt.get("provider_status")
    if proof_id != FUNDED_PROOF_ID:
        raise SafetyError("prior resume receipt proof ID mismatch")
    if request_id != FUNDED_AUTHORIZED_REQUEST_ID:
        raise SafetyError("prior resume receipt provider request ID mismatch")
    if reason != "SafetyError":
        raise SafetyError("prior resume receipt reason mismatch")
    if provider_status != SUCCESS_STATUS:
        raise SafetyError("prior resume receipt provider status mismatch")
    counters_value = receipt.get("resume_counters")
    expected_counters = {
        "generation_posts": 0,
        "status_poll_gets": 1,
        "asset_download_gets": 1,
        "b2_heads": 5,
        "b2_puts": 1,
        "b2_gets": 0,
        "retries": 0,
        "fallbacks": 0,
        "other_network_methods": 0,
    }
    if not isinstance(counters_value, Mapping):
        raise SafetyError("prior resume receipt counters are missing")
    counters = {
        name: _require_int(counters_value.get(name), f"resume_counters.{name}")
        for name in expected_counters
    }
    if set(counters_value) != set(expected_counters) or counters != expected_counters:
        raise SafetyError("prior resume receipt counter invariants mismatch")
    writes = receipt.get("successfully_written_keys")
    if not isinstance(writes, list) or any(not isinstance(key, str) for key in writes):
        raise SafetyError("prior resume receipt successful-write list is malformed")
    if writes:
        raise SafetyError("prior resume receipt evidences a successful B2 write")
    lineage = receipt.get("combined_proof_lineage")
    expected_lineage = {
        "proof_id": FUNDED_PROOF_ID,
        "original_submit_revision": FUNDED_SUBMIT_REVISION,
        "original_provider_posts": 1,
        "resume_provider_posts": 0,
        "total_provider_posts": 1,
    }
    if not isinstance(lineage, Mapping) or dict(lineage) != expected_lineage:
        raise SafetyError("prior resume receipt lineage mismatch")
    new_submit = receipt.get("new_submit_authorized")
    if new_submit is not False:
        raise SafetyError("prior resume receipt does not forbid a new submission")
    return PriorResumeAttempt(
        proof_id=proof_id,
        provider_request_id=request_id,
        reason_code=reason,
        provider_status=provider_status,
        counters=counters,
        successful_writes=tuple(writes),
        combined_lineage=dict(lineage),
        new_submit_authorized=new_submit,
        sha256=digest,
    )


def parse_attempt_lock(
    path: Path, attempt_profile: str | AttemptProfile | None = None
) -> AttemptLock:
    profile = (
        ORIGINAL_AMBIGUOUS_ATTEMPT
        if attempt_profile is None
        else resolve_attempt_profile(attempt_profile)
    )
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise SafetyError("attempt lock is missing or unreadable") from exc
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SafetyError("attempt lock is not UTF-8") from exc
    values: dict[str, str] = {}
    for line in text.splitlines():
        if not line or "=" not in line:
            raise SafetyError("attempt lock is malformed")
        key, value = line.split("=", 1)
        if key in values:
            raise SafetyError("attempt lock contains a duplicate field")
        values[key] = value
    if set(values) != profile.accepted_lock_field_set:
        raise SafetyError("attempt lock field set is malformed")
    if values["branch"] != REQUIRED_BRANCH:
        raise SafetyError("attempt lock branch mismatch")
    if values["revision"] != profile.submit_revision:
        raise SafetyError("attempt lock profile revision mismatch")
    try:
        maximum_cost = Decimal(values["maximum_cost_usd"])
        submit_limit = int(values["generation_submit_limit"])
        expected_cost = (
            Decimal(values["expected_cost_usd"])
            if "expected_cost_usd" in values
            else None
        )
    except Exception as exc:
        raise SafetyError("attempt lock numeric field is malformed") from exc
    if maximum_cost != profile.required_cost_ceiling:
        raise SafetyError("attempt lock cost ceiling mismatch")
    if submit_limit != profile.generation_submit_limit:
        raise SafetyError("attempt lock generation-submit limit mismatch")
    if profile is FUNDED_ACCEPTED_ATTEMPT and expected_cost != Decimal("0.035"):
        raise SafetyError("funded attempt lock expected cost mismatch")
    return AttemptLock(
        branch=values["branch"],
        revision=values["revision"],
        maximum_cost_usd=maximum_cost,
        generation_submit_limit=submit_limit,
        sha256=_sha256(raw),
        expected_cost_usd=expected_cost,
    )


def validate_attempt_profile(
    attempt: OriginalAttempt,
    lock: AttemptLock,
    attempt_profile: str | AttemptProfile,
) -> AttemptProfile:
    profile = resolve_attempt_profile(attempt_profile)
    if attempt.proof_id != profile.proof_id:
        raise SafetyError("failure receipt proof-ID mismatch for attempt profile")
    if lock.branch != REQUIRED_BRANCH or lock.revision != profile.submit_revision:
        raise SafetyError("attempt lock lineage mismatch for attempt profile")
    if lock.sha256 != profile.attempt_lock_sha256:
        raise SafetyError("attempt lock has been modified or belongs to another profile")
    if attempt.sha256 != profile.failure_receipt_sha256:
        raise SafetyError(
            "failure receipt has been modified or belongs to another profile"
        )
    if attempt.counters != PROFILE_COUNTER_INVARIANTS[profile.name]:
        raise SafetyError("failure receipt counter invariants mismatch")
    if attempt.successful_writes:
        raise SafetyError("attempt contains successful B2 writes")
    if not attempt.second_post_forbidden:
        raise SafetyError("failure receipt does not forbid a second POST")
    if not attempt.resume_possible:
        raise SafetyError("failure receipt does not authorize known-ID reconciliation")
    if lock.maximum_cost_usd != profile.required_cost_ceiling:
        raise SafetyError("attempt lock cost ceiling mismatch")
    if lock.generation_submit_limit != profile.generation_submit_limit:
        raise SafetyError("attempt lock generation-submit limit mismatch")
    if profile is FUNDED_ACCEPTED_ATTEMPT:
        if lock.expected_cost_usd != Decimal("0.035"):
            raise SafetyError("funded attempt lock expected cost mismatch")
        if attempt.submit_classification != c5.ACCEPTED:
            raise SafetyError("funded attempt submit classification must be ACCEPTED")
    return profile


def validate_original_attempt(attempt: OriginalAttempt, lock: AttemptLock) -> None:
    if attempt.proof_id != ORIGINAL_PROOF_ID:
        raise SafetyError("failure receipt proof-ID mismatch")
    if lock.branch != REQUIRED_BRANCH or lock.revision != ORIGINAL_SUBMIT_REVISION:
        raise SafetyError("attempt lock lineage mismatch")
    if lock.sha256 != ATTEMPT_LOCK_SHA256:
        raise SafetyError("attempt lock has been modified")
    if attempt.counters["generation_posts"] != 1:
        raise SafetyError("original generation POST count must equal one")
    if attempt.counters["b2_puts"] != 0:
        raise SafetyError("original B2 PUT count must equal zero")
    if attempt.successful_writes:
        raise SafetyError("original attempt contains successful B2 writes")
    if not attempt.second_post_forbidden:
        raise SafetyError("failure receipt does not forbid a second POST")
    if lock.generation_submit_limit > 1:
        raise SafetyError("original generation-submit maximum exceeds one")


def reconciliation_state(
    attempt: OriginalAttempt,
    profile: AttemptProfile = ORIGINAL_AMBIGUOUS_ATTEMPT,
) -> str:
    if profile is FUNDED_ACCEPTED_ATTEMPT:
        return "READY_TO_RESUME_EXISTING_SUCCESSFUL_REQUEST"
    if attempt.submit_classification == c5.DEFINITIVE_PROVIDER_REJECTION:
        return c5.DEFINITIVE_PROVIDER_REJECTION
    if attempt.submit_classification == c5.ACCEPTED:
        return "READY_TO_RESUME_WITH_KNOWN_REQUEST_ID"
    return "NEEDS_PROVIDER_CONSOLE_RECONCILIATION"


def reconcile_documents(
    attempt: OriginalAttempt,
    lock: AttemptLock,
    attempt_profile: str | AttemptProfile | None = None,
) -> dict[str, Any]:
    if attempt_profile is None:
        profile = ORIGINAL_AMBIGUOUS_ATTEMPT
        validate_original_attempt(attempt, lock)
    else:
        profile = validate_attempt_profile(attempt, lock, attempt_profile)
    state = reconciliation_state(attempt, profile)
    return {
        "mode": "offline-reconcile",
        "state": state,
        "proof_id": attempt.proof_id,
        "original_attempt_revision": lock.revision,
        "original_generation_posts": attempt.counters["generation_posts"],
        "original_status_poll_gets": attempt.counters["status_poll_gets"],
        "original_asset_download_gets": attempt.counters["asset_download_gets"],
        "original_b2_heads": attempt.counters["b2_heads"],
        "original_b2_gets": attempt.counters["b2_gets"],
        "original_b2_puts": attempt.counters["b2_puts"],
        "original_successful_writes": len(attempt.successful_writes),
        "provider_submit_classification": attempt.submit_classification,
        "new_submit_authorized": False,
        "authorized_request_id": AUTHORIZED_RESUME_REQUEST_IDS.get(profile.name),
        "resume_provider_post_limit": RESUME_GENERATION_POST_LIMIT,
        "maximum_additional_generation_cost_usd": "0.00",
        "resume_possible_if_request_id_is_supplied": (
            state != c5.DEFINITIVE_PROVIDER_REJECTION and attempt.resume_possible
        ),
        "network_counters": {
            "provider_posts": 0,
            "provider_status_gets": 0,
            "asset_gets": 0,
            "b2_heads": 0,
            "b2_gets": 0,
            "b2_puts": 0,
        },
    }


def reconcile(
    failure_receipt: Path,
    attempt_lock: Path,
    attempt_profile: str | AttemptProfile | None = None,
) -> dict[str, Any]:
    return reconcile_documents(
        parse_failure_receipt(failure_receipt),
        parse_attempt_lock(attempt_lock, attempt_profile),
        attempt_profile,
    )


def fixed_plan(
    env: Mapping[str, str],
    attempt_profile: str | AttemptProfile = ORIGINAL_AMBIGUOUS_ATTEMPT,
) -> dict[str, Any]:
    profile = resolve_attempt_profile(attempt_profile)
    plan = c5.make_key_plan(profile.proof_id)
    return {
        "mode": "offline-plan",
        "provider": c5.PROVIDER_NAME,
        "model": c5.MODEL,
        "attempt_profile": profile.name,
        "original_proof_id": profile.proof_id,
        "original_attempt_revision": profile.submit_revision,
        "expected_b2_prefix": plan.prefix + "/",
        "exact_keys": list(plan.ordered),
        "resume_provider_post_limit": RESUME_GENERATION_POST_LIMIT,
        "maximum_additional_generation_cost_usd": "0.00",
        "required_local_files": {
            "attempt_lock": profile.attempt_lock_path.is_file(),
            "failure_receipt": profile.failure_receipt_path.is_file(),
        },
        "credential_presence": credential_presence(env),
        "network_counters": {
            "provider_posts": 0,
            "provider_status_gets": 0,
            "asset_gets": 0,
            "b2_heads": 0,
            "b2_gets": 0,
            "b2_puts": 0,
        },
    }


class _SelfTestResponse:
    def __init__(self, status: int, body: bytes, content_type: str):
        self.status_code = status
        self.content = body
        self.headers = {"content-type": content_type}

    def json(self) -> Any:
        return json.loads(self.content)


class _NoGetTransport:
    def __init__(self):
        self.get_calls = 0
        self.post_calls = 0

    def get(self, _url: str, **_kwargs: Any) -> ResponseLike:
        self.get_calls += 1
        raise AssertionError("offline self-test attempted GET")

    def post(self, _url: str, **_kwargs: Any) -> ResponseLike:
        self.post_calls += 1
        raise AssertionError("POST reached transport")

    def close(self) -> None:
        pass


def offline_self_test(
    env: Mapping[str, str],
    attempt_profile: str | AttemptProfile = ORIGINAL_AMBIGUOUS_ATTEMPT,
) -> dict[str, Any]:
    counters = ResumeCounters()
    raw = _NoGetTransport()
    boundary = ResumeProviderHTTP(raw, "request_safe_1", counters)
    try:
        boundary.post("/requests")
    except SafetyError:
        pass
    else:
        raise SafetyError("resume POST prohibition self-test failed")
    if raw.post_calls or counters.generation_posts:
        raise SafetyError("resume POST reached transport")
    accepted = _SelfTestResponse(
        200, b'{"request_id":"safe_1","message":"ok"}', "application/json"
    )
    diagnostic, _data, request_id = c5.classify_submit_response(accepted)
    if diagnostic["submit_classification"] != c5.ACCEPTED or request_id != "safe_1":
        raise SafetyError("accepted-response classification self-test failed")
    rejected = _SelfTestResponse(
        401,
        b'{"error":{"code":"auth","message":"Authorization: secret"}}',
        "application/json",
    )
    diagnostic, _data, _request_id = c5.classify_submit_response(rejected)
    if (
        diagnostic["submit_classification"] != c5.DEFINITIVE_PROVIDER_REJECTION
        or "secret" in json.dumps(diagnostic)
    ):
        raise SafetyError("rejection/redaction self-test failed")
    legacy = OriginalAttempt(
        proof_id=ORIGINAL_PROOF_ID,
        counters={
            "generation_posts": 1,
            "status_poll_gets": 0,
            "asset_download_gets": 0,
            "b2_heads": 5,
            "b2_gets": 0,
            "b2_puts": 0,
            "other_network_methods": 0,
        },
        successful_writes=(),
        failed_key=None,
        reason_code="PipelineError",
        outer_exception_type="PipelineError",
        submit_classification=None,
        submit_diagnostic=None,
        second_post_forbidden=True,
        resume_possible=True,
    )
    lock = AttemptLock(
        REQUIRED_BRANCH,
        ORIGINAL_SUBMIT_REVISION,
        c5.MAX_COST_USD,
        1,
        ATTEMPT_LOCK_SHA256,
    )
    if reconcile_documents(legacy, lock)["state"] != (
        "NEEDS_PROVIDER_CONSOLE_RECONCILIATION"
    ):
        raise SafetyError("legacy receipt self-test failed")
    plan = fixed_plan(env, attempt_profile)
    plan.update(
        {
            "mode": "offline-self-test",
            "status": "PASS",
            "resume_post_structurally_unavailable": True,
            "retry_count": 0,
            "fallback_count": 0,
            "redaction_verified": True,
            "legacy_receipt_supported": True,
            "response_classifications_verified": True,
            "network_client_constructed": False,
        }
    )
    return plan


class SplitOriginProviderTransport:
    """Route exact GMI status and anonymous asset GETs to separate clients."""

    def __init__(
        self,
        credentials: Mapping[str, str],
        client_factory: Callable[..., ProviderGetTransport] | None = None,
    ):
        if client_factory is None:
            import httpx

            client_factory = httpx.Client
        self._install_asset_log_redaction()
        self._closed = False
        self._status_client = client_factory(
            base_url=GMI_STATUS_BASE_URL,
            headers={"Authorization": f"Bearer {credentials['GMI_API_KEY']}"},
            timeout=c5.PROVIDER_TIMEOUT_SECONDS,
            follow_redirects=False,
        )
        try:
            self._asset_client = client_factory(
                timeout=c5.PROVIDER_TIMEOUT_SECONDS,
                follow_redirects=False,
            )
        except Exception:
            try:
                self._status_client.close()
            except Exception:
                pass
            self._closed = True
            raise

    @staticmethod
    def _install_asset_log_redaction() -> None:
        class _AssetURLFilter(logging.Filter):
            _proofstudio_ps042c8 = True

            def filter(self, record: logging.LogRecord) -> bool:
                if GMI_ASSET_HOST in str(record.msg):
                    record.msg = "HTTP asset transport event [URL redacted]"
                    record.args = ()
                    return True
                if isinstance(record.args, tuple):
                    record.args = tuple(
                        "[asset URL redacted]"
                        if GMI_ASSET_HOST in str(value)
                        else value
                        for value in record.args
                    )
                elif isinstance(record.args, Mapping) and any(
                    GMI_ASSET_HOST in str(value) for value in record.args.values()
                ):
                    record.msg = "HTTP asset transport event [URL redacted]"
                    record.args = ()
                return True

        for logger_name in ("httpx", "httpcore"):
            logger = logging.getLogger(logger_name)
            if not any(
                getattr(existing, "_proofstudio_ps042c8", False)
                for existing in logger.filters
            ):
                logger.addFilter(_AssetURLFilter())

    @staticmethod
    def _asset_url_is_allowed(url: str) -> bool:
        try:
            parsed = urlparse(url)
            port = parsed.port
        except (TypeError, ValueError):
            return False
        return (
            parsed.scheme == "https"
            and parsed.hostname == GMI_ASSET_HOST
            and port in {None, 443}
            and parsed.username is None
            and parsed.password is None
            and "#" not in url
            and bool(parsed.path)
        )

    @staticmethod
    def _validate_request_options(kwargs: Mapping[str, Any]) -> None:
        if not set(kwargs).issubset({"timeout", "follow_redirects"}):
            raise SafetyError("provider GET request options are not allowed")
        redirect_value = kwargs.get("follow_redirects")
        if redirect_value is not None and redirect_value is not False:
            raise SafetyError("redirects are forbidden for provider GETs")

    def get(self, url: str, **kwargs: Any) -> ResponseLike:
        if not isinstance(url, str):
            raise SafetyError("provider GET target is not allowed")
        self._validate_request_options(kwargs)
        status_prefix = "/requests/"
        if url.startswith(status_prefix) and REQUEST_ID_PATTERN.fullmatch(
            url[len(status_prefix) :]
        ) is not None:
            try:
                return self._status_client.get(url, **kwargs)
            except Exception:
                raise SafetyError("authenticated status transport failed") from None
        if self._asset_url_is_allowed(url):
            try:
                return self._asset_client.get(url, **kwargs)
            except Exception:
                raise SafetyError("anonymous asset transport failed") from None
        raise SafetyError("provider GET target is not allowed")

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            self._status_client.close()
        finally:
            self._asset_client.close()


class ResumeProviderHTTP:
    """GET-only GMI boundary. POST raises without invoking the transport."""

    def __init__(
        self,
        transport: ProviderGetTransport,
        request_id: str,
        counters: ResumeCounters,
    ):
        if REQUEST_ID_PATTERN.fullmatch(request_id) is None:
            raise SafetyError("resume request ID violates the safe ID contract")
        self._transport = transport
        self.request_id = request_id
        self.counters = counters
        self.asset_url: str | None = None

    def post(self, *_args: Any, **_kwargs: Any) -> Any:
        raise SafetyError("provider POST is structurally forbidden in resume mode")

    def get_status(self) -> Mapping[str, Any]:
        if self.counters.status_poll_gets >= MAX_STATUS_GETS:
            raise ResumeIncompleteError("bounded provider status polling exhausted")
        endpoint = f"/requests/{self.request_id}"
        self.counters.status_poll_gets += 1
        try:
            response = self._transport.get(
                endpoint, timeout=c5.PROVIDER_TIMEOUT_SECONDS, follow_redirects=False
            )
        except Exception as exc:
            raise ResumeIncompleteError("provider status GET failed without retry") from exc
        if response.status_code != 200:
            raise ResumeIncompleteError("provider status GET did not return HTTP 200")
        try:
            detail = response.json()
        except Exception as exc:
            raise ResumeIncompleteError("provider status response was not JSON") from exc
        if not isinstance(detail, Mapping):
            raise ResumeIncompleteError("provider status response was not an object")
        return detail

    def download_asset(self, asset_url: str) -> ResponseLike:
        parsed = urlparse(asset_url)
        if (
            parsed.scheme.lower() != "https"
            or not parsed.netloc
            or parsed.username is not None
            or parsed.password is not None
            or parsed.fragment
        ):
            raise SafetyError("provider returned an unsafe asset URL")
        if self.asset_url is not None and self.asset_url != asset_url:
            raise SafetyError("asset URL changed after terminal success")
        if self.counters.asset_download_gets >= 1:
            raise SafetyError("second asset GET blocked before sending")
        self.asset_url = asset_url
        self.counters.asset_download_gets += 1
        try:
            response = self._transport.get(
                asset_url,
                timeout=c5.PROVIDER_TIMEOUT_SECONDS,
                follow_redirects=False,
            )
        except Exception as exc:
            raise SafetyError("asset GET failed without retry") from exc
        if response.status_code != 200:
            headers = {str(key).lower(): str(value) for key, value in response.headers.items()}
            body = bytes(response.content)
            content_type = headers.get("content-type", "").split(";", 1)[0].strip().lower()
            if re.fullmatch(r"[a-z0-9!#$&^_.+-]+/[a-z0-9!#$&^_.+-]+", content_type) is None:
                content_type = "unknown"
            diagnostic: dict[str, Any] = {
                "http_status": response.status_code,
                "content_type": content_type,
                "byte_length": len(body),
                "body_sha256": _sha256(body),
            }
            location = headers.get("location")
            if location:
                redirect = urlparse(location)
                diagnostic["redirect_location_host"] = redirect.hostname or ""
                diagnostic["redirect_location_path_sha256"] = _sha256(
                    (redirect.path or "/").encode("utf-8")
                )
            message = (
                "asset redirect rejected"
                if 300 <= response.status_code < 400
                else "asset GET did not return HTTP 200"
            )
            raise AssetDownloadError(message, diagnostic)
        return response

    def get(self, *_args: Any, **_kwargs: Any) -> Any:
        self.counters.other_network_methods += 1
        raise SafetyError("unscoped provider GET is forbidden")

    def request(self, *_args: Any, **_kwargs: Any) -> Any:
        self.counters.other_network_methods += 1
        raise SafetyError("generic provider request is forbidden")

    def close(self) -> None:
        self._transport.close()


def normalize_status(detail: Mapping[str, Any]) -> str:
    value = detail.get("status")
    if not isinstance(value, str):
        raise SafetyError("provider status is missing or malformed")
    normalized = value.strip().lower()
    if normalized not in PENDING_STATUSES | TERMINAL_FAILURE_STATUSES | {SUCCESS_STATUS}:
        raise SafetyError("unknown provider status failed closed")
    return normalized


def _one_asset_url(detail: Mapping[str, Any]) -> str:
    outcome = detail.get("outcome")
    if not isinstance(outcome, Mapping):
        raise SafetyError("successful provider result has no outcome object")
    media_urls = outcome.get("media_urls")
    if not isinstance(media_urls, list) or len(media_urls) != 1:
        raise SafetyError("successful provider result must contain exactly one output asset")
    entry = media_urls[0]
    asset_url = entry.get("url") if isinstance(entry, Mapping) else entry
    if not isinstance(asset_url, str):
        raise SafetyError("successful provider output URL is malformed")
    return asset_url


def poll_existing_request(
    provider: ResumeProviderHTTP,
    sleep: Callable[[float], None],
) -> tuple[Mapping[str, Any], str]:
    while provider.counters.status_poll_gets < MAX_STATUS_GETS:
        detail = provider.get_status()
        status = normalize_status(detail)
        if status in PENDING_STATUSES:
            if provider.counters.status_poll_gets >= MAX_STATUS_GETS:
                break
            sleep(STATUS_POLL_INTERVAL_SECONDS)
            continue
        if status in TERMINAL_FAILURE_STATUSES:
            raise ResumeTerminalError(status)
        return detail, status
    raise ResumeIncompleteError("bounded provider status polling timed out")


class ResumeB2Client:
    """Exact-key-only B2 boundary with collision preflight and conditional PUT."""

    def __init__(
        self,
        transport: B2Transport,
        bucket: str,
        plan: Any,
        counters: ResumeCounters,
    ):
        self._transport = transport
        self.bucket = bucket
        self.plan = plan
        self.allowed = frozenset(plan.ordered)
        self.counters = counters
        self.preflight_complete = False
        self.writes_enabled = False
        self.successful_writes: list[str] = []
        self._put_attempts: set[str] = set()

    def _validate_key(self, key: str) -> None:
        if key not in self.allowed:
            raise SafetyError("B2 operation escaped the exact key plan")

    def _missing(self, key: str) -> bool:
        self._validate_key(key)
        self.counters.b2_heads += 1
        try:
            self._transport.head_object(Bucket=self.bucket, Key=key)
            return False
        except c5.ClientError as exc:
            code = str(exc.response.get("Error", {}).get("Code", ""))
            status = exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode")
            if code in {"404", "NoSuchKey", "NotFound"} or status == 404:
                return True
            raise SafetyError("B2 exact-key HEAD failed") from exc

    def assert_all_absent(self) -> None:
        collisions = [key for key in self.plan.ordered if not self._missing(key)]
        if collisions:
            raise SafetyError("planned B2 key already exists; all PUTs blocked")
        self.preflight_complete = True

    def enable_writes(self) -> None:
        if not self.preflight_complete:
            raise SafetyError("B2 writes blocked before exact-key collision checks")
        self.writes_enabled = True

    def put_once(self, key: str, data: bytes, content_type: str) -> None:
        self._validate_key(key)
        if not self.writes_enabled:
            raise SafetyError("B2 PUT blocked before successful image validation")
        if key in self._put_attempts:
            raise SafetyError("B2 PUT retry blocked before sending")
        expected = self.plan.ordered[len(self.successful_writes)]
        if key != expected:
            raise SafetyError("B2 PUT order violated")
        self._put_attempts.add(key)
        self.counters.b2_puts += 1
        try:
            self._transport.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=data,
                ContentType=content_type,
                IfNoneMatch="*",
            )
        except Exception as exc:
            raise SafetyError("B2 conditional PUT failed without retry") from exc
        self.successful_writes.append(key)

    def get_exact(self, key: str) -> bytes:
        self._validate_key(key)
        self.counters.b2_gets += 1
        try:
            response = self._transport.get_object(Bucket=self.bucket, Key=key)
            return response["Body"].read()
        except Exception as exc:
            raise SafetyError("B2 exact-key rehydration failed") from exc

    def close(self) -> None:
        self._transport.close()

    def __getattr__(self, name: str) -> Any:
        if name.startswith(("list", "delete", "copy", "rename", "create_multipart")):
            self.counters.other_network_methods += 1
            raise SafetyError("forbidden B2 operation")
        raise AttributeError(name)


def _safe_b2_diagnostic(operation: str, key: str, exc: BaseException) -> dict[str, Any]:
    diagnostic: dict[str, Any] = {
        "operation": operation,
        "key_sha256": _sha256(key.encode("utf-8")),
        "exception_type": type(exc).__name__,
    }
    response = getattr(exc, "response", None)
    if not isinstance(response, Mapping):
        return diagnostic
    metadata = response.get("ResponseMetadata")
    if isinstance(metadata, Mapping):
        status = metadata.get("HTTPStatusCode")
        if isinstance(status, int) and not isinstance(status, bool):
            diagnostic["http_status"] = status
        request_id = metadata.get("RequestId")
        if isinstance(request_id, str) and request_id:
            diagnostic["request_id_sha256"] = _sha256(request_id.encode("utf-8"))
        headers = metadata.get("HTTPHeaders")
        if "request_id_sha256" not in diagnostic and isinstance(headers, Mapping):
            for name in ("x-bz-request-id", "x-amz-request-id"):
                value = headers.get(name)
                if isinstance(value, str) and value:
                    diagnostic["request_id_sha256"] = _sha256(value.encode("utf-8"))
                    break
    error = response.get("Error")
    if isinstance(error, Mapping):
        code = error.get("Code")
        if isinstance(code, str) and re.fullmatch(r"[A-Za-z0-9_.:-]{1,100}", code):
            diagnostic["provider_error_code"] = code
        body = error.get("Body")
        if isinstance(body, bytes):
            diagnostic["response_body_sha256"] = _sha256(body)
    return diagnostic


def _verify_rehydrated_bytes(
    key: str,
    actual: bytes,
    intended: bytes,
    *,
    expected_length: int | None = None,
    expected_sha256: str | None = None,
) -> None:
    length = len(intended) if expected_length is None else expected_length
    digest = _sha256(intended) if expected_sha256 is None else expected_sha256
    if len(actual) != length:
        raise SafetyError("B2 postwrite verification length mismatch")
    if _sha256(actual) != digest:
        raise SafetyError("B2 postwrite verification SHA-256 mismatch")
    if actual != intended:
        raise SafetyError("B2 postwrite byte mismatch")
    if key == "":
        raise SafetyError("B2 verification key is empty")


class BackblazeCompatibleB2Client:
    """Single-writer plain PUT boundary with exact preflight and immediate GET."""

    def __init__(
        self,
        transport: B2Transport,
        bucket: str,
        plan: Any,
        counters: ResumeCounters,
    ):
        self._transport = transport
        self.bucket = bucket
        self.plan = plan
        self.allowed = frozenset(plan.ordered)
        self.counters = counters
        self.preflight_complete = False
        self.writes_enabled = False
        self.successful_writes: list[str] = []
        self.verified_payloads: dict[str, bytes] = {}
        self._put_attempts: set[str] = set()

    def _validate_key(self, key: str) -> None:
        if key not in self.allowed:
            raise SafetyError("B2 operation escaped the exact key plan")

    @staticmethod
    def _is_absent(exc: BaseException) -> bool:
        response = getattr(exc, "response", None)
        if not isinstance(response, Mapping):
            return False
        error = response.get("Error")
        metadata = response.get("ResponseMetadata")
        code = error.get("Code") if isinstance(error, Mapping) else None
        status = metadata.get("HTTPStatusCode") if isinstance(metadata, Mapping) else None
        return code in {"404", "NoSuchKey", "NotFound"} or status == 404

    def _missing(self, key: str) -> bool:
        self._validate_key(key)
        if self.counters.b2_heads >= C9_B2_HEAD_LIMIT:
            raise SafetyError("B2 HEAD limit exceeded")
        self.counters.b2_heads += 1
        try:
            self._transport.head_object(Bucket=self.bucket, Key=key)
            return False
        except Exception as exc:
            if self._is_absent(exc):
                return True
            raise B2CompatibilityError(
                "B2 exact-key HEAD failed",
                _safe_b2_diagnostic("HeadObject", key, exc),
            ) from None

    def assert_all_absent(self) -> None:
        collisions = [key for key in self.plan.ordered if not self._missing(key)]
        if self.counters.b2_heads != C9_B2_HEAD_LIMIT:
            raise SafetyError("B2 exact-key HEAD count mismatch")
        if collisions:
            raise SafetyError("planned B2 key already exists; all PUTs blocked")
        self.preflight_complete = True

    def enable_writes(self) -> None:
        if not self.preflight_complete or self.counters.b2_heads != C9_B2_HEAD_LIMIT:
            raise SafetyError("B2 writes blocked before all exact-key absence checks")
        self.writes_enabled = True

    def put_and_verify_once(self, key: str, data: bytes, content_type: str) -> bytes:
        self._validate_key(key)
        if not self.writes_enabled:
            raise SafetyError("B2 PUT blocked before exact-key absence preflight")
        if key in self._put_attempts:
            raise SafetyError("B2 PUT retry blocked before sending")
        expected_key = self.plan.ordered[len(self._put_attempts)]
        if key != expected_key:
            raise SafetyError("B2 PUT order violated")
        if self.counters.b2_puts >= C9_B2_PUT_LIMIT:
            raise SafetyError("B2 PUT limit exceeded")
        self._put_attempts.add(key)
        self.counters.b2_puts += 1
        try:
            self._transport.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=data,
                ContentType=content_type,
            )
        except Exception as exc:
            raise B2CompatibilityError(
                "B2 plain PutObject failed without retry",
                _safe_b2_diagnostic("PutObject", key, exc),
            ) from None
        if self.counters.b2_gets >= C9_B2_GET_LIMIT:
            raise SafetyError("B2 verification GET limit exceeded")
        self.counters.b2_gets += 1
        try:
            response = self._transport.get_object(Bucket=self.bucket, Key=key)
            body = response["Body"]
            actual = body.read() if hasattr(body, "read") else bytes(body)
            if not isinstance(actual, bytes):
                actual = bytes(actual)
        except Exception as exc:
            raise B2CompatibilityError(
                "B2 immediate verification GetObject failed",
                _safe_b2_diagnostic("GetObject", key, exc),
            ) from None
        _verify_rehydrated_bytes(key, actual, data)
        self.successful_writes.append(key)
        self.verified_payloads[key] = actual
        return actual

    def close(self) -> None:
        self._transport.close()

    def __getattr__(self, name: str) -> Any:
        if name.startswith(
            ("list", "delete", "copy", "rename", "create_multipart", "upload_part")
        ):
            self.counters.other_network_methods += 1
            raise SafetyError("forbidden B2 operation")
        raise AttributeError(name)


def _git(*args: str) -> str:
    return subprocess.run(
        ("git", *args),
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    ).stdout.strip()


def inspect_repo_state(source_revision: str) -> ResumeRepoState:
    ancestor = subprocess.run(
        ("git", "merge-base", "--is-ancestor", source_revision, "HEAD"),
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0
    return ResumeRepoState(
        branch=_git("branch", "--show-current"),
        head=_git("rev-parse", "HEAD"),
        origin=_git("rev-parse", f"origin/{REQUIRED_BRANCH}"),
        clean=not bool(_git("status", "--porcelain")),
        source_revision_is_ancestor=ancestor,
    )


def validate_resume_gates(
    *,
    attempt: OriginalAttempt,
    lock: AttemptLock,
    request_id: str | None,
    authorization_token: str | None,
    expected_revision: str | None,
    max_additional_cost: str | None,
    env: Mapping[str, str],
    repo_state: ResumeRepoState,
    attempt_profile: str | AttemptProfile | None = None,
) -> dict[str, str]:
    if attempt_profile is None:
        profile = ORIGINAL_AMBIGUOUS_ATTEMPT
        validate_original_attempt(attempt, lock)
    else:
        profile = validate_attempt_profile(attempt, lock, attempt_profile)
    if repo_state.branch != REQUIRED_BRANCH:
        raise SafetyError("wrong branch")
    if not repo_state.clean:
        raise SafetyError("worktree is not clean")
    if expected_revision is None or REVISION_PATTERN.fullmatch(expected_revision) is None:
        raise SafetyError("expected revision must be exactly 40 lowercase hexadecimal characters")
    if repo_state.head != repo_state.origin:
        raise SafetyError("HEAD does not equal origin branch")
    if repo_state.head != expected_revision:
        raise SafetyError("HEAD does not equal explicit expected revision")
    if not repo_state.source_revision_is_ancestor:
        raise SafetyError("original submit revision is not an ancestor of HEAD")
    if authorization_token != RESUME_AUTHORIZATION_TOKEN:
        raise SafetyError("resume authorization token rejected")
    try:
        supplied_cost = Decimal(max_additional_cost or "")
    except Exception as exc:
        raise SafetyError("explicit maximum additional cost is required") from exc
    if supplied_cost != MAX_ADDITIONAL_GENERATION_COST_USD:
        raise SafetyError("maximum additional generation cost must equal 0.00 USD")
    if request_id is None or REQUEST_ID_PATTERN.fullmatch(request_id) is None:
        raise SafetyError("resume request ID violates the safe ID contract")
    authorized_request_id = AUTHORIZED_RESUME_REQUEST_IDS.get(profile.name)
    if authorized_request_id is not None and request_id != authorized_request_id:
        raise SafetyError("resume request ID is not authorized for attempt profile")
    if RESUME_GENERATION_POST_LIMIT != 0 or RESUME_AUTOMATIC_RETRIES != 0:
        raise SafetyError("resume POST/retry contract mismatch")
    present = credential_presence(env)
    missing = [name for name, exists in present.items() if not exists]
    if missing:
        raise SafetyError("missing required credential variable(s): " + ", ".join(missing))
    return {name: env[name] for name in REQUIRED_CREDENTIALS}


def validate_c9_continuation_gates(
    *,
    attempt: OriginalAttempt,
    lock: AttemptLock,
    prior: PriorResumeAttempt,
    request_id: str | None,
    authorization_token: str | None,
    expected_revision: str | None,
    max_additional_cost: str | None,
    env: Mapping[str, str],
    repo_state: ResumeRepoState,
    attempt_profile: str | AttemptProfile,
) -> dict[str, str]:
    profile = resolve_attempt_profile(attempt_profile)
    if profile is not FUNDED_ACCEPTED_ATTEMPT:
        raise SafetyError("B2-compatible continuation requires the funded profile")
    validate_attempt_profile(attempt, lock, profile)
    if prior.proof_id != profile.proof_id:
        raise SafetyError("prior resume proof ID does not match funded profile")
    if prior.provider_request_id != request_id:
        raise SafetyError("prior resume request ID does not match authorized request")
    if repo_state.branch != REQUIRED_BRANCH:
        raise SafetyError("wrong branch")
    if not repo_state.clean:
        raise SafetyError("worktree is not clean")
    if expected_revision is None or REVISION_PATTERN.fullmatch(expected_revision) is None:
        raise SafetyError(
            "expected revision must be exactly 40 lowercase hexadecimal characters"
        )
    if repo_state.head != repo_state.origin:
        raise SafetyError("HEAD does not equal origin branch")
    if repo_state.head != expected_revision:
        raise SafetyError("HEAD does not equal explicit expected revision")
    if not repo_state.source_revision_is_ancestor:
        raise SafetyError("funded submit revision is not an ancestor of HEAD")
    if authorization_token != C9_CONTINUATION_AUTHORIZATION_TOKEN:
        raise SafetyError("B2-compatible continuation authorization token rejected")
    try:
        supplied_cost = Decimal(max_additional_cost or "")
    except Exception as exc:
        raise SafetyError("explicit maximum additional cost is required") from exc
    if supplied_cost != MAX_ADDITIONAL_GENERATION_COST_USD:
        raise SafetyError("maximum additional generation cost must equal 0.00 USD")
    if request_id != FUNDED_AUTHORIZED_REQUEST_ID:
        raise SafetyError("continuation request ID is not the funded authorized request")
    if prior.new_submit_authorized is not False:
        raise SafetyError("new generation submission is not forbidden")
    if any((RESUME_GENERATION_POST_LIMIT, RESUME_AUTOMATIC_RETRIES, RESUME_FALLBACKS)):
        raise SafetyError("continuation zero-POST/retry/fallback contract mismatch")
    present = credential_presence(env)
    missing = [name for name, exists in present.items() if not exists]
    if missing:
        raise SafetyError("missing required credential variable(s): " + ", ".join(missing))
    return {name: env[name] for name in REQUIRED_CREDENTIALS}


def create_c9_execution_lock(
    path: Path,
    *,
    now: datetime,
    branch: str,
    expected_revision: str,
    proof_id: str,
    request_id: str,
) -> str:
    payload = {
        "authorization_timestamp_utc": now.astimezone(timezone.utc).isoformat(),
        "branch": branch,
        "expected_revision": expected_revision,
        "proof_id": proof_id,
        "provider_request_id": request_id,
        "provider_post_limit": 0,
        "b2_put_limit": C9_B2_PUT_LIMIT,
    }
    raw = _canonical_json_bytes(payload) + b"\n"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise SafetyError("continuation execution lock already exists") from exc
    except OSError as exc:
        raise SafetyError("continuation execution lock could not be created") from exc
    try:
        view = memoryview(raw)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise OSError("short execution-lock write")
            view = view[written:]
        os.fsync(descriptor)
    except OSError as exc:
        raise SafetyError("continuation execution lock could not be recorded") from exc
    finally:
        os.close(descriptor)
    return _sha256(raw)


def _counter_dict(counters: ResumeCounters) -> dict[str, int]:
    return dict(counters.__dict__)


def _original_counter_dict(attempt: OriginalAttempt) -> dict[str, int]:
    return dict(attempt.counters)


def _combined_lineage(
    attempt: OriginalAttempt,
    resume_counters: Mapping[str, int],
    profile: AttemptProfile = ORIGINAL_AMBIGUOUS_ATTEMPT,
) -> dict[str, Any]:
    return {
        "proof_id": attempt.proof_id,
        "original_submit_revision": profile.submit_revision,
        "original_provider_posts": attempt.counters["generation_posts"],
        "resume_provider_posts": resume_counters["generation_posts"],
        "total_provider_posts": (
            attempt.counters["generation_posts"] + resume_counters["generation_posts"]
        ),
    }


def build_resume_artifacts(
    *,
    attempt: OriginalAttempt,
    request_id: str,
    image: Any,
    bucket: str,
    plan: Any,
    observed_resume_counters: ResumeCounters,
    now: datetime,
    profile: AttemptProfile = ORIGINAL_AMBIGUOUS_ATTEMPT,
) -> tuple[tuple[tuple[str, bytes, str], ...], dict[str, Any]]:
    final_resume_counters = _counter_dict(observed_resume_counters)
    final_resume_counters.update({"b2_heads": 5, "b2_puts": 5, "b2_gets": 5})
    lineage = _combined_lineage(attempt, final_resume_counters, profile)
    step = c5.build_generation_step()
    step.status = c5.StepStatus.SUCCEEDED
    step.started_at = now
    step.completed_at = now
    step.retries = 0
    step.cost_usd = float(c5.EXPECTED_PRICE_USD)
    step.provider_payload = {
        "gmicloud": {"request_id": request_id, "status": SUCCESS_STATUS},
        "recovery_mode": "resume-existing-request-get-only",
    }
    step.assets = [
        c5.Asset(
            url=f"b2://{bucket}/{plan.image}",
            media_type=image.media_type,
            sha256=image.sha256,
            size_bytes=image.size_bytes,
            width=image.width,
            height=image.height,
            metadata={"source_classification": "resumed-provider-output-locally-verified"},
        )
    ]
    run = c5.Run(
        name="ps042c6-resume-original-proof",
        status=c5.RunStatus.COMPLETED,
        steps=[step],
        started_at=now,
        completed_at=now,
        metadata={"combined_proof_lineage": lineage},
    )
    step.run_id = run.run_id
    step.step_index = 0
    manifest = c5.Manifest.from_run(run)
    if not manifest.verify():
        raise SafetyError("GenBlaze manifest verification failed before B2 writes")
    manifest_bytes = manifest.to_canonical_json().encode("utf-8")
    brief = {
        "schema": "proofstudio.ps042c6.brief.v1",
        "proof_id": attempt.proof_id,
        "prompt": c5.CANONICAL_PROMPT,
        "prompt_sha256": c5.PROMPT_SHA256,
        "provider": c5.PROVIDER_NAME,
        "model": c5.MODEL,
        "dimensions": c5.SIZE,
        "output_format": c5.OUTPUT_FORMAT,
        "watermark": c5.WATERMARK,
        "price_basis_usd_per_output": str(c5.EXPECTED_PRICE_USD),
        "original_authorization_ceiling_usd": str(c5.MAX_COST_USD),
        "maximum_additional_generation_cost_usd": "0.00",
    }
    archive = {
        "schema": "proofstudio.ps042c6.run-bundle.v1",
        "proof_id": attempt.proof_id,
        "provider_request_id": request_id,
        "campaign_brief": brief,
        "manifest": json.loads(manifest_bytes),
        "original_submission_counters": _original_counter_dict(attempt),
        "resume_counters": final_resume_counters,
        "combined_proof_lineage": lineage,
        "truth_boundary": "pipeline-operations-and-byte-integrity-only",
    }
    receipt = {
        "schema": "proofstudio.ps042c6.verification-receipt.v1",
        "proof_id": attempt.proof_id,
        "status": "succeeded",
        "completeness_status": "complete",
        "provider": c5.PROVIDER_NAME,
        "model": c5.MODEL,
        "provider_request_id": request_id,
        "configured_prompt_sha256": c5.PROMPT_SHA256,
        "image_media_type": image.media_type,
        "image_size_bytes": image.size_bytes,
        "image_sha256": image.sha256,
        "image_dimensions": c5.SIZE,
        "manifest_canonical_hash": manifest.canonical_hash,
        "manifest_file_sha256": _sha256(manifest_bytes),
        "manifest_verification": True,
        "original_submission_counters": _original_counter_dict(attempt),
        "resume_counters": final_resume_counters,
        "combined_proof_lineage": lineage,
        "provider_calls_during_rehydrate": 0,
        "b2_uris": {
            name: f"b2://{bucket}/{key}"
            for name, key in (
                ("brief", plan.brief),
                ("image", plan.image),
                ("manifest", plan.manifest),
                ("archive", plan.archive),
                ("receipt", plan.receipt),
            )
        },
    }
    for value in (brief, archive, receipt):
        c5.assert_redacted(value, {})
    payloads = (
        (plan.brief, _canonical_json_bytes(brief), "application/json"),
        (plan.image, image.data, "image/png"),
        (plan.manifest, manifest_bytes, "application/json"),
        (plan.archive, _canonical_json_bytes(archive), "application/json"),
        (plan.receipt, _canonical_json_bytes(receipt), "application/json"),
    )
    return payloads, receipt


def build_c9_continuation_artifacts(
    *,
    attempt: OriginalAttempt,
    prior: PriorResumeAttempt,
    request_id: str,
    image: Any,
    bucket: str,
    plan: Any,
    observed_counters: ResumeCounters,
    now: datetime,
) -> tuple[tuple[tuple[str, bytes, str], ...], dict[str, Any]]:
    payloads, receipt = build_resume_artifacts(
        attempt=attempt,
        request_id=request_id,
        image=image,
        bucket=bucket,
        plan=plan,
        observed_resume_counters=observed_counters,
        now=now,
        profile=FUNDED_ACCEPTED_ATTEMPT,
    )
    by_key = {key: (data, content_type) for key, data, content_type in payloads}
    archive = json.loads(by_key[plan.archive][0])
    receipt = dict(receipt)
    truth = {
        "b2_write_mode": C9_B2_WRITE_MODE,
        "atomic_create_if_absent": False,
        "local_single_writer_enforced": True,
        "postwrite_byte_verification": True,
        "exact_key_preflight": True,
    }
    archive.update(truth)
    receipt.update(truth)
    archive.update(
        {
            "schema": "proofstudio.ps042c9.run-bundle.v1",
            "continuation_counters": archive["resume_counters"],
            "prior_resume_receipt_sha256": prior.sha256,
            "prior_resume_counters": prior.counters,
            "storage_truth_boundary": dict(truth),
        }
    )
    receipt.update(
        {
            "schema": C9_VERIFICATION_RECEIPT_SCHEMA,
            "continuation_counters": receipt["resume_counters"],
            "prior_resume_receipt_sha256": prior.sha256,
            "prior_resume_counters": prior.counters,
            "storage_truth_boundary": dict(truth),
        }
    )
    updated = (
        (plan.brief, by_key[plan.brief][0], by_key[plan.brief][1]),
        (plan.image, by_key[plan.image][0], by_key[plan.image][1]),
        (plan.manifest, by_key[plan.manifest][0], by_key[plan.manifest][1]),
        (plan.archive, _canonical_json_bytes(archive), "application/json"),
        (plan.receipt, _canonical_json_bytes(receipt), "application/json"),
    )
    if tuple(key for key, _data, _content_type in updated) != tuple(plan.ordered):
        raise SafetyError("C9 artifact order does not match the exact proof plan")
    for value in (archive, receipt):
        c5.assert_redacted(value, {})
    return updated, receipt


def _write_local_resume_receipt(
    *,
    root: Path,
    attempt: OriginalAttempt,
    request_id: str,
    counters: ResumeCounters,
    reason_code: str,
    provider_status: str | None,
    successful_writes: list[str],
    profile: AttemptProfile = ORIGINAL_AMBIGUOUS_ATTEMPT,
    asset_download_diagnostic: Mapping[str, Any] | None = None,
) -> Path:
    directory = root / attempt.proof_id
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "resume-receipt.json"
    payload = {
        "schema": RESUME_RECEIPT_SCHEMA,
        "proof_id": attempt.proof_id,
        "status": "incomplete",
        "reason_code": reason_code,
        "provider_status": provider_status,
        "provider_request_id": request_id,
        "new_submit_authorized": False,
        "original_submission_counters": _original_counter_dict(attempt),
        "resume_counters": _counter_dict(counters),
        "combined_proof_lineage": _combined_lineage(
            attempt, _counter_dict(counters), profile
        ),
        "successfully_written_keys": successful_writes,
    }
    if asset_download_diagnostic is not None:
        payload["asset_download_diagnostic"] = dict(asset_download_diagnostic)
    c5.assert_redacted(payload, {})
    path.write_bytes(_canonical_json_bytes(payload) + b"\n")
    return path


def _write_c9_local_receipt(
    *,
    root: Path,
    attempt: OriginalAttempt,
    prior: PriorResumeAttempt,
    request_id: str,
    counters: ResumeCounters,
    reason_code: str,
    provider_status: str | None,
    successful_writes: list[str],
    execution_lock_sha256: str,
    diagnostic: Mapping[str, Any] | None = None,
) -> Path:
    directory = root / attempt.proof_id
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "continuation-receipt.json"
    payload: dict[str, Any] = {
        "schema": C9_LOCAL_RECEIPT_SCHEMA,
        "proof_id": attempt.proof_id,
        "status": "incomplete",
        "reason_code": reason_code,
        "provider_status": provider_status,
        "provider_request_id": request_id,
        "new_submit_authorized": False,
        "maximum_additional_generation_cost_usd": "0.00",
        "original_submission_counters": _original_counter_dict(attempt),
        "prior_resume_receipt_sha256": prior.sha256,
        "prior_resume_counters": prior.counters,
        "continuation_counters": _counter_dict(counters),
        "combined_proof_lineage": _combined_lineage(
            attempt, _counter_dict(counters), FUNDED_ACCEPTED_ATTEMPT
        ),
        "successfully_written_keys": successful_writes,
        "execution_lock_retained": True,
        "execution_lock_sha256": execution_lock_sha256,
        "b2_write_mode": C9_B2_WRITE_MODE,
        "atomic_create_if_absent": False,
        "local_single_writer_enforced": True,
        "postwrite_byte_verification": True,
        "exact_key_preflight": True,
    }
    if diagnostic is not None:
        payload["b2_failure_diagnostic"] = dict(diagnostic)
    c5.assert_redacted(payload, {})
    path.write_bytes(_canonical_json_bytes(payload) + b"\n")
    return path


def _write_completion_marker(
    root: Path,
    attempt: OriginalAttempt,
    request_id: str,
    lock_sha256: str,
    receipt: Mapping[str, Any],
) -> Path:
    directory = root / attempt.proof_id
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "completion-marker.json"
    marker = {
        "schema": COMPLETION_MARKER_SCHEMA,
        "proof_id": attempt.proof_id,
        "provider_request_id": request_id,
        "attempt_lock_retained": True,
        "attempt_lock_sha256": lock_sha256,
        "verification_receipt_sha256": _sha256(_canonical_json_bytes(receipt)),
        "combined_proof_lineage": receipt["combined_proof_lineage"],
    }
    path.write_bytes(_canonical_json_bytes(marker) + b"\n")
    return path


def resume_existing(
    *,
    failure_receipt: Path,
    attempt_lock: Path,
    request_id: str | None,
    authorization_token: str | None,
    expected_revision: str | None,
    max_additional_cost: str | None,
    env: Mapping[str, str],
    dependencies: ResumeDependencies,
    attempt_profile: str | AttemptProfile | None = None,
) -> dict[str, Any]:
    profile = (
        ORIGINAL_AMBIGUOUS_ATTEMPT
        if attempt_profile is None
        else resolve_attempt_profile(attempt_profile)
    )
    attempt = parse_failure_receipt(failure_receipt)
    lock = parse_attempt_lock(attempt_lock, attempt_profile)
    credentials = validate_resume_gates(
        attempt=attempt,
        lock=lock,
        request_id=request_id,
        authorization_token=authorization_token,
        expected_revision=expected_revision,
        max_additional_cost=max_additional_cost,
        env=env,
        repo_state=dependencies.repo_state(lock.revision),
        attempt_profile=attempt_profile,
    )
    assert request_id is not None
    counters = ResumeCounters()
    provider: ResumeProviderHTTP | None = None
    b2: ResumeB2Client | None = None
    provider_status: str | None = None
    successful_writes: list[str] = []
    asset_download_diagnostic: Mapping[str, Any] | None = None
    try:
        provider = ResumeProviderHTTP(
            dependencies.provider_transport(credentials), request_id, counters
        )
        detail, provider_status = poll_existing_request(provider, dependencies.sleep)
        asset_url = _one_asset_url(detail)
        image = c5.validate_png(provider.download_asset(asset_url))
        if counters.generation_posts != 0:
            raise SafetyError("resume provider POST counter changed")

        plan = c5.make_key_plan(attempt.proof_id)
        b2 = ResumeB2Client(
            dependencies.b2_transport(credentials),
            credentials["B2_BUCKET"],
            plan,
            counters,
        )
        b2.assert_all_absent()
        payloads, receipt = build_resume_artifacts(
            attempt=attempt,
            request_id=request_id,
            image=image,
            bucket=credentials["B2_BUCKET"],
            plan=plan,
            observed_resume_counters=counters,
            now=dependencies.now(),
            profile=profile,
        )
        b2.enable_writes()
        for key, data, content_type in payloads:
            b2.put_once(key, data, content_type)
        successful_writes = list(b2.successful_writes)
        if successful_writes != list(plan.ordered):
            raise SafetyError("verification receipt was not written last")

        provider_counts_before_rehydrate = (
            counters.generation_posts,
            counters.status_poll_gets,
            counters.asset_download_gets,
        )
        rehydrated = {key: b2.get_exact(key) for key in plan.ordered}
        expected = {key: data for key, data, _content_type in payloads}
        if any(rehydrated[key] != expected[key] for key in plan.ordered):
            raise SafetyError("complete exact-key rehydration mismatch")
        parsed_manifest = c5.parse_manifest(json.loads(rehydrated[plan.manifest]))
        if not parsed_manifest.verify():
            raise SafetyError("rehydrated manifest verification failed")
        final_receipt = json.loads(rehydrated[plan.receipt])
        if final_receipt.get("completeness_status") != "complete":
            raise SafetyError("rehydrated receipt is incomplete")
        if provider_counts_before_rehydrate != (
            counters.generation_posts,
            counters.status_poll_gets,
            counters.asset_download_gets,
        ):
            raise SafetyError("provider operation occurred during rehydration")
        expected_final = final_receipt["resume_counters"]
        if _counter_dict(counters) != expected_final:
            raise SafetyError("resume counter lineage does not match observed operations")
        if attempt_lock.read_bytes() is None or _sha256(attempt_lock.read_bytes()) != lock.sha256:
            raise SafetyError("attempt lock changed during resume")
        marker = _write_completion_marker(
            dependencies.completion_root, attempt, request_id, lock.sha256, final_receipt
        )
        result = dict(final_receipt)
        result["completion_marker_created"] = True
        result["completion_marker_name"] = marker.name
        result["attempt_lock_retained"] = True
        return result
    except Exception as exc:
        if isinstance(exc, ResumeTerminalError):
            provider_status = exc.status
        if isinstance(exc, AssetDownloadError):
            asset_download_diagnostic = exc.diagnostic
        _write_local_resume_receipt(
            root=dependencies.local_receipt_root,
            attempt=attempt,
            request_id=request_id,
            counters=counters,
            reason_code=type(exc).__name__,
            provider_status=provider_status,
            successful_writes=successful_writes,
            profile=profile,
            asset_download_diagnostic=asset_download_diagnostic,
        )
        if isinstance(exc, SafetyError):
            raise
        if isinstance(exc, c5.SafetyError):
            raise SafetyError(str(exc)) from exc
        raise SafetyError("resume failed closed; see redacted local receipt") from exc
    finally:
        if provider is not None:
            provider.close()
        if b2 is not None:
            b2.close()


def continue_funded_b2(
    *,
    failure_receipt: Path,
    attempt_lock: Path,
    prior_resume_receipt: Path,
    request_id: str | None,
    authorization_token: str | None,
    expected_revision: str | None,
    max_additional_cost: str | None,
    env: Mapping[str, str],
    dependencies: ContinuationDependencies,
    attempt_profile: str | AttemptProfile,
) -> dict[str, Any]:
    profile = resolve_attempt_profile(attempt_profile)
    if profile is not FUNDED_ACCEPTED_ATTEMPT:
        raise SafetyError("B2-compatible continuation is unavailable to original profile")
    if failure_receipt != FUNDED_FAILURE_RECEIPT:
        raise SafetyError("funded original failure receipt path mismatch")
    if attempt_lock != FUNDED_ATTEMPT_LOCK:
        raise SafetyError("funded attempt lock path mismatch")
    attempt = parse_failure_receipt(failure_receipt)
    lock = parse_attempt_lock(attempt_lock, profile)
    prior = parse_prior_resume_receipt(prior_resume_receipt)
    repo = dependencies.repo_state(lock.revision)
    credentials = validate_c9_continuation_gates(
        attempt=attempt,
        lock=lock,
        prior=prior,
        request_id=request_id,
        authorization_token=authorization_token,
        expected_revision=expected_revision,
        max_additional_cost=max_additional_cost,
        env=env,
        repo_state=repo,
        attempt_profile=profile,
    )
    assert request_id is not None and expected_revision is not None
    authorization_time = dependencies.now()
    execution_lock_sha256 = create_c9_execution_lock(
        dependencies.execution_lock,
        now=authorization_time,
        branch=repo.branch,
        expected_revision=expected_revision,
        proof_id=attempt.proof_id,
        request_id=request_id,
    )
    counters = ResumeCounters()
    provider: ResumeProviderHTTP | None = None
    b2: BackblazeCompatibleB2Client | None = None
    provider_status: str | None = None
    successful_writes: list[str] = []
    diagnostic: Mapping[str, Any] | None = None
    try:
        provider = ResumeProviderHTTP(
            dependencies.provider_transport(credentials), request_id, counters
        )
        detail = provider.get_status()
        provider_status = normalize_status(detail)
        if provider_status != SUCCESS_STATUS:
            raise SafetyError("continuation requires an already-successful provider request")
        if counters.status_poll_gets != C9_PROVIDER_STATUS_GET_LIMIT:
            raise SafetyError("continuation provider status GET count mismatch")
        asset_url = _one_asset_url(detail)
        image = c5.validate_png(provider.download_asset(asset_url))
        if counters.asset_download_gets != C9_ASSET_GET_LIMIT:
            raise SafetyError("continuation asset GET count mismatch")
        provider_counts = (
            counters.generation_posts,
            counters.status_poll_gets,
            counters.asset_download_gets,
        )
        if provider_counts != (0, 1, 1):
            raise SafetyError("continuation provider counter contract mismatch")

        plan = c5.make_key_plan(attempt.proof_id)
        b2 = BackblazeCompatibleB2Client(
            dependencies.b2_transport(credentials),
            credentials["B2_BUCKET"],
            plan,
            counters,
        )
        b2.assert_all_absent()
        payloads, receipt = build_c9_continuation_artifacts(
            attempt=attempt,
            prior=prior,
            request_id=request_id,
            image=image,
            bucket=credentials["B2_BUCKET"],
            plan=plan,
            observed_counters=counters,
            now=authorization_time,
        )
        b2.enable_writes()
        for key, data, content_type in payloads:
            b2.put_and_verify_once(key, data, content_type)
            successful_writes = list(b2.successful_writes)
            if (
                counters.generation_posts,
                counters.status_poll_gets,
                counters.asset_download_gets,
            ) != provider_counts:
                raise SafetyError("provider counters changed during B2 operations")
        if successful_writes != list(plan.ordered):
            raise SafetyError("verification receipt was not written and verified last")
        if counters.b2_heads != 5 or counters.b2_puts != 5 or counters.b2_gets != 5:
            raise SafetyError("continuation B2 counter contract mismatch")
        if counters.retries or counters.fallbacks or counters.other_network_methods:
            raise SafetyError("continuation retry/fallback/method contract mismatch")

        rehydrated = b2.verified_payloads
        parsed_manifest = c5.parse_manifest(json.loads(rehydrated[plan.manifest]))
        if not parsed_manifest.verify():
            raise SafetyError("rehydrated manifest verification failed")
        final_archive = json.loads(rehydrated[plan.archive])
        final_receipt = json.loads(rehydrated[plan.receipt])
        if final_receipt.get("completeness_status") != "complete":
            raise SafetyError("rehydrated verification receipt is incomplete")
        if final_receipt != receipt:
            raise SafetyError("rehydrated verification receipt content mismatch")
        required_truth = {
            "b2_write_mode": C9_B2_WRITE_MODE,
            "atomic_create_if_absent": False,
            "local_single_writer_enforced": True,
            "postwrite_byte_verification": True,
            "exact_key_preflight": True,
        }
        if any(
            any(document.get(key) != value for key, value in required_truth.items())
            for document in (final_archive, final_receipt)
        ):
            raise SafetyError("rehydrated storage truth boundary mismatch")
        if _counter_dict(counters) != final_receipt["continuation_counters"]:
            raise SafetyError("continuation counter lineage mismatch")
        lineage = final_receipt.get("combined_proof_lineage", {})
        if (
            lineage.get("original_provider_posts"),
            lineage.get("resume_provider_posts"),
            lineage.get("total_provider_posts"),
        ) != (1, 0, 1):
            raise SafetyError("combined provider POST lineage mismatch")
        if _sha256(attempt_lock.read_bytes()) != lock.sha256:
            raise SafetyError("funded attempt lock changed during continuation")
        if _sha256(prior_resume_receipt.read_bytes()) != prior.sha256:
            raise SafetyError("prior resume receipt changed during continuation")
        marker = _write_completion_marker(
            dependencies.completion_root, attempt, request_id, lock.sha256, final_receipt
        )
        result = dict(final_receipt)
        result.update(
            {
                "completion_marker_created": True,
                "completion_marker_name": marker.name,
                "attempt_lock_retained": True,
                "continuation_execution_lock_retained": True,
                "continuation_execution_lock_sha256": execution_lock_sha256,
            }
        )
        return result
    except Exception as exc:
        if isinstance(exc, B2CompatibilityError):
            diagnostic = exc.diagnostic
        _write_c9_local_receipt(
            root=dependencies.local_receipt_root,
            attempt=attempt,
            prior=prior,
            request_id=request_id,
            counters=counters,
            reason_code=type(exc).__name__,
            provider_status=provider_status,
            successful_writes=successful_writes,
            execution_lock_sha256=execution_lock_sha256,
            diagnostic=diagnostic,
        )
        if isinstance(exc, SafetyError):
            raise
        if isinstance(exc, c5.SafetyError):
            raise SafetyError(str(exc)) from exc
        raise SafetyError("continuation failed closed; see safe local receipt") from None
    finally:
        if provider is not None:
            provider.close()
        if b2 is not None:
            b2.close()


def _default_provider_transport(credentials: Mapping[str, str]) -> ProviderGetTransport:
    return SplitOriginProviderTransport(credentials)


def _default_b2_transport(credentials: Mapping[str, str]) -> B2Transport:
    import boto3

    return boto3.client(
        "s3",
        endpoint_url=f"https://s3.{credentials['B2_REGION']}.backblazeb2.com",
        region_name=credentials["B2_REGION"],
        aws_access_key_id=credentials["B2_KEY_ID"],
        aws_secret_access_key=credentials["B2_APP_KEY"],
        config=c5.Config(
            retries={"max_attempts": 0, "mode": "standard"},
            connect_timeout=c5.PROVIDER_TIMEOUT_SECONDS,
            read_timeout=c5.PROVIDER_TIMEOUT_SECONDS,
        ),
    )


def default_dependencies() -> ResumeDependencies:
    return ResumeDependencies(
        repo_state=inspect_repo_state,
        provider_transport=_default_provider_transport,
        b2_transport=_default_b2_transport,
    )


def default_continuation_dependencies() -> ContinuationDependencies:
    return ContinuationDependencies(
        repo_state=inspect_repo_state,
        provider_transport=_default_provider_transport,
        b2_transport=_default_b2_transport,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PS-042C6 GMI submit reconciliation")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--plan", action="store_true")
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--reconcile", action="store_true")
    modes.add_argument("--resume", action="store_true")
    modes.add_argument("--continue-funded-b2", action="store_true")
    parser.add_argument(
        "--attempt-profile", choices=tuple(ATTEMPT_PROFILES), required=True
    )
    parser.add_argument("--failure-receipt", type=Path)
    parser.add_argument("--attempt-lock", type=Path)
    parser.add_argument("--prior-resume-receipt", type=Path)
    parser.add_argument("--resume-request-id")
    parser.add_argument("--authorization-token")
    parser.add_argument("--expected-revision")
    parser.add_argument("--max-additional-generation-cost-usd")
    return parser


def _print_json(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False))


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not (
        args.plan
        or args.self_test
        or args.reconcile
        or args.resume
        or args.continue_funded_b2
    ):
        parser.print_usage(sys.stderr)
        print("error: exactly one mode is required", file=sys.stderr)
        return 2
    offline_only_args = (
        args.resume_request_id,
        args.authorization_token,
        args.expected_revision,
        args.max_additional_generation_cost_usd,
    )
    if (args.plan or args.self_test or args.reconcile) and any(offline_only_args):
        print("error: resume-only arguments are forbidden in offline modes", file=sys.stderr)
        return 2
    if (args.plan or args.self_test) and (args.failure_receipt or args.attempt_lock):
        print("error: receipt/lock arguments are forbidden in this offline mode", file=sys.stderr)
        return 2
    if (args.reconcile or args.resume or args.continue_funded_b2) and not (
        args.failure_receipt and args.attempt_lock
    ):
        print("error: --failure-receipt and --attempt-lock are required", file=sys.stderr)
        return 2
    if args.continue_funded_b2 and not args.prior_resume_receipt:
        print("error: --prior-resume-receipt is required", file=sys.stderr)
        return 2
    if not args.continue_funded_b2 and args.prior_resume_receipt:
        print("error: --prior-resume-receipt requires --continue-funded-b2", file=sys.stderr)
        return 2
    if args.continue_funded_b2 and args.attempt_profile != "funded":
        print("error: --continue-funded-b2 requires --attempt-profile funded", file=sys.stderr)
        return 2
    try:
        if args.plan:
            _print_json(fixed_plan(os.environ, args.attempt_profile))
        elif args.self_test:
            _print_json(offline_self_test(os.environ, args.attempt_profile))
        elif args.reconcile:
            _print_json(
                reconcile(
                    args.failure_receipt, args.attempt_lock, args.attempt_profile
                )
            )
        elif args.resume:
            _print_json(
                resume_existing(
                    failure_receipt=args.failure_receipt,
                    attempt_lock=args.attempt_lock,
                    request_id=args.resume_request_id,
                    authorization_token=args.authorization_token,
                    expected_revision=args.expected_revision,
                    max_additional_cost=args.max_additional_generation_cost_usd,
                    env=os.environ,
                    dependencies=default_dependencies(),
                    attempt_profile=args.attempt_profile,
                )
            )
        else:
            dependencies = default_continuation_dependencies()
            _print_json(
                continue_funded_b2(
                    failure_receipt=args.failure_receipt,
                    attempt_lock=args.attempt_lock,
                    prior_resume_receipt=args.prior_resume_receipt,
                    request_id=args.resume_request_id,
                    authorization_token=args.authorization_token,
                    expected_revision=args.expected_revision,
                    max_additional_cost=args.max_additional_generation_cost_usd,
                    env=os.environ,
                    dependencies=dependencies,
                    attempt_profile=args.attempt_profile,
                )
            )
    except SafetyError as exc:
        slice_label = "PS-042C9" if args.continue_funded_b2 else "PS-042C6"
        print(f"{slice_label} blocked: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
