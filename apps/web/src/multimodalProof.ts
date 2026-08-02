// PS-037a Multimodal Proof Layer -- canonical multimodal proof data module.
//
// This is the single, shared source of per-modality artifact-evidence framing
// for every core proof surface. It exists so a reviewer, client, or judge reads
// the SAME honest per-modality answer -- what media / artifact exists, what
// modality it belongs to, where the artifact reference is recorded, what hash /
// digest / manifest evidence is recorded, whether the artifact is local / demo /
// golden evidence or live evidence, whether provider activity happened, and
// whether transcript / timestamp / voice / emotion / campaign-intelligence
// evidence is absent, deferred, or later-slice owned -- on the Judge Cockpit
// Home, the B2 Evidence Explorer, the Manifest Verification Panel, the B2
// Rehydrate Comparison, the B2 Audit Vault, the Review + Approval Workspace, the
// Judge Evidence Pack, the Public Provenance Passport, and the Review Room.
//
// The layer is a proof-inspection layer over already-recorded evidence, not a
// new proof surface, not a new route, and not a new backend endpoint. It is
// purely client-side by default: it calls no provider, reads no B2 object,
// performs no browser-side B2 byte verification, performs no broad B2 scan, and
// writes no B2 object. It only reads accepted local / golden / demo data
// already captured by the pipeline and reuses the PS-037 disclosure concepts.
//
// PS-037a does not invent new media, new hashes, new transcripts, or new
// provider outputs. It states the existing recorded artifact evidence
// consistently and honestly, per modality.
//
// Truth boundary: ProofStudio proves what the pipeline recorded. The Multimodal
// Proof Layer is not a legal authenticity system, not a live B2 verifier, not a
// truth system, not an identity system, not a biometric system, not a deepfake
// detector, not a content moderator, not an OCR verifier, not a transcript
// verifier, not a timestamp verifier, not a voice verifier, and not an emotion
// verifier. It is not semantic truth, not legal authenticity, not human
// authorship, not C2PA authenticity, not Object Lock, not tamper-proof, not
// browser-side B2 byte verification, not live B2 availability, and not
// production security.

import {
  GOLDEN_DEMO_ARCHIVE_SHA256,
  GOLDEN_DEMO_ARCHIVE_URI,
  GOLDEN_DEMO_PROVIDER_CALLS_DURING_REHYDRATE,
  GOLDEN_DEMO_REHYDRATE_SOURCE,
} from "./b2Evidence";

// ---------------------------------------------------------------------------
// Layer identity (spec section 21). Verbatim.
// ---------------------------------------------------------------------------

export const MULTIMODAL_PROOF_LAYER_SLICE_ID = "PS-037a";
export const MULTIMODAL_PROOF_LAYER_TITLE = "Multimodal Proof Layer";

// One-line positioning statement. Surfaced by the summary variant and the panel
// header so the per-modality framing is identical on every core proof surface.
export const MULTIMODAL_PROOF_LAYER_POSITIONING =
  "ProofStudio proves what the pipeline recorded, per modality.";

// ---------------------------------------------------------------------------
// Read-only reuse of accepted checked-in artifact evidence.
//
// Archive URI, archive SHA-256, rehydrate source, and provider-call counts are
// sourced verbatim from apps/web/src/b2Evidence.ts (PS-026), which is itself
// traced to docs/evidence/demo/golden-demo-run.json (PS-024) and the PS-021 live
// B2 durable rehydrate smoke. The manifest URI / manifest hash are sourced
// verbatim from the same golden demo manifest (PS-035A). No value is invented
// here; PS-037a does not mutate these values.
// ---------------------------------------------------------------------------

// Recorded B2 archive reference for the golden demo run (PS-021 / PS-026).
export const MULTIMODAL_PROOF_ARCHIVE_URI = GOLDEN_DEMO_ARCHIVE_URI;

// Recorded SHA-256 digest of the B2 archive content for the golden demo run
// (PS-021 / PS-026). This is the artifact digest for the B2 archive modality.
export const MULTIMODAL_PROOF_ARCHIVE_SHA256 = GOLDEN_DEMO_ARCHIVE_SHA256;

// Recorded rehydrate source (durable_source = b2_rehydrated) from PS-021.
export const MULTIMODAL_PROOF_REHYDRATE_SOURCE = GOLDEN_DEMO_REHYDRATE_SOURCE;

// Recorded provider-call count during rehydrate (PS-021 proved zero).
export const MULTIMODAL_PROOF_PROVIDER_CALLS_DURING_REHYDRATE =
  GOLDEN_DEMO_PROVIDER_CALLS_DURING_REHYDRATE;

// Recorded manifest URI for the golden demo run (PS-035A). This is a
// checked-in local repo-relative fixture path, not a live B2 URL.
export const MULTIMODAL_PROOF_MANIFEST_URI =
  "docs/evidence/ps-035a/manifest-fixture.json";

// Recorded 64-hex manifest hash for the golden demo run (PS-035A). This is the
// independent SHA-256 recomputed over the exact bytes of the manifest fixture.
export const MULTIMODAL_PROOF_MANIFEST_HASH =
  "438fabca46481a232373067eedb6d0e3a684c8ed513410dfe2047e3b4950022f";

// The checked-in golden demo manifest the layer references (read-only).
export const MULTIMODAL_PROOF_GOLDEN_MANIFEST_PATH =
  "docs/evidence/demo/golden-demo-run.json";

// ---------------------------------------------------------------------------
// Canonical multimodal proof concepts (spec section 10.2 / 21). Verbatim.
// Surfaced as the concept labels on every core proof surface.
// ---------------------------------------------------------------------------

export const MULTIMODAL_PROOF_CONCEPTS: readonly string[] = [
  "artifact evidence",
  "modality",
  "media kind",
  "artifact reference",
  "artifact digest",
  "manifest reference",
  "manifest hash",
  "B2 evidence status",
  "rehydrate evidence status",
  "provider activity status",
  "local verification",
  "live verification status",
  "disclosure boundary",
  "not claimed",
  "unknown",
  "deferred to later slice",
];

// ---------------------------------------------------------------------------
// Modality set (spec section 10.4). The modalities that already exist in
// accepted checked-in evidence, plus honest "not available yet" states.
// ---------------------------------------------------------------------------

export type MultimodalModality =
  | "image"
  | "video"
  | "audio"
  | "text"
  | "manifest"
  | "b2 archive"
  | "rehydrate"
  | "export pack";

export type MultimodalProofState =
  | "recorded"
  | "locally_verified"
  | "recorded_only"
  | "not_verified"
  | "not_claimed"
  | "unknown"
  | "deferred_to_later_slice";

// ---------------------------------------------------------------------------
// Multimodal proof item shape (spec section 12.2). Derived from accepted data.
// ---------------------------------------------------------------------------

export interface MultimodalProofItem {
  modality: MultimodalModality;
  // media_kind: the concrete media kind recorded, or honestly "not available
  // yet".
  media_kind: string;
  // artifact_reference: where the reference is recorded, or honestly
  // unavailable.
  artifact_reference: string;
  // artifact_digest: the recorded hash / digest, or honestly unavailable.
  artifact_digest: string;
  // manifest_reference: the recorded manifest_uri, or honestly unavailable.
  manifest_reference: string;
  // manifest_hash: the recorded 64-hex manifest_hash, or honestly unavailable.
  manifest_hash: string;
  // b2_evidence_status: recorded-only by default.
  b2_evidence_status: string;
  // rehydrate_evidence_status: whether rehydrate evidence is recorded.
  rehydrate_evidence_status: string;
  // provider_activity_status: no provider calls by default.
  provider_activity_status: string;
  // local_verification: locally verified against accepted checked-in data.
  local_verification: string;
  // live_verification_status: local / check-only by default.
  live_verification_status: string;
  // disclosure_boundary: per-modality disclosure boundary (consistent with
  // PS-037).
  disclosure_boundary: string;
  // state: one of the canonical states.
  state: MultimodalProofState;
}

// Honest per-modality artifact evidence. Image / video / audio raw media bytes
// are NOT checked into accepted evidence, so those modalities honestly surface
// "not available yet" / "unknown" states rather than fabricated references or
// digests. Text / manifest / B2 archive / rehydrate / export pack evidence is
// recorded in accepted checked-in data.
export const MULTIMODAL_PROOF_ITEMS: readonly MultimodalProofItem[] = [
  {
    modality: "image",
    media_kind: "image",
    artifact_reference:
      "not available yet (raw image bytes not checked into accepted evidence)",
    artifact_digest: "unknown",
    manifest_reference: "not available yet",
    manifest_hash: "not available yet",
    b2_evidence_status: "not applicable",
    rehydrate_evidence_status: "not applicable",
    provider_activity_status: "no provider calls",
    local_verification: "not verified (artifact evidence not available yet)",
    live_verification_status: "local / check-only",
    disclosure_boundary: "unknown",
    state: "unknown",
  },
  {
    modality: "video",
    media_kind: "video",
    artifact_reference:
      "not available yet (raw video bytes not checked into accepted evidence)",
    artifact_digest: "unknown",
    manifest_reference: "not available yet",
    manifest_hash: "not available yet",
    b2_evidence_status: "not applicable",
    rehydrate_evidence_status: "not applicable",
    provider_activity_status: "no provider calls",
    local_verification: "not verified (artifact evidence not available yet)",
    live_verification_status: "local / check-only",
    disclosure_boundary: "unknown",
    state: "unknown",
  },
  {
    modality: "audio",
    media_kind: "audio",
    artifact_reference:
      "not available yet (raw audio bytes not checked into accepted evidence)",
    artifact_digest: "unknown",
    manifest_reference: "not available yet",
    manifest_hash: "not available yet",
    b2_evidence_status: "not applicable",
    rehydrate_evidence_status: "not applicable",
    provider_activity_status: "no provider calls",
    local_verification: "not verified (artifact evidence not available yet)",
    live_verification_status: "local / check-only",
    disclosure_boundary: "deferred to later slice (voice / emotion)",
    state: "unknown",
  },
  {
    modality: "text",
    media_kind: "text / JSON evidence",
    artifact_reference: MULTIMODAL_PROOF_GOLDEN_MANIFEST_PATH,
    artifact_digest: "not available yet (digest not recorded for this artifact)",
    manifest_reference: MULTIMODAL_PROOF_MANIFEST_URI,
    manifest_hash: MULTIMODAL_PROOF_MANIFEST_HASH,
    b2_evidence_status: "recorded-only",
    rehydrate_evidence_status: "not applicable",
    provider_activity_status: "no provider calls",
    local_verification: "locally verified (checked-in evidence)",
    live_verification_status: "local / check-only",
    disclosure_boundary: "media hash does not equal semantic truth",
    state: "locally_verified",
  },
  {
    modality: "manifest",
    media_kind: "manifest (Genblaze JSON fixture)",
    artifact_reference: MULTIMODAL_PROOF_MANIFEST_URI,
    artifact_digest: MULTIMODAL_PROOF_MANIFEST_HASH,
    manifest_reference: MULTIMODAL_PROOF_MANIFEST_URI,
    manifest_hash: MULTIMODAL_PROOF_MANIFEST_HASH,
    b2_evidence_status: "recorded-only",
    rehydrate_evidence_status: "not applicable",
    provider_activity_status: "no provider calls",
    local_verification: "locally verified (checked-in fixture)",
    live_verification_status: "local / check-only",
    disclosure_boundary: "manifest hash does not equal human authorship",
    state: "locally_verified",
  },
  {
    modality: "b2 archive",
    media_kind: "run archive (JSON)",
    artifact_reference: MULTIMODAL_PROOF_ARCHIVE_URI,
    artifact_digest: MULTIMODAL_PROOF_ARCHIVE_SHA256,
    manifest_reference: "not applicable",
    manifest_hash: "not applicable",
    b2_evidence_status: "recorded-only (B2 evidence referenced, not live-verified)",
    rehydrate_evidence_status: "recorded (b2_rehydrated)",
    provider_activity_status:
      "no provider calls during rehydrate (" +
      String(MULTIMODAL_PROOF_PROVIDER_CALLS_DURING_REHYDRATE) +
      ")",
    local_verification: "locally verified (checked-in evidence)",
    live_verification_status: "local / check-only",
    disclosure_boundary: "artifact reference does not equal legal authenticity",
    state: "recorded_only",
  },
  {
    modality: "rehydrate",
    media_kind: "rehydrated run archive",
    artifact_reference: MULTIMODAL_PROOF_ARCHIVE_URI,
    artifact_digest: MULTIMODAL_PROOF_ARCHIVE_SHA256,
    manifest_reference: "not applicable",
    manifest_hash: "not applicable",
    b2_evidence_status: "recorded-only",
    rehydrate_evidence_status:
      "recorded (b2_rehydrated, zero provider calls)",
    provider_activity_status: "no provider calls",
    local_verification: "locally verified (checked-in evidence)",
    live_verification_status: "local / check-only",
    disclosure_boundary:
      "local artifact evidence does not equal live B2 availability",
    state: "locally_verified",
  },
  {
    modality: "export pack",
    media_kind: "judge evidence pack (JSON / Markdown)",
    artifact_reference:
      "docs/ps-031-export-campaign-pack-v2-proof.md / local browser export",
    artifact_digest: "not available yet (digest not recorded for the pack)",
    manifest_reference: "not applicable",
    manifest_hash: "not applicable",
    b2_evidence_status: "not applicable",
    rehydrate_evidence_status: "not applicable",
    provider_activity_status: "no provider calls",
    local_verification: "locally verified (local browser export)",
    live_verification_status: "local / check-only",
    disclosure_boundary: "demo/golden artifact does not equal production security",
    state: "locally_verified",
  },
];

// ---------------------------------------------------------------------------
// Required deferred later-slice states (spec section 10.6 / 21). Verbatim.
//
// These are non-claim states: they state what is not available yet, owned by a
// later slice, and must never be read as a hidden proof. PS-037a must not fake
// a transcript, a timestamp, a voiceover, a voice / emotion analysis, or a
// campaign intelligence / judge narrative.
// ---------------------------------------------------------------------------

export const MULTIMODAL_PROOF_DEFERRED_HEADING = "deferred to later slice";

export const MULTIMODAL_PROOF_DEFERRED_STATES: readonly string[] = [
  "transcript evidence not available",
  "timestamp evidence not available",
  "voice evidence not available",
  "emotion evidence not available",
  "campaign intelligence not available",
];

// The later slice that owns each deferred state. Surfaced so no reviewer
// mistakes an absent proof for a hidden proof.
export const MULTIMODAL_PROOF_DEFERRED_OWNERS: readonly string[] = [
  "transcript evidence not available -> deferred to later slice (PS-037b AssemblyAI transcript / timestamp)",
  "timestamp evidence not available -> deferred to later slice (PS-037b AssemblyAI transcript / timestamp)",
  "voice evidence not available -> deferred to later slice (PS-037c Hume / ElevenLabs voiceover)",
  "emotion evidence not available -> deferred to later slice (PS-037c Hume / ElevenLabs voiceover)",
  "campaign intelligence not available -> deferred to later slice (PS-037d Gemini campaign intelligence / judge narrative)",
];

// ---------------------------------------------------------------------------
// Required de-escalation pairs (spec section 10.7 / 21). Surfaced verbatim so
// a judge never mistakes a strong-sounding artifact for a stronger guarantee.
// Stated as non-claims so context-aware forbidden-claim scanners never flag
// these boundary terms as overclaims.
// ---------------------------------------------------------------------------

export const MULTIMODAL_PROOF_DEESCALATION_PAIRS: readonly string[] = [
  "proof does not equal truth",
  "artifact reference does not equal legal authenticity",
  "media hash does not equal semantic truth",
  "manifest hash does not equal human authorship",
  "local artifact evidence does not equal live B2 availability",
  "demo/golden artifact does not equal production security",
];

// ---------------------------------------------------------------------------
// Required negative boundary strings (spec section 10.8 / 21). Surfaced
// verbatim. These are the canonical "not claimed" set rendered as pills.
// ---------------------------------------------------------------------------

export const MULTIMODAL_PROOF_NEGATIVE_BOUNDARY: readonly string[] = [
  "not semantic truth",
  "not legal authenticity",
  "not human authorship",
  "not C2PA authenticity",
  "not Object Lock",
  "not tamper-proof",
  "not browser-side B2 byte verification",
  "not live B2 availability",
  "not production security",
  "not identity verification",
  "not biometric identification",
  "not deepfake detection",
  "not content moderation",
  "not OCR correctness",
  "not transcript correctness",
  "not timestamp correctness",
  "not voice authenticity",
  "not emotion truth",
  "not model output truth",
];

// ---------------------------------------------------------------------------
// Persistent per-modality boundary statement (spec section 11). Verbatim.
// Written as non-claim copy so the project's forbidden-claim scanners never
// flag the boundary terms.
// ---------------------------------------------------------------------------

export const MULTIMODAL_PROOF_PERSISTENT_STATEMENT =
  "ProofStudio proves what the pipeline recorded. " +
  "Proof does not equal truth. " +
  "An artifact reference does not equal legal authenticity. " +
  "A media hash does not equal semantic truth. " +
  "A manifest hash does not equal human authorship. " +
  "Local artifact evidence does not equal live B2 availability. " +
  "A demo/golden artifact does not equal production security.";

// Compact one-line summary used by the summary variant.
export const MULTIMODAL_PROOF_SUMMARY =
  "Multimodal Proof Layer: artifact evidence across image, video, audio, text, " +
  "manifest, B2 archive, rehydrate, and export pack; proof does not equal truth.";

// ---------------------------------------------------------------------------
// Truth-boundary posture (spec section 10.1). Surfaced so the disclosure
// contract is deterministic and auditable. These are non-claim posture notes.
// ---------------------------------------------------------------------------

export const MULTIMODAL_PROOF_POSTURE: readonly string[] = [
  "no provider calls",
  "no live B2 reads",
  "no B2 writes",
  "no broad B2 scans",
  "local / static by default",
];

// ---------------------------------------------------------------------------
// Required core proof surfaces (spec section 10.3). Listed so the multimodal
// proof contract documents exactly where the shared layer is rendered.
// ---------------------------------------------------------------------------

export const MULTIMODAL_PROOF_REQUIRED_SURFACES: readonly string[] = [
  "Judge Cockpit Home",
  "B2 Evidence Explorer",
  "Manifest Verification Panel",
  "B2 Rehydrate Comparison",
  "Archive / Rehydrate / B2 Audit Vault",
  "Review + Approval Workspace",
  "Judge Evidence Pack",
  "Public Provenance Passport",
  "Review Room",
];
