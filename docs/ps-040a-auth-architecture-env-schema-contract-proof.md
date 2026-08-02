# PS-040A Auth Architecture + Env/Schema Contract Proof

Date: 2026-07-07
Branch: `ps-040/auth-account-system-v1`
Base: `origin/accepted/proofstudio @ 24d0b695920dbcb0a8fa0357951ddfe3164e9dfc`

## What Changed

- Added `specs/65-ps-040-auth-account-system.md` as the canonical PS-040
  implementation contract.
- Added this proof document.
- Added a minimal PS-040A pointer in `specs/08-roadmap-slices.md`.

## Why This Is Contract-First

PS-040 requires real auth and durable account storage, but the current product
surface is split between a Vite React static/client app and a FastAPI proof API
with an in-memory store. PS-040A records the provider, env, schema, route,
runtime-boundary, trust-boundary, and later acceptance-gate contract before any
runtime auth work starts.

No login/signup UI, real auth endpoints, migrations, dependencies, secrets, or
fake auth were added.

## Sources Inspected

- `specs/08-roadmap-slices.md`
- `specs/62-ps-038b-winning-product-presentation-architecture.md`
- `specs/64-ps-039a-website-dashboard-build-authority-visual-rebuild-contract.md`
- `.env.example`
- `.env.production.example`
- `docs/deployment/environment.md`
- `docs/deployment/cors-and-security.md`

## Decisions Locked

- Better Auth is the primary auth provider direction.
- Supabase Auth is the backup auth provider direction.
- Supabase Postgres is the database direction.
- Drizzle ORM is the ORM direction.
- Current Vite-static plus FastAPI-in-memory architecture is not sufficient for
  runtime auth without a server-capable auth boundary.
- V1 should keep the existing FastAPI proof API stable and add a dedicated
  server-capable auth surface for Better Auth + Drizzle + Supabase Postgres,
  unless a later implementation slice documents an approved alternative.
- PS-040 remains auth/account focused and does not include PS-041 dashboard
  work.

## Decisions Deferred

- Exact server substrate and framework files for Better Auth.
- Whether Supabase client keys are needed beyond a server database URL.
- Exact email provider.
- Exact disposable-domain source.
- Exact rate-limit store.
- Exact schema implementation and migrations.
- Exact auth smoke implementation.

## Risks

- Runtime auth can drift if a later implementation tries to attach cookie or
  session behavior to static Vite without a server boundary.
- OAuth/email verification cannot be validated until placeholder-safe provider
  configuration and smokes exist.
- Email deliverability checks can accidentally reject legitimate company or
  custom domains unless the allowlist/blocklist logic is conservative and
  observable.
- RBAC and audit hooks must be built with account-specific boundaries and must
  not become proof-truth claims.

## Validation Run

PS-040A validation run:

- `git diff --check`
- `git status --short`
- `git ls-files -v | rg '^[hS]' || true`
- forbidden-claim scan over `specs`, `docs`, `.env.example`, and
  `.env.production.example`

Results are recorded in
`/tmp/proofstudio-ps040a-auth-contract-pack/validation.txt` and
`/tmp/proofstudio-ps040a-auth-contract-pack/forbidden-scan.txt`.

Frontend build was not run because PS-040A changes no app code. Backend tests
were not run because PS-040A changes no backend code.

## Runtime Auth Confirmation

PS-040A implemented no runtime auth.

PS-040A added:

- no login/signup UI
- no real auth endpoints
- no database migrations
- no auth dependency installs
- no fake auth path
- no provider calls
- no B2/archive changes
- no evidence mutation

## Dependency Confirmation

No dependencies were installed.

## Secret Confirmation

No secrets were added. Environment variable names and placeholder examples are
documented only in the PS-040 spec. No real credentials, tokens, OAuth secrets,
private keys, database URLs, or email provider keys were added.

## Truth Boundary Confirmation

PS-040A records that auth proves account/session identity only. It does not
claim semantic truth, legal authenticity, human authorship, C2PA authenticity,
enterprise security, production compliance, Object Lock, tamper-proof storage,
browser-side B2 byte verification, or public deployment verification.
