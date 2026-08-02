# AGENTS.md — ProofStudio Operating Law

This is the operating law every GLM / OpenCode / Codex / agent session inherits
before any ProofStudio product work. It is concise by design: it links the
roadmap, it does not copy it. Authoritative detail lives in the linked docs.

- Master spec plan: specs/07-master-spec-plan.md
- Roadmap slices: specs/08-roadmap-slices.md
- Validation policy: docs/validation/proofstudio-smoke-harness-v1.md
- This law's spec: specs/50-ps-035d-root-agents-operating-rules.md

## 1. Branch base

- the authoritative accepted-base source of truth is the dynamic Git ref origin/accepted/proofstudio, never a hardcoded commit hash
- future ProofStudio branches must start from origin/accepted/proofstudio, not main
- before starting any ProofStudio work, fetch and verify origin/accepted/proofstudio (and the commit it currently resolves to) and build on whatever commit that ref points to at that moment
- do not treat any commit hash written anywhere as the authority; the ref is the authority

## 2. Smoke discipline

- no recursive smokes
- a feature smoke validates only the current slice
- a feature smoke may write only its own evidence; never mutate prior evidence
- future feature-smoke default should be non-mutating local validation
- feature-smoke standard flags: --check-only, --write-evidence, --no-frontend

## 3. Central regression gate

- regression gate is central and non-mutating by default
- normal validation uses --check-only / --report-out
- canonical evidence regeneration requires explicit ownership

Canonical commands:

```
canonical release command: python scripts/proofstudio_regression_gate.py --current <slice> --frontend --report-out /tmp/proofstudio-release-report.json
PS-034A canonical gate report write requires: python scripts/proofstudio_regression_gate.py --current ps034a --write-report
```

## 4. No Git hiding

- no assume-unchanged
- no skip-worktree
- no git update-index
- no update-index
- hidden Git flags h and S must be checked explicitly: read git ls-files -v and fail when line[0] is h or S. A lowercase-only marker check is not sufficient because it misses uppercase `S` skip-worktree; the checker must fail on the uppercase S flag as well as h.

## 5. No workarounds / no leaks

- no guardian / polling workaround
- no broad B2 reads
- no provider calls unless the slice explicitly owns live provider behavior and PM approves
- no secrets printed
- no staging/commit/push unless explicitly instructed after validation

## 6. Truth-boundary red lines

ProofStudio proves what the pipeline did. It does not overclaim.

- do not claim legal authenticity.
- do not claim semantic truth.
- do not claim human authorship.
- do not claim C2PA unless implemented and verified.
- do not claim Object Lock / tamper-proof storage unless implemented and verified.
- do not claim browser-side B2 byte verification unless implemented and verified.
- do not claim public deployment verification unless deployed and tested.
- do not claim enterprise security.
- do not claim actual spend/latency/quota unless captured.
- do not claim provider failures/reruns/variants unless evidenced.
