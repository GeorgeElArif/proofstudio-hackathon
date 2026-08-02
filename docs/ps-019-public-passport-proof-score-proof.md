# PS-019 — Public Provenance Passport Share Page + Proof Score Proof

## Summary

PS-019 adds a judge-facing public Provenance Passport route and deterministic Proof Score UI.

Frontend route:

`/passport/:runId`

Deployed Render URL pattern:

`https://proofstudio-web.onrender.com/passport/<run_id>`

## What changed

- Added `apps/web/src/PublicPassportPage.tsx`.
- Kept `apps/web/src/App.tsx` integration small:
  - imports the public passport component
  - detects `/passport/:runId`
  - routes to the public passport page
- Added public passport styles to `apps/web/src/styles.css`.
- Added Render static-site rewrite in `render.yaml`:
  - `/passport/*` → `/index.html`

## Proof Score

The Proof Score is deterministic and UI-local.

It scores visible passport evidence completeness:

- run identity
- campaign linkage
- prompt/campaign context
- dry-run/live explicitness
- provider/model state
- attempt ledger presence
- asset list presence
- manifest field presence
- fallback status
- truth boundary visibility

Badge mapping:

- 90–100: Verified
- 70–89: Mostly verified
- 40–69: Partial evidence
- 0–39: Weak evidence

## Local behavior smoke

Smoke result JSON:

{
  "ok": true,
  "campaign_status_code": 201,
  "run_status_code": 201,
  "passport_status_code": 200,
  "campaign_id": "camp_363dc577f0974c46bdb4df6d0b66de74",
  "run_id": "run_0664374a2b6745f684385e9b53532739",
  "passport_api_status": "verified",
  "safe_dry_run": true,
  "provider_call": false,
  "b2_write": false,
  "public_passport_path": "/passport/run_0664374a2b6745f684385e9b53532739"
}

Validated:

- `POST /campaigns` returned `201`.
- `POST /runs` returned `201`.
- `GET /runs/{run_id}/passport` returned `200`.
- Safe dry-run stayed enabled.
- No provider call occurred.
- No B2/Genblaze write occurred.
- Built frontend bundle contains public passport UI markers:
  - `ProofStudio Public Provenance Passport`
  - `Proof Score`
  - `Chain of custody for AI media`

## Public demo URL pattern

After this branch is deployed to Render, create a safe dry-run from the public app or API, then open:

`https://proofstudio-web.onrender.com/passport/<run_id>`

Example local smoke path:

`/passport/run_0664374a2b6745f684385e9b53532739`

## Truth boundary

PS-019 proves:

- a public route for shareable Provenance Passport viewing
- deterministic Proof Score UI
- safe dry-run passport rendering
- no provider call by default
- no B2/Genblaze write by default
- static-site rewrite support for direct `/passport/:runId` links

PS-019 does not prove:

- legal authenticity
- C2PA authenticity
- semantic truth of generated media
- human authorship
- paid production reliability
- authentication
- production database persistence

The current public backend is still in-memory. A passport URL for a newly created run is valid while that run exists in the running backend process. Production persistence remains a later requirement.

## Live public verification

PS-019 was verified live on the deployed Render frontend and backend.

Live evidence file:

- docs/evidence/ps-019/live-public-passport-smoke-summary.json

Validated live:

- Public API health returned 200.
- POST /campaigns returned 201.
- POST /runs returned 201.
- GET /runs/{run_id}/passport returned 200.
- CORS preflight returned 200.
- Public passport deep link returned 200.
- Frontend JS bundle returned 200.
- Public passport URL: https://proofstudio-web.onrender.com/passport/run_b852f08667bf4178b931d8466be1b2c8.
- Safe dry-run stayed enabled.
- No provider call occurred.
- No B2/Genblaze write occurred.
- Render static-site rewrite was confirmed operational: /passport/* -> /index.html.
