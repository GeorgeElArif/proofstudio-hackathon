# PS-037c — Voice/Audio Evidence Provider Choice Layer (Proof)

## 1. What PS-037c adds

PS-037c adds a reusable **Voice/Audio Evidence Provider Choice Layer** that
exposes a customer-selectable voice/audio evidence path consistently on every
core proof surface. It is a provider-choice layer by design: it is **not**
ElevenLabs-only and **not** Hume-only. It supports two evidence tracks the
customer can choose between:

1. **ElevenLabs Voiceover Artifact Evidence** (provider: ElevenLabs)
2. **Hume Emotion-Signal Evidence** (provider: Hume)

The layer makes the voice/audio provider-choice framing identical everywhere
voice/audio evidence is shown. A reviewer or judge can immediately read:

- which voice/audio evidence path is selected
- whether the selected path is ElevenLabs Voiceover Artifact Evidence or Hume
  Emotion-Signal Evidence
- whether voiceover artifact evidence exists
- whether emotion-signal evidence exists
- what audio artifact the evidence relates to
- what source media artifact the evidence relates to
- what provider is named for voice/audio evidence labeling (ElevenLabs or Hume)
- whether the evidence is local / demo / golden fixture evidence or live
  provider evidence
- where the audio artifact reference / digest is recorded
- where the provider output reference / digest is recorded (if available)
- whether provider activity happened
- whether B2 / rehydrate evidence exists for the audio artifact
- whether transcript/timestamp evidence from PS-037b cross-references the
  audio artifact
- whether voice authenticity, speaker identity, biometric identity, emotion
  truth, psychological diagnosis, or health inference is claimed

PS-037c proves what the pipeline recorded. It is a voice/audio evidence
inspection layer over already-recorded or honestly-unavailable data, not a new
proof surface, not a new route, not a new backend endpoint, not a live provider
integration, and not a voice-generation or emotion-inference system.

## 2. Files changed

New files (PS-037c owned):

- `apps/web/src/voiceAudioEvidenceChoice.ts` — the canonical camelCase
  voice/audio evidence provider choice data module.
- `apps/web/src/VoiceAudioEvidenceChoiceLayer.tsx` — the shared
  voice/audio evidence provider choice component (`variant="panel"` /
  `variant="summary"`).
- `scripts/ps037c_voice_audio_evidence_provider_choice_smoke.py` — the
  PS-037c feature smoke.
- `docs/ps-037c-voice-audio-evidence-provider-choice-layer-proof.md` — this
  proof doc.
- `docs/evidence/ps-037c/voice-audio-evidence-provider-choice-report.json` —
  the only evidence PS-037c may write, and only when `--write-evidence` is
  explicit.

Additive edits (existing files, additive only):

- `apps/web/src/App.tsx` — render the voice/audio evidence provider choice
  layer on the Review Room.
- `apps/web/src/JudgeCockpitHome.tsx` — render the layer on the home surface.
- `apps/web/src/B2EvidenceExplorer.tsx` — render the layer (B2 evidence status
  for the audio artifact).
- `apps/web/src/B2RehydrateComparison.tsx` — render the layer (rehydrate
  evidence status for the audio artifact).
- `apps/web/src/ManifestVerificationPanel.tsx` — render the layer (source media
  artifact reference / digest modalities).
- `apps/web/src/B2AuditVault.tsx` — render the layer (B2 / rehydrate audit for
  the audio artifact).
- `apps/web/src/ReviewApprovalWorkspace.tsx` — render the layer (reviewable
  artifact voice/audio evidence provider choice).
- `apps/web/src/JudgeEvidencePack.tsx` — render the layer (export-pack audio
  artifact summary).
- `apps/web/src/PublicPassportPage.tsx` — render the layer (provenance
  passport voice/audio evidence).
- `apps/web/src/styles.css` — additive `.voice-audio-evidence-choice-layer*`
  classes only. No existing class is removed or weakened.

## 3. How provider choice works

The layer exposes a `provider choice` between two evidence tracks. Each track
carries its honest present / not available / not claimed / unknown status. The
`selected voice/audio evidence path` records which track is chosen, honestly
surfaced. Because no voiceover artifact, emotion signal, audio artifact
reference, audio artifact digest, provider output reference, or provider output
digest is checked into accepted evidence, the default selected path is
honestly surfaced as `not_available` with `local/demo evidence` as the default
posture, and `live provider evidence not available` as the default live state.

The layer cross-references the PS-037a Multimodal Proof Layer (fills the
concrete voice/audio provider-choice evidence PS-037a reserved as `voice
evidence not available` / `emotion evidence not available`) and the PS-037b
Transcript/Timestamp Evidence layer (surfaces an honest
transcript/timestamp cross-reference indicator).

## 4. Why provider choice does not equal provider availability

Naming ElevenLabs or Hume is **evidence labeling only**. It does not imply a
live provider call, live provider availability, a voice-generation guarantee,
an emotion-inference guarantee, or any correctness guarantee over what the
pipeline recorded. The default posture is `local/demo evidence` with
`live provider evidence not available`, `ElevenLabs evidence path not
available`, and `Hume evidence path not available`. No live ElevenLabs path and
no live Hume path exists in PS-037c. A live-provider path may only be enabled
by a later PM-approved slice with cost controls, env gates, and evidence
boundaries.

## 5. Why ElevenLabs / Hume are evidence labels only in this slice

PS-037c is a customer-selectable voice/audio evidence provider choice layer.
ElevenLabs is named as the selectable provider for the Voiceover Artifact
Evidence track; Hume is named as the selectable provider for the
Emotion-Signal Evidence track. Both names exist so a reviewer can read which
provider a given evidence track is labeled against. Neither name is a live
call, neither name is an availability claim, and neither name is a correctness
claim. The persistent voice/audio boundary statement is surfaced verbatim on
every surface.

## 6. Local / static default; no live provider / API / B2 behavior

PS-037c is purely client-side by default. It makes:

- no ElevenLabs API calls
- no Hume API calls
- no provider calls
- no live B2 reads
- no B2 writes
- no broad B2 scans

It reads only accepted local / golden / demo data and existing accepted data
modules, or surfaces explicit honest "not available" / "not claimed" /
"unknown" states. The PS-037c smoke is local / static by default
(`--check-only`) and writes only `docs/evidence/ps-037c/` evidence when
`--write-evidence` is explicit.

## 7. PS-037 / PS-037a / PS-037b preservation and cross-reference

- **PS-037 Disclosure + Trust Boundary Layer** — preserved. The
  voice/audio provider-choice layer renders alongside `TrustBoundaryLayer`,
  reuses the shared disclosure concepts, and never contradicts the PS-037
  boundary.
- **PS-037a Multimodal Proof Layer** — preserved and cross-referenced. The
  layer renders alongside `MultimodalProofLayer` and fills the concrete
  voice/audio provider-choice evidence PS-037a only reserved as deferred; it
  does not duplicate, weaken, or remove the PS-037a deferred voice/emotion
  states.
- **PS-037b Transcript/Timestamp Evidence layer** — preserved and
  cross-referenced. The layer renders alongside
  `TranscriptTimestampEvidenceLayer` and surfaces an honest
  transcript/timestamp cross-reference indicator; it does not duplicate or
  weaken the PS-037b contract.

The `.trust-boundary-layer*` (PS-037), `.multimodal-proof-layer*` (PS-037a),
and `.transcript-timestamp-evidence-layer*` (PS-037b) classes are untouched.
The PS-037c styles are purely additive `.voice-audio-evidence-choice-layer*`
classes.

## 8. Validation commands and results

```
python scripts/ps037c_voice_audio_evidence_provider_choice_smoke.py --check-only --no-frontend
python scripts/ps037c_voice_audio_evidence_provider_choice_smoke.py --write-evidence --no-frontend
python scripts/proofstudio_regression_gate.py --current ps037c --no-frontend --report-out /tmp/proofstudio-ps037c-regression-report.json
cd apps/web && npx tsc --noEmit
git ls-files -v   # h/S hidden flag check on line[0]
git diff --check
```

Prior evidence outside `docs/evidence/ps-037c/` is unchanged. No staging,
commit, or push was performed.

## 9. Truth boundary / negative claims

ProofStudio proves what the pipeline recorded for voice/audio evidence. Proof
does not equal truth. Provider choice does not equal provider availability. A
voiceover artifact reference does not equal legal authenticity. An audio
artifact does not equal voice authenticity. A provider voice output does not
equal speaker identity. An emotion signal does not equal emotion truth. Local
voice/audio evidence does not equal live ElevenLabs availability. Local
voice/audio evidence does not equal live Hume availability. Demo/golden
voice/audio evidence does not equal production security.

PS-037c does not claim voice authenticity, speaker identity, biometric
identification, emotion truth, psychological diagnosis, mental state
diagnosis, health inference, semantic truth, legal authenticity, human
authorship, C2PA authenticity, Object Lock, tamper-proof storage,
browser-side B2 byte verification, live B2 availability, live ElevenLabs
availability, live Hume availability, production security, identity
verification, deepfake detection, content moderation, OCR correctness,
transcript correctness, timestamp correctness, or model output truth. The
canonical negative boundary strings and de-escalation pairs are surfaced
verbatim on every core proof surface and in the PS-037c evidence report.

Campaign intelligence is deferred to PS-037d (Gemini Campaign Intelligence /
Judge Narrative). PS-037c only reserves an honest "campaign intelligence
deferred to PS-037d" state; it does not produce, store, or claim a campaign
intelligence output or a judge narrative.
