# PS-013 Demo UI Shell / Review Room Frontend

## 1. Purpose

PS-013 creates the first visible ProofStudio demo UI.

Previous milestones proved the backend product spine:

- PS-006: ProviderRouter Core
- PS-007: Live ProviderRouter Chain + B2 + Genblaze
- PS-008: Backend API Skeleton
- PS-009: API to Live Run Bridge
- PS-010: Run Archive + Rehydrate from B2
- PS-011: Review Room / Provenance Passport API
- PS-012: FastAPI Server Mode + Demo API Contract

PS-013 must make this understandable through a demo-first frontend.

The UI goal:

Create Campaign
-> Create Safe Run
-> View Run Evidence
-> View Attempts
-> View Assets
-> View Manifest
-> View Provenance Passport

This is not a full production app. It is the first judge-facing Review Room shell.

## 2. Product Meaning

ProofStudio is a provenance-aware AI media operations system.

The frontend must make that obvious.

A judge should be able to open the UI and understand:

- ProofStudio is not just an image generator.
- It records provider attempts.
- It records generated asset metadata.
- It shows manifest verification.
- It creates a Provenance Passport.
- It separates what the system proves from what it does not prove.

## 3. Demo Principle

The UI must explain the product in under 30 seconds.

Priority order:

1. Clarity
2. Proof
3. Speed
4. Visual polish
5. Extensibility

Do not build a complicated dashboard.

Build a sharp Review Room demo shell.

## 4. Current Foundation

PS-012 exposes a FastAPI app with these routes:

- GET /health
- GET /version
- POST /campaigns
- GET /campaigns/{campaign_id}
- POST /runs
- GET /runs/{run_id}
- GET /runs/{run_id}/attempts
- GET /runs/{run_id}/assets
- GET /runs/{run_id}/manifest
- GET /runs/{run_id}/passport

PS-013 must consume these endpoints.

Default frontend behavior must use safe dry-run mode unless explicitly changed.

## 5. Non-Goals

Do not deploy.

Do not add auth.

Do not add a production database.

Do not add payment.

Do not add complex team/workspace management.

Do not force live provider calls by default.

Do not require B2 credentials for the default UI smoke.

Do not fake media.

Do not fake manifest verification.

Do not fake passport evidence.

Do not claim C2PA authenticity.

Do not claim legal authenticity.

Do not claim semantic truth.

Do not modify historical proof scripts.

## 6. Required Files

Allowed new files depend on existing repo structure.

Preferred if a frontend app already exists:

- use the existing frontend app directory

If no frontend app exists, create a minimal app under:

- apps/web/

Allowed new files may include:

- apps/web/package.json
- apps/web/index.html
- apps/web/src/main.tsx or apps/web/src/main.jsx
- apps/web/src/App.tsx or apps/web/src/App.jsx
- apps/web/src/api.ts
- apps/web/src/styles.css
- apps/web/README.md
- scripts/ps013_demo_ui_review_room_smoke.py
- docs/ps-013-demo-ui-review-room-frontend-proof.md

Allowed modified files:

- root package/dependency files only if the repo already uses them
- apps/web files
- docs only as needed

Do not modify backend service behavior unless a tiny compatibility fix is required and justified.

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

## 7. Frontend Technology

Inspect the repo before choosing.

If a frontend framework already exists, use it.

If no frontend exists, create a minimal Vite + React + TypeScript app if Node tooling is available.

Acceptable fallback:

- simple static HTML/CSS/JS demo shell under apps/web

Do not over-engineer.

The UI must be easy to run locally.

Document exact commands.

## 8. Required UI Sections

The first screen should include these sections.

### 8.1 Hero / Positioning

Must communicate:

ProofStudio is a provenance-aware AI media operations system for creator and marketing teams.

Suggested headline:

ProofStudio turns AI media generation into verifiable production evidence.

Suggested subcopy:

Create a campaign, run a provider workflow, inspect attempts, assets, manifest verification, and a Provenance Passport.

### 8.2 API Status Card

Show:

- backend health
- version
- framework mode
- capabilities

Use:

- GET /health
- GET /version

### 8.3 Campaign Builder

Fields:

- campaign name
- brief
- target audience
- platform
- objective

Action:

- Create Campaign

Uses:

- POST /campaigns

After creation, show:

- campaign_id
- campaign summary

### 8.4 Run Creator

Fields:

- prompt
- budget mode
- run_live toggle

Default:

- run_live false

The toggle must clearly warn:

Live mode may call external providers and B2.

Actions:

- Create Safe Dry Run
- Optional Create Live Run only if explicitly enabled

Uses:

- POST /runs

### 8.5 Evidence Overview

After run creation, show:

- run_id
- status
- selected provider
- selected model
- fallback used
- attempt count
- asset count
- manifest URI
- manifest hash

Uses:

- GET /runs/{run_id}

### 8.6 Attempt Timeline

Show a readable list/table:

- attempt index
- provider
- model
- status
- normalized status
- latency
- retryable
- fallback allowed
- sanitized error message

Uses:

- GET /runs/{run_id}/attempts

### 8.7 Assets Panel

Show:

- asset URL
- media type
- sha256
- size bytes
- metadata

Uses:

- GET /runs/{run_id}/assets

For dry-run, must honestly show no generated assets.

### 8.8 Manifest Panel

Show:

- manifest URI
- manifest hash
- in-memory verify
- stored verify
- transfer failures
- stored transfer failures

Uses:

- GET /runs/{run_id}/manifest

For dry-run, must honestly show manifest unavailable/not ready.

### 8.9 Provenance Passport Panel

Show a judge-friendly passport summary:

- passport source
- run summary
- generation summary
- attempt timeline
- manifest verification
- archive and rehydration
- trust boundary
- reviewer next actions

Uses:

- GET /runs/{run_id}/passport

The trust boundary must be visible.

### 8.10 Truth Boundary Footer

Always visible:

ProofStudio verifies workflow evidence, asset hashes, provider attempts, storage records, and manifest metadata when present. It does not prove semantic truth, legal authenticity, C2PA authenticity, human authorship, or production security.

## 9. UX Requirements

The UI should feel like an operator review room, not a generic CRUD app.

Design direction:

- dark or neutral technical theme
- clear cards
- strong evidence hierarchy
- status pills
- readable JSON expanders
- no childish visuals
- no fake graphs
- no fake provider logos
- no fake media placeholders pretending to be real output

Suggested sections order:

1. Header / positioning
2. Backend status
3. Campaign builder
4. Run creator
5. Evidence overview
6. Attempts
7. Assets
8. Manifest
9. Provenance Passport
10. Truth boundary

## 10. Data Handling Rules

The UI must consume real API responses.

It must not hardcode successful proof data.

It may include placeholder helper text before a run exists.

It must distinguish clearly between:

- no run yet
- dry-run no media
- live completed
- live failed
- live blocked
- manifest unavailable
- archive unavailable

No fake media.

No fake manifest URI.

No fake archive URI.

## 11. Configuration

The frontend should support API base URL configuration.

Suggested:

- VITE_PROOFSTUDIO_API_BASE_URL
- fallback to http://127.0.0.1:8000

Document this clearly.

## 12. Smoke Script

Create:

scripts/ps013_demo_ui_review_room_smoke.py

The smoke script must validate the frontend without requiring a browser if possible.

It should:

1. Set output dir:
   /tmp/proofstudio-ps-013
2. Verify frontend files exist.
3. Verify package/dependency file exists if using Node.
4. Verify UI source references required API endpoints.
5. Verify UI contains the required sections:
   - health/status
   - campaign builder
   - run creator
   - evidence overview
   - attempts
   - assets
   - manifest
   - passport
   - trust boundary
6. Verify default run_live is false or safe.
7. Verify no hardcoded fake media success.
8. Verify no hardcoded fake manifest success.
9. Verify no secrets.
10. If Node dependencies are available, run build or typecheck.
11. Write summary JSON:
   /tmp/proofstudio-ps-013/demo-ui-review-room-summary.json
12. Write transcript JSON:
   /tmp/proofstudio-ps-013/demo-ui-review-room-transcript.json
13. Print final summary JSON.

Optional stronger smoke:

- start FastAPI server locally
- start frontend dev server or use built assets
- perform a basic HTTP check

But default acceptance should not require complex browser automation.

## 13. Required Summary Fields

The PS-013 summary must include:

- ok
- slice
- frontend_path
- frontend_type
- package_file_present
- api_base_config_present
- health_section_present
- campaign_builder_present
- run_creator_present
- evidence_overview_present
- attempts_panel_present
- assets_panel_present
- manifest_panel_present
- passport_panel_present
- trust_boundary_present
- default_run_live_safe
- no_fake_media
- no_fake_manifest
- no_secrets
- build_checked
- build_status
- summary_path
- transcript_path
- truth_boundary

## 14. Documentation Proof

Create:

docs/ps-013-demo-ui-review-room-frontend-proof.md

It must include:

- status
- frontend path
- frontend technology
- run commands
- API base URL configuration
- required UI sections
- default safe dry-run behavior
- live mode warning behavior
- evidence panels
- passport panel
- truth boundary
- build/smoke result
- limitations
- next milestone recommendation

## 15. Acceptance Criteria

PS-013 is accepted if:

- frontend shell exists
- UI can be run locally
- UI references PS-012 API endpoints
- UI includes required Review Room sections
- default run creation is safe dry-run
- live mode requires explicit user action
- no fake media is shown
- no fake manifest proof is shown
- Provenance Passport panel exists
- trust boundary is visible
- smoke summary ok true
- historical proof scripts remain untouched
- secret scan passes

## 16. Failure Conditions

Reject PS-013 if:

- UI hardcodes successful proof evidence
- UI fakes generated media
- UI fakes manifest verification
- UI runs live mode by default
- UI hides the truth boundary
- UI ignores the passport endpoint
- backend proof scripts are modified
- secrets are introduced
- unrelated files are changed
- the app becomes too large or unfocused for demo use

## 17. Truth Boundary

PS-013 proves ProofStudio has a local demo UI shell for reviewing campaign/run evidence through the FastAPI API.

It does not prove:

- production deployment
- public app URL
- auth
- production persistence
- background job reliability
- legal authenticity
- C2PA authenticity
- semantic truth
- human authorship

Those are later slices.
