# PS-028 — Manifest Verification Panel

## Status

Specification slice.

## Roadmap Discipline

This slice follows the PS-022 master roadmap.

Completed lead-in:

- PS-023 — Judge Cockpit Home
- PS-024 — Golden Demo Run Pinning
- PS-025 — Public Durable Passport Unlock
- PS-026 — B2 Evidence Explorer
- PS-027 — Genblaze Pipeline Graph

PS-026 made B2 evidence visible.
PS-027 made Genblaze orchestration visible.
PS-028 must now make manifest verification visible.

## Purpose

Expose the golden run manifest as a judge-facing verification panel.

ProofStudio already has durable evidence across:

- golden demo manifest
- PS-021 B2 durable rehydrate evidence
- PS-025 public durable passport evidence
- PS-026 B2 Evidence Explorer evidence
- PS-027 Genblaze Pipeline Graph evidence

Judges should not need to inspect raw JSON to see whether the key fields agree.

## Product Goal

A judge should be able to open a product surface and clearly see:

- which manifest is the source of the golden run
- which evidence files agree with it
- which fields match across sources
- which proof is local contract proof
- which proof is verified durable evidence
- what is not being claimed

Expected judge path:

Judge Cockpit -> Manifest Verification Panel -> Genblaze Pipeline Graph -> B2 Evidence Explorer -> Public Passport

## Current Verified Base

Use only checked-in evidence and verified golden values.

Relevant evidence sources:

- PS-021 live B2 durable rehydrate proof:
  - `docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json`

- PS-024 golden demo manifest:
  - `docs/evidence/demo/golden-demo-run.json`

- PS-025 public durable passport unlock evidence:
  - `docs/evidence/ps-025/public-durable-passport-unlock-smoke.json`

- PS-026 B2 evidence explorer evidence:
  - `docs/evidence/ps-026/b2-evidence-explorer-smoke.json`

- PS-027 Genblaze Pipeline Graph evidence:
  - `docs/evidence/ps-027/genblaze-pipeline-graph-smoke.json`

Verified golden values:

- run_id: `run_89d967f9000045efa22ed4cc78cfa67f`
- campaign_id: `camp_bea5161faa6244079d2ee01ce445c259`
- archive SHA-256: `a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141`
- archive URI: `https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-021/assets/a6/ad/a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141.json`
- rehydrate_source: `b2_rehydrated`
- provider_calls_during_rehydrate: `0`
- no_live_provider_call_during_rehydrate: `true`

## Non-Negotiable Rules

Do not fake manifest verification.

Do not claim the B2 object was fetched and byte-verified unless that is actually implemented and validated.

Do not claim cryptographic notarization, legal authenticity, C2PA authenticity, human authorship, semantic truth, tamper-proof storage, Object Lock, enterprise auth, or production security unless actually implemented.

Do not modify historical evidence JSON under PS-019/020/021/024/025/026/027.

Do not modify historical smoke scripts PS-019 through PS-027.

Do not broaden public durable-read scope.

Do not call providers.

Do not expose secrets.

Do not claim public deployment verification unless actually tested.

## Required Discovery

Before implementation, inspect:

- `specs/37-ps-028-manifest-verification-panel.md`
- `docs/evidence/demo/golden-demo-run.json`
- `docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json`
- `docs/evidence/ps-025/public-durable-passport-unlock-smoke.json`
- `docs/evidence/ps-026/b2-evidence-explorer-smoke.json`
- `docs/evidence/ps-027/genblaze-pipeline-graph-smoke.json`
- `scripts/ps027_genblaze_pipeline_graph_smoke.py`
- `scripts/ps026_b2_evidence_explorer_smoke.py`
- `scripts/ps025_public_durable_passport_unlock_smoke.py`
- `scripts/ps024_golden_demo_run_pinning_smoke.py`
- `scripts/ps023_judge_cockpit_home_smoke.py`
- `apps/web/src/App.tsx`
- `apps/web/src/JudgeCockpitHome.tsx`
- `apps/web/src/GenblazePipelineGraph.tsx`
- `apps/web/src/B2EvidenceExplorer.tsx`
- `apps/web/src/PublicPassportPage.tsx`
- existing shared frontend evidence/data files

## Required Product Surface

Implement a Manifest Verification Panel product surface.

Preferred:

- dedicated frontend route: `/manifest-verification`
- component: `apps/web/src/ManifestVerificationPanel.tsx`
- optional data file: `apps/web/src/manifestVerification.ts`
- frontend-only using verified checked-in evidence constants

Alternative acceptable form:

- strong panel embedded in Genblaze Pipeline Graph or B2 Evidence Explorer if dedicated route is too risky

Dedicated route is preferred because PS-028 is a roadmap surface.

## Required Verification Content

The panel must show a clear verification table or checklist.

Required sources:

1. Golden demo manifest
2. PS-021 B2 durable rehydrate evidence
3. PS-025 public durable passport evidence
4. PS-026 B2 Evidence Explorer evidence
5. PS-027 Genblaze Pipeline Graph evidence

Required fields to compare:

- run_id
- campaign_id
- archive_uri
- archive_sha256
- rehydrate_source
- provider_calls_during_rehydrate
- no_live_provider_call_during_rehydrate

Required visible outcomes:

- all core identifiers match
- archive URI matches
- archive SHA-256 matches
- rehydrate source is B2 rehydrated
- provider calls during rehydrate equal zero
- no live provider call during rehydrate is true
- truth boundary is present
- public deployment is still pending unless verified

## Required CTA Changes

Update product navigation so judges can reach the Manifest Verification Panel.

Required:

- Judge Cockpit has a clear CTA to `/manifest-verification`
- Manifest Verification Panel links to:
  - `/genblaze-pipeline`
  - `/b2-evidence`
  - `/passport/run_89d967f9000045efa22ed4cc78cfa67f`
  - `/`
- Genblaze Pipeline Graph may link to `/manifest-verification` if low-risk
- B2 Evidence Explorer may link to `/manifest-verification` if low-risk
- No broken internal links

## Required Truth Boundary

The panel must clearly distinguish:

- manifest field consistency across checked-in evidence
- durable B2 archive proof
- local public passport contract proof
- inferred product explanation
- public deployment pending

Allowed claims:

- checked-in evidence agrees on golden run identifiers
- checked-in evidence agrees on archive URI and SHA-256
- checked-in evidence records B2 rehydrate proof
- checked-in evidence records zero provider calls during rehydrate

Forbidden claims:

- the panel proves semantic truth of media
- the panel proves legal authenticity
- the panel proves human authorship
- the panel proves C2PA authenticity
- the panel proves Object Lock or tamper-proof storage
- the browser fetched and hashed the B2 object unless implemented
- public deployment is verified unless tested

## Required API Behavior

No new API endpoint is required.

Prefer frontend-only implementation using verified checked-in evidence constants.

If an API endpoint is added, it must be:

- read-only
- golden-run-scoped
- no provider calls
- no arbitrary B2 reads
- no secrets
- truth-boundary included

## Required Evidence

Create:

- `docs/evidence/ps-028/manifest-verification-panel-smoke.json`

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
- `sources_verified`
- `fields_verified`
- `manifest_consistency_verified`
- `manifest_panel_surface_verified`
- `truth_boundary_present`
- `source_ps021_evidence`
- `source_ps024_manifest`
- `source_ps025_evidence`
- `source_ps026_evidence`
- `source_ps027_evidence`
- `frontend_surface_verified`
- `api_surface_verified`
- `no_provider_call`
- `no_broad_b2_read`
- `no_prior_slice_evidence_modified`
- `public_deployment_pending`
- `checked_at`

## Required Proof Doc

Create:

- `docs/ps-028-manifest-verification-panel-proof.md`

The proof doc must include:

- roadmap alignment
- product surface chosen
- files changed
- route/CTA map
- verification source list
- verified field list
- consistency result
- manifest claim boundary
- no-provider-call confirmation
- no-broad-B2-read confirmation
- no-prior-slice-evidence-mutation confirmation
- truth boundary confirmation
- validation commands
- smoke result
- limitations

## Required Smoke Script

Create:

- `scripts/ps028_manifest_verification_panel_smoke.py`

The smoke script must validate:

1. Manifest Verification Panel surface exists
2. route `/manifest-verification` exists if dedicated route is chosen
3. Judge Cockpit links to the panel
4. panel links to Genblaze Pipeline Graph
5. panel links to B2 Evidence Explorer
6. panel links to golden passport
7. required evidence sources are present
8. required verification fields are present
9. run_id matches across PS-021/024/025/026/027 sources
10. campaign_id matches across PS-021/024/025/026/027 sources
11. archive URI matches across PS-021/024/025/026/027 sources
12. archive SHA-256 matches across PS-021/024/025/026/027 sources
13. rehydrate_source equals `b2_rehydrated`
14. provider_calls_during_rehydrate equals `0`
15. no_live_provider_call_during_rehydrate is `true`
16. truth boundary is present
17. no provider call is introduced
18. no broad B2 read is introduced
19. no secrets
20. no forbidden affirmative claims
21. no prior-slice evidence is modified
22. PS-027 smoke still passes
23. PS-026 smoke still passes through snapshot/restore protection if needed
24. PS-025 smoke still passes through snapshot/restore protection if needed
25. PS-024 smoke still passes
26. PS-023 smoke still passes
27. frontend typecheck/build passes if frontend changed

Important:

PS-028 smoke must preserve prior-slice evidence exactly. If it runs any prior smoke that writes evidence, snapshot/restore prior evidence files so the working tree remains clean outside PS-028 files.

Do not add brittle duplicate inline product scanners to final commit gates if canonical smoke already validates the product surface.

## Expected Allowed Files

Implementation may modify only files needed for PS-028.

Likely allowed files:

- `apps/web/src/App.tsx`
- `apps/web/src/JudgeCockpitHome.tsx`
- optional `apps/web/src/GenblazePipelineGraph.tsx`
- optional `apps/web/src/B2EvidenceExplorer.tsx`
- optional `apps/web/src/PublicPassportPage.tsx`
- optional `apps/web/src/styles.css`
- new `apps/web/src/ManifestVerificationPanel.tsx`
- optional `apps/web/src/manifestVerification.ts`
- `docs/evidence/ps-028/manifest-verification-panel-smoke.json`
- `docs/ps-028-manifest-verification-panel-proof.md`
- `scripts/ps028_manifest_verification_panel_smoke.py`

Do not modify:

- historical evidence JSON under PS-019/020/021/024/025/026/027
- historical smoke scripts PS-019 through PS-027
- provider code unless a real bug is found and explained before commit
- backend API unless necessary and justified
- deployment config
- unrelated files

## Backend Validation Environment Rule

Any PS-028 validation that imports backend/API code must run with:

- `source .venv/bin/activate`
- `export PYTHONPATH="$PWD/src"`

Do not run `python -m pip install -e .` from repo root.

## Validation Requirements

Before commit, run:

- PS-028 smoke script
- PS-027 smoke script, through snapshot/restore protection if needed
- PS-026 smoke script, through snapshot/restore protection if needed
- PS-025 smoke script, through snapshot/restore protection if needed
- PS-024 smoke script
- PS-023 smoke script
- frontend typecheck/build if frontend changed
- backend syntax/API tests if backend files changed
- whitespace check
- exact status/cached-file guard

## Acceptance Criteria

PS-028 is accepted only if:

1. Judges can reach a clear Manifest Verification Panel surface.
2. The panel compares required sources.
3. The panel compares required fields.
4. The panel shows all core manifest values match across evidence sources.
5. Verified values match PS-021/PS-024/PS-025/PS-026/PS-027 evidence.
6. No fake manifest verification is claimed.
7. No provider call is introduced.
8. No broad B2 read is introduced.
9. No prior-slice evidence is modified.
10. Truth boundary remains visible.
11. PS-028 smoke passes.
12. PS-027, PS-026, PS-025, PS-024, and PS-023 regressions pass.
13. Final working tree contains only PS-028 files before commit.

## Failure Conditions

Fail the slice if:

- panel is decorative but not evidence-backed
- panel omits required evidence sources
- panel omits required verification fields
- field consistency is claimed without checking source evidence
- panel claims browser-side B2 byte verification without implementing it
- panel claims certification/authenticity not implemented
- panel claims public deployment success without verification
- panel introduces provider calls
- panel introduces broad B2 reads
- prior-slice evidence is modified
- archive URI/hash is copied incorrectly
- truth boundary is removed or weakened
- forbidden claims are introduced
- unrelated files are changed

## Next Slice After PS-028

PS-029 — B2 Rehydrate Comparison
