# PS-011 Review Room / Provenance Passport API

## 1. Purpose

PS-011 creates the first product-facing Provenance Passport API for ProofStudio.

Previous milestones proved the underlying system:

- PS-006: ProviderRouter core
- PS-007: live provider chain + B2 + Genblaze
- PS-008: backend API skeleton
- PS-009: API live run bridge
- PS-010: run archive + rehydrate from B2 evidence

PS-011 turns that evidence into a Review Room object that a user, judge, client, or reviewer can understand.

The key product endpoint is:

`GET /runs/{run_id}/passport`

In service-only mode, the equivalent service method may be:

`get_run_passport(run_id)`

## 2. Product Meaning

ProofStudio should not only store evidence.

It should explain evidence.

The Provenance Passport answers:

- What was generated?
- Which provider generated it?
- Which model was used?
- Which attempts happened?
- Did fallback happen?
- What failed or was skipped?
- Which asset was produced?
- What are the asset hashes?
- Where is the manifest?
- Was the manifest verified?
- Is there a durable archive?
- Was the run rehydrated from B2 evidence?
- What does this proof claim?
- What does this proof not claim?

This slice converts raw proof metadata into a clear review artifact.

## 3. Demo Value

This is a judge-facing feature.

The demo moment:

1. Create or rehydrate a run.
2. Open its Provenance Passport.
3. Show a clean, structured object:
   - provider/model
   - attempt timeline
   - asset hashes
   - manifest verification
   - archive/rehydration proof
   - truth boundary
4. Explain that ProofStudio is a system of record, not just an image generator.

## 4. Current Foundation

Completed and available:

- PS-009 can create live API runs.
- PS-010 can archive and rehydrate runs from B2 object content.
- API/service layer currently runs in service_only mode because FastAPI is not installed.
- Existing service names should be inspected before editing:
  - `ProofStudioService`
  - `create_default_service`
  - `InMemoryStore`

PS-011 must build on current implementation reality, not guessed names.

## 5. Non-Goals

Do not build frontend UI.

Do not add authentication.

Do not add production database.

Do not deploy.

Do not add background workers.

Do not rerun providers just to build a passport.

Do not upload fake passport artifacts.

Do not fake manifest verification.

Do not claim C2PA authenticity.

Do not claim legal authenticity.

Do not claim semantic truth.

Do not claim human authorship.

Do not modify historical proof scripts.

## 6. Required Files

Allowed new files:

- `src/proofstudio/api/passport.py`
- `scripts/ps011_provenance_passport_api_smoke.py`
- `docs/ps-011-review-room-provenance-passport-api-proof.md`

Allowed modifications:

- `src/proofstudio/api/models.py`
- `src/proofstudio/api/store.py`
- `src/proofstudio/api/services.py`
- `src/proofstudio/api/app.py`
- `src/proofstudio/api/archive.py` only if a tiny reusable helper is required

Do not modify historical proof scripts:

- `scripts/ps004_provider_router_cloudflare_smoke.py`
- `scripts/ps005_pollinations_fallback_smoke.py`
- `scripts/ps006_provider_router_core_smoke.py`
- `scripts/ps007_live_provider_router_chain_smoke.py`
- `scripts/ps008_backend_api_smoke.py`
- `scripts/ps009_api_live_run_bridge_smoke.py`
- `scripts/ps010_run_archive_rehydrate_b2_smoke.py`

## 7. Passport API / Service Behavior

Add a service method such as:

- `get_run_passport(run_id)`

If FastAPI route wiring is present or cleanly supported, expose:

- `GET /runs/{run_id}/passport`

FastAPI is not required for this slice because current environment is service_only.

Passport generation must:

1. Load run from the existing store/service.
2. Load attempts through normal readback methods.
3. Load assets through normal readback methods.
4. Load manifest through normal readback methods.
5. Include archive/rehydration metadata when available.
6. Return a structured passport object.
7. Never call providers.
8. Never call B2 unless explicitly reading already-known evidence is necessary.
9. Never create fake media.
10. Never fake verification.

## 8. Passport Schema

Create `src/proofstudio/api/passport.py`.

It should expose functions such as:

- `build_provenance_passport(...)`
- `validate_provenance_passport(...)`
- `write_passport_local(...)`

Exact names may vary, but the capability must be clear and tested.

The passport object must include these top-level sections:

### 8.1 passport_identity

Required fields:

- passport_id
- passport_schema_version
- run_id
- campaign_id
- created_at
- source

Source examples:

- live_run
- rehydrated_run
- archive_rehydrated_run

### 8.2 run_summary

Required fields:

- status
- selected_provider
- selected_model
- api_method
- job_type
- fallback_used
- attempt_count
- asset_count
- manifest_uri
- manifest_hash

### 8.3 campaign_snapshot

Include campaign data that is safe and already stored:

- campaign_id
- name
- brief
- target_audience
- platform
- objective

### 8.4 generation_summary

Include:

- generated_media_present
- primary_asset_uri
- primary_asset_media_type
- primary_asset_sha256
- primary_asset_size_bytes
- image_mime_type if available
- image_sha256 if available

### 8.5 attempt_timeline

A judge-friendly timeline derived from full ProviderAttempt records.

Each timeline entry should include:

- attempt_index
- provider
- model
- api_method
- status
- normalized_status
- latency_ms
- retryable
- fallback_allowed
- skip_reason
- sanitized_error_message
- output_asset_refs

The passport may include the full raw attempts separately, but the timeline must be readable.

### 8.6 assets

Include asset records:

- url
- media_type
- sha256
- size_bytes
- metadata

### 8.7 manifest_verification

Include:

- manifest_uri
- manifest_hash
- in_memory_manifest_verify
- stored_manifest_verify
- transfer_failures
- stored_transfer_failures

### 8.8 archive_and_rehydration

Include when available:

- archive_uri
- archive_sha256
- archive_storage_mode
- rehydrate_source
- rehydrate_completed
- restored_manifest_uri
- restored_manifest_hash
- no_live_provider_call_during_rehydrate

If unavailable, include explicit not_available status instead of omitting the section.

### 8.9 trust_boundary

Include both:

- claims
- non_claims

Claims may include:

- provider attempt evidence was captured
- asset hashes were recorded
- B2/Genblaze manifest verification occurred when present
- archive rehydration occurred when present

Non-claims must include:

- semantic truth
- legal authenticity
- C2PA authenticity
- human authorship
- final production security

### 8.10 review_room_summary

A concise human-readable summary:

- one_sentence_summary
- risk_flags
- reviewer_next_actions

Risk flags examples:

- fallback_used
- failed_attempts_present
- manifest_not_verified
- archive_not_available
- generated_media_missing

## 9. Attempt Contract

Passport building must validate that attempts use the full PS-006 20-field contract when attempts exist.

Required attempt fields:

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

Do not use compact attempts as the source of truth.

## 10. Service Readback Integration

The passport must use normal service/store readbacks:

- `get_run`
- `get_run_attempts`
- `get_run_assets`
- `get_run_manifest`

If the run was rehydrated in PS-010, the passport should work from the fresh rehydrated store state.

## 11. Smoke Script

Create:

`scripts/ps011_provenance_passport_api_smoke.py`

The smoke script must:

1. Set output directory:
   `/tmp/proofstudio-ps-011`
2. Create a service/store.
3. Create campaign.
4. Create live run with `run_live=true`.
5. Archive and rehydrate the run using PS-010 archive functions if practical.
6. Build passport from the rehydrated service/store.
7. Validate passport schema.
8. Validate attempt timeline.
9. Validate manifest verification section.
10. Validate archive/rehydration section.
11. Validate trust boundary/non-claims.
12. Verify no provider call happened during passport generation itself.
13. Verify no fake media was created.
14. Write passport JSON:
    `/tmp/proofstudio-ps-011/provenance-passport.json`
15. Write summary JSON:
    `/tmp/proofstudio-ps-011/provenance-passport-summary.json`
16. Write transcript JSON:
    `/tmp/proofstudio-ps-011/provenance-passport-transcript.json`
17. Print final summary JSON.

If live run blocks, the script may exit 0 only if:

- blocked state is honest
- no fake passport success is claimed
- passport either is not created or clearly represents blocked/no-media state
- summary documents the blocked reason

## 12. Required Summary Fields

The PS-011 summary must include:

- ok
- slice
- live_run_attempted
- live_run_status
- live_run_completed
- rehydrate_used
- passport_created
- passport_validated
- passport_source
- passport_path
- run_id
- campaign_id
- selected_provider
- selected_model
- fallback_used
- attempt_count
- timeline_entries
- asset_count
- manifest_uri
- manifest_hash
- stored_manifest_verify
- archive_uri
- archive_sha256
- rehydrate_source
- trust_boundary_checked
- non_claims_checked
- no_provider_call_during_passport
- no_fake_media
- summary_path
- transcript_path
- truth_boundary

## 13. Acceptance Criteria

PS-011 is accepted if:

- passport module exists
- passport can be built from a live or rehydrated run
- passport uses normal service readbacks
- attempt timeline is derived from full attempts
- manifest verification section is present
- archive/rehydration section is present or explicitly not_available
- trust boundary includes claims and non-claims
- no provider calls happen during passport generation
- no fake media is created
- no C2PA/legal/semantic truth claims are made
- historical proof scripts remain untouched
- smoke summary ok true

## 14. Failure Conditions

Reject PS-011 if:

- passport generation reruns providers
- passport uses compact attempts as source of truth
- manifest verification is faked
- archive/rehydration proof is faked
- blocked/no-media runs are presented as successful media
- C2PA/legal/human-authorship claims are made
- historical proof scripts are modified
- unrelated files are changed
- secrets are introduced

## 15. Documentation Proof

Create:

`docs/ps-011-review-room-provenance-passport-api-proof.md`

It must include:

- status
- passport source
- selected provider/model
- attempt timeline summary
- asset/hash summary
- manifest verification summary
- archive/rehydration summary
- trust boundary
- reviewer next actions
- limitations and next improvements
- connection to PS-010

## 16. Truth Boundary

PS-011 proves that ProofStudio can transform run evidence into a structured Review Room / Provenance Passport object.

It does not prove:

- semantic truth
- legal authenticity
- C2PA authenticity
- human authorship
- final UI behavior
- production security
- production persistence

Those are later slices.
