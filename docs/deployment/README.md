# ProofStudio — Deployment

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


PS-017 prepared ProofStudio for a future real public deployment. **PS-018
selects Render** as the public-deployment target and adds a reviewable
deployment plan (`render.yaml`), a Render runbook, and a gated live URL smoke.
against real URLs.

## Deployment status

See [`platform-decision.md`](./platform-decision.md) and
[`render.md`](./render.md).

## Local proof status

The local product is fully working through PS-016, and deployment prep through
PS-017:

- One-click local demo: `scripts/ps015_one_click_local_demo.py`
- Submission evidence pack: `scripts/ps016_submission_evidence_pack_smoke.py`
- Deployment prep smoke: `scripts/ps017_deployment_prep_smoke.py`
- Two-terminal stack (FastAPI + Vite Review Room)
- Safe dry-run by default (no provider, no B2, no fake media)
- Explicit opt-in live proof path

## Render target (PS-018)

- [`render.md`](./render.md) — the Render runbook (backend web service + frontend
  static site, env vars, build/start commands, CORS, GitHub deploy, how to
  verify public URLs, limitations).
- [`../../render.yaml`](../../render.yaml) — the Render blueprint (backend +
  frontend services; secrets use `sync: false`; no real secrets committed).
- [`../../scripts/ps018_live_url_smoke.py`](../../scripts/ps018_live_url_smoke.py)
  — the live URL smoke. Default mode is a safe local contract check (no
  providers, no B2). Live URL mode is explicit and only runs against real
  non-localhost HTTPS URLs.

## Live URL smoke env vars (explicit live mode only)

Live URL mode runs only when **all three** are set:

- `PS018_RUN_LIVE_URL_SMOKE=true`
- `PROOFSTUDIO_PUBLIC_API_BASE_URL` — real non-localhost HTTPS API URL
- `PROOFSTUDIO_PUBLIC_WEB_URL` — real non-localhost HTTPS web URL

If any are missing, the smoke honestly reports

## Production env template

The single source of truth for production environment shape is:

- [`../../.env.production.example`](../../.env.production.example)

It contains **placeholders only** (`replace-me`, `https://replace-with-api-host`,
`https://replace-with-web-host`). Copy it to your host's secret manager (or a
git-ignored `.env.production`) and replace every placeholder with a real value
before deploying. See [`environment.md`](./environment.md) for the full variable
reference.

PS-018B verified public URL values:

- Public API base URL: `https://replace-with-api-host`
- Public web URL: `https://replace-with-web-host`

## Commands

### Local deployment-prep smoke (safe, no providers, no B2)

```bash
cd /home/proofstudio-work/proofstudio
source .venv/bin/activate
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"
python -m py_compile scripts/ps017_deployment_prep_smoke.py
python scripts/ps017_deployment_prep_smoke.py
```

The smoke writes:

- `/tmp/proofstudio-ps-017/deployment-prep-summary.json`
- `/tmp/proofstudio-ps-017/deployment-prep-transcript.json`

It never calls live providers or B2.

### PS-018 live URL smoke (safe default; explicit live URL mode)

```bash
cd /home/proofstudio-work/proofstudio
source .venv/bin/activate
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"
python scripts/ps018_live_url_smoke.py
```

The default mode verifies the Render plan, docs, and PS-017 prep without
network calls, providers, or B2. It writes:

- `/tmp/proofstudio-ps-018/live-url-smoke-summary.json`
- `/tmp/proofstudio-ps-018/live-url-smoke-transcript.json`

Explicit live URL mode (only when real public URLs exist):

```bash
export PS018_RUN_LIVE_URL_SMOKE=true
export PROOFSTUDIO_PUBLIC_API_BASE_URL=https://<real-api-host>
export PROOFSTUDIO_PUBLIC_WEB_URL=https://<real-web-host>
python scripts/ps018_live_url_smoke.py
```

### Frontend production build

```bash
cd apps/web && npm run build
```

`npm run build` runs `tsc --noEmit` then `vite build`, producing static assets
in `apps/web/dist/`. When building for a real deployment, set
`VITE_PROOFSTUDIO_API_BASE_URL` to the public API base URL first.

### Backend start (production-style host binding)

```bash
cd /home/proofstudio-work/proofstudio
source .venv/bin/activate
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"
uvicorn proofstudio.api.app:app --host 0.0.0.0 --port 8000
```

On Render, use the platform port:
`PYTHONPATH=src uvicorn proofstudio.api.app:app --host 0.0.0.0 --port $PORT`
(see [`render.md`](./render.md)). For local development keep using
`--host 127.0.0.1 --port 8000 --reload`.

## Documents in this directory

- [`render.md`](./render.md) — Render runbook (PS-018 selected target).
- [`environment.md`](./environment.md) — full variable reference (required,
  optional, frontend vs backend, local vs production, secret handling).
- [`cors-and-security.md`](./cors-and-security.md) — local vs production CORS,
  wildcard guidance, credentials, secret handling.
- [`platform-decision.md`](./platform-decision.md) — platform requirements;
- [`preflight-checklist.md`](./preflight-checklist.md) — before/after deploy
  checklist (includes PS-018 live URL smoke steps).

## Next steps for a real deployment

Render is selected (PS-018), and PS-018B verifies the real public deployment. For future redeploys or final launch hardening:

1. Re-read Render's current docs, then deploy from `render.yaml` (see
   `render.md`).
2. Set every `sync: false` value in the Render dashboard (public API/web URLs,
   `PROOFSTUDIO_CORS_ORIGINS`, `VITE_PROOFSTUDIO_API_BASE_URL`).
3. Set explicit production CORS origins (no wildcard).
4. Provision real public API + web URLs and run the PS-018 live URL smoke in
   live URL mode against them.
5. The live URL smoke has passed in PS-018B; keep the real public URL recorded in
   `docs/submission/submission-checklist.md`.

## Truth boundary

This directory proves ProofStudio has deployment preparation (PS-017), a
selected Render deployment target with a reviewable plan (`render.yaml`) and
runbook (PS-018), an env template, and a preflight checklist. It does **not**
prove a public deployment exists, a working public app URL, final Devpost
submission, production availability, authentication, production persistence,
background job reliability, legal authenticity, C2PA authenticity, semantic
truth, or human authorship — unless and until the PS-018 live URL smoke passes
against real public URLs.

## PS-018 Render deployment target

The selected public deployment target for PS-018 is Render.

Target-specific runbook:

- `docs/deployment/render.md`

Live URL smoke script:

- `scripts/ps018_live_url_smoke.py`

Explicit live URL smoke requires these public, non-localhost HTTPS values:

- `PROOFSTUDIO_PUBLIC_API_BASE_URL`
- `PROOFSTUDIO_PUBLIC_WEB_URL`


## PS-018B live Render deployment

PS-018B completes the real public Render URL verification.

- Public frontend: `https://proofstudio-web.onrender.com`
- Public backend: `https://proofstudio.onrender.com`
- Deployment target: Render.
- Backend type: Render Web Service.
- Frontend type: Render Static Site.
- Live URL smoke: passed.
- CORS preflight: passed for `https://proofstudio-web.onrender.com`.
- Safe public dry-run: passed with `run_live=false`, no provider selected, zero attempts, zero assets, and no B2/Genblaze manifest write.

Evidence:

- `../ps-018b-render-deployment-public-url-verification-proof.md`
- `../evidence/ps-018b/live-url-smoke-summary.json`
- `../evidence/ps-018b/live-url-smoke-transcript.json`
- `../evidence/ps-018b/safe-public-dry-run-semantic.json`
