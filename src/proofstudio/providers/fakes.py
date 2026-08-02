"""Deterministic fake providers for PS-006 router testing.

These fakes exist ONLY to exercise :class:`proofstudio.providers.router.ProviderRouter`
in a deterministic, offline, no-key, no-network way. They must never be used as
live provider adapters.

Truth boundary for these fakes:

- They make no network calls and use no secrets.
- :class:`AlwaysSucceedProvider` simulates a provider ``OK`` outcome at the
  router level. It does NOT generate, store, or reference any real media asset.
  Its ``output_asset_refs`` carries a clearly-labeled synthetic success marker
  with no image bytes, no file path, and no real asset hash. This keeps the
  router's success-path plumbing exercised without fabricating generated media.
- :class:`AlwaysFailProvider` always returns a normalized, fallback-allowed
  failure.
- :class:`DisabledProvider` always returns a ``SKIPPED_DISABLED`` skip attempt,
  modeling a provider turned off by configuration.

All three produce realistic, JSON-serializable attempt records.
"""

from __future__ import annotations

from datetime import timedelta

from proofstudio.providers.types import (
    ATTEMPT_STATUS_FAILED,
    ATTEMPT_STATUS_SKIPPED,
    ATTEMPT_STATUS_SUCCEEDED,
    NS_OK,
    NS_PROVIDER_DOWN,
    NS_SKIPPED_DISABLED,
    ProviderAttempt,
    ProviderJob,
    build_attempt,
    utc_now_iso,
)


JOB_TYPE_IMAGE_GENERATION = "image_generation"


def _synthetic_cost(provider_id: str, note: str) -> dict:
    return {
        "amount": 0.0,
        "currency": "USD",
        "cost_basis": "synthetic-fake-provider",
        "free_tier_used": True,
        "paid_required": False,
        "provider_credit_note": f"PS-006 fake provider {provider_id}: {note}",
    }


def _finish_after(started_at: str, milliseconds: int) -> str:
    from datetime import datetime

    start = datetime.fromisoformat(started_at)
    return (start + timedelta(milliseconds=milliseconds)).isoformat()


class _FakeProviderBase:
    job_type: str = JOB_TYPE_IMAGE_GENERATION
    free_or_paid: str = "free"

    @property
    def display_name(self) -> str:
        return self.provider_id

    def _cost(self) -> dict:
        return _synthetic_cost(self.provider_id, "no real cost; deterministic fake.")


class AlwaysSucceedProvider(_FakeProviderBase):
    provider_id = "fake-always-succeed"
    model = "fake-success-model"
    api_method = "fake-attempt-always-succeed"

    def attempt(self, job: ProviderJob) -> ProviderAttempt:
        started_at = utc_now_iso()
        finished_at = _finish_after(started_at, 42)
        return build_attempt(
            attempt_index=0,
            provider=self.provider_id,
            model=self.model,
            api_method=self.api_method,
            job_type=self.job_type,
            status=ATTEMPT_STATUS_SUCCEEDED,
            normalized_status=NS_OK,
            started_at=started_at,
            finished_at=finished_at,
            estimated_cost=self._cost(),
            free_or_paid=self.free_or_paid,
            output_asset_refs=[
                {
                    "kind": "synthetic_success_marker",
                    "synthetic": True,
                    "provider": self.provider_id,
                    "model": self.model,
                    "api_method": self.api_method,
                    "job_type": self.job_type,
                    "produced_real_media": False,
                    "note": (
                        "Deterministic fake provider OK marker. No real media "
                        "asset was generated, fetched, stored, or hashed."
                    ),
                }
            ],
            notes=(
                "AlwaysSucceedProvider simulated an OK provider outcome for "
                "router-core testing. No network call and no real asset."
            ),
        )


class AlwaysFailProvider(_FakeProviderBase):
    provider_id = "fake-always-fail"
    model = "fake-fail-model"
    api_method = "fake-attempt-always-fail"

    def __init__(self, *, normalized_status: str = NS_PROVIDER_DOWN) -> None:
        self.normalized_status = normalized_status

    def attempt(self, job: ProviderJob) -> ProviderAttempt:
        started_at = utc_now_iso()
        finished_at = _finish_after(started_at, 137)
        return build_attempt(
            attempt_index=0,
            provider=self.provider_id,
            model=self.model,
            api_method=self.api_method,
            job_type=self.job_type,
            status=ATTEMPT_STATUS_FAILED,
            normalized_status=self.normalized_status,
            started_at=started_at,
            finished_at=finished_at,
            raw_error_type="FakeProviderError",
            sanitized_error_message=(
                "AlwaysFailProvider deterministically failed for router-core "
                "testing. No provider was contacted."
            ),
            estimated_cost=self._cost(),
            free_or_paid=self.free_or_paid,
            notes=(
                "AlwaysFailProvider simulated a normalized provider failure. "
                "Failure is fallback-allowed so the router should continue."
            ),
        )


class DisabledProvider(_FakeProviderBase):
    provider_id = "fake-disabled"
    model = "fake-disabled-model"
    api_method = "fake-attempt-disabled"

    def attempt(self, job: ProviderJob) -> ProviderAttempt:
        started_at = utc_now_iso()
        finished_at = _finish_after(started_at, 1)
        return build_attempt(
            attempt_index=0,
            provider=self.provider_id,
            model=self.model,
            api_method=self.api_method,
            job_type=self.job_type,
            status=ATTEMPT_STATUS_SKIPPED,
            normalized_status=NS_SKIPPED_DISABLED,
            started_at=started_at,
            finished_at=finished_at,
            skip_reason=(
                "Provider disabled by configuration (deterministic fake)."
            ),
            raw_error_type="DisabledByConfig",
            sanitized_error_message=(
                "DisabledProvider was skipped because it is disabled. No "
                "provider was contacted."
            ),
            estimated_cost=self._cost(),
            free_or_paid=self.free_or_paid,
            notes=(
                "DisabledProvider simulated a SKIPPED_DISABLED skip. It is "
                "preserved in the ledger and fallback is allowed."
            ),
        )


__all__ = [
    "AlwaysSucceedProvider",
    "AlwaysFailProvider",
    "DisabledProvider",
]
