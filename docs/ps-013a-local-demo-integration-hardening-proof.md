# PS-013A Local Demo Integration Hardening — Proof

## status

Accepted (default smoke green). PS-013A makes the local browser demo reliable:
the Vite frontend at `http://127.0.0.1:5173` can fetch the FastAPI backend at
`http://127.0.0.1:8000` without a cross-origin block, and the API Status card
no longer collapses into a generic network error.

## root cause

PS-013 shipped a Vite + React + TypeScript frontend (`apps/web`) on origin
`http://127.0.0.1:5173` that calls the FastAPI backend on origin
`http://127.0.0.1:8000`. The backend (`proofstudio.api.app:app`) had **no CORS
middleware**, so the browser blocked every cross-origin `fetch()` to
`/version` (and the rest of the contract). The frontend surfaced this as an
opaque "Network error reaching …" message, which looked like the backend was
broken even though `/health` and `/docs` worked fine when opened directly.

Two problems, both fixed in this slice:

1. **Backend**: no `CORSMiddleware` → browser CORS preflight/actual failed.
2. **Frontend**: one combined error state for `/health` + `/version`, with no
   hint that the cause was "backend not running" vs "CORS block".

## CORS behavior added

`src/proofstudio/api/app.py` now registers FastAPI's `CORSMiddleware` inside
`_build_app()` (so both the `uvicorn …:app` server and `TestClient` see it):

```python
application.add_middleware(
    CORSMiddleware,
    allow_origins=list(LOCAL_DEMO_CORS_ORIGINS),  # explicit list, no wildcard
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)
```

`allow_credentials=False` deliberately. The slice never uses unsafe wildcard
credentials (`allow_origins=["*"]` + `allow_credentials=True` is forbidden).
`CORSMiddleware` ships with Starlette (already pulled in by the `fastapi`
dependency in `apps/api/requirements.txt`), so no new dependency was added.

## allowed local origins

`LOCAL_DEMO_CORS_ORIGINS` (defined in `src/proofstudio/api/app.py`):

- `http://127.0.0.1:5173` — Vite dev server (required)
- `http://localhost:5173` — Vite dev server via localhost (required)
- `http://127.0.0.1:4173` — Vite preview server (useful)
- `http://localhost:4173` — Vite preview server via localhost (useful)

Disallowed origins are not echoed an `Access-Control-Allow-Origin` header
(verified by the smoke).

## endpoints tested

The PS-013A smoke (FastAPI `TestClient`) exercises:

- `OPTIONS /version` preflight — `Origin: http://127.0.0.1:5173` + `localhost:5173`
- `GET /version` with `Origin` header
- `GET /health`
- `POST /campaigns`
- `POST /runs` (default safe dry-run)
- `GET /runs/{run_id}/assets` (empty for dry-run)
- `GET /runs/{run_id}/passport` (no generated media for dry-run)

Each CORS preflight returns `200` with the origin reflected in
`Access-Control-Allow-Origin` and `GET` present in
`Access-Control-Allow-Methods`. Each actual GET carries the echoed origin.

## default safe dry-run behavior

The default `POST /runs` body is `{ run_live: false }`. The service layer keeps
the unchanged dry-run contract from PS-008/PS-012: status
`dry_run_created`, no provider selected, empty attempt ledger, empty assets,
manifest not-ready. No backend service behavior was changed in this slice.

## no-provider-call proof

The smoke monkeypatches `services.execute_live_run`,
`archive.store_run_archive_with_genblaze`, and `archive.read_archive_from_b2`
with sentinels that raise if called. After the full default contract
(health → version → campaign → dry-run → assets → passport), the counters are
asserted to be exactly `0`:

- `provider_calls == 0` → `default_no_live_provider_call: true`
- `b2_calls == 0` → `default_no_b2_call: true`

## no-B2-call proof

Same sentinel wiring as above. The dry-run path never enters
`_execute_live_and_apply` (only reached when `run_live=true` and
`dry_run=false`), so `store_run_archive_with_genblaze` /
`read_archive_from_b2` are never reached.

## no fake media

For the dry-run: `GET /runs/{id}/assets` returns `asset_count: 0`, and the
passport's `generation_summary.generated_media_present` is `false`. The UI
never substitutes placeholder media for real output (unchanged from PS-013).
Smoke field: `no_fake_media: true`.

## frontend API status behavior

`apps/web/src/api.ts` adds `describeApiError(err)`:

- `ApiError` with `status === 0` (a `fetch()` that never reached the backend)
  → "Backend not reachable at <base URL>. Start the FastAPI backend …. If it
  is already running, this is likely a CORS block: the backend must allow this
  origin."
- non-zero status → `<message> (HTTP <status>)`.
- Never fakes success; never hides the cause.

`apps/web/src/App.tsx` API Status card (`#api-status`) now:

- Always shows the resolved **API base URL** (a labeled code block).
- Fetches `/health` and `/version` **separately**, each with its own result
  block and its own error state, so a partial failure no longer hides the
  piece that worked.
- Shows a distinct **backend not reachable** pill when the error is a
  status-0/CORS-style failure, vs a generic **error** pill for HTTP errors.

`apps/web/src/styles.css` adds `.baseurl`, `.status-block`,
`.status-block-head`, and `.status-block-title` for the split layout.

## exact two-terminal local runbook

### Terminal 1 — FastAPI backend

```bash
cd /home/proofstudio-work/proofstudio
source .venv/bin/activate
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"
uvicorn proofstudio.api.app:app --reload --host 127.0.0.1 --port 8000
```

### Terminal 2 — Review Room frontend

```bash
cd /home/proofstudio-work/proofstudio/apps/web
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

### Open

- Review Room UI: http://127.0.0.1:5173
- Backend health: http://127.0.0.1:8000/health
- Backend docs (Swagger): http://127.0.0.1:8000/docs

This runbook is documented verbatim in `apps/web/README.md`.

## smoke / verification

```bash
cd /home/proofstudio-work/proofstudio
source .venv/bin/activate
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"
python scripts/ps013a_local_demo_integration_hardening_smoke.py
```

Writes:

- `/tmp/proofstudio-ps-013a/local-demo-integration-hardening-summary.json`
- `/tmp/proofstudio-ps-013a/local-demo-integration-hardening-transcript.json`

Frontend build:

```bash
cd apps/web
npm run build      # tsc --noEmit && vite build
```

## limitations

- This is a **local demo only** CORS policy. It is not a production CORS
  policy and must not be shipped as-is to a public origin.
- `allow_credentials=False` means cookie/credentialed cross-origin flows are
  not supported (intentional; the demo uses no credentials).
- Origins are hardcoded to localhost dev/preview ports. Any other origin
  (LAN IP, tunnel, deployed host) is intentionally not allowed.
- CORS is necessary but not sufficient for a real deployment — auth, HTTPS,
  rate limiting, and persistence are out of scope (PS-013A non-goals).
- The CORS check uses FastAPI's `TestClient`, which simulates the browser's
  preflight/actual flow at the ASGI layer; it does not launch a real browser.

## truth boundary

PS-013A proves the local browser demo can connect to the FastAPI backend
through safe local CORS settings and execute the default dry-run demo path. It
does **not** prove public deployment, production CORS policy, authentication,
production persistence, background job reliability, legal authenticity, C2PA
authenticity, semantic truth, or human authorship.

## next milestone recommendation

With the local demo flow reliable, the next milestone can focus on
**end-to-end live-run evidence in the browser**: wire the existing PS-009 live
bridge through the UI (explicit Live Run opt-in with the existing warning),
render real attempts / assets / manifest verification / passport for a
completed live run, and optionally add PS-010 archive/rehydrate evidence to
the passport panel. This keeps the truth boundary honest while making the
full product story demoable in one screen.
