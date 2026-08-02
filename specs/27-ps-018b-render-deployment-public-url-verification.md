# PS-018B Render Deployment Execution + Public URL Verification

## 1. Purpose

PS-018B turns PS-018 Level A deployment readiness into verified public deployment evidence.

PS-018 Level A proved:

- Render was selected as the public deployment target.
- `render.yaml` exists.
- Render deployment runbook exists.
- `scripts/ps018_live_url_smoke.py` exists.
- Local contract smoke passes.
- Public URL status is honestly pending.

PS-018B must prove the missing judge requirement:

- a real working public app URL

This slice must deploy ProofStudio publicly, run the explicit live URL smoke against real URLs, and update submission evidence only after verification passes.

## 2. Target

Selected deployment target:

- Render

Expected public services:

- Backend FastAPI web service
- Frontend static site

Expected public URLs:

- `PROOFSTUDIO_PUBLIC_API_BASE_URL`
- `PROOFSTUDIO_PUBLIC_WEB_URL`

Both must be real non-localhost HTTPS URLs.

## 3. Manual Deployment Boundary

PS-018B includes manual deployment work in the Render dashboard.

Do not fake this step.

Do not invent public URLs.

Do not record public URLs until Render provides real deployed URLs.

Do not mark verification passed until `scripts/ps018_live_url_smoke.py` passes in explicit live URL mode.

## 4. Backend Deployment Requirements

Backend service:

- Render service type: Web Service
- Runtime: Python
- Repo: `GeorgeElArif/proofstudio`
- Branch: `ps-018b/render-deployment-public-url-verification`, unless deploying from another approved branch
- Root directory: repository root
- Build command must be based on actual repo dependency files
- Start command:

`PYTHONPATH=src uvicorn proofstudio.api.app:app --host 0.0.0.0 --port $PORT`

Health check path:

`/health`

Required backend environment variables for safe public demo:

- `PROOFSTUDIO_ENV`
- `PROOFSTUDIO_PUBLIC_WEB_URL`
- `PROOFSTUDIO_CORS_ORIGINS`
- `PROOFSTUDIO_RUN_LIVE_DEFAULT`

Safe default:

- `PROOFSTUDIO_RUN_LIVE_DEFAULT` must remain `false`

Provider/B2 secrets are optional for this slice and must not be required for the default safe public smoke.

## 5. Frontend Deployment Requirements

Frontend service:

- Render service type: Static Site
- Repo: `GeorgeElArif/proofstudio`
- Branch: `ps-018b/render-deployment-public-url-verification`, unless deploying from another approved branch
- Root directory: `apps/web`
- Build command:

`npm ci && npm run build`

- Publish directory:

`dist`

Required frontend environment variable:

- `VITE_PROOFSTUDIO_API_BASE_URL`

This value is frontend-public and must contain only the public backend base URL.

Do not put secrets in `VITE_*` variables.

## 6. CORS Requirements

After both Render URLs exist:

Backend must allow the frontend origin through:

- `PROOFSTUDIO_CORS_ORIGINS`

Expected value:

- the public frontend URL

Do not use wildcard production CORS.

If temporary testing needs local origins, keep them explicit and documented.

## 7. Live URL Smoke Requirements

Run:

`PS018_RUN_LIVE_URL_SMOKE=true PROOFSTUDIO_PUBLIC_API_BASE_URL=<real api url> PROOFSTUDIO_PUBLIC_WEB_URL=<real web url> python scripts/ps018_live_url_smoke.py`

The smoke must verify:

- public API `/health`
- public API `/version`
- public frontend loads HTML
- CORS preflight from frontend origin succeeds
- public URLs are non-localhost HTTPS
- no provider call by default
- no B2 call by default

Acceptance summary must show:

- `ok`: true
- `live_url_mode_enabled`: true
- `live_url_smoke_status`: `passed`
- `public_url_verified`: true
- `api_health_checked`: true
- `api_version_checked`: true
- `web_load_checked`: true
- `cors_preflight_checked`: true
- `default_no_live_provider_call`: true
- `default_no_b2_call`: true

## 8. Required Files

Allowed new files:

- `docs/ps-018b-render-deployment-public-url-verification-proof.md`

Allowed modified files:

- `README.md`
- `apps/web/README.md`
- `.env.production.example`
- `docs/deployment/render.md`
- `docs/deployment/preflight-checklist.md`
- `docs/submission/submission-checklist.md`
- `docs/submission/judge-evidence-pack.md`
- `docs/ps-018-public-deployment-target-live-url-smoke-proof.md`
- `render.yaml` only if Render requires a correction discovered during deployment
- `scripts/ps018_live_url_smoke.py` only if live deployed behavior reveals a smoke bug
- `apps/api/requirements.txt` only if Render backend import fails because of dependency packaging
- `src/proofstudio/api/app.py` only if public CORS/port behavior exposes a tiny production compatibility issue

Avoid code changes unless Render deployment proves they are necessary.

Do not modify frontend app code unless deployment proves it is necessary.

Do not modify providers, provenance, archive, or historical proof scripts.

## 9. Historical Scripts Must Remain Untouched

Do not modify:

- `scripts/ps004_provider_router_cloudflare_smoke.py`
- `scripts/ps005_pollinations_fallback_smoke.py`
- `scripts/ps006_provider_router_core_smoke.py`
- `scripts/ps007_live_provider_router_chain_smoke.py`
- `scripts/ps008_backend_api_smoke.py`
- `scripts/ps009_api_live_run_bridge_smoke.py`
- `scripts/ps010_run_archive_rehydrate_b2_smoke.py`
- `scripts/ps011_provenance_passport_api_smoke.py`
- `scripts/ps012_fastapi_server_demo_contract_smoke.py`
- `scripts/ps013_demo_ui_review_room_smoke.py`
- `scripts/ps013a_local_demo_integration_hardening_smoke.py`
- `scripts/ps014_live_demo_flow_review_room_smoke.py`
- `scripts/ps015_demo_seed_pack_one_click_smoke.py`
- `scripts/ps016_submission_evidence_pack_smoke.py`
- `scripts/ps017_deployment_prep_smoke.py`

PS-018 smoke may be run. It should only be modified if a real smoke bug is discovered.

## 10. Documentation Update Requirements

After public URLs are verified:

Update `docs/submission/submission-checklist.md`:

- record public frontend URL
- record public backend URL
- record live URL smoke status
- record smoke summary path
- record verification timestamp

Update `docs/submission/judge-evidence-pack.md`:

- record public frontend URL
- record public backend URL
- record PS-018B proof status
- explain safe public demo default
- keep no-live/no-B2 default truth boundary

Update `docs/deployment/render.md`:

- add actual verified service names/URLs
- add any Render dashboard settings used
- add deployment troubleshooting notes if needed

Create `docs/ps-018b-render-deployment-public-url-verification-proof.md` with:

- status
- branch
- commit target
- Render backend URL
- Render frontend URL
- backend service settings
- frontend static site settings
- env var strategy
- CORS verification
- live URL smoke result
- summary path
- transcript path
- no-secret proof
- no fake URL proof
- no provider/B2 default proof
- changed files
- limitations
- next milestone recommendation
- truth boundary

## 11. Failure Conditions

Reject PS-018B if:

- no real public URLs exist
- URLs are localhost
- URLs are HTTP instead of HTTPS
- public `/health` fails
- public `/version` fails
- frontend does not load
- CORS preflight fails
- the smoke claims verification without real network checks
- provider/B2 calls happen by default
- secrets are committed
- frontend `VITE_*` env contains secrets
- public URL is invented or copied from docs
- submission docs are updated before verification
- historical proof scripts are modified

## 12. Acceptance Criteria

PS-018B is accepted only when:

- backend is deployed publicly
- frontend is deployed publicly
- explicit live URL smoke passes
- `public_url_verified` is true
- submission docs record verified URLs
- proof doc records verified URLs and smoke status
- no secrets are committed
- default public demo remains safe
- historical scripts untouched
- frontend build still passes
- repo branch is committed and pushed

## 13. Truth Boundary

PS-018B proves ProofStudio has a working public app URL only for the verified deployed URLs and smoke timestamp.

PS-018B does not prove:

- final Devpost submission
- long-term production availability
- authentication
- production persistence
- background job reliability
- legal authenticity
- C2PA authenticity
- semantic truth
- human authorship
- that every future deploy will remain healthy
