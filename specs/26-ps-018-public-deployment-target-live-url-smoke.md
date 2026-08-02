# PS-018 Public Deployment Target Selection + Live URL Smoke

## 1. Purpose

PS-018 moves ProofStudio from deployment preparation to a selected public deployment target and a real live URL smoke path.

Previous milestones proved:

- PS-015: deterministic local demo seed pack and one-click local demo
- PS-016: judge-ready submission script and evidence pack
- PS-017: deployment preparation, production environment template, and CORS/environment hardening

PS-018 targets the next missing judge requirement:

- a working public app URL judges can access

This slice must select a deployment target, prepare target-specific deployment configuration/runbook, and create a live URL smoke that verifies public frontend/backend behavior without running live providers or B2 by default.

## 2. Selected Target

Selected deployment target for PS-018:

- Render

Reason:

- Render supports Python/FastAPI web services.
- Render supports static frontend hosting.
- Render supports environment variables/secrets.
- ProofStudio currently has a FastAPI backend and a Vite/React frontend.
- PS-017 already prepared production CORS and environment templates.

Do not treat this as final production architecture.

This is a hackathon/public-demo deployment target.

## 3. Product Meaning

ProofStudio already works locally.

PS-018 must make it judge-accessible by preparing and validating:

- public backend URL
- public frontend URL
- public API health
- public API version
- frontend loading from a public URL
- frontend configured to talk to the public backend
- safe dry-run behavior through the public backend
- no live provider or B2 calls by default

The public URL should be added to submission docs only after a real URL exists.

## 4. Safety Principle

Do not expose secrets.

Do not commit real API keys.

Do not commit `.env`.

Do not make live mode default.

Do not run live providers during default live URL smoke.

Do not call B2 during default live URL smoke.

Do not claim public deployment until a real deployed URL is supplied and verified.

Do not fake public health checks.

Do not fake screenshots.

Do not fake generated media.

Do not fake provider success.

Do not fake B2 or Genblaze evidence.

## 5. Current Deployment Foundation

From PS-017:

- `.env.production.example`
- `docs/deployment/README.md`
- `docs/deployment/environment.md`
- `docs/deployment/cors-and-security.md`
- `docs/deployment/platform-decision.md`
- `docs/deployment/preflight-checklist.md`
- `scripts/ps017_deployment_prep_smoke.py`
- environment-based CORS origin reader in `src/proofstudio/api/app.py`

Current backend production-style start command:

- `uvicorn proofstudio.api.app:app --host 0.0.0.0 --port 8000`

Render-style backend start should use platform port environment when needed:

- `PYTHONPATH=src uvicorn proofstudio.api.app:app --host 0.0.0.0 --port $PORT`

Current frontend production build command:

- `cd apps/web && npm run build`

Current frontend API base env:

- `VITE_PROOFSTUDIO_API_BASE_URL`

Reminder:

- `VITE_*` variables are frontend-public build variables.
- Do not put secrets in `VITE_*` variables.

## 6. Non-Goals

Do not add authentication.

Do not add a production database.

Do not add a queue.

Do not add persistent production storage.

Do not change provider router behavior.

Do not run live AI generation by default.

Do not run B2 by default.

Do not redesign the UI.

Do not merge branches.

Do not modify historical proof scripts.

Do not claim final Devpost submission.

## 7. Required Files

Allowed new files:

- `render.yaml`
- `docs/deployment/render.md`
- `scripts/ps018_live_url_smoke.py`
- `docs/ps-018-public-deployment-target-live-url-smoke-proof.md`

Allowed modified files:

- `README.md`
- `apps/web/README.md`
- `.env.production.example`
- `docs/deployment/README.md`
- `docs/deployment/platform-decision.md`
- `docs/deployment/preflight-checklist.md`
- `docs/submission/submission-checklist.md`
- `docs/submission/judge-evidence-pack.md`
- `apps/api/requirements.txt` only if clean deployment import requires dependency correction
- `src/proofstudio/api/app.py` only if live URL/CORS smoke reveals a tiny production compatibility issue

Avoid backend changes unless the live URL path proves they are necessary.

Do not modify historical proof scripts:

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

## 8. Render Configuration Requirement

Create:

- `render.yaml`

It must define a clear Render deployment plan for:

### Backend service

- service type: web service
- runtime: Python or equivalent Render-supported Python service
- root: repository root unless implementation proves another path is safer
- build command based on actual repo dependency files
- start command compatible with Render port environment
- health check path: `/health`
- production environment keys needed by backend
- no real secrets

Expected backend start shape:

- `PYTHONPATH=src uvicorn proofstudio.api.app:app --host 0.0.0.0 --port $PORT`

The implementation must inspect actual dependency files before choosing the final build command.

### Frontend service

- service type: static site
- root: `apps/web`
- build command: `npm ci && npm run build` or equivalent
- publish directory: `dist`
- frontend public API base URL variable pointing to backend public URL placeholder
- no secrets in frontend env variables

If a single Render blueprint cannot safely represent both backend and frontend in this repo, document the manual Render setup in `docs/deployment/render.md` and keep `render.yaml` as the best-effort baseline.

## 9. Render Runbook Requirement

Create:

- `docs/deployment/render.md`

It must include:

- selected target: Render
- why Render was selected
- backend service setup
- frontend static site setup
- environment variables
- build commands
- start commands
- health check path
- CORS/domain setup
- how to deploy from GitHub
- how to set frontend API base URL
- how to verify public URLs
- how to run PS-018 live URL smoke
- what not to expose
- limitations

It must clearly state:

- public deployment is not proven until real URLs pass the live smoke
- provider and B2 secrets are optional for the default public safe demo
- explicit live generation should remain manually gated

Avoid secret-like assignment examples in prose.

Use table/prose style for secret placeholders.

## 10. Live URL Smoke Requirement

Create:

- `scripts/ps018_live_url_smoke.py`

The smoke must support two modes:

### Local contract mode

Default mode.

This mode does not require public URLs.

It verifies:

- required PS-018 docs/config files exist
- `render.yaml` exists and references backend/frontend deployment plan
- `docs/deployment/render.md` exists and documents Render setup
- no secrets are present
- historical scripts untouched
- frontend build passes
- PS-017 prep remains intact

It must not call live providers or B2.

### Live URL mode

Explicit gated mode.

It may run only when:

- `PS018_RUN_LIVE_URL_SMOKE` is true
- `PROOFSTUDIO_PUBLIC_API_BASE_URL` is set to a non-localhost HTTPS URL
- `PROOFSTUDIO_PUBLIC_WEB_URL` is set to a non-localhost HTTPS URL

Live URL mode must verify:

- API `/health` returns success
- API `/version` returns success
- frontend public URL returns HTML
- API CORS preflight from frontend origin succeeds for `/version`
- safe campaign creation works if endpoint contract supports it
- safe dry-run creation works with `run_live` false if endpoint contract supports it
- safe run does not include live provider call
- safe run does not include B2 call
- public URLs are not localhost
- no invented/fake URL results

If live URLs are absent, live smoke must be skipped honestly and summary must show:

- `live_url_smoke_status`: `skipped_missing_urls`

If live URLs are present but fail, summary must show failure and exit non-zero.

## 11. Required Smoke Summary Fields

The PS-018 smoke summary must include stable schema:

- `ok`
- `slice`
- `selected_target`
- `render_config_checked`
- `render_runbook_checked`
- `deployment_docs_updated`
- `submission_docs_updated`
- `env_template_checked`
- `no_secret_leakage`
- `historical_scripts_untouched`
- `frontend_build_checked`
- `frontend_build_status`
- `local_contract_checked`
- `live_url_mode_enabled`
- `live_url_smoke_status`
- `public_api_url_status`
- `public_web_url_status`
- `api_health_checked`
- `api_version_checked`
- `web_load_checked`
- `cors_preflight_checked`
- `safe_public_dry_run_checked`
- `default_no_live_provider_call`
- `default_no_b2_call`
- `public_url_verified`
- `backend_changed`
- `frontend_app_changed`
- `summary_path`
- `transcript_path`
- `truth_boundary`

Schema rules:

- booleans must be booleans
- status fields must be strings
- lists must use `*_paths` or `*_items`
- URL fields must not contain fake URLs
- if no public URLs are set, `public_url_verified` must be false

Expected default local contract summary:

- `ok`: true
- `selected_target`: `render`
- `live_url_mode_enabled`: false
- `live_url_smoke_status`: `skipped_missing_urls`
- `public_url_verified`: false
- `default_no_live_provider_call`: true
- `default_no_b2_call`: true

Expected live URL summary after real deployment:

- `ok`: true
- `live_url_mode_enabled`: true
- `live_url_smoke_status`: `passed`
- `public_url_verified`: true
- `api_health_checked`: true
- `api_version_checked`: true
- `web_load_checked`: true
- `cors_preflight_checked`: true

## 12. Documentation Update Requirement

Update:

- `docs/deployment/platform-decision.md`

It must move selected status from pending to:

- selected: Render

It must include why Render was chosen and what remains to verify.

Update:

- `docs/deployment/README.md`

It must point to:

- `docs/deployment/render.md`
- `scripts/ps018_live_url_smoke.py`
- live URL env vars required for explicit smoke

Update:

- `docs/deployment/preflight-checklist.md`

It must include PS-018 live URL smoke steps.

Update:

- `docs/submission/submission-checklist.md`

It must mark public URL as:

- pending until live URL smoke passes

If real URLs are available and smoke passes, it may record the real verified URLs.

If no real URLs exist yet, keep public URL pending.

Update:

- `docs/submission/judge-evidence-pack.md`

It must mention PS-018 selected deployment target and live URL smoke status honestly.

## 13. Proof Document Requirement

Create:

- `docs/ps-018-public-deployment-target-live-url-smoke-proof.md`

It must include:

- status
- selected target
- files created/modified
- backend changed or unchanged
- frontend app changed or unchanged
- Render config status
- public URL status
- live URL smoke mode
- smoke summary path
- transcript path
- no-secret proof
- no fake URL proof
- default no-live/no-B2 proof
- limitations
- next milestone recommendation
- truth boundary

## 14. Acceptance Criteria

PS-018 has two acceptance levels.

### Level A: Target selection and live smoke readiness

Accepted if:

- Render is selected and documented
- `render.yaml` exists or an honest manual Render setup is documented
- live URL smoke script exists
- local contract smoke passes
- frontend build passes
- no secrets are introduced
- no fake URLs are introduced
- historical scripts untouched
- public URL status is honestly pending if not deployed

### Level B: Real public URL verified

Accepted only if:

- public API URL is supplied
- public web URL is supplied
- live URL smoke is explicitly enabled
- public `/health` passes
- public `/version` passes
- public frontend loads
- CORS preflight passes
- safe public dry-run passes without provider/B2 calls
- public URL is recorded in submission docs

If only Level A is completed, the next milestone should be actual deployment execution and URL verification, or PS-018B if using suffix workflow.

## 15. Failure Conditions

Reject PS-018 if:

- it claims public URL verified without live smoke
- it invents public URLs
- it invents public health checks
- it exposes secrets
- it commits real provider/storage credentials
- it makes live mode default
- it calls live providers during default smoke
- it calls B2 during default smoke
- it puts secrets in frontend `VITE_*` variables
- it weakens CORS to wildcard production behavior
- it modifies historical proof scripts
- it uses list values where boolean fields are required
- truth boundary omits required non-claims

## 16. Truth Boundary

PS-018 Level A proves ProofStudio has a selected deployment target, Render deployment configuration/runbook, and a gated live URL smoke path.

PS-018 Level A does not prove:

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

PS-018 Level B proves a public URL only if real URLs are supplied and the explicit live URL smoke passes.
