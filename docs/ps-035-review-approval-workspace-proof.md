# PS-035 — Review + Approval Workspace (Proof)

Status: Implemented on branch `ps-035/review-approval-workspace`, starting from
`origin/accepted/proofstudio` at commit
`964cc404fe1fa6a0f046b5130aa01b2425a1d7df`.

Spec: `specs/51-ps-035-review-approval-workspace.md`.

## 1. What PS-035 ships

PS-035 adds a dedicated Review + Approval Workspace: a local / demo-only human
decision surface over the existing ProofStudio proof chain. A reviewer opens a
reviewable item from accepted local / golden / demo data, reads its asset /
media summary, reads the proof the pipeline already captured, sets a review
state, records a rationale and notes, and reads the local approval trail.

It is distinct from the legacy `/review` Review Room (PS-013 / PS-014 live
operator flow), which stays unchanged.

## 2. Surface identity

- Route: `/review-approval-workspace` (registered in `apps/web/src/App.tsx` via
  `isReviewApprovalWorkspacePath()` and
  `<ReviewApprovalWorkspace variant="page" />`).
- Component: `apps/web/src/ReviewApprovalWorkspace.tsx`
  (`variant="page"`, same convention as every other surface).
- Data module: `apps/web/src/reviewApprovalWorkspace.ts` (camelCase, same
  convention as `judgeEvidencePack.ts`, `lineageComparisonLab.ts`, etc.).
- Nav link: a CTA tile + golden-run row link in
  `apps/web/src/JudgeCockpitHome.tsx`.
- Styles: minimal additive classes in `apps/web/src/styles.css`.

## 3. Data source

All reviewable-item data is sourced read-only from accepted checked-in demo
data:

- `docs/evidence/demo/golden-demo-run.json` (run_id, campaign_id, archive_uri,
  archive_sha256, manifest_uri, manifest_hash, rehydrate_source,
  provider_calls_during_rehydrate, no_live_provider_call_during_rehydrate).

The single reviewable item is the golden-run archive. The data module records
golden values verbatim; the PS-035 smoke verifies they match the manifest.

Honesty: the checked-in evidence does not capture a provider/model for the
golden asset, the raw media bytes, the asset size, or a human reviewer
identity. PS-035 records those as "not captured in checked-in evidence". No
verified status, manifest hash, archive URI, or reviewer identity is invented.

## 4. Review state lifecycle

The four required states (machine value / human label):

- `pending_review` — Pending Review
- `approved` — Approved
- `rejected` — Rejected
- `needs_changes` — Needs Changes

Every reviewable item starts in `pending_review`. The current state is shown as
a visible pill on every item at all times.

## 5. Decision + rationale

For each decision the workspace captures the reviewable item id, decision
state, reason category (optional; master-spec taxonomy: `brand_mismatch`,
`wrong_aspect_ratio`, `too_generic`, `compliance_issue`, `weak_quality`,
`provider_failure`, `needs_disclosure`, `ready_for_export`), free-text
rationale, free-text notes, reviewer label (optional), and a local-clock
timestamp. Decisions are recorded in a local / in-session ledger keyed by item
id.

## 6. Proof linkage

For each reviewable item the workspace shows read-only proof links / summaries
drawn from accepted data: provenance passport, manifest verification, B2
evidence, rehydrate, and export pack. Each is shown with an honest
"available" / "not available" status; no link or verified status is fabricated.

## 7. Boundary honesty (verbatim)

Approval records the reviewer's workflow decision; it does not prove semantic
truth, legal authenticity, C2PA authenticity, human authorship, Object Lock /
tamper-proof storage, or production security. The review ledger is local /
in-session in this slice; it is not durable, tamper-proof, replicated, or
production-multi-user. The workspace reads no B2 object, calls no provider, and
performs no browser-side B2 byte verification. The local contract is verified;
the public deployment remains pending until the new backend is deployed and the
public URL is verified end-to-end.

## 8. Smoke

`scripts/ps035_review_approval_workspace_smoke.py` validates only PS-035. It is
local / static by default (`--check-only`), writes only
`docs/evidence/ps-035/review-approval-workspace-report.json` under explicit
`--write-evidence`, accepts `--no-frontend`, never runs the frontend, never
calls a provider, never reads or writes B2, never calls the central regression
gate, and never recursively executes another feature smoke. It validates route
registration, component + data module presence, the four review states, the
boundary copy, the proof links, no provider/B2 code paths, no forbidden
overclaims, the explicit `h` / `S` hidden Git flag checker over
`git ls-files -v`, absence of the bad lowercase-only hidden-flag command
literal, `git diff --check` cleanliness, and prior-evidence immutability.

## 9. Files changed (implementation)

- `apps/web/src/reviewApprovalWorkspace.ts` (new data module)
- `apps/web/src/ReviewApprovalWorkspace.tsx` (new component)
- `apps/web/src/App.tsx` (route guard + render)
- `apps/web/src/JudgeCockpitHome.tsx` (nav CTA)
- `apps/web/src/styles.css` (minimal additive classes)
- `scripts/ps035_review_approval_workspace_smoke.py` (new smoke)
- `specs/07-master-spec-plan.md` (cross-reference)
- `specs/08-roadmap-slices.md` (status update)
- `docs/validation/proofstudio-smoke-harness-v1.md` (additive PS-035 note)
- `docs/ps-035-review-approval-workspace-proof.md` (this file)
- `docs/evidence/ps-035/review-approval-workspace-report.json` (only under
  explicit `--write-evidence`)

PS-035 does not modify `AGENTS.md`, `.env*`, `render.yaml`, requirements, the
central regression gate, `smoke_lib.py`, any provider wrapper, any B2 path, or
any prior-slice evidence.
