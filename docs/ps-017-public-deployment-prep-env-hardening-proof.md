# PS-017 Public Deployment Prep + Environment Hardening — Proof

## Status

**Complete (docs + env template + tiny CORS/env compatibility fix + smoke).**
PS-017 prepares ProofStudio for a future real public deployment **without
claiming deployment is complete**. It adds a production env template, a
deployment doc set, a platform-decision page (pending), a preflight checklist,
and a non-network smoke that verifies all of the above plus the existing
default safe dry-run path.

No public URL is provisioned. No platform is selected. No live provider or B2
call is made by the smoke.

## Files created

- `.env.production.example` — production env template (placeholders only).
- `docs/deployment/README.md` — deployment runbook + status.
- `docs/deployment/environment.md` — full variable reference.
- `docs/deployment/cors-and-security.md` — local vs production CORS strategy.
- `docs/deployment/platform-decision.md` — platform requirements; **pending**.
- `docs/deployment/preflight-checklist.md` — before/after deploy checklist.
- `scripts/ps017_deployment_prep_smoke.py` — deployment-prep smoke.
- `docs/ps-017-public-deployment-prep-env-hardening-proof.md` — this file.

Allowed modified files:

- `README.md` — added a short deployment-prep pointer.
- `apps/web/README.md` — added a short deployment-prep pointer.
- `src/proofstudio/api/app.py` — added a tiny environment-based CORS origin
  reader (`_resolve_cors_origins()` + `CORS_ORIGINS_ENV_VAR`). Local demo
  origins are preserved exactly; production origins from
  `PROOFSTUDIO_CORS_ORIGINS` are merged in (deduped); wildcard production CORS
  (`*`) is refused; `allow_credentials` stays `false`.

## Backend changed

**Yes — tiny, explicitly allowed, and documented.** One file changed:
`src/proofstudio/api/app.py`. The change adds:

- `import logging`, `import os`, a module-level `logger`,
- `CORS_ORIGINS_ENV_VAR = "PROOFSTUDIO_CORS_ORIGINS"`,
- `_resolve_cors_origins()`, which returns the local allow-list when the env
  var is unset (backward compatible), refuses `*`, and otherwise merges the
  comma-separated origins with the local defaults (deduped),
- a single call-site change `allow_origins=list(LOCAL_DEMO_CORS_ORIGINS)` →
  `allow_origins=_resolve_cors_origins()`.

No route, model, service, store, provider, B2, provenance, or passport logic
was touched. The change is the minimum needed so a deployed frontend origin
does not get CORS-blocked by a backend that previously only knew local origins.

## Frontend changed

**No app-source change.** `apps/web/src/api.ts` already supported
`VITE_PROOFSTUDIO_API_BASE_URL` with a local fallback, so no edit was needed.
Only `apps/web/README.md` was updated with a deployment-prep pointer.

## Environment template

`.env.production.example` contains placeholders only. Required keys:

- `PROOFSTUDIO_ENV=production`
- `PROOFSTUDIO_API_HOST=0.0.0.0`
- `PROOFSTUDIO_API_PORT=8000`
- `PROOFSTUDIO_PUBLIC_API_BASE_URL=https://replace-with-api-host`
- `PROOFSTUDIO_PUBLIC_WEB_URL=https://replace-with-web-host`
- `PROOFSTUDIO_CORS_ORIGINS=https://replace-with-web-host`
- `VITE_PROOFSTUDIO_API_BASE_URL=https://replace-with-api-host`
- `PROOFSTUDIO_RUN_LIVE_DEFAULT=false`

Optional provider/storage keys (placeholders only):

- `B2_BUCKET=replace-me`
- `B2_REGION=replace-me`
- `B2_KEY_ID=replace-me`
- `B2_APP_KEY` — placeholder `replace-me`
- `CLOUDFLARE_ACCOUNT_ID=replace-me`
- `CLOUDFLARE_API_TOKEN` — placeholder `replace-me`
- `GEMINI_API_KEY` — placeholder `replace-me`
- `ELEVENLABS_API_KEY` — placeholder `replace-me`

The smoke verifies every value is a known placeholder (`replace-me`,
`https://replace-with-api-host`, `https://replace-with-web-host`,
`production`, `0.0.0.0`, `8000`, `false`) and that no secret-like key carries
a real-looking token.

## CORS strategy

- Local demo origins (unchanged): `http://127.0.0.1:5173`,
  `http://localhost:5173`, `http://127.0.0.1:4173`, `http://localhost:4173`.
- Production origins are read from `PROOFSTUDIO_CORS_ORIGINS` and merged with
  the local defaults (deduped).
- Wildcard production CORS (`*`) is refused by the backend reader; it logs a
  warning and falls back to local-only.
- `allow_credentials` remains `false`. The Review Room does not use cookies or
  HTTP auth.
- Full rationale and setup steps: `docs/deployment/cors-and-security.md`.

## Frontend API base URL strategy

The frontend reads `VITE_PROOFSTUDIO_API_BASE_URL` (Vite build-time) and falls
back to `http://127.0.0.1:8000` only when it is unset. For a production build,
`VITE_PROOFSTUDIO_API_BASE_URL` must be set to the public API host in the
build environment; a production bundle should not silently fall back to
localhost. The value must match the origin(s) in the backend's CORS allow-list.

No code change was needed in `apps/web/src/api.ts`; the strategy is documented
in `docs/deployment/cors-and-security.md` and `docs/deployment/environment.md`.

## No-secret proof

- `.env.production.example` contains only placeholders. The smoke parses every
  `KEY=value` line and rejects any value that is not a known placeholder.
- The smoke scans the env template, every `docs/deployment/*` file, and this
  proof doc for real secret patterns (bearer tokens, real Backblaze B2 object
  URLs, and secret-key assignments whose value matches a real-looking token).
- The smoke scans its own transcript JSON before writing and fails if any
  secret pattern appears there.
- No real B2 keys, Cloudflare tokens, Gemini keys, or ElevenLabs keys are
  present anywhere in the slice.

## Default no-live proof

The smoke drives the default API path through `TestClient`:

1. `POST /campaigns` → `201`.
2. `POST /runs` (default — no `run_live`, no `dry_run=false`) → `201` with
   `status=dry_run_created`, `dry_run=true`, `run_live=false`.
3. `GET /runs/{id}/attempts` → `attempt_count=0`.
4. `GET /runs/{id}/assets` → `asset_count=0`.
5. `GET /runs/{id}/manifest` → `ready=false`.

Structural evidence of a live provider call (`selected_provider` set, or any
attempts recorded) and of a B2 call (any asset with a `b2_url`, or
`stored_manifest_verify` set) are both absent. The default path is honest.

## Deployment status

**`prep_only`**. Preparation is complete; deployment has not happened. No
platform is selected. No public URL is provisioned. `public_url_status` is
**`pending`**.

## Limitations

- No public deployment exists. The slice prepares the path; a later slice must
  choose a platform, provision real URLs, set real secrets in the platform
  secret manager, and walk the "After deploying" preflight list.
- The backend's live store is still in-memory (no production persistence).
- No authentication or authorization layer.
- The slice adds the CORS/env reader but does not exercise it against a real
  deployed frontend (there is none yet).
- `.env.production.example` is the only env file allowed in the repo; any real
  `.env.production` must remain git-ignored / in the platform secret manager.

## Next milestone recommendation

Pick a platform (see `docs/deployment/platform-decision.md`), provision real
public API + web URLs, set real secret values in the platform secret manager,
build the frontend with the public `VITE_PROOFSTUDIO_API_BASE_URL`, deploy
backend + frontend, and walk the "After deploying" section of
`docs/deployment/preflight-checklist.md`. Only then record the real public URL
in `docs/submission/submission-checklist.md`. Record the ~3-minute demo against
the deployed URL following `docs/submission/recording-runbook.md`.

## Truth boundary

PS-017 proves ProofStudio has deployment preparation, environment templates,
and preflight checks for moving from local demo to public hosting. It does
**not** prove:

- public deployment;
- a working public app URL;
- final Devpost submission;
- production availability;
- authentication;
- production persistence;
- background job reliability;
- legal authenticity;
- C2PA authenticity;
- semantic truth;
- human authorship.
