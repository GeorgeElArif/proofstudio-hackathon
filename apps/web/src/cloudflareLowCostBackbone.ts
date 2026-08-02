// PS-037e Cloudflare Low-Cost Backbone -- canonical data module.
//
// This is the single, shared source of Cloudflare low-cost backbone framing
// for every core proof surface. It exists so a reviewer, client, or judge
// reads the SAME honest low-cost backbone / infrastructure posture /
// deployment readiness answer -- what the Cloudflare low-cost backbone plan
// is, which infrastructure roles Cloudflare is expected to cover, which roles
// remain on Backblaze B2 / Genblaze / existing proof evidence, whether the
// backbone is planned / local/demo / live, whether any Cloudflare resources
// exist, whether any Cloudflare deployment has happened, whether DNS has been
// changed, whether Cloudflare Pages / Workers / R2 is planned or active,
// whether Backblaze B2 remains the durable proof/archive system of record,
// what the Cloudflare label means in this slice, what the backbone status /
// deployment status / Cloudflare resource status / DNS status / cost-control
// status / cold-start mitigation status / production readiness status is,
// whether backbone evidence is local / demo / golden fixture evidence or live
// Cloudflare evidence, and whether the layer cross-references the PS-037 Trust
// Boundary, the PS-037a Multimodal Proof Layer, the PS-037b Transcript/
// Timestamp Evidence layer, the PS-037c Voice/Audio Evidence Provider Choice
// layer, and the PS-037d Gemini Campaign Intelligence / Judge Narrative layer
// -- on the Judge Cockpit Home, the B2 Evidence Explorer, the Manifest
// Verification Panel, the B2 Rehydrate Comparison, the B2 Audit Vault, the
// Review + Approval Workspace, the Judge Evidence Pack, the Public Provenance
// Passport, and the Review Room.
//
// The layer is a deployment-readiness / infrastructure-posture inspection
// layer over already-recorded or honestly-unavailable data, not a new proof
// surface, not a new route, and not a new backend endpoint. It is plan-over-
// recorded-proof by design: it reads what the pipeline already recorded and
// renders a consistent low-cost backbone / infrastructure posture plan. It is
// purely client-side by default: it makes no Cloudflare API call, mutates no
// DNS, creates no Cloudflare resource, deploys no Cloudflare Pages, deploys no
// Cloudflare Workers, performs no Cloudflare R2 live read, performs no
// Cloudflare R2 write, performs no Backblaze B2 write, calls no provider,
// reads no B2 object, performs no browser-side B2 byte verification, performs
// no broad B2 scan, and writes no B2 object. It only reads accepted local /
// golden / demo data and existing accepted data modules, and reuses the PS-037
// disclosure concepts, the PS-037a multimodal proof framing, the PS-037b
// transcript/timestamp evidence framing, the PS-037c voice/audio evidence
// provider choice framing, and the PS-037d campaign intelligence / judge
// narrative framing.
//
// Cloudflare is named as a platform/backbone provider label for evidence
// labeling only. Naming Cloudflare does not imply a live Cloudflare API call,
// live Cloudflare availability, live Cloudflare resource existence, live DNS
// ownership, a deployment, or any correctness guarantee. The Cloudflare label
// does not equal live Cloudflare availability.
//
// PS-037e does not invent new live deployments, new Cloudflare resources, new
// DNS changes, new Cloudflare Pages deployments, new Cloudflare Workers
// deployments, new Cloudflare R2 availability, new Backblaze B2 live
// availability, new production readiness, new production security, new
// production compliance, new legal compliance, new uptime guarantees, new cost
// guarantees, new performance guarantees, or new cold-start mitigation
// implementations. It states the existing recorded backbone posture
// consistently and honestly, and surfaces explicit honest "not available" /
// "not claimed" / "planned" / "unknown" states where no evidence exists.
//
// Truth boundary: ProofStudio proves what the pipeline recorded. The Cloudflare
// Low-Cost Backbone layer is not a live Cloudflare deployment, not a DNS change
// system, not a Cloudflare resource creator, not a Cloudflare Pages deployment
// system, not a Cloudflare Workers deployment system, not a Cloudflare R2 live
// reader, not a Cloudflare R2 writer, not a Backblaze B2 writer, not a live B2
// verifier, not a truth system, not a semantic-truth system, not a model-output-
// truth system, not a production readiness system, not a production security
// system, not a production compliance system, not a legal compliance system,
// not an uptime guarantee system, not a cost guarantee system, not a performance
// guarantee system, not a cold-start mitigation implementation system, not a
// campaign performance predictor, not a marketing effectiveness scorer, and not
// an identity / biometric / authenticity system. It is not live deployment, not
// production readiness, not production security, not production compliance, not
// legal compliance, not uptime guarantee, not cost guarantee, not performance
// guarantee, not cold-start mitigation implementation, not DNS ownership, not
// Cloudflare resource existence, not Cloudflare Pages availability, not
// Cloudflare Workers availability, not Cloudflare R2 availability, not Backblaze
// B2 live availability, not Object Lock, not tamper-proof, not browser-side B2
// byte verification, not live B2 availability, not semantic truth, not legal
// authenticity, not human authorship, and not C2PA authenticity.

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

export const CLOUDFLARE_LOW_COST_BACKBONE_SLICE_ID = "PS-037e";
export const CLOUDFLARE_LOW_COST_BACKBONE_TITLE = "Cloudflare Low-Cost Backbone";

// One-line positioning statement. Surfaced by the summary variant and the
// panel header so the low-cost backbone / infrastructure-posture framing is
// identical on every core proof surface.
export const CLOUDFLARE_LOW_COST_BACKBONE_POSITIONING =
  "ProofStudio proves what the pipeline recorded for the low-cost backbone; " +
  "this is a plan-over-recorded-proof layer; Cloudflare is named as a " +
  "platform/backbone provider label for evidence labeling only; the Cloudflare " +
  "label does not equal live Cloudflare availability.";

// ---------------------------------------------------------------------------
// Read-only reuse of accepted checked-in artifact evidence.
//
// The archive reference (archive_uri), the archive digest (archive_sha256),
// the rehydrate source, and the provider-call count are sourced verbatim from
// apps/web/src/b2Evidence.ts (PS-026), traced to
// docs/evidence/demo/golden-demo-run.json (PS-024) and the PS-021 live B2
// durable rehydrate smoke. The manifest_uri / manifest_hash are sourced
// verbatim from apps/web/src/multimodalProof.ts (PS-035A). PS-037e does not
// mutate these values and does not invent a live deployment, a Cloudflare
// resource, a DNS change, or a Cloudflare R2 availability that is not in
// accepted data.
// ---------------------------------------------------------------------------

// Recorded B2 archive reference for the golden demo run (PS-021 / PS-026). This
// is the recorded low-cost backbone system-of-record archive reference the
// layer cross-references (honestly surfaced, recorded-only).
export const CLOUDFLARE_LOW_COST_BACKBONE_ARCHIVE_REFERENCE =
  GOLDEN_DEMO_ARCHIVE_URI;

// Recorded SHA-256 digest of the B2 archive content for the golden demo run
// (PS-021 / PS-026). This is the recorded system-of-record archive digest.
export const CLOUDFLARE_LOW_COST_BACKBONE_ARCHIVE_DIGEST =
  GOLDEN_DEMO_ARCHIVE_SHA256;

// Recorded manifest reference (PS-035A) cross-referenced with the PS-037a
// multimodal proof layer and the Genblaze manifest.
export const CLOUDFLARE_LOW_COST_BACKBONE_MANIFEST_REFERENCE =
  MULTIMODAL_PROOF_MANIFEST_URI;

// Recorded 64-hex manifest hash (PS-035A) cross-referenced with PS-037a.
export const CLOUDFLARE_LOW_COST_BACKBONE_MANIFEST_HASH =
  MULTIMODAL_PROOF_MANIFEST_HASH;

// Recorded rehydrate source (durable_source = b2_rehydrated) from PS-021.
export const CLOUDFLARE_LOW_COST_BACKBONE_REHYDRATE_SOURCE =
  GOLDEN_DEMO_REHYDRATE_SOURCE;

// Recorded provider-call count during rehydrate (PS-021 proved zero).
export const CLOUDFLARE_LOW_COST_BACKBONE_PROVIDER_CALLS_DURING_REHYDRATE =
  GOLDEN_DEMO_PROVIDER_CALLS_DURING_REHYDRATE;

// The named platform/backbone provider (evidence labeling only; no live
// Cloudflare API call).
export const CLOUDFLARE_LOW_COST_BACKBONE_PROVIDER_LABEL = "Cloudflare";

// The checked-in golden demo manifest the layer references (read-only).
export const CLOUDFLARE_LOW_COST_BACKBONE_GOLDEN_MANIFEST_PATH =
  "docs/evidence/demo/golden-demo-run.json";

// ---------------------------------------------------------------------------
// Cloudflare low-cost backbone honesty (spec section 10.1 / 10.4 / 10.5). The
// default posture is local / demo / golden fixture evidence: no Cloudflare API
// call, no DNS mutation, no Cloudflare resource creation, no Cloudflare Pages
// deployment, no Cloudflare Workers deployment, no Cloudflare R2 live read, no
// Cloudflare R2 write, and no Backblaze B2 write. No live Cloudflare deployment,
// Cloudflare resource, DNS change, or Cloudflare R2 availability is checked
// into accepted evidence, so the layer surfaces honest "live Cloudflare
// evidence not available", "Cloudflare deployment not available", "Cloudflare
// resource evidence not available", and "DNS evidence not available" states
// rather than fabricated values.
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// Canonical Cloudflare low-cost backbone concepts (spec section 10.2 / 21).
// Verbatim. Surfaced as the concept labels on every core proof surface.
// ---------------------------------------------------------------------------

export const CLOUDFLARE_LOW_COST_BACKBONE_CONCEPTS: readonly string[] = [
  "low-cost backbone",
  "infrastructure posture",
  "deployment readiness evidence",
  "Cloudflare",
  "Cloudflare provider label",
  "Cloudflare Pages plan",
  "Cloudflare Workers plan",
  "Cloudflare R2 plan",
  "Backblaze B2 system of record",
  "B2 archive remains system of record",
  "Genblaze manifest evidence remains system of record",
  "backbone status",
  "deployment status",
  "Cloudflare resource status",
  "DNS status",
  "cost-control status",
  "cold-start mitigation status",
  "production readiness status",
  "trust boundary cross-reference",
  "multimodal proof cross-reference",
  "transcript/timestamp cross-reference",
  "voice/audio evidence cross-reference",
  "campaign intelligence cross-reference",
  "local verification",
  "live verification status",
  "disclosure boundary",
  "not claimed",
  "unknown",
  "planned",
];

// ---------------------------------------------------------------------------
// Cloudflare low-cost backbone status values (spec section 12.2).
// ---------------------------------------------------------------------------

export type BackboneStatus =
  | "planned"
  | "local_demo"
  | "not_available"
  | "not_claimed"
  | "unknown";

export type CloudflareBackboneState =
  | "recorded"
  | "locally_verified"
  | "recorded_only"
  | "not_verified"
  | "not_available"
  | "not_claimed"
  | "planned"
  | "unknown"
  | "deferred_to_later_slice";

export interface CloudflareBackboneItem {
  // concept: the verbatim concept label (spec section 21).
  concept: string;
  // label: the human-readable label, matching the verbatim strings.
  label: string;
  // value: the evidence value, honest about local / recorded-only /
  // unavailable / not claimed / planned / unknown.
  value: string;
  // applicable: false when the concept honestly does not apply.
  applicable: boolean;
  // state: one of the canonical states.
  state: CloudflareBackboneState;
}

// ---------------------------------------------------------------------------
// Cloudflare low-cost backbone items (spec section 12.2). Derived from accepted
// data. No live Cloudflare deployment, Cloudflare resource, DNS change,
// Cloudflare Pages deployment, Cloudflare Workers deployment, Cloudflare R2
// availability, or Backblaze B2 live availability is checked into accepted
// evidence, so those concepts honestly surface "not available" / "planned"
// states. The recorded B2 / manifest / rehydrate evidence the layer
// cross-references is honestly surfaced from the recorded golden demo archive
// and the PS-035A manifest (recorded-only, not live-verified here).
// ---------------------------------------------------------------------------

export const CLOUDFLARE_LOW_COST_BACKBONE_ITEMS: readonly CloudflareBackboneItem[] =
  [
    {
      concept: "low-cost backbone",
      label: "low-cost backbone",
      value:
        "recorded low-cost hosting/backbone plan over the recorded proof stack " +
        "(local / demo plan; a backbone plan does not equal live deployment)",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "infrastructure posture",
      label: "infrastructure posture",
      value:
        "judge-facing infrastructure posture view over the recorded proof stack " +
        "(local / demo posture; infrastructure posture does not equal production " +
        "security)",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "deployment readiness evidence",
      label: "deployment readiness evidence",
      value:
        "recorded deployment readiness evidence over the recorded proof stack " +
        "(local / demo evidence; deployment readiness does not equal production " +
        "readiness)",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "Cloudflare",
      label: "Cloudflare",
      value:
        "Cloudflare is named as a platform/backbone provider label for evidence " +
        "labeling only (naming Cloudflare does not imply a live Cloudflare API " +
        "call, live Cloudflare availability, live Cloudflare resource existence, " +
        "or live DNS ownership)",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "Cloudflare provider label",
      label: "Cloudflare provider label",
      value:
        "Cloudflare is named as a platform/backbone provider label for evidence " +
        "labeling only (the Cloudflare label does not equal live Cloudflare " +
        "availability)",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "Cloudflare Pages plan",
      label: "Cloudflare Pages plan",
      value:
        "planned (Cloudflare Pages hosting plan is planned; the Cloudflare Pages " +
        "plan does not equal Cloudflare Pages availability)",
      applicable: true,
      state: "planned",
    },
    {
      concept: "Cloudflare Workers plan",
      label: "Cloudflare Workers plan",
      value:
        "planned (Cloudflare Workers compute plan is planned; the Cloudflare " +
        "Workers plan does not equal Cloudflare Workers availability)",
      applicable: true,
      state: "planned",
    },
    {
      concept: "Cloudflare R2 plan",
      label: "Cloudflare R2 plan",
      value:
        "planned (Cloudflare R2 object storage plan is planned; the Cloudflare R2 " +
        "plan does not equal live R2 availability)",
      applicable: true,
      state: "planned",
    },
    {
      concept: "Backblaze B2 system of record",
      label: "Backblaze B2 system of record",
      value:
        "Backblaze B2 remains the durable proof/archive system of record " +
        "(archive reference " +
        CLOUDFLARE_LOW_COST_BACKBONE_ARCHIVE_REFERENCE +
        " / archive digest " +
        CLOUDFLARE_LOW_COST_BACKBONE_ARCHIVE_DIGEST +
        "; recorded-only, not live-verified here)",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "B2 archive remains system of record",
      label: "B2 archive remains system of record",
      value:
        "the B2 archive remains the durable proof/archive system of record " +
        "(Backblaze B2 is the system of record; the Cloudflare low-cost backbone " +
        "does not displace it)",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "Genblaze manifest evidence remains system of record",
      label: "Genblaze manifest evidence remains system of record",
      value:
        "the Genblaze manifest evidence remains the system of record " +
        "(manifest " +
        CLOUDFLARE_LOW_COST_BACKBONE_MANIFEST_REFERENCE +
        " / manifest hash " +
        CLOUDFLARE_LOW_COST_BACKBONE_MANIFEST_HASH +
        "; recorded-only)",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "backbone status",
      label: "backbone status",
      value:
        "planned (local / demo low-cost backbone plan over recorded proof " +
        "evidence); live Cloudflare evidence not available",
      applicable: true,
      state: "planned",
    },
    {
      concept: "deployment status",
      label: "deployment status",
      value: "Cloudflare deployment not available",
      applicable: true,
      state: "not_available",
    },
    {
      concept: "Cloudflare resource status",
      label: "Cloudflare resource status",
      value: "none (Cloudflare resource evidence not available)",
      applicable: true,
      state: "not_available",
    },
    {
      concept: "DNS status",
      label: "DNS status",
      value: "unchanged (DNS evidence not available; no DNS mutation)",
      applicable: true,
      state: "not_available",
    },
    {
      concept: "cost-control status",
      label: "cost-control status",
      value:
        "planned (cost-control posture is planned; a low-cost posture does not " +
        "equal cost guarantee)",
      applicable: true,
      state: "planned",
    },
    {
      concept: "cold-start mitigation status",
      label: "cold-start mitigation status",
      value: "cold-start mitigation deferred to PS-038",
      applicable: true,
      state: "deferred_to_later_slice",
    },
    {
      concept: "production readiness status",
      label: "production readiness status",
      value: "production readiness deferred to PS-038",
      applicable: true,
      state: "deferred_to_later_slice",
    },
    {
      concept: "trust boundary cross-reference",
      label: "trust boundary cross-reference",
      value:
        "the layer cross-references the PS-037 Disclosure + Trust Boundary and " +
        "never contradicts it",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "multimodal proof cross-reference",
      label: "multimodal proof cross-reference",
      value:
        "the layer cross-references the PS-037a Multimodal Proof Layer (manifest " +
        CLOUDFLARE_LOW_COST_BACKBONE_MANIFEST_REFERENCE +
        " / manifest hash " +
        CLOUDFLARE_LOW_COST_BACKBONE_MANIFEST_HASH +
        " reused from PS-035A via PS-037a)",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "transcript/timestamp cross-reference",
      label: "transcript/timestamp cross-reference",
      value:
        "the layer cross-references the PS-037b Transcript/Timestamp Evidence " +
        "layer",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "voice/audio evidence cross-reference",
      label: "voice/audio evidence cross-reference",
      value:
        "the layer cross-references the PS-037c Voice/Audio Evidence Provider " +
        "Choice layer",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "campaign intelligence cross-reference",
      label: "campaign intelligence cross-reference",
      value:
        "the layer cross-references the PS-037d Gemini Campaign Intelligence / " +
        "Judge Narrative layer",
      applicable: true,
      state: "recorded_only",
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
        "live Cloudflare evidence not available (local / check-only by default; " +
        "no live Cloudflare API call)",
      applicable: true,
      state: "not_verified",
    },
    {
      concept: "disclosure boundary",
      label: "disclosure boundary",
      value:
        "low-cost backbone disclosure boundary, consistent with PS-037: proof " +
        "does not equal truth; the Cloudflare label does not equal live Cloudflare " +
        "availability; a backbone plan does not equal live deployment; deployment " +
        "readiness does not equal production readiness; a low-cost posture does " +
        "not equal cost guarantee; infrastructure posture does not equal " +
        "production security; a Cloudflare R2 plan does not equal live R2 " +
        "availability; local backbone evidence does not equal live Cloudflare " +
        "availability; demo/golden backbone evidence does not equal production " +
        "security",
      applicable: true,
      state: "recorded_only",
    },
    {
      concept: "not claimed",
      label: "not claimed",
      value:
        "the honest set of things ProofStudio does not claim for the low-cost " +
        "backbone",
      applicable: true,
      state: "not_claimed",
    },
    {
      concept: "unknown",
      label: "unknown",
      value:
        "what remains unknown or not surfaced for the low-cost backbone",
      applicable: true,
      state: "unknown",
    },
    {
      concept: "planned",
      label: "planned",
      value:
        "what is planned but not yet live for the low-cost backbone " +
        "(Cloudflare Pages plan / Cloudflare Workers plan / Cloudflare R2 plan / " +
        "cost-control posture are planned, not live)",
      applicable: true,
      state: "planned",
    },
  ];

// ---------------------------------------------------------------------------
// Required deferred later-slice / honest unavailable / not-claimed states
// (spec section 10.6 / 21). Verbatim.
//
// These are non-claim states: they state what is not available, not claimed,
// planned, or unknown, owned by PS-037e or a later slice, and must never be
// read as a hidden proof. PS-037e must not fake a live deployment, a Cloudflare
// resource, a DNS change, a Cloudflare Pages deployment, a Cloudflare Workers
// deployment, a Cloudflare R2 availability, or a Backblaze B2 live availability.
// ---------------------------------------------------------------------------

export const CLOUDFLARE_LOW_COST_BACKBONE_DEFERRED_HEADING =
  "honest unavailable / not-claimed / planned / deferred states";

export const CLOUDFLARE_LOW_COST_BACKBONE_DEFERRED_STATES: readonly string[] = [
  "local/demo evidence",
  "live Cloudflare evidence not available",
  "Cloudflare deployment not available",
  "Cloudflare resource evidence not available",
  "DNS evidence not available",
  "production security evidence not available",
  "production compliance evidence not available",
  "cold-start mitigation deferred to PS-038",
  "production readiness deferred to PS-038",
  "final submission packaging deferred to PS-039",
  "not claimed",
  "unknown",
  "planned",
];

// The later slice / out-of-scope owner for each deferred / not-claimed state.
// Surfaced so no reviewer mistakes an absent proof for a hidden proof.
export const CLOUDFLARE_LOW_COST_BACKBONE_DEFERRED_OWNERS: readonly string[] = [
  "local/demo evidence -> default posture (local / golden / demo fixture evidence, not live Cloudflare evidence)",
  "live Cloudflare evidence not available -> PS-037e default (no live Cloudflare API call; local / check-only by default)",
  "Cloudflare deployment not available -> PS-037e (Cloudflare named for evidence labeling only; the Cloudflare label does not equal live Cloudflare availability)",
  "Cloudflare resource evidence not available -> PS-037e (no Cloudflare resource created)",
  "DNS evidence not available -> PS-037e (no DNS mutation)",
  "production security evidence not available -> out of scope (PS-037e is not a production security system)",
  "production compliance evidence not available -> out of scope (PS-037e is not a production compliance system)",
  "cold-start mitigation deferred to PS-038 -> PS-038 (PS-037e is not a cold-start mitigation implementation)",
  "production readiness deferred to PS-038 -> PS-038 (PS-037e is not a production readiness system)",
  "final submission packaging deferred to PS-039 -> PS-039 (PS-037e is not a final submission packaging system)",
  "not claimed -> out of scope (PS-037e states what it does not prove for the low-cost backbone)",
  "unknown -> honest state (what remains unknown or not surfaced for the low-cost backbone)",
  "planned -> honest state (what is planned but not yet live for the low-cost backbone)",
];

// ---------------------------------------------------------------------------
// Cross-reference statements with the PS-037 Disclosure + Trust Boundary, the
// PS-037a Multimodal Proof Layer, the PS-037b Transcript/Timestamp Evidence
// layer, the PS-037c Voice/Audio Evidence Provider Choice layer, and the
// PS-037d Gemini Campaign Intelligence / Judge Narrative layer. Surfaced so the
// layer states explicitly that it integrates / cross-references each
// predecessor layer and never weakens its contract.
// ---------------------------------------------------------------------------

export const CLOUDFLARE_LOW_COST_BACKBONE_TRUST_BOUNDARY_CROSS_REFERENCE =
  "Cross-references the PS-037 Disclosure + Trust Boundary: renders alongside " +
  "TrustBoundaryLayer, reuses the shared disclosure concepts, and never " +
  "contradicts the PS-037 boundary.";

export const CLOUDFLARE_LOW_COST_BACKBONE_MULTIMODAL_CROSS_REFERENCE =
  "Cross-references the PS-037a Multimodal Proof Layer: renders alongside " +
  "MultimodalProofLayer and surfaces an honest multimodal proof " +
  "cross-reference. Manifest reference " +
  CLOUDFLARE_LOW_COST_BACKBONE_MANIFEST_REFERENCE +
  " / manifest hash " +
  CLOUDFLARE_LOW_COST_BACKBONE_MANIFEST_HASH +
  " reused from PS-035A via PS-037a.";

export const CLOUDFLARE_LOW_COST_BACKBONE_TRANSCRIPT_CROSS_REFERENCE =
  "Cross-references the PS-037b Transcript/Timestamp Evidence layer: renders " +
  "alongside TranscriptTimestampEvidenceLayer and surfaces an honest " +
  "transcript/timestamp cross-reference.";

export const CLOUDFLARE_LOW_COST_BACKBONE_VOICE_AUDIO_CROSS_REFERENCE =
  "Cross-references the PS-037c Voice/Audio Evidence Provider Choice layer: " +
  "renders alongside VoiceAudioEvidenceChoiceLayer and surfaces an honest " +
  "voice/audio evidence cross-reference.";

export const CLOUDFLARE_LOW_COST_BACKBONE_CAMPAIGN_INTELLIGENCE_CROSS_REFERENCE =
  "Cross-references the PS-037d Gemini Campaign Intelligence / Judge Narrative " +
  "layer: renders alongside CampaignIntelligenceJudgeNarrativeLayer and " +
  "surfaces an honest campaign intelligence cross-reference.";

// ---------------------------------------------------------------------------
// Required de-escalation pairs (spec section 10.7 / 21). Surfaced verbatim so
// a judge never mistakes a strong-sounding backbone plan, Cloudflare label, or
// deployment-readiness value for a stronger guarantee. Stated as non-claims so
// context-aware forbidden-claim scanners never flag these boundary terms as
// overclaims.
// ---------------------------------------------------------------------------

export const CLOUDFLARE_LOW_COST_BACKBONE_DEESCALATION_PAIRS: readonly string[] =
  [
    "proof does not equal truth",
    "Cloudflare label does not equal live Cloudflare availability",
    "backbone plan does not equal live deployment",
    "deployment readiness does not equal production readiness",
    "low-cost posture does not equal cost guarantee",
    "infrastructure posture does not equal production security",
    "Cloudflare R2 plan does not equal live R2 availability",
    "local backbone evidence does not equal live Cloudflare availability",
    "demo/golden backbone evidence does not equal production security",
  ];

// ---------------------------------------------------------------------------
// Required negative boundary strings (spec section 10.8 / 21). Surfaced
// verbatim. These are the canonical "not claimed" set rendered as pills.
// ---------------------------------------------------------------------------

export const CLOUDFLARE_LOW_COST_BACKBONE_NEGATIVE_BOUNDARY: readonly string[] =
  [
    "not live deployment",
    "not production readiness",
    "not production security",
    "not production compliance",
    "not legal compliance",
    "not uptime guarantee",
    "not cost guarantee",
    "not performance guarantee",
    "not cold-start mitigation implementation",
    "not DNS ownership",
    "not Cloudflare resource existence",
    "not Cloudflare Pages availability",
    "not Cloudflare Workers availability",
    "not Cloudflare R2 availability",
    "not Backblaze B2 live availability",
    "not Object Lock",
    "not tamper-proof",
    "not browser-side B2 byte verification",
    "not semantic truth",
    "not legal authenticity",
    "not human authorship",
    "not C2PA authenticity",
    "not campaign performance prediction",
    "not marketing effectiveness proof",
    "not model output truth",
  ];

// ---------------------------------------------------------------------------
// Persistent low-cost backbone boundary statement (spec section 11). Verbatim.
// Written as non-claim copy so the project's forbidden-claim scanners never
// flag the boundary terms.
// ---------------------------------------------------------------------------

export const CLOUDFLARE_LOW_COST_BACKBONE_PERSISTENT_STATEMENT =
  "ProofStudio proves what the pipeline recorded for the low-cost backbone. " +
  "Proof does not equal truth. The Cloudflare label does not equal live " +
  "Cloudflare availability. A backbone plan does not equal live deployment. " +
  "Deployment readiness does not equal production readiness. A low-cost posture " +
  "does not equal cost guarantee. An infrastructure posture does not equal " +
  "production security. A Cloudflare R2 plan does not equal live R2 " +
  "availability. Local backbone evidence does not equal live Cloudflare " +
  "availability. Demo/golden backbone evidence does not equal production " +
  "security.";

// Compact one-line summary used by the summary variant.
export const CLOUDFLARE_LOW_COST_BACKBONE_SUMMARY =
  "Cloudflare Low-Cost Backbone: a low-cost backbone / infrastructure posture / " +
  "deployment readiness evidence plan over recorded proof evidence; Cloudflare " +
  "named for evidence labeling only; the Cloudflare label does not equal live " +
  "Cloudflare availability; live Cloudflare evidence not available; Cloudflare " +
  "deployment not available; local/demo evidence by default; proof does not " +
  "equal truth.";

// ---------------------------------------------------------------------------
// Truth-boundary posture (spec section 10.1 / 21). Surfaced so the disclosure
// contract is deterministic and auditable. These are non-claim posture notes.
// ---------------------------------------------------------------------------

export const CLOUDFLARE_LOW_COST_BACKBONE_POSTURE: readonly string[] = [
  "no Cloudflare API calls",
  "no DNS mutation",
  "no Cloudflare resource creation",
  "no Cloudflare Pages deployment",
  "no Cloudflare Workers deployment",
  "no Cloudflare R2 live reads",
  "no Cloudflare R2 writes",
  "no Backblaze B2 writes",
  "no provider calls",
  "no live B2 reads",
  "no B2 writes",
  "no broad B2 scans",
  "local / static by default",
];

// ---------------------------------------------------------------------------
// Required core proof surfaces (spec section 10.3). Listed so the Cloudflare
// low-cost backbone contract documents exactly where the shared layer is
// rendered.
// ---------------------------------------------------------------------------

export const CLOUDFLARE_LOW_COST_BACKBONE_REQUIRED_SURFACES: readonly string[] =
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
