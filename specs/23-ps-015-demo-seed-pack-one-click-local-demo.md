# PS-015 Demo Seed Pack + One-Click Local Demo

## 1. Purpose

PS-015 makes ProofStudio easier to demo, record, recover, and hand to reviewers.

Previous milestones proved:

- PS-012: FastAPI demo API contract exists.
- PS-013: Review Room frontend exists.
- PS-013A: local frontend/backend browser integration works.
- PS-014: Review Room supports safe dry-run and explicit live proof run paths.

PS-015 adds a repeatable local demo layer:

- a deterministic demo seed pack
- a one-command local demo helper
- safe default demo setup
- optional explicit live run mode
- generated demo proof summary
- clear runbook for recording the hackathon demo

The default path must stay safe and must not call live providers or B2.

## 2. Product Meaning

A judge, teammate, or future reviewer should not need to remember fragile manual setup steps.

They should be able to run one command and get:

- backend readiness checked or started
- frontend readiness checked or started
- a demo campaign created or seeded
- a safe dry-run created
- Review Room URL printed
- API docs URL printed
- evidence summary written to `/tmp`
- optional live mode only with an explicit flag

PS-015 turns the existing product into a reliable demo workflow.

## 3. Safety Principle

Default mode is safe.

The one-click demo must never call live providers or B2 unless the user explicitly enables live mode.

Required default:

- no provider calls
- no B2 calls
- no fake media
- no fake manifest
- no fake passport evidence
- safe dry-run only

Optional live mode requires an explicit environment variable or CLI flag.

Allowed explicit live gates:

- `PROOFSTUDIO_PS015_LIVE=1`
- or `--live`

Default acceptance must not require live provider spend.

## 4. Current Foundation

Backend local command:

- `uvicorn proofstudio.api.app:app --reload --host 127.0.0.1 --port 8000`

Frontend local command:

- `cd apps/web && npm run dev -- --host 127.0.0.1 --port 5173`

Browser URLs:

- Review Room: `http://127.0.0.1:5173`
- API health: `http://127.0.0.1:8000/health`
- API docs: `http://127.0.0.1:8000/docs`

Existing routes:

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

## 5. Non-Goals

Do not deploy.

Do not add authentication.

Do not add a production database.

Do not add a background worker system.

Do not add a queue.

Do not redesign the UI.

Do not change the provider router.

Do not make live mode default.

Do not fake media.

Do not fake manifest verification.

Do not fake B2 archive evidence.

Do not fake passport evidence.

Do not claim legal authenticity.

Do not claim C2PA authenticity.

Do not claim semantic truth.

Do not claim human authorship.

Do not modify historical proof scripts.

## 6. Required Files

Allowed new files:

- `examples/ps015/demo-seed-pack.json`
- `scripts/ps015_one_click_local_demo.py`
- `scripts/ps015_demo_seed_pack_one_click_smoke.py`
- `docs/ps-015-demo-seed-pack-one-click-local-demo-proof.md`

Allowed modified files:

- `apps/web/README.md`
- `apps/web/src/App.tsx` only if tiny demo seed affordance is needed
- `apps/web/src/styles.css` only if tiny styling is needed
- `apps/web/package.json` only if a useful demo script is needed
- root `README.md` only if it already exists and a short demo command belongs there

Prefer no backend changes.

Backend changes are allowed only for tiny compatibility fixes and must preserve all existing contracts.

Do not modify historical proof scripts:

- `scripts/ps004_provider_router_cloudflare_smoke.py`
- `scripts/ps005_pollinations_fallback_smoke.py`
- `scripts/ps006_provider_router_core_smoke.py`
- `scripts/ps007_live_provider_router_chain_smoke.py`
- `scripts/ps008_backend_api_smoke.py`
- `scripts/ps009_api_live_run_bridge_smoke.py`
- `scripts/ps010_run_archive_rehydrate_b2_smoke.py`
- `scripts/ps011_provenance_passport_api_smoke.py`
- `scripts/ps012_fastapi_server_demo_contract_smoke.py`
- `scripts/ps013_demo_ui_review_room_smoke.py`
- `scripts/ps013a_local_demo_integration_hardening_smoke.py`
- `scripts/ps014_live_demo_flow_review_room_smoke.py`

## 7. Demo Seed Pack Requirement

Create:

- `examples/ps015/demo-seed-pack.json`

The seed pack must contain deterministic demo inputs, not fake generated evidence.

Required fields:

- `slice`
- `demo_name`
- `campaign`
  - `name`
  - `brief`
  - `audience`
  - `channels`
  - `tone`
  - `creative_constraints`
- `safe_run`
  - `run_live: false`
  - `prompt`
  - `expected_mode`
- `optional_live_run`
  - `run_live: true`
  - `prompt`
  - `requires_explicit_opt_in: true`
- `reviewer_script`
  - ordered demo talking points
- `truth_boundary`
- `created_for`

The seed pack may include demo prompts and campaign metadata.

It must not include:

- fake image URLs
- fake manifest URIs
- fake B2 URLs
- fake hashes
- fake provider/model claims
- secrets

## 8. One-Click Local Demo Helper

Create:

- `scripts/ps015_one_click_local_demo.py`

The helper should support a safe default mode.

Required default behavior:

1. Confirm it is running inside the ProofStudio repo.
2. Confirm Python imports work with `src` layout.
3. Load `examples/ps015/demo-seed-pack.json`.
4. Import the FastAPI app.
5. Use TestClient or equivalent to create a demo campaign.
6. Create a safe dry-run with `run_live=false`.
7. Fetch:
   - run
   - attempts
   - assets
   - manifest
   - passport
8. Confirm default path did not call live providers.
9. Confirm default path did not call B2.
10. Write a local demo summary JSON to:
    `/tmp/proofstudio-ps-015/one-click-local-demo-summary.json`
11. Write a local demo transcript JSON to:
    `/tmp/proofstudio-ps-015/one-click-local-demo-transcript.json`
12. Print:
    - Review Room URL
    - API docs URL
    - backend command
    - frontend command
    - created campaign id
    - created run id
    - summary path
    - transcript path

The helper may also support:

- `--print-runbook`
- `--check-ports`
- `--serve`
- `--live`

But only the safe default path is required for acceptance.

## 9. One-Click Serve Mode

Optional but useful:

`scripts/ps015_one_click_local_demo.py --serve`

If implemented, it should:

- start backend on `127.0.0.1:8000`
- start frontend on `127.0.0.1:5173`
- print URLs
- keep processes alive until Ctrl-C
- terminate child processes cleanly on exit
- not run live mode by default

If this mode is not implemented, docs must be honest and call the script a safe seed/check helper rather than a server process manager.

## 10. Optional Explicit Live Demo Mode

Optional live mode may run only when:

- `PROOFSTUDIO_PS015_LIVE=1`
- or `--live`

When live mode is enabled:

- the helper may create `run_live=true`
- it must print a clear warning before doing so
- it must record whether the live run:
  - completed
  - failed
  - blocked
- it must not fake success
- it must not fake media
- it must not fake manifest proof

Default acceptance must not require live mode.

## 11. Frontend Requirement

Prefer no major UI change.

If a small change is useful, the UI may include:

- a note pointing users to the seed pack
- copy explaining the demo sequence
- a reminder that live mode is explicit
- a link-style display of the local runbook

Do not redesign the UI.

Do not add fake seeded evidence to the frontend.

## 12. Documentation Requirement

Create:

- `docs/ps-015-demo-seed-pack-one-click-local-demo-proof.md`

It must include:

- status
- seed pack path
- one-click helper path
- safe default behavior
- exact default command
- optional live command if implemented
- exact two-terminal manual fallback
- generated summary path
- generated transcript path
- default no-provider/no-B2 proof
- no-fake-evidence proof
- demo recording checklist
- limitations
- next milestone recommendation
- truth boundary

## 13. Smoke Script

Create:

- `scripts/ps015_demo_seed_pack_one_click_smoke.py`

The smoke must run the safe default path only.

The smoke must:

1. Set output dir:
   `/tmp/proofstudio-ps-015`
2. Verify seed pack exists.
3. Verify seed pack schema.
4. Verify seed pack has no fake evidence URLs/hashes/provider claims.
5. Verify one-click helper exists.
6. Execute or import the one-click helper safe default path.
7. Verify campaign was created.
8. Verify safe dry-run was created.
9. Verify run_live is false.
10. Verify no live provider call.
11. Verify no B2 call.
12. Verify no fake media.
13. Verify no fake manifest.
14. Verify helper printed or returned Review Room URL.
15. Verify helper printed or returned API docs URL.
16. Verify frontend build still passes.
17. Verify docs mention:
    - default command
    - optional live gate
    - two-terminal fallback
    - truth boundary
18. Write summary JSON:
    `/tmp/proofstudio-ps-015/demo-seed-pack-one-click-summary.json`
19. Write transcript JSON:
    `/tmp/proofstudio-ps-015/demo-seed-pack-one-click-transcript.json`
20. Print final summary JSON.

## 14. Required Summary Fields

The PS-015 smoke summary must include:

- `ok`
- `slice`
- `seed_pack_path`
- `seed_pack_checked`
- `seed_pack_schema_checked`
- `seed_pack_no_fake_evidence`
- `one_click_helper_path`
- `one_click_helper_checked`
- `campaign_created`
- `safe_dry_run_created`
- `run_live_default_false`
- `default_no_live_provider_call`
- `default_no_b2_call`
- `no_fake_media`
- `no_fake_manifest`
- `review_room_url`
- `api_docs_url`
- `frontend_build_checked`
- `frontend_build_status`
- `docs_updated`
- `live_mode_enabled`
- `live_run_status`
- `summary_path`
- `transcript_path`
- `truth_boundary`

## 15. Acceptance Criteria

PS-015 is accepted if:

- seed pack exists
- seed pack schema is valid
- seed pack has no fake evidence
- one-click helper exists
- one-click helper creates demo campaign
- one-click helper creates safe dry-run by default
- default run_live is false
- default path does not call providers
- default path does not call B2
- no fake media
- no fake manifest
- helper prints Review Room and API docs URLs
- docs include clear runbook
- frontend build passes
- smoke summary ok true
- historical scripts remain untouched
- secret scan passes

## 16. Failure Conditions

Reject PS-015 if:

- live mode is default
- providers are called during default smoke
- B2 is called during default smoke
- seed pack contains fake generated evidence
- helper fakes successful media or manifest
- frontend build breaks
- existing backend API contract regresses
- historical proof scripts are modified
- secrets are introduced
- unrelated files are changed

## 17. Truth Boundary

PS-015 proves ProofStudio has a deterministic local demo seed pack and a safe one-click helper for preparing a local Review Room demo.

It does not prove:

- public deployment
- production availability
- authentication
- production persistence
- background job reliability
- legal authenticity
- C2PA authenticity
- semantic truth
- human authorship
