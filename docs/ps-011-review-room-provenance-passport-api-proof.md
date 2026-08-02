# PS-011 Review Room / Provenance Passport API Proof

## Status

**Passed.** PS-011 implements the first product-facing Provenance Passport API.
A live run was completed, archived to B2, rehydrated from B2 object content
into a fresh in-memory store, and a Provenance Passport was assembled from the
rehydrated readbacks — all without rerunning any provider and without creating
fake media.

Smoke result: `ok: true`, exit `0`.

## Passport Source

The passport was built from a **rehydrated run** (`source:
archive_rehydrated_run`). The smoke:

1. Created a live run (`run_live=true`).
2. Built a durable run archive and stored it as a real B2/Genblaze asset.
3. Created a fresh service/store (simulating memory loss).
4. Rehydrated the run by reading the archive bytes back from B2 object content
   (`rehydrate_source: b2`, `archive_storage_mode: b2_object_content`).
5. Built the passport from the rehydrated service's normal readbacks.

This proves the passport works after durable recovery, not just from live
in-memory state.

## Selected Provider / Model

- **Selected provider:** `cloudflare-workers-ai`
- **Selected model:** `@cf/bytedance/stable-diffusion-xl-lightning`
- **api_method:** `workers-ai-run`
- **job_type:** `image_generation`
- **fallback_used:** `false`
- **attempt_count:** `1` (Cloudflare succeeded on the primary attempt)

## Attempt Timeline Summary

| # | provider | model | normalized | latency_ms | retryable | fallback_allowed |
|---|----------|-------|------------|-----------|-----------|------------------|
| 0 | cloudflare-workers-ai | @cf/bytedance/stable-diffusion-xl-lightning | OK | 3493 | false | false |

- One `OK` attempt, no failures, no skips.
- The compact `attempt_timeline` is derived from `raw_attempts`, which carry
  the full PS-006 20-field ProviderAttempt shape (`attempt_id`, `attempt_index`,
  `provider`, `model`, `api_method`, `job_type`, `status`, `normalized_status`,
  `started_at`, `finished_at`, `latency_ms`, `retryable`, `fallback_allowed`,
  `skip_reason`, `raw_error_type`, `sanitized_error_message`, `estimated_cost`,
  `free_or_paid`, `output_asset_refs`, `notes`). Compact attempts are never the
  source of truth.

## Asset / Hash Summary

Generated media is present and its hash is recorded:

- **generated_media_present:** `true`
- **primary_asset_media_type:** `image/jpeg`
- **primary_asset_sha256:** `df00563687939b9fc22ea32d4dba94b3281017457ad11141105af06d05a131c7`
- **primary_asset_size_bytes:** `97801`
- **asset_count:** `4` (generated image, prompt packet, attempt ledger,
  provider note — all stored in B2 and verified by the manifest).

Each asset in the passport `assets` section carries `url`, `media_type`,
`sha256`, `size_bytes`, and `metadata`.

## Manifest Verification Summary

- **manifest_uri:** `https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-011/manifests/<uuid>.json`
- **manifest_hash:** `8bbcc38bb2a0d1696b108032727e1fa0a335801648a14e668ed52ab0ee17a86a`
- **in_memory_manifest_verify:** `true`
- **stored_manifest_verify:** `true`
- **transfer_failures:** `[]`
- **stored_transfer_failures:** `[]`

Manifest verification was read back from stored run evidence; it was never
faked. The verification flags are surfaced verbatim from the normal
`get_run_manifest` readback.

## Archive / Rehydration Summary

- **archive_uri:** `https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-011/assets/<sha>.json`
- **archive_sha256:** `b22ed7d73e26c35e2b7106061b259eedc05f43c376e584c85b3250573965ad1d`
- **archive_storage_mode:** `b2_object_content` (strong pass — archive bytes
  were actually read back from B2).
- **rehydrate_source:** `b2`
- **rehydrate_completed:** `true`
- **restored_manifest_uri / restored_manifest_hash:** match the original live
  manifest URI/hash.
- **no_live_provider_call_during_rehydrate:** `true`.

When archive/rehydration evidence is not available, the passport section is
explicitly `status: not_available` with a `reason` — it is never omitted.

## Trust Boundary

**Claims** (asserted by this passport):

- `provider_attempt_evidence_was_captured`
- `asset_hashes_were_recorded`
- `manifest_verification_occurred`
- `archive_rehydration_evidence_present`

**Non-claims** (explicitly NOT asserted):

- `semantic_truth`
- `legal_authenticity`
- `c2pa_authenticity`
- `human_authorship`
- `final_production_security`

The validator enforces that every non-claim is present and that no non-claim
is ever asserted as a positive claim.

## Reviewer Next Actions

- For this completed run, risk flags were empty. Reviewers should proceed with
  normal review while respecting the non-claims above.
- When a passport surfaces risk flags
  (`fallback_used`, `failed_attempts_present`, `manifest_not_verified`,
  `archive_not_available`, `generated_media_missing`), the reviewer next
  actions guide the reviewer to inspect the attempt timeline, require manifest
  verification, or archive the run before trusting its evidence.

## Service / API Surface

- **Service method:** `ProofStudioService.get_run_passport(run_id, *, archive_evidence=None, source="auto")`
  in `src/proofstudio/api/services.py`. Uses normal readbacks
  (`get_run` / `get_run_attempts` / `get_run_assets` / `get_run_manifest`),
  never calls providers, never reruns generation, never writes media, never
  fakes manifest verification.
- **FastAPI route:** `GET /runs/{run_id}/passport` wired in
  `src/proofstudio/api/app.py` (guarded for `service_only` mode; activates
  automatically when FastAPI is importable).
- **Passport module:** `src/proofstudio/api/passport.py` exposing
  `build_provenance_passport(...)`, `validate_provenance_passport(...)`,
  `write_passport_local(...)`, and `timeline_from_attempts(...)`.

## Limitations and Next Improvements

- The passport is assembled from in-store evidence plus caller-supplied
  archive/rehydration metadata; it does not itself call B2. A future slice may
  have the service look up archive evidence from the store.
- This is a backend/service-only milestone. There is no Review Room UI yet.
- Passport generation does not prove production persistence or multi-user
  recovery; those are later slices.
- No C2PA signing, no legal/semantic authenticity, and no human-authorship
  verification is claimed or implemented.

## Connection to PS-010

PS-011 builds directly on PS-010's durability layer:

- PS-010 proved a run can be archived into a durable artifact and rehydrated
  from B2 object content without rerunning providers.
- PS-011 consumes that rehydrated state: the PS-011 smoke reuses the PS-010
  archive functions (`build_run_archive`, `store_run_archive_with_genblaze`,
  `read_archive_from_b2`, `rehydrate_run_from_archive`) and then assembles a
  Provenance Passport from the rehydrated readbacks with the PS-010 archive
  evidence attached.

## Files

- New: `src/proofstudio/api/passport.py`
- New: `scripts/ps011_provenance_passport_api_smoke.py`
- New: `docs/ps-011-review-room-provenance-passport-api-proof.md`
- Modified: `src/proofstudio/api/services.py` (added `get_run_passport` +
  `passport_module` import/export)
- Modified: `src/proofstudio/api/app.py` (added `GET /runs/{run_id}/passport`)
- Historical proof scripts (PS-004 … PS-010) are untouched.

## Truth Boundary

PS-011 proves that ProofStudio can transform stored run evidence (provider
attempts, asset hashes, manifest verification, archive/rehydration metadata)
into a structured Review Room / Provenance Passport object using normal service
readbacks.

It does not prove:

- semantic truth
- legal authenticity
- C2PA authenticity
- human authorship
- final production security
- production persistence
