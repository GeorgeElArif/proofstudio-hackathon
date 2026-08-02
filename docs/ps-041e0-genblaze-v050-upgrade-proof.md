# PS-041E0 — Genblaze v0.5.0 Release-Wave Upgrade Proof

Slice: PS-041E0 — Genblaze v0.5.0 Release-Wave Upgrade and Runtime Guard.
Implementation branch: `ps-041e0/genblaze-v050-upgrade-v1`, built from accepted base `origin/accepted/proofstudio` at `35e19a2790ffabf908406fc4fdf01c19ec31707f`.

## 1. Official release

- Genblaze umbrella tag: `v0.5.0` (tag object `a3d0ad184e1e289e8179ffb980bebb68d0c6d436`).
- Release commit: `c5f7a5ba0bf3823d4c0d9546ee94a1e6d3102074`.
- The umbrella version is a release-wave label only. The three Python packages remain on their own `0.3.x` lines; no claim is made that any individual Python package is itself version `0.5.0`. The umbrella `genblaze[all]` package is not installed.

## 2. Exact Python package mapping

Authoritative pin file: `apps/api/requirements.txt`. Exact pins only; no ranges, no bare names.

| Package             | Accepted (PS-035A) | PS-041E0 |
| ------------------- | ------------------ | -------- |
| `genblaze-core`     | 0.3.4              | 0.3.6    |
| `genblaze-s3`       | 0.3.4              | 0.3.5    |
| `genblaze-gmicloud` | 0.3.2              | 0.3.3    |

## 3. Accepted audit verdict

GREEN — UPGRADE RECOMMENDED. The audit proved 34/34 PS-041D focused tests pass, PS-041D and PS-041C smokes pass, the bundle fingerprint, every node ID, every edge ID, and the full portable Passport remain identical, Manifest 1.5 still excludes `parent_run_id` from `canonical_hash`, ProofStudio still includes `parent_run_id` in normalized conflict identity, contradictory lineage remains a safe 409, no source adaptation or data migration is required, and rollback restores the previous three pins AND reverts the PS-041E0 source contract (guard integration + expected-version map) together (reverting pins alone is NOT sufficient).

## 4. Repository changes and dependency scope

Eight repository files are owned by PS-041E0 (see section 14). The change
is NOT limited to `apps/api/requirements.txt`: the runtime guard module, the
startup wiring, the focused tests, the version smoke, this proof document,
and the spec are also added or modified. This section separates two distinct
kinds of dependency change.

### A. Repository runtime dependency change (`apps/api/requirements.txt`)

Exactly four exact-equality runtime pins change:

- three Genblaze release-wave pins:
  - `genblaze-core==0.3.6`
  - `genblaze-s3==0.3.5`
  - `genblaze-gmicloud==0.3.3`
- one Pillow security pin:
  - `pillow==12.3.0` (Pillow is a runtime requirement of `genblaze-core`)

Pillow is a repository runtime pin, not an audited-tooling fix: it lives in
`apps/api/requirements.txt` so every fresh deploy resolves to the fixed
release. No minimum range, compatibility marker, environment override,
umbrella package, or provider package is introduced.

### B. Audited-environment tooling change (NOT a runtime requirement)

`setuptools==83.0.0` was applied to the audited local environment only. It
is NOT added to `apps/api/requirements.txt` because setuptools is not an
application runtime dependency (no runtime package `Requires:` it; it is
build/base-image tooling). It must be pinned in a future deployment
base/build layer or omitted from the runtime image entirely.

### What the full Python audit proves and does not prove

The full Python audit proves that the **current canonical 72-package
environment** had zero known vulnerabilities at validation time. It does
NOT, by itself, prove that every future deployment image will resolve the
same `setuptools` version, because `setuptools` is not pinned in
`apps/api/requirements.txt`. The built-deployment-environment verification
is therefore recorded as a PS-042 follow-up (section 16).

## 5. Byte-stable bundle / node / edge / Passport identity

The accepted PS-041D fixture is parsed unchanged through the upgraded `genblaze-core` Manifest 1.5 models:

- Bundle fingerprint: `f5e85c7fd7f85c272f1205d8a276c89fd77076e583b9de9839591589a1cd8a6c` (unchanged).
- Node count: 16 (unchanged); every node ID unchanged.
- Edge count: 16 (unchanged); every edge ID unchanged.
- Portable Passport schema: `proofstudio.portable_lineage_passport.v1` (unchanged).

## 6. Manifest 1.5 parent-hash contract

Manifest 1.5 records `parent_run_id` as authoritative evidence but excludes it from the canonical manifest hash. The upgrade does not change that contract. Every normalized parent edge continues to carry `evidence_class=recorded` and `hash_covered=false`. ProofStudio still includes `parent_run_id` in the normalized conflict identity, so contradictory lineage remains a safe 409.

## 7. Runtime exact-version guard

`src/proofstudio/api/genblaze_runtime.py` is the single fail-closed guard. It reads installed versions through `importlib.metadata.version` only, compares against an exact-equality allowlist hard-coded in the module, and raises `GenblazeRuntimeVersionError` on any mismatch, missing distribution, partial upgrade, or unexpected prerelease/local version. It performs no provider import, no provider call, and no B2/network access; never reads, prints, or logs environment variables, credentials, DB URLs, tokens, or paths; is never overridden by an environment variable; and is never added to authorization or evidence identity.

The guard is wired into `proofstudio.api.__init__` and runs before any Genblaze-dependent submodule (`services`, `store`, `archive`, `live_bridge`, `genblaze_external_adapter`) is imported. This is necessary because the package initializer imports `services` (which transitively imports `genblaze_external_adapter` → `genblaze_core`, plus `live_bridge` → providers + `genblaze_store`) before `app` is reached; without the package-level guard, a missing/mismatched distribution would raise an uncontrolled `ImportError` with a stack trace from `services` instead of the controlled `GenblazeRuntimeVersionError`. `proofstudio.api.app.create_app()` consumes the same idempotent cached verification (`verify_runtime_versions_cached`), so the underlying metadata check runs exactly once per process even when `create_app()` is called repeatedly.

### Guard behavior summary

| Probe                                                | Result       |
| ---------------------------------------------------- | ------------ |
| Exact target versions (`0.3.6 / 0.3.5 / 0.3.3`)      | pass         |
| `genblaze-core` held at `0.3.4` (partial upgrade)    | fail closed  |
| `genblaze-s3` held at `0.3.4` (partial upgrade)      | fail closed  |
| `genblaze-gmicloud` held at `0.3.2` (partial upgrade)| fail closed  |
| Missing `genblaze-core`                              | fail closed  |
| Missing `genblaze-s3`                                | fail closed  |
| Missing `genblaze-gmicloud`                          | fail closed  |
| Unexpected newer version                             | fail closed  |
| Unexpected prerelease/local/epoch version            | fail closed  |
| Cold-start failure (fresh subprocess)                | controlled `GenblazeRuntimeVersionError`; `services`, `genblaze_external_adapter`, `store`, any `proofstudio.providers.*`, `boto3`, and `genblaze_core` all stay unimported; no route becomes visible |
| Error message leaks                                  | package names and safe versions only; no env values, credentials, DB URLs, tokens, paths, or stack traces |
| Idempotent startup                                   | underlying metadata check runs exactly once per process across `__init__` + `create_app()` repeats |

## 8. Mixed-worker policy

Per-worker scope of the guard (precise statement):

- The runtime guard prevents a single worker that is starting from the
  PS-041E0 source from coming up if its installed Genblaze packages are
  missing, old, partial, newer, prerelease, or carry a local version
  suffix. Such a worker fails before readiness.
- The guard does NOT discover, inspect, or stop an already-running worker
  on a different source commit. It is purely a per-process startup check.
- Fleet-wide version uniformity is an operational deployment control, not a
  property enforced by the runtime guard alone.

Operational deployment control:

- All workers must be rebuilt/reinstalled against the new pins before
  restart.
- Deployment must stop or drain old workers before starting target workers.
- No rolling old-commit / new-commit overlap is authorized.
- Process-local imported state is naturally lost on restart and is not
  durable evidence.

No claim is made that the runtime guard alone enforces fleet-wide version
uniformity. The guard enforces per-worker version exactness at startup;
fleet-wide uniformity is achieved by the stop/drain deployment procedure.

## 9. No data migration

The upgrade is source- and identity-compatible. There is no bundle fingerprint migration, no Passport migration, no evidence migration, and no Auth Postgres migration. Durable accepted evidence remains readable.

## 10. No provider or live-B2 requirement

PS-041E0 makes no provider call and performs no live-B2 operation. The runtime guard, the focused tests, and the version smoke are metadata-only. `provider_calls=0` and `b2_calls=0` throughout.

## 11. Rollback plan

Rollback restores the prior accepted PS-035A/PS-041D state. It must restore
**both** halves of the contract together; reverting the dependency pins alone
is NOT sufficient, because the PS-041E0 source still enforces the v0.5.0
exact-version guard and would refuse to start against the old pins.

### A. Dependency pins to restore

- `genblaze-core==0.3.4`
- `genblaze-s3==0.3.4`
- `genblaze-gmicloud==0.3.2`

### B. Matching source expectations to restore

Revert the complete PS-041E0 upgrade commit, which restores:

- `apps/api/requirements.txt` to the prior three pins;
- the absence of `src/proofstudio/api/genblaze_runtime.py`;
- the absence of the guard wiring in `src/proofstudio/api/__init__.py` and
  `src/proofstudio/api/app.py`;
- the absence of the v0.5.0 expected-version map and the
  `verify_runtime_versions_cached` startup integration;
- the absence of the PS-041E0 tests, smoke, spec, and proof doc.

### Preferred operational procedure

1. Stop or drain every API worker.
2. Revert the complete PS-041E0 upgrade commit (source + pins together).
3. Recreate/reinstall the Python environment from the reverted requirements.
4. Run `pip check`.
5. Run PS-041D focused tests and PS-041D/PS-041C smokes.
6. Restart every worker at the same reverted commit.
7. Verify no mixed old/new workers remain (manual process-level check, since
   the reverted source has no guard).

### Rollback validation transcript

The cold-start guard harness was used to prove the two rollback invariants.
No canonical distribution was modified; each probe patches
`importlib.metadata.version` in a fresh subprocess only.

1. **New PS-041E0 source + old packages** (genblaze-core 0.3.4 /
   genblaze-s3 0.3.4 / genblaze-gmicloud 0.3.2): the cold-start guard raises
   the controlled `GenblazeRuntimeVersionError` before `services`,
   `genblaze_external_adapter`, `store`, any `proofstudio.providers.*`,
   `boto3`, or `genblaze_core` is imported; no route becomes visible; no
   stack trace, path, environment value, credential, or DB URL appears in the
   captured diagnostic. Result: **fails closed** (as required).
2. **Reverted source contract + old packages**: with the PS-041E0 source
   reverted the guard module is absent, so the reverted `requirements.txt`
   pins (0.3.4 / 0.3.4 / 0.3.2) match the installed packages; PS-041D focused
   suite (34 passed) and PS-041D/PS-041C smokes pass. Result: **passes**.
3. **Migration**: no bundle fingerprint migration, no Passport migration, no
   evidence migration, and no Auth Postgres migration is required on
   rollback. Durable accepted evidence remains readable.

### Review evidence status

The PS-041E0 pins and source are implemented and validated but **not yet
committed**. The review pack therefore records `exact_pins_committed=false`.
No artifact may claim `"exact_pins_committed": true` until an actual commit
exists on the branch.

## 12. Truth boundary

ProofStudio proves what the pipeline did. It does not claim semantic truth, legal authenticity, C2PA authenticity, human authorship, Object Lock / tamper-proof storage, browser-side B2 byte verification, public deployment verification, enterprise security, actual spend/latency/quota, or provider failures/reruns/variants unless evidenced. The upgrade does not broaden any of these claims.

## 13. Validation summary

- Focused runtime-guard suite: 28 passed, including 14 true cold-start subprocess cases. Breakdown: 11 in-process unit tests + 2 cached-verifier behavior tests + 1 `create_app` idempotency test + 14 cold-start subprocess cases (1 exact-versions import-and-serve, 3 missing-distribution, 3 old-distribution, and 7 parametrized unexpected-newer/prerelease/local cases).
- PS-041D focused suite: 34 passed.
- PS-041D smoke: pass.
- PS-041C smoke: pass.
- Version smoke: exact versions, accepted fingerprint, 16/16 nodes/edges, portable Passport schema unchanged, parent `hash_covered=false`, `provider_calls=0`, `b2_calls=0`.
- Cold-start guard harness (fresh subprocess per scenario): exact versions import and serve routes; missing core / missing s3 / missing gmicloud / old core / old s3 / old gmicloud / unexpected newer or prerelease each raise the controlled `GenblazeRuntimeVersionError` before `services`, `genblaze_external_adapter`, `store`, any provider, `boto3`, or `genblaze_core` is imported; no route becomes visible; no stack trace, path, environment value, credential, or DB URL appears in the captured diagnostic.
- Auth and web regressions: pass.
- Production audits: 0 vulnerabilities.
- Central regression gate: 12 historical contracts, frontend ran, non-mutating, PS-034A digest unchanged, no provider call, no live B2.
- `pip check`: clean.
- Python vulnerability audit: 0 known vulnerabilities. Pillow was pinned to `12.3.0` as a repository runtime requirement in `apps/api/requirements.txt`; `setuptools==83.0.0` was applied to the audited local environment only as base-image tooling (not an application runtime requirement).

## 14. Implementation scope

Eight owned files. The original seven-file plan grew by one repository file
(`src/proofstudio/api/__init__.py`) because the package initializer imports
the Genblaze-dependent `services`/`store` submodules before `app` is reached;
the guard therefore has to execute at the top of the package, before any of
those imports. This is the direct, reproducible dependency-security
requirement that justifies the one additional repository file.

## 15. Known limitations

- Process-local imported bundle state is not durable and is naturally lost on restart; durable accepted evidence remains readable.
- The upgrade does not prove upstream improvements that ProofStudio does not directly use.
- The runtime guard enforces exact versions at FastAPI readiness for a single worker starting from the PS-041E0 source; it does not provide a rolling mixed-version deployment path and does not enforce fleet-wide version uniformity on its own.
- The guard does not change authorization, PS-041D identity, or Passport contracts.

## 16. Deployment security follow-up (non-blocking, PS-042)

The PS-041E0 full Python audit proves that the **current canonical 72-package
environment** had zero known vulnerabilities at validation time. It does
NOT, by itself, prove that every future deployment image will resolve the
same `setuptools` version, because `setuptools` is not pinned in
`apps/api/requirements.txt` (it is base-image tooling, not an application
runtime dependency).

A non-blocking final-deployment requirement is therefore recorded for
PS-042 / deployment hardening:

- PS-042 must verify the **built** deployment environment, not just the
  audited local environment.
- If `setuptools` is present in the built deployment image, it must resolve
  to `>= 83.0.0`.
- `pillow` must resolve exactly to `12.3.0` in the built deployment image
  (it is pinned in `apps/api/requirements.txt`, so this should hold, but the
  built image must still be checked).
- PS-042 must run `pip check` and a full `pip-audit` against the built
  deployment environment.
- No vulnerability-clean deployment claim is allowed until that built-image
  check passes.

This is a deployment reproducibility requirement, not a PS-041E0 runtime-code
change. PS-041E0 does not change runtime code to satisfy it.
