# PS-004 Provider Router + Cloudflare Workers AI Visual Proof

## 1. Purpose

PS-004 starts the real ProofStudio provider-router architecture.

The goal is not just to call Cloudflare. The goal is to prove this flow:

campaign prompt
→ provider router
→ provider attempt ledger
→ Cloudflare Workers AI visual generation
→ fallback-ready result contract
→ B2 storage
→ Genblaze manifest
→ manifest read-back verification

## 2. Why This Slice Exists

PS-001A proved B2 + Genblaze.

PS-002 proved Gemini campaign intelligence.

PS-003 proved that Gemini / Imagen image generation is currently blocked by quota or paid-plan requirements.

PS-004 proves that ProofStudio can move to an available free/cheap provider without losing the product thesis.

## 3. Product Value

This slice supports:

- Credit-Aware Provider Router
- Failure-as-Proof Timeline
- Why This Provider?
- Cost Ledger
- Provenance Passport
- Model Audition Board
- B2 system of record
- Genblaze manifest verification

## 4. Provider Strategy

Initial image provider order for this slice:

1. Cloudflare Workers AI primary image model
2. Cloudflare Workers AI fallback image model
3. Pollinations fallback is reserved for PS-005, not implemented here

Default Cloudflare models:

- @cf/bytedance/stable-diffusion-xl-lightning
- @cf/stabilityai/stable-diffusion-xl-base-1.0

## 5. Required Environment Variables

Cloudflare values must only exist in local .env, never committed.

Required Cloudflare variables:

- CLOUDFLARE_ACCOUNT_ID
- CLOUDFLARE_API_TOKEN
- CLOUDFLARE_IMAGE_MODEL_PRIMARY
- CLOUDFLARE_IMAGE_MODEL_FALLBACK

Existing B2 variables are also required:

- B2_KEY_ID
- B2_APP_KEY
- B2_BUCKET
- B2_REGION

## 6. Normalized Error Mapping

Cloudflare provider errors must map to Provider Router statuses:

- OK
- AUTH_FAILED
- QUOTA_EXCEEDED
- BILLING_REQUIRED
- MODEL_UNAVAILABLE
- SAFETY_BLOCKED
- TIMEOUT
- BAD_REQUEST
- PROVIDER_DOWN
- SKIPPED_MISSING_KEY
- UNKNOWN_ERROR

## 7. Attempt Ledger Requirements

Every provider attempt must record:

- provider: cloudflare-workers-ai
- model
- job_type: image_generation
- attempt_index
- started_at
- finished_at
- latency_ms
- status
- normalized_status
- raw_error_type if failed
- sanitized_error_message if failed
- estimated_cost
- free_or_paid
- fallback_allowed
- output asset refs if successful

The ledger must serialize to JSON.

## 8. B2 Storage Requirements

On success, PS-004 must store:

- generated image
- prompt packet JSON
- provider attempt ledger JSON
- provider note Markdown

Suggested local output folder:

/tmp/proofstudio-ps-004/

Suggested B2 prefix:

proofstudio/ps-004/

## 9. Genblaze Requirements

The generated image, prompt packet, provider note, and attempt ledger must be included as assets in a Genblaze manifest.

A real pass requires:

- ok: true
- stored_manifest_verify: true
- transfer_failures: []
- stored_transfer_failures: []

## 10. Script Target

Create:

scripts/ps004_provider_router_cloudflare_smoke.py

The script should:

1. Load .env.
2. Validate required B2 variables.
3. Validate Cloudflare variables.
4. Build a ProofStudio visual prompt packet.
5. Create a provider job.
6. Try Cloudflare primary model.
7. If primary fails, record attempt and try fallback model.
8. If one succeeds, save returned image bytes locally.
9. Write attempt ledger.
10. Write provider note.
11. Upload artifacts through Genblaze/B2 flow.
12. Read manifest back.
13. Verify manifest.
14. Print final summary JSON.

## 11. Failure Rules

Do not fake success.

If Cloudflare is missing keys:

- status must be SKIPPED_MISSING_KEY
- script should fail with clear setup instruction
- no fake local image should be generated

If Cloudflare returns quota or auth errors:

- record them in the attempt ledger
- fail honestly if no fallback provider succeeds

If B2 upload fails:

- fail the whole slice

If Genblaze manifest verification fails:

- fail the whole slice

## 12. Acceptance Criteria

PS-004 is accepted only if one of these is true.

### Accepted Pass

- Cloudflare returns image bytes
- image saved locally
- attempt ledger saved locally
- image uploaded to B2
- attempt ledger uploaded to B2
- Genblaze manifest written to B2
- stored manifest read back
- manifest verifies
- zero transfer failures

### Accepted Blocked

Only acceptable if Cloudflare account or API entitlement blocks the run.

Blocked status must include:

- exact normalized error
- sanitized provider error
- no fake generated asset
- clear next setup requirement

## 13. Judge Value

This slice proves:

- ProofStudio can move beyond one provider
- provider failures are first-class evidence
- free/cheap generation paths can feed the same B2/Genblaze proof pipeline
- the future paid-provider upgrade path is clean

## 14. GLM 5.2 Implementation Rules

GLM 5.2 must implement only this slice.

GLM must not:

- touch unrelated branches
- commit secrets
- fake provider success
- skip attempt ledger
- skip B2 storage on success
- skip Genblaze verification on success
- silently swallow provider failures

GLM must produce:

- script
- docs update if needed
- compile check
- smoke command
- clear changed-file summary
