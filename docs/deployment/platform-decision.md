# ProofStudio — Platform Decision

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


What a deployment platform must support to host ProofStudio publicly, and the
current selection status. PS-018 **selects Render** as the public-deployment
passes against real URLs.

## Selection status

**`selected: Render`** — PS-018 selects Render as the hackathon / public-demo
deployment target. Render runs the FastAPI backend as a Python web service and
the Vite/React frontend as a static site, supports env vars and encrypted
secrets, terminates TLS, and exposes a reviewable blueprint (`render.yaml`).
See [`render.md`](./render.md) for the full setup.

deployment is live. A public URL is only valid once the PS-018 live URL smoke
(`scripts/ps018_live_url_smoke.py`) passes against real non-localhost HTTPS
URLs. Re-read Render's current docs before a real deploy, because hosting UIs,
env-var conventions, and blueprint schema change over time.

## What the platform must support

The platform must support, at minimum:

- A Python 3 runtime capable of running `uvicorn` and FastAPI.
- Long-running server processes (the backend is a stateful server, not a
  function-only surface).
- Configurable environment variables / secrets at runtime.
- A public HTTPS URL for the backend with TLS termination.
- A way to serve the built static frontend (Vite `dist/`) over HTTPS.
- Network egress to Backblaze B2 and the configured providers (only used on
  explicit live proof runs).
- Access to runtime logs for debugging.

## Hosting options

### Option A — Combined backend + frontend on one host

One server runs the FastAPI backend and also serves the static frontend bundle.
Simplest CORS story (same origin), simplest ops. Good for a small hackathon
deployment.

- Build frontend, copy `apps/web/dist/` into a directory the backend serves.
- Single public URL, e.g. `https://replace-with-web-host` (frontend) and
  `https://replace-with-web-host/api` (backend) — or same origin with no CORS
  needed.
- One TLS cert, one host.

### Option B — Separate backend and frontend hosts

Frontend is served by a static-edge platform (CDN/static host). Backend is a
long-running process host. Matches the current local two-origin architecture.

- Frontend public URL: `https://replace-with-web-host`.
- Backend public URL: `https://replace-with-api-host`.
- Requires explicit CORS on the backend (see `cors-and-security.md`).

Either option is acceptable. Option B mirrors the local two-terminal demo most
directly.

## Environment variable support

The platform must allow setting every variable in
[`.env.production.example`](../../.env.production.example) as a runtime secret
or env var, in particular:

- The required runtime variables (`PROOFSTUDIO_ENV`, host/port, public URLs,
  `PROOFSTUDIO_CORS_ORIGINS`, `PROOFSTUDIO_RUN_LIVE_DEFAULT=false`).
- The frontend build-time variable (`VITE_PROOFSTUDIO_API_BASE_URL`).
- The optional provider/B2 variables (only if live runs will be allowed).

Frontend build-time variables must be present in the build environment, not just
the runtime environment, because Vite inlines them at build time.

## Build commands

| Artifact | Command |
| --- | --- |
| Frontend bundle | `cd apps/web && npm run build` (after setting `VITE_PROOFSTUDIO_API_BASE_URL`) |
| Backend | no build step; install with `pip install -r apps/api/requirements.txt` (or install `src/` as a package) |

## Start commands

| Service | Command |
| --- | --- |
| Backend (Render) | `PYTHONPATH=src uvicorn proofstudio.api.app:app --host 0.0.0.0 --port $PORT` |
| Backend (local) | `uvicorn proofstudio.api.app:app --host 0.0.0.0 --port 8000` |
| Frontend (static) | serve `apps/web/dist/` with the platform's static host |

On Render the backend binds `0.0.0.0` and uses the platform-injected `$PORT`
(never hard-code 8000 in production). TLS is terminated by Render; the backend
itself is plain HTTP.

## CORS / domain setup

- If using Option B (separate hosts), set `PROOFSTUDIO_CORS_ORIGINS` on the
  backend to the exact frontend origin(s).
- If using Option A (combined host), CORS may be unnecessary because the
  frontend and backend share an origin. Keep the explicit allow-list anyway.
- Never use wildcard production CORS. See `cors-and-security.md`.

## Log access

The platform must expose:

- Backend stdout/stderr (uvicorn request logs + app logs).
- Build logs for both frontend and backend deploys.
- Enough history to debug a failed `/health` or `/version` after deploy.

## Secrets management

The platform must provide a secrets manager (or encrypted env vars) for:

- B2 keys, Cloudflare token, Gemini key, ElevenLabs key (if live runs allowed).
- Never echo secrets into build logs or runtime logs.

## Expected public URLs (placeholders)

| Role | URL |
| --- | --- |
| Public API | `https://replace-with-api-host` |
| Public Review Room | `https://replace-with-web-host` |

These are placeholders in `.env.production.example`. Real URLs will be
provisioned by a later slice once a platform is selected.

## Candidate platforms (not selected)

Other candidates that were evaluated before selecting Render (verify each
platform's current docs before any switch):

- Railway — long-running service; env vars; volumes.
- Fly.io — full-process hosts with TLS; secrets via `fly secrets`.
- Vercel / Netlify / Cloudflare Pages — static-frontend-friendly; for the
  backend these pair with a separate process host or serverless functions
  (note: FastAPI on serverless may not preserve in-memory state across
  invocations — important caveat for this app's in-memory store).
- A plain VM (e.g. a small cloud box) behind Caddy/nginx for TLS — most control,
  most manual ops.

## Truth boundary

This document captures the platform-selection criteria and the Render selection.
Selecting Render proves a target has been chosen and a deployment plan exists
(`render.yaml` + `render.md`). It does **not** prove a public deployment is
live, that any public URL works, that deployment succeeds end-to-end, or that
any of the other candidates currently behaves as summarized. Re-verify
Render's docs before implementing, and only record a public URL after the
PS-018 live URL smoke passes.

## PS-018B verified public URLs

Render remains the selected public deployment target. PS-018B verifies the real public URLs:

- Frontend public URL: `https://proofstudio-web.onrender.com`
- Backend public URL: `https://proofstudio.onrender.com`

The PS-018 live URL smoke passed in explicit live URL mode, and the separate semantic public dry-run confirmed the default public API path does not call live providers and does not write to B2/Genblaze storage.
