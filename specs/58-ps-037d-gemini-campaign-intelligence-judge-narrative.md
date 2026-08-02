# PS-037d — Gemini Campaign Intelligence / Judge Narrative

## 1. Status

PS-037d — Gemini Campaign Intelligence / Judge Narrative is currently:

- Spec only.
- Implementation pending. No product code, frontend code, backend code,
  scripts, evidence, AGENTS.md, `.env*`, `render.yaml`, or requirements files
  are changed during this phase.

PS-037d must not be implemented, and no implementation files may be changed,
until this spec is accepted by the PM. The authoritative accepted base is the
dynamic Git ref `origin/accepted/proofstudio`, never a hardcoded commit hash.
At the time of this spec the ref resolves to commit
`d766c5d6e3dcb227f65cc42303fae8bb4d4c72f8` (the post-PS-037c accepted state).
The ref is the authority; the commit hash is recorded for traceability only
and must not be treated as a hardcoded base.

This spec-only commit touches only this file:
`specs/58-ps-037d-gemini-campaign-intelligence-judge-narrative.md`.

PS-037d must not call Gemini, must not call any live model, must not call any
live provider, must not read or write live B2, must not perform broad B2 scans,
must not mutate any evidence, must not run the frontend, must not run the
backend, must not stage, commit, or push, and must not print secrets during
this phase. PS-037d obeys the root `AGENTS.md` operating law and the validation
policy in `docs/validation/proofstudio-smoke-harness-v1.md`.

## 2. Purpose

PS-037d defines a reusable Gemini Campaign Intelligence / Judge Narrative layer
that turns ProofStudio's existing recorded proof stack into a judge-facing
campaign story. The layer reads only what the pipeline already recorded (B2 /
archive / rehydrate evidence, Genblaze / manifest evidence, the PS-037
Disclosure + Trust Boundary, the PS-037a Multimodal Proof Layer, the PS-037b
AssemblyAI Transcript/Timestamp Evidence layer, and the PS-037c Voice/Audio
Evidence Provider Choice layer) and renders a consistent campaign-level
summary that makes the proof stack understandable as a campaign proof
narrative for judges, customers, and demo reviewers.

PS-037a (Multimodal Proof Layer), PS-037b (Transcript/Timestamp Evidence), and
PS-037c (Voice/Audio Evidence Provider Choice) already reserve honest
"campaign intelligence not available" / "campaign intelligence deferred to
PS-037d" deferred states pointing at PS-037d, but own no campaign intelligence
output and no judge narrative. PS-037d fills those reservations with a real,
inspectable campaign intelligence / judge narrative layer that answers, in one
consistent place, the basic campaign-story questions a judge or demo reviewer
asks:

- what campaign or demo story the proof stack represents
- which artifacts are included in the campaign proof narrative
- which evidence layers support the narrative
- which proof surfaces are summarized
- which providers / evidence tracks were recorded
- what the Gemini campaign intelligence label means in this slice
- whether campaign intelligence is local / demo / golden fixture evidence or
  live model evidence
- whether model output exists or is honestly unavailable
- whether the judge narrative is generated from recorded proof evidence
- whether the narrative cross-references B2 / archive / rehydrate evidence
- whether the narrative cross-references Genblaze / manifest evidence
- whether the narrative cross-references PS-037 Trust Boundary
- whether the narrative cross-references PS-037a Multimodal Proof
- whether the narrative cross-references PS-037b Transcript/Timestamp Evidence
- whether the narrative cross-references PS-037c Voice/Audio Evidence Provider
  Choice
- what the campaign narrative proves and does not prove
- whether semantic truth, legal authenticity, production security, campaign
  performance, or marketing effectiveness is claimed

The layer is a campaign intelligence / judge narrative inspection layer over
already-recorded or honestly-unavailable data, not a new proof surface, not a
new route, not a new backend endpoint, not a live Gemini integration, and not a
model generation system. It makes the existing campaign framing consistent and
judge-safe, and it states honestly what ProofStudio proves and what ProofStudio
does not prove for campaign intelligence and the judge narrative.

PS-037d proves what the pipeline recorded. The layer does not prove model
output truth, semantic truth, legal authenticity, human authorship, C2PA
authenticity, Object Lock / tamper-proof storage, browser-side B2 byte
verification, live B2 availability, live Gemini availability, production
security, production compliance, legal review, transcript correctness,
timestamp correctness, voice authenticity, speaker identity, emotion truth,
campaign performance prediction, marketing effectiveness, business outcome
guarantees, conversion lift, revenue impact, audience targeting accuracy, ad
compliance approval, identity verification, biometric identification, deepfake
detection, content moderation, OCR correctness, or chain-of-custody guarantees
beyond recorded pipeline evidence.

Gemini may be named as a campaign intelligence / judge narrative provider label
for evidence labeling only. Naming Gemini does not imply a live Gemini API
call, live Gemini availability, live model availability, or any correctness
guarantee.

## 3. Root Cause / Product Gap

ProofStudio already records a deep proof stack: B2 archive + rehydrate evidence
(PS-010, PS-020, PS-021, PS-026, PS-029, PS-036), Genblaze manifest evidence
(PS-028), the Disclosure + Trust Boundary (PS-037), the Multimodal Proof Layer
(PS-037a), the AssemblyAI Transcript/Timestamp Evidence layer (PS-037b), and
the Voice/Audio Evidence Provider Choice layer (PS-037c). Each layer is honest
about what it proves and what it does not prove. PS-037a, PS-037b, and PS-037c
all reserve honest "campaign intelligence not available" / "campaign
intelligence deferred to PS-037d" states.

Those reservations are honest, but they are only placeholders, and the proof
stack itself is now so deep that a reviewer cannot read it as a single
campaign story. There is no place where a judge or demo reviewer can read what
campaign or demo story the proof stack represents, which artifacts are
included in the campaign proof narrative, which evidence layers support the
narrative, which proof surfaces are summarized, which providers / evidence
tracks were recorded, what the Gemini campaign intelligence label means in this
slice, whether campaign intelligence is local/demo/golden fixture evidence or
live model evidence, whether model output exists or is honestly unavailable,
whether the judge narrative is generated from recorded proof evidence, and what
the narrative cross-references.

The gap this creates is judge-safety at the campaign / narrative boundary,
compounded by the risk of provider-name and campaign-word overclaim. Today:

- `apps/web/src/multimodalProof.ts` (PS-037a) reserves honest "campaign
  intelligence not available -> deferred to later slice (PS-037d Gemini campaign
  intelligence / judge narrative)" but PS-037a owns no campaign intelligence
  output, no judge narrative, no proof stack summary, and no campaign proof
  narrative. It can only say "campaign intelligence not available yet."
- `apps/web/src/assemblyAITranscriptEvidence.ts` (PS-037b) reserves honest
  "campaign intelligence deferred to PS-037d -> PS-037d (Gemini campaign
  intelligence / judge narrative)" but PS-037b owns no campaign narrative.
- `apps/web/src/voiceAudioEvidenceChoice.ts` (PS-037c) reserves honest
  "campaign intelligence deferred to PS-037d -> PS-037d (Gemini campaign
  intelligence / judge narrative)" but PS-037c owns no campaign narrative.
- no accepted slice records a campaign proof narrative, a campaign evidence
  summary, a judge narrative, a proof stack summary, a Gemini campaign
  intelligence provider label, a model output reference, a model output digest,
  a model output status, a campaign intelligence status, a judge narrative
  status, or a set of narrative source evidence references in a single
  inspectable place.
- a judge reading a proof surface today cannot tell what campaign story the
  proof stack represents, cannot read a single proof stack summary, and cannot
  tell whether a Gemini label means a live Gemini call, live Gemini
  availability, a model output, or a campaign performance claim. A Gemini name
  that appears without a clear disclosure boundary looks like a live model call
  or a correctness claim; a campaign word that appears without a clear boundary
  looks like a marketing effectiveness or business outcome claim.

PS-037d closes that gap by adding one shared campaign intelligence / judge
narrative layer — a canonical data module plus a shared component — that the
core proof surfaces render additively. The layer reads only accepted local /
golden / demo evidence and the existing accepted data modules, or exposes
explicit honest "not available" / "not claimed" / "unknown" states. It does not
invent a campaign performance number, a marketing effectiveness score, a
business outcome forecast, a conversion lift, a revenue impact figure, an
audience targeting accuracy, an ad compliance approval, or any model output
that is not in accepted data. It is local / static by default: it adds no
Gemini API calls, no provider calls, no live B2 reads, no B2 writes, no broad
B2 scans, no new backend, no new env, no new paid service dependency, and no
deployment changes.

Gemini is named as a campaign intelligence / judge narrative provider label for
evidence labeling only. The implementation must default to local/static
behavior. No live Gemini API call may occur unless a later PM-approved slice
explicitly enables a live-provider path with cost controls, env gates, and
evidence boundaries. The implementation phase relies on checked-in local /
golden / demo evidence or explicit unavailable states, and must not require
live provider credentials.

## 4. User Story

As a reviewer (designer, marketer, reviewer, client, or judge), I want one
honest, consistent campaign intelligence / judge narrative view, so that on any
core proof surface I can immediately read: what campaign or demo story the
proof stack represents; which artifacts are included in the campaign proof
narrative; which evidence layers support the narrative; which proof surfaces
are summarized; which providers / evidence tracks were recorded; what the
Gemini campaign intelligence label means in this slice; whether campaign
intelligence is local / demo / golden fixture evidence or live model evidence;
whether model output exists or is honestly unavailable; whether the judge
narrative is generated from recorded proof evidence; whether the narrative
cross-references B2 / archive / rehydrate evidence; whether it cross-references
Genblaze / manifest evidence; whether it cross-references PS-037 Trust
Boundary, PS-037a Multimodal Proof, PS-037b Transcript/Timestamp Evidence, and
PS-037c Voice/Audio Evidence Provider Choice; what the campaign narrative
proves and does not prove; and whether semantic truth, legal authenticity,
production security, campaign performance, or marketing effectiveness is
claimed — and so I never mistake a Gemini provider label for live Gemini
availability, a model output reference for semantic truth, a judge narrative
for legal authenticity, campaign intelligence for campaign performance, a
campaign narrative for marketing effectiveness, local campaign intelligence
for live Gemini availability, or demo/golden campaign narrative for production
security.

As a customer, I want the recorded proof stack understood as a single
campaign proof narrative that states, honestly, what the campaign proves, what
it does not prove, and what is honestly not available yet — including whether
any model output exists.

As a demo presenter, I want a reusable campaign intelligence / judge narrative
layer that is useful in a three-minute hackathon demo: a compact campaign
evidence summary that lists the campaign proof narrative, the proof stack
summary, the recorded campaign evidence and its honest "not available" / "not
claimed" / "unknown" states, plus an expanded judge-narrative panel that
states, verbatim, what campaign intelligence proves, what it does not prove,
what is unavailable, what is not claimed, and what the shared disclosure
boundary is — all working offline from accepted local / golden / demo
fixtures, with no Gemini API calls, no provider calls, no live B2 reads, no B2
writes, and no broad B2 scans.

## 5. Current Accepted Base

The current accepted base for PS-037d is:

- branch: `accepted/proofstudio`
- ref: `origin/accepted/proofstudio` (the authoritative source of truth; the
  ref is the authority, not any hardcoded commit hash)
- commit the ref resolves to at the time of this spec:
  `d766c5d6e3dcb227f65cc42303fae8bb4d4c72f8`
- this is the post-PS-037c accepted state: the Disclosure + Trust Boundary
  Layer from PS-037 is in place (`apps/web/src/trustBoundary.ts` +
  `apps/web/src/TrustBoundaryLayer.tsx`); the Multimodal Proof Layer from
  PS-037a is in place (`apps/web/src/multimodalProof.ts` +
  `apps/web/src/MultimodalProofLayer.tsx`), and PS-037a reserves honest
  "campaign intelligence not available -> deferred to later slice (PS-037d
  Gemini campaign intelligence / judge narrative)" pointing at PS-037d; the
  AssemblyAI Transcript/Timestamp Evidence layer from PS-037b is in place
  (`apps/web/src/assemblyAITranscriptEvidence.ts` +
  `apps/web/src/TranscriptTimestampEvidenceLayer.tsx`), and PS-037b reserves
  honest "campaign intelligence deferred to PS-037d" pointing at PS-037d; the
  Voice/Audio Evidence Provider Choice layer from PS-037c is in place
  (`apps/web/src/voiceAudioEvidenceChoice.ts` +
  `apps/web/src/VoiceAudioEvidenceChoiceLayer.tsx`), and PS-037c reserves
  honest "campaign intelligence deferred to PS-037d" pointing at PS-037d; the
  Archive / Rehydrate / B2 Audit Vault is in place from PS-036; the Review +
  Approval Workspace is in place from PS-035; the root `AGENTS.md` operating
  law is in place (PS-035D); the accepted-base-pointer-drift guard is in place
  (PS-035E); the central regression gate is non-mutating by default from
  PS-035C; the golden-fixture digest freeze is in place from PS-035B; the
  golden-run manifest carries a real non-null `manifest_uri` and a real 64-hex
  `manifest_hash` from PS-035A.

PS-037d must start from `origin/accepted/proofstudio`, not from `main`.

Relevant accepted facts at this base that PS-037d builds on (PS-037d must not
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
  core proof surfaces; PS-037d integrates with it and does not weaken it
- the PS-037a Multimodal Proof Layer exists and is rendered on the core proof
  surfaces; PS-037a reserves honest "campaign intelligence not available"
  pointing at PS-037d; PS-037d integrates with / fills the reservation PS-037a
  made and does not weaken it or remove its deferred states
- the PS-037b AssemblyAI Transcript/Timestamp Evidence layer exists and is
  rendered on the core proof surfaces; PS-037b reserves honest "campaign
  intelligence deferred to PS-037d"; PS-037d cross-references PS-037b and does
  not weaken the PS-037b layer
- the PS-037c Voice/Audio Evidence Provider Choice layer exists and is rendered
  on the core proof surfaces; PS-037c reserves honest "campaign intelligence
  deferred to PS-037d"; PS-037d cross-references PS-037c and does not weaken
  the PS-037c layer
- the existing shared component classes (`.trust-boundary`,
  `.trust-boundary-layer*`, the multimodal proof layer classes, the
  transcript/timestamp evidence layer classes, the voice/audio evidence
  provider choice layer classes, pills, cards, `JsonExpander`) already exist
  in `apps/web/src/styles.css`

## 6. Scope

PS-037d is a product slice. It adds a reusable Gemini Campaign Intelligence /
Judge Narrative layer (a shared data module plus a shared component) and
renders it additively on the core proof surfaces. It is local / static by
default: it must work without Gemini API calls, without provider calls, without
live B2 reads, without B2 writes, and without broad B2 scans, by reading
accepted local / golden / demo fixtures and existing accepted data modules, or
by surfacing explicit honest "not available" / "not claimed" / "unknown"
states.

PS-037d owns the campaign intelligence / judge narrative evidence layer only.
It must:

1. Add a shared, canonical campaign intelligence / judge narrative data module
   (`apps/web/src/geminiCampaignIntelligence.ts`, or the project's accepted
   equivalent) that exposes one consistent set of campaign intelligence / judge
   narrative concepts, the campaign proof narrative, the campaign evidence
   summary, the proof stack summary, the Gemini provider label, the model
   output reference / digest / status, honest "not available" / "not claimed"
   / "unknown" states, and deferred / unavailable later-slice states for every
   core proof surface.
2. Add a shared campaign intelligence / judge narrative component
   (`apps/web/src/CampaignIntelligenceJudgeNarrativeLayer.tsx`, or the
   project's accepted equivalent) that renders the layer, including an optional
   compact campaign evidence summary and an expanded judge-narrative panel
   pattern, reading only from `apps/web/src/geminiCampaignIntelligence.ts`.
3. Render the campaign intelligence / judge narrative layer additively on the
   required core proof surfaces (section 10.3) that are present in this repo so
   the campaign-intelligence / judge-narrative framing is consistent everywhere
   the campaign proof narrative is shown.
4. State, for campaign intelligence and the judge narrative, "what ProofStudio
   proves" and "what ProofStudio does not prove."
5. Surface the canonical campaign intelligence / judge narrative concepts
   (section 10.2): campaign intelligence, judge narrative, campaign proof
   narrative, campaign evidence summary, Gemini, Gemini provider label, model
   output reference, model output digest, model output status, campaign
   intelligence status, judge narrative status, narrative source evidence,
   narrative source evidence references, proof stack summary, B2 evidence
   cross-reference, manifest evidence cross-reference, rehydrate evidence
   cross-reference, trust boundary cross-reference, multimodal proof
   cross-reference, transcript/timestamp cross-reference, voice/audio evidence
   cross-reference, provider activity status, local verification, live
   verification status, disclosure boundary, not claimed, unknown, local/demo
   evidence, and live provider evidence not available.
6. Surface the honest unavailable / not-claimed states (section 10.6) verbatim
   so no reviewer mistakes an absent campaign intelligence output or judge
   narrative for a hidden proof, and no reviewer mistakes a Gemini label for a
   live Gemini call or a correctness claim.
7. Surface the canonical campaign-intelligence / judge-narrative
   de-escalation pairs (section 10.7) verbatim so no judge mistakes a
   strong-sounding campaign narrative or model output reference for a stronger
   guarantee.
8. Surface the canonical campaign-intelligence / judge-narrative negative
   boundary strings (section 10.8) verbatim.
9. Integrate with the PS-037 TrustBoundaryLayer (render alongside it; reuse the
   shared disclosure concepts; do not duplicate or weaken the PS-037 boundary).
10. Integrate / cross-reference with the PS-037a MultimodalProofLayer (render
    alongside it; fill the concrete campaign intelligence / judge narrative
    evidence that PS-037a only reserved as deferred; do not duplicate or weaken
    the PS-037a layer or its deferred campaign intelligence state).
11. Integrate / cross-reference with the PS-037b TranscriptTimestampEvidenceLayer
    (render alongside it; surface an honest transcript/timestamp
    cross-reference; do not duplicate or weaken the PS-037b layer).
12. Integrate / cross-reference with the PS-037c VoiceAudioEvidenceChoiceLayer
    (render alongside it; surface an honest voice/audio evidence
    cross-reference; do not duplicate or weaken the PS-037c layer).
13. Preserve the existing per-surface artifact / boundary panels; the shared
    campaign intelligence / judge narrative layer complements them. PS-037d
    must not delete or weaken any existing per-surface non-claim, per-surface
    artifact record, the PS-037 disclosure contract, the PS-037a multimodal
    proof contract, the PS-037b transcript/timestamp contract, or the PS-037c
    voice/audio evidence provider choice contract.
14. Be demo-friendly and judge-friendly: useful in a three-minute demo, no
    generic AI hype copy, no unsupported claims, no faked campaign performance,
    no faked marketing effectiveness, no faked business outcomes, no faked
    model output.
15. Work without Gemini API calls, without provider calls, without live B2
    reads, without B2 writes, and without broad B2 scans, by using accepted
    local / golden / demo data or existing accepted data paths.
16. Not mutate any prior evidence. Any PS-037d-owned evidence lives only under
    `docs/evidence/ps-037d/`.
17. Not change the golden run canonical constants, the historical contracts the
    regression gate verifies, any provider / B2 behavior, the PS-037 disclosure
    contract, the PS-037a multimodal proof contract, the PS-037b
    transcript/timestamp contract, or the PS-037c voice/audio evidence provider
    choice contract.

## 7. Non-goals

PS-037d must not:

- do not implement product code during the spec-only phase
- do not make any Gemini API call
- do not make any live model call
- do not make any live provider call
- do not implement live Gemini generation
- do not implement live model generation
- do not implement live provider routing
- do not implement the later or out-of-scope capabilities:
  - voice authenticity proof, speaker identity proof, biometric identification,
    emotion truth, psychological diagnosis, mental state diagnosis, health
    inference, content moderation, deepfake detection, legal review, or
    semantic truth verification (PS-037d must only reserve honest "not claimed"
    states for these; it must not fake them)
  - campaign performance prediction, marketing effectiveness proof, business
    outcome forecasting, conversion lift, revenue impact, audience targeting
    accuracy, or ad compliance approval (PS-037d must only reserve honest "not
    claimed" states for these; it must not fake them)
- do not implement identity verification, biometric identification, speaker
  identity proof, voice authenticity proof, emotion truth, mental state
  diagnosis, psychological diagnosis, health inference, content moderation,
  deepfake detection, legal review, semantic truth verification, OCR
  correctness, transcript correctness, timestamp correctness, campaign
  performance prediction, marketing effectiveness scoring, business outcome
  forecasting, conversion lift, revenue impact, audience targeting, or ad
  compliance review
- do not fake campaign intelligence outputs, judge narratives, proof stack
  summaries, model outputs, campaign performance numbers, marketing
  effectiveness scores, business outcome forecasts, conversion lift, revenue
  impact figures, audience targeting accuracies, or ad compliance approvals
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
- do not call Gemini (no Gemini API calls)
- do not call any model (no live model calls)
- do not call any provider (no provider calls)
- do not read B2 (no live B2 reads)
- do not write B2 (no B2 writes)
- do not perform broad B2 scans
- do not claim model output truth
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
- do not claim live Gemini availability unless a live Gemini check is explicitly
  implemented and approved with cost controls, env gates, and evidence
  boundaries
- do not claim production security
- do not claim production compliance
- do not claim legal review
- do not claim chain-of-custody guarantees beyond recorded pipeline evidence
- do not claim campaign performance prediction
- do not claim marketing effectiveness proof
- do not claim business outcome guarantee
- do not claim conversion lift
- do not claim revenue impact
- do not claim audience targeting accuracy
- do not claim ad compliance approval
- do not claim identity verification
- do not claim biometric identification
- do not claim deepfake detection
- do not claim content moderation
- do not claim OCR correctness
- do not claim transcript correctness
- do not claim timestamp correctness
- do not claim voice authenticity
- do not claim speaker identity
- do not claim emotion truth
- do not delete or weaken any existing per-surface truth-boundary panel,
  non-claim, artifact record, the PS-037 disclosure contract, the PS-037a
  multimodal proof contract, the PS-037b transcript/timestamp contract, or the
  PS-037c voice/audio evidence provider choice contract
- do not add a new backend, a new Gemini client, a new model client, a new
  provider wrapper, a new B2 client, a new env variable, a new paid service
  dependency, or any deployment change
- do not build CI, billing, deployment, auth, teams, permissions, or a full
  enterprise DAM
- do not change the golden run canonical constants
- do not change the historical contracts the regression gate verifies
- do not change the PS-037 disclosure contract
- do not change the PS-037a multimodal proof contract
- do not change the PS-037b transcript/timestamp contract
- do not change the PS-037c voice/audio evidence provider choice contract
- do not introduce a control name containing `KEY`, `TOKEN`, or `SECRET`
- do not use hidden Git flags (`assume-unchanged`, `skip-worktree`,
  `git update-index`, `update-index`)
- do not run recursive smokes
- do not use generic AI hype copy or unsupported claims
- do not create duplicate context-blind overclaim scanners in chat/spec
  guidance; the PS-037d smoke and its evidence report are the source of truth
  for slice overclaim validation; do not scan smoke guard fixtures as product
  claims

PS-037d only edits this spec file in the spec-only phase.
Implementation-phase candidate files are listed in section 8.

## 8. Implementation Candidate Files

The following are implementation-phase candidates only, clearly marked as
implementation-phase only. They are **not** for this spec-only commit. They are
listed so the implementation phase has a grounded file plan that follows
existing app conventions (each surface has a PascalCase `.tsx` component, a
camelCase `.ts` data module, a smoke script, and an evidence directory).

Shared layer (new files):
- `apps/web/src/geminiCampaignIntelligence.ts` (new) — the canonical camelCase
  campaign intelligence / judge narrative data module. Exposes the single
  shared set of campaign intelligence / judge narrative concepts, the campaign
  proof narrative, the campaign evidence summary, the proof stack summary, the
  Gemini provider label, the model output reference / digest / status, the
  campaign intelligence status, the judge narrative status, the narrative
  source evidence references, the cross-references (B2 / manifest / rehydrate /
  trust boundary / multimodal proof / transcript/timestamp / voice/audio),
  honest "not available" / "not claimed" / "unknown" states, deferred
  later-slice states, de-escalation pairs, negative boundary strings, and
  not-claimed / unknown status used by every core proof surface. Same
  convention as `voiceAudioEvidenceChoice.ts`, `assemblyAITranscriptEvidence.ts`,
  `multimodalProof.ts`, `trustBoundary.ts`, `b2Evidence.ts`,
  `b2RehydrateComparison.ts`, `judgeEvidencePack.ts`, etc. Gemini is named as a
  campaign intelligence / judge narrative provider label for evidence labeling
  only; the module must not contain a live Gemini API call.
- `apps/web/src/CampaignIntelligenceJudgeNarrativeLayer.tsx` (new) — the shared
  campaign intelligence / judge narrative component. Accepts the existing
  `variant` convention (for example `variant="panel"` for an expanded
  judge-narrative panel and `variant="summary"` / `variant="badge"` for a
  compact campaign evidence summary), reads only from
  `apps/web/src/geminiCampaignIntelligence.ts`, and renders the campaign
  intelligence / judge narrative layer with no Gemini API calls, no provider
  calls, and no live B2 reads. Rendered alongside the existing
  `TrustBoundaryLayer` (PS-037), `MultimodalProofLayer` (PS-037a),
  `TranscriptTimestampEvidenceLayer` (PS-037b), and
  `VoiceAudioEvidenceChoiceLayer` (PS-037c).

Additive use on core proof surfaces (existing files, edited additively only):
- `apps/web/src/JudgeCockpitHome.tsx` (PS-023) — render the campaign
  intelligence / judge narrative layer on the home surface.
- `apps/web/src/B2EvidenceExplorer.tsx` (PS-026) — render the campaign
  intelligence / judge narrative layer (B2 evidence cross-reference).
- `apps/web/src/B2RehydrateComparison.tsx` (PS-029) — render the campaign
  intelligence / judge narrative layer (rehydrate evidence cross-reference).
- `apps/web/src/ManifestVerificationPanel.tsx` (PS-028) — render the campaign
  intelligence / judge narrative layer (manifest evidence cross-reference).
- `apps/web/src/B2AuditVault.tsx` (PS-036) — render the campaign intelligence /
  judge narrative layer (B2 / rehydrate evidence cross-reference audit).
- `apps/web/src/ReviewApprovalWorkspace.tsx` (PS-035) — render the campaign
  intelligence / judge narrative layer (the reviewable artifact's campaign
  proof narrative).
- `apps/web/src/JudgeEvidencePack.tsx` (PS-031) — render the campaign
  intelligence / judge narrative layer (export-pack campaign evidence summary).
- `apps/web/src/PublicPassportPage.tsx` (PS-019) — render the campaign
  intelligence / judge narrative layer (provenance passport campaign proof
  narrative).
- `apps/web/src/App.tsx` (PS-013 / PS-014) — render the campaign intelligence /
  judge narrative layer on the Review Room, complementing the existing asset /
  manifest / evidence panels, the PS-037 disclosure layer, the PS-037a
  multimodal proof layer, the PS-037b transcript/timestamp evidence layer, and
  the PS-037c voice/audio evidence provider choice layer.

Additive styles (existing file, additive classes only):
- `apps/web/src/styles.css` — add only the classes needed for the campaign
  intelligence / judge narrative layer (campaign-narrative pills, judge-narrative
  pills, proof-stack-summary rows, campaign-evidence-summary rows,
  gemini-provider-label pills, model-output-reference rows,
  model-output-digest rows, narrative-source-evidence-rows,
  cross-reference pills, unavailable / not-claimed / unknown pills). No global
  style rewrite. PS-037d must not remove or weaken the existing
  `.trust-boundary-layer*` classes from PS-037, the multimodal proof layer
  classes from PS-037a, the transcript/timestamp evidence layer classes from
  PS-037b, or the voice/audio evidence provider choice layer classes from
  PS-037c.

Backend (`src/proofstudio`) — none:
- PS-037d is a frontend-only campaign intelligence / judge narrative layer over
  existing accepted data. No backend change is expected. If any read-only reuse
  of an accepted data path is needed, it must reuse the existing accepted data
  paths under `src/proofstudio/api/` and `src/proofstudio/provenance/` without
  calling Gemini, without calling any model, without calling any provider, and
  without reading live B2. No new provider wiring, no Gemini client, no model
  client, no new B2 client, no new B2 write path, no new broad B2 scan path. If
  no backend change is needed, none is made.

Smoke (scripts):
- `scripts/ps037d_gemini_campaign_intelligence_judge_narrative_smoke.py` (new)
  — the PS-037d feature smoke. Must reuse `scripts/smoke_lib.py` for shared
  validation logic and must implement its own explicit `h` / `S`
  hidden-Git-flags checker (see section 14). Local / static only.

Spec / docs:
- `specs/07-master-spec-plan.md` — implementation-phase cross-reference only
  (register PS-037d acceptance). Must not change any historical item or golden
  constant.
- `specs/08-roadmap-slices.md` — implementation-phase status update only.
- `docs/validation/proofstudio-smoke-harness-v1.md` — implementation-phase
  PS-037d note only, additive, must not weaken any existing PS-034A / PS-035C
  contract.
- `docs/ps-037d-gemini-campaign-intelligence-judge-narrative-proof.md` (new) —
  the PS-037d proof doc.

Evidence:
- `docs/evidence/ps-037d/gemini-campaign-intelligence-judge-narrative-report.json`
  (new) — the only evidence PS-037d may write, and only when `--write-evidence`
  is explicit.

Any edit to `src/proofstudio/**` during implementation requires the backend
change to remain read-only over accepted data and to make no Gemini API call,
no model call, no provider call, and no live B2 read.

## 9. Forbidden files Unless PM-approved Later

PS-037d implementation must not touch without explicit PM approval:

- `AGENTS.md`
- `.env*`
- `render.yaml`
- requirements files
- `docs/evidence/**` paths other than `docs/evidence/ps-037d/**`
- any prior-slice evidence prefix (for example `docs/evidence/ps-037c/**`,
  `docs/evidence/ps-037b/**`, `docs/evidence/ps-037a/**`,
  `docs/evidence/ps-037/**`, `docs/evidence/ps-036/**`,
  `docs/evidence/ps-035/**`, `docs/evidence/ps-031/**`,
  `docs/evidence/ps-029/**`, `docs/evidence/ps-026/**`,
  `docs/evidence/ps-021/**`, `docs/evidence/demo/golden-demo-run.json`,
  `docs/evidence/golden-fixture-digests.json`)
- `scripts/proofstudio_regression_gate.py` (the central gate is not owned by
  PS-037d)
- `scripts/smoke_lib.py` (shared library; PS-037d must not mutate shared
  validation behavior)
- any provider wrapper under `src/proofstudio/providers/**` (PS-037d owns no
  live provider behavior)
- any B2 client / storage write path (PS-037d performs no live B2 read, no B2
  write, and no broad B2 scan)
- any Gemini client / live Gemini integration path (PS-037d names Gemini for
  campaign intelligence / judge narrative evidence labeling only; no live Gemini
  API call is allowed unless a later PM-approved slice explicitly enables a
  live-provider path with cost controls, env gates, and evidence boundaries)
- any live model client / live model integration path (PS-037d names Gemini for
  campaign intelligence / judge narrative evidence labeling only; no live model
  call is allowed unless a later PM-approved slice explicitly enables a
  live-provider path with cost controls, env gates, and evidence boundaries)
- the PS-037 disclosure contract files (`apps/web/src/trustBoundary.ts`,
  `apps/web/src/TrustBoundaryLayer.tsx`) except for additive integration; any
  change that weakens or duplicates the PS-037 boundary is forbidden
- the PS-037a multimodal proof contract files
  (`apps/web/src/multimodalProof.ts`, `apps/web/src/MultimodalProofLayer.tsx`)
  except for additive cross-reference; any change that weakens, duplicates, or
  removes the PS-037a deferred campaign intelligence state is forbidden
- the PS-037b transcript/timestamp contract files
  (`apps/web/src/assemblyAITranscriptEvidence.ts`,
  `apps/web/src/TranscriptTimestampEvidenceLayer.tsx`) except for additive
  cross-reference; any change that weakens, duplicates, or removes the PS-037b
  contract is forbidden
- the PS-037c voice/audio evidence provider choice contract files
  (`apps/web/src/voiceAudioEvidenceChoice.ts`,
  `apps/web/src/VoiceAudioEvidenceChoiceLayer.tsx`) except for additive
  cross-reference; any change that weakens, duplicates, or removes the PS-037c
  contract is forbidden

The only implementation-phase files allowed without PM approval are those in
section 8. Any other path requires explicit PM approval.

## 10. Gemini Campaign Intelligence / Judge Narrative Product Contract

PS-037d defines the following contract for the Gemini Campaign Intelligence /
Judge Narrative layer.

### 10.1 Layer identity

- It is a reusable campaign intelligence / judge narrative layer, not a new
  proof surface, not a new route, and not a new backend endpoint.
- It is narrative-over-recorded-proof by design: it reads what the pipeline
  already recorded and renders a consistent campaign proof narrative. It is not
  a model generation system and not a live Gemini integration.
- It is purely client-side by default: it makes no Gemini API call, calls no
  model, calls no provider, reads no B2 object, exposes no arbitrary `run_id`
  input, performs no browser-side B2 byte verification, performs no broad B2
  scan, and writes no B2 object.
- It is sourced from accepted local / golden / demo data and existing accepted
  data modules only, or from explicit honest "not available" / "not claimed" /
  "unknown" states.
- It makes the campaign-intelligence / judge-narrative framing consistent on
  every core proof surface. It does not invent new model outputs, new campaign
  performance numbers, new marketing effectiveness scores, new business outcome
  forecasts, new conversion lift, new revenue impact, new audience targeting
  accuracies, or new ad compliance approvals; it states the existing recorded
  campaign evidence consistently and honestly, and it states honest "not
  available" / "not claimed" / "unknown" states where no evidence exists.
- Gemini is named as a campaign intelligence / judge narrative provider label
  for evidence labeling only. Naming Gemini does not imply a live Gemini API
  call, live Gemini availability, live model availability, or any correctness
  guarantee. The Gemini label does not equal live Gemini availability.
- It integrates with the PS-037 Disclosure + Trust Boundary Layer: it renders
  alongside `TrustBoundaryLayer` and reuses the shared disclosure concepts, and
  must not duplicate or weaken the PS-037 boundary.
- It integrates / cross-references the PS-037a Multimodal Proof Layer: it
  renders alongside `MultimodalProofLayer` and fills the concrete campaign
  intelligence / judge narrative evidence that PS-037a only reserved as
  deferred, and must not duplicate, weaken, or remove the PS-037a deferred
  campaign intelligence state.
- It integrates / cross-references the PS-037b Transcript/Timestamp Evidence
  layer: it renders alongside `TranscriptTimestampEvidenceLayer` and surfaces an
  honest transcript/timestamp cross-reference, and must not duplicate or weaken
  the PS-037b contract.
- It integrates / cross-references the PS-037c Voice/Audio Evidence Provider
  Choice layer: it renders alongside `VoiceAudioEvidenceChoiceLayer` and
  surfaces an honest voice/audio evidence cross-reference, and must not
  duplicate or weaken the PS-037c contract.

### 10.2 Required campaign-intelligence / judge-narrative concepts

The layer must surface these canonical campaign intelligence / judge narrative
concepts, each as a clearly labeled item:

- `campaign intelligence` — the recorded campaign intelligence framing, sourced
  from accepted evidence or honestly unavailable. Campaign intelligence does not
  equal campaign performance.
- `judge narrative` — the judge-facing narrative over the recorded proof stack,
  generated from recorded proof evidence or honestly unavailable. Judge
  narrative does not equal legal authenticity.
- `campaign proof narrative` — what campaign or demo story the proof stack
  represents.
- `campaign evidence summary` — a compact summary of the campaign evidence the
  narrative covers.
- `Gemini` — the named provider for campaign intelligence / judge narrative
  evidence labeling.
- `Gemini provider label` — the labeling-only provider label. The Gemini label
  does not equal live Gemini availability.
- `model output reference` — where the model output reference is recorded, if
  available; honestly surfaced or honestly unavailable.
- `model output digest` — the recorded hash / digest for the model output, if
  available; honestly surfaced or honestly unavailable.
- `model output status` — the honest status of the model output (present / not
  available / not claimed / unknown). Model output does not equal semantic
  truth.
- `campaign intelligence status` — the honest status of the campaign
  intelligence (present / not available / not claimed / unknown).
- `judge narrative status` — the honest status of the judge narrative (present
  / not available / not claimed / unknown).
- `narrative source evidence` — the set of recorded evidence the narrative is
  generated from.
- `narrative source evidence references` — the cross-references that point at
  the source evidence the narrative is generated from.
- `proof stack summary` — a single consistent summary of the recorded proof
  stack (B2 / manifest / rehydrate / trust boundary / multimodal proof /
  transcript/timestamp / voice/audio) the narrative is built over.
- `B2 evidence cross-reference` — whether the narrative cross-references B2 /
  archive / rehydrate evidence.
- `manifest evidence cross-reference` — whether the narrative cross-references
  Genblaze / manifest evidence.
- `rehydrate evidence cross-reference` — whether the narrative cross-references
  rehydrate evidence.
- `trust boundary cross-reference` — whether the narrative cross-references the
  PS-037 Disclosure + Trust Boundary.
- `multimodal proof cross-reference` — whether the narrative cross-references
  the PS-037a Multimodal Proof Layer.
- `transcript/timestamp cross-reference` — whether the narrative
  cross-references the PS-037b Transcript/Timestamp Evidence layer.
- `voice/audio evidence cross-reference` — whether the narrative
  cross-references the PS-037c Voice/Audio Evidence Provider Choice layer.
- `provider activity status` — whether provider activity happened for the
  campaign intelligence (no provider calls by default; local/demo evidence by
  default).
- `local verification` — whether evidence is locally verified against
  checked-in / accepted data.
- `live verification status` — whether a live check is in scope (local /
  check-only by default; live provider evidence not available by default).
- `disclosure boundary` — the campaign-intelligence / judge-narrative
  disclosure boundary, sourced from / consistent with PS-037.
- `not claimed` — the honest set of things ProofStudio does not claim for
  campaign intelligence / judge narrative.
- `unknown` — what remains unknown or not surfaced for campaign intelligence /
  judge narrative.
- `local/demo evidence` — whether the campaign intelligence / judge narrative
  evidence is local / demo / golden fixture evidence (the default posture).
- `live provider evidence not available` — the honest default state that no
  live provider campaign intelligence / judge narrative evidence is available.

If a concept does not apply, the layer must show an honest "not available" /
"not claimed" / "unknown" state and must not fabricate a value.

### 10.3 Required surfaces

The campaign intelligence / judge narrative layer must be rendered
(additively) on at least these required core proof surfaces, so
`required_surfaces_have_campaign_intelligence_layer` is truthful:

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

- local campaign intelligence / judge narrative evidence (campaign proof
  narrative, campaign evidence summary, proof stack summary, narrative source
  evidence references, model output reference / digest recorded in accepted
  checked-in data)
- live evidence (none, by default — PS-037d performs no Gemini API call, no
  model call, no provider call, and no live B2 read)
- demo / golden evidence (the golden demo run, which is local / golden, not
  production)

A reviewer reading the layer must never mistake a Gemini label for live Gemini
availability, a model output reference for semantic truth, a judge narrative
for legal authenticity, campaign intelligence for campaign performance, a
campaign narrative for marketing effectiveness, local campaign intelligence for
live Gemini availability, or a demo/golden campaign narrative for production
security.

### 10.5 Model output honesty

The layer must never fabricate a model output. Where no model output exists in
accepted data, the layer must surface honest "model output not available" and
"Gemini evidence not available" states. Where a model output reference /
digest is recorded in accepted data, the layer must surface it as recorded
evidence (local / recorded-only) and must not imply model output truth,
semantic truth, or live Gemini availability. The model output status and the
Gemini provider label must be honestly local / recorded-only by default.

### 10.6 Required unavailable / not-claimed states (verbatim)

The layer must surface, honestly, these unavailable / not-claimed states
verbatim. These are non-claim states: they state what is not available, not
claimed, or unknown, and must never be read as a hidden proof:

- local/demo evidence
- live provider evidence not available
- Gemini evidence not available
- model output not available
- campaign intelligence not available
- judge narrative not available
- campaign performance prediction not claimed
- marketing effectiveness proof not claimed
- business outcome guarantee not claimed
- conversion lift not claimed
- revenue impact not claimed
- audience targeting accuracy not claimed
- ad compliance approval not claimed
- model output truth not claimed
- semantic truth not claimed
- legal authenticity not claimed
- voice authenticity not claimed
- speaker identity not claimed
- biometric identification not claimed
- emotion truth not claimed
- deepfake detection not claimed
- content moderation not claimed
- transcript correctness not claimed
- timestamp correctness not claimed
- not claimed
- unknown

PS-037d must not fake a campaign intelligence output, a judge narrative, a
model output, a campaign performance number, a marketing effectiveness score,
a business outcome forecast, a conversion lift, a revenue impact figure, an
audience targeting accuracy, or an ad compliance approval. The honest
unavailable / not-claimed / unknown states are the only acceptable
representation of those concepts when no accepted evidence exists.

### 10.7 Required de-escalation pairs (verbatim)

The layer must surface these campaign-intelligence / judge-narrative
de-escalation pairs verbatim so a judge never mistakes a strong-sounding
campaign narrative, Gemini label, or model output reference for a stronger
guarantee:

- proof does not equal truth
- Gemini label does not equal live Gemini availability
- model output does not equal semantic truth
- judge narrative does not equal legal authenticity
- campaign intelligence does not equal campaign performance
- campaign narrative does not equal marketing effectiveness
- local campaign intelligence does not equal live Gemini availability
- demo/golden campaign narrative does not equal production security

### 10.8 Required negative boundary strings (verbatim)

The layer must surface these negative boundary strings verbatim:

- not model output truth
- not semantic truth
- not legal authenticity
- not human authorship
- not C2PA authenticity
- not Object Lock
- not tamper-proof
- not browser-side B2 byte verification
- not live B2 availability
- not live Gemini availability
- not production security
- not production compliance
- not legal review
- not chain-of-custody guarantee
- not campaign performance prediction
- not marketing effectiveness proof
- not business outcome guarantee
- not conversion lift
- not revenue impact
- not audience targeting accuracy
- not ad compliance approval
- not identity verification
- not biometric identification
- not deepfake detection
- not content moderation
- not OCR correctness
- not transcript correctness
- not timestamp correctness
- not voice authenticity
- not speaker identity
- not emotion truth

### 10.9 Boundary honesty

The layer must not imply that any ProofStudio campaign intelligence output,
judge narrative, campaign proof narrative, campaign evidence summary, proof
stack summary, Gemini provider label, model output reference, model output
digest, or narrative source evidence reference proves anything beyond what the
pipeline recorded. In particular it must not imply that those concepts prove
model output truth, semantic truth, legal authenticity, human authorship, C2PA
authenticity, Object Lock / tamper-proof storage, browser-side B2 byte
verification, live B2 availability, live Gemini availability, production
security, production compliance, legal review, chain-of-custody guarantees,
campaign performance prediction, marketing effectiveness, business outcome
guarantee, conversion lift, revenue impact, audience targeting accuracy, ad
compliance approval, identity verification, biometric identification, deepfake
detection, content moderation, OCR correctness, transcript correctness,
timestamp correctness, voice authenticity, speaker identity, or emotion truth.

## 11. UI/UX Contract

The Gemini Campaign Intelligence / Judge Narrative layer UI must include:

- A clear title: "Gemini Campaign Intelligence / Judge Narrative" (or an
  equivalent clear title), with a positioning line that ProofStudio proves what
  the pipeline recorded for campaign intelligence / judge narrative, that this
  is a narrative-over-recorded-proof layer, and that Gemini is named as a
  campaign intelligence / judge narrative provider label for evidence labeling
  only (the Gemini label does not equal live Gemini availability).
- A compact campaign evidence summary variant (for example `variant="summary"`
  or `variant="badge"`) that lists, in one compact block, the campaign proof
  narrative, the proof stack summary, the recorded campaign evidence and its
  honest "not available" / "not claimed" / "unknown" states, suitable for
  surfaces where space is constrained.
- An expanded judge-narrative panel variant (for example `variant="panel"`)
  that states, in full, the campaign intelligence / judge narrative contract.
- A campaign-narrative block that shows: campaign intelligence, judge narrative,
  campaign proof narrative, campaign evidence summary, proof stack summary,
  and the campaign intelligence status / judge narrative status.
- a Gemini / model-output block that shows: Gemini, Gemini provider label,
  model output reference, model output digest, model output status, provider
  activity status, and an honest unavailable / not claimed / unknown state
  where no value exists.
- A narrative-source-evidence block that shows: narrative source evidence,
  narrative source evidence references, B2 evidence cross-reference, manifest
  evidence cross-reference, rehydrate evidence cross-reference, trust boundary
  cross-reference, multimodal proof cross-reference, transcript/timestamp
  cross-reference, and voice/audio evidence cross-reference.
- A local / live block that shows: local verification, live verification
  status, local/demo evidence, and live provider evidence not available.
- A "not claimed" section listing, verbatim, what campaign intelligence / judge
  narrative does not prove (section 10.8), the honest unavailable /
  not-claimed states (section 10.6).
- The de-escalation pairs (section 10.7), surfaced verbatim.
- The negative boundary strings (section 10.8), surfaced verbatim.
- Integration with the PS-037 Disclosure + Trust Boundary Layer: the campaign
  intelligence / judge narrative layer renders alongside `TrustBoundaryLayer`,
  reuses the shared disclosure concepts, and never contradicts the PS-037
  boundary.
- Integration / cross-reference with the PS-037a Multimodal Proof Layer, the
  PS-037b Transcript/Timestamp Evidence layer, and the PS-037c Voice/Audio
  Evidence Provider Choice layer: the campaign intelligence / judge narrative
  layer renders alongside those layers, cross-references them honestly, and
  never contradicts or weakens their contracts.
- A persistent campaign-intelligence / judge-narrative boundary statement that
  states verbatim (or equivalent):

  > ProofStudio proves what the pipeline recorded for campaign intelligence /
  > judge narrative. Proof does not equal truth. The Gemini label does not
  > equal live Gemini availability. A model output reference does not equal
  > semantic truth. A judge narrative does not equal legal authenticity.
  > Campaign intelligence does not equal campaign performance. A campaign
  > narrative does not equal marketing effectiveness. Local campaign
  > intelligence does not equal live Gemini availability. Demo/golden campaign
  > narrative does not equal production security.

UI / UX constraints:

- Must be useful in a three-minute hackathon demo: open any core proof surface
  -> read the compact campaign evidence summary -> read the campaign proof
  narrative and the proof stack summary -> expand the judge-narrative panel ->
  read what campaign intelligence proves -> read what it does not prove -> read
  the unavailable / not-claimed states -> read the de-escalation pairs -> read
  the negative boundary strings.
- Must render the same campaign-intelligence / judge-narrative framing on every
  required surface (section 10.3).
- Must not introduce generic AI hype copy.
- Must not add unsupported claims.
- Must not fabricate campaign intelligence outputs, judge narratives, model
  outputs, campaign performance numbers, marketing effectiveness scores,
  business outcome forecasts, conversion lift, revenue impact figures,
  audience targeting accuracies, ad compliance approvals, digests, or any
  provider output that is not in accepted data.
- Must follow the existing component conventions (`variant`, pills, cards,
  `JsonExpander`, the `.trust-boundary`, `.trust-boundary-layer*`, multimodal
  proof layer, transcript/timestamp evidence layer, and voice/audio evidence
  provider choice layer styles) used by the other surfaces.
- Must not delete or weaken any existing per-surface truth-boundary panel,
  per-surface artifact record, the PS-037 disclosure layer, the PS-037a
  multimodal proof layer, the PS-037b transcript/timestamp evidence layer, or
  the PS-037c voice/audio evidence provider choice layer; the campaign
  intelligence / judge narrative layer is additive.

## 12. Data Contract

### 12.1 Source data (read-only inputs)

PS-037d reads accepted local / golden / demo data and existing accepted data
modules as immutable inputs. It must not mutate these and must not change their
canonical values. Acceptable read-only sources:

- `apps/web/src/trustBoundary.ts` (PS-037) — reuse the shared disclosure
  concepts; do not duplicate or weaken them
- `apps/web/src/multimodalProof.ts` (PS-037a) — reuse / fill the deferred
  campaign intelligence reservation; do not duplicate, weaken, or remove it
- `apps/web/src/assemblyAITranscriptEvidence.ts` (PS-037b) — reuse /
  cross-reference the transcript/timestamp evidence; do not duplicate, weaken,
  or remove it
- `apps/web/src/voiceAudioEvidenceChoice.ts` (PS-037c) — reuse /
  cross-reference the voice/audio evidence provider choice; do not duplicate,
  weaken, or remove it
- `apps/web/src/b2Evidence.ts` (PS-026) — archive URI, archive SHA-256,
  rehydrate source, provider-call counts
- `apps/web/src/b2RehydrateComparison.ts` (PS-029) — rehydrate evidence
- `apps/web/src/manifestVerification.ts` (PS-028) — `manifest_uri`,
  `manifest_hash`
- `apps/web/src/b2AuditVault.ts` (PS-036)
- `apps/web/src/failureAsProofTimeline.ts` (PS-030)
- `apps/web/src/judgeEvidencePack.ts` (PS-031) — final asset / archive summary
- `apps/web/src/operationsCockpit.ts` (PS-032)
- `apps/web/src/providerDecisionIntelligence.ts` (PS-033)
- `apps/web/src/lineageComparisonLab.ts` (PS-034)
- `apps/web/src/reviewApprovalWorkspace.ts` (PS-035)
- `apps/web/src/api.ts` (passport / trust_boundary shape exposed by the
  Provenance Passport)
- `docs/evidence/demo/golden-demo-run.json` — `archive_uri`, `archive_sha256`,
  `manifest_uri`, `manifest_hash`, `rehydrate_source`,
  `provider_calls_during_rehydrate`, and the honest `unavailable_fields` map
- `docs/evidence/golden-fixture-digests.json`

Where no accepted campaign intelligence / judge narrative evidence exists,
PS-037d must surface explicit honest "not available" / "not claimed" /
"unknown" states and must not fabricate values. PS-037d must not change the
golden run canonical constants. The canonical constants are owned by their
respective accepted slices.

### 12.2 Campaign intelligence / judge narrative item shape

A campaign intelligence / judge narrative item is derived from accepted data
and must expose:

- `campaign_intelligence` (the recorded campaign intelligence framing, honestly
  surfaced)
- `judge_narrative` (the judge-facing narrative over the recorded proof stack,
  honestly surfaced)
- `campaign_proof_narrative` (what campaign or demo story the proof stack
  represents)
- `campaign_evidence_summary` (a compact summary of the campaign evidence)
- `gemini_provider_label` (the labeling-only Gemini provider label)
- `model_output_reference` (the recorded model output reference, if available,
  or honestly unavailable)
- `model_output_digest` (the recorded model output digest, if available, or
  honestly unavailable)
- `model_output_status` (one of `present`, `not_available`, `not_claimed`,
  `unknown`)
- `campaign_intelligence_status` (one of `present`, `not_available`,
  `not_claimed`, `unknown`)
- `judge_narrative_status` (one of `present`, `not_available`, `not_claimed`,
  `unknown`)
- `narrative_source_evidence` (the set of recorded evidence the narrative is
  generated from)
- `narrative_source_evidence_references` (the cross-references pointing at the
  source evidence)
- `proof_stack_summary` (a single consistent summary of the recorded proof
  stack)
- `b2_evidence_cross_reference` (honest indicator)
- `manifest_evidence_cross_reference` (honest indicator)
- `rehydrate_evidence_cross_reference` (honest indicator)
- `trust_boundary_cross_reference` (honest indicator)
- `multimodal_proof_cross_reference` (honest indicator)
- `transcript_timestamp_cross_reference` (honest indicator)
- `voice_audio_evidence_cross_reference` (honest indicator)
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
  `not_verified`, `not_available`, `not_claimed`, `unknown`,
  `deferred_to_later_slice`)

### 12.3 Evidence report schema rule

The PS-037d evidence report must follow the harness schema rule: boolean
fields remain booleans and detail / list fields use explicit detail names. A
field whose name implies a boolean success flag must remain a boolean. List
fields must use explicit detail names such as `_ids`, `_details`, or
`_failures` (see section 13).

## 13. Evidence Contract

PS-037d owns exactly one evidence directory: `docs/evidence/ps-037d/`.

- A feature smoke may write only its own evidence, and only when
  `--write-evidence` is explicit. The default PS-037d smoke behavior is
  non-mutating local validation.
- PS-037d must not write any file outside `docs/evidence/ps-037d/`.
- PS-037d must not mutate any prior-slice evidence (every prior evidence prefix
  is guarded by `scripts/smoke_lib.py` and
  `scripts/proofstudio_regression_gate.py`), including the PS-037 evidence
  under `docs/evidence/ps-037/`, the PS-037a evidence under
  `docs/evidence/ps-037a/`, the PS-037b evidence under
  `docs/evidence/ps-037b/`, and the PS-037c evidence under
  `docs/evidence/ps-037c/`.
- The PS-037d evidence file is
  `docs/evidence/ps-037d/gemini-campaign-intelligence-judge-narrative-report.json`.

The PS-037d evidence report must carry these boolean fields (booleans as
booleans; `failures` as a list):

- `ok` (boolean; true only when every measured field is truthful and no
  forbidden overclaim or forbidden file change is present)
- `slice_id`: `ps037d`
- `campaign_intelligence_component_present` (boolean;
  `CampaignIntelligenceJudgeNarrativeLayer` component exists)
- `campaign_intelligence_data_module_present` (boolean;
  `geminiCampaignIntelligence.ts` exists)
- `campaign_intelligence_layer_present` (boolean; the shared layer is wired in)
- `required_surfaces_have_campaign_intelligence_layer` (boolean; the required
  surfaces in section 10.3 that are present in this repo render the layer)
- `trust_boundary_cross_reference_present` (boolean; the layer integrates /
  cross-references the PS-037 Disclosure + Trust Boundary Layer)
- `multimodal_proof_cross_reference_present` (boolean; the layer integrates /
  cross-references the PS-037a Multimodal Proof Layer)
- `transcript_timestamp_cross_reference_present` (boolean; the layer integrates
  / cross-references the PS-037b Transcript/Timestamp Evidence layer)
- `voice_audio_evidence_cross_reference_present` (boolean; the layer integrates
  / cross-references the PS-037c Voice/Audio Evidence Provider Choice layer)
- `gemini_label_present` (boolean; Gemini is named as a campaign intelligence /
  judge narrative provider label for evidence labeling)
- `campaign_intelligence_present` (boolean)
- `judge_narrative_present` (boolean)
- `campaign_proof_narrative_present` (boolean)
- `campaign_evidence_summary_present` (boolean)
- `gemini_provider_label_present` (boolean)
- `model_output_reference_present_or_honestly_unavailable` (boolean)
- `model_output_digest_present_or_honestly_unavailable` (boolean)
- `model_output_status_present` (boolean)
- `campaign_intelligence_status_present` (boolean)
- `judge_narrative_status_present` (boolean)
- `narrative_source_evidence_present` (boolean)
- `narrative_source_evidence_references_present` (boolean)
- `proof_stack_summary_present` (boolean)
- `b2_evidence_cross_reference_present` (boolean)
- `manifest_evidence_cross_reference_present` (boolean)
- `rehydrate_evidence_cross_reference_present` (boolean)
- `provider_activity_status_present` (boolean)
- `local_verification_status_present` (boolean)
- `live_verification_status_present` (boolean)
- `disclosure_boundary_present` (boolean)
- `not_claimed_status_present` (boolean)
- `unknown_status_present` (boolean)
- `local_demo_evidence_present` (boolean)
- `live_provider_evidence_not_available_present` (boolean)
- `gemini_evidence_not_available_present` (boolean)
- `model_output_not_available_present` (boolean)
- `campaign_intelligence_not_available_present` (boolean)
- `judge_narrative_not_available_present` (boolean)
- `proof_does_not_equal_truth_present` (boolean)
- `gemini_label_does_not_equal_live_gemini_availability_present` (boolean)
- `model_output_does_not_equal_semantic_truth_present` (boolean)
- `judge_narrative_does_not_equal_legal_authenticity_present` (boolean)
- `campaign_intelligence_does_not_equal_campaign_performance_present` (boolean)
- `campaign_narrative_does_not_equal_marketing_effectiveness_present` (boolean)
- `local_campaign_intelligence_does_not_equal_live_gemini_availability_present`
  (boolean)
- `demo_golden_campaign_narrative_does_not_equal_production_security_present`
  (boolean)
- `no_model_output_truth_claim` (boolean)
- `no_semantic_truth_claim` (boolean)
- `no_legal_authenticity_claim` (boolean)
- `no_human_authorship_claim` (boolean)
- `no_c2pa_authenticity_claim` (boolean)
- `no_object_lock_claim` (boolean)
- `no_tamper_proof_claim` (boolean)
- `no_browser_side_b2_byte_verification_claim` (boolean)
- `no_live_b2_availability_claim` (boolean)
- `no_live_gemini_availability_claim` (boolean)
- `no_production_security_claim` (boolean)
- `no_production_compliance_claim` (boolean)
- `no_legal_review_claim` (boolean)
- `no_chain_of_custody_guarantee_claim` (boolean)
- `no_campaign_performance_prediction_claim` (boolean)
- `no_marketing_effectiveness_proof_claim` (boolean)
- `no_business_outcome_guarantee_claim` (boolean)
- `no_conversion_lift_claim` (boolean)
- `no_revenue_impact_claim` (boolean)
- `no_audience_targeting_accuracy_claim` (boolean)
- `no_ad_compliance_approval_claim` (boolean)
- `no_identity_verification_claim` (boolean)
- `no_biometric_identification_claim` (boolean)
- `no_deepfake_detection_claim` (boolean)
- `no_content_moderation_claim` (boolean)
- `no_ocr_correctness_claim` (boolean)
- `no_transcript_correctness_claim` (boolean)
- `no_timestamp_correctness_claim` (boolean)
- `no_voice_authenticity_claim` (boolean)
- `no_speaker_identity_claim` (boolean)
- `no_emotion_truth_claim` (boolean)
- `no_gemini_api_calls` (boolean)
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

PS-037d ships one feature smoke:
`scripts/ps037d_gemini_campaign_intelligence_judge_narrative_smoke.py`.

The PS-037d feature smoke must:

- validate only the PS-037d slice (no recursive smokes; must never launch
  another feature smoke as a subprocess; must never call the central regression
  gate)
- read checked-in prior evidence and accepted data modules as immutable inputs
- write only its own evidence file
  `docs/evidence/ps-037d/gemini-campaign-intelligence-judge-narrative-report.json`,
  and only when `--write-evidence` is explicit
- never call Gemini (no Gemini API calls)
- never call any model (no live model calls)
- never call any provider (no provider calls)
- never read arbitrary B2 objects (no live B2 reads)
- never write B2 (no B2 writes)
- never perform broad B2 scans
- never run the frontend typecheck / build (that belongs to the central gate)
- reuse `scripts/smoke_lib.py` for shared validation logic
- validate the shared `CampaignIntelligenceJudgeNarrativeLayer` component is
  present
- validate the shared `geminiCampaignIntelligence.ts` data module is present
- validate the campaign intelligence / judge narrative layer is rendered on the
  required proof surfaces that are present in this repo (section 10.3)
- validate the layer integrates / cross-references the PS-037 Trust Boundary
  (`trust_boundary_cross_reference_present`)
- validate the layer integrates / cross-references the PS-037a Multimodal Proof
  Layer (`multimodal_proof_cross_reference_present`)
- validate the layer integrates / cross-references the PS-037b Transcript/
  Timestamp Evidence layer (`transcript_timestamp_cross_reference_present`)
- validate the layer integrates / cross-references the PS-037c Voice/Audio
  Evidence Provider Choice layer (`voice_audio_evidence_cross_reference_present`)
- validate the required campaign intelligence / judge narrative UI strings
  (section 21) are present
- validate the required negative boundary strings (section 21) are present
- validate the deferred / unavailable / not-claimed states (section 10.6) are
  present and honest
- validate no Gemini API calls are introduced
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
  the PS-037d changed files, without the smoke or this spec reproducing that
  literal
- validate prior evidence is unchanged
- validate `git diff --check` is clean
- do not scan smoke guard fixtures as product claims (the future PS-037d smoke
  and its evidence report are the source of truth for slice overclaim
  validation; smoke guard fixtures are not product claims)

The PS-037d feature smoke must support these standard flags:

- `--check-only` (default: non-mutating local validation; no evidence file is
  written)
- `--write-evidence` (write only `docs/evidence/ps-037d/` evidence)
- `--no-frontend`

Default PS-037d smoke behavior is non-mutating local validation
(`--check-only`).

The smoke must not contain the bad lowercase-only hidden-flag marker check and
must not rely on a lowercase-only marker check. The hidden-Git-flags check must
be the explicit `h` / `S` checker over `git ls-files -v`, and must record
`no_hidden_git_flags_h` and `no_hidden_git_flags_S` as separate booleans.

PS-037d smoke performs no Gemini API calls, no provider calls, no live B2
reads, no B2 writes, and no broad B2 scans.

The PS-037d smoke must not create duplicate context-blind overclaim scanners.
The smoke and its evidence report are the source of truth for PS-037d overclaim
validation. The smoke must not scan smoke guard fixtures as product claims.

## 15. Regression Gate Contract

The central regression gate remains the single cross-slice release-readiness
gate and is non-mutating by default. PS-037d does not own or modify the central
gate.

Normal future PS-037d release validation command:

```
python scripts/proofstudio_regression_gate.py --current ps037d --frontend --report-out /tmp/proofstudio-release-report.json
```

Contract-only gate (no frontend):

```
python scripts/proofstudio_regression_gate.py --current ps037d --no-frontend --report-out /tmp/proofstudio-ps037d-regression-report.json
```

- The gate runs `npm run typecheck` and `npm run build` in `apps/web` exactly
  once per invocation, and only when `--frontend` is passed. PS-037d feature
  smoke must never trigger nested frontend builds.
- The gate must not write the canonical PS-034A report. `--write-report` is
  rejected for `--current ps037d` (PS-035C accepted behavior; only PS-034A may
  regenerate the canonical report).
- Running the gate for `ps037d` must leave all prior-slice evidence unchanged,
  including the PS-037, PS-037a, PS-037b, and PS-037c evidence.
- No recursive smokes: the gate never executes a feature smoke.

Canonical PS-034A regeneration (unchanged, owned by PS-034A only):

```
python scripts/proofstudio_regression_gate.py --current ps034a --write-report
```

## 16. Truth Boundary

ProofStudio proves what the pipeline recorded. The Gemini Campaign Intelligence
/ Judge Narrative layer is a narrative-over-recorded-proof surface that makes
the recorded campaign evidence explicit and consistent on every core proof
surface. It is not a legal authenticity system, not a live B2 verifier, not a
truth system, not a semantic-truth system, not a model-output-truth system, not
a live Gemini verifier, not a live model system, not a campaign performance
predictor, not a marketing effectiveness scorer, not a business outcome
forecaster, not a conversion / revenue / audience / ad-compliance engine, not
an identity system, not a biometric system, not a deepfake detector, not a
content moderator, not an OCR verifier, not a transcript verifier, not a
timestamp verifier, not a voice-authenticity system, not a speaker-identity
system, and not an emotion-truth system.

The layer must preserve these truth-boundary red lines verbatim across the
spec, the UI, and any evidence report:

- do not claim model output truth
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
- do not claim live Gemini availability unless a live Gemini check is
  explicitly implemented and approved with cost controls, env gates, and
  evidence boundaries
- do not claim public deployment verification unless deployed and tested
- do not claim enterprise security
- do not claim production security
- do not claim production compliance
- do not claim legal review
- do not claim chain-of-custody guarantees beyond recorded pipeline evidence
- do not claim campaign performance prediction
- do not claim marketing effectiveness proof
- do not claim business outcome guarantee
- do not claim conversion lift
- do not claim revenue impact
- do not claim audience targeting accuracy
- do not claim ad compliance approval
- do not claim identity verification
- do not claim biometric identification
- do not claim deepfake detection
- do not claim content moderation
- do not claim OCR correctness
- do not claim transcript correctness
- do not claim timestamp correctness
- do not claim voice authenticity
- do not claim speaker identity
- do not claim emotion truth
- do not claim actual spend / latency / quota unless captured
- do not claim provider failures / reruns / variants unless evidenced

PS-037d does not prove model output truth, semantic truth, product correctness,
production security, production compliance, B2 immutability, Object Lock,
tamper-proof storage, browser-side B2 byte verification, live B2 availability,
live Gemini availability, real billing API integration, billing behavior, CI
enforcement, legal review, identity, biometric identity, deepfake absence,
content-policy compliance, OCR correctness, transcript correctness, timestamp
correctness, voice authenticity, speaker identity, emotion truth, campaign
performance, marketing effectiveness, business outcome, conversion lift,
revenue impact, audience targeting accuracy, ad compliance approval, or
deployment readiness. No PS-037d artifact may imply any of these. The campaign
intelligence / judge narrative layer states what the pipeline already recorded;
it does not re-fetch, re-hash, or re-verify live B2 bytes, it does not call
Gemini, it does not call any model, and it does not call any provider.

## 17. Later-slice Boundaries

PS-037d must not implement, fake, or claim the later provider-specific slices
or out-of-scope capabilities. The boundaries are:

- live Gemini campaign intelligence generation — out of scope for PS-037d.
  PS-037d names Gemini as a campaign intelligence / judge narrative provider
  label for evidence labeling only. A live Gemini path may only be enabled by a
  later PM-approved slice with cost controls, env gates, and evidence
  boundaries. PS-037d must only reserve an honest "Gemini evidence not
  available" / "model output not available" state.
- live model generation — out of scope for PS-037d. PS-037d must only reserve
  an honest "model output not available" state.
- campaign performance prediction — out of scope. PS-037d must only reserve an
  honest "campaign performance prediction not claimed" state.
- marketing effectiveness proof — out of scope. PS-037d must only reserve an
  honest "marketing effectiveness proof not claimed" state.
- business outcome forecasting — out of scope. PS-037d must only reserve an
  honest "business outcome guarantee not claimed" state.
- conversion lift — out of scope. PS-037d must only reserve an honest
  "conversion lift not claimed" state.
- revenue impact — out of scope. PS-037d must only reserve an honest "revenue
  impact not claimed" state.
- audience targeting accuracy — out of scope. PS-037d must only reserve an
  honest "audience targeting accuracy not claimed" state.
- ad compliance approval — out of scope. PS-037d must only reserve an honest
  "ad compliance approval not claimed" state.
- model output truth — out of scope. PS-037d must only reserve an honest "model
  output truth not claimed" state.
- semantic truth verification — out of scope. PS-037d must not claim it.
- legal authenticity — out of scope. PS-037d must only reserve an honest "legal
  authenticity not claimed" state.
- legal review — out of scope. PS-037d must not claim it.
- identity verification / biometric identification / deepfake detection /
  content moderation / OCR correctness / transcript correctness / timestamp
  correctness / voice authenticity / speaker identity / emotion truth — out of
  scope. PS-037d must only reserve honest "not claimed" states for these.

PS-037d may reserve fields and honest "not available yet" / "not claimed" /
"unknown" states for those later-slice / out-of-scope areas, but must not fake
campaign intelligence outputs, judge narratives, model outputs, campaign
performance numbers, marketing effectiveness scores, business outcome
forecasts, conversion lift, revenue impact figures, audience targeting
accuracies, ad compliance approvals, or any provider output.

## 18. Risks

PS-037d must record the following risks with mitigations:

- overclaim risk
  - risk: a reviewer misreads the campaign intelligence / judge narrative layer
    or its copy as a forbidden overclaim — i.e. as claiming model output truth,
    semantic truth, legal authenticity, human authorship, C2PA authenticity,
    Object Lock / tamper-proof storage, browser-side B2 byte verification, live
    B2 availability, live Gemini availability, production security, production
    compliance, legal review, chain-of-custody guarantees beyond recorded
    pipeline evidence, campaign performance prediction, marketing effectiveness
    proof, business outcome guarantee, conversion lift, revenue impact,
    audience targeting accuracy, ad compliance approval, identity verification,
    biometric identification, deepfake detection, content moderation, OCR
    correctness, transcript correctness, timestamp correctness, voice
    authenticity, speaker identity, or emotion truth. ProofStudio does not
    claim any of these.
  - mitigation: the persistent campaign-intelligence / judge-narrative boundary
    statement (section 11) is mandatory; the truth-boundary red lines (section
    16) are preserved verbatim; the de-escalation pairs (section 10.7) and
    negative boundary strings (section 10.8) are surfaced verbatim; the
    evidence report carries `no_forbidden_overclaims`.
- Gemini-label overclaim risk
  - risk: the Gemini provider label is misread as a live Gemini call, live
    Gemini availability, live model availability, a model generation guarantee,
    or a correctness guarantee. Naming Gemini is misread as live Gemini
    availability.
  - mitigation: the Gemini-label honesty (sections 10.1, 10.4) is mandatory;
    the Gemini label does not equal live Gemini availability; the default
    posture is local/demo evidence with `live provider evidence not available`,
    `Gemini evidence not available`, and `model output not available`; the
    evidence report carries `no_gemini_api_calls`, `no_provider_calls`, and
    `no_live_gemini_availability_claim`; no live Gemini path exists in PS-037d.
- campaign-word overclaim risk
  - risk: a campaign word is misread as a campaign performance claim, a
    marketing effectiveness claim, a business outcome claim, a conversion /
    revenue / audience / ad-compliance claim, or a model output truth claim.
  - mitigation: the de-escalation pairs in section 10.7 are surfaced verbatim
    (campaign intelligence does not equal campaign performance; a campaign
    narrative does not equal marketing effectiveness); the negative boundary
    strings in section 10.8 are surfaced verbatim.
- faking-model-output risk
  - risk: a model output reference, a model output digest, a campaign
    intelligence output, a judge narrative, a campaign performance number, a
    marketing effectiveness score, a business outcome forecast, a conversion
    lift, a revenue impact figure, an audience targeting accuracy, or an ad
    compliance approval is silently represented as present when it is not, or is
    silently omitted so it looks hidden.
  - mitigation: the unavailable / not-claimed states (section 10.6) are
    surfaced verbatim and honestly; the model output honesty (section 10.5) is
    mandatory; the smoke validates their presence; PS-037d never produces those
    outputs unless they exist in accepted data.
- de-escalation-gap risk
  - risk: a judge mistakes a Gemini label for live Gemini availability, a model
    output reference for semantic truth, a judge narrative for legal
    authenticity, campaign intelligence for campaign performance, a campaign
    narrative for marketing effectiveness, local campaign intelligence for live
    Gemini availability, or demo/golden campaign narrative for production
    security.
  - mitigation: the de-escalation pairs in section 10.7 are surfaced verbatim.
- PS-037 / PS-037a / PS-037b / PS-037c weakening risk
  - risk: the campaign intelligence / judge narrative layer duplicates,
    contradicts, weakens, or removes the PS-037 Disclosure + Trust Boundary
    Layer, the PS-037a Multimodal Proof Layer (including its deferred campaign
    intelligence state), the PS-037b Transcript/Timestamp Evidence layer, or the
    PS-037c Voice/Audio Evidence Provider Choice layer.
  - mitigation: the campaign intelligence / judge narrative layer renders
    alongside `TrustBoundaryLayer`, `MultimodalProofLayer`,
    `TranscriptTimestampEvidenceLayer`, and `VoiceAudioEvidenceChoiceLayer`,
    reuses the shared disclosure concepts, fills the PS-037a deferred
    reservation, cross-references PS-037b and PS-037c, and never contradicts the
    PS-037 boundary or removes the PS-037a deferred state or the PS-037b /
    PS-037c contracts; PS-037d does not edit the PS-037, PS-037a, PS-037b, or
    PS-037c contract files except additively (section 9).
- live-B2-read risk
  - risk: the layer triggers a live B2 read or a broad B2 scan.
  - mitigation: the layer is purely client-side over accepted data; the smoke
    enforces `no_live_b2_reads`, `no_b2_writes`, `no_broad_b2_scans`.
- evidence-mutation risk
  - risk: the PS-037d smoke or the central gate run overwrites prior-slice
    evidence, including PS-037, PS-037a, PS-037b, and PS-037c evidence.
  - mitigation: PS-037d writes only `docs/evidence/ps-037d/`; the gate is
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
  - risk: PS-037d expands into live Gemini behavior, a live model integration,
    live model generation, campaign performance prediction, marketing
    effectiveness scoring, business outcome forecasting, conversion lift,
    revenue impact, audience targeting, ad compliance review, model output truth,
    semantic truth verification, legal review, identity verification,
    biometric identification, deepfake detection, content moderation, OCR
    correctness, transcript correctness, timestamp correctness, voice
    authenticity, speaker identity, emotion truth, CI, billing, deployment,
    auth, teams, permissions, a full enterprise DAM, a new backend, or a live B2
    fetcher.
  - mitigation: section 7 lists these as non-goals; section 9 forbids the
    relevant paths; section 17 fixes the later-slice / out-of-scope boundaries.
- recursive-smoke risk
  - risk: the PS-037d smoke launches another feature smoke or calls the central
    gate.
  - mitigation: the smoke must never launch another feature smoke as a
    subprocess and must never call the central regression gate; the central
    gate is the only cross-slice validator.
- duplicate-scanner risk
  - risk: PS-037d adds duplicate context-blind overclaim scanners in chat/spec
    guidance that treat smoke guard fixtures as product claims.
  - mitigation: PS-037d does not create duplicate context-blind overclaim
    scanners; the PS-037d smoke and its evidence report are the source of truth
    for slice overclaim validation; smoke guard fixtures are not scanned as
    product claims.

## 19. Acceptance Criteria

PS-037d (spec-only phase) is accepted only when:

- this spec exists at
  `specs/58-ps-037d-gemini-campaign-intelligence-judge-narrative.md`
- only this spec file is changed in the spec-only phase
- the branch `ps-037d/gemini-campaign-intelligence-judge-narrative` starts from
  `origin/accepted/proofstudio` at commit
  `d766c5d6e3dcb227f65cc42303fae8bb4d4c72f8` (the merge-base equals that
  commit)
- the product scope is clear and owns the campaign intelligence / judge
  narrative layer only; it does not expand into CI, billing, deployment, Gemini
  API calls, model calls, provider calls, live B2 reads, B2 writes, broad B2
  scans, live model generation, campaign performance prediction, marketing
  effectiveness proof, business outcome forecasting, conversion lift, revenue
  impact, audience targeting accuracy, ad compliance approval, model output
  truth, semantic truth verification, legal authenticity, legal review,
  identity verification, biometric identification, deepfake detection, content
  moderation, OCR correctness, transcript correctness, timestamp correctness,
  voice authenticity, speaker identity, or emotion truth
- the required campaign-intelligence / judge-narrative concepts (section 10.2)
  and the required surfaces (section 10.3) are specified
- the unavailable / not-claimed states (section 10.6), the de-escalation pairs
  (section 10.7), and the negative boundary strings (section 10.8) are
  specified verbatim
- the UI / UX contract (section 11) and the persistent campaign-intelligence /
  judge-narrative boundary statement are specified
- the data contract (section 12) reuses accepted checked-in evidence as
  read-only inputs and surfaces honest unavailable / not-claimed / unknown
  states where no evidence exists
- the truth boundary (section 16) is explicit and the boundary copy is
  specified
- the later-slice boundaries (section 17) are fixed
- the implementation candidate files (section 8) are listed, but no
  implementation is done in this phase
- the validation plan uses the PS-037d feature smoke plus the central
  regression gate (sections 14 and 15)
- no evidence mutation occurs in this phase
- no hidden Git flags `h` or `S` are present (verified by the explicit h/S
  checker over `git ls-files -v`)
- `git diff --check` is clean
- no staging, commit, or push occurs until PM approval
- `AGENTS.md`, `specs/07-master-spec-plan.md`, and
  `specs/08-roadmap-slices.md` are not changed in this phase

Implementation-phase acceptance (for reference, not this phase) additionally
requires: the shared `CampaignIntelligenceJudgeNarrativeLayer` component +
`geminiCampaignIntelligence.ts` data module exist; the campaign intelligence /
judge narrative layer is rendered on the required surfaces present in this repo
(section 10.3); the layer integrates / cross-references the PS-037a Multimodal
Proof Layer, the PS-037b Transcript/Timestamp Evidence layer, and the PS-037c
Voice/Audio Evidence Provider Choice layer and preserves the PS-037
TrustBoundaryLayer; the required campaign-intelligence / judge-narrative
concepts, unavailable / not-claimed states, de-escalation pairs, and negative
boundary strings are present; the PS-037d smoke passes in `--check-only`
(default) and writes only `docs/evidence/ps-037d/**` under `--write-evidence`;
the central gate passes for `--current ps037d`; no Gemini API call, no model
call, no provider call, no live B2 read, no B2 write, no broad B2 scan occurs;
prior evidence is unchanged, including PS-037, PS-037a, PS-037b, and PS-037c
evidence; no forbidden overclaim is introduced; the PS-037 disclosure boundary,
the PS-037a multimodal proof contract, the PS-037b transcript/timestamp
contract, and the PS-037c voice/audio evidence provider choice contract are not
weakened.

## 20. Rollback

Rollback of the PS-037d spec-only phase is a single revert of this spec commit,
because only
`specs/58-ps-037d-gemini-campaign-intelligence-judge-narrative.md` is changed in
this phase.

Future implementation rollback must restore the pre-PS-037d state of the edited
files in section 8. Specifically:

- remove `apps/web/src/geminiCampaignIntelligence.ts`
- remove `apps/web/src/CampaignIntelligenceJudgeNarrativeLayer.tsx`
- revert the additive campaign-intelligence-judge-narrative renders in
  `apps/web/src/JudgeCockpitHome.tsx`,
  `apps/web/src/B2EvidenceExplorer.tsx`,
  `apps/web/src/B2RehydrateComparison.tsx`,
  `apps/web/src/ManifestVerificationPanel.tsx`,
  `apps/web/src/B2AuditVault.tsx`,
  `apps/web/src/ReviewApprovalWorkspace.tsx`,
  `apps/web/src/JudgeEvidencePack.tsx`,
  `apps/web/src/PublicPassportPage.tsx`, and
  `apps/web/src/App.tsx` to pre-PS-037d state
- revert the additive campaign-intelligence-judge-narrative classes in
  `apps/web/src/styles.css` to pre-PS-037d state
- remove `scripts/ps037d_gemini_campaign_intelligence_judge_narrative_smoke.py`
- remove `docs/ps-037d-gemini-campaign-intelligence-judge-narrative-proof.md`
- remove `docs/evidence/ps-037d/` if it was added
- revert the additive cross-references in `specs/07-master-spec-plan.md`,
  `specs/08-roadmap-slices.md`, and
  `docs/validation/proofstudio-smoke-harness-v1.md` to pre-PS-037d state

Rollback of PS-037d must not touch any evidence under `docs/evidence/**` other
than `docs/evidence/ps-037d/`, must not touch the central gate
(`scripts/proofstudio_regression_gate.py`), `scripts/smoke_lib.py`,
`AGENTS.md`, `.env*`, `render.yaml`, requirements files, any provider wrapper,
any Gemini client, any model client, any B2 storage path, the PS-037 disclosure
contract, the PS-037a multimodal proof contract, the PS-037b transcript/
timestamp contract, or the PS-037c voice/audio evidence provider choice
contract. Rollback is isolated and reversible because PS-037d is a
self-contained campaign intelligence / judge narrative layer over existing
accepted data; it does not change provider behavior, Gemini behavior, model
behavior, B2 behavior, billing behavior, deployment topology, the PS-037
boundary, the PS-037a contract, the PS-037b contract, or the PS-037c contract.

## 21. Verbatim implementation/audit contract strings

The PS-037d implementation, the Gemini Campaign Intelligence / Judge Narrative
layer UI, the PS-037d smoke, and the PS-037d evidence report must preserve the
following exact strings so the campaign-intelligence / judge-narrative contract
is deterministic and auditable. Any future PM audit must check these exact
strings; do not rely on close-enough wording. No surprise audit checks: any
exact string a future PM audit should check is listed here.

The required identity / positioning strings are:

- PS-037d
- Gemini Campaign Intelligence / Judge Narrative

The required concept strings are:

- campaign intelligence
- judge narrative
- campaign proof narrative
- campaign evidence summary
- Gemini
- Gemini provider label

The required model-output / evidence-record strings are:

- model output reference
- model output digest
- model output status

The required status / boundary concept strings are:

- campaign intelligence status
- judge narrative status
- narrative source evidence
- narrative source evidence references
- proof stack summary
- B2 evidence cross-reference
- manifest evidence cross-reference
- rehydrate evidence cross-reference
- trust boundary cross-reference
- multimodal proof cross-reference
- transcript/timestamp cross-reference
- voice/audio evidence cross-reference
- provider activity status
- local verification
- live verification status
- disclosure boundary
- not claimed
- unknown
- local/demo evidence

The required honest unavailable / not-claimed state strings are:

- live provider evidence not available
- Gemini evidence not available
- model output not available
- campaign intelligence not available
- judge narrative not available

The required de-escalation-pair strings are:

- proof does not equal truth
- Gemini label does not equal live Gemini availability
- model output does not equal semantic truth
- judge narrative does not equal legal authenticity
- campaign intelligence does not equal campaign performance
- campaign narrative does not equal marketing effectiveness
- local campaign intelligence does not equal live Gemini availability
- demo/golden campaign narrative does not equal production security

The required negative-boundary strings are:

- not model output truth
- not semantic truth
- not legal authenticity
- not human authorship
- not C2PA authenticity
- not Object Lock
- not tamper-proof
- not browser-side B2 byte verification
- not live B2 availability
- not live Gemini availability
- not production security
- not production compliance
- not legal review
- not chain-of-custody guarantee
- not campaign performance prediction
- not marketing effectiveness proof
- not business outcome guarantee
- not conversion lift
- not revenue impact
- not audience targeting accuracy
- not ad compliance approval
- not identity verification
- not biometric identification
- not deepfake detection
- not content moderation
- not OCR correctness
- not transcript correctness
- not timestamp correctness
- not voice authenticity
- not speaker identity
- not emotion truth

The required posture / boundary strings are:

- no Gemini API calls
- no provider calls
- no live B2 reads
- no B2 writes
- no broad B2 scans
- no recursive smokes
- hidden Git flags h
- line[0]

The required evidence-report boolean keys are:

- `ok`
- `slice_id: ps037d`
- `campaign_intelligence_component_present`
- `campaign_intelligence_data_module_present`
- `campaign_intelligence_layer_present`
- `required_surfaces_have_campaign_intelligence_layer`
- `trust_boundary_cross_reference_present`
- `multimodal_proof_cross_reference_present`
- `transcript_timestamp_cross_reference_present`
- `voice_audio_evidence_cross_reference_present`
- `gemini_label_present`
- `campaign_intelligence_present`
- `judge_narrative_present`
- `campaign_proof_narrative_present`
- `campaign_evidence_summary_present`
- `gemini_provider_label_present`
- `model_output_reference_present_or_honestly_unavailable`
- `model_output_digest_present_or_honestly_unavailable`
- `model_output_status_present`
- `campaign_intelligence_status_present`
- `judge_narrative_status_present`
- `narrative_source_evidence_present`
- `narrative_source_evidence_references_present`
- `proof_stack_summary_present`
- `b2_evidence_cross_reference_present`
- `manifest_evidence_cross_reference_present`
- `rehydrate_evidence_cross_reference_present`
- `provider_activity_status_present`
- `local_verification_status_present`
- `live_verification_status_present`
- `disclosure_boundary_present`
- `not_claimed_status_present`
- `unknown_status_present`
- `local_demo_evidence_present`
- `live_provider_evidence_not_available_present`
- `gemini_evidence_not_available_present`
- `model_output_not_available_present`
- `campaign_intelligence_not_available_present`
- `judge_narrative_not_available_present`
- `proof_does_not_equal_truth_present`
- `gemini_label_does_not_equal_live_gemini_availability_present`
- `model_output_does_not_equal_semantic_truth_present`
- `judge_narrative_does_not_equal_legal_authenticity_present`
- `campaign_intelligence_does_not_equal_campaign_performance_present`
- `campaign_narrative_does_not_equal_marketing_effectiveness_present`
- `local_campaign_intelligence_does_not_equal_live_gemini_availability_present`
- `demo_golden_campaign_narrative_does_not_equal_production_security_present`
- `no_model_output_truth_claim`
- `no_semantic_truth_claim`
- `no_legal_authenticity_claim`
- `no_human_authorship_claim`
- `no_c2pa_authenticity_claim`
- `no_object_lock_claim`
- `no_tamper_proof_claim`
- `no_browser_side_b2_byte_verification_claim`
- `no_live_b2_availability_claim`
- `no_live_gemini_availability_claim`
- `no_production_security_claim`
- `no_production_compliance_claim`
- `no_legal_review_claim`
- `no_chain_of_custody_guarantee_claim`
- `no_campaign_performance_prediction_claim`
- `no_marketing_effectiveness_proof_claim`
- `no_business_outcome_guarantee_claim`
- `no_conversion_lift_claim`
- `no_revenue_impact_claim`
- `no_audience_targeting_accuracy_claim`
- `no_ad_compliance_approval_claim`
- `no_identity_verification_claim`
- `no_biometric_identification_claim`
- `no_deepfake_detection_claim`
- `no_content_moderation_claim`
- `no_ocr_correctness_claim`
- `no_transcript_correctness_claim`
- `no_timestamp_correctness_claim`
- `no_voice_authenticity_claim`
- `no_speaker_identity_claim`
- `no_emotion_truth_claim`
- `no_gemini_api_calls`
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

- `python scripts/proofstudio_regression_gate.py --current ps037d --frontend --report-out /tmp/proofstudio-release-report.json`
- `python scripts/proofstudio_regression_gate.py --current ps037d --no-frontend --report-out /tmp/proofstudio-ps037d-regression-report.json`
- `scripts/ps037d_gemini_campaign_intelligence_judge_narrative_smoke.py`
- `docs/evidence/ps-037d/gemini-campaign-intelligence-judge-narrative-report.json`
- `docs/ps-037d-gemini-campaign-intelligence-judge-narrative-proof.md`
