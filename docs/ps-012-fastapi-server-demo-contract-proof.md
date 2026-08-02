# PS-012 FastAPI Server Mode + Demo API Contract — Proof

## Status

**Accepted.** ProofStudio is no longer service-only. `proofstudio.api.app:app`
is a real FastAPI instance and the full demo API contract is exercisable over
HTTP via `uvicorn proofstudio.api.app:app` or FastAPI's `TestClient`.

## Installed / Declared Dependencies

Server-mode dependencies were installed into the project venv and declared in
`apps/api/requirements.txt`:

| Dependency | Purpose                                   | Declared |
|------------|-------------------------------------------|----------|
| `fastapi`  | The ASGI web framework behind `app`       | yes      |
| `uvicorn`  | ASGI server runner (`uvicorn proofstudio.api.app:app`) | yes      |
| `httpx`    | Backs FastAPI's `TestClient` for the smoke | yes      |

Installed versions observed: `fastapi 0.138.1`, `uvicorn 0.49.0`,
`httpx 0.28.1`. Install command used:

```
python -m pip install fastapi uvicorn httpx
```

No environment folders or lock files were committed.

## Server Mode Result

- `proofstudio.api.app:app` is **not** `None`.
- `isinstance(app, fastapi.FastAPI)` is **True**.
- `FRAMEWORK_MODE` is now `"fastapi"` (was `"service_only"` before install).
- The module-level `app` is built by `create_app()`, which wires a single
  `ProofStudioService` (built by `create_default_service()`). Route handlers
  delegate to service methods — no business logic is duplicated in the handlers.

Run it directly:

```
uvicorn proofstudio.api.app:app
```

Interactive docs are available at FastAPI's default `/docs`.

## Endpoint List

All 10 required contract routes are registered and verified through the
`TestClient`:

| Method | Path                           |
|--------|--------------------------------|
| GET    | `/health`                      |
| GET    | `/version`                     |
| POST   | `/campaigns`                   |
| GET    | `/campaigns/{campaign_id}`     |
| POST   | `/runs`                        |
| GET    | `/runs/{run_id}`               |
| GET    | `/runs/{run_id}/attempts`      |
| GET    | `/runs/{run_id}/assets`        |
| GET    | `/runs/{run_id}/manifest`      |
| GET    | `/runs/{run_id}/passport`      |

`GET /health` returns `ok`, `service`, `mode`, `version` (PS-012 contract).
`GET /version` returns `service`, `version`, `framework_mode`, `capabilities`.
Capabilities include `provider_router`, `live_run_bridge`,
`b2_archive_rehydrate`, `provenance_passport`, and `fastapi_server`.

## Default Safe Dry-Run Behavior

The default `POST /runs` (omitting `run_live` or sending `run_live=false`) is a
safe dry-run:

- Run status is `dry_run_created`.
- No provider is selected; `selected_provider` is null.
- `attempts` list is empty (no provider was called).
- `assets` list is empty (no media was generated — no fake media).
- `manifest` is `ready: false` with an honest `not_ready_reason`; no manifest
  URI and no faked `stored_manifest_verify`.

Live execution only happens when `run_live=true` (and `dry_run=false`). The
optional live path in the smoke is gated behind `PROOFSTUDIO_PS012_LIVE=1` and
is never required for acceptance.

## Passport Endpoint Behavior

`GET /runs/{run_id}/passport` calls `service.get_run_passport(run_id)` (PS-011),
which reads the run, attempts, assets, and manifest through normal service
readbacks and assembles a Provenance Passport. It never reruns providers.

For a dry-run run it returns an honest no-evidence / no-media passport:

- `generation_summary.generated_media_present` is `false`.
- `manifest_verification.manifest_uri` is null; `stored_manifest_verify` is not
  faked to `true`.
- `archive_and_rehydration.status` is `not_available` (with a reason), not
  fabricated as available.
- `trust_boundary.non_claims` always surfaces `semantic_truth`,
  `legal_authenticity`, `c2pa_authenticity`, `human_authorship`, and
  `final_production_security`.

## Optional Live Mode Behavior

Not exercised by default. When `PROOFSTUDIO_PS012_LIVE=1` is set, the smoke
additionally creates a `run_live=true` run and records its status
(`summary.live_run_status`). A blocked/failed live run (e.g. no provider
credits) is recorded honestly and does not fail the smoke. Default acceptance
never requires live provider calls, provider credits, or B2.

## No-Provider-Call Proof in Default Mode

The PS-012 smoke replaces `proofstudio.api.services.execute_live_run` with a
sentinel that raises if invoked, then runs the full default contract (health,
version, create campaign, get campaign, dry-run create run, get run, attempts,
assets, manifest, passport) through the `TestClient`. The sentinel was invoked
**0 times**, proving the default dry-run path never calls a live provider.
`summary.default_no_live_provider_call` is `true`.

## No-B2-Call Proof in Default Mode

The smoke also replaces the archive module's B2 entry points
(`store_run_archive_with_genblaze`, `read_archive_from_b2`) with sentinels.
Neither was invoked during the default contract, proving no B2 call occurred.
`summary.default_no_b2_call` is `true`. This is corroborated structurally: the
dry-run run carries no manifest URI, zero assets, and a not-ready manifest.

## Truth Boundary

PS-012 proves ProofStudio has a runnable FastAPI demo API contract. It does
**not** prove production deployment, a public app URL, authentication,
production database persistence, background job reliability, legal
authenticity, C2PA authenticity, semantic truth, or human authorship. Those are
later slices.

## Connection to PS-011

PS-011 built the Review Room / Provenance Passport at the **service** layer
(`get_run_passport`). PS-012 exposes that same passport over HTTP at
`GET /runs/{run_id}/passport` with no reimplementation — the route handler
delegates directly to `service.get_run_passport(run_id)`. The passport's honest
no-evidence state for dry-runs is preserved exactly as PS-011 specified.

## Next Milestone Recommendation

With a stable HTTP contract in place, the next slice can build the judge-facing
web app against these real endpoints (`/health`, `/version`, `/campaigns`,
`/runs`, `/runs/{id}/passport`) and/or add deployment (public URL) — without
touching the service layer. The service layer remains the single source of
truth; the HTTP contract is now the demo surface.
