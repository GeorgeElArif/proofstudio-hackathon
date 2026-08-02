# PS-007 Live ProviderRouter Chain

## 1. Purpose

PS-007 proves the real ProofStudio provider-router product thesis:

Cloudflare Workers AI primary provider
→ Pollinations no-key fallback provider
→ full attempt ledger
→ generated visual asset
→ Backblaze B2 storage
→ Genblaze manifest
→ stored manifest verification

This slice connects the reusable ProviderRouter core from PS-006 with the live provider behavior proven in PS-004 and PS-005.

## 2. Why This Slice Exists

PS-004 proved Cloudflare Workers AI can generate an image and store it through B2 + Genblaze.

PS-005 proved Pollinations can work as a no-key fallback provider and store its output through B2 + Genblaze.

PS-006 proved deterministic reusable ProviderRouter behavior.

PS-007 must now prove the real live chain:

- real Cloudflare provider adapter
- real Pollinations provider adapter
- reusable ProviderRouter from src/proofstudio/providers/router.py
- fallback behavior
- B2 + Genblaze storage
- full ProviderAttempt ledger evidence

## 3. Product Meaning

ProofStudio is not a one-provider image generator.

It is a provenance-aware AI media operations system that can:

- pick a provider
- explain why that provider was tried
- preserve failed and skipped attempts
- fall back when allowed
- store the chosen output
- store the full attempt ledger
- produce a manifest-backed provenance record

PS-007 is the first live proof of that end-to-end loop.

## 4. Required Files

Create or modify only PS-007-related files.

Expected new files:

- src/proofstudio/providers/live_cloudflare.py
- src/proofstudio/providers/live_pollinations.py
- src/proofstudio/provenance/__init__.py
- src/proofstudio/provenance/genblaze_store.py
- scripts/ps007_live_provider_router_chain_smoke.py
- docs/ps-007-live-provider-router-chain-proof.md

Allowed modification:

- src/proofstudio/providers/__init__.py only if needed for clean exports.

Do not rewrite PS-004, PS-005, or PS-006 proof scripts.

Do not delete historical proof scripts.

## 5. Non-Goals

Do not build a web app.

Do not add FastAPI yet.

Do not add a database.

Do not create UI.

Do not introduce C2PA claims.

Do not fake provider output.

Do not upload placeholder media.

Do not hide failed attempts.

Do not require paid providers beyond the existing Cloudflare credentials already configured locally.

## 6. Provider Chain

Default provider order:

1. Cloudflare Workers AI
2. Pollinations

Provider IDs:

- cloudflare-workers-ai
- pollinations

Job type:

- image_generation

Cloudflare API method:

- workers-ai-run

Pollinations API method:

- pollinations-image-get

Cloudflare model defaults:

- CLOUDFLARE_IMAGE_MODEL_PRIMARY if set
- otherwise @cf/bytedance/stable-diffusion-xl-lightning

Pollinations model label:

- pollinations-image-default

## 7. Required Environment Variables

Required for B2 + Genblaze:

- B2_KEY_ID
- B2_APP_KEY
- B2_BUCKET
- B2_REGION

Required for Cloudflare attempt:

- CLOUDFLARE_ACCOUNT_ID
- CLOUDFLARE_API_TOKEN

Optional:

- CLOUDFLARE_IMAGE_MODEL_PRIMARY
- CLOUDFLARE_IMAGE_MODEL_FALLBACK
- POLLINATIONS_ENABLED
- POLLINATIONS_WIDTH
- POLLINATIONS_HEIGHT
- POLLINATIONS_MODEL_NAME
- PROOFSTUDIO_BUDGET_MODE

If Cloudflare credentials are missing, Cloudflare must produce a skipped attempt with normalized status SKIPPED_MISSING_KEY, then the router must try Pollinations.

If POLLINATIONS_ENABLED=false, Pollinations must produce a skipped attempt with normalized status SKIPPED_DISABLED.

## 8. Normalized Statuses

The live providers and router must use the statuses from PS-006:

- OK
- MODEL_UNAVAILABLE
- SAFETY_BLOCKED
- TIMEOUT
- BAD_REQUEST
- PROVIDER_DOWN
- UNSUPPORTED_MODE
- SKIPPED_DISABLED
- SKIPPED_MISSING_KEY
- QUOTA_OR_BILLING_BLOCKED
- UNKNOWN_ERROR

## 9. Attempt Ledger Requirements

Every live attempt must use the full ProviderAttempt contract from PS-006.

Every attempt must include:

- attempt_id
- attempt_index
- provider
- model
- api_method
- job_type
- status
- normalized_status
- started_at
- finished_at
- latency_ms
- retryable
- fallback_allowed
- skip_reason
- raw_error_type
- sanitized_error_message
- estimated_cost
- free_or_paid
- output_asset_refs
- notes

The final attempt ledger must preserve every provider attempt, including:

- skipped attempts
- failed attempts
- successful attempt
- fallback reason
- selected provider
- selected model

## 10. Live Provider Adapter Requirements

### Cloudflare Adapter

Create:

src/proofstudio/providers/live_cloudflare.py

It must:

1. Implement the PS-006 Provider protocol.
2. Use CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN.
3. Call Cloudflare Workers AI image endpoint.
4. Return image bytes only on true success.
5. Detect provider errors.
6. Normalize auth, quota, billing, model, timeout, and provider errors.
7. Never expose the API token.
8. Never write a fake image.
9. Record full ProviderAttempt evidence.

If Cloudflare succeeds, router should stop and Pollinations should not be called.

If Cloudflare fails or is skipped, router should try Pollinations if fallback is allowed.

### Pollinations Adapter

Create:

src/proofstudio/providers/live_pollinations.py

It must:

1. Implement the PS-006 Provider protocol.
2. Require no API key.
3. Respect POLLINATIONS_ENABLED.
4. Call the Pollinations image endpoint.
5. Detect actual MIME from bytes.
6. Reject HTML, JSON errors, tiny payloads, and non-image bytes.
7. Never fake success.
8. Record full ProviderAttempt evidence.

## 11. Output Artifact Requirements

The PS-007 smoke script must write local files under:

/tmp/proofstudio-ps-007/

Required local outputs:

- proofstudio-ps007-hero.<detected_ext>
- proofstudio-ps007-prompt-packet.json
- proofstudio-ps007-attempt-ledger.json
- proofstudio-ps007-provider-note.md
- failed-provider-attempts.json if failed or blocked
- last-run-summary.json

B2 prefix:

proofstudio/ps-007

## 12. B2 + Genblaze Requirements

Create:

src/proofstudio/provenance/genblaze_store.py

It should provide reusable storage helpers based on the proven working pattern:

- S3StorageBackend.for_backblaze(...)
- ObjectStorageSink(...)
- Pipeline.ingest(...) without sink
- sink.write_run(result.run, result.manifest)
- result.manifest.verify()
- sink.read_manifest(result.run, verify=True)

The PS-007 script must store:

- generated image
- prompt packet JSON
- full attempt ledger JSON
- provider note Markdown

A real pass requires:

- in_memory_manifest_verify true
- stored_manifest_verify true
- transfer_failures []
- stored_transfer_failures []
- asset_count >= 4

## 13. Script Target

Create:

scripts/ps007_live_provider_router_chain_smoke.py

The script must:

1. Load .env.
2. Validate required B2 variables.
3. Build a ProofStudio prompt packet.
4. Instantiate Cloudflare provider.
5. Instantiate Pollinations provider.
6. Run ProviderRouter with Cloudflare first, Pollinations second.
7. Preserve every full attempt record.
8. Save selected image locally with MIME-correct extension.
9. Write prompt packet.
10. Write full attempt ledger.
11. Write provider note.
12. Upload all four artifacts through Genblaze/B2.
13. Read stored manifest back.
14. Verify manifest.
15. Print final summary JSON.
16. Write last-run-summary.json.

## 14. Required Scenarios to Support

The script must support these real-world outcomes:

### Scenario A: Cloudflare succeeds

Expected:

- ok true
- selected_provider cloudflare-workers-ai
- Pollinations not called
- attempt_count 1
- fallback_used false
- B2 + Genblaze success

### Scenario B: Cloudflare missing key or fails, Pollinations succeeds

Expected:

- ok true
- selected_provider pollinations
- attempt_count >= 2
- fallback_used true
- Cloudflare skipped or failed attempt preserved
- Pollinations OK attempt preserved
- B2 + Genblaze success

### Scenario C: All providers fail or are disabled

Expected:

- ok false
- no fake output
- failed-provider-attempts.json written
- no fake B2 image upload
- full attempt evidence preserved

The normal live smoke will run once with the current local environment.

## 15. Validation Requirements

PS-007 acceptance requires:

- script compiles
- live providers compile
- reusable Genblaze storage helper compiles
- secret scan passes
- live smoke produces ok true OR accepted blocked
- if ok true:
  - selected_provider is cloudflare-workers-ai or pollinations
  - selected_model is present
  - image_mime_type matches actual bytes
  - image_sha256 is present
  - attempt_count >= 1
  - full attempt ledger has all required fields
  - B2 asset URLs are present
  - manifest_uri is present
  - in_memory_manifest_verify true
  - stored_manifest_verify true
  - transfer_failures []
  - stored_transfer_failures []
- if blocked:
  - failed-provider-attempts.json exists
  - no fake image is uploaded
  - normalized failure statuses are explicit
  - next remediation is clear

## 16. Failure Conditions

Reject PS-007 if:

- it does not use ProviderRouter from PS-006
- it writes compact attempts instead of full ProviderAttempt records
- it loses failed or skipped attempts
- it fakes image output
- it uploads placeholder media
- it hides provider errors
- it leaks secrets
- it makes C2PA/legal authenticity claims
- it requires manual provider calls outside the script
- it modifies unrelated slices

## 17. Documentation Proof

Create:

docs/ps-007-live-provider-router-chain-proof.md

It must include:

- status
- selected provider
- selected model
- whether fallback was used
- attempt count
- attempt status summary
- B2 asset summary
- manifest URI
- manifest hash
- why this proves the product thesis
- truth boundary

## 18. Truth Boundary

PS-007 proves live provider routing, fallback behavior, evidence capture, B2 storage, Genblaze manifest writing, and byte-level manifest verification.

It does not prove:

- semantic truth
- legal authenticity
- human authorship
- C2PA authenticity
- final production security
- final UI behavior

Those require later slices.
