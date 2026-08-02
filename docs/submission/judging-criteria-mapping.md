# ProofStudio — Judging Criteria Mapping

<!-- PS-018B_CURRENT_PUBLIC_DEPLOYMENT_START -->
## Current public deployment status — PS-018B

PS-018B supersedes the earlier PS-018 pre-deployment state.

- Public app URL: `https://proofstudio-web.onrender.com`
- Public API URL: `https://proofstudio.onrender.com`
- Live URL smoke: passed.
- Public URL verified: true.
- API health/version: verified.
- Frontend load: verified.
- CORS preflight from the deployed frontend origin: verified.
- Safe public dry-run: verified with no provider call and no B2/Genblaze write.

Evidence:

- `docs/ps-018b-render-deployment-public-url-verification-proof.md`
- `docs/evidence/ps-018b/live-url-smoke-summary.json`
- `docs/evidence/ps-018b/live-url-smoke-transcript.json`
- `docs/evidence/ps-018b/safe-public-dry-run-semantic.json`
<!-- PS-018B_CURRENT_PUBLIC_DEPLOYMENT_END -->


How ProofStudio maps to the four judging criteria. For each criterion: what the
judge should look at, which feature proves it, which files/scripts support it,
and what remains a limitation.

## 1. Real-world utility

**The claim:** ProofStudio solves a real, repeatable pain — teams generate AI
media across providers but lose the evidence trail (prompt, model, retries,
storage, manifest, trust). It gives them a Review Room to review, verify, and
trust AI-generated assets.

**What the judge should look at:**

- The Review Room end-to-end flow: campaign → safe dry-run → explicit live proof
  run → attempts → assets → manifest → Provenance Passport.
- The Provenance Passport turning raw evidence into reviewer-actionable output.

**Which feature proves it:**

- The campaign/run/evidence product model and the Review Room UI (PS-013,
  PS-014).
- The provider-router with primary + fallback and full attempt ledger (PS-006,
  PS-007).

**Supporting files/scripts:**

- `apps/web/src/App.tsx`, `apps/web/src/api.ts` (Review Room UI).
- `src/proofstudio/api/services.py`, `src/proofstudio/api/passport.py`.
- `scripts/ps014_live_demo_flow_review_room_smoke.py`,
  `scripts/ps015_one_click_local_demo.py`.

**What remains a limitation:**

- **Public deployment verified in PS-018B**; utility is demonstrated through the live Render app and locally via
  the one-click helper, not at a public URL.

## 2. Production readiness

**The claim:** ProofStudio is built like a production-minded system: a typed
FastAPI contract, a service layer with clear error behavior, CORS hardening,
honest failure handling, and a durable archive/rehydrate path.

**What the judge should look at:**

- The FastAPI server mode + full 10-route demo contract (PS-012).
- Honest live-run outcomes: `live_completed`, `live_failed`, `live_blocked` —
  no fabricated success (PS-009, PS-014).
- The run archive/rehydrate durability path (PS-010).

**Which feature proves it:**

- Server-mode FastAPI app (`proofstudio.api.app:app`) with `/health`, `/version`,
  and the campaign/run/attempt/asset/manifest/passport routes.
- Default **safe dry-run**; explicit opt-in live mode with a constant warning.

**Supporting files/scripts:**

- `src/proofstudio/api/app.py`, `src/proofstudio/api/models.py`,
  `src/proofstudio/api/services.py`, `src/proofstudio/api/live_bridge.py`,
  `src/proofstudio/api/archive.py`.
- `scripts/ps012_fastapi_server_demo_contract_smoke.py`,
  `scripts/ps013a_local_demo_integration_hardening_smoke.py`.

**What remains a limitation:**

- **In-memory store** (process-local), no production database persistence yet.
- **No authentication / authorization.**
- **Public deployment verified in PS-018B.** Remaining production caveat: Render free-tier reliability/cold-start behavior should be upgraded before final judging.
- Durability lives in the B2 archive artifact, not a live database.

## 3. Backblaze B2 storage / data orchestration

**The claim:** Backblaze B2 is the system of record for generated assets, prompt
packets, attempt ledgers, provider notes, run archives, and manifests — all
byte-level verified through the Genblaze pipeline.

**What the judge should look at:**

- A live run storing the generated image and supporting artifacts in B2 with a
  verified manifest (PS-004, PS-005, PS-007, PS-009).
- A run archived to B2 and **rehydrated from B2 object content** without
  rerunning any provider (PS-010).

**Which feature proves it:**

- The reusable `GenblazeStore` B2 + manifest helper.
- The archive/rehydrate layer (`store_run_archive_with_genblaze`,
  `read_archive_from_b2`, `rehydrate_run_from_archive`).

**Supporting files/scripts:**

- `src/proofstudio/provenance/genblaze_store.py`, `src/proofstudio/api/archive.py`.
- `scripts/ps001a_b2_manifest_smoke.py`,
  `scripts/ps004_provider_router_cloudflare_smoke.py`,
  `scripts/ps005_pollinations_fallback_smoke.py`,
  `scripts/ps007_live_provider_router_chain_smoke.py`,
  `scripts/ps009_api_live_run_bridge_smoke.py`,
  `scripts/ps010_run_archive_rehydrate_b2_smoke.py`.

**What remains a limitation:**

- B2 is exercised on the **live proof path** only; the demo default is a safe
  dry-run with no B2 call.
- Rehydration restores into an in-memory store, not a production database.

## 4. Genblaze use

**The claim:** The Genblaze pipeline ingests assets and writes/verifies manifests,
and manifest verification is used as provenance evidence across the whole product.

**What the judge should look at:**

- Manifest write → read-back from B2 → byte-level verification
  (`stored_manifest_verify: true`, `transfer_failures: []`).
- The Provenance Passport surfacing manifest verification as reviewer evidence.

**Which feature proves it:**

- `GenblazeStore` write/read/verify pattern reused from PS-001A through PS-011.
- The Provenance Passport assembled from rehydrated manifest-verified evidence
  (PS-011).

**Supporting files/scripts:**

- `src/proofstudio/provenance/genblaze_store.py`,
  `src/proofstudio/api/passport.py`.
- `scripts/ps001a_b2_manifest_smoke.py`,
  `scripts/ps007_live_provider_router_chain_smoke.py`,
  `scripts/ps010_run_archive_rehydrate_b2_smoke.py`,
  `scripts/ps011_provenance_passport_api_smoke.py`.

**What remains a limitation:**

- Genblaze proves **workflow integrity and byte-level asset integrity only** —
  not semantic truth, legal authenticity, C2PA authenticity, or human
  authorship.
- The passport is assembled from stored evidence; it does not itself call B2 at
  read time.

## At-a-glance matrix

| Criterion | Strongest proof slices | Demo surface | Main limitation |
|-----------|------------------------|--------------|-----------------|
| Real-world utility | PS-006, PS-007, PS-013, PS-014 | Review Room UI + passport | Public URL verified in PS-018B |
| Production readiness | PS-009, PS-010, PS-012, PS-013A | FastAPI contract + archive/rehydrate | In-memory store, no auth |
| B2 storage/data orchestration | PS-001A, PS-004, PS-005, PS-007, PS-009, PS-010 | Live run + rehydrate | B2 only on live path |
| Genblaze use | PS-001A, PS-007, PS-010, PS-011 | Manifest verify + passport | Workflow integrity only |
