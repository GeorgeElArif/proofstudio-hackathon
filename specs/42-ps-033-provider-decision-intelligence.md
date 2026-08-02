# PS-033 — Provider Decision Intelligence

Status: Spec
Date: 2026-06-30
Base branch: `ps-032/operations-cockpit-flight-recorder-v2`

## Product Thesis

PS-033 implements the next hardened product module after PS-032.

It must not be a decorative provider list.

It must explain provider routing decisions in a way designers, marketers, reviewers, clients, and judges can understand.

ProofStudio should answer:

- Why this provider?
- What budget mode is active?
- What is the fallback path?
- What costs or time are known?
- What costs or time are not captured yet?
- What can run with keys?
- What can run without keys?
- What is evidence-backed versus policy/inferred?

This slice must help real creative teams trust routing decisions without reading source code.

## Roadmap Alignment

PS-033 follows:

- `docs/roadmap/proofstudio-winning-implementation-roadmap-2026-06-29.md`
- `docs/roadmap/ps-031a-hardened-product-modules-correction.md`

PS-031A says PS-033 should implement:

- Provider Decision Intelligence

This hardened product module merges:

- Credit-Aware Provider Router
- Provider Budget Modes
- Cost and Time Ledger
- Why This Provider
- Emergency No-Key Mode
- quota / paid / free risk explanation

## User Job

A creative operator, designer, marketer, client, or judge should be able to open one surface and answer:

- Which provider path was selected for the golden run?
- Which provider options are available or planned?
- Which providers require paid keys?
- Which providers can act as emergency no-key fallback?
- What budget mode would choose each path?
- What cost or time information is actually captured?
- What is only a policy classification and not measured billing?
- Why did ProofStudio choose this path?
- What would happen if keys, quota, or provider availability changed?
- Which proof surfaces verify the decision chain?

## Current Verified Base

PS-033 must preserve and reuse the verified golden chain:

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

### Existing Product Surfaces

- `apps/web/src/App.tsx`
- `apps/web/src/JudgeCockpitHome.tsx`
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

### Provider / Router Sources

Inspect if present:

- provider router implementation files
- provider router tests
- provider fallback docs
- provider matrix docs
- Genblaze orchestration code
- no-key fallback code or docs
- Pollinations fallback code or docs
- Cloudflare Workers AI proof code or docs

If a source does not exist, do not invent it. Mark the missing item honestly in limitations.

### Smoke / Regression Patterns

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

- `/provider-decision-intelligence`

Preferred files:

- `apps/web/src/ProviderDecisionIntelligence.tsx`
- `apps/web/src/providerDecisionIntelligence.ts`

Update:

- `apps/web/src/App.tsx`
- `apps/web/src/JudgeCockpitHome.tsx`
- `apps/web/src/OperationsCockpit.tsx`
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

Do not modify provider code in PS-033 unless a blocking bug is found and explained.

## Required Provider Intelligence Sections

The `/provider-decision-intelligence` page must include:

### 1. Provider Decision Identity

Visible labels:

- `Provider Decision Intelligence`
- `Why This Provider`
- `PS-033`
- run_id
- campaign_id
- public deployment pending

### 2. Decision Summary

Show a compact routing summary:

- selected route for the golden proof chain
- provider decision state
- budget mode state
- cost/time ledger state
- fallback state
- emergency no-key mode state
- evidence-backed versus policy/inferred split

If the selected provider is not explicitly available from checked-in evidence, say so honestly.

Do not invent the selected provider.

### 3. Provider Option Matrix

Show a clear provider decision matrix.

Each option must include:

- provider name
- model or role
- modality or output type
- key requirement
- budget class
- fallback role
- evidence status
- risk notes
- truth class

Provider options may include only options supported by existing code/docs/evidence.

If optional providers are documented but not active in the golden run, mark them as documented or planned, not verified for this run.

Truth classes should include at least:

- `checked_in_evidence`
- `documented_provider_option`
- `router_policy`
- `fallback_policy`
- `cost_policy_estimate`
- `not_captured_in_evidence`
- `public_deployment_pending`

### 4. Budget Modes

Show budget modes as routing policies, not live billing facts.

Required modes:

- `free_safe`
- `balanced`
- `quality_max`
- `emergency_no_key`

Each mode must include:

- goal
- preferred route behavior
- fallback behavior
- key/payment dependency
- risk
- what is measured
- what is not measured yet

Do not claim actual billing cost unless measured evidence exists.

### 5. Why This Provider

Create a human-readable explanation panel.

It must answer:

- why this route is acceptable for the golden chain
- what evidence backs the decision
- what is not known from checked-in evidence
- how the system should behave if a provider key is unavailable
- how emergency no-key mode differs from quality mode

### 6. Cost and Time Ledger

Include a ledger-ready section.

It must clearly separate:

- captured values
- not captured values
- future measurement fields

Required fields:

- provider
- model_or_role
- attempt_count
- fallback_count
- provider_calls_during_rehydrate
- estimated_cost_class
- measured_cost
- measured_latency
- evidence_source
- truth_class

If measured cost or latency is not captured, show `not captured in checked-in evidence`.

Do not invent prices, spend, latency, quota usage, or token usage.

### 7. Emergency No-Key Mode

Include a section for no-key or low-friction fallback.

It must explain:

- when this mode is useful
- how it protects demos or user onboarding
- what quality tradeoffs may exist
- what evidence/code supports it if present
- what is not verified for the golden run

Do not claim no-key generation works in production unless actually validated.

### 8. Provider Failure / Fallback Policy

Include policy explanation for:

- key missing
- quota exhausted
- provider timeout
- provider unavailable
- moderation or safety block
- paid provider skipped
- fallback to no-key mode

Do not claim any of these happened in the golden run unless evidence proves it.

### 9. Designer / Marketer Interpretation

This must be useful to non-technical users.

Add plain-language explanations for:

- best quality mode
- cheapest safe mode
- emergency demo mode
- why provider choice affects review
- why proof matters for client handoff
- when to export evidence pack

### 10. Action Rail

Add CTAs to:

- `/operations-cockpit`
- `/evidence-pack`
- `/failure-timeline`
- `/b2-rehydrate-comparison`
- `/manifest-verification`
- `/b2-evidence`
- `/genblaze-pipeline`
- `/passport/run_89d967f9000045efa22ed4cc78cfa67f`
- `/`

### 11. Truth Boundary

Must clearly say what this page does and does not prove.

It may claim:

- it summarizes checked-in evidence and documented routing policy
- it explains provider decision tradeoffs
- it shows cost/budget classes as policy unless measured evidence exists
- it shows zero provider calls during rehydrate
- it helps marketers understand routing choices
- it shows pending gaps honestly

It must not claim:

- actual spend unless captured
- actual latency unless captured
- actual quota status unless captured
- real provider failures unless captured
- production no-key generation unless validated
- legal authenticity
- semantic truth
- human authorship
- C2PA authenticity
- Object Lock / tamper-proof storage
- browser-side B2 byte verification
- public deployment verification
- enterprise security

### 12. Limitations

Must include:

- no live provider call in PS-033
- no broad B2 read
- no live pricing API
- no measured billing unless present in checked-in evidence
- no measured latency unless present in checked-in evidence
- no quota inspection
- public deployment pending
- checked-in evidence and documented policy only
- no invented provider failure events

## Required Data Shape

In `providerDecisionIntelligence.ts`, create a structured data model with at least:

- intelligence_id
- intelligence_version
- generated_from
- run_id
- campaign_id
- archive_uri
- archive_sha256
- rehydrate_source
- provider_calls_during_rehydrate
- no_live_provider_call_during_rehydrate
- public_deployment_pending
- selected_route_summary
- provider_options
- budget_modes
- why_this_provider
- cost_time_ledger
- emergency_no_key_mode
- fallback_policy
- designer_marketer_interpretation
- action_routes
- truth_boundary
- limitations
- source_evidence

## Required CTA Changes

Add a visible link to `/provider-decision-intelligence` from:

- Judge Cockpit Home
- Operations Cockpit
- Judge Evidence Pack

Optional backlinks from:

- Failure-as-Proof Timeline
- B2 Rehydrate Comparison
- Manifest Verification Panel
- B2 Evidence Explorer
- Genblaze Pipeline Graph
- Public Passport

The Provider Decision Intelligence page must link back to:

- `/`
- `/operations-cockpit`
- `/evidence-pack`

## Required Evidence

Create:

- `docs/evidence/ps-033/provider-decision-intelligence-smoke.json`

Evidence JSON must include:

- ok
- route_or_surface
- intelligence_id
- intelligence_version
- run_id
- campaign_id
- archive_uri
- archive_sha256
- rehydrate_source
- provider_calls_during_rehydrate
- no_live_provider_call_during_rehydrate
- public_deployment_pending
- provider_decision_surface_verified
- decision_identity_visible
- decision_summary_visible
- provider_option_matrix_verified
- budget_modes_verified
- why_this_provider_visible
- cost_time_ledger_visible
- emergency_no_key_mode_visible
- fallback_policy_visible
- designer_marketer_interpretation_visible
- action_rail_verified
- truth_boundary_present
- limitations_present
- cost_claims_are_policy_not_billing
- no_actual_spend_claim_without_evidence
- no_actual_latency_claim_without_evidence
- no_quota_status_claim_without_evidence
- no_real_provider_failure_claim_without_evidence
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

- `docs/ps-033-provider-decision-intelligence-proof.md`

Proof doc must include:

- PS-031A alignment
- hardened product module alignment
- old-window idea consolidation
- product surface chosen
- files changed
- route/CTA map
- provider decision sections implemented
- provider option matrix explanation
- budget modes explanation
- why-this-provider explanation
- cost/time ledger explanation
- emergency no-key mode explanation
- fallback policy explanation
- designer/marketer value
- source evidence list
- proof chain explanation
- no-provider-call confirmation
- no-broad-B2-read confirmation
- no-fake-provider-failure confirmation
- no-raw-media-byte confirmation
- no-actual-spend-without-evidence confirmation
- no-actual-latency-without-evidence confirmation
- no-quota-status-without-evidence confirmation
- no-prior-slice-evidence-mutation confirmation
- truth boundary
- limitations
- validation commands
- smoke result

## Required Smoke Script

Create:

- `scripts/ps033_provider_decision_intelligence_smoke.py`

Smoke must validate at least:

1. Provider Decision Intelligence component exists.
2. Provider Decision Intelligence data module exists.
3. route `/provider-decision-intelligence` exists.
4. Judge Cockpit links to `/provider-decision-intelligence`.
5. Operations Cockpit links to `/provider-decision-intelligence`.
6. Judge Evidence Pack links to `/provider-decision-intelligence`.
7. Provider Decision page links to `/`.
8. Provider Decision page links to `/operations-cockpit`.
9. Provider Decision page links to `/evidence-pack`.
10. Provider Decision page links to Failure Timeline.
11. Provider Decision page links to B2 Rehydrate Comparison.
12. Provider Decision page links to Manifest Verification.
13. Provider Decision page links to B2 Evidence Explorer.
14. Provider Decision page links to Genblaze Pipeline Graph.
15. Provider Decision page links to golden passport.
16. decision identity visible.
17. decision summary visible.
18. required golden values visible or in data.
19. provider option matrix exists.
20. provider options contain provider name.
21. provider options contain model or role.
22. provider options contain modality or output type.
23. provider options contain key requirement.
24. provider options contain budget class.
25. provider options contain fallback role.
26. provider options contain evidence status.
27. provider options contain risk notes.
28. provider options contain truth class.
29. required truth classes exist.
30. budget modes exist.
31. budget mode `free_safe` exists.
32. budget mode `balanced` exists.
33. budget mode `quality_max` exists.
34. budget mode `emergency_no_key` exists.
35. budget modes are labeled as policy, not live billing.
36. Why This Provider section exists.
37. cost/time ledger exists.
38. measured_cost is not invented.
39. measured_latency is not invented.
40. provider_calls_during_rehydrate equals `0`.
41. emergency no-key mode exists.
42. fallback policy exists.
43. key missing policy exists.
44. quota exhausted policy exists.
45. timeout policy exists.
46. provider unavailable policy exists.
47. moderation/safety block policy exists.
48. paid provider skipped policy exists.
49. designer/marketer interpretation exists.
50. action rail exists.
51. truth boundary exists.
52. limitations exist.
53. source evidence includes PS-021.
54. source evidence includes PS-024.
55. source evidence includes PS-025.
56. source evidence includes PS-026.
57. source evidence includes PS-027.
58. source evidence includes PS-028.
59. source evidence includes PS-029.
60. source evidence includes PS-030.
61. source evidence includes PS-031.
62. source evidence includes PS-032.
63. source evidence includes PS-031A.
64. run_id matches known golden run.
65. campaign_id matches known golden campaign.
66. archive URI matches known archive.
67. archive SHA-256 matches known archive hash.
68. rehydrate_source equals `b2_rehydrated`.
69. no_live_provider_call_during_rehydrate is true.
70. no provider call introduced.
71. no broad B2 read introduced.
72. no fake provider failure claim introduced.
73. no raw media byte claim introduced.
74. no actual spend claim without evidence.
75. no actual latency claim without evidence.
76. no quota status claim without evidence.
77. no forbidden authenticity/security claims introduced.
78. no secrets.
79. no prior-slice evidence modified.
80. PS-032 smoke still passes using snapshot/restore if needed.
81. PS-031 smoke still passes using snapshot/restore if needed.
82. PS-030 smoke still passes using snapshot/restore if needed.
83. PS-029 smoke still passes using snapshot/restore if needed.
84. PS-028 smoke still passes using snapshot/restore if needed.
85. PS-027 smoke still passes using snapshot/restore if needed.
86. PS-026 smoke still passes using snapshot/restore if needed.
87. PS-025 smoke still passes using snapshot/restore if needed.
88. PS-024 smoke still passes.
89. PS-023 smoke still passes.
90. frontend typecheck/build passes if frontend changed.

The smoke script must leave the working tree clean except for PS-033 files.

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
- `apps/web/src/JudgeEvidencePack.tsx`
- optional `apps/web/src/FailureAsProofTimeline.tsx`
- optional `apps/web/src/B2RehydrateComparison.tsx`
- optional `apps/web/src/ManifestVerificationPanel.tsx`
- optional `apps/web/src/B2EvidenceExplorer.tsx`
- optional `apps/web/src/GenblazePipelineGraph.tsx`
- optional `apps/web/src/PublicPassportPage.tsx`
- `apps/web/src/styles.css`
- new `apps/web/src/ProviderDecisionIntelligence.tsx`
- new `apps/web/src/providerDecisionIntelligence.ts`
- `docs/evidence/ps-033/provider-decision-intelligence-smoke.json`
- `docs/ps-033-provider-decision-intelligence-proof.md`
- `scripts/ps033_provider_decision_intelligence_smoke.py`

Do not modify:

- historical evidence JSON under PS-019/020/021/024/025/026/027/028/029/030/031/032
- historical smoke scripts PS-019 through PS-032
- provider code unless a blocking bug is found and explained
- deployment config
- backend API unless necessary and justified
- unrelated docs

## Acceptance Criteria

PS-033 is accepted only when:

- spec is implemented as a real provider decision surface, not a decorative matrix
- `/provider-decision-intelligence` route works
- provider decision identity is visible
- provider option matrix is visible
- budget modes are visible
- Why This Provider is visible
- cost/time ledger is visible
- emergency no-key mode is visible
- fallback policy is visible
- designer/marketer interpretation is visible
- all required proof routes are linked
- PS-031A consolidation is referenced
- no fake provider failures are claimed
- no actual spend is claimed without evidence
- no actual latency is claimed without evidence
- no quota status is claimed without evidence
- no provider calls are introduced
- no broad B2 reads are introduced
- no forbidden authenticity/security claims are introduced
- PS-033 smoke passes
- PS-032 through PS-023 regressions pass
- frontend typecheck/build pass
- no prior-slice evidence is modified
- final git status contains only expected PS-033 files before commit

## Failure Conditions

Reject the slice if it:

- builds another disconnected decorative page
- ignores PS-031A
- renumbers roadmap slices
- invents selected provider facts
- invents actual spend
- invents actual latency
- invents quota status
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

After PS-033 is accepted, the next hardened module should be:

- PS-034 — Lineage + Comparison Lab
