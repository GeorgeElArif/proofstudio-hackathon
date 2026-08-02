# PS-034B — Historical Smoke Local-Mode Retrofit (Proof)

Status: Implemented
Date: 2026-07-01
Base branch: `ps-034a/smoke-harness-v1`
Spec: `specs/45-ps-034b-historical-smoke-local-mode-retrofit.md`

## Why PS-034B Exists

PS-034A created the central validation harness (`scripts/smoke_lib.py`,
`scripts/proofstudio_regression_gate.py`, the validation doc, and the
PS-034A evidence report). However, the historical feature-slice smoke scripts
(PS-023 through PS-034) were written before the PS-034A validation policy and
contained dangerous patterns that made them unsafe to run directly:

- **Recursive smoke execution**: PS-025 through PS-033 each launched prior
  slice smokes as subprocesses, forming a deep recursion chain that multiplied
  runtime and obscured failures.
- **Nested frontend builds**: PS-026 through PS-034 ran `npm run typecheck`
  and `npm run build` inside each feature smoke, so a single regression run
  could execute the frontend toolchain many times and time out.
- **Prior-evidence snapshot/restore hacks**: PS-026 through PS-033 snapshot-
  restored prior-slice evidence bytes around regression runs, masking real
  evidence mutation.
- **Self-unlink of evidence**: PS-027 through PS-033 unlinked their own tracked
  evidence file before rewriting it, leaving the repo dirty if a run failed.
- **Git index hiding**: PS-028 through PS-033 used `git update-index
  --assume-unchanged` to hide deletions from downstream smokes.
- **No safe local/check mode**: Running any historical smoke directly
  triggered the full recursion + frontend build chain.

PS-034B retrofits every historical smoke so it can run safely in local /
check-only mode without damaging the PS-034A validation architecture.

## How PS-034B Sweeps the Historical Smokes

PS-034B performs a controlled local-mode sweep of retrofitted historical
smokes. It does not reintroduce the old recursive smoke chain because the
historical smokes no longer execute each other: every `run_subprocess_smoke`
call site was removed (verified by AST-based
`assert_no_recursive_smoke_execution`). The PS-034B smoke runs each
historical smoke as a subprocess in `--local --check-only` mode (the safe
default), then verifies the working tree is left clean.

## How Provider / Network Proof Is Computed

`no_provider_call` is no longer hardcoded. It is produced by
`check_no_provider_call_paths`, which walks the parsed AST of every
retrofitted historical smoke (PS-023 through PS-034) and flags any real
`Call` node that invokes a network/provider primitive (`urlopen`, `Request`,
`requests.*`, `httpx.*`, `call_provider`, `fetchFromProvider`). Static
scan-string pattern lists such as `PROVIDER_CALL_PATTERNS` are plain string
constants, not `Call` nodes, so they are never flagged.

The single allowed exception is the PS-025 passport smoke, which may use
`urlopen` / `Request` only inside its explicitly gated `--live` branch. The
PS-034B smoke verifies all of the following before allowing it:

- the file is `ps025_public_durable_passport_unlock_smoke.py`;
- it parses its CLI with `parse_slice_smoke_cli(..., allow_live=True)`;
- it calls `_get_passport_json(..., live=opts.live)`;
- every `urlopen` / `Request` call is nested inside an `if live:` guard;
- default local / check runs pass without `--live` (proven by
  `check_each_smoke_local_mode`, which runs PS-025 in `--local --check-only`).

No other historical smoke may contain any executable provider/network call.

## How Broad-B2 Proof Is Computed

`no_broad_b2_read` is no longer hardcoded. It is produced by
`check_no_broad_b2_read_paths`, which walks the parsed AST of every
retrofitted historical smoke and flags any real `Call` node that invokes a B2
access primitive (`boto3.client`, `boto3.resource`, `.get_object`,
`.list_objects`, `.list_objects_v2`, `.download_fileobj`, `.head_object`,
`read_archive_from_b2`, `fetchB2Object`, `list_b2_objects`). Static
scan-string pattern lists such as `BROAD_B2_READ_PATTERNS` (which police the
product frontend) are plain string constants, not `Call` nodes, so they are
never flagged.

## Root Causes Fixed

1. **Recursion**: Removed all `run_subprocess_smoke` functions and their call
   sites from PS-025 through PS-033. No historical smoke now subprocess-invokes
   another feature smoke. Verified by AST-based
   `assert_no_recursive_smoke_execution`.

2. **Nested frontend builds**: Removed all direct `run_npm` functions and calls
   from PS-026 through PS-034. The frontend typecheck/build now belongs only to
   the central regression gate (`--frontend` flag). Static check confirms no
   `npm run`, `typecheck`, `vite build`, `pnpm`, `yarn`, or `tsc --noEmit`
   references remain in any historical smoke.

3. **Git index hiding**: Removed all `_set_assume_unchanged` functions,
   `TRACKED_UNLINK_PRONE_EVIDENCE` constants, and any `assume-unchanged` /
   `skip-worktree` / `update-index` references from PS-028 through PS-033.
   Static check confirms none of these terms remain.

4. **Prior-evidence snapshot/restore**: Removed all `_snapshot_evidence` and
   `_restore_evidence` functions from PS-026 through PS-033. Prior evidence is
   no longer mutated or restored during local/check mode runs.

5. **Self-unlink**: Removed all `EVIDENCE_OUT.unlink()` calls from PS-027
   through PS-033. Evidence is now written atomically via
   `sl.write_json_atomic` only when `--write-evidence` is passed.

6. **No safe local mode**: Added `--local`, `--check-only`, and
   `--write-evidence` CLI flags to every historical smoke (PS-023 through
   PS-034). The default behavior is now safe local / check-only mode.

7. **PS-025 live URL**: The optional live/network URL path is now gated behind
   an explicit `--live` flag. It is never used by default.

8. **PS-034 frontend build**: Removed the direct `run_npm("typecheck")` and
   `run_npm("build")` calls. PS-034 stays non-recursive (it already used a
   contract-table approach, not smoke execution).

## Files Changed

- `scripts/smoke_lib.py` — added `parse_slice_smoke_cli` and
  `run_contract_checks` helpers (additive only; no existing helper altered).
- `scripts/ps023_judge_cockpit_home_smoke.py` — CLI flags, scrubbed literal.
- `scripts/ps024_golden_demo_run_pinning_smoke.py` — CLI flags.
- `scripts/ps025_public_durable_passport_unlock_smoke.py` — removed recursion,
  live behind `--live`, CLI flags.
- `scripts/ps026_b2_evidence_explorer_smoke.py` — removed recursion, frontend
  builds, snapshot/restore, CLI flags.
- `scripts/ps027_genblaze_pipeline_graph_smoke.py` — same + removed self-unlink.
- `scripts/ps028_manifest_verification_panel_smoke.py` — same + removed Git
  hiding.
- `scripts/ps029_b2_rehydrate_comparison_smoke.py` — same.
- `scripts/ps030_failure_as_proof_timeline_smoke.py` — same.
- `scripts/ps031_export_campaign_pack_v2_smoke.py` — same.
- `scripts/ps032_operations_cockpit_flight_recorder_smoke.py` — same.
- `scripts/ps033_provider_decision_intelligence_smoke.py` — same.
- `scripts/ps034_lineage_comparison_lab_smoke.py` — removed frontend
  typecheck/build, CLI flags.
- `scripts/ps034b_historical_smoke_local_mode_retrofit_smoke.py` — new.
- `docs/evidence/ps-034b/historical-smoke-local-mode-retrofit-report.json` — new.
- `docs/validation/proofstudio-smoke-harness-v1.md` — appended PS-034B
  completion note.

## How Recursion Was Removed

Every `run_subprocess_smoke` function and all its call sites were deleted from
PS-025 through PS-033. Each smoke now validates only its own slice contracts
(routes, golden constants, truth boundary, forbidden claims, secret scan,
broad-B2-read patterns, provider-call patterns). Cross-slice regression
belongs only to the central gate. The AST-based
`assert_no_recursive_smoke_execution` check confirms no subprocess call in any
historical smoke targets a `ps0...smoke.py` script.

## How Nested Frontend Builds Were Removed

Every `run_npm` function and all its call sites were deleted from PS-026
through PS-034. The `frontend_typecheck` and `frontend_build` check entries
were removed from the downstream check lists. The frontend toolchain now runs
only once at the central gate level via
`assert_frontend_typecheck_build_once()`. A static regex check confirms no
`npm run`, `typecheck`, `vite build`, `pnpm`, `yarn`, or `tsc --noEmit`
reference remains.

## How Git Hiding Was Removed

Every `_set_assume_unchanged` function, `TRACKED_UNLINK_PRONE_EVIDENCE`
constant, and all references to `assume-unchanged`, `skip-worktree`, and
`update-index` were deleted from PS-028 through PS-033. The
`git ls-files -v` verification (no lowercase tag flags) is checked before and
after every PS-034B validation run.

## Why Historical Evidence Is Not Rewritten by Default

Each retrofitted smoke defaults to `--check-only` mode, which does not write
any evidence file. Evidence is written only when `--write-evidence` is
explicitly passed. The PS-034B smoke verifies that running every historical
smoke in `--local --check-only` mode leaves no prior-slice evidence file dirty
(`docs/evidence/ps-025/` through `docs/evidence/ps-034/`).

## PS-034A Required-Line Preservation

The exact PS-034A validation-doc sentence:

```
Historical smoke local-mode retrofit is deferred to PS-034B.
```

remains verbatim in `docs/validation/proofstudio-smoke-harness-v1.md`.
PS-034B appends a separate completion note:

```
Historical smoke local-mode retrofit is now complete as of PS-034B.
```

without removing or altering the required PS-034A line.

## Validation Commands

```bash
# 1. Syntax compile
python -m py_compile scripts/ps023_*.py ... scripts/ps034b_*.py

# 2. AST no-recursive-smoke check
python scripts/ps034b_historical_smoke_local_mode_retrofit_smoke.py

# 3. PS-034A smoke still passes
python scripts/ps034a_smoke_harness_v1_smoke.py

# 4. No hidden Git flags
git ls-files -v | awk '$1 ~ /^[a-z]/ {print}'

# 5. Run each historical smoke in safe mode
python scripts/ps023_judge_cockpit_home_smoke.py --local --check-only
... through ...
python scripts/ps034_lineage_comparison_lab_smoke.py --local --check-only
```

## Limitations

- PS-034B does not implement PS-034C or PS-035.
- PS-034B does not modify the central regression gate
  (`scripts/proofstudio_regression_gate.py`).
- The `--write-evidence` mode writes only the smoke's own evidence file; it
  does not rewrite prior-slice evidence.
- The PS-025 `--live` flag requires a configured `PROOFSTUDIO_PS025_API_BASE_URL`
  environment variable and is never used by default.

## Why PS-034C and PS-035 Remain Blocked

Per the spec roadmap gate:

- PS-034C remains blocked until PS-034B is accepted.
- PS-035 remains blocked until PS-034B and PS-034C are accepted.

PS-034B does not create PS-034C and does not begin PS-035.
