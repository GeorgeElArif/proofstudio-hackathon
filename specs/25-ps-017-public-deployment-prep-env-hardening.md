# PS-017 Public Deployment Prep + Environment Hardening

## 1. Purpose

PS-017 prepares ProofStudio for a real public deployment without pretending deployment is complete.

Previous milestones proved:

- PS-012: FastAPI server mode and demo API contract
- PS-013: Review Room frontend
- PS-013A: local frontend/backend integration hardening
- PS-014: live demo flow in the Review Room
- PS-015: demo seed pack and one-click local demo
- PS-016: submission demo script and judge evidence pack

PS-017 must prepare the app for the next missing submission requirement:

- a working public app URL judges can access

This slice is deployment preparation and environment hardening.

It must create:

- deployment target decision notes
- production environment template
- frontend API base URL strategy
- backend CORS production strategy
- no-secret deployment checklist
- local production-mode smoke
- deployment readiness proof

PS-017 should not claim public deployment unless a real URL is produced in a later slice.

## 2. Product Meaning

A local demo is not enough for final submission.

Judges need either:

- a working app URL
- or a clearly documented local demo until deployment is complete

PS-017 closes the gap between local demo and public deployment by making the deployment path explicit, safe, and verifiable.

## 3. Safety Principle

Do not expose secrets.

Do not commit real API keys.

Do not commit `.env`.

Do not weaken CORS into unsafe wildcard production behavior.

Do not make live mode default.

Do not make provider/B2 calls during deployment-prep smoke.

Do not claim a public URL exists until it exists.

Do not fake deployment screenshots.

Do not fake public health checks.

## 4. Current Foundation

Backend local command:

- `uvicorn proofstudio.api.app:app --reload --host 127.0.0.1 --port 8000`

Frontend local command:

- `cd apps/web && npm run dev -- --host 127.0.0.1 --port 5173`

Frontend API base URL:

- `VITE_PROOFSTUDIO_API_BASE_URL`
- fallback: `http://127.0.0.1:8000`

Current local URLs:

- Review Room: `http://127.0.0.1:5173`
- API health: `http://127.0.0.1:8000/health`
- API docs: `http://127.0.0.1:8000/docs`

Current backend routes:

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

## 5. Non-Goals

Do not deploy yet unless explicitly requested in a later slice.

Do not create a fake public URL.

Do not add authentication.

Do not add production persistence.

Do not add a database.

Do not add a queue.

Do not change provider router behavior.

Do not change B2/Genblaze proof logic.

Do not redesign the UI.

Do not run live providers by default.

Do not call B2 by default.

Do not modify historical proof scripts.

## 6. Required Files

Allowed new files:

- `.env.production.example`
- `docs/deployment/README.md`
- `docs/deployment/environment.md`
- `docs/deployment/cors-and-security.md`
- `docs/deployment/platform-decision.md`
- `docs/deployment/preflight-checklist.md`
- `scripts/ps017_deployment_prep_smoke.py`
- `docs/ps-017-public-deployment-prep-env-hardening-proof.md`

Allowed modified files:

- `README.md`
- `apps/web/README.md`
- `apps/web/src/api.ts` only if tiny production base URL validation/helper is needed
- `src/proofstudio/api/app.py` only if tiny CORS/env compatibility fix is required
- `apps/api/requirements.txt` only if required by a safe deployment entrypoint
- `apps/web/package.json` only if a production preview script is useful

Prefer documentation + smoke script + environment template.

Backend changes should be avoided unless the current CORS or settings shape makes production deployment unsafe or unclear.

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
- scripts/ps014_live_demo_flow_review_room_smoke.py
- scripts/ps015_demo_seed_pack_one_click_smoke.py
- scripts/ps016_submission_evidence_pack_smoke.py

## 7. Environment Template Requirement

Create:

- `.env.production.example`

It must include placeholders only.

Required variables:

- `PROOFSTUDIO_ENV=production`
- `PROOFSTUDIO_API_HOST=0.0.0.0`
- `PROOFSTUDIO_API_PORT=8000`
- `PROOFSTUDIO_PUBLIC_API_BASE_URL=https://replace-with-api-host`
- `PROOFSTUDIO_PUBLIC_WEB_URL=https://replace-with-web-host`
- `PROOFSTUDIO_CORS_ORIGINS=https://replace-with-web-host`
- `VITE_PROOFSTUDIO_API_BASE_URL=https://replace-with-api-host`
- `PROOFSTUDIO_RUN_LIVE_DEFAULT=false`

Optional provider/storage variables as placeholders only:

- `B2_BUCKET=replace-me`
- `B2_REGION=replace-me`
- `B2_KEY_ID=replace-me`
- `B2_APP_KEY` — placeholder `replace-me`
- `CLOUDFLARE_ACCOUNT_ID=replace-me`
- `CLOUDFLARE_API_TOKEN` — placeholder `replace-me`
- `GEMINI_API_KEY` — placeholder `replace-me`
- `ELEVENLABS_API_KEY` — placeholder `replace-me`

Do not include real secrets.

## 8. CORS and Security Requirement

Production CORS must be explicit.

Create:

- `docs/deployment/cors-and-security.md`

It must explain:

- local CORS origins
- production CORS origins
- why wildcard production CORS is unsafe
- how to set `PROOFSTUDIO_CORS_ORIGINS`
- why credentials should remain false unless needed
- how frontend API base URL should point to the deployed API host
- secret handling rules
- what not to commit

If backend currently hardcodes local CORS only, PS-017 may add a tiny environment-based CORS origin reader.

If added, it must preserve local origins and allow production origins from `PROOFSTUDIO_CORS_ORIGINS`.

## 9. Frontend API Base URL Requirement

Create or document:

- production frontend must use `VITE_PROOFSTUDIO_API_BASE_URL`
- local fallback remains `http://127.0.0.1:8000`
- production build should not silently point to localhost unless explicitly intended

If current `apps/web/src/api.ts` already supports this, document it.

If it needs a tiny validation helper or clearer error copy, keep the change minimal.

## 10. Platform Decision Requirement

Create:

- `docs/deployment/platform-decision.md`

It must include:

- what a deployment platform must support
- separate or combined backend/frontend hosting options
- environment variable support
- build commands
- start commands
- CORS/domain setup
- log access
- secrets management
- expected public URLs
- recommendation placeholder

Do not claim a platform is selected unless it is actually selected.

Allowed status:

- selected: pending

If the user later chooses Render, Railway, Fly.io, Vercel, Netlify, Cloudflare Pages, or another provider, a later slice should verify current platform docs before implementation.

## 11. Deployment Runbook Requirement

Create:

- `docs/deployment/README.md`

It must include:

- deployment status
- local proof status
- production env template path
- frontend build command
- backend start command
- smoke command
- public URL placeholders
- next steps for a real deployment slice

Must include commands:

- `python scripts/ps017_deployment_prep_smoke.py`
- `cd apps/web && npm run build`
- `uvicorn proofstudio.api.app:app --host 0.0.0.0 --port 8000`

## 12. Environment Documentation Requirement

Create:

- `docs/deployment/environment.md`

It must include:

- required production variables
- optional provider/storage variables
- frontend variables
- backend variables
- local vs production values
- secret handling
- where not to store secrets
- how to verify env readiness

## 13. Preflight Checklist Requirement

Create:

- `docs/deployment/preflight-checklist.md`

It must include:

### Before deploying

- choose platform
- set public API URL
- set public frontend URL
- set CORS origins
- configure secrets
- run local smoke
- run frontend build
- confirm live mode default false
- confirm no `.env` committed

### After deploying

- verify public `/health`
- verify public `/version`
- verify frontend API status
- create safe dry-run
- confirm no provider/B2 call by default
- optionally run explicit live proof
- update submission checklist with real public URL

## 14. Proof Document Requirement

Create:

- `docs/ps-017-public-deployment-prep-env-hardening-proof.md`

It must include:

- status
- files created/modified
- backend changed or unchanged
- frontend changed or unchanged
- environment template
- CORS strategy
- frontend API base URL strategy
- no-secret proof
- default no-live proof
- deployment status
- limitations
- next milestone recommendation
- truth boundary

## 15. Smoke Script Requirement

Create:

- `scripts/ps017_deployment_prep_smoke.py`

The smoke must not call live providers or B2.

The smoke must:

1. Set output dir:
   `/tmp/proofstudio-ps-017`
2. Verify required deployment docs exist.
3. Verify `.env.production.example` exists.
4. Verify `.env.production.example` contains placeholders only.
5. Verify required production env keys exist.
6. Verify no real secrets appear.
7. Verify CORS docs include explicit production origin guidance.
8. Verify frontend API base URL strategy is documented.
9. Verify deployment platform decision is marked pending unless selected.
10. Verify preflight checklist includes before/after deployment checks.
11. Verify backend can import FastAPI app.
12. Verify `/health` and `/version` work through TestClient.
13. Verify default safe dry-run still avoids providers/B2.
14. Verify frontend build passes.
15. Verify no backend/provider/provenance changes unless explicitly allowed and documented.
16. Verify historical scripts untouched.
17. Write summary JSON:
    `/tmp/proofstudio-ps-017/deployment-prep-summary.json`
18. Write transcript JSON:
    `/tmp/proofstudio-ps-017/deployment-prep-transcript.json`
19. Print final summary JSON.

## 16. Required Summary Fields

The PS-017 smoke summary must include:

- `ok`
- `slice`
- `env_template_checked`
- `env_template_no_real_secrets`
- `required_env_keys_checked`
- `deployment_docs_created`
- `cors_strategy_checked`
- `frontend_api_base_strategy_checked`
- `platform_decision_checked`
- `preflight_checklist_checked`
- `fastapi_import_checked`
- `health_checked`
- `version_checked`
- `default_no_live_provider_call`
- `default_no_b2_call`
- `frontend_build_checked`
- `frontend_build_status`
- `backend_changed`
- `frontend_app_changed`
- `historical_scripts_untouched`
- `no_secret_leakage`
- `deployment_status`
- `public_url_status`
- `summary_path`
- `transcript_path`
- `truth_boundary`

Use stable machine schema:

- booleans must be booleans
- lists should use `*_paths` or `*_items`
- statuses should be strings

## 17. Acceptance Criteria

PS-017 is accepted if:

- deployment prep docs exist
- production env example exists and has placeholders only
- CORS strategy is explicit
- frontend API base URL strategy is clear
- platform decision is honest
- preflight checklist is complete
- no real secrets are introduced
- default path does not call providers
- default path does not call B2
- frontend build passes
- backend/provider/provenance changes are absent or tiny and documented
- historical scripts untouched
- smoke summary ok true

## 18. Failure Conditions

Reject PS-017 if:

- it claims public deployment without a real URL
- it invents public health checks
- it commits real secrets
- it weakens CORS into unsafe wildcard production behavior
- it makes live mode default
- it calls providers during default smoke
- it calls B2 during default smoke
- it changes backend behavior without documenting why
- it modifies historical proof scripts
- summary schema uses list where boolean is required
- truth boundary omits required non-claims

## 19. Truth Boundary

PS-017 proves ProofStudio has deployment preparation, environment templates, and preflight checks for moving from local demo to public hosting.

It does not prove:

- public deployment
- working public app URL
- final Devpost submission
- production availability
- authentication
- production persistence
- background job reliability
- legal authenticity
- C2PA authenticity
- semantic truth
- human authorship
