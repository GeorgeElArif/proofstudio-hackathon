# PS-013A Local Demo Integration Hardening

## 1. Purpose

PS-013A fixes and hardens the local browser demo integration created in PS-013.

PS-013 created the Review Room frontend under `apps/web`.

Manual browser testing showed:

- FastAPI backend works at `http://127.0.0.1:8000/health`
- FastAPI docs work at `http://127.0.0.1:8000/docs`
- Frontend renders at the Vite dev server
- Frontend API Status card showed:
  - Network error reading `http://127.0.0.1:8000/version`

The likely cause is cross-origin browser integration between:

- frontend: `http://127.0.0.1:5173`
- backend: `http://127.0.0.1:8000`

PS-013A must make the local demo reliable.

## 2. Naming Rule

This slice is intentionally named PS-013A, not PS-014.

It is a hardening slice attached to PS-013.

Main roadmap numbering must remain stable.

Future corrective or integration slices should use suffixes such as:

- PS-013A
- PS-013B
- PS-010A
- PS-009A

Do not consume a new main roadmap number for a local hardening patch.

## 3. Product Meaning

A judge-facing demo cannot start with a network error.

PS-013A makes the local demo flow reliable:

1. Start backend.
2. Start frontend.
3. Open frontend.
4. API Status card connects.
5. Campaign creation works.
6. Safe dry-run works.
7. Evidence panels populate honestly.
8. Passport endpoint works.
9. No live provider calls happen by default.
10. No B2 calls happen by default.

## 4. Current Foundation

Completed:

- PS-012: FastAPI Server Mode + Demo API Contract
- PS-013: Demo UI Shell / Review Room Frontend

Current known routes:

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

Current frontend path:

- apps/web

Current local run commands:

- backend: `uvicorn proofstudio.api.app:app --reload --host 127.0.0.1 --port 8000`
- frontend: `cd apps/web && npm run dev -- --host 127.0.0.1 --port 5173`

## 5. Non-Goals

Do not build new product features.

Do not redesign the UI.

Do not add auth.

Do not deploy.

Do not add production persistence.

Do not run live providers by default.

Do not call B2 by default.

Do not fake media.

Do not fake manifest verification.

Do not fake passport evidence.

Do not claim semantic truth.

Do not claim legal authenticity.

Do not claim C2PA authenticity.

Do not claim human authorship.

Do not modify historical proof scripts.

## 6. Required Files

Allowed new files:

- scripts/ps013a_local_demo_integration_hardening_smoke.py
- docs/ps-013a-local-demo-integration-hardening-proof.md

Allowed modified files:

- src/proofstudio/api/app.py
- src/proofstudio/api/services.py only if needed for capabilities or metadata
- apps/api/requirements.txt only if CORS/test dependency needs declaration
- apps/web/src/api.ts
- apps/web/src/App.tsx
- apps/web/src/styles.css
- apps/web/README.md
- apps/web/package.json only if a useful local script is needed

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

## 7. Backend CORS Requirement

FastAPI must allow local frontend origins.

Required allowed origins:

- http://127.0.0.1:5173
- http://localhost:5173

Optional useful origins:

- http://127.0.0.1:4173
- http://localhost:4173

Implementation should use FastAPI CORSMiddleware.

CORS should be safe for local demo.

Do not use wildcard credentials unless justified.

Recommended:

- allow_origins explicit localhost list
- allow_methods all or explicit required methods
- allow_headers all
- allow_credentials false unless required

## 8. Frontend API Reliability Requirement

The frontend should clearly show API connectivity state.

Improve the API Status card if needed:

- show API base URL
- show health result
- show version result
- show helpful error if backend is not running
- distinguish backend unavailable from API response error

The UI should not silently fail.

## 9. Local Demo Runbook Requirement

The README/proof doc must include exact two-terminal flow:

Terminal 1:

- cd /home/proofstudio-work/proofstudio
- source .venv/bin/activate
- export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"
- uvicorn proofstudio.api.app:app --reload --host 127.0.0.1 --port 8000

Terminal 2:

- cd /home/proofstudio-work/proofstudio/apps/web
- npm install
- npm run dev -- --host 127.0.0.1 --port 5173

Open:

- http://127.0.0.1:5173
- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/docs

## 10. CORS Smoke Requirement

Create:

scripts/ps013a_local_demo_integration_hardening_smoke.py

The smoke must:

1. Set output dir:
   /tmp/proofstudio-ps-013a
2. Import FastAPI app.
3. Verify app is FastAPI.
4. Verify required CORS middleware is installed or CORS behavior works.
5. Use TestClient or equivalent.
6. Send OPTIONS preflight for `/version` with:
   - Origin: http://127.0.0.1:5173
   - Access-Control-Request-Method: GET
7. Verify CORS response allows origin/method.
8. Send GET `/version` with Origin header.
9. Verify response succeeds and includes Access-Control-Allow-Origin when appropriate.
10. Repeat at least one check for:
    - http://localhost:5173
11. Verify `/health` still works.
12. Verify `/campaigns` and `/runs` safe dry-run path still works.
13. Verify no live provider call by default.
14. Verify no B2 call by default.
15. Verify no fake media.
16. Verify frontend API file includes API base URL configuration.
17. Verify README/proof docs include two-terminal local run commands.
18. Write summary JSON:
    /tmp/proofstudio-ps-013a/local-demo-integration-hardening-summary.json
19. Write transcript JSON:
    /tmp/proofstudio-ps-013a/local-demo-integration-hardening-transcript.json
20. Print final summary JSON.

## 11. Required Summary Fields

The PS-013A summary must include:

- ok
- slice
- fastapi_app_checked
- cors_middleware_present
- cors_preflight_checked
- cors_get_checked
- allowed_origins_checked
- health_checked
- version_checked
- campaign_create_checked
- dry_run_create_checked
- default_no_live_provider_call
- default_no_b2_call
- no_fake_media
- frontend_api_base_config_checked
- frontend_status_error_copy_checked
- local_runbook_checked
- docs_updated
- summary_path
- transcript_path
- truth_boundary

## 12. Documentation Proof

Create:

docs/ps-013a-local-demo-integration-hardening-proof.md

It must include:

- status
- root cause
- CORS behavior added
- allowed local origins
- endpoints tested
- default safe dry-run behavior
- no-provider-call proof
- no-B2-call proof
- frontend API status behavior
- exact two-terminal local runbook
- limitations
- next milestone recommendation

## 13. Acceptance Criteria

PS-013A is accepted if:

- local frontend origins are allowed by backend CORS
- browser-style CORS preflight passes for `/version`
- browser-style GET with Origin passes
- `/health` and `/version` still work
- campaign creation works
- safe dry-run creation works
- default path does not call live providers
- default path does not call B2
- no fake media is created
- frontend shows clearer API status/error behavior
- exact local runbook is documented
- smoke summary ok true
- historical proof scripts remain untouched
- secret scan passes

## 14. Failure Conditions

Reject PS-013A if:

- CORS uses unsafe wildcard credentials
- frontend still has unclear generic network failure only
- default run path calls live providers
- default run path calls B2
- fake media or fake manifest proof is introduced
- historical proof scripts are modified
- unrelated files are changed
- secrets are introduced

## 15. Truth Boundary

PS-013A proves the local browser demo can connect to the FastAPI backend through safe local CORS settings and execute the default dry-run demo path.

It does not prove:

- public deployment
- production CORS policy
- authentication
- production persistence
- background job reliability
- legal authenticity
- C2PA authenticity
- semantic truth
- human authorship
