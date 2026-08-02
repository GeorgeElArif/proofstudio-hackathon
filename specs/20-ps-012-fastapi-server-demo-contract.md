# PS-012 FastAPI Server Mode + Demo API Contract

## 1. Purpose

PS-012 turns ProofStudio from a service-only backend into a runnable FastAPI demo API.

Previous milestones proved the product spine:

- PS-006: ProviderRouter Core
- PS-007: Live ProviderRouter Chain + B2 + Genblaze
- PS-008: Backend API Skeleton
- PS-009: API to Live Run Bridge
- PS-010: Run Archive + Rehydrate from B2
- PS-011: Review Room / Provenance Passport API

PS-012 must expose the core product path through a stable HTTP API contract.

The demo goal:

uvicorn proofstudio.api.app:app
-> create campaign
-> create run
-> inspect run evidence
-> inspect attempts/assets/manifest
-> inspect Provenance Passport

## 2. Product Meaning

ProofStudio now needs to become demo-accessible.

Judges and reviewers should not need to read Python smoke scripts to understand the system.

They should be able to hit API endpoints and see:

- service health
- version/capabilities
- campaigns
- runs
- run evidence
- attempt ledger
- asset metadata
- manifest verification
- Provenance Passport

This slice is the bridge between backend proof and the future web app.

## 3. Why This Matters

The hackathon requires a working app URL.

Before building the frontend, the backend must be a real server.

PS-012 creates the stable API contract that the app and demo can rely on.

This also reduces future risk:

- UI can be built against real endpoints.
- Demo scripts can use HTTP, not internal Python objects.
- Deployment later becomes simpler.
- The product story becomes easier to show.

## 4. Current Foundation

Current reality:

- FastAPI was previously unavailable in the venv.
- `proofstudio.api.app.app` may currently be `None` when FastAPI is missing.
- Service-only mode has been accepted through PS-011.
- PS-011 added `get_run_passport`.
- PS-009/010/011 proof paths already work at service level.

PS-012 must make FastAPI server mode actually available.

## 5. Non-Goals

Do not build a frontend.

Do not deploy.

Do not add authentication.

Do not add production database.

Do not add background workers.

Do not force live provider calls in every server smoke.

Do not fake media.

Do not fake manifest verification.

Do not fake passport evidence.

Do not claim legal authenticity.

Do not claim C2PA authenticity.

Do not claim semantic truth.

Do not modify historical proof scripts.

## 6. Required Files

Allowed new files:

- `scripts/ps012_fastapi_server_demo_contract_smoke.py`
- `docs/ps-012-fastapi-server-demo-contract-proof.md`

Allowed modified files:

- dependency file if present:
  - `pyproject.toml`
  - `requirements.txt`
  - `requirements-dev.txt`
  - or equivalent existing project dependency file
- `src/proofstudio/api/app.py`
- `src/proofstudio/api/models.py`
- `src/proofstudio/api/services.py`
- `src/proofstudio/api/passport.py` only if a tiny compatibility helper is required
- `src/proofstudio/api/archive.py` only if a tiny compatibility helper is required

Do not modify historical proof scripts:

- `scripts/ps004_provider_router_cloudflare_smoke.py`
- `scripts/ps005_pollinations_fallback_smoke.py`
- `scripts/ps006_provider_router_core_smoke.py`
- `scripts/ps007_live_provider_router_chain_smoke.py`
- `scripts/ps008_backend_api_smoke.py`
- `scripts/ps009_api_live_run_bridge_smoke.py`
- `scripts/ps010_run_archive_rehydrate_b2_smoke.py`
- `scripts/ps011_provenance_passport_api_smoke.py`

## 7. Dependency Requirement

PS-012 must make FastAPI server mode available in a clean way.

Required runtime dependencies:

- `fastapi`
- `uvicorn`

Recommended optional test dependency:

- `httpx`

Implementation should update the existing dependency declaration file if one exists.

If no dependency declaration file exists, create the minimal appropriate one or document the install command clearly.

The smoke script may install nothing automatically unless the project already has a managed dependency flow. It should fail clearly if FastAPI/uvicorn are missing.

## 8. Server App Requirement

`proofstudio.api.app:app` must be a real FastAPI instance when dependencies are installed.

The app must expose:

- title
- version
- service/capabilities metadata
- clear docs at `/docs` through FastAPI defaults

The app must use the existing service layer.

Do not duplicate business logic inside route handlers.

Route handlers should call `ProofStudioService` methods.

## 9. Required HTTP Endpoints

### 9.1 Health

`GET /health`

Returns:

- ok
- service
- mode
- version

### 9.2 Version

`GET /version`

Returns:

- service
- version
- framework_mode
- capabilities

Capabilities should mention, when available:

- provider_router
- live_run_bridge
- b2_archive_rehydrate
- provenance_passport
- fastapi_server

### 9.3 Create Campaign

`POST /campaigns`

Request fields should support current service campaign creation fields.

Response:

- campaign_id
- created campaign data

### 9.4 Get Campaign

`GET /campaigns/{campaign_id}`

Returns campaign record or 404.

### 9.5 Create Run

`POST /runs`

Request fields:

- campaign_id
- prompt optional
- budget_mode optional
- dry_run optional
- run_live optional, default false

Rules:

- default must be safe dry-run
- live provider execution only when `run_live=true`
- no fake media
- clear error handling

### 9.6 Get Run

`GET /runs/{run_id}`

Returns run record or 404.

### 9.7 Get Attempts

`GET /runs/{run_id}/attempts`

Returns attempts list.

### 9.8 Get Assets

`GET /runs/{run_id}/assets`

Returns assets list.

### 9.9 Get Manifest

`GET /runs/{run_id}/manifest`

Returns manifest metadata.

### 9.10 Get Passport

`GET /runs/{run_id}/passport`

Returns Provenance Passport.

Must use `get_run_passport`.

Must not rerun providers.

## 10. Error Handling

HTTP errors must be clean and demo-safe.

Required behavior:

- missing campaign -> 404 or clear 400 depending current service behavior
- missing run -> 404
- invalid request -> 422 or clear 400
- live failure -> structured run status, not unhandled crash
- provider/B2 errors must not print secrets

No stack traces in normal JSON responses.

## 11. Demo Contract Mode

The default PS-012 smoke must validate the API contract without forcing live provider calls.

Default smoke flow:

1. Start/import FastAPI app.
2. Use FastAPI TestClient or equivalent.
3. GET `/health`.
4. GET `/version`.
5. POST `/campaigns`.
6. GET `/campaigns/{campaign_id}`.
7. POST `/runs` with `run_live=false`.
8. GET `/runs/{run_id}`.
9. GET attempts/assets/manifest for dry-run.
10. GET passport for dry-run or verify clear no-evidence state.
11. Confirm no live provider call happened.
12. Confirm no B2 call happened.
13. Confirm no fake media was created.

Optional live mode:

The smoke may support an environment flag such as:

`PROOFSTUDIO_PS012_LIVE=1`

When enabled, it may create a live run and verify:

- attempts
- assets
- manifest
- passport

But default acceptance must not require spending provider credits.

## 12. Passport Behavior in Server Mode

`GET /runs/{run_id}/passport` must work for at least:

- dry-run/no-media state with honest limitations
- live completed state if a live run exists

For dry-run, the passport must not pretend media exists.

It may return:

- generated_media_present false
- manifest unavailable
- archive unavailable
- trust boundary
- reviewer next actions

## 13. Smoke Script

Create:

`scripts/ps012_fastapi_server_demo_contract_smoke.py`

The smoke script must:

1. Set output dir:
   `/tmp/proofstudio-ps-012`
2. Import `proofstudio.api.app`.
3. Verify `app` is not None.
4. Verify FastAPI server mode is active.
5. Use FastAPI TestClient or an equivalent local HTTP client.
6. Validate required endpoints.
7. Create a campaign.
8. Create a safe dry-run.
9. Validate readbacks.
10. Validate passport endpoint.
11. Confirm no live provider call happened in default mode.
12. Confirm no B2 call happened in default mode.
13. Confirm no fake media.
14. Write summary JSON:
    `/tmp/proofstudio-ps-012/fastapi-server-demo-contract-summary.json`
15. Write transcript JSON:
    `/tmp/proofstudio-ps-012/fastapi-server-demo-contract-transcript.json`
16. Print final summary JSON.

Optional live run validation may write extra fields but must not be required by default.

## 14. Required Summary Fields

The PS-012 summary must include:

- ok
- slice
- framework_mode
- fastapi_available
- app_is_fastapi
- server_contract_checked
- health_checked
- version_checked
- campaign_create_checked
- campaign_get_checked
- dry_run_create_checked
- run_get_checked
- attempts_get_checked
- assets_get_checked
- manifest_get_checked
- passport_get_checked
- default_no_live_provider_call
- default_no_b2_call
- no_fake_media
- live_mode_enabled
- live_run_status
- route_count
- docs_available
- summary_path
- transcript_path
- truth_boundary

## 15. Documentation Proof

Create:

`docs/ps-012-fastapi-server-demo-contract-proof.md`

It must include:

- status
- installed/declared dependencies
- server mode result
- endpoint list
- default safe dry-run behavior
- passport endpoint behavior
- optional live mode behavior if tested
- no-provider-call proof in default mode
- no-B2-call proof in default mode
- truth boundary
- connection to PS-011
- next milestone recommendation

## 16. Acceptance Criteria

PS-012 is accepted if:

- FastAPI dependency is declared or installed path is documented
- `proofstudio.api.app:app` is a real FastAPI app
- required endpoints exist
- default smoke validates HTTP API contract
- default smoke does not call live providers
- default smoke does not call B2
- dry-run does not fake media
- passport endpoint returns honest no-media or real evidence state
- service layer remains the source of truth
- historical proof scripts remain untouched
- smoke summary ok true
- secret scan passes

## 17. Failure Conditions

Reject PS-012 if:

- app remains None after dependency setup
- route handlers duplicate business logic instead of using service methods
- default smoke calls live providers
- default smoke calls B2
- dry-run creates fake assets
- passport endpoint fakes evidence
- secrets are printed or committed
- historical proof scripts are modified
- unrelated files are changed
- service-only paths from earlier slices break without reason

## 18. Truth Boundary

PS-012 proves that ProofStudio has a runnable FastAPI demo API contract.

It does not prove:

- production deployment
- public app URL
- authentication
- production database persistence
- background job reliability
- legal authenticity
- C2PA authenticity
- semantic truth
- human authorship

Those are later slices.
