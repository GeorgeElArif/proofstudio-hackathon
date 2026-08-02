# PS-013 Demo UI Shell / Review Room Frontend — Proof

## Status

**Accepted.** ProofStudio now has its first visible demo UI — a judge-facing
operator **Review Room** shell under `apps/web/`. It consumes the full PS-012
FastAPI demo contract live, makes the product understandable in under 30
seconds, defaults to a safe dry-run, and never hard-codes successful proof
evidence.

## Frontend Path

`apps/web/`

## Frontend Technology

Minimal **Vite + React + TypeScript** app (no UI framework dependency). Chosen
because no frontend previously existed (`apps/web/` only held `.gitkeep`) and
Node 24 / npm 11 are available in the environment. Detected frontend type:
`vite_react_ts`.

Files:

| File | Purpose |
|------|---------|
| `apps/web/package.json` | Dependencies + `dev` / `build` / `preview` / `typecheck` scripts |
| `apps/web/index.html` | Vite HTML entry |
| `apps/web/vite.config.ts` | Vite + `@vitejs/plugin-react` config |
| `apps/web/tsconfig.json` | Strict TS config (`noEmit`, JSX react-jsx) |
| `apps/web/src/vite-env.d.ts` | Types for `VITE_PROOFSTUDIO_API_BASE_URL` |
| `apps/web/src/main.tsx` | React root bootstrap |
| `apps/web/src/App.tsx` | Review Room shell + all 10 sections |
| `apps/web/src/api.ts` | Typed client for all 10 PS-012 endpoints |
| `apps/web/src/styles.css` | Dark operator-review-room theme |
| `apps/web/README.md` | Local run + config docs |

## Local Run Commands

```bash
# 1. Backend (PS-012) — serves http://127.0.0.1:8000
source .venv/bin/activate
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"
uvicorn proofstudio.api.app:app --reload

# 2. Frontend — serves http://127.0.0.1:5173
cd apps/web
npm install
npm run dev
```

Production build:

```bash
cd apps/web
npm install
npm run build     # tsc --noEmit && vite build  ->  apps/web/dist/
npm run preview
```

## API Base URL Configuration

Resolved at runtime in `apps/web/src/api.ts`:

1. `VITE_PROOFSTUDIO_API_BASE_URL` env var (non-empty).
2. Fallback: `http://127.0.0.1:8000`.

```bash
VITE_PROOFSTUDIO_API_BASE_URL="https://api.example.com" npm run build
# or apps/web/.env.local:  VITE_PROOFSTUDIO_API_BASE_URL=https://api.example.com
```

## Backend Run Command

`uvicorn proofstudio.api.app:app` (PS-012). Interactive docs at `/docs`.

## Required UI Sections (all present)

1. **Hero / positioning** — "ProofStudio turns AI media generation into verifiable production evidence."
2. **API Status Card** — `GET /health` + `GET /version` (backend health, mode, version, capabilities pills).
3. **Campaign Builder** — `POST /campaigns` / `GET /campaigns/{id}` (name, brief, audience, platform, objective).
4. **Run Creator** — `POST /runs` (prompt, budget mode, live toggle with warning).
5. **Evidence Overview** — `GET /runs/{id}` (run_id, status, provider/model, fallback, counts, manifest URI/hash).
6. **Attempt Timeline** — `GET /runs/{id}/attempts` (index, provider, model, status, latency, retryable, fallback, sanitized error).
7. **Assets Panel** — `GET /runs/{id}/assets` (url, media type, sha256, size, metadata).
8. **Manifest Panel** — `GET /runs/{id}/manifest` (URI, hash, in-memory/stored verify, transfer failures).
9. **Provenance Passport Panel** — `GET /runs/{id}/passport` (source, run/generation summary, timeline, manifest verification, archive/rehydration, reviewer actions).
10. **Truth Boundary Footer** — always-visible non-claims.

## Default Safe Dry-Run Behavior

- `run_live` defaults to **false** (`const [runLive, setRunLive] = useState(false)`).
- The primary action is **Create Safe Dry Run** — no provider calls, no B2, no
  Genblaze, no fabricated media.
- **Create Live Run** is disabled until the user explicitly enables Live mode.

## Live Mode Warning

Live mode requires an explicit user action (a checkbox) and carries the exact
warning everywhere it appears:

> Live mode may call external providers and B2.

The same warning is restated in the Truth Boundary footer.

## Evidence Panels (data honesty)

The UI consumes real API responses only and distinguishes these states
clearly:

- **no run yet** — honest helper text before any run exists.
- **dry-run · no media** — empty attempts/assets, manifest `unavailable`.
- **live completed** — green pill, real asset/metadata when present.
- **live failed** — red pill + sanitized error.
- **live blocked** — amber pill + blocked reason.
- **manifest unavailable** — shown honestly, never faked.
- **archive unavailable** — passport `archive_and_rehydration.status` surfaced
  as an amber pill with the reason.

No fake media, no fake manifest URIs, no fake archive URIs, no provider logos.
Every raw payload is available behind a JSON expander for review.

## Provenance Passport Panel

Renders `GET /runs/{id}/passport` as a judge-friendly summary: passport source,
schema, media-present pill, archive availability, one-sentence review summary,
risk-flag pills, and reviewer next actions. The trust-boundary claims /
non-claims and the full raw passport are exposed in JSON expanders.

## Truth Boundary

ProofStudio verifies workflow evidence, asset hashes, provider attempts,
storage records, and manifest metadata when present. It does **not** prove
semantic truth, legal authenticity, C2PA authenticity, human authorship, or
production security. PS-013 proves ProofStudio has a local demo UI shell for
reviewing campaign/run evidence through the FastAPI API; it does not prove
production deployment, a public app URL, auth, persistence, background-job
reliability, legal authenticity, C2PA authenticity, semantic truth, or human
authorship.

## Smoke / Build Result

```bash
python scripts/ps013_demo_ui_review_room_smoke.py
```

- `ok`: **true**
- `frontend_type`: `vite_react_ts`
- `build_checked`: true · `build_status`: **passed** (`tsc --noEmit && vite build`)
- All required sections present; `default_run_live_safe` true;
  `live_mode_warning_present` true; `no_fake_media` / `no_fake_manifest` /
  `no_secrets` true; historical proof scripts untouched.
- Summary: `/tmp/proofstudio-ps-013/demo-ui-review-room-summary.json`
- Transcript: `/tmp/proofstudio-ps-013/demo-ui-review-room-transcript.json`

## Limitations

- Local demo shell only; no deployment, public URL, auth, or persistence.
- Single-file `App.tsx` shell — intentionally not a large app.
- Evidence only appears when the backend is running and reachable.
- The smoke verifies source/build; it does not drive a real browser.

## Next Milestone Recommendation

Deploy the Review Room + the PS-012 FastAPI app behind a public URL (the
hackathon "working app URL"), and/or add a real end-to-end dry-run smoke that
boots both servers and exercises the live HTTP path from the UI's own API
client. The service layer remains the single source of truth; this frontend is
now the demo surface.
