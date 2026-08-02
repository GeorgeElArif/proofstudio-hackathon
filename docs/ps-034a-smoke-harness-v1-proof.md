# PS-034A — Smoke Harness v1 (Proof)

Status: Proof
Date: 2026-06-30
Slice: PS-034A (validation infrastructure)
Base branch: `ps-034/lineage-comparison-lab`

## Why PS-034A Exists

PS-034A fixes ProofStudio's validation architecture before any new product
module continues. It is not a product feature. It is a validation
infrastructure slice that prevents recursive smoke chains, repeated frontend
builds, Git-index workarounds, prior-evidence mutation, and timeout-prone
regression execution.

## Root Cause Summary

Historical smokes validated their slice by launching the previous slice's
smoke. The chain (PS-034 -> PS-033 -> ... -> older) re-ran the frontend
pipeline repeatedly, re-touched evidence it did not own, and produced nested
status checks that saw temporary evidence changes as real diffs. Validation
responsibility was spread across many recursive entry points instead of one
central, non-recursive coordinator.

## Files Changed

PS-034A touches only validation infrastructure and documentation:

- `scripts/smoke_lib.py` (new) — shared validation helpers.
- `scripts/proofstudio_regression_gate.py` (new) — central non-recursive gate.
- `scripts/ps034a_smoke_harness_v1_smoke.py` (new, optional) — PS-034A slice smoke.
- `docs/validation/proofstudio-smoke-harness-v1.md` (new) — validation policy.
- `docs/ps-034a-smoke-harness-v1-proof.md` (new) — this proof.
- `docs/evidence/ps-034a/smoke-harness-v1-report.json` (new) — gate evidence.
- `specs/44-ps-034a-smoke-harness-v1.md` (spec, already present).

No product UI, provider, backend API, deployment config, or historical evidence
is modified.

## Validation Policy Locked

Feature slice smokes validate the slice. The regression gate validates the release.

- No recursive smoke execution.
- No Git index hiding flags.
- No polling background watcher / concurrent rewriter workaround.
- A slice smoke may write only its own evidence file.
- Frontend typecheck and build run once at the top-level gate.
- Historical regression is contract-based, not recursive.
- PS-034B historical local-mode retrofit is deferred.

## Smoke Library Summary

`scripts/smoke_lib.py` centralizes the repeated validation logic:

- `repo_root()`, `read_text()`, `read_json()`, `write_json_atomic()`
- `run_command()`, `git_status_short()`, `sha256_bytes()`
- `assert_no_staged_changes()`, `assert_no_hidden_git_flags()`
- `assert_status_only()`, `assert_no_paths_changed()`
- `assert_no_forbidden_terms()`, `assert_no_secret_like_patterns()`
- `assert_frontend_typecheck_build_once()` (single-invocation guard)
- `assert_route_registered()`, `assert_component_imported()`, `assert_file_exists()`
- `assert_evidence_contract(path, required_constants=...)`
- `assert_no_recursive_smoke_execution(path)` (AST-based recursion detection)
- forbidden-term constant lists (assembled at runtime so the source never
  contains the literal forbidden strings it polices)

## Regression Gate Summary

`scripts/proofstudio_regression_gate.py` is the single cross-slice coordinator.
It contains no historical feature-smoke path references. Historical regression
uses a contract table (slice id, evidence JSON path, route path, component /
source file path, golden-constant requirement, ok/pass expectation) — never
smoke script paths. On each run it:

1. verifies the repo root
2. verifies no staged changes
3. verifies no hidden Git index flags before validation
4. rejects Git-hiding and polling-watcher workaround terms in harness files
5. verifies the gate itself is non-recursive via AST-based execution detection
6. verifies prior-slice evidence is not modified
7. verifies accepted historical contracts for PS-021 through PS-034 from the
   contract table (evidence existence, ok status, no fail checks, golden
   constants, route registration, component presence)
8. verifies golden constants against the canonical golden run
9. optionally runs frontend typecheck/build exactly once (`--frontend`) through
   the shared library helper
10. verifies no hidden Git index flags after validation
11. writes the PS-034A evidence report
12. exits nonzero on any failure

It delegates every subprocess need to `smoke_lib` (only for the top-level
`npm run typecheck` and `npm run build` commands); it never calls a provider,
never reads arbitrary B2, and never mutates prior evidence.

## No Recursive Smoke Confirmation

Confirmed. Recursive execution is detected structurally via AST parsing, not
with brittle text grep. The shared helper
`assert_no_recursive_smoke_execution` walks the parsed syntax tree and flags
only real `Call` nodes that invoke a process-execution primitive
(`subprocess.run`, `subprocess.check_call`, `subprocess.check_output`,
`os.system`, `os.popen`, `Popen`) or a `run_command`-family helper whose
arguments name a feature smoke script. The gate never launches a feature smoke.
Historical slices are verified through checked-in evidence contracts and a
contract table, not by re-running their smokes.

## No Git Hiding Confirmation

Confirmed. No harness file uses Git index hiding. The gate checks
`git ls-files -v` before and after validation and rejects any lowercase tag.
The literal flag/command forms are forbidden terms in the harness source.

## No Polling Watcher Workaround Confirmation

Confirmed. No background watcher, concurrent rewriter, or polling mechanism
that rewrites prior evidence is present. The harness source forbids those
workaround tokens and the gate asserts their absence on every run.

## No Prior Evidence Mutation Confirmation

Confirmed. The gate guards every historical evidence prefix
(`docs/evidence/ps-019/` through `docs/evidence/ps-034/` and
`docs/evidence/demo/`) and asserts they remain unchanged. PS-034A writes only
`docs/evidence/ps-034a/`.

## Frontend Build Once Policy

Frontend typecheck and build run once at the top-level gate. The shared library
counts frontend invocations per process and rejects any second build attempt.
Feature smokes never trigger a frontend build.

## Evidence Report Schema Policy

Evidence report keys must never be overloaded. A field whose name implies a
boolean success flag must remain a boolean; a list of details must live in a
field whose name explicitly denotes a list.

- Boolean fields must remain booleans.
- Detail/list fields must use explicit detail names such as `_ids`, `_details`,
  or `_failures`.
- Do not overload evidence report keys.

For historical contract verification the PS-034A gate emits a strict schema:
`historical_contracts_verified` is a boolean that is `true` only when every
required historical contract passes (never a list); `historical_contract_ids`
is the list of verified slice ids; `historical_contract_count` is the integer
count of those ids; and `historical_contract_failures` is the list of
per-contract failure descriptions (empty on success). The PS-034A slice smoke
asserts this schema on every run.

## PS-034B Cleanup Plan

Historical smoke local-mode retrofit is deferred to PS-034B. PS-034B will
retrofit PS-023 through PS-033 smokes to support local / contract / no-frontend
modes without launching other smokes and without rebuilding the frontend.
PS-034A intentionally leaves those historical scripts frozen.

## Validation Commands

```bash
# contract-only
python scripts/proofstudio_regression_gate.py --current ps034a --no-frontend

# full release readiness (frontend once)
python scripts/proofstudio_regression_gate.py --current ps034a --frontend

# PS-034A slice smoke
python scripts/ps034a_smoke_harness_v1_smoke.py

# confirm no hidden git index flags
git ls-files -v | awk '$1 ~ /^[a-z]/ {print}'
```

## Limitations

- Contract-based regression confirms accepted evidence and current route/file
  presence. It does not prove every old smoke script would re-run today. That
  full retrofit belongs to PS-034B.
- Historical smokes PS-023 through PS-033 are intentionally not modified by
  PS-034A.
- The PS-034A slice smoke exercises the gate in contract-only mode to preserve
  the build-once policy; the frontend build is exercised at the top-level
  validation step.
- The evidence report `checked_at` timestamp updates on each gate run by design.
