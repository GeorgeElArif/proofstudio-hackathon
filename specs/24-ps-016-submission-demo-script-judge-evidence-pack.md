# PS-016 Submission Demo Script + Judge Evidence Pack

## 1. Purpose

PS-016 turns the working ProofStudio product into a judge-ready submission package.

Previous milestones proved:

- PS-006: ProviderRouter Core
- PS-007: Live ProviderRouter Chain
- PS-008: Backend API Skeleton
- PS-009: API to Live Run Bridge
- PS-010: Run Archive and Rehydrate from B2
- PS-011: Provenance Passport API
- PS-012: FastAPI Server Mode and Demo API Contract
- PS-013: Demo UI Shell / Review Room Frontend
- PS-013A: Local Demo Integration Hardening
- PS-014: Live Demo Flow / End-to-End Review Room Path
- PS-015: Demo Seed Pack + One-Click Local Demo

PS-016 must create the submission narrative, demo script, and judge evidence pack.

This slice does not build a new product feature.

It packages what already works so judges can understand:

- what the product is
- who it is for
- what problem it solves
- how to run it
- how the demo works
- how it uses Backblaze B2
- how it uses Genblaze
- which AI providers and models are used
- why the architecture is production-minded
- what the provenance passport proves
- what it intentionally does not prove

## 2. Product Meaning

ProofStudio is no longer only code and smoke tests.

It needs a submission-ready story:

- a clear 3-minute demo script
- an exact recording sequence
- a feature-to-judging-criteria mapping
- provider/model inventory
- Backblaze B2 and Genblaze usage proof
- screenshots/evidence checklist
- setup/run commands
- truth boundary
- known limitations
- final submission checklist

The goal is to make the project easy to judge.

## 3. Current Hackathon Submission Requirements

The submission package must prepare for these public requirements:

- working app URL judges can access
- GitHub repository with setup instructions
- providers and models list
- explanation of B2 and Genblaze usage
- short demo video around 3 minutes
- clear real-world utility
- clear production readiness
- meaningful B2 storage/data orchestration
- meaningful Genblaze use

PS-016 should not claim final public deployment if deployment is not done yet.

If no public URL exists yet, the pack must mark it as pending and point to the local demo path from PS-015.

## 4. Safety Principle

The evidence pack must not overclaim.

Do not claim:

- public deployment if not deployed
- production availability if local only
- authentication if not implemented
- production persistence if not implemented
- legal authenticity
- C2PA authenticity
- semantic truth
- human authorship

Do not fake screenshots.

Do not fake live provider output.

Do not fake B2 evidence.

Do not fake Genblaze manifests.

Do not invent provider/model use.

Do not include secrets.

## 5. Non-Goals

Do not deploy.

Do not add authentication.

Do not add production database persistence.

Do not redesign the UI.

Do not create fake screenshots.

Do not create fake media.

Do not run live providers by default.

Do not call B2 by default.

Do not change the ProviderRouter.

Do not change the FastAPI API contract.

Do not change the frontend product flow unless a tiny documentation link is useful.

Do not modify historical proof scripts.

## 6. Required Files

Allowed new files:

- docs/submission/README.md
- docs/submission/demo-video-script.md
- docs/submission/recording-runbook.md
- docs/submission/judge-evidence-pack.md
- docs/submission/provider-model-inventory.md
- docs/submission/b2-genblaze-usage.md
- docs/submission/judging-criteria-mapping.md
- docs/submission/submission-checklist.md
- scripts/ps016_submission_evidence_pack_smoke.py
- docs/ps-016-submission-demo-script-judge-evidence-pack-proof.md

Allowed modified files:

- README.md only if it exists and needs a short submission section
- apps/web/README.md only if it needs a short pointer to the submission pack

Prefer docs-only plus smoke script.

Backend changes are not allowed for PS-016.

Frontend app changes are not allowed unless explicitly justified as a tiny link or README-only improvement.

Do not modify historical proof scripts:

- scripts/ps004_provider_router_cloudflare_smoke.py
- scripts/ps005_pollinations_fallback_smoke.py
- scripts/ps006_provider_router_core_smoke.py
- scripts/ps007_live_provider_router_chain_smoke.py
- scripts/ps008_backend_api_smoke.py
- scripts/ps009_api_live_run_bridge_smoke.py
- scripts/ps010_run_archive_rehydrate_b2_smoke.py
- scripts/ps011_provenance_passport_api_smoke.py
- scripts/ps012_fastapi_server_demo_contract_smoke.py
- scripts/ps013_demo_ui_review_room_smoke.py
- scripts/ps013a_local_demo_integration_hardening_smoke.py
- scripts/ps014_live_demo_flow_review_room_smoke.py
- scripts/ps015_demo_seed_pack_one_click_smoke.py

## 7. Demo Video Script Requirement

Create:

- docs/submission/demo-video-script.md

The script must be designed for about 3 minutes.

Required structure:

### 0:00-0:20 Hook

Explain the pain:

Creative and marketing teams generate AI media across multiple providers, but lose the evidence trail: prompt, model, retries, storage, manifests, and what can be trusted.

### 0:20-0:45 Product

Introduce ProofStudio as a Review Room for AI media operations.

State the clear audience:

- creator teams
- marketing teams
- agencies
- production teams reviewing AI-generated assets

### 0:45-1:20 Safe Demo Setup

Show:

- one-click helper
- local Review Room
- API health
- safe dry-run default
- no provider/B2 calls by default

### 1:20-2:10 Live Proof Flow

Show:

- explicit live mode warning
- create live proof run
- provider attempt ledger
- fallback/readiness story
- generated asset metadata if available
- manifest evidence if available

If live provider fails or is blocked, show the failure honestly and explain that failed attempts are also evidence.

### 2:10-2:40 Provenance Passport

Show:

- generation summary
- manifest verification
- archive/rehydration if available
- trust boundary
- reviewer next actions

### 2:40-3:00 Why It Wins

Map to judging criteria:

- real-world utility
- production readiness
- B2 storage/data orchestration
- Genblaze orchestration

End with the product claim:

ProofStudio turns AI media generation from a black-box output into a reviewable, durable, evidence-backed workflow.

## 8. Recording Runbook Requirement

Create:

- docs/submission/recording-runbook.md

It must include:

- exact local backend command
- exact local frontend command
- exact one-click helper command
- browser URLs
- what to show on screen
- what not to show on screen
- fallback plan if live provider fails
- fallback plan if local frontend is unavailable
- final recording checklist

It must include commands:

- cd /home/proofstudio-work/proofstudio
- source .venv/bin/activate
- export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"
- python scripts/ps015_one_click_local_demo.py
- uvicorn proofstudio.api.app:app --reload --host 127.0.0.1 --port 8000
- cd apps/web
- npm run dev -- --host 127.0.0.1 --port 5173

## 9. Judge Evidence Pack Requirement

Create:

- docs/submission/judge-evidence-pack.md

It must summarize:

- product name
- one-sentence pitch
- audience
- pain point
- workflow
- completed slices
- architecture
- API endpoints
- frontend path
- demo commands
- proof scripts
- smoke summaries
- B2/Genblaze evidence
- provider/model evidence
- truth boundary
- limitations
- next work

It must be honest about what is local-only and what is not yet deployed.

## 10. Provider/Model Inventory Requirement

Create:

- docs/submission/provider-model-inventory.md

It must list only providers/models actually implemented or proven in this repo.

Expected categories:

### Live proven or implemented

- Cloudflare Workers AI image provider
- Pollinations image fallback provider
- Gemini campaign intelligence if included in prior proofs

### Attempted but blocked

- GMI Cloud generation blocked by credits
- Gemini/Imagen visual generation blocked by quota/paid-plan limits
- Luma skipped because card required

### Optional later

- ElevenLabs
- OpenAI
- Runway
- Stability Audio
- NVIDIA NIM

Do not claim optional providers are implemented unless they are.

## 11. B2 + Genblaze Usage Requirement

Create:

- docs/submission/b2-genblaze-usage.md

It must explain:

- Backblaze B2 stores generated assets, metadata, archives, manifests, or proof objects when live proof paths are used
- Genblaze Pipeline ingests assets and writes/verifies manifests
- manifest verification is used as provenance evidence
- archive/rehydrate path restores evidence from B2
- truth boundary: this proves workflow evidence, not semantic truth or legal authenticity

It must reference actual completed proof slices:

- PS-001A
- PS-002
- PS-004
- PS-005
- PS-007
- PS-009
- PS-010
- PS-011

Only include claims supported by existing scripts/docs.

## 12. Judging Criteria Mapping Requirement

Create:

- docs/submission/judging-criteria-mapping.md

It must map ProofStudio to:

- real-world utility
- production readiness
- B2 storage/data orchestration
- Genblaze use

For each criterion include:

- what the judge should look at
- which feature proves it
- which files/scripts support it
- what is still a limitation

## 13. Submission Checklist Requirement

Create:

- docs/submission/submission-checklist.md

It must include:

### Required before final submission

- working app URL
- repo access
- setup instructions
- providers/models list
- B2 and Genblaze explanation
- demo video around 3 minutes

### Local proof already available

- one-click helper
- smoke tests
- Review Room UI
- API docs
- B2/Genblaze proofs
- passport proof

### Still pending if not done yet

- public deployment
- production persistence
- auth
- final video recording
- final public URL

## 14. Submission README Requirement

Create:

- docs/submission/README.md

It must be the entry point for judges and reviewers.

It should link to:

- demo video script
- recording runbook
- judge evidence pack
- provider/model inventory
- B2 + Genblaze usage
- judging criteria mapping
- submission checklist

## 15. Proof Document Requirement

Create:

- docs/ps-016-submission-demo-script-judge-evidence-pack-proof.md

It must include:

- status
- files created
- what the pack covers
- source-of-truth assumptions
- public requirements covered
- local proof commands
- no fake evidence statement
- limitations
- next milestone recommendation
- truth boundary

## 16. Smoke Script Requirement

Create:

- scripts/ps016_submission_evidence_pack_smoke.py

The smoke must not call live providers or B2.

The smoke must:

1. Set output dir:
   /tmp/proofstudio-ps-016
2. Verify all required docs exist.
3. Verify demo video script contains the required timeline sections.
4. Verify recording runbook contains exact backend/frontend/helper commands.
5. Verify judge evidence pack contains product, audience, workflow, architecture, and limitations.
6. Verify provider/model inventory does not overclaim optional providers.
7. Verify B2 + Genblaze usage doc references actual prior proof slices.
8. Verify judging criteria mapping includes all four criteria.
9. Verify submission checklist includes required submission items.
10. Verify docs/submission/README.md links to all submission docs.
11. Verify no fake screenshots/media/B2 URLs/manifests are invented.
12. Verify no secrets.
13. Verify no backend changes.
14. Verify historical proof scripts untouched.
15. Optionally verify frontend build still passes.
16. Write summary JSON:
    /tmp/proofstudio-ps-016/submission-evidence-pack-summary.json
17. Write transcript JSON:
    /tmp/proofstudio-ps-016/submission-evidence-pack-transcript.json
18. Print final summary JSON.

## 17. Required Summary Fields

The PS-016 smoke summary must include:

- ok
- slice
- docs_created
- demo_script_checked
- recording_runbook_checked
- judge_evidence_pack_checked
- provider_model_inventory_checked
- b2_genblaze_usage_checked
- judging_criteria_mapping_checked
- submission_checklist_checked
- submission_readme_checked
- public_requirements_covered
- judging_criteria_covered
- no_fake_screenshots
- no_fake_media
- no_fake_b2_evidence
- no_fake_manifest_evidence
- no_secret_leakage
- backend_unchanged
- historical_scripts_untouched
- frontend_build_checked
- frontend_build_status
- summary_path
- transcript_path
- truth_boundary

## 18. Acceptance Criteria

PS-016 is accepted if:

- submission docs exist
- demo script is usable for about 3 minutes
- recording runbook is exact
- judge evidence pack is clear
- provider/model inventory is honest
- B2 + Genblaze usage is accurate
- judging criteria mapping is complete
- submission checklist covers all required items
- no fake evidence is introduced
- no secrets are introduced
- backend is unchanged
- historical scripts remain untouched
- smoke summary ok true

## 19. Failure Conditions

Reject PS-016 if:

- it claims public deployment without proof
- it claims optional providers are implemented without proof
- it invents screenshots
- it invents generated media
- it invents B2 URLs
- it invents manifest hashes
- it hides limitations
- it exposes secrets
- it modifies backend code
- it modifies historical proof scripts
- it shifts roadmap numbering incorrectly

## 20. Truth Boundary

PS-016 proves ProofStudio has a judge-ready submission evidence pack and demo script grounded in the current local product and prior proof slices.

It does not prove:

- public deployment
- final Devpost submission
- production availability
- authentication
- production persistence
- background job reliability
- legal authenticity
- C2PA authenticity
- semantic truth
- human authorship
