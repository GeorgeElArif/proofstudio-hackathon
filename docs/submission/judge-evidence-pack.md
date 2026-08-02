# ProofStudio — Judge Evidence Pack

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


The one-stop summary for judges and reviewers. Everything here is grounded in the
current local product and the prior proof slices (PS-001A through PS-015). Where
something is not yet done, it is marked **pending**.

## Product name

**ProofStudio** — a provenance-aware AI media operations app.

## One-sentence pitch

ProofStudio turns AI media generation from a black-box output into a reviewable,
durable, evidence-backed workflow.

## Audience

- **Creator teams** producing AI assets at volume.
- **Marketing teams** reviewing campaign media across channels.
- **Agencies** managing multiple clients and providers.
- **Production teams** reviewing AI-generated assets before release.

## Pain point

Creative and marketing teams generate AI media across multiple providers, but they
lose the evidence trail: the prompt, the model, the retries, the storage, the
manifest, and what can be trusted. Every run is a black box with no reviewable,
durable, evidence-backed workflow behind it.

## Workflow

The MVP golden path:

```
Campaign brief
  → Genblaze pipeline orchestration
  → provider-routed generation (primary + fallback)
  → generated media stored in Backblaze B2
  → Genblaze manifest write + byte-level verification
  → run archived to B2 and rehydratable from B2
  → Provenance Passport (reviewable evidence)
  → review / export
```

In the Review Room UI, the operator flow is: create a campaign → **safe dry-run
by default** → explicitly enable Live mode → **Create Live Proof Run** → inspect
evidence, attempts, assets, manifest verification, and the Provenance Passport,
with the truth boundary always visible.

## Completed slices

| Slice | What it proved |
|-------|----------------|
| PS-001A | Local asset + Genblaze manifest + Backblaze B2 round-trip and byte-level verification. |
| PS-001B | Live GMI generation path implemented; currently billing-blocked (insufficient credits). |
| PS-002 | Gemini campaign intelligence: brief → structured strategy/prompt packs → B2 + manifest verification. |
| PS-003 | Gemini/Imagen visual generation path implemented; currently quota/paid-plan blocked. |
| PS-004 | Cloudflare Workers AI image provider → B2 → Genblaze manifest verification. |
| PS-005 | Pollinations no-key image fallback provider → B2 → Genblaze manifest verification. |
| PS-006 | ProviderRouter core: deterministic routing, fallback, full 20-field attempt ledger, no fake media. |
| PS-007 | Live ProviderRouter chain: real Cloudflare primary + Pollinations fallback, B2 + manifest verification. |
| PS-008 | Backend API skeleton: typed FastAPI models, in-memory store, service layer, dry-run default. |
| PS-009 | API → live run bridge: `create_run(run_live=true)` drives the live chain, B2, manifest verification. |
| PS-010 | Run archive + rehydrate from B2 object content, without rerunning any provider. |
| PS-011 | Review Room / Provenance Passport API, assembled from rehydrated stored evidence. |
| PS-012 | FastAPI server mode + full 10-route demo API contract over HTTP. |
| PS-013 | Review Room frontend shell (Vite + React + TypeScript), all 10 sections, safe dry-run default. |
| PS-013A | Local demo integration hardening: CORS allow-list, split API status states. |
| PS-014 | End-to-end Review Room live demo flow: explicit live proof run + honest evidence rendering. |
| PS-015 | Deterministic demo seed pack + safe one-click local demo helper. |
| PS-016 | Submission evidence pack + judge-facing submission docs. |
| PS-017 | Deployment prep: production env template, CORS/env hardening, platform decision, preflight checklist. |
| PS-018 | Public deployment target selection (**Render**) + Render blueprint/runbook + gated live URL smoke. |
| PS-018B | Verified public Render frontend/backend URLs + CORS + safe public dry-run evidence. |

## Architecture

- **Providers:** `src/proofstudio/providers/` — `types.py` (normalized statuses +
  20-field `ProviderAttempt`), `router.py` (`ProviderRouter`), live adapters
  (`live_cloudflare.py`, `live_pollinations.py`), and deterministic fakes.
- **Provenance:** `src/proofstudio/provenance/genblaze_store.py` — reusable
  `GenblazeStore` / `AssetSpec` helpers wrapping the proven B2 + Genblaze
  ingest / write / read-manifest / verify pattern.
- **API:** `src/proofstudio/api/` — `models.py`, `store.py` (in-memory store),
  `services.py` (business logic), `app.py` (FastAPI app + CORS),
  `live_bridge.py` (live run execution), `archive.py` (archive/rehydrate),
  `passport.py` (Provenance Passport).
- **Frontend:** `apps/web/` — Vite + React + TypeScript Review Room consuming
  all 10 contract endpoints (`src/api.ts`, `src/App.tsx`).
- **Proof scripts:** `scripts/ps0xx_*.py` — one smoke per slice; live paths are
  explicit opt-in, defaults are safe.

## API endpoints (PS-012 contract)

All ten routes are implemented and exercisable over HTTP via
`uvicorn proofstudio.api.app:app`:

| Method | Path |
|--------|------|
| GET | `/health` |
| GET | `/version` |
| POST | `/campaigns` |
| GET | `/campaigns/{campaign_id}` |
| POST | `/runs` |
| GET | `/runs/{run_id}` |
| GET | `/runs/{run_id}/attempts` |
| GET | `/runs/{run_id}/assets` |
| GET | `/runs/{run_id}/manifest` |
| GET | `/runs/{run_id}/passport` |

`POST /runs` defaults to a **safe dry-run** (`run_live=false`). Live execution is
opt-in via `run_live=true` (and `dry_run=false`).

## Frontend path

`apps/web/` — the Review Room. Local dev: `http://127.0.0.1:5173`. Resolves the
API base URL from `VITE_PROOFSTUDIO_API_BASE_URL` (fallback
`http://127.0.0.1:8000`). See `apps/web/README.md`.

## Demo commands

Safe one-click demo (no provider, no B2):

```bash
cd /home/proofstudio-work/proofstudio
source .venv/bin/activate
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"
python scripts/ps015_one_click_local_demo.py
```

Two-terminal stack and browser URLs are in
[`recording-runbook.md`](./recording-runbook.md).

## Proof scripts

| Slice | Script |
|-------|--------|
| PS-001A | `scripts/ps001a_b2_manifest_smoke.py` |
| PS-001B | `scripts/ps001b_gmi_b2_generation_smoke.py` |
| PS-002 | `scripts/ps002_gemini_campaign_intelligence.py` |
| PS-003 | `scripts/ps003_gemini_visual_asset_proof.py` |
| PS-004 | `scripts/ps004_provider_router_cloudflare_smoke.py` |
| PS-005 | `scripts/ps005_pollinations_fallback_smoke.py` |
| PS-006 | `scripts/ps006_provider_router_core_smoke.py` |
| PS-007 | `scripts/ps007_live_provider_router_chain_smoke.py` |
| PS-008 | `scripts/ps008_backend_api_smoke.py` |
| PS-009 | `scripts/ps009_api_live_run_bridge_smoke.py` |
| PS-010 | `scripts/ps010_run_archive_rehydrate_b2_smoke.py` |
| PS-011 | `scripts/ps011_provenance_passport_api_smoke.py` |
| PS-012 | `scripts/ps012_fastapi_server_demo_contract_smoke.py` |
| PS-013 | `scripts/ps013_demo_ui_review_room_smoke.py` |
| PS-013A | `scripts/ps013a_local_demo_integration_hardening_smoke.py` |
| PS-014 | `scripts/ps014_live_demo_flow_review_room_smoke.py` |
| PS-015 | `scripts/ps015_demo_seed_pack_one_click_smoke.py` |
| PS-016 | `scripts/ps016_submission_evidence_pack_smoke.py` |
| PS-017 | `scripts/ps017_deployment_prep_smoke.py` |
| PS-018 | `scripts/ps018_live_url_smoke.py` |

## Smoke summaries

Each proof slice writes a summary + transcript to `/tmp/proofstudio-ps-0xx/`.
Key results that back this pack (recorded in their proof docs):

- **PS-004 / PS-005 / PS-007 / PS-009 / PS-010 / PS-011:** live Cloudflare
  Workers AI run completed, generated image stored in B2, Genblaze manifest
  written and byte-level verified (`stored_manifest_verify: true`,
  `transfer_failures: []`), full 20-field attempt ledger preserved.
- **PS-010:** run archived as a B2/Genblaze asset and rehydrated from B2 object
  content into a fresh store without rerunning any provider.
- **PS-015:** one-click helper default path proves `default_no_live_provider_call:
  true` and `default_no_b2_call: true` via sentinels.

The concrete manifest URIs, manifest hashes, and asset SHA-256 values are
recorded in the respective proof docs under `docs/` (e.g.
`docs/ps-007-live-provider-router-chain-proof.md`). They are referenced, not
re-invented, by this pack.

## B2 / Genblaze evidence

See [`b2-genblaze-usage.md`](./b2-genblaze-usage.md) for the full breakdown.
Backblaze B2 stores generated assets, prompt packets, attempt ledgers, provider
notes, run archives, and manifests. The Genblaze pipeline ingests assets and
writes/verifies manifests, and manifest verification is used as provenance
evidence. The archive/rehydrate path restores evidence from B2. This is backed
by PS-001A, PS-002, PS-004, PS-005, PS-007, PS-009, PS-010, and PS-011.

## Provider / model evidence

See [`provider-model-inventory.md`](./provider-model-inventory.md). Live-proven
or implemented providers: **Cloudflare Workers AI** (image primary), **Pollinations**
(image fallback), **Gemini campaign intelligence** (strategy layer). Blocked:
GMI Cloud (credits), Gemini/Imagen visual (quota/paid plan), Luma (card
required). Optional later providers are **not** implemented.

## Truth boundary

ProofStudio proves **workflow evidence**: provider attempts, asset hashes,
storage records, manifest metadata, archive/rehydration, and passport assembly.
It does **not** prove semantic truth, legal authenticity, C2PA authenticity,
human authorship, public deployment, production availability, authentication,
production persistence, or background job reliability.

## Limitations

  target and ships a Render blueprint (`render.yaml`) + runbook
  (`docs/deployment/render.md`) + a gated live URL smoke
  yet**: live URL smoke status is `skipped_missing_urls` and
  supplied and the explicit live URL smoke passes. The demo is local via the
  one-click helper and the two-terminal stack.
- The backend store is **in-memory** (process-local); durability lives in the B2
  run archive, not a production database.
- **No authentication / authorization** layer.
- The default demo path is a **safe dry-run**; live provider runs require
  explicit opt-in and may fail/block based on credits/quotas.
- Some visual providers are **blocked** (GMI Cloud credits, Gemini/Imagen quota).
- The smoke scripts validate source/build/contract; they do not drive a real
  browser.
- No C2PA signing, no legal/semantic authenticity, no human-authorship
  verification is claimed or implemented.

## Next work

- Re-run the Render live URL smoke before final Devpost submission against the
  real public API + web URLs; only then record the public URL in
  `docs/submission/submission-checklist.md`.
- Production persistence (e.g. Postgres/SQLite) with the B2 archive as the system
  of record.
- Authentication.
- Final demo video recording; public URL is verified by PS-018B.
- Recover-by-run-id / rehydrate-from-manifest-URI.

## PS-018B public deployment evidence

PS-018B adds verified public Render deployment evidence.

- Public app URL: `https://proofstudio-web.onrender.com`
- Public API URL: `https://proofstudio.onrender.com`
- Live URL smoke: passed.
- API health/version: verified.
- Frontend load: verified.
- CORS preflight: verified.
- Safe public dry-run: verified with no provider call and no B2/Genblaze write.

Evidence files:

- `docs/ps-018b-render-deployment-public-url-verification-proof.md`
- `docs/evidence/ps-018b/live-url-smoke-summary.json`
- `docs/evidence/ps-018b/live-url-smoke-transcript.json`
- `docs/evidence/ps-018b/safe-public-dry-run-semantic.json`

<!-- PS-019_JUDGE_EVIDENCE_START -->
## PS-019 public passport evidence

PS-019 adds the public passport URL pattern:

`https://proofstudio-web.onrender.com/passport/<run_id>`

Local acceptance evidence:

- public route implementation: `apps/web/src/PublicPassportPage.tsx`
- static deep-link rewrite: `render.yaml` (`/passport/*` → `/index.html`)
- proof doc: `docs/ps-019-public-passport-proof-score-proof.md`
- local smoke summary: `docs/evidence/ps-019/local-passport-smoke-summary.json`
- live public smoke summary: `docs/evidence/ps-019/live-public-passport-smoke-summary.json`

Truth boundary: PS-019 proves the public passport UI and Proof Score behavior. It does not prove production persistence, legal authenticity, C2PA authenticity, semantic truth, human authorship, authentication, or paid production reliability.
<!-- PS-019_JUDGE_EVIDENCE_END -->
