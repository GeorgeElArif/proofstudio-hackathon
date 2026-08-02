# PS-010 Run Archive + Rehydrate from B2

## 1. Purpose

PS-010 proves that ProofStudio runs are durable beyond in-memory API state.

PS-009 proved:

API request
→ live provider router
→ generated asset
→ B2 storage
→ Genblaze manifest
→ API readback

PS-010 must now prove:

live run
→ durable run archive stored in B2
→ API/store memory cleared or replaced
→ run rehydrated from B2/manifest/archive evidence
→ readbacks restored without rerunning providers

This is the first durability and recovery milestone.

## 2. Product Meaning

ProofStudio is not just a generator.

ProofStudio should be a system of record for AI media operations.

A creator, agency, or marketing team must be able to answer:

- What was generated?
- Which provider made it?
- Which model was used?
- What attempts failed or were skipped?
- What prompt packet was used?
- Where are the stored assets?
- Which manifest verifies the artifact set?
- Can this run be reconstructed later?

PS-010 proves that the answer is yes.

## 3. Why This Matters for the Demo

This is an out-of-the-box winning feature:

“Rehydrate from B2.”

Judges should see that ProofStudio does not lose the provenance story when app memory is gone.

The demo moment:

1. Create a live run.
2. Show API readback.
3. Clear or replace the in-memory store.
4. Rehydrate the run from durable B2/Genblaze evidence.
5. Show the same run state restored.
6. Show the manifest and hashes still verify.

This makes B2 feel essential, not decorative.

## 4. Current Foundation

Completed:

- PS-006 ProviderRouter Core
- PS-007 Live ProviderRouter Chain + B2 + Genblaze
- PS-008 Backend API Skeleton
- PS-009 API Live Run Bridge

PS-010 must build on PS-009, not rewrite it.

## 5. Non-Goals

Do not build frontend UI.

Do not add production database.

Do not add authentication.

Do not deploy.

Do not add background workers.

Do not rerun live providers during rehydration.

Do not fake archived runs.

Do not fake B2 objects.

Do not fake Genblaze verification.

Do not claim C2PA authenticity.

Do not claim legal authenticity.

Do not claim semantic truth.

Do not modify historical proof scripts.

## 6. Required Behavior

PS-010 must support this lifecycle:

1. Create campaign.
2. Create live run using `run_live=true`.
3. Store a durable run archive artifact.
4. Confirm live run readbacks work.
5. Create a fresh in-memory store/service.
6. Rehydrate the run from durable evidence.
7. Confirm restored readbacks work:
   - run
   - attempts
   - assets
   - manifest
8. Confirm no live provider was called during rehydration.
9. Confirm no fake media was created during rehydration.
10. Confirm restored data matches the original run identity and proof metadata.

## 7. Required Files

Allowed new files:

- `src/proofstudio/api/archive.py`
- `scripts/ps010_run_archive_rehydrate_b2_smoke.py`
- `docs/ps-010-run-archive-rehydrate-b2-proof.md`

Allowed modifications:

- `src/proofstudio/api/models.py`
- `src/proofstudio/api/store.py`
- `src/proofstudio/api/services.py`
- `src/proofstudio/api/live_bridge.py`
- `src/proofstudio/api/app.py`
- `src/proofstudio/provenance/genblaze_store.py` only if a small reusable helper is required

Do not modify historical proof scripts:

- `scripts/ps004_provider_router_cloudflare_smoke.py`
- `scripts/ps005_pollinations_fallback_smoke.py`
- `scripts/ps006_provider_router_core_smoke.py`
- `scripts/ps007_live_provider_router_chain_smoke.py`
- `scripts/ps008_backend_api_smoke.py`
- `scripts/ps009_api_live_run_bridge_smoke.py`

## 8. Archive Artifact

Create a durable run archive JSON artifact.

Suggested local name:

`proofstudio-run-archive.json`

Suggested B2/Genblaze metadata:

- artifact_type: `run_archive`
- proofstudio_test: `ps-010`
- slice: `PS-010`
- run_id
- campaign_id
- selected_provider
- selected_model
- manifest_uri
- manifest_hash
- archive_schema_version

The archive JSON must contain enough information to reconstruct API readbacks:

- archive_schema_version
- run_id
- campaign_id
- campaign snapshot
- run status
- selected_provider
- selected_model
- api_method
- job_type
- fallback_used
- attempt_count
- full attempts
- assets
- manifest metadata
- local paths if useful
- B2 URLs
- image SHA-256
- prompt packet metadata
- provider note metadata
- truth boundary
- created_at
- archived_at

## 9. Archive Truth Rules

The archive must not invent facts.

It must only include data from:

- campaign record
- run record
- provider attempts
- asset metadata
- manifest metadata
- PS-009 live result

If live run fails or blocks, archive may still store a failed/blocked run archive, but it must not fake image or manifest success.

## 10. Rehydrate Service

Create:

`src/proofstudio/api/archive.py`

It should expose functions similar to:

- `build_run_archive(...)`
- `write_run_archive_local(...)`
- `store_run_archive_with_genblaze(...)`
- `download_or_read_archive_from_b2(...)`
- `rehydrate_run_from_archive(...)`
- `rehydrate_run_from_manifest_uri(...)` if practical

The exact function names may vary, but the capability must be clear and tested.

## 11. Rehydration Requirements

Rehydration must:

1. Load a durable run archive.
2. Validate archive schema version.
3. Validate required fields.
4. Validate full ProviderAttempt 20-field shape.
5. Restore campaign into a fresh store if missing.
6. Restore run into a fresh store.
7. Restore attempts.
8. Restore assets.
9. Restore manifest metadata.
10. Return a structured rehydration result.
11. Not call live providers.
12. Not upload fake B2 artifacts.
13. Not create fake generated media.

## 12. Manifest/B2 Lookup

Preferred path:

- Store the run archive as one of the Genblaze assets.
- Use the manifest or returned B2 asset list to locate the archive artifact.
- Download/read the archive artifact.
- Validate SHA-256 if available.
- Rehydrate from the archive JSON.

Acceptable fallback for PS-010:

- If direct B2 archive download is difficult, the smoke may use the archive local file plus manifest/B2 metadata to validate the archive was stored.
- But the documentation must call this out honestly.
- The target product path should still be B2-based rehydration.

Strong pass:

- rehydrate from B2 object content or manifest-linked archive content.

Weak pass:

- rehydrate from local archive after proving archive asset was uploaded.

## 13. API/Service Additions

Add service methods if useful:

- `archive_run(run_id)`
- `rehydrate_run_from_archive(...)`
- `rehydrate_run_from_manifest(...)`
- `clear_store_for_test()` only if safe and clearly test-only

Readbacks after rehydration must use the normal PS-008/PS-009 methods:

- `get_run`
- `get_run_attempts`
- `get_run_assets`
- `get_run_manifest`

## 14. Smoke Script

Create:

`scripts/ps010_run_archive_rehydrate_b2_smoke.py`

The smoke script must:

1. Set output directory:
   `/tmp/proofstudio-ps-010`
2. Create service/store.
3. Create campaign.
4. Create live run with `run_live=true`.
5. If live run completes:
   - verify selected provider/model
   - verify attempts
   - verify assets
   - verify manifest
6. Build run archive JSON.
7. Store run archive through B2/Genblaze or as part of a Genblaze artifact set.
8. Create a fresh service/store.
9. Rehydrate run from archive/B2 evidence.
10. Verify restored campaign exists.
11. Verify restored run exists.
12. Verify restored attempts match count and full schema.
13. Verify restored assets match count.
14. Verify restored manifest metadata matches manifest URI/hash.
15. Verify no provider call happened during rehydration.
16. Verify no fake media was created.
17. Write summary JSON:
    `/tmp/proofstudio-ps-010/run-archive-rehydrate-summary.json`
18. Write transcript JSON:
    `/tmp/proofstudio-ps-010/run-archive-rehydrate-transcript.json`
19. Print final summary JSON.

If live run is blocked, the script may exit 0 only if:

- blocked state is honest
- no fake archive success is claimed
- clear blocked reason is written
- no fake media/manifest exists

## 15. Required Summary Fields

The summary must include:

- ok
- slice
- live_run_attempted
- live_run_status
- live_run_completed
- archive_created
- archive_stored
- archive_storage_mode
- archive_uri
- archive_sha256
- rehydrate_attempted
- rehydrate_completed
- rehydrate_source
- restored_run_id
- restored_campaign_id
- selected_provider
- selected_model
- fallback_used
- attempt_count
- restored_attempt_count
- asset_count
- restored_asset_count
- manifest_uri
- restored_manifest_uri
- manifest_hash
- restored_manifest_hash
- stored_manifest_verify
- no_live_provider_call_during_rehydrate
- no_fake_media
- readbacks_checked
- summary_path
- transcript_path
- truth_boundary

## 16. Acceptance Criteria

PS-010 is accepted if:

- live run completes honestly or blocks honestly
- archive JSON is created
- archive contains full attempt ledger
- archive is stored durably or storage limitation is documented honestly
- fresh service/store can rehydrate from archive evidence
- normal readback methods work after rehydration
- restored run metadata matches original live run metadata
- no live provider is called during rehydration
- no fake media is created
- no fake manifest is created
- secrets are not leaked
- historical proof scripts remain untouched

## 17. Failure Conditions

Reject PS-010 if:

- rehydration reruns providers
- archive contains compact attempts
- archive invents asset or manifest metadata
- local-only archive is claimed as B2 rehydration without proof
- fake media is created
- fake manifest URI is created
- secrets are printed or committed
- historical proof scripts are modified
- unrelated files are changed
- dry-run/live behavior from PS-009 regresses

## 18. Documentation Proof

Create:

`docs/ps-010-run-archive-rehydrate-b2-proof.md`

It must include:

- status
- live run status
- selected provider/model
- archive creation proof
- archive storage mode
- archive URI if available
- rehydration source
- restored run proof
- restored attempts/assets/manifest proof
- no-provider-call-during-rehydrate proof
- truth boundary
- connection to PS-009
- limitations and next improvements

## 19. Truth Boundary

PS-010 proves that ProofStudio can archive and reconstruct run evidence from durable artifacts.

It does not prove:

- production database persistence
- multi-user recovery
- auth/security
- legal authenticity
- C2PA authenticity
- semantic truth
- final UI behavior
- full disaster recovery automation

Those are later slices.
