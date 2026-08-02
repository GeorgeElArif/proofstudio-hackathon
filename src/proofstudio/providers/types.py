"""Provider router core types.

This module defines the deterministic, JSON-serializable vocabulary that the
ProofStudio provider router uses to record every provider attempt.

Design rules for PS-006:

- Stdlib only. No network, no Pydantic, no provider SDKs.
- Every attempt is preserved (success, failure, or skip).
- Failure evidence is never discarded.
- Success is never fabricated. An ``OK`` normalized status must come from a
  provider that actually returned a result; the types here only carry data.
- All public objects serialize to plain JSON via ``to_dict()`` / ``json.dumps``.

See specs/09-provider-router-contract.md and specs/10-attempt-ledger-contract.md
for the contract this module implements, and specs/14-ps-006-provider-router-core.md
for the PS-006 slice scope.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol, runtime_checkable


ATTEMPT_STATUS_SKIPPED = "skipped"
ATTEMPT_STATUS_STARTED = "started"
ATTEMPT_STATUS_FAILED = "failed"
ATTEMPT_STATUS_SUCCEEDED = "succeeded"
ATTEMPT_STATUS_SELECTED = "selected"
ATTEMPT_STATUS_REJECTED = "rejected"
ATTEMPT_STATUS_RETRIED = "retried"

ATTEMPT_STATUSES = frozenset(
    {
        ATTEMPT_STATUS_SKIPPED,
        ATTEMPT_STATUS_STARTED,
        ATTEMPT_STATUS_FAILED,
        ATTEMPT_STATUS_SUCCEEDED,
        ATTEMPT_STATUS_SELECTED,
        ATTEMPT_STATUS_REJECTED,
        ATTEMPT_STATUS_RETRIED,
    }
)


NS_OK = "OK"
NS_MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
NS_SAFETY_BLOCKED = "SAFETY_BLOCKED"
NS_TIMEOUT = "TIMEOUT"
NS_BAD_REQUEST = "BAD_REQUEST"
NS_PROVIDER_DOWN = "PROVIDER_DOWN"
NS_UNSUPPORTED_MODE = "UNSUPPORTED_MODE"
NS_SKIPPED_DISABLED = "SKIPPED_DISABLED"
NS_SKIPPED_MISSING_KEY = "SKIPPED_MISSING_KEY"
NS_QUOTA_OR_BILLING_BLOCKED = "QUOTA_OR_BILLING_BLOCKED"
NS_UNKNOWN_ERROR = "UNKNOWN_ERROR"

NORMALIZED_STATUSES = frozenset(
    {
        NS_OK,
        NS_MODEL_UNAVAILABLE,
        NS_SAFETY_BLOCKED,
        NS_TIMEOUT,
        NS_BAD_REQUEST,
        NS_PROVIDER_DOWN,
        NS_UNSUPPORTED_MODE,
        NS_SKIPPED_DISABLED,
        NS_SKIPPED_MISSING_KEY,
        NS_QUOTA_OR_BILLING_BLOCKED,
        NS_UNKNOWN_ERROR,
    }
)

SUCCESS_NORMALIZED_STATUSES = frozenset({NS_OK})

SKIP_NORMALIZED_STATUSES = frozenset({NS_SKIPPED_DISABLED, NS_SKIPPED_MISSING_KEY})

RETRYABLE_NORMALIZED_STATUSES = frozenset(
    {
        NS_MODEL_UNAVAILABLE,
        NS_TIMEOUT,
        NS_PROVIDER_DOWN,
        NS_UNKNOWN_ERROR,
    }
)

FALLBACK_ALLOWED_NORMALIZED_STATUSES = frozenset(
    {
        NS_MODEL_UNAVAILABLE,
        NS_SAFETY_BLOCKED,
        NS_TIMEOUT,
        NS_BAD_REQUEST,
        NS_PROVIDER_DOWN,
        NS_UNSUPPORTED_MODE,
        NS_UNKNOWN_ERROR,
        NS_QUOTA_OR_BILLING_BLOCKED,
        NS_SKIPPED_DISABLED,
        NS_SKIPPED_MISSING_KEY,
    }
)

TRUTH_BOUNDARY = (
    "The router records provider execution evidence only. It does not prove "
    "semantic truth, legal authenticity, or C2PA authenticity. A provider "
    "returning OK proves the provider returned a result; it does not prove "
    "the output is fit for any particular use."
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def compute_latency_ms(started_at: str, finished_at: str) -> int:
    if not started_at or not finished_at:
        return 0
    try:
        start = datetime.fromisoformat(started_at)
        end = datetime.fromisoformat(finished_at)
    except ValueError:
        return 0
    return max(0, int((end - start).total_seconds() * 1000))


def classify_normalized_status(normalized_status: str) -> tuple[bool, bool]:
    if normalized_status not in NORMALIZED_STATUSES:
        raise ValueError(f"Unknown normalized status: {normalized_status!r}")
    retryable = normalized_status in RETRYABLE_NORMALIZED_STATUSES
    fallback_allowed = normalized_status in FALLBACK_ALLOWED_NORMALIZED_STATUSES
    return retryable, fallback_allowed


def _new_attempt_id() -> str:
    return uuid.uuid4().hex


@dataclass
class ProviderJob:
    job_type: str
    prompt: str = ""
    budget_mode: str = "free-only"
    campaign_id: str = "proofstudio-launch"
    job_id: str = field(default_factory=_new_attempt_id)
    params: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_type": self.job_type,
            "prompt": self.prompt,
            "budget_mode": self.budget_mode,
            "campaign_id": self.campaign_id,
            "job_id": self.job_id,
            "params": dict(self.params),
        }


@dataclass
class ProviderAttempt:
    attempt_id: str
    attempt_index: int
    provider: str
    model: str
    api_method: str
    job_type: str
    status: str
    normalized_status: str
    started_at: str
    finished_at: str
    retryable: bool
    fallback_allowed: bool
    skip_reason: str | None = None
    raw_error_type: str | None = None
    sanitized_error_message: str | None = None
    estimated_cost: dict[str, Any] = field(default_factory=dict)
    free_or_paid: str = "unknown"
    output_asset_refs: list[dict[str, Any]] = field(default_factory=list)
    notes: str = ""
    latency_ms: int = 0

    def __post_init__(self) -> None:
        if self.latency_ms == 0:
            self.latency_ms = compute_latency_ms(self.started_at, self.finished_at)

    def to_dict(self) -> dict[str, Any]:
        return {
            "attempt_id": self.attempt_id,
            "attempt_index": self.attempt_index,
            "provider": self.provider,
            "model": self.model,
            "api_method": self.api_method,
            "job_type": self.job_type,
            "status": self.status,
            "normalized_status": self.normalized_status,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "latency_ms": self.latency_ms,
            "retryable": self.retryable,
            "fallback_allowed": self.fallback_allowed,
            "skip_reason": self.skip_reason,
            "raw_error_type": self.raw_error_type,
            "sanitized_error_message": self.sanitized_error_message,
            "estimated_cost": dict(self.estimated_cost),
            "free_or_paid": self.free_or_paid,
            "output_asset_refs": [dict(ref) for ref in self.output_asset_refs],
            "notes": self.notes,
        }


@dataclass
class ProviderResult:
    ok: bool
    final_status: str
    final_normalized_status: str
    selected_provider: str | None
    selected_model: str | None
    selected_attempt_id: str | None
    selected_attempt_index: int | None
    fallback_used: bool
    attempts: list[ProviderAttempt] = field(default_factory=list)
    job_type: str = ""
    budget_mode: str = "free-only"
    campaign_id: str = "proofstudio-launch"
    job_id: str = ""
    started_at: str = ""
    finished_at: str = ""
    output_asset_refs: list[dict[str, Any]] = field(default_factory=list)
    stopped_reason: str | None = None
    truth_boundary: str = TRUTH_BOUNDARY

    @property
    def attempt_count(self) -> int:
        return len(self.attempts)

    def to_dict(self) -> dict[str, Any]:
        selected = None
        for attempt in self.attempts:
            if (
                self.selected_attempt_id is not None
                and attempt.attempt_id == self.selected_attempt_id
            ):
                selected = attempt
                break
        return {
            "ok": self.ok,
            "final_status": self.final_status,
            "final_normalized_status": self.final_normalized_status,
            "selected_provider": self.selected_provider,
            "selected_model": self.selected_model,
            "selected_attempt_id": self.selected_attempt_id,
            "selected_attempt_index": self.selected_attempt_index,
            "fallback_used": self.fallback_used,
            "attempt_count": self.attempt_count,
            "attempts": [attempt.to_dict() for attempt in self.attempts],
            "selected_attempt": selected.to_dict() if selected is not None else None,
            "job_type": self.job_type,
            "budget_mode": self.budget_mode,
            "campaign_id": self.campaign_id,
            "job_id": self.job_id,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "output_asset_refs": [dict(ref) for ref in self.output_asset_refs],
            "stopped_reason": self.stopped_reason,
            "truth_boundary": self.truth_boundary,
        }


@runtime_checkable
class Provider(Protocol):
    provider_id: str
    display_name: str
    model: str
    api_method: str
    job_type: str

    def attempt(self, job: ProviderJob) -> ProviderAttempt:
        ...


def build_attempt(
    *,
    attempt_index: int,
    provider: str,
    model: str,
    api_method: str,
    job_type: str,
    status: str,
    normalized_status: str,
    started_at: str,
    finished_at: str,
    skip_reason: str | None = None,
    raw_error_type: str | None = None,
    sanitized_error_message: str | None = None,
    estimated_cost: dict[str, Any] | None = None,
    free_or_paid: str = "unknown",
    output_asset_refs: list[dict[str, Any]] | None = None,
    notes: str = "",
    attempt_id: str | None = None,
) -> ProviderAttempt:
    retryable, fallback_allowed = classify_normalized_status(normalized_status)
    return ProviderAttempt(
        attempt_id=attempt_id or _new_attempt_id(),
        attempt_index=attempt_index,
        provider=provider,
        model=model,
        api_method=api_method,
        job_type=job_type,
        status=status,
        normalized_status=normalized_status,
        started_at=started_at,
        finished_at=finished_at,
        retryable=retryable,
        fallback_allowed=fallback_allowed,
        skip_reason=skip_reason,
        raw_error_type=raw_error_type,
        sanitized_error_message=sanitized_error_message,
        estimated_cost=dict(estimated_cost or {}),
        free_or_paid=free_or_paid,
        output_asset_refs=list(output_asset_refs or []),
        notes=notes,
    )
