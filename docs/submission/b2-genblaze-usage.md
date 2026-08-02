# ProofStudio — Backblaze B2 + Genblaze Usage

How ProofStudio uses **Backblaze B2** for durable storage and the **Genblaze
pipeline** for manifest-based provenance. Every claim below is backed by an
existing proof script and proof doc. Concrete manifest URIs, manifest hashes,
and asset SHA-256 values live in the referenced proof docs — this pack points to
them rather than re-inventing them.

## What Backblaze B2 stores

When a **live proof path** is used, Backblaze B2 is the system of record for:

- **Generated assets** (e.g. the generated image bytes, byte-detected MIME).
- **Prompt packets** (the visual prompt sent to the provider, as JSON).
- **Provider attempt ledgers** (the full 20-field attempt records).
- **Provider notes** (Markdown notes per run).
- **Run archives** (a single durable JSON archive of an entire run).
- **Manifests** (the Genblaze manifest object for each run).

The B2 bucket used by the proof runs is `proofstudio-project-assets`
(region `eu-central-003`), as recorded in the proof docs. The bucket name and
region are not secrets.

## What the Genblaze pipeline does

The Genblaze pipeline ingests assets and **writes and verifies manifests**:

- `GenblazeStore.ingest()` / `write_run()` upload assets through the reusable
  provenance helper (`src/proofstudio/provenance/genblaze_store.py`).
- A **manifest** is written to B2 for each run.
- The manifest is **read back from B2** and **byte-level verified**
  (`stored_manifest_verify: true`, `transfer_failures: []`).
- **Manifest verification is the provenance evidence** that the recorded
  workflow integrity and byte-level asset integrity hold.

## Manifest verification as provenance evidence

A verified manifest proves:

- the recorded assets were stored;
- their hashes match what was uploaded;
- the transfer had zero failures.

It is surfaced to judges and reviewers in the **Provenance Passport** and the
Review Room Manifest panel.

## Archive / rehydrate path (restoring evidence from B2)

ProofStudio can archive a run into a durable artifact and **rehydrate it from B2
object content** into a fresh in-memory store — **without rerunning any
provider** and without fabricating media or a manifest:

- `build_run_archive` → `store_run_archive_with_genblaze` (archive stored as a
  real B2/Genblaze asset and verified).
- `read_archive_from_b2` → `rehydrate_run_from_archive` (archive bytes read back
  from B2 and reconstructed).
- Rehydration is proven to make **zero provider calls** and write **zero new
  media files** (sentinel-guarded in PS-010).

## Truth boundary

B2 + Genblaze prove **workflow evidence and byte-level asset integrity only**.
They do **not** prove semantic truth, legal authenticity, C2PA authenticity, or
human authorship. A verified manifest proves the recorded workflow happened and
the bytes are intact — not that an image means what the prompt asked for.

## Backing proof slices

Each claim above maps to a completed proof slice. These are the source-of-truth
references (proof docs under `docs/`):

### PS-001A — Local asset + manifest + B2 round-trip

Proves the foundational pattern: a local generated asset → Genblaze
`Pipeline.ingest()` → Backblaze B2 `ObjectStorageSink` → manifest stored in B2 →
`manifest.verify()` PASS → stored manifest read back from B2 and verified → zero
asset transfer failures. No live AI generation required.

- Script: `scripts/ps001a_b2_manifest_smoke.py`
- Doc: `docs/ps-001-local-setup.md`

### PS-002 — Gemini campaign intelligence → B2 + manifest

Proves campaign brief → structured Gemini strategy/prompt packs → JSON + markdown
uploaded to B2 → Genblaze manifest → stored manifest verification → zero transfer
failures.

- Script: `scripts/ps002_gemini_campaign_intelligence.py`
- Doc: `docs/ps-002-gemini-campaign-intelligence.md`

### PS-004 — Cloudflare Workers AI → B2 → manifest verification

Proves the first working visual provider path: real Cloudflare image bytes,
byte-detected MIME, image + prompt packet + attempt ledger + provider note stored
in B2, manifest written/read-back/verified.

- Script: `scripts/ps004_provider_router_cloudflare_smoke.py`
- Doc: `docs/ps-004-provider-router-cloudflare-proof.md`

### PS-005 — Pollinations fallback → B2 → manifest verification

Proves a no-key fallback visual provider preserves campaign continuity through
the same B2 + Genblaze provenance pipeline.

- Script: `scripts/ps005_pollinations_fallback_smoke.py`
- Doc: `docs/ps-005-pollinations-fallback-proof.md`

### PS-007 — Live ProviderRouter chain → B2 → manifest verification

Proves the live router: real Cloudflare primary + Pollinations fallback adapters,
reusable `ProviderRouter`, full 20-field attempt ledger, generated asset stored
in B2, manifest written/read-back/byte-level verified.

- Script: `scripts/ps007_live_provider_router_chain_smoke.py`
- Doc: `docs/ps-007-live-provider-router-chain-proof.md`

### PS-009 — API live run bridge → B2 → manifest verification

Proves a product-facing `create_run(run_live=true)` drives the live provider
chain, stores artifacts in B2, writes/verifies a Genblaze manifest, and feeds the
real evidence back into the API readbacks.

- Script: `scripts/ps009_api_live_run_bridge_smoke.py`
- Doc: `docs/ps-009-api-live-run-bridge-proof.md`

### PS-010 — Run archive + rehydrate from B2

Proves durability: a live run archived into a durable JSON artifact, stored as a
real B2/Genblaze asset, rehydrated from **B2 object content** into a fresh store
without rerunning any provider, with no fake media and no fake manifest.

- Script: `scripts/ps010_run_archive_rehydrate_b2_smoke.py`
- Doc: `docs/ps-010-run-archive-rehydrate-b2-proof.md`

### PS-011 — Provenance Passport API from rehydrated evidence

Proves the Provenance Passport is assembled from rehydrated stored evidence
(attempts, asset hashes, manifest verification, archive/rehydration metadata),
never rerunning generation and never faking verification.

- Script: `scripts/ps011_provenance_passport_api_smoke.py`
- Doc: `docs/ps-011-review-room-provenance-passport-api-proof.md`
