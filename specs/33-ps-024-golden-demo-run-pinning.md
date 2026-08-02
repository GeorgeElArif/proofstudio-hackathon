# PS-024 — Golden Demo Run Pinning

## Status

Specification slice.

## Purpose

Pin one canonical judge-facing demo run across ProofStudio.

PS-023 created the Judge Cockpit homepage, but the Provenance Passport path still depends on a user-entered run ID. That is honest, but it creates friction for judges.

PS-024 must create a single canonical demo path that lets judges open the strongest available run/passport/evidence without guessing IDs or reading internal docs first.

## Product Goal

A judge should be able to click one button and land on a real, coherent ProofStudio proof story:

`Judge Cockpit -> Golden Demo Run -> Provenance Passport -> B2 Evidence -> Rehydrate Proof -> Submission Evidence`

## Current Proven Base

Known proven project state before PS-024:

- PS-018B: public Render deployment and live URL smoke.
- PS-019: public passport route and public passport proof score.
- PS-020: durable passport B2 rehydrate foundation.
- PS-021: live B2 durable rehydrate proof.
- PS-022: master winning roadmap.
- PS-023: Judge Cockpit homepage and canonical PS-023 validation script.

PS-021 accepted durable proof:

- commit: `2294e180f5a8462fa4922c9529e4463b61d0729e`
- archive SHA-256: `a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141`
- archive URI: `https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-021/assets/a6/ad/a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141.json`

## Non-Negotiable Rule

Do not invent a run ID, campaign ID, passport URL, manifest URI, proof score, or archive proof.

PS-024 must discover canonical values from existing repo evidence or block honestly.

## Required Discovery

Before implementation, inspect existing evidence and docs:

- `docs/evidence/ps-019/`
- `docs/evidence/ps-020/`
- `docs/evidence/ps-021/`
- `docs/ps-019-public-passport-proof-score-proof.md`
- `docs/ps-020-durable-passport-b2-rehydrate-proof.md`
- `docs/ps-021-live-b2-durable-rehydrate-proof.md`
- `apps/web/src/`
- `docs/submission/`
- `README.md`

The implementation must identify the best canonical demo source from existing evidence.

If multiple candidate runs exist, choose the one that gives the strongest judge story:

1. public passport route works
2. proof score exists
3. B2 archive URI exists
4. B2 readback proof exists
5. rehydrate proof exists
6. provider calls during rehydrate equals zero
7. truth boundary exists

## Canonical Demo Manifest

Create a single canonical demo manifest if implementation confirms enough source evidence exists.

Expected file:

- `docs/evidence/demo/golden-demo-run.json`

The manifest should include only verified values available from existing evidence:

- `demo_id`
- `source_slice`
- `run_id`
- `campaign_id`
- `public_app_url`
- `public_api_url`
- `public_passport_url`
- `archive_uri`
- `archive_sha256`
- `manifest_uri`
- `manifest_hash`
- `proof_score`
- `rehydrate_source`
- `provider_calls_during_rehydrate`
- `no_live_provider_call_during_rehydrate`
- `truth_boundary`
- `evidence_files`

If a field is not available from existing evidence, it must be either omitted or set to `null` with a clear reason. Do not fake missing values.

## Required Product Changes

### 1. Homepage Golden Demo CTA

Update the Judge Cockpit home so the primary demo/passport path can open the canonical demo directly.

Expected behavior:

- “Open Judge Demo” should still route to the Review Room if that is the implemented demo surface.
- “View Provenance Passport” should open the pinned passport directly if a verified `run_id` exists.
- If a verified `run_id` does not exist, the CTA must remain honest and disabled/planned.

### 2. Public Demo Route or Helper

If the existing frontend structure supports it cleanly, add a route such as:

- `/demo`
- `/demo/golden`

The route should guide judges to the canonical run/passport/evidence surfaces.

Do not add a route if it creates risk or duplicates existing functionality. A direct pinned homepage CTA is acceptable if cleaner.

### 3. Evidence Pack Linkage

The canonical demo run should be referenced from:

- homepage
- PS-024 proof doc
- submission evidence docs if safe
- README only if the values are verified and not likely to become stale immediately

### 4. Truth Boundary

The pinned demo must keep the same truth boundary:

ProofStudio proves what this pipeline did. It does not prove semantic truth, legal authenticity, C2PA authenticity, or human authorship.

## Required Proof Doc

Create:

- `docs/ps-024-golden-demo-run-pinning-proof.md`

The proof doc must include:

- discovery process
- source evidence files inspected
- selected canonical run and why
- omitted/null fields and why
- CTA target map
- validation commands
- no-fake-proof confirmation
- truth boundary confirmation
- limitations

## Required Smoke Script

Create:

- `scripts/ps024_golden_demo_run_pinning_smoke.py`

The smoke script must validate:

1. canonical manifest exists, if enough evidence exists
2. pinned values match source evidence
3. homepage contains the pinned CTA or honest planned/disabled state
4. public passport URL shape is valid if `run_id` exists
5. archive URI/hash match source evidence if present
6. rehydrate proof fields are honest if present
7. truth boundary exists
8. no forbidden affirmative claims
9. no secrets
10. no broken internal route markers introduced

The smoke script must exit nonzero if:

- any canonical value is invented
- source evidence does not match the pinned manifest
- homepage hard-codes an unverified run ID
- a broken CTA is introduced
- forbidden claims are introduced
- secrets are exposed

## Expected Allowed Files

Implementation may modify only files justified by inspection.

Likely allowed files:

- `apps/web/src/JudgeCockpitHome.tsx`
- `apps/web/src/App.tsx` only if a demo route is added
- optional new frontend demo/config file
- `docs/evidence/demo/golden-demo-run.json`
- `docs/ps-024-golden-demo-run-pinning-proof.md`
- `scripts/ps024_golden_demo_run_pinning_smoke.py`
- selected submission docs only if they reference verified pinned values

Do not modify historical proof scripts.

## Validation Requirements

Before commit, run:

- PS-024 smoke script
- existing PS-023 smoke script
- frontend typecheck
- frontend build
- secret scan
- forbidden claim scan
- whitespace check
- status/cached-file guard

## Acceptance Criteria

PS-024 is accepted only if:

1. The project has one canonical demo run path or honestly documents why pinning is blocked.
2. Any pinned run/passport/archive/proof values are traced to existing evidence.
3. Homepage CTA friction is reduced.
4. No run ID, URI, hash, score, or proof field is invented.
5. The canonical demo manifest is machine-checkable if enough evidence exists.
6. The proof doc explains source evidence and limitations.
7. PS-024 smoke passes.
8. PS-023 smoke still passes.
9. Frontend typecheck/build passes if frontend files changed.
10. Final working tree contains only PS-024 files before commit.

## Failure Conditions

Fail the slice if:

- any canonical value is guessed
- homepage links to a fake or unverified run
- proof score is invented
- B2 URI/hash is copied incorrectly
- rehydrate status is claimed without source evidence
- CTAs are broken
- truth boundary is removed or weakened
- forbidden claims are introduced
- unrelated files are changed

## Next Slice After PS-024

PS-026 — B2 Evidence Explorer, unless PS-024 reveals a higher-risk blocker.

PS-025 Judge Mode remains useful, but pinning the golden run first gives Judge Mode something concrete to point at.
