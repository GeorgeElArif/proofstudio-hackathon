# PS-027 — Genblaze Pipeline Graph

## Status

Specification slice.

## Roadmap Discipline

This slice follows the PS-022 master roadmap.

Completed lead-in:

- PS-023 — Judge Cockpit Home
- PS-024 — Golden Demo Run Pinning
- PS-025 — Public Durable Passport Unlock
- PS-026 — B2 Evidence Explorer

PS-026 made Backblaze B2 evidence visible as a product surface.

PS-027 must now make Genblaze orchestration visible as a product surface.

## Purpose

Expose the ProofStudio media pipeline as a clear Genblaze Pipeline Graph.

Judges should not need to infer the orchestration path from code, JSON, smoke scripts, or docs. They should see a product-level graph that explains how a run flows through:

Brief -> Provider Router -> Genblaze pipeline -> Generated asset -> B2 archive -> Provenance passport -> Rehydrate without provider rerun

## Product Goal

A judge should be able to open a product page and understand:

- where Genblaze sits in the workflow
- what steps are orchestrated
- which evidence is verified
- which steps are local contract proof
- which parts are not being overclaimed
- how B2 and passport evidence connect to the pipeline

Expected judge path:

Judge Cockpit -> Genblaze Pipeline Graph -> B2 Evidence Explorer -> Public Passport

## Current Verified Base

Use only verified data from existing evidence files.

Relevant evidence sources:

- PS-021 live B2 durable rehydrate proof:
  - `docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json`

- PS-024 golden demo manifest:
  - `docs/evidence/demo/golden-demo-run.json`

- PS-025 public durable passport unlock evidence:
  - `docs/evidence/ps-025/public-durable-passport-unlock-smoke.json`

- PS-026 B2 evidence explorer evidence:
  - `docs/evidence/ps-026/b2-evidence-explorer-smoke.json`

Verified golden values:

- run_id: `run_89d967f9000045efa22ed4cc78cfa67f`
- campaign_id: `camp_bea5161faa6244079d2ee01ce445c259`
- archive SHA-256: `a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141`
- archive URI: `https://s3.eu-central-003.backblazeb2.com/proofstudio-project-assets/proofstudio/ps-021/assets/a6/ad/a6ade0a678847bd0e7a6a258c93e815af3194da264a35e19a75e2ccae84a7141.json`
- rehydrate_source: `b2_rehydrated`
- provider_calls_during_rehydrate: `0`
- no_live_provider_call_during_rehydrate: `true`

## Non-Negotiable Rules

Do not fake Genblaze execution.

Do not invent pipeline steps that are not supported by the project.

Do not claim a live provider call occurred unless verified.

Do not claim every graph node is a direct Genblaze SDK primitive unless verified.

Do not claim public deployment verification unless actually tested.

Do not claim Object Lock, tamper-proof storage, legal authenticity, C2PA authenticity, semantic truth, human authorship, enterprise auth, or production security unless actually implemented.

Do not alter historical PS-019/020/021/024/025/026 evidence.

Do not broaden public durable-read scope.

Do not call providers.

Do not expose secrets.

## Required Discovery

Before implementation, inspect:

- `specs/36-ps-027-genblaze-pipeline-graph.md`
- `docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json`
- `docs/evidence/demo/golden-demo-run.json`
- `docs/evidence/ps-025/public-durable-passport-unlock-smoke.json`
- `docs/evidence/ps-026/b2-evidence-explorer-smoke.json`
- `scripts/ps026_b2_evidence_explorer_smoke.py`
- `scripts/ps025_public_durable_passport_unlock_smoke.py`
- `scripts/ps024_golden_demo_run_pinning_smoke.py`
- `scripts/ps023_judge_cockpit_home_smoke.py`
- `src/proofstudio/provenance/genblaze_store.py`
- `src/proofstudio/api/live_bridge.py`
- `src/proofstudio/api/services.py`
- `src/proofstudio/api/durable_passport.py`
- `src/proofstudio/providers/router.py`
- `apps/web/src/App.tsx`
- `apps/web/src/JudgeCockpitHome.tsx`
- `apps/web/src/B2EvidenceExplorer.tsx`
- `apps/web/src/PublicPassportPage.tsx`

## Required Product Surface

Implement a Genblaze Pipeline Graph product surface.

Preferred:

- dedicated frontend route: `/genblaze-pipeline`
- component: `apps/web/src/GenblazePipelineGraph.tsx`
- static, verified, evidence-backed graph using existing golden run data

Alternative acceptable form:

- strong section inside Judge Cockpit or Public Passport if a dedicated route is too risky

Dedicated route is preferred because PS-027 is a roadmap surface, not a hidden detail.

## Required Graph Content

The graph must show a clear pipeline with nodes and edges.

Required nodes:

1. Campaign brief
2. Provider Router
3. Genblaze orchestration
4. Media generation attempt
5. Asset / manifest capture
6. Backblaze B2 archive
7. Provenance passport
8. Durable rehydrate
9. Judge review

Required edge story:

- brief enters pipeline
- router selects provider path
- Genblaze-backed flow records generation/provenance
- asset and manifest are archived to B2
- passport exposes run proof
- rehydrate loads durable archive
- rehydrate uses zero provider calls
- judge reviews evidence

Required visible values:

- run_id
- campaign_id
- archive URI
- archive SHA-256
- rehydrate_source
- provider_calls_during_rehydrate = 0
- no_live_provider_call_during_rehydrate = true
- evidence source files
- truth boundary

## Required CTA Changes

Update product navigation so judges can reach the graph.

Required:

- Judge Cockpit has a clear CTA to `/genblaze-pipeline`
- Genblaze Pipeline Graph links to:
  - `/b2-evidence`
  - `/passport/run_89d967f9000045efa22ed4cc78cfa67f`
  - `/`
- B2 Evidence Explorer may link back to `/genblaze-pipeline` if low-risk
- No broken internal links

## Required Truth Boundary

The graph must distinguish between:

- verified pipeline evidence
- inferred product explanation
- local contract proof
- public deployment pending

The graph may say:

- Genblaze is used in the ProofStudio pipeline
- the pipeline records provider/model/provenance and B2 archive evidence
- this golden run has verified archive and rehydrate proof

The graph must not say:

- Genblaze independently certifies the truth of the media
- the media is legally authentic
- the asset is C2PA-authenticated
- the archive is tamper-proof
- Object Lock is enabled
- public deployment has been verified unless it has

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

- `docs/evidence/ps-027/genblaze-pipeline-graph-smoke.json`

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
- `pipeline_nodes_verified`
- `pipeline_edges_verified`
- `genblaze_surface_verified`
- `truth_boundary_present`
- `source_ps021_evidence`
- `source_ps024_manifest`
- `source_ps025_evidence`
- `source_ps026_evidence`
- `frontend_surface_verified`
- `api_surface_verified`
- `no_provider_call`
- `no_broad_b2_read`
- `no_prior_slice_evidence_modified`
- `public_deployment_pending`
- `checked_at`

## Required Proof Doc

Create:

- `docs/ps-027-genblaze-pipeline-graph-proof.md`

The proof doc must include:

- roadmap alignment
- product surface chosen
- files changed
- route/CTA map
- graph node list
- graph edge list
- evidence source files
- Genblaze claim boundary
- no-provider-call confirmation
- no-broad-B2-read confirmation
- no-prior-slice-evidence-mutation confirmation
- truth boundary confirmation
- validation commands
- smoke result
- limitations

## Required Smoke Script

Create:

- `scripts/ps027_genblaze_pipeline_graph_smoke.py`

The smoke script must validate:

1. Genblaze Pipeline Graph surface exists
2. route `/genblaze-pipeline` exists if dedicated route is chosen
3. Judge Cockpit links to the graph
4. graph links to B2 Evidence Explorer
5. graph links to golden passport
6. required pipeline nodes are present
7. required pipeline edges/story are present
8. run_id matches golden manifest
9. campaign_id matches golden manifest
10. archive URI matches PS-021/PS-024/PS-026 evidence
11. archive SHA-256 matches PS-021/PS-024/PS-026 evidence
12. rehydrate_source equals `b2_rehydrated`
13. provider_calls_during_rehydrate equals `0`
14. no_live_provider_call_during_rehydrate is `true`
15. truth boundary is present
16. no provider call is introduced
17. no broad B2 read is introduced
18. no secrets
19. no forbidden affirmative claims
20. no prior-slice evidence is modified
21. PS-026 smoke still passes
22. PS-025 smoke still passes through read-only preservation if needed
23. PS-024 smoke still passes
24. PS-023 smoke still passes
25. frontend typecheck/build passes if frontend changed

Important: PS-027 smoke must preserve prior-slice evidence exactly. If it runs any prior smoke that writes evidence, it must snapshot/restore prior evidence files so the working tree remains clean outside PS-027 files.

## Expected Allowed Files

Implementation may modify only files needed for PS-027.

Likely allowed files:

- `apps/web/src/App.tsx`
- `apps/web/src/JudgeCockpitHome.tsx`
- optional `apps/web/src/B2EvidenceExplorer.tsx`
- optional `apps/web/src/PublicPassportPage.tsx`
- optional `apps/web/src/styles.css`
- new `apps/web/src/GenblazePipelineGraph.tsx`
- optional `apps/web/src/genblazePipeline.ts`
- `docs/evidence/ps-027/genblaze-pipeline-graph-smoke.json`
- `docs/ps-027-genblaze-pipeline-graph-proof.md`
- `scripts/ps027_genblaze_pipeline_graph_smoke.py`

Do not modify:

- historical evidence JSON under PS-019/020/021/024/025/026
- historical smoke scripts PS-019 through PS-026
- provider code unless a real bug is found and explained before commit
- backend API unless necessary and justified
- deployment config
- unrelated styling

## Backend Validation Environment Rule

Any PS-027 validation that imports backend/API code must run with:

- `source .venv/bin/activate`
- `export PYTHONPATH="$PWD/src"`

Do not run `python -m pip install -e .` from repo root.

## Validation Requirements

Before commit, run:

- PS-027 smoke script
- PS-026 smoke script, but without leaving prior-slice evidence dirty
- PS-025 smoke if needed, but with snapshot/restore protection
- PS-024 smoke
- PS-023 smoke
- frontend typecheck/build if frontend changed
- backend syntax/API tests if backend files changed
- whitespace check
- exact status/cached-file guard

## Acceptance Criteria

PS-027 is accepted only if:

1. Judges can reach a clear Genblaze Pipeline Graph surface.
2. The graph includes the required nodes and edges.
3. The graph connects Genblaze, Provider Router, B2 archive, Passport, and Rehydrate.
4. Verified values match PS-021/PS-024/PS-025/PS-026 evidence.
5. No fake Genblaze execution is claimed.
6. No provider call is introduced.
7. No broad B2 read is introduced.
8. No prior-slice evidence is modified.
9. Truth boundary remains visible.
10. PS-027 smoke passes.
11. PS-026, PS-025, PS-024, and PS-023 regressions pass.
12. Final working tree contains only PS-027 files before commit.

## Failure Conditions

Fail the slice if:

- graph is decorative but not evidence-backed
- graph omits Genblaze or hides it behind vague wording
- graph claims certification/authenticity not implemented
- graph claims public deployment success without verification
- graph introduces provider calls
- graph introduces broad B2 reads
- prior-slice evidence is modified
- archive URI/hash is copied incorrectly
- truth boundary is removed or weakened
- forbidden claims are introduced
- unrelated files are changed

## Next Slice After PS-027

PS-028 — Manifest Verification Panel
