# PS-037c — Voice/Audio Evidence Provider Choice Layer

## 1. Status

PS-037c — Voice/Audio Evidence Provider Choice Layer is currently:

- Spec only.
- Implementation pending. No product code, frontend code, backend code,
  scripts, evidence, AGENTS.md, `.env*`, `render.yaml`, or requirements files
  are changed during this phase.

PS-037c must not be implemented, and no implementation files may be changed,
until this spec is accepted by the PM. The authoritative accepted base is the
dynamic Git ref `origin/accepted/proofstudio`, never a hardcoded commit hash.
At the time of this spec the ref resolves to commit
`6d51b1d3fc0db88ff6c9fdaf16161e3df9c706ad` (the post-PS-037b accepted state).
The ref is the authority; the commit hash is recorded for traceability only
and must not be treated as a hardcoded base.

This spec-only commit touches only this file:
`specs/57-ps-037c-voice-audio-evidence-provider-choice-layer.md`.

PS-037c must not call ElevenLabs, must not call Hume, must not call any live
provider, must not read or write live B2, must not perform broad B2 scans, must
not mutate any evidence, must not run the frontend, must not run the backend,
must not stage, commit, or push, and must not print secrets during this phase.
PS-037c obeys the root `AGENTS.md` operating law and the validation policy in
`docs/validation/proofstudio-smoke-harness-v1.md`.

## 2. Purpose

PS-037c defines a reusable Voice/Audio Evidence Provider Choice Layer that lets
ProofStudio expose a customer-selectable voice/audio evidence path while
preserving strict truth boundaries. The layer is provider-choice by design: it
is not ElevenLabs-only and not Hume-only. It supports two evidence tracks the
customer can choose between:

1. ElevenLabs Voiceover Artifact Evidence
2. Hume Emotion-Signal Evidence

PS-037a (Multimodal Proof Layer) already reserves honest "voice evidence not
available" and "emotion evidence not available" deferred states pointing at
PS-037c, but owns no voice/audio artifact and no provider choice. PS-037c
fills that reservation with a real, inspectable voice/audio evidence provider
choice layer that answers, in one consistent place, the basic voice/audio
evidence questions a reviewer or judge asks:

- which voice/audio evidence path is selected
- whether the selected path is ElevenLabs Voiceover Artifact Evidence
- whether the selected path is Hume Emotion-Signal Evidence
- whether voiceover artifact evidence exists
- whether emotion-signal evidence exists
- what audio artifact the evidence relates to
- what source media artifact the evidence relates to
- what provider is named for evidence labeling
- whether the evidence is local/demo/golden fixture evidence or live provider
  evidence
- where the audio artifact reference is recorded
- where the audio artifact digest is recorded
- where provider output reference/digest is recorded, if available
- whether provider activity happened
- whether B2 archive evidence exists for the audio artifact
- whether rehydrate evidence exists for the audio artifact
- whether transcript/timestamp evidence from PS-037b cross-references the
  audio artifact
- whether voice authenticity, speaker identity, biometric identity, emotion
  truth, psychological diagnosis, or health inference is claimed
- what ProofStudio proves and does not prove for voice/audio evidence

The layer is a voice/audio evidence-inspection layer over already-recorded or
honestly-unavailable data, not a new proof surface, not a new route, not a new
backend endpoint, not a live provider integration, and not a voice-generation
or emotion-inference system. It makes the existing voice/audio framing
consistent and judge-safe, and it states honestly what ProofStudio proves and
what ProofStudio does not prove for voice/audio evidence.

PS-037c proves what the pipeline recorded. The layer does not prove voice
authenticity, speaker identity, biometric identification, emotion truth,
psychological diagnosis, health inference, mental state diagnosis, semantic
truth, legal authenticity, C2PA authenticity, human authorship, Object Lock /
tamper-proof storage, browser-side B2 byte verification, live B2 availability,
live ElevenLabs availability, live Hume availability, production security,
production compliance, legal review, transcript correctness, timestamp
correctness, or chain-of-custody guarantees beyond recorded pipeline evidence.

## 3. Root Cause / Product Gap

PS-037a consolidated artifact evidence across modalities and explicitly
reserved honest "voice evidence not available" and "emotion evidence not
available" deferred states, pointing the deferred ownership at PS-037c.
PS-037b added an AssemblyAI Transcript/Timestamp Evidence layer that
cross-references PS-037a and that may reference a media/audio artifact.
Those reservations are honest, but they are only placeholders. No slice yet
makes voice/audio evidence inspectable as a customer-selectable provider
choice: there is no single place where a reviewer can read which voice/audio
evidence path is selected, whether the selected path is ElevenLabs Voiceover
Artifact Evidence or Hume Emotion-Signal Evidence, what audio artifact the
evidence relates to, what source media artifact it relates to, what provider
is named for evidence labeling, where the audio artifact reference and digest
are recorded, where provider output reference/digest is recorded (if
available), whether provider activity happened, and whether B2 / rehydrate
evidence exists for the audio artifact.

The gap this creates is judge-safety at the voice/audio boundary, compounded by
the risk of provider-name overclaim. Today:

- `apps/web/src/multimodalProof.ts` (PS-037a) reserves honest "voice evidence
  not available" and "emotion evidence not available" deferred states, but
  PS-037a owns no voice/audio artifact, no provider choice, no voiceover
  artifact reference, no emotion-signal reference, and no audio artifact
  digest. It cannot answer "which voice/audio evidence path is selected"; it
  can only say "none yet."
- `apps/web/src/assemblyAITranscriptEvidence.ts` (PS-037b) cross-references a
  media/audio artifact for transcript/timestamp evidence, but PS-037b owns no
  voice/audio provider choice and no voiceover / emotion-signal evidence.
- no accepted slice records a voice/audio provider choice, a selected
  voice/audio evidence path, a voiceover artifact reference, an emotion-signal
  reference, an audio artifact digest, a provider output reference/digest, or a
  source media artifact reference in a single inspectable place.
- a judge reading a proof surface today cannot tell whether voice/audio
  evidence is genuinely absent, deferred, locally recorded, provider-labeled,
  or simply not surfaced. An absent voiceover that is silently omitted looks
  like a hidden voiceover; a provider name (ElevenLabs or Hume) that appears
  without a clear disclosure boundary looks like a live provider call or a
  correctness claim.

PS-037c closes that gap by adding one shared voice/audio evidence provider
choice layer — a canonical data module plus a shared component — that the core
proof surfaces render additively. The layer reads only accepted local /
golden / demo evidence, or exposes explicit honest "not available" / "not
claimed" / "unknown" states. It does not invent a voiceover, an emotion
signal, a voice analysis, an emotion analysis, or any provider output that is
not in accepted data. It is local / static by default: it adds no ElevenLabs
API calls, no Hume API calls, no provider calls, no live B2 reads, no B2
writes, no broad B2 scans, no new backend, no new env, no new paid service
dependency, and no deployment changes.

ElevenLabs and Hume are named as selectable evidence providers for evidence
labeling only. The implementation must default to local/static behavior. No
live ElevenLabs API call and no live Hume API call may occur unless a later
PM-approved slice explicitly enables a live-provider path with cost controls,
env gates, and evidence boundaries.

## 4. User Story

As a reviewer (designer, marketer, reviewer, client, or judge), I want one
honest, consistent voice/audio evidence provider choice view, so that on any
core proof surface I can immediately read: which voice/audio evidence path is
selected; whether the selected path is ElevenLabs Voiceover Artifact Evidence
or Hume Emotion-Signal Evidence; whether voiceover artifact evidence exists;
whether emotion-signal evidence exists; what audio artifact the evidence
relates to; what source media artifact the evidence relates to; what provider
is named for voice/audio evidence labeling (ElevenLabs or Hume); whether the
evidence is local / demo / golden fixture evidence or live provider evidence;
where the audio artifact reference is recorded; where the audio artifact digest
is recorded; where provider output reference/digest is recorded, if available;
whether provider activity happened; whether B2 archive evidence exists for the
audio artifact; whether rehydrate evidence exists for the audio artifact;
whether transcript/timestamp evidence from PS-037b cross-references the audio
artifact; whether voice authenticity, speaker identity, biometric identity,
emotion truth, psychological diagnosis, or health inference is claimed — and so
I never mistake a provider choice for provider availability, a voiceover
artifact reference for legal authenticity, an audio artifact for voice
authenticity, a provider voice output for speaker identity, an emotion signal
for emotion truth, local voice/audio evidence for live ElevenLabs availability,
local voice/audio evidence for live Hume availability, or demo/golden
voice/audio evidence for production security.

As a customer, I want to choose which voice/audio evidence path fits my use
case — ElevenLabs Voiceover Artifact Evidence or Hume Emotion-Signal Evidence
— and have that choice surfaced honestly alongside what each path proves, what
each path does not prove, and what is honestly not available yet.

As a demo presenter, I want a reusable voice/audio evidence provider choice
layer that is useful in a three-minute hackathon demo: a compact summary that
lists the selected path, the two evidence tracks, the recorded voice/audio
evidence and its honest "not available" / "not claimed" / "unknown" states,
plus an expanded panel that states, verbatim, what voice/audio evidence proves,
what it does not prove, what is unavailable, what is not claimed, and what the
shared disclosure boundary is — all working offline from accepted local /
golden / demo fixtures, with no ElevenLabs API calls, no Hume API calls, no
provider calls, no live B2 reads, no B2 writes, and no broad B2 scans.

## 5. Current Accepted Base

The current accepted base for PS-037c is:

- branch: `accepted/proofstudio`
- ref: `origin/accepted/proofstudio` (the authoritative source of truth; the
  ref is the authority, not any hardcoded commit hash)
- commit the ref resolves to at the time of this spec:
  `6d51b1d3fc0db88ff6c9fdaf16161e3df9c706ad`
- this is the post-PS-037b accepted state: the Disclosure + Trust Boundary
  Layer from PS-037 is in place (`apps/web/src/trustBoundary.ts` +
  `apps/web/src/TrustBoundaryLayer.tsx`); the Multimodal Proof Layer from
  PS-037a is in place (`apps/web/src/multimodalProof.ts` +
  `apps/web/src/MultimodalProofLayer.tsx`), and PS-037a reserves honest "voice
  evidence not available" and "emotion evidence not available" deferred states
  pointing at PS-037c; the AssemblyAI Transcript/Timestamp Evidence layer from
  PS-037b is in place (`apps/web/src/assemblyAITranscriptEvidence.ts` +
  `apps/web/src/TranscriptTimestampEvidenceLayer.tsx`); the Archive / Rehydrate
  / B2 Audit Vault is in place from PS-036; the Review + Approval Workspace is
  in place from PS-035; the root `AGENTS.md` operating law is in place
  (PS-035D); the accepted-base-pointer-drift guard is in place (PS-035E); the
  central regression gate is non-mutating by default from PS-035C; the
  golden-fixture digest freeze is in place from PS-035B; the golden-run
  manifest carries a real non-null `manifest_uri` and a real 64-hex
  `manifest_hash` from PS-035A.

PS-037c must start from `origin/accepted/proofstudio`, not from `main`.

Relevant accepted facts at this base that PS-037c builds on (PS-037c must not
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
  core proof surfaces; PS-037c integrates with it and does not weaken it
- the PS-037a Multimodal Proof Layer exists and is rendered on the core proof
  surfaces; PS-037a reserves honest "voice evidence not available" and
  "emotion evidence not available" deferred states pointing at PS-037c;
  PS-037c integrates with / fills the reservation PS-037a made and does not
  weaken it or remove its deferred states
- the PS-037b AssemblyAI Transcript/Timestamp Evidence layer exists and is
  rendered on the core proof surfaces; PS-037b cross-references a media/audio
  artifact; PS-037c cross-references PS-037b so a reviewer can read whether
  transcript/timestamp evidence cross-references the audio artifact, and does
  not weaken the PS-037b layer
- the existing shared component classes (`.trust-boundary`,
  `.trust-boundary-layer*`, the multimodal proof layer classes, the
  transcript/timestamp evidence layer classes, pills, cards, `JsonExpander`)
  already exist in `apps/web/src/styles.css`

## 6. Scope

PS-037c is a product slice. It adds a reusable Voice/Audio Evidence Provider
Choice Layer (a shared data module plus a shared component) and renders it
additively on the core proof surfaces. It is local / static by default: it must
work without ElevenLabs API calls, without Hume API calls, without live
provider calls, without live B2 reads, without B2 writes, and without broad B2
scans, by reading accepted local / golden / demo fixtures and existing accepted
data modules, or by surfacing explicit honest "not available" / "not claimed" /
"unknown" states.

PS-037c owns the voice/audio evidence provider choice layer only. It must:

1. Add a shared, canonical voice/audio evidence provider choice data module
   (`apps/web/src/voiceAudioEvidenceChoice.ts`, or the project's accepted
   equivalent) that exposes one consistent set of voice/audio evidence
   provider choice concepts, the two evidence tracks (ElevenLabs Voiceover
   Artifact Evidence and Hume Emotion-Signal Evidence), the provider choice
   and selected path, audio artifact evidence, honest "not available" / "not
   claimed" / "unknown" states, and deferred later-slice states for every core
   proof surface.
2. Add a shared voice/audio evidence provider choice component
   (`apps/web/src/VoiceAudioEvidenceChoiceLayer.tsx`, or the project's accepted
   equivalent) that renders the layer, including an optional compact
   voice/audio provider-choice summary and an expanded voice/audio
   provider-choice panel pattern, reading only from
   `apps/web/src/voiceAudioEvidenceChoice.ts`.
3. Render the voice/audio evidence provider choice layer additively on the
   required core proof surfaces (section 10.3) that are present in this repo so
   the voice/audio provider-choice framing is consistent everywhere
   voice/audio evidence is shown.
4. State, for voice/audio evidence, "what ProofStudio proves" and "what
   ProofStudio does not prove."
5. Surface the canonical voice/audio provider-choice concepts (section 10.2):
   provider choice, selected voice/audio evidence path, ElevenLabs Voiceover
   Artifact Evidence, Hume Emotion-Signal Evidence, ElevenLabs, Hume,
   voiceover artifact evidence, emotion-signal evidence, audio artifact, audio
   artifact reference, audio artifact digest, provider output reference,
   provider output digest, source media artifact reference, source media
   artifact digest, voice/audio evidence status, voiceover status,
   emotion-signal status, provider activity status, B2 evidence status,
   rehydrate evidence status, local verification, live verification status,
   disclosure boundary, not claimed, unknown, local/demo evidence, and live
   provider evidence not available.
6. Surface the honest unavailable / not-claimed states (section 10.6) verbatim
   so no reviewer mistakes an absent voice/audio proof for a hidden proof, and
   no reviewer mistakes a provider name for a live provider call or a
   correctness claim.
7. Surface the canonical voice/audio provider-choice de-escalation pairs
   (section 10.7) verbatim so no judge mistakes a strong-sounding voiceover
   artifact or emotion signal for a stronger guarantee.
8. Surface the canonical voice/audio provider-choice negative boundary strings
   (section 10.8) verbatim.
9. Integrate with the PS-037 TrustBoundaryLayer (render alongside it; reuse the
   shared disclosure concepts; do not duplicate or weaken the PS-037 boundary).
10. Integrate / cross-reference with the PS-037a MultimodalProofLayer (render
    alongside it; fill the concrete voice/audio provider-choice evidence that
    PS-037a only reserved as deferred; do not duplicate or weaken the PS-037a
    layer or its deferred voice/emotion states).
11. Integrate / cross-reference with the PS-037b TranscriptTimestampEvidenceLayer
    (render alongside it; surface an honest transcript/timestamp cross-reference
    so a reviewer can read whether transcript/timestamp evidence from PS-037b
    cross-references the audio artifact; do not duplicate or weaken the PS-037b
    layer).
12. Preserve the existing per-surface artifact / boundary panels; the shared
    voice/audio provider-choice layer complements them. PS-037c must not delete
    or weaken any existing per-surface non-claim, per-surface artifact record,
    the PS-037 disclosure contract, the PS-037a multimodal proof contract, or
    the PS-037b transcript/timestamp contract.
13. Be demo-friendly and judge-friendly: useful in a three-minute demo, no
    generic AI hype copy, no unsupported claims, no faked voiceovers, no faked
    emotion signals, no faked voice analysis, no faked emotion analysis.
14. Work without ElevenLabs API calls, without Hume API calls, without provider
    calls, without live B2 reads, without B2 writes, and without broad B2
    scans, by using accepted local / golden / demo data or existing accepted
    data paths.
15. Not mutate any prior evidence. Any PS-037c-owned evidence lives only under
    `docs/evidence/ps-037c/`.
16. Not change the golden run canonical constants, the historical contracts the
    regression gate verifies, any provider / B2 behavior, the PS-037 disclosure
    contract, the PS-037a multimodal proof contract, or the PS-037b
    transcript/timestamp contract.

## 7. Non-goals

PS-037c must not:

- do not implement product code during the spec-only phase
- do not make any ElevenLabs API call
- do not make any Hume API call
- do not make any live provider call
- do not implement live ElevenLabs voice generation
- do not implement live Hume emotion inference
- do not implement voice clone authenticity
- do not implement the later or out-of-scope capabilities:
  - PS-037d Gemini Campaign Intelligence / Judge Narrative (PS-037c must not
    fake campaign intelligence; it may only reserve honest "campaign
    intelligence deferred to PS-037d" states)
  - voice authenticity proof, speaker identity proof, biometric identification,
    emotion truth, psychological diagnosis, mental state diagnosis, health
    inference, content moderation, deepfake detection, legal review, or
    semantic truth verification (PS-037c must only reserve honest "not claimed"
    states for these; it must not fake them)
- do not implement identity verification, biometric identification, speaker
  identity proof, voice authenticity proof, emotion truth, mental state
  diagnosis, psychological diagnosis, health inference, content moderation,
  deepfake detection, legal review, or semantic truth verification
- do not fake voiceovers, emotion signals, voice analyses, emotion analyses,
  voice clones, speaker identities, biometric identities, or any provider
  output that is not in accepted data
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
- do not claim voice authenticity
- do not claim speaker identity
- do not claim biometric identification
- do not claim emotion truth
- do not claim psychological diagnosis
- do not claim mental state diagnosis
- do not claim health inference
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
- do not claim live ElevenLabs availability unless a live ElevenLabs check is
  explicitly implemented and approved with cost controls, env gates, and
  evidence boundaries
- do not claim live Hume availability unless a live Hume check is explicitly
  implemented and approved with cost controls, env gates, and evidence
  boundaries
- do not claim production security
- do not claim production compliance
- do not claim legal review
- do not claim chain-of-custody guarantees beyond recorded pipeline evidence
- do not claim identity verification
- do not claim deepfake detection
- do not claim content moderation
- do not claim OCR correctness
- do not claim transcript correctness
- do not claim timestamp correctness
- do not claim model output truth
- do not delete or weaken any existing per-surface truth-boundary panel,
  non-claim, artifact record, the PS-037 disclosure contract, the PS-037a
  multimodal proof contract, or the PS-037b transcript/timestamp contract
- do not add a new backend, a new ElevenLabs client, a new Hume client, a new
  provider wrapper, a new B2 client, a new env variable, a new paid service
  dependency, or any deployment change
- do not build CI, billing, deployment, auth, teams, permissions, or a full
  enterprise DAM
- do not change the golden run canonical constants
- do not change the historical contracts the regression gate verifies
- do not change the PS-037 disclosure contract
- do not change the PS-037a multimodal proof contract
- do not change the PS-037b transcript/timestamp contract
- do not introduce a control name containing `KEY`, `TOKEN`, or `SECRET`
- do not use hidden Git flags (`assume-unchanged`, `skip-worktree`,
  `git update-index`, `update-index`)
- do not run recursive smokes
- do not use generic AI hype copy or unsupported claims
- do not create duplicate context-blind overclaim scanners in chat/spec
  guidance; the PS-037c smoke and its evidence report are the source of truth
  for slice overclaim validation; do not scan smoke guard fixtures as product
  claims

PS-037c only edits this spec file in the spec-only phase.
Implementation-phase candidate files are listed in section 8.

## 8. Implementation Candidate Files

The following are implementation-phase candidates only, clearly marked as
implementation-phase only. They are **not** for this spec-only commit. They are
listed so the implementation phase has a grounded file plan that follows
existing app conventions (each surface has a PascalCase `.tsx` component, a
camelCase `.ts` data module, a smoke script, and an evidence directory).

Shared layer (new files):
- `apps/web/src/voiceAudioEvidenceChoice.ts` (new) — the canonical camelCase
  voice/audio evidence provider choice data module. Exposes the single shared
  set of voice/audio evidence provider choice concepts, the two evidence tracks
  (ElevenLabs Voiceover Artifact Evidence and Hume Emotion-Signal Evidence),
  the provider choice and selected voice/audio evidence path, audio artifact
  evidence, honest "not available" / "not claimed" / "unknown" states, deferred
  later-slice states, de-escalation pairs, negative boundary strings, and
  not-claimed / unknown status used by every core proof surface. Same
  convention as `assemblyAITranscriptEvidence.ts`, `multimodalProof.ts`,
  `trustBoundary.ts`, `b2Evidence.ts`, `b2RehydrateComparison.ts`,
  `judgeEvidencePack.ts`, etc. ElevenLabs and Hume are named as selectable
  evidence providers for evidence labeling only; the module must not contain a
  live ElevenLabs API call or a live Hume API call.
- `apps/web/src/VoiceAudioEvidenceChoiceLayer.tsx` (new) — the shared
  voice/audio evidence provider choice component. Accepts the existing
  `variant` convention (for example `variant="panel"` for an expanded
  voice/audio provider-choice panel and `variant="summary"` /
  `variant="badge"` for a compact voice/audio provider-choice summary), reads
  only from `apps/web/src/voiceAudioEvidenceChoice.ts`, and renders the
  voice/audio evidence provider choice layer with no ElevenLabs API calls, no
  Hume API calls, no provider calls, and no live B2 reads. Rendered alongside
  the existing `TrustBoundaryLayer` (PS-037), `MultimodalProofLayer`
  (PS-037a), and `TranscriptTimestampEvidenceLayer` (PS-037b).

Additive use on core proof surfaces (existing files, edited additively only):
- `apps/web/src/JudgeCockpitHome.tsx` (PS-023) — render the voice/audio
  evidence provider choice layer on the home surface.
- `apps/web/src/B2EvidenceExplorer.tsx` (PS-026) — render the voice/audio
  evidence provider choice layer (B2 evidence status for the audio artifact).
- `apps/web/src/B2RehydrateComparison.tsx` (PS-029) — render the voice/audio
  evidence provider choice layer (rehydrate evidence status for the audio
  artifact).
- `apps/web/src/ManifestVerificationPanel.tsx` (PS-028) — render the
  voice/audio evidence provider choice layer (source media artifact reference
  + source media artifact digest modalities).
- `apps/web/src/B2AuditVault.tsx` (PS-036) — render the voice/audio evidence
  provider choice layer (B2 evidence status / rehydrate evidence status audit
  for the audio artifact).
- `apps/web/src/ReviewApprovalWorkspace.tsx` (PS-035) — render the voice/audio
  evidence provider choice layer (the reviewable artifact's voice/audio
  evidence provider choice).
- `apps/web/src/JudgeEvidencePack.tsx` (PS-031) — render the voice/audio
  evidence provider choice layer (export-pack audio artifact summary).
- `apps/web/src/PublicPassportPage.tsx` (PS-019) — render the voice/audio
  evidence provider choice layer (provenance passport voice/audio evidence).
- `apps/web/src/App.tsx` (PS-013 / PS-014) — render the voice/audio evidence
  provider choice layer on the Review Room, complementing the existing asset /
  manifest / evidence panels, the PS-037 disclosure layer, the PS-037a
  multimodal proof layer, and the PS-037b transcript/timestamp evidence layer.

Additive styles (existing file, additive classes only):
- `apps/web/src/styles.css` — add only the classes needed for the voice/audio
  evidence provider choice layer (provider-choice pills, selected-path rows,
  track-status pills, voiceover-status pills, emotion-signal-status pills,
  audio-artifact-reference rows, audio-artifact-digest rows,
  provider-output-reference rows, provider-output-digest rows,
  source-media-artifact-reference rows, source-media-artifact-digest rows,
  unavailable / not-claimed / unknown pills). No global style rewrite. PS-037c
  must not remove or weaken the existing `.trust-boundary-layer*` classes from
  PS-037, the multimodal proof layer classes from PS-037a, or the
  transcript/timestamp evidence layer classes from PS-037b.

Backend (`src/proofstudio`) — none:
- PS-037c is a frontend-only voice/audio evidence provider choice layer over
  existing accepted data. No backend change is expected. If any read-only reuse
  of an accepted data path is needed, it must reuse the existing accepted data
  paths under `src/proofstudio/api/` and `src/proofstudio/provenance/` without
  calling ElevenLabs, without calling Hume, without calling any provider, and
  without reading live B2. No new provider wiring, no ElevenLabs client, no
  Hume client, no new B2 client, no new B2 write path, no new broad B2 scan
  path. If no backend change is needed, none is made.

Smoke (scripts):
- `scripts/ps037c_voice_audio_evidence_provider_choice_smoke.py` (new) — the
  PS-037c feature smoke. Must reuse `scripts/smoke_lib.py` for shared
  validation logic and must implement its own explicit `h` / `S`
  hidden-Git-flags checker (see section 14). Local / static only.

Spec / docs:
- `specs/07-master-spec-plan.md` — implementation-phase cross-reference only
  (register PS-037c acceptance). Must not change any historical item or golden
  constant.
- `specs/08-roadmap-slices.md` — implementation-phase status update only.
- `docs/validation/proofstudio-smoke-harness-v1.md` — implementation-phase
  PS-037c note only, additive, must not weaken any existing PS-034A / PS-035C
  contract.
- `docs/ps-037c-voice-audio-evidence-provider-choice-layer-proof.md` (new) —
  the PS-037c proof doc.

Evidence:
- `docs/evidence/ps-037c/voice-audio-evidence-provider-choice-report.json`
  (new) — the only evidence PS-037c may write, and only when `--write-evidence`
  is explicit.

Any edit to `src/proofstudio/**` during implementation requires the backend
change to remain read-only over accepted data and to make no ElevenLabs API
call, no Hume API call, no provider call, and no live B2 read.

## 9. Forbidden files Unless PM-approved Later

PS-037c implementation must not touch without explicit PM approval:

- `AGENTS.md`
- `.env*`
- `render.yaml`
- requirements files
- `docs/evidence/**` paths other than `docs/evidence/ps-037c/**`
- any prior-slice evidence prefix (for example `docs/evidence/ps-037b/**`,
  `docs/evidence/ps-037a/**`, `docs/evidence/ps-037/**`,
  `docs/evidence/ps-036/**`, `docs/evidence/ps-035/**`,
  `docs/evidence/ps-031/**`, `docs/evidence/ps-029/**`,
  `docs/evidence/ps-026/**`, `docs/evidence/ps-021/**`,
  `docs/evidence/demo/golden-demo-run.json`,
  `docs/evidence/golden-fixture-digests.json`)
- `scripts/proofstudio_regression_gate.py` (the central gate is not owned by
  PS-037c)
- `scripts/smoke_lib.py` (shared library; PS-037c must not mutate shared
  validation behavior)
- any provider wrapper under `src/proofstudio/providers/**` (PS-037c owns no
  live provider behavior; PS-037d owns the other later provider-specific slice)
- any B2 client / storage write path (PS-037c performs no live B2 read, no B2
  write, and no broad B2 scan)
- any ElevenLabs client / live ElevenLabs integration path (PS-037c names
  ElevenLabs for evidence labeling only; no live ElevenLabs API call is allowed
  unless a later PM-approved slice explicitly enables a live-provider path with
  cost controls, env gates, and evidence boundaries)
- any Hume client / live Hume integration path (PS-037c names Hume for evidence
  labeling only; no live Hume API call is allowed unless a later PM-approved
  slice explicitly enables a live-provider path with cost controls, env gates,
  and evidence boundaries)
- the PS-037 disclosure contract files (`apps/web/src/trustBoundary.ts`,
  `apps/web/src/TrustBoundaryLayer.tsx`) except for additive integration; any
  change that weakens or duplicates the PS-037 boundary is forbidden
- the PS-037a multimodal proof contract files
  (`apps/web/src/multimodalProof.ts`,
  `apps/web/src/MultimodalProofLayer.tsx`) except for additive cross-reference;
  any change that weakens, duplicates, or removes the PS-037a deferred
  voice/emotion states is forbidden
- the PS-037b transcript/timestamp contract files
  (`apps/web/src/assemblyAITranscriptEvidence.ts`,
  `apps/web/src/TranscriptTimestampEvidenceLayer.tsx`) except for additive
  cross-reference; any change that weakens, duplicates, or removes the PS-037b
  contract is forbidden

The only implementation-phase files allowed without PM approval are those in
section 8. Any other path requires explicit PM approval.

## 10. Voice/Audio Evidence Provider Choice Product Contract

PS-037c defines the following contract for the Voice/Audio Evidence Provider
Choice Layer.

### 10.1 Layer identity

- It is a reusable voice/audio evidence provider choice layer, not a new proof
  surface, not a new route, and not a new backend endpoint.
- It is provider-choice by design: the customer can select between two
  evidence tracks. It is not ElevenLabs-only and not Hume-only.
- It is purely client-side by default: it makes no ElevenLabs API call, makes
  no Hume API call, calls no provider, reads no B2 object, exposes no
  arbitrary `run_id` input, performs no browser-side B2 byte verification,
  performs no broad B2 scan, and writes no B2 object.
- It is sourced from accepted local / golden / demo data and existing accepted
  data modules only, or from explicit honest "not available" / "not claimed" /
  "unknown" states.
- It makes the voice/audio provider-choice framing consistent on every core
  proof surface. It does not invent new voiceovers, new emotion signals, new
  voice analyses, new emotion analyses, new voice clones, or new provider
  outputs; it states the existing recorded voice/audio evidence consistently
  and honestly, and it states honest "not available" / "not claimed" /
  "unknown" states where no evidence exists.
- ElevenLabs and Hume are named as selectable evidence providers for evidence
  labeling only. Naming a provider does not imply a live provider call, live
  provider availability, or any correctness guarantee. Provider choice does not
  equal provider availability.
- It integrates with the PS-037 Disclosure + Trust Boundary Layer: it renders
  alongside `TrustBoundaryLayer` and reuses the shared disclosure concepts, and
  must not duplicate or weaken the PS-037 boundary.
- It integrates / cross-references the PS-037a Multimodal Proof Layer: it
  renders alongside `MultimodalProofLayer` and fills the concrete voice/audio
  provider-choice evidence that PS-037a only reserved as deferred, and must not
  duplicate, weaken, or remove the PS-037a deferred voice/emotion states.
- It integrates / cross-references the PS-037b Transcript/Timestamp Evidence
  layer: it renders alongside `TranscriptTimestampEvidenceLayer` and surfaces an
  honest transcript/timestamp cross-reference so a reviewer can read whether
  transcript/timestamp evidence from PS-037b cross-references the audio
  artifact, and must not duplicate or weaken the PS-037b contract.

### 10.2 Required voice/audio provider-choice concepts

The layer must surface these canonical voice/audio evidence provider choice
concepts, each as a clearly labeled item:

- `provider choice` — the customer-selectable decision between the two evidence
  tracks. Provider choice does not equal provider availability.
- `selected voice/audio evidence path` — which voice/audio evidence path is
  currently selected (one of the two tracks, honestly surfaced).
- `ElevenLabs Voiceover Artifact Evidence` — the first selectable evidence
  track.
- `Hume Emotion-Signal Evidence` — the second selectable evidence track.
- `ElevenLabs` — the named provider for the Voiceover Artifact Evidence track,
  for evidence labeling only.
- `Hume` — the named provider for the Emotion-Signal Evidence track, for
  evidence labeling only.
- `voiceover artifact evidence` — whether voiceover artifact evidence exists
  for the ElevenLabs track.
- `emotion-signal evidence` — whether emotion-signal evidence exists for the
  Hume track.
- `audio artifact` — the recorded audio artifact, if any, that the voice/audio
  evidence relates to.
- `audio artifact reference` — where the audio artifact reference is recorded
  (for example an audio artifact id, file reference, or audio artifact URI),
  honestly surfaced or honestly unavailable.
- `audio artifact digest` — the recorded hash / digest for the audio artifact,
  honestly surfaced or honestly unavailable.
- `provider output reference` — where the provider output reference is
  recorded, if available (for example a voiceover output reference or an
  emotion-signal output reference); honestly surfaced or honestly unavailable.
- `provider output digest` — the recorded hash / digest for the provider
  output, if available; honestly surfaced or honestly unavailable.
- `source media artifact reference` — what source media artifact the voice/audio
  evidence relates to (for example `archive_uri`, `manifest_uri`, asset id),
  honestly surfaced or honestly unavailable.
- `source media artifact digest` — the recorded hash / digest for the source
  media artifact (for example `archive_sha256`), honestly surfaced or honestly
  unavailable.
- `voice/audio evidence status` — the honest status of the voice/audio evidence
  (present / not available / not claimed / unknown).
- `voiceover status` — the honest status of the voiceover artifact evidence
  (present / not available / not claimed / unknown).
- `emotion-signal status` — the honest status of the emotion-signal evidence
  (present / not available / not claimed / unknown).
- `provider activity status` — whether provider activity happened for the
  voice/audio evidence (no provider calls by default; local/demo evidence by
  default).
- `B2 evidence status` — whether B2 archive evidence is recorded for the audio
  artifact, and whether it is recorded-only or live-verified (recorded-only by
  default).
- `rehydrate evidence status` — whether rehydrate evidence is recorded for the
  audio artifact.
- `local verification` — whether evidence is locally verified against
  checked-in / accepted data.
- `live verification status` — whether a live check is in scope (local /
  check-only by default; live provider evidence not available by default).
- `disclosure boundary` — the voice/audio disclosure boundary, sourced from /
  consistent with PS-037.
- `not claimed` — the honest set of things ProofStudio does not claim for
  voice/audio evidence.
- `unknown` — what remains unknown or not surfaced for voice/audio evidence.
- `local/demo evidence` — whether the voice/audio evidence is local / demo /
  golden fixture evidence (the default posture).
- `live provider evidence not available` — the honest default state that no
  live provider voice/audio evidence is available.

If a concept does not apply, the layer must show an honest "not available" /
"not claimed" / "unknown" state and must not fabricate a value.

### 10.3 Required surfaces

The voice/audio evidence provider choice layer must be rendered (additively) on
at least these required core proof surfaces, so
`required_surfaces_have_voice_audio_choice_layer` is truthful:

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

### 10.4 Two evidence tracks

The layer exposes a provider choice between two evidence tracks:

1. ElevenLabs Voiceover Artifact Evidence (provider: ElevenLabs)
2. Hume Emotion-Signal Evidence (provider: Hume)

For each track, the layer records honestly whether evidence exists in accepted
data, whether it is local / demo / golden evidence or live evidence, and what
it proves and does not prove. The selected voice/audio evidence path records
which track is chosen. The layer must not invent a voiceover, an emotion
signal, a voice analysis, an emotion analysis, a voice clone, or any provider
output that is not backed by accepted evidence or by an honest "not available
yet" state.

### 10.5 Local / live evidence honesty

The layer must distinguish clearly between:

- local voice/audio evidence (audio artifact references, audio artifact
  digests, source media artifact references/digests, provider output
  references/digests recorded in accepted checked-in data)
- live evidence (none, by default — PS-037c performs no live B2 read, no
  ElevenLabs API call, no Hume API call, and no provider call)
- demo / golden evidence (the golden demo run, which is local / golden, not
  production)

A reviewer reading the layer must never mistake a provider choice for provider
availability, local voice/audio evidence for live ElevenLabs availability,
local voice/audio evidence for live Hume availability, a demo/golden voice/audio
artifact for production security, a voiceover artifact reference for legal
authenticity, an audio artifact for voice authenticity, a provider voice output
for speaker identity, or an emotion signal for emotion truth.

### 10.6 Required unavailable / not-claimed states (verbatim)

The layer must surface, honestly, these unavailable / not-claimed states
verbatim. These are non-claim states: they state what is not available, not
claimed, or unknown, and must never be read as a hidden proof:

- local/demo evidence
- live provider evidence not available
- ElevenLabs evidence path not available
- Hume evidence path not available
- voiceover artifact not available
- emotion signal not available
- speaker identity not claimed
- voice authenticity not claimed
- biometric identification not claimed
- emotion truth not claimed
- psychological diagnosis not claimed
- health inference not claimed
- campaign intelligence deferred to PS-037d
- transcript/timestamp cross-reference
- not claimed
- unknown

PS-037c must not fake a voiceover, an emotion signal, a voice analysis, an
emotion analysis, a voice clone, a speaker identity, a biometric identity, a
campaign intelligence output, or any provider output. The honest unavailable /
not-claimed / unknown states are the only acceptable representation of those
concepts when no accepted evidence exists.

### 10.7 Required de-escalation pairs (verbatim)

The layer must surface these voice/audio provider-choice de-escalation pairs
verbatim so a judge never mistakes a strong-sounding voiceover artifact or
emotion signal for a stronger guarantee:

- proof does not equal truth
- provider choice does not equal provider availability
- voiceover artifact reference does not equal legal authenticity
- audio artifact does not equal voice authenticity
- provider voice output does not equal speaker identity
- emotion signal does not equal emotion truth
- local voice/audio evidence does not equal live ElevenLabs availability
- local voice/audio evidence does not equal live Hume availability
- demo/golden voice/audio evidence does not equal production security

### 10.8 Required negative boundary strings (verbatim)

The layer must surface these negative boundary strings verbatim:

- not voice authenticity
- not speaker identity
- not biometric identification
- not emotion truth
- not psychological diagnosis
- not health inference
- not mental state diagnosis
- not semantic truth
- not legal authenticity
- not human authorship
- not C2PA authenticity
- not Object Lock
- not tamper-proof
- not browser-side B2 byte verification
- not live B2 availability
- not live ElevenLabs availability
- not live Hume availability
- not production security
- not identity verification
- not deepfake detection
- not content moderation
- not OCR correctness
- not transcript correctness
- not timestamp correctness
- not model output truth

### 10.9 Boundary honesty

The layer must not imply that any ProofStudio voice/audio artifact or provider
choice proves anything beyond what the pipeline recorded. In particular it must
not imply that a provider choice, a voiceover artifact reference, an audio
artifact, an audio artifact digest, a provider output reference, a provider
output digest, a source media artifact reference, an emotion signal, or a
selected voice/audio evidence path proves voice authenticity, speaker identity,
biometric identity, biometric identification, emotion truth, psychological
diagnosis, mental state diagnosis, health inference, semantic truth, legal
authenticity, human authorship, C2PA authenticity, identity, deepfake absence,
content-policy compliance, OCR correctness, transcript correctness, timestamp
correctness, model output truth, live ElevenLabs availability, live Hume
availability, or production security.

## 11. UI/UX Contract

The Voice/Audio Evidence Provider Choice Layer UI must include:

- A clear title: "Voice/Audio Evidence Provider Choice Layer" (or an equivalent
  clear title), with a positioning line that ProofStudio proves what the
  pipeline recorded for voice/audio evidence, that this is a provider-choice
  layer supporting ElevenLabs Voiceover Artifact Evidence and Hume
  Emotion-Signal Evidence, and that ElevenLabs and Hume are named as
  selectable evidence providers for evidence labeling only (provider choice
  does not equal provider availability).
- A compact voice/audio provider-choice summary variant (for example
  `variant="summary"` or `variant="badge"`) that lists, in one compact block,
  the selected voice/audio evidence path, the two evidence tracks, the recorded
  voice/audio evidence and its honest "not available" / "not claimed" /
  "unknown" states, suitable for surfaces where space is constrained.
- An expanded voice/audio provider-choice panel variant (for example
  `variant="panel"`) that states, in full, the voice/audio provider-choice
  contract.
- A provider-choice block that shows: provider choice, selected voice/audio
  evidence path, and the two tracks (ElevenLabs Voiceover Artifact Evidence /
  Hume Emotion-Signal Evidence), each with its honest present / not available /
  not claimed / unknown status.
- A voiceover-evidence block that shows: voiceover status, audio artifact,
  audio artifact reference, audio artifact digest, provider output reference,
  provider output digest, source media artifact reference, source media
  artifact digest, provider (ElevenLabs), and an honest unavailable / not
  claimed / unknown state where no value exists.
- An emotion-signal-evidence block that shows: emotion-signal status, provider
  (Hume), provider output reference, provider output digest, and honest
  unavailable / not claimed / unknown states where no value exists.
- A provider-activity / B2 / rehydrate block that shows: provider activity
  status, B2 evidence status, rehydrate evidence status, local verification,
  and live verification status.
- A "not claimed" section listing, verbatim, what voice/audio evidence does
  not prove (section 10.8), the honest unavailable / not-claimed states
  (section 10.6), and the deferred later-slice states (section 10.6).
- The de-escalation pairs (section 10.7), surfaced verbatim.
- The negative boundary strings (section 10.8), surfaced verbatim.
- A transcript/timestamp cross-reference indicator that states, honestly,
  whether transcript/timestamp evidence from PS-037b cross-references the audio
  artifact.
- A persistent voice/audio boundary statement that states verbatim (or
  equivalent):

  > ProofStudio proves what the pipeline recorded for voice/audio evidence.
  > Proof does not equal truth. Provider choice does not equal provider
  > availability. A voiceover artifact reference does not equal legal
  > authenticity. An audio artifact does not equal voice authenticity. A
  > provider voice output does not equal speaker identity. An emotion signal
  > does not equal emotion truth. Local voice/audio evidence does not equal
  > live ElevenLabs availability. Local voice/audio evidence does not equal
  > live Hume availability. Demo/golden voice/audio evidence does not equal
  > production security.

- Integration with the PS-037 Disclosure + Trust Boundary Layer: the
  voice/audio provider-choice layer renders alongside `TrustBoundaryLayer`,
  reuses the shared disclosure concepts, and never contradicts the PS-037
  boundary.
- Integration / cross-reference with the PS-037a Multimodal Proof Layer: the
  voice/audio provider-choice layer renders alongside `MultimodalProofLayer`
  and fills the concrete voice/audio provider-choice evidence that PS-037a only
  reserved as deferred, and never contradicts or removes the PS-037a deferred
  voice/emotion states.
- Integration / cross-reference with the PS-037b Transcript/Timestamp Evidence
  layer: the voice/audio provider-choice layer renders alongside
  `TranscriptTimestampEvidenceLayer` and surfaces an honest
  transcript/timestamp cross-reference, and never contradicts or weakens the
  PS-037b contract.

UI / UX constraints:

- Must be useful in a three-minute hackathon demo: open any core proof surface
  -> read the compact voice/audio provider-choice summary -> read the selected
  path and the two tracks -> expand the voice/audio provider-choice panel ->
  read what voice/audio evidence proves -> read what it does not prove -> read
  the unavailable / not-claimed states -> read the de-escalation pairs -> read
  the negative boundary strings.
- Must render the same voice/audio provider-choice framing on every required
  surface (section 10.3).
- Must not introduce generic AI hype copy.
- Must not add unsupported claims.
- Must not fabricate voiceovers, emotion signals, voice analyses, emotion
  analyses, voice clones, speaker identities, biometric identities, digests, or
  provider outputs that are not in accepted data.
- Must follow the existing component conventions (`variant`, pills, cards,
  `JsonExpander`, the `.trust-boundary`, `.trust-boundary-layer*`, multimodal
  proof layer, and transcript/timestamp evidence layer styles) used by the
  other surfaces.
- Must not delete or weaken any existing per-surface truth-boundary panel,
  per-surface artifact record, the PS-037 disclosure layer, the PS-037a
  multimodal proof layer, or the PS-037b transcript/timestamp evidence layer;
  the voice/audio provider-choice layer is additive.

## 12. Data Contract

### 12.1 Source data (read-only inputs)

PS-037c reads accepted local / golden / demo data and existing accepted data
modules as immutable inputs. It must not mutate these and must not change their
canonical values. Acceptable read-only sources:

- `apps/web/src/trustBoundary.ts` (PS-037) — reuse the shared disclosure
  concepts; do not duplicate or weaken them
- `apps/web/src/multimodalProof.ts` (PS-037a) — reuse / fill the deferred
  voice/emotion reservation; do not duplicate, weaken, or remove it
- `apps/web/src/assemblyAITranscriptEvidence.ts` (PS-037b) — reuse /
  cross-reference the transcript/timestamp evidence that may reference a
  media/audio artifact; do not duplicate, weaken, or remove it
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

Where no accepted voice/audio evidence exists, PS-037c must surface explicit
honest "not available" / "not claimed" / "unknown" states and must not
fabricate values. PS-037c must not change the golden run canonical constants.
The canonical constants are owned by their respective accepted slices.

### 12.2 Voice/audio provider-choice item shape

A voice/audio evidence provider choice item is derived from accepted data and
must expose:

- `provider_choice` (the customer-selectable decision between the two tracks;
  honestly surfaced)
- `selected_voice_audio_evidence_path` (which track is selected; one of
  `elevenlabs_voiceover_artifact_evidence`, `hume_emotion_signal_evidence`,
  or an honest `not_available` / `unknown` default)
- `elevenlabs_voiceover_artifact_evidence` (the ElevenLabs Voiceover Artifact
  Evidence track record, honestly surfaced)
- `hume_emotion_signal_evidence` (the Hume Emotion-Signal Evidence track
  record, honestly surfaced)
- `voiceover_status` (one of `present`, `not_available`, `not_claimed`,
  `unknown`)
- `emotion_signal_status` (one of `present`, `not_available`, `not_claimed`,
  `unknown`)
- `voice_audio_evidence_status` (one of `present`, `not_available`,
  `not_claimed`, `unknown`)
- `audio_artifact_reference` (where the audio artifact reference is recorded,
  or honestly unavailable)
- `audio_artifact_digest` (the recorded hash / digest, or honestly unavailable)
- `provider_output_reference` (the recorded provider output reference, if
  available, or honestly unavailable)
- `provider_output_digest` (the recorded provider output digest, if available,
  or honestly unavailable)
- `source_media_artifact_reference` (the recorded source media artifact
  reference, or honestly unavailable)
- `source_media_artifact_digest` (the recorded source media artifact digest, or
  honestly unavailable)
- `b2_evidence_status` (recorded-only by default)
- `rehydrate_evidence_status`
- `provider_activity_status` (no provider calls by default)
- `local_verification` (locally verified against accepted checked-in data)
- `live_verification_status` (local / check-only by default; live provider
  evidence not available by default)
- `disclosure_boundary` (sourced from / consistent with PS-037)
- `transcript_timestamp_cross_reference` (an honest indicator of whether
  transcript/timestamp evidence from PS-037b cross-references the audio
  artifact)
- `label` (the human-readable label, matching the verbatim strings in
  section 21)
- `value` (the evidence value, honest about local / recorded-only /
  unavailable / not claimed / unknown)
- `applicable` (boolean; false when the concept honestly does not apply)
- `state` (one of `recorded`, `locally_verified`, `recorded_only`,
  `not_verified`, `not_available`, `not_claimed`, `unknown`, `deferred_to_later_slice`)

### 12.3 Evidence report schema rule

The PS-037c evidence report must follow the harness schema rule: boolean
fields remain booleans and detail / list fields use explicit detail names. A
field whose name implies a boolean success flag must remain a boolean. List
fields must use explicit detail names such as `_ids`, `_details`, or
`_failures` (see section 13).

## 13. Evidence Contract

PS-037c owns exactly one evidence directory: `docs/evidence/ps-037c/`.

- A feature smoke may write only its own evidence, and only when
  `--write-evidence` is explicit. The default PS-037c smoke behavior is
  non-mutating local validation.
- PS-037c must not write any file outside `docs/evidence/ps-037c/`.
- PS-037c must not mutate any prior-slice evidence (every prior evidence prefix
  is guarded by `scripts/smoke_lib.py` and
  `scripts/proofstudio_regression_gate.py`), including the PS-037 evidence
  under `docs/evidence/ps-037/`, the PS-037a evidence under
  `docs/evidence/ps-037a/`, and the PS-037b evidence under
  `docs/evidence/ps-037b/`.
- The PS-037c evidence file is
  `docs/evidence/ps-037c/voice-audio-evidence-provider-choice-report.json`.

The PS-037c evidence report must carry these boolean fields (booleans as
booleans; `failures` as a list):

- `ok` (boolean; true only when every measured field is truthful and no
  forbidden overclaim or forbidden file change is present)
- `slice_id`: `ps037c`
- `voice_audio_choice_component_present` (boolean;
  `VoiceAudioEvidenceChoiceLayer` component exists)
- `voice_audio_choice_data_module_present` (boolean;
  `voiceAudioEvidenceChoice.ts` exists)
- `voice_audio_choice_layer_present` (boolean; the shared layer is wired in)
- `required_surfaces_have_voice_audio_choice_layer` (boolean; the required
  surfaces in section 10.3 that are present in this repo render the layer)
- `multimodal_proof_cross_reference_present` (boolean; the layer integrates /
  cross-references the PS-037a Multimodal Proof Layer)
- `transcript_timestamp_cross_reference_present` (boolean; the layer integrates
  / cross-references the PS-037b Transcript/Timestamp Evidence layer)
- `trust_boundary_preserved` (boolean; the PS-037 Disclosure + Trust Boundary
  Layer is preserved)
- `provider_choice_present` (boolean)
- `selected_voice_audio_evidence_path_present` (boolean)
- `elevenlabs_voiceover_artifact_evidence_present` (boolean)
- `hume_emotion_signal_evidence_present` (boolean)
- `elevenlabs_label_present` (boolean; ElevenLabs is named as a selectable
  evidence provider for evidence labeling)
- `hume_label_present` (boolean; Hume is named as a selectable evidence
  provider for evidence labeling)
- `voiceover_artifact_evidence_present` (boolean)
- `emotion_signal_evidence_present` (boolean)
- `audio_artifact_present` (boolean)
- `audio_artifact_reference_present` (boolean)
- `audio_artifact_digest_present` (boolean)
- `provider_output_reference_present_or_honestly_unavailable` (boolean)
- `provider_output_digest_present_or_honestly_unavailable` (boolean)
- `source_media_artifact_reference_present` (boolean)
- `source_media_artifact_digest_present` (boolean)
- `voice_audio_evidence_status_present` (boolean)
- `voiceover_status_present` (boolean)
- `emotion_signal_status_present` (boolean)
- `provider_activity_status_present` (boolean)
- `b2_evidence_status_present` (boolean)
- `rehydrate_evidence_status_present` (boolean)
- `local_verification_status_present` (boolean)
- `live_verification_status_present` (boolean)
- `disclosure_boundary_present` (boolean)
- `not_claimed_status_present` (boolean)
- `unknown_status_present` (boolean)
- `local_demo_evidence_present` (boolean)
- `live_provider_evidence_not_available_present` (boolean)
- `elevenlabs_evidence_path_not_available_present` (boolean)
- `hume_evidence_path_not_available_present` (boolean)
- `voiceover_artifact_not_available_present` (boolean)
- `emotion_signal_not_available_present` (boolean)
- `speaker_identity_not_claimed_present` (boolean)
- `voice_authenticity_not_claimed_present` (boolean)
- `biometric_identification_not_claimed_present` (boolean)
- `emotion_truth_not_claimed_present` (boolean)
- `psychological_diagnosis_not_claimed_present` (boolean)
- `health_inference_not_claimed_present` (boolean)
- `campaign_intelligence_deferred_to_ps037d_present` (boolean)
- `proof_does_not_equal_truth_present` (boolean)
- `no_voice_authenticity_claim` (boolean)
- `no_speaker_identity_claim` (boolean)
- `no_biometric_identification_claim` (boolean)
- `no_emotion_truth_claim` (boolean)
- `no_psychological_diagnosis_claim` (boolean)
- `no_health_inference_claim` (boolean)
- `no_mental_state_diagnosis_claim` (boolean)
- `no_semantic_truth_claim` (boolean)
- `no_legal_authenticity_claim` (boolean)
- `no_human_authorship_claim` (boolean)
- `no_c2pa_authenticity_claim` (boolean)
- `no_object_lock_claim` (boolean)
- `no_tamper_proof_claim` (boolean)
- `no_browser_side_b2_byte_verification_claim` (boolean)
- `no_live_b2_availability_claim` (boolean)
- `no_live_elevenlabs_availability_claim` (boolean)
- `no_live_hume_availability_claim` (boolean)
- `no_production_security_claim` (boolean)
- `no_identity_verification_claim` (boolean)
- `no_deepfake_detection_claim` (boolean)
- `no_content_moderation_claim` (boolean)
- `no_ocr_correctness_claim` (boolean)
- `no_transcript_correctness_claim` (boolean)
- `no_timestamp_correctness_claim` (boolean)
- `no_model_output_truth_claim` (boolean)
- `no_elevenlabs_api_calls` (boolean)
- `no_hume_api_calls` (boolean)
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

PS-037c ships one feature smoke:
`scripts/ps037c_voice_audio_evidence_provider_choice_smoke.py`.

The PS-037c feature smoke must:

- validate only the PS-037c slice (no recursive smokes; must never launch
  another feature smoke as a subprocess; must never call the central regression
  gate)
- read checked-in prior evidence and accepted data modules as immutable inputs
- write only its own evidence file
  `docs/evidence/ps-037c/voice-audio-evidence-provider-choice-report.json`,
  and only when `--write-evidence` is explicit
- never call ElevenLabs (no ElevenLabs API calls)
- never call Hume (no Hume API calls)
- never call any provider (no provider calls)
- never read arbitrary B2 objects (no live B2 reads)
- never write B2 (no B2 writes)
- never perform broad B2 scans
- never run the frontend typecheck / build (that belongs to the central gate)
- reuse `scripts/smoke_lib.py` for shared validation logic
- validate the shared `VoiceAudioEvidenceChoiceLayer` component is present
- validate the shared `voiceAudioEvidenceChoice.ts` data module is present
- validate the voice/audio evidence provider choice layer is rendered on the
  required proof surfaces that are present in this repo (section 10.3)
- validate the layer integrates / cross-references the PS-037a Multimodal Proof
  Layer (`multimodal_proof_cross_reference_present`)
- validate the layer integrates / cross-references the PS-037b Transcript/
  Timestamp Evidence layer (`transcript_timestamp_cross_reference_present`)
- validate the PS-037 TrustBoundaryLayer is preserved
  (`trust_boundary_preserved`)
- validate the required voice/audio provider-choice UI strings (section 21) are
  present
- validate the required negative boundary strings (section 21) are present
- validate the deferred later-slice states (section 10.6) are present and
  honest
- validate no ElevenLabs API calls are introduced
- validate no Hume API calls are introduced
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
  the PS-037c changed files, without the smoke or this spec reproducing that
  literal
- validate prior evidence is unchanged
- validate `git diff --check` is clean
- do not scan smoke guard fixtures as product claims (the future PS-037c smoke
  and its evidence report are the source of truth for slice overclaim
  validation; smoke guard fixtures are not product claims)

The PS-037c feature smoke must support these standard flags:

- `--check-only` (default: non-mutating local validation; no evidence file is
  written)
- `--write-evidence` (write only `docs/evidence/ps-037c/` evidence)
- `--no-frontend`

Default PS-037c smoke behavior is non-mutating local validation
(`--check-only`).

The smoke must not contain the bad lowercase-only hidden-flag marker check and
must not rely on a lowercase-only marker check. The hidden-Git-flags check must
be the explicit `h` / `S` checker over `git ls-files -v`, and must record
`no_hidden_git_flags_h` and `no_hidden_git_flags_S` as separate booleans.

PS-037c smoke performs no ElevenLabs API calls, no Hume API calls, no provider
calls, no live B2 reads, no B2 writes, and no broad B2 scans.

The PS-037c smoke must not create duplicate context-blind overclaim scanners.
The smoke and its evidence report are the source of truth for PS-037c overclaim
validation. The smoke must not scan smoke guard fixtures as product claims.

## 15. Regression Gate Contract

The central regression gate remains the single cross-slice release-readiness
gate and is non-mutating by default. PS-037c does not own or modify the central
gate.

Normal future PS-037c release validation command:

```
python scripts/proofstudio_regression_gate.py --current ps037c --frontend --report-out /tmp/proofstudio-release-report.json
```

Contract-only gate (no frontend):

```
python scripts/proofstudio_regression_gate.py --current ps037c --no-frontend --report-out /tmp/proofstudio-ps037c-regression-report.json
```

- The gate runs `npm run typecheck` and `npm run build` in `apps/web` exactly
  once per invocation, and only when `--frontend` is passed. PS-037c feature
  smoke must never trigger nested frontend builds.
- The gate must not write the canonical PS-034A report. `--write-report` is
  rejected for `--current ps037c` (PS-035C accepted behavior; only PS-034A may
  regenerate the canonical report).
- Running the gate for `ps037c` must leave all prior-slice evidence unchanged,
  including the PS-037, PS-037a, and PS-037b evidence.
- No recursive smokes: the gate never executes a feature smoke.

Canonical PS-034A regeneration (unchanged, owned by PS-034A only):

```
python scripts/proofstudio_regression_gate.py --current ps034a --write-report
```

## 16. Truth Boundary

ProofStudio proves what the pipeline recorded. The Voice/Audio Evidence
Provider Choice Layer is a voice/audio evidence-inspection surface that makes
the recorded voice/audio evidence and the customer-selectable provider choice
explicit and consistent on every core proof surface. It is not a legal
authenticity system, not a live B2 verifier, not a truth system, not an
identity system, not a biometric system, not a speaker-identity system, not a
voice-authenticity system, not an emotion-truth system, not a psychological-
diagnosis system, not a health-inference system, not a deepfake detector, not a
content moderator, not an OCR verifier, not a transcript verifier, not a
timestamp verifier, not a live ElevenLabs verifier, and not a live Hume
verifier.

The layer must preserve these truth-boundary red lines verbatim across the
spec, the UI, and any evidence report:

- do not claim voice authenticity
- do not claim speaker identity
- do not claim biometric identification
- do not claim emotion truth
- do not claim psychological diagnosis
- do not claim mental state diagnosis
- do not claim health inference
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
- do not claim live ElevenLabs availability unless a live ElevenLabs check is
  explicitly implemented and approved with cost controls, env gates, and
  evidence boundaries
- do not claim live Hume availability unless a live Hume check is explicitly
  implemented and approved with cost controls, env gates, and evidence
  boundaries
- do not claim public deployment verification unless deployed and tested
- do not claim enterprise security
- do not claim production security
- do not claim production compliance
- do not claim legal review
- do not claim chain-of-custody guarantees beyond recorded pipeline evidence
- do not claim identity verification
- do not claim deepfake detection
- do not claim content moderation
- do not claim OCR correctness
- do not claim transcript correctness
- do not claim timestamp correctness
- do not claim model output truth
- do not claim actual spend / latency / quota unless captured
- do not claim provider failures / reruns / variants unless evidenced

PS-037c does not prove voice authenticity, speaker identity, biometric
identification, emotion truth, psychological diagnosis, mental state diagnosis,
health inference, product correctness, production security, production
compliance, B2 immutability, Object Lock, tamper-proof storage, browser-side B2
byte verification, live B2 availability, live ElevenLabs availability, live
Hume availability, real billing API integration, billing behavior, CI
enforcement, legal review, identity, biometric identity, deepfake absence,
content-policy compliance, OCR correctness, transcript correctness, timestamp
correctness, model output truth, or deployment readiness. No PS-037c artifact
may imply any of these. The voice/audio evidence provider choice layer states
what the pipeline already recorded; it does not re-fetch, re-hash, or re-verify
live B2 bytes, it does not call ElevenLabs, it does not call Hume, and it does
not call any provider.

## 17. Later-slice Boundaries

PS-037c must not implement, fake, or claim the later provider-specific slices
or out-of-scope capabilities. The boundaries are:

- PS-037d Gemini Campaign Intelligence / Judge Narrative — owns campaign
  intelligence and the judge narrative. PS-037c must only reserve an honest
  "campaign intelligence deferred to PS-037d" state. PS-037c must not produce,
  store, or claim a campaign intelligence output or a judge narrative.
- live ElevenLabs voice generation — out of scope for PS-037c. PS-037c names
  ElevenLabs for evidence labeling only. A live ElevenLabs path may only be
  enabled by a later PM-approved slice with cost controls, env gates, and
  evidence boundaries. PS-037c must only reserve an honest "ElevenLabs evidence
  path not available" state.
- live Hume emotion inference — out of scope for PS-037c. PS-037c names Hume
  for evidence labeling only. A live Hume path may only be enabled by a later
  PM-approved slice with cost controls, env gates, and evidence boundaries.
  PS-037c must only reserve an honest "Hume evidence path not available" state.
- voice clone authenticity — out of scope. PS-037c must not claim it.
- voice authenticity proof — out of scope. PS-037c must only reserve an honest
  "voice authenticity not claimed" state.
- speaker identity proof — out of scope. PS-037c must only reserve an honest
  "speaker identity not claimed" state.
- biometric identification — out of scope. PS-037c must only reserve an honest
  "biometric identification not claimed" state.
- emotion truth — out of scope. PS-037c must only reserve an honest "emotion
  truth not claimed" state.
- psychological diagnosis — out of scope. PS-037c must only reserve an honest
  "psychological diagnosis not claimed" state.
- mental state diagnosis — out of scope. PS-037c must not claim it.
- health inference — out of scope. PS-037c must only reserve an honest "health
  inference not claimed" state.
- content moderation — out of scope. PS-037c must not claim it.
- deepfake detection — out of scope. PS-037c must not claim it.
- legal review — out of scope. PS-037c must not claim it.
- semantic truth verification — out of scope. PS-037c must not claim it.

PS-037c may reserve fields and honest "not available yet" / "not claimed" /
"unknown" states for those later-slice / out-of-scope areas, but must not fake
voiceovers, emotion signals, voice analyses, emotion analyses, voice clones,
campaign intelligence, speaker identities, biometric identities, or any
provider output.

## 18. Risks

PS-037c must record the following risks with mitigations:

- overclaim risk
  - risk: a reviewer misreads the voice/audio evidence provider choice layer
    or its copy as a forbidden overclaim — i.e. as claiming voice authenticity,
    speaker identity, biometric identification, emotion truth, psychological
    diagnosis, mental state diagnosis, health inference, semantic truth, legal
    authenticity, human authorship, C2PA authenticity, Object Lock /
    tamper-proof storage, browser-side B2 byte verification, live B2
    availability, live ElevenLabs availability, live Hume availability,
    production security, production compliance, legal review, chain-of-custody
    guarantees beyond recorded pipeline evidence, identity verification,
    deepfake detection, content moderation, OCR correctness, transcript
    correctness, timestamp correctness, or model output truth. ProofStudio
    does not claim any of these.
  - mitigation: the persistent voice/audio boundary statement (section 11) is
    mandatory; the truth-boundary red lines (section 16) are preserved verbatim;
    the de-escalation pairs (section 10.7) and negative boundary strings
    (section 10.8) are surfaced verbatim; the evidence report carries
    `no_forbidden_overclaims` and `trust_boundary_preserved`.
- provider-choice overclaim risk
  - risk: the provider choice (ElevenLabs or Hume) is misread as a live
    provider call, live provider availability, a voice-generation guarantee,
    an emotion-inference guarantee, or a correctness guarantee. Naming
    ElevenLabs or Hume is misread as live ElevenLabs availability or live Hume
    availability.
  - mitigation: the provider-choice honesty (sections 10.1, 10.5) is mandatory;
    provider choice does not equal provider availability; the default posture
    is local/demo evidence with `live provider evidence not available`,
    `ElevenLabs evidence path not available`, and `Hume evidence path not
    available`; the evidence report carries `no_elevenlabs_api_calls`,
    `no_hume_api_calls`, `no_provider_calls`, `no_live_elevenlabs_availability_claim`,
    and `no_live_hume_availability_claim`; no live ElevenLabs or live Hume path
    exists in PS-037c.
- faking-voice/audio risk
  - risk: a voiceover, an emotion signal, a voice analysis, an emotion
    analysis, a voice clone, a speaker identity, or a biometric identity is
    silently represented as present when it is not, or is silently omitted so
    it looks hidden.
  - mitigation: the unavailable / not-claimed states (section 10.6) are
    surfaced verbatim and honestly; the smoke validates their presence;
    PS-037c never produces those provider outputs unless they exist in accepted
    data.
- de-escalation-gap risk
  - risk: a judge mistakes a provider choice for provider availability, a
    voiceover artifact reference for legal authenticity, an audio artifact for
    voice authenticity, a provider voice output for speaker identity, an
    emotion signal for emotion truth, local voice/audio evidence for live
    ElevenLabs availability, local voice/audio evidence for live Hume
    availability, or demo/golden voice/audio evidence for production security.
  - mitigation: the de-escalation pairs in section 10.7 are surfaced verbatim.
- PS-037 / PS-037a / PS-037b weakening risk
  - risk: the voice/audio provider-choice layer duplicates, contradicts,
    weakens, or removes the PS-037 Disclosure + Trust Boundary Layer, the
    PS-037a Multimodal Proof Layer (including its deferred voice/emotion
    states), or the PS-037b Transcript/Timestamp Evidence layer.
  - mitigation: the voice/audio provider-choice layer renders alongside
    `TrustBoundaryLayer`, `MultimodalProofLayer`, and
    `TranscriptTimestampEvidenceLayer`, reuses the shared disclosure concepts,
    fills the PS-037a deferred reservation, cross-references PS-037b, and never
    contradicts the PS-037 boundary or removes the PS-037a deferred states or
    the PS-037b contract; PS-037c does not edit the PS-037, PS-037a, or PS-037b
    contract files except additively (section 9).
- live-B2-read risk
  - risk: the layer triggers a live B2 read or a broad B2 scan.
  - mitigation: the layer is purely client-side over accepted data; the smoke
    enforces `no_live_b2_reads`, `no_b2_writes`, `no_broad_b2_scans`.
- evidence-mutation risk
  - risk: the PS-037c smoke or the central gate run overwrites prior-slice
    evidence, including PS-037, PS-037a, and PS-037b evidence.
  - mitigation: PS-037c writes only `docs/evidence/ps-037c/`; the gate is
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
  - risk: PS-037c expands into PS-037d provider behavior, a live ElevenLabs
    integration, a live Hume integration, live voice generation, live emotion
    inference, voice clone authenticity, identity verification, speaker
    identity proof, biometric identification, emotion truth, psychological
    diagnosis, health inference, content moderation, deepfake detection, CI,
    billing, deployment, auth, teams, permissions, a full enterprise DAM, a new
    backend, or a live B2 fetcher.
  - mitigation: section 7 lists these as non-goals; section 9 forbids the
    relevant paths; section 17 fixes the later-slice / out-of-scope boundaries.
- recursive-smoke risk
  - risk: the PS-037c smoke launches another feature smoke or calls the central
    gate.
  - mitigation: the smoke must never launch another feature smoke as a
    subprocess and must never call the central regression gate; the central
    gate is the only cross-slice validator.
- duplicate-scanner risk
  - risk: PS-037c adds duplicate context-blind overclaim scanners in
    chat/spec guidance that treat smoke guard fixtures as product claims.
  - mitigation: PS-037c does not create duplicate context-blind overclaim
    scanners; the PS-037c smoke and its evidence report are the source of truth
    for slice overclaim validation; smoke guard fixtures are not scanned as
    product claims.

## 19. Acceptance Criteria

PS-037c (spec-only phase) is accepted only when:

- this spec exists at
  `specs/57-ps-037c-voice-audio-evidence-provider-choice-layer.md`
- only this spec file is changed in the spec-only phase
- the branch `ps-037c/voice-audio-evidence-provider-choice-layer` starts from
  `origin/accepted/proofstudio` at commit
  `6d51b1d3fc0db88ff6c9fdaf16161e3df9c706ad` (the merge-base equals that
  commit)
- the product scope is clear and owns the voice/audio evidence provider choice
  layer only; it does not expand into CI, billing, deployment, ElevenLabs API
  calls, Hume API calls, provider calls, live B2 reads, B2 writes, broad B2
  scans, PS-037d, live voice generation, live emotion inference, voice clone
  authenticity, identity verification, biometric identification, speaker
  identity proof, voice authenticity proof, emotion truth, psychological
  diagnosis, mental state diagnosis, health inference, content moderation,
  deepfake detection, legal review, or semantic truth verification
- the required voice/audio provider-choice concepts (section 10.2), the two
  evidence tracks (section 10.4), and the required surfaces (section 10.3) are
  specified
- the unavailable / not-claimed states (section 10.6), the de-escalation pairs
  (section 10.7), and the negative boundary strings (section 10.8) are
  specified verbatim
- the UI / UX contract (section 11) and the persistent voice/audio boundary
  statement are specified
- the data contract (section 12) reuses accepted checked-in evidence as
  read-only inputs and surfaces honest unavailable / not-claimed / unknown
  states where no evidence exists
- the truth boundary (section 16) is explicit and the boundary copy is
  specified
- the later-slice boundaries (section 17) are fixed
- the implementation candidate files (section 8) are listed, but no
  implementation is done in this phase
- the validation plan uses the PS-037c feature smoke plus the central
  regression gate (sections 14 and 15)
- no evidence mutation occurs in this phase
- no hidden Git flags `h` or `S` are present (verified by the explicit h/S
  checker over `git ls-files -v`)
- `git diff --check` is clean
- no staging, commit, or push occurs until PM approval
- `AGENTS.md`, `specs/07-master-spec-plan.md`, and
  `specs/08-roadmap-slices.md` are not changed in this phase

Implementation-phase acceptance (for reference, not this phase) additionally
requires: the shared `VoiceAudioEvidenceChoiceLayer` component +
`voiceAudioEvidenceChoice.ts` data module exist; the voice/audio evidence
provider choice layer is rendered on the required surfaces present in this repo
(section 10.3); the layer integrates / cross-references the PS-037a Multimodal
Proof Layer and the PS-037b Transcript/Timestamp Evidence layer and preserves
the PS-037 TrustBoundaryLayer; the required voice/audio provider-choice
concepts, unavailable / not-claimed states, de-escalation pairs, and negative
boundary strings are present; the PS-037c smoke passes in `--check-only`
(default) and writes only `docs/evidence/ps-037c/**` under `--write-evidence`;
the central gate passes for `--current ps037c`; no ElevenLabs API call, no Hume
API call, no provider call, no live B2 read, no B2 write, no broad B2 scan
occurs; prior evidence is unchanged, including PS-037, PS-037a, and PS-037b
evidence; no forbidden overclaim is introduced; the PS-037 disclosure boundary,
the PS-037a multimodal proof contract, and the PS-037b transcript/timestamp
contract are not weakened.

## 20. Rollback

Rollback of the PS-037c spec-only phase is a single revert of this spec commit,
because only
`specs/57-ps-037c-voice-audio-evidence-provider-choice-layer.md` is changed in
this phase.

Future implementation rollback must restore the pre-PS-037c state of the edited
files in section 8. Specifically:

- remove `apps/web/src/voiceAudioEvidenceChoice.ts`
- remove `apps/web/src/VoiceAudioEvidenceChoiceLayer.tsx`
- revert the additive voice/audio-evidence-provider-choice-layer renders in
  `apps/web/src/JudgeCockpitHome.tsx`,
  `apps/web/src/B2EvidenceExplorer.tsx`,
  `apps/web/src/B2RehydrateComparison.tsx`,
  `apps/web/src/ManifestVerificationPanel.tsx`,
  `apps/web/src/B2AuditVault.tsx`,
  `apps/web/src/ReviewApprovalWorkspace.tsx`,
  `apps/web/src/JudgeEvidencePack.tsx`,
  `apps/web/src/PublicPassportPage.tsx`, and
  `apps/web/src/App.tsx` to pre-PS-037c state
- revert the additive voice/audio-evidence-provider-choice-layer classes in
  `apps/web/src/styles.css` to pre-PS-037c state
- remove `scripts/ps037c_voice_audio_evidence_provider_choice_smoke.py`
- remove `docs/ps-037c-voice-audio-evidence-provider-choice-layer-proof.md`
- remove `docs/evidence/ps-037c/` if it was added
- revert the additive cross-references in `specs/07-master-spec-plan.md`,
  `specs/08-roadmap-slices.md`, and
  `docs/validation/proofstudio-smoke-harness-v1.md` to pre-PS-037c state

Rollback of PS-037c must not touch any evidence under `docs/evidence/**` other
than `docs/evidence/ps-037c/`, must not touch the central gate
(`scripts/proofstudio_regression_gate.py`), `scripts/smoke_lib.py`,
`AGENTS.md`, `.env*`, `render.yaml`, requirements files, any provider wrapper,
any ElevenLabs client, any Hume client, any B2 storage path, the PS-037
disclosure contract, the PS-037a multimodal proof contract, or the PS-037b
transcript/timestamp contract. Rollback is isolated and reversible because
PS-037c is a self-contained voice/audio evidence provider choice layer over
existing accepted data; it does not change provider behavior, ElevenLabs
behavior, Hume behavior, B2 behavior, billing behavior, deployment topology,
the PS-037 boundary, the PS-037a contract, or the PS-037b contract.

## 21. Verbatim implementation/audit contract strings

The PS-037c implementation, the Voice/Audio Evidence Provider Choice Layer UI,
the PS-037c smoke, and the PS-037c evidence report must preserve the following
exact strings so the voice/audio provider-choice contract is deterministic
and auditable. Any future PM audit must check these exact strings; do not rely
on close-enough wording. No surprise audit checks: any exact string a future PM
audit should check is listed here.

The required identity / positioning strings are:

- PS-037c
- Voice/Audio Evidence Provider Choice Layer

The required provider-choice / evidence-track concept strings are:

- provider choice
- selected voice/audio evidence path
- ElevenLabs Voiceover Artifact Evidence
- Hume Emotion-Signal Evidence
- ElevenLabs
- Hume
- voiceover artifact evidence
- emotion-signal evidence

The required audio artifact / evidence-record strings are:

- audio artifact
- audio artifact reference
- audio artifact digest
- provider output reference
- provider output digest
- source media artifact reference
- source media artifact digest

The required status / boundary concept strings are:

- voice/audio evidence status
- voiceover status
- emotion-signal status
- provider activity status
- B2 evidence status
- rehydrate evidence status
- local verification
- live verification status
- disclosure boundary
- not claimed
- unknown
- local/demo evidence

The required honest unavailable / not-claimed state strings are:

- local/demo evidence
- live provider evidence not available
- ElevenLabs evidence path not available
- Hume evidence path not available
- voiceover artifact not available
- emotion signal not available
- speaker identity not claimed
- voice authenticity not claimed
- biometric identification not claimed
- emotion truth not claimed
- psychological diagnosis not claimed
- health inference not claimed
- campaign intelligence deferred to PS-037d
- transcript/timestamp cross-reference

The required de-escalation-pair strings are:

- proof does not equal truth
- provider choice does not equal provider availability
- voiceover artifact reference does not equal legal authenticity
- audio artifact does not equal voice authenticity
- provider voice output does not equal speaker identity
- emotion signal does not equal emotion truth
- local voice/audio evidence does not equal live ElevenLabs availability
- local voice/audio evidence does not equal live Hume availability
- demo/golden voice/audio evidence does not equal production security

The required negative-boundary strings are:

- not voice authenticity
- not speaker identity
- not biometric identification
- not emotion truth
- not psychological diagnosis
- not health inference
- not mental state diagnosis
- not semantic truth
- not legal authenticity
- not human authorship
- not C2PA authenticity
- not Object Lock
- not tamper-proof
- not browser-side B2 byte verification
- not live B2 availability
- not live ElevenLabs availability
- not live Hume availability
- not production security
- not identity verification
- not deepfake detection
- not content moderation
- not OCR correctness
- not transcript correctness
- not timestamp correctness
- not model output truth

The required posture / boundary strings are:

- no ElevenLabs API calls
- no Hume API calls
- no provider calls
- no live B2 reads
- no B2 writes
- no broad B2 scans
- no recursive smokes
- hidden Git flags h
- line[0]

The required evidence-report boolean keys are:

- `ok`
- `slice_id: ps037c`
- `voice_audio_choice_component_present`
- `voice_audio_choice_data_module_present`
- `voice_audio_choice_layer_present`
- `required_surfaces_have_voice_audio_choice_layer`
- `multimodal_proof_cross_reference_present`
- `transcript_timestamp_cross_reference_present`
- `trust_boundary_preserved`
- `provider_choice_present`
- `selected_voice_audio_evidence_path_present`
- `elevenlabs_voiceover_artifact_evidence_present`
- `hume_emotion_signal_evidence_present`
- `elevenlabs_label_present`
- `hume_label_present`
- `voiceover_artifact_evidence_present`
- `emotion_signal_evidence_present`
- `audio_artifact_present`
- `audio_artifact_reference_present`
- `audio_artifact_digest_present`
- `provider_output_reference_present_or_honestly_unavailable`
- `provider_output_digest_present_or_honestly_unavailable`
- `source_media_artifact_reference_present`
- `source_media_artifact_digest_present`
- `voice_audio_evidence_status_present`
- `voiceover_status_present`
- `emotion_signal_status_present`
- `provider_activity_status_present`
- `b2_evidence_status_present`
- `rehydrate_evidence_status_present`
- `local_verification_status_present`
- `live_verification_status_present`
- `disclosure_boundary_present`
- `not_claimed_status_present`
- `unknown_status_present`
- `local_demo_evidence_present`
- `live_provider_evidence_not_available_present`
- `elevenlabs_evidence_path_not_available_present`
- `hume_evidence_path_not_available_present`
- `voiceover_artifact_not_available_present`
- `emotion_signal_not_available_present`
- `speaker_identity_not_claimed_present`
- `voice_authenticity_not_claimed_present`
- `biometric_identification_not_claimed_present`
- `emotion_truth_not_claimed_present`
- `psychological_diagnosis_not_claimed_present`
- `health_inference_not_claimed_present`
- `campaign_intelligence_deferred_to_ps037d_present`
- `proof_does_not_equal_truth_present`
- `no_voice_authenticity_claim`
- `no_speaker_identity_claim`
- `no_biometric_identification_claim`
- `no_emotion_truth_claim`
- `no_psychological_diagnosis_claim`
- `no_health_inference_claim`
- `no_mental_state_diagnosis_claim`
- `no_semantic_truth_claim`
- `no_legal_authenticity_claim`
- `no_human_authorship_claim`
- `no_c2pa_authenticity_claim`
- `no_object_lock_claim`
- `no_tamper_proof_claim`
- `no_browser_side_b2_byte_verification_claim`
- `no_live_b2_availability_claim`
- `no_live_elevenlabs_availability_claim`
- `no_live_hume_availability_claim`
- `no_production_security_claim`
- `no_identity_verification_claim`
- `no_deepfake_detection_claim`
- `no_content_moderation_claim`
- `no_ocr_correctness_claim`
- `no_transcript_correctness_claim`
- `no_timestamp_correctness_claim`
- `no_model_output_truth_claim`
- `no_elevenlabs_api_calls`
- `no_hume_api_calls`
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

- `python scripts/proofstudio_regression_gate.py --current ps037c --frontend --report-out /tmp/proofstudio-release-report.json`
- `python scripts/proofstudio_regression_gate.py --current ps037c --no-frontend --report-out /tmp/proofstudio-ps037c-regression-report.json`
- `scripts/ps037c_voice_audio_evidence_provider_choice_smoke.py`
- `docs/evidence/ps-037c/voice-audio-evidence-provider-choice-report.json`
- `docs/ps-037c-voice-audio-evidence-provider-choice-layer-proof.md`
