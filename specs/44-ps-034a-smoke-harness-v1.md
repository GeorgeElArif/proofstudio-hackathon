# PS-034A — Smoke Harness v1

Status: Spec
Date: 2026-06-30
Base branch: `ps-034/lineage-comparison-lab`

## Purpose

PS-034A fixes ProofStudio's validation architecture before any new product module continues.

This is not a product feature slice.

This is a validation infrastructure slice that prevents recursive smoke chains, repeated frontend builds, hidden Git-index workarounds, prior-evidence mutation, and timeout-prone regression execution.

## Problem Statement

Historical slice smokes grew recursively.

The broken pattern was:

- PS-034 smoke runs PS-033 smoke
- PS-033 smoke runs PS-032 smoke
- PS-032 smoke runs PS-031 smoke
- older smokes run more older smokes
- multiple smokes run frontend typecheck/build repeatedly
- some historical smokes rewrite evidence
- nested status checks see temporary evidence changes
- deep subprocesses time out
- agents attempted workarounds such as Git hiding flags or polling guardians

This is not acceptable for a professional product.

## Architectural Decision

Feature slice smokes validate the current slice.

A central regression gate validates release readiness.

They are not the same thing.

From PS-035 onward:

- no feature smoke may recursively execute another smoke
- no feature smoke may manipulate Git index flags
- no feature smoke may mutate prior-slice evidence
- no feature smoke may repeatedly run frontend builds through nested chains
- no feature smoke may call providers unless that slice explicitly owns provider execution
- no feature smoke may read arbitrary B2 objects

## Scope

PS-034A should add the validation harness foundation.

Required new files:

- `scripts/smoke_lib.py`
- `scripts/proofstudio_regression_gate.py`
- `docs/validation/proofstudio-smoke-harness-v1.md`
- `docs/evidence/ps-034a/smoke-harness-v1-report.json`
- `docs/ps-034a-smoke-harness-v1-proof.md`

Optional new file:

- `scripts/ps034a_smoke_harness_v1_smoke.py`

PS-034A should not retrofit PS-023 through PS-033 smokes yet.

That later cleanup will be PS-034B.

## Non-Goals

Do not implement PS-035.

Do not rewrite historical smoke scripts PS-023 through PS-033.

Do not mutate historical evidence JSON.

Do not modify product UI unless needed to document validation status, which is not expected.

Do not modify provider code.

Do not modify backend API.

Do not modify deployment config.

Do not call providers.

Do not read arbitrary B2 objects.

Do not use Git hiding flags.

## Required Validation Policy

The harness must document and enforce:

### 1. No Recursive Smoke Execution

A smoke script must not call another smoke script.

Forbidden patterns include:

- invoking `scripts/ps0*_smoke.py` from inside another smoke
- subprocess-running another feature smoke
- nesting regression chains
- using one slice smoke as the parent of prior slice smokes

### 2. Central Regression Gate Only

Only `scripts/proofstudio_regression_gate.py` may coordinate cross-slice validation.

It must do so non-recursively.

It should validate prior slices through contracts:

- checked-in evidence exists
- accepted status exists where available
- golden constants match where applicable
- expected source files exist
- expected routes exist
- forbidden claims are absent
- Git status remains clean except expected current-slice files

### 3. Frontend Build Once

The top-level regression gate may run:

- frontend typecheck once
- frontend build once

Feature smokes must not cause repeated nested frontend builds.

### 4. Evidence Ownership

A slice smoke may write only its own evidence file.

Example:

- PS-034 may write `docs/evidence/ps-034/...`
- PS-034A may write `docs/evidence/ps-034a/...`

A slice smoke must not write, unlink, or hide prior-slice evidence.

### 5. No Git Hiding Flags

The harness must reject these terms in smoke scripts and validation docs:

- `assume-unchanged`
- `skip-worktree`
- `git update-index`
- `update-index`

The harness must also check:

- no lowercase `git ls-files -v` flags before validation
- no lowercase `git ls-files -v` flags after validation

### 6. No Polling Guardian Workaround

The harness must reject guardian/polling/thread workarounds designed to mask evidence mutation.

Forbidden terms in smoke scripts include:

- `EvidenceGuardian`
- `_EvidenceGuardian`
- `guardian`
- `threading`
- polling to rewrite prior evidence while another smoke runs

### 7. No Prior Evidence Mutation

The harness must guard historical evidence prefixes:

- `docs/evidence/ps-019/`
- `docs/evidence/ps-020/`
- `docs/evidence/ps-021/`
- `docs/evidence/ps-024/`
- `docs/evidence/ps-025/`
- `docs/evidence/ps-026/`
- `docs/evidence/ps-027/`
- `docs/evidence/ps-028/`
- `docs/evidence/ps-029/`
- `docs/evidence/ps-030/`
- `docs/evidence/ps-031/`
- `docs/evidence/ps-032/`
- `docs/evidence/ps-033/`
- `docs/evidence/ps-034/`

### 8. Contract-Based Historical Regression

For accepted historical slices, the central gate should verify contracts instead of re-running recursive historical smokes.

Contracts should include:

- evidence file exists
- evidence JSON has `ok: true` when available
- key smoke fields are pass/true where available
- golden constants match the canonical golden run where applicable
- expected routes still exist
- expected source files still exist

### 9. Explicit Known Limitation

The docs must honestly say:

Contract-based regression confirms accepted evidence and current route/file presence.

It does not prove every old smoke script would re-run today.

That full retrofit belongs to PS-034B.

## Required Shared Library

Create `scripts/smoke_lib.py`.

It should include reusable helpers, such as:

- `repo_root()`
- `read_text(path)`
- `read_json(path)`
- `write_json_atomic(path, data)`
- `run_command(command, cwd=None, timeout=None)`
- `git_status_short()`
- `assert_no_staged_changes()`
- `assert_no_hidden_git_flags()`
- `assert_status_only(expected_modified, expected_untracked)`
- `assert_no_paths_changed(prefixes)`
- `assert_no_forbidden_terms(paths, terms)`
- `assert_no_secret_like_patterns(paths)`
- `assert_frontend_typecheck_build_once()`
- `assert_route_registered(app_tsx, route)`
- `assert_file_exists(path)`
- `assert_evidence_contract(path, required_constants=None)`
- `sha256_bytes(data)`

Implementation may adjust helper names, but the library must centralize the repeated validation logic.

## Required Regression Gate

Create `scripts/proofstudio_regression_gate.py`.

It must be non-recursive.

Minimum supported usage:

- `python scripts/proofstudio_regression_gate.py --current ps034a`
- `python scripts/proofstudio_regression_gate.py --current ps034 --no-frontend`
- `python scripts/proofstudio_regression_gate.py --current ps034 --frontend`

The gate must:

1. Verify repo root.
2. Verify no staged changes.
3. Verify no hidden Git flags before validation.
4. Reject Git hiding terms and guardian workaround terms in smoke scripts.
5. Verify prior evidence is not modified.
6. Verify historical accepted contracts PS-023 through PS-034.
7. Verify golden constants against canonical evidence where applicable.
8. Verify required route/file contracts for product surfaces.
9. Optionally run frontend typecheck/build once.
10. Verify no hidden Git flags after validation.
11. Write a report JSON for PS-034A.
12. Exit nonzero on any failure.

The gate must not:

- call feature smokes recursively
- call providers
- read arbitrary B2
- mutate prior evidence
- hide files through Git index flags

## Required Documentation

Create `docs/validation/proofstudio-smoke-harness-v1.md`.

It must include:

- problem statement
- root cause from PS-034 recursive smoke failure
- new validation architecture
- slice-local smoke rules
- central regression gate rules
- evidence ownership rules
- frontend build once rule
- forbidden workaround list
- historical contract validation explanation
- PS-034B retrofit plan
- rules for all future slices PS-035 onward
- example commands

Required exact lines:

`Feature slice smokes validate the slice. The regression gate validates the release.`

`No feature smoke may recursively execute another feature smoke.`

`No smoke may hide evidence changes with Git index flags.`

`A slice smoke may write only its own evidence file.`

`Frontend typecheck and build run once at the top-level gate.`

`Historical smoke local-mode retrofit is deferred to PS-034B.`

## Required PS-034A Proof Doc

Create `docs/ps-034a-smoke-harness-v1-proof.md`.

It must include:

- why PS-034A exists
- root cause summary
- files changed
- validation policy locked
- smoke library summary
- regression gate summary
- no recursive smoke confirmation
- no Git hiding confirmation
- no guardian/polling workaround confirmation
- no prior evidence mutation confirmation
- frontend build once policy
- PS-034B cleanup plan
- validation commands
- limitations

## Required PS-034A Evidence

Create `docs/evidence/ps-034a/smoke-harness-v1-report.json`.

It must include:

- ok
- harness_id
- harness_version
- current_slice
- non_recursive_gate
- smoke_lib_created
- regression_gate_created
- validation_doc_created
- proof_doc_created
- no_recursive_smoke_policy
- no_git_hiding_policy
- no_guardian_workaround_policy
- evidence_ownership_policy
- frontend_once_policy
- historical_contracts_verified
- prior_evidence_clean
- no_hidden_git_flags_before
- no_hidden_git_flags_after
- no_provider_call
- no_broad_b2_read
- ps034b_retrofit_deferred
- checked_at

## Required PS-034A Smoke

If creating `scripts/ps034a_smoke_harness_v1_smoke.py`, it must verify:

1. `scripts/smoke_lib.py` exists.
2. `scripts/proofstudio_regression_gate.py` exists.
3. validation doc exists.
4. proof doc exists.
5. evidence report exists.
6. regression gate contains no recursive feature smoke execution.
7. smoke scripts/docs contain no Git hiding terms.
8. smoke scripts/docs contain no guardian workaround terms.
9. validation doc includes required exact lines.
10. proof doc includes PS-034B retrofit plan.
11. evidence report has `ok: true`.
12. regression gate can run with `--current ps034a --no-frontend`.
13. frontend typecheck/build can run once from the gate when requested.
14. no prior evidence is modified.
15. no hidden Git flags before/after.
16. no provider/backend/deployment files changed.

## Expected Allowed Files

PS-034A implementation should normally touch only:

- `scripts/smoke_lib.py`
- `scripts/proofstudio_regression_gate.py`
- optional `scripts/ps034a_smoke_harness_v1_smoke.py`
- `docs/validation/proofstudio-smoke-harness-v1.md`
- `docs/evidence/ps-034a/smoke-harness-v1-report.json`
- `docs/ps-034a-smoke-harness-v1-proof.md`
- `specs/44-ps-034a-smoke-harness-v1.md`

Do not modify product UI files.

Do not modify historical evidence.

Do not modify historical smokes.

Do not modify provider/backend/deployment files.

## Acceptance Criteria

PS-034A is accepted only when:

- smoke library exists
- central regression gate exists
- validation policy doc exists
- proof doc exists
- evidence report exists
- no recursive smoke execution is introduced
- no Git hiding workaround is present
- no guardian/polling workaround is present
- prior evidence remains clean
- hidden Git flags are absent before and after validation
- regression gate verifies PS-023 through PS-034 contracts non-recursively
- frontend build/typecheck is run once only when requested
- PS-034B retrofit plan is documented
- final git status contains only expected PS-034A files

## Failure Conditions

Reject PS-034A if it:

- recursively executes historical feature smokes
- uses Git index hiding flags
- uses polling guardian workaround
- mutates prior-slice evidence
- rewrites PS-023 through PS-034 historical smokes
- modifies product UI
- modifies provider/backend/deployment files
- calls providers
- reads arbitrary B2
- runs repeated nested frontend builds
- omits PS-034B retrofit plan

## Future Required Work

After PS-034A is accepted, create:

- PS-034B — Historical Smoke Local-Mode Retrofit

PS-034B will carefully retrofit PS-023 through PS-033 smokes to support local/contract/no-frontend modes.

Only after PS-034A and PS-034B are accepted should PS-035 begin.

## Next Product Slice After Validation Hardening

After validation hardening:

- PS-035 — Review + Approval Workspace
