# PS-040C Better Auth Runtime Wiring + Drizzle Migrations Proof

Date: 2026-07-07
Branch: `ps-040/auth-account-system-v1`
Base: `origin/accepted/proofstudio @ 6aa53a33d63a962844e32244fcaac89d0966a453`

## What Changed

- Replaced the PS-040B `/auth/*` placeholder with a gated Better Auth runtime
  boundary in `apps/auth-server`.
- Wired Better Auth to Drizzle/Postgres through the installed
  `drizzleAdapter(db, { provider: "pg", schema })` API.
- Kept database initialization lazy and request/runtime scoped; import,
  typecheck, and build do not contact a database.
- Updated the Drizzle schema so Better Auth core models use compatible fields
  while preserving ProofStudio auth audit, RBAC, email-domain policy, and
  rate-limit foundation tables.
- Generated and committed the initial Drizzle migration under
  `apps/auth-server/drizzle/`.
- Added package-local scripts for Drizzle generation/checking/migration and a
  missing-env auth boundary smoke.

## Runtime Boundary Behavior

- `/healthz` returns a process-live response and does not check the database.
- `/readyz` reports env configuration, database reachability when env is
  configured, and auth runtime availability.
- `/auth/*` fails closed with a `503` JSON response while required env values
  are missing or placeholder-safe.
- `/auth/*` checks database reachability before handing a request to Better
  Auth when env is configured.
- The server binds to `127.0.0.1` by default for local smokes.

## Env Gating Behavior

The runtime gate requires non-placeholder values for:

- `PROOFSTUDIO_APP_BASE_URL` or `AUTH_BASE_URL`
- `PROOFSTUDIO_PUBLIC_WEB_URL`
- `PROOFSTUDIO_AUTH_SECRET` or `AUTH_SECRET`
- `PROOFSTUDIO_DATABASE_URL` or `DATABASE_URL`
- `PROOFSTUDIO_CORS_ORIGINS` or `CORS_ALLOWED_ORIGINS`
- `PROOFSTUDIO_EMAIL_PROVIDER` or `EMAIL_PROVIDER`
- `PROOFSTUDIO_EMAIL_FROM` or `EMAIL_FROM`
- `PROOFSTUDIO_DISPOSABLE_EMAIL_BLOCKLIST_SOURCE` or
  `DISPOSABLE_EMAIL_BLOCKLIST_SOURCE`

OAuth credentials are optional for typecheck/build and are only attached when
the corresponding provider config is present.

## Migration Files Generated

- `apps/auth-server/drizzle/0000_bent_bullseye.sql`
- `apps/auth-server/drizzle/meta/0000_snapshot.json`
- `apps/auth-server/drizzle/meta/_journal.json`

No live database migration was applied.

## Scripts Added Or Changed

- `drizzle:generate`: `drizzle-kit generate`
- `drizzle:migrate`: `drizzle-kit migrate`
- `drizzle:check`: `drizzle-kit check`
- `smoke:missing-env`: builds the package and runs the no-env auth boundary
  smoke with plain Node.

`drizzle-kit generate --dry-run` is not supported by installed Drizzle Kit
`0.31.10`; the command returns `Unrecognized options for command 'generate':
--dry-run`.

## Smoke Tests Added

`scripts/smoke-missing-env.ts` starts the auth server with auth env stripped and
asserts:

- `/healthz` returns a live server response.
- `/readyz` returns `503` and not-ready without required env.
- `/auth/session` returns fail-closed `503` without required env.
- no fake `user` or `session` object is returned.

## What Is Live Now

- A real Better Auth handler exists behind the runtime gate.
- Drizzle/Postgres adapter wiring exists behind the runtime gate.
- Better Auth email/password shape requires email verification.
- Better Auth database rate-limit storage is configured when runtime is live.
- Structured audit hook foundation logs account/session events without
  persisting fake audit rows.

## Deliberately Not Live

- No login UI.
- No signup UI.
- No dashboard UI.
- No fake users.
- No fake sessions.
- No live email sending.
- No provider calls during build/typecheck/smoke.
- No FastAPI proof API changes.
- No proof/evidence mutation.
- No PS-041 implementation.

## PS-040D Continuation Notes

PS-040D should add the approved live email provider integration, disposable
domain validation smokes, rate-limit behavior smokes, RBAC/account smokes, and
database-persisted audit events. It should also validate the provider-specific
OAuth credential shapes against live approved test credentials only when PM
approves that provider behavior.

## Validation Results

- `git fetch origin`: PASS after approved `.git/FETCH_HEAD` write.
- `git switch -C ps-040/auth-account-system-v1 origin/accepted/proofstudio`:
  PASS.
- `npm ci --ignore-scripts`: PASS.
- `npm run typecheck`: PASS.
- `npm run build`: PASS.
- `npm run smoke:missing-env`: PASS with approved local loopback bind
  escalation.
- `npm run drizzle:generate`: PASS; migration generated.
- `npm run drizzle:generate -- --dry-run`: NOT SUPPORTED by installed Drizzle
  Kit.
- `npm run drizzle:check`: PASS.
- `npm install --package-lock-only --ignore-scripts --dry-run`: PASS.
- `npm audit --omit=dev`: PASS after approved network retry; found 0
  vulnerabilities.
- `git diff --check`: PASS.
- hidden Git flag scan with `git ls-files -v | rg '^[hS]'`: PASS, no matches.

## Trust Boundaries

Auth proves account/session identity only.
Auth does not prove semantic truth.
Auth does not prove legal authenticity.
Auth does not prove human authorship.
Auth does not prove C2PA authenticity.
ProofStudio proves what the pipeline recorded. Proof does not equal truth.
