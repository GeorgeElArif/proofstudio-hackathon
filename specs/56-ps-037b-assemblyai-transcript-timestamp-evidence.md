# PS-037b — AssemblyAI Transcript/Timestamp Evidence

## 1. Status

PS-037b — AssemblyAI Transcript/Timestamp Evidence is currently:

- Spec only.
- Implementation pending. No product code, frontend code, backend code,
  scripts, evidence, AGENTS.md, `.env*`, `render.yaml`, or requirements files
  are changed during this phase.

PS-037b must not be implemented, and no implementation files may be changed,
until this spec is accepted by the PM. The authoritative accepted base is the
dynamic Git ref `origin/accepted/proofstudio`, never a hardcoded commit hash.
At the time of this spec the ref resolves to commit
`ef5bae08f042875db0c11b6eef4da105a7eefb1e` (the post-PS-037a accepted state).
The ref is the authority; the commit hash is recorded for traceability only
and must not be treated as a hardcoded base.

This spec-only commit touches only this file:
`specs/56-ps-037b-assemblyai-transcript-timestamp-evidence.md`.

PS-037b must not call AssemblyAI, must not call any live provider, must not
read or write live B2, must not perform broad B2 scans, must not mutate any
evidence, must not run the frontend, must not run the backend, must not stage,
commit, or push, and must not print secrets during this phase. PS-037b obeys
the root `AGENTS.md` operating law and the validation policy in
`docs/validation/proofstudio-smoke-harness-v1.md`.

## 2. Purpose

PS-037b defines a reusable AssemblyAI Transcript/Timestamp Evidence layer that
makes ProofStudio's transcript-related evidence inspectable, honest, and
judge-safe. PS-037a (Multimodal Proof Layer) already reserves honest
"transcript evidence not available" and "timestamp evidence not available"
deferred states pointing at PS-037b, but does not own transcript or timestamp
evidence itself. PS-037b fills that reservation with a real, inspectable
transcript/timestamp evidence layer that answers, in one consistent place, the
basic transcript questions a reviewer or judge asks:

- whether transcript evidence exists
- whether timestamp evidence exists
- what media/artifact the transcript evidence relates to
- what provider is named for transcript/timestamp evidence
- whether the evidence is local/demo/golden fixture evidence or live provider
  evidence
- where the transcript artifact reference is recorded
- where the transcript artifact digest is recorded
- where timestamp segments / utterance windows / word timing evidence is
  recorded, if available
- what transcript fields are unavailable
- whether provider activity happened
- whether B2 archive evidence exists for the transcript artifact
- whether rehydrate evidence exists for the transcript artifact
- whether transcript/timestamp evidence was verified locally, unavailable, or
  not claimed
- what ProofStudio proves and does not prove for transcript/timestamp evidence

The layer is a transcript/timestamp evidence-inspection layer over
already-recorded or honestly-unavailable data, not a new proof surface, not a
new route, not a new backend endpoint, and not a live provider integration. It
makes the existing transcript/timestamp framing consistent and judge-safe, and
it states honestly what ProofStudio proves and what ProofStudio does not prove
for transcript/timestamp evidence.

PS-037b proves what the pipeline recorded. The layer does not prove transcript
correctness, timestamp correctness, speaker identity correctness, semantic
truth, legal authenticity, C2PA authenticity, human authorship, Object Lock /
tamper-proof storage, browser-side B2 byte verification, live B2 availability,
live AssemblyAI availability, production security, production compliance, legal
review, or chain-of-custody guarantees beyond recorded pipeline evidence.

## 3. Root Cause / Product Gap

PS-037a consolidated artifact evidence across modalities and explicitly
reserved honest "transcript evidence not available" / "timestamp evidence not
available" states, pointing the deferred ownership at PS-037b. That reservation
is honest, but it is only a placeholder. No slice yet makes transcript /
timestamp evidence inspectable: there is no single place where a reviewer can
read whether a transcript artifact exists, what media it relates to, what
provider is named for it, where its reference and digest are recorded, whether
timestamp segments / utterance windows / word timing evidence exists, what
fields are unavailable, whether provider activity happened, and whether B2 /
rehydrate evidence exists for the transcript artifact.

The gap this creates is judge-safety at the transcript boundary. Today:

- `apps/web/src/multimodalProof.ts` (PS-037a) reserves honest
  "transcript evidence not available" and "timestamp evidence not available"
  states, but PS-037a owns no transcript artifact, no transcript reference,
  no transcript digest, no timestamp segments, no word timing evidence, and no
  utterance timing evidence. It cannot answer "what transcript evidence
  exists"; it can only say "none yet."
- no accepted slice records a transcript artifact reference, a transcript
  artifact digest, a transcript provider, timestamp segments, word timing
  evidence, or utterance timing evidence in a single inspectable place.
- a judge reading a proof surface today cannot tell whether transcript /
  timestamp evidence is genuinely absent, deferred, locally recorded, or simply
  not surfaced. An absent transcript that is silently omitted looks like a
  hidden transcript; a transcript that appears without a clear disclosure
  boundary looks like a correctness claim.

PS-037b closes that gap by adding one shared transcript/timestamp evidence
layer — a canonical data module plus a shared component — that the core proof
surfaces render additively. The layer reads only accepted local / golden / demo
evidence, or exposes explicit honest "not available" / "not claimed" / "unknown"
states. It does not invent a transcript, a timestamp, a speaker identity, a
word-timing array, or any provider output that is not in accepted data. It is
local / static by default: it adds no AssemblyAI API calls, no provider calls,
no live B2 reads, no B2 writes, no broad B2 scans, no new backend, no new env,
no new paid service dependency, and no deployment changes.

AssemblyAI is named as the transcript/timestamp provider for evidence labeling
only. The implementation must default to local/static behavior. No live
AssemblyAI API call may occur unless a later PM-approved slice explicitly
enables a live-provider path with cost controls, env gates, and evidence
boundaries.

## 4. User Story

As a reviewer (designer, marketer, reviewer, client, or judge), I want one
honest, consistent transcript/timestamp evidence view, so that on any core
proof surface I can immediately read: whether transcript evidence exists;
whether timestamp evidence exists; what media / artifact the transcript
evidence relates to; what provider is named for transcript / timestamp
evidence (AssemblyAI); whether the evidence is local / demo / golden fixture
evidence or live provider evidence; where the transcript artifact reference is
recorded; where the transcript artifact digest is recorded; where timestamp
segments / utterance windows / word timing evidence is recorded, if available;
what transcript fields are unavailable; whether provider activity happened;
whether B2 archive evidence exists for the transcript artifact; whether
rehydrate evidence exists for the transcript artifact; whether transcript /
timestamp evidence was verified locally, unavailable, or not claimed — and so I
never mistake a transcript artifact reference for legal authenticity,
transcript text for semantic truth, timestamp evidence for timestamp
correctness, a provider transcript for speaker identity, local transcript
evidence for live AssemblyAI availability, or demo/golden transcript evidence
for production security.

As a demo presenter, I want a reusable transcript/timestamp evidence layer
that is useful in a three-minute hackathon demo: a compact summary that lists
the recorded transcript/timestamp evidence and its honest "not available" /
"not claimed" / "unknown" states, plus an expanded panel that states,
verbatim, what transcript/timestamp evidence proves, what it does not prove,
what is unavailable, what is not claimed, and what the shared disclosure
boundary is — all working offline from accepted local / golden / demo fixtures,
with no AssemblyAI API calls, no provider calls, no live B2 reads, no B2
writes, and no broad B2 scans.

## 5. Current Accepted Base

The current accepted base for PS-037b is:

- branch: `accepted/proofstudio`
- ref: `origin/accepted/proofstudio` (the authoritative source of truth; the
  ref is the authority, not any hardcoded commit hash)
- commit the ref resolves to at the time of this spec:
  `ef5bae08f042875db0c11b6eef4da105a7eefb1e`
- this is the post-PS-037a accepted state: the Multimodal Proof Layer from
  PS-037a is in place (`apps/web/src/multimodalProof.ts` +
  `apps/web/src/MultimodalProofLayer.tsx`); the Disclosure + Trust Boundary
  Layer from PS-037 is in place (`apps/web/src/trustBoundary.ts` +
  `apps/web/src/TrustBoundaryLayer.tsx`); the Archive / Rehydrate / B2 Audit
  Vault is in place from PS-036; the Review + Approval Workspace is in place
  from PS-035; the root `AGENTS.md` operating law is in place (PS-035D); the
  accepted-base-pointer-drift guard is in place (PS-035E); the central
  regression gate is non-mutating by default from PS-035C; the golden-fixture
  digest freeze is in place from PS-035B; the golden-run manifest carries a
  real non-null `manifest_uri` and a real 64-hex `manifest_hash` from PS-035A.

PS-037b must start from `origin/accepted/proofstudio`, not from `main`.

Relevant accepted facts at this base that PS-037b builds on (PS-037b must not
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
  `archive_sha256`, `manifest_uri`, `manifest_hash`, `rehydrate_source`, and
  an honest `unavailable_fields` map for values that are not present
- the PS-037 Disclosure + Trust Boundary Layer exists and is rendered on the
  core proof surfaces; PS-037b integrates with it and does not weaken it
- the PS-037a Multimodal Proof Layer exists and is rendered on the core proof
  surfaces; PS-037a reserves honest "transcript evidence not available" and
  "timestamp evidence not available" deferred states pointing at PS-037b;
  PS-037b integrates with / cross-references PS-037a and does not weaken it
- the existing shared component classes (`.trust-boundary`,
  `.trust-boundary-layer*`, the multimodal proof layer classes, pills, cards,
  `JsonExpander`) already exist in `apps/web/src/styles.css`

## 6. Scope

PS-037b is a product slice. It adds a reusable AssemblyAI Transcript/Timestamp
Evidence layer (a shared data module plus a shared component) and renders it
additively on the core proof surfaces. It is local / static by default: it must
work without AssemblyAI API calls, without live provider calls, without live B2
reads, without B2 writes, and without broad B2 scans, by reading accepted
local / golden / demo fixtures and existing accepted data modules, or by
surfacing explicit honest "not available" / "not claimed" / "unknown" states.

PS-037b owns transcript/timestamp evidence only. It must:

1. Add a shared, canonical transcript/timestamp evidence data module
   (`apps/web/src/assemblyAITranscriptEvidence.ts`, or the project's accepted
   equivalent) that exposes one consistent set of transcript/timestamp evidence
   concepts, transcript artifact evidence, timestamp evidence, honest
   "not available" / "not claimed" / "unknown" states, and deferred
   later-slice states for every core proof surface.
2. Add a shared transcript/timestamp evidence component
   (`apps/web/src/TranscriptTimestampEvidenceLayer.tsx`, or the project's
   accepted equivalent) that renders the layer, including an optional compact
   transcript/timestamp summary and an expanded transcript/timestamp panel
   pattern, reading only from `apps/web/src/assemblyAITranscriptEvidence.ts`.
3. Render the transcript/timestamp evidence layer additively on the required
   core proof surfaces (section 10.3) that are present in this repo so the
   transcript/timestamp framing is consistent everywhere transcript evidence is
   shown.
4. State, for transcript/timestamp evidence, "what ProofStudio proves" and
   "what ProofStudio does not prove."
5. Surface the canonical transcript/timestamp evidence concepts (section 10.2):
   transcript evidence, timestamp evidence, transcript artifact, transcript
   artifact reference, transcript artifact digest, transcript provider,
   AssemblyAI, media artifact reference, media artifact digest, timestamp
   segments, word timing evidence, utterance timing evidence, transcript
   status, timestamp status, transcript verification status, timestamp
   verification status, B2 evidence status, rehydrate evidence status,
   provider activity status, local verification, live verification status,
   disclosure boundary, not claimed, unknown, local/demo evidence, and live
   provider evidence not available.
6. Surface the honest unavailable / not-claimed states (section 10.6) verbatim
   so no reviewer mistakes an absent transcript / timestamp proof for a hidden
   proof, and no reviewer mistakes a recorded transcript for a correctness
   claim.
7. Surface the canonical transcript/timestamp de-escalation pairs (section
   10.7) verbatim so no judge mistakes a strong-sounding transcript artifact
   for a stronger guarantee.
8. Surface the canonical transcript/timestamp negative boundary strings
   (section 10.8) verbatim.
9. Integrate with the PS-037 TrustBoundaryLayer (render alongside it; reuse the
   shared disclosure concepts; do not duplicate or weaken the PS-037 boundary).
10. Integrate / cross-reference with the PS-037a MultimodalProofLayer (render
    alongside it; supply the concrete transcript/timestamp evidence that
    PS-037a only reserved as deferred; do not duplicate or weaken the PS-037a
    layer or its deferred states).
11. Preserve the existing per-surface artifact / boundary panels; the shared
    transcript/timestamp layer complements them. PS-037b must not delete or
    weaken any existing per-surface non-claim, per-surface artifact record, the
    PS-037 disclosure contract, or the PS-037a deferred transcript/timestamp
    states.
12. Be demo-friendly and judge-friendly: useful in a three-minute demo, no
    generic AI hype copy, no unsupported claims, no faked transcripts, no faked
    timestamps, no faked word timing.
13. Work without AssemblyAI API calls, without provider calls, without live B2
    reads, without B2 writes, and without broad B2 scans, by using accepted
    local / golden / demo data or existing accepted data paths.
14. Not mutate any prior evidence. Any PS-037b-owned evidence lives only under
    `docs/evidence/ps-037b/`.
15. Not change the golden run canonical constants, the historical contracts the
    regression gate verifies, any provider / B2 behavior, the PS-037 disclosure
    contract, or the PS-037a multimodal proof contract.

## 7. Non-goals

PS-037b must not:

- do not implement product code during the spec-only phase
- do not make any AssemblyAI API call
- do not make any live provider call
- do not implement the later provider-specific slices:
  - PS-037c Hume or ElevenLabs voiceover artifact, voice evidence, or emotion
    evidence (PS-037b must not fake voice analysis, emotion analysis, or a
    voiceover artifact; it may only reserve honest "emotion evidence deferred
    to PS-037c" states)
  - PS-037d Gemini Campaign Intelligence / Judge Narrative (PS-037b must not
    fake campaign intelligence; it may only reserve honest "campaign
    intelligence deferred to PS-037d" states)
- do not implement identity verification, biometric identification, speaker
  identity proof, voice authenticity proof, emotion truth, content moderation,
  deepfake detection, legal review, or semantic truth verification
- do not fake transcripts, timestamps, speaker labels, word timing, utterance
  timing, or any provider output that is not in accepted data
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
- do not claim transcript correctness
- do not claim timestamp correctness
- do not claim speaker identity correctness
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
- do not claim live AssemblyAI availability unless a live AssemblyAI check is
  explicitly implemented and approved with cost controls, env gates, and
  evidence boundaries
- do not claim production security
- do not claim production compliance
- do not claim legal review
- do not claim chain-of-custody guarantees beyond recorded pipeline evidence
- do not claim identity verification
- do not claim biometric identification
- do not claim deepfake detection
- do not claim content moderation
- do not claim OCR correctness
- do not claim voice authenticity
- do not claim emotion truth
- do not claim model output truth
- do not delete or weaken any existing per-surface truth-boundary panel,
  non-claim, artifact record, the PS-037 disclosure contract, or the PS-037a
  multimodal proof contract
- do not add a new backend, a new AssemblyAI client, a new provider wrapper, a
  new B2 client, a new env variable, a new paid service dependency, or any
  deployment change
- do not build CI, billing, deployment, auth, teams, permissions, or a full
  enterprise DAM
- do not change the golden run canonical constants
- do not change the historical contracts the regression gate verifies
- do not change the PS-037 disclosure contract
- do not change the PS-037a multimodal proof contract
- do not introduce a control name containing `KEY`, `TOKEN`, or `SECRET`
- do not use hidden Git flags (`assume-unchanged`, `skip-worktree`,
  `git update-index`, `update-index`)
- do not run recursive smokes
- do not use generic AI hype copy or unsupported claims
- do not create duplicate context-blind overclaim scanners in chat/spec
  guidance; the PS-037b smoke and its evidence report are the source of truth
  for slice overclaim validation; do not scan smoke guard fixtures as product
  claims

PS-037b only edits this spec file in the spec-only phase.
Implementation-phase candidate files are listed in section 8.

## 8. Implementation Candidate Files

The following are implementation-phase candidates only, clearly marked as
implementation-phase only. They are **not** for this spec-only commit. They are
listed so the implementation phase has a grounded file plan that follows
existing app conventions (each surface has a PascalCase `.tsx` component, a
camelCase `.ts` data module, a smoke script, and an evidence directory).

Shared layer (new files):
- `apps/web/src/assemblyAITranscriptEvidence.ts` (new) — the canonical
  camelCase transcript/timestamp evidence data module. Exposes the single
  shared set of transcript/timestamp evidence concepts, transcript artifact
  evidence, timestamp evidence, honest "not available" / "not claimed" /
  "unknown" states, deferred later-slice states, de-escalation pairs, negative
  boundary strings, and not-claimed / unknown status used by every core proof
  surface. Same convention as `multimodalProof.ts`, `trustBoundary.ts`,
  `b2Evidence.ts`, `b2RehydrateComparison.ts`, `judgeEvidencePack.ts`, etc.
  AssemblyAI is named as the transcript provider for evidence labeling only;
  the module must not contain a live AssemblyAI API call.
- `apps/web/src/TranscriptTimestampEvidenceLayer.tsx` (new) — the shared
  transcript/timestamp evidence component. Accepts the existing `variant`
  convention (for example `variant="panel"` for an expanded
  transcript/timestamp panel and `variant="summary"` / `variant="badge"` for a
  compact transcript/timestamp summary), reads only from
  `apps/web/src/assemblyAITranscriptEvidence.ts`, and renders the
  transcript/timestamp evidence layer with no AssemblyAI API calls, no provider
  calls, and no live B2 reads. Rendered alongside the existing
  `TrustBoundaryLayer` (PS-037) and `MultimodalProofLayer` (PS-037a).

Additive use on core proof surfaces (existing files, edited additively only):
- `apps/web/src/JudgeCockpitHome.tsx` (PS-023) — render the transcript/timestamp
  evidence layer on the home surface.
- `apps/web/src/B2EvidenceExplorer.tsx` (PS-026) — render the transcript/
  timestamp evidence layer (B2 evidence status for the transcript artifact).
- `apps/web/src/B2RehydrateComparison.tsx` (PS-029) — render the transcript/
  timestamp evidence layer (rehydrate evidence status for the transcript
  artifact).
- `apps/web/src/ManifestVerificationPanel.tsx` (PS-028) — render the
  transcript/timestamp evidence layer (media artifact reference + media
  artifact digest modalities).
- `apps/web/src/B2AuditVault.tsx` (PS-036) — render the transcript/timestamp
  evidence layer (B2 evidence status / rehydrate evidence status audit for the
  transcript artifact).
- `apps/web/src/ReviewApprovalWorkspace.tsx` (PS-035) — render the
  transcript/timestamp evidence layer (the reviewable artifact's transcript /
  timestamp evidence).
- `apps/web/src/JudgeEvidencePack.tsx` (PS-031) — render the transcript/
  timestamp evidence layer (export-pack transcript artifact summary).
- `apps/web/src/PublicPassportPage.tsx` (PS-019) — render the transcript/
  timestamp evidence layer (provenance passport transcript evidence).
- `apps/web/src/App.tsx` (PS-013 / PS-014) — render the transcript/timestamp
  evidence layer on the Review Room, complementing the existing asset /
  manifest / evidence panels, the PS-037 disclosure layer, and the PS-037a
  multimodal proof layer.

Additive styles (existing file, additive classes only):
- `apps/web/src/styles.css` — add only the classes needed for the
  transcript/timestamp evidence layer (transcript-status pills,
  timestamp-status pills, transcript-artifact-reference rows,
  transcript-artifact-digest rows, timestamp-segment rows, word-timing rows,
  utterance-timing rows, unavailable / not-claimed / unknown pills). No global
  style rewrite. PS-037b must not remove or weaken the existing
  `.trust-boundary-layer*` classes from PS-037 or the multimodal proof layer
  classes from PS-037a.

Backend (`src/proofstudio`) — none:
- PS-037b is a frontend-only transcript/timestamp evidence layer over existing
  accepted data. No backend change is expected. If any read-only reuse of an
  accepted data path is needed, it must reuse the existing accepted data paths
  under `src/proofstudio/api/` and `src/proofstudio/provenance/` without
  calling AssemblyAI, without calling any provider, and without reading live
  B2. No new provider wiring, no AssemblyAI client, no new B2 client, no new B2
  write path, no new broad B2 scan path. If no backend change is needed, none
  is made.

Smoke (scripts):
- `scripts/ps037b_assemblyai_transcript_timestamp_evidence_smoke.py` (new) —
  the PS-037b feature smoke. Must reuse `scripts/smoke_lib.py` for shared
  validation logic and must implement its own explicit `h` / `S`
  hidden-Git-flags checker (see section 14). Local / static only.

Spec / docs:
- `specs/07-master-spec-plan.md` — implementation-phase cross-reference only
  (register PS-037b acceptance). Must not change any historical item or golden
  constant.
- `specs/08-roadmap-slices.md` — implementation-phase status update only.
- `docs/validation/proofstudio-smoke-harness-v1.md` — implementation-phase
  PS-037b note only, additive, must not weaken any existing PS-034A / PS-035C
  contract.
- `docs/ps-037b-assemblyai-transcript-timestamp-evidence-proof.md` (new) — the
  PS-037b proof doc.

Evidence:
- `docs/evidence/ps-037b/assemblyai-transcript-timestamp-evidence-report.json`
  (new) — the only evidence PS-037b may write, and only when `--write-evidence`
  is explicit.

Any edit to `src/proofstudio/**` during implementation requires the backend
change to remain read-only over accepted data and to make no AssemblyAI API
call, no provider call, and no live B2 read.

## 9. Forbidden files Unless PM-approved Later

PS-037b implementation must not touch without explicit PM approval:

- `AGENTS.md`
- `.env*`
- `render.yaml`
- requirements files
- `docs/evidence/**` paths other than `docs/evidence/ps-037b/**`
- any prior-slice evidence prefix (for example `docs/evidence/ps-037a/**`,
  `docs/evidence/ps-037/**`, `docs/evidence/ps-036/**`,
  `docs/evidence/ps-035/**`, `docs/evidence/ps-031/**`,
  `docs/evidence/ps-029/**`, `docs/evidence/ps-026/**`,
  `docs/evidence/ps-021/**`, `docs/evidence/demo/golden-demo-run.json`,
  `docs/evidence/golden-fixture-digests.json`)
- `scripts/proofstudio_regression_gate.py` (the central gate is not owned by
  PS-037b)
- `scripts/smoke_lib.py` (shared library; PS-037b must not mutate shared
  validation behavior)
- any provider wrapper under `src/proofstudio/providers/**` (PS-037b owns no
  provider behavior; PS-037c / PS-037d own the other provider-specific later
  slices)
- any B2 client / storage write path (PS-037b performs no live B2 read, no B2
  write, and no broad B2 scan)
- any AssemblyAI client / live AssemblyAI integration path (PS-037b names
  AssemblyAI for evidence labeling only; no live AssemblyAI API call is allowed
  unless a later PM-approved slice explicitly enables a live-provider path with
  cost controls, env gates, and evidence boundaries)
- the PS-037 disclosure contract files (`apps/web/src/trustBoundary.ts`,
  `apps/web/src/TrustBoundaryLayer.tsx`) except for additive integration; any
  change that weakens or duplicates the PS-037 boundary is forbidden
- the PS-037a multimodal proof contract files
  (`apps/web/src/multimodalProof.ts`,
  `apps/web/src/MultimodalProofLayer.tsx`) except for additive cross-reference;
  any change that weakens, duplicates, or removes the PS-037a deferred
  transcript/timestamp states is forbidden

The only implementation-phase files allowed without PM approval are those in
section 8. Any other path requires explicit PM approval.

## 10. AssemblyAI Transcript/Timestamp Evidence Product Contract

PS-037b defines the following contract for the AssemblyAI Transcript/Timestamp
Evidence layer.

### 10.1 Layer identity

- It is a reusable transcript/timestamp evidence-inspection layer, not a new
  proof surface, not a new route, and not a new backend endpoint.
- It is purely client-side by default: it makes no AssemblyAI API call, calls
  no provider, reads no B2 object, exposes no arbitrary `run_id` input,
  performs no browser-side B2 byte verification, performs no broad B2 scan, and
  writes no B2 object.
- It is sourced from accepted local / golden / demo data and existing accepted
  data modules only, or from explicit honest "not available" / "not claimed" /
  "unknown" states.
- It makes the transcript/timestamp framing consistent on every core proof
  surface. It does not invent new transcripts, new timestamps, new speaker
  labels, new word timing, or new provider outputs; it states the existing
  recorded transcript/timestamp evidence consistently and honestly, and it
  states honest "not available" / "not claimed" / "unknown" states where no
  evidence exists.
- AssemblyAI is named as the transcript provider for evidence labeling only.
  Naming AssemblyAI does not imply a live AssemblyAI API call, live AssemblyAI
  availability, or any correctness guarantee.
- It integrates with the PS-037 Disclosure + Trust Boundary Layer: it renders
  alongside `TrustBoundaryLayer` and reuses the shared disclosure concepts, and
  must not duplicate or weaken the PS-037 boundary.
- It integrates / cross-references the PS-037a Multimodal Proof Layer: it
  renders alongside `MultimodalProofLayer` and supplies the concrete
  transcript/timestamp evidence that PS-037a only reserved as deferred, and
  must not duplicate, weaken, or remove the PS-037a deferred
  transcript/timestamp states.

### 10.2 Required transcript/timestamp evidence concepts

The layer must surface these canonical transcript/timestamp evidence concepts,
each as a clearly labeled item:

- `transcript evidence` — whether transcript evidence exists.
- `timestamp evidence` — whether timestamp evidence exists.
- `transcript artifact` — the recorded transcript artifact, if any, that the
  pipeline produced or stored.
- `transcript artifact reference` — where the transcript artifact reference is
  recorded (for example a transcript artifact id, file reference, or
  transcript artifact URI), honestly surfaced or honestly unavailable.
- `transcript artifact digest` — the recorded hash / digest for the transcript
  artifact, honestly surfaced or honestly unavailable.
- `transcript provider` — the provider named for transcript/timestamp evidence
  labeling (AssemblyAI by convention). Naming a provider does not imply a live
  provider call or live provider availability.
- `AssemblyAI` — the named transcript/timestamp provider.
- `media artifact reference` — what media / artifact the transcript evidence
  relates to (for example `archive_uri`, `manifest_uri`, asset id), honestly
  surfaced or honestly unavailable.
- `media artifact digest` — the recorded hash / digest for the media artifact
  the transcript evidence relates to (for example `archive_sha256`), honestly
  surfaced or honestly unavailable.
- `timestamp segments` — whether timestamp segment evidence is recorded, and if
  so where; honestly "not available" otherwise.
- `word timing evidence` — whether word-level timing evidence is recorded, and
  if so where; honestly "not available" otherwise.
- `utterance timing evidence` — whether utterance-level timing evidence is
  recorded, and if so where; honestly "not available" otherwise.
- `transcript status` — the honest status of the transcript evidence (present /
  not available / not claimed / unknown).
- `timestamp status` — the honest status of the timestamp evidence (present /
  not available / not claimed / unknown).
- `transcript verification status` — whether transcript evidence was verified
  locally, unavailable, or not claimed.
- `timestamp verification status` — whether timestamp evidence was verified
  locally, unavailable, or not claimed.
- `B2 evidence status` — whether B2 archive evidence is recorded for the
  transcript artifact, and whether it is recorded-only or live-verified
  (recorded-only by default).
- `rehydrate evidence status` — whether rehydrate evidence is recorded for the
  transcript artifact.
- `provider activity status` — whether provider activity happened for the
  transcript/timestamp evidence (no provider calls by default; local/demo
  evidence by default).
- `local verification` — whether evidence is locally verified against
  checked-in / accepted data.
- `live verification status` — whether a live check is in scope (local /
  check-only by default; live provider evidence not available by default).
- `disclosure boundary` — the transcript/timestamp disclosure boundary, sourced
  from / consistent with PS-037.
- `not claimed` — the honest set of things ProofStudio does not claim for
  transcript/timestamp evidence.
- `unknown` — what remains unknown or not surfaced for transcript/timestamp
  evidence.
- `local/demo evidence` — whether the transcript/timestamp evidence is local /
  demo / golden fixture evidence (the default posture).
- `live provider evidence not available` — the honest default state that no
  live provider transcript/timestamp evidence is available.

If a concept does not apply, the layer must show an honest "not available" /
"not claimed" / "unknown" state and must not fabricate a value.

### 10.3 Required surfaces

The transcript/timestamp evidence layer must be rendered (additively) on at
least these required core proof surfaces, so
`required_surfaces_have_transcript_timestamp_evidence` is truthful:

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

### 10.4 Local / live evidence honesty

The layer must distinguish clearly between:

- local transcript/timestamp evidence (transcript artifact references,
  transcript artifact digests, timestamp segments, word timing, utterance
  timing recorded in accepted checked-in data)
- live evidence (none, by default — PS-037b performs no live B2 read, no
  AssemblyAI API call, and no provider call)
- demo / golden evidence (the golden demo run, which is local / golden, not
  production)

A reviewer reading the layer must never mistake local transcript evidence for
live AssemblyAI availability, a demo/golden transcript for production security,
or a recorded transcript artifact reference for legal authenticity.

### 10.5 AssemblyAI provider-labeling honesty

AssemblyAI is named as the transcript/timestamp provider for evidence labeling.
This naming must not imply any of the following:

- a live AssemblyAI API call (none by default)
- live AssemblyAI availability
- transcript correctness
- timestamp correctness
- speaker identity correctness
- any correctness guarantee over what the pipeline recorded

The default posture is local/demo evidence with `live provider evidence not
available`. A live AssemblyAI path is out of scope for PS-037b and may only be
enabled by a later PM-approved slice with cost controls, env gates, and
evidence boundaries.

### 10.6 Required unavailable / not-claimed states (verbatim)

The layer must surface, honestly, these unavailable / not-claimed states
verbatim. These are non-claim states: they state what is not available, not
claimed, or unknown, and must never be read as a hidden proof:

- local/demo evidence
- live provider evidence not available
- transcript evidence not available
- timestamp evidence not available
- speaker identity not claimed
- voice authenticity not claimed
- emotion evidence deferred to PS-037c
- campaign intelligence deferred to PS-037d
- not claimed
- unknown

PS-037b must not fake a transcript, a timestamp, a speaker label, word timing,
utterance timing, a voice analysis, an emotion analysis, a campaign
intelligence output, or any provider output. The honest unavailable /
not-claimed / unknown states are the only acceptable representation of those
concepts when no accepted evidence exists.

### 10.7 Required de-escalation pairs (verbatim)

The layer must surface these transcript/timestamp de-escalation pairs verbatim
so a judge never mistakes a strong-sounding transcript artifact for a stronger
guarantee:

- proof does not equal truth
- transcript artifact reference does not equal legal authenticity
- transcript text does not equal semantic truth
- timestamp evidence does not equal timestamp correctness
- provider transcript does not equal speaker identity
- local transcript evidence does not equal live AssemblyAI availability
- demo/golden transcript evidence does not equal production security

### 10.8 Required negative boundary strings (verbatim)

The layer must surface these negative boundary strings verbatim:

- not transcript correctness
- not timestamp correctness
- not speaker identity
- not voice authenticity
- not semantic truth
- not legal authenticity
- not human authorship
- not C2PA authenticity
- not Object Lock
- not tamper-proof
- not browser-side B2 byte verification
- not live B2 availability
- not live AssemblyAI availability
- not production security
- not identity verification
- not biometric identification
- not deepfake detection
- not content moderation
- not OCR correctness
- not emotion truth
- not model output truth

### 10.9 Boundary honesty

The layer must not imply that any ProofStudio transcript/timestamp artifact
proves anything beyond what the pipeline recorded. In particular it must not
imply that a transcript artifact reference, a transcript artifact digest, a
transcript text, a timestamp segment, word timing, or utterance timing proves
transcript correctness, timestamp correctness, speaker identity, semantic
truth, legal authenticity, human authorship, C2PA authenticity, identity,
biometric identity, deepfake absence, content-policy compliance, OCR
correctness, voice authenticity, emotion truth, live AssemblyAI availability,
or model output truth.

## 11. UI/UX Contract

The AssemblyAI Transcript/Timestamp Evidence layer UI must include:

- A clear title: "AssemblyAI Transcript/Timestamp Evidence" (or an equivalent
  clear title), with a positioning line that ProofStudio proves what the
  pipeline recorded for transcript/timestamp evidence, and that AssemblyAI is
  named as the transcript provider for evidence labeling only.
- A compact transcript/timestamp summary variant (for example
  `variant="summary"` or `variant="badge"`) that lists, in one compact block,
  the recorded transcript/timestamp evidence and its honest "not available" /
  "not claimed" / "unknown" states, suitable for surfaces where space is
  constrained.
- An expanded transcript/timestamp panel variant (for example
  `variant="panel"`) that states, in full, the transcript/timestamp evidence
  contract.
- A transcript-evidence block that shows: transcript status, transcript
  artifact, transcript artifact reference, transcript artifact digest,
  transcript provider (AssemblyAI), media artifact reference, media artifact
  digest, transcript verification status, and an honest unavailable / not
  claimed / unknown state where no value exists.
- A timestamp-evidence block that shows: timestamp status, timestamp segments,
  word timing evidence, utterance timing evidence, timestamp verification
  status, and honest unavailable / not claimed / unknown states where no value
  exists.
- A provider-activity / B2 / rehydrate block that shows: provider activity
  status, B2 evidence status, rehydrate evidence status, local verification,
  and live verification status.
- A "not claimed" section listing, verbatim, what transcript/timestamp evidence
  does not prove (section 10.8), the honest unavailable / not-claimed states
  (section 10.6), and the deferred later-slice states (section 10.6).
- The de-escalation pairs (section 10.7), surfaced verbatim.
- The negative boundary strings (section 10.8), surfaced verbatim.
- A persistent transcript/timestamp boundary statement that states verbatim
  (or equivalent):

  > ProofStudio proves what the pipeline recorded for transcript/timestamp
  > evidence. Proof does not equal truth. A transcript artifact reference does
  > not equal legal authenticity. Transcript text does not equal semantic truth.
  > Timestamp evidence does not equal timestamp correctness. A provider
  > transcript does not equal speaker identity. Local transcript evidence does
  > not equal live AssemblyAI availability. Demo/golden transcript evidence
  > does not equal production security.

- Integration with the PS-037 Disclosure + Trust Boundary Layer: the
  transcript/timestamp evidence layer renders alongside `TrustBoundaryLayer`,
  reuses the shared disclosure concepts, and never contradicts the PS-037
  boundary.
- Integration / cross-reference with the PS-037a Multimodal Proof Layer: the
  transcript/timestamp evidence layer renders alongside `MultimodalProofLayer`
  and supplies the concrete transcript/timestamp evidence that PS-037a only
  reserved as deferred, and never contradicts or removes the PS-037a deferred
  transcript/timestamp states.

UI / UX constraints:

- Must be useful in a three-minute hackathon demo: open any core proof surface
  -> read the compact transcript/timestamp summary -> expand the
  transcript/timestamp panel -> read what transcript/timestamp evidence proves
  -> read what it does not prove -> read the unavailable / not-claimed states
  -> read the de-escalation pairs -> read the negative boundary strings.
- Must render the same transcript/timestamp framing on every required surface
  (section 10.3).
- Must not introduce generic AI hype copy.
- Must not add unsupported claims.
- Must not fabricate transcripts, timestamps, speaker labels, word timing,
  utterance timing, digests, or provider outputs that are not in accepted data.
- Must follow the existing component conventions (`variant`, pills, cards,
  `JsonExpander`, the `.trust-boundary`, `.trust-boundary-layer*`, and
  multimodal proof layer styles) used by the other surfaces.
- Must not delete or weaken any existing per-surface truth-boundary panel,
  per-surface artifact record, the PS-037 disclosure layer, or the PS-037a
  multimodal proof layer; the transcript/timestamp layer is additive.

## 12. Data Contract

### 12.1 Source data (read-only inputs)

PS-037b reads accepted local / golden / demo data and existing accepted data
modules as immutable inputs. It must not mutate these and must not change their
canonical values. Acceptable read-only sources:

- `apps/web/src/trustBoundary.ts` (PS-037) — reuse the shared disclosure
  concepts; do not duplicate or weaken them
- `apps/web/src/multimodalProof.ts` (PS-037a) — reuse / cross-reference the
  deferred transcript/timestamp reservation; do not duplicate, weaken, or
  remove it
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

Where no accepted transcript/timestamp evidence exists, PS-037b must surface
explicit honest "not available" / "not claimed" / "unknown" states and must not
fabricate values. PS-037b must not change the golden run canonical constants.
The canonical constants are owned by their respective accepted slices.

### 12.2 Transcript/timestamp evidence item shape

A transcript/timestamp evidence item is derived from accepted data and must
expose:

- `transcript_status` (one of `present`, `not_available`, `not_claimed`,
  `unknown`)
- `timestamp_status` (one of `present`, `not_available`, `not_claimed`,
  `unknown`)
- `transcript_artifact` (the recorded transcript artifact, or honestly
  unavailable)
- `transcript_artifact_reference` (where the reference is recorded, or honestly
  unavailable)
- `transcript_artifact_digest` (the recorded hash / digest, or honestly
  unavailable)
- `transcript_provider` (the named provider; AssemblyAI by convention)
- `media_artifact_reference` (the recorded media / artifact reference, or
  honestly unavailable)
- `media_artifact_digest` (the recorded media / artifact digest, or honestly
  unavailable)
- `timestamp_segments` (recorded timestamp segment evidence, or honestly
  unavailable)
- `word_timing_evidence` (recorded word-level timing, or honestly unavailable)
- `utterance_timing_evidence` (recorded utterance-level timing, or honestly
  unavailable)
- `transcript_verification_status` (one of `locally_verified`, `unavailable`,
  `not_claimed`, `unknown`)
- `timestamp_verification_status` (one of `locally_verified`, `unavailable`,
  `not_claimed`, `unknown`)
- `b2_evidence_status` (recorded-only by default)
- `rehydrate_evidence_status`
- `provider_activity_status` (no provider calls by default)
- `local_verification` (locally verified against accepted checked-in data)
- `live_verification_status` (local / check-only by default; live provider
  evidence not available by default)
- `disclosure_boundary` (sourced from / consistent with PS-037)
- `label` (the human-readable label, matching the verbatim strings in
  section 21)
- `value` (the evidence value, honest about local / recorded-only /
  unavailable / not claimed / unknown)
- `applicable` (boolean; false when the concept honestly does not apply)
- `state` (one of `recorded`, `locally_verified`, `recorded_only`,
  `not_verified`, `not_available`, `not_claimed`, `unknown`, `deferred_to_later_slice`)

### 12.3 Evidence report schema rule

The PS-037b evidence report must follow the harness schema rule: boolean
fields remain booleans and detail / list fields use explicit detail names. A
field whose name implies a boolean success flag must remain a boolean. List
fields must use explicit detail names such as `_ids`, `_details`, or
`_failures` (see section 13).

## 13. Evidence Contract

PS-037b owns exactly one evidence directory: `docs/evidence/ps-037b/`.

- A feature smoke may write only its own evidence, and only when
  `--write-evidence` is explicit. The default PS-037b smoke behavior is
  non-mutating local validation.
- PS-037b must not write any file outside `docs/evidence/ps-037b/`.
- PS-037b must not mutate any prior-slice evidence (every prior evidence prefix
  is guarded by `scripts/smoke_lib.py` and
  `scripts/proofstudio_regression_gate.py`), including the PS-037 evidence
  under `docs/evidence/ps-037/` and the PS-037a evidence under
  `docs/evidence/ps-037a/`.
- The PS-037b evidence file is
  `docs/evidence/ps-037b/assemblyai-transcript-timestamp-evidence-report.json`.

The PS-037b evidence report must carry these boolean fields (booleans as
booleans; `failures` as a list):

- `ok` (boolean; true only when every measured field is truthful and no
  forbidden overclaim or forbidden file change is present)
- `slice_id`: `ps037b`
- `transcript_timestamp_component_present` (boolean;
  `TranscriptTimestampEvidenceLayer` component exists)
- `transcript_timestamp_data_module_present` (boolean;
  `assemblyAITranscriptEvidence.ts` exists)
- `transcript_timestamp_layer_present` (boolean; the shared layer is wired in)
- `required_surfaces_have_transcript_timestamp_evidence` (boolean; the required
  surfaces in section 10.3 that are present in this repo render the layer)
- `multimodal_proof_cross_reference_present` (boolean; the layer integrates /
  cross-references the PS-037a Multimodal Proof Layer)
- `trust_boundary_preserved` (boolean; the PS-037 Disclosure + Trust Boundary
  Layer is preserved)
- `assemblyai_label_present` (boolean; AssemblyAI is named as the transcript
  provider for evidence labeling)
- `transcript_evidence_present` (boolean)
- `timestamp_evidence_present` (boolean)
- `transcript_artifact_present` (boolean)
- `transcript_artifact_reference_present` (boolean)
- `transcript_artifact_digest_present` (boolean)
- `transcript_provider_present` (boolean)
- `media_artifact_reference_present` (boolean)
- `media_artifact_digest_present` (boolean)
- `timestamp_segments_present_or_honestly_unavailable` (boolean)
- `word_timing_evidence_present_or_honestly_unavailable` (boolean)
- `utterance_timing_evidence_present_or_honestly_unavailable` (boolean)
- `transcript_status_present` (boolean)
- `timestamp_status_present` (boolean)
- `transcript_verification_status_present` (boolean)
- `timestamp_verification_status_present` (boolean)
- `b2_evidence_status_present` (boolean)
- `rehydrate_evidence_status_present` (boolean)
- `provider_activity_status_present` (boolean)
- `local_verification_status_present` (boolean)
- `live_verification_status_present` (boolean)
- `disclosure_boundary_present` (boolean)
- `not_claimed_status_present` (boolean)
- `unknown_status_present` (boolean)
- `local_demo_evidence_present` (boolean)
- `live_provider_evidence_not_available_present` (boolean)
- `transcript_evidence_not_available_present` (boolean)
- `timestamp_evidence_not_available_present` (boolean)
- `speaker_identity_not_claimed_present` (boolean)
- `voice_authenticity_not_claimed_present` (boolean)
- `emotion_evidence_deferred_to_ps037c_present` (boolean)
- `campaign_intelligence_deferred_to_ps037d_present` (boolean)
- `proof_does_not_equal_truth_present` (boolean)
- `no_transcript_correctness_claim` (boolean)
- `no_timestamp_correctness_claim` (boolean)
- `no_speaker_identity_claim` (boolean)
- `no_voice_authenticity_claim` (boolean)
- `no_semantic_truth_claim` (boolean)
- `no_legal_authenticity_claim` (boolean)
- `no_human_authorship_claim` (boolean)
- `no_c2pa_authenticity_claim` (boolean)
- `no_object_lock_claim` (boolean)
- `no_tamper_proof_claim` (boolean)
- `no_browser_side_b2_byte_verification_claim` (boolean)
- `no_live_b2_availability_claim` (boolean)
- `no_live_assemblyai_availability_claim` (boolean)
- `no_production_security_claim` (boolean)
- `no_identity_verification_claim` (boolean)
- `no_biometric_identification_claim` (boolean)
- `no_deepfake_detection_claim` (boolean)
- `no_content_moderation_claim` (boolean)
- `no_ocr_correctness_claim` (boolean)
- `no_emotion_truth_claim` (boolean)
- `no_model_output_truth_claim` (boolean)
- `no_assemblyai_api_calls` (boolean)
- `no_provider_calls` (boolean)
- `no_live_b2_reads` (boolean)
- `no_b2_writes` (boolean)
- `no_broad_b2_scans` (boolean)
- `no_recursive_smokes` (boolean)
- `no_hidden_git_flags_h` (boolean)
- `no_hidden_git_flags_S` (boolean)
- `no_forbidden_overclaims` (boolean)
- `prior_evidence_clean` (boolean)
- `failures` (list; empty on success)

`ok` must be `false` if `failures` is non-empty. Boolean fields must remain
booleans; list / detail fields must use explicit detail names. This evidence
file is created only in the implementation phase and only when
`--write-evidence` is explicit.

## 14. Smoke / Validation Contract

PS-037b ships one feature smoke:
`scripts/ps037b_assemblyai_transcript_timestamp_evidence_smoke.py`.

The PS-037b feature smoke must:

- validate only the PS-037b slice (no recursive smokes; must never launch
  another feature smoke as a subprocess; must never call the central regression
  gate)
- read checked-in prior evidence and accepted data modules as immutable inputs
- write only its own evidence file
  `docs/evidence/ps-037b/assemblyai-transcript-timestamp-evidence-report.json`,
  and only when `--write-evidence` is explicit
- never call AssemblyAI (no AssemblyAI API calls)
- never call any provider (no provider calls)
- never read arbitrary B2 objects (no live B2 reads)
- never write B2 (no B2 writes)
- never perform broad B2 scans
- never run the frontend typecheck / build (that belongs to the central gate)
- reuse `scripts/smoke_lib.py` for shared validation logic
- validate the shared `TranscriptTimestampEvidenceLayer` component is present
- validate the shared `assemblyAITranscriptEvidence.ts` data module is present
- validate the transcript/timestamp evidence layer is rendered on the required
  proof surfaces that are present in this repo (section 10.3)
- validate the layer integrates / cross-references the PS-037a Multimodal Proof
  Layer (`multimodal_proof_cross_reference_present`)
- validate the PS-037 TrustBoundaryLayer is preserved
  (`trust_boundary_preserved`)
- validate the required transcript/timestamp UI strings (section 21) are
  present
- validate the required negative boundary strings (section 21) are present
- validate the deferred later-slice states (section 10.6) are present and
  honest
- validate no AssemblyAI API calls are introduced
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
  the PS-037b changed files, without the smoke or this spec reproducing that
  literal
- validate prior evidence is unchanged
- validate `git diff --check` is clean
- do not scan smoke guard fixtures as product claims (the future PS-037b smoke
  and its evidence report are the source of truth for slice overclaim
  validation; smoke guard fixtures are not product claims)

The PS-037b feature smoke must support these standard flags:

- `--check-only` (default: non-mutating local validation; no evidence file is
  written)
- `--write-evidence` (write only `docs/evidence/ps-037b/` evidence)
- `--no-frontend`

Default PS-037b smoke behavior is non-mutating local validation
(`--check-only`).

The smoke must not contain the bad lowercase-only hidden-flag marker check and
must not rely on a lowercase-only marker check. The hidden-Git-flags check must
be the explicit `h` / `S` checker over `git ls-files -v`, and must record
`no_hidden_git_flags_h` and `no_hidden_git_flags_S` as separate booleans.

PS-037b smoke performs no AssemblyAI API calls, no provider calls, no live B2
reads, no B2 writes, and no broad B2 scans.

The PS-037b smoke must not create duplicate context-blind overclaim scanners.
The smoke and its evidence report are the source of truth for PS-037b overclaim
validation. The smoke must not scan smoke guard fixtures as product claims.

## 15. Regression Gate Contract

The central regression gate remains the single cross-slice release-readiness
gate and is non-mutating by default. PS-037b does not own or modify the central
gate.

Normal future PS-037b release validation command:

```
python scripts/proofstudio_regression_gate.py --current ps037b --frontend --report-out /tmp/proofstudio-release-report.json
```

Contract-only gate (no frontend):

```
python scripts/proofstudio_regression_gate.py --current ps037b --no-frontend --report-out /tmp/proofstudio-ps037b-regression-report.json
```

- The gate runs `npm run typecheck` and `npm run build` in `apps/web` exactly
  once per invocation, and only when `--frontend` is passed. PS-037b feature
  smoke must never trigger nested frontend builds.
- The gate must not write the canonical PS-034A report. `--write-report` is
  rejected for `--current ps037b` (PS-035C accepted behavior; only PS-034A may
  regenerate the canonical report).
- Running the gate for `ps037b` must leave all prior-slice evidence unchanged,
  including the PS-037 and PS-037a evidence.
- No recursive smokes: the gate never executes a feature smoke.

Canonical PS-034A regeneration (unchanged, owned by PS-034A only):

```
python scripts/proofstudio_regression_gate.py --current ps034a --write-report
```

## 16. Truth Boundary

ProofStudio proves what the pipeline recorded. The AssemblyAI Transcript/
Timestamp Evidence layer is a transcript/timestamp evidence-inspection surface
that makes the recorded transcript/timestamp evidence explicit and consistent
on every core proof surface. It is not a legal authenticity system, not a live
B2 verifier, not a truth system, not an identity system, not a biometric
system, not a speaker-identity system, not a deepfake detector, not a content
moderator, not an OCR verifier, not a transcript-correctness verifier, not a
timestamp-correctness verifier, not a voice verifier, not an emotion verifier,
and not a live AssemblyAI verifier.

The layer must preserve these truth-boundary red lines verbatim across the
spec, the UI, and any evidence report:

- do not claim transcript correctness
- do not claim timestamp correctness
- do not claim speaker identity correctness
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
- do not claim live AssemblyAI availability unless a live AssemblyAI check is
  explicitly implemented and approved with cost controls, env gates, and
  evidence boundaries
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
- do not claim voice authenticity
- do not claim emotion truth
- do not claim model output truth
- do not claim actual spend / latency / quota unless captured
- do not claim provider failures / reruns / variants unless evidenced

PS-037b does not prove transcript correctness, timestamp correctness, speaker
identity, product correctness, production security, production compliance, B2
immutability, Object Lock, tamper-proof storage, browser-side B2 byte
verification, live B2 availability, live AssemblyAI availability, real billing
API integration, billing behavior, CI enforcement, legal review, identity,
biometric identity, deepfake absence, content-policy compliance, OCR
correctness, voice authenticity, emotion truth, model output truth, or
deployment readiness. No PS-037b artifact may imply any of these. The
transcript/timestamp evidence layer states what the pipeline already recorded;
it does not re-fetch, re-hash, or re-verify live B2 bytes, it does not call
AssemblyAI, and it does not call any provider.

## 17. Later-slice Boundaries

PS-037b must not implement, fake, or claim the later provider-specific slices
or out-of-scope capabilities. The boundaries are:

- PS-037c Hume or ElevenLabs voiceover artifact — owns voice and emotion
  evidence and any voiceover artifact. PS-037b must only reserve honest
  "emotion evidence deferred to PS-037c" and "voice authenticity not claimed"
  states. PS-037b must not produce, store, or claim a voiceover, a voice
  analysis, or an emotion analysis.
- PS-037d Gemini Campaign Intelligence / Judge Narrative — owns campaign
  intelligence and the judge narrative. PS-037b must only reserve an honest
  "campaign intelligence deferred to PS-037d" state. PS-037b must not produce,
  store, or claim a campaign intelligence output or a judge narrative.
- identity verification — out of scope. PS-037b must only reserve an honest
  "speaker identity not claimed" state.
- biometric identification — out of scope. PS-037b must not claim it.
- speaker identity proof — out of scope. PS-037b must only reserve an honest
  "speaker identity not claimed" state.
- voice authenticity proof — out of scope. PS-037b must only reserve an honest
  "voice authenticity not claimed" state.
- emotion truth — out of scope. PS-037b must only reserve an honest "emotion
  evidence deferred to PS-037c" state.
- content moderation — out of scope. PS-037b must not claim it.
- deepfake detection — out of scope. PS-037b must not claim it.
- legal review — out of scope. PS-037b must not claim it.
- semantic truth verification — out of scope. PS-037b must not claim it.

PS-037b may reserve fields and honest "not available yet" / "not claimed" /
"unknown" states for those later-slice / out-of-scope areas, but must not fake
voice analysis, emotion analysis, campaign intelligence, speaker identity,
voice authenticity, or any provider output.

## 18. Risks

PS-037b must record the following risks with mitigations:

- overclaim risk
  - risk: a reviewer misreads the transcript/timestamp evidence layer or its
    copy as a forbidden overclaim — i.e. as claiming transcript correctness,
    timestamp correctness, speaker identity correctness, semantic truth, legal
    authenticity, human authorship, C2PA authenticity, Object Lock /
    tamper-proof storage, browser-side B2 byte verification, live B2
    availability, live AssemblyAI availability, production security, production
    compliance, legal review, chain-of-custody guarantees beyond recorded
    pipeline evidence, identity verification, biometric identification,
    deepfake detection, content moderation, OCR correctness, voice
    authenticity, emotion truth, or model output truth. ProofStudio does not
    claim any of these.
  - mitigation: the persistent transcript/timestamp boundary statement
    (section 11) is mandatory; the truth-boundary red lines (section 16) are
    preserved verbatim; the de-escalation pairs (section 10.7) and negative
    boundary strings (section 10.8) are surfaced verbatim; the evidence report
    carries `no_forbidden_overclaims` and `trust_boundary_preserved`.
- provider-overclaim risk
  - risk: naming AssemblyAI as the transcript provider is misread as a live
    AssemblyAI API call, live AssemblyAI availability, or a transcript /
    timestamp / speaker-identity correctness guarantee.
  - mitigation: the provider-labeling honesty (section 10.5) is mandatory; the
    default posture is local/demo evidence with `live provider evidence not
    available`; the evidence report carries `no_assemblyai_api_calls`,
    `no_provider_calls`, and `no_live_assemblyai_availability_claim`; no live
    AssemblyAI path exists in PS-037b.
- faking-transcript risk
  - risk: a transcript, timestamp, speaker label, word timing, or utterance
    timing is silently represented as present when it is not, or is silently
    omitted so it looks hidden.
  - mitigation: the unavailable / not-claimed states (section 10.6) are
    surfaced verbatim and honestly; the smoke validates their presence;
    PS-037b never produces those provider outputs unless they exist in accepted
    data.
- de-escalation-gap risk
  - risk: a judge mistakes a transcript artifact reference for legal
    authenticity, transcript text for semantic truth, timestamp evidence for
    timestamp correctness, a provider transcript for speaker identity, local
    transcript evidence for live AssemblyAI availability, or demo/golden
    transcript evidence for production security.
  - mitigation: the de-escalation pairs in section 10.7 are surfaced verbatim.
- PS-037 / PS-037a weakening risk
  - risk: the transcript/timestamp layer duplicates, contradicts, weakens, or
    removes the PS-037 Disclosure + Trust Boundary Layer or the PS-037a
    Multimodal Proof Layer (including its deferred transcript/timestamp
    states).
  - mitigation: the transcript/timestamp layer renders alongside
    `TrustBoundaryLayer` and `MultimodalProofLayer`, reuses the shared
    disclosure concepts, cross-references PS-037a, and never contradicts the
    PS-037 boundary or removes the PS-037a deferred states; PS-037b does not
    edit the PS-037 or PS-037a contract files except additively (section 9).
- live-B2-read risk
  - risk: the layer triggers a live B2 read or a broad B2 scan.
  - mitigation: the layer is purely client-side over accepted data; the smoke
    enforces `no_live_b2_reads`, `no_b2_writes`, `no_broad_b2_scans`.
- evidence-mutation risk
  - risk: the PS-037b smoke or the central gate run overwrites prior-slice
    evidence, including PS-037 and PS-037a evidence.
  - mitigation: PS-037b writes only `docs/evidence/ps-037b/`; the gate is
    non-mutating by default; prior evidence prefixes are guarded.
- hidden-Git-flags risk
  - risk: a session uses `assume-unchanged`, `skip-worktree`, or
    `git update-index` / `update-index` to mask a dirty tree, including the
    uppercase `S` skip-worktree flag that a lowercase-only marker check misses.
  - mitigation: the operating law forbids these verbatim; the smoke uses the
    explicit `h` / `S` checker over `git ls-files -v` and fails on `line[0]`
    being `h` or `S`, recording `no_hidden_git_flags_h` and
    `no_hidden_git_flags_S` as separate booleans.
- scope-creep risk
  - risk: PS-037b expands into PS-037c / PS-037d provider behavior, a live
    AssemblyAI integration, identity verification, speaker identity proof,
    biometric identification, content moderation, deepfake detection, CI,
    billing, deployment, auth, teams, permissions, a full enterprise DAM, a new
    backend, or a live B2 fetcher.
  - mitigation: section 7 lists these as non-goals; section 9 forbids the
    relevant paths; section 17 fixes the later-slice / out-of-scope boundaries.
- recursive-smoke risk
  - risk: the PS-037b smoke launches another feature smoke or calls the central
    gate.
  - mitigation: the smoke must never launch another feature smoke as a
    subprocess and must never call the central regression gate; the central
    gate is the only cross-slice validator.
- duplicate-scanner risk
  - risk: PS-037b adds duplicate context-blind overclaim scanners in
    chat/spec guidance that treat smoke guard fixtures as product claims.
  - mitigation: PS-037b does not create duplicate context-blind overclaim
    scanners; the PS-037b smoke and its evidence report are the source of truth
    for slice overclaim validation; smoke guard fixtures are not scanned as
    product claims.

## 19. Acceptance Criteria

PS-037b (spec-only phase) is accepted only when:

- this spec exists at
  `specs/56-ps-037b-assemblyai-transcript-timestamp-evidence.md`
- only this spec file is changed in the spec-only phase
- the branch `ps-037b/assemblyai-transcript-timestamp-evidence` starts from
  `origin/accepted/proofstudio` at commit
  `ef5bae08f042875db0c11b6eef4da105a7eefb1e` (the merge-base equals that
  commit)
- the product scope is clear and owns transcript/timestamp evidence only; it
  does not expand into CI, billing, deployment, AssemblyAI API calls, provider
  calls, live B2 reads, B2 writes, broad B2 scans, PS-037c, PS-037d, identity
  verification, biometric identification, speaker identity proof, voice
  authenticity proof, emotion truth, content moderation, deepfake detection,
  legal review, or semantic truth verification
- the required transcript/timestamp evidence concepts (section 10.2) and the
  required surfaces (section 10.3) are specified
- the unavailable / not-claimed states (section 10.6), the de-escalation pairs
  (section 10.7), and the negative boundary strings (section 10.8) are
  specified verbatim
- the UI / UX contract (section 11) and the persistent transcript/timestamp
  boundary statement are specified
- the data contract (section 12) reuses accepted checked-in evidence as
  read-only inputs and surfaces honest unavailable / not-claimed / unknown
  states where no evidence exists
- the truth boundary (section 16) is explicit and the boundary copy is
  specified
- the later-slice boundaries (section 17) are fixed
- the implementation candidate files (section 8) are listed, but no
  implementation is done in this phase
- the validation plan uses the PS-037b feature smoke plus the central
  regression gate (sections 14 and 15)
- no evidence mutation occurs in this phase
- no hidden Git flags `h` or `S` are present (verified by the explicit h/S
  checker over `git ls-files -v`)
- `git diff --check` is clean
- no staging, commit, or push occurs until PM approval
- `AGENTS.md`, `specs/07-master-spec-plan.md`, and
  `specs/08-roadmap-slices.md` are not changed in this phase

Implementation-phase acceptance (for reference, not this phase) additionally
requires: the shared `TranscriptTimestampEvidenceLayer` component +
`assemblyAITranscriptEvidence.ts` data module exist; the transcript/timestamp
evidence layer is rendered on the required surfaces present in this repo
(section 10.3); the layer integrates / cross-references the PS-037a Multimodal
Proof Layer and preserves the PS-037 TrustBoundaryLayer; the required
transcript/timestamp concepts, unavailable / not-claimed states, de-escalation
pairs, and negative boundary strings are present; the PS-037b smoke passes in
`--check-only` (default) and writes only `docs/evidence/ps-037b/**` under
`--write-evidence`; the central gate passes for `--current ps037b`; no
AssemblyAI API call, no provider call, no live B2 read, no B2 write, no broad
B2 scan occurs; prior evidence is unchanged, including PS-037 and PS-037a
evidence; no forbidden overclaim is introduced; the PS-037 disclosure boundary
and the PS-037a multimodal proof contract are not weakened.

## 20. Rollback

Rollback of the PS-037b spec-only phase is a single revert of this spec commit,
because only
`specs/56-ps-037b-assemblyai-transcript-timestamp-evidence.md` is changed in
this phase.

Future implementation rollback must restore the pre-PS-037b state of the edited
files in section 8. Specifically:

- remove `apps/web/src/assemblyAITranscriptEvidence.ts`
- remove `apps/web/src/TranscriptTimestampEvidenceLayer.tsx`
- revert the additive transcript/timestamp-evidence-layer renders in
  `apps/web/src/JudgeCockpitHome.tsx`,
  `apps/web/src/B2EvidenceExplorer.tsx`,
  `apps/web/src/B2RehydrateComparison.tsx`,
  `apps/web/src/ManifestVerificationPanel.tsx`,
  `apps/web/src/B2AuditVault.tsx`,
  `apps/web/src/ReviewApprovalWorkspace.tsx`,
  `apps/web/src/JudgeEvidencePack.tsx`,
  `apps/web/src/PublicPassportPage.tsx`, and
  `apps/web/src/App.tsx` to pre-PS-037b state
- revert the additive transcript/timestamp-evidence-layer classes in
  `apps/web/src/styles.css` to pre-PS-037b state
- remove `scripts/ps037b_assemblyai_transcript_timestamp_evidence_smoke.py`
- remove `docs/ps-037b-assemblyai-transcript-timestamp-evidence-proof.md`
- remove `docs/evidence/ps-037b/` if it was added
- revert the additive cross-references in `specs/07-master-spec-plan.md`,
  `specs/08-roadmap-slices.md`, and
  `docs/validation/proofstudio-smoke-harness-v1.md` to pre-PS-037b state

Rollback of PS-037b must not touch any evidence under `docs/evidence/**` other
than `docs/evidence/ps-037b/`, must not touch the central gate
(`scripts/proofstudio_regression_gate.py`), `scripts/smoke_lib.py`,
`AGENTS.md`, `.env*`, `render.yaml`, requirements files, any provider wrapper,
any AssemblyAI client, any B2 storage path, the PS-037 disclosure contract, or
the PS-037a multimodal proof contract. Rollback is isolated and reversible
because PS-037b is a self-contained transcript/timestamp evidence layer over
existing accepted data; it does not change provider behavior, AssemblyAI
behavior, B2 behavior, billing behavior, deployment topology, the PS-037
boundary, or the PS-037a contract.

## 21. Verbatim implementation/audit contract strings

The PS-037b implementation, the AssemblyAI Transcript/Timestamp Evidence UI,
the PS-037b smoke, and the PS-037b evidence report must preserve the following
exact strings so the transcript/timestamp evidence contract is deterministic
and auditable. Any future PM audit must check these exact strings; do not rely
on close-enough wording. No surprise audit checks: any exact string a future PM
audit should check is listed here.

The required identity / positioning strings are:

- PS-037b
- AssemblyAI Transcript/Timestamp Evidence
- AssemblyAI

The required transcript/timestamp evidence-concept strings are:

- transcript evidence
- timestamp evidence
- transcript artifact
- transcript artifact reference
- transcript artifact digest
- transcript provider
- media artifact reference
- media artifact digest
- timestamp segments
- word timing evidence
- utterance timing evidence
- transcript status
- timestamp status
- transcript verification status
- timestamp verification status
- B2 evidence status
- rehydrate evidence status
- provider activity status
- local verification
- live verification status
- disclosure boundary
- not claimed
- unknown
- local/demo evidence

The required honest unavailable / not-claimed state strings are:

- local/demo evidence
- live provider evidence not available
- transcript evidence not available
- timestamp evidence not available
- speaker identity not claimed
- voice authenticity not claimed
- emotion evidence deferred to PS-037c
- campaign intelligence deferred to PS-037d

The required de-escalation-pair strings are:

- proof does not equal truth
- transcript artifact reference does not equal legal authenticity
- transcript text does not equal semantic truth
- timestamp evidence does not equal timestamp correctness
- provider transcript does not equal speaker identity
- local transcript evidence does not equal live AssemblyAI availability
- demo/golden transcript evidence does not equal production security

The required negative-boundary strings are:

- not transcript correctness
- not timestamp correctness
- not speaker identity
- not voice authenticity
- not semantic truth
- not legal authenticity
- not human authorship
- not C2PA authenticity
- not Object Lock
- not tamper-proof
- not browser-side B2 byte verification
- not live B2 availability
- not live AssemblyAI availability
- not production security
- not identity verification
- not biometric identification
- not deepfake detection
- not content moderation
- not OCR correctness
- not emotion truth
- not model output truth

The required posture / boundary strings are:

- no AssemblyAI API calls
- no provider calls
- no live B2 reads
- no B2 writes
- no broad B2 scans
- no recursive smokes
- hidden Git flags h
- line[0]

The required evidence-report boolean keys are:

- `ok`
- `slice_id: ps037b`
- `transcript_timestamp_component_present`
- `transcript_timestamp_data_module_present`
- `transcript_timestamp_layer_present`
- `required_surfaces_have_transcript_timestamp_evidence`
- `multimodal_proof_cross_reference_present`
- `trust_boundary_preserved`
- `assemblyai_label_present`
- `transcript_evidence_present`
- `timestamp_evidence_present`
- `transcript_artifact_present`
- `transcript_artifact_reference_present`
- `transcript_artifact_digest_present`
- `transcript_provider_present`
- `media_artifact_reference_present`
- `media_artifact_digest_present`
- `timestamp_segments_present_or_honestly_unavailable`
- `word_timing_evidence_present_or_honestly_unavailable`
- `utterance_timing_evidence_present_or_honestly_unavailable`
- `transcript_status_present`
- `timestamp_status_present`
- `transcript_verification_status_present`
- `timestamp_verification_status_present`
- `b2_evidence_status_present`
- `rehydrate_evidence_status_present`
- `provider_activity_status_present`
- `local_verification_status_present`
- `live_verification_status_present`
- `disclosure_boundary_present`
- `not_claimed_status_present`
- `unknown_status_present`
- `local_demo_evidence_present`
- `live_provider_evidence_not_available_present`
- `transcript_evidence_not_available_present`
- `timestamp_evidence_not_available_present`
- `speaker_identity_not_claimed_present`
- `voice_authenticity_not_claimed_present`
- `emotion_evidence_deferred_to_ps037c_present`
- `campaign_intelligence_deferred_to_ps037d_present`
- `proof_does_not_equal_truth_present`
- `no_transcript_correctness_claim`
- `no_timestamp_correctness_claim`
- `no_speaker_identity_claim`
- `no_voice_authenticity_claim`
- `no_semantic_truth_claim`
- `no_legal_authenticity_claim`
- `no_human_authorship_claim`
- `no_c2pa_authenticity_claim`
- `no_object_lock_claim`
- `no_tamper_proof_claim`
- `no_browser_side_b2_byte_verification_claim`
- `no_live_b2_availability_claim`
- `no_live_assemblyai_availability_claim`
- `no_production_security_claim`
- `no_identity_verification_claim`
- `no_biometric_identification_claim`
- `no_deepfake_detection_claim`
- `no_content_moderation_claim`
- `no_ocr_correctness_claim`
- `no_emotion_truth_claim`
- `no_model_output_truth_claim`
- `no_assemblyai_api_calls`
- `no_provider_calls`
- `no_live_b2_reads`
- `no_b2_writes`
- `no_broad_b2_scans`
- `no_recursive_smokes`
- `no_hidden_git_flags_h`
- `no_hidden_git_flags_S`
- `no_forbidden_overclaims`
- `prior_evidence_clean`
- `failures`

The required regression-gate and smoke contract commands and paths are:

- `python scripts/proofstudio_regression_gate.py --current ps037b --frontend --report-out /tmp/proofstudio-release-report.json`
- `python scripts/proofstudio_regression_gate.py --current ps037b --no-frontend --report-out /tmp/proofstudio-ps037b-regression-report.json`
- `scripts/ps037b_assemblyai_transcript_timestamp_evidence_smoke.py`
- `docs/evidence/ps-037b/assemblyai-transcript-timestamp-evidence-report.json`
- `docs/ps-037b-assemblyai-transcript-timestamp-evidence-proof.md`
