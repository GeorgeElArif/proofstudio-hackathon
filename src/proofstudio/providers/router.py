"""Provider router core.

The :class:`ProviderRouter` runs providers in priority order until one succeeds
or all providers have been attempted. It preserves every attempt (success,
failure, or skip) and never fakes success.

Behavior (see specs/14-ps-006-provider-router-core.md section 8):

1. Accept a list of providers in priority order.
2. Call ``provider.attempt(job)`` one by one.
3. Stop on the first successful provider (``normalized_status == OK``).
4. Preserve failed/skipped attempts before success.
5. Stop early if a failed attempt is not fallback-allowed (e.g. a hard policy
   violation). Skipped providers and fallback-allowed failures advance to the
   next provider.
6. Return the final selected provider/model, every attempt, the final
   normalized status, and a clear ``ok`` boolean.

This module performs no network access and introduces no secrets. Live provider
adapters are implemented in later slices (PS-007+).
"""

from __future__ import annotations

import uuid
from typing import Iterable

from proofstudio.providers.types import (
    NS_OK,
    NS_UNKNOWN_ERROR,
    TRUTH_BOUNDARY,
    Provider,
    ProviderAttempt,
    ProviderJob,
    ProviderResult,
    utc_now_iso,
)


class ProviderRouter:
    """Route a job through an ordered chain of providers.

    The router is intentionally dumb about provider internals. Each provider is
    fully responsible for producing a :class:`ProviderAttempt` that honestly
    reflects what happened (success, a normalized failure, or a skip). The
    router only decides ordering, stopping, and final aggregation.
    """

    def __init__(self, providers: Iterable[Provider] | None = None) -> None:
        self.providers: list[Provider] = list(providers or [])

    def with_providers(self, providers: Iterable[Provider]) -> "ProviderRouter":
        return ProviderRouter(providers)

    def route(
        self,
        job: ProviderJob,
        providers: Iterable[Provider] | None = None,
    ) -> ProviderResult:
        chain = list(providers) if providers is not None else list(self.providers)

        attempts: list[ProviderAttempt] = []
        selected: ProviderAttempt | None = None
        stopped_reason: str | None = None

        for index, provider in enumerate(chain):
            attempt = provider.attempt(job)
            attempt.attempt_index = index
            attempts.append(attempt)

            if attempt.normalized_status == NS_OK:
                selected = attempt
                attempt.status = attempt.status or "succeeded"
                break

            if not attempt.fallback_allowed:
                stopped_reason = attempt.normalized_status
                break

        return self._build_result(
            job=job,
            attempts=attempts,
            selected=selected,
            stopped_reason=stopped_reason,
        )

    def _build_result(
        self,
        *,
        job: ProviderJob,
        attempts: list[ProviderAttempt],
        selected: ProviderAttempt | None,
        stopped_reason: str | None,
    ) -> ProviderResult:
        ok = selected is not None
        fallback_used = len(attempts) > 1

        if not attempts:
            final_normalized_status = NS_UNKNOWN_ERROR
            final_status = "failed"
            started_at = utc_now_iso()
            finished_at = started_at
        else:
            last = attempts[-1]
            final_normalized_status = NS_OK if ok else last.normalized_status
            final_status = "succeeded" if ok else "failed"
            started_at = attempts[0].started_at
            finished_at = attempts[-1].finished_at

        return ProviderResult(
            ok=ok,
            final_status=final_status,
            final_normalized_status=final_normalized_status,
            selected_provider=selected.provider if selected is not None else None,
            selected_model=selected.model if selected is not None else None,
            selected_attempt_id=selected.attempt_id if selected is not None else None,
            selected_attempt_index=(
                selected.attempt_index if selected is not None else None
            ),
            fallback_used=fallback_used,
            attempts=attempts,
            job_type=job.job_type,
            budget_mode=job.budget_mode,
            campaign_id=job.campaign_id,
            job_id=job.job_id,
            started_at=started_at,
            finished_at=finished_at,
            output_asset_refs=list(selected.output_asset_refs) if selected else [],
            stopped_reason=stopped_reason,
            truth_boundary=TRUTH_BOUNDARY,
        )


def new_router_id() -> str:
    return uuid.uuid4().hex
