# PS-040F Configured Auth Runtime + Email/OAuth Readiness Proof

Date: 2026-07-10
Branch: `ps-040/auth-account-system-v1`
Base: `origin/accepted/proofstudio @ 365098e6908fa4e65a45f34befdc84609b1877c4`

## What Changed

- Added a shared database URL safety classifier for auth DB and migration smokes.
- Added a package-local disposable Postgres Compose service for local configured auth smokes.
- Added guarded migration, DB safety, configured auth runtime, and email/OAuth readiness smokes.
- Added local email capture readiness mode that does not send live email and does not verify email.
- Fixed Better Auth Drizzle runtime compatibility for text IDs, snake-case field mappings, and account provider mapping.
- Added a web configured auth client smoke that reads configured runtime readiness and session state from the local auth server.

## Safe DB Strategy

PS-040F uses `apps/auth-server/docker-compose.auth-test.yml` by default:

- host: `127.0.0.1`
- port: `55440`
- database: `proofstudio_auth_smoke_test`
- purpose: disposable local auth smoke database

The DB is local-only and can be removed with `npm run db:test:down`, which runs Compose with `down -v`.

## DB URL Safety Rules

The classifier returns:

- `missing`
- `local_test`
- `explicit_nonlocal_test_allowed`
- `unsafe_nonlocal`
- `production_like`
- `invalid`

Only `local_test` is accepted by default. A nonlocal database is accepted only as
`explicit_nonlocal_test_allowed` when `AUTH_ALLOW_NONLOCAL_TEST_DB=true` and the
database name clearly identifies disposable test use. Production-looking hosts
or names are refused. Scripts print only classification, host, database name,
protocol, and reasons; they do not print passwords or full URLs.

## Migration Smoke Result

`npm run db:test:migrate` applied committed Drizzle migrations to the disposable local DB and verified all expected auth tables. It also verified Better Auth core ID columns are text-compatible.

Observed result:

- `result`: `passed`
- `database.classification`: `local_test`
- required tables present: `9`

## Configured Auth Runtime Smoke Result

`npm run smoke:configured-auth` started the auth server with explicit PS-040F local test env and the disposable DB.

Observed result:

- `/healthz`: process-live
- `/readyz`: `200`, ready
- `/session` before signup: unauthenticated, no user
- email/password signup: accepted by Better Auth
- runtime user row: created
- `email_verified`: `false`
- login before email verification: rejected with `403`
- session after signup: unauthenticated
- logout without session: `401`, not performed

No fake user, fake session, seed user, or client-only auth state was added.

## Email Readiness Result

`npm run smoke:email-oauth-readiness` verifies:

- missing email config reports `unavailable`
- `PROOFSTUDIO_EMAIL_PROVIDER=capture` with `PROOFSTUDIO_EMAIL_CAPTURE_MODE=local` reports local capture
- capture mode does not send live email
- capture mode does not fake email verification success

Live SMTP/API delivery remains deferred to a provider-owned slice.

## OAuth Readiness Result

The readiness smoke checks Google, GitHub, and Apple config shapes without live provider calls.

Observed checks:

- Google placeholders are classified as `placeholder`
- partial GitHub config is classified as `invalid_shape`
- local-test-shaped Google config is `configured`
- local-test-shaped GitHub config is `configured`
- local-test-shaped Apple config is `configured`

No live OAuth redirect, callback, provider token exchange, or provider account success is claimed.

## Web Configured Runtime Result

`apps/web` includes `npm run smoke:configured-auth-client`. It starts the local auth server against the disposable DB, checks configured readiness, and verifies session readback returns unauthenticated with no user when no server-owned session exists.

The web client continues to use `credentials: "include"` and does not store auth in `localStorage` or `sessionStorage`.

## What Is Live Now

- Better Auth can run against a safe local/test Postgres DB.
- Committed migrations can be applied to a disposable local DB.
- Email/password signup can create a real unverified local test user through the runtime.
- Session readback remains server-owned.
- Login is blocked before email verification.
- Email/OAuth readiness can be classified without logging secrets or contacting providers.

## Deliberately Not Live

- Dashboard UI.
- PS-041.
- Campaign list behind auth.
- Proof room access control.
- Admin UI.
- Production deployment.
- Production email delivery.
- Production OAuth provider success.
- Live OAuth redirects/callbacks.
- Seed users.
- Fake users or fake sessions.
- Client-only auth state.
- FastAPI proof API changes.

## Trust Boundaries

Auth proves account/session identity only.
ProofStudio proves what the pipeline recorded. Proof does not equal truth.

Auth does not prove semantic truth.
Auth does not prove legal authenticity.
Auth does not prove human authorship.
Auth does not prove C2PA authenticity.
PS-040F does not claim Object Lock, tamper-proof storage, enterprise security, production compliance, or public deployment verification.

## Known Limitations

- Email verification delivery is captured locally only; live delivery is not tested.
- No verification-link consumption flow is implemented in this slice.
- OAuth readiness validates env shape and callback/base URL consistency only; no provider callback is exercised.
- Rate limiting remains local/database-backed for the auth runtime smoke, not a distributed production claim.
- Web configured smoke validates the web auth client boundary against the configured auth server; it does not add dashboard behavior.

## Next Slice Recommendation

The next PS-040 slice should use approved provider test credentials to exercise live email delivery and provider-specific OAuth callback behavior, then add verification-link handling if approved. PS-041 dashboard work should remain separate.
