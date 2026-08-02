# PS-034 — Lineage + Comparison Lab

Status: Spec
Date: 2026-06-30
Base branch: `ps-033/provider-decision-intelligence`

## Product Thesis

PS-034 implements the next hardened product module after PS-033.

It must not invent variant families, model results, provider swaps, or reruns that are not captured in evidence.

It must create a real comparison workspace that helps designers, marketers, reviewers, clients, and judges understand:

- what lineage exists for the verified golden run
- what can be compared from checked-in evidence
- what manifest fields prove continuity
- where model audition results would appear
- where provider swap reruns would appear
- where variant families would appear
- what is verified versus planned or not captured

ProofStudio should feel like a creative operations product that can support real campaign iteration, not a single-output demo.

## Roadmap Alignment

PS-034 follows:

- `docs/roadmap/proofstudio-winning-implementation-roadmap-2026-06-29.md`
- `docs/roadmap/ps-031a-hardened-product-modules-correction.md`

PS-031A says PS-034 should implement:

- Lineage + Comparison Lab

This hardened product module merges:

- Model Audition Board
- Manifest Diff
- Provider Swap Re-run
- Variant Family Tree

## User Job

A designer, marketer, reviewer, client, or judge should be able to open one lab and answer:

- What is the golden run?
- What artifact lineage is verified?
- Which manifest fields can be compared?
- Is there more than one real variant in checked-in evidence?
- Which comparison slots are empty because no rerun evidence exists yet?
- How would a provider swap rerun be evaluated later?
- How would a model audition board work without faking results?
- What is the relationship between campaign, run, manifest, archive, rehydrate, passport, evidence pack, and review?
- Which proof surface should I open next?

## Current Verified Base

PS-034 must preserve and reuse the verified golden chain:

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
- `specs/42-ps-033-provider-decision-intelligence.md`
- `specs/41-ps-032-operations-cockpit-flight-recorder-v2.md`
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
- `docs/evidence/ps-032/operations-cockpit-flight-recorder-v2-smoke.json`
- `docs/evidence/ps-033/provider-decision-intelligence-smoke.json`

### Existing Product Surfaces

- `apps/web/src/App.tsx`
- `apps/web/src/JudgeCockpitHome.tsx`
- `apps/web/src/ProviderDecisionIntelligence.tsx`
- `apps/web/src/providerDecisionIntelligence.ts`
- `apps/web/src/OperationsCockpit.tsx`
- `apps/web/src/operationsCockpit.ts`
- `apps/web/src/JudgeEvidencePack.tsx`
- `apps/web/src/judgeEvidencePack.ts`
- `apps/web/src/FailureAsProofTimeline.tsx`
- `apps/web/src/B2RehydrateComparison.tsx`
- `apps/web/src/ManifestVerificationPanel.tsx`
- `apps/web/src/B2EvidenceExplorer.tsx`
- `apps/web/src/GenblazePipelineGraph.tsx`
- `apps/web/src/PublicPassportPage.tsx`
- `apps/web/src/styles.css`

### Provider / Router / Manifest Sources

Inspect if present:

- provider router implementation files
- provider router tests
- provider fallback docs
- provider inventory docs
- Genblaze orchestration code
- manifest-generation code
- archive/rehydrate code
- manifest verification code
- no-key fallback code or docs
- Pollinations fallback code or docs
- Cloudflare Workers AI proof code or docs

If a source does not exist, do not invent it. Mark the missing item honestly in limitations.

### Smoke / Regression Patterns

- `scripts/ps033_provider_decision_intelligence_smoke.py`
- `scripts/ps032_operations_cockpit_flight_recorder_smoke.py`
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

- `/lineage-comparison-lab`

Preferred files:

- `apps/web/src/LineageComparisonLab.tsx`
- `apps/web/src/lineageComparisonLab.ts`

Update:

- `apps/web/src/App.tsx`
- `apps/web/src/JudgeCockpitHome.tsx`
- `apps/web/src/OperationsCockpit.tsx`
- `apps/web/src/ProviderDecisionIntelligence.tsx`
- `apps/web/src/JudgeEvidencePack.tsx`
- `apps/web/src/styles.css`

Optional low-risk backlinks from:

- `apps/web/src/FailureAsProofTimeline.tsx`
- `apps/web/src/B2RehydrateComparison.tsx`
- `apps/web/src/ManifestVerificationPanel.tsx`
- `apps/web/src/B2EvidenceExplorer.tsx`
- `apps/web/src/GenblazePipelineGraph.tsx`
- `apps/web/src/PublicPassportPage.tsx`

Frontend-only preferred.

Do not add a backend endpoint unless truly required and justified.

Do not modify provider code, manifest code, archive code, or backend API in PS-034 unless a blocking bug is found and explained.

## Required Lineage + Comparison Lab Sections

The `/lineage-comparison-lab` page must include:

### 1. Lab Identity

Visible labels:

- `Lineage + Comparison Lab`
- `Model Audition Board`
- `Manifest Diff`
- `Provider Swap Re-run`
- `Variant Family Tree`
- `PS-034`
- run_id
- campaign_id
- public deployment pending

### 2. Lineage Summary

Show a compact lineage summary:

- campaign identity
- golden run identity
- archive status
- manifest status
- rehydrate status
- passport status
- evidence pack status
- comparison readiness
- variant family status
- provider swap status

If only one verified run exists, say so honestly.

Required exact truth line:

`Only one verified golden run is available in checked-in evidence.`

### 3. Variant Family Tree

Show a clear variant family view.

It may be a card/tree layout, not a graph library.

Required nodes:

- Campaign
- Golden Run
- Asset / Manifest
- B2 Archive
- Rehydrated Evidence
- Public Passport
- Judge Evidence Pack
- Review / Next Action

Required relationship labels:

- owns
- generated
- archived_to
- rehydrated_from
- exposes
- exports
- awaits_review

If additional variants are not present, show empty slots as:

- `future variant slot`
- `not captured in checked-in evidence`

Do not invent variant IDs, model outputs, or provider reruns.

### 4. Manifest Diff

Create a manifest comparison panel.

For PS-034, compare the known golden manifest/evidence fields against the rehydrated/archive proof fields where available.

Required fields:

- run_id
- campaign_id
- archive_uri
- archive_sha256
- rehydrate_source
- provider_calls_during_rehydrate
- no_live_provider_call_during_rehydrate
- public_deployment_pending

Each field must include:

- left/source value
- right/comparison value
- match status
- evidence source
- truth class

If a field cannot be compared because one side is not captured, show:

- `not captured in checked-in evidence`

Do not invent missing manifest fields.

### 5. Model Audition Board

Create an audition board that shows how multiple model candidates would be compared.

Required columns:

- candidate
- provider / model role
- modality
- evidence status
- quality review status
- cost/time status
- proof status
- decision

For the golden run, if selected provider/model is not captured, say:

- `selected provider/model not captured in checked-in evidence`

For future slots, mark:

- `audition slot not run`
- `not captured in checked-in evidence`

Do not invent model scores, quality scores, cost scores, or winner labels.

### 6. Provider Swap Re-run Planner

Create a planner section for rerunning the same brief with a different provider.

Required policy steps:

1. keep campaign_id
2. create new run_id
3. preserve source prompt/brief if available
4. route through provider decision policy
5. capture new asset/manifest
6. archive to B2
7. compare manifest diff
8. attach to variant family
9. update review/export state

This is a planner, not an executed rerun.

Required exact truth line:

`No provider swap rerun is claimed for the verified golden run.`

### 7. Comparison Readiness Checklist

Show whether the system has enough evidence to compare variants.

Required checklist items:

- golden run exists
- B2 archive exists
- manifest hash exists
- rehydrate proof exists
- provider calls during rehydrate captured
- evidence pack exists
- operations cockpit exists
- provider decision policy exists
- second real variant exists
- model scores captured
- measured cost captured
- measured latency captured
- review decision captured

Mark missing items honestly.

### 8. Designer / Marketer Interpretation

This must be useful to non-technical users.

Add plain-language explanations for:

- why lineage matters
- why comparing variants helps campaigns
- why manifest diff matters
- how provider swaps help creative teams
- when to rerun with another model
- when to export the evidence pack
- why missing variant data is not a failure

### 9. Action Rail

Add CTAs to:

- `/provider-decision-intelligence`
- `/operations-cockpit`
- `/evidence-pack`
- `/failure-timeline`
- `/b2-rehydrate-comparison`
- `/manifest-verification`
- `/b2-evidence`
- `/genblaze-pipeline`
- `/passport/run_89d967f9000045efa22ed4cc78cfa67f`
- `/`

### 10. Truth Boundary

Must clearly say what this page does and does not prove.

It may claim:

- it summarizes checked-in lineage evidence
- it compares known manifest/proof fields
- it shows where future variants and provider swaps would appear
- it shows only one verified golden run if that is true
- it helps creative teams plan comparison workflows
- it shows pending gaps honestly

It must not claim:

- multiple real variants unless captured
- completed provider swap reruns unless captured
- model audition results unless captured
- actual quality scores unless captured
- actual winner labels unless captured
- actual spend unless captured
- actual latency unless captured
- legal authenticity
- semantic truth
- human authorship
- C2PA authenticity
- Object Lock / tamper-proof storage
- browser-side B2 byte verification
- public deployment verification
- enterprise security

### 11. Limitations

Must include:

- no live provider call in PS-034
- no provider swap rerun executed
- no second real variant captured unless evidence exists
- no model score captured unless evidence exists
- no broad B2 read
- no live pricing API
- no measured billing unless present in checked-in evidence
- no measured latency unless present in checked-in evidence
- public deployment pending
- checked-in evidence and documented policy only
- no invented variant events

## Required Data Shape

In `lineageComparisonLab.ts`, create a structured data model with at least:

- lab_id
- lab_version
- generated_from
- run_id
- campaign_id
- archive_uri
- archive_sha256
- rehydrate_source
- provider_calls_during_rehydrate
- no_live_provider_call_during_rehydrate
- public_deployment_pending
- lineage_summary
- variant_family_tree
- manifest_diff
- model_audition_board
- provider_swap_rerun_planner
- comparison_readiness_checklist
- designer_marketer_interpretation
- action_routes
- truth_boundary
- limitations
- source_evidence

## Required CTA Changes

Add a visible link to `/lineage-comparison-lab` from:

- Judge Cockpit Home
- Operations Cockpit
- Provider Decision Intelligence
- Judge Evidence Pack

Optional backlinks from:

- Failure-as-Proof Timeline
- B2 Rehydrate Comparison
- Manifest Verification Panel
- B2 Evidence Explorer
- Genblaze Pipeline Graph
- Public Passport

The Lineage + Comparison Lab page must link back to:

- `/`
- `/provider-decision-intelligence`
- `/operations-cockpit`
- `/evidence-pack`

## Required Evidence

Create:

- `docs/evidence/ps-034/lineage-comparison-lab-smoke.json`

Evidence JSON must include:

- ok
- route_or_surface
- lab_id
- lab_version
- run_id
- campaign_id
- archive_uri
- archive_sha256
- rehydrate_source
- provider_calls_during_rehydrate
- no_live_provider_call_during_rehydrate
- public_deployment_pending
- lineage_comparison_surface_verified
- lab_identity_visible
- lineage_summary_visible
- variant_family_tree_verified
- manifest_diff_verified
- model_audition_board_visible
- provider_swap_rerun_planner_visible
- comparison_readiness_checklist_visible
- designer_marketer_interpretation_visible
- action_rail_verified
- truth_boundary_present
- limitations_present
- only_one_verified_run_disclosed
- no_provider_swap_rerun_claim
- no_second_variant_claim_without_evidence
- no_model_score_claim_without_evidence
- no_winner_claim_without_evidence
- no_actual_spend_claim_without_evidence
- no_actual_latency_claim_without_evidence
- source_ps021_evidence
- source_ps024_manifest
- source_ps025_evidence
- source_ps026_evidence
- source_ps027_evidence
- source_ps028_evidence
- source_ps029_evidence
- source_ps030_evidence
- source_ps031_evidence
- source_ps032_evidence
- source_ps033_evidence
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

- `docs/ps-034-lineage-comparison-lab-proof.md`

Proof doc must include:

- PS-031A alignment
- hardened product module alignment
- old-window idea consolidation
- product surface chosen
- files changed
- route/CTA map
- Lineage + Comparison Lab sections implemented
- variant family tree explanation
- manifest diff explanation
- model audition board explanation
- provider swap rerun planner explanation
- comparison readiness explanation
- designer/marketer value
- source evidence list
- proof chain explanation
- no-provider-call confirmation
- no-broad-B2-read confirmation
- no-provider-swap-rerun claim confirmation
- no-second-variant-without-evidence confirmation
- no-model-score-without-evidence confirmation
- no-winner-without-evidence confirmation
- no-actual-spend-without-evidence confirmation
- no-actual-latency-without-evidence confirmation
- no-raw-media-byte confirmation
- no-prior-slice-evidence-mutation confirmation
- truth boundary
- limitations
- validation commands
- smoke result

## Required Smoke Script

Create:

- `scripts/ps034_lineage_comparison_lab_smoke.py`

Smoke must validate at least:

1. Lineage Comparison Lab component exists.
2. Lineage Comparison Lab data module exists.
3. route `/lineage-comparison-lab` exists.
4. Judge Cockpit links to `/lineage-comparison-lab`.
5. Operations Cockpit links to `/lineage-comparison-lab`.
6. Provider Decision Intelligence links to `/lineage-comparison-lab`.
7. Judge Evidence Pack links to `/lineage-comparison-lab`.
8. Lineage Comparison Lab page links to `/`.
9. Lineage Comparison Lab page links to `/provider-decision-intelligence`.
10. Lineage Comparison Lab page links to `/operations-cockpit`.
11. Lineage Comparison Lab page links to `/evidence-pack`.
12. Lineage Comparison Lab page links to Failure Timeline.
13. Lineage Comparison Lab page links to B2 Rehydrate Comparison.
14. Lineage Comparison Lab page links to Manifest Verification.
15. Lineage Comparison Lab page links to B2 Evidence Explorer.
16. Lineage Comparison Lab page links to Genblaze Pipeline Graph.
17. Lineage Comparison Lab page links to golden passport.
18. lab identity visible.
19. lineage summary visible.
20. required golden values visible or in data.
21. variant family tree exists.
22. required variant family nodes exist.
23. required variant family relationship labels exist.
24. future variant slot is honestly labeled.
25. manifest diff exists.
26. manifest diff includes required fields.
27. manifest diff shows match status.
28. manifest diff handles missing fields honestly.
29. model audition board exists.
30. model audition board required columns exist.
31. selected provider/model not captured is disclosed if not present.
32. audition slots are not claimed as run.
33. provider swap rerun planner exists.
34. provider swap steps exist.
35. exact line `No provider swap rerun is claimed for the verified golden run.` exists.
36. comparison readiness checklist exists.
37. checklist includes existing and missing items.
38. designer/marketer interpretation exists.
39. action rail exists.
40. truth boundary exists.
41. limitations exists.
42. exact line `Only one verified golden run is available in checked-in evidence.` exists.
43. source evidence includes PS-021.
44. source evidence includes PS-024.
45. source evidence includes PS-025.
46. source evidence includes PS-026.
47. source evidence includes PS-027.
48. source evidence includes PS-028.
49. source evidence includes PS-029.
50. source evidence includes PS-030.
51. source evidence includes PS-031.
52. source evidence includes PS-032.
53. source evidence includes PS-033.
54. source evidence includes PS-031A.
55. run_id matches known golden run.
56. campaign_id matches known golden campaign.
57. archive URI matches known archive.
58. archive SHA-256 matches known archive hash.
59. rehydrate_source equals `b2_rehydrated`.
60. provider_calls_during_rehydrate equals `0`.
61. no_live_provider_call_during_rehydrate is true.
62. no provider call introduced.
63. no broad B2 read introduced.
64. no fake provider failure claim introduced.
65. no raw media byte claim introduced.
66. no second variant claim without evidence.
67. no provider swap rerun claim without evidence.
68. no model score claim without evidence.
69. no winner claim without evidence.
70. no actual spend claim without evidence.
71. no actual latency claim without evidence.
72. no forbidden authenticity/security claims introduced.
73. no secrets.
74. no prior-slice evidence modified.
75. PS-033 smoke still passes using snapshot/restore if needed.
76. PS-032 smoke still passes using snapshot/restore if needed.
77. PS-031 smoke still passes using snapshot/restore if needed.
78. PS-030 smoke still passes using snapshot/restore if needed.
79. PS-029 smoke still passes using snapshot/restore if needed.
80. PS-028 smoke still passes using snapshot/restore if needed.
81. PS-027 smoke still passes using snapshot/restore if needed.
82. PS-026 smoke still passes using snapshot/restore if needed.
83. PS-025 smoke still passes using snapshot/restore if needed.
84. PS-024 smoke still passes.
85. PS-023 smoke still passes.
86. frontend typecheck/build passes if frontend changed.

The smoke script must leave the working tree clean except for PS-034 files.

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
- `apps/web/src/OperationsCockpit.tsx`
- `apps/web/src/ProviderDecisionIntelligence.tsx`
- `apps/web/src/JudgeEvidencePack.tsx`
- optional `apps/web/src/FailureAsProofTimeline.tsx`
- optional `apps/web/src/B2RehydrateComparison.tsx`
- optional `apps/web/src/ManifestVerificationPanel.tsx`
- optional `apps/web/src/B2EvidenceExplorer.tsx`
- optional `apps/web/src/GenblazePipelineGraph.tsx`
- optional `apps/web/src/PublicPassportPage.tsx`
- `apps/web/src/styles.css`
- new `apps/web/src/LineageComparisonLab.tsx`
- new `apps/web/src/lineageComparisonLab.ts`
- `docs/evidence/ps-034/lineage-comparison-lab-smoke.json`
- `docs/ps-034-lineage-comparison-lab-proof.md`
- `scripts/ps034_lineage_comparison_lab_smoke.py`

Do not modify:

- historical evidence JSON under PS-019/020/021/024/025/026/027/028/029/030/031/032/033
- historical smoke scripts PS-019 through PS-033
- provider code unless a blocking bug is found and explained
- manifest/archive code unless a blocking bug is found and explained
- deployment config
- backend API unless necessary and justified
- unrelated docs

## Acceptance Criteria

PS-034 is accepted only when:

- spec is implemented as a real lineage/comparison lab, not a decorative matrix
- `/lineage-comparison-lab` route works
- lab identity is visible
- lineage summary is visible
- variant family tree is visible
- manifest diff is visible
- model audition board is visible
- provider swap rerun planner is visible
- comparison readiness checklist is visible
- designer/marketer interpretation is visible
- all required proof routes are linked
- PS-031A consolidation is referenced
- only one verified golden run is honestly disclosed if true
- no fake variants are claimed
- no provider swap rerun is claimed without evidence
- no model score is claimed without evidence
- no winner is claimed without evidence
- no actual spend is claimed without evidence
- no actual latency is claimed without evidence
- no provider calls are introduced
- no broad B2 reads are introduced
- no forbidden authenticity/security claims are introduced
- PS-034 smoke passes
- PS-033 through PS-023 regressions pass
- frontend typecheck/build pass
- no prior-slice evidence is modified
- final git status contains only expected PS-034 files before commit

## Failure Conditions

Reject the slice if it:

- builds another disconnected decorative page
- ignores PS-031A
- renumbers roadmap slices
- invents variant IDs
- invents model audition results
- invents model scores
- invents winner labels
- invents provider swap reruns
- invents actual spend
- invents actual latency
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
- changes unrelated backend/provider/manifest/archive files
- fails frontend typecheck/build

## Next Slice

After PS-034 is accepted, the next hardened module should be:

- PS-035 — Review + Approval Workspace
