// PS-037c Voice/Audio Evidence Provider Choice Layer -- canonical data module.
//
// This is the single, shared source of voice/audio evidence provider choice
// framing for every core proof surface. It exists so a reviewer, client, or
// judge reads the SAME honest voice/audio answer -- which voice/audio evidence
// path is selected, whether the selected path is ElevenLabs Voiceover Artifact
// Evidence or Hume Emotion-Signal Evidence, whether voiceover artifact evidence
// exists, whether emotion-signal evidence exists, what audio artifact the
// evidence relates to, what source media artifact the evidence relates to, what
// provider is named for voice/audio evidence labeling (ElevenLabs or Hume),
// whether the evidence is local / demo / golden fixture evidence or live
// provider evidence, where the audio artifact reference is recorded, where the
// audio artifact digest is recorded, where provider output reference / digest
// is recorded (if available), whether provider activity happened, whether B2 /
// rehydrate evidence exists for the audio artifact, whether
// transcript/timestamp evidence from PS-037b cross-references the audio
// artifact, and whether voice authenticity, speaker identity, biometric
// identity, emotion truth, psychological diagnosis, or health inference is
// claimed -- on the Judge Cockpit Home, the B2 Evidence Explorer, the Manifest
// Verification Panel, the B2 Rehydrate Comparison, the B2 Audit Vault, the
// Review + Approval Workspace, the Judge Evidence Pack, the Public Provenance
// Passport, and the Review Room.
//
// The layer is a voice/audio evidence provider choice layer over
// already-recorded or honestly-unavailable data, not a new proof surface, not
// a new route, and not a new backend endpoint. It is purely client-side by
// default: it makes no ElevenLabs API call, makes no Hume API call, calls no
// provider, reads no B2 object, performs no browser-side B2 byte verification,
// performs no broad B2 scan, and writes no B2 object. It only reads accepted
// local / golden / demo data and existing accepted data modules, and reuses the
// PS-037 disclosure concepts, the PS-037a multimodal proof framing, and the
// PS-037b transcript/timestamp evidence framing.
//
// ElevenLabs and Hume are named as selectable evidence providers for evidence
// labeling only. Naming ElevenLabs or Hume does not imply a live provider call,
// live provider availability, voice authenticity, speaker identity, emotion
// truth, or any correctness guarantee over what the pipeline recorded.
// Provider choice does not equal provider availability.
//
// PS-037c does not invent new voiceovers, new emotion signals, new voice
// analyses, new emotion analyses, new voice clones, or new provider outputs. It
// states the existing recorded voice/audio evidence consistently and honestly,
// and surfaces explicit honest "not available" / "not claimed" / "unknown"
// states where no evidence exists.
//
// Truth boundary: ProofStudio proves what the pipeline recorded. The Voice/Audio
// Evidence Provider Choice Layer is not a legal authenticity system, not a live
// B2 verifier, not a truth system, not an identity system, not a biometric
// system, not a speaker-identity system, not a voice-authenticity system, not
// an emotion-truth system, not a psychological-diagnosis system, not a
// health-inference system, not a deepfake detector, not a content moderator,
// not an OCR verifier, not a transcript verifier, not a timestamp verifier, not
// a live ElevenLabs verifier, and not a live Hume verifier. It is not semantic
// truth, not legal authenticity, not human authorship, not C2PA authenticity,
// not Object Lock, not tamper-proof, not browser-side B2 byte verification,
// not live B2 availability, not live ElevenLabs availability, not live Hume
// availability, and not production security.

import {
  GOLDEN_DEMO_ARCHIVE_SHA256,
  GOLDEN_DEMO_ARCHIVE_URI,
  GOLDEN_DEMO_PROVIDER_CALLS_DURING_REHYDRATE,
  GOLDEN_DEMO_REHYDRATE_SOURCE,
} from "./b2Evidence";
import {
  MULTIMODAL_PROOF_MANIFEST_HASH,
  MULTIMODAL_PROOF_MANIFEST_URI,
} from "./multimodalProof";

// ---------------------------------------------------------------------------
// Layer identity (spec section 21). Verbatim.
// ---------------------------------------------------------------------------

export const VOICE_AUDIO_EVIDENCE_CHOICE_SLICE_ID = "PS-037c";
export const VOICE_AUDIO_EVIDENCE_CHOICE_TITLE =
  "Voice/Audio Evidence Provider Choice Layer";

// One-line positioning statement. Surfaced by the summary variant and the panel
// header so the voice/audio provider-choice framing is identical on every core
// proof surface.
export const VOICE_AUDIO_EVIDENCE_CHOICE_POSITIONING =
  "ProofStudio proves what the pipeline recorded for voice/audio evidence; " +
  "this is a provider-choice layer supporting ElevenLabs Voiceover Artifact " +
  "Evidence and Hume Emotion-Signal Evidence; ElevenLabs and Hume are named " +
  "as selectable evidence providers for evidence labeling only; provider " +
  "choice does not equal provider availability.";

// ---------------------------------------------------------------------------
// Read-only reuse of accepted checked-in artifact evidence.
//
// The source media artifact reference (archive_uri) and the source media
// artifact digest (archive_sha256) are sourced verbatim from
// apps/web/src/b2Evidence.ts (PS-026), traced to
// docs/evidence/demo/golden-demo-run.json (PS-024) and the PS-021 live B2
// durable rehydrate smoke. The manifest_uri / manifest_hash are sourced
// verbatim from apps/web/src/multimodalProof.ts (PS-035A). PS-037c does not
// mutate these values and does not invent a voiceover artifact, a voiceover
// artifact reference, a voiceover artifact digest, an emotion signal, an
// emotion-signal reference, an emotion-signal digest, an audio artifact, an
// audio artifact reference, an audio artifact digest, a provider output
// reference, or a provider output digest that is not in accepted data.
// ---------------------------------------------------------------------------

// Recorded B2 archive reference for the golden demo run (PS-021 / PS-026). This
// is the recorded source media artifact reference the voice/audio evidence
// relates to (honestly surfaced, recorded-only).
export const VOICE_AUDIO_EVIDENCE_CHOICE_SOURCE_MEDIA_ARTIFACT_REFERENCE =
  GOLDEN_DEMO_ARCHIVE_URI;

// Recorded SHA-256 digest of the B2 archive content for the golden demo run
// (PS-021 / PS-026). This is the recorded source media artifact digest.
export const VOICE_AUDIO_EVIDENCE_CHOICE_SOURCE_MEDIA_ARTIFACT_DIGEST =
  GOLDEN_DEMO_ARCHIVE_SHA256;

// Recorded manifest reference (PS-035A) cross-referenced with the PS-037a
// multimodal proof layer.
export const VOICE_AUDIO_EVIDENCE_CHOICE_MANIFEST_REFERENCE =
  MULTIMODAL_PROOF_MANIFEST_URI;

// Recorded 64-hex manifest hash (PS-035A) cross-referenced with PS-037a.
export const VOICE_AUDIO_EVIDENCE_CHOICE_MANIFEST_HASH =
  MULTIMODAL_PROOF_MANIFEST_HASH;

// Recorded rehydrate source (durable_source = b2_rehydrated) from PS-021.
export const VOICE_AUDIO_EVIDENCE_CHOICE_REHYDRATE_SOURCE =
  GOLDEN_DEMO_REHYDRATE_SOURCE;

// Recorded provider-call count during rehydrate (PS-021 proved zero).
export const VOICE_AUDIO_EVIDENCE_CHOICE_PROVIDER_CALLS_DURING_REHYDRATE =
  GOLDEN_DEMO_PROVIDER_CALLS_DURING_REHYDRATE;

// The named voiceover artifact evidence provider (evidence labeling only; no
// live ElevenLabs API call).
export const VOICE_AUDIO_EVIDENCE_CHOICE_ELEVENLABS_LABEL = "ElevenLabs";

// The named emotion-signal evidence provider (evidence labeling only; no live
// Hume API call).
export const VOICE_AUDIO_EVIDENCE_CHOICE_HUME_LABEL = "Hume";

// The checked-in golden demo manifest the layer references (read-only).
export const VOICE_AUDIO_EVIDENCE_CHOICE_GOLDEN_MANIFEST_PATH =
  "docs/evidence/demo/golden-demo-run.json";

// ---------------------------------------------------------------------------
// Provider choice (spec section 10.4). The layer exposes a customer-selectable
// choice between two evidence tracks. Provider choice does not equal provider
// availability. The default selected path is honestly recorded; no live
// provider path exists in PS-037c.
// ---------------------------------------------------------------------------

export const VOICE_AUDIO_EVIDENCE_CHOICE_PROVIDER_CHOICE_LABEL =
  "provider choice";

export const VOICE_AUDIO_EVIDENCE_CHOICE_SELECTED_PATH_LABEL =
  "selected voice/audio evidence path";

// The selected voice/audio evidence path. Both tracks are named honestly and
// surfaced with their honest status; the default selected path is surfaced as
// honestly unavailable for live provider evidence.
export const VOICE_AUDIO_EVIDENCE_CHOICE_SELECTED_PATH =
  "not_available (local/demo evidence by default; provider choice does not " +
  "equal provider availability)";

// ---------------------------------------------------------------------------
// Two evidence tracks (spec section 10.4). Verbatim names.
// ---------------------------------------------------------------------------

export const VOICE_AUDIO_EVIDENCE_CHOICE_TRACK_ELEVENLABS =
  "ElevenLabs Voiceover Artifact Evidence";

export const VOICE_AUDIO_EVIDENCE_CHOICE_TRACK_HUME =
  "Hume Emotion-Signal Evidence";

// ---------------------------------------------------------------------------
// Canonical voice/audio evidence provider choice concepts (spec section 10.2 /
// 21). Verbatim. Surfaced as the concept labels on every core proof surface.
// ---------------------------------------------------------------------------

export const VOICE_AUDIO_EVIDENCE_CHOICE_CONCEPTS: readonly string[] = [
  "provider choice",
  "selected voice/audio evidence path",
  "ElevenLabs Voiceover Artifact Evidence",
  "Hume Emotion-Signal Evidence",
  "ElevenLabs",
  "Hume",
  "voiceover artifact evidence",
  "emotion-signal evidence",
  "audio artifact",
  "audio artifact reference",
  "audio artifact digest",
  "provider output reference",
  "provider output digest",
  "source media artifact reference",
  "source media artifact digest",
  "voice/audio evidence status",
  "voiceover status",
  "emotion-signal status",
  "provider activity status",
  "B2 evidence status",
  "rehydrate evidence status",
  "local verification",
  "live verification status",
  "disclosure boundary",
  "not claimed",
  "unknown",
  "local/demo evidence",
];

// ---------------------------------------------------------------------------
// Voice/audio provider-choice status values (spec section 12.2).
// ---------------------------------------------------------------------------

export type VoiceAudioEvidenceStatus =
  | "present"
  | "not_available"
  | "not_claimed"
  | "unknown";

export type VoiceAudioEvidenceVerification =
  | "locally_verified"
  | "unavailable"
  | "not_claimed"
  | "unknown";

export type VoiceAudioEvidenceState =
  | "recorded"
  | "locally_verified"
  | "recorded_only"
  | "not_verified"
  | "not_available"
  | "not_claimed"
  | "unknown"
  | "deferred_to_later_slice";

export interface VoiceAudioEvidenceChoiceItem {
  // concept: the verbatim concept label (spec section 21).
  concept: string;
  // label: the human-readable label, matching the verbatim strings.
  label: string;
  // value: the evidence value, honest about local / recorded-only /
  // unavailable / not claimed / unknown.
  value: string;
  // applicable: false when the concept honestly does not apply.
  applicable: boolean;
  // state: one of the canonical states.
  state: VoiceAudioEvidenceState;
}

// ---------------------------------------------------------------------------
// Voice/audio evidence items (spec section 12.2). Derived from accepted data.
// No voiceover artifact, voiceover artifact reference, voiceover artifact
// digest, emotion signal, emotion-signal reference, emotion-signal digest,
// audio artifact, audio artifact reference, audio artifact digest, provider
// output reference, or provider output digest is checked into accepted
// evidence, so those concepts honestly surface "not available" states. The
// source media artifact reference and the source media artifact digest are
// honestly surfaced from the recorded golden demo archive (recorded-only, not
// live-verified here).
// ---------------------------------------------------------------------------

const VOICEOVER_UNAVAILABLE = "voiceover artifact not available";
const EMOTION_UNAVAILABLE = "emotion signal not available";

export const VOICE_AUDIO_EVIDENCE_CHOICE_ITEMS: readonly VoiceAudioEvidenceChoiceItem[] =
  [
    {
      concept: "provider choice",
      label: "provider choice",
      value:
        "customer-selectable decision between ElevenLabs Voiceover Artifact " +
        "Evidence and Hume Emotion-Signal Evidence (provider choice does not " +
        "equal provider availability)",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "selected voice/audio evidence path",
      label: "selected voice/audio evidence path",
      value: VOICE_AUDIO_EVIDENCE_CHOICE_SELECTED_PATH,
      applicable: true,
      state: "not_available",
    },
    {
      concept: "voiceover artifact evidence",
      label: "voiceover artifact evidence",
      value: VOICEOVER_UNAVAILABLE,
      applicable: true,
      state: "not_available",
    },
    {
      concept: "emotion-signal evidence",
      label: "emotion-signal evidence",
      value: EMOTION_UNAVAILABLE,
      applicable: true,
      state: "not_available",
    },
    {
      concept: "audio artifact",
      label: "audio artifact",
      value:
        "audio artifact not available (no audio artifact checked into accepted evidence)",
      applicable: true,
      state: "not_available",
    },
    {
      concept: "audio artifact reference",
      label: "audio artifact reference",
      value:
        "audio artifact not available (no audio artifact reference recorded)",
      applicable: true,
      state: "not_available",
    },
    {
      concept: "audio artifact digest",
      label: "audio artifact digest",
      value:
        "audio artifact not available (no audio artifact digest recorded)",
      applicable: true,
      state: "not_available",
    },
    {
      concept: "provider output reference",
      label: "provider output reference",
      value:
        "provider output reference not available (no ElevenLabs voiceover or Hume emotion-signal output reference recorded)",
      applicable: true,
      state: "not_available",
    },
    {
      concept: "provider output digest",
      label: "provider output digest",
      value:
        "provider output digest not available (no ElevenLabs voiceover or Hume emotion-signal output digest recorded)",
      applicable: true,
      state: "not_available",
    },
    {
      concept: "source media artifact reference",
      label: "source media artifact reference",
      value: VOICE_AUDIO_EVIDENCE_CHOICE_SOURCE_MEDIA_ARTIFACT_REFERENCE,
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "source media artifact digest",
      label: "source media artifact digest",
      value: VOICE_AUDIO_EVIDENCE_CHOICE_SOURCE_MEDIA_ARTIFACT_DIGEST,
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "voice/audio evidence status",
      label: "voice/audio evidence status",
      value: "not_available",
      applicable: true,
      state: "not_available",
    },
    {
      concept: "voiceover status",
      label: "voiceover status",
      value: "not_available",
      applicable: true,
      state: "not_available",
    },
    {
      concept: "emotion-signal status",
      label: "emotion-signal status",
      value: "not_available",
      applicable: true,
      state: "not_available",
    },
    {
      concept: "provider activity status",
      label: "provider activity status",
      value:
        "no provider calls (no live ElevenLabs API call; no live Hume API call; local/demo evidence by default)",
      applicable: true,
      state: "not_claimed",
    },
    {
      concept: "B2 evidence status",
      label: "B2 evidence status",
      value: "recorded-only (B2 evidence referenced, not live-verified here)",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "rehydrate evidence status",
      label: "rehydrate evidence status",
      value:
        "recorded (" +
        VOICE_AUDIO_EVIDENCE_CHOICE_REHYDRATE_SOURCE +
        ", " +
        String(VOICE_AUDIO_EVIDENCE_CHOICE_PROVIDER_CALLS_DURING_REHYDRATE) +
        " provider calls during rehydrate)",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "local verification",
      label: "local verification",
      value:
        "local/demo evidence (locally checked-in golden / demo data; not live-verified)",
      applicable: true,
      state: "locally_verified",
    },
    {
      concept: "live verification status",
      label: "live verification status",
      value:
        "live provider evidence not available (local / check-only by default)",
      applicable: true,
      state: "not_verified",
    },
    {
      concept: "disclosure boundary",
      label: "disclosure boundary",
      value:
        "voiceover artifact reference does not equal legal authenticity; " +
        "audio artifact does not equal voice authenticity; provider voice " +
        "output does not equal speaker identity; emotion signal does not " +
        "equal emotion truth",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "not claimed",
      label: "not claimed",
      value:
        "the honest set of things ProofStudio does not claim for voice/audio evidence",
      applicable: true,
      state: "not_claimed",
    },
    {
      concept: "unknown",
      label: "unknown",
      value:
        "what remains unknown or not surfaced for voice/audio evidence",
      applicable: true,
      state: "unknown",
    },
    {
      concept: "local/demo evidence",
      label: "local/demo evidence",
      value:
        "local/demo evidence (the default posture; local / golden / demo fixture evidence, not live provider evidence)",
      applicable: true,
      state: "locally_verified",
    },
  ];

// ---------------------------------------------------------------------------
// Provider track records (spec section 10.4). Each track is named honestly and
// carries its honest present / not available / not claimed / unknown status.
// ---------------------------------------------------------------------------

export interface VoiceAudioEvidenceChoiceTrack {
  name: string;
  provider: string;
  provider_label_note: string;
  evidence_status: VoiceAudioEvidenceStatus;
  reference: string;
  digest: string;
}

export const VOICE_AUDIO_EVIDENCE_CHOICE_TRACKS: readonly VoiceAudioEvidenceChoiceTrack[] =
  [
    {
      name: VOICE_AUDIO_EVIDENCE_CHOICE_TRACK_ELEVENLABS,
      provider: VOICE_AUDIO_EVIDENCE_CHOICE_ELEVENLABS_LABEL,
      provider_label_note:
        "ElevenLabs is named as a selectable evidence provider for evidence labeling only (provider choice does not equal provider availability)",
      evidence_status: "not_available",
      reference: VOICEOVER_UNAVAILABLE,
      digest: VOICEOVER_UNAVAILABLE,
    },
    {
      name: VOICE_AUDIO_EVIDENCE_CHOICE_TRACK_HUME,
      provider: VOICE_AUDIO_EVIDENCE_CHOICE_HUME_LABEL,
      provider_label_note:
        "Hume is named as a selectable evidence provider for evidence labeling only (provider choice does not equal provider availability)",
      evidence_status: "not_available",
      reference: EMOTION_UNAVAILABLE,
      digest: EMOTION_UNAVAILABLE,
    },
  ];

// ---------------------------------------------------------------------------
// Required deferred later-slice / honest unavailable / not-claimed states
// (spec section 10.6 / 21). Verbatim.
//
// These are non-claim states: they state what is not available, not claimed,
// or unknown, owned by PS-037c or a later slice, and must never be read as a
// hidden proof. PS-037c must not fake a voiceover, an emotion signal, a voice
// analysis, an emotion analysis, a voice clone, a speaker identity, a
// biometric identity, a campaign intelligence output, or any provider output.
// ---------------------------------------------------------------------------

export const VOICE_AUDIO_EVIDENCE_CHOICE_DEFERRED_HEADING =
  "honest unavailable / not-claimed / deferred states";

export const VOICE_AUDIO_EVIDENCE_CHOICE_DEFERRED_STATES: readonly string[] = [
  "local/demo evidence",
  "live provider evidence not available",
  "ElevenLabs evidence path not available",
  "Hume evidence path not available",
  "voiceover artifact not available",
  "emotion signal not available",
  "speaker identity not claimed",
  "voice authenticity not claimed",
  "biometric identification not claimed",
  "emotion truth not claimed",
  "psychological diagnosis not claimed",
  "health inference not claimed",
  "campaign intelligence deferred to PS-037d",
];

// The later slice / out-of-scope owner for each deferred / not-claimed state.
// Surfaced so no reviewer mistakes an absent proof for a hidden proof.
export const VOICE_AUDIO_EVIDENCE_CHOICE_DEFERRED_OWNERS: readonly string[] = [
  "local/demo evidence -> default posture (local / golden / demo fixture evidence, not live provider evidence)",
  "live provider evidence not available -> PS-037c default (no live ElevenLabs API call; no live Hume API call)",
  "ElevenLabs evidence path not available -> PS-037c (no ElevenLabs Voiceover Artifact Evidence checked into accepted evidence)",
  "Hume evidence path not available -> PS-037c (no Hume Emotion-Signal Evidence checked into accepted evidence)",
  "voiceover artifact not available -> PS-037c (no voiceover artifact checked into accepted evidence)",
  "emotion signal not available -> PS-037c (no emotion signal checked into accepted evidence)",
  "speaker identity not claimed -> out of scope (PS-037c owns voice/audio provider choice only)",
  "voice authenticity not claimed -> out of scope (PS-037c names ElevenLabs for evidence labeling only)",
  "biometric identification not claimed -> out of scope (PS-037c is not a biometric system)",
  "emotion truth not claimed -> out of scope (PS-037c names Hume for evidence labeling only)",
  "psychological diagnosis not claimed -> out of scope (PS-037c is not a clinical system)",
  "health inference not claimed -> out of scope (PS-037c is not a health system)",
  "campaign intelligence deferred to PS-037d -> PS-037d (Gemini campaign intelligence / judge narrative)",
];

// ---------------------------------------------------------------------------
// Transcript/timestamp cross-reference (spec section 11). Surfaced so the layer
// states honestly whether transcript/timestamp evidence from PS-037b
// cross-references the audio artifact.
// ---------------------------------------------------------------------------

export const VOICE_AUDIO_EVIDENCE_CHOICE_TRANSCRIPT_CROSS_REFERENCE =
  "transcript/timestamp cross-reference: no transcript/timestamp evidence from " +
  "PS-037b cross-references the audio artifact (audio artifact not available); " +
  "the layer cross-references the PS-037b Transcript/Timestamp Evidence layer " +
  "so a reviewer can read this honestly.";

// ---------------------------------------------------------------------------
// Required de-escalation pairs (spec section 10.7 / 21). Surfaced verbatim so
// a judge never mistakes a strong-sounding voiceover artifact or emotion
// signal for a stronger guarantee. Stated as non-claims so context-aware
// forbidden-claim scanners never flag these boundary terms as overclaims.
// ---------------------------------------------------------------------------

export const VOICE_AUDIO_EVIDENCE_CHOICE_DEESCALATION_PAIRS: readonly string[] =
  [
    "proof does not equal truth",
    "provider choice does not equal provider availability",
    "voiceover artifact reference does not equal legal authenticity",
    "audio artifact does not equal voice authenticity",
    "provider voice output does not equal speaker identity",
    "emotion signal does not equal emotion truth",
    "local voice/audio evidence does not equal live ElevenLabs availability",
    "local voice/audio evidence does not equal live Hume availability",
    "demo/golden voice/audio evidence does not equal production security",
  ];

// ---------------------------------------------------------------------------
// Required negative boundary strings (spec section 10.8 / 21). Surfaced
// verbatim. These are the canonical "not claimed" set rendered as pills.
// ---------------------------------------------------------------------------

export const VOICE_AUDIO_EVIDENCE_CHOICE_NEGATIVE_BOUNDARY: readonly string[] =
  [
    "not voice authenticity",
    "not speaker identity",
    "not biometric identification",
    "not emotion truth",
    "not psychological diagnosis",
    "not health inference",
    "not mental state diagnosis",
    "not semantic truth",
    "not legal authenticity",
    "not human authorship",
    "not C2PA authenticity",
    "not Object Lock",
    "not tamper-proof",
    "not browser-side B2 byte verification",
    "not live B2 availability",
    "not live ElevenLabs availability",
    "not live Hume availability",
    "not production security",
    "not identity verification",
    "not deepfake detection",
    "not content moderation",
    "not OCR correctness",
    "not transcript correctness",
    "not timestamp correctness",
    "not model output truth",
  ];

// ---------------------------------------------------------------------------
// Persistent voice/audio boundary statement (spec section 11). Verbatim.
// Written as non-claim copy so the project's forbidden-claim scanners never
// flag the boundary terms.
// ---------------------------------------------------------------------------

export const VOICE_AUDIO_EVIDENCE_CHOICE_PERSISTENT_STATEMENT =
  "ProofStudio proves what the pipeline recorded for voice/audio evidence. " +
  "Proof does not equal truth. Provider choice does not equal provider " +
  "availability. A voiceover artifact reference does not equal legal " +
  "authenticity. An audio artifact does not equal voice authenticity. A " +
  "provider voice output does not equal speaker identity. An emotion signal " +
  "does not equal emotion truth. Local voice/audio evidence does not equal " +
  "live ElevenLabs availability. Local voice/audio evidence does not equal " +
  "live Hume availability. Demo/golden voice/audio evidence does not equal " +
  "production security.";

// Compact one-line summary used by the summary variant.
export const VOICE_AUDIO_EVIDENCE_CHOICE_SUMMARY =
  "Voice/Audio Evidence Provider Choice Layer: ElevenLabs Voiceover Artifact " +
  "Evidence and Hume Emotion-Signal Evidence tracks; provider choice does not " +
  "equal provider availability; local/demo evidence by default; live provider " +
  "evidence not available; proof does not equal truth.";

// ---------------------------------------------------------------------------
// Integration / cross-reference with the PS-037a Multimodal Proof Layer.
// Surfaced so the layer states explicitly that it cross-references PS-037a and
// fills the concrete voice/audio provider-choice evidence that PS-037a only
// reserved as deferred.
// ---------------------------------------------------------------------------

export const VOICE_AUDIO_EVIDENCE_CHOICE_MULTIMODAL_CROSS_REFERENCE =
  "Cross-references the PS-037a Multimodal Proof Layer: fills the concrete " +
  "voice/audio provider-choice evidence that PS-037a reserved as " +
  "'voice evidence not available' / 'emotion evidence not available'. " +
  "Manifest reference " +
  VOICE_AUDIO_EVIDENCE_CHOICE_MANIFEST_REFERENCE +
  " / manifest hash " +
  VOICE_AUDIO_EVIDENCE_CHOICE_MANIFEST_HASH +
  " reused from PS-035A via PS-037a.";

// ---------------------------------------------------------------------------
// Truth-boundary posture (spec section 10.1 / 21). Surfaced so the disclosure
// contract is deterministic and auditable. These are non-claim posture notes.
// ---------------------------------------------------------------------------

export const VOICE_AUDIO_EVIDENCE_CHOICE_POSTURE: readonly string[] = [
  "no ElevenLabs API calls",
  "no Hume API calls",
  "no provider calls",
  "no live B2 reads",
  "no B2 writes",
  "no broad B2 scans",
  "local / static by default",
];

// ---------------------------------------------------------------------------
// Required core proof surfaces (spec section 10.3). Listed so the voice/audio
// evidence provider choice contract documents exactly where the shared layer
// is rendered.
// ---------------------------------------------------------------------------

export const VOICE_AUDIO_EVIDENCE_CHOICE_REQUIRED_SURFACES: readonly string[] =
  [
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
