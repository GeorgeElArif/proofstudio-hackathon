# PS-029 — B2 Rehydrate Comparison

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
- PS-028 — Manifest Verification Panel

PS-026 made B2 evidence visible.
PS-027 made Genblaze orchestration visible.
PS-028 made manifest consistency visible.
PS-029 must now make B2 rehydrate value visible.

## Purpose

Expose a judge-facing B2 Rehydrate Comparison surface.

ProofStudio already proves that the golden run can be rehydrated from durable B2-backed evidence without calling providers again.

Judges should clearly see the before/after comparison:

- golden run evidence
- B2 archived evidence
- rehydrated evidence
- provider calls during rehydrate equal zero
- no live provider call during rehydrate equals true
- archive URI and SHA-256 match across evidence

## Product Goal

A judge should be able to open a product surface and understand:

- what was archived
- what was rehydrated
- which fields match
- which fields prove no provider rerun occurred
- how B2 reduces dependency on live provider availability
- what is local contract proof vs verified durable evidence
- what is not being claimed

Expected judge path:

Judge Cockpit -> B2 Rehydrate Comparison -> Manifest Verification Panel -> B2 Evidence Explorer -> Public Passport

## Current Verified Base

Use only checked-in evidence and verified golden values.

Relevant evidence sources:

- PS-021 live B2 durable rehydrate proof:
  - docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json

- PS-024 golden demo manifest:
  - docs/evidence/demo/golden-demo-run.json

- PS-025 public durable passport unlock evidence:
  - docs/evidence/ps-025/public-durable-passport-unlock-smoke.json

- PS-026 B2 Evidence Explorer evidence:
  - docs/evidence/ps-026/b2-evidence-explorer-smoke.json

- PS-027 Genblaze Pipeline Graph evidence:
  - docs/evidence/ps-027/genblaze-pipeline-graph-smoke.json

- PS-028 Manifest Verification Panel evidence:
  - docs/evidence/ps-028/manifest-verification-panel-smoke.json

Verified golden values:

- run_id: run_89d967f9000045efa22ed4cc78cfa67f
- campaign_id: camp_bea5161faa6244079d2ee01ce445c259
- archive SHA-256: a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141
- archive URI: https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-021/assets/a6/ad/a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141.json
- rehydrate_source: b2_rehydrated
- provider_calls_during_rehydrate: 0
- no_live_provider_call_during_rehydrate: true

## Non-Negotiable Rules

Do not fake B2 rehydrate proof.

Do not call providers.

Do not fetch arbitrary B2 objects through untrusted input.

Do not broaden public durable-read scope.

Do not claim browser-side B2 byte verification unless actually implemented and validated.

Do not claim public deployment verification unless actually tested.

Do not claim legal authenticity, C2PA authenticity, human authorship, semantic truth, tamper-proof storage, Object Lock, enterprise auth, or production security unless actually implemented.

Do not modify historical evidence JSON under PS-019/020/021/024/025/026/027/028.

Do not modify historical smoke scripts PS-019 through PS-028.

Do not expose secrets.

## Required Discovery

Before implementation, inspect:

- specs/38-ps-029-b2-rehydrate-comparison.md
- docs/evidence/demo/golden-demo-run.json
- docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json
- docs/evidence/ps-025/public-durable-passport-unlock-smoke.json
- docs/evidence/ps-026/b2-evidence-explorer-smoke.json
- docs/evidence/ps-027/genblaze-pipeline-graph-smoke.json
- docs/evidence/ps-028/manifest-verification-panel-smoke.json
- scripts/ps028_manifest_verification_panel_smoke.py
- scripts/ps027_genblaze_pipeline_graph_smoke.py
- scripts/ps026_b2_evidence_explorer_smoke.py
- scripts/ps025_public_durable_passport_unlock_smoke.py
- scripts/ps024_golden_demo_run_pinning_smoke.py
- scripts/ps023_judge_cockpit_home_smoke.py
- apps/web/src/App.tsx
- apps/web/src/JudgeCockpitHome.tsx
- apps/web/src/ManifestVerificationPanel.tsx
- apps/web/src/GenblazePipelineGraph.tsx
- apps/web/src/B2EvidenceExplorer.tsx
- apps/web/src/PublicPassportPage.tsx
- existing shared frontend evidence/data files

## Required Product Surface

Implement a B2 Rehydrate Comparison product surface.

Preferred:

- dedicated frontend route: /b2-rehydrate-comparison
- component: apps/web/src/B2RehydrateComparison.tsx
- optional data file: apps/web/src/b2RehydrateComparison.ts
- frontend-only using verified checked-in evidence constants

Alternative acceptable form:

- strong panel embedded in Manifest Verification Panel or B2 Evidence Explorer if dedicated route is too risky

Dedicated route is preferred because PS-029 is a roadmap surface.

## Required Comparison Content

The comparison must show the story in a simple, judge-readable way.

Required comparison columns or sections:

1. Golden run / manifest
2. B2 archive evidence
3. Rehydrated evidence
4. Rehydrate result

Required fields:

- run_id
- campaign_id
- archive_uri
- archive_sha256
- rehydrate_source
- provider_calls_during_rehydrate
- no_live_provider_call_during_rehydrate

Required visible outcomes:

- same run_id
- same campaign_id
- same archive URI
- same archive SHA-256
- rehydrate_source equals b2_rehydrated
- provider_calls_during_rehydrate equals 0
- no_live_provider_call_during_rehydrate equals true
- no live provider rerun required for rehydrate
- truth boundary is present
- public deployment remains pending unless verified

## Required CTA Changes

Update product navigation so judges can reach the B2 Rehydrate Comparison.

Required:

- Judge Cockpit has a clear CTA to /b2-rehydrate-comparison
- B2 Rehydrate Comparison links to:
  - /manifest-verification
  - /b2-evidence
  - /genblaze-pipeline
  - /passport/run_89d967f9000045efa22ed4cc78cfa67f
  - /
- Manifest Verification Panel may link to /b2-rehydrate-comparison if low-risk
- B2 Evidence Explorer may link to /b2-rehydrate-comparison if low-risk
- No broken internal links

## Required Truth Boundary

The comparison must clearly distinguish:

- checked-in manifest consistency
- durable B2 archive proof
- B2 rehydrate proof
- local public passport contract proof
- inferred product explanation
- public deployment pending

Allowed claims:

- checked-in evidence records B2 rehydrate proof
- checked-in evidence records zero provider calls during rehydrate
- checked-in evidence agrees on archive URI and SHA-256
- rehydrate uses durable archive evidence instead of a live provider rerun for the verified golden run

Forbidden claims:

- the comparison proves semantic truth of media
- the comparison proves legal authenticity
- the comparison proves human authorship
- the comparison proves C2PA authenticity
- the comparison proves Object Lock or tamper-proof storage
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

- docs/evidence/ps-029/b2-rehydrate-comparison-smoke.json

Evidence must include:

- ok
- route_or_surface
- run_id
- campaign_id
- archive_uri
- archive_sha256
- rehydrate_source
- provider_calls_during_rehydrate
- no_live_provider_call_during_rehydrate
- comparison_sources_verified
- comparison_fields_verified
- rehydrate_comparison_verified
- b2_rehydrate_surface_verified
- truth_boundary_present
- source_ps021_evidence
- source_ps024_manifest
- source_ps025_evidence
- source_ps026_evidence
- source_ps027_evidence
- source_ps028_evidence
- frontend_surface_verified
- api_surface_verified
- no_provider_call
- no_broad_b2_read
- no_prior_slice_evidence_modified
- public_deployment_pending
- checked_at

## Required Proof Doc

Create:

- docs/ps-029-b2-rehydrate-comparison-proof.md

The proof doc must include:

- roadmap alignment
- product surface chosen
- files changed
- route/CTA map
- comparison source list
- compared field list
- rehydrate comparison result
- no-provider-rerun explanation
- B2 value explanation
- no-provider-call confirmation
- no-broad-B2-read confirmation
- no-prior-slice-evidence-mutation confirmation
- truth boundary confirmation
- validation commands
- smoke result
- limitations

## Required Smoke Script

Create:

- scripts/ps029_b2_rehydrate_comparison_smoke.py

The smoke script must validate:

1. B2 Rehydrate Comparison surface exists
2. route /b2-rehydrate-comparison exists if dedicated route is chosen
3. Judge Cockpit links to the comparison
4. comparison links to Manifest Verification Panel
5. comparison links to B2 Evidence Explorer
6. comparison links to Genblaze Pipeline Graph
7. comparison links to golden passport
8. required comparison sources are present
9. required comparison fields are present
10. run_id matches across PS-021/024/025/026/027/028 sources
11. campaign_id matches across PS-021/024/025/026/027/028 sources
12. archive URI matches across PS-021/024/025/026/027/028 sources
13. archive SHA-256 matches across PS-021/024/025/026/027/028 sources
14. rehydrate_source equals b2_rehydrated
15. provider_calls_during_rehydrate equals 0
16. no_live_provider_call_during_rehydrate is true
17. no-provider-rerun story is visible
18. truth boundary is present
19. no provider call is introduced
20. no broad B2 read is introduced
21. no secrets
22. no forbidden affirmative claims
23. no prior-slice evidence is modified
24. PS-028 smoke still passes through snapshot/restore protection if needed
25. PS-027 smoke still passes through snapshot/restore protection if needed
26. PS-026 smoke still passes through snapshot/restore protection if needed
27. PS-025 smoke still passes through snapshot/restore protection if needed
28. PS-024 smoke still passes
29. PS-023 smoke still passes
30. frontend typecheck/build passes if frontend changed

Important:

PS-029 smoke must preserve prior-slice evidence exactly. If it runs any prior smoke that writes evidence, snapshot/restore prior evidence files so the working tree remains clean outside PS-029 files.

Do not modify prior smoke scripts. Wrap them safely from PS-029.

Do not add brittle duplicate inline product scanners to final commit gates if canonical smoke already validates the product surface.

## Expected Allowed Files

Implementation may modify only files needed for PS-029.

Likely allowed files:

- apps/web/src/App.tsx
- apps/web/src/JudgeCockpitHome.tsx
- optional apps/web/src/ManifestVerificationPanel.tsx
- optional apps/web/src/B2EvidenceExplorer.tsx
- optional apps/web/src/GenblazePipelineGraph.tsx
- optional apps/web/src/PublicPassportPage.tsx
- optional apps/web/src/styles.css
- new apps/web/src/B2RehydrateComparison.tsx
- optional apps/web/src/b2RehydrateComparison.ts
- docs/evidence/ps-029/b2-rehydrate-comparison-smoke.json
- docs/ps-029-b2-rehydrate-comparison-proof.md
- scripts/ps029_b2_rehydrate_comparison_smoke.py

Do not modify:

- historical evidence JSON under PS-019/020/021/024/025/026/027/028
- historical smoke scripts PS-019 through PS-028
- provider code unless a real bug is found and explained before commit
- backend API unless necessary and justified
- deployment config
- unrelated files

## Backend Validation Environment Rule

Any PS-029 validation that imports backend/API code must run with:

- source .venv/bin/activate
- export PYTHONPATH="$PWD/src"

Do not run python -m pip install -e . from repo root.

## Validation Requirements

Before commit, run:

- PS-029 smoke script
- PS-028 smoke script, through snapshot/restore protection if needed
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

PS-029 is accepted only if:

1. Judges can reach a clear B2 Rehydrate Comparison surface.
2. The comparison shows golden run vs B2 archive vs rehydrate result.
3. The comparison includes required sources.
4. The comparison includes required fields.
5. The comparison shows provider calls during rehydrate equal zero.
6. The comparison shows no live provider call during rehydrate is true.
7. Verified values match PS-021/PS-024/PS-025/PS-026/PS-027/PS-028 evidence.
8. No fake B2 rehydrate proof is claimed.
9. No provider call is introduced.
10. No broad B2 read is introduced.
11. No prior-slice evidence is modified.
12. Truth boundary remains visible.
13. PS-029 smoke passes.
14. PS-028, PS-027, PS-026, PS-025, PS-024, and PS-023 regressions pass.
15. Final working tree contains only PS-029 files before commit.

## Failure Conditions

Fail the slice if:

- comparison is decorative but not evidence-backed
- comparison omits required evidence sources
- comparison omits required verification fields
- comparison claims no provider rerun without evidence
- comparison claims browser-side B2 byte verification without implementing it
- comparison claims certification/authenticity not implemented
- comparison claims public deployment success without verification
- comparison introduces provider calls
- comparison introduces broad B2 reads
- prior-slice evidence is modified
- archive URI/hash is copied incorrectly
- truth boundary is removed or weakened
- forbidden claims are introduced
- unrelated files are changed

## Next Slice After PS-029

PS-030 — Failure-as-Proof Timeline
