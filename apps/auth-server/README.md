# ProofStudio Auth Server Substrate

PS-040F hardens this package as the dedicated server-capable auth/runtime surface
for Better Auth + Drizzle + Supabase Postgres.

Current status:

- Real Better Auth handler exists behind env and database readiness gates.
- No login/signup UI.
- No OAuth callbacks.
- OAuth providers are configured only when provider credentials are present.
- Email verification is shaped, but live email delivery is still deferred.
- Disposable-domain, rate-limit, RBAC, readiness, and audit foundations have
  deterministic no-secret smokes.
- Initial Drizzle migrations are committed under `drizzle/`.
- `docker-compose.auth-test.yml` provides a disposable local-only Postgres
  service for configured auth runtime smokes.
- No provider calls during build or typecheck.

`/healthz` reports the server process is live. `/readyz` reports env readiness,
safe provider readiness categories, database reachability when env is
configured, and auth runtime availability.
`/auth/*` returns a `503` JSON boundary response while required env is missing
or placeholder-safe, and only reaches Better Auth after the gate passes.

Useful local commands:

- `npm run test:policy`
- `npm run smoke:missing-env`
- `npm run smoke:readiness`
- `npm run smoke:auth-behavior`
- `npm run smoke:auth-db`
- `npm run db:test:up`
- `npm run db:test:migrate`
- `npm run smoke:configured-auth`
- `npm run smoke:email-oauth-readiness`
- `npm run db:test:down`

`smoke:auth-db`, `db:test:migrate`, and `smoke:configured-auth` refuse to run
unless the database URL is classified as `local_test` or as
`explicit_nonlocal_test_allowed` with `AUTH_ALLOW_NONLOCAL_TEST_DB=true`. The
scripts print only the classification, host, database name, and reasons; they
do not print passwords or full database URLs. The default target is the
package-local Compose database on `127.0.0.1:55440` named
`proofstudio_auth_smoke_test`.

Email provider `capture` with `PROOFSTUDIO_EMAIL_CAPTURE_MODE=local` is a
local/test readiness mode only. It lets Better Auth request email verification
without sending live email and without marking verification complete.

Trust boundary: Auth proves account/session identity only. It does not verify
artifact meaning, legal status, creator identity, or content credentials.
ProofStudio proves what the pipeline recorded. Proof does not equal truth.
