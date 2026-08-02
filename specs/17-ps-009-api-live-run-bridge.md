# PS-009 API Live Run Bridge

## 1. Purpose

PS-009 connects the PS-008 backend API skeleton to the PS-007 live ProviderRouter chain.

This slice turns ProofStudio from:

- smoke scripts
- reusable provider code
- an in-memory API model

into a backend that can create a run through the API and, when explicitly requested, execute the live generation/provenance pipeline.

The key product path is:

POST /runs with run_live=true
→ ProviderRouter live chain
→ Cloudflare primary / Pollinations fallback
→ full ProviderAttempt ledger
→ generated asset
→ B2 storage
→ Genblaze manifest
→ API run record updated with proof metadata
→ GET /runs/{run_id} returns real evidence state

## 2. Why This Slice Matters

PS-007 proved the engine.

PS-008 proved the API shell.

PS-009 proves the bridge.

This is the first slice where a product-facing API request can produce live proof-backed AI media output.

## 3. Current Foundation

Already completed:

- PS-006 ProviderRouter Core
- PS-007 Live ProviderRouter Chain
- PS-008 Backend API Skeleton

PS-009 must reuse the existing PS-007 live pipeline behavior instead of duplicating it.

## 4. Non-Goals

Do not build a frontend.

Do not add authentication.

Do not add a production database.

Do not deploy.

Do not add background workers yet.

Do not remove dry-run behavior.

Do not make live execution the default.

Do not fake media.

Do not fake B2 or Genblaze success.

Do not claim C2PA, legal authenticity, semantic truth, or human authorship.

Do not rewrite PS-004, PS-005, PS-006, PS-007, or PS-008 proof scripts.

## 5. Required Files

Expected new or modified files:

Allowed modifications:

- `src/proofstudio/api/models.py`
- `src/proofstudio/api/store.py`
- `src/proofstudio/api/services.py`
- `src/proofstudio/api/app.py`
- `src/proofstudio/provenance/genblaze_store.py` only if a small reusable helper is required
- `scripts/ps009_api_live_run_bridge_smoke.py`
- `docs/ps-009-api-live-run-bridge-proof.md`

Optional new file if needed:

- `src/proofstudio/api/live_bridge.py`

Do not modify historical proof scripts:

- `scripts/ps004_provider_router_cloudflare_smoke.py`
- `scripts/ps005_pollinations_fallback_smoke.py`
- `scripts/ps006_provider_router_core_smoke.py`
- `scripts/ps007_live_provider_router_chain_smoke.py`
- `scripts/ps008_backend_api_smoke.py`

## 6. API Behavior

### Dry-run remains default

POST /runs without run_live=true must behave exactly like PS-008:

- no live provider calls
- no B2 calls
- no Genblaze calls
- no fake media
- status remains dry-run style
- attempts/assets/manifest may be empty or not-ready

### Live run is explicit

POST /runs with run_live=true must execute the live bridge.

Input fields:

- campaign_id
- prompt optional
- budget_mode optional
- dry_run optional
- run_live true

Live run behavior:

1. Validate campaign exists.
2. Build prompt packet from campaign + prompt.
3. Execute PS-007 live ProviderRouter chain behavior.
4. Capture selected provider.
5. Capture selected model.
6. Capture fallback_used.
7. Capture full attempt ledger.
8. Capture generated image metadata.
9. Capture B2 asset refs.
10. Capture Genblaze manifest metadata.
11. Store all run metadata in the in-memory API store.
12. Return the updated run response.

## 7. Reuse Requirement

PS-009 must reuse PS-007 provider and storage code:

- `LiveCloudflareProvider`
- `LivePollinationsProvider`
- `ProviderRouter`
- Genblaze/B2 storage helper from `src/proofstudio/provenance/genblaze_store.py`

It may extract reusable helper functions from PS-007 behavior into a clean module if needed.

It must not shell out to the PS-007 script as the main implementation.

It must not duplicate large blocks of PS-007 code if a reusable service can be created cleanly.

## 8. Live Bridge Service

If creating `src/proofstudio/api/live_bridge.py`, it should expose a function like:

- `execute_live_run(...)`

Input:

- campaign record
- prompt
- budget_mode
- output directory
- B2 prefix

Output:

A structured result containing:

- ok
- selected_provider
- selected_model
- api_method
- job_type
- fallback_used
- attempt_count
- attempts
- image_mime_type
- image_sha256
- local_image
- manifest_hash
- manifest_uri
- in_memory_manifest_verify
- stored_manifest_verify
- transfer_failures
- stored_transfer_failures
- asset_count
- assets
- local_prompt_packet
- local_attempt_ledger
- local_provider_note
- truth_boundary

## 9. Environment Requirements

Live execution requires the same environment as PS-007:

Required for B2 + Genblaze:

- B2_KEY_ID
- B2_APP_KEY
- B2_BUCKET
- B2_REGION

Required for Cloudflare primary attempt:

- CLOUDFLARE_ACCOUNT_ID
- CLOUDFLARE_API_TOKEN

Pollinations fallback requires no key.

If Cloudflare credentials are missing, the Cloudflare attempt must be skipped with a clear normalized status.

If all providers fail or required storage variables are missing, the API live run must return a clear failed/blocked run state.

## 10. Failure Behavior

A failed live run must not crash the API smoke.

It must:

- create a run record
- set status to live_failed or live_blocked
- preserve provider attempts if available
- preserve normalized failure statuses
- not create fake image assets
- not fake a manifest URI
- return clear error details
- write a local blocked summary for the smoke script

## 11. Run Statuses

Suggested statuses:

- dry_run_created
- live_running
- live_completed
- live_failed
- live_blocked

PS-009 acceptance requires at least:

- dry_run_created still works
- live_completed works when providers/storage succeed
- live_failed or live_blocked is represented clearly when live execution cannot complete

## 12. Store Requirements

The in-memory store must support updating a run after live execution.

A live completed run should store:

- status
- selected_provider
- selected_model
- api_method
- job_type
- fallback_used
- attempt_count
- attempts
- assets
- manifest metadata
- local output paths where relevant
- truth boundary

A dry-run run must not pretend to have media or manifest evidence.

## 13. Endpoint Readback Requirements

After a successful live run:

### GET /runs/{run_id}

Must return:

- run_id
- campaign_id
- status live_completed
- selected_provider
- selected_model
- fallback_used
- attempt_count
- asset_count
- manifest_uri

### GET /runs/{run_id}/attempts

Must return full ProviderAttempt-shaped records.

Every attempt must include the PS-006 20 fields:

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

### GET /runs/{run_id}/assets

Must return generated image and supporting artifact refs when live_completed.

### GET /runs/{run_id}/manifest

Must return:

- manifest_uri
- manifest_hash
- in_memory_manifest_verify
- stored_manifest_verify
- transfer_failures
- stored_transfer_failures

## 14. Smoke Script

Create:

`scripts/ps009_api_live_run_bridge_smoke.py`

The smoke script must:

1. Import the API service/app.
2. Lock into service mode if FastAPI is unavailable.
3. Create a campaign.
4. Create a dry-run run and verify no live/B2/fake media.
5. Create a live run with run_live=true.
6. If live succeeds:
   - verify status live_completed
   - verify selected_provider is cloudflare-workers-ai or pollinations
   - verify selected_model exists
   - verify attempt_count >= 1
   - verify at least one OK attempt
   - verify all attempts have 20 required fields
   - verify asset_count >= 4
   - verify manifest_uri exists
   - verify stored_manifest_verify true
   - verify transfer_failures []
   - verify stored_transfer_failures []
   - verify GET-style readbacks for run, attempts, assets, manifest
7. If live is blocked:
   - verify status live_failed or live_blocked
   - verify no fake image or fake manifest
   - verify clear error/blocked reason
8. Write summary JSON to:
   `/tmp/proofstudio-ps-009/api-live-run-bridge-summary.json`
9. Write transcript JSON to:
   `/tmp/proofstudio-ps-009/api-live-run-bridge-transcript.json`
10. Print final summary JSON.

## 15. Required Local Outputs

Success or blocked:

- `/tmp/proofstudio-ps-009/api-live-run-bridge-summary.json`
- `/tmp/proofstudio-ps-009/api-live-run-bridge-transcript.json`

If live succeeds, expected live artifacts under:

- `/tmp/proofstudio-ps-009/live-run/`

## 16. Summary Requirements

The PS-009 summary must include:

- ok
- slice
- framework_mode
- dry_run_checked
- live_run_attempted
- live_run_status
- live_run_completed
- selected_provider
- selected_model
- fallback_used
- attempt_count
- attempts_checked
- assets_checked
- manifest_checked
- manifest_uri
- manifest_hash
- stored_manifest_verify
- transfer_failures
- stored_transfer_failures
- no_fake_media
- dry_run_no_live_calls
- dry_run_no_b2_calls
- readbacks_checked
- truth_boundary
- summary_path
- transcript_path

## 17. Acceptance Criteria

PS-009 is accepted if:

- API still imports
- dry-run behavior from PS-008 still works
- live run bridge is explicit via run_live=true
- live run either completes honestly or fails/blocks honestly
- successful live run stores real provider, attempt, asset, and manifest metadata
- readback services expose the stored live metadata
- attempt ledger uses the full 20-field contract
- no fake media is created
- no fake manifest is created
- no secrets are introduced
- historical scripts are untouched

## 18. Failure Conditions

Reject PS-009 if:

- live execution happens by default
- dry-run calls providers or B2
- live run shells out to old scripts as the main implementation
- attempts are compact instead of full ProviderAttempt records
- failed/skipped attempts are lost
- image output is faked
- B2/Genblaze success is faked
- manifest verification is not checked
- historical proof scripts are modified
- unrelated files are changed
- secrets are printed or committed

## 19. Documentation Proof

Create:

`docs/ps-009-api-live-run-bridge-proof.md`

It must include:

- status
- dry-run behavior
- live-run behavior
- selected provider if live completed
- selected model if live completed
- fallback_used
- attempt_count
- asset_count
- manifest_uri
- manifest_hash
- readback proof
- blocked/failure behavior if applicable
- truth boundary
- connection to PS-007 and PS-008

## 20. Truth Boundary

PS-009 proves that the backend API/service layer can explicitly trigger and store a live proof-backed generation run.

It does not prove:

- production persistence
- background workers
- auth
- deployment
- multi-user security
- semantic truth
- legal authenticity
- C2PA authenticity
- final UI behavior
