# PS-035D — Root AGENTS.md Operating Rules

Status: Spec only.
Base branch: `ps-035d/root-agents-operating-rules`
Base commit: `3ad84f770a70d983565b1d3648a01c356a2e55bf` (accepted PS-035c)
Date: 2026-07-02

This spec-only commit touches only one file:
`specs/50-ps-035d-root-agents-operating-rules.md`. No implementation files, no
root `AGENTS.md`, no scripts, no smoke scripts, no `smoke_lib`, no regression
gate, no evidence, no proof docs, no env files, and no requirements are changed
or performed during this phase. No provider is called, no B2 is read, and no B2
is written during this phase.

PS-035D is an operating-rules slice, not a product slice. It adds a minimal
root-level `AGENTS.md` contract so that future GLM / OpenCode / Codex / agent
sessions inherit the validation, evidence, branch, truth-boundary, and
anti-recursion rules before starting the PS-035 Review + Approval Workspace. It
does not change product behavior, provider behavior, B2 behavior, or billing
behavior.

## 1. Status

PS-035D is currently:

- Spec only.
- Implementation pending.

PS-035D must not be implemented, and no implementation files may be changed,
until this spec is accepted. The latest accepted base is `accepted/proofstudio`
commit `3ad84f770a70d983565b1d3648a01c356a2e55bf`.

PS-035D is the next operating-rules slice after PS-035c. It exists to make the
accumulated PS-034A / PS-035c validation, evidence, branch, truth-boundary, and
anti-recursion rules inheritable by every future agent session before any
further product work begins. This spec-only phase writes only this file.
PS-035D must not call live providers, must not read or write live B2, must not
mutate any evidence, and must not print secrets.

## 2. Purpose

PS-035D introduces a minimal root-level `AGENTS.md` operating law at the
repository root. The goal is that any future GLM / OpenCode / Codex / agent
session, on first load, inherits the same operating rules that the PS-034A and
PS-035c slices already enforce through smoke scripts and the central regression
gate.

Today those rules live inside `scripts/smoke_lib.py`,
`scripts/proofstudio_regression_gate.py`, the PS-034A spec, the PS-035c spec,
and `docs/validation/proofstudio-smoke-harness-v1.md`. A fresh agent session
does not always read those files before starting work, so it can repeat the
exact failure modes PS-034A was created to stop: recursive smoke chains,
hidden Git-index workarounds, prior-evidence mutation, repeated frontend
builds, broad B2 reads, unapproved provider calls, and overclaims.

PS-035D closes that gap by defining a concise root-level operating contract that
an agent inherits immediately, without having to discover the validation
harness first.

PS-035D is the last slice before the PS-035 Review + Approval Workspace. It
exists so the review workspace opens on a repo whose operating law is already
inheritable, not negotiable per-session.

## 3. Why AGENTS.md Now

The PS-035c non-mutating regression gate mode is now accepted at base commit
`3ad84f7`. The validation, evidence, branch, truth-boundary, and anti-recursion
rules are now stable and proven by the PS-034A and PS-035c smokes.

Until now those rules were enforced reactively: a session would start work,
the smoke harness would then catch a violation, and the session would have to
re-run after a manual restore. That is expensive, slow, and brittle. It also
relies on every agent re-discovering the same rules independently.

A root `AGENTS.md` makes those rules proactive and inheritable. OpenCode, Codex,
and similar agents read a root `AGENTS.md` on session start by convention. By
putting the operating law there, a new session starts already bound to the
correct branch base, the non-mutating gate, the feature-smoke scope rules, the
truth boundary, and the no-hidden-Git rule, before it writes a single file.

PS-035D does this now, rather than later, because:

- the rules are stable after PS-035c (the gate is already non-mutating);
- the next phase is the PS-035 Review + Approval Workspace, which will involve
  review/approval flows that must not regress the operating discipline; and
- deferring the root contract any further risks a new session silently
  violating a rule that only the smoke harness would catch after the fact.

PS-035D adds the root operating instructions only. It does not itself prove
product correctness, production security, or any truth-boundary claim (see
section 14).

## 4. Current Accepted Base

The current accepted base is:

- branch: `accepted/proofstudio`
- commit: `3ad84f770a70d983565b1d3648a01c356a2e55bf`
- remote: `origin/accepted/proofstudio` is at the same commit
- this is the post-PS-035c accepted state

Relevant accepted facts at this base:

- `scripts/proofstudio_regression_gate.py` already supports `--current`,
  `--frontend`, `--no-frontend`, `--check-only`, `--report-out`, and
  `--write-report` (PS-035c accepted).
- the gate is already non-mutating by default for non-PS034A current slices
  (PS-035c accepted).
- `docs/validation/proofstudio-smoke-harness-v1.md` exists and documents the
  PS-034A smoke harness v1 architecture (PS-034A accepted).
- there is no `AGENTS.md` at the repository root today. PS-035D introduces it.
- `scripts/smoke_lib.py` provides the shared smoke helpers, including the
  no-hidden-Git-flags and prior-evidence-clean checks.

## 5. Scope

PS-035D is an operating-rules slice. It adds the root-level `AGENTS.md`
contract and updates the documentation that references it. It is local/static
only and must not touch the network for providers or B2.

PS-035D must:

1. Introduce a concise root-level `AGENTS.md` at the repository root that future
   GLM / OpenCode / Codex / agent sessions inherit on session start.
2. Codify the accepted-base branch rule: future ProofStudio branches must start
   from `origin/accepted/proofstudio`, not from `main`.
3. Record the current accepted base commit
   `3ad84f770a70d983565b1d3648a01c356a2e55bf`.
4. Forbid recursive smoke chains and repeated frontend builds through nested
   smokes.
5. State that a feature smoke validates only the current slice and may write
   only its own evidence.
6. State that the future feature-smoke default should be non-mutating local
   validation, and define the standard feature-smoke flags `--check-only`,
   `--write-evidence`, and `--no-frontend`.
7. State that the central regression gate is the single release-readiness gate
   and is non-mutating by default.
8. Give the canonical release command and the canonical normal-validation
   command.
9. State that canonical evidence regeneration requires explicit ownership, and
   give the canonical PS-034A regeneration command.
10. Forbid hidden Git index manipulation (assume-unchanged, skip-worktree,
    `git update-index` / `update-index`) and require the hidden-Git-flags `h`
    and `S` to be checked.
11. Forbid guardian / polling workarounds.
12. Forbid broad B2 reads.
13. Forbid provider calls unless the slice explicitly owns live provider
    behavior and the PM approves.
14. Forbid printing secrets.
15. Forbid staging, committing, or pushing unless explicitly instructed after
    validation.
16. Preserve the truth-boundary red lines verbatim (section 14).
17. Keep the root `AGENTS.md` concise. It is an operating law, not a duplicate
    roadmap. The roadmap lives in `specs/07-master-spec-plan.md` and
    `specs/08-roadmap-slices.md`; `AGENTS.md` links to them, it does not copy
    them.

## 6. Non-goals

PS-035D must not:

- do not implement the root `AGENTS.md` during the spec-only phase
- do not edit product code under `src/**`
- do not edit frontend code under `apps/**`
- do not edit scripts
- do not edit evidence
- do not run frontend
- do not call providers
- do not read or write B2 (no B2 reads, no B2 writes)
- do not stage, commit, or push unless explicitly instructed after validation
- do not use hidden Git flags (`assume-unchanged`, `skip-worktree`,
  `git update-index`, `update-index`)
- do not claim product correctness, production security, B2 immutability,
  tamper-proof storage, or billing behavior
- do not claim semantic truth, legal authenticity, C2PA authenticity, or human
  authorship
- do not add a new provider
- do not change the golden demo canonical constants
- do not change the historical contracts the gate verifies
- do not introduce a control name containing `KEY`, `TOKEN`, or `SECRET`
- do not duplicate the roadmap into `AGENTS.md`
- do not make forbidden overclaims

PS-035D only edits this spec file in the spec-only phase.
Implementation-phase candidates are listed in section 8.

## 7. Spec-only Allowed File

This spec-only commit touches only:

- `specs/50-ps-035d-root-agents-operating-rules.md`

No other files are changed during the spec-only phase. No root `AGENTS.md`, no
scripts, no smoke scripts, no `smoke_lib`, no regression gate, no evidence, no
proof docs, no env files, and no requirements are changed.

## 8. Recommended Implementation Files

The following are implementation-phase candidates only, clearly marked as
implementation-phase only. They are not for this spec-only commit:

- `AGENTS.md` (new, at repository root)
- `specs/07-master-spec-plan.md`
- `specs/08-roadmap-slices.md`
- `docs/validation/proofstudio-smoke-harness-v1.md`

Any edit to `AGENTS.md` is the implementation phase actually creating the
root operating law. It must be concise, must link (not copy) the roadmap and
the validation doc, and must contain every required string in section 11. It
must not introduce forbidden overclaims.

Any edit to `specs/07-master-spec-plan.md` or `specs/08-roadmap-slices.md` is
the implementation phase registering PS-035D as an accepted operating-rules
slice and must not change any historical roadmap item or golden constant.

Any edit to `docs/validation/proofstudio-smoke-harness-v1.md` is the
implementation phase cross-referencing the root `AGENTS.md` from the smoke
harness doc, and must not weaken any existing PS-034A / PS-035c contract.

PS-035D implementation must not edit `scripts/**`, `src/**`, `apps/**`, or any
evidence file.

## 9. Forbidden Files Unless PM-approved Later

PS-035D implementation must not touch:

- `src/**`
- `apps/**`
- `scripts/**`
- `docs/evidence/**`
- `.env*`
- `render.yaml`
- requirements files

The only implementation-phase files allowed without PM approval are the four in
section 8 (`AGENTS.md`, `specs/07-master-spec-plan.md`,
`specs/08-roadmap-slices.md`, `docs/validation/proofstudio-smoke-harness-v1.md`).
Any other path requires explicit PM approval.

## 10. Root AGENTS.md Contract

PS-035D defines the following contract for the root-level `AGENTS.md`.

- It lives at the repository root (`AGENTS.md`), so OpenCode / Codex / agent
  sessions inherit it on session start by convention.
- It is concise. It is an operating law, not a duplicate roadmap. The roadmap
  lives in `specs/07-master-spec-plan.md` and `specs/08-roadmap-slices.md`;
  `AGENTS.md` links to them, it does not reproduce them.
- It is machine-inheritable: every required string in section 11 must appear
  verbatim so a session (or a validator) can grep for them.
- It does not introduce any claim outside the truth boundary (section 14). It
  must not claim product correctness, production security, B2 immutability,
  tamper-proof storage, semantic truth, legal authenticity, C2PA authenticity,
  human authorship, browser-side B2 byte verification, deployment readiness, or
  enterprise security.
- It does not override or weaken any existing PS-034A / PS-035c contract. It
  surfaces those contracts at the root; it does not replace them.
- It points at the canonical commands (section 11) verbatim, so a session never
  has to guess the release or validation invocation.
- It forbids hidden Git index manipulation and the guardian/polling workaround
  verbatim.
- It forbids staging, committing, or pushing unless explicitly instructed after
  validation.

## 11. Required AGENTS.md Content

The root `AGENTS.md` created in the implementation phase must contain at least
the following content. Each item below must appear verbatim (or as a verbatim
quoted command) so that it is greppable and inheritable.

Accepted base rule:

- future ProofStudio branches must start from `origin/accepted/proofstudio`,
  not from `main`.

Current accepted base commit:

- `3ad84f770a70d983565b1d3648a01c356a2e55bf`

Smoke discipline rules:

- no recursive smokes. A feature smoke must not recursively execute another
  smoke.
- a feature smoke validates only the current slice.
- a feature smoke may write only its own evidence; it must not mutate prior or
  historical evidence.
- the future feature-smoke default should be non-mutating local validation.
- the future feature-smoke standard flags are:
  `--check-only`
  `--write-evidence`
  `--no-frontend`

Central regression gate rules:

- the regression gate is central and non-mutating by default.
- the canonical release command is:
  `python scripts/proofstudio_regression_gate.py --current <slice> --frontend --report-out /tmp/proofstudio-release-report.json`
- normal validation uses `--check-only` / `--report-out`.
- canonical evidence regeneration requires explicit ownership.
- the PS-034A canonical gate report write requires:
  `python scripts/proofstudio_regression_gate.py --current ps034a --write-report`

No Git hiding:

- no `assume-unchanged`.
- no `skip-worktree`.
- no `git update-index`.
- no `update-index`.
- hidden Git flags h and S must be checked explicitly. Do not use
  a lowercase-only grep marker check as the final check because it misses
  uppercase `S` skip-worktree. Use a checker that reads `git ls-files -v` and
  fails when `line[0]` is `h` or `S`.

No workarounds / no leaks:

- no guardian / polling workaround.
- no repeated frontend builds (no nested frontend typecheck/build chains).
- no broad B2 reads.
- no provider calls unless the slice explicitly owns live provider behavior and
  the PM approves.
- no secrets printed.
- no staging, committing, or pushing unless explicitly instructed after
  validation.

Truth-boundary red lines (must appear verbatim):

- do not claim legal authenticity.
- do not claim semantic truth.
- do not claim human authorship.
- do not claim C2PA unless implemented and verified.
- do not claim Object Lock / tamper-proof storage unless implemented and
  verified.
- do not claim browser-side B2 byte verification unless implemented and
  verified.
- do not claim public deployment verification unless deployed and tested.
- do not claim enterprise security.
- do not claim actual spend / latency / quota unless captured.
- do not claim provider failures / reruns / variants unless evidenced.


### Verbatim required AGENTS.md strings

The implementation-phase `AGENTS.md` must include these exact strings so future
audit checks are deterministic and do not depend on close-enough wording:

- hidden Git flags h and S
- no staging/commit/push
- do not claim Object Lock / tamper-proof storage unless implemented and verified
- do not claim browser-side B2 byte verification unless implemented and verified
- do not claim actual spend/latency/quota unless captured
- do not claim provider failures/reruns/variants unless evidenced

## 12. Validation Plan

PS-035D implementation must be validated with local/static validation only. No
provider calls, no B2 reads, no B2 writes, no frontend run.

- verify the implementation branch starts from `origin/accepted/proofstudio`
  (the branch's merge-base with `origin/accepted/proofstudio` must equal the
  accepted base commit).
- verify `AGENTS.md` exists at the repository root.
- verify `AGENTS.md` is concise and is not a duplicate of the roadmap (it links
  to `specs/07-master-spec-plan.md` and `specs/08-roadmap-slices.md` rather
  than copying them).
- verify every required string in section 11 is present in `AGENTS.md`
  (greppable check for each item).
- verify forbidden files are unchanged: `src/**`, `apps/**`, `scripts/**`,
  `docs/evidence/**`, `.env*`, `render.yaml`, requirements files must not
  appear in the implementation diff.
- verify no evidence mutation: `git status` must show no evidence file changed.
- verify no hidden Git flags h or S with an explicit h/S checker:
  read `git ls-files -v`, inspect `line[0]`, and fail when the marker is `h`
  (assume-unchanged) or `S` (skip-worktree). Do not use
  a lowercase-only grep marker check as the final check because it misses
  uppercase `S`.
- `git diff --check` returns clean.
- final `git status` is exact: only `AGENTS.md`, `specs/07-master-spec-plan.md`,
  `specs/08-roadmap-slices.md`, and
  `docs/validation/proofstudio-smoke-harness-v1.md` may appear (and only those
  that were actually edited).
- no false claims of product correctness, production security, B2 immutability,
  tamper-proof storage, real billing API integration, billing behavior,
  semantic truth, legal authenticity, C2PA authenticity, human authorship,
  browser-side B2 byte verification, deployment readiness, or enterprise
  security (no forbidden overclaims).
- PS-035D implementation performs no provider calls, no B2 reads, and no B2
  writes.

## 13. Evidence Model

PS-035D is an operating-rules slice and does not introduce a new tracked
feature-smoke evidence report or a new proof doc in the spec-only phase.

The acceptance evidence for PS-035D is the combination of:

- this spec file (accepted);
- the future root `AGENTS.md` existing at the repository root and containing
  every required string in section 11; and
- the final `git status` / `git diff --check` / hidden-Git-flags check being
  clean during implementation validation.

A future PS-035D implementation may optionally add
`docs/evidence/ps-035d/root-agents-operating-rules-report.json` with measured
fields such as:

- `ok`
- `slice_id: ps035d`
- `checked_at`
- `agents_md_exists_at_root`
- `required_strings_present`
- `agents_md_is_concise`
- `forbidden_files_unchanged`
- `no_evidence_mutation`
- `no_hidden_git_flags_h`
- `no_hidden_git_flags_S`
- `git_diff_check_clean`
- `truth_boundary_preserved`
- `no_forbidden_overclaims`
- `no_provider_calls`
- `no_b2_reads`
- `no_b2_writes`
- `failures`

`ok` is true only when every measured field is truthful and no forbidden
overclaim or forbidden file change is present. `failures` must be empty on
acceptance. This evidence file is optional and is not required for the
spec-only phase.

## 14. Truth Boundary

ProofStudio proves what the pipeline did.

PS-035D adds agent operating instructions only. It does not prove product
correctness, production security, B2 immutability, tamper-proof storage, real
billing API integration, billing behavior, semantic truth, legal authenticity,
C2PA authenticity, human authorship, browser-side B2 byte verification,
deployment readiness, or CI enforcement.

PS-035D does not prove:

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
- deployment readiness
- enterprise security
- CI enforcement

PS-035D only proves that the root operating law (`AGENTS.md`) exists and states
the accepted-base branch rule, the non-mutating gate rules, the feature-smoke
scope rules, the no-hidden-Git rule, the truth-boundary red lines, and the
canonical commands.

PS-035D must preserve this boundary verbatim across `AGENTS.md` and any
optional evidence report. No PS-035D artifact may imply product correctness,
production security, B2 immutability, tamper-proof storage, real billing API
integration, billing behavior, semantic truth, legal authenticity, C2PA
authenticity, human authorship, browser-side B2 byte verification, deployment
readiness, enterprise security, or CI enforcement.

## 15. Risks

PS-035D must record the following risks with mitigations:

- agent does not inherit the law
  - risk: a future session starts on `main` or ignores the operating rules and
    repeats a PS-034A-era violation (recursive smoke, hidden Git flag,
    evidence mutation, broad B2 read, unapproved provider call).
  - mitigation: PS-035D places the law at the repository root `AGENTS.md`,
    states the `origin/accepted/proofstudio` branch rule and the current base
    commit, and makes every required string greppable.
- roadmap duplication drift
  - risk: `AGENTS.md` copies the roadmap and then drifts out of sync with
    `specs/07-master-spec-plan.md` / `specs/08-roadmap-slices.md`.
  - mitigation: the contract requires `AGENTS.md` to be concise and to link
    (not copy) the roadmap; section 12 validates that it is not a duplicate.
- overclaim drift
  - risk: `AGENTS.md` or a future artifact describes ProofStudio as proving
    product correctness, production security, B2 immutability, C2PA, Object
    Lock, semantic truth, legal authenticity, human authorship, deployment
    readiness, or enterprise security.
  - mitigation: preserve the truth boundary verbatim in section 14 and in
    `AGENTS.md`; report `no_forbidden_overclaims`.
- secret-safety drift
  - risk: `AGENTS.md` introduces a control name containing `KEY`, `TOKEN`, or
    `SECRET`, or otherwise leaks secrets.
  - mitigation: PS-035D must not introduce control names containing `KEY`,
    `TOKEN`, or `SECRET`, and must not print secrets.
- hidden Git flags reintroduced
  - risk: a session uses `assume-unchanged`, `skip-worktree`, or
    `git update-index` / `update-index` to mask a dirty tree and the violation
    is not caught.
  - mitigation: the root law forbids these verbatim and requires hidden Git
    flags h and S to be checked with an explicit h/S checker that reads
    `git ls-files -v` and fails when `line[0]` is `h` or `S`.
- scope creep
  - risk: PS-035D implementation edits product code, scripts, or evidence.
  - mitigation: section 9 forbids those paths; section 12 verifies forbidden
    files are unchanged.

## 16. Acceptance Criteria

PS-035D is accepted only when:

- the PS-035D spec exists (this document, accepted)
- only the spec file is changed in the spec-only phase
- the accepted-base branch rule is documented (future branches start from
  `origin/accepted/proofstudio`, not `main`)
- the current accepted base commit `3ad84f770a70d983565b1d3648a01c356a2e55bf`
  is recorded
- the smoke discipline rules are documented (no recursive smokes; feature
  smoke validates only the current slice; feature smoke writes only its own
  evidence)
- the future feature-smoke default (non-mutating local validation) and the
  standard feature-smoke flags (`--check-only`, `--write-evidence`,
  `--no-frontend`) are documented
- the central regression gate is documented as central and non-mutating by
  default
- the canonical release command is documented verbatim
  (`python scripts/proofstudio_regression_gate.py --current <slice> --frontend --report-out /tmp/proofstudio-release-report.json`)
- the canonical normal-validation invocation is documented (`--check-only` /
  `--report-out`)
- the canonical PS-034A regeneration command is documented verbatim
  (`python scripts/proofstudio_regression_gate.py --current ps034a --write-report`)
- the no-Git-hiding rule is documented (`assume-unchanged`, `skip-worktree`,
  `git update-index`, `update-index`, and the `h` / `S` flags)
- the guardian/polling workaround, repeated frontend builds, broad B2 reads,
  unapproved provider calls, secret printing, and unapproved staging/commit/
  push are forbidden
- the truth-boundary red lines are documented verbatim
- the truth boundary is preserved (PS-035D adds operating instructions only; it
  does not prove product correctness, production security, B2 immutability,
  tamper-proof storage, real billing API integration, billing behavior,
  semantic truth, legal authenticity, C2PA authenticity, human authorship,
  browser-side B2 byte verification, deployment readiness, enterprise security,
  or CI enforcement)
- PS-035D performs no provider calls, no B2 reads, and no B2 writes
- no implementation files are changed during the spec-only phase
- commit and push are required before acceptance

## 17. Rollback

Rollback of the PS-035D spec-only phase is a single revert of the PS-035D spec
commit, because only this spec file is changed in this phase.

Future implementation rollback must restore the pre-PS-035D state of the edited
files in section 8. Specifically, if PS-035D implementation turns out to
introduce a forbidden overclaim, a roadmap duplication, or an edited forbidden
file, rollback must restore:

- remove `AGENTS.md` from the repository root (it did not exist before PS-035D)
- restore `specs/07-master-spec-plan.md` and `specs/08-roadmap-slices.md` to
  their pre-PS-035D state if they were edited
- restore `docs/validation/proofstudio-smoke-harness-v1.md` to its pre-PS-035D
  state if it was edited
- remove the optional
  `docs/evidence/ps-035d/root-agents-operating-rules-report.json` if it was
  added

Rollback of PS-035D must not touch any evidence under `docs/evidence/**` other
than the optional PS-035D report, must not touch `scripts/**`, `src/**`,
`apps/**`, `.env*`, `render.yaml`, or requirements files.

Because PS-035D is intentionally scoped to a root operating law plus light
documentation cross-references, rollback is isolated, reversible, and does not
require touching product UI, providers, deployment topology, product code,
frontend code, env files, or deployment config.
