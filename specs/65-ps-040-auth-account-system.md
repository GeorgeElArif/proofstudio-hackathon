# PS-040 — Auth + Account System

Status: Contract/spec only.
Slice: PS-040
Sub-slice: PS-040A — Auth Architecture + Env/Schema Contract
Date: 2026-07-07
Branch: `ps-040/auth-account-system-v1`
Spec: `specs/65-ps-040-auth-account-system.md`

## 1. Slice Identity

PS-040 is the future Auth + Account System slice. PS-040A is the
contract-first sub-slice that records the auth architecture, environment
contract, logical schema contract, route contract, and acceptance gates before
runtime auth work begins.

The accepted base for this slice is:

- ref: `origin/accepted/proofstudio`
- commit the ref resolved to at slice start:
  `24d0b695920dbcb0a8fa0357951ddfe3164e9dfc`

The ref is the authority. The commit is recorded for traceability because this
slice was explicitly opened against
`origin/accepted/proofstudio @ 24d0b695920dbcb0a8fa0357951ddfe3164e9dfc`.

PS-040A implements no runtime auth. It adds no login/signup UI, no auth API
endpoints, no database migrations, no dependencies, no secrets, no fake auth,
and no production security or compliance claims.

## 2. Roadmap Source Of Truth

Authoritative roadmap context:

- `specs/08-roadmap-slices.md`
- `specs/62-ps-038b-winning-product-presentation-architecture.md`

PS-038b recorded the high-level PS-040 auth/account direction. The roadmap
records PS-040 as Auth + Account System. There was no dedicated PS-040 spec
before PS-040A; this file is the canonical implementation contract for PS-040
going forward.

## 3. Provider And Data Direction

Implementation targets, not installed dependencies yet:

| Concern | Direction | PS-040A status |
| --- | --- | --- |
| Auth provider | Better Auth primary | Recorded only |
| Auth backup | Supabase Auth | Recorded only |
| Database | Supabase Postgres | Recorded only |
| ORM | Drizzle ORM | Recorded only |

No package install is authorized by PS-040A. Runtime implementation must happen
in a later PS-040 implementation sub-slice after PM approval.

## 4. Server Runtime Decision

Current repo mismatch:

- the current frontend is a Vite React 18 static/client app
- the current backend is FastAPI with an in-memory store
- PS-040 requires real server auth and durable account storage

Do not bolt cookie/session auth onto the static Vite client without a server
boundary. Auth cookies, OAuth callbacks, session issuance, email verification,
rate limiting, account mutations, audit hooks, and database writes require a
server-capable boundary with explicit ownership.

The implementation substrate must be decided before runtime auth work starts.
That decision must identify where Better Auth, Drizzle, Supabase Postgres,
cookie/session handling, OAuth callbacks, and account routes run.

## 5. Recommended V1 Architecture

Recommended safe V1 direction:

- keep the existing FastAPI proof API stable
- add a dedicated server-capable auth surface for Better Auth + Drizzle +
  Supabase Postgres in the web/app architecture
- preserve the proof API contracts unless a later slice explicitly owns a
  backend integration change
- do not migrate the entire product unless explicitly approved
- keep PS-040 focused on auth/account only, not the PS-041 dashboard

If repository constraints force an alternative, the later implementation slice
must document the exact approved alternative before adding runtime auth. An
approved alternative still needs a real server boundary and durable account
storage; it must not rely on static-client-only auth.

## 6. Required Capabilities

PS-040 implementation scope from the roadmap:

- Google OAuth
- Apple OAuth
- GitHub OAuth
- email/password signup
- username login if useful
- email verification before activation
- disposable/temp email blocking
- email syntax validation
- domain/MX/deliverability validation where possible
- configurable email domain allowlist/blocklist
- RBAC/account model
- rate limiting for auth-sensitive endpoints
- server-side validation
- audit hooks for important account actions

Email validation must avoid rejecting legitimate custom/company domains. Domain
and deliverability checks should be conservative, configurable, and observable
through audit-safe events.

## 7. Environment Contract

PS-040A does not add real secrets or change runtime env readers. These names
are placeholders for the later implementation contract.

| Variable | Purpose | Local | Production | Secret/public | Owner slice |
| --- | --- | --- | --- | --- | --- |
| `PROOFSTUDIO_APP_BASE_URL` | Server-visible app base URL for auth redirects | Required | Required | Public | PS-040 runtime |
| `PROOFSTUDIO_PUBLIC_WEB_URL` | Browser-visible web URL, aligned with existing deployment contract | Required | Required | Public | Existing/PS-040 runtime |
| `PROOFSTUDIO_AUTH_SECRET` | Auth/session signing secret | Required | Required | Secret | PS-040 runtime |
| `PROOFSTUDIO_DATABASE_URL` | Supabase Postgres/pooled database connection | Required | Required | Secret | PS-040 runtime |
| `PROOFSTUDIO_SUPABASE_URL` | Supabase project URL if Supabase client access is needed | Optional | Required if used | Public or server-only by usage | PS-040 runtime |
| `PROOFSTUDIO_SUPABASE_SERVICE_ROLE_KEY` | Server-only Supabase privileged key if needed | Not required unless used | Required if used | Secret | PS-040 runtime |
| `PROOFSTUDIO_GOOGLE_CLIENT_ID` | Google OAuth client id | Required for live Google OAuth | Required for live Google OAuth | Public-ish identifier | PS-040 runtime |
| `PROOFSTUDIO_GOOGLE_CLIENT_SECRET` | Google OAuth client secret | Required for live Google OAuth | Required for live Google OAuth | Secret | PS-040 runtime |
| `PROOFSTUDIO_APPLE_CLIENT_ID` | Apple OAuth client id/service id | Required for live Apple OAuth | Required for live Apple OAuth | Public-ish identifier | PS-040 runtime |
| `PROOFSTUDIO_APPLE_TEAM_ID` | Apple developer team id | Required for live Apple OAuth | Required for live Apple OAuth | Public-ish identifier | PS-040 runtime |
| `PROOFSTUDIO_APPLE_KEY_ID` | Apple private key id | Required for live Apple OAuth | Required for live Apple OAuth | Public-ish identifier | PS-040 runtime |
| `PROOFSTUDIO_APPLE_PRIVATE_KEY` | Apple OAuth private key material | Required for live Apple OAuth | Required for live Apple OAuth | Secret | PS-040 runtime |
| `PROOFSTUDIO_GITHUB_CLIENT_ID` | GitHub OAuth client id | Required for live GitHub OAuth | Required for live GitHub OAuth | Public-ish identifier | PS-040 runtime |
| `PROOFSTUDIO_GITHUB_CLIENT_SECRET` | GitHub OAuth client secret | Required for live GitHub OAuth | Required for live GitHub OAuth | Secret | PS-040 runtime |
| `PROOFSTUDIO_EMAIL_PROVIDER` | Email provider selector/config pointer | Required for email verification | Required | Public config | PS-040 runtime |
| `PROOFSTUDIO_EMAIL_FROM` | Verified sender address | Required for email verification | Required | Public | PS-040 runtime |
| `PROOFSTUDIO_EMAIL_API_KEY` | Email provider API credential if provider uses an API key | Required for provider-backed email | Required | Secret | PS-040 runtime |
| `PROOFSTUDIO_DISPOSABLE_DOMAIN_SOURCE` | Disposable/temp email source or local list pointer | Required | Required | Public config | PS-040 runtime |
| `PROOFSTUDIO_EMAIL_DOMAIN_ALLOWLIST` | Comma-separated allowlist or config pointer | Optional | Optional | Public config unless tenant-private | PS-040 runtime |
| `PROOFSTUDIO_EMAIL_DOMAIN_BLOCKLIST` | Comma-separated blocklist or config pointer | Optional | Optional | Public config unless tenant-private | PS-040 runtime |
| `PROOFSTUDIO_AUTH_RATE_LIMIT_WINDOW_SECONDS` | Auth-sensitive rate-limit window | Required | Required | Public config | PS-040 runtime |
| `PROOFSTUDIO_AUTH_RATE_LIMIT_MAX` | Auth-sensitive max attempts per window | Required | Required | Public config | PS-040 runtime |
| `PROOFSTUDIO_SESSION_COOKIE_NAME` | Session cookie name | Required | Required | Public config | PS-040 runtime |
| `PROOFSTUDIO_SESSION_COOKIE_DOMAIN` | Cookie domain for deployment | Optional locally | Required if cross-subdomain | Public config | PS-040 runtime |
| `PROOFSTUDIO_SESSION_COOKIE_SECURE` | Require secure cookies | Optional locally | Required true | Public config | PS-040 runtime |
| `PROOFSTUDIO_CORS_ORIGINS` | Explicit allowed origins | Required if non-local | Required | Public config | Existing/PS-040 runtime |

Example placeholders for later env templates must be obvious placeholders such
as `CHANGE_ME_AUTH_SECRET`, `https://example.localhost`,
`your-google-client-id`, and `replace-with-email-provider-key`. Do not commit
live credentials. Do not use fake values that resemble real credentials.

## 8. Logical Schema Contract

PS-040A adds no migration files and no SQL. The later implementation must
define durable schema entities for:

| Entity | Required purpose |
| --- | --- |
| `user` | Stable user identity, primary email, username if enabled, activation/verification state, created/updated timestamps |
| `account` | Linked OAuth/provider accounts and provider subject identifiers |
| `session` | Server-owned session state, expiry, revocation metadata, user agent/IP hash if approved |
| `verification_token` | Email verification and password/account verification tokens with expiry and one-time use state |
| `role` / `membership` | RBAC assignments, account/team membership, role scope, activation state |
| `auth_audit_event` | Audit-safe records for signup, login, logout, verification, failed attempt, role changes, account changes |
| `email_domain_policy_entry` | Allow/block/disposable-domain policy rows or synchronized source entries |
| `rate_limit_counter` or provider-owned store | Auth-sensitive rate-limit accounting without leaking secrets or raw sensitive payloads |

SQL, Drizzle schema files, and migrations belong to a later implementation
slice. If Better Auth supplies required tables, the implementation must map
that provider schema to this logical contract and document any differences.

## 9. Routes And API Contract

Future routes/actions to define before implementation:

| Route/action | Purpose | Notes |
| --- | --- | --- |
| `/login` | Login screen/action boundary | No UI in PS-040A |
| `/signup` | Signup screen/action boundary | Must enforce email checks before activation |
| `/verify` | Email verification flow | One-time token or provider-equivalent |
| `/account` | Account/profile read/update surface | Server-validated |
| `/logout` or logout action | Session revocation | Server-owned |
| OAuth callback route(s) | Google/Apple/GitHub callback handling | Server boundary only |
| Session readback route | Return current authenticated account/session | Must avoid overexposing provider data |
| Account audit/admin-safe route if needed | Audit-safe event readback | RBAC gated |

These routes are contract targets only. PS-040A implements none of them.

## 10. Trust Boundaries

Auth proves account/session identity only. It does not prove the truth of a
campaign, artifact, prompt, model output, provider result, review decision, or
business outcome.

Required negative boundaries:

- Auth does not prove semantic truth.
- Auth does not prove legal authenticity.
- Auth does not prove human authorship.
- Auth does not prove C2PA authenticity.
- Auth does not prove Object Lock or tamper-proof storage.
- Auth does not prove browser-side B2 byte verification.
- ProofStudio must not claim enterprise security from PS-040.
- ProofStudio must not claim production compliance from PS-040.

PS-040 may establish account identity and authorization for product workflows.
It must not weaken the PS-037 disclosure/trust-boundary layer.

## 11. Out Of Scope

Out of scope for PS-040A and for the first PS-040 auth/account implementation
unless explicitly approved:

- PS-041 dashboard
- deployment/domain hardening
- final submission pack
- provider media generation
- B2/archive changes
- evidence mutation
- production compliance claims
- public deployment verification
- C2PA implementation
- Object Lock implementation
- browser-side B2 byte verification

## 12. Later Implementation Acceptance Gates

Before any PS-040 runtime auth implementation can be accepted, the later slice
must satisfy:

- env example updated with placeholder-safe values only
- schema/migrations added
- auth smoke passes
- OAuth config remains placeholder-safe in repo
- email verification smoke passes
- disposable email block smoke passes
- rate-limit smoke passes
- RBAC smoke passes
- audit hook smoke passes
- frontend typecheck/build passes if frontend code changes
- backend smoke passes if backend code changes
- secret scan passes
- forbidden claim scan passes
- hidden Git flag check passes by reading `git ls-files -v` and failing on
  leading `h` or `S`
- `git diff --check` passes
- no live credentials committed

PS-040 runtime implementation must also report whether it touched FastAPI,
web/app server code, env templates, schema/migrations, frontend UI, and smoke
scripts.
