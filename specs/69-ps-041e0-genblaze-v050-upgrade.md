# PS-041E0 — Genblaze v0.5.0 Release-Wave Upgrade and Runtime Guard

Status: implementation slice. Backend only. Accepted base: `origin/accepted/proofstudio` at `35e19a2790ffabf908406fc4fdf01c19ec31707f`. Implementation branch: `ps-041e0/genblaze-v050-upgrade-v1`.

## 1. Official release

- Genblaze umbrella tag: `v0.5.0` (tag object `a3d0ad184e1e289e8179ffb980bebb68d0c6d436`).
- Release commit: `c5f7a5ba0bf3823d4c0d9546ee94a1e6d3102074`.
- The umbrella version is a release-wave label. The three Python packages remain on their own `0.3.x` lines. No claim is made that any individual Python package is itself version `0.5.0`. The umbrella `genblaze[all]` package is not installed.

## 2. Exact Python package mapping

Authoritative pin file: `apps/api/requirements.txt`. Exact pins only; no ranges, no bare names.

| Package             | Accepted (PS-035A) | PS-041E0 |
| ------------------- | ------------------ | -------- |
| `genblaze-core`     | 0.3.4              | 0.3.6    |
| `genblaze-s3`       | 0.3.4              | 0.3.5    |
| `genblaze-gmicloud` | 0.3.2              | 0.3.3    |

## 3. Accepted audit verdict

GREEN — UPGRADE RECOMMENDED. The audit proved:

- 34/34 PS-041D focused tests pass;
- PS-041D and PS-041C smokes pass;
- bundle fingerprint remains identical;
- all 16 node IDs remain identical;
- all 16 edge IDs remain identical;
- full portable Passport remains identical;
- Manifest 1.5 still excludes `parent_run_id` from `canonical_hash`;
- ProofStudio still includes `parent_run_id` in normalized conflict identity;
- contradictory lineage remains a safe 409;
- no source adaptation or data migration is required;
- rollback restores the previous three pins AND reverts the PS-041E0 source contract (guard integration + expected-version map) together; reverting pins alone is NOT sufficient.

## 4. Repository changes and dependency scope

Eight repository files are owned by PS-041E0 (see section 13). The
runtime-behavior surface is wider than `apps/api/requirements.txt` alone:
the runtime guard module, the startup wiring, the focused tests, the version
smoke, this spec, and the proof document are also added or modified.

`apps/api/requirements.txt` changes exactly four runtime dependency pins,
all exact-equality:

- `genblaze-core==0.3.6` (release-wave pin)
- `genblaze-s3==0.3.5` (release-wave pin)
- `genblaze-gmicloud==0.3.3` (release-wave pin)
- `pillow==12.3.0` (security pin; `genblaze-core` runtime requirement)

No minimum range, no compatibility marker, no environment override, no
umbrella package, and no provider package is introduced.

`setuptools==83.0.0` was applied to the audited local environment only. It
is NOT listed in `apps/api/requirements.txt` because setuptools is not an
application runtime dependency (no runtime package `Requires:` it). It is
base-image / build-layer tooling and must be pinned in a future deployment
base/build layer (or omitted from the runtime image) — see section 15.

## 5. Byte-stable identity

The accepted PS-041D fixture is parsed unchanged through the upgraded `genblaze-core` models. The byte-stable contract is preserved:

- Bundle fingerprint: `f5e85c7fd7f85c272f1205d8a276c89fd77076e583b9de9839591589a1cd8a6c` (unchanged).
- Node count: 16 (unchanged); every node ID unchanged.
- Edge count: 16 (unchanged); every edge ID unchanged.
- Portable Passport schema: `proofstudio.portable_lineage_passport.v1` (unchanged).

## 6. Manifest 1.5 parent-hash contract

Manifest 1.5 records `parent_run_id` as authoritative evidence for parent edges but excludes it from the canonical manifest hash. The upgrade does not change that contract. Every normalized parent edge therefore continues to carry `evidence_class=recorded` and `hash_covered=false`. ProofStudio still includes `parent_run_id` in the normalized conflict identity, so contradictory lineage remains a safe 409.

## 7. Runtime exact-version guard

`src/proofstudio/api/genblaze_runtime.py` is the single fail-closed guard. It:

- reads installed versions through `importlib.metadata.version` only;
- compares against an exact-equality allowlist hard-coded in the module;
- raises `GenblazeRuntimeVersionError` on any mismatch, missing distribution, partial upgrade, or unexpected prerelease/local version;
- performs no provider import, no provider call, and no B2/network access;
- never reads, prints, or logs environment variables, credentials, DB URLs, tokens, or paths;
- is never overridden by an environment variable and is never added to authorization or evidence identity.

The guard is wired into `proofstudio.api.__init__` and runs before any Genblaze-dependent submodule (`services`, `store`, `archive`, `live_bridge`, `genblaze_external_adapter`) is imported. `proofstudio.api.app.create_app()` consumes the same idempotent cached verification, so the underlying metadata check runs exactly once per process even when `create_app()` is called repeatedly.

Per-worker scope of the guard (precise statement):

- The guard prevents a single worker that is starting from the PS-041E0
  source from coming up if its installed Genblaze packages are missing, old,
  partial, newer, prerelease, or carry a local version suffix. Such a worker
  fails before readiness.
- The guard does NOT discover, inspect, or stop an already-running worker on
  a different source commit. It is purely a per-process startup check.
- Fleet-wide version uniformity is an operational deployment control, not a
  property enforced by the runtime guard alone. Deployment must stop or drain
  old workers before starting workers on the new commit; no rolling
  old-commit / new-commit overlap is authorized (see section 11).

## 8. Truth boundary unchanged

ProofStudio proves what the pipeline did. It does not claim semantic truth, legal authenticity, C2PA authenticity, human authorship, Object Lock / tamper-proof storage, browser-side B2 byte verification, public deployment verification, enterprise security, actual spend/latency/quota, or provider failures/reruns/variants unless evidenced. The upgrade does not broaden any of these claims.

## 9. No data migration

The upgrade is source- and identity-compatible. There is no bundle fingerprint migration, no Passport migration, no evidence migration, and no Auth Postgres migration. Durable accepted evidence remains readable.

## 10. No provider or live-B2 requirement

PS-041E0 makes no provider call and performs no live-B2 operation. The runtime guard, the focused tests, and the version smoke are all metadata-only.

## 11. Deployment stability

- All workers must be rebuilt/reinstalled against the new pins before restart.
- Deployment must stop or drain old workers before starting target workers.
- No rolling old-commit / new-commit overlap is authorized. Fleet-wide
  version uniformity is an operational deployment control: it is achieved by
  stopping/draining old workers before the new commit's workers start. The
  runtime guard does NOT, by itself, enforce fleet-wide version uniformity —
  it only prevents a single worker starting from the PS-041E0 source from
  coming up on missing/old/partial/newer/prerelease/local-suffix Genblaze
  packages, and it does not discover or stop already-running workers on the
  previous source commit.
- Process-local imported state is naturally lost on restart and is not durable evidence.

## 12. Rollback plan

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
- the absence of `src/proofstudio/api/genblaze_runtime.py` (the guard module);
- the absence of the guard wiring in `src/proofstudio/api/__init__.py` and
  `src/proofstudio/api/app.py`;
- the absence of the v0.5.0 expected-version map and `verify_runtime_versions_cached` startup integration;
- the absence of the PS-041E0 tests, smoke, spec, and proof doc.

### Preferred operational procedure

1. Stop or drain every API worker.
2. Revert the complete PS-041E0 upgrade commit (source + pins together).
3. Recreate/reinstall the Python environment from the reverted requirements.
4. Run `pip check`.
5. Run PS-041D focused tests and PS-041D/PS-041C smokes.
6. Restart every worker at the same reverted commit.
7. Verify no mixed old/new workers remain (the guard is gone in the reverted
   source, so this check is a manual process-level verification).

### Rollback validation transcript

- New PS-041E0 source + old packages (0.3.4 / 0.3.4 / 0.3.2): fails closed at
  `GenblazeRuntimeVersionError` before readiness (proven by the cold-start
  rollback probe in the proof document).
- Reverted source contract + old packages (0.3.4 / 0.3.4 / 0.3.2): passes
  (no guard present; PS-041D focused suite and PS-041D/PS-041C smokes green).
- No evidence migration, identity migration, Passport migration, or Auth
  Postgres migration is required on rollback.

### Review evidence status

The PS-041E0 pins and source are implemented and validated but **not yet
committed**. No review artifact may claim `"exact_pins_committed": true` until
an actual commit exists on the branch. The review pack records
`exact_pins_committed=false`.

## 13. Implementation scope

Eight owned files. The original seven-file plan grew by one repository file
(`src/proofstudio/api/__init__.py`) because the package initializer imports
the Genblaze-dependent `services`/`store` submodules before `app` is reached;
the guard therefore has to execute at the top of the package, before any of
those imports. This is a direct, reproducible dependency-security requirement
(documented in the proof document).

- `apps/api/requirements.txt` (pin lift);
- `src/proofstudio/api/genblaze_runtime.py` (guard module + cached verifier);
- `src/proofstudio/api/__init__.py` (guard executes before services/store/app imports);
- `src/proofstudio/api/app.py` (startup integration);
- `tests/test_ps041e0_genblaze_runtime_guard.py` (focused tests + cold-start subprocess tests);
- `scripts/ps041e0_genblaze_version_smoke.py` (version smoke);
- `specs/69-ps-041e0-genblaze-v050-upgrade.md` (this spec);
- `docs/ps-041e0-genblaze-v050-upgrade-proof.md` (proof document).

## 14. Validation

- Focused runtime-guard suite: 28 passed, including 14 true cold-start subprocess cases.
- PS-041D focused suite: 34 passed.
- PS-041D and PS-041C smokes pass.
- Version smoke passes: exact versions, accepted fingerprint, 16/16 nodes/edges, portable Passport schema unchanged, parent `hash_covered=false`, `provider_calls=0`, `b2_calls=0`.
- Central regression gate passes in non-mutating mode with 12 historical contracts.
- `pip check` clean; Python vulnerability audit clean.

## 15. Deployment security follow-up (non-blocking, PS-042)

The PS-041E0 full Python audit proves that the **current canonical 72-package
environment** had zero known vulnerabilities at validation time. It does NOT,
by itself, prove that every future deployment image will resolve the same
`setuptools` version (setuptools is not pinned in
`apps/api/requirements.txt`). A non-blocking final-deployment requirement is
therefore recorded for PS-042 / deployment hardening:

- PS-042 must verify the **built** deployment environment, not just the
  audited local environment.
- If `setuptools` is present in the built deployment image, it must resolve
  to `>= 83.0.0`.
- `pillow` must resolve exactly to `12.3.0` in the built deployment image.
- PS-042 must run `pip check` and a full `pip-audit` against the built
  deployment environment.
- No vulnerability-clean deployment claim is allowed until that built-image
  check passes.

This is a deployment reproducibility requirement, not a PS-041E0 runtime-code
change. PS-041E0 does not change runtime code to satisfy it.
