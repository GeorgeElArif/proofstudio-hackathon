# PS-030 — Failure-as-Proof Timeline

## Status

Specification slice.

## Roadmap Discipline

This slice follows:

- PS-022 master roadmap
- PS-029 accepted B2 Rehydrate Comparison
- docs/roadmap/proofstudio-winning-implementation-roadmap-2026-06-29.md

The implementation roadmap is now binding: old-window out-of-the-box ideas are implementation commitments, not notes.

PS-030 implements:

- Failure-as-Proof Timeline
- Failure Theater
- visible production workflow timeline
- no-provider-rerun story
- Archive / Rehydrate Lab foundation
- proof that ProofStudio is an AI media operations cockpit, not another AI generator

## Product Thesis

ProofStudio is not an AI image generator.

ProofStudio is an AI media operations cockpit.

The winning idea:

Failure, skipped providers, retry decisions, fallback readiness, durable storage, and rehydrate behavior are not hidden noise. They are part of the production proof trail.

For this slice, do not invent actual failures. Instead:

- show the verified golden workflow
- show where failures, retries, and fallbacks would appear
- show that B2 rehydrate works without provider rerun for the verified golden run
- keep the truth boundary explicit

## Purpose

Expose a judge-facing Failure-as-Proof Timeline surface.

A judge should understand:

- what happened in the golden workflow
- which proof surfaces exist
- where evidence lives
- where operational failures, retries, and fallbacks would be recorded
- why durable B2 rehydrate matters
- what is verified evidence vs local contract proof vs future failure-handling model
- why this is a real production workflow, not a shallow MVP

Expected judge path:

Judge Cockpit -> Failure-as-Proof Timeline -> B2 Rehydrate Comparison -> Manifest Verification Panel -> B2 Evidence Explorer -> Genblaze Pipeline Graph -> Public Passport

## Current Verified Base

Use only checked-in evidence and verified golden values.

Relevant evidence sources:

- docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json
- docs/evidence/demo/golden-demo-run.json
- docs/evidence/ps-025/public-durable-passport-unlock-smoke.json
- docs/evidence/ps-026/b2-evidence-explorer-smoke.json
- docs/evidence/ps-027/genblaze-pipeline-graph-smoke.json
- docs/evidence/ps-028/manifest-verification-panel-smoke.json
- docs/evidence/ps-029/b2-rehydrate-comparison-smoke.json

Verified golden values:

- run_id: run_89d967f9000045efa22ed4cc78cfa67f
- campaign_id: camp_bea5161faa6244079d2ee01ce445c259
- archive SHA-256: a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141
- archive URI: https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-021/assets/a6/ad/a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141.json
- rehydrate_source: b2_rehydrated
- provider_calls_during_rehydrate: 0
- no_live_provider_call_during_rehydrate: true

## Non-Negotiable Rules

Do not fake operational failures.

Do not invent provider outages, failed calls, retries, fallback attempts, incident events, or recovery events unless checked-in evidence proves them.

Do not claim live production monitoring unless implemented.

Do not call providers.

Do not fetch arbitrary B2 objects through untrusted input.

Do not broaden public durable-read scope.

Do not claim browser-side B2 byte verification unless implemented and validated.

Do not claim public deployment verification unless actually tested.

Do not claim legal authenticity, C2PA authenticity, human authorship, semantic truth, tamper-proof storage, Object Lock, enterprise auth, or production security unless actually implemented.

Do not modify historical evidence JSON under PS-019/020/021/024/025/026/027/028/029.

Do not modify historical smoke scripts PS-019 through PS-029.

Do not expose secrets.

## Required Discovery

Before implementation, inspect:

- specs/39-ps-030-failure-as-proof-timeline.md
- docs/roadmap/proofstudio-winning-implementation-roadmap-2026-06-29.md
- docs/evidence/demo/golden-demo-run.json
- docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json
- docs/evidence/ps-025/public-durable-passport-unlock-smoke.json
- docs/evidence/ps-026/b2-evidence-explorer-smoke.json
- docs/evidence/ps-027/genblaze-pipeline-graph-smoke.json
- docs/evidence/ps-028/manifest-verification-panel-smoke.json
- docs/evidence/ps-029/b2-rehydrate-comparison-smoke.json
- scripts/ps029_b2_rehydrate_comparison_smoke.py
- scripts/ps028_manifest_verification_panel_smoke.py
- scripts/ps027_genblaze_pipeline_graph_smoke.py
- scripts/ps026_b2_evidence_explorer_smoke.py
- scripts/ps025_public_durable_passport_unlock_smoke.py
- scripts/ps024_golden_demo_run_pinning_smoke.py
- scripts/ps023_judge_cockpit_home_smoke.py
- apps/web/src/App.tsx
- apps/web/src/JudgeCockpitHome.tsx
- apps/web/src/B2RehydrateComparison.tsx
- apps/web/src/ManifestVerificationPanel.tsx
- apps/web/src/B2EvidenceExplorer.tsx
- apps/web/src/GenblazePipelineGraph.tsx
- apps/web/src/PublicPassportPage.tsx
- existing shared frontend evidence/data files

## Required Product Surface

Implement a dedicated frontend route:

- /failure-timeline

Preferred files:

- apps/web/src/FailureAsProofTimeline.tsx
- apps/web/src/failureAsProofTimeline.ts

Frontend-only is preferred.

No new API endpoint is required unless a real need is justified.

## Required Timeline Content

The timeline must include these evidence-backed stages:

1. Golden run identity established
2. Provider routing / orchestration path recorded
3. Generation / provenance path captured
4. B2 archive created
5. Golden manifest pinned
6. Public passport contract unlocked locally
7. B2 Evidence Explorer surface created
8. Genblaze Pipeline Graph surface created
9. Manifest Verification Panel confirms consistency
10. B2 Rehydrate Comparison confirms durable rehydrate without provider rerun
11. Public deployment pending remains explicit

Required visible proof fields:

- run_id
- campaign_id
- archive_uri
- archive_sha256
- rehydrate_source
- provider_calls_during_rehydrate
- no_live_provider_call_during_rehydrate

## Required Failure-as-Proof / Failure Theater Section

The page must include a visible section titled:

- Failure-as-Proof

It must explain:

- traditional tools hide failed/skipped attempts and provider instability
- ProofStudio treats operational events as auditable workflow evidence
- captured failures, retries, and fallbacks would appear in this timeline
- the verified golden run currently proves durable B2 rehydrate with zero provider calls
- no actual provider failure/fallback is claimed unless evidence exists

Required visible language:

- No fake failures are claimed.
- This timeline shows where captured failures, retries, and fallbacks would appear.
- For the verified golden run, rehydrate uses B2-backed evidence with zero provider calls.

## Required Archive / Rehydrate Lab Foundation

The page must include a section or card that connects to Archive / Rehydrate Lab direction.

It must show:

- archive URI
- archive SHA-256
- rehydrate source
- provider calls during rehydrate = 0
- no live provider call during rehydrate = true
- link to /b2-rehydrate-comparison

This is not a full lab yet. It is the timeline foundation for later PS-031/043 work.

## Required CTA Changes

Update navigation so judges can reach the Failure-as-Proof Timeline.

Required:

- Judge Cockpit has a clear CTA to /failure-timeline
- Failure Timeline links to:
  - /b2-rehydrate-comparison
  - /manifest-verification
  - /b2-evidence
  - /genblaze-pipeline
  - /passport/run_89d967f9000045efa22ed4cc78cfa67f
  - /
- B2 Rehydrate Comparison may link to /failure-timeline if low-risk
- Manifest Verification Panel may link to /failure-timeline if low-risk
- No broken internal links

## Required Truth Boundary

The timeline must distinguish:

- checked-in evidence
- durable B2 archive proof
- B2 rehydrate proof
- local public passport contract proof
- inferred product explanation
- future/hypothetical failure-handling model
- public deployment pending

Allowed claims:

- checked-in evidence records B2 rehydrate proof
- checked-in evidence records zero provider calls during rehydrate
- checked-in evidence agrees on archive URI and SHA-256
- ProofStudio can present operational workflow steps as evidence-backed timeline entries
- future provider failures, retries, and fallbacks would be represented in this model if captured by evidence

Forbidden claims:

- actual provider failure occurred unless evidence proves it
- actual fallback occurred unless evidence proves it
- the timeline proves semantic truth of media
- the timeline proves legal authenticity
- the timeline proves human authorship
- the timeline proves C2PA authenticity
- the timeline proves Object Lock or tamper-proof storage
- the browser fetched and hashed the B2 object unless implemented
- public deployment is verified unless tested

## Required Evidence

Create:

- docs/evidence/ps-030/failure-as-proof-timeline-smoke.json

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
- timeline_sources_verified
- timeline_events_verified
- failure_as_proof_surface_verified
- failure_theater_visible
- archive_rehydrate_lab_foundation_visible
- no_provider_rerun_story_visible
- no_fake_failure_claims
- truth_boundary_present
- source_ps021_evidence
- source_ps024_manifest
- source_ps025_evidence
- source_ps026_evidence
- source_ps027_evidence
- source_ps028_evidence
- source_ps029_evidence
- source_implementation_roadmap
- frontend_surface_verified
- api_surface_verified
- no_provider_call
- no_broad_b2_read
- no_prior_slice_evidence_modified
- public_deployment_pending
- checked_at

## Required Proof Doc

Create:

- docs/ps-030-failure-as-proof-timeline-proof.md

The proof doc must include:

- roadmap alignment
- implementation-roadmap commitment alignment
- old-window/out-of-the-box idea implemented
- product surface chosen
- files changed
- route/CTA map
- timeline source list
- timeline event list
- Failure-as-Proof explanation
- Failure Theater explanation
- Archive / Rehydrate Lab foundation explanation
- no-fake-failure confirmation
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

- scripts/ps030_failure_as_proof_timeline_smoke.py

The smoke script must validate:

1. Failure-as-Proof Timeline surface exists
2. route /failure-timeline exists
3. Judge Cockpit links to the timeline
4. timeline links to B2 Rehydrate Comparison
5. timeline links to Manifest Verification Panel
6. timeline links to B2 Evidence Explorer
7. timeline links to Genblaze Pipeline Graph
8. timeline links to golden passport
9. required timeline sources are present
10. required timeline events are present
11. implementation roadmap is referenced
12. run_id matches across PS-021/024/025/026/027/028/029 sources
13. campaign_id matches across PS-021/024/025/026/027/028/029 sources
14. archive URI matches across PS-021/024/025/026/027/028/029 sources
15. archive SHA-256 matches across PS-021/024/025/026/027/028/029 sources
16. rehydrate_source equals b2_rehydrated
17. provider_calls_during_rehydrate equals 0
18. no_live_provider_call_during_rehydrate is true
19. no-provider-rerun story is visible
20. Failure-as-Proof section is visible
21. Failure Theater / failure placement model is visible
22. Archive / Rehydrate Lab foundation is visible
23. no fake actual failure/fallback/outage claim is introduced
24. truth boundary is present
25. no provider call is introduced
26. no broad B2 read is introduced
27. no secrets
28. no forbidden affirmative claims
29. no prior-slice evidence is modified
30. PS-029 smoke still passes through snapshot/restore protection if needed
31. PS-028 smoke still passes through snapshot/restore protection if needed
32. PS-027 smoke still passes through snapshot/restore protection if needed
33. PS-026 smoke still passes through snapshot/restore protection if needed
34. PS-025 smoke still passes through snapshot/restore protection if needed
35. PS-024 smoke still passes
36. PS-023 smoke still passes
37. frontend typecheck/build passes if frontend changed

Important:

PS-030 smoke must preserve prior-slice evidence exactly.

If it runs prior smokes that write evidence, snapshot/restore prior evidence files or use safe index handling so the working tree remains clean outside PS-030 files.

Do not modify prior smoke scripts.

Do not add brittle duplicate inline product scanners to final commit gates if canonical smoke already validates the product surface.

## Expected Allowed Files

Implementation may modify only files needed for PS-030.

Likely allowed files:

- apps/web/src/App.tsx
- apps/web/src/JudgeCockpitHome.tsx
- optional apps/web/src/B2RehydrateComparison.tsx
- optional apps/web/src/ManifestVerificationPanel.tsx
- optional apps/web/src/B2EvidenceExplorer.tsx
- optional apps/web/src/GenblazePipelineGraph.tsx
- optional apps/web/src/PublicPassportPage.tsx
- optional apps/web/src/styles.css
- new apps/web/src/FailureAsProofTimeline.tsx
- optional apps/web/src/failureAsProofTimeline.ts
- docs/evidence/ps-030/failure-as-proof-timeline-smoke.json
- docs/ps-030-failure-as-proof-timeline-proof.md
- scripts/ps030_failure_as_proof_timeline_smoke.py

Do not modify:

- historical evidence JSON under PS-019/020/021/024/025/026/027/028/029
- historical smoke scripts PS-019 through PS-029
- provider code unless a real bug is found and explained before commit
- backend API unless necessary and justified
- deployment config
- unrelated files

## Backend Validation Environment Rule

Any PS-030 validation that imports backend/API code must run with:

- source .venv/bin/activate
- export PYTHONPATH="$PWD/src"

Do not run python -m pip install -e . from repo root.

## Validation Requirements

Before commit, run:

- PS-030 smoke script
- PS-029 smoke script, through snapshot/restore protection if needed
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

PS-030 is accepted only if:

1. Judges can reach a clear Failure-as-Proof Timeline surface.
2. The timeline explains ProofStudio as a production workflow, not an image generator.
3. The timeline includes required sources.
4. The timeline includes required events.
5. Failure-as-Proof is visible and useful.
6. Failure Theater / failure placement model is visible.
7. Archive / Rehydrate Lab foundation is visible.
8. The timeline shows provider calls during rehydrate equal zero.
9. The timeline shows no live provider call during rehydrate is true.
10. No fake actual failure/fallback/outage is claimed.
11. Verified values match PS-021/PS-024/PS-025/PS-026/PS-027/PS-028/PS-029 evidence.
12. No provider call is introduced.
13. No broad B2 read is introduced.
14. No prior-slice evidence is modified.
15. Truth boundary remains visible.
16. PS-030 smoke passes.
17. PS-029, PS-028, PS-027, PS-026, PS-025, PS-024, and PS-023 regressions pass.
18. Final working tree contains only PS-030 files before commit.

## Failure Conditions

Fail the slice if:

- timeline is decorative but not evidence-backed
- timeline omits required evidence sources
- timeline omits required events
- timeline claims actual failures/fallbacks without evidence
- timeline claims no provider rerun without evidence
- timeline claims browser-side B2 byte verification without implementing it
- timeline claims certification/authenticity not implemented
- timeline claims public deployment success without verification
- timeline introduces provider calls
- timeline introduces broad B2 reads
- prior-slice evidence is modified
- archive URI/hash is copied incorrectly
- truth boundary is removed or weakened
- forbidden claims are introduced
- unrelated files are changed

## Next Slice After PS-030

PS-031 — Export Campaign Pack v2 / Judge Evidence Pack
