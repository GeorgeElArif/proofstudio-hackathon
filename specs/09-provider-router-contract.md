# Provider Router Contract

## 1. Purpose

The Provider Router selects and attempts AI providers for media jobs.

It must support:

- text generation
- campaign intelligence
- image generation
- video generation
- audio generation
- metadata generation
- review summarization

It must not fake success.

## 2. Provider Job Types

Supported job types:

- campaign_intelligence
- prompt_pack
- image_generation
- image_edit
- video_generation
- audio_generation
- metadata_generation
- review_summary
- export_copy

## 3. Normalized Provider Status

All providers must map results to one of:

- OK
- AUTH_FAILED
- QUOTA_EXCEEDED
- BILLING_REQUIRED
- MODEL_UNAVAILABLE
- SAFETY_BLOCKED
- TIMEOUT
- BAD_REQUEST
- PROVIDER_DOWN
- UNSUPPORTED_MODE
- SKIPPED_MISSING_KEY
- UNKNOWN_ERROR

## 4. Provider Result Shape

A successful provider result must include:

- ok: true
- provider
- model
- job_type
- output_assets
- raw_metadata
- normalized_status: OK
- started_at
- finished_at
- latency_ms
- estimated_cost
- free_or_paid
- notes

A failed provider result must include:

- ok: false
- provider
- model
- job_type
- normalized_status
- raw_error_type
- sanitized_error_message
- retryable
- fallback_allowed
- started_at
- finished_at
- latency_ms
- estimated_cost
- notes

## 5. Provider Interface

Each provider wrapper must implement:

- provider_id
- display_name
- supported_job_types
- supported_budget_modes
- required_env_vars
- estimated_cost_policy
- check_config()
- run(job)
- normalize_error(error)

## 6. Budget Modes

### free-only

Only use providers with free/no-key/free-tier options.

Allowed examples:

- Gemini Flash text if quota available
- Cloudflare Workers AI free allocation
- Pollinations fallback
- OpenRouter free models
- Groq free limits

### cheap

Use free providers first, then very low-cost APIs.

Allowed examples:

- Cloudflare
- Pollinations
- Stability
- Runware
- WaveSpeed

### premium-final

Use high-quality paid providers.

Allowed examples:

- GMICloud
- Gemini / Imagen / Vertex
- Stability premium
- Runway
- Luma
- ElevenLabs

### sponsor-demo

Prioritize sponsor visibility and system proof:

- Genblaze must be visible
- B2 must be visible
- GMICloud preferred if credits exist
- fallback allowed if GMICloud blocked
- no fake success

## 7. Default Image Provider Order

Initial order:

1. GMICloud if premium-final or sponsor-demo and credits exist
2. Cloudflare Workers AI
3. Pollinations
4. Stability
5. Runware
6. Gemini image
7. Imagen / Vertex
8. manual pre-generated asset fallback only if labeled clearly

## 8. Default Text Provider Order

Initial order:

1. Gemini Flash
2. OpenRouter free
3. Groq
4. Mistral
5. Cerebras
6. premium paid model if needed

## 9. Failure Handling

The router must continue if:

- quota exceeded
- billing required
- model unavailable
- timeout
- provider down
- missing optional key
- bad request caused by provider config mismatch

The router must stop if:

- no provider remains
- job violates policy or safety constraints
- required user input is missing
- B2 storage fails after successful output
- manifest verification fails

## 10. Attempt Recording

Every provider event must be recorded:

- skipped
- failed
- successful
- selected
- rejected
- retried

No silent fallbacks.

## 11. Storage Rule

If a provider succeeds:

1. save output locally
2. upload output to B2 through Genblaze-compatible flow
3. write manifest
4. read manifest back
5. verify manifest
6. record asset URLs and hashes

## 12. Truth Boundary

The router must never say a provider generated an asset if the provider failed.

The router must never say a manifest proves content truth.

The router must never hide quota, billing, or auth failures.
