# PS-014 Live Demo Flow / End-to-End Review Room Path — Proof

## Status

**Accepted (default safe smoke).** PS-014 connects the first complete
end-to-end product demo path through the Review Room UI: create campaign →
safe dry-run by default → explicitly enable live mode → Create Live Proof Run
→ fetch and display run evidence, attempts, assets, manifest, and the
Provenance Passport, with the truth boundary always visible.

The default smoke proves the safe path without calling any live provider and
without calling B2. The optional explicit live path is exercised only when
`PROOFSTUDIO_PS014_LIVE=1` is set and provider/B2 credentials are configured.

This slice builds on PS-012 (FastAPI demo contract), PS-013 (Review Room UI
shell), and PS-013A (local integration hardening / CORS).

## Frontend path

- App: `apps/web/`
- UI entry: `apps/web/src/App.tsx`
- API client: `apps/web/src/api.ts`
- Styles: `apps/web/src/styles.css`
- Technology: Vite + React + TypeScript

## Local run commands (exact two-terminal runbook)

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

### Browser

- Review Room UI: http://127.0.0.1:5173
- Backend health: http://127.0.0.1:8000/health
- Backend docs: http://127.0.0.1:8000/docs

### Demo sequence

1. Open http://127.0.0.1:5173; confirm the API Status card is **online**.
2. Create a campaign in the Campaign Builder.
3. Click **Create Safe Dry Run**; inspect the honest no-media / no-manifest
   state across every panel.
4. Intentionally toggle **Live mode** on; read the warning.
5. Click **Create Live Proof Run**; wait for the in-progress banner to clear.
6. Inspect Evidence Overview, Attempt Timeline, Assets (preview when an image
   with a reachable URL), Manifest, Provenance Passport, and the Truth Boundary.

## Safe dry-run path (default)

- `run_live` defaults to **false** (`useState(false)`).
- The primary action is **Create Safe Dry Run**. It sends `run_live=false`,
  which the backend resolves to status `dry_run_created`.
- No live provider is called. No B2 call is made. No Genblaze manifest is
  written. No media is generated.
- The UI honestly shows: empty attempts ledger, empty assets, manifest
  `ready=false`, and a passport that reports `generated_media_present=false`
  and an unavailable archive.

## Explicit live path (opt-in)

- The **Create Live Proof Run** button is disabled until the user explicitly
  toggles Live mode on.
- A clear warning is always shown next to the toggle and again above the
  actions:

  > Live mode may call external providers and B2.

- While the live request is pending, the action buttons are disabled (no
  accidental double-submit) and an informational "Live run in progress" banner
  is shown.
- After the live run returns, the UI fetches, in parallel:
  - `GET /runs/{run_id}`
  - `GET /runs/{run_id}/attempts`
  - `GET /runs/{run_id}/assets`
  - `GET /runs/{run_id}/manifest`
  - `GET /runs/{run_id}/passport`
- Evidence is rendered honestly for `live_completed`, `live_failed`, and
  `live_blocked`. No media or manifest is ever fabricated.

## Live mode warning

The exact string **"Live mode may call external providers and B2."** appears in
`App.tsx` both beside the Live mode toggle and when live mode is active, and is
restated in the Trust Boundary footer. The default action is always a safe
dry-run.

## Evidence panels

The Review Room renders every required panel, each populated live from the API:

- **Evidence Overview** (`GET /runs/{run_id}`): run_id, status, selected
  provider, selected model, fallback used, attempt count, asset count,
  manifest uri, manifest hash.
- **Attempt Timeline** (`GET /runs/{run_id}/attempts`): attempt index,
  provider, model, status, normalized status, latency, retryable, fallback
  allowed, sanitized error message.
- **Assets** (`GET /runs/{run_id}/assets`): url, media type, sha256, size
  bytes, metadata, plus an honest image preview (see below).
- **Manifest** (`GET /runs/{run_id}/manifest`): manifest uri, manifest hash,
  stored manifest verify, transfer failures, stored transfer failures.
- **Provenance Passport** (`GET /runs/{run_id}/passport`): passport identity,
  run summary, generation summary, manifest verification, archive and
  rehydration, trust boundary, reviewer next actions.

## Asset preview behavior

When an asset's `media_type` is an image and a URL exists, the Assets panel
attempts to render a preview from the **real asset URL** (the `<img src>` is
the actual asset URL). The preview only becomes visible once the image
successfully loads (`onLoad`). If the browser cannot load the image (broken
URL, CORS on the media host, etc.), `onError` hides the preview and the panel
falls back to **metadata only**, with an explicit notice. The UI never
substitutes a placeholder that could look like generated output, and never
claims a preview before the image actually loads. Asset metadata (sha256,
size_bytes, media_type) is always shown and remains the source of truth.

## Manifest proof behavior

For dry-runs and any run without a stored manifest, the Manifest panel shows
**"Manifest unavailable."** with the backend's `not_ready_reason` — it never
fakes a manifest URI or a successful verification. For completed live runs, it
shows the real manifest URI, manifest hash, in-memory verify, and the stored
manifest verify flag (sourced directly from the Genblaze store-and-verify
result).

## Passport proof behavior

The Provenance Passport is assembled server-side from the real run, attempts,
assets, and manifest readbacks. For dry-runs it honestly reports
`generated_media_present=false`, an unavailable archive, the trust boundary,
and reviewer next actions. For completed live runs it reports generated media
present, the manifest verification result, and the trust boundary. The trust
boundary is always visible, both inside the passport and as a footer.

## Default no-provider / no-B2 proof

The default PS-014 smoke wires sentinel functions over
`services.execute_live_run`, `archive.store_run_archive_with_genblaze`, and
`archive.read_archive_from_b2` before exercising the default HTTP contract
(health → version → campaign → safe dry-run → readbacks → passport). After the
run it asserts both call counters are exactly zero. This proves the default
path does not call a live provider and does not call B2.

## Optional live proof

When `PROOFSTUDIO_PS014_LIVE=1` is set, the smoke additionally creates a real
live run (`POST /runs` with `run_live=true`) against the configured provider /
B2 chain (no sentinels in this path). It asserts the run status is
`live_completed`, `live_failed`, or `live_blocked`. If completed, it verifies
`selected_provider`, `selected_model`, attempts, assets, manifest, passport,
and `stored_manifest_verify=true`. If failed/blocked, it verifies no fake media
and no fake manifest with a clear failure state. Default acceptance never
requires live provider spend.

## Truth boundary

PS-014 proves ProofStudio has a local end-to-end Review Room demo path for safe
dry-runs and explicit live proof runs through the FastAPI API.

It does **not** prove:

- public deployment
- production availability
- authentication
- production persistence
- background job reliability
- legal authenticity
- C2PA authenticity
- semantic truth
- human authorship

## Limitations

- The frontend is a local demo shell, not a production app.
- Live runs require configured provider and B2 credentials and may incur
  provider spend; the default smoke never exercises them.
- State is in-memory (no production persistence across backend restarts).
- Asset previews depend on the media host being reachable / CORS-permissive
  from the browser; otherwise metadata-only is shown.
- The smoke validates the frontend source and the backend HTTP contract; it
  does not drive a real browser.

## Backend changes

None. PS-014 required no backend changes. The PS-012 contract (health, version,
campaigns, runs, attempts, assets, manifest, passport) and the PS-013A CORS
hardening are preserved unchanged.

## Next milestone recommendation

A hosted/public deployment slice (e.g. PS-015) to expose the Review Room at a
stable URL for judges, plus optional persistence (run archive rehydrate is
already proven at PS-010) so completed live runs survive backend restarts.
