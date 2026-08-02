// PS-037d Gemini Campaign Intelligence / Judge Narrative Layer -- canonical
// data module.
//
// This is the single, shared source of campaign intelligence / judge narrative
// framing for every core proof surface. It exists so a reviewer, client, or
// judge reads the SAME honest campaign-level answer -- what campaign or demo
// story the proof stack represents, which artifacts are included in the
// campaign proof narrative, which evidence layers support the narrative, which
// proof surfaces are summarized, which providers / evidence tracks were
// recorded, what the Gemini campaign intelligence label means in this slice,
// whether campaign intelligence is local / demo / golden fixture evidence or
// live model evidence, whether model output exists or is honestly unavailable,
// whether the judge narrative is generated from recorded proof evidence,
// whether the narrative cross-references B2 / archive / rehydrate evidence,
// whether it cross-references Genblaze / manifest evidence, and whether it
// cross-references the PS-037 Trust Boundary, the PS-037a Multimodal Proof
// Layer, the PS-037b Transcript/Timestamp Evidence layer, and the PS-037c
// Voice/Audio Evidence Provider Choice layer -- on the Judge Cockpit Home, the
// B2 Evidence Explorer, the Manifest Verification Panel, the B2 Rehydrate
// Comparison, the B2 Audit Vault, the Review + Approval Workspace, the Judge
// Evidence Pack, the Public Provenance Passport, and the Review Room.
//
// The layer is a campaign intelligence / judge narrative inspection layer over
// already-recorded or honestly-unavailable data, not a new proof surface, not
// a new route, and not a new backend endpoint. It is purely client-side by
// default: it makes no Gemini API call, calls no model, calls no provider,
// reads no B2 object, performs no browser-side B2 byte verification, performs
// no broad B2 scan, and writes no B2 object. It only reads accepted local /
// golden / demo data and existing accepted data modules, and reuses the PS-037
// disclosure concepts, the PS-037a multimodal proof framing, the PS-037b
// transcript/timestamp evidence framing, and the PS-037c voice/audio evidence
// provider choice framing.
//
// Gemini is named as a campaign intelligence / judge narrative provider label
// for evidence labeling only. Naming Gemini does not imply a live Gemini API
// call, live Gemini availability, live model availability, a model generation
// guarantee, or any correctness guarantee over what the pipeline recorded.
// The Gemini label does not equal live Gemini availability.
//
// PS-037d does not invent new model outputs, new campaign performance numbers,
// new marketing effectiveness scores, new business outcome forecasts, new
// conversion lift, new revenue impact, new audience targeting accuracies, or
// new ad compliance approvals. It states the existing recorded campaign
// evidence consistently and honestly as a judge-facing narrative, and surfaces
// explicit honest "not available" / "not claimed" / "unknown" states where no
// evidence exists.
//
// Truth boundary: ProofStudio proves what the pipeline recorded. The Gemini
// Campaign Intelligence / Judge Narrative Layer is not a legal authenticity
// system, not a live B2 verifier, not a truth system, not a semantic-truth
// system, not a model-output-truth system, not a live Gemini verifier, not a
// live model system, not a campaign performance predictor, not a marketing
// effectiveness scorer, not a business outcome forecaster, not a conversion /
// revenue / audience / ad-compliance engine, not an identity system, not a
// biometric system, not a deepfake detector, not a content moderator, not an
// OCR verifier, not a transcript verifier, not a timestamp verifier, not a
// voice-authenticity system, not a speaker-identity system, and not an
// emotion-truth system. It is not semantic truth, not legal authenticity, not
// human authorship, not C2PA authenticity, not Object Lock, not tamper-proof,
// not browser-side B2 byte verification, not live B2 availability, not live
// Gemini availability, and not production security.

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

export const GEMINI_CAMPAIGN_INTELLIGENCE_SLICE_ID = "PS-037d";
export const GEMINI_CAMPAIGN_INTELLIGENCE_TITLE =
  "Gemini Campaign Intelligence / Judge Narrative";

// One-line positioning statement. Surfaced by the summary variant and the
// panel header so the campaign-intelligence / judge-narrative framing is
// identical on every core proof surface.
export const GEMINI_CAMPAIGN_INTELLIGENCE_POSITIONING =
  "ProofStudio proves what the pipeline recorded for campaign intelligence / " +
  "judge narrative; this is a narrative-over-recorded-proof layer; Gemini is " +
  "named as a campaign intelligence / judge narrative provider label for " +
  "evidence labeling only; the Gemini label does not equal live Gemini " +
  "availability.";

// ---------------------------------------------------------------------------
// Read-only reuse of accepted checked-in artifact evidence.
//
// The archive reference (archive_uri), the archive digest (archive_sha256),
// the rehydrate source, and the provider-call count are sourced verbatim from
// apps/web/src/b2Evidence.ts (PS-026), traced to
// docs/evidence/demo/golden-demo-run.json (PS-024) and the PS-021 live B2
// durable rehydrate smoke. The manifest_uri / manifest_hash are sourced
// verbatim from apps/web/src/multimodalProof.ts (PS-035A). PS-037d does not
// mutate these values and does not invent a model output, a campaign
// performance number, a marketing effectiveness score, a business outcome
// forecast, a conversion lift, a revenue impact figure, an audience targeting
// accuracy, or an ad compliance approval that is not in accepted data.
// ---------------------------------------------------------------------------

// Recorded B2 archive reference for the golden demo run (PS-021 / PS-026). This
// is the recorded campaign archive reference the narrative cross-references
// (honestly surfaced, recorded-only).
export const GEMINI_CAMPAIGN_INTELLIGENCE_ARCHIVE_REFERENCE =
  GOLDEN_DEMO_ARCHIVE_URI;

// Recorded SHA-256 digest of the B2 archive content for the golden demo run
// (PS-021 / PS-026). This is the recorded campaign archive digest.
export const GEMINI_CAMPAIGN_INTELLIGENCE_ARCHIVE_DIGEST =
  GOLDEN_DEMO_ARCHIVE_SHA256;

// Recorded manifest reference (PS-035A) cross-referenced with the PS-037a
// multimodal proof layer and the Genblaze manifest.
export const GEMINI_CAMPAIGN_INTELLIGENCE_MANIFEST_REFERENCE =
  MULTIMODAL_PROOF_MANIFEST_URI;

// Recorded 64-hex manifest hash (PS-035A) cross-referenced with PS-037a.
export const GEMINI_CAMPAIGN_INTELLIGENCE_MANIFEST_HASH =
  MULTIMODAL_PROOF_MANIFEST_HASH;

// Recorded rehydrate source (durable_source = b2_rehydrated) from PS-021.
export const GEMINI_CAMPAIGN_INTELLIGENCE_REHYDRATE_SOURCE =
  GOLDEN_DEMO_REHYDRATE_SOURCE;

// Recorded provider-call count during rehydrate (PS-021 proved zero).
export const GEMINI_CAMPAIGN_INTELLIGENCE_PROVIDER_CALLS_DURING_REHYDRATE =
  GOLDEN_DEMO_PROVIDER_CALLS_DURING_REHYDRATE;

// The named campaign intelligence / judge narrative provider (evidence labeling
// only; no live Gemini API call).
export const GEMINI_CAMPAIGN_INTELLIGENCE_PROVIDER_LABEL = "Gemini";

// The checked-in golden demo manifest the narrative references (read-only).
export const GEMINI_CAMPAIGN_INTELLIGENCE_GOLDEN_MANIFEST_PATH =
  "docs/evidence/demo/golden-demo-run.json";

// ---------------------------------------------------------------------------
// Campaign intelligence / judge narrative honesty (spec section 10.1 / 10.4 /
// 10.5). The default posture is local / demo / golden fixture evidence: no
// Gemini API call, no model call, no provider call, and no live B2 read. No
// model output is checked into accepted evidence, so the layer surfaces honest
// "model output not available" / "Gemini evidence not available" states rather
// than fabricated model output references or digests.
// ---------------------------------------------------------------------------

// The campaign intelligence framing label. The recorded campaign intelligence
// framing is present (a local / demo narrative over recorded proof evidence);
// no live Gemini-generated campaign intelligence is available.
export const GEMINI_CAMPAIGN_INTELLIGENCE_LABEL = "campaign intelligence";

// The judge narrative framing label. The recorded judge narrative is present
// (a local / demo narrative over recorded proof evidence); no live
// model-generated judge narrative is available.
export const GEMINI_CAMPAIGN_INTELLIGENCE_JUDGE_NARRATIVE_LABEL =
  "judge narrative";

// ---------------------------------------------------------------------------
// Canonical campaign intelligence / judge narrative concepts (spec section
// 10.2 / 21). Verbatim. Surfaced as the concept labels on every core proof
// surface.
// ---------------------------------------------------------------------------

export const GEMINI_CAMPAIGN_INTELLIGENCE_CONCEPTS: readonly string[] = [
  "campaign intelligence",
  "judge narrative",
  "campaign proof narrative",
  "campaign evidence summary",
  "Gemini",
  "Gemini provider label",
  "model output reference",
  "model output digest",
  "model output status",
  "campaign intelligence status",
  "judge narrative status",
  "narrative source evidence",
  "narrative source evidence references",
  "proof stack summary",
  "B2 evidence cross-reference",
  "manifest evidence cross-reference",
  "rehydrate evidence cross-reference",
  "trust boundary cross-reference",
  "multimodal proof cross-reference",
  "transcript/timestamp cross-reference",
  "voice/audio evidence cross-reference",
  "provider activity status",
  "local verification",
  "live verification status",
  "disclosure boundary",
  "not claimed",
  "unknown",
  "local/demo evidence",
];

// ---------------------------------------------------------------------------
// Campaign intelligence / judge narrative status values (spec section 12.2).
// ---------------------------------------------------------------------------

export type CampaignIntelligenceStatus =
  | "present"
  | "not_available"
  | "not_claimed"
  | "unknown";

export type CampaignIntelligenceState =
  | "recorded"
  | "locally_verified"
  | "recorded_only"
  | "not_verified"
  | "not_available"
  | "not_claimed"
  | "unknown"
  | "deferred_to_later_slice";

export interface CampaignIntelligenceItem {
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
  state: CampaignIntelligenceState;
}

// ---------------------------------------------------------------------------
// Campaign intelligence / judge narrative items (spec section 12.2). Derived
// from accepted data. No model output reference, model output digest, or
// generated campaign intelligence output is checked into accepted evidence, so
// those concepts honestly surface "not available" states. The recorded B2 /
// manifest / rehydrate evidence the narrative cross-references is honestly
// surfaced from the recorded golden demo archive and the PS-035A manifest
// (recorded-only, not live-verified here).
// ---------------------------------------------------------------------------

const MODEL_OUTPUT_UNAVAILABLE = "model output not available";

export const GEMINI_CAMPAIGN_INTELLIGENCE_ITEMS: readonly CampaignIntelligenceItem[] =
  [
    {
      concept: "campaign intelligence",
      label: "campaign intelligence",
      value:
        "recorded campaign intelligence framing over the recorded proof stack " +
        "(local / demo narrative; campaign intelligence does not equal " +
        "campaign performance)",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "judge narrative",
      label: "judge narrative",
      value:
        "recorded judge-facing narrative over the recorded proof stack " +
        "(local / demo narrative; judge narrative does not equal legal " +
        "authenticity)",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "campaign proof narrative",
      label: "campaign proof narrative",
      value:
        "the golden demo campaign story the proof stack represents: a recorded " +
        "Genblaze pipeline run archived to B2, rehydrated with zero provider " +
        "calls, and summarized into a judge-facing campaign proof narrative",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "campaign evidence summary",
      label: "campaign evidence summary",
      value:
        "compact summary of the recorded campaign evidence: B2 archive " +
        GEMINI_CAMPAIGN_INTELLIGENCE_ARCHIVE_REFERENCE +
        " / archive digest " +
        GEMINI_CAMPAIGN_INTELLIGENCE_ARCHIVE_DIGEST +
        " / manifest " +
        GEMINI_CAMPAIGN_INTELLIGENCE_MANIFEST_REFERENCE +
        " / manifest hash " +
        GEMINI_CAMPAIGN_INTELLIGENCE_MANIFEST_HASH +
        " / rehydrate " +
        GEMINI_CAMPAIGN_INTELLIGENCE_REHYDRATE_SOURCE +
        " (" +
        String(
          GEMINI_CAMPAIGN_INTELLIGENCE_PROVIDER_CALLS_DURING_REHYDRATE,
        ) +
        " provider calls during rehydrate)",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "Gemini provider label",
      label: "Gemini provider label",
      value:
        "Gemini is named as a campaign intelligence / judge narrative provider " +
        "label for evidence labeling only (the Gemini label does not equal " +
        "live Gemini availability)",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "model output reference",
      label: "model output reference",
      value: MODEL_OUTPUT_UNAVAILABLE,
      applicable: true,
      state: "not_available",
    },
    {
      concept: "model output digest",
      label: "model output digest",
      value: MODEL_OUTPUT_UNAVAILABLE,
      applicable: true,
      state: "not_available",
    },
    {
      concept: "model output status",
      label: "model output status",
      value: "not_available",
      applicable: true,
      state: "not_available",
    },
    {
      concept: "campaign intelligence status",
      label: "campaign intelligence status",
      value:
        "present (local / demo campaign intelligence framing over recorded " +
        "proof evidence); live Gemini-generated campaign intelligence not " +
        "available",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "judge narrative status",
      label: "judge narrative status",
      value:
        "present (local / demo judge narrative over recorded proof evidence); " +
        "live model-generated judge narrative not available",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "narrative source evidence",
      label: "narrative source evidence",
      value:
        "the set of recorded evidence the narrative is generated from: B2 " +
        "archive / rehydrate evidence (PS-021 / PS-026), Genblaze manifest " +
        "evidence (PS-028 / PS-035A), the PS-037 Disclosure + Trust Boundary, " +
        "the PS-037a Multimodal Proof Layer, the PS-037b Transcript/Timestamp " +
        "Evidence layer, and the PS-037c Voice/Audio Evidence Provider Choice " +
        "layer",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "narrative source evidence references",
      label: "narrative source evidence references",
      value:
        "cross-references that point at the source evidence the narrative is " +
        "generated from (B2 evidence cross-reference, manifest evidence " +
        "cross-reference, rehydrate evidence cross-reference, trust boundary " +
        "cross-reference, multimodal proof cross-reference, " +
        "transcript/timestamp cross-reference, voice/audio evidence " +
        "cross-reference)",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "proof stack summary",
      label: "proof stack summary",
      value:
        "single consistent summary of the recorded proof stack the narrative " +
        "is built over: B2 archive / rehydrate evidence, Genblaze manifest " +
        "evidence, PS-037 Disclosure + Trust Boundary, PS-037a Multimodal " +
        "Proof, PS-037b Transcript/Timestamp Evidence, and PS-037c Voice/Audio " +
        "Evidence Provider Choice",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "B2 evidence cross-reference",
      label: "B2 evidence cross-reference",
      value:
        "the narrative cross-references recorded B2 / archive evidence " +
        "(archive reference " +
        GEMINI_CAMPAIGN_INTELLIGENCE_ARCHIVE_REFERENCE +
        " / archive digest " +
        GEMINI_CAMPAIGN_INTELLIGENCE_ARCHIVE_DIGEST +
        "; recorded-only, not live-verified here)",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "manifest evidence cross-reference",
      label: "manifest evidence cross-reference",
      value:
        "the narrative cross-references recorded Genblaze / manifest evidence " +
        "(manifest " +
        GEMINI_CAMPAIGN_INTELLIGENCE_MANIFEST_REFERENCE +
        " / manifest hash " +
        GEMINI_CAMPAIGN_INTELLIGENCE_MANIFEST_HASH +
        "; recorded-only)",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "rehydrate evidence cross-reference",
      label: "rehydrate evidence cross-reference",
      value:
        "the narrative cross-references recorded rehydrate evidence " +
        "(rehydrate " +
        GEMINI_CAMPAIGN_INTELLIGENCE_REHYDRATE_SOURCE +
        " / " +
        String(
          GEMINI_CAMPAIGN_INTELLIGENCE_PROVIDER_CALLS_DURING_REHYDRATE,
        ) +
        " provider calls during rehydrate; recorded-only)",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "trust boundary cross-reference",
      label: "trust boundary cross-reference",
      value:
        "the narrative cross-references the PS-037 Disclosure + Trust Boundary " +
        "and never contradicts it",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "multimodal proof cross-reference",
      label: "multimodal proof cross-reference",
      value:
        "the narrative cross-references the PS-037a Multimodal Proof Layer and " +
        "fills the concrete campaign intelligence evidence PS-037a reserved " +
        "as deferred",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "transcript/timestamp cross-reference",
      label: "transcript/timestamp cross-reference",
      value:
        "the narrative cross-references the PS-037b Transcript/Timestamp " +
        "Evidence layer",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "voice/audio evidence cross-reference",
      label: "voice/audio evidence cross-reference",
      value:
        "the narrative cross-references the PS-037c Voice/Audio Evidence " +
        "Provider Choice layer",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "provider activity status",
      label: "provider activity status",
      value:
        "no provider calls (no live Gemini API call; no live model call; " +
        "local/demo evidence by default)",
      applicable: true,
      state: "not_claimed",
    },
    {
      concept: "local verification",
      label: "local verification",
      value:
        "local/demo evidence (locally checked-in golden / demo data; not " +
        "live-verified)",
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
        "campaign intelligence / judge narrative disclosure boundary, " +
        "consistent with PS-037: proof does not equal truth; the Gemini label " +
        "does not equal live Gemini availability; a model output reference " +
        "does not equal semantic truth; a judge narrative does not equal legal " +
        "authenticity; campaign intelligence does not equal campaign " +
        "performance; a campaign narrative does not equal marketing " +
        "effectiveness",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "not claimed",
      label: "not claimed",
      value:
        "the honest set of things ProofStudio does not claim for campaign " +
        "intelligence / judge narrative",
      applicable: true,
      state: "not_claimed",
    },
    {
      concept: "unknown",
      label: "unknown",
      value:
        "what remains unknown or not surfaced for campaign intelligence / " +
        "judge narrative",
      applicable: true,
      state: "unknown",
    },
    {
      concept: "local/demo evidence",
      label: "local/demo evidence",
      value:
        "local/demo evidence (the default posture; local / golden / demo " +
        "fixture evidence, not live provider evidence)",
      applicable: true,
      state: "locally_verified",
    },
  ];

// ---------------------------------------------------------------------------
// Required deferred later-slice / honest unavailable / not-claimed states
// (spec section 10.6 / 21). Verbatim.
//
// These are non-claim states: they state what is not available, not claimed,
// or unknown, owned by PS-037d or a later slice, and must never be read as a
// hidden proof. PS-037d must not fake a model output, a campaign intelligence
// output, a judge narrative, a campaign performance number, a marketing
// effectiveness score, a business outcome forecast, a conversion lift, a
// revenue impact figure, an audience targeting accuracy, or an ad compliance
// approval.
// ---------------------------------------------------------------------------

export const GEMINI_CAMPAIGN_INTELLIGENCE_DEFERRED_HEADING =
  "honest unavailable / not-claimed / deferred states";

export const GEMINI_CAMPAIGN_INTELLIGENCE_DEFERRED_STATES: readonly string[] = [
  "local/demo evidence",
  "live provider evidence not available",
  "Gemini evidence not available",
  "model output not available",
  "campaign intelligence not available",
  "judge narrative not available",
  "campaign performance prediction not claimed",
  "marketing effectiveness proof not claimed",
  "business outcome guarantee not claimed",
  "conversion lift not claimed",
  "revenue impact not claimed",
  "audience targeting accuracy not claimed",
  "ad compliance approval not claimed",
  "model output truth not claimed",
  "semantic truth not claimed",
  "legal authenticity not claimed",
  "voice authenticity not claimed",
  "speaker identity not claimed",
  "biometric identification not claimed",
  "emotion truth not claimed",
  "deepfake detection not claimed",
  "content moderation not claimed",
  "transcript correctness not claimed",
  "timestamp correctness not claimed",
];

// The later slice / out-of-scope owner for each deferred / not-claimed state.
// Surfaced so no reviewer mistakes an absent proof for a hidden proof.
export const GEMINI_CAMPAIGN_INTELLIGENCE_DEFERRED_OWNERS: readonly string[] = [
  "local/demo evidence -> default posture (local / golden / demo fixture evidence, not live provider evidence)",
  "live provider evidence not available -> PS-037d default (no live Gemini API call; no live model call)",
  "Gemini evidence not available -> PS-037d (Gemini named for evidence labeling only; the Gemini label does not equal live Gemini availability)",
  "model output not available -> PS-037d (no model output checked into accepted evidence)",
  "campaign intelligence not available -> PS-037d (no live Gemini-generated campaign intelligence)",
  "judge narrative not available -> PS-037d (no live model-generated judge narrative)",
  "campaign performance prediction not claimed -> out of scope (PS-037d is not a campaign performance predictor)",
  "marketing effectiveness proof not claimed -> out of scope (PS-037d is not a marketing effectiveness scorer)",
  "business outcome guarantee not claimed -> out of scope (PS-037d is not a business outcome engine)",
  "conversion lift not claimed -> out of scope (PS-037d is not a conversion lift engine)",
  "revenue impact not claimed -> out of scope (PS-037d is not a revenue impact engine)",
  "audience targeting accuracy not claimed -> out of scope (PS-037d is not an audience targeting system)",
  "ad compliance approval not claimed -> out of scope (PS-037d is not an ad compliance system)",
  "model output truth not claimed -> out of scope (PS-037d is not a model-output-truth system)",
  "semantic truth not claimed -> out of scope (PS-037d is not a semantic-truth verifier)",
  "legal authenticity not claimed -> out of scope (PS-037d is not a legal authenticity system)",
  "voice authenticity not claimed -> out of scope (PS-037d names providers for evidence labeling only)",
  "speaker identity not claimed -> out of scope (PS-037d is not a speaker-identity system)",
  "biometric identification not claimed -> out of scope (PS-037d is not a biometric system)",
  "emotion truth not claimed -> out of scope (PS-037d is not an emotion-truth system)",
  "deepfake detection not claimed -> out of scope (PS-037d is not a deepfake detector)",
  "content moderation not claimed -> out of scope (PS-037d is not a content moderator)",
  "transcript correctness not claimed -> out of scope (PS-037d is not a transcript verifier)",
  "timestamp correctness not claimed -> out of scope (PS-037d is not a timestamp verifier)",
];

// ---------------------------------------------------------------------------
// Cross-reference statements with the PS-037 Disclosure + Trust Boundary, the
// PS-037a Multimodal Proof Layer, the PS-037b Transcript/Timestamp Evidence
// layer, and the PS-037c Voice/Audio Evidence Provider Choice layer. Surfaced
// so the layer states explicitly that it integrates / cross-references each
// predecessor layer and never weakens its contract.
// ---------------------------------------------------------------------------

export const GEMINI_CAMPAIGN_INTELLIGENCE_TRUST_BOUNDARY_CROSS_REFERENCE =
  "Cross-references the PS-037 Disclosure + Trust Boundary: renders alongside " +
  "TrustBoundaryLayer, reuses the shared disclosure concepts, and never " +
  "contradicts the PS-037 boundary.";

export const GEMINI_CAMPAIGN_INTELLIGENCE_MULTIMODAL_CROSS_REFERENCE =
  "Cross-references the PS-037a Multimodal Proof Layer: renders alongside " +
  "MultimodalProofLayer and fills the concrete campaign intelligence / judge " +
  "narrative evidence that PS-037a reserved as 'campaign intelligence not " +
  "available'. Manifest reference " +
  GEMINI_CAMPAIGN_INTELLIGENCE_MANIFEST_REFERENCE +
  " / manifest hash " +
  GEMINI_CAMPAIGN_INTELLIGENCE_MANIFEST_HASH +
  " reused from PS-035A via PS-037a.";

export const GEMINI_CAMPAIGN_INTELLIGENCE_TRANSCRIPT_CROSS_REFERENCE =
  "Cross-references the PS-037b Transcript/Timestamp Evidence layer: renders " +
  "alongside TranscriptTimestampEvidenceLayer and surfaces an honest " +
  "transcript/timestamp cross-reference.";

export const GEMINI_CAMPAIGN_INTELLIGENCE_VOICE_AUDIO_CROSS_REFERENCE =
  "Cross-references the PS-037c Voice/Audio Evidence Provider Choice layer: " +
  "renders alongside VoiceAudioEvidenceChoiceLayer and surfaces an honest " +
  "voice/audio evidence cross-reference.";

// ---------------------------------------------------------------------------
// Required de-escalation pairs (spec section 10.7 / 21). Surfaced verbatim so
// a judge never mistakes a strong-sounding campaign narrative, Gemini label,
// or model output reference for a stronger guarantee. Stated as non-claims so
// context-aware forbidden-claim scanners never flag these boundary terms as
// overclaims.
// ---------------------------------------------------------------------------

export const GEMINI_CAMPAIGN_INTELLIGENCE_DEESCALATION_PAIRS: readonly string[] =
  [
    "proof does not equal truth",
    "Gemini label does not equal live Gemini availability",
    "model output does not equal semantic truth",
    "judge narrative does not equal legal authenticity",
    "campaign intelligence does not equal campaign performance",
    "campaign narrative does not equal marketing effectiveness",
    "local campaign intelligence does not equal live Gemini availability",
    "demo/golden campaign narrative does not equal production security",
  ];

// ---------------------------------------------------------------------------
// Required negative boundary strings (spec section 10.8 / 21). Surfaced
// verbatim. These are the canonical "not claimed" set rendered as pills.
// ---------------------------------------------------------------------------

export const GEMINI_CAMPAIGN_INTELLIGENCE_NEGATIVE_BOUNDARY: readonly string[] =
  [
    "not model output truth",
    "not semantic truth",
    "not legal authenticity",
    "not human authorship",
    "not C2PA authenticity",
    "not Object Lock",
    "not tamper-proof",
    "not browser-side B2 byte verification",
    "not live B2 availability",
    "not live Gemini availability",
    "not production security",
    "not production compliance",
    "not legal review",
    "not chain-of-custody guarantee",
    "not campaign performance prediction",
    "not marketing effectiveness proof",
    "not business outcome guarantee",
    "not conversion lift",
    "not revenue impact",
    "not audience targeting accuracy",
    "not ad compliance approval",
    "not identity verification",
    "not biometric identification",
    "not deepfake detection",
    "not content moderation",
    "not OCR correctness",
    "not transcript correctness",
    "not timestamp correctness",
    "not voice authenticity",
    "not speaker identity",
    "not emotion truth",
  ];

// ---------------------------------------------------------------------------
// Persistent campaign-intelligence / judge-narrative boundary statement (spec
// section 11). Verbatim. Written as non-claim copy so the project's
// forbidden-claim scanners never flag the boundary terms.
// ---------------------------------------------------------------------------

export const GEMINI_CAMPAIGN_INTELLIGENCE_PERSISTENT_STATEMENT =
  "ProofStudio proves what the pipeline recorded for campaign intelligence / " +
  "judge narrative. Proof does not equal truth. The Gemini label does not " +
  "equal live Gemini availability. A model output reference does not equal " +
  "semantic truth. A judge narrative does not equal legal authenticity. " +
  "Campaign intelligence does not equal campaign performance. A campaign " +
  "narrative does not equal marketing effectiveness. Local campaign " +
  "intelligence does not equal live Gemini availability. Demo/golden campaign " +
  "narrative does not equal production security.";

// Compact one-line summary used by the summary variant.
export const GEMINI_CAMPAIGN_INTELLIGENCE_SUMMARY =
  "Gemini Campaign Intelligence / Judge Narrative: a judge-facing campaign " +
  "proof narrative over recorded proof evidence; Gemini named for evidence " +
  "labeling only; the Gemini label does not equal live Gemini availability; " +
  "model output not available; local/demo evidence by default; proof does not " +
  "equal truth.";

// ---------------------------------------------------------------------------
// Truth-boundary posture (spec section 10.1 / 21). Surfaced so the disclosure
// contract is deterministic and auditable. These are non-claim posture notes.
// ---------------------------------------------------------------------------

export const GEMINI_CAMPAIGN_INTELLIGENCE_POSTURE: readonly string[] = [
  "no Gemini API calls",
  "no provider calls",
  "no live B2 reads",
  "no B2 writes",
  "no broad B2 scans",
  "local / static by default",
];

// ---------------------------------------------------------------------------
// Required core proof surfaces (spec section 10.3). Listed so the campaign
// intelligence / judge narrative contract documents exactly where the shared
// layer is rendered.
// ---------------------------------------------------------------------------

export const GEMINI_CAMPAIGN_INTELLIGENCE_REQUIRED_SURFACES: readonly string[] =
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
