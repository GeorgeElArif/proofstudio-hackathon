# PS-008 Backend API Skeleton

## 1. Purpose

PS-008 creates the first backend API skeleton for ProofStudio.

Previous slices proved the core pipeline:

- PS-001A: B2 + Genblaze manifest storage
- PS-002: Gemini campaign intelligence proof
- PS-004: Cloudflare visual generation proof
- PS-005: Pollinations fallback proof
- PS-006: reusable ProviderRouter core
- PS-007: live ProviderRouter chain with B2 + Genblaze verification

PS-008 exposes the product concepts through API endpoints so a future UI can create campaigns, start runs, inspect provider attempts, inspect assets, and retrieve manifest evidence.

This is the bridge from smoke scripts to application architecture.

## 2. Product Meaning

ProofStudio needs to become a usable app, not only a collection of proof scripts.

The backend API should make these concepts first-class:

- campaign
- generation run
- provider attempts
- selected provider
- generated asset
- prompt packet
- attempt ledger
- provider note
- Genblaze manifest
- B2 asset refs
- run status

## 3. Non-Goals

Do not build frontend UI.

Do not add authentication yet.

Do not add a production database yet.

Do not deploy.

Do not add background workers yet.

Do not claim C2PA, legal authenticity, semantic truth, or human authorship.

Do not rewrite PS-004, PS-005, PS-006, or PS-007 proof scripts.

Do not require a live provider call for every API smoke test.

## 4. Required Files

Create these files:

- `src/proofstudio/api/__init__.py`
- `src/proofstudio/api/app.py`
- `src/proofstudio/api/models.py`
- `src/proofstudio/api/store.py`
- `src/proofstudio/api/services.py`
- `scripts/ps008_backend_api_smoke.py`
- `docs/ps-008-backend-api-skeleton-proof.md`

Allowed modification:

- `requirements.txt`, `pyproject.toml`, or another dependency file only if the repo already uses one or if needed to declare FastAPI dependencies.
- `src/proofstudio/__init__.py` only if needed for package exports.

Do not touch unrelated slices.

## 5. API Technology

Preferred API framework:

- FastAPI

If FastAPI is already available, use it.

If FastAPI is not available, either:

1. add a minimal dependency declaration and document the install command, or
2. implement the API app in a way that can be imported and tested without network server startup.

The smoke test must run locally in the current virtual environment.

## 6. Required Endpoints

### GET /health

Returns:

- ok
- service
- version
- environment

### GET /version

Returns:

- service
- slice
- git_branch if detectable
- app_version or proof_version

### POST /campaigns

Creates an in-memory campaign record.

Request fields:

- name
- brief
- target_audience optional
- platform optional
- objective optional

Response fields:

- campaign_id
- status
- campaign

### GET /campaigns/{campaign_id}

Returns the stored campaign.

If missing, return 404-style response.

### POST /runs

Creates a generation run request for a campaign.

Request fields:

- campaign_id
- prompt optional
- budget_mode optional
- dry_run optional, default true
- run_live optional, default false

Important:

- By default, this endpoint must not trigger live provider calls.
- The default dry-run path should create a run record with status queued or simulated.
- Live execution can be explicitly supported only when run_live true, but PS-008 acceptance does not require live provider execution.

Response fields:

- run_id
- campaign_id
- status
- selected_provider optional
- fallback_used optional
- attempt_count
- links

### GET /runs/{run_id}

Returns run details.

Response should include:

- run_id
- campaign_id
- status
- selected_provider
- selected_model
- fallback_used
- attempt_count
- manifest_uri if present
- asset_count if present

### GET /runs/{run_id}/attempts

Returns provider attempts for the run.

Attempt records must follow the PS-006 20-field ProviderAttempt shape when attempts exist.

### GET /runs/{run_id}/assets

Returns assets associated with the run.

### GET /runs/{run_id}/manifest

Returns manifest metadata for the run:

- manifest_uri
- manifest_hash
- in_memory_manifest_verify
- stored_manifest_verify
- transfer_failures
- stored_transfer_failures

If no manifest exists yet, return a clear not-ready response.

## 7. Storage Model

Use an in-memory store for PS-008.

Create:

`src/proofstudio/api/store.py`

It should support:

- create campaign
- get campaign
- create run
- get run
- list attempts for run
- list assets for run
- get manifest metadata for run

The store should use clear dictionaries or dataclasses.

No production database in this slice.

## 8. Service Layer

Create:

`src/proofstudio/api/services.py`

It should separate route handlers from business logic.

At minimum:

- create_campaign
- get_campaign
- create_run
- get_run
- get_run_attempts
- get_run_assets
- get_run_manifest

The service layer should be designed so PS-009 or PS-010 can connect it to the live PS-007 pipeline.

## 9. Models

Create:

`src/proofstudio/api/models.py`

Use Pydantic models if FastAPI/Pydantic is available.

If not, use dataclasses or plain validation helpers.

Models should represent:

- CampaignCreate
- CampaignRecord
- RunCreate
- RunRecord
- AttemptRecord
- AssetRecord
- ManifestRecord
- ErrorResponse

## 10. Dry-Run Behavior

Dry-run is the default.

When POST /runs is called with dry_run true or no live flag:

- create a run record
- status should be queued, simulated, or dry_run_created
- no provider should be called
- no B2 upload should happen
- no fake image should be created
- attempts can be empty or can include a clearly marked dry-run note, but must not pretend media was generated

## 11. Optional Live Hook

The API may include a placeholder for live execution.

If implemented, it must be guarded by:

- run_live true

and must reuse PS-007 code paths rather than duplicating provider logic.

PS-008 acceptance does not require live execution through the API.

## 12. Smoke Script

Create:

`scripts/ps008_backend_api_smoke.py`

The smoke script must:

1. Import the API app or service layer.
2. Verify health response.
3. Create a campaign.
4. Fetch the campaign.
5. Create a dry-run generation run.
6. Fetch the run.
7. Fetch run attempts.
8. Fetch run assets.
9. Fetch run manifest.
10. Verify missing campaign/run behavior.
11. Write summary JSON to:

`/tmp/proofstudio-ps-008/backend-api-smoke-summary.json`

12. Print final summary JSON.

The smoke test must not require live provider keys.

The smoke test must not call B2.

The smoke test must not upload anything.

## 13. Local Output

The PS-008 smoke script must write:

- `/tmp/proofstudio-ps-008/backend-api-smoke-summary.json`

Optional:

- `/tmp/proofstudio-ps-008/backend-api-smoke-transcript.json`

## 14. Acceptance Criteria

PS-008 is accepted only if:

- API package files exist
- smoke script compiles
- API app imports
- health endpoint or service health call works
- campaign create/get works
- dry-run run create/get works
- attempts/assets/manifest endpoints return clear valid responses
- missing IDs produce clear error responses
- smoke summary ok true
- no live provider keys are required
- no B2 upload occurs
- no fake generated media is created
- no secrets are introduced
- historical proof scripts are untouched

## 15. Failure Conditions

Reject PS-008 if:

- API smoke requires Cloudflare, Pollinations, Gemini, GMICloud, B2, or Genblaze live credentials
- POST /runs silently calls live providers by default
- dry-run pretends it generated real media
- missing resources crash instead of returning clear errors
- provider attempt schema is compact or inconsistent
- historical proof scripts are modified
- secrets are committed
- unrelated files are changed

## 16. Documentation Proof

Create:

`docs/ps-008-backend-api-skeleton-proof.md`

It must include:

- status
- endpoints implemented
- smoke test summary
- dry-run behavior
- why no live provider call is required in this slice
- how this connects to PS-007
- truth boundary

## 17. Truth Boundary

PS-008 proves the backend API skeleton and in-memory product model.

It does not prove:

- production persistence
- authentication
- authorization
- deployment
- background job execution
- live provider execution through the API
- B2 upload through the API
- C2PA authenticity
- legal authenticity
- semantic truth

Those are later slices.
