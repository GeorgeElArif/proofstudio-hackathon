# PS-021 — Live B2 Durable Rehydrate Proof

## Status

PS-021 live B2 durable rehydrate smoke passed with real Backblaze B2.

A public ProofStudio Provenance Passport can be restored from a real B2 archive after backend memory loss, behind explicit gates, without rerunning providers and without faking proof.

## What changed

- Added `scripts/ps021_live_b2_durable_rehydrate_smoke.py`.
- Added `docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json`.

No product code changes were required: the existing PS-020 durable passport module (`src/proofstudio/api/durable_passport.py`) already supports the real B2 rehydrate path behind the explicit durable read + durable B2 read gates. PS-021 wires that path up to a live B2 archive and proves it end-to-end.

## Required gates (all default off)

- `PROOFSTUDIO_DURABLE_PASSPORT_READ_ENABLED` — false by default.
- `PROOFSTUDIO_DURABLE_PASSPORT_B2_READ_ENABLED` — false by default.
- `PROOFSTUDIO_PS021_LIVE_B2_REHYDRATE=1` — explicit opt-in for the live smoke.

The live smoke refuses to run if the durable read or durable B2 read gates are already enabled by default in the caller environment.

## Proof path

1. A safe dry-run ProofStudio run (`dry_run: true`, `run_live: false`) is created. No provider is called, no media is generated.
2. A run archive is built from service readbacks only (`build_run_archive`).
3. The archive is stored as a real B2/Genblaze asset (`store_run_archive_with_genblaze`).
4. A durable run index pointing to the real B2 archive URI is built and written locally (`build_run_index` + `write_run_index_local`).
5. Backend memory is cleared (`ProofStudioService.clear_store_for_test`).
6. With durable gates disabled, `GET /runs/{run_id}/passport` returns 404. The passport is honestly unavailable.
7. Only the explicit durable passport read gates are enabled inside the smoke.
8. `GET /runs/{run_id}/passport` returns 200 with `durable_passport.source == "b2_rehydrated"`. The archive bytes were read back from B2 by `read_archive_from_b2`.

## Safety result

- Provider call during rehydrate: false
- Provider calls during rehydrate: 0
- B2 archive write: true (real archive JSON stored as a B2/Genblaze asset)
- B2 archive read: true (real archive bytes read back from B2 during rehydrate)
- B2 generated media write: false
- Durable read default: false
- Durable B2 read default: false
- Missing without durable gate: true (404)

## Smoke evidence

Evidence file:

- `docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json`

Live B2 smoke result:

- ok: true
- slice: PS-021
- run_id: run_9567ddc8a5eb4ee08670de7282584803
- campaign_id: camp_c3d2697d3d524e9f8a4cc93997478ef7
- archive_uri: real B2 URI under `proofstudio/ps-021`
- archive_sha256: 21c5805c1568628d33517006ef57e0c4b9922e884ac1d077c5c38ac9dafc0ae8
- archive_storage_mode: b2_object_content
- missing_without_gate: true
- api_rehydrate_status_code: 200
- durable_source: b2_rehydrated
- rehydrate_completed: true
- no_live_provider_call_during_rehydrate: true
- provider_calls_during_rehydrate: 0
- b2_archive_write: true
- b2_archive_read: true
- b2_generated_media_write: false

## How to reproduce

```bash
source .venv/bin/activate
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"
# Requires B2_KEY_ID, B2_APP_KEY, B2_BUCKET, B2_REGION in the environment
# or in .env (loaded automatically by the smoke).
PROOFSTUDIO_PS021_LIVE_B2_REHYDRATE=1 \
python scripts/ps021_live_b2_durable_rehydrate_smoke.py
```

Without the explicit live gate, the smoke exits with code 78 and reports `skipped: true` so the durable B2 path is never accidentally exercised.

## Current boundary

This slice proves the live B2 durable rehydrate path for a public Provenance Passport behind explicit gates.

It does not prove production-database persistence, multi-user recovery, auth/security, legal authenticity, C2PA authenticity, or semantic truth.

## Why this matters

PS-019 made the passport public.

PS-020 added the durable foundation with a local inline archive index.

PS-021 proves the same recovery path against a real B2 archive: a public passport is not dependent on temporary backend memory. It can be restored from archived evidence in B2 without rerunning providers and without faking proof.
