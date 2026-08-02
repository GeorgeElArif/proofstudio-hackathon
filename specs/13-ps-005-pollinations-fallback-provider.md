# PS-005 Pollinations No-Key Fallback Provider Proof

## 1. Purpose

PS-005 proves ProofStudio can generate a visual asset through a no-key emergency fallback provider while preserving the same B2 + Genblaze provenance pipeline.

This is not the premium final visual provider.

This is a fallback path for:

- no credits
- quota exhaustion
- paid-plan blocks
- provider outage
- fast demo recovery

## 2. Why This Slice Exists

PS-003 proved that Gemini / Imagen visual generation is blocked under current free account limits.

PS-004 proved that Cloudflare Workers AI can generate a visual asset and store it through B2 + Genblaze.

PS-005 adds a second provider path that requires no API key, giving ProofStudio a stronger fallback story.

## 3. Product Value

This slice supports:

- Provider fallback resilience
- Free-only budget mode
- Failure-as-Proof Timeline
- Why This Provider?
- Model Audition Board
- Export Pack continuity
- B2 system of record
- Genblaze manifest verification

## 4. Provider Strategy

Provider:

- Pollinations

Provider ID:

- pollinations

Job type:

- image_generation

API method:

- pollinations-image-get

Default endpoint pattern:

- https://image.pollinations.ai/prompt/{encoded_prompt}

The script may add safe query params for deterministic or better output, but must not require secrets.

## 5. Required Environment Variables

No provider key is required.

Existing B2 variables are required:

- B2_KEY_ID
- B2_APP_KEY
- B2_BUCKET
- B2_REGION

Optional:

- POLLINATIONS_ENABLED=true

If POLLINATIONS_ENABLED=false, the script should skip with normalized status UNSUPPORTED_MODE or SKIPPED_DISABLED.

## 6. Normalized Error Mapping

Pollinations provider errors must map to Provider Router statuses:

- OK
- MODEL_UNAVAILABLE
- SAFETY_BLOCKED
- TIMEOUT
- BAD_REQUEST
- PROVIDER_DOWN
- UNSUPPORTED_MODE
- UNKNOWN_ERROR

## 7. Attempt Ledger Requirements

Every attempt must record:

- provider: pollinations
- model or endpoint label
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

On success, PS-005 must store:

- generated image
- prompt packet JSON
- provider attempt ledger JSON
- provider note Markdown

Suggested local output folder:

/tmp/proofstudio-ps-005/

Suggested B2 prefix:

proofstudio/ps-005/

## 9. Genblaze Requirements

The generated image, prompt packet, provider note, and attempt ledger must be included as assets in a Genblaze manifest.

A real pass requires:

- ok: true
- stored_manifest_verify: true
- transfer_failures: []
- stored_transfer_failures: []

## 10. Script Target

Create:

scripts/ps005_pollinations_fallback_smoke.py

The script should:

1. Load `.env`.
2. Validate required B2 variables.
3. Respect POLLINATIONS_ENABLED if present.
4. Build a ProofStudio visual prompt packet.
5. URL-encode the prompt.
6. Call Pollinations image endpoint.
7. Detect actual image MIME from bytes.
8. Save returned image bytes locally with correct extension.
9. Write attempt ledger.
10. Write prompt packet.
11. Write provider note.
12. Upload artifacts through Genblaze/B2 flow.
13. Read manifest back.
14. Verify manifest.
15. Print final summary JSON.

## 11. Failure Rules

Do not fake success.

If Pollinations returns HTML, JSON error, tiny invalid response, timeout, or non-image bytes:

- record failed attempt
- write failed-provider-attempts.json
- exit non-zero
- do not upload fake image

If B2 upload fails:

- fail the whole slice

If Genblaze manifest verification fails:

- fail the whole slice

## 12. Acceptance Criteria

### Accepted Pass

- Pollinations returns valid image bytes
- MIME type is detected from bytes
- image saved locally with correct extension
- attempt ledger saved locally
- image uploaded to B2
- attempt ledger uploaded to B2
- Genblaze manifest written to B2
- stored manifest read back
- manifest verifies
- zero transfer failures

### Accepted Blocked

Only acceptable if Pollinations endpoint is unavailable or blocks the request.

Blocked status must include:

- exact normalized error
- sanitized provider error
- no fake generated asset
- clear next fallback recommendation

## 13. Judge Value

This slice proves ProofStudio can preserve campaign continuity even when premium and key-based image providers fail.

It strengthens the "free-only mode" and makes the provider fallback strategy real instead of theoretical.

## 14. Truth Boundary

Pollinations output is a fallback provider output.

It should not be positioned as the premium final provider unless quality is strong enough.

The app must disclose provider and model/source clearly in the Provenance Passport and Export Pack.
