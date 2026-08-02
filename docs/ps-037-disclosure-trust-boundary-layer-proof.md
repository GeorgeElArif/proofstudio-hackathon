# PS-037 — Disclosure & Trust Boundary Layer — Proof

## 1. Status

PS-037 — Disclosure & Trust Boundary Layer is implemented. It adds one reusable
disclosure layer (a canonical data module plus a shared component) and renders
it additively on the core proof surfaces so the boundary language is identical
everywhere proof is shown.

PS-037 is local / static by default. It adds no provider calls, no live B2
reads, no B2 writes, no broad B2 scans, no new backend, no new env variable,
and no deployment change. It does not mutate any prior evidence. PS-037-owned
evidence lives only under `docs/evidence/ps-037/` and is written only when
`--write-evidence` is explicit.

## 2. What this slice proves

ProofStudio proves what the pipeline recorded. The Disclosure & Trust Boundary
layer is a disclosure surface that makes that boundary explicit and identical
on every core proof surface. It is not a legal authenticity system, not a live
B2 verifier, and not a truth system.

The layer states, in one consistent place:

- What ProofStudio proves
- What ProofStudio does not prove
- pipeline-recorded evidence
- local verification
- live verification status
- provider activity status
- B2 evidence status
- reviewer decision boundary
- not claimed
- unknown

## 3. De-escalation pairs (verbatim)

So a judge never mistakes a strong-sounding artifact for a stronger guarantee:

- proof does not equal truth
- workflow approval does not equal legal authenticity
- B2 archive reference does not equal Object Lock
- hash match does not equal semantic truth
- manifest hash does not equal human authorship
- local evidence does not equal live B2 availability
- demo/golden evidence does not equal production security

## 4. Negative boundary strings (verbatim)

The Disclosure & Trust Boundary layer does not claim any of the following. They
are surfaced as non-claims:

- not semantic truth
- not legal authenticity
- not human authorship
- not C2PA authenticity
- not Object Lock
- not tamper-proof
- not browser-side B2 byte verification
- not live B2 availability
- not production security

## 5. Persistent boundary statement

ProofStudio proves what the pipeline recorded. Proof does not equal truth.
Workflow approval does not equal legal authenticity. A B2 archive reference
does not equal Object Lock. A hash match does not equal semantic truth. A
manifest hash does not equal human authorship. Local evidence does not equal
live B2 availability. Demo/golden evidence does not equal production security.

## 6. Implementation files

Shared layer (new):

- `apps/web/src/trustBoundary.ts` — canonical disclosure data module.
- `apps/web/src/TrustBoundaryLayer.tsx` — shared disclosure component
  (`variant="badge"` compact badge, `variant="panel"` expanded panel).

Additive styles (existing file, additive classes only):

- `apps/web/src/styles.css` — `.trust-boundary-layer-*` classes.

Additive renders on the required core proof surfaces (existing files, edited
additively only; no existing per-surface truth-boundary panel is deleted or
weakened):

- `apps/web/src/JudgeCockpitHome.tsx` (Judge Cockpit Home, route `/`)
- `apps/web/src/B2EvidenceExplorer.tsx` (B2 Evidence Explorer, route `/b2-evidence`)
- `apps/web/src/ManifestVerificationPanel.tsx` (Manifest Verification Panel, route `/manifest-verification`)
- `apps/web/src/B2RehydrateComparison.tsx` (B2 Rehydrate Comparison, route `/b2-rehydrate-comparison`)
- `apps/web/src/B2AuditVault.tsx` (Archive / Rehydrate / B2 Audit Vault, route `/b2-audit-vault`)
- `apps/web/src/ReviewApprovalWorkspace.tsx` (Review + Approval Workspace, route `/review-approval-workspace`)
- `apps/web/src/JudgeEvidencePack.tsx` (Judge Evidence Pack, route `/evidence-pack`)
- `apps/web/src/PublicPassportPage.tsx` (Public Provenance Passport, route `/passport/:id`)
- `apps/web/src/App.tsx` (Review Room footer, route `/review`)

Smoke:

- `scripts/ps037_disclosure_trust_boundary_layer_smoke.py`

Evidence (only when `--write-evidence` is explicit):

- `docs/evidence/ps-037/disclosure-trust-boundary-layer-report.json`

## 7. Validation

Feature smoke (non-mutating local validation by default):

```
python scripts/ps037_disclosure_trust_boundary_layer_smoke.py --check-only --no-frontend
python scripts/ps037_disclosure_trust_boundary_layer_smoke.py --write-evidence --no-frontend
```

Central regression gate (contract-only, non-mutating):

```
python scripts/proofstudio_regression_gate.py --current ps037 --no-frontend --report-out /tmp/proofstudio-ps037-regression-report.json
```

Frontend typecheck:

```
cd apps/web && npx tsc --noEmit
```

Hidden Git flags check (explicit `h` / `S` checker over `git ls-files -v`,
failing when `line[0]` is `h` or `S`):

```
git ls-files -v
```

The PS-037 smoke implements the explicit h/S checker and records
`no_hidden_git_flags_h` and `no_hidden_git_flags_S` as separate booleans. It
does not rely on a lowercase-only marker check.

## 8. Truth boundary

ProofStudio proves what the pipeline recorded. The Disclosure & Trust Boundary
layer is not a legal authenticity system, not a live B2 verifier, and not a
truth system. It does not prove semantic truth, legal authenticity, human
authorship, C2PA authenticity, Object Lock / tamper-proof storage,
browser-side B2 byte verification, live B2 availability, production security,
production compliance, legal review, or chain-of-custody guarantees beyond
recorded pipeline evidence.
