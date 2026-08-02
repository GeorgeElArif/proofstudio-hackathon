# PS-037 — Disclosure + Trust Boundary Layer

## 1. Status

PS-037 — Disclosure + Trust Boundary Layer is currently:

- Spec only.
- Implementation pending. No product code, frontend code, backend code,
  scripts, evidence, AGENTS.md, `.env*`, `render.yaml`, or requirements files
  are changed during this phase.

PS-037 must not be implemented, and no implementation files may be changed,
until this spec is accepted by the PM. The latest accepted base is
`accepted/proofstudio` commit
`aaa93a72263d81dddae7cafdbb9be5ace7c3cb5d`.

This spec-only commit touches only this file:
`specs/54-ps-037-disclosure-trust-boundary-layer.md`.

PS-037 must not call live providers, must not read or write live B2, must not
perform broad B2 scans, must not mutate any evidence, must not run the
frontend, must not stage, commit, or push, and must not print secrets during
this phase. PS-037 obeys the root `AGENTS.md` operating law and the validation
policy in `docs/validation/proofstudio-smoke-harness-v1.md`.

## 2. Purpose

PS-037 defines a reusable disclosure and trust-boundary layer that makes
ProofStudio's limits visible, consistent, and judge-safe across the core proof
surfaces. Today every accepted proof surface carries its own independently
authored truth-boundary copy, its own non-claims list, and its own framing of
"what is locally verified versus not claimed." PS-037 consolidates that into a
single shared disclosure layer so a reviewer, client, or judge reads the same
honest boundary language everywhere proof is shown.

The layer is a disclosure layer, not a new proof surface. It states, in one
consistent place, what ProofStudio proves, what ProofStudio does not prove,
whether evidence is local/check-only or live, whether B2 evidence is recorded
or live-verified, whether provider activity happened, whether a reviewer
decision is a workflow decision (not a truth/legal/authorship claim), whether
manifest/hash/digest evidence is locally verified, and what remains unknown or
not claimed.

PS-037 proves what the pipeline recorded. The disclosure layer makes that
boundary explicit and identical on every core proof surface. It does not prove
semantic truth, legal authenticity, C2PA authenticity, human authorship, Object
Lock / tamper-proof storage, browser-side B2 byte verification, live B2
availability, production security, production compliance, legal review, or
chain-of-custody guarantees beyond recorded pipeline evidence.

## 3. Root Cause / Product Gap

ProofStudio already records strong evidence and already surfaces a truth
boundary on nearly every surface. The gap is consistency. The truth-boundary
copy and the non-claims lists are written independently inside each surface's
own data module, so they drift in wording, in completeness, and in framing:

- `apps/web/src/App.tsx` (PS-013/PS-014 Review Room) carries a local
  `TRUTH_BOUNDARY_TEXT` and a local `NON_CLAIMS` list.
- `apps/web/src/JudgeCockpitHome.tsx` (PS-023) carries its own
  truth-boundary footer with its own boundary string.
- `apps/web/src/b2Evidence.ts` (PS-026), `apps/web/src/b2RehydrateComparison.ts`
  (PS-029), `apps/web/src/manifestVerification.ts` (PS-028),
  `apps/web/src/failureAsProofTimeline.ts` (PS-030),
  `apps/web/src/judgeEvidencePack.ts` (PS-031),
  `apps/web/src/operationsCockpit.ts` (PS-032),
  `apps/web/src/providerDecisionIntelligence.ts` (PS-033), and
  `apps/web/src/lineageComparisonLab.ts` (PS-034) each define their own
  per-surface truth-boundary text and per-surface non-claims lists.
- `apps/web/src/reviewApprovalWorkspace.ts` (PS-035) carries its own approval
  boundary message and its own non-claims list.
- `apps/web/src/b2AuditVault.ts` (PS-036) carries its own truth-boundary panel
  text and its own boundary red lines.

Each surface is honest on its own, but a judge moving from surface to surface
sees a different boundary sentence, a different set of not-claimed items, and
a different framing of what "local verification" means. That drift is a
judge-safety risk: a boundary that is correct on one surface but absent or
reworded on another looks like a hedge or a contradiction.

PS-037 closes that gap by adding one shared disclosure layer — a canonical
data module plus a shared component — that every core proof surface renders.
The layer does not invent new claims; it makes the existing boundary
consistent. It is local/static by default: it adds no provider calls, no live
B2 reads, no B2 writes, no broad B2 scans, no new backend, no new env, and no
deployment changes.

## 4. User Story

As a reviewer (designer, marketer, reviewer, client, or judge), I want the
same disclosure and trust-boundary language to appear on every core proof
surface, so that when I read "what ProofStudio proves" and "what ProofStudio
does not prove," the wording is identical whether I am on the Judge Cockpit
Home, a B2 Evidence surface, a Manifest Verification surface, a Review +
Approval surface, or a B2 Audit Vault surface — and so I never mistake a
workflow approval for legal authenticity, a hash match for semantic truth, or
a B2 archive reference for Object Lock.

As a demo presenter, I want a reusable disclosure layer that is useful in a
three-minute hackathon demo: a compact disclosure badge that summarizes the
boundary, plus an expanded panel that states, verbatim, what is proven, what
is locally verified, what is live-verified, what provider activity happened,
what the B2 evidence status is, what the reviewer decision boundary is, what
is not claimed, and what is unknown — all working offline from accepted
local / golden / demo fixtures, with no live provider calls, no live B2
reads, no B2 writes, and no broad B2 scans.

## 5. Current Accepted Base

The current accepted base for PS-037 is:

- branch: `accepted/proofstudio`
- commit: `aaa93a72263d81dddae7cafdbb9be5ace7c3cb5d`
- remote: `origin/accepted/proofstudio` is at the same commit
- this is the post-PS-036 accepted state: the root `AGENTS.md` operating law
  is already in place (PS-035D); the accepted-base-pointer-drift guard is in
  place (PS-035E); the central regression gate is non-mutating by default from
  PS-035C; the golden-fixture digest freeze is in place from PS-035B; the
  golden-run manifest carries a real non-null `manifest_uri` and a real 64-hex
  `manifest_hash` from PS-035A; the Review + Approval Workspace is in place
  from PS-035; the Archive / Rehydrate / B2 Audit Vault is in place from
  PS-036.

PS-037 must start from `origin/accepted/proofstudio`, not from `main`.

Relevant accepted facts at this base that PS-037 builds on (PS-037 must not
mutate these and must not change their values):

- the central regression gate
  (`scripts/proofstudio_regression_gate.py`) supports `--current`,
  `--frontend`, `--no-frontend`, `--check-only`, `--report-out`, and
  `--write-report` (PS-035C accepted)
- the gate is non-mutating by default for any current slice that is not
  PS-034A (PS-035C accepted)
- the root `AGENTS.md` operating law exists at the repository root
  (PS-035D accepted), including the rule that hidden Git flags `h` and `S`
  must be checked explicitly by reading `git ls-files -v` and failing when
  `line[0]` is `h` or `S`
- the accepted-base-pointer-drift guard exists (PS-035E accepted)
- the golden-fixture digest freeze exists at
  `docs/evidence/golden-fixture-digests.json` (PS-035B accepted)
- the golden-run manifest carries a real non-null `manifest_uri` and a real
  64-hex `manifest_hash` (PS-035A accepted)
- every existing core proof surface already renders some form of truth
  boundary (PS-023 through PS-036); PS-037 consolidates that boundary, it does
  not invent a new claim
- the existing shared component classes (`.trust-boundary`, pills, cards,
  `JsonExpander`) already exist in `apps/web/src/styles.css`

## 6. Scope

PS-037 is a product slice. It adds a reusable disclosure / trust-boundary
layer (a shared data module plus a shared component) and renders it
additively on the core proof surfaces. It is local / static by default: it
must work without live provider calls, without live B2 reads, without B2
writes, and without broad B2 scans, by reading accepted local / golden / demo
fixtures and existing accepted data modules.

PS-037 must:

1. Add a shared, canonical disclosure data module
   (`apps/web/src/trustBoundary.ts`, or the project's accepted equivalent)
   that exposes one consistent set of disclosure concepts and boundary
   language for every core proof surface.
2. Add a shared disclosure component
   (`apps/web/src/TrustBoundaryLayer.tsx`, or the project's accepted
   equivalent) that renders the disclosure layer, including an optional
   compact badge and an expanded panel pattern.
3. Render the disclosure layer additively on the required core proof surfaces
   (section 10.3) so the boundary language is identical everywhere proof is
   shown.
4. State, in one consistent place, "What ProofStudio proves" and "What
   ProofStudio does not prove."
5. Surface the canonical disclosure concepts: pipeline-recorded evidence,
   local verification, live verification status, provider activity status,
   B2 evidence status, reviewer decision boundary, not claimed, and unknown.
6. Surface the canonical de-escalation pairs verbatim (section 10.4) so no
   judge mistakes a strong-sounding artifact for a stronger guarantee.
7. Surface the canonical negative boundary strings verbatim (section 10.5).
8. Preserve the existing per-surface truth-boundary panels; the shared layer
   complements them with one canonical source of boundary language. PS-037
   must not delete or weaken any existing per-surface non-claim.
9. Be demo-friendly and judge-friendly: useful in a three-minute demo, no
   generic AI hype copy, no unsupported claims.
10. Work without provider calls, without live B2 reads, without B2 writes,
    and without broad B2 scans, by using accepted local / golden / demo data
    or existing accepted data paths.
11. Not mutate any prior evidence. Any PS-037-owned evidence lives only under
    `docs/evidence/ps-037/`.
12. Not change the golden run canonical constants, the historical contracts
    the regression gate verifies, or any provider / B2 behavior.

## 7. Non-goals

PS-037 must not:

- do not implement product code during the spec-only phase
- do not edit product code under `src/**`
- do not edit frontend code under `apps/**`
- do not edit scripts under `scripts/**`
- do not edit evidence under `docs/evidence/**`
- do not edit `AGENTS.md`
- do not edit `.env*`
- do not edit `render.yaml`
- do not edit requirements files
- do not run the frontend
- do not call any provider
- do not read B2 (no live B2 reads)
- do not write B2 (no B2 writes)
- do not perform broad B2 scans
- do not claim semantic truth
- do not claim legal authenticity
- do not claim human authorship
- do not claim C2PA authenticity unless implemented and verified
- do not claim Object Lock / tamper-proof storage unless implemented and
  verified
- do not claim browser-side B2 byte verification unless implemented and
  verified
- do not claim live B2 availability unless a live B2 check is explicitly
  implemented and approved
- do not claim production security
- do not claim production compliance
- do not claim legal review
- do not claim chain-of-custody guarantees beyond recorded pipeline evidence
- do not claim public deployment verification unless deployed and tested
- do not claim enterprise security
- do not claim actual spend / latency / quota unless captured
- do not claim provider failures / reruns / variants unless evidenced
- do not delete or weaken any existing per-surface truth-boundary panel or
  non-claim
- do not add a new backend, a new provider wrapper, a new B2 client, a new
  env variable, or any deployment change
- do not build CI, billing, deployment, auth, teams, permissions, or a full
  enterprise DAM
- do not change the golden run canonical constants
- do not change the historical contracts the regression gate verifies
- do not introduce a control name containing `KEY`, `TOKEN`, or `SECRET`
- do not use hidden Git flags (`assume-unchanged`, `skip-worktree`,
  `git update-index`, `update-index`)
- do not run recursive smokes
- do not use generic AI hype copy or unsupported claims

PS-037 only edits this spec file in the spec-only phase. Implementation-phase
candidate files are listed in section 8.

## 8. Implementation Candidate Files

The following are implementation-phase candidates only, clearly marked as
implementation-phase only. They are **not** for this spec-only commit. They
are listed so the implementation phase has a grounded file plan that follows
existing app conventions (each surface has a PascalCase `.tsx` component, a
camelCase `.ts` data module, a smoke script, and an evidence directory).

Shared layer (new files):
- `apps/web/src/trustBoundary.ts` (new) — the canonical camelCase disclosure
  data module. Exposes the single shared set of disclosure concepts, boundary
  language, de-escalation pairs, negative boundary strings, and not-claimed /
  unknown status used by every core proof surface. Same convention as
  `b2Evidence.ts`, `b2RehydrateComparison.ts`, `reviewApprovalWorkspace.ts`,
  etc.
- `apps/web/src/TrustBoundaryLayer.tsx` (new) — the shared disclosure
  component. Accepts the existing `variant` convention (for example
  `variant="panel"` for an expanded panel and `variant="badge"` for a compact
  badge), reads only from `apps/web/src/trustBoundary.ts`, and renders the
  disclosure layer with no provider calls and no live B2 reads.

Additive use on core proof surfaces (existing files, edited additively only):
- `apps/web/src/JudgeCockpitHome.tsx` (PS-023) — render the shared disclosure
  layer on the home surface.
- `apps/web/src/B2EvidenceExplorer.tsx` (PS-026) — render the shared
  disclosure layer.
- `apps/web/src/B2RehydrateComparison.tsx` (PS-029) — render the shared
  disclosure layer.
- `apps/web/src/ManifestVerificationPanel.tsx` (PS-028) — render the shared
  disclosure layer.
- `apps/web/src/B2AuditVault.tsx` (PS-036) — render the shared disclosure
  layer.
- `apps/web/src/ReviewApprovalWorkspace.tsx` (PS-035) — render the shared
  disclosure layer, including the reviewer decision boundary.
- `apps/web/src/JudgeEvidencePack.tsx` (PS-031) — render the shared disclosure
  layer (export / campaign pack surface).
- `apps/web/src/PublicPassportPage.tsx` (PS-019) — render the shared
  disclosure layer (provenance passport / proof summary surface).
- `apps/web/src/App.tsx` — render the shared disclosure layer on the Review
  Room (PS-013/PS-014) footer, complementing the existing local truth
  boundary.

Additive styles (existing file, additive classes only):
- `apps/web/src/styles.css` — add only the classes needed for the shared
  disclosure layer (compact badge, expanded panel, what-is-proven /
  what-is-not-proven rows, disclosure concept rows). No global style rewrite.

Backend (src/proofstudio) — none:
- PS-037 is a frontend-only disclosure layer over existing accepted data. No
  backend change is expected. If any read-only reuse of an accepted data path
  is needed, it must reuse the existing accepted data paths under
  `src/proofstudio/api/` and `src/proofstudio/provenance/` without calling
  providers and without reading live B2. No new provider wiring, no new B2
  client, no new B2 write path, no new broad B2 scan path. If no backend
  change is needed, none is made.

Smoke (scripts):
- `scripts/ps037_disclosure_trust_boundary_layer_smoke.py` (new) — the PS-037
  feature smoke. Must reuse `scripts/smoke_lib.py` for shared validation logic
  and must implement its own explicit `h` / `S` hidden-Git-flags checker (see
  section 14). Local / static only.

Spec / docs:
- `specs/07-master-spec-plan.md` — implementation-phase cross-reference only
  (register PS-037 acceptance). Must not change any historical item or golden
  constant.
- `specs/08-roadmap-slices.md` — implementation-phase status update only.
- `docs/validation/proofstudio-smoke-harness-v1.md` — implementation-phase
  PS-037 note only, additive, must not weaken any existing PS-034A / PS-035C
  contract.
- `docs/ps-037-disclosure-trust-boundary-layer-proof.md` (new) — the PS-037
  proof doc.

Evidence:
- `docs/evidence/ps-037/disclosure-trust-boundary-layer-report.json` (new) —
  the only evidence PS-037 may write, and only when `--write-evidence` is
  explicit.

Any edit to `src/proofstudio/**` during implementation requires the backend
change to remain read-only over accepted data and to make no provider call and
no live B2 read.

## 9. Forbidden Files Unless PM-approved Later

PS-037 implementation must not touch without explicit PM approval:

- `AGENTS.md`
- `.env*`
- `render.yaml`
- requirements files
- `docs/evidence/**` paths other than `docs/evidence/ps-037/**`
- any prior-slice evidence prefix (for example `docs/evidence/ps-021/**`,
  `docs/evidence/ps-026/**`, `docs/evidence/ps-029/**`,
  `docs/evidence/ps-031/**`, `docs/evidence/ps-035/**`,
  `docs/evidence/ps-036/**`, `docs/evidence/demo/golden-demo-run.json`,
  `docs/evidence/golden-fixture-digests.json`)
- `scripts/proofstudio_regression_gate.py` (the central gate is not owned by
  PS-037)
- `scripts/smoke_lib.py` (shared library; PS-037 must not mutate shared
  validation behavior)
- any provider wrapper under `src/proofstudio/providers/**` (PS-037 owns no
  provider behavior)
- any B2 client / storage write path (PS-037 performs no live B2 read, no B2
  write, and no broad B2 scan)

The only implementation-phase files allowed without PM approval are those in
section 8. Any other path requires explicit PM approval.

## 10. Disclosure / Trust Boundary Product Contract

PS-037 defines the following contract for the Disclosure & Trust Boundary
layer.

### 10.1 Layer identity

- It is a reusable disclosure layer, not a new proof surface, not a new route,
  and not a new backend endpoint.
- It is purely client-side by default: it calls no provider, reads no B2
  object, exposes no arbitrary `run_id` input, performs no browser-side B2
  byte verification, performs no broad B2 scan, and writes no B2 object.
- It is sourced from accepted local / golden / demo data and existing accepted
  data modules only.
- It makes the boundary identical on every core proof surface. It does not
  invent new claims; it states the existing boundary consistently.

### 10.2 Required disclosure concepts

The layer must surface these canonical disclosure concepts, each as a clearly
labeled disclosure item:

- `pipeline-recorded evidence` — what ProofStudio proves is what the pipeline
  recorded.
- `local verification` — whether evidence is locally verified against
  checked-in / accepted data.
- `live verification status` — whether a live check is in scope (local/check
  only by default).
- `provider activity status` — whether provider activity happened for the
  surfaced evidence.
- `B2 evidence status` — whether B2 evidence is recorded, and whether it is
  recorded-only or live-verified (recorded-only by default).
- `reviewer decision boundary` — whether a reviewer decision is a workflow
  decision, not a truth / legal / authorship claim.
- `not claimed` — the honest set of things ProofStudio does not claim.
- `unknown` — what remains unknown or not surfaced.

If a concept does not apply to a given surface, the layer must show an honest
"not applicable" / "unknown" state and must not fabricate a value.

### 10.3 Required surfaces

The disclosure layer must be rendered (additively) on at least these required
core proof surfaces, so `required_surfaces_have_disclosure` is truthful:

- Judge Cockpit Home (`apps/web/src/JudgeCockpitHome.tsx`, route `/`)
- B2 Evidence Explorer (`apps/web/src/B2EvidenceExplorer.tsx`, route
  `/b2-evidence`)
- Manifest Verification Panel (`apps/web/src/ManifestVerificationPanel.tsx`,
  route `/manifest-verification`)
- B2 Rehydrate Comparison (`apps/web/src/B2RehydrateComparison.tsx`, route
  `/b2-rehydrate-comparison`)
- Archive / Rehydrate / B2 Audit Vault (`apps/web/src/B2AuditVault.tsx`,
  route `/b2-audit-vault`)
- Review + Approval Workspace (`apps/web/src/ReviewApprovalWorkspace.tsx`,
  route `/review-approval-workspace`)
- Judge Evidence Pack (`apps/web/src/JudgeEvidencePack.tsx`, route
  `/evidence-pack`)
- Public Provenance Passport (`apps/web/src/PublicPassportPage.tsx`, route
  `/passport/:id`)
- Review Room (`apps/web/src/App.tsx`, route `/review`)

Additional accepted surfaces (Genblaze Pipeline Graph, Failure-as-Proof
Timeline, Operations Cockpit, Provider Decision Intelligence, Lineage +
Comparison Lab) may render the layer but are not required for the minimum
contract.

### 10.4 Required de-escalation pairs (verbatim)

The layer must surface these de-escalation pairs verbatim so a judge never
mistakes a strong-sounding artifact for a stronger guarantee:

- proof does not equal truth
- workflow approval does not equal legal authenticity
- B2 archive reference does not equal Object Lock
- hash match does not equal semantic truth
- manifest hash does not equal human authorship
- local evidence does not equal live B2 availability
- demo/golden evidence does not equal production security

### 10.5 Required negative boundary strings (verbatim)

The layer must surface these negative boundary strings verbatim:

- not semantic truth
- not legal authenticity
- not human authorship
- not C2PA authenticity
- not Object Lock
- not tamper-proof
- not browser-side B2 byte verification
- not live B2 availability
- not production security

### 10.6 Boundary honesty

The layer must distinguish clearly between:

- what is locally verified against accepted checked-in evidence (manifest
  hashes, archive references, digests, provider-call counts, rehydrate
  sources)
- what is not verified (live B2 availability, browser-side B2 byte
  verification, Object Lock / tamper-proof storage, public deployment,
  production security, production compliance, legal review)
- what is not claimed (semantic truth, legal authenticity, C2PA
  authenticity, human authorship, chain-of-custody guarantees beyond recorded
  pipeline evidence)

The disclosure layer must not imply that any ProofStudio artifact proves
anything beyond what the pipeline recorded.

## 11. UI/UX Contract

The Disclosure & Trust Boundary layer UI must include:

- A clear title: "Disclosure & Trust Boundary" (or an equivalent clear title),
  with a positioning line that ProofStudio proves what the pipeline recorded.
- A compact badge variant (for example `variant="badge"`) that summarizes the
  boundary in one line, suitable for surfaces where space is constrained.
- An expanded panel variant (for example `variant="panel"`) that states, in
  full, the disclosure contract.
- A "What ProofStudio proves" section listing pipeline-recorded evidence,
  local verification, live verification status, provider activity status, B2
  evidence status, and reviewer decision boundary.
- A "What ProofStudio does not prove" section listing the not-claimed /
  unknown status.
- The de-escalation pairs (section 10.4), surfaced verbatim.
- The negative boundary strings (section 10.5), surfaced verbatim.
- An honest not-claimed / unknown status panel.
- A persistent boundary statement that states verbatim (or equivalent):

  > ProofStudio proves what the pipeline recorded. Proof does not equal truth.
  > Workflow approval does not equal legal authenticity. A B2 archive
  > reference does not equal Object Lock. A hash match does not equal semantic
  > truth. A manifest hash does not equal human authorship. Local evidence
  > does not equal live B2 availability. Demo/golden evidence does not equal
  > production security.

UI / UX constraints:

- Must be useful in a three-minute hackathon demo: open any core proof
  surface -> read the compact badge -> expand the disclosure panel -> read
  what is proven -> read what is not proven -> read the de-escalation pairs ->
  read the negative boundary strings.
- Must render the same boundary language on every required surface (section
  10.3).
- Must not introduce generic AI hype copy.
- Must not add unsupported claims.
- Must not fabricate statuses that are not in accepted data.
- Must follow the existing component conventions (`variant`, pills, cards,
  `JsonExpander`, the `.trust-boundary` styles) used by the other surfaces.
- Must not delete or weaken any existing per-surface truth-boundary panel;
  the shared layer is additive.

## 12. Data Contract

### 12.1 Source data (read-only inputs)

PS-037 reads accepted local / golden / demo data and existing accepted data
modules as immutable inputs. It must not mutate these and must not change
their canonical values. Acceptable read-only sources:

- `apps/web/src/b2Evidence.ts` (PS-026)
- `apps/web/src/b2RehydrateComparison.ts` (PS-029)
- `apps/web/src/manifestVerification.ts` (PS-028)
- `apps/web/src/failureAsProofTimeline.ts` (PS-030)
- `apps/web/src/judgeEvidencePack.ts` (PS-031)
- `apps/web/src/operationsCockpit.ts` (PS-032)
- `apps/web/src/providerDecisionIntelligence.ts` (PS-033)
- `apps/web/src/lineageComparisonLab.ts` (PS-034)
- `apps/web/src/reviewApprovalWorkspace.ts` (PS-035)
- `apps/web/src/b2AuditVault.ts` (PS-036)
- `apps/web/src/api.ts` (`trust_boundary` shape exposed by the Provenance
  Passport)
- `docs/evidence/demo/golden-demo-run.json`
- `docs/evidence/golden-fixture-digests.json`

PS-037 must not change the golden run canonical constants. The canonical
constants are owned by their respective accepted slices.

### 12.2 Disclosure item shape

A disclosure item is derived from accepted data and must expose:

- `concept` (stable; one of the keys in section 10.2)
- `label` (the human-readable label, matching the verbatim strings in
  section 20)
- `value` (the disclosure value, honest about local / recorded-only / unknown)
- `applicable` (boolean; false when the concept honestly does not apply to the
  surface)
- `verification` (one of `locally_verified`, `recorded_only`, `not_verified`,
  `not_claimed`, `unknown`)

### 12.3 Evidence report schema rule

The PS-037 evidence report must follow the harness schema rule: boolean
fields remain booleans and detail / list fields use explicit detail names. A
field whose name implies a boolean success flag must remain a boolean. List
fields must use explicit detail names such as `_ids`, `_details`, or
`_failures` (see section 13).

## 13. Evidence Contract

PS-037 owns exactly one evidence directory: `docs/evidence/ps-037/`.

- A feature smoke may write only its own evidence, and only when
  `--write-evidence` is explicit. The default PS-037 smoke behavior is
  non-mutating local validation.
- PS-037 must not write any file outside `docs/evidence/ps-037/`.
- PS-037 must not mutate any prior-slice evidence (every prior evidence prefix
  is guarded by `scripts/smoke_lib.py` and
  `scripts/proofstudio_regression_gate.py`).
- The PS-037 evidence file is
  `docs/evidence/ps-037/disclosure-trust-boundary-layer-report.json`.

The PS-037 evidence report must carry these boolean fields (booleans as
booleans; `failures` as a list):

- `ok` (boolean; true only when every measured field is truthful and no
  forbidden overclaim or forbidden file change is present)
- `slice_id`: `ps037`
- `trust_boundary_component_present` (boolean; `TrustBoundaryLayer` component
  exists)
- `trust_boundary_data_module_present` (boolean; `trustBoundary.ts` exists)
- `disclosure_layer_present` (boolean; the shared layer is wired in)
- `required_surfaces_have_disclosure` (boolean; the required surfaces in
  section 10.3 render the layer)
- `what_proofstudio_proves_present` (boolean)
- `what_proofstudio_does_not_prove_present` (boolean)
- `pipeline_recorded_evidence_present` (boolean)
- `local_verification_status_present` (boolean)
- `live_verification_status_present` (boolean)
- `provider_activity_status_present` (boolean)
- `b2_evidence_status_present` (boolean)
- `reviewer_decision_boundary_present` (boolean)
- `not_claimed_status_present` (boolean)
- `unknown_status_present` (boolean)
- `proof_does_not_equal_truth_present` (boolean)
- `no_semantic_truth_claim` (boolean)
- `no_legal_authenticity_claim` (boolean)
- `no_human_authorship_claim` (boolean)
- `no_c2pa_authenticity_claim` (boolean)
- `no_object_lock_claim` (boolean)
- `no_tamper_proof_claim` (boolean)
- `no_browser_side_b2_byte_verification_claim` (boolean)
- `no_live_b2_availability_claim` (boolean)
- `no_production_security_claim` (boolean)
- `no_provider_calls` (boolean)
- `no_live_b2_reads` (boolean)
- `no_b2_writes` (boolean)
- `no_broad_b2_scans` (boolean)
- `no_recursive_smokes` (boolean)
- `no_hidden_git_flags_h` (boolean)
- `no_hidden_git_flags_S` (boolean)
- `truth_boundary_preserved` (boolean)
- `no_forbidden_overclaims` (boolean)
- `prior_evidence_clean` (boolean)
- `failures` (list; empty on success)

`ok` must be `false` if `failures` is non-empty. Boolean fields must remain
booleans; list / detail fields must use explicit detail names. This evidence
file is created only in the implementation phase and only when
`--write-evidence` is explicit.

## 14. Smoke / Validation Contract

PS-037 ships one feature smoke:
`scripts/ps037_disclosure_trust_boundary_layer_smoke.py`.

The PS-037 feature smoke must:

- validate only the PS-037 slice (no recursive smokes; must never launch
  another feature smoke as a subprocess; must never call the central
  regression gate)
- read checked-in prior evidence and accepted data modules as immutable inputs
- write only its own evidence file
  `docs/evidence/ps-037/disclosure-trust-boundary-layer-report.json`, and only
  when `--write-evidence` is explicit
- never call a provider
- never read arbitrary B2 objects (no live B2 reads)
- never write B2 (no B2 writes)
- never perform broad B2 scans
- never run the frontend typecheck / build (that belongs to the central gate)
- reuse `scripts/smoke_lib.py` for shared validation logic
- validate the shared `TrustBoundaryLayer` component is present
- validate the shared `trustBoundary.ts` data module is present
- validate the disclosure layer is rendered on the required proof surfaces
  (section 10.3)
- validate the required disclosure / trust-boundary UI strings (section 20)
  are present
- validate the required negative boundary strings (section 20) are present
- validate the required de-escalation pairs (section 10.4) are present
- validate no provider calls are introduced
- validate no live B2 reads are introduced
- validate no B2 writes are introduced
- validate no broad B2 scans are introduced
- validate no forbidden overclaims are introduced
- validate no recursive smokes (the smoke must not launch another feature
  smoke)
- validate no hidden Git flags `h` or `S` with an explicit h/S checker that
  reads `git ls-files -v` and fails when `line[0]` is `h` or `S` (a
  lowercase-only marker check is not sufficient because it misses uppercase
  `S` skip-worktree)
- validate the bad lowercase-only hidden-flag command literal is absent from
  the PS-037 changed files, without the smoke or this spec reproducing that
  literal
- validate prior evidence is unchanged
- validate `git diff --check` is clean

The PS-037 feature smoke must support these standard flags:

- `--check-only` (default: non-mutating local validation; no evidence file is
  written)
- `--write-evidence` (write only `docs/evidence/ps-037/` evidence)
- `--no-frontend`

Default PS-037 smoke behavior is non-mutating local validation
(`--check-only`).

The smoke must not contain the bad lowercase-only hidden-flag marker check and
must not rely on a lowercase-only marker check. The hidden-Git-flags check
must be the explicit `h` / `S` checker over `git ls-files -v`, and must record
`no_hidden_git_flags_h` and `no_hidden_git_flags_S` as separate booleans.

PS-037 smoke performs no provider calls, no live B2 reads, no B2 writes, and
no broad B2 scans.

## 15. Regression Gate Contract

The central regression gate remains the single cross-slice release-readiness
gate and is non-mutating by default. PS-037 does not own or modify the central
gate.

Normal PS-037 release validation command:

```
python scripts/proofstudio_regression_gate.py --current ps037 --frontend --report-out /tmp/proofstudio-release-report.json
```

Contract-only gate (no frontend):

```
python scripts/proofstudio_regression_gate.py --current ps037 --no-frontend --report-out /tmp/proofstudio-ps037-regression-report.json
```

- The gate runs `npm run typecheck` and `npm run build` in `apps/web` exactly
  once per invocation, and only when `--frontend` is passed. PS-037 feature
  smoke must never trigger nested frontend builds.
- The gate must not write the canonical PS-034A report. `--write-report` is
  rejected for `--current ps037` (PS-035C accepted behavior; only PS-034A may
  regenerate the canonical report).
- Running the gate for `ps037` must leave all prior-slice evidence unchanged.
- No recursive smokes: the gate never executes a feature smoke.

Canonical PS-034A regeneration (unchanged, owned by PS-034A only):

```
python scripts/proofstudio_regression_gate.py --current ps034a --write-report
```

## 16. Truth Boundary

ProofStudio proves what the pipeline recorded. The Disclosure & Trust Boundary
layer is a disclosure surface that makes that boundary explicit and identical
on every core proof surface. It is not a legal authenticity system, not a live
B2 verifier, and not a truth system.

The layer must preserve these truth-boundary red lines verbatim across the
spec, the UI, and any evidence report:

- do not claim semantic truth
- do not claim legal authenticity
- do not claim human authorship
- do not claim C2PA unless implemented and verified
- do not claim Object Lock / tamper-proof storage unless implemented and
  verified
- do not claim browser-side B2 byte verification unless implemented and
  verified
- do not claim live B2 availability unless a live B2 check is explicitly
  implemented and approved
- do not claim public deployment verification unless deployed and tested
- do not claim enterprise security
- do not claim production compliance
- do not claim legal review
- do not claim chain-of-custody guarantees beyond recorded pipeline evidence
- do not claim actual spend / latency / quota unless captured
- do not claim provider failures / reruns / variants unless evidenced

PS-037 does not prove product correctness, production security, production
compliance, B2 immutability, Object Lock, tamper-proof storage, browser-side
B2 byte verification, live B2 availability, real billing API integration,
billing behavior, CI enforcement, legal review, or deployment readiness. No
PS-037 artifact may imply any of these. The disclosure layer states what the
pipeline already recorded; it does not re-fetch, re-hash, or re-verify live
B2 bytes.

## 17. Risks

PS-037 must record the following risks with mitigations:

- overclaim risk
  - risk: a reviewer misreads the disclosure layer or its copy as a forbidden
    overclaim — i.e. as claiming semantic truth, legal authenticity, human
    authorship, C2PA authenticity, Object Lock / tamper-proof storage,
    browser-side B2 byte verification, live B2 availability, production
    security, production compliance, legal review, or chain-of-custody
    guarantees beyond recorded pipeline evidence. ProofStudio does not claim
    any of these.
  - mitigation: the persistent boundary statement (section 11) is mandatory;
    the truth-boundary red lines (section 16) are preserved verbatim; the
    de-escalation pairs (section 10.4) and negative boundary strings
    (section 10.5) are surfaced verbatim; the evidence report carries
    `no_forbidden_overclaims` and `truth_boundary_preserved`.
- drift / inconsistency risk
  - risk: a surface keeps a divergent local truth-boundary copy that
    contradicts the shared layer.
  - mitigation: the shared layer is rendered on every required surface
    (section 10.3); the smoke validates
    `required_surfaces_have_disclosure`; existing per-surface panels are
    preserved, not weakened.
- de-escalation-gap risk
  - risk: a judge mistakes a hash match for semantic truth, a B2 archive
    reference for Object Lock, a manifest hash for human authorship, a
    workflow approval for legal authenticity, local evidence for live B2
    availability, or demo/golden evidence for production security.
  - mitigation: the de-escalation pairs in section 10.4 are surfaced verbatim.
- live-B2-read risk
  - risk: the layer triggers a live B2 read or a broad B2 scan.
  - mitigation: the layer is purely client-side over accepted data; the smoke
    enforces `no_live_b2_reads`, `no_b2_writes`, `no_broad_b2_scans`.
- evidence-mutation risk
  - risk: the PS-037 smoke or the central gate run overwrites prior-slice
    evidence.
  - mitigation: PS-037 writes only `docs/evidence/ps-037/`; the gate is
    non-mutating by default; prior evidence prefixes are guarded.
- hidden-Git-flags risk
  - risk: a session uses `assume-unchanged`, `skip-worktree`, or
    `git update-index` / `update-index` to mask a dirty tree, including the
    uppercase `S` skip-worktree flag that a lowercase-only marker check
    misses.
  - mitigation: the operating law forbids these verbatim; the smoke uses the
    explicit `h` / `S` checker over `git ls-files -v` and fails on `line[0]`
    being `h` or `S`, recording `no_hidden_git_flags_h` and
    `no_hidden_git_flags_S` as separate booleans.
- scope-creep risk
  - risk: PS-037 expands into CI, billing, deployment, auth, teams,
    permissions, a full enterprise DAM, a new backend, or a live B2 fetcher.
  - mitigation: section 7 lists these as non-goals; section 9 forbids the
    relevant paths.
- recursive-smoke risk
  - risk: the PS-037 smoke launches another feature smoke or calls the central
    gate.
  - mitigation: the smoke must never launch another feature smoke as a
    subprocess and must never call the central regression gate; the central
    gate is the only cross-slice validator.

## 18. Acceptance Criteria

PS-037 (spec-only phase) is accepted only when:

- this spec exists at `specs/54-ps-037-disclosure-trust-boundary-layer.md`
- only this spec file is changed in the spec-only phase
- the branch `ps-037/disclosure-trust-boundary-layer` starts from
  `origin/accepted/proofstudio` at commit
  `aaa93a72263d81dddae7cafdbb9be5ace7c3cb5d` (the merge-base equals that
  commit)
- the product scope is clear and does not expand into CI, billing, deployment,
  provider calls, live B2 reads, B2 writes, or broad B2 scans
- the required disclosure concepts (section 10.2) and the required surfaces
  (section 10.3) are specified
- the de-escalation pairs (section 10.4) and the negative boundary strings
  (section 10.5) are specified verbatim
- the UI / UX contract (section 11) and the persistent boundary statement are
  specified
- the data contract (section 12) reuses accepted checked-in evidence as
  read-only inputs
- the truth boundary (section 16) is explicit and the boundary copy is
  specified
- the implementation candidate files (section 8) are listed, but no
  implementation is done in this phase
- the validation plan uses the PS-037 feature smoke plus the central
  regression gate (sections 14 and 15)
- no evidence mutation occurs in this phase
- no hidden Git flags `h` or `S` are present (verified by the explicit h/S
  checker over `git ls-files -v`)
- `git diff --check` is clean
- no staging, commit, or push occurs until PM approval
- `AGENTS.md`, `specs/07-master-spec-plan.md`, and `specs/08-roadmap-slices.md`
  are not changed in this phase

Implementation-phase acceptance (for reference, not this phase) additionally
requires: the shared `TrustBoundaryLayer` component + `trustBoundary.ts` data
module exist; the disclosure layer is rendered on the required surfaces
(section 10.3); the required disclosure concepts, de-escalation pairs, and
negative boundary strings are present; the PS-037 smoke passes in
`--check-only` (default) and writes only `docs/evidence/ps-037/**` under
`--write-evidence`; the central gate passes for `--current ps037`; no provider
call, no live B2 read, no B2 write, no broad B2 scan occurs; prior evidence is
unchanged; no forbidden overclaim is introduced.

## 19. Rollback

Rollback of the PS-037 spec-only phase is a single revert of this spec commit,
because only `specs/54-ps-037-disclosure-trust-boundary-layer.md` is changed
in this phase.

Future implementation rollback must restore the pre-PS-037 state of the edited
files in section 8. Specifically:

- remove `apps/web/src/trustBoundary.ts`
- remove `apps/web/src/TrustBoundaryLayer.tsx`
- revert the additive disclosure-layer renders in
  `apps/web/src/JudgeCockpitHome.tsx`,
  `apps/web/src/B2EvidenceExplorer.tsx`,
  `apps/web/src/B2RehydrateComparison.tsx`,
  `apps/web/src/ManifestVerificationPanel.tsx`,
  `apps/web/src/B2AuditVault.tsx`,
  `apps/web/src/ReviewApprovalWorkspace.tsx`,
  `apps/web/src/JudgeEvidencePack.tsx`,
  `apps/web/src/PublicPassportPage.tsx`, and
  `apps/web/src/App.tsx` to pre-PS-037 state
- revert the additive disclosure-layer classes in
  `apps/web/src/styles.css` to pre-PS-037 state
- remove `scripts/ps037_disclosure_trust_boundary_layer_smoke.py`
- remove `docs/ps-037-disclosure-trust-boundary-layer-proof.md`
- remove `docs/evidence/ps-037/` if it was added
- revert the additive cross-references in `specs/07-master-spec-plan.md`,
  `specs/08-roadmap-slices.md`, and
  `docs/validation/proofstudio-smoke-harness-v1.md` to pre-PS-037 state

Rollback of PS-037 must not touch any evidence under `docs/evidence/**` other
than `docs/evidence/ps-037/`, must not touch the central gate
(`scripts/proofstudio_regression_gate.py`), `scripts/smoke_lib.py`,
`AGENTS.md`, `.env*`, `render.yaml`, requirements files, any provider wrapper,
or any B2 storage path. Rollback is isolated and reversible because PS-037 is
a self-contained disclosure layer over existing accepted data; it does not
change provider behavior, B2 behavior, billing behavior, or deployment
topology.

## 20. Verbatim implementation/audit contract strings

The PS-037 implementation, the Disclosure & Trust Boundary UI, and the PS-037
smoke must preserve the following exact strings so the disclosure contract is
deterministic and auditable. The required identity / positioning strings are:

- PS-037
- Disclosure & Trust Boundary
- What ProofStudio proves
- What ProofStudio does not prove

The required disclosure-concept strings are:

- pipeline-recorded evidence
- local verification
- live verification status
- provider activity status
- B2 evidence status
- reviewer decision boundary
- not claimed
- unknown

The required de-escalation-pair strings are:

- proof does not equal truth
- workflow approval does not equal legal authenticity
- B2 archive reference does not equal Object Lock
- hash match does not equal semantic truth
- manifest hash does not equal human authorship
- local evidence does not equal live B2 availability
- demo/golden evidence does not equal production security

The required negative-boundary strings are:

- not semantic truth
- not legal authenticity
- not human authorship
- not C2PA authenticity
- not Object Lock
- not tamper-proof
- not browser-side B2 byte verification
- not live B2 availability
- not production security

The required posture / boundary strings are:

- no provider calls
- no live B2 reads
- no B2 writes
- no broad B2 scans
- no recursive smokes
- hidden Git flags h
- line[0]

The required evidence-report boolean keys are:

- `ok`
- `slice_id: ps037`
- `trust_boundary_component_present`
- `trust_boundary_data_module_present`
- `disclosure_layer_present`
- `required_surfaces_have_disclosure`
- `what_proofstudio_proves_present`
- `what_proofstudio_does_not_prove_present`
- `pipeline_recorded_evidence_present`
- `local_verification_status_present`
- `live_verification_status_present`
- `provider_activity_status_present`
- `b2_evidence_status_present`
- `reviewer_decision_boundary_present`
- `not_claimed_status_present`
- `unknown_status_present`
- `proof_does_not_equal_truth_present`
- `no_semantic_truth_claim`
- `no_legal_authenticity_claim`
- `no_human_authorship_claim`
- `no_c2pa_authenticity_claim`
- `no_object_lock_claim`
- `no_tamper_proof_claim`
- `no_browser_side_b2_byte_verification_claim`
- `no_live_b2_availability_claim`
- `no_production_security_claim`
- `no_provider_calls`
- `no_live_b2_reads`
- `no_b2_writes`
- `no_broad_b2_scans`
- `no_recursive_smokes`
- `no_hidden_git_flags_h`
- `no_hidden_git_flags_S`
- `truth_boundary_preserved`
- `no_forbidden_overclaims`
- `prior_evidence_clean`
- `failures`

The required regression-gate and smoke contract commands and paths are:

- `python scripts/proofstudio_regression_gate.py --current ps037 --frontend --report-out /tmp/proofstudio-release-report.json`
- `python scripts/proofstudio_regression_gate.py --current ps037 --no-frontend --report-out /tmp/proofstudio-ps037-regression-report.json`
- `scripts/ps037_disclosure_trust_boundary_layer_smoke.py`
- `docs/evidence/ps-037/disclosure-trust-boundary-layer-report.json`
- `docs/ps-037-disclosure-trust-boundary-layer-proof.md`
