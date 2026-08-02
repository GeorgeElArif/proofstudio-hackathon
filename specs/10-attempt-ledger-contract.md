# Attempt Ledger Contract

## 1. Purpose

The Attempt Ledger is a durable record of everything ProofStudio tried while producing a campaign asset.

It turns provider failure into production evidence.

## 2. Ledger Scope

A ledger can exist for:

- campaign intelligence run
- visual generation run
- audio generation run
- video generation run
- export pack run
- provider audition run
- provider swap rerun

## 3. Ledger Object

Required fields:

- ledger_id
- campaign_id
- job_id
- job_type
- budget_mode
- created_at
- completed_at
- final_status
- selected_provider
- selected_model
- attempts
- output_assets
- b2_artifacts
- manifest_uri
- manifest_hash
- truth_boundary

## 4. Attempt Object

Required fields:

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

## 5. Status Values

Attempt status:

- skipped
- started
- failed
- succeeded
- selected
- rejected
- retried

Normalized status:

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

## 6. Cost Ledger Fields

For each attempt:

- estimated_cost_amount
- estimated_cost_currency
- cost_basis
- free_tier_used
- paid_required
- provider_credit_note

Cost basis examples:

- free allocation
- no-key public endpoint
- paid credits
- unknown
- blocked before billing
- provider did not return usage

## 7. B2 Storage

The ledger must be stored as JSON in B2.

Suggested prefix:

- proofstudio/campaigns/{campaign_id}/jobs/{job_id}/attempt-ledger.json

For smoke tests:

- proofstudio/ps-004/attempt-ledgers/{run_id}.json

## 8. Manifest Inclusion

The Attempt Ledger must be included as a manifest asset when possible.

The manifest should include:

- generated asset
- prompt packet
- provider note
- attempt ledger
- review record if available
- export note if available

## 9. UI Usage

The Attempt Ledger powers:

- Mission Control
- Failure-as-Proof Timeline
- Model Audition Board
- Why This Provider?
- Cost Ledger
- Provenance Passport
- Export Pack

## 10. Sanitization

Raw provider errors must not expose secrets.

Rules:

- never store API keys
- never store Authorization headers
- never store signed URLs longer than needed
- avoid storing full presigned URLs in final exported artifacts
- store sanitized error summaries
- keep raw stack traces local only unless explicitly safe

## 11. Acceptance Criteria

A valid ledger must:

- include at least one attempt
- include final status
- include skipped providers if relevant
- include failed providers if relevant
- include selected provider if success
- include all successful output asset refs
- serialize to JSON
- upload to B2
- verify through Genblaze manifest when included as an asset
