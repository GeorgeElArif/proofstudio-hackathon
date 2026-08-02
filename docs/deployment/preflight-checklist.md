# ProofStudio — Preflight Checklist

## PS-042C0B free staging synchronization steps

All live steps remain unchecked and require separate PS-042C0B authorization:

- [ ] Confirm the workspace has an unused free Postgres slot.
- [ ] Confirm included instance hours, bandwidth, and pipeline minutes remain.
- [ ] Confirm the Blueprint preview shows only free resources.
- [ ] Confirm estimated recurring price is `$0.00`.
- [ ] Confirm exact resource names and expected `onrender.com` hostnames.
- [ ] Create the Blueprint with Auto Sync disabled.
- [ ] Run migrations with temporary exact-IP database access.
- [ ] Remove database external access immediately after migration.
- [ ] Deploy services.
- [ ] Run live health and gateway checks.
- [ ] Provision synthetic staging accounts.
- [ ] Never provision a real judge account.

Stop if the preview shows a non-zero charge or if Render does not assign the
exact `proofstudio-auth.onrender.com` hostname required by the checked-in
same-origin rewrites.

## PS-042B2 future production judge-access steps

PS-042B2 validates these operations locally only. Every production step remains
unchecked and requires separate authorization:

- [ ] Apply database migrations `0000`, `0001`, and `0002` to the confirmed
      production auth database; record the migration result without credentials.
- [ ] Obtain explicit judge-provisioning approval and set the approval variable
      to exact lowercase `true` only for the bounded operator action.
- [ ] Provision the judge account with the minimum `viewer` role and the exact
      approved campaign linkage.
- [ ] Verify production login, session readback, linked dashboard campaign,
      private Proof Room, Passport, lineage reads, denials, logout, and session
      invalidation.
- [ ] Deliver the credential through private Devpost judge instructions after
      verifying the destination and access scope.
- [ ] After judging, rotate the credential or disable the account, revoke its
      active campaign access, and revoke active sessions.

## PS-042B1 release-candidate preflight (no deployment)

- [ ] Verify the branch and accepted ref match the authorized PS-042B1 base;
      zero commits are ahead before work and the index is empty.
- [ ] Verify exactly the allowlisted paths changed, no lockfile changed, and
      `git ls-files -v` contains no `h` or uppercase `S` index flags.
- [ ] Run `git diff --check` and the exact `apps/web/package.json` script check.
- [ ] Run `python3 scripts/ps042b1_render_blueprint_smoke.py`; require four
      resources, one duplicate-free route mapping, seven ordered rewrites,
      six no-store rules, current Blueprint fields, explicit service-reference
      types, default-off live flags, and zero external counters.
- [ ] Run auth typecheck/build/Drizzle check, production-topology smoke, and all
      existing auth behavior/account/private-proof/lineage smokes.
- [ ] Against an empty local PostgreSQL instance only, apply migrations `0000`,
      `0001`, `0002`; invoke the migration gate a second time and verify tables
      and indexes. Never use a production connection string.
- [ ] Run web typecheck/build plus auth-client, account/private-proof/lineage,
      and production-auth-gateway smokes.
- [ ] Run focused FastAPI tests and the central non-mutating gate with
      `--current ps042b1 --frontend --report-out /tmp/...`.
- [ ] Compare the canonical PS-034A report SHA-256 before and after validation.
- [ ] Run the classified secret scan; classify only the three known auth schema
      field mappings as runtime redaction-shaped literals and require zero
      credential findings.
- [ ] Confirm provider, B2, Render, production-database and deployment counters
      all remain zero.

PS-042B1 stops here. Do not synchronize the Blueprint, create paid resources,
run production migrations, provision a judge, or contact Render. Those are
separately authorized PS-042C operations.

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


Walk this list before and after any real public deployment. PS-017 prepared the
deployment path; **PS-018 selects Render** as the target and adds the live URL
smoke step. The actual deploy + URL verification happens against Render (see
[`render.md`](./render.md) and [`platform-decision.md`](./platform-decision.md)).

## Before deploying

- [x] **Choose platform.** PS-018 selects **Render**. Re-read Render's current
      docs before the real deploy.
- [ ] **Set public API URL.** Provision `https://replace-with-api-host` and put
      the real value into `PROOFSTUDIO_PUBLIC_API_BASE_URL` and
      `VITE_PROOFSTUDIO_API_BASE_URL` (the latter in the Render static-site
      build environment).
- [ ] **Set public frontend URL.** Provision `https://replace-with-web-host`
      and put the real value into `PROOFSTUDIO_PUBLIC_WEB_URL`.
- [ ] **Set CORS origins.** Put the real frontend origin(s) into
      `PROOFSTUDIO_CORS_ORIGINS`. Never use `*` in production. Mirror
      `PROOFSTUDIO_PUBLIC_WEB_URL`.
- [ ] **Configure secrets.** Put real B2 / Cloudflare / Gemini / ElevenLabs
      values into the Render dashboard (use the `sync: false` slots in
      `render.yaml`). Leave them as `replace-me` in `.env.production.example`
      (the repo copy never holds real secrets). Secrets are optional for a
      dry-run-only public demo.
- [ ] **Run local smoke.**
      `python scripts/ps017_deployment_prep_smoke.py` must pass clean.
- [ ] **Run PS-018 live URL smoke (local contract mode).**
      `python scripts/ps018_live_url_smoke.py` must pass clean (no providers,
      no B2). Confirm `ok: true`, `selected_target: render`,
      `live_url_smoke_status: skipped_missing_urls`.
- [ ] **Run frontend build.**
      `cd apps/web && npm run build` must pass clean, with
      `VITE_PROOFSTUDIO_API_BASE_URL` set to the public API URL.
- [ ] **Confirm live mode default is false.**
      `PROOFSTUDIO_RUN_LIVE_DEFAULT=false`. Provider/B2 must never run by
      default.
- [ ] **Confirm no `.env` is committed.** No `.env`, `.env.local`, or
      `.env.production` (with real values) may be tracked by git. Only
      `.env.production.example` is allowed in the repo, and only with
      placeholder values.

## After deploying

- [ ] **Verify public `/health`.**
      `GET <api-url>/health` returns `{ok: true, ...}`.
- [ ] **Verify public `/version`.**
      `GET <api-url>/version` returns the service/version.
- [ ] **Verify frontend API status.** Open the Review Room at the public web
      URL; the **API Status** card must report the backend online (no CORS
      block, no network error).
- [ ] **Create a safe dry-run.** Create a campaign and run a dry-run. Confirm
      status `dry_run_created`, no media, no manifest, no provider call, no B2
      call.
- [ ] **Confirm no provider/B2 call by default.** Inspect backend logs; the
      dry-run path must not have hit a provider or B2.
- [ ] **Run PS-018 live URL smoke (live URL mode).** With the real public URLs:

      ```bash
      export PS018_RUN_LIVE_URL_SMOKE=true
      export PROOFSTUDIO_PUBLIC_API_BASE_URL=https://<real-api-host>
      export PROOFSTUDIO_PUBLIC_WEB_URL=https://<real-web-host>
      python scripts/ps018_live_url_smoke.py
      ```

      It must report `live_url_smoke_status: passed`,
      `public_url_verified: true`, CORS preflight ok, and a clean safe dry-run.
- [ ] **Optionally run an explicit live proof.** With real provider/B2 keys
      configured, toggle live mode and create a live proof run. Accept honest
      `live_completed` / `live_failed` / `live_blocked` outcomes.
- [ ] **Update the submission checklist.** Only **after** the PS-018 live URL
      smoke passes, record the real public URL in
      `docs/submission/submission-checklist.md` and flip the working-app-URL
      item from **PENDING** to done. Do not record a URL that has not been
      verified live.

## Truth boundary

This checklist defines what "ready to deploy" and "deployed" mean for
ProofStudio. Walking the "Before" list does not mean the app is deployed.
Walking the "After" list only proves the items actually checked. It does
**not** prove final Devpost submission, authentication, production persistence,
legal authenticity, C2PA authenticity, semantic truth, or human authorship.

## PS-018B completion status

PS-018B public deployment verification is complete.

- [x] Public API URL provisioned: `https://proofstudio.onrender.com`
- [x] Public web URL provisioned: `https://proofstudio-web.onrender.com`
- [x] Backend `/health` verified.
- [x] Backend `/version` verified.
- [x] Frontend public load verified.
- [x] CORS preflight verified from frontend origin.
- [x] PS-018 live URL smoke passed in explicit live URL mode.
- [x] Semantic public dry-run verified safe defaults: no provider call, no B2/Genblaze write.
