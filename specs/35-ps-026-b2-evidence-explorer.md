# PS-026 — B2 Evidence Explorer

## Status

Specification slice.

## Roadmap Discipline

This slice returns to the PS-022 master roadmap after the controlled PS-025 blocker-resolution slice.

PS-022 roadmap item:

- PS-026 — B2 Evidence Explorer

PS-024 revealed the public passport blocker.
PS-025 unlocked the golden public passport contract locally.
PS-026 now makes the verified B2 evidence visible and judge-friendly.

## Purpose

Expose Backblaze B2 evidence as a first-class product surface.

ProofStudio already stores and verifies durable evidence through B2, but much of that proof is currently buried in JSON files, archive URIs, proof docs, and smoke outputs.

Judges need to see B2 as an active part of the product, not a hidden backend detail.

## Product Goal

A judge should be able to open the golden passport and clearly understand:

This run has durable B2 evidence. Here is the archive URI. Here is the SHA-256. Here is the rehydrate source. Here is proof that rehydrate did not call a live provider.

Expected judge path:

Judge Cockpit -> Public Golden Passport -> B2 Evidence Explorer -> Archive / Hash / Rehydrate Proof / Truth Boundary

## Current Verified Base

From PS-024 and PS-025:

- golden manifest: `docs/evidence/demo/golden-demo-run.json`
- PS-025 evidence: `docs/evidence/ps-025/public-durable-passport-unlock-smoke.json`
- golden run_id: `run_89d967f9000045efa22ed4cc78cfa67f`
- campaign_id: `camp_bea5161faa6244079d2ee01ce445c259`
- archive SHA-256: `a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141`
- archive URI: `https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-021/assets/a6/ad/a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141.json`
- rehydrate_source: `b2_rehydrated`
- provider_calls_during_rehydrate: `0`
- no_live_provider_call_during_rehydrate: `true`
- PS-025 status: local contract unlocked, public deployment pending

## Non-Negotiable Rules

Do not fake B2 reads.

Do not claim Object Lock, tamper-proof storage, legal authenticity, C2PA authenticity, semantic truth, human authorship, enterprise auth, or production security unless actually implemented.

Do not imply the B2 object itself was publicly fetched in the browser unless that is actually implemented and verified.

Do not expose secrets.

Do not alter historical PS-019/020/021 evidence.

Do not broaden public durable read scope.

## Required Discovery

Before implementation, inspect:

- `docs/evidence/demo/golden-demo-run.json`
- `docs/evidence/ps-025/public-durable-passport-unlock-smoke.json`
- `docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json`
- `scripts/ps025_public_durable_passport_unlock_smoke.py`
- `scripts/ps024_golden_demo_run_pinning_smoke.py`
- `scripts/ps023_judge_cockpit_home_smoke.py`
- `src/proofstudio/api/durable_passport.py`
- `src/proofstudio/api/services.py`
- `src/proofstudio/api/passport.py`
- `apps/web/src/JudgeCockpitHome.tsx`
- `apps/web/src/PublicPassportPage.tsx`
- existing frontend route structure in `apps/web/src/App.tsx`

## Required Product Surface

Implement a B2 Evidence Explorer surface.

Acceptable forms:

1. A dedicated frontend route, preferred if low-risk:
   - `/b2-evidence`
   - `/evidence/b2`
   - `/passport/<run_id>` section deep-link

2. A strong section inside the Public Passport page, acceptable if cleaner:
   - B2 Evidence Explorer panel
   - archive URI
   - archive SHA-256
   - source slice
   - rehydrate source
   - provider calls during rehydrate
   - no live provider call
   - evidence file references
   - truth boundary

3. A minimal API-backed route if needed:
   - API returns the golden B2 evidence from checked-in manifest/evidence
   - frontend renders it

The implementation should choose the lowest-risk route that gives judges the clearest proof.

## Required Explorer Content

The B2 Evidence Explorer must show:

- run_id
- campaign_id
- archive URI
- archive SHA-256
- source slice
- B2 archive status
- rehydrate source
- provider calls during rehydrate
- no live provider call during rehydrate
- source evidence files
- public deployment status if relevant
- truth boundary

It should clearly distinguish:

- verified B2 durable evidence
- local contract proof
- public deployment pending proof

## Required CTA Changes

Update Judge Cockpit and/or Public Passport page so judges can reach the B2 Evidence Explorer.

Required behavior:

- If the golden passport route is linked, add a nearby B2 Evidence CTA.
- If a dedicated B2 route is added, link to it from the homepage and passport page.
- No broken internal links.
- External GitHub links are allowed only as source references, not as the primary product experience.

## Required API Behavior

Only add or change API behavior if needed.

If an API endpoint is added, it must:

- be read-only
- expose only verified golden demo B2 evidence unless a wider safe design is explicitly justified
- not read arbitrary B2 objects by untrusted user input
- not expose secrets
- not call providers
- return truth boundary and limitation fields

## Required Evidence

Create:

- `docs/evidence/ps-026/b2-evidence-explorer-smoke.json`

Evidence must include:

- `ok`
- `route_or_surface`
- `run_id`
- `campaign_id`
- `archive_uri`
- `archive_sha256`
- `rehydrate_source`
- `provider_calls_during_rehydrate`
- `no_live_provider_call_during_rehydrate`
- `truth_boundary_present`
- `source_manifest`
- `source_ps025_evidence`
- `source_ps021_evidence`
- `frontend_surface_verified`
- `api_surface_verified`
- `no_broad_b2_read`
- `public_deployment_pending`
- `checked_at`

## Required Proof Doc

Create:

- `docs/ps-026-b2-evidence-explorer-proof.md`

The proof doc must include:

- roadmap alignment
- product surface chosen
- files changed
- evidence source files
- route/CTA map
- API contract if any
- no-fake-B2 confirmation
- no-provider-call confirmation
- no-broad-B2-read confirmation
- truth boundary confirmation
- validation commands
- smoke result
- limitations

## Required Smoke Script

Create:

- `scripts/ps026_b2_evidence_explorer_smoke.py`

The smoke script must validate:

1. B2 evidence surface exists in frontend and/or API
2. displayed/published run_id matches golden manifest
3. displayed/published campaign_id matches golden manifest
4. archive URI matches golden manifest and PS-021 evidence
5. archive SHA-256 matches golden manifest and PS-021 evidence
6. rehydrate source equals `b2_rehydrated`
7. provider_calls_during_rehydrate equals `0`
8. no_live_provider_call_during_rehydrate is `true`
9. truth boundary is present
10. no broad B2 read is introduced
11. no secrets
12. no forbidden affirmative claims
13. PS-025 smoke still passes
14. PS-024 smoke still passes
15. PS-023 smoke still passes
16. frontend typecheck/build passes if frontend changed

## Expected Allowed Files

Implementation may modify only files needed for this slice.

Likely allowed files:

- `apps/web/src/JudgeCockpitHome.tsx`
- `apps/web/src/PublicPassportPage.tsx`
- `apps/web/src/App.tsx` only if adding a route
- optional new frontend component, for example `apps/web/src/B2EvidenceExplorer.tsx`
- optional API file if endpoint is added
- `docs/evidence/ps-026/b2-evidence-explorer-smoke.json`
- `docs/ps-026-b2-evidence-explorer-proof.md`
- `scripts/ps026_b2_evidence_explorer_smoke.py`

Do not modify:

- historical evidence JSON under PS-019/020/021
- historical smoke scripts PS-019 through PS-025
- provider code
- deployment config unless absolutely required and explained
- unrelated styling

## Backend Validation Environment Rule

Any PS-026 validation that imports backend/API code must run with:

- `source .venv/bin/activate`
- `export PYTHONPATH="$PWD/src"`

Do not run `python -m pip install -e .` from repo root.

## Validation Requirements

Before commit, run:

- PS-026 smoke script
- PS-025 smoke script
- PS-024 smoke script
- PS-023 smoke script
- backend syntax/API tests if backend files changed
- frontend typecheck/build if frontend files changed
- whitespace check
- exact status/cached-file guard

## Acceptance Criteria

PS-026 is accepted only if:

1. Judges can reach a clear B2 Evidence Explorer surface.
2. Explorer values match PS-024/PS-025/PS-021 evidence.
3. B2 evidence is visible as a product feature, not just docs.
4. No fake B2 read or public deployment verification is claimed.
5. No broad B2 read is introduced.
6. No provider call is introduced.
7. Truth boundary remains visible.
8. PS-026 smoke passes.
9. PS-025, PS-024, and PS-023 smoke still pass.
10. Final working tree contains only PS-026 files before commit.

## Failure Conditions

Fail the slice if:

- archive URI/hash is copied incorrectly
- B2 evidence is only linked in GitHub docs and not surfaced in product UI/API
- frontend links are broken
- arbitrary B2 object reads are enabled
- provider calls happen
- public deployment success is claimed without verification
- truth boundary is removed or weakened
- forbidden claims are introduced
- unrelated files are changed

## Next Slice After PS-026

PS-027 — Genblaze Pipeline Graph
