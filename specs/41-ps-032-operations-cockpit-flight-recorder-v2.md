# PS-032 — Operations Cockpit / Flight Recorder v2

Status: Spec
Date: 2026-06-29
Base branch: `ps-031a/hardened-product-modules-roadmap`

## Product Thesis

PS-032 implements the first major hardened product module after PS-031A.

It must not be another disconnected proof page.

It must become the operating cockpit that helps designers, marketers, reviewers, clients, and judges understand what happened across a ProofStudio run without reading raw JSON.

ProofStudio should feel like an AI media operations product, not a technical demo.

## Roadmap Alignment

PS-032 follows:

- `docs/roadmap/proofstudio-winning-implementation-roadmap-2026-06-29.md`
- `docs/roadmap/ps-031a-hardened-product-modules-correction.md`

PS-031A says PS-032 should implement:

- Operations Cockpit / Flight Recorder v2

This hardened product module merges:

- Mission Control
- Flight Recorder
- Failure-as-Proof Timeline
- Failure Theater
- Evidence Graph
- pipeline lifecycle view

## User Job

A creative operator, marketer, client, or judge should be able to open one cockpit and answer:

- What campaign/run am I looking at?
- What happened first, next, and last?
- Which evidence is checked-in?
- Which evidence points to B2?
- Which evidence points to Genblaze manifest verification?
- Did rehydrate call providers again?
- Where would failures/retries/fallbacks appear?
- What is ready for review/export?
- What is still pending or not claimed?
- Which proof surface should I open next?

## Current Verified Base

PS-032 must preserve and reuse the verified golden chain:

- run_id: `run_89d967f9000045efa22ed4cc78cfa67f`
- campaign_id: `camp_bea5161faa6244079d2ee01ce445c259`
- archive_uri: `https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-021/assets/a6/ad/a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141.json`
- archive_sha256: `a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141`
- rehydrate_source: `b2_rehydrated`
- provider_calls_during_rehydrate: `0`
- no_live_provider_call_during_rehydrate: `true`
- public_deployment_pending: `true`

## Required Discovery

Before implementation, inspect:

### Roadmap / Spec Sources

- `docs/roadmap/proofstudio-winning-implementation-roadmap-2026-06-29.md`
- `docs/roadmap/ps-031a-hardened-product-modules-correction.md`
- `specs/40-ps-031-export-campaign-pack-v2.md`

### Evidence Sources

- `docs/evidence/demo/golden-demo-run.json`
- `docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json`
- `docs/evidence/ps-025/public-durable-passport-unlock-smoke.json`
- `docs/evidence/ps-026/b2-evidence-explorer-smoke.json`
- `docs/evidence/ps-027/genblaze-pipeline-graph-smoke.json`
- `docs/evidence/ps-028/manifest-verification-panel-smoke.json`
- `docs/evidence/ps-029/b2-rehydrate-comparison-smoke.json`
- `docs/evidence/ps-030/failure-as-proof-timeline-smoke.json`
- `docs/evidence/ps-031/export-campaign-pack-v2-smoke.json`

### Existing Product Surfaces

- `apps/web/src/App.tsx`
- `apps/web/src/JudgeCockpitHome.tsx`
- `apps/web/src/JudgeEvidencePack.tsx`
- `apps/web/src/judgeEvidencePack.ts`
- `apps/web/src/FailureAsProofTimeline.tsx`
- `apps/web/src/failureAsProofTimeline.ts`
- `apps/web/src/B2RehydrateComparison.tsx`
- `apps/web/src/ManifestVerificationPanel.tsx`
- `apps/web/src/B2EvidenceExplorer.tsx`
- `apps/web/src/GenblazePipelineGraph.tsx`
- `apps/web/src/PublicPassportPage.tsx`
- `apps/web/src/styles.css`

### Smoke / Regression Patterns

- `scripts/ps031_export_campaign_pack_v2_smoke.py`
- `scripts/ps030_failure_as_proof_timeline_smoke.py`
- `scripts/ps029_b2_rehydrate_comparison_smoke.py`
- `scripts/ps028_manifest_verification_panel_smoke.py`
- `scripts/ps027_genblaze_pipeline_graph_smoke.py`
- `scripts/ps026_b2_evidence_explorer_smoke.py`
- `scripts/ps025_public_durable_passport_unlock_smoke.py`
- `scripts/ps024_golden_demo_run_pinning_smoke.py`
- `scripts/ps023_judge_cockpit_home_smoke.py`

## Required Product Surface

Add a dedicated route:

- `/operations-cockpit`

Preferred files:

- `apps/web/src/OperationsCockpit.tsx`
- `apps/web/src/operationsCockpit.ts`

Update:

- `apps/web/src/App.tsx`
- `apps/web/src/JudgeCockpitHome.tsx`
- `apps/web/src/JudgeEvidencePack.tsx`
- `apps/web/src/FailureAsProofTimeline.tsx`
- `apps/web/src/styles.css`

Optional low-risk backlinks from:

- `apps/web/src/B2RehydrateComparison.tsx`
- `apps/web/src/ManifestVerificationPanel.tsx`
- `apps/web/src/B2EvidenceExplorer.tsx`
- `apps/web/src/GenblazePipelineGraph.tsx`
- `apps/web/src/PublicPassportPage.tsx`

Frontend-only preferred.

Do not add a backend endpoint unless truly required and justified.

## Required Cockpit Sections

The `/operations-cockpit` page must include:

### 1. Cockpit Identity

Visible labels:

- `Operations Cockpit`
- `Flight Recorder`
- `PS-032`
- run_id
- campaign_id
- public deployment pending

### 2. Run Status Summary

Show a compact operational summary:

- campaign/run identity
- archive status
- manifest status
- rehydrate status
- provider call status during rehydrate
- evidence pack status
- review/export readiness
- pending public deployment

### 3. Operational Phase Map

Show the run as phases.

Required phases:

1. Campaign brief
2. Provider routing / orchestration
3. Media generation attempt
4. Asset and manifest capture
5. Backblaze B2 archive
6. Genblaze manifest verification
7. B2 rehydrate
8. Failure-as-Proof / retry visibility
9. Judge Evidence Pack export
10. Review / next action

Each phase must include:

- title
- status
- truth class
- evidence source
- next route or action

Truth classes should include at least:

- `checked_in_evidence`
- `b2_archive_reference`
- `genblaze_manifest_evidence`
- `rehydrate_proof`
- `local_export_contract`
- `inferred_product_explanation`
- `public_deployment_pending`

### 4. Flight Recorder Timeline

Show an ordered timeline of events that explains the golden run.

Each event must include:

- sequence number
- event title
- event type
- status
- evidence anchor
- route link when available
- truth class

Do not invent real timestamps if not present.

If timestamp is not available, label it honestly as:

- `source evidence order`
- `checked-in evidence order`
- or `not timestamped in checked-in evidence`

### 5. Evidence Graph

Add a clear evidence graph representation.

It does not need to be a canvas or complex graph library.

It may be accessible cards/columns.

Required nodes:

- Campaign
- Run
- Provider Router
- Genblaze Pipeline
- Asset / Manifest
- B2 Archive
- Manifest Verification
- B2 Rehydrate
- Failure-as-Proof Timeline
- Judge Evidence Pack
- Public Passport
- Review / Next Action

Required edges:

- Campaign -> Run
- Run -> Provider Router
- Provider Router -> Genblaze Pipeline
- Genblaze Pipeline -> Asset / Manifest
- Asset / Manifest -> B2 Archive
- Asset / Manifest -> Manifest Verification
- B2 Archive -> B2 Rehydrate
- B2 Rehydrate -> Public Passport
- Failure-as-Proof Timeline -> Judge Evidence Pack
- Judge Evidence Pack -> Review / Next Action

### 6. Failure Theater Slot

Include a section that shows where failures/retries/fallbacks would appear.

Required exact truth line:

`No fake failures are claimed.`

Also include:

`For the verified golden run, rehydrate uses B2-backed evidence with zero provider calls.`

Do not invent provider failures.

### 7. Action Rail

Add CTAs to:

- `/evidence-pack`
- `/failure-timeline`
- `/b2-rehydrate-comparison`
- `/manifest-verification`
- `/b2-evidence`
- `/genblaze-pipeline`
- `/passport/run_89d967f9000045efa22ed4cc78cfa67f`
- `/`

### 8. Designer / Marketer Next Actions

This cockpit must be useful to non-technical users.

Add a section for designers/marketers with next actions:

- review asset proof
- open evidence pack
- inspect rehydrate proof
- verify manifest
- prepare client handoff
- understand disclosure boundary
- continue to review/approval workspace when available

### 9. Truth Boundary

Must clearly say what this cockpit does and does not prove.

It may claim:

- it summarizes checked-in evidence
- it links to B2 archive evidence
- it links to Genblaze manifest evidence
- it shows zero provider calls during rehydrate
- it helps reviewers understand workflow provenance
- it shows pending product gaps honestly

It must not claim:

- legal authenticity
- semantic truth
- human authorship
- C2PA authenticity
- Object Lock / tamper-proof storage
- browser-side B2 byte verification
- public deployment verification
- enterprise security

unless implemented and validated.

### 10. Limitations

Must include:

- no live provider call in PS-032
- no broad B2 read
- no browser-side B2 byte verification
- no raw media byte inspection
- public deployment pending
- checked-in evidence only
- no invented failure events

## Required Data Shape

In `operationsCockpit.ts`, create a structured data model with at least:

- cockpit_id
- cockpit_version
- generated_from
- run_id
- campaign_id
- archive_uri
- archive_sha256
- rehydrate_source
- provider_calls_during_rehydrate
- no_live_provider_call_during_rehydrate
- public_deployment_pending
- phase_map
- flight_recorder_events
- evidence_graph
- action_routes
- designer_marketer_next_actions
- truth_boundary
- limitations
- source_evidence

## Required CTA Changes

Add a visible link to `/operations-cockpit` from:

- Judge Cockpit Home
- Judge Evidence Pack
- Failure-as-Proof Timeline

The Operations Cockpit must link back to:

- `/`
- `/evidence-pack`
- `/failure-timeline`

## Required Evidence

Create:

- `docs/evidence/ps-032/operations-cockpit-flight-recorder-v2-smoke.json`

Evidence JSON must include:

- ok
- route_or_surface
- cockpit_id
- cockpit_version
- run_id
- campaign_id
- archive_uri
- archive_sha256
- rehydrate_source
- provider_calls_during_rehydrate
- no_live_provider_call_during_rehydrate
- public_deployment_pending
- operations_cockpit_surface_verified
- cockpit_identity_visible
- run_status_summary_visible
- phase_map_verified
- flight_recorder_verified
- evidence_graph_verified
- failure_theater_slot_visible
- designer_marketer_next_actions_visible
- action_rail_verified
- truth_boundary_present
- limitations_present
- source_ps021_evidence
- source_ps024_manifest
- source_ps025_evidence
- source_ps026_evidence
- source_ps027_evidence
- source_ps028_evidence
- source_ps029_evidence
- source_ps030_evidence
- source_ps031_evidence
- source_ps031a_roadmap_correction
- frontend_surface_verified
- api_surface_verified
- no_provider_call
- no_broad_b2_read
- no_raw_media_byte_claim
- no_fake_failure_claim
- no_prior_slice_evidence_modified
- checked_at

## Required Proof Doc

Create:

- `docs/ps-032-operations-cockpit-flight-recorder-v2-proof.md`

Proof doc must include:

- PS-031A alignment
- hardened product module alignment
- old-window idea consolidation
- product surface chosen
- files changed
- route/CTA map
- cockpit sections implemented
- phase map explanation
- flight recorder explanation
- evidence graph explanation
- Failure Theater slot explanation
- designer/marketer value
- source evidence list
- proof chain explanation
- no-provider-call confirmation
- no-broad-B2-read confirmation
- no-fake-failure confirmation
- no-raw-media-byte confirmation
- no-prior-slice-evidence-mutation confirmation
- truth boundary
- limitations
- validation commands
- smoke result

## Required Smoke Script

Create:

- `scripts/ps032_operations_cockpit_flight_recorder_smoke.py`

Smoke must validate at least:

1. Operations Cockpit component exists.
2. Operations Cockpit data module exists.
3. route `/operations-cockpit` exists.
4. Judge Cockpit links to `/operations-cockpit`.
5. Judge Evidence Pack links to `/operations-cockpit`.
6. Failure Timeline links to `/operations-cockpit`.
7. Operations Cockpit links to `/`.
8. Operations Cockpit links to `/evidence-pack`.
9. Operations Cockpit links to `/failure-timeline`.
10. Operations Cockpit links to B2 Rehydrate Comparison.
11. Operations Cockpit links to Manifest Verification.
12. Operations Cockpit links to B2 Evidence Explorer.
13. Operations Cockpit links to Genblaze Pipeline Graph.
14. Operations Cockpit links to golden passport.
15. cockpit identity visible.
16. run status summary visible.
17. required golden values visible or in data.
18. phase map exists.
19. all required phases exist.
20. truth classes exist.
21. flight recorder events exist.
22. event sequence exists.
23. timestamp honesty exists when exact timestamps are unavailable.
24. evidence graph exists.
25. required evidence graph nodes exist.
26. required evidence graph edges exist.
27. failure theater slot exists.
28. exact line `No fake failures are claimed.` exists.
29. exact line `For the verified golden run, rehydrate uses B2-backed evidence with zero provider calls.` exists.
30. designer/marketer next actions exist.
31. action rail exists.
32. truth boundary exists.
33. limitations exist.
34. source evidence includes PS-021.
35. source evidence includes PS-024.
36. source evidence includes PS-025.
37. source evidence includes PS-026.
38. source evidence includes PS-027.
39. source evidence includes PS-028.
40. source evidence includes PS-029.
41. source evidence includes PS-030.
42. source evidence includes PS-031.
43. source evidence includes PS-031A.
44. run_id matches known golden run.
45. campaign_id matches known golden campaign.
46. archive URI matches known archive.
47. archive SHA-256 matches known archive hash.
48. rehydrate_source equals `b2_rehydrated`.
49. provider_calls_during_rehydrate equals `0`.
50. no_live_provider_call_during_rehydrate is true.
51. no provider call introduced.
52. no broad B2 read introduced.
53. no fake failure claim introduced.
54. no raw media byte claim introduced.
55. no forbidden authenticity/security claims introduced.
56. no secrets.
57. no prior-slice evidence modified.
58. PS-031 smoke still passes using snapshot/restore if needed.
59. PS-030 smoke still passes using snapshot/restore if needed.
60. PS-029 smoke still passes using snapshot/restore if needed.
61. PS-028 smoke still passes using snapshot/restore if needed.
62. PS-027 smoke still passes using snapshot/restore if needed.
63. PS-026 smoke still passes using snapshot/restore if needed.
64. PS-025 smoke still passes using snapshot/restore if needed.
65. PS-024 smoke still passes.
66. PS-023 smoke still passes.
67. frontend typecheck/build passes if frontend changed.

The smoke script must leave the working tree clean except for PS-032 files.

If prior smokes rewrite evidence, snapshot/restore prior evidence files.

Do not modify prior smoke scripts.

## Backend Validation Environment Rule

If smoke imports backend/API code, run with:

- `source .venv/bin/activate`
- `export PYTHONPATH="$PWD/src"`

Do not run `python -m pip install -e .` from repo root.

## Expected Allowed Files

Implementation should normally touch only:

- `apps/web/src/App.tsx`
- `apps/web/src/JudgeCockpitHome.tsx`
- `apps/web/src/JudgeEvidencePack.tsx`
- `apps/web/src/FailureAsProofTimeline.tsx`
- optional `apps/web/src/B2RehydrateComparison.tsx`
- optional `apps/web/src/ManifestVerificationPanel.tsx`
- optional `apps/web/src/B2EvidenceExplorer.tsx`
- optional `apps/web/src/GenblazePipelineGraph.tsx`
- optional `apps/web/src/PublicPassportPage.tsx`
- `apps/web/src/styles.css`
- new `apps/web/src/OperationsCockpit.tsx`
- new `apps/web/src/operationsCockpit.ts`
- `docs/evidence/ps-032/operations-cockpit-flight-recorder-v2-smoke.json`
- `docs/ps-032-operations-cockpit-flight-recorder-v2-proof.md`
- `scripts/ps032_operations_cockpit_flight_recorder_smoke.py`

Do not modify:

- historical evidence JSON under PS-019/020/021/024/025/026/027/028/029/030/031
- historical smoke scripts PS-019 through PS-031
- provider code
- deployment config
- backend API unless necessary and justified
- unrelated docs

## Acceptance Criteria

PS-032 is accepted only when:

- spec is implemented as a real cockpit, not a marketing page
- `/operations-cockpit` route works
- cockpit identity is visible
- phase map is visible
- flight recorder timeline is visible
- evidence graph is visible
- failure theater slot is visible
- designer/marketer next actions are visible
- all required proof routes are linked
- PS-031A consolidation is referenced
- no fake failures are claimed
- no provider calls are introduced
- no broad B2 reads are introduced
- no forbidden authenticity/security claims are introduced
- PS-032 smoke passes
- PS-031 through PS-023 regressions pass
- frontend typecheck/build pass
- no prior-slice evidence is modified
- final git status contains only expected PS-032 files before commit

## Failure Conditions

Reject the slice if it:

- builds another disconnected decorative page
- ignores PS-031A
- renumbers roadmap slices
- creates fake provider failures
- claims real retry/fallback events without evidence
- calls providers
- reads arbitrary B2 objects
- claims legal authenticity
- claims semantic truth
- claims human authorship
- claims C2PA authenticity
- claims Object Lock / tamper-proof storage
- claims browser-side B2 byte verification
- claims public deployment verification
- claims enterprise security
- mutates prior-slice evidence
- changes prior smoke scripts
- changes unrelated backend/provider files
- fails frontend typecheck/build

## Next Slice

After PS-032 is accepted, the next hardened module should be:

- PS-033 — Provider Decision Intelligence
