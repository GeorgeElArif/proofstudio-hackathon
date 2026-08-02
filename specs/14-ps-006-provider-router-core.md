# PS-006 ProviderRouter Core

## 1. Purpose

PS-006 converts the proven one-off provider smoke scripts into reusable ProofStudio product code.

PS-004 proved Cloudflare Workers AI image generation.

PS-005 proved Pollinations no-key fallback image generation.

PS-006 must extract the shared provider-routing logic into a reusable core module without weakening the proof discipline.

This slice is not UI work.

This slice is not a full backend API.

This slice is not a new provider integration.

This slice creates the reusable provider router foundation that later slices will use.

## 2. Product Meaning

ProofStudio should not behave like a single-provider image generator.

It should behave like a provenance-aware media operations system that can:

- choose a provider
- explain why that provider was chosen
- attempt generation
- normalize provider failures
- fall back when allowed
- record every attempt
- preserve provider evidence
- store resulting assets through the B2 + Genblaze pipeline

PS-006 turns that behavior into reusable code.

## 3. Required Files

Create these files:

- `src/proofstudio/__init__.py`
- `src/proofstudio/providers/__init__.py`
- `src/proofstudio/providers/types.py`
- `src/proofstudio/providers/router.py`
- `src/proofstudio/providers/fakes.py`
- `scripts/ps006_provider_router_core_smoke.py`
- `docs/ps-006-provider-router-core-proof.md`

Do not delete or rewrite PS-004 or PS-005 scripts.

Those scripts remain historical runtime proofs.

## 4. Non-Goals

Do not implement a web app.

Do not implement a database.

Do not add FastAPI yet.

Do not refactor PS-004 or PS-005 into oblivion.

Do not require live network calls in PS-006.

Do not require Cloudflare, Pollinations, Gemini, GMICloud, or any provider API key for the PS-006 core smoke test.

Do not upload fake generated images to B2.

## 5. Core Concepts

### Provider

A provider is an adapter that can attempt one job type.

For now, PS-006 only needs image-generation-shaped behavior, but the type system must not make future audio/video impossible.

### ProviderAttempt

A ProviderAttempt records one provider attempt, whether success, skipped, or failed.

### ProviderResult

A ProviderResult is the final router output after one or more attempts.

### ProviderRouter

The ProviderRouter runs providers in order until one succeeds or all fail.

It must preserve every attempt.

It must not hide failures.

It must not fake success.

## 6. Normalized Statuses

The reusable code must support these normalized statuses:

- `OK`
- `MODEL_UNAVAILABLE`
- `SAFETY_BLOCKED`
- `TIMEOUT`
- `BAD_REQUEST`
- `PROVIDER_DOWN`
- `UNSUPPORTED_MODE`
- `SKIPPED_DISABLED`
- `SKIPPED_MISSING_KEY`
- `QUOTA_OR_BILLING_BLOCKED`
- `UNKNOWN_ERROR`

## 7. Attempt Schema

Every attempt object must include:

- `attempt_id`
- `attempt_index`
- `provider`
- `model`
- `api_method`
- `job_type`
- `status`
- `normalized_status`
- `started_at`
- `finished_at`
- `latency_ms`
- `retryable`
- `fallback_allowed`
- `skip_reason`
- `raw_error_type`
- `sanitized_error_message`
- `estimated_cost`
- `free_or_paid`
- `output_asset_refs`
- `notes`

The shape should be serializable to JSON without custom encoders.

## 8. Router Behavior

The router must:

1. Accept a list of providers in priority order.
2. Call providers one by one.
3. Stop on the first successful provider result.
4. Preserve failed/skipped attempts before success.
5. Return final selected provider and model.
6. Return all attempts.
7. Return final normalized status.
8. Return a clear `ok` boolean.
9. Never discard failure evidence.
10. Never fake success if no provider succeeds.

## 9. Fallback Behavior

If provider A fails and provider B succeeds, the final result must include:

- `ok: true`
- `selected_provider: provider B`
- all attempts from provider A and provider B
- provider A failure status
- provider B OK status
- `fallback_used: true`

If all providers fail, the final result must include:

- `ok: false`
- all failed attempts
- final normalized status from the last meaningful failure
- `fallback_used: false` or `true` depending on whether more than one provider was attempted
- no fake output

## 10. Fake Providers Required for PS-006

Create fake providers only for deterministic router testing:

- `AlwaysFailProvider`
- `AlwaysSucceedProvider`
- `DisabledProvider`

These fake providers must not make network calls.

They should produce realistic attempt records.

## 11. PS-006 Smoke Script

Create:

`scripts/ps006_provider_router_core_smoke.py`

The smoke script must run at least three scenarios:

### Scenario A: First Provider Succeeds

Provider chain:

- AlwaysSucceedProvider

Expected:

- ok true
- one attempt
- selected provider is first provider
- fallback_used false

### Scenario B: First Fails, Second Succeeds

Provider chain:

- AlwaysFailProvider
- AlwaysSucceedProvider

Expected:

- ok true
- two attempts
- selected provider is second provider
- fallback_used true
- failed attempt preserved

### Scenario C: Disabled Provider, Then Success

Provider chain:

- DisabledProvider
- AlwaysSucceedProvider

Expected:

- ok true
- two attempts
- disabled attempt preserved
- selected provider is second provider
- fallback_used true

### Scenario D: All Fail

Provider chain:

- AlwaysFailProvider
- AlwaysFailProvider

Expected:

- ok false
- two attempts
- no selected provider
- no fake output
- failure evidence preserved

## 12. Local Outputs

The smoke script must write:

- `/tmp/proofstudio-ps-006/provider-router-core-summary.json`
- `/tmp/proofstudio-ps-006/provider-router-core-attempts.json`

No B2 upload is required in PS-006.

Reason:

PS-006 tests deterministic router behavior. B2 + Genblaze upload behavior is already proven in PS-001A, PS-004, and PS-005.

B2 + Genblaze re-enters in PS-007 when the real fallback chain is implemented.

## 13. Documentation Proof

Create:

`docs/ps-006-provider-router-core-proof.md`

It must include:

- status
- scenarios tested
- selected provider per scenario
- attempt counts
- fallback behavior
- failure behavior
- why no B2 upload is required in this slice
- truth boundary

## 14. Acceptance Criteria

PS-006 is accepted only if:

- reusable provider router files exist
- smoke script compiles
- smoke script passes all four scenarios
- attempts are JSON serializable
- failure attempts are preserved
- disabled attempts are preserved
- all-fail scenario returns ok false
- no fake success is created
- no secrets are introduced
- no live API keys are required
- no unrelated files are modified

## 15. Failure Conditions

Reject PS-006 if:

- the router hides failed attempts
- the router stops after failure without trying fallback
- disabled providers disappear from the ledger
- all-fail scenario returns success
- fake image/output assets are created
- script requires Cloudflare, Pollinations, Gemini, GMICloud, or any live provider
- code is placed only in scripts with no reusable module
- code touches unrelated slices

## 16. Next Slice Dependency

PS-007 will use this router core to implement the real live fallback chain:

Cloudflare Workers AI primary → Pollinations fallback → B2 + Genblaze manifest.

Therefore PS-006 must keep provider interfaces practical enough for live adapters in PS-007.
