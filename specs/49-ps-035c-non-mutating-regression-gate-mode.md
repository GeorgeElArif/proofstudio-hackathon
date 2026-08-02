# PS-035C — Non-Mutating Regression Gate Mode

Status: Spec only.
Base branch: `ps-035c/non-mutating-regression-gate-mode`
Base commit: `f5a659a29908277dacb5f80f5e9d6e6c861c2e38` (accepted PS-035b)
Date: 2026-07-01

This spec-only commit touches only one file:
`specs/49-ps-035c-non-mutating-regression-gate-mode.md`. No implementation
files, no scripts, no smoke scripts, no `smoke_lib`, no evidence, no proof docs,
no env files, and no requirements are changed or performed during this phase.
No provider is called, no B2 is read, and no B2 is written during this phase.

PS-035C is a validation-harness slice, not a product slice. It fixes a
validation-harness root-cause bug. It is not a PS-035b product bug and it is not
a regression in any product behavior.

## 1. Status

PS-035C is currently:

- Spec only.
- Implementation pending.

PS-035C must not be implemented, and no implementation files may be changed,
until this spec is accepted. The latest accepted slice is PS-035b commit
`f5a659a`.

PS-035C is the next blocking validation-harness slice after PS-035b. It exists
to stop the central regression gate from mutating tracked historical PS-034A
evidence during normal future-slice validation. This spec-only phase writes only
this file. PS-035C must not call live providers, must not read or write live B2,
must not call any provider, must not mutate
`docs/evidence/ps-034a/smoke-harness-v1-report.json`, and must not print secrets.

## 2. Purpose

PS-035C introduces a non-mutating regression gate mode. The central regression
gate (`scripts/proofstudio_regression_gate.py`) must be able to validate all
historical contracts and print the same pass/fail summary without writing the
tracked PS-034A historical evidence file
`docs/evidence/ps-034a/smoke-harness-v1-report.json`.

Today the central gate always writes to that one hardcoded tracked path, so
running the gate for any later slice (for example
`python scripts/proofstudio_regression_gate.py --current ps035b --no-frontend`)
mutates tracked historical PS-034A evidence. That forced PS-035b validation to
manually restore the file after the central gate ran. This is a
validation-harness root-cause bug, not a product behavior bug, and not a
PS-035b product bug.

PS-035C closes that gap by defining:

- a non-mutating regression gate contract (the gate must not mutate tracked
  historical PS-034A evidence during normal future-slice validation);
- a CLI contract with future-safe modes: `--check-only` (no report file is
  written), `--report-out <path>` (write only to an explicitly supplied path),
  and `--write-report` (required for writing the canonical tracked PS-034A
  report);
- an explicit default-behavior decision: default to check-only for non-PS034A
  current slices, while preserving a clear explicit write path for PS-034A
  harness evidence regeneration;
- a PS-034A historical evidence protection contract (the canonical tracked
  report may only be written under explicit, PM-aware regeneration, never as a
  side effect of validating a later slice); and
- a local/static smoke validation model that proves the gate leaves `git status`
  clean and leaves the PS-034A report digest unchanged in check-only mode,
  without ever calling a provider or touching live B2.

After PS-035C, future slices must be able to run the central regression gate as
part of their validation without manually restoring the PS-034A evidence
afterward.

## 3. Root Cause

The central regression gate has a hardcoded tracked report path. In
`scripts/proofstudio_regression_gate.py`:

- line 48: `REPORT_PATH = EVIDENCE / "ps-034a" / "smoke-harness-v1-report.json"`
- lines 300-301: `write_report(report)` always writes to that path via
  `sl.write_json_atomic(REPORT_PATH, report)`
- line 398: `run_gate` calls `write_report(report)` unconditionally before
  returning

Because the report path is hardcoded to the tracked PS-034A historical evidence
file and the write is unconditional, running the central gate for any later
slice (for example
`python scripts/proofstudio_regression_gate.py --current ps035b --no-frontend`)
overwrites `docs/evidence/ps-034a/smoke-harness-v1-report.json` with a report
whose `current_slice`, `checked_at`, and other fields reflect the later slice,
not the historical PS-034A run. That mutates tracked historical evidence as a
side effect of validating a future slice.

This forced PS-035b validation to manually restore
`docs/evidence/ps-034a/smoke-harness-v1-report.json` after the central gate ran.
The manual restore is a workaround, not a fix. The fix is to make the central
gate non-mutating by default for non-PS034A slices.

This is a validation-harness root-cause bug. It is not a PS-035b product bug, it
is not a regression in product behavior, and it is not a security bug in the
product. It is a defect in the validation harness that owns the central gate.

## 4. Current Discovery Facts

Central regression gate state
(`scripts/proofstudio_regression_gate.py`, at base commit `f5a659a`):

- `REPORT_PATH` is hardcoded at line 48 to
  `EVIDENCE / "ps-034a" / "smoke-harness-v1-report.json"`, which resolves to
  `docs/evidence/ps-034a/smoke-harness-v1-report.json`.
- `write_report(report)` (lines 300-301) always calls
  `sl.write_json_atomic(REPORT_PATH, report)` to that one path.
- `run_gate(current_slice, frontend)` (line 314) calls `write_report(report)`
  unconditionally at line 398 before returning, regardless of `current_slice`.
- The CLI (`main`, lines 416-436) currently supports only `--current`,
  `--frontend`, and `--no-frontend`. There is no `--check-only`, no
  `--report-out`, and no `--write-report` flag today.
- The default frontend behavior is `frontend=False` (line 431
  `parser.set_defaults(frontend=False)`). Frontend is opt-in, not default.

`smoke_lib` state (`scripts/smoke_lib.py`):

- `write_json_atomic(path, data)` exists (line 95) and is reusable for any path.
  It is not constrained to the PS-034A report path.

PS-034A historical evidence state:

- `docs/evidence/ps-034a/smoke-harness-v1-report.json` exists and is tracked.
- It is referenced as `REPORT_PATH` in the central gate.
- It is not in the `PRIOR_EVIDENCE_PREFIXES` list (lines 50-56) of the gate
  itself; the prefix list covers `ps-019`..`ps-034`, `ps-035a`, and `demo`, but
  not `ps-034a`. The gate therefore does not currently self-assert that its own
  output path is unchanged, because the gate is the writer.

PS-035b validation experience (the trigger for this slice):

- Running `python scripts/proofstudio_regression_gate.py --current ps035b
  --no-frontend` overwrote
  `docs/evidence/ps-034a/smoke-harness-v1-report.json` with a PS-035b-tagged
  report.
- PS-035b validation had to manually restore
  `docs/evidence/ps-034a/smoke-harness-v1-report.json` afterward for `git status`
  to be clean.

CLI / contract state:

- There is no check-only mode today.
- There is no explicit report-out path today.
- There is no explicit write-report flag today.
- The canonical tracked PS-034A report can be regenerated by anyone who runs
  the gate with `--current ps034a`, but today that is the only way to make the
  gate not lie about `current_slice`, and it still mutates the file as a side
  effect of every other invocation.

This is a validation-harness root-cause bug, not a product bug, and not a
PS-035b product bug.

## 5. Scope

PS-035C is a validation-harness slice. It makes the central regression gate
non-mutating by default for non-PS034A slices and adds explicit, future-safe
write paths. It is local/static-only and must not touch the network for
providers or B2.

PS-035C must:

1. Make the central regression gate non-mutating during normal future-slice
   validation. Running the gate for a non-PS034A current slice must not write
   `docs/evidence/ps-034a/smoke-harness-v1-report.json`.
2. Add a check-only mode (`--check-only`) that validates all historical
   contracts and prints the same pass/fail summary without writing any report
   file.
3. Add an explicit report-out mode (`--report-out <path>`) that writes the
   report only to the explicitly supplied path. The recommended use is to supply
   a path outside tracked evidence during commit gates (for example
   `/tmp/...`).
4. Add an explicit write-report mode (`--write-report`) that is required for
   writing the canonical tracked PS-034A report at
   `docs/evidence/ps-034a/smoke-harness-v1-report.json`.
5. Specify the default behavior explicitly. The preferred default is
   check-only for non-PS034A current slices, while preserving a clear explicit
   write path for PS-034A harness evidence regeneration.
6. Preserve existing accepted PS-034A and PS-034B behavior. The PS-034A and
   PS-034B smokes must still pass after the PS-035C commit.
7. Preserve existing `--current`, `--frontend`, and `--no-frontend` behavior.
   These flags must remain supported.
8. Provide a PS-035C smoke that proves:
   - invoking the central gate in check-only mode leaves `git status` clean and
     leaves the PS-034A report digest unchanged;
   - explicit `--report-out /tmp/...` writes only to the requested out-of-tree
     report path and does not dirty tracked evidence;
   - the smoke does not run frontend unless explicitly requested.
9. Preserve the truth boundary (section 17). PS-035C fixes validation mutation
   only. It does not prove product correctness, production security, B2
   immutability, or billing behavior.
10. Define local/static smoke validation only (section 15). PS-035C must not
    call providers and must not read or write live B2.
11. Preserve PS-034A/PS-034B harness constraints. Both smokes must still pass
    after the commit, in safe local mode with no evidence mutation.
12. No hidden Git index flags may be introduced. PS-035C must not add or rely on
    any hidden Git index flag.

## 6. Non-goals

PS-035C must not:

- do not call live providers (no provider calls)
- do not read or write live B2 (no B2 reads, no B2 writes)
- do not do broad B2 reads
- do not run frontend unless explicitly requested
- do not claim product correctness, production security, B2 immutability,
  tamper-proof storage, or billing behavior
- do not claim semantic truth, legal authenticity, C2PA authenticity, or human
  authorship
- do not change the historical contracts that the gate verifies
- do not change the golden demo canonical constants
- do not change product UI
- do not introduce a new provider
- do not require any control name containing `KEY`, `TOKEN`, or `SECRET`
- do not print secrets
- do not add hidden Git index flags
- do not mutate `docs/evidence/ps-034a/smoke-harness-v1-report.json` during
  normal future-slice validation
- do not call providers, read B2, or write B2 as part of PS-035C validation
- do not silently break existing PS-034A/PS-034B behavior
- do not make forbidden overclaims

PS-035C only edits this spec file in the spec-only phase.
Implementation-phase candidates are listed in section 8.

## 7. Spec-only Allowed File

This spec-only commit touches only:

- `specs/49-ps-035c-non-mutating-regression-gate-mode.md`

No other files are changed during the spec-only phase. No scripts, no smoke
scripts, no `smoke_lib`, no regression gate, no evidence, no proof docs, no env
files, and no requirements are changed.

## 8. Recommended Implementation Files

The following are implementation-phase candidates only, clearly marked as
implementation-phase only. They are not for this spec-only commit:

- `scripts/proofstudio_regression_gate.py`
- `scripts/ps034a_smoke_harness_v1_smoke.py`
- `scripts/ps035c_non_mutating_regression_gate_mode_smoke.py`
- `docs/evidence/ps-035c/non-mutating-regression-gate-mode-report.json`
- `docs/ps-035c-non-mutating-regression-gate-mode-proof.md`
- `docs/validation/proofstudio-smoke-harness-v1.md`
- `specs/07-master-spec-plan.md`
- `specs/08-roadmap-slices.md`

Any edit to `scripts/proofstudio_regression_gate.py` is the implementation
phase actually adding the non-mutating mode and the new CLI flags. It must
preserve PS-034A/PS-034B harness constraints (safe local mode, no evidence
mutation, no provider calls, no live B2) and must keep `--current`,
`--frontend`, and `--no-frontend` supported.

Any edit to `scripts/ps034a_smoke_harness_v1_smoke.py` is allowed only to keep
the accepted PS-034A smoke compatible with the new explicit write contract. If
the PS-034A smoke needs to regenerate the canonical tracked PS-034A report, it
must invoke the central gate with `--write-report`; otherwise it must use a
non-mutating mode. This prevents an implicit canonical-report write path from
surviving under the old smoke invocation.

Any edit to `docs/validation/proofstudio-smoke-harness-v1.md`,
`specs/07-master-spec-plan.md`, or `specs/08-roadmap-slices.md` is the
implementation phase documenting the non-mutating mode and must not introduce
forbidden overclaims.

PS-035C implementation must not edit `scripts/smoke_lib.py` unless a
PM-approved change is required to support the new modes. If
`scripts/smoke_lib.py` is edited, the change must be additive and must not
break existing helpers.

## 9. Forbidden Files Unless PM-approved Later

PS-035C implementation must not touch:

- `src/**`
- `apps/**`
- `docs/evidence/ps-034a/smoke-harness-v1-report.json`
- `docs/evidence/demo/**`
- `docs/evidence/ps-035a/**`
- `docs/evidence/ps-035b/**`
- `.env*`
- `render.yaml`
- requirements files

The canonical tracked PS-034A report
(`docs/evidence/ps-034a/smoke-harness-v1-report.json`) may only be written by
the central gate under an explicit, PM-aware regeneration (the `--write-report`
path, ideally combined with `--current ps034a`). It must never be written as a
side effect of validating a later slice, and its bytes must not be hand-edited.

## 10. Non-mutating Regression Gate Contract

PS-035C defines the following behavioral contract for the central regression
gate.

- During normal future-slice validation, the gate must not mutate tracked
  historical PS-034A evidence. Specifically, running the gate with a
  non-PS034A `--current` must not write
  `docs/evidence/ps-034a/smoke-harness-v1-report.json`.
- The gate must support a non-mutating mode that can validate all historical
  contracts and print the same pass/fail summary without writing any report
  file.
- The gate must support writing the report to an explicitly supplied path
  (`--report-out <path>`), recommended to be outside tracked evidence during
  commit gates.
- The gate must require an explicit `--write-report` to write the canonical
  tracked PS-034A report.
- The default behavior must be specified explicitly. Preferred default:
  check-only for non-PS034A current slices, while preserving a clear explicit
  write path for PS-034A harness evidence regeneration.
- The gate must still compute the same pass/fail summary, the same
  `historical_contracts_verified` boolean, the same
  `historical_contract_ids`/`historical_contract_count`/`historical_contract_failures`,
  and the same frontend behavior, regardless of whether a report file is
  written.
- The gate must not call live providers and must not read or write live B2
  while validating. The validation is local/static only.
- The gate must not add or rely on hidden Git index flags.

## 11. CLI Contract

PS-035C defines the following CLI contract for
`scripts/proofstudio_regression_gate.py`. Existing flags must remain
supported.

Existing flags (must remain supported):

- `--current <slice>`: required. Current slice id, for example `ps034a`,
  `ps035b`, or `ps034`. Behavior is unchanged for accepted historical slices.
- `--frontend`: run the frontend typecheck/build exactly once at the top level.
  Opt-in. Default is off.
- `--no-frontend`: skip the frontend typecheck/build. This is the default.

New flags (added by PS-035C):

- `--check-only`: no report file is written. The gate validates all historical
  contracts and prints the same pass/fail summary. This is the preferred
  default for non-PS034A current slices.
- `--report-out <path>`: write the report only to the explicitly supplied path.
  Recommended use is to supply a path outside tracked evidence during commit
  gates (for example `/tmp/ps035c-gate-report.json`). When `--report-out` is
  supplied, the canonical tracked PS-034A report must not be written.
- `--write-report`: required for writing the canonical tracked PS-034A report
  at `docs/evidence/ps-034a/smoke-harness-v1-report.json`. Recommended use is
  combined with `--current ps034a` for PM-aware PS-034A harness evidence
  regeneration.

Default behavior decision (must be specified explicitly):

- Preferred default: for a non-PS034A `--current` slice, the gate defaults to
  check-only. No report file is written unless `--report-out` or
  `--write-report` is supplied.
- For `--current ps034a`, writing the canonical tracked PS-034A report still
  requires `--write-report`. The PS-034A smoke must be updated, if needed, to
  pass `--write-report` explicitly when regenerating the canonical PS-034A
  harness evidence.

Conflict rules:

- `--check-only` conflicts with `--write-report` and with `--report-out`. If
  conflicting write modes are supplied, the gate must error out clearly and
  must not write any file.
- `--write-report` and `--report-out` are mutually exclusive. If both are
  supplied, the gate must error out clearly and must not write any file.
- Regardless of write mode, the gate must never write the canonical tracked
  PS-034A report as a side effect of validating a non-PS034A slice.

The implementation must report the selected write mode as a measured field
(`write_mode`, one of `check_only`, `report_out`, `write_report`) in the report
when a report is written, and must reflect the selected mode in the printed
summary.

## 12. Report Output Contract

The report content schema stays the same as the accepted PS-034A schema. The
same `ok`, `current_slice`, `historical_contracts_verified`,
`historical_contract_ids`, `historical_contract_count`,
`historical_contract_failures`, `prior_evidence_clean`,
`no_hidden_git_flags_before`, `no_hidden_git_flags_after`, `no_provider_call`,
`no_broad_b2_read`, `frontend_ran`, `failures`, and `checked_at` fields must be
populated the same way regardless of where (or whether) the report is written.

When a report is written, the implementation must add at least these new
measured fields:

- `write_mode`: one of `check_only`, `report_out`, `write_report`.
- `report_path`: the absolute or repo-relative path the report was written to,
  or `null` / omitted when no report is written.
- `non_mutating_gate`: `true` when the canonical tracked PS-034A report was not
  written as a side effect.
- `ps034a_report_digest_unchanged`: `true` when the SHA-256 digest of
  `docs/evidence/ps-034a/smoke-harness-v1-report.json` is unchanged across the
  gate run.

In `--check-only` mode, no report file is written and the pass/fail summary is
printed to stdout/stderr the same way it is today.

In `--report-out <path>` mode, the report is written only to `<path>`. The
canonical tracked PS-034A report must not be written.

In `--write-report` mode, the canonical tracked PS-034A report is written at
`docs/evidence/ps-034a/smoke-harness-v1-report.json`. This mode is intended for
PM-aware PS-034A harness evidence regeneration, ideally with `--current ps034a`.

## 13. Backward Compatibility Contract

PS-035C must not silently break existing accepted behavior.

- PS-034A and PS-034B smokes must still pass after the PS-035C commit. If the
  PS-034A smoke writes the canonical PS-034A report, that write must occur only
  through the explicit `--write-report` path; later-slice validation must remain
  non-mutating.
- `--current`, `--frontend`, and `--no-frontend` must remain supported and must
  behave the same way for accepted historical slices.
- The historical contract table verified by the gate must not be weakened. The
  same set of historical slices must be verified with the same evidence, route,
  component, and golden requirements.
- The golden demo canonical constants must not be changed.
- The `no_provider_call`, `no_broad_b2_read`, and `no_git_hiding_policy`
  assurances must remain true.

The only behavioral change for existing callers is that running the gate for a
non-PS034A slice no longer writes the canonical tracked PS-034A report. Callers
who depended on that side effect must switch to `--report-out <path>` or
`--write-report`. This is the intended fix, not a regression.

## 14. PS-034A Historical Evidence Protection Contract

The canonical tracked PS-034A report
(`docs/evidence/ps-034a/smoke-harness-v1-report.json`) is historical evidence.
PS-035C protects it as follows.

- During normal future-slice validation (any non-PS034A `--current`), the gate
  must not write the canonical tracked PS-034A report.
- The canonical tracked PS-034A report may only be written under an explicit,
  PM-aware regeneration via `--write-report`, ideally combined with
  `--current ps034a`.
- The PS-035C smoke must prove that invoking the central gate in check-only
  mode leaves the SHA-256 digest of
  `docs/evidence/ps-034a/smoke-harness-v1-report.json` unchanged.
- The PS-035C smoke must prove that `--report-out /tmp/...` writes only to the
  requested out-of-tree path and does not dirty tracked evidence.
- The bytes of `docs/evidence/ps-034a/smoke-harness-v1-report.json` must not be
  hand-edited by PS-035C.

This contract complements the existing PS-034A/PS-034B historical evidence
prefix lists. The PS-034A report path is the gate's own output, so it is not in
the gate's `PRIOR_EVIDENCE_PREFIXES` list. PS-035C protects it by behavior
(non-mutating default), not by adding it to the prefix list.

## 15. Validation Plan

PS-035C implementation must be validated with local/static validation only:

- py_compile of the edited central gate and the new PS-035C smoke.
- the PS-035C smoke pass.
- the PS-035C smoke proves that invoking the central gate in check-only mode
  leaves `git status` clean and leaves the PS-034A report digest unchanged.
- the PS-035C smoke proves that explicit `--report-out /tmp/...` writes only to
  the requested out-of-tree report path and does not dirty tracked evidence.
- the PS-035C smoke does not run frontend unless explicitly requested.
- the PS-035a smoke still passes.
- the PS-035b smoke still passes.
- the PS-034A smoke still passes after the commit and uses the explicit
  `--write-report` path if it regenerates canonical PS-034A evidence.
- the PS-034B smoke still passes after the commit.
- the central gate, when run in check-only mode for a non-PS034A current slice,
  leaves `git status` clean.
- no executable provider/B2 calls in the PS-035C smoke (static proof: the smoke
  must perform no live provider call, no live B2 read, no live B2 write).
- no false claims of product correctness, production security, B2 immutability,
  tamper-proof storage, or billing behavior (no forbidden overclaims).
- changed-files allowlist: only the files in section 8 may appear in the diff.
- a no-hidden-Git-flags check:
  ```
  git ls-files -v | grep -E '^[a-z]'
  ```
  must return nothing both before and after validation.
- `git diff --check` returns clean.
- no read or write of B2 during PS-035C validation (no B2 reads, no B2 writes).
- no provider calls during PS-035C validation.

## 16. Evidence Model

The future PS-035C evidence report JSON
(`docs/evidence/ps-035c/non-mutating-regression-gate-mode-report.json`) must
include at least:

- `ok`
- `slice_id: ps035c`
- `checked_at`
- `non_mutating_gate`
- `write_mode_check_only_supported`
- `write_mode_report_out_supported`
- `write_mode_write_report_supported`
- `default_is_check_only_for_non_ps034a`
- `check_only_leaves_git_clean`
- `check_only_leaves_ps034a_digest_unchanged`
- `report_out_writes_only_to_requested_path`
- `report_out_does_not_dirty_tracked_evidence`
- `write_report_required_for_canonical_ps034a_report`
- `current_flag_supported`
- `frontend_flag_supported`
- `no_frontend_flag_supported`
- `no_provider_calls`
- `no_b2_reads`
- `no_b2_writes`
- `no_hidden_git_flags`
- `frontend_not_run_unless_requested`
- `truth_boundary_preserved`
- `no_forbidden_overclaims`
- `no_forbidden_file_changes`
- `failures`

`ok` is true only when every measured field is truthful and no forbidden
overclaim or forbidden file change is present. `failures` is a list of
human-readable failure strings and must be empty on acceptance.

## 17. Truth Boundary

ProofStudio proves what the pipeline did.

PS-035C fixes validation mutation only. It does not prove product correctness,
production security, B2 immutability, tamper-proof storage, real billing API
integration, or billing behavior.

PS-035C does not prove:

- product correctness
- production security
- B2 immutability
- tamper-proof storage
- real billing API integration
- billing behavior
- semantic truth
- legal authenticity
- C2PA authenticity
- human authorship
- browser-side B2 byte verification

PS-035C only proves that the central regression gate, in non-mutating mode, no
longer overwrites tracked historical PS-034A evidence as a side effect of
validating a later slice, and that the same pass/fail summary is produced.

PS-035C must preserve this boundary verbatim across the proof doc, evidence
report, and smoke. No PS-035C artifact may imply product correctness,
production security, B2 immutability, tamper-proof storage, real billing API
integration, or billing behavior.

## 18. Risks

PS-035C must record the following risks with mitigations:

- silent evidence mutation
  - risk: the central gate overwrites
    `docs/evidence/ps-034a/smoke-harness-v1-report.json` whenever a later slice
    is validated, and the mutation is only noticed when `git status` is checked.
  - mitigation: PS-035C makes the gate non-mutating by default for non-PS034A
    slices and reports `non_mutating_gate` and
    `check_only_leaves_ps034a_digest_unchanged` as measured fields.
- caller depends on the side effect
  - risk: an existing caller relied on the central gate writing the tracked
    PS-034A report as a side effect, and silently stops getting that file.
  - mitigation: PS-035C preserves an explicit `--write-report` path for
    PS-034A harness evidence regeneration, and an explicit `--report-out` path
    for any caller that wants the report at a chosen location.
- default-behavior surprise
  - risk: changing the default to check-only surprises a caller who expected a
    written report.
  - mitigation: the default decision is documented explicitly in section 11;
    `--report-out` and `--write-report` remain available.
- harness regression
  - risk: PS-035C changes break the PS-034A/PS-034B harness.
  - mitigation: PS-035C must preserve PS-034A/PS-034B harness constraints; both
    smokes must still pass after the commit in safe local mode.
- conflict-handling
  - risk: conflicting write modes (`--check-only` with `--write-report`, or
    `--report-out` with `--write-report`) silently pick one and write the
    canonical PS-034A report anyway.
  - mitigation: conflicting write modes must error out clearly and must not
    write any file.
- overclaim drift
  - risk: a future artifact describes PS-035C as proving product correctness,
    production security, B2 immutability, or billing behavior.
  - mitigation: preserve the truth boundary verbatim; PS-035C fixes validation
    mutation only; report `no_forbidden_overclaims`.
- secret-safety drift
  - risk: PS-035C introduces a control name containing `KEY`, `TOKEN`, or
    `SECRET`, or otherwise leaks secrets.
  - mitigation: PS-035C must not introduce control names containing `KEY`,
    `TOKEN`, or `SECRET`, and must not print secrets.

## 19. Acceptance Criteria

PS-035C is accepted only when:

- the PS-035C spec exists (this document, accepted)
- only the spec file is changed in the spec-only phase
- the root cause is documented accurately: the central gate has a hardcoded
  tracked PS-034A report path and `write_report(report)` always writes to it,
  so running the gate for a later slice mutates tracked historical PS-034A
  evidence
- the CLI contract is documented (`--check-only`, `--report-out`, and
  `--write-report`, plus existing `--current`, `--frontend`, `--no-frontend`)
- the non-mutating mode is documented
- the explicit `--report-out` / `--write-report` behavior is documented
- the default behavior decision is documented (preferred default check-only for
  non-PS034A current slices)
- historical PS-034A report protection is documented
- future validation can run the central gate without a manual restore of
  `docs/evidence/ps-034a/smoke-harness-v1-report.json`
- the truth boundary is preserved (PS-035C fixes validation mutation only; it
  does not prove product correctness, production security, B2 immutability, or
  billing behavior)
- PS-035C performs no provider calls, no B2 reads, and no B2 writes
- PS-035C preserves PS-034A/PS-034B harness constraints
- the PS-034A smoke uses `--write-report` explicitly if it regenerates the
  canonical tracked PS-034A report
- PS-035C makes no claim of product correctness, production security, B2
  immutability, tamper-proof storage, real billing API integration, or billing
  behavior
- no implementation files are changed during the spec-only phase
- commit and push are required before acceptance

## 20. Rollback

Rollback of the PS-035C spec-only phase is a single revert of the PS-035C spec
commit, because only this spec file is changed in this phase.

Future implementation rollback must restore the pre-PS-035C state of the edited
files in section 8. Specifically, if PS-035C implementation turns out to break
the PS-034A/PS-034B harness or to fail to keep the gate non-mutating, rollback
must restore:

- `scripts/proofstudio_regression_gate.py` to its pre-PS-035C state
- remove `scripts/ps035c_non_mutating_regression_gate_mode_smoke.py`
- remove `docs/evidence/ps-035c/non-mutating-regression-gate-mode-report.json`
- remove `docs/ps-035c-non-mutating-regression-gate-mode-proof.md`
- restore `docs/validation/proofstudio-smoke-harness-v1.md`,
  `specs/07-master-spec-plan.md`, and `specs/08-roadmap-slices.md` to their
  pre-PS-035C state if they were edited

Rollback of PS-035C implementation must not touch
`docs/evidence/ps-034a/smoke-harness-v1-report.json`. If the canonical tracked
PS-034A report was mistakenly mutated, it must be restored from git history to
its last accepted PS-034A state, not hand-edited.

Because PS-035C is intentionally scoped to a non-mutating regression gate mode,
a PS-035C smoke, PS-035C evidence, a PS-035C proof doc, the validation doc, the
master spec plan, and the roadmap slices doc, rollback is isolated, reversible,
and does not require touching product UI, providers, deployment topology,
product code under `src/**`, frontend code under `apps/**`, env files, or
deployment config.
