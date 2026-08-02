# PS-037a — Multimodal Proof Layer

## 1. Status

PS-037a — Multimodal Proof Layer is currently:

- Spec only.
- Implementation pending. No product code, frontend code, backend code,
  scripts, evidence, AGENTS.md, `.env*`, `render.yaml`, or requirements files
  are changed during this phase.

PS-037a must not be implemented, and no implementation files may be changed,
until this spec is accepted by the PM. The latest accepted base is the dynamic
Git ref `origin/accepted/proofstudio`, which at the time of this spec resolves
to commit `e8fb667ecbc299e00c6ec166feb576960039285b` (the post-PS-037 accepted
state). The ref is the authority; the commit hash is recorded for traceability
only and must not be treated as a hardcoded base.

This spec-only commit touches only this file:
`specs/55-ps-037a-multimodal-proof-layer.md`.

PS-037a must not call live providers, must not read or write live B2, must not
perform broad B2 scans, must not mutate any evidence, must not run the
frontend, must not run the backend, must not stage, commit, or push, and must
not print secrets during this phase. PS-037a obeys the root `AGENTS.md`
operating law and the validation policy in
`docs/validation/proofstudio-smoke-harness-v1.md`.

## 2. Purpose

PS-037a defines a reusable multimodal proof layer that makes ProofStudio's
artifact evidence easier to inspect across every modality that already exists
in checked-in local / golden / demo data: image, video, audio, text, manifest,
B2 archive, rehydrate, and export-pack evidence. Today that artifact evidence
is scattered across independent per-surface data modules and per-surface
truth-boundary panels. A reviewer moving from surface to surface cannot, in one
place, answer the basic multimodal questions: what media / artifact exists,
what modality it belongs to, where the artifact reference is recorded, what
hash / digest / manifest evidence is recorded, whether the artifact is local /
demo / golden evidence or live evidence, whether provider activity happened,
whether B2 archive evidence exists, whether rehydrate evidence exists, and
whether transcript / timestamp / voice / emotion / campaign-intelligence
evidence is absent, deferred, or later-slice owned.

The Multimodal Proof Layer consolidates those answers into one shared,
additive layer. It is a proof-inspection layer over already-recorded evidence,
not a new proof surface, not a new route, and not a new backend endpoint. It
makes the existing artifact evidence consistent and judge-safe across modality,
and it states honestly, per modality, what ProofStudio proves and what
ProofStudio does not prove.

PS-037a proves what the pipeline recorded. The layer does not prove semantic
truth, legal authenticity, C2PA authenticity, human authorship, Object Lock /
tamper-proof storage, browser-side B2 byte verification, live B2 availability,
production security, production compliance, legal review, or chain-of-custody
guarantees beyond recorded pipeline evidence. It does not fake transcripts,
timestamps, voice analysis, emotion analysis, campaign intelligence, or any
provider output that a later slice owns.

## 3. Root Cause / Product Gap

ProofStudio already records strong artifact evidence across modalities and
already surfaces a truth boundary on nearly every surface. The gap is
modality-level consistency and inspectability. The artifact evidence and its
boundary copy live independently inside each surface's own data module, so the
"what media exists and what does it prove" framing drifts in wording, in
completeness, and in modality coverage:

- `apps/web/src/b2Evidence.ts` (PS-026) carries archive URI, archive SHA-256,
  rehydrate source, and provider-call counts, but framed only as B2 evidence,
  not as a per-modality artifact record.
- `apps/web/src/b2RehydrateComparison.ts` (PS-029) carries rehydrate evidence
  and a local-vs-remote framing, but no consolidated modality view.
- `apps/web/src/manifestVerification.ts` (PS-028) carries `manifest_uri` and a
  64-hex `manifest_hash`, but framed as manifest verification, not as the
  per-modality manifest reference for the underlying media.
- `apps/web/src/judgeEvidencePack.ts` (PS-031) carries final asset / archive
  summary and a "the pack does not include raw media bytes" boundary, but no
  consolidated multimodal view of which media modalities exist in the run.
- `apps/web/src/b2AuditVault.ts` (PS-036) carries archive / rehydrate audit
  framing and boundary red lines, but no per-modality artifact digest.
- `apps/web/src/reviewApprovalWorkspace.ts` (PS-035) carries an approval
  boundary, but no multimodal view of the reviewable artifact.
- `apps/web/src/trustBoundary.ts` + `apps/web/src/TrustBoundaryLayer.tsx`
  (PS-037) carry the shared disclosure boundary, but not a per-modality proof
  view of which media exists and what each modality does and does not prove.

Each surface is honest on its own, but a reviewer reading "what media exists
and what is it proven to be" sees a different framing on every surface, and
never sees a single honest answer to: is this artifact local / demo / golden
evidence or live evidence; is there a transcript / timestamp / voice / emotion /
campaign-intelligence proof, or is that honestly not available yet. That drift
is a judge-safety risk: an absent transcript that is silently omitted looks
like a hidden transcript; a deferred emotion analysis that is not stated looks
like a claim that no analysis is possible.

PS-037a closes that gap by adding one shared multimodal proof layer — a
canonical data module plus a shared component — that the core proof surfaces
render additively. The layer reads only accepted checked-in artifact evidence.
It does not invent new media, new hashes, new transcripts, or new provider
outputs. It is local / static by default: it adds no provider calls, no live
B2 reads, no B2 writes, no broad B2 scans, no new backend, no new env, and no
deployment changes.

## 4. User Story

As a reviewer (designer, marketer, reviewer, client, or judge), I want one
honest, consistent multimodal view of the artifact evidence in a run, so that
on any core proof surface I can immediately read: what media / artifact
exists; what modality it belongs to (image, video, audio, text, manifest, B2
archive, rehydrate, export pack); where the artifact reference is recorded;
what hash / digest / manifest evidence is recorded; whether the artifact is
local / demo / golden evidence or live evidence; whether provider activity
happened; whether B2 archive evidence exists; whether rehydrate evidence
exists; whether transcript / timestamp / voice / emotion / campaign-intelligence
evidence is absent, deferred, or later-slice owned — and so I never mistake a
media hash for semantic truth, an artifact reference for legal authenticity, a
manifest hash for human authorship, local artifact evidence for live B2
availability, or a demo / golden artifact for production security.

As a demo presenter, I want a reusable multimodal proof layer that is useful in
a three-minute hackathon demo: a compact per-modality summary that lists the
recorded artifact evidence and its honest "not available yet" states, plus an
expanded panel that states, verbatim, what each modality proves, what each
modality does not prove, what is deferred to a later slice, and what the shared
disclosure boundary is — all working offline from accepted local / golden /
demo fixtures, with no live provider calls, no live B2 reads, no B2 writes, and
no broad B2 scans.

## 5. Current Accepted Base

The current accepted base for PS-037a is:

- branch: `accepted/proofstudio`
- ref: `origin/accepted/proofstudio` (the authoritative source of truth; the
  ref is the authority, not any hardcoded commit hash)
- commit the ref resolves to at the time of this spec:
  `e8fb667ecbc299e00c6ec166feb576960039285b`
- this is the post-PS-037 accepted state: the Disclosure + Trust Boundary Layer
  from PS-037 is in place (`apps/web/src/trustBoundary.ts` +
  `apps/web/src/TrustBoundaryLayer.tsx`); the Archive / Rehydrate / B2 Audit
  Vault is in place from PS-036; the Review + Approval Workspace is in place
  from PS-035; the root `AGENTS.md` operating law is in place (PS-035D); the
  accepted-base-pointer-drift guard is in place (PS-035E); the central
  regression gate is non-mutating by default from PS-035C; the golden-fixture
  digest freeze is in place from PS-035B; the golden-run manifest carries a
  real non-null `manifest_uri` and a real 64-hex `manifest_hash` from PS-035A.

PS-037a must start from `origin/accepted/proofstudio`, not from `main`.

Relevant accepted facts at this base that PS-037a builds on (PS-037a must not
mutate these and must not change their values):

- the central regression gate (`scripts/proofstudio_regression_gate.py`)
  supports `--current`, `--frontend`, `--no-frontend`, `--check-only`,
  `--report-out`, and `--write-report` (PS-035C accepted)
- the gate is non-mutating by default for any current slice that is not
  PS-034A (PS-035C accepted)
- the root `AGENTS.md` operating law exists at the repository root (PS-035D
  accepted), including the rule that hidden Git flags `h` and `S` must be
  checked explicitly by reading `git ls-files -v` and failing when `line[0]`
  is `h` or `S`
- the accepted-base-pointer-drift guard exists (PS-035E accepted)
- the golden-fixture digest freeze exists at
  `docs/evidence/golden-fixture-digests.json` (PS-035B accepted)
- the golden-run manifest carries a real non-null `manifest_uri` and a real
  64-hex `manifest_hash` (PS-035A accepted), and the golden demo manifest at
  `docs/evidence/demo/golden-demo-run.json` carries `archive_uri`,
  `archive_sha256`, `manifest_uri`, `manifest_hash`, `rehydrate_source`, and an
  honest `unavailable_fields` map for values that are not present
- every existing core proof surface already records some artifact evidence
  (PS-021 through PS-036); PS-037a consolidates that evidence into one
  per-modality view, it does not invent new media or new hashes
- the PS-037 Disclosure + Trust Boundary Layer exists and is rendered on the
  core proof surfaces; PS-037a integrates with it and does not weaken it
- the existing shared component classes (`.trust-boundary`, pills, cards,
  `JsonExpander`, the `.trust-boundary-layer*` classes) already exist in
  `apps/web/src/styles.css`

## 6. Scope

PS-037a is a product slice. It adds a reusable multimodal proof layer (a shared
data module plus a shared component) and renders it additively on the core proof
surfaces. It is local / static by default: it must work without live provider
calls, without live B2 reads, without B2 writes, and without broad B2 scans, by
reading accepted local / golden / demo fixtures and existing accepted data
modules.

PS-037a must:

1. Add a shared, canonical multimodal proof data module
   (`apps/web/src/multimodalProof.ts`, or the project's accepted equivalent)
   that exposes one consistent set of multimodal proof concepts, per-modality
   artifact evidence, per-modality disclosure boundary, and honest "not
   available yet" / deferred states for every core proof surface.
2. Add a shared multimodal proof component
   (`apps/web/src/MultimodalProofLayer.tsx`, or the project's accepted
   equivalent) that renders the layer, including an optional compact
   per-modality summary and an expanded per-modality panel pattern, reading
   only from `apps/web/src/multimodalProof.ts`.
3. Render the multimodal proof layer additively on the required core proof
   surfaces (section 10.3) so the per-modality framing is consistent everywhere
   artifact evidence is shown.
4. State, per modality, "what ProofStudio proves" and "what ProofStudio does
   not prove."
5. Surface the canonical multimodal proof concepts (section 10.2): artifact
   evidence, modality, media kind, artifact reference, artifact digest,
   manifest reference, manifest hash, B2 evidence status, rehydrate evidence
   status, provider activity status, local verification, live verification
   status, disclosure boundary, not claimed, unknown, and deferred to later
   slice.
6. Surface, per modality, the honest deferred later-slice states (section 10.6)
   verbatim so no reviewer mistakes an absent transcript / timestamp / voice /
   emotion / campaign-intelligence proof for a hidden proof.
7. Surface the canonical multimodal de-escalation pairs (section 10.7) verbatim
   so no judge mistakes a strong-sounding artifact for a stronger guarantee.
8. Surface the canonical multimodal negative boundary strings (section 10.8)
   verbatim.
9. Integrate with the PS-037 TrustBoundaryLayer (render alongside it; reuse the
   shared disclosure concepts; do not duplicate or weaken the PS-037 boundary).
10. Preserve the existing per-surface artifact / boundary panels; the shared
    multimodal layer complements them. PS-037a must not delete or weaken any
    existing per-surface non-claim or per-surface artifact record.
11. Be demo-friendly and judge-friendly: useful in a three-minute demo, no
    generic AI hype copy, no unsupported claims, no faked modalities.
12. Work without provider calls, without live B2 reads, without B2 writes, and
    without broad B2 scans, by using accepted local / golden / demo data or
    existing accepted data paths.
13. Not mutate any prior evidence. Any PS-037a-owned evidence lives only under
    `docs/evidence/ps-037a/`.
14. Not change the golden run canonical constants, the historical contracts the
    regression gate verifies, any provider / B2 behavior, or the PS-037
    disclosure contract.

## 7. Non-goals

PS-037a must not:

- do not implement product code during the spec-only phase
- do not implement the later provider-specific slices:
  - PS-037b AssemblyAI Transcript / Timestamp Evidence (PS-037a must not fake
    transcripts or timestamps; it may only reserve honest "transcript evidence
    not available" / "timestamp evidence not available" states)
  - PS-037c Hume or ElevenLabs voiceover artifact (PS-037a must not fake voice
    analysis, emotion analysis, or a voiceover artifact; it may only reserve
    honest "voice evidence not available" / "emotion evidence not available"
    states)
  - PS-037d Gemini Campaign Intelligence / Judge Narrative (PS-037a must not
    fake campaign intelligence; it may only reserve an honest "campaign
    intelligence not available" state)
- do not fake transcripts, timestamps, voice analysis, emotion analysis,
  campaign intelligence, or any provider output that a later slice owns
- do not edit product code under `src/**`
- do not edit frontend code under `apps/**`
- do not edit scripts under `scripts/**`
- do not edit evidence under `docs/evidence/**`
- do not edit `AGENTS.md`
- do not edit `.env*`
- do not edit `render.yaml`
- do not edit requirements files
- do not run the frontend
- do not run the backend
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
- do not claim identity verification
- do not claim biometric identification
- do not claim deepfake detection
- do not claim content moderation
- do not claim OCR correctness
- do not claim transcript correctness
- do not claim timestamp correctness
- do not claim voice authenticity
- do not claim emotion truth
- do not claim model output truth
- do not delete or weaken any existing per-surface truth-boundary panel,
  non-claim, or artifact record
- do not add a new backend, a new provider wrapper, a new B2 client, a new
  env variable, or any deployment change
- do not build CI, billing, deployment, auth, teams, permissions, or a full
  enterprise DAM
- do not change the golden run canonical constants
- do not change the historical contracts the regression gate verifies
- do not change the PS-037 disclosure contract
- do not introduce a control name containing `KEY`, `TOKEN`, or `SECRET`
- do not use hidden Git flags (`assume-unchanged`, `skip-worktree`,
  `git update-index`, `update-index`)
- do not run recursive smokes
- do not use generic AI hype copy or unsupported claims

PS-037a only edits this spec file in the spec-only phase.
Implementation-phase candidate files are listed in section 8.

## 8. Implementation Candidate Files

The following are implementation-phase candidates only, clearly marked as
implementation-phase only. They are **not** for this spec-only commit. They are
listed so the implementation phase has a grounded file plan that follows
existing app conventions (each surface has a PascalCase `.tsx` component, a
camelCase `.ts` data module, a smoke script, and an evidence directory).

Shared layer (new files):
- `apps/web/src/multimodalProof.ts` (new) — the canonical camelCase multimodal
  proof data module. Exposes the single shared set of multimodal proof
  concepts, per-modality artifact evidence, per-modality disclosure boundary,
  honest deferred later-slice states, de-escalation pairs, negative boundary
  strings, and not-claimed / unknown / deferred status used by every core proof
  surface. Same convention as `trustBoundary.ts`, `b2Evidence.ts`,
  `b2RehydrateComparison.ts`, `judgeEvidencePack.ts`, etc.
- `apps/web/src/MultimodalProofLayer.tsx` (new) — the shared multimodal proof
  component. Accepts the existing `variant` convention (for example
  `variant="panel"` for an expanded per-modality panel and `variant="badge"` /
  `variant="summary"` for a compact per-modality summary), reads only from
  `apps/web/src/multimodalProof.ts`, and renders the multimodal proof layer
  with no provider calls and no live B2 reads. Rendered alongside the existing
  `TrustBoundaryLayer` so the PS-037 disclosure boundary stays canonical.

Additive use on core proof surfaces (existing files, edited additively only):
- `apps/web/src/JudgeCockpitHome.tsx` (PS-023) — render the multimodal proof
  layer on the home surface.
- `apps/web/src/B2EvidenceExplorer.tsx` (PS-026) — render the multimodal proof
  layer (B2 archive + rehydrate modalities).
- `apps/web/src/B2RehydrateComparison.tsx` (PS-029) — render the multimodal
  proof layer (rehydrate evidence status modality).
- `apps/web/src/ManifestVerificationPanel.tsx` (PS-028) — render the multimodal
  proof layer (manifest reference + manifest hash modalities).
- `apps/web/src/B2AuditVault.tsx` (PS-036) — render the multimodal proof layer
  (archive / rehydrate audit modalities).
- `apps/web/src/ReviewApprovalWorkspace.tsx` (PS-035) — render the multimodal
  proof layer (the reviewable artifact's modalities).
- `apps/web/src/JudgeEvidencePack.tsx` (PS-031) — render the multimodal proof
  layer (export-pack artifact summary).
- `apps/web/src/PublicPassportPage.tsx` (PS-019) — render the multimodal proof
  layer (provenance passport artifact evidence).
- `apps/web/src/App.tsx` (PS-013 / PS-014) — render the multimodal proof layer
  on the Review Room, complementing the existing asset / manifest / evidence
  panels and the existing PS-037 disclosure layer.

Additive styles (existing file, additive classes only):
- `apps/web/src/styles.css` — add only the classes needed for the multimodal
  proof layer (per-modality rows, modality pills, artifact-reference rows,
  artifact-digest rows, disclosure-boundary rows, deferred-state pills). No
  global style rewrite. PS-037a must not remove or weaken the existing
  `.trust-boundary-layer*` classes from PS-037.

Backend (`src/proofstudio`) — none:
- PS-037a is a frontend-only multimodal proof layer over existing accepted
  data. No backend change is expected. If any read-only reuse of an accepted
  data path is needed, it must reuse the existing accepted data paths under
  `src/proofstudio/api/` and `src/proofstudio/provenance/` without calling
  providers and without reading live B2. No new provider wiring, no new B2
  client, no new B2 write path, no new broad B2 scan path. If no backend change
  is needed, none is made.

Smoke (scripts):
- `scripts/ps037a_multimodal_proof_layer_smoke.py` (new) — the PS-037a feature
  smoke. Must reuse `scripts/smoke_lib.py` for shared validation logic and must
  implement its own explicit `h` / `S` hidden-Git-flags checker (see
  section 14). Local / static only.

Spec / docs:
- `specs/07-master-spec-plan.md` — implementation-phase cross-reference only
  (register PS-037a acceptance). Must not change any historical item or golden
  constant.
- `specs/08-roadmap-slices.md` — implementation-phase status update only.
- `docs/validation/proofstudio-smoke-harness-v1.md` — implementation-phase
  PS-037a note only, additive, must not weaken any existing PS-034A / PS-035C
  contract.
- `docs/ps-037a-multimodal-proof-layer-proof.md` (new) — the PS-037a proof
  doc.

Evidence:
- `docs/evidence/ps-037a/multimodal-proof-layer-report.json` (new) — the only
  evidence PS-037a may write, and only when `--write-evidence` is explicit.

Any edit to `src/proofstudio/**` during implementation requires the backend
change to remain read-only over accepted data and to make no provider call and
no live B2 read.

## 9. Forbidden files Unless PM-approved Later

PS-037a implementation must not touch without explicit PM approval:

- `AGENTS.md`
- `.env*`
- `render.yaml`
- requirements files
- `docs/evidence/**` paths other than `docs/evidence/ps-037a/**`
- any prior-slice evidence prefix (for example `docs/evidence/ps-037/**`,
  `docs/evidence/ps-036/**`, `docs/evidence/ps-035/**`,
  `docs/evidence/ps-031/**`, `docs/evidence/ps-029/**`,
  `docs/evidence/ps-026/**`, `docs/evidence/ps-021/**`,
  `docs/evidence/demo/golden-demo-run.json`,
  `docs/evidence/golden-fixture-digests.json`)
- `scripts/proofstudio_regression_gate.py` (the central gate is not owned by
  PS-037a)
- `scripts/smoke_lib.py` (shared library; PS-037a must not mutate shared
  validation behavior)
- any provider wrapper under `src/proofstudio/providers/**` (PS-037a owns no
  provider behavior; PS-037b / PS-037c / PS-037d own the provider-specific
  later slices)
- any B2 client / storage write path (PS-037a performs no live B2 read, no B2
  write, and no broad B2 scan)
- the PS-037 disclosure contract files (`apps/web/src/trustBoundary.ts`,
  `apps/web/src/TrustBoundaryLayer.tsx`) except for additive integration; any
  change that weakens or duplicates the PS-037 boundary is forbidden

The only implementation-phase files allowed without PM approval are those in
section 8. Any other path requires explicit PM approval.

## 10. Multimodal Proof Product Contract

PS-037a defines the following contract for the Multimodal Proof Layer.

### 10.1 Layer identity

- It is a reusable multimodal proof-inspection layer, not a new proof surface,
  not a new route, and not a new backend endpoint.
- It is purely client-side by default: it calls no provider, reads no B2
  object, exposes no arbitrary `run_id` input, performs no browser-side B2
  byte verification, performs no broad B2 scan, and writes no B2 object.
- It is sourced from accepted local / golden / demo data and existing accepted
  data modules only.
- It makes the per-modality framing consistent on every core proof surface. It
  does not invent new media, new hashes, new transcripts, or new provider
  outputs; it states the existing recorded artifact evidence consistently and
  honestly.
- It integrates with the PS-037 Disclosure + Trust Boundary Layer: it renders
  alongside `TrustBoundaryLayer` and reuses the shared disclosure concepts, and
  must not duplicate or weaken the PS-037 boundary.

### 10.2 Required multimodal proof concepts

The layer must surface these canonical multimodal proof concepts, each as a
clearly labeled per-modality item:

- `artifact evidence` — what media / artifact exists, per modality, that the
  pipeline recorded.
- `modality` — the modality bucket the artifact belongs to (image, video,
  audio, text, manifest, B2 archive, rehydrate, export pack).
- `media kind` — the concrete media kind recorded (for example image, video,
  audio, text).
- `artifact reference` — where the artifact reference is recorded (for example
  `archive_uri`, `manifest_uri`, asset id).
- `artifact digest` — the hash / digest recorded for the artifact (for example
  `archive_sha256`), honestly surfaced or honestly unavailable.
- `manifest reference` — the recorded `manifest_uri`.
- `manifest hash` — the recorded 64-hex `manifest_hash`.
- `B2 evidence status` — whether B2 archive evidence is recorded, and whether
  it is recorded-only or live-verified (recorded-only by default).
- `rehydrate evidence status` — whether rehydrate evidence is recorded.
- `provider activity status` — whether provider activity happened for the
  surfaced evidence (no provider calls by default).
- `local verification` — whether evidence is locally verified against
  checked-in / accepted data.
- `live verification status` — whether a live check is in scope (local /
  check-only by default).
- `disclosure boundary` — the per-modality disclosure boundary, sourced from /
  consistent with PS-037.
- `not claimed` — the honest set of things ProofStudio does not claim, per
  modality.
- `unknown` — what remains unknown or not surfaced.
- `deferred to later slice` — what is honestly owned by a later slice
  (PS-037b / PS-037c / PS-037d).

If a concept does not apply to a given modality, the layer must show an honest
"not applicable" / "unknown" / "deferred to later slice" state and must not
fabricate a value.

### 10.3 Required surfaces

The multimodal proof layer must be rendered (additively) on at least these
required core proof surfaces, so
`required_surfaces_have_multimodal_proof` is truthful:

- Judge Cockpit Home (`apps/web/src/JudgeCockpitHome.tsx`, path `/`)
- B2 Evidence Explorer (`apps/web/src/B2EvidenceExplorer.tsx`, path
  `/b2-evidence`)
- Manifest Verification Panel (`apps/web/src/ManifestVerificationPanel.tsx`,
  path `/manifest-verification`)
- B2 Rehydrate Comparison (`apps/web/src/B2RehydrateComparison.tsx`, path
  `/b2-rehydrate-comparison`)
- Archive / Rehydrate / B2 Audit Vault (`apps/web/src/B2AuditVault.tsx`, path
  `/b2-audit-vault`)
- Review + Approval Workspace (`apps/web/src/ReviewApprovalWorkspace.tsx`,
  path `/review-approval-workspace`)
- Judge Evidence Pack (`apps/web/src/JudgeEvidencePack.tsx`, path
  `/evidence-pack`)
- Public Provenance Passport (`apps/web/src/PublicPassportPage.tsx`, path
  `/passport/:id`)
- Review Room (`apps/web/src/App.tsx`, path `/review`)

Additional accepted surfaces (Genblaze Pipeline Graph, Failure-as-Proof
Timeline, Operations Cockpit, Provider Decision Intelligence, Lineage +
Comparison Lab) may render the layer but are not required for the minimum
contract. The smoke validates presence only on surfaces that are present in
this repo (section 14).

### 10.4 Modality set

The layer covers the modalities that already exist in accepted checked-in
evidence:

- image
- video
- audio
- text
- manifest
- B2 archive
- rehydrate
- export pack

For each modality, the layer records honestly whether artifact evidence exists
in accepted data, whether it is local / demo / golden evidence or live
evidence, and what it proves and does not prove. The layer must not invent a
modality that is not backed by accepted evidence or by an honest "not available
yet" state.

### 10.5 Local / live evidence honesty

The layer must distinguish clearly between:

- local artifact evidence (manifest hashes, archive references, digests,
  provider-call counts, rehydrate sources recorded in accepted checked-in
  data)
- live evidence (none, by default — PS-037a performs no live B2 read and no
  provider call)
- demo / golden evidence (the golden demo run, which is local / golden, not
  production)

A reviewer reading the layer must never mistake local artifact evidence for
live B2 availability, or a demo / golden artifact for production security.

### 10.6 Required deferred later-slice states (verbatim)

The layer must surface, per modality and honestly, these deferred later-slice
states verbatim. These are non-claim states: they state what is not available
yet, owned by a later slice, and must never be read as a hidden proof:

- transcript evidence not available (deferred to PS-037b)
- timestamp evidence not available (deferred to PS-037b)
- voice evidence not available (deferred to PS-037c)
- emotion evidence not available (deferred to PS-037c)
- campaign intelligence not available (deferred to PS-037d)

PS-037a must not fake a transcript, a timestamp, a voiceover, a voice / emotion
analysis, or a campaign intelligence / judge narrative. The deferred states are
the only acceptable representation of those modalities in PS-037a.

### 10.7 Required de-escalation pairs (verbatim)

The layer must surface these multimodal de-escalation pairs verbatim so a judge
never mistakes a strong-sounding artifact for a stronger guarantee:

- proof does not equal truth
- artifact reference does not equal legal authenticity
- media hash does not equal semantic truth
- manifest hash does not equal human authorship
- local artifact evidence does not equal live B2 availability
- demo/golden artifact does not equal production security

### 10.8 Required negative boundary strings (verbatim)

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
- not identity verification
- not biometric identification
- not deepfake detection
- not content moderation
- not OCR correctness
- not transcript correctness
- not timestamp correctness
- not voice authenticity
- not emotion truth
- not model output truth

### 10.9 Boundary honesty

The layer must not imply that any ProofStudio artifact proves anything beyond
what the pipeline recorded. In particular it must not imply that a media hash,
a manifest hash, an artifact reference, a rehydrate source, or an export pack
proves semantic truth, legal authenticity, human authorship, C2PA
authenticity, identity, biometric identity, deepfake absence, content-policy
compliance, OCR correctness, transcript correctness, timestamp correctness,
voice authenticity, emotion truth, or model output truth.

## 11. UI/UX Contract

The Multimodal Proof Layer UI must include:

- A clear title: "Multimodal Proof Layer" (or an equivalent clear title), with
  a positioning line that ProofStudio proves what the pipeline recorded, per
  modality.
- A compact per-modality summary variant (for example `variant="summary"` or
  `variant="badge"`) that lists, in one compact block, the recorded modalities
  and their honest "not available yet" states, suitable for surfaces where
  space is constrained.
- An expanded per-modality panel variant (for example `variant="panel"`) that
  states, in full, the multimodal proof contract per modality.
- A per-modality list that, for each modality present in accepted data, shows:
  modality, media kind, artifact reference, artifact digest, manifest
  reference, manifest hash, B2 evidence status, rehydrate evidence status,
  provider activity status, local verification, and live verification status.
- A "deferred to later slice" section listing, verbatim, the honest
  not-available-yet states (section 10.6).
- A "not claimed" section listing, per modality, what ProofStudio does not
  prove (section 10.8).
- The de-escalation pairs (section 10.7), surfaced verbatim.
- The negative boundary strings (section 10.8), surfaced verbatim.
- A persistent per-modality boundary statement that states verbatim (or
  equivalent):

  > ProofStudio proves what the pipeline recorded. Proof does not equal truth.
  > An artifact reference does not equal legal authenticity. A media hash does
  > not equal semantic truth. A manifest hash does not equal human authorship.
  > Local artifact evidence does not equal live B2 availability. A demo/golden
  > artifact does not equal production security.

- Integration with the PS-037 Disclosure + Trust Boundary Layer: the
  multimodal proof layer renders alongside `TrustBoundaryLayer`, reuses the
  shared disclosure concepts, and never contradicts the PS-037 boundary.

UI / UX constraints:

- Must be useful in a three-minute hackathon demo: open any core proof surface
  -> read the compact per-modality summary -> expand the multimodal proof panel
  -> read what each modality proves -> read what each modality does not prove
  -> read the deferred later-slice states -> read the de-escalation pairs ->
  read the negative boundary strings.
- Must render the same per-modality framing on every required surface
  (section 10.3).
- Must not introduce generic AI hype copy.
- Must not add unsupported claims.
- Must not fabricate modalities, statuses, digests, or provider outputs that
  are not in accepted data.
- Must follow the existing component conventions (`variant`, pills, cards,
  `JsonExpander`, the `.trust-boundary` and `.trust-boundary-layer*` styles)
  used by the other surfaces.
- Must not delete or weaken any existing per-surface truth-boundary panel,
  per-surface artifact record, or the PS-037 disclosure layer; the multimodal
  layer is additive.

## 12. Data Contract

### 12.1 Source data (read-only inputs)

PS-037a reads accepted local / golden / demo data and existing accepted data
modules as immutable inputs. It must not mutate these and must not change their
canonical values. Acceptable read-only sources:

- `apps/web/src/trustBoundary.ts` (PS-037) — reuse the shared disclosure
  concepts; do not duplicate or weaken them
- `apps/web/src/b2Evidence.ts` (PS-026) — archive URI, archive SHA-256,
  rehydrate source, provider-call counts
- `apps/web/src/b2RehydrateComparison.ts` (PS-029) — rehydrate evidence
- `apps/web/src/manifestVerification.ts` (PS-028) — `manifest_uri`,
  `manifest_hash`
- `apps/web/src/failureAsProofTimeline.ts` (PS-030)
- `apps/web/src/judgeEvidencePack.ts` (PS-031) — final asset / archive summary
- `apps/web/src/operationsCockpit.ts` (PS-032)
- `apps/web/src/providerDecisionIntelligence.ts` (PS-033)
- `apps/web/src/lineageComparisonLab.ts` (PS-034)
- `apps/web/src/reviewApprovalWorkspace.ts` (PS-035)
- `apps/web/src/b2AuditVault.ts` (PS-036)
- `apps/web/src/api.ts` (passport / trust_boundary shape exposed by the
  Provenance Passport)
- `docs/evidence/demo/golden-demo-run.json` — `archive_uri`, `archive_sha256`,
  `manifest_uri`, `manifest_hash`, `rehydrate_source`,
  `provider_calls_during_rehydrate`, and the honest `unavailable_fields` map
- `docs/evidence/golden-fixture-digests.json`

PS-037a must not change the golden run canonical constants. The canonical
constants are owned by their respective accepted slices.

### 12.2 Multimodal proof item shape

A multimodal proof item is derived from accepted data and must expose:

- `modality` (stable; one of the modalities in section 10.4)
- `media_kind` (the concrete media kind, or honestly "not available yet")
- `artifact_reference` (where the reference is recorded, or honestly
  unavailable)
- `artifact_digest` (the recorded hash / digest, or honestly unavailable)
- `manifest_reference` (the recorded `manifest_uri`, or honestly unavailable)
- `manifest_hash` (the recorded 64-hex `manifest_hash`, or honestly
  unavailable)
- `b2_evidence_status` (recorded-only by default)
- `rehydrate_evidence_status`
- `provider_activity_status` (no provider calls by default)
- `local_verification` (locally verified against accepted checked-in data)
- `live_verification_status` (local / check-only by default)
- `disclosure_boundary` (sourced from / consistent with PS-037)
- `label` (the human-readable label, matching the verbatim strings in
  section 21)
- `value` (the proof value, honest about local / recorded-only / unknown /
  deferred)
- `applicable` (boolean; false when the concept honestly does not apply to the
  modality)
- `state` (one of `recorded`, `locally_verified`, `recorded_only`,
  `not_verified`, `not_claimed`, `unknown`, `deferred_to_later_slice`)

### 12.3 Evidence report schema rule

The PS-037a evidence report must follow the harness schema rule: boolean
fields remain booleans and detail / list fields use explicit detail names. A
field whose name implies a boolean success flag must remain a boolean. List
fields must use explicit detail names such as `_ids`, `_details`, or
`_failures` (see section 13).

## 13. Evidence Contract

PS-037a owns exactly one evidence directory: `docs/evidence/ps-037a/`.

- A feature smoke may write only its own evidence, and only when
  `--write-evidence` is explicit. The default PS-037a smoke behavior is
  non-mutating local validation.
- PS-037a must not write any file outside `docs/evidence/ps-037a/`.
- PS-037a must not mutate any prior-slice evidence (every prior evidence prefix
  is guarded by `scripts/smoke_lib.py` and
  `scripts/proofstudio_regression_gate.py`), including the PS-037 evidence
  under `docs/evidence/ps-037/`.
- The PS-037a evidence file is
  `docs/evidence/ps-037a/multimodal-proof-layer-report.json`.

The PS-037a evidence report must carry these boolean fields (booleans as
booleans; `failures` as a list):

- `ok` (boolean; true only when every measured field is truthful and no
  forbidden overclaim or forbidden file change is present)
- `slice_id`: `ps037a`
- `multimodal_proof_component_present` (boolean; `MultimodalProofLayer`
  component exists)
- `multimodal_proof_data_module_present` (boolean; `multimodalProof.ts` exists)
- `multimodal_proof_layer_present` (boolean; the shared layer is wired in)
- `required_surfaces_have_multimodal_proof` (boolean; the required surfaces in
  section 10.3 that are present in this repo render the layer)
- `artifact_evidence_present` (boolean)
- `modality_present` (boolean)
- `media_kind_present` (boolean)
- `artifact_reference_present` (boolean)
- `artifact_digest_present` (boolean)
- `manifest_reference_present` (boolean)
- `manifest_hash_present_or_honestly_unavailable` (boolean)
- `b2_evidence_status_present` (boolean)
- `rehydrate_evidence_status_present` (boolean)
- `provider_activity_status_present` (boolean)
- `local_verification_status_present` (boolean)
- `live_verification_status_present` (boolean)
- `disclosure_boundary_present` (boolean)
- `not_claimed_status_present` (boolean)
- `unknown_status_present` (boolean)
- `later_slice_deferred_status_present` (boolean)
- `transcript_evidence_not_available_present` (boolean)
- `timestamp_evidence_not_available_present` (boolean)
- `voice_evidence_not_available_present` (boolean)
- `emotion_evidence_not_available_present` (boolean)
- `campaign_intelligence_not_available_present` (boolean)
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
- `no_identity_verification_claim` (boolean)
- `no_biometric_identification_claim` (boolean)
- `no_deepfake_detection_claim` (boolean)
- `no_content_moderation_claim` (boolean)
- `no_ocr_correctness_claim` (boolean)
- `no_transcript_correctness_claim` (boolean)
- `no_timestamp_correctness_claim` (boolean)
- `no_voice_authenticity_claim` (boolean)
- `no_emotion_truth_claim` (boolean)
- `no_model_output_truth_claim` (boolean)
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

PS-037a ships one feature smoke:
`scripts/ps037a_multimodal_proof_layer_smoke.py`.

The PS-037a feature smoke must:

- validate only the PS-037a slice (no recursive smokes; must never launch
  another feature smoke as a subprocess; must never call the central regression
  gate)
- read checked-in prior evidence and accepted data modules as immutable inputs
- write only its own evidence file
  `docs/evidence/ps-037a/multimodal-proof-layer-report.json`, and only when
  `--write-evidence` is explicit
- never call a provider
- never read arbitrary B2 objects (no live B2 reads)
- never write B2 (no B2 writes)
- never perform broad B2 scans
- never run the frontend typecheck / build (that belongs to the central gate)
- reuse `scripts/smoke_lib.py` for shared validation logic
- validate the shared `MultimodalProofLayer` component is present
- validate the shared `multimodalProof.ts` data module is present
- validate the multimodal proof layer is rendered on the required proof
  surfaces that are present in this repo (section 10.3)
- validate the required multimodal proof UI strings (section 21) are present
- validate the required negative boundary strings (section 21) are present
- validate the deferred later-slice states (section 10.6) are present and
  honest
- validate no provider calls are introduced
- validate no live B2 reads are introduced
- validate no B2 writes are introduced
- validate no broad B2 scans are introduced
- validate no forbidden overclaims are introduced
- validate no recursive smokes (the smoke must not launch another feature
  smoke)
- validate no hidden Git flags `h` or `S` with an explicit h/S checker that
  reads `git ls-files -v` and fails when `line[0]` is `h` or `S` (a
  lowercase-only marker check is not sufficient because it misses uppercase `S`
  skip-worktree)
- validate the bad lowercase-only hidden-flag command literal is absent from
  the PS-037a changed files, without the smoke or this spec reproducing that
  literal
- validate prior evidence is unchanged
- validate `git diff --check` is clean
- do not scan smoke guard fixtures as product claims (the future PS-037a smoke
  and its evidence report are the source of truth for slice overclaim
  validation; smoke guard fixtures are not product claims)

The PS-037a feature smoke must support these standard flags:

- `--check-only` (default: non-mutating local validation; no evidence file is
  written)
- `--write-evidence` (write only `docs/evidence/ps-037a/` evidence)
- `--no-frontend`

Default PS-037a smoke behavior is non-mutating local validation
(`--check-only`).

The smoke must not contain the bad lowercase-only hidden-flag marker check and
must not rely on a lowercase-only marker check. The hidden-Git-flags check must
be the explicit `h` / `S` checker over `git ls-files -v`, and must record
`no_hidden_git_flags_h` and `no_hidden_git_flags_S` as separate booleans.

PS-037a smoke performs no provider calls, no live B2 reads, no B2 writes, and
no broad B2 scans.

## 15. Regression Gate Contract

The central regression gate remains the single cross-slice release-readiness
gate and is non-mutating by default. PS-037a does not own or modify the central
gate.

Normal PS-037a release validation command:

```
python scripts/proofstudio_regression_gate.py --current ps037a --frontend --report-out /tmp/proofstudio-release-report.json
```

Contract-only gate (no frontend):

```
python scripts/proofstudio_regression_gate.py --current ps037a --no-frontend --report-out /tmp/proofstudio-ps037a-regression-report.json
```

- The gate runs `npm run typecheck` and `npm run build` in `apps/web` exactly
  once per invocation, and only when `--frontend` is passed. PS-037a feature
  smoke must never trigger nested frontend builds.
- The gate must not write the canonical PS-034A report. `--write-report` is
  rejected for `--current ps037a` (PS-035C accepted behavior; only PS-034A may
  regenerate the canonical report).
- Running the gate for `ps037a` must leave all prior-slice evidence unchanged,
  including the PS-037 evidence.
- No recursive smokes: the gate never executes a feature smoke.

Canonical PS-034A regeneration (unchanged, owned by PS-034A only):

```
python scripts/proofstudio_regression_gate.py --current ps034a --write-report
```

## 16. Truth Boundary

ProofStudio proves what the pipeline recorded. The Multimodal Proof Layer is a
proof-inspection surface that makes the per-modality artifact evidence
explicit and consistent on every core proof surface. It is not a legal
authenticity system, not a live B2 verifier, not a truth system, not an
identity system, not a biometric system, not a deepfake detector, not a content
moderator, not an OCR verifier, not a transcript verifier, not a timestamp
verifier, not a voice verifier, and not an emotion verifier.

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
- do not claim production security
- do not claim production compliance
- do not claim legal review
- do not claim chain-of-custody guarantees beyond recorded pipeline evidence
- do not claim identity verification
- do not claim biometric identification
- do not claim deepfake detection
- do not claim content moderation
- do not claim OCR correctness
- do not claim transcript correctness
- do not claim timestamp correctness
- do not claim voice authenticity
- do not claim emotion truth
- do not claim model output truth
- do not claim actual spend / latency / quota unless captured
- do not claim provider failures / reruns / variants unless evidenced

PS-037a does not prove product correctness, production security, production
compliance, B2 immutability, Object Lock, tamper-proof storage, browser-side B2
byte verification, live B2 availability, real billing API integration, billing
behavior, CI enforcement, legal review, identity, biometric identity, deepfake
absence, content-policy compliance, OCR correctness, transcript correctness,
timestamp correctness, voice authenticity, emotion truth, model output truth,
or deployment readiness. No PS-037a artifact may imply any of these. The
multimodal proof layer states what the pipeline already recorded; it does not
re-fetch, re-hash, or re-verify live B2 bytes, and it does not call providers.

## 17. Later-slice Boundaries

PS-037a must not implement, fake, or claim the later provider-specific slices.
The boundaries are:

- PS-037b AssemblyAI Transcript / Timestamp Evidence — owns transcript and
  timestamp evidence. PS-037a must only reserve honest "transcript evidence not
  available" and "timestamp evidence not available" states. PS-037a must not
  produce, store, or claim a transcript or timestamp.
- PS-037c Hume or ElevenLabs voiceover artifact — owns voice and emotion
  evidence and any voiceover artifact. PS-037a must only reserve honest "voice
  evidence not available" and "emotion evidence not available" states. PS-037a
  must not produce, store, or claim a voiceover, a voice analysis, or an
  emotion analysis.
- PS-037d Gemini Campaign Intelligence / Judge Narrative — owns campaign
  intelligence and the judge narrative. PS-037a must only reserve an honest
  "campaign intelligence not available" state. PS-037a must not produce, store,
  or claim a campaign intelligence output or a judge narrative.

PS-037a may reserve fields and honest "not available yet" states for those
later slices, but must not fake transcripts, timestamps, voice analysis,
emotion analysis, campaign intelligence, or any provider output.

## 18. Risks

PS-037a must record the following risks with mitigations:

- overclaim risk
  - risk: a reviewer misreads the multimodal proof layer or its copy as a
    forbidden overclaim — i.e. as claiming semantic truth, legal authenticity,
    human authorship, C2PA authenticity, Object Lock / tamper-proof storage,
    browser-side B2 byte verification, live B2 availability, production
    security, production compliance, legal review, chain-of-custody guarantees
    beyond recorded pipeline evidence, identity verification, biometric
    identification, deepfake detection, content moderation, OCR correctness,
    transcript correctness, timestamp correctness, voice authenticity, emotion
    truth, or model output truth. ProofStudio does not claim any of these.
  - mitigation: the persistent per-modality boundary statement (section 11) is
    mandatory; the truth-boundary red lines (section 16) are preserved verbatim;
    the de-escalation pairs (section 10.7) and negative boundary strings
    (section 10.8) are surfaced verbatim; the evidence report carries
    `no_forbidden_overclaims` and `truth_boundary_preserved`.
- deferred-state faking risk
  - risk: a later-slice modality (transcript, timestamp, voice, emotion,
    campaign intelligence) is silently represented as present when it is not,
    or is silently omitted so it looks hidden.
  - mitigation: the deferred later-slice states (section 10.6) are surfaced
    verbatim and honestly; the smoke validates their presence; PS-037a never
    produces those provider outputs.
- modality drift / inconsistency risk
  - risk: a surface keeps a divergent local artifact framing that contradicts
    the shared multimodal layer.
  - mitigation: the shared layer is rendered on every required surface
    (section 10.3); the smoke validates `required_surfaces_have_multimodal_proof`;
    existing per-surface panels are preserved, not weakened.
- de-escalation-gap risk
  - risk: a judge mistakes a media hash for semantic truth, an artifact
    reference for legal authenticity, a manifest hash for human authorship,
    local artifact evidence for live B2 availability, or a demo / golden
    artifact for production security.
  - mitigation: the de-escalation pairs in section 10.7 are surfaced verbatim.
- live-B2-read risk
  - risk: the layer triggers a live B2 read or a broad B2 scan.
  - mitigation: the layer is purely client-side over accepted data; the smoke
    enforces `no_live_b2_reads`, `no_b2_writes`, `no_broad_b2_scans`.
- evidence-mutation risk
  - risk: the PS-037a smoke or the central gate run overwrites prior-slice
    evidence, including PS-037 evidence.
  - mitigation: PS-037a writes only `docs/evidence/ps-037a/`; the gate is
    non-mutating by default; prior evidence prefixes are guarded.
- hidden-Git-flags risk
  - risk: a session uses `assume-unchanged`, `skip-worktree`, or
    `git update-index` / `update-index` to mask a dirty tree, including the
    uppercase `S` skip-worktree flag that a lowercase-only marker check misses.
  - mitigation: the operating law forbids these verbatim; the smoke uses the
    explicit `h` / `S` checker over `git ls-files -v` and fails on `line[0]`
    being `h` or `S`, recording `no_hidden_git_flags_h` and
    `no_hidden_git_flags_S` as separate booleans.
- PS-037 weakening risk
  - risk: the multimodal layer duplicates, contradicts, or weakens the PS-037
    Disclosure + Trust Boundary Layer.
  - mitigation: the multimodal layer renders alongside `TrustBoundaryLayer`,
    reuses the shared disclosure concepts, and never contradicts the PS-037
    boundary; PS-037a does not edit the PS-037 disclosure contract except
    additively (section 9).
- scope-creep risk
  - risk: PS-037a expands into PS-037b / PS-037c / PS-037d provider behavior,
    CI, billing, deployment, auth, teams, permissions, a full enterprise DAM,
    a new backend, or a live B2 fetcher.
  - mitigation: section 7 lists these as non-goals; section 9 forbids the
    relevant paths; section 17 fixes the later-slice boundaries.
- recursive-smoke risk
  - risk: the PS-037a smoke launches another feature smoke or calls the central
    gate.
  - mitigation: the smoke must never launch another feature smoke as a
    subprocess and must never call the central regression gate; the central
    gate is the only cross-slice validator.

## 19. Acceptance Criteria

PS-037a (spec-only phase) is accepted only when:

- this spec exists at `specs/55-ps-037a-multimodal-proof-layer.md`
- only this spec file is changed in the spec-only phase
- the branch `ps-037a/multimodal-proof-layer` starts from
  `origin/accepted/proofstudio` at commit
  `e8fb667ecbc299e00c6ec166feb576960039285b` (the merge-base equals that
  commit)
- the product scope is clear and does not expand into CI, billing, deployment,
  provider calls, live B2 reads, B2 writes, broad B2 scans, or the later slices
  PS-037b / PS-037c / PS-037d
- the required multimodal proof concepts (section 10.2), the modality set
  (section 10.4), and the required surfaces (section 10.3) are specified
- the deferred later-slice states (section 10.6), the de-escalation pairs
  (section 10.7), and the negative boundary strings (section 10.8) are
  specified verbatim
- the UI / UX contract (section 11) and the persistent per-modality boundary
  statement are specified
- the data contract (section 12) reuses accepted checked-in evidence as
  read-only inputs
- the truth boundary (section 16) is explicit and the boundary copy is
  specified
- the later-slice boundaries (section 17) are fixed
- the implementation candidate files (section 8) are listed, but no
  implementation is done in this phase
- the validation plan uses the PS-037a feature smoke plus the central
  regression gate (sections 14 and 15)
- no evidence mutation occurs in this phase
- no hidden Git flags `h` or `S` are present (verified by the explicit h/S
  checker over `git ls-files -v`)
- `git diff --check` is clean
- no staging, commit, or push occurs until PM approval
- `AGENTS.md`, `specs/07-master-spec-plan.md`, and
  `specs/08-roadmap-slices.md` are not changed in this phase

Implementation-phase acceptance (for reference, not this phase) additionally
requires: the shared `MultimodalProofLayer` component + `multimodalProof.ts`
data module exist; the multimodal proof layer is rendered on the required
surfaces present in this repo (section 10.3); the required multimodal proof
concepts, deferred later-slice states, de-escalation pairs, and negative
boundary strings are present; the PS-037a smoke passes in `--check-only`
(default) and writes only `docs/evidence/ps-037a/**` under `--write-evidence`;
the central gate passes for `--current ps037a`; no provider call, no live B2
read, no B2 write, no broad B2 scan occurs; prior evidence is unchanged,
including PS-037 evidence; no forbidden overclaim is introduced; the PS-037
disclosure boundary is not weakened.

## 20. Rollback

Rollback of the PS-037a spec-only phase is a single revert of this spec commit,
because only `specs/55-ps-037a-multimodal-proof-layer.md` is changed in this
phase.

Future implementation rollback must restore the pre-PS-037a state of the edited
files in section 8. Specifically:

- remove `apps/web/src/multimodalProof.ts`
- remove `apps/web/src/MultimodalProofLayer.tsx`
- revert the additive multimodal-proof-layer renders in
  `apps/web/src/JudgeCockpitHome.tsx`,
  `apps/web/src/B2EvidenceExplorer.tsx`,
  `apps/web/src/B2RehydrateComparison.tsx`,
  `apps/web/src/ManifestVerificationPanel.tsx`,
  `apps/web/src/B2AuditVault.tsx`,
  `apps/web/src/ReviewApprovalWorkspace.tsx`,
  `apps/web/src/JudgeEvidencePack.tsx`,
  `apps/web/src/PublicPassportPage.tsx`, and
  `apps/web/src/App.tsx` to pre-PS-037a state
- revert the additive multimodal-proof-layer classes in
  `apps/web/src/styles.css` to pre-PS-037a state
- remove `scripts/ps037a_multimodal_proof_layer_smoke.py`
- remove `docs/ps-037a-multimodal-proof-layer-proof.md`
- remove `docs/evidence/ps-037a/` if it was added
- revert the additive cross-references in `specs/07-master-spec-plan.md`,
  `specs/08-roadmap-slices.md`, and
  `docs/validation/proofstudio-smoke-harness-v1.md` to pre-PS-037a state

Rollback of PS-037a must not touch any evidence under `docs/evidence/**` other
than `docs/evidence/ps-037a/`, must not touch the central gate
(`scripts/proofstudio_regression_gate.py`), `scripts/smoke_lib.py`,
`AGENTS.md`, `.env*`, `render.yaml`, requirements files, any provider wrapper,
any B2 storage path, or the PS-037 disclosure contract. Rollback is isolated
and reversible because PS-037a is a self-contained multimodal proof layer over
existing accepted data; it does not change provider behavior, B2 behavior,
billing behavior, deployment topology, or the PS-037 boundary.

## 21. Verbatim implementation/audit contract strings

The PS-037a implementation, the Multimodal Proof Layer UI, the PS-037a smoke,
and the PS-037a evidence report must preserve the following exact strings so
the multimodal proof contract is deterministic and auditable. Any future PM
audit must check these exact strings; do not rely on close-enough wording.

The required identity / positioning strings are:

- PS-037a
- Multimodal Proof Layer

The required multimodal proof-concept strings are:

- artifact evidence
- modality
- media kind
- artifact reference
- artifact digest
- manifest reference
- manifest hash
- B2 evidence status
- rehydrate evidence status
- provider activity status
- local verification
- live verification status
- disclosure boundary
- not claimed
- unknown
- deferred to later slice

The required deferred later-slice state strings are:

- transcript evidence not available
- timestamp evidence not available
- voice evidence not available
- emotion evidence not available
- campaign intelligence not available

The required de-escalation-pair strings are:

- proof does not equal truth
- artifact reference does not equal legal authenticity
- media hash does not equal semantic truth
- manifest hash does not equal human authorship
- local artifact evidence does not equal live B2 availability
- demo/golden artifact does not equal production security

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
- not identity verification
- not biometric identification
- not deepfake detection
- not content moderation
- not OCR correctness
- not transcript correctness
- not timestamp correctness
- not voice authenticity
- not emotion truth
- not model output truth

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
- `slice_id: ps037a`
- `multimodal_proof_component_present`
- `multimodal_proof_data_module_present`
- `multimodal_proof_layer_present`
- `required_surfaces_have_multimodal_proof`
- `artifact_evidence_present`
- `modality_present`
- `media_kind_present`
- `artifact_reference_present`
- `artifact_digest_present`
- `manifest_reference_present`
- `manifest_hash_present_or_honestly_unavailable`
- `b2_evidence_status_present`
- `rehydrate_evidence_status_present`
- `provider_activity_status_present`
- `local_verification_status_present`
- `live_verification_status_present`
- `disclosure_boundary_present`
- `not_claimed_status_present`
- `unknown_status_present`
- `later_slice_deferred_status_present`
- `transcript_evidence_not_available_present`
- `timestamp_evidence_not_available_present`
- `voice_evidence_not_available_present`
- `emotion_evidence_not_available_present`
- `campaign_intelligence_not_available_present`
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
- `no_identity_verification_claim`
- `no_biometric_identification_claim`
- `no_deepfake_detection_claim`
- `no_content_moderation_claim`
- `no_ocr_correctness_claim`
- `no_transcript_correctness_claim`
- `no_timestamp_correctness_claim`
- `no_voice_authenticity_claim`
- `no_emotion_truth_claim`
- `no_model_output_truth_claim`
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

- `python scripts/proofstudio_regression_gate.py --current ps037a --frontend --report-out /tmp/proofstudio-release-report.json`
- `python scripts/proofstudio_regression_gate.py --current ps037a --no-frontend --report-out /tmp/proofstudio-ps037a-regression-report.json`
- `scripts/ps037a_multimodal_proof_layer_smoke.py`
- `docs/evidence/ps-037a/multimodal-proof-layer-report.json`
- `docs/ps-037a-multimodal-proof-layer-proof.md`
