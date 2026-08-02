"""Provider router subpackage.

Public types and the router are re-exported here for convenience:

    from proofstudio.providers import ProviderRouter, ProviderAttempt

The ``fakes`` module is kept importable but is intentionally not re-exported
because fake providers are for deterministic testing only and must never be
used as live provider adapters.

PS-007 introduces the live adapters in ``live_cloudflare`` and
``live_pollinations``. These are re-exported here for clean access from the
PS-007 smoke script and later slices:

    from proofstudio.providers import LiveCloudflareProvider, LivePollinationsProvider
"""

from proofstudio.providers.types import (
    NORMALIZED_STATUSES,
    ATTEMPT_STATUSES,
    Provider,
    ProviderAttempt,
    ProviderJob,
    ProviderResult,
    build_attempt,
    classify_normalized_status,
    utc_now_iso,
)
from proofstudio.providers.router import ProviderRouter
from proofstudio.providers.live_cloudflare import LiveCloudflareProvider
from proofstudio.providers.live_pollinations import LivePollinationsProvider

__all__ = [
    "ProviderRouter",
    "Provider",
    "ProviderAttempt",
    "ProviderJob",
    "ProviderResult",
    "build_attempt",
    "classify_normalized_status",
    "utc_now_iso",
    "NORMALIZED_STATUSES",
    "ATTEMPT_STATUSES",
    "LiveCloudflareProvider",
    "LivePollinationsProvider",
]
