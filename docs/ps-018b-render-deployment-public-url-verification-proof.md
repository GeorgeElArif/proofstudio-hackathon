# PS-018B — Render Deployment Public URL Verification Proof

## Status

PS-018B is verified.

ProofStudio now has public Render URLs for both backend and frontend:

- Public frontend: `https://proofstudio-web.onrender.com`
- Public backend: `https://proofstudio.onrender.com`

## Backend verification

The backend Render Web Service is live at:

`https://proofstudio.onrender.com`

Verified public API routes:

- `/health`
- `/version`

The backend reports production mode and the ProofStudio API service/version/capabilities.

## Frontend verification

The frontend Render Static Site is live at:

`https://proofstudio-web.onrender.com`

The public frontend loads successfully during the live URL smoke.

## CORS verification

The backend is configured to allow the frontend origin:

`https://proofstudio-web.onrender.com`

The semantic dry-run check confirmed:

- `access-control-allow-origin = https://proofstudio-web.onrender.com`

## Live URL smoke proof

The explicit live URL smoke was run with:

- `PS018_RUN_LIVE_URL_SMOKE=true`
- `PROOFSTUDIO_PUBLIC_API_BASE_URL=https://proofstudio.onrender.com`
- `PROOFSTUDIO_PUBLIC_WEB_URL=https://proofstudio-web.onrender.com`

Result:

- `ok = true`
- `live_url_smoke_status = passed`
- `public_api_url_status = verified`
- `public_web_url_status = verified`
- `api_health_checked = true`
- `api_version_checked = true`
- `web_load_checked = true`
- `cors_preflight_checked = true`
- `public_url_verified = true`
- `default_no_live_provider_call = true`
- `default_no_b2_call = true`

Evidence files:

- `docs/evidence/ps-018b/live-url-smoke-summary.json`
- `docs/evidence/ps-018b/live-url-smoke-transcript.json`

## Safe public dry-run proof

A separate semantic safe public dry-run was run against the public backend with the frontend origin.

Result:

- `ok = true`
- `campaign_created = true`
- `run_created = true`
- `status_is_dry_run_created = true`
- `dry_run_true = true`
- `run_live_false = true`
- `selected_provider_null = true`
- `selected_model_null = true`
- `api_method_null = true`
- `job_type_null = true`
- `attempt_count_zero = true`
- `attempts_empty = true`
- `asset_count_zero = true`
- `assets_empty = true`
- `manifest_uri_null = true`
- `manifest_hash_null = true`
- `stored_manifest_verify_null = true`
- `transfer_failures_empty = true`
- `stored_transfer_failures_empty = true`
- `default_no_live_provider_call = true`
- `default_no_b2_call = true`
- `cors_allow_origin_correct = true`

Evidence file:

- `docs/evidence/ps-018b/safe-public-dry-run-semantic.json`

## Truth boundary

PS-018B proves:

- The backend is publicly deployed on Render.
- The frontend is publicly deployed on Render.
- The public frontend URL loads.
- The public backend `/health` and `/version` routes respond.
- CORS allows the deployed frontend origin.
- Public default dry-run creates a safe run without provider calls.
- Public default dry-run performs no B2 or Genblaze storage writes.

PS-018B does not prove:

- Final Devpost submission.
- Paid production reliability.
- Authentication or user accounts.
- Production database persistence.
- Background worker reliability.
- Legal authenticity.
- C2PA authenticity.
- Semantic truth of generated media.
- Human authorship.

## Final URLs for submission draft

- App URL: `https://proofstudio-web.onrender.com`
- API URL: `https://proofstudio.onrender.com`
