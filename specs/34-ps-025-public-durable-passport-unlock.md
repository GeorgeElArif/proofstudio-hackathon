# PS-025 — Public Durable Passport Unlock

## Status

Specification slice.

## Purpose

Resolve the blocker discovered by PS-024.

PS-024 pinned verified golden demo evidence, but public passport pinning remained blocked because the verified durable PS-021 run does not currently resolve as a public `/passport/<run_id>` on the deployed backend.

PS-025 must safely unlock a public durable passport path for the golden demo run without rerunning providers, inventing proof, or enabling unsafe broad durable reads.

## Roadmap Discipline

This is a controlled roadmap adjustment, not drift.

Original PS-022 roadmap listed PS-025 as Judge Mode. PS-024 revealed a higher-risk blocker: judges cannot open the verified golden run through a public passport route yet.

Therefore PS-025 is reassigned to Public Durable Passport Unlock.

Judge Mode remains valuable, but it should come after there is a real public durable passport for Judge Mode to point at.

## Product Goal

A judge should be able to open a stable public URL and see the golden run passport backed by verified durable B2 evidence.

Expected judge path:

`Judge Cockpit -> Golden Demo Run -> Public Provenance Passport -> B2 Archive Evidence -> Truth Boundary`

## Current Verified Base

From PS-024 golden demo manifest:

- file: `docs/evidence/demo/golden-demo-run.json`
- source slice: PS-021
- run_id: `run_89d967f9000045efa22ed4cc78cfa67f`
- campaign_id: `camp_bea5161faa6244079d2ee01ce445c259`
- archive SHA-256: `a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141`
- archive URI: `https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-021/assets/a6/ad/a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141.json`
- rehydrate_source: `b2_rehydrated`
- provider_calls_during_rehydrate: `0`
- no_live_provider_call_during_rehydrate: `true`
- public_passport_url: `null` before PS-025 because pinning is blocked

## Non-Negotiable Rules

Do not fake public passport success.

Do not rerun providers to make the golden passport work.

Do not enable broad unauthenticated durable reads for arbitrary run IDs.

Do not expose secrets.

Do not claim semantic truth, legal authenticity, C2PA authenticity, human authorship, Object Lock, tamper-proof storage, enterprise auth, or production security unless actually implemented.

## Required Discovery

Before implementation, inspect:

- `docs/evidence/demo/golden-demo-run.json`
- `docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json`
- `src/proofstudio/api/app.py`
- `src/proofstudio/api/passport.py`
- `src/proofstudio/api/durable_passport.py`
- `src/proofstudio/api/archive.py`
- `src/proofstudio/api/store.py`
- `apps/web/src/PublicPassportPage.tsx`
- `apps/web/src/JudgeCockpitHome.tsx`
- existing API tests and smoke scripts
- Render/public deployment docs if relevant

## Required Design

PS-025 should implement the narrowest safe unlock.

Preferred design:

1. Add a verified golden-demo durable passport path.
2. Allow the public passport API to resolve only the known golden `run_id` from the PS-024 manifest.
3. Rehydrate the passport from the verified B2 archive or from a checked-in manifest only if the source is explicitly marked as evidence-derived.
4. Preserve `provider_calls_during_rehydrate = 0`.
5. Return clear API fields showing:
   - durable source
   - archive URI
   - archive SHA-256
   - no provider call during rehydrate
   - truth boundary
   - public unlock scope

Acceptable alternatives:

- A dedicated endpoint such as `/api/passports/golden-demo`.
- A narrow allowlist config loaded from `docs/evidence/demo/golden-demo-run.json`.
- A public route that serves the golden passport from durable evidence without allowing arbitrary public durable reads.

Rejected approaches:

- enabling all durable reads publicly
- requiring live provider keys
- generating a new run just for the public route
- hard-coding fake passport data disconnected from evidence
- hiding that the passport is evidence-derived
- editing historical proof JSON/scripts to make values match

## Frontend Requirement

After backend unlock, update the Judge Cockpit homepage so:

- “View Provenance Passport” opens the verified public golden passport URL if the backend route is verified.
- The previous blocked message is replaced or softened to explain that PS-025 unlocked the public golden passport.
- The page still states the truth boundary.
- The page must not link to a fake route.

Update the PS-024 manifest or create a PS-025 public manifest extension only after verification proves the public URL works.

## Required Evidence

Create:

- `docs/evidence/ps-025/public-durable-passport-unlock-smoke.json`

This evidence must include:

- `ok`
- `public_passport_url`
- `run_id`
- `campaign_id`
- `archive_uri`
- `archive_sha256`
- `rehydrate_source`
- `provider_calls_during_rehydrate`
- `no_live_provider_call_during_rehydrate`
- `truth_boundary_present`
- `api_status_code`
- `frontend_public_url_checked`
- `no_broad_public_durable_read`
- `source_manifest`
- `checked_at`

If public deployment cannot be tested locally in this slice, the evidence must clearly separate:

- local contract proof
- public deployment pending proof

Do not mark public deployment verified unless it is actually verified.

## Required Proof Doc

Create:

- `docs/ps-025-public-durable-passport-unlock-proof.md`

The proof doc must include:

- blocker from PS-024
- implementation design
- safety model
- public unlock scope
- source evidence used
- route/API contract
- validation commands
- smoke result
- no-provider-rerun confirmation
- no-broad-public-read confirmation
- truth boundary confirmation
- limitations

## Required Smoke Script

Create:

- `scripts/ps025_public_durable_passport_unlock_smoke.py`

The smoke script must validate:

1. golden manifest exists
2. API can resolve the golden passport route locally or through a configured base URL
3. returned run_id matches PS-024 manifest
4. returned archive_uri/archive_sha256 match PS-024/PS-021 evidence
5. provider_calls_during_rehydrate equals 0
6. no_live_provider_call_during_rehydrate is true
7. truth boundary is present
8. broad arbitrary durable read is not enabled
9. frontend homepage links to public golden passport only after verified unlock
10. PS-024 smoke still passes
11. PS-023 smoke still passes
12. no secrets
13. no forbidden affirmative claims

## Expected Allowed Files

Implementation may modify only files needed for this slice.

Likely allowed files:

- `src/proofstudio/api/app.py`
- `src/proofstudio/api/passport.py`
- `src/proofstudio/api/durable_passport.py`
- `src/proofstudio/api/archive.py` only if needed
- `src/proofstudio/api/models.py` only if response schema needs an explicit field
- `apps/web/src/JudgeCockpitHome.tsx`
- `apps/web/src/PublicPassportPage.tsx` only if needed
- `docs/evidence/demo/golden-demo-run.json` only if public URL becomes verified
- `docs/evidence/ps-025/public-durable-passport-unlock-smoke.json`
- `docs/ps-025-public-durable-passport-unlock-proof.md`
- `scripts/ps025_public_durable_passport_unlock_smoke.py`
- focused API tests if an existing test structure supports this safely

Do not modify:

- historical PS-019/020/021 evidence JSON
- historical proof scripts
- provider router code
- unrelated frontend styles
- deployment config unless absolutely necessary and explained

## Validation Requirements

Before commit, run:

- PS-025 smoke script
- PS-024 smoke script
- PS-023 smoke script
- backend tests if present and relevant
- frontend typecheck/build if frontend files changed
- secret scan through canonical smoke
- forbidden claim scan through canonical smoke
- whitespace check
- exact status/cached-file guard

## Acceptance Criteria

PS-025 is accepted only if:

1. The golden demo run has a verified public durable passport path, or the slice honestly proves why the unlock remains blocked.
2. No provider is called during passport unlock/rehydrate.
3. The returned passport values match PS-024/PS-021 source evidence.
4. Public durable read scope is narrow, preferably only the golden demo run.
5. Arbitrary public run IDs cannot trigger durable B2 reads.
6. Homepage only links to the public golden passport after verification.
7. Evidence JSON is machine-checkable.
8. Proof doc explains safety model and limitations.
9. PS-025 smoke passes.
10. PS-024 and PS-023 smoke still pass.
11. Final working tree contains only PS-025 files before commit.

## Failure Conditions

Fail the slice if:

- a fake public passport URL is added
- arbitrary public durable reads are enabled
- provider calls happen during unlock/rehydrate
- PS-024 manifest values are changed without evidence
- public success is claimed without proof
- frontend links to an unverified public route
- historical proof/evidence is rewritten
- forbidden claims are introduced
- unrelated files are changed

## Next Slice After PS-025

If PS-025 succeeds:

- PS-026 — B2 Evidence Explorer

If PS-025 remains blocked:

- PS-025B — Public Durable Passport Deployment Gate

Judge Mode should remain after the public durable passport is available.
