# ProofStudio — Render Deployment Runbook

## PS-042C0 free staging profile

PS-042C0A prepares the single free staging Blueprint at
[`render.free.yaml`](../../render.free.yaml). This is a local, reviewable
deployment plan only. It does not contact Render or authorize synchronization.
PS-042C0B may synchronize one Blueprint after independent review. A later paid
conversion must change that same Blueprint's path to `render.yaml`; it must not
create a second Blueprint alongside the staging one.

The staging profile has free API, auth, and PostgreSQL resources, plus the free
static site. Free services may sleep. Do not send keep-alive traffic, and do
not conduct final judging on free services. The free PostgreSQL database is a
temporary 1 GB database with no backup. Stop before synchronization if the
Render preview shows any non-zero charge.

Migrations remain an explicit operator action. Database external access begins
blocked with `ipAllowList: []`. During PS-042C0B only, the operator may
temporarily allow the operator's exact current IP to run migrations, then must
remove that external access immediately after migration. No migration runs in
a build, start, startup, pre-deploy, or initial-deploy hook.

The staging profile contains no provider, B2, OAuth, or email-delivery
credential and no real judge account. Email uses the accepted local capture
mode (`PROOFSTUDIO_EMAIL_PROVIDER=capture` and
`PROOFSTUDIO_EMAIL_CAPTURE_MODE=local`), which satisfies readiness without
sending email. Synthetic accounts are provisioned later through the accepted
explicit command after migrations pass.

The same-origin gateway is pinned to
`https://proofstudio-auth.onrender.com`. Live synchronization must stop if
Render does not assign that exact hostname. The auth service calls the free API
through its public `RENDER_EXTERNAL_URL`, because the free API cannot receive
private-network traffic.

## PS-042B1 production release blueprint

PS-042B1 replaces the two-resource PS-018 plan with a committed, locally
validated four-resource topology. It does not synchronize the Blueprint,
create a paid resource, run a production migration, provision a judge account,
or prove that the accepted application is deployed.

| Resource | Current Blueprint shape | Purpose |
| --- | --- | --- |
| `proofstudio-web` | `type: web`, `runtime: static` | Vite application and same-origin gateway |
| `proofstudio-auth` | `type: web`, `runtime: node`, `plan: starter` | Better Auth, sessions, account/private proof gateway |
| `proofstudio-api` | `type: web`, `runtime: python`, `plan: starter` | Public proof and server-authenticated private proof APIs |
| `proofstudio-db` | Render Postgres `basic-256mb`, PostgreSQL 18 | Auth, session, membership and access data |

The two dynamic services and database are pinned to `oregon`. The `starter`
services are the always-on release-candidate posture required to avoid the
historical free-service wake-up delay. They and the paid database must not be
created without explicit human approval. `autoDeployTrigger: off` keeps a push
from authorizing a deployment.

The web service has exactly one ordered `routes` mapping. `/auth/*`,
`/session`, `/logout`, `/account/*`, `/healthz`, and `/readyz` rewrite to the
auth web service before the final `/* -> /index.html` SPA fallback. Rewrites
retain the browser-visible web URL, so cookies remain first-party. The same six
families receive `Cache-Control: no-store` at the static gateway; the auth
runtime also applies `no-store` and `Pragma: no-cache` before dispatch.

Render's current Blueprint names are used: `runtime` rather than legacy `env`,
`autoDeployTrigger` rather than deprecated `autoDeploy`, `runtime: static` for
the static site, `previews.generation: off` rather than deprecated
`previewsEnabled`, `preDeployCommand` for migrations, `fromService` /
`fromDatabase` references, and a current flexible PostgreSQL plan. Every
`fromService` reference includes the required service `type`.

### Build, start, migration and health commands

| Resource | Build | Pre-deploy | Start / publish | Health |
| --- | --- | --- | --- | --- |
| API | `pip install -r apps/api/requirements.txt` | none | `PYTHONPATH=src uvicorn proofstudio.api.app:app --host 0.0.0.0 --port $PORT` | `/health` |
| Auth | `npm ci --include=dev && npm run build` | `npm run drizzle:migrate` | `npm run start` | `/readyz` |
| Web | `npm ci && npm run build` | none | publish `dist` | static shell |

Auth resolves `PORT` before its local `PROOFSTUDIO_AUTH_SERVER_PORT` fallback
and defaults to `0.0.0.0` in production. Invalid ports fail startup. Local
defaults remain `127.0.0.1:8787`. Migration failure blocks activation; startup
does not run migrations. Do not automate a down migration during rollback.

The generated internal service token lives first on `proofstudio-auth` and is
referenced into `proofstudio-api`; it is never a `VITE_*` value. The auth
database URL comes from `proofstudio-db.connectionString`. Public Render URLs
are referenced through `RENDER_EXTERNAL_URL`; provider and B2 credentials are
absent. The four execution flags remain false.

### Local release-candidate validation

Run without production credentials or network calls:

```bash
python3 scripts/ps042b1_render_blueprint_smoke.py
cd apps/auth-server && npm run typecheck && npm run build && npm run drizzle:check && npm run smoke:production-topology
cd ../web && npm run typecheck && npm run build && npm run smoke:production-auth-gateway
cd ../.. && python3 scripts/proofstudio_regression_gate.py --current ps042b1 --frontend --report-out /tmp/proofstudio-ps042b1-release-report.json
```

The feature smokes are check-only and non-recursive. The central gate writes
only the requested `/tmp` report and must leave the canonical PS-034A report
digest unchanged.

### Deployment and rollback boundary

PS-042C, not PS-042B1, owns any Blueprint synchronization, paid-resource
approval, production migration, judge provisioning, public endpoint checks,
browser matrix, and cold-start observation. When separately authorized, set
the server-only email readiness values in Render's secret manager before
traffic activation; OAuth and live provider/B2 credentials remain optional.

Rollback order is: freeze changes; preserve redacted logs; roll back web only
if gateway routing is defective; roll back auth and API to accepted deploys;
retain the forward-compatible database schema; verify `/health`, `/version`,
`/healthz`, `/readyz`; then rerun public and authenticated journeys. Never
delete production data or automatically reverse migrations.

The historical PS-018/PS-018B material below records the earlier public demo.
It does not prove that this four-resource release candidate is deployed.

<!-- PS-018B_CURRENT_PUBLIC_DEPLOYMENT_START -->
## Current public deployment status — PS-018B

PS-018B supersedes the earlier PS-018 pre-deployment state.

- Public app URL: `https://proofstudio-web.onrender.com`
- Public API URL: `https://proofstudio.onrender.com`
- Live URL smoke: passed.
- Public URL verified: true.
- API health/version: verified.
- Frontend load: verified.
- CORS preflight from the deployed frontend origin: verified.
- Safe public dry-run: verified with no provider call and no B2/Genblaze write.

Evidence:

- `docs/ps-018b-render-deployment-public-url-verification-proof.md`
- `docs/evidence/ps-018b/live-url-smoke-summary.json`
- `docs/evidence/ps-018b/live-url-smoke-transcript.json`
- `docs/evidence/ps-018b/safe-public-dry-run-semantic.json`
<!-- PS-018B_CURRENT_PUBLIC_DEPLOYMENT_END -->


Selected public-deployment target for PS-018: **Render**.

This runbook documents how to deploy the ProofStudio FastAPI backend and the
Vite/React Review Room frontend to Render, and how to verify the public URLs.
It is **preparation + a gated live URL smoke path**, not a claim that a
deployment is live. A public URL is only valid once the PS-018 live URL smoke
passes against real URLs (see
[`scripts/ps018_live_url_smoke.py`](../../scripts/ps018_live_url_smoke.py)).

Re-read Render's current docs before a real deploy — hosting UIs, env-var
conventions, and blueprint schema change over time.

## Why Render was selected

Render was chosen because it maps cleanly onto the current ProofStudio
architecture without forcing a redesign:

- Render runs **long-running Python web services**, so the FastAPI backend
  (`uvicorn proofstudio.api.app:app`) runs as a real process host, preserving
  the in-memory store contract (important caveat: the store is still in-memory;
  see limitations).
- Render has a **static site** service type that serves the built Vite `dist/`
  over HTTPS, matching the local two-origin architecture (frontend + backend).
- Render supports **environment variables and encrypted secrets**, so the
  `.env.production.example` shape maps directly to Render's env/secret model.
- Render terminates **TLS** and gives each service a public HTTPS URL, which is
  the missing judge requirement (a working public app URL).
- Render supports a **blueprint** (`render.yaml`) so the deployment plan is
  reviewable in the repo.

This is a hackathon/public-demo deployment target, not a final production
architecture decision.

## Services in the blueprint

The deployment plan lives in [`render.yaml`](../../render.yaml):

| Service | Render type | Root | Purpose |
| --- | --- | --- | --- |
| `proofstudio-api` | `web` (Python) | repo root | FastAPI backend |
| `proofstudio-web` | `static` | `apps/web` | Vite/React frontend |

## Backend service setup

1. Create a **Web Service** on Render, connected to this GitHub repo, Python
   runtime.
2. Root directory: repository root (`.`) so the start command resolves
   `PYTHONPATH=src` and the build command resolves `apps/api/requirements.txt`.
3. Build command:

   ```text
   pip install -r apps/api/requirements.txt
   ```

   There is no separate build step beyond installing declared dependencies.
   `apps/api/requirements.txt` includes `fastapi`, `uvicorn`, and `httpx`.

4. Start command (uses the platform `$PORT`; never hard-code 8000):

   ```text
   PYTHONPATH=src uvicorn proofstudio.api.app:app --host 0.0.0.0 --port $PORT
   ```

5. Health check path: `/health` (`GET /health` returns `{ok: true, ...}`).

## Frontend static site setup

1. Create a **Static Site** on Render, connected to this GitHub repo.
2. Root directory: `apps/web`.
3. Build command:

   ```text
   npm ci && npm run build
   ```

   (`npm run build` runs `tsc --noEmit` then `vite build`.)
4. Publish directory: `dist`.
5. SPA fallback: rewrite all routes to `/index.html` so client-side routing
   resolves (the frontend is a single-page app).

## Environment variables

Render distinguishes **public env values** (safe in the blueprint) from
**per-deployment values / secrets** (set in the dashboard). In `render.yaml`,
secret-shaped and per-deployment variables use `sync: false`, which keeps the
dashboard value and never commits a real one.

### Backend (web service)

| Variable | Where to set | Notes |
| --- | --- | --- |
| `PROOFSTUDIO_ENV` | blueprint | `production` |
| `PROOFSTUDIO_RUN_LIVE_DEFAULT` | blueprint | `false`. Live provider/B2 runs are never the default. |
| `PROOFSTUDIO_PUBLIC_API_BASE_URL` | dashboard | The real public API base URL after deploy. |
| `PROOFSTUDIO_PUBLIC_WEB_URL` | dashboard | The real public web URL after deploy. |
| `PROOFSTUDIO_CORS_ORIGINS` | dashboard | The exact frontend origin(s). Explicit only; never `*`. |
| `B2_*`, `CLOUDFLARE_*`, `GEMINI_API_KEY`, `ELEVENLABS_API_KEY` | dashboard | **Optional.** Leave unset for a dry-run-only public demo. Never commit. |

### Frontend (static site)

| Variable | Where to set | Notes |
| --- | --- | --- |
| `VITE_PROOFSTUDIO_API_BASE_URL` | dashboard (build env) | The public API base URL. This is a **public build-time** value. Never put a secret behind a `VITE_` prefix. |

`VITE_*` variables are inlined by Vite at **build time**, so
`VITE_PROOFSTUDIO_API_BASE_URL` must be present in the build environment (the
Render dashboard static-site env), not only at runtime.

## Build commands (summary)

| Artifact | Command |
| --- | --- |
| Backend deps | `pip install -r apps/api/requirements.txt` |
| Frontend bundle | `npm ci && npm run build` (inside `apps/web`, with `VITE_PROOFSTUDIO_API_BASE_URL` set) |

## Start commands (summary)

| Service | Command |
| --- | --- |
| Backend | `PYTHONPATH=src uvicorn proofstudio.api.app:app --host 0.0.0.0 --port $PORT` |
| Frontend | served by Render's static host from `apps/web/dist` |

## Health check path

`GET /health` returns `{ok: true, service, mode, version, environment}`. Set the
backend web service's health check to `/health`.

`GET /version` returns service, version, framework mode, capabilities, and the
detected git branch.

## CORS / domain setup

The backend reads `PROOFSTUDIO_CORS_ORIGINS` (comma-separated) and merges it
with the local demo origins. Rules (implemented in
`src/proofstudio/api/app.py`):

- The local demo origins (`http://127.0.0.1:5173`, `http://localhost:5173`,
  `http://127.0.0.1:4173`, `http://localhost:4173`) are always preserved.
- Production origins from `PROOFSTUDIO_CORS_ORIGINS` are merged in, deduped.
- Wildcard production CORS (`*`) is **refused**; the backend logs a warning and
  falls back to local-only.
- `allow_credentials` stays `false` (no cookies / HTTP auth).

For Render: set `PROOFSTUDIO_CORS_ORIGINS` to the exact deployed web origin
(e.g. `https://proofstudio-web.onrender.com`). Never use `*`.

## How to deploy from GitHub

1. Push the `ps-018/...` branch (or merge to `main`, per your workflow).
2. In Render, create the two services from `render.yaml` (Render reads the
   blueprint) or create them manually per the setup above.
3. In the Render dashboard, set every `sync: false` variable:
   - Backend: `PROOFSTUDIO_PUBLIC_API_BASE_URL`,
     `PROOFSTUDIO_PUBLIC_WEB_URL`, `PROOFSTUDIO_CORS_ORIGINS`.
   - Frontend build env: `VITE_PROOFSTUDIO_API_BASE_URL` (point at the deployed
     API URL).
   - Optional provider/B2 secrets — only if live runs will be allowed.
4. Trigger a deploy. Watch the backend logs for `Uvicorn running on ...`.
5. Walk the "After deploying" section of
   [`preflight-checklist.md`](./preflight-checklist.md).

## How to set the frontend API base URL

`VITE_PROOFSTUDIO_API_BASE_URL` is the only knob. Set it in the Render static
site's environment (build environment) to the public backend URL. The frontend
falls back to `http://127.0.0.1:8000` only when unset; a production bundle
should not silently fall back to localhost.

## How to verify public URLs

Honest verification means checking real endpoints against real public URLs:

- `GET <api-url>/health` → `200`, `{ok: true, ...}`.
- `GET <api-url>/version` → `200`, version present.
- Open the public web URL; the Review Room loads.
- The **API Status** card reports the backend online (no CORS block).
- A CORS preflight from the frontend origin to `/version` succeeds.

Do **not** record a URL as verified until the live smoke actually passes it.

## How to run the PS-018 live URL smoke

Local contract mode (default; skips public URL verification; no providers, no B2):

```bash
cd /home/proofstudio-work/proofstudio
source .venv/bin/activate
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"
python scripts/ps018_live_url_smoke.py
```

Live URL mode (explicit, only when real public URLs exist):

```bash
export PS018_RUN_LIVE_URL_SMOKE=true
export PROOFSTUDIO_PUBLIC_API_BASE_URL=https://<real-api-host>
export PROOFSTUDIO_PUBLIC_WEB_URL=https://<real-web-host>
python scripts/ps018_live_url_smoke.py
```

Live URL mode runs only when all three env vars are set and both URLs are
non-localhost HTTPS. It verifies `/health`, `/version`, frontend HTML, a CORS
preflight for `/version`, a safe campaign creation, and a safe dry-run
(`run_live=false`) — and proves the safe run made no provider and no B2 call.

If public URLs are absent, the smoke honestly reports
`live_url_smoke_status: skipped_missing_urls`.

## What not to expose

- Never commit real provider or storage credentials.
- Never commit a real `.env` or `.env.production`. Only `.env.production.example`
  (placeholders) is tracked.
- Never put secrets behind `VITE_*` variables (they are public at build time).
- Never set `PROOFSTUDIO_CORS_ORIGINS=*` in production.
- Never echo secrets into build/runtime logs.

## Limitations

- **Public deployment is not proven until real URLs pass the live smoke.**
  Level A (this slice by default) proves target selection, configuration, and
  the smoke path — not a live public URL.
- Provider/B2 secrets are **optional** for the default safe public demo. The
  default path is a dry-run: no provider call, no B2 call.
- **Explicit live generation remains manually gated** (`run_live=true`). It is
  never the default and is not part of the default smoke.
- The backend live store is **in-memory** (process-local). Durability lives in
  the B2 run archive, not a production database.
- No authentication / authorization layer.
- Render free-tier services may spin down after inactivity; first request after
  idle can be slow.
- This runbook describes a hackathon/public-demo target, not final production
  architecture.

## Truth boundary

This runbook proves ProofStudio has a selected Render deployment target, a
reviewable deployment plan (`render.yaml`), and a gated live URL smoke path. It
does **not** prove a public deployment exists, a working public app URL, final
Devpost submission, production availability, authentication, production
persistence, background job reliability, legal authenticity, C2PA authenticity,
semantic truth, or human authorship — unless and until real public URLs pass
the PS-018 live URL smoke.
