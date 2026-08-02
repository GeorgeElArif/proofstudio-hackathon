# PS-034B — Historical Smoke Local-Mode Retrofit

Status: Spec only.
Base branch: `ps-034a/smoke-harness-v1`
Date: 2026-07-01

## 1. Status

PS-034B is currently:

- Spec only.
- Implementation pending.

PS-034B must not be implemented until this spec is accepted.

PS-034B depends on PS-034A being accepted. PS-034A created the central validation
harness (`scripts/smoke_lib.py`, `scripts/proofstudio_regression_gate.py`, the
validation doc, and the PS-034A evidence report). PS-034B does not modify that
architecture; it makes historical smokes safe to run directly alongside it.

## 2. Purpose

PS-034A created the central validation harness. PS-034B retrofits the historical
feature smoke scripts (PS-023 through PS-034) so that direct historical smoke
execution cannot reintroduce:

- recursion across the feature-smoke chain
- nested frontend builds
- prior-evidence mutation or snapshot/restore hacks
- self-unlink of evidence files
- Git index hiding flags
- prior-evidence rewrites by default

PS-034B is a surgical retrofit of historical smoke scripts only.

It makes the historical smokes safe to run directly without damaging the
PS-034A validation architecture.

Important: PS-034B does not weaken the PS-034A gate, does not mutate PS-034A
evidence, and does not rewrite PS-034A required validation lines.

The exact PS-034A validation-doc sentence:

```
Historical smoke local-mode retrofit is deferred to PS-034B.
```

must remain untouched, because PS-034A smoke still requires it. PS-034B may
later append a separate completion note saying the retrofit has now been
completed, but that exact sentence must remain verbatim in
`docs/validation/proofstudio-smoke-harness-v1.md`.

## 3. Root Cause

Historical smoke scripts were written before the PS-034A validation policy.

Known source-audit findings across PS-023 through PS-034:

- PS-025 through PS-033 recursively execute prior smoke scripts. Each smoke
  launches the previous slice's smoke, forming a deep recursion chain that
  multiplies runtime and obscures failures.
- PS-026 through PS-034 run nested frontend typecheck/build. Running the
  frontend toolchain inside a feature smoke means a single regression run can
  execute `tsc`/`vite build` multiple times and time out.
- PS-028 through PS-033 contain forbidden Git hiding/index manipulation
  patterns (e.g. `assume-unchanged`, `skip-worktree`, `update-index`).
- Several historical smokes mutate prior-slice evidence by snapshotting the
  file, overwriting it during the run, and restoring it afterward.
- Several historical smokes self-unlink their own evidence file before
  rewriting it, which leaves the repo in a dirty or inconsistent state if a
  run fails midway.
- Historical smokes do not use `scripts/smoke_lib.py`. They duplicate
  validation logic per script, which is why the dangerous patterns kept
  recurring.
- No historical smoke currently has a safe local/check-only mode. Running any
  of them directly today triggers the full recursion + frontend build chain.
- PS-023 and PS-024 are mostly safe but still lack parity local/check flags.
- PS-034 is already non-recursive but still runs direct frontend
  build/typecheck.
- Feature smoke responsibilities are mixed with release regression
  responsibilities: a feature smoke should validate its own slice, while
  cross-slice release regression belongs only to the central gate.

Root-cause summary: the historical smokes combined feature-slice validation,
release regression, evidence rewriting, and frontend building into a single
recursively chained script with no safe local mode.

## 4. Scope

PS-034B scope is historical smoke scripts PS-023 through PS-034 only.

In scope:

- retrofit of `scripts/ps023_*_smoke.py` through `scripts/ps034_*_smoke.py`
- the new PS-034B smoke script
- the PS-034B evidence report
- the PS-034B proof doc
- an additive helper in `scripts/smoke_lib.py` only if strictly necessary
- an appended completion note in the validation doc (without removing the
  required PS-034A exact sentence)
- this spec

Out of scope: everything else, including the central regression gate, product
UI, backend, provider code, deployment config, roadmap, and master spec.

## 5. Non-goals

PS-034B must not:

- do not modify product UI
- do not modify backend/provider/deployment code
- do not modify roadmap/master spec
- do not implement PS-034C
- do not run live providers
- do not read arbitrary B2
- do not rewrite historical evidence by default
- do not delete or rewrite the PS-034A required validation sentence:
  `Historical smoke local-mode retrofit is deferred to PS-034B.`
- do not weaken the central regression gate
- do not modify the PS-034A smoke script
- do not modify PS-034A evidence
- do not require running
  `scripts/proofstudio_regression_gate.py --current ps034b`
  unless the gate is safely updated in a later PM-approved slice; the current
  PS-034A gate writes to the PS-034A report path, so running it for PS-034B
  can mutate PS-034A evidence. For this spec, require the central gate to be
  validated only in its existing PS-034A-safe mode, or require no
  central-gate mutation.

## 6. Allowed files for implementation

PS-034B implementation may touch only:

- `scripts/ps023_judge_cockpit_home_smoke.py`
- `scripts/ps024_golden_demo_run_pinning_smoke.py`
- `scripts/ps025_public_durable_passport_unlock_smoke.py`
- `scripts/ps026_b2_evidence_explorer_smoke.py`
- `scripts/ps027_genblaze_pipeline_graph_smoke.py`
- `scripts/ps028_manifest_verification_panel_smoke.py`
- `scripts/ps029_b2_rehydrate_comparison_smoke.py`
- `scripts/ps030_failure_as_proof_timeline_smoke.py`
- `scripts/ps031_export_campaign_pack_v2_smoke.py`
- `scripts/ps032_operations_cockpit_flight_recorder_smoke.py`
- `scripts/ps033_provider_decision_intelligence_smoke.py`
- `scripts/ps034_lineage_comparison_lab_smoke.py`
- `scripts/smoke_lib.py` only if an additive helper is truly needed
- `scripts/ps034b_historical_smoke_local_mode_retrofit_smoke.py`
- `docs/evidence/ps-034b/historical-smoke-local-mode-retrofit-report.json`
- `docs/ps-034b-historical-smoke-local-mode-retrofit-proof.md`
- `docs/validation/proofstudio-smoke-harness-v1.md` only to append a
  completion note, not to remove PS-034A exact required lines
- `specs/45-ps-034b-historical-smoke-local-mode-retrofit.md`

No other files may be modified.

## 7. Forbidden files

PS-034B must not touch:

- `apps/web/**`
- `src/**`
- `workers/**`
- `packages/**`
- `render.yaml`
- `.env*`
- scripts/proofstudio_regression_gate.py unless a later PM prompt explicitly authorizes it (it currently writes to the PS-034A report path, so running it for PS-034B can mutate PS-034A evidence)
- `scripts/ps034a_smoke_harness_v1_smoke.py`
- `docs/evidence/ps-034a/**`
- `docs/evidence/ps-025/**` through `docs/evidence/ps-034/**` unless an
  explicit write-evidence mode is separately approved
- `docs/roadmap/**`
- master spec / roadmap docs

## 8. Required changes

Each retrofitted historical smoke (PS-023 through PS-034) must:

- accept `--local`
- accept `--check-only` or an equivalent no-evidence mode
- default to safe local behavior when invoked without flags
- never execute another feature smoke (no recursion into another
  `scripts/ps0*_smoke.py`)
- never run `npm`, `typecheck`, or `build` directly
- never use Git index hiding flags (`assume-unchanged`,
  `skip-worktree`, `update-index`, `git update-index`)
- never snapshot/restore prior evidence
- never self-unlink its own evidence file
- never mutate prior evidence
- not write historical evidence by default in local/check mode
- use `scripts/smoke_lib.py` policy checks where practical
- keep its own-slice contract semantics intact (golden constants,
  expected routes, expected source files, evidence field shape)

### PS-025 specifics

PS-025 must:

- keep any optional live URL/network path behind an explicit `--live` flag
- never run that live/network path by default
- in local/check mode, validate contracts only, without network calls

### PS-034 specifics

PS-034 must:

- remove direct frontend build/typecheck behavior
- stay non-recursive (it is already non-recursive today)
- keep its lineage-comparison-lab contract checks intact

### smoke_lib additions

If a shared helper is genuinely needed across the retrofitted smokes (for
example a `run_local_check_mode` or `assert_no_frontend_build_invocation`
helper), it must be added additively to `scripts/smoke_lib.py` without
removing or altering any existing PS-034A helper or behavior.

### Validation doc note

`docs/validation/proofstudio-smoke-harness-v1.md` may only be edited to
append a completion note such as:

```
Historical smoke local-mode retrofit is now complete as of PS-034B.
```

The existing PS-034A required line must remain untouched:

```
Historical smoke local-mode retrofit is deferred to PS-034B.
```

No other line in that doc may be removed.

## 9. Evidence model

PS-034B should produce only its own report:

```
docs/evidence/ps-034b/historical-smoke-local-mode-retrofit-report.json
```

Historical local/check mode must not rewrite historical evidence unless an
explicit write-evidence flag is used. By default, the retrofitted smokes must
not write to `docs/evidence/ps-025/**` through `docs/evidence/ps-034/**`.

The PS-034B report fields must include:

- `ok`
- `slice_id`: `ps034b`
- `retrofit_scope`
- `retrofitted_smokes`
- `non_recursive`
- `no_nested_frontend_builds`
- `no_git_hiding`
- `no_prior_evidence_mutation`
- `no_historical_evidence_rewrite_by_default`
- `no_provider_call`
- `no_broad_b2_read`
- `smoke_lib_policy_checks`
- `ps034a_required_lines_preserved`
- `ps034a_smoke_still_passes`
- `checked_at`
- `failures`

The report must record each retrofitted smoke and whether it passed local /
check mode without recursion, frontend builds, Git hiding, or evidence
mutation.

## 10. Required validation commands

The PS-034B implementation must be validated with:

1. Python syntax compile of all changed scripts, e.g.:
   ```
   python -m py_compile scripts/ps023_*.py ... scripts/ps034b_*.py
   ```
2. AST-based no-recursive-smoke check over PS-023 through PS-034 (no script
   may subprocess-invoke or import another `ps0*_smoke` module).
3. Static no npm/typecheck/build command check over PS-023 through PS-034
   (forbidden terms: `npm`, `vite build`, `tsc`, `pnpm`, `yarn`).
4. Static no Git hiding term check over PS-023 through PS-034
   (forbidden terms: `assume-unchanged`, `skip-worktree`, `update-index`).
5. Static no snapshot/restore/self-unlink check over PS-023 through PS-034
   (forbidden terms: snapshot/restore pairs, `os.unlink`, `os.remove` on an
   evidence path, `Path(...).unlink()` on an evidence path).
6. Run each retrofitted smoke in safe local/check mode, e.g.:
   ```
   python scripts/ps023_judge_cockpit_home_smoke.py --local --check-only
   ... through ...
   python scripts/ps034_lineage_comparison_lab_smoke.py --local --check-only
   ```
7. Run the PS-034B smoke:
   ```
   python scripts/ps034b_historical_smoke_local_mode_retrofit_smoke.py
   ```
8. Run the PS-034A smoke to prove the PS-034A architecture still passes:
   ```
   python scripts/ps034a_smoke_harness_v1_smoke.py
   ```
   This must not mutate PS-034A evidence. The central regression gate, if
   invoked at all, must be invoked only in its existing PS-034A-safe mode
   (e.g. `--current ps034a --no-frontend`). Do not run
   `scripts/proofstudio_regression_gate.py --current ps034b` unless the
   gate is safely updated in a later PM-approved slice.
9. Verify no hidden Git flags before and after validation:
   ```
   git ls-files -v | grep -E '^[a-z]'
   ```
   must return nothing both before and after.
10. Verify the final git status contains only allowed PS-034B files (see
    section 6). No product, backend, provider, deployment, roadmap, master
    spec, or prior-evidence file may appear in the diff.

## 11. Acceptance criteria

PS-034B is accepted only when:

- PS-034B spec exists (this document, accepted).
- All retrofitted historical smokes PS-023 through PS-034 pass in
  local/check mode.
- No recursive smoke execution remains in PS-023 through PS-034.
- No direct frontend build/typecheck command remains in PS-023 through
  PS-034.
- No Git hiding terms remain in PS-023 through PS-034.
- No snapshot/restore/self-unlink evidence hacks remain in PS-023 through
  PS-034.
- No prior evidence is dirty after validation
  (`docs/evidence/ps-025/**` through `docs/evidence/ps-034/**` unchanged
  by default).
- PS-034A smoke still passes.
- The PS-034A required validation line
  `Historical smoke local-mode retrofit is deferred to PS-034B.`
  remains present in `docs/validation/proofstudio-smoke-harness-v1.md`.
- PS-034B evidence report `ok: true`.
- No product files changed.
- Clean commit and push are required before acceptance.

## 12. Rollback

Rollback of PS-034B is a single revert of the PS-034B implementation commit.

Rollback must:

- leave the PS-034A accepted commit fully intact
- restore the historical smokes to their pre-PS-034B behavior (the
  pre-PS-034B state was unsafe to run directly, but it is the known
  baseline and does not break the central regression gate)
- not require any change to the central regression gate
- not require any change to PS-034A evidence

Because PS-034B only retrofits historical smoke scripts and does not touch
product, backend, provider, deployment, roadmap, master spec, or PS-034A
files, rollback is low-risk and isolated.

## 13. Roadmap gate

- PS-034C remains blocked until PS-034B accepted.
- PS-035 remains blocked until PS-034B and PS-034C accepted.

PS-034B does not create PS-034C and does not begin PS-035.
