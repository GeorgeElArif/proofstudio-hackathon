# PS-014 Live Demo Flow / End-to-End Review Room Path

## 1. Purpose

PS-014 creates the first end-to-end live demo path through the Review Room UI.

Previous milestones proved:

- PS-009: API can trigger a live provider run.
- PS-010: run evidence can be archived and rehydrated from B2.
- PS-011: Provenance Passport can explain the evidence.
- PS-012: FastAPI exposes the demo API contract.
- PS-013: Review Room frontend exists.
- PS-013A: local frontend/backend integration is hardened with CORS and clear API status.

PS-014 must now connect the visible UI to the live proof path.

The product demo path:

Create campaign
-> explicitly enable live mode
-> create live run
-> show run status
-> show provider/model
-> show attempt timeline
-> show asset metadata and generated media when available
-> show manifest verification
-> show Provenance Passport
-> show truth boundary

## 2. Product Meaning

This slice makes ProofStudio demoable as a product, not only as backend proof scripts.

A judge should be able to see:

- the user creates a campaign
- the user chooses safe dry-run or explicitly chooses live mode
- live mode is clearly warned
- ProofStudio records what happened
- attempts are shown
- asset metadata is shown
- manifest proof is shown
- the Provenance Passport explains the result
- the truth boundary is visible

## 3. Safety Principle

Live mode must be explicit.

Default behavior must remain safe dry-run.

The UI must never call live providers by default.

The UI must never call B2 by default unless live mode is explicitly enabled and the backend path requires it.

The user must clearly understand:

Live mode may call external providers and B2.

## 4. Current Foundation

Backend:

- FastAPI app is available at `proofstudio.api.app:app`.
- Local backend runs on `http://127.0.0.1:8000`.
- CORS allows local frontend origins.
- Required endpoints exist:
  - GET /health
  - GET /version
  - POST /campaigns
  - GET /campaigns/{campaign_id}
  - POST /runs
  - GET /runs/{run_id}
  - GET /runs/{run_id}/attempts
  - GET /runs/{run_id}/assets
  - GET /runs/{run_id}/manifest
  - GET /runs/{run_id}/passport

Frontend:

- Vite + React + TypeScript app exists under `apps/web`.
- Local frontend runs on `http://127.0.0.1:5173`.
- API base URL config uses `VITE_PROOFSTUDIO_API_BASE_URL` with fallback `http://127.0.0.1:8000`.

## 5. Non-Goals

Do not deploy.

Do not add authentication.

Do not add production database persistence.

Do not add background workers.

Do not build a full dashboard.

Do not redesign the entire UI.

Do not make live mode default.

Do not hide live mode risk.

Do not fake media.

Do not fake manifest verification.

Do not fake B2 archive evidence.

Do not fake Provenance Passport evidence.

Do not claim legal authenticity.

Do not claim C2PA authenticity.

Do not claim semantic truth.

Do not claim human authorship.

Do not modify historical proof scripts.

## 6. Required Files

Allowed new files:

- scripts/ps014_live_demo_flow_review_room_smoke.py
- docs/ps-014-live-demo-flow-review-room-path-proof.md

Allowed modified files:

- apps/web/src/App.tsx
- apps/web/src/api.ts
- apps/web/src/styles.css
- apps/web/README.md
- apps/web/package.json only if a useful demo script is needed
- src/proofstudio/api/app.py only if a tiny compatibility fix is required
- src/proofstudio/api/services.py only if a tiny compatibility fix is required

Do not modify historical proof scripts:

- scripts/ps004_provider_router_cloudflare_smoke.py
- scripts/ps005_pollinations_fallback_smoke.py
- scripts/ps006_provider_router_core_smoke.py
- scripts/ps007_live_provider_router_chain_smoke.py
- scripts/ps008_backend_api_smoke.py
- scripts/ps009_api_live_run_bridge_smoke.py
- scripts/ps010_run_archive_rehydrate_b2_smoke.py
- scripts/ps011_provenance_passport_api_smoke.py
- scripts/ps012_fastapi_server_demo_contract_smoke.py
- scripts/ps013_demo_ui_review_room_smoke.py
- scripts/ps013a_local_demo_integration_hardening_smoke.py

## 7. UI Requirements

The Review Room must support two clear paths:

### 7.1 Safe Dry Run

Default path.

Behavior:

- run_live is false
- no live provider call
- no B2 call
- status shows dry_run_created or equivalent
- no generated assets are shown
- manifest is unavailable/not ready honestly
- passport explains no-media/no-manifest state honestly

### 7.2 Explicit Live Run

Opt-in path.

Behavior:

- user must intentionally enable live mode
- UI must show warning before live run:
  - Live mode may call external providers and B2.
- button text should be explicit:
  - Create Live Proof Run
- UI should show loading/progress state while request is in flight
- UI should not allow accidental double-submit while live run is pending
- after completion, UI should fetch:
  - run
  - attempts
  - assets
  - manifest
  - passport

## 8. Evidence Display Requirements

After live run completes or fails/blocks, UI must show evidence honestly.

### 8.1 Evidence Overview

Show:

- run_id
- status
- selected_provider
- selected_model
- fallback_used
- attempt_count
- asset_count
- manifest_uri
- manifest_hash

### 8.2 Attempt Timeline

Show:

- attempt_index
- provider
- model
- status
- normalized_status
- latency_ms
- retryable
- fallback_allowed
- sanitized_error_message

### 8.3 Assets Panel

Show:

- URL
- media_type
- sha256
- size_bytes
- metadata

If the primary asset is an image and the URL is reachable by the browser, show a preview.

If preview cannot load, show metadata only.

Do not fake preview.

Do not use placeholder as if it were generated output.

### 8.4 Manifest Panel

Show:

- manifest_uri
- manifest_hash
- stored_manifest_verify
- transfer_failures
- stored_transfer_failures

If manifest is unavailable, say unavailable.

### 8.5 Passport Panel

Show:

- passport_identity
- run_summary
- generation_summary
- manifest_verification
- archive_and_rehydration
- trust_boundary
- reviewer_next_actions

The trust boundary must stay visible.

## 9. Error Handling Requirements

The UI must handle:

- backend unavailable
- CORS/network failure
- validation error
- missing campaign
- live provider failure
- live blocked
- B2/storage failure
- manifest unavailable
- passport unavailable

Errors must be clear, not raw stack traces.

No secrets should appear.

## 10. Backend Requirements

Prefer no backend changes.

If backend changes are needed, they must be tiny compatibility fixes only.

Backend must preserve:

- safe dry-run default
- explicit live mode only
- no fake media
- no fake manifest
- existing API contract

## 11. Demo Runbook Requirement

Docs must include exact demo sequence:

Terminal 1 backend:

- cd /home/proofstudio-work/proofstudio
- source .venv/bin/activate
- export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"
- uvicorn proofstudio.api.app:app --reload --host 127.0.0.1 --port 8000

Terminal 2 frontend:

- cd /home/proofstudio-work/proofstudio/apps/web
- npm install
- npm run dev -- --host 127.0.0.1 --port 5173

Browser:

- open http://127.0.0.1:5173
- confirm API status online
- create campaign
- create safe dry-run
- inspect honest no-media state
- enable live mode intentionally
- create live proof run
- inspect attempts/assets/manifest/passport

## 12. Smoke Script

Create:

scripts/ps014_live_demo_flow_review_room_smoke.py

The smoke must have two modes.

### 12.1 Default Safe Smoke

Default smoke must not call live providers or B2.

It must:

1. Set output dir:
   /tmp/proofstudio-ps-014
2. Verify frontend files exist.
3. Verify UI contains explicit live mode warning.
4. Verify UI default run_live is false.
5. Verify UI has Create Safe Dry Run action.
6. Verify UI has explicit Create Live Proof Run action.
7. Verify UI references all required endpoints.
8. Verify UI displays evidence sections.
9. Verify UI has no fake media success.
10. Verify UI has no fake manifest success.
11. Verify FastAPI API still passes safe dry-run HTTP flow.
12. Verify default smoke does not call live providers.
13. Verify default smoke does not call B2.
14. Verify frontend build passes.
15. Write summary JSON:
    /tmp/proofstudio-ps-014/live-demo-flow-review-room-summary.json
16. Write transcript JSON:
    /tmp/proofstudio-ps-014/live-demo-flow-review-room-transcript.json
17. Print final summary JSON.

### 12.2 Explicit Live Smoke

Optional live smoke may run only when:

PROOFSTUDIO_PS014_LIVE=1

When enabled, it may call:

POST /runs with run_live=true

It must then verify:

- live_run_attempted true
- run status is live_completed, live_failed, or live_blocked
- if completed:
  - selected_provider exists
  - selected_model exists
  - attempts exist
  - assets exist
  - manifest exists
  - passport exists
  - stored_manifest_verify true
- if failed/blocked:
  - no fake media
  - no fake manifest
  - clear failure state

Default acceptance must not require live provider spend.

Final acceptance can optionally include explicit live proof if user chooses to run it.

## 13. Required Summary Fields

The PS-014 summary must include:

- ok
- slice
- frontend_path
- default_safe_mode_checked
- live_mode_explicit_checked
- live_mode_warning_present
- safe_dry_run_action_present
- live_run_action_present
- api_endpoints_referenced
- evidence_overview_present
- attempts_panel_present
- assets_panel_present
- manifest_panel_present
- passport_panel_present
- trust_boundary_present
- default_no_live_provider_call
- default_no_b2_call
- no_fake_media
- no_fake_manifest
- frontend_build_checked
- frontend_build_status
- safe_api_flow_checked
- live_mode_enabled
- live_run_status
- live_run_completed
- selected_provider
- selected_model
- manifest_uri
- passport_checked
- summary_path
- transcript_path
- truth_boundary

## 14. Documentation Proof

Create:

docs/ps-014-live-demo-flow-review-room-path-proof.md

It must include:

- status
- frontend path
- local run commands
- safe dry-run path
- explicit live path
- live mode warning
- evidence panels
- asset preview behavior
- manifest proof behavior
- passport proof behavior
- default no-provider/no-B2 proof
- optional live proof if run
- truth boundary
- limitations
- next milestone recommendation

## 15. Acceptance Criteria

PS-014 is accepted if:

- UI supports safe dry-run default
- UI supports explicit live proof run action
- live mode warning is visible
- default path does not call providers
- default path does not call B2
- UI shows attempts/assets/manifest/passport panels
- UI displays completed live evidence when live run succeeds
- UI displays failed/blocked live state honestly when live run fails/blocks
- no fake media
- no fake manifest
- frontend build passes
- safe API flow passes
- smoke summary ok true
- historical scripts remain untouched
- secret scan passes

## 16. Failure Conditions

Reject PS-014 if:

- live mode is default
- live provider calls happen during default smoke
- B2 calls happen during default smoke
- UI fakes live media
- UI fakes manifest verification
- UI hides the truth boundary
- UI hides live mode risk
- backend API contract regresses
- historical proof scripts are modified
- secrets are introduced
- unrelated files are changed

## 17. Truth Boundary

PS-014 proves ProofStudio has a local end-to-end Review Room demo path for safe dry-runs and explicit live proof runs.

It does not prove:

- public deployment
- production availability
- authentication
- production persistence
- background job reliability
- legal authenticity
- C2PA authenticity
- semantic truth
- human authorship
