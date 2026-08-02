# PS-042A — Production Topology and Judge Access Contract v1

Status: specification only. This document is the authoritative production contract for PS-042B through PS-042D. It does not deploy, provision, migrate, authorize, or access any production resource.

## 1. Accepted source state and evidence boundary

- Accepted commit: `977323571ced7cee538839a959081a2cd2361dc1`.
- Latest accepted slice: PS-041E2-B.
- PS-041E2 decision: readiness-only; no live PS-041E2 B2 operation is claimed.

The historical public deployment remains reachable at:

- public web: `https://proofstudio-web.onrender.com`;
- public proof API: `https://proofstudio.onrender.com`.

The current read-only observations were `GET /health` = 200 with a first-request duration of approximately 53.7 seconds, `GET /version` = 200 with a warm duration of approximately 0.32 seconds, and `GET` of the web root = 200 in approximately 0.36 seconds. These URLs and observations prove only that the historical static web and FastAPI deployment remain reachable. They do not prove that the accepted authentication, database, private dashboard, ownership, or private-lineage surfaces are deployed.

The accepted `render.yaml` currently defines only `proofstudio-api` and `proofstudio-web`. It does not define `proofstudio-auth`, `proofstudio-db`, auth database migrations, judge-account provisioning, or a same-origin auth gateway. The static service also contains duplicate `routes:` mappings. Under normal YAML parsing the later mapping supersedes the earlier one. PS-042B must consolidate every rewrite into exactly one ordered `routes:` list.

The classified source scan found 23 test-or-smoke findings and 3 runtime-source findings. The runtime-source findings are redaction-shaped literals assigned to `accessToken`, `refreshToken`, and `idToken`; they are not classified or claimed as production credentials. PS-042B must retain an explicit classified secret scan that distinguishes synthetic/redaction fixtures from real credential material.

### 1.1 PS-042 release lifecycle and authorization gates

PS-042A — Production Topology and Judge Access Contract
Defines the production architecture, security boundaries, judge-access
strategy, migration law, rollback law and acceptance criteria.

PS-042B — Render/Auth/Database Deployment Hardening
Implements the accepted blueprint, same-origin auth gateway, production
environment contract, migrations, health/readiness controls and deployment
smokes. It does not create the final production release unless separately
authorized.

PS-042C — Public Release Candidate Deployment
Deploys the exact committed PS-042B release candidate to the approved Render
resources after explicit human authorization for any paid resources,
production migration and judge-account provisioning.

PS-042D — Independent Judge-Journey Acceptance
Validates the committed and deployed release candidate through the public
credential-free journey, authenticated judge journey, access-denial matrix,
browser matrix, cold-start reliability, rollback rehearsal and claim-to-
evidence review.

Completion of PS-042A does not authorize PS-042B implementation.
Completion of PS-042B does not authorize PS-042C deployment.
PS-042C requires explicit human authorization.
PS-042D acceptance is independent from the implementation and deployment agent.

## 2. Authoritative production topology

| Component | Render resource | Purpose |
| --- | --- | --- |
| `proofstudio-web` | Static site | Judge-facing React/Vite application and same-origin request gateway |
| `proofstudio-auth` | Node web service | Better Auth, sessions, account campaign access, private proof gateway |
| `proofstudio-api` | Python web service | FastAPI proof records, passports, lineage, manifests and evidence APIs |
| `proofstudio-db` | Render PostgreSQL | Better Auth, sessions, memberships, audit events and campaign access |

All dynamic services and the database must use the same Render region. The static web service may remain free. The final judge-ready release must use always-on instances for `proofstudio-auth` and `proofstudio-api`. Free or sleeping dynamic services are unacceptable for the final release candidate because the judge's first request must not incur a one-minute wake-up.

The database decision must be recorded as one of these options:

1. Paid managed PostgreSQL for the final judging period — preferred.
2. An explicitly accepted temporary hackathon database with documented expiry, backup, and restoration limitations — fallback only.

No paid resource may be created without explicit human approval.

## 3. Judge-access model

### 3.1 Primary path — public, deterministic, credential-free

A judge must be able to evaluate ProofStudio without logging in:

```text
/
→ Judge Cockpit
→ fixed golden campaign
→ generation attempts and fallback
→ Genblaze lineage
→ B2 evidence and manifest verification
→ provider-free reconstruction
→ provenance passport
→ truth boundary
```

This path has no arbitrary private campaign lookup, browser-held service token, operator token, B2 credential, provider credential, or live-generation requirement. It exposes only explicitly curated public golden evidence. Fixture/demo evidence is visibly source-labelled. A fallback never masquerades as a live provider, live B2 read, or production database result. The public journey remains usable when authentication is temporarily unavailable.

### 3.2 Secondary path — authenticated production proof

The release provides one dedicated, low-privilege judge account using email/password login, with no OAuth dependency and no judge self-signup requirement. No password or password hash enters Git, and no credentials appear in screenshots, recordings, logs, evidence packs, or fixtures. Credentials are supplied only through the hackathon's judge-testing instructions.

The account is linked only to curated golden campaign records and receives the minimum sufficient role. Cross-account and unlinked-campaign reads remain denied. It can be disabled or rotated after judging. Provisioning is a separate, explicit production operation after PS-042B acceptance; it must be idempotent and auditable and must never run automatically on every application startup.

The public journey is the judging safety path. The authenticated journey proves production readiness and access control.

## 4. Same-origin authentication gateway

The browser treats authentication requests as first-party requests through the public web origin. The production web origin is the browser-facing auth base. The future static-site route list is ordered as follows:

```text
1. /auth/*   → proofstudio-auth
2. /session  → proofstudio-auth
3. /logout   → proofstudio-auth
4. /account/* → proofstudio-auth
5. /healthz  → proofstudio-auth
6. /readyz   → proofstudio-auth
7. /*        → /index.html
```

The catch-all SPA rewrite is last. No auth, account, health or readiness route
may appear after it. The Render static service contains exactly one routes
mapping.

The auth, session, logout, account, health, and readiness route families rewrite to the public `proofstudio-auth` service while preserving the original browser-visible web origin. This ordered list is a PS-042B requirement; it does not claim that Render routing has already been changed. Production browser clients must not call the auth service through a different site.

Required cookie posture is `secure=true`, an HTTP-only session cookie, no browser-readable session secret, no localStorage authentication token, no cross-subdomain cookie requirement, and no wildcard trusted origin. The auth server treats the public web origin as its configured base URL and trusted origin. Local development may continue to use an explicit localhost auth base.

## 5. FastAPI boundary

The public browser may continue to read non-cookie FastAPI public surfaces through its configured public API URL. Production FastAPI CORS allows only the exact public web origin, rejects wildcard production CORS, keeps credentialed CORS disabled, and exposes no service or operator credential to the browser.

Private account proof reads follow:

```text
browser
→ same-origin auth gateway
→ proofstudio-auth
→ proofstudio-api internal route
```

The auth server sends `X-ProofStudio-Internal-Token`. The browser never receives or constructs that token. The production `PROOFSTUDIO_PROOF_API_BASE_URL` value is server-only.

## 6. Environment and secret contract

`VITE_*` values are public build-time values and must never contain secrets.

### Static web: public values only

```text
VITE_PROOFSTUDIO_API_BASE_URL
VITE_PROOFSTUDIO_AUTH_BASE_URL
```

The production auth value resolves to the public web origin or a relative same-origin base.

### Authentication service: server-only values

```text
PROOFSTUDIO_ENV
PROOFSTUDIO_APP_BASE_URL
PROOFSTUDIO_PUBLIC_WEB_URL
PROOFSTUDIO_AUTH_SECRET
PROOFSTUDIO_DATABASE_URL
PROOFSTUDIO_CORS_ORIGINS
PROOFSTUDIO_PROOF_API_BASE_URL
PROOFSTUDIO_INTERNAL_SERVICE_TOKEN
PROOFSTUDIO_SESSION_COOKIE_NAME
PROOFSTUDIO_SESSION_COOKIE_SECURE
```

OAuth and live email delivery remain optional for the judge release.

### FastAPI service: server values

```text
PROOFSTUDIO_ENV
PROOFSTUDIO_PUBLIC_API_BASE_URL
PROOFSTUDIO_PUBLIC_WEB_URL
PROOFSTUDIO_CORS_ORIGINS
PROOFSTUDIO_INTERNAL_SERVICE_TOKEN
PROOFSTUDIO_IMPORT_OPERATOR_TOKEN
PROOFSTUDIO_RUN_LIVE_DEFAULT
PROOFSTUDIO_LIVE_RUNS_ENABLED
PROOFSTUDIO_B2_WRITES_ENABLED
PROOFSTUDIO_PAID_RUN_APPROVED
```

Final safe defaults are:

```text
PROOFSTUDIO_RUN_LIVE_DEFAULT=false
PROOFSTUDIO_LIVE_RUNS_ENABLED=false
PROOFSTUDIO_B2_WRITES_ENABLED=false
PROOFSTUDIO_PAID_RUN_APPROVED=false
```

Provider and B2 secrets remain unset unless a later, separately authorized operation requires them. Secret values use the Render secret manager, generated values, a protected environment group, or a database reference; they are never committed. The shared internal service token is generated once and injected consistently into both server services.

## 7. Build, startup, and migration contract

FastAPI:

```text
build: pip install -r apps/api/requirements.txt
start: PYTHONPATH=src uvicorn proofstudio.api.app:app --host 0.0.0.0 --port $PORT
```

Auth server:

```text
root: apps/auth-server
build: npm ci
       npm run build
start: npm run start
bind: host=0.0.0.0, port=$PORT
```

PS-042B must adapt the existing host/port environment contract safely without breaking local defaults.

All three accepted Drizzle migrations apply cleanly to a fresh PostgreSQL database. Migrations run before the new auth release receives judge traffic; failure fails deployment and is never silently skipped. Application startup does not repeatedly mutate schema, no destructive down-migration is automated, PS-042 changes remain backward-compatible with the previously deployed application revision, and code rollback requires no database rollback. Migration transcripts redact the connection string and acceptance evidence contains no production row content.

A paid Render service may use `preDeployCommand`. A profile that cannot use a pre-deploy command must provide a separate explicit migration gate before service activation. Migration execution must not be hidden in an unreviewed startup chain.

## 8. Health, readiness, release, and degraded-mode semantics

FastAPI `GET /health` is the Render health check. `GET /version` exposes a non-secret release identity sufficient to verify the deployed revision.

Auth `GET /healthz` is liveness. `GET /readyz` is readiness and verifies required environment configuration, authentication runtime availability, and PostgreSQL reachability. The Render auth health check uses `/readyz` for the judge release because a process without a reachable database is unusable.

Neither health endpoint exposes database URLs, secrets, tokens, credentials, provider keys, or raw exception messages containing secrets.

### 8.1 Cold-start and first-request reliability

The observed historical FastAPI first request took approximately 53.7 seconds. Final judge-facing auth and API services must be always-on. A warm-up ping is not a substitute for always-on services. The first request after at least 20 minutes of inactivity must complete without a free-instance wake-up delay. The public static shell must remain available independently.

A server outage must produce a visibly source-labelled unavailable or degraded state. A degraded fallback must not claim live provider, live B2, live Genblaze runtime or production database activity. Authorization denial must never trigger a public or fixture fallback. It must not convert a private read into a public read.

## 9. Rollback law

Rollback order is exact:

1. Freeze new deployment changes.
2. Preserve failed-release logs with secrets redacted.
3. Roll back static web only if its gateway or routing is defective.
4. Roll back auth and API to their last accepted deploys.
5. Do not automatically reverse database migrations.
6. Verify that the retained schema remains compatible with the rolled-back code.
7. Re-run `/health`, `/version`, `/healthz`, and `/readyz`.
8. Re-run the public golden journey.
9. Re-run the authenticated judge journey.
10. Record the rollback revision and outcome.

Rollback must not reset or delete production data, rotate secrets unnecessarily, invoke B2, invoke providers, or change accepted Git history.

## 10. PS-042 implementation boundaries

The anticipated PS-042B implementation allowlist may be narrowed from the following planning candidates only:

```text
render.yaml
.env.production.example
apps/auth-server/package.json
apps/auth-server/src/server.ts
apps/auth-server/src/env.ts
apps/auth-server/scripts/*
apps/web/src/authClient.ts
apps/web/scripts/*
scripts/ps042_*
docs/deployment/*
specs/72-ps-042-production-topology-judge-access-contract.md
docs/ps-042-*
```

This is not blanket authority to modify every listed path. The final PS-042B allowlist will be narrowed after implementation planning. Application visual redesign is not authorized. FastAPI proof semantics, B2 contracts, Genblaze parsing, accepted fixture contents, and authentication authorization rules are not authorized to change unless a narrowly documented production blocker proves a modification necessary.

### 10.1 Explicit prohibitions

Live provider execution and live media generation are not authorized by PS-042A.

B2 writes and a live PS-041E2 operation are not authorized by PS-042A.

Wildcard production CORS is forbidden and must never be enabled.

Authentication and session tokens must not be stored in localStorage or
sessionStorage.

No paid Render resource, production migration or judge account may be created
without explicit human authorization.

These are prohibitions, not permissions.

## 11. Required future acceptance matrix

### Repository and blueprint

- Exact accepted base verified.
- Only approved files changed; index clean before commit; no hidden Git flags.
- YAML valid, with no duplicate mapping keys.
- Exactly three services and one PostgreSQL database.
- Exactly one ordered static-site `routes:` list.
- No committed secrets; production-safe default flags remain false.
- Build commands resolve from their declared roots.

### Local build and tests

- FastAPI focused tests pass.
- Auth typecheck and production build pass.
- Web typecheck and production build pass.
- Drizzle schema check passes.
- All auth behavior smokes pass.
- Account campaign access smokes pass.
- Private proof and lineage access smokes pass.
- Central non-mutating regression gate passes.
- Historical PS-034A digest remains unchanged unless separately authorized.

### Fresh database

- An empty PostgreSQL database is created for acceptance.
- Migrations `0000`, `0001`, and `0002` apply exactly once.
- A second migration invocation is safe.
- Required tables and indexes exist.
- No production database is used for local smoke tests.

### Public topology

- Web root returns 200.
- SPA deep links `/passport/<golden-run>`, `/login`, `/dashboard`, and the fixed golden Proof Room path return the web application.
- FastAPI `/health` returns 200.
- FastAPI `/version` returns 200 and the expected release identity.
- Auth `/healthz` returns 200.
- Auth `/readyz` returns 200 only when PostgreSQL is reachable.
- Exact production CORS origin passes; an unapproved origin fails; wildcard production CORS is absent.

### Public judge journey

- Requires no credentials, starts at `/`, and reaches the fixed golden campaign without manual identifiers.
- Shows provider attempts and fallback evidence, Genblaze lineage, B2 evidence or accurately labelled recorded B2 evidence, manifest/hash verification, provider-free reconstruction, provenance passport, and the truth boundary.
- Performs no provider call and no B2 write.

### Authenticated judge journey

- Dedicated judge login succeeds; session survives navigation and refresh.
- Session cookie is Secure and HTTP-only; browser storage contains no auth token.
- Dashboard lists only linked campaigns.
- Authorized Proof Room and Passport succeed.
- Authorized lineage list, detail, and Passport succeed.
- Unlinked campaign access remains denied; a second account cannot access the judge account's campaign.
- Logout invalidates session readback.
- Chromium, Firefox, and WebKit/Safari-class behavior are tested.

### Reliability

- The first judge request after at least 20 minutes of inactivity incurs no free-service wake-up.
- Core path completes without a dependency timeout.
- Server outage produces a labelled unavailable/degraded state.
- Authorization denial never falls back.
- Rollback rehearsal succeeds and the previous successful deploy remains recoverable.

### Security and evidence

- Classified secret scan passes and runtime redaction literals are explicitly classified.
- No secret appears in build artifacts, browser JavaScript, logs, or screenshots.
- No `.env` content is read into evidence.
- No provider or B2 operation occurs.
- No production database rows are copied into the repository.
- Every final claim is bound to a command, response, screenshot, or deployment record.

## 12. Explicit non-goals

PS-042 does not include new product features, visual redesign, new media providers, live media generation, live PS-041E2 B2 execution, B2 writes, OAuth launch, production email delivery, password-reset UX, an administrator console, billing, multi-tenant organization management, a custom-domain requirement, background workers, queue infrastructure, C2PA claims, legal-authenticity claims, semantic-truth claims, or human-authorship claims.

## 13. Core truth boundary

```text
ProofStudio proves what the pipeline recorded.
Proof does not equal truth.
```

```text
A reachable historical deployment does not prove that the current accepted
product is deployed. A production claim becomes valid only after the exact
accepted release candidate passes the PS-042 public acceptance matrix.
```
