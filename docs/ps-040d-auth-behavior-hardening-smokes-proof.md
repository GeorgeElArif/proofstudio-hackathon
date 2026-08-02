# PS-040D Auth Behavior Hardening + Smokes Proof

Date: 2026-07-07
Branch: `ps-040/auth-account-system-v1`
Base: `origin/accepted/proofstudio @ 81fdeba8a07f039c01185997e08631b71d75eecc`

## What Changed

- Added safe provider/env readiness classifications for auth base config,
  database, email, Google OAuth, GitHub OAuth, and Apple OAuth.
- Added a server-side email verification delivery foundation that reports
  unavailable/deferred and does not fake delivery.
- Added server-side email domain policy checks for syntax, normalization,
  allowlist, blocklist, and local disposable-domain blocking.
- Added a local-only in-memory auth rate-limit foundation with deterministic
  window reset behavior.
- Added a minimal auth/account RBAC policy for owner, reviewer, and viewer.
- Added an audit writer foundation that persists to `auth_audit_event` only
  when a DB handle is available.
- Added deterministic no-secret smokes and a guarded DB-backed smoke path.

## Provider And Env Checks

`/readyz` now includes safe provider readiness categories only. It exposes
provider names, status, required flag, and issue names. It does not expose env
values, credentials, tokens, secrets, database URLs, or private keys.

Statuses are:

- `configured`
- `missing`
- `placeholder`
- `invalid_shape`

Required runtime categories are auth base config, database, and email. OAuth
providers remain optional unless their credential pairs are present.

## Email Verification Foundation

Better Auth remains configured to require email verification and not auto sign
in after verification. The PS-040D email abstraction reports:

- `unavailable` when provider/sender/credential env is absent
- `deferred` when provider-shaped config exists, because live delivery is not
  enabled by this slice

Missing email config fails closed. The implementation does not send live email
unless a later provider-owned slice explicitly enables delivery.

## Disposable-Domain Behavior

The domain policy module validates email syntax, extracts normalized domains,
honors allowlist entries first, blocks explicit blocklist entries, and blocks a
small local disposable list for deterministic smokes. It does not fetch remote
disposable-domain lists during build, test, or smoke.

## Rate Limiting Behavior

The PS-040D rate limiter is a local-only in-memory foundation for deterministic
smokes. It proves repeated attempts within a configured window eventually block
and that attempts after the window reset are allowed. It is not a distributed
rate-limit claim.

Better Auth database rate-limit config from PS-040C remains behind the live
runtime/database gate.

## RBAC Behavior

Roles:

- `owner`
- `reviewer`
- `viewer`

Permissions:

- `account.read`
- `account.update`
- `audit.read`
- `auth.manage`

Policy tests use static role fixtures only. No runtime fake users or fake
sessions were added.

## Audit Hook Foundation

The audit writer accepts auth event type, nullable actor/user ids, request id,
IP/user-agent hash inputs, outcome, reason, and redacted metadata. Email
metadata is reduced to domain when persisted. Secret-like metadata keys are
redacted.

Without DB configured, the writer returns `unavailable` and does not fake
persistence. With DB configured, the writer inserts into `auth_audit_event`.

## DB-Backed Smoke Path

`npm run smoke:auth-db` refuses to run unless `DATABASE_URL` or
`PROOFSTUDIO_DATABASE_URL` is set. It also refuses URLs that do not look
local/test unless `PROOFSTUDIO_AUTH_DB_SMOKE_ALLOW_NONLOCAL=true` is set for an
approved test database.

The smoke checks connection readiness, verifies the expected auth tables exist,
and performs rollback-only writes to `auth_audit_event` and `auth_rate_limit`.
It does not apply migrations and must not be pointed at a production-looking
database.

## Smoke And Test Results

Validation results are recorded in the PS-040D review pack after execution.
The DB-backed smoke was not run by default because no safe local/test
`DATABASE_URL` was provided.

## What Is Live Now

- Safe readiness status classification.
- Fail-closed auth runtime gate for missing, placeholder, or invalid required
  runtime config.
- Email verification requirement and delivery foundation.
- Server-side domain policy foundation.
- Local-only rate-limit behavior foundation.
- Deterministic RBAC policy module.
- Audit writer foundation.
- Guarded DB smoke path.

## Deliberately Not Live

- Login UI.
- Signup UI.
- Dashboard UI.
- OAuth buttons.
- Live email delivery.
- Live OAuth provider calls.
- Fake users.
- Fake sessions.
- Seed users.
- PS-041 dashboard work.

## Trust Boundaries

Auth proves account/session identity only.
Auth does not prove semantic truth.
Auth does not prove legal authenticity.
Auth does not prove human authorship.
Auth does not prove C2PA authenticity.
ProofStudio proves what the pipeline recorded. Proof does not equal truth.

## Known Limitations

- The local disposable-domain list is intentionally small and deterministic.
- The in-memory rate limiter is suitable for no-env/local smokes only.
- Live provider delivery and OAuth provider validation remain deferred.
- Domain MX/deliverability checks remain deferred.
- The DB smoke requires an operator-provided approved local/test database.

## PS-040E Continuation

PS-040E should continue by enabling an approved live email provider integration,
expanding domain validation only with conservative controls, exercising
provider-specific OAuth behavior with approved test credentials, and deciding
whether the rate-limit/audit paths need a production-owned distributed store.
It should continue to avoid login/signup UI and dashboard work unless that
scope is explicitly approved.
