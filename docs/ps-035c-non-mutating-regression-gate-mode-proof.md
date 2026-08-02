# PS-035C — Non-Mutating Regression Gate Mode (Proof)

Slice: PS-035C — Non-Mutating Regression Gate Mode
Branch: `ps-035c/non-mutating-regression-gate-mode`
Date: 2026-07-01

## Root cause

The central regression gate (`scripts/proofstudio_regression_gate.py`) had a
hardcoded tracked report path:

- `REPORT_PATH = docs/evidence/ps-034a/smoke-harness-v1-report.json`
- `write_report(report)` unconditionally called
  `sl.write_json_atomic(REPORT_PATH, report)` to that one path.
- `run_gate(...)` called `write_report(report)` unconditionally before
  returning, regardless of `--current`.

Because the report path was hardcoded to the tracked PS-034A historical
evidence file and the write was unconditional, running the central gate for any
later slice (for example
`python scripts/proofstudio_regression_gate.py --current ps035b --no-frontend`)
overwrote `docs/evidence/ps-034a/smoke-harness-v1-report.json` with a report
whose `current_slice`, `checked_at`, and other fields reflected the later slice,
not the historical PS-034A run. That dirtied tracked historical evidence as a
side effect of validating a future slice, and forced PS-035b validation to
manually restore the file afterward.

This is a validation-harness root-cause bug. It is not a PS-035b product bug,
not a regression in product behavior, and not a security bug in the product.

## Files changed

- `scripts/proofstudio_regression_gate.py` — added `--check-only`,
  `--report-out <path>`, and `--write-report`; made the gate non-mutating by
  default; added write-mode conflict resolution; rejected `--write-report` for
  non-PS034A current slices; added the `write_mode`, `report_path`,
  `non_mutating_gate`, and `ps034a_report_digest_unchanged` measured fields.
- `scripts/ps034a_smoke_harness_v1_smoke.py` — the PS-034A smoke now passes
  `--write-report` explicitly when it regenerates the canonical tracked PS-034A
  report (no implicit canonical-report write path survives).
- `scripts/ps035c_non_mutating_regression_gate_mode_smoke.py` (new) — local /
  static PS-035C smoke proving the non-mutating contract.
- `docs/evidence/ps-035c/non-mutating-regression-gate-mode-report.json` (new) —
  PS-035C evidence report (written by the smoke).
- `docs/ps-035c-non-mutating-regression-gate-mode-proof.md` (new) — this proof
  doc.
- `docs/validation/proofstudio-smoke-harness-v1.md` — append-only PS-035C note.
- `specs/07-master-spec-plan.md` — PS-035C status update.
- `specs/08-roadmap-slices.md` — PS-035C acceptance update.

No product code under `src/**`, no frontend code under `apps/**`, no env files,
no requirements, no `render.yaml`, no `scripts/smoke_lib.py`, and no prior-slice
evidence bytes were changed. The canonical tracked PS-034A report
(`docs/evidence/ps-034a/smoke-harness-v1-report.json`) was not hand-edited; its
SHA-256 digest is unchanged from the pre-PS-035C baseline.

## CLI behavior

Existing flags remain supported and unchanged for accepted historical slices:

- `--current <slice>` (required).
- `--frontend` (opt-in top-level typecheck/build).
- `--no-frontend` (default).

New PS-035C flags:

- `--check-only` — no report file is written; the gate validates every
  historical contract and prints the same pass/fail summary.
- `--report-out <path>` — the report is written only to the explicitly supplied
  path (recommended outside tracked evidence during commit gates). The
  canonical tracked PS-034A report is never written in this mode.
- `--write-report` — writes the canonical tracked PS-034A report at
  `docs/evidence/ps-034a/smoke-harness-v1-report.json`. This is only allowed
  with `--current ps034a` (or `ps-034a` / `ps034A`-equivalent).

Conflict handling (errors clearly before any file is written):

- `--check-only` conflicts with `--report-out` and with `--write-report`.
- `--report-out` conflicts with `--write-report`.

`--write-report` for a non-PS034A current slice is rejected. The gate exits
nonzero with a clear message and writes no file. This is the preferred and
implemented behavior, so a later slice can never mutate the canonical tracked
PS-034A report as a side effect.

## Default behavior

The default write mode for every slice (including PS-034A) is check-only. No
report file is written unless `--report-out <path>` or `--write-report` is
supplied. Writing the canonical tracked PS-034A report always requires the
explicit `--write-report` flag (recommended with `--current ps034a` for PM-aware
PS-034A harness evidence regeneration). This removes the manual-restore
workaround that PS-035b validation had to perform.

## Check-only leaves the canonical PS-034A report unchanged

In check-only mode the gate writes no file. The SHA-256 digest of
`docs/evidence/ps-034a/smoke-harness-v1-report.json` is measured before and
after the gate run and reported as `ps034a_report_digest_unchanged: true`. The
file is never dirtied.

## report-out writes only the requested out-of-tree path

In report-out mode the gate writes only to the explicitly supplied path. The
canonical tracked PS-034A report is never written. The PS-035C smoke proves that
`--report-out /tmp/...` writes only the requested `/tmp` file, leaves tracked
evidence clean, and leaves the PS-034A report digest unchanged.

## write-report is explicit

The canonical tracked PS-034A report may only be written under an explicit,
PM-aware regeneration via `--write-report` (ideally with `--current ps034a`).
The PS-035C smoke exercises this exactly once: it regenerates the canonical
report with `--current ps034a --write-report`, confirms the digest changed
(proving the write really happened), then restores the canonical report from
git immediately and confirms the digest returns to the baseline. This is the
only permitted canonical-report write, and it is wrapped so the restore always
runs.

## PS-034A smoke updated

`scripts/ps034a_smoke_harness_v1_smoke.py` now passes `--write-report`
explicitly when it invokes the central gate to regenerate canonical PS-034A
evidence. No old implicit canonical-report write path survives; later-slice
validation remains non-mutating.

## No provider / B2 / frontend

PS-035C is validation-harness only. The PS-035C smoke and the central gate
perform no live provider call, no live B2 read, and no live B2 write. The
frontend is not run unless `--frontend` is explicitly passed; the PS-035C smoke
and all validation invocations use `--no-frontend`. PS-035C adds no hidden Git
index flags and relies on none.

## Validation results

- `py_compile` of the edited gate, the PS-034A smoke, and the PS-035C smoke:
  pass.
- PS-035C smoke: pass (all measured fields true, `failures` empty).
- Central gate `--current ps035c --no-frontend --check-only`: pass; canonical
  PS-034A report digest unchanged; `git status` clean except PS-035C
  implementation files.
- Central gate `--current ps035c --no-frontend --report-out /tmp/...`: pass;
  writes only the requested `/tmp` file; tracked evidence clean; PS-034A report
  digest unchanged.
- Conflicting flag combinations error before writing.
- `--write-report` for a non-PS034A current slice is rejected.
- Hidden Git index flags: none before or after.
- `git diff --check`: clean.
- Changed-files allowlist: only the PS-035C allowed implementation files appear.
- `docs/evidence/ps-034a/smoke-harness-v1-report.json` SHA-256 unchanged from
  the pre-PS-035C baseline.

## Truth Boundary

ProofStudio proves what the pipeline did.

PS-035C fixes validation mutation only: the central regression gate, in
non-mutating mode, no longer overwrites tracked historical PS-034A evidence as a
side effect of validating a later slice, and the same pass/fail summary is
produced.

PS-035C does not prove product correctness, production security, B2
immutability, tamper-proof storage, real billing API integration, billing
behavior, semantic truth, legal authenticity, C2PA authenticity, human
authorship, or browser-side B2 byte verification. It is not tamper-proof, not
Object Lock, not production immutability, not B2 immutability, not real billing,
and not production security. PS-035C fixes validation mutation only.
