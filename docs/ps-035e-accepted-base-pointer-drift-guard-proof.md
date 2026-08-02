# PS-035E — Accepted Base Pointer Drift Guard (Proof)

Date: 2026-07-02
Slice: PS-035E — Accepted Base Pointer Drift Guard

## 1. Starting state

- Repo: /home/proofstudio-work/proofstudio
- Branch: ps-035e/accepted-base-pointer-drift-guard
- Starting HEAD: 85aabb153c997af70d2e1d10ff5b589d74710264
- Nothing staged at start.
- No hidden Git flags `h` or `S` present (verified by reading `git ls-files -v`).

## 2. What changed

Only two files were changed, both operating-law / docs files:

- AGENTS.md (root operating law)
- docs/ps-035e-accepted-base-pointer-drift-guard-proof.md (this proof)

No product, backend, frontend, scripts, evidence, env, render, or requirements
files were touched. No provider wrapper, B2 client, or storage path was touched.

## 3. AGENTS.md wording change

The stale hardcoded line was removed:

- removed: `current accepted base commit: 3ad84f770a70d983565b1d3648a01c356a2e55bf`

The dynamic authority was preserved and made explicit. The `Branch base` section
now reads:

- the authoritative accepted-base source of truth is the dynamic Git ref
  origin/accepted/proofstudio, never a hardcoded commit hash
- future ProofStudio branches must start from origin/accepted/proofstudio, not main
- before starting any ProofStudio work, fetch and verify origin/accepted/proofstudio
  (and the commit it currently resolves to) and build on whatever commit that ref
  points to at that moment
- do not treat any commit hash written anywhere as the authority; the ref is the
  authority

No commit hash is mentioned in AGENTS.md as authority. No new hardcoded
"current accepted base commit" line was added. Every other operating-law section
(smoke discipline, central regression gate, no Git hiding, no workarounds / no
leaks, truth-boundary red lines) is preserved unchanged.

## 4. Required preserved / forbidden content

Preserved (present in AGENTS.md):

- `future ProofStudio branches must start from origin/accepted/proofstudio, not main`
- `origin/accepted/proofstudio`
- `fetch`
- `verify`

Removed (absent from AGENTS.md):

- `3ad84f770a70d983565b1d3648a01c356a2e55bf` (the stale commit)
- `current accepted base commit:`

## 5. Behavior boundary

- No product / backend / frontend / scripts / evidence / env / deploy changes.
- No provider calls.
- No B2 reads.
- No B2 writes.
- No frontend run.
- No backend run.
- No evidence mutation.
- No .env edits.
- No staging, commit, or push.
- No hidden Git flags (`h` / `S`).

## 6. Validation commands and results

Run from the repo root on the branch
`ps-035e/accepted-base-pointer-drift-guard`:

1. Verify repo path:
   `pwd` -> /home/proofstudio-work/proofstudio

2. Verify branch:
   `git rev-parse --abbrev-ref HEAD`
   -> ps-035e/accepted-base-pointer-drift-guard

3. Verify starting HEAD:
   `git rev-parse HEAD`
   -> 85aabb153c997af70d2e1d10ff5b589d74710264

4. Verify nothing staged:
   `git status --short` (index) -> clean (no staged entries before edits)

5. Verify changed file set is exactly AGENTS.md and this proof doc:
   `git status --short` lists only these two files.

6. Verify AGENTS.md does NOT contain the stale commit / stale line:
   - `3ad84f770a70d983565b1d3648a01c356a2e55bf` -> absent
   - `3ad84f770a70d983565b1d3648a01c356a2e55bf` (full) -> absent
   - `current accepted base commit:` -> absent

7. Verify AGENTS.md DOES contain the required strings:
   - `future ProofStudio branches must start from origin/accepted/proofstudio, not main` -> present
   - `origin/accepted/proofstudio` -> present
   - `fetch` -> present
   - `verify` -> present

8. Verify forbidden files unchanged:
   no path under `src/**`, `apps/**`, `scripts/**`, `docs/evidence/**`,
   `.env*`, `render.yaml`, or requirements files appears in the diff.

9. Hidden Git flags h/S checker:
   read `git ls-files -v`, inspect `line[0]`, fail when `h` or `S`.
   Result: no line begins with `h` or `S` -> PASS.

10. `git diff --check` -> clean (no whitespace errors).

11. Final `git status` -> only AGENTS.md and this proof doc changed; nothing
    staged.

## 7. Truth boundary

PS-035E only proves that the root operating law no longer hardcodes a stale
accepted-base commit as authority and instead treats the dynamic ref
`origin/accepted/proofstudio` as the source of truth, with an explicit
verify-before-work step. It does not prove product correctness, production
security, B2 immutability, tamper-proof storage, semantic truth, legal
authenticity, C2PA authenticity, human authorship, browser-side B2 byte
verification, deployment readiness, or enterprise security.

## Validation boundary summary

PS-035E is an operating-law documentation repair only. The accepted validation
boundary is:

- no product
- no provider
- no B2
- no evidence
- no frontend
- no backend
