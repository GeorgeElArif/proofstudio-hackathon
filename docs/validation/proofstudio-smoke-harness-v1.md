# ProofStudio Smoke Harness v1 (Validation Policy)

Status: Active (PS-034A)
Date: 2026-06-30
Scope: All feature slices PS-023 onward; mandatory for PS-035 and beyond.

## Problem Statement

Historical feature-slice smokes grew into recursive chains. A smoke for one
slice would launch the smoke for the previous slice, which launched the smoke
before it, and so on. As the chain deepened it caused:

- repeated nested frontend typecheck/build runs inside a single validation pass
- some historical smokes rewriting checked-in evidence while a parent smoke ran
- nested Git status checks seeing temporary evidence changes as real diffs
- deep subprocess trees that timed out
- workaround attempts such as Git index hiding flags or polling background
  watchers that rewrote prior evidence to mask the mutation

This is not acceptable for a professional product.

## Root Cause (from the PS-034 recursive smoke failure)

The PS-034 smoke attempted to validate the full historical chain by depending
on transitive smoke execution. Each prior smoke owned its own evidence and its
own frontend build, so a single PS-034 run effectively re-ran the whole
frontend pipeline many times and re-touched evidence it did not own. The
failure mode was architectural: validation responsibility was spread across
many recursive entry points instead of one central, non-recursive coordinator.

## New Validation Architecture

Feature slice smokes validate the slice. The regression gate validates the release.

There are exactly two validation roles:

1. **Feature slice smoke** — validates the current slice only. It runs local,
   contract-based checks over the slice's own component, data, route, and
   evidence. It owns only its own evidence file.
2. **Central regression gate** (`scripts/proofstudio_regression_gate.py`) —
   validates release readiness across all accepted slices. It is non-recursive.
   It verifies accepted historical slices through checked-in contracts instead
   of re-running their smokes.

Feature slice smokes and the central regression gate are not the same thing.

## Slice-Local Smoke Rules

No feature smoke may recursively execute another feature smoke.

A feature smoke must:

- validate only the current slice
- read checked-in prior evidence as immutable inputs
- write only its own evidence file
- never launch another smoke script as a subprocess
- never call a provider (unless the slice explicitly owns provider execution)
- never read arbitrary B2 objects
- never run the frontend typecheck/build (that belongs to the central gate)

## Central Regression Gate Rules

A slice smoke may write only its own evidence file.

Only `scripts/proofstudio_regression_gate.py` may coordinate cross-slice
validation, and it must do so non-recursively. The gate contains no
historical feature-smoke path references. It verifies prior slices through a
contract table — not through smoke script paths:

- slice id
- evidence JSON path (where applicable)
- route path (where applicable)
- component / source file path (where applicable)
- golden constants required or not
- expected ok / pass fields

For each accepted historical slice the contract table confirms:

- checked-in evidence exists where applicable
- accepted status (`ok: true`) exists where applicable
- key smoke checks contain no `fail` entries where applicable
- golden constants match the canonical golden run where applicable
- the expected route is still registered in `apps/web/src/App.tsx`
- the expected component / source file still exists
- no forbidden authenticity claims are absent
- Git status remains clean except for expected current-slice files
- prior evidence is not modified

The gate never executes a feature smoke. It never calls a provider. It never
reads arbitrary B2. It never mutates prior-slice evidence.

## Evidence Ownership Rules

Each slice owns exactly one evidence directory. A slice smoke may write only
its own evidence file.

| Slice           | Evidence it may write                       |
|-----------------|---------------------------------------------|
| PS-021          | `docs/evidence/ps-021/`                     |
| PS-025 .. PS-034| `docs/evidence/ps-0NN/`                     |
| PS-034A         | `docs/evidence/ps-034a/`                    |
| PS-035 onward   | `docs/evidence/ps-0NN(a)/` for that slice   |

Prior-slice evidence prefixes are guarded and must remain clean during any
slice smoke or gate run.

## Frontend Build Once Rule

Frontend typecheck and build run once at the top-level gate.

The central gate runs `npm run typecheck` and `npm run build` in `apps/web`
exactly once per invocation, and only when `--frontend` is passed. Feature
smokes must never trigger nested frontend builds. The shared library enforces a
single-invocation guard so a second build attempt in the same process fails.

## Forbidden Workaround List

No smoke may hide evidence changes with Git index flags.

The harness rejects the following in smoke scripts and validation docs.

Git index hiding (the literal hyphenated flag forms are forbidden):

- assume unchanged flag
- skip worktree flag
- git update index command
- update index command

The harness also verifies that `git ls-files -v` shows no lowercase tag flags
before validation and after validation.

Polling / background-rewriter workarounds are forbidden:

- background watcher classes that poll and rewrite prior evidence
- concurrent rewriter threads that mask evidence mutation
- any mechanism that rewrites prior-slice evidence while another smoke runs

The shared library centralizes these term lists and asserts their absence in
the harness files on every gate run.

## Historical Contract Validation Explanation

For accepted historical slices PS-023 through PS-034, the central gate verifies
a contract table instead of re-running recursive historical smokes. The gate
contains no historical feature-smoke path references. For each accepted slice
the contract table confirms:

- the evidence file exists where applicable
- the evidence JSON reports `ok: true` where an `ok` field exists
- the evidence `checks` map contains no `fail` entries where present
- golden constants (run id, campaign id, archive uri, archive sha256,
  rehydrate source, provider calls during rehydrate, no live provider call
  during rehydrate) agree with the canonical golden run where those fields
  exist
- the expected route is still registered in `apps/web/src/App.tsx`
- the expected source component still exists
- no forbidden authenticity claims are present
- prior evidence is not modified

Contract-based regression confirms accepted evidence and current route/file
presence. It does not prove every old smoke script would re-run today. That
full retrofit belongs to PS-034B.

## Evidence Report Schema Rule

Evidence report keys must never be overloaded. A field whose name implies a
boolean success flag must remain a boolean; a list of details must live in a
field whose name explicitly denotes a list.

- Boolean fields must remain booleans.
- Detail/list fields must use explicit detail names such as `_ids`, `_details`,
  or `_failures`.
- Do not overload evidence report keys.

The PS-034A gate enforces this for historical contract verification:

- `historical_contracts_verified`: boolean `true` only when every required
  historical contract passes. It is never a list.
- `historical_contract_ids`: list of verified slice ids, for example
  `["ps021", "ps023", "ps025", "ps026", "ps027", "ps028", "ps029", "ps030",
  "ps031", "ps032", "ps033", "ps034"]`.
- `historical_contract_count`: integer count of verified contract ids, equal to
  `len(historical_contract_ids)`.
- `historical_contract_failures`: list of per-contract failure descriptions,
  empty on success.

The PS-034A slice smoke verifies each of these on every run.

## Recursive Execution Detection

Recursive execution is detected structurally via Python AST parsing, not with
brittle text grep. The shared helper `assert_no_recursive_smoke_execution`
walks the parsed syntax tree and flags only real `Call` nodes that invoke a
process-execution primitive (`subprocess.run`, `subprocess.check_call`,
`subprocess.check_output`, `os.system`, `os.popen`, `Popen`) or a
`run_command`-family helper whose arguments name a feature smoke script
(`ps0...smoke.py`). Comments, docstrings, and policy text that merely mention
these mechanisms are never flagged. The banned literal term scan for Git
hiding and polling-watcher workarounds remains text-based by design.

## PS-034B Retrofit Plan

Historical smoke local-mode retrofit is deferred to PS-034B.

PS-034B will carefully retrofit PS-023 through PS-033 smokes so each can run in
a local / contract / no-frontend mode without launching other smokes and
without rebuilding the frontend. PS-034A deliberately does not modify those
historical scripts. Until PS-034B lands, the central gate is the authoritative
cross-slice validator and the historical scripts are treated as frozen inputs.

Historical smoke local-mode retrofit is now complete as of PS-034B. Every
historical smoke PS-023 through PS-034 defaults to safe local / check-only
mode, no longer recursively executes prior smokes, no longer runs nested
frontend builds, no longer uses Git index hiding, and no longer mutates prior
evidence by default.

## Rules For All Future Slices PS-035 Onward

Every future feature slice must:

1. Ship a feature smoke that validates only its own slice.
2. Never recursively execute another feature smoke.
3. Write only its own evidence file.
4. Never manipulate Git index flags.
5. Never use a polling background watcher or concurrent rewriter to mask
   evidence mutation.
6. Never run the frontend typecheck/build; delegate that to the central gate.
7. Never call a provider unless the slice explicitly owns provider execution.
8. Never read arbitrary B2 objects.
9. Reuse `scripts/smoke_lib.py` for shared validation logic.
10. Be exercised end-to-end by the central regression gate.

## Example Commands

Central gate, contract-only (no frontend):

```bash
python scripts/proofstudio_regression_gate.py --current ps034a --no-frontend
```

Central gate, full release readiness (frontend once):

```bash
python scripts/proofstudio_regression_gate.py --current ps034a --frontend
```

PS-034A slice smoke:

```bash
python scripts/ps034a_smoke_harness_v1_smoke.py
```

Verify no hidden Git index flags remain:

```bash
git ls-files -v | awk '$1 ~ /^[a-z]/ {print}'
```

## PS-034C Note (2026-07-01)

PS-034C (Winning Roadmap + Master Spec Replan) is documentation/spec/roadmap
only. It adds a dedicated doc-contract smoke
(`scripts/ps034c_winning_roadmap_master_spec_replan_smoke.py`) that is local /
static only: it reads docs/specs only, does not call providers, does not read
B2, does not run the frontend or backend, does not call the central regression
gate, and does not mutate prior evidence. It writes only
`docs/evidence/ps-034c/winning-roadmap-master-spec-replan-report.json`.

PS-034C does not modify this harness, the central regression gate, or any
PS-034A/PS-034B behavior. The PS-034A required validation sentence above
("Historical smoke local-mode retrofit is deferred to PS-034B.") and the
PS-034B retrofit completion statement remain unchanged. The PS-034C smoke is
additive and does not renumber or override the existing slice-evidence
ownership rules.

## PS-035a Note (2026-07-01)

PS-035a (Genblaze v0.4.0 Manifest Verification / Golden-Run Manifest
Correctness) closes the canonical golden-run manifest null gap. It is named
truthfully as "Genblaze manifest correctness with exact published pins": the
requested v0.4.0 target was probed unavailable on the configured index at
implementation time, so the published-version fallback
(`genblaze-core==0.3.4`, `genblaze-s3==0.3.4`, `genblaze-gmicloud==0.3.2`) was
selected and recorded honestly. No v0.4.0 claim is made.

PS-035a adds a feature smoke
(`scripts/ps035a_genblaze_manifest_correctness_smoke.py`) that is local /
static only: it reads checked-in files only, does not call providers, does not
read or write B2, does not run the frontend, does not run the backend, does not
call the central regression gate, does not mutate prior evidence, and writes
only `docs/evidence/ps-035a/genblaze-manifest-correctness-report.json`.

PS-035a migrates the PS-024 smoke from the old null-manifest contract to a
real-manifest contract: the canonical golden run now carries a real non-null
`manifest_uri` (a checked-in local fixture path, not a live B2 URL), a real
64-hex `manifest_hash`, a matching `manifest_sha256`, the exact recorded
Genblaze versions actually installed, and the checked-in manifest fixture's
independent SHA-256 recompute equals the golden `manifest_hash`.

PS-035a does not modify this harness, the central regression gate, the shared
smoke library, the PS-021 smoke, or any PS-034A/PS-034B behavior. The PS-034A
required validation sentence above ("Historical smoke local-mode retrofit is
deferred to PS-034B.") and the PS-034B retrofit completion statement remain
unchanged. The PS-035a smoke is additive and does not renumber or override the
existing slice-evidence ownership rules. A checked-in manifest fixture proves
reproducible local manifest-hash correctness, not live B2 Object Lock,
tamper-proof storage, or semantic truth.

## PS-035b Note (2026-07-01)

PS-035b (Cost Caps + Golden-Fixture Governance) adds a real, default-off
backend governance contract plus a golden-fixture digest freeze. It is named
truthfully as "Cost Caps + Golden-Fixture Governance": the four governance
controls (`PROOFSTUDIO_LIVE_RUNS_ENABLED=false`,
`PROOFSTUDIO_B2_WRITES_ENABLED=false`, `PROOFSTUDIO_COST_CAP_USD=0.00`,
`PROOFSTUDIO_FIXTURES_FROZEN=true`) plus an explicit PM/human approval gate
(`PROOFSTUDIO_PAID_RUN_APPROVED=false`) are policy flags, not secrets, and
never use names containing `KEY`, `TOKEN`, or `SECRET`.

PS-035b adds a feature smoke
(`scripts/ps035b_cost_caps_golden_fixture_governance_smoke.py`) that is local /
static only: it reads checked-in files only, does not call providers, does not
read or write B2, does not run the frontend, does not run the backend, does not
call the central regression gate, does not mutate prior evidence, and writes
only `docs/evidence/ps-035b/cost-caps-golden-fixture-governance-report.json`.

PS-035b enforces the gate in `src/proofstudio/api/live_bridge.py` and
`src/proofstudio/api/services.py`: `run_live=true` alone is no longer
sufficient to execute providers; the governance flags must explicitly enable
live runs, approve the paid run, set a non-zero cost cap, and not be in
`free-only` budget mode. B2 writes after a successful live run require
`PROOFSTUDIO_B2_WRITES_ENABLED=true`. A checked-in digest manifest
(`docs/evidence/golden-fixture-digests.json`) records SHA-256 digests for the
golden demo run and the PS-035a manifest fixture; the PS-035b smoke recomputes
and verifies them. PS-035a evidence (`docs/evidence/ps-035a/`) is now protected
by the `HISTORICAL_PRIOR_EVIDENCE_PREFIXES` list in `scripts/smoke_lib.py` and
the `PRIOR_EVIDENCE_PREFIXES` list in
`scripts/proofstudio_regression_gate.py`.

PS-035b does not renumber or override the existing slice-evidence ownership
rules. The PS-035b smoke is additive and writes only its own evidence. The
golden-fixture freeze proves byte equality to recorded digests only; it is not
tamper-proof, not Object Lock, and not production immutability. The cost cap is
a local policy gate, not a real billing API integration and not production
multi-user budget accounting.

## PS-035C Note (2026-07-01)

PS-035C (Non-Mutating Regression Gate Mode) is a validation-harness slice. It
fixes a validation-harness root-cause bug, not a product bug: the central
regression gate previously had a hardcoded tracked report path and wrote
`docs/evidence/ps-034a/smoke-harness-v1-report.json` unconditionally, so running
the gate for any later slice mutated tracked historical PS-034A evidence as a
side effect.

PS-035C makes the central gate non-mutating by default. The accepted write modes
are:

- `--check-only` (default for every slice, including PS-034A): validate every
  historical contract and print the same pass/fail summary without writing any
  report file. The canonical tracked PS-034A report is never touched.
- `--report-out <path>`: write the report only to the explicitly supplied path
  (recommended outside tracked evidence during commit gates). The canonical
  tracked PS-034A report is never touched.
- `--write-report`: write the canonical tracked PS-034A report. This is only
  allowed with `--current ps034a` (or `ps-034a` / `ps034A`-equivalent) for
  PM-aware PS-034A harness evidence regeneration. `--write-report` for any
  non-PS034A current slice is rejected.

Conflicting write modes (`--check-only` with `--report-out` or `--write-report`,
and `--report-out` with `--write-report`) error clearly before any file is
written. When a report is written, the gate adds the measured fields
`write_mode`, `report_path`, `non_mutating_gate`, and
`ps034a_report_digest_unchanged`.

PS-035C adds a feature smoke
(`scripts/ps035c_non_mutating_regression_gate_mode_smoke.py`) that is local /
static only: it runs the central gate in its PS-035C write modes, does not call
providers, does not read or write B2, does not run the frontend, does not mutate
prior evidence, and writes only
`docs/evidence/ps-035c/non-mutating-regression-gate-mode-report.json`. It proves
that `--check-only` leaves `git status` clean (except PS-035C implementation
files) and leaves the SHA-256 digest of the canonical PS-034A report unchanged,
that `--report-out /tmp/...` writes only the requested out-of-tree path, that
`--write-report` is supported for `--current ps034a` and rejected for any
non-PS034A current slice, and that conflicting flags fail before writing.

The PS-034A smoke (`scripts/ps034a_smoke_harness_v1_smoke.py`) was updated to
pass `--write-report` explicitly when it regenerates the canonical tracked
PS-034A report, so no old implicit canonical-report write path survives. The
existing `--current`, `--frontend`, and `--no-frontend` behavior is unchanged.
PS-035C does not renumber or override the existing slice-evidence ownership
rules. PS-035C fixes validation mutation only; it does not prove product
correctness, production security, B2 immutability, tamper-proof storage, real
billing API integration, or billing behavior.

## PS-035D Note (2026-07-02)

PS-035D (Root AGENTS.md Operating Rules) introduces a concise root-level
`AGENTS.md` operating law at the repository root. Future agent sessions must
read the root `AGENTS.md` before any product work; it surfaces (and links, not
copies) the same PS-034A / PS-035C contracts already enforced here. The
no-hidden-Git rule from this harness is unchanged, and the hidden Git flags `h`
and `S` require explicit checking: a checker must read `git ls-files -v` and
fail when `line[0]` is `h` or `S` (a lowercase-only marker check is not
sufficient because it misses the uppercase `S` (skip worktree) flag). PS-035D is local /
static only (no provider calls, no B2 reads, no B2 writes, no frontend run),
does not weaken any PS-034A / PS-035C contract, and does not renumber the
existing slice-evidence ownership rules.

## PS-035 Note (2026-07-02)

PS-035 (Review + Approval Workspace) adds a dedicated
`/review-approval-workspace` route (distinct from the legacy `/review` Review
Room) plus a `ReviewApprovalWorkspace` component and a
`reviewApprovalWorkspace.ts` data module. It is a local / demo-only human
decision surface over accepted local / golden / demo data: a reviewer inspects
a reviewable item, reads its asset / media summary, reads the proof the
pipeline already captured (provenance passport, manifest verification, B2
evidence, rehydrate, export pack), sets one of the four review states
(`pending_review`, `approved`, `rejected`, `needs_changes`), records a rationale
and notes, and reads a local / in-session review ledger.

PS-035 adds a feature smoke
(`scripts/ps035_review_approval_workspace_smoke.py`) that is local / static
only: it reads checked-in files only, does not call providers, does not read or
write B2, does not run the frontend, does not run the backend, does not call
the central regression gate, does not recursively execute another feature
smoke, and writes only
`docs/evidence/ps-035/review-approval-workspace-report.json` under explicit
`--write-evidence`. It supports the standard feature-smoke flags `--check-only`
(default, non-mutating), `--write-evidence`, and `--no-frontend`. It validates
route registration, component + data module presence, the four review states,
the boundary copy, the proof links, no provider / B2 code paths, no forbidden
overclaims, the explicit `h` / `S` hidden Git flag checker over
`git ls-files -v`, absence of the bad lowercase-only hidden-flag command
literal, `git diff --check` cleanliness, and prior-evidence immutability.

PS-035 does not modify this harness, the central regression gate, the shared
smoke library, `AGENTS.md`, `.env*`, `render.yaml`, requirements, or any
PS-034A / PS-034B / PS-035C behavior, and does not renumber or override the
existing slice-evidence ownership rules. PS-035 is additive and writes only its
own evidence. Approval records the reviewer's workflow decision; it does not
prove semantic truth, legal authenticity, C2PA authenticity, human authorship,
Object Lock / tamper-proof storage, or production security. The review ledger is
local / in-session and is not durable, tamper-proof, replicated, or
production-multi-user.
