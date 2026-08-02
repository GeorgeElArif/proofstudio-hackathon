# ProofStudio · Review Room (PS-015 Demo Seed Pack + One-Click Local Demo)

The judge-facing ProofStudio **Review Room** over the PS-012 FastAPI demo
contract. PS-014 wired up the first complete end-to-end product demo path:
create a campaign → safe dry-run by default → explicitly enable live mode →
**Create Live Proof Run** → inspect run evidence, attempts, assets (with an
honest image preview), manifest verification, and a Provenance Passport, with
the truth boundary always visible. PS-015 adds a deterministic demo seed pack
and a one-click local demo helper so the whole flow is repeatable from a single
command.

This is **not** a production app. It is a sharp local demo shell. It builds on
the PS-013 UI shell and the PS-013A local integration hardening.

## One-click local demo (PS-015)

PS-015 adds a deterministic seed pack and a safe one-click helper that seeds a
demo campaign, creates a safe dry-run (no provider, no B2, no fake media), and
prints the Review Room + API docs URLs. The default path never calls live
providers or B2.

```bash
# from repo root
source .venv/bin/activate
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"
python scripts/ps015_one_click_local_demo.py
```

Seed pack: `examples/ps015/demo-seed-pack.json`. The helper also supports
`--print-runbook`, `--check-ports`, `--serve`, and an explicit opt-in `--live`
flag (live mode is never the default). See
`docs/ps-015-demo-seed-pack-one-click-local-demo-proof.md` for the full
runbook.

## Submission pack

The judge-ready submission evidence pack (demo video script, recording runbook,
judge evidence pack, provider/model inventory, B2 + Genblaze usage, judging
criteria mapping, submission checklist) lives in
[`docs/submission/`](../../docs/submission/README.md). Public deployment is
pending; this Review Room is the local demo surface.

## Deployment prep

Production env template, CORS strategy, platform decision, and preflight
checklist live in [`docs/deployment/`](../../docs/deployment/README.md). PS-018
selects **Render** as the deployment target; see
[`docs/deployment/render.md`](../../docs/deployment/render.md) for the frontend
static-site setup. For a production frontend build, set
`VITE_PROOFSTUDIO_API_BASE_URL` to the public API host before running
`npm run build`. The public URL is pending until
[`scripts/ps018_live_url_smoke.py`](../../scripts/ps018_live_url_smoke.py)
passes in live URL mode.

## Frontend technology

Minimal **Vite + React + TypeScript** app, no extra UI framework.

## Local run commands (exact two-terminal runbook)

The local demo runs the FastAPI backend and the Vite frontend on two different
origins (`http://127.0.0.1:8000` and `http://127.0.0.1:5173`). The backend
explicitly allows the local frontend origins through CORS (see PS-013A), so the
browser can fetch the API without a cross-origin block.

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

> If the API Status card shows **backend not reachable**, the FastAPI backend in
> Terminal 1 is not running (or is on a different host/port). Start it first. If
> it is running but the browser still blocks the request, confirm the backend's
> CORS allow-list includes the origin you opened (the default includes
> `http://127.0.0.1:5173` and `http://localhost:5173`).

## Production build

```bash
cd apps/web
npm install
npm run build      # type-checks (tsc --noEmit) then builds static assets to dist/
npm run preview    # serve the built dist/ locally
```

## API base URL configuration

The UI resolves the backend base URL at runtime:

1. `VITE_PROOFSTUDIO_API_BASE_URL` env var (if set, non-empty).
2. Fallback: `http://127.0.0.1:8000`.

Set it when building/dev-serving, e.g.:

```bash
VITE_PROOFSTUDIO_API_BASE_URL="https://api.example.com" npm run build
# or create apps/web/.env.local with:
#   VITE_PROOFSTUDIO_API_BASE_URL=https://api.example.com
```

## Consumed endpoints (PS-012 contract)

All ten contract routes are consumed live — see `src/api.ts`:

- `GET  /health`
- `GET  /version`
- `POST /campaigns`
- `GET  /campaigns/{campaign_id}`
- `POST /runs`
- `GET  /runs/{run_id}`
- `GET  /runs/{run_id}/attempts`
- `GET  /runs/{run_id}/assets`
- `GET  /runs/{run_id}/manifest`
- `GET  /runs/{run_id}/passport`

## Required UI sections

1. Hero / positioning
2. API Status Card
3. Campaign Builder
4. Run Creator
5. Evidence Overview
6. Attempt Timeline
7. Assets Panel
8. Manifest Panel
9. Provenance Passport Panel
10. Truth Boundary Footer

## Default safe dry-run behavior

- `run_live` defaults to **false**.
- The primary action is **Create Safe Dry Run** — no provider calls, no B2,
  no Genblaze, no fake media.
- The dry-run state honestly shows no media, no assets, no manifest, and a
  passport that explains the no-media/no-manifest state.
- The **Create Live Proof Run** button is disabled until the user explicitly
  toggles Live mode on, and a clear warning is always shown:

  > Live mode may call external providers and B2.

## Explicit live run path (PS-014)

The live path is opt-in and explicit:

1. Create a campaign.
2. Toggle **Live mode** on (read the warning).
3. Click **Create Live Proof Run**.
4. While the request is pending, the action buttons are disabled (no accidental
   double-submit) and a "Live run in progress" banner is shown.
5. After the live run returns, the UI fetches, in parallel:
   - `GET /runs/{run_id}`
   - `GET /runs/{run_id}/attempts`
   - `GET /runs/{run_id}/assets`
   - `GET /runs/{run_id}/manifest`
   - `GET /runs/{run_id}/passport`
6. Evidence is shown honestly for `live_completed`, `live_failed`, and
   `live_blocked` outcomes. No media or manifest is ever fabricated.

## Asset preview behavior (PS-014)

When an asset's `media_type` is an image and a URL exists, the Assets panel
attempts to render a preview from the real asset URL. If the browser cannot
load the image, the preview falls back to **metadata only** — the UI never
substitutes a placeholder that could look like generated output. Asset
metadata (sha256, size_bytes, media_type, etc.) is always shown and remains the
source of truth.

## Data honesty

The UI never hard-codes successful proof evidence. It shows honest helper text
before a run exists and clearly distinguishes: **no run yet**, **dry-run no
media**, **live completed**, **live failed**, **live blocked**, **manifest
unavailable**, and **archive unavailable**. No fake media, no fake manifest
URIs, no fake archive URIs, no provider logos.

## Smoke / build verification

```bash
# from repo root
source .venv/bin/activate
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"
python scripts/ps014_live_demo_flow_review_room_smoke.py
```

Writes:

- `/tmp/proofstudio-ps-014/live-demo-flow-review-room-summary.json`
- `/tmp/proofstudio-ps-014/live-demo-flow-review-room-transcript.json`

Optional explicit live smoke (calls real providers/B2 — only when credentials
are configured):

```bash
PROOFSTUDIO_PS014_LIVE=1 python scripts/ps014_live_demo_flow_review_room_smoke.py
```

Default acceptance never requires live provider spend.

## Truth boundary

PS-014 proves ProofStudio has a local end-to-end Review Room demo path for safe
dry-runs and explicit live proof runs through the FastAPI API. It does **not**
prove production deployment, a public app URL, auth, persistence, background
job reliability, legal authenticity, C2PA authenticity, semantic truth, or
human authorship.
