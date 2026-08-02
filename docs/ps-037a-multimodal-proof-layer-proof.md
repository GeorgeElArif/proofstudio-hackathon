# PS-037a — Multimodal Proof Layer

## Status

PS-037a — Multimodal Proof Layer is implemented as a reusable, additive
multodal proof-inspection layer over already-recorded artifact evidence. It is
local / static by default: it makes no provider call, reads no live B2 object,
performs no browser-side B2 byte verification, performs no broad B2 scan, writes
no B2 object, and adds no backend endpoint. It reads only accepted local /
golden / demo data and existing accepted data modules.

## What it is

The Multimodal Proof Layer is one shared, canonical data module
(`apps/web/src/multimodalProof.ts`) plus one shared component
(`apps/web/src/MultimodalProofLayer.tsx`) rendered additively on every core
proof surface. It makes the per-modality framing of artifact evidence consistent
across image, video, audio, text, manifest, B2 archive, rehydrate, and export
pack evidence. It is a proof-inspection layer, not a new proof surface, not a
new route, and not a new backend endpoint.

It integrates with the PS-037 Disclosure & Trust Boundary Layer: it renders
alongside `TrustBoundaryLayer`, reuses the shared disclosure concepts, and never
contradicts the PS-037 boundary. Existing per-surface truth-boundary panels and
artifact records are preserved unchanged; the multimodal layer is additive.

## Per-modality artifact evidence

For each modality the layer records honestly whether artifact evidence exists in
accepted checked-in data, whether it is local / demo / golden evidence or live
evidence, and what it proves and does not prove:

- `image` — raw image bytes are not checked into accepted evidence; honest
  "not available yet" / "unknown" state. No fabricated reference or digest.
- `video` — raw video bytes are not checked into accepted evidence; honest
  "not available yet" / "unknown" state.
- `audio` — raw audio bytes are not checked into accepted evidence; honest
  "not available yet" / "unknown" state, with voice / emotion deferred to a
  later slice.
- `text` — the checked-in golden demo manifest / JSON evidence is locally
  verified (recorded-only, not live-verified).
- `manifest` — the recorded manifest reference (`manifest_uri`) and the recorded
  64-hex `manifest_hash` (PS-035A), locally verified against the checked-in
  fixture.
- `b2 archive` — the recorded archive reference (`archive_uri`) and the recorded
  artifact digest (`archive_sha256`, PS-021 / PS-026), recorded-only (referenced,
  not live-verified here).
- `rehydrate` — the recorded rehydrate evidence status (`b2_rehydrated`, zero
  provider calls during rehydrate, PS-021), locally verified against checked-in
  evidence.
- `export pack` — the local browser judge evidence pack (PS-031), locally
  verified; no raw media bytes are included.

## Honest deferred later-slice states (verbatim)

PS-037a does not fake any later-slice provider output. It reserves these honest
non-claim states verbatim:

- transcript evidence not available (deferred to later slice — PS-037b)
- timestamp evidence not available (deferred to later slice — PS-037b)
- voice evidence not available (deferred to later slice — PS-037c)
- emotion evidence not available (deferred to later slice — PS-037c)
- campaign intelligence not available (deferred to later slice — PS-037d)

These are non-claims. An absent transcript / timestamp / voice / emotion /
campaign-intelligence proof is stated, never hidden, and never faked.

## De-escalation pairs (verbatim)

- proof does not equal truth
- artifact reference does not equal legal authenticity
- media hash does not equal semantic truth
- manifest hash does not equal human authorship
- local artifact evidence does not equal live B2 availability
- demo/golden artifact does not equal production security

## Negative boundary (verbatim)

not semantic truth · not legal authenticity · not human authorship · not C2PA
authenticity · not Object Lock · not tamper-proof · not browser-side B2 byte
verification · not live B2 availability · not production security · not identity
verification · not biometric identification · not deepfake detection · not
content moderation · not OCR correctness · not transcript correctness · not
timestamp correctness · not voice authenticity · not emotion truth · not model
output truth.

## Truth boundary

ProofStudio proves what the pipeline recorded. The Multimodal Proof Layer is not
a legal authenticity system, not a live B2 verifier, not a truth system, not an
identity system, not a biometric system, not a deepfake detector, not a content
moderator, not an OCR verifier, not a transcript verifier, not a timestamp
verifier, not a voice verifier, and not an emotion verifier. The layer does not
claim semantic truth, legal authenticity, human authorship, C2PA authenticity,
Object Lock / tamper-proof storage, browser-side B2 byte verification, live B2
availability, production security, identity verification, biometric
identification, deepfake detection, content moderation, OCR correctness,
transcript correctness, timestamp correctness, voice authenticity, emotion truth,
or model output truth.

## Posture

no provider calls · no live B2 reads · no B2 writes · no broad B2 scans · local
/ static by default.

## Validation

- Feature smoke: `scripts/ps037a_multimodal_proof_layer_smoke.py` (default
  `--check-only`; writes only `docs/evidence/ps-037a/` when `--write-evidence` is
  explicit).
- Evidence: `docs/evidence/ps-037a/multimodal-proof-layer-report.json`.
- Contract-only gate:
  `python scripts/proofstudio_regression_gate.py --current ps037a --no-frontend --report-out /tmp/proofstudio-ps037a-regression-report.json`
