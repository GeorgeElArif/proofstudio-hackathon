# ProofStudio — Submission Checklist

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


What is required for the final hackathon submission, what local proof is already
available, and what is still pending. Honest status as of PS-018B.

## Required before final submission

- [x] **Working app URL** judges can access — verified by PS-018B:
      `https://proofstudio-web.onrender.com`.
- [x] **Public API URL** — verified by PS-018B:
      `https://proofstudio.onrender.com`.
- [x] **Repo access** — the GitHub repository with the full source, specs, docs,
      and proof scripts.
- [x] **Setup instructions** — `recording-runbook.md` + `apps/web/README.md` +
      `README.md`.
- [x] **Providers / models list** — `provider-model-inventory.md`.
- [x] **B2 and Genblaze explanation** — `b2-genblaze-usage.md`.
- [ ] **Demo video (~3 minutes)** — pending recording. The script
      (`demo-video-script.md`) and runbook (`recording-runbook.md`) are ready;
      the video itself must still be captured.

## Deployment target and public URL status

- **Selected target:** Render (see `docs/deployment/render.md` and `render.yaml`).
- **Public deployment:** verified by PS-018B.
- **Final public app URL:** `https://proofstudio-web.onrender.com`
- **Public API URL:** `https://proofstudio.onrender.com`
- **Live URL smoke:** passed in explicit live URL mode.
- **Safe public dry-run:** passed with no provider call and no B2/Genblaze write.

## Local proof already available

- [x] **One-click helper** — `scripts/ps015_one_click_local_demo.py` (safe
      default: no provider, no B2, no fake media).
- [x] **Smoke tests** — one per slice (`scripts/ps0xx_*.py`), each writing a
      summary + transcript to `/tmp/proofstudio-ps-0xx/`.
- [x] **Review Room UI** — `apps/web/` (Vite + React + TypeScript), all 10
      sections, safe dry-run default, explicit live proof run.
- [x] **API docs** — FastAPI Swagger at `http://127.0.0.1:8000/docs` once the
      backend is running; contract documented in `apps/web/README.md`.
- [x] **B2 / Genblaze proofs** — PS-001A, PS-004, PS-005, PS-007, PS-009,
      PS-010 (see `b2-genblaze-usage.md`).
- [x] **Passport proof** — PS-011 Provenance Passport assembled from rehydrated
      stored evidence.
- [x] **Public URL proof** — PS-018B Render public deployment verification.

## Still pending

- [ ] **Production persistence** (e.g. Postgres/SQLite) with the B2 archive as
      the system of record. The live deployed API currently uses in-memory
      storage.
- [ ] **Authentication** (no auth/authorization layer yet).
- [ ] **Final video recording** of the ~3-minute demo.

## How to verify locally right now

```bash
cd /home/proofstudio-work/proofstudio
source .venv/bin/activate
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"

# Safe one-click demo (no provider, no B2)
python scripts/ps015_one_click_local_demo.py

# Submission evidence pack smoke (docs/contract/secret/backend-unchanged checks)
python scripts/ps016_submission_evidence_pack_smoke.py

# PS-018 live URL smoke (default: local contract mode, no providers, no B2)
python scripts/ps018_live_url_smoke.py
```

## Truth boundary

This checklist reflects the real state of the project. PS-018B claims and verifies
public app and API URLs. It does **not** claim paid production availability,
authentication, production persistence,
background job reliability, legal authenticity, C2PA authenticity, semantic
truth, or human authorship.

## PS-018 public URL status

Historical PS-018 Level A did not verify a live URL. PS-018B now verifies the live Render public app and API URLs.

The public API URL and public web URL are recorded here because `scripts/ps018_live_url_smoke.py` passed in explicit live URL mode against the real deployed URLs.

## PS-018B public URL status

PS-018B verifies the public Render deployment.

- Final public app URL: `https://proofstudio-web.onrender.com`
- Public API URL: `https://proofstudio.onrender.com`
- Live URL smoke status: passed.
- Public URL verified: true.
- Safe public dry-run: passed.
- Default public dry-run provider call: false.
- Default public dry-run B2/Genblaze write: false.

Evidence:

- `../ps-018b-render-deployment-public-url-verification-proof.md`
- `../evidence/ps-018b/live-url-smoke-summary.json`
- `../evidence/ps-018b/live-url-smoke-transcript.json`
- `../evidence/ps-018b/safe-public-dry-run-semantic.json`

<!-- PS-019_SUBMISSION_CHECKLIST_START -->
## PS-019 public passport checklist

- [x] Public passport route implemented: `/passport/:runId`.
- [x] Proof Score UI implemented.
- [x] Safe dry-run passport smoke passed.
- [x] No provider call by default.
- [x] No B2/Genblaze write by default.
- [x] Frontend build passed.
- [x] Render static-site rewrite added for `/passport/*`.

Demo URL pattern after deployment:

`https://proofstudio-web.onrender.com/passport/<run_id>`

Production caveat: current run persistence is still in-memory; durable public passport links require the later persistence/B2-source-of-truth slice.
<!-- PS-019_SUBMISSION_CHECKLIST_END -->
