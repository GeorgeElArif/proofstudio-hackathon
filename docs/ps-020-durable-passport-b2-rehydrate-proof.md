# PS-020 — Durable Passport / B2 Source-of-Truth Rehydrate Proof

## Status

PS-020 backend and frontend foundation passed local validation.

This slice makes the public Provenance Passport route safer after backend memory loss by adding a gated durable rehydrate path.

## What changed

- Added `src/proofstudio/api/durable_passport.py`.
- Extended `ProofStudioService.get_run_passport()` to try durable rehydrate only when the run is missing from memory.
- Kept durable reads disabled by default.
- Kept B2 reads disabled by default.
- Added local durable index support for deterministic smoke tests.
- Added a public passport UI source panel.
- Added frontend type support for `durable_passport`.

## Safety result

- Provider call: false
- B2 read: false
- B2 write: false
- Durable read default: false
- Durable B2 read default: false

## Smoke evidence

Evidence file:

- `docs/evidence/ps-020/durable-passport-foundation-smoke.json`

Smoke result:

- ok: True
- run_id: run_f085ee18af444f27b019a3666cbe9c55
- campaign_id: camp_579b3fc3d444446caa00faf0ea4f6f14
- missing_without_gate: True
- api_rehydrate_status_code: 200
- durable_source: local_rehydrated
- rehydrate_completed: True
- no_live_provider_call_during_rehydrate: True
- provider_call: False
- b2_read: False
- b2_write: False

## Current boundary

This commit proves the durable passport foundation and local index rehydrate behavior.

It does not yet claim a live B2 rehydrate smoke. That remains gated behind explicit B2 read configuration.

## Why this matters

PS-019 made the passport public.

PS-020 starts making it durable.

A missing in-memory run can now be restored from indexed archive evidence when durable reads are explicitly enabled, without rerunning providers and without faking proof.
