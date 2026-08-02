# PS-031 — Export Campaign Pack v2 / Judge Evidence Pack

## Status

Specification slice.

## Roadmap Discipline

This slice follows:

- PS-030 accepted Failure-as-Proof Timeline
- docs/roadmap/proofstudio-winning-implementation-roadmap-2026-06-29.md

The implementation roadmap is binding.

Old-window ideas are implementation commitments, not notes.

PS-031 implements:

- Export Campaign Pack
- Judge Evidence Pack
- Proof View / Audit Pack foundation
- continuation of Provenance Passport
- continuation of Failure-as-Proof
- continuation of Archive / Rehydrate Lab direction

## Product Thesis

ProofStudio must not stop at showing proof pages.

The product must let a judge, client, reviewer, or operator take the proof chain away as a usable evidence package.

Most AI media tools export only an image.

ProofStudio should export the operational proof around the media:

- what was generated
- which run produced it
- where it is archived
- which manifest describes it
- how it rehydrates from B2
- whether providers were called again
- what is known
- what is not claimed
- what a judge/client should review

## Purpose

Create a judge-facing Export Campaign Pack / Judge Evidence Pack surface.

A judge should understand the whole proof chain without reading raw JSON.

Expected judge path:

Judge Cockpit
-> Judge Evidence Pack
-> Failure-as-Proof Timeline
-> B2 Rehydrate Comparison
-> Manifest Verification Panel
-> B2 Evidence Explorer
-> Genblaze Pipeline Graph
-> Public Passport

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

- PS-029 B2 Rehydrate Comparison evidence:
  - docs/evidence/ps-029/b2-rehydrate-comparison-smoke.json

- PS-030 Failure-as-Proof Timeline evidence:
  - docs/evidence/ps-030/failure-as-proof-timeline-smoke.json

- Roadmap commitment:
  - docs/roadmap/proofstudio-winning-implementation-roadmap-2026-06-29.md

Verified golden values:

- run_id: run_89d967f9000045efa22ed4cc78cfa67f
- campaign_id: camp_bea5161faa6244079d2ee01ce445c259
- archive SHA-256: a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141
- archive URI: https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-021/assets/a6/ad/a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141.json
- rehydrate_source: b2_rehydrated
- provider_calls_during_rehydrate: 0
- no_live_provider_call_during_rehydrate: true
- public_deployment_pending: true

## Non-Negotiable Rules

Do not fake an exported file if no export behavior exists.

Do not claim a zip download unless a zip is actually generated.

Do not claim the pack contains raw media bytes unless it actually does.

Do not claim browser-side B2 byte verification unless implemented.

Do not claim public deployment verification unless tested.

Do not claim legal authenticity, C2PA authenticity, human authorship, semantic truth, tamper-proof storage, Object Lock, enterprise auth, or production security unless actually implemented.

Do not invent provider failures or fallback events.

Do not call providers.

Do not fetch arbitrary B2 objects through untrusted input.

Do not broaden public durable-read scope.

Do not modify historical evidence JSON under PS-019/020/021/024/025/026/027/028/029/030.

Do not modify historical smoke scripts PS-019 through PS-030.

Do not expose secrets.

## Required Discovery

Before implementation, inspect:

- specs/40-ps-031-export-campaign-pack-v2.md
- docs/roadmap/proofstudio-winning-implementation-roadmap-2026-06-29.md
- docs/evidence/demo/golden-demo-run.json
- docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json
- docs/evidence/ps-025/public-durable-passport-unlock-smoke.json
- docs/evidence/ps-026/b2-evidence-explorer-smoke.json
- docs/evidence/ps-027/genblaze-pipeline-graph-smoke.json
- docs/evidence/ps-028/manifest-verification-panel-smoke.json
- docs/evidence/ps-029/b2-rehydrate-comparison-smoke.json
- docs/evidence/ps-030/failure-as-proof-timeline-smoke.json
- scripts/ps030_failure_as_proof_timeline_smoke.py
- scripts/ps029_b2_rehydrate_comparison_smoke.py
- scripts/ps028_manifest_verification_panel_smoke.py
- scripts/ps027_genblaze_pipeline_graph_smoke.py
- scripts/ps026_b2_evidence_explorer_smoke.py
- scripts/ps025_public_durable_passport_unlock_smoke.py
- scripts/ps024_golden_demo_run_pinning_smoke.py
- scripts/ps023_judge_cockpit_home_smoke.py
- apps/web/src/App.tsx
- apps/web/src/JudgeCockpitHome.tsx
- apps/web/src/FailureAsProofTimeline.tsx
- apps/web/src/failureAsProofTimeline.ts
- apps/web/src/B2RehydrateComparison.tsx
- apps/web/src/ManifestVerificationPanel.tsx
- apps/web/src/B2EvidenceExplorer.tsx
- apps/web/src/GenblazePipelineGraph.tsx
- apps/web/src/PublicPassportPage.tsx
- existing shared frontend evidence/data files

## Required Product Surface

Implement a dedicated frontend route:

- /evidence-pack

Preferred files:

- apps/web/src/JudgeEvidencePack.tsx
- apps/web/src/judgeEvidencePack.ts

Frontend-only is preferred.

No new API endpoint is required unless a real need is justified.

## Required Pack Behavior

The page must behave as a real evidence-pack surface, not just a marketing page.

At minimum, it must provide copy/download actions for:

1. Judge Evidence Pack JSON
2. Judge Evidence Pack README / Markdown

The download action may be browser-side using Blob/download.

If browser download is implemented, label it honestly:

- Local browser export
- Generated from checked-in ProofStudio evidence
- Does not fetch B2 bytes
- Does not include raw media bytes unless implemented

Do not claim a zip export unless zip generation is actually implemented.

## Required Pack Content

The Judge Evidence Pack must include visible sections:

1. Pack identity
2. Campaign / run identity
3. Final asset / archive summary
4. Prompt / generation evidence summary, if available from checked-in evidence
5. Provider / model / attempt ledger summary, if available from checked-in evidence
6. B2 archive evidence
7. Genblaze manifest evidence
8. B2 rehydrate proof
9. Failure-as-Proof summary
10. Public passport link
11. Review / approval status
12. Disclosure readiness notes
13. Truth boundary
14. Limitations
15. Next actions for judge/client

Required visible proof fields:

- run_id
- campaign_id
- archive_uri
- archive_sha256
- rehydrate_source
- provider_calls_during_rehydrate
- no_live_provider_call_during_rehydrate
- public_deployment_pending

Required evidence links:

- /failure-timeline
- /b2-rehydrate-comparison
- /manifest-verification
- /b2-evidence
- /genblaze-pipeline
- /passport/run_89d967f9000045efa22ed4cc78cfa67f
- /

## Required Judge Evidence Pack JSON Shape

The exported/generated pack JSON must include:

- pack_id
- pack_version
- generated_from
- generated_at
- campaign_id
- run_id
- archive_uri
- archive_sha256
- rehydrate_source
- provider_calls_during_rehydrate
- no_live_provider_call_during_rehydrate
- source_evidence
- route_map
- proof_chain
- failure_as_proof_summary
- disclosure_notes
- truth_boundary
- limitations
- public_deployment_pending

The pack JSON can be static/deterministic frontend data derived from checked-in evidence.

If generated_at is dynamic in browser export, the smoke must avoid brittle timestamp expectations.

## Required README / Markdown Export

The generated README/Markdown must include:

- title: ProofStudio Judge Evidence Pack
- run_id
- campaign_id
- what the pack proves
- what it does not prove
- B2 archive URI
- archive SHA-256
- rehydrate proof
- zero provider calls during rehydrate
- proof surface links
- disclosure notes
- limitations
- public deployment pending

## Required CTA Changes

Update navigation so judges can reach the Judge Evidence Pack.

Required:

- Judge Cockpit has a clear CTA to /evidence-pack
- Failure Timeline links to /evidence-pack
- Evidence Pack links to:
  - /failure-timeline
  - /b2-rehydrate-comparison
  - /manifest-verification
  - /b2-evidence
  - /genblaze-pipeline
  - /passport/run_89d967f9000045efa22ed4cc78cfa67f
  - /
- No broken internal links

Optional low-risk backlinks:

- B2 Rehydrate Comparison links to /evidence-pack
- Manifest Verification Panel links to /evidence-pack
- B2 Evidence Explorer links to /evidence-pack
- Genblaze Pipeline Graph links to /evidence-pack
- Public Passport links to /evidence-pack

## Required Truth Boundary

The Evidence Pack must distinguish:

- checked-in evidence
- durable B2 archive proof
- Genblaze manifest evidence
- B2 rehydrate proof
- local browser export
- local public passport contract proof
- inferred product explanation
- public deployment pending

Allowed claims:

- checked-in evidence records B2 archive and rehydrate proof
- checked-in evidence records zero provider calls during rehydrate
- the pack is generated from local checked-in ProofStudio evidence
- the browser export gives judges a portable proof summary
- the pack helps reviewers understand workflow provenance and limitations

Forbidden claims:

- pack proves semantic truth of media
- pack proves legal authenticity
- pack proves human authorship
- pack proves C2PA authenticity
- pack proves Object Lock or tamper-proof storage
- browser verified B2 bytes unless implemented
- pack includes raw media bytes unless implemented
- public deployment is verified unless tested
- actual provider failure/fallback occurred unless evidence proves it

## Required Evidence

Create:

- docs/evidence/ps-031/export-campaign-pack-v2-smoke.json

Evidence must include:

- ok
- route_or_surface
- pack_id
- pack_version
- run_id
- campaign_id
- archive_uri
- archive_sha256
- rehydrate_source
- provider_calls_during_rehydrate
- no_live_provider_call_during_rehydrate
- evidence_pack_surface_verified
- json_export_available
- markdown_export_available
- pack_identity_verified
- pack_sections_verified
- route_map_verified
- proof_chain_verified
- failure_as_proof_summary_visible
- disclosure_notes_visible
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
- source_implementation_roadmap
- frontend_surface_verified
- api_surface_verified
- no_provider_call
- no_broad_b2_read
- no_raw_media_byte_claim
- no_zip_claim_unless_implemented
- no_prior_slice_evidence_modified
- public_deployment_pending
- checked_at

## Required Proof Doc

Create:

- docs/ps-031-export-campaign-pack-v2-proof.md

The proof doc must include:

- roadmap alignment
- implementation-roadmap commitment alignment
- old-window/out-of-the-box idea implemented
- product surface chosen
- files changed
- route/CTA map
- pack sections
- pack JSON shape
- README/Markdown export behavior
- source evidence list
- proof chain explanation
- Failure-as-Proof carryover
- Disclosure Readiness carryover
- no-zip-claim confirmation unless implemented
- no-raw-media-byte-claim confirmation unless implemented
- no-provider-call confirmation
- no-broad-B2-read confirmation
- no-prior-slice-evidence-mutation confirmation
- truth boundary confirmation
- validation commands
- smoke result
- limitations

## Required Smoke Script

Create:

- scripts/ps031_export_campaign_pack_v2_smoke.py

The smoke script must validate:

1. Evidence Pack surface exists
2. route /evidence-pack exists
3. Judge Cockpit links to /evidence-pack
4. Failure Timeline links to /evidence-pack
5. Evidence Pack links to Failure Timeline
6. Evidence Pack links to B2 Rehydrate Comparison
7. Evidence Pack links to Manifest Verification Panel
8. Evidence Pack links to B2 Evidence Explorer
9. Evidence Pack links to Genblaze Pipeline Graph
10. Evidence Pack links to golden passport
11. pack JSON export action exists
12. pack Markdown/README export action exists
13. required pack sections are visible
14. required pack JSON shape is present in data/source
15. route map is present
16. proof chain is present
17. Failure-as-Proof summary is visible
18. disclosure notes are visible
19. limitations are visible
20. truth boundary is visible
21. run_id matches PS-021/024/025/026/027/028/029/030 sources
22. campaign_id matches PS-021/024/025/026/027/028/029/030 sources
23. archive URI matches PS-021/024/025/026/027/028/029/030 sources
24. archive SHA-256 matches PS-021/024/025/026/027/028/029/030 sources
25. rehydrate_source equals b2_rehydrated
26. provider_calls_during_rehydrate equals 0
27. no_live_provider_call_during_rehydrate is true
28. no provider call is introduced
29. no broad B2 read is introduced
30. no raw media byte export claim unless implemented
31. no zip claim unless implemented
32. no forbidden authenticity claims
33. no secrets
34. no prior-slice evidence is modified
35. PS-030 smoke still passes through snapshot/restore protection if needed
36. PS-029 smoke still passes through snapshot/restore protection if needed
37. PS-028 smoke still passes through snapshot/restore protection if needed
38. PS-027 smoke still passes through snapshot/restore protection if needed
39. PS-026 smoke still passes through snapshot/restore protection if needed
40. PS-025 smoke still passes through snapshot/restore protection if needed
41. PS-024 smoke still passes
42. PS-023 smoke still passes
43. frontend typecheck/build passes if frontend changed

Important:

PS-031 smoke must preserve prior-slice evidence exactly.

If it runs prior smokes that write evidence, snapshot/restore prior evidence files or use safe index handling so the working tree remains clean outside PS-031 files.

Do not modify prior smoke scripts.

Do not add brittle duplicate inline product scanners to final commit gates if canonical smoke already validates the product surface.

## Expected Allowed Files

Implementation may modify only files needed for PS-031.

Likely allowed files:

- apps/web/src/App.tsx
- apps/web/src/JudgeCockpitHome.tsx
- apps/web/src/FailureAsProofTimeline.tsx
- optional apps/web/src/B2RehydrateComparison.tsx
- optional apps/web/src/ManifestVerificationPanel.tsx
- optional apps/web/src/B2EvidenceExplorer.tsx
- optional apps/web/src/GenblazePipelineGraph.tsx
- optional apps/web/src/PublicPassportPage.tsx
- optional apps/web/src/styles.css
- new apps/web/src/JudgeEvidencePack.tsx
- new apps/web/src/judgeEvidencePack.ts
- docs/evidence/ps-031/export-campaign-pack-v2-smoke.json
- docs/ps-031-export-campaign-pack-v2-proof.md
- scripts/ps031_export_campaign_pack_v2_smoke.py

Do not modify:

- historical evidence JSON under PS-019/020/021/024/025/026/027/028/029/030
- historical smoke scripts PS-019 through PS-030
- provider code unless a real bug is found and explained before commit
- backend API unless necessary and justified
- deployment config
- unrelated files

## Backend Validation Environment Rule

Any PS-031 validation that imports backend/API code must run with:

- source .venv/bin/activate
- export PYTHONPATH="$PWD/src"

Do not run python -m pip install -e . from repo root.

## Validation Requirements

Before commit, run:

- PS-031 smoke script
- PS-030 smoke script, through snapshot/restore protection if needed
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

PS-031 is accepted only if:

1. Judges can reach a clear Judge Evidence Pack surface.
2. The surface explains ProofStudio as a production workflow, not an image generator.
3. The pack includes required sections.
4. The pack includes required verified values.
5. JSON export is available or honestly represented as local browser export.
6. Markdown/README export is available or honestly represented as local browser export.
7. The pack links to all proof surfaces.
8. Failure-as-Proof is carried into the pack.
9. Disclosure readiness is visible.
10. Limitations are visible.
11. Truth boundary remains visible.
12. No zip claim is made unless zip generation is implemented.
13. No raw media byte export claim is made unless implemented.
14. No provider call is introduced.
15. No broad B2 read is introduced.
16. No prior-slice evidence is modified.
17. PS-031 smoke passes.
18. PS-030, PS-029, PS-028, PS-027, PS-026, PS-025, PS-024, and PS-023 regressions pass.
19. Final working tree contains only PS-031 files before commit.

## Failure Conditions

Fail the slice if:

- the pack is decorative but not evidence-backed
- the pack omits required evidence sources
- the pack omits required sections
- the pack claims zip export without implementing it
- the pack claims raw media bytes without including them
- the pack claims browser-side B2 byte verification without implementing it
- the pack claims certification/authenticity not implemented
- the pack claims public deployment success without verification
- the pack introduces provider calls
- the pack introduces broad B2 reads
- prior-slice evidence is modified
- archive URI/hash is copied incorrectly
- truth boundary is removed or weakened
- forbidden claims are introduced
- unrelated files are changed

## Next Slice After PS-031

PS-032 — Mission Control / Flight Recorder v2
