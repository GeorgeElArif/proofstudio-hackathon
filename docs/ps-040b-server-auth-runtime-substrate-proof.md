# PS-040B Server Auth / Runtime Substrate Proof

Date: 2026-07-07
Branch: `ps-040/auth-account-system-v1`
Base: `origin/accepted/proofstudio @ 9fafa4b3b615c33accde22a13b4f9c4f734d8ed9`

## What Changed

- Added `apps/auth-server/` as a dedicated TypeScript/Node server-capable auth
  substrate.
- Added Better Auth, Drizzle ORM, PostgreSQL driver, Drizzle Kit, TypeScript,
  and local TypeScript runtime tooling to the new package only.
- Added placeholder-safe PS-040B env examples to `.env.example` and
  `.env.production.example`.
- Added Drizzle schema contract files for auth/account entities.
- Added a Better Auth boundary config factory that remains non-live in PS-040B.
- Added health/readiness route code that reports substrate readiness only.

## Server Auth Substrate Location

The substrate lives in `apps/auth-server`.

This keeps the existing Vite client static and avoids bolting cookie/session
auth into the browser-only app. It also keeps the existing FastAPI proof API
stable; PS-040B does not modify `src/proofstudio/api/**`.

## Dependencies Added

Runtime dependencies in `apps/auth-server/package.json`:

- `better-auth`
- `drizzle-orm`
- `pg`

Development dependencies:

- `@types/node`
- `@types/pg`
- `drizzle-kit`
- `tsx`
- `typescript`

No Supabase Auth dependency was added. Supabase Auth remains the documented
backup direction from PS-040A, not the primary substrate dependency.

## Env Placeholders Added

Local aliases added to `.env.example`:

- `AUTH_BASE_URL`
- `AUTH_SECRET`
- `DATABASE_URL`
- `CORS_ALLOWED_ORIGINS`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GITHUB_CLIENT_ID`
- `GITHUB_CLIENT_SECRET`
- `APPLE_CLIENT_ID`
- `APPLE_TEAM_ID`
- `APPLE_KEY_ID`
- `APPLE_PRIVATE_KEY`
- `EMAIL_PROVIDER_API_KEY`
- `EMAIL_SMTP_URL`
- `DISPOSABLE_EMAIL_BLOCKLIST_SOURCE`
- `AUTH_RATE_LIMIT_WINDOW_SECONDS`
- `AUTH_RATE_LIMIT_MAX_ATTEMPTS`
- `SESSION_COOKIE_NAME`
- `SESSION_COOKIE_DOMAIN`
- `SESSION_COOKIE_SECURE`

Canonical `PROOFSTUDIO_*` names were added to `.env.production.example` for the
production template. All values are obvious placeholders.

## Schema Files Added

`apps/auth-server/src/db/schema.ts` defines Drizzle tables/enums for:

- user
- account
- session
- verification token
- role
- membership
- auth audit event
- email domain policy entry
- rate-limit counter

`apps/auth-server/drizzle.config.ts` points Drizzle Kit at that schema, but no
migrations were generated and no database was contacted.

PS-040B intentionally does not run `drizzle-kit check`: this slice has no
generated migrations and no `drizzle/meta/_journal.json`. Migration generation
and migration checking belong to PS-040C. PS-040B validation relies on
TypeScript typecheck/build for the Drizzle schema/config skeleton.

## Runtime Boundary Decision

PS-040B establishes a dedicated server boundary for later auth work. The
current `/auth/*` response is intentionally `503` and documented as non-live.
The package can be typechecked and built without real OAuth, email, auth
secret, or database credentials.

PS-040C should continue by wiring Better Auth handlers, the Drizzle adapter,
database migrations, email verification behavior, OAuth provider configuration,
rate limiting, audit hooks, and auth smokes against placeholder-safe env.

## Deliberately Not Implemented

- Login page
- Signup page
- Account page
- OAuth buttons
- Live OAuth callback success flow
- Email verification UI
- Live email sending
- Dashboard
- Runtime session issuance
- Seed users, fake users, or fake sessions
- LocalStorage auth or client-only auth
- FastAPI proof API changes
- Evidence mutation

## Security And Trust Boundaries

Auth proves account/session identity only.
Auth does not prove semantic truth.
Auth does not prove legal status of artifacts.
Auth does not prove who created an artifact.
Auth does not prove content credential status.
ProofStudio proves what the pipeline recorded. Proof does not equal truth.

PS-040B does not claim enterprise-grade controls, production-grade compliance,
browser-side B2 byte verification, public deployment verification, immutable
storage controls, or write-once storage.

## Validation Results

- `npm run typecheck`: PASS
- `npm run build`: PASS
- `npm install --package-lock-only --ignore-scripts --dry-run`: PASS
- `npm audit --omit=dev`: INCONCLUSIVE due
  `getaddrinfo EAI_AGAIN registry.npmjs.org`; no vulnerability count claimed.
- `git diff --check`: PASS
- Hidden Git flag scan: PASS
- Forbidden scan: PASS
- Secret scan: PASS
- `drizzle:check` was intentionally removed from PS-040B because no migrations
  exist yet; migration generation/checking belongs to PS-040C.
