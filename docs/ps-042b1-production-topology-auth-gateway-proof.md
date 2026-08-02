# PS-042B1 — Production Blueprint and Same-Origin Auth Gateway v1 proof

## Evidence boundary

Branch: `ps-042b1/render-blueprint-auth-gateway-v1`

Accepted base at preflight: `0a560956f2181f1c1003d95e89a784658a8b8d92`

Repair commit: `<pending: fix(deploy): align same-origin production auth boundary>`

PS-042B1 implements and locally validates a release-candidate Blueprint. It
does not synchronize Render, create any resource, run a production migration,
provision a judge, or prove a live deployment. The historical public PS-018B
URLs do not prove this four-resource topology is deployed.

## Implemented contract

- `render.yaml` defines exactly three services (`proofstudio-api`,
  `proofstudio-auth`, `proofstudio-web`) and one PostgreSQL database
  (`proofstudio-db`). Dynamic resources share `oregon`; API and auth use
  always-on `starter`; PostgreSQL uses `basic-256mb` and blocks public inbound
  database access.
- Current Render fields are used: `runtime`, `autoDeployTrigger`,
  `preDeployCommand`, `fromService`, `fromDatabase`, `runtime: static`, and a
  current flexible database plan. Automatic deployment is off.
- The static service has one ordered route mapping: six auth-facing rewrites,
  then the SPA fallback. The six auth paths have `Cache-Control: no-store`.
- The auth server honors Render `PORT`, binds `0.0.0.0` in production, retains
  `127.0.0.1:8787` local defaults, and refuses malformed/out-of-range ports.
- Node request conversion preserves method, query, request headers (including
  cookie), and raw body bytes. Response conversion preserves status, bytes,
  ordinary headers, and multiple `Set-Cookie` values. Auth-facing responses
  are non-cacheable.
- Production browser auth resolves to the configured web origin or
  `window.location.origin`; local development retains the localhost auth
  fallback. Auth requests include cookie credentials. Browser storage auth,
  browser-held service tokens, and direct private FastAPI reads are absent.
- Auth secret and internal service token are generated. The internal token is
  referenced consistently into FastAPI; the database URL is referenced from
  Render Postgres. Cross-subdomain cookie configuration is absent.
- The production environment template sets
  `PROOFSTUDIO_APP_BASE_URL=https://replace-with-web-host`, documenting the
  browser-visible same-origin gateway rather than the auth service host.
- Production-shaped auth CORS allows the exact public web URL and exact
  configured non-wildcard origins, while denying `http://localhost:5173`,
  `http://127.0.0.1:5173`, unconfigured origins, and `*`. Local-shaped auth
  configuration continues to allow both localhost spellings.
- Live provider, paid run and B2-write flags remain false. No provider/B2
  credentials are present in the Blueprint.

## Same-origin boundary repair validation

The repair is validated with these exact local commands:

```text
git diff --check
.venv/bin/python scripts/ps042b1_render_blueprint_smoke.py
cd apps/auth-server
npm run typecheck
npm run build
npm run smoke:production-topology
npm run smoke:readiness
npm run smoke:auth-behavior
npm run smoke:session-readback
npm run smoke:body-forwarding
cd /home/proofstudio-work/proofstudio
env PYTHONPATH=src .venv/bin/python -m pytest -q
.venv/bin/python scripts/proofstudio_regression_gate.py --current ps042b1 --frontend --report-out /tmp/proofstudio-ps042b1-repair-release-report.json
```

These checks are synthetic/local. They do not access Render or prove that this
topology, CORS behavior, or authentication boundary has run on Render.

Repair validation completed locally: the Blueprint smoke passed with
`credential_findings=0`; all seven required auth commands passed; the full
Python suite passed with 523 tests; and the central regression gate passed with
12 historical contracts, no historical contract failures,
`non_mutating_gate: true`, and `ps034a_report_digest_unchanged: true`. The
central frontend run used the already-installed Node 24 runtime first on
`PATH`, preserving the previously documented workaround for the host Node 18
esbuild truncation defect. The non-live counters below remain unchanged.

## Slice-local and regression evidence

The following local, non-live checks are the completion gate:

```text
node web package-script assertion
python3 scripts/ps042b1_render_blueprint_smoke.py
auth typecheck + production build + drizzle schema check
auth production-topology and accepted behavior/access smokes
web typecheck + production build + accepted client/access/lineage smokes
focused FastAPI pytest suite
central regression gate, current ps042b1, frontend once, report only under /tmp
classified secret scan
PS-034A canonical report SHA-256 before/after comparison
scope, hidden-index-flag, lockfile and diff checks
```

The Blueprint smoke uses the Python standard library only, rejects duplicate
YAML mapping keys, validates the exact route/header/resource ordering, checks
the corrected web script registration and prints non-live counters. Feature
smokes are non-recursive and do not write historical evidence.

Completed local results:

- web package-script assertion, lockfile guard, `git diff --check`, and the
  standard-library Blueprint smoke passed;
- auth typecheck, build, Drizzle schema check, production-topology smoke, and
  accepted environment/readiness/behavior/session/body/email/configured-auth/
  database/account/private-proof/imported-lineage smokes passed;
- a freshly recreated local PostgreSQL test database applied migrations
  `0000`, `0001`, and `0002` on the first invocation; the second invocation
  applied no files and retained all nine required tables; the disposable
  container and volume were removed after validation;
- web typecheck and production build passed under the already-installed Linux
  Node 24 runtime; auth-client, configured-auth-client, dashboard contract/UI,
  account-campaign, private-proof, lineage source-contract, and PS-042B1
  production-auth-gateway smokes passed;
- 62 focused FastAPI/import/runtime-guard tests passed (32 + 30);
- the central gate passed with `--current ps042b1 --frontend --report-out
  /tmp/proofstudio-ps042b1-release-report.json`, verified 12 historical
  contracts, ran the frontend once, remained non-mutating, and reported
  `ps034a_report_digest_unchanged: true`;
- canonical PS-034A report SHA-256 before validation was
  `56e795b008b1e5c4d268b9938f09be0cb6309f40f7839c7cec470aadeab657c5`.

The host default Node 18 runtime truncated Vite's esbuild source-map response
at 524,159 bytes and lacks `import.meta.dirname`; the exact build and affected
historical smoke passed when run with the already-installed Linux Node 24
runtime first on `PATH`. No dependency or lockfile changed. The optional
browser-driven lineage runtime smoke reported that Playwright Node/Python was
not installed and made no assertions; browser-matrix acceptance remains a
PS-042D concern. No result here is a deployment or acceptance claim.

## Classified secret scan

The known runtime-source findings are the three Better Auth schema mappings
named `accessToken`, `refreshToken`, and `idToken`, whose values are snake-case
database field names. They are classified as schema/redaction-shaped literals,
not production credentials. Synthetic smoke cookies/hosts are test-only.
Generated secret declarations and secret-manager references contain no values.
Any actual private-key block, AWS-style access key, or provider-token shape is
an unclassified failure.

## Non-live counters

```text
external_http_calls=0
render_calls=0
deployments=0
provider_calls=0
b2_calls=0
b2_writes=0
production_database_calls=0
production_migrations=0
judge_accounts_provisioned=0
paid_resources_created=0
```

## Truth boundary

ProofStudio proves what the pipeline recorded. Proof does not equal truth.
This slice proves local configuration and code contracts only; it does not
prove production availability, live authentication, live PostgreSQL data,
cold-start behavior, rollback rehearsal, browser-matrix behavior, or judge
acceptance.
