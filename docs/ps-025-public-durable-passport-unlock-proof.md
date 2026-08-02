# PS-025 — Public Durable Passport Unlock — Proof

## Status

Implemented. Local contract verified. Public deployment pending.

## Blocker from PS-024

PS-024 pinned the verified golden demo run
(`run_89d967f9000045efa22ed4cc78cfa67f`) and its durable B2 evidence, but the
public Provenance Passport pinning remained blocked:

- The PS-021 verified run was created during a local smoke and was never present
  in the public backend's in-memory store.
- The public deployment's durable read gates
  (`PROOFSTUDIO_DURABLE_PASSPORT_READ_ENABLED` and
  `PROOFSTUDIO_DURABLE_PASSPORT_B2_READ_ENABLED`) both default to `false`, so
  `GET /runs/<run_id>/passport` returned `404` for this run on the public API.
- `public_passport_url` in `docs/evidence/demo/golden-demo-run.json` was `null`
  because no verified public passport URL existed. No URL was invented.

PS-025 resolves this blocker with the narrowest safe unlock.

## Implementation Design

PS-025 adds a single, narrow allowlist path that resolves ONLY the verified
golden demo `run_id`, from checked-in evidence only.

### Backend

`src/proofstudio/api/durable_passport.py` gains a golden-demo resolver:

- `load_golden_demo_manifest()` reads `docs/evidence/demo/golden-demo-run.json`
  (a checked-in, public, evidence-derived file with no secrets).
- `golden_demo_run_id()` returns the verified golden run id from the manifest.
- `golden_demo_unlock_enabled()` reports whether the manifest carries the
  required durable fields.
- `try_golden_demo_passport(service, run_id)` returns an evidence-derived
  Provenance Passport when `run_id` exactly equals the golden run id, and
  `None` for any other run id.

`src/proofstudio/api/services.py` `get_run_passport` calls
`try_golden_demo_passport` only as a fallback after:

1. the run is not in the in-memory store, AND
2. the gated durable-rehydrate path (`try_rehydrate_passport`, which still
   requires the default-off durable read flags) did not resolve it.

The golden path is intentionally NOT gated behind the durable read / B2 read
flags. Safety comes from the narrow allowlist (exact `run_id` equality), not
from a gate. This is what lets the public deployment resolve the single golden
run without broad durable reads and without B2 credentials.

### Frontend

`apps/web/src/JudgeCockpitHome.tsx`:

- Adds a `GOLDEN_DEMO_RUN_ID` constant sourced verbatim from the manifest.
- Pre-fills the run-id input with the golden run id so the existing
  "View Provenance Passport" / "Open Passport" CTAs open the golden passport.
- Adds an explicit "Open Golden Passport" CTA in the golden-demo-run section
  using a dynamically-built href (`goldenPassportHref`).
- Updates the copy to state that PS-025 unlocked the golden passport locally
  while the public deployment remains planned.

The href is always built dynamically from the constant (never a literal pinned
`href="/passport/run_..."`), so no fabricated URL is hard-coded into the page.

### No-provider-rerun confirmation

The golden resolver reads the checked-in manifest only. It performs:

- no B2 read,
- no provider call,
- no new run,
- no media write.

The recorded `provider_calls_during_rehydrate = 0` and
`no_live_provider_call_during_rehydrate = true` are carried verbatim from the
PS-021 source evidence via the manifest. They describe the original PS-021
durable rehydrate; PS-025 does not rerun it.

## Safety Model

### Public unlock scope

- Scope: `golden_demo_only`. Only `run_89d967f9000045efa22ed4cc78cfa67f`
  resolves through the PS-025 unlock path.
- Any other `run_id` (including arbitrary attacker-chosen ids) still returns
  `404` from `GET /runs/<run_id>/passport` when the run is not in the store and
  durable gates are off.
- The PS-025 smoke proves this: an arbitrary run id returns `404`.

### No-broad-public-read confirmation

- The durable read gates (`PROOFSTUDIO_DURABLE_PASSPORT_READ_ENABLED`,
  `PROOFSTUDIO_DURABLE_PASSPORT_B2_READ_ENABLED`) remain default-off. They are
  not changed by PS-025.
- The golden path does not touch `try_rehydrate_passport`'s gate logic and does
  not call `read_archive_from_b2`.
- Arbitrary public run ids cannot trigger durable B2 reads.

## Source Evidence Used

- `docs/evidence/demo/golden-demo-run.json` (PS-024 golden manifest) — the
  single source the golden resolver reads at runtime.
- `docs/evidence/ps-021/live-b2-durable-rehydrate-smoke.json` — the original
  durable rehydrate proof (archive URI/SHA-256, `b2_rehydrated`, zero provider
  calls).

Historical PS-019/020/021 evidence JSON and historical proof scripts were NOT
modified.

## Route / API Contract

Route: `GET /runs/{run_id}/passport` (unchanged path; behavior extended for one
allowlisted run id only).

For the golden `run_id`, when the run is not in the store and durable gates did
not resolve it, the response is `200` with a Provenance Passport that includes:

- `passport_identity.run_id` / `campaign_id` matching the manifest.
- `archive_and_rehydration` with `status: "available"`, the real `archive_uri`,
  `archive_sha256`, `rehydrate_source: "b2_rehydrated"`,
  `rehydrate_completed: true`, and
  `no_live_provider_call_during_rehydrate: true`.
- `durable_passport` with `source: "golden_demo_evidence_derived"`.
- `golden_demo_unlock` block carrying the PS-025 required fields:
  `public_unlock_scope: "golden_demo_only"`, `source`,
  `source_manifest`, `run_id`, `campaign_id`, `archive_uri`, `archive_sha256`,
  `rehydrate_source`, `provider_calls_during_rehydrate: 0`,
  `no_live_provider_call_during_rehydrate: true`,
  `no_broad_public_durable_read: true`, `local_contract_proof`,
  `public_deployment_pending`, and `truth_boundary`.
- The canonical PS-011 `truth_boundary` string.

For any non-golden `run_id` not in the store, the response remains `404`
(unchanged). `GET /runs/{run_id}` (the run record route) is unchanged and still
returns `404` for the golden run — only the passport route resolves it.

## Truth Boundary Confirmation

The response carries the truth boundary and the golden_demo_unlock block both
state the boundary. PS-025 does not prove semantic truth, legal authenticity,
C2PA authenticity, or human authorship. It does not claim production security,
auth, multi-user support, Object Lock, or tamper-proof storage.

## Frontend CTA Target Map

| CTA | Target | Condition |
|-----|--------|-----------|
| Hero "View Provenance Passport" | `/passport/<run_id>` (dynamic, pre-filled golden) | always (input pre-filled with golden run id) |
| Golden demo run "Open Golden Passport" | `/passport/run_89d967f9000045efa22ed4cc78cfa67f` (dynamic `goldenPassportHref`) | PS-025 local contract verified |
| Passport CTA tile "Open Passport" | `/passport/<run_id>` (dynamic, pre-filled golden) | input non-empty (default golden) |
| "Open PS-021 Proof" | external GitHub proof doc | always |

The frontend only links to the golden passport because the PS-025 smoke verified
the backend route resolves that run id. The link is relative
(`/passport/<golden_run_id>`); on the public deployment it requires the new
backend to be deployed first (public deployment pending).

## Validation Commands

```bash
cd /home/proofstudio-work/proofstudio
python scripts/ps025_public_durable_passport_unlock_smoke.py
python scripts/ps024_golden_demo_run_pinning_smoke.py
python scripts/ps023_judge_cockpit_home_smoke.py

cd apps/web
npm run typecheck
npm run build
cd ../..

git diff --check
git status --short --branch --untracked-files=all
```

## Smoke Result

PS-025 smoke (`scripts/ps025_public_durable_passport_unlock_smoke.py`): **PASS**
(all 14 checks). Evidence written to
`docs/evidence/ps-025/public-durable-passport-unlock-smoke.json`.

PS-024 smoke: **PASS** (unchanged). PS-023 smoke: **PASS** (unchanged).

## Local vs Public Honesty

- `local_contract_proof`: **true** — the FastAPI TestClient (fresh empty store)
  resolves the golden run with `200`, returns all required fields, and returns
  `404` for an arbitrary run id.
- `public_deployment_verified`: **false** — the public Render deployment was NOT
  tested in this slice. The new backend code must be deployed and the public URL
  verified separately (a follow-up deployment gate).
- `public_deployment_pending`: **true**.
- `public_passport_url`: remains `null` in the PS-024 manifest because the
  public URL is not verified.

## Files Changed

Created:

- `scripts/ps025_public_durable_passport_unlock_smoke.py`
- `docs/evidence/ps-025/public-durable-passport-unlock-smoke.json`
- `docs/ps-025-public-durable-passport-unlock-proof.md`

Modified:

- `src/proofstudio/api/durable_passport.py` — golden-demo resolver.
- `src/proofstudio/api/services.py` — golden-demo fallback in `get_run_passport`.
- `apps/web/src/JudgeCockpitHome.tsx` — golden passport link + updated copy.

Not modified (as required):

- historical PS-019/020/021 evidence JSON,
- historical proof scripts (PS-023/024 smokes),
- provider router code,
- `docs/evidence/demo/golden-demo-run.json` (public_passport_url stays null;
  public deployment is not verified).

## Limitations / Risks

- The golden passport is **evidence-derived**, not a full live rehydrate in this
  path. The PS-011 passport it returns honestly shows no attempts/assets/manifest
  verification for the golden run (those are not in the checked-in manifest).
  The durable archive evidence (`b2_rehydrated`, zero provider calls, archive
  URI/SHA-256) IS present and matches PS-021.
- Public deployment is not verified here. A judge opening
  `/passport/<golden_run_id>` on the currently-deployed Render frontend will hit
  the old backend and get `404` until the PS-025 backend is deployed and the
  frontend is rebuilt. This is recorded as `public_deployment_pending`.
- The unlock is deliberately narrow (single golden run). Scaling durable public
  reads to more runs is explicitly out of scope and would require a new slice
  with its own safety review.
