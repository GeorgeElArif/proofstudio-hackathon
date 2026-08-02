# PS-009 API Live Run Bridge Proof

## Status

Accepted pass.

PS-009 connects the PS-008 backend API skeleton to the PS-007 live
ProviderRouter chain. A `create_run(run_live=true)` request now drives the
real live provider chain (Cloudflare Workers AI primary, Pollinations
no-key fallback), captures the full 20-field ProviderAttempt ledger, stores
the generated image and supporting artifacts in Backblaze B2, writes and
verifies a Genblaze manifest, and feeds all of that evidence back into the
in-memory API store so readbacks return the real evidence state.

- Overall: `ok: true`
- Live run status: `live_completed`
- Framework mode: `service_only` (FastAPI is not installed in the current
  venv, so the service layer is exercised directly; the FastAPI route wiring
  in `app.py` delegates to the same service layer and requires no FastAPI
  dependency for this slice)
- PS-004, PS-005, PS-006, PS-007, and PS-008 proof scripts are unchanged

## Slice Scope

PS-009 is the first slice where a product-facing API request can produce
live proof-backed AI media output. It is intentionally not:

- a frontend
- an authentication / authorization layer
- a production database layer
- a deployment
- a background-worker system
- a C2PA / legal authenticity claim

## Files Changed

- `src/proofstudio/api/models.py` - added PS-009 live run statuses
  (`live_running`, `live_completed`, `live_failed`, `live_blocked`) and
  extended `RunRecord` with live-run metadata fields: `api_method`,
  `job_type`, `attempts`, `assets`, manifest verification fields
  (`manifest_hash`, `in_memory_manifest_verify`, `stored_manifest_verify`,
  `transfer_failures`, `stored_transfer_failures`), local artifact paths
  (`local_image`, `local_prompt_packet`, `local_attempt_ledger`,
  `local_provider_note`), `truth_boundary`, and `error` / `blocked_reason`.
- `src/proofstudio/api/store.py` - added `set_attempts` and `set_assets` so
  the live bridge can register the full attempt ledger / asset list in one
  call after live execution.
- `src/proofstudio/api/live_bridge.py` - **new file**. Exposes
  `execute_live_run(...)`, the clean bridge function that drives the PS-007
  live ProviderRouter chain + B2 + Genblaze pipeline and returns a
  structured result dict.
- `src/proofstudio/api/services.py` - wired `create_run(run_live=true)` to
  the live bridge via `_execute_live_and_apply`. Dry-run behavior is
  completely unchanged. `PROOF_VERSION` bumped to `ps-009`.
- `src/proofstudio/api/app.py` - description string updated to reference
  PS-009. No route changes were needed: the existing route handlers already
  delegate to the service layer, so the live path is available through the
  same endpoints when FastAPI is importable.
- `scripts/ps009_api_live_run_bridge_smoke.py` - **new file**. Smoke test.
- `docs/ps-009-api-live-run-bridge-proof.md` - this file.

Historical proof scripts (PS-004 / PS-005 / PS-006 / PS-007 / PS-008) were
not modified.

## Dry-Run Behavior

Dry-run remains the default and is completely unchanged from PS-008.

`POST /runs` without `run_live=true` (or with `dry_run=true`) produces a run
with status `dry_run_created` and:

- no live provider calls (no Cloudflare, no Pollinations)
- no B2 calls
- no Genblaze manifest write
- no media generated or fabricated
- `attempt_count` is `0`; attempts list is empty
- `asset_count` is `0`; assets list is empty
- manifest readback returns `{ ready: false, not_ready_reason: ... }`
- all live metadata fields (`selected_provider`, `manifest_uri`,
  `manifest_hash`, `local_image`, etc.) are `null` / empty

The smoke script explicitly verifies this: `dry_run_checked: true`,
`dry_run_no_live_calls: true`, `dry_run_no_b2_calls: true`,
`no_fake_media: true`.

## Live-Run Behavior

`POST /runs` with `run_live=true` and `dry_run=false` triggers the live
bridge. The flow is:

1. The run record is created with status `live_running`.
2. `execute_live_run(...)` drives the PS-007 live ProviderRouter chain:
   - Cloudflare Workers AI primary attempt
   - Pollinations no-key fallback attempt (only if Cloudflare fails/skips)
3. Every attempt is recorded as a full PS-006 20-field `ProviderAttempt`.
4. On provider success, the real generated image is persisted locally, the
   prompt packet / attempt ledger / provider note are written, and all four
   artifacts are stored in B2 through the reusable `GenblazeStore` helper.
5. The Genblaze manifest is written to B2, read back, and byte-level
   verified.
6. The run record is updated with the live result: selected provider/model,
   `api_method`, `job_type`, `fallback_used`, full attempts, assets, manifest
   metadata, local artifact paths, and `truth_boundary`.
7. The attempts / assets / manifest sub-resources are registered so the
   readback endpoints return the real evidence.

### Selected Provider

`cloudflare-workers-ai`

### Selected Model

`@cf/bytedance/stable-diffusion-xl-lightning`

### Fallback Used

`false` (Cloudflare succeeded on the primary attempt; Pollinations was not
called)

### Attempt Count

`1` (Cloudflare primary succeeded; no fallback needed)

### Asset Count

`4` (generated image, prompt packet JSON, attempt ledger JSON, provider note
Markdown)

## Manifest Evidence

- **Manifest URI:**
  `https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-009/manifests/f859ca2c-d6f4-40e0-85d3-f32652d7f154.json`
- **Manifest hash:**
  `ff750084948aa86e1daa7cb5466ce6dce42fb5336b0f107534b53858870be2fa`
- `in_memory_manifest_verify: true`
- `stored_manifest_verify: true`
- `transfer_failures: []`
- `stored_transfer_failures: []`

## Readback Proof

After the live run completed, the service-layer readbacks returned the real
stored evidence:

- **`get_run(run_id)`** returned `status: live_completed`,
  `selected_provider: cloudflare-workers-ai`, `selected_model` present,
  `attempt_count: 1`, `asset_count: 4`, `manifest_uri` present.
- **`get_run_attempts(run_id)`** returned 1 full 20-field `ProviderAttempt`
  record (Cloudflare, `normalized_status: OK`, `api_method: workers-ai-run`,
  real latency recorded).
- **`get_run_assets(run_id)`** returned 4 asset references: the real
  generated JPEG (`produced_real_media: true`, real SHA-256, real B2 URL),
  the prompt packet JSON, the attempt ledger JSON, and the provider note
  Markdown.
- **`get_run_manifest(run_id)`** returned `ready: true`, the manifest URI,
  manifest hash, `stored_manifest_verify: true`, and empty transfer failure
  lists.

## Blocked / Failure Behavior

The live bridge and service layer handle honest failures and blocks without
faking success:

- **Missing B2 environment variables** -> status `live_blocked`. No provider
  is called, no image is written, no manifest is produced. A clear
  `blocked_reason` explains which variables are missing.
- **All providers fail or are skipped** -> status `live_failed`. The full
  attempt ledger is preserved (including skipped / failed attempts) so
  failure evidence is never lost. No fake image, no fake manifest.
- **Provider succeeds but B2/Genblaze storage fails** -> status
  `live_failed`. Real attempts and the real local image are preserved; a
  clear `error` explains the storage failure.

In all failure/block cases:
- no fake image is created
- no fake manifest URI or hash is produced
- `stored_manifest_verify` is never `true`
- a clear `error` or `blocked_reason` is set on the run record
- attempts are preserved when available

## Smoke Test Summary

Run:

```
python -m py_compile \
  src/proofstudio/api/models.py \
  src/proofstudio/api/store.py \
  src/proofstudio/api/services.py \
  src/proofstudio/api/app.py \
  src/proofstudio/api/live_bridge.py \
  scripts/ps009_api_live_run_bridge_smoke.py

python scripts/ps009_api_live_run_bridge_smoke.py
```

- `py_compile`: clean (all six files compile)
- smoke: `ok: true`
- `framework_mode: service_only`
- `dry_run_checked: true`
- `dry_run_no_live_calls: true`
- `dry_run_no_b2_calls: true`
- `live_run_attempted: true`
- `live_run_status: live_completed`
- `live_run_completed: true`
- `selected_provider: cloudflare-workers-ai`
- `selected_model: @cf/bytedance/stable-diffusion-xl-lightning`
- `fallback_used: false`
- `attempt_count: 1`
- `attempts_checked: true` (all attempts validated against the PS-006
  20-field contract; no compact attempts)
- `assets_checked: true` (asset_count >= 4)
- `manifest_checked: true`
- `stored_manifest_verify: true`
- `transfer_failures: []`
- `stored_transfer_failures: []`
- `no_fake_media: true` (local image path points at a real on-disk file)
- `readbacks_checked: true`
- secret-leak scan on the transcript: clean

Summary: `/tmp/proofstudio-ps-009/api-live-run-bridge-summary.json`
Transcript: `/tmp/proofstudio-ps-009/api-live-run-bridge-transcript.json`
Live artifacts: `/tmp/proofstudio-ps-009/live-run/`

## How PS-009 Connects to PS-007 and PS-008

PS-009 reuses the PS-007 live pipeline components directly - no shelling out
to the PS-007 script, no duplication of large code blocks:

- `LiveCloudflareProvider` / `LivePollinationsProvider` from
  `src/proofstudio/providers/live_*.py`
- `ProviderRouter` from `src/proofstudio/providers/router.py`
- `GenblazeStore` / `AssetSpec` from
  `src/proofstudio/provenance/genblaze_store.py`

The `live_bridge.py` module packages the PS-007 orchestration (build
providers, route, persist image, write artifacts, upload + verify) as a
single reusable function that the PS-008 service layer calls. PS-008 built
the chassis (API skeleton, in-memory store, service layer, typed models,
registration hooks); PS-009 attaches the PS-007 engine at the labeled wiring
point (`_execute_live_and_apply`) that PS-008 left open.

## Truth Boundary

PS-009 proves the backend API/service layer can explicitly trigger and store
a live proof-backed generation run:

- live provider routing through the PS-007 chain
- full ProviderAttempt ledger capture (20-field contract)
- real generated image persistence
- B2 storage of all artifacts
- Genblaze manifest write + read-back + byte-level verification
- API run record updated with real provider/model/asset/manifest metadata
- readback endpoints expose the real evidence state

It does NOT prove:

- production persistence (the store is process-local)
- authentication / authorization
- deployment
- background job execution
- semantic truth
- legal authenticity
- C2PA authenticity
- human authorship

Those are later slices.
