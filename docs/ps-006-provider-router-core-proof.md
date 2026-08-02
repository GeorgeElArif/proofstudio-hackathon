# PS-006 ProviderRouter Core Proof

## Status

Accepted pass.

PS-006 converts the proven one-off provider behavior from PS-004 (Cloudflare
Workers AI) and PS-005 (Pollinations no-key fallback) into reusable
ProofStudio product code: a deterministic provider router core with
JSON-serializable attempt records.

- Overall: `ok: true` (4/4 scenarios passed)
- No network calls, no API keys, no B2, no real media generated.
- PS-004 and PS-005 scripts are unchanged and remain historical runtime proofs.

## Slice Scope

This slice implements router-core behavior only. It is intentionally not:

- a web app
- a database layer
- a FastAPI service
- a new live provider integration
- a B2 / Genblaze upload path

It creates the reusable foundation that PS-007 will use to implement the real
fallback chain: Cloudflare Workers AI primary -> Pollinations fallback -> B2 +
Genblaze manifest.

## Reusable Files Created

- `src/proofstudio/__init__.py`
- `src/proofstudio/providers/__init__.py`
- `src/proofstudio/providers/types.py` — normalized statuses, `ProviderJob`,
  `ProviderAttempt`, `ProviderResult`, `Provider` protocol, `build_attempt`
  helper, JSON-serializable via `to_dict()`.
- `src/proofstudio/providers/router.py` — `ProviderRouter` that runs providers
  in priority order, stops on first success, preserves every attempt, falls
  back on failures/skips, and returns `ok: false` when all providers fail.
- `src/proofstudio/providers/fakes.py` — `AlwaysSucceedProvider`,
  `AlwaysFailProvider`, `DisabledProvider` deterministic fakes (no network).
- `scripts/ps006_provider_router_core_smoke.py` — deterministic 4-scenario
  smoke test.
- `docs/ps-006-provider-router-core-proof.md` — this file.

## Provider Interface

The `Provider` protocol exposes the practical surface that PS-007 live
adapters will implement:

- `provider_id`
- `display_name`
- `model`
- `api_method`
- `job_type`
- `attempt(job: ProviderJob) -> ProviderAttempt`

## Normalized Statuses Supported

`OK`, `MODEL_UNAVAILABLE`, `SAFETY_BLOCKED`, `TIMEOUT`, `BAD_REQUEST`,
`PROVIDER_DOWN`, `UNSUPPORTED_MODE`, `SKIPPED_DISABLED`, `SKIPPED_MISSING_KEY`,
`QUOTA_OR_BILLING_BLOCKED`, `UNKNOWN_ERROR`.

## Attempt Schema

Every attempt includes: `attempt_id`, `attempt_index`, `provider`, `model`,
`api_method`, `job_type`, `status`, `normalized_status`, `started_at`,
`finished_at`, `latency_ms`, `retryable`, `fallback_allowed`, `skip_reason`,
`raw_error_type`, `sanitized_error_message`, `estimated_cost`, `free_or_paid`,
`output_asset_refs`, `notes`.

All attempts serialize to JSON without custom encoders.

## Scenarios Tested

### Scenario A: First Provider Succeeds

- Chain: `AlwaysSucceedProvider`
- `ok: true`
- attempt count: 1
- selected provider: `fake-always-succeed` (index 0)
- `fallback_used: false`
- final normalized status: `OK`

### Scenario B: First Fails, Second Succeeds

- Chain: `AlwaysFailProvider`, `AlwaysSucceedProvider`
- `ok: true`
- attempt count: 2
- selected provider: `fake-always-succeed` (index 1)
- `fallback_used: true`
- failed attempt (attempt 0, `PROVIDER_DOWN`) preserved in the ledger
- final normalized status: `OK`

### Scenario C: Disabled Provider, Then Success

- Chain: `DisabledProvider`, `AlwaysSucceedProvider`
- `ok: true`
- attempt count: 2
- disabled attempt (attempt 0, `SKIPPED_DISABLED`) preserved in the ledger
- selected provider: `fake-always-succeed` (index 1)
- `fallback_used: true`
- final normalized status: `OK`

### Scenario D: All Fail

- Chain: `AlwaysFailProvider`, `AlwaysFailProvider`
- `ok: false`
- attempt count: 2
- selected provider: none
- no fake output, no `output_asset_refs` on any failure attempt
- failure evidence (both `PROVIDER_DOWN` attempts) preserved
- final normalized status: `PROVIDER_DOWN`

## Selected Provider Per Scenario

| Scenario | Selected provider | Selected attempt index |
|---|---|---|
| A | `fake-always-succeed` | 0 |
| B | `fake-always-succeed` | 1 |
| C | `fake-always-succeed` | 1 |
| D | none | none |

## Attempt Counts

| Scenario | Attempts | Successes | Failures | Skips |
|---|---|---|---|---|
| A | 1 | 1 | 0 | 0 |
| B | 2 | 1 | 1 | 0 |
| C | 2 | 1 | 0 | 1 |
| D | 2 | 0 | 2 | 0 |

## Fallback Behavior

- The router advances to the next provider whenever an attempt is
  `fallback_allowed` (all failures and skips in PS-006 are fallback-allowed).
- It stops on the first `OK` attempt.
- It stops early if a failure is not `fallback_allowed` (hard policy stop);
  no scenario in PS-006 triggers this, but the path exists for PS-007.
- `fallback_used` is `true` whenever more than one provider is attempted.

## Failure Behavior

- No failed or skipped attempt is ever discarded.
- Failures are mapped to normalized statuses with `retryable` and
  `fallback_allowed` flags derived from the normalized status.
- Sanitized error messages contain no secrets and no provider payload detail.
- When all providers fail, the result is `ok: false`, `final_status: failed`,
  with the last attempt's normalized status surfaced as the final
  normalized status and the full failure ledger preserved.

## No Fake Success / No Fake Media

- `AlwaysSucceedProvider` simulates a provider `OK` at the router level only.
- It does NOT generate, fetch, store, or hash any real media asset.
- Its `output_asset_refs` carries a single clearly-labeled
  `synthetic_success_marker` with `produced_real_media: false` and no
  `local_path`, no `sha256`, no `b2_url`, and no media bytes.
- The smoke script actively asserts no attempt produced real media and that
  failure attempts carry no `output_asset_refs`.
- Scenario D returns `ok: false` with no fake output.

## Why No B2 Upload Is Required In This Slice

PS-006 tests deterministic router-core behavior: provider ordering, stopping on
first success, fallback after failure/disabled providers, attempt preservation,
and honest all-fail reporting.

The B2 + Genblaze upload + manifest verification path is already proven in:

- PS-001A (local asset + manifest + B2 round-trip)
- PS-004 (Cloudflare Workers AI provider -> B2 -> Genblaze)
- PS-005 (Pollinations fallback -> B2 -> Genblaze)

Re-running a B2 upload in PS-006 would add no new router-core evidence and
would require live credentials, which PS-006 explicitly avoids. The durable
storage + manifest layer re-enters in PS-007 when the real live fallback chain
is implemented on top of this router core.

## Local Outputs

The smoke script writes deterministic evidence to `/tmp`:

- `/tmp/proofstudio-ps-006/provider-router-core-summary.json`
- `/tmp/proofstudio-ps-006/provider-router-core-attempts.json`

The summary `ok: true` only if all four scenarios pass. No B2 artifacts are
produced.

## Acceptance Criteria Check

- reusable provider router files exist: yes
- smoke script compiles: yes (`py_compile` clean)
- smoke script passes all four scenarios: yes (4/4)
- attempts are JSON serializable: yes (validated inline by the smoke script)
- failure attempts are preserved: yes (Scenario B, Scenario D)
- disabled attempts are preserved: yes (Scenario C)
- all-fail scenario returns `ok: false`: yes (Scenario D)
- no fake success is created: yes (success is router-level only; no fake media)
- no secrets are introduced: yes (no keys, tokens, or auth in any file)
- no live API keys are required: yes (stdlib only; no provider imports)
- no unrelated files are modified: yes (only the seven required files added)

## Truth Boundary

PS-006 proves deterministic router-core behavior only.

It does NOT prove:

- that any real provider executed
- that any media asset was generated
- that any manifest exists or was verified
- semantic truth, legal authenticity, or C2PA authenticity
- that the router works against a live API

It DOES prove:

- the router preserves every attempt (success, failure, skip)
- the router stops on the first success
- the router falls back correctly after failures and disabled providers
- the router returns `ok: false` with full evidence when all providers fail
- the router never fabricates success or media
