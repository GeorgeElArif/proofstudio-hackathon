# PS-010 Run Archive + Rehydrate from B2 Proof

## Status

Accepted pass (strong pass: rehydrated from B2 object content).

PS-010 proves that a live ProofStudio run can be archived into a durable
run-archive JSON artifact, stored as a real B2/Genblaze asset, and later
reconstructed into a fresh in-memory API store **without rerunning any
provider** and without fabricating media or a manifest. The archive carried
the full PS-006 20-field attempt ledger, asset refs, manifest metadata, B2
URLs, image SHA-256, and prompt/provider-note metadata; the rehydrated run
was read back through the normal PS-008/PS-009 service methods and matched
the original live run exactly.

- Overall: `ok: true`
- Live run status: `live_completed`
- Framework mode: `service_only` (FastAPI is not installed in the current
  venv, so the service layer is exercised directly; the archive/rehydrate
  service methods and `app.py` route wiring use the same service layer and
  require no FastAPI dependency for this slice)
- Archive storage mode: `b2_object_content` (the archive bytes were actually
  read back from Backblaze B2 and rehydrated)
- PS-004, PS-005, PS-006, PS-007, PS-008, and PS-009 proof scripts are
  unchanged

## Slice Scope

PS-010 is the first durability/recovery milestone. It is intentionally not:

- a production database layer
- a multi-user recovery system
- an authentication / authorization layer
- a deployment
- a background-worker system
- a C2PA / legal authenticity claim
- full disaster-recovery automation

## Files Changed

- `src/proofstudio/api/models.py` - added PS-010 archive constants:
  `ARCHIVE_SCHEMA_VERSION` (`ps-010.1`), honest archive storage modes
  (`ARCHIVE_STORAGE_MODE_B2`, `ARCHIVE_STORAGE_MODE_LOCAL`), and
  `ARCHIVE_TRUTH_BOUNDARY`.
- `src/proofstudio/provenance/genblaze_store.py` - added two small reusable
  helpers so an archive stored as a B2 asset can be read back by URL:
  `GenblazeStore.read_bytes_for_url(url)` and
  `GenblazeStore.object_exists_for_url(url)`.
- `src/proofstudio/api/archive.py` - **new file**. The durability/recovery
  layer. Exposes `build_run_archive`, `write_run_archive_local`,
  `store_run_archive_with_genblaze`, `read_archive_from_b2`,
  `validate_archive`, `load_archive`, and `rehydrate_run_from_archive`.
- `src/proofstudio/api/services.py` - added `archive_run(run_id)`,
  `rehydrate_run_from_archive(source)`, and the clearly test-only
  `clear_store_for_test()` to `ProofStudioService`.
- `scripts/ps010_run_archive_rehydrate_b2_smoke.py` - **new file**. Smoke
  test.
- `docs/ps-010-run-archive-rehydrate-b2-proof.md` - this file.

`src/proofstudio/api/store.py`, `src/proofstudio/api/live_bridge.py`, and
`src/proofstudio/api/app.py` were not modified: the existing store methods
(`create_campaign` / `create_run` with explicit ids, `set_attempts`,
`set_assets`, `set_manifest`, `update_run`) already support restoring a run
from an archive, and the live bridge and route handlers are unchanged.

Historical proof scripts (PS-004 / PS-005 / PS-006 / PS-007 / PS-008 /
PS-009) were not modified.

## Live Run Status

The smoke started from a real PS-009 live run (`run_live=true`) so the
archive would carry genuine evidence:

- **Selected provider:** `cloudflare-workers-ai`
- **Selected model:** `@cf/bytedance/stable-diffusion-xl-lightning`
- **Fallback used:** `false` (Cloudflare succeeded on the primary attempt)
- **Attempt count:** `1` (full 20-field `ProviderAttempt`)
- **Asset count:** `4` (generated image, prompt packet JSON, attempt ledger
  JSON, provider note Markdown)
- **Stored manifest verify:** `true`

## Archive Creation Proof

`build_run_archive(service, run_id)` read the run and its sub-resources
through the normal PS-008/PS-009 readback methods and produced an archive
dict that validated against `validate_archive` (schema version, required
fields, and the full PS-006 20-field attempt shape). The archive included:

- `archive_schema_version: ps-010.1`
- `run_id`, `campaign_id`, full `campaign_snapshot`
- run status, selected provider/model, `api_method`, `job_type`,
  `fallback_used`, `attempt_count`
- the full `attempts` ledger (20-field each, no compact attempts)
- `assets` (4 refs with B2 URLs and the real image SHA-256)
- `manifest_metadata` (URI, hash, `stored_manifest_verify`)
- honest `local_artifacts` metadata (path / exists / sha256 / size) for the
  generated image, prompt packet, attempt ledger, and provider note
- `b2_urls`, `image_sha256`, `prompt_packet_metadata`,
  `provider_note_metadata`
- `truth_boundary`, `created_at`, `archived_at`

`archive_created: true`.

## Archive Storage Mode

`b2_object_content` (strong pass).

`store_run_archive_with_genblaze` ingested the archive JSON through the
reusable `GenblazeStore` helper with `artifact_type: run_archive` and the
PS-010 metadata block, stored it as a real B2 object, and verified it through
a Genblaze manifest.

- **Archive URI:**
  `https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-010/assets/7f/d1/7fd1179981a5f706498d320cac0068446bba0c3db5481c5a18ef7b17ab357783.json`
- **Archive SHA-256:**
  `7fd1179981a5f706498d320cac0068446bba0c3db5481c5a18ef7b17ab357783`
- archive's own Genblaze manifest was written and byte-level verified
  (`archive_stored_manifest_verify: true`)

`archive_stored: true`, `archive_uri` and `archive_sha256` populated.

## Rehydration Source

`b2` - the archive JSON was downloaded as real object content from B2 via
`GenblazeStore.read_bytes_for_url(archive_uri)` and parsed, then handed to
`rehydrate_run_from_archive` as an inline archive. This is the spec's strong
pass: rehydration used the bytes actually read from B2, not a local copy.

If the direct B2 object read had failed, the smoke would have fallen back to
the local archive and reported `archive_storage_mode: local_after_b2_store`
honestly (the archive is still proven to have been stored as a B2 asset). If
B2 storage itself were unavailable (e.g. a blocked live run on missing B2
env), it would report `archive_storage_mode: local_only`. Neither fallback
was needed in this run.

## Restored Run Proof

After clearing the original in-memory state and rehydrating into a fresh
service/store, the normal readback methods returned restored evidence:

- **`get_run(run_id)`** returned `status: live_completed`,
  `selected_provider: cloudflare-workers-ai`, `selected_model` present.
- **`get_run_attempts(run_id)`** returned `1` full 20-field attempt (validated
  against the PS-006 contract; no compact attempts).
- **`get_run_assets(run_id)`** returned `4` assets matching the original
  count, including the real generated-image asset with its original SHA-256
  and B2 URL.
- **`get_run_manifest(run_id)`** returned `ready: true` with the original
  manifest URI and hash.

- `restored_run_id` matches the original `run_id`
- `restored_campaign_id` matches the original `campaign_id`
- `restored_attempt_count: 1` == `attempt_count: 1`
- `restored_asset_count: 4` == `asset_count: 4`

## Restored Attempts / Assets / Manifest Proof

- **Restored manifest URI:** `https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-010/manifests/54d73492-5fb6-43fe-bc22-0e6d43032929.json`
  (matches the original `manifest_uri` exactly)
- **Restored manifest hash:** `86e574f6df5070584aac890992dae3cb71d3d93403d098fe71dc040093ea4344`
  (matches the original `manifest_hash` exactly)
- `stored_manifest_verify: true` carried through the archive unchanged

The restored run references the same on-disk local artifacts (image, prompt
packet, attempt ledger, provider note) carried verbatim from the archive - no
new files were written during rehydration.

## No-Provider-Call-During-Rehydrate Proof

Rehydration restores state through plain store writes (`create_campaign`,
`create_run`, `set_attempts`, `set_assets`, `set_manifest`); it never calls
`create_run(run_live=true)`, never calls the PS-009 live bridge, and never
calls a provider. To prove this, the smoke replaced the service layer's only
entry point to the live bridge (`proofstudio.api.services.execute_live_run`)
with a sentinel that would raise if invoked, then ran rehydrate under that
guard:

- `no_live_provider_call_during_rehydrate: true`
- `rehydrate_result.provider_calls_made: 0`
- sentinel call count during rehydrate: `0`

## No-Fake-Media Proof

- `no_fake_media: true`
- the set of files under the output directory was snapshotted before
  rehydrate and was unchanged after rehydrate (no new media files written)
- `rehydrate_result.media_files_written: 0`
- no fake manifest was fabricated: the restored manifest URI/hash are the
  original ones carried through the archive

## Smoke Test Summary

Run:

```
python -m py_compile \
  src/proofstudio/api/models.py \
  src/proofstudio/api/store.py \
  src/proofstudio/api/services.py \
  src/proofstudio/api/live_bridge.py \
  src/proofstudio/api/archive.py \
  scripts/ps010_run_archive_rehydrate_b2_smoke.py

python scripts/ps010_run_archive_rehydrate_b2_smoke.py
```

- `py_compile`: clean
- smoke: `ok: true`, exit `0`
- `framework_mode: service_only`
- `live_run_attempted: true`
- `live_run_status: live_completed`
- `live_run_completed: true`
- `selected_provider: cloudflare-workers-ai`
- `selected_model: @cf/bytedance/stable-diffusion-xl-lightning`
- `fallback_used: false`
- `attempt_count: 1`
- `asset_count: 4`
- `archive_created: true`
- `archive_stored: true`
- `archive_storage_mode: b2_object_content`
- `archive_uri` and `archive_sha256` populated
- `rehydrate_attempted: true`
- `rehydrate_completed: true`
- `rehydrate_source: b2`
- `restored_attempt_count: 1`, `restored_asset_count: 4`
- `restored_manifest_uri` == `manifest_uri`
- `restored_manifest_hash` == `manifest_hash`
- `stored_manifest_verify: true`
- `no_live_provider_call_during_rehydrate: true`
- `no_fake_media: true`
- `readbacks_checked: true`
- secret-leak scan on the transcript: clean

Summary: `/tmp/proofstudio-ps-010/run-archive-rehydrate-summary.json`
Transcript: `/tmp/proofstudio-ps-010/run-archive-rehydrate-transcript.json`

## Truth Boundary

PS-010 proves ProofStudio can archive a run into a durable artifact and
reconstruct its API readback state from that evidence without rerunning
providers:

- durable run-archive JSON with the full attempt ledger, assets, manifest
  metadata, B2 URLs, image SHA-256, and prompt/provider-note metadata
- archive stored as a real B2/Genblaze asset and byte-level verified
- run rehydrated from B2 object content into a fresh store
- normal readbacks restored and matching the original live run
- no provider call, no fake media, no fake manifest during rehydration

It does NOT prove:

- production-database persistence (the live store is still process-local;
  durability lives in the B2 archive artifact, not a database)
- multi-user recovery
- authentication / authorization
- deployment
- background job execution
- full disaster-recovery automation
- semantic truth
- legal authenticity
- C2PA authenticity
- human authorship

## Connection to PS-009

PS-009 made the live run possible: `create_run(run_live=true)` drives the
PS-007 provider-router chain, captures the full ProviderAttempt ledger,
stores the generated image and supporting artifacts in B2, and writes/verifies
a Genblaze manifest. PS-010 builds directly on that evidence:

- `build_run_archive` reads the PS-009 run readbacks and the PS-009 local
  artifact paths (generated image, prompt packet, attempt ledger, provider
  note) and folds them into a single durable archive.
- The archive reuses the same `GenblazeStore` / `AssetSpec` B2 storage helper
  as PS-009 to store the archive artifact itself.
- Rehydration restores the exact PS-009 run shape (status, selected
  provider/model, attempts, assets, manifest metadata) so the rehydrated run
  is indistinguishable from the original through the readback surface.

PS-009 proved a live run can be created and stored; PS-010 proves that run
survives beyond the process that created it.

## Limitations and Next Improvements

- The archive is stored as its own Genblaze artifact set. A future slice
  could link the archive asset into the original run's manifest (or derive
  the archive URI from the run manifest) so recovery can start from a run id
  rather than a stored archive URI.
- Rehydration restores into an in-memory store; a later slice should add a
  durable application state backend (Postgres/SQLite) with the B2 archive as
  the system of record.
- `rehydrate_run_from_manifest_uri` (recover by reading the run manifest and
  locating the archive asset) is the natural next capability.
- No background/automated recovery job yet; rehydration is explicit.
