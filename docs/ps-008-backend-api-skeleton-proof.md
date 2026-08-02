# PS-008 Backend API Skeleton Proof

## Status

Accepted pass.

PS-008 introduces the first backend API skeleton for ProofStudio. It exposes
the product concepts (campaign, generation run, provider attempts, generated
asset refs, prompt packet refs, attempt ledger refs, provider note refs,
manifest metadata, run status) through a FastAPI service layer backed by an
in-memory store.

- Overall: `ok: true`
- Framework mode: `fastapi` (FastAPI 0.115.x + Pydantic v2 are installed in the
  project venv, so the real FastAPI app is exercised via `TestClient`; no HTTP
  server is required)
- `framework_mode` is also reported in the smoke summary so a service-only
  fallback path remains available if FastAPI is ever absent
- PS-004, PS-005, PS-006, and PS-007 proof scripts are unchanged

## Slice Scope

This slice is the bridge from smoke scripts to application architecture. It is
intentionally not:

- a frontend
- an authentication / authorization layer
- a production database layer
- a deployment
- a background-worker system
- a live provider execution path
- a B2 upload path
- a Genblaze manifest-writing path
- a C2PA / legal authenticity claim

## Files Created

- `src/proofstudio/api/__init__.py` - API subpackage entry point; re-exports
  models, service, store, and (when FastAPI is importable) `app` / `create_app`.
- `src/proofstudio/api/models.py` - Pydantic v2 request/response models:
  `CampaignCreate`, `CampaignRecord`, `RunCreate`, `RunRecord`,
  `AttemptRecord` (PS-006 20-field shape), `AssetRecord`, `ManifestRecord`,
  `ErrorResponse`.
- `src/proofstudio/api/store.py` - `InMemoryStore`: create/get campaign,
  create/get run, list attempts, list assets, get/set manifest metadata, plus a
  `snapshot()` for auditability.
- `src/proofstudio/api/services.py` - `ProofStudioService` business logic:
  `health`, `version`, `create_campaign`, `get_campaign`, `create_run`,
  `get_run`, `get_run_attempts`, `get_run_assets`, `get_run_manifest`, plus
  registration hooks (`register_attempt`, `register_asset`,
  `register_manifest`) for later slices.
- `src/proofstudio/api/app.py` - FastAPI app wiring endpoints to the service
  layer; `FRAMEWORK_MODE` (`fastapi` or `service_only`), `create_app()`, and a
  module-level `app` singleton.
- `scripts/ps008_backend_api_smoke.py` - smoke test (TestClient-based, no
  server).
- `docs/ps-008-backend-api-skeleton-proof.md` - this file.

Allowed modifications:

- No dependency file was changed. FastAPI, Pydantic, and `TestClient` were
  already installed in the venv, so no `requirements.txt` / `pyproject.toml`
  edit was needed.
- `src/proofstudio/__init__.py` was not modified; `import proofstudio.api`
  works without changes.

## Endpoints / Services Implemented

FastAPI endpoints (all under the in-memory store, dry-run by default):

| Method | Path | Behavior |
|---|---|---|
| `GET` | `/health` | `{ ok, service, version, environment }` |
| `GET` | `/version` | `{ service, slice, git_branch, app_version, proof_version }` |
| `POST` | `/campaigns` | creates an in-memory campaign; returns `{ campaign_id, status, campaign }` |
| `GET` | `/campaigns/{campaign_id}` | returns stored campaign; 404 `ErrorResponse` if missing |
| `POST` | `/runs` | creates a generation run; defaults to dry-run; 404 if campaign missing |
| `GET` | `/runs/{run_id}` | returns run details; 404 if missing |
| `GET` | `/runs/{run_id}/attempts` | returns provider attempts (empty for dry-run); 404 if run missing |
| `GET` | `/runs/{run_id}/assets` | returns assets (empty for dry-run); 404 if run missing |
| `GET` | `/runs/{run_id}/manifest` | returns manifest metadata or a clear not-ready response; 404 if run missing |

Service-layer equivalents (`ProofStudioService`) exist for every endpoint so
the smoke script (and future slices) can exercise the API without an HTTP
server. Missing resources raise `NotFoundError`, which the FastAPI layer maps
to a 404 `ErrorResponse`.

## Smoke Test Summary

Run:

```
python -m py_compile \
  src/proofstudio/api/models.py \
  src/proofstudio/api/store.py \
  src/proofstudio/api/services.py \
  src/proofstudio/api/app.py \
  scripts/ps008_backend_api_smoke.py

python scripts/ps008_backend_api_smoke.py
```

- `py_compile`: clean (all five files compile)
- smoke: `ok: true`
- `framework_mode`: `fastapi`
- endpoints exercised via `fastapi.testclient.TestClient` (no socket, no uvicorn)
- `campaign_created: true`
- `campaign_fetched: true`
- `dry_run_created: true`
- `run_fetched: true`
- `attempts_checked: true`
- `assets_checked: true`
- `manifest_checked: true`
- `missing_campaign_checked: true` (404 `ErrorResponse`, no crash)
- `missing_run_checked: true` (404 for run and its sub-resources, no crash)
- `no_live_provider_calls: true`
- `no_b2_calls: true`
- `no_fake_media: true`
- `attempt_contract_fields: 20` (static check that `AttemptRecord` /
  `REQUIRED_ATTEMPT_FIELDS` exactly matches the PS-006 20-field shape; no
  attempt is fabricated by this check)

Summary: `/tmp/proofstudio-ps-008/backend-api-smoke-summary.json`
Transcript: `/tmp/proofstudio-ps-008/backend-api-smoke-transcript.json`

## Dry-Run Behavior

`POST /runs` defaults to a dry run (`dry_run` defaults to `True`,
`run_live` defaults to `False`). When the dry-run path is taken:

- a run record is created with status `dry_run_created`
- no provider is contacted (Cloudflare, Pollinations, Gemini, GMICloud, ...)
- no B2 upload occurs
- no Genblaze manifest is written
- no media is generated or fabricated
- `attempt_count` is `0` and `GET /runs/{run_id}/attempts` returns an empty list
- `asset_count` is `0` and `GET /runs/{run_id}/assets` returns an empty list
- `GET /runs/{run_id}/manifest` returns `{ ready: false, not_ready_reason: ... }`
  rather than crashing
- `selected_provider`, `selected_model`, `manifest_uri`, `prompt_packet_ref`,
  `attempt_ledger_ref`, and `provider_note_ref` are all `null` on the run record

The dry run never pretends a provider executed or produced media.

## Why No Live Provider Call Is Required in This Slice

PS-008's job is to prove the backend API skeleton and the in-memory product
model: that the product concepts exist as first-class, typed, addressable
resources and that the service layer can create/read them with clear error
behavior.

Live provider execution is already proven end-to-end in PS-007 (Cloudflare
primary -> Pollinations fallback -> B2 + Genblaze manifest + verification), and
the deterministic router behavior is proven in PS-006. Requiring a live
provider call in PS-008 would:

- couple an API-architecture proof to network availability and provider quotas
- require live API keys just to smoke-test the skeleton
- risk accidental cost / quota consumption on every API test
- hide the fact that PS-008 proves structure, not generation

Therefore the PS-008 default is a dry run, and the smoke test runs with zero
network calls, zero API keys, zero B2 access, and zero Genblaze access.

## How PS-008 Connects to PS-007

PS-008 is built so the live PS-007 pipeline can be attached without rewriting
the API. Specifically:

- `AttemptRecord` (`src/proofstudio/api/models.py`) mirrors the PS-006 20-field
  `ProviderAttempt` shape from `src/proofstudio/providers/types.py`, so a
  `ProviderAttempt.to_dict()` from a PS-007 router result can be stored
  verbatim.
- `ProofStudioService.register_attempt` / `register_asset` / `register_manifest`
  (`src/proofstudio/api/services.py`) are the wiring points where PS-009 or
  PS-010 will attach the PS-007 provider-router + `GenblazeStore` pipeline.
- `POST /runs` has an explicit `run_live` flag. In PS-008, opting into live
  execution records status `live_execution_not_supported_in_ps008` and performs
  no provider/B2/Genblaze call - the single `_record_live_not_supported_note`
  method documents the exact place a later slice will connect the live path.
- `ManifestRecord` carries `manifest_uri`, `manifest_hash`,
  `in_memory_manifest_verify`, `stored_manifest_verify`, `transfer_failures`,
  and `stored_transfer_failures` - the same fields a PS-007 `GenblazeRunResult`
  produces - so a live run's manifest evidence maps directly onto the API.

In short: PS-007 proved the live engine; PS-008 builds the chassis and leaves
labeled attachment points for that engine.

## Truth Boundary

PS-008 proves the backend API skeleton and the in-memory product model only.

It does NOT prove:

- production persistence (the store is process-local and non-durable)
- authentication
- authorization
- deployment
- background job execution
- live provider execution through the API
- B2 upload through the API
- Genblaze manifest writing through the API
- C2PA authenticity
- legal authenticity
- semantic truth
- human authorship

Those are later slices.

## Acceptance Criteria Check

- API package files exist: yes
- smoke script compiles: yes
- API app imports: yes (`fastapi` mode)
- health / version works: yes
- campaign create / get works: yes
- dry-run run create / get works: yes
- attempts / assets / manifest responses are clear and valid: yes
- missing IDs return clear errors (404 `ErrorResponse`, no crash): yes
- smoke summary `ok: true`: yes
- no live provider keys required: yes
- no B2 upload occurs: yes
- no fake generated media is created: yes
- no secrets introduced: yes
- historical proof scripts (PS-004 / PS-005 / PS-006 / PS-007) untouched: yes
