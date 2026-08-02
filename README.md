# ProofStudio

## Judge quick start

<!-- PROOFSTUDIO_JUDGE_QUICK_START -->
ProofStudio turns AI-generated media into durable, reviewable evidence with
provider lineage, Genblaze manifests, SHA-256 integrity records, and
Backblaze B2 storage verification.

- **Public application:** https://proofstudio-web.onrender.com
- **Verified GMI to Backblaze B2 proof:** https://proofstudio-web.onrender.com/live-proof.html
- **Interactive FastAPI documentation:** https://proofstudio.onrender.com/docs
- **Demo video:** https://www.youtube.com/watch?v=awJsDzYsX-E

### Verified live result

The public proof records one successful GMI Cloud request using Seedream 5.0
Lite, one original 4096 x 2304 PNG, zero continuation generation posts, and
five evidence objects written to and immediately read back from Backblaze B2.

The evidence boundary is explicit: hashes verify recorded bytes. ProofStudio
does not claim semantic truth, legal authenticity, human authorship, C2PA
certification, or globally atomic create-if-absent storage.
<!-- /PROOFSTUDIO_JUDGE_QUICK_START -->

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


ProofStudio is a provenance-aware AI media operations app that turns campaign briefs into verified media kits using Genblaze and Backblaze B2.

## Hackathon thesis

Most AI media apps stop at generation. ProofStudio focuses on the production layer:

- campaign brief intake
- Genblaze media pipeline orchestration
- Backblaze B2 storage for assets, manifests, thumbnails, logs, and exports
- SHA-256 provenance verification
- variant lineage
- review/export workflows

## MVP golden path

Brief → Genblaze pipeline → generated media → B2 storage → Provenance Passport → variant lineage → review/export.

## Repo structure

    specs/      Product, architecture, storage, pipeline, and acceptance specs
    apps/web/   React + TypeScript + Vite frontend
    apps/api/   FastAPI backend
    workers/    Background worker for Genblaze jobs
    packages/   Shared schemas/types if needed
    docs/       Architecture diagrams and submission notes
    scripts/    Smoke tests and operational scripts

## Current phase

Public hackathon submission snapshot. The deployed application, verified GMI
generation proof, Backblaze B2 evidence, typed API, public source snapshot, and
demo video are live.

## Local quick start

Prerequisites: Python, Node.js, npm, and Git.

    git clone https://github.com/GeorgeElArif/proofstudio-hackathon.git
    cd proofstudio-hackathon
    python -m pip install -r apps/api/requirements.txt
    cd apps/web
    npm ci
    npm run build
    cd ../..
    python scripts/ps015_one_click_local_demo.py

Environment templates are provided in `.env.example` and
`.env.production.example`. External-provider and Backblaze credentials are not
committed. Live generation and storage operations remain explicit,
credential-dependent actions.

## Submission pack

Judge-ready submission docs (demo script, recording runbook, judge evidence pack,
provider/model inventory, B2 + Genblaze usage, judging criteria mapping, and
submission checklist) live in [`docs/submission/`](./docs/submission/README.md).
Public deployment target is **Render**. PS-018B verifies the live public frontend and backend URLs. Run the local demo with
`python scripts/ps015_one_click_local_demo.py`.

## Deployment target

PS-018 selected **Render** as the public-deployment target. PS-018B verifies the real public Render deployment.

- Public app URL: `https://proofstudio-web.onrender.com`
- Public API URL: `https://proofstudio.onrender.com`
- Deployment plan: `render.yaml`
- Render runbook and live URL smoke docs: [`docs/deployment/`](./docs/deployment/README.md)
- Live URL smoke script: `scripts/ps018_live_url_smoke.py`

## PS-018B public deployment status

PS-018B verifies the real public Render deployment.

- Public app URL: `https://proofstudio-web.onrender.com`
- Public API URL: `https://proofstudio.onrender.com`
- Live URL smoke: passed.
- API `/health`: verified.
- API `/version`: verified.
- Frontend load: verified.
- CORS preflight from the deployed frontend origin: verified.
- Safe public dry-run: verified with no provider call and no B2/Genblaze write.

Evidence:

- `docs/ps-018b-render-deployment-public-url-verification-proof.md`
- `docs/evidence/ps-018b/live-url-smoke-summary.json`
- `docs/evidence/ps-018b/live-url-smoke-transcript.json`
- `docs/evidence/ps-018b/safe-public-dry-run-semantic.json`

<!-- PS-019_PUBLIC_PASSPORT_START -->
## Public Provenance Passport — PS-019

PS-019 adds a public, shareable Provenance Passport route with a deterministic Proof Score.

URL pattern:

`https://proofstudio-web.onrender.com/passport/<run_id>`

The route is designed for judge-facing proof review: run identity, campaign context, provider state, attempt/fallback timeline, B2/Genblaze proof status, asset evidence, Proof Score, and truth boundary.

Evidence:

- `docs/ps-019-public-passport-proof-score-proof.md`
- `docs/evidence/ps-019/local-passport-smoke-summary.json`
- `docs/evidence/ps-019/live-public-passport-smoke-summary.json`
<!-- PS-019_PUBLIC_PASSPORT_END -->
