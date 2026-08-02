# PS-037b — AssemblyAI Transcript/Timestamp Evidence

## Status

PS-037b — AssemblyAI Transcript/Timestamp Evidence is implemented as a
reusable, additive transcript/timestamp evidence-inspection layer over
already-recorded or honestly-unavailable data. It is local / static by
default: it makes no AssemblyAI API call, calls no provider, reads no live B2
object, performs no browser-side B2 byte verification, performs no broad B2
scan, writes no B2 object, and adds no backend endpoint. It reads only
accepted local / golden / demo data and existing accepted data modules.

## What it is

The AssemblyAI Transcript/Timestamp Evidence layer is one shared, canonical
data module (`apps/web/src/assemblyAITranscriptEvidence.ts`) plus one shared
component (`apps/web/src/TranscriptTimestampEvidenceLayer.tsx`) rendered
additively on every core proof surface. It makes the transcript/timestamp
framing of evidence consistent across the Judge Cockpit Home, the B2 Evidence
Explorer, the Manifest Verification Panel, the B2 Rehydrate Comparison, the
B2 Audit Vault, the Review + Approval Workspace, the Judge Evidence Pack, the
Public Provenance Passport, and the Review Room. It is a transcript/timestamp
evidence-inspection layer, not a new proof surface, not a new route, and not a
new backend endpoint.

AssemblyAI is named as the transcript/timestamp provider for evidence labeling
only. Naming AssemblyAI does not imply a live AssemblyAI API call, live
AssemblyAI availability, transcript correctness, timestamp correctness,
speaker identity correctness, or any correctness guarantee over what the
pipeline recorded.

It integrates with the PS-037 Disclosure & Trust Boundary Layer: it renders
alongside `TrustBoundaryLayer`, reuses the shared disclosure concepts, and
never contradicts the PS-037 boundary. It integrates / cross-references the
PS-037a Multimodal Proof Layer: it renders alongside `MultimodalProofLayer`,
supplies the concrete transcript/timestamp evidence that PS-037a only reserved
as "transcript evidence not available" / "timestamp evidence not available",
and never contradicts or removes the PS-037a deferred states. Existing
per-surface truth-boundary panels and artifact records are preserved
unchanged; the transcript/timestamp layer is additive.

## Transcript/timestamp evidence

PS-037b owns transcript/timestamp evidence only. For each concept the layer
records honestly whether evidence exists in accepted checked-in data, whether
it is local / demo / golden evidence or live provider evidence, and what it
proves and does not prove:

- transcript evidence — honestly `not_available` (no transcript artifact
  checked into accepted evidence); honest "transcript evidence not available"
  state. No fabricated transcript.
- timestamp evidence — honestly `not_available` (no timestamp / word timing /
  utterance timing checked into accepted evidence); honest "timestamp evidence
  not available" state. No fabricated timestamp segments.
- transcript artifact — honest "transcript evidence not available" state. No
  fabricated transcript artifact.
- transcript artifact reference — honest "transcript evidence not available"
  state (no transcript artifact reference recorded).
- transcript artifact digest — honest "transcript evidence not available"
  state (no transcript artifact digest recorded).
- transcript provider — AssemblyAI (named as transcript provider for evidence
  labeling only; no live AssemblyAI API call).
- media artifact reference — the recorded golden demo archive reference
  (`archive_uri`, PS-021 / PS-026), recorded-only (referenced, not
  live-verified here).
- media artifact digest — the recorded golden demo archive SHA-256
  (`archive_sha256`, PS-021 / PS-026), recorded-only.
- timestamp segments — honest "timestamp evidence not available" state.
- word timing evidence — honest "timestamp evidence not available" state.
- utterance timing evidence — honest "timestamp evidence not available" state.
- transcript status — `not_available`.
- timestamp status — `not_available`.
- transcript verification status — `unavailable`.
- timestamp verification status — `unavailable`.
- B2 evidence status — `recorded-only` (B2 evidence referenced, not
  live-verified here).
- rehydrate evidence status — recorded (`b2_rehydrated`, zero provider calls
  during rehydrate, PS-021).
- provider activity status — no provider calls (no live AssemblyAI API call;
  local/demo evidence by default).
- local verification — local/demo evidence (locally checked-in golden / demo
  data; not live-verified).
- live verification status — live provider evidence not available (local /
  check-only by default).
- disclosure boundary — the transcript/timestamp disclosure boundary,
  consistent with PS-037.
- not claimed — the honest set of things ProofStudio does not claim for
  transcript/timestamp evidence.
- unknown — what remains unknown or not surfaced for transcript/timestamp
  evidence.
- local/demo evidence — the default posture (local / golden / demo fixture
  evidence, not live provider evidence).

## Honest unavailable / not-claimed / deferred states (verbatim)

PS-037b does not fake any transcript, timestamp, speaker label, word timing,
utterance timing, voice analysis, emotion analysis, campaign intelligence, or
provider output. It reserves these honest non-claim states verbatim:

- local/demo evidence
- live provider evidence not available
- transcript evidence not available
- timestamp evidence not available
- speaker identity not claimed
- voice authenticity not claimed
- emotion evidence deferred to PS-037c
- campaign intelligence deferred to PS-037d

These are non-claims. An absent transcript / timestamp / speaker-identity /
voice-authenticity / emotion / campaign-intelligence proof is stated, never
hidden, and never faked.

## De-escalation pairs (verbatim)

- proof does not equal truth
- transcript artifact reference does not equal legal authenticity
- transcript text does not equal semantic truth
- timestamp evidence does not equal timestamp correctness
- provider transcript does not equal speaker identity
- local transcript evidence does not equal live AssemblyAI availability
- demo/golden transcript evidence does not equal production security

## Negative boundary (verbatim)

not transcript correctness · not timestamp correctness · not speaker identity ·
not voice authenticity · not semantic truth · not legal authenticity · not
human authorship · not C2PA authenticity · not Object Lock · not tamper-proof ·
not browser-side B2 byte verification · not live B2 availability · not live
AssemblyAI availability · not production security · not identity verification ·
not biometric identification · not deepfake detection · not content moderation ·
not OCR correctness · not emotion truth · not model output truth.

## Truth boundary

ProofStudio proves what the pipeline recorded. The AssemblyAI Transcript/
Timestamp Evidence layer is not a legal authenticity system, not a live B2
verifier, not a truth system, not an identity system, not a biometric system,
not a speaker-identity system, not a deepfake detector, not a content
moderator, not an OCR verifier, not a transcript-correctness verifier, not a
timestamp-correctness verifier, not a voice verifier, not an emotion verifier,
and not a live AssemblyAI verifier. The layer does not claim transcript
correctness, timestamp correctness, speaker identity, semantic truth, legal
authenticity, human authorship, C2PA authenticity, Object Lock / tamper-proof
storage, browser-side B2 byte verification, live B2 availability, live
AssemblyAI availability, production security, identity verification, biometric
identification, deepfake detection, content moderation, OCR correctness, voice
authenticity, emotion truth, or model output truth.

## Posture

no AssemblyAI API calls · no provider calls · no live B2 reads · no B2 writes ·
no broad B2 scans · local / static by default.

## Validation

- Feature smoke: `scripts/ps037b_assemblyai_transcript_timestamp_evidence_smoke.py`
  (default `--check-only`; writes only `docs/evidence/ps-037b/` when
  `--write-evidence` is explicit).
- Evidence: `docs/evidence/ps-037b/assemblyai-transcript-timestamp-evidence-report.json`.
- Contract-only gate:
  `python scripts/proofstudio_regression_gate.py --current ps037b --no-frontend --report-out /tmp/proofstudio-ps037b-regression-report.json`
