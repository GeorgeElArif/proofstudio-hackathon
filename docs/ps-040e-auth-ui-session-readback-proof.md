# PS-040E Auth UI + Session Readback Proof

Date: 2026-07-09
Branch: `ps-040/auth-account-system-v1`
Base/HEAD: `8c5fc8620e4ba29b3237bcc060dd56644cb53a2b`

## What Changed

- Added safe auth-server session readback at `GET /session` and `GET /auth/session`.
- Added a safe auth-server logout wrapper at `POST /logout`.
- Added a typed web auth client boundary for readiness, session readback, email login/signup submit requests, and logout.
- Added `/login`, `/signup`, `/account`, and `/account/session` client routes.
- Added a minimal account/session surface showing readiness, provider configuration status, and current sanitized session state.
- Verified auth-server POST body forwarding from Node `IncomingMessage` into Web `Request` objects for Better Auth email routes.
- Added deterministic PS-040E auth-server and web client smokes.

## Auth Server Session Readback Behavior

`/session` and `/auth/session` are safe wrappers around the Better Auth session readback path. When required env is missing or placeholder-safe, the routes return `503` with `state: "unavailable"`, `authenticated: false`, and provider/readiness categories only.

When the runtime is configured, the route asks Better Auth for the current session and returns one of:

- `authenticated`: sanitized session and user fields only.
- `unauthenticated`: no server-owned session is present.
- `unavailable`: the runtime/database could not safely serve readback.

The readback does not return cookies, provider tokens, secrets, private keys, or raw database connection data.

## Logout Behavior

`POST /logout` fails closed when required env is missing or placeholder-safe. When runtime config is present, it first performs session readback. If no active session exists, it returns `401` with `logout: "not_performed"` and does not report success. If a session exists, it delegates sign-out to Better Auth and returns the resulting sanitized state.

## Web Auth Client Boundary

`apps/web/src/authClient.ts` centralizes:

- auth server base URL from `VITE_PROOFSTUDIO_AUTH_BASE_URL`, defaulting to local auth-server loopback.
- readiness checks against `/readyz`.
- sanitized session readback against `/session`.
- email login/signup submit requests against Better Auth email routes.
- logout requests against `/logout`.

All browser calls use `credentials: "include"` for server-owned cookie handling. The client does not store auth in `localStorage` or `sessionStorage`, does not create client-only sessions, and does not force authenticated success.

## Auth Server POST Body Forwarding

The auth server preserves method and headers when converting Node `IncomingMessage` requests into Web `Request` objects. `GET` and `HEAD` requests omit a body. Non-`GET`/`HEAD` requests forward the request stream with Node-compatible `duplex: "half"` handling.

This protects Better Auth email endpoints used by the web client:

- `/auth/sign-in/email`
- `/auth/sign-up/email`

Login/signup JSON submit bodies are server-forwarded to Better Auth only after the runtime passes the env/database gate. Missing or placeholder env still fails closed before auth success can be reported. Request body values, passwords, tokens, secrets, and raw emails are not logged by the request bridge.

## Login UI Behavior

`/login` shows the auth runtime boundary, readiness summary, provider status, and email/password form. The form is disabled while the runtime is not ready. If a submit request is accepted by the auth server, the UI still relies on session readback for actual session state and does not fake successful login.

## Signup UI Behavior

`/signup` shows the same readiness and provider boundary with name/email/password inputs. The form is disabled while the runtime is not ready. Signup submission remains server-owned; email verification and session readback are not simulated by the client.

## Account/Session UI Behavior

`/account` and `/account/session` show the current auth server readiness, safe provider configuration categories, and sanitized session state. The page shows no user when the server returns unavailable, unauthenticated, or network failure. Logout is only rendered when readback reports an authenticated session.

No dashboard, campaign list, proof room access control, admin UI, fake user, seed account, or PS-041 surface was added.

## Missing-Env Behavior

With no real auth env configured:

- `/healthz` remains process-live.
- `/readyz` reports not ready.
- `/session` and `/auth/session` return unavailable and unauthenticated without user/session payloads.
- `/logout` returns unavailable and unauthenticated without reporting logout success.
- Login/signup forms show honest unavailable/not-ready behavior.
- Account/session shows no fake user.

## Screenshots Captured

Captured into the review pack:

- `screenshots/01-desktop-login.png`
- `screenshots/02-desktop-signup.png`
- `screenshots/03-desktop-account-session.png`
- `screenshots/04-mobile-login.png`
- `screenshots/05-mobile-signup.png`
- `screenshots/06-mobile-account-session.png`

## Validation Results

Repo-level:

- `git diff --check`: PASS.
- `git ls-files -v | rg '^[hS]' || true`: PASS, no hidden Git flag matches.

Auth server:

- `npm ci --ignore-scripts`: PASS.
- `npm run typecheck`: PASS.
- `npm run build`: PASS.
- `npm run test:policy`: PASS.
- `npm run smoke:readiness`: PASS.
- `npm run smoke:auth-behavior`: PASS.
- `npm run smoke:body-forwarding`: PASS.
- `npm run smoke:missing-env`: PASS after approved local loopback retry.
- `npm run smoke:session-readback`: PASS after approved local loopback retry.
- `npm run drizzle:check`: PASS.
- `npm install --package-lock-only --ignore-scripts --dry-run`: PASS.
- `npm audit --omit=dev`: PASS after approved registry network retry; found 0 vulnerabilities.

Web:

- `npm ci --ignore-scripts`: PASS.
- `npm run typecheck`: PASS.
- `npm run build`: PASS with the existing Vite large chunk warning.
- `npm run smoke:auth-client`: PASS.
- `npm audit --omit=dev`: PASS after approved registry network retry; found 0 vulnerabilities.

DB smoke NOT RUN — no safe local/test DATABASE_URL provided.

## What Is Live Now

- Safe auth readiness display.
- Safe session readback wrappers.
- Safe logout wrapper.
- Login/signup/account UI routes.
- Browser auth client boundary using server-owned credentials mode.
- Provider readiness summary with disabled OAuth buttons unless configured.

## What Remains Deliberately Not Live

- Dashboard UI.
- PS-041.
- Campaign list behind auth.
- Proof room access control.
- Admin UI.
- Seed users.
- Fake users or fake sessions.
- Client-only auth state.
- Live email/OAuth provider verification without approved runtime config.
- FastAPI proof API changes.
- Production deployment verification.

## Trust Boundaries

Auth proves account/session identity only.
ProofStudio proves what the pipeline recorded. Proof does not equal truth.

Auth does not prove semantic truth.
Auth does not prove legal authenticity.
Auth does not prove human authorship.
Auth does not prove C2PA authenticity.

## Known Limitations

- The runtime was validated in missing-env/not-ready mode only; no DB-backed auth smoke was run.
- OAuth buttons are readiness-aware but no live OAuth provider flow was exercised.
- Email verification remains server-owned and was not exercised with live provider credentials.
- The account surface is intentionally limited to session readback and readiness, not profile management.

## Next Slice Recommendation

PS-040F should continue with an approved safe local/test database and provider-specific test credentials, then exercise real Better Auth session creation, email verification behavior, OAuth callback behavior, and logout against a real test runtime. It should keep dashboard and PS-041 work separate.
