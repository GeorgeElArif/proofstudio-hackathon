# PS-018 Public Deployment Target Selection + Live URL Smoke — Proof

> **Historical note:** This PS-018 Level A proof was true before real public deployment. It is now superseded by PS-018B, which verifies the live Render frontend and backend URLs. See `docs/ps-018b-render-deployment-public-url-verification-proof.md`.


## Status

**Complete — Level A (target selection + live smoke readiness).** PS-018 moves
ProofStudio from deployment preparation to a **selected** public-deployment
target (Render), a reviewable deployment plan (`render.yaml`), a Render runbook,
and a gated live URL smoke path. The default smoke passes without public URLs,
providers, or B2.

**Level B (real public URL verified) is not claimed.** No real public URL is
supplied or invented. The public URL is honestly **pending** until the live URL
smoke passes against real non-localhost HTTPS URLs.

## Selected target

**Render.**

Render was selected because it maps cleanly onto the current architecture
without a redesign: long-running Python web service (FastAPI backend), a static
site service (Vite/React frontend), env vars + encrypted secrets, TLS, and a
reviewable blueprint. See `docs/deployment/render.md` for the full rationale.

## Files created

- `render.yaml` — Render blueprint (backend `web` + frontend `static`).
- `docs/deployment/render.md` — Render runbook.
- `scripts/ps018_live_url_smoke.py` — two-mode live URL smoke.
- `docs/ps-018-public-deployment-target-live-url-smoke-proof.md` — this file.

## Files modified

- `README.md` — updated deployment/submission pointers (Render selected).
- `apps/web/README.md` — added Render pointer + live URL smoke reference.
- `.env.production.example` — added PS-018 live-URL smoke placeholder
  (`PS018_RUN_LIVE_URL_SMOKE=false`) and updated header.
- `docs/deployment/README.md` — Render target section, PS-018 smoke steps, live
  URL env vars.
- `docs/deployment/platform-decision.md` — `selected: Render`; real URL pending;
  Render start command (`$PORT`).
- `docs/deployment/preflight-checklist.md` — PS-018 local + live URL smoke steps.
- `docs/submission/submission-checklist.md` — public URL pending until live
  smoke passes; deployment target section.
- `docs/submission/judge-evidence-pack.md` — PS-016/017/018 slices added;
  Render selected + live URL smoke status honest.

## Backend changed

**No.** `src/` is untouched. The PS-017 CORS/env reader (`app.py`) already
supports production origins, wildcard refusal, and `allow_credentials=false`, so
no production-compatibility edit was required. The smoke confirms
`backend_changed: false`.

## Frontend app changed

**No.** `apps/web/src/` is untouched. `apps/web/src/api.ts` already resolves
`VITE_PROOFSTUDIO_API_BASE_URL` with a local fallback, so no app-source edit was
required. Only `apps/web/README.md` was updated. The smoke confirms
`frontend_app_changed: false`.

## Render config status

`render.yaml` is complete and reviewable:

- Backend `web` service (Python), root = repo root,
  `buildCommand: pip install -r apps/api/requirements.txt`,
  `startCommand: PYTHONPATH=src uvicorn proofstudio.api.app:app --host 0.0.0.0 --port $PORT`,
  `healthCheckPath: /health`.
- Frontend `static` service, root = `apps/web`,
  `buildCommand: npm ci && npm run build`, publish = `dist`, SPA rewrite to
  `/index.html`.
- `PROOFSTUDIO_ENV=production`, `PROOFSTUDIO_RUN_LIVE_DEFAULT=false`.
- All per-deployment and secret-shaped env vars use `sync: false` (set in the
  Render dashboard; never committed).
- `VITE_PROOFSTUDIO_API_BASE_URL` is a public build-time value (no secrets
  behind a `VITE_` prefix).

## Public URL status

**`pending`** / `public_url_verified: false`. No real public URL exists or is
invented. The live URL smoke reports `live_url_smoke_status:
skipped_missing_urls` because no real URLs were supplied.

## Live URL smoke mode

**Local contract mode (default).** It verifies: required PS-018 files exist;
`render.yaml` references backend/frontend, `$PORT`, `/health`, `dist`, npm build,
and the frontend API base URL variable; `docs/deployment/render.md` covers the
required topics; the env template is placeholders-only; deployment/submission
docs updated; PS-017 prep intact (CORS reader, `/health`, `/version`, default
safe dry-run); frontend build passes; backend/frontend app unchanged;
historical scripts untouched; no secrets; proof doc sections present.

**Live URL mode** is gated behind `PS018_RUN_LIVE_URL_SMOKE=true` plus both
non-localhost HTTPS `PROOFSTUDIO_PUBLIC_API_BASE_URL` and
`PROOFSTUDIO_PUBLIC_WEB_URL`. It is not exercised in this slice because no real
public URLs exist.

## Smoke summary path

`/tmp/proofstudio-ps-018/live-url-smoke-summary.json`

Expected default (Level A) summary keys:

- `ok: true`
- `slice: "PS-018"`
- `selected_target: "render"`
- `render_config_checked: true`
- `render_runbook_checked: true`
- `deployment_docs_updated: true`
- `submission_docs_updated: true`
- `env_template_checked: true`
- `no_secret_leakage: true`
- `historical_scripts_untouched: true`
- `frontend_build_checked: true`
- `frontend_build_status: "passed"`
- `local_contract_checked: true`
- `live_url_mode_enabled: false`
- `live_url_smoke_status: "skipped_missing_urls"`
- `public_api_url_status: "not_set"`
- `public_web_url_status: "not_set"`
- `api_health_checked: false`
- `api_version_checked: false`
- `web_load_checked: false`
- `cors_preflight_checked: false`
- `safe_public_dry_run_checked: false`
- `default_no_live_provider_call: true`
- `default_no_b2_call: true`
- `public_url_verified: false`
- `backend_changed: false`
- `frontend_app_changed: false`

## Transcript path

`/tmp/proofstudio-ps-018/live-url-smoke-transcript.json`

## No-secret proof

- `render.yaml` commits no real values: every secret-shaped / per-deployment env
  var uses `sync: false`; only public defaults (`PROOFSTUDIO_ENV=production`,
  `PROOFSTUDIO_RUN_LIVE_DEFAULT=false`) carry values.
- `.env.production.example` keeps every value a known placeholder
  (`replace-me`, `https://replace-with-api-host`, `https://replace-with-web-host`,
  `production`, `0.0.0.0`, `8000`, `false`).
- The smoke scans `render.yaml`, `render.md`, the env template, this proof doc,
  and the updated deployment/submission docs for real-secret patterns (bearer
  tokens, real Backblaze object URLs, long secret-like assignments). None found.
- The smoke scans its own transcript JSON before writing and fails if any secret
  pattern appears. No B2 keys, Cloudflare tokens, Gemini keys, or ElevenLabs
  keys are present anywhere in the slice.
- No `VITE_*` variable holds a secret.

## No fake URL proof

- No public URL is invented. `public_url_verified` is `false`.
- `PROOFSTUDIO_PUBLIC_API_BASE_URL` / `PROOFSTUDIO_PUBLIC_WEB_URL` remain the
  `https://replace-with-*-host` placeholders in the template.
- The smoke refuses placeholder and localhost URLs in live URL mode; it does not
  fabricate health/version/CORS results. Local contract mode makes no network
  calls.
- Submission docs keep the working-app-URL item **PENDING**.

## Default no-live / no-B2 proof

The smoke drives the default API path through `TestClient`:

1. `POST /campaigns` → `201`.
2. `POST /runs` with `run_live=false` → `201`, `status=dry_run_created`,
   `dry_run=true`, `run_live=false`.
3. `GET /runs/{id}/attempts` → `attempt_count=0`.
4. `GET /runs/{id}/assets` → `asset_count=0`.
5. `GET /runs/{id}/manifest` → `ready=false`.

Structural evidence of a live provider call (`selected_provider` set, attempts
recorded) and of a B2 call (asset `b2_url`, `stored_manifest_verify`) are both
absent: `default_no_live_provider_call: true`, `default_no_b2_call: true`.
`PROOFSTUDIO_RUN_LIVE_DEFAULT=false` everywhere.

## Limitations

- No public deployment is verified live. Level B requires real Render URLs and
  a passing live URL smoke.
- Provider/B2 secrets are optional for the default safe public demo; explicit
  live generation remains manually gated (`run_live=true`).
- Backend store is in-memory (process-local).
- No authentication / authorization.
- Render free-tier services may spin down after inactivity.
- This is a hackathon/public-demo target, not final production architecture.

## Next milestone recommendation

Deploy to Render from `render.yaml`, set every `sync: false` value in the
Render dashboard, provision real public API + web URLs, then run
`scripts/ps018_live_url_smoke.py` in live URL mode. Only after it reports
`live_url_smoke_status: passed` and `public_url_verified: true`, record the real
public URL in `docs/submission/submission-checklist.md` (PS-018B / final
submission).

## Truth boundary

PS-018 Level A proves ProofStudio has a selected deployment target (Render), a
reviewable deployment plan (`render.yaml`), a Render runbook, and a gated live
URL smoke path. It does **not** prove:

- public deployment;
- a working public app URL;
- final Devpost submission;
- production availability;
- authentication;
- production persistence;
- background job reliability;
- legal authenticity;
- C2PA authenticity;
- semantic truth;
- human authorship.

PS-018 Level B proves a public URL only if real URLs are supplied and the
explicit live URL smoke passes.
