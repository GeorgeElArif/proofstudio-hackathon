# ProofStudio — CORS and Security

## PS-042B1 same-origin authentication boundary

Production browser authentication is first-party: the browser calls the
public web origin and Render rewrites the six auth-facing route families to
`proofstudio-auth` without changing the visible URL. The SPA fallback is last.
Both the static gateway and auth runtime emit `Cache-Control: no-store` for
those routes; the runtime also emits `Pragma: no-cache`.

Request method, URL query, cookie/header values, and body bytes are forwarded
into the Better Auth `Request`. Response status, bytes, ordinary headers, and
multiple `Set-Cookie` values are copied back. The slice-local auth smoke proves
these mechanics with synthetic byte buffers and makes no external request.

The session posture is Secure, HTTP-only, same-origin and no explicit cookie
domain. Browser auth calls use `credentials: "include"`. Browser source neither
reads localStorage/sessionStorage for authentication nor constructs the shared
internal service token. Private account reads travel browser -> same-origin
auth gateway -> auth-server -> FastAPI; only auth-server adds
`X-ProofStudio-Internal-Token`.

Better Auth retains an exact trusted-origin list based on the public web URL;
wildcard trusted origins and disabled CSRF/origin checks are forbidden. Auth
CORS never reflects `*`. Localhost origins are accepted only for local-shaped
auth configuration. When the configured public web URL is non-local, auth CORS
accepts only the exact public web URL and exact configured non-wildcard
origins. FastAPI keeps its existing non-credentialed public-read CORS boundary;
private cookie-backed reads do not go directly from the browser to FastAPI.

The Blueprint contains generated/reference metadata only. Provider and B2
secrets are absent, `VITE_*` remains public-only, and the production execution
flags remain default-off. The classified scan treats the three
`accessToken`/`refreshToken`/`idToken` snake-case mappings in the Better Auth
schema as schema/redaction-shaped runtime literals, not credentials; actual
credential-shaped material fails the smoke.

CORS and secret-handling strategy for the historical public demo and the
PS-042B1 release plan. PS-042B1 does not claim a new deployment.

## Current local CORS behavior

The FastAPI backend (`src/proofstudio/api/app.py`) defines an explicit local
allow-list:

| Origin | Purpose |
| --- | --- |
| `http://127.0.0.1:5173` | Vite dev server (Review Room) |
| `http://localhost:5173` | Vite dev server (alt host) |
| `http://127.0.0.1:4173` | Vite preview server |
| `http://localhost:4173` | Vite preview server (alt host) |

This is what lets the browser at `http://127.0.0.1:5173` fetch
`http://127.0.0.1:8000` without a CORS block during the local two-terminal
demo. The middleware uses `allow_methods=["*"]`, `allow_headers=["*"]`, and
`allow_credentials=False`.

## Production CORS strategy

Production CORS must be **explicit**. The deployed Review Room origin
(`https://replace-with-web-host` in the template) must be added to the backend's
allow-list via the `PROOFSTUDIO_CORS_ORIGINS` environment variable.

- The backend reader (`src/proofstudio/api/app.py`) reads
  `PROOFSTUDIO_CORS_ORIGINS`, splits on commas, trims whitespace, and merges
  those origins with the local defaults (deduped).
- If the variable is unset, behavior is identical to the local demo
  (local origins only) — backward compatible.
- If the variable contains `*` (a wildcard), the reader **refuses** to widen
  CORS and falls back to the local allow-list, with a clear log line. Wildcard
  production CORS is never silently enabled.
- `allow_credentials` remains `false`. The Review Room does not use cookies or
  HTTP auth today; there is nothing to credential.

## Why wildcard production CORS is unsafe

A wildcard `Access-Control-Allow-Origin` combined with a permissive API lets
any website on the internet drive your backend (and any billable
provider/B2 call behind it) from a visitor's browser. Even without credentials,
wildcard CORS in front of a backend that can issue live proof runs is an
abuse/spend vector. ProofStudio therefore requires an explicit origin allow-list
in production.

## How to set production CORS origins

Set `PROOFSTUDIO_CORS_ORIGINS` to a comma-separated list of the exact frontend
origins that should be allowed. Example (placeholder hosts):

```
PROOFSTUDIO_CORS_ORIGINS=https://replace-with-web-host
```

For multiple frontends (e.g. a preview + a primary):

```
PROOFSTUDIO_CORS_ORIGINS=https://replace-with-web-host,https://replace-with-preview-host
```

Rules:

- Origins must include the scheme (`https://`) and the exact host:port.
- No trailing slash.
- The value `*` is rejected by the backend reader.
- Mirror the value you set for `PROOFSTUDIO_PUBLIC_WEB_URL`.

## Historical public FastAPI credentials posture

`allow_credentials` stays **false** for direct public FastAPI reads. PS-042B1
introduces cookie authentication only on the separate same-origin auth gateway;
it does not widen FastAPI CORS to credentialed browser requests.

## Frontend API base URL strategy

The deployed frontend must point at the deployed API host. The frontend reads
the API base URL in this order (`apps/web/src/api.ts`):

1. `VITE_PROOFSTUDIO_API_BASE_URL` (build-time Vite env var).
2. Fallback: `http://127.0.0.1:8000` (local dev only).

For a production build, set `VITE_PROOFSTUDIO_API_BASE_URL` to the public API
URL when running `npm run build`. A production bundle should not silently fall
back to localhost; the build pipeline must provide the real value. The value
must match the host that the backend sees in its CORS allow-list.

## Secret handling rules

- Real secrets (B2 keys, Cloudflare token, Gemini key, ElevenLabs key) live only
  in the platform secret manager or a git-ignored `.env.production` on the host.
- The repo only ever contains `.env.production.example` with placeholder values
  such as `replace-me` and `https://replace-with-api-host`.
- Never prefix a secret with `VITE_` — Vite inlines those into the browser
  bundle. Only public values (like the API base URL) should use `VITE_`.
- Never log secrets, never put them in smoke transcripts, never paste them into
  docs, screenshots, or recordings.

## What NOT to commit

- `.env`, `.env.local`, `.env.production` (real values).
- Any file containing a real API key, token, or password.
- Real presigned B2 URLs.
- Provider dashboards / billing consoles.
- Any screenshot or recording that shows secret material.

The PS-017 smoke scans `.env.production.example` and these docs for real
secret-like patterns and fails if any are found.

## Truth boundary

This document defines the CORS and secret-handling strategy for a future
deployment. It does **not** prove a deployment exists, a public URL works,
authentication, production persistence, or any provider/B2 behavior beyond what
earlier proof slices already established.
