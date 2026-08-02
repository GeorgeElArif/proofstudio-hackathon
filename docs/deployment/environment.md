# ProofStudio — Environment Variables

Production environment reference for the PS-017 deployment-prep slice and the
PS-042B1 four-resource release plan. The
single checked-in template is
[`.env.production.example`](../../.env.production.example) and contains
**placeholders only**.

> Formatting note: variable names are listed in tables to avoid secret-looking
> `KEY=value` snippets in prose. Every real value lives in your platform's secret
> manager or a git-ignored `.env.production`, never in the repo.

## PS-042B1 ownership and same-origin rules

| Owner | Variables | Rule |
| --- | --- | --- |
| Static web (public build-time) | `VITE_PROOFSTUDIO_API_BASE_URL`, `VITE_PROOFSTUDIO_AUTH_BASE_URL` | Auth value is the public web origin (or omitted for the production `window.location.origin` fallback). Never contains a secret. |
| Auth server | `PROOFSTUDIO_APP_BASE_URL`, `PROOFSTUDIO_PUBLIC_WEB_URL`, `PROOFSTUDIO_AUTH_SECRET`, `PROOFSTUDIO_DATABASE_URL`, `PROOFSTUDIO_CORS_ORIGINS`, `PROOFSTUDIO_PROOF_API_BASE_URL`, `PROOFSTUDIO_INTERNAL_SERVICE_TOKEN`, cookie and email-readiness values | Server-only. App base and trusted origin are the exact public web origin. |
| FastAPI | public API/web/CORS values, internal/operator tokens and default-off governance flags | Service and operator credentials never enter browser code. |

Render injects `PORT` into auth production runtime; the server falls back to
`PROOFSTUDIO_AUTH_SERVER_PORT=8787` locally. Production host defaults to
`0.0.0.0`; local host defaults to `127.0.0.1`. The environment template lists
both local override names without changing Render's injected-port priority.

No `PROOFSTUDIO_SESSION_COOKIE_DOMAIN` is used. The production session is
Secure and HTTP-only, while the same-origin web rewrite removes any need for a
cross-subdomain cookie. No auth/session secret is browser-readable or stored in
localStorage/sessionStorage.

The Blueprint generates `PROOFSTUDIO_AUTH_SECRET` and one
`PROOFSTUDIO_INTERNAL_SERVICE_TOKEN`, references the internal token into
FastAPI, and references the database connection string from Render Postgres.
`PROOFSTUDIO_EMAIL_PROVIDER`, `PROOFSTUDIO_EMAIL_FROM`, the appropriate
provider credential, and the disposable-domain source remain dashboard-owned
server values required by the accepted readiness implementation. OAuth, live
email use by the judge, and provider/B2 credentials are not required by this
release plan.

## Required production variables

These must be set on the backend host before serving public traffic.

| Variable | Purpose | Production placeholder |
| --- | --- | --- |
| `PROOFSTUDIO_ENV` | Runtime environment marker | `production` |
| `PROOFSTUDIO_API_HOST` | uvicorn bind host | `0.0.0.0` |
| `PROOFSTUDIO_API_PORT` | uvicorn bind port | `8000` |
| `PROOFSTUDIO_PUBLIC_API_BASE_URL` | Public API base URL the browser calls | `https://replace-with-api-host` |
| `PROOFSTUDIO_PUBLIC_WEB_URL` | Public Review Room URL | `https://replace-with-web-host` |
| `PROOFSTUDIO_PROOF_API_BASE_URL` | Server-only FastAPI base URL used by the auth read gateway | `https://replace-with-private-proof-api-host` |
| `PROOFSTUDIO_INTERNAL_SERVICE_TOKEN` | Server-only shared credential for auth-server to FastAPI reads; inject through the production secret manager | `CHANGE_ME_INTERNAL_SERVICE_TOKEN` |
| `PROOFSTUDIO_IMPORT_OPERATOR_TOKEN` | Separate server/operator-only credential for the FastAPI bundle-import mutation; inject through the production secret manager and never expose to auth-server browser routes | `CHANGE_ME_IMPORT_OPERATOR_TOKEN` |
| `PROOFSTUDIO_IMPORT_BUCKET_ALIAS` | Non-secret server-authorized alias accepted in imported structured B2 references | `configured-import` |
| `PROOFSTUDIO_IMPORT_ROOT` | Allowlisted relative object-key root for imported B2 references | `import-root` |
| `PROOFSTUDIO_CORS_ORIGINS` | Explicit CORS allow-list (comma-separated) | `https://replace-with-web-host` |
| `PROOFSTUDIO_RUN_LIVE_DEFAULT` | Whether live mode is default (must stay `false`) | `false` |

`PROOFSTUDIO_RUN_LIVE_DEFAULT` must remain `false` for the hackathon deployment.
Live provider/B2 runs are explicit opt-in only (`run_live=true` on a single
request), never the default.

## PS-035b default-off governance controls

PS-035b adds real, default-off backend governance controls. These are POLICY
FLAGS, not secrets. They never use names containing `KEY`, `TOKEN`, or `SECRET`,
and they are never printed or exposed as secrets. Dry/demo runs remain available
with these defaults; only live provider execution, B2 writes, paid runs, and
fixture mutation are gated.

| Variable | Purpose | Default |
| --- | --- | --- |
| `PROOFSTUDIO_LIVE_RUNS_ENABLED` | Live provider execution blocked unless explicitly enabled | `false` |
| `PROOFSTUDIO_B2_WRITES_ENABLED` | B2 writes after a successful live run blocked unless explicitly enabled | `false` |
| `PROOFSTUDIO_COST_CAP_USD` | Local cost-cap policy gate in USD; paid execution blocked when zero | `0.00` |
| `PROOFSTUDIO_FIXTURES_FROZEN` | Golden fixtures frozen by default | `true` |
| `PROOFSTUDIO_PAID_RUN_APPROVED` | Explicit PM/human approval for any paid/live run | `false` |

Behavioral contract:

- `run_live=true` alone is **not** sufficient to execute providers. The backend
  (`src/proofstudio/api/live_bridge.py`, `src/proofstudio/api/services.py`)
  enforces a governance gate that requires `PROOFSTUDIO_LIVE_RUNS_ENABLED=true`,
  `PROOFSTUDIO_PAID_RUN_APPROVED=true`, a non-zero `PROOFSTUDIO_COST_CAP_USD`,
  and a non-`free-only` `budget_mode`.
- `PROOFSTUDIO_RUN_LIVE_DEFAULT=false` is honored truthfully: PS-035b supersedes
  it with the enforced `PROOFSTUDIO_LIVE_RUNS_ENABLED` gate, so the documented
  default is no longer a phantom-only contract.
- B2 writes after a successful live provider run require
  `PROOFSTUDIO_B2_WRITES_ENABLED=true`.
- Paid/non-free providers are blocked when `budget_mode="free-only"` or when the
  cost cap is `0.00`.
- B2 reads remain disabled by default (PS-019/PS-021/PS-025 durable passport
  contract). PS-035b adds no live B2 read path.
- The cost cap is a local policy gate, not a real billing API integration and
  not production multi-user budget accounting.

## Frontend build-time variables

Vite inlines `VITE_*` variables at build time, so these must be present in the
build environment.

| Variable | Purpose | Production placeholder |
| --- | --- | --- |
| `VITE_PROOFSTUDIO_API_BASE_URL` | Public API base URL baked into the bundle | `https://replace-with-api-host` |
| `VITE_PROOFSTUDIO_AUTH_BASE_URL` | Same-origin auth base; use the public web origin | `https://replace-with-web-host` |

Local API fallback in `apps/web/src/api.ts` is `http://127.0.0.1:8000`. Local
auth fallback is `http://127.0.0.1:8787`; in a production browser, an absent
auth build value resolves to `window.location.origin`. Production
builds must NOT silently fall back to localhost — set the env var when building.

## Backend variables

The backend reads its bind host/port and environment marker from the required
variables above. CORS origins are read from `PROOFSTUDIO_CORS_ORIGINS` (see
[`cors-and-security.md`](./cors-and-security.md) for the local defaults and the
production strategy).

## Optional provider/storage variables

Only required if you intend to allow explicit live proof runs. For a
dry-run-only deployment, leave them as placeholders.

| Variable | Purpose | Placeholder |
| --- | --- | --- |
| `B2_BUCKET` | Backblaze B2 bucket name | `replace-me` |
| `B2_REGION` | B2 region | `replace-me` |
| `B2_KEY_ID` | B2 application key id | `replace-me` |
| `B2_APP_KEY` | B2 application key (secret) | `replace-me` |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare account for Genblaze | `replace-me` |
| `CLOUDFLARE_API_TOKEN` | Cloudflare API token (secret) | `replace-me` |
| `GEMINI_API_KEY` | Google Gemini API key (secret) | `replace-me` |
| `ELEVENLABS_API_KEY` | ElevenLabs API key (secret, optional provider) | `replace-me` |

Optional providers (ElevenLabs, OpenAI, Runway, Stability Audio, NVIDIA NIM)
are documented as **not implemented** in
`docs/submission/provider-model-inventory.md`. Setting an ElevenLabs key does
not enable a provider that is not wired up.

## Local vs production values

| Concern | Local | Production |
| --- | --- | --- |
| API host:port | `http://127.0.0.1:8000` | `https://replace-with-api-host` |
| Web URL | `http://127.0.0.1:5173` | `https://replace-with-web-host` |
| CORS origins | local defaults hard-coded in `app.py` | explicit `PROOFSTUDIO_CORS_ORIGINS` |
| uvicorn bind | `127.0.0.1:8000` | `0.0.0.0:8000` (behind TLS-terminating proxy) |
| Live default | `false` (explicit opt-in) | `false` (explicit opt-in) |
| Provider/B2 keys | typically unset | real values in secret manager |
| `.env` files | git-ignored, local only | never in repo; use secret manager |

## Secret handling

- Real secret values live **only** in your deployment platform's secret manager
  or a git-ignored `.env.production` on the host.
- The repo may only ever contain `.env.production.example` with placeholder
  values such as `replace-me` and `https://replace-with-api-host`.
- The PS-017 smoke scans the env template and deployment docs for real
  secret-like patterns and fails if any are found.

## Where NOT to store secrets

- Never in `.env.production.example`.
- Never in any file under `docs/` or `specs/`.
- Never in shell history that gets committed.
- Never in frontend source (Vite inlines `VITE_*` at build time, so frontend
  vars must be public-only — never put a secret behind a `VITE_` prefix).
- Never in screenshots, recordings, or logs.
- Never in the smoke transcript JSON under `/tmp/proofstudio-ps-017/`.

## How to verify env readiness

Before deploying, run:

```bash
cd /home/proofstudio-work/proofstudio
source .venv/bin/activate
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"
python scripts/ps017_deployment_prep_smoke.py
```

The smoke verifies the template exists, contains only placeholders, includes
every required key, and contains no real secrets. It does **not** verify your
real production values — confirm those manually in the platform secret manager
before flipping traffic on.

For per-variable preflight, see [`preflight-checklist.md`](./preflight-checklist.md).
