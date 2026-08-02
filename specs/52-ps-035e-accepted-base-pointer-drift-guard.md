# PS-035E — Accepted Base Pointer Drift Guard

Status: Spec only.
Base branch: `ps-035e/accepted-base-pointer-drift-guard`
Base commit: `d13f2d1eee699c71e56252209f257a4a5d29a698` (accepted PS-035D /
PS-035)
Date: 2026-07-02

This spec-only commit touches only one file:
`specs/52-ps-035e-accepted-base-pointer-drift-guard.md`. No implementation
files, no root `AGENTS.md`, no scripts, no smoke scripts, no `smoke_lib`, no
regression gate, no evidence, no proof docs, no env files, and no requirements
are changed or performed during this phase. No provider is called, no B2 is
read, and no B2 is written during this phase.

PS-035E is an operating-law docs-repair slice, not a product slice. It specifies
a tiny `AGENTS.md` repair that removes stale hardcoded accepted-base drift and
makes the root operating law safer for future slices. It does not change product
behavior, provider behavior, B2 behavior, or billing behavior.

## 1. Status

PS-035E is currently:

- Spec only.
- Implementation pending.

PS-035E must not be implemented, and no implementation files may be changed,
until this spec is accepted. The latest accepted base is `accepted/proofstudio`
commit `d13f2d1eee699c71e56252209f257a4a5d29a698` (remote
`origin/accepted/proofstudio` is at the same commit).

PS-035E is an operating-law repair slice. It exists to remove the stale
hardcoded accepted-base commit from the root `AGENTS.md` operating law so future
GLM / OpenCode / Codex / agent sessions are not misled by an out-of-date
pointer. This spec-only phase writes only this file. PS-035E must not call live
providers, must not read or write live B2, must not mutate any evidence, and
must not print secrets.

## 2. Purpose

PS-035E makes the authoritative accepted-base pointer the dynamic Git ref
`origin/accepted/proofstudio`, instead of a hardcoded commit hash inside the
root operating law.

Today the root `AGENTS.md` contains a stale hardcoded line:

```
current accepted base commit: 3ad84f770a70d983565b1d3648a01c356a2e55bf
```

That commit was the accepted base at PS-035c time. The real accepted base has
since moved forward to `d13f2d1eee699c71e56252209f257a4a5d29a698`
(post-PS-035D / PS-035). A hardcoded commit in the operating law drifts every
time the accepted line advances, and a stale pointer can mislead a future agent
into building on the wrong base.

The authoritative source of truth must always be the dynamic ref
`origin/accepted/proofstudio`. PS-035E specifies a minimal repair so the
operating law:

- stops hardcoding a commit hash as authority;
- states that future ProofStudio branches must start from
  `origin/accepted/proofstudio`, not `main`;
- requires a session to verify the ref (and its resolved commit) before starting
  work;
- treats any commit hash mentioned in the operating law only as an example or
  last-known value, never as the authority.

## 3. Root Cause

The drift was introduced by PS-035D, which recorded the then-current accepted
base commit `3ad84f770a70d983565b1d3648a01c356a2e55bf` directly inside the root
`AGENTS.md` operating law. That line was accurate at PS-035c acceptance time.
Since then the accepted line has advanced through PS-035D and PS-035, but the
hardcoded line in `AGENTS.md` was not updated. The result is a root operating
law that points at a stale commit while the real accepted ref has moved on.

The deeper root cause is that a commit hash is a poor authority inside an
operating law: it is correct exactly once (the moment it is written) and is
stale on every subsequent acceptance. A dynamic Git ref is correct every time it
is resolved. PS-035E replaces the stale hardcoded authority with the dynamic ref
plus an explicit "verify before work" step.

## 4. Current Accepted Base

The current accepted base for PS-035E is:

- branch: `accepted/proofstudio`
- commit: `d13f2d1eee699c71e56252209f257a4a5d29a698`
- remote: `origin/accepted/proofstudio` is at the same commit
- this is the post-PS-035D / post-PS-035 accepted state

PS-035E must start from `origin/accepted/proofstudio`, not from `main`.

Important: the commit hash above is recorded here as the last-known accepted
value at spec time. It is **not** an authority for future sessions. The
authoritative source of truth is always the dynamic ref
`origin/accepted/proofstudio`. A future session must resolve the ref before
starting work and must use whatever commit the ref resolves to at that moment.

Relevant accepted facts at this base:

- the root `AGENTS.md` operating law already exists at the repository root
  (PS-035D accepted).
- the central regression gate
  (`scripts/proofstudio_regression_gate.py`) supports `--current`,
  `--frontend`, `--no-frontend`, `--check-only`, `--report-out`, and
  `--write-report` (PS-035C accepted) and is non-mutating by default for
  non-PS034A current slices.
- the root `AGENTS.md` still contains the stale hardcoded accepted-base line
  `current accepted base commit: 3ad84f770a70d983565b1d3648a01c356a2e55bf`,
  which is the exact line PS-035E removes.

## 5. Scope

PS-035E is an operating-law docs-repair slice. It edits the root operating law
to remove stale accepted-base drift. It is local / static only and must not
touch the network for providers or B2.

PS-035E must:

1. Update `AGENTS.md` so it no longer hardcodes a stale accepted-base commit as
   authority. The stale line
   `current accepted base commit: 3ad84f770a70d983565b1d3648a01c356a2e55bf`
   must be removed.
2. Prefer wording that says future ProofStudio branches must start from
   `origin/accepted/proofstudio`, not `main`.
3. Require that a session verify the ref `origin/accepted/proofstudio` (and its
   resolved commit) before starting any ProofStudio work.
4. If a commit hash is mentioned at all, it must be explicitly described as an
   example or last-known value, never as the authority. The authoritative source
   of truth is always `origin/accepted/proofstudio`.
5. Preserve the rest of the operating law unchanged: the smoke discipline
   rules, the central regression gate rules, the canonical commands, the
   no-Git-hiding rule, the no-workarounds / no-leaks rules, and the
   truth-boundary red lines.
6. Not introduce any new overclaim, provider call, B2 read, B2 write, evidence
   mutation, hidden Git flag, or staging/commit/push.

## 6. Non-goals

PS-035E must not:

- do not edit the root `AGENTS.md` during the spec-only phase
- do not change the smoke discipline rules
- do not change the central regression gate rules or canonical commands
- do not change the no-Git-hiding rule
- do not change the no-workarounds / no-leaks rules
- do not change the truth-boundary red lines
- do not edit product code under `src/**`
- do not edit frontend code under `apps/**`
- do not edit scripts under `scripts/**` (including `smoke_lib.py` and
  `scripts/proofstudio_regression_gate.py`)
- do not edit evidence under `docs/evidence/**`
- do not edit `.env*`
- do not edit `render.yaml`
- do not edit requirements files
- do not run the frontend
- do not call providers
- do not read or write B2 (no B2 reads, no B2 writes)
- do not stage, commit, or push unless explicitly instructed after validation
- do not use hidden Git flags (`assume-unchanged`, `skip-worktree`,
  `git update-index`, `update-index`)
- do not add a new provider
- do not change the golden demo canonical constants
- do not change the historical contracts the gate verifies
- do not introduce a control name containing `KEY`, `TOKEN`, or `SECRET`
- do not claim product correctness, production security, B2 immutability,
  tamper-proof storage, semantic truth, legal authenticity, C2PA authenticity,
  human authorship, browser-side B2 byte verification, deployment readiness, or
  enterprise security

PS-035E only edits this spec file in the spec-only phase.
Implementation-phase candidate files are listed in section 7.

## 7. Implementation Candidate Files

The following are implementation-phase candidates only, clearly marked as
implementation-phase only. They are **not** for this spec-only commit:

- `AGENTS.md` (at repository root) — the primary repair target. The
  implementation phase removes the stale hardcoded accepted-base line and
  replaces the accepted-base section with wording that:
  - keeps `future ProofStudio branches must start from origin/accepted/proofstudio, not main`;
  - keeps `origin/accepted/proofstudio`;
  - states that a session must verify the ref `origin/accepted/proofstudio`
    (and its resolved commit) before starting work;
  - does not contain the stale commit `3ad84f770a70d983565b1d3648a01c356a2e55bf`;
  - if any commit hash is mentioned, describes it only as an example or
    last-known value, not as the authority.
- PS-035E spec / proof / status docs only, if needed:
  - `specs/07-master-spec-plan.md` — implementation-phase cross-reference only
    (register PS-035E acceptance). Must not change any historical item or
    golden constant.
  - `specs/08-roadmap-slices.md` — implementation-phase status update only.

Any edit to `AGENTS.md` is the implementation phase actually performing the
operating-law repair. It must keep the operating law concise, must preserve
every other section verbatim, and must contain every required string in
section 9. It must not introduce forbidden overclaims.

Any edit to `specs/07-master-spec-plan.md` or `specs/08-roadmap-slices.md` is
the implementation phase registering PS-035E as an accepted operating-law
repair slice and must not change any historical roadmap item or golden
constant.

PS-035E implementation must not edit `scripts/**`, `src/**`, `apps/**`, or any
evidence file.

## 8. Forbidden Files

PS-035E implementation must not touch:

- `src/**`
- `apps/**`
- `scripts/**` (including `scripts/smoke_lib.py` and
  `scripts/proofstudio_regression_gate.py`)
- any provider wrapper under `src/proofstudio/providers/**`
- any B2 client / storage path
- `docs/evidence/**`
- `.env*`
- `render.yaml`
- requirements files

The only implementation-phase files allowed are `AGENTS.md` plus the PS-035E
spec / proof / status docs in section 7 (`specs/07-master-spec-plan.md`,
`specs/08-roadmap-slices.md`) if needed. Any other path requires explicit PM
approval.

## 9. Validation Contract

PS-035E implementation must be validated with local / static validation only.
No provider calls, no B2 reads, no B2 writes, no frontend run, no evidence
mutation.

### 9.1 Stale commit guard

- verify `AGENTS.md` does **not** contain the stale commit
  `3ad84f770a70d983565b1d3648a01c356a2e55bf`. The check must fail if that
  string appears anywhere in `AGENTS.md`.

### 9.2 Dynamic-ref authority

- verify `AGENTS.md` contains `origin/accepted/proofstudio`.
- verify `AGENTS.md` contains the verbatim branch rule
  `future ProofStudio branches must start from origin/accepted/proofstudio, not main`.
- verify `AGENTS.md` requires a session to verify the ref
  `origin/accepted/proofstudio` (and its resolved commit) before starting work.
- if a commit hash is mentioned in `AGENTS.md`, verify it is described only as
  an example or last-known value, not as the authority.

### 9.3 Hidden Git flags guard

- verify no hidden Git flags `h` and `S` with an explicit h/S checker:
  read `git ls-files -v`, inspect `line[0]`, and fail when the marker is `h`
  (assume-unchanged) or `S` (skip-worktree). Do not use a lowercase-only grep
  marker check as the final check because it misses uppercase `S` skip-worktree.
  The checker must fail on the uppercase `S` flag as well as `h`.

### 9.4 Scope guard

- verify the implementation touches only `AGENTS.md` and, if needed, the
  PS-035E spec / proof / status docs listed in section 7
  (`specs/07-master-spec-plan.md`, `specs/08-roadmap-slices.md`).
- verify no product, app, backend, provider, B2, evidence, env, render,
  requirements, `smoke_lib`, or central gate files are touched. Specifically
  the diff must not contain any path under `src/**`, `apps/**`, `scripts/**`,
  `docs/evidence/**`, `.env*`, `render.yaml`, or requirements files.

### 9.5 Hygiene guards

- verify no evidence mutation: `git status` must show no evidence file changed.
- verify the implementation branch starts from `origin/accepted/proofstudio`
  (the branch's merge-base with `origin/accepted/proofstudio` must equal the
  accepted base commit).
- `git diff --check` returns clean.
- final `git status` is exact: only `AGENTS.md` and (if edited)
  `specs/07-master-spec-plan.md` / `specs/08-roadmap-slices.md` may appear.
- no false claims of product correctness, production security, B2 immutability,
  tamper-proof storage, semantic truth, legal authenticity, C2PA authenticity,
  human authorship, browser-side B2 byte verification, deployment readiness, or
  enterprise security (no forbidden overclaims).
- PS-035E implementation performs no provider calls, no B2 reads, and no B2
  writes.

### Verbatim required validation strings

The PS-035E implementation and validation must preserve these exact strings so
the repair contract is deterministic and not dependent on close-enough wording:

- `origin/accepted/proofstudio`
- `future ProofStudio branches must start from origin/accepted/proofstudio, not main`
- `3ad84f770a70d983565b1d3648a01c356a2e55bf` (must be absent from `AGENTS.md`)
- hidden Git flags h and S
- `git ls-files -v`

## 10. Acceptance Criteria

PS-035E (spec-only phase) is accepted only when:

- this spec exists at `specs/52-ps-035e-accepted-base-pointer-drift-guard.md`
- only this spec file is changed in the spec-only phase
- the branch `ps-035e/accepted-base-pointer-drift-guard` starts from
  `origin/accepted/proofstudio` at commit
  `d13f2d1eee699c71e56252209f257a4a5d29a698` (the merge-base equals that
  commit)
- the repair purpose, root cause, and scope are explicit
- the stale commit `3ad84f770a70d983565b1d3648a01c356a2e55bf` is identified as
  the exact line to remove
- the dynamic ref `origin/accepted/proofstudio` is identified as the authority
- the validation contract (section 9) covers the stale-commit guard, the
  dynamic-ref authority, the hidden-Git-flags `h` / `S` checker, the scope
  guard, and the hygiene guards
- the truth boundary (section 12) is explicit
- no evidence mutation occurs in this phase
- no hidden Git flags `h` or `S` are present (verified by the explicit h/S
  checker over `git ls-files -v`)
- `git diff --check` is clean
- no staging, commit, or push occurs until PM approval

Implementation-phase acceptance (for reference, not this phase) additionally
requires: `AGENTS.md` no longer contains
`3ad84f770a70d983565b1d3648a01c356a2e55bf`; `AGENTS.md` still contains
`origin/accepted/proofstudio` and
`future ProofStudio branches must start from origin/accepted/proofstudio, not main`;
`AGENTS.md` requires verifying the ref before work; every other operating-law
section is preserved verbatim; no product, app, backend, provider, B2,
evidence, env, render, requirements, `smoke_lib`, or central gate file is
touched; no hidden Git flag `h` or `S` is present; `git diff --check` is clean;
no provider call, no B2 read, no B2 write occurs; no forbidden overclaim is
introduced.

## 11. Rollback

Rollback of the PS-035E spec-only phase is a single revert of the PS-035E spec
commit, because only `specs/52-ps-035e-accepted-base-pointer-drift-guard.md` is
changed in this phase.

Future implementation rollback must restore the pre-PS-035E state of the edited
files in section 7. Specifically, if PS-035E implementation turns out to
introduce a forbidden overclaim, a scope violation, or an edited forbidden file,
rollback must restore:

- revert `AGENTS.md` to its pre-PS-035E state (the stale hardcoded line would
  reappear; that is acceptable only as part of a clean revert, not as a target
  state)
- revert `specs/07-master-spec-plan.md` and `specs/08-roadmap-slices.md` to
  their pre-PS-035E state if they were edited

Rollback of PS-035E must not touch any evidence under `docs/evidence/**`, must
not touch `scripts/**`, `src/**`, `apps/**`, `.env*`, `render.yaml`, or
requirements files.

Because PS-035E is intentionally scoped to a tiny operating-law repair plus
light documentation cross-references, rollback is isolated, reversible, and
does not require touching product UI, providers, deployment topology, product
code, frontend code, env files, or deployment config.

## 12. Truth Boundary

ProofStudio proves what the pipeline did.

PS-035E edits the operating law's accepted-base pointer only. It does not prove
product correctness, production security, B2 immutability, tamper-proof storage,
real billing API integration, billing behavior, semantic truth, legal
authenticity, C2PA authenticity, human authorship, browser-side B2 byte
verification, deployment readiness, enterprise security, or CI enforcement.

PS-035E does not prove:

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

PS-035E only proves that the root operating law (`AGENTS.md`) no longer
hardcodes a stale accepted-base commit as authority and instead treats the
dynamic ref `origin/accepted/proofstudio` as the source of truth, with an
explicit verify-before-work step and the existing hidden-Git-flags, evidence,
and truth-boundary rules preserved.

PS-035E must preserve this boundary verbatim across `AGENTS.md` and any
cross-reference doc. No PS-035E artifact may imply product correctness,
production security, B2 immutability, tamper-proof storage, real billing API
integration, billing behavior, semantic truth, legal authenticity, C2PA
authenticity, human authorship, browser-side B2 byte verification, deployment
readiness, enterprise security, or CI enforcement.

## Verbatim audit contract strings

The PS-035E implementation and validation must preserve these exact strings so
the guard is deterministic and not dependent on close-enough wording:

- Root cause
- Implementation candidate files
- Forbidden files
- Validation contract
- Acceptance criteria
- Truth boundary
- no backend
- no commit
- no push
